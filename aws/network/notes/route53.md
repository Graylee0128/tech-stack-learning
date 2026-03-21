# AWS Route 53 學習筆記

## 目錄

- [一、核心紀錄類型 (Record Types)](#一核心紀錄類型-record-types)
- [二、七大路由政策 (Routing Policies)](#二七大路由政策-routing-policies)
- [三、Alias vs. CNAME 終極對決](#三alias-vs-cname-終極對決)
- [四、網域管理三層體系](#四網域管理三層體系為什麼不會撞名)
- [五、Public vs. Private Hosted Zone](#五public-vs-private-hosted-zone)
- [六、進階考點（ANS 級別）](#六進階考點ans-級別)
- [七、快速排錯直覺](#七快速排錯直覺)

---

## 一、核心紀錄類型 (Record Types)

| 紀錄類型 | 關鍵用途 | 考試必記陷阱 |
|---------|---------|------------|
| **A** | 域名 → IPv4 地址 | 到處都能用（Apex 或子網域皆可） |
| **AAAA** | 域名 → IPv6 地址 | 看到 IPv6 就選它 |
| **CNAME** | 域名 → 域名 | **不能用於 Zone Apex**（RFC 限制） |
| **Alias** | AWS 專屬域名對應 | 可用於 Apex；指向 ALB/CloudFront/S3；免費且自動更新 IP |
| **NS** | 指定誰管這個 Zone | 委派子網域（Delegation）必填 |
| **SOA** | 網域的身分證 | 包含 TTL 和管理員資訊 |
| **PTR** | IP → 域名（反向） | 通常用於防止 Email 被當垃圾郵件 |

---

## 二、七大路由政策 (Routing Policies)

看到場景關鍵字直接對號入座：

| 路由政策 | 場景關鍵字 | 備註 |
|---------|-----------|------|
| **Simple** | 一對一，或隨機回傳多個 IP | 無健康檢查 |
| **Weighted** | A/B Testing、藍綠佈署、按比例分配流量 | 例如 90% vs 10% |
| **Latency** | 效能優先、哪台反應最快就去哪 | 依使用者到各區的延遲選路 |
| **Failover** | 災難恢復（DR）、Active-Passive 主從切換 | **必須搭配 Health Check** |
| **Geolocation** | 內容在地化、根據使用者國籍/洲別導流 | 例如法國人看法文版 |
| **Geoproximity** | 考慮資源負荷的動態導流、**Bias 偏向值** | 想讓某機房扛更多鄰近流量時使用 |
| **Multivalue Answer** | 簡單負載平衡 + 健康檢查 | 回傳最多 8 個健康 IP，客戶端自選 |

---

## 三、Alias vs. CNAME 終極對決

考試最愛考的細節：

| 特性 | CNAME | Alias（別名紀錄） |
|------|-------|----------------|
| **Zone Apex（根網域）** | ❌ 不支援（會報錯） | ✅ 支援（首選！） |
| **收費** | 依查詢次數收費 | 免費（連向 AWS 資源時） |
| **目標變更時** | 需等待 TTL 生效 | 即時生效（AWS 自動更新） |
| **目標限制** | 任何域名皆可 | 只能指向 AWS 內部資源 |

### 為什麼 CNAME 不能放在 Apex？

DNS 底層法律（RFC 規範）：CNAME 是**排他性**的，不能跟別的紀錄共存。
而 **Zone Apex 依法必須擁有 NS 和 SOA**，所以 Apex 絕對不能設 CNAME。

**Alias 的黑科技**：外表像 A Record（所以不跟 NS/SOA 衝突，能放 Apex），靈魂像 CNAME（自動追蹤 AWS 資源的 IP 變動）。

### 考試口訣

> 看到「把頂級網域（Apex）連到 Load Balancer 或 CloudFront」→ 答案只有一個：**Alias Record**

| 目標 | 子網域（`www`） | 頂級網域（Apex） |
|------|--------------|----------------|
| 一般做法 | 用 CNAME 指向 CloudFront/ALB | **禁止** 使用 CNAME |
| AWS 做法 | 用 CNAME 或 Alias | **強烈建議用 Alias** |

---

## 四、網域管理三層體系（為什麼不會撞名）

```
ICANN（制定規則）
  └── Registry 註冊局（每個 TLD 唯一一家，如 .com → Verisign；.tw → TWNIC）
        └── Registrar 註冊商（AWS Route 53、GoDaddy、Namecheap 等零售商）
```

- **ICANN**：全球最高權力機構，授權各 TLD 的 Registry
- **Registry**：每種後綴（.com/.tw）只有**唯一一家**中央資料庫；一旦網域被購買，秒級鎖定同步全球
- **Registrar**：代你跟 Registry 溝通的零售商

### Registrar vs. DNS Hosting（重要概念分清）

| 角色 | Registrar（註冊商） | DNS Hosting（託管紀錄） |
|------|-------------------|----------------------|
| **比喻** | 地政事務所/代書 | 大樓管理員/指路牌 |
| **任務** | 確認你擁有這個網域的「產權」 | 告訴訪客你的 IP 在哪 |
| **AWS 服務** | Route 53 - Registered Domains | Route 53 - Hosted Zones |

**分家實務（常見考題場景）：**
在 GoDaddy 買網域（GoDaddy 當 Registrar），但把 DNS 紀錄放在 AWS 管（AWS 當 Hosted Zone）。
只需在 GoDaddy 後台把 **NS 紀錄改成 AWS 的 4 台伺服器**即可。

**Transfer 要分清：**
- **Transfer Registrar**：把產權從 GoDaddy 移到 AWS，需 5~7 天、解鎖、拿 Auth Code
- **Update NS**：只是改管理員，幾小時內生效，產權不變

---

## 五、Public vs. Private Hosted Zone

| 特性 | Public Hosted Zone | Private Hosted Zone |
|------|-------------------|-------------------|
| **誰能查詢** | 網際網路上的任何人 | 只有指定 VPC 內的 EC2 |
| **解析出的 IP** | 通常是 Public IP | 通常是 Private IP（10.x.x.x） |
| **安全性** | 紀錄透明，全世界可見 | 隱身，外部無法查到 |
| **網域命名** | 必須擁有該網域所有權 | 可以隨便取名（甚至 `google.com`） |
| **使用場景** | 官網、電商、公開 API | 資料庫、內部微服務、地端 VPN 資源 |

### Split-Horizon DNS（拆分大腦）— ANS 必考

同一個網域名稱（如 `example.com`），依查詢來源回傳不同結果：

- **VPC 內查詢** `api.example.com` → 解析到內網 IP `10.0.0.5`（省流量、快、安全）
- **Internet 查詢** `api.example.com` → 解析到公網 IP `1.2.3.4`（透過 Load Balancer）

**AWS 規則：** VPC 關聯了 Private Hosted Zone 時，**優先看 Private Zone**；查不到才去 Public。

### Private Hosted Zone 不生效的常見原因

確認 VPC 設定是否啟用（必考點）：
- ✅ **Enable DNS Hostnames**
- ✅ **Enable DNS Support**

---

## 六、進階考點（ANS 級別）

### Route 53 Resolver

| 方向 | 說明 | 關鍵字 |
|------|------|-------|
| **Inbound Endpoint** | 地端（On-Premises）問雲端 | 地端連不到 PHZ |
| **Outbound Endpoint** | 雲端問地端 | Forwarding Rules |

使用場景：**Hybrid Cloud（混合雲）** 架構，讓地端 DNS 能解析 AWS 的 Private Hosted Zone。

### Health Checks

- 可監控 **Endpoint**，也可監控 **CloudWatch Alarm**
- **Calculated Health Checks**：組合多個檢查結果，例如「3 台 Web 死了才觸發 Failover」

---

## 七、快速排錯直覺

| 症狀 | 排查方向 |
|------|---------|
| 改了 DNS 沒生效 | 檢查 **TTL**（客戶端快取未過期） |
| 頂級網域連不上 CloudFront | 檢查是否誤用 CNAME → 改用 **Alias** |
| Failover 沒動靜 | 確認有沒有把 **Health Check 關聯到 Record** |
| 地端連不到 Private Hosted Zone | 建立 **Inbound Resolver Endpoint** |
