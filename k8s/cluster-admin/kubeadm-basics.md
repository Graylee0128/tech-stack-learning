# kubeadm 基礎筆記

更新日期：2026-03-26

## 一句話先說結論

`kubeadm` 不是 Kubernetes 的別名，也不是像 `kubectl` 那種單純 CLI。  
它比較像是「**用來初始化與管理標準 Kubernetes 叢集生命週期的工具**」。

如果你用 `kubeadm`，通常是在做這些事：

- 安裝與初始化 control plane
- 讓 worker node 加入 cluster
- 做 cluster upgrade
- 做部分 reset / cleanup

## 常見名詞一次分清楚

### `k8s` / Kubernetes

- 整個容器編排系統的通稱
- 包含 API server、scheduler、controller manager、etcd、kubelet、kube-proxy 等元件

### `kubectl`

- 操作 Kubernetes API 的 CLI
- 負責查詢、部署、除錯、套用 YAML

### `kubeadm`

- 負責「把標準 Kubernetes cluster 建起來」的 bootstrapping 工具
- 官方文件把它定位成建立符合 best practices 的最小可用叢集，並支援 bootstrap tokens、cluster upgrades 等生命週期功能

### `k3s`

- 輕量版 Kubernetes 發行版
- 適合 homelab、edge、development
- 幫你把很多 cluster 建置細節包起來，安裝更快、資源占用更小

## `kubeadm` 到底做了什麼

官方文件裡，`kubeadm init` 的重點流程包括：

1. 先做 preflight checks
2. 產生憑證與 kubeconfig
3. 產生 control plane static Pod manifests
4. 將 manifest 寫到 `/etc/kubernetes/manifests`
5. 由 kubelet 監看並啟動 API server、controller manager、scheduler，若使用 local etcd 也會建立 etcd static Pod

所以 `kubeadm` 的角色不是日常操作 app，而是把叢集基礎骨架建起來。

## 什麼情況適合學 `kubeadm`

官方文件提到，`kubeadm` 很適合這些場景：

- 第一次試著建 Kubernetes cluster
- 想自動化建立測試 / 實驗叢集
- 想把它當成更大安裝器或自動化工具的 building block

以你的脈絡來看，學 `kubeadm` 特別有價值的地方是：

- 更理解 control plane 是怎麼組起來的
- 更理解 node join、upgrade、reset 這些 cluster lifecycle
- 對 CKA 或企業自管叢集的理解會更扎實

## `kubeadm` 和 `k3s` 的差異

### 共同點

兩者最後都會讓你得到一個 Kubernetes cluster，所以這些能力是共通的：

- Pod / Deployment / Service / ConfigMap / Secret
- `kubectl`
- YAML
- Helm
- GitOps
- Monitoring
- Troubleshooting 基本思路

### 差異點

`kubeadm` 比較偏：

- 標準 Kubernetes 元件安裝流程
- 自己選 container runtime、CNI、部分系統參數
- 更接近「我自己組一套 cluster」

`k3s` 比較偏：

- 輕量封裝
- 預設幫你整合較多元件
- 更快進入 homelab / dev / lab 實作

## `kubeadm` 路線比 `k3s` 多了哪些要自己管的事

這一段是最容易卡住、但也最有助於建立正確認知的地方。

很多人會以為：

- `k8s` 功能比較多
- `k3s` 功能比較少

更精確的說法其實是：

- `k3s` 幫你把很多 Kubernetes 叢集基礎元件先整合好
- `kubeadm` 路線則把更多選擇權與維運責任留給使用者

### 一張表先看懂

| 面向 | `k3s` | `kubeadm` 路線 |
|------|------|----------------|
| 安裝體驗 | 單一安裝腳本，快速起 cluster | 需要分階段準備 host、runtime、套件、初始化流程 |
| Container runtime | 預設整合 | 要自己準備與確認 CRI runtime |
| Pod network / CNI | 預設整合 Flannel | 要自己選 CNI 並安裝 |
| Ingress | 預設整合 Traefik | 通常要自己選並安裝 Ingress controller |
| LoadBalancer | 預設帶 ServiceLB | bare metal 常要自己補方案，例如 MetalLB 類型工具 |
| Dynamic storage | 預設帶 local-path-provisioner | 通常要自己處理 storage class / CSI / local provisioner |
| Control plane 包裝 | 單一發行版封裝較多細節 | 更接近原生元件組裝與 lifecycle 管理 |
| Datastore | 預設有較簡化選項 | etcd / HA / 拓樸規劃通常要自己理解更多 |
| Cluster lifecycle | 較多預設幫你收斂 | `init` / `join` / `upgrade` / `reset` 要更熟 |
| 安裝細節坑位 | 相對少 | cgroup driver、swap、node IP、CNI 殘留等更常要自己排 |

### 1. Container runtime

在 `kubeadm` 路線裡，container runtime 是你要自己負責的一塊。

官方文件明確提到，每個 node 都需要安裝符合 CRI 的 runtime，像是：

- `containerd`
- `CRI-O`

這代表你要自己確認：

- runtime 有沒有裝好
- kubelet 是否能正確連到 runtime
- cgroup driver 是否匹配

