# GitHub Environments + Manual Approval + Trivy Security Scan

## 概念：什麼是 GitHub Environments

GitHub Environments 是 GitHub 原生的「部署環境管理」功能，可以：
- 為不同環境（staging、production）設定不同 Secrets
- 設定 **Protection Rules**（需要人工批准才能繼續部署）
- 在 GitHub UI 上看到每個環境的部署歷史

---

## Part 1：GitHub Environments UI 設定（手動操作一次）

### 步驟

1. 進入 GitHub repo → **Settings** → **Environments**
2. 點 **New environment**，建立兩個：
   - `staging`
   - `production`

3. 對 `production` 環境點進去，設定：
   - **Required reviewers**：加入自己的帳號
   - **Wait timer**：可選（例如等 5 分鐘才能批准）
   - 勾選 **Prevent self-review** 如果是 team 協作

4. 對兩個環境分別加入對應 Secrets（例如 `SSH_KEY`、`SERVER_IP`）

### 設定後的效果

workflow 跑到 `environment: production` 的 job 時，會在 GitHub UI **暫停**，顯示等待批准的對話框。批准者點確認後才繼續。

---

## Part 2：Multi-environment Workflow（staging + production）

### 架構

```
develop branch push → deploy to staging（自動）
main branch push    → deploy to production（需手動批准）
```

### 完整 Workflow

```yaml
name: Multi-environment Deploy

on:
  push:
    branches:
      - develop   # 觸發 staging
      - main      # 觸發 production

env:
  IMAGE_NAME: your-dockerhub-username/my-app

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

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
          tags: ${{ env.IMAGE_NAME }}:${{ github.sha }}

  # Staging：develop branch 推送時自動跑
  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    environment: staging          # 使用 staging 環境的 Secrets
    if: github.ref == 'refs/heads/develop'

    steps:
      - name: Deploy to staging
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.SERVER_IP }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_KEY }}
          envs: IMAGE_NAME,GITHUB_SHA
          script: |
            docker pull $IMAGE_NAME:$GITHUB_SHA
            docker stop my-app-staging || true
            docker rm my-app-staging || true
            docker run -d --name my-app-staging -p 5001:5000 $IMAGE_NAME:$GITHUB_SHA

  # Production：main branch 推送時，需要人工批准
  deploy-production:
    needs: build
    runs-on: ubuntu-latest
    environment: production       # 這裡觸發 protection rule，等待批准
    if: github.ref == 'refs/heads/main'

    steps:
      - name: Deploy to production
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.SERVER_IP }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_KEY }}
          envs: IMAGE_NAME,GITHUB_SHA
          script: |
            docker pull $IMAGE_NAME:$GITHUB_SHA
            docker stop my-app || true
            docker rm my-app || true
            docker run -d --name my-app -p 5000:5000 $IMAGE_NAME:$GITHUB_SHA
```

---

## Part 3：Trivy Security Scan

Trivy 是 Aqua Security 開源的容器 image 漏洞掃描工具。掃描 Docker image 中的 OS 套件和語言套件的 CVE（已知漏洞）。

### 加到 CI Pipeline（在 push 之前掃）

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      # 先 build（不 push），掃完才 push
      - name: Build Docker image
        run: docker build -t ${{ env.IMAGE_NAME }}:${{ github.sha }} .

      # Trivy scan
      - name: Run Trivy vulnerability scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ env.IMAGE_NAME }}:${{ github.sha }}
          format: 'table'             # 輸出格式（table / json / sarif）
          exit-code: '1'              # 發現漏洞時讓 job 失敗（阻擋部署）
          ignore-unfixed: true        # 忽略還沒有修復版本的漏洞
          severity: 'CRITICAL,HIGH'  # 只對這兩個等級報警

      # 掃完才 push
      - name: Login and push
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - run: docker push ${{ env.IMAGE_NAME }}:${{ github.sha }}
```

### Trivy severity 等級說明

| 等級 | 說明 | 建議處理 |
|------|------|---------|
| CRITICAL | 嚴重，已知可被利用 | 立刻修 |
| HIGH | 高風險 | 本次 PR 要修 |
| MEDIUM | 中等 | 排進 backlog |
| LOW | 低風險 | 可接受 |
| UNKNOWN | 資訊不足 | 忽略或調查 |

### 常用參數

```yaml
with:
  image-ref: 'myapp:latest'
  format: 'sarif'               # 上傳到 GitHub Security tab 用
  output: 'trivy-results.sarif'
  exit-code: '1'
  severity: 'CRITICAL,HIGH'
  ignore-unfixed: true          # 沒有 patch 的漏洞不算（減少噪音）
