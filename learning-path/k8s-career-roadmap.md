# Kubernetes 學習與職涯對齊路線圖

更新日期：2026-03-26

## 為什麼現在值得補強 Kubernetes

以你目前履歷來看，你已經有很不錯的基礎：

- AWS SAA
- Linux / RHEL 維運
- Terraform
- Python
- 雲端架構與 PoC 經驗

這代表你不是從零開始學 k8s，而是很適合把既有的 AWS + Linux + IaC 能力，往「雲原生平台 / DevOps / SRE」再推進一階。

這次查到的職缺與官方資料，顯示出一個很清楚的方向：

- 市場上常把 **Kubernetes、AWS、Terraform、CI/CD、監控告警** 綁在一起看
- CNCF 仍把 Kubernetes 放在 cloud native 技能主軸
- 對你這種偏 infra / platform 背景的人來說，**CKA / EKS / GitOps / Observability** 的投資報酬率比只學理論更高

## 結合 devops-homelab 之後的判斷

綜合參考 `devops-homelab/README.md`、`devops-homelab/plan.md`、`devops-homelab/system-reference.md` 後，你的 k8s 學習其實已經有一個很好的落地場景，不需要另外再想一個全新的 side project。

你現在的 homelab 已有這些條件：

- Ubuntu 24.04.4 LTS
- Docker 已可正常運作
- Tailscale / SSH 已打通遠端管理
- 主機資源約 30 GiB RAM，足夠拿來做 k3s 單節點或小型多節點練習
- 現有規劃本來就包含 Linux、K8s、Monitoring、GitOps、Terraform

所以更合理的策略不是「另外學 Kubernetes」，而是：

1. 把 `devops-homelab` 升級成 **Kubernetes 主專案**
2. 用 homelab 驗證平台能力
3. 再把同樣的設計思路外推到 EKS

## 先學什麼最划算

### 第一層：核心觀念

先把這些打穩，之後看 EKS、Helm、Argo CD 才不會碎掉：

1. Cluster 架構
2. Pod / Deployment / StatefulSet / DaemonSet / Job / CronJob
3. Service / DNS / Gateway / Ingress
4. ConfigMap / Secret / Probe
5. Volume / PV / PVC / StorageClass
6. Requests / Limits / HPA
7. RBAC / ServiceAccount / 基本安全觀念
8. kubectl 操作與故障排查

### 第二層：真的會讓履歷加分的主題

這一層最接近職場實作：

1. Helm
2. Argo CD / GitOps
3. Prometheus + Grafana
4. Logs / metrics / tracing 的基本觀念
5. NetworkPolicy
6. Pod Security / Secret 管理
7. Cluster upgrade / node maintenance / rollout / rollback
8. Troubleshooting：CrashLoopBackOff、ImagePullBackOff、探針失敗、排程失敗

### 第三層：和你背景最搭的 AWS 路線

如果目標是找 DevOps / Cloud / Platform Engineer，建議把 k8s 學習主線直接綁到 EKS：

1. EKS cluster lifecycle
2. IAM 與 Kubernetes access
3. IRSA / workload access to AWS
4. ECR 映像流程
5. Load balancing / external access
6. Managed add-ons
7. CloudWatch / Prometheus 觀測
8. Terraform 建 EKS

## 依你背景，建議的學習順序

### 路線判斷

以你的履歷來看，我會建議：

- 主線：**CKA / 平台維運導向**
- 支線：EKS + Terraform + GitOps
- 補強：Observability + Security basics

這是因為你目前已經偏 infra / cloud engineer，而不是純 application developer。  
所以比起優先衝 CKAD，**先把 CKA 能力做紮實**，對履歷敘事會更一致。

以上是根據你的履歷做的推論，不是唯一正解；如果你之後想轉偏 application platform 或 developer productivity，再補 CKAD 很合理。

## 和 devops-homelab 對齊的執行路線

### Stage 1：延續既有 Linux 強化

這一段不用重做方向，只要讓它更明確地服務後面的 k8s：

