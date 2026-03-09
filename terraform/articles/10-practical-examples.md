# 實戰案例：S3 + CloudFront + IAM

**來源：** company-website-poc 專案實際配置
**場景：** 使用 Terraform 部署完整的靜態網站託管架構

---

## 架構圖

```
使用者
  │
  ↓
Route 53 (DNS)
  │
  ↓
CloudFront (CDN)
  │ ← ACM Certificate (SSL/TLS)
  │ ← WAF (Web Application Firewall)
  │ ← 地理限制 / 快取策略
  ↓
S3 Bucket (靜態內容)
  │ ← OAI (Origin Access Identity) 控制存取
  │ ← 版本控制 + 加密 + 生命週期管理
  │ ← 公開存取封鎖
  ↓
S3 Logs Bucket (存取日誌)
```

---

## 專案結構

```
project/
├── modules/
│   └── s3/
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
│
├── s3-hosting/
│   ├── main.tf            # 呼叫模塊 + CloudFront + IAM
│   ├── variables.tf
│   ├── outputs.tf
│   └── terraform.tfvars
│
└── provider.tf
```

---

## S3 完整配置

### Bucket 建立 + 安全配置

```hcl
# S3 Bucket
resource "aws_s3_bucket" "website" {
  bucket = "${var.project_name}-website"
  tags   = merge(var.tags, { Name = "Website Bucket" })
}

# 阻止公開存取（必須！）
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
```

### 生命週期管理（成本優化）

```hcl
resource "aws_s3_bucket_lifecycle_configuration" "website" {
  bucket = aws_s3_bucket.website.id

  rule {
    id     = "archive-old-versions"
    status = "Enabled"

    # 舊版本 30 天後遷移到 Glacier
    noncurrent_version_transition {
      noncurrent_days = 30
      storage_class   = "GLACIER"
    }

    # 舊版本 90 天後完全刪除
    noncurrent_version_expiration {
      noncurrent_days = 90
    }

    # 清理不完整的 Multipart Upload
    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}
```

### 強制 HTTPS 存取

```hcl
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
      Condition = {
        Bool = { "aws:SecureTransport" = "false" }
      }
    }]
  })
}
```

### 日誌和 CORS

```hcl
# 存取日誌
resource "aws_s3_bucket_logging" "website" {
  bucket        = aws_s3_bucket.website.id
  target_bucket = aws_s3_bucket.logs.id
  target_prefix = "website-logs/"
}

# CORS 配置
resource "aws_s3_bucket_cors_configuration" "website" {
  bucket = aws_s3_bucket.website.id
  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "HEAD"]
    allowed_origins = ["https://${var.domain_name}"]
    expose_headers  = ["ETag", "Content-Length"]
    max_age_seconds = 3600
  }
}
```

---

## CloudFront 配置

### OAI + Distribution

```hcl
# OAI — 讓 CloudFront 安全存取私有 S3 Bucket
resource "aws_cloudfront_origin_access_identity" "website" {
  comment = "OAI for ${var.project_name}"
}

resource "aws_cloudfront_distribution" "website" {
  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"
  http_version        = "http2"
  price_class         = "PriceClass_100"    # 北美 + 歐洲（最便宜）
  aliases             = [var.domain_name, "www.${var.domain_name}"]

  # 源配置（S3）
  origin {
    domain_name = aws_s3_bucket.website.bucket_regional_domain_name
    origin_id   = "S3Origin"
    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.website.cloudfront_access_identity_path
    }
  }

  # 默認快取行為
  default_cache_behavior {
    allowed_methods        = ["GET", "HEAD", "OPTIONS"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "S3Origin"
    compress               = true                   # Gzip 壓縮
    viewer_protocol_policy = "redirect-to-https"    # 強制 HTTPS
    default_ttl            = 86400                   # 1 天
    max_ttl                = 31536000                # 1 年
    min_ttl                = 0

    forwarded_values {
      query_string = false
      cookies { forward = "none" }
    }
  }

  # SSL/TLS 證書
  viewer_certificate {
    acm_certificate_arn      = aws_acm_certificate.website.arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }

  # 地理限制
  restrictions {
    geo_restriction {
      restriction_type = "none"
      # restriction_type = "whitelist"
      # locations        = ["US", "CA", "GB", "TW"]
    }
  }

  # 日誌
  logging_config {
    include_cookies = false
    bucket          = aws_s3_bucket.logs.bucket_regional_domain_name
    prefix          = "cloudfront-logs/"
  }

  # WAF（可選）
  # web_acl_id = aws_wafv2_web_acl.main.arn

  tags = var.tags
}
```

