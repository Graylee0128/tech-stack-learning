# Objective 8: 讀取、生成與修改配置

**考試目標：** Read, Generate, and Modify Configuration
**學習資源：** [Bryan Krausen Labs](https://github.com/btkrausen/hashicorp/tree/master/terraform) | [Configuration Language](https://www.terraform.io/docs/language/index.html)

---

## 對應 Labs

| 子目標 | Lab |
|--------|-----|
| 8a. Variables and outputs | Input Variables, Local Values, Outputs, Variable Validation and Suppression |
| 8b. Secure secret injection | Terraform Secure Variables |
| 8c. Collection and structural types | Terraform Collection Types |
| 8d. Resource and data configuration | Terraform Resources, Terraform Data Blocks and Configuration |
| 8e. Resource addressing | Terraform Interpolation Syntax, Terraform Console |
| 8f. Built-in functions | Terraform Console, Terraform Functions, Terraform Conditional Operator |
| 8g. Dynamic block | Terraform Dynamic Blocks |
| 8h. Dependency management | Terraform Graph, Terraform Lifecycles |

---

## 8a. 變數與輸出

### 變數類型

```hcl
# === 基本類型（Primitive） ===
variable "name"    { type = string }
variable "count"   { type = number }
variable "enable"  { type = bool }

# === 集合類型（Collection） ===
variable "cidrs"   { type = list(string) }     # 有序，可重複
variable "tags"    { type = map(string) }      # 鍵值對
variable "ids"     { type = set(string) }      # 無序，不可重複

# === 結構類型（Structural） ===
variable "config" {
  type = object({          # 每個屬性可有不同型別
    engine   = string
    version  = string
    instance = string
  })
}

variable "rules" {
  type = tuple([string, number, bool])    # 固定長度，固定型別
}

# === any 類型 ===
variable "flexible" {
  type = any    # 接受任何類型（Terraform 自動推斷）
}
```

### 變數賦值優先順序（由低到高）

```
1. default 值（最低優先）
2. terraform.tfvars / terraform.tfvars.json（自動載入）
3. *.auto.tfvars / *.auto.tfvars.json（自動載入，字母順序）
4. -var-file="file.tfvars"（命令列指定）
5. -var="key=value"（命令列指定）
6. TF_VAR_name 環境變數（最高優先）
```

> **考試重點（高頻考題）：** 優先順序。環境變數和 `-var` 優先級最高。`terraform.tfvars` 會自動載入，自訂名稱的 `.tfvars` 需要用 `-var-file` 指定。

### 變數使用方式

```bash
# 方式 1：terraform.tfvars（自動載入，推薦）
# terraform.tfvars
aws_region  = "us-east-1"
environment = "prod"

# 方式 2：命令列
terraform apply -var="aws_region=us-west-2"

# 方式 3：環境變數（前綴 TF_VAR_）
export TF_VAR_aws_region="us-east-1"

# 方式 4：自訂 .tfvars 檔案
terraform apply -var-file="prod.tfvars"
```

### 變數驗證

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

variable "cidr_block" {
  type = string
  validation {
    condition     = can(cidrhost(var.cidr_block, 0))
    error_message = "必須是合法的 CIDR 表示法。"
  }
}
```

### Local Values

```hcl
locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }

  bucket_name = "${var.project_name}-${var.environment}"

  is_production = var.environment == "prod"
}

resource "aws_s3_bucket" "main" {
  bucket = local.bucket_name
  tags   = local.common_tags
}
```

> **考試重點：** `variable` = 外部輸入（可被覆蓋），`locals` = 內部計算值（不能被外部覆蓋）。

### Output Values

```hcl
output "bucket_id" {
  description = "The S3 bucket ID"
  value       = aws_s3_bucket.main.id
}

output "bucket_arn" {
  description = "The S3 bucket ARN"
  value       = aws_s3_bucket.main.arn
  sensitive   = true    # 隱藏輸出
}

