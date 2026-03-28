# Kubernetes 生態系套件總覽

更新日期：2026-03-26

## 先講結論

Kubernetes 本身只提供「容器編排平台的核心能力」。

但真正在工作或 homelab 裡，通常還要再補上一整圈生態系工具，才會變成一個能實際運作的平台。  
你前面提到的 `Helm`、`Istio` 就是這個生態系的一部分。

可以先把整體分成這幾層：

1. 套件管理與配置
2. 交付與 GitOps
3. 對外流量入口
4. 觀測與告警
5. 憑證與安全
6. 網路與 CNI
7. 備份與災難復原
8. Service Mesh

## 一張圖看懂角色分工

```text
開發者 / Git Repo
    ↓
Helm / Kustomize
    ↓
Argo CD
    ↓
Kubernetes Cluster
    ├─ Ingress-NGINX / Traefik / Gateway API implementation
    ├─ Prometheus + Alertmanager
    ├─ Grafana
    ├─ cert-manager
    ├─ Cilium
    ├─ Velero
    └─ Istio
```

## 1. Helm

### 它是做什麼的

`Helm` 是 Kubernetes 的 package manager。  
官方文件把它定位成幫助你定義、安裝、升級 Kubernetes 應用。

它的核心概念是：

- `Chart`：一組可重複使用的 Kubernetes manifests 模板
- `Release`：某個 chart 在 cluster 裡實際安裝出來的實例
- `values.yaml`：你用來覆寫參數的設定檔

### 它解決什麼問題

如果只靠手寫 YAML，你很快就會遇到：

- 同一套 app 在 dev / staging / prod 參數不同
- 安裝第三方元件很麻煩
- 版本升級不好管理

`Helm` 讓你可以比較像：

- `apt install`
- `brew install`
- `terraform module`

那樣去管理 Kubernetes 套件。

### 什麼時候用

- 安裝 Prometheus、Grafana、Argo CD、ingress controller 等常見元件
- 管理多環境配置差異
- 做版本化升級與回滾

### 你現在的優先度

很高。  
對你目前的 homelab 來說，`Helm` 幾乎是第一批該學的生態工具。

## 2. Kustomize

### 它是做什麼的

Kubernetes 官方文件把 `Kustomize` 定位成自訂 Kubernetes objects 的工具，`kubectl` 也直接支援 `-k`。

### 它解決什麼問題

如果你不想用模板語言，而想保持 YAML 原貌，只做：

- base / overlay
- patch
- image tag 替換
- labels / namespace 注入

那 `Kustomize` 很適合。

### 和 Helm 差在哪

- `Helm` 偏套件管理、模板化、參數化
- `Kustomize` 偏原生 YAML 疊加、patch、overlay

### 你怎麼用比較好

對你現在來說：

- 安裝第三方元件先用 `Helm`
- 自己的 app 多環境配置可以再學 `Kustomize`

## 3. Argo CD

### 它是做什麼的

`Argo CD` 是 Kubernetes 的 declarative GitOps CD 工具。  
官方 getting started 文件的流程核心就是：把 Git repo 內容同步部署到 cluster。

### 它解決什麼問題

它讓「Git repo 裡的設定」變成系統的 source of truth。

也就是說：

- 你改 Git
- Argo CD 偵測差異
- Argo CD 幫你同步到 cluster

### 典型角色

- GitHub Actions：build、test、security scan
- Argo CD：deploy / sync

### 你現在的優先度

很高。  
因為它和你的 `devops-homelab` GitOps 規劃直接對齊。

## 4. Ingress Controller / Gateway API

### 它是做什麼的

這一層負責把 cluster 內的服務對外暴露。

常見做法有：

- `ingress-nginx`
- `Traefik`
- Gateway API 的各種實作

### 重要背景

Kubernetes 官方文件目前已明確寫出：

- `Ingress` API 仍可用
- 但 `Ingress API has been frozen`
- 官方建議新的方向看 `Gateway API`

所以今天你還是會常看到 Ingress controller，  
但觀念上最好知道未來方向正在往 Gateway API 走。

### 常見工具

#### `ingress-nginx`

- 很常見
- 社群使用量大
- 很多教學都以它為基準

#### `Traefik`

