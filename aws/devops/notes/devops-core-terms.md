# DevOps 核心術語速查：從 P99 到讀寫擴散

> 目的：把剛接觸 DevOps / SRE 時最常撞到的核心術語放進同一張地圖，先建立語感，再往 AWS、Kubernetes、可觀測性與資料系統延伸。

---

## 一句話先抓主軸

如果只用一句話概括這份筆記：

- **效能面**：系統到底有多快、多穩、多容易在尖峰時變慢？
- **可靠性面**：系統壞掉時，我們怎麼量化目標、處理事故、降低風險？
- **交付面**：我們怎麼把變更安全地部署出去？
- **資料面**：為什麼只做一次讀寫，系統背後卻可能放大成很多次操作？

---

## 1. 效能與流量（Performance）

| Term | 白話解釋 | 你應該怎麼理解 |
|------|----------|----------------|
| `Latency` | 延遲，單次請求花多久完成 | 看的是「快不快」 |
| `Percentile` | 百分位數，表示某比例請求落在某個時間內 | 比平均值更能反映真實體感 |
| `P50` | 50% 的請求比這個值更快 | 接近中位數 |
| `P90` | 90% 的請求比這個值更快 | 開始看慢請求 |
| `P99` | 99% 的請求比這個值更快 | 觀察尾延遲最常用 |
| `P999` | 99.9% 的請求比這個值更快 | 用來看更極端的慢請求 |
| `Tail Latency` | 尾延遲，少數特別慢的請求 | 常常決定使用者體感與事故風險 |
| `Throughput` | 吞吐量，單位時間處理多少工作 | 看的是「量能」 |
| `RPS / QPS` | 每秒請求數 / 每秒查詢數 | 流量大小的常見量法 |
| `Error Rate` | 錯誤率，失敗請求佔比 | 看的是「穩不穩」 |
| `Saturation` | 飽和度，資源是否接近上限 | CPU、記憶體、連線數是否快爆了 |

### 直覺記法

- `Average latency` 很容易把少數超慢請求洗掉。
- `P99` 比平均值更能看出真實使用者痛感。
- 當 `P99` 突然變差，但平均值沒什麼變，通常代表有尾部問題正在發生。

---

## 2. 可靠性與服務目標（Reliability）

| Term | 白話解釋 | 你應該怎麼理解 |
|------|----------|----------------|
| `Availability` | 可用性，系統有多少時間可正常服務 | 常見表達像 `99.9%` |
| `SLA` | Service Level Agreement，對客戶的承諾 | 偏商務與契約 |
| `SLO` | Service Level Objective，內部目標 | 例如「99% 請求在 300ms 內完成」 |
| `SLI` | Service Level Indicator，實際量測指標 | 拿來衡量 SLO 是否達標 |
| `Error Budget` | 錯誤預算，SLO 容許你失誤的空間 | 用來平衡穩定與發布速度 |
| `Incident` | 事故，影響服務可用性或品質的事件 | 不一定是完全掛掉才算 |
| `MTTR` | Mean Time To Recovery，平均修復時間 | 壞掉後多久恢復 |
| `Postmortem` | 事後復盤 | 重點是學習，不是找戰犯 |

### 例子

如果你的 `SLO` 是「99% 的請求在 1 秒內完成」，那：

- `SLI` 可以是「1 秒內完成的請求比例」
- `Error Budget` 就是剩下那 1% 的容忍空間
- 當 `P99` 持續惡化時，往往也代表你正在燃燒 `Error Budget`

---

## 3. 可觀測性與監控（Observability）

| Term | 白話解釋 | 你應該怎麼理解 |
|------|----------|----------------|
| `Observability` | 可觀測性，從外部訊號理解系統內部狀態的能力 | 不只是監控面板多，而是能定位問題 |
| `Metrics` | 指標型資料 | CPU、記憶體、RPS、P99 |
| `Logs` | 日誌 | 記錄發生了什麼事 |
| `Traces` | 追蹤 | 一次請求經過哪些服務、每段花多久 |
| `APM` | Application Performance Monitoring | 專注應用程式效能與交易路徑 |
| `Alerting` | 告警機制 | 異常發生時通知人或自動處理 |
| `Runbook` | 操作手冊 | 告警發生後怎麼處理 |

### 常見觀測框架

| Framework | 組成 | 適用場景 |
|-----------|------|----------|
| `Four Golden Signals` | `Latency` / `Traffic` / `Errors` / `Saturation` | 服務整體健康度 |
| `RED` | `Rate` / `Errors` / `Duration` | API / 微服務 |
| `USE` | `Utilization` / `Saturation` / `Errors` | 主機、磁碟、網路等資源層 |

---

## 4. 交付與部署（Delivery）

