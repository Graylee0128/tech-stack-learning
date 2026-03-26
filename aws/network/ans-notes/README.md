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

1. `06-hybrid-networking.md`
2. `02-vpc.md`
3. `05-security.md`
4. `04-route53-cdn.md`
5. `03-load-balancer.md`
6. `01-fundamentals.md`
7. `08-eks-networking.md`
8. `07-hybrid-services.md`
9. `09-cost-dr-governance.md`
