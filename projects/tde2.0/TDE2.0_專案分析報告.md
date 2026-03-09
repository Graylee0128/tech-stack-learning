# TDE 2.0 DevOps 專案分析報告

> **一句話定義**：這是一個 DevOps 學習專案，將一個「輸入 URL → 自動轉 PDF → 存雲端」的 Web App，從零部署到 AWS，並實現自動化 CI/CD、監控、回滾全流程。

---

## 一、應用程式是什麼

使用者登入後輸入任意網頁 URL，系統自動截圖轉成 PDF 存到雲端，可下載或刪除。功能簡單，但背後串接 6 個 AWS 服務同時協作。

### 1.1 API 端點一覽

| 動作 | Method | 路徑 |
|------|--------|------|
| 註冊 / 登入 | POST | `/api/v1/sign-up` / `/api/v1/sign-in` |
| 發送 PDF 請求 | POST | `/api/v1/request` |
| 列出檔案 | GET | `/api/v1/files` |
| 下載檔案 | GET | `/api/v1/file/:name` |
| 刪除檔案 | DELETE | `/api/v1/file/:name` |

---

## 二、系統架構拆解

### 2.1 六層架構

| 層級 | 技術 | 職責 |
|------|------|------|
| 前端 | React.js (SPA) | 使用者介面 |
| 後端 | Golang + Gin | REST API、JWT 認證、DB 溝通 |
| 訊息佇列 | AWS SQS | 緩衝請求，防止後端阻塞 |
| 無伺服器 | AWS Lambda (Golang) | 執行 HTML → PDF 轉換 |
| 資料庫 | RDS MySQL + DynamoDB | 用戶資料 + PDF 索引 |
| 物件儲存 | AWS S3 | 存放 PDF 檔案 |

### 2.2 一個請求的完整旅程

```
使用者輸入 URL
  → POST /api/v1/request
  → 後端驗證 JWT
  → 推送訊息到 SQS
  → Lambda 拉取訊息
      ├─ wkhtmltopdf 渲染 HTML
      ├─ 轉成 PDF
      ├─ 上傳到 S3
      └─ DynamoDB 記錄 {user_id: [filename]}
  → 前端顯示檔案，使用者下載
```

> **為何要 SQS + Lambda？** PDF 轉換是重 I/O 工作，讓後端直接做會被阻塞。SQS 像點餐紙條，Lambda 是專職廚師，分離後任一掛掉不影響另一方。

### 2.3 資料庫分工

| DB | 類型 | 存什麼 |
|----|------|--------|
| RDS MySQL | 關聯式 | 用戶帳密（MD5）、JWT Token |
| DynamoDB | NoSQL | `{username: [pdf_file_list]}` |

> 注意：JWT 是單設備登入，同帳號第二次登入會讓前一個 Token 失效。

---

## 三、雲端基礎設施

### 3.1 Terraform IaC 檔案結構

```
prod/
├── 01-main.tf          # Provider 設定
├── 02-vpc.tf           # 虛擬網路
├── 03-key-pair.tf      # SSH Key
├── 04-eks.tf           # Kubernetes 叢集
├── 05-rds.tf           # MySQL 資料庫
├── 06-dynamodb.tf      # NoSQL 資料庫
├── 07-ecr.tf           # Docker Image 倉庫
├── 08-s3.tf            # 物件儲存
├── 09-lambda.tf        # 無伺服器函數
├── 10-sqs.tf           # 訊息佇列
├── 11-datadog.tf       # 監控整合
├── 12-helm.tf          # K8s 操作元件
├── 13-acm_and_route53.tf  # SSL + DNS
├── 14-kubernetes.tf    # K8s 資源
├── 15-bastion_host.tf  # 跳板機
├── crd-helm-chart/     # GitHub Actions Runner 自訂 Helm Chart
└── helm-chart-values/  # ArgoCD Apps 的 values.yaml
```

