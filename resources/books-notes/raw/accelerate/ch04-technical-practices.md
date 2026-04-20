# Chapter 4: Technical Practices

> 來源：Accelerate (Forsgren, Humble, Kim) — Part I: What We Found
> 轉錄日期：2026-04-19

---

## 背景

Agile Manifesto (2001) 時期，Extreme Programming (XP) 是最熱門的 Agile 框架，強調 TDD 和 CI 等技術實踐。但許多 Agile 導入**把技術實踐當作次要**，只關注管理和團隊實踐。

> **研究發現：技術實踐在達成成果中扮演關鍵角色。**

---

## 什麼是 Continuous Delivery？

CD 是一組能力，讓我們能將所有類型的變更（features、config changes、bug fixes、experiments）**安全、快速、可持續地**送到 production 或使用者手上。

### CD 五大原則

| # | 原則 | 說明 |
|---|------|------|
| 1 | **Build quality in** | 不靠檢查達成品質，而是**把品質建入產品**（Deming 第三點）。建立文化+工具，快速偵測問題並立即修復 |
| 2 | **Work in small batches** | 把工作拆成小塊，快速交付可衡量的商業成果，獲取回饋並修正方向。改變軟體交付的經濟模型，讓單次推送成本極低 |
| 3 | **Computers perform repetitive tasks; people solve problems** | 自動化重複性工作（迴歸測試、部署），釋放人力做更高價值的問題解決工作 |
| 4 | **Relentlessly pursue continuous improvement** | 高績效團隊永不滿足，持續改善是每個人日常工作的一部分 |
| 5 | **Everyone is responsible** | 避免部門各管各的（dev 管 throughput、test 管 quality、ops 管 stability）。這些都是**系統層級結果**，需要所有人緊密協作 |

### CD 三大基礎

| 基礎 | 說明 |
|------|------|
| **Comprehensive configuration management** | 從版本控制中的資訊，全自動化地 provision 環境、build、test、deploy。任何環境/軟體變更都透過自動化流程從版本控制套用 |
| **Continuous integration (CI)** | 分支短命（< 1 天），頻繁整合到 trunk/master。每次變更觸發 build + unit tests。失敗時立即修復 |
| **Continuous testing** | 測試不是「dev complete」後才開始。自動化 unit + acceptance tests 跑在每個 commit。開發者可在本機跑所有自動化測試。測試人員持續對 CI 最新 build 做探索性測試。沒有通過所有相關測試就不算「done」 |

> CD 正確實施後，發布新版本應該是**日常例行活動**，可隨時 on demand 執行。

---

## CD 的影響（The Impact of Continuous Delivery）

### 2014-2016 衡量的能力

1. Version control（application code、system config、app config、build scripts）
2. Comprehensive test automation（可靠、容易修復、定期執行）
3. Deployment automation
4. Continuous integration
5. Shift left on security
6. Trunk-based development
7. Effective test data management

### CD 的成果

這些能力合在一起對軟體交付績效有**強正面影響**，同時：
- **降低部署痛苦（deployment pain）**
- **降低團隊倦怠（team burnout）**
- **更強的組織認同感（identity）**
- **改善組織文化** — 實施 CD → 開發者對品質和穩定性等全局結果承擔責任 → 正面影響團隊互動和組織文化

### 2017 年擴展分析

建立 first-order CD construct，直接衡量 CD：
- 團隊能在整個交付生命週期中 **on demand 部署到 production**
- 系統品質和可部署性的**快速回饋**對所有人可用，且所有人都優先處理

新增兩個有統計顯著影響的能力：
- **Loosely coupled, well-encapsulated architecture**（詳見 Chapter 5）
- **Teams that can choose their own tools**

> **Figure 4.1：** 9 大能力 → Continuous Delivery
> Version Control, Deployment Automation, CI, Trunk-Based Development, Test Automation, Test Data Management, Shift Left on Security, Loosely Coupled Architecture, Empowered Teams, Monitoring, Proactive Notification

### Figure 4.2 — CD 的全面影響

```
Continuous Delivery → Westrum Organizational Culture
                    → Software Delivery Performance → Organizational Performance
                    → Less Rework
                    → Identity
```

### Figure 4.3 — CD 讓工作更永續

```
Continuous Delivery → Less Deployment Pain
                    → Less Burnout
```

