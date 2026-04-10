# Kubernetes Deployment Strategies

> 來源：CNCF Presentation - Deployment Strategies on Kubernetes (Etienne Tremel, Container Solutions)
> Hands-on repo: https://github.com/ContainerSolutions/k8s-deployment-strategies

---

## 目錄

- [總覽](#總覽)
- [1. Recreate](#1-recreate)
- [2. Ramped (Rolling Update)](#2-ramped-rolling-update)
- [3. Blue/Green (Red/Black)](#3-bluegreen-redblack)
- [4. Canary](#4-canary)
- [5. A/B Testing](#5-ab-testing)
- [6. Shadow (Mirrored/Dark)](#6-shadow-mirroreddark)
- [策略比較表](#策略比較表)
- [選擇指南](#選擇指南)

---

## 總覽

K8s 的 6 種部署策略依複雜度分為三級：

| 等級 | 策略 | 說明 |
|------|------|------|
| **Native**（原生支援） | Recreate, Ramped | `kubectl apply` 即可，無需額外元件 |
| **Extra step**（需額外操作） | Blue/Green, Canary | 需手動切換 Service selector 或調整 replica 數量 |
| **Additional component**（需額外元件） | A/B Testing, Shadow | 需要 Istio / Linkerd 等 service mesh |

### K8s 基礎架構複習

```
Deployment → ReplicaSet → Pod(s) ← Service ← Ingress ← User
```

- **Deployment**：管理 ReplicaSet，定義 Pod template 與 rollout 策略
- **ReplicaSet**：確保指定數量的 Pod 副本在運行
- **Service**：透過 label selector 將流量導向 Pod
- **Ingress**：L7 路由（host/path based），由 Ingress Controller 實作（Nginx、Traefik、Istio 等）

---

## 1. Recreate

### 機制

先把舊版本 (V1) **全部終止**，再啟動新版本 (V2)。

```
V1 running → V1 terminated → V2 starting → V2 running
                  ↑ downtime ↑
```

### 設定

```yaml
kind: Deployment
spec:
  replicas: 3
  strategy:
    type: Recreate
```

```bash
kubectl apply -f ./manifest.yaml
```

### 流量特徵

部署期間會有一段 **service unavailable**，時間取決於應用的 shutdown + boot 時間。

### 優缺點

| Pros | Cons |
|------|------|
| 設定最簡單 | 有停機時間（downtime） |
| 確保不會有新舊版本同時運行 | 對使用者影響大 |

### 適用場景

- 開發/測試環境
- 停機可接受的內部工具
- 新舊版本不能共存（如 DB schema 不相容）

---

## 2. Ramped (Rolling Update)

> 又名：Incremental、Rolling Update

### 機制

逐步用新版本 Pod 取代舊版本 Pod。過程中新舊版本會**共存**。

```
V1(3) → V1(2)+V2(1) → V1(1)+V2(2) → V2(3)
```

### 設定

```yaml
kind: Deployment
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 2        # 允許同時多出幾個新 Pod
      maxUnavailable: 0  # 滾動更新期間允許幾個 Pod 不可用
```

```bash
kubectl apply -f ./manifest.yaml
```

### 關鍵參數

| 參數 | 說明 | 常見設定 |
|------|------|---------|
| `maxSurge` | 更新時可超出 `replicas` 的 Pod 數量 | `1` 或 `25%` |
| `maxUnavailable` | 更新時允許不可用的 Pod 數量 | `0`（zero downtime）或 `1` |

### 流量特徵

流量從 V1 **平滑過渡**到 V2，沒有停機但過渡期新舊版本混合接收請求。

### 優缺點

| Pros | Cons |
|------|------|
| 簡單易用（K8s 預設策略） | 滾動更新需要時間 |
| 零停機 | 無法精確控制流量比例 |
| 適合 stateful app（漸進式 data rebalancing） | rollback 也需要時間 |

### 適用場景

- 大部分 production workload 的預設選擇
- 無狀態服務
- 新舊版本可短暫共存的場景

---

## 3. Blue/Green (Red/Black)

> 又名：Red/Black（Netflix 用語）

### 機制

1. V1（Blue）正在運行中，Service 指向 V1
2. 部署 V2（Green）完整副本，但 **Service 尚未指向它**
3. 測試 V2 確認正常
4. **切換 Service selector**，所有流量瞬間從 V1 → V2
5. 確認穩定後刪除 V1

```
Before:  Service → V1 (Blue)    V2 (Green) [idle]
Switch:  Service → V2 (Green)   V1 (Blue) [idle → delete]
```

### 設定方式一：Single Service（切換 selector）

```yaml
# Service 用 version label 精確匹配
kind: Service
spec:
  selector:
    app: my-app
    version: v1.0.0   # ← 切換時改成 v2.0.0
```

```bash
# 1. 部署 V2
kubectl apply -f ./manifest-v2.yaml

# 2. 切換流量（瞬間完成）
kubectl patch service my-app -p \
  '{"spec":{"selector":{"version":"v2.0.0"}}}'

# 3. 確認穩定後刪除 V1
kubectl delete -f ./manifest-v1.yaml
```

### 設定方式二：Ingress（多服務同時切換）

適合需要同時切換多個 microservice 的場景：

```yaml
kind: Ingress
spec:
  rules:
  - host: login.domain.com
    http:
      paths:
      - backend:
          serviceName: login-v2    # ← 指向新版 Service
          servicePort: 80
  - host: cart.domain.com
    http:
      paths:
      - backend:
          serviceName: cart-v2     # ← 指向新版 Service
          servicePort: 80
```

```bash
kubectl apply -f ./manifest-v2.yaml
kubectl apply -f ./ingress.yaml
kubectl delete -f ./manifest-v1.yaml
```

### 流量特徵

切換瞬間完成，**沒有新舊版本混合接收流量的過渡期**。

### 優缺點

| Pros | Cons |
|------|------|
| **瞬間切換**（instant rollout/rollback） | 需要**雙倍資源**（V1 + V2 同時運行） |
| 適合前端（versioned assets 從同一 server 載入） | 切換前需要完整測試 V2 |
| 可解決 dependency hell（整組服務一起切） | |

### 適用場景

- 需要零停機 + 瞬間 rollback 的關鍵服務
- 前端部署（避免 JS/CSS 版本混亂）
- 多個 microservice 需要同時切版

### 與 Recreate 的關鍵差異

| | Recreate | Blue/Green |
|---|----------|-----------|
| 停機 | 有 | 無 |
| 資源 | 1x | 2x |
| 切換速度 | 慢（等 boot） | 瞬間 |
| rollback | 慢（重新部署） | 瞬間（切回 selector） |

### Rollback 方式

只要把 Service selector 切回 V1 即可：

```bash
kubectl patch service my-app -p \
  '{"spec":{"selector":{"version":"v1.0.0"}}}'
```

---

## 4. Canary

### 機制

1. V1 承擔 100% 流量
2. 部署少量 V2 Pod（如 1/10），讓 V2 承擔約 10% 流量
3. 觀察 V2 的 error rate / latency / metrics
4. 逐步增加 V2 比例
5. 確認穩定後完全切換到 V2

### 設定方式一：Native（用 replica 數量控制比例）

```yaml
# V1: 9 replicas
kind: Deployment
metadata:
  name: my-app-v1
spec:
  replicas: 9
  template:
    labels:
      app: my-app
      version: v1.0.0

# V2: 1 replica（約 10% 流量）
kind: Deployment
metadata:
  name: my-app-v2
spec:
  replicas: 1
  template:
    labels:
      app: my-app
      version: v2.0.0

# Service 只看 app label，不區分 version
kind: Service
spec:
  selector:
    app: my-app   # ← 同時匹配 V1 和 V2 的 Pod
```

```bash
kubectl apply -f ./manifest-v2.yaml
kubectl scale deploy/my-app-v2 --replicas=10
kubectl delete -f ./manifest-v1.yaml
```

### 設定方式二：Istio（精確 weight-based routing）

```yaml
kind: RouteRule
metadata:
  name: my-app
spec:
  destination:
    name: my-app
  route:
  - labels:
      version: v1.0.0
    weight: 90    # 90% 流量
  - labels:
      version: v2.0.0
    weight: 10    # 10% 流量
```

### 優缺點

| Pros | Cons |
|------|------|
| 只對少量用戶暴露新版本 | 滾動較慢 |
| 適合監控 error rate / performance | 可能需要 sticky session |
| 快速 rollback（刪除 V2 即可） | 精確流量控制需要 Istio/Linkerd |

---

## 5. A/B Testing

### 機制

根據**請求條件**（而非隨機比例）將流量路由到不同版本。

### 可用條件

- Geolocation
- Language
- Cookie
- User-Agent（device、OS）
- Custom Header
- Query Parameters

### 設定（需 Istio）

```yaml
# V1: 匹配 header x-api-version: v1.0.0
kind: RouteRule
metadata:
  name: my-app-v1
spec:
  destination:
    name: my-app
  route:
  - labels:
      version: v1.0.0
  match:
    request:
      headers:
        x-api-version:
          exact: "v1.0.0"

# V2: 匹配 header x-api-version: v2.0.0
kind: RouteRule
metadata:
  name: my-app-v2
spec:
  destination:
    name: my-app
  route:
  - labels:
      version: v2.0.0
  match:
    request:
      headers:
        x-api-version:
          exact: "v2.0.0"
```

### 優缺點

| Pros | Cons |
|------|------|
| 多版本並行運行 | 需要 Istio / Linkerd |
| 完全控制流量分配 | 排錯困難，需要 distributed tracing |
| 適合 A/B 商業測試（提升 conversion） | |

### 與 Canary 的差異

| | Canary | A/B Testing |
|---|--------|-------------|
| 路由依據 | 隨機比例 | 請求條件（header, cookie 等） |
| 目的 | 驗證穩定性 | 驗證功能/UX 效果 |
| 精確度 | 粗略（replica 比例） | 精確（條件匹配） |

---

## 6. Shadow (Mirrored/Dark)

### 機制

1. V1 正常處理所有生產流量
2. 流量被**複製（mirror）**到 V2
3. V2 處理複製的請求，但 **response 被丟棄**（不影響使用者）
4. 監控 V2 的 performance / error
5. 確認穩定後正式切換

### 設定（需 Istio）

```yaml
kind: RouteRule
spec:
  destination:
    name: my-app
  route:
  - labels:
      version: v1.0.0
    weight: 100
  - labels:
      version: v2.0.0
    weight: 0
  mirror:
    name: my-app-v2
    labels:
      version: v2.0.0
```

### 優缺點

| Pros | Cons |
|------|------|
| 用真實流量測試 performance | 設定複雜 |
| 對使用者完全無影響 | 需要雙倍資源 |
| 上線前就能驗證穩定性 | 不是真正的用戶測試（可能誤導） |
| | 有副作用的操作需要 mock（如寫入 DB） |

---

## 策略比較表

| 策略 | Zero Downtime | Real Traffic Testing | Targeted Users | Cloud Cost | Rollback Duration | User Impact | Setup Complexity |
|------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Recreate** | X | X | X | Low | High | High | Low |
| **Ramped** | O | X | X | Low | High | Low | Low |
| **Blue/Green** | O | X | X | **High** | **Low** | Medium | Medium |
| **Canary** | O | O | X | Low | Low | Low | Medium |
| **A/B Testing** | O | O | O | Low | Low | Low | **High** |
| **Shadow** | O | O | X | **High** | Low | None | **High** |

---

## 選擇指南

```
需要停機嗎？
├── 可以停機 → Recreate
└── 不可以
    ├── 需要瞬間切換？ → Blue/Green
    ├── 需要精確控制流量到特定用戶？ → A/B Testing（需 Istio）
    ├── 想先用真實流量測試但不影響用戶？ → Shadow（需 Istio）
    ├── 想先對少量用戶驗證？ → Canary
    └── 一般滾動更新就好 → Ramped（K8s 預設）
```

### 一句話總結

- **Recreate**：停機換版，最簡單
- **Ramped**：K8s 預設，漸進式替換
- **Blue/Green**：雙環境秒切，貴但安全
- **Canary**：先讓 10% 用戶試水溫
- **A/B Testing**：按條件分流，驗證商業假設
- **Shadow**：暗中用真實流量壓測，用戶無感

---

*最後更新：2026-04-10*
