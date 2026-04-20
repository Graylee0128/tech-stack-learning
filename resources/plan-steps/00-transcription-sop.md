# 00 - Transcription SOP

## 目標

把單一本書的一個批次或一個章節，從 PDF 轉成可維護的 Markdown raw 筆記。

## 輸入

- PDF 路徑
- 目標輸出目錄
- 頁碼範圍或章節範圍

## 標準輸出

```text
output/
  ├── chapter-01-pages-1-20.txt
  ├── chapter-02-pages-21-40.txt
  └── ...
```

後續整理後輸出為對應的 `.md` 檔。

## 步驟

### 1. 預清洗

- 安裝依賴：`pip install PyPDF2`
- 每批不超過 20 頁
- 腳本預計放在 `tools/`
- 執行形式：

```bash
bash extract-pdf.sh <pdf_path> <output_dir> --batch-size 20
```

### 2. AI 結構化轉換

- 補上 Markdown 標題層級（H1/H2/H3）
- 公式轉成 LaTeX 格式（`$$...$$`）
- 表格轉成 Markdown table
- 圖片用佔位符，例如 `[圖：chapter-02-page-25.png]`
- 程式碼區塊加上語言標籤

### 3. 輸出驗證

- 執行：`wc -l output/*.md`
- 預期：單檔通常小於 2000 行
- 快速檢查是否有明顯漏段、亂序、標題階層錯誤

## 完成定義

- raw 檔已寫入正確目錄
- 結構已可閱讀，不只是純文字堆疊
- 行數與章節切分合理
- 後續 refined 可以直接引用

## 備註

- 如果只是先求可用，先完成 raw，不必同步做 refined。
- 遇到超長章節時，優先拆段，不要硬塞進單一檔案。
