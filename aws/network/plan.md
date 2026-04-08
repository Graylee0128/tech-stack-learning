# AWS 網路證照 4 週高強度學習計畫

**目標：** 4 週內以考試通過優先，掌握 AWS Advanced Networking Specialty 高頻題型、核心選型判斷與常見陷阱。

**進度：** `34 / 127`

**主教材：**
- `ans-notes/` 為主線
- `notes/` 與 `articles/` 僅用來補高頻陷阱與理解盲點

**每週節奏：**
- 2 次主題學習，每次 60-75 分鐘
- 1 次題目演練，每次 60 分鐘
- 1 次錯題複盤或輕量 lab，每次 45-60 分鐘

## 學習進度

### Week 1 - Hybrid Networking 核心
- [ ] 讀完 `ans-notes/06-hybrid-networking.md` 的 `BGP`
- [ ] 讀完 `ans-notes/06-hybrid-networking.md` 的 `Route Priority in AWS`
- [ ] 讀完 `ans-notes/06-hybrid-networking.md` 的 `Direct Connect`
- [ ] 讀完 `ans-notes/06-hybrid-networking.md` 的 `DXGW`
- [ ] 讀完 `ans-notes/06-hybrid-networking.md` 的 `VGW / Site-to-Site VPN / Client VPN`
- [ ] 讀完 `ans-notes/06-hybrid-networking.md` 的 `Transit Gateway`
- [ ] 補讀 `ans-notes/02-vpc.md` 的 `Subnets / Route Tables / IGW / Egress-only IGW`
- [x] 理解 BGP 的 `LOCAL_PREF` 主要影響 outbound path
- [x] 理解 `AS_PATH prepend` 常用來影響 inbound path
- [x] 理解 `MED` 是多條連線時的偏好提示，不是萬能控制鈕
- [x] 能口述 AWS 路由優先序：`Longest Prefix -> Static -> DX -> VPN static -> VPN BGP`
- [x] 分清 `VGW = 單 VPC 邊界`
- [x] 分清 `TGW = 多 VPC / 多站點 hub`
- [x] 分清 `DXGW = DX 跨 Region / 多 VPC 的邏輯中介`
- [x] 分清 `DX = physical link`
- [x] 分清 `VIF = logical lane`
- [x] 分清 `DXGW = DX 進 AWS 的 distribution hub`
- [x] 分清 `Site-to-Site VPN = 網路對網路的加密接入`
- [x] 分清 `Client VPN = 終端使用者遠端接入`
- [x] 分清 `VPN CloudHub = 多個 remote sites 經同一個 VGW 互通`
- [x] 理解 DX 為主、VPN 為備援的常見設計
- [x] 分清 `Private VIF = 進 VPC 私網`
- [x] 分清 `Public VIF = 去 AWS public services`
- [x] 分清 `Transit VIF = 進 TGW transit 架構`
- [x] 理解 `Transit VIF -> DXGW -> TGW` 的連接模型
- [x] 理解 `Private VIF -> DXGW -> VGW -> VPC` 的連接模型
- [x] 理解 `DXGW` 解的是「一條 DX 不用綁死單一 VPC」的擴展痛點
- [x] 理解 `VIF` 解的是「同一條 DX 線上不同流量用途的分流」
- [x] 理解 `DXGW` 不等於 `TGW`
- [x] 理解 `VGW = one VPC edge`、`TGW = many VPC hub`
- [x] 理解 TGW 為什麼比 full-mesh VPC peering 更適合大規模互聯
- [x] 理解 `association = attachment 查哪張 TGW route table`
- [x] 理解 `propagation = attachment 的路由散到哪些 TGW route table`
- [x] 理解 `associate to one, propagate to many`
- [x] 理解 TGW 題型常考的是 segmentation、shared services、attachment 建了卻不通
- [x] 完成 1 次 Hybrid 題型練習
- [x] 記錄 3 題 Hybrid 題的錯因或判斷依據
- [x] 記錄 1 組 Direct Connect / VIF / DXGW 的易混點
- [x] 記錄 1 組 `VGW vs TGW` 與 `VPN family` 的易混點
- [x] 記錄 1 組 `association vs propagation` 的易混點
- [ ] 完成 1 次 TGW / VPN 輕量 lab
- [ ] 若未實作，改做 1 張 TGW hub-and-spoke 紙上架構圖
- [x] 題目驗收點：看到 Hybrid 題時，能先判斷該選 DX、VPN、VGW 還是 TGW

