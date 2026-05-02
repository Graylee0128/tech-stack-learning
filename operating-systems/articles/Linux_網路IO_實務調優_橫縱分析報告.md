# Linux 網路 I/O 實務調優：橫縱分析報告

> **適用場景**：Kubernetes + Nginx/Ingress + Go services + HTTP/gRPC 混合
> **業務形態**：博弈 / 電商類高併發服務
> **工作邊界**：可同時調整 application / Kubernetes / node
> **核心目標**：tail latency / jitter 治理、高連線高併發承載
> **證據標記**：📖 官方事實 ｜ 🔧 工程實踐/案例 ｜ 🔗 交叉推論

---

## 目錄

- [一、一句話定義](#一一句話定義)
- [一‧五、看不見的效能稅：為什麼調優的本質是「少過邊檢站」](#一五看不見的效能稅為什麼調優的本質是少過邊檢站)
  - [稅收一：Syscall / Mode Switch](#稅收一syscall--mode-switch--空間邊界的邊檢站)
  - [稅收二：Context Switch](#稅收二context-switch--時間碎片的車道切換)
  - [稅收三：Data Copy](#稅收三data-copy--搬運工的體力活)
  - [稅收四：Interrupt (IRQ)](#稅收四interrupt-irq--強制停車檢查)
- [二、縱向分析：從經典 I/O 模型到現代 Linux 資料路徑](#二縱向分析從經典-io-模型到現代-linux-資料路徑)
  - [2.1 I/O 模型演進：blocking → epoll](#21-io-模型演進blocking--epoll)
  - [2.2 Readiness Model 的邊界](#22-readiness-model-的邊界)
  - [2.3 NIC Queue → IRQ → NAPI → sk_buff → Socket Queue：收包全路徑](#23-nic-queue--irq--napi--sk_buff--socket-queue收包全路徑)
  - [2.4 Linux 多核網路擴展：RSS / RPS / RFS / XPS](#24-linux-多核網路擴展rss--rps--rfs--xps)
  - [2.5 Syscall Batching：recvmmsg / sendmmsg](#25-syscall-batchingrecvmmsg--sendmmsg)
  - [2.6 io_uring 在 Network Path 的真實位置](#26-io_uring-在-network-path-的真實位置)
- [三、橫向分析：博弈 / 電商 K8s 服務的調優圖譜](#三橫向分析博弈--電商-k8s-服務的調優圖譜)
  - [3.1 端到端資料路徑圖](#31-端到端資料路徑圖)
  - [3.2 情境一：Tail Latency / Jitter](#32-情境一tail-latency--jitter)
  - [3.3 情境二：高連線 / Burst 壓力](#33-情境二高連線--burst-壓力)
  - [3.4 情境三：Core Hotspot / CPU 不均](#34-情境三core-hotspot--cpu-不均)
  - [3.5 情境四：選型與中長期改造](#35-情境四選型與中長期改造)
- [四、橫縱交匯洞察](#四橫縱交匯洞察)
- [五、交付表格與清單](#五交付表格與清單)
  - [5.1 症狀對照表](#51-症狀對照表)
  - [5.2 命令手冊](#52-命令手冊)
  - [5.3 選型決策表](#53-選型決策表)
  - [5.4 K8s 映射表](#54-k8s-映射表)
  - [5.5 Go 映射表](#55-go-映射表)
  - [5.6 調優 Checklist](#56-調優-checklist)
- [六、進階延伸](#六進階延伸)
- [來源](#來源)

---

## 一、一句話定義

Linux 網路 I/O 的工作本質不是「收發封包」四個字，而是：

> **資料在 NIC queue → IRQ → softirq → sk_buff → socket queue → wakeup → user-space syscall → application runtime 之間怎麼流動，每一段的排隊、喚醒、CPU 調度開銷，最終如何放大成 tail latency 與連線承載問題。**

當你在 K8s 上跑 Go HTTP/gRPC 服務，經過 Nginx Ingress 收流量時，你面對的不是一個「快或慢」的二元問題，而是一條多段 pipeline——任何一段的 queue 堆積、CPU locality 錯位、wakeup 延遲，都會在 p99/p999 上留下痕跡。

---

## 一‧五、看不見的效能稅：為什麼調優的本質是「少過邊檢站」

> **工程師金句**：「效能優化的本質，就是與作業系統設計中的『安全性稅收』與『多工公平性稅收』進行的一場零和博弈。」

在進入具體的 I/O 模型和收包路徑之前，你需要先理解一個前提：**Linux 為了安全和穩定，設下了好幾道邊界，每道邊界都有通行代價**。你在這篇報告裡看到的所有調優手段（epoll、io_uring、RSS、NAPI、busy poll），本質上都在做同一件事——**減少穿越這些邊界的次數或成本**。

如果不先理解這些「隱形稅收」，你會知道 io_uring 比 epoll 好，但不知道**為什麼好**；知道 context switch 不好，但不知道**它到底在燒什麼**。

### 稅收一：Syscall / Mode Switch —— 空間邊界的邊檢站

**類比**：想像你在一棟辦公大樓裡工作（User Space），但所有重要檔案都鎖在地下金庫（Kernel Space）。每次你需要拿一份文件，你必須：走到電梯 → 刷門禁卡（權限檢查）→ 搭電梯下去 → 拿文件 → 搭電梯回來 → 重新刷卡進辦公室。即使拿文件本身只要 3 秒，整套流程可能花 30 秒。

Linux 為了保護系統穩定，將記憶體與權限嚴格劃分為 **User Space（用戶態）** 和 **Kernel Space（內核態）**。Application 無法直接操作網卡或磁碟——當你呼叫 `read()`、`write()`、`epoll_wait()` 這類 syscall 時，CPU 必須執行一次 **mode switch**：

```
User Mode                            Kernel Mode
────────                            ────────────
你的程式在這裡跑                      網卡、磁碟、socket 在這裡管
                    ─── syscall ──→
                    保存暫存器
                    切換權限等級
                    切換 page table (KPTI)
                    ←── 返回 ───
                    恢復暫存器
                    TLB 可能失效
```

每次穿越這道邊界，CPU 要付出的代價：

| 動作 | 消耗 | 為什麼痛 |
|------|------|---------|
| **暫存器保存與恢復** | ~10-20ns | 要把 CPU 當前的工作狀態完整保留，回來時再還原 |
| **權限等級切換** | ~5ns | CPU 從 Ring 3 → Ring 0，修改 CS/SS 暫存器 |
| **KPTI page table 切換** | ~50-100ns | 2018 年 Meltdown 修補後新增。進出 kernel 時切換整張 page table，防止 user-space 偷看 kernel 記憶體 |
| **TLB flush / miss** | ~100-300ns | **這是最痛的**。TLB (Translation Lookaside Buffer) 是 CPU 的「地址翻譯快取」。page table 一切換，TLB 裡的快取大量失效 → 後續記憶體訪問出現 cache miss → 連鎖性的延遲 |

**合計**：一次 syscall 的 overhead 在 Meltdown 修補前約 ~100ns，修補後約 **~300-500ns**。

**為什麼這很重要**：如果你每秒發 50 萬次 `recvfrom()`（UDP 高 PPS 場景），光 syscall 的通行稅就吃掉 150-250ms 的 CPU 時間/秒——一個核心的 15-25% 花在「過邊檢站」而不是在做正事。

**本報告中對應的解法**：

| 策略 | 手段 | 怎麼省稅 |
|------|------|---------|
| 批量過站 | `recvmmsg` / `sendmmsg`（[§2.5](#25-syscall-batchingrecvmmsg--sendmmsg)） | 一次 syscall 帶 100 個 datagram，平均每個 datagram 的稅降到 1/100 |
| 不過站 | `io_uring` 共享記憶體（[§2.6](#26-io_uring-在-network-path-的真實位置)） | SQ/CQ 在 user/kernel 共享記憶體，提交和取回結果都不需要 syscall |
| 減少過站次數 | 更大的 read buffer、Go runtime netpoll 封裝 | 一次 `read()` 讀 64KB 比四次 `read()` 各讀 16KB 省三次 syscall |

### 稅收二：Context Switch —— 時間碎片的車道切換

**類比**：想像一條高速公路只有 4 條車道（4 顆 CPU），但有 10000 輛車（10000 個 thread）要同時跑。OS scheduler 的做法是：讓每輛車跑幾百公尺就靠邊停，換下一輛上來跑。每次「靠邊停 → 換車」的過程就是 context switch——你要熄火、記住油門位置（保存暫存器）、讓新車啟動、暖引擎（載入新車的快取）。

當 OS scheduler 決定把 CPU 從 Task A 切換到 Task B，CPU 必須：

1. **保存 Task A 的所有暫存器**（程式計數器、堆疊指標、通用暫存器等）到記憶體
2. **載入 Task B 的暫存器**
3. **切換 page table**（如果 A 和 B 是不同 process）
4. **承受 L1/L2 cache 失效**——這是最隱蔽的代價。Task A 剛好把自己常用的資料暖進了 CPU cache，切換到 Task B 後，B 的資料不在 cache 裡 → 大量 cache miss → 記憶體訪問從 ~1ns（L1 hit）退化到 ~50-100ns（L3/DRAM）

**兩種 Context Switch**：

| 類型 | 觸發原因 | 場景 | 代價 |
|------|---------|------|------|
| **自願切換 (Voluntary CS)** | Thread 主動放棄 CPU（呼叫 `read()` 後睡覺等資料、mutex 搶不到） | Blocking I/O、鎖等待 | CPU 被釋放可做別的事，但喚醒時要重新載入上下文 |
| **非自願切換 (Involuntary CS)** | CPU 時間片用完，被 OS 強制踢下來 | 高負載時 thread/goroutine 太多 | **更痛**——Task A 正在做正事但被打斷，cache 暖了一半就被沖掉 |

**定量感受**：一次 context switch 的成本通常在 **1µs - 5µs**。看似很小，但：

```
假設每秒 100,000 次 context switch（高併發下很常見）：
  保守估計 2µs/次 → 0.2 秒/秒的 CPU 時間花在「換車道」
  = 一個核心 20% 的時間在做無用功
  如果有 4 個核心都這樣 → 整台機器近 1 個核心的算力浪費在切換上
```

**為什麼 Blocking I/O 在高併發下不行**：一萬個連線 = 一萬個 thread。大部分 thread 在睡覺等資料（自願 CS），但每次資料到達就要喚醒 → 頻繁 CS。OS scheduler 光是決定「誰該醒、誰該睡」就忙得不可開交。

**本報告中對應的解法**：

| 策略 | 手段 | 怎麼省稅 |
|------|------|---------|
| 減少 thread 數量 | `epoll` 事件驅動（[§2.1](#21-io-模型演進blocking--epoll)） | 一個 thread 管上萬個 fd，不需要一個連線一個 thread |
| M:N 調度 | Go goroutine（[§5.5](#55-go-映射表)） | 數萬 goroutine 映射到少量 OS thread，goroutine 切換成本 ~200ns（比 OS thread 的 ~2µs 快 10 倍） |
| 避免不必要的 wakeup | `EPOLLEXCLUSIVE`、`SO_REUSEPORT`（[§2.2](#22-readiness-model-的邊界)） | 消除 thundering herd → 減少「叫醒又沒事做」的白跑 CS |

### 稅收三：Data Copy —— 搬運工的體力活

**類比**：你在二樓辦公室（User Space），快遞到了放在一樓櫃台（Kernel Buffer）。你不能直接拿——保安要幫你從一樓搬到二樓。如果包裹很大、或一樓和二樓不在同一棟樓（跨 NUMA node），搬運時間就更長。

當 application 呼叫 `read()` 從 socket 讀取資料時，kernel 必須把資料從 **kernel buffer（sk_buff）** 複製到 **user-space buffer**。這個複製是 `memcpy` 等級的操作——CPU 一個 byte 一個 byte 搬。

| 情況 | 延遲 | 原因 |
|------|------|------|
| 同 NUMA node、資料在 L3 cache | ~幾微秒 | CPU 和記憶體很近，cache hit |
| 同 NUMA node、資料不在 cache | ~10-20µs | 要去 DRAM 拿，但至少在同一個記憶體控制器 |
| **跨 NUMA node** | ~20-60µs | CPU 在 NUMA node 0，但 sk_buff 被分配在 NUMA node 1 的記憶體 → 要走 QPI/UPI 匯流排到另一顆 CPU 的記憶體控制器取資料，延遲 ×2-3 |

**為什麼跨 NUMA 會發生**：封包被 CPU 0（NUMA node 0）的 softirq 收進來 → sk_buff 分配在 node 0 的記憶體。但你的 application thread 跑在 CPU 8（NUMA node 1）→ `read()` 時要做跨 node 的 memory access。

**本報告中對應的解法**：

| 策略 | 手段 | 怎麼省稅 |
|------|------|---------|
| 讓收包和讀取在同一 CPU | RFS（[§2.4](#24-linux-多核網路擴展rss--rps--rfs--xps)） | 把封包導向正在處理該 flow 的 CPU |
| 完全不搬 | io_uring zero-copy send（[§2.6](#26-io_uring-在-network-path-的真實位置)） | 資料直接從 user buffer DMA 到 NIC，不經過 kernel buffer |
| 觀測問題 | `perf c2c`、`numastat`（[§3.2](#32-情境一tail-latency--jitter)） | 找出跨 NUMA 的 memory access 熱點 |

### 稅收四：Interrupt (IRQ) —— 強制停車檢查

**類比**：你正在高速公路上全速開車（CPU 在執行你的程式），突然路邊有人揮紅旗把你攔下來（硬體中斷）：「有封包到了，你必須現在處理！」你被迫停車、處理完再重新加速。如果每秒被攔 100 萬次，你根本跑不了多遠。

NIC 收到封包後，用**硬體中斷 (hard IRQ)** 通知 CPU。CPU 收到中斷後，會**立刻暫停**手上正在做的任何事（不管是你的 application、GC、還是另一個 syscall），跳到中斷處理函式。

中斷的代價：

| 動作 | 消耗 |
|------|------|
| 暫停當前執行流 + 保存現場 | ~100ns |
| 執行 IRQ handler | ~200-500ns（Linux 的 hard IRQ handler 做的事很少，主要就是標記 NAPI poll） |
| 恢復現場 + 繼續執行 | ~100ns |
| **附帶傷害：cache 污染** | 中斷 handler 的 code 和 data 擠進 cache → 你原本的工作資料被趕出去 → cache miss |

**中斷風暴**：當 PPS 到百萬級，如果每個封包都觸發一次中斷，CPU 光處理中斷就花掉大部分時間，沒空做真正的應用邏輯。

**本報告中對應的解法**：

| 策略 | 手段 | 怎麼省稅 |
|------|------|---------|
| 中斷合併 + 批量處理 | NAPI poll（[§2.3](#23-nic-queue--irq--napi--sk_buff--socket-queue收包全路徑)） | 第一個封包觸發中斷，之後改 polling 批量收包，不再逐個中斷 |
| 分散中斷到多核 | RSS / RPS（[§2.4](#24-linux-多核網路擴展rss--rps--rfs--xps)） | 多個 NIC queue 的中斷分到不同 CPU，避免單核被打滿 |
| 完全跳過中斷路徑 | busy poll（[§3.2](#32-情境一tail-latency--jitter)） | Application 自己直接 poll NIC ring buffer，跳過 IRQ → softirq → wakeup |

### 四種稅收的全景對照

```
┌─────────────────────────────────────────────────────────────────────┐
│                        效能稅收全景圖                                │
│                                                                     │
│   稅收類型          單次成本        高併發下的累積效應                 │
│   ─────────        ────────        ──────────────────               │
│   Syscall          300-500ns       50萬次/秒 → 吃掉 15-25% 單核      │
│   Context Switch   1-5µs          10萬次/秒 → 吃掉 10-50% 單核      │
│   Data Copy        5-60µs         跨 NUMA 時延遲 ×2-3               │
│   IRQ              0.5-1µs        百萬 PPS → CPU 光處理中斷就飽和     │
│                                                                     │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │  核心啟示：                                                  │   │
│   │  1. 物理界限決定效能上限 — 所有調優都在規避 OS 的邊界開銷      │   │
│   │  2. 併發 ≠ 並行 — 過多 CS 把 CPU 變成「只會搬家、不做事」     │   │
│   │  3. 效能是省出來的 — 最高級的調優是讓 CPU 減少無謂的狀態切換   │   │
│   └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

有了這個「稅收」心智模型，接下來的所有技術演進和調優手段都可以用一句話解釋：**它幫你省了哪種稅、省了多少**。

---

## 二、縱向分析：從經典 I/O 模型到現代 Linux 資料路徑

### 2.1 I/O 模型演進：blocking → epoll

#### 演進主線：每一步在解什麼痛

```
blocking I/O
    ↓  痛點：一個 thread 只能等一個連線，連線多了 thread 爆炸
non-blocking I/O
    ↓  痛點：不卡了，但要自己不停檢查，CPU 空轉 (busy poll)
select / poll
    ↓  痛點：能同時等了，但每次要把整份 fd 清單掃一遍
epoll
    ↓  痛點：效率夠了，但 syscall 本身仍有成本（尤其 Meltdown 後）
io_uring
```

#### Step 1 → 2：blocking 為什麼撐不住高併發

Blocking I/O 的運作方式：你呼叫 `read(fd, buf, len)`，如果對面的資料還沒送到，kernel 直接把你的 thread 從 CPU 上拿下來放進等待佇列（sleep）。等資料到了，kernel 再把你叫醒，把資料複製到你的 buffer，`read()` 才返回。

這在低連線數時完全沒問題——一個 thread 服務一個 client，邏輯清晰。但當連線數到幾千、上萬時，問題就來了：

- **每個連線需要一個 thread**：Linux 預設 thread stack 是 8MB。1000 個連線 = 8GB 光 stack 就吃掉了。
- **context switch 成本**：1000 個 thread 頻繁被喚醒、睡下去，OS scheduler 光是切換就花掉大量 CPU（保存/恢復暫存器、flush TLB、cache miss）。
- **大部分 thread 在睡覺**：高併發時多數連線其實是閒置的（等 client 慢慢傳），thread 睡在那裡什麼事都沒做，但記憶體照吃。

所以第一步改進很直覺：**能不能不要讓 thread 睡死？**

#### Step 2 → 3：non-blocking 為什麼不夠

Non-blocking I/O 解決了「thread 睡死」的問題：你把 socket 設成 `O_NONBLOCK`，呼叫 `read()` 時如果沒有資料，kernel 不會讓你睡，而是立刻返回一個錯誤碼 `EAGAIN`（意思是「現在沒東西，晚點再來」）。

聽起來很好，但問題在於：**你要自己安排「晚點再來」這件事**。

最天真的做法就是寫個 loop 一直重試：

```c
while (1) {
    ret = read(fd, buf, len);
    if (ret > 0) break;         // 有資料了
    if (errno == EAGAIN) continue; // 沒資料，再試
}
```

這就是 **busy polling**——CPU 在 loop 裡全速空轉，每秒可能檢查幾百萬次，但真正有資料的可能只有幾次。CPU utilization 100% 但都在做無用功。

而且如果你有 1000 個 socket 都要管，你要一個一個輪流問「你有資料了嗎？」，問完一輪可能根本沒有任何 socket 有資料——白跑一圈。

所以下一步的需求是：**能不能讓 kernel 幫我盯著一大群 socket，誰真的有資料再告訴我？**

#### Step 3 → 4：select / poll 為什麼被 epoll 取代

`select` 和 `poll` 做的事情很像：你把一堆 fd（file descriptor）打包交給 kernel，說「幫我看看這裡面誰可讀、誰可寫」。kernel 檢查完畢後返回，告訴你哪些 fd 有事件。

這解決了 busy polling 的問題——你不用自己一個一個問了。但它們有自己的效能天花板：

**select 的問題：**
- fd 數量有上限：`FD_SETSIZE` 通常是 1024，寫死在編譯時。超過 1024 個連線就不能用了。
- 每次呼叫都要把整份 fd 集合從 user-space 複製到 kernel-space。
- kernel 回傳後，你要自己把整份集合掃一遍，才知道是哪些 fd 有事件。

**poll 的改進：**
- 沒有 1024 的限制了（用 `pollfd` array，可以自己開大）。
- 但核心問題沒變：每次呼叫仍然要把整份 fd 列表傳進去，kernel 仍然要線性掃描，你也仍然要線性掃描返回結果。

也就是說，如果你有 10000 個連線但只有 3 個有事件，select/poll 每次仍然要掃完 10000 個才能找到那 3 個。時間複雜度是 O(n)，n 是總 fd 數量。

**epoll 怎麼解決：**

epoll 換了一套做法：

1. **`epoll_create`**：先建立一個 epoll instance（一個 kernel 物件）
2. **`epoll_ctl`**：用 `EPOLL_CTL_ADD` 把 fd 註冊進去。這一步只做一次，不需要每次都傳整份列表。
3. **`epoll_wait`**：等事件。kernel 內部維護一個 **ready list**——每當某個 fd 有事件（例如收到資料），kernel 直接把它加進 ready list。`epoll_wait` 返回的只有 ready list 裡的 fd。

關鍵差異：

| | select/poll | epoll |
|---|---|---|
| 每次呼叫需要傳入的資料 | 整份 fd 列表 | 不需要（fd 已經透過 `epoll_ctl` 註冊） |
| kernel 掃描方式 | 線性掃描所有 fd | 只返回有事件的 fd（ready list） |
| 返回後應用需要做的事 | 掃描整份列表找有事件的 | 直接遍歷返回的事件 |
| 時間複雜度 | O(總 fd 數) | O(有事件的 fd 數) |
| fd 上限 | select: 1024；poll: 無硬限制但效能退化 | 無硬限制，效能不隨總 fd 數退化 |

這就是為什麼 10000 個連線中只有 3 個活躍時，epoll 遠比 select/poll 高效。

#### Step 4 → 5：epoll 還有什麼省不掉

epoll 已經足夠好，絕大多數高併發服務停在這裡。但如果你深入看，每次 `epoll_wait → read/write` 仍有成本：

1. **syscall 成本**：`epoll_wait` 本身是一次 syscall，`read()` 又是一次。每次 syscall 都要 user → kernel mode switch。在 Meltdown/Spectre 修補之後，這個 mode switch 可能還需要做 KPTI（Kernel Page Table Isolation）→ TLB flush，成本更高。
2. **兩步模型**：epoll 告訴你「ready 了」，你還要自己呼叫 `read()` 去拿資料（readiness model）。這兩步之間有排程間隔。

`io_uring` 的思路是：

- 把 readiness model 換成 **completion model**——你提交「幫我讀這個 fd」的請求，kernel 做完後直接把結果放在共享記憶體裡，你只需要去撿。
- submission 和 completion 透過共享記憶體的 ring buffer 傳遞，可以完全不需要 syscall（SQPOLL 模式）。
- 一次可以提交多個 I/O 請求（batching），進一步減少 syscall 次數。

但 io_uring 的門檻和限制也很明確——詳見 [§2.6](#26-io_uring-在-network-path-的真實位置)。

#### 為什麼高併發主流停在 epoll 而不是 AIO

你可能會問：Linux 不是一直有 AIO（Asynchronous I/O）嗎？它不就是 completion-based 嗎？

📖 答案是：Linux 有兩套 AIO，但都不適合 network I/O。

- **POSIX AIO**（`aio_read`）：在 glibc 層用 thread pool 模擬的。每次「async I/O」其實是背景開一個 thread 去做 blocking read。這不是真正的 kernel async，開銷反而更大。
- **Linux native AIO**（`io_submit`）：真正的 kernel-level async，但設計上主要面向 **direct I/O on block device**（磁碟）。對 socket fd 要嘛不支援，要嘛行為不符合預期。

所以直到 `io_uring`（kernel 5.1+, 2019 年）出現之前，Linux network I/O 沒有可用的 completion-based 方案。過去二十年的主流技術棧就是：

```
non-blocking fd + epoll (readiness notification) + event loop / thread pool
```

Nginx、HAProxy、Redis、Go runtime netpoll、Node.js libuv 都是這條線的產物。

#### epoll 的兩種觸發模式

epoll 有兩種方式通知你「fd 有事件」：

**Level Triggered (LT)**——水平觸發：

只要 fd 的 buffer 裡還有資料沒讀完，**每次你呼叫 `epoll_wait` 都會再告訴你一次**。就像一個鬧鐘，只要鍋裡還有水就一直響。

- 好處：不怕漏讀。你這次只讀了一部分，下次 `epoll_wait` 還會提醒你。
- 壞處：如果 fd 上有資料但你暫時不想處理，它會反覆通知你，產生多餘的 wakeup。

**Edge Triggered (ET)**——邊緣觸發：

只在 fd 的狀態**發生變化**時通知你一次。例如：原本 buffer 是空的，現在來了資料 → 通知一次。之後即使 buffer 裡還有資料沒讀完，也不會再通知了。就像一個鬧鐘只在水位上升時響一聲。

- 好處：通知次數少，不會反覆 wakeup，更省 CPU。
- 壞處：你必須在收到通知時**一次讀到 `EAGAIN`**（讀到沒東西為止），否則剩下的資料會永遠待在 buffer 裡，而 epoll 不會再通知你。這是 ET 最容易踩的坑。

| 模式 | 行為 | 典型使用者 | 需要注意 |
|------|------|-----------|---------|
| LT（預設） | 只要 fd 仍有資料可讀，每次 `epoll_wait` 都會回報 | libevent 預設 | 簡單但可能產生多餘 wakeup |
| ET | 只在狀態變化時回報一次，之後要自己讀到 `EAGAIN` | Nginx、Go netpoll | 必須一次讀完，否則會 miss event |

📖 `epoll(7)` man page 明確說明：ET 模式下若不讀到 `EAGAIN`，後續資料到達可能不會再觸發事件。

🔧 **Go runtime 的 netpoll** 在 Linux 上使用 **ET 模式** + `EPOLLET | EPOLLRDHUP`。但 Go 開發者通常不需要擔心 ET 的複雜度，因為 runtime 在 goroutine 層面做了封裝：當 goroutine 呼叫 `net.Conn.Read()` 時，如果底層 fd 返回 `EAGAIN`，runtime 會把這個 goroutine 掛起來（park），等 netpoll 收到下一次 epoll 事件再喚醒它。對你來說就像在做 blocking read，但背後不佔 OS thread。

### 2.2 Readiness Model 的邊界

epoll 是 readiness-based：它告訴你「fd ready 了，你可以去讀」，但**不幫你讀**。這看起來像是小事，但在高併發場景下，readiness model 有三個邊界問題會直接影響 tail latency：

#### 邊界 1：wakeup 到 read 之間有延遲

`epoll_wait` 返回後，事情並沒有做完。完整路徑是：

```
epoll_wait 返回（你知道 fd ready 了）
  → 你的 thread/goroutine 需要被 OS scheduler 排到 CPU 上
  → 你呼叫 read()
  → kernel 把資料從 kernel buffer (sk_buff) 複製到你的 user-space buffer
  → read() 返回
```

在這條路上，「scheduler 排到 CPU」這一步可能會有延遲。如果你的 CPU 正在忙（做其他 goroutine 的事、處理 softirq、跑 GC），你的 thread 要排隊等 CPU 時間片。在正常情況下可能只等幾十微秒，但在 CPU 繁忙時可能等好幾毫秒——這就是 tail latency 的其中一個來源。

🔧 在 Go 裡面，這反映成 `scheduler latency`：goroutine 被 netpoll 放回 run queue，但要等到有空閒的 P 才能執行。如果同時有大量 goroutine 在 run queue 裡排隊，延遲就會被放大。

#### 邊界 2：thundering herd（驚群效應）

想像一個場景：你的 Nginx 有 8 個 worker process，它們都在 `epoll_wait` 同一個 listen socket，等新連線進來。現在一個新連線到了，kernel 發出 accept 事件——

**誰應該被喚醒？**

理論上只需要一個 worker 去 accept 這個連線就好。但在早期的 epoll 實作中，kernel 可能把 **所有** 等待中的 worker 都喚醒。結果 8 個 worker 爭搶同一個連線，7 個失敗（`accept()` 返回 `EAGAIN`），然後又睡回去。

這就是 thundering herd：大量不必要的 wakeup → 大量白跑的 context switch → 浪費 CPU。

📖 Linux 提供了兩種解決方案：

- **`EPOLLEXCLUSIVE`**（Linux 4.5+）：加了這個 flag 後，kernel 保證同一個事件只喚醒一個（或少數幾個）等待者，而不是全部。Nginx 1.11.3+ 在 Linux 4.5+ 上會自動啟用。

- **`SO_REUSEPORT`**（Linux 3.9+）：更根本的解法。讓每個 worker bind 到同一個 `ip:port`，但 **每個 worker 有自己獨立的 listen socket 和 accept queue**。kernel 在底層用 hash（基於來源 IP:port）決定新連線進哪個 worker 的 queue。這樣連「同一個 accept queue 被多人搶」這件事本身都消失了。

#### 邊界 3：readiness ≠ data ready in user-space

epoll 說「fd ready 了」，意思是「kernel buffer 裡有資料了」。但你呼叫 `read()` 時，kernel 還要做一件事：把資料從 kernel buffer（sk_buff）複製到你的 user-space buffer。

這個複製不是免費的：

- **正常情況**：sk_buff 和你的 user buffer 在同一個 NUMA node 的記憶體，複製很快（幾微秒）。
- **不好的情況**：封包被某個 CPU 收進來（softirq 在 CPU 0 上跑），sk_buff 分配在 NUMA node 0 的記憶體。但你的 application thread 跑在 CPU 15（NUMA node 1）→ `read()` 要做跨 NUMA 的 memory access，延遲可能 ×2-3。

這個問題用 `perf c2c`（cache-to-cache）可以觀測，用 RFS（把封包導向 application 所在的 CPU）可以緩解。

### 2.3 NIC Queue → IRQ → NAPI → sk_buff → Socket Queue：收包全路徑

這是理解 tail latency 的關鍵。一個封包從網線到 application 要經過的每一站：

```
                          ┌─────────────────────────────────────────────────┐
                          │              Hardware / NIC                     │
                          │                                                 │
  wire ──→ NIC RX ring ──┤  DMA 寫入 pre-allocated skb / page             │
           buffer         │  NIC 觸發 hard IRQ                             │
                          └───────────────┬─────────────────────────────────┘
                                          │
                          ┌───────────────▼─────────────────────────────────┐
                          │              Hard IRQ handler                    │
                          │                                                 │
                          │  1. 記錄 NAPI 需要 poll                         │
                          │  2. 觸發 softirq (NET_RX_SOFTIRQ)              │
                          │  3. 返回（盡快，減少 hard IRQ 時間）             │
                          └───────────────┬─────────────────────────────────┘
                                          │
                          ┌───────────────▼─────────────────────────────────┐
                          │              NAPI poll (softirq context)         │
                          │                                                 │
                          │  1. 從 NIC ring buffer 批量收包                  │
                          │  2. 每個包建立 / 填充 sk_buff                    │
                          │  3. 送入協議棧：ip_rcv → tcp_v4_rcv              │
                          │  4. 資料放入 socket receive queue                │
                          │  5. 喚醒等待在該 socket 上的 task               │
                          │                                                 │
                          │  budget 用完（預設 300 packets/輪）就讓出 CPU    │
                          └───────────────┬─────────────────────────────────┘
                                          │
                          ┌───────────────▼─────────────────────────────────┐
                          │              Socket Receive Queue               │
                          │                                                 │
                          │  sk->sk_receive_queue (sk_buff 鏈表)            │
                          │  受 SO_RCVBUF / tcp_rmem 控制                   │
                          └───────────────┬─────────────────────────────────┘
                                          │
                          ┌───────────────▼─────────────────────────────────┐
                          │              Application read() / recv()        │
                          │                                                 │
                          │  skb_copy_datagram_msg: kernel → user-space     │
                          │  copy 完成後釋放 sk_buff                         │
                          └─────────────────────────────────────────────────┘
```

#### 每一站到底在發生什麼事

**第 1 站：NIC RX Ring Buffer**

> 🍣 **類比：迴轉壽司台**。Ring buffer 就像一條環形的迴轉壽司輸送帶——廚師（NIC）不斷往帶子上放壽司（封包），客人（CPU）從帶子上拿。如果客人吃得太慢，帶子一圈轉回來時位子被佔滿，廚師只能把新壽司丟掉。

網卡收到封包後，要把資料放到記憶體裡讓 CPU 來處理。但 NIC 和 CPU 是非同步運作的——NIC 隨時可能收到封包，CPU 可能正在忙別的事。所以中間需要一個 **緩衝區**。

NIC RX ring buffer 就是這個緩衝區。它是一個固定大小的環形佇列，通常有 256-4096 個 slot。NIC 透過 **DMA（Direct Memory Access，直接記憶體存取——NIC 硬體直接把資料寫進 RAM，完全不需要 CPU 幫忙搬運）** 直接把封包資料寫進預先分配好的記憶體位置，不需要 CPU 參與——這是高效率的關鍵。

問題是：如果 CPU 處理速度跟不上封包到達速度，ring buffer 會**滿**。滿了之後新到的封包直接被丟棄（NIC 層面的丟包），TCP 層看到的是 retransmission，application 看到的是延遲上升或 timeout。

- 觀測：`ethtool -S eth0` 看 `rx_missed_errors` 或 `rx_no_buffer_count`
- 調整：`ethtool -G eth0 rx 4096`（增大 ring buffer，給 CPU 更多緩衝時間）

**第 2 站：Hard IRQ → Softirq（兩階段中斷）**

> 🚨 **類比：119 報案 vs 消防隊出勤**。Hard IRQ 就像 119 接線員——電話一響就必須立刻接（最高優先級），但接線員只做一件事：記下地址、派消防隊出動（觸發 softirq）。真正的滅火工作（收包處理）由消防隊（softirq / NAPI poll）來做，因為消防隊可以同時處理多起火警、可以被調度。如果讓接線員自己去滅火，那其他報案電話就沒人接了。

NIC 把封包放進 ring buffer 後，需要通知 CPU「有東西來了」。通知方式就是觸發一個**硬體中斷（hard IRQ）**。

CPU 收到中斷後，會暫停手上的工作，跳到中斷處理函式執行。但 hard IRQ 的處理要盡可能快（因為它會阻塞該 CPU 上的所有其他工作），所以 Linux 的做法是：在 hard IRQ 裡只做最少的事——記錄「NAPI 需要 poll」然後觸發一個**軟體中斷（softirq）**，把真正的收包處理交給 softirq。softirq 的優先級比一般 process 高但比 hard IRQ 低，可以被其他 hard IRQ 打斷，不會長時間霸佔 CPU。

hard IRQ 本身的問題是：**每個 NIC queue 的中斷通常綁定到一個 CPU**。如果 NIC 只有一個 RX queue，那所有封包的中斷都打到同一個 CPU → 該 CPU 的中斷處理就成了瓶頸。

- 觀測：`cat /proc/interrupts | grep eth` 看每個 CPU 收到多少中斷
- 調整：配合 RSS（多 queue）+ IRQ affinity 把不同 queue 的中斷分到不同 CPU

**第 3 站：NAPI Poll（softirq 上下文）**

> 📦 **類比：批次收發快遞**。想像你是一個倉庫管理員。如果每來一個包裹就跑到門口簽收，一天來 100 萬個包裹你就光跑門口了。NAPI 的做法是：第一個包裹到時跑去門口開門，然後跟快遞員說「你把包裹都堆門口，我一次搬 300 個進來」。搬完了，快遞員再按門鈴通知下一批。

📖 **NAPI (New API)** 是 Linux 為了解決「中斷風暴」問題而設計的機制。

問題是這樣的：如果每收到一個封包就觸發一次 hard IRQ，那當 PPS（Packets Per Second）到達百萬級時，CPU 光處理中斷就忙不過來，沒有時間做真正的協議處理和 application 邏輯。

NAPI 的做法是**在高流量時從 interrupt-driven 切換到 polling mode**：

1. 第一個封包到達時觸發一次 hard IRQ。
2. hard IRQ handler 把 NIC 的 NAPI 結構排進 softirq 的 poll 列表，然後**暫時關閉該 queue 的中斷**。
3. softirq 開始 polling：直接從 ring buffer 批量取封包，不再等中斷。
4. 每次 poll 最多處理 `netdev_budget` 個封包（預設 300）。如果 budget 用完了但 ring buffer 還有包，softirq 退出讓 CPU 做別的事，稍後再進來繼續 poll。
5. 如果 ring buffer 空了（封包處理完），重新開啟中斷，回到 interrupt-driven 模式。

這個切換機制讓 Linux 在低流量時有快速回應（中斷驅動），高流量時有高吞吐（polling 驅動）。

- **time_squeeze** 的意義：`/proc/net/softnet_stat` 的第 2 列記錄「softirq 想繼續 poll 但 budget/time 用完被迫退出」的次數。如果這個值持續增長，說明 softirq 處理不及 → 收包延遲增加。

NAPI poll 階段還會建立或填充 **sk_buff**（socket buffer）。

> 🪪 **類比：封包的身分證 + 行李箱**。sk_buff 就像每個封包隨身攜帶的一個文件夾，裡面裝著這個封包的所有資訊：「我從哪來（源 IP:port）、我要去哪（目標 IP:port）、我的內容在哪裡（payload pointer）、我走到哪一步了（protocol metadata）」。kernel 每收到一個封包就要新建一個 sk_buff → 封包被 application 讀完就要銷毀它。

sk_buff 是 Linux kernel 用來表示一個網路封包的核心資料結構，包含所有的 header pointer、payload pointer、protocol metadata。在高 PPS 場景，sk_buff 的分配（`__alloc_skb`）和釋放（`kfree_skb`）是顯著的 CPU 開銷——每個封包都要走一次記憶體分配器，百萬 PPS 就是每秒百萬次 `kmalloc`/`kfree`。

**第 4 站：協議棧處理**

sk_buff 建立後，會依序經過 Linux 協議棧：

- `ip_rcv()`：IP 層處理（檢查 header、路由決策）
- `tcp_v4_rcv()`：TCP 層處理（checksum 驗證、sequence number 驗證、狀態機、ACK 生成）
- 最終把 payload 放進對應 socket 的 **receive queue**

**第 5 站：Socket Receive Queue**

每個 TCP socket 都有一個 receive queue（`sk->sk_receive_queue`），是一個 sk_buff 的鏈表。TCP 協議棧把處理好的資料放進這個 queue，然後喚醒正在等待的 application thread/goroutine。

queue 的大小受 `SO_RCVBUF`（per-socket）和 `net.ipv4.tcp_rmem`（全域預設）控制。如果 queue 滿了：
- TCP 會縮小 receive window（在 ACK 裡告訴對端「我接收不了那麼多了」）
- 對端被迫減慢發送速度
- 端到端延遲上升

這也是為什麼 socket queue 堆積通常不是 NIC 或 kernel 的問題，而是 **application 讀取速度不夠快**——handler 太慢、goroutine 太多排不到 CPU、GC pause 等。

**第 6 站：Application read()**

Application 呼叫 `read()` 或 `recv()` 時，kernel 執行 `skb_copy_datagram_msg()`：把 sk_buff 裡的 payload 從 kernel buffer 複製到 user-space buffer。複製完成後 sk_buff 被釋放。

#### 每一站的調優速查

| 站點 | Tail Latency 影響 | 可觀測 | 可調整 |
|------|-------------------|--------|--------|
| **NIC RX ring** | ring 滿 → NIC 層丟包 → TCP retransmit → 延遲 | `ethtool -S`（`rx_missed_errors`） | `ethtool -G` 調 ring size |
| **Hard IRQ** | IRQ 集中單核 → 該核成為瓶頸 | `/proc/interrupts` | IRQ affinity、RSS 多 queue |
| **NAPI poll** | budget 不足 → time_squeeze → 收包延遲 | `/proc/net/softnet_stat`（第 2 列） | `net.core.netdev_budget` |
| **softirq** | 處理時間過長 → `ksoftirqd` 被 scheduler 降級 → 延遲從 μs 跳到 ms | `mpstat -P ALL`（%soft） | RSS 分散 softirq |
| **sk_buff alloc** | 高 PPS 下分配/釋放壓力大 | `perf` / `eBPF` | GRO 合併封包 |
| **Socket queue** | queue 滿 → TCP window 縮小 → 全鏈路變慢 | `ss -tnpm`（Recv-Q） | `SO_RCVBUF`、`tcp_rmem` |
| **Wakeup** | goroutine/thread 不在目前 CPU → scheduler 延遲 | `runqlat`（eBPF） | CPU affinity、cgroup cpuset |
| **User-space copy** | 跨 NUMA node copy → 延遲 ×2-3 | `numastat`、`perf c2c` | RFS、NUMA-aware scheduling |

📖 **GRO (Generic Receive Offload)**：

> 📬 **類比：把零散信件合併成一個大包裹再拆信**。如果你每天收 1000 封信，每封都要單獨拆開、蓋章、歸檔，一天就做不了別的事。GRO 的做法是：先把寄給同一個收件人（同一 TCP flow）的信合成一個大包裹，蓋一次章就好。

在 NAPI poll 階段把多個屬於同一 TCP flow 的小封包合併成一個大的 sk_buff，再交給協議棧。這樣一來，協議棧只需要處理一次（而不是每個小封包都跑一次完整的 `tcp_v4_rcv`），sk_buff 分配次數也大幅減少。對 TCP 效果顯著，可用 `ethtool -K eth0 gro on` 開啟（大多數發行版預設已開）。

### 2.4 Linux 多核網路擴展：RSS / RPS / RFS / XPS

📖 來源：docs.kernel.org「Scaling in the Linux Networking Stack」

#### 為什麼需要多核擴展

從前面的收包路徑可以看到，每個封包的處理（IRQ → NAPI poll → 協議棧 → socket queue）都在**某一個 CPU 上**完成。如果所有封包都打到同一個 CPU，那這顆 CPU 會成為整個系統的瓶頸——即使你有 32 顆核心，其他 31 顆閒著也幫不上忙。

Linux 提供了四種機制來把封包處理分散到多核，可以分成收包側三種、發包側一種：

#### RSS：硬體層面的多核分流（首選）

**RSS (Receive Side Scaling)** 是最直接也最有效的方案，因為分流發生在 NIC 硬體上，完全不吃 CPU。

運作方式：

1. 現代 NIC 通常有多個 **RX queue**（例如 8 個或 16 個），每個 queue 有自己的 ring buffer 和 IRQ。
2. 當封包到達時，NIC 用封包的 4-tuple（源 IP、目標 IP、源 port、目標 port）做 hash 計算。
3. 根據 hash 值決定封包進哪個 RX queue。
4. 每個 RX queue 的 IRQ 綁定到不同的 CPU → 不同 CPU 並行處理不同 queue 的封包。

關鍵特性是：**同一個 TCP 連線（同一組 4-tuple）的封包一定進同一個 queue**，由同一個 CPU 處理。這保證了封包的有序性，也讓 CPU cache 更有效。

```bash
# 查看 NIC 支援多少 queue
ethtool -l eth0

# 設定 queue 數量（combined = RX 和 TX 共用）
ethtool -L eth0 combined 8

# 查看每個 queue 的 IRQ affinity
cat /proc/interrupts | grep eth0
# 然後看 /proc/irq/<N>/smp_affinity 確認每個 IRQ 綁在哪個 CPU
```

🔧 **大多數情況只要做好 RSS + IRQ affinity 就夠了**。這是成本最低的多核分流方案。

#### RPS：軟體層面的補充

**RPS (Receive Packet Steering)** 是 RSS 的軟體版本。它在 softirq 階段用 hash 把封包分發到其他 CPU 處理。

什麼時候需要 RPS：

- NIC 只有一個 RX queue（比較舊的網卡、某些虛擬 NIC）
- RSS queue 數量少於 CPU 核心數（例如 NIC 只有 4 queue 但有 16 核）
- K8s 環境中 veth 虛擬介面通常不支援 RSS

運作方式：封包被 NAPI 從 ring buffer 取出後，RPS 根據封包的 hash 值，用 IPI（Inter-Processor Interrupt）把這個封包轉給另一個 CPU 的 softirq 去做後續的協議棧處理。

代價是：多了一次 IPI 和一次跨核的 sk_buff 傳遞。所以如果 NIC 已經有足夠的 RSS queue，不需要再開 RPS。

```bash
# 設定 RPS：讓 rx-0 的封包可以被分散到 CPU 0-7（bitmask ff = 11111111）
echo ff > /sys/class/net/eth0/queues/rx-0/rps_cpus
```

#### RFS：讓封包去它該去的 CPU

**RFS (Receive Flow Steering)** 是 RPS 的進階版。它解決的問題是：RPS 用 hash 分流，但 hash 分到的 CPU 不一定是正在處理這個 TCP 連線的 application thread 所在的 CPU。

想像一下：
- RPS 把某個連線的封包分到 CPU 3 做協議棧處理
- 但正在 `read()` 這個 socket 的 goroutine 跑在 CPU 7
- 結果 CPU 3 處理完後要跨核喚醒 CPU 7 的 goroutine → cache miss、wakeup latency

RFS 的做法是：kernel 會記住每個 flow（socket）最後在哪個 CPU 上被 application `read()`，下次收到同一 flow 的封包時，直接把它送到那個 CPU 處理。這樣協議棧處理和 application 讀取在同一個 CPU 上 → cache 更熱、wakeup 更快。

```bash
# 全域設定 RFS flow table 大小
echo 32768 > /proc/sys/net/core/rps_sock_flow_entries

# 每個 queue 的 flow table 大小
echo 4096 > /sys/class/net/eth0/queues/rx-0/rps_flow_cnt
```

🔧 **RFS 在 Go 服務上的價值有限**：Go 的 goroutine 會在 P (processor) 之間遷移，也就是說同一個 socket 的 `read()` 可能這次在 CPU 3、下次在 CPU 7。RFS 追蹤到的「上次在哪個 CPU」很快就過期了。如果你需要 CPU locality，用 cgroup cpuset 把 Pod 固定到一組 CPU 反而更直接。

#### XPS：發包側的多核分流

**XPS (Transmit Packet Steering)** 解決的是發包側的問題。

當多個 CPU 同時要發包，但 NIC 只有少量 TX queue 時，多個 CPU 會競爭同一個 TX queue 的鎖 → 鎖競爭成為瓶頸。

XPS 的做法是：指定每個 CPU 使用哪個 TX queue。例如 CPU 0-3 用 tx-0，CPU 4-7 用 tx-1。這樣同一個 TX queue 不會被太多 CPU 同時競爭。

```bash
# 設定 CPU 0-3 使用 tx-0
echo 0f > /sys/class/net/eth0/queues/tx-0/xps_cpus
# 設定 CPU 4-7 使用 tx-1
echo f0 > /sys/class/net/eth0/queues/tx-1/xps_cpus
```

#### 四種機制的選擇順序

| 順序 | 機制 | 收/發 | 層級 | 設定方式 |
|------|------|-------|------|---------|
| 1（首選） | **RSS** | 收包 | 硬體 | `ethtool -L` + IRQ affinity |
| 2（RSS 不夠時） | **RPS** | 收包 | 軟體 | `/sys/class/net/<dev>/queues/rx-N/rps_cpus` |
| 3（需要 locality） | **RFS** | 收包 | 軟體 | `/proc/sys/net/core/rps_sock_flow_entries` |
| 4（發包競爭時） | **XPS** | 發包 | 軟體 | `/sys/class/net/<dev>/queues/tx-N/xps_cpus` |

🔧 **K8s 環境注意**：容器網路通常經過 veth pair → bridge/IPVS/eBPF。veth 是虛擬介面，不支援 RSS。如果你的 node NIC 有 RSS 但容器內的 veth 沒有，RPS 可以在 veth 層補上 softirq 的多核分散。但更好的方案是用 Cilium eBPF，它可以在 XDP 層直接分流，跳過 veth 的部分開銷。

### 2.5 Syscall Batching：recvmmsg / sendmmsg

#### 先理解 syscall 的成本

在講 batching 之前，要先理解為什麼 syscall 不是「免費的」。

你的 application 跑在 user-space，但 kernel 的功能（讀網路、讀磁碟、分配記憶體）跑在 kernel-space。每次你呼叫 `read()`、`write()`、`epoll_wait()` 這類 syscall，CPU 要做一次 **mode switch**：

1. **保存 user-space 狀態**：暫存器、stack pointer 等
2. **切換到 kernel mode**：修改 CPU 的權限等級
3. **執行 kernel 邏輯**：處理你的請求
4. **切回 user mode**：恢復你的暫存器和 stack

在 2018 年 Meltdown 漏洞修補之後，這個切換更貴了——Linux 引入了 **KPTI (Kernel Page Table Isolation)**，每次進出 kernel 都要切換 page table → 可能導致 TLB flush → cache miss 增加。一次 syscall 的 overhead 從原本的 ~100ns 可能增加到 ~300-500ns。

單次看起來微不足道，但如果你每秒收 50 萬個 UDP 封包，每個封包一次 `recvfrom()`，光 syscall overhead 就吃掉 150-250ms 的 CPU 時間/秒——佔一個核心的 15-25%。

#### recvmmsg / sendmmsg 怎麼 batch

📖 `recvmmsg(2)`（Linux 2.6.33+）和 `sendmmsg(2)`（Linux 3.0+）的做法很直接：把多次 `recvfrom` / `sendto` 合成一次 syscall。

```c
// 原本：每個 datagram 一次 syscall
for (int i = 0; i < 100; i++) {
    recvfrom(fd, buf[i], len, 0, &addr[i], &addrlen);  // 100 次 syscall
}

// 改成：一次 syscall 收 100 個 datagram
struct mmsghdr msgs[100];
// ... 設定 msgs 的 buffer ...
recvmmsg(fd, msgs, 100, 0, NULL);  // 1 次 syscall，最多收 100 個
```

一次 mode switch 的成本被 100 個 datagram 分攤，平均每個 datagram 的 syscall overhead 降低到原來的 1/100。

🔧 **實測效果**：Cloudflare 在其 DNS 服務中使用 `recvmmsg` 後，syscall overhead 減少約 30-50%，PPS 處理能力提升顯著。

#### 對 TCP 服務和 Go 的適用性

`recvmmsg/sendmmsg` 是為 **datagram socket**（UDP）設計的，因為 UDP 每個 datagram 是獨立的，天然適合批量收發。

**TCP 不直接適用**，原因是 TCP 是 byte stream——沒有「一個 datagram」的概念，`read()` 就是讀一段連續的 bytes。但「減少 syscall 次數」的思路在 TCP 上也成立，只是實現方式不同：

- **使用更大的 read buffer**：一次 `read(fd, buf, 64*1024)` 比四次 `read(fd, buf, 16*1024)` 少三次 syscall
- **Go 的做法**：`net.Conn.Read` 底層已經做了 buffer 管理，而且 Go runtime 的 netpoll 會在 `read` 返回 `EAGAIN` 時讓 goroutine park，不會做 busy polling。對大多數 Go TCP 服務來說，syscall overhead 不是主要瓶頸。
- **gRPC 的做法**：`MaxRecvMsgSize` 和 HTTP/2 flow control window size 間接影響每次 `read` 能拿到多少資料。window 太小 → 每次 `read` 只拿到少量資料 → syscall 次數多。

### 2.6 io_uring 在 Network Path 的真實位置

📖 `io_uring` 是 Linux 5.1+（Jens Axboe, 2019）引入的 completion-based 異步 I/O 框架。它試圖從根本上解決 epoll 模型剩下的兩個問題：**syscall overhead** 和 **readiness vs completion 的兩步問題**。

#### io_uring 的核心運作方式

傳統的 epoll 模型：

```
Application → syscall: epoll_wait() → Kernel 返回 ready fds
Application → syscall: read(fd) → Kernel 返回 data
兩次 syscall，兩次 mode switch
```

io_uring 的做法完全不同——它在 user-space 和 kernel-space 之間建立了**兩個共享記憶體的 ring buffer**：

```
Application                                    Kernel
    │                                             │
    │  ┌──────────────────────┐                   │
    ├──│  Submission Queue    │──→ Kernel 從 SQ   │
    │  │  (SQ, 共享記憶體)    │    取出 SQE 並    │
    │  │                      │    執行 I/O       │
    │  │  App 寫入 SQE:       │                   │
    │  │  "幫我 read fd=5"    │                   │
    │  │  "幫我 accept fd=3"  │                   │
    │  └──────────────────────┘                   │
    │                                             │
    │  ┌──────────────────────┐                   │
    │  │  Completion Queue    │←── Kernel 完成後  │
    ←──│  (CQ, 共享記憶體)    │    把結果填入 CQE │
    │  │                      │                   │
    │  │  CQE: "fd=5 read     │                   │
    │  │   完成, 讀了 1024B"  │                   │
    │  └──────────────────────┘                   │
```

**SQE (Submission Queue Entry)**：你要 kernel 做什麼事。比如「讀 fd 5 的資料到 buffer A」、「accept fd 3 的新連線」。

**CQE (Completion Queue Entry)**：kernel 做完後的結果。比如「fd 5 讀完了，讀了 1024 bytes」、「fd 3 accept 成功，新 fd 是 12」。

因為 SQ 和 CQ 都是 user/kernel 共享記憶體，所以：

- **提交 I/O 請求**：application 直接寫入 SQ 的記憶體，不需要 syscall。只有在需要通知 kernel「SQ 有新東西了」時才呼叫 `io_uring_enter()`——而且一次 `io_uring_enter` 可以提交多個 SQE。
- **取得 I/O 結果**：application 直接從 CQ 的記憶體讀取，不需要 syscall。
- **極端模式 (SQPOLL)**：開啟 `IORING_SETUP_SQPOLL` 後，kernel 會啟動一個專用 thread 持續 poll SQ。這樣連 `io_uring_enter()` 都不需要了——application 寫入 SQ，kernel thread 自動取走處理。**完全零 syscall 的 I/O**。

#### io_uring 和 epoll 的本質差異

| 面向 | epoll (readiness) | io_uring (completion) |
|------|---|---|
| kernel 告訴你什麼 | 「fd 5 可以讀了」 | 「fd 5 的資料已經讀完了，在 buffer 裡」|
| 你需要做什麼 | 自己呼叫 `read()` | 直接用結果 |
| syscall 次數 | `epoll_wait` + `read` = 2 次/event | 0-1 次（SQPOLL 模式下可以 0） |
| 參數傳遞方式 | syscall 引數（每次 copy） | 共享記憶體（零 copy） |
| batching | 一次 `epoll_wait` 可返回多個事件，但後續 `read` 仍需逐個呼叫 | 一次可提交多個 SQE，結果批量出現在 CQ |

#### io_uring 在 network path 的現狀（截至 2025）

| 能力 | 狀態 | 說明 |
|------|------|------|
| `read/write` on socket fd | ✅ 穩定 | 基本的 socket I/O |
| `recv/send` | ✅ 穩定 | 5.6+ |
| `accept` | ✅ 穩定 | `IORING_OP_ACCEPT`，5.5+ |
| `connect` | ✅ 穩定 | 5.5+ |
| `recvmsg/sendmsg` | ✅ 穩定 | 5.3+ |
| multishot accept | ✅ 穩定 | 一次 SQE 持續 accept 多個連線，6.0+。不需要每 accept 一次就重新提交 SQE |
| multishot recv | ✅ 穩定 | 一次 SQE 持續接收多筆資料，6.0+。kernel 每收到一批資料就產生一個 CQE |
| zero-copy send | ✅ 穩定 | `IORING_OP_SEND_ZC`，6.0+。資料直接從 user buffer DMA 到 NIC，不經過 kernel buffer copy |
| io_uring + SQPOLL for network | ⚠️ 可用但需注意 | SQPOLL thread 持續佔用一個 CPU 核心（即使沒有 I/O）；安全性考量：需要 `CAP_SYS_ADMIN` 或較新 kernel 的 unprivileged SQPOLL |

#### io_uring vs epoll：什麼時候值得切換

🔧 **epoll 仍然足夠的場景**（大多數 Go 服務）：

對於一般的 Go HTTP/gRPC 服務，syscall overhead 通常只佔 CPU 總消耗的 5% 以下。你的 CPU 主要花在 JSON 序列化、業務邏輯、GC、downstream 等待上。即使 io_uring 把 syscall 成本歸零，對整體效能的改善也微乎其微。

具體來說，如果你的場景是：
- 連線數 < 10 萬
- PPS < 100 萬
- 業務邏輯佔 CPU 比例 > 50%
- 使用 Go 標準庫（runtime netpoll 深度整合 epoll）

→ **不需要考慮 io_uring**。

🔧 **io_uring 值得評估的場景**：

當 syscall overhead 佔 CPU 的 15% 以上時，io_uring 的收益才會顯著。這通常出現在：

- **超高 PPS 的 UDP 服務**：即時報價、DNS resolver、遊戲伺服器。每秒百萬級 `recvfrom`/`sendto`，syscall 成為真實瓶頸。
- **proxy / gateway 類服務**：每個 request 可能涉及 2+ 個 fd 的 read/write（upstream + downstream），syscall 次數翻倍。Envoy proxy 社區有 io_uring transport 的實驗。
- **C/C++/Rust 寫的 data plane**：這些語言沒有 Go runtime 的額外排程層，syscall overhead 佔比更高。
- **需要 zero-copy send**：大檔案或大 payload 傳輸時，`IORING_OP_SEND_ZC` 可以避免 kernel buffer copy，直接從 user buffer DMA 到 NIC。

🔧 **怎麼判斷自己需不需要**：

```bash
# 方法 1：用 perf 看 syscall 佔比
perf stat -e 'syscalls:sys_enter_read,syscalls:sys_enter_write,syscalls:sys_enter_epoll_wait' -p <PID> sleep 10

# 方法 2：用 strace 看 syscall 時間佔比
strace -c -p <PID> -e read,write,epoll_wait
# 看 "% time" 欄位。如果 read+write+epoll_wait 加總 < 10%，io_uring 不是你的優先級
```

🔗 **對 Go 的實際影響**：

Go 標準庫至今（Go 1.24）沒有原生 io_uring 支援，而且短期內不太可能加入。原因是 Go runtime 的 netpoll 和 goroutine scheduler 深度綁定 epoll——每個 socket fd 的 ready 事件會直接觸發 goroutine 的 park/unpark。要改用 io_uring，需要重新設計 runtime 的 I/O 調度模型，這是一個巨大的工程。

社區有 `iceber/iouring-go` 等封裝，但使用它意味著繞過 `net.Conn` 的抽象 → 無法使用 `net/http`、`google.golang.org/grpc` 等標準生態。除非你是在寫 Go 的 sidecar proxy 或 raw socket 處理器且已經用 `perf` 確認 syscall 是瓶頸，否則 epoll 路線仍是正確選擇。

---

## 三、橫向分析：博弈 / 電商 K8s 服務的調優圖譜

### 3.1 端到端資料路徑圖

```
Client (Browser / App / Upstream)
    │
    │  TCP/TLS
    ▼
┌─────────────────────────────────────────────────────────────┐
│  Cloud LB / MetalLB / NodePort                              │
│  (L4/L7 load balancer)                                      │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  K8s Node                                                    │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  kube-proxy (iptables / IPVS)                         │  │
│  │  or Cilium eBPF                                       │  │
│  └───────────────────────┬───────────────────────────────┘  │
│                          │                                   │
│                          ▼                                   │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Nginx Ingress Controller Pod                         │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │  Nginx worker process                           │  │  │
│  │  │  - epoll (ET) event loop                        │  │  │
│  │  │  - upstream keepalive pool                      │  │  │
│  │  │  - TLS termination                              │  │  │
│  │  │  - request buffering / proxy_pass               │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────┬───────────────────────────────┘  │
│                          │                                   │
│                          │  HTTP/gRPC (Pod-to-Pod, 通常      │
│                          │  經過 veth + bridge/IPVS/eBPF)    │
│                          ▼                                   │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Application Pod (Go HTTP/gRPC server)                │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │  Go runtime                                     │  │  │
│  │  │  - netpoll (epoll ET, fd → goroutine wakeup)    │  │  │
│  │  │  - GOMAXPROCS goroutine scheduler               │  │  │
│  │  │  - GC (STW pause, mark assist)                  │  │  │
│  │  │                                                 │  │  │
│  │  │  net/http or gRPC server                        │  │  │
│  │  │  - Accept loop                                  │  │  │
│  │  │  - Handler goroutine per request                │  │  │
│  │  │  - Middleware chain                             │  │  │
│  │  │  - Business logic + downstream calls            │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────┬───────────────────────────────┘  │
│                          │                                   │
│                          ▼                                   │
│                    Downstream: DB, Redis, MQ, upstream APIs  │
└─────────────────────────────────────────────────────────────┘
```

#### 三層架構的邊界開銷圖

上面的端到端路徑可以簡化成三個層級，每個層級之間都有 [§一‧五](#一五看不見的效能稅為什麼調優的本質是少過邊檢站) 提到的「效能稅」：

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Layer 3: Application Space (Go runtime)                                │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  goroutine handler → business logic → downstream call            │  │
│  │                                                                   │  │
│  │  💰 內部稅：GC STW pause、goroutine scheduler latency、           │  │
│  │            channel contention、memory allocation                  │  │
│  └───────────────────────────┬───────────────────────────────────────┘  │
│                              │                                          │
│          ════════════════════╪══════════════════════════════════         │
│          ║  邊界 A: User ↔ Kernel  (syscall mode switch)     ║         │
│          ║  💰 稅收：~300-500ns/次 (KPTI + TLB flush)        ║         │
│          ║  涉及：read(), write(), epoll_wait()              ║         │
│          ════════════════════╪══════════════════════════════════         │
│                              │                                          │
│  Layer 2: Kernel Space (TCP/IP stack + scheduler)                       │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  socket queue → TCP/IP 協議棧 → sk_buff → NAPI poll              │  │
│  │                                                                   │  │
│  │  💰 內部稅：conntrack lock、softirq 排隊、ksoftirqd 降級、       │  │
│  │            跨 NUMA data copy、context switch                      │  │
│  └───────────────────────────┬───────────────────────────────────────┘  │
│                              │                                          │
│          ════════════════════╪══════════════════════════════════         │
│          ║  邊界 B: Kernel ↔ Hardware  (IRQ / DMA)           ║         │
│          ║  💰 稅收：~0.5-1µs/次 (IRQ handler + cache 污染)  ║         │
│          ║  涉及：hard IRQ、NIC ring buffer DMA               ║         │
│          ════════════════════╪══════════════════════════════════         │
│                              │                                          │
│  Layer 1: Hardware (NIC + CPU cache + NUMA)                             │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  NIC RX ring → RSS hash → DMA write → IRQ signal                │  │
│  │                                                                   │  │
│  │  💰 內部稅：ring buffer overflow (丟包)、RSS hash 不均、          │  │
│  │            NUMA remote memory access (延遲 ×2-3)                  │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘

K8s 額外疊加的邊界：
  • veth pair (Pod ↔ Node)：虛擬網卡，不支援 RSS，每個封包多一次 softirq
  • kube-proxy iptables/IPVS：conntrack insert + DNAT 規則遍歷
  • Cilium eBPF：可跳過 veth + conntrack，直接在 XDP/TC 層做轉發
```

> **閱讀指南**：當你在排查效能問題時，先確認瓶頸在哪個 Layer，再看它碰到的是「邊界稅」還是「內部稅」。邊界稅靠減少穿越次數（batching、io_uring）；內部稅靠分散負載（RSS、多 Pod）或消除競爭（Cilium bypass conntrack）。

#### 瓶頸通常先長在哪

🔧 根據工程經驗，在 K8s + Nginx Ingress + Go 這條路上，瓶頸出現的頻率排序：

1. **Application 層**（最常見）：慢 DB query、慢 upstream、goroutine leak、GC pause、connection pool exhaustion
2. **Ingress 層**：Nginx worker 數不夠、upstream keepalive 用盡、proxy buffer 設定不當、TLS handshake CPU 開銷
3. **Node 層**：conntrack table 滿、softirq 集中單核、kube-proxy iptables 規則太多
4. **Network 層**（最不常見但最難查）：MTU mismatch、CNI overhead、跨 AZ 延遲

### 3.2 情境一：Tail Latency / Jitter

**症狀**：p50 正常但 p99/p999 突然惡化，延遲出現週期性或隨機尖峰。

#### 為什麼 tail latency 特別難搞

Tail latency（p99/p999）和 average latency 的根因通常不同。Average latency 反映的是「大多數 request 要走多長的路」，通常由 business logic、DB query、序列化決定。但 tail latency 反映的是「極少數 request 為什麼比別人慢很多」。

在 Linux 網路 I/O 的上下文裡，tail latency 通常不是因為「那個 request 的 handler 特別慢」，而是因為那個 request 正好撞上了某個系統級的暫停或排隊：

- **GC STW**：Go 的 GC 有短暫的 stop-the-world 階段，所有 goroutine 暫停。如果你的 request 剛好在處理中遇到 STW，延遲就會多出這段暫停時間。這通常表現為**週期性**的 p99 尖峰（GC 頻率固定）。
- **softirq 排隊**：網路中斷集中在一顆 CPU，該 CPU 的 softirq 處理不及 → 封包在 NAPI queue 裡等待 → 即使 application 已經準備好讀取，資料到 socket queue 的時間就是變慢了。
- **scheduler 排隊**：goroutine 被 netpoll 喚醒後，要等到有空閒的 P 才能執行。如果所有 P 都在忙，這個等待可能是幾毫秒。
- **偶發的跨 NUMA access**：某些 request 剛好被 scheduler 遷移到另一個 NUMA node 的 CPU，memory access 延遲倍增。

這就是為什麼 tail latency 排障不能只看 application profile——你需要同時看 **app 層、kernel 層、hardware 層**。

#### 排障切層

```
Step 1: 確認抖動位置
  ├─ Ingress 側量到的 latency 就高？ → 問題在 Ingress 之前或 Ingress 本身
  └─ Ingress 側低但 client 側高？   → 問題在 LB 或 network path

Step 2: App 內部定位
  ├─ 看 Go pprof goroutine profile → 是否有大量 goroutine 卡在某個 downstream call
  ├─ 看 GC pause (GODEBUG=gctrace=1) → STW 是否 > 1ms
  ├─ 看 handler 耗時分佈 → 是否某幾個 endpoint 特別慢
  └─ 看 scheduler latency (runtime/metrics SchedulerLatency) → goroutine 是否排不到 CPU

Step 3: Node 層
  ├─ mpstat -P ALL → 是否有單核 softirq 很高
  ├─ /proc/net/softnet_stat → time_squeeze 是否持續增長
  ├─ /proc/interrupts → IRQ 是否集中
  └─ ss -tnpm → socket queue 是否堆積
```

#### 常見根因與對策

| 根因 | 為什麼導致 tail latency | 觀測方式 | 調優手段 |
|------|------------------------|---------|---------|
| **GC STW pause** | Go GC 的 stop-the-world 階段暫停所有 goroutine，正在處理的 request 延遲增加 | `GODEBUG=gctrace=1`、`runtime/metrics` | 降低 allocation rate（sync.Pool、減少逃逸）、調整 `GOGC`/`GOMEMLIMIT` |
| **Scheduler latency** | goroutine 太多，排隊等 P 執行 | `runtime/metrics /sched/latencies:seconds` | 減少 goroutine 數（限流、bounded worker pool）、增加 `GOMAXPROCS` |
| **softirq 集中** | 所有網路中斷由單核處理，該核的 softirq 佔比 > 30% | `mpstat -P ALL`（%soft 列）、`/proc/interrupts` | RSS 多 queue + IRQ affinity |
| **NAPI budget 用盡** | `time_squeeze` 持續增長 → softirq 被迫讓出 CPU → 收包延遲 | `/proc/net/softnet_stat` 第 2 列 | 增大 `net.core.netdev_budget` |
| **Socket queue 堆積** | application 讀取速度跟不上到達速度，TCP window 縮小 | `ss -tnpm`（Recv-Q > 0 持續） | 加快 application 處理、增大 `SO_RCVBUF` / `tcp_rmem`（治標） |
| **conntrack 競爭** | K8s 使用 iptables DNAT 時，conntrack insert 在高併發下有鎖競爭 | `dmesg` 看 `nf_conntrack: table full`、`conntrack -C` | 增大 `nf_conntrack_max`、改用 IPVS 或 Cilium eBPF（bypass conntrack） |
| **NUMA remote access** | 封包處理在 NUMA node A，application 跑在 NUMA node B → memory access 延遲 ×2-3 | `numastat`、`perf c2c` | NUMA-aware Pod scheduling、RFS |
| **Nginx proxy buffer** | `proxy_buffering on` 但 buffer 太小 → 頻繁 disk 溢出 | Nginx error log、`proxy_buffer_size` | 調大 `proxy_buffers`，或對 gRPC streaming 用 `proxy_buffering off` |

#### 深入：softirq 集中為什麼會導致延遲抖動

這個根因值得多解釋，因為它是很多人第一時間想不到的。

正常情況下，封包從 NIC 到 socket queue 的路徑是：hard IRQ → softirq (NAPI poll) → 協議棧 → socket queue → wakeup。整條路在 softirq context 裡完成，通常幾十微秒。

但如果**所有封包的 softirq 都集中在同一個 CPU**（因為只有一個 RSS queue 或 IRQ affinity 沒設），那這顆 CPU 會非常忙。當 softirq 連續處理時間超過 kernel 的限制（`__do_softirq` 預設最多跑 2ms 或 10 次迭代），kernel 會**把剩下的 softirq 工作交給 `ksoftirqd` kernel thread**。

問題在於：`ksoftirqd` 是一個普通的 kernel thread，需要被 scheduler 排程。它的優先級不像 hard IRQ 或直接的 softirq 那樣高。所以一旦 softirq 處理被降級到 `ksoftirqd`，延遲可能從微秒級**跳到毫秒級**。

這在 `mpstat` 裡表現為某個 CPU 的 `%soft` 很高（> 30%），在 `/proc/net/softnet_stat` 裡表現為 `time_squeeze`（第 2 列）持續增長。

#### Busy Poll：用 CPU 換延遲

📖 `SO_BUSY_POLL`（socket 層）/ `net.core.busy_poll`（全域）。

正常的收包路徑是：NIC 收到封包 → 觸發 hard IRQ → 排程 softirq → softirq 處理 → 喚醒 application。每一步都有排程延遲。

Busy poll 的做法是：在 application 呼叫 `epoll_wait` 或 `recv` 時，**不是等 softirq 把資料送到 socket queue**，而是讓 application 自己直接去 poll NIC 的 ring buffer。跳過了 IRQ → softirq → wakeup 整條路。

🔧 **效果**：封包從 NIC 到 application 的延遲可從 ~20μs 降到 ~5μs。

🔧 **代價**：CPU 在 busy poll 期間完全被佔住，不做其他任何事。等於用 CPU 時間換延遲。**只適合延遲敏感 + CPU 充裕的場景**，例如金融報價、即時盤口。如果你的 CPU 已經 70% utilization，開 busy poll 只會讓情況更糟。

```bash
# 全域設定：每次 epoll_wait/recv 先 busy poll 50 微秒再進入睡眠
sysctl -w net.core.busy_poll=50
sysctl -w net.core.busy_read=50

# 或 per-socket 設定
setsockopt(fd, SOL_SOCKET, SO_BUSY_POLL, &timeout, sizeof(timeout));
```

### 3.3 情境二：高連線 / Burst 壓力

**症狀**：突發流量（開盤、秒殺）時大量 connection reset、`connect timeout`、`accept` 變慢。

#### 先理解：建連線為什麼需要 queue

TCP 三次交握（SYN → SYN-ACK → ACK）需要時間，而 application 的 `accept()` 呼叫不一定能即時處理每一個完成交握的連線。所以 kernel 在中間維護了**兩個 queue**，讓「交握中的連線」和「交握完等待 accept 的連線」有地方排隊。

如果這兩個 queue 任何一個滿了，新連線就會被拒絕或延遲——這就是 burst 時 connection reset / timeout 的根因。

#### TCP 連線建立的 queue 結構

```
Client SYN ──→ ┌──────────────────┐
               │  SYN Queue       │  半連線 (SYN_RECV 狀態)
               │  (SYN backlog)   │  大小受 tcp_max_syn_backlog 影響
               └────────┬─────────┘
                        │ 收到 ACK，三次交握完成
                        ▼
               ┌──────────────────┐
               │  Accept Queue    │  全連線 (ESTABLISHED 但尚未被 accept)
               │  (listen backlog)│  大小 = min(backlog 參數, somaxconn)
               └────────┬─────────┘
                        │ application 呼叫 accept()
                        ▼
               ┌──────────────────┐
               │  Application fd  │  進入 epoll 監控
               └──────────────────┘
```

📖 **Accept queue 滿時的行為**：
- `net.ipv4.tcp_abort_on_overflow = 0`（預設）：kernel 直接**丟棄 client 的最後一個 ACK**。client 以為連線已建立（三次交握完成了），但 server 沒有記錄。client 開始發資料，server 看不懂 → 過了一段時間 client timeout 重連。**表現為延遲增加但沒有明確錯誤**，很難排查。
- `net.ipv4.tcp_abort_on_overflow = 1`：kernel 回 RST → client 立刻知道連線失敗，可以快速重試或報錯。**表現為明確的 connection refused**。

🔧 在博弈/電商場景，建議設 `tcp_abort_on_overflow = 1`。讓 client 快速失敗比讓它傻等要好——至少可以被 retry logic 或 circuit breaker 接住。

#### 怎麼看 accept queue 的使用量

```bash
# ss -tnlp 看 listen socket
ss -tnlp

# 輸出範例：
# State  Recv-Q  Send-Q  Local Address:Port  ...
# LISTEN    0      4096   *:8080              ...
#
# 對於 LISTEN 狀態的 socket：
#   Recv-Q = 目前在 accept queue 裡等待的連線數（越大越危險）
#   Send-Q = accept queue 的上限（= min(backlog, somaxconn)）
#
# 如果 Recv-Q 接近 Send-Q → accept queue 快滿了

# 看 accept queue 溢出的歷史次數
nstat -az TcpExtListenOverflows
```

#### 調優手段

| 問題 | 觀測 | 調整 |
|------|------|------|
| Accept queue 滿 | `ss -tnlp`（Recv-Q 接近 Send-Q）、`nstat TcpExtListenOverflows` | 增大 `net.core.somaxconn`（建議 ≥ 4096）、增大 application `listen(fd, backlog)` |
| SYN queue 滿 | `nstat TcpExtTCPReqQFullDrop` | 增大 `net.ipv4.tcp_max_syn_backlog`、開啟 `tcp_syncookies` |
| TIME_WAIT 堆積 | `ss -s`（timewait 數量）| 開啟 `tcp_tw_reuse`（不要用 `tcp_tw_recycle`，已在 kernel 4.12 移除） |
| FD 耗盡 | `ulimit -n`、Pod 內 `/proc/sys/fs/nr_open` | 增大 `ulimit -n`（≥ 65535）、K8s Pod securityContext 可設定 |
| conntrack 滿 | `dmesg` 報 `table full, dropping packet` | `net.netfilter.nf_conntrack_max`、考慮 Cilium eBPF 直接 bypass |
| Ingress upstream 連線不夠 | Nginx upstream 回應變慢、error log 出現 `no live upstreams` | 調大 `upstream keepalive`、增加 `keepalive_requests` |

#### SO_REUSEPORT 的價值

📖 `SO_REUSEPORT`（Linux 3.9+）允許多個 socket bind 同一個 `ip:port`，kernel 用一致性 hash（基於 4-tuple）把新連線分配到不同 socket → 不同 thread/process。

🔧 **解決的問題**：
1. **消除 accept 瓶頸**：沒有 `SO_REUSEPORT` 時，所有連線進同一個 accept queue，多個 worker epoll_wait 同一 listen fd 可能 thundering herd。有了 `SO_REUSEPORT`，每個 worker 有自己的 accept queue，kernel 直接分流。
2. **改善 CPU locality**：封包直接進到 worker 對應的 queue，減少跨核轉發。

🔧 **Nginx 已經用了**：Nginx 1.9.1+ 支援 `listen 80 reuseport;`。在高 CPS（connections per second）場景效果顯著。

🔧 **Go 的情況**：Go 標準庫的 `net.Listen` 沒有直接暴露 `SO_REUSEPORT`。社區方案如 `libp2p/go-reuseport` 可以用，但需要評估是否值得繞過標準庫。在多 Pod 的 K8s 環境，通常靠 Service/Ingress 做連線分散，`SO_REUSEPORT` 的價值主要在 Nginx Ingress 本身或 node-level 的 proxy。

### 3.4 情境三：Core Hotspot / CPU 不均

**症狀**：整體 CPU utilization 看起來不高（例如 40%），但某幾顆核心 100%，其餘閒置。延遲和吞吐都不理想。

這是高併發服務中最常被誤判的情況。你看 Grafana 的 node CPU 圖表顯示「CPU 40%，還有很多餘裕」，但 p99 已經開始惡化。原因是 **CPU 不是一坨，而是多顆獨立的核心**——平均 40% 可能意味著某 2 顆核心 100% 而其餘 12 顆只有 20%。被打滿的那 2 顆核心成為整個系統的瓶頸。

#### 為什麼會發生

1. **IRQ 集中**：如果 NIC 只有一個 RSS queue，或 IRQ affinity 沒設定，所有封包的硬體中斷都打到 CPU 0。CPU 0 要負責所有 hard IRQ + softirq（NAPI poll、協議棧），很容易被打滿。其他核心再閒也幫不上這段路。

2. **softirq 集中**：即使有多個 RSS queue，如果 IRQ affinity 沒正確設定（例如多個 queue 的 IRQ 都綁到同一個 CPU），softirq 仍然集中。RPS 沒開的話，軟體層也無法補救。

3. **conntrack 鎖**：在 K8s 使用 iptables 做 DNAT（kube-proxy iptables 模式）時，每個新連線都要在 conntrack table 裡插入一條記錄。conntrack table 用 hash bucket 組織，插入時要鎖住對應的 bucket。在高 CPS 場景，如果多個 CPU 同時插入且 hash 到同一個 bucket → 鎖競爭 → 某些 CPU 花大量時間等鎖。

4. **Go scheduler 不均**：`GOMAXPROCS` 設定比實際可用 CPU 多（常見於容器環境：host 有 32 核但 Pod 只分配 4 核），Go scheduler 建立太多 P → 跟其他 Pod 和系統搶 CPU → context switch 增加、cache miss 增加。

#### 診斷

```bash
# 看每個 CPU 的 IRQ 分佈
cat /proc/interrupts | grep eth0

# 看每個 CPU 的 softirq 時間
mpstat -P ALL 1

# 看每個 CPU 的 softnet_stat（包處理統計）
cat /proc/net/softnet_stat
# 每行對應一個 CPU: processed, time_squeeze, ...

# 看 NIC 的 queue 數量
ethtool -l eth0

# 看 NIC 每個 queue 的流量分佈
ethtool -S eth0 | grep rx_queue
```

#### 調優

| 手段 | 怎麼做 | 效果 |
|------|--------|------|
| **增加 RSS queue** | `ethtool -L eth0 combined 8`（看 NIC 支援上限） | 硬體層面分散，開銷最小 |
| **設定 IRQ affinity** | `echo 2 > /proc/irq/<N>/smp_affinity`（或用 `irqbalance`） | 把不同 queue 的 IRQ 分到不同核心 |
| **開啟 RPS** | `echo ff > /sys/class/net/eth0/queues/rx-0/rps_cpus` | NIC queue 不夠時的軟體補充 |
| **開啟 RFS** | `echo 32768 > /proc/sys/net/core/rps_sock_flow_entries` | 把封包導向處理該 flow 的 CPU |
| **K8s CPU pinning** | Pod `resources.limits.cpu` + `static` CPU manager policy | 確保 Pod 不跟系統 softirq 搶同一組核心 |
| **Cilium eBPF** | 取代 kube-proxy iptables | 消除 conntrack 鎖競爭 |

🔗 **K8s 特別考量：GOMAXPROCS 的陷阱**

這個問題非常常見，值得特別說明。

Go 的 `runtime.NumCPU()` 讀的是 OS 層面的 CPU 數量。在容器裡，它讀到的是 **host 的 CPU 數量**（例如 32），而不是 cgroup 限制的 CPU quota（例如 4 核）。

所以如果你的 Pod 設定 `resources.limits.cpu: "4"`，但 `GOMAXPROCS` 是 32，Go scheduler 會建立 32 個 P。這 32 個 P 全部在搶 4 核的 CPU 時間片 → 大量 context switch → cache thrashing → 效能反而比正確設 `GOMAXPROCS=4` 更差。

解法很簡單：

```go
import _ "go.uber.org/automaxprocs" // 在 main.go import

// automaxprocs 會自動讀 cgroup v1/v2 的 CPU quota，
// 設定 GOMAXPROCS = quota / period，例如 400000/100000 = 4
```

另一個相關的 K8s CPU 設定是 **CPU manager static policy**。預設情況下，kubelet 使用 `none` policy，所有 Pod 共享 node 的所有 CPU。開啟 `static` policy 後，Guaranteed QoS 的 Pod（request = limit 且是整數核心）會被分配到**獨佔的 CPU 核心**，其他 Pod 和系統服務不會跑在這些核心上。這可以避免 application 和 softirq 搶同一組核心。

### 3.5 情境四：選型與中長期改造

**問題**：已經把 application 和 kernel tuning 做到一定程度，下一步該怎麼選？

#### 決策樹

```
你的瓶頸到底在哪？
│
├─ syscall overhead 佔 CPU > 15%
│   ├─ UDP + 高 PPS → 先試 recvmmsg/sendmmsg batching
│   ├─ TCP proxy/gateway → 評估 io_uring（如果是 C/Rust 寫的組件）
│   └─ Go 服務 → syscall 開銷通常不是主因，先看 GC 和 goroutine
│
├─ accept 瓶頸（CPS > 5 萬/秒）
│   ├─ Nginx → 加 reuseport
│   └─ Go → 多 Pod 分散，或評估 SO_REUSEPORT 方案
│
├─ softirq 集中
│   ├─ 先加 RSS queue
│   ├─ 再調 IRQ affinity
│   └─ 不夠再開 RPS/RFS
│
├─ TCP buffer / queue 問題
│   ├─ 先調 tcp_rmem / tcp_wmem / somaxconn
│   └─ 再看 GRO / GSO 是否開啟
│
└─ 以上都做了還不夠
    ├─ 考慮 Cilium eBPF 替代 kube-proxy
    ├─ 考慮 node-level proxy 直接用 io_uring
    └─ 極端場景：XDP / AF_XDP（進階延伸，不進主線）
```

---

## 四、橫縱交匯洞察

### 洞察 1：為什麼很多人以為是 TCP 問題，實際是 queue / wakeup / CPU locality 問題

🔗 很多 incident 的初始判斷是「TCP 慢」「網路慢」，但實際上：

- **TCP retransmission 高** → 可能不是網路丟包，而是 NIC ring buffer 滿了（`ethtool -S` 看 `rx_missed_errors`）
- **TCP connection timeout** → 可能不是對端慢，而是 accept queue 滿了（`nstat TcpExtListenOverflows`）
- **TCP throughput 低** → 可能不是頻寬不夠，而是 receive window 被縮小（因為 application 沒及時讀走 socket queue 的資料）

教訓：**不要直接跳到 TCP 參數調整，先確認 queue 在哪裡堆積、CPU 在哪裡不均**。

### 洞察 2：為什麼用了 epoll 還是會 latency 抖

🔗 epoll 解決了「如何高效等待事件」，但它不解決：

1. **wakeup latency**：epoll_wait 返回後，goroutine/thread 需要被 scheduler 排到 CPU 上才能開始工作。如果 CPU 被 softirq 或其他 task 佔用，這段等待就是延遲。
2. **kernel copy latency**：fd ready 後的 `read()` 仍然要做 kernel → user-space 的 data copy。如果資料在遠端 NUMA node，copy 延遲會明顯增加。
3. **GC pause**：Go 的 GC STW 階段會暫停所有 goroutine，包括正在做 I/O 的。
4. **head-of-line blocking**：如果 handler 內有一個慢 downstream call，它佔住 goroutine 的同時，其他 request 的處理不受影響（Go 模型的好處），但該 request 本身的 latency 會很高。

教訓：**epoll 是必要條件，不是充分條件。latency 抖動要從 wakeup path、CPU locality、GC、application logic 逐層排查**。

### 洞察 3：為什麼某些場景先調 ingress / node 比先改 app 值得

🔗 如果你有 20 個 Go 微服務，都經過同一個 Nginx Ingress：

- 調一次 Ingress 的 `keepalive` / `reuseport` / `proxy_buffer` → 所有服務受益
- 調一次 node 的 `somaxconn` / `tcp_rmem` / RSS → 所有 Pod 受益
- 改一個 app → 只有那個服務受益

🔧 **高槓桿調優順序**：
1. Node kernel parameter（影響所有 Pod）
2. Ingress configuration（影響所有經過它的流量）
3. Application code / runtime tuning（只影響自己）

例外：如果 profiling 明確指向某個 app 的 GC pause 或 DB query，那當然先修 app。

### 洞察 4：什麼情況值得考慮 io_uring，什麼情況只是提早優化

🔗 io_uring 的收益在 **syscall overhead 佔比高** 的場景才顯著：

- 一般 Go HTTP server：syscall overhead 可能只佔 CPU 的 5% 以下，即使消除也不會有感的改善
- C/Rust 寫的 proxy 每秒處理 50 萬次 recv/send：syscall overhead 可能佔 CPU 的 20-30%，io_uring 的 batching + zero-syscall polling 才有實質收益

🔧 判斷方法：用 `perf stat` 或 `strace -c` 看 syscall 佔比。如果 `read`/`write`/`epoll_wait` 的 syscall 時間加總 < 10% of CPU time，io_uring 不是你現在需要的。

---

## 五、交付表格與清單

### 5.1 症狀對照表

#### Tail Latency / Jitter 排障對照表

| 症狀 | 先看哪層 | 跑哪些命令 | 懷疑什麼 | 底層邏輯（為什麼這個指標 = 這個瓶頸） | 可調什麼 | 調整後的副作用 |
|------|---------|-----------|---------|-------------------------------------|---------|---------------|
| p99 週期性尖峰（10-50ms） | App | `GODEBUG=gctrace=1`、`runtime/metrics` | GC STW pause | GC 的 STW 階段暫停**所有** goroutine。如果尖峰週期與 GC 頻率吻合（`gctrace` 可看到），幾乎可以確認。參見 [§一‧五 稅收二](#稅收二context-switch--時間碎片的車道切換) | `GOGC`、`GOMEMLIMIT`、降低 alloc rate | `GOGC` 調大 → GC 頻率降低但每次 pause 可能更長；需配合 `GOMEMLIMIT` 避免 OOM |
| p99 隨機抖動（1-5ms） | Node | `mpstat -P ALL`、`/proc/interrupts` | softirq 集中單核 | 所有封包的 softirq 由同一 CPU 處理 → 該 CPU 的 `%soft > 30%` → softirq 處理不及被降級到 `ksoftirqd`（普通 thread）→ 延遲從 µs 跳到 ms。參見 [§一‧五 稅收四](#稅收四interrupt-irq--強制停車檢查) | RSS + IRQ affinity | RSS queue 增多 → 每個 queue 的 hash bucket 變少，極端情況某些 flow 可能集中 |
| p999 偶發超高（>100ms） | App + Node | goroutine profile、`ss -tnpm`（Recv-Q） | goroutine 堆積 + socket queue 滿 | goroutine 數量遠超 `GOMAXPROCS` → run queue 排隊等 P → scheduler latency 累積。同時 application 讀取變慢 → socket queue 堆積 → TCP window 縮小 → 對端被迫降速 → 全鏈路變慢 | 限流、timeout、增大 buffer | 增大 buffer 只是治標（延後 queue 滿的時間點），根因是 application 處理速度 |
| 延遲隨 PPS 線性上升 | Node | `/proc/net/softnet_stat`（time_squeeze） | NAPI budget 不夠 | `time_squeeze` 代表「softirq 想繼續 poll 但 budget/time 用完被迫讓出 CPU」。像一個海關官員，每批最多蓋 300 個章就必須休息 → PPS 越高、排隊越長、延遲線性增加 | `net.core.netdev_budget` | budget 調太大 → softirq 佔用 CPU 時間過長 → application 的 context switch latency 反而上升 |
| Ingress 側 latency 低但 client 側高 | Network | `tcpdump`、MTU check、LB health | 網路路徑問題 | 如果 application 和 Ingress 之間延遲正常，問題一定在 Ingress 之前：LB 的健康檢查失敗導致流量不均、MTU mismatch 導致分片重組、跨 AZ 的物理延遲 | MTU、LB 設定、跨 AZ | — |
| 壓測正常但上線後抖 | App + Node | 比對壓測 vs 線上的連線數、payload、downstream | 壓測不夠真實 | 壓測通常用均勻流量，但線上流量有 burst（例如開盤瞬間）；壓測的 downstream 通常比線上穩定；壓測時 conntrack 表是冷的但線上是熱的 | 加 chaos / shadow traffic | — |

#### 高連線 / Burst 排障對照表

| 症狀 | 先看哪層 | 跑哪些命令 | 懷疑什麼 | 底層邏輯（為什麼這個指標 = 這個瓶頸） | 可調什麼 | 調整後的副作用 |
|------|---------|-----------|---------|-------------------------------------|---------|---------------|
| 大量 connection reset | Node | `nstat TcpExtListenOverflows`、`dmesg` | accept queue 滿 or conntrack 滿 | `ListenOverflows` 代表三次交握完成的連線到了 accept queue，但 queue 已滿 → kernel 丟棄 ACK（預設）或回 RST。如果 `dmesg` 出現 `conntrack: table full` → 是 conntrack 滿而非 queue 滿 | `somaxconn`、`nf_conntrack_max` | `somaxconn` 調大只延後問題，根因是 application `accept()` 太慢；`nf_conntrack_max` 調大增加 kernel 記憶體 (~300B/條) |
| connect timeout 增加 | Node + Ingress | `ss -tnlp`（Recv-Q vs Send-Q）、Nginx error log | SYN/accept queue 飽和 | `ss -tnlp` 看到 Recv-Q ≈ Send-Q 代表 accept queue 快滿。此時新連線的 ACK 被丟棄 → client 以為連線建好了開始發資料 → server 不認識 → client 等到 timeout 才重試。這種 timeout 比 RST 更難排查 | `tcp_max_syn_backlog`、`somaxconn`、Nginx `worker_connections` | 建議同時設 `tcp_abort_on_overflow=1` 讓 client 快速失敗而非傻等 |
| TIME_WAIT 堆積 | Node | `ss -s` | 短連線太多 | TIME_WAIT 是 TCP 正常狀態（防止舊封包干擾新連線），預設等 60 秒。短連線密集場景每秒新建/關閉上千連線 → TIME_WAIT 堆積 → port 耗盡 → 新連線建不了 | `tcp_tw_reuse`、改用 keepalive | `tcp_tw_reuse` 只對**主動發起連線方**有效（outgoing）；**不要用** `tcp_tw_recycle`（已在 kernel 4.12 移除，NAT 環境下會斷連） |
| fd 耗盡 | Pod | `ls /proc/<pid>/fd \| wc -l`、`ulimit -n` | fd limit 太低 | Linux 預設 ulimit 通常 1024。每個 TCP 連線佔一個 fd，加上 log file、epoll instance 等 → 高連線場景很快超限 → `accept()` 返回 `EMFILE` → 新連線全部失敗 | 提高 `ulimit -n`、Pod securityContext | 無明顯副作用，建議設 ≥ 65535 |
| Nginx 502/504 增加 | Ingress | Nginx error log、upstream 連線數 | upstream keepalive 用盡 | Nginx 默認 `upstream keepalive` 很小（如 32）。burst 時所有 keepalive 連線被佔用 → 新 request 需要建立 TCP 新連線 → 三次交握 + TLS handshake → 延遲飆升或 upstream timeout → 502/504 | 增大 `upstream keepalive`、`keepalive_requests` | keepalive 連線佔記憶體，設太大在 upstream Pod 縮容時可能 hit dead backend |

### 5.2 命令手冊

> ⚠️ **安全標籤說明**：每個命令區塊標註了操作風險等級，幫助你判斷是否可以在生產環境直接執行。
>
> | 標籤 | 含義 |
> |------|------|
> | 🟢 唯讀/觀測 | 不改變系統狀態，可隨時安全執行 |
> | 🟡 中風險/即時生效 | 修改系統參數且立即生效，重啟後失效（除非寫入 sysctl.conf）。建議先在 staging 測試 |
> | 🔴 高風險/可能影響服務 | 可能導致短暫封包丟失、連線中斷或效能波動。**必須在維護窗口執行，且預先備份原始值** |

#### 網路連線與 Socket 狀態 🟢 唯讀/觀測

```bash
# 看 TCP 連線狀態摘要
ss -s

# 看所有 TCP 連線，含 timer、memory 資訊
ss -tnpm

# 看 listen socket 的 accept queue 使用量
# Recv-Q = 目前在 accept queue 等待的連線數
# Send-Q = accept queue 上限 (backlog)
ss -tnlp

# 看指定 port 的連線數
ss -tn state established sport = :8080 | wc -l

# 看 TCP 統計（overflow、retransmit 等）
nstat -az TcpExt

# 特別有用的幾個指標
nstat -az TcpExtListenOverflows     # accept queue 溢出次數
nstat -az TcpExtListenDrops         # listen socket 丟棄次數
nstat -az TcpExtTCPTimeouts         # TCP timeout 次數
nstat -az TcpExtTCPRetransFail      # 重傳失敗次數
```

#### CPU 與中斷分佈 🟢 唯讀/觀測

```bash
# 每個 CPU 的使用率分佈（含 softirq）
mpstat -P ALL 1

# 看中斷分佈
cat /proc/interrupts | head -5    # 看 header
cat /proc/interrupts | grep eth   # 看網卡相關中斷

# softnet_stat：每行一個 CPU
# 欄位：processed | time_squeeze | ...
cat /proc/net/softnet_stat
```

#### NIC 與硬體

```bash
# --- 🟢 唯讀/觀測 ---

# NIC 統計（丟包、錯誤）
ethtool -S eth0 | grep -E 'rx_missed|rx_errors|rx_dropped|tx_errors'

# NIC queue 數量
ethtool -l eth0

# NIC ring buffer 大小
ethtool -g eth0

# 查看 offload 設定（GRO, GSO, TSO）
ethtool -k eth0

# --- 🔴 高風險/即時生效 — 修改 NIC 硬體設定，可能導致短暫封包丟失 ---
# ⚠️ 調整 queue 數量或 ring buffer 時，NIC 會短暫 reset → 該介面上所有 TCP 連線可能瞬斷
# ⚠️ 建議在維護窗口執行，並先記錄原始值以便回滾

# 調整 NIC queue 數量（原始值用 ethtool -l 查看）
ethtool -L eth0 combined 8

# 調整 ring buffer（原始值用 ethtool -g 查看）
ethtool -G eth0 rx 4096

# 開啟 GRO（通常預設已開，風險較低）
ethtool -K eth0 gro on
```

#### Kernel 參數（sysctl）

```bash
# --- 🟢 唯讀/觀測 ---
sysctl net.core.somaxconn
sysctl net.ipv4.tcp_rmem
sysctl net.ipv4.tcp_wmem
sysctl net.core.netdev_budget
sysctl net.netfilter.nf_conntrack_max

# --- 🟡 中風險/即時生效 — 重啟後失效（除非寫入 /etc/sysctl.conf）---
# ⚠️ sysctl -w 修改立即生效，影響所有 TCP 連線。建議先記錄舊值：
#    sysctl net.core.somaxconn  # 記下舊值再改

# 連線佇列相關（影響新建連線的排隊行為）
sysctl -w net.core.somaxconn=4096              # [中風險] 增大 accept queue 上限
sysctl -w net.ipv4.tcp_max_syn_backlog=4096    # [中風險] 增大 SYN queue 上限

# softirq 收包相關（影響封包處理吞吐）
sysctl -w net.core.netdev_budget=600           # [中風險] 增大 NAPI 每輪處理封包數
sysctl -w net.core.netdev_budget_usecs=4000    # [中風險] 增大 NAPI 每輪處理時間上限

# TCP 連線回收（影響短連線密集場景）
sysctl -w net.ipv4.tcp_tw_reuse=1              # [中風險] 允許重用 TIME_WAIT socket

# --- 🔴 高風險/即時生效 — TCP buffer 調整直接影響所有現有連線的記憶體使用 ---
# ⚠️ max 設太大可能在連線數多時導致 OOM（每個 socket 最多佔 max 那麼多記憶體）
# ⚠️ 公式：最大記憶體消耗 ≈ max_connections × tcp_rmem_max。先算好再改！
sysctl -w net.ipv4.tcp_rmem="4096 131072 16777216"   # [高風險] min/default/max (bytes)
sysctl -w net.ipv4.tcp_wmem="4096 65536 16777216"     # [高風險] min/default/max (bytes)
sysctl -w net.core.rmem_max=16777216                   # [高風險] socket 接收緩衝區全域上限
sysctl -w net.core.wmem_max=16777216                   # [高風險] socket 發送緩衝區全域上限
```

#### Conntrack

```bash
# --- 🟢 唯讀/觀測 ---

# 當前 conntrack 使用量
conntrack -C

# conntrack 上限
sysctl net.netfilter.nf_conntrack_max

# 查看 conntrack table
conntrack -L | head -20

# dmesg 看是否有 table full
dmesg | grep conntrack

# --- 🟡 中風險/即時生效 ---
# ⚠️ 增大 conntrack_max 會增加 kernel 記憶體消耗（每條約 ~300 bytes）
# ⚠️ 100 萬條 ≈ 300MB。確保 node 有足夠記憶體
# sysctl -w net.netfilter.nf_conntrack_max=524288    # [中風險]
```

#### 流量觀測 🟢 唯讀/觀測

```bash
# 網路流量統計（PPS、BPS）
sar -n DEV 1

# socket 統計
sar -n SOCK 1

# TCP 錯誤
sar -n ETCP 1
```

#### IRQ Affinity / RPS / RFS 設定

```bash
# --- 🟢 唯讀/觀測 ---
cat /proc/irq/<N>/smp_affinity          # 看某個 IRQ 綁定到哪些 CPU
cat /sys/class/net/eth0/queues/rx-0/rps_cpus  # 看 RPS 設定

# --- 🟡 中風險/即時生效 — 封包分發路徑改變，短暫可能亂序 ---
# ⚠️ 修改 IRQ affinity 後，部分 TCP flow 可能被分到新的 CPU → 短暫 cache miss
echo 2 > /proc/irq/<N>/smp_affinity     # [中風險] 綁定 IRQ 到特定 CPU
echo ff > /sys/class/net/eth0/queues/rx-0/rps_cpus  # [中風險] 開啟 RPS
echo 32768 > /proc/sys/net/core/rps_sock_flow_entries  # [中風險] 設定 RFS flow table
```

### 5.3 選型決策表

#### epoll / SO_REUSEPORT / batching / io_uring / busy poll 決策表

| 技術 | 解決什麼問題 | 適用前提 | 實施成本 | 典型收益 | 不適用場景 |
|------|-------------|---------|---------|---------|-----------|
| **epoll (ET)** | 大量 fd 事件監聽 | Linux 2.6+ | 已內建於框架 | 基礎能力，必備 | — |
| **SO_REUSEPORT** | accept 瓶頸、thundering herd | Linux 3.9+、多 worker | Nginx: 加 `reuseport`；Go: 需 library | CPS 提升 2-3x | 單 worker 架構、已在 K8s 多 Pod 分流 |
| **recvmmsg / sendmmsg** | 高 PPS UDP 的 syscall overhead | UDP datagram 場景 | 需改 application code | syscall 減少 30-50% | TCP（stream-based）、Go 標準庫無直接支援 |
| **io_uring** | syscall overhead、kernel-user 切換開銷 | Linux 5.1+、C/Rust 組件 | 需重寫 I/O 層 | syscall overhead 消除 | Go 服務（runtime 深度綁 epoll）、kernel < 5.10 |
| **busy poll** | 收包延遲（IRQ → softirq → wakeup 路徑） | CPU 充裕、延遲極度敏感 | sysctl 一行 | 延遲從 ~20μs 降到 ~5μs | CPU 緊張的服務、批量吞吐優先 |

### 5.4 K8s 映射表

| 層級 | 可觀測點 | 調優旋鈕 |
|------|---------|---------|
| **Host / Node** | `/proc/interrupts`、`/proc/net/softnet_stat`、`mpstat`、`ethtool -S`、`conntrack -C`、`dmesg` | RSS queue、IRQ affinity、`sysctl` kernel param、NIC ring buffer、GRO/GSO |
| **kube-proxy / CNI** | `conntrack -C`、`iptables -L -n -v | wc -l`（iptables 規則數）、Cilium metrics | 切換 IPVS 模式、Cilium eBPF 替代 iptables、`nf_conntrack_max` |
| **Ingress (Nginx)** | Nginx status page（active connections, waiting）、error log、upstream response time | `worker_processes`、`worker_connections`、`upstream keepalive`、`reuseport`、`proxy_buffers`、`keepalive_timeout` |
| **Pod network** | `ss -tnpm`（from inside Pod）、Pod CPU/memory metrics、`/proc/<pid>/fd` count | `ulimit -n`、Pod `securityContext`、Pod `resources.limits` |
| **Application (Go)** | pprof（goroutine, heap, CPU）、`GODEBUG=gctrace=1`、`runtime/metrics`、application-level metrics（handler latency histogram） | `GOMAXPROCS`（用 `automaxprocs`）、`GOGC`/`GOMEMLIMIT`、`http.Transport` pool、timeout、middleware |
| **Downstream** | DB slow query log、Redis `INFO stats`、gRPC channel metrics | connection pool size、query timeout、circuit breaker、read replica |

### 5.5 Go 映射表

#### Go Runtime 與 Linux Readiness Model 的關係

```
Linux 層                                Go 層
──────────────────                     ──────────────────
epoll fd 事件到達                       netpoll 被喚醒
  ↓                                       ↓
epoll_wait 返回 ready fds              goready(): 把對應 goroutine 放回 run queue
  ↓                                       ↓
kernel → user-space                    goroutine 被 P 調度執行
  ↓                                       ↓
read() / write()                       net.Conn.Read() / Write() 返回
```

#### Go 關鍵組件與 Linux 映射

| Go 概念 | Linux 底層 | 調優意義 |
|---------|-----------|---------|
| `runtime.netpoll` | `epoll_create` + `epoll_ctl` + `epoll_wait`（ET 模式） | Go 的 I/O 等待不佔 OS thread，但 goroutine 數量和 run queue 深度仍有意義 |
| `GOMAXPROCS` | 控制 Go scheduler 的 P 數量 → 決定同時有多少 goroutine 在 CPU 上跑 | 在容器中必須匹配 cgroup quota（用 `automaxprocs`） |
| `net.Conn.Read()` | fd 設 `O_NONBLOCK`，read 返回 `EAGAIN` 時 goroutine park → 等 netpoll 喚醒 | 大量慢連線 → 大量 parked goroutine → 記憶體壓力 |
| `http.Transport` | 維護 per-host 的 TCP keepalive connection pool | `MaxIdleConnsPerHost`、`IdleConnTimeout` 直接影響 downstream 連線數 |
| `GC STW` | 暫停所有 goroutine（包括 netpoll 的 wakeup 處理）| STW 期間到達的 epoll event 不會被處理，queue 堆積 → tail latency |
| `goroutine leak` | fd 沒關閉 + goroutine 沒退出 → fd 數和記憶體持續增長 | 用 `pprof /debug/pprof/goroutine?debug=2` 診斷 |

#### Go HTTP/gRPC Server 常見調優參數

```go
// HTTP server
server := &http.Server{
    ReadTimeout:       5 * time.Second,   // 讀完 request 的時限
    WriteTimeout:      10 * time.Second,  // 寫完 response 的時限
    IdleTimeout:       120 * time.Second, // keepalive 閒置時限
    MaxHeaderBytes:    1 << 20,           // 1MB
    ReadHeaderTimeout: 2 * time.Second,   // 讀完 header 的時限（防慢速攻擊）
}

// HTTP client (downstream call)
transport := &http.Transport{
    MaxIdleConns:        100,
    MaxIdleConnsPerHost: 20,             // 預設只有 2！幾乎一定要調
    IdleConnTimeout:     90 * time.Second,
    TLSHandshakeTimeout: 5 * time.Second,
    DisableKeepAlives:   false,          // 保持 keepalive
}

// gRPC server
grpcServer := grpc.NewServer(
    grpc.MaxRecvMsgSize(4 << 20),        // 4MB
    grpc.MaxSendMsgSize(4 << 20),
    grpc.KeepaliveParams(keepalive.ServerParameters{
        MaxConnectionIdle: 5 * time.Minute,
        Time:              2 * time.Hour,
        Timeout:           20 * time.Second,
    }),
    grpc.KeepaliveEnforcementPolicy(keepalive.EnforcementPolicy{
        MinTime:             5 * time.Second,
        PermitWithoutStream: true,
    }),
)
```

### 5.6 調優 Checklist

#### Go on Linux on K8s 調優 Checklist

**Application 層**

- [ ] `GOMAXPROCS` 使用 `automaxprocs` 自動匹配 cgroup quota
- [ ] `GOGC` / `GOMEMLIMIT` 根據 heap profile 調整（高 throughput 服務考慮 `GOGC=200` + `GOMEMLIMIT`）
- [ ] `http.Transport.MaxIdleConnsPerHost` ≥ 10（預設 2 太低）
- [ ] 所有 downstream call 設定合理 timeout（connect + read + write）
- [ ] 沒有 goroutine leak（定期 pprof goroutine profile）
- [ ] Handler 內沒有 unbounded blocking（用 `context.WithTimeout`）
- [ ] `sync.Pool` 用於高頻分配的臨時物件（JSON encoder、buffer）
- [ ] gRPC 設定 keepalive 和 max message size
- [ ] Server 設定 `ReadHeaderTimeout`（防 Slowloris 攻擊）

**Kubernetes 層**

- [ ] Pod `resources.requests` 和 `limits` 設定合理（CPU request = limit 避免 throttling）
- [ ] Pod `ulimit -n` ≥ 65535
- [ ] 使用 `topologySpreadConstraints` 分散 Pod 到不同 node
- [ ] Ingress Nginx `worker_connections` ≥ 10240
- [ ] Ingress Nginx `upstream keepalive` ≥ 32
- [ ] Ingress Nginx 對 gRPC 使用 `grpc_pass` 而非 `proxy_pass`
- [ ] 如果用 iptables 模式的 kube-proxy，Service 數量 > 1000 時考慮 IPVS 或 Cilium

**Node / Kernel 層**

- [ ] `net.core.somaxconn` ≥ 4096
- [ ] `net.ipv4.tcp_max_syn_backlog` ≥ 4096
- [ ] `net.ipv4.tcp_rmem` / `tcp_wmem` 的 max 值 ≥ 16MB（高 BDP 場景）
- [ ] `net.core.netdev_budget` ≥ 300（預設），高 PPS 場景考慮 600
- [ ] NIC RSS queue 數量 ≥ 可用 CPU 核心數（或至少 4+）
- [ ] IRQ affinity 分散到不同核心（或使用 `irqbalance`）
- [ ] `net.netfilter.nf_conntrack_max` ≥ 預期最大連線數 × 2
- [ ] `net.ipv4.tcp_tw_reuse = 1`
- [ ] NIC GRO 開啟（`ethtool -K eth0 gro on`）
- [ ] NIC ring buffer 適當增大（`ethtool -G eth0 rx 4096`）

---

## 六、進階延伸

以下技術不進主體調優流程，但在特定場景下可能需要評估：

| 技術 | 適用場景 | 為什麼不進主線 |
|------|---------|---------------|
| **XDP (eXpress Data Path)** | 需要在 NIC driver 層直接處理封包（DDoS 防禦、L4 load balancer） | 開發門檻高，需 eBPF 程式設計，大多數後端服務不需要 |
| **AF_XDP** | 需要 kernel bypass 但不想用 DPDK 的場景 | 仍需要專用的 socket 處理程式，不適用於通用 Go 服務 |
| **DPDK** | 電信級、金融級需要完全繞過 kernel 的封包處理 | 需要專用 CPU、NIC 獨佔，與 K8s 生態整合困難 |
| **TCP Fast Open (TFO)** | 短連線多、首次建連延遲敏感 | 需要 client 支援、CDN/LB 支援，且 keepalive 已經解決大部分場景 |
| **eBPF 觀測** | 深度排查 kernel 層問題（runqlat、biolatency、tcplife） | 需要 kernel 4.15+ 且工具安裝門檻較高，放在「需要時再用」 |

---

## 來源

### 官方文件 📖

- `socket(7)`, `tcp(7)`, `epoll(7)`, `io_uring(7)`, `recvmmsg(2)` — man7.org
- Scaling in the Linux Networking Stack — docs.kernel.org
- NAPI — docs.kernel.org
- Go runtime netpoll — go.dev/src/runtime/netpoll.go
- Go runtime netpoll_epoll — go.dev/src/runtime/netpoll_epoll.go

### 工程實踐 🔧

- Nginx `listen reuseport` — nginx.org/en/docs/http/ngx_http_core_module.html
- Cloudflare: How to receive a million packets per second — blog.cloudflare.com
- Brendan Gregg: Linux Performance — brendangregg.com
- uber-go/automaxprocs — github.com/uber-go/automaxprocs
- Linux kernel networking tuning — access.redhat.com/documentation

### 基礎筆記

- 本專案 `notes/io-model-and-linux-high-concurrency-study-notes.md` — I/O 模型與高併發基礎概念筆記
- study-area.sre.tw R4 系列 — Linux 效能優化實戰
