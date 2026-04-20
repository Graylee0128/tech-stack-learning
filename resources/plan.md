# PDF 轉錄計畫 (PDF-to-Markdown Conversion Plan)

> 參考 HVAC 專案 SOP，建立可擴展的書籍轉錄系統
>
> 目標：將技術書籍 PDF 轉成結構化 Markdown 筆記，支援快速查閱、主題精提與平行執行

---

## 計畫使用方式

- `plan.md`：保留目標、原則、進度、優先順序與 step 入口
- `plan-steps/*.md`：獨立可執行的工作單位，方便單獨丟給 agent
- `books.md`：書籍總索引與入手狀態

> 如果要省 token，優先只帶 `plan.md` + 單一 `plan-steps/*.md`。

## Step 入口

| 類型 | 檔案 | 用途 |
|------|------|------|
| 共用 SOP | [`plan-steps/00-transcription-sop.md`](./plan-steps/00-transcription-sop.md) | PDF 轉錄的共同流程 |
| 基礎建設 | [`plan-steps/01-foundation.md`](./plan-steps/01-foundation.md) | 目錄、腳本、範本、驗證 |
| Accelerate raw | [`plan-steps/02-accelerate-raw.md`](./plan-steps/02-accelerate-raw.md) | 章節級 raw 轉錄，已拆成可平行 lane |
| Accelerate refined | [`plan-steps/03-accelerate-refined.md`](./plan-steps/03-accelerate-refined.md) | 主題統整與面試整理 |
| 核心技術書 | [`plan-steps/04-core-books.md`](./plan-steps/04-core-books.md) | AWS / K8s 主線書籍 |
| 補充書籍 | [`plan-steps/05-supplementary-books.md`](./plan-steps/05-supplementary-books.md) | 次優先閱讀與轉錄 |
| 跨書精提 | [`plan-steps/06-cross-book-refined.md`](./plan-steps/06-cross-book-refined.md) | refined 層交叉索引 |
| Phoenix Project | [`plan-steps/07-phoenix-project.md`](./plan-steps/07-phoenix-project.md) | 故事型書籍的輕量整理模式 |

## 目標資料結構

```text
tech-stack-learning/
  resources/
    ├── books.md                # 書籍總索引
    ├── plan.md                 # 總覽、進度、入口
    ├── plan-steps/             # 可獨立執行的 steps
    ├── *.pdf                   # 原始 PDF
    └── books-notes/
        ├── raw/                # 逐章節原始轉錄
        └── refined/            # 主題式精提統整
```

## 核心原則

| 原則 | 說明 |
|------|------|
| `raw` 層優先 | 先把原始知識安全落地，再做重組 |
| `refined` 層加值 | 主題聚合、交叉索引、面試可引用 |
| 小批處理 | 每批轉錄不超過 20 頁，避免 token 爆炸 |
| 小檔輸出 | 單檔預估不超過 50KB，必要時拆段 |
| 可驗證 | 轉錄後要做結構與行數檢查 |
| 可並行 | 每個 step file 盡量只代表一條工作流 |

## 當前焦點

1. 先完成 [`plan-steps/01-foundation.md`](./plan-steps/01-foundation.md)，把共用工具補齊。
2. 以 [`plan-steps/02-accelerate-raw.md`](./plan-steps/02-accelerate-raw.md) 跑第一輪完整流程，目前 Lane A 已完成。
3. raw 穩定後，再開 [`plan-steps/03-accelerate-refined.md`](./plan-steps/03-accelerate-refined.md)。

## 📊 進度追蹤表

> 格式說明：
> - ⬜ 待轉錄
> - 🟨 部分完成 / 進行中
> - ✅ raw 層完成
> - 🎯 refined 層完成（可選）

### AWS / Cloud

