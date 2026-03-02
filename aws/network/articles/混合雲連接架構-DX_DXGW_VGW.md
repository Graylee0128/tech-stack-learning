# 混合雲連接架構：為什麼是 DX → DXGW → VGW？

## 摘要

在 AWS 的混合雲架構中，**Direct Connect (DX) → Direct Connect Gateway (DXGW) → Virtual Private Gateway (VGW)** 是標準的連接路徑。本文從歷史演進、架構層次與實務限制出發，深入解釋為何採用這種三層設計，以及在面臨路由限制時應如何做出最有效率的架構決策。

---

## 一、三層架構的本質

### 1.1 架構圖解

```
Local Data Center
       ↓
   Direct Connect (DX)
   ├─ 專線物理連接
   ├─ 提供穩定的 10G/1G 頻寬
   └─ 連接點：AWS Region
       ↓
Direct Connect Gateway (DXGW)
├─ 集中管理跨區域的 DX
├─ 支援多個 DX 連接
├─ 支援多區域 (Inter-Region) 轉發
└─ 關鍵角色：「大盤商」
       ↓
Virtual Private Gateway (VGW)
├─ VPC 的虛擬門戶
├─ 與特定 VPC 關聯
├─ 配接 DXGW + 其他連接（VPN、Peering）
└─ 關鍵角色：「零售店門口」
       ↓
VPC 內的資源
（EC2、RDS、Lambda 等）
```

### 1.2 為什麼需要三層？

| 層次 | 組件 | 作用 | 好處 |
|------|------|------|------|
| **Layer 1** | Direct Connect | 物理專線 | 穩定、高頻寬、低延遲 |
| **Layer 2** | DXGW | 連接集中點 | 一條專線 → 多個 VPC（跨區域） |
| **Layer 3** | VGW | VPC 入口 | 路由隔離、多連接支援 |

---

## 二、DXGW：為何需要「大盤商」概念？

### 2.1 問題場景：多 VPC + 跨區域

**場景 1：單區域多 VPC**
```
Data Center ──DX──┬→ VPC-A (us-east-1)
             └→ VPC-B (us-east-1)
```

**場景 2：跨區域多 VPC**
```
Data Center ──DX──┬→ VPC-A (us-east-1)
             └→ VPC-C (eu-west-1)
```

在 AWS 發展史中，早期直接連接 VGW 時，**跨區域需要多條 DX**。這會導致：

- 成本高（多條 DX 線路）
- 管理複雜
- 流量效率低

### 2.2 DXGW 的解決方案

DXGW 是 AWS 在 2017 年推出的核心功能，目的是：

**一條 DX 專線 + DXGW → 支援多個 VPC（甚至跨區域）**

優勢：
- ✅ 降低 DX 線路數量
- ✅ 集中管理 BGP 路由宣告
- ✅ 支援 Virtual Interface (VIF) 隔離
- ✅ 企業級可擴展性

---

## 三、VGW：為什麼不能跳過？

### 3.1 VGW 的核心職責

**VGW = VPC 的網路邊界控制器**

```
DXGW ──BGP→ VGW ──路由表→ VPC 子網
                      ↓
                   EC2/RDS/Lambda
```

VGW 必須：

1. **接收 DXGW 的路由廣告**
   - BGP dynamic routing
   - 預設 AS_PATH / Weight 優先級

2. **注入到 VPC 路由表**
   - Propagated Routes（從 BGP 學習）
   - Static Routes（手動設定）

3. **隔離與安全**
   - 不同 VPC 的 VGW 獨立
   - Route Table Segmentation
   - 防止無意中的跨 VPC 洩露

### 3.2 為什麼不能 DXGW 直接連 VPC？

**理由 1：VPC 路由表不允許直接綁定 DXGW**
- AWS VPC 架構要求必須有「VPC Gateway」概念
- VGW 是 AWS 內唯一支援 BGP dynamic routing 的 VPC Gateway

**理由 2：DXGW 跨區域，VGW 才是本地化控制點**
```
DXGW (全球視野)
    ↓
VGW A (us-east-1 本地化)
VGW B (eu-west-1 本地化)
VGW C (ap-southeast-1 本地化)
    ↓
各自 VPC 路由表
```

**理由 3：安全性隔離**
- 不同 VPC 可能有不同的安全策略
- VGW 提供細粒度的路由過濾與 ACL

