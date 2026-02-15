# Terraform 完整 Cheatsheet（來自 company-website-poc 實戰）

**Updated: 2026-02-06**
**基於真實項目的實踐總結**

---

## 📌 快速導航

| 章節 | 內容 |
|-----|------|
| [1. 基礎概念](#1-基礎概念) | Terraform 核心 |
| [2. 提供商配置](#2-提供商配置provider) | AWS Provider 設置 |
| [3. 變量系統](#3-變量系統variables) | 輸入、驗證、默認值 |
| [4. 資源管理](#4-資源管理resources) | 創建、引用、依賴 |
| [5. 模塊設計](#5-模塊化designmodules) | 代碼複用、最佳實踐 |
| [6. 狀態管理](#6-狀態管理state) | 本地與遠程狀態 |
| [7. 實戰案例](#7-實戰案例s3-cloudfront-iam) | S3/CloudFront/IAM 完整實現 |
| [8. 常用命令](#8-常用命令commands) | 工作流程 |
| [9. 常見問題](#9-常見問題faq) | 故障排除 |

---

## 1. 基礎概念

### Terraform 生命周期

```
1. Write (編寫代碼)
   ↓
2. Init (初始化：terraform init)
   - 下載 Provider
   - 初始化後端
   ↓
3. Plan (規劃：terraform plan)
   - 檢查當前狀態
   - 對比配置
   - 生成執行計劃
   ↓
4. Apply (應用：terraform apply)
   - 執行創建/更新/刪除
   - 更新狀態文件
   ↓
5. Destroy (銷毀：terraform destroy)
   - 刪除所有資源
```

### 核心概念

| 術語 | 定義 | 示例 |
|-----|------|------|
| **Provider** | 與雲服務通信的插件 | `provider "aws"` |
| **Resource** | 要管理的實際基礎設施 | `resource "aws_s3_bucket"` |
| **Variable** | 輸入參數（可配置） | `variable "aws_region"` |
| **Output** | 輸出值（供其他模塊使用） | `output "bucket_id"` |
| **Module** | 代碼複用單位 | `module "s3_module"` |
| **State** | 已部署資源的記錄 | `terraform.tfstate` |
| **Data Source** | 查詢已有資源的數據 | `data "aws_ami"` |

---

## 2. 提供商配置（Provider）

### 基礎 Provider 配置

```hcl
# provider.tf
terraform {
  required_version = ">= 1.0"  # Terraform 最低版本要求

  required_providers {
    aws = {
      source  = "hashicorp/aws"  # Provider 來源
      version = "~> 5.0"         # ⭐ 版本約束
    }
  }

  # 如果需要遠程狀態存儲（可選）
  # backend "s3" {
  #   bucket         = "my-terraform-state"
  #   key            = "terraform.tfstate"
  #   region         = "us-east-1"
  #   encrypt        = true
  #   dynamodb_table = "terraform-locks"
  # }
}

provider "aws" {
  region = var.aws_region

  # ⭐ 默認標籤：自動應用到所有 AWS 資源
  default_tags {
    tags = {
      Environment = var.environment
      Project     = var.project_name
      ManagedBy   = "Terraform"
      CreatedAt   = timestamp()  # 資源創建時間戳
    }
  }
}
```

### 版本約束符

```hcl
version = "= 5.0.0"      # 精確版本
version = "~> 5.0"       # >= 5.0, < 6.0（次版本升級）
version = ">= 5.0"       # 大於等於 5.0
version = ">= 5.0, < 6"  # 版本範圍
```

### 多區域配置

```hcl
# ⭐ 定義別名提供商
provider "aws" {
  alias  = "us-east-1"
  region = "us-east-1"
}

provider "aws" {
  alias  = "us-west-2"
  region = "us-west-2"
}

# 使用時指定提供商
resource "aws_s3_bucket" "primary" {
  provider = aws.us-east-1
  bucket   = "primary-bucket"
}

resource "aws_s3_bucket" "backup" {
  provider = aws.us-west-2
  bucket   = "backup-bucket"
}
```

---

## 3. 變量系統（Variables）

### 變量定義（variables.tf）

```hcl
# ===== 基礎變量 =====
variable "aws_region" {
  description = "AWS 區域"
  type        = string
  default     = "us-east-1"  # 可選默認值
  sensitive   = false        # 是否在輸出中隱藏敏感信息
}

# ===== 強制變量（無默認值）=====
variable "domain_name" {
  description = "網站域名"
  type        = string
  # 無 default = 創建時必須提供此值
}

# ===== 複雜類型：列表 =====
variable "allowed_cidr_blocks" {
  description = "允許的 IP CIDR"
  type        = list(string)
  default     = ["0.0.0.0/0"]

  # 驗證
  validation {
    condition     = alltrue([for cidr in var.allowed_cidr_blocks : can(cidrhost(cidr, 0))])
    error_message = "必須提供有效的 CIDR 表示法"
  }
}

# ===== 複雜類型：映射（Map）=====
variable "tags" {
  description = "資源標籤"
  type        = map(string)
  default = {
    Owner       = "TeamA"
    Environment = "prod"
  }
}

# ===== 複雜類型：對象 =====
variable "database_config" {
  description = "數據庫配置"
  type = object({
    engine   = string
    version  = string
    instance = string
  })
  default = {
    engine   = "mysql"
    version  = "5.7"
    instance = "db.t3.small"
  }
}

# ===== 帶驗證的變量 =====
variable "environment" {
  description = "環境名稱"
  type        = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "環境必須是 dev, staging 或 prod 之一"
  }
}

variable "instance_count" {
  description = "EC2 實例數量"
  type        = number

  validation {
    condition     = var.instance_count > 0 && var.instance_count <= 10
    error_message = "實例數量必須在 1-10 之間"
  }
}
```

### 變量使用方式

```hcl
# 方式 1：terraform.tfvars 文件（推薦）
# terraform.tfvars
aws_region      = "us-east-1"
environment     = "prod"
domain_name     = "example.com"

# 方式 2：命令行傳參
terraform apply -var="aws_region=us-west-2"

# 方式 3：環境變量（自動識別 TF_VAR_ 前綴）
export TF_VAR_aws_region="us-east-1"
export TF_VAR_environment="prod"

# 方式 4：.tfvars 文件（自定義名稱）
terraform apply -var-file="prod.tfvars"
```

### 變量引用

```hcl
resource "aws_s3_bucket" "main" {
  bucket = "${var.project_name}-${var.environment}"

  tags = merge(
    var.tags,
    {
      Name = var.bucket_name
    }
  )
}
```

---

## 4. 資源管理（Resources）

### 資源創建基礎

```hcl
resource "aws_s3_bucket" "primary" {
  bucket = "my-bucket-name"

  tags = {
    Name = "My Bucket"
  }
}
```

### 資源引用

```hcl
# 引用同資源的屬性
output "bucket_id" {
  value = aws_s3_bucket.primary.id
}

# 引用另一個資源的屬性
resource "aws_s3_bucket_policy" "main" {
  bucket = aws_s3_bucket.primary.id  # ⭐ 自動創建依賴
  policy = jsonencode({...})
}
```

### 條件資源創建（count）

```hcl
# ⭐ 根據條件創建資源
resource "aws_s3_bucket_versioning" "this" {
  count = var.enable_versioning ? 1 : 0

  bucket = aws_s3_bucket.main.id
  versioning_configuration {
    status = "Enabled"
  }
}

# 引用 count 資源
output "versioning_status" {
  value = var.enable_versioning ? aws_s3_bucket_versioning.this[0].id : null
}
```

### 循環資源（for_each）

```hcl
# 方式 1：循環列表
variable "bucket_names" {
  type = list(string)
  default = ["data", "logs", "archive"]
}

resource "aws_s3_bucket" "buckets" {
  for_each = toset(var.bucket_names)
  bucket   = "${each.value}-${var.environment}"
}

# 引用 for_each 資源
output "bucket_ids" {
  value = {
    for name, bucket in aws_s3_bucket.buckets : name => bucket.id
  }
}

# 方式 2：循環映射
variable "environments" {
  type = map(object({
    region = string
  }))
  default = {
    dev = {
      region = "us-east-1"
    }
    prod = {
      region = "us-west-2"
    }
  }
}

resource "aws_vpc" "envs" {
  for_each = var.environments

  cidr_block = "10.0.0.0/16"

  tags = {
    Environment = each.key
    Region      = each.value.region
  }
}
```

### 依賴管理

```hcl
# ⭐ 隱式依賴（Terraform 自動檢測）
resource "aws_s3_bucket" "main" {
  bucket = "my-bucket"
}

resource "aws_s3_bucket_policy" "main" {
  bucket = aws_s3_bucket.main.id  # 隱式依賴
  policy = jsonencode({...})
}

# ⭐ 顯式依賴（手動指定）
resource "aws_instance" "app" {
  ami           = "ami-12345678"
  instance_type = "t3.micro"

  # 等待 S3 準備完成
  depends_on = [aws_s3_bucket.main]
}

# ⭐ 檢查依賴圖
# terraform graph | dot -Tpng > graph.png
```

### 資源刪除保護

```hcl
# ⭐ 防止資源被意外刪除
resource "aws_rds_cluster" "main" {
  cluster_identifier = "my-cluster"

  # 設置為 true 時，必須手動修改才能刪除
  skip_final_snapshot       = false
  final_snapshot_identifier = "my-cluster-final-snapshot-${timestamp()}"
}

# 手動命令刪除保護資源
terraform destroy -target=aws_rds_cluster.main
```

---

## 5. 模塊化設計（Modules）

### 模塊結構

```
project/
├── modules/              # ⭐ 可複用的模塊
│   └── s3/
│       ├── main.tf       # 資源定義
│       ├── variables.tf  # 輸入變量
│       ├── outputs.tf    # 輸出值
│       └── README.md     # 文檔
│
├── s3-hosting/           # S3 方案實現
│   ├── main.tf           # 調用模塊
│   ├── variables.tf      # 項目變量
│   ├── outputs.tf        # 項目輸出
│   └── terraform.tfvars  # 變量值
│
└── provider.tf           # Provider 配置
```

### 模塊定義（modules/s3/main.tf）

```hcl
# ===== 模塊內資源定義 =====
resource "aws_s3_bucket" "this" {
  bucket = var.bucket_name
  tags   = var.tags
}

resource "aws_s3_bucket_versioning" "this" {
  count  = var.enable_versioning ? 1 : 0
  bucket = aws_s3_bucket.this.id

  versioning_configuration {
    status     = "Enabled"
    mfa_delete = var.enable_mfa_delete ? "Enabled" : "Disabled"
  }
}

resource "aws_s3_bucket_encryption_configuration" "this" {
  bucket = aws_s3_bucket.this.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = var.sse_algorithm
    }
  }
}
```

### 模塊輸出（modules/s3/outputs.tf）

```hcl
output "bucket_id" {
  description = "S3 Bucket ID"
  value       = aws_s3_bucket.this.id
  # sensitive = false  # 是否隱藏輸出
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

### 模塊變量（modules/s3/variables.tf）

```hcl
variable "bucket_name" {
  description = "S3 Bucket 名稱"
  type        = string
}

variable "enable_versioning" {
  description = "是否啟用版本控制"
  type        = bool
  default     = false
}

variable "enable_mfa_delete" {
  description = "是否啟用 MFA 刪除保護"
  type        = bool
  default     = false
}

variable "sse_algorithm" {
  description = "加密算法"
  type        = string
  default     = "AES256"

  validation {
    condition     = contains(["AES256", "aws:kms"], var.sse_algorithm)
    error_message = "只支持 AES256 或 aws:kms"
  }
}

variable "tags" {
  description = "資源標籤"
  type        = map(string)
  default     = {}
}
```

### 模塊調用（main.tf）

```hcl
# ⭐ 基礎調用
module "s3_primary" {
  source = "../../modules/s3"

  bucket_name       = "${var.project_name}-primary"
  enable_versioning = true
  tags              = local.common_tags
}

# ⭐ 調用多個實例（for_each）
variable "buckets" {
  type = map(object({
    enable_versioning = bool
    storage_class     = string
  }))
  default = {
    data = {
      enable_versioning = true
      storage_class     = "STANDARD"
    }
    logs = {
      enable_versioning = false
      storage_class     = "STANDARD_IA"
    }
  }
}

module "s3_buckets" {
  for_each = var.buckets

  source = "../../modules/s3"

  bucket_name       = "${var.project_name}-${each.key}"
  enable_versioning = each.value.enable_versioning
  tags              = merge(
    local.common_tags,
    { Name = each.key }
  )
}

# ⭐ 使用模塊輸出
output "bucket_ids" {
  value = {
    for name, bucket in module.s3_buckets : name => bucket.bucket_id
  }
}
```

### 遠程模塊

```hcl
# 從 GitHub 使用
module "vpc" {
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-vpc.git?ref=v3.0.0"

  name = "my-vpc"
  cidr = "10.0.0.0/16"
}

# 從 Terraform Registry 使用
module "security_group" {
  source = "terraform-aws-modules/security-group/aws"

  name        = "my-sg"
  description = "Security Group"
  vpc_id      = aws_vpc.main.id
}
```

---

## 6. 狀態管理（State）

### 本地狀態

```hcl
# 默認在項目根目錄
terraform.tfstate        # 當前狀態
terraform.tfstate.backup # 備份狀態
.terraform/              # Provider 和模塊緩存
```

### 遠程狀態（推薦生產環境）

```hcl
# provider.tf
terraform {
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"  # ⭐ 防止並發修改
  }
}

# 初始化遠程狀態
terraform init

# 切換到遠程狀態
terraform init -migrate-state

# 從遠程狀態拉回本地（調試用）
terraform init -reconfigure
rm terraform.tfstate*
```

### 狀態命令

```bash
# 查看當前狀態
terraform show

# 查看特定資源
terraform state show aws_s3_bucket.main

# 列出所有資源
terraform state list

# 刪除狀態中的資源（不刪除實際資源）
terraform state rm aws_s3_bucket.main

# 導入已有資源
terraform import aws_s3_bucket.main my-bucket-name

# 鎖定狀態（用於調試）
terraform state lock

# 解鎖狀態
terraform state unlock
```

### 狀態安全性

```hcl
# ✅ 最佳實踐
terraform {
  backend "s3" {
    bucket         = "terraform-state"
    key            = "terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true              # ⭐ 加密狀態文件
    dynamodb_table = "terraform-locks" # ⭐ 狀態鎖定
  }
}

# ✅ S3 存儲桶安全配置
resource "aws_s3_bucket" "terraform_state" {
  bucket = "terraform-state"
}

# 阻止公開訪問
resource "aws_s3_bucket_public_access_block" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# 啟用版本控制
resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  versioning_configuration {
    status = "Enabled"
  }
}

# 啟用加密
resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}
```

---

## 7. 實戰案例：S3 + CloudFront + IAM

### 完整 S3 配置示例

```hcl
# ===== S3 Bucket 創建 =====
resource "aws_s3_bucket" "website" {
  bucket = "${var.project_name}-website"

  tags = merge(
    var.tags,
    {
      Name = "Website Bucket"
    }
  )
}

# ===== 阻止公開訪問 =====
resource "aws_s3_bucket_public_access_block" "website" {
  bucket = aws_s3_bucket.website.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ===== 版本控制 =====
resource "aws_s3_bucket_versioning" "website" {
  bucket = aws_s3_bucket.website.id

  versioning_configuration {
    status = "Enabled"
  }
}

# ===== 服務器端加密 =====
resource "aws_s3_bucket_server_side_encryption_configuration" "website" {
  bucket = aws_s3_bucket.website.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
    bucket_key_enabled = true  # ⭐ 降低 KMS 成本
  }
}

# ===== 生命週期規則（成本優化）=====
resource "aws_s3_bucket_lifecycle_configuration" "website" {
  bucket = aws_s3_bucket.website.id

  rule {
    id     = "archive-old-versions"
    status = "Enabled"

    # 舊版本遷移到 Glacier（30天）
    noncurrent_version_transition {
      noncurrent_days = 30
      storage_class   = "GLACIER"
    }

    # 完全刪除（90天）
    noncurrent_version_expiration {
      noncurrent_days = 90
    }

    # 清理不完整上傳（7天）
    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}

# ===== 強制 HTTPS 訪問 =====
resource "aws_s3_bucket_policy" "enforce_ssl" {
  bucket = aws_s3_bucket.website.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "DenyInsecureTransport"
        Effect = "Deny"
        Principal = "*"
        Action   = "s3:*"
        Resource = [
          aws_s3_bucket.website.arn,
          "${aws_s3_bucket.website.arn}/*"
        ]
        Condition = {
          Bool = {
            "aws:SecureTransport" = "false"
          }
        }
      }
    ]
  })
}

# ===== 服務器日誌 =====
resource "aws_s3_bucket_logging" "website" {
  bucket = aws_s3_bucket.website.id

  target_bucket = aws_s3_bucket.logs.id
  target_prefix = "website-logs/"
}

# ===== CORS 配置 =====
resource "aws_s3_bucket_cors_configuration" "website" {
  bucket = aws_s3_bucket.website.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "HEAD"]
    allowed_origins = ["https://example.com"]
    expose_headers  = ["ETag", "Content-Length"]
    max_age_seconds = 3600
  }
}
```

### CloudFront 完整配置

```hcl
# ===== OAI（原始訪問身份）=====
resource "aws_cloudfront_origin_access_identity" "website" {
  comment = "OAI for ${var.project_name}"
}

# ===== CloudFront Distribution =====
resource "aws_cloudfront_distribution" "website" {
  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"
  http_version        = "http2"
  price_class         = "PriceClass_100"  # ⭐ 成本控制

  # ===== 源配置 =====
  origin {
    domain_name = aws_s3_bucket.website.bucket_regional_domain_name
    origin_id   = "S3Origin"

    # 使用 OAI 存取 S3
    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.website.cloudfront_access_identity_path
    }
  }

  # ===== 域名別名 =====
  aliases = [var.domain_name, "www.${var.domain_name}"]

  # ===== 默認行為 =====
  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3Origin"
    compress         = true  # ⭐ Gzip 壓縮

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    default_ttl            = 86400      # 1 天
    max_ttl                = 31536000   # 1 年
    min_ttl                = 0
  }

  # ===== 地理限制 =====
  restrictions {
    geo_restriction {
      restriction_type = "none"
      # restriction_type = "whitelist"
      # locations        = ["US", "CA", "GB"]
    }
  }

  # ===== SSL/TLS 證書 =====
  viewer_certificate {
    acm_certificate_arn            = aws_acm_certificate.website.arn
    ssl_support_method             = "sni-only"
    minimum_protocol_version       = "TLSv1.2_2021"
    cloudfront_default_certificate = false
  }

  # ===== 日誌配置 =====
  logging_config {
    include_cookies = false
    bucket          = aws_s3_bucket.logs.bucket_regional_domain_name
    prefix          = "cloudfront-logs/"
  }

  # ===== WAF 關聯 =====
  web_acl_id = aws_wafv2_web_acl.main.arn

  tags = var.tags
}

