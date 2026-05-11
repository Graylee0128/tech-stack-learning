# Cardano 組織與核心技術 — 橫縱分析報告

> 工程師視角的全貌理解，不做投資建議。
>
> 更新日期：2026-05-12
> 維護者：自用研究筆記
> 篇幅：約 10,000 中文字

---

## 0. 為什麼這份報告值得讀

如果你是 Cloud / Platform / SRE 出身，第一次認真看 Cardano，很容易卡在兩種誤解之間：一種是粉絲社群的「最嚴謹的區塊鏈」，另一種是反方的「論文很多但沒人用」。這兩種說法都對也都不對。

Cardano 真正的特殊之處不在某一個技術組件，而在它從 2015 年開始就押注一件事：**區塊鏈這個東西要當成公共基礎設施做，所以開發流程要長得像航太或晶片驗證，而不是像 Web2 的 move-fast-break-things**。這個哲學決定了它的研究流程、開發語言選擇、共識協議、帳本模型、甚至最終的鏈上治理設計。所有「為什麼這麼慢」「為什麼這麼複雜」的問題，幾乎都能在這個哲學上找到答案。

這份報告的兩條主線是：

- **組織治理線：** IOG → Cardano Foundation → EMURGO → Intersect → CIP-1694 → Chang → Plomin → Voltaire。
- **技術演進線：** Byron → Shelley → Goguen → Basho → Voltaire，對應「能跑 → 能去中心化 → 能做合約 → 能擴容 → 能自治」。

兩條線在每個時代會交叉一次，因為技術版本決定了權力可以下放多少，而治理結構決定了技術下一步可以動什麼。

橫軸我們會把 Cardano 放回主流 L1 的座標系，跟 Ethereum、Solana、Polkadot、Cosmos 對照。ADA 代幣只當背景變數出現，談激勵、治理權重、treasury 的角色，不談價格。

---

## 1. 縱軸 Part 1 — 起源與哲學定錨 (2015–2017, Byron)

### 1.1 IOG 起源與和 Ethereum 的分歧

2015 年，Charles Hoskinson 和 Jeremy Wood 在離開 Ethereum 早期創辦人團隊之後，於瑞士成立 **IOHK（Input Output HK，後改名 IOG）**。Hoskinson 離開的關鍵分歧是組織形式：他主張一條公鏈要有持續的研究預算、有正式法人實體、有可被審計的程序，而不是純粹的非營利基金會加開源社群。這個分歧在當時被很多人視為「太企業化」，但它後來變成 Cardano 整個體系的基因。

差不多同時，日本投資公司 **EMURGO** 在東京成立，負責商業採用、企業合作、教育與孵化；瑞士再成立 **Cardano Foundation**，負責品牌、合規、生態關係。一開始就形成一個刻意的三足結構：研究與開發、商業推廣、公共代表，分屬不同實體。後面我們會看到這個結構在 2023 年再加上 Intersect 變成四足，並在 2024–2025 年透過鏈上治理把實質權力從這些公司轉到代幣持有者與選出的代表手上。

### 1.2 「研究先行」是什麼意思

很多公鏈會說自己「以研究為基礎」，但 Cardano 把這件事字面執行：所有核心協議在實作之前，必須先有經過 peer review 的學術論文。Ouroboros 這個 PoS 家族的第一篇論文 2017 年發在 CRYPTO（密碼學最頂尖的會議之一），之後每一次共識機制升級——Praos、Genesis、Crypsinous、Chronos——都對應一篇 IACR ePrint 的論文。

對 SRE / 平台工程的腦袋來說，這個流程的類比是：**先寫 RFC、再寫 design doc、再寫程式碼**，而且 RFC 要被外部專家審過才算數。代價是慢；好處是當你後面要說「為什麼 slot leader 是這樣選的」、「為什麼這個資料結構這樣設計」，你拿得出證明，而不是「因為作者當時想這樣」。

### 1.3 Byron 主網 (2017 Sep) — 第一條腿

2017 年 9 月，Cardano 主網以 **Byron** 紀元啟動。這時的鏈非常「Bitcoin 風」：

- 用 **UTXO 模型**而不是 account 模型，但還沒有 Extended UTXO。
- **沒有智能合約**、沒有原生 staking、沒有 dApp。
- 共識用的是 Ouroboros Classic，但出塊節點仍由 IOG / Foundation / EMURGO 運行，**沒有真正去中心化**。
- 錢包是 Daedalus 與 Yoroi 兩條線，分別代表 full node 與輕錢包路徑。

Byron 對應的工程能力是「鏈能跑、轉帳能用、有可審計的協議規格」。對應的組織狀態是「公司化的核心團隊主導，社群是觀眾」。這個時期最常見的批評就是「上面的東西都沒有，跟 Bitcoin 比沒有意義」——是事實，但這條鏈當時被定位成基礎設施先決方案，不是產品。

