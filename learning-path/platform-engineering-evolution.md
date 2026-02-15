# Platform Engineering：從 DevOps 到基礎設施產品化的演進

> 核心洞察：Platform Engineering 不是把 Ops 重新分離出來回到傳統模式，而是用軟體工程方式將運維能力「產品化」，讓小規模平台團隊支撐大規模開發團隊。

## 第一層：歷史演進（時間維度）

### Traditional SLDA Era（傳統時代）
**結構：Dev vs Ops 完全隔離**

```
Dev Team                    Ops/Admin Team
(寫程式)          →    (管機器、部署、權限)
      ↓                         ↓
   壓縮檔 ─────"扔過牆"─→  部署失敗
```

**典型痛點：**
- Dev：「我程式可以跑」
- Ops：「你在我機器跑不起來」
- 大量 ticket 與手動流程
- 交付速度慢（Weeks → Months）

**環境特徵：**
- On-premise 為主
- ITIL 流程治理公司
- 傳統系統集成商（SI）
- 密碼與環境由 Ops 完全掌控

---

### DevOps Era（打破牆時代）

**新文化：「You build it, you run it」**

本質變化不是一個人同時做 Dev + Ops，而是：
- ✅ Shared responsibility（共同責任）
- ✅ Automation + CI/CD
- ✅ Infrastructure as Code（IaC）
- ✅ 減少人工部署

**早期收益：**
- 反饋路徑縮短
- 迭代速度加快
- Dev 與 Ops 目標對齐

**但隨之而來的新痛點：**

#### 問題 1：認知負荷爆炸（DevOps Tax）

開發者除了寫業務邏輯，還得會：
- Kubernetes（容器編排）
- Terraform（基礎設施代碼）
- Networking（網路配置）
- IAM（權限管理）
- Observability（監控、日誌、追蹤）
- CI/CD Pipeline（部署流水線）

對純開發者來說 = 地獄

#### 問題 2：每個團隊重複造輪子

各個團隊自行搞定：
- CI/CD 流水線
- Kubernetes 部署模板
- Logging 與 Monitoring
- Security baseline（安全基線）
- 成本治理

結果：
- ❌ 配置不一致
- ❌ 安全風險難控
- ❌ 成本失控

---

### Platform Engineering Era（產品化時代）

**核心轉變：不是分離，而是產品化**

```
❌ 錯誤理解：「再把 Ops 分離出來」（回到傳統）
✅ 正確理解：「把 Ops 的能力產品化」（前進）
```

新結構：Internal Developer Platform（IDP）提供自助服務

```
           Platform Team（平台工程）
         ┌────────────────────┐
         │ CI/CD 平台         │
         │ Kubernetes 平台    │
         │ Observability 套件 │
         │ Security baseline  │
         │ FinOps 治理        │
         └─────────▲──────────┘
                   │ Self-Service（自助門戶）
        ┌──────────┴──────────┐
        │                     │
   Dev Team A           Dev Team B
（專心寫業務）        （專心寫功能）
```

---

## 第二層：痛點驅動的演進

| 時代 | 核心痛點 | 解法方向 | 新痛點 |
|------|---------|---------|--------|
| **Traditional** | Dev & Ops 溝通黑洞 | 打破牆 → DevOps | Dev 工具負荷爆炸 |
| **DevOps** | 每個團隊造輪子 | 標準化能力 → 產品化 | 平台設計精度要求高 |
| **Platform Engineering** | 規模化與認知負荷 | IDP + Golden Path | 持續優化 DX（開發者體驗） |

---

## 第三層：核心思維轉變

### 三個時代的本質差異

| 維度 | Traditional Ops | DevOps（早期/理想） | Platform Engineering |
|------|----------------|-----------------|----------------------|
| **互動方式** | 提交工單（Ticket） | 全員全棧（Full Stack） | API / Self-Service 門戶（IDP） |
| **運維責任** | 全由 Ops 承擔 | 全由 Dev 承擔 | 共同承擔（底層平台 vs 頂層配置） |
| **交付物** | 部署好的伺服器 | 運維腳本 / YAML | 基礎設施即產品（IDP） |
| **核心目標** | 穩定性 | 交付速度 | **降低認知負荷 + 規模化標準** |
| **典型說法** | **我幫你做** | **你自己做** | **我做個工具讓你輕鬆做** |

### 三句話總結

```
Traditional Ops：我幫你做 ─→ 阻礙速度
DevOps：你自己做 ─→ 增加負荷
Platform Engineering：我做工具，讓你輕鬆自助做 ─→ 快速 + 專注
```

---

## 第四層：為什麼不是「歷史倒退」？

關鍵差異在於「規模化能力」：

### Traditional Ops 模式
- 每多一台伺服器 → Ops 團隊要增加人力
- 人力與伺服器數量 **線性關係**
- 無法規模化

