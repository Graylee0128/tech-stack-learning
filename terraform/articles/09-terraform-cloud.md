# Objective 9: Terraform Cloud 與 Enterprise

**考試目標：** Understand Terraform Cloud and Enterprise Capabilities
**學習資源：** [Bryan Krausen Labs](https://github.com/btkrausen/hashicorp/tree/master/terraform) | [Terraform Cloud Documentation](https://www.terraform.io/docs/cloud/index.html)

---

## 對應 Labs

| 子目標 | Lab |
|--------|-----|
| 9a. Sentinel, registry, workspaces | Getting Started, Workspaces, Private Module Registry, Sentinel for Terraform |
| 9b. Differentiate OSS and TFE workspaces | Terraform Cloud: Workspaces |
| 9c. Summarize features of Terraform Cloud | Terraform Cloud CLI Workflow, Terraform Cloud Collaboration |

---

## Terraform Cloud 概述

Terraform Cloud 是 HashiCorp 的**托管服務**，為團隊協作提供完整的 Terraform 工作流。

```
Terraform Cloud 功能架構：
├── Remote Execution    — 遠端執行 plan/apply
├── State Management    — 安全的遠端 State 儲存
├── VCS Integration     — Git push → 自動觸發
├── Private Registry    — 團隊內部模塊分享
├── Sentinel            — Policy as Code
├── Team Management     — 角色權限控制（RBAC）
├── Cost Estimation     — Apply 前估算費用
├── Run Tasks           — 整合第三方工具
└── Secure Variables    — 加密的變數儲存
```

### 版本對比

| 功能 | Terraform OSS | Terraform Cloud (Free) | Terraform Cloud (Team & Governance) | Terraform Enterprise |
|------|-------------|----------------------|-----------------------------------|---------------------|
| CLI 工具 | Yes | Yes | Yes | Yes |
| Remote State | 需自建 | Yes | Yes | Yes |
| VCS 整合 | 無 | Yes | Yes | Yes |
| Private Registry | 無 | Yes | Yes | Yes |
| Team Management | 無 | Limited | Yes | Yes |
| Sentinel | 無 | 無 | Yes | Yes |
| SSO / SAML | 無 | 無 | 無 | Yes |
| 自建 | N/A | 無 | 無 | Yes（私有部署） |

---

## 9a. Sentinel、Registry 與 Workspaces

### Sentinel — Policy as Code

Sentinel 是 HashiCorp 的策略框架，在 **plan 之後、apply 之前** 執行策略檢查。

```python
# 範例 1：強制所有 EC2 實例必須有 "Owner" 標籤
import "tfplan"

main = rule {
  all tfplan.resources.aws_instance as _, instances {
    all instances as _, r {
      r.applied.tags contains "Owner"
    }
  }
}

# 範例 2：限制 EC2 實例類型
import "tfplan"

allowed_types = ["t3.micro", "t3.small", "t3.medium"]

main = rule {
  all tfplan.resources.aws_instance as _, instances {
    all instances as _, r {
      r.applied.instance_type in allowed_types
    }
  }
}
```

### Sentinel 策略等級

| 等級 | 行為 |
|------|------|
| **Advisory** | 警告，但允許繼續（建議性） |
| **Soft Mandatory** | 預設阻止，但管理員可以覆蓋 |
| **Hard Mandatory** | 強制阻止，無法覆蓋 |

### Sentinel 執行流程

```
terraform plan
    ↓
Sentinel Policy Check    ← 在這裡執行
    ↓
    ├── Pass → terraform apply
    └── Fail → 阻止 apply
```

> **考試重點：** Sentinel 是 **Terraform Cloud (Team & Governance) / Enterprise 專屬**功能。OSS 版沒有。它在 plan 之後、apply 之前執行。

### Private Module Registry

團隊內部共享可複用的 Terraform 模塊。

```
Private Registry 功能：
├── 版本管理（Semantic Versioning）
├── VCS 整合（Push tag → 自動發佈新版本）
├── 使用方式和 Public Registry 完全相同
└── 命名規範：terraform-<PROVIDER>-<NAME>
```

```hcl
# 從 Private Registry 使用模塊
module "vpc" {
  source  = "app.terraform.io/my-org/vpc/aws"
  version = "~> 1.0"
}
```

### Terraform Cloud Workspaces

```
每個 Workspace 包含：
├── Terraform Configuration（配置代碼）
├── Variables（變數，支持加密）
├── State（遠端 State，自動加密）
├── Run History（執行歷史）
└── Access Control（權限設定）
```

---

## 9b. OSS Workspaces vs Cloud Workspaces

| 特性 | OSS Workspaces | Cloud Workspaces |
|-----|---------------|-----------------|
| **State 儲存** | 本地 / 自行管理的 Backend | Terraform Cloud 管理（自動加密） |
| **變數管理** | `.tfvars` 檔案 | Web UI / API，支持加密（Sensitive） |
| **權限控制** | 無 | Team-based RBAC |
| **執行環境** | 本地機器 | Cloud 代管的 Runner |
| **VCS 整合** | 手動 | 自動觸發 Plan/Apply |
| **Run 歷史** | 無 | 完整的執行歷史和日誌 |
| **鎖定** | 需自行配置（如 DynamoDB） | 自動 |
| **配置代碼** | 共用同一份代碼 | 每個 Workspace 可對應不同 VCS repo/branch |
| **用途** | `terraform.workspace` 做簡單多環境 | 完整的團隊協作環境 |

### OSS Workspace 用法

```bash
# 建立和切換
terraform workspace new dev
terraform workspace select prod

# State 儲存在不同目錄
terraform.tfstate.d/dev/terraform.tfstate
terraform.tfstate.d/prod/terraform.tfstate

# 在配置中使用
resource "aws_s3_bucket" "main" {
  bucket = "myapp-${terraform.workspace}"
}
```

### Cloud Workspace 用法

```hcl
# 配置 Cloud Backend
terraform {
  cloud {
    organization = "my-org"
    workspaces {
      name = "my-workspace"
      # 或使用 tag 匹配多個 workspace
      # tags = ["app:web"]
    }
  }
}
```

> **考試重點：** OSS Workspace = 共用配置 + 獨立 State + 無權限控制。Cloud Workspace = 獨立配置 + 獨立 State + RBAC + VCS 整合 + 完整功能。

---

## 9c. Terraform Cloud 功能摘要

### 三種工作流程

| 工作流 | 觸發方式 | 適用場景 |
|--------|---------|---------|
| **VCS Workflow** | Push 到 Git → 自動觸發 Plan → Review → Apply | 團隊日常開發 |
| **CLI Workflow** | 本地 `terraform plan/apply` → 遠端執行 | 開發者本地測試 |
| **API Workflow** | 透過 REST API 觸發 | CI/CD Pipeline 整合 |

### VCS Workflow 流程

```
Developer
    │
    ├── Push to feature branch
    │       ↓
    ├── Pull Request → Terraform Cloud 自動 plan
    │       ↓
    ├── Review Plan → 團隊 Code Review
    │       ↓
    ├── Merge to main → 自動觸發 Apply
    │       ↓
    └── Apply 完成 → 更新 State
```

### 變數管理

```
Terraform Cloud 變數類型：
├── Terraform Variables（對應 .tf 中的 variable）
│   ├── 普通變數：明文儲存，可在 UI 查看
│   └── Sensitive 變數：加密儲存，寫入後無法查看
│
└── Environment Variables（系統環境變數）
    ├── AWS_ACCESS_KEY_ID
    ├── AWS_SECRET_ACCESS_KEY（Sensitive）
    └── 其他自訂環境變數
```

### Cost Estimation

```
terraform apply 之前顯示：

Resources: 3 to add, 0 to change, 0 to destroy
Cost Estimation:
  Monthly cost will increase by $45.26
  ├── aws_instance.web: +$8.47/mo
  ├── aws_rds_instance.db: +$25.55/mo
  └── aws_nat_gateway.main: +$11.24/mo
```

### Run Tasks

整合第三方工具到 Terraform Cloud 的工作流中：

```
支持的整合類型：
├── 安全掃描（Snyk, Bridgecrew, Checkov）
├── 合規檢查（OPA, Regula）
├── 成本管理（Infracost）
└── 自訂 webhook
```

---

## 重點整理

| 考點 | 要記住的 |
|------|---------|
| Sentinel | Cloud/Enterprise 專屬，plan 後 apply 前執行 |
| Sentinel 等級 | Advisory / Soft Mandatory / Hard Mandatory |
| Private Registry | 命名 `terraform-<PROVIDER>-<NAME>`，VCS 整合 |
| OSS vs Cloud Workspace | OSS = 共用配置 + 獨立 State；Cloud = 完整功能 |
| 三種 Workflow | VCS（Git push）, CLI（本地觸發）, API（API 觸發） |
| 變數管理 | Terraform Variables + Environment Variables，支持 Sensitive |
| Cost Estimation | Apply 前估算月費 |

---

**上一篇：** [08-terraform-configuration.md](08-terraform-configuration.md)
**下一篇：** [10-practical-examples.md](10-practical-examples.md) — 實戰案例
