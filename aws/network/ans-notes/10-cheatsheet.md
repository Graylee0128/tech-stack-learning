# ANS-C01 Master Cheat Sheet

> 來源：SkillCertPro AWS Advanced Networking Specialty Master Cheat Sheet，整理成快速複習格式。

---

## 考試範圍（ANS-C01）

| Domain | 佔比 |
|--------|------|
| D1: Network Design | 30% |
| D2: Network Implementation | 26% |
| D3: Network Management and Operation | 20% |
| D4: Network Security, Compliance, and Governance | 24% |

---

## ENI / ENA / Enhanced Networking

### Elastic Network Interfaces (ENI)

- 每個 ENI 可綁定多個 IP，數量依 instance type 而異
- VPC 有 IPv6 CIDR block 時，每個 ENI 可有多個 IPv6 地址
- ENI 可跨 subnet 移動，但**不能跨 AZ**
- 同一 instance 的兩個 ENI 不要放同一 subnet（會造成路由問題），改用 secondary private IP
- Cross-account ENI 需 AWS 白名單，是自動化瓶頸

### Elastic IPs

- 停止被收費的方式：**釋放**或**綁到 running instance**
- 可透過 CLI reclaim 已釋放的 EIP

### Elastic Network Adapter (ENA)

- 支援最高 **20 Gbps**（不同於 ENI）
- 註冊 AMI 時需啟用 ENA Support flag

### Enhanced Networking

- EC2 to EC2 在 placement group 外最高 **5 Gbps**
- Intel 網卡在 placement group 內：**10 Gbps**
- ENA 在 placement group 內：**20 Gbps**

---

## VPC 核心

### VPC 基礎

- CIDR 範圍：/16 ~ /28，使用 `10.0.0.0/8`、`172.16.0.0/12`、`192.168.0.0/16`
- 預設 VPC：`172.31.0.0/16`
- 每個 region 最多 **5 個 IGW**
- 每個 subnet 保留 **5 個 IP**：`.0`(network), `.1`(router), `.2`(DNS), `.3`(reserved), `.255`(broadcast)
- NAT Gateway 需要 Elastic IP
- VPC Peering 支援跨 region
- CloudHub 用於 on-prem → VPC，**不是** VPC ↔ VPC
- 可從 Organizations 用 SCP deny IGW 的 attach
- AWS **不支援** broadcast/multicast（需 VPN overlay + GRE tunnel）
- IPS/IDS 用 agent-based approach，no promiscuous mode

### VPC Gateway Endpoint

- 需要：route table 指向 public IP prefix + DNS resolution
- 從 VPC 外部透過 private VIF 或 VPN 存取時需 proxy
- 無法跨 region 使用 endpoint
- AWS IP 範圍可查 `ip-ranges.json`，變更可訂閱 SNS topic `AmazonIpSpaceChanged`

### VPC Interface Endpoint

- 可在 VPC 間使用 private IP 存取
- 可透過 Direct Connect 存取
- **不能**透過 VPN 或 VPC Peering 存取

### PrivateLink

- 屬於 Interface VPC Endpoint，搭配 **NLB** 使用
- Consumer 端可發起連線，Producer 端**不能**
- 限制：不支援跨 region、僅 IPv4 TCP、需與 AWS 對齊 AZ

---

## Security Groups / NACLs

- SG 最多 50 rules，每個 EC2 最多 5 個 SG（= 250 rules 上限）
- SG **不能** apply 到 Egress Only Gateway 或 NAT Gateway
- Database subnet group 需要至少 **2 個 subnet**
- DDoS 緊急處置：移除 default NACL 暫時切斷流量
- Ephemeral ports **1024–65535** 需在 outbound 規則放行（web server 回應流量）

---

## Direct Connect (DX)

### 基礎

