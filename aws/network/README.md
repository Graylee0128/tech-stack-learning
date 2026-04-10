# AWS 網路服務

AWS 網路相關的學習筆記和精品文章。涵蓋 VPC、PrivateLink、Direct Connect、VPC Peering 等核心概念。

## 學習入口

- [plan.md](./plan.md) - AWS 網路證照 4 週高強度學習計畫
- [learning-log.md](./learning-log.md) - 學習紀錄索引與每日筆記入口
- [exam-result-analysis-2026-04-09.md](./exam-result-analysis-2026-04-09.md) - 4/9 ANS 考後分析、弱點判斷與 retake 建議
- [questions/README.md](./questions/README.md) - 解題紀錄與錯題複盤入口
- [ans-notes/README.md](./ans-notes/README.md) - 9 大主題筆記與建議複習順序

## 近期進度

- Week 1 進行中：已完成 BGP 路由優先序、DX / VIF / DXGW、VPN family、VGW vs TGW 基礎釐清
- 下一步：補完 Direct Connect 細節與 Transit Gateway route table / attachment 題型

## 目錄結構

### notes/ - 學習筆記
個人學習過程中的筆記、實驗記錄和 Q&A：

| 檔案 | 主題 |
|------|------|
| [ANS-Cheat-Sheet-中文版.md](./notes/ANS-Cheat-Sheet-中文版.md) | ANS 完整速查表（中文版，含高頻考點速記） |
| [memo.md](./notes/memo.md) | ANS-C01 四大層級備考筆記（TGW、BGP、監控） |
| [memo2.md](./notes/memo2.md) | 補充備考筆記 |
| [privateLink.md](./notes/privateLink.md) | PrivateLink 完整架構設計（Provider/Consumer、集中式 Endpoint） |
| [DX知識.md](./notes/DX知識.md) | Direct Connect MACsec、LAG、CAK/CKN |
| [DX-backup.md](./notes/DX-backup.md) | DX 備援架構設計 |
| [S2S-VPN知識.md](./notes/S2S-VPN知識.md) | Site-to-Site VPN、IKE Phase、DPD、NAT Keepalive |
| [route53知識.md](./notes/route53知識.md) | Route 53 路由策略（Latency、Geolocation、Failover 等） |
| [NAT.md](./notes/NAT.md) | NAT 複雜度與 PrivateLink 解法 |
| [hub-n-spoke架構.md](./notes/hub-n-spoke架構.md) | TGW Hub-and-Spoke 架構設計 |
| [透明防火牆是啥.md](./notes/透明防火牆是啥.md) | GWLB 透明防火牆（Bump-in-the-wire）、IGW Gateway Route Table |
| [Default-NACL-vs-SG-行為比較.md](./notes/Default-NACL-vs-SG-行為比較.md) | NACL vs Security Group 完整比較 |
| [RAM.md](./notes/RAM.md) | Resource Access Manager 跨帳號共享 |
| [AWS-跨帳號網路架構-TGW-vs-VPC-Sharing.md](./notes/AWS-跨帳號網路架構-TGW-vs-VPC-Sharing.md) | TGW vs VPC Sharing 跨帳號架構選型 |
| [TGW-Connect-vs-DX-路由控制差異.md](./notes/TGW-Connect-vs-DX-路由控制差異.md) | TGW Connect 與 DX 的路由控制差異 |
| [ANS-116-DNS架構演進題.md](./notes/ANS-116-DNS架構演進題.md) | DNS 架構演進實戰題解析 |
| [不支援DNS.md](./notes/不支援DNS.md) | 哪些服務不支援 DNS（考試陷阱） |
| [DHCP設定不能改嗎.md](./notes/DHCP設定不能改嗎.md) | DHCP Option Set 設定方式 |
| [AWS-ANS-Lab-Outline.md](./notes/AWS-ANS-Lab-Outline.md) | ANS 認證 Lab 實作大綱與考試領域對應 |
| [cloud-front.md](./notes/cloud-front.md) | CloudFront VPP/OPP 兩段式連線架構與 S3 來源設定 |
| [ELB知識.md](./notes/ELB知識.md) | ALB vs NLB 選型比較、X-Forwarded-For 來源 IP 實務 |
| [DNS紀錄.md](./notes/DNS紀錄.md) | Route 53 DNS 紀錄類型與 CloudFront 指向陷阱題 |
| [MTU.md](./notes/MTU.md) | MTU / Jumbo Frames 網路傳輸效能優化 |
| [NAT知識.md](./notes/NAT知識.md) | NAT Gateway 特性與常見陷阱題型 |
| [網路校能.md](./notes/網路校能.md) | 網路效能黃金三角（Same AZ、Placement Group、Enhanced Networking） |
| [群組.md](./notes/群組.md) | Target Group vs Placement Group 觀念釐清 |
| [路由評估順序.md](./notes/路由評估順序.md) | AWS Route Evaluation Order 路由評估鐵律 |
| [監控.md](./notes/監控.md) | IDS/IPS 網路安全監控設備 |
| [看流量題型.md](./notes/看流量題型.md) | EC2 網路流量檢查題型解析 |
| [公共IP&EIP.md](./notes/公共IP&EIP.md) | Public IP vs Elastic IP 生命週期差異 |
| [遷移.md](./notes/遷移.md) | 雲端遷移策略（Legacy Application 判斷） |
| [vpc連接\[暫定\].md](<./notes/vpc連接[暫定].md>) | VPC 連接架構（Hub-Spoke 檔案伺服器情境） |
| [workspace.md](./notes/workspace.md) | AWS WorkSpaces 虛擬桌面架構 |

