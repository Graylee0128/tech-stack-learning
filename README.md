# Tech Stack Learning 📚

我的技術棧學習記錄庫。系統性記錄學習過程中的筆記、最佳實踐和實戰項目。

## 📁 目錄結構 - 按質量分層

每個技術主題下分為兩層：
- **`notes/`** - 個人學習筆記、Q&A、備忘錄等
- **`articles/`** - 精打磨發布級別的技術文章

### 技術主題

#### Cloud & Infrastructure
- **AWS 雲服務**
  - [aws/network/](./aws/network/) - AWS 網路服務（VPC、PrivateLink、Direct Connect 等）
    - `notes/` 備考筆記和實驗 | `articles/` 內網、DNS、NAT 等深度文章
  - [aws/security/](./aws/security/) - AWS 安全服務（IAM、KMS 等）
    - `notes/` 安全備考筆記 | `articles/` 安全架構文章
  - [aws/sap/](./aws/sap/) - AWS Solutions Architect Professional 認證
    - `notes/` 備考路線圖 | `articles/` 架構模式分析
  - [aws/articles/](./aws/articles/) - AWS 通用架構文章
    - 跨服務系統架構設計

- **terraform/** - 基礎設施即代碼
  - `notes/` Terraform 速查表和最佳實踐 | `articles/` 設計模式

- **k8s/** - Kubernetes 核心、常用平台生態與 Cluster admin 進階
  - `core/` Kubernetes 核心：`k3s`、`kubectl`、核心物件與基本排錯
  - `ecosystem/` 常用平台生態：Helm、Argo CD、Prometheus、Grafana、cert-manager、Cilium、Velero、Istio
  - `cluster-admin/` 進階主題：`kubeadm`、control plane、cluster bootstrap、CNI / CRI / storage / HA
  - `LEARNING-STRUCTURE.md` 總學習架構與建議順序

#### DevOps & Development
- **cicd/github-actions/** - [GitHub Actions 學習與實踐](./cicd/github-actions/)
  - `notes/` 基礎、速查表、最佳實踐 | `articles/` 深度教學

- **docker/** - 容器化技術
  - `notes/` Docker 基礎和 Q&A | `articles/` 深度教學

- **git/** - 版本控制
  - `notes/` Git 命令和工作流程 Q&A | `articles/` 深度指南

### 其他重要目錄
- **[learning-path/](./learning-path/)** - 學習路線圖和規劃
- **[projects/](./projects/)** - 實戰項目記錄
- **[cheatsheet/](./cheatsheet/)** - 速查表和常用命令

## 🎯 目的

建立一個個人的、系統化的技術棧知識庫，幫助：
- 📖 記錄學習過程（notes/）
- 📝 精打磨技術文章（articles/）
- 🔍 快速查詢已學知識
- 📈 追蹤學習進度
- 🤝 便於未來分享和協作

## 📋 質量分層說明

### Notes（筆記層）
- 學習過程中的原始記錄
- Q&A 形式的知識點整理
- 實驗和研究筆記
- 備忘錄和速查表

### Articles（文章層）
- 從筆記中精心萃取的高質量內容
- 採用「Pillar（主文）+ Cluster（子文）」策略組織
- 適合對外分享和發布
- 持續迭代和改進的內容

## 📝 如何使用

1. **快速查詢** - 進入對應技術主題，查看 `notes/` 中的 Q&A 和筆記
2. **深入學習** - 閱讀 `articles/` 中的精品文章
3. **學習路線** - 查看 `learning-path/` 了解推薦的學習順序
4. **實踐項目** - 參考 `projects/` 下的項目案例
5. **建立筆記** - 在相應技術主題的 `notes/` 目錄中記錄學習過程
6. **提升質量** - 將筆記提煉成 `articles/` 中的精品文章

## 🚀 工作流程

```
學習和實驗
    ↓
在 notes/ 記錄筆記和發現
    ↓
積累足夠的知識深度
    ↓
精心打磨成 articles/ 中的文章
    ↓
發布到個人部落格或分享
```

---

**最後更新：** 2026-02-15
