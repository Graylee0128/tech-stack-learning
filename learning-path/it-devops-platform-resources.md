# IT / DevOps / Platform Engineer 學習資源

> 對應職涯路線：Linux SysEng → DevOps Engineer → Platform Engineer

---

## 書籍

### 文化 & 策略（建立視野）

| 書名 | 作者 | 重點 |
|------|------|------|
| **The Phoenix Project** | Kim, Behr, Spafford | DevOps 思維入門，小說形式，最容易讀完的第一本 |
| **Accelerate** | Forsgren, Humble, Kim | 數據驅動，高效能 DevOps 團隊的科學指標，面試答題神器 |
| **Team Topologies** | Skelton, Pais | Platform Engineer 必讀，Team API 概念是 IDP 設計基礎 |
| **Platform Strategy** | Gregor Hohpe | 治理、架構決策、標準化 vs 彈性的平衡 |

### 技術深化

| 書名 | 作者 | 適合時機 |
|------|------|---------|
| **Site Reliability Engineering** | Google | SRE 聖經，[免費線上版](https://sre.google/sre-book/table-of-contents/)，可觀測性/SLO/告警基礎 |
| **Infrastructure as Code** (3rd Ed.) | Kief Morris | Terraform 深度使用者必讀，模式與測試策略 |
| **Kubernetes in Action** (2nd Ed.) | Lukša | K8s 最好的入門深化書，比官方文件好讀 |
| **The Site Reliability Workbook** | Google | SRE Book 的實踐版，有具體 template |

### AWS / Cloud 架構

| 書名 | 作者 | 說明 |
|------|------|------|
| **AWS for Solutions Architects** (2nd Ed.) | Shrivastava et al. | SAP 備考後的實戰架構設計延伸 |
| **AWS Cookbook** | Culkin, Zazon | 70+ 自包含食譜，直接可執行，補強實務缺口 |

---

## GitHub 學習專案

### Roadmap & 路線圖

| 專案 | 說明 |
|------|------|
| [kamranahmedse/developer-roadmap](https://github.com/kamranahmedse/developer-roadmap) | roadmap.sh，DevOps/Platform/Cloud 路線圖（~300k stars） |
| [techiescamp/kubernetes-learning-path](https://github.com/techiescamp/kubernetes-learning-path) | K8s 從零到進階結構化路線 |

### Platform Engineering 實戰

| 專案 | 說明 |
|------|------|
| [wnqueiroz/platform-engineering-backstack](https://github.com/wnqueiroz/platform-engineering-backstack) | **BACK Stack**：Backstage + ArgoCD + Crossplane + Kyverno，一鍵本地實驗 |
| [backstage/backstage](https://github.com/backstage/backstage) | Spotify 開源 IDP 框架，Platform Engineer 核心工具 |
| [crossplane/crossplane](https://github.com/crossplane/crossplane) | K8s-native IaC，Terraform 概念可直接遷移 |

### Kubernetes 動手實作

| 專案 | 說明 |
|------|------|
| [techiescamp/kubernetes-projects](https://github.com/techiescamp/kubernetes-projects) | 實際專案練習 |
| [NotHarshhaa/kubernetes-projects-learning](https://github.com/NotHarshhaa/kubernetes-projects-learning) | 實時場景 K8s 練習集 |
| [saiyam1814/Kubernetes-crash-course-2025](https://github.com/saiyam1814/Kubernetes-crash-course-2025) | 免費 K8s 速成課 2025 版 |

### 系統設計

| 專案 | 說明 |
|------|------|
| [donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer) | 系統設計面試備考（~280k stars） |

---

## 學習優先序

```
現在         →  Accelerate + Team Topologies（建立 Platform 視野）
K8s 深化     →  Kubernetes in Action + techiescamp K8s path
Platform 實作 →  BACK Stack（Backstage + ArgoCD + Crossplane）動手跑起來
AWS 架構     →  AWS Cookbook（補實務缺口）
長期          →  SRE Book + Infrastructure as Code
```

---

## 相關筆記

- [platform-engineering-evolution.md](./platform-engineering-evolution.md) - Platform Engineering 演進
- [telecom-idc-cloud-vs-public-cloud.md](./telecom-idc-cloud-vs-public-cloud.md) - 雲端類型比較
