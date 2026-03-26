# 05 Security

## WAF

**What:** AWS WAF 是 Layer 7 Web Application Firewall。

**When to use:** 保護 ALB、CloudFront、API Gateway、AppSync 免受 SQLi、XSS、Bot、HTTP Flood 等攻擊。

**Key Points:**
- Web ACL 是主要配置單位。
- Rule 可比對 Country、IP、Header、Cookie、Path、Body、Method 等。
- Rate-based Rule 可限制來源速率。
- 可使用 Managed Rule Groups，也可自建 Rule Group。
- WAF 可做 Block、Count、Captcha、Label、Custom Response/Header。

**⚠️ 考試陷阱:**
- WAF 不是萬能 DDoS 工具，L3/L4 仍是 Shield 的範圍。

**✅ 記憶點:**
- `SQLi/XSS/Geo/Rate limit` 想 WAF。

## Shield

**What:** Shield 提供 AWS 上的 DDoS 防護。

**When to use:** 公網入口保護、需要 DDoS response team、財務保護。

**Key Points:**
- Shield Standard 對所有 AWS 客戶預設可用，主打 L3/L4 常見防護。
- Shield Advanced 為付費方案，可保護 CloudFront、Route 53、GA、ELB、EIP 等。
- Shield Advanced 含 SRT、進階可視性、可與 WAF 深度整合。

**⚠️ 考試陷阱:**
- Shield Advanced 不是自動保護所有資源，通常要明確啟用或用 Firewall Manager policy 套用。

**✅ 記憶點:**
- `Need SRT / advanced DDoS visibility` 想 Shield Advanced。

## Network Firewall / Firewall Manager / URL Filtering

**What:** 這組服務處理 VPC 內網路層與跨帳號中央管理的流量安全。

**When to use:** 中央防火牆、東西向/南北向檢查、組織層級統一政策、URL filtering。

**Key Points:**
- AWS Network Firewall 由 Firewall、Firewall Policy、Rule Groups 組成。
- Stateless engine 看 5-tuple；Stateful engine 用 Suricata 規則。
- Capacity 建立後不能改。
- Logging 主要記錄送入 stateful engine 的流量。
- Firewall Manager 可在 Organizations 層級統一管理 WAF、Shield Advanced、SG、Network Firewall、Resolver DNS Firewall。
- URL Filtering 需要 L7 aware 裝置，常見解法是 Proxy 或具 L7 檢查能力的安全設備。

**⚠️ 考試陷阱:**
- 想過濾 `https://example.com/path` 這類 URL，不能只用 SG/NACL。

**✅ 記憶點:**
- `Org-wide enforcement` 想 Firewall Manager。
- `VPC packet/domain inspection` 想 Network Firewall。

## CloudHSM

**What:** CloudHSM 是單租戶 HSM 服務，讓你完全控制加密金鑰材料。

**When to use:** FIPS Level 3、BYOK/自主管理 HSM、需標準 HSM API。

**Key Points:**
- CloudHSM 是 single-tenant，AWS 不持有你的密鑰控制權。
- 可透過 PKCS#11、JCE、CNG 使用。
- 可和 KMS 整合成 Custom Key Store。
- 高可用通常要多個 HSM 組成 cluster。

**⚠️ 考試陷阱:**
- CloudHSM 不是所有 AWS 服務都能像 KMS 那樣原生整合。

**✅ 記憶點:**
- `Strict key custody / compliance` 想 CloudHSM。

## CloudTrail / Config / Inspector / Macie

**What:** 這些服務分別負責 API 審計、資源設定追蹤、漏洞評估、S3 敏感資料識別。

**When to use:** 稽核、合規、事件追查、自動修復、資料保護。

**Key Points:**
- CloudTrail 記錄 Management、Data、Insights Events；預設 Event History 90 天。
- Trail 可單區或全區，也能做 Organization Trail。
- Log File Integrity Validation 可驗證日誌未被竄改。
- Config 追蹤設定變更並用 Rules/Conformance Packs 檢查合規，可整合 EventBridge 與 SSM remediation。
- Inspector 做網路暴露與主機弱點評估。
- Macie 專注 S3 敏感資料發現，可做 Managed 或 Custom Data Identifiers。

**⚠️ 考試陷阱:**
- 問「誰刪掉了某資源」通常是 CloudTrail，不是 Config。
- 問「資源現在是否符合政策」通常是 Config。

**✅ 記憶點:**
- `API audit` 想 CloudTrail。
- `Compliance drift` 想 Config。
- `EC2 vulnerability` 想 Inspector。
- `S3 sensitive data` 想 Macie。

## S3 Access Points / ip-ranges.json / Control Tower

**What:** 這些工具分別協助 S3 存取治理、AWS 公網範圍更新與多帳號治理。

**When to use:** 大型 S3 bucket 多團隊使用、公網 IP 白名單自動更新、多帳號安全落地。

**Key Points:**
- S3 Access Point 可為同一 Bucket 建立多個獨立入口與政策。
- Access Point 可限制 VPC 存取，並與 Endpoint Policy 配合。
- `ip-ranges.json` 提供 AWS 公網位址範圍，可訂閱 SNS 更新通知自動同步規則。
- Control Tower 用 Organizations、IAM Identity Center、Config、CloudTrail 等打造 Landing Zone 與 Guardrails。

**⚠️ 考試陷阱:**
- Access Point policy 不會自動取代 Bucket policy，通常兩邊都要允許。

**✅ 記憶點:**
- `Many apps/teams one bucket` 想 S3 Access Points。
- `Governed multi-account baseline` 想 Control Tower。
