# 07 - The Phoenix Project

## 目標

以最小成本把 `The Phoenix Project` 轉成可複習、可面試、可拿來對照 `Accelerate` 的案例型筆記。

## 策略

- 這本書採用「輕量整理模式」，不要像技術書一樣逐章完整 raw 轉錄。
- 優先保留故事主線、角色映射、問題演進、管理與 DevOps 核心洞察。
- 輸出重點是「可引用的案例筆記」，不是小說全文重建。

## 目標輸出

- `books-notes/raw/phoenix-project/00-story-outline.md`
- `books-notes/raw/phoenix-project/01-characters-and-system-map.md`
- `books-notes/raw/phoenix-project/02-bottlenecks-and-failures.md`
- `books-notes/refined/phoenix-project-core-lessons.md`
- `books-notes/refined/phoenix-project-interview-cheatsheet.md`

## 工作流

### Step 0 - 掃描結構

- [ ] 掃描 PDF 目錄與 Part / Chapter 邊界
- [ ] 確認是否為文字型 PDF
- [ ] 決定要用「章節群組」還是「Part 群組」切段

### Step 1 - 建立故事骨架

- [ ] `00-story-outline.md`

內容至少包含：

- Bill Palmer 的角色弧線
- 公司主線危機時間線
- 三個工作流（開發、維運、業務）衝突點
- Brent 作為 bottleneck 的象徵意義

### Step 2 - 建立角色與系統地圖

- [ ] `01-characters-and-system-map.md`

內容至少包含：

- 主要角色與對應職能
- 各團隊互相依賴關係
- 核心系統 / 專案 / 事故脈絡
- 哪些衝突是流程問題、哪些是組織設計問題

### Step 3 - 建立失敗模式與瓶頸清單

- [ ] `02-bottlenecks-and-failures.md`

內容至少包含：

- Phoenix 專案問題
- 過載、上下文切換、未控 WIP
- 變更失敗、交付延遲、溝通失真
- 可對照 `Accelerate` / DORA 的指標與能力

### Step 4 - refined 主題整理

- [ ] `books-notes/refined/phoenix-project-core-lessons.md`
- [ ] `books-notes/refined/phoenix-project-interview-cheatsheet.md`

`core-lessons` 建議主題：

- The Three Ways
- Bottleneck management
- Flow efficiency vs local optimization
- Change management and deployment discipline
- Leadership and organizational learning

`interview-cheatsheet` 建議主題：

- 怎麼用故事解釋 DevOps
- 怎麼用 Brent 講 bottleneck
- 怎麼把 Phoenix Project 對應到真實團隊問題
- 怎麼把小說案例連回 `Accelerate`

## 可平行拆分

- 軌道 A：故事骨架與時間線
- 軌道 B：角色 / 團隊 / 系統映射
- 軌道 C：瓶頸 / 事故 / 反模式整理
- 軌道 D：refined 與面試 cheat sheet

## 完成定義

- 不需要完整逐章 raw，也能快速回想全書
- 至少有一份可直接拿去面試或寫文章的總結
- 能和 `Accelerate`、平台工程、DevOps 文化主題互相連結

## 備註

- 如果後續發現這本書的章節結構很適合細拆，再補成更細的 raw lane 即可。
- 初版先追求高訊號，不追求全文覆蓋率。