- systemd、journalctl、網路、防火牆、磁碟與檔案系統
- 把 server baseline 寫成 runbook
- 明確記錄 hostname、IP、VPN、SSH、磁碟、服務狀態

這段做完後，你之後在 k8s 遇到 node、container runtime、network 問題時，會比一般只背指令的人更有優勢。

### Stage 2：把 Docker 階段做成 k8s 前置

`devops-homelab` 原本的 Docker 階段很合理，建議保留，但目的要改成「為 k8s 做準備」：

- 至少做 1 個可部署的 app image
- 補 health check、env、volume、non-root、image scan
- 讓 app 可以先在 Docker Compose 跑，再遷移到 k8s

這樣你後面就能清楚展示「從 containerization 走到 orchestration」。

### Stage 3：先在 homelab 跑 k3s，不要一開始就跳 EKS

依你目前 homelab 規劃，**k3s 是最合理的第一個 k8s 落地點**：

- 成本低
- 控制面可見度高
- 適合 troubleshooting
- 很容易和你現有 Ubuntu / Docker / Tailscale / SSH 環境銜接

這個階段建議的最小驗收：

1. 安裝 k3s
2. 用 `kubectl` 管理 cluster
3. 部署 app 到 Deployment + Service
4. 加入 ConfigMap、Secret、Probe
5. 用 Ingress 或 Gateway 做外部存取
6. 用 Helm 部署至少一個常見元件

### Stage 4：把可觀測性棧接上 k3s

你原本 `devops-homelab` 的 Monitoring 規劃，正好就是 k8s 履歷的加分區：

- Prometheus
- Grafana
- Alertmanager
- 日誌集中化

這一段建議不要只停在「有裝起來」，而是要做到：

- 有 node / pod / workload dashboard
- 有 CPU、memory、restart、latency 等關鍵指標
- 有至少 2 到 3 條實際會觸發的告警規則
- 有一份故障排查紀錄

### Stage 5：把 GitHub Actions + Argo CD 串成 GitOps 故事

這會直接把 homelab 從學習專案提升成平台專案：

- GitHub Actions 負責 build、test、scan
- Argo CD 負責 deploy 到 k3s
- `main` / `develop` 對應 prod / staging
- rollback 流程清楚可展示

這部分做起來之後，你面試時就不只是在講 k8s，而是在講 **平台交付能力**。

### Stage 6：最後再把同一套概念外推到 EKS

EKS 不該是第一步，比較像是 homelab 驗證完成後的升級版：

- 用 Terraform 建 EKS
- 將 homelab 上已驗證的 app / Helm / GitOps / monitoring 模式搬上去
- 補 IAM、IRSA、ECR、managed add-ons

這樣你的作品集會形成很漂亮的敘事：

`homelab k3s 驗證平台能力` → `EKS 展示雲端落地能力`

## 最值得做成作品集的題目

### 題目 1：以 devops-homelab 為核心的 k3s 平台專案

內容：

- 在 homelab 上安裝 k3s
- 部署 sample app
- 補 Helm、Ingress 或 Gateway、Secrets、PVC
- 接 Prometheus / Grafana / Alertmanager
- 接 GitHub Actions + Argo CD

履歷價值：

- 最貼近你目前已有規劃
- 可以持續迭代
- 面試時可 demo，可講 troubleshooting，也可講平台設計

### 題目 2：從 Docker Compose 遷移到 Kubernetes

內容：

- 先把 app 跑在 Docker Compose
- 再遷移到 k3s
- 比較部署、回滾、設定管理、監控方式的差異
- 寫 migration plan、rollback plan、runbook

履歷價值：

- 很像企業從 legacy / VM / compose 走向 k8s 的真實場景
- 能把你原本 Linux / Docker 能力自然接到 k8s

### 題目 3：Homelab 驗證後，再外推到 EKS

內容：

- Terraform 建 EKS、VPC、IAM、ECR
- 把 homelab 上驗證過的 workload 與部署流程搬到 EKS
- 補 IRSA、CloudWatch、managed add-ons

履歷價值：

