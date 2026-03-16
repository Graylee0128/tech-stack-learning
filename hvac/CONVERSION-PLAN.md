# PDF to Markdown 轉換計畫

> **書籍**：Refrigeration and Air Conditioning, 2nd Ed. — W.F. Stoecker & J.W. Jones
> **來源**：`resources/Refrigeration_and_Air_Conditioning_2nd_Ed_Stoecker_Jones.pdf`（440 頁）
> **輸出**：`notes/raw/`（階段一原始轉換）→ `notes/refined/`（階段二統整提煉）→ `articles/`（技術文章）
> **策略**：因 PDF 共 440 頁，採**逐章分批處理**，共 21 批次
> **範圍**：僅轉換文字內容；圖片跳過，學習途中自行查詢補充

---

## 批次總覽與檢核表

| 批次 | 輸出檔案 | PDF 頁碼 | 頁數 | 狀態 |
|:----:|----------|:--------:|:----:|:----:|
| 01 | `00-table-of-contents.md` + `ch01-applications.md` | 1-10 | 10 | ✅ 完成（1-1~1-5 掃描缺頁已標註） |
| 02 | `ch02-thermal-principles.md` | 11-37 | 27 | ✅ 完成 |
| 03 | `ch03-psychrometry.md` | 38-56 | 19 | ✅ 完成 |
| 04 | `ch04-heating-cooling-load.md` | 57-85 | 29 | ✅ 完成 |
| 05 | `ch05-air-conditioning-systems.md` | 86-100 | 15 | ⬜ 待執行 |
| 06 | `ch06-fan-duct-systems.md` | 101-125 | 25 | ⬜ 待執行 |
| 07 | `ch07-pumps-piping.md` | 126-142 | 17 | ⬜ 待執行 |
| 08 | `ch08-cooling-dehumidifying-coils.md` | 143-156 | 14 | ⬜ 待執行 |
| 09 | `ch09-air-conditioning-controls.md` | 157-182 | 26 | ⬜ 待執行 |
| 10 | `ch10-vapor-compression-cycle.md` | 183-200 | 18 | ⬜ 待執行 |
| 11 | `ch11-compressors.md` | 201-228 | 28 | ⬜ 待執行 |
| 12 | `ch12-condensers-evaporators.md` | 229-255 | 27 | ⬜ 待執行 |
| 13 | `ch13-expansion-devices.md` | 256-276 | 21 | ⬜ 待執行 |
| 14 | `ch14-system-analysis.md` | 277-291 | 15 | ⬜ 待執行 |
| 15 | `ch15-refrigerants.md` | 292-303 | 12 | ⬜ 待執行 |
| 16 | `ch16-multipressure-systems.md` | 304-323 | 20 | ⬜ 待執行 |
| 17 | `ch17-absorption-refrigeration.md` | 324-346 | 23 | ⬜ 待執行 |
| 18 | `ch18-heat-pumps.md` | 347-360 | 14 | ⬜ 待執行 |
| 19 | `ch19-cooling-towers.md` | 361-375 | 15 | ⬜ 待執行 |
| 20 | `ch20-solar-energy.md` | 376-396 | 21 | ⬜ 待執行 |
| 21 | `ch21-acoustics-noise-control.md` + `appendix-index.md` | 397-440 | 44 | ⬜ 待執行 |

---

## 每批執行流程

```
Step 1: 提取 + 預清洗文字（Python PyPDF2，一步到位）
  └─ ⚠️ 不使用 pdftoppm / Read PDF 工具（環境未安裝 pdftoppm）
  └─ 使用以下 Python 腳本提取並預清洗，減少 AI 端需處理的垃圾 token：

       python -c "
       import PyPDF2, re
       with open(r'<PDF_PATH>', 'rb') as f:
           reader = PyPDF2.PdfReader(f)
           for i in range(<START_0INDEX>, <END_0INDEX>):
               text = reader.pages[i].extract_text()
               lines = text.split('\n')
               # 移除純符號/單字母垃圾行（長度 ≤ 3 且非數字開頭）
               lines = [l for l in lines if len(l.strip()) > 3
                        or re.match(r'^\d', l.strip())]
               # 移除頁碼殘留行（如 '60 REFRIGERATION AND AIR CONDITIONING'）
               lines = [l for l in lines
                        if not re.match(r'^\d+\s+REFRIGERATION', l.strip())]
               # 合併連字號斷行
               cleaned = '\n'.join(lines)
               cleaned = re.sub(r'­\n', '', cleaned)       # soft hyphen + newline
               cleaned = re.sub(r'-\n(?=[a-z])', '', cleaned)  # hyphen + newline before lowercase
               # 修正常見 OCR 空格錯誤
               cleaned = cleaned.replace('HV AC', 'HVAC')
               print(f'=== PAGE {i+1} ===')
               print(cleaned)
       "

  └─ 若輸出超過 60KB（約 25–30 頁），分兩段提取避免截斷

Step 2: AI 結構化轉換
  └─ 經 Step 1 預清洗後，剩餘工作為結構化（不再需要大量手動去噪）：
       • 章節標題 → # Chapter X: Title
       • 小節標題 → ## X-Y Section Title
       • 公式 → LaTeX $...$ 或 $$...$$
       • 表格 → Markdown table（注意 OCR 表格常錯位，需對照原文修正）
       • 圖片 → 跳過，保留 > *[Figure X-X] 描述* 佔位符
       • Example → **Example X-X** ... *Solution* 格式
       • Problems → ## Problems 區塊，保留題號與答案
  └─ ⚠️ 格式已穩定，不需再讀前章作為格式參考

Step 3: 寫入檔案
  └─ 使用 Write 工具寫入對應的 .md 檔案至 hvac/notes/raw/
  └─ 寫入後用 wc -l 驗證行數合理性
```

