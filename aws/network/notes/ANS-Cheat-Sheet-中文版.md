# AWS Advanced Networking Specialty — 中文速查表

> 原文來源：SkillCertPro Master Cheat Sheet
> 改編：翻譯為繁體中文，並補充重要細節與考試提示

---

## 考試架構

| Domain | 主題 | 占比 |
|--------|------|------|
| Domain 1 | 設計並實作大規模混合 IT 網路架構 | 23% |
| Domain 2 | 設計並實作 AWS 網路 | 29% |
| Domain 3 | 自動化 AWS 任務 | 8% |
| Domain 4 | 設定網路與應用服務的整合 | 15% |
| Domain 5 | 設計並實作安全性與合規 | 12% |
| Domain 6 | 管理、優化與排除網路問題 | 13% |

---

## Elastic Network Interfaces（ENI）彈性網路介面

[官方文件](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-eni.html)

- 每個 ENI 可綁定多個 IP（數量上限依 instance type 而異）
- 如果 VPC 有 IPv6 CIDR block，ENI 也可以有多個 IPv6 地址
- ENI **可以在同 AZ 的子網之間移動**，但**不能跨 AZ 移動**
- 在同一個子網中將兩個 ENI 附加到同一個 instance 可能造成路由問題；建議改用主 ENI 的第二個 IPv4 地址
- 跨帳號 ENI 需要 AWS 手動白名單，可能造成自動化瓶頸

> 💡 考試重點：ENI 搬遷限制（同 AZ 可以、跨 AZ 不行）

---

## Elastic IPs（EIP）彈性 IP

[官方文件](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/elastic-ip-addresses-eip.html)

- 停止被收費的方式（兩者擇一）：
  - 從帳號中 **Release** 掉
  - 把 EIP 關聯到一個 **正在執行的 instance**（非 stopped）
- 可透過 CLI 重新申領（reclaim）已釋放的 EIP

---

## Elastic Network Adapters（ENA）彈性網路轉接器

[官方文件](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/enhanced-networking-ena.html)

- ENA（Elastic Network Adapter）支援最高 **20 Gbps**（與 ENI 不同，ENI 是虛擬介面，ENA 是驅動層）
- 在 AMI 上要使用 ENA，**需在 AMI 註冊時啟用 ENA Support 旗標**

> 💡 ENA vs ENI 區分：ENI 是 VPC 層的虛擬網路介面；ENA 是底層的高速網路驅動程式

---

## Enhanced Networking 增強型網路

[官方文件](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/enhanced-networking.html)

- EC2 to EC2 在 **Placement Group 外**：最高 **5 Gbps**
- 使用 Intel 網路介面（SR-IOV）在 Placement Group 內：最高 **10 Gbps**
- 使用 ENA 在 Placement Group 內：最高 **20 Gbps**

| 網路類型 | 上限 |
|---------|------|
| 一般 EC2-to-EC2（無 PG） | 5 Gbps |
| Intel SR-IOV + Placement Group | 10 Gbps |
| ENA + Placement Group | 20 Gbps |

---

## VPC Gateways（Internet Gateway / S3、DynamoDB Gateway Endpoint）

[官方文件](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Internet_Gateway.html)

**Internet Gateway 需求：**
- Route table 需有指向公有 IP 的路由條目
- VPC 要啟用 DNS resolution
- 若從 Private VIF 或 VPN 出去，需要 Proxy 設定

