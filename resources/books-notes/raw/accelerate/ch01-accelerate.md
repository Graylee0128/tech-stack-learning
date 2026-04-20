# Chapter 1: Accelerate

> 來源：Accelerate (Forsgren, Humble, Kim) — Part I: What We Found
> 轉錄日期：2026-04-19

---

## 核心論點

"Business as usual" is no longer enough to remain competitive.

組織正在從大型瀑布式專案轉向小團隊、短週期、快速回饋的模式。高績效者不斷精進，不讓任何障礙阻擋，即便面對高風險和不確定性。

為了保持競爭力，組織必須加速（accelerate）以下四件事：

1. **交付商品與服務** — 取悅客戶
2. **與市場互動** — 偵測和理解客戶需求
3. **預期合規與監管變更** — 影響系統的法規變化
4. **應對潛在風險** — 如安全威脅或經濟變化

**軟體是這一切加速的核心。** 這適用於所有行業。銀行靠交易速度和安全性而非金庫競爭，零售商靠線上線下無縫體驗取勝。

---

## Focus on Capabilities, Not Maturity

**Maturity model 的四大缺陷：**

| # | 問題 | Capability model 的優勢 |
|---|------|----------------------|
| 1 | 追求「到達成熟狀態」後就停止 | 持續改進，永不停止 |
| 2 | 一體適用（lock-step），Level 1/2 對所有團隊一樣 | 多維度、動態的，團隊可依自身情境自訂 |
| 3 | 只衡量工具安裝程度（vanity metrics） | 聚焦結果（outcome-based），連結商業影響 |
| 4 | 定義靜態的技術/流程/能力目標 | 適應不斷變化的技術和商業環境 |

> **關鍵差異：** Maturity model 讓組織以為自己「到了」就停止；Capability model 讓組織持續改進。最高績效者每年都在進步，從不滿足於去年的成就。

---

## Evidence-Based Transformations Focus on Key Capabilities

廠商推銷自家產品的能力，顧問推薦自己擅長的能力 — 都有偏見。

**研究發現以下常被引用的因素並不預測績效：**

- 應用程式的年齡和技術（mainframe "systems of record" vs. greenfield "systems of engagement"）
- 部署是由 ops 團隊還是 dev 團隊執行
- 是否實施了 Change Approval Board (CAB)

**真正有差異的是 24 項關鍵能力**（見 Quick Reference / Appendix A），這些能力：
- 容易定義、衡量和改善
- 適用於所有類型的組織

---

## The Value of Adopting DevOps

### 2017 年高績效者 vs. 低績效者的差距

| 指標 | 高績效者優勢 |
|------|-----------|
| 部署頻率（Deployment Frequency） | **46 倍** 更頻繁 |
| 變更前置時間（Lead Time for Changes） | **440 倍** 更快（commit → deploy） |
| 平均復原時間（MTTR） | **170 倍** 更快（從停機中恢復） |
| 變更失敗率（Change Failure Rate） | **1/5**（低 5 倍） |

### 趨勢觀察

相比 2016 年：
- **Tempo 差距縮小** — 低績效者在提升部署頻率和前置時間
- **Stability 差距擴大** — 低績效者的復原時間和失敗率反而更差

**解讀：** 低績效者試圖加快速度，但沒有在品質上投資。結果是更大的部署失敗、更久的復原時間。

> **核心洞察：** 高績效者不需要在速度和穩定性之間取捨 — 通過建構品質（building quality in），他們兩者兼得。

---

## 本章重點摘要

1. 軟體正在改變所有行業，DevOps 能力是競爭力關鍵
2. 用 **Capability model** 取代 Maturity model（持續改進 > 階段到達）
3. 研究發現 **24 項關鍵能力**驅動績效提升
4. 高績效者在 4 項 DORA 指標上全面碾壓低績效者
5. **Speed 和 Stability 不是 trade-off** — 高績效者兩者兼得
6. 常見假設（技術年齡、誰做部署、CAB）並不影響績效