- 在 `k3s` 裡常見
- 整合度高
- homelab 體驗通常不錯

### 你現在的優先度

高。  
因為一旦你要做 homelab demo、Argo CD UI、Grafana UI，就會碰到對外入口。

## 5. Prometheus

### 它是做什麼的

`Prometheus` 是開源監控與告警工具包。  
官方文件強調它收集並儲存 time series metrics，並以 labels 做多維度查詢。

### 它解決什麼問題

你需要知道：

- node CPU / memory
- pod restart 次數
- HTTP latency
- error rate
- 資源是否快爆了

`Prometheus` 幫你蒐集 metrics。  
它通常還會搭配：

- exporters
- alerting rules
- Alertmanager

### 你要記住的角色

- `Prometheus`：收集與查詢 metrics
- `Alertmanager`：處理告警通知、靜音、聚合

### 你現在的優先度

非常高。  
你目標是 DevOps / SRE / platform 類職涯，沒有 metrics/alerting 幾乎不完整。

## 6. Grafana

### 它是做什麼的

Grafana 官方文件把它定位成查詢、視覺化、告警、探索 metrics / logs / traces 的平台。

### 它解決什麼問題

如果 Prometheus 比較像資料來源，  
那 Grafana 就比較像可視化與操作介面。

你通常用它來：

- 看 dashboard
- 追查異常
- 做 alerting 視覺化
- 串接不同資料來源

### 典型組合

- Prometheus + Grafana = metrics 監控的經典組合
- Loki + Grafana = logs
- Tempo + Grafana = traces

### 你現在的優先度

非常高。  
因為它最容易把你的 homelab 做成可展示、可觀察的平台。

## 7. cert-manager

### 它是做什麼的

`cert-manager` 是 Kubernetes / OpenShift 的 X.509 certificate controller。  
官方文件說它會取得憑證、確保憑證有效、並在到期前自動更新。

### 它解決什麼問題

如果你的服務要 HTTPS / TLS，手動管憑證非常麻煩。

`cert-manager` 常見用途：

- 幫 Ingress 自動簽發 TLS 憑證
- 對接 Let's Encrypt
- 對接內部 PKI / Vault / private CA
- 支援 service mesh 相關憑證需求

### 你現在的優先度

中高。  
當你開始把服務對外暴露、想做 HTTPS 時，它就很重要。

## 8. Cilium

### 它是做什麼的

`Cilium` 是基於 eBPF 的 Kubernetes networking、security、observability 解法。  
官方文件強調它可提供網路連線、安全控管、以及可視性。

### 它解決什麼問題

它不只是 CNI，還常被拿來做：

- NetworkPolicy
- kube-proxy replacement
- 更進階的流量可視化
- Hubble 網路觀測

### 什麼時候需要它

當你開始覺得「只是把 Pod 接起來」不夠，想要：

- 看 service-to-service 流量
- 做更強的 network policy
- 練 cloud native networking 深度

就會碰到 `Cilium`。

### 你現在的優先度

中。  
不是第一批，但很值得之後補，尤其你本來就偏 infra / networking 背景。

## 9. Velero

### 它是做什麼的

`Velero` 是 Kubernetes 備份與還原工具。  
官方文件說它能備份 / 還原 cluster resources 與 persistent volumes，也能做 cluster migration。

### 它解決什麼問題

它回答的是這類問題：

- cluster 壞了怎麼救
- namespace 被刪掉怎麼回復
- workload 要搬去另一個 cluster 怎麼處理

### 你現在的優先度

中。  
不是最早要學，但如果你想把 homelab 做得更像 production 平台，這塊會很加分。

## 10. Istio

### 它是做什麼的

`Istio` 是 service mesh。  
官方文件把它描述成一層透明套在既有分散式應用上的 service mesh，提供更一致的安全、連線、監控與流量控制能力。

### 它解決什麼問題

當你的系統開始變成多服務時，服務間流量會出現很多進階需求：

- service-to-service mTLS
- identity-based auth
- traffic splitting
- retries / failover
- fault injection
- 更細的 east-west traffic 觀測

這些不是一般 Ingress 或 basic Service 就能完整處理的。

### 你可以怎麼理解它

