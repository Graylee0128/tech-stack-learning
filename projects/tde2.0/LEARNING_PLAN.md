# TDE 2.0 DevOps 學習計畫

> 基於 `tech-stack-learning/` 所有現有教材，規劃從基礎到進階的完整學習路徑。
> 最終目標：對齊 **Platform Engineering / SRE** 職涯方向。

---

## 前言：這個專案到底在幹嘛？實務上有什麼用？

TDE 2.0 表面上是一個「輸入 URL → 轉 PDF → 存雲端」的小工具。但它的價值不在應用本身，而在於它背後的**架構模式**是業界極度常見的套路。

### 核心架構模式：「接收請求 → 排隊 → 非同步處理 → 存結果」

這個 **SQS + Lambda + S3** 的組合，直接對應到以下真實場景：

| 實際業務場景 | 對應 TDE 2.0 的哪一段 |
|-------------|---------------------|
| **電商發票/報表產生** — 用戶下單後，系統非同步生成 PDF 發票存 S3 | URL→PDF = 訂單→發票 |
| **影音轉檔** — 用戶上傳影片，Lambda 觸發 MediaConvert 轉碼，存回 S3 | HTML→PDF = MP4→HLS |
| **圖片處理** — 上傳大圖後，自動生成縮圖、浮水印、不同尺寸 | wkhtmltopdf = ImageMagick |
| **資料匯出** — 用戶點「匯出 CSV/Excel」，後台排隊處理，完成後通知下載 | 同樣的非同步排隊模式 |
| **批次信件/通知** — 行銷系統排隊發送 email/SMS | SQS 排隊 + Lambda 逐筆處理 |
| **ETL Pipeline** — 資料進 SQS，Lambda 清洗轉換，寫入 DB/S3 | 完全相同的解耦模式 |

### 基礎設施模式：「EKS + Terraform + GitOps」= 業界標配

| 實際業務場景 | 對應 TDE 2.0 的哪一段 |
|-------------|---------------------|
| **任何 SaaS 產品的後端** — 多微服務跑在 K8s，Terraform 管基礎設施 | 完全一樣 |
| **金融科技平台** — 多 AZ 高可用、Private Subnet 隔離、密鑰集中管理 | VPC 三層子網 + Parameter Store |
| **醫療/合規系統** — 稽核追蹤、加密、存取控制 | IAM + Parameter Store + CloudWatch |
| **遊戲後端** — HPA 自動擴展應對流量尖峰 | EKS + Cluster Autoscaler + HPA |

### CI/CD 模式：「GitOps 三倉庫」= 多團隊協作標準

| 實際業務場景 | 為什麼用這個模式 |
|-------------|----------------|
| **多團隊協作** — 前端/後端/SRE 各自有 repo，互不干擾 | Code / CI / CD 分離 |
| **需要審計的環境** — 每次部署都有 Git commit 紀錄 | ArgoCD + Git = 完整部署歷史 |
| **頻繁發版** — 一天多次部署，需要快速回滾能力 | ArgoCD Rollback + git revert |

### 一句話總結

> TDE 2.0 的架構 = **任何需要「接收用戶請求 → 非同步處理重任務 → 回傳結果」的系統**。電商、影音、SaaS、FinTech、遊戲後端都是這個套路，只是把 `wkhtmltopdf` 換成不同的業務邏輯。

---

## 學習路徑總覽

```
Phase 1          Phase 2              Phase 3           Phase 4           Phase 5
基礎工具鏈  ──→  DevOps 實戰專案  ──→  網路專精(ANS)  ──→  安全專精(SCS)  ──→  架構專精(SAP)
Week 1-2         Week 3-4             Week 5-8          Week 9-12         Week 13-16
```

---

## TDE 2.0 專案能讓我學到什麼？

這個專案的價值不在應用程式本身（URL 轉 PDF 很簡單），而在於它逼你把 **DevOps 全流程**走一遍。具體來說：

### 硬技能（Hard Skills）

