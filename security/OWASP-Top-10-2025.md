# OWASP Top 10 - Web 應用安全風險指南

> 針對 DevOps / Cloud Engineer (AWS) 背景量身整理，每個漏洞類別都包含雲端基礎設施視角的解讀

## 什麼是 OWASP Top 10？

**OWASP** = Open Worldwide Application Security Project（開放式全球應用安全計畫）

OWASP Top 10 是業界公認的 **Web 應用最關鍵安全風險** 標準參考文件。不只是開發者要懂，**DevOps / SRE / Cloud Engineer** 在設計架構、部署管線、配置基礎設施時同樣必須理解。

| 項目 | 說明 |
|------|------|
| 更新頻率 | 每 3-4 年 |
| 最新版本 | **2025**（2025 年初發布） |
| 上一版本 | 2021 |
| 涵蓋 CWE 數量 | 248 個（2025 版） |

---

## 2021 → 2025 版本演進對照

| 2025 排名 | 2025 名稱 | 2021 排名 | 變化說明 |
|-----------|-----------|-----------|----------|
| A01 | Broken Access Control | A01 (2021) | 維持 #1，SSRF 併入此類 |
| A02 | Security Misconfiguration | A05 (2021) | **大幅上升**，反映雲端錯誤配置氾濫 |
| A03 | Software Supply Chain Failures | A06 (2021) | **全新擴展**，從「過時元件」升級為供應鏈安全 |
| A04 | Cryptographic Failures | A02 (2021) | 微降 |
| A05 | Injection | A03 (2021) | 持續下降，工具鏈進步有效緩解 |
| A06 | Insecure Design | A04 (2021) | 微降 |
| A07 | Authentication Failures | A07 (2021) | 維持 |
| A08 | Software or Data Integrity Failures | A08 (2021) | 維持 |
| A09 | Logging & Alerting Failures | A09 (2021) | 改名：Monitoring → **Alerting**，強調告警能力 |
| A10 | Mishandling of Exceptional Conditions | 新增 | **全新類別**，取代 SSRF（SSRF 併入 A01） |

**2025 版重點趨勢：**
- 從「症狀」轉向「根因」分析
- Security Misconfiguration 升至 #2 → **對 DevOps/Cloud 工程師是最大警訊**
- 供應鏈安全獨立成類 → CI/CD pipeline 安全成為焦點
- SSRF 不再獨立，併入 Broken Access Control

---

## 十大漏洞詳解

### A01: Broken Access Control（破損的存取控制）

**2025 排名 #1 | 2021 排名 #1 | 最嚴重的安全風險**

**白話解釋：** 系統沒有正確檢查「你是誰」和「你能做什麼」，讓使用者能存取或操作他們不該碰的東西。

**常見攻擊模式：**

| 攻擊手法 | 說明 | 範例 |
|----------|------|------|
| IDOR | 直接修改物件 ID 存取他人資料 | `/api/user/123` → `/api/user/456` |
| 權限提升 | 普通用戶執行管理員操作 | 普通帳號呼叫 `/admin/delete-user` |
| SSRF（2025 併入） | 利用伺服器發起內部請求 | 存取 `http://169.254.169.254/` 取得 AWS metadata |
| 功能級繞過 | 前端隱藏的功能後端未驗證 | 直接 POST 到隱藏的 API endpoint |

**真實案例：**
- **Facebook 資料外洩（2021）**：API 未限制存取控制，5.33 億用戶資料被大規模爬取
- **Capital One 事件（2019）**：WAF 設定錯誤 + SSRF → 攻擊者存取 AWS metadata → 取得 IAM 臨時憑證 → 存取 S3 bucket 中 1 億筆客戶資料

**DevOps / Cloud 視角 — 你的工作場景中怎麼出現？**

