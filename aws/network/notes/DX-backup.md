# AWS Direct Connect 與 Site-to-Site VPN 混合架構

## 概述

在混合雲環境中，當單條 Direct Connect 連結面臨頻寬飽和或需要提高可靠性時，Site-to-Site VPN 提供了一種成本高效的補充方案。本文檔介紹如何設計和最佳化 DX + VPN 的混合部署架構。

## 核心場景：頻寬擴展與故障轉移

### 問題描述
- 現有 1 Gbps DX 連結同時承載地端員工和遠端員工流量，處於飽和狀態
- 需要增加 20% 的頻寬容量
- 同時需要提高網路可靠性（備援機制）
- 預算有限，避免大規模基礎設施投資

### 解決方案架構

**混合部署策略：DX 優先 + VPN 備援**

```
地端員工 (10.10.0.0/16) ──→ [DX] ──→ AWS
                    │
                    └─ 故障時自動轉向 VPN

遠端員工 (10.100.0.0/16) ──→ [VPN] ──→ AWS
```

**為什麼這樣分流？**

| 流量來源 | 連接方式 | 原因 |
|--------|--------|------|
| **地端員工** | DX（主連結） | 位於內網，已習慣低延遲穩定連接；DX 的 sub-ms 延遲對其業務關鍵 |
| **遠端員工** | VPN（輔助連結） | 來自公網，已承受 ISP 波動；VPN 的延遲變化對其體感影響小 |

**頻寬效果：**
- DX：1.0 Gbps（僅供地端員工）
- VPN：1.25 Gbps（2025 版本支援 5 Gbps）
- 合計：2.25 Gbps（超過 +20% 需求）

**成本對比：**

| 方案 | 月成本 | 部署時間 | 故障轉移時間 | 適用場景 |
|------|--------|--------|-----------|--------|
| **DX（1 Gbps）單線** | $219 | 2-4 週 | N/A | 初期架構 |
| **DX + S2S VPN（1.25G）** | $255 (~$219 + $36) | < 1 天 (VPN 部分) | 90 秒 (預設) | **當前最優** |
| **DX + S2S VPN（5G）** | $579 (~$219 + $360) | < 1 天 | 3-10 秒 (優化後) | 高效能備援 |
| **雙 DX + Client VPN** | $1000+ | 2-4 週 | < 1 秒 | 雲原生/全面升級 |

---

## 流量分流實現：Policy-Based Routing

### 在地端防火牆配置分流（以 Cisco ASR 為例）

#### 步驟 1：定義路由政策

```cisco
! 定義 BGP Local Preference
route-map PREFER_DX permit 10
  set local-preference 200

route-map PREFER_VPN permit 10
  set local-preference 100

! 應用到 BGP session
router bgp 65000
  neighbor 169.254.10.1 remote-as 64512    ! DX VIF
  address-family ipv4
    neighbor 169.254.10.1 route-map PREFER_DX in

  neighbor 169.254.20.1 remote-as 64512    ! VPN
  address-family ipv4
    neighbor 169.254.20.1 route-map PREFER_VPN in
```

#### 步驟 2：按來源 IP 分流

```cisco
! 定義 ACL (Access Control List)
access-list 101 permit ip 10.10.0.0 0.0.255.255 any   ! 地端員工
access-list 102 permit ip 10.100.0.0 0.0.255.255 any  ! 遠端員工

! 定義 PBR (Policy-Based Routing)
route-map ROUTE_DX permit 10
  match ip address 101
  set ip next-hop 169.254.10.1    ! DX interface

route-map ROUTE_VPN permit 10
  match ip address 102
  set ip next-hop 169.254.20.1    ! VPN tunnel interface

! 在邊界路由器應用 PBR
interface GigabitEthernet 0/0/0
  ip policy route-map ROUTE_DX
  ip policy route-map ROUTE_VPN
```

#### 步驟 3：故障轉移配置

```cisco
! 預設路由指向 DX（DX 故障時自動轉向 VPN）
ip route 0.0.0.0 0.0.0.0 169.254.10.1 10      ! DX (AD=10)
ip route 0.0.0.0 0.0.0.0 169.254.20.1 20      ! VPN (AD=20, 僅當 DX 不可達時用)
```

### 配置效果

✅ **流量精確分流**：不同網段走不同連結
✅ **DX 被充分利用**：地端流量專用，頻寬不浪費
✅ **自動故障轉移**：DX 斷線時所有流量自動轉向 VPN
✅ **成本最優化**：無需額外硬體投資，僅需軟體配置

---

## BGP 最佳化：加快故障檢測時間

### 問題：預設故障轉移延遲

- BGP Keepalive Timer（預設 30 秒）
- BGP Hold Timer（預設 90 秒）
- 故障轉移時間 = 90-120 秒（業務中斷時間長）

### 最佳化方案

#### 方案 A：調整 BGP 計時器（快速，推薦）

```cisco
router bgp 65000
  neighbor 169.254.10.1 remote-as 64512
  neighbor 169.254.10.1 timers 3 10
    ! Keepalive: 3秒, Hold: 10秒

結果：故障檢測時間縮短至 10-15 秒內
AWS 端會自動協商以符合地端設定值
```

**參數調優指南：**
- Keepalive: 3-5 秒（不要過低，防止誤判）
- Hold: 3x Keepalive（通常 9-15 秒）

#### 方案 B：啟用 BFD（毫秒級檢測）

