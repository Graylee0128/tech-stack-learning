# AWS NAT Gateway 完整知識筆記

---

## 核心陷阱題型

### 🚨 題目情境

題目要求選出 **「錯誤的敘述」**（NAT Gateway 的錯誤特性）。

**常見選項**：
- A. Supports bursts of up to 10 Gbps
- B. Associate exactly one Elastic IP
- C. ❌ **You can associate a security group with a NAT gateway**
- D. Supports TCP and UDP protocol

**正確答案**：C（這是錯誤敘述）

---

## 第一部分：為什麼 C 是錯的？

### 🔑 AWS 考試「陷阱排行第一名」

**NAT Gateway 的本質**：
- 是 AWS **託管服務** (Managed Service)
- 是一個「黑盒子」——AWS 幫你完全維護和管理
- **絕對不能**關聯 Security Group ❌

**NAT Instance 的本質**：
- 是自己開啟的 EC2 實例
- 用 EC2 當作 NAT 角色
- **可以**關聯 Security Group ✅

### 💡 流量控制的替代方案

在 NAT Gateway 上，不能用 Security Group 控制流量，但有其他方式：

| 控制方式 | NAT Gateway | NAT Instance |
|---------|-----------|-----------|
| **Security Group** | ❌ 不支援 | ✅ 支援 |
| **NACL** | ✅ 支援 (Subnet 層級) | ✅ 支援 (Subnet 層級) |

**關鍵**：使用 Subnet 層級的 **NACL (Network ACL)** 來控制進出 NAT Gateway 的流量

---

## 第二部分：其他選項為什麼是對的？

### ✅ 選項 A：Supports bursts of up to 10 Gbps

**現代規格**：
- 標準基準：10 Gbps
- 當前最高：45+ Gbps（自動擴充）
- 考試答案：10 Gbps 通常被視為正確基準描述

### ✅ 選項 B：Associate exactly one Elastic IP

**Public NAT Gateway 的要求**：
- 必須綁定「**正好一個**」Elastic IP (EIP)
- 不能少於 1 個，也不能多於 1 個
- Private NAT Gateway 例外（不需要 EIP）

### ✅ 選項 D：Supports TCP and UDP protocol

**NAT Gateway 支援的協議**：
- ✅ TCP (傳輸控制協議)
- ✅ UDP (用戶數據報協議)

**不支援的協議**：
- ❌ ICMP (Internet Control Message Protocol)
  - 後果：無法透過 NAT Gateway ping 外部網站
  - 但可以：透過 NAT Gateway 執行 curl、wget 等

---

## 第三部分：NAT Gateway vs NAT Instance 對比表

### 🔄 完整特性對比

| 特性 | NAT Gateway (託管) | NAT Instance (自建) |
|------|-----------------|-----------------|
| **Security Group** | ❌ 不支援 | ✅ 支援 |
| **NACL** | ✅ 支援 | ✅ 支援 |
| **高可用性 (HA)** | ✅ 內建（AWS 負責） | ❌ 需手動設定 |
| **頻寬自動擴充** | ✅ 自動（最高 45+ Gbps） | ❌ 受限於 EC2 實例類型 |
| **維護成本** | ✅ 低（AWS 完全維護） | ❌ 高（需自行修補系統） |
| **管理方式** | Route Table 指路 | 需關閉 Source/Dest Check |
| **成本** | 按使用量計費 | EC2 實例費用 + 流量費 |
| **可靠性** | ⭐⭐⭐⭐⭐ | ⭐⭐ |

---

## 第四部分：NAT Gateway 的完整特性清單

### 📋 重要特性速查

#### 1️⃣ Elastic IP 要求
- Public NAT Gateway：必須綁定 1 個 EIP
- Private NAT Gateway：不需要 EIP

#### 2️⃣ 高可用性
- 單一 NAT Gateway：綁定到單一可用區 (AZ)
- 多個 AZ 覆蓋：需在每個 AZ 建立獨立的 NAT Gateway

#### 3️⃣ 協議支援
```
✅ 支援：TCP、UDP
❌ 不支援：ICMP
```

#### 4️⃣ 安全性控制
```
❌ 不支援 Security Group
✅ 支援 NACL（Subnet 層級）
```

#### 5️⃣ 頻寬特性
- 初始：10 Gbps
- 自動擴充：最高 45+ Gbps（無需干預）
- 超過限制：請聯絡 AWS 支援

---

## 第五部分：考場反射動作

### 🎯 記憶口訣

**看到「NAT Gateway + Security Group」，直接反射**：

```
NAT Gateway (託管)
    ↓
黑盒子 → 不能掛 Security Group
    ↓
用 NACL 代替
```

### 🚨 託管服務的通用規則

只要看到這些**託管服務** (Managed Service)，通常**都不能直接掛 Security Group**：

| 服務 | 說明 | 控制方式 |
|------|------|---------|
| **NAT Gateway** | 託管 NAT 服務 | NACL、Route Table |
| **NLB** | Network Load Balancer | NACL、Route Table |
| **ALB** | Application Load Balancer | Security Group ✅（這個例外！） |
| **RDS** | 數據庫服務 | Security Group ✅（這個也例外！） |

💡 **特別注意**：ALB 和 RDS 可以掛 Security Group，但 NAT Gateway 不行！

---

## 第六部分：快速決策樹

### 🌳 NAT 類型判斷

```
需要 NAT？
  ├─ 需要託管服務
  │  ├─ 需要 HA（跨 AZ）→ NAT Gateway (多個)
  │  └─ 單一 AZ → NAT Gateway
  │
  └─ 需要完全控制
     └─ NAT Instance (自建 EC2 + Security Group)
```

### 🌳 Security Group 判斷

```
要控制 NAT 的流量？
  ├─ NAT Gateway
  │  └─ 使用 NACL（Subnet 層級）
  │
  └─ NAT Instance
     └─ 使用 Security Group
```

---

## 考試必記

### ⭐ 核心知識點

1. **NAT Gateway 不支援 Security Group**（陷阱題第一名）
2. **必須用 NACL 控制 NAT Gateway 的流量**
3. **Public NAT Gateway 必須綁定 1 個 EIP**
4. **NAT Gateway 不支援 ICMP（無法 ping）**
5. **NAT Gateway 自動擴充，無需手動干預**

### 🎓 教練總結

> 這題考的就是「**託管服務** vs **自建實例**」的本質差別。
> AWS 託管服務通常會限制你直接管理某些資源（如 Security Group），
> 但會為你處理高可用、自動擴充等複雜邏輯。