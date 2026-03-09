# AWS 考題解析：不支援 DNS 之 IoT 流量架構設計

## 結論概要 (TL;DR)

當客戶端（如 IoT 設備、舊版應用程式）不支援 DNS 解析且需要高併發處理能力時，`Network Load Balancer (NLB)` 是官方推薦的首選架構。它能在每個可用區域 (AZ) 原生提供固定的靜態 IP (`Static IP`)，完美解決無法解析 DNS 的限制，且比疊加 `AWS Global Accelerator` 更具備成本效益。

## 核心考點與需求分析

這題在 AWS Certification 考試中，主要測驗你對 `Well-Architected Framework` 中「效能效率 (`Performance Efficiency`)」與「成本優化 (`Cost Optimization`)」 的權衡能力。

- **關鍵字 1：`IoT devices cannot support DNS resolution` (不支援 DNS 解析)**
    - **技術限制：** 設備必須連線到固定的 IP 地址。
    - **架構推論：** 不能單獨使用 `Application Load Balancer (ALB)`，因為 ALB 只提供 DNS Name，底層節點的 IP 會隨著流量動態擴縮容而改變。

- **關鍵字 2：`Millions of end users` (百萬級使用者)**
    - **技術限制：** 需要處理極高併發的網路連線。
    - **架構推論：** 必須搭配 `EC2 Auto Scaling Group (ASG)`，且入口的 Load Balancer 必須具備極高的吞吐量。`NLB` 是 L4 (`TCP/UDP`) 負載平衡器，天生適合處理百萬級別的每秒請求。

- **關鍵字 3：`MOST cost-effectively` (最高成本效益)**
    - **技術限制：** 在滿足上述兩個條件下，找出最省錢的方案。
    - **架構推論：** `AWS Global Accelerator` 雖然也能提供固定 IP，但它是計時收費加收流量費用的「進階/全球級」服務。若無「跨區域加速」需求，單用 `NLB` 最省錢。

## AWS 服務選型比較 (DNS 與 IP 特性)

| 服務名稱            | OSI 模型層級       | IP 特性                          | 適用場景與成本考量                                                                    |
| ------------------- | ------------------ | -------------------------------- | ------------------------------------------------------------------------------------- |
| **ALB**             | `Layer 7` (HTTP/HTTPS) | 動態 IP (需依賴 DNS)             | 適合 Web 應用、需要 Path-based routing。無法直接給不支援 DNS 的設備使用。             |
| **NLB**             | `Layer 4` (TCP/UDP)    | 靜態 IP (每個 AZ 給定一個 EIP)   | 適合 IoT、遊戲伺服器、極低延遲需求。原生解決無 DNS 問題，無額外固定 IP 附加費。   |
| **Global Accelerator** | `Layer 4` (Anycast)    | 全球靜態 IP (2 個 `Anycast IP`)  | 提供全球加速與跨 Region 容災。成本最高 ($0.025/hr + Data Transfer Premium)。 |

## 選項掃雷與錯誤原因分析 (Exam Trap)

### ❌ (A) 組合技：NLB 轉發給 ALB
**為何錯：** 雖然架構上可行（利用 `NLB` 拿靜態 IP，再轉給 `ALB` 做 L7 處理），但題目並沒有要求 HTTP/HTTPS 的進階路由功能。多掛一個 `ALB` 只會徒增架構複雜度與雙重 LB 的處理費用，不符合 `cost-effectively`。

### ❌ (B) 組合技：Global Accelerator + ALB
**為何錯：** `GA` 可以給固定 IP，但 `GA` 成本高昂；且後方掛 `ALB` 對於 IoT 設備的純 `TCP/UDP` 資料傳輸通常不是最佳實務。

### ✅ (C) 單一服務：NLB + EC2 ASG
**為何對：** 架構最精簡。`NLB` 直接提供靜態 IP 給 IoT 設備寫死在韌體裡，後端直接對接 `EC2 ASG` 進行運算擴展。成本最低，效能最高。

### ❌ (D) 組合技：Global Accelerator + NLB
**為何錯：** 考試常見陷阱！考生看到 "Millions of users" 容易被誤導需要 `GA` 來做加速。但題目沒有提及「全球分佈 (`Global users`)」或「跨區域高可用 (`Multi-Region`)」，使用 `GA` 屬於過度設計 (`Over-engineering`) 且違反成本效益。

## 實務落地指南 (Implementation Runbook)

如果在真實專案中你要實作這個架構，請依照以下步驟：

1.  **建立 `EC2 Auto Scaling Group (ASG)`：**
    -   準備好你的 IoT 資料處理程式的 `AMI` 或是 `Launch Template`。
    -   設定好 `Scale-out` / `Scale-in` 的政策（例如基於 CPU 使用率或 `NLB` 的 `ActiveFlowCount` 網路流量指標）。
2.  **部署 `Network Load Balancer (NLB)`：**
    -   建立 `NLB` 時，選擇 "Internal" 或 "Internet-facing"。
    -   在 Listener 設定中，將流量導向你建立的 ASG 的 Target Group。
    -   完成後，AWS 會在每個你選定的 AZ 中各分配一個彈性 IP (EIP) 給 NLB。這些就是你可以提供給 IoT 設備的固定 IP。
