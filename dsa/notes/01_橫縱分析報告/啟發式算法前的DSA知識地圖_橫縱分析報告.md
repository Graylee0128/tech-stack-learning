# 啟發式算法前的 DSA 知識地圖（橫縱分析報告）

> 研究時間：2026-05-06 | 所屬領域：DSA / Algorithmic Foundations | 研究對象類型：技術知識地圖
> 報告 1 主文。範圍鎖定：heuristic 之前的 DSA。heuristic search、local search、近似最佳化與 solver 由報告 2 處理。

## 一句話定義

啟發式算法前的 DSA 知識地圖，研究的是：在進入 heuristic、approximation、solver 之前，一個工程師至少要具備哪些 exact algorithm、資料結構、複雜度與建模能力，才不會把「本來能精確解的問題」誤判成「只能靠直覺亂試」。

這份報告不是要把所有 DSA 都塞進學習計畫。

它做的是取捨。

DSA 的宇宙太大，從 array 到 suffix automaton，從 BFS 到 min-cost max-flow，從 binary search 到 heavy-light decomposition，都可以說重要。但如果目標是 Senior SE / AI 時代的判斷力，學習順序不能照百科全書排。真正的問題是：哪些東西是理解 heuristic 前一定要有的地基？哪些東西是競賽支線，值得尊重，但不該搶主線？哪些東西是 AI 會生成，卻需要你能讀懂與驗證的核心？

這份報告的答案很直接：

> heuristic 之前，先補「複雜度感、基本資料結構、搜尋、圖、貪心、DP、剪枝與建模」；沒有這些，後面的最佳化技術會變成名詞遊戲。

## 為什麼先做這份，再做報告 2

報告 2 談的是「不能硬求最佳解之後怎麼辦」。但在那之前，必須先有能力判斷一件事：

這題真的不能硬求嗎？

很多工程錯誤都發生在這裡。明明是 shortest path，卻用手寫 heuristic 亂調權重。明明 sliding window 可以線性解，卻暴力枚舉再剪枝。明明可以用 heap 做 top-k，卻排序整包資料。明明 N 很小，直接 bitmask DP 就能拿 exact baseline，卻先做一個無法驗證的 random search。

所以報告 1 的任務不是「成為競賽選手」。它的任務更務實：

- 看到資料量，能估大概能不能跑
- 看到題型，能辨認常見 exact 解法
- 看到 AI 生成程式，能檢查複雜度與邊界
- 看到最佳化問題，能先建 baseline
- 走進 heuristic 前，知道自己到底放棄了什麼

沒有報告 1，報告 2 會太飄。

## 縱軸：DSA 從計算技巧到工程判斷力的演進

### 1950s-60s：演算法開始變成可分析的對象

早期程式設計的世界，演算法還沒有今天這種課本化的秩序。人們當然會寫排序、搜尋、路徑、表格處理，但更像是在特定機器與特定任務裡累積技巧。

1950s 到 1960s，這件事開始變。Dijkstra 1959 年的 shortest path 論文，把圖上的最短路問題寫成可以清楚描述、清楚分析的程序。Bellman 的 Dynamic Programming 則把多階段決策問題變成一種遞推語言：把大問題拆成子問題，保存中間結果，避免重複計算。

Knuth 從 1968 年開始出版 *The Art of Computer Programming*，也代表一個時代訊號：程式不再只是能跑就好，演算法、資料結構、分析方法本身值得被系統整理。

這一段對今天的學習意義是：複雜度不是面試裝飾，而是工程語言。

你說一個解法是 `O(n log n)`、`O(n^2)`、`O(2^n)`，其實是在回答「這個方法能不能在資料規模下活下來」。heuristic 的第一個前置能力，就是不要對規模失去感覺。

### 1970s：圖、DP、貪心與 NP-hard 邊界同時成形

1970s 是演算法世界開始長出邊界感的年代。

一邊是大量 exact algorithm 技術逐漸成熟：圖論、最短路、最小生成樹、matching、flow、dynamic programming、greedy proof。另一邊是 complexity theory 把人拉回現實：不是所有看起來像「找最佳」的問題都能有漂亮的多項式解。

