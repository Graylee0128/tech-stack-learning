# Objective 5: Terraform 模塊化設計

**考試目標：** Interact with Terraform Modules
**學習資源：** [Bryan Krausen Labs](https://github.com/btkrausen/hashicorp/tree/master/terraform) | [Modules Documentation](https://www.terraform.io/docs/language/modules/index.html)

---

## 對應 Labs

| 子目標 | Lab |
|--------|-----|
| 5a. Contrast module source options | Terraform Modules, Sourcing Terraform Modules |
| 5b. Interact with module inputs and outputs | Terraform Module Inputs and Outputs |
| 5c. Describe variable scope within modules | Terraform Module Variables Scope |
| 5d. Discover modules from public registry | Consuming Terraform Modules from Public Module Registry |
| 5e. Defining module version | Versioning Terraform Modules |

---

## 模塊的概念

模塊 = **可複用的 Terraform 配置包**。每個包含 `.tf` 檔案的目錄都是一個模塊。

```
project/
├── modules/              # 可複用模塊（Child Modules）
│   └── s3/
│       ├── main.tf       # 資源定義
│       ├── variables.tf  # 輸入變量（模塊介面）
│       ├── outputs.tf    # 輸出值
│       └── README.md
│
├── environments/
│   └── prod/
│       ├── main.tf       # 呼叫模塊（Root Module）
│       ├── variables.tf
│       ├── outputs.tf
│       └── terraform.tfvars
│
└── provider.tf
```

### Root Module vs Child Module

| | Root Module | Child Module |
|--|------------|-------------|
| **定義** | `terraform plan/apply` 執行的目錄 | 被 `module {}` 呼叫的模塊 |
| **角色** | 入口點，呼叫子模塊 | 被呼叫、可複用的配置包 |
| **Provider** | 在這裡定義 Provider | 繼承自 Root Module |

---

## 5a. 模塊來源選項

```hcl
# 1. 本地路徑（Local Path）
module "vpc" {
  source = "./modules/vpc"
  # source = "../shared/modules/vpc"
}

# 2. Terraform Registry（公開模塊）
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.0.0"    # ← Registry 模塊必須指定版本
}

# 3. GitHub
module "vpc" {
  source = "git::https://github.com/org/repo.git//modules/vpc?ref=v1.0.0"
  #                                              ↑ 雙斜線    ↑ Git ref
}

# 4. Bitbucket
module "vpc" {
  source = "bitbucket.org/org/terraform-vpc"
}

# 5. S3 Bucket
module "vpc" {
  source = "s3::https://s3-eu-west-1.amazonaws.com/bucket/vpc.zip"
}

# 6. GCS Bucket
module "vpc" {
  source = "gcs::https://www.googleapis.com/storage/v1/bucket/vpc.zip"
}
```

> **考試重點：**
> - **Registry** 模塊必須使用 `version` 參數
> - **Git** 來源使用 `ref` 指定版本（tag/branch/commit）
> - **本地路徑**不需要也不支持版本約束
> - Git URL 中用 `//` 分隔 repo 和子目錄路徑

---

## 5b. 模塊的輸入與輸出

### 模塊定義（Child Module）

```hcl
# === modules/s3/variables.tf ===
variable "bucket_name" {
  description = "S3 Bucket 名稱"
  type        = string
  # 無 default → 必填參數
}

variable "enable_versioning" {
  description = "是否啟用版本控制"
  type        = bool
  default     = false    # 有 default → 可選參數
}

variable "tags" {
  description = "資源標籤"
  type        = map(string)
  default     = {}
}

# === modules/s3/main.tf ===
resource "aws_s3_bucket" "this" {
  bucket = var.bucket_name
  tags   = var.tags
}

resource "aws_s3_bucket_versioning" "this" {
  count  = var.enable_versioning ? 1 : 0
  bucket = aws_s3_bucket.this.id
  versioning_configuration { status = "Enabled" }
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

output "bucket_domain_name" {
  description = "S3 域名"
  value       = aws_s3_bucket.this.bucket_regional_domain_name
}
```

### 呼叫模塊（Root Module）

```hcl
# === main.tf ===
module "s3_primary" {
  source = "../../modules/s3"

  bucket_name       = "${var.project_name}-primary"
  enable_versioning = true
  tags              = local.common_tags
}

# 使用模塊輸出
output "primary_bucket_id" {
  value = module.s3_primary.bucket_id
}

# 使用 for_each 建立多個模塊實例
module "s3_buckets" {
  for_each = toset(["data", "logs", "archive"])

  source = "../../modules/s3"

  bucket_name       = "${var.project_name}-${each.value}"
  enable_versioning = each.value == "data"
  tags              = merge(local.common_tags, { Name = each.value })
}

output "all_bucket_ids" {
  value = { for name, mod in module.s3_buckets : name => mod.bucket_id }
}
```

---

## 5c. 模塊內的變數作用域

```
Root Module
├── var.region = "us-east-1"           # Root 的變數
├── var.project_name = "myapp"
│
├── module "s3" {
│     source      = "./modules/s3"
│     bucket_name = var.project_name   # ← 顯式傳遞
│   }
│
└── modules/s3/ (Child Module)
    ├── var.bucket_name = "myapp"      # ← 只能存取自己的變數
    ├── ❌ var.region                  # ← 父模塊的變數不可見！
    └── output "id" → 父模塊透過 module.s3.id 存取
```

### 關鍵規則

1. **子模塊無法直接存取父模塊的變數** — 必須透過 `variable` 顯式傳遞
2. **父模塊無法直接存取子模塊的資源** — 必須透過 `output` 暴露
3. **Provider 從 Root Module 繼承** — 子模塊不需要重新定義 Provider

```hcl
# ❌ 錯誤：子模塊無法直接用 var.region
# modules/s3/main.tf
resource "aws_s3_bucket" "this" {
  bucket = "${var.region}-bucket"    # ← 如果子模塊沒有定義 var.region 就會報錯
}

# ✅ 正確：透過 variable 傳入
# modules/s3/variables.tf
variable "region" { type = string }

# root main.tf
module "s3" {
  source = "./modules/s3"
  region = var.region    # ← 顯式傳遞
}
```

> **考試重點：** 子模塊**無法**直接存取父模塊的變數。所有資料必須透過 `variable`（輸入）和 `output`（輸出）顯式傳遞。

---

## 5d. 從公開 Registry 發現模塊

### Terraform Registry

- 網址：[registry.terraform.io](https://registry.terraform.io/)
- 命名規範：`<NAMESPACE>/<NAME>/<PROVIDER>`

### 常用官方模塊

| 模塊 | 用途 |
|------|------|
| `terraform-aws-modules/vpc/aws` | VPC 網路配置 |
| `terraform-aws-modules/ec2-instance/aws` | EC2 實例 |
| `terraform-aws-modules/s3-bucket/aws` | S3 儲存桶 |
| `terraform-aws-modules/rds/aws` | RDS 資料庫 |
| `terraform-aws-modules/security-group/aws` | 安全組 |
| `terraform-aws-modules/iam/aws` | IAM 角色/策略 |

### Registry 模塊頁面資訊

```
每個模塊頁面顯示：
├── Inputs — 所有輸入變數及其類型、預設值
├── Outputs — 所有輸出值
├── Resources — 會建立的資源列表
├── Dependencies — 依賴的其他模塊
├── Versions — 所有版本歷史
└── Usage — 範例代碼
```

### 發佈模塊到 Registry 的要求

1. 必須在 GitHub 上
2. Repo 命名：`terraform-<PROVIDER>-<NAME>`
3. 必須有 `main.tf`、`variables.tf`、`outputs.tf`
4. 使用 Git Tag 做版本（Semantic Versioning）

---

## 5e. 模塊版本

```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.0.0"        # 精確版本
  # version = "~> 5.0"     # Pessimistic Constraint
  # version = ">= 5.0"     # 最低版本
}
```

### 版本管理

```bash
# 初次下載模塊
terraform init

# 更新到符合版本約束的最新版本
terraform init -upgrade

# 模塊快取位置
.terraform/modules/
```

> **注意：** 本地路徑模塊（`source = "./modules/xxx"`）不支持 `version` 參數。

---

## 實戰範例：完整模塊設計

```hcl
# === modules/s3/variables.tf ===
variable "bucket_name" {
  description = "S3 Bucket 名稱"
  type        = string
}

variable "enable_versioning" {
  type    = bool
  default = false
}

variable "sse_algorithm" {
  type    = string
  default = "AES256"
  validation {
    condition     = contains(["AES256", "aws:kms"], var.sse_algorithm)
    error_message = "只支持 AES256 或 aws:kms"
  }
}

variable "tags" {
  type    = map(string)
  default = {}
}

# === modules/s3/main.tf ===
resource "aws_s3_bucket" "this" {
  bucket = var.bucket_name
  tags   = var.tags
}

resource "aws_s3_bucket_versioning" "this" {
  count  = var.enable_versioning ? 1 : 0
  bucket = aws_s3_bucket.this.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "this" {
  bucket = aws_s3_bucket.this.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = var.sse_algorithm
    }
  }
}

# === modules/s3/outputs.tf ===
output "bucket_id"  { value = aws_s3_bucket.this.id }
output "bucket_arn" { value = aws_s3_bucket.this.arn }
output "bucket_domain_name" {
  value = aws_s3_bucket.this.bucket_regional_domain_name
}
```

---

## 重點整理

| 考點 | 要記住的 |
|------|---------|
| Module 是什麼 | 包含 .tf 檔案的目錄 = 一個模塊 |
| Root vs Child | Root = 執行目錄，Child = 被呼叫的 |
| Source 類型 | Local, Registry, Git, S3, GCS |
| Registry 版本 | 必須指定 `version`，Local 不需要 |
| 變數作用域 | 子模塊不能存取父模塊變數 |
| 資料傳遞 | variable（輸入）+ output（輸出） |
| 命名規範 | `terraform-<PROVIDER>-<NAME>` |

---

**上一篇：** [04-terraform-cli.md](04-terraform-cli.md)
**下一篇：** [06-terraform-workflow.md](06-terraform-workflow.md) — 核心工作流程
