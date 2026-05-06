# 手寫 Heuristic vs Solver 觀念比較筆記

> 系統觀念筆記。回答：什麼問題該手寫 heuristic？什麼問題該丟給 OR-Tools / Gurobi？

## 一句話總結

**標準問題 + 中型規模 + 需要解釋性 → Solver**
**非標準問題 + 怪鄰域 + 即時性極高 → 手寫**

## 兩條路線的對比

| 維度 | 手寫 Heuristic | Solver（OR-Tools / Gurobi / CP-SAT） |
|---|---|---|
| **入門成本** | 低（會寫 Go 就能開工） | 中（要學建模語言、constraint 寫法） |
| **問題泛用性** | 一題一寫 | 一個 framework 解一大類 |
| **解品質** | 看你功夫 | 通常比手寫好（多年研究 baked in） |
| **可解釋性** | 你寫的你懂 | 看 solver 報告 |
| **執行速度（達到夠好解）** | 可調，但寫得差會慢 | 通常快，且能設 time limit |
| **修改成本** | 改 code | 改 constraint |
| **適合場景** | 即時、嵌入式、無依賴 | 後台批次、規劃系統 |
| **不適合場景** | 標準 routing / scheduling | 即時、依賴重的環境 |

## 決策清單

該丟給 solver 的訊號：

- ✅ 問題能寫成 LP / MIP / CP / SAT 的標準形式
- ✅ 是 TSP / VRP / Job Shop / Assignment 等經典變體
- ✅ 規模在 solver 能處理範圍內（試試 OR-Tools 通常 ≤ 萬級變數）
- ✅ 不需要極端低延遲（可以接受 1-60 秒回應）
- ✅ Constraint 之後可能會變，希望易維護

該手寫 heuristic 的訊號：

- ✅ 問題太特殊，沒辦法寫成標準 LP / CP
- ✅ 規模超大（百萬以上），solver 跑不動
- ✅ 即時性需求極高（毫秒級）
- ✅ 部署環境不允許依賴重型 solver
- ✅ 客製鄰域 / 客製 reward shaping 才能拿到好解
- ✅ 學術研究就是要證明你的 heuristic 比 solver 強

## 混合策略

最常見其實是混合：

- **Initial solution by greedy → Local search refine → SA escape local optimum**
- **Solver give baseline → 手寫 heuristic 改善後處理**
- **Decompose: Solver 解子問題 → 手寫整合**

## 反直覺案例（待補）

- 案例 1：某 routing 問題，OR-Tools 30 秒給 95% 最優；手寫 SA 5 分鐘還只到 90%
- 案例 2：某客製排班問題，OR-Tools 模型寫到崩潰；手寫貪心 + 局部交換 50 行搞定
- 案例 3：你工作上遇到的真實案例 → ★ 強烈建議補一個

## 怎麼選 Solver

- **OR-Tools (Google)**：開源，Routing 強，CP-SAT 成熟，Python API → 報告 2 ⭐ 主推
- **Gurobi / CPLEX**：商業，MIP 王者，但要 license
- **HiGHS**：開源 LP / MIP，輕量
- **MiniZinc**：建模語言，可切換多種 solver backend
- **Z3**：SMT solver，適合邏輯約束強的問題

報告 2 主軸鎖定 OR-Tools，其他作為延伸閱讀。
