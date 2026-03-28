# AWS ANS Notes

這個資料夾把原始 AWS Advanced Networking Specialty 筆記整理成 9 份主題筆記。整理原則是統一格式、合併同類主題、去除明顯重複，但保留重要考點、限制、比較、路由優先序與常見陷阱。

## 目錄

- `01-fundamentals.md`
- `02-vpc.md`
- `03-load-balancer.md`
- `04-route53-cdn.md`
- `05-security.md`
- `06-hybrid-networking.md`
- `07-hybrid-services.md`
- `08-eks-networking.md`
- `09-cost-dr-governance.md`

## 高頻考點導覽

- `06-hybrid-networking.md`
  DX、VGW、TGW、BGP、VPN、Route Priority、Cloud WAN、Global Accelerator 是 ANS 核心。
- `02-vpc.md`
  VPC Router、Subnet、Route Table、NACL vs SG、Endpoints、Peering、IPv6 幾乎每份題目都會碰到。
- `05-security.md`
  WAF、Shield、Network Firewall、CloudTrail、Config、Macie 常和情境題一起出。
- `04-route53-cdn.md`
  Route 53 Routing Policies、Resolver Endpoints、CloudFront、ACM 很常和全球架構一起考。
- `08-eks-networking.md`
  Pod IP、VPC CNI、Ingress/NLB/ALB、SG for Pods 是容器題重點。

## 建議複習順序

依**考試出題比重**排列——先掌握高頻核心，再補齊周邊知識：

| 順序 | 檔案 | 理由 |
|------|------|------|
| 1 | `06-hybrid-networking.md` | DX/VPN/TGW/BGP 是 ANS 最高比重題型（約 30%） |
| 2 | `02-vpc.md` | VPC 是幾乎所有題目的底層基礎 |
| 3 | `05-security.md` | WAF/Shield/Network Firewall 常與情境題組合 |
| 4 | `04-route53-cdn.md` | Route 53 + CloudFront 是全球架構核心 |
| 5 | `03-load-balancer.md` | ALB/NLB/GWLB 選型搭配上述主題出題 |
| 6 | `01-fundamentals.md` | DNS 協定、OSI、NAT 等基礎——已熟悉者可跳過 |
| 7 | `08-eks-networking.md` | EKS 題數較少但細節刁鑽 |
| 8 | `07-hybrid-services.md` | 輔助服務（Wavelength、Outposts 等）低頻 |
| 9 | `09-cost-dr-governance.md` | 成本與治理偶爾出現，考前掃過即可 |