```
你做 AWS 上雲 PoC 時的風險點：

1. IAM Policy 太寬鬆
   ❌ "Effect": "Allow", "Action": "*", "Resource": "*"
   ✅ 最小權限原則，每個 Lambda/EC2 只給需要的權限

2. S3 Bucket Policy 公開
   ❌ "Principal": "*"（公開存取）
   ✅ 限定特定 IAM Role 或 VPC Endpoint

3. API Gateway 缺少授權
   ❌ API endpoint 沒有設定 Authorizer
   ✅ 使用 Cognito / Lambda Authorizer / IAM Auth

4. EC2 metadata SSRF（Capital One 同類）
   ❌ 使用 IMDSv1（HTTP GET 即可取得）
   ✅ 強制 IMDSv2（需要 PUT token 才能存取）
```

**AWS 具體防禦：**
- IAM Access Analyzer：自動分析過寬權限
- AWS Config Rules：持續檢查資源配置合規性
- VPC Endpoint Policy：限制 S3/DynamoDB 的存取來源
- IMDSv2：防止 SSRF 竊取 EC2 metadata

---

### A02: Security Misconfiguration（安全配置錯誤）

**2025 排名 #2（從 2021 #5 大幅上升）| 對 DevOps 最重要的類別**

**白話解釋：** 系統、服務、雲端資源使用了不安全的預設配置，或者管理員忘記關掉不該開的東西。

**為什麼 2025 年升到 #2？** 因為雲端基礎設施爆炸性成長，IaC 部署速度快，配置錯誤成為最常見的攻擊入口。

**常見錯誤配置：**

| 層級 | 錯誤範例 | 後果 |
|------|---------|------|
| OS 層 | RHEL 預設開啟不需要的服務 | 攻擊面增大 |
| 網路層 | Security Group 0.0.0.0/0 開放 SSH | 暴力破解風險 |
| 應用層 | Debug mode 在 production 開啟 | 洩漏 stack trace、環境變數 |
| 雲端層 | S3 bucket public access 未關閉 | 資料外洩 |
| 容器層 | Docker container 用 root 運行 | 容器逃逸風險 |
| IaC 層 | Terraform 未設定 encryption at rest | 資料未加密 |

**真實案例：**
- **Uber S3 外洩（2017）**：GitHub 上意外暴露 AWS 憑證 → 存取未加密的 S3 bucket → 5700 萬用戶資料外洩
- **Tesla Kubernetes Dashboard（2018）**：K8s dashboard 無密碼保護 → 攻擊者進入後用 Tesla 的 AWS 資源挖礦

**DevOps / Cloud 視角 — 你的日常工作中最常踩的坑：**

```
RHEL 系統升級專案中的配置風險：

1. 升級後 firewalld 規則重置
   ❌ 升級 RHEL 7→8→9 後未驗證 firewall rules
   ✅ Post-upgrade checklist 包含 firewalld 驗證

2. SELinux 被設成 Permissive 或 Disabled
   ❌ 為了「方便」關掉 SELinux
   ✅ 保持 Enforcing，用 audit2allow 處理 policy

3. SSH 配置
   ❌ PermitRootLogin yes, PasswordAuthentication yes
   ✅ PermitRootLogin no, 只允許 key-based auth

Terraform IaC 中的配置風險：

4. Security Group 過寬
   ❌ ingress { from_port=0, to_port=65535, cidr_blocks=["0.0.0.0/0"] }
   ✅ 只開放需要的 port，限制來源 IP

5. RDS 公開存取
   ❌ publicly_accessible = true
   ✅ publicly_accessible = false，透過 VPC 內部存取

6. 未啟用加密
   ❌ 忘記設定 storage_encrypted = true
   ✅ 所有 RDS、EBS、S3 預設加密
```

**AWS 具體防禦：**
- AWS Config：持續監控配置偏移
- AWS Security Hub：統一安全態勢管理
- tfsec / checkov：Terraform 靜態安全掃描
- AWS Trusted Advisor：自動建議安全改善

---

### A03: Software Supply Chain Failures（軟體供應鏈失敗）

**2025 排名 #3（全新擴展）| 從 2021 的「過時元件」升級為完整供應鏈安全**

**白話解釋：** 你的應用依賴的第三方套件、CI/CD 工具鏈、或建構流程本身被污染或有漏洞。