| Term | 白話解釋 | 你應該怎麼理解 |
|------|----------|----------------|
| `CI` | Continuous Integration，持續整合 | 每次提交都自動建置與測試 |
| `CD` | Continuous Delivery / Deployment | 自動把變更送往環境甚至上線 |
| `IaC` | Infrastructure as Code | 用程式碼管理基礎設施 |
| `GitOps` | 以 Git 作為部署真相來源 | Git 狀態決定環境狀態 |
| `Rolling Update` | 滾動更新 | 一批一批替換舊版本 |
| `Blue-Green Deployment` | 藍綠部署 | 維持兩套環境切換流量 |
| `Canary Release` | 金絲雀發布 | 先放少量流量驗證新版本 |
| `Rollback` | 回滾 | 新版有問題時退回上一版 |
| `Feature Flag` | 功能開關 | 不重新部署也能控功能開關 |

---

## 5. 韌性與保護機制（Resilience）

| Term | 白話解釋 | 你應該怎麼理解 |
|------|----------|----------------|
| `Retry` | 重試 | 暫時性失敗時再試一次 |
| `Timeout` | 逾時 | 不讓請求無限等待 |
| `Exponential Backoff` | 指數退避 | 每次重試間隔逐步拉長，避免打爆系統 |
| `Circuit Breaker` | 熔斷 | 下游故障時先暫停呼叫，防止連鎖雪崩 |
| `Rate Limiting` | 限流 | 控制單位時間可進來多少請求 |
| `Backpressure` | 背壓 | 下游忙不過來時，向上游施加節流 |
| `Idempotency` | 冪等 | 同樣請求重送多次，結果應一致 |

### 常見關係

- 只有 `Retry` 沒有 `Timeout`，容易把等待堆積成事故。
- 只有 `Retry` 沒有 `Backoff`，容易在高壓時把故障放大。
- 沒有 `Idempotency` 的重試，可能造成重複扣款、重複寫入、重複建立資源。

---

## 6. 資料系統與「擴散 / 放大」（Amplification）

這一組特別值得記，因為它們常常是把 `P99` 拉高的真正元凶。

| Term | 白話解釋 | 你應該怎麼理解 |
|------|----------|----------------|
| `Read Amplification` | 讀擴散，明明只讀一次，系統背後卻讀了更多資料 | 查詢變慢、IO 增加 |
| `Write Amplification` | 寫擴散，明明只寫一次，系統背後卻寫了很多次 | 寫入成本增加、SSD 壽命消耗更快 |
| `Space Amplification` | 空間擴散，占用的實體空間比邏輯資料更多 | 壓縮、副本、版本、索引都可能導致 |
| `Compaction` | 壓實 / 合併整理資料 | 常見於 LSM-tree 系統，也常帶來寫擴散 |
| `Hot Partition` | 熱分區，少數 key / shard 流量過熱 | 容易造成局部延遲飆高 |

### `Read Amplification`

一次讀請求，背後需要讀更多區塊、更多檔案、更多節點，才能把結果湊出來。

常見例子：

- 查 1 筆資料，卻要掃多個 `SSTable` 或 segment
- API 查詢背後還要串多個微服務
- Cache miss 後打到 DB，又連動索引與磁碟讀取

常見後果：

- `Latency` 變高
- `P99` 惡化
- 磁碟或網路壓力上升

### `Write Amplification`

一次寫入，背後實際寫了更多次資料。

常見例子：

- 主資料之外，還要寫 `WAL`、index、replica
- `LSM-tree` 先寫記憶體，再 flush，再 compaction 重寫
- SSD 因 erase block 機制，4KB 寫入可能觸發更大範圍搬移

常見後果：

- 寫入延遲升高
- 背景 `compaction` 增加
- SSD 壽命更快被消耗

### 快速心法

- `Read Amplification`：為了讀 1 次，系統多讀很多次
- `Write Amplification`：為了寫 1 次，系統多寫很多次
- `Space Amplification`：為了存 1 份資料，系統多佔很多空間

---

## 7. 初學者最值得先熟的術語清單

如果要先背最小集合，建議優先熟這 20 個：

- `Latency`
- `P99`
- `Tail Latency`
- `Throughput`
- `RPS`
- `Error Rate`
- `Availability`
- `SLA`
- `SLO`
- `SLI`
- `Error Budget`
- `Metrics`
- `Logs`
- `Traces`
- `CI/CD`
- `IaC`
- `Rollback`
- `Timeout`
- `Backpressure`
- `Read Amplification`

---

## 8. 一條實用學習順序

1. 先懂 `Latency`、`P99`、`Throughput`、`Error Rate`
2. 再懂 `SLA`、`SLO`、`SLI`、`Error Budget`
3. 接著補 `Metrics`、`Logs`、`Traces`、`Alerting`
4. 然後補 `CI/CD`、`IaC`、`GitOps`、`Rollback`
5. 最後把 `Retry`、`Timeout`、`Circuit Breaker`、`Backpressure`、`Read/Write Amplification` 串起來

這樣你之後不管是在看 AWS、Kubernetes、Elasticsearch、Prometheus，還是面試 DevOps / SRE，都比較不會一直被術語打斷。
