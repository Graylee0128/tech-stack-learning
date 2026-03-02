# ANS-116：DNS 架構演進題 — 完整學習筆記

## 📋 題目場景

**場景設定：**
- 公司在 AWS 建立多帳號混合架構
- 共享帳號連接地端與 AWS
- On-Prem 員工透過 DNS 名稱存取 AWS 服務（domain: `example.internal`）
- 服務運行在不同 AWS 帳號的 VPC 中

**痛點（Before）：**
```
新服務上線流程：
開發團隊申請 → 多團隊審核 → 手動改 On-Prem DNS
                              ↑
                        慢、複雜、人工流程
```

**目標（After）：**
1. ✅ 服務團隊自助註冊 DNS（不依賴 On-Prem DNS 團隊）
2. ✅ On-Prem 員工照常用 DNS name 存取
3. ✅ 最小化對 On-Prem 配置的改動（Least configuration changes）
4. ✅ 成本有效（Cost-effective）

---

## 📝 官方答案

**正確答案：C, E, F**

| 選項 | 內容 |
|------|------|
| **A** | ❌ 創建本地私有 hosted zone，手動通知員工 |
| **B** | ❌ Route 53 Inbound Endpoint + Conditional Forwarder |
| **C** | ✅ Route 53 Resolver 規則：forward `onprem.example.internal` → On-Prem DNS |
| **D** | ❌ 在共享帳號建 Route 53 PHZ，集中管理 |
| **E** | ✅ 部署 BIND EC2 作為 DNS 中繼 |
| **F** | ✅ 各帳號建自己的 PHZ（服務團隊自管 record） |

---

## 🧠 核心概念解析

### 為什麼是 C + E + F？

#### 解題思路三問

**Q1: On-Prem 員工如何查到 AWS 服務？**

```
On-Prem 員工 → query service1.aws.example.internal
              ↓
              On-Prem DNS（但它只知道 example.internal，不知道 aws.xxx）
              ↓
              ❌ 需要有人告訴它「aws.example.internal 問這個 IP」
```

**答案：** On-Prem 加 conditional forwarder
```
aws.example.internal → forward to [某個 AWS 地方]
```

---

**Q2: AWS 那個「某個地方」是什麼？**

有兩種選擇：

| 方案 | 核心思路 |
|------|---------|
| **方案 B：Route 53 Inbound Endpoint** | 直接在共享帳號建 Endpoint，On-Prem 直接查詢 |
| **方案 E：BIND 中繼** | 在共享帳號建 EC2 BIND，BIND 再 forward 到各帳號 PHZ |

**B vs E 決策：**

```
B 架構：
On-Prem DNS
    ↓ conditional forwarder
    aws.example.internal → Inbound Endpoint
                                ↓
                           route 53 PHZ

問題：
- 新增帳號2時 → On-Prem 要加一條 forwarder
  account2.aws.example.internal → 共享帳號 PHZ

- 新增帳號3時 → 又要改一次 On-Prem
  account3.aws.example.internal → 共享帳號 PHZ

❌ 長期來看 On-Prem 改動頻繁（違反「Least changes」）
```

```
E 架構（BIND 中繼）：
On-Prem DNS
    ↓ conditional forwarder（設定一次！）
    *.aws.example.internal → BIND IP
                                ↓
                        BIND Server (shared account)

BIND 內部規則：
├─ account1.aws.example.internal → Account1 PHZ
├─ account2.aws.example.internal → Account2 PHZ
└─ account3.aws.example.internal → Account3 PHZ

✅ On-Prem 永遠只需改一次
   新增帳號只需在 BIND 加一條 rule
   On-Prem DNS 不需再動
```

**核心洞察：**

> **「Least configuration changes」不是指技術最簡單，而是指對組織流程阻力最小。**

BIND 中繼的本質是把「守門人」（On-Prem DNS 團隊）從關鍵流程中移除。

---

**Q3: 各團隊如何自助註冊？**

**答案：F - 各帳號建自己的 PHZ**

```
Account1:
├─ PHZ: account1.aws.example.internal
└─ 開發團隊自管 record
   ├─ service1.account1.aws.example.internal → IP1
   ├─ service2.account1.aws.example.internal → IP2
   └─ ...自己新增

Account2:
├─ PHZ: account2.aws.example.internal
└─ 另一團隊自管 record
   ├─ api.account2.aws.example.internal → IP3
   └─ ...自己新增

✅ 不用找 On-Prem DNS 團隊
✅ 權限隔離（各帳號管自己的）
✅ 自動化部署可行
```