# 查看輸出
# terraform output
# terraform output bucket_id
# terraform output -json
```

---

## 8b. 安全的密鑰注入

```hcl
# ❌ 不安全 — 硬編碼在程式碼中
resource "aws_db_instance" "main" {
  password = "MyPassword123"    # 會被提交到 Git！
}

# ✅ 使用 sensitive 變數
variable "db_password" {
  type      = string
  sensitive = true
}
resource "aws_db_instance" "main" {
  password = var.db_password
}
# 使用時：export TF_VAR_db_password="..." && terraform apply

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
resource "aws_db_instance" "main" {
  password = data.vault_generic_secret.db.data["password"]
}
```

---

## 8c. 集合與結構類型

### Collection Types（集合類型）

```hcl
# list — 有序，可重複，數值索引
variable "subnets" {
  type    = list(string)
  default = ["10.0.1.0/24", "10.0.2.0/24"]
}
# 存取：var.subnets[0]

# map — 鍵值對
variable "ami_map" {
  type = map(string)
  default = {
    us-east-1 = "ami-12345"
    us-west-2 = "ami-67890"
  }
}
# 存取：var.ami_map["us-east-1"]

# set — 無序，不可重複
variable "unique_ids" {
  type = set(string)
}
# 用途：for_each 需要 set 或 map
```

### Structural Types（結構類型）

```hcl
# object — 每個屬性可有不同型別
variable "server" {
  type = object({
    name     = string
    size     = number
    enabled  = bool
    tags     = map(string)
  })
  default = {
    name    = "web"
    size    = 2
    enabled = true
    tags    = { Env = "prod" }
  }
}

# tuple — 固定長度，每個位置有固定型別
variable "rule" {
  type    = tuple([string, number, bool])
  default = ["allow", 80, true]
}
```

### 型別轉換

```hcl
# list → set（for_each 需要）
for_each = toset(var.bucket_names)

# map → list
keys(var.ami_map)       # ["us-east-1", "us-west-2"]
values(var.ami_map)     # ["ami-12345", "ami-67890"]

# any → specific
tostring(42)     # "42"
tonumber("42")   # 42
tobool("true")   # true
```

---

## 8d. Resource vs Data Source

```hcl
# Resource — 建立並管理新資源（CRUD）
resource "aws_s3_bucket" "new_bucket" {
  bucket = "my-new-bucket"
}
# Terraform 負責 Create, Read, Update, Delete

# Data Source — 查詢已存在的資源（Read Only）
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]    # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-*-amd64-server-*"]
  }
}

# 使用 Data Source 的結果
resource "aws_instance" "web" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.micro"
}
```

| | Resource | Data Source |
|--|---------|------------|
| **語法** | `resource "type" "name"` | `data "type" "name"` |
| **行為** | 建立/管理資源 | 查詢已有資源（唯讀） |
| **State** | 記錄在 State 中 | 每次 plan/apply 重新查詢 |
| **引用** | `aws_s3_bucket.main.id` | `data.aws_ami.ubuntu.id` |

---

## 8e. 資源定址與引用

```hcl
# Resource 屬性
aws_s3_bucket.main.id
aws_s3_bucket.main.arn

# Data Source
data.aws_ami.ubuntu.id

# Module Output
module.vpc.vpc_id

# Variable
var.region

# Local
local.common_tags

# Terraform 內建
terraform.workspace       # 當前工作區名稱
path.module               # 當前模塊路徑
path.root                 # Root 模塊路徑
path.cwd                  # 當前工作目錄

# count 索引
aws_instance.web[0].id
aws_instance.web[*].id    # Splat expression（所有實例的 ID）

# for_each key
aws_s3_bucket.buckets["data"].id
```

### Splat Expression

```hcl
# count 情境
resource "aws_instance" "web" {
  count = 3
  ami   = "ami-12345"
}

