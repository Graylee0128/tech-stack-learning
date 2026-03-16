# IDS/IPS 架構設計筆記

## 概述
VPC 網路架構設計中的流量檢測與入侵偵測系統（IDS/IPS）架構選型。特別針對大規模（數千台實例）環境下的設計模式。

---

## 📚 Inspection VPC 演進史

### 三個時代的架構演進

| 時代 | 名稱 | 特點 | 適用場景 |
|------|------|------|---------|
| **早期** | VPC Peering 時代 | 多個 Peering + 複雜路由表 | 小規模、早期系統 |
| **中期** | Transit Gateway 時代 | 所有 VPC 連到 TGW，統一向 Inspection VPC 導流 | 多帳號、數百台實例 |
| **現代** | GWLB 時代 | Gateway Load Balancer 無縫導流 | 超大規模、高可用 |

---

## 🎯 考試速查表（初級版）

### 秒殺規則

1. **看到 "Promiscuous mode"** → 直接刪掉
   - AWS VPC 基於映射（Mapping），不是傳統交換機，絕對不支援

2. **看到 "Scale to thousands" + "Security/IDS"** → 尋找
   - "Centralized"、"Second VPC" 或 "Transit Gateway" 描述

3. **看到 "Analyze all traffic"** → 現代題目可能
   - VPC Traffic Mirroring（現代中心化方案）

---

## 💡 核心決策：中心化 vs 分散式

### 為什麼大規模場景下 D (Agent-based) 被判為正確？

#### 關鍵字分析
**"Scale to thousands of instances"** 是這題的核心

#### B (中心化 Inspection VPC) 的問題

1. **吞吐量瓶頸 (Throughput Bottleneck)**
   - 所有流量經過 Peering/TGW 再進入中心防火牆
   - 防火牆頻寬上限 = 整體系統瓶頸

2. **管理複雜度**
   - VPC Route Table 控制數千台機器流向困難
   - 容易產生網路延遲

#### D (分散式 Agent-based) 的優勢

1. **真正的水平擴張 (True Horizontal Scaling)**
   - 1,000 台 EC2 = 1,000 個檢測點
   - 防禦能力隨規模線性成長，無中心化瓶頸

2. **在地化處理 (Local Processing)**
   - 在資料離開主機前進行檢測
   - 提供 OS 層面上下文（Process、檔案變動）
   - B 選項（網路層）看不到這些資訊

3. **分散式架構**
   - 符合雲端原生設計
   - 避免單點故障（SPOF）

---

## 🛡️ 更新的「IDS/IPS 題型」決策流程

### 第一步：先砍掉絕對錯誤

```
看到 "Promiscuous mode" → ❌ 秒刪
AWS VPC 不支援，絕對答案
```

### 第二步：判斷「監控方式」

| 題目強調 | 優先選項 |
|---------|--------|
| 「數千台實例」、「分散式」 | **Agent-based** |
| 「合規性」、「不改應用主機」 | **VPC Traffic Mirroring** 或 **Centralized Inspection VPC** |
| 「無伺服器」、「帳戶層級稽核」 | **Amazon GuardDuty** |

### 第三步：服務選型指南

| 監控層次 | AWS 推薦服務 | 考試關鍵字 |
|---------|-------------|----------|
| **主機層 (HIDS)** | Agent-based (如 OSSEC) | Thousands of instances, Deep visibility |
| **網路層 (NIDS)** | VPC Traffic Mirroring | Out-of-band, No agent required |
| **威脅偵測** | Amazon GuardDuty | Intelligent, Managed service |
| **應用層 (Layer 7)** | AWS WAF | SQL Injection, XSS, HTTP rules |

---

## 📊 B vs D 決策矩陣

| 比較維度 | B. 中心化 Inspection VPC | D. 分散式 Agent-based |
|---------|------------------------|----------------------|
| **擴展瓶頸** | ⚠️ 容易產生瓶頸，規模越大延遲越高 | ✅ 無瓶頸，性能線性成長 |
| **可視化深度** | 網路層（NIDS）- 只看封包 | 主機層（HIDS）- 看 Process、檔案、記憶體 |
| **適用場景** | 企業合規、強制檢查 | 超大規模、深度防護 |
| **管理難度** | ✅ 簡單（改一處規則） | ❌ 困難（數千個 Agent 版本管理） |

---

## 🎯 考試秒殺技巧

### 1. "Scale to thousands" 無中心化網關 → 選 D

```
邏輯：
- 無 TGW/GWLB → B (中心化) = 瓶頸
- 只有 Agent 才能支撐極限規模
```

### 2. 觀察檢測「深度」需求

```
❌ 要偵測 OS 內部異常 (Process、檔案修改) → D
✅ 只分析網路流量 (IP 黑名單) → B
```

### 3. 檢查「限制條件」

```
❌ 「不能在應用主機裝軟體」 → D 出局，必選 B
❌ 「不支援混雜模式」→ 提示改用 Traffic Mirroring 或 Agent
```

---

## 🚨 2024-2026 年陷阱題更新

### 如果選項出現「E. Amazon GuardDuty」

**GuardDuty 成為第一優先答案**

原因：
- ✅ 不需要安裝 Agent（D 的缺點）
- ✅ 不需要改路由（B 的缺點）
- ✅ 透過分析 VPC Flow Logs 實現
- ✅ 受管服務，AWS 原生

### 現代考試首選順序
1. **Amazon GuardDuty** ← 新時代首選
2. **VPC Traffic Mirroring + GWLB** ← 次選
3. **Agent-based** ← 特殊場景
4. **Centralized Inspection VPC** ← 傳統方案

---

## 💬 專家碎碎念

### 關於題目「時代感」

這份題目解析提到：**「直到 VPC Traffic Mirroring 出現前，Agent 是唯一解」**

這暗示：
- 題目可能反映早期 SAA (Solutions Architect Associate) 考法
- 現代考試會優先考 GuardDuty（受管服務）
- 題目年代越新，越傾向選「受管服務」而非「自建方案」

### 背後的考試邏輯

```
中心化 (B) = 管理導向（易管但難推向極限）
分散式 (D) = 效能導向（難管但能推向極限）

題目強調「Scale to thousands」= 考效能能力
→ 必選效能導向的方案
```

---

## 📌 快速檢查清單

- [ ] 題目有提到「混雜模式 (Promiscuous Mode)」嗎？ → 如是，刪掉該選項
- [ ] 題目強調「數千台實例」嗎？ → 如是，優先考慮分散式
- [ ] 題目提到「改應用主機」嗎？ → 如是，要考慮成本和可行性
- [ ] 選項有 GuardDuty 嗎？ → 如有，優先考慮它
- [ ] 題目強調「自動化、無伺服器」嗎？ → 如是，選受管服務