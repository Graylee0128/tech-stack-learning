# I/O Model 與 Linux 高併發教學筆記

> 這份筆記以 `study-area.sre.tw` 的 `R4: Linux 效能優化實戰` 為主軸重組，不是逐頁翻譯，而是用 junior 工程師比較容易吸收的方式，把「I/O model」、「高併發」、「Linux 效能分析」串成一條工作上用得到的線。

## 這份筆記要解決什麼問題

如果你之後是用 Go 做博彩或電商後端，最常碰到的不是「演算法不會寫」，而是這幾類問題：

- request 一多，延遲突然上升
- CPU 沒滿，但系統就是變慢
- goroutine 很多，吞吐卻沒上去
- WebSocket 或 keep-alive 連線一堆，機器開始喘
- 壓測數字很好看，上線後卻還是出事

R4 這條線在教你的，其實不是「神奇調參」。它在教你先建立一個判斷框架：

1. 先知道效能要看哪些指標
2. 再知道 I/O 等待是怎麼發生的
3. 再知道大量連線時 Linux 為什麼容易卡住
4. 最後才談要調哪一層

## 一句話先講完 R4 的核心

高併發問題通常不是單一魔法參數沒調好，而是整條請求路徑裡，有某一層正在浪費資源或已經飽和。  
而 I/O model，就是你理解這件事的起點。

## 1. 效能問題到底在看什麼

### 觀念

`01 如何學習 Linux 效能最佳化` 先把方向講得很清楚：效能不是只看 CPU 百分比，而是同時看使用者感受到的快不快，還有系統資源是不是快撐不住了。

可以先記住幾個最常用的詞：

- `Latency`: 一次請求要等多久
- `Throughput`: 單位時間能處理多少工作
- `Concurrency`: 同時有多少工作在進行
- `Utilization`: 資源用了多少
- `Saturation`: 資源是否已經塞車

### 白話比喻

餐廳生意好不好，不是只看廚房火開多大。你還要看：

- 客人等多久才上菜
- 同時來幾桌
- 廚師有沒有忙到卡住
- 外場是不是一直在塞單

系統效能也是一樣。CPU 很像廚房火力，但不是全部。

### 工程現象

同一個網站可能出現這種情況：

- CPU 只跑 40%
- 但 ALB latency 很高
- DB connections 爆掉
- 加機器沒有效

這通常表示瓶頸可能不在純計算，而在等待、連線、鎖、I/O 或 downstream。

### 常見誤解

- `CPU 不高 = 系統沒問題`  
  錯。很多慢是因為在等 I/O，不是因為在算東西。
- `加機器一定能解`  
  錯。如果 bottleneck 在共享資源，例如資料庫、Redis、網路、連線池，加機器可能只是把問題放大。

### Go 實務映射

Go API server 很常是 I/O bound，不是 CPU bound。  
你看到 goroutine 一大堆時，要先問：

- 是不是都在等 DB / Redis / upstream？
- 是不是 timeout 太長導致連線堆積？
- 是不是 connection pool 太小或太大？

## 1.5 補上 02~34：R4 前半段到底在鋪什麼

你這個提醒很重要。  
如果只抓 `01、35、36、43/44` 幾個點，會很像在直接摘結論。  
但 `R4` 真正厲害的地方，其實是它在 `02~34` 先把你訓練成：

- 知道 CPU 問題怎麼看
- 知道 memory 問題怎麼看
- 知道 file system / disk I/O 問題怎麼看
- 最後才回到 I/O model、disk bottleneck、network basics

也就是說，`I/O model` 不是孤立的一章，  
它是整條 Linux 效能分析主線裡的一個關鍵轉折點。

### 你可以把 `R4 #01 ~ #11` 理解成這四大段

| 範圍 | 主題 | 你在學什麼 |
|------|------|------|
| `01~13` | CPU 與排程世界 | load average、context switch、中斷、CPU 使用率、怎麼找 CPU bottleneck |
| `14~21` | 記憶體世界 | memory 運作、buffer/cache、page cache、memory leak、swap、怎麼查 memory 問題 |
| `22~31` | 檔案系統與磁碟 I/O 世界 | file system、disk I/O、log 打爆、慢 SQL、Redis 延遲、怎麼查 I/O bottleneck |
| `32~35` | I/O model 與高併發世界 | blocking / non-blocking、sync / async、Linux 網路基礎、C10K/C1000K |

### 為什麼這個順序很重要

因為線上變慢時，症狀常常會長得很像，但根因不是同一層。

例如：

