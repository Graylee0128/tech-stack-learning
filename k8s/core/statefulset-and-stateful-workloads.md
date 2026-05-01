# StatefulSet 與有狀態工作負載教學筆記

> 這份筆記以 `study-area.sre.tw` 的 `R3: 深入剖析 K8s` 為核心來源。R3 在站上其實非常聚焦，主要落在第十八、十九章，主題就是 `StatefulSet`。這很合理，因為很多人學 Kubernetes 時先學會 `Deployment`，但真正一進到資料庫、佇列、叢集型服務，就會撞上「無狀態思維不夠用」這件事。

## 這份筆記要解決什麼問題

很多剛碰 K8s 的人會有一個直覺：

> 反正 Pod 壞了會自動重建，那所有服務是不是都用 Deployment 就好？

對 stateless service 常常沒問題。  
但只要你的服務開始出現下面特性，事情就變了：

- 副本之間有順序
- 每個副本要有固定身分
- 每個副本要綁自己的資料
- Pod 重建後要接回原本那份資料

這些就是 R3 在談的核心。

## 一句話先講完 R3 的核心

StatefulSet 是 Kubernetes 用來處理「有狀態工作負載」的原生機制，重點不是多一個控制器而已，而是它幫你保留了順序、身分和儲存關聯。

## 1. 先搞懂：什麼叫 stateless，什麼叫 stateful

### 觀念

R3 第十八章一開始就把對比講得很清楚：

- `Deployment` 很適合無狀態應用
- 有些服務不只是多開幾個副本，而是副本之間有相依性與資料延續性

### 白話比喻

無狀態服務像超商店員，A 店員跟 B 店員可以互換，只要有人站櫃就行。  
有狀態服務比較像保險箱，每個櫃位有自己的編號、自己的內容，不能隨便互換。

### 常見的 stateful 場景

- 資料庫
- 具 leader / follower 關係的服務
- 需要固定節點識別的叢集
- 需要每個副本綁定自己磁碟的系統

### Go 實務映射

如果你用 Go 寫的是：

- API server
- stateless worker
- 一般 Web service

通常比較接近 `Deployment`。  
但如果你要在 K8s 上運行的是：

- Redis / PostgreSQL / MySQL
- ZooKeeper / etcd 類型系統
- 某些 message broker

就很容易需要 `StatefulSet` 的思維。

## 2. Deployment 為什麼不夠

### 觀念

`Deployment` 的假設是：每個 Pod 都差不多，可以隨意替換。  
這對 Web service 很合理，因為每個 Pod 都只是同一份程式的另一個副本。

但 R3 提醒你，有些服務不接受這個假設：

- 某個節點要先起來，別的節點才能加入
- Pod A 和 Pod B 不是對等的
- 刪掉重建後，不能接到別人的資料

### 白話比喻

Deployment 像是叫外送員補班，誰來都差不多。  
StatefulSet 比較像交響樂團，第一小提琴和第二小提琴不是一模一樣的角色，出場順序也有意義。

## 3. StatefulSet 的第一個重點：拓樸狀態

### 觀念

R3 第十八章把 StatefulSet 的第一個核心叫做「拓樸狀態」。

意思是：

- Pod 之間有順序
- Pod 之間可能有依賴
- 每個 Pod 需要可預測的名稱

### R3 提到的關鍵特徵

1. Pod 名稱有固定編號，例如 `web-0`、`web-1`
2. 建立時有順序，會先等 `web-0` ready，再處理 `web-1`
3. 刪除時也會按順序反向處理

### 白話比喻

這不是「多開兩台一樣的機器」，而是「先把老大架起來，再讓其他節點照著規則加入」。

### 為什麼這很重要

很多分散式系統在啟動時需要：

- 預測 leader 名稱
- 預測 seed node
- 依照固定順序加入 cluster

如果 Pod 名稱每次亂跳，系統自己就很難建立穩定拓樸。

## 4. Headless Service 在 StatefulSet 裡扮演什麼角色

### 觀念

R3 第十八章特別點出 `clusterIP: None` 與 `serviceName`。  
這不是小細節，而是讓每個 StatefulSet Pod 可以有穩定 DNS 身分的關鍵。

### Headless Service 是什麼

一般 `Service` 比較像一個 VIP，流量打進去由它再轉給後面 Pod。  
`Headless Service` 則不是提供單一虛擬 IP，而是讓你能直接解析到後面的 Pod。

### R3 給的 DNS 規則

`<pod_name>.<service_name>.<namespace>.svc.cluster.local`

例如：

`web-0.nginx.default.svc.cluster.local`

### 白話比喻

一般 Service 像總機，只知道「請幫我轉接客服部」。  
Headless Service 比較像公司內線表，讓你直接找到「客服部第 0 號座位」。

### 常見誤解

- `Headless Service 比較高級，所以所有服務都該用`  
  不是。它是為了「直接找特定 Pod」這個需求，不是通用替代品。

## 5. StatefulSet 的第二個重點：儲存狀態

### 觀念

R3 第十九章把第二個核心叫做「儲存狀態」。

意思是：

- Pod 現在用的資料
- 經過重建、重排程、時間流逝之後
- 仍然要能對回同一份資料

這就是為什麼 stateful workload 不只需要固定名字，還需要穩定的 storage 綁定。

### 白話比喻