# ===== S3 Bucket Policy：允許 CloudFront =====
resource "aws_s3_bucket_policy" "website" {
  bucket = aws_s3_bucket.website.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowCloudFront"
        Effect = "Allow"
        Principal = {
          AWS = aws_cloudfront_origin_access_identity.website.iam_arn
        }
        Action   = "s3:GetObject"
        Resource = "${aws_s3_bucket.website.arn}/*"
      }
    ]
  })
}

# ===== CloudFront 無效化（部署後清除快取）=====
resource "aws_cloudfront_invalidation" "website" {
  distribution_id = aws_cloudfront_distribution.website.id
  paths           = ["/index.html", "/", "/*"]

  # 可選：wait_for_completion = true
}
```

### IAM 角色和策略

```hcl
# ===== S3 複製角色 =====
resource "aws_iam_role" "s3_replication" {
  name = "${var.environment}-s3-replication-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "s3.amazonaws.com"
        }
      }
    ]
  })
}

# ===== S3 複製策略 =====
resource "aws_iam_role_policy" "s3_replication" {
  name = "${var.environment}-s3-replication-policy"
  role = aws_iam_role.s3_replication.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetReplicationConfiguration",
          "s3:ListBucket"
        ]
        Resource = aws_s3_bucket.primary.arn
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObjectVersionForReplication",
          "s3:GetObjectVersionAcl"
        ]
        Resource = "${aws_s3_bucket.primary.arn}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:ReplicateObject",
          "s3:ReplicateDelete"
        ]
        Resource = "${aws_s3_bucket.backup.arn}/*"
      }
    ]
  })
}