- API latency 很高，可能是 CPU 爆
- 也可能是 page cache miss 變多
- 也可能是 disk I/O 等太久
- 也可能是 Redis 慢
- 也可能只是 thread / connection 模型不對

`R4` 的安排，其實是在訓練你不要一看到「慢」就只會喊 `epoll` 或 `加機器`。

## 1.6 `02~13`：CPU 線到底在教什麼

`#01 CH01-04` 和 `#02~#04` 這一段，主軸是先建立 CPU 視角。

### `02`: 平均負載

這章在提醒你：

- `load average` 不是 CPU 百分比
- 它更像是「有多少工作正在等 CPU 或等不可中斷資源」
- 所以 load 高，不一定代表 CPU 已滿

這很重要，因為 junior 很容易把：

- `CPU 低`
- `load 高`
- `系統慢`

這三件事看成互相矛盾。  
其實不矛盾，因為有些 process 可能卡在 I/O wait 或不可中斷狀態。

### `03~04`: CPU context switch

這兩章在補一個很關鍵的觀念：

> 系統忙，不代表都在做有效工作。

如果大量時間花在 context switch：

- 保存執行狀態
- 恢復執行狀態
- cache 失效

那 CPU 看起來很忙，但實際吞吐不一定好。

這跟高併發超有關，因為：

- thread 太多
- process 切太碎
- 中斷與排程太頻繁

都會讓切換成本變成真實瓶頸。

### `05`: 某個應用 CPU 100% 怎麼辦

這章是在教你不要只停在 `top` 那一層。  
你要開始學會分：

- 是哪個 process 吃 CPU
- 是 user CPU 還是 system CPU
- 是單核滿還是整體滿
- 是短暫尖峰還是持續壓滿

這種思維以後拿來看 Go 服務也很好用。  
例如：

- 是 JSON encoding 很重？
- 是 GC 很忙？
- 是某個熱迴圈？
- 是 busy polling？

### `06`: 軟中斷與硬中斷

這章很容易被當成太底層跳過，但其實它在幫你理解：

- 網卡收包
- 磁碟 I/O
- kernel 處理事件

這些都不是「應用程式自己突然就拿到資料」。  
中斷、softirq、下半部處理，背後都在幫你接這條鏈。

如果你的服務是高流量或高 PPS，  
你就很可能不是只有 app code 要看，還要看 irq / softirq 分佈。

### `07~08`: 不可中斷程序與殭屍程序

這兩章的價值是讓你分清楚：

- `D state` 不是單純睡著
- zombie 不是還在工作的 process

尤其 `D state` 很重要，因為它常常暗示：

- 在等磁碟
- 在等某些 kernel resource
- 在某些 I/O 路徑上卡住

這也是為什麼前面講 load average 時，會提到「高 load 不一定是 CPU」。

### `09~13`: perf、CPU bottleneck、優化思路、案例答疑

這幾章的重點，不是教你背工具名稱，而是建立分析順序：

1. 先量測
2. 再定位熱點
3. 再決定是否優化
4. 先做低副作用、易回滾的優化

這裡的精神很值得記：

- 不是所有問題都要優化
- 先找最先達到上限的資源
- 先做最簡單且副作用最小的改善

這種思維比單一工具更值錢。

## 1.7 `14~21`：記憶體線到底在教什麼

`#05~#07` 這一段在補 memory 視角。  
很多系統慢，根因不是 CPU，也不是連線模型，而是記憶體管理出了問題。

### `14`: 用 perf 看 Java

雖然例子是 Java，但對你不用太糾結語言。  
它真正要補的是：

- 如何看火焰圖
- 如何找熱點
- 如何分辨「語言 runtime 問題」和「系統層問題」

這放到 Go 也成立。  
只是 Go 你可能改看 `pprof`、runtime 指標、GC 行為。

### `15`: Linux 記憶體怎麼工作

這章是 memory 線的地基。  
至少要有這些直覺：

- 記憶體不是只有「程式吃多少 RAM」
- 還有 page、cache、回收、換出
- 記憶體管理是 kernel 主導的重要資源調度

### `16`: buffer 和 cache

這一章很關鍵，因為很多人看到 Linux 記憶體被吃滿就慌。  
但 Linux 會主動拿空閒記憶體去做 cache，這通常不是壞事。

你要會分：

- `buffer/cache` 高，是不是正常利用
- 還是真的壓到需要 swap、回收、甚至 OOM

### `17`: 系統快取怎麼幫程式變快

這章把 page cache 的價值拉進來：

