# AWS PrivateLink 架構設計

## 概述

AWS PrivateLink 是一種網路技術，允許在不經過公網的前提下，透過 AWS 骨幹網路私密地存取服務。它基於「提供者 (Provider) 與消費者 (Consumer)」模型運作，是多帳號、多 VPC 環境中實現服務互通的核心機制。

---

## 核心概念：Provider 與 Consumer 模型

```
Provider（提供者）                        Consumer（消費者）
┌──────────────────────┐                ┌──────────────────────┐
│ VPC-A                │                │ VPC-B                │
│                      │                │                      │
│  ┌──────────┐        │                │        ┌───────────┐ │
│  │ 應用程式  │        │   PrivateLink  │        │ ENI       │ │
│  │ (EC2/ECS) │──→ NLB ├───────────────→ VPC    │ (私有 IP) │ │
│  └──────────┘        │   (AWS 骨幹)   │ Endpoint└───────────┘ │
│                      │                │                      │
│  VPC Endpoint        │                │  Interface           │
│  Service (插座)       │                │  VPC Endpoint (插頭) │
└──────────────────────┘                └──────────────────────┘
```

### 提供者端：VPC Endpoint Service

**職責：** 將應用程式以私有方式「發佈」給其他 VPC 使用

**建立流程：**
1. 將應用程式部署在 NLB 或 GWLB 後方
2. 建立 VPC Endpoint Service，綁定該 Load Balancer
3. 系統生成服務名稱（如 `com.amazonaws.vpce.us-east-1.vpce-svc-03d5a...`）
4. 將服務名稱提供給消費者

**支援的 Load Balancer 類型：**

| Load Balancer | 用途 | 跨區域支援 |
|--------------|------|---------|
| **NLB (Network LB)** | 一般應用服務發佈（TCP/UDP/TLS） | 支援跨區域 |
| **GWLB (Gateway LB)** | 網路安全設備（防火牆、IDS/IPS） | 不支援跨區域 |

### 消費者端：Interface VPC Endpoint

**職責：** 在自己的 VPC 中建立連線節點，存取 Provider 的服務

**建立流程：**
1. 在 Private Subnet 中建立 Interface VPC Endpoint
2. 指定要連接的服務名稱
3. AWS 在指定子網中生成 ENI（帶有私有 IP）
4. 應用程式直接透過該私有 IP 存取服務

**高可用部署：** 建議在至少 2 個 AZ 中建立 Endpoint，確保單一 AZ 故障不影響服務。

---

## VPC Endpoint 的三種類型

### 1. Interface Endpoint（基於 PrivateLink）

```
你的 VPC
├─ Private Subnet (AZ-a)
│  └─ ENI (10.0.1.50) ──→ 透過 PrivateLink 連到 AWS 服務
├─ Private Subnet (AZ-b)
│  └─ ENI (10.0.2.50) ──→ 透過 PrivateLink 連到 AWS 服務（HA）
```

- **原理：** 在子網中建立 ENI，流量透過 AWS 骨幹私密傳輸
- **費用：** $0.01/小時/AZ + $0.01/GB 數據處理費
- **支援服務：** 大多數 AWS 服務（SQS、SNS、KMS、Secrets Manager、CloudWatch...）
- **安全控制：** Security Group + Endpoint Policy

### 2. Gateway Endpoint（不使用 PrivateLink）

```
你的 VPC
├─ Route Table
│  └─ pl-xxxxx (S3 Prefix List) ──→ vpce-xxxxx（Gateway Endpoint）
```

- **原理：** 在 Route Table 中加入路由條目，流量直接導向 AWS 服務
- **費用：** 免費
- **支援服務：** 僅 S3 和 DynamoDB
- **安全控制：** Endpoint Policy（無 Security Group）

### 3. Gateway Load Balancer Endpoint

```
你的 VPC                              安全設備 VPC
├─ Route Table                        ├─ GWLB
│  └─ 0.0.0.0/0 → GWLBe ──────────→ │  └─ 防火牆 / IDS / IPS
```

- **原理：** 將流量透明地導向第三方安全設備進行檢查
- **費用：** $0.01/小時 + $0.0035/GB
- **典型場景：** 集中式防火牆、入侵偵測

### 類型選擇決策

```
需要存取 S3 或 DynamoDB？
  ├─ 是 → Gateway Endpoint（免費，優先選擇）
  │       （S3 也支援 Interface Endpoint，
  │         當需要從地端透過 DX/VPN 存取時使用）
  └─ 否 → 需要安全設備檢查？
           ├─ 是 → Gateway Load Balancer Endpoint
           └─ 否 → Interface Endpoint
```

---

## 🎯 核心體悟：何時需要 Provider 端？

> **這是理解 PrivateLink 架構最關鍵的一個區別**

