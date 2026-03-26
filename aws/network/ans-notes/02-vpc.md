# 02 VPC

## VPC Core

**What:** VPC 是 AWS 區域級、隔離的虛擬網路。

**When to use:** 幾乎所有 AWS Networking 題目的基礎。

**Key Points:**
- VPC 是 Regional service，跨 AZ 提供邏輯網路。
- Primary IPv4 CIDR 建立時指定，範圍約 `/16` 到 `/28`。
- 可追加 Secondary IPv4 CIDR，IPv6 則通常配置 `/56` 給 VPC，再切 `/64` 到子網。
- VPC 預設沒有任何對外連線能力，需明確加上 IGW、VPN、DX、TGW、Endpoints 等。

**Limits / Caveats:**
- AWS 在每個 Subnet 會保留 5 個 IP。
- IPv6 在 VPC 中都是可路由位址，但是否可達仍取決於 Route 與 Security Controls。

**⚠️ 考試陷阱:**
- VPC 是區域級，不是 AZ 級；Subnet 才是 AZ 級。

**✅ 記憶點:**
- `VPC = regional boundary`, `Subnet = AZ boundary`。

## DNS / DHCP / VPC Router

**What:** VPC 內建 DNS、DHCP 與虛擬路由器是所有 EC2 與私網服務通信的基礎。

**When to use:** VPC DNS、Hybrid DNS、Hostname、DHCP Option Set、Route propagation 題型。

**Key Points:**
- AmazonProvidedDNS 位於 VPC Base CIDR `+2` 位址。
- `enableDnsSupport` 控制 DNS resolution；`enableDnsHostnames` 控制 public hostname 行為。
- DHCP Option Set 可指定 DNS、NTP 等，但建立後內容不能改，只能換關聯。
- VPC Router 是 HA、Managed、Regional 的虛擬路由器。
- 每個 Subnet 的 `network + 1` 是預設 Gateway。

**⚠️ 考試陷阱:**
- DHCP Option Set 切換是立即生效於 VPC 關聯，但既有主機通常要等 DHCP renew 才拿到新設定。

**✅ 記憶點:**
- `+1` 想 Gateway，`+2` 想 AmazonProvidedDNS。

## Subnets / Route Tables / IGW / Egress-only IGW

**What:** Subnet 決定 AZ 邊界，Route Table 決定流量去向，IGW/EOIGW 決定對外模式。

**When to use:** 公私子網、IPv4/IPv6 出網、AZ 失效、Transit 題型。

**Key Points:**
- 一個 Subnet 只能屬於一個 AZ。
- 每個 Subnet 一次只能關聯一張 Route Table。
- Main Route Table 建議盡量保持單純，複雜路由使用 Custom Route Table。
- IGW 提供 IPv4/IPv6 雙向公網連線。
- Egress-only IGW 只用於 IPv6 outbound-only。

**Comparison:**
- IGW 讓外部可主動連入；EOIGW 只允許內部主動發起的 IPv6 連線返回。

**⚠️ 考試陷阱:**
- Public Subnet 不只是有 IGW，還必須有對 IGW 的 route，且實例要有 Public IP。

**✅ 記憶點:**
- `IPv4 private outbound` 用 NAT；`IPv6 outbound only` 用 EOIGW。

## NACL vs Security Group

**What:** 兩者都是 VPC 基礎流量控制，但層次與行為不同。

**When to use:** 題目問 allow/deny、subnet 邊界、return traffic、自我參照。

**Key Points:**
- NACL 關聯在 Subnet，為 Stateless，支援 Allow 與 Deny。
- SG 關聯在 ENI，為 Stateful，只支援 Allow。
- NACL 規則有順序，編號越小越先比對。
- SG 不看順序，所有規則聯集後做允許判斷。

**⚠️ 考試陷阱:**
- NACL 只影響穿越 Subnet 邊界的流量；同一子網內部流量不受 NACL 影響。

**✅ 記憶點:**
- `Subnet + Deny` 想 NACL；`ENI + Stateful` 想 SG。

## Flow Logs / Reachability / Access Analysis

**What:** 這些工具用來觀察或分析 VPC 網路狀態。

**When to use:** 疑難排解、Security posture、Pre-change validation。

**Key Points:**
- Flow Logs 是 Metadata，不含封包內容。
- 可掛在 VPC、Subnet、ENI 層級。
- 可送到 S3、CloudWatch Logs、Firehose。
- Reachability Analyzer 用靜態配置分析能否到達，不送真封包。
- Network Access Analyzer 用來驗證網路是否符合安全政策。

