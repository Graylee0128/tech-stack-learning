[← 返回總覽](./00-README.md) | [快速選擇](./01-quick-choice-guide.md) | [完整對比](./02-comparison.md)

---

# AI Agent 本地部署 - 快速選擇指南

> 不想讀那麼多文檔？3 分鐘快速找到最適合你的方案！

## ⚡ 快速決策樹

```
你是誰？
│
├─ 個人開發者、愛好者
│   └─ 用什麼硬體？
│       ├─ 樹莓派、低配設備
│       │   └─ ✅ 選擇：NanoClaw 或 ZeroClaw
│       │
│       └─ 標準 PC / Mac
│           └─ ✅ 選擇：ZeroClaw（最強）或 OpenClaw（功能最全）
│
├─ 企業、團隊
│   └─ 需要什麼？
│       ├─ 多平台訊息整合（WhatsApp、Slack 等）
│       │   └─ ✅ 選擇：OpenClaw
│       │
│       └─ 自動化和運維（監控、爬蟲、日誌分析）
│           └─ ✅ 選擇：ZeroClaw（超高效）
│
├─ AI 研究者
│   └─ ✅ 選擇：Zeroclaw（社群最活躍）或 ZeroClaw（性能最優）
│
└─ 初學者，想快速上手
    └─ ✅ 選擇：NanoClaw（最簡潔，文件清楚）
```

## 📊 方案速查表

### 我想要什麼？

| 需求 | 推薦方案 | 原因 |
|------|--------|------|
| **最輕量、最簡潔** | NanoClaw | 5 檔案，容器隔離，MIT 開源 |
| **最強性能** | ZeroClaw | 內存 200 倍優化，毫秒啟動 |
| **最多功能** | OpenClaw | 7+ 訊息平台，完整生態 |
| **最活躍社群** | Zeroclaw | 21.8k 星，86+ PR，實時支援 |
| **技能共享** | ClawHub | 與 OpenClaw 搭配 |
| **AI 代理社交** | Moltbook | 了解新概念（早期） |

## 🎯 按場景選擇

### 1️⃣ 樹莓派上運行 AI Agent

```
樹莓派 4 (4GB RAM)
    ↓
需要輕量級
    ↓
推薦：NanoClaw ⭐⭐⭐⭐⭐
替代：ZeroClaw ⭐⭐⭐⭐⭐
```

**為什麼**：
- NanoClaw: 5 檔案，容器隔離，完全設計為樹莓派
- ZeroClaw: 性能最優，7.8MB 內存甚至樹莓派 Zero 也能跑

**快速上手**:
```bash
# NanoClaw
git clone <nanoclaw-repo>
docker run -it <image> zeroclaw onboard

# ZeroClaw
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
cargo install --path . --force
zeroclaw onboard --interactive
```

---

### 2️⃣ 公司要整合多個訊息平台（WhatsApp、Slack、Discord 等）

```
需要：多訊息平台
      ↓
需要：生產級穩定
      ↓
推薦：OpenClaw ⭐⭐⭐⭐
替代：ZeroClaw ⭐⭐⭐⭐（如果性能是首要）
```

**為什麼**:
- OpenClaw: 支援 7+ 訊息平台，Gateway 架構，完整文件
- ZeroClaw: 支援 Slack、Discord 等主流平台，性能優異

**成本對比**：
```
如需部署 5 個代理：
OpenClaw:  7.8 GB 內存   → ~$40/月
ZeroClaw:  39 MB 內存    → $2.5/月 ← 節省 94%
```

---

### 3️⃣ 自動化流水線（爬蟲、監控、日誌分析）

```
需要：高效率、低成本批量部署
      ↓
推薦：ZeroClaw ⭐⭐⭐⭐⭐
替代：NanoClaw ⭐⭐⭐⭐
```

**為什麼**:
- ZeroClaw: 毫秒啟動，極低內存，支援定時任務
- 可在 $5/月 的微型 VPS 上運行 50+ 代理

**典型用例**:
```
深夜 2 點定時抓取博客
    ↓
ZeroClaw + 定時任務
    ↓
低成本，高效率
```

---

### 4️⃣ 開發者，想深入學習和修改

```
需要：靈活配置、活躍社群、完整文件
      ↓
推薦：Zeroclaw ⭐⭐⭐⭐⭐（社群最大：21.8k 星）
替代：ZeroClaw ⭐⭐⭐⭐⭐（性能最優）
```

