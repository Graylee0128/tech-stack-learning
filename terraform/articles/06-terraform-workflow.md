# Objective 6: Terraform 核心工作流程

**考試目標：** Navigate Terraform Workflow
**學習資源：** [Bryan Krausen Labs](https://github.com/btkrausen/hashicorp/tree/master/terraform) | [Core Terraform Workflow](https://www.terraform.io/guides/core-workflow.html)

---

## 對應 Labs

| 子目標 | Lab |
|--------|-----|
| 6a. Describe Terraform workflow | Terraform Workflow, Terraform CLI |
| 6b. `terraform init` | terraform init |
| 6c. `terraform validate` | terraform validate |
| 6d. `terraform plan` | terraform plan |
| 6e. `terraform apply` | terraform apply |
| 6f. `terraform destroy` | terraform destroy |

---

## 6a. 核心工作流程：Write → Plan → Apply

```
1. Write（編寫）
   │  撰寫 .tf 配置檔、定義所需資源
   ↓
2. Init（初始化：terraform init）
   │  下載 Provider 外掛、初始化 Backend
   ↓
3. Validate（驗證：terraform validate）
   │  檢查語法正確性（不連線 API）
   ↓
4. Plan（規劃：terraform plan）
   │  比對：配置 vs State vs 實際環境
   │  產出執行計劃
   ↓
5. Apply（應用：terraform apply）
   │  執行變更、更新 State
   ↓
6. Destroy（銷毀：terraform destroy）
      移除所有受管資源
```

### Plan 的輸出符號

```
Terraform will perform the following actions:

  # aws_s3_bucket.main will be created
  + resource "aws_s3_bucket" "main" {        ← + 新建
      + bucket = "my-bucket"
    }

  # aws_instance.web will be updated in-place
  ~ resource "aws_instance" "web" {          ← ~ 就地更新
      ~ instance_type = "t3.micro" -> "t3.large"
    }

  # aws_security_group.old will be destroyed
  - resource "aws_security_group" "old" {    ← - 刪除
      - name = "old-sg"
    }

  # aws_instance.app must be replaced
-/+ resource "aws_instance" "app" {          ← -/+ 刪除後重建
      ~ ami = "ami-old" -> "ami-new" (forces replacement)
    }

Plan: 1 to add, 1 to change, 1 to destroy.
```

---

## 6b. `terraform init`

初始化 Terraform 工作目錄。**每次更改 Provider、Backend 或 Module 配置後都需要重新執行。**

```bash
terraform init                   # 標準初始化
terraform init -upgrade          # 更新 Provider 和模塊到最新版本
terraform init -migrate-state    # 切換 Backend 時遷移 State
terraform init -reconfigure      # 重新設定 Backend（不遷移 State）
terraform init -backend=false    # 跳過 Backend 初始化
terraform init -get=false        # 跳過模塊下載
```

### init 執行的步驟

```
terraform init
├── 1. 讀取 terraform {} 區塊
├── 2. 初始化 Backend（State 儲存位置）
├── 3. 下載 required_providers 中的 Provider 外掛
├── 4. 下載 module {} 引用的模塊
├── 5. 產生/更新 .terraform.lock.hcl
└── 6. 建立 .terraform/ 目錄
```

> **考試重點：** `init` 是使用 Terraform 的**第一個命令**。它是安全的、可以重複執行的。

---

## 6c. `terraform validate`

驗證配置的語法和內部一致性。

```bash
terraform validate               # 標準驗證
terraform validate -json          # JSON 格式輸出（CI/CD 用）
```

### validate 的特性

```
terraform validate 會檢查：
├── ✅ HCL 語法正確性
├── ✅ 屬性名稱和類型是否正確
├── ✅ 必要參數是否提供
├── ✅ 模塊呼叫的參數匹配
│
├── ❌ 不會連線到雲平台 API
├── ❌ 不會檢查資源是否已存在
├── ❌ 不會驗證變數的實際值
└── ❌ 不需要設定認證（credentials）
```

> **考試重點：** `validate` 只做語法檢查，**不會存取任何 API**。不需要認證。

---

## 6d. `terraform plan`

比對配置、State 和實際環境，產生執行計劃。

```bash
terraform plan                          # 生成執行計劃
terraform plan -out=tfplan              # 儲存計劃到檔案（推薦）
terraform plan -destroy                 # 預覽銷毀操作
terraform plan -target=aws_s3_bucket.main  # 只計劃特定資源
terraform plan -var="key=value"         # 指定變數
terraform plan -var-file="prod.tfvars"  # 使用變數檔
terraform plan -refresh=false           # 跳過狀態刷新（加速，但可能不準）
terraform plan -parallelism=20          # 調整並行度（預設 10）
terraform plan -json | jq              # JSON 格式輸出
terraform plan -detailed-exitcode       # 細分 exit code（0=無變更, 1=錯誤, 2=有變更）
```

### plan 的比對邏輯

```
terraform plan 的三方比對：

  .tf 配置          terraform.tfstate       實際雲端資源
  （期望狀態）        （已知狀態）             （真實狀態）
       │                   │                     │
       └───────┬───────────┘                     │
               │                                 │
         配置 vs State                     State vs 實際
         （你改了什麼？）               （有人手動改了什麼？）
               │                                 │
               └─────────────┬───────────────────┘
                             │
                     執行計劃（Plan）
                   + create / ~ update / - destroy
```

> **最佳實踐：** 使用 `-out=tfplan` 儲存計劃，再用 `terraform apply tfplan` 應用。確保 plan 和 apply 之間的操作一致。

---

## 6e. `terraform apply`

執行計劃中的變更。

```bash
terraform apply                         # 互動式確認（先 plan 再確認）
terraform apply tfplan                  # 應用已儲存的計劃（不再 plan）
terraform apply -auto-approve           # 自動確認（CI/CD 用，謹慎使用）
terraform apply -target=aws_s3_bucket.main  # 只應用特定資源
terraform apply -replace="aws_instance.web" # 強制重建資源
terraform apply -var="key=value"        # 指定變數
terraform apply -parallelism=20         # 調整並行度
terraform apply -refresh-only           # 只刷新 State（取代 terraform refresh）
terraform apply -lock=false             # 不鎖定 State（危險，不建議）
```

### apply 的流程

```
terraform apply
├── 1. 讀取配置和 State
├── 2. 刷新 State（查詢實際狀態）
├── 3. 產生執行計劃（等同 plan）
├── 4. 顯示計劃並等待確認（除非 -auto-approve）
├── 5. 按依賴順序執行變更
│   ├── 平行建立無依賴的資源
│   └── 順序處理有依賴的資源
├── 6. 更新 State 檔案
└── 7. 顯示 Output 值
```

> **考試重點：** 使用 `terraform apply tfplan` 時不會再次 plan，直接應用已儲存的計劃。

---

## 6f. `terraform destroy`

銷毀所有 Terraform 管理的資源。

```bash
terraform destroy                       # 互動式確認
terraform destroy -auto-approve         # 自動確認（CI/CD 用）
terraform destroy -target=aws_s3_bucket.main  # 只銷毀特定資源
```

### destroy 等同於

```bash
# 以下兩個命令等效
terraform destroy
terraform apply -destroy
```

### 銷毀順序

```
terraform destroy 的順序：
├── 1. 計算依賴圖的反向順序
├── 2. 先刪除依賴方（如 bucket_policy）
├── 3. 再刪除被依賴方（如 s3_bucket）
└── 4. 更新 State（移除已銷毀的資源）
```

> **考試重點：** `terraform destroy` = `terraform apply -destroy`。銷毀順序是依賴圖的**反向**。

---

## 完整工作流程範例

```bash
# 1. 編寫配置
vim main.tf

# 2. 初始化
terraform init

# 3. 格式化（可選）
terraform fmt -recursive

# 4. 驗證語法
terraform validate

# 5. 預覽變更
terraform plan -out=tfplan

# 6. 應用變更
terraform apply tfplan

# 7. 查看結果
terraform show
terraform output

# 8.（完成後）銷毀資源
terraform destroy
```

---

## 重點整理

| 考點 | 要記住的 |
|------|---------|
| 核心流程 | Write → Init → Plan → Apply |
| `init` | 第一個命令，下載 Provider + 初始化 Backend |
| `validate` | 只檢查語法，不連 API，不需認證 |
| `plan` 符號 | `+` 新建, `~` 更新, `-` 刪除, `-/+` 重建 |
| `plan -out` | 儲存計劃，確保 apply 一致 |
| `apply tfplan` | 不再 plan，直接應用 |
| `-auto-approve` | 跳過確認，CI/CD 用 |
| `destroy` | = `apply -destroy`，反向依賴順序 |
| `-detailed-exitcode` | 0=無變更, 1=錯誤, 2=有變更 |

---

**上一篇：** [05-terraform-modules.md](05-terraform-modules.md)
**下一篇：** [07-terraform-state.md](07-terraform-state.md) — State 管理
