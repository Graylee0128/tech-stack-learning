# AWS 跨帳號網路架構

## 1. 架構大局觀：多帳號與隔離策略 (Multi-Account Strategy)

企業級 AWS 環境採用 **Hub-and-Spoke（樞紐與分支）** 網路拓撲：

| 角色 | 帳號類型 | 職責 |
|------|---------|------|
| **Hub（樞紐）** | Connectivity Account（網路/連線帳號） | Transit Gateway (TGW)、Direct Connect、VPN、NAT Gateway、集中式防火牆 |
| **Spokes（分支）** | Production / Dev Accounts（工作負載帳號） | 應用程式（EC2, ECS, Lambda 等） |

### 為什麼要隔離？

- **限縮爆炸半徑 (Blast Radius)**：Production 帳號被駭或誤刪，核心網路（TGW）不受影響
- **職責分離 (Separation of Duties)**：網路工程師專管 Connectivity 帳號，開發人員專管 Production 帳號
- **突破配額限制 (Service Quotas)**：每個帳號有資源上限，多帳號可平行擴展

---

## 2. 核心分享引擎：AWS RAM (Resource Access Manager)

無論是分享 TGW 還是分享 Subnet，底層都使用 **AWS RAM**。

- **功能**：在不同 AWS 帳號之間安全地共享特定資源
- **與 Organizations 整合**：同一 Organization 內可開啟「自動接受分享」；跨 Organization 則必須雙向確認
- **可分享的網路資源**：Transit Gateways、VPC Subnets、Direct Connect Gateways、Prefix Lists 等

---

## 3. TGW 跨帳號連線標準流程

> 考點：當 Auto-accept 關閉時，必須嚴格遵守「擁有者分享 → 使用者請求 → 擁有者核准」的順序。

```
Step 1 【擁有者】建立資源共享
  └─ Connectivity 帳號透過 AWS RAM 將 TGW 分享給 Production 帳號

Step 2 【使用者】接受資源
  └─ Production 帳號接受 RAM 資源分享邀請

Step 3 【使用者】發起連線請求
  └─ Production 帳號建立 VPC Attachment → 狀態為 pendingAcceptance

Step 4 【擁有者】核准並路由
  └─ Connectivity 帳號 Accept Attachment → 關聯 (Associate) 到 TGW 路由表
```

---

## 4. VPC Sharing（共享 VPC / 共享子網）

與 TGW Sharing **完全不同的架構**。

- **做法**：資源擁有者建立 VPC，透過 AWS RAM 將「子網 (Subnets)」分享給其他帳號
- **同一張網**：所有參與帳號都在同一個 VPC，共享同一個 CIDR、IGW、NAT Gateway
- **帳單分離**：網路基礎設施費用由擁有者付；EC2、RDS 費用由建立該資源的參與帳號付
- **安全邊界**：參與帳號只能看到並使用被分享的 Subnet，無法修改 Route Table 或 NACL

---

## 5. TGW Sharing vs. VPC Sharing 對比

| 比較維度 | TGW 跨帳號連接 | 共享子網 (VPC Sharing) |
|---------|---------------|---------------------|
| **分享的資源** | Transit Gateway | VPC Subnets |
| **網路邊界** | 多個獨立 VPC 互聯 | 所有帳號都在**同一個 VPC** 內 |
| **適用場景** | 企業級 Hub-and-Spoke，串接不同部門/環境 | 微服務架構，關係緊密的團隊需要同一網段，節省 IP |
| **路由控制權** | 每個 VPC + TGW 各有路由表 | 只有 VPC 擁有者能控制路由表 |
| **連線發起者** | 使用者建立 VPC Attachment | 使用者直接在 Subnet 裡建立 EC2/ENI |

---

## 專家心法

- **TGW Sharing = 「修馬路」**：每個帳號都有自己的家（VPC），透過分享 TGW（交流道）讓大家互相通車
- **VPC Sharing = 「分房間」**：公司買了一棟大別墅（VPC），把不同房間（Subnet）分給不同員工（帳號），共用同一個大門（IGW）

---

## 參考來源

- [AWS Docs - Transit Gateway](https://docs.aws.amazon.com/vpc/latest/tgw/what-is-transit-gateway.html)
- [AWS Docs - Share your VPC](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-sharing.html)
- [AWS Docs - AWS RAM](https://docs.aws.amazon.com/ram/latest/userguide/what-is.html)