---

## 2. 縱軸 Part 2 — 去中心化與 staking (2020, Shelley)

### 2.1 Ouroboros 家族：可證明安全的 PoS

要理解 Shelley，你得先理解 Cardano 的共識協議家族 **Ouroboros**。它不是單一協議，而是一系列：

| 版本 | 解決的問題 | 上線 |
|---|---|---|
| Ouroboros Classic | 第一個可證明安全的 PoS | 2017 |
| Ouroboros BFT | Byron 過渡到 Shelley 的橋接 | 2020 初 |
| Ouroboros Praos | 抗適應性攻擊、私有 slot leader 選舉 | 2020 (Shelley) |
| Ouroboros Genesis | 從創世塊安全 bootstrap，不需信任檢查點 | 設計完成、漸進採用 |
| Ouroboros Crypsinous | 加上隱私（zero-knowledge） | 研究中 |
| Ouroboros Chronos | 把全網時間同步也內生化 | 研究中 |

對工程師最直觀的類比：把 PoS 想成「分散式 cron 排程」，每一個 **slot**（約 1 秒）會抽出一個 leader 來出塊，**epoch** 是 5 天（432,000 slots）為一個結算週期。Praos 用 **VRF（Verifiable Random Function）** 做 slot leader 選舉——你不會事先知道下一秒誰要出塊，但事後可以驗證「沒錯就該是這個人」。這擋掉了一大類「先攻擊將要出塊的人」的 grinding attack。

安全假設是 **honest majority of stake**：只要誠實的 stake 超過 50%，鏈是安全的。這比 PoW 的 honest hash 多了一個額外保護：在 Praos 中，攻擊者就算知道未來的 stake 分布，也算不出未來的 slot leader 是誰，因為 VRF 的種子要等到該 epoch 開始才確定。

### 2.2 Stake pool 與 delegation：經濟去中心化

Shelley 升級的第二個核心是 **stake pool 體制**。它解決一個真實問題：大部分持幣者不想自己 24/7 維運節點，但又不想把錢包私鑰交給別人。

Cardano 的解法是 **non-custodial delegation**：你保留私鑰，只是把 staking right（投票權與出塊權）委託給某個 stake pool。pool 替你出塊、領獎勵，再扣固定費用後分回給 delegators。

幾個值得記的數字與機制：

- **k = 500**：協議參數，目標是讓網路飽和於 500 個 pool。當一個 pool 的 stake 超過「總 stake / k」這條飽和線，獎勵會被打折，逼大 pool 拆分或讓 delegators 改委託小 pool。
- **a0 參數**：pool operator 自己 pledge 的 ADA 越多，獎勵越好，目的是讓 pool 有 skin in the game。
- **epoch = 5 天**：獎勵按 epoch 結算，**獎勵會延遲兩個 epoch 才入帳**（為了讓 stake snapshot 不能被新買進的幣套利）。

這套設計在工程上是個漂亮的「自我去中心化」機制：經濟誘因把網路推離寡頭結構。實際結果是 Cardano 在 SPO 數量上長期保持在 ~2,500–3,000 個註冊 pool、~1,300 個 active pool 上下，**Nakamoto Coefficient（要拿到 51% 出塊需要多少獨立實體合謀）**通常在 20–30 之間，明顯高於多數 L1。

### 2.3 組織狀態：三足結構真正開始運轉

Shelley 之後，IOG / Foundation / EMURGO 三足結構第一次有了實質意義：

- **IOG** 寫程式碼、發論文、運維部分基礎設施。
- **Cardano Foundation** 開始大量處理交易所上架、合規、學術夥伴、地區社群。
- **EMURGO** 推商業 PoC、企業整合、孵化 startup。

但這時候的「去中心化」其實只是出塊層的去中心化。**協議升級、roadmap、財庫使用，仍由這三家公司主導**。社群的影響力靠 Twitter 和論壇發聲，沒有正式投票權。這個落差在 2021–2024 年逐漸變成主要的政治壓力，最後催出 CIP-1694。

---

## 3. 縱軸 Part 3 — 智能合約與 EUTXO (2021, Goguen/Alonzo)

### 3.1 為什麼選 EUTXO 而不是 account model

2021 年 9 月，**Alonzo 硬分岔**啟動智能合約能力。最關鍵的設計決策是：**Cardano 採用 Extended UTXO 模型，而不是學 Ethereum 的 account model**。這個決策影響每個寫過 Plutus 合約的人。

讓我用一個工程類比說清楚：