### 場景 1：存取 AWS 託管服務（S3、Secrets Manager、SQS 等）

```
你的 VPC
└─ Interface Endpoint ← 只需要這個（Consumer 端）
   ↓
   AWS 已經為 S3/Secrets Manager 等建立好
   VPC Endpoint Service（Provider 端已由 AWS 管理）
```

✅ **特點：只需架設 Consumer 端**
- AWS 已經為你建好 Provider 側的 VPC Endpoint Service
- 你只需在自己 VPC 建立 Interface Endpoint
- 最簡單的「半個 PrivateLink」設置

---

### 場景 2：存取自己的服務（跨帳號 API、微服務等）

```
你的 Service VPC（Provider）           別人的 VPC（Consumer）
├─ 應用程式                            ├─ Interface Endpoint
├─ NLB                                 │  ↓
├─ VPC Endpoint Service ← 你要建    │  指定你的服務名稱
   ↓
   AWS 骨幹網路（PrivateLink）
```

✅ **特點：需要完整的 Provider + Consumer 架構**
- 你要在 **Provider 端**建立 VPC Endpoint Service（包裝你的 NLB）
- Consumer 才能建立 Interface Endpoint 連接你
- 這是完整的「雙邊 PrivateLink」設置

---

### 對比表

| 項目 | 連接 AWS 託管服務 | 連接自己的服務 |
|------|---------------|-----------|
| **Provider 端** | AWS 已建好 ✅ | 你要建 VPC Endpoint Service |
| **Consumer 端** | 你建 Interface Endpoint | 你或別人建 Interface Endpoint |
| **複雜度** | 低（只需 Consumer） | 高（需完整架構） |
| **成本** | Interface Endpoint 費用 | Endpoint + NLB 費用 |
| **典型場景** | 私有存取 S3、KMS 等 | 跨帳號微服務、共享 API |

---

## DNS 設定與名稱解析

## DNS 設定與名稱解析

### Private DNS（最常見配置）

建立 Interface Endpoint 時啟用 Private DNS，AWS 會自動建立 Route 53 Private Hosted Zone (PHZ)：

```
啟用前：
  nslookup secretsmanager.us-east-1.amazonaws.com
  → 解析到公有 IP（203.0.113.x）

啟用後：
  nslookup secretsmanager.us-east-1.amazonaws.com
  → 解析到 Endpoint 的私有 IP（10.0.1.50）

效果：應用程式無需修改任何代碼，DNS 自動導向私有路徑
```

### 多 VPC 環境的 DNS 解析

**問題：** Private DNS 的 PHZ 只對建立 Endpoint 的 VPC 有效。其他 VPC 無法自動解析。

**解法 1：Route 53 Resolver + 條件轉發**
```
中央 VPC（建立 Endpoint）
├─ Interface Endpoint (secretsmanager)
├─ Route 53 Resolver Inbound Endpoint
└─ Route 53 PHZ

其他 VPC / 地端
├─ Route 53 Resolver Rule:
│   *.us-east-1.amazonaws.com → 轉發到中央 VPC 的 Resolver Inbound
└─ 流量路徑：DNS 查詢 → 中央 VPC 解析 → 回傳私有 IP
```

**解法 2：Route 53 Profiles（2025 推薦方式）**
```
建立 Route 53 Profile：
  包含所有 PrivateLink 的 PHZ 關聯
  一次性套用到所有需要的 VPC

優勢：
  - 不需要每個 VPC 都建立 Resolver Rule
  - 集中管理所有 DNS 配置
  - 大幅簡化多帳號環境的 DNS 架構
```

---

## 跨帳號與跨區域架構

### 跨帳號存取

```
帳號 A（Provider）                    帳號 B（Consumer）
┌──────────────────┐                ┌──────────────────┐
│ VPC Endpoint     │   PrivateLink  │ Interface        │
│ Service          │ ←──────────── │ VPC Endpoint     │
│ (NLB + 應用)     │                │                  │
└──────────────────┘                └──────────────────┘

設定步驟：
  1. Provider（帳號 A）：建立 Endpoint Service
  2. Provider：將帳號 B 的 AWS Account ID 加入允許清單
     aws ec2 modify-vpc-endpoint-service-permissions \
       --service-id vpce-svc-xxx \
       --add-allowed-principals arn:aws:iam::222222222222:root

  3. Consumer（帳號 B）：建立 Interface VPC Endpoint
     指定服務名稱：com.amazonaws.vpce.us-east-1.vpce-svc-xxx

  4. Provider：接受連線請求（若啟用手動核准）
```

### 跨區域存取（2025 新功能）