# ===== CloudTrail 角色 =====
resource "aws_iam_role" "cloudtrail" {
  name = "${var.environment}-cloudtrail-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "cloudtrail" {
  name = "${var.environment}-cloudtrail-policy"
  role = aws_iam_role.cloudtrail.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AWSCloudTrailAclCheck"
        Effect = "Allow"
        Action = "s3:GetBucketAcl"
        Resource = aws_s3_bucket.audit.arn
      },
      {
        Sid    = "AWSCloudTrailWrite"
        Effect = "Allow"
        Action = "s3:PutObject"
        Resource = "${aws_s3_bucket.audit.arn}/*"
        Condition = {
          StringEquals = {
            "s3:x-amz-acl" = "bucket-owner-full-control"
          }
        }
      }
    ]
  })
}

# ===== CodePipeline 角色 =====
resource "aws_iam_role" "codepipeline" {
  name = "${var.environment}-codepipeline-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "codepipeline.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "codepipeline" {
  name = "${var.environment}-codepipeline-policy"
  role = aws_iam_role.codepipeline.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:GetObjectVersion"
        ]
        Resource = "${aws_s3_bucket.artifacts.arn}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "codebuild:BatchGetBuilds",
          "codebuild:BatchGetBuildBatches",
          "codebuild:StartBuild",
          "codebuild:StartBuildBatch"
        ]
        Resource = "*"
      }
    ]
  })
}
```

---

## 8. 常用命令（Commands）

### 初始化和規劃

```bash
# ===== 初始化 =====
terraform init                          # 初始化 Terraform

