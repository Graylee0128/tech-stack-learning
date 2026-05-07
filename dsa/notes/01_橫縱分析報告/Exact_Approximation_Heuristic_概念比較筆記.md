# Exact / Approximation / Heuristic 概念比較筆記

> 橋的子筆記之一。釐清三種演算法世界的本質差異，避免之後走進 heuristic、approximation、solver 時混淆。
> 這份筆記要回答的不是「哪個演算法比較強」，而是「我現在犧牲了哪一種保證，換到了哪一種可用性」。

## 一句話定義

| 類別 | 一句話 |
|---|---|
| **Exact** | 保證找到最優解或正確答案，且能分析時間 / 空間複雜度 |
| **Approximation** | 不保證最優，但有可證明的誤差上界，例如 `<= 2 * OPT` |
| **Heuristic** | 不保證最優、也不保證誤差上界，但實務上可能夠好、夠快 |

最短版：

```text
Exact:        我保證對
Approximation:我不保證最好，但保證不會差太遠
Heuristic:    我不保證，但我會用 baseline 和實驗證明它值得
```

這三類不是演算法名字的分類，而是**保證的分類**。同一個題目可以同時有 exact、approximation、heuristic 三種解法；同一個演算法也可能因條件不同，保證跟著改變。

## 核心差異

| 維度 | Exact | Approximation | Heuristic |
|---|---|---|---|
| 最優保證 | 有 | 沒有 | 沒有 |
| 正確性保證 | 有 | 通常保證可行 | 通常只靠設計與實驗 |
| 誤差上界 | `0`，因為就是最佳 | 有，例如 `2-approx`、`O(log n)` | 通常沒有 |
| 複雜度分析 | 必須清楚 | 必須清楚 | 仍要估，但常看實驗分布 |
| 典型代表 | BFS、Dijkstra、DP、Backtracking、Branch and Bound | Vertex Cover 2-approx、Set Cover greedy、Metric TSP Christofides | A* 的 aggressive 版本、2-opt、SA、GA、Tabu、Beam Search |
| 適用問題 | P；或 NP-hard 的小規模 instance | NP-hard 但有可接受近似比 | NP-hard、即時系統、問題特殊且工具不合適 |
| 對外承諾 | 「這是最佳 / 正確答案」 | 「最壞不會比最佳差超過某比例」 | 「在測試分布上比 baseline 好」 |
| 工程心態 | 對就是對 | 夠近，而且我能證明 | 先可用，再用實驗守住品質 |

Approximation 和 Heuristic 最容易混在一起。它們都可能回傳非最佳解，但 Approximation 的重點是**證明**；Heuristic 的重點是**實驗與可交付**。

## 何時用哪一種

優先順序可以這樣記：

```text
1. 能 exact，就 exact。
2. 不能 exact，但有可接受近似比，就 approximation。
3. 標準工程最佳化問題，先試 solver。
4. 以上都不合適，再手寫 heuristic。
```

更具體地說：

- 問題在 **P** 內，資料量合理 → 直接 Exact。
- 問題是 NP-hard，但 `n` 很小 → Exact / brute force / DP / branch and bound 仍可能可用。
- 問題是 NP-hard，且有成熟近似算法 → 如果需要對上層交代品質，優先 Approximation。
- 問題是 routing / scheduling / assignment / packing → 優先試 OR-Tools / CP-SAT / MIP solver。
- 問題太大、太特殊、即時性要求高，或 approximation / solver 不合適 → Heuristic。
- 即時性要求遠大於最佳性，例如遊戲 AI、線上推薦、快速排程修補 → Heuristic。

## 三類方法和建模的關係

建模筆記裡的四元組是：

```text
state + action + objective + constraints
```

三類方法看的是同一個模型，但問的問題不同。