### Week 2 - VPC 與流量路徑
- [ ] 讀完 `ans-notes/02-vpc.md` 的 `VPC Core`
- [ ] 讀完 `ans-notes/02-vpc.md` 的 `DNS / DHCP / VPC Router`
- [ ] 讀完 `ans-notes/02-vpc.md` 的 `Subnets / Route Tables / IGW / Egress-only IGW`
- [ ] 讀完 `ans-notes/02-vpc.md` 的 `NACL vs Security Group`
- [ ] 讀完 `ans-notes/02-vpc.md` 的 `Flow Logs / Reachability / Access Analysis`
- [ ] 讀完 `ans-notes/02-vpc.md` 的 `VPC Endpoints / PrivateLink`
- [ ] 讀完 `ans-notes/02-vpc.md` 的 `VPC Peering`
- [ ] 補讀 `ans-notes/01-fundamentals.md` 的 `NAT`
- [ ] 補讀 `ans-notes/01-fundamentals.md` 的 `Jumbo Frames / MTU`
- [ ] 補讀 `ans-notes/01-fundamentals.md` 的 `DNS Protocol Basics`
- [ ] 理解 `VPC = regional`、`Subnet = AZ-boundary`
- [ ] 理解 `+1 = gateway`、`+2 = AmazonProvidedDNS`
- [ ] 分清 public subnet 成立條件：對 IGW 的 route + instance 有 public IP
- [ ] 分清 `NACL = subnet + stateless + allow/deny`
- [ ] 分清 `SG = ENI + stateful + allow only`
- [ ] 分清 `Flow Logs = metadata`
- [ ] 分清 `Traffic Mirroring = packet payload inspection`
- [ ] 分清 `Gateway Endpoint = S3 / DynamoDB only`
- [ ] 分清 `Interface Endpoint = ENI + PrivateLink + 更多 AWS / SaaS 服務`
- [ ] 分清 `VPC Peering = 一對一且 non-transitive`
- [ ] 完成 1 次 VPC / endpoint 題型練習
- [ ] 記錄 3 個常見流量不通的排查順序
- [ ] 寫出 1 份自己的「流量判斷口訣」筆記
- [ ] 題目驗收點：遇到連不通題時，能判斷是 route、SG、NACL、endpoint 還是哪個元件在擋流量

### Week 3 - 全球入口與流量導向
- [ ] 讀完 `ans-notes/04-route53-cdn.md` 的 `Hosted Zones / Resolver / DNSSEC`
- [ ] 讀完 `ans-notes/04-route53-cdn.md` 的 `Route 53 Health Checks`
- [ ] 讀完 `ans-notes/04-route53-cdn.md` 的 `Route 53 Routing Policies`
- [ ] 讀完 `ans-notes/04-route53-cdn.md` 的 `CloudFront`
- [ ] 讀完 `ans-notes/04-route53-cdn.md` 的 `CloudFront Security / Private Content / Lambda@Edge`
- [ ] 讀完 `ans-notes/04-route53-cdn.md` 的 `ACM`
- [ ] 讀完 `ans-notes/03-load-balancer.md` 的 `ALB`
- [ ] 讀完 `ans-notes/03-load-balancer.md` 的 `NLB`
- [ ] 讀完 `ans-notes/03-load-balancer.md` 的 `GWLB`
- [ ] 讀完 `ans-notes/05-security.md` 的 `WAF`
- [ ] 讀完 `ans-notes/05-security.md` 的 `Shield`
- [ ] 讀完 `ans-notes/05-security.md` 的 `Network Firewall / Firewall Manager`
- [ ] 讀完 `ans-notes/05-security.md` 的 `Route 53 Resolver DNS Firewall`
- [ ] 補讀 `articles/global-accelerator-vs-cloudfront.md` 的選型比較
- [ ] 分清 `Inbound Resolver Endpoint = on-prem 查 AWS`
- [ ] 分清 `Outbound Resolver Endpoint = AWS 查 on-prem`
- [ ] 分清 `Health Check = DNS failover 的前提`
- [ ] 分清 `CloudFront = HTTP/HTTPS + caching`
- [ ] 分清 `Global Accelerator = Anycast IP + no caching + TCP/UDP`
- [ ] 分清 `ALB = L7 routing`
- [ ] 分清 `NLB = static IP / non-HTTP / PrivateLink`
- [ ] 分清 `GWLB = security appliance scaling`
- [ ] 分清 `WAF = L7`
- [ ] 分清 `Shield = DDoS`
- [ ] 分清 `DNS Firewall = 擋惡意網域解析`
- [ ] 完成 1 次全球流量導向題型練習
- [ ] 完成 1 次 Load Balancer 選型題複盤
- [ ] 記錄 5 個關鍵字對應服務，例如 `static IP -> NLB`
- [ ] 題目驗收點：Edge 題能快速判斷該選 CloudFront、Global Accelerator、ALB、NLB、GWLB、WAF 或 Shield

