# AWS 資安三劍客：GuardDuty vs Inspector vs Macie

> **萃取來源**: AWS SAA 考題實戰分析
> **核心場景**: EC2 被入侵後散播惡意軟體的偵測與防護
> **最後更新**: 2026-03-04

---

## 📌 Domain Insights 提煉

### 核心問題場景
**情境描述**：
- 你的應用程式存在漏洞（SQL Injection / RCE）
- 駭客透過漏洞入侵 EC2 instance
- EC2 被當作「跳板（Botnet）」散播惡意軟體
- AWS 發出濫用警告信（Abuse Report）

**業務需求**：
- 即時監控惡意網路行為
- 最低維運成本（LEAST operational effort）
- 能偵測「已被入侵後的異常流量」

---

## 🎯 AWS 資安服務定位矩陣

| 服務 | 核心定位 | 主要功能 | 監控對象 | 使用時機 |
|------|---------|---------|---------|---------|
| **GuardDuty** | 🕵️ 抓現行犯 | Threat Detection | VPC Flow Logs<br>DNS Logs<br>CloudTrail | 偵測異常連線<br>惡意 IP 通訊<br>帳號異常行為 |
| **Inspector** | 🏥 做體檢 | Vulnerability Management | EC2/Container<br>軟體版本 | 掃描 CVE 漏洞<br>網路開放檢查 |
| **Macie** | 🔍 找機密 | Data Privacy | S3 Objects | 敏感個資偵測<br>PII/PCI 合規 |

---

## 🔬 技術深度解析

### 1️⃣ Amazon GuardDuty

#### 工作原理
```
┌─────────────────────────────────────────┐
│  GuardDuty (全自動威脅偵測引擎)           │
├─────────────────────────────────────────┤
│  自動分析數據源:                         │
│  ├── VPC Flow Logs (網路流量)            │
│  ├── DNS Query Logs (DNS 查詢記錄)       │
│  ├── CloudTrail (API 呼叫記錄)           │
│  └── S3 Data Events                     │
└─────────────────────────────────────────┘
           ↓
    威脅情報資料庫比對
    (已知惡意 IP/Domain)
           ↓
    ┌─────────────────┐
    │  發出 Findings   │
    │  (威脅警報)      │
    └─────────────────┘
```

#### 典型偵測場景（Findings 範例）

**1. Backdoor:EC2/C&CActivity.B!DNS**
```yaml
威脅描述: EC2 正在連線至已知的 C&C (Command & Control) 伺服器
嚴重程度: High
業務影響: Instance 可能已被植入後門，正在接收駭客指令
建議處置:
  - 立即隔離 Instance (修改 Security Group)
  - 取得記憶體快照 (Memory Dump) 進行鑑識
  - 從乾淨的 AMI 重建
```

**2. UnauthorizedAccess:EC2/MaliciousIPCaller.Custom**
```yaml
威脅描述: EC2 正在對外連線至惡意 IP (散播惡意軟體)
嚴重程度: Medium
業務影響: 可能違反 AWS Abuse Policy，面臨帳號暫停風險
建議處置:
  - 檢查 VPC Flow Logs 確認流量模式
  - 封鎖目的地 IP (NACL Deny Rule)
  - 檢查應用程式漏洞
```

**3. CryptoCurrency:EC2/BitcoinTool.B!DNS**
```yaml
威脅描述: EC2 正在執行挖礦程式
嚴重程度: High
業務影響:
  - 高額 EC2 運算成本
  - 資源被竊用影響正常服務
建議處置: 立即終止 Instance 並調查帳號權限
```

#### 啟用方式與成本
```bash
# 啟用 GuardDuty (一鍵開啟，無需安裝 Agent)
aws guardduty create-detector --enable

# 成本結構
# - VPC Flow Logs: $1.13 / GB analyzed
# - CloudTrail: $4.80 / 1M events
# - DNS Logs: $0.40 / GB analyzed
# 💡 有 30 天免費試用
```

---

### 2️⃣ Amazon Inspector

#### 工作原理
```
┌────────────────────────────────────┐
│  Inspector (系統健檢掃描器)         │
├────────────────────────────────────┤
│  掃描目標:                          │
│  ├── EC2 Instances                 │
│  ├── ECR Container Images          │
│  └── Lambda Functions              │
└────────────────────────────────────┘
          ↓
    深度掃描 (需安裝 SSM Agent)
          ↓
┌────────────────────────────────────┐
│  檢測項目:                          │
│  ├── 軟體漏洞 (CVE 資料庫比對)       │
│  ├── 網路可達性 (Reachability)      │
│  └── CIS Benchmarks 合規性          │
└────────────────────────────────────┘
```