Karp 1972 年整理的 NP-complete 問題尤其關鍵。它讓「這題很難」不再只是感覺，而是可以放進一個理論框架裡討論。

#### NP 相關概念：不是背分類，而是建立可解性邊界

在這份報告裡，NP 相關概念不需要先學成 complexity theory 的完整證明系統，而是先當成工程雷達：

- `P`：可以在多項式時間內求出答案。
- `NP`：給你一個候選答案，可以在多項式時間內驗證。
- `NP-complete`：NP 裡最有代表性的困難 decision problems；如果其中一個能被多項式時間解掉，整個 NP 都會被拉動。
- `NP-hard`：至少跟 NP-complete 一樣難，不一定本身是 decision problem；很多最佳化版本會落在這裡。

所以 `NP-hard` 的學習意義不是「這題不用想了」，而是提醒你：先找 exact 子結構、特殊限制、資料規模與 baseline；確定一般情況真的撞到邊界後，再把問題交給報告 2 的 approximation、heuristic 或 solver。

這裡有一個很重要的學習順序：

先學會哪些問題能 exact 解，再學哪些問題可能不能。

如果反過來，一開始就沉迷 NP-hard、heuristic、metaheuristic，很容易得到一種錯覺：最佳化問題都是玄學。但其實很多真實問題有乾淨的 exact 子結構。你可能只需要排序、二分、prefix sum、graph traversal、Dijkstra、DP，甚至把問題拆成幾個 exact 子問題，就能解掉 80%。

### 1980s-90s：競賽演算法把技巧打磨成題型語言

1980s 到 1990s，演算法教育和競賽文化開始把 DSA 變成一套高密度題型語言。

ICPC 的根可追溯到 1970 年 Texas A&M 的程式競賽，1977 年進入多層級比賽形式；IOI 1989 年開始，讓高中生也進入以演算法為核心的競賽體系。這些競賽做了一件很厲害的事：它們把演算法壓縮成可訓練、可測量、可比較的能力。

於是很多今天熟悉的題型感就固定下來：

- two pointers 看單調性
- sliding window 看區間可維護性
- prefix sum 看重複區間查詢
- binary search 看答案空間
- DFS / BFS 看狀態擴展
- topological sort 看依賴
- greedy 看交換論證或局部選擇
- DP 看狀態與轉移

競賽世界的貢獻很大，但它也有副作用。競賽喜歡短時間內的高技巧密度，會自然偏向「漂亮招式」與「邊界極端」。工程世界則更在乎可讀性、可維護性、資料分布、失敗模式。

所以本學習計畫吸收競賽的題型語言，但不照競賽完整路線走。

Segment Tree、HLD、SCC、suffix array、advanced flow 都可以很重要，但它們不必成為 heuristic 前置主線。除非具體題目需要，否則先放支線。

### 2000s-2010s：面試平台把 DSA 工業化

2000s 到 2010s，DSA 被另一股力量重塑：求職面試。

CLRS 在大學和專業領域裡成為標準參考，LeetCode 這類平台則把演算法題變成大規模、可刷題、可排名、可分類的面試準備系統。這件事有好有壞。

好處是，常見題型被整理得很清楚。binary search、hash map、two pointers、sliding window、heap、DFS/BFS、backtracking、basic DP，這些技能變成軟體工程師的共享語言。即使你不喜歡刷題，它也讓很多人第一次認真建立複雜度感。

壞處是，面試平台容易把 DSA 學成「看到題目套模板」。模板有用，但 heuristic 前置需要的不是條件反射，而是建模能力。你要知道為什麼這題能 sliding window，為什麼那題不能；為什麼這個 DP state 足夠，為什麼另一個 state 會爆；為什麼 greedy 在這題能證，在那題只是猜。

面試 DSA 是入口，不是終點。

### 2020s：AI 生成解法時代，「能讀」比「能背」更重要

到了 2020s，DSA 的角色又變了。

LLM 可以很快寫出一個看似完整的解法。它會生成程式、測試、註解，甚至講一段複雜度分析。這讓「從零背出模板」的重要性下降，但讓「讀懂與驗證」的重要性上升。

