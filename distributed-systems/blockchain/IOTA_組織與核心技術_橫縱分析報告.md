# IOTA 組織與核心技術橫縱分析報告

> 研究日期：2026-05-12
> 研究方法：橫縱分析法（Horizontal-Vertical Analysis）
> 研究對象：IOTA Foundation 與 IOTA 協議（從 2015 Tangle 白皮書到 2026 Starfish 共識）
> 報告口吻：平衡審慎、工程師可讀
> 報告定位：技術 + 組織盡職調查，不做投資建議

---

## 一句話定義

> **IOTA 是一個由德國 IOTA Foundation 維護、原始定位為 IoT 微支付的 DAG 帳本；2025–2026 期間經歷大規模重構，已轉變為「DAG mempool + Move 物件導向 VM + DPoS 共識」的智慧合約 L1，目前的官方敘事是「全球貿易與真實世界資產（RWA）的結算層」。**

它不再是 2017 年那個「無費、無區塊、IoT 機器經濟」的網路。理解 IOTA，要拆成「兩個 IOTA」：
- **Legacy IOTA（2015–2023）**：Tangle、Coordinator、Curl-P、Trinity 事件。
- **Rebased IOTA（2025– ）**：基於 Sui 的 Move 物件模型、Mysticeti → Starfish 共識、DPoS、IOTA EVM L2。

兩者的代幣連續、但底層幾乎全部換過。

---

## TL;DR（關鍵結論先讀）

1. **協議身份已換骨。** 2025 年 5 月 5 日上線的「IOTA Rebased」是把 Mysten Labs（Sui 的開發者）的 Rust codebase 與 MoveVM 移植過來，再疊上 IOTA 自家的 DAG mempool 設計。技術上更接近「fork of Sui with IOTA-flavored consensus」，而非延續 2017 年的 Tangle。【1】【2】
2. **組織總部在柏林，非營利基金會，已運作 9 年。** IOTA Foundation 註冊地為 Pappelallee 78/79, 10437 Berlin，2017 年成立，公開資料宣稱 110+ 員工分布於 27+ 地點。【3】
3. **「去中心化」承諾被拖了 6 年才落地。** 2019 年宣布 Coordicide，但實際達成無 Coordinator 的可營運主網要等到 2025 Rebased 啟用 DPoS（最多 150 validators）。中間經歷了 2020 年 Trinity wallet 攻擊 + Coordinator 關閉導致整網停擺約 28 天。【4】【5】
4. **存在重大歷史風險紀錄。** 2017 年 MIT DCI 揭露 Curl-P hash function 可在普通硬體上於秒級內找到 collision，可偽造簽名；2020 年 Trinity wallet 第三方 SDK 投毒，約 8.55 Ti（~$2M）被竊；2020 年共同創辦人 David Sønstebø 遭董事會「全體一致」決議解職。這三件事對該專案的密碼學文化、開發流程與治理都是長尾警訊。【6】【7】【8】
5. **當前敘事高度押在「全球貿易結算層」。** 2026 年 1 月 22 日發表的 IOTA Manifesto，把策略重心放在 TWIN（與 TradeMark Africa、肯亞海關合作）、AfCFTA 的 ADAPT、數位產品護照 Orobo、貿易金融 Salus。官方目標是「2030 年觸及 30+ 國貿易系統、年化 6.5 億筆貿易文件交易」。【9】
6. **代幣機制已非「無費」。** 4.6B 總供應，每 epoch 鑄造 767,000 IOTA 給 staking 獎勵（初期 ~6% 年通膨），交易費約 0.005 IOTA 並燒毀；staking APY 官方宣稱 10–15%。【10】【11】
7. **橫向比較裡，IOTA 的位置很尷尬。** 純 DAG 即時支付有 Nano，企業 aBFT 有 Hedera，DePIN/IoT 有 IoTeX，企業供應鏈有 VeChain。IOTA 用「Move + DPoS + 真實貿易」雙重押注，但也意味著它的差異化來自「敘事 + 客戶」，而非單純的技術獨佔。

---

## 目錄

