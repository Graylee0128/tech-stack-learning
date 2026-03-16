# AWS Direct Connect (DX) 完整知識筆記

---

## 第一部分：MACsec 基礎知識

### 1️⃣ MACsec 概念

**定義**：MACsec = IEEE 802.1AE，第 2 層加密

**OSI 層級對比**：
```
Layer 7  應用層
Layer 4  TCP/UDP
Layer 3  IP       (← IPSec 在此層)
Layer 2  以太網路  (← MACsec 在此層加密 ✅)
Layer 1  實體線路
```

**特點**：
- 相比 IPSec（Layer 3），MACsec 更底層
- 加密發生在乙太網路幀層級
- 無需應用層修改

---

### 2️⃣ MACsec 的兩個關鍵元素

| 元素 | 全名 | 用途 |
|------|------|------|
| **CAK** | Connectivity Association Key | 主金鑰，驗證雙方身份 |
| **CKN** | Connection Key Name | 識別 CAK 的名稱 |

**認證流程**：
1. 兩端設備用 CAK + CKN 互相認證
2. 認證成功後自動衍生 SAK（Session Key）
3. SAK 用來實際加密資料

---

### 3️⃣ MACsec 的硬體要求

⚠️ **關鍵點：MACsec 需要支援的實體硬體**

| 硬體版本 | 說明 | 升級選項 |
|---------|------|--------|
| **舊硬體** | 不支援 MACsec | ❌ 無法升級，只能換新 |
| **新硬體** | 支援 MACsec | ✅ 可以啟用 |

**AWS Direct Connect 的限制**：
- 只有特定的 DX port/circuit 才支援 MACsec
- 現有的 LAG（舊電路）不一定支援
- 無法線上升級，需要建立新的 LAG + 新的 circuits

---

### 4️⃣ LAG 上的 MACsec 設定層級

**LAG 結構**：
```
LAG (Link Aggregation Group)
├── Connection 1 (10Gbps)
└── Connection 2 (10Gbps)
```

**設定位置**：
- ✅ **LAG 層級**（推薦）：設定自動套用到所有 member connection
- 可選：每條 connection 個別設定（但不標準）

---

## 第二部分：MACsec 題型解題三部曲

### 📋 MACsec 與 Direct Connect 的多選題解題流程

**步驟**：
1. **Step 1**: 建新 LAG（支援 MACsec 的硬體）
2. **Step 2**: 設定 CAK + CKN（金鑰認證）
3. **Step 3**: 啟用 MACsec encryption mode（LAG 層級設定）

### 🎯 三部曲記憶口訣

| 步驟 | 操作 | 選項 |
|------|------|------|
| ① 換新硬體 | 現有的通常不行，要買新的專用埠 | (A) Create new LAG with new circuits |
| ② 對暗號 | 使用 CKN 和 CAK | (B) Configure CAK + CKN |
| ③ 設在 LAG 上 | 在 LAG 層級設定加密模式 | (E) Set encryption mode at LAG level |

---

## 第三部分：DX LAG 的兩大物理限制

### 1️⃣ 速度對稱性 (Speed Symmetry)

LAG 中所有連線必須相同速度。不能混搭不同速率。

### 2️⃣ 最大連線數量限制 (Maximum Connection Limit)

**AWS 官方配額**：

| 連線速度 | LAG 最大活躍連線數 |
|---------|------------------|
| 1 Gbps | **4 條** |
| 10 Gbps | **4 條** |
| 100 Gbps | 需查詢最新文件 |

💡 **考試金句**：一個 LAG 最多只能綁 **4 條活躍連線**（針對 1/10 Gbps）

---

## 第四部分：大流量傳輸的成本優化

### 📍 題型關鍵字識別

看到這些關鍵字時要警惕：

| 關鍵字 | 含義 | 影響 |
|--------|------|------|
| **"large amounts of data"** | 大量資料 | 流量非常龐大 |
| **"new data every time"** | 每次都是新資料 | 持續不斷的傳輸，非一次性遷移 |
| **"reduce transfer cost"** | 降低傳輸成本 | 重點在流量費，而非建置費 |

---

### ❌ VPN 方案的隱藏成本

**AWS 方面**：
- Internet Data Transfer Out: **$0.09 / GB**（非常昂貴）
- 流量費會累積成龐大開支

**地端方面**：
- 需要向 ISP 租用企業級頻寬方案
- 佔用公司對外 Internet 頻寬
- 月租費用極高

**結論**：VPN「免安裝費」的優勢會被流量費完全抵消