# ===== 驗證和格式化 =====
terraform validate                      # 驗證語法
terraform fmt                           # 自動格式化代碼
terraform fmt -recursive                # 遞歸格式化

# ===== 規劃 =====
terraform plan                          # 生成執行計劃
terraform plan -out=tfplan              # 保存執行計劃
terraform plan -destroy                 # 預覽銷毀計劃
terraform plan -var="key=value"         # 指定變量
terraform plan -var-file="prod.tfvars"  # 使用變量文件

# ===== 詳細輸出 =====
terraform plan -json | jq               # JSON 格式（便於解析）
terraform show                          # 顯示當前狀態
terraform show tfplan                   # 顯示保存的計劃
```

### 應用和銷毀

```bash
# ===== 應用 =====
terraform apply                         # 交互式應用
terraform apply tfplan                  # 應用保存的計劃
terraform apply -auto-approve           # 自動批准（CI/CD）
terraform apply -target=resource_type.name  # 應用特定資源
terraform apply -var="key=value"        # 指定變量

# ===== 銷毀 =====
terraform destroy                       # 交互式銷毀
terraform destroy -auto-approve         # 自動批准銷毀
terraform destroy -target=resource_type.name  # 銷毀特定資源
```

### 狀態管理

```bash
# ===== 狀態檢查 =====
terraform show                          # 顯示當前狀態
terraform state list                    # 列出所有資源
terraform state show aws_s3_bucket.main # 顯示特定資源
terraform state list -json              # JSON 格式輸出