# 取得所有 ID
output "all_ids" {
  value = aws_instance.web[*].id    # ["i-111", "i-222", "i-333"]
}
```

---

## 8f. 內建函數

### 字串函數

```hcl
upper("hello")                    # "HELLO"
lower("HELLO")                    # "hello"
title("hello world")              # "Hello World"
format("Hello, %s!", "World")     # "Hello, World!"
join(", ", ["a", "b", "c"])       # "a, b, c"
split(",", "a,b,c")              # ["a", "b", "c"]
replace("hello", "l", "L")       # "heLLo"
trimspace("  hello  ")           # "hello"
substr("hello", 0, 3)            # "hel"
regex("[a-z]+", "abc123")        # "abc"
```

### 集合函數

```hcl
length(["a", "b", "c"])          # 3
contains(["a", "b"], "a")        # true
merge({a=1}, {b=2})              # {a=1, b=2}
flatten([[1,2], [3,4]])          # [1,2,3,4]
keys({a=1, b=2})                 # ["a", "b"]
values({a=1, b=2})               # [1, 2]
lookup({a=1}, "a", 0)            # 1（找到 key "a"）
lookup({a=1}, "b", 0)            # 0（沒找到，回傳預設值）
element(["a","b","c"], 1)        # "b"
index(["a","b","c"], "b")        # 1
distinct(["a","b","a"])          # ["a","b"]
sort(["c","a","b"])              # ["a","b","c"]
toset(["a", "b", "a"])           # toset(["a", "b"])
zipmap(["a","b"], [1,2])         # {a=1, b=2}
```

### 檔案系統函數

```hcl
file("${path.module}/script.sh")              # 讀取檔案內容
fileexists("${path.module}/script.sh")        # 檢查檔案是否存在
filebase64("${path.module}/cert.pem")         # Base64 編碼讀取
templatefile("template.tftpl", {name="World"})  # 模板渲染
```

### 編碼函數

```hcl
jsonencode({key = "value"})      # '{"key":"value"}'
jsondecode('{"key":"value"}')    # {key = "value"}
yamlencode({key = "value"})      # YAML 格式
yamldecode("key: value")         # HCL 格式
base64encode("hello")            # "aGVsbG8="
base64decode("aGVsbG8=")         # "hello"
urlencode("hello world")         # "hello+world"
```

### 網路函數

```hcl
cidrhost("10.0.0.0/24", 5)      # "10.0.0.5"
cidrnetmask("10.0.0.0/24")      # "255.255.255.0"
cidrsubnet("10.0.0.0/16", 8, 1) # "10.0.1.0/24"
cidrsubnet("10.0.0.0/16", 8, 2) # "10.0.2.0/24"
```

### 條件與邏輯

```hcl
# 條件運算子
instance_type = var.env == "prod" ? "t3.large" : "t3.micro"

# coalesce — 回傳第一個非空值
coalesce("", "default")         # "default"
coalesce("first", "second")     # "first"

# try — 安全存取（不存在時回傳預設值）
try(var.optional.field, "fallback")

# can — 測試運算式是否成功
can(cidrhost(var.cidr, 0))      # true/false
```

### for Expression

```hcl
# list → list
upper_names = [for name in var.names : upper(name)]

# list → filtered list
prod_servers = [for s in var.servers : s if s.env == "prod"]

# list → map
name_map = { for s in var.servers : s.name => s.id }

