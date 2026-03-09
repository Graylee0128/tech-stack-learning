# Transit Gateway Hub-and-Spoke 架構設計模式

## 概述

當 AWS 環境成長到多個 VPC 時，點對點的 VPC Peering 會迅速失控——10 個 VPC 互通需要 45 條連線 (N*(N-1)/2)，20 個 VPC 則需要 190 條。Transit Gateway (TGW) 以中央路由器的角色取代這種網狀拓撲，所有 VPC 作為 Spoke 連接到 Hub，路由集中管理。

根據安全性和隔離需求的不同，TGW 架構主要分為兩大設計模式。

---

## 核心概念：Association 與 Propagation

在理解兩大模式之前，必須先掌握 TGW Route Table 的兩個關鍵機制：

| 機制 | 意義 | 類比 |
|------|------|------|
| **Association（關聯）** | 決定「誰查閱這張路由表」——流量從哪個 Attachment 進入時，使用哪張路由表做轉發決策 | 「誰拿到這本地圖」 |
| **Propagation（傳播）** | 決定「路由表裡有誰的路徑」——哪些 Attachment 的 CIDR 會被自動寫入路由表 | 「地圖上畫了誰的位置」 |

**設計邏輯：** 透過控制「誰看哪張表」和「表裡有誰」，就能精準控制不同 VPC 之間的可達性。

---

## 模式一：一般 Hub-and-Spoke（Full Mesh / 互通型）

### 痛點與適用情境

**解決的問題：**

```
傳統 VPC Peering 的困境：

  VPC-A ←──→ VPC-B
    ↕    ╲  ╱    ↕
  VPC-C ←──→ VPC-D
    ↕    ╱  ╲    ↕
  VPC-E ←──→ VPC-F

  6 個 VPC = 15 條 Peering
  10 個 VPC = 45 條 Peering
  20 個 VPC = 190 條 Peering

  問題：
  - 拓撲像一團亂麻，極難維護
  - 每新增一個 VPC 要手動建立 N-1 條 Peering
  - 路由表分散，無法集中管控
  - 每個 VPC 若要連回地端，各需獨立 VPN/DX
```

**適用情境：**
- 同一組織內部的微服務架構，各 VPC 間需要自由通訊
- 新創公司或單一部門的內部系統
- 高度信任的環境，無嚴格的網路隔離合規要求
- 開發/測試環境中，團隊需要快速互通

### 架構設計：單一路由表

```
                    ┌─────────────────┐
                    │  Transit Gateway │
                    │  ┌────────────┐ │
                    │  │ 路由表（1張）│ │
                    │  │            │ │
                    │  │ All ← Assoc│ │
                    │  │ All ← Prop │ │
                    │  └────────────┘ │
                    └──┬──┬──┬──┬──┬──┘
                       │  │  │  │  │
            ┌──────────┘  │  │  │  └──────────┐
            ↓             ↓  ↓  ↓             ↓
         VPC-A         VPC-B VPC-C         VPN/DX
      (App Team 1)  (App Team 2)(Shared)   (地端)
```

| 設定項目 | 配置 |
|---------|------|
| **路由表數量** | 1 張 |
| **Association** | 所有 Attachment（全部 VPC + VPN/DX） |
| **Propagation** | 所有 Attachment（全部 VPC + VPN/DX） |
| **結果** | Any-to-Any，完全互通 |

### 優勢與限制

| 優勢 | 限制 |
|------|------|
| 架構最簡單，維運負擔最低 | 無法阻止 Spoke 間的橫向移動 |
| 新增 VPC 只需建立 1 個 Attachment | 不符合嚴格的網路隔離合規 |
| 路由自動傳播，無需手動維護 | 爆炸半徑大——一個 VPC 被攻破可能波及全網 |

---

## 模式二：Isolated Spoke（隔離型）

### 痛點與適用情境

**解決的問題：**

```
互通型架構的安全隱患：

  駭客攻破 Dev VPC
       ↓
  透過 TGW 路由，直接橫向移動到 Prod VPC
       ↓
  存取生產資料庫、竊取客戶資料

  這就是「橫向移動 (Lateral Movement)」攻擊——
  在互通型架構中，一旦突破邊界，攻擊者可以自由穿越所有 VPC。
```