**為什麼**:
- Zeroclaw: 社群最活躍，86+ PR，隨時有人幫忙
- ZeroClaw: Rust 代碼簡潔，性能優異

**學習價值**:
- Zeroclaw: 了解 AI Agent 開發的主流做法
- ZeroClaw: 學習 Rust，高效能編程

---

### 5️⃣ 個人助手，只用 WhatsApp

```
需要：簡單、快速、安全
      ↓
推薦：NanoClaw ⭐⭐⭐⭐⭐
替代：ZeroClaw ⭐⭐⭐⭐
```

**為什麼**:
- NanoClaw: 最簡單，容器隔離最安全
- 專為 WhatsApp 優化

**安裝時間**: < 5 分鐘

---

### 6️⃣ AI 研究者，探索新概念

```
需要：靈活性、多提供商支援、新技術
      ↓
推薦：Zeroclaw ⭐⭐⭐⭐⭐（社群資源多）
替代：ZeroClaw ⭐⭐⭐⭐⭐（AIEOS 支援）
      Moltbook ⭐⭐⭐（新概念）
```

**為什麼**:
- Zeroclaw: 多提供商、活躍社群、豐富案例
- ZeroClaw: AIEOS 框架支援，現代設計
- Moltbook: 了解 AI 代理社交新方向（早期）

---

## 🎓 AIEOS 框架對你的影響？

### 什麼是 AIEOS？

**AIEOS** 是一個框架規範，讓你定義 AI 代理的「靈魂」：

```json
{
  "identity": "誰？",
  "psychology": "性格特徵",
  "linguistics": "說話方式",
  "motivations": "目標和驅動力"
}
```

### 支援 AIEOS 的方案

| 方案 | AIEOS 支援 |
|------|-----------|
| **ZeroClaw** | ✅ 完整支援 |
| **OpenClaw** | ✅ 原生支援 |
| **NanoClaw** | ❌ 不支援 |

### 你需要 AIEOS 嗎？

- ✅ **需要** - 如果想讓 AI 代理有持久化記憶和一致人設
- ✅ **需要** - 如果計劃多方案間遷移代理
- ⚠️ **可選** - 如果只是簡單的一次性任務

👉 **想深入了解？** 看 [AIEOS 框架詳解](./framework-aieos.md)

---

## 💡 最終建議

### 🥇 如果只能選一個

**99% 的人應該選：ZeroClaw**

**為什麼**：
1. 性能最優（200 倍內存改進）
2. 功能均衡（不少於 OpenClaw）
3. 成本最低（可批量部署）
4. 現代設計（AIEOS、沙箱安全）
5. 正在快速迭代

---

## 📋 安裝速度對比

| 方案 | 安裝時間 | 難度 |
|------|--------|------|
| **NanoClaw** | 5 分鐘 | 非常簡單 |
| **ZeroClaw** | 10 分鐘 | 簡單 |
| **OpenClaw** | 15-20 分鐘 | 中等 |
| **Zeroclaw** | 20 分鐘 | 中等 |
| **Moltbook** | 無需安裝（Web） | 無 |

---

## 🚀 後續行動

### Step 1：根據場景選擇（5 分鐘）
使用上面的決策樹或場景表格

### Step 2：閱讀詳細分析（20 分鐘）
- NanoClaw：看 [nanoclaw.md](./solution-nanoclaw.md)
- ZeroClaw：看 [zeroclaw-rust-version.md](./solution-zeroclaw-rust.md)
- OpenClaw：看 [openclaw.md](./solution-openclaw.md)

### Step 3：安裝和嘗試（10-30 分鐘）
大多數方案都有快速上手指南

### Step 4（可選）：深入 AIEOS（1 小時）
如需自訂 AI 代理的人設，讀 [aieos-framework.md](./framework-aieos.md)

---

## 🆘 還有疑問？

| 疑問 | 參考文檔 |
|------|--------|
| 性能對比 | [comparison.md](./02-comparison.md) |
| AIEOS 框架 | [aieos-framework.md](./framework-aieos.md) |
| 完整功能列表 | 各方案的詳細分析文檔 |
| 社群支援 | 各方案的 GitHub 或官方渠道 |

---

**祝你找到最適合的方案！** 🎉

如果你最後還是無法決定，就選 **ZeroClaw** - 它是目前最均衡、性能最優的選擇。

**更新日期**: 2026-03-02
