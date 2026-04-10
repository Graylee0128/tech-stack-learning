# AWS ANS-C01 考後分析與下一步建議

**考試日期：** `2026-04-09`  
**考試名稱：** `AWS Certified Advanced Networking - Specialty (ANS-C01)`  
**成績：** `679 / 1000`  
**通過門檻：** `750`  
**結果：** `FAIL`  
**與通過差距：** `71` 分

## 一句結論

這次不是基礎完全不夠，而是：

- `Network Implementation` 已達通過水準
- `Network Design`
- `Network Management and Operation`
- `Network Security, Compliance, and Governance`

這三大塊還不夠穩，尤其是在英文題幹下的選型、排錯順序、與安全邊界判斷。

換句話說，現在最有效的方向不是「整份重讀一次」，而是：

- 用刷題建立題感
- 用穩定複習把弱點變成反射

## 成績單解讀

根據成績單：

- `Domain 1: Network Design (30%)` -> `Needs Improvement`
- `Domain 2: Network Implementation (26%)` -> `Meets Competencies`
- `Domain 3: Network Management and Operation (20%)` -> `Needs Improvement`
- `Domain 4: Network Security, Compliance, and Governance (24%)` -> `Needs Improvement`

### 這代表什麼

#### 1. `Implementation` 已經不是主問題

這和近期複習內容相符。你已經系統性補過：

- `DX / VIF / DXGW`
- `VGW / TGW / VPN family`
- `Route 53 / CloudFront / Global Accelerator`
- `VPC flow path / endpoint / PrivateLink`

所以 `Implementation` 達標是合理的。

#### 2. `Design` 需要加強的不是名詞，而是 tradeoff

這類題通常不是問你「某服務是什麼」，而是問你：

- 為什麼是 `TGW` 不是 `Peering`
- 為什麼是 `PrivateLink` 不是 `TGW`
- 為什麼是 `Warm Standby` 不是 `Pilot Light`
- 為什麼是 `CloudFront` 不是 `Global Accelerator`

也就是：

- 關鍵字抓取
- 架構邊界
- 成本 / 擴展 / 風險 / 管理面的取捨

#### 3. `Management and Operation` 是這次很關鍵的失分區

這一塊很容易在準備時被低估，因為它不像 DX / TGW 那麼「主角感」強，但在 ANS 很常出。

高風險題型包括：

- `Flow Logs / Traffic Mirroring / Reachability Analyzer`
- `DX physical troubleshooting`
- `BGP failover / AS_PATH / route priority`
- `MTU / Jumbo Frames / fragmentation`
- `ip-ranges.json`
- `IPAM / AWS Network Manager`
- `what should be checked first`

#### 4. `Security / Compliance / Governance` 還沒內化成穩定選型

雖然概念你已經補過，但成績顯示這塊還不夠穩，尤其容易混：

- `WAF`
- `Shield`
- `Network Firewall`
- `Route 53 Resolver DNS Firewall`
- `Firewall Manager`
- `inspection VPC / GWLB / appliance mode`

## 與目前學習狀況對照

### 已經做對的事

你最近的補法其實是有效的，因為：

- 主幹服務邊界已經補起來了
- `plan.md` 已改成「快速掃讀即可先 mark」
- `learning-log` 和 `logs/2026-04-08.md` 已沉澱出大量選型口訣與易混點

這些都說明你不是零散亂讀，而是已經建立了自己的骨架。

### 目前的主要缺口

不是「不知道」，而是這三件事還不夠穩：

1. 英文題幹下的關鍵字抓取速度
2. 四個選項都像對時的排除能力
3. 對 operation / security 類題型的第一反應

## 接下來的建議策略

## 核心原則

**主線改成：刷題為主，穩定複習為輔。**

不要再平均重讀整份教材。  
下一階段最有效的做法是：

- `英文題目`
- `中文解析`
- `錯題分類`
- `穩定回補`

## 建議的學習節奏

### 每日節奏

#### `Block A - 刷題`

- 每天 `20~30 題`
- 以英文題幹為主
- 不求一次全對，重點是建立題型辨識