如果選 D（集中 PHZ 在共享帳號）：
- ❌ 所有 record 集中管理 → 還是得有守門人
- ❌ 無法下放權限給各團隊

---

#### C 的角色：雙向通信

**場景：AWS 資源需要存取 On-Prem 服務**

```
AWS EC2 → query db.onprem.example.internal
         ↓
         Route 53 Resolver
         ↓
         ❌ 不知道 onprem.xxx 是什麼

需要：Resolver Rule
onprem.example.internal → On-Prem DNS IP
```

**C 選項：**
```
Create an Amazon Route 53 Resolver rule to forward
any queries made to onprem.example.internal
to the on-premises DNS servers.
```

這提供了 **AWS → On-Prem** 的反向查詢通道。

---

## 📊 完整架構圖

```
┌─────────────────────────────────────────────────────────┐
│                   ON-PREMISES                           │
│                                                          │
│  Office Employees                                        │
│      ↓ query service1.aws.example.internal              │
│  On-Prem DNS Zone (example.internal)                     │
│      ↓                                                    │
│  Conditional Forwarder [E 設定]                          │
│  *.aws.example.internal → BIND Server IP               │
│                                                          │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│              AWS SHARED ACCOUNT                          │
│                                                          │
│  BIND Server (EC2) [E]                                  │
│  ├─ account1.aws.example.internal → Account1 PHZ        │
│  ├─ account2.aws.example.internal → Account2 PHZ        │
│  └─ Resolver Rule [C]: onprem.xxx → On-Prem DNS         │
│                                                          │
└─────────────────────────────────────────────────────────┘
       ↓                           ↓                      ↓
┌──────────────┐          ┌──────────────┐      ┌──────────────┐
│ Account 1    │          │ Account 2    │      │ Account 3    │
│              │          │              │      │              │
│ PHZ [F]      │          │ PHZ [F]      │      │ PHZ [F]      │
│ account1...  │          │ account2...  │      │ account3...  │
│              │          │              │      │              │
│ VPC Services │          │ VPC Services │      │ VPC Services │
└──────────────┘          └──────────────┘      └──────────────┘
```

---

## 🔄 完整查詢流程

### Forward Path (On-Prem → AWS)

```
Step 1: Office員工查詢
query service1.account1.aws.example.internal

Step 2: On-Prem DNS 查詢自己的 zone (example.internal)
查到 Conditional Forwarder
*.aws.example.internal → BIND IP (Shared Account)

Step 3: Forward 到 BIND Server
query service1.account1.aws.example.internal

Step 4: BIND 根據內部規則
account1.aws.example.internal → Account1 PHZ

Step 5: Account1 PHZ 回傳 IP
service1.account1.aws.example.internal → 10.x.x.x

Step 6: 回傳到 On-Prem DNS → 員工
✅ 解析完成
```

### Reverse Path (AWS → On-Prem)

```
Step 1: AWS EC2 查詢
query db.onprem.example.internal

Step 2: Route 53 Resolver
看到 onprem.example.internal，檢查 Resolver Rule [C]

Step 3: Forward 到 On-Prem DNS
query db.onprem.example.internal

Step 4: On-Prem DNS 回傳
db.onprem.example.internal → 192.168.x.x

Step 5: 回傳到 AWS EC2
✅ 解析完成
```

---

## 📈 架構對比：BIND 中繼 vs Inbound Endpoint

| 維度 | BIND 中繼 (C,E,F) | Inbound Endpoint (B,D) |
|------|-------------------|----------------------|
| **On-Prem 改動次數** | 一次，永不再改 ✅ | 每新增帳號改一次 ❌ |
| **AWS 側複雜度** | EC2 維護（技術債） | 託管服務（低維運） |
| **Subdomain 分流** | BIND 自動處理 ✅ | Inbound Endpoint 無法 ❌ |
| **自動化程度** | 高（雲端團隊自管） | 中（依賴 RAM 規則） |
| **成本** | EC2 運營成本 | 按查詢次數計費 |
| **何時選** | On-Prem 流程僵化 | 雲原生、低維運優先 |

**關鍵區別：**
- **B 方案**：Inbound Endpoint **無法做 subdomain delegation**
  - 無法自動分發到不同帳號
  - 每新帳號都要在 On-Prem 加一條 forwarder

- **E 方案**：BIND 可以做 subdomain delegation
  - account1.aws.xxx → Account1 PHZ
  - account2.aws.xxx → Account2 PHZ
  - On-Prem 完全不知道這些細節

---

## ❌ 各選項錯誤原因