**為什麼獨立成類？** 近年供應鏈攻擊爆炸性成長，攻擊者不直接攻擊你，而是攻擊你信任的上游。

**攻擊面：**

```
供應鏈攻擊的三個層面：

1. 依賴層 — 惡意或有漏洞的套件
   └─ npm/pip/gem 套件被植入後門
   └─ 已知 CVE 的舊版本未更新

2. 建構層 — CI/CD pipeline 被入侵
   └─ GitHub Actions workflow 被篡改
   └─ 建構伺服器被攻破

3. 分發層 — 更新機制被劫持
   └─ 軟體更新伺服器被攻陷
   └─ 缺少簽名驗證
```

**真實案例：**
- **SolarWinds Orion（2020）**：建構系統被入侵 → 在合法更新中植入後門 → 影響 18,000+ 組織（包括美國政府）
- **XZ Utils 後門（2024）**：維護者帳號被社交工程攻陷 → 在壓縮工具中植入後門 → 差點影響所有 Linux 發行版
- **Log4Shell（2021）**：Log4j 零日漏洞 → 幾乎所有 Java 應用受影響 → 史上影響範圍最大的漏洞之一
- **Codecov Bash Uploader（2021）**：CI 工具的腳本被篡改 → 竊取用戶的環境變數和密鑰

**DevOps / Cloud 視角 — 你的 CI/CD 和基礎設施：**

```
GitHub Actions 風險：
❌ 使用 third-party action 不鎖版本
   uses: some-action@main  # 可能被惡意更新
✅ 鎖定 commit hash
   uses: some-action@abc123def456

Docker Image 風險：
❌ FROM python:latest  # 可能引入已知漏洞
✅ FROM python:3.12-slim@sha256:abc123...  # 鎖定 digest

Terraform Provider 風險：
❌ 不鎖版本的 provider
✅ required_providers { aws = { version = "~> 5.0" } }

RHEL 套件風險：
❌ yum install 未驗證 GPG 簽名
✅ 使用 Red Hat 官方 repo + GPG key 驗證
```

**防禦工具鏈：**
- Dependabot / Renovate：自動更新依賴 + 漏洞通知
- Trivy / Grype：容器映像漏洞掃描
- SBOM（Software Bill of Materials）：軟體物料清單
- AWS ECR Image Scanning：容器映像掃描
- Sigstore / cosign：容器映像簽名驗證

---

### A04: Cryptographic Failures（加密失敗）

**2025 排名 #4 | 2021 排名 #2**

**白話解釋：** 敏感資料在傳輸或儲存時沒有被正確加密保護，或者使用了已被破解的加密方式。

**常見錯誤：**

| 層面 | 錯誤 | 正確做法 |
|------|------|---------|
| 傳輸中 | HTTP 明文傳輸敏感資料 | 強制 HTTPS (TLS 1.2+) |
| 儲存中 | 密碼明文存資料庫 | bcrypt / Argon2 雜湊 |
| 金鑰管理 | 硬編碼 API Key 在程式碼中 | 使用 Secrets Manager |
| 演算法 | MD5 / SHA-1 | SHA-256+ / AES-256 |
| 憑證 | 自簽憑證用在 production | ACM 免費託管憑證 |

**真實案例：**
- **Equifax（2017）**：未修補 Apache Struts 漏洞 + 敏感資料未加密 → 1.47 億人個資外洩
- **Adobe（2013）**：3800 萬用戶密碼用 3DES ECB 模式加密（可逆且有 pattern）→ 輕易破解

**DevOps / Cloud 視角：**

