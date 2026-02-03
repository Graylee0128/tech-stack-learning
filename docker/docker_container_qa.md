# Docker & 容器化架構 Q&A

> 整理自 2025-02-03 關於官網上雲 PoC 的討論

---

## Q1: 為什麼需要 Docker？Git 版本控制不就夠了嗎？

### A: Git 和 Docker 解決的是不同層面的問題

```
Git 版本控制：記錄源代碼歷史
├─ ✅ 記錄：app.py, requirements.txt 改了什麼
├─ ❌ 不記錄：Python 版本、系統庫版本
└─ 結果：同一個 git commit，不同電腦運行結果可能不同

Docker 版本控制：打包完整運行環境
├─ ✅ 記錄：OS + 系統庫 + Python + 依賴 + 代碼
├─ ✅ 完全隔離：環境不受宿主機影響
└─ 結果：同一個鏡像，任何地方運行結果完全相同
```

### 真實問題場景

```
小王電腦：Ubuntu 20.04 + Python 3.9 + Flask 2.3.0
小李電腦：Ubuntu 18.04 + Python 3.8 + Flask 2.0.0
EC2 服務器：Amazon Linux 2 + Python 3.7 + 混亂的依賴

三人 git pull 同一個 commit
┌─────────────────────────────────────┐
│ 結果：                              │
│ 小王：✅ 正常運行                    │
│ 小李：❌ ImportError (Flask API)      │
│ 服務器：❌ Segmentation Fault         │
└─────────────────────────────────────┘

用 Docker：
在 ubuntu:20.04 容器中構建一次
三人都運行同一個鏡像
┌─────────────────────────────────────┐
│ 結果：                              │
│ 小王：✅ 完全相同的環境              │
│ 小李：✅ 完全相同的環境              │
│ 服務器：✅ 完全相同的環境            │
└─────────────────────────────────────┘
```

---

## Q2: IaC (Terraform) 和 Docker 什麼關係？

### A: 兩者管理不同層級

```
Terraform (Infrastructure as Code)
────────────────────────────────
責任：創建和配置基礎設施
├─ EC2 實例
├─ VPC 網絡
├─ RDS 數據庫
├─ Security Groups
└─ IAM 角色

頻率：很少更新（可能每月幾次）
改動：基礎設施變化時 → terraform apply

Docker (Application Deployment)
────────────────────────────────
責任：打包和運行應用代碼
├─ 應用代碼
├─ 依賴版本
├─ 運行環境
└─ 配置

頻率：很頻繁（每天多次）
改動：應用更新時 → docker build & push
```

### 不應該這樣做

```
❌ 錯誤做法：用 Terraform 部署每次應用更新
terraform apply (改 user_data script)
  ↓ EC2 重啟（可能停機！）
  ↓ 重新安裝依賴（很慢）
  ↓ 應用更新（低效）

✅ 正確做法：Terraform 只改基礎設施
git push → Docker build → Docker push → EC2 拉新鏡像
  ↓ EC2 不需重啟
  ↓ 容器快速替換（秒級）
  ↓ 應用無縫更新
```

---

## Q3: CloudFront 是必需嗎？

### A: 不是必需，是可選擴展

```
基礎設置（必需）：
S3 靜態文件 → CloudFront 緩存分發
                       ↓
                   用戶瀏覽器

最小化配置（可選 CloudFront）：
S3 靜態文件 → 直接返回給用戶
                ↓
            延遲略高，但可用

加入 CloudFront 的優勢：
✅ 邊緣節點緩存（更快）
✅ 自動 GZIP 壓縮
✅ DDoS 防護
❌ 額外成本 $8.50/月 (100GB)

POC 階段建議：先不加，測試通過後再考慮
```

---

## Q4: 不同編程語言對容器化的影響

### A: 語言影響依賴地獄的嚴重程度

```
語言排名：依賴問題嚴重程度

🔴 最嚴重：Python, Node.js
   └─ 原因：
      • Python pip：版本衝突常見，易陷入依賴地獄
        └─ 例：numpy 版本 A 需要 Python 3.9，但項目用 3.8
      • Node.js npm：node_modules 地獄（層級深、冗餘多）
        └─ 例：一個小項目的 node_modules 可能 150+ MB，487 個包
   └─ Docker 必要性：⭐⭐⭐⭐ 強烈建議

🟡 中等：Java
   └─ 原因：
      • JAR 版本衝突
      • JVM 配置複雜
      • ClassLoader 運行時才暴露問題
   └─ Docker 必要性：⭐⭐⭐ 建議

🟢 較輕：Go, Rust
   └─ 原因：
      • Go mod 依賴管理相對好
      • Rust 編譯時檢查嚴格，版本衝突編譯時就發現
      • 兩者都是單二進制輸出
   └─ Docker 必要性：⭐⭐ 可選
```

