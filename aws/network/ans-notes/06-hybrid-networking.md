# 06 Hybrid Networking

## BGP

**What:** BGP 是 AWS 與 On-prem 之間最重要的動態路由協定。

**When to use:** DX、Dynamic VPN、TGW Connect、Cloud WAN、Hybrid path control。

**Key Points:**
- BGP 使用 TCP/179，交換的是 Prefix 與 Path Attributes。
- Autonomous System 以 ASN 表示；16-bit private ASN 常見範圍是 `64512-65534`。
- 重要路徑屬性：`LOCAL_PREF`、`AS_PATH`、`MED`。
- 一般來說最具體 Prefix 先贏，再比 BGP 屬性。

**Comparison:**
- `LOCAL_PREF` 影響 outbound path，且在 AS 內部傳播。
- `AS_PATH prepend` 常用來影響對方如何回來。
- `MED` 常用來影響鄰居在多條連線中偏好哪條。

**⚠️ 考試陷阱:**
- `LOCAL_PREF` 控制的是你自己出去，不是外部進來。
- `MED` 不是萬能，還要看是否在相同 ASN 比較。

**✅ 記憶點:**
- 出站偏好想 `LOCAL_PREF`。
- 入站偏好 AWS 回你哪條線，多半想 `AS_PATH prepend`。

## Route Priority in AWS

**What:** AWS 路由優先序決定多條候選路由時誰會被選上。

**When to use:** DX + VPN 備援、Static vs Propagated、Hybrid failover 題型。

**Key Points — 路由選擇優先序（由高到低）:**

1. **Longest prefix match**（最具體的 CIDR 永遠優先）
2. **Static route**（手動加的 route entry）
3. **Prefix list reference**（managed prefix list）
4. **Propagated: DX BGP route**
5. **Propagated: VPN static route**
6. **Propagated: VPN BGP route**
7. 若同為 BGP propagated 且 prefix 相同，再比 `AS_PATH`（短優先）→ `MED`（低優先）

**⚠️ 考試陷阱:**
- 很多題目故意同時給 DX 與 VPN，想考你 DX 預設比 VPN 更優先。
- Static route 會蓋過 propagated route，即使 propagated 是更佳路徑。

**✅ 記憶點:**
- 口訣：`Longest → Static → DX → VPN static → VPN BGP`。

## Direct Connect

**What:** DX 是實體專線，把企業機房或營運商網路直接拉到 AWS DX Location。

**When to use:** 高吞吐、低延遲、穩定私網、長期大量傳輸。

**Key Points:**
- DX 是 physical port，不自帶 end-to-end 連線，你通常還要透過 provider/cross-connect。
- Dedicated Connection 速率：1G / 10G / 100G（整個 port 歸你）。
- Hosted Connection 速率：50 Mbps ~ 10 Gbps（透過 APN Partner 取得，適合 sub-1G 或快速啟用）。
- DX 沒有內建加密。
- VIF 類型：Public、Private、Transit。
- Private VIF 連 VGW 或 DXGW；Transit VIF 經 DXGW 連 TGW；Public VIF 可到 AWS 公網服務。
- BFD 可把 failover 時間從 BGP 的數十秒縮短到次秒級。
- MACsec 提供 hop-by-hop L2 加密，但不是 end-to-end。

**Limits / Caveats:**
- Private VIF 經 VGW 時，經典模型是 `1 Private VIF = 1 VGW = 1 VPC`。
- Private VIF 不支援直接存取 Route 53 Resolver `VPC + 2` 與 Gateway Endpoints。
- Prefix advertised over private VIF 有硬限制，超出可能導致介面 idle。

**⚠️ 考試陷阱:**
- 要加密時，MACsec 不等於取代 IPSec；MACsec 是 hop-by-hop。
- `Public VIF` 能到公網 AWS 服務，但不是私有 VPC 資源。

**✅ 記憶點:**
- `Private VIF = private VPC access`
- `Public VIF = AWS public services`
- `Transit VIF = TGW integration`