**核心矛盾：**
- VPC 之間必須嚴格隔離（Dev 不能碰 Prod）
- 但所有 VPC 都需要存取共用基礎設施（AD 伺服器、DNS、地端專線）
- 需要在「隔離」與「共用」之間找到平衡

**適用情境：**
- 多環境分離（Dev / QA / Staging / Prod）
- 多租戶架構（不同客戶/部門的工作負載）
- 金融、醫療等受監管產業的合規要求
- PCI DSS、HIPAA 等標準要求的網路分段

### 架構設計：雙路由表

```
                    ┌──────────────────────────┐
                    │      Transit Gateway      │
                    │                           │
                    │  ┌──────────┐ ┌─────────┐│
                    │  │Spoke 路由表│ │Hub 路由表││
                    │  │(受限視界) │ │(全域視界)││
                    │  │          │ │         ││
                    │  │Assoc:    │ │Assoc:   ││
                    │  │ App VPCs │ │ Shared  ││
                    │  │          │ │ VPN/DX  ││
                    │  │Prop:     │ │         ││
                    │  │ Shared   │ │Prop:    ││
                    │  │ VPN/DX   │ │ All App ││
                    │  │          │ │ VPCs    ││
                    │  └──────────┘ └─────────┘│
                    └──┬──┬──┬────────┬──┬─────┘
                       │  │  │        │  │
            ┌──────────┘  │  │        │  └──────┐
            ↓             ↓  ↓        ↓         ↓
         App VPC-A    App VPC-B   Shared     VPN/DX
         (Dev)        (Prod)      Services   (地端)
            │             │          ↑          ↑
            │             │          │          │
            └─────────────┴──────────┘──────────┘
              只能看到 Hub，看不到彼此
```

**Spoke 路由表（受限視界）：**

| 設定項目 | 配置 |
|---------|------|
| **Association** | 所有 App VPCs |
| **Propagation** | 僅 Shared Services + VPN/DX |
| **結果** | Spoke 只能看到 Hub，互相看不見 |

**Hub 路由表（全域視界）：**

| 設定項目 | 配置 |
|---------|------|
| **Association** | Shared Services + VPN/DX |
| **Propagation** | 所有 App VPCs |
| **結果** | Hub 可以將回應精準送回任何 Spoke |

### 為什麼是「2 張表」而不是更多？

關鍵在於**需求分組**：

```
判斷邏輯：

  需要隔離嗎？
    ├─ 否 → 1 張表（Full Mesh）
    └─ 是 → Hub 端成員的需求是否一致？
              ├─ 是（VPN 和 Shared 都要跟所有 App 互通）
              │   → 2 張表（Spoke 一張 + Hub 一張）
              └─ 否（例如 VPN 不能存取 Shared Services）
                  → 3 張表或更多
```

所有 Spoke 的「視界」相同（只能看 Hub），所以共用一張表。Hub 端的 Shared Services 和 VPN 需求一致（都要能回傳給所有 Spoke），也共用一張表。

### 回程路由如何運作

```
完整的請求-回應流程：

  1. App VPC-A (10.1.0.0/16) 發送請求到 Shared Services (10.0.0.0/16)
     → App VPC-A 查閱 Spoke 路由表
     → 找到 10.0.0.0/16 (Shared Services 的傳播路由)
     → 轉發到 Shared Services

  2. Shared Services 回應給 App VPC-A
     → Shared Services 查閱 Hub 路由表
     → 找到 10.1.0.0/16 (App VPC-A 的傳播路由)
     → 精準回傳給 App VPC-A（而非 VPC-B）
```

---

## 進階模式：Centralized Inspection（集中檢測型）

### 痛點與適用情境

**解決的問題：**

即使在 Isolated Spoke 模式下，Spoke 與 Hub 之間的流量仍然是「直通」的，缺乏深度封包檢測（DPI）。對於需要 IDS/IPS、URL 過濾、威脅情報整合的組織，需要在 TGW 路由中插入一個 Inspection 層。

**適用情境：**
- 需要集中式 IDS/IPS 和 DPI
- 合規要求所有跨 VPC 流量必須經過安全檢測
- 需要統一的出站流量過濾（Centralized Egress）