# ===== 狀態操作 =====
terraform import aws_s3_bucket.main my-bucket  # 導入已有資源
terraform state rm aws_s3_bucket.main   # 移除狀態中的資源
terraform state mv src dst              # 移動狀態資源
terraform state replace-provider old new # 替換 Provider

# ===== 狀態備份 =====
terraform state pull > backup.tfstate   # 拉回狀態文件
terraform state push backup.tfstate     # 上傳狀態文件
```

### 調試和排查

```bash
# ===== 調試輸出 =====
TF_LOG=DEBUG terraform apply            # 啟用調試日誌
TF_LOG_PATH=terraform.log terraform apply  # 日誌到文件

# ===== 查看計算結果 =====
terraform console                       # 交互式控制台

# ===== 圖形化 =====
terraform graph | dot -Tpng > graph.png # 生成依賴圖

# ===== 其他 =====
terraform version                       # 顯示版本
terraform help                          # 顯示幫助
terraform providers                     # 列出使用的 Provider
```

### 工作區管理

```bash
# ===== 工作區操作 =====
terraform workspace list                # 列出工作區
terraform workspace new prod            # 創建工作區
terraform workspace select prod         # 切換工作區
terraform workspace delete prod         # 刪除工作區

# 示例：多環境管理
terraform workspace new dev
terraform workspace select dev
terraform apply -var-file="dev.tfvars"