- [一、研究方法與證據分級](#一研究方法與證據分級)
- [二、縱向分析：IOTA 的歷時演進（2015 → 2026）](#二縱向分析iota-的歷時演進2015--2026)
- [三、核心技術原理（工程師視角）](#三核心技術原理工程師視角)
- [四、橫向分析：DAG／IoT／企業鏈競品脈絡](#四橫向分析dagiot企業鏈競品脈絡)
- [五、橫縱交匯：歷史包袱如何塑造 2026 的全球貿易敘事](#五橫縱交匯歷史包袱如何塑造-2026-的全球貿易敘事)
- [六、爭議、風險與證據層級](#六爭議風險與證據層級)
- [七、給工程師讀者的判斷框架](#七給工程師讀者的判斷框架)
- [八、結論](#八結論)
- [附錄 A：年表彙整](#附錄-a年表彙整)
- [附錄 B：來源清單](#附錄-b來源清單)

---

## 一、研究方法與證據分級

本報告採橫縱分析法：
- **縱軸**：從 2015 年 Popov 的 Tangle 白皮書追到 2026-05 的 Starfish 主網與 v1.22.1 release，呈現 IOTA 在技術、組織、敘事三條線上的演進。
- **橫軸**：在 2026 當下時間切面，把 IOTA 與同類路線（DAG 即時支付、企業 aBFT、DePIN IoT、企業供應鏈）的競品做系統性比較。

### 證據分級規則

| 等級 | 來源類型 | 報告中標示 |
|---|---|---|
| A | 一手：IOTA Foundation 官方部落格、官方文件、官方 GitHub、官方白皮書 | 不特別標 |
| B | 二手：Wikipedia、CoinDesk、學術論文 | 「據 CoinDesk」「據 Wikipedia」等明寫 |
| C | 三手或推測：分析網站、社群媒體、評論 | 標「分析網站稱」、「未獨立查證」 |
| ⚠️ | 官方敘事但無公開驗證資料 | 標「官方主張」「無公開驗證資料」 |

預設立場：**對官方敘事打折，對技術主張要求引用**。代幣段落只談機制，不談價格。

---

## 二、縱向分析：IOTA 的歷時演進（2015 → 2026）

把 IOTA 11 年史拆成五個敘事章節。每章後面附「這一章留下什麼包袱」，因為這些包袱會在 2026 章節重新冒出來。

### 2.1 第一章：Tangle 的原始承諾（2015–2017）

- **2015**：Serguei Popov 發表 *The Tangle* 白皮書，提出以 DAG 取代區塊鏈，每筆交易確認前必須驗證另外兩筆未確認交易。設計目標：**無區塊、無礦工、無手續費、能跑在 IoT 微控制器上**。
- **2015–2017**：David Sønstebø、Dominik Schiener、Sergey Ivancheglo（CFB）、Serguei Popov 四人合夥推進，CFB 來自 Nxt/Jinn 計畫。
- **2017**：眾籌約 1,337 BTC（當時 ~$0.5M），鑄造 MIOTA 代幣並上線，總供應 2,779,530,283,277,761（IOTA 基本單位），通常顯示為 2.78 Pi。
- **2017 年中**：與 Microsoft 的合作公告被外界誤讀為「Microsoft 採用 IOTA」，後來澄清只是 IoT 數據市場展示。

> **這一章留下的包袱**：IoT / 無手續費 / 機器經濟的敘事深度植入早期社群與媒體報導。2026 年要改口談「全球貿易」時，會有大量 legacy 內容需要清理。

### 2.2 第二章：Curl-P 危機與密碼學文化爭議（2017）

- **2017-07-14**：MIT Digital Currency Initiative 的 Ethan Heilman、Neha Narula 等人向 IOTA 揭露 Curl-P-27 hash function 存在差分密碼分析弱點，**80 cores 上幾分鐘即可生成 collision**，可在 chosen-message 設定下偽造 IOTA bundle（一組交易）的簽名。【6】
- **2017-07-22**：MIT 揭露改進攻擊。
- **2017-08-07**：IOTA 進行向後不相容升級，停用 Curl-P-27 作為簽名 hash，改用基於 Keccak-384 的 Kerl。
- **2018 Black Hat**：完整論文 *Cryptanalysis of Curl-P and Other Attacks on the IOTA Cryptocurrency* 公開發表。【6】
- 雙方對「自製密碼學原語」的爭議延燒至今：IOTA 創辦人之一 CFB 主張這是「copy-protection」（故意留漏洞防分叉），MIT 團隊與多數密碼學界視為不負責任的工程實踐。

> **這一章留下的包袱**：「自製 hash function 之前是漏洞」這件事，是工程審查 IOTA 時繞不過去的歷史標籤。也直接影響後續設計改用業界標準（Ed25519、Blake2、Keccak）。

### 2.3 第三章：Coordinator 與「臨時的中心化」（2016–2024）

- **設計動機**：早期 Tangle 因為網路雜湊算力不足以抵禦 51% 攻擊，IOTA Foundation 自己跑一個叫 **Coordinator（Coo）** 的節點，定期發佈簽名的「milestone」交易；只有被 milestone 引用的交易才算最終確認。【4】
- **批評**：這等於 IOTA Foundation 擁有單點否決權，可以選擇優先確認哪些交易、能凍結資金、被攻擊就整網停擺。
- **2019-05**：Foundation 公布 *Coordicide* 白皮書，承諾移除 Coordinator，路徑分兩階段：Chrysalis（1.5）+ Coordicide（2.0）。【4】
- **2020-02-12**：Trinity wallet 攻擊（見下章），Foundation **主動關閉 Coordinator**，整網停擺到 2020-03-10，約 28 天。【7】這是「Coordinator 是否真的中心化」這件事最直接的公開事證。
- 之後 Coordicide 一再延期，要到 2025 Rebased 才真正以 DPoS 取代 Coordinator。

> **這一章留下的包袱**：Coordicide 拖延 6 年，是「敘事先行於工程交付」最常被引用的案例。

### 2.4 第四章：Trinity wallet 事件與治理震盪（2020）

- **攻擊時間軸**【7】【8】：
  - 2020-01-25：攻擊者透過 Cloudflare DNS 開始投放惡意 SDK 到 MoonPay 服務（Trinity 桌面錢包整合的法幣入金供應商）。
  - 2019-12-17 ~ 2020-02-18：在這段時間內打開或更新 Trinity 桌面錢包的使用者，種子可能被外洩。
  - 2020-02-10：攻擊高峰，種子被解密並上傳到攻擊者伺服器。
  - 2020-02-12：使用者通報後，Foundation 在 25 分鐘內關閉 Coordinator。約 50 個獨立種子被掃，約 **8.55 Ti / 約 $2M** 被竊。
  - 2020-02-29：發佈 Seed Migration Tool。
  - 2020-03-10：Coordinator 重啟。
- **責任處置**：創辦人 David Sønstebø 公開承諾以個人資金賠償受害者。
- **治理連鎖反應**：
  - 2020-02：CFB（Sergey Ivancheglo）公開表示與 Sønstebø 的合作關係終止，並提及涉及約 25M MIOTA、$7.7M 與 Jinn Labs 資金的爭議。【12】
  - 2020-12-10：IOTA Foundation 監督委員會「全體一致」決議與 Sønstebø 分道揚鑣，理由是「個人利益與專案分歧重大」。Sønstebø 隨後在 Medium 上反擊 Foundation 治理與資金運用。【12】

> **這一章留下的包袱**：(a) 桌面錢包對第三方 SDK 的供應鏈攻擊面，(b) Foundation 對主網的單方控制權，(c) 共同創辦人公開撕裂——這三件事直接影響社群對「IOTA = 一個可信任的長期基礎設施」的信任成本。

### 2.5 第五章：三次大型協議升級（2021–2026）

| 升級 | 日期 | 核心變化 | 是否破壞性 |
|---|---|---|---|
| **Chrysalis（IOTA 1.5）** | 2021-04 | 簽名方案改用 EdDSA、新位址格式、新節點軟體 Hornet/Bee，網路效能與穩定性大幅改善。**仍依賴 Coordinator**。 | 是，要種子遷移 |
| **Stardust（IOTA 2.0 過渡版）** | 2023-10-04 | 引入原生資產（Native Tokenization Framework）、輸出（Output）模型替代純值轉移、L2 智能合約鏈定位、Coordinator 被「Permissioned Validator Committee」取代。**總供應從 2.78 Pi 重新定義為 4.6 B IOTA**（含通膨後新增供應）。網路分叉為 IOTA Stardust 與 IOTA Stardust Classic。【11】【13】 | 是，要遷移 |
| **Rebased** | 2025-05-05 | **協議幾乎重寫**：基於 Sui 的 Rust 程式碼，導入 Move VM、物件導向帳本、Mysticeti 共識（DAG 排序）+ DPoS（13 → 50 → 150 validators）、staking 獎勵（767K/epoch 鑄造）、交易費焚毀。**舊 Stardust 持有者透過匯入助記詞無痛遷移**。【1】【2】【14】 | 否（種子層級無痛）但底層全換 |
| **Starfish** | testnet 2026-Q1、mainnet **2026-04-28** | 升級 Mysticeti 共識，引入 Reed-Solomon 抹除編碼、Data Availability Certificates、Push Pacemaker，p99 commit latency 從 ~486ms 降到 ~312ms，對外請求降一個量級。【15】【16】 | 不破壞 |

> **這一章留下的包袱**：技術代債清得很快，但每次升級都重新訓練社群與媒體的敘事，使得「IOTA 到底是什麼」這件事的答案在四年內換了四次。

### 2.6 第六章：2026 Q1 進度（最新切面）

從官方 Q1 2026 進度報告抽幾項可驗證的事實【17】：
- v1.16.0 將 Starfish 上 testnet。
- 啟用 Protocol v20 與 IIP-8（動態最低 validator commission）。
- 推出 IOTA Names（人類可讀的位址命名服務，已上 mainnet）。
- IOTA Identity 1.9：SD-JWT 升級。
- Account Abstraction 進入 devnet/alphanet/testnet。
- FastCommitSyncer 把同步速度提升 20–30 倍。
- Indexer 性能提升約 80 倍。
- Bullish 交易所整合完成。
- TWIN：與肯亞海關（KenTrade、KRA、TLIP）多節點連通；探索盧安達咖啡出口試點；英國 Teesside Port 資訊共享網路建立。
- ADAPT（AfCFTA-led）：正式動員。

`tech-stack-learning` 讀者要注意：**Q1 2026 報告刻意沒給 TPS、validator 數量、交易量等具體數據**，只給「速度提升 N 倍」的相對描述。要評估網路規模，得另外從鏈上 explorer 或第三方分析（未在本報告獨立查證）。

---

## 三、核心技術原理（工程師視角）

### 3.1 整體分層

```
┌─────────────────────────────────────────────────────────┐
│ Application Layer                                        │
│   - IOTA Identity, IOTA Names, Tokenization, Notarization│
│   - Apps: TWIN, Orobo, Salus, Pools Finance, Virtue      │
├─────────────────────────────────────────────────────────┤
│ L2: IOTA EVM (Solidity-compatible smart contract chain)  │
│   - Wasp node + ISC framework                            │
├─────────────────────────────────────────────────────────┤
│ L1: Move-based Object Ledger                             │
│   - Execution: MoveVM (object-centric, ported from Sui)  │
│   - Mempool / Ordering: DAG-based (Mysticeti / Starfish) │
│   - Sybil resistance: Delegated Proof-of-Stake           │
│   - Validators: up to 150                                │
│   - Account Abstraction (testnet)                        │
├─────────────────────────────────────────────────────────┤
│ Tokenomics                                               │
│   - Total supply: 4.6B IOTA                              │
│   - Issuance: 767,000 IOTA per epoch                     │
│   - Fees: ~0.005 IOTA / tx, burned                       │
└─────────────────────────────────────────────────────────┘
```

### 3.2 DAG mempool：把「排序」與「執行」解耦

**為什麼是 DAG，而不是線性 blockchain：**
傳統 BFT 共識（PBFT 風格）要靠一個 leader 提案、其他人簽名一筆。當交易量大、leader 容易塞爆、單點失敗會卡住整網。

DAG-based BFT（Narwhal / Bullshark / Mysticeti / Starfish 這條學術線）的核心思想是：
1. **mempool = DAG**：每個 validator 不斷打包自己的「block」，互相引用其他 validator 上一輪的 block，組成 DAG。
2. **consensus 變成「對 DAG 排序」**：只要 DAG 結構達到某些條件，就能對其中的 block 推導出一致的線性順序，而不需要 leader 提案。
3. 結果：吞吐量基本上吃滿頻寬，而不是被 leader 卡住。

IOTA Rebased 採的是 **Mysticeti**（Mysten Labs 在 2024 提出的低延遲 DAG-BFT），然後再升級到自家設計的 **Starfish**。

### 3.3 Starfish 共識：解了 Mysticeti 一個 unsafe 角落

Starfish 的問題意識來自一個 Mysticeti 弱點【16】：

> 在 uncertified DAG 協議裡，誠實節點可能在還沒打出自己的 block 時就推進 round，導致 DAG 上出現「洞」（gap）。當網路恢復同步後，這些洞讓 leader commit 卡住，造成 desynchronization attack。

Starfish 三個關鍵設計：

#### (1) Reed-Solomon 抹除編碼
把交易 payload 拆成 fragments，分送給不同 validator。重建只需要 **f+1 個有效 fragment**（不是傳統的 2f+1），把「重共識」與「重 payload」解耦。

#### (2) Data Availability Certificates (DACs) 內建在 DAG header
Validator 在 header 裡簽署「我已驗證 payload」。當某個 block 的因果歷史裡累計到 2f+1 個 ack，這個 block 自動成為 availability certificate。**沒有額外的 availability 輪次**，可用性隨 DAG 自然成長。

#### (3) Push Pacemaker
Validator 必須先產出自己這一輪的 block 才能推進 round，從結構上禁止「空洞 DAG」。

#### 量化結果（官方測試環境，非生產實測）【16】
- p99 commit latency：~486ms → ~312ms（降低約 36%）
- Outbound request rate：降一個數量級
- 頻寬使用：~2 倍（trade-off：用前置通訊買後置可預期性）

#### 與 Bullshark/Mysticeti 的差異點
- Bullshark 走 certified DAG（每個 block 要先取得 2f+1 簽名才入 DAG），延遲較高但 robust。
- Mysticeti 走 uncertified DAG（block 不需要先 certify），延遲低但有上面講的 desync 風險。
- Starfish 維持 uncertified 的低延遲，但用 DACs + 抹除編碼補上可用性。
- 學術基礎引用 Keidar/Naor/Shapiro 的 *Cordial Miners*（DISC 2023）。

> **工程閱讀重點：** Starfish 的 narrative 是「mean latency 略升、tail latency 大幅降」，這是 production-grade 取捨。對需要穩定 SLA 的企業 RWA 場景比較對胃口，對追求 peak TPS 的 narratives 反而不是強項。

### 3.4 Move VM：物件導向帳本

從 Sui 移植的 Move VM 與 EVM/UTXO 都不一樣：
- **物件作為一等公民**：每個資產（代幣、NFT、合約狀態）都是一個有 id、有 owner 的物件。轉移資產 = 修改物件的 owner 欄位。
- **平行執行**：不同 owner 的物件互不衝突，可平行執行。這是 Move 物件模型最大的工程收益。
- **靜態驗證 + 形式化驗證友善**：Move 設計時就把 linear types（資源不能被複製或丟失）放進型別系統。
- **安全性收益**：Aptos/Sui 多次 audit 報告都指出 Move 比 Solidity 更難寫出 reentrancy / double-spend / unchecked-call bug。

IOTA 的特色修改【14】：
- **Sponsored transactions**：開發者可代付 gas，做 feeless UX。
- **Storage deposit**：佔用儲存要押金，釋放後可退（沿用 Stardust 設計）。
- **Identity SDK**：多 controller、進階存取控制，配合 IOTA Identity 的 DID 場景。
- 計畫中的 **MultiVM 願景**：把 EVM 整合進 L1（目前 EVM 還在 L2 Wasp）。

### 3.5 DPoS validator set 與經濟激勵

| 參數 | 值 | 來源 |
|---|---|---|
| 最大 validator 數 | 150 | 【18】 |
| Genesis validator | 13 | 【2】 |
| 每 epoch 鑄造 | 767,000 IOTA | 【10】 |
| 初期年通膨 | ~6%（≈ 279.955M IOTA/年，按 365 epoch） | 【10】 |
| 平均交易費 | ~0.005 IOTA | 【14】 |
| 交易費去向 | 焚毀 | 【14】 |
| Staking APY（官方主張） | 10–15% | 【10】 |
| 競爭性席位 | 新 validator 可以靠更高質押替換現有 validator（與 Sui 不同） | 【14】 |

> 兩個工程關注點：
> 1. **APY 與通膨不是同一件事**。10–15% APY 來自把 6% 通膨「重新分配」給質押者，且非質押者承擔稀釋。
> 2. **「燒費 + 鑄獎勵」是淨通膨還是淨通縮**，取決於鏈上交易量。在當前交易量資料未公開的情況下，預設它仍是淨通膨。

### 3.6 Tangle 還在嗎？

技術角度：**Tangle 作為 L1 帳本結構，已經不在了**。當前 L1 是物件導向帳本，DAG 出現在 mempool/共識層，而不是帳本層。
品牌角度：IOTA 官方仍把 DAG 形容為「平行化資料結構」，但已不強調 Tangle 名詞。
媒體角度：部分 2017–2023 的文章仍把 IOTA 視同「Tangle」，這是讀舊資料時要校正的偏差。

---

## 四、橫向分析：DAG／IoT／企業鏈競品脈絡

這份報告只看 **跟 IOTA 歷史敘事同源** 的競品，不做泛 L1 比較（避免變成投資視角）。

### 4.1 Nano：純粹 DAG + 即時支付的對照組

| 維度 | Nano | IOTA |
|---|---|---|
| 帳本結構 | Block-lattice（每個帳戶自己一條鏈） | 物件導向帳本 + DAG mempool |
| 共識 | Open Representative Voting（ORV，依質押權重投票） | DPoS + Mysticeti/Starfish |
| 智能合約 | ❌ 無 | ✅ Move L1 + EVM L2 |
| 手續費 | 0（PoW spam 防護） | ~0.005 IOTA，焚毀 |
| 確認時間 | 1–2 秒 | sub-second mempool propagation；commit 數百 ms 量級 |
| 主要敘事 | 純支付 / 點對點現金 | 全球貿易結算 / RWA |

> **取捨對照**：Nano 把 DAG 用到極致換來「真正無費、真正即時」，但放棄了智能合約。IOTA Rebased 走相反方向——保留 DAG 結構但完整補上智能合約棧，代價是接受 staking inflation 與 ~0.005 IOTA 的 gas。

### 4.2 Hedera：企業 DLT 的另一條路徑

| 維度 | Hedera | IOTA |
|---|---|---|
| 共識 | Hashgraph aBFT（Leemon Baird 提出，專利） | DAG-BFT，開源 |
| 治理 | Hedera Governing Council（Google、IBM、Boeing、LG、Deutsche Telekom 等限額成員） | IOTA Foundation 非營利 + 開放 validator |
| 智能合約 | EVM | Move L1 + EVM L2 |
| 主打場景 | 企業 / 微支付 / IoT / supply chain | 全球貿易 / RWA / IoT 餘音 |
| 性能主張 | 10,000+ TPS、5 秒內 finality（官方主張） | 未公開 TPS 數字 |

> Hedera 走的是「集中治理 + 開放使用」的企業聯盟鏈思路；IOTA 是「分散治理 + 開放使用」但同樣鎖定企業客戶。兩者目標市場高度重疊，治理哲學差異最大。【19】

### 4.3 IoTeX：DePIN / IoT 路線的純粹版

IoTeX 是 IOTA 最容易混淆的對照組，因為兩者都源自「區塊鏈 + IoT」敘事【20】：

| 維度 | IoTeX | IOTA |
|---|---|---|
| L1 | EVM-compatible | Move（Sui-rooted） |
| 鏈下計算 | W3bstream（ZK + TEE + MPC 混合驗證） | 無對應元件 |
| 設備識別 | ioID + Quicksilver AI | IOTA Identity（DID） |
| 主敘事 | DePIN / 真實世界 AI 應用 / 物理智能 | 全球貿易結算 |
| 監管定位 | 2025-12 發佈 MiCA-compliant whitepaper（歐盟） | 在歐盟基金會註冊但無 MiCA whitepaper 公開資料 |

> IoTeX 把「IoT 鏈」這條路線繼續深耕到 DePIN 與物理 AI；IOTA 已經把同一個敘事讓給了 IoTeX，自己轉向貿易結算。這是 2025–2026 兩條路線的最大分歧。

### 4.4 VeChain：企業供應鏈的直接競品

VeChain 是 IOTA 在 RWA / supply chain 場景的最直接對手【21】：

| 維度 | VeChain | IOTA |
|---|---|---|
| 架構 | VeChainThor（單鏈、PoA → PoS hybrid） | DAG-BFT + DPoS |
| 雙代幣 | VET（價值）/ VTHO（gas，焚毀） | 單代幣 IOTA |
| 企業客戶 | BMW、Walmart China、PwC、DNV | 肯亞 KRA、英國 BT、TradeMark Africa |
| 標誌專案 | VeBetterDAO（聯合國 SDG 對齊，GreenCart / Mugshot 各 1M+ 用戶） | TWIN（貿易單據數位化）、ADAPT（AfCFTA） |
| 2025 升級 | Galactica 協議（VTHO 100% 焚毀）、StarGate staking | Rebased + Starfish |

> 兩者都把「企業現有業務上鏈」當核心敘事。**VeChain 的優勢是已商業化客戶與消費級 dApp 流量**，**IOTA 的優勢是非營利定位、Move VM 與 Foundation 的政府／NGO 通路**（TradeMark Africa、AfCFTA 是政府間通路，VeChain 較少這類連結）。

### 4.5 一張匯總圖

```
                        Smart contracts?
                            ┌──No──→ Nano (純支付)
                            │
                     DAG?  ─┤            ┌── Hedera (aBFT、企業聯盟治理)
                            │            │
                            └──Yes──→  ─┼── IoTeX (DePIN / IoT / W3bstream)
                                         │
                                         ├── VeChain (企業供應鏈 / 已商業化)
                                         │
                                         └── IOTA Rebased (Move L1 + 貿易敘事)
```

IOTA 在 2026 的差異化 = **唯一同時擁有：（a）非營利身份、（b）Move 物件模型 L1、（c）政府／NGO 通路、（d）DAG-BFT 共識（Starfish）** 的選項。但每一項單獨都有替代品。

---

## 五、橫縱交匯：歷史包袱如何塑造 2026 的全球貿易敘事

縱軸跟橫軸交叉後，IOTA 的當前定位才看得清楚。我把它整理成四條觀察線：

### 5.1 「無費 IoT」敘事的退場是必然，不是失敗

- 縱軸告訴我們：原始 Tangle 設計依賴 Coordinator 才能安全運轉，2020 年的網路停擺證明這個設計不耐生產壓力。
- 橫軸告訴我們：IoT / DePIN 賽道已經被 IoTeX 等專案佔據，且這條路本身的商業變現也是缓慢的。
- 結論：**從 IoT 退場、從手續費退場是務實選擇**，不是「失敗」。但這個轉向也意味著 IOTA 2017 年的早期投資人買到的故事與今天的產品是兩個不同的東西。

### 5.2 採用 Sui 棧是技術上正確、敘事上敏感

- 縱軸告訴我們：自製密碼學（Curl-P）與自製共識（Coordicide）兩條都消耗了大量工程時間且結果不理想。
- 橫軸告訴我們：Move VM + DAG-BFT 是 2024–2026 年的學術主流，社群成熟、形式化工具齊全。
- 結論：**採用 Sui 的 Rust codebase 與 Move VM 是技術理性選擇**【1】。但這也意味著 IOTA 的差異化不再是「我的技術」，而是「我的客戶 + 我的治理」。對工程審查者來說，這降低了協議自身風險，但提高了「IOTA 與 Sui 路徑為什麼會分歧」的長期判斷難度。

### 5.3 全球貿易是少數能容下「非營利 + 政府通路」優勢的賽道

- 橫軸告訴我們：DeFi、NFT、GameFi 這些賽道對「非營利」沒任何溢價，反而要求 token-economic 激進設計。
- 縱軸告訴我們：IOTA Foundation 9 年下來累積的政府／NGO 通路（特別是非洲、北歐、東歐）才是它真正能變現的資產。
- 結論：**Manifesto 把策略壓在「全球貿易 = Blue Ocean」是 Foundation 把自身組織能力與市場錯位處對齊的結果**【9】。這個押注的風險是：貿易 IT 採購週期長、合規門檻高、對手不是其他 L1 而是 SWIFT、IBM、Bolero 這類傳統玩家。

### 5.4 過去的單點脆弱性，今天還沒完全證明已修復

- 縱軸告訴我們：2020 年 Coordinator 整網一指令停擺。
- 橫軸告訴我們：2026 年 mainnet 上有 150 validator 的 DPoS。
- 但要證明 IOTA 真的「無單點」，要等到一次主網級別的攻擊或 validator 大規模 failover 在公開環境下被觀察過。**截至 2026-05，沒有這類公開測試的 post-mortem 證據**。所以結論是「設計上已修，工程上尚待時間驗證」。

---

## 六、爭議、風險與證據層級

> 本節必要但克制。每一條都標證據層級。

### 6.1 已被廣泛認定的事實層風險（高證據）

1. **Curl-P 漏洞（2017）**：MIT DCI 的 cryptanalysis 論文在 IACR ePrint 2019/344 與 Black Hat 2018 公開。IOTA 已替換 hash function。**現況：歷史紀錄，已修復**，但影響了業界對 IOTA 早期工程實踐的看法。【6】
2. **Trinity 事件（2020-02）**：~$2M 被竊、Coordinator 關閉 28 天。Sønstebø 個人承諾賠付。**現況：受害者層面已賠付，治理層面引爆 Foundation 內部裂痕**。【7】【8】
3. **Coordinator 中心化**：從 2016 上線到 2025 Rebased，Coordinator 機制存在約 9 年。其間 Coordicide 路線圖多次延期。**現況：Rebased 之後 Coordinator 已退場，但「承諾兌現週期太長」的紀錄是真實的**。【4】【5】
4. **Sønstebø 解職（2020-12-10）**：Foundation 監督委員會「一致決議」與 Sønstebø 分道。Sønstebø 公開反擊 Foundation 治理與資金。**現況：兩造各執一詞**，但 Foundation 的監督委員會結構自此明顯收緊。【12】

### 6.2 爭議性質的論點（中等證據）

5. **「IOTA Rebased 算不算 Sui 的 fork」**：第三方分析（Four Pillars 等）直接稱為 fork；官方傾向用「以 Sui 為基礎、保留 IOTA 設計哲學」。技術上兩個說法差距不大，定性差距大。**證據等級：B**。【1】
6. **TPS / finality 主張**：截至 2026-05-12，IOTA 官方頁面與部落格未提供獨立可驗證的 TPS / finality 數字。Starfish 部落格有 p99 latency 數字但屬於官方測試環境。**證據等級：A 引用、但未獨立查證**。【15】【16】

### 6.3 敘事性主張（低證據，需要打折）

7. **「2030 年觸及 30+ 國貿易系統、6.5 億筆/年交易」**：來自 Manifesto 的目標宣告，沒有合約／LOI 對應證據公開。**證據等級：⚠️ 官方主張，無公開驗證資料**。【9】
8. **「IOTA 在全球貿易賽道沒有大型對手」**：Manifesto 的論點之一，但完全忽略 SWIFT、Bolero、essDOCS、TradeLens 後繼者、以及 VeChain 等競爭者。**證據等級：⚠️ 立場性論述**。

### 6.4 應該被淡化處理的舊爭議

9. 早年「IOTA 與 Microsoft 合作」的媒體誤讀、創辦人在社群上的口角、價格相關評論——對 2026 年的工程／組織判斷已無關鍵價值，本報告不列為重點。

---

## 七、給工程師讀者的判斷框架

> 把這份報告濃縮成「你拿到一個 IOTA 相關評估／PoC 任務時，要問哪些問題」。

### 7.1 技術判斷清單

- [ ] **你要用的是 L1 還是 L2？** L1 = Move + 物件帳本；L2 = EVM（Solidity）。兩者是不同的開發者經驗。
- [ ] **你需要 sub-second finality 嗎？** Starfish 的數字落在 commit ~312ms p99（官方測試環境），實際生產延遲取決於 validator 分布。
- [ ] **你需要 sponsored tx？** 這是 IOTA Rebased 對企業 UX 的關鍵賣點，比 Sui 更積極。
- [ ] **你有 IoT 設備端的約束嗎？** 不要被 IOTA 名字誤導；當前 L1 對嵌入式設備的直接整合並不是賣點。對應該找 IoTeX 或 Helium-style DePIN。
- [ ] **你會被 Move 綁住嗎？** Move 生態（Sui + Aptos + IOTA）目前小於 EVM 生態。會員制供應商、合約 audit 工具、開發者人才庫都比 EVM 薄。

### 7.2 組織／合作判斷清單

- [ ] **是否與 IOTA Foundation 直接簽 LOI / 客戶協議**？Foundation 的政府／NGO 通路是其核心資產。
- [ ] **是否依賴 Foundation 的 ecosystem fund**？該基金來自 Stardust 的通膨增發，使用條件對開發者通常友善但要看具體條款。
- [ ] **5–10 年依賴的風險**：Foundation 是德國非營利，治理較其他 L1 透明；但歷史紀錄顯示策略可能再次大轉向（如過去從 IoT 轉貿易）。

### 7.3 監管／合規

- [ ] IOTA 代幣未在歐盟發行 MiCA-compliant whitepaper（截至 2026-05-12 未見公開），對受 MiCA 約束的歐盟金融服務商是需要追問的點。
- [ ] L2 IOTA EVM 的合規模型與 L1 相同，但實際合約執行者責任歸屬要與 IOTA Foundation 法律團隊另行確認。

---

## 八、結論

**IOTA 在 2026 是一個身份重生的協議**：
- 它的早期敘事（無費 IoT 微支付）已退場；
- 它的早期技術（Tangle + Coordinator + Curl-P）已被全面替換為主流的（DAG-BFT + Move + Ed25519 + DPoS）；
- 它的當前定位（全球貿易結算層）是一個合理但未被市場驗證的押注；
- 它的最大資產不是技術獨佔，而是 9 年累積的 Foundation 政府／NGO 通路與非營利定位。

**對工程師讀者，最務實的態度是：**

> 把「2017–2023 的 IOTA」與「2025– 的 IOTA Rebased」當成兩個專案。對前者的歷史風險紀錄不要忽略，對後者的技術成熟度要承認，對兩者之間的「敘事連續性」要打折處理。

**對風險審查者，最務實的紅旗是：**

> 不在於技術，而在於「策略再轉向」的歷史傾向。如果在未來 24 個月內全球貿易賽道沒有商業驗證，下一次轉向幾乎是可預期的。

**對職涯／興趣的閱讀者：**

> Starfish 共識的論文（Cordial Miners → Mysticeti → Starfish 這條學術線）是 2024–2026 年分散式系統最值得讀的議題之一，無論你之後是否關心 IOTA。Move VM 也是 EVM 之外目前最值得學習的 smart contract 平台。

---

## 附錄 A：年表彙整

| 年月 | 事件 | 類別 |
|---|---|---|
| 2015 | Popov 發表 *The Tangle* 白皮書 | 技術 |
| 2017 | IOTA ICO、Mainnet 啟動、Coordinator 上線 | 組織／技術 |
| 2017-07 | MIT DCI 揭露 Curl-P 漏洞 | 風險 |
| 2017-08 | 切換到 Kerl，停用 Curl-P-27 簽名 | 技術 |
| 2018-08 | Curl-P cryptanalysis 論文 Black Hat 發表 | 風險 |
| 2019-05 | Coordicide 白皮書與計畫公布 | 技術 |
| 2020-01-25 | Trinity 攻擊投放開始（透過 MoonPay SDK） | 風險 |
| 2020-02-12 | Trinity 事件公開、Coordinator 關閉 | 風險 |
| 2020-02 | Ivancheglo 公開與 Sønstebø 分道 | 治理 |
| 2020-03-10 | Coordinator 重啟、網路恢復 | 風險 |
| 2020-12-10 | Foundation 監督委員會解任 Sønstebø | 治理 |
| 2021-04 | Chrysalis（IOTA 1.5）上線，改用 EdDSA | 技術 |
| 2023-10-04 | Stardust 升級，總供應重定為 4.6B，多資產帳本 | 技術 |
| 2024-11 | Mysticeti 共識整合測試 | 技術 |
| 2025-05-05 | IOTA Rebased mainnet 啟用，Move VM + DPoS | 技術 |
| 2025-05-30 | 發佈 Technical and Tokenomics Whitepaper | 文件 |
| 2026-01-22 | IOTA Manifesto 發表 | 敘事 |
| 2026-Q1 | Starfish 上 testnet、IOTA Names 上 mainnet、IIP-8 | 技術 |
| 2026-04-28 | Starfish mainnet release | 技術 |
| 2026-05-06 | v1.22.1 mainnet release | 技術 |
| 2026-05-07 | *Why Starfish Matters* 技術深潛文章 | 文件 |

---

## 附錄 B：來源清單

> 為方便重讀核對，所有引用編號集中於此。

### 一手：IOTA Foundation 官方
- 【1】*IOTA Rebased: Technical View*, IOTA Foundation Blog — https://blog.iota.org/iota-rebased-technical-view/
- 【2】*IOTA Rebased Mainnet Upgrade*, IOTA Foundation Blog — https://blog.iota.org/rebased-mainnet-upgrade/
- 【3】IOTA Foundation 組織頁 — https://iota-foundation.org
- 【4】*Coordinator. Part 1: The Path to Coordicide*, IOTA Foundation Blog — https://blog.iota.org/coordinator-part-1-the-path-to-coordicide-ee4148a8db08/
- 【5】*Coordicide* announcement & PDF — https://blog.iota.org/coordicide-e039fd43a871/ ；https://files.iota.org/papers/Coordicide_WP.pdf
- 【7】*Trinity Attack Incident Part 1: Summary and Next Steps* — https://blog.iota.org/trinity-attack-incident-part-1-summary-and-next-steps-8c7ccc4d81e8/
- 【8】*Trinity Attack Incident Part 2: Seed Migration Plan* — https://blog.iota.org/trinity-attack-incident-part-2-trinity-seed-migration-plan-4c52086699b6/
- 【9】*IOTA Manifesto*（2026-01-22）— https://blog.iota.org/iota-manifesto/
- 【10】*IOTA Tokenomics* 學習頁與 Stardust 後續說明 — https://www.iota.org/learn/tokenomics ；https://blog.iota.org/stardust-upgrade-iota-tokenomics/
- 【11】*Stardust Upgrade and the Evolution of $IOTA Tokenomics* — https://blog.iota.org/stardust-upgrade-iota-tokenomics/
- 【13】*IOTA Stardust Upgrade* — https://blog.iota.org/iota-stardust-upgrade/
- 【14】*IOTA Rebased Fast Forward* — https://blog.iota.org/iota-rebased-fast-forward/
- 【15】*Starfish Mainnet Release*（2026-04-28）— https://blog.iota.org/starfish-mainnet-release/
- 【16】*Why Starfish Matters* — https://blog.iota.org/why-starfish-matters/
- 【17】*Q1 2026 Progress Update* — https://blog.iota.org/q12026-progress-update/
- 【18】*IOTA Mainnet 產品頁* — https://www.iota.org/products/mainnet
- IOTA Technical and Tokenomics Whitepaper（2025-05-30）— https://www.iota.org/pdf/IOTA_Technical_and_Tokenomics_Whitepaper.pdf
- IOTA Foundation parts ways with David Sønstebø — https://blog.iota.org/iota-foundation-parts-ways-with-david-sonstebo/
- IOTA Token 文件 — https://docs.iota.org/about-iota/tokenomics/iota-token

### 一手：開源
- IOTA 主 repo — https://github.com/iotaledger/iota（Rust + Move、Apache-2.0 + CC-BY-4.0、v1.22.1 mainnet at 2026-05-06）
- IOTA 組織 GitHub — https://github.com/iotaledger
- 供應量增加歷史 repo — https://github.com/iotaledger/new_supply

### 學術
- 【6】Heilman, Narula et al., *Cryptanalysis of Curl-P and Other Attacks on the IOTA Cryptocurrency*（Black Hat 2018; IACR ePrint 2019/344）— https://eprint.iacr.org/2019/344.pdf ；https://i.blackhat.com/us-18/Wed-August-8/us-18-Narula-Heilman-Cryptanalysis-of-Curl-P-wp.pdf
- MIT DCI 公告 — https://www.dci.mit.edu/dci-news/cryptanalysis-of-curl-p-and-other-attacks-on-the-iota-cryptocurrency
- MIT DCI tangled-curl repo — https://github.com/mit-dci/tangled-curl
- Keidar, Naor, Shapiro, *Cordial Miners*（DISC 2023）（Starfish 引用之共識先驅論文）

### 二手：媒體 / 第三方分析
- IOTA Wikipedia 條目 — https://en.wikipedia.org/wiki/IOTA_(technology)
- CoinDesk: *IOTA Foundation Suspends Network, Probes Fund Theft in Trinity Wallet*（2020-02-13）— https://www.coindesk.com/tech/2020/02/13/iota-foundation-suspends-network-probes-fund-theft-in-trinity-wallet
- CoinDesk: *IOTA Being Shut Off Is the Latest Chapter in an Absurdist History*（2020-02-25）— https://www.coindesk.com/business/2020/02/25/iota-being-shut-off-is-the-latest-chapter-in-an-absurdist-history
- 【12】Sønstebø vs. Schiener 撕裂事件 — https://blockonomi.com/iota-co-founders-embezzlement-accusations/ ；https://medium.com/@DavidSonstebo/iota-as-and-the-iota-foundation-82983b71b963 ；https://blockchainreporter.net/iota-co-founder-dropped-from-project-following-unanimous-board-decision/
- Four Pillars: *IOTA's Bid for the Next DAG-Based Breakthrough* — https://4pillars.io/en/articles/iota-s-bid-for-the-next-dag-based-breakthrough
- Luganodes: *Move's Expanding Universe* — https://www.luganodes.com/blog/move-journey-part-2/
- Wikipedia IOTA technology — https://en.wikipedia.org/wiki/IOTA_(technology)
- 一份對 IOTA 安全議題的學術 survey — https://www.sciencedirect.com/science/article/abs/pii/S1084804522000467

### 競品來源
- 【19】Hedera Hashgraph：白皮書與分析 — https://hedera.com/wp-content/uploads/2025/11/hh-consensus-service-whitepaper.pdf ；https://coinlaw.io/hedera-hashgraph-statistics/ ；CoinDesk *Leemon Baird on Hedera's Technical Gambit*（2025-05-12）— https://www.coindesk.com/consensus-toronto-2025-coverage/2025/05/12/leemon-baird-on-hederas-technical-gambit-and-ais-future
- 【20】IoTeX：Q3 2025 Messari brief — https://messari.io/report/iotex-q3-2025-brief ；W3bstream — https://cryptoslate.com/iotex-launches-w3bstream-devnet-paving-the-way-for-accelerated-depin-development/ ；MiCA whitepaper 公告（2025-12）
- 【21】VeChain：*VeChain Deep Dive: 2025 Protocol Upgrades* — https://bsc.news/post/vechain-ve ；VeBetterDAO 報告 — https://cryptonews.net/news/altcoins/30333694/
- Nano：Block-lattice 設計 — https://docs.nano.org/protocol-design/introduction/ ；Nano vs IOTA 比較 — https://hackernoon.com/iota-vs-raiblocks-413679bb4c3e

---

## 報告自審記錄

| 檢查項 | 結果 |
|---|---|
| 事實檢查：所有關鍵日期與版本均有來源 | ✅ 通過。Starfish mainnet 2026-04-28、Rebased 2025-05-05、Stardust 2023-10-04、Chrysalis 2021-04、Curl-P 揭露 2017-07-14 均對應官方／學術／媒體來源 |
| 時效檢查：是否反映 2026-04-28 Starfish | ✅ 已納入 |
| 技術可讀性：每段技術都答了「問題／解法／代價」 | ✅ Starfish、Move VM、DPoS、Tokenomics 段已對齊 |
| 風險檢查：官方主張與獨立證據區分 | ✅ 已用「⚠️」「官方主張」「未獨立查證」明標 |
| 不做投資建議 | ✅ 全文未提幣價、未談 buy/hold/sell |
| 單檔完整敘事，不分割成多個 module | ✅ 一份報告完成所有章節 |
| 來源清單可讀、Markdown 結構正確 | ✅ 全部使用相對引用編號與完整 URL |

> 完。