| 能力維度 | 你會學到的東西 | 為什麼重要 |
|----------|---------------|-----------|
| **系統架構設計** | 六層架構拆解（Frontend → Backend → SQS → Lambda → DB → S3）、何時該解耦、何時用同步 vs 非同步 | 面試必問「你怎麼設計一個系統」，這個專案就是一個完整答案 |
| **IaC 實戰** | Terraform 15 個檔案的組織方式、模組依賴管理、Terraform Cloud 遠端執行、一次建 128 個 AWS 資源 | 不是寫 hello world 等級的 tf，是 production-grade 的結構 |
| **Kubernetes 操作** | EKS 叢集管理、6 個 Helm Chart 部署（Nginx Ingress / ArgoCD / Datadog 等）、HPA 自動擴展、kubectl 日常操作 | K8s 是 DevOps 的核心戰場，這裡一次把操作面和管理面都練到 |
| **CI/CD 全流程** | GitOps 三倉庫模型（Code → CI → CD）、GitHub Actions Self-hosted Runner、ArgoCD 自動同步、Image Tag 策略（SHA-based） | 不是只會跑 pipeline，而是理解整個 GitOps 設計哲學 |
| **AWS 多服務協作** | EKS + SQS + Lambda + RDS + DynamoDB + S3 + ECR + NLB + Route53 + ACM + Parameter Store，共 11+ 個服務串接 | 單一服務誰都會，**串接**才是真功夫 |
| **監控體系** | Datadog Agent（DaemonSet）→ Metrics/Logs/APM → Monitor Alert → PagerDuty 電話通知，完整 Observability 鏈路 | 「部署完就結束」是初級思維，能監控才是 production-ready |
| **版本回滾** | ArgoCD History Rollback + Auto-Sync 管理 + git revert 策略（在 CI Repo 操作，不碰 CD Repo） | 出事不怕，怕的是不知道怎麼回滾 |
| **網路架構** | VPC 三層子網（Public / Private / DB）、跨 2 AZ 高可用、NLB TLS Termination、Nginx Ingress 反向代理 | 理解流量從 Internet 到 Pod 走了哪些路 |
| **密鑰管理** | AWS Parameter Store 集中管理，不用 K8s Secrets，搭配 IAM Role-based 存取 | 安全基本功，面試加分項 |

### 軟技能 & 工程思維

| 思維模式 | 從專案中學到的體現 |
|----------|-------------------|
| **解耦思維** | SQS + Lambda 把重 I/O 工作從後端拆出，任一方掛掉不拖垮整體 |
| **宣告式思維** | Terraform「我要什麼狀態」、ArgoCD「Git 是唯一真相來源」—— 不是一步步命令，而是描述終態 |
| **可觀測思維** | 不是出問題才看 log，而是 Metrics → Logs → Alerts 三層主動覆蓋 |
| **Everything as Code** | 基礎設施、部署流程、設定全部是程式碼，人不碰生產環境，Git 是唯一入口 |
| **故障回復思維** | 不只是「怎麼部署」，還有「壞了怎麼辦」—— 回滾流程是設計的一部分，不是事後補丁 |

### 一句話總結

> TDE 2.0 讓你從「我會用某個工具」升級到「我能把 11+ 個 AWS 服務 + K8s + CI/CD + 監控串成一個可運維的生產系統」。這就是 **Junior → Mid-level DevOps Engineer** 的分水嶺。

---

## 整個學習計畫過程中，我會學到什麼？

### Phase by Phase 技能累積

```
Phase 1 (基礎)        Phase 2 (實戰)         Phase 3 (網路)        Phase 4 (安全)         Phase 5 (架構)
───────────────       ──────────────        ──────────────       ──────────────        ──────────────
會用工具         →    會串系統          →    會設計網路      →    會保護系統        →    會設計架構

Git 版控               多服務協作             VPC 進階設計          威脅偵測與回應         多帳戶治理
Docker 容器化          Terraform IaC          混合雲連接             IAM 進階策略           全球化 HA/DR
Terraform 基礎         K8s/EKS 操作           流量工程               加密與密鑰管理         混合雲遷移
GitHub Actions CI      GitOps CI/CD           DNS 架構               網路安全防禦           成本與架構權衡
                       監控 & 回滾            負載平衡選型           合規與稽核
```

### 逐 Phase 詳細收穫

#### Phase 1 — 基礎工具鏈（你會從「聽過」變成「會用」）

| 學到的能力 | 具體表現 |
|-----------|---------|
| Git 工作流 | 不再搞混 clone/pull/fetch，能處理 merge conflict，建立日常 commit 習慣 |
| Docker 選型判斷 | 能回答「什麼時候用容器、什麼時候用 Serverless、什麼時候用 ECS vs EKS」 |
| Terraform 全流程 | 從 init 到 destroy 都跑過，懂 state lock、remote backend、module 拆分 |
| CI Pipeline 設計 | 能寫 GitHub Actions workflow，懂 matrix build、caching、secrets 最佳實踐 |

#### Phase 2 — DevOps 實戰（你會從「會用工具」變成「會串系統」）