- 為什麼同樣的檔案第二次讀比較快
- 為什麼 cache hit / miss 會改變 I/O 表現
- 為什麼很多「看起來像磁碟慢」的問題，其實是 cache 行為改變

### `18`: memory leak

這章教的是定位思維：

- 記憶體是真的被持續佔住不放
- 還是只是工作集暫時變大
- 是 app leak、cache 成長、還是 kernel memory 行為

這對 Go 很實用，因為你以後很常遇到：

- goroutine 堆積
- object retention
- map 或 cache 沒清
- GC 壓力變重

### `19~20`: swap 為什麼變高

這兩章的價值是把 `swap = 壞事` 這種太粗糙的直覺拆開。  
你要開始理解：

- swap 為什麼存在
- swappiness 在調什麼
- NUMA 與 swap 可能怎麼互相影響

也就是說，不是看到 swap 有用量就立刻下結論。

### `21`: 怎麼快狠準找到 memory 問題

這章把前面收斂成排查套路。  
核心問題變成：

- 是記憶體不夠？
- 是回收壓力大？
- 是 cache 行為改變？
- 是 app leak？
- 是 cgroup / resource limit？

這種分層問法，比單純看 `free -m` 強太多。

## 1.8 `22~31`：檔案系統與磁碟 I/O 線到底在教什麼

這一段其實是很多後端工程師最容易低估、但線上最容易踩到的區塊。

### `22~23`: 文件系統與磁碟不是同一件事

這兩章的第一個核心觀念就是：

- disk 是底層 block device
- file system 是你如何組織、命名、索引、存取資料的方式

也就是說：

- 磁碟沒壞，不代表 file system 沒問題
- file 操作慢，不一定只是硬碟本體慢

inode、directory entry、metadata、link，這些都開始進場。

### `24~25`: Linux 磁碟 I/O 怎麼工作

這兩章在補 disk stack 直覺：

- block device
- I/O scheduler
- IOPS / throughput / latency
- random vs sequential

也就是你開始知道：

- 同樣叫做「磁碟慢」，可能完全不是同一種慢
- 隨機讀寫跟順序讀寫的表現可能差很多

### `26`: 找出狂打日誌的內鬼

這章很實戰。  
因為很多 I/O 問題不是 storage 本身爛，而是應用行為太粗暴。

例如：

- log 太多
- log level 太高
- 一直 flush
- 同一路徑被高頻寫入

這種問題不先在應用層修，底下再怎麼調都很有限。

### `27`: 為什麼磁碟 I/O 延遲很高

這章開始把 disk I/O 問題往 latency 視角看。  
重點不是只問「有沒有在讀寫」，而是問：

- 響應時間高不高
- queue 有沒有塞住
- utilization 有沒有滿
- 是哪個 workload 在打

### `28`: 一個 SQL 查詢要 15 秒

這章其實非常好，因為它在提醒你：

> 使用者感受到的 I/O 問題，常常是穿過應用、資料庫、儲存整條鏈後的表現。

所以不是所有慢 SQL 都是 DBA 題。  
它也可能牽涉到：

- index
- schema 設計
- app query pattern
- storage latency

### `29`: Redis 延遲很嚴重

這章同樣在提醒你：

- memory store 不代表永遠快
- persistence、save 策略、blocking command、單執行緒模型，都可能造成延遲

這對 Go 團隊很重要，因為很多服務把 Redis 當「一定快」的黑盒。

### `30~31`: 怎麼找出 I/O bottleneck、怎麼做 I/O 優化

這兩章和前面的 CPU / memory 線一樣，最後都回到套路：

1. 先確認是哪種 I/O 指標異常
2. 再確認是 file system、disk、DB、cache，還是 app 行為
3. 先做低風險、能量測效果的優化

這也是為什麼 `R4` 到這裡其實已經在幫後面的 `I/O model` 鋪路了。  
因為你已經學會：

- 慢不一定在 CPU
- 慢不一定在磁碟
- 慢不一定在 app code

接下來才有資格問：

「那等待本身，究竟是怎麼被安排的？」

## 2. I/O model 到底是什麼

### 觀念

I/O model 處理的核心問題很單純：

> 當程式要讀資料或等網路回應時，等待的這段時間怎麼安排？

R4 的 `C10K 與 C1000K 回顧` 把常見模型列得很清楚：

- blocking I/O
- non-blocking I/O
- I/O multiplexing: `select` / `poll` / `epoll`
- signal-driven I/O
- asynchronous I/O

但這裡要先校正一個很重要的點：

