# HashiCorp Certified: Terraform Associate — 課程心智圖

**來源：Bryan Krausen - Terraform Hands-On Labs Course**
**轉換自原始 PDF 心智圖**

---

## 課程總覽

```
HashiCorp Certified: Terraform Associate - Hands On Labs
│
├── 1. Understand IaC Concepts
├── 2. Understand Terraform's Purpose
├── 3. Understand Terraform Basics
├── 4. Use the Terraform CLI
├── 5. Interact with Terraform Modules
├── 6. Navigate Terraform Workflow
├── 7. Implement and Maintain State
├── 8. Read, Generate, and Modify Configuration
├── 9. Understand Terraform Cloud and Enterprise
└── Preparing for the Exam
```

---

## Objective 1: Understand Infrastructure as Code (IaC) Concepts

```
1. Understand IaC Concepts
├── 1a. Explain what IaC is
│   └── Lab: What is Infrastructure as Code
└── 1b. Describe advantages of IaC patterns
    └── Lab: Benefits of IaC
```

→ 詳細內容：[01-02-iac-and-terraform-purpose.md](01-02-iac-and-terraform-purpose.md)

---

## Objective 2: Understand Terraform's Purpose (vs other IaC)

```
2. Understand Terraform's Purpose
├── 2a. Explain multi-cloud and provider-agnostic benefits
│   ├── Lab: Terraform Purpose
│   └── Lab: Terraform Basics
└── 2b. Explain the benefits of state
    └── Lab: Benefits of State
```

→ 詳細內容：[01-02-iac-and-terraform-purpose.md](01-02-iac-and-terraform-purpose.md)

---

## Objective 3: Understand Terraform Basics

```
3. Understand Terraform Basics
├── 3. Terraform HCL Basics
│   ├── Lab: HashiCorp Configuration Language (HCL)
│   ├── Lab: Terraform Configuration Block
│   ├── Lab: Terraform Resource Block
│   ├── Lab: Terraform Data Block
│   ├── Lab: Terraform Input Variable Block
│   ├── Lab: Terraform Local Variable Block
│   ├── Lab: Terraform Module Block
│   ├── Lab: Terraform Output Block
│   └── Lab: Commenting Terraform Code
│
├── 3a. Handle Terraform and provider installation and versioning
│   └── Lab: Provider Installation
│
├── 3b. Describe plugin based architecture
│   └── Lab: Terraform Plug-in Based Architecture
│
├── 3c. Demonstrate using multiple providers
│   ├── Lab: Using Multiple Terraform Providers
│   └── Lab: Terraform TLS Provider
│
├── 3d. Describe how Terraform finds and fetches providers
│   └── Lab: Fetch, Version and Upgrade Terraform Providers
│
└── 3e. Explain when to use and not use provisioners
    └── Lab: Terraform Provisioners
```

→ 詳細內容：[03-terraform-basics.md](03-terraform-basics.md)

---

## Objective 4: Use the Terraform CLI (outside of core workflow)

```
4. Use the Terraform CLI
├── 4a. Choose when to use terraform fmt
│   └── Lab: Auto Formatting Terraform Code
│
├── 4b. Choose when to use terraform taint
│   └── Lab: Terraform Taint and Replace
│
├── 4c. Choose when to use terraform import
│   └── Lab: Terraform Import
│
├── 4d. Choose when to use terraform workspace
│   └── Lab: Terraform Workspaces (OSS)
│
├── 4e. Choose when to use terraform state
│   └── Lab: Terraform State CLI
│
└── 4f. Choose when to enable verbose logging
    └── Lab: Debugging Terraform
```

→ 詳細內容：[04-terraform-cli.md](04-terraform-cli.md)

---

## Objective 5: Interact with Terraform Modules

```
5. Interact with Terraform Modules
├── 5a. Contrast module source options
│   ├── Lab: Terraform Modules
│   └── Lab: Sourcing Terraform Modules
│
├── 5b. Interact with module inputs and outputs
│   └── Lab: Terraform Module Inputs and Outputs
│
├── 5c. Describe variable scope within modules/child modules
│   └── Lab: Terraform Module Variables Scope
│
├── 5d. Discover modules from the public Terraform Module Registry
│   └── Lab: Consuming Terraform Modules from Public Module Registry
│
└── 5e. Defining module version
    └── Lab: Versioning Terraform Modules
```

→ 詳細內容：[05-terraform-modules.md](05-terraform-modules.md)

---

## Objective 6: Navigate Terraform Workflow

```
6. Navigate Terraform Workflow
├── 6a. Describe Terraform workflow (Write -> Plan -> Create)
│   ├── Lab: Terraform Workflow
│   └── Lab: Terraform CLI
│
├── 6b. Initialize a Terraform working directory (terraform init)
│   └── Lab: terraform init
│
├── 6c. Validate a Terraform configuration (terraform validate)
│   └── Lab: terraform validate
│
├── 6d. Generate and review an execution plan (terraform plan)
│   └── Lab: terraform plan
│
├── 6e. Execute changes to infrastructure (terraform apply)
│   └── Lab: terraform apply
│
└── 6f. Destroy Terraform managed infrastructure (terraform destroy)
    └── Lab: terraform destroy
```

→ 詳細內容：[06-terraform-workflow.md](06-terraform-workflow.md)

---

## Objective 7: Implement and Maintain State