AI 生成解法最常見的問題不是語法，而是判斷：

- 把 `O(n^2)` 說成 `O(n)`
- 忽略空陣列、重複值、負數、overflow
- 用 greedy 解其實需要 DP 的題
- 用 DFS 爆棧或重複搜尋
- 對 graph cycle、unreachable state、duplicate state 沒處理
- 對 NP-hard 問題直接給出看似 polynomial 的「最佳解」

這些錯誤需要 DSA 地基才能抓出來。

AI 時代不是不用學 DSA，而是不用把 DSA 學成手工藝崇拜。真正該學的是：能不能快速判斷生成解法屬於哪一類，複雜度是否符合資料規模，邊界是否完整，能不能用小樣本暴力解驗它。

這正是報告 1 的定位。

## 橫軸：當下四個世界如何看 DSA

同一個 DSA topic，在不同場域裡價值完全不同。

| 世界 | 重視什麼 | 不重視什麼 | 對「heuristic 前置」的意義 |
|---|---|---|---|
| 競賽（CP） | 題型密度、模板熟練、極端邊界、證明 | 工程可讀性、團隊維護 | 提供深度，但只取主線需要的部分 |
| 求職面試 | 高頻題、模式識別、短時間正確實作 | 完整理論、長期維護 | 是最小可用 DSA 的主要來源 |
| AI / ML 系統 | 建模、搜尋空間、資料規模、近似容忍 | 手寫冷門模板 | 直通 heuristic、search、optimization |
| 工程 / Systems | 時空成本、資料結構選型、可維運、可觀測 | 炫技、過度抽象 | 決定哪些 topic 真值得投入 |

這張表的重點不是分高下，而是分語境。

競賽會把 Segment Tree 看得很重要，面試通常不會。工程會很在意 hash map 的記憶體與碰撞風險，競賽常常只在意能不能 AC。AI 系統會關心 state space 與 pruning，面試題可能只要求你寫出 basic DFS。每個世界都對，但每個世界都不完整。

這份學習地圖要服務的是 Senior SE / AI 時代，所以取法如下：

- 從面試世界拿最小可用基本功
- 從競賽世界拿嚴謹的題型與複雜度感
- 從工程世界拿可維運與資料規模判斷
- 從 AI / ML 世界拿建模與搜尋空間意識

四個世界交叉後，才知道哪些是主線。

## 交叉分析：哪些 DSA 是 heuristic 前的真正地基

### 第一層：複雜度與資料規模感

這是所有東西的地板。

如果你不能看到 `n = 10^5` 立刻排除 `O(n^2)`，不能看到 `n = 20` 意識到 bitmask DP 可能可行，不能看到 `n = 50` 知道 `2^n` 大概完了，那你後面很容易亂選方法。

最低要求：

- 會估 `O(1)`、`O(log n)`、`O(n)`、`O(n log n)`、`O(n^2)`、`O(2^n)`、`O(n!)`
- 知道時間複雜度和常數、記憶體、資料分布會一起影響工程結果
- 能用 brute force 小樣本當 oracle

這一層是讀 AI 生成解法的第一道防線。

### 第二層：基本資料結構

資料結構不是背 API，而是理解「操作成本」。

| Topic | 主要能力 | 為什麼是前置 |
|---|---|---|
| Array / Slice | 連續記憶體、index、排序前處理 | 幾乎所有題目的資料底座 |
| Linked List | 指標操作、局部插入刪除 | 理解結構性修改，但工程中少用 |
| Stack / Queue | LIFO / FIFO、單調結構前置 | DFS、BFS、括號、單調棧 |
| Hash Table | `O(1)` average lookup、去重、計數 | two-sum、頻率、visited set |
| Heap | 動態最小值 / 最大值 | top-k、Dijkstra、priority scheduling |

這些東西看起來基礎，但 heuristic 後面也一直用。A* 要 priority queue，搜尋要 visited set，local search 要快速計算 delta，solver 前的資料整理也離不開 hash 與 array。

### 第三層：線性題型工具箱

這一層是面試高頻，但不要小看它。

