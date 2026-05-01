# Continuous Delivery 教學筆記

> 這份筆記以 `study-area.sre.tw` 的 `R2: Continuous Delivery` 為主軸重組。R2 網站本身提供的是 15 章導讀結構，涵蓋從「交付為什麼會卡住」一路到「持續交付管理」的完整流程。我這裡不照章節順序逐頁翻，而是把它改寫成一條 Go 後端工程師比較容易吸收、也比較能拿去看自己團隊流程的主線。

## 這份筆記要解決什麼問題

很多人一提到 `CI/CD`，腦中先想到的是：

- GitHub Actions
- Jenkins
- Argo CD
- 部署腳本

但 R2 在提醒你的其實是另一件事：

> 工具只是表面，真正的題目是「你的團隊能不能把變更安全、快速、可重複地送到線上」。

如果你之後做的是 Go 後端，尤其是博彩或電商這種高流量產品，這題很重要。因為真正讓團隊痛苦的，通常不是「不會 deploy」，而是：

- 每次 deploy 都像開獎
- 測試很多，但還是不敢發
- 環境不一致，問題只能線上才重現
- 某個人不在，就沒人敢上版
- 小改動也要排大流程，速度越來越慢

R2 的價值，就是把這一整條交付鏈拆開來看。

## 一句話先講完 R2 的核心

Continuous Delivery 不是「把部署自動化」而已，而是讓軟體交付這件事變成一條可靠、可預測、可頻繁執行的工程流程。

## 1. 先不要急著談工具，先談交付問題

### 觀念

R2 的第一章叫做「軟體交付的問題」，這個起手很重要。  
因為如果你不先承認交付本身是一個系統問題，後面很容易把焦點錯放在某個工具或某個人身上。

常見交付問題其實長這樣：

- code merge 很晚，整合痛苦
- 測試集中在後段，回饋太慢
- 每個環境都不太一樣
- 發佈流程太依賴手工
- 發版成功與否靠經驗，不靠系統設計

### 白話比喻

如果開發像工廠生產，交付不是最後把貨搬上車就算結束。  
你前面設計、備料、品管、包裝、出貨，只要任何一段不穩，最後都會拖慢整條線。

### Go 實務映射

你寫 Go API 服務時，就算 code 本身不差，也可能被這些事拖垮：

- schema migration 沒流程
- staging 與 production 差太多
- 測試只跑 unit test，整合問題都留到線上
- rollback 沒有被演練過

## 2. CD 的主線，其實是把交付拆成可控的小步驟

### 觀念

R2 的章節安排很有意思，從 `設置管理`、`持續整合`、`測試策略`、`部署流水線`，一路到 `資料管理`、`相依性管理`、`版本控制進階`、`持續交付管理`。  
這代表它要講的不是單點技巧，而是一整套能力。

把它重組成工程語言，大概可以分成五塊：

1. 讓變更可追蹤
2. 讓整合可頻繁
3. 讓驗證可自動
4. 讓部署可重複
5. 讓整條流程可管理

### 這也呼應你本地 `Accelerate` 筆記的主線

你現有的 `Accelerate` 筆記把 CD 說得很清楚：

- 把品質建進流程
- 小批次交付
- 重複工作交給電腦
- 持續改善
- 每個人都要對結果負責

這些剛好就是 R2 章節背後的骨架。

## 3. Configuration Management 不是雜事，而是交付底盤

### 觀念

R2 第二章是 `設置管理`。這一章很容易被低估，但其實它是整條 CD 的底盤。  
因為如果你連：

- 程式碼
- 應用設定
- 系統設定
- build script
- deployment script

都沒有一致地版本化與追蹤，後面的自動化就很脆。

### 白話比喻

你不可能要求工廠自動出貨，但每次原料配方都放在不同人的腦袋裡。

### 常見誤解

- `只要 app code 在 Git 裡就夠了`  
  不夠。設定與流程若沒版本化，系統還是不可重現。
- `先手動做，之後再補自動化`  
  可以，但如果手動步驟太多又沒被明文化，很快就變成組織債。

### Go 實務映射

Go 服務常見要一起管理的東西：

- `.env` / config file
- migration scripts
- Dockerfile
- Helm chart / manifest
- CI pipeline definition
- release notes / rollback steps

## 4. CI 的真正價值，不是自動跑測試，而是快速整合