- **Account model（Ethereum 路線）：** 像關聯式資料庫的一張表，欄位是 `(address, balance, nonce, storage_root)`。每筆交易是「在這張表上做 UPDATE」。
- **UTXO model（Bitcoin 路線）：** 像 Git 物件圖。沒有「帳號」，只有「未被花掉的輸出」。每筆交易消耗舊的 UTXO，產生新的 UTXO。
- **Extended UTXO（Cardano）：** 在 UTXO 上掛一段「驗證腳本」與「datum（資料）」。當你想花掉一個 EUTXO，你必須提供 redeemer，讓附在這個 EUTXO 上的驗證腳本回傳 True。

EUTXO 的好處是**本地可決定性**：當你構造一筆交易，你已經可以在本機完全算出它能不能成功、會花多少 gas，因為它只依賴它消費的那些 UTXO。Ethereum 的 account model 因為共享 storage，你看似在 wallet 模擬成功的交易，**上鏈後可能被其他人插隊改動 storage 而失敗**——這就是 MEV/sandwich attack 與「pending pool 撞單」的底層成因之一。

對應 SRE 直覺：EUTXO 像「不可變物件 + pure function」，account model 像「可變狀態 + 鎖機制」。前者並行性極好（兩筆不碰同樣 UTXO 的交易可以無衝突並排處理），後者天然容易產生熱點 storage 競爭。

### 3.2 EUTXO 的工程代價

EUTXO 不是免費的午餐，它有幾個讓 Solidity 開發者頭痛的問題：

1. **單一全域狀態的合約寫起來很彆扭。** 在 Ethereum 寫一個「全網共用的 AMM 池」，你只要操作一個 storage slot。在 EUTXO，你要把池子表達為「一個 UTXO」，意味著**同一個池子在同一 slot 內只能被一筆交易動到**。Cardano DEX 解法是「batcher」模式：用戶下單變成 UTXO 排到 batcher 的隊列裡，batcher 一次性把多筆訂單聚合進池子。這個架構在去中心化、抗 MEV 上更乾淨，但寫起來更繞，使用者初次接觸會困惑「為什麼我的 swap 要等」。
2. **狀態壓縮挑戰：** UTXO 集合本身會膨脹。Cardano 的解法之一是把長期不動的 UTXO 累積進 boot 過程，並研究用 Mithril 等聚合簽章加速冷啟動。
3. **開發者體驗：** Plutus 用 Haskell 子集寫，前期工具鏈不友善、文件偏學術。

### 3.3 Plutus / Aiken / Marlowe — 智能合約的三條腿

| 工具 | 定位 | 適合誰 |
|---|---|---|
| **Plutus (PlutusTx + Plutus Core)** | 主流。Haskell embedded DSL 編譯到 Plutus Core | 想徹底控制、能吃下 Haskell 學習曲線的核心協議團隊 |
| **Aiken** | 2022 起的新興語言，Rust-like 語法，工具鏈現代化 | 大多數新合約 dev，現在算事實上的「第二選擇預設」 |
| **Marlowe** | 領域特化（金融合約），可視化建模 | 律師、商業分析師、金融結構設計者 |
| **OpShin** | 用 Python 子集寫 Plutus | Python 友善開發者 |

Aiken 的出現對 Cardano 生態是 game changer，它把 onboarding 門檻從「先學 Haskell」降到「會 Rust/TypeScript 大概一週能上手」，這直接反映在 2024 年之後新合約上線速度加快。

### 3.4 組織狀態：第一次治理壓力

Alonzo 上線之後，Cardano 第一次面對「合約上線了但 dApp 很少、流動性還沒進來、其他鏈已經跑很遠」的指責。社群裡開始出現對 IOG 主導 roadmap 的不滿。這個壓力直接推動了後面 Voltaire 路線——**如果繼續讓三家公司決定一切，這條鏈的合法性會被它的去中心化承諾反咬**。

---

## 4. 縱軸 Part 4 — 擴容 (Basho)

Basho 紀元不是一次硬分岔，而是一系列擴容工作的總稱。對工程師而言，最值得理解的有兩個：**Hydra** 與 **Mithril**。

### 4.1 Hydra — Isomorphic State Channels

Hydra 不是「Cardano 的 L2」這麼簡單。它的設計叫 **isomorphic state channels**：

- 一群參與者（最多大約 100 人）打開一個 **Hydra Head**，把鏈上 EUTXO 鎖進去。
- 在 Head 內部，他們繼續用**完全一樣的 Plutus 與 EUTXO 語意**做交易，只是不過鏈。
- 任何時候有人想退出，可以把 Head 的最新狀態結算回主鏈。

「同構」的意思是：你在 Head 內跑的智能合約跟主鏈上的完全一致，**不用重寫合約**。這對開發者是巨大的價值。對比 Optimism、Arbitrum 那種 EVM-compatible L2 仍然要處理跨層橋接、bridge security、不同 fork 行為，Hydra 在語意層是「同一個世界的小房間」。