| Topic | 核心直覺 | 典型訊號 |
|---|---|---|
| Sorting | 先建立順序，降低決策難度 | 比大小、區間、去重、合併 |
| Binary Search | 在單調答案空間中找邊界 | 「最小可行值」「最大滿足值」 |
| Prefix Sum | 區間查詢轉成差分 | subarray sum、range query |
| Two Pointers | 利用排序或單調移動 | pair、去重、左右夾逼 |
| Sliding Window | 維護連續區間狀態 | longest / shortest subarray |

它們的共同點是：把暴力枚舉降維。

這正是 heuristic 前置的精神。先問能不能用結構把搜尋空間砍掉，而不是一看到組合爆炸就說要 heuristic。

### 第四層：遞迴、回溯、剪枝

這一層是走向 heuristic 的第一座橋。

Backtracking 讓你第一次把問題看成 state space：

```text
state: 目前已做的選擇
action: 下一步可選什麼
constraint: 哪些選擇非法
goal: 什麼時候完成
```

剪枝則分成兩種：

- exact pruning：剪掉不可能成為答案的分支，不改變正確性
- heuristic pruning：為了速度放棄某些可能分支，可能失去最佳性

報告 1 只要求先掌握 exact pruning。你要能寫 N-Queens、subset、permutation、combination、basic branch and bound，知道如何用 constraint 提早失敗。

一旦你理解 state/action/constraint，報告 2 的 A*、local search、SA、MCTS 才有語言可接。

### 第五層：圖與樹

圖是 heuristic 前最重要的 exact 世界之一。

| Topic | 解決什麼 | 為什麼重要 |
|---|---|---|
| Tree DFS | 層級結構、子樹聚合 | 遞迴建模與 DP 前置 |
| BFS | 無權最短路、層序擴展 | A* / heuristic search 的對照基準 |
| DFS | 可達性、連通、狀態探索 | backtracking 與 graph traversal 基礎 |
| Topological Sort | DAG 依賴順序 | scheduling / dependency 建模前置 |
| Dijkstra | 非負權最短路 | A* 的 exact baseline |

這裡的關鍵不是把所有圖論都學完，而是知道圖如何表示 state transition。

很多最佳化問題表面不是圖，建模後就是圖。任務依賴是 DAG，迷宮是 grid graph，狀態轉移是 implicit graph，搜尋樹是 graph 的特殊展開。

圖學不好，heuristic search 會直接失根。

### 第六層：Greedy

Greedy 是最容易被 AI 和人類一起濫用的東西。

它的誘惑很大：每一步做看起來最好的選擇，程式短，跑得快，解釋也順。但 greedy 的問題從來不是會不會寫，而是能不能證。

最低要求不是掌握所有 greedy 題，而是學會三種判斷：

- 是否有 exchange argument
- 是否有 matroid / interval / ordering 這類可貪心結構
- 如果不能證，它只是 heuristic baseline，不是 exact algorithm

這句話非常重要：同一段 greedy 程式，在不同問題裡身份不同。

在 activity selection，它可能是 exact。在 Set Cover，它是 approximation。在 TSP nearest neighbor，它只是 heuristic。你要能分辨。

### 第七層：Basic DP

DP 是 heuristic 前最重要的建模訓練。

DP 逼你回答：

- state 是什麼？
- transition 從哪裡來？
- base case 是什麼？
- 狀態數多少？
- 每個狀態轉移成本多少？
- 是否能壓縮空間？

這些問題和報告 2 的建模語言完全相通。DP 是 exact 的，但它訓練的是「把問題拆成狀態」的能力。

最低要求：

- 1D / 2D DP
- Knapsack
- LIS
- Grid DP
- Interval DP 入門
- Bitmask DP 小規模

不需要一開始衝高階 DP。重點是能把題目轉成狀態與轉移，並估狀態空間。

## Topic 取捨：主線、橋、支線

### 主線：必須先補的最小可用基本功

```text
Complexity
Array / Linked List / Stack / Queue / Hash Table / Heap
Sorting / Binary Search / Prefix Sum / Two Pointers / Sliding Window
Recursion / Backtracking / Exact Pruning
Tree DFS / BFS / DFS / Topological Sort / Dijkstra
Greedy
Basic DP
```

