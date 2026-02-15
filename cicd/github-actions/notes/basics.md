# GitHub Actions 基礎概念

## 什麼是 GitHub Actions？

GitHub Actions 是 GitHub 提供的內建 CI/CD 和工作流程自動化平台。它允許你在 GitHub 上自動化軟體開發工作流程，無需部署額外的 CI/CD 工具。

## 核心概念深入解析

### 1. Workflows（工作流程）

**定義**: 由一個或多個任務組成的自動化流程。

**特點**：
- 存儲在 `.github/workflows/` 目錄中
- 使用 YAML 格式定義
- 由特定事件觸發
- 可以並行或順序執行

**基本結構**：
```yaml
name: My Workflow              # 工作流程名稱
on: push                       # 觸發事件
jobs:                          # 任務集合
  my-job:                      # 任務 ID
    runs-on: ubuntu-latest     # 運行環境
    steps:                     # 步驟列表
      - name: Step 1
        run: echo "Hello"
```

### 2. Events（事件）

事件是觸發工作流程執行的活動。

**常見事件類型**：

#### Repository 事件
- `push` - 推送代碼到倉庫
- `pull_request` - 創建或更新拉取請求
- `release` - 發布新版本
- `issues` - 創建或更新 Issue
- `fork` - Fork 倉庫

#### Scheduled 事件
- `schedule` - 使用 Cron 表達式定時執行
  ```yaml
  on:
    schedule:
      - cron: '0 0 * * 0'  # 每週日午夜執行
  ```

#### Manual 事件
- `workflow_dispatch` - 手動觸發
  ```yaml
  on:
    workflow_dispatch:
      inputs:
        version:
          description: 'Version number'
          required: true
  ```

#### 其他事件
- `pull_request_review` - 拉取請求評論
- `pull_request_target` - PR 目標分支更改
- `workflow_run` - 工作流程完成

### 3. Jobs（任務）

**定義**: 工作流程中的執行單位，由多個步驟組成。

**特點**：
- 默認並行執行
- 可以設置依賴關係使其順序執行
- 每個任務在獨立的 Runner 實例上運行

**任務配置**：
```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: npm install
      - run: npm test

  deploy:
    runs-on: ubuntu-latest
    needs: build              # 依賴於 build 任務
    steps:
      - run: npm run deploy
```

**任務選項**：
- `runs-on` - 指定 Runner 類型
- `needs` - 設置依賴任務
- `if` - 條件執行
- `timeout-minutes` - 超時設置
- `continue-on-error` - 錯誤時繼續

### 4. Steps（步驟）

**定義**: 任務中的個別操作。

**步驟類型**：

#### Run Step - 執行命令
```yaml
- name: Run script
  run: npm test
```

#### Uses Step - 使用 Action
```yaml
- name: Checkout code
  uses: actions/checkout@v3
```

**步驟特性**：
- 按順序執行
- 可以設置 ID、名稱、條件
- 可以設置超時

### 5. Actions（動作）

**定義**: 可重複使用的應用程序，用於執行特定任務。

**Action 類型**：
- 容器 Action
- JavaScript Action
- 組合 Action

**官方 Actions 示例**：
```yaml
- uses: actions/checkout@v3       # 檢出代碼
- uses: actions/setup-node@v3     # 設置 Node.js
- uses: actions/upload-artifact@v3 # 上傳工件
```

**Action 版本指定**：
```yaml
uses: actions/checkout@v3         # 主版本
uses: actions/checkout@v3.1.0     # 完整版本
uses: actions/checkout@main       # 分支
```

## 工作流程執行流程

```
事件觸發
   ↓
讀取 .github/workflows/*.yml 文件
   ↓
創建 Runner 實例
   ↓
執行所有任務（默認並行）
   ↓
執行每個任務中的步驟（順序執行）
   ↓
生成日誌和輸出
   ↓
通知工作流程結果
```

## 環境和上下文

### 運行者（Runner）

**什麼是 Runner？**
- 執行工作流程的虛擬機或容器
- 由 GitHub 提供或自託管
- 每個任務在獨立的 Runner 實例上執行

**可用 Runner**：
| 系統 | 虛擬環境 | 標籤 |
|------|--------|------|
| Ubuntu | 最新版本 | `ubuntu-latest` |
| Windows | 最新版本 | `windows-latest` |
| macOS | 最新版本 | `macos-latest` |

### 上下文（Context）

上下文提供了關於工作流程執行、運行環境和事件的信息。

**常用上下文**：

```yaml
steps:
  - name: Print contexts
    run: |
      echo "Event: ${{ github.event_name }}"
      echo "Branch: ${{ github.ref }}"
      echo "Commit: ${{ github.sha }}"
      echo "Actor: ${{ github.actor }}"
```

**主要上下文對象**：
- `github` - GitHub 事件和工作流程信息
- `env` - 環境變數
- `secrets` - 存儲的敏感信息
- `runner` - Runner 的信息
- `steps` - 前面步驟的輸出

## 安全性考慮

### Secrets 管理

**存儲敏感信息**：
1. 進入倉庫設置 → Secrets and variables → Actions
2. 點擊 "New repository secret"
3. 添加名稱和值

**使用 Secrets**：
```yaml
- name: Deploy
  run: deploy.sh
  env:
    DEPLOY_KEY: ${{ secrets.DEPLOY_KEY }}
```

**最佳實踐**：
- 不要在 YAML 文件中硬編碼敏感信息
- 使用環境 Secrets 而不是倉庫 Secrets
- 限制 Secret 訪問權限
- 定期輪換敏感信息

### 權限管理

```yaml
permissions:
  contents: read
  pull-requests: write
```

## 計費和限制

**免費額度**：
- 公開倉庫：無限制
- 私有倉庫：每月 2000 分鐘

**限制**：
- 工作流程運行時限：6 小時
- 工件保留期：90 天
- 工作流程大小：100 MB
- Job 數量：256 個（並行）

## 常見使用場景

1. **持續集成（CI）** - 自動運行測試
2. **持續部署（CD）** - 自動部署應用
3. **代碼質量檢查** - 運行 Lint 和分析工具
4. **發布管理** - 自動發布版本
5. **文檔生成** - 自動生成和發布文檔
6. **定期任務** - 計劃執行的任務
