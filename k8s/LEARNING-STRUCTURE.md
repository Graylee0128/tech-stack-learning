# Kubernetes 學習架構

更新日期：2026-03-26

## 目的

這份文件是 `tech-stack-learning/k8s/` 的總學習架構。  
目標不是一次把所有工具都學完，而是把 Kubernetes 拆成幾個層次，讓學習順序更清楚。

整體可以分成三條主線：

1. `Kubernetes 核心`
2. `Kubernetes 常用平台生態`
3. `Cluster admin 進階`

對應目錄：

- `core/`
- `ecosystem/`
- `cluster-admin/`

---

## 一、Kubernetes 核心

這一段的重點是：

- 先把 Kubernetes 當成平台來用
- 先能部署、觀察、除錯 workload
- 先在 homelab 用 `k3s` 把手感做出來

### 1. 前置基礎

- Linux 基本操作
- Container / image 基本概念
- Docker 基本觀念
- 基本網路：IP、port、DNS、HTTP
- TLS / 憑證基礎

### 2. Kubernetes 核心名詞

- Cluster
- Node
- Namespace
- Pod
- ReplicaSet
- Deployment
- Service
- Ingress / Gateway
- ConfigMap
- Secret

### 3. kubectl 操作

- `kubectl get`
- `kubectl describe`
- `kubectl logs`
- `kubectl exec`
- `kubectl apply`
- `kubectl delete`
- `kubectl rollout`
- `kubectl top`
- 看 `events` 的習慣

### 4. Workload 類型

- Deployment
- StatefulSet
- DaemonSet
- Job
- CronJob

### 5. 網路與服務暴露

- Pod-to-Pod 基本概念
- Service discovery
- ClusterIP
- NodePort
- LoadBalancer
- Ingress
- Gateway API 基本觀念

### 6. 設定與機密管理

- ConfigMap
- Secret
- environment variables
- volume mount

### 7. 儲存基礎

- Volume
- PersistentVolume
- PersistentVolumeClaim
- StorageClass

### 8. 健康檢查與資源管理

- liveness probe
- readiness probe
- startup probe
- requests / limits
- HPA 基本概念

### 9. 安全基礎

- Namespace 隔離概念
- RBAC
- ServiceAccount
- Pod security 基本觀念

### 10. 日常維運與排錯

- rollout / rollback
- Pod Pending
- CrashLoopBackOff
- ImagePullBackOff
- 探針失敗
- 資源不足
- `kubectl describe` + `logs` + `events` 的排查流程

### 這一段的學習目標

做到這裡時，你應該可以：

- 用 `k3s` 跑起一個 Kubernetes cluster
- 部署自己的 app
- 做基本設定、健康檢查、儲存與對外暴露
- 知道怎麼看狀態、看 log、做基本排錯

---

## 二、Kubernetes 常用平台生態

這一段的重點是：

- 把 cluster 從「能跑 app」升級成「像平台」
- 開始接近真實 DevOps / platform / SRE 工作流

### 1. 套件管理與配置

- Helm
- Kustomize

### 2. 交付與 GitOps

- GitHub Actions
- Argo CD
- GitOps workflow

### 3. 對外流量入口

- Traefik
- ingress-nginx
- Gateway API

### 4. 觀測與告警

- Prometheus
- Alertmanager
- Grafana
- metrics 基本設計

### 5. 憑證與 TLS 自動化

- cert-manager
- Let's Encrypt
- Ingress TLS

### 6. 日誌與追蹤

- Loki 或 EFK / ELK
- tracing 基本概念

### 7. 備份與還原

- Velero
- namespace / workload backup
- cluster restore 基本概念

### 8. 進階網路

- Cilium
- Hubble
- NetworkPolicy 深化

### 9. Service Mesh

- Istio
- mTLS
- traffic splitting
- retries / failover
- service-to-service observability

### 這一段的學習目標

做到這裡時，你應該可以：

- 用 `Helm` 安裝平台元件
- 用 `Argo CD` 做 GitOps
- 讓服務能穩定對外
- 建立監控與告警
- 把 homelab 做成可展示的 platform project