代價是 Hydra Head 是參與者集合鎖定的，不適合「公開、任意人加入」的全網級擴容，而適合**已知參與者的高頻互動**：遊戲對局、支付通道、機構間清算。把 Hydra 想成「VPN 內部的快速通道」，主鏈則是「公共網路」。

### 4.2 Mithril — Aggregated Signatures for Fast Bootstrap

Mithril 解的是另一個問題：**新節點同步太慢**。

它用 **STM (Stake-based Threshold Multi-signature)** 來把一群 SPO 對「epoch X 的狀態快照是這個 hash」的簽名聚合成一個小簽章。新節點要 bootstrap 時，**只需要驗一個 Mithril 證書**就能信任快照，再從快照接著同步，不用從創世塊重新跑全部歷史。

這對輕客戶端、行動裝置、跨鏈橋的「快速證明源鏈狀態」場景特別重要。橫向比一下，Ethereum 對應的研究是 **Verkle Trees + stateless clients**，Cosmos 是 **light client + state sync**，Solana 是 **snapshot + accounts hash**。Mithril 的差異是：它把可信任性綁回到 stake，而不是綁回到「一群預設的 sync 伺服器」。

### 4.3 Sidechain 與 Partner Chains

2023–2024 年，IOG 推出 **Partner Chains** 框架：讓任何第三方（包括非 EVM 環境，例如 Substrate 的鏈）可以借 Cardano 的 SPO 當共識提供者，做出自己的 sidechain。這條路線目標是「不把 Cardano 主鏈變成全宇宙計算中心，而是讓主鏈當共識服務的供應端」。從架構角度，這跟 Cosmos 的 ICS（Interchain Security）、Polkadot 的 Parachain 思路接近，但執行細節不同——後面橫軸對比會展開。

---

## 5. 縱軸 Part 5 — 治理上鏈 (Voltaire, 2024–2025)

這是 Cardano 故事裡最大的政治轉折。

### 5.1 CIP-1694：把治理寫進協議

**CIP-1694** 是 Cardano Improvement Proposal 中史上最受關注的一份，由 Charles Hoskinson 與多位 IOG / Foundation 研究員共同主導，2022 年底開始公開草案，2023 年密集做了全球工作坊（Edinburgh、Buenos Aires、Nairobi 等），把社群意見往回灌進設計。

它要解決的事情很單純：**讓三家公司退場，把治理權交給代幣持有者與選出的代表**。但實作不單純，因為這條鏈上有 100 億顆 ADA 的 stake、有 2,500+ 個 SPO、有跨國家的合規問題、有財庫（treasury）需要持續決策。

CIP-1694 的核心設計是三權分立：

| 角色 | 縮寫 | 數量 | 怎麼產生 | 主要權力 |
|---|---|---|---|---|
| **Delegated Representatives** | DRep | 任意 | 任何人註冊成為 DRep，幣的持有人把投票權委託給 DRep | 對治理動議投票 |
| **Stake Pool Operators** | SPO | ~1,300 active | 已經在運作出塊 | 對特定類型動議有否決或必過要求 |
| **Constitutional Committee** | CC | 7 人（會變動） | 由代幣持有者選舉 | 守護憲法，動議若違憲可以否決 |

**任何治理動作（governance action）必須通過上述三權的相應門檻才能執行**。動作類型包括：

- 修改協議參數（區塊大小、k、a0、minimum pool cost 等）
- 動用 treasury 撥款
- 硬分岔啟動
- 修改憲法
- 對 CC 投信任 / 不信任

每個動作類型對 DRep / SPO / CC 的門檻組合不同。例如協議參數修改要 DRep + SPO 雙過；硬分岔要 DRep + SPO + CC 三過；treasury 動用主要看 DRep + CC。這是有意識的「不同決策不同 quorum」設計，避免某一方擁有單獨決定權。

### 5.2 Chang Hard Fork (2024 年 9 月)

Chang 硬分岔（紀念已故密碼學家 Andrew Chang，但官方說法主要是紀念社群成員 Chang Hwan）把 CIP-1694 的第一階段啟動：DRep 系統開始註冊，但實際治理門檻還沒 enforce，期間視為 **bootstrap phase**。

工程上 Chang 的意義是：**鏈上多了一整套新的交易型別**——註冊 DRep、委託投票權、發起動議、投票。這些都不是模擬，是真實的 transaction body 變動，所有錢包、節點、瀏覽器都得跟進。

### 5.3 Plomin Hard Fork (2025 年初)

Plomin 是第二階段，把治理門檻正式 enforce。從 Plomin 之後：

- 協議參數變更必須走鏈上動議。
- IOG、Foundation、EMURGO 不能再單方面決定 roadmap。
- treasury 的每一筆撥款都要 DRep + CC 通過。