| 書名 | 作者 | 頁數 | 狀態 | 完成日期 | 備註 |
|------|------|------|------|---------|------|
| Solutions Architect's Handbook (2nd Ed.) | Shrivastava et al. | ~500 | ⬜ | - | 優先級 ⭐⭐⭐ |
| AWS for Solutions Architects (2nd Ed.) | Shrivastava et al. | ~450 | ⬜ | - | 優先級 ⭐⭐⭐ |
| Python and AWS Cookbook | Mitchell Model | ~300 | ⬜ | - | 優先級 ⭐⭐⭐ |
| Automated FinOps for Cloud | - | ~250 | ⬜ | - | 優先級 ⭐⭐ |

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
| **Accelerate** | Forsgren, Humble, Kim | ~288 | 🟨 進行中 | - | 優先級 ⭐⭐⭐ (在讀中，2026-04-19 入手) |
| The Phoenix Project | Kim et al. | ~400 | ⬜ | - | 優先級 ⭐ (故事梗概 + 核心洞察；step 已建立) |
| Team Topologies | Skelton, Pais | ~240 | ⬜ | - | 優先級 ⭐⭐ |
| Platform Strategy | Gregor Hohpe | ~200 | ⬜ | - | 優先級 ⭐⭐ |

## 工作流摘要

| Workstream | 目標 | 狀態 | 目前進度 | Step |
|------------|------|------|----------|------|
| Foundation | 建立共同工具與目錄 | 🟨 | `raw/`、`refined/` 目錄已就緒；腳本/模板/checklist 待補 | [`01-foundation`](./plan-steps/01-foundation.md) |
| Accelerate raw | 跑第一輪逐章轉錄 | 🟨 | 已完成 `ch00-ch04`，目前 `5/18` | [`02-accelerate-raw`](./plan-steps/02-accelerate-raw.md) |
| Accelerate refined | 產出主題摘要與面試版 | ⬜ | 尚未開始 | [`03-accelerate-refined`](./plan-steps/03-accelerate-refined.md) |
| Core books | AWS / K8s 主線書籍 | ⬜ | 尚未開始 | [`04-core-books`](./plan-steps/04-core-books.md) |
| Supplementary books | 補充書籍 | ⬜ | 尚未開始 | [`05-supplementary-books`](./plan-steps/05-supplementary-books.md) |
| Cross-book refined | 跨書索引與導覽 | ⬜ | 尚未開始 | [`06-cross-book-refined`](./plan-steps/06-cross-book-refined.md) |
| Phoenix Project | 輕量整理故事案例書 | 🟨 | 獨立 step 與模板檔已建立，等待填內容 | [`07-phoenix-project`](./plan-steps/07-phoenix-project.md) |

## 新增書籍流程

1. 更新 [`books.md`](./books.md) 的書籍索引。
2. 在本檔進度表新增一行。
3. 需要開始轉錄時，建立 `books-notes/raw/<book-slug>/`。
4. 執行 [`plan-steps/00-transcription-sop.md`](./plan-steps/00-transcription-sop.md)。
5. 視需求把工作掛進對應的 step file。

## 工具和資源

### 依賴

- Python 3.8+
- PyPDF2

### 腳本待編寫

| 腳本 | 位置 | 用途 |
|------|------|------|
| `extract-pdf.sh` | `tools/` | PyPDF2 批量預清洗 |
| `validate-markdown.sh` | `tools/` | 驗證轉錄品質 |

### 參考文檔

- `CLAUDE.md`
- `pdf-reader.md` skill SOP
- HVAC 專案結構

## 進度更新日誌

| 日期 | 事項 | 狀態 |
|------|------|------|
| 2026-04-05 | 建立計畫文檔 `plan.md` | ✅ |
| 2026-04-19 | 入手 Accelerate PDF，加入進度表，設為 Phase 2 首選試驗書 | ✅ |
| 2026-04-19 | Foundation 工作流：`raw/`、`refined/` 目錄已建立 | 🟨 |
| 2026-04-19 | Accelerate raw 工作流：已完成 `ch00-ch04` | 🟨 |
| 2026-04-19 | 建立 `The Phoenix Project` 獨立 step 與模板檔（輕量整理模式） | 🟨 |
| - | Accelerate refined 工作流 | ⬜ |

## 備註

- `plan.md` 盡量不要再塞長 checklist，避免再次膨脹。
- 需要派工時，直接指定單一 `plan-steps/*.md`。
- `raw` 是基礎層，`refined` 是加值層；優先順序不要反過來。