> 「五種 I/O 模型」和「同步 / 非同步 I/O」不是同一條分類軸。

如果分類得更精準，應該先這樣看：

- `Synchronous I/O`
  - blocking I/O
  - non-blocking I/O
  - I/O multiplexing
  - signal-driven I/O（很多教材會把它放這邊，因為真正讀資料仍要你自己做）
- `Asynchronous I/O`
  - POSIX AIO
  - Linux 原生 AIO
  - `io_uring` 這類 completion-based 介面

也就是說：

- `blocking / non-blocking / multiplexing / signal-driven`  
  通常是在講「同步 I/O 的不同等待方式」
- `AIO` 才是在講「真正把 I/O 完成動作交給系統背景執行」

我前一版把五種模型直接平鋪在同一層，作為入門記憶不算完全錯，但如果講嚴謹分類，確實不夠精準。你貼的圖抓到的，就是這個問題。

真正要抓住的是：

> I/O 不只是「讀資料」這一下，而是通常包含「等資料準備好」和「把資料搬給應用程式」兩段。

以 socket `read()` 為例，可以粗略拆成兩步：

1. 等 kernel 收到資料，放進 kernel buffer
2. 把資料從 kernel buffer 複製到 user space buffer

很多 I/O model 的差異，主要就出在：

- 你是怎麼等第 1 步完成的
- 第 2 步是同步做，還是系統幫你做完再通知你

這裡我也特別對齊了一篇整理得不錯的文章：  
`Linux 中的五種 I/O 模型`。它把教學上常見的展開方式列成：

1. blocking I/O
2. non-blocking I/O
3. I/O multiplexing
4. signal-driven I/O
5. asynchronous I/O

這種「五種模型平行展開」很常見，方便初學者記憶；  
但如果你要問分類學上更精準的口徑，應該回到上面那個：

- 先分 `synchronous` / `asynchronous`
- 再看同步 I/O 底下有哪些等待與通知方式

### 白話比喻

想像你是客服：

- blocking I/O: 接到一通電話後就一直抱著電話等，別的客戶先不管
- non-blocking I/O: 你每隔幾秒自己去問一次「好了沒」
- I/O multiplexing: 你把很多客戶先掛在總機，有人真的有事再通知你
- AIO: 工作先丟出去，完成後再通知你回來收結果

另一個更貼近 kernel 的比喻是「收包裹」：

- blocking I/O: 你站在門口一直等快遞，快遞到了再親手把包裹搬進房間
- non-blocking I/O: 你一直自己探頭看快遞到了沒，沒到就先做別的
- I/O multiplexing: 你請管理員幫你盯，哪一戶有快遞到了再叫你下來拿
- AIO: 你連搬包裹都外包，東西進房間後才通知你

### 先分清楚兩組概念

這裡最容易混淆兩組詞：

- `blocking / non-blocking`
- `synchronous / asynchronous`

它們不是完全同一件事。

#### blocking / non-blocking

這組在講：

> 當前這次系統呼叫會不會把你卡住？

- blocking: 沒準備好就先卡住
- non-blocking: 沒準備好就立刻回來，通常回 `EAGAIN` / `EWOULDBLOCK`

#### synchronous / asynchronous

這組在講：

> 資料搬運這件事，是不是還要你自己回來收尾？

- synchronous: 你還是要自己呼叫 `read()` / `recv()` 把資料拿走
- asynchronous: 系統把整件事做完，完成後再通知你

所以很常見的組合其實是：

- blocking + synchronous
- non-blocking + synchronous
- non-blocking + synchronous + multiplexing
- signal-driven + synchronous
- asynchronous I/O

### 再加一個更實戰的切法：`readiness` vs `completion`

如果你是做 Linux 網路服務，還有另一條非常有用的分類軸：

- `readiness-based`
  - `select`
  - `poll`
  - `epoll`
  - signal-driven I/O
- `completion-based`
  - POSIX AIO
  - Linux AIO
  - `io_uring` 的完成事件模型

差別在於：

- readiness: 系統通知你「現在可以做 I/O 了」
- completion: 系統通知你「I/O 已經做完了」

這條軸在實務上往往比「五種模型名稱背出來」更有用。

### 工程現象

高 I/O 服務的時間常常不是花在「做事」，而是花在「等事」：

- 等 client 傳資料
- 等 DB 回應
- 等 upstream API
- 等磁碟或網路

如果每個等待都綁死一個 thread，資源會浪費得非常快。

