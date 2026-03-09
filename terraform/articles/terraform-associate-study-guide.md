# Terraform Associate 認證完整學習指南

**Updated: 2026-03-04**
**學習資源：[Bryan Krausen - Terraform Hands-On Labs](https://github.com/btkrausen/hashicorp/tree/master/terraform) + 實戰專案經驗**

---

## 目錄

| 考試目標 | 內容 |
|---------|------|
| [Objective 1](#objective-1-understand-infrastructure-as-code-iac-concepts) | 理解 IaC 概念 |
| [Objective 2](#objective-2-understand-terraforms-purpose-vs-other-iac) | Terraform 的定位與優勢 |
| [Objective 3](#objective-3-understand-terraform-basics) | Terraform 基礎 |
| [Objective 4](#objective-4-use-the-terraform-cli-outside-of-core-workflow) | CLI 進階操作 |
| [Objective 5](#objective-5-interact-with-terraform-modules) | 模塊化設計 |
| [Objective 6](#objective-6-navigate-terraform-workflow) | 核心工作流程 |
| [Objective 7](#objective-7-implement-and-maintain-state) | 狀態管理 |
| [Objective 8](#objective-8-read-generate-and-modify-configuration) | 讀取、生成與修改配置 |
| [Objective 9](#objective-9-understand-terraform-cloud-and-enterprise-capabilities) | Terraform Cloud / Enterprise |
| [實戰案例](#實戰案例s3--cloudfront--iam) | S3 + CloudFront + IAM 完整實現 |
| [考試要訣](#考試要訣) | 備考策略與重點提示 |
| [常見問題](#常見問題faq) | 故障排除與最佳實踐 |

---

## Objective 1: Understand Infrastructure as Code (IaC) Concepts

### 1a. 什麼是 Infrastructure as Code？

IaC 是透過**程式碼**（而非手動操作）來管理和配置基礎設施的方法。

```
傳統方式（手動）              IaC 方式（自動化）
────────────────              ─────────────────
登入 AWS Console              編寫 .tf 配置檔
點擊建立 EC2          →      terraform apply
手動配置安全組                 版本控制 + 可重複部署
無法追蹤變更                   Git 追蹤所有歷史
```

### 1b. IaC 的核心優勢

| 優勢 | 說明 |
|-----|------|
| **版本控制** | 所有配置都在 Git 中，可追蹤、可回滾 |
| **可重複性** | 同一份程式碼可部署到 dev/staging/prod |
| **一致性** | 消除「手動點擊」造成的環境差異（Configuration Drift） |
| **自動化** | 整合 CI/CD 管線，實現自動部署 |
| **文件化** | 程式碼即文件，團隊成員一看就懂 |
| **成本管理** | 快速建立和銷毀環境，避免資源閒置 |

> **考試重點：** IaC 解決的核心問題是 **Configuration Drift**（配置漂移）——手動管理的環境會隨時間產生不一致。

---

## Objective 2: Understand Terraform's Purpose (vs other IaC)

### 2a. 多雲與供應商無關的優勢

Terraform 的核心定位：**供應商無關（Provider-Agnostic）的 IaC 工具**。

```
                    Terraform
                       │
         ┌─────────────┼─────────────┐
         │             │             │
       AWS          Azure          GCP
    (aws_*)      (azurerm_*)     (google_*)
         │             │             │
    EC2, S3,      VM, Blob,     GCE, GCS,
    RDS, ...     SQL DB, ...    SQL, ...
```

**與其他 IaC 工具的比較：**

| 工具 | 類型 | 特色 | 適用場景 |
|-----|------|------|---------|
| **Terraform** | Declarative / Provisioning | 多雲、狀態管理、模組化 | 基礎設施配置 |
| **CloudFormation** | Declarative / Provisioning | AWS 原生、深度整合 | 純 AWS 環境 |
| **Ansible** | Procedural / Configuration | 無代理、SSH、配置管理 | 軟體安裝/配置 |
| **Pulumi** | Declarative / Provisioning | 使用通用程式語言 | 開發者偏好的 IaC |

> **考試重點：** Terraform 使用 **Declarative**（聲明式）方式——你描述「想要什麼」，Terraform 計算「如何達到」。

### 2b. State 的用途

State（狀態）是 Terraform 的核心機制，記錄了「你管理的基礎設施長什麼樣」。

```
terraform.tfstate 的作用：
├── 記錄已部署資源的真實狀態
├── 作為 plan 的對比基準（代碼 vs 狀態 vs 實際環境）
├── 追蹤資源之間的依賴關係
└── 提升 plan/apply 的效能（不需每次全量掃描）
```

> **考試重點：** State 的三個關鍵目的——**Mapping**（映射配置到真實資源）、**Metadata**（追蹤依賴）、**Performance**（快取資源屬性）。

---

## Objective 3: Understand Terraform Basics

### HCL 語法與配置區塊

Terraform 使用 **HCL（HashiCorp Configuration Language）** 編寫配置。

#### 核心區塊類型

| 區塊 | 用途 | 語法 |
|-----|------|------|
| `terraform {}` | 全域設定（版本、Provider、Backend） | `terraform { required_version = ">= 1.0" }` |
| `provider {}` | 雲平台連線設定 | `provider "aws" { region = "us-east-1" }` |
| `resource {}` | 建立/管理實際基礎設施 | `resource "aws_s3_bucket" "main" {}` |
| `data {}` | 查詢已存在的資源 | `data "aws_ami" "latest" {}` |
| `variable {}` | 定義輸入參數 | `variable "region" { type = string }` |
| `output {}` | 定義輸出值 | `output "id" { value = aws_s3_bucket.main.id }` |
| `locals {}` | 定義本地變數 | `locals { env = "prod" }` |
| `module {}` | 引用可複用模塊 | `module "vpc" { source = "./modules/vpc" }` |

### 3a. Provider 安裝與版本管理

```hcl
terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"    # Provider 來源
      version = "~> 5.0"           # 版本約束
    }
  }
}

provider "aws" {
  region = var.aws_region

  # 默認標籤：自動應用到所有 AWS 資源
  default_tags {
    tags = {
      Environment = var.environment
      Project     = var.project_name
      ManagedBy   = "Terraform"
    }
  }
}
```

#### 版本約束符號

```hcl
version = "= 5.0.0"       # 精確版本
version = "~> 5.0"         # >= 5.0, < 6.0（Pessimistic Constraint）
version = ">= 5.0"         # 大於等於 5.0
version = ">= 5.0, < 6"   # 版本範圍
```

> **考試重點：** `~>` 是 Pessimistic Constraint Operator。`~> 5.0` 允許 `5.x` 但不允許 `6.0`；`~> 5.0.1` 允許 `5.0.x` 但不允許 `5.1.0`。

### 3b. 外掛架構（Plugin-Based Architecture）

```
terraform init 做了什麼？
├── 1. 讀取 required_providers 區塊
├── 2. 從 registry.terraform.io 下載 Provider 外掛
├── 3. 安裝到 .terraform/providers/ 目錄
├── 4. 產生 .terraform.lock.hcl（鎖定版本）
└── 5. 初始化 Backend（狀態儲存）
```

Terraform 核心只負責**流程編排**，實際的 API 呼叫由 Provider 外掛處理。

### 3c. 多 Provider 使用

```hcl
# 多區域配置（使用 alias）
provider "aws" {
  alias  = "us-east-1"
  region = "us-east-1"
}

provider "aws" {
  alias  = "us-west-2"
  region = "us-west-2"
}

# 指定使用哪個 Provider
resource "aws_s3_bucket" "primary" {
  provider = aws.us-east-1
  bucket   = "primary-bucket"
}

resource "aws_s3_bucket" "backup" {
  provider = aws.us-west-2
  bucket   = "backup-bucket"
}
```

也可以使用不同類型的 Provider（例如同時使用 `aws` + `tls` + `random`）。

### 3d. Provider 的尋找與下載機制

```
Provider 來源優先順序：
1. .terraform/providers/（本地快取）
2. .terraform.lock.hcl（版本鎖定檔）
3. registry.terraform.io（公開 Registry）
4. 自訂 Mirror / Filesystem Mirror
```

```bash
# 更新 Provider 到符合約束的最新版本
terraform init -upgrade
```

### 3e. Provisioner（最後手段）

Provisioner 用於在資源建立後執行腳本，但 **HashiCorp 建議盡量避免使用**。

```hcl
resource "aws_instance" "web" {
  ami           = "ami-12345678"
  instance_type = "t3.micro"

  # local-exec：在執行 Terraform 的機器上執行
  provisioner "local-exec" {
    command = "echo ${self.public_ip} >> ip_list.txt"
  }

  # remote-exec：在遠端機器上執行（透過 SSH）
  provisioner "remote-exec" {
    inline = [
      "sudo apt update",
      "sudo apt install -y nginx"
    ]
  }
}
```

> **考試重點：** Provisioners are a **Last Resort**。優先使用 `user_data`（EC2）或 `cloud-init`，或配合 Ansible/Chef 等配置管理工具。

---

## Objective 4: Use the Terraform CLI (outside of core workflow)

### 4a. `terraform fmt` — 程式碼格式化

```bash
terraform fmt                    # 格式化當前目錄
terraform fmt -recursive         # 遞歸格式化所有子目錄
terraform fmt -check             # 只檢查，不修改（CI/CD 用）
terraform fmt -diff              # 顯示差異
```

> 強制團隊統一風格，建議加入 CI/CD pre-commit hook。

### 4b. `terraform taint` / `terraform apply -replace`

```bash
# 舊方式（已棄用）
terraform taint aws_instance.web

# 新方式（推薦）
terraform apply -replace="aws_instance.web"
```

**用途：** 強制在下次 apply 時重建某個資源（destroy + create）。

> **考試重點：** `taint` 在 Terraform 0.15.2+ 已被 `-replace` 取代，但考試可能兩個都考。

### 4c. `terraform import` — 導入已有資源

```bash
# 1. 先在配置中定義資源框架
resource "aws_s3_bucket" "imported" {
  bucket = "my-existing-bucket"
}

# 2. 執行導入
terraform import aws_s3_bucket.imported my-existing-bucket

# 3. 驗證配置匹配
terraform plan    # 應顯示「No changes」
```

> **考試重點：** `import` 只更新 State，不會自動產生配置代碼。你需要手動補齊 `.tf` 配置。

### 4d. `terraform workspace` — 工作區管理

```bash
terraform workspace list           # 列出所有工作區
terraform workspace new dev        # 建立工作區
terraform workspace select dev     # 切換工作區
terraform workspace show           # 顯示當前工作區
terraform workspace delete dev     # 刪除工作區
```

```hcl
# 在配置中使用工作區名稱
resource "aws_s3_bucket" "main" {
  bucket = "myapp-${terraform.workspace}"    # myapp-dev / myapp-prod
}
```

> **考試重點：** OSS Workspaces 共用相同的配置代碼但維護獨立的 State，適合簡單的多環境管理。預設工作區是 `default`，無法刪除。

### 4e. `terraform state` — 狀態操作

```bash
terraform state list                          # 列出所有受管資源
terraform state show aws_s3_bucket.main       # 顯示資源詳情
terraform state mv aws_s3_bucket.old aws_s3_bucket.new  # 重新命名資源
terraform state rm aws_s3_bucket.main         # 從狀態中移除（不刪除實際資源）
terraform state pull > backup.tfstate         # 匯出遠端狀態到本地
terraform state push backup.tfstate           # 上傳狀態到遠端
terraform state replace-provider old new      # 替換 Provider
```

### 4f. Debugging — 除錯日誌

```bash
# 啟用除錯日誌
export TF_LOG=TRACE        # 最詳細（TRACE > DEBUG > INFO > WARN > ERROR）
export TF_LOG_PATH=terraform.log   # 輸出到檔案

terraform apply

# 關閉除錯
unset TF_LOG
unset TF_LOG_PATH
```

> **考試重點：** `TF_LOG` 環境變數控制日誌等級。有效值為 `TRACE`、`DEBUG`、`INFO`、`WARN`、`ERROR`。

---

## Objective 5: Interact with Terraform Modules

### 模塊的概念

模塊 = **可複用的 Terraform 配置包**。每個包含 `.tf` 檔案的目錄都是一個模塊。

```
project/
├── modules/              # 可複用模塊
│   └── s3/
│       ├── main.tf       # 資源定義
│       ├── variables.tf  # 輸入變量（模塊介面）
│       ├── outputs.tf    # 輸出值
│       └── README.md
│
├── environments/
│   └── prod/
│       ├── main.tf       # 呼叫模塊
│       ├── variables.tf
│       ├── outputs.tf
│       └── terraform.tfvars
│
└── provider.tf
```

### 5a. 模塊來源選項

```hcl
# 本地路徑
module "vpc" {
  source = "./modules/vpc"
}

# Terraform Registry（公開模塊）
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.0.0"
}

# GitHub
module "vpc" {
  source = "git::https://github.com/org/repo.git//modules/vpc?ref=v1.0.0"
}

# S3 Bucket
module "vpc" {
  source = "s3::https://s3-eu-west-1.amazonaws.com/bucket/vpc.zip"
}
```

> **考試重點：** Registry 模塊必須使用 `version` 參數。Git 來源使用 `ref` 指定版本。本地路徑不需要也不支持版本約束。

### 5b. 模塊的輸入與輸出

```hcl
# === modules/s3/variables.tf ===
variable "bucket_name" {
  description = "S3 Bucket 名稱"
  type        = string
}

variable "enable_versioning" {
  description = "是否啟用版本控制"
  type        = bool
  default     = false
}

# === modules/s3/outputs.tf ===
output "bucket_id" {
  description = "S3 Bucket ID"
  value       = aws_s3_bucket.this.id
}

output "bucket_arn" {
  description = "S3 Bucket ARN"
  value       = aws_s3_bucket.this.arn
}

# === 呼叫端 main.tf ===
module "s3_primary" {
  source = "../../modules/s3"

  bucket_name       = "${var.project_name}-primary"
  enable_versioning = true
}

# 使用模塊輸出
output "primary_bucket_id" {
  value = module.s3_primary.bucket_id
}
```

### 5c. 模塊內的變數作用域

```
Root Module
├── var.region = "us-east-1"           # Root 的變數
├── module "s3" {
│     source      = "./modules/s3"
│     bucket_name = var.project_name   # 顯式傳遞給子模塊
│   }
│
└── modules/s3/ (Child Module)
    ├── var.bucket_name                # 只能存取自己的變數
    ├── 不能直接存取 var.region        # ← 父模塊的變數不可見
    └── output "id" → 父模塊透過 module.s3.id 存取
```

> **考試重點：** 子模塊**無法**直接存取父模塊的變數。所有資料必須透過 `variable`（輸入）和 `output`（輸出）顯式傳遞。

### 5d. 從公開 Registry 發現模塊

- 網址：[registry.terraform.io](https://registry.terraform.io/)
- 命名規範：`<NAMESPACE>/<NAME>/<PROVIDER>`（如 `terraform-aws-modules/vpc/aws`）
- 每個模塊頁面顯示：Inputs、Outputs、Resources、Dependencies

### 5e. 模塊版本

```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"    # 使用相同的版本約束語法
}
```

> `terraform init` 時下載模塊；`terraform init -upgrade` 更新到符合約束的最新版本。

---

## Objective 6: Navigate Terraform Workflow

### 6a. 核心工作流程：Write → Plan → Apply

```
1. Write（編寫）
   │  撰寫 .tf 配置檔
   ↓
2. Init（初始化：terraform init）
   │  下載 Provider、初始化 Backend
   ↓
3. Plan（規劃：terraform plan）
   │  比對：配置 vs 狀態 vs 實際環境
   │  產出執行計劃（+ / - / ~）
   ↓
4. Apply（應用：terraform apply）
   │  執行變更、更新 State
   ↓
5. Destroy（銷毀：terraform destroy）
      移除所有受管資源
```

### 6b–6f. 核心命令詳解

#### `terraform init`

```bash
terraform init                   # 標準初始化
terraform init -upgrade          # 更新 Provider 和模塊
terraform init -migrate-state    # 切換 Backend 時遷移狀態
terraform init -reconfigure      # 重新設定 Backend（不遷移）
terraform init -backend=false    # 跳過 Backend 初始化
```

#### `terraform validate`

```bash
terraform validate               # 檢查語法和內部一致性
```

> 只檢查配置語法，不會連線到任何雲平台 API。

#### `terraform plan`

```bash
terraform plan                          # 生成執行計劃
terraform plan -out=tfplan              # 儲存計劃到檔案
terraform plan -destroy                 # 預覽銷毀
terraform plan -var="key=value"         # 指定變數
terraform plan -var-file="prod.tfvars"  # 使用變數檔
terraform plan -json | jq              # JSON 格式輸出
terraform plan -refresh=false          # 跳過狀態刷新（加速）
terraform plan -parallelism=20         # 調整並行度
```

#### `terraform apply`

```bash
terraform apply                         # 互動式確認
terraform apply tfplan                  # 應用已儲存的計劃
terraform apply -auto-approve           # 自動確認（CI/CD）
terraform apply -target=aws_s3_bucket.main  # 只應用特定資源
terraform apply -replace="aws_instance.web" # 強制重建資源
```

#### `terraform destroy`

```bash
terraform destroy                       # 互動式確認銷毀
terraform destroy -auto-approve         # 自動確認
terraform destroy -target=aws_s3_bucket.main  # 只銷毀特定資源
```

---

## Objective 7: Implement and Maintain State

### 7a. 預設 Local Backend

```
.
├── terraform.tfstate          # 當前狀態（JSON 格式）
├── terraform.tfstate.backup   # 上一次的狀態備份
└── .terraform/                # Provider 和模塊快取
    ├── providers/
    └── modules/
```

> **考試重點：** 預設的 Local Backend 將狀態存在當前目錄的 `terraform.tfstate` 檔案中。

### 7b. State Locking（狀態鎖定）

```hcl
# S3 + DynamoDB 實現狀態鎖定
terraform {
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"    # 鎖定用
  }
}
```

```
鎖定機制運作方式：
1. terraform plan/apply 開始時 → 取得鎖
2. 其他人嘗試操作 → 鎖衝突，需等待
3. 操作完成 → 釋放鎖
4. 異常退出 → terraform force-unlock <LOCK_ID>
```

> **考試重點：** 不是所有 Backend 都支持鎖定。S3 + DynamoDB 支持，Local 也支持，但 HTTP Backend 不一定支持。

### 7c. Backend 認證方式

```bash
# 方式 1：環境變數（推薦）
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."

# 方式 2：共用認證設定
provider "aws" {
  shared_credentials_files = ["~/.aws/credentials"]
  profile                  = "production"
}

# 方式 3：IAM Role（EC2 / ECS / Lambda）
# 無需額外設定，自動使用 Instance Profile
```

### 7d. 遠端狀態儲存

```hcl
# S3 Backend（最常用）
terraform {
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}

# Terraform Cloud Backend
terraform {
  cloud {
    organization = "my-org"
    workspaces {
      name = "my-workspace"
    }
  }
}
```

**狀態遷移（Local → Remote）：**

```bash
# 1. 添加 backend 配置到 .tf 檔
# 2. 執行遷移
terraform init -migrate-state
```

### 7e. `terraform refresh`

```bash
terraform refresh    # 已棄用，改用：
terraform apply -refresh-only
```

> 從雲平台 API 讀取實際狀態，更新 State 檔案（不做任何變更）。

### 7f. Backend 配置與 Partial Configuration

```bash
# 完整配置寫在 .tf 中
terraform {
  backend "s3" {
    bucket = "my-state"
    key    = "terraform.tfstate"
    region = "us-east-1"
  }
}

# 部分配置（Partial Configuration）—— 敏感資訊在初始化時傳入
terraform init \
  -backend-config="access_key=AKIA..." \
  -backend-config="secret_key=..."

# 或使用檔案
terraform init -backend-config=backend.hcl
```

### 7g. State 中的敏感資料

```hcl
# 標記變數為敏感
variable "db_password" {
  type      = string
  sensitive = true    # plan/apply 輸出中不顯示
}

# 標記 output 為敏感
output "password" {
  value     = var.db_password
  sensitive = true
}
```

> **考試重點：** `sensitive = true` 只影響 CLI 輸出的顯示。State 檔案中**仍然以明文儲存**，所以必須加密 State 檔案。

### 狀態安全最佳實踐

```hcl
# 1. 加密 State
backend "s3" {
  encrypt = true
}

# 2. 阻止公開存取
resource "aws_s3_bucket_public_access_block" "state" {
  bucket                  = aws_s3_bucket.state.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# 3. 啟用版本控制（可回滾狀態）
resource "aws_s3_bucket_versioning" "state" {
  bucket = aws_s3_bucket.state.id
  versioning_configuration {
    status = "Enabled"
  }
}

# 4. .gitignore
# terraform.tfstate*
# .terraform/
# *.tfvars
```

---

## Objective 8: Read, Generate, and Modify Configuration

### 8a. 變數與輸出

#### 變數類型

```hcl
# 基本類型
variable "name"   { type = string }
variable "count"  { type = number }
variable "enable" { type = bool }

# 集合類型（Collection）
variable "cidrs"  { type = list(string) }
variable "tags"   { type = map(string) }
variable "ids"    { type = set(string) }

# 結構類型（Structural）
variable "config" {
  type = object({
    engine   = string
    version  = string
    instance = string
  })
}

variable "rules" {
  type = tuple([string, number, bool])
}
```

#### 變數賦值優先順序（由低到高）

```
1. default 值（最低）
2. terraform.tfvars / terraform.tfvars.json（自動載入）
3. *.auto.tfvars / *.auto.tfvars.json（自動載入，字母順序）
4. -var-file="file.tfvars"（命令列指定）
5. -var="key=value"（命令列指定）
6. TF_VAR_name 環境變數（最高）
```

> **考試重點：** 優先順序是高頻考點。環境變數和 `-var` 的優先級高於 `.tfvars` 檔案。

#### 變數驗證

```hcl
variable "environment" {
  type = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "環境必須是 dev、staging 或 prod 之一。"
  }
}

variable "instance_count" {
  type = number
  validation {
    condition     = var.instance_count > 0 && var.instance_count <= 10
    error_message = "實例數量必須在 1-10 之間。"
  }
}
```

#### Local Values

```hcl
locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }

  bucket_name = "${var.project_name}-${var.environment}"
}

resource "aws_s3_bucket" "main" {
  bucket = local.bucket_name
  tags   = local.common_tags
}
```

> **考試重點：** `variable` = 外部輸入，`locals` = 內部計算值。Locals 不能被外部覆蓋。

### 8b. 安全的密鑰注入

```hcl
# ❌ 不安全
resource "aws_db_instance" "main" {
  password = "MyPassword123"
}

# ✅ 使用環境變數
variable "db_password" {
  type      = string
  sensitive = true
}

# ✅ 使用 AWS Secrets Manager
data "aws_secretsmanager_secret_version" "db" {
  secret_id = "prod/db/password"
}

resource "aws_db_instance" "main" {
  password = jsondecode(
    data.aws_secretsmanager_secret_version.db.secret_string
  )["password"]
}

# ✅ 使用 HashiCorp Vault
data "vault_generic_secret" "db" {
  path = "secret/data/db"
}
```

### 8c. 集合與結構類型

```hcl
# list — 有序集合，可重複
variable "subnets" {
  type    = list(string)
  default = ["10.0.1.0/24", "10.0.2.0/24"]
}

# map — 鍵值對
variable "ami_map" {
  type = map(string)
  default = {
    us-east-1 = "ami-12345"
    us-west-2 = "ami-67890"
  }
}

# set — 無序集合，不可重複
variable "unique_ids" {
  type = set(string)
}

# object — 結構化型別（每個屬性可有不同型別）
variable "server" {
  type = object({
    name     = string
    size     = number
    enabled  = bool
  })
}

# tuple — 固定長度，固定型別的序列
variable "rule" {
  type = tuple([string, number, bool])
}
```

### 8d. Resource vs Data Source

```hcl
# Resource — 建立並管理新資源
resource "aws_s3_bucket" "new_bucket" {
  bucket = "my-new-bucket"
}

# Data Source — 查詢已存在的資源（唯讀）
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]  # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-*-amd64-server-*"]
  }
}

resource "aws_instance" "web" {
  ami = data.aws_ami.ubuntu.id    # 使用查詢結果
}
```

### 8e. 資源定址與引用

```hcl
# 引用同類型資源
aws_s3_bucket.main.id
aws_s3_bucket.main.arn

# 引用 Data Source
data.aws_ami.ubuntu.id

# 引用 Module Output
module.vpc.vpc_id

# 引用 Variable
var.region

# 引用 Local
local.common_tags

# 引用 Terraform 內建
terraform.workspace
path.module
path.root
```

### 8f. 內建函數

```hcl
# 字串函數
upper("hello")                    # "HELLO"
lower("HELLO")                    # "hello"
format("Hello, %s!", "World")     # "Hello, World!"
join(", ", ["a", "b", "c"])       # "a, b, c"
split(",", "a,b,c")              # ["a", "b", "c"]
trimspace("  hello  ")           # "hello"

# 集合函數
length(["a", "b", "c"])          # 3
contains(["a", "b"], "a")        # true
merge({a=1}, {b=2})              # {a=1, b=2}
flatten([[1,2], [3,4]])          # [1,2,3,4]
keys({a=1, b=2})                 # ["a", "b"]
values({a=1, b=2})               # [1, 2]
lookup({a=1}, "a", 0)            # 1
element(["a","b","c"], 1)        # "b"
toset(["a", "b", "a"])           # toset(["a", "b"])

# 檔案系統函數
file("${path.module}/script.sh")        # 讀取檔案內容
filebase64("${path.module}/cert.pem")   # Base64 編碼讀取
templatefile("template.tftpl", {name="World"})  # 模板渲染

# 編碼函數
jsonencode({key = "value"})      # '{"key":"value"}'
jsondecode('{"key":"value"}')    # {key = "value"}
base64encode("hello")            # "aGVsbG8="
base64decode("aGVsbG8=")         # "hello"

# 類型轉換
tostring(42)                     # "42"
tonumber("42")                   # 42
tobool("true")                   # true
tolist(toset(["a","b"]))        # ["a", "b"]
tomap({a = "1"})                # {a = "1"}

# 條件與邏輯
coalesce("", "default")         # "default"
try(var.optional.field, "fallback")  # 安全存取

# 網路函數
cidrhost("10.0.0.0/24", 5)      # "10.0.0.5"
cidrsubnet("10.0.0.0/16", 8, 1) # "10.0.1.0/24"
```

> **考試重點：** `lookup()`、`merge()`、`file()`、`templatefile()`、`cidrsubnet()` 是高頻考題。使用 `terraform console` 互動式測試函數。

### 8g. Dynamic Block

```hcl
variable "ingress_rules" {
  type = list(object({
    port        = number
    protocol    = string
    cidr_blocks = list(string)
  }))
  default = [
    { port = 80,  protocol = "tcp", cidr_blocks = ["0.0.0.0/0"] },
    { port = 443, protocol = "tcp", cidr_blocks = ["0.0.0.0/0"] },
  ]
}

resource "aws_security_group" "web" {
  name = "web-sg"

  dynamic "ingress" {
    for_each = var.ingress_rules
    content {
      from_port   = ingress.value.port
      to_port     = ingress.value.port
      protocol    = ingress.value.protocol
      cidr_blocks = ingress.value.cidr_blocks
    }
  }
}
```

> **考試重點：** Dynamic Block 中使用 `<block_label>.value` 存取迭代項目。`iterator` 參數可自訂迭代變數名稱。

### 8h. 內建依賴管理

```hcl
# 隱式依賴（Implicit）— Terraform 自動偵測
resource "aws_s3_bucket" "main" {
  bucket = "my-bucket"
}

resource "aws_s3_bucket_policy" "main" {
  bucket = aws_s3_bucket.main.id    # ← 引用 = 隱式依賴
  policy = jsonencode({...})
}

# 顯式依賴（Explicit）— 手動指定
resource "aws_instance" "app" {
  ami           = "ami-12345678"
  instance_type = "t3.micro"
  depends_on    = [aws_s3_bucket.main]    # ← 手動指定依賴
}
```

#### Lifecycle 規則

```hcl
resource "aws_instance" "web" {
  ami           = "ami-12345678"
  instance_type = "t3.micro"

  lifecycle {
    create_before_destroy = true     # 先建新的，再刪舊的
    prevent_destroy       = true     # 阻止 destroy 操作
    ignore_changes        = [tags]   # 忽略特定屬性變更
    # replace_triggered_by = [aws_s3_bucket.main.id]  # 當指定資源變更時重建
  }
}
```

> **考試重點：** `create_before_destroy` 解決零停機部署。`prevent_destroy` 保護重要資源。`ignore_changes` 忽略外部手動修改。

```bash
# 生成依賴圖
terraform graph | dot -Tpng > graph.png
terraform graph -type=plan | dot -Tpng > plan-graph.png
```

---

## Objective 9: Understand Terraform Cloud and Enterprise Capabilities

### Terraform Cloud 概述

```
Terraform Cloud 提供的功能：
├── Remote State 儲存與管理
├── Remote Plan/Apply 執行
├── VCS 整合（GitHub, GitLab, Bitbucket）
├── Private Module Registry
├── Sentinel Policy as Code
├── 團隊管理與 RBAC
├── Cost Estimation
└── Secure Variable Storage
```

### 9a. Sentinel、Registry 與 Workspaces

#### Sentinel — Policy as Code

```python
# 示例：強制所有 EC2 實例必須有 "Owner" 標籤
import "tfplan"

main = rule {
  all tfplan.resources.aws_instance as _, instances {
    all instances as _, r {
      r.applied.tags contains "Owner"
    }
  }
}
```

> **考試重點：** Sentinel 是 **Enterprise/Cloud 專屬**功能，OSS 版沒有。可在 plan 之後、apply 之前執行策略檢查。

#### Private Module Registry

- 團隊內部共享模塊
- 版本管理
- 與 VCS 整合自動發佈
- 命名規範：`terraform-<PROVIDER>-<NAME>`

### 9b. OSS Workspaces vs Cloud Workspaces

| 特性 | OSS Workspaces | Cloud Workspaces |
|-----|---------------|-----------------|
| **State 儲存** | 本地 / 自行管理的 Backend | Terraform Cloud 管理 |
| **變數管理** | `.tfvars` 檔案 | Web UI / API，支持加密 |
| **權限控制** | 無 | Team-based RBAC |
| **執行環境** | 本地機器 | Cloud 代管的 Runner |
| **VCS 整合** | 手動 | 自動觸發 Plan/Apply |
| **適用場景** | 個人/小團隊 | 團隊協作/企業環境 |

### 9c. Terraform Cloud 功能摘要

- **VCS Workflow：** Push 到 Git → 自動觸發 Plan → Review → Apply
- **CLI Workflow：** 本地執行 `terraform plan`，遠端執行 Apply
- **API Workflow：** 透過 API 觸發所有操作
- **Cost Estimation：** Apply 前估算資源費用
- **Run Tasks：** 整合第三方工具（安全掃描等）

---

## 實戰案例：S3 + CloudFront + IAM

> 以下案例來自 company-website-poc 專案的實際配置，展示完整的靜態網站託管架構。

### 架構圖

```
使用者
  │
  ↓
CloudFront (CDN)
  │ ← SSL/TLS (ACM Certificate)
  │ ← WAF (Web ACL)
  ↓
S3 Bucket (靜態內容)
  │ ← OAI (Origin Access Identity) 控制存取
  │ ← 版本控制 + 加密 + 生命週期管理
  ↓
S3 Logs Bucket (存取日誌)
```

### S3 完整配置

```hcl
# S3 Bucket
resource "aws_s3_bucket" "website" {
  bucket = "${var.project_name}-website"
  tags   = merge(var.tags, { Name = "Website Bucket" })
}

# 阻止公開存取
resource "aws_s3_bucket_public_access_block" "website" {
  bucket                  = aws_s3_bucket.website.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# 版本控制
resource "aws_s3_bucket_versioning" "website" {
  bucket = aws_s3_bucket.website.id
  versioning_configuration { status = "Enabled" }
}

# 伺服器端加密
resource "aws_s3_bucket_server_side_encryption_configuration" "website" {
  bucket = aws_s3_bucket.website.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
    bucket_key_enabled = true    # 降低 KMS API 呼叫成本
  }
}

# 生命週期管理（成本優化）
resource "aws_s3_bucket_lifecycle_configuration" "website" {
  bucket = aws_s3_bucket.website.id

  rule {
    id     = "archive-old-versions"
    status = "Enabled"

    noncurrent_version_transition {
      noncurrent_days = 30
      storage_class   = "GLACIER"
    }

    noncurrent_version_expiration {
      noncurrent_days = 90
    }

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}

# 強制 HTTPS
resource "aws_s3_bucket_policy" "enforce_ssl" {
  bucket = aws_s3_bucket.website.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid       = "DenyInsecureTransport"
      Effect    = "Deny"
      Principal = "*"
      Action    = "s3:*"
      Resource  = [
        aws_s3_bucket.website.arn,
        "${aws_s3_bucket.website.arn}/*"
      ]
      Condition = { Bool = { "aws:SecureTransport" = "false" } }
    }]
  })
}
```

### CloudFront 配置

```hcl
# OAI — 讓 CloudFront 安全存取 S3
resource "aws_cloudfront_origin_access_identity" "website" {
  comment = "OAI for ${var.project_name}"
}

resource "aws_cloudfront_distribution" "website" {
  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"
  http_version        = "http2"
  price_class         = "PriceClass_100"    # 只使用北美和歐洲節點（最便宜）
  aliases             = [var.domain_name, "www.${var.domain_name}"]

  origin {
    domain_name = aws_s3_bucket.website.bucket_regional_domain_name
    origin_id   = "S3Origin"
    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.website.cloudfront_access_identity_path
    }
  }

  default_cache_behavior {
    allowed_methods        = ["GET", "HEAD", "OPTIONS"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "S3Origin"
    compress               = true
    viewer_protocol_policy = "redirect-to-https"
    default_ttl            = 86400      # 1 天
    max_ttl                = 31536000   # 1 年

    forwarded_values {
      query_string = false
      cookies { forward = "none" }
    }
  }

  viewer_certificate {
    acm_certificate_arn      = aws_acm_certificate.website.arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }

  restrictions {
    geo_restriction { restriction_type = "none" }
  }
}
```

### IAM 角色配置模式

```hcl
# 標準 IAM Role 配置模式：Trust Policy + Permission Policy
resource "aws_iam_role" "service_role" {
  name = "${var.environment}-service-role"

  # Trust Policy — 誰可以 Assume 這個 Role
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "s3.amazonaws.com" }
    }]
  })
}

# Permission Policy — 這個 Role 可以做什麼
resource "aws_iam_role_policy" "service_policy" {
  name = "${var.environment}-service-policy"
  role = aws_iam_role.service_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:PutObject"]
        Resource = "${aws_s3_bucket.main.arn}/*"
      }
    ]
  })
}
```

---

## 考試要訣

### 準備策略

1. **動手實驗比死背重要**：在自己的 AWS 帳號中跑完所有 Lab，理解每個指令的效果
2. **理解「為什麼」**：不只知道正確答案，也要理解為什麼其他選項是錯的
3. **善用官方文件**：考題通常來自官方文件的措辭
4. **免費練習**：使用 `local`、`tls`、`random` Provider 做實驗，不會產生雲端費用

### 高頻考點清單

| 主題 | 重點 |
|------|------|
| **版本約束** | `~>` Pessimistic Constraint 的行為 |
| **變數優先順序** | env var > -var > -var-file > auto.tfvars > terraform.tfvars > default |
| **State** | 為什麼需要 State、State Locking、Sensitive Data in State |
| **Provisioner** | 是「Last Resort」，優先用 user_data/cloud-init |
| **Module** | 子模塊無法存取父模塊變數、Registry 命名規範 |
| **Workspace** | OSS vs Cloud Workspace 的差異 |
| **Sentinel** | Enterprise/Cloud 專屬功能 |
| **Backend** | Partial Configuration、Migration |
| **Lifecycle** | create_before_destroy / prevent_destroy / ignore_changes |
| **Dynamic Block** | 語法和迭代器使用 |

### 考試格式

- **題型：** 多選題、多選複選題、填空題
- **費用：** $70.50（PSI 監考）
- **時長：** 60 分鐘
- **及格線：** ~70%

---

## 常見問題（FAQ）

### 部署相關

**Q: 如何回滾更改？**
```bash
# 方式 1：Git 回退 + 重新 Apply
git checkout HEAD -- main.tf
terraform apply

# 方式 2：從 S3 版本控制恢復舊 State
aws s3api list-object-versions --bucket terraform-state --prefix terraform.tfstate
```

**Q: 如何只部署特定資源？**
```bash
terraform apply -target=aws_s3_bucket.main
terraform apply -target=module.s3_primary
```

**Q: 如何導入已有 AWS 資源？**
```bash
# 1. 寫出資源定義框架
resource "aws_s3_bucket" "imported" {
  bucket = "my-existing-bucket"
}

# 2. 導入
terraform import aws_s3_bucket.imported my-existing-bucket

# 3. 補齊配置，確保 plan 無變更
terraform plan
```

### 狀態相關

**Q: 不小心刪除了 terraform.tfstate？**
```bash
# 從遠端 Backend 恢復
terraform init -reconfigure

# 從 S3 備份恢復
aws s3 cp s3://bucket/terraform.tfstate.backup ./terraform.tfstate
terraform state push terraform.tfstate
```

**Q: 如何在團隊間共享狀態？**
→ 使用 S3 + DynamoDB Backend，或 Terraform Cloud。

### 安全相關

**Q: 敏感資訊如何處理？**
- 使用 `sensitive = true` 標記變數
- 使用 AWS Secrets Manager / HashiCorp Vault
- 絕不在 `.tf` 檔案中硬編碼密碼
- 將 `*.tfvars` 加入 `.gitignore`

**Q: 如何防止 State 檔案洩漏？**
- Backend 啟用 `encrypt = true`
- S3 Bucket 阻止公開存取
- 啟用版本控制以便回滾
- `.gitignore` 中排除 `terraform.tfstate*` 和 `.terraform/`

### 效能相關

**Q: 如何加速 `terraform plan`？**
```bash
terraform plan -parallelism=20       # 提高並行度（預設 10）
terraform plan -refresh=false        # 跳過狀態刷新（謹慎使用）
```

**Q: 大型專案如何組織？**
```
project/
├── modules/           # 可複用模塊
│   ├── networking/
│   ├── compute/
│   └── storage/
├── environments/      # 各環境獨立配置
│   ├── dev/
│   ├── staging/
│   └── prod/
└── global/            # 全域設定
    ├── provider.tf
    └── backend.tf
```

---

## 延伸學習資源

| 資源 | 連結 |
|------|------|
| Terraform 官方文件 | https://www.terraform.io/docs |
| AWS Provider 文件 | https://registry.terraform.io/providers/hashicorp/aws |
| 公開模塊 Registry | https://registry.terraform.io/modules |
| Bryan Krausen 課程 Labs | https://github.com/btkrausen/hashicorp/tree/master/terraform |
| Terraform Associate 學習指南 | https://developer.hashicorp.com/terraform/tutorials/certification |
| 練習考題（Udemy） | https://www.udemy.com/course/terraform-hands-on-labs |

---

**最後更新：2026-03-04**
**來源：Bryan Krausen Terraform Hands-On Labs 課程 + company-website-poc 實戰經驗**