```
你的 AWS 架構中的加密要點：

傳輸中加密 (Encryption in Transit):
├─ ALB/CloudFront → ACM 免費 TLS 憑證
├─ API Gateway → 強制 HTTPS
└─ RDS 連線 → require_ssl = true

靜態加密 (Encryption at Rest):
├─ S3 → SSE-S3 / SSE-KMS
├─ RDS → storage_encrypted = true
├─ EBS → encrypted = true
└─ DynamoDB → 預設 AWS managed key

金鑰管理:
├─ AWS KMS → 集中管理加密金鑰
├─ AWS Secrets Manager → API key, DB password
├─ Parameter Store → 非敏感配置
└─ 絕對不要把 secret 放在 Terraform state 明文中
    → 使用 S3 backend + encryption + DynamoDB lock
```

---

### A05: Injection（注入攻擊）

**2025 排名 #5 | 2021 排名 #3 | 持續下降但仍然危險**

**白話解釋：** 攻擊者在輸入中夾帶惡意指令，系統把它當成合法指令執行。

**主要類型及範例：**

#### SQL Injection
```sql
-- 用戶輸入: ' OR '1'='1' --
-- 原始查詢: SELECT * FROM users WHERE name = '{input}'
-- 變成:     SELECT * FROM users WHERE name = '' OR '1'='1' --'
-- 結果: 繞過驗證，返回所有用戶
```

#### Command Injection（OS 指令注入）
```bash
# 應用功能: ping 使用者指定的 host
# 用戶輸入: google.com; cat /etc/passwd
# 實際執行: ping google.com; cat /etc/passwd
# 結果: 執行了任意系統指令
```

#### Template Injection（模板注入）
```python
# Jinja2 SSTI
# 用戶輸入: {{7*7}}
# 如果直接渲染，輸出 49 → 確認可注入
# 進階: {{config.items()}} → 洩漏應用配置
```

**防禦要點：**
```python
# ❌ 字串拼接 SQL（絕對不要）
query = f"SELECT * FROM users WHERE id = {user_id}"

# ✅ 參數化查詢
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))

# ✅ ORM（更好）
user = User.objects.get(id=user_id)
```

**DevOps 視角：**
- Shell script 中使用 `eval` 或不加引號的變數展開是 command injection 溫床
- Terraform `local-exec` provisioner 如果用了未驗證的輸入也會有風險
- AWS Lambda 執行外部 command 時同樣要注意
- AWS WAF + Cloud Armor 可在網路層攔截常見注入 pattern

---

### A06: Insecure Design（不安全的設計）

**2025 排名 #6 | 2021 排名 #4**

**白話解釋：** 問題不在「實作寫錯」，而在「設計就沒考慮安全」。再完美的程式碼也修不了設計層面的缺陷。

**設計 vs 實作的差別：**

```
Insecure Design（設計問題）:
  "密碼重設只需要生日" → 設計就是不安全的

Implementation Bug（實作問題）:
  "密碼重設的 token 沒有過期時間" → 實作有 bug

前者需要重新設計架構，後者修幾行 code 就好
```

**常見設計缺陷：**
- 沒有做 Threat Modeling（威脅建模）
- 無 rate limiting 的登入/API
- 沒有考慮 abuse case（濫用情境）
- 過度信任 client 端的資料

**DevOps / Cloud 視角 — 架構設計時要考慮的：**

```
你做 AWS 架構設計時的安全設計原則：

1. 網路隔離
   ✅ Public / Private / Isolated subnet 分層
   ✅ NAT Gateway 讓 private subnet 出去
   ✅ VPC Endpoint 避免流量走 internet

2. 最小權限
   ✅ 每個 Lambda/EC2 獨立的 IAM Role
   ✅ 細粒度 Policy（指定 Resource ARN）

3. Defense in Depth（縱深防禦）
   ✅ Security Group + NACL + WAF 多層防禦
   ✅ 不只靠一層做安全

4. Fail Secure
   ✅ 系統故障時進入安全狀態，而非開放狀態
   ✅ 預設 deny all，明確 allow 需要的
```

---

### A07: Authentication Failures（身份驗證失敗）

**2025 排名 #7 | 2021 排名 #7**

**白話解釋：** 登入機制有缺陷，讓攻擊者能冒充合法使用者。

**常見漏洞：**
- 允許弱密碼（`123456`, `password`）
- 無 MFA（多因素認證）
- Session ID 可預測
- 暴力破解無防護（無 rate limit、無 lockout）
- 密碼重設流程不安全

