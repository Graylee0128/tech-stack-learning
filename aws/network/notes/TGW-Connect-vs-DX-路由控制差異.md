# TGW Connect vs Direct Connect (DX) — 路由控制與 Community Tag 差異

> 在 AWS 網路設計中，TGW Connect 與 Direct Connect (DX) 雖然都使用 BGP 協議，但它們處理「路由控制」的邏輯與 Community Tag 的應用場景截然不同。

---

## 1. Transit Gateway (TGW) Connect 的路由控制

TGW Connect 主要用於與 **SD-WAN 虛擬設備**（如 Cisco、Fortinet、Palo Alto）透過 GRE 隧道建立 BGP 鄰居關係。

### Community Tag 的角色

在 TGW Connect 中，AWS **不提供**像 DX 那樣預定義好的標準 Community Tags 來控制流量。

### 如何控制路由

- **主備模式 (Active-Passive)**：最有效率的作法是使用 **AS_PATH Prepend**。在備援設備宣告路由時增加 AS 長度，TGW 就會優先選擇路徑較短的主設備。
- **負載平衡 (ECMP)**：如果兩台設備宣告的 AS_PATH 長度相同，TGW 預設會開啟 ECMP 進行流量分擔。

> **總結**：TGW Connect 的路由偏向「標準 BGP 屬性控制」，依賴 AS_PATH 或 MED，而非特定的 Community Tag。

---

## 2. Direct Connect (DX) 的 Community Tag

與 TGW Connect 不同，AWS 為 Direct Connect 提供了豐富的**預定義 BGP Community Tags**，讓客戶能精準控制路由在 AWS 全球網路中的「傳播範圍」與「優先級」。

### 影響範圍控制 (Scope Tags)

| Community Tag | 傳播範圍 |
|---------------|---------|
| `7224:9100` | 僅在本地區域 (Local Region) 宣告路由 |
| `7224:9200` | 在同一大陸 (All Regions in a Continent) 宣告路由 |
| `7224:9300` | 全域宣告 (Global)，路由出現在 AWS 全球所有 Region |

### 優先級控制 (Preference Tags)

當你有多條 DX 連線時，可以使用以下 Tag 告訴 AWS 哪條線路是主用、哪條是備援：

| Community Tag | 優先級 |
|---------------|-------|
| `7224:7100` | Low |
| `7224:7200` | Medium |
| `7224:7300` | High |

> 這對**入向流量 (Inbound to AWS)** 的影響非常直接。

> **總結**：DX 的 Community Tag 是 AWS 定義好的「指令碼」，用來解決跨地域、跨線路的複雜選路問題。

---

## 3. 主備控制：Static Route vs AS_PATH Prepend

### 方法 A — 靜態路由控制主備 (Static Route)

在 TGW Route Table 手動寫入路由：

```
0.0.0.0/0    (default)  → Secondary
10.1.0.0/16  (specific) → Primary
10.2.0.0/16  (specific) → Primary
10.x.x.x/xx (specific) → Primary
```

**選路原則**：Longest Prefix Match — specific (`/16`) > default (`/0`)
- 正常情況 → 走 Primary
- Primary 掛掉 → 走 Secondary

**問題**：
- 每次新增網段 → 要**手動加** specific route
- Primary 掛掉時 → static route 還在 → TGW 還是嘗試送到 Primary → **不會自動 failover**

### 方法 C — 動態路由控制主備 (BGP AS_PATH Prepend)

Secondary appliance 廣播 BGP 路由時加上 AS_PATH Prepend：

```
Primary 廣播：
  10.0.0.0/8  AS_PATH: 65000           ← 路徑短，優先選

Secondary 廣播：
  10.0.0.0/8  AS_PATH: 65000 65000 65000  ← 路徑長，不優先選
```

- 正常情況 → TGW 自動選 Primary
- Primary 掛掉 → BGP 撤回路由 → TGW **自動切換** Secondary
- **完全自動，不需手動**

---

## 4. 主備 vs ECMP 概念

| 模式 | 流量分配 | 特點 |
|------|---------|------|
| **主備 (Active/Standby)** | Primary 處理所有流量，Secondary 待機 | 同時只有一台工作，Primary 掛才切換 |
| **ECMP (Active/Active)** | 兩台各處理 50% 流量 | 兩台同時工作，需要 AS_PATH 長度相同 |

> 考試中如果題目要求「主備」，選 AS_PATH Prepend；如果看到兩台 AS_PATH 長度相同，那就是 ECMP。

---

## 5. BGP 主備控制工具總覽

| 工具 | 原理 | 適用場景 | 備註 |
|------|------|---------|------|
| **Static Route** | 手動指定路徑 | 簡單環境 | 不自動 failover |
| **AS_PATH Prepend** | path 越長越不優先 | 動態 BGP 環境 | 自動收斂，需要 BGP |
| **BGP Community** | 標記路由用途 / 優先級 | 複雜路由策略 | AWS 特定標記 (`7224:XXXX`) |
| **Local Preference** | BGP 出方向優先級 | 同 AS 內部控制 | 數字越大越優先，iBGP 使用 |
| **MED (Metric)** | 建議對端選路 | 跨 AS 建議 | 數字越小越優先，對端可忽略 |

---

## 6. 核心差異對比表

| 特性 | Transit Gateway Connect | Direct Connect (DX) |
|------|------------------------|---------------------|
| **主要協議元件** | GRE Tunnel + BGP | 802.1Q VLAN + BGP |
| **Community Tag 支援** | 無官方預定義 Tag | 豐富的預定義 Tag (`7224:XXXX`) |
| **主備切換建議** | AS_PATH Prepend | Community Tags (`7224:7100-7300`) |
| **適用場景** | SD-WAN、雲端虛擬防火牆整合 | 實體機房與 AWS 專線連接 |

---

## 7. 常見考試陷阱

- **誤以為**可以使用 DX Tag（如 `7224:7300`）來控制 TGW Connect → TGW Connect 不支援這些 Tag
- **忽略 Tag 的範圍限制**導致跨 Region 路由不通 → 注意 `9100` / `9200` / `9300` 的差別
- **誤選 Static Route** 做主備 → Static Route 不會自動 failover，應選 AS_PATH Prepend
- **混淆主備與 ECMP** → AS_PATH 長度相同 = ECMP（Active/Active），不是主備