| 學到的能力 | 具體表現 |
|-----------|---------|
| 端到端系統部署 | 能從零用 Terraform 建出 128 個 AWS 資源，再用 CI/CD 把應用部署上去 |
| 架構設計能力 | 能解釋六層架構每一層的選型理由，能畫架構圖 |
| GitOps 實踐 | 理解三倉庫模型，能操作 ArgoCD 做自動部署和回滾 |
| 生產級維運 | 能用 Datadog 看 dashboard、查 log、設 alert，出事能回滾 |
| 職涯定位 | 理解 Platform Engineering 演進脈絡，知道自己要往哪走 |

#### Phase 3 — 網路專精（你會從「能連上」變成「懂為什麼能連上」）

| 學到的能力 | 具體表現 |
|-----------|---------|
| VPC 進階設計 | VPC Endpoint 三種類型的差異與選型（Interface / Gateway / GWLB） |
| 混合雲連接 | DX / VPN / DXGW 的使用場景、成本分析、故障排除 |
| 流量工程 | Transit Gateway 路由設計、Hub-and-Spoke 架構、Appliance Mode |
| DNS 架構 | Route 53 Resolver、Split-Horizon DNS、Hybrid DNS 解析 |
| 邊緣服務 | CloudFront vs Global Accelerator 的選型邏輯 |
| 負載平衡 | ALB vs NLB vs GWLB 的技術差異和適用場景 |
| 網路排錯 | 三層排錯法（Routing → Security → Application）、BGP Route Selection |
| **認證級別** | ANS-C01 考試 ~85% 範圍覆蓋 |

#### Phase 4 — 安全專攻（你會從「知道要安全」變成「知道怎麼做安全」）

| 學到的能力 | 具體表現 |
|-----------|---------|
| 威脅偵測 | GuardDuty 自動偵測 + Security Hub 聚合 + EventBridge 自動回應 |
| 事件回應 | CloudTrail 追蹤 + Detective 分析 + Athena 查詢，完整 forensics 流程 |
| IAM 進階 | Organizations 多帳戶、SCP 防護欄、Permission Boundary、ABAC 標籤授權 |
| 加密體系 | KMS 金鑰管理、Envelope Encryption、Secrets Manager 輪替、傳輸加密（ACM/TLS） |
| 網路安全 | WAF 規則設計、Shield DDoS 防護、Network Firewall、GWLB 安全檢查 |
| 合規稽核 | Config 規則、CloudTrail 日誌完整性、Audit Manager 合規報告 |
| **認證級別** | SCS 考試全範圍覆蓋 |

#### Phase 5 — 架構大師（你會從「會建系統」變成「會設計可擴展的企業架構」）

| 學到的能力 | 具體表現 |
|-----------|---------|
| 多帳戶治理 | Organizations + IAM Identity Center + Control Tower 企業級基礎架構 |
| 安全監控整合 | GuardDuty + Inspector + Security Hub 跨帳戶安全態勢 |
| 分層網路防禦 | WAF → Network Firewall → Firewall Manager 統一管理 |
| 資料保護 | KMS + Macie 敏感資料偵測 + ACM 憑證管理 |
| 混合雲遷移 | DMS 資料庫遷移 + DataSync 檔案同步 + Storage Gateway + VPN/TGW 連接 |
| 全球化 HA/DR | Multi-Region 架構、Route 53 Failover、Aurora Global DB、S3 CRR、AWS Backup |
| **認證級別** | SAP 考試 100% 範圍覆蓋 |

### 16 週後你的技能雷達圖

```
                        架構設計 ★★★★★
                       ╱              ╲
               安全防護 ★★★★★    網路設計 ★★★★★
                  │                      │
              IaC/自動化 ★★★★★    容器/K8s ★★★★☆
                  │                      │
              CI/CD ★★★★★        監控/維運 ★★★★☆
                       ╲              ╱
                        雲端服務 ★★★★★

面試時能說的話：
├─「我做過一個 11+ AWS 服務的 DevOps 專案，從 IaC 到 CI/CD 到監控全流程」
├─「我有 ANS 等級的網路知識，能設計混合雲和多 VPC 架構」
├─「我有 SCS 等級的安全知識，能建立威脅偵測到自動回應的完整鏈路」
└─「我有 SAP 等級的架構能力，能設計多帳戶、多區域、高可用的企業架構」
```

---

## Phase 1 — 基礎工具鏈（Week 1-2）

**目標**：確保核心工具鏈的基礎概念扎實，為 TDE 2.0 專案做準備。

