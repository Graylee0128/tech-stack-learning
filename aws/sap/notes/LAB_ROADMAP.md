# AWS SAP認證 - 6大核心Lab實作規劃

## 設計原則
- 涵蓋80%+考試範圍
- 從簡單到複雜漸進
- 每個Lab 2-4小時完成
- 實際動手，非純理論

---

## Lab 1: Multi-Account Foundation (20%考題覆蓋)
**目標**: 建立企業級多帳號架構基礎

### 實作內容
1. **Organizations架構**
   - 創建Organization (3個member accounts)
   - 建立OU結構: Security / Workloads / Sandbox
   - 實作SCP策略 (禁止關閉CloudTrail、限制regions)

2. **IAM Identity Center**
   - 設定SSO
   - 創建Permission Sets (ReadOnly/PowerUser/Admin)
   - 配置跨帳號訪問

3. **Control Tower** (進階)
   - Landing Zone部署
   - Guardrails配置 (Detective + Preventive)
   - Account Factory建立新帳號

### 驗證點
- 能用單一登入訪問3個帳號
- SCP成功阻止違規操作
- CloudTrail記錄所有帳號活動

### 相關服務
Organizations, IAM Identity Center, Control Tower, CloudTrail, SCP

---

## Lab 2: 安全監控與響應 (25%考題覆蓋)
**目標**: 建立完整威脅檢測與自動響應系統

### 實作內容
1. **威脅檢測層**
   - GuardDuty跨3帳號啟用 (delegated admin)
   - Inspector掃描EC2漏洞
   - Security Hub啟用CIS + PCI DSS standards

2. **合規監控**
   - Config規則: 檢查S3加密、SG開放端口
   - Conformance Pack部署 (PCI DSS)
   - Config Aggregator跨帳號

3. **自動化響應**
   - EventBridge Rule: GuardDuty發現 → Lambda
   - Lambda function: 隔離受感染instance (修改SG)
   - SNS通知安全團隊

### 驗證點
- 手動觸發GuardDuty測試事件，驗證Lambda成功隔離
- Config檢測到不合規資源並記錄
- Security Hub dashboard顯示跨帳號發現

### 相關服務
GuardDuty, Inspector, Security Hub, Config, EventBridge, Lambda, SNS

---

## Lab 3: 網絡安全分層防禦 (15%考題覆蓋)
**目標**: 實現多層網絡防護

### 實作內容
1. **VPC基礎**
   - 創建Multi-tier VPC (Public/Private/Data subnets)
   - NAT Gateway + Internet Gateway
   - VPC Flow Logs → CloudWatch

2. **防火牆配置**
   - WAF: 建立Web ACL (rate limiting + SQL injection規則)
   - WAF整合ALB
   - Network Firewall: 出站流量過濾 (block惡意domain)
   - Shield Standard驗證

3. **集中管理**
   - Firewall Manager: 跨帳號管理WAF規則
   - Security Group統一策略

### 驗證點
- WAF成功阻擋rate limit超標請求
- Network Firewall阻止訪問黑名單域名
- Firewall Manager策略套用到所有帳號

### 相關服務
VPC, WAF, Network Firewall, Shield, Firewall Manager, CloudWatch

---

## Lab 4: 數據保護與加密 (15%考題覆蓋)
**目標**: 實現端到端數據加密

### 實作內容
1. **KMS密鑰管理**
   - 創建Customer Managed Key
   - Key policy配置 (跨帳號訪問)
   - Multi-region key (災難恢復)

2. **服務加密**
   - S3: SSE-KMS + Bucket Keys啟用
   - EBS: 預設加密
   - RDS: TDE啟用
   - S3 Bucket Policy強制加密上傳

3. **敏感數據發現**
   - Macie掃描S3 bucket
   - 識別PII數據
   - 自動分類標記

4. **證書管理**
   - ACM申請證書
   - ALB整合HTTPS
   - 自動續期驗證

### 驗證點
- 嘗試未加密上傳被拒絕
- Macie發現並報告敏感數據
- HTTPS連接成功，證書valid

### 相關服務
KMS, S3, EBS, RDS, Macie, ACM, ALB

---

## Lab 5: 混合雲遷移實戰 (15%考題覆蓋)
**目標**: 模擬本地到AWS遷移全流程

### 實作內容
1. **網絡連接**
   - Site-to-Site VPN建立 (模擬本地)
   - Transit Gateway設定
   - 路由表配置

2. **資料庫遷移**
   - Source: 本地MySQL (EC2模擬)
   - SCT評估 (模擬異構: MySQL→PostgreSQL)
   - DMS設定:
     - Full Load
     - CDC持續複製
   - Target: Aurora PostgreSQL

3. **存儲遷移**
   - DataSync: 本地NFS → S3
   - Storage Gateway: File Gateway設定
   - 資料驗證

### 驗證點
- VPN tunnel建立成功
- DMS完成initial load + CDC同步 (lag < 5秒)
- DataSync傳輸完成，檔案一致性驗證

### 相關服務
VPN, Transit Gateway, DMS, SCT, Aurora, DataSync, Storage Gateway

---

## Lab 6: 全球HA與災難恢復 (10%考題覆蓋)
**目標**: 實現跨區域高可用架構

### 實作內容
1. **Multi-Region部署**
   - Region 1 (us-east-1): Primary
   - Region 2 (us-west-2): DR

2. **數據複製**
   - S3 Cross-Region Replication
   - DynamoDB Global Tables (2 regions)
   - Aurora Global Database

3. **流量管理**
   - Route 53:
     - Health checks (primary region)
     - Failover routing policy
   - Global Accelerator設定
   - CloudFront distribution

4. **災難恢復演練**
   - 模擬Region 1故障
   - Failover到Region 2
   - RTO/RPO測量

5. **備份策略**
   - AWS Backup:
     - 跨region備份
     - Backup vault lock
   - Lifecycle policies

### 驗證點
- 主region "故障"時自動切換到DR
- Failover時間 < 5分鐘
- 數據無丟失 (RPO=0)
- 備份可成功還原

### 相關服務
Route 53, Global Accelerator, CloudFront, S3 CRR, DynamoDB Global Tables, Aurora Global Database, AWS Backup

---

## 完成後技能矩陣

| Lab | 核心服務 | 難度 | 時數 | 考題覆蓋 |
|-----|---------|------|------|---------|
| Lab 1 | Organizations, IAM Identity Center, Control Tower | ⭐⭐ | 3h | 20% |
| Lab 2 | GuardDuty, Security Hub, Config, EventBridge | ⭐⭐⭐ | 4h | 25% |
| Lab 3 | WAF, Network Firewall, Firewall Manager | ⭐⭐⭐ | 3h | 15% |
| Lab 4 | KMS, Macie, ACM | ⭐⭐ | 3h | 15% |
| Lab 5 | DMS, DataSync, VPN, Transit Gateway | ⭐⭐⭐⭐ | 4h | 15% |
| Lab 6 | Route 53, Global Accelerator, Aurora Global | ⭐⭐⭐⭐ | 3h | 10% |

**總計**: 20小時實作，覆蓋100%考試範圍（含重疊）

## 建議實作順序
1. Lab 1 → Lab 4 → Lab 3 (基礎建立)
2. Lab 2 (整合前面所有)
3. Lab 5 → Lab 6 (進階場景)

## Cost估算
- 單次完整實作: ~$50-80 (記得cleanup!)
- 建議使用AWS Free Tier + Sandbox帳號
- Lab結束立即刪除資源降低成本