| 類別 | 對模型的提問 |
|---|---|
| Exact | 能不能完整搜尋，或用 DP / graph / greedy 性質壓縮搜尋，仍保證最佳？ |
| Approximation | 能不能用某個結構證明回傳解和 `OPT` 的距離有上界？ |
| Heuristic | 能不能設計好的 state representation、neighbor、evaluation，讓解品質在實驗上穩定？ |
| Solver | 能不能把 variables、constraints、objective 宣告清楚，交給工具在 time limit 內求解？ |

Solver 不在標題三分法裡，但工程上一定要放進決策流程。它可能內部混合 exact search、relaxation、cut、constraint propagation 與 heuristic；你要看的是 solver 回傳的 status，而不是想像它永遠給神諭答案。

## 經典邊界例題

### 1. Shortest Path

| 解法 | 類別 | 保證 | 適用 |
|---|---|---|---|
| BFS | Exact | 無權圖最短路 | 邊權全部相同 |
| Dijkstra | Exact | 非負權重最短路 | 一般非負權圖 |
| Bellman-Ford | Exact | 可處理負權，能偵測負環 | 節點 / 邊不太大 |
| A* with admissible `h` | Exact with heuristic guidance | 保證最短 | 有好 heuristic，例如 grid map |
| Weighted A* | Heuristic | 通常不保證最短 | 想用最佳性換速度 |

這題提醒：`heuristic` 這個字不一定代表「沒有保證」。A* 用 heuristic function 導引搜尋，但只要 `h` 不高估，仍可保證最佳。

### 2. TSP

| 解法 | 類別 | 保證 | 適用 |
|---|---|---|---|
| Brute force | Exact | 保證最佳 | 很小 `n` |
| Held-Karp DP | Exact | 保證最佳，`O(n^2 * 2^n)` | 小到中小規模 |
| Branch and Bound | Exact | 剪枝正確時保證最佳 | bound 強、instance 不太壞 |
| Christofides（metric TSP） | Approximation | `<= 1.5 * OPT`，需滿足 metric 條件 | metric TSP |
| Nearest Neighbor | Heuristic | 無近似保證 | 快速 baseline |
| 2-opt / SA / GA | Heuristic | 無一般最佳保證 | 大規模、實務求好解 |
| OR-Tools Routing | Solver | 視 status / time limit 而定 | VRP、TSP 工程變體 |

TSP 是這份筆記的核心練習題：同一個問題，三個世界都能講，而且每個世界犧牲的東西不同。

### 3. Set Cover

| 解法 | 類別 | 保證 | 適用 |
|---|---|---|---|
| 枚舉所有 subset | Exact | 保證最小集合數 / 最低成本 | 小樣本 baseline |
| Integer Programming / Solver | Solver / Exact or feasible | 視 solver status | 工程建模、可設 time limit |
| Greedy 每次選覆蓋最多新元素的集合 | Approximation | 有 `O(log n)` 級別近似保證 | 大多數入門版本 |
| 隨機挑選 / 客製 scoring | Heuristic | 無一般保證 | 特殊權重或線上場景 |

Set Cover 是 Approximation 的好入口，因為 greedy 看起來很直覺，但它不是普通 heuristic：它背後有可證明的近似界。

### 4. Vertex Cover

| 解法 | 類別 | 保證 | 適用 |
|---|---|---|---|
| 枚舉點集合 | Exact | 保證最小 cover | 小圖 |
| Branch and Bound | Exact | 保證最佳 | 中小圖、剪枝有效 |
| Matching-based 2-approx | Approximation | `<= 2 * OPT` | 需要簡單、可證明的解 |
| Local search | Heuristic | 無一般保證 | 大圖、特定分布 |

Vertex Cover 很適合練「approximation 不等於亂貪心」。2-approx 的重點不是它很聰明，而是它的證明乾淨。

### 5. Knapsack

| 解法 | 類別 | 保證 | 適用 |
|---|---|---|---|
| DP by capacity | Exact | 保證最佳，`O(nW)` | `W` 不大 |
| DP by value | Exact | 保證最佳，和總 value 有關 | value 總和不大 |
| FPTAS | Approximation | 可調 epsilon 的近似保證 | 需要品質保證但 exact 太慢 |
| value / weight greedy | Heuristic | 0/1 knapsack 無最佳保證 | baseline，或 fractional knapsack 才 exact |

