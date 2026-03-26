# 09 Cost DR Governance

## VPC / TGW / DX Cost

**What:** 網路成本主要來自 Attachment、NAT、跨 AZ、跨 Region 與資料傳輸。

**When to use:** 架構選型、成本最佳化、集中式網路設計。

**Key Points:**
- NAT Gateway 有每小時計費與資料處理費。
- VPC 內同 AZ 私網流量通常免費；跨 AZ 常會計費。
- 同一 VPC 內若用 Public IP 互通，可能因繞 IGW 而產生成本。
- VPC Peering 同 AZ 流量通常免費；跨 AZ/跨 Region 會計費。
- TGW 對 Attachment 與資料處理都收費；跨區 Peering 另有區域傳輸費。
- DX 有 Port-hour fee 與 Outbound data transfer fee；DX Gateway 本身免費。

**⚠️ 考試陷阱:**
- 架構上「看起來都是私網」不代表沒有跨 AZ 成本。

**✅ 記憶點:**
- 成本題先想：`NAT`、`cross-AZ`、`cross-Region`、`TGW data processing`。

## Disaster Recovery

**What:** DR 是在成本、RTO、RPO 之間做取捨的架構設計。

**When to use:** 多 Region 容災、備援、商業持續性題型。

**Key Points:**
- Backup & Restore 最便宜，但 RTO 最長。
- Pilot Light 保留最小核心元件，平時成本低、恢復中等。
- Warm Standby 長期保留縮小版環境，恢復快於 Pilot Light。
- Active/Active 成本最高，但可接近零恢復時間。
- Storage 面向要看 EBS Snapshot、S3、EFS 的區域/多 AZ 特性。
- Compute 面向要看 ASG、ECS/Fargate、Lambda 在多 AZ/多 Region 的部署。
- Database 面向要看 RDS Multi-AZ、Aurora、DynamoDB Global Tables、Aurora Global Database。
- Network 面向要看 Route 53 Failover、ELB、多區入口。

**⚠️ 考試陷阱:**
- Multi-AZ 不等於 Multi-Region DR。

**✅ 記憶點:**
- `Cheap and slow` 是 Backup。
- `Fast and expensive` 是 Active/Active。

## IPAM

**What:** IPAM 用來集中管理私網與公網位址空間。

**When to use:** 多帳號多區域 CIDR 治理、VPC CIDR 發號施令、避免衝突。

**Key Points:**
- IPAM 有 Public 與 Private Scope。
- Pool 可分層配置，從大 Pool 切出子 Pool 再配給 VPC。
- 可與 Organizations 整合。
- 可搭配 SCP 強制 VPC 從 IPAM Pool 取 CIDR。
- 可追蹤位址使用量、歷史與 Public IP Insights。

**⚠️ 考試陷阱:**
- 免費層與進階層功能不同，Private IP Pool 管理常需 Advanced tier。

**✅ 記憶點:**
- `Avoid overlapping CIDR at scale` 想 IPAM。

## AWS Network Manager

**What:** Network Manager 是集中查看 Cloud WAN、Global Network、Reachability、IPAM 等網路治理入口。

**When to use:** 需要統一可視化與跨服務網路治理。

**Key Points:**
- 可作為 Cloud WAN 與 Global Network 的操作/觀察入口。
- 可整合 Reachability Analyzer、Network Access Analyzer、IPAM。

**⚠️ 考試陷阱:**
- Network Manager 偏 Dashboard/管理層，不是資料平面的轉送元件。

**✅ 記憶點:**
- `Central network visibility` 想 Network Manager。
