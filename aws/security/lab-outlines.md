# AWS Security Specialty 實戰 Lab 建議大綱

## Lab 1: 威脅偵測與自動化響應 (Detection & Automated Response)
**目標：** 建立完整的威脅偵測和自動化響應系統

### 實作項目
1. **GuardDuty 設置與監控**
   - 啟用 GuardDuty（多區域）
   - 配置 S3/RDS/Lambda 保護
   - 建立測試用例觸發 findings（模擬攻擊場景）

2. **Security Hub 整合**
   - 啟用 Security Hub 並聚合多服務 findings
   - 配置 AWS Foundational Security Best Practices 標準
   - 自訂 insights 和儀表板

3. **自動化響應流程**
   - EventBridge 規則：監聽 GuardDuty findings
   - Lambda 函數：自動隔離受感染 EC2（修改 Security Group）
   - SNS 通知：告警發送到 Slack/Email
   - Systems Manager Automation：執行修復腳本

### 預期成果
- 偵測到可疑活動後 5 分鐘內自動隔離
- 完整的事件日誌和通知鏈路
- 可視化安全態勢儀表板

---

## Lab 2: 事件響應與取證分析 (Incident Response & Forensics)
**目標：** 模擬安全事件並進行完整的取證調查

### 實作項目
1. **事件準備階段**
   - 建立隔離的 VPC（forensics environment）
   - 配置 CloudTrail 跨區域日誌收集
   - 啟用 VPC Flow Logs 並送到 S3
   - S3 Object Lock 保護證據完整性

2. **模擬安全事件**
   - 建立 EC2 並故意暴露 SSH（0.0.0.0/0）
   - 使用工具模擬暴力破解攻擊
   - 觸發 GuardDuty findings

3. **事件調查與分析**
   - 使用 Detective 視覺化攻擊路徑
   - Athena 查詢 CloudTrail/VPC Flow Logs
   - CloudWatch Logs Insights 分析異常行為
   - 建立 EBS 快照進行離線分析

4. **證據保全**
   - EBS 快照加密並 tag 標記
   - CloudTrail digest 驗證日誌完整性
   - 輸出調查報告（PDF 格式）

### 預期成果
- 完整的事件時間軸重建
- 識別攻擊來源和影響範圍
- 可呈現給管理層的調查報告

---

## Lab 3: IAM 進階權限管理 (Advanced IAM & Access Control)
**目標：** 實作企業級 IAM 最佳實踐和多帳號權限管理

### 實作項目
1. **Organizations 與 SCP 治理**
   - 建立 AWS Organizations 結構（Dev/Stage/Prod OUs）
   - 實作 SCP 策略：
     - 禁止關閉 CloudTrail
     - 限制可用區域（只允許特定區域）
     - 強制標籤政策

2. **跨帳號權限架構**
   - 設計跨帳號 IAM Role（Trust Policy + 外部 ID）
   - 建立集中式身份帳號（Identity Account）
   - 實作 Permission Boundary 防止權限提升

3. **IAM Access Analyzer 應用**
   - 掃描意外對外開放的資源
   - 生成最小權限策略（基於 CloudTrail 分析）
   - 驗證策略語法和邏輯

4. **ABAC 實作**
   - 使用 Session Tags 動態授權
   - 基於部門標籤的 S3 存取控制
   - 測試不同場景下的權限效果

### 預期成果
- 多帳號權限架構圖
- 零信任模型實作
- 可審計的權限變更流程

---

## Lab 4: 資料加密與金鑰管理 (Data Encryption & Key Management)
**目標：** 實作端到端加密和金鑰生命週期管理

### 實作項目
1. **KMS 金鑰管理**
   - 建立 Customer Managed Key（對稱和非對稱）
   - 配置 Key Policy 和 Grants
   - 實作自動金鑰輪換
   - Multi-Region Keys 設置（災難恢復場景）

2. **服務加密整合**
   - S3：SSE-KMS 加密（強制加密 Bucket Policy）
   - RDS：啟用 at-rest 加密和 SSL 連線
   - EBS：加密 Volume 並共享給其他帳號
   - Lambda：環境變數加密

3. **Secrets Manager 與輪換**
   - 儲存 RDS 密碼到 Secrets Manager
   - 配置自動輪換（Lambda 函數）
   - 應用程式整合（Python boto3 範例）

4. **Envelope Encryption 實作**
   - 使用 GenerateDataKey 加密大檔案
   - 本地加密/解密流程
   - 性能與成本分析

### 預期成果
- 完整的金鑰管理生命週期
- 零明文密碼架構
- 符合合規要求的加密配置

---

## Lab 5: 網路安全與 DDoS 防護 (Network Security & DDoS Protection)
**目標：** 建立多層次網路防禦體系

