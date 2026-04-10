# AWS 專業級認證比較：SAP vs DOP vs ANS

## 一句話定位

| 認證 | 核心問題 |
|------|----------|
| **SAP** (Solutions Architect Professional) | 架構怎麼選？ |
| **DOP** (DevOps Engineer Professional) | 怎麼自動化交付與維運？ |
| **ANS** (Advanced Networking Specialty) | 網路怎麼通？ |

---

## DOP 考試重點（不只是服務知識）

DOP 的核心不是「你認識多少服務」，而是**你能不能設計自動化的交付流程並在出事時快速恢復**：

1. **CI/CD Pipeline 設計** — CodePipeline/CodeBuild/CodeDeploy 的組合、藍綠/金絲雀部署策略、rollback 機制
2. **IaC 實戰判斷** — CloudFormation vs CDK 的取捨、stack 拆分策略、drift detection、custom resources
3. **監控與事件驅動** — CloudWatch Alarms → SNS → Lambda 自動修復、EventBridge 規則設計
4. **合規自動化** — Config Rules + SSM Automation 自動修復不合規資源、Organizations SCP
5. **故障排除情境題** — 給你一個壞掉的 pipeline/部署/log，問你怎麼 debug
6. **多帳號治理** — Organizations、Control Tower、跨帳號部署

---

## ANS 考試重點（網路極深）

ANS 幾乎 100% 聚焦網路：

1. **VPC 深度設計** — CIDR 規劃、子網策略、路由表優先級、multiple ENI、prefix list
2. **混合網路** — Direct Connect（含 LAG、DXGW、Transit VIF）、Site-to-Site VPN（含 accelerated VPN）、failover 設計
3. **Transit Gateway 進階** — 路由表隔離、peering across region、multicast、blackhole route
4. **DNS 架構** — Route 53 Resolver（inbound/outbound endpoint）、PHZ 跨帳號共享、DNS firewall
5. **負載均衡深度** — ALB/NLB/GWLB 的 L4 vs L7 差異、cross-zone、sticky session、PrivateLink 搭配 NLB
6. **網路安全** — Security Group vs NACL 狀態差異、Network Firewall、WAF 規則設計、Traffic Mirroring
7. **效能與排錯** — VPC Flow Logs 分析、Reachability Analyzer、Network Access Analyzer、MTU/Jumbo Frame

### ANS 獨有的「硬知識」（SAP/DOP 不會碰到）

- **BGP 路由控制** — AS path prepending、LP/MED 優先級、advertised/received route
- **Direct Connect 物理細節** — 1G/10G/100G port、cross-connect、LAG、MACsec 加密
- **GWLB + appliance 架構** — 第三方防火牆（Palo Alto/Fortinet）流量導引
- **IPv6 雙棧設計** — egress-only IGW、IPv6 CIDR 規劃
- **Wavelength / Local Zone / Outpost 的網路差異**

---

## 三張考試詳細對比

| 面向 | SAP | DOP | ANS |
|------|-----|-----|-----|
| **廣度** | 最廣 | 中等 | 最窄 |
| **深度** | 中等（每個都碰） | CI/CD 很深 | 網路**極深** |
| **VPC** | 基本設計 | 幾乎不考 | 鉅細靡遺 |
| **Direct Connect** | 知道用途 | 不考 | 物理層到邏輯層全考（BGP、VLAN、LOA） |
| **Transit Gateway** | 知道架構 | 不考 | 路由表設計、隔離策略 |
| **DNS / Route 53** | 路由策略選型 | 不考 | Resolver endpoint、PHZ、混合 DNS |
| **CI/CD** | 淺 | **核心（~25-30%）** | 不考 |
| **IaC** | 基本 | 深入（nested stacks、macros、custom resources） | 偶爾出現 |
| **監控 / 日誌** | 基本了解 | 深入（CloudWatch agent、Logs Insights、X-Ray） | Flow Logs 為主 |
| **自動修復** | 偶爾出現 | 高頻（SSM Automation、Lambda remediation） | 不考 |
| **容器** | ECS/EKS 架構選型 | ECS/EKS 部署策略（rolling、blue/green） | 容器網路（VPC CNI） |
| **合規自動化** | Config Rules 知道就好 | Config + SSM + Lambda 端到端自動化 | 不考 |
| **BGP** | 不考 | 不考 | **必考**（AS path、MED、community） |
| **封包層級排錯** | 不考 | 不考 | 考（Flow Logs、Traffic Mirroring） |
| **考試風格** | 長題幹多限制 | 情境 troubleshooting | 網路拓撲圖 + 路由分析 |
| **與 SAP 重疊** | — | ~40% | ~25%（僅 VPC 基礎） |

---

## 難度排名（主觀）

> **ANS ≥ SAP > DOP**
>
> - ANS 難在**深度**（一個 Direct Connect 題可以考 5 層細節）
> - SAP 難在**廣度**（什麼都可能出）
> - DOP 相對最好準備，因為範圍明確

---

## 建議考試順序

以 Linux/DevOps/Platform Engineer 背景：

```
SAP（架構全貌）→ DOP（重疊最多，順勢考）→ ANS（網路專精，最後攻）
```
