# AWS Resource Access Manager (RAM) - 多帳號網路架構設計

## 概述

AWS Resource Access Manager (RAM) 是用於跨帳號安全共享資源的核心服務。特別是在多帳號架構中，RAM 使得中央網路帳號可以集中管理基礎設施，而業務帳號則專注於應用部署，無需複製資源、重複管理。

## 為什麼需要 RAM？

### 傳統多帳號痛點

**沒有 RAM 的情況下：**
```
網路帳號 (Account A)           業務帳號 1 (Account B)
├─ VPC (192.168.0.0/16)      ├─ VPC (10.0.0.0/16)
├─ NAT Gateway                ├─ NAT Gateway（重複投資）
├─ VPC Endpoints              ├─ VPC Endpoints（重複投資）
├─ Route 53 Resolver          └─ ...
└─ ...

                             業務帳號 2 (Account C)
                             ├─ VPC (10.1.0.0/16)
                             ├─ NAT Gateway（重複投資）
                             ├─ VPC Endpoints（重複投資）
                             └─ ...
```

**成本問題：**
- 每個帳號都需要自己的 NAT Gateway（$32/月）
- 每個帳號都需要自己的 VPC Endpoints（$7-15/月/個）
- 重複維護、複雜度高

### RAM 解決的問題

```
網路帳號 (Account A)              [透過 RAM 共享]
├─ VPC (192.168.0.0/16) ────────────────────┐
├─ NAT Gateway（1 個，所有帳號共用）       │
├─ VPC Endpoints（1 套，所有帳號共用）    │
├─ Route 53 Resolver Rules（中央管理）    │
└─ Transit Gateway（中央樞紐）             │
                                            │
                    ┌───────────────────────┼───────────────────────┐
                    ↓                       ↓                       ↓
            業務帳號 1 (B)        業務帳號 2 (C)        業務帳號 3 (D)
            ├─ VPC                ├─ VPC                ├─ VPC
            ├─ EC2               ├─ EC2               ├─ EC2
            └─ App               └─ App               └─ App
```

**好處：**
- ✅ 成本降低 60-70%（共用 NAT Gateway、Endpoint）
- ✅ 運維簡化（中央管理，統一更新）
- ✅ 安全一致（中央定義 Security Group、路由政策）

---

## 四大常見共享資源

### 1. Managed Prefix Lists（受管前綴清單）

**用途：** 集中管理 IP 白名單，分享給所有帳號的 Security Group

**場景：**
```
中央帳號維護：
  Prefix List "Corporate_IP_Range" = 203.0.113.0/24 (總部 VPN)
                                      198.51.100.0/24 (分公司 VPN)

所有業務帳號的 Security Group 規則：
  Inbound Rule: Allow TCP 443 from prefix-list-12345
                ↓（自動解析為 203.0.113.0/24 + 198.51.100.0/24）
```

**優勢：**
- 一次修改，所有帳號自動生效
- 無需更新數十個 Security Group

---

### 2. VPC Subnets（共享 VPC 子網）

**用途：** 多個帳號在同一 VPC 的子網上部署資源

**架構：**
```
網路帳號 (Account A)
┌─────────────────────────────────────┐
│ VPC (10.0.0.0/16)                  │
│ ├─ Public Subnet  (10.0.1.0/24) ──┐│
│ ├─ Private Subnet (10.0.2.0/24) ──┼─→ 透過 RAM 共享
│ └─ NAT Gateway (共用)           ──┘│
└─────────────────────────────────────┘

業務帳號 1、2、3...
└─ 在共享的 Subnet 上啟動 EC2（無法修改 Route Table）
```

**特點：**
- 業務帳號**可以**在共享子網上建立 EC2、RDS 等
- 業務帳號**無法**修改 Route Table、IGW、NAT Gateway
- 網路帳號完全掌控網路層的配置

**成本效益：**
```
傳統方式（5 個帳號）：
  5 × $32（NAT Gateway）= $160/月

使用 RAM 共享：
  1 × $32（NAT Gateway）= $32/月
  節省成本：88%
```

---

### 3. Transit Gateway（中轉閘道）

**用途：** 在中央帳號建立 TGW，供所有業務帳號的 VPC 掛載

**架構（Hub-and-Spoke）：**

```
                中央網路帳號
              ┌─────────────┐
              │ Transit GW  │ ←─ 透過 RAM 共享
              │  (TGW)      │
              └────┬───┬────┘
                   │   │
        ┌──────────┘   └──────────┐
        ↓                         ↓
    業務帳號 1                 業務帳號 2
    ┌──────┐                  ┌──────┐
    │ VPC1 │                  │ VPC2 │
    │掛載到│                   │掛載到│
    │ TGW  │                  │ TGW  │
    └──────┘                  └──────┘
```