### 實作項目
1. **VPC 安全架構**
   - 設計多層 VPC（Public/Private/DB subnets）
   - Security Groups：最小權限原則
   - NACLs：拒絕已知惡意 IP
   - VPC Flow Logs：流量分析並送到 Athena

2. **WAF 防護規則**
   - 部署 ALB + WAF
   - 配置規則：
     - Rate limiting（防止爆破）
     - IP reputation list（託管規則組）
     - SQL injection / XSS 防護
     - Geo-blocking（封鎖特定國家）
   - 測試規則有效性

3. **CloudFront + Shield**
   - 配置 CloudFront distribution
   - 啟用 Shield Advanced
   - Origin Access Control (OAC) 保護 S3
   - Custom SSL 憑證（ACM）

4. **Gateway Load Balancer**
   - 部署第三方安全設備（IDS/IPS）
   - 流量鏡像和檢查
   - 整合 VPC Endpoint Service

### 預期成果
- 可抵禦 L3/L4/L7 攻擊的架構
- 流量分析和異常偵測
- 實測 DDoS 模擬攻擊後的防護效果

---

## Lab 6: 合規審計與持續監控 (Compliance & Continuous Monitoring)
**目標：** 建立持續合規監控和自動修復系統

### 實作項目
1. **AWS Config 規則部署**
   - 啟用 Config Recorder（所有區域）
   - 部署合規規則：
     - S3 bucket 必須加密
     - EC2 不可有公開 IP（除 bastion）
     - IAM 密碼策略檢查
     - 未使用的 IAM 憑證偵測
   - 多帳號聚合（Aggregator）

2. **CloudTrail 進階配置**
   - Organization Trail（涵蓋所有帳號）
   - Data Events 監控（S3/Lambda）
   - Insights Events（異常活動偵測）
   - Log File Integrity Validation

3. **自動修復**
   - Systems Manager Automation 整合 Config
   - 偵測到違規後自動修復：
     - 移除過度開放的 Security Group 規則
     - 啟用 S3 加密
     - 撤銷超過 90 天未使用的 IAM key
   
4. **合規報告生成**
   - Security Hub 合規儀表板
   - 定期生成 PDF 報告（Lambda + SNS）
   - 整合 Jira/ServiceNow 工單系統

### 預期成果
- 24/7 持續合規監控
- 違規自動修復率 >80%
- 可審計的合規證據鏈
- 管理層可讀的安全態勢報告

---

## Lab 執行建議

### 前置準備
- 準備至少 2 個 AWS 帳號（測試跨帳號場景）
- 預算規劃：每個 Lab 約 $10-50（記得清理資源）
- 工具準備：AWS CLI, Terraform/CloudFormation, Python

### 學習路徑
1. **循序漸進**：按順序完成，每個 Lab 建立在前一個基礎上
2. **實戰導向**：不只是配置服務，要理解背後的「為什麼」
3. **破壞與修復**：故意製造安全問題，練習偵測和修復
4. **文檔化**：每個 Lab 寫下架構圖、決策理由和經驗教訓

### 成本控制
- 使用 AWS Free Tier（EC2 t2.micro, S3 前 5GB）
- 實驗後立即清理資源
- 使用 CloudFormation Stack 一鍵刪除
- 設置 Budget Alerts（超過 $100 告警）

### 認證準備
- 每個 Lab 對應考試的一個 Domain
- 完成 6 個 Lab 後，覆蓋考試 80% 實作內容
- 結合理論學習（官方文件、白皮書）
- 模擬考試：AWS Skill Builder Practice Exam

---

## 額外挑戰（進階學習者）

### Challenge 1: 紅隊藍隊演練
- 紅隊：嘗試繞過安全控制
- 藍隊：偵測並響應攻擊
- 使用 Kali Linux 工具集

### Challenge 2: 多雲安全
- 整合 Azure/GCP 日誌到 AWS Security Lake
- 統一的威脅偵測和響應

### Challenge 3: 零信任架構
- 實作完整的零信任模型
- 每個請求都需驗證和授權
- 微分段網路隔離

---

## 總結

這 6 個 Lab 涵蓋 AWS Security Specialty 認證的所有核心領域：
- **Lab 1-2**：Domain 1-2（Detection + Incident Response）
- **Lab 3-4**：Domain 4-5（IAM + Data Protection）
- **Lab 5**：Domain 3（Infrastructure Security）
- **Lab 6**：Domain 6（Governance & Compliance）

**預估完成時間：** 40-60 小時（含學習和實驗）
**難度等級：** 中高級（需有 AWS SAA 基礎）
**投資報酬率：** 極高（實戰技能 + 認證通過）
