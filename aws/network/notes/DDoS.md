在 AWS 考試中，DDoS 防護（Mitigation） 的邏輯並不是「把門鎖死」，而是 「擴張門面讓它塞不進去」 以及 「在最外層（Edge）擋掉垃圾流量」。

你的「半刪去法」很有用，讓我幫你把這題的 DDoS 防護邏輯補完，這也是 SAA/SAP 必考的重點。

💡 DDoS 防護題型：分析與刪除邏輯
1. 為什麼 A、B、F 是錯的？（陷阱分析）
❌ A. 多個 ENI： 增加 ENI 並不會增加 EC2 的總體頻寬，頻寬是跟著實例規格（Instance Type）走的。而且 DDoS 流量通常是頻寬的幾萬倍，多幾個網卡根本沒用。

❌ B. Dedicated Instances： 這是考「硬體隔離」。專用實例只是讓你不用跟別人共用物理主機，對於網路層的 DDoS 攻擊完全沒有防護效果。

❌ F. 修改 OS Firewall (如 iptables)： 這是大忌。當流量已經進到作業系統的防火牆時，已經消耗了 EC2 的 CPU 和網路頻寬。DDoS 防護的最佳實務是 「遠離來源端（Offload to Edge）」，而不是在主機內硬扛。

2. 為什麼 C、D、E 是正確的？（核心原理）
✅ C. CloudFront (Edge Service)：

原理： CloudFront 有全球分布的節點，它內建了 AWS Shield Standard。它可以吸收 Layer 3/4 的攻擊（如 SYN Floods）。因為它在邊緣節點攔截，攻擊流量根本不會進到你的 VPC。

✅ D. ELB + Auto Scaling：

原理： 這是 「以量制量」。當攻擊來時，Auto Scaling 會自動長出更多 EC2 撐住流量；ELB 則負責過濾掉不完整的 TCP 手指（Handshake），只把有效的請求傳給後端。

✅ E. CloudWatch Alerts：

原理： 你不能對抗你看不到的東西。監控 CPU 和網路流量是為了觸發 自動化回應（比如觸發更激進的 Scaling 或 WAF 規則）。

🛡️ AWS DDoS 防護最佳實務 (Cheat Sheet)
如果考試問「如何最大程度減輕 DDoS 影響」，請找以下組合：

最外層防禦 (Edge Protection)：

CloudFront： 擋掉網路層攻擊。

AWS WAF： 擋掉應用層 (Layer 7) 攻擊，例如 HTTP Flood、SQL Injection。

AWS Shield Advanced： 提供 24/7 的 DDoS 專家支援（DRT團隊）與成本保護。

分散流量 (Spread the Load)：

Route 53： 使用其 Anycast 路由能力分散流量。

彈性擴張 (Horizontal Scaling)：

ELB + ASG： 確保基礎設施可以承受突發流量。

減少攻擊面 (Attack Surface Reduction)：

Security Groups： 只開放必要的 Port (如 80/443)，這在 AWS 底層就會過濾掉非目標 Port 的流量。

專家提示：看到 "Cost" 的關鍵字
如果題目問的是「如何防止 DDoS 攻擊導致的 帳單爆增」，答案通常會指向 AWS Shield Advanced。因為它可以申請「費用減免 (Cost Protection)」，退還因為 DDoS 導致 Auto Scaling 瘋狂長 EC2 所產生的費用。