# AWS ANS 筆記整理計畫

## 來源
- Repo: https://github.com/Ernyoke/certified-aws-advanced-networking-specialty
- Clone 位置: `C:\Users\李欣翰\Downloads\certified-aws-advanced-networking-specialty\`

## 目標
將 55 個原始 Markdown 檔整理成 9 個主題筆記，存放於：
`tech-stack-learning/aws/network/ans-notes/`

整理時以「系統化重組」為主，不以刪減內容為目標；
尤其是重要考點、限制條件、比較差異、路由優先順序與考試陷阱，需完整保留。

---

## 輸出檔案規劃

| 輸出檔案 | 來源章節 | 涵蓋內容 | 狀態 |
|---------|---------|---------|------|
| `01-fundamentals.md` | 01-fundamentals | DNS、Route53、DDoS、OSI、NAT、SSL、VLAN、Jumbo Frame、Reserved IPv4 | ✅ 已完成 |
| `02-vpc.md` | 02-vpc | VPC 核心、Endpoints、Peering、EC2 Networking | ✅ 已完成 |
| `03-load-balancer.md` | 04-lb | ELB、GWLB | ✅ 已完成 |
| `04-route53-cdn.md` | 05-r53、06-cdn | Route 53 進階、CloudFront、ACM | ✅ 已完成 |
| `05-security.md` | 07-security | Network Firewall、Shield、WAF、Firewall Manager、CloudHSM、CloudTrail、Config、Inspector、Macie、S3 Access Points、IP Ranges | ✅ 已完成 |
| `06-hybrid-networking.md` | 08-hybrid-networking | BGP、DX、TGW、VGW、S2S VPN、Client VPN、Cloud WAN、IPSec、Global Accelerator、Route Priority | ✅ 已完成 |
| `07-hybrid-services.md` | 09-hybrid-services | Directory Services、FSx、Storage Gateway、WorkSpaces | ✅ 已完成 |
| `08-eks-networking.md` | 10-eks-networking | Kubernetes/EKS Networking | ✅ 已完成 |
| `09-cost-dr-governance.md` | 11-cost-management、12-dr、13-network-management | DX/VPC Cost、DR 策略、IPAM、Network Manager | ✅ 已完成 |
| `README.md` | — | 目錄索引 + 考試重點導覽 | ✅ 已完成 |

---

## 整理格式（每個服務統一）

```markdown
## 服務名稱

**What:** 一句話說明是什麼

**When to use:** 使用場景

**Key Points:**
- 重點 1
- 重點 2

**Comparison:**  
- 相似服務或方案差異（若適用）

**Limits / Caveats:**  
- 限制條件、配額、例外情況（若適用）

**Design Notes:**  
- 架構選型或判斷依據（若適用）

**⚠️ 考試陷阱:**
- 陷阱 1

**✅ 記憶點:**
- 記憶點 1
```

---

## 整理原則

1. **合併同類**：55 個原始檔 → 9 個主題檔，降低碎片化，但不代表刪減資訊
2. **統一格式**：使用固定欄位整理，讓內容可快速查找與複習
3. **完整保留重要考點**：重要觀念、限制、比較、例外、優先順序不可省略
4. **保留考試重點**：標記 `⚠️ 考試陷阱` 和 `✅ 記憶點`
5. **允許去重，不允許漏重點**：重複內容可整併，但不能遺失高價值資訊
6. **中英對照**：標題英文，說明可混中文，技術術語保留原文

---

## 執行優先順序

1. **`06-hybrid-networking.md`** ← 最重要，DX + TGW + BGP 佔 ANS 大比例，且需完整保留路由、連線模式、DNS 與比較考點
2. **`02-vpc.md`** ← 基礎核心
3. **`05-security.md`** ← 題目常出
4. 其餘章節依序完成
5. 最後建立 `README.md` 索引

---

## 進度追蹤

- [x] 01-fundamentals.md
- [x] 02-vpc.md
- [x] 03-load-balancer.md
- [x] 04-route53-cdn.md
- [x] 05-security.md
- [x] 06-hybrid-networking.md  ← 優先
- [x] 07-hybrid-services.md
- [x] 08-eks-networking.md
- [x] 09-cost-dr-governance.md
- [x] README.md