## DX: Dedicated vs Hosted Connection / LAG

**What:** DX 連線分 Dedicated 與 Hosted 兩種取得方式；LAG 可將多條連線綁定提高頻寬與冗餘。

**When to use:** 選型題（頻寬需求、前置時間、成本）、LAG 聚合題。

**Key Points:**
- **Dedicated Connection**：直接向 AWS 申請，速率 1 Gbps / 10 Gbps / 100 Gbps，你擁有整個 physical port。
- **Hosted Connection**：透過 APN Partner 提供，速率從 50 Mbps 到 10 Gbps 不等，適合不需要整個 port 或需要 sub-1G 速率的場景。
- Dedicated 前置時間通常數週到數月；Hosted 通常更快（取決於 Partner）。
- **LAG（Link Aggregation Group）**：把同一 DX Location 的多條同速率連線綁成一組，使用 LACP。
- LAG 中所有連線必須相同速率、相同 DX Location。
- LAG 可設定 minimum links：低於此數量則整個 LAG 失效。

**Comparison:**
| | Dedicated | Hosted |
|--|-----------|--------|
| 速率 | 1G / 10G / 100G | 50M ~ 10G |
| Port 擁有權 | 你獨占 | Partner 分享 |
| VIF 建立 | 自己建 | Partner 預建或你建 |
| 適用 | 高頻寬、長期 | 低頻寬、快速啟用、PoC |

**⚠️ 考試陷阱:**
- 題目要求「500 Mbps DX」只能選 Hosted Connection，Dedicated 最低 1G。
- LAG 不能混合不同速率的連線。

**✅ 記憶點:**
- `Sub-1G DX` 一定是 Hosted Connection。
- `Aggregate bandwidth at same location` 想 LAG。

## DX Resiliency Patterns

**What:** AWS 官方定義的 DX 高可用架構模式，依照冗餘程度分為四個等級。

**When to use:** 題目問 DX HA、DX 備援設計、RTO/RPO 與成本取捨。

**Key Points:**
- **Maximum Resiliency**：2 個 DX Location × 每個 Location 各 2 條連線 = 4 條，能容忍整個 Location 失效且仍有冗餘。
- **High Resiliency**：2 個 DX Location × 每個 Location 各 1 條連線 = 2 條，能容忍單一 Location 失效。
- **Development / Test**：1 個 DX Location × 1 條連線，無冗餘，僅適合非生產環境。
- **DX + VPN Backup**：DX 為主要路徑，S2S VPN 為備援，成本較低但 VPN 頻寬有限（~1.25 Gbps）。
- BFD（Bidirectional Forwarding Detection）可加速故障偵測，將 failover 從 BGP 的數十秒縮短到次秒級。

**Comparison:**
| 模式 | Location 數 | 連線數 | 容錯能力 | 成本 |
|------|------------|--------|---------|------|
| Maximum Resiliency | 2 | 4 | Location 失效 + 連線失效 | 最高 |
| High Resiliency | 2 | 2 | 單一 Location 失效 | 中高 |
| DX + VPN Backup | 1 | 1 DX + VPN | DX 失效（VPN 接手） | 中 |
| Dev/Test | 1 | 1 | 無 | 最低 |

**⚠️ 考試陷阱:**
- 題目若要求「容忍整個 DX Location 失效」，至少需要 High Resiliency（2 locations）。
- DX + VPN backup 時，VPN 頻寬遠低於 DX，不適合需要 full bandwidth failover 的場景。

**✅ 記憶點:**
- `Production critical` 至少 High Resiliency（2 locations）。
- `Cost-sensitive backup` 想 DX + VPN。

## Direct Connect Gateway (DXGW)

**What:** DXGW 是全球性的邏輯閘道，讓一條 DX 連線可以跨 Region 存取多個 VPC 或 TGW。

**When to use:** 多 Region VPC 存取、DX 與 TGW 整合、避免每個 Region 都拉獨立 DX。

