# 04 Route53 CDN

## Route 53 Hosted Zones / Resolver / DNSSEC

**What:** Route 53 提供註冊、Hosted Zone、Routing Policy、Health Check、Resolver Endpoint 與 DNSSEC。

**When to use:** Public/Private DNS、Hybrid DNS、Global routing、容災切換。

**Key Points:**
- Public Hosted Zone 可從公網與 VPC 解析；Private Hosted Zone 只對關聯 VPC 解析。
- 同名 Public 與 Private Hosted Zone 可做 Split-view DNS。
- ALIAS 能把 zone apex 指向 AWS 資源。
- Route 53 Resolver Endpoint 分成 Inbound 與 Outbound。
- Inbound 讓 On-prem 轉送查詢進 AWS；Outbound 讓 AWS 轉送查詢到 On-prem DNS。
- DNSSEC 啟用時會涉及 KSK、ZSK、DS record 與 parent zone chain of trust。

**Comparison:**
- Inbound Endpoint 是「On-prem 查 AWS」。
- Outbound Endpoint 是「AWS 查 On-prem」。

**⚠️ 考試陷阱:**
- `VPC + 2` Resolver 本身不能直接被 On-prem 用；混合解析要靠 Resolver Endpoints。

**✅ 記憶點:**
- `Hybrid DNS` 幾乎都在考 Inbound/Outbound Resolver Endpoint。

## Route 53 Health Checks

**What:** Route 53 Health Check 持續監控 endpoint 健康狀態，驅動 DNS failover 與路由決策。

**When to use:** Active/Passive failover、Routing Policy 搭配、多 Region DR、Alarm-based 切換。

**Key Points:**
- 三種 Health Check 類型：
  - **Endpoint**：直接對 IP 或 FQDN 做 HTTP/HTTPS/TCP 檢查。
  - **Calculated**：聚合多個子 Health Check 的結果（AND/OR/至少 N 個健康）。
  - **CloudWatch Alarm-based**：依據 CloudWatch Alarm 狀態判斷健康。
- Endpoint Health Check 由全球多個 Region 的 checker 發出請求，需在 SG/NACL 放行這些 IP。
- Health Check 可設定 failure threshold（連續幾次失敗才算 unhealthy）與 request interval（10s 或 30s）。
- String Matching：HTTP/HTTPS 可檢查回應 body 前 5120 bytes 是否包含指定字串。
- Failover Routing Policy 必須搭配 Health Check 才能自動切換。

**Comparison:**
- Endpoint HC 適合直接監控服務可達性。
- CloudWatch Alarm HC 適合監控內部指標（如 DynamoDB throttling、Lambda error rate）來觸發 DNS 切換。
- Calculated HC 適合複合判斷（例如：3 個 microservice 中至少 2 個健康才算整體健康）。

**⚠️ 考試陷阱:**
- Health Check 只能監控公網可達的 endpoint；私網 endpoint 需改用 CloudWatch Alarm-based HC。
- Health Check 結果有傳播延遲，不是即時切換。

**✅ 記憶點:**
- `DNS failover` 一定要有 Health Check。
- `Private endpoint health` 想 CloudWatch Alarm-based HC。

## Route 53 Routing Policies

**What:** Route 53 可依不同策略回傳不同解析結果。

**When to use:** Failover、全球導流、區域限制、簡易流量分配。

**Key Points:**
- Simple Routing 最基本，不支援 health-check aware load balancing。
- Failover 適合 active/passive。
- Weighted 適合流量分流、藍綠、灰度。
- Multivalue 最多回 8 個健康記錄，不是正式負載平衡器。
- Latency-based 依 AWS 維護的 latency 資料庫回應。
- Geolocation 看使用者地理位置；Geoproximity 看距離與 bias。
- IP-based routing 依客戶端來源 CIDR 做對應。

**⚠️ 考試陷阱:**
- Weighted 搭配 health check 時，不健康記錄不會直接從權重概念消失，題目會考 retry 行為。

**✅ 記憶點:**
- `User location restriction` 想 Geolocation。
- `Closest based on AWS latency map` 想 Latency-based。

## CloudFront

**What:** CloudFront 是 CDN，透過 Edge Location 與快取改善內容交付。

**When to use:** 靜態內容加速、全球低延遲、S3/ALB 前置、防護與內容限制。

**Key Points:**
- CloudFront 核心概念是 Distribution、Behavior、Origin、Edge Location、Regional Edge Cache。
- Behavior 可控制 Origin、TTL、Protocol Policy、Allowed Methods、Compression、Field-level Encryption、Lambda@Edge。
- Cache hit 可降低 Origin 壓力；Cache miss 會發生 origin fetch。
- Invalidations 可強制快取失效，但有成本；版本化檔名通常更實用。
- Viewer 與 Origin 是兩條獨立連線，TLS 設定需分開考慮。

**Comparison:**
- CloudFront 靠快取把內容靠近使用者。
- Global Accelerator 不快取，是把使用者更快帶進 AWS 全球網路。

**Limits / Caveats:**
- CloudFront 的自訂網域憑證要放在 `us-east-1` 的 ACM。
- S3 origin 與 custom origin 的能力、TLS 要求與快取路徑不同。

**⚠️ 考試陷阱:**
- 不是所有 Origin 都能用 OAI；新題型更偏向 OAC。

**✅ 記憶點:**
- `Need caching` 一定先想到 CloudFront，不是 Global Accelerator。

## CloudFront Security / Private Content / Lambda@Edge

**What:** CloudFront 可做私有內容發放、Geo restriction、Field-level encryption 與邊緣運算。

**When to use:** 下載授權、內容區域限制、在 Edge 改寫請求或回應。

**Key Points:**
- OAC 是目前比 OAI 更新的 S3 origin 保護方式。
- Private Distribution 可透過 Signed URL 或 Signed Cookie 保護。
- Geo restriction 只支援國家層級。
- Lambda@Edge 可在 Viewer/Origin request/response 階段插入邏輯。

**Comparison:**
- Signed URL 適合單一物件；Signed Cookie 適合一群物件。
- Geo Restriction 是整個 Distribution 的粗粒度管控；第三方邏輯可更細。

**⚠️ 考試陷阱:**
- 要限制到使用者屬性或更細的規則，不是靠原生 Geo restriction。

**✅ 記憶點:**
- `Edge auth / rewrite / personalization` 想 Lambda@Edge。

## ACM

**What:** ACM 是 AWS 憑證管理服務，可簽發或匯入憑證。

**When to use:** ALB、CloudFront、整合 AWS 受管服務的 TLS。

**Key Points:**
- ACM 是 Regional service。
- ACM 產生的憑證可自動續期；匯入憑證需要自己管理續期。
- CloudFront 屬於 Global service，但憑證仍必須放在 `us-east-1`。

**⚠️ 考試陷阱:**
- 要給 ALB 用的憑證，必須存在 ALB 所在 Region。
- 要給 CloudFront 用的憑證，必須在 `us-east-1`。

**✅ 記憶點:**
- `CloudFront certificate = us-east-1`。
