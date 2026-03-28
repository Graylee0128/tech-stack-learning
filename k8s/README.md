# Kubernetes 學習指南

Kubernetes 相關的學習筆記與技術文章。這個目錄目前以三個分類來整理：

1. `Kubernetes 核心`
2. `Kubernetes 常用平台生態`
3. `Cluster admin 進階`

## 目錄結構

### 根目錄

- `LEARNING-STRUCTURE.md` - Kubernetes 學習主架構，拆成基礎 / 生態 / 進階三條主線
- `README.md` - 本目錄入口與導覽

### `core/` - Kubernetes 核心

- `k3s-vs-kubernetes.md` - `K3s` 與標準 Kubernetes 的差異、適用場景、選擇邏輯

### `ecosystem/` - Kubernetes 常用平台生態

- `ecosystem-overview.md` - Helm、Argo CD、Ingress、Prometheus、Grafana、cert-manager、Cilium、Velero、Istio

### `cluster-admin/` - Cluster admin 進階

- `kubeadm-basics.md` - `kubeadm`、cluster bootstrap、control plane、自管叢集入門

### 各分類目前筆記

- `core/k3s-vs-kubernetes.md`
- `ecosystem/ecosystem-overview.md`
- `cluster-admin/kubeadm-basics.md`

## 快速導覽

- 先看 `LEARNING-STRUCTURE.md` 建立整體學習地圖
- 想先上手 Kubernetes 本體，進 `core/`
- 想補 Helm / Argo CD / Prometheus / Grafana / Istio，進 `ecosystem/`
- 想補 `kubeadm` / control plane / CNI / HA，進 `cluster-admin/`

## 這個目錄在學什麼

### 1. Kubernetes 核心

先搞懂平台本體，以及在 `k3s` 上就能直接練到的知識：

- `k8s` / Kubernetes 是什麼
- `kubectl`
- `k3s`
- Cluster / Pod / Deployment / Service / Ingress / Storage / RBAC

### 2. Kubernetes 常用平台生態

再補齊實際工作環境常見套件：

- `Helm`：套件管理
- `Kustomize`：原生 YAML 疊加
- `Argo CD`：GitOps
- `Ingress` / `Gateway`：入口流量
- `Prometheus` + `Grafana`：監控觀測
- `cert-manager`：憑證自動化
- `Cilium`：進階網路與觀測
- `Velero`：備份還原
- `Istio`：service mesh

### 3. Cluster admin 進階

最後再補更貼近自管叢集與叢集管理員的知識：

- `kubeadm`
- control plane
- cluster bootstrap
- CNI / CRI
- storage 深化
- upgrade / reset / backup
- HA 與拓樸

## 建議閱讀順序

1. **先釐清平台名詞** - `core/k3s-vs-kubernetes.md`
2. **再看整體學習地圖** - `../k8s/LEARNING-STRUCTURE.md`
3. **接著看生態系全貌** - `ecosystem/ecosystem-overview.md`
4. **最後補 cluster admin 深度** - `cluster-admin/kubeadm-basics.md`

## 學習順序建議

1. `Kubernetes 核心`：核心物件、`kubectl`、`k3s`
2. `Kubernetes 常用平台生態`：`Helm`、`Ingress` / `Gateway`、`Prometheus`、`Grafana`、`Argo CD`、`cert-manager`
3. `Cluster admin 進階`：`kubeadm`、control plane、CNI / CRI、storage、HA、upgrade

## 對你目前最適合的主線

如果目標是先做出能展示的 DevOps / platform 作品集，最適合你的順序是：

1. `Kubernetes 核心`
2. `Kubernetes 常用平台生態`
3. `Cluster admin 進階`

如果展開成實作順序，會是：

1. `k3s`
2. `Helm`
3. `Ingress`
4. `Prometheus`
5. `Grafana`
6. `Argo CD`
7. `cert-manager`
8. `kubeadm`
9. `Cilium` / `Velero` / `Istio`

這樣比較符合你目前的 homelab 階段，也比較容易把學習成果轉成履歷亮點。

---

**最後更新：** 2026-03-26