```
帳號 A (us-east-1, Provider)          帳號 B (ap-northeast-1, Consumer)
┌──────────────────┐                ┌──────────────────┐
│ VPC Endpoint     │   PrivateLink  │ Interface        │
│ Service (NLB)    │ ←──────────── │ VPC Endpoint     │
│ us-east-1        │   跨區域       │ ap-northeast-1   │
└──────────────────┘                └──────────────────┘

限制：
  - 僅支援 NLB 類型（GWLB 不支援）
  - 不支援 AWS 託管服務和 Marketplace 服務
  - 需要 IAM Policy 和 SCP 同時允許
  - 使用條件鍵 ec2:VpceServiceRegion 控制允許的區域
```

---

## 安全架構：多層防護

### 第 1 層：Security Group（作用在 ENI 上）

```json
{
  "SecurityGroupIngress": [
    {
      "IpProtocol": "tcp",
      "FromPort": 443,
      "ToPort": 443,
      "CidrIp": "10.0.0.0/16"  // 僅允許 VPC 內流量
    }
  ]
}
```

### 第 2 層：Endpoint Policy（控制可存取的資源）

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "arn:aws:secretsmanager:us-east-1:111111111111:secret:prod/*"
    }
  ]
}
```

效果：即使擁有完整 IAM 權限，若透過此 Endpoint 存取，也只能讀取 `prod/*` 開頭的 Secret。

### 第 3 層：Provider 端的存取控制

```
Provider 可設定：
  1. 允許清單（Allowed Principals）— 限制哪些帳號可以建立連線
  2. 手動核准（Acceptance Required）— 每個連線請求需人工審核
  3. NLB Security Group — 限制來源 IP 範圍
```

### 安全設計最佳實踐

```
防護層            控制點           建議
──────────────────────────────────────────────────
網路層            Security Group   僅允許 VPC CIDR 的 443 連接埠
資源層            Endpoint Policy  限制可存取的 API 和資源 ARN
身份層            IAM Policy       限制哪些角色可以使用此 Endpoint
組織層            SCP              限制跨區域、跨帳號的操作範圍
Provider 層       允許清單          僅授權特定帳號連線
```

---

## 集中式 Endpoint 架構（成本最佳化）

### 問題：每個 VPC 都建 Endpoint 太貴

```
傳統做法（每個 VPC 獨立建立 Endpoint）：
  VPC-A：Interface Endpoint (SQS)   → $7.2/月
  VPC-B：Interface Endpoint (SQS)   → $7.2/月
  VPC-C：Interface Endpoint (SQS)   → $7.2/月
  合計：$21.6/月（僅 1 個服務）

  若需要 10 個 AWS 服務 × 3 個 VPC = 30 個 Endpoint
  成本：$216/月
```

### 解法：集中式 Endpoint VPC

```
中央 Endpoint VPC
┌─────────────────────────────────────┐
│ Interface Endpoint (SQS)            │
│ Interface Endpoint (SNS)            │
│ Interface Endpoint (KMS)            │
│ Interface Endpoint (Secrets Mgr)    │
│ ...（集中建立所有 Endpoint）         │
│                                      │
│ Route 53 Resolver Inbound Endpoint  │
└────────────────┬────────────────────┘
                 │ Transit Gateway
        ┌────────┼────────┐
        ↓        ↓        ↓
     VPC-A    VPC-B    VPC-C
     (業務)   (業務)   (業務)

DNS 解析路徑：
  VPC-A 的 EC2 → DNS 查詢 sqs.us-east-1.amazonaws.com
    → Route 53 Resolver Rule 轉發到中央 VPC
    → 解析為 Endpoint 的私有 IP
    → 流量透過 TGW 到達中央 VPC 的 Endpoint
    → PrivateLink 連到 SQS
```

**成本效益：**
```
集中式（1 個 Endpoint VPC）：
  10 個 Endpoint × $7.2/月 = $72/月

傳統式（3 個 VPC 各自建立）：
  10 × 3 × $7.2/月 = $216/月

節省比例：67%
```

**注意事項：**
- 流量會經過 TGW，需考慮 TGW 的數據處理費（$0.02/GB）
- 若資料傳輸量極大，逐一建立 Endpoint 可能更划算
- 需要配置 DNS 轉發規則或 Route 53 Profiles

---

## 常見架構模式

### 模式 1：存取 AWS 託管服務

```
場景：EC2 在 Private Subnet 中需要存取 Secrets Manager

架構：
  Private Subnet
  ├─ EC2 Instance
  └─ Interface Endpoint (com.amazonaws.us-east-1.secretsmanager)
     └─ ENI (10.0.1.50)

流量路徑：
  EC2 → ENI (10.0.1.50) → PrivateLink → Secrets Manager
  全程私有，不經過 NAT Gateway，不經過公網
```

### 模式 2：跨 VPC 微服務通訊

```
場景：帳號 A 的支付服務需要被帳號 B 的訂單服務呼叫

帳號 A（支付服務）：
  VPC-Payment
  ├─ ECS Tasks (支付 API)
  ├─ NLB (接收流量)
  └─ VPC Endpoint Service (對外發佈)

帳號 B（訂單服務）：
  VPC-Order
  ├─ ECS Tasks (訂單 API)
  └─ Interface VPC Endpoint (連到支付服務)

流量路徑：
  訂單 API → Endpoint ENI → PrivateLink → NLB → 支付 API
  全程私有，無需 VPC Peering 或 Transit Gateway
```

### 模式 3：地端透過 DX/VPN 存取 AWS 服務

```
場景：地端伺服器需要私密存取 S3

架構：
  地端機房
  └─ Direct Connect / VPN ──→ VPC
                               ├─ Interface Endpoint (S3)
                               │  （此處必須用 Interface，
                               │    不能用 Gateway Endpoint，
                               │    因為 Gateway Endpoint 不支援
                               │    從 VPC 外部路由存取）
                               └─ Route 53 Resolver

DNS 設定：
  地端 DNS → 條件轉發 → Route 53 Resolver Inbound
    → 解析 S3 Endpoint 的私有 IP
    → 地端流量透過 DX → VPC Endpoint → S3
```

### 模式 4：集中式安全檢查（GWLB）

```
場景：所有進出 VPC 的流量都需經過防火牆檢查

檢查 VPC
├─ GWLB (Gateway Load Balancer)
│  └─ 防火牆設備（Palo Alto / Fortinet）
└─ VPC Endpoint Service (GWLB 類型)

業務 VPC
├─ Route Table:
│   0.0.0.0/0 → GWLBe (Gateway Load Balancer Endpoint)
│   ↓
│   流量自動導向檢查 VPC 的防火牆
│   ↓
│   防火牆放行後，流量繼續前進

效果：
  - 對應用程式完全透明（無需修改代碼）
  - 集中管理安全政策
  - 支援水平擴展（GWLB 自動分配流量到多個防火牆）
```

---

## 故障排查

### 症狀 1：無法透過 Endpoint 存取服務

```
排查步驟：
  1. 確認 Endpoint 狀態：
     aws ec2 describe-vpc-endpoints --vpc-endpoint-ids vpce-xxx
     → Status 應為 "available"

  2. 確認 DNS 解析正確：
     nslookup secretsmanager.us-east-1.amazonaws.com
     → 應返回 Endpoint 的私有 IP（10.x.x.x），而非公有 IP

  3. 確認 Security Group 允許流量：
     → Endpoint 的 SG 必須允許來源 IP 的 TCP 443

  4. 確認 Endpoint Policy 允許操作：
     → 查看 Policy 是否限制了特定的 Action 或 Resource

  5. 確認 IAM 權限：
     → 呼叫者的 IAM Role 必須同時擁有服務操作的權限
```

### 症狀 2：跨帳號連線被拒絕

```
排查步驟：
  1. Provider 端：確認 Consumer 帳號已在允許清單中
  2. Provider 端：若啟用手動核准，確認連線請求已被接受
  3. Consumer 端：確認服務名稱拼寫正確
  4. 雙方：確認 SCP 未限制 PrivateLink 相關操作
```

### 症狀 3：DNS 解析仍指向公有 IP

```
排查步驟：
  1. 確認 Endpoint 啟用了 Private DNS
  2. 確認 VPC 的 DNS Resolution 和 DNS Hostnames 均已啟用：
     aws ec2 describe-vpc-attribute --vpc-id vpc-xxx --attribute enableDnsSupport
     aws ec2 describe-vpc-attribute --vpc-id vpc-xxx --attribute enableDnsHostnames
  3. 等待 DNS 緩存過期（通常 60 秒內）
  4. 若從其他 VPC 存取，需配置 Route 53 Resolver 條件轉發
```

---

## 參考資源

- [AWS PrivateLink 概念](https://docs.aws.amazon.com/vpc/latest/privatelink/concepts.html)
- [集中式 VPC Endpoint 架構](https://docs.aws.amazon.com/whitepapers/latest/building-scalable-secure-multi-vpc-network-infrastructure/centralized-access-to-vpc-private-endpoints.html)
- [跨區域 PrivateLink](https://aws.amazon.com/blogs/networking-and-content-delivery/introducing-cross-region-connectivity-for-aws-privatelink/)
- [Route 53 Profiles 簡化 DNS 管理](https://aws.amazon.com/blogs/networking-and-content-delivery/streamline-dns-management-for-aws-privatelink-deployment-with-amazon-route-53-profiles/)
- [跨帳號 Private API 架構模式](https://aws.amazon.com/blogs/compute/architecture-patterns-for-consuming-private-apis-cross-account/)