---

### 🎯 Direct Connect 方案的成本優勢

**AWS 方面**：
- DX Data Transfer Out: **$0.02 / GB 或更低**
- 相比 VPN 便宜 **75%** 以上

**地端方面**：
- 使用專屬光纖，不佔用 Internet 頻寬
- 頻寬獨享，性能穩定

**黃金交叉點**：
當資料量達到一定規模，**DX 省下的流量費遠遠超過拉專線的建置費**

---

### ❌ 其他選項為什麼錯？

| 選項 | 方案 | 問題 |
|------|------|------|
| **C** | Snowball / Import-Export | 題目說「每次都是新資料」，實體運送無法滿足持續性需求 |
| **D** | 資料留在地端，VPN 遠端查詢 | 直接違反題目要求：「必須傳到 VPC」 |

---

## 第五部分：考場反射動作

### 🚨 AWS 考試計費鐵律

**觸發條件**：題目同時出現以下兩個關鍵字

```
「Large amounts of data (持續性大量資料)」
    ＋
「Reduce network / transfer cost (降低網路/傳輸成本)」
```

**正確答案**：**100% 是 Direct Connect (DX)**

---

### 💡 陷阱與破解

**常見誤區**：
- ❌ 被 VPN「免安裝費」迷惑，忽略背後龐大的「流量過路費」
- ❌ 沒有比較 Data Transfer Out 的單價差異
- ❌ 低估長期維運成本

**破解方法**：
✅ 記住關鍵邏輯：**「大流量 = DX 最省」**
✅ 看到計費題就做 TCO (Total Cost of Ownership) 比較
✅ 永遠考慮地端隱藏成本

---

## 快速查閱表

### MACsec 題型速查

```
需要加密 Direct Connect？
  ├─ 是 → 檢查現有硬體是否支援
  │  ├─ 支援 → 直接設定 CAK + CKN
  │  └─ 不支援 → Create new LAG + 新硬體
  └─ 否 → 無需 MACsec
```

### 計費題型速查

```
大量持續傳輸 + 降低成本？
  ├─ 是 → Direct Connect
  └─ 否 → 評估其他選項
```



恭喜你！這題你選 A 是完全正確的！這代表你對 Direct Connect (DX) 的底層機制——Virtual Interface (VIF, 虛擬介面) 已經有了很紮實的理解。這題考的是：「如何透過專線去存取 AWS 的公有服務（如 S3）」。我們馬上用「題幹手術」來複習這個核心觀念。1. 【核心觀念：Direct Connect 的三種「通道」】當你拉了一條 Direct Connect 實體專線後，它只是一條「沒通電」的線。你必須在上面建立 VIF 才能傳資料。AWS 提供三種 VIF，就像三種不同的車道：Public VIF (公有虛擬介面)：用途： 讓你從地端機房，透過專線直接連到 AWS 的 「公有服務」（如 S3, DynamoDB, EC2 公有 IP）。特點： 你會透過 BGP 收到全 AWS 的公有 IP 路由。這就是這題的 正解。Private VIF (私有虛擬介面)：用途： 讓你連到 VPC 內部的 「私有資源」（如 EC2 的私有 IP）。特點： 它會連往 VGW 或 Direct Connect Gateway。Transit VIF (中轉虛擬介面)：用途： 連接到 Transit Gateway (TGW)，一次串接幾百個 VPC。2. 【為什麼其他選項是煙霧彈？】❌ B. Establish a VPN connection：雖然 VPN 也能通，但題目要求的是 「Dedicated connection (專用連線)」 且要 「Low latency (低延遲)」。VPN 走的是公共網際網路，會抖動、延遲高，完全違背了買專線的初衷。❌ C. Configure a private virtual interface：這是一個很強的干擾項。如果你想用 Private VIF 存取 S3，你必須在 VPC 裡建立 S3 Interface Endpoint (PrivateLink)。但題目明講是要連到 「Public S3 endpoint」，所以必須走 Public VIF。❌ D. Add a BGP route...：這句話半對半錯。建立 VIF 的過程確實需要 BGP 宣告路由，但「增加一條路由」並不是「建立連線」的完整步驟，它只是配置的一部分，描述太籠統。💡 專家教練的考場直覺在 AWS 網路考試中，請記住這個 「目的地 vs. 車道」 的對應表：目的地 (Destination)該選哪種 VIF？S3 / DynamoDB / Public APIPublic VIFEC2 Private IP (單一 VPC)Private VIF數個 VPC / Transit GatewayTransit VIF