### articles/ - 精品文章
精心打磨的技術文章，採用「Pillar + Cluster」策略：

**Pillar（主文）**
- [AWS 內網到底是什麼？我的釐清過程](./articles/aws-private-network-explained.md)
- [Global Accelerator vs CloudFront：AWS 的兩條快速通道](./articles/global-accelerator-vs-cloudfront.md)
- [混合雲連接架構：DX、DXGW、VGW 的選型邏輯](./articles/混合雲連接架構-DX_DXGW_VGW.md)

**Cluster（子文）**
- [DNS 在 AWS 中的運作](./articles/DNS在幹啥.md)
- [內網通訊機制詳解](./articles/內網是啥.md)
- [NAT 在雲端架構設計中的缺點](<./articles/NAT 在雲端架構設計中的缺點.md>)
- [混合雲 DNS 解析（Hybrid DNS Resolution）](<./articles/混合雲 DNS 解析 (Hybrid DNS Resolution).md>)

## 快速入門

1. **不了解 AWS 網路？** 先讀：
   - [內網是啥.md](./articles/內網是啥.md)
   - [DNS在幹啥.md](./articles/DNS在幹啥.md)

2. **備考 ANS — 從這裡開始：**
   - [ANS-Cheat-Sheet-中文版.md](./notes/ANS-Cheat-Sheet-中文版.md)（全主題速查）
   - [memo.md](./notes/memo.md)（四層備考架構）

3. **深入特定主題：**
   - PrivateLink → [privateLink.md](./notes/privateLink.md)
   - Direct Connect → [DX知識.md](./notes/DX知識.md)、[DX-backup.md](./notes/DX-backup.md)
   - VPN → [S2S-VPN知識.md](./notes/S2S-VPN知識.md)
   - GWLB 透明防火牆 → [透明防火牆是啥.md](./notes/透明防火牆是啥.md)

## 官方文件資源

### 核心服務
- [AWS VPC 官方文件](https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html)
- [AWS PrivateLink 指南](https://docs.aws.amazon.com/vpc/latest/privatelink/what-is-privatelink.html)
- [AWS Direct Connect 文件](https://docs.aws.amazon.com/directconnect/latest/UserGuide/getting_started.html)
- [AWS VPN 使用者指南](https://docs.aws.amazon.com/vpn/latest/s2svpn/VPC_VPN.html)
- [Transit Gateway 文件](https://docs.aws.amazon.com/vpc/latest/tgw/what-is-transit-gateway.html)
- [Route 53 開發者指南](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/Welcome.html)
- [Elastic Load Balancing](https://docs.aws.amazon.com/elasticloadbalancing/latest/userguide/what-is-load-balancing.html)

### 進階主題
- [Enhanced Networking（ENA）](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/enhanced-networking-ena.html)
- [Elastic Network Interfaces（ENI）](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-eni.html)
- [Network MTU 設定](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/network_mtu.html)
- [Link Aggregation Groups（LAG）](https://docs.aws.amazon.com/directconnect/latest/UserGuide/lags.html)
- [Placement Groups](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/placement-groups.html)
- [AWS CloudFront 開發者指南](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/Introduction.html)
- [AWS WAF 與 DDoS 防護](https://docs.aws.amazon.com/waf/latest/developerguide/ddos-overview.html)

### ANS 備考 Whitepapers
- [Amazon VPC Network Connectivity Options](https://docs.aws.amazon.com/whitepapers/latest/aws-vpc-connectivity-options/welcome.html)
- [AWS Security Best Practices](https://docs.aws.amazon.com/whitepapers/latest/aws-security-best-practices/welcome.html)
- [AWS Best Practices for DDoS Resiliency](https://docs.aws.amazon.com/whitepapers/latest/aws-best-practices-ddos-resiliency/welcome.html)
- [Integrating AWS with Multiprotocol Label Switching (MPLS)](https://d1.awsstatic.com/whitepapers/Networking/integrating-aws-with-multiprotocol-label-switching.pdf)

### 工具
- [AWS IP Address Ranges（ip-ranges.json）](https://ip-ranges.amazonaws.com/ip-ranges.json)

---

**最後更新：** 2026-04-10