# map → map
upper_tags = { for k, v in var.tags : k => upper(v) }
```

> **考試重點：** `lookup()`、`merge()`、`file()`、`templatefile()`、`cidrsubnet()` 是高頻考題。使用 `terraform console` 互動式測試函數。

---

## 8g. Dynamic Block

用於動態產生重複的嵌套區塊。

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
    { port = 22,  protocol = "tcp", cidr_blocks = ["10.0.0.0/8"] },
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

### 自訂迭代器名稱

```hcl
dynamic "ingress" {
  for_each = var.ingress_rules
  iterator = rule    # ← 自訂名稱（預設是區塊名稱 "ingress"）
  content {
    from_port   = rule.value.port
    to_port     = rule.value.port
    protocol    = rule.value.protocol
    cidr_blocks = rule.value.cidr_blocks
  }
}
```

### 巢狀 Dynamic Block

```hcl
dynamic "setting" {
  for_each = var.settings
  content {
    name  = setting.value.name
    value = setting.value.value

    dynamic "nested" {
      for_each = setting.value.nested_items
      content {
        key = nested.value
      }
    }
  }
}
```

> **考試重點：** Dynamic Block 中使用 `<block_label>.value` 存取迭代項目。`iterator` 參數可自訂迭代變數名稱。Dynamic Block 只能用於**嵌套區塊**（如 `ingress`），不能用於頂層資源。

---

## 8h. 內建依賴管理

### 隱式依賴 vs 顯式依賴

```hcl
# 隱式依賴（Implicit）— Terraform 自動偵測
resource "aws_s3_bucket" "main" {
  bucket = "my-bucket"
}

resource "aws_s3_bucket_policy" "main" {
  bucket = aws_s3_bucket.main.id    # ← 引用 = 自動建立依賴
  policy = jsonencode({...})
}

# 顯式依賴（Explicit）— 手動指定
resource "aws_instance" "app" {
  ami           = "ami-12345678"
  instance_type = "t3.micro"
  depends_on    = [aws_s3_bucket.main]    # ← 手動指定
}
```

### 依賴圖

```bash
# 生成依賴圖
terraform graph | dot -Tpng > graph.png
terraform graph -type=plan | dot -Tpng > plan-graph.png
```

### Lifecycle 規則

```hcl
resource "aws_instance" "web" {
  ami           = "ami-12345678"
  instance_type = "t3.micro"

  lifecycle {
    # 先建新的，再刪舊的（零停機部署）
    create_before_destroy = true

    # 阻止 terraform destroy 刪除此資源
    prevent_destroy = true

    # 忽略特定屬性的變更（外部手動修改不觸發更新）
    ignore_changes = [tags, ami]
    # ignore_changes = all    # 忽略所有變更

    # 當指定資源變更時，觸發重建
    replace_triggered_by = [
      aws_s3_bucket.main.id
    ]
  }
}
```

| Lifecycle 規則 | 行為 | 使用場景 |
|---------------|------|---------|
| `create_before_destroy` | 先建後刪 | 零停機部署、DNS 切換 |
| `prevent_destroy` | 阻止刪除 | 保護重要資源（RDS、S3） |
| `ignore_changes` | 忽略變更 | 外部系統管理的屬性（如 ASG 的 desired_capacity） |
| `replace_triggered_by` | 連動重建 | 當相關資源變更時強制重建 |

> **考試重點：**
> - `create_before_destroy` 解決零停機部署
> - `prevent_destroy` 只阻止 `terraform destroy`，不阻止手動刪除
> - `ignore_changes` 忽略外部手動修改，防止 Terraform 回滾手動變更

---

## 重點整理

| 考點 | 要記住的 |
|------|---------|
| 變數優先順序 | env var > -var > -var-file > auto.tfvars > terraform.tfvars > default |
| variable vs locals | variable = 外部輸入，locals = 內部計算 |
| Collection Types | list（有序）, map（鍵值）, set（無序不重複） |
| Structural Types | object（命名屬性）, tuple（位置屬性） |
| Resource vs Data | resource = CRUD, data = Read Only |
| 高頻函數 | lookup, merge, file, templatefile, cidrsubnet |
| Dynamic Block | `<label>.value` 存取，`iterator` 自訂名稱 |
| 隱式 vs 顯式依賴 | 引用 = 隱式，depends_on = 顯式 |
| Lifecycle | create_before_destroy, prevent_destroy, ignore_changes |

---

**上一篇：** [07-terraform-state.md](07-terraform-state.md)
**下一篇：** [09-terraform-cloud.md](09-terraform-cloud.md) — Terraform Cloud / Enterprise