```

### 上傳掃描結果到 GitHub Security tab（進階）

```yaml
      - name: Upload Trivy scan results to GitHub Security tab
        uses: github/codeql-action/upload-sarif@v2
        if: always()    # 即使 scan 失敗也上傳
        with:
          sarif_file: 'trivy-results.sarif'
```

---

## 把所有東西串起來的完整 Pipeline

```yaml
name: Full CI/CD Pipeline

on:
  push:
    branches: [ develop, main ]

env:
  IMAGE_NAME: your-dockerhub-username/my-app

jobs:
  build-and-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build Docker image
        run: docker build -t ${{ env.IMAGE_NAME }}:${{ github.sha }} .

      - name: Trivy scan (block on CRITICAL/HIGH)
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ env.IMAGE_NAME }}:${{ github.sha }}
          format: 'table'
          exit-code: '1'
          severity: 'CRITICAL,HIGH'
          ignore-unfixed: true

      - name: Push to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - run: docker push ${{ env.IMAGE_NAME }}:${{ github.sha }}

  deploy-staging:
    needs: build-and-scan
    runs-on: ubuntu-latest
    environment: staging
    if: github.ref == 'refs/heads/develop'
    steps:
      - uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.SERVER_IP }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_KEY }}
          envs: IMAGE_NAME,GITHUB_SHA
          script: |
            PREV=$(docker inspect my-app-staging --format='{{.Config.Image}}' 2>/dev/null || echo "none")
            docker pull $IMAGE_NAME:$GITHUB_SHA
            docker stop my-app-staging || true && docker rm my-app-staging || true
            docker run -d --name my-app-staging -p 5001:5000 $IMAGE_NAME:$GITHUB_SHA
            sleep 5
            STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5001/health)
            if [ "$STATUS" != "200" ]; then
              docker stop my-app-staging && docker rm my-app-staging
              [ "$PREV" != "none" ] && docker run -d --name my-app-staging -p 5001:5000 $PREV
              exit 1
            fi

  deploy-production:
    needs: build-and-scan
    runs-on: ubuntu-latest
    environment: production     # 暫停，等人工批准
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.SERVER_IP }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_KEY }}
          envs: IMAGE_NAME,GITHUB_SHA
          script: |
            PREV=$(docker inspect my-app --format='{{.Config.Image}}' 2>/dev/null || echo "none")
            docker pull $IMAGE_NAME:$GITHUB_SHA
            docker stop my-app || true && docker rm my-app || true
            docker run -d --name my-app -p 5000:5000 $IMAGE_NAME:$GITHUB_SHA
            sleep 5
            STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/health)
            if [ "$STATUS" != "200" ]; then
              docker stop my-app && docker rm my-app
              [ "$PREV" != "none" ] && docker run -d --name my-app -p 5000:5000 $PREV
              exit 1
            fi
```

---

## 面試說法

> 我在 CI pipeline 加了 Trivy 做 container image 掃描，設定遇到 CRITICAL 和 HIGH 的 CVE 就阻擋部署。Staging 環境在 develop branch push 後自動部署，Production 則用 GitHub Environments 的 protection rule，需要手動批准才能繼續，模擬公司的 change approval 流程。
