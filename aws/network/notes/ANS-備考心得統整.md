# AWS Advanced Networking Specialty (ANS-C01) 備考心得統整

> 來源：Reddit r/AWSCertifications、dev.to (DevonPatrick Adkins)
> 整理日期：2026-03-16

---

## 考試難度共識

- **比 SAA 難很多**，屬於 Specialty 等級，scenario-heavy（大量情境題）
- 即使有 CCNA/CCNP 等傳統網路背景，仍需 **4-6 個月** 專門準備
- 若已有 AWS 網路實務經驗，最少也要 **2-3 個月**
- 建議先通過 SAA 再來挑戰，基礎會比較穩

---

## 核心考試主題（必須深入理解）

| 領域 | 重點項目 |
|------|----------|
| **Hybrid Connectivity** | Direct Connect、Site-to-Site VPN、Transit Gateway、Customer Gateway |
| **VPC 設計** | VPC Peering、Subnetting、Route Tables、Security Groups、NACLs |
| **DNS** | Route 53（各種 Routing Policy）、DNS Resolution、Private Hosted Zones |
| **BGP** | AS Path、Route Propagation、BGP Communities、MED、Local Preference |
| **Network Security** | WAF、Shield、Network Firewall、NACLs vs SG |
| **Troubleshooting** | Flow Logs、Reachability Analyzer、連線排錯場景 |
| **Load Balancing** | ALB/NLB/GWLB 差異與適用場景 |
| **Multi-Account** | Transit Gateway 跨帳號、RAM 共享、VPC Sharing |

---

## 推薦學習資源（依優先順序）

### Step 1：影片課程（建立知識框架）

| 資源 | 特色 | 備註 |
|------|------|------|
| **Adrian Cantrill** | 業界公認最佳 ANS 課程，Lab 品質極高（含 Multi-Cloud VPN Lab） | 有點貴但值得，可請公司買 |
| **Cloud Academy** | 結構化學習 + 內建 Lab + 知識檢測，適合從頭開始 | 提供 Practice Exam，建議考 5 次平均 90% 再上場 |
| **AWS Skill Builder** | 官方免費學習路徑（Exam Prep Plan for ANS-C01） | [Learning Plan 連結](https://skillbuilder.aws/learning-plan/QR39N4AN1C) |

### Step 2：模擬考題（檢驗學習成果）

| 資源 | 特色 |
|------|------|
| **Tutorials Dojo / Jon Bonso** | 最多人推薦，題目比真實考試還難，附架構圖 + 影片解說 + AWS 官方文件連結 |
| **Tutorials Dojo Cheat Sheets** | [Networking & CDN Cheat Sheets](https://tutorialsdojo.com/aws-cheat-sheets-networking-and-content-delivery/) |

### Step 3：額外補充

| 資源 | 說明 |
|------|------|
| **AWS Power Hour Series** | AWS 官方直播教學，可在 [Twitch/AWS](https://www.twitch.tv/aws) 觀看回放 |
| **AWS Whitepapers & FAQs** | VPC、Direct Connect、Transit Gateway 的官方白皮書必讀 |
| **Adrian Cantrill GitHub** | [github.com/acantril](https://github.com/acantril) - 免費 Lab 範例 |

---

## 備考策略與考試技巧

### 備考期間
1. **理解 > 背誦**：每題都要搞懂「為什麼」，而非單純記答案
2. **動手做 Lab**：特別是 VPN、Direct Connect、Transit Gateway 相關的實作
3. **閱讀題目解析**：Tutorials Dojo 的解釋非常詳細，每題都要看
4. **讀官方文檔**：考試會考到很細的設定和限制

### 考試當天
1. **時間管理是關鍵**：遇到太耗時的題目，先標記跳過
2. **持續注意計時器**：不要在單一題目上卡太久
3. **情境題要看全貌**：先理解整體架構需求，再選答案

---

## 建議備考時程

| 背景 | 建議時間 | 說明 |
|------|----------|------|
| 純 SAA 基礎 | 4-6 個月 | 需要大量補網路基礎 |
| 有 AWS + 網路實務經驗 | 2-3 個月 | 專注在 hybrid connectivity 和 BGP |
| 有 CCNP + AWS 經驗 | 6-8 週 | 已有網路底子，專注在 AWS 特有服務 |

---

## 備註

- Medium 文章（Niraj Kumar 的 Study Guide）因 Cloudflare 擋住無法取得，如有需要可手動查閱
- Reddit 討論串中也有人推薦 [另一篇完整資源指南](https://www.reddit.com/r/AWSCertifications/comments/1iqaqck/aws_certified_advanced_networking_specialty/)