這不像旅館臨時換房，行李搬過去就好。  
比較像銀行保管箱，`web-0` 就該對 `web-0` 那個箱子，不應該臨時拿到 `web-1` 的資料。

## 6. PV / PVC 在這裡解的，是「誰提供儲存、誰使用儲存」

### 觀念

R3 第十九章很重要的一點，是把 `PV` 和 `PVC` 的分工講清楚：

- `PV`: 資源提供者
- `PVC`: 資源需求者

這個抽象很漂亮，因為它讓應用開發者不用直接面對底層儲存系統的細節。

### 白話比喻

- PV 像房東，表示有哪些房子可租
- PVC 像租客，表示自己需要什麼樣的房子

Kubernetes 幫你做的，就是把需求和供給配對起來。

### R3 指出的好處

1. 應用只講需求，不用知道後端儲存細節
2. 提供者與使用者權責分離
3. 問題定位比較清楚

### 常見誤解

- `有 Volume 就等於有持久化`  
  不一定。要看 Volume 的來源與生命週期。
- `Pod 重建後還在，就是資料安全`  
  錯。Pod 活著不代表資料跟它有穩定綁定。

## 7. `volumeClaimTemplates` 為什麼是 StatefulSet 的關鍵

### 觀念

R3 第十九章提到，StatefulSet 可以透過 `volumeClaimTemplates`，為每個 Pod 自動建立對應規格的 PVC。

這帶來很重要的效果：

- 每個 Pod 有自己的 PVC
- 名稱會跟 Pod 編號對應
- Pod 重建時能接回原本那顆儲存

### 你可以記成這樣

- `web-0` 對 `www-web-0`
- `web-1` 對 `www-web-1`

這種一對一綁定，就是有狀態工作負載穩定的基礎。

### 白話比喻

不是每次上班都去公共置物櫃亂抽一格。  
而是每個人都有自己固定的那格，今天重來、明天重來，拿到的都還是同一格。

## 8. Pod 重建時，StatefulSet 真正保住的是什麼

### 觀念

很多人以為 StatefulSet 最有價值的是「Pod 不會壞」。  
這其實搞錯重點了。

Pod 當然還是會壞、會被刪、會被重建。  
StatefulSet 真正保住的是：

- 相同的命名身分
- 相同的順序角色
- 相同的儲存綁定

### 白話比喻

不是保證某個人永遠不離職，而是保證「這個職位的編號、座位、文件櫃」可以被穩定接手。

## 9. 什麼時候該用 StatefulSet，什麼時候不該

### 適合用 StatefulSet

- 需要固定 Pod identity
- 需要 ordered rollout / termination
- 需要每個副本綁定自己的 persistent volume
- 需要直接透過固定 DNS 名稱互相發現

### 不一定需要 StatefulSet

- 一般 stateless API
- 短生命週期 worker
- session 不綁單 Pod 的 Web service
- 只是想「比較穩」但其實沒有狀態需求的服務

### 常見誤解

- `有資料就一定要 StatefulSet`  
  不一定。某些情況是外部資料庫 + stateless app，那 app 本身仍然適合 Deployment。
- `StatefulSet 比 Deployment 進階，所以能用就用`  
  錯。控制模型越複雜，越應該只在真的有需要時用。

## 10. 如果你是 Go 後端，R3 會怎麼出現在工作裡

### 你不一定自己部署資料庫

很多公司會用託管服務，例如 RDS、Cloud SQL、ElastiCache。  
這種情況下，你可能不常自己寫 StatefulSet manifest。

但你仍然需要懂這些，因為你會一直碰到它的影子：

- 為什麼某些中介元件比較適合跑在 stateful workload 模型
- 為什麼 storage、DNS identity、順序性會影響系統設計
- 為什麼 K8s 不是所有東西都能用 Deployment 粗暴解掉

### 更實際一點的工作場景

- 看平台團隊的 manifest，知道 `serviceName`、Headless Service、PVC 在做什麼
- 知道某個有狀態元件出事時，問題可能在 Pod、PVC、PV、StorageClass 哪一層
- 理解資料面和應用面為什麼不能混成同一種 rollout 思維

## 11. 面試版最短回答

### StatefulSet 在解什麼問題？

它在解 Kubernetes 裡有狀態工作負載的管理問題，讓 Pod 具有固定身分、穩定順序，以及和持久化儲存的一對一綁定。

### 它和 Deployment 差在哪？

Deployment 假設每個 Pod 都可以互換，適合無狀態服務；StatefulSet 則保留 Pod 的順序、名稱與儲存關聯，適合需要 identity 和 persistent storage 的服務。

### Headless Service 為什麼重要？

因為 StatefulSet 常需要直接找到某個特定 Pod，而不是只透過一個虛擬 Service IP 做負載平衡。Headless Service 提供了這種穩定 DNS 身分。

## 來源

- `R3 活動摘要`: https://study-area.sre.tw/03_K8s/
- `R3 第十八章：深入理解 StatefulSet（一）：拓樸狀態`: https://study-area.sre.tw/03_K8s/CH18/
- `R3 第十九章：深入理解 StatefulSet（二）：儲存狀態`: https://study-area.sre.tw/03_K8s/CH19/
- `Cloud Native DevOps with Kubernetes` 本地轉錄筆記中對 `StatefulSet` 的補充：`tech-stack-learning/resources/Cloud Native DevOps with Kubernetes - John Arundel.md`