#### 適用場景
✅ **適合**：
- 定期安全體檢（每週/每月掃描）
- 合規稽核（PCI-DSS, HIPAA）
- 容器映像檔上線前檢查

❌ **不適合**：
- **即時威脅偵測**（這題的場景）
- 網路流量深度檢測（DPI）
- 執行階段惡意行為監控

#### 實際報告範例
```json
{
  "finding": {
    "title": "CVE-2021-44228 - Log4Shell",
    "severity": "CRITICAL",
    "description": "Apache Log4j2 遠端程式碼執行漏洞",
    "recommendation": "升級至 log4j-core 2.17.0",
    "affectedResources": [
      "i-0abcd1234efgh5678"
    ]
  }
}
```

---

### 3️⃣ Amazon Macie

#### 工作原理
```
┌──────────────────────────────────┐
│  Macie (S3 敏感資料守護者)        │
├──────────────────────────────────┤
│  使用 ML 與 Pattern Matching:    │
│  ├── 信用卡號 (PCI)               │
│  ├── 身分證字號                   │
│  ├── API Keys / Credentials      │
│  └── 個人健康資訊 (PHI)           │
└──────────────────────────────────┘
          ↓
    自動掃描 S3 Buckets
          ↓
    ┌──────────────────┐
    │  產生 Findings    │
    │  並評估風險等級   │
    └──────────────────┘
```

#### 典型應用
```python
# 場景: 開發團隊不小心將含有客戶資料的 CSV 上傳到 S3
# Macie 會自動發出警報

{
  "type": "SensitiveData:S3Object/Personal",
  "severity": "HIGH",
  "details": {
    "bucket": "my-app-logs",
    "key": "backup/customer_data.csv",
    "findings": [
      "10 個信用卡號",
      "523 個 Email 地址",
      "100 個電話號碼"
    ]
  }
}
```

---

## 🧠 考試技巧：快速判斷邏輯樹

```
資安題出現時，先問自己:

Q1: 要保護的是「資料」還是「系統」？
    ├─ 資料 (S3 個資外洩) → Macie
    └─ 系統 → Q2

Q2: 是「事前預防」還是「事中偵測」？
    ├─ 預防 (掃漏洞) → Inspector
    └─ 偵測 → Q3

Q3: 偵測的是「異常行為」還是「系統弱點」？
    ├─ 異常行為 (惡意連線/可疑 API) → GuardDuty ✅
    └─ 系統弱點 → Inspector
```

---

## 🚨 本題陷阱完整分析

### 題目關鍵字解構
| 原文 | 中文 | 技術含義 |
|------|------|---------|
| **compromised app** | 被入侵的應用 | 漏洞已被利用，系統已失守 |
| **spread malware** | 散播惡意軟體 | **出向流量異常**（關鍵） |
| **notification from AWS** | AWS 警告信 | Abuse Report（濫用通知） |
| **LEAST operational effort** | 最低維運成本 | 排除自建 IDS/IPS 方案 |

### 選項深度分析

#### ❌ 選項 B: GuardDuty + Decoy systems
**錯誤原因**：
- GuardDuty **不提供**誘餌系統（Honeypot）功能
- Decoy systems 需要額外部署（如 Thinkst Canary）
- 這是「混淆視聽」的干擾選項

**補充知識**：
```
真正的 Decoy/Honeypot 架構:
┌────────────────────────────────┐
│  Production VPC                │
│  ├── Real App Servers          │
│  └── Honeypot EC2 (誘餌)       │
│      └── 故意開放 SSH/RDP      │
└────────────────────────────────┘
         ↓
  任何連線到 Honeypot = 100% 惡意
         ↓
    觸發 Lambda 自動封鎖
```

#### ❌ 選項 C: Gateway Load Balancer + IDS
**看似合理，但違反題意**：

**技術可行性**: ✅ 可以做到
```
Internet
    ↓
Gateway Load Balancer (GWLB)
    ↓
Third-party IDS (Palo Alto / Check Point)
    ↓ (Deep Packet Inspection)
Protected VPC
```

**為何不選**：
1. **維運成本高**:
   - 需要採購 IDS 授權
   - 維護高可用性（Multi-AZ）
   - 持續更新威脅規則庫

2. **GuardDuty 已足夠**:
   - 相同目的（偵測惡意流量）
   - 零維運（全託管服務）
   - 成本更低

**適用場景**:
- 金融業需要符合特定合規要求
- 需要客製化 IDS 規則
- 已有既有 IDS 設備要上雲

#### ❌ 選項 D: Amazon Inspector (你的選擇)
**迷惑性最強的陷阱**！