### S3 Policy：允許 CloudFront 存取

```hcl
resource "aws_s3_bucket_policy" "allow_cloudfront" {
  bucket = aws_s3_bucket.website.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid       = "AllowCloudFront"
      Effect    = "Allow"
      Principal = {
        AWS = aws_cloudfront_origin_access_identity.website.iam_arn
      }
      Action   = "s3:GetObject"
      Resource = "${aws_s3_bucket.website.arn}/*"
    }]
  })
}
```

### Price Class 對照表

| Price Class | 涵蓋區域 | 費用 |
|------------|---------|------|
| `PriceClass_100` | 北美 + 歐洲 | 最便宜 |
| `PriceClass_200` | + 亞太、中東、非洲 | 中等 |
| `PriceClass_All` | 全部（含南美） | 最貴 |

---

## IAM 角色配置模式

### 標準模式：Trust Policy + Permission Policy

```hcl
# Trust Policy — 誰可以 Assume 這個 Role
resource "aws_iam_role" "service_role" {
  name = "${var.environment}-service-role"

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
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:GetObject", "s3:PutObject"]
      Resource = "${aws_s3_bucket.main.arn}/*"
    }]
  })
}
```

### S3 跨區域複製 IAM

```hcl
resource "aws_iam_role" "s3_replication" {
  name = "${var.environment}-s3-replication-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "s3.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy" "s3_replication" {
  name = "${var.environment}-s3-replication-policy"
  role = aws_iam_role.s3_replication.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:GetReplicationConfiguration", "s3:ListBucket"]
        Resource = aws_s3_bucket.primary.arn
      },
      {
        Effect   = "Allow"
        Action   = ["s3:GetObjectVersionForReplication", "s3:GetObjectVersionAcl"]
        Resource = "${aws_s3_bucket.primary.arn}/*"
      },
      {
        Effect   = "Allow"
        Action   = ["s3:ReplicateObject", "s3:ReplicateDelete"]
        Resource = "${aws_s3_bucket.backup.arn}/*"
      }
    ]
  })
}
```

### CodePipeline IAM

```hcl
resource "aws_iam_role" "codepipeline" {
  name = "${var.environment}-codepipeline-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "codepipeline.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy" "codepipeline" {
  name = "${var.environment}-codepipeline-policy"
  role = aws_iam_role.codepipeline.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:PutObject", "s3:GetObjectVersion"]
        Resource = "${aws_s3_bucket.artifacts.arn}/*"
      },
      {
        Effect   = "Allow"
        Action   = [
          "codebuild:BatchGetBuilds",
          "codebuild:StartBuild"
        ]
        Resource = "*"
      }
    ]
  })
}
```

---

## Terraform 學到的設計模式

### 1. 資源分離模式

```hcl
# 每個 S3 配置都是獨立的 resource（不是放在同一個 block 內）
resource "aws_s3_bucket" "main" { ... }
resource "aws_s3_bucket_versioning" "main" { ... }
resource "aws_s3_bucket_server_side_encryption_configuration" "main" { ... }
resource "aws_s3_bucket_lifecycle_configuration" "main" { ... }
resource "aws_s3_bucket_policy" "main" { ... }
# 這是 AWS Provider v4+ 的標準做法
```

### 2. 標籤策略

```hcl
locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# 使用 merge 為特定資源添加額外標籤
resource "aws_s3_bucket" "main" {
  tags = merge(local.common_tags, { Name = "main-bucket" })
}
```

### 3. 條件資源

```hcl
# 根據環境決定是否建立資源
resource "aws_cloudfront_distribution" "website" {
  count = var.enable_cdn ? 1 : 0
  ...
}
```

---

**上一篇：** [09-terraform-cloud.md](09-terraform-cloud.md)
**下一篇：** [11-exam-tips.md](11-exam-tips.md) — 考試要訣
