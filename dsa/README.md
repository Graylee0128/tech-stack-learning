# Applied Algorithms for Systems

目標：建立 Cloud Platform / SRE / DevSecOps / FinOps 路線需要的演算法判斷力。這裡不再把 Advanced Algorithms 當主線，而是保留對系統工程有實務價值的 applied algorithms。

核心原則：

> 演算法是輔修，不是主戰場。主戰場在 Linux / Networking / Kubernetes / Cloud / SRE / Security / FinOps。

要學的是能幫你理解 sharding、cache、service topology、observability、capacity planning、autoscaling、cost optimization 的算法，而不是追求完整啃完高階理論課。

## 整理原則

- **README 只留這一份**：這裡是唯一入口與學習計畫。
- **先做題與寫筆記，再擴目錄**：沒有實作或內容的資料夾先不要開。
- **技術演進、程式架構不獨立成區**：需要時寫進各 topic 筆記即可。
- **heuristic 是後段模組，不是主線本身**：先把 systems 會碰到的 graph、hashing、sketch、queueing、optimization intuition 補起來。

## 目前入口

| 類型 | 檔案 |
|---|---|
| DSA 大地圖 | [啟發式算法前的 DSA 知識地圖](notes/01_橫縱分析報告/啟發式算法前的DSA知識地圖_橫縱分析報告.md) |
| Heuristic / Solver 大地圖 | [從啟發式搜尋到近似最佳化](notes/01_橫縱分析報告/從啟發式搜尋到近似最佳化_橫縱分析報告.md) |
| 概念橋 | [Exact / Approximation / Heuristic 比較](notes/01_橫縱分析報告/Exact_Approximation_Heuristic_概念比較筆記.md) |
| 建模橋 | [狀態 / 行動 / 評估函數](notes/01_橫縱分析報告/狀態_行動_評估函數_建模筆記.md) |
| Topic 模板 | [算法機制筆記模板](notes/03_算法機制筆記/_TEMPLATE.md) |

## 學習順序

### 1. Systems 最小可用基本功

先攻這些，目標是能讀懂題目、估資料量、判斷 AI 生成解法是否合理。

```text
Complexity
Array / Linked List / Stack / Queue / Hash Table / Heap
Sorting / Binary Search / Prefix Sum / Two Pointers / Sliding Window
Recursion / Backtracking / Pruning
Tree DFS / BFS / DFS / Topological Sort
Greedy
Basic DP
```

這一層不追求刷題量最大化，重點是能看懂複雜度、邊界條件、資料量限制，並且知道什麼時候不用把問題想太複雜。

### 2. Applied Algorithms for Systems 主線

這一段是正式輔修重點。

```text
Graph algorithms
Hashing
Consistent hashing
Bloom filter
Count-Min Sketch
HyperLogLog
MinHash
Amortized analysis
Queueing intuition
Online algorithms 概念
Approximation algorithms 概念
Linear programming 基礎
Constraint optimization
```

對應的 systems 用途：

| 演算法概念 | 實務連結 |
|---|---|
| Graph algorithms | Terraform dependency graph、service topology、network path |
| Hashing | sharding、cache、load balancing |
| Consistent hashing | distributed cache、service routing |
| Bloom filter | cache precheck、deduplication |
| Count-Min Sketch | heavy hitter detection、observability |
| HyperLogLog | unique user / high cardinality estimation |
| Amortized analysis | batching、compaction、buffer flush、autoscaling |
| Online algorithms | autoscaling、job scheduling、spot instance decision |
| Approximation | placement、cost optimization |
| Linear programming | FinOps、capacity planning、resource allocation |

### 3. 搜尋最佳化

這一段處理 so-called「技巧」：它們不是新的資料結構，而是讓暴力搜尋變得可控。

```text
Pruning
Branch and Bound
Memoization
Meet-in-the-middle
Constraint Propagation
```

學這組時要分清楚：

- **Exact pruning**：剪掉不可能成為答案的分支，不改變正確性。
- **Heuristic pruning**：為了速度放棄某些分支，可能不保證最佳解。

### 4. 通往 heuristic 的橋

基本功不是為了背模板，而是為了能把問題拆成：

```text
state + action + objective + constraints
```

這一段先讀：

