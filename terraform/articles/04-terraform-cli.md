# Objective 4: Terraform CLI 進階操作

**考試目標：** Use the Terraform CLI (outside of core workflow)
**學習資源：** [Bryan Krausen Labs](https://github.com/btkrausen/hashicorp/tree/master/terraform) | [CLI Commands](https://www.terraform.io/docs/cli/commands/index.html)

---

## 對應 Labs

| 子目標 | Lab |
|--------|-----|
| 4a. `terraform fmt` | Auto Formatting Terraform Code |
| 4b. `terraform taint` / `-replace` | Terraform Taint and Replace |
| 4c. `terraform import` | Terraform Import |
| 4d. `terraform workspace` | Terraform Workspaces (OSS) |
| 4e. `terraform state` | Terraform State CLI |
| 4f. Verbose logging | Debugging Terraform |

---

## 4a. `terraform fmt` — 程式碼格式化

自動將 `.tf` 檔案格式化為 HashiCorp 標準風格。

```bash
terraform fmt                    # 格式化當前目錄的 .tf 檔
terraform fmt -recursive         # 遞歸格式化所有子目錄
terraform fmt -check             # 只檢查，不修改（CI/CD 用，不符合時 exit code = 3）
terraform fmt -diff              # 顯示差異
terraform fmt -write=false       # 只顯示結果，不寫入檔案
```

### 格式化規則

```hcl
# fmt 之前（亂排）
resource "aws_instance""web"{
ami="ami-12345"
instance_type    =     "t3.micro"
tags={Name="web"}
}

# fmt 之後（標準化）
resource "aws_instance" "web" {
  ami           = "ami-12345"
  instance_type = "t3.micro"
  tags          = { Name = "web" }
}
```

> **最佳實踐：** 加入 CI/CD pre-commit hook：`terraform fmt -check -recursive`

---

## 4b. `terraform taint` / `terraform apply -replace`

強制在下次 apply 時**重建**某個資源（destroy + create）。

```bash
# 舊方式（Terraform 0.15.2 前）— 已棄用
terraform taint aws_instance.web
terraform untaint aws_instance.web    # 取消標記

# 新方式（推薦）
terraform apply -replace="aws_instance.web"
```

### 使用場景

| 場景 | 說明 |
|------|------|
| Provisioner 失敗 | 資源已建立但配置未完成 |
| 手動修改 | 有人手動改了資源，需要回到預期狀態 |
| 強制輪換 | 需要新的 IP / Instance ID |
| 安全更新 | 需要重建使用新 AMI |

> **考試重點：** `taint` 在 Terraform 0.15.2+ 已被 `-replace` 取代，但考試可能兩個都考。`taint` 修改 State 中的標記，`-replace` 直接在 apply 時處理。

---

## 4c. `terraform import` — 導入已有資源

將已存在的雲端資源納入 Terraform 管理。

### 操作步驟

```bash
# Step 1: 先在 .tf 配置中定義資源框架
resource "aws_s3_bucket" "imported" {
  bucket = "my-existing-bucket"
}

# Step 2: 執行導入（將實際資源映射到 State）
terraform import aws_s3_bucket.imported my-existing-bucket

# Step 3: 檢視導入的資源屬性
terraform state show aws_s3_bucket.imported

# Step 4: 根據 state show 的結果，補齊 .tf 配置
# ...

# Step 5: 驗證配置匹配
terraform plan    # 應顯示「No changes」
```

### 導入的限制

```
terraform import 的行為：
├── ✅ 更新 State（記錄資源資訊）
├── ❌ 不會自動產生 .tf 配置代碼
├── ❌ 不會偵測資源之間的依賴
└── ❌ 一次只能導入一個資源
```

### Import Block（Terraform 1.5+）

```hcl
# 新語法：在配置中聲明導入
import {
  to = aws_s3_bucket.imported
  id = "my-existing-bucket"
}

resource "aws_s3_bucket" "imported" {
  bucket = "my-existing-bucket"
}

# 搭配 terraform plan -generate-config-out=generated.tf
# 可以自動產生配置！
```

> **考試重點：** `import` 只更新 State，不會自動產生配置代碼。你需要手動補齊 `.tf` 配置。

---

## 4d. `terraform workspace` — 工作區管理

Workspace 允許在**相同配置代碼**下維護**獨立的 State**。

```bash
terraform workspace list           # 列出所有工作區
terraform workspace new dev        # 建立新工作區
terraform workspace select dev     # 切換工作區
terraform workspace show           # 顯示當前工作區
terraform workspace delete dev     # 刪除工作區（需先切到其他工作區）
```

### 在配置中使用工作區

```hcl
# 使用 terraform.workspace 引用當前工作區名稱
resource "aws_s3_bucket" "main" {
  bucket = "myapp-${terraform.workspace}"    # myapp-dev / myapp-prod
}

resource "aws_instance" "web" {
  instance_type = terraform.workspace == "prod" ? "t3.large" : "t3.micro"
}
```

### State 儲存位置

```
使用 Workspace 時的 State 結構：

Local Backend:
├── terraform.tfstate.d/
│   ├── dev/
│   │   └── terraform.tfstate
│   └── prod/
│       └── terraform.tfstate
└── terraform.tfstate            ← default workspace

S3 Backend:
├── env:/dev/terraform.tfstate
├── env:/prod/terraform.tfstate
└── terraform.tfstate            ← default workspace
```

> **考試重點：**
> - 預設工作區是 `default`，**無法刪除**
> - OSS Workspaces 共用相同配置但維護獨立 State
> - 適合簡單的多環境管理
> - 不同於 Terraform Cloud Workspaces（功能更豐富）

---

## 4e. `terraform state` — 狀態操作

直接操作 Terraform State 的進階命令。

```bash
# === 檢視 ===
terraform state list                          # 列出所有受管資源
terraform state show aws_s3_bucket.main       # 顯示特定資源的完整屬性

# === 修改 ===
terraform state mv aws_s3_bucket.old aws_s3_bucket.new  # 重新命名（移動）
terraform state rm aws_s3_bucket.main         # 從 State 移除（不刪除實際資源）

# === 匯入匯出 ===
terraform state pull > backup.tfstate         # 匯出遠端 State 到本地
terraform state push backup.tfstate           # 上傳 State 到遠端

# === 其他 ===
terraform state replace-provider hashicorp/aws registry.acme.corp/acme/aws
```

### 常用場景

| 命令 | 使用場景 |
|------|---------|
| `state mv` | 重構代碼時重新命名資源（避免 destroy + create） |
| `state rm` | 不再由 Terraform 管理某資源（但不刪除它） |
| `state pull/push` | 備份/恢復 State |
| `state list` | 查看 Terraform 管理了哪些資源 |
| `state show` | 查看資源的詳細屬性（import 後用來補齊配置） |

> **注意：** `state rm` 只從 State 中移除記錄，實際的雲端資源**不會被刪除**。之後 Terraform 就「看不到」這個資源了。

---

## 4f. Debugging — 除錯日誌

```bash
# 設定日誌等級
export TF_LOG=TRACE        # 最詳細

# 日誌等級（由詳細到簡略）
# TRACE > DEBUG > INFO > WARN > ERROR

# 輸出到檔案
export TF_LOG_PATH=terraform.log

# 執行操作（會產生詳細日誌）
terraform apply

# 關閉除錯
unset TF_LOG
unset TF_LOG_PATH
```

### 除錯場景

| 場景 | 建議日誌等級 |
|------|------------|
| Provider API 錯誤 | `DEBUG` 或 `TRACE` |
| 認證問題 | `DEBUG` |
| State 鎖定問題 | `INFO` |
| 一般性排查 | `WARN` |

### 其他除錯工具

```bash
# 互動式控制台（測試表達式）
terraform console
> var.region
"us-east-1"
> cidrsubnet("10.0.0.0/16", 8, 1)
"10.0.1.0/24"

# 依賴圖可視化
terraform graph | dot -Tpng > graph.png

# 顯示當前狀態
terraform show

# 顯示版本資訊
terraform version
```

> **考試重點：** `TF_LOG` 環境變數控制日誌等級。有效值為 `TRACE`、`DEBUG`、`INFO`、`WARN`、`ERROR`。`TF_LOG_PATH` 指定日誌輸出檔案。

---

## 命令速查表

```bash
# 格式化
terraform fmt -recursive -check

# 強制重建
terraform apply -replace="aws_instance.web"

# 導入
terraform import aws_s3_bucket.main my-bucket

# 工作區
terraform workspace new dev && terraform workspace select dev

# 狀態
terraform state list
terraform state show aws_s3_bucket.main
terraform state mv old_name new_name
terraform state rm aws_s3_bucket.main

# 除錯
TF_LOG=DEBUG terraform plan
```

---

## 重點整理

| 考點 | 要記住的 |
|------|---------|
| `fmt` | 標準化格式，`-check` 用於 CI/CD |
| `taint` vs `-replace` | taint 已棄用，用 `-replace` 代替 |
| `import` | 只更新 State，不產生配置代碼 |
| `workspace` | 共用配置 + 獨立 State，default 不能刪 |
| `state mv` | 重構代碼時避免 destroy + create |
| `state rm` | 移除 State 記錄，不刪實際資源 |
| `TF_LOG` | TRACE > DEBUG > INFO > WARN > ERROR |

---

**上一篇：** [03-terraform-basics.md](03-terraform-basics.md)
**下一篇：** [05-terraform-modules.md](05-terraform-modules.md) — 模塊化設計