| # | 主題 | 教材路徑 | 預估時間 |
|---|------|----------|----------|
| 1 | Git 基礎 | `git/notes/git_qa.md` | 1-2 hr |
| 2 | Docker 概念釐清 | `docker/note：確保核心工具鏈的基礎概念扎實，為s/docker_container_qa.md` | 2-3 hr |
| 3 | Terraform 速查表 | `terraform/notes/cheatsheet_tmp.md` | 3-4 hr |
| 4 | GitHub Actions 全套 | `cicd/github-actions/notes/` (basics → cheatsheet → examples → best-practices) | 4-5 hr |

### 學習重點
- **Git**：clone vs pull、add vs commit、衝突解決、日常工作流
- **Docker**：Docker vs Terraform 定位差異、容器 vs Serverless 選型、ECS vs EKS 決策
- **Terraform**：lifecycle（init/plan/apply/destroy）、變數系統、module 設計、state 管理
- **GitHub Actions**：workflow 結構、觸發事件、matrix build、secrets 管理、快取優化

---

## Phase 2 — TDE 2.0 DevOps 完整專案（Week 3-4）

**目標**：透過端到端的 DevOps 專案，理解從 IaC 到 CI/CD 到監控的完整生命週期。

### 閱讀順序

| # | 文件 | 重點內容 |
|---|------|----------|
| 1 | `TDE2.0_01_Application.pdf` | 六層應用架構、REST API 設計、SQS + Lambda 解耦模式 |
| 2 | `TDE2.0_02_Infrastructure.pdf` | Terraform 15 檔 IaC 結構、VPC 網路架構、EKS 節點組件 |
| 3 | `TDE2.0_03_Installation.pdf` | 從零部署完整 SOP（~128 個 AWS 資源、~30 分鐘） |
| 4 | `TDE2.0_04_Checking_and_Testing.pdf` | kubectl 操作、CI/CD 驗證、Datadog 監控、日誌查詢 |
| 5 | `TDE2.0_05_Rollback.pdf` | ArgoCD 回滾流程、Auto-Sync 管理、git revert 策略 |
| 6 | `TDE2.0_06_Conclusion.pdf` | 專案總結、技能盤點 |
| 7 | `TDE2.0_專案分析報告.md` | 核心工程哲學：解耦、宣告式、可觀測、Everything as Code |
| 8 | `learning-path/platform-engineering-evolution.md` | 職涯定位：Traditional Ops → DevOps → Platform Engineering |

### 核心技術棧

| 分類 | 技術 |
|------|------|
| 應用層 | React.js SPA + Golang/Gin + wkhtmltopdf |
| 訊息/無伺服器 | AWS SQS + Lambda (Golang) |
| 資料層 | RDS Aurora MySQL + DynamoDB + S3 |
| 容器編排 | Amazon EKS (K8s 1.29) + Helm Charts |
| IaC | Terraform + Terraform Cloud |
| CI/CD | GitHub Actions (Self-hosted Runner) + ArgoCD (GitOps) |
| 監控告警 | Datadog (Metrics/Logs/APM) + PagerDuty |
| 網路/安全 | NLB + Nginx Ingress + Route 53 + ACM + Parameter Store |

### 關鍵概念理解檢查
- [ ] 能解釋為何用 SQS + Lambda 而非後端直接處理 PDF
- [ ] 能畫出 GitOps 三倉庫架構（Code Repo → CI Repo → CD Repo）
- [ ] 能說明回滾時為何在 CI Repo 做 git revert 而非 CD Repo
- [ ] 能解釋 Terraform 依賴順序（VPC → EKS → Helm → K8s resources）
- [ ] 能區分 RDS MySQL 和 DynamoDB 各自的職責

---

## Phase 3 — AWS ANS 網路深潛（Week 5-8）

**目標**：取得 AWS Advanced Networking Specialty (ANS-C01) 認證等級的網路知識。

| # | 主題 | 教材路徑 | 預估時間 |
|---|------|----------|----------|
| 1 | ANS 考試筆記（核心服務） | `aws/network/notes/memo.md` | 3-4 hr |
| 2 | ANS 深潛（PrivateLink、Split-Horizon DNS） | `aws/network/notes/memo2.md` | 3-4 hr |
| 3 | 6 個 Hands-on Labs | `aws/network/notes/AWS-ANS-Lab-Outline.md` | 10-13 hr |
| 4 | 7 篇網路專題文章 | `aws/network/articles/` | 5-7 hr |

### 6 個 Labs 概覽

