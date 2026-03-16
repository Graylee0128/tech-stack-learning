在 CloudFront 的世界裡，一次完整的網頁存取其實是**「兩段獨立的旅程」**。身為架構師，你就像是保全主管，必須分別為「前門」和「後門」設定安檢規則。

我們馬上進入這兩個名詞的深度解析：

1. 【情境掃描】（兩段式連線架構）
當使用者瀏覽你的網站時，流量路徑是這樣的：
User (Viewer)  ==[段落 A]==>  CloudFront (Edge Location)  ==[段落 B]==>  Origin (S3 / EC2 / ALB)

段落 A (前門)： 由 VPP (Viewer Protocol Policy) 管控。

段落 B (後門)： 由 OPP (Origin Protocol Policy) 管控。

2. 【核心名詞拆解】
🚪 前門：VPP (Viewer Protocol Policy)
這是用來規定**「使用者（瀏覽器）可以用什麼方式連到 CloudFront」**。
在 AWS Console 中，你有三個選項：

HTTP and HTTPS：來者不拒，用什麼協議來都可以。（通常不建議，因為不安全）

Redirect HTTP to HTTPS：（官方強烈推薦實務）如果使用者笨笨地打 http://，CloudFront 會回傳 301 轉向，強迫他用 https:// 重連。

HTTPS Only：非常嚴格，如果用 HTTP 連進來，直接拒絕（回傳 403 錯誤）。

🚪 後門：OPP (Origin Protocol Policy)
這是用來規定**「CloudFront 抓資料時，要用什麼方式連回你的來源伺服器 (Origin)」。
如果是自訂來源 (Custom Origin)**，例如 EC2、ALB 或「S3 靜態網站端點」，你一樣有三個選項：

HTTP Only：不管使用者怎麼連，CloudFront 一律降級用 HTTP 去後端抓資料。

HTTPS Only：不管使用者怎麼連，CloudFront 一律用 HTTPS 去後端抓資料（前提是你的後端要有 SSL 憑證）。

Match Viewer：跟屁蟲模式。使用者用 HTTP，CloudFront 就用 HTTP 去後端；使用者用 HTTPS，CloudFront 就用 HTTPS 去後端。

3. 【考試大魔王：S3 來源的特殊硬性規定】
現在，我們把 VPP 和 OPP 的概念套回上一題。為什麼上一題的官方解析會說：「如果要 CloudFront 到 S3 走 HTTPS，你必須去改 VPP」？

這是因為 AWS 針對 S3 REST API 來源（也就是你直接在下拉選單選的那個 bucket.s3.amazonaws.com）有一個強制的底層設計：

⚠️ 專家筆記：
當 Origin 是 S3 REST API 時，AWS 不允許你手動設定 OPP。CloudFront 的底層邏輯被鎖死在 「Match Viewer（跟隨使用者）」。

邏輯推演如下：

目標： 你想要「後門 (CF 到 S3)」絕對安全（走 HTTPS）。

阻礙： 你不能直接改 OPP，因為它被鎖定在「Match Viewer」。

解法： 既然它會「跟隨」前門，那你只要把「前門 (VPP)」強制設定為 Redirect HTTP to HTTPS 或 HTTPS Only，那麼前門進來的流量 100% 都是 HTTPS，後門自然就 100% 是 HTTPS 了！

這就是前一題選項 D 成為正確答案的原因：「牽一髮（前門）而動全身（後門）」。

4. 【另一個陷阱：S3 靜態網站端點】
如果你在 CloudFront 的來源填的是 S3 Website Endpoint（例如 bucket.s3-website-us-east-1.amazonaws.com），AWS 會把它當作 Custom Origin（自訂來源） 來處理。

這時候，選項就解鎖了，你可以手動設定 OPP。但是！千萬別掉進陷阱：

S3 靜態網站端點「不支援 HTTPS」。

如果你傻傻地把 OPP 設成 HTTPS Only，或者設成 Match Viewer 且使用者剛好用 HTTPS 連線...

結果： CloudFront 會嘗試用 HTTPS 連接 S3 網站端點，然後連線失敗，使用者會看到 502 Bad Gateway。

💡 實務落地總結（架構師的 Checklist）
下次你在設計 CloudFront + S3 架構時，請照著這樣做：

來源選擇： 盡量選 S3 REST API 端點（配合 OAC/OAI 鎖住權限）。

VPP 設定 (前門)： 永遠選 Redirect HTTP to HTTPS。這樣對使用者的體驗最好（不用自己手打 https），同時又保證了安全性。

OPP 設定 (後門)： 如果是 S3 REST API，你不用管（它會自動變成 HTTPS）；如果是 ALB 或 EC2，請確保後端有憑證，並設為 HTTPS Only 或 Match Viewer。