| 選項 | 為什麼錯 |
|------|---------|
| **A** | 手動通知員工 = 沒有架構解法，還是得改 On-Prem DNS |
| **B** | Inbound Endpoint 無法 subdomain delegation；每新增帳號 On-Prem 還要改 |
| **D** | PHZ 集中在共享帳號 = 所有 record 集中管理 = 沒有權限下放 = 還是得找守門人 |

---

## 🎯 考試解題信號

**看到「Least configuration changes」**
→ 選 **BIND 中繼架構（E）** ✅

**看到「Operational Excellence / 低維運」**
→ 選 **Route 53 Resolver 託管（B/D）** ✅

**看到「各團隊自助管理」**
→ 各帳號獨立 **PHZ（F）** ✅

**看到「雙向 DNS（AWS ↔ On-Prem）」**
→ 需要 **Resolver Rule（C）** ✅

**看到「多帳號 + 少改動」**
→ **C + E + F 組合** ✅

---

## 💡 實務參考價值

### 真實企業痛點

```
傳統企業狀況：
├─ On-Prem DNS 團隊 = 守門人
├─ 每次新服務上線都要拜託他們
├─ 審核流程漫長（跨部門協調）
└─ 阻礙敏捷交付

BIND 中繼解法：
├─ On-Prem 一次性配置
├─ 雲端團隊自治（不再依賴 On-Prem）
├─ 新服務無需 On-Prem DNS 團隊參與
└─ 加速交付 ✅
```

### 實際應用場景

**何時用 BIND 中繼（E）：**
- On-Prem IT 流程僵化（審核慢）
- 多帳號持續增長（頻繁改動 On-Prem 不可行）
- 需要雲端團隊獨立交付 DNS 變更

**何時用 Inbound Endpoint（B）：**
- 雲原生企業（On-Prem 快速反應）
- 帳號數量固定（不再增長）
- 優先考慮低維運（不想管 EC2）

---

## 🎓 延伸學習方向

### 1. Route 53 Resolver 深入

**Inbound Endpoint：**
- 用途：將 AWS 資源暴露給 On-Prem
- 限制：無法做 subdomain delegation

**Outbound Endpoint：**
- 用途：AWS 查詢外部 DNS
- 常見：AWS → 自建 DNS

**Resolver Rule：**
- 用途：自動轉發特定 domain
- 支援：Conditional forward + Response filtering
- 跨帳號分享：透過 RAM

### 2. 混合雲 DNS 架構模式

**Hub-Spoke DNS 設計：**
```
On-Prem Central DNS
    ↓
AWS Shared Account DNS (BIND 或 R53)
    ↓
├─ Account1
├─ Account2
└─ Account3
```

**DNS Delegation 原理：**
- Root Zone → Top-level domain → Subdomain
- 每層可以有不同的 authoritative NS

### 3. 現代替代方案

**AWS Cloud Map：**
- 針對服務發現（Service Discovery）
- 自動註冊 / 取消註冊
- 健康檢查自動化

**VPC Lattice：**
- 服務網格（Service Mesh）
- 無需 DNS 也能找到服務
- 流量控制 + 安全隔離

**AWS PrivateLink：**
- 跨帳號服務共享
- 無需 DNS，直接點對點

---

## 🏆 金句總結

> **「Least configuration changes 不是技術最簡單，而是對組織流程阻力最小。」**

> **「BIND 是技術債，但有時候技術債換來的是跨部門溝通的解放。」**

> **「DNS 架構的本質是權力分散——誰可以無授權修改 zone？」**

---

## 📚 相關考點速查

| 考點 | 核心概念 | 選擇信號 |
|------|---------|--------|
| Route 53 Resolver | Inbound/Outbound 差異 | 看「AWS → On-Prem」反向通信 |
| Conditional Forwarder | DNS 流量分流 | 看「On-Prem → AWS」跨境查詢 |
| PHZ Delegation | 各帳號自管 | 看「服務團隊自助」 |
| BIND vs Resolver | 改動少 vs 低維運 | 看「Operational constraints」 |
| Cross-Account DNS | RAM 分享 Resolver Rule | 看「多帳號」 |

---

## 🔗 後續學習方向

1. **[相關文章] 混合雲 DNS 解析 (Hybrid DNS Resolution)**
   - Inbound/Outbound Endpoint 詳解
   - 故障排查方法

2. **[實驗] 搭建 BIND 中繼架構**
   - 在 EC2 安裝 BIND
   - 配置 conditional forwarding

3. **[進階] AWS 多帳號 DNS 策略**
   - 跨帳號 PHZ 共享
   - Resolver Endpoint 最佳實踐
