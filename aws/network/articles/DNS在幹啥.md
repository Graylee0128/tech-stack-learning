# DNS 在幹啥：從皮毛到專家的完整指南

## 核心概念速覽

### 層級查詢路徑
- **什麼是層級查詢？** 查詢 `mobile.customersite.com.` 時，會從後往前逐層問
- **查詢順序**：`. (Root)` → `.com (TLD)` → `customersite (SLD)` → `mobile (Subdomain)`
- **專業名稱**：這種查詢方式叫「迭代查詢」

### 子網域授權（Delegation）
- **可以只管某個 Subdomain 嗎？** 完全可以
- **怎麼做？** 在父網域（如 GoDaddy）加一條 **NS 紀錄** 指向 Route 53
- **結果**：那塊領地就完全歸你管理

### SOA（區域身分證）
- **是什麼？** DNS Zone 的「開國詔書」，每個 Zone 必須有且只有一個
- **記錄內容**：誰管這區、多久更新一次
- **建立 Zone 時**：AWS 會自動幫你寫好，不用手動操作

### 國家網域（ccTLD）
- **.tw / .jp 是什麼？** 國家代碼頂級網域（Country Code TLD）
- **技術邏輯**：跟 `.com` 一樣，只是管理單位換成各國政府

## 詳解：DNS 階層查詢的完整流程
想像這是一個官僚體系：每個層級都只知道「下一層是誰管的」，而不知道最終答案。

### 1️⃣ 根網域（Root Server）

**詢問**：我想找 `mobile.customersite.com.`

**回答**：「我不認識它，但我知道所有 `.com` 的伺服器地址，你去問他們吧。」

### 2️⃣ 頂級網域（TLD Server .com）

**詢問**：我想找 `mobile.customersite.com.`

**回答**：「我也不認識這個子網域，但我知道 `customersite.com` 是由 GoDaddy（或其他註冊商）管的，這是他們的地址。」

### 3️⃣ 第二級網域（SLD Server customersite.com）

**詢問**：我想找 `mobile.customersite.com.`

**關鍵動作**：此伺服器查了一下設定檔，發現做了 **Delegation（授權）**

**回答**：「喔！`mobile` 這個部門我已經外包給 AWS Route 53 了，這是那 4 台 Route 53 伺服器的地址。」

### 4️⃣ 子網域權威伺服器（Authoritative Server）

**詢問**：我想找 `mobile.customersite.com.`

**回答**：「沒錯，這是我管的！這台伺服器的 IP 地址是 `1.2.3.4`。」



## 結論概要（TL;DR）

- **「買」的是名分** —— 你付錢給註冊商取得 SLD 使用權，然後自由指定哪台 Nameserver 來幫你管
- **SOA 是「區域身分證」** —— DNS Zone 的第一個紀錄，宣告「誰才是這塊領地的老大」
- **.tw / .jp 是 ccTLD** —— 國家代碼頂級網域，地位與 `.com` 相同

---

## 深度解析

### 1. 你到底是「買」了什麼？
在 DNS 的世界，我們通常說「註冊網域」而非「買伺服器」。

#### 註冊網域（Registering an SLD）

你付錢給如 AWS Route 53 或 GoDaddy 這樣的註冊商。這筆錢會交給 TLD 管理局（例如管理 `.com` 的 Verisign 或管理 `.tw` 的 TWNIC），讓他們在資料庫裡記下：「`customersite.com` 現在歸你管」

#### 指派 Nameserver

註冊完後，告訴管理局：「以後有人問我的網域，請導向這四台 Route 53 伺服器」。這四台伺服器就是你實際在操作的「後台」。

**專家觀點**：你買的是「冠名權」，Route 53 提供的是「代管服務」。

---

### 2. SOA（Start of Authority）到底是什麼？
如果把 DNS Zone 比喻成一個領地，那 SOA 紀錄就是這塊領地的「開國詔書」。它是每個託管區域（Hosted Zone）**必須存在的第一條紀錄**。

#### SOA 包含的重要資訊

| 欄位 | 說明 |
|------|------|
| **Primary Nameserver** | 這塊區域的主要管理伺服器 |
| **Responsible Person** | 管理者的 Email（@ 會被換成 `.`） |
| **Serial Number** | 版本號，每次改動 DNS 就會增加，讓備援伺服器知道要更新 |
| **Timers（Refresh/Retry）** | 其他伺服器多久來同步一次資料 |

#### 為什麼建立 Zone 時不用加 SOA？

當你在 Route 53 建立 `mobile.customersite.com` 時，**AWS 會自動幫你寫好**。你只需要在「父網域」加一個 **NS 紀錄**（路標）指過來就行了。

---

## 多層委派鏈：真實場景

想像你有一個複雜的網域結構，委派可以多層次進行：

```
根 DNS
    ↓ （NS 紀錄指向）
.com Nameserver
    ↓
example.com Zone（Production 環境）
    ├─ staging.example.com → NS 紀錄指向 Staging 的 NS（委派）
    └─ api.example.com → NS 紀錄指向 API 的 NS（委派）
```

### 實際查詢流程

**用戶查詢**：`test.staging.example.com`

