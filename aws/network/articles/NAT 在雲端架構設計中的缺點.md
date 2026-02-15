# NAT 在雲端架構設計中的缺點

## 摘要（Abstract）

在傳統資料中心與早期雲端架構中，NAT（Network Address Translation）被廣泛用於讓私有子網安全地存取網際網路。然而，在現代雲原生（Cloud-Native）與大規模 VPC 架構中，過度依賴 NAT（特別是 NAT Gateway）會帶來成本、可擴展性、連線穩定性與可觀測性等多方面的架構劣勢。本文從實務架構設計角度，深入分析 NAT 的核心缺點，以及何時應該減少對 NAT 的依賴（例如導入 IPv6 + Egress-Only IGW、PrivateLink、VPC Endpoint 等替代方案）。

## 一、NAT 的本質定位：它其實是「折衷解法」，不是理想解法

在 AWS VPC 設計中，NAT Gateway 的主要用途是：

```
Private Subnet → NAT Gateway → Internet
（只出不進）
```

其核心目的：

- 隱藏私有 IP（10.x）
- 提供 outbound internet access
- 避免直接暴露 public IP

但從架構師角度來看：

> NAT 是為了解決 IPv4 地址不足與安全隔離的「歷史性折衷方案」，而非雲原生最佳設計。

## 二、NAT 的核心架構缺點（最重要五大類）

### 1️⃣ 成本問題（FinOps 最大痛點）

NAT Gateway 是持續性高成本元件。在 AWS 計費模型中，NAT Gateway 收費包含：

- 每小時固定費用
- 每 GB Data Processing 費用
- 跨 AZ 流量費（若設計不當）

典型流量路徑：

```
Private EC2 → NAT GW → Internet API / S3 / 外部服務
```

即使只是：

- 系統更新（yum/apt）
- 拉 Docker image
- API 呼叫

全部都會經過 NAT 並產生費用。

**架構影響（長期）**

| 架構 | 成本趨勢 |
|------|---------|
| 全私網 + NAT 出網 | 高（隨流量線性成長） |
| IPv6 + Egress Only IGW | 低（無 NAT processing fee） |
| VPC Endpoint / PrivateLink | 最低（內網流量） |

對於高流量系統（DevOps pipeline、微服務、資料處理），NAT 成本可能成為月帳單最大項之一。

### 2️⃣ 連線穩定性問題（Stateful Connection Tracking）

NAT Gateway 是一個 Stateful Network Device（有連線狀態表），這會導致幾個經典問題：

#### (1) Idle Timeout（常見 ANS 考點）

AWS NAT Gateway：

- Idle timeout ≈ 350 秒（約 5 分 50 秒）

影響場景：

- 長時間資料庫查詢
- 長連線 API
- Streaming / WebSocket（部分情況）
- 批次處理任務

典型故障模式：

```
EC2 → 發送請求
（長時間無回應）
NAT：清除 state
DB → 回應
→ 回應被丟棄（client 收不到）
```

這在實務中非常難除錯。

#### (2) Port Exhaustion（高併發風險）

NAT 需要做：

- Source IP + Port translation

當大量連線時：

- 可用 ephemeral port 被耗盡
- 造成隨機連線失敗
- 高併發微服務架構特別容易中招

對於：

- Kubernetes Cluster
- 高 QPS API service
- Lambda 高併發外呼

是隱性風險。

### 3️⃣ 可觀測性（Observability）與除錯困難

NAT 會「隱藏真實來源 IP」，導致：

- Log 分析困難
- Trace 斷裂
- 外部服務只看到 NAT IP

例如：

```
10.0.1.25 → NAT GW → 54.x.x.x → 外部API
```

外部系統只記錄：

- 54.x.x.x（NAT IP）

這對：

- 安全稽核
- 分散式追蹤
- 零信任架構

都是不利因素。

### 4️⃣ 架構擴展性（Scalability）限制

NAT 架構通常是：

```
多個 Private Subnet
        ↓
  NAT Gateway（單一出口）
```

潛在問題：

- 成為流量集中點（egress bottleneck）
- 多 AZ 設計需多個 NAT（成本更高）
- 跨 AZ NAT 會增加 latency + cost

大型企業架構（多 VPC / 多帳號）會逐步減少對 NAT 的依賴，改用更分散的 egress 設計。

### 5️⃣ 安全模型上的誤解（False Sense of Security）

很多工程師誤以為：

> 有 NAT = 很安全

實際上：

- NAT ≠ 防火牆
- NAT 只是「不接受未建立的 inbound 連線」

安全控制仍然依賴：

- Security Group
- NACL
- WAF / Zero Trust

而且 NAT 會讓：

- egress control 變得模糊
- 難以做精細流量限制（除非搭配 firewall）

## 三、NAT 在雲原生架構中的替代設計（Modern Best Practice）

### 1️⃣ IPv6 + Egress-Only Internet Gateway（最推薦）

優勢：

- 不需要 NAT
- 無 stateful translation
- 支援 outbound-only 安全模型
- 降低成本 + 提升穩定性

適合：

- Private Subnet 需要對外 API 存取
- DB / Batch / Backend services

### 2️⃣ VPC Endpoint（極致 FinOps + 安全）

如果流量是：

- S3
- DynamoDB
- AWS API

最佳架構：

```
Private EC2 → VPC Endpoint → AWS Service
（完全不經過 NAT / Internet）
```

優勢：

- 0 NAT cost
- 低延遲
- 高安全（不走公網）

### 3️⃣ AWS PrivateLink（企業級）

適用：

- SaaS 服務整合
- 跨帳號服務
- 零信任架構

可完全避免：

- 公網
- NAT
- IGW

## 四、何時仍然「應該使用 NAT」？（務實架構觀）

NAT 並非過時，而是在特定情境仍然合理。

**適合使用 NAT 的情境：**

- Legacy IPv4-only 系統
- 短期過渡架構（Migration phase）
- 小型系統（低流量）
- 需要簡單 egress control

**不適合高度依賴 NAT 的情境：**

- 高流量微服務架構
- 大規模 Kubernetes
- 長連線資料處理系統
- 成本敏感（FinOps優先）組織

## 五、架構師最終結論（Strategic Takeaway）

從現代雲架構（AWS Well-Architected + FinOps）角度：

> NAT Gateway 應被視為「相容性與過渡型元件」，而非長期核心網路出口設計。隨著系統規模成長，應逐步導入 IPv6、VPC Endpoint、PrivateLink 等無 NAT 架構，以降低成本、提升穩定性與可擴展性。

## 六、給你（DevOps + 雲端路線）的實務建議（高價值）

以你的職涯方向（Cloud / DevOps / FinOps）：

- 面試 AWS / Cloud Architect
- 設計 VPC 架構
- 做成本優化

這句話非常加分：

> "We should minimize NAT dependency by using VPC Endpoints and IPv6 egress design to reduce cost and avoid stateful bottlenecks."

**下一篇進階續作：**

《NAT Gateway vs VPC Endpoint vs PrivateLink vs EIGW：架構選型決策樹（ANS + 實務通用）》