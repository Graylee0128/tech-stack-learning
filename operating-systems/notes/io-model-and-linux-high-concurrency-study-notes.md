# I/O Model 與 Linux 高併發教學筆記

> 這份筆記以 Go 後端工程師的視角，把「I/O model」、「高併發」、「Linux 效能分析」串成一條工作上用得到的線。目標不是背名詞，而是：能白話講清楚、能對應到 Go runtime 行為、能在高流量場景下判斷瓶頸在哪一層。

---

## 目錄

- [1. 效能指標：到底在看什麼](#1-效能指標到底在看什麼)
- [2. 平均負載與 Context Switch](#2-平均負載與-context-switch)
- [3. I/O Model 全貌](#3-io-model-全貌)
  - [3.1 兩階段模型：等資料 + 搬資料](#31-兩階段模型等資料--搬資料)
  - [3.2 Blocking I/O](#32-blocking-io)
  - [3.3 Non-blocking I/O](#33-non-blocking-io)
  - [3.4 I/O Multiplexing](#34-io-multiplexing)
  - [3.5 Signal-driven I/O](#35-signal-driven-io)
  - [3.6 Asynchronous I/O](#36-asynchronous-io)
  - [3.7 一句話分辨五種模型](#37-一句話分辨五種模型)
  - [3.8 Readiness vs Completion：更實戰的分類軸](#38-readiness-vs-completion更實戰的分類軸)
  - [3.9 常見誤解](#39-常見誤解)
- [4. select / poll / epoll 深入比較](#4-select--poll--epoll-深入比較)
  - [4.1 比較表](#41-比較表)
  - [4.2 Level-Triggered vs Edge-Triggered](#42-level-triggered-vs-edge-triggered)
  - [4.3 為什麼主流是 non-blocking + epoll](#43-為什麼主流是-non-blocking--epoll)
- [5. C10K 到 C1000K](#5-c10k-到-c1000k)
- [6. 高併發瓶頸分層圖](#6-高併發瓶頸分層圖)
- [7. 博彩與電商案例拆解](#7-博彩與電商案例拆解)
- [8. 網路效能分析：從哪一層開始](#8-網路效能分析從哪一層開始)
- [9. 應用模型比 kernel 調參更重要](#9-應用模型比-kernel-調參更重要)
- [10. Go netpoll 與 I/O Model 對照](#10-go-netpoll-與-io-model-對照)
- [11. Incident 排查提綱：延遲飆高時先看這 8 個指標](#11-incident-排查提綱延遲飆高時先看這-8-個指標)
- [12. 面試版最短回答](#12-面試版最短回答)
- [附錄 A：R4 學習路線地圖](#附錄-ar4-學習路線地圖)
- [附錄 B：搭配 R1 建議](#附錄-b搭配-r1-建議)
- [來源](#來源)

---

## 1. 效能指標：到底在看什麼

### 觀念

效能不是只看 CPU 百分比，而是同時看使用者感受到的快不快，還有系統資源是不是快撐不住了。先記住五個最常用的詞：

| 指標 | 意義 | 白話 |
|------|------|------|
| Latency | 一次請求要等多久 | 客人等多久才上菜 |
| Throughput | 單位時間能處理多少工作 | 一小時出幾道菜 |
| Concurrency | 同時有多少工作在進行 | 同時來幾桌 |
| Utilization | 資源用了多少 | 廚師忙不忙 |
| Saturation | 資源是否已經塞車 | 外場是不是一直在塞單 |

### 工程現象

同一個網站可能出現這種情況：

- CPU 只跑 40%
- 但 ALB latency 很高
- DB connections 爆掉
- 加機器沒有效

這通常表示瓶頸不在純計算，而在等待、連線、鎖、I/O 或 downstream。

### 常見誤解

| 誤解 | 真相 |
|------|------|
| CPU 不高 = 系統沒問題 | 很多慢是因為在等 I/O，不是在算東西 |
| 加機器一定能解 | 如果 bottleneck 在共享資源（DB、Redis、連線池），加機器只是把問題放大 |

### Go 實務映射

Go API server 很常是 I/O bound，不是 CPU bound。看到 goroutine 一大堆時，先問：

- 是不是都在等 DB / Redis / upstream？
- 是不是 timeout 太長導致連線堆積？
- 是不是 connection pool 太小或太大？

---

## 2. 平均負載與 Context Switch

### 為什麼要先懂這個

很多人連「系統為什麼忙」都還沒搞懂，就急著談高併發調優。你至少要先有這些直覺：

- **平均負載不是 CPU 使用率的同義詞**。`load average` 更像是「有多少工作正在等 CPU 或等不可中斷資源」，所以 load 高不一定代表 CPU 已滿。
- **等 I/O 的程序也可能讓 load 上升**。junior 很容易把「CPU 低、load 高、系統慢」看成互相矛盾，其實不矛盾——有些 process 卡在 I/O wait 或不可中斷狀態（D state）。
- **Context switch 太多，本身就是成本**。切換前保存狀態、切換後恢復狀態、cache 可能失效。

### 白話比喻

一個主管看起來很忙，不代表他真的在產出。如果他一直在不同會議室之間來回切換，時間都浪費在轉場。thread / process 的 context switch 也類似。

### 工程現象

如果你用 thread-per-connection 或大量短生命週期工作模型，可能看到：

- context switch 很高
- CPU 不一定滿，但有效工作比例下降
- latency 變差

### Go 實務映射

goroutine 比 OS thread 輕很多，但不是免費。如果你的服務因為 timeout、重試、慢查詢或 blocked channel 導致 goroutine 大量堆積，問題最後還是會反映到 scheduler、記憶體和延遲上。（關於 Go scheduler 如何降低切換成本，見 [Section 10](#10-go-netpoll-與-io-model-對照)）

---

## 3. I/O Model 全貌

### 核心問題

> 當程式要讀資料或等網路回應時，等待的這段時間怎麼安排？

### 分類框架

先校正一個常見混淆：「五種 I/O 模型」和「同步 / 非同步 I/O」不是同一條分類軸。

更精準的分類：

```
I/O 模型
├── Synchronous I/O（資料搬運仍需你自己收尾）
│   ├── Blocking I/O
│   ├── Non-blocking I/O
│   ├── I/O Multiplexing（select / poll / epoll）
│   └── Signal-driven I/O
└── Asynchronous I/O（系統連搬運都幫你做完再通知）
    ├── POSIX AIO
    ├── Linux 原生 AIO
    └── io_uring
```

也就是說：前四種模型都屬於同步 I/O 的不同等待方式，只有 AIO 是真正的非同步 I/O。

### 先分清楚兩組概念

#### blocking / non-blocking

> 當前這次系統呼叫會不會把你卡住？

- blocking：沒準備好就先卡住
- non-blocking：沒準備好就立刻回來（回 `EAGAIN` / `EWOULDBLOCK`）

#### synchronous / asynchronous

> 資料搬運這件事，是不是還要你自己回來收尾？

- synchronous：你還是要自己呼叫 `read()` / `recv()` 把資料拿走
- asynchronous：系統把整件事做完，完成後再通知你

### 3.1 兩階段模型：等資料 + 搬資料

以 socket `read()` 為例，I/O 可拆成兩步：

1. **等 kernel 收到資料**，放進 kernel buffer
2. **把資料從 kernel buffer 複製到 user space buffer**

五種模型的差異，主要出在：

- 你是怎麼等第 1 步完成的
- 第 2 步是同步做，還是系統幫你做完再通知你

### 3.2 Blocking I/O

**運作方式**：呼叫 `read()` 時，如果資料還沒到 → thread 直接睡下去 → kernel 等到資料準備好 → 複製給你 → 呼叫返回。

**白話比喻**：你站在門口一直等快遞，快遞到了再親手把包裹搬進房間。

| 優點 | 缺點 |
|------|------|
| 好懂，程式流程直線 | 一個 thread 只服務一個等待點 |
| 單連線、低併發時夠用 | thread 數一多，記憶體和 context switch 成本就上來 |

**關鍵記憶點**：blocking 最大的問題不是「它很慢」，而是「它讓等待成本很高」。

### 3.3 Non-blocking I/O

**運作方式**：socket 設成 non-blocking 後，`read()` 不會睡下去，沒東西可讀就立刻返回。你可以之後再回來試。

**白話比喻**：你一直自己探頭看快遞到了沒，沒到就先做別的。

| 優點 | 缺點 |
|------|------|
| 不會把 thread 卡死 | 如果一直自己重複試 = busy polling |
| 給 event-driven 模型打基礎 | CPU 可能空轉得很兇 |

**關鍵記憶點**：non-blocking 不是「魔法加速」，它只是把「等」從睡覺改成你自己要想辦法安排。

### 3.4 I/O Multiplexing

**運作方式**：把很多 fd 交給 `select` / `poll` / `epoll`，讓多工機制替你等：誰可讀、誰可寫、誰發生錯誤。等它通知你「這幾個 ready 了」，你再對那些 fd 呼叫 `read()` / `write()`。

**白話比喻**：你請管理員幫你盯，哪一戶有快遞到了再叫你下來拿。

**關鍵理解**：`select/poll/epoll` **不是**直接幫你把資料讀完。它們是 readiness notification——告訴你「現在可以讀了」，你還是要自己去讀。

**為什麼這招重要**：你不需要一個 thread 綁一個 socket。可以用少量 worker 管很多連線，把 thread 留給真的有事件的連線。

（三者的詳細差異見 [Section 4](#4-select--poll--epoll-深入比較)）

### 3.5 Signal-driven I/O

**運作方式**：先註冊訊號 → 當 fd ready 時 kernel 發 signal 給你 → 你收到後再自己去處理 I/O。

通知方式是非同步的，但真正的資料讀取仍是同步收尾的，所以它屬於 synchronous I/O 裡的 readiness-based 子類。

實務上你比較少在一般後端服務中把它當主角。知道它存在即可。

### 3.6 Asynchronous I/O

**運作方式**：你先把 I/O 請求交出去 → 系統連資料搬運都幫你做 → 做完後再通知你。

**白話比喻**：你連搬包裹都外包，東西進房間後才通知你。

**和 multiplexing 的真正差別**：

| | Multiplexing | AIO |
|---|---|---|
| 通知你什麼 | 「可以讀了」（ready） | 「已經讀完了」（done） |
| 你要做什麼 | 自己再 `read()` | 直接拿結果 |
| 分類 | readiness-based | completion-based |

### 3.7 一句話分辨五種模型

| 模型 | 一句話 |
|------|------|
| Blocking I/O | 我呼叫一次，沒好就卡在那裡等 |
| Non-blocking I/O | 我呼叫一次，沒好就立刻回來 |
| I/O Multiplexing | 我先等系統告訴我「哪些 fd 好了」，再自己去讀 |
| Signal-driven I/O | 系統用 signal 跟我說「某個 fd 好了」，我再自己去讀 |
| Asynchronous I/O | 我把整個 I/O 工作交出去，做完才通知我 |

### 3.8 Readiness vs Completion：更實戰的分類軸

| 分類 | 代表機制 | 系統通知你什麼 |
|------|------|------|
| Readiness-based | `select`、`poll`、`epoll`、signal-driven | 「現在可以做 I/O 了」 |
| Completion-based | POSIX AIO、Linux AIO、`io_uring` | 「I/O 已經做完了」 |

這條軸在實務上往往比「五種模型名稱背出來」更有用。

### 3.9 常見誤解

| 誤解 | 真相 |
|------|------|
| non-blocking 一定比較快 | 如果只是把 blocking 改成 busy polling，CPU 可能更慘 |
| async 聽起來最強，一定最好 | 很多高併發網路服務的主流仍然是 non-blocking + epoll |
| select/poll/epoll 已經把資料幫我讀好了 | 它們只是通知你「現在可以讀了」 |
| non-blocking = async | non-blocking 只代表不會傻等，不代表系統幫你完整代辦 |
| 五種模型和同步/非同步是同一層分類 | 前四種屬同步 I/O 的不同等待方式，只有 AIO 是真正非同步 |

---

## 4. select / poll / epoll 深入比較

### 觀念

當連線變很多時，傳統的「一個連線一個 thread」很難撐，於是改成：socket 設為 non-blocking → 由多工機制監看很多 fd → 誰 ready 再交給 worker 處理。

### 白話比喻

- `select` / `poll`：你每一輪都拿整份名單，一個一個問「你有事嗎？」
- `epoll`：誰有事誰舉手，系統把有事的人放進清單，你直接處理那份清單

### 4.1 比較表

| 維度 | `select` | `poll` | `epoll` |
|------|----------|--------|---------|
| **fd 上限** | 預設 1024（`FD_SETSIZE`） | 無硬限制（用 linked list） | 無硬限制 |
| **監聽方式** | 每次呼叫傳入整個 fd_set，kernel 線性掃描 | 每次呼叫傳入 pollfd 陣列，kernel 線性掃描 | fd 註冊到 kernel 的紅黑樹，只回傳 ready 的 fd |
| **每次呼叫開銷** | O(n)：全部掃一遍 | O(n)：全部掃一遍 | O(1) per event：只處理 ready 的 |
| **fd 集合傳遞** | 每次都要把整個 fd_set 從 user space 複製到 kernel | 每次都要複製整個陣列 | 只需 `epoll_ctl` 增刪，`epoll_wait` 時不需重傳 |
| **觸發模式** | 僅 Level-Triggered | 僅 Level-Triggered | 支援 LT 和 ET |
| **適用場景** | fd 少、跨平台需求 | fd 中等、需要突破 1024 限制 | 大量連線（C10K+） |
| **典型使用者** | 老舊程式碼、跨平台庫 | 中小型服務 | nginx、Go runtime netpoll、Redis |
| **主要缺點** | fd 上限太低、每次全掃 | 仍需每次全掃 | Linux 限定、ET 模式下程式設計較複雜 |

### 4.2 Level-Triggered vs Edge-Triggered

這是理解 `epoll` 行為的關鍵：

| | Level-Triggered (LT) | Edge-Triggered (ET) |
|---|---|---|
| **通知時機** | 只要 fd 還有資料可讀，每次 `epoll_wait` 都會通知你 | 只在狀態改變時通知一次 |
| **沒讀完會怎樣** | 下一輪還會再提醒你 | 不會再提醒，直到有新資料到達 |
| **程式設計要求** | 比較寬容，慢慢讀也行 | 必須一次把資料盡量讀乾淨（loop until `EAGAIN`） |
| **效能特性** | 可能產生多餘的 wake-up | 更少的 wake-up，但出錯代價更高 |
| **適用場景** | 對正確性要求高、不想踩坑 | 高效能服務、能保證一次讀完的場景 |

#### 5 分鐘口頭版講解

> 想像你住公寓，管理員幫你收包裹：
>
> **LT 模式**：只要你的包裹還放在管理室，管理員每天都會跟你說「你有包裹喔」。你可以今天拿一半，明天再拿剩下的，他不會忘記提醒你。好處是不會漏掉，壞處是管理員一直在叫你，即使你已經知道了。
>
> **ET 模式**：管理員只在包裹剛到的那一刻通知你一次。之後不管你有沒有拿，他都不會再提醒。所以你收到通知後，必須立刻下去把所有包裹全部搬完。如果你只拿了一半就回去，剩下的就會一直躺在那裡，直到有新包裹到才會再通知你。
>
> Go runtime 的 netpoll 用的是 ET 模式。這也是為什麼 netpoll 內部會做 loop read——它必須確保每次被喚醒時把資料盡量讀乾淨。

#### ET 沒處理乾淨會怎樣

1. 資料殘留在 kernel buffer
2. 沒有新事件觸發 → `epoll_wait` 不會再回報這個 fd
3. 連線看起來「死了」但其實只是沒人去讀
4. 如果是 server，client 會覺得 request 被吃掉了

這是 ET 模式下最常見的 bug pattern。

### 4.3 為什麼主流是 non-blocking + epoll

C10K 問題的關鍵在兩件事：

1. 怎麼在少量 thread 內處理很多請求
2. 怎麼節省資源去處理更多連線

`non-blocking + epoll` 剛好很適合：

- 少量 worker 監看大量 fd
- 只在有事件時處理
- 避免 thread-per-connection 的高成本

`nginx`、Redis、Go runtime netpoll 的思路都和這條線很接近。

---

## 5. C10K 到 C1000K

### 觀念

`C10K` 討論的是一台機器如何處理一萬個連線。真正痛點不是硬體不夠，而是軟體模型撐不住。

### 演進主線

```
thread-per-connection（blocking）
  → 太浪費：每個連線佔一個 thread，記憶體和切換成本爆炸
  ↓
non-blocking + select/poll
  → 能撐更多，但 fd 多了以後每次全掃成本太高
  ↓
non-blocking + epoll（event-driven）
  → C10K 的主流解法：少量 thread 管大量連線
  ↓
C1000K：百萬連線
  → 光靠 epoll 不夠，還要一起處理 CPU、記憶體、網路和 kernel 限制
```

### C1000K 級別的常見瓶頸

| 層級 | 瓶頸 |
|------|------|
| OS 資源 | fd 數量、單連線記憶體成本 |
| Kernel | socket buffer、backlog、conntrack table |
| 網路 | NIC 吞吐、PPS、LB / firewall / router 能力 |
| 應用 | 序列化成本、GC 壓力、goroutine 排程 |

### 常見誤解

| 誤解 | 真相 |
|------|------|
| 高併發 = 每秒請求量高 | 高併發更偏向「同時進行中的工作數與連線數」 |
| 只要換成 nginx 就結束了 | 後面還有 DB、cache、MQ、kernel、網路設備 |

---

## 6. 高併發瓶頸分層圖

當系統扛不住大量連線時，瓶頸可能出在任何一層。以下按從上到下的順序排列：

```
┌─────────────────────────────────────────────────────┐
│  Application Layer                                   │
│  ┌─────────────────────────────────────────────────┐ │
│  │ • request pattern（熱點集中、慢查詢）             │ │
│  │ • 序列化 / 反序列化成本（JSON、protobuf）         │ │
│  │ • connection pool 設定（太小排隊、太大佔資源）     │ │
│  │ • timeout 設定（太長堆積、太短誤殺）              │ │
│  │ • cache hit rate（miss → 打穿 DB）               │ │
│  │ • 重試風暴（upstream 慢 → 指數放大）              │ │
│  └─────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────┤
│  Runtime Layer（Go 為例）                            │
│  ┌─────────────────────────────────────────────────┐ │
│  │ • goroutine 數量暴增（leak、blocked channel）     │ │
│  │ • GC 壓力（STW、大量小物件）                      │ │
│  │ • stack growth / shrink 頻率                      │ │
│  │ • netpoll 回調延遲                                │ │
│  │ • scheduler latency（GOMAXPROCS 設定）            │ │
│  └─────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────┤
│  Kernel Layer                                        │
│  ┌─────────────────────────────────────────────────┐ │
│  │ • fd 上限（ulimit -n、fs.file-max）               │ │
│  │ • TCP backlog（somaxconn、syn_backlog）           │ │
│  │ • conntrack table 滿（NAT / firewall 場景）       │ │
│  │ • socket buffer 大小（rmem_max、wmem_max）        │ │
│  │ • context switch 頻率                             │ │
│  │ • softirq / 中斷處理負載                          │ │
│  │ • TIME_WAIT 堆積                                  │ │
│  └─────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────┤
│  Network Layer                                       │
│  ┌─────────────────────────────────────────────────┐ │
│  │ • NIC 頻寬 / PPS 上限                             │ │
│  │ • LB 連線數上限、health check 頻率               │ │
│  │ • Firewall / Security Group 規則數                │ │
│  │ • DNS 解析延遲                                    │ │
│  │ • TCP retransmission / packet loss                │ │
│  │ • TLS handshake 成本                              │ │
│  └─────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────┤
│  Shared Dependency Layer                             │
│  ┌─────────────────────────────────────────────────┐ │
│  │ • DB connection pool 飽和                         │ │
│  │ • Redis 單執行緒阻塞（KEYS、大 value）            │ │
│  │ • MQ 消費速度 < 生產速度                          │ │
│  │ • 跨服務 cascading failure                        │ │
│  └─────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

**使用方式**：遇到高併發問題時，從上往下逐層排查。先確認應用層沒有明顯問題（timeout、pool、cache），再往下看 runtime、kernel、network。大多數線上問題的根因在 Application 或 Shared Dependency 這兩層。

---

## 7. 博彩與電商案例拆解

### 案例一：電商秒殺——短時間尖峰流量

**場景**：雙 11 零點開搶，3 秒內湧入 50 萬請求。

```
時間線：
T-5s   預熱完成，cache 就緒
T+0s   閘門打開，請求瞬間湧入
T+1s   QPS 從 5K 飆到 200K
T+3s   DB connection pool 全滿
T+5s   upstream timeout → 重試風暴
T+10s  cascading failure → 全站延遲飆高
```

**瓶頸分析**：

| 層級 | 會先碰到什麼 |
|------|------|
| Application | 庫存扣減的 hot key 競爭、cache miss 打穿 DB |
| Runtime | goroutine 暴增（每個 pending request 佔一個）、GC 壓力上升 |
| Kernel | TCP backlog 滿 → SYN drop、conntrack table 滿 |
| Network | LB 連線數接近上限 |
| Shared Dep | DB connection pool 飽和 → 排隊 → 連鎖 timeout |

**常見緩解手段**：

- 前端限流（令牌桶、排隊頁）
- 庫存預扣到 Redis，非同步落 DB
- DB connection pool 加 queue timeout，避免無限等待
- 設合理的 client timeout + circuit breaker，防止重試風暴
- backlog、conntrack、fd 預先調大

### 案例二：博彩即時盤口——大量 WebSocket 長連線

**場景**：熱門足球賽事，10 萬用戶同時在線，每秒推送 500 次盤口變動。

```
連線特性：
- WebSocket 長連線，單連線生命週期 60~90 分鐘
- 大量連線處於 idle 狀態，但隨時需要接收 push
- 進球/紅牌等事件 → 瞬間所有連線同時需要推送
```

**瓶頸分析**：

| 層級 | 會先碰到什麼 |
|------|------|
| Application | 廣播風暴：10 萬連線同時寫，write buffer 堆積 |
| Runtime | 每個 WebSocket 連線綁一個 goroutine（讀）+ 一個（寫）= 20 萬 goroutine，記憶體壓力 |
| Kernel | 10 萬 fd、socket buffer 總量、keep-alive 探測成本 |
| Network | 單機出口頻寬、PPS 上限 |
| Shared Dep | 盤口資料源如果延遲 → 所有推送都 stale |

**常見緩解手段**：

- 分組推送（fan-out tree），避免單點廣播
- 合併小訊息（batching），降低 PPS
- 用 `gobwas/ws` 或 `netpoll` 框架取代 `gorilla/websocket`，降低 per-connection goroutine 數
- 按興趣 topic 分 channel，減少不必要推送
- 連線層和業務層分離部署，連線層水平擴展

### 兩個案例的共同教訓

1. **瓶頸通常不在單一層**——秒殺的問題看起來像 DB，但根因常常是 timeout 和重試策略沒設好
2. **連線數高 ≠ TPS 高**——博彩場景連線很多但大部分 idle，電商場景連線不多但每個都在做事
3. **先改應用層，再碰 kernel**——大多數團隊最有效的改善在 timeout、pool、cache、限流

---

## 8. 網路效能分析：從哪一層開始

### 觀念

> 先搞清楚你在測哪一層，否則數字再漂亮也不代表問題找對了。

不同層要看的指標不同：

| 層級 | 關注指標 | 常用工具 |
|------|------|------|
| Link / Routing | BPS、PPS | `iftop`、`sar`、`/proc/net/dev`、`ethtool` |
| Transport | TCP/UDP throughput、latency | `iperf3`、`netperf`、`ss` |
| Connection | concurrent connections、CPS | `ss`、`netstat`、`conntrack` |
| Application | HTTP latency、RPS、error rate | `ab`、`wrk`、`jmeter`、`vegeta` |
| Packet-level | 封包內容、重傳、亂序 | `tcpdump`、`wireshark` |

### 白話比喻

你不能用「高速公路總車流量」去判斷「某家餐廳出餐效率」。同樣地，`iperf3` 的頻寬數字不能直接當作 HTTP 服務的真實表現。

### 常見誤解

| 誤解 | 真相 |
|------|------|
| 壓測能打很高，線上一定也行 | 壓測通常只覆蓋一部分真實路徑 |
| HTTP 慢就是網路慢 | 可能是 app、序列化、DB、TLS、cache miss |

---

## 9. 應用模型比 kernel 調參更重要

### 觀念

優化層級的優先順序：

```
1. 先把應用模型寫對（I/O 模型、worker 模型、連線重用、cache）
2. 再看 socket / TCP / kernel 參數
3. 最後才考慮 DPDK、XDP 等繞過 kernel 的方案
```

### 應用程式層最常見的改善點

- I/O 模型選對
- process / worker 模型合理
- 長連線重用，減少 TCP 建立成本
- cache 使用得當
- 協定與序列化成本合理（JSON → protobuf）

### Go 團隊最常做的優化

- 調整 `http.Transport`（MaxIdleConns、IdleConnTimeout）
- 設定合理的 timeout 與 keep-alive
- 改善連線池與重試策略
- 降低單請求內的 blocking dependency
- 加 cache、拆熱點、做限流

不是一開始就去碰 `XDP`。

### 常見誤解

| 誤解 | 真相 |
|------|------|
| 性能優化 = sysctl 調參 | 太片面。先改 request pattern、timeout、pool、cache |
| 先談 DPDK 比較厲害 | 對大多數後端團隊，先把應用和 kernel 基本功練好效益更高 |

---

## 10. Go netpoll 與 I/O Model 對照

### Go 沒讓你直接寫 epoll，但底層就是 epoll

Go runtime 在 Linux 上有一個 **network poller**（`runtime/netpoll_epoll.go`），它的核心行為：

```
初始化：
  epoll_create1() → 建立 epoll instance

註冊 fd：
  當 goroutine 做網路 I/O（net.Conn.Read 等）且資料未就緒時
  → runtime 把 fd 註冊到 epoll（epoll_ctl + EPOLLET）
  → goroutine 被 park（暫停排程）

事件驅動：
  sysmon / findrunnable 定期呼叫 netpoll()
  → epoll_wait() 拿到 ready 的 fd list
  → 把對應的 goroutine unpark（重新排入 run queue）
  → goroutine 醒來繼續執行 read/write
```

### 關鍵設計決策

| 決策 | 原因 |
|------|------|
| 用 Edge-Triggered | 減少 wake-up 次數，配合 loop read 確保讀完 |
| goroutine park/unpark 取代 thread block | goroutine 只佔 ~2KB stack，park 成本遠低於 thread sleep |
| netpoll 整合進 scheduler | 不需要額外的 event loop thread，由 sysmon 和 findrunnable 驅動 |

### 和 GMP 的關係

```
G（goroutine）做 I/O
  → 資料沒好 → G 被 park，M 被釋放去跑其他 G
  → netpoll 檢測到 fd ready → G 被 unpark，放進 P 的 local run queue
  → 某個 M 撿起 G 繼續執行
```

這就是為什麼 Go 能用幾十條 OS thread 管幾十萬個 goroutine 的 I/O：

- goroutine 不等於 thread → 切換成本低
- I/O 等待不佔 thread → M 可以去做別的
- epoll ET 減少 wake-up → 降低 kernel/user 互動成本

### Go 視角的 I/O Model 對照圖

| 傳統 Linux | Go runtime | 差異 |
|------|------|------|
| 一個 thread 綁一個連線 | 一個 goroutine 綁一個連線，但 thread 共享 | goroutine stack 只佔 ~2KB vs thread ~1MB |
| epoll_wait 在 event loop thread 中 | netpoll 被 sysmon 和 scheduler 驅動 | 不需要手動管理 event loop |
| 開發者手動 `epoll_ctl` + `read()` | 開發者寫同步 `conn.Read()`，runtime 自動處理 | 看起來像 blocking，底層是 non-blocking + epoll |
| ET 模式需要手動 loop read | runtime 內部幫你做 loop read | 開發者不需要知道 ET 的細節 |

### 但 Go 不是萬能的

即使 runtime 幫你包了 epoll，以下問題仍然是你的責任：

- timeout 設太長 → goroutine 堆積 → 記憶體暴增
- connection pool 太小 → 排隊 → 延遲飆高
- 慢 upstream → goroutine 全部卡住等回應
- 大量閒置 WebSocket → fd 和 goroutine 都佔著不放
- 沒有 circuit breaker → cascading failure

**一句話**：Go 幫你把 I/O model 包成同步寫法，但高併發的系統瓶頸不會因此消失。

---

## 11. Incident 排查提綱：延遲飆高時先看這 8 個指標

當線上 Go 服務變慢時，按這個順序問：

| # | 指標 | 怎麼看 | 在判斷什麼 |
|---|------|------|------|
| 1 | **P99 latency 的變化** | APM / Prometheus histogram | 是整體變慢還是尾部變慢 |
| 2 | **error rate** | HTTP 5xx rate、gRPC error code | 是慢還是壞 |
| 3 | **goroutine 數量** | `runtime.NumGoroutine()`、pprof | 是不是在堆積（leak / blocked） |
| 4 | **CPU utilization** | `top`、`mpstat`、Grafana | 是在算還是在等 |
| 5 | **memory / GC** | `GOGC`、`runtime.MemStats`、pprof heap | GC 是否頻繁、STW 是否過長 |
| 6 | **DB / Redis latency** | 慢查詢 log、connection pool metrics | 共享依賴是否拖後腿 |
| 7 | **fd 數量 / connection count** | `ss -s`、`/proc/pid/fd` | 是不是連線洩漏或 TIME_WAIT 堆積 |
| 8 | **network retransmission / packet loss** | `netstat -s`、`ss -ti` | 是不是網路層在丟包重傳 |

### 排查決策樹

```
延遲飆高
├── goroutine 暴增？
│   ├── 是 → 找 blocked 的原因（timeout、channel、lock）
│   └── 否 ↓
├── CPU 高？
│   ├── user CPU 高 → pprof CPU profile 找熱點
│   ├── system CPU 高 → 看 context switch、syscall、irq
│   └── 否 ↓
├── GC 頻繁 / STW 長？
│   ├── 是 → 看 heap profile、降低分配率
│   └── 否 ↓
├── DB / Redis 慢？
│   ├── 是 → 慢查詢、connection pool、索引
│   └── 否 ↓
├── fd / connection 異常？
│   ├── 是 → 連線洩漏、TIME_WAIT、backlog
│   └── 否 ↓
└── 網路層問題？
    └── 重傳率高 → MTU、擁塞、路由、NIC
```

---

## 12. 面試版最短回答

### 什麼是 blocking / non-blocking I/O？

blocking I/O 是呼叫 `read()` 之後，資料沒到就卡住等；non-blocking I/O 則是不讓 thread 卡死，可以先去做別的事，再搭配事件通知機制回來處理。

### `epoll` 在解決什麼問題？

它在解決大量 fd 的事件監聽成本。讓 Linux 可以用更適合大規模連線的方式通知應用程式哪些 socket ready，不需要每一輪都把全部 fd 掃一遍。它用紅黑樹管理 fd 註冊、用 ready list 只回傳有事件的 fd，所以處理成本和 ready 事件數成正比，不隨總 fd 數線性增長。

### 為什麼 Go 工程師還要懂這些？

因為 Go runtime 雖然幫你包起來了，但高併發時真正出問題的地方，還是會落在連線、timeout、pool、I/O 等待、系統資源和 network stack。你懂底層模型，排查會快很多。而且面試時被問到「Go 底層怎麼處理網路 I/O」，你能回答「runtime 用 non-blocking fd + epoll ET + goroutine park/unpark」，遠比「Go 很快」有說服力。

### Level-Triggered 和 Edge-Triggered 差在哪？

LT 是只要有資料就一直通知你；ET 是狀態變化時只通知一次。Go runtime 用 ET 是為了減少不必要的 wake-up，但代價是內部必須 loop read 把資料讀完。

---

## 附錄 A：R4 學習路線地圖

> 這份筆記的原理素材主要來自 `study-area.sre.tw` 的 `R4: Linux 效能優化實戰`。以下是 R4 的知識結構地圖，幫助你理解各章節在整條主線中的位置。

### R4 四大段

| 範圍 | 主題 | 在學什麼 |
|------|------|------|
| `01~13` | CPU 與排程 | load average、context switch、中斷、CPU 使用率、找 CPU bottleneck |
| `14~21` | 記憶體 | memory 運作、buffer/cache、page cache、memory leak、swap |
| `22~31` | 檔案系統與磁碟 I/O | file system、disk I/O、IOPS、log 打爆、慢 SQL、Redis 延遲 |
| `32~35` | I/O model 與高併發 | blocking/non-blocking、sync/async、C10K/C1000K |

### 為什麼這個順序很重要

線上變慢時，症狀常常很像，但根因不在同一層：

- API latency 高，可能是 CPU 爆
- 也可能是 page cache miss 變多
- 也可能是 disk I/O 等太久
- 也可能是 Redis 慢
- 也可能只是 thread / connection 模型不對

R4 的安排是在訓練你不要一看到「慢」就只會喊 `epoll` 或 `加機器`。

### 各段重點摘要

#### CPU 線（02~13）

- **02 平均負載**：load average ≠ CPU 百分比。load 高可能有很多 task 在等 I/O。
- **03~04 Context Switch**：大量時間花在切換 = CPU 看起來忙但吞吐不好。
- **05 CPU 100%**：分清 user CPU / system CPU / 單核滿 / 整體滿。
- **06 軟中斷與硬中斷**：網卡收包、磁碟 I/O、kernel 事件處理，高 PPS 時要看 irq 分佈。
- **07~08 D state 與 zombie**：D state 常暗示在等磁碟或 kernel resource。
- **09~13 分析套路**：先量測 → 定位熱點 → 決定是否優化 → 先做低副作用的改善。

#### 記憶體線（14~21）

- **15 記憶體運作**：不只是「程式吃多少 RAM」，還有 page、cache、回收、換出。
- **16 buffer/cache**：Linux 拿空閒記憶體做 cache 通常不是壞事，要分清正常利用 vs 真的壓到 swap。
- **17 page cache**：同樣的檔案第二次讀比較快，很多「磁碟慢」其實是 cache 行為改變。
- **18 memory leak**：Go 常見的 goroutine 堆積、map 沒清、GC 壓力變重。
- **19~20 swap**：不是看到 swap 有用量就立刻下結論。要理解 swappiness、NUMA 影響。

#### 檔案系統與磁碟 I/O 線（22~31）

- **22~23 fs vs disk**：磁碟沒壞不代表 file system 沒問題。
- **24~25 disk stack**：同樣叫「磁碟慢」，random vs sequential 表現差很多。
- **26 狂打日誌**：很多 I/O 問題是應用行為太粗暴（log 太多、一直 flush）。
- **28 慢 SQL**：使用者感受到的 I/O 問題常穿過應用 → DB → 儲存整條鏈。
- **29 Redis 延遲**：persistence、blocking command、單執行緒模型都可能造成延遲。

---

## 附錄 B：搭配 R1 建議

這份筆記是底層直覺。如果你只看 R4，你會知道系統怎麼慢；但不一定知道為什麼團隊要在意這些慢。R1 會補上另一半：

- 為什麼要先定義 SLI / SLO
- 為什麼監控不能只看 dashboard
- 為什麼容量規劃跟高併發是同一題
- 為什麼 on-call 和 automation 會反過來決定系統品質

---

## 來源

- `R4 #01 CH01-04`: https://study-area.sre.tw/04_Linux/R4-01/
- `R4 #02 共筆（CH05-06）`: https://hackmd.io/%40sre-tw/ryGdFLIY8
- `R4 #03 共筆（CH07-10）`: https://hackmd.io/%40sre-tw/HyrkQYWcU
- `R4 #04 共筆（CH11-13）`: https://hackmd.io/%40sre-tw/HJCaOYW58
- `R4 #05 共筆（CH14-16）`: https://hackmd.io/%40sre-tw/rJyiTZr3I
- `R4 #06 共筆（CH17-20）`: https://hackmd.io/%40sre-tw/HkpyqTGRI
- `R4 #07 共筆（CH21-23）`: https://hackmd.io/%40sre-tw/Sk8WqpfRL
- `R4 #08 共筆（CH24-26）`: https://hackmd.io/%40sre-tw/ByY796G0L
- `R4 #09 共筆（CH27-29）`: https://hackmd.io/%40sre-tw/SJVr9pGAU
- `R4 #10 共筆（CH30-32）`: https://hackmd.io/%40t18NtqosQuCL3YbId5boEg/rkK9LzrXw
- `R4 #11 共筆（CH33-35）`: https://hackmd.io/%40sre-tw/rktsLK_QD
- `01 如何學習 Linux 效能最佳化`: https://study-area.sre.tw/pdf/Linux/01_How-to-Learn.pdf
- `35. 基礎篇：C10K與C1000K回顧`: https://study-area.sre.tw/pdf/Linux/35_recap_C10K_C1000K.pdf
- `36 - 套路篇: 怎麼評估系統的網路效能`: https://study-area.sre.tw/pdf/Linux/36_evaluate_network_performance.pdf
- `43/44 網路性能最佳化的幾個思路`: https://study-area.sre.tw/pdf/Linux/43_44_network_performance_optimization.pdf
- `Linux 中的五種 I/O 模型`: https://github.com/0voice/linux_kernel_wiki/blob/main/%E6%96%87%E7%AB%A0/%E7%BD%91%E7%BB%9C%E5%8D%8F%E8%AE%AE%E6%A0%88/Linux%20%E4%B8%AD%E7%9A%84%E4%BA%94%E7%A7%8DIO%E6%A8%A1%E5%9E%8B.md
- Go runtime netpoll: https://go.dev/src/runtime/netpoll.go
- Go runtime epoll implementation on Linux: https://go.dev/src/runtime/netpoll_epoll.go
