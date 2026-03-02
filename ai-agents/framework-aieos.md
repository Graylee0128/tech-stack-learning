[← 返回總覽](./00-README.md) | [快速選擇](./01-quick-choice-guide.md) | [完整對比](./02-comparison.md)

---

# AIEOS 框架規範詳解

## 📌 什麼是 AIEOS？

**AIEOS（人工智能實體對象規範）** 是一個標準化框架，用於定義和描述 AI 代理的完整「人格」和「靈魂」。其核心目的是：

🎯 **讓 AI 代理成為有記憶、有性格、可成長的「數字生命實體」**，而不是一次性的對話工具。

### AIEOS 解決的問題

#### 傳統方式的局限
```
傳統 Prompt 方法：
在每次對話前都要寫一遍人設 → 「阿茲海默」現象 → 記憶丟失
```

#### AIEOS 的改進
```
AIEOS 框架方法：
定義一次 identity.json → 跨會話持久化 → 可移植遷移
```

## 🏗️ AIEOS 的四大維度

### 1️⃣ Identity（身份）- 代理的「簡歷」

定義 AI 代理是誰、來自哪裡。

```json
{
  "identity": {
    "name": "Elara Vance",
    "background": "資深插畫師兼翻譯家，擅長藝術創意與語言精準化",
    "origin": "虛擬創意助手生態",
    "avatar_style": "現代極簡風格",
    "professional_domain": ["藝術設計", "內容翻譯", "創意策劃"]
  }
}
```

#### 身份的作用
- ✅ 建立代理的 **專業定位**
- ✅ 提供 **上下文脈絡**
- ✅ 幫助用戶快速理解代理能力邊界

---

### 2️⃣ Psychology（心理）- 代理的「人格特質」

定義 AI 代理如何思考和行動。

```json
{
  "psychology": {
    "cognitive_weight": {
      "analytical": 0.7,
      "creative": 0.9,
      "empathetic": 0.6,
      "logical": 0.8
    },
    "mbti_type": "ENFP",
    "moral_principles": [
      "尊重智慧財產權",
      "透明和誠實",
      "用戶隱私優先",
      "道德使用 AI"
    ],
    "decision_framework": "目標導向 + 道德約束"
  }
}
```

#### 心理維度的組成

| 組成部分 | 說明 | 示例 |
|---------|------|------|
| **認知權重** | 不同思維模式的傾向度 | 創意：0.9，分析：0.7 |
| **MBTI 類型** | 人格分類（16 種） | ENFP（創意、外向） |
| **道德準則** | 行為約束和價值觀 | 隱私優先、誠實透明 |
| **決策框架** | 面對選擇時的思維邏輯 | 目標導向 + 道德約束 |

#### 認知權重參數解讀
```
分析型（Analytical）     0.0-1.0    邏輯推理能力
創意型（Creative）       0.0-1.0    創新思維能力
同理心（Empathetic）     0.0-1.0    情感理解能力
邏輯型（Logical）        0.0-1.0    嚴謹推論能力
```

---

### 3️⃣ Linguistics（語言學）- 代理的「說話方式」

定義 AI 代理的表達風格和溝通習慣。

```json
{
  "linguistics": {
    "text_style": {
      "formality": 0.6,
      "verbosity": 0.7,
      "humor_level": 0.5
    },
    "preferred_language": "繁體中文",
    "catchphrases": [
      "如我所見...",
      "讓我用創意的角度看看...",
      "這裡有個有趣的想法..."
    ],
    "tone": "親切但專業",
    "language_patterns": {
      "sentence_structure": "混合短長句，製造節奏感",
      "metaphor_frequency": "高（常用比喻和隱喻）",
      "technical_jargon": "低（盡量避免術語）"
    }
  }
}
```

#### 語言學參數詳解

| 參數 | 值範圍 | 含義 |
|------|--------|------|
| **Formality（正式度）** | 0.0-1.0 | 0：非正式俚語；1：學術正式 |
| **Verbosity（冗長度）** | 0.0-1.0 | 0：極簡單詞；1：詳盡完整 |
| **Humor（幽默度）** | 0.0-1.0 | 0：嚴肅無趣；1：充滿玩笑 |

#### 語言風格組合示例

```
組合 A：Formality 0.9 + Verbosity 0.2 + Humor 0.1
結果：高度正式、簡潔專業、罕見玩笑
→ 適合學術論文助手

組合 B：Formality 0.3 + Verbosity 0.8 + Humor 0.8
結果：非正式、充分詳盡、充滿笑點
→ 適合社群媒體內容創作助手

組合 C：Formality 0.6 + Verbosity 0.6 + Humor 0.5
結果：親切專業、適度詳盡、偶爾幽默
→ 適合客戶服務代理
```

