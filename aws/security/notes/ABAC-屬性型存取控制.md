# Beyond RBAC: 用 ABAC 擴展 AWS 安全性

> 來源：[AWS in Plain English - Niraj Kumar](https://aws.plainenglish.io/beyond-rbac-scaling-aws-security-with-attribute-based-access-control-abac-10f6ae08e0c7)
> 發布日期：2026-02-23
> 整理日期：2026-03-16

---

## 核心問題：Role Explosion（角色爆炸）

- 組織成長後，RBAC 會從 3 個角色膨脹到 500+ 個角色
- 每個新專案、微服務、團隊都需要略不同的權限邊界
- 每次新增 S3 bucket 或人員調動，IAM 管理員都要手動更新 JSON policy 中的 ARN
- **RBAC 的複雜度與組織規模成線性增長**，造成運維瓶頸和人為錯誤風險

---

## RBAC vs ABAC 對比

| 面向 | RBAC | ABAC |
|------|------|------|
| **授權邏輯** | 「這個使用者有什麼角色？」 | 「使用者的 tag 是否匹配資源的 tag？」 |
| **Resource 指定方式** | 明確列出每個 ARN | `Resource: "*"` + Condition 動態比對 |
| **新資源加入時** | 需手動更新 policy 加入新 ARN | 只要 tag 正確，自動獲得存取權 |
| **擴展性** | 線性增長（N 團隊 × M 專案 = N×M 角色） | 寫一次 policy，tag 做剩下的事 |
| **維運負擔** | 每次變更都需 IT ticket | 零手動 IAM policy 更新 |

### RBAC 的痛點範例

開發者加入 Project X → 建立 `DatabaseAdmin-ProjectX` 角色 → policy 明確列出 DB ARN → 團隊新增 `projectx-db-2` → **Access Denied** → 開 IT ticket → 等管理員更新 policy → 才能繼續工作

### ABAC 的解法

開發者 tag: `Project = X` → 通用角色 `DatabaseAdmin` → policy 比對 `aws:ResourceTag/Project == aws:PrincipalTag/Project` → 新 DB 只要 tag `Project = X` → **自動獲得存取權**

---

## ABAC 在 AWS 的運作機制

### 兩個關鍵 IAM Condition Key

| Key | 說明 |
|-----|------|
| `aws:PrincipalTag` | 附在**身分**（user/role）上的 tag |
| `aws:ResourceTag` | 附在**資源**（EC2/S3/RDS）上的 tag |

### 核心 Policy 範例

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowProjectDatabaseAccess",
      "Effect": "Allow",
      "Action": [
        "rds:StartDBInstance",
        "rds:StopDBInstance",
        "rds:RebootDBInstance"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "aws:ResourceTag/Project": "${aws:PrincipalTag/Project}"
        }
      }
    }
  ]
}
```

**關鍵設計：**
- `Resource: "*"` 看起來危險，但 **Condition 是動態安全網**
- `StringEquals` 確保只有 tag 匹配時才允許操作

### Implicit Deny 安全機制

- 使用者 `Project=Alpha` 嘗試存取 `Project=Beta` 的 DB → 條件不符 → **Implicit Deny**
- 資源沒有 `Project` tag → 無法匹配 → **Implicit Deny**
- 架構**預設失敗為關閉（fail closed）**，即使基礎設施擴展也能維持安全邊界

### RBAC vs ABAC：Resource 使用方式的根本差異（重大痛點）

這是 ABAC 相比 RBAC 最巧妙的地方，也經常被誤解：

**RBAC 中的 `Resource: "*"` — 死亡之吻**
```json
{
  "Effect": "Allow",
  "Action": "rds:StartDBInstance",
  "Resource": "*"  // ❌ 嚴重安全漏洞！使用者可以操作所有 DB
}
```
- 這在 RBAC 中絕對禁止，會造成全局權限擴散
- 任何有這個 policy 的使用者都能操作**整個帳戶的所有資源**

**ABAC 中的 `Resource: "*"` — 優雅且安全的設計**
```json
{
  "Effect": "Allow",
  "Action": "rds:StartDBInstance",
  "Resource": "*",
  "Condition": {
    "StringEquals": {
      "aws:ResourceTag/Project": "${aws:PrincipalTag/Project}"
    }
  }
}
```
- `Resource: "*"` 搭配 Condition 組合，使用者**看似**能操作所有資源
- 但 Condition 在**評估時刻（runtime）動態檢查**，條件不符直接 Implicit Deny
- 等同於寫了「允許存取所有資源，但條件是 tag 必須匹配」
- **安全邊界完全靠 tag 治理維持**（不靠 ARN hardcode）

**為什麼 ABAC 能這樣設計而 RBAC 不行？**

| 差異點 | RBAC | ABAC |
|------|------|------|
| 權限來源 | 靜態列表（ARN） | 動態比對（tag） |
| 新資源加入 | 需更新 Resource 列表 | 自動生效（只要 tag 對） |
| 人為錯誤風險 | 高（遺漏 ARN） | 低（tag 治理失敗） |
| 評估速度 | 快（字符串匹配） | 稍慢（條件評估） |

---

## 端到端架構：從 IdP 帶入 Tag

### Session Tags（會話標籤）

**問題：** 如果直接在 AWS 中硬編碼 tag 到個別 IAM user/role，就回到了手動管理的老路

**解法：** 從企業 Identity Provider（Entra ID / Okta）動態帶入 tag

### 架構流程

```
1. IdP（如 Entra ID）中設定使用者屬性：
   Alice → Department: Engineering, Project: Alpha