- [Exact / Approximation / Heuristic 比較](notes/01_橫縱分析報告/Exact_Approximation_Heuristic_概念比較筆記.md)
- [狀態 / 行動 / 評估函數](notes/01_橫縱分析報告/狀態_行動_評估函數_建模筆記.md)

### 5. Heuristic / Approximation / Solver 模組

等基本功有手感後，再開始下面這組：

```text
Baseline 思維
A* / Weighted A* / Beam Search
Hill Climbing / Random Restart / 2-opt / Neighborhood Design
Simulated Annealing
Monte Carlo Simulation / Randomized Algorithms
NP-hard Recognition
Approximation Algorithms
OR-Tools Routing
```

近似算法是獨立 topic，不等於 heuristic。它的重點是「不保證最佳，但有可證明的誤差上界」，例如 Set Cover greedy approximation、Vertex Cover 2-approx、Metric TSP approximation。

GA、ACO、MCTS、Network Flow、Segment Tree 這些先不要搶主線進度。它們很有價值，但應該由具體題目需求觸發。

### 暫不投入

以下 topic 暫時不放入近期主線：

```text
van Emde Boas tree
fusion tree
semidefinite programming
computational geometry
fast exponential algorithms
```

不是它們沒價值，而是對目前 Cloud Platform / SRE / DevSecOps / FinOps 的短期 ROI 不高。

## Topic 工作流

每攻一個 topic：

1. 從 [算法機制筆記模板](notes/03_算法機制筆記/_TEMPLATE.md) 複製一份到 `notes/03_算法機制筆記/`。
2. 在 `exercises/<topic>/` 放實作、測試與題目紀錄。
3. 先做 3 題基礎題，再做 2 題變形題。
4. 隔 7 天不看答案重寫至少 1 題，結果記在 topic 筆記或 `logs/`。

建議命名：

```text
notes/03_算法機制筆記/01_Complexity_研究筆記.md
exercises/01_complexity/problem_001.go
exercises/01_complexity/problem_001_test.go
logs/2026-05-06_進度.md
```

## 實驗主軸

不要每個演算法都孤立學。用固定題型橫向比較，才看得出差異。

| 題型 | 對照算法 |
|---|---|
| Grid Pathfinding | BFS / Dijkstra / A* / Weighted A* |
| Sorting / Top-K | quick sort / merge sort / heap top-k |
| 基本面試題 | binary search / two pointers / sliding window / prefix sum / hash |
| TSP | nearest neighbor / 2-opt / simulated annealing |
| Set Cover | brute force 小樣本 / greedy approximation / heuristic |
| Vertex Cover | exact 小樣本 / 2-approx |
| VRP / 排班 | handwritten heuristic / OR-Tools |

實驗紀錄至少包含：

```text
資料規模 | random seed | 參數設定
best / average / worst | runtime
是否保證最佳解 | 與 baseline 的 gap
```

## 完成標準

一個 topic 暫時算完成，要滿足：

- 能用自己的話說出它解決什麼瓶頸。
- 能估時間與空間複雜度。
- 能從零寫出 Go 版核心模板。
- 能做 3 題基礎題、2 題變形題。
- 隔 7 天後能不看答案重寫至少 1 題。
- 能判斷 AI 生成解法的複雜度與邊界條件是否合理。

heuristic / solver 額外要求：

- 能把問題寫成 `state + action + objective + constraints`。
- 能說清楚是否保證最佳解。
- 能用同一題比較至少 2 種算法。
- 能建立 exact / greedy / brute-force 小樣本 baseline。

## 目錄結構

```text
dsa/
  README.md
  notes/
    01_橫縱分析報告/        # 大地圖與概念橋
    03_算法機制筆記/        # 單一 topic 深入筆記
    05_系統觀念筆記/        # 跨 topic 的決策表與觀念整合
  exercises/                # 按 topic 建立實作與測試
  logs/                     # 學習日誌與 7 天回測
```

## 主要教材

- `algorithmzuo/algorithm-journey`
- `cp-algorithms`
- `OI Wiki`
- `MIT 6.006 / 6.046`
- `Skiena Algorithm Design Manual`
- `USACO Guide`
- `CSES Problem Set`
- OR-Tools docs

實作語言：Go 為主；OR-Tools / CP-SAT 可用 Python。Java/C++ 教材只吸收思想與模板結構。