這也是為什麼高併發 server 的核心優化，常常不是把單次運算變快，而是讓「等待中的連線」不要霸佔太多 thread、記憶體和排程成本。

### 你可以把同步 / 非同步先記成這張表

| 類型 | 子類型 | 等資料時 | 資料就緒後 | 直覺特徵 |
|------|------|------|------|------|
| synchronous I/O | blocking I/O | 呼叫執行緒被卡住 | 同一個呼叫把資料搬回來 | 最直覺，但很佔 thread |
| synchronous I/O | non-blocking I/O | 不會卡住，自己反覆檢查 | 你自己再呼叫讀取 | 容易變 busy polling |
| synchronous I/O | I/O multiplexing | 卡在 `select/poll/epoll` 等事件 | 事件來了後仍要自己 `read()` | 最常見的高併發主流 |
| synchronous I/O | signal-driven I/O | 先註冊訊號 | 收到訊號後再自己讀 | 靠 signal 做 readiness 通知 |
| asynchronous I/O | AIO / completion-based | 整件事丟給系統 | 系統做完再通知 | completion 模式，不只通知 ready |

### 如果你只是要背「五種模型」，可以再看這張平鋪表

| 模型 | 在更精準分類中的位置 | 一句話 |
|------|------|------|
| blocking I/O | synchronous I/O | 呼叫後直接卡住等 |
| non-blocking I/O | synchronous I/O | 呼叫後立刻回來，自己再試 |
| I/O multiplexing | synchronous I/O | 先等通知，再自己讀 |
| signal-driven I/O | 通常歸在 synchronous/readiness | 用 signal 通知 ready，再自己讀 |
| asynchronous I/O | asynchronous I/O | I/O 完成後才通知你 |

### 2.1 Blocking I/O

#### 它怎麼運作

當你呼叫 `read()` 或 `recv()` 時，如果資料還沒到：

- thread 直接睡下去
- kernel 等到資料準備好
- kernel 再把資料複製給你
- 呼叫返回

#### 優點

- 好懂
- 程式流程直線
- 單連線、低併發時夠用

#### 缺點

- 一個 thread 很容易只服務一個等待點
- thread 數一多，記憶體和 context switch 成本就上來

#### junior 最該記住的點

blocking 最大的問題不是「它很慢」，而是「它讓等待成本很高」。

### 2.2 Non-blocking I/O

#### 它怎麼運作

socket 被設成 non-blocking 後，如果資料還沒準備好：

- `read()` 不會睡下去
- 它會很快返回，告訴你現在沒東西可讀

你可以之後再回來試。

#### 優點

- 不會把 thread 卡死
- 給 event-driven 模型打基礎

#### 缺點

- 如果你一直自己重複試，就是 busy polling
- CPU 可能空轉得很兇

#### junior 最該記住的點

non-blocking 不是「魔法加速」，它只是把「等」這件事從睡覺改成你自己要想辦法安排。

### 2.3 I/O Multiplexing

#### 它怎麼運作

你先不要直接對每個 socket 死等，而是先把很多 fd 交給：

- `select`
- `poll`
- `epoll`

讓其中一個多工機制替你等：

- 誰可讀
- 誰可寫
- 誰發生錯誤

等它通知你「這幾個 ready 了」，你再對那些 fd 呼叫 `read()` / `write()`。

#### 關鍵理解

這裡很多人會誤會：  
`select/poll/epoll` 不是直接幫你把資料讀完。  
它們是在告訴你：

> 「現在可以讀了，你可以去讀。」

也就是說，它們多半是 `readiness notification`，不是 `completion notification`。

#### 為什麼這招重要

因為你不需要一個 thread 綁一個 socket。  
你可以用少量 worker 管很多連線，把 thread 留給真的有事件的連線。

### 2.4 Signal-driven I/O

R4 提到這個模型，但實務上你比較少在一般後端服務中把它當主角。  
概念上是：

- 先註冊訊號
- 當 fd ready 時，kernel 發 signal 給你
- 你收到後再自己去處理 I/O

這也是為什麼它雖然名字常被翻成「訊號驅動 I/O」甚至被某些文章放在「非同步」那邊，  
但如果用更嚴格的口徑看，它更像：

- 通知方式是非同步的
- 真正的資料讀取仍是同步收尾的

所以它很常被放在 `synchronous I/O` 裡的 `readiness-based` 子類。

你可以知道它存在，但現階段不用把它當學習主力。

### 2.5 Asynchronous I/O

#### 它和 multiplexing 真正差在哪

multiplexing 是：