這些是 README 裡的第一段主線。它們共同構成「能讀懂大多數 AI 生成解法，也能做小樣本 baseline」的最低能力。

### 橋：通往 heuristic 的搜尋最佳化

```text
Branch and Bound
Memoization
Meet-in-the-middle
Constraint Propagation
State / Action / Objective / Constraints
```

這些不是完全獨立的新世界，而是從 exact search 走向 heuristic / solver 的橋。

Branch and Bound 讓你理解 bound 如何剪掉不可能更好的分支。Memoization 讓你看到重複 state 可以合併。Meet-in-the-middle 讓你理解搜尋空間可以從 `2^n` 拆成兩個 `2^(n/2)`。Constraint Propagation 則是 solver 世界的前奏。

### 支線：有價值，但不搶主線

```text
Segment Tree
Fenwick Tree
Union Find advanced variants
SCC
Network Flow
HLD
Suffix Array / Suffix Automaton
Computational Geometry
```

這些不是不重要。

它們只是跟「走進 heuristic 前的最小地基」不是同一件事。Network Flow 尤其要小心：它是很多問題的 exact 解法，非常有價值，但不是 heuristic 進階。等具體題目需要，再拉進 topic 筆記。

## 橫縱交匯洞察

### 洞察 1：DSA 的主線不是難度排序，而是判斷力排序

傳統學習很容易照難度排：array 簡單，DP 困難，graph 更困難，flow 超困難。

但 Senior SE / AI 時代更應該照判斷力排。

你先需要 complexity，因為它決定能不能跑。你需要 hash、heap、sorting，因為它們是大量工程問題的成本工具。你需要 BFS / Dijkstra，因為它們是 pathfinding 與 A* 的 exact baseline。你需要 backtracking / pruning，因為它們讓你理解 state space。你需要 greedy / DP，因為它們訓練你分辨「局部選擇」和「完整狀態」。

這條順序不是學術最完整，但最符合現在的目標。

### 洞察 2：競賽提供深度，面試提供入口，工程決定取捨

競賽很適合訓練邊界與技巧，但如果全盤照收，學習計畫會失焦。面試題很適合建立基本盤，但如果只停在面試，會缺少證明與建模。工程場景會逼你回到資料規模、維護成本、可解釋性與失敗模式。

所以本地圖的策略是混合：

- 用面試高頻題建立最小肌肉
- 用競賽思維補複雜度與反例
- 用工程問題決定是否深入高階 topic
- 用 AI 生成解法當檢查對象，訓練閱讀與驗證

這比單純「刷 500 題」更接近真正可用的能力。

### 洞察 3：heuristic 的入口不是 GA / SA，而是 backtracking 與 DP

很多人一聽 heuristic，就想到 Genetic Algorithm、Simulated Annealing、Ant Colony。

但真正的入口更樸素：backtracking 和 DP。

Backtracking 教你 state/action/constraint。DP 教你 state compression 與 overlapping subproblems。Graph search 教你 frontier、visited、cost。Greedy 教你 evaluation function 的危險與力量。

這些東西才是 heuristic 的語法。

如果跳過它們直接學 SA，你會知道 temperature，但不知道 state 怎麼設。如果直接學 GA，你會知道 mutation，但不知道 chromosome 是否保留問題結構。如果直接學 MCTS，你會知道 rollout，但不知道 state transition 是否可控。

先學 DSA，是為了讓 heuristic 不變成儀式。

### 洞察 4：AI 時代的 DSA 完成標準要改

以前學 DSA，完成標準常常是「我能不能默寫模板」。

現在更好的標準是：

- 能不能判斷 AI 生成解法的類別
- 能不能指出複雜度錯誤
- 能不能補出 edge cases
- 能不能用 brute force 小樣本驗證
- 能不能把題目改寫成 `state + action + objective + constraints`
- 能不能說出為什麼不用更重的演算法

手寫仍然重要，因為不寫就沒有細節感。但手寫不是終點。讀懂、驗證、取捨，才是現在更稀缺的能力。