terraform workspace select prod
terraform apply -var-file="prod.tfvars"
```

---

## 9. 常見問題（FAQ）

### 部署相關

**Q: 如何更新已部署的資源？**

```bash
# 修改代碼後
terraform plan        # 查看變更
terraform apply      # 應用變更
```

**Q: 如何回滾更改？**

```bash
# 方式 1：修改代碼並重新應用
git checkout HEAD -- main.tf
terraform apply

# 方式 2：使用狀態版本控制（遠程狀態）
terraform state pull > backup.tfstate
# 恢復后
terraform state push backup.tfstate
```

**Q: 如何只部署特定資源？**

```bash
terraform apply -target=aws_s3_bucket.main
terraform apply -target=module.s3_primary
```

**Q: 如何預覽銷毀操作？**

```bash
terraform plan -destroy
terraform destroy  # 會提示確認
```

### 狀態相關

**Q: 不小心刪除了本地 terraform.tfstate，怎麼辦？**

```bash
# 從遠程狀態恢復
terraform init -reconfigure

# 或者從 S3 備份恢復
aws s3 cp s3://bucket/terraform.tfstate.backup ./terraform.tfstate
terraform state push terraform.tfstate
```

**Q: 如何在團隊間共享狀態？**

```hcl
terraform {
  backend "s3" {
    bucket         = "team-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"  # ⭐ 防止並發編輯
  }
}
```

**Q: 如何導入已有的 AWS 資源？**

```bash
# 1. 先寫出資源定義（不需要完整配置）
resource "aws_s3_bucket" "imported" {
  bucket = "my-existing-bucket"
}

