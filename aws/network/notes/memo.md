# AWS ANS-C01 認證備考筆記

---

## 📚 Level 1：基礎概念（必讀）

### 1.1 四大核心服務與考試占比

在 ANS-C01 考試中，以下四項服務的出現頻率最高，精通這四項可拿到約 **55% 的分數基礎**：

| 服務 | 占比 | 核心考點 |
|------|------|--------|
| **Connectivity** (DX / VPN / DXGW) | ~25% | BGP 路由優先級（AS_PATH）、高可用備援（Failover）、加密傳輸（MACsec / IPsec） |
| **Routing & Architecture** (TGW) | ~20% | 多帳號連網、路由表隔離（Segmentation）、Appliance Mode、與 DXGW 搭配 |
| **Name Resolution** (Route 53 Resolver) | ~10% | 地查雲 / 雲查地雙向解析、跨帳號共享 Resolver Rules |
| **其他** (安全、自動化、監控) | ~45% | 分散在各個領域 |

### 1.2 基礎排錯三層檢查法

**記住：當看到「不通」，按以下順序檢查：**

| 層級 | 檢查項目 | 例子 |
|------|--------|------|
| **Layer 3 (Routing)** | 路由表有沒有寫目標 Gateway？ | 是否有到目標 CIDR 的路由？ |
| **Layer 4 (Security)** | SG/NACL 是否放行對應 Port/Protocol？ | UDP 53 (DNS) 是否被擋住？ |
| **Layer 7 (App/DNS)** | 解析是否正確？ | DNS 是否有跨雲同步？ |

**常見基礎問題示例：**
- ✅ 能 Ping IP 但不能 Ping 域名 → 檢查 UDP 53 (DNS) 是否被 Security Group 擋住
- ✅ 10G 頻寬且最低維運成本 → Direct Connect + MACsec
- ✅ 1G DX 燈不亮 → Disable Auto-negotiation；手動鎖死速率與雙工

---

## 📚 Level 2：中級場景與配置

### 2.1 故障排查邏輯鏈

**當題目看到「流量傳不過去」時，按順序檢查：**

#### 問題 1：有沒有 Transitive 限制？
- **症狀**：VPC <-> VPC <-> VPC (Peering) 無法通信
- **原因**：VPC Peering 不支援跨越
- **解決方案**：改用 **Transit Gateway (TGW)**

#### 問題 2：路通了，但連線會斷？
- **症狀**：間歇性連接中斷
- **原因**：中間有跨 AZ 的防火牆（Appliance）
- **解決方案**：在 TGW Attachment 開啟 **Appliance Mode**

#### 問題 3：路通了，但名字解不出來？
- **症狀**：IP 連通，但 DNS 解析失敗
- **原因**：DNS 沒有跨雲同步
- **解決方案**：用 **Route 53 Resolver (Inbound/Outbound)**

### 2.2 路由優先順序 (BGP & LPM)

| 場景 | 解決方案 | 說明 |
|------|--------|------|
| **建立 Active/Passive 備援** | AS Path Prepending (增加路徑長度) | BGP 會選擇 AS Path 最短的路由 |
| **路由表網段衝突** | Longest Prefix Match (LPM) | /24 > /16（網段遮罩越長越優先） |

### 2.3 負載平衡與可用性

| 問題 | 原因 | 解決方案 |
|------|------|--------|
| **NLB 流量不進新 AZ** | NLB 本身未在該 AZ 啟用 | 檢查 NLB Subnet Mapping |

---

## 📚 Level 3：高級監控與最佳實踐

### 3.1 監控類題目的四大套路

**當題目提到「監控」，先問自己：「監控什麼？」**

#### 1️⃣ 監控「流量 / 性能」
- **關鍵詞**：bandwidth, latency, throughput
- **服務選型**：
  - VPC Flow Logs → 流量分析
  - CloudWatch Metrics → 性能指標
  - AWS Network Manager → 網絡可視化
- **例子**：監控 DX 的吞吐 → **CloudWatch Metrics**

#### 2️⃣ 監控「路由變化」
- **關鍵詞**：route advertised, BGP change, routing update
- **服務選型**：
  - Transit Gateway Network Manager → 路由事件
  - CloudWatch Logs + EventBridge → 事件觸發
  - Route 53 Health Check → DNS 健康
- **例子**：每次新路由廣告要通知 → **TGW Network Manager + EventBridge**

