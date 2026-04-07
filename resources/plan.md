# 📚 PDF 轉錄計畫 (PDF-to-Markdown Conversion Plan)

> 參考 HVAC 專案 SOP，建立可擴展的書籍轉錄系統
> 
> **目標**：將技術書籍 PDF → 結構化 Markdown 筆記，支援快速查閱與主題精提

---

## 📋 計畫概述

### 目標資料結構
```
tech-stack-learning/
  resources/
    ├── books.md          # 書籍總索引 (維護中)
    ├── plan.md           # 本文件：轉錄計畫與進度
    ├── *.pdf             # 原始 PDF 檔案
    └── books-notes/
        ├── raw/          # 預清洗的原始轉錄（逐章節）
        │   ├── aws-solutions-architects/
        │   ├── python-aws-cookbook/
        │   ├── k8s-security/
        │   └── ...
        └── refined/      # 主題式精提統整 (可選但推薦)
            ├── AWS架構設計核心概念.md
            ├── Kubernetes安全實踐.md
            └── ...
```

### 核心原則

| 原則 | 說明 |
|------|------|
| **raw 層** | 逐字逐句原始轉錄 → 供日後精提之用 |
| **refined 層** | 主題聚集、交叉索引 → 實戰快速參考 |
| **頁數限制** | 每批轉錄 ≤ 20 頁（避免 token 爆炸） |
| **大小限制** | 單個 .md 檔預估 ≤ 50KB（拆段） |
| **驗證** | 轉錄完成後用 `wc -l` 驗證行數合理 |

---

## 🔧 轉錄執行 SOP

### 第一階段：預清洗 + 結構化提取

#### Step 1️⃣ - PyPDF2 預清洗
```bash
# 安裝依賴
pip install PyPDF2

# 提取文字（每批 ≤ 20 頁）
# 腳本應存放於 tools/ 目錄
bash extract-pdf.sh <pdf_path> <output_dir> --batch-size 20
```

**輸出格式**：
```
output/
  ├── chapter-01-pages-1-20.txt
  ├── chapter-02-pages-21-40.txt
  └── ...
```

#### Step 2️⃣ - AI 結構化轉換
- 注入 Markdown 標題層級 (H1/H2/H3)
- 公式轉 LaTeX 格式 (`$$...$$`)
- 表格轉 Markdown table
- 圖片用佔位符標註：`[圖：chapter-02-page-25.png]`
- 程式碼區塊用語言標籤

#### Step 3️⃣ - 輸出與驗證
```bash
# 驗證行數合理性
wc -l output/*.md

# 預期結果：單檔 < 2000 行
```

### 第二階段：主題精提（可選但推薦）

**何時執行**：raw 層轉錄完成後
**方式**：在 `refined/` 層按主題重新組織，加上交叉索引

**範例**：
```
raw/aws-solutions-architects/
  ├── chapter-01-core-concepts.md
  ├── chapter-02-vpc.md
  ├── chapter-03-security.md
  └── ...
        ↓
refined/
  ├── AWS架構設計核心概念.md (整合 ch1-5)
  ├── AWS網路與安全架構.md (整合 ch2-3-7)
  └── AWS成本優化.md (整合 ch8-9)
```

---

## 📊 進度追蹤表

> 格式說明：
> - ⬜ 待轉錄
> - 🟨 進行中
> - ✅ raw 層完成
> - 🎯 refined 層完成（可選）

### AWS / Cloud

| 書名 | 作者 | 頁數 | 狀態 | 完成日期 | 備註 |
|------|------|------|------|---------|------|
| Solutions Architect's Handbook (2nd Ed.) | Shrivastava et al. | ~500 | ⬜ | - | 優先級 ⭐⭐⭐ |
| AWS for Solutions Architects (2nd Ed.) | Shrivastava et al. | ~450 | ⬜ | - | 優先級 ⭐⭐⭐ |
| Python and AWS Cookbook | Mitchell Model | ~300 | ⬜ | - | 優先級 ⭐⭐⭐ |
| Automated FinOps for Cloud | | ~250 | ⬜ | - | 優先級 ⭐⭐ |