**⚠️ 考試陷阱:**
- 想看封包內容用 Traffic Mirroring，不是 Flow Logs。

**✅ 記憶點:**
- `Metadata` 想 Flow Logs；`Path simulation` 想 Reachability Analyzer。

## IPv6 / BYOIP

**What:** VPC 可同時支援 IPv4 與 IPv6；BYOIP 允許把自有位址空間帶入 AWS。

**When to use:** IPv6 migration、公有位址持有權、EKS IPv6、Global routing。

**Key Points:**
- VPC 可啟用 AWS 提供的 `/56` IPv6 範圍。
- Routing 對 IPv4 與 IPv6 是分開管理。
- IPv6 沒有 NAT 概念。
- BYOIP 需完成 ROA、RPKI/RDAP 等授權流程，讓 AWS 合法代你公告路由。

**⚠️ 考試陷阱:**
- IPv6 all public routable 不等於 all reachable；還要看 route 與 security controls。

**✅ 記憶點:**
- `Need your own IP reputation / portability` 想 BYOIP。

## VPC Endpoints / PrivateLink

**What:** VPC Endpoint 讓你私網存取 AWS 服務或第三方服務，不經公網。

**When to use:** 私網取用 S3、DynamoDB、AWS API、第三方 SaaS、跨帳號私網服務。

**Key Points:**
- Gateway Endpoint 只支援 S3、DynamoDB。
- Gateway Endpoint 透過 Prefix List + Route Table 生效。
- Interface Endpoint 是 ENI，背後基礎是 PrivateLink。
- Interface Endpoint 可綁 SG，支援 Private DNS，支援更多 AWS/第三方服務。
- PrivateLink 可跨帳號提供私網服務，也可經 DX、VPN、Peering 存取。

**Comparison:**
- Gateway Endpoint：Regional、HA、僅 S3/DynamoDB、靠 Routing。
- Interface Endpoint：ENI-based、需每 AZ 建立才高可用、靠 DNS。

**⚠️ 考試陷阱:**
- 從 On-prem 經 VGW 不能用 Gateway Endpoint 存取 S3/DynamoDB，但可透過 Interface Endpoint 存取支援的服務。

**✅ 記憶點:**
- `S3/DynamoDB private access` 先想 Gateway Endpoint。
- `Anything else private` 多半想 Interface Endpoint / PrivateLink。

## VPC Peering

**What:** Peering 是兩個 VPC 間的一對一私網連線。

**When to use:** 小規模互聯、低延遲、低成本、同區或跨區 VPC 通信。

**Key Points:**
- 一條 Peering 只連兩個 VPC。
- 支援同區、跨區、跨帳號。
- 流量私有且加密。
- 必須自行加 Route，CIDR 不能重疊。
- Same-region 可互參 SG；cross-region 不行。

**⚠️ 考試陷阱:**
- `A-B peered` 且 `B-C peered` 不代表 `A-C` 可通。

**✅ 記憶點:**
- 小規模、低 hop、低成本想 Peering；大量互聯想 TGW。

## EC2 Networking / Performance / Placement

**What:** EC2 網路能力建立在 ENI、IP、SR-IOV、Placement Group 與附加功能之上。

**When to use:** 高效能網路、HPC、HA、Network appliances、EKS Node networking。

**Key Points:**
- Primary ENI 不能移除；Secondary ENI 可搬移。
- Security Group 綁在 ENI，不是綁在 Instance 本體。
- Source/Destination Check 對 NAT instance、appliance 很重要，常需關閉。
- ENA/SR-IOV 提供 enhanced networking。
- EFA 適合 HPC/ML，支援 OS bypass。
- Cluster Placement Group 提供最高效能；Spread 提供最高隔離；Partition 適合大量節點拓樸感知工作負載。

**⚠️ 考試陷阱:**
- 要讓 appliance 轉送非自身為來源/目的的封包，必須關閉 Source/Destination Check。

**✅ 記憶點:**
- `High PPS / low latency` 想 ENA、Placement Group、EFA。

## Traffic Mirroring

**What:** Traffic Mirroring 把 ENI 流量鏡像到監控或安全設備。

**When to use:** IDS/IPS、封包分析、深度疑難排解。

**Key Points:**
- 使用 VXLAN；若經 GWLB 則涉及 GENEVE。
- Mirror target 可是 ENI、NLB、GWLB。
- Flow Logs 看不到 Mirrored traffic 的 payload。

**⚠️ 考試陷阱:**
- 看內容不是 Flow Logs，要用 Traffic Mirroring。

**✅ 記憶點:**
- `Need packet-level inspection` 想 Mirroring。
