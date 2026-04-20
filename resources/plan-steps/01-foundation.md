# 01 - Foundation

## 目標

建立所有書籍共用的轉錄底座，避免之後每本書都重新發明流程。

## 目前狀態

- 🟨 部分完成
- 已有 `books-notes/raw/`、`books-notes/refined/` 與 `raw/accelerate/`
- 尚缺共用腳本、Markdown 模板、驗證 checklist

## 產出物

- `books-notes/raw/` 與 `books-notes/refined/` 目錄規範
- `tools/extract-pdf.sh`
- Markdown 標準化範本
- 驗證檢查清單

## 任務清單

- [x] 建立或補齊 `books-notes/raw/` 和 `books-notes/refined/` 目錄結構
- [ ] 編寫 `extract-pdf.sh`，支援每批最多 20 頁
- [ ] 建立 Markdown 範本，統一章節、圖片、表格、程式碼格式
- [ ] 建立驗證 checklist，包含行數、標題層級、缺段檢查

## 可平行拆分

- 軌道 A：目錄與命名規範
- 軌道 B：PDF 預清洗腳本
- 軌道 C：Markdown 模板與驗證 checklist

## 完成定義

- 新書可以直接套同一套流程
- 轉錄不再依賴臨時 prompt
- raw / refined 的輸出格式有一致規範
