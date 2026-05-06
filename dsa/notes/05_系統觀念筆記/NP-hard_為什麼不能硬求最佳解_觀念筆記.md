# NP-hard 為什麼不能硬求最佳解 觀念筆記

> 系統觀念筆記。回答：NP-hard 到底是什麼？為什麼它逼我們走進 heuristic？

## 一句話定義

**NP-hard** = 至少和 NP 中最難的問題一樣難。
**目前沒有已知的多項式時間演算法**能解任何 NP-hard 問題到最佳解。
（注意：是「目前沒有」，不是「證明沒有」— P vs NP 問題仍未解。）

## 直覺理解（不從理論硬啃）

| 等級 | 直覺 | 例子 |
|---|---|---|
| **P** | 多項式時間能解 | Sorting、Shortest Path、Min Spanning Tree |
| **NP** | 給你一個解，能多項式時間驗證 | SAT、3-coloring、TSP（決策版） |
| **NP-hard** | 跟 NP 中最難的一樣難（甚至更難） | TSP、Knapsack、Set Cover、Scheduling |
| **NP-complete** | NP-hard 且本身在 NP 內 | SAT、3-coloring、Hamiltonian Path |

## 為什麼這逼我們走進 heuristic

NP-hard 的問題規模一大，exact 演算法的時間就會炸：

| 規模 | O(n²) | O(n³) | O(2ⁿ) | O(n!) |
|---|---|---|---|---|
| n=20 | 400 | 8,000 | ~10⁶ | ~10¹⁸ |
| n=50 | 2,500 | 125,000 | ~10¹⁵ | 算不完 |
| n=100 | 10,000 | 10⁶ | 算不完 | 算不完 |

→ 規模一上去，只能：
1. **Approximation**：放棄最佳，但有理論誤差上界
2. **Heuristic**：放棄最佳和保證，求實務上夠好
3. **Solver**：用工業級的剪枝、branch & bound、constraint propagation 撐久一點

## NP-hard 識別清單

工程上看到下列訊號，先懷疑是 NP-hard：

- ✅ 有「分配」性質：把 N 個東西分到 K 個容器
- ✅ 有「排序 / 排班」性質：N 個任務最佳順序
- ✅ 有「選擇子集合」性質：從 N 個選 K 個最佳組合
- ✅ 有「路徑經過所有節點」性質：TSP 變體
- ✅ 有「滿足所有約束」性質：SAT、CSP

→ 看到這些 → 不要先想 exact，**先想能不能丟 solver 或 heuristic**。

## NP-hard ≠ 沒救

很多 NP-hard 問題在實務上有極強的解法：

- **TSP**：Concorde solver 解到萬級城市最佳
- **SAT**：MiniSat / Glucose 解工業實例飛快
- **MIP**：Gurobi 解上百萬變數的真實問題

這就是為什麼「**NP-hard 識別 + Solver 認識**」比自己手寫 heuristic 更重要。

## 一個常見誤解

> 「NP-hard = 不可能解」 ❌

正確理解：
> 「NP-hard = 沒有已知的『**永遠快 + 永遠最佳**』演算法。但你可以：放棄最佳（heuristic）/ 放棄一般性（solver 對特定實例可能極快）/ 接受不確定（Monte Carlo）。」

## 為什麼 Senior SE 必懂

- 老闆/PM 拍桌「能不能再快一點」→ 你要分得清「P 問題還能優化」vs「NP-hard 沒救要放棄某些東西」
- 設計系統時看到 NP-hard 訊號 → 提前選對工具，避免做到一半發現演算法路線錯
- 讀 AI 生成的解法 → 第一個要問「這題本質是 P 還是 NP-hard？AI 給的演算法符合本質嗎？」

## 進階閱讀（待補）

- Karp 1972 的 21 個 NP-complete 問題
- Garey & Johnson《Computers and Intractability》
- Cook-Levin theorem（為什麼 SAT 是 NP-complete 之祖）
