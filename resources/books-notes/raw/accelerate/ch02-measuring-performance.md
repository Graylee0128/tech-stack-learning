# Chapter 2: Measuring Performance

> 來源：Accelerate (Forsgren, Humble, Kim) — Part I: What We Found
> 轉錄日期：2026-04-19

---

## 衡量軟體績效的難題

軟體績效難以衡量，原因：
- 不像製造業有可見的庫存
- 工作拆解方式是隨意的
- 在 Agile 中，設計和交付同步進行

---

## 過去衡量方法的缺陷

傳統方法有兩大問題：
1. **聚焦 outputs 而非 outcomes**
2. **聚焦個人/局部指標而非團隊/全局指標**

### 三個有缺陷的指標

| 指標 | 問題 |
|------|------|
| **Lines of Code** | 鼓勵膨脹程式碼；我們更希望用 10 行解決 1000 行的問題 |
| **Velocity** | 是相對指標非絕對指標；容易被灌水；破壞跨團隊協作 |
| **Utilization** | 利用率接近 100% 時，排隊理論告訴我們 lead time 趨近無窮大；必須保留 slack 來吸收非計畫工作 |

---

## DORA 四大指標（Software Delivery Performance）

好的績效衡量需要兩個特性：
1. **聚焦全局結果** — 不讓團隊互相對抗
2. **衡量 outcomes 而非 outputs** — 不獎勵無意義的忙碌

### Lead Time（前置時間）

Lead time 的兩個部分：

| Product Design & Development | Product Delivery (Build, Testing, Deployment) |
|------------------------------|-----------------------------------------------|
| 創新探索，估計高度不確定 | 標準化工作，可預測 |
| 從未做過的全新工作 | 持續整合、測試、部署，越快越好 |
| 結果高度可變 | 結果應低可變 |

> **本書衡量的是 delivery lead time：** 從 code committed → code running in production 的時間。

調查選項：
- less than one hour
- less than one day
- between one day and one week
- between one week and one month
- between one month and six months
- more than six months

### Deployment Frequency（部署頻率）

- Lean 的核心：縮小 batch size（批量大小）
- 軟體中 batch size 不可見 → 用**部署頻率**作為代理指標
- 部署頻率 = batch size 的倒數（越頻繁 = 批量越小）

調查選項：
- on demand (multiple deploys per day)
- between once per hour and once per day
- between once per day and once per week
- between once per week and once per month
- between once per month and once every six months
- fewer than once every six months

### Tempo vs. Stability

- Lead time + Deployment frequency = **Tempo（節奏）**
- 但需要檢驗：加快節奏是否犧牲穩定性？

### Mean Time to Restore (MTTR)

- 現代複雜系統中，故障不可避免
- 關鍵問題不是「會不會壞」而是「多快能修好」
- 調查選項同 lead time

### Change Failure Rate（變更失敗率）

- 變更到 production 後導致服務降級、需要 hotfix/rollback/fix-forward 的百分比
- 在 Lean 中等同於 **percent complete and accurate**

> **Figure 2.1 — Software Delivery Performance 四指標：**
> Lead Time, Deployment Frequency, MTTR, Change Fail Percentage

---

## Cluster Analysis 結果

用 cluster analysis（無監督分群）分析四年調查資料，每年都發現顯著不同的績效群體。

### Table 2.2 — Software Delivery Performance for 2016

| 指標 | High Performers | Medium Performers | Low Performers |
|------|----------------|-------------------|----------------|
| Deployment Frequency | On demand (多次/天) | 1次/週 ~ 1次/月 | 1次/月 ~ 1次/半年 |
| Lead Time for Changes | < 1 hour | 1週 ~ 1月 | 1月 ~ 6月 |
| MTTR | < 1 hour | < 1 day | < 1 day* |
| Change Failure Rate | 0-15% | 31-45% | 16-30% |

### Table 2.3 — Software Delivery Performance for 2017

| 指標 | High Performers | Medium Performers | Low Performers |
|------|----------------|-------------------|----------------|
| Deployment Frequency | On demand (多次/天) | 1次/週 ~ 1次/月 | 1次/週 ~ 1次/月* |
| Lead Time for Changes | < 1 hour | 1週 ~ 1月 | 1週 ~ 1月* |
| MTTR | < 1 hour | < 1 day | 1天 ~ 1週 |
| Change Failure Rate | 0-15% | 0-15% | 31-45% |

> *Low performers 平均值更低（統計顯著），但中位數與 medium 相同。

### 關鍵發現

- **沒有 trade-off：** 高績效者在所有四個指標上都更好
- **高績效者正在拉開差距：** 從 2014-2017，high performers 持續進步；low performers 在 2014-2016 停滯，2017 才開始追趕 tempo 但 stability 反而惡化

### Surprise! — Medium Performers 的失敗率

2016 年 medium performers 的 change failure rate 反而比 low performers 更差（31-45% vs. 16-30%）。

可能原因：medium performers 正在進行大規模重構/轉型，花更多時間在新工作上，忽略了技術債，導致系統更脆弱。

---

## The Impact of Delivery Performance on Organizational Performance

組織績效衡量維度：profitability, market share, productivity

**核心發現：** 高績效組織達成商業目標的可能性是低績效的**兩倍**。

2017 年擴展到非商業組織：高績效者在 quantity of goods/services, operating efficiency, customer satisfaction, quality, mission goals 上也是兩倍可能超標。

> **Figure 2.4：** Software Delivery Performance → Organizational Performance + Noncommercial Performance

### 對外包的啟示

軟體交付績效直接影響商業績效 → **不應該外包核心軟體開發**，應該自建能力。非核心軟體（如 office、payroll）則適合 SaaS 模式。

---

## Driving Change

有了可靠的衡量方式，就能：
- 跨團隊和產業做 benchmark
- 追蹤改善或退步趨勢
- **超越相關性做出預測（predictive analysis）**
- 回答「Change approval board 真的有效嗎？」（Spoiler：沒有，反而負相關）

### 使用指標的警告

> **"Whenever there is fear, you get the wrong numbers."** — Deming

在 pathological 和 bureaucratic 文化中，指標被當作控制手段，人們會隱藏資訊。在使用科學方法改善績效之前，**必須先理解和發展你的文化**。

---

## 本章重點摘要

1. 傳統指標（LOC、velocity、utilization）有根本性缺陷
2. DORA 四指標衡量 **delivery performance**：Lead Time, Deployment Frequency, MTTR, Change Failure Rate
3. Tempo（速度）和 Stability（穩定性）**不是 trade-off** — 高績效者兩者兼得
4. 高績效的軟體交付**預測**更好的商業績效（2x）
5. 不應外包核心軟體開發
6. 在 pathological 文化中使用指標會適得其反 — 先改善文化
