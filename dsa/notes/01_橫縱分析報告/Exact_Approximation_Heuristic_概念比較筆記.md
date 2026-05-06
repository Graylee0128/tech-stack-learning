# Exact / Approximation / Heuristic 概念比較筆記

> 橋的子筆記之一。釐清三種演算法世界的本質差異，避免之後走進 heuristic 時混淆。

## 一句話定義

| 類別 | 一句話 |
|---|---|
| **Exact** | 保證找到最優解，複雜度可分析 |
| **Approximation** | 不保證最優，但有可證明的誤差上界（如 ≤ 2× 最優） |
| **Heuristic** | 不保證最優、也不保證誤差，但實務上夠好、夠快 |

## 何時用哪一種

- 問題在 **P** 內 → 直接 Exact
- 問題在 **NP-hard** 但可接受誤差證明 → Approximation
- 問題在 NP-hard 且 approximation 也太貴 / 沒有好的近似演算法 → Heuristic
- 即時性要求 > 正確性 → Heuristic

## 比較表（待補實例）

| 維度 | Exact | Approximation | Heuristic |
|---|---|---|---|
| 最優保證 | ✅ | ❌（有誤差上界） | ❌ |
| 複雜度保證 | ✅ | ✅ | ❌ |
| 典型代表 | DP、Dijkstra、二分 | Vertex Cover 2-approx、Christofides | A*、SA、GA、Tabu |
| 適用問題 | P | NP-hard 中可近似 | NP-hard 一般 |
| 實作複雜度 | 中 | 高 | 中-高 |
| 工程心態 | 「對就是對」 | 「夠近就行，且我能證明」 | 「先跑出來再優化」 |

## 經典邊界例題（待補）

- 同一個問題（如 TSP）用三種方法各會怎麼解？
- Set Cover、Vertex Cover、Knapsack 各落在哪一類？

## 為什麼這個區分對 Senior SE 重要

- 讀 AI 生成的解法時，第一個要問的就是「它在哪一類」
- 用錯類別 = 用 exact 解 NP-hard（永遠跑不完）/ 用 heuristic 解 P（被同事笑）
- 跟 PM/老闆談需求時的取捨語言全部來自這三類