**Key Points:**
- DXGW 本身是全球資源，不屬於任何 Region。
- 一個 DXGW 可關聯多個 VGW（不同 Region 的 VPC）或一個 TGW。
- Private VIF 連 DXGW → DXGW 連 VGW，實現跨 Region 私網存取。
- Transit VIF 連 DXGW → DXGW 連 TGW，實現跨 Region transit。
- DXGW 不做 transitive routing：VGW-A 和 VGW-B 都掛在同一個 DXGW，但 VPC-A 和 VPC-B 不能透過 DXGW 互通。
- DXGW 本身免費，計費在 DX port 與 data transfer。

**Comparison:**
- Private VIF → DXGW → VGW：適合少量 VPC，每個 VPC 獨立路由。
- Transit VIF → DXGW → TGW：適合大量 VPC，TGW 統一管理路由。

**Limits / Caveats:**
- 一個 DXGW 最多關聯 10 個 VGW 或 3 個 TGW（可申請提高）。
- DXGW 不能同時關聯 VGW 和 TGW。
- Allowed prefixes 需要手動設定，控制哪些 CIDR 會被公告。

**⚠️ 考試陷阱:**
- DXGW 不提供 VPC-to-VPC 的 transitive routing，要互通仍需 Peering 或 TGW。
- Transit VIF 只能連 DXGW，不能直接連 TGW。

**✅ 記憶點:**
- `Cross-region DX access` 想 DXGW。
- `DX + TGW` 一定經過 Transit VIF → DXGW → TGW。

## VGW / Site-to-Site VPN / IPSec / Client VPN

**What:** 這組服務處理傳統 VPC 對 On-prem 與使用者遠端接入。

**When to use:** 快速 Hybrid 連線、DX 備援、使用者遠端接入。

**Key Points:**
- VGW 一次只能掛一個 VPC，但可作為 DX 與 S2S VPN 的終止點。
- VGW 支援 route propagation 到 VPC route table，這是與 TGW 很重要的差異。
- S2S VPN 可 Static 或 Dynamic；Dynamic 透過 BGP 提供更好的 HA 與路由彈性。
- VPN 常見速率上限約 1.25 Gbps，且有加密開銷。
- Accelerated VPN 只適用 TGW attachment，不適用 VGW。
- NAT-T 用 UDP/4500，解決 Customer Gateway 位於 NAT 後方。
- Client VPN 是 OpenVPN-based managed service，支援 split tunnel 與多種身份驗證。

**⚠️ 考試陷阱:**
- `Accelerated VPN` 只能搭 TGW。
- `Split tunnel` 在 Client VPN 預設不是開的。

**✅ 記憶點:**
- `Quick encrypted hybrid` 想 S2S VPN。
- `End-user remote access` 想 Client VPN。

## VPN CloudHub

**What:** VPN CloudHub 是利用 VGW 作為 hub，讓多個遠端站點（Customer Gateways）透過 AWS 互通的架構模式。

**When to use:** 多個 On-prem 站點需要透過 AWS 互相通訊、低成本 hub-and-spoke WAN。

**Key Points:**
- 多個 Customer Gateway 連到同一個 VGW，每個 site 使用不同 BGP ASN。
- 站點間流量走 VGW 做 transit（hub-and-spoke）。
- 本質上是多條 S2S VPN 共用一個 VGW 的拓樸。
- 流量經公網加密傳輸，不需要 DX。

**Comparison:**
- CloudHub 適合少量站點、低成本；TGW 適合大量站點與更複雜的路由控制。
- CloudHub 用 VGW 做 hub；TGW 本身就是更強大的 hub。

**⚠️ 考試陷阱:**
- CloudHub 不是獨立的 AWS 服務，而是一種架構模式（多 CGW → 單一 VGW）。
- 每個 site 必須使用不同 BGP ASN。

**✅ 記憶點:**
- `Multiple remote sites need to talk via AWS without DX` 想 VPN CloudHub。

## Transit Gateway

**What:** TGW 是 AWS 的 Regional Hub-and-Spoke transit service。

**When to use:** 大量 VPC 互聯、Hybrid transit、中央 egress、中央檢查。

