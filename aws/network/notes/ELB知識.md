# AWS ELB 知識筆記

---

## ALB vs NLB：架構師的核心選型

### 1. ALB + X-Forwarded-For：軟體層的「代領快遞」

使用 ALB 時，它就像一個高級管家。他會幫你簽收快遞（終止 TCP 連線、拆開 SSL 加密），然後再把東西轉交給你（向後端 EC2 發起新連線）。

**優點：** 它可以看懂 HTTP 內容，做「路徑轉發」（例如 `/api` 去 A 機器，`/images` 去 B 機器），還能掛載 WAF（網頁防火牆）。

**痛點：** 因為連線是管家重啟的，你的 EC2 看到的「寄件人」自然變成了管家（ALB 的 IP）。

**解決方案：** `X-Forwarded-For` 就是管家在交給你東西時，順便在盒子上面貼一張便利貼，寫著：「這是真正的客人 `1.2.3.4` 寄來的喔！」

### 2. NLB 的「透明」代價：硬體層的「暴力直通」

NLB 雖然能「保留來源 IP (Source IP Preservation)」，但它的代價很高：

**NLB 的特長：** 它操作在第四層（Layer 4）。它不拆封包，只是把封包像投籃一樣直接投給後端 EC2。後端 EC2 看到的來源 IP 真的就是客人本人。

**NLB 的代價 (Trade-off)：**
- **它看不懂網址：** 它不能根據網址路徑（如 `/login`）分流，它只認得 Port
- **無法直接掛 WAF：** 因為它不拆 HTTP 內容，所以 AWS WAF 無法擋在它前面
- **健康檢查較粗：** 因為它更底層，沒辦法做很細緻的應用程式層檢查

### 3. 實務「生存指南」比較表

| 比較維度 | ALB + X-Forwarded-For | NLB（預設狀態） |
|---------|----------------------|----------------|
| 通訊層級 | Layer 7 (HTTP/HTTPS) | Layer 4 (TCP/UDP) |
| 來源 IP 獲取 | 必須從 HTTP Header 裡撈 | 直接從網路封包裡看（透明） |
| 主要優點 | 功能強大（WAF, Path routing, OIDC） | 極高效能（百萬級併發、固定 IP） |
| 適用場景 | 絕大多數的 Web 應用 | 遊戲伺服器、金融交易、需要固定 IP 的場景 |

> 💡 在 95% 的 Web 專案中，我們寧願去改一下 Web Server 的 Log 設定來讀取 X-Forwarded-For，也不願意放棄 ALB 提供的路徑路由、SSL 卸載以及 WAF 保護。只有當你的流量大到 ALB 會喘（例如秒殺活動、或是非 HTTP 的協議），我們才會痛苦地選擇 NLB 並放棄那些「聰明」的功能。

---

## X-Forwarded-For 實務題：CloudFront → ALB → EC2

### 題型：「沒有 Console/API 權限，如何找到真實客戶 IP？」

當架構是 `CloudFront → ALB → EC2` 時，封包路徑如下：

```
真正的客戶 (1.2.3.4) → CloudFront → ALB → EC2
```

**痛點：** 對於 EC2 上的 Web Server（如 Apache 或 Nginx）來說，它看到的來源 IP 永遠是 ALB 的私有 IP。如果你直接看標準的 `access.log`，你會發現全世界的人 IP 都長得一樣。

### 解法：修改 Web Server Log Format

ALB 和 CloudFront 會把原始客戶的 IP 塞進 HTTP Header `X-Forwarded-For`。

**動作：** 修改 EC2 裡 Web Server 的設定檔（例如修改 Nginx 的 `log_format`），告訴它把 `X-Forwarded-For` 欄位也寫進 log 檔案裡。

**結果：** 在 EC2 終端機輸入 `tail -f /var/log/nginx/access.log`，就能看到隱藏在 Header 裡的真實客戶 IP。

### 干擾選項分析

| 選項 | 為什麼錯 |
|------|---------|
| ❌ Instance Metadata | Metadata 存放的是機器自己的資訊（Instance ID、Public IP），不記錄連線來源 |
| ❌ Access logs 預設就有 | 預設只記錄「前一跳（ALB）」的 IP，不改 Log Format 看不到 X-Forwarded-For |
| ❌ 換成 Classic Load Balancer | 開倒車，CLB 也支援 X-Forwarded-For，但沒理由為了查 IP 更換整個架構 |

### 考場秒殺口訣

> 只要看到「透過 Load Balancer / CDN」+「找原始客戶 IP」→ 唯一關鍵字：**X-Forwarded-For**

---

## Classic Load Balancer (CLB) 的 WAF 相容性陷阱

### 核心考點：CLB 不支援 WAF

當題目架構中出現 `ELB-Classic (CLB)` 時，任何「在 Load Balancer 上掛 WAF」的選項都是陷阱。

**原因：** AWS WAF 只支援 ALB、CloudFront、API Gateway、App Runner、Verified Access，**不支援 CLB**。

### 實務題型：EC2 + S3 + CLB + CloudFront 的安全措施

題目要求選出兩項正確的安全措施：

**正確答案：**

| 選項 | 理由 |
|------|------|
| ✅ WAF on CloudFront | CloudFront 是最前線入口，掛 WAF 可防 SQL Injection、XSS 等攻擊 |
| ✅ Restricted S3 Bucket Policy | 配合 OAC 限制只有 CloudFront 能讀取 S3，防止繞過 CDN 直接存取 |

**干擾選項：**

| 選項 | 為什麼錯 |
|------|---------|
| ❌ WAF on CLB | CLB 不支援 WAF，技術上行不通 |
| ❌ NACL blocks all ports | 等於「拔插頭」，網站完全無法運作。正確做法是只開放必要 Port（80/443） |

### 考場秒殺口訣

> - 看到 **Classic Load Balancer** → 立刻畫叉，它跟 WAF 沒緣分
> - 看到 **S3** → 直覺反應 Bucket Policy + OAC
> - 看到 **CloudFront** → 反應就是 WAF 或 HTTPS