- 系統通知你「可以讀了」
- 你自己再去 `read()`

AIO 更接近：

- 你先把 I/O 請求交出去
- 系統連資料搬運都幫你做
- 做完後再通知你

也就是：

- multiplexing 比較像 `ready`
- AIO 比較像 `done`

#### 為什麼大家常把它和 epoll 混在一起

因為兩者都不是最原始的 blocking 模型。  
但它們其實是兩條不同思路：

- `epoll`: readiness-based
- AIO: completion-based

### 2.6 用一句話分辨這五種模型

- blocking I/O: 我呼叫一次，沒好就卡在那裡等
- non-blocking I/O: 我呼叫一次，沒好就立刻回來
- I/O multiplexing: 我先等系統告訴我「哪些 fd 好了」，再自己去讀
- signal-driven I/O: 系統用 signal 跟我說「某個 fd 好了」，我再自己去讀
- asynchronous I/O: 我把整個 I/O 工作交出去，做完才通知我

### 2.7 為什麼 Linux 高併發主流常落在 `non-blocking + epoll`

根據 R4 的 `35_recap_C10K_C1000K.pdf`，C10K 問題的關鍵就在兩件事：

1. 怎麼在少量 thread 內處理很多請求
2. 怎麼節省資源去處理更多連線

`non-blocking + epoll` 剛好很適合這個方向，因為它能做到：

- 少量 worker 監看大量 fd
- 只在有事件時處理
- 避免 thread-per-connection 的高成本

這也是為什麼 `nginx`、很多 event-driven server，甚至 Go runtime 背後的 netpoll 思路，都和這條線很接近。

### 常見誤解

- `non-blocking 一定比較快`  
  不一定。如果只是把 blocking 改成 busy polling，CPU 可能更慘。
- `async 聽起來最強，所以一定最好`  
  不一定。很多 Linux 高併發網路服務的主流仍然是 non-blocking + `epoll`。
- `select/poll/epoll` 已經把資料幫我讀好了  
  不是。大多數情況下它們只是在告訴你「現在可以讀了」。
- `non-blocking = async`  
  不是。non-blocking 只代表這次呼叫不會傻等，並不代表整件 I/O 已經由系統完整代辦。
- `五種 I/O 模型` 和 `同步 / 非同步 I/O` 是同一層分類  
  不是。更精準的說法是：五種模型是常見教學展開；嚴格分類時，前四種多半仍屬於同步 I/O 的不同等待/通知方式，只有 AIO 是真正非同步 I/O。
- `signal-driven I/O` 跟 `multiplexing` 完全不同類  
  目標很像，都是先告訴你「ready 了」，差別主要在通知手段：一個靠 `select/poll/epoll` 等待事件，一個靠 signal 通知。

### Go 實務映射

你平常寫 Go 不會直接自己呼叫 `epoll_wait()`，但這不代表 I/O model 跟你沒關係。  
Go runtime 在 Linux 上本來就有 network poller；官方 runtime source 直接顯示 Linux 版本的 netpoll 會建立 epoll descriptor，並使用 edge-triggered 事件通知處理 fd。

對 Go 工程師來說，這段最實用的理解是：

- goroutine 很輕，但不是拿來無限浪費等待成本的
- `net/http` 幫你包了很多底層細節，但大量 timeout、慢依賴、長連線，仍然會反映成真實系統壓力
- 你不必手寫 epoll，但你要知道自己遇到的是 `ready` 型通知世界，不是「系統自動把所有等待都消失了」

## 3. `select`、`poll`、`epoll` 在解什麼問題

### 觀念

R4 的核心轉折就是這裡。

當連線變很多時，傳統的「一個連線一個 thread」很難撐，於是大家改成：

- socket 設為 non-blocking
- 由一個 I/O 多工機制幫你監看很多 fd
- 誰 ready，再交給 worker 處理

### 最簡版差異

- `select`: 能做，但規模上去後成本高
- `poll`: 比 `select` 彈性好，但仍需要掃描很多 fd
- `epoll`: 讓 kernel 幫你維護 ready 事件，處理大量連線更有優勢

### 白話比喻

- `select` / `poll`: 你每一輪都要拿整份名單，一個一個問「你有事嗎？」
- `epoll`: 誰有事誰舉手，系統把有事的人放進清單，你直接處理那份清單

### R4 裡值得記住的點

`35_recap_C10K_C1000K.pdf` 強調了三件事：

- 高併發伺服器常用 non-blocking I/O
- `select` / `poll` 屬於水平觸發思路
- `epoll` 常見於邊緣觸發思路，效率不會隨 fd 數量線性惡化