### 傳統架構：Inspection VPC（2025 年 7 月前）

```
                    ┌──────────────────────────────┐
                    │        Transit Gateway        │
                    │                               │
                    │  ┌────────┐ ┌──────┐ ┌──────┐│
                    │  │Spoke RT│ │Insp RT│ │Hub RT││
                    │  └────────┘ └──────┘ └──────┘│
                    └──┬──┬────────┬────────┬──┬───┘
                       │  │        │        │  │
            ┌──────────┘  │        │        │  └────┐
            ↓             ↓        ↓        ↓       ↓
         App VPC-A    App VPC-B  Inspection  Shared  VPN
                                   VPC       Svc
                                    │
                              AWS Network
                               Firewall
```

這種模式需要：
- 獨立的 Inspection VPC 和專用子網
- 額外的路由表管理（至少 3 張）
- 手動處理跨 AZ 流量的對稱路由

### 新架構：Network Firewall Native TGW 整合（2025 年 7 月後）

2025 年 7 月，AWS 推出 **Network Firewall Native Transit Gateway Support**，大幅簡化了檢測架構：

```
                    ┌──────────────────────────────┐
                    │        Transit Gateway        │
                    │                               │
                    │  ┌────────┐       ┌─────────┐│
                    │  │Spoke RT│       │ Hub RT  ││
                    │  └────────┘       └─────────┘│
                    │        │    ┌──────┐    │     │
                    │        └──→│ NFW  │←───┘     │
                    │            │ 直接  │          │
                    │            │ 掛載  │          │
                    │            └──────┘          │
                    └──┬──┬──────────────┬──┬──────┘
                       │  │              │  │
            ┌──────────┘  │              │  └──────┐
            ↓             ↓              ↓         ↓
         App VPC-A    App VPC-B      Shared     VPN/DX
                                     Services
```

**改進之處：**

| 傳統 Inspection VPC | Native TGW 整合 |
|---------------------|------------------|
| 需要獨立的 Inspection VPC | 直接掛載到 TGW，無需額外 VPC |
| 手動管理子網和路由表 | 自動多 AZ 冗餘 |
| 至少 3 張路由表 | 路由配置大幅簡化 |
| 成本較高（需維護 VPC 和 NAT） | 支援彈性成本分攤（跨帳號計費） |

---

## 進階模式：Centralized Egress（集中出站）

### 痛點與適用情境

**解決的問題：**

```
每個 VPC 獨立出站的成本：

  VPC-A → NAT GW → IGW → Internet    ($32/月)
  VPC-B → NAT GW → IGW → Internet    ($32/月)
  VPC-C → NAT GW → IGW → Internet    ($32/月)
  ...
  10 個 VPC = $320/月（僅 NAT Gateway）

集中出站：
  All VPCs → TGW → Egress VPC → NAT GW → IGW → Internet
  1 個 Egress VPC = $32/月（節省 90%）
```

### 架構設計

```
                    ┌──────────────────────┐
                    │   Transit Gateway    │
                    └──┬──┬──┬──┬──┬──────┘
                       │  │  │  │  │
            ┌──────────┘  │  │  │  └──────────┐
            ↓             ↓  ↓  ↓             ↓
         App VPC-A    App VPC-B  App VPC-C   Egress VPC
                                               │
                                          ┌────┴────┐
                                          │ NAT GW  │
                                          │ (共用)   │
                                          └────┬────┘
                                               │
                                            Internet
```

**關鍵配置：**
- Spoke 路由表：預設路由 `0.0.0.0/0` 指向 Egress VPC
- Egress VPC 路由表：通過 NAT Gateway 出站
- Egress VPC 的 TGW Attachment 子網需要回程路由指向 TGW

**可與 Isolated Spoke 模式結合：** Spoke 之間仍然隔離，但共用 Egress VPC 出站，兼顧安全與成本。

---

## 架構演進路徑：TGW → Cloud WAN

### 何時該考慮 Cloud WAN