#### 3️⃣ 監控「安全 / 攻擊」
- **關鍵詞**：DDoS, SYN flood, intrusion, anomaly
- **服務選型**：
  - AWS Shield → DDoS 防護
  - Network Firewall Logs → 防火牆日誌
  - VPC Flow Logs → 異常流量檢測
- **例子**：檢測異常流量 → **VPC Flow Logs + CloudWatch**

#### 4️⃣ 監控「連接狀態」
- **關鍵詞**：connection, availability, failover, health check
- **服務選型**：
  - Route 53 Health Check → DNS 健康檢查
  - ELB Health Check → 負載均衡器健康
  - VPC Reachability Analyzer → 可達性檢查
- **例子**：檢測 DX 連接可用性 → **Route 53 Health Check**

### 3.2 監控快速判斷樹

```
題目提「監控」
        ↓
    問：「監控啥？」
        ↓
    ┌────┬────┬────┬────┐
    ↓    ↓    ↓    ↓
  流量  路由  安全  連接
    ↓    ↓    ↓    ↓
   VPC  TGW  Shield  Route53
  Flow  NetMgr  FW  Health
  Logs + CW + EventBridge Check
```

**核心速記：**
- 流量 → VPC Flow Logs + CloudWatch
- 路由 → Transit Gateway Network Manager + EventBridge
- 安全 → Shield + Network Firewall Logs
- 連接 → Route 53 Health Check + Reachability Analyzer

### 3.3 AWS 安全與合規：關鍵字對應表

| 關鍵字 | 對應服務 |
|--------|---------|
| OS Package Vulnerabilities / CVE | Amazon Inspector |
| Sensitive Data in S3 (PII) | AWS Macie |
| DDoS Protection (L3/L4) | AWS Shield |
| Application Layer Attacks (SQLi/XSS) | AWS WAF |
| Governance & Compliance Auditing | AWS Audit Manager |

---

## 🎯 Level 4：考試衝刺（高頻考點總結）

### 4.1 高頻題目速查表

| 題目類別 | 關鍵情境 | 反射答案 / 關鍵字 |
|---------|---------|------------------|
| 混合雲監控 | 監控 DX 傳過來的新路由 | Transit Gateway Network Manager + EventBridge |
| 傳輸加密 | 10G 頻寬且最低維運成本 | Direct Connect + MACsec |
| 基礎排錯 | 能 Ping IP 但不能 Ping 域名 | 檢查 UDP 53 (DNS) 是否被 SG 擋住 |
| BGP 選路 | 建立 Active/Passive 備援 | AS Path Prepending (增加路徑長度) |
| 路由優先 | 路由表網段衝突 | Longest Prefix Match (LPM)：/24 > /16 |
| 負載平衡 | NLB 流量不進新 AZ | 檢查 NLB Subnet Mapping |
| 物理層 | 1G DX 燈不亮 | Disable Auto-negotiation；手動鎖死速率 |

### 4.2 VPC Peering 陷阱速記（三大限制）

**在 ANS 考試中，看到 Peering，請反射檢查這三點：**

| 限制名稱 | 說明 | 例子 | 對策 |
|---------|------|------|------|
| **不可傳遞** (No Transitive) | VPC A ↔ B ↔ C，A 無法到 C | VPC Peering 鏈接無法跨越 | 改用 **Transit Gateway (TGW)** |
| **不可重疊** (No Overlapping) | 兩邊網段相同無法 Peer | VPC A 10.0.0.0/16 ↔ VPC B 10.0.0.0/16 | 改用 **PrivateLink** |
| **邊緣限制** (Edge to Edge Limitation) | 地端通過 VPN 無法再走 Peering 跨 VPC | On-Premises ──VPN→ VPC A ──Peering→ VPC B（❌ 不通） | 改用 **Transit Gateway** 或 **MPLS VPN** |

**核心記憶：** 任何 Peering 的「轉接」問題，答案都是 **Transit Gateway**！

### 4.3 專家備考建議

**你的強項與改進方向：**
- ✅ 強項：S3/Athena 分析、MACsec 直覺良好
- ⚠️ 需加強：底層協議（Protocol 50, UDP 67/68 等）

**最核心的考點：**
- **Domain 1 (Network Design)** 最核心：Transit Gateway (TGW) 的多路由表 (Route Table Propagation/Association)
- **VPC Peering 考點**：Transitive / Overlapping / Edge-to-Edge 三大限制務必記住
- **備考重點**：把「故障排查邏輯鏈」（問題 1、2、3）背熟，這是解題的黃金鑰匙