### Week 4 - 考前衝刺與模擬考
- [ ] 快速掃過 `ans-notes/08-eks-networking.md` 的 `VPC CNI / Pod IP / Security Groups for Pods / Exposing Services`
- [ ] 快速掃過 `ans-notes/07-hybrid-services.md` 的 `Directory Service / FSx / Storage Gateway / WorkSpaces`
- [ ] 快速掃過 `ans-notes/09-cost-dr-governance.md` 的 `VPC / TGW / DX Cost`
- [ ] 快速掃過 `ans-notes/09-cost-dr-governance.md` 的 `Disaster Recovery`
- [ ] 快速掃過 `ans-notes/09-cost-dr-governance.md` 的 `IPAM / AWS Network Manager`
- [ ] 重讀 `notes/ANS-Cheat-Sheet-中文版.md` 的高頻考點速記
- [ ] 整理 1 份自己的 10 條高頻選型口訣
- [ ] 做完第 1 回模擬題或第 1 組計時練習
- [ ] 做完第 2 回模擬題或第 2 組計時練習
- [ ] 建立 1 份弱點清單
- [ ] 將弱點清單分類成最多 3 類主題
- [ ] 只回補弱點清單中的 3 類主題，不再全面重讀
- [ ] 回補時只重讀對應 `ans-notes` 段落與錯題，不重跑整份教材
- [ ] 題目驗收點：能用 10 個高頻關鍵字快速對應到正確服務或架構

### 錯題複盤規則
- [ ] 建立 1 份錯題清單
- [ ] 每題錯題記下題目主題分類：Hybrid / VPC / Edge / Security / Misc
- [ ] 每題錯題都標記成因：服務不熟 / 路由判斷錯 / 題幹關鍵字漏看
- [ ] 每題錯題都補 1 句正確判斷依據
- [ ] 同類錯誤累積 3 次時，回補對應原筆記
- [ ] 每週至少做 1 次 30 分鐘錯題複盤

### 輕量 Lab 規則
- [ ] 只做高回報 lab：VPC Endpoint、TGW / VPN、Load Balancer 選型
- [ ] 單次 lab 控制在 60 分鐘內
- [ ] 超過 60 分鐘的 lab 直接降級成架構圖演練，不追求完整部署
- [ ] lab 前先寫下這次要驗證的 1 個重點
- [ ] lab 完成後記下 1 個選型理由與 1 個常見陷阱

## 驗收標準
- [ ] 完成 4 週學習節奏，且每週都有主題閱讀、題目演練、複盤或輕量 lab
- [ ] 完成 2 回模擬題或等量計時題組
- [ ] 建立並維護 1 份錯題清單
- [ ] 完成 3 次高價值輕量 lab / 架構演練
- [ ] 能口述 10 個高頻選型判斷
- [ ] 能在情境題中分辨 Hybrid、VPC、Edge、Security 四大類核心服務的選型邏輯