| 維度 | Transit Gateway | Cloud WAN |
|------|----------------|-----------|
| **範圍** | 單一 Region | 全球多 Region |
| **跨 Region** | 需手動建立 TGW Peering | 內建自動化跨 Region 連線 |
| **路由管理** | 手動設定路由表和傳播 | 集中策略定義，自動下發 |
| **分段隔離** | 透過路由表實現 | 原生 Segment 概念 |
| **監控** | 需自行整合 CloudWatch | 內建效能監控和儀表板 |
| **適用規模** | 少數 Region，< 50 VPCs | 多 Region，大規模全球網路 |
| **成本** | 較低（按 Attachment 計費） | 較高（額外管理費用） |

### 遷移路徑

```
階段 1：單 Region Hub-and-Spoke
  └─ 使用 TGW + 路由表隔離（當前最常見）

階段 2：多 Region TGW Peering
  └─ 跨 Region TGW Peering，手動管理路由

階段 3：Cloud WAN 整合
  └─ 將 TGW Peering 替換為 Cloud WAN
  └─ 透過 Cloud WAN 與現有 TGW 建立 Peering Attachment
  └─ 逐步將路由遷移至 Cloud WAN Segment
```

---

## 模式對比總結

| 比較維度 | Full Mesh（互通） | Isolated Spoke（隔離） | Centralized Inspection | Centralized Egress |
|---------|-------------------|----------------------|----------------------|-------------------|
| **核心目標** | 簡化連線，打通全網 | 集中連線，嚴格隔離 | 深度流量檢測 | 統一出站，節省成本 |
| **Spoke 間通訊** | 允許 | 拒絕（路由黑洞） | 視檢測策略而定 | 視路由表設計而定 |
| **最少路由表數** | 1 張 | 2 張 | 2 張（Native TGW 後） | 2 張 |
| **安全性** | 低（爆炸半徑大） | 高（橫向移動受阻） | 最高（DPI + IPS） | 中（集中出站控制） |
| **複雜度** | 最低 | 中等 | 高 | 中等 |
| **典型場景** | 新創、內部系統 | 多環境分離、合規 | 金融/醫療受監管環境 | 大規模多 VPC 環境 |

---

## 設計最佳實踐

### 子網規劃
- 為每個 TGW VPC Attachment 使用**專用子網**
- 使用小 CIDR（如 /28），保留更多 IP 給計算資源

### 路由表設計
- 僅提供「需要通訊」的路由，省略不需要通訊的路徑
- 善用 **Blackhole Route** 明確拒絕特定目標的流量
- 路由表數量以「需求分組」為原則——需求相同的 Attachment 共用一張表

### 安全分層
- **Security Group**：Instance 層級防火牆
- **Network ACL**：Subnet 層級存取控制
- **TGW Route Table**：VPC 間可達性控制
- **Network Firewall**：深度封包檢測（可直接掛載 TGW）

### 大規模管理
- 1000+ VPC 場景下，使用「分組關聯」策略可大幅降低維運負擔
- 考慮使用 AWS RAM 跨帳號共享 TGW
- 多 Region 場景優先評估 Cloud WAN

---

## 參考資源

- [AWS Well-Architected: Prefer Hub-and-Spoke Topologies](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/rel_planning_network_topology_prefer_hub_and_spoke.html)
- [Building Scalable and Secure Multi-VPC Network Infrastructure](https://docs.aws.amazon.com/whitepapers/latest/building-scalable-secure-multi-vpc-network-infrastructure/transit-gateway.html)
- [AWS Network Firewall: Native TGW Support](https://aws.amazon.com/about-aws/whats-new/2025/07/aws-network-firewall-native-transit-gateway-support/)
- [Centralized Traffic Filtering with AWS Network Firewall](https://aws.amazon.com/blogs/networking-and-content-delivery/deploy-centralized-traffic-filtering-using-aws-network-firewall/)
- [Creating a Single Internet Exit Point with TGW](https://aws.amazon.com/blogs/networking-and-content-delivery/creating-a-single-internet-exit-point-from-multiple-vpcs-using-aws-transit-gateway/)
- [Cloud WAN and Transit Gateway Migration Patterns](https://aws.amazon.com/blogs/networking-and-content-delivery/aws-cloud-wan-and-aws-transit-gateway-migration-and-interoperability-patterns/)