#### `Block B - 錯題複盤`

每題錯題至少記這 4 件事：

- 題目主題：`Design / Implementation / Operation / Security`
- 錯因類型：
  - `服務不熟`
  - `路由判斷錯`
  - `關鍵字漏看`
  - `排除選項失敗`
- 正解關鍵字
- 為什麼不是另外三個

#### `Block C - 穩定複習`

每天只回補 `1~2 個弱點小主題`，例如：

- `WAF vs Shield vs Network Firewall vs DNS Firewall`
- `PrivateLink vs Interface Endpoint vs Gateway Endpoint`
- `Pilot Light vs Warm Standby`
- `Flow Logs vs Traffic Mirroring vs Reachability Analyzer`

## 建議的優先順序

### 第一優先：`Security / Governance`

因為：

- domain 失分明確
- 觀念容易混
- 補強後回報率高

優先主題：

- `WAF / Shield / Network Firewall / DNS Firewall`
- `Firewall Manager`
- `GWLB / inspection VPC / appliance mode`
- `CloudFront + WAF + Shield`

### 第二優先：`Management / Operation`

優先主題：

- `Flow Logs / Traffic Mirroring / Reachability Analyzer`
- `DX physical troubleshooting`
- `BGP route selection`
- `MTU / Jumbo Frames`
- `IPAM / Network Manager`
- `ip-ranges.json`

### 第三優先：`Design`

優先主題：

- `TGW vs Peering vs PrivateLink`
- `CloudFront vs Global Accelerator`
- `ALB vs NLB vs GWLB`
- `Pilot Light vs Warm Standby`
- `DX vs VPN`

## 不建議的做法

### 1. 不要重新平均讀全部服務

因為：

- `Implementation` 已經過線
- 全面重讀會稀釋掉你真正該補的分數來源

### 2. 不要只看筆記不做題

你現在最大的瓶頸不是「沒有資料」，而是：

- 英文題幹壓力下
- 需要快速做正確排除

這只有刷題能補。

### 3. 不要用「今天學很多」取代「今天解對更多」

下一階段的 KPI 應該從：

- 讀了多少頁

改成：

- 做了幾題
- 錯題有沒有分類
- 同類錯誤有沒有下降

## 建議的 14 天 retake sprint

### Day 1-4

主打：

- `Security`
- `Operation`

每天：

- `20~30 題`
- 錯題分類
- 回補 1~2 個主題

### Day 5-8

主打：

- `Design`
- `高頻混淆題`

例如：

- `TGW / Peering / PrivateLink`
- `ALB / NLB / GWLB`
- `CloudFront / GA`
- `DR / Cost`

### Day 9-11

主打：

- 混合模擬題
- 計時練習
- 弱點二次回補

### Day 12-14

只做：

- 口訣
- 錯題
- 弱點主題

不要再開新內容。

## 我對你重考的看法

你這次 `679`，差 `71` 分。  
這不是需要推倒重來的分數。

更像是：

- 主體已經有了
- 只差把失分題型打穩

如果接下來真的採用：

- 刷題主導
- 英文題幹訓練
- 中文解析
- 錯題分類
- 穩定複習

那下一次把分數推過 `750` 是有機會的。

## 下一步建議

### 立刻開始的做法

1. 以 `questions/` 或題庫做每日英文題練習
2. 每天固定做錯題分類
3. 每天只回補少量弱點，不全面重讀
4. 優先補 `Security / Operation / Design`

### 在這個 repo 內的建議搭配

- `plan.md`
  用來看主線進度
- `learning-log.md`
  用來看學習日期索引
- `logs/`
  用來補概念與口訣
- `questions/`
  用來做刷題與錯題沉澱
- `notes/ANS-Cheat-Sheet-中文版.md`
  用來做考前高頻速複

## 最後一句話

你現在最需要的不是再把知識面變更寬，  
而是把已經學過的內容轉成：

- 英文題幹下的快速辨識
- 題目選項間的穩定排除
- 錯題可回收的反覆修正能力

這次之後，準備方式從「學習導向」切到「得分導向」，會更有效。