### Platform Engineering 模式
- Platform 團隊 5 人 → 支撐 500 個開發者
- 人力與開發者數量 **非線性關係**
- 通過軟體工程實現規模化

**金句：** 「DevOps 是一種文化，而平台工程是實現這種文化的技術路徑。」

---

## 第五層：Golden Path（黃金路徑）

Platform 工程師會定義標準化的最佳實踐路徑：

### 走黃金路徑（推薦）
- 點選按鈕 → 自動建好：
  - AWS 資源配置
  - Kubernetes Namespace
  - 監控 Dashboard
  - CI/CD 流水線
  - 安全基線

### 自定義路徑（可選）
- 你依然可以自己寫複雜配置
- 但平台不再提供「開箱即用」的保證
- 你需要自行承擔複雜度與風險

---

## 第六層：判斷公司所處的階段

### 停留在傳統階段的信號
- [ ] 還在大量手動部署
- [ ] 開環境要開 Ticket
- [ ] Ops 控制著所有密碼與權限
- [ ] 部署流程走 ITIL 審批

### 偽 DevOps（分散式小作坊）
- [ ] 每個團隊的部署方式都不一樣
- [ ] CI/CD pipeline 到處都是自定義版本
- [ ] Security baseline 無法統一

### 真正的 Platform Engineering 時代
- [ ] ✅ 有專門的 Internal Developer Platform（IDP）
- [ ] ✅ Self-service CI/CD（點選按鈕就能部署）
- [ ] ✅ IaC 標準模板（Golden Path）
- [ ] ✅ Cost Governance（FinOps）
- [ ] ✅ Observability 標準化（監控、日誌、追蹤一致）

---

## 第七層：職涯視角——你現在的優勢

基於平台工程的演進，你的經驗映射：

| 你的經驗 | Platform Engineering 核心能力 |
|---------|-------------------------------|
| RHEL 升級自動化 | Infrastructure Automation |
| IaC（Terraform） | Paved Road 基礎 |
| 成本治理（FinOps） | Self-Service 資源管理 |
| 架構思維 + AI Agent | IDP 設計與自動化 |

**結論：** 你比純 Dev 更容易轉向 Platform Engineer / SRE / Cloud Platform Engineer

**市場機會：** 很多公司都在建 Platform Team，卻缺少懂成本優化 + 基礎設施自動化的工程師。

---

## 第八層：面試級答案

### 問題：「DevOps 和 Platform Engineering 有什麼區別？」

**一句話答案：**
> DevOps 是一種文化和實踐，強調 Dev 和 Ops 的協作與自動化。而 Platform Engineering 是實現這種文化的技術路徑，通過將基礎設施產品化（IDP），讓開發者能夠通過自助服務降低認知負荷，同時平台團隊通過軟體工程實現規模化賦能。

### 發展脈絡：
```
Traditional：Dev 和 Ops 分離
    ↓ (痛點：溝通黑洞、交付慢)
DevOps：打破牆、文化整合
    ↓ (痛點：認知負荷爆炸、重複造輪子)
Platform Engineering：基礎設施產品化
    ↓ (目標：規模化、DX 優化、成本控制)
```

---

## 第九層：實踐建議

### 如果你在建立 Platform 團隊

1. **定義 Golden Path**
   - CI/CD 標準流水線
   - Kubernetes 部署模板
   - IaC 最佳實踐

2. **構建 Self-Service 門戶**
   - 提供 API 或 UI
   - 讓開發者無需工單

3. **標準化 Observability**
   - 統一的監控與日誌方案
   - 避免各自為政

4. **引入 FinOps**
   - Cost governance 治理
   - 資源使用最佳化

5. **持續優化 DX**
   - 收集開發者反饋
   - 定期改進工具鏈

---

## 參考框架

### Spotify Model（業界參考）
Spotify 將 Platform Engineering 組織為：
- **Platform Team**：提供 CI/CD、Kubernetes、Observability
- **Squad**（開發團隊）：專注業務邏輯
- 互動方式：Self-service，不需要 Platform Team 手動部署

### 核心數字
- Platform Team 規模：5-10 人
- 支撐開發者：500+ 人
- 部署時間：按鈕點擊 → 幾分鐘完成
- 無人工干預

---

## 總結

**Platform Engineering 是：**
- ✅ 軟體工程思維應用於運維
- ✅ 將共性能力產品化
- ✅ 規模化賦能開發者
- ✅ 降低認知負荷
- ✅ 不是回到傳統，而是進化

**就像一句話說的：**
> 「與其要求每個賽車手都必須學會修引擎（DevOps 的負擔），不如提供一輛性能卓越、且帶有自動維修監測系統的賽車（IDP）。」

---

**相關閱讀：**
- Platform Engineering 的 DORA 指標
- Internal Developer Platform 設計原則
- FinOps 與 Platform Engineering 的結合
- SRE vs Platform Engineer 的區別