Knapsack 容易踩坑：fractional knapsack 用 ratio greedy 是 exact；0/1 knapsack 用 ratio greedy 通常只是 heuristic。

### 6. Scheduling / 排班

| 解法 | 類別 | 保證 | 適用 |
|---|---|---|---|
| 特定簡化規則，例如 SPT / EDF | Exact 或有理論性質 | 視問題版本 | 單機、objective 很單純 |
| Brute force / DP | Exact | 小規模保證最佳 | 小樣本 baseline |
| CP-SAT / MIP | Solver | 視 `OPTIMAL` / `FEASIBLE` / gap | 工程首選 |
| Greedy + local repair | Heuristic | 無一般保證 | 快速可用、需求特殊 |
| SA / Tabu | Heuristic | 無一般保證 | 大規模、有完整解和 neighbor |

Scheduling 不是一道題，而是一個問題家族。只要 constraints 稍微變多，就要重新判斷保證，不要把簡化版規則硬套到工程版排班。

## 三類方法的最低驗收標準

### Exact

要能交代：

```text
正確性理由:
時間複雜度:
空間複雜度:
資料量上限:
邊界條件:
```

如果是 DP，要說清楚 state、transition、base case、order。如果是 graph，要說清楚權重條件。如果是 pruning，要說清楚剪掉的分支為什麼不可能成為答案。

### Approximation

要能交代：

```text
近似比:
OPT 的定義:
證明依賴的前提:
演算法複雜度:
前提不成立時會怎樣:
```

不要只說「這是貪心」。Approximation 的價值在於你能說出它為什麼不會差太多。

### Heuristic

要能交代：

```text
state representation:
action / neighbor:
evaluation / fitness:
baseline:
random seed:
best / average / worst:
runtime:
失敗場景:
是否保證最佳解: 否
```

Heuristic 不是不能用，而是不能只靠故事。它要用 baseline、分布統計和可重現實驗換可信度。

## AI 生成解法的判斷清單

看到 AI 或網路給的解法，先不要急著看程式漂亮不漂亮，先問：

1. 它宣稱的是 Exact、Approximation 還是 Heuristic？
2. 如果它宣稱 Exact，正確性條件是什麼？資料量會不會爆？
3. 如果它宣稱 Approximation，近似比是多少？問題前提是否符合？
4. 如果它是 Heuristic，有沒有 baseline、seed、best / average / worst？
5. 它有沒有把 NP-hard 問題講得像排序一樣簡單？
6. 它有沒有把 greedy 誤講成 optimal？
7. 它有沒有把 solver 的 `FEASIBLE` 當成 `OPTIMAL`？
8. 它有沒有把 hard constraint 融進 magic weight，導致不可行解看起來分數很好？

AI 很擅長產生「看起來合理」的 heuristic。你的工作不是一開始就否定，而是把它放回這張分類表裡驗。

## 常見誤區

| 誤區 | 為什麼錯 | 正確說法 |
|---|---|---|
| 「heuristic 就是不正確」 | 有些 heuristic guidance 仍保證最佳，例如 admissible A* | 看它是否保留 exact guarantee |
| 「greedy 都是 heuristic」 | 有些 greedy 是 exact，有些是 approximation，有些只是 heuristic | 看正確性或近似比證明 |
| 「NP-hard 不能 exact」 | 小規模或特殊 instance 仍可 exact | NP-hard 指一般情況沒有已知多項式 exact |
| 「approximation 和 heuristic 一樣」 | approximation 有可證明誤差上界 | 有 ratio 才叫 approximation |
| 「solver 會給最佳解」 | time limit 下可能只給 feasible | 必須讀 status、objective、bound、gap |
| 「跑得快就好」 | 可能比 random baseline 還差 | 至少和 random / greedy / exact 小樣本比 |