### 觀念

R2 第三章是 `持續整合`。  
CI 最常被誤解成「有 pipeline 跑 test 就叫 CI」，但它更核心的價值是：

- 頻繁整合
- 快速回饋
- 讓主幹保持可部署

### 白話比喻

如果團隊每個人都把改動藏在自己房間一週，最後一起搬出來，整合一定爆。  
CI 的意思是大家早點把東西接到一起，問題早爆比晚爆便宜太多。

### 常見誤解

- `PR 有 check 就算 CI`  
  不完整。CI 真正關心的是整合頻率、回饋速度、失敗後是否立即修復。
- `分支很多比較安全`  
  不一定。長命分支常常只是把整合風險往後推。

### Go 實務映射

Go 專案的 CI 至少應該幫你守住：

- `go test ./...`
- lint / format 規範
- build 是否可重現
- 依賴是否可解析
- container image 是否能產生

如果 repo 再成熟一點，還會補：

- integration tests
- vulnerability scan
- contract tests

## 5. 測試策略不是測越多越好，而是要放對階段

### 觀念

R2 第四章到第九章幾乎都在談測試與驗證：

- 測試策略的實現
- 提交階段
- 驗收測試階段
- 非功能需求測試

這說明一個很重要的觀念：

> Continuous Delivery 不是最後才驗，而是把不同類型的驗證放進不同關卡。

### 你可以把它想成三層

1. `commit stage`  
   快、便宜、每次都跑。像 unit test、lint、basic build。
2. `acceptance stage`  
   驗證主要功能是否真的能工作。像 API 整合測試、基本端到端流程。
3. `non-functional stage`  
   驗證不是功能對錯，而是系統性質。像效能、安全、穩定性、容量。

### 白話比喻

不是每次出貨前都要做完整災難演習。  
有些檢查應該每次都跑，有些該在特定節點跑，不然整條線會慢到失去意義。

### Go 實務映射

對 Go 後端很實際的分法是：

- commit stage: `go test`, lint, build
- acceptance stage: 啟一個 test environment，跑 API flow
- non-functional stage: 壓測、DB migration rehearsal、security scan

## 6. Deployment Pipeline 在解的不是部署，而是風險切分

### 觀念

R2 第五章就是 `部署流水線`。  
很多人聽到 pipeline，腦中只想到 YAML，但這章真正重要的是：

> 把一次變更從 commit 走到 production 的過程切成明確關卡，每一關都在降低風險。

### 白話比喻

像機場安檢一樣，不是因為安檢本身有價值，而是它把不同風險在不同位置攔下來。  
越早攔到，代價越小。

### 一條簡化版 pipeline

1. 開發者 commit
2. build + 快速測試
3. 產生 artifact
4. 部署到測試環境
5. 跑驗收與必要的非功能驗證
6. 決定是否發佈到 production

### Go 實務映射

對 Go 服務，pipeline 很常串這些：

- build binary
- build container image
- push image 到 registry
- deploy 到 staging
- 跑 smoke test
- 人工核准或自動發佈

## 7. Script 化不是為了帥，是為了可重複與可預測

### 觀念

R2 第六章是 `建置與佈署腳本化`。  
這一章的重點很樸素：

- 只要一件事要做很多次，就應該逐步轉成程式化
- 只要一件事對成功率很關鍵，就不該只靠口頭流程

### 常見誤解

- `有 Runbook 就夠了`  
  不夠。Runbook 很重要，但高頻、重複、容易出錯的步驟，還是該盡量腳本化。
- `先寫一堆 script 就是成熟`  
  不一定。沒有版本控制、測試與權限邊界的 script，可能只是另一種技術債。

### Go 實務映射

你在團隊裡可能會看到：

- `make deploy`
- release script
- migration runner
- rollback script
- health check script

這些東西如果沒有標準化，很容易變成「只有某個人會用」。

## 8. 應用部署、基礎設施、資料，三者不能拆開看

### 觀念

R2 後半段章節很關鍵：

- 第十章：應用程式的部署與發佈
- 第十一章：管理基礎設施與環境
- 第十二章：資料管理
- 第十三章：元件相依性管理

這代表 R2 在講一個很成熟的觀點：

> 真正的交付不是把 app 丟上去，而是一起管理 app、環境、資料、相依性。

### 白話比喻