1. **根 DNS** → 「去問 `.com`」
2. **.com Nameserver** → 「`example.com` 在 Production」
3. **Production 的 example.com Zone** → 「`staging.example.com` 的 NS 在 Staging」
4. **指向 Staging 的 Nameserver**
5. **Staging 的 Zone** → 回答 `test.staging.example.com` 的 IP ✓

**關鍵點**：每一層都可以做進一步的委派，形成「委派鏈」。只要路標（NS 紀錄）指對了，DNS 查詢就會跟著一層層往下找。

---

## 實戰應用：子域 vs 路徑的選擇

### 技術區別

#### 子域方式（test.staging.example.com）

```
test.staging.example.com  ←─ 不同的「主機名」
api.staging.example.com
需要 DNS 解析每個子域的 A/CNAME 紀錄
每個子域可指向不同的 IP/LB
```

#### 路徑方式（staging.example.com/test）

```
staging.example.com/test   ←─ 同一個「主機名」
staging.example.com/api       不同路徑
DNS 只需解析一次
所有路徑都指向同一個目標 IP
由應用層（ALB Path-based routing）處理
```

### DNS 層面的區別

| 方式 | DNS 記錄 | 查詢結果 | 路由處理 |
|------|---------|---------|---------|
| **子域** | `test.staging.example.com` 需要 A/CNAME | 可指向不同的 IP/LB | DNS 層面完成 |
| **路徑** | `staging.example.com` 一條記錄 | 同一個 IP | 應用層（HTTP）完成 |

### 工作實務：什麼時候用子域？什麼時候用路徑？

#### ✅ 選子域（test.staging.example.com）

**場景 1：不同服務，獨立部署**
- `api.staging.example.com` → API 服務
- `web.staging.example.com` → 前端服務
- `db.staging.example.com` → 數據庫公網接口
- 每個服務獨立配置、獨立 SSL/TLS
- 獨立的 ALB 或 IP
- **例**：大型微服務架構

**場景 2：跨域資源共享（CORS）**
- 前端：`app.staging.example.com`
- API：`api.staging.example.com`
- 不同域名之間才有跨域問題，需要配置 CORS
- **例**：前後端分離架構

**場景 3：多環境隔離**
- `dev.example.com`
- `staging.example.com`
- `prod.example.com`
- 通過 DNS 完全隔離，物理隔離（不同服務器）
- **例**：完整的 DevOps 流程

#### ✅ 選路徑（staging.example.com/api）

**場景 1：同一個應用，多個功能**
- `staging.example.com/api` → API 端點
- `staging.example.com/admin` → 後台
- `staging.example.com/docs` → 文檔
- 同一個應用實例處理，用 ALB Path-based routing
- **例**：單體應用架構

**場景 2：簡單應用，功能少**
- 只有一個主機名
- 通過應用邏輯處理路由
- 成本低（一個 SSL 證書、一個 LB）
- **例**：小型初創公司應用

**場景 3：API 版本控制**
- `/v1/api`、`/v2/api`、`/v3/api`
- 同一個應用服務多版本，向後兼容處理
- **例**：公開 API 服務

### 實務決策樹 🌳

**Q1. 服務獨立嗎？**
- ✅ **是** → 用**子域**（獨立開發、部署、縮放）
- ❌ **否** → 用**路徑**（同一個應用、同一個 LB）

**Q2. 有 CORS 需求嗎？**
- ✅ **是** → 用**子域**（不同域名才有跨域問題）
- ❌ **否** → 路徑可以

**Q3. 成本考慮？**
- SSL 證書：
  - 子域：`*.staging.example.com`（通配符，便宜）
  - 路徑：`staging.example.com`（便宜）
  - → 都差不多
- LB 成本：
  - 子域：可能多個 LB（貴）
  - 路徑：一個 LB（便宜）✓
  - → **推薦路徑**（簡單應用）

**Q4. 規模考慮？**
- 大型：微服務 → **子域**
- 中型：多服務 → **子域**
- 小型：單體 → **路徑**

### 實務例子

#### 場景 A：Netflix 級別的架構

```
api.staging.example.com → API Gateway
auth.staging.example.com → 認證服務
ui.staging.example.com → 前端
payment.staging.example.com → 支付服務
```

**為什麼用子域？**
- 獨立團隊、獨立部署
- 不同技術棧
- 可以獨立縮放
- ✓ **用子域**

#### 場景 B：中型 SaaS 公司

```
staging.example.com/dashboard
staging.example.com/api/v1
staging.example.com/users
```

**為什麼用路徑？**
- 一個前端應用、一個後端
- ALB 做路由
- 成本低
- ✓ **用路徑**

#### 場景 C：大型企業多環境

```
dev.example.com（開發環境）
  ├─ api.dev.example.com
  ├─ auth.dev.example.com

staging.example.com（預發環境）
  ├─ api.staging.example.com
  ├─ auth.staging.example.com

prod.example.com（生產環境）
  ├─ api.prod.example.com
  └─ auth.prod.example.com
```

**策略**：每個環境用子域隔離，環境內部根據需要再選子域或路徑
✓ **用子域（環境層級）+ 可搭配路徑（環境內部）**