- 每個 VPC 需一個 Virtual Interface (VIF)
- Hosted VIF：給不擁有 DX connection 的帳號使用
- < 1 Gbps → 用 hosted connection
- 每條 connection 每個 DC 一份 LOA；LAG 算一條
- Private VIF 最多 advertise **100 prefixes**
- DX Gateway 可跨 region 存取
- 停止計費唯一方式：**刪除 DX connection**（刪 VIF 不行）
- Private VIF **無法**存取 S3 endpoint

### DX 物理需求

- 需要 BGP + BGP MD5 auth
- 1 Gbps：single mode fibre **1000BASE-LX (1310nm)**
- 10 Gbps：**10GBASE-LR** + 802.1Q VLAN
- Auto-negotiation 必須**關閉**
- 無法更改既有 connection 的 port speed
- BGP advertised routes per route table 上限：**100**
- DX Partner 最低頻寬：**50 Mbps**

### DX 相關協定

- **MED (Multi-Exit Discriminator)**：影響 BGP 路由選擇
- **DSCP (Differentiated Services Code Point)**：L3 QoS 流量分類
- **FEC (Forwarding Equivalence Class)**：MPLS 相關

---

## VPN

### 基礎

- IPSec 使用 **IP protocol 50** + **UDP port 500**
- 提供：加密、傳輸保護、peer 驗證、資料完整性
- CloudWatch 可監控 VPN，但**不能**維持 IPSec tunnel（需另外的 monitoring tool）
- AWS VPN **不支援 128-bit AES**，支援 4-byte ASN

### 路由限制

- Static VPN：最多 **50 routes** IPv4 + 50 IPv6
- Dynamic VPN (BGP)：最多 **100 routes**

### 關鍵限制

- VPN over DX 需要 **Public VIF** 才能存取 VPN endpoint
- VPN **不能**用 S3 endpoint，但可用 Public VIF + VPN
- 高可用 VPN：多個 Customer Gateway + dynamic routing

---

## Routing 決策重點

| 情境 | 解法 |
|------|------|
| 讓 AWS 偏好 VPN 而非 DX | 設定 **more specific route** |
| 2 條 DX 做 active/passive | Passive 端設 **AS_PATH prepending**（path 變長 → 不優先） |
| Higher MED | 使路徑**不被偏好**（但不如 AS_PATH prepending 好用） |
| 2 條 VPN 偏好其一 | **More specific route** |
| DX + VPN 共存，偏好 DX | VPN 端 advertise **less specific prefix** |
| BGP routes > 100 | 用 **route summarization** |
| CloudHub | 多個 Customer Gateway（需 public IP）+ 共用一個 VGW |

### 路由優先級

- More specific CIDR → 更被優先
- AS_PATH 越長 → 越不被優先
- Higher MED → 越不被優先

---

## Link Aggregation Groups (LAG)

- Active/Active 模式
- 可隸屬另一個 LAG，但必須在同一 AWS device
- Layer 2 連線
- 2 條 DX connection 的 LAG → 每個 VIF 有 **1 個 BGP session**

---

## MTU

- Jumbo frame (9001 bytes) 僅限 **VPC 內**，不支援跨 VPC
- 最佳化：兩個 ENI — 外部 MTU 1500 + 內部 MTU 9001
- Instance type 決定最大 MTU
- 檢查 MTU：`tracepath`（需 UDP）
- VPN 和 IGW 流量限制 **1500 MTU**，超過會被 fragment 或丟棄（若設 Don't Fragment flag）

```bash
# 啟用 jumbo frame
sudo ip link set dev eth0 mtu 9001

# 查看 MTU
ip link show eth0 | grep mtu
```

---

## OSI / TCP-IP 層級速查

| 協定/服務 | 層級 |
|-----------|------|
| IPSec | Network / Internet Layer |
| TCP / UDP | Transport Layer |
| DNS / DHCP | Application Layer |
| FTP / SMTP | Application Layer |
| BGP | Application Layer |
| AWS Shield | Network + Transport Layer |

---

## Placement Groups

- 所有 instance 需**同時啟動**
- 可跨 VPC
- 策略：cluster、spread
- **不能**將現有 instance 移入

---