### 單批完成檢核（每批結束後逐項確認）

- [ ] 檔案已產生且非空
- [ ] 章節標題完整（對照目錄）
- [ ] 小節編號連續無遺漏
- [ ] 無明顯 OCR 殘留亂碼
- [ ] 更新上方檢核表狀態 ⬜ → ✅

---

## 階段一完工檢核

全部 21 批次完成後執行：

- [ ] **檔案完整性**：所有 23 個 .md 檔案已產生（目錄 + 21 章 + 附錄）
- [ ] **行數統計**：`wc -l *.md` 確認各檔案內容量合理
- [ ] **章節連貫性**：Ch1–Ch21 小節編號無跳號、無重複
- [ ] **目錄交叉比對**：`00-table-of-contents.md` 中列出的所有章節都有對應檔案
- [ ] **Markdown 渲染**：VSCode 預覽確認格式正常

---

## 階段二：統整與提煉

> 書籍轉換完成後，將原始章節內容統整、提煉為高質量學習筆記與技術文章。
> 遵循專案「notes → articles」兩層品質分層體系。

### 2-1 統整：主題式學習筆記（→ `notes/`）

將 21 章內容按**主題**重新組織，打破原書章節順序，產出跨章節的統整筆記：

| 主題 | 涵蓋章節 | 輸出檔案 | 狀態 |
|------|----------|----------|:----:|
| 熱力學基礎 | Ch2, Ch10 | `summary-thermodynamics.md` | ⬜ |
| 空氣性質與濕空氣處理 | Ch3, Ch8 | `summary-psychrometry.md` | ⬜ |
| 負荷計算與系統設計 | Ch4, Ch5 | `summary-load-and-systems.md` | ⬜ |
| 風管與水管系統 | Ch6, Ch7 | `summary-distribution.md` | ⬜ |
| 冷凍循環與元件 | Ch10–Ch14 | `summary-refrigeration-cycle.md` | ⬜ |
| 冷媒 | Ch15 | `summary-refrigerants.md` | ⬜ |
| 進階系統 | Ch16–Ch18 | `summary-advanced-systems.md` | ⬜ |
| 冷卻塔與輔助設備 | Ch12, Ch19 | `summary-heat-rejection.md` | ⬜ |
| 控制與噪音 | Ch9, Ch21 | `summary-controls-acoustics.md` | ⬜ |
| 應用與能源 | Ch1, Ch20 | `summary-applications-energy.md` | ⬜ |

> 主題分類為初步規劃，可依學習過程調整合併或拆分。

### 2-2 提煉：技術文章（→ `articles/`）

從統整筆記中萃取，採 **Pillar + Cluster** 策略產出對外發布級內容：

```
hvac/articles/
├── pillar-refrigeration-fundamentals.md    ← 主文：冷凍空調全景概述
├── cluster-vapor-compression.md            ← 子文：蒸氣壓縮循環深度解析
├── cluster-psychrometric-chart.md          ← 子文：濕空氣線圖實務應用
├── cluster-load-calculation.md             ← 子文：冷暖房負荷計算方法
├── cluster-refrigerants.md                 ← 子文：冷媒選用與環保趨勢
└── ...（依學習深度持續擴充）
```

### 2-3 提煉流程

```
notes/raw/ch01~ch21 (階段一：原書逐章轉換)
    │
    ▼
notes/refined/summary-*.md (階段二：主題式統整筆記)
    │
    ▼
articles/pillar-*.md + cluster-*.md (Pillar + Cluster 技術文章)
    │
    ▼
personal-blog/technical-articles/ (對外發布)
```

### 階段二檢核

- [ ] 所有主題統整筆記產出且內容完整
- [ ] 至少 1 篇 Pillar 主文完成
- [ ] 各 Cluster 子文能獨立閱讀，且引導回主文
- [ ] 文章品質達到可對外分享水準

---

## 輸出目錄結構

```
tech-stack-learning/hvac/
├── notes/
│   ├── raw/                                ← 階段一：逐章原始轉換
│   │   ├── 00-table-of-contents.md
│   │   ├── ch01-applications.md
│   │   ├── ch02-thermal-principles.md
│   │   ├── ...
│   │   ├── ch21-acoustics-noise-control.md
│   │   └── appendix-index.md
│   └── refined/                            ← 階段二：主題式統整提煉
│       ├── summary-thermodynamics.md
│       ├── summary-psychrometry.md
│       ├── summary-load-and-systems.md
│       ├── summary-distribution.md
│       ├── summary-refrigeration-cycle.md
│       ├── summary-refrigerants.md
│       ├── summary-advanced-systems.md
│       ├── summary-heat-rejection.md
│       ├── summary-controls-acoustics.md
│       └── summary-applications-energy.md
├── articles/                               ← 階段二：Pillar + Cluster 技術文章
│   ├── pillar-refrigeration-fundamentals.md
│   ├── cluster-vapor-compression.md
│   ├── cluster-psychrometric-chart.md
│   └── ...
├── resources/
│   └── Refrigeration_and_Air_Conditioning_2nd_Ed_Stoecker_Jones.pdf
└── CONVERSION-PLAN.md                      ← 本檔案（執行計畫與進度追蹤）
```

## 備註

- **公式**：掃描 OCR 對數學公式提取品質有限，盡力轉 LaTeX，複雜公式可能需手動修正
- **圖片**：跳過不處理，僅保留 Figure 編號標記，學習時自行查詢補充
- **表格**：盡力轉 Markdown table，複雜表格可能需微調
- **OCR 雜訊**：`.,. .r` `,,. F` 等掃描殘留符號會在轉換時清除