# 2. 導入狀態
terraform import aws_s3_bucket.imported my-existing-bucket

# 3. 更新配置以匹配實際狀態
terraform plan  # 應該顯示無變更
```

### 變數和模塊相關

**Q: 如何覆蓋默認變量？**

```bash
# 方式 1：命令行
terraform apply -var="aws_region=us-west-2"

# 方式 2：環境變量
export TF_VAR_aws_region="us-west-2"
terraform apply

# 方式 3：變量文件（推薦）
terraform apply -var-file="prod.tfvars"
```

**Q: 如何在模塊間傳遞複雜數據？**

```hcl
variable "database_config" {
  type = object({
    engine   = string
    version  = string
    instance = string
  })
}

module "db" {
  source = "./modules/rds"

  engine   = var.database_config.engine
  version  = var.database_config.version
  instance = var.database_config.instance
}
```

**Q: 如何使本地模塊路徑靈活？**

```hcl
locals {
  module_path = var.use_local_modules ? "../modules" : "../../modules"
}

module "s3" {
  source = "${local.module_path}/s3"
  ...
}
```

### 安全相關

**Q: 敏感信息（密碼、密鑰）應該如何處理？**

```hcl
# ❌ 不要直接寫在代碼中
resource "aws_db_instance" "main" {
  password = "MyPassword123"  # ❌ 不安全！
}