**優勢：**
- 完全的網路隔離（各帳號無法直接互訪，除非通過 TGW Route Table 授權）
- 中央帳號掌控所有路由決策
- 無需建立複雜的 VPC Peering

---

### 4. Route 53 Resolver Rules（DNS 轉發規則）

**用途：** 統一管理混合環境的 DNS 轉發規則

**場景：**
```
中央帳號定義：
  Route 53 Resolver Rule:
    company.local.  →  轉發到地端 DNS (192.168.1.10)
    aws.internal.   →  使用 AWS Route 53

所有業務帳號：
  └─ 自動應用此規則，無需各自配置
```

**優勢：**
- 統一的名稱解析策略
- 無縫支援混合環境（地端 + AWS）

---

## 多帳號網路架構設計模式

### 模式 1：中央網路帳號 (Hub-and-Spoke with TGW)

```
組織結構：
  AWS Organizations
  ├─ 網路帳號（Network Account）【中央】
  │  ├─ VPC（10.0.0.0/16）
  │  ├─ Transit Gateway
  │  ├─ Direct Connect
  │  └─ 地端 VPN 連線
  │
  ├─ 業務帳號 1（Workload Account A）
  │  ├─ VPC（10.1.0.0/16）掛載到 TGW
  │  └─ EC2、RDS、Lambda...
  │
  ├─ 業務帳號 2（Workload Account B）
  │  ├─ VPC（10.2.0.0/16）掛載到 TGW
  │  └─ EC2、RDS、Lambda...
  │
  └─ 安全帳號（Security Account）
     ├─ GuardDuty、SecurityHub
     └─ CloudTrail 日誌集中地
```

**RAM 共享資源：**
- Transit Gateway（供業務帳號掛載）
- VPC Subnet（若需共享）
- Managed Prefix Lists（IP 白名單）

**網路流量路徑：**
```
業務帳號 A 的 EC2
  ↓ 連接到 TGW
  ↓ TGW Route Table 決策：目標在業務帳號 B？轉發到其 VPC attachment
  ↓ 業務帳號 B 的 EC2
```

---

### 模式 2：VPC Subnet Sharing（共享子網）

```
適用場景：
  - 多個團隊在同一 VPC 內部署
  - 需要統一的網路隔離和監控
  - 子網數量有限（避免 IP 分割太細）

架構：
  網路帳號
  └─ VPC (10.0.0.0/16)
     ├─ Subnet A (10.0.1.0/24) ─→ 共享給開發團隊
     ├─ Subnet B (10.0.2.0/24) ─→ 共享給測試團隊
     └─ Subnet C (10.0.3.0/24) ─→ 共享給生產團隊

開發團隊（帳號 B）
└─ 在 Subnet A 上啟動 EC2（自己的帳號）
   ├─ 可以修改 EC2 的 Security Group
   ├─ 可以管理 EC2 的生命週期
   └─ 無法修改 Subnet、Route Table、NAT Gateway
```

**細粒度權限控制：**
```
RAM 資源共享時設定的 IAM 策略：
  允許：ec2:RunInstances, ec2:TerminateInstances, ...
  禁止：ec2:ModifySubnetAttribute, ec2:ReplaceRoute, ...
```

---

## 跨帳號流量監控與故障排查

### 統一的 VPC Flow Logs 分析

**場景：** 業務帳號 A 的 EC2 無法連到業務帳號 B 的資源

**排查步驟：**

```
第 1 層：確認 RAM 共享有效
  aws ram describe-resources --resource-type "ec2:TransitGateway"
  → 確認 TGW 在「ASSOCIATED」狀態

第 2 層：檢查 TGW 路由表
  aws ec2 describe-transit-gateway-route-tables
  aws ec2 describe-transit-gateway-routes \
    --transit-gateway-route-table-id tgw-rtb-xxx
  → 確認帳號 B 的 VPC attachment 被允許

第 3 層：檢查 Security Group 規則
  (在帳號 B 中執行)
  aws ec2 describe-security-groups --group-id sg-xxx
  → 確認 Inbound 規則允許來自帳號 A 的流量

第 4 層：查看 VPC Flow Logs
  (在網路帳號的中央日誌位置)
  aws logs filter-log-events \
    --log-group-name "/aws/vpc/flowlogs" \
    --filter-pattern "[srcaddr != ?, dstaddr != ?, action = \"REJECT\", ...]"
  → 確認封包在哪一層被丟棄（Transport vs Network）
```

### 集中監控儀表板

