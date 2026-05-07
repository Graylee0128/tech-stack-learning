# Linux / OS Internals Roadmap for SRE

> 建立日期：2026-05-07
> 定位：Cloud Platform / SRE / DevSecOps / FinOps 主線的底層能力地圖。

## 目標

這份 roadmap 不追求把作業系統課本完整讀完，而是優先補真實 incident 裡會用到的 Linux 內部機制。

要能回答的問題：

- 為什麼 CPU 高但 throughput 沒上去？
- 為什麼 memory pressure 導致 pod eviction？
- 為什麼 fd leak 會拖垮 service？
- 為什麼 TCP connection 還在但 gRPC timeout？
- 為什麼 conntrack table 滿會造成服務不穩？
- 為什麼 container 被 limit throttling，app 卻只看到 latency 上升？

## 主題優先級

| 優先級 | 主題 | SRE 實務連結 |
|---|---|---|
| P1 | Process / Thread | CPU 飆高、context switch、goroutine / thread 對照 |
| P1 | Scheduler | run queue、CPU saturation、throttling |
| P1 | Memory management | RSS、page cache、OOM、memory pressure |
| P1 | Virtual memory | page fault、swap、copy-on-write |
| P1 | File descriptor | fd leak、socket leak、ulimit |
| P1 | Linux networking stack | TCP state、socket buffer、conntrack、iptables / nftables |
| P2 | epoll / io_uring | high concurrency server、event loop、I/O bottleneck |
| P2 | cgroups / namespaces | container isolation、Kubernetes resource behavior |
| P2 | systemd | service lifecycle、restart policy、journal |
| P2 | eBPF | tracing、network observability、runtime security |
| P3 | Filesystem / block I/O | disk latency、fsync、overlayfs、PVC behavior |
| P3 | Performance tooling | `top`、`htop`、`pidstat`、`vmstat`、`iostat`、`ss`、`perf`、`bcc` |

## 實作型 Lab

### Lab 1：CPU 高但 throughput 沒上去

- 建立一個 CPU-bound HTTP service
- 用 `top` / `pidstat` 看 CPU 使用率
- 用壓測觀察 throughput 與 latency
- 分析 user time、system time、context switch
- 對照 container CPU limit / throttling

### Lab 2：Memory pressure 與 pod eviction

- 建立一個可控制 memory growth 的 service
- 觀察 RSS、page cache、swap、OOM killer
- 在 Kubernetes 中設定 requests / limits
- 觀察 pod OOMKilled 與 eviction 差異

### Lab 3：FD leak

- 建立一個故意不關 socket / file 的程式
- 用 `lsof` / `/proc/<pid>/fd` 觀察 fd 數量
- 調整 `ulimit -n`
- 記錄服務失敗模式

### Lab 4：TCP connection 還在但 request timeout

- 建立 client / server 測試
- 模擬 server slow response
- 觀察 `ss -tanp`、TCP state、socket queue
- 對照 HTTP / gRPC timeout 設定

### Lab 5：conntrack table 滿

- 觀察 `nf_conntrack` 相關參數
- 用大量短連線模擬 conntrack 壓力
- 觀察 NAT / Kubernetes Service 可能受到的影響
- 整理排錯順序

## 產出格式

每個 lab 都要留下：

```text
問題情境
實驗拓樸
操作指令
觀察指標
失敗模式
排錯順序
Kubernetes / Cloud 對照
面試說法
```

## 與其他 repo 的分工

| 內容 | 放哪裡 |
|---|---|
| Linux internals 概念筆記 | `tech-stack-learning/operating-systems/` |
| 實際 homelab 排錯紀錄 | `devops-homelab/system-performance/` 或對應 logs |
| Kubernetes resource behavior | `devops-homelab/kubernetes/` |
| 對外 portfolio 敘事 | `devops-homelab/projects/secure-finops-k8s-platform/` |

