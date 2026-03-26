# 08 EKS Networking

## Kubernetes / EKS Architecture

**What:** EKS 是 AWS 受管 Kubernetes；Control Plane 由 AWS 管，Data Plane 在你的 VPC。

**When to use:** 容器平台、Kubernetes 網路模型、Pod-to-Pod / Pod-to-Service 連線。

**Key Points:**
- EKS Control Plane 在 AWS managed VPC。
- Data Plane 節點在 customer VPC。
- EKS 會在你的 VPC 中建立 ENI 做控制平面與叢集通訊。
- Cluster Endpoint 可是 Public、Public+Private、或 Private only。

**⚠️ 考試陷阱:**
- EKS API 與 Kubernetes API server 概念不同；題目常故意混淆。

**✅ 記憶點:**
- `Control plane AWS managed, worker nodes customer VPC`。

## VPC CNI / Pod IP / Prefix Delegation

**What:** EKS 官方網路模型依賴 VPC CNI，讓 Pod 直接使用 VPC 位址。

**When to use:** Pod IP 規劃、ENI 限制、IP 用盡、Nitro 優化。

**Key Points:**
- Amazon VPC CNI 會在 Node 上建立/附加 ENI，並把 Secondary IP 分配給 Pods。
- 每種 Instance type 可附加的 ENI 與每 ENI 可掛的 IP 不同，因此會影響 Pod 數上限。
- Prefix delegation 可把 `/28` IPv4 或 `/80` IPv6 Prefix 指派給 ENI，提高可用 Pod IP 數。
- EKS 不支援 dual-stack Pod 模式。

**⚠️ 考試陷阱:**
- Pod 數量上限常不是 Kubernetes 限制，而是 ENI/IP 容量限制。

**✅ 記憶點:**
- `Pod IP shortage` 先想 Instance ENI limits、Prefix delegation、Custom networking。

## Pod Egress / IPv6 / Custom Networking

**What:** Pod 對外流量與 IP 規劃是 EKS 題型常見陷阱。

**When to use:** Pod 對外來源 IP、Secondary CIDR、IPv6-only Pod。

**Key Points:**
- Pod 對外到 VPC 外部 IPv4 時，預設會 SNAT 成 Node Primary ENI Primary IPv4。
- Private Subnet 常再透過 NAT Gateway 出網。
- 啟用 Custom Networking 後，可讓 Pod 從 Secondary CIDR 子網拿 IP，例如 `100.64.0.0/10` 空間。
- IPv6 Pod 不需要 NAT，但 VPC 基礎仍需要 IPv4。

**⚠️ 考試陷阱:**
- EKS IPv6 不代表整個 VPC 可以沒有 IPv4。

**✅ 記憶點:**
- `Need more pod IPs without resizing VPC` 想 Secondary CIDR + Custom Networking。

## Security Groups for Pods

**What:** EKS 預設是 Node 共用 SG；進階模式可讓 Pod 擁有獨立 SG。

**When to use:** 不同 Pod 需要不同網路隔離規則。

**Key Points:**
- 預設 SG 綁在 Node ENI 上，所有 Pod 共用。
- 可透過 Trunk/Branch ENI 與 `amazon-vpc-resource-controller-k8s` 讓 Pod 有獨立 ENI/SG。
- 也可用 Calico 等 Network Policy Engine 控制 Pod 間流量。

**⚠️ 考試陷阱:**
- 問到「Pod 層級 SG」通常不是單純 Kubernetes Network Policy 就能完成。

**✅ 記憶點:**
- `AWS-native SG per pod` 想 Trunk/Branch ENI。

## Exposing Services

**What:** Kubernetes Service/Ingress 決定應用如何被叢集內外存取。

**When to use:** Cluster internal service、L4 對外、L7 對外。

**Key Points:**
- `ClusterIP` 只供叢集內部使用。
- `NodePort` 以 NodeIP:Port 對外，不是大規模正式入口首選。
- `ServiceType=LoadBalancer` 多用 NLB。
- `Ingress` 多搭配 AWS Load Balancer Controller 建立 ALB。
- ALB 可透過 Ingress Group 共用同一個 ALB。
- `X-Forwarded-For` 與 `externalTrafficPolicy` 會影響 Client IP 保存。

**⚠️ 考試陷阱:**
- `externalTrafficPolicy=Local` 才能保留 Client IP，但可能造成流量分佈不均。

**✅ 記憶點:**
- `L4 external` 想 LoadBalancer/NLB。
- `L7 external` 想 Ingress/ALB。
