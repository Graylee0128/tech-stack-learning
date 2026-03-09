# Objective 7: Terraform 狀態管理

**考試目標：** Implement and Maintain State
**學習資源：** [Bryan Krausen Labs](https://github.com/btkrausen/hashicorp/tree/master/terraform) | [State Documentation](https://www.terraform.io/docs/language/state/index.html)

---

## 對應 Labs

| 子目標 | Lab |
|--------|-----|
| 7a. Default local backend | Terraform Local State |
| 7b. State locking | Terraform State Locking |
| 7c. Backend authentication | Terraform State: Backend Authentication |
| 7d. Remote state storage | Standard Backend Storage, Remote State Enhanced Backend, State Migration |
| 7e. Terraform refresh | Terraform Refresh |
| 7f. Backend block and partial configurations | Terraform Backend Configurations |
| 7g. Secret management in state | Terraform State Secrets |

---

## 7a. 預設 Local Backend

```
.
├── terraform.tfstate          # 當前狀態（JSON 格式）
├── terraform.tfstate.backup   # 上一次的狀態備份（自動產生）
└── .terraform/                # Provider 和模塊快取
    ├── providers/
    └── modules/
```

### Local Backend 的特性

| 優點 | 缺點 |
|------|------|
| 零配置，開箱即用 | 不適合團隊協作 |
| 快速存取 | 無法遠端共享 |
| 自動備份 | 可能被意外刪除 |

> **考試重點：** 預設的 Local Backend 將狀態存在當前目錄的 `terraform.tfstate` 檔案中。自動產生 `.backup` 檔。

---

## 7b. State Locking（狀態鎖定）

防止多人同時修改 State 造成衝突。

```hcl
# S3 + DynamoDB 實現狀態鎖定
terraform {
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"    # ← 鎖定用的 DynamoDB 表
  }
}
```

### 鎖定機制

```
鎖定運作方式：
1. terraform plan/apply 開始 → 取得鎖（DynamoDB 寫入 Lock Record）
2. 其他人嘗試操作 → 鎖衝突，顯示「State locked」錯誤
3. 操作完成 → 釋放鎖（刪除 Lock Record）
4. 異常退出 → 手動解鎖

# 強制解鎖（異常退出時）
terraform force-unlock <LOCK_ID>
```

### 支持鎖定的 Backend

| Backend | 支持鎖定 | 鎖定機制 |
|---------|---------|---------|
| Local | Yes | 檔案鎖 |
| S3 | Yes | DynamoDB |
| Consul | Yes | Consul Lock |
| Terraform Cloud | Yes | 內建 |
| HTTP | 取決於實作 | 自訂 |

> **考試重點：** 不是所有 Backend 都支持鎖定。S3 需要搭配 DynamoDB 才能鎖定。使用 `terraform force-unlock` 解除異常鎖定。

---

## 7c. Backend 認證方式

```bash
# 方式 1：環境變數（推薦，最安全）
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."

# 方式 2：共用認證設定
provider "aws" {
  shared_credentials_files = ["~/.aws/credentials"]
  profile                  = "production"
}

# 方式 3：IAM Role（EC2 / ECS / Lambda）
# 無需額外設定，自動使用 Instance Profile / Task Role

# 方式 4：Assume Role
provider "aws" {
  assume_role {
    role_arn = "arn:aws:iam::123456789012:role/terraform-role"
  }
}
```

### 認證優先順序（AWS Provider）

```
1. Provider 區塊中的硬編碼（不建議）
2. 環境變數（AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY）
3. 共用認證檔（~/.aws/credentials）
4. EC2 Instance Profile / ECS Task Role
```

---

## 7d. 遠端狀態儲存

### S3 Backend（最常用）

```hcl
terraform {
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true                    # 加密
    dynamodb_table = "terraform-locks"       # 鎖定
  }
}
```

### Terraform Cloud Backend

```hcl
terraform {
  cloud {
    organization = "my-org"
    workspaces {
      name = "my-workspace"
    }
  }
}
```

### Consul Backend

```hcl
terraform {
  backend "consul" {
    address = "consul.example.com:8500"
    scheme  = "https"
    path    = "terraform/state"
  }
}
```

### 狀態遷移

```bash
# Local → S3（添加 backend 配置後）
terraform init -migrate-state

# S3 → Local（移除 backend 配置後）
terraform init -migrate-state

# 重新配置 Backend（不遷移）
terraform init -reconfigure
```

### Remote State Data Source（跨專案引用 State）

```hcl
# 讀取其他專案的 State 輸出
data "terraform_remote_state" "vpc" {
  backend = "s3"
  config = {
    bucket = "terraform-state"
    key    = "vpc/terraform.tfstate"
    region = "us-east-1"
  }
}

# 使用
resource "aws_instance" "web" {
  subnet_id = data.terraform_remote_state.vpc.outputs.subnet_id
}
```

---

## 7e. `terraform refresh`

```bash
# 已棄用
terraform refresh

# 推薦替代
terraform apply -refresh-only
```

### refresh 的行為

```
terraform refresh / apply -refresh-only：
├── 1. 查詢所有受管資源的實際狀態（呼叫雲 API）
├── 2. 更新 State 檔案以反映實際狀態
├── 3. 不做任何資源變更
└── 用途：偵測手動修改（Configuration Drift）
```

> **考試重點：** `terraform refresh` 已棄用，改用 `terraform apply -refresh-only`。它只更新 State，不修改任何資源。

---

## 7f. Backend 配置與 Partial Configuration

### 完整配置

```hcl
terraform {
  backend "s3" {
    bucket         = "my-state"
    key            = "terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}
```

### Partial Configuration（部分配置）

敏感資訊不寫在 `.tf` 中，在 `init` 時傳入。

```hcl
# backend.tf — 只寫非敏感部分
terraform {
  backend "s3" {
    bucket = "my-state"
    key    = "terraform.tfstate"
    region = "us-east-1"
  }
}
```

```bash
# 方式 1：命令列傳入
terraform init \
  -backend-config="access_key=AKIA..." \
  -backend-config="secret_key=..."

# 方式 2：使用 .hcl 檔案
terraform init -backend-config=backend.hcl
```

```hcl
# backend.hcl（不提交到 Git）
access_key     = "AKIA..."
secret_key     = "..."
dynamodb_table = "terraform-locks"
encrypt        = true
```

> **考試重點：** Partial Configuration 允許在 `terraform init` 時傳入 Backend 設定，避免敏感資訊寫在程式碼中。

---

## 7g. State 中的敏感資料

### 標記敏感變數

```hcl
variable "db_password" {
  type      = string
  sensitive = true    # plan/apply 輸出中不顯示
}

output "password" {
  value     = var.db_password
  sensitive = true    # output 中不顯示
}
```

### sensitive 的限制

```
sensitive = true 的行為：
├── ✅ CLI 輸出（plan/apply）中隱藏值
├── ✅ terraform output 中隱藏值
├── ❌ State 檔案中仍然是明文！
└── ❌ 日誌中可能仍然可見（TF_LOG=TRACE）
```

> **考試重點：** `sensitive = true` 只影響 CLI 輸出的顯示。State 檔案中**仍然以明文儲存**，所以必須：
> 1. 加密 State 檔案（`encrypt = true`）
> 2. 限制 State 存取權限
> 3. 不要將 State 提交到 Git

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

# 3. 啟用版本控制（可回滾 State）
resource "aws_s3_bucket_versioning" "state" {
  bucket = aws_s3_bucket.state.id
  versioning_configuration { status = "Enabled" }
}
```

### `.gitignore` 必備設定

```gitignore
# Terraform State（絕對不能提交到 Git）
terraform.tfstate
terraform.tfstate.backup
terraform.tfstate.d/

# Terraform 快取
.terraform/

# 可能包含敏感資訊的變數檔
*.tfvars
!example.tfvars
```

---

## 重點整理

| 考點 | 要記住的 |
|------|---------|
| Local Backend | 預設，`terraform.tfstate` + `.backup` |
| State Locking | S3 + DynamoDB，`force-unlock` 解除 |
| 認證 | 環境變數 > 共用認證檔 > Instance Profile |
| 遠端 Backend | S3, Terraform Cloud, Consul |
| State 遷移 | `terraform init -migrate-state` |
| refresh | 已棄用，用 `apply -refresh-only` |
| Partial Config | `init -backend-config` 傳入敏感資訊 |
| sensitive | 只隱藏 CLI 輸出，State 仍是明文 |
| 安全 | encrypt + 阻止公開存取 + 版本控制 + .gitignore |

---

**上一篇：** [06-terraform-workflow.md](06-terraform-workflow.md)
**下一篇：** [08-terraform-configuration.md](08-terraform-configuration.md) — 讀取、生成與修改配置