### Python 依賴問題的深層原因

```
Python 特別容易出問題的原因：

1. 宽松的版本管理
   pip install Flask       ← 沒指定版本，裝最新
   pip install Flask==2.0  ← 需要手動指定

2. 虛擬環境易被忽視
   很多人直接 pip install 到全局 Python
   └─ 不同項目互相污染
   └─ 新電腦又要重新裝一遍

3. 系統 Python vs 用戶 Python 混亂
   /usr/bin/python3        ← 系統自帶
   ~/miniconda3/python3    ← 用戶安裝
   └─ 裝包裝到哪個環境了？不知道

4. C 擴展編譯問題
   numpy, scipy, pandas 都需要編譯
   └─ 需要：gcc, python-dev, 系統庫
   └─ 依賴鏈極長

結果：
小王電腦用 conda 裝 numpy，自動編譯，環境完美
小李電腦用 pip 裝 numpy，但系統少了 BLAS 庫，編譯失敗

Docker 解決：
在 ubuntu:20.04 基礎鏡像構建一次
所有編譯依賴都在鏡像裡固定了
任何地方跑都是同一個鏡像，100% 相同
```

### Node.js 的 node_modules 地獄

```
package.json 只寫了 3 個頂級依賴：
{
  "express": "^4.18.0",
  "mongoose": "^6.0.0",
  "lodash": "^4.17.0"
}

npm install 後：
ls node_modules | wc -l
# 輸出: 487 個包！

為什麼？
express → 依賴 20 個包
mongoose → 依賴 100 個包
這些包 → 又依賴其他包...

問題：
小王用 npm install (Ubuntu)
  └─ node_modules: 100MB, 結構 A

小李用 npm install (Windows)
  └─ node_modules: 120MB, 結構 B
      └─ 原因：native modules 編譯不同

同一個 package.json，兩個 node_modules 不一樣！

Docker 解決：
npm install 一次 → 完整快照
任何地方 docker run → 相同的 node_modules
```

---

## Q5: Serverless (Lambda) 為什麼不需要 Docker？

### A: AWS 已經為你做了容器化

```
傳統 EC2：需要自己構建容器
代碼 → 自己 docker build → 自己 docker push → 自己管理鏡像版本

Serverless Lambda：AWS 內置容器
代碼 → AWS 自動創建隔離環境 → AWS 自動管理版本

Lambda 的黑箱：
┌─────────────────────────────────────┐
│ 你提交：requirements.txt + app.py     │
├─────────────────────────────────────┤
│ AWS 內部（對你不可見）：              │
│ ├─ 自動選擇 Python 3.9 容器          │
│ ├─ 自動 pip install requirements    │
│ ├─ 自動版本隔離                      │
│ ├─ 自動創建 N 個容器副本             │
│ └─ 自動擴展到 1000+ 容器             │
└─────────────────────────────────────┘
     ↓
   零運維
```

### Lambda 不需要 Docker 的原因

```
✅ 標準情況（99% 的應用）
   └─ Python/Node.js/Java 的標準庫都支持
   └─ 代碼上傳 → AWS 自動打包 → 自動部署
   └─ 無需 Dockerfile

❌ 特殊情況（1% 的應用）
   └─ 需要特殊系統庫（OpenCV、GDAL、ffmpeg）
   └─ 鏡像大小超過 250MB
   └─ 此時：寫 Dockerfile → 推 ECR → Lambda 用自定義鏡像
```

---

## Q6: Docker、ECS、EKS 的區別

### A: 三個不同層級的容器技術

