# 03 Load Balancer

## Elastic Load Balancing Overview

**What:** ELB 是 AWS 的受管負載平衡家族，包含 ALB、NLB、GWLB，以及舊版 CLB。

**When to use:** 對外入口、流量分散、健康檢查、TLS termination、流量導向安全設備。

**Key Points:**
- ELB 是 Regional 服務，會在你選定的多個 AZ 子網中建立節點。
- 建議每個 ELB 子網保留足夠 IP，通常至少 `/27` 比較安全。
- Internet-facing ELB 節點有 Public IP；Internal ELB 只有 Private IP。
- Cross-zone Load Balancing 對流量分配與成本都很重要。

**⚠️ 考試陷阱:**
- ELB 真正是每個 AZ 一組節點，不是一台單一設備。

**✅ 記憶點:**
- ELB 題型先判斷「L7/L4/Appliance」。

## ALB

**What:** ALB 是 Layer 7 Load Balancer，懂 HTTP/HTTPS/WebSocket。

**When to use:** Web 應用、Path/Host-based routing、OIDC/Cognito 認證、WAF 整合。

**Key Points:**
- ALB 支援 Listener Rules、Target Groups、Application Health Checks。
- 規則可依 Host Header、Path、Header、Method、Query String、Source IP 決策。
- HTTPS 一定在 ALB 終止，後端是另一條連線。
- 可搭配 `X-Forwarded-For` 傳遞原始客戶端 IP。

**⚠️ 考試陷阱:**
- 想保留 end-to-end unbroken TLS，不應先選 ALB。

**✅ 記憶點:**
- `Host/path based routing` 想 ALB。

## NLB

**What:** NLB 是 Layer 4 Load Balancer，適合高效能 TCP/TLS/UDP。

**When to use:** 非 HTTP 協定、極低延遲、靜態 IP、PrivateLink。

**Key Points:**
- NLB 支援 TCP、TLS、UDP、TCP_UDP。
- 可配置 Static IP，方便 White-list。
- 可做 TLS Passthrough 或搭配 PROXY protocol 傳遞 Client IP。
- 常拿來作為 PrivateLink 的 Provider 端。

**⚠️ 考試陷阱:**
- 需要 Layer 7 routing 時，NLB 不夠。

**✅ 記憶點:**
- `Static IP`, `PrivateLink`, `non-HTTP` 想 NLB。

## GWLB

**What:** GWLB 用來把流量導向與分散到第三方安全設備或自建網路設備。

**When to use:** 中央化流量檢查、Stateful Firewall、IDS/IPS、Transparent Appliance。

**Key Points:**
- GWLB 透過 GENEVE 封裝流量到後端 Appliance。
- GWLB Endpoint 讓其他 VPC 安全地把流量送到 GWLB。
- 可搭配 TGW Appliance Mode 形成中央檢查架構。

**⚠️ 考試陷阱:**
- 要做透明安全檢查時，不該選 ALB/NLB，應選 GWLB。

**✅ 記憶點:**
- `Security appliance scaling` 想 GWLB。

## Deregistration Delay / Connection Draining

**What:** 控制目標離線時，是否讓 in-flight requests 優雅結束。

**When to use:** 滾動更新、Auto Scaling、維護窗口。

**Key Points:**
- CLB 用詞是 Connection Draining。
- ALB/NLB/GWLB 用詞是 Deregistration Delay，設定在 Target Group。
- 預設通常是 300 秒。

**⚠️ 考試陷阱:**
- Connection Draining 是 CLB 名詞；新一代 LB 題目通常寫 Deregistration Delay。

**✅ 記憶點:**
- 優雅下線想 Target Group deregistration delay。
