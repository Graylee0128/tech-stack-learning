# 混合雲 DNS 解析 (Hybrid DNS Resolution)

> 本文整理混合雲環境下，常見的 DNS 解析問題與 AWS 解決方案，特別針對考試中常見的題型與陷阱。

## 核心概念

在深入探討問題之前，先了解幾個關鍵字：

-   **Route 53 Resolver Rules**: 允許你條件性地將 DNS 查詢從你的 VPC 轉發到地端 DNS 解析器，反之亦然。
-   **BIND 伺服器**: 傳統上在地端環境中常見的開源 DNS 軟體。
-   **魔術 IP (`169.254.169.253`)**: AWS VPC 內部提供的 DNS 伺服器位址。
-   **託管化 (Managed Service)**: AWS Well-Architected 的核心精神。AWS 鼓勵用戶使用 `Route 53 Resolver` 這類雲原生服務，而非在 EC2 上自建 DNS 伺服器。

---

## 📖 楔子：為什麼「查名字」會變成惡夢？

在純地端（On-premises）時代，DNS 解析相對單純。公司機房裡的 DNS 伺服器（如 Windows AD DNS 或 Linux BIND）能解析所有內部網域（例如 `hr.corp.local`）。

當企業開始採用雲端，將應用程式部署到 AWS VPC 後，問題便浮現了。雲端資源（如資料庫）可能使用 AWS Private Hosted Zone (PHZ) 中的域名（例如 `db.aws.internal`）。這導致了所謂的 **「DNS 雙腦問題 (Split-Brain DNS)」**。

### 🚨 痛點一：地端找不到雲端

地端辦公室的電腦想存取雲端內部系統 `app.aws.internal`。查詢請求發給地端 DNS，但地端 DNS 的紀錄中並無 `.aws.internal` 網域，導致查詢失敗 (NXDOMAIN)。

### 🚨 痛點二：雲端找不到地端

反之，在 AWS VPC 內的 EC2 應用程式需要呼叫地端 ERP 系統的 API `api.corp.local`。EC2 向 VPC 內建的 DNS (`169.254.169.253`) 查詢，但 AWS 的 DNS 不認識私有的 `.corp.local` 網域，連線同樣失敗。

> **工程師的吶喊：** 「明明 Direct Connect (專線) 和 VPN 都通了，IP 也 PING 得到，為什麼就是無法用網址互相存取？！」

這就是混合雲 DNS 要解決的核心痛點：**如何讓兩個不同世界的電話簿，可以互相查閱？**

---

## 🏚️ 過去的血淚史：常見的陷阱解法

在 AWS 推出 Route 53 Resolver 之前，存在一些舊的解決方案。在考試中，這些過時的解法往往是最誘人的陷阱選項。

### 💣 陷阱 A：在 EC2 上自建 DNS Proxy (例如 BIND)

-   **對應考題選項：** `Create DNS proxy servers`
-   **做法：** 在 VPC 中啟動 EC2 實例，安裝 BIND 或其他 DNS 軟體。設定轉發規則：遇到 `.corp.local` 查詢就轉發給地端 DNS；遇到 `.aws.internal` 就轉發給 AWS 的魔術 IP。
-   **為什麼這是個坑（考點）：**
    *   **維運地獄 (Management Overhead):** 需要自行管理 EC2 的作業系統更新、安全修補。服務中斷將導致整個 VPC 解析癱瘓。
    *   **擴展性差 (Poor Scalability):** 流量增加時，需要手動設定 Auto Scaling 和 Load Balancer。
    *   **違反 AWS 哲學:** 與 AWS Well-Architected Framework 提倡的「託管化 (Managed Services)」背道而馳。

### 💣 陷阱 B：暴力修改 VPC 的 DHCP Options Set

-   **對應考題選項：** `Modify the DHCP options set by setting a custom DNS server value`
-   **做法：** 將 VPC 的 DHCP Options Set 中的 DNS 伺服器從預設的 `AmazonProvidedDNS` 改成地端 DNS 伺服器的 IP（例如 `10.0.0.53`），強迫所有 EC2 都去查詢地端 DNS。
-   **為什麼這是個致命坑（考點）：**
    *   **自廢武功:** 這會讓許多依賴 AWS 原生 DNS (`169.254.169.253`) 的功能失效。
    *   **PrivateLink (VPC Endpoints) 失效:** 當你使用 S3 或 API Gateway 的 Interface Endpoint 時，AWS 會在背景透過 DNS 將公有網址解析為 VPC 內的私有 IP。若 DNS 指向地端，此機制將完全失效，因為地端 DNS 不知道這些 AWS 內部的解析規則。

---
## ✅ 正確的解法：Route 53 Resolver

為了解決上述問題，AWS 提供了 `Route 53 Resolver` 服務，它包含以下幾個關鍵組件：

-   **Outbound Endpoint**: 扮演一個出口的角色，讓 VPC 內部的 DNS 查詢可以安全地「打出去」，轉發到地端網路的 DNS 伺服器 (例如透過 Direct Connect 或 VPN)。
-   **Inbound Endpoint**: 扮演一個入口的角色，讓地端網路的 DNS 查詢可以進入 VPC，解析 AWS 內部的域名 (例如 PHZ 中的紀錄)。
-   **Forwarding Rules (轉發規則)**: 你可以建立規則，例如：「凡是查詢 `corp.internal` 網域的請求，就透過 Outbound Endpoint 轉發。」
-   **Resource Access Manager (RAM)**: 透過 RAM，你可以將建立的轉發規則共享給組織 (AWS Organizations) 內的其他 VPC，無須重複設定，實現集中管理。

透過組合使用這些功能，即可搭建一個高可用、易於管理且符合 AWS 最佳實踐的混合雲 DNS 解析架構。