- Ingress / Gateway：偏 north-south traffic，外面進來 cluster
- Istio：偏 east-west traffic，service 彼此之間

### 什麼時候需要它

當你已經有：

- 多服務架構
- 流量治理需求
- mTLS / service identity 需求
- service-level observability 需求

才會真正感受到 `Istio` 的價值。

### 你現在的優先度

偏後。  
它很重要，但不是你現在 homelab 第一階段最該先裝的東西。

先把：

- `Helm`
- `Ingress`
- `Prometheus`
- `Grafana`
- `Argo CD`

走順，再補 `Istio` 會比較自然。

## 11. 這些工具怎麼串起來

一個常見的 homelab / platform 組合會像這樣：

1. 用 `Helm` 安裝平台元件
2. 用 `Argo CD` 做 GitOps 同步
3. 用 `Ingress controller` 或 `Gateway API` 對外暴露服務
4. 用 `cert-manager` 管 TLS 憑證
5. 用 `Prometheus + Alertmanager` 收集 metrics 與告警
6. 用 `Grafana` 做 dashboard
7. 進階再補 `Cilium` 做網路可視化與策略
8. 再進一步補 `Istio` 做 service mesh
9. 用 `Velero` 做備份還原

## 12. 對你目前最重要的學習順序

依你現在的 `devops-homelab` 目標，我建議優先順序是：

### 第一批：先學

- `Helm`
- `Ingress controller` 或 `Traefik`
- `Prometheus`
- `Grafana`
- `Argo CD`

這一批能最快讓你的 homelab 變成「有部署、有入口、有監控、有 GitOps」的平台。

### 第二批：接著補

- `cert-manager`
- `Kustomize`
- `Velero`

這一批會讓平台更完整、更接近 production。

### 第三批：進階

- `Cilium`
- `Istio`

這一批比較偏網路、治理、service mesh 深度，不是現在第一優先。

## 13. 一句話版速記

- `Helm`：Kubernetes 套件管理
- `Kustomize`：原生 YAML 疊加與 patch
- `Argo CD`：GitOps 部署同步
- `Ingress / Gateway`：把服務對外暴露
- `Prometheus`：metrics 與 alerting
- `Grafana`：dashboard 與可視化
- `cert-manager`：TLS 憑證自動化
- `Cilium`：進階網路、安全、觀測
- `Velero`：備份與還原
- `Istio`：service mesh 與流量治理

## 14. 對你現在最有用的結論

如果你現在是在想：

> Kubernetes 生態系這麼多套件，我到底先碰哪幾個？

那對你最實際的答案是：

1. 先學 `Helm`
2. 再學 `Ingress`
3. 再做 `Prometheus + Grafana`
4. 然後接 `Argo CD`
5. HTTPS 需要時補 `cert-manager`
6. `Istio` 放到後面，等你真的有多服務治理需求再上

## 官方參考來源

- Helm Introduction  
  https://helm.sh/docs/intro/
- Using Helm  
  https://helm.sh/docs/intro/using_helm
- Kustomize  
  https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization
- Argo CD Getting Started  
  https://argo-cd.readthedocs.io/en/latest/getting_started/
- Ingress  
  https://kubernetes.io/docs/concepts/services-networking/ingress/
- Ingress Controllers  
  https://kubernetes.io/docs/concepts/services-networking/ingress-controllers/
- Gateway API  
  https://kubernetes.io/docs/concepts/services-networking/gateway/
- Prometheus Overview  
  https://prometheus.io/docs/
- Prometheus Alerting Overview  
  https://prometheus.io/docs/alerting/latest/overview/
- Grafana Introduction  
  https://grafana.com/docs/grafana/latest/introduction
- cert-manager  
  https://cert-manager.io/
- Cilium Introduction  
  https://docs.cilium.io/en/stable/intro/
- Velero Overview  
  https://velero.io/docs/main/
- What is Istio?  
  https://istio.io/latest/docs/overview/what-is-istio/

## 補充說明

文中關於「哪些工具你該先學、哪些放後面」這一段，不是官方直接給你的固定排序。  
這是我根據：

- 這些工具的官方定位
- 你目前的 homelab 階段
- 你要做 DevOps / platform 向作品集

做出的實務排序建議。