## 決策樹

```text
拿到一題最佳化 / 搜尋問題
  ↓
1. 先建模：state + action + objective + constraints 是否清楚？
   否 → 先回建模筆記補模型
   是 → 繼續
  ↓
2. 能用已知 exact algorithm 在合理時間內解嗎？
   是 → 用 exact，並交代複雜度
   否 → 繼續
  ↓
3. n 很小，或可以只在小樣本 exact 嗎？
   是 → 建 exact baseline
   否 → 至少建 greedy / random baseline
  ↓
4. 有成熟 approximation algorithm 嗎？
   是 → 若需要品質保證，優先 approximation
   否 → 繼續
  ↓
5. 是 routing / scheduling / assignment / packing / CP / MIP 嗎？
   是 → 優先 solver，讀 status / gap
   否 → 繼續
  ↓
6. 能自然定義完整解與 neighbor 嗎？
   是 → Local Search / SA / Tabu / 2-opt
   否 → 繼續
  ↓
7. 是 sequential decision 且 simulation 便宜嗎？
   是 → Monte Carlo / MCTS
   否 → problem-specific heuristic + 強制 baseline
```

這棵樹不是要限制創意，而是防止一開始就跳進最沒有保證的那條路。

## Senior SE 為什麼要分清楚

這個區分對 Senior SE 的價值，不在考試，而在決策。

- 讀 AI 生成的解法時，第一個要問「它在哪一類」。
- 跟 PM / 老闆談需求時，可以把「最佳、近似、可用、即時」講成取捨，而不是情緒。
- 遇到 NP-hard 訊號時，不會亂承諾一定最佳。
- 看到 solver 結果時，知道 `OPTIMAL`、`FEASIBLE`、`UNKNOWN` 不是同一件事。
- 寫 heuristic 時，會自然要求 baseline、seed、分布與 gap。
- 審 code 時，能看出「看起來很聰明」但不可驗證的演算法。

用錯類別的代價很高：

```text
用 exact 硬解大規模 NP-hard → 跑不完
用 heuristic 解 P 問題 → 放棄不該放棄的保證
把 approximation 當 heuristic → 浪費可證明的承諾
把 heuristic 當 approximation → 對外承諾過頭
把 solver feasible 當 optimal → 業務結果可能錯
```

## 練習方式

之後每學一個 topic，都回來補一行：

| 題型 | Exact | Approximation | Heuristic | Solver / Baseline |
|---|---|---|---|---|
| Grid Pathfinding | BFS / Dijkstra / A* | 通常不需要 | Weighted A* / Beam Search | BFS / Dijkstra baseline |
| TSP | Brute force / Held-Karp | Christofides（metric） | NN / 2-opt / SA | OR-Tools Routing |
| Set Cover | brute force / IP | greedy `O(log n)` | custom scoring | IP / greedy baseline |
| Vertex Cover | brute force / BnB | 2-approx | local search | exact 小圖 baseline |
| Knapsack | DP | FPTAS | ratio greedy | DP 小樣本 baseline |
| Scheduling | 特定簡化版 / brute force | 視版本而定 | greedy repair / SA | CP-SAT |

最低要求：

- 每題至少能說出一個 exact baseline。
- 至少分清楚 greedy 是 exact、approximation 還是 heuristic。
- 如果用了 heuristic，必須記錄 seed、best / average / worst、runtime。
- 如果用了 solver，必須記錄 status、objective value、bound / gap、time limit。

## 結論

Exact、Approximation、Heuristic 的差別，不是誰比較高級，而是各自承擔不同風險。

```text
Exact 犧牲速度，換最佳保證。
Approximation 犧牲最佳，換誤差上界。
Heuristic 犧牲理論保證，換實務速度與彈性。
Solver 犧牲手寫控制感，換建模能力與工業級搜尋。
```

真正成熟的判斷是：先建模，再問保證；先 baseline，再談 heuristic；先確認可證明與可工具化的路，再決定要不要手寫。