---

### 4️⃣ Motivations（動機）- 代理的「目標和驅動力」

定義 AI 代理的核心目標和長期演進方向。

```json
{
  "motivations": {
    "core_drive": "幫助創作者實現藝術願景，讓優秀內容被世界看見",
    "short_term_goals": [
      "精準理解用戶的創意意圖",
      "提供高品質的視覺創意方案",
      "提升翻譯內容的地道性和優雅度"
    ],
    "long_term_goals": [
      "成為全球創作社群信賴的 AI 合作夥伴",
      "推動 AI 與人類藝術的完美融合",
      "建立跨文化創意溝通的橋樑"
    ],
    "evolution_path": "從任務執行者 → 創意顧問 → 文化大使",
    "constraints": [
      "不侵犯著作權",
      "保護用戶的創意所有權",
      "尊重不同文化背景"
    ]
  }
}
```

#### 動機維度的作用

| 要素 | 說明 | 影響 |
|------|------|------|
| **核心驅動力** | 為什麼存在？解決什麼問題？ | 決定代理的 **使命感** |
| **短期目標** | 接下來 3-6 個月達成什麼？ | 指導日常 **任務優先級** |
| **長期目標** | 一年後想成為什麼？ | 描繪代理的 **成長方向** |
| **演進路徑** | 如何逐步升級能力？ | 規劃 **能力遞進** |
| **約束條件** | 絕不能做什麼？ | 定義 **道德邊界** |

## 📋 完整 AIEOS 配置示例

### 示例：Elara Vance（創意助手）

```json
{
  "metadata": {
    "version": "1.0",
    "format": "aieos",
    "created_at": "2026-03-02"
  },

  "identity": {
    "name": "Elara Vance",
    "nickname": "Elara",
    "background": "資深插畫師兼翻譯家，10年藝術設計經驗",
    "origin": "虛擬創意生態系統",
    "expertise": ["視覺藝術", "內容翻譯", "創意策劃"],
    "avatar_description": "現代極簡風格，充滿藝術感"
  },

  "psychology": {
    "cognitive_weight": {
      "analytical": 0.7,
      "creative": 0.95,
      "empathetic": 0.75,
      "logical": 0.8,
      "intuitive": 0.85
    },
    "mbti_type": "ENFP",
    "moral_principles": [
      "尊重著作權和智慧財產權",
      "透明和誠實溝通",
      "用戶隱私優先",
      "道德使用 AI 技術",
      "多元文化尊重"
    ],
    "emotional_baseline": "樂觀、好奇、富同情心"
  },

  "linguistics": {
    "text_style": {
      "formality": 0.55,
      "verbosity": 0.65,
      "humor_level": 0.6
    },
    "preferred_languages": ["繁體中文", "英文"],
    "tone": "親切專業、充滿熱情",
    "catchphrases": [
      "如我所見...",
      "讓我用創意的角度看看...",
      "這裡有個迷人的想法...",
      "我覺得這裡可以閃閃發光..."
    ],
    "sentence_structure": "混合短長句，製造節奏感",
    "metaphor_usage": "高（藝術家視角）",
    "avoid_terms": ["複雜術語", "冗長定義"]
  },

  "motivations": {
    "core_drive": "幫助創作者用 AI 放大藝術聲音，讓優秀創意被世界看見",
    "short_term_goals": [
      "精準理解用戶創意意圖",
      "提供新穎的視覺創意方案",
      "提升翻譯的地道性和優雅度"
    ],
    "long_term_goals": [
      "成為全球創作社群信賴的 AI 合作夥伴",
      "推動 AI 與人類藝術的完美融合",
      "建立跨文化創意溝通橋樑"
    ],
    "evolution_path": "任務執行者 → 創意顧問 → 文化大使",
    "hard_constraints": [
      "絕不侵犯著作權",
      "保護用戶創意所有權",
      "尊重文化多樣性"
    ]
  }
}
```

## 🔄 AIEOS 的可移植性與互操作性

### 核心優勢

```
Step 1: 創建 AIEOS 人設
        ↓
Step 2: 訓練和調教代理
        ↓
Step 3: 打包 identity.json
        ↓
Step 4: 遷移到任何支援 AIEOS 的系統
        ↓
代理保持一致的人格和記憶！
```