### 水平觸發和邊緣觸發

- `Level Triggered`: 只要還沒讀完，系統還會一直提醒你
- `Edge Triggered`: 狀態改變時提醒你一次，之後要自己把資料盡量讀乾淨

### 常見誤解

- `epoll = 更快的函式`  
  不夠精準。它更像是更適合大量 fd 的事件通知機制。
- `用了 epoll 就一定沒事`  
  錯。`epoll` 只是高併發的入場券，不是全部。

### Go 實務映射

Go 的價值不是讓你不用懂這些，而是幫你把這些機制包起來。  
你還是需要知道：

- 大量閒置連線為什麼會吃資源
- 為什麼 timeout 設太大會把 fd 和 goroutine 拖住
- 為什麼慢 upstream 會反向壓垮你的 service

## 4. 平均負載與 context switch 為什麼要先懂

### 觀念

R4 一開始不是先衝 `epoll`，而是先講平均負載和 CPU context switch。這個安排很對，因為很多人連「系統為什麼忙」都還沒搞懂，就急著談高併發調優。

你至少要先有這些直覺：

- 平均負載不是 CPU 使用率的同義詞
- 等 I/O 的程序也可能讓 load 上升
- context switch 太多，本身就是成本

### 白話比喻

一個主管看起來很忙，不代表他真的在產出。  
如果他一直在不同會議室之間來回切換，實際上時間都浪費在轉場。

thread / process 的 context switch 也類似：

- 切換前要保存狀態
- 切換後要恢復狀態
- cache 可能還會失效

### 工程現象

如果你用 thread-per-connection 或大量短生命週期工作模型，可能看到：

- context switch 很高
- CPU 不一定滿，但有效工作比例下降
- latency 變差

### 常見誤解

- `load average 高 = CPU 一定爆了`  
  不一定。也可能有很多 task 在等 I/O。
- `thread 多表示並行能力強`  
  不一定。thread 過多有管理成本，還會帶來排程與切換開銷。

### Go 實務映射

goroutine 比 OS thread 輕很多，但不是免費。  
如果你的服務因為 timeout、重試、慢查詢或 blocked channel 導致 goroutine 大量堆積，問題最後還是會反映到 scheduler、記憶體和延遲上。

## 5. C10K 到 C1000K 的真正意思

### 觀念

`C10K` 討論的是一台機器如何處理一萬個連線。  
R4 點出的真正痛點不是硬體不夠，而是軟體模型撐不住：

- 怎麼在少量 worker 下處理很多請求
- 怎麼節省記憶體和 thread 成本
- 怎麼避免大量 idle connection 把系統拖垮

### R4 的主線

從 `35_recap_C10K_C1000K.pdf` 可以整理出這條演進：

1. blocking 模型太浪費
2. 改成 non-blocking
3. 用 `select` / `poll` / `epoll` 做多路複用
4. 到了百萬連線，還要一起處理 CPU、記憶體、網路和 kernel 限制

### 白話比喻

抓一隻老鼠跟抓一千隻老鼠，不是同一件事。  
單一請求很快，不代表大量同時請求也能撐住。

### 工程現象

到了 `C1000K` 級別，常見瓶頸不只應用程式：

- fd 數量
- 單連線記憶體成本
- socket buffer
- backlog
- NIC 吞吐與 PPS
- LB / firewall / router 能力

### 常見誤解

- `高併發 = 每秒請求量高`  
  不完全一樣。高併發比較偏同時進行中的工作數與連線數。
- `只要把 Web server 換成 nginx 就結束了`  
  不夠。後面還有 DB、cache、MQ、kernel、網路設備。

### Go 實務映射

博彩和電商很容易遇到流量尖峰：

- 熱門賽事開盤
- 秒殺與大促
- WebSocket 長連線
- 即時推播或即時盤口

這些場景都會把「大量連線管理」放大。你需要的不只是會寫 handler，而是知道哪一層可能先倒。

## 6. 網路效能分析要從哪一層開始

### 觀念

R4 的 `36 怎麼評估系統的網路效能` 和 `43/44 網路性能最佳化的幾個思路` 都在提醒一件事：

> 先搞清楚你在測哪一層，否則數字再漂亮也不代表問題找對了。

不同層要看的指標不同：

- Link / routing 層: `BPS`, `PPS`
- Transport 層: TCP / UDP throughput, latency
- Application 層: HTTP latency, RPS, error rate
- Connection 層: concurrent connections, CPS