---

## 四、VPC 路由表限制與解決方案

### 4.1 關鍵限制：Propagated Routes 上限

**AWS VPC 路由表限制：**
- 透過 BGP 傳播（Propagated Routes）的動態路由數量
- **預設上限：100 條路由**
- 即使 TGW 可承載數千條，但不適用此場景

### 4.2 問題場景

你的地端路由器宣告了 **超過 100 條路由** 給 AWS，則：

```
地端路由器 ──BGP(200個路由)──→ DXGW
                                ↓
                              VGW
                                ↓
                            VPC 路由表
                          ❌ 只會收到 100 條
                             （超額被丟棄）
```

**影響：**
- 某些地端子網無法連接到 AWS
- 連接性間歇性中斷
- 除錯困難

### 4.3 最有效率的解決方案：地端路由彙總

**最佳做法：在地端路由器執行「路由彙總」(Route Summarization)**

```
原始宣告：
┌─────────────────────────────┐
│ 192.168.1.0/24              │
│ 192.168.2.0/24              │
│ 192.168.3.0/24              │
│ ... (200 條)                │
└─────────────────────────────┘
           ↓
        (彙總)
           ↓
├─ 彙總為 192.168.0.0/16
│  （Supernet）
└─ 或分層彙總
   ├─ 192.168.0.0/17
   ├─ 192.168.128.0/17
```

**優勢：**
- ✅ 減少宣告路由數量（200 → 10～20）
- ✅ 符合 VPC 100 條路由限制
- ✅ 降低 BGP 資料庫負載
- ✅ 提升轉發效率
- ✅ 最低維運成本（Operationally Efficient）

### 4.4 為什麼不用 Transit Gateway (TGW)？

有人會建議：「用 TGW 代替 DXGW，TGW 支援數千條路由啊！」

**答案：不符合題目要求**

| 選項 | 優點 | 缺點 | 何時用 |
|------|------|------|--------|
| **路由彙總** | 最小改動、低成本、即時生效 | 需要地端配置更新 | ✅ **最有效率** |
| **TGW 重新設計** | 長期更靈活、支援多帳號 | 需要重新架構、建立新 Attachment、驗證、部署時間長 | 🟡 長期演進方向 |

**關鍵結論：**

> 如果題目要求「最有效率方式（Most Operationally Efficient）」且已有 DXGW + VGW，答案是 **在地端執行路由彙總**，不是推翻重來換 TGW。

---

## 五、完整決策樹

```
需要混合雲連接
    ↓
選擇物理專線（DX）
    ↓
支援跨區域多 VPC？
├─ YES → 需要 DXGW（大盤商）
└─ NO  → 直接 DX 連 VGW（小規模）
    ↓
VPC 路由表超過 100 條？
├─ YES → 在地端執行路由彙總 (Route Summarization)
├─ NO  → 直接用 Propagated Routes
└─ MAYBE TGW → 長期演進（非短期解決方案）
    ↓
配置完成
```

---

## 六、實務總結

### 6.1 DX → DXGW → VGW 的適用場景

**何時應該採用這個架構：**

- ✅ 多個 VPC（同區域或跨區域）
- ✅ 需要穩定的地端連接
- ✅ 對延遲敏感（DX 優於 VPN）
- ✅ 企業級 SLA 要求
- ✅ 地端路由較簡單（< 100 條）

### 6.2 核心設計原則

1. **分層設計**
   - DX = 物理層（頻寬、延遲）
   - DXGW = 邏輯層（跨區域轉發）
   - VGW = VPC 本地化（安全隔離）

2. **路由管理**
   - 優先使用 BGP dynamic routing
   - 地端執行路由彙總以符合 VPC 限制
   - 定期監控 Propagated Routes 數量

3. **可靠性**
   - 多條 DX 冗餘（主備或 ECMP）
   - BGP AS_PATH Prepending 做 failover
   - Route 53 Health Check 監控可用性

### 6.3 給架構師的一句話

> **DX 是管道，DXGW 是交換機，VGW 是門戶。三層分工清晰，彙總是解決過多路由的最優雅方案。**

---

## 七、相關延伸閱讀

- 《AWS Direct Connect 設計模式與故障排查》
- 《VPC 路由表最佳實踐》
- 《BGP 動態路由在 AWS 混合雲的應用》
- 《Transit Gateway vs DXGW 架構選型指南》