**Key Points:**
- TGW 支援 VPC、VPN、DXGW attachment，並支援 transitive routing。
- Attachments 只會關聯一張 TGW Route Table，但可 Propagate 到多張。
- 預設所有 attachment 會互通，隔離要靠多張 TGW Route Table 做關聯與傳播控制。
- TGW Peering 跨區可行，但不自動傳播路由，需要 static route。
- Appliance Mode 可維持 stateful appliance 所需的對稱流量。
- TGW Connect 透過 GRE + BGP 連第三方虛擬設備或 SD-WAN。

**⚠️ 考試陷阱:**
- TGW peering 不像普通 attachment 會自動學路由。
- Security Group reference 是 VPC Peering 的優勢，TGW 不支援。

**✅ 記憶點:**
- `Many VPCs + Hybrid` 首選 TGW。

## Cloud WAN

**What:** Cloud WAN 是全球層級、政策驅動的 WAN 管理服務。

**When to use:** 多區域、多帳號、混合雲 WAN 簡化與集中治理。

**Key Points:**
- 以 Core Network Policy 為核心，透過 JSON 定義 segments、edge locations、attachment policies。
- 可連 VPC、VPN、Connect、TGW route table，並用 Network Manager 觀察。
- Segment 是邏輯 routing domain。
- 可直接與 DX Gateway 整合，但對 BGP community 與 static route 有限制。

**⚠️ 考試陷阱:**
- Cloud WAN 常搭配 Network Manager；題目會用 segment/attachment policy 語意出題。

**✅ 記憶點:**
- `Global multi-region segmentation` 想 Cloud WAN。

## Global Accelerator

**What:** Global Accelerator 透過 Anycast IP + AWS Global Network，讓使用者更快到達你的應用。

**When to use:** TCP/UDP 全球入口、快速故障切換、非 HTTP 應用加速。

**Key Points:**
- 提供 2 個 Anycast IP。
- 流量先進最近的 Edge，再走 AWS backbone 到健康 endpoint。
- 不快取內容，支援 TCP/UDP。
- Custom Routing Accelerator 可把不同連線確定導向特定 EC2 目標。

**⚠️ 考試陷阱:**
- 題目若要求非 HTTP、固定 Anycast IP、快速區域切換，通常是 GA，不是 CloudFront。

**✅ 記憶點:**
- `Need performance without caching` 想 Global Accelerator。

---

## Quick Reference: Hybrid Connectivity 比較表

| 特性 | Direct Connect | Site-to-Site VPN | TGW + VPN | TGW + DX |
|------|---------------|-----------------|-----------|----------|
| **連線類型** | 專線（實體） | 公網加密隧道 | 公網加密隧道 | 專線（實體） |
| **頻寬** | 1G / 10G / 100G（Dedicated）；50M~10G（Hosted） | ~1.25 Gbps per tunnel | ~1.25 Gbps per tunnel（可 ECMP 聚合至 ~50 Gbps） | 同 DX |
| **延遲** | 低且穩定 | 受公網影響，不穩定 | 同 VPN，Accelerated VPN 可改善 | 同 DX |
| **加密** | 無內建（可疊加 IPSec over DX 或 MACsec） | IPSec 內建 | IPSec 內建 | 同 DX |
| **建置時間** | 數週~數月 | 數分鐘 | 數分鐘 | 數週~數月 |
| **冗餘** | 需自行規劃（Resiliency Patterns） | 預設 2 tunnels | 預設 2 tunnels per attachment | 需自行規劃 |
| **Transitive routing** | 不支援（需 DXGW + TGW） | 不支援（VGW 模式） | 支援 | 支援（經 TGW） |
| **成本** | Port-hour + Data out | VPN connection-hour + Data out | TGW attachment + Data processing + VPN | TGW attachment + Data processing + DX |
| **典型場景** | 長期高頻寬、穩定延遲 | 快速啟用、備援、PoC | 多 VPC hub-and-spoke、ECMP 聚合 | 大規模 Hybrid + 多 VPC |