### Kubernetes / Container

| 書名 | 作者 | 頁數 | 狀態 | 完成日期 | 備註 |
|------|------|------|------|---------|------|
| Cloud Native DevOps with Kubernetes | Arundel & Domingus | ~400 | ⬜ | - | 優先級 ⭐⭐⭐ |
| Learn Kubernetes Security | Tom Scaria | ~350 | ⬜ | - | 優先級 ⭐⭐⭐ |

### CI/CD & DevOps

| 書名 | 作者 | 頁數 | 狀態 | 完成日期 | 備註 |
|------|------|------|------|---------|------|
| GitOps (Jenkins X / Flux) | Walter Lee | ~200 | ⬜ | - | 優先級 ⭐⭐ |

### 文化 & 組織

| 書名 | 作者 | 頁數 | 狀態 | 完成日期 | 備註 |
|------|------|------|------|---------|------|
| The Phoenix Project | Kim et al. | ~400 | ⬜ | - | 優先級 ⭐ (故事梗概+核心洞察) |

---

## 🚀 執行計畫

### Phase 1（基礎架構建立）
- [ ] 建立 `books-notes/raw/` 和 `refined/` 目錄結構
- [ ] 編寫 `extract-pdf.sh` PyPDF2 預清洗腳本
- [ ] 建立 Markdown 標準化範本
- [ ] 建立驗證檢查清單

### Phase 2（核心書籍優先）
- [ ] Solutions Architect's Handbook - 第 1-3 章（試驗流程）
- [ ] Learn Kubernetes Security - 第 1-2 章（平行進行）

### Phase 3（擴展轉錄）
- [ ] 完成 Solutions Architect's Handbook 全冊
- [ ] 完成 Learn Kubernetes Security 全冊
- [ ] Cloud Native DevOps with Kubernetes

### Phase 4（補充書籍）
- [ ] Python and AWS Cookbook
- [ ] Automated FinOps for Cloud
- [ ] GitOps

### Phase 5（主題精提 - 可選）
- [ ] 建立 refined 層交叉索引
- [ ] 按主題重組筆記
- [ ] 新增導覽頁面

---

## 📝 新增書籍流程

當有新書加入時：

1. **更新 `books.md`**：在適當類別新增行
   ```markdown
   | 新書名 | 作者 | ✅ 已入手 |
   ```

2. **在 plan.md 進度表新增行**：
   ```markdown
   | 新書名 | 作者 | ~XXX | ⬜ | - | 優先級 ⭐⭐ |
   ```

3. **建立對應目錄**（轉錄時）：
   ```bash
   mkdir -p books-notes/raw/new-book-slug/
   ```

4. **按 SOP 轉錄**：上述第一階段的 Step 1-3

---

## 🛠️ 工具和資源

### 依賴
- Python 3.8+
- PyPDF2 (PDF 文字提取)

### 腳本待編寫
| 腳本 | 位置 | 用途 |
|------|------|------|
| `extract-pdf.sh` | `tools/` | PyPDF2 批量預清洗 |
| `validate-markdown.sh` | `tools/` | 驗證轉錄品質 |

### 參考文檔
- CLAUDE.md - `pdf-reader.md` skill SOP
- HVAC 專案結構 - 主題層級化參考

---

## 📌 進度更新日誌

| 日期 | 事項 | 狀態 |
|------|------|------|
| 2026-04-05 | 建立計畫文檔 plan.md | ✅ |
| - | Phase 1 架構建立 | ⬜ |
| - | Phase 2 試驗轉錄 | ⬜ |

---

## 💡 備註

- 本計畫可逐步擴展，新書籍可隨時加入
- raw 層優先完成，refined 層為可選加值
- 建議定期審視進度，調整優先級
- 轉錄結果應納入 git 版本控制 (除大於 50MB 的檔案)