**DevOps / Cloud 視角：**

```
AWS 環境的身份驗證安全：

IAM 層面：
├─ Root Account → 啟用 MFA + 極少使用
├─ IAM User → 啟用 MFA + 強密碼政策
├─ Access Key → 定期輪換（90 天）
├─ Assume Role → 跨帳號用 STS，不要長期憑證
└─ SSO → 使用 AWS IAM Identity Center 集中管理

Linux 系統層面（你的 RHEL 經驗）：
├─ SSH Key-based auth only（禁用密碼登入）
├─ fail2ban → 防暴力破解
├─ PAM 模組 → 密碼複雜度要求
└─ sudo → 細粒度授權，不用 NOPASSWD

應用層面：
├─ Cognito / Auth0 → 不要自己造輪子
├─ JWT → 設定合理過期時間
└─ OAuth 2.0 + PKCE → 現代授權流程
```

---

### A08: Software or Data Integrity Failures（軟體或資料完整性失敗）

**2025 排名 #8 | 2021 排名 #8**

**白話解釋：** 程式碼或資料在傳遞過程中被竄改，但系統沒有能力偵測到。

**與 A03（供應鏈）的區別：**
- A03 關注「你用的東西本身有問題」（惡意套件、CVE）
- A08 關注「傳遞過程中被竄改」（更新被劫持、CI/CD 被入侵）

**常見場景：**
- 應用自動更新沒有驗證簽名
- CI/CD pipeline 沒有保護建構產物
- Deserialization 攻擊（反序列化）
- CDN 上的 JavaScript 被竄改但沒有 SRI 驗證

**DevOps / Cloud 視角：**

```
CI/CD Pipeline 安全：
├─ GitHub Actions
│   ├─ ✅ 用 OIDC 取代 long-lived AWS credentials
│   ├─ ✅ 限制 workflow permissions (最小權限)
│   └─ ✅ Branch protection rules + required reviews
├─ 建構產物
│   ├─ ✅ Docker image 簽名 (cosign)
│   ├─ ✅ Terraform plan 產出需要人工 approve
│   └─ ✅ 建構環境隔離（不共用 runner）
└─ 部署
    ├─ ✅ 不可變基礎設施（immutable infrastructure）
    ├─ ✅ 藍綠部署 / Canary 部署
    └─ ✅ 部署後自動化驗證
```

---

### A09: Logging & Alerting Failures（日誌和告警失敗）

**2025 排名 #9 | 2021 排名 #9 | 改名：Monitoring → Alerting**

**白話解釋：** 被攻擊了卻不知道，或者知道了卻沒人處理。業界平均發現入侵的時間是 **200 天**。

**改名的意義：** 光有「監控」不夠，需要有效的「告警」才能觸發行動。

**該記錄什麼：**
```
必須記錄的事件（Audit Log）：
├─ 身份驗證：登入成功/失敗、密碼重設
├─ 授權：權限變更、存取被拒
├─ 資料操作：CRUD 敏感資料
├─ 系統：配置變更、服務啟停
└─ 安全：WAF 告警、異常流量

不該記錄的：
├─ 密碼明文
├─ Session token
├─ 信用卡號
└─ 個人敏感資料
```

**DevOps / Cloud 視角 — 這是你最日常的工作：**

```
AWS 日誌和監控生態系：

收集：
├─ CloudTrail → AWS API 操作記錄（誰在什麼時候做了什麼）
├─ VPC Flow Logs → 網路流量記錄
├─ CloudWatch Logs → 應用/系統日誌
├─ S3 Access Logs → Bucket 存取記錄
├─ ALB/API Gateway Logs → 請求記錄
└─ Config → 資源配置變更記錄

集中管理：
├─ CloudWatch Log Groups → 集中查詢
├─ S3 + Athena → 大量日誌分析
└─ OpenSearch → 全文搜索 (ELK 替代方案)

告警：
├─ CloudWatch Alarms → 指標告警
├─ EventBridge → 事件驅動告警
├─ SNS → 通知分發（Email/Slack/PagerDuty）
└─ GuardDuty → 智慧威脅偵測

RHEL 系統層面：
├─ journald / rsyslog → 系統日誌
├─ auditd → 安全審計日誌
└─ 集中到 CloudWatch Agent 統一管理
```