2. AWS IAM Identity Center 設定 Access Control Attributes：
   將 SAML/OIDC claim 映射到 AWS Session Tags

3. Alice 登入 AWS access portal：
   Entra ID 發送 token（含 Project=Alpha claim）
   → AWS 讀取 claim
   → 假設通用 Developer 角色
   → 注入 aws:PrincipalTag/Project = Alpha 到 session

4. Alice 操作資源時，ABAC policy 自動比對 tag
```

### Zero-Touch Provisioning 效果

- Alice 明年轉組 → HR 在 Entra ID 更新她的 Project 屬性 → 下次登入 AWS 權限自動更新
- **零手動 AWS policy 更新**

---

## Tag Governance（標籤治理）— 成功的前提

> **ABAC 完全依賴準確且安全的 tagging。如果 tag 混亂，安全性就混亂。**

### 權限升級風險

在 ABAC 架構中，**tag 修改等同於 IAM policy 修改**

範例：
- 開發者 session tag: `Project = Alpha`
- 想存取敏感 DB（tag: `Project = Secure`）
- 如果有 `rds:AddTagsToResource` 權限 → 改 DB tag 為 `Project = Alpha` → **繞過安全邊界**

### 防禦層 1：SCP 強制建立時打 Tag

用 **Service Control Policies (SCPs)** 在 AWS Organizations 層級：
- **Deny** 任何未包含必要 tag（如 `Project`、`Environment`）的資源建立請求
- 確保所有新基礎設施一出生就在 ABAC 治理範圍內

### 防禦層 2：鎖定 Tag 修改權限

以下 action 必須視同 `iam:AttachRolePolicy` 同等級別管控：
- `ec2:CreateTags` / `ec2:DeleteTags`
- `s3:PutBucketTagging`

**最佳實踐：**
- 人類使用者**幾乎不應有**修改 tag 的權限
- Tag 管理專屬交給 **IaC pipeline**（Terraform / CloudFormation）
- 透過 CI/CD deployment role 處理，確保 tag 是版控的、可稽核的、防竄改的

---

## 何時用 RBAC vs ABAC

| 情境 | 建議 |
|------|------|
| 小型環境、少量團隊和角色 | **RBAC** — 設定快、overhead 低 |
| Break-glass 緊急管理員角色 | **RBAC** — 需要明確靜態權限，不依賴可能錯誤的 tag |
| 不支援 tagging 的 legacy 資源 | **RBAC** — ABAC 無法實作 |
| 快速擴展的多租戶環境 | **ABAC** — 大幅減少運維負擔 |
| 工程師每週花數小時更新 IAM policy | **ABAC** — 巨大的運維效率提升 |
| 已有成熟 IaC pipeline（Terraform/CDK） | **ABAC** — 基礎已建好，只需開啟 |

---

## 實作建議

1. **不要一次全換** — 從單一、tag 完善的服務開始（如 Secrets Manager 或 EC2）
2. **先證明價值** — 用 IdP tag 實現動態存取，優化 SCP 的 tag governance
3. **觀察效果** — 看 IAM policy 管理工作量是否縮減
4. **逐步推廣** — 團隊體驗到 ABAC 的無摩擦存取後，再全面推廣

---

## 考試重點整理（SAP / SCS 適用）

- **aws:PrincipalTag** vs **aws:ResourceTag** 的區別和用法
- ABAC policy 中 `Resource: "*"` 搭配 `Condition` 的設計模式
- **Session Tags** 從 IdP 動態注入的架構
- **SCP 強制 tagging** 作為 ABAC 的前提條件
- Tag 修改權限 = IAM policy 修改權限（權限升級風險）
- RBAC 和 ABAC 的適用場景判斷