## 完成標準：報告 1 到什麼程度算過關

一個 topic 暫時算完成，至少要滿足：

- 能用自己的話說出它解決什麼瓶頸
- 能估時間與空間複雜度
- 能從零寫出 Go 版核心模板
- 能做 3 題基礎題、2 題變形題
- 隔 7 天後能不看答案重寫至少 1 題
- 能判斷 AI 生成解法的複雜度與邊界條件是否合理

報告 1 額外要求：

- 每個搜尋 / DP 題都要能說出 state
- 每個 greedy 題都要能說出是 exact、approximation 還是 heuristic baseline
- 每個 graph 題都要能說出節點、邊、cost、visited 的語意
- 每個 topic 至少留一個 brute force 小樣本驗證方式

## 建議學習路線

### 第一輪：建立成本感

- Complexity
- Array / Hash Table / Stack / Queue
- Sorting
- Binary Search

目標：看到資料規模就能排除明顯錯解。

### 第二輪：建立線性掃描與區間直覺

- Prefix Sum
- Two Pointers
- Sliding Window
- Heap / Top-K

目標：把常見 `O(n^2)` 暴力降到 `O(n)` 或 `O(n log n)`。

### 第三輪：建立搜尋空間語言

- Recursion
- Backtracking
- Exact Pruning
- BFS / DFS
- Tree DFS

目標：能把問題拆成 state/action/constraint。

### 第四輪：建立圖與依賴模型

- Topological Sort
- Dijkstra
- Basic graph representation

目標：為 A*、solver、scheduling 類問題打底。

### 第五輪：建立最佳化前置能力

- Greedy
- Basic DP
- Memoization
- Meet-in-the-middle
- Branch and Bound 入門

目標：知道哪些問題可以 exact，哪些只能做 baseline，哪些準備交給報告 2。

## 結論

啟發式算法前的 DSA，不是為了把你訓練成競賽選手，也不是為了讓你在 AI 時代繼續手刻所有模板。

它的目的更實際：

> 在放棄最佳解之前，你要先知道自己有沒有資格放棄。

如果 exact 能解，就不要用 heuristic。  
如果 greedy 能證，就不要把它說成「經驗上可行」。  
如果 DP 能建 baseline，就不要空口說 heuristic 很好。  
如果資料規模一看就爆，就不要假裝多加幾個剪枝能救。

報告 1 的終點，就是報告 2 的起點：當你已經知道哪些 exact 工具該試、哪些 baseline 該建、哪些問題真的碰到 NP-hard 或工程限制時，再進入 heuristic、approximation、solver 的世界。

## 資訊來源

- E. W. Dijkstra, “A Note on Two Problems in Connexion with Graphs,” Numerische Mathematik, 1959. https://doi.org/10.1007/BF01386390
- Richard Bellman, *Dynamic Programming*, Princeton University Press, 1957. https://openlibrary.org/books/OL6220631M/Dynamic_programming.
- Donald E. Knuth, *The Art of Computer Programming*, Volume 1 first published in 1968. https://www-cs-faculty.stanford.edu/~knuth/taocp.html
- Richard M. Karp, “Reducibility among Combinatorial Problems,” 1972. https://doi.org/10.1007/978-1-4684-2001-2_9
- MIT Press, *Introduction to Algorithms*, first edition, 1990. https://mitpress.mit.edu/9780262031417/introduction-to-algorithms/
- MIT Press, *Introduction to Algorithms*, fourth edition, 2022. https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/
- ICPC Foundation, ICPC history and scope. https://icpc.foundation/
- International Olympiad in Informatics official site, IOI history. https://ioinformatics.org/index.shtml
- LeetCode company profile, interview preparation platform context. https://www.crunchbase.com/organization/leetcode

## 方法論說明

本報告依照 hv-analysis 橫縱分析法整理：縱軸追蹤 DSA 從早期演算法分析、圖與 DP、競賽文化、面試平台到 AI 生成解法時代的演進；橫軸把同一批 DSA 能力放進競賽、面試、AI / ML 系統、工程四個當下場域對比；最後在兩軸交會處抽出 heuristic 前置學習的取捨原則。