換句話說，**Plomin 之後 Cardano 不再是一家公司管的開源專案，而是一條按自己憲法運作的鏈**。

### 5.4 Intersect — 治理的執行機構

但「鏈上治理」不能憑空運作——你需要一個會持續寫提案、跑會議、做技術維護、聽社群意見的法人實體。這就是 **Intersect** 的角色。

Intersect 是 2023 年成立的會員制組織（Member-Based Organization, MBO），構造接近 Apache Foundation 或 Linux Foundation：

- 任何人或組織可以付費入會（個人小額、企業大額）。
- 內部有多個工作組（Open Source Committee、Product Committee、Civics Committee 等）。
- Intersect 接手原本 IOG 維護的核心程式碼庫（Cardano Node、CLI、ledger 等）。
- Intersect 是治理動議在鏈下的彙整、寫提案、跑討論、做風險分析的中介。

注意 Intersect 不擁有否決權——它沒有票。它的合法性來自「會員制 + 開放治理 + 鏈上動議仍由 DRep / SPO / CC 決定」。它類似於把 Linux Foundation + Apache 的角色搬到區塊鏈上：**它做枯燥的維護與協調工作，但實質權力在鏈上**。

---

## 6. 組織深入分析 — 權力是怎麼一步步從公司搬到鏈上的

把 2015 到 2025 這十年壓縮成一張權力分布圖：

| 時期 | 誰決定協議升級 | 誰維護程式碼 | 誰用 treasury | 誰代表 Cardano |
|---|---|---|---|---|
| Byron (2017) | IOG | IOG | (還沒有正式 treasury) | Foundation |
| Shelley (2020) | IOG（社群有諮詢） | IOG | IOG + Foundation | Foundation |
| Goguen / Basho (2021–2023) | IOG（社群壓力升高） | IOG | IOG + Foundation | Foundation + EMURGO |
| Chang (2024) | DRep + SPO（bootstrap） | Intersect 接管中 | DRep + CC 通過 | 鏈上社群 |
| Plomin 之後 (2025+) | DRep + SPO + CC | Intersect 主導，IOG 變承包商 | DRep + CC | 鏈上社群 |

幾個非顯然的觀察：

**IOG 的角色從「擁有者」變成「最大承包商」。** Plomin 之後 IOG 還在，但要靠 treasury 撥款拿到合約，跟其他開發團隊一起競標。這對一家公司是巨大的角色轉換——你蓋的房子變成別人的，你只能投標當管家。從工程紀律角度，這逼 IOG 把過去「內部慣例」全部正規化成「投標書 + 驗收標準」。

**Cardano Foundation 變成合規與法律窗口。** 它不寫程式，但繼續代表 Cardano 與監管機關、傳統金融、學術界打交道。它的合法性來自瑞士法人地位，不來自代幣。

**EMURGO 失去了核心地位。** 在 Voltaire 之後，EMURGO 仍存在但影響力下降，因為「商業採用」這件事在鏈上治理框架下變成一群獨立公司各自做的事，不再需要中央推手。

**Intersect 成為新的協調中樞，但故意做得「無權」。** 它的設計就是「做最多事、拿最少票」，目的是避免再次出現一家公司主導的局面。

**社群代表（DRep）變成一個新興職業。** 已經出現專業 DRep——技術背景、寫公開投票理由、做政策研究的人。他們的合法性來自「有多少 ADA 委託票」，類似議員。

---

## 7. 橫軸對比 — 把 Cardano 放回 L1 座標系

接下來把 Cardano 和四條主流 L1 放在同一張表上比。**比較維度**用工程師關心的：技術哲學、帳本模型、共識、開發者體驗、治理、生態速度、安全取向。

### 7.1 vs Ethereum

Ethereum 是 Cardano 的「天然對照組」——Hoskinson 從 Ethereum 出來，整條鏈很多設計可以解讀為「Vitalik 那邊我同意 → 保留，我不同意 → 換掉」。

| 維度 | Ethereum | Cardano |
|---|---|---|
| 帳本 | Account model | Extended UTXO |
| 共識 | PoS (Gasper = Casper FFG + LMD GHOST) | Ouroboros Praos |
| 智能合約 | EVM, Solidity / Vyper | Plutus / Aiken / Marlowe |
| 升級流程 | EIP + AllCoreDevs 會議 + 客戶端執行 | CIP + 鏈上治理 |
| 客戶端多樣性 | 高（Geth, Nethermind, Besu, Erigon, Reth；Prysm, Lighthouse, Teku, Nimbus, Lodestar） | 中（Cardano Node 為主，Amaru 等替代正在開發） |
| Roadmap 速度 | 快、社群驅動 | 慢、研究驅動 |
| MEV | 已成熟產業（Flashbots） | EUTXO + batcher 模式天然抑制大部分 sandwich MEV |
| 開發者社群 | 巨大、成熟 | 中小、Aiken 之後成長 |