**為何會選錯**：
- Inspector 確實掃描「漏洞」
- 題目提到「compromised app」（有漏洞）
- **但時間點錯誤** → 漏洞已被利用，馬後炮

**正確時間軸理解**：
```
T0: 應用存在 SQL Injection 漏洞
    → Inspector 在此階段有用 ✅

T1: 駭客利用漏洞入侵 EC2
    → Inspector 無法阻止（已發生）

T2: EC2 開始散播惡意軟體 ⚠️
    → 題目問的是「此階段」如何偵測
    → Inspector 不檢查網路流量 ❌
    → GuardDuty 分析 VPC Flow Logs ✅
```

**Inspector 的侷限性**：
```bash
# Inspector 能做的
✅ 掃描 CVE-2023-12345 漏洞
✅ 偵測 22/3389 port 對外開放
✅ 檢查 IMDSv1 是否啟用

# Inspector 不能做的
❌ 分析即時網路流量
❌ 偵測連線至惡意 IP
❌ 監控異常 DNS 查詢
❌ 偵測資料外洩 (Data Exfiltration)
```

#### ✅ 選項 A: Amazon GuardDuty (正確答案)

**完美符合需求**：
| 需求 | GuardDuty 如何滿足 |
|------|-------------------|
| 偵測惡意軟體散播 | 分析 VPC Flow Logs，比對已知惡意 IP |
| 最低維運成本 | 一鍵啟用，無需安裝 Agent |
| 即時警報 | 持續監控，發現威脅立即通知 |
| 成本效益 | 按使用量計費，有免費額度 |

**實戰部署範例**：
```bash
# Step 1: 啟用 GuardDuty
aws guardduty create-detector \
    --enable \
    --finding-publishing-frequency FIFTEEN_MINUTES

# Step 2: 設定自動回應 (進階)
# CloudWatch Events Rule
aws events put-rule \
    --name GuardDuty-AutoResponse \
    --event-pattern '{
      "source": ["aws.guardduty"],
      "detail-type": ["GuardDuty Finding"],
      "detail": {
        "severity": [7, 8, 9]
      }
    }'

# Step 3: 觸發 Lambda 自動隔離
# Lambda Function (偽代碼)
def lambda_handler(event):
    instance_id = event['detail']['resource']['instanceDetails']['instanceId']

    # 修改 Security Group 為隔離模式
    ec2.modify_instance_attribute(
        InstanceId=instance_id,
        Groups=['sg-quarantine-000000']
    )

    # 通知 Security Team
    sns.publish(
        Topic='SecurityIncidents',
        Message=f'Instance {instance_id} has been quarantined'
    )
```

---

## 💡 實戰記憶口訣

```
資安三劍客，各有專攻：
🕵️ GuardDuty 抓賊忙 → 威脅偵測
🏥 Inspector 健檢強 → 漏洞掃描
🔍 Macie 找個資藏 → 敏感資料
```

**場景速配表**：
- 「EC2 連到怪 IP」 → **GuardDuty**
- 「軟體沒更新」 → **Inspector**
- 「S3 有信用卡號」 → **Macie**

---

## 📚 延伸學習資源

### 官方文件
- [GuardDuty Findings Types](https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_finding-types-active.html)
- [Inspector Rules Packages](https://docs.aws.amazon.com/inspector/latest/user/inspector_rule-packages.html)
- [Macie Sensitive Data Discovery](https://docs.aws.amazon.com/macie/latest/user/discovery-jobs.html)

### 實戰練習建議
1. **GuardDuty**:
   - 啟用服務並產生測試 Findings（官方提供 PoC）
   - 設定 EventBridge Rule 整合 Slack 通知

2. **Inspector**:
   - 對測試 EC2 執行 Network Reachability 掃描
   - 匯出 CVE 報告並制定修補計畫

3. **Macie**:
   - 建立測試 S3 Bucket 上傳含個資檔案
   - 設定自動化分類（Sensitive / Public / Internal）

---

## ✅ 檢核清單

學完本文後，你應該能夠：
- [ ] 快速區分三個服務的核心定位
- [ ] 判斷「已被入侵」vs「預防入侵」的服務選擇
- [ ] 解釋為何 Inspector 不適合即時威脅偵測
- [ ] 說出至少 3 種 GuardDuty Findings 類型
- [ ] 設計基本的 GuardDuty 自動回應機制

---

**下一步學習路徑**：
→ 進階主題：[AWS Security Hub 整合三劍客](./AWS-Security-Hub整合實戰.md)
→ 實戰演練：[GuardDuty + Lambda 自動化事件回應](./GuardDuty-IR-Automation.md)

---

*本文件遵循 [tech-stack-learning 筆記規範](../../README.md)*