### 3.2 網路架構

```
Internet
  └─ AWS NLB（終止 TLS，憑證來自 ACM）
       └─ EKS（VPC 10.0.0.0/16）
            ├─ Public Subnets：10.0.4.0/24, 10.0.5.0/24（NAT Gateway）
            ├─ Private Subnets：10.0.1.0/24, 10.0.2.0/24（Worker Nodes）
            └─ DB Subnets：10.0.41.0/24, 10.0.42.0/24（RDS）
```

- 跨 2 個 AZ，防單點故障
- EKS 使用 Cluster Autoscaler，預設 2 個 Worker Node（t3.large）

### 3.3 EKS 節點內的 6 個元件

| 元件 | 類型 | 用途 |
|------|------|------|
| Nginx Ingress Controller | 操作 | 反向代理，路由進入流量 |
| ArgoCD | 操作 | GitOps CD，自動同步 Git → K8s |
| GitHub Actions Runner Controller | 操作 | 管理 CI Self-hosted Runner |
| ACK Lambda Controller | 操作 | 用 K8s 方式管理 Lambda 函數 |
| Datadog Agent | 監控 | 收集叢集 Metrics/Logs |
| Application（API + UI + HPA） | 應用 | 前後端 Pod + 水平自動擴展 |

### 3.4 Terraform 依賴順序

```
VPC
 ├─ RDS
 ├─ EKS ──→ HELM ──→ KUBERNETES
 │    ├─ S3
 │    ├─ ECR
 │    │    └─ LAMBDA
 │    │         ├─ DYNAMODB
 │    │         └─ SQS
 │    └─ DATADOG
```

---

## 四、部署流程

### 4.1 基礎設施部署（~30 分鐘）

```bash
# 前置條件
# - app.terraform.io 帳號
# - AWS 帳號（含 Host Zone）
# - 網域名稱

# 步驟
1. Terraform Cloud → New Workspace → Version Control Workflow
2. 連接 GitHub repo（tntk-infra）
3. Working Directory 設為 prod/
4. 填入 12 個變數（aws_region, base_domain, datadog_api_key 等）
5. Start Plan → 確認無誤 → Confirm & Apply
   # 建立約 128 個資源
```

### 4.2 應用程式部署

```bash
# Step 1：設定 GitHub CI 變數
gh variable set ACCOUNT_ID --repo tntk-io/tntk-ci --body "012345678901"
gh variable set AWS_REGION  --body "us-east-1"
gh variable set BASE_DOMAIN --body "your-domain.com"
gh secret set API_TOKEN_GITHUB --body "ghp_xxxxx"

# Step 2：觸發 CI
git commit --allow-empty -m "init deploy"
git push

# Step 3：等待 CI 完成（3 個 Job：get_inputs → build → k8s_manifest_storing）

# Step 4：取得 ArgoCD 密碼
aws eks update-kubeconfig --name eks-prod
kubectl -n argocd get secrets argocd-initial-admin-secret -o json \
  | jq -r .data.password | base64 -d

# Step 5：登入 ArgoCD 確認 Synced + Healthy
# https://argo.prod.your-domain.com
```

---

## 五、CI/CD 設計

### 5.1 GitOps 三倉庫架構

```
開發者 push code
  → CI Repo（tntk-ci）
      GitHub Actions 觸發
        ├─ Build Docker Image（api / ui / lambda）
        ├─ Tag：{short_sha}
        ├─ Push 到 ECR
        └─ 更新 CD Repo 的 manifest（image tag）
              → ArgoCD 偵測到變化
                  → 自動 Deploy 到 EKS
```

### 5.2 觸發方式

| 方式 | 行為 | 結果 |
|------|------|------|
| commit push | 新 Image Tag = 新 SHA | CI + CD 都執行 |
| 手動觸發 | Image Tag 不變 | 只跑 CI，CD 跳過（SHA 相同） |

---