# ✅ 使用環境變量
variable "db_password" {
  type      = string
  sensitive = true  # 隱藏輸出
}

resource "aws_db_instance" "main" {
  password = var.db_password
}

# ✅ 使用 AWS Secrets Manager
data "aws_secretsmanager_secret_version" "db_password" {
  secret_id = "prod/db/password"
}

resource "aws_db_instance" "main" {
  password = jsondecode(data.aws_secretsmanager_secret_version.db_password.secret_string)["password"]
}
```

**Q: 如何防止狀態文件洩露？**

```hcl
terraform {
  backend "s3" {
    bucket         = "terraform-state"
    key            = "terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true              # ✅ 加密
    dynamodb_table = "terraform-locks" # ✅ 鎖定
  }
}

# ✅ .gitignore
echo "terraform.tfstate*" >> .gitignore
echo ".terraform/" >> .gitignore
echo "*.tfvars" >> .gitignore  # 變量文件可能包含敏感信息
```

### 性能相關

**Q: 如何加快 terraform plan？**

```bash
# 並行化執行（默認 10）
terraform plan -parallelism=20

# 跳過不必要的狀態檢查（謹慎使用）
terraform plan -refresh=false
```

**Q: 大型項目如何組織？**

```
project/
├── modules/
│   ├── networking/
│   ├── compute/
│   └── storage/
│
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── terraform.tfvars
│   │
│   └── prod/
│       ├── main.tf
│       ├── variables.tf
│       └── terraform.tfvars
│
├── global/
│   ├── provider.tf
│   └── backend.tf
│
└── README.md
```

---

## 📚 延伸閱讀

| 主題 | 鏈接 |
|-----|------|
| 官方文檔 | https://www.terraform.io/docs |
| AWS Provider | https://registry.terraform.io/providers/hashicorp/aws |
| 社區模塊 | https://registry.terraform.io/modules |
| 最佳實踐 | https://www.terraform.io/cloud-docs |
| 安全指南 | https://www.terraform.io/docs/cloud/security |

---

## 🎯 最佳實踐速記

```hcl
✅ DO:
- 使用模塊組織代碼
- 為變量添加驗證
- 使用遠程狀態存儲
- 啟用狀態鎖定
- 為敏感變量標記 sensitive = true
- 使用 for_each 代替 count（靈活性更高）
- 定義清晰的輸出
- 為資源添加標籤

❌ DON'T:
- 在代碼中存儲敏感信息
- 將 terraform.tfstate 提交到 Git
- 直接修改狀態文件
- 在生產環境使用本地狀態
- 忽視 terraform validate
- 跳過 terraform plan
- 為不同資源使用相同的名稱
- 混合使用 count 和 for_each
```

---

**最後更新: 2026-02-06**
**基於 company-website-poc 實際項目**