**重要細節：**
- VPC endpoint 無法跨 Region 連接其他 Region 的服務
- AWS 維護所有 Gateway 服務的 IP 清單：
  - 檔案：[`ip-ranges.json`](https://ip-ranges.amazonaws.com/ip-ranges.json)
  - 當 IP 範圍變動時，可訂閱 SNS Topic `AmazonIpSpaceChanged` 接收通知
- 一個 Region **最多 5 個 Internet Gateway**
- Internet Gateway 可被 AWS Organizations SCP 政策拒絕附加

> 💡 考試技巧：看到「監控 AWS 服務 IP 變更」→ `ip-ranges.json` + SNS `AmazonIpSpaceChanged`

---

## VPC Interfaces（Interface VPC Endpoints）

[官方文件](https://docs.aws.amazon.com/vpc/latest/privatelink/vpce-interface.html)

- 可透過**私有 IP** 在 VPC 之間存取
- 可透過 **Direct Connect** 存取
- **不可**透過 VPN 或 VPC Peering 存取

---

## PrivateLink

[官方文件](https://docs.aws.amazon.com/vpc/latest/privatelink/what-is-privatelink.html)

- 是 Interface VPC Endpoint 的一種，背後使用 **Network Load Balancer**
- **單向**：Consumer 可以發起連線，Producer 端**無法**主動發起
- **限制：**
  - 不支援跨 Region 存取（2024 後有條件支援 NLB 類型）
  - 只支援 **IPv4 + TCP**
  - 需要與 AWS 確認 AZ 對齊（AZ alignment）才能建立 Interface Endpoint

> 💡 考試速記：看到「SaaS 多租戶、數百客戶、IP 衝突、複雜 NAT」→ 答案是 **PrivateLink**

---

## VPCs

[官方文件](https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html)

**CIDR 範圍：**
- VPC 可用 `/16` 到 `/28`
- 只能使用私有 IP 範圍：`10.0.0.0/8`、`172.16.0.0/12`、`192.168.0.0/16`
- 預設 VPC 使用 `172.31.0.0/16`（可重新建立）

**每個子網保留 5 個 IP：**

| 地址 | 用途 |
|------|------|
| `.0` | 網路地址 |
| `.1` | VPC Router |
| `.2` | DNS（只用 VPC 的 .2） |
| `.3` | 保留供 AWS 未來使用 |
| `.255` | 廣播地址（AWS 不使用，但仍保留） |

**其他重點：**
- NAT Gateway 需要 Elastic IP
- VPC Peering 支援**跨 Region**
- Cloudhub 是用來連接地端到 VPC，**不允許** VPC to VPC Peering
- AWS **不支援 broadcast / multicast**；如需實作只能透過 VPN overlay（GRE tunnel）
- IDS/IPS 使用 **agent-based 方式**（不支援 promiscuous mode）

> 💡 CIDR 計算：子網 host 數 = 2^(32-prefix) - 5（扣掉 5 個保留地址）

---

## EC2

[官方文件](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-networking.html)

| 操作 | Public IP 行為 |
|------|--------------|
| **Reboot**（重啟，不換實體機） | **保留** Public IP，且留在同一台實體主機 |
| **Stop → Start**（停止後再啟動） | **失去** Public IP（除非使用 EIP） |

- 如果 EC2 要當郵件伺服器，要先通知 AWS 該 IP（避免被判定為 spam）

---

## Security Groups / NACLs

[官方文件](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html)

**Security Group 限制：**
- 每個 SG 最多 **50 條規則**
- 每個 EC2 instance 最多 **5 個 SG**（可申請提高到 250 條規則）
- SG **不能**套用在 **Egress Only Gateway** 或 **NAT Gateway** 上
- SG 只能設定 **Allow rule**，無法設定 Deny

**NACL 重點：**
- Stateless：回程流量需要明確規則
- Custom NACL 預設全 Deny，Default NACL 預設全 Allow
- **DDoS 緊急應對**：移除 Default NACL 可暫時切斷所有流量
- **Ephemeral ports 1024–65535**：Web Server 需要在防火牆開放 outbound

**資料庫：**
- Database subnet group 需要**至少 2 個子網**（通常跨 2 個 AZ）

---

## Direct Connect 與 Virtual Interfaces

[官方文件](https://docs.aws.amazon.com/directconnect/latest/UserGuide/getting_started.html)

**VIF 類型：**
- **Private VIF**：連接 VPC（每個 VPC 需要一個 VIF）
- **Public VIF**：連接 AWS 公共服務（S3 public endpoint 等）
- **Transit VIF**：連接 Transit Gateway
- **Hosted Virtual Interface**：供**不同帳號**使用（與擁有 DX 的帳號不同）

**重要細節：**
- Sub 1Gbps → 使用 **Hosted Connection**（透過 DX Partner）
- 每個資料中心每條連接一份 **LOA**（Letter of Authorization）；LAG 算一份
- Private VIF **最多廣播 100 個 prefix**
- **DX Gateway** 可讓一條 DX 連接到**多個 Region**
- 停止計費的唯一方式：**刪除 DX Connection**（只刪 VIF 不夠）
- Private VIF **不能存取 S3 Gateway Endpoint**（需用 Interface Endpoint 或 Public VIF）
- CloudWatch 監控 DX：`aws cloudwatch list-metrics --namespace "AWS/DX"`

**BGP 路由優先級工具：**
- **MED（Multi-Exit Discriminator）**：數值越高越不被優先選擇；比 AS_PATH Prepending 效果差
- **AS_PATH Prepending**：增加路徑長度使其不被優先選擇（Active/Passive 首選工具）
- **DSCP（Differentiated Services Code Point）**：Layer 3 的 QoS 流量分類

---

## DX 物理規格需求

[官方文件](https://docs.aws.amazon.com/directconnect/latest/UserGuide/physicalConnections.html)

| 項目 | 規格 |
|------|------|
| 路由協定 | BGP + BGP MD5 認證 |
| 1 Gbps 光纖 | Single-mode fiber 1000BASE-LX（1310nm） |
| 10 Gbps 光纖 | 10GBASE-LR，使用 802.1q VLANs |
| Auto-negotiation | **必須停用**（Disable） |
| Port 速率 | 建立後**不可更改** |
| BGP 每個路由表廣播上限 | **100 條路由** |
| DX Partner 最低頻寬 | **50 Mbps** |

> 💡 考試陷阱：「DX 燈不亮」→ 檢查 Auto-negotiation 是否已 Disable

---

## VPN（Site-to-Site）

[官方文件](https://docs.aws.amazon.com/vpn/latest/s2svpn/VPC_VPN.html)

**協定基礎：**
- IPSec + ESP（Encapsulating Security Protocol）
- IP Protocol **50**；UDP Port **500**（IKE）

**VPN 提供：**
- 網際網路上的資料加密
- Peer ID 身份認證（VPN Gateway ↔ Customer Gateway）
- 傳輸中的資料完整性

**路由限制：**
| 類型 | IPv4 路由上限 | IPv6 路由上限 |
|------|------------|------------|
| Static VPN | 50 | 50 |
| Dynamic VPN（BGP） | 100 | — |

**重要細節：**
- CloudWatch 可監控 VPN **指標**，但**無法**維持 IPSec tunnel 的存活（需要另外的監控工具）
- AWS VPN **不支援 128-bit AES**，**支援 4-byte ASN**
- 要在 DX 上跑 VPN，需要使用 **Public VIF** 才能到達 VPN endpoints
- HA 設計：使用多個 Customer Gateway + Dynamic routing（BGP）
- **不能**透過 VPN 使用 S3 endpoint；可以用 Public VIF + VPN

---

## 路由場景（Routing Scenarios）

**優先級規則：**
- **Longest Prefix Match**：更具體的路由（如 /24）優先於 /16
- DX vs VPN 選路：更具體的路由是讓 AWS 選 VPN over DX 的**唯一方式**
- 2 條 VPN 要讓其中一條優先 → 設定**更具體的路由**

**AS_PATH Prepending：**
- Active/Passive 設計：在 passive 那條 DX 上做 AS_PATH Prepending（路徑變長 → 不被優先選）
- MED 數值越高越不被優先（但 AS_PATH Prepending 更常用）

**Public VIF 特性：**
- 可以存取**不只連接那個 Region** 的公共服務
- 限制：僅 North America，需透過 BGP 廣播 non-local public ranges

**CloudHub：**
- 用多個 Customer Gateway（各有公有 IP）
- 每個 CGW 都建立一條 VPN 連接到同一個 Virtual Private Gateway
- 功能：讓多個地端站點透過 AWS 骨幹互相通訊

**BGP 路由超過 100 條：**
- 做 **Route Summarization**（路由聚合）

---

## Link Aggregation Groups（LAG）

[官方文件](https://docs.aws.amazon.com/directconnect/latest/UserGuide/lags.html)

- LAG 以 **Active/Active** 模式運作（不是 Active/Passive）
- LAG 可以是另一個 LAG 的成員，但**必須在同一台 AWS 設備上**
- LAG 是 **Layer 2** 連接
- 一個 LAG 上有 2 條 DX 連接 → 每個 VIF 有 **1 個 BGP session**

> 💡 MACsec + LAG：MACsec 設定在 LAG 層級，自動套用到所有成員連接；需要支援 MACsec 的新硬體（不能線上升級）

---

## Maximum Transmission Units（MTU）

[官方文件](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/network_mtu.html)

| 場景 | MTU 上限 |
|------|---------|
| VPC 內部（Jumbo Frames） | **9,001 bytes** |
| VPC 之間（inter-VPC） | 1,500 bytes |
| VPN / Internet Gateway | **1,500 bytes**（超過會被切割或丟棄） |
| AWS Workspaces | 最低需 1,200 bytes |

**最大化效能：**
- 準備兩個 ENI：外部用 MTU 1,500；內部用 MTU 9,001

**常用指令：**
```bash
# 設定 Jumbo Frames
sudo ip link set dev eth0 mtu 9001

# 查詢目前 MTU
ip link show eth0 | grep mtu

# 測試兩台主機間 MTU（需要 UDP）
tracepath <target-ip>
```

> 💡 `tracepath` 來自 `iputils` 套件；需要 UDP 才能運作

---

## OSI Layers / IP Suite

[OSI 參考](https://en.wikipedia.org/wiki/OSI_model)

| 協定 | OSI 層 |
|------|--------|
| IPSec | Layer 3（網路層） |
| TCP / UDP | Layer 4（傳輸層） |
| DNS / DHCP | Layer 7（應用層） |
| FTP / SMTP | Layer 7（應用層） |
| BGP | Layer 7（應用層） |
| AWS Shield | Layer 3 + Layer 4 |
| MACsec | Layer 2（資料連結層） |

> 💡 考試常考：BGP 是 Layer 7（很多人誤以為是 Layer 3）

---

## Placement Groups

[官方文件](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/placement-groups.html)

- 所有 instance 必須**同時啟動**（不能分批加入）
- 可以**跨 VPC**
- 部署策略：**Cluster**（最低延遲）、**Spread**（最高可用性）、**Partition**（大型分散式系統）
- **不能**把現有 instance 移入 Placement Group（必須重新啟動）

---

## Route 53

[官方文件](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/Welcome.html)

**CNAME vs Alias 比較：**

| 項目 | CNAME | Alias |
|------|-------|-------|
| 費用 | 每次查詢收費 | **免費**（對 AWS 資源） |
| 指向對象 | 任何 DNS 記錄 | **只能是 AWS 資源** |
| 可見性 | 公開 | 只透過 Console 或 API 可見 |
| Zone Apex 支援 | ❌ | ✅ |

**路由策略：**

| 策略 | 說明 |
|------|------|
| Simple | 無條件回傳，適合單一目標 |
| Weighted | 按比例分流（A/B Test） |
| Latency | 導向延遲最低的 Region |
| Geolocation | 按用戶地理位置 |
| Geoproximity | 按地理距離（可偏移） |
| Failover | 主掛了自動切備援 |
| Multivalue | 回傳多個 IP + Health Check |

**其他重要細節：**
- 建立 Hosted Zone 時自動產生：**NS 記錄** + **SOA 記錄**
- 要固定使用特定 name server → 在 API 建立 **Reusable Delegation Set**（Console 無法建立）
- Route53 Health Check 可以**檢查其他 Health Check**（hierarchical）
- Route53 **不支援 UDP Health Check**（支援 HTTP/HTTPS/TCP）
- VPC 內的 instance 要有公有 DNS 名稱 → 啟用 `enableDnsHostnames`
- **Shuffle Sharding**：將 Hosted Zone 分散到多個 instance，減緩 DDoS 影響
- **Anycast Striping**：多個 instance 回應同一 IP，用戶自動導向最近的 anycast server
- **White Label Servers**：Route 53 的 name server 與 hosted zone 的 domain name 相同

---

## Elastic Load Balancers（ELB）

[官方文件](https://docs.aws.amazon.com/elasticloadbalancing/latest/userguide/what-is-load-balancing.html)

**基本規格：**
- ELB 需要 **最小 /27 子網**
- Connection Draining（連接排空）：最短 1 秒、最長 1 小時、預設 **5 分鐘**

**三種 ELB 類型比較：**

| 功能 | Classic（CLB） | Application（ALB） | Network（NLB） |
|------|------------|----------------|--------------|
| Target Group | ❌ | ✅ | ✅ |
| WAF 整合 | ❌ | ✅ | ❌ |
| Sticky Session | ✅ | ✅ | — |
| X-Forwarded-For | ✅ | ✅ | ❌ |
| Proxy Protocol | ✅（只有 Classic，且不能從 Console 設定）| ❌ | ✅ |
| SSL/TLS | ✅ | ✅ | ✅ |
| Log 預設間隔 | **60 分鐘** | — | — |

**SSL 協商：** 需要設定 Security Policy、SSL Protocols、SSL Ciphers、Server Order Preference

**日誌：**
- 要在 Access Log 中看到 Client 真實 IP → 需要 `X-Forwarded-For` Header

---

## AWS Workspaces

[官方文件](https://docs.aws.amazon.com/workspaces/latest/adminguide/amazon-workspaces.html)

- 最低需要 MTU **1,200 bytes**
- 網路架構：**2 個 Private Subnet + 1 個 Public Subnet**
- 每個 Workspace 有 **2 個網路介面**
- 使用 Active Directory，選項：**Microsoft AD / AD Connector / Simple AD**
- 支援使用地端 **RADIUS** 作為 MFA 驗證

---

## Active Directory

[官方文件](https://docs.aws.amazon.com/directoryservice/latest/admin-guide/what_is.html)

| 類型 | 限制 | 適用場景 |
|------|------|---------|
| Simple AD | < 5,000 users；**不支援 Microsoft 產品** | 輕量 Linux 環境 |
| AD Connector | 不儲存帳號，代理到地端 AD；**認證流量可能過高** | 地端 AD 整合 |
| Microsoft AD（AWS Managed） | 完整 AD 功能 | 企業 Windows 環境 |

---

## CloudFront

[官方文件](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/Introduction.html)

- CloudFront 與 S3 之間**不能使用 HTTPS**（用 HTTP）
- CloudFront 轉發到 S3 的協定，與 viewer 使用的協定相同（Origin Protocol Policy = **Match Viewer**）
- WAF 整合：**WAF → CloudFront**、**WAF → ALB**
- **Origin Access Identity（OAI）**：建立一個 CloudFront 專屬用戶，給予 S3 Bucket 的唯讀權限
- 限時 URL → 使用 **Signed URL**
- Security Group 可設定只允許 **CloudFront 的 IP 範圍**（詳見 ip-ranges.json）
- 自訂 Header 共享密鑰（Custom Header）：在 CloudFront 到 Origin 的請求中加入 secret header

---

## DDoS 與環境防護

[官方文件](https://docs.aws.amazon.com/waf/latest/developerguide/ddos-overview.html)

- DDoS 可以是 **TCP 或 UDP**
- **AWS Shield Standard**：免費，自動保護所有 AWS 客戶
- **AWS Shield Advanced**：付費（約 $3,000/月），提供更高階防護與支援
- WAF 設定初期：先**以 Monitor 模式**建立流量 baseline，再轉換為 Block 模式

---

## Networking Tools（Linux 常用診斷工具）

在 AWS Linux instance 上常用的網路診斷工具：

| 工具 | 用途 |
|------|------|
| `iperf3` | TCP/UDP 效能測速 |
| `ec2-net-utils` | 自動化設定 ENI（僅 Amazon Linux，`yum install ec2-net-utils`） |
| `mtr` | 結合 traceroute + ping 的網路診斷工具 |
| `hping3` | TCP/UDP/ICMP 封包組裝與分析 |
| `tcpdump` | 封包捕捉與分析 |
| `tracepath` | 測試兩台主機間的 MTU（需 UDP） |

---

## 高頻考點速記

> 考場上遇到這些關鍵字，直接對應到答案

| 關鍵情境 | 最佳解法 |
|---------|---------|
| SaaS 多租戶、IP 衝突、複雜 NAT | **PrivateLink** |
| DX Active/Passive 備援 | **AS_PATH Prepending**（passive 那條） |
| VPN over DX | 需要 **Public VIF** |
| S3 Gateway Endpoint + Private VIF | ❌ 不可行；改用 Interface Endpoint 或 Public VIF |
| DX 停止計費 | **刪除 DX Connection**（刪 VIF 不夠） |
| DX 燈不亮 | **Disable Auto-negotiation** |
| Route53 Nameserver 固定 | API 建立 **Reusable Delegation Set**（Console 不行） |
| 監控 AWS IP 範圍變動 | **ip-ranges.json** + SNS `AmazonIpSpaceChanged` |
| DDoS 緊急切斷 | 移除 **Default NACL** |
| CloudFront 限時存取 | **Signed URL** |
| LAG + MACsec | 設定在 **LAG 層級**；需要新硬體（CKN + CAK） |
| Jumbo Frames | VPC 內 9,001B；VPN/IGW 限制 1,500B |
| BGP = OSI 哪層？ | **Layer 7（應用層）** |
| EC2 stop/start 後 IP？ | **失去 Public IP**（除非使用 EIP） |
| Placement Group 無法做什麼？ | 無法把現有 instance **移入** |

---

*最後更新：2026-03-11*
