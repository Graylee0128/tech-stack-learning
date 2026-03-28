# K3s vs Kubernetes 比較筆記

更新日期：2026-03-26

## 先講最重要的結論

`K3s` 不是 Kubernetes 以外的另一套系統。  
`K3s` 本身就是一個 **fully compliant Kubernetes distribution**。

所以真正的比較不是：

- `K3s` vs `Kubernetes` 功能完全不同

而是比較接近：

- `K3s` vs 標準 / 上游 / 自管 Kubernetes 的安裝與維運方式

如果放到 homelab 語境裡，大家口中的「用 k8s」很多時候其實是在指：

- 用 `kubeadm` 或其他方式去搭一套比較接近上游原生的 Kubernetes

## 一張表先看懂

| 面向 | `K3s` | 標準 Kubernetes |
|------|------|------------------|
| 本質 | 輕量版 Kubernetes 發行版 | Kubernetes 本體 / 上游生態 |
| 相容性 | Fully compliant Kubernetes | 原生基準 |
| 安裝體驗 | 極簡，單一發行版整合較多元件 | 較模組化，通常需要自己組更多東西 |
| 預設元件 | 內建較多 batteries-included 元件 | 很多元件要自己選、自己裝 |
| 資源占用 | 較低 | 通常較高 |
| 適合場景 | Homelab、edge、dev、CI | 大型 production、自管叢集、深入學習 |
| 學習成本 | 較低，先上手快 | 較高，需理解更多底層與組件 |
| 自由度 | 有預設，較快落地 | 更高，但更多責任也回到使用者 |

## 共同點

你在 `K3s` 學到的很多東西，到了其他 Kubernetes 環境仍然通用：

- `kubectl`
- Pod / Deployment / Service
- ConfigMap / Secret
- PVC / StorageClass 基本概念
- Helm
- Argo CD / GitOps
- Prometheus / Grafana
- 基本 troubleshooting 思路

所以先學 `K3s`，不是走偏，而是在學 Kubernetes。

## 真正的差異在哪

### 1. K3s 幫你整合得更多

K3s 官方文件明確列出，它把很多建立 cluster 需要的元件直接打包進來，例如：

- container runtime
- Flannel CNI
- CoreDNS
- Traefik Ingress controller
- ServiceLB
- Kube-router Network Policy controller
- Local-path-provisioner

這代表你裝好 `K3s` 後，很快就有一個能跑 workload 的 cluster。

相對地，標準 Kubernetes 不會用同樣方式把這些都幫你整合好。  
你通常得自己處理更多元件選型與安裝。

## 2. 標準 Kubernetes 更像「自己組一台車」

如果你走比較接近上游原生 Kubernetes 的路，通常要自己面對：

- container runtime
- CNI 選型
- Ingress controller
- LoadBalancer 解法
- Storage / CSI
- control plane 拓樸
- etcd / HA 規劃
- 升級流程

也就是說，Kubernetes 本身比較像一套平台標準；  
而 `K3s` 比較像是「已經幫你裝好很多合理預設」的發行版。

## 3. K3s 的優勢是更快落地

K3s 官方首頁直接寫它適合：

- Homelab
- Development
- CI
- Edge

這很符合你現在的情境，因為你主要目標是：

- 快速建立 homelab
- 跑部署、監控、GitOps
- 做出可展示的作品集

這種情況下，`K3s` 的價值不只是「輕」，而是能讓你更早進入真正的 Kubernetes 實作。

## 4. 標準 Kubernetes 的價值是理解更深

標準 Kubernetes 比較有價值的地方在於：

- 更理解 control plane
- 更理解叢集 bootstrap
- 更理解 CNI / CRI / storage / HA
- 更貼近 cluster admin / self-managed cluster 的世界

所以它不是比較「高級」，而是更偏：

- 高自由度
- 高複雜度
- 高維運責任

## 到底是 K3s 少了什麼嗎？

對初學者來說，最容易誤會的是：

- `K3s` 是不是功能被閹割？
- 會不會學了 K3s 反而不會真正的 Kubernetes？

比較精確的回答是：

- `K3s` 不是把 Kubernetes 核心概念拿掉
- 它主要是把安裝、打包、預設元件和資源使用做得更輕更簡化

所以差異比較像：

- `K3s` 少的是一部分安裝與維運複雜度
- 不是少掉 Kubernetes 核心能力

## 對使用者來說，標準 Kubernetes 多了哪些要自己管的部分

如果把問題翻成實務語言，標準 Kubernetes 通常比 `K3s` 多出這些要自己管的事：

### Runtime

- 要自己確認 container runtime
- 要自己確認 kubelet 與 runtime 的整合

### 網路

- 要自己選 CNI
- 要自己處理 Pod 網路、NetworkPolicy、路由問題

### 對外流量

- 要自己選 Ingress controller
- bare metal 場景還要自己處理 LoadBalancer 解法

### 儲存

- 要自己處理 default storage 與 CSI / provisioner

### 控制平面

- 要更理解 API server、scheduler、controller manager、etcd
- 要自己處理多 control plane / HA 設計時的更多細節

### 叢集生命週期

- 初始化
- 節點加入
- 升級
- reset / cleanup

### Host 整合

- swap
- cgroup driver
- 多網卡 / node IP
- 防火牆 / iptables / nftables

所以說到底：

**標準 Kubernetes 不一定是「功能多很多」，而是「需要你自己決定和管理的部分多很多」。**

## 那我該選哪一個

### 如果你現在要的是這些

- 先把 homelab 做起來
- 先學 Kubernetes 核心物件
- 先接 GitHub Actions / Argo CD / Prometheus / Grafana
- 先做作品集

建議先選：

- `K3s`

### 如果你現在要的是這些

- 更深入理解 cluster bootstrap
- 練 self-managed cluster 能力
- 補 cluster admin / CKA 深度
- 想理解企業自管叢集的安裝與維運

就該補：

- 標準 Kubernetes 路線

在 homelab 裡，這通常會落到：

- `kubeadm`

## 對你目前最適合的路線

依你現在的 `devops-homelab` 和職涯目標，我會建議：

1. 先用 `K3s` 做主線實作
2. 把部署、監控、GitOps、troubleshooting 做起來
3. 再補標準 Kubernetes / `kubeadm` 的知識深度

這樣可以同時拿到：

- 快速落地的作品集
- 比較紮實的 Kubernetes 理解

## 你現在可以記住的版本

一句話版：

> `K3s` 是輕量、整合度更高的 Kubernetes 發行版；標準 Kubernetes 則給你更高自由度，也把更多安裝與維運責任交還給你。

兩句話版：

> 學 `K3s` 不是偏離 Kubernetes，而是在用更容易落地的方式學 Kubernetes。  
> 標準 Kubernetes 並不是比較「正統」而已，而是它通常需要你自己管理更多 cluster 基礎設施細節。

## 官方參考來源

- K3s Documentation  
  https://docs.k3s.io/
- K3s Quick Start  
  https://docs.k3s.io/quick-start
- Installing kubeadm  
  https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/
- Creating a cluster with kubeadm  
  https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/create-cluster-kubeadm/
- Container Runtimes  
  https://kubernetes.io/docs/setup/production-environment/container-runtimes/

## 補充說明

文中說的「標準 Kubernetes」在實務上通常指較接近上游原生、需要自行組裝較多元件的 Kubernetes 環境。  
在 homelab / 自建語境裡，常見做法就是用 `kubeadm`，但 `kubeadm` 只是其中一種實現方式，不等於 Kubernetes 本體。