你不能只把新餐點菜單印好了，就說餐廳準備完成。  
後廚設備、食材供應、冷藏條件、服務流程都要一起準備。

### Go 實務映射

Go 後端常見的真正發版風險往往在這裡：

- migration 跟 app 版本不相容
- Redis schema / key pattern 改了
- 環境變數漏配
- 第三方 API 變更
- image 換了 base layer 後出現 runtime 差異

所以交付成熟度不只看 deploy 成不成功，還要看整體變更是不是一致。

## 9. Version Control 進階是在管理「整個變更系統」

### 觀念

R2 第十四章是 `版本控制進階`。  
這不是單純 Git 指令技巧，而是在問：

- 你如何管理主幹穩定性
- 你如何管理分支策略
- 你如何讓 release 可追溯
- 你如何把 infra / config / script 納入同一套變更治理

### 常見誤解

- `Git flow 看起來完整，所以一定最好`  
  不一定。分支策略應該服務交付速度與風險控制，不是反過來。
- `版本控制只管程式碼`  
  太窄。成熟交付會把 config、infra、scripts 一起納入。

### Go 實務映射

你之後很容易遇到這個取捨：

- 想維持單一主幹，快速整合
- 又想保留足夠 release 控制

這沒有唯一答案，但 R2 會逼你先問：

- 我們的風險在什麼地方？
- 我們是為了控制風險，還是只是把流程變複雜？

## 10. Continuous Delivery 和 Continuous Deployment 不一樣

### 觀念

這個 distinction 很值得記。

- `Continuous Delivery`: 系統隨時可以上線，但是否真的進 production，可能保留人工決策點
- `Continuous Deployment`: 每個變更都自動一路上到 production

### 白話比喻

前者像是貨物永遠都打包好，隨時可以出貨。  
後者像是只要包好就直接發車。

### 常見誤解

- `沒有自動上 production 就不算成熟`  
  錯。很多高風險系統成熟的做法，是能隨時上，但在某些節點保留人為判斷。

### Go 實務映射

博彩或電商這種高流量場景，常見做法反而是：

- build、test、artifact、staging deploy 全自動
- production release 保留審核、時段控制、canary 或 feature flag

## 11. 如果你是 Go 後端，R2 會怎麼出現在工作裡

### 你真正會拿這些知識做什麼

- 判斷現在的 CI/CD 痛點到底卡在哪
- 知道「測試很多但還是不敢發」通常代表流程設計問題
- 看懂 deployment 不是 app team 單獨的事
- 能跟 SRE / platform / QA 討論交付邊界
- 幫團隊把 release 風險變小，而不是只把流程拉長

### 一個很實用的自查清單

如果你想快速看一個團隊的交付成熟度，可以先問：

1. 每次 commit 多快收到回饋？
2. 主幹是不是大部分時間可部署？
3. build、test、deploy 是不是可重複？
4. config、infra、migration 有沒有版本化？
5. 上 production 的風險有沒有被分段攔下？
6. rollback 或 revert 有沒有被設計，而不是臨時想？

## 12. 面試版最短回答

### Continuous Delivery 是什麼？

Continuous Delivery 是一組工程能力，讓團隊能把變更安全、快速、可重複地送到可發佈狀態，並在需要時可靠地發布。

### 它和 CI / Continuous Deployment 差在哪？

CI 聚焦在頻繁整合與快速回饋；Continuous Delivery 聚焦在讓整條交付鏈可穩定發佈；Continuous Deployment 則更進一步，把變更自動一路送到 production。

### 為什麼 backend engineer 要懂這些？

因為你寫的程式最後一定要經過 build、test、deploy、config、migration、rollback 這整條線。功能能不能安全上線，本來就是工程能力的一部分，不只是平台團隊的事。

## 來源

- `R2 活動摘要與章節清單`: https://study-area.sre.tw/02_CD/
- `R2 第十章 應用程式的部署與發佈`: https://study-area.sre.tw/02_CD/CH10/
- `Accelerate Chapter 4`（本地筆記，用來補強 CD 能力與影響）: `tech-stack-learning/resources/books-notes/raw/accelerate/ch04-technical-practices.md`
- `AWS DevOps dop-notes`（本地散筆記，用來補 CI/CD 基本定義）: `tech-stack-learning/aws/devops/dop-notes/01-sdlc-automation/cicd.md`