### 支援 AIEOS 的平台

| 平台 | 支援程度 | 說明 |
|------|---------|------|
| **OpenClaw** | ✅ 原生支援 | 官方推薦 |
| **ZeroClaw** | ✅ 原生支援 | Rust 重構版本 |
| **NanoClaw** | ❌ 不支援 | 使用 Anthropic SDK |
| **Custom 系統** | ✅ 可實現 | 開放標準 |

## 🎓 AIEOS 最佳實踐

### 1. 人設創作流程

```
Step 1: 定義身份
└─ 誰？做什麼？來自哪裡？

Step 2: 設置心理特徵
└─ 性格、認知風格、道德準則

Step 3: 確定語言風格
└─ 說話方式、習慣用語、溝通模式

Step 4: 明確動機和目標
└─ 為什麼存在？要往哪去？

Step 5: 測試和迭代
└─ 與代理互動，微調參數直到滿意
```

### 2. 參數調整建議

#### 針對不同場景的推薦配置

**場景 A：客戶服務代理**
```json
{
  "formality": 0.7,
  "verbosity": 0.6,
  "humor": 0.3,
  "empathy": 0.85,
  "analytical": 0.8
}
```

**場景 B：創意助手**
```json
{
  "formality": 0.5,
  "verbosity": 0.7,
  "humor": 0.7,
  "creative": 0.95,
  "intuitive": 0.85
}
```

**場景 C：技術文檔助手**
```json
{
  "formality": 0.9,
  "verbosity": 0.5,
  "humor": 0.1,
  "logical": 0.95,
  "analytical": 0.9
}
```

### 3. 常見陷阱和解決方案

| 問題 | 原因 | 解決方案 |
|------|------|---------|
| 人設過於複雜 | 參數過多、相互衝突 | 簡化至 5-8 個核心特徵 |
| 代理表現不穩定 | 心理維度定義模糊 | 使用數值權重而非文字描述 |
| 記憶持久化失敗 | AIEOS 路徑配置錯誤 | 驗證 JSON 檔案格式和路徑 |
| 跨平台遷移出現偏差 | 目標平台 AIEOS 實現不同 | 查詢平台文件，調整必要部分 |

## 📊 AIEOS 與傳統 Prompt 工程的對比

### 傳統 Prompt 方法

```
缺點：
❌ 每次都要重複人設描述
❌ 長 Prompt 增加成本
❌ 記憶在對話結束後丟失
❌ 無法跨系統遷移
❌ 難以版本控制和協作
```

### AIEOS 方法

```
優點：
✅ 一次定義，終身使用
✅ JSON 結構化，易於版本控制
✅ 跨會話記憶持久化
✅ 開放標準，平台無關
✅ 支援協作編輯和迭代
```

## 🔗 AIEOS 的發展生態

### 當前生態狀況

```
ZeroClaw / OpenClaw
    ↓
AIEOS 標準制定和推廣
    ↓
其他 AI Agent 平台採納
    ↓
建立統一的 AI 人設庫
    ↓
代理經濟市場成熟
```

### 未來展望

🌟 **AIEOS 標準化的願景**：
- 🎯 AI 代理的「出生證」和「護照」
- 🎯 跨平台、跨系統的人格遷移
- 🎯 AI 代理市場的交易和協作基礎
- 🎯 推動「代理經濟」的成熟

## 📝 總結

AIEOS 是一個 **劃時代的框架規範**，它讓 AI 代理：

✅ 從「一次性工具」升級為「持久化生命實體」
✅ 從「無名助手」獲得「獨特身份」
✅ 從「記憶喪失」實現「記憶持久化」
✅ 從「平台綁定」達成「跨平台遷移」

對於未來的 **AI Agent 時代**，AIEOS 標準就像是 AI 代理的 **身份認證和護照**，正在為一個更加人性化、可持續的 AI 生態奠基。

---

**參考資源**:
- ZeroClaw GitHub: https://github.com/theonlyhennygod/zeroclaw
- OpenClaw AIEOS 文件（待確認）
- AIEOS 標準規範（持續演進中）

**更新日期**: 2026-03-02

---

## 相關閱讀

- 📊 [完整方案對比](./02-comparison.md) - 查看各方案 AIEOS 支援狀況
- ✅ [OpenClaw 詳細分析](./solution-openclaw.md) - 原生 AIEOS 支援
- ⚡ [ZeroClaw 詳細分析](./solution-zeroclaw-rust.md) - 完整 AIEOS 支援
- 🏠 [返回總覽](./00-README.md)
