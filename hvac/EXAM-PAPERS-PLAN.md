# 歷屆試題收集與整理計畫

> **目標**：100~114 年 冷凍空調工程技師歷屆試題（115年尚未開放）
> **輸出**：`exam-papers/{科目}/{年度}-{科目}.pdf`

---

## 快速下載指令

```bash
# 下載所有未完成年份（自動跳過已存在）
python download-exams.py

# 只下載特定一年
python download-exams.py 112

# 下載某個區間
python download-exams.py 100 109
```

腳本位置：[download-exams.py](download-exams.py)

---

## 各年度考試代碼（已全部確認）

> 類科代碼 `c=009`（冷凍空調工程技師）**全年份固定**

| 年度 | code   | 年度 | code   |
|:----:|:------:|:----:|:------:|
| 100  | 100230 | 108  | 108180 |
| 101  | 101180 | 109  | 109180 |
| 102  | 102180 | 110  | 110180 |
| 103  | 103170 | 111  | 111180 |
| 104  | 104170 | 112  | 112190 |
| 105  | 105170 | 113  | 113190 |
| 106  | 106180 | 114  | 114180 |
| 107  | 107180 | 115  | 尚未開放 |

---

## 已確認科目代碼（113年）

> 科目代碼 `s=` 每年不同，腳本自動查詢，此表供手動驗證參考

| 科目 | 目錄 | 檔名格式 | s= |
|------|------|----------|----|
| 電工學（包括電機機械） | `electrical-engineering/` | `{年度}-electrical-engineering.pdf` | `0604` |
| 熱力學與熱傳學 | `thermodynamics/` | `{年度}-thermodynamics.pdf` | `0609` |
| 流體力學與流體機械 | `fluid-mechanics/` | `{年度}-fluid-mechanics.pdf` | `0612` |
| 冷凍工程與設計 | `refrigeration-engineering/` | `{年度}-refrigeration-engineering.pdf` | `0613` |
| 空調工程與設計 | `air-conditioning-engineering/` | `{年度}-air-conditioning-engineering.pdf` | `0614` |
| 冷凍空調自動控制 | `automatic-control/` | `{年度}-automatic-control.pdf` | `0615` |

**手動下載單科指令模板：**
```bash
# 格式：curl -sk -L "https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?t=Q&code={CODE}&c=009&s={S}&q=1" -o {科目}.pdf
curl -sk -L "https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?t=Q&code=113190&c=009&s=0609&q=1" -o thermodynamics.pdf
```

---

## 下載進度追蹤

| 年度 | 電工學 | 熱力學 | 流力 | 冷凍工程 | 空調工程 | 自動控制 | 完成 |
|:----:|:------:|:------:|:----:|:--------:|:--------:|:--------:|:----:|
| 100 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 101 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 102 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 103 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 104 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 105 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 106 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 107 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 108 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 109 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 110 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 111 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 112 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 113 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 114 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 115 | —  | —  | —  | —  | —  | —  | 尚未開放 |

---

## 解答來源（官方只提供題目）

| 年度 | 來源 | 網址 |
|------|------|------|
| 110~113 | 立功教育文化事業 | https://li-kung.blogspot.com/2024/12/blog-post_12.html |
| 多年度 | CPmarks 解析 | https://cpmarks.com/refrigeration-air-conditioning/ |
| 多年度 | 張世青技師部落格 | 搜尋「冷凍空調技師 解答」 |
