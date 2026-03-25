# Docker Deploy Pattern：SHA Tagging + Health Check + Rollback

## 為什麼用 SHA tag，不用 latest

| tag 策略 | 問題 |
|----------|------|
| `:latest` | 不知道跑的是哪個版本；rollback 時不知道回到哪 |
| `:${{ github.sha }}` | 每個 commit 對應唯一 image；可精準 rollback |

---

## 完整 Workflow：Build → Deploy → Health Check → Rollback

```yaml
name: Deploy to HomeLab

on:
  push:
    branches: [ develop ]   # staging 環境用 develop branch

env:
  IMAGE_NAME: your-dockerhub-username/my-app

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    outputs:
      image-tag: ${{ github.sha }}   # 把 SHA 傳給下一個 job

    steps:
      - uses: actions/checkout@v3

      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build and push (SHA-tagged)
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: |
            ${{ env.IMAGE_NAME }}:${{ github.sha }}
            ${{ env.IMAGE_NAME }}:latest

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest

    steps:
      - name: Deploy to staging via SSH
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.SERVER_IP }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_KEY }}
          envs: IMAGE_NAME,GITHUB_SHA   # 把環境變數帶進去
          script: |
            # 記錄目前運行的 image（供 rollback 用）
            PREV_IMAGE=$(docker inspect my-app --format='{{.Config.Image}}' 2>/dev/null || echo "none")
            echo "Previous image: $PREV_IMAGE"

            # 拉新 image
            docker pull $IMAGE_NAME:$GITHUB_SHA

            # 停止並移除舊 container
            docker stop my-app || true
            docker rm my-app || true

            # 啟動新 container
            docker run -d \
              --name my-app \
              --restart unless-stopped \
              -p 5000:5000 \
              -e PREV_IMAGE="$PREV_IMAGE" \
              $IMAGE_NAME:$GITHUB_SHA

            # 等待啟動
            sleep 5

            # Health check
            HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/health)
            echo "Health check status: $HTTP_STATUS"

            if [ "$HTTP_STATUS" != "200" ]; then
              echo "Health check FAILED. Rolling back to $PREV_IMAGE..."

              docker stop my-app || true
              docker rm my-app || true

              if [ "$PREV_IMAGE" != "none" ]; then
                docker run -d \
                  --name my-app \
                  --restart unless-stopped \
                  -p 5000:5000 \
                  $PREV_IMAGE
                echo "Rollback complete."
              else
                echo "No previous image to rollback to."
              fi

              exit 1   # 讓 workflow 標記失敗
            fi

            echo "Deployment successful. Running: $IMAGE_NAME:$GITHUB_SHA"
```

---

## 拆解關鍵邏輯

### 1. 記錄 previous image

```bash
PREV_IMAGE=$(docker inspect my-app --format='{{.Config.Image}}' 2>/dev/null || echo "none")
```

- `docker inspect` 取得目前 container 使用的 image
- `2>/dev/null` 避免第一次部署時（container 不存在）報錯
- `|| echo "none"` fallback 值

### 2. Health check 判斷

```bash
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/health)
if [ "$HTTP_STATUS" != "200" ]; then
  # rollback
  exit 1
fi
```

- `-s` 靜默模式（不顯示進度）
- `-o /dev/null` 丟棄 body
- `-w "%{http_code}"` 只取 HTTP status code
- `exit 1` 讓 GitHub Actions 把這個 job 標記為失敗

### 3. Rollback

```bash
docker stop my-app && docker rm my-app
docker run -d --name my-app $PREV_IMAGE
```

回到上一個成功的 image tag（SHA），不是 latest。

---

## App 需要有 /health endpoint

Health check 要能打到 `/health`，app 要自己實作：

```javascript
// Node.js + Express 最簡範例
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok' });
});
```

---

## Job outputs 傳遞 SHA

如果 build 和 deploy 拆成兩個 job，用 `outputs` 傳遞：

```yaml
jobs:
  build:
    outputs:
      image-tag: ${{ steps.vars.outputs.sha }}
    steps:
      - id: vars
        run: echo "sha=${{ github.sha }}" >> $GITHUB_OUTPUT

  deploy:
    needs: build
    steps:
      - run: echo "Deploying ${{ needs.build.outputs.image-tag }}"
```

---

## 常見問題

**Q：deploy script 裡怎麼用 GitHub Actions 的環境變數？**
在 `appleboy/ssh-action` 的 `envs` 欄位列出要帶入的變數：
```yaml
envs: IMAGE_NAME,GITHUB_SHA
```
SSH session 裡就能直接用 `$IMAGE_NAME`、`$GITHUB_SHA`。

**Q：rollback 後 workflow 要標記成功還是失敗？**
標記失敗（`exit 1`）。面試時可以說：「部署失敗會自動 rollback，並在 GitHub Actions 顯示 failed，讓開發者知道需要修 code，不是靜默回滾。」

**Q：第一次部署沒有 PREV_IMAGE 怎麼辦？**
`PREV_IMAGE="none"` fallback，rollback 時判斷 `if [ "$PREV_IMAGE" != "none" ]`，跳過 rollback 只顯示錯誤訊息。
