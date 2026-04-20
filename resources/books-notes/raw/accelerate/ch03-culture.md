# Chapter 3: Measuring and Changing Culture

> 來源：Accelerate (Forsgren, Humble, Kim) — Part I: What We Found
> 轉錄日期：2026-04-19

---

## Westrum 組織文化模型

組織文化預測資訊在組織中的流動方式。好的資訊有三個特性：

1. 回答接收者需要的問題
2. 及時
3. 以接收者能有效使用的方式呈現

好的資訊流在高節奏、高後果的環境中至關重要，包括科技組織。

### Table 3.1 — Westrum 的三種組織文化類型

| Pathological (Power-Oriented) | Bureaucratic (Rule-Oriented) | Generative (Performance-Oriented) |
|-------------------------------|-----------------------------|------------------------------------|
| Low cooperation | Modest cooperation | High cooperation |
| Messengers "shot" | Messengers neglected | Messengers trained |
| Responsibilities shirked | Narrow responsibilities | Risks are shared |
| Bridging discouraged | Bridging tolerated | Bridging encouraged |
| Failure leads to scapegoating | Failure leads to justice | Failure leads to inquiry |
| Novelty crushed | Novelty leads to problems | Novelty implemented |

> **核心洞察：** 這個文化定義不僅描述組織行為，還能**預測績效結果（performance outcomes）**。

---

## 衡量文化（Measuring Culture）

三種文化類型形成一個連續光譜（Westrum continuum），適合用 **Likert 量表**衡量。

- Likert 量表：1（Strongly disagree）到 7（Strongly agree）
- 陳述必須措辭強烈，讓受訪者可以明確同意或不同意

### Figure 3.1 — Likert 調查問題

| 問題 |
|------|
| Information is actively sought. |
| Messengers are not punished when they deliver news of failures or other bad news. |
| Responsibilities are shared. |
| Cross-functional collaboration is encouraged and rewarded. |
| Failure causes inquiry. |
| New ideas are welcomed. |
| Failures are treated primarily as opportunities to improve the system. |

### 分析構念（Analyzing Constructs）

在進行任何關聯分析之前，必須先驗證量測工具本身：

- **Discriminant validity（區辨效度）**：確保不相關的項目確實不相關
- **Convergent validity（收斂效度）**：確保應相關的項目確實相關
- **Reliability（信度/內部一致性）**：確保所有人對問題的理解一致

> Westrum construct 已被研究團隊驗證為**同時有效且可靠**。可以在自己的調查中使用。
> 計算方式：每題的 1-7 分取平均值。

---

## 文化如何促進資訊處理

Generative 文化透過三個機制促進資訊處理：

1. **更好的協作與信任** — 跨組織、上下層級的信任度更高
2. **強調使命（mission is primary）** — 個人和部門議題讓位給組織使命；hierarchy 扮演較少角色（level playing field）
3. **更好的決策品質** — 更好的資訊 + 決策更容易逆轉（因為團隊更開放透明）

### 官僚體制不一定是壞的

Mark Schwartz (《The Art of Business Value》)：官僚的目標是透過規則確保公平、消除任意性。

> **Westrum 的 rule-oriented 文化**指的是：遵循規則比達成使命更重要的組織。
> 美國聯邦政府中也有 generative 團隊；新創公司也可能是 pathological。

---

## Westrum 文化能預測什麼？

Westrum 理論：資訊流更好的組織運作更有效。好的文化是以下特質的**代理指標（proxy）**：

1. **信任與合作** — 反映組織內部的協作水準
2. **決策品質** — 更好的資訊、更容易逆轉錯誤決策
3. **人員關懷** — 問題更快被發現和處理

### 研究假說與驗證

假說：文化能預測軟體交付績效和組織績效，並帶來更高的工作滿意度。

**結果：兩個假說都被證實。**

> **Figure 3.2：** Westrum Organizational Culture → Software Delivery Performance + Organizational Performance

### 2016 年受訪者文化分布

- 31% pathological
- 48% bureaucratic
- 21% generative

---

## Westrum 理論對科技組織的啟示

對於面對快速技術和經濟變化的現代組織，**韌性（resilience）和創新能力**缺一不可。

研究證實這兩個特質是相連的 — Westrum 文化同時預測軟體交付績效和組織績效。

### Google 團隊研究

Google 發起兩年研究，200+ 訪談、250+ 屬性、180+ 團隊：

> **"Who is on a team matters less than how the team members interact, structure their work, and view their contributions."**
> — 一切歸結於**團隊動態（team dynamics）**。

### The Delivery Performance Construct

統計驗證發現：四個 DORA 指標中，只有 **lead time、release frequency、time to restore** 三個通過效度和信度測試，形成有效構念。

> Change fail rate 與構念高度相關，但未被納入構念定義中。
> 本書後續提到 "software delivery performance" 時，指的是這三個指標的組合。

---

## 如何處理失敗

- **Pathological 組織**：找到「該被掐死的人」（throat to choke），懲罰或怪罪
- **事實**：複雜適應系統中，事故幾乎不是單一個人的錯，而是多重因素的**湧現行為（emergent behavior）**
- 停在「人為錯誤」的調查不僅不好，而且**危險**
- **Human error 應該是調查的起點，不是終點**
- 目標：改善資訊流，讓人們有更好/更即時的資訊，或更好的工具

---

## 如何改變文化？

### John Shook 的洞察（NUMMI 工廠轉型）

> **"The way to change culture is not to first change how people think, but instead to start by changing how people behave — what they do."** — Shook 2010

改變文化的路徑：**先改變行為，思維自然跟著改變**（而非反過來）。

### 研究驗證

實施 Lean 和 Agile 運動的實踐可以影響文化。

> **Figure 3.3：** Continuous Delivery + Lean Management → Westrum Organizational Culture

**你可以透過實施這些實踐來「做出」更好的文化**，就像在製造業一樣。

---

## 本章重點摘要

1. Westrum 模型將組織文化分為三類：Pathological / Bureaucratic / Generative
2. 使用 **Likert 量表**衡量文化，已驗證為有效且可靠的構念
3. Generative 文化預測更好的**軟體交付績效、組織績效、工作滿意度**
4. Google 團隊研究佐證：**團隊動態 > 個人能力**
5. Delivery Performance 構念 = lead time + release frequency + time to restore（不含 change fail rate）
6. Human error 是調查的**起點**，不是終點
7. **改變文化靠改變行為**（act → think），不是靠改變思維
8. **CD + Lean Management → 驅動 generative 文化**