- 最能把你原本的 AWS + Terraform + Linux 優勢和 k8s 串起來

### 題目 4：Kubernetes Troubleshooting Lab

內容：

- 故意製造 probe fail、DNS fail、image pull fail、resource shortage、RBAC deny
- 記錄排查流程與修復手法

履歷價值：

- 很適合你目前偏系統工程 / 維運敘事
- 面試時很容易拿來講 incident handling

## 建議你真正採用的主線

如果綜合 `resume/` 和 `devops-homelab/` 來看，我會建議你把主線收斂成這樣：

1. 用 `devops-homelab` 完成 Linux → Docker → k3s → Monitoring → GitOps
2. 把這整套整理成 portfolio 主專案
3. 再做一個 EKS 版本，當作 cloud extension

這樣會比「單獨學 k8s 指令」或「一開始就直接衝 EKS」更有職涯效果。

## 履歷上可以怎麼包裝

當你把 `devops-homelab` 走到 k3s + monitoring + GitOps 後，履歷 bullet 可以往這種方向寫：

- 在 Ubuntu homelab 上建置 k3s 容器平台，完成從 Docker 化應用到 Kubernetes 編排的落地實作
- 以 GitHub Actions 與 Argo CD 建立 GitOps 交付流程，實現 staging / production 多環境部署
- 導入 Prometheus、Grafana 與告警機制，建立 pod / node / workload 可觀測性與故障排查流程
- 規劃 Kubernetes health checks、滾動更新、回滾與設定管理，提升服務穩定性與部署一致性

如果後續再補 EKS 版本，則可以再加：

- 使用 Terraform 建置 Amazon EKS 與基礎網路資源，將 homelab 驗證過的平台模式外推至 AWS

## 這次 web fetch 的重點結論

1. 官方最新穩定版 Kubernetes 目前是 **v1.35.3**。
2. 官方文件仍把 cluster architecture、workloads、networking、configuration、security、observability 當核心學習面向。
3. Kubernetes 官方文件已明確提醒：**Ingress 還能用，但 API 已 frozen，新的方向更偏 Gateway**。
4. CNCF 官方證照路線仍以 **KCNA → CKA → CKS** 或 **KCNA → CKAD** 為主。
5. 台灣職缺上，`K8s + Terraform + AWS + GitOps + Prometheus/Grafana + Linux/Python` 的組合非常常見。
6. 依你目前履歷背景，最值得投資的是 **先用 homelab 做 k3s 平台實作，再延伸到 CKA + EKS + GitOps + Observability**。

## 官方與參考來源

- Kubernetes stable release: https://dl.k8s.io/release/stable.txt
- Kubernetes Components: https://kubernetes.io/docs/concepts/overview/components/
- Kubernetes Install Tools: https://kubernetes.io/docs/tasks/tools/
- Install kubectl on Windows: https://kubernetes.io/docs/tasks/tools/install-kubectl-windows/
- Ingress: https://kubernetes.io/docs/concepts/services-networking/ingress/
- Linux Foundation LFS158 Introduction to Kubernetes: https://training.linuxfoundation.org/training/introduction-to-kubernetes/
- CNCF Training & Certification: https://www.cncf.io/training/
- Amazon EKS User Guide: https://docs.aws.amazon.com/eks/latest/userguide/what-is-eks.html
- AWS EKS Best Practices Guide: https://aws.github.io/aws-eks-best-practices/
- 104 SRE / DevOps 職缺搜尋： https://www.104.com.tw/jobs/search/?keyword=sre+devops

## 我對你的建議

如果目標是「讓履歷在未來 3 到 6 個月更有競爭力」，不要把重心放在背很多 YAML。  
最有效的做法是：

1. 先用 `devops-homelab` 完成 **k3s + monitoring + GitOps**
2. 把過程整理成 runbook、架構圖、troubleshooting 記錄
3. 再把同樣模式延伸成 **EKS + Terraform** 版本
4. 最後再決定要不要補 **CKA**

這樣最容易把學習成果轉成可面試、可寫履歷、可展示的職涯資產。