---

### A10: Mishandling of Exceptional Conditions（異常條件處理不當）

**2025 排名 #10 | 全新類別（取代 SSRF，SSRF 併入 A01）**

**白話解釋：** 系統遇到錯誤或異常時處理不當，可能洩漏敏感資訊、進入不安全狀態、或直接崩潰。

**常見問題：**

| 問題 | 範例 | 風險 |
|------|------|------|
| Fail Open | 驗證服務故障時跳過驗證 | 未授權存取 |
| 資訊洩漏 | 錯誤訊息包含 stack trace | 洩漏內部架構 |
| 資源耗盡 | 未處理的異常導致 memory leak | DoS |
| 不一致狀態 | 交易中途失敗未 rollback | 資料損壞 |

**DevOps / Cloud 視角：**

```
基礎設施層面的異常處理：

1. Terraform apply 失敗
   ❌ 半套資源建立了，網路不通
   ✅ 使用 lifecycle rules + depends_on 確保順序
   ✅ 失敗時有回滾策略

2. 健康檢查和自動復原
   ✅ ALB health check → 自動移除故障 target
   ✅ ASG → 自動替換不健康的 instance
   ✅ Route 53 failover → DNS 層面容災

3. 錯誤頁面
   ❌ 500 error 顯示完整 stack trace 和 DB 連線字串
   ✅ 返回通用錯誤訊息，detail 只進日誌

4. Circuit Breaker Pattern
   ✅ 下游服務故障時快速失敗（而非卡住）
   ✅ API Gateway 設定 timeout 和 throttling
```

---

## 對你最重要的 Top 5（DevOps/Cloud Engineer 視角排序）

根據你的背景（AWS 架構、RHEL 維運、Terraform IaC、CI/CD），重新排序：

| 優先級 | 類別 | 原因 |
|--------|------|------|
| 1 | **A02 Security Misconfiguration** | 你每天都在配置 AWS 資源、RHEL 系統、Terraform — 這是你最可能犯錯的地方 |
| 2 | **A01 Broken Access Control** | IAM Policy、S3 Bucket Policy、Security Group — 存取控制是雲端安全的核心 |
| 3 | **A03 Supply Chain Failures** | CI/CD pipeline、Docker image、Terraform provider — 供應鏈安全直接影響你的部署管線 |
| 4 | **A09 Logging & Alerting** | CloudTrail、CloudWatch、GuardDuty — 沒有可觀測性就等於瞎飛 |
| 5 | **A04 Cryptographic Failures** | KMS、ACM、加密配置 — 資料保護是合規的基礎 |

---

## 防禦工具速查表

### 靜態分析（Shift Left — 部署前就抓到問題）

| 工具 | 用途 | 整合方式 |
|------|------|---------|
| tfsec / checkov | Terraform 安全掃描 | CI/CD pipeline |
| trivy | 容器映像 + IaC 漏洞掃描 | CI/CD + Registry |
| Dependabot | 依賴漏洞通知 + 自動 PR | GitHub native |
| OWASP ZAP | Web 應用動態掃描 | CI/CD pipeline |
| Bandit | Python 靜態安全分析 | CI/CD pipeline |
| hadolint | Dockerfile lint | CI/CD pipeline |

### 運行時防護（Runtime — 部署後持續監控）

| AWS 服務 | 對應 OWASP 類別 | 用途 |
|----------|----------------|------|
| GuardDuty | A01, A07 | 智慧威脅偵測 |
| Security Hub | 全部 | 統一安全態勢 |
| Config | A02, A05 | 配置合規監控 |
| CloudTrail | A09 | API 活動審計 |
| WAF | A01, A05 | Web 應用防火牆 |
| Inspector | A03, A06 | EC2/Lambda 漏洞掃描 |
| IAM Access Analyzer | A01 | 過寬權限分析 |
| Secrets Manager | A04 | 密鑰集中管理 |
| KMS | A04 | 加密金鑰管理 |

