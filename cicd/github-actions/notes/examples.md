# GitHub Actions 工作流程示例

## 1. Node.js 項目的 CI 工作流程

### 基礎 CI 流程

```yaml
name: Node.js CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        node-version: [14.x, 16.x, 18.x]

    steps:
    - uses: actions/checkout@v3

    - name: Use Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v3
      with:
        node-version: ${{ matrix.node-version }}
        cache: 'npm'

    - name: Install dependencies
      run: npm ci

    - name: Run linter
      run: npm run lint

    - name: Run tests
      run: npm test

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        files: ./coverage/lcov.info
```

## 2. Docker 鏡像構建和推送

```yaml
name: Build and Push Docker Image

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2

    - name: Login to Docker Hub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}

    - name: Build and push
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: ${{ secrets.DOCKER_USERNAME }}/myapp:latest
        cache-from: type=registry,ref=${{ secrets.DOCKER_USERNAME }}/myapp:buildcache
        cache-to: type=registry,ref=${{ secrets.DOCKER_USERNAME }}/myapp:buildcache,mode=max
```

## 3. 自動發布到 npm

```yaml
name: Publish to npm

on:
  release:
    types: [created]

jobs:
  publish:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - uses: actions/setup-node@v3
      with:
        node-version: '18'
        registry-url: 'https://registry.npmjs.org'

    - run: npm ci
    - run: npm test
    - run: npm publish
      env:
        NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
```

## 4. 自動化部署到服務器

```yaml
name: Deploy to Server

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Deploy to server
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.SERVER_HOST }}
        username: ${{ secrets.SERVER_USER }}
        key: ${{ secrets.SSH_PRIVATE_KEY }}
        port: ${{ secrets.SERVER_PORT }}
        script: |
          cd /var/www/myapp
          git pull origin main
          npm install
          npm run build
          pm2 restart myapp
```

## 5. 代碼質量檢查和分析

```yaml
name: Code Quality

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  analysis:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3
      with:
        fetch-depth: 0

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install SonarQube Scanner
      run: |
        pip install sonarscan
        wget https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-4.7.0.2747-linux.zip
        unzip sonar-scanner-cli-4.7.0.2747-linux.zip

    - name: Run SonarQube analysis
      env:
        SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
      run: |
        ./sonar-scanner-4.7.0.2747-linux/bin/sonar-scanner \
          -Dsonar.projectKey=myproject \
          -Dsonar.sources=src \
          -Dsonar.host.url=https://sonarqube.example.com \
          -Dsonar.login=$SONAR_TOKEN
```

## 6. 定時任務 - 每日檢查

```yaml
name: Daily Security Check

on:
  schedule:
    - cron: '0 2 * * *'  # 每天凌晨 2 點
  workflow_dispatch:     # 允許手動觸發

jobs:
  security-check:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - uses: actions/setup-node@v3
      with:
        node-version: '18'

    - name: Install dependencies
      run: npm ci

    - name: Run security audit
      run: npm audit

    - name: Check for vulnerabilities
      run: npm audit --audit-level=moderate

    - name: Send notification
      if: failure()
      uses: actions/github-script@v6
      with:
        script: |
          github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: '⚠️ Security vulnerabilities detected!'
          })
```

## 7. 前端項目部署到 GitHub Pages

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'

    - name: Install dependencies
      run: npm ci

    - name: Build
      run: npm run build

    - name: Deploy to GitHub Pages
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./dist
```

## 8. 自動化合併拉取請求

```yaml
name: Auto Merge Dependabot PRs

on:
  pull_request:

permissions:
  pull-requests: write
  contents: write

jobs:
  automerge:
    runs-on: ubuntu-latest
    if: github.actor == 'dependabot[bot]'

    steps:
    - uses: actions/checkout@v3

    - name: Approve and merge Dependabot PRs
      uses: actions/github-script@v6
      with:
        script: |
          github.rest.pulls.createReview({
            owner: context.repo.owner,
            repo: context.repo.repo,
            pull_number: context.issue.number,
            event: 'APPROVE'
          })
          github.rest.pulls.merge({
            owner: context.repo.owner,
            repo: context.repo.repo,
            pull_number: context.issue.number
          })
```

## 9. 多平台構建

```yaml
name: Multi-platform Build

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ${{ matrix.os }}

    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        node-version: [16.x, 18.x]

    steps:
    - uses: actions/checkout@v3

    - uses: actions/setup-node@v3
      with:
        node-version: ${{ matrix.node-version }}

    - name: Install dependencies
      run: npm ci

    - name: Build
      run: npm run build

    - name: Upload artifact
      uses: actions/upload-artifact@v3
      with:
        name: build-${{ matrix.os }}-${{ matrix.node-version }}
        path: dist/
```

## 10. 生成版本標籤

```yaml
name: Create Release

on:
  push:
    tags:
      - 'v*.*.*'

jobs:
  create-release:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Get version from tag
      id: tag_version
      run: echo "version=${GITHUB_REF#refs/tags/}" >> $GITHUB_OUTPUT

    - name: Create Release
      uses: actions/create-release@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        tag_name: ${{ steps.tag_version.outputs.version }}
        release_name: Release ${{ steps.tag_version.outputs.version }}
        draft: false
        prerelease: false
```

## 使用這些示例的步驟

1. 複製 YAML 代碼
2. 在你的倉庫中創建 `.github/workflows/` 目錄（如不存在）
3. 創建對應的 `.yml` 文件（如 `ci.yml`）
4. 將代碼粘貼到文件中
5. 根據需要修改參數和環境變數
6. 提交並推送到倉庫
7. 在 GitHub 的 Actions 標籤中查看執行結果

## 調試工作流程

### 啟用調試日誌
```yaml
env:
  ACTIONS_STEP_DEBUG: true
```

### 查看日誌
1. 進入倉庫的 Actions 標籤
2. 選擇工作流程運行
3. 展開失敗的步驟查看詳細日誌

### 本地測試
使用 `act` 工具在本地測試工作流程：
```bash
npm install -g @actions/toolkit
act
```