**Ethereum 跟 Cardano 的根本分歧不在 PoS，而在「如何把不可信參與者拉進共識」。** Ethereum 用 32 ETH 質押 + slashing；Cardano 用 stake pool delegation + 經濟誘因抑制集中化。前者更個體化、適合機構運作；後者更平等化、犧牲一些 slashing 的清晰性換取廣泛參與。

**升級流程：** Ethereum 是「客戶端團隊先寫，硬分岔上鏈」；Cardano（Plomin 之後）是「鏈上動議通過，IOG / Intersect 等才能執行」。Ethereum 的方式更敏捷，但治理權集中在客戶端團隊與 EF；Cardano 慢，但理論上抗捕獲（capture-resistant）更強。

### 7.2 vs Solana

Solana 是 Cardano 的反面：**極致追求吞吐**。

| 維度 | Solana | Cardano |
|---|---|---|
| 哲學 | 越快越好，硬體要求高沒關係 | 安全與去中心化優先 |
| TPS | 實測上萬 | 主鏈百級 (Hydra Head 可上萬) |
| 區塊時間 | 400ms | 20s 平均 |
| 共識 | PoH + PoS (Tower BFT) | Ouroboros Praos |
| 客戶端 | Agave（Solana Labs），Firedancer（Jump）發展中 | Cardano Node 為主 |
| 宕機紀錄 | 多次主網中斷（2021–2024） | 主網 0 次中斷 |
| Validator 入場門檻 | 高（硬體 + 質押） | 低（任何人能跑 SPO） |
| MEV | 高，已有 Jito 等基建 | 結構性抑制 |

工程師最重要的觀察：**Solana 把區塊鏈當高頻交易系統設計，Cardano 把區塊鏈當公共記錄系統設計**。兩種哲學各有應用範疇。如果你要做衍生品交易所，Solana 的延遲與吞吐是必要條件；如果你要做身份系統、產權登記、跨國清算憑證，Cardano 的可審計性與穩定性更貼合。

Solana 的多次宕機（2022 年 9 月、2023 年 2 月等）跟它的 leader-based 高速出塊架構直接相關——任何一個 leader 異常就會引起連鎖。Cardano 的 Praos 因為 slot leader 由 VRF 隨機抽，沒有單一節點當「主要 leader」，可用性結構更分散。

### 7.3 vs Polkadot

Polkadot 跟 Cardano 是「兄弟鏈」——兩條鏈的創辦人都從 Ethereum 出來（Gavin Wood / Hoskinson），兩條鏈都用 Rust / Haskell 等強型別語言，兩條都極度看重正式設計。

| 維度 | Polkadot | Cardano |
|---|---|---|
| 安全模型 | Shared security (Relay Chain + Parachain) | 主鏈共識，sidechain 借 SPO 共識 |
| 治理 | OpenGov（已升級多次） | CIP-1694 / Voltaire |
| 開發語言 | Substrate (Rust) | Haskell / Plutus / Aiken |
| 升級 | Wasm runtime 升級，鏈上投票即可 | 硬分岔 + 鏈上動議 |
| 跨鏈 | XCM（原生） | Mithril + Partner Chains（晚發展） |
| 哲學 | 多鏈優先 | 單鏈為主，sidechain 補足 |

Polkadot 的 **runtime upgrade via WASM** 是一個非常聰明的工程設計：你不用硬分岔，鏈上跑的是一個 Wasm runtime，治理通過就直接換 runtime。Cardano 沒走這條，主因是 Cardano 早期 codebase 是 Haskell 編譯到 native，runtime 抽象沒做。換來的代價是 Cardano 每次升級都得協調全網升級節點，比較重。

但 Cardano 的賭注是「治理本身要慢，慢才能擋住惡意提案」。Polkadot 的 OpenGov 也走鏈上治理路線，但設計更接近 Web2 的「快速迭代」——可以發起動議、有 fast track、有 conviction voting（鎖更久權重更大）。兩條鏈在治理哲學上是同一個大方向，細節各有取捨。

### 7.4 vs Cosmos

Cosmos 是「主權鏈聯邦」的代表。它跟 Cardano 的對照很有啟發。

| 維度 | Cosmos (Hub + Zones) | Cardano |
|---|---|---|
| 安全模型 | 每條 zone 自己負責，可選 ICS 共享安全 | 單一主鏈 |
| SDK | Cosmos SDK (Go) | Plutus / Aiken |
| 跨鏈 | IBC (原生協議) | Mithril + Partner Chains |
| 治理 | 每條 zone 自己的 governance module | 全網 CIP-1694 |
| 終結性 | Tendermint BFT (即時終結) | Ouroboros 概率終結 |