---

## 三、Cluster admin 進階

這一段的重點是：

- 不只是把 Kubernetes 拿來用
- 而是開始理解 cluster 是怎麼被建起來、維護、升級與治理的

這會更貼近：

- control plane
- cluster bootstrap
- CNI / CRI / storage / HA
- cluster admin / self-managed cluster

### 1. Control Plane 組成

- kube-apiserver
- kube-scheduler
- kube-controller-manager
- etcd
- kubelet
- kube-proxy

### 2. Cluster Bootstrap

- 憑證
- kubeconfig
- bootstrap token
- static Pod
- `kubeadm init`
- `kubeadm join`

### 3. Container Runtime / CRI

- containerd
- CRI
- kubelet 與 runtime 的關係
- cgroup driver

### 4. CNI 與網路深化

- Flannel
- Calico
- Cilium
- Pod network
- Service routing
- NetworkPolicy
- overlay / routing 基本差異

### 5. Storage 深化

- CSI
- dynamic provisioning
- local storage vs network storage
- stateful workload 的存儲考量

### 6. Cluster Lifecycle

- upgrade
- backup
- reset / cleanup
- node drain / cordon
- maintenance

### 7. HA 與拓樸

- single control plane
- stacked etcd
- external etcd
- multi-control-plane
- API endpoint 與 load balancing 概念

### 8. 安全深化

- admission control
- policy engine 基本概念
- image security
- secret management
- service-to-service identity

### 9. Self-Managed vs Managed Kubernetes

- `kubeadm`
- `k3s`
- `EKS`
- 自管 vs 代管的責任邊界

### 這一段的學習目標

做到這裡時，你應該可以：

- 更理解 control plane
- 更理解叢集 bootstrap
- 更理解 CNI / CRI / storage / HA
- 更貼近 cluster admin / self-managed cluster 的世界

---

## 建議學習順序

### Phase 1：先把 Kubernetes 用起來

1. 前置基礎
2. Kubernetes 核心物件
3. `kubectl`
4. `k3s`
5. 基本排錯

### Phase 2：把 homelab 做成平台

1. Helm
2. Ingress / Gateway
3. Prometheus
4. Grafana
5. Argo CD
6. cert-manager

### Phase 3：補 cluster admin 深度

1. `kubeadm`
2. Control plane
3. CNI / CRI
4. storage 深化
5. HA 與 upgrade

### Phase 4：補進階平台能力

1. Velero
2. Cilium
3. Istio
4. EKS 或其他 managed Kubernetes

---

## 對你目前最適合的主線

如果依你目前 `devops-homelab` 的階段和職涯目標，我會建議你這樣走：

1. `k3s`
2. Kubernetes 核心物件
3. `kubectl` + troubleshooting
4. Helm
5. Ingress
6. Prometheus + Grafana
7. Argo CD
8. cert-manager
9. `kubeadm`
10. Cilium / Velero / Istio
11. 最後再補 EKS

這樣的好處是：

- 前期先做出東西
- 中期把平台能力補齊
- 後期再補 cluster admin 深度

---

## 目錄使用建議

你之後可以把 `tech-stack-learning/k8s/` 大致維持成這樣：

- `README.md`：入口與導覽
- `LEARNING-STRUCTURE.md`：總學習架構
- `notes/`：主題筆記
- `articles/`：整理後的高質量文章

`notes/` 內可以逐步增加：

- `kubectl-basics.md`
- `workloads.md`
- `services-ingress.md`
- `storage-basics.md`
- `helm-basics.md`
- `argocd-basics.md`
- `prometheus-grafana-basics.md`
- `cert-manager-basics.md`
- `cni-cri-basics.md`
- `istio-basics.md`

## 一句話版

你可以把 Kubernetes 學習架構記成：

> 先學會用 `k3s` 跑 Kubernetes，再用生態工具把它做成平台，最後再補 `kubeadm`、control plane、CNI / CRI / HA 這些更偏 cluster admin 的深度知識。