> CD 幫助實現 Agile Manifesto 原則：「Agile processes promote sustainable development. The sponsors, developers, and users should be able to maintain a constant pace indefinitely.」

---

## CD 對品質的影響

品質衡量指標（proxy variables）：
- 應用程式品質和效能（從事者的主觀感知）
- **花在 rework 或 unplanned work 的時間比例**（最強相關）
- 花在處理終端使用者發現的 defects 的時間比例

### Figure 4.4 — New Work vs. Unplanned Work

| 指標 | High Performers | Low Performers |
|------|----------------|----------------|
| **New Work** | **49%** | 38% |
| **Unplanned Work or Rework** | **21%** | 27% |
| **Other Work**（meetings, routing maintenance, etc.） | 30% | 35% |

### Failure Demand 概念

- **Unplanned work** = 品質未被建入產品的證據
- 《The Visible Ops Handbook》比喻：注意油量警示燈 vs. 在高速公路上沒油
- **Failure demand**（John Seddon, Vanguard Method）= 因為第一次沒做對而產生的工作需求

---

## CD 實踐：各能力細節

### Version Control

- 不只是 application code — **system config 和 app config 在版本控制中的相關性比 app code 更高**
- 配置通常被視為次要關注，但研究顯示這是個**誤解**

### Test Automation

預測 IT 績效的實踐：

1. **測試必須可靠（reliable）**
   - 通過 = 有信心軟體可發布
   - 失敗 = 有信心是真實缺陷
   - 不可靠的測試放入 **quarantine suite** 獨立執行，或直接刪除
2. **開發者主導建立和維護 acceptance tests**
   - QA 或外包維護的自動化測試**與 IT 績效不相關**
   - 開發者寫測試 → 程式碼更可測試（TDD 的重要原因）
   - 開發者負責測試 → 更投入維護和修復

> **Testers 的角色並非消失**：手動測試（探索性、可用性、驗收測試）+ 與開發者協作建立自動化測試套件

### Test Data Management

- 成功團隊有足夠的測試資料跑完整自動化測試
- 能 on demand 取得測試資料
- 測試資料不是自動化測試的瓶頸

### Trunk-Based Development

研究發現：
- 在 trunk/master 上開發（而非 long-lived feature branches）**與更高交付績效相關**
- 高績效團隊：**< 3 active branches**，分支生命 **< 1 天**，無 code freeze/stabilization 期
- 這些結果**獨立於團隊大小、組織大小、產業**

> **GitHub Flow 的爭論：**
> - 短命分支（< 1 天整合 + < 1 天 merge）的表現優於長命分支
> - 長命分支阻礙重構和團隊內部溝通
> - GitHub Flow **適合** open source（兼職貢獻者的分支可以活更久）

### Information Security（Shift Left）

- 高績效團隊將 infosec 整合到交付流程中
- 安全人員在軟體交付生命週期的**每一步**提供回饋（設計 → demo → test automation）
- **不減慢開發速度**，將安全關注整合到團隊日常工作
- 整合安全實踐**提升**軟體交付績效

---

## 導入 Continuous Delivery

CD 的技術實踐對組織有**巨大影響**：
- 改善交付績效和品質
- 改善文化
- 降低倦怠和部署痛苦

但導入需要：
- 重新思考團隊協作方式、工具和流程
- 大量投資測試和部署自動化
- **持續簡化系統架構**，確保自動化的建立和維護成本不會過高

> **關鍵障礙：企業和應用程式架構。** → Chapter 5

---

## 本章重點摘要

1. 技術實踐在 Agile 導入中不是次要的 — **它們至關重要**
2. CD 五大原則：Build quality in、Small batches、Automate repetitive tasks、Continuous improvement、Everyone is responsible
3. CD 三大基礎：Configuration management、CI、Continuous testing
4. 9 大能力驅動 CD（含 2017 新增的 loosely coupled architecture 和 empowered teams）
5. CD → 更好的交付績效 + 文化 + 組織認同 + 更少 rework
6. CD → 更少 deployment pain + burnout（工作更永續）
7. High performers：49% new work / 21% rework；Low performers：38% / 27%
8. **Config 在版本控制中比 code 更重要**（出乎意料的發現）
9. 開發者主導測試 > QA 主導測試
10. Trunk-based development（< 1 天分支）優於 long-lived branches
11. Security 左移不會拖慢速度，反而**提升**績效
12. 導入 CD 的最大障礙是**架構**