```bash
# 在 DX VIF 層級啟用 BFD
aws ec2 describe-customer-gateways
aws directconnect describe-virtual-interfaces

# 地端防火牆配置 BFD
interface BGP_DX
  ip address 169.254.10.1 255.255.255.252
  bfd interval 300 min_rx 300 multiplier 3
    ! 檢測間隔：300ms，失敗倍數：3
    ! 故障檢測時間：~900ms

router bgp 65000
  neighbor 169.254.10.1 remote-as 64512
  neighbor 169.254.10.1 timers 3 10
  neighbor 169.254.10.1 bfd
```

**BFD 工作原理：**
- 獨立的故障檢測機制，不依賴 BGP Keepalive
- 檢測間隔可低至 100ms（毫秒級）
- BGP + BFD 組合可實現 < 3 秒的故障檢測

#### 方案 C：AS-Path Prepending（複雜場景）

```cisco
! 在地端防火牆手動延長 VPN 的 AS-Path
route-map LONG_PATH permit 10
  set as-path prepend 65000 65000 65000

! 應用到 VPN BGP 鄰居
router bgp 65000
  neighbor 169.254.20.1 remote-as 64512
  address-family ipv4
    neighbor 169.254.20.1 route-map LONG_PATH out

結果：
  DX 路由 AS-Path：65000（短）→ 優先
  VPN 路由 AS-Path：65000 65000 65000 65000（長）→ 備用
```

---

## Transit Gateway 環境特殊考慮

### TGW Route Table 的優先級決策順序

```
1. 更明確的前綴匹配（Longest Prefix Match）
2. AS-Path 長度
3. MED (Multi-Exit Discriminator) 值
4. Route Priority 手動設定

⚠️ 重要：Transit Gateway 不支援 Local Preference
   → 必須搭配地端 PBR 來進行流量分流
```

### TGW + DX + VPN 的推薦配置

```
步驟 1：在 TGW 中為 DX 和 VPN 創建 Attachment
  ├─ DX Attachment（VIF）
  └─ VPN Attachment

步驟 2：配置 TGW Route Table Association
  DX Attachment  → Route Priority: 100（高）
  VPN Attachment → Route Priority: 200（低）

步驟 3：在地端防火牆配置 PBR
  地端員工流量 → 指向 DX 介面
  遠端員工流量 → 指向 VPN 介面

效果：
  ✅ TGW 收到相同前綴時，依靠地端側的分流決策
  ✅ 避免 TGW 路由衝突
  ✅ 確保可預測的流量行為
```

---

## 架構設計檢查清單

### 容量規劃

- [ ] 計算峰值流量需求，驗證 DX + VPN 總頻寬充足
- [ ] 預留 30% 的容量餘量，應對流量突增
- [ ] 評估是否需要升級至 VPN 5 Gbps

### 故障轉移

- [ ] 配置 BGP 計時器（推薦 3-10 秒）
- [ ] 考慮啟用 BFD 以達成 < 3 秒故障檢測
- [ ] 在生產環境前進行故障模擬測試

### 監控與告警

- [ ] 監控 DX 連結利用率，預警閾值設為 70%
- [ ] 監控 VPN 隧道狀態和丟包率
- [ ] 設置 BGP 鄰居狀態變化告警
- [ ] 記錄故障轉移事件到 CloudWatch

### 成本最佳化

- [ ] 定期審視流量模式，確認 PBR 分流有效
- [ ] 評估是否可以進一步降低 BGP 計時器
- [ ] 考慮按需升級至 5 Gbps VPN（僅在高負載時）

---

## 常見故障排查

### 症狀 1：VPN 隧道建立失敗

**排查步驟：**
1. 確認客戶網關（地端防火牆）IP 地址正確
2. 驗證 Pre-Shared Key (PSK) 配置一致
3. 檢查安全群組和網路 ACL 允許 UDP 500/4500 連接埠
4. 查看 VPN 日誌：`aws ec2 describe-vpn-connections --filters Name=vpn-connection-id`

### 症狀 2：流量未按預期分流

**排查步驟：**
1. 驗證 PBR 規則是否正確應用：`show route-map ROUTE_DX`
2. 檢查 ACL 規則：`show access-list 101 102`
3. 確認 BGP 鄰居狀態：`show bgp summary`
4. 查看實際路由表：`show ip route`

### 症狀 3：VPN 故障轉移延遲過長

**排查步驟：**
1. 驗證 BGP 計時器設置：`show ip bgp neighbors`
2. 檢查是否啟用了 BFD
3. 查看 DX 層面的故障檢測機制
4. 評估是否需要進一步降低 BGP 計時器

---

## 架構演進路徑

### 當前狀態（成本最佳化階段）
- **現狀**：DX + VPN（1.25 Gbps），地端員工優先
- **成本**：~$255/月
- **故障轉移**：90 秒（預設）或 10 秒（優化後）
- **適用企業**：成本敏感型，已有地端網路基礎設施

### 中期目標（高可靠性階段）
- **方案**：DX + VPN（5 Gbps），啟用 BFD
- **成本**：~$579/月
- **故障轉移**：< 3 秒
- **適用企業**：追求可靠性和效能的快速增長企業

### 長期目標（雲原生階段）
- **方案**：Client VPN + AWS-native 服務，弱化地端依賴
- **成本**：高（按人頭和連接時長計費），但運維成本低
- **故障轉移**：自動擴展，無單點故障
- **適用企業**：全面雲化，地端足跡最小化

---

## 參考資源

- [AWS Direct Connect 最佳實踐](https://docs.aws.amazon.com/directconnect/latest/UserGuide/)
- [Site-to-Site VPN 配置](https://docs.aws.amazon.com/vpn/latest/s2svpn/VPC_VPN.html)
- [Transit Gateway 路由](https://docs.aws.amazon.com/vpc/latest/tgw/tgw-route-tables.html)