而 `k3s` 會把這一層整合掉很多，所以你較少在一開始就卡在 runtime 相依。

### 2. Pod 網路 / CNI

`kubeadm` 建好 control plane 之後，不代表 Pod 網路就已經可用。  
官方建立 cluster 的流程明確提到，你還需要安裝 Pod network add-on。

這一步通常代表你要自己選：

- Calico
- Flannel
- Cilium

並理解：

- Pod-to-Pod 怎麼通
- NetworkPolicy 是否支援
- overlay / routing 行為差異

而 `k3s` 預設已經幫你整合 Flannel，所以你會比較快得到一個「能跑 workload」的 cluster。

### 3. Ingress / 對外流量

在 `kubeadm` 路線裡，Ingress controller 通常不是一開始就有。  
你往往要自己決定：

- NGINX Ingress
- Traefik
- Gateway API 相關實作

如果是在 bare metal 或 homelab，還常常要再思考：

- 服務怎麼對外暴露
- 80 / 443 怎麼進來
- DNS / reverse proxy / local network / VPN 要怎麼配

`k3s` 預設整合 Traefik，這代表你比較快能把焦點放在 app 部署，而不是先花很多時間組外部流量入口。

### 4. LoadBalancer

在雲端 managed Kubernetes 裡，`LoadBalancer` Service 常會自動接到雲端負載平衡器。  
但在 `kubeadm` 的 bare metal / homelab 場景，這通常不是自動存在的。

你通常要自己處理：

- 內網 IP 配置
- bare metal LoadBalancer 解法
- L2 / ARP / address pool 的概念

`k3s` 預設帶了 ServiceLB，雖然不是萬能，但對單機或小型 lab 來說已經很夠用。

### 5. Storage 與 Persistent Volume

`kubeadm` 不會自動給你一個很方便的預設 storage 方案。  
如果你的 workload 需要持久化，通常要自己補：

- 預設 `StorageClass`
- local provisioner
- CSI driver
- NFS / Longhorn / Ceph 之類的外部存儲整合

而 `k3s` 預設整合 `local-path-provisioner`，對 homelab 初期來說非常省事。

### 6. Control plane / datastore / HA 拓樸

這是 `kubeadm` 真正自由度變高、也更吃基礎的一塊。

你需要更理解：

- control plane 有哪些元件
- etcd 在哪裡
- 是 stacked etcd 還是 external etcd
- 多 control plane 要怎麼做
- 憑證、API endpoint、join token 如何處理

`k3s` 雖然也不是完全沒這些概念，但它把很多 control plane 複雜度包裝起來了，所以對 homelab 來說比較友善。

### 7. 升級與清理

用 `kubeadm` 的時候，你會更直接面對 cluster lifecycle：

- `kubeadm init`
- `kubeadm join`
- `kubeadm upgrade`
- `kubeadm reset`

這些都不是日常部署 app 的命令，而是 cluster admin 的工作。

尤其 `kubeadm reset` 很值得特別記住：

- 它是 best effort cleanup
- 不代表會幫你把一切都清乾淨

官方文件特別提醒，像這些可能都要自己再處理：

- `/etc/cni/net.d`
- iptables / nftables / IPVS 規則
- `$HOME/.kube/config`

### 8. Host 層前置條件與坑位

`kubeadm` 路線更容易讓你碰到 host 層問題，像是：

- `swap` 沒處理
- cgroup driver 不一致
- 多網卡 / 多 default gateway
- hostname / node IP 不符合預期
- container runtime 設定錯誤

也就是說，`kubeadm` 的難度不只在 Kubernetes 本身，也在 Linux host 與系統整合。

## 這些差異對學習有什麼意義

### `k3s` 比較像

- 「先讓我做出一個能跑的 Kubernetes 平台」
- 讓你把時間放在 workload、監控、GitOps、部署流程

### `kubeadm` 比較像

- 「讓我真的理解 cluster 是怎麼組起來的」
- 讓你更貼近 cluster admin / self-managed Kubernetes 的世界

所以兩者不是誰取代誰，而是：

- `k3s` 偏快速落地
- `kubeadm` 偏結構理解與維運深度

## 對你目前最實際的建議

如果回到你現在的學習目標與 homelab 脈絡：

### 先用 `k3s` 的理由

- 你想先做出可展示的 homelab 平台
- 你想接 GitHub Actions、Argo CD、Prometheus、Grafana
- 你不想前期大量時間卡在 cluster bootstrap 細節

### 之後補 `kubeadm` 的理由

- 你想更理解標準 Kubernetes 安裝與元件角色
- 你想補強 CKA / cluster admin 能力
- 你想知道公司自管叢集常見問題會出在哪

## 一句話總結

你目前的理解可以整理成這樣：

> `kubeadm` 路線不是單純「功能比 k3s 多」，而是它讓使用者自己管理更多 cluster 基礎設施細節；`k3s` 則幫你把很多這些元件先整合好，讓你更快進入實作。

### 你現在該怎麼選

對你目前的 `devops-homelab` 來說：

- **主線先用 `k3s`**
- **知識面補 `kubeadm`**

