# Heuristic 工程選型與失敗場景 觀念筆記

> 系統觀念筆記。回答：拿到一個問題，怎麼選 heuristic 派別？什麼時候 heuristic 會踩坑？

## 工程選型決策樹（待細化）

```text
拿到一個最佳化問題
  ↓
1. 能在合理時間內 exact 解嗎？
   ├─ Yes → 用 exact（DP / Dijkstra / LP），不要過度設計
   └─ No → 繼續
  ↓
2. 是 routing / scheduling / assignment 等標準問題嗎？
   ├─ Yes → 優先試 OR-Tools / CP-SAT
   └─ No → 繼續
  ↓
3. 解空間有明顯結構（鄰域、目標函數平滑）嗎？
   ├─ Yes → Local Search / SA
   └─ No → 繼續
  ↓
4. 問題能寫成 game tree / sequential decision？
   ├─ Yes → MCTS / RL
   └─ No → 繼續
  ↓
5. 有理論需求要近似比保證嗎？
   ├─ Yes → 找 Approximation Algorithm
   └─ No → 試 Hybrid heuristic（greedy initial + LS + SA）
```

## 各派別典型失敗場景

| 派別 | 典型踩坑 |
|---|---|
| A* | heuristic 不 admissible → 找不到最佳；heuristic 太弱 → 退化成 Dijkstra |
| Hill Climbing | 卡 local optimum；plateau 走不出去 |
| Simulated Annealing | 溫度排程沒調好 → 一開始亂跳 / 後期不收斂 |
| Genetic Algorithm | 種群多樣性消失；fitness function 設計不當 |
| Ant Colony | 參數爆多；小問題用大砲 |
| MCTS | 模擬步驟太貴 → 抽樣不夠；reward 稀疏 |
| Approximation | 近似比理論好但常數巨大；實務反而不快 |
| Solver | 模型寫錯 → 跑出怪解；模型對但 solver 跑不出來（建模沒利用結構） |

## 「看起來聰明、實際不可驗證」的 heuristic

AI 生成 / 文獻常見的陷阱：

- 用大量 magic number 但沒交代調參過程
- 沒有 baseline 對照（不知道有沒有比 random 好）
- 只報 best case，沒報 worst / average / variance
- 沒給 random seed，無法重現
- 「實驗結果顯示有效」但實驗集太小或挑過

→ **判斷準則**：能不能用同一個 random seed 跑 100 次，且結果分布合理？沒辦法 = 這個 heuristic 不可信。

## 何時手寫、何時用 solver

→ 詳見 [手寫Heuristic_vs_Solver_觀念比較筆記.md](手寫Heuristic_vs_Solver_觀念比較筆記.md)
