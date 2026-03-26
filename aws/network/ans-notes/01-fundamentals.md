# 01 Fundamentals

## DNS / Route 53 Basics

**What:** DNS 是把人類可讀名稱轉成機器可用 IP 的分散式命名系統；Route 53 是 AWS 的全球 DNS 與網域服務。

**When to use:** 理解 VPC DNS、Hybrid DNS、Hosted Zone、記錄型別與快取行為時一定會用到。

**Key Points:**
- DNS 核心元件是 Resolver、Zone、Zonefile、Nameserver。
- DNS 是階層式信任模型，Root Zone 只管理頂層網域並把權限委派給下層。
- 常見記錄型別：`A`、`AAAA`、`CNAME`、`MX`、`TXT`、`NS`。
- TTL 影響快取存活時間，TTL 越長，變更生效越慢，但查詢成本與負載通常越低。
- Route 53 可同時扮演 Domain Registrar 與 Hosted Zone Provider。
- Hosted Zone 可分成 Public Hosted Zone 與 Private Hosted Zone。

**Comparison:**
- `A/AAAA` 是名稱對 IP；`CNAME` 是名稱對名稱。
- Public Hosted Zone 對公網可解析；Private Hosted Zone 只對關聯 VPC 可解析。

**Limits / Caveats:**
- Apex domain 不能用 `CNAME`，AWS 以 `ALIAS` 解決指向 ELB、CloudFront 等 AWS 資源的需求。
- Private Hosted Zone 只有關聯的 VPC 才能解析，不是整個 AWS 帳號都能用。

**⚠️ 考試陷阱:**
- `ALIAS` 是 AWS 擴充功能，不是標準 DNS record type。
- VPC 內解析 Public AWS 資源時，可能解析成私網位址，尤其在 VPC 與 Peering 題型很常考。

**✅ 記憶點:**
- DNS 看的是「授權 + 委派 + 快取」。
- Route 53 最常考：Hosted Zone、Routing Policy、Health Check、Alias、Hybrid DNS。

## DDoS

**What:** DDoS 是用大量分散流量癱瘓系統的攻擊模式。

**When to use:** 判斷 Shield、WAF、CloudFront、Global Accelerator 的選型與分層保護時。

**Key Points:**
- DDoS 類型可分成 Application Layer、Protocol、Volumetric/Amplification。
- Application Layer 例如 HTTP Flood。
- Protocol 類型例如 SYN Flood。
- Volumetric 類型例如 DNS Amplification。

**Design Notes:**
- L3/L4 攻擊偏向 Shield。
- L7 攻擊偏向 WAF、Rate-based Rules。

**⚠️ 考試陷阱:**
- 不是所有 DDoS 都靠 WAF；WAF 主要處理 L7。

**✅ 記憶點:**
- L3/L4 想 Shield，L7 想 WAF。

## NAT

**What:** NAT 是將私有 IPv4 與公網 IPv4 之間做位址轉換的機制。

**When to use:** VPC 出網、NAT Gateway、IGW、Egress-only IGW 題型都會用到。

**Key Points:**
- Static NAT 是 1:1 位址轉換；AWS IGW 對 Public IPv4 可視為 1:1 Static NAT。
- Dynamic NAT 是從 Public IP Pool 動態分配。
- PAT 是多個 Private IP 共用一個 Public IP；AWS NAT Gateway 屬於 PAT。
- NAT 的本質是為了解決 IPv4 位址不足，不適用於 IPv6。

**Comparison:**
- NAT Gateway 支援大量私網主機主動連外，但不支援外部主動連入。
- IGW 可提供雙向連線；NAT Gateway 只適合 Outbound initiated traffic。

**⚠️ 考試陷阱:**
- IPv6 不用 NAT Gateway，應改用 IGW 或 Egress-only IGW。

**✅ 記憶點:**
- `IPv4 private outbound only` 想 NAT Gateway。
- `IPv6 outbound only` 想 Egress-only IGW。

## OSI / Transport / Session

**What:** OSI 模型幫助理解 AWS 網路元件位於哪一層，以及各種控制平面到底能看見什麼。

**When to use:** 判斷 NACL、SG、WAF、GWLB、Proxy、TLS termination 題型時。

