# AWS WAF 學習筆記

## 概述
AWS Web Application Firewall (WAF) 的支援服務和整合方式。WAF 是部署在流量入口的防禦層，用於阻擋常見的網頁攻擊（SQL Injection、XSS 等）。

---

## 🛡️ AWS WAF 的「守護對象」清單

AWS WAF 的設計初衷是擋在「**流量入口**」的前面。在 AWS 的世界裡，它主要跟以下服務整合：

### ✅ 支援 WAF 的 AWS 服務

| 服務 | 部署位置 | 用途 | 常見度 |
|------|--------|------|--------|
| **Amazon CloudFront** | 全球邊緣節點（Edge Locations） | CDN 層的請求過濾 | ⭐⭐⭐⭐⭐ |
| **Application Load Balancer (ALB)** | VPC 內部 | 應用程式層入口防護 | ⭐⭐⭐⭐⭐ |
| **Amazon API Gateway** | API 層 | REST/HTTP API 保護 | ⭐⭐⭐⭐ |
| **AWS AppSync** | GraphQL 層 | GraphQL 查詢保護 | ⭐⭐⭐ |
| **Amazon Cognito** | 身份驗證層 | 登入介面保護 | ⭐⭐⭐ |

---

## 📊 重點服務詳解

### A. Amazon CloudFront
```
最常見用法
流量來源 → CloudFront (邊緣節點) ← WAF 守衛
          ↓
         源站 (Origin)
```

**優勢：**
- 全球邊緣節點就先過濾惡意流量
- 保護源站不被攻擊淹沒
- 最經濟的防禦位置

**應用場景：** 對外公開的網站、內容分發、DDoS 防禦

### C. Application Load Balancer (ALB)
```
內部應用保護
VPC 内
客戶端 → ALB ← WAF 守衛 → 後端應用
```

**優勢：**
- 保護 VPC 內部的應用層
- 精確的路由和規則定義
- 與應用直接整合

**應用場景：** 微服務架構、多個後端應用、複雜的流量路由

---

## ❌ 為什麼 B 和 D 不對？

### B. AWS Lambda（不支援）

```
❌ 不能直接掛 WAF
Lambda 沒有直接與 WAF 對接的介面
```

**正確做法：**
```
Lambda
  ↑
API Gateway (或 ALB) ← 掛 WAF
  ↑
客戶端
```

**解釋：**
- Lambda 本身是無伺服器計算，沒有「入口」的概念
- 必須透過 ALB 或 API Gateway 作為流量中介
- WAF 才能掛在中介服務上，不是直接掛 Lambda

### D. AWS Classic Load Balancer (CLB)（不支援）

```
❌ 歷史遺留產物
AWS 沒有開發 CLB + WAF 整合功能
```

**為什麼被淘汰？**
- CLB 是舊時代的負載均衡器
- 功能較弱，AWS 推薦升級到 ALB
- 官方優先為新型 LB（ALB、NLB）開發新功能

**官方建議：** 如果還在用 CLB + 需要 WAF → **升級到 ALB**

---

## 💡 考場秒殺心法

### 快速判斷「WAF 支援嗎？」

#### 黃金法則
```
WAF 只跟「有門牌號碼的入口」整合
```

#### 三大入口（必背）

| 入口 | 服務名 | 記憶點 |
|------|-------|-------|
| **全球入口** | CloudFront | 邊緣節點、CDN |
| **應用程式入口** | ALB | 應用層、VPC |
| **API 入口** | API Gateway | REST API、無伺服器 |

#### 絕對錯誤的選項

```
❌ Lambda - 無伺服器計算，沒有入口
❌ CLB - 舊型負載均衡器，被淘汰
❌ EC2 - WAF 不掛在單個 EC2，掛在 ALB
❌ RDS - 資料庫層，在 WAF 後面
❌ S3 - 物件存儲，WAF 通常沒用（但 CloudFront + S3 例外）
```

---

## 🎯 考試應對策略

### 單選題判斷流程

```
1️⃣ 題目說「應用層防護」？
   → 考慮 CloudFront 或 ALB

2️⃣ 題目說「API 保護」？
   → API Gateway 優先

3️⃣ 題目說「Lambda 後面」？
   → 需要 ALB 或 API Gateway 中介

4️⃣ 題目提到 CLB？
   → 可能是干擾項或需要升級

5️⃣ 題目提到無伺服器（Serverless）？
   → API Gateway + WAF 組合
```

### 多選題判斷流程

```
✅ CloudFront 可以跟 WAF？ - YES
✅ ALB 可以跟 WAF？ - YES
✅ API Gateway 可以跟 WAF？ - YES
❌ Lambda 直接跟 WAF？ - NO
❌ CLB 跟 WAF？ - NO
```

---

## 📌 快速檢查清單

- [ ] 題目問「哪些服務支援 WAF」？ → CloudFront、ALB、API Gateway、AppSync、Cognito
- [ ] 題目提到 Lambda 要用 WAF？ → 需要 ALB 或 API Gateway 中介
- [ ] 題目提到 CLB？ → 可能是考 WAF 不支援或需要升級
- [ ] 題目強調「邊緣層防護」？ → CloudFront + WAF
- [ ] 題目強調「應用層防護」？ → ALB + WAF

---

## 💬 補充說明

### WAF 規則的常見條件

WAF 可以基於以下條件阻擋請求：

```
- SQL Injection（SQL 隱碼攻擊）
- Cross-Site Scripting (XSS)
- IP 黑名單/白名單
- 地理位置限制
- Rate Limiting（速率限制）
- Bot 保護
- 自訂條件（Regular Expression）
```

### WAF vs Shield vs GuardDuty

| 服務 | 防禦層 | 防禦對象 | 方式 |
|------|-------|--------|------|
| **WAF** | 應用層 (L7) | Web 應用 | 規則引擎 |
| **Shield** | 傳輸層 (L3/L4) | DDoS 攻擊 | AWS 托管 |
| **GuardDuty** | 檢測層 | 異常行為 | AI/ML 分析 |