```
7. Implement and Maintain State
├── 7a. Describe default local backend
│   └── Lab: Terraform Local State
│
├── 7b. Outline state locking
│   └── Lab: Terraform State Locking
│
├── 7c. Handle backend authentication methods
│   └── Lab: Terraform State: Backend Authentication
│
├── 7d. Describe remote state storage mechanisms
│   ├── Lab: Terraform State: Standard Backend Storage
│   ├── Lab: Terraform Remote State Enhanced Backend
│   └── Lab: Terraform State Migration
│
├── 7e. Describe effect of Terraform refresh on state
│   └── Lab: Terraform Refresh
│
├── 7f. Describe backend block and partial configurations
│   └── Lab: Terraform Backend Configurations
│
└── 7g. Understand secret management in state files
    └── Lab: Terraform State Secrets
```

→ 詳細內容：[07-terraform-state.md](07-terraform-state.md)

---

## Objective 8: Read, Generate, and Modify Configuration

```
8. Read, Generate, and Modify Configuration
├── 8a. Demonstrate use of variables and outputs
│   ├── Lab: Terraform Input Variables
│   ├── Lab: Terraform Local Values
│   └── Lab: Terraform Outputs
│
├── 8b. Describe secure secret injection best practice
│   └── Lab: Terraform Secure Variables
│
├── 8c. Understand the use of collection and structural types
│   └── Lab: Terraform Collection Types
│
├── 8d. Create and differentiate resource and data configuration
│   ├── Lab: Terraform Resources
│   └── Lab: Terraform Data Blocks and Configuration
│
├── 8e. Use resource addressing and resource parameters
│   ├── Lab: Terraform Interpolation Syntax
│   └── Lab: Terraform Console
│
├── 8f. Use Terraform built-in functions
│   ├── Lab: Terraform Console
│   ├── Lab: Terraform Functions
│   └── Lab: Terraform Conditional Operator
│
├── 8g. Configure resource using a dynamic block
│   └── Lab: Terraform Dynamic Blocks
│
└── 8h. Describe built-in dependency management
    ├── Lab: Terraform Graph
    └── Lab: Terraform Lifecycles
```

→ 詳細內容：[08-terraform-configuration.md](08-terraform-configuration.md)

---

## Objective 9: Understand Terraform Cloud and Enterprise Capabilities

```
9. Terraform Cloud and Enterprise
├── 9a. Describe benefits of Sentinel, registry, and workspaces
│   ├── Lab: Terraform Cloud: Getting Started
│   ├── Lab: Terraform Cloud: Workspaces
│   ├── Lab: Terraform Cloud: Private Module Registry
│   └── Lab: Terraform Cloud: Sentinel for Terraform
│
├── 9b. Differentiate OSS and TFE workspaces
│   └── Lab: Terraform Cloud: Workspaces
│
└── 9c. Summarize features of Terraform Cloud
    ├── Lab: Terraform Cloud CLI Workflow
    └── Lab: Terraform Cloud Collaboration
```

→ 詳細內容：[09-terraform-cloud.md](09-terraform-cloud.md)

---

## Preparing for the Exam

```
Preparing for the Exam
├── Retake this course and focus on objectives you need to improve
├── Take a series of Terraform Certification Practice Tests
├── Review Study Tips
└── Pass the Certification
    └── HashiCorp Certified: Terraform Associate
```

### 備考建議

1. **動手實驗**：跑完所有 70+ Labs，在自己的 AWS 帳號中實際操作
2. **理解原理**：不只知道正確答案，也要理解為什麼其他選項是錯的
3. **善用官方文件**：考題措辭通常來自官方文件
4. **免費練習**：使用 `local`、`tls`、`random` Provider，不產生雲端費用
5. **練習考題**：使用 Bryan Krausen 的 Udemy Practice Tests

---

## 學習文件索引

| 文件 | 對應考試目標 | 內容 |
|------|------------|------|
| [01-02-iac-and-terraform-purpose.md](01-02-iac-and-terraform-purpose.md) | Objective 1-2 | IaC 概念、Terraform 定位與 State 用途 |
| [03-terraform-basics.md](03-terraform-basics.md) | Objective 3 | HCL 語法、Provider、多區域配置、Provisioner |
| [04-terraform-cli.md](04-terraform-cli.md) | Objective 4 | fmt / taint / import / workspace / state / debugging |
| [05-terraform-modules.md](05-terraform-modules.md) | Objective 5 | 模塊結構、來源、輸入輸出、作用域、版本管理 |
| [06-terraform-workflow.md](06-terraform-workflow.md) | Objective 6 | init / validate / plan / apply / destroy 完整工作流 |
| [07-terraform-state.md](07-terraform-state.md) | Objective 7 | State 管理、鎖定、Backend、敏感資料、安全實踐 |
| [08-terraform-configuration.md](08-terraform-configuration.md) | Objective 8 | 變數系統、內建函數、Dynamic Block、依賴管理、Lifecycle |
| [09-terraform-cloud.md](09-terraform-cloud.md) | Objective 9 | Terraform Cloud、Sentinel、OSS vs Cloud Workspace |
| [10-practical-examples.md](10-practical-examples.md) | 實戰案例 | S3 + CloudFront + IAM 完整配置 |
| [11-exam-tips.md](11-exam-tips.md) | 考試要訣 | 高頻考點清單、備考策略 |
| [terraform-associate-study-guide.md](terraform-associate-study-guide.md) | 全部 | 完整學習指南（總覽） |
