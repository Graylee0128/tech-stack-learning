# GitHub Actions 速查表

## 工作流程基本結構

```yaml
name: Workflow Name
on: [push, pull_request]
jobs:
  job-name:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: echo "Hello World"
```

## 觸發事件

| 事件 | 說明 | 用法 |
|------|------|------|
| `push` | 推送代碼 | `on: [push]` |
| `pull_request` | 拉取請求 | `on: [pull_request]` |
| `schedule` | 定時執行 | `on: schedule: - cron: '0 0 * * *'` |
| `workflow_dispatch` | 手動觸發 | `on: workflow_dispatch` |
| `release` | 版本發布 | `on: [release]` |

## Runner 類型

| Runner | 說明 | 用法 |
|--------|------|------|
| `ubuntu-latest` | Ubuntu 最新版本 | `runs-on: ubuntu-latest` |
| `windows-latest` | Windows 最新版本 | `runs-on: windows-latest` |
| `macos-latest` | macOS 最新版本 | `runs-on: macos-latest` |
| `self-hosted` | 自託管 Runner | `runs-on: self-hosted` |

## 常用步驟

### 檢出代碼
```yaml
- uses: actions/checkout@v3
```

### 設置運行環境
```yaml
- uses: actions/setup-node@v3
  with:
    node-version: '16'
```

### 執行命令
```yaml
- run: npm install
- run: npm test
```

### 上傳工件
```yaml
- uses: actions/upload-artifact@v3
  with:
    name: coverage-report
    path: coverage/
```

### 下載工件
```yaml
- uses: actions/download-artifact@v3
  with:
    name: coverage-report
```

## 環境變數和 Secret

### 設置環境變數
```yaml
env:
  NODE_ENV: production
  DEBUG: false

steps:
  - run: echo $NODE_ENV
```

### 使用 Secret
```yaml
- run: npm publish
  env:
    NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
```

## 條件控制

### 基於分支
```yaml
on:
  push:
    branches: [ main, develop ]
```

### 基於路徑
```yaml
on:
  push:
    paths:
      - 'src/**'
      - 'package.json'
```

### 步驟條件
```yaml
- run: npm test
  if: github.event_name == 'pull_request'
```

## Matrix 構建（多環境測試）

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [14, 16, 18]
    steps:
      - uses: actions/setup-node@v3
        with:
          node-version: ${{ matrix.node-version }}
      - run: npm test
```

## 工作流狀態檢查

```yaml
- name: Check build status
  if: failure()
  run: echo "Previous step failed"

- name: Success notification
  if: success()
  run: echo "Workflow completed successfully"
```

## 輸出日誌

### 簡單輸出
```yaml
- run: echo "Build successful"
```

### 帶顏色的輸出
```yaml
- run: echo "::notice file=app.js::Something happened"
- run: echo "::warning file=app.js::Warning message"
- run: echo "::error file=app.js::Error message"
```

### 設置輸出值
```yaml
- id: greeting
  run: echo "value=Hello" >> $GITHUB_OUTPUT
- run: echo "${{ steps.greeting.outputs.value }}"
```

## 常用 Actions

```yaml
# 代碼檢出
- uses: actions/checkout@v3

# Node.js 設置
- uses: actions/setup-node@v3

# Python 設置
- uses: actions/setup-python@v4

# 代碼覆蓋率
- uses: codecov/codecov-action@v3

# Docker 構建和推送
- uses: docker/build-push-action@v4

# 發布到 npm
- uses: JS-DevTools/npm-publish@v1

# 創建 GitHub Release
- uses: actions/create-release@v1
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Workflow 文件位置

所有工作流程文件必須放在：
```
.github/workflows/
├── ci.yml
├── deploy.yml
└── schedule.yml
```

## 常見 Context 變數

| 變數 | 說明 |
|------|------|
| `github.event_name` | 觸發事件類型 |
| `github.ref` | 分支/標籤參考 |
| `github.sha` | 提交 SHA |
| `github.actor` | 觸發者用戶名 |
| `runner.os` | Runner 操作系統 |
| `job.status` | 工作狀態 |
