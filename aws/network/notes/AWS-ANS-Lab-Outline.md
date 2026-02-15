# AWS ANS Certification - Lab 實作大綱建議

## ANS-C01 考試覆蓋率分析

### 📊 Lab vs 考試領域對應表

| 考試領域 | 官方比重 | 對應Lab | Lab覆蓋率 |
|---------|---------|---------|----------|
| **Domain 1: Network Design** | 30% | Lab 1,3,4,6 | ✅ 90% |
| **Domain 2: Network Implementation** | 26% | Lab 2,4,5,6 | ✅ 85% |
| **Domain 3: Network Management & Operation** | 20% | Lab 1,2,6 | ✅ 80% |
| **Domain 4: Network Security, Compliance** | 24% | Lab 3,6 | ⚠️ 70% |

**整體覆蓋率：85%** (6個Lab + 額外補充 → 可達90%+)

### 🎯 各Lab考試比重估算

| Lab | 核心主題 | 預估考題占比 | 高頻考點 |
|-----|---------|-------------|----------|
| Lab 1 | VPC Endpoints | **18-22%** | Gateway vs Interface選型、Endpoint Policy |
| Lab 2 | Load Balancer | **12-15%** | ALB routing、NLB static IP、選型決策 |
| Lab 3 | PrivateLink | **8-12%** | Service Provider架構、跨帳號連接 |
| Lab 4 | Hybrid Connectivity | **15-18%** | Transit Gateway、VPN、路由決策 |
| Lab 5 | Edge Services | **8-10%** | CloudFront vs Global Accelerator |
| Lab 6 | 綜合架構 | **15-20%** | 故障排查、成本優化、架構決策 |

**總計：76-97%** (題目會有組合型場景，因此範圍較寬)

### ⚠️ 未完全覆蓋領域（需額外補充）

1. **Route 53 進階路由** (5-7%)
   - Geolocation、Latency-based、Weighted routing
   - Health check 與 failover 策略
   - Private Hosted Zone

2. **Direct Connect 深度配置** (3-5%)
   - LAG (Link Aggregation Group)
   - VLAN tagging 與 BGP attributes
   - DX Gateway 多 region 連接

3. **AWS Network Firewall** (2-3%)
   - Stateful rule groups
   - Domain filtering
   - IPS 整合

4. **IPv6 進階場景** (2-3%)
   - Egress-only Internet Gateway
   - IPv6 CIDR 規劃

**補充建議：**
- 完成 6 個 Lab 後，額外研讀官方文檔 2-3 小時
- 重點練習 AWS 官方 Sample Questions
- 使用 Tutorials Dojo 或 Whizlabs 模擬考題

---

## Lab 設計原則
- 每個 Lab 60-90 分鐘
- 覆蓋考試高頻場景
- 由簡到難，逐步建構複雜架構
- 強調故障排查和成本優化

---

## Lab 1: VPC Endpoints 架構實戰 (基礎)
**核心目標：掌握三種 VPC Endpoint 類型的實際應用**

**📊 ANS-C01 考試比重：18-22%**
- Domain 1 (Network Design): Gateway vs Interface 選型決策
- Domain 3 (Management): Endpoint policy 配置與故障排查

### 實作項目
1. **Gateway Endpoint：**
   - 創建私有子網路 EC2
   - 配置 S3 Gateway Endpoint
   - 測試無 internet route 下的 S3 存取
   - 自訂 endpoint policy 限制 bucket 存取

2. **Interface Endpoint：**
   - 為 SQS 創建 Interface Endpoint
   - 測試 Private DNS 解析
   - 配置 Security Group 控制存取
   - 驗證 from on-premises access（模擬）

3. **成本對比實驗：**
   - 計算 Gateway Endpoint vs NAT Gateway 成本差異
   - 監控資料傳輸量

### 預期產出
- 理解何時選擇 Gateway vs Interface
- 掌握 endpoint policy vs IAM policy 組合
- 能夠故障排查 endpoint 連接問題

### 高頻考點
✓ Gateway Endpoint **僅支援 S3 和 DynamoDB**
✓ Interface Endpoint 需啟用 Private DNS（SQS 為必要）
✓ Gateway Endpoint 免費，Interface Endpoint $0.01/hr/AZ
✓ Security Group 僅適用於 Interface Endpoint

**所需資源：** 1 VPC, 2 subnets, 1 EC2, 2 endpoints (~$2-3)

---

## Lab 2: Load Balancer 選型與配置 (基礎-中級)
**核心目標：實際對比 ALB、NLB、GWLB 的使用場景**

**📊 ANS-C01 考試比重：12-15%**
- Domain 2 (Implementation): Load Balancer 部署與配置
- Domain 1 (Design): 依需求選擇正確的 LB 類型