---

## 安全開發生命週期（DevSecOps 視角）

```
   設計階段              開發階段              部署階段              運維階段
┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│ 威脅建模     │   │ 靜態掃描     │   │ IaC 安全掃描 │   │ 持續監控     │
│ 安全需求     │──→│ 依賴掃描     │──→│ 容器掃描     │──→│ 日誌分析     │
│ 架構審查     │   │ Code Review  │   │ 配置驗證     │   │ 告警回應     │
│ (A04, A06)  │   │ (A03, A05)  │   │ (A02)       │   │ (A09)       │
└─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘
                                                              │
                                    ┌───────────────────────────┘
                                    ▼
                            持續改進 & 回饋
                            ├─ 滲透測試結果
                            ├─ 事件事後分析
                            └─ 更新 Runbook
```

---

## 實踐檢查清單（DevOps / Cloud Engineer 版）

### 每次部署前
- [ ] Terraform plan 有經過安全掃描（tfsec/checkov）
- [ ] Docker image 有經過漏洞掃描（trivy）
- [ ] 依賴有更新到安全版本
- [ ] IAM Policy 遵守最小權限原則
- [ ] Security Group 只開放必要 port
- [ ] 敏感資料使用 Secrets Manager，不在程式碼中

### 架構設計時
- [ ] 網路隔離（Public/Private/Isolated subnet）
- [ ] 加密：傳輸中（TLS）+ 靜態（KMS）
- [ ] 存取控制：IAM + Resource Policy + VPC Endpoint
- [ ] 日誌：CloudTrail + VPC Flow Logs + 應用日誌
- [ ] 告警：GuardDuty + CloudWatch Alarms + SNS

### 系統維運時
- [ ] 定期修補（yum update --security）
- [ ] SSH key rotation
- [ ] IAM Access Key rotation（90 天）
- [ ] 安全掃描報告 review
- [ ] 定期檢查 Security Hub findings

---

## 進一步學習資源

### 官方文件
- [OWASP Top 10:2025 官方](https://owasp.org/Top10/2025/)
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
- [AWS Security Best Practices](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/)
- [GCP OWASP Top 10 Mitigation](https://docs.cloud.google.com/architecture/security/owasp-top-ten-mitigation)

### 實作練習
- [OWASP WebGoat](https://owasp.org/www-project-webgoat/) — 互動式漏洞學習
- [TryHackMe OWASP Top 10](https://tryhackme.com/) — 引導式安全挑戰
- [flaws.cloud](http://flaws.cloud/) — AWS 安全實戰挑戰（超推薦）
- [CloudGoat](https://github.com/RhinoSecurityLabs/cloudgoat) — AWS 安全靶場

### 相關認證路徑
- **AWS Security Specialty (SCS)** — 你下一張目標認證，直接涵蓋 OWASP 雲端面向
- **CompTIA Security+** — 安全基礎廣度
- **CEH / OSCP** — 深入滲透測試

---

**Sources:**
- [OWASP Top 10:2025 Official](https://owasp.org/Top10/2025/)
- [OWASP Top 10:2021 Official](https://owasp.org/Top10/2021/)
- [GCP OWASP Top 10 Mitigation Guide](https://docs.cloud.google.com/architecture/security/owasp-top-ten-mitigation)
- [OWASP Top 10 2025: Key Changes - Aikido](https://www.aikido.dev/blog/owasp-top-10-2025-changes-for-developers)
- [OWASP Top 10 2025 vs 2021 - Equixly](https://equixly.com/blog/2025/12/01/owasp-top-10-2025-vs-2021/)
- [Orca Security - OWASP Top 10](https://orca.security/glossary/owasp-top-10-list/)

**最後更新**: 2026-03-30