**建議使用 AWS Network Manager：**

```
AWS Network Manager 可提供：
  - 所有帳號的網路拓撲視覺化
  - 跨帳號的 VPC 和 On-Premises 連線狀態
  - 實時的頻寬利用率監控
  - 自動故障檢測和告警
```

---

## 共享資源的權限管理

### 最小權限原則

**場景：** 業務帳號應該能啟動 EC2，但不能刪除 Subnet

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:RunInstances",
        "ec2:TerminateInstances",
        "ec2:DescribeInstances"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Deny",
      "Action": [
        "ec2:DeleteSubnet",
        "ec2:ModifySubnetAttribute",
        "ec2:ReplaceRouteTableAssociation"
      ],
      "Resource": "*"
    }
  ]
}
```

### Service Control Policies (SCP) 層級的控制

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "Action": "ec2:DeleteSubnet",
      "Resource": "arn:aws:ec2:*:*:subnet/*",
      "Condition": {
        "StringEquals": {
          "aws:RequestedRegion": "ap-northeast-1"
        }
      }
    }
  ]
}
```

這會在組織級別禁止所有帳號刪除子網（無論是否通過 RAM 共享）。

---

## 共享資源的生命週期管理

### 何時該取消共享

```
1. 業務帳號遷離或廢止
   └─ 立即停止共享，避免孤立的資源

2. 安全策略變更
   └─ 若該帳號不再符合合規要求，取消共享

3. 架構調整
   └─ 從 Subnet Sharing 遷移到 TGW，需要逐步取消舊共享
```

### 取消共享的影響

```
⚠️ 重要：AWS RAM 不會自動清理
   取消共享後，接收帳號已部署的資源（EC2、RDS 等）仍然存在！

操作流程：
  1. 通知業務帳號：30 天內遷移數據
  2. 在接收帳號中備份/遷移所有資源
  3. 確認所有資源已安全遷移後，取消共享
  4. 刪除網路帳號的共享資源（若不再使用）
```

---

## 常見共享資源對比

| 資源類型 | 可共享範圍 | 接收方可做 | 接收方不可做 | 典型場景 |
|---------|---------|---------|-----------|--------|
| **Transit Gateway** | 組織內所有帳號 | 掛載自己的 VPC | 刪除 TGW、修改路由 | 中央樞紐網路 |
| **VPC Subnet** | 組織內所有帳號 | 啟動 EC2、建立資源 | 刪除/修改 Subnet、Route Table | 多團隊共用網路 |
| **Managed Prefix Lists** | 組織內所有帳號 | 在 SG 規則中引用 | 修改內容（只有所有者可） | 集中 IP 白名單管理 |
| **Route 53 Resolver Rules** | 組織內所有帳號 | 使用 DNS 解析規則 | 修改規則 | 混合環境 DNS |
| **Licence Manager** | 特定帳號 | 使用授權 | 修改授權策略 | 跨帳號軟體授權 |

---

## 架構設計最佳實踐

### 檢查清單

- [ ] **帳號設計** - 確認是否需要中央網路帳號，或使用 AWS Organizations
- [ ] **資源清點** - 列出需要共享的資源（TGW、Subnet、Prefix Lists 等）
- [ ] **權限設定** - 定義每個接收帳號的最小必要權限
- [ ] **監控告警** - 設置 VPC Flow Logs、Network Manager 監控
- [ ] **故障排查** - 預先規劃跨帳號流量問題的排查流程
- [ ] **合規審計** - 定期檢視 RAM 共享狀態、CloudTrail 日誌

### 成本優化考量

```
每個帳號獨立部署的成本：
  NAT Gateway:        $32/月 × 5 帳號 = $160/月
  VPC Endpoints:      $10/月 × 5 帳號 = $50/月
  Route 53 Resolver:  $0.40/日 × 30   = $12/月
  ────────────────────────────────────────────
  小計：                              $222/月

使用 RAM 共享的成本：
  NAT Gateway:        $32/月 × 1      = $32/月
  VPC Endpoints:      $10/月 × 1      = $10/月
  Route 53 Resolver:  $0.40/日 × 30   = $12/月
  ────────────────────────────────────────────
  小計：                              $54/月

節省比例：76%（$222 → $54）
```

---

## 參考資源

- [AWS Resource Access Manager 文件](https://docs.aws.amazon.com/ram/latest/userguide/)
- [Transit Gateway 最佳實踐](https://docs.aws.amazon.com/vpc/latest/tgw/)
- [VPC Sharing 配置指南](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-sharing.html)
- [AWS Organizations - 多帳號架構設計](https://docs.aws.amazon.com/organizations/latest/userguide/)
