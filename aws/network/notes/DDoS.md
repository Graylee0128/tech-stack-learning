# AWS DDoS 防護學習筆記

## 目錄

- [一、防護核心邏輯](#一防護核心邏輯)
- [二、常見錯誤選項解析](#二常見錯誤選項解析)
- [三、正確防護策略解析](#三正確防護策略解析)
- [四、DDoS 防護最佳實務 Cheat Sheet](#四ddos-防護最佳實務-cheat-sheet)
- [五、考試專項提示](#五考試專項提示)

---

## 一、防護核心邏輯

AWS 考試中，DDoS 防護的邏輯並不是「把門鎖死」，而是：

> **「擴張門面讓它塞不進去」** + **「在最外層（Edge）擋掉垃圾流量」**

關鍵原則：**Offload to Edge** — 防護點越靠近來源端越好，絕對不能讓攻擊流量進到 VPC 或 OS 層才處理。

---

## 二、常見錯誤選項解析

| 選項 | 為何錯 |
|------|--------|
| **多個 ENI** | 頻寬跟著 Instance Type 走，不跟 ENI 數量。DDoS 流量是頻寬的幾萬倍，多幾個網卡無效 |
| **Dedicated Instances** | 只提供硬體隔離（不共用物理主機），對網路層 DDoS 完全沒有防護效果 |
| **修改 OS Firewall（iptables）** | 流量進到 OS 防火牆時，EC2 的 CPU 和頻寬已被消耗。違反 Offload to Edge 原則 |

---

## 三、正確防護策略解析

| 服務 | 防護原理 |
|------|---------|
| **CloudFront** | 全球邊緣節點內建 AWS Shield Standard；吸收 L3/L4 攻擊（如 SYN Flood）；攻擊流量根本不進 VPC |
| **ELB + Auto Scaling** | 「以量制量」；Auto Scaling 自動擴展撐住流量；ELB 過濾不完整的 TCP Handshake，只轉發有效請求 |
| **CloudWatch Alerts** | 監控 CPU 與網路流量，觸發自動化回應（更激進的 Scaling 或 WAF 規則）—「看不到的攻擊無法對抗」 |

---

## 四、DDoS 防護最佳實務 Cheat Sheet

| 防護層級 | 服務 | 功能 |
|---------|------|------|
| **最外層防禦（Edge）** | CloudFront | 擋 L3/L4 網路層攻擊 |
| | AWS WAF | 擋 L7 應用層攻擊（HTTP Flood、SQL Injection） |
| | AWS Shield Advanced | 24/7 DDoS 專家支援（DRT 團隊）+ 費用保護 |
| **分散流量** | Route 53 | Anycast 路由分散流量 |
| **彈性擴張** | ELB + ASG | 承受突發流量 |
| **縮小攻擊面** | Security Groups | 只開放必要 Port（80/443），底層直接過濾非目標流量 |

---

## 五、考試專項提示

**看到「帳單爆增」關鍵字：**
題目問「如何防止 DDoS 導致的費用暴增」→ 答案指向 **AWS Shield Advanced**。
它可申請「費用減免（Cost Protection）」，退還因 DDoS 觸發 Auto Scaling 瘋狂擴展所產生的費用。
