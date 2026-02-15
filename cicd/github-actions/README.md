# GitHub Actions 學習指南

## 概述
GitHub Actions 是 GitHub 的內建持續整合和持續部署 (CI/CD) 平台，允許你在發生特定事件時自動執行工作流程。

## 目錄結構

### notes/ - 學習筆記
- `basics.md` - GitHub Actions 基礎知識
- `cheatsheet.md` - GitHub Actions 速查表
- `examples.md` - 工作流程示例
- `best-practices.md` - 最佳實踐

### articles/ - 精品文章
（待補充）

## 核心概念

### 1. Workflows（工作流程）
- 定義在 `.github/workflows/` 目錄中的 YAML 文件
- 由事件觸發自動執行的流程

### 2. Events（事件）
觸發工作流程的事件類型：
- `push` - 代碼推送
- `pull_request` - 拉取請求
- `schedule` - 定時觸發（Cron）
- `workflow_dispatch` - 手動觸發
- `release` - 版本發布

### 3. Jobs（任務）
- 工作流程中的獨立執行單位
- 可以並行或順序執行
- 在 runner 上執行

### 4. Steps（步驟）
- 任務中的具體執行單位
- 執行命令或使用 Action

### 5. Actions（動作）
- 可重複使用的應用程序
- 簡化工作流程配置
- 官方和社區提供的 Actions

## 基本工作流程結構

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3
    - name: 設置環境
      run: echo "Setting up environment"
    - name: 執行測試
      run: npm test
```

## 常用 Actions

### 官方 Actions
- `actions/checkout@v3` - 檢出代碼
- `actions/setup-node@v3` - 設置 Node.js
- `actions/setup-python@v4` - 設置 Python
- `actions/upload-artifact@v3` - 上傳工件
- `actions/create-release@v1` - 創建版本發布

### 社區 Actions
- `codecov/codecov-action` - 代碼覆蓋率
- `actions/labeler` - 自動標籤管理
- `github/codeql-action` - 代碼安全分析

## 學習路線

1. **第 1 週** - 基礎概念和簡單工作流程
   - 理解 GitHub Actions 核心概念
   - 創建第一個簡單的工作流程

2. **第 2 週** - 實踐應用
   - 設置 CI/CD 流程
   - 集成測試框架
   - 部署應用

3. **第 3 週** - 高級功能
   - 使用 Matrix 進行多環境測試
   - 環境變數和 Secret 管理
   - 創建自定義 Action

4. **第 4 週** - 最佳實踐和優化
   - 工作流程優化
   - 安全性考慮
   - 成本優化

## 資源連結

- [官方文檔](https://docs.github.com/zh/actions)
- [Actions 市場](https://github.com/marketplace?type=actions)
- [社區模板](https://github.com/actions/starter-workflows)

## 我的筆記

（待補充學習筆記）