**Cosmos 的賭注是「讓 1,000 條鏈各自做主，用 IBC 串起來」**；**Cardano 的賭注是「先把主鏈做到極穩，再以此為基底長出 sidechain」**。哪個對？取決於你對「同質性 vs 多樣性」的判斷。

實務上，Cosmos 的 IBC 已經是區塊鏈跨鏈標準的事實王者，但每條 zone 安全各自為政，有不少被惡意接管的案例。Cardano 主鏈從未被攻陷，但 sidechain 生態仍小。

---

## 8. 工程師視角 — Cardano 解決了什麼、犧牲了什麼

讀完縱橫兩條軸，可以給一個誠實的總結。

### 8.1 Cardano 真正做對的事

1. **可證明安全的 PoS。** Ouroboros 是第一個有完整密碼學證明的 PoS 協議家族。這對「不能宕、不能被攻陷」的應用是硬通貨。
2. **EUTXO 模型的局部可決定性。** 對清算、身份、產權登記、合規記錄這類「上鏈成功與否要在送出之前確定」的場景，EUTXO 提供 account model 給不了的保證。
3. **結構性抑制 MEV。** EUTXO + batcher 架構，讓 sandwich attack 等 MEV 樣式天然難以實施。
4. **長期主網可用性紀錄。** 主網從 2017 到現在，**0 次中斷**。對比 Solana 多次宕機，這個紀錄是有錢買不到的工程資產。
5. **鏈上治理的真正落地。** Plomin 之後 Cardano 是少數真把 roadmap 決定權交給鏈上代幣 + 代表的 L1。Polkadot OpenGov 在這方面是同類，但 Cardano 把「公司退場」做得更徹底。
6. **形式化驗證友善的開發語言。** Plutus / Aiken 走的是「可被機器驗證正確性」的方向，對金融基礎設施是必要條件。

### 8.2 Cardano 沒做好的事

1. **慢。** 從研究到上線常常以年計。當業界已經有 10 條 EVM 鏈跑 dApp 時，Alonzo 才剛上線；當 ETH rollup 生態已經爆發時，Hydra 還在優化。研究先行的代價是市場時機的代價。
2. **開發者門檻。** 即使有 Aiken，整個生態仍然遠比 EVM 系難上手。文件分散在 IOG、Foundation、Intersect、社群 wiki 之間，工程師體驗不如 Solidity + Hardhat 的成熟組合。
3. **生態冷啟動。** 缺乏現象級 dApp。DeFi、NFT、GameFi 都有，但規模相對小。資金流入慢，TVL 長期低於它的歷史敘事預期。
4. **治理複雜度。** CIP-1694 設計優雅但複雜。普通持幣者要理解 DRep、SPO、CC 的不同門檻、不同動作類型、不同投票週期，門檻不低。早期 DRep 投票率與委託率將是壓力測試。
5. **客戶端單一性。** Cardano Node 是主要實作，Amaru 等替代仍在開發。對比 Ethereum 的 5 個執行客戶端 + 5 個共識客戶端，Cardano 的客戶端多樣性是真實風險。
6. **創辦人個人色彩。** Hoskinson 仍是社群的精神領袖，他的言論對市場與社群有不成比例的影響。Voltaire 的去中心化能否徹底消化這種「創辦人引力」，是 2025–2027 年的觀察重點。

### 8.3 一句話定位

> Cardano 是一個押注在「公共基礎設施需要學術級紀律」的 L1，它的慢是有意為之，它的研究投入買到了長期可用性與形式化可驗證的合約環境，代價是錯過了短期市場熱度與開發者規模。

---

## 9. ADA 的角色（背景說明，不做投資判斷）

ADA 在這個體系裡擔任四個功能性角色，**這份報告只解釋它「是什麼」，不評估價格走向**。

1. **Staking 計算單位。** 你的 stake 決定你被選為 slot leader 的機率（透過 stake pool delegation）。
2. **治理權重。** Plomin 之後，你委託給某個 DRep 的 ADA 數量決定你那一票的權重。
3. **手續費單位。** 每筆交易的 gas 用 ADA 結算，min UTXO requirement 也用 ADA。
4. **Treasury 來源與計價。** 每個 epoch 出塊獎勵的一部分會撥入 treasury，未來透過鏈上動議撥款。

幾個非顯然的設計選擇：

