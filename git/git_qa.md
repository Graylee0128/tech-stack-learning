# Git 核心概念 Q&A

> 整理自 2025-02-03 的實戰學習

---

## Q1: clone vs pull 有什麼區別？

### A:
- **git clone** = 第一次下載整個項目
  ```bash
  git clone https://github.com/Graylee0128/resume.git
  # ↓ 全新建立資料夾，下載所有代碼和歷史
  ```

- **git pull** = 更新已有項目的最新代碼
  ```bash
  cd existing-project
  git pull origin main
  # ↓ 同步 GitHub 上的最新更改
  ```

**記法：**
- Clone = 第一次複製
- Pull = 之後每次更新

---

## Q2: git status 的作用是什麼？

### A:
檢查你的項目當前狀態，顯示三種情況：

```
1. 未修改 (Untracked)
   └─ 新建的檔案，Git 還沒追蹤

2. 修改但未暫存 (Modified - 紅色)
   └─ my_resume.yaml
   └─ 你改了，但還沒 git add

3. 已暫存待提交 (Staged - 綠色)
   └─ company-website-poc/
   └─ 已 git add，等著 git commit
```

**實際例子：**
```bash
git status
# 看到 modified: my_resume.yaml
# ↓ 表示這個檔案改了，但還沒 add
```

---

## Q3: git add 和 git commit 的區別？

### A:
兩個不同的步驟，分別做不同的事：

### **git add** = 選擇要提交的檔案
```bash
git add my_resume.yaml      # 加入暫存區
git add -A                  # 全部加進去
```
**結果：** 檔案進入暫存區（Staging Area）

### **git commit** = 把暫存區的檔案打包成一個版本
```bash
git commit -m "Update AWS project description"
```
**結果：** 建立一個版本快照

### 時間線對比：
```
修改檔案
  ↓
git add -A          ← 選擇要提交的檔案
  ↓
暫存區
  ↓
git commit          ← 打包成一個版本
  ↓
本機 commit 歷史
  ↓
git push            ← 推到 GitHub
  ↓
GitHub 看得到！
```

**為什麼分開？**
- 可以分次提交不同的檔案
- commit 歷史更清楚
- 便於版本管理

---

## Q4: git remote 是做什麼的？

### A:
告訴 Git：你這個項目連接到哪個 GitHub 倉庫

```bash
git remote -v
# 輸出：
# origin  https://github.com/Graylee0128/resume.git (fetch)
# origin  https://github.com/Graylee0128/resume.git (push)
```

**解讀：**
- `origin` = 別名（預設就叫 origin）
- `https://...` = GitHub 的真實位址
- `fetch` = 拉代碼用這個位址
- `push` = 推代碼用這個位址

**實際用途：**
```bash
git push origin main
       ↑      ↑
    remote  分支名
# Git 用 remote 設定知道要推到哪個 GitHub 倉庫
```

---

## Q5: Ctrl+S 和 git add 有什麼區別？

### A:
**超重要的區別！**

### **Ctrl+S** = 存在你的電腦裡
```
你的硬碟：檔案已保存 ✓
GitHub：看不到 ❌
```

### **git add** = 告訴 Git 要提交這個檔案
```
你的硬碟：檔案已保存 ✓
Git 暫存區：已準備 ✓
GitHub：還看不到 ❌
```

### 完整流程：
```
你改了 my_resume.yaml
        ↓
Ctrl+S 存檔
        ↓
檔案保存在你的電腦 ✓
GitHub 還看不到 ❌
        ↓
git add my_resume.yaml
        ↓
Git 暫存區有了 ✓
GitHub 還看不到 ❌
        ↓
git commit -m "更新"
        ↓
Git 本機歷史有了 ✓
GitHub 還看不到 ❌
        ↓
git push origin main
        ↓
GitHub 終於看到了！✓✓✓
```

**簡單記法：**
```
Ctrl+S   = 存檔（個人用）
git add  = 上傳清單（告訴 Git 要送什麼）
git commit = 打包（保存一個版本）
git push = 寄出（送到 GitHub）
```

---

## Q6: push 和 fetch 一樣嗎？

### A:
**完全不一樣，方向相反！**

### **git push** = 送代碼到 GitHub（⬆️ 上傳）
```
你的電腦 → GitHub
git push origin main
```

### **git fetch** = 拿代碼從 GitHub（⬇️ 下載）
```
GitHub → 你的電腦
git fetch origin main
# 下載但不合併
```

### 圖示：
```
你的電腦                    GitHub
   ↓                          ↑
   │                          │
   └──── fetch ────→ 拿代碼過來

   ↑                          │
   │                          ↓
   └←──── push ─────← 送代碼過去
```

### **git pull** = fetch + 自動合併
```bash
git pull origin main
# = git fetch origin main + git merge
```

**簡單記法：**
- **Push** = 我要 **送** 給 GitHub（⬆️）
- **Fetch** = 我要 **拿** 從 GitHub（⬇️）
- **Pull** = 我要 **拿** + **用** GitHub 的（⬇️ + 合併）

---

## Q7: GitHub 上改了，我這邊也改了，應該用什麼？

### A:
**安全流程：先看情況，再決定**

### Step 1: 先看自己改了什麼
```bash
git diff
# 看你本機的修改內容
```

### Step 2: 再看 GitHub 改了什麼
```bash
git fetch origin main
# 拿下來但不合併（安全看看）
```

### Step 3: 決定怎麼處理

**情況 A：沒有衝突**
```bash
git pull origin main
# Git 會自動合併，完成！
```

**情況 B：有衝突（改同一行）**
```bash
git pull origin main
# ↓
# Git 會說：Conflict! 你和 GitHub 改同一個地方
# 需要手動選擇誰的版本

# 改好後：
git add .
git commit -m "Resolve conflict"
git push origin main
```

### 衝突標記（在檔案中）：
```
<<<<<<< HEAD
你的版本
=======
GitHub 的版本
>>>>>>> origin/main
```

**簡單記法：**
```
GitHub 改了 + 你也改了
      ↓
git diff   ← 先看自己改了什麼
git fetch  ← 再看 GitHub 改了什麼
git pull   ← 嘗試合併
      ↓
有衝突？→ 手動解決 → commit → push
沒衝突？→ 直接 push
```

---

## 今天的實戰流程

```bash
# 1. 檢查狀態
git status

# 2. 暫存所有修改
git add -A

# 3. 提交
git commit -m "Update AWS website migration PoC project achievements"

# 4. 推送到 GitHub
git push origin main

# 5. 驗證成功
git log --oneline -1
```

---

## 日常 3 件事

```bash
# 早上來：抓最新代碼
git pull origin main

# 幹活：改東西
# ... 改檔案 ...

# 下班前：推上去
git add -A
git commit -m "改了什麼"
git push origin main
```

---

## 常用查詢指令

```bash
# 看修改了什麼
git diff

# 看提交歷史
git log --oneline

# 看遠端資訊
git remote -v

# 檢查當前狀態
git status
```

---

**最後提醒：**
> 99% 時間 `git pull` 會自動搞定，只有改同一行才會衝突。
> 遇到問題時先 `git status` 看清楚，再決定下一步！