## 六、版本回滾

ArgoCD 記錄每次部署對應的 Commit，回滾流程：

```
1. ArgoCD → App Settings → DISABLE AUTO-SYNC
2. History and Rollback → 選擇穩定版本 Commit → Rollback
3. 確認舊版運作正常
4. CI Repo 執行 git revert（不要在 CD Repo 做）
   git revert <broken_commit>..<latest_commit>
5. push → 等 CI/CD 完成 → 重新 ENABLE AUTO-SYNC
```

> **關鍵**：Revert 做在 CI Repo，保留 CI ↔ CD 的 Commit 對應關係。回滾後 ArgoCD 狀態顯示 `OutOfSync`（正常，表示當前非最新 commit）。

---

## 七、監控與告警

### 7.1 監控架構

```
EKS Worker Nodes（Datadog Agent DaemonSet）
  └─ 收集 Metrics / Logs / APM
       └─ Datadog SaaS
            └─ Monitor 觸發 Alert
                 └─ PagerDuty（SMS / 電話通知）
```

### 7.2 日誌查詢方式

```bash
# 應用程式 Pod 日誌
kubectl logs -n application <pod-name>

# Lambda 日誌
# AWS Console → CloudWatch → /aws/lambda/demo-app-eks-lambda

# RDS 錯誤日誌
# AWS Console → CloudWatch → /aws/rds/cluster/rds/error

# Datadog Dashboard
# Kubernetes Cluster Overview / AWS Overview / Argo CD Overview
```

---

## 八、密鑰管理

所有密鑰存 **AWS Parameter Store**，不用 K8s Secrets。

| 優點 | 說明 |
|------|------|
| 集中管理 | 所有服務統一讀取 |
| IAM 控管 | Role-based 存取，細粒度權限 |
| 稽核追蹤 | 自動記錄存取紀錄 |
| 不進 Git | 避免密鑰意外外洩 |

---

## 九、完整技術栈

| 分類 | 技術 |
|------|------|
| 前端 | React.js SPA |
| 後端 | Golang + Gin + GORM |
| PDF 引擎 | wkhtmltopdf（via go-wkhtmltopdf） |
| 容器編排 | Amazon EKS（Kubernetes 1.29） |
| IaC | Terraform + Terraform Cloud |
| CD | ArgoCD（GitOps） |
| CI | GitHub Actions（Self-hosted Runner） |
| Image 倉庫 | Amazon ECR |
| 訊息佇列 | AWS SQS |
| 無伺服器 | AWS Lambda（Golang） |
| 關聯式 DB | AWS RDS Aurora（MySQL） |
| NoSQL DB | AWS DynamoDB |
| 物件儲存 | AWS S3 |
| 負載平衡 | AWS NLB + Nginx Ingress Controller |
| DNS | AWS Route53 |
| SSL | AWS ACM |
| K8s 套件 | Helm Charts |
| Lambda 管理 | ACK Lambda Controller |
| 監控 | Datadog（Metrics + Logs + APM） |
| 告警 | PagerDuty |
| 密鑰 | AWS Parameter Store |
| 跳板機 | Bastion Host |

---

## 十、核心工程哲學總結

**1. 解耦（Decoupling）**
SQS + Lambda 把 PDF 轉換從後端拆出來。任一方故障，不拖垮整體。

**2. 宣告式（Declarative）**
Terraform 和 ArgoCD 都是「告訴它要什麼狀態，它自己達到」。比命令式更穩定、可追蹤。

**3. 可觀測（Observability）**
Metrics → Logs → Alerts，三層覆蓋。問題發生前預警，發生後快速定位。

**4. Everything as Code**
基礎設施是程式碼、部署是程式碼、設定是程式碼。人不碰生產環境，Git 是唯一入口。

---

> *「好的系統設計，是讓人不需要在凌晨三點爬起來手動修復問題。這，就是 DevOps 的目標。」*
