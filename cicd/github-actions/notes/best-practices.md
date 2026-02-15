# GitHub Actions 最佳實踐

## 1. 工作流程設計

### 保持工作流程簡單清晰

✅ **推薦**：
```yaml
name: CI Pipeline
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm install
      - run: npm test
```

❌ **避免**：
```yaml
# 過於複雜的工作流程，混合多個不相關的任務
```

### 使用有意義的名稱

✅ **推薦**：
```yaml
name: Build and Test
jobs:
  unit-tests:
    steps:
      - name: Run unit tests
```

❌ **避免**：
```yaml
name: Job1
jobs:
  job:
    steps:
      - name: Step1
```

### 拆分多個任務

✅ **推薦** - 並行執行：
```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - run: npm run lint

  test:
    runs-on: ubuntu-latest
    steps:
      - run: npm test

  build:
    needs: [lint, test]
    runs-on: ubuntu-latest
    steps:
      - run: npm run build
```

## 2. 性能優化

### 使用工件緩存

✅ **推薦**：
```yaml
- uses: actions/setup-node@v3
  with:
    node-version: '18'
    cache: 'npm'

# 或手動緩存
- uses: actions/cache@v3
  with:
    path: ~/.npm
    key: ${{ runner.os }}-npm-${{ hashFiles('**/package-lock.json') }}
    restore-keys: ${{ runner.os }}-npm-
```

### 限制工作流程運行

```yaml
# 防止多個工作流程並發運行
concurrency:
  group: ${{ github.ref }}
  cancel-in-progress: true
```

### 優化 Docker 映像

```yaml
- uses: docker/setup-buildx-action@v2

- uses: docker/build-push-action@v4
  with:
    cache-from: type=registry,ref=myrepo/myimage:buildcache
    cache-to: type=registry,ref=myrepo/myimage:buildcache,mode=max
```

## 3. 安全性最佳實踐

### 管理 Secrets

✅ **推薦**：
```yaml
env:
  API_KEY: ${{ secrets.API_KEY }}

- run: |
    curl -H "Authorization: Bearer $API_KEY" \
      https://api.example.com
```

❌ **避免**：
```yaml
env:
  API_KEY: "sk_live_1234567890"  # 直接存儲敏感信息

- run: echo "Password is MyPassword123"  # 洩露敏感信息
```

### 限制權限

```yaml
permissions:
  contents: read
  pull-requests: write
  packages: write
  id-token: write
```

### 使用環境級別的 Secrets

```yaml
jobs:
  deploy:
    environment: production
    steps:
      - run: deploy.sh
        env:
          DEPLOY_KEY: ${{ secrets.DEPLOY_KEY }}
```

### 驗證外部 Actions

✅ **推薦**：使用特定版本的 Action：
```yaml
- uses: actions/checkout@v3.1.0
```

❌ **避免**：使用 latest 或 main：
```yaml
- uses: actions/checkout@main  # 不推薦
```

## 4. 錯誤處理

### 優雅地處理失敗

```yaml
- name: Run tests
  id: test
  run: npm test
  continue-on-error: true

- name: Upload coverage if tests passed
  if: steps.test.outcome == 'success'
  run: npm run coverage
```

### 設置超時

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - name: Long running test
        run: ./long-test.sh
        timeout-minutes: 10
```

### 重試失敗的步驟

使用第三方 Action：
```yaml
- name: Flaky test
  uses: nick-invision/retry@v2
  with:
    timeout_minutes: 10
    max_attempts: 3
    retry_wait_seconds: 60
    command: npm test
```

## 5. 監控和日誌

### 添加詳細日誌

```yaml
- name: Debug info
  if: failure()
  run: |
    echo "Workflow failed at: $(date)"
    echo "Commit: ${{ github.sha }}"
    echo "Branch: ${{ github.ref }}"
```

### 生成工件

```yaml
- name: Upload test results
  if: always()
  uses: actions/upload-artifact@v3
  with:
    name: test-results
    path: test-results/
    retention-days: 30
```

### 通知

```yaml
- name: Notify on failure
  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    text: 'Build failed!'
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

## 6. 依賴管理

### 使用 Matrix 進行多版本測試

```yaml
strategy:
  matrix:
    node-version: [14.x, 16.x, 18.x]
    os: [ubuntu-latest, windows-latest, macos-latest]
  fail-fast: false
```

### 固定 Action 版本

```yaml
# ✅ 推薦
- uses: actions/setup-node@v3.5.0

# ⚠️ 可以接受
- uses: actions/setup-node@v3

# ❌ 不推薦
- uses: actions/setup-node@main
```

## 7. 成本優化

### 限制工作流程執行

```yaml
on:
  push:
    branches: [main]
    paths:
      - 'src/**'
      - 'package.json'

  pull_request:
    types: [opened, synchronize, reopened]
```

### 使用自託管 Runner

如果有大量工作流程，考慮使用自託管 Runner 以降低成本。

### 清理工件

```yaml
- name: Clean up old artifacts
  uses: geekyeggo/delete-artifact@v2
  with:
    name: build-artifacts
```

## 8. 工作流程維護

### 文檔化工作流程

```yaml
# 構建和測試工作流程
# 在推送到 main 或創建拉取請求時運行
# 安裝依賴、運行 linter 和測試
name: CI Pipeline
```

### 定期更新 Actions

```yaml
# 定期檢查 Action 更新
# 使用 Dependabot 來自動創建更新 PR
name: Update Actions
on:
  schedule:
    - cron: '0 0 * * 0'
```

### 使用工作流程模板

在 `.github/workflows/` 目錄中創建可重複使用的工作流程。

## 9. 常見陷阱和解決方案

### 問題 1：超時
```yaml
# 設置合適的超時時間
timeout-minutes: 30

jobs:
  test:
    timeout-minutes: 30
```

### 問題 2：磁盤空間不足
```yaml
- name: Clean up space
  run: |
    docker system prune -af
    rm -rf /usr/share/dotnet
```

### 問題 3：環境變數不正確傳遞

✅ **推薦**：
```yaml
- name: Deploy
  env:
    API_URL: ${{ vars.API_URL }}
    API_KEY: ${{ secrets.API_KEY }}
  run: ./deploy.sh
```

### 問題 4：工作流程不觸發

檢查清單：
- 確認事件配置正確
- 檢查分支過濾器
- 確認文件在正確的位置：`.github/workflows/*.yml`
- 驗證 YAML 語法

## 10. 實用技巧

### 使用 GitHub Script

```yaml
- uses: actions/github-script@v6
  with:
    script: |
      github.rest.issues.createComment({
        issue_number: context.issue.number,
        owner: context.repo.owner,
        repo: context.repo.repo,
        body: '✅ All checks passed!'
      })
```

### 條件執行

```yaml
- name: Deploy to production
  if: |
    github.event_name == 'push' &&
    github.ref == 'refs/heads/main'
  run: deploy.sh
```

### 使用變數

```yaml
env:
  REGISTRY: ghcr.io

jobs:
  build:
    runs-on: ubuntu-latest
    env:
      IMAGE_NAME: ${{ env.REGISTRY }}/${{ github.repository }}
```

## 檢查清單

在發佈工作流程前檢查：

- [ ] 已測試工作流程邏輯
- [ ] Secrets 正確配置
- [ ] 權限設置最小化
- [ ] 超時設置合理
- [ ] 錯誤處理完善
- [ ] 日誌和輸出清晰
- [ ] Action 版本已固定
- [ ] 工作流程文檔完整
- [ ] 性能已優化（緩存、並行等）
- [ ] 成本考慮因素已評估