## Route 53

### CNAME vs Alias

| | CNAME | Alias |
|--|-------|-------|
| 費用 | 查詢收費 | AWS 資源查詢**免費** |
| 指向 | 任何 DNS record | 僅 AWS 資源 |
| 可見性 | 標準 DNS | 僅 Console/API |

### 重要細節

- 建立 Hosted Zone 自動產生：**NS record** + **SOA record**
- 固定 nameserver：用 **Reusable Delegation Set**（無法在 Console 建立）
- Health check 可檢查其他 health check，**不支援 UDP**
- VPC 內 instance 取得 public DNS：啟用 `enableDnsHostnames`
- **Shuffle sharding**：分散 hosted zone 到多個 instance 防 DDoS
- **Anycast striping**：多個 instance 回應同一 IP，路由到最近的 server
- **White label servers**：R53 nameserver 名稱 = hosted zone 的 domain name

---

## Elastic Load Balancers

### 通用

- ELB 需要 subnet 至少 **/27**
- Connection draining：min 1 sec / max 1 hr / default **5 min**
- `x-forwarded-for` header 用來在 access log 看到 client IP
- Sticky sessions：ELB Classic + ALB 支援
- Target groups：ALB + NLB 支援

### SSL

- SSL negotiation 需要：Security policy、SSL protocols、SSL ciphers、Server order preference
- 可在 LB 上 terminate SSL

### ELB Classic 特有

- Proxy protocol 僅 Classic（**無法從 Console 啟用**）
- 可用 TCP/443
- 用 Alias record
- Configurable idle timeout
- Log 預設間隔：**60 分鐘**

### WAF 整合

- WAF 支援：CloudFront、**ALB**
- **不支援** ELB Classic

---

## CloudFront

- CloudFront 與 S3 之間**不能用 HTTPS**
- Origin Protocol Policy 設 **Match Viewer** 可同時支援 HTTP/HTTPS
- **Origin Access Identity (OAI)**：建立特殊 CloudFront user → S3 bucket policy 設 read-only
- Signed URL：控制內容過期時間
- Security Group 可設定只開放 **CloudFront IP 範圍**
- 可用 **shared secret custom header** 驗證 origin 請求來源

---

## AWS Workspaces

- 最低 MTU：**1200**
- 子網需求：2 private + 1 public
- 有 **2 個 network interface**
- 使用 Active Directory（Microsoft AD / AD Connector / Simple AD）
- 支援 on-prem **RADIUS** 做 MFA

### Active Directory

- Simple AD **不支援** Microsoft 產品，上限 **5,000 users**
- AD Connector 會造成大量 auth 流量

---

## DDoS / Shield

- DDoS 可以是 TCP 或 UDP
- AWS Shield Advanced 需額外付費
- WAF 初始化建議先用 **monitor mode** 建立 baseline

---

## 網路診斷工具

| 工具 | 用途 |
|------|------|
| `iperf3` | TCP/UDP 速度測試 |
| `ec2-net-utils` | 自動設定網卡（僅 Amazon Linux） |
| `mtr` | traceroute + ping 合體 |
| `hping3` | TCP/UDP/ICMP 封包組裝分析 |
| `tcpdump` | 封包擷取分析 |
| `tracepath` | 檢查 MTU（需 UDP） |

---

## 實際考試常見題型（過來人分享）

1. 在 resiliency / cost / performance / security / compliance 限制下設計架構
2. Network access 類型選擇（proxy、peering、transitive、endpoint）+ 路由 edge case
3. ELB 類型差異比較（大量題目）
4. Direct Connect troubleshooting
5. **Route 53 大量出題** — AWS / on-prem / internet 之間的 DNS 解析排錯
6. Gateway vs Interface endpoint、PrivateLink vs cross-account ENI 選型
7. Multicast / packet sniffing 陷阱、`ip-ranges.json`
8. CloudFront 功能整合與網路 edge case
9. Firewall boundary troubleshooting（大量題目）
10. High performance networking、placement groups
