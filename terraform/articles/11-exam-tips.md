# Terraform Associate 考試要訣

**考試：** HashiCorp Certified: Terraform Associate
**資源：** [Bryan Krausen Exam Tips](https://github.com/btkrausen/hashicorp/blob/master/terraform/ExamTips.md) | [HashiCorp 認證頁面](https://developer.hashicorp.com/terraform/tutorials/certification)

---

## 考試格式

| 項目 | 內容 |
|------|------|
| **題型** | 多選題、多選複選題、填空題 |
| **費用** | $70.50 USD |
| **監考** | PSI 線上監考 |
| **時長** | 60 分鐘 |
| **題數** | ~57 題 |
| **及格線** | ~70% |
| **有效期** | 2 年 |
| **重考** | 24 小時後可重考 |

---

## 準備策略

### 1. 動手實驗 > 死背

> "There's no better way to study and prepare than to use the product in your own environment."

- 在自己的 AWS 帳號中跑完所有 70+ Labs
- 理解每個指令的效果，而不只是記住語法
- 故意打破配置，看看會發生什麼

### 2. 理解「為什麼」

- 不只知道正確答案，也要理解為什麼其他選項是錯的
- 考題通常包含 2-3 個看起來合理的選項

### 3. 善用官方文件

- 考題措辭通常來自官方文件
- 有不確定的地方，查閱 [Terraform Documentation](https://www.terraform.io/docs)

### 4. 免費練習

使用不需要雲帳號的 Provider 做實驗：
- `random` — 隨機值產生
- `tls` — TLS 金鑰和憑證
- `local` — 本地檔案操作
- `null` — 空資源（觸發 Provisioner）

### 5. 練習考題

- [Bryan Krausen Practice Exams (Udemy)](https://www.udemy.com/course/terraform-hands-on-labs)
- HashiCorp 官方 Sample Questions

---

## 高頻考點清單

### Tier 1：必考（幾乎每次都出現）

| 主題 | 重點 | 出處 |
|------|------|------|
| **版本約束** | `~>` Pessimistic Constraint 的行為 | Obj 3a |
| **變數優先順序** | TF_VAR > -var > -var-file > auto.tfvars > terraform.tfvars > default | Obj 8a |
| **State 用途** | Mapping, Metadata, Performance | Obj 2b |
| **Provisioner** | 是「Last Resort」，優先用 user_data/cloud-init | Obj 3e |
| **Module 作用域** | 子模塊無法存取父模塊變數 | Obj 5c |

### Tier 2：常考

| 主題 | 重點 | 出處 |
|------|------|------|
| **OSS vs Cloud Workspace** | 功能差異、State 管理方式 | Obj 9b |
| **Sentinel** | Enterprise/Cloud 專屬，plan 後 apply 前 | Obj 9a |
| **Backend** | Partial Configuration、`-migrate-state` | Obj 7f |
| **Lifecycle** | create_before_destroy / prevent_destroy / ignore_changes | Obj 8h |
| **Dynamic Block** | 語法、iterator 使用 | Obj 8g |
| **State Locking** | S3 + DynamoDB，force-unlock | Obj 7b |

### Tier 3：偶爾出現

| 主題 | 重點 | 出處 |
|------|------|------|
| **terraform import** | 只更新 State，不產生配置 | Obj 4c |
| **terraform fmt** | `-check` 用於 CI/CD | Obj 4a |
| **sensitive** | 只隱藏 CLI 輸出，State 仍明文 | Obj 7g |
| **terraform graph** | 依賴圖可視化 | Obj 8h |
| **TF_LOG** | TRACE > DEBUG > INFO > WARN > ERROR | Obj 4f |

---

## 易混淆概念對照

### `count` vs `for_each`

| | `count` | `for_each` |
|--|---------|-----------|
| **輸入** | 數字 | set 或 map |
| **引用** | `resource[0]` | `resource["key"]` |
| **刪除行為** | 刪除中間元素會重建後面的 | 只刪除指定的 key |
| **推薦** | 簡單的開關（0 或 1） | 大多數情況 |

### `variable` vs `locals` vs `output`

| | `variable` | `locals` | `output` |
|--|-----------|---------|---------|
| **方向** | 外部 → 模塊 | 模塊內部 | 模塊 → 外部 |
| **可覆蓋** | Yes（tfvars, env, CLI） | No | No |
| **用途** | 參數化 | 計算值、減少重複 | 暴露給其他模塊/CLI |

### `terraform refresh` vs `terraform plan`

| | `refresh` | `plan` |
|--|----------|--------|
| **行為** | 只更新 State | 比對配置 + State + 實際 |
| **輸出** | 無執行計劃 | 有執行計劃 |
| **修改資源** | 不修改 | 不修改（plan 階段） |
| **現狀** | 已棄用 → `apply -refresh-only` | 仍然使用 |

### Resource vs Data Source

| | Resource | Data Source |
|--|---------|------------|
| **語法** | `resource "type" "name"` | `data "type" "name"` |
| **行為** | Create/Update/Delete | Read Only |
| **State** | 記錄在 State | 每次重新查詢 |
| **引用** | `type.name.attr` | `data.type.name.attr` |

---

## 常見陷阱

### 1. `terraform validate` 不連 API
```
❌ 以為 validate 會檢查 AWS 資源是否存在
✅ validate 只檢查語法，不需要任何認證
```

### 2. `sensitive = true` 不加密 State
```
❌ 以為標記 sensitive 就安全了
✅ State 檔案中仍然是明文，必須用 encrypt = true 加密
```

### 3. `terraform import` 不產生代碼
```
❌ 以為 import 會自動產生 .tf 檔案
✅ import 只更新 State，需要手動寫配置（1.5+ 的 import block 除外）
```

### 4. Module source 路徑中的 `//`
```
❌ source = "git::https://github.com/org/repo.git/modules/vpc"
✅ source = "git::https://github.com/org/repo.git//modules/vpc"
                                                 ↑↑ 雙斜線分隔 repo 和子目錄
```

### 5. Provider 繼承
```
❌ 在子模塊中重新定義 Provider
✅ 子模塊自動繼承 Root Module 的 Provider
```

---

## 考前清單

- [ ] 能說出 Terraform 工作流程的 5 個步驟
- [ ] 能解釋 `~> 5.0` 和 `~> 5.0.1` 的差異
- [ ] 能列出變數優先順序（6 個層級）
- [ ] 能區分 OSS Workspace 和 Cloud Workspace
- [ ] 能解釋 State 的三大用途
- [ ] 能寫出 Dynamic Block 語法
- [ ] 能說出 Sentinel 的三個策略等級
- [ ] 能區分 `state rm` 和 `destroy` 的差異
- [ ] 能解釋 `create_before_destroy` 的行為
- [ ] 能列出 Provisioner 的替代方案

---

## 學習文件索引

| 文件 | 對應考試目標 |
|------|------------|
| [01-02-iac-and-terraform-purpose.md](01-02-iac-and-terraform-purpose.md) | Objective 1-2 |
| [03-terraform-basics.md](03-terraform-basics.md) | Objective 3 |
| [04-terraform-cli.md](04-terraform-cli.md) | Objective 4 |
| [05-terraform-modules.md](05-terraform-modules.md) | Objective 5 |
| [06-terraform-workflow.md](06-terraform-workflow.md) | Objective 6 |
| [07-terraform-state.md](07-terraform-state.md) | Objective 7 |
| [08-terraform-configuration.md](08-terraform-configuration.md) | Objective 8 |
| [09-terraform-cloud.md](09-terraform-cloud.md) | Objective 9 |
| [10-practical-examples.md](10-practical-examples.md) | 實戰案例 |
| [00-course-mindmap.md](00-course-mindmap.md) | 課程心智圖總覽 |
| [terraform-associate-study-guide.md](terraform-associate-study-guide.md) | 完整學習指南 |
