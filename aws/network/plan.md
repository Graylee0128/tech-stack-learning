# AWS 網路證照 4 週高強度學習計畫

**目標：** 4 週內以考試通過優先，掌握 AWS Advanced Networking Specialty 高頻題型、核心選型判斷與常見陷阱。

**主教材：**
- `ans-notes/` 為主線
- `notes/` 與 `articles/` 僅用來補高頻陷阱與理解盲點

**每週節奏：**
- 2 次主題學習，每次 60-75 分鐘
- 1 次題目演練，每次 60 分鐘
- 1 次錯題複盤或輕量 lab，每次 45-60 分鐘

## 學習進度

### Week 1 - Hybrid Networking 核心
- [ ] 讀完 `ans-notes/06-hybrid-networking.md`
- [ ] 補讀 `ans-notes/02-vpc.md` 中 route table / route propagation / endpoints 相關段落
- [ ] 理解 BGP 的 `LOCAL_PREF`、`AS_PATH`、`MED` 各自影響什麼方向的流量
- [ ] 能口述 AWS 路由優先序：`Longest Prefix -> Static -> DX -> VPN static -> VPN BGP`
- [ ] 分清 DX / VPN / TGW / DXGW / VGW / Client VPN 的角色差異與典型場景
- [ ] 完成 1 次 Hybrid 題型練習
- [ ] 完成 1 次 TGW / VPN 輕量 lab 或紙上架構演練
- [ ] 題目驗收點：看到 Hybrid 題時，能先判斷該選 DX、VPN 還是 TGW

### Week 2 - VPC 與流量路徑
- [ ] 讀完 `ans-notes/02-vpc.md`
- [ ] 補讀 `ans-notes/01-fundamentals.md` 中 NAT / MTU / DNS Protocol Basics
- [ ] 分清 Subnet、Route Table、IGW、Egress-only IGW、NAT Gateway 的責任邊界
- [ ] 分清 NACL vs Security Group、Flow Logs vs Traffic Mirroring、VPC Peering vs TGW
- [ ] 分清 Gateway Endpoint vs Interface Endpoint / PrivateLink 的選型邏輯
- [ ] 完成 1 次 VPC / endpoint 題型練習
- [ ] 寫出 1 份自己的「流量判斷口訣」筆記
- [ ] 題目驗收點：遇到連不通題時，能判斷是哪個元件在擋流量

### Week 3 - 全球入口與流量導向
- [ ] 讀完 `ans-notes/04-route53-cdn.md`
- [ ] 讀完 `ans-notes/03-load-balancer.md`
- [ ] 讀完 `ans-notes/05-security.md`
- [ ] 補讀 `articles/global-accelerator-vs-cloudfront.md` 的選型比較
- [ ] 分清 Route 53 routing policies、Resolver inbound / outbound、health checks 的使用時機
- [ ] 分清 CloudFront vs Global Accelerator、ALB vs NLB vs GWLB 的選型邏輯
- [ ] 分清 WAF、Shield、Network Firewall、DNS Firewall 的層級與適用場景
- [ ] 完成 1 次全球流量導向題型練習
- [ ] 完成 1 次 Load Balancer 選型題複盤
- [ ] 題目驗收點：Edge 題能快速判斷該選 CloudFront、Global Accelerator、ALB、NLB 或 GWLB

### Week 4 - 考前衝刺與模擬考
- [ ] 快速掃過 `ans-notes/08-eks-networking.md`
- [ ] 快速掃過 `ans-notes/07-hybrid-services.md`
- [ ] 快速掃過 `ans-notes/09-cost-dr-governance.md`
- [ ] 重讀 `notes/ANS-Cheat-Sheet-中文版.md` 的高頻考點速記
- [ ] 做完 2 回模擬題或 2 組計時練習
- [ ] 建立 1 份弱點清單，列出錯最多的 3 類主題
- [ ] 只回補弱點清單中的 3 類主題，不再全面重讀
- [ ] 題目驗收點：能用 10 個高頻關鍵字快速對應到正確服務或架構

### 錯題複盤規則
- [ ] 建立 1 份錯題清單
- [ ] 每題錯題都標記成因：服務不熟 / 路由判斷錯 / 題幹關鍵字漏看
- [ ] 同類錯誤累積 3 次時，回補對應原筆記
- [ ] 每週至少做 1 次 30 分鐘錯題複盤

### 輕量 Lab 規則
- [ ] 只做高回報 lab：VPC Endpoint、TGW / VPN、Load Balancer 選型
- [ ] 單次 lab 控制在 60 分鐘內
- [ ] 超過 60 分鐘的 lab 直接降級成架構圖演練，不追求完整部署
- [ ] lab 完成後記下 1 個選型理由與 1 個常見陷阱

## 驗收標準
- [ ] 完成 4 週學習節奏，且每週都有主題閱讀、題目演練、複盤或輕量 lab
- [ ] 完成 2 回模擬題或等量計時題組
- [ ] 建立並維護 1 份錯題清單
- [ ] 完成 3 次高價值輕量 lab / 架構演練
- [ ] 能口述 10 個高頻選型判斷
- [ ] 能在情境題中分辨 Hybrid、VPC、Edge、Security 四大類核心服務的選型邏輯
