# Objective 3: Terraform 基礎

**考試目標：** Understand Terraform Basics
**學習資源：** [Bryan Krausen Labs](https://github.com/btkrausen/hashicorp/tree/master/terraform) | [Terraform Language Documentation](https://www.terraform.io/docs/language/index.html)

---

## 對應 Labs

| 子目標 | Lab |
|--------|-----|
| HCL Basics | HCL, Configuration Block, Resource Block, Data Block, Input/Local/Module/Output Block, Commenting |
| 3a. Provider installation and versioning | Provider Installation |
| 3b. Plugin based architecture | Terraform Plug-in Based Architecture |
| 3c. Using multiple providers | Using Multiple Terraform Providers, Terraform TLS Provider |
| 3d. How Terraform finds and fetches providers | Fetch, Version and Upgrade Terraform Providers |
| 3e. Provisioners | Terraform Provisioners |

---

## HCL 語法與配置區塊

Terraform 使用 **HCL（HashiCorp Configuration Language）** 編寫配置。

### 核心區塊類型

| 區塊 | 用途 | 語法 |
|-----|------|------|
| `terraform {}` | 全域設定（版本、Provider、Backend） | `terraform { required_version = ">= 1.0" }` |
| `provider {}` | 雲平台連線設定 | `provider "aws" { region = "us-east-1" }` |
| `resource {}` | 建立/管理實際基礎設施 | `resource "aws_s3_bucket" "main" {}` |
| `data {}` | 查詢已存在的資源（唯讀） | `data "aws_ami" "latest" {}` |
| `variable {}` | 定義輸入參數 | `variable "region" { type = string }` |
| `output {}` | 定義輸出值 | `output "id" { value = aws_s3_bucket.main.id }` |
| `locals {}` | 定義本地變數（內部計算） | `locals { env = "prod" }` |
| `module {}` | 引用可複用模塊 | `module "vpc" { source = "./modules/vpc" }` |

### HCL 基礎語法

```hcl
# 這是單行註解

// 這也是單行註解

/*
  這是多行註解
*/

# 字串插值
name = "bucket-${var.environment}"

# 條件運算
instance_type = var.environment == "prod" ? "t3.large" : "t3.micro"

# Heredoc（多行字串）
description = <<-EOT
  This is a
  multi-line string
EOT
```

---

## 3a. Provider 安裝與版本管理

### Provider 配置

```hcl
terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"    # <NAMESPACE>/<TYPE>
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

### 版本約束符號

```hcl
version = "= 5.0.0"       # 精確版本（Exact）
version = "~> 5.0"         # >= 5.0, < 6.0（Pessimistic Constraint）
version = "~> 5.0.1"       # >= 5.0.1, < 5.1.0（更嚴格的 Pessimistic）
version = ">= 5.0"         # 大於等於 5.0
version = ">= 5.0, < 6"   # 版本範圍
version = "!= 5.1.0"       # 排除特定版本
```

> **考試重點：** `~>` 是 **Pessimistic Constraint Operator**。
> - `~> 5.0` → 允許 `5.x` 但不允許 `6.0`
> - `~> 5.0.1` → 允許 `5.0.x` 但不允許 `5.1.0`

### `.terraform.lock.hcl`

```
terraform init 後產生的鎖定檔：
├── 鎖定 Provider 的精確版本和 Hash
├── 確保團隊成員使用相同版本
├── 應該提交到 Git
└── 類似 package-lock.json / Gemfile.lock
```

---

## 3b. 外掛架構（Plugin-Based Architecture）

Terraform 採用**核心 + 外掛**架構：

```
┌──────────────────────────────────┐
│         Terraform Core           │
│  (CLI, HCL 解析, 依賴圖, State) │
└──────────┬───────────────────────┘
           │ RPC (gRPC)
    ┌──────┴──────┐
    │  Providers  │ ← 外掛（動態下載）
    │  ┌────────┐ │
    │  │  AWS   │ │ → 呼叫 AWS API
    │  │ Azure  │ │ → 呼叫 Azure API
    │  │  GCP   │ │ → 呼叫 GCP API
    │  │ Random │ │ → 本地隨機值
    │  └────────┘ │
    └─────────────┘
```

### `terraform init` 做了什麼？

```
terraform init
├── 1. 讀取 required_providers 區塊
├── 2. 從 registry.terraform.io 下載 Provider 外掛
├── 3. 安裝到 .terraform/providers/ 目錄
├── 4. 產生 .terraform.lock.hcl（鎖定版本）
└── 5. 初始化 Backend（狀態儲存）
```

### 目錄結構

```
project/
├── main.tf
├── variables.tf
├── outputs.tf
├── provider.tf
├── terraform.tfvars
├── .terraform.lock.hcl          # ← 鎖定檔（提交到 Git）
├── .terraform/                   # ← 快取目錄（不提交到 Git）
│   └── providers/
│       └── registry.terraform.io/
│           └── hashicorp/
│               └── aws/
│                   └── 5.x.x/
│                       └── (binary)
└── terraform.tfstate             # ← State（不提交到 Git）
```

---

## 3c. 多 Provider 使用

### 同一 Provider 多區域（alias）

```hcl
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

### 不同類型的 Provider

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

# 使用 random Provider 產生隨機字串
resource "random_string" "suffix" {
  length  = 8
  special = false
  upper   = false
}

# 使用 tls Provider 產生金鑰
resource "tls_private_key" "ssh" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

# 搭配 AWS 使用
resource "aws_s3_bucket" "main" {
  bucket = "my-bucket-${random_string.suffix.result}"
}
```

> **學習提示：** `random`、`tls`、`local` Provider 不需要雲帳號，適合免費練習。

---

## 3d. Provider 的尋找與下載機制

```
Provider 來源優先順序：
1. .terraform/providers/（本地快取）
2. .terraform.lock.hcl（版本鎖定檔）
3. registry.terraform.io（公開 Registry）
4. 自訂 Mirror / Filesystem Mirror
```

### Provider 相關命令

```bash
# 初始化並下載 Provider
terraform init

# 更新 Provider 到符合約束的最新版本
terraform init -upgrade

# 查看目前使用的 Provider
terraform providers

# 鎖定 Provider（產生 .terraform.lock.hcl）
terraform providers lock

# Provider Mirror（離線環境使用）
terraform providers mirror /path/to/mirror
```

### Provider 命名規範

```
registry.terraform.io/<NAMESPACE>/<TYPE>

範例：
├── hashicorp/aws        → 官方 AWS Provider
├── hashicorp/azurerm    → 官方 Azure Provider
├── hashicorp/google     → 官方 GCP Provider
├── hashicorp/random     → 隨機值 Provider
└── integrations/github  → 社群 GitHub Provider
```

---

## 3e. Provisioner（最後手段）

Provisioner 用於在資源建立後執行腳本，但 **HashiCorp 明確建議盡量避免使用**。

### local-exec vs remote-exec

```hcl
resource "aws_instance" "web" {
  ami           = "ami-12345678"
  instance_type = "t3.micro"

  # local-exec：在執行 Terraform 的機器上執行
  provisioner "local-exec" {
    command = "echo ${self.public_ip} >> ip_list.txt"
  }

  # remote-exec：在遠端機器上執行（透過 SSH/WinRM）
  provisioner "remote-exec" {
    inline = [
      "sudo apt update",
      "sudo apt install -y nginx"
    ]

    connection {
      type        = "ssh"
      user        = "ubuntu"
      private_key = file("~/.ssh/id_rsa")
      host        = self.public_ip
    }
  }

  # 銷毀時執行的 Provisioner
  provisioner "local-exec" {
    when    = destroy
    command = "echo 'Instance destroyed' >> log.txt"
  }
}
```

### 為什麼 Provisioner 是 Last Resort？

| Provisioner 的問題 | 更好的替代方案 |
|-------------------|--------------|
| 不在 State 中追蹤 | `user_data` — EC2 原生支持 |
| 失敗處理困難 | `cloud-init` — 標準化配置 |
| 不具冪等性 | Ansible/Chef/Puppet — 專業配置管理 |
| 增加部署複雜度 | Packer — 預烤 AMI |

### `on_failure` 行為

```hcl
provisioner "local-exec" {
  command    = "some-command"
  on_failure = continue    # 失敗時繼續（預設是 fail）
}
```

> **考試重點：** Provisioners are a **Last Resort**。優先使用 `user_data`（EC2）或 `cloud-init`，或配合 Ansible/Chef 等配置管理工具。Provisioner 的執行結果不會記錄在 State 中。

---

## 重點整理

| 考點 | 要記住的 |
|------|---------|
| HCL 區塊 | terraform, provider, resource, data, variable, output, locals, module |
| 版本約束 `~>` | Pessimistic Constraint：`~> 5.0` = `>= 5.0, < 6.0` |
| `.terraform.lock.hcl` | 鎖定 Provider 版本，應提交到 Git |
| Plugin Architecture | Core + Provider 外掛，透過 gRPC 通訊 |
| Multiple Providers | 使用 `alias` 做多區域配置 |
| Provider 來源 | registry.terraform.io，格式 `<NAMESPACE>/<TYPE>` |
| Provisioner | Last Resort，優先用 user_data / cloud-init |
| local-exec vs remote-exec | local = 本地執行，remote = 遠端 SSH 執行 |

---

**上一篇：** [01-02-iac-and-terraform-purpose.md](01-02-iac-and-terraform-purpose.md)
**下一篇：** [04-terraform-cli.md](04-terraform-cli.md) — CLI 進階操作