- **沒有 burn 機制。** 大部分手續費流回 SPO 與 reserve，不像 ETH 的 EIP-1559 有 base fee burn。這是有意為之，因為 Cardano 認為 burn 會讓貨幣政策難以預測。
- **總量上限 450 億 ADA。** 但實際流通遠未達上限，因為「未發行的 ADA」會逐步從 reserve 釋放到 staking 獎勵與 treasury。
- **獎勵單調遞減。** 每個 epoch 從 reserve 撥出固定比例，所以早期獎勵率高、後期遞減。這是設計上的「指數衰減」激勵曲線。

如果你想問「ADA 該不該買」，這份報告刻意不答，因為任何答案都會是個人的風險偏好 + 資產配置的函數，不是研究報告該下的結論。

---

## 10. 工程師結論 — 什麼樣的問題適合用 Cardano

如果你只想拿一個結論回去做技術選型，我會這樣說：

**Cardano 適合：**

- 需要長期穩定運作（10 年級）的公共記錄系統：身份、產權、學歷、跨國證書。
- 需要交易行為在送出前可決定性極高的應用：合規清算、機構結算、保險理賠自動化。
- 想避開 MEV 與 sandwich 風險的金融原語：去中心化交易所（透過 batcher 模式）。
- 需要可驗證隨機性的應用：抽獎、隨機分配、密鑰更新（VRF 是 native primitive）。
- 跟非洲、東南亞、拉美等基礎設施合作的場景：Cardano Foundation 在這些區域長期經營，社群與在地團隊密度遠高於其他 L1。

**Cardano 不適合：**

- 高頻交易、衍生品撮合：Solana / 高效能 L2 更貼。
- 想快速上線 + 沿用 EVM 生態工具的應用：直接用 EVM 系。
- 需要瞬時最終性的清算：Tendermint 系（Cosmos zones）更合適。
- 對開發者 onboarding 速度敏感的早期專案：EVM 仍然是最低阻力選擇。

把這份報告當作一個座標系：你不需要愛上 Cardano，但你應該知道它在哪裡、為什麼在那裡、什麼時候它會是你的工具箱裡最合適的那一把。

---

## 11. 來源

主要來源優先採官方與一手資料。

### 官方與一手

- Cardano Roadmap — https://roadmap.cardano.org/
- Cardano Docs (Developer Portal) — https://docs.cardano.org/
- Cardano Improvement Proposals (CIPs) — https://github.com/cardano-foundation/CIPs
- CIP-1694 (On-Chain Governance) — https://github.com/cardano-foundation/CIPs/tree/master/CIP-1694
- Cardano Foundation — https://cardanofoundation.org/
- Input Output (IOG) — https://iohk.io/
- EMURGO — https://emurgo.io/
- Intersect MBO — https://www.intersectmbo.org/

### 學術論文（Ouroboros 家族）

- Ouroboros: A Provably Secure Proof-of-Stake Blockchain Protocol (CRYPTO 2017) — https://eprint.iacr.org/2016/889
- Ouroboros Praos: An Adaptively-Secure, Semi-Synchronous PoS Protocol (EUROCRYPT 2018) — https://eprint.iacr.org/2017/573
- Ouroboros Genesis (CCS 2018) — https://eprint.iacr.org/2018/378
- Hydra: Fast Isomorphic State Channels — https://eprint.iacr.org/2020/299
- Mithril: Stake-based Threshold Multisignatures — https://iohk.io/en/research/library/papers/mithril-stake-based-threshold-multisignatures/

### EUTXO 與 Plutus

- The Extended UTXO Model (FC 2020) — https://iohk.io/en/research/library/papers/the-extended-utxo-model/
- Plutus: A Functional Contract Platform — https://iohk.io/en/research/library/papers/plutus-a-functional-contract-platform/
- Aiken Language — https://aiken-lang.org/
- Marlowe — https://marlowe.iohk.io/

### 治理

- CIP-1694 Final Text — 同上
- Intersect Constitution Documents — https://www.intersectmbo.org/news
- Chang Hard Fork — https://docs.cardano.org/about-cardano/evolution/upgrades/chang
- Plomin Hard Fork — https://docs.cardano.org/about-cardano/evolution/upgrades/plomin

### 橫軸對照（主要 L1 官方）

- Ethereum.org — https://ethereum.org/
- Ethereum Roadmap — https://ethereum.org/en/roadmap/
- Solana Docs — https://solana.com/docs
- Polkadot Wiki — https://wiki.polkadot.network/
- Cosmos Hub Docs — https://hub.cosmos.network/
- Inter-Blockchain Communication (IBC) — https://ibc.cosmos.network/

### 其他可信第三方參考

- Messari Cardano Profile — https://messari.io/project/cardano
- L2Beat (對 Hydra / rollup 比較) — https://l2beat.com/
- DefiLlama Cardano — https://defillama.com/chain/Cardano

---

*本報告為個人學習筆記，不構成投資建議。所有時間、人物、技術細節以官方文件為準；若發現事實錯誤請以 issue 形式回報。*