**Key Points:**
- Layer 1 是實體傳輸；Layer 2 是 MAC/Frame；Layer 3 是 IP Routing；Layer 4 是 TCP/UDP。
- Router 依 Route Table 做 Layer 3 路由，Longest Prefix Match 永遠優先。
- TCP 提供可靠性、重傳、順序控制與 Flow Control；UDP 側重低延遲。
- Stateful firewall 能理解請求與回應屬於同一個 session；Stateless firewall 不行。

**Comparison:**
- NACL 像傳統 Stateless Firewall。
- Security Group 像 Stateful Firewall。
- WAF 是 Layer 7，能理解 HTTP/S 細節。

**⚠️ 考試陷阱:**
- 只看 IP/Port 的裝置無法做 URL Filtering；要用 L7 Proxy/WAF 類產品。

**✅ 記憶點:**
- 「看得到 Session」才談得上 stateful。

## SSL / TLS

**What:** TLS/SSL 提供傳輸加密、完整性與身分驗證。

**When to use:** ACM、ALB、CloudFront、mTLS 題型。

**Key Points:**
- TLS 是 SSL 的新版本。
- 通常先用非對稱加密交換金鑰，再改用對稱加密傳輸資料。
- HTTPS 的價值是機密性、完整性與伺服器身分驗證。

**⚠️ 考試陷阱:**
- 某些 AWS 服務會在自己那端終止 TLS，例如 ALB、CloudFront。

**✅ 記憶點:**
- TLS termination 發生在哪裡，常常就是題目的關鍵。

## VLAN / Trunk / QinQ

**What:** VLAN 透過 802.1Q 標記，把同一個 Layer 2 網路切成多個廣播域。

**When to use:** DX VLAN、VIF、企業網路延伸、QinQ 題型。

**Key Points:**
- VLAN 可建立隔離的 Layer 2 Segment。
- Trunk Port 能承載多個 VLAN。
- QinQ/802.1ad 允許 Provider 疊加額外 Tag，適合營運商情境。

**⚠️ 考試陷阱:**
- VLAN 是 Layer 2 隔離，不是 Layer 3 路由控制。

**✅ 記憶點:**
- DX VIF 本質上就是「VLAN 隔離 + BGP Peering」。

## Jumbo Frames / MTU

**What:** Jumbo Frame 是大於標準 1500 Bytes Ethernet MTU 的大封包，常見值約 9000 Bytes。

**When to use:** DX、TGW、Same-region Peering、高吞吐工作負載。

**Key Points:**
- Jumbo Frames 可降低 Frame overhead，提高有效傳輸效率。
- 路徑上每一跳都要支援足夠 MTU，否則可能 fragmentation 或丟包。
- AWS 中不是所有傳輸路徑都支援 Jumbo Frames。

**Limits / Caveats:**
- VPN、IGW、VPC 對外路徑通常不支援 Jumbo Frames。
- Same-region VPC Peering 可支援；Inter-region Peering 不支援。
- DX 與 TGW 可支援較大 MTU，但題目常特別寫到上限不是無限制。

**⚠️ 考試陷阱:**
- 只要流量「離開 VPC 到公網」通常就不要期待 Jumbo Frames。

**✅ 記憶點:**
- 同區私網路徑比較可能支援 Jumbo；公網與 VPN 類型通常不行。

## Reserved IPv4 Ranges

**What:** 某些 IPv4 區段有特殊用途，不能當成一般公網可路由位址。

**When to use:** CIDR 規劃、Hybrid Routing、Exam elimination。

**Key Points:**
- 私網常見區段：`10.0.0.0/8`、`172.16.0.0/12`、`192.168.0.0/16`。
- `100.64.0.0/10` 是 CGNAT Shared Address Space。
- `127.0.0.0/8` 是 Loopback。
- `169.254.0.0/16` 是 Link-local。
- `224.0.0.0/4` 用於 Multicast。

**⚠️ 考試陷阱:**
- `100.64.0.0/10` 不是 RFC1918，但仍非一般公網位址。

**✅ 記憶點:**
- 題目問 VPC secondary CIDR、EKS custom networking 時，常會看到 `100.64.0.0/10`。