### 白話比喻

你不能用「高速公路總車流量」去判斷「某家餐廳出餐效率」。  
同樣地，你也不能拿 `iperf3` 的頻寬數字，直接當作 HTTP 服務的真實表現。

### R4 裡給的工具地圖

- `iperf3`, `netperf`: TCP / UDP
- `ab`, `wrk`, `jmeter`: 應用層
- `ss`, `netstat`: 連線數
- `iftop`, `sar`, `/proc/net/dev`: 流量觀測
- `tcpdump`, `wireshark`: 封包檢查
- `ethtool`: 網卡層

### 常見誤解

- `壓測工具能打很高，線上一定也行`  
  錯。壓測通常只覆蓋一部分真實路徑。
- `HTTP 慢就是網路慢`  
  不一定。可能是 app、序列化、DB、TLS、cache miss。

### Go 實務映射

當你看 Go 服務時，至少要分清楚：

- 是 listener 撐不住
- 是 handler 邏輯慢
- 是 DB / Redis 慢
- 是 upstream 慢
- 是 network stack 或 LB 出現限制

## 7. Linux 高併發不是只靠 kernel，還要看應用模型

### 觀念

`43/44 網路性能最佳化的幾個思路` 很值得記，因為它把最佳化層級分得很清楚：

- 應用程式
- socket
- 傳輸層
- 網路層
- 資料連結層
- 跳出 kernel 的方案，例如 `DPDK`、`XDP`

也就是說，順序通常是：

1. 先把應用模型寫對
2. 再看 socket / TCP / kernel
3. 最後才考慮更極端的資料路徑

### 應用程式層最常見的改善點

- I/O 模型選對
- process / worker 模型合理
- 長連線重用，減少 TCP 建立成本
- cache 使用得當
- 協定與序列化成本合理

### 常見誤解

- `性能優化 = sysctl 調參`  
  太片面。很多時候先該改的是 request pattern、timeout、pool、cache。
- `先談 DPDK 比較厲害`  
  對大多數後端團隊來說，先把應用與 kernel 內的基本功練好，效益更高。

### Go 實務映射

Go 團隊最常真的會做的是：

- 調整 `http.Transport`
- 設定 timeout 與 keep-alive
- 改善連線池與重試策略
- 降低單請求內的 blocking dependency
- 加 cache、拆熱點、做限流

不是一開始就去碰 `XDP`。

## 8. 如果你是 Go 後端，這些知識會怎麼出現在工作裡

### 你大概不會天天手寫 epoll

但你會一直遇到它的影子：

- `net/http`
- gRPC
- Redis client
- MySQL driver
- reverse proxy
- WebSocket server

### 你真正會拿這些知識來做什麼

- 讀懂壓測報告，不只看 QPS
- 看 incident 時知道先查哪層
- 知道 goroutine 多不等於免費
- 知道連線多跟 TPS 高不是同一件事
- 能跟 SRE / Infra / DBA 對齊語言

### 很實用的排查順序

當線上服務變慢時，先問：

1. 變慢的是 latency、throughput、還是 error rate？
2. 是全部請求都慢，還是某一類請求慢？
3. CPU、memory、fd、connections 哪個先異常？
4. 是 app 在算，還是在等？
5. 是單機瓶頸，還是共享依賴瓶頸？

## 9. 面試版最短回答

### 什麼是 blocking / non-blocking I/O？

blocking I/O 是呼叫 `read()` 之後，資料沒到就卡住等；non-blocking I/O 則是不讓 thread 卡死，可以先去做別的事，再搭配事件通知機制回來處理。

### `epoll` 在解決什麼問題？

它在解決大量 fd 的事件監聽成本，讓 Linux 可以用更適合大規模連線的方式通知應用程式哪些 socket ready，不需要每一輪都把全部 fd 掃一遍。

### 為什麼 Go 工程師還要懂這些？

因為 Go runtime 雖然幫你包起來了，但高併發時真正出問題的地方，還是會落在連線、timeout、pool、I/O 等待、系統資源和 network stack。你懂底層模型，排查會快很多。

## 10. 這份筆記建議怎麼搭配 R1

這份是底層直覺。  
如果你只看 R4，你會知道系統怎麼慢；但你不一定知道為什麼團隊要在意這些慢。  
R1 會補上另一半：

- 為什麼要先定義 SLI / SLO
- 為什麼監控不能只看 dashboard
- 為什麼容量規劃跟高併發是同一題
- 為什麼 on-call 和 automation 會反過來決定系統品質

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