```
Docker：容器運行時（最基礎）
├─ 負責：把應用打包成容器
├─ 學習曲線：⭐⭐ 簡單
├─ 用途：開發、測試、本地運行
└─ 例：docker build, docker run

ECS：AWS 容器編排（中等）
├─ 負責：在 EC2 上運行和管理多個 Docker 容器
├─ 功能：
│  ├─ 自動調度容器到可用 EC2
│  ├─ 自動重啟失敗容器
│  ├─ 負載均衡
│  └─ 滾動更新
├─ 成本：$0.05/小時 ECS 費用 + EC2 費用
├─ 學習曲線：⭐⭐⭐ 中等
└─ 適用：中等規模、想用 AWS 原生工具

EKS：Kubernetes 編排（複雜）
├─ 負責：企業級容器編排
├─ 功能：
│  ├─ ECS 有的都有
│  ├─ 自動伸縮（Pod 級別）
│  ├─ 自我修復（Health check）
│  ├─ 跨雲平台（不只是 AWS）
│  └─ 業界標準（LinkedIn、Netflix 都用）
├─ 成本：$73 EKS 費用 + 3+ EC2 費用（$90+）
├─ 學習曲線：⭐⭐⭐⭐⭐ 很陡
└─ 適用：大規模、複雜應用、多團隊

選擇樹：
你的流量是多少？
  ├─ 自動擴展，不可預測？
  │  └─ → Serverless Lambda（最簡單）
  │
  ├─ 穩定，中等規模 (100K-1M DAU)？
  │  └─ → 傳統 EC2 + ECS（Docker）
  │
  └─ 超大規模，複雜需求 (1M+ DAU)？
     └─ → EKS (Kubernetes)
```

---

## Q7: POC 階段應該用 Docker 嗎？

### A: 取決於你選的編程語言

```
使用 Python/Node.js：
✅ 推薦加入 Docker
   原因：
   • pip/npm 依賴問題最嚴重
   • 多人協作容易出現環境差異
   • POC 階段加入，生產化時已經習慣
   成本：額外 $20/月 + 學習成本 (1-2 天)

使用 Go/Rust：
⭐ 可選 Docker
   原因：
   • 單二進制，依賴問題少
   • 可以直接 SSH 部署二進制
   • 環境差異風險低
   成本：額外 $0 + 無額外學習

使用 Java：
✅ 建議加入 Docker
   原因：
   • JVM 配置複雜
   • Docker 可以簡化環境配置
   成本：額外 $20/月 + 學習成本

總體建議：
┌─────────────────────────────────────┐
│ POC 最簡方案：SSH + Git 直接部署     │
│ ├─ 適用：Python/Node.js, 單人開發   │
│ ├─ 成本：$0 額外費用                  │
│ └─ 風險：環境差異，線上故障機率高   │
│                                      │
│ POC 推薦方案：Docker + ECS           │
│ ├─ 適用：Python/Node.js, 多人團隊    │
│ ├─ 成本：$20/月                      │
│ └─ 益處：環境一致，為生產做準備      │
│                                      │
│ POC 不推薦：EKS/Kubernetes           │
│ ├─ 原因：過度設計，學習曲線太陡     │
│ ├─ 成本：$200+/月                    │
│ └─ 等到：需要超大規模再考慮          │
└─────────────────────────────────────┘
```

---

## Q8: 為什麼所有語言都有依賴地獄？

### A: 這是現代編程的通病

```
根本原因：軟件複雜度爆炸

過去（2000 年代）：
應用 → 可能依賴 5-10 個第三方庫
└─ 簡單，手動管理都行

現在（2020 年代）：
應用 → 依賴 100+ 個第三方庫
  ├─ 這些庫又依賴其他庫...
  ├─ 層級深達 10-20 層
  └─ 每個庫都有自己的版本號
      └─ 版本號方案還不統一
      └─ 有人用 Semver，有人隨意改版本

結果：
version conflict 幾乎不可避免

Docker 不是根本解決方案
而是「冷凍」現狀的方案：
把工作的環境完整快照下來
放到容器裡，避免環境因素影響
```

---

## 總結

```
選型決策矩陣：

                SSH 直接部署    Docker + ECS    Serverless Lambda   EKS
───────────────────────────────────────────────────────────────────────
編程語言        推薦 Go/Rust    推薦 Python/Node  任何語言            任何
團隊規模        1-2 人          3-5 人            1-∞                5+
月度成本        $260            $280             $100               $360+
運維複雜度      ⭐⭐⭐⭐       ⭐⭐⭐          ⭐                ⭐⭐⭐⭐⭐
部署頻率        low             high             high               high
環境一致性      否              是              是                  是
POC 適合性      ✅ 快速         ✅ 推薦          ✅ 最優雅          ❌ 過度設計
生產就緒        否              是              是                  是

最常見的組合：
小項目（<100K DAU）→ Serverless Lambda（最便宜、最省事）
中等項目（100K-1M DAU）→ 傳統 EC2 + Docker + ECS（平衡方案）
大項目（1M+ DAU）→ EKS（完整企業級方案）
```

---

> 更多詳細決策參見：POC_PLAN.md & COST_ANALYSIS.md