### 實作項目
1. **ALB 高級路由：**
   - 配置 path-based routing (/api/* vs /web/*)
   - 設置 host-based routing (api.domain.com vs www.domain.com)
   - 實現 HTTP redirect (HTTP→HTTPS)
   - 配置 fixed-response for maintenance mode

2. **NLB 性能測試：**
   - 部署 NLB with static IP
   - 測試 source IP preservation
   - 對比 ALB vs NLB latency（使用 wrk 或 ab 工具）

3. **故障排查演練：**
   - 製造 health check failure scenario
   - 分析 5xx error 原因
   - 調整 deregistration delay 參數

### 預期產出
- 能夠根據需求選擇正確的 LB 類型
- 理解不同 LB 的性能特性
- 掌握 LB 故障排查技巧

### 高頻考點
✓ **靜態 IP 需求 = NLB**（唯一支援 Elastic IP）
✓ **Path/Host routing = ALB**（Layer 7 特性）
✓ **保留來源 IP = NLB**（ALB 需用 X-Forwarded-For header）
✓ **PrivateLink 只能用 NLB** 作為 backend

**所需資源：** 1 VPC, 2 AZs, 4 EC2 targets, 2 LBs (~$5-7)

---

## Lab 3: PrivateLink 服務提供者架構 (中級)
**核心目標：構建完整的 PrivateLink service provider/consumer 架構**

**📊 ANS-C01 考試比重：8-12%**
- Domain 1 (Design): Multi-consumer 服務架構設計
- Domain 4 (Security): 跨帳號安全連接

### 實作項目
1. **Service Provider 側：**
   - 創建 NLB backed service
   - 配置 VPC Endpoint Service
   - 設置 service acceptance（手動 approve）

2. **Service Consumer 側：**
   - 從不同 VPC 創建 Interface Endpoint
   - 測試跨 VPC 私有連接
   - 驗證 no VPC peering needed

3. **安全與監控：**
   - 配置 endpoint service permissions
   - 使用 CloudWatch 監控連接狀態
   - 測試 multi-consumer scenario

### 預期產出
- 理解 PrivateLink vs VPC Peering 差異
- 能夠設計 multi-consumer service 架構
- 掌握 service acceptance workflow

### 高頻考點
✓ PrivateLink **必須使用 NLB** 作為 backend
✓ **單向連接**，consumer 無法反向存取 provider VPC
✓ **無 CIDR 重疊限制**（vs VPC Peering 必須無重疊）
✓ 可擴展至數千個 consumer（VPC Peering 需 full mesh）

**所需資源：** 2 VPCs, 1 NLB, 1 endpoint service, 2 interface endpoints (~$4-6)

---

## Lab 4: Hybrid Network 連接與路由 (中級-高級)
**核心目標：實現 AWS 與 on-premises 的混合網路架構**

**📊 ANS-C01 考試比重：15-18%**
- Domain 1 (Design): Hybrid connectivity 架構決策
- Domain 2 (Implementation): VPN、Transit Gateway 配置

### 實作項目
1. **Site-to-Site VPN Setup：**
   - 配置 Virtual Private Gateway
   - 創建 Customer Gateway（模擬 on-prem）
   - 建立 VPN connection
   - 配置 BGP routing

2. **Transit Gateway Hub-and-Spoke：**
   - 創建 Transit Gateway
   - 連接 3 個 VPCs + VPN
   - 配置 TGW route tables
   - 實現 inter-VPC routing

3. **路由優化：**
   - 測試 VPC Peering vs Transit Gateway
   - 分析 cost trade-offs
   - 實現基於 prefix 的 selective routing

### 預期產出
- 能夠設計 hybrid network architecture
- 理解 Transit Gateway vs VPC Peering 選型
- 掌握複雜路由場景配置

### 高頻考點
✓ **VPC Peering 非遞移**（non-transitive），需 full mesh
✓ **Transit Gateway 可連接 5000+ VPCs**
✓ VPN 作為 Direct Connect **備援方案**
✓ TGW route table 控制 VPC 間路由

**所需資源：** 3 VPCs, 1 TGW, 1 VPN (~$6-8)

---

## Lab 5: Edge Services - CloudFront & Global Accelerator (中級)
**核心目標：優化全球用戶存取性能**

**📊 ANS-C01 考試比重：8-10%**
- Domain 2 (Implementation): CDN 和全球加速器配置
- Domain 1 (Design): 服務選型決策

### 實作項目
1. **CloudFront Distribution：**
   - 配置 Origin（S3 + ALB dual origin）
   - 設置 cache behavior rules
   - 實現 Lambda@Edge for URL rewrite
   - 測試 cache hit ratio

2. **Global Accelerator：**
   - 創建 accelerator with 2 regions
   - 配置 endpoint groups（ALB in us-east-1 & eu-west-1）
   - 測試 health-based failover
   - 對比 CloudFront vs Global Accelerator performance

3. **Cost Optimization：**
   - 分析 CloudFront cache metrics
   - 優化 origin request count
   - 計算 data transfer savings

### 預期產出
- 理解 CloudFront vs Global Accelerator 差異
- 能夠實現 multi-region failover
- 掌握 edge service 性能調優

### 高頻考點
✓ **CloudFront = CDN + Caching**（適合 HTTP/HTTPS）
✓ **Global Accelerator = Anycast IP + Health-based routing**（適合非 HTTP）
✓ Lambda@Edge viewer request 在**快取檢查前**執行
✓ GA 提供 **2 個靜態 Anycast IP**

**所需資源：** 2 regions, 2 ALBs, 1 CloudFront, 1 GA (~$10-15)

---

## Lab 6: 綜合場景 - Production-Grade Multi-Tier Architecture (高級)
**核心目標：整合所有知識點，構建 production-ready 架構**

**📊 ANS-C01 考試比重：15-20%**
- Domain 1-4 綜合考核：架構設計、故障排查、成本優化、安全合規
- 模擬真實 production 場景的複雜決策

### 實作項目
**Scenario：** 電商平台需要高可用、安全、性能優化的網路架構

**要求：**
- 多 AZ 高可用
- 私有子網路資料庫（RDS）
- S3 私有存取（no internet route）
- 全球用戶低延遲存取
- On-premises integration
- 全流量 IPS/IDS 檢測

**實現架構：**
```
Users (Global)
  ↓
CloudFront (CDN + WAF)
  ↓
Global Accelerator (multi-region failover)
  ↓
ALB (us-east-1 + eu-west-1)
  ↓
GWLB Endpoint → Gateway LB → IPS/IDS Appliances
  ↓
EC2 Auto Scaling Group
  ↓
RDS (private subnet)
  ↓
S3 (via Gateway Endpoint)
  ↓
On-premises (via Direct Connect + VPN backup)
```

### 具體任務
1. 設計 VPC 網路拓撲（CIDR 規劃）
2. 部署 multi-region ALB + auto scaling
3. 配置 GWLB + security appliances（可用開源 Suricata IDS 模擬）
4. 實現 PrivateLink for cross-account service
5. 配置 CloudFront + Global Accelerator
6. 模擬 failure scenarios 並驗證 failover

### 預期產出
- 完整 production 架構 diagram
- Cost estimation breakdown
- Performance benchmark results
- Disaster recovery plan
- Security compliance checklist

### 高頻考點整合
✓ **Multi-layer 安全**：Security Group + NACL + WAF + GWLB
✓ **成本優化**：Gateway Endpoint（免費）vs NAT Gateway
✓ **高可用設計**：Multi-AZ + Multi-Region + Health checks
✓ **故障排查**：VPC Flow Logs、CloudWatch、Route table 分析

**所需資源：** 2 regions, 2 VPCs, multi-AZ setup (~$30-50)
**建議時間：** 3-4 小時（可分 2 次完成）

---

## Lab 執行建議

### 通用準備
1. **成本控制：**
   - 使用 t3.micro instances
   - 完成後立即刪除資源
   - 設置 billing alert

2. **故障排查工具：**
   - VPC Flow Logs
   - CloudWatch metrics
   - AWS CLI for debugging

3. **文檔記錄：**
   - 每步截圖
   - 命令記錄
   - troubleshooting notes

### 學習順序
1. Lab 1 → Lab 2：掌握基礎組件（2-3 小時）
2. Lab 3 → Lab 4：理解互聯架構（3-4 小時）
3. Lab 5：熟悉 edge services（1.5-2 小時）
4. Lab 6：綜合實戰（3-4 小時）

**總計時間：** 10-13 小時 hands-on practice

### 考試模擬
完成所有 Lab 後：
- 練習 AWS 官方 sample questions
- 參加模擬考試（Tutorials Dojo, Whizlabs）
- 重點複習每個 Lab 的 architecture decision rationale

---

## 額外建議

### Terraform IaC 實踐（可選）
將 Lab 1-5 用 Terraform 重寫：
- 學習 IaC 最佳實踐
- 理解資源 dependencies
- 可重複部署測試

### 成本優化 Challenge
針對 Lab 6 架構：
- 如何在不影響 performance 下減少 30% cost？
- 哪些服務可用 Reserved Instance？
- Data transfer 優化機會？

### 故障注入測試
- 模擬 AZ failure
- 測試 DDoS 場景（limited）
- 驗證 backup connectivity paths