這樣最有效率。  
也就是說，實作先求快速落地，原理與標準叢集生命週期再用 `kubeadm` 補深度。

## `kubeadm` 的基本安裝觀念

官方 `Installing kubeadm` 文件列出的基本前提包括：

- Linux 主機
- 每台至少 2 GB RAM
- control plane 至少 2 CPU
- 節點間要有完整網路連通

常見會安裝的套件是：

- `kubelet`
- `kubeadm`
- `kubectl`

官方也特別提醒：

- 套件升級不能隨便跟著系統更新一起滾
- `kubelet` 與 container runtime 的 cgroup driver 要匹配，不然 kubelet 可能起不來

## 用 `kubeadm` 建 cluster 的最小流程

### 1. 每台機器準備前置條件

- 安裝 container runtime
- 安裝 `kubelet`、`kubeadm`、`kubectl`
- 關注 swap、網路、hostname、CRI、cgroup driver

### 2. 在 control plane 執行 `kubeadm init`

這一步會初始化 control plane node。

初始化完成後，通常你會：

- 取得 admin kubeconfig
- 設定 `kubectl`
- 安裝 CNI

### 3. 其他節點執行 `kubeadm join`

worker node 透過 token 與控制平面連線，加入叢集。

### 4. 後續維運

- `kubeadm upgrade` 做 cluster 升級
- `kubeadm reset` 做節點清理

## 重要子命令速覽

### `kubeadm init`

- 初始化 control plane node
- 是建 cluster 的起點

### `kubeadm join`

- 讓 worker node 或額外 control plane node 加入叢集

### `kubeadm upgrade`

- 用於升級 kubeadm 叢集
- 官方文件提醒升級前應先讀 release notes、做好備份，且 `swap` 必須停用

### `kubeadm reset`

- 盡力回復 `kubeadm init` 或 `kubeadm join` 對主機造成的變更
- 但它**不會**幫你清乾淨所有東西

官方文件特別提醒幾個常見殘留：

- `/etc/cni/net.d` 可能要自己清
- iptables / nftables / IPVS 規則不一定會幫你清
- `$HOME/.kube/config` 也不會自動刪掉

這點很重要，因為很多人以為 reset 後就完全乾淨了，其實不是。

## `kubeadm` 對 homelab 的真正價值

如果你在 homelab 上直接用 `kubeadm`，最大的收穫通常不是「比較炫」，而是：

- 更理解控制平面的組成
- 更理解 cluster bootstrap 與 upgrade
- 更理解 CNI、CRI、憑證、節點加入等底層議題

但代價是：

- 比 `k3s` 花更多時間
- 更容易卡在安裝與相依細節
- 較不利於你快速做出作品集成果

所以對你現在的建議仍然是：

1. homelab 主專案先用 `k3s`
2. 另開一份 `kubeadm` 筆記理解標準 cluster lifecycle
3. 等 `k3s` 平台專案穩了，再做一次 `kubeadm` lab

## 可以怎麼把 `kubeadm` 排進你的學習順序

### Phase 1：先求可用

- `k3s`
- `kubectl`
- 基本 workload 部署
- Monitoring / GitOps

### Phase 2：補 cluster admin 深度

- `kubeadm init`
- `kubeadm join`
- CNI / CRI 基本概念
- kubelet / control plane 角色

### Phase 3：補維運生命週期

- `kubeadm upgrade`
- 憑證與 kubeconfig
- reset / cleanup
- 多 control plane / HA 觀念

## 對你最有用的結論

- `k3s` 適合你現在把 homelab 快速做起來
- `kubeadm` 適合你補「標準自建 Kubernetes」知識深度
- 兩者不是互斥，而是先後順序的問題

如果你未來面試被問到：

> 為什麼 homelab 用 k3s，不直接用 kubeadm？

你可以回答：

> 我在 homelab 主線先用 k3s 快速完成平台實作，像是部署、監控與 GitOps；同時另外補 kubeadm，理解標準 Kubernetes cluster 的 bootstrap、join、upgrade、reset 流程。這樣可以同時兼顧交付速度與 cluster admin 深度。

## 官方參考來源

- Installing kubeadm  
  https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/
- Creating a cluster with kubeadm  
  https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/create-cluster-kubeadm/
- kubeadm init  
  https://kubernetes.io/docs/reference/setup-tools/kubeadm/kubeadm-init/
- kubeadm join  
  https://kubernetes.io/docs/reference/setup-tools/kubeadm/kubeadm-join/
- Upgrading kubeadm clusters  
  https://kubernetes.io/docs/tasks/administer-cluster/kubeadm/kubeadm-upgrade/
- kubeadm reset  
  https://kubernetes.io/docs/reference/setup-tools/kubeadm/kubeadm-reset/
- K3s Documentation  
  https://docs.k3s.io/

## 補充說明

文中關於「你目前應該先用 `k3s`、再補 `kubeadm`」這個部分，是依據：

- Kubernetes 官方對 `kubeadm` 的定位
- K3s 官方對 homelab / development 的定位
- 你目前 `devops-homelab` 的資源與作品集目標

這一段屬於基於官方文件與你現況做出的實務推論。
