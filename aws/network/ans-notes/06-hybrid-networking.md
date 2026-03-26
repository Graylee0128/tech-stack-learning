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

**Key Points:**
- 最長前綴永遠優先。
- Equal prefix 時，通常 Static Route 優先於 Prefix List，再優先於 Propagated。
- 在 Propagated routes 中，DX BGP route 優先於 VPN static，再優先於 VPN BGP。
- 若都是 BGP propagated，會再看 `AS_PATH` 與 `MED`。

**⚠️ 考試陷阱:**
- 很多題目故意同時給 DX 與 VPN，想考你 DX 預設比 VPN 更優先。

**✅ 記憶點:**
- `Equal prefix` 時先想 Static，再想 DX propagated，再想 VPN。

## Direct Connect

**What:** DX 是實體專線，把企業機房或營運商網路直接拉到 AWS DX Location。

**When to use:** 高吞吐、低延遲、穩定私網、長期大量傳輸。

**Key Points:**
- DX 是 physical port，不自帶 end-to-end 連線，你通常還要透過 provider/cross-connect。
- 常見速率為 1G / 10G / 100G。
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
