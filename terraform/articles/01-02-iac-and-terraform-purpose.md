# Objective 1-2: IaC 概念與 Terraform 定位

**考試目標：** Understand Infrastructure as Code (IaC) Concepts + Understand Terraform's Purpose
**學習資源：** [Bryan Krausen Labs](https://github.com/btkrausen/hashicorp/tree/master/terraform) | [Terraform 官方文件](https://www.terraform.io/docs)

---

## 對應 Labs

| 子目標 | Lab |
|--------|-----|
| 1a. Explain what IaC is | What is Infrastructure as Code |
| 1b. Describe advantages of IaC patterns | Benefits of IaC |
| 2a. Explain multi-cloud and provider-agnostic benefits | Terraform Purpose / Terraform Basics |
| 2b. Explain the benefits of state | Benefits of State |

---

## 1a. 什麼是 Infrastructure as Code？

IaC 是透過**程式碼**（而非手動操作）來管理和配置基礎設施的方法。

```
傳統方式（手動）              IaC 方式（自動化）
────────────────              ─────────────────
登入 AWS Console              編寫 .tf 配置檔
點擊建立 EC2          →      terraform apply
手動配置安全組                 版本控制 + 可重複部署
無法追蹤變更                   Git 追蹤所有歷史
```

### IaC 的兩種方式

| 方式 | 說明 | 代表工具 |
|-----|------|---------|
| **Declarative（聲明式）** | 描述「想要什麼」，工具決定「如何達到」 | Terraform, CloudFormation |
| **Imperative（命令式）** | 一步步描述「怎麼做」 | Ansible (部分), Shell Script |

```hcl
# Declarative 範例 — 你只需要描述最終狀態
resource "aws_instance" "web" {
  ami           = "ami-12345678"
  instance_type = "t3.micro"
  tags = { Name = "web-server" }
}
# Terraform 會自動判斷需要 create / update / 還是什麼都不做
```

---

## 1b. IaC 的核心優勢

| 優勢 | 說明 |
|-----|------|
| **版本控制** | 所有配置都在 Git 中，可追蹤、可回滾 |
| **可重複性** | 同一份程式碼可部署到 dev/staging/prod |
| **一致性** | 消除「手動點擊」造成的環境差異（Configuration Drift） |
| **自動化** | 整合 CI/CD 管線，實現自動部署 |
| **文件化** | 程式碼即文件，團隊成員一看就懂 |
| **成本管理** | 快速建立和銷毀環境，避免資源閒置 |
| **風險降低** | 透過 `terraform plan` 預覽變更，減少人為錯誤 |
| **協作** | 多人協作、Code Review、Pull Request 流程 |

### Configuration Drift 問題

```
Day 1: 透過 Console 建立 EC2 (t3.micro)
Day 30: 有人手動改成 t3.large（沒有記錄）
Day 60: 另一個人改了安全組（也沒記錄）
Day 90: 沒人知道這台 EC2 的完整配置了 ← Configuration Drift
```

**IaC 如何解決：**
- 所有變更都在 Git 中，有完整歷史
- `terraform plan` 會偵測 Drift（配置 vs 實際環境的差異）
- `terraform apply` 可以強制回到預期狀態

> **考試重點：** IaC 解決的核心問題是 **Configuration Drift**（配置漂移）。

---

## 2a. 多雲與供應商無關的優勢

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

### 與其他 IaC 工具的比較

| 工具 | 類型 | 語言 | 特色 | 適用場景 |
|-----|------|------|------|---------|
| **Terraform** | Declarative / Provisioning | HCL | 多雲、狀態管理、模組化 | 基礎設施配置 |
| **CloudFormation** | Declarative / Provisioning | JSON/YAML | AWS 原生、深度整合 | 純 AWS 環境 |
| **Ansible** | Procedural / Configuration | YAML | 無代理、SSH、配置管理 | 軟體安裝/配置 |
| **Pulumi** | Declarative / Provisioning | Python/JS/Go | 使用通用程式語言 | 開發者偏好的 IaC |
| **Chef/Puppet** | Declarative / Configuration | Ruby/DSL | 成熟、大規模 | 伺服器配置管理 |

### Terraform 獨特優勢

1. **Provider 生態系統**：3000+ Provider 涵蓋主流雲平台和 SaaS
2. **一致的工作流程**：不管管理什麼資源，都是 `init → plan → apply`
3. **State 管理**：精確追蹤資源狀態，支持團隊協作
4. **模組化設計**：可複用的配置包，減少重複代碼
5. **開源社群**：龐大的社群模塊和最佳實踐

> **考試重點：** Terraform 使用 **Declarative**（聲明式）方式——你描述「想要什麼」，Terraform 計算「如何達到」。

---

## 2b. State 的用途

State（狀態）是 Terraform 的核心機制，記錄了「你管理的基礎設施長什麼樣」。

### State 的三大用途

```
terraform.tfstate 的作用：
├── 1. Mapping（映射）
│   └── 配置中的 resource "aws_s3_bucket" "main" → 實際的 S3 Bucket ID
│
├── 2. Metadata（元資料）
│   └── 追蹤資源依賴關係、Provider 版本
│
└── 3. Performance（效能）
    └── 快取資源屬性，不需每次都呼叫 API 查詢
```

### State 的運作流程

```
terraform plan 的比對邏輯：

  .tf 配置檔（你想要的狀態）
       │
       ├── 比較 ──→ terraform.tfstate（State 記錄的狀態）
       │                    │
       │                    ├── 比較 ──→ 實際雲端資源
       │                    │
       ↓                    ↓
  執行計劃：+ create / ~ update / - destroy
```

### 為什麼需要 State？

| 沒有 State | 有 State |
|-----------|---------|
| 無法知道哪些資源是 Terraform 管理的 | 精確追蹤所有受管資源 |
| 每次 plan 都需要掃描整個雲帳號 | 直接從快取讀取，更快 |
| 無法偵測 Drift | 可比對配置 vs 實際狀態 |
| 無法處理資源依賴順序 | 內建依賴圖（Dependency Graph） |

### State 檔案範例

```json
{
  "version": 4,
  "terraform_version": "1.6.0",
  "resources": [
    {
      "mode": "managed",
      "type": "aws_s3_bucket",
      "name": "main",
      "provider": "provider[\"registry.terraform.io/hashicorp/aws\"]",
      "instances": [
        {
          "attributes": {
            "id": "my-bucket-12345",
            "bucket": "my-bucket-12345",
            "region": "us-east-1",
            "arn": "arn:aws:s3:::my-bucket-12345"
          }
        }
      ]
    }
  ]
}
```

> **考試重點：** State 的三個關鍵目的——**Mapping**（映射配置到真實資源）、**Metadata**（追蹤依賴）、**Performance**（快取資源屬性）。

---

## 重點整理

| 考點 | 要記住的 |
|------|---------|
| IaC 是什麼 | 透過程式碼管理基礎設施 |
| IaC 核心問題 | Configuration Drift |
| Declarative vs Imperative | Terraform = Declarative |
| Terraform 獨特性 | Provider-Agnostic, 多雲, State 管理 |
| State 三大用途 | Mapping, Metadata, Performance |
| State 存放位置 | 預設 `terraform.tfstate`（本地） |

---

**下一篇：** [03-terraform-basics.md](03-terraform-basics.md) — HCL 語法與 Provider 配置