| Lab | 主題 | 涵蓋考試範圍 |
|-----|------|-------------|
| Lab 1 | VPC Endpoints（Interface / Gateway / GWLB） | ~15% |
| Lab 2 | Load Balancer 選型（ALB / NLB / GWLB） | ~10% |
| Lab 3 | PrivateLink 架構 | ~10% |
| Lab 4 | Hybrid Network（VPN / TGW） | ~25% |
| Lab 5 | Edge Services（CloudFront / Global Accelerator） | ~10% |
| Lab 6 | Production-Grade Multi-Tier 架構 | ~15% |

### 關鍵知識點
- DX / VPN / DXGW 連接模式（~25% 考試比重）
- TGW 路由（~20%）
- Route 53 Resolver（~10%）
- BGP Route Selection
- 三層排錯法：Routing → Security → Application
- Hub-and-Spoke + Appliance Mode

---

## Phase 4 — AWS SCS 安全專攻（Week 9-12）

**目標**：取得 AWS Security Specialty (SCS) 認證等級的安全知識。

| # | 主題 | 教材路徑 | 預估時間 |
|---|------|----------|----------|
| 1 | 6 個安全 Labs | `aws/security/notes/lab-outlines.md` | 40-60 hr |

### 6 個 Labs 概覽

| Lab | 主題 | 核心技術 |
|-----|------|----------|
| Lab 1 | Threat Detection & Response | GuardDuty / Security Hub / EventBridge / Lambda |
| Lab 2 | Incident Response & Forensics | CloudTrail / Detective / Athena |
| Lab 3 | Advanced IAM | Organizations / SCP / Permission Boundary / ABAC |
| Lab 4 | Data Encryption | KMS / Secrets Manager / Envelope Encryption |
| Lab 5 | Network Security & DDoS | WAF / Shield / GWLB / Network Firewall |
| Lab 6 | Compliance & Monitoring | Config / CloudTrail / Audit Manager |

---

## Phase 5 — AWS SAP 架構大師（Week 13-16）

**目標**：取得 AWS Solutions Architect Professional (SAP) 認證等級的架構設計能力。

| # | 主題 | 教材路徑 | 預估時間 |
|---|------|----------|----------|
| 1 | 6 個架構 Labs | `aws/sap/notes/LAB_ROADMAP.md` | 20 hr |
| 2 | 系統架構設計文章 | `aws/articles/系統架構與組織結構.md` | 1-2 hr |

### 6 個 Labs 概覽

| Lab | 主題 | 核心技術 |
|-----|------|----------|
| Lab 1 | Multi-Account Foundation | Organizations / IAM Identity Center / Control Tower |
| Lab 2 | Security Monitoring & Response | GuardDuty / Inspector / Security Hub |
| Lab 3 | Network Security Layered Defense | WAF / Network Firewall / Firewall Manager |
| Lab 4 | Data Protection & Encryption | KMS / Macie / ACM |
| Lab 5 | Hybrid Cloud Migration | DMS / DataSync / VPN / TGW |
| Lab 6 | Global HA & Disaster Recovery | Multi-Region / Route 53 / Aurora Global DB / AWS Backup |

---

## 技術棧覆蓋全景

| 領域 | 技術 | 深度 |
|------|------|------|
| AWS Compute | EKS, EC2, Lambda | 深（Hands-on） |
| AWS Networking | VPC, TGW, DX, VPN, PrivateLink, NLB/ALB, Route 53, CloudFront | 極深（ANS 認證級） |
| AWS Security | IAM, Organizations, SCP, KMS, GuardDuty, WAF, Shield, Config | 極深（SCS 認證級） |
| AWS Storage/DB | S3, RDS Aurora, DynamoDB, ECR | 中深 |
| AWS Migration | DMS, DataSync, Storage Gateway | 中（SAP Labs） |
| IaC | Terraform (providers, modules, state, Terraform Cloud) | 深 |
| Containers | Docker, Kubernetes (EKS), Helm Charts | 中深 |
| CI/CD | GitHub Actions, ArgoCD (GitOps) | 深 |
| Monitoring | Datadog (Metrics/Logs/APM), PagerDuty | 中深 |
| Architecture | Microservices, Event-driven, GitOps, Platform Engineering | 概念到深入 |

---

## 職涯對齊

```
你的經驗                        目標職位
─────────────────────────────────────────────────
RHEL 升級自動化          ──→    Infrastructure Automation
Terraform IaC            ──→    Paved Road / Golden Path
FinOps 經驗              ──→    Self-Service Platform
TDE 2.0 DevOps 專案      ──→    Platform Engineering 實戰
ANS + SCS + SAP 認證     ──→    技術深度證明
```

> *「好的系統設計，是讓人不需要在凌晨三點爬起來手動修復問題。」*
