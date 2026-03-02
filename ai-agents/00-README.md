# AI Agent 本地部署方案研究

本目錄對比研究幾個主流的AI Agent本地部署方案，涵蓋功能、效能、優劣勢、社群生態等方面。

## 📋 方案概覽

| 方案 | 類型 | 星標 | 難度 | 特點 |
|------|------|------|------|------|
| [OpenClaw](./solution-openclaw.md) | 完整平台 | ⭐ 待研究 | 中 | 多平台整合、生產就緒、Gateway架構 |
| [NanoClaw](./solution-nanoclaw.md) | 輕量級方案 | 6.7k | 低 | 容器隔離、簡潔設計、樹莓派友善 |
| [Zeroclaw](./solution-zeroclaw-cli.md) | 開發工具 | 21.8k | 中 | 易用入門、多提供商、跨平台 |
| [ClawHub](./solution-clawhub.md) | 技能市場 | - | 低 | 技能註冊表、社群共享 |
| [Moltbook](./solution-moltbook.md) | 社交網路 | - | 低 | AI代理社交平台（早期） |

## 🎯 核心對比 & 快速選擇

### ⚡ 3 分鐘快速選擇
👉 **[快速選擇指南](./01-quick-choice-guide.md)** - 根據你的場景立即找到最適合的方案！

### 📊 詳細對比
詳見 [**完整對比分析**](./02-comparison.md)

### 🚀 快速推薦

| 場景 | 推薦方案 | 理由 |
|------|---------|------|
| **樹莓派/個人使用** | NanoClaw | 5 檔案、容器隔離、超簡單 |
| **性能第一、規模部署** | ZeroClaw ⭐ | 內存低 200 倍、毫秒啟動 |
| **多平台企業集成** | OpenClaw | 7+ 訊息平台、生產就緒 |
| **開發者/社群** | Zeroclaw | 21.8k 星、最活躍 |
| **技能共享** | ClawHub | 與 OpenClaw 搭配 |

## 📚 文件結構

```
ai-agents/
├── 00-README.md                      # 總覽和快速導航（此檔案）
├── 01-quick-choice-guide.md          # ⚡ 快速選擇（推薦先看）
├── 02-comparison.md                  # 📊 全面對比分析

├── 📋 完整方案分析
│   ├── solution-openclaw.md          # OpenClaw 詳細分析
│   ├── solution-zeroclaw-rust.md     # ⭐ ZeroClaw 詳細分析（OpenClaw 高效版）
│   ├── solution-nanoclaw.md          # NanoClaw 詳細分析
│   ├── solution-zeroclaw-cli.md      # Zeroclaw CLI 工具分析
│   ├── solution-clawhub.md           # ClawHub 技能市場
│   └── solution-moltbook.md          # Moltbook 社交平台
│
└── 🔬 框架與標準
    └── framework-aieos.md             # ⭐ AIEOS 框架規範詳解（重點！）

📖 推薦閱讀順序：
   新手: 00-README → 01-quick-choice → 02-comparison → 選定方案
   進階: framework-aieos → solution-openclaw → solution-zeroclaw-rust
```

## 🔗 官方參考源

| 項目 | GitHub / 官網 | 備註 |
|------|--------------|------|
| **OpenClaw** | [GitHub](https://github.com/openclaw/openclaw) | 完整多平台平台 |
| **NanoClaw** | [GitHub](https://github.com/qwibitai/nanoclaw) | 輕量級方案 |
| **Zeroclaw** | [GitHub](https://github.com/zeroclaw-labs/zeroclaw) | 開源 CLI 工具 |
| **ZeroClaw** | [Official](https://zeroclaw.bot/) / [GitHub](https://github.com/theonlyhennygod/zeroclaw) | Rust 重構版本 |
| **ClawHub** | [官方文件](https://clawhub.ai/) | 技能市場 |
| **Moltbook** | [官網](https://www.moltbook.com/) | AI 代理社交平台 |

💡 **所有 AIEOS 相關資訊均已對比官方來源驗證。**

## 🔍 研究基準

本研究基於以下維度進行分析：

1. **功能性** - 支援的功能特性、整合能力
2. **效能** - 資源佔用、回應速度、可擴展性
3. **大小** - 部署大小、依賴項數量
4. **優劣勢** - 相對優勢、限制條件
5. **社群** - 社群活躍度、支援品質、文件完整度
6. **部署** - 本地化程度、安裝難度、維護成本
7. **成本** - 授權證、商業因素

## 🌟 關鍵框架：AIEOS

**AIEOS（AI Entity Object Specification）** 是標準化 AI 代理人設的框架。支援方案：
- ✅ OpenClaw（原生支援）
- ✅ ZeroClaw（完整支援）
- ❌ NanoClaw（不支援）

👉 **詳見 [AIEOS 框架詳解](./framework-aieos.md)**

## 🚀 推薦亮點：ZeroClaw（Rust 重構版）

性能最優的 OpenClaw 替代方案：
- 內存占用降 200 倍（7.8 MB vs 1,560 MB）
- 毫秒級啟動（vs 秒級）
- 完整 AIEOS 支援
- 最適合樹莓派、邊緣計算、批量部署

👉 **詳見 [ZeroClaw 詳細分析](./solution-zeroclaw-rust.md)**

---

**更新日期**: 2026-03-02
**研究來源**: 官方文件、GitHub 專案、技術文章、官方網站
