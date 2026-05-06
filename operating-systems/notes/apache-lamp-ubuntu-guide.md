# Apache / LAMP 實戰教學 — Ubuntu 現代版

> 本文改寫自鳥哥 Linux 私房菜《WWW 伺服器》章節。原文基於 CentOS 6 + Apache 2.2，本版改寫為 **Ubuntu 24.04 LTS + Apache 2.4**，保留知識脈絡，全面替換為現行可直接操作的流程。

---

## 目錄

0. [本文範圍與版本基準](#0-本文範圍與版本基準)
1. [時代差異速覽：CentOS 6 vs. Ubuntu 現行做法](#1-時代差異速覽centos-6-vs-ubuntu-現行做法)
2. [LAMP 安裝](#2-lamp-安裝)
3. [Apache 目錄結構（Ubuntu 版）](#3-apache-目錄結構ubuntu-版)
4. [Apache 基本設定（2.4 語法）](#4-apache-基本設定24-語法)
5. [PHP 安裝與驗證](#5-php-安裝與驗證)
6. [MySQL 安裝與驗證](#6-mysql-安裝與驗證)
7. [防火牆設定（ufw）](#7-防火牆設定ufw)
8. [HTTPS：Let's Encrypt / Certbot](#8-httpslets-encrypt--certbot)
9. [虛擬主機（Virtual Host）](#9-虛擬主機virtual-host)
10. [常用排錯與驗收清單](#10-常用排錯與驗收清單)
11. [附錄：本次不整理的舊內容](#11-附錄本次不整理的舊內容)
12. [參考資料](#12-參考資料)

---

## 0. 本文範圍與版本基準

本文以 **Ubuntu 24.04 LTS + Apache 2.4 + MySQL 8.x + Ubuntu 套件庫提供的 PHP 版本**為主要基準。Ubuntu 22.04 LTS 也大致適用，但 PHP 版號、部分套件預設值可能不同。

實作時請先確認自己的系統版本：

```bash
lsb_release -a
apache2 -v
php -v
mysql --version
```

本文目標是讓你完成一台可練習、可延伸到正式站台的 LAMP 主機：

- Apache 能服務靜態頁面
- PHP 能透過 Apache 正常執行
- PHP 能連上 MySQL
- 可建立多個 Virtual Host
- 可用 HTTPS 對外服務
- 遇到常見錯誤時知道從哪裡查

> **版本提醒：** 教學中的 `php8.x` 請依你的實際版本替換。不要硬背 `php8.3`；先用 `php -v` 或 `ls /etc/apache2/mods-available/php*.load` 查出本機版本。

---

## 1. 時代差異速覽：CentOS 6 vs. Ubuntu 現行做法

在照著舊教學操作之前，先搞清楚哪些東西已經換了，可以省掉大量除錯時間。

| 項目 | 鳥哥原文（CentOS 6 / Apache 2.2） | 現行做法（Ubuntu LTS / Apache 2.4） |
|------|-------------------------------------|---------------------------------------|
| 套件管理 | `yum install httpd` | `apt install apache2` |
| 服務管理 | `service httpd start`、`chkconfig httpd on` | `systemctl start apache2`、`systemctl enable apache2` |
| 主設定目錄 | `/etc/httpd/` | `/etc/apache2/` |
| 主設定檔 | `/etc/httpd/conf/httpd.conf`（單一大檔） | `/etc/apache2/apache2.conf` + 拆分檔案 |
| 站台設定 | 直接寫在 `httpd.conf` 或 `conf.d/*.conf` | `sites-available/*.conf` + `a2ensite` 啟用 |
| 模組管理 | `LoadModule` 直接寫在設定檔 | `mods-available/` + `a2enmod` 啟用 |
| 存取控制語法 | `Order Allow,Deny` / `Allow from all` | `Require all granted` / `Require ip ...` |
| 虛擬主機指令 | 需要 `NameVirtualHost *:80` | **已移除**，不需要也不能寫 |
| 網頁根目錄 | `/var/www/html` | `/var/www/html`（一樣） |
| 防火牆 | `iptables` + SELinux | `ufw`（AppArmor 通常不需額外設定） |
| PHP 模組 | `yum install php` → 自動載入 | `apt install libapache2-mod-php` |
| MySQL | `yum install mysql-server` → `service mysqld start` | `apt install mysql-server` → `systemctl start mysql` |

> **一句話總結：** 套件名、設定路徑、存取控制語法、服務指令全部不同。只有網頁根目錄 `/var/www/html` 沒變。

---

## 2. LAMP 安裝

LAMP = **L**inux + **A**pache + **M**ySQL + **P**HP。Ubuntu 上一次裝完：

```bash
# 更新套件清單
sudo apt update

# 安裝 Apache
sudo apt install -y apache2

# 安裝 PHP 與 Apache PHP 模組
sudo apt install -y php libapache2-mod-php

# 安裝 MySQL
sudo apt install -y mysql-server

# 安裝 PHP 的 MySQL 擴充（讓 PHP 能連 MySQL）
sudo apt install -y php-mysql
```

安裝完畢後確認服務狀態：

```bash
# Apache
systemctl status apache2

# MySQL
systemctl status mysql
```

在一般 Ubuntu Server 環境中，這兩個服務安裝後通常會自動啟動並設為開機啟用。若你的環境沒有自動啟動，可手動補上：

```bash
sudo systemctl enable --now apache2
sudo systemctl enable --now mysql
```

**快速驗證 Apache：** 瀏覽器開 `http://<你的 IP>`，看到 Ubuntu 的 Apache2 預設頁面就表示成功。或用 CLI：

```bash
curl -s http://localhost | head -5
```

**本章驗收：**

- `systemctl status apache2` 顯示 `active (running)`
- `systemctl status mysql` 顯示 `active (running)`
- `curl -I http://localhost` 回傳 `HTTP/1.1 200 OK`

---

## 3. Apache 目錄結構（Ubuntu 版）

Ubuntu 的 Apache 採用**模組化拆分結構**，和 CentOS 的「一個 `httpd.conf` 搞定一切」完全不同。理解這個結構是後續所有操作的基礎。

```
/etc/apache2/
├── apache2.conf          # 主設定檔（全域設定、Include 其他檔案）
├── ports.conf            # 監聽的 port（預設 Listen 80）
├── envvars               # 環境變數（APACHE_RUN_USER 等）
│
├── sites-available/      # 所有站台設定檔（放這裡不代表啟用）
│   ├── 000-default.conf  # 預設站台
│   └── mysite.conf       # 你自己建的站台
│
├── sites-enabled/        # 啟用的站台（symlink → sites-available）
│   └── 000-default.conf → ../sites-available/000-default.conf
│
├── mods-available/       # 所有可用模組的設定
├── mods-enabled/         # 啟用的模組（symlink → mods-available）
│
├── conf-available/       # 額外設定片段
└── conf-enabled/         # 啟用的額外設定（symlink）
```

### 關鍵觀念

| 觀念 | 說明 |
|------|------|
| `*-available` vs `*-enabled` | `available` 是「存在但未啟用」，`enabled` 是「正在使用」。啟用靠 symlink，不要手動 ln，用指令操作 |
| `a2ensite` / `a2dissite` | 啟用 / 停用站台設定 |
| `a2enmod` / `a2dismod` | 啟用 / 停用模組 |
| `a2enconf` / `a2disconf` | 啟用 / 停用額外設定片段 |

```bash
# 啟用站台
sudo a2ensite mysite.conf

# 停用預設站台
sudo a2dissite 000-default.conf

# 啟用 rewrite 模組
sudo a2enmod rewrite

# 改完設定後，先測試語法再 reload
sudo apache2ctl configtest
sudo systemctl reload apache2
```

> **⚠ 舊習慣注意：** CentOS 上改完 `httpd.conf` 直接 `service httpd restart`。Ubuntu 上應該用 `systemctl reload apache2`（reload 不中斷連線），只有改模組才需要 `restart`。

### 網頁根目錄

預設網頁根目錄是 `/var/www/html`，和 CentOS 一樣。

```bash
ls /var/www/html/
# index.html  ← Apache 預設歡迎頁
```

### 權限觀念：練習環境 vs. 正式環境

練習時常會把整個站台目錄交給 Apache 使用者：

```bash
sudo chown -R www-data:www-data /var/www/mysite
```

這樣操作簡單，但正式環境不建議讓 Apache 對整個站台都有寫入權限。較穩妥的做法是：

- 程式碼與靜態檔案由部署使用者擁有
- Apache 使用者 `www-data` 只需要讀取權限
- 只有上傳目錄、快取目錄、session 目錄等需要寫入的位置，才另外給 `www-data` 寫入權限

範例：

```bash
# 程式碼由部署使用者擁有；deploy 請換成你的部署帳號
sudo chown -R deploy:www-data /var/www/mysite

# 目錄 755、檔案 644：Apache 可讀，不能任意改
sudo find /var/www/mysite -type d -exec chmod 755 {} \;
sudo find /var/www/mysite -type f -exec chmod 644 {} \;

# 只有 uploads 允許 Apache 寫入
sudo mkdir -p /var/www/mysite/uploads
sudo chown -R www-data:www-data /var/www/mysite/uploads
sudo chmod 755 /var/www/mysite/uploads
```

---

## 4. Apache 基本設定（2.4 語法）

### 4.1 存取控制：告別 Order/Allow/Deny

Apache 2.4 最大的語法改變就是存取控制。鳥哥原文大量使用的 `Order`、`Allow`、`Deny` 在 2.4 中已被 `Require` 指令取代。

| 舊語法（2.2） | 新語法（2.4） | 意思 |
|---------------|--------------|------|
| `Order allow,deny` + `Allow from all` | `Require all granted` | 允許所有人存取 |
| `Order deny,allow` + `Deny from all` | `Require all denied` | 拒絕所有人存取 |
| `Allow from 192.168.1.0/24` | `Require ip 192.168.1.0/24` | 只允許特定網段 |
| `Allow from .example.com` | `Require host example.com` | 只允許特定主機 |

**完整範例：** 設定 `/var/www/html` 允許所有人存取

```apache
# 舊寫法（Apache 2.2）— 不要用
<Directory /var/www/html>
    Order allow,deny
    Allow from all
</Directory>

# 新寫法（Apache 2.4）— 用這個
<Directory /var/www/html>
    Require all granted
</Directory>
```

**組合條件範例：** 只允許內網 + 特定外部 IP

```apache
<Directory /var/www/internal>
    <RequireAny>
        Require ip 192.168.1.0/24
        Require ip 203.0.113.50
    </RequireAny>
</Directory>
```

### 4.2 主設定檔重點欄位

Ubuntu 的 `apache2.conf` 已經把大部分設定拆到子檔案，主檔主要負責全域行為：

```bash
# 查看主設定檔（重點段落）
grep -v '^\s*#' /etc/apache2/apache2.conf | grep -v '^$'
```

常見需要調整的欄位：

```apache
# 伺服器名稱（避免啟動時的 FQDN 警告）
# 在 apache2.conf 或另建 conf-available/servername.conf
ServerName localhost

# 全域安全設定：禁止列出目錄內容
<Directory /var/www/>
    Options -Indexes +FollowSymLinks
    AllowOverride None
    Require all granted
</Directory>
```

> **Options 說明：**
> - `-Indexes`：目錄下沒有 index 檔時，不要列出檔案清單（安全考量）
> - `+FollowSymLinks`：允許使用 symlink（Apache 效能需要）

### 4.3 監聽 Port

```bash
cat /etc/apache2/ports.conf
```

```apache
Listen 80

<IfModule ssl_module>
    Listen 443
</IfModule>
```

如果要改 port（例如改為 8080）：

```bash
sudo sed -i 's/Listen 80/Listen 8080/' /etc/apache2/ports.conf
sudo systemctl reload apache2
```

> **提醒：** 如果站台已經上線，改 port 前要同步檢查防火牆、反向代理、DNS 或雲端安全群組。練習環境可以直接改，正式環境建議先備份設定檔。

### 4.4 設定檢查流程

**每次改完設定，養成這個習慣：**

```bash
# 1. 語法檢查
sudo apache2ctl configtest
# 看到 "Syntax OK" 才繼續

# 2. 套用設定
sudo systemctl reload apache2

# 3. 確認服務正常
systemctl status apache2
```

### 4.5 基礎安全設定

Apache 預設會在部分回應或錯誤頁透露伺服器版本。這不是最嚴重的風險，但正式站台通常會降低資訊暴露：

```bash
sudo tee /etc/apache2/conf-available/security-hardening.conf <<'EOF'
ServerTokens Prod
ServerSignature Off
EOF

sudo a2enconf security-hardening.conf
sudo apache2ctl configtest
sudo systemctl reload apache2
```

搭配前面提到的目錄設定：

```apache
<Directory /var/www/>
    Options -Indexes +FollowSymLinks
    AllowOverride None
    Require all granted
</Directory>
```

這組設定的效果是：

- 不在 HTTP header 或錯誤頁主動顯示詳細 Apache 版本
- 目錄沒有 index 檔時，不列出檔案清單
- 預設不允許 `.htaccess` 覆蓋主設定，避免設定散落難查

---

## 5. PHP 安裝與驗證

安裝已在第 2 節完成。這裡做功能驗證。

### 5.1 確認 PHP 模組已載入

```bash
# 查看已載入的 Apache 模組
apache2ctl -M | grep php

# 預期輸出類似：
#  php8.x_module (shared)
```

如果沒有載入：

```bash
# 先查出可用的 PHP Apache 模組
ls /etc/apache2/mods-available/php*.load

# 例如看到 php8.3.load，就啟用 php8.3；版號依你的環境調整
sudo a2enmod php8.3
sudo systemctl restart apache2
```

### 5.2 phpinfo() 測試頁

```bash
# 建立測試頁
echo '<?php phpinfo(); ?>' | sudo tee /var/www/html/info.php
```

瀏覽器開 `http://<你的 IP>/info.php`，看到 PHP 資訊頁就表示 Apache 能正確解析 PHP。

```bash
# CLI 驗證
curl -s http://localhost/info.php | head -3
```

> **⚠ 安全提醒：** `phpinfo()` 會洩漏伺服器完整資訊。測試完畢後務必刪除：
> ```bash
> sudo rm /var/www/html/info.php
> ```

### 5.3 常用 PHP 擴充

根據需求安裝額外擴充：

```bash
# 常見擴充
sudo apt install -y php-curl php-gd php-mbstring php-xml php-zip

# 安裝後重啟 Apache
sudo systemctl restart apache2
```

**本章驗收：**

- `apache2ctl -M | grep php` 看得到 PHP 模組
- `curl -s http://localhost/info.php | grep -i php` 能看到 PHP 輸出
- 測試完已刪除 `/var/www/html/info.php`

---

## 6. MySQL 安裝與驗證

### 6.1 安裝後狀態確認

```bash
systemctl status mysql
```

### 6.2 登入測試

Ubuntu 上 MySQL 安裝後，root 帳號預設使用 `auth_socket` 認證（用系統使用者身份登入），不需要密碼：

```bash
# 用 sudo 以 root 身份登入
sudo mysql
```

```sql
-- 確認版本
SELECT VERSION();

-- 查看資料庫
SHOW DATABASES;

-- 離開
EXIT;
```

> **⚠ 和舊版的差異：**
> 鳥哥原文中 CentOS 的 MySQL 安裝後常會先執行 `mysql_secure_installation` 設定 root 密碼。Ubuntu 上的 MySQL 8.x 預設用 `auth_socket`，`sudo mysql` 就能登入，不需要（也不建議新手一開始就）把 root 改成密碼認證。
>
> 但 `mysql_secure_installation` 仍可用來移除匿名使用者、測試資料庫、限制遠端 root 登入等。正式環境可以執行，只是不要把它理解成「一定要替 root 設密碼」。

### 6.3 建立應用程式用的帳號（建議做法）

不要讓應用程式用 root 連資料庫。建一個專用帳號：

```bash
sudo mysql
```

```sql
-- 建立帳號，用密碼認證；請換成自己的強密碼
CREATE USER 'webuser'@'localhost' IDENTIFIED BY 'YourStrongPassword123!';

-- 建立資料庫
CREATE DATABASE mywebdb;

-- 練習環境可先給該資料庫完整權限
GRANT ALL PRIVILEGES ON mywebdb.* TO 'webuser'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

正式環境應依應用程式需求縮小權限。例如只需要讀寫資料，不需要改 schema 時，就不要給 `ALTER`、`DROP` 這類高風險權限。

驗證新帳號可以登入：

```bash
mysql -u webuser -p mywebdb
# 輸入密碼後應能成功進入
```

### 6.4 PHP 連 MySQL 驗證

建立測試腳本確認 PHP 能連上 MySQL：

```bash
cat <<'EOF' | sudo tee /var/www/html/dbtest.php
<?php
$conn = new mysqli('localhost', 'webuser', 'YourStrongPassword123!', 'mywebdb');
if ($conn->connect_error) {
    die('Connection failed: ' . $conn->connect_error);
}
echo 'MySQL connection OK. Server version: ' . $conn->server_info;
$conn->close();
?>
EOF
```

瀏覽器開 `http://<你的 IP>/dbtest.php`，看到版本資訊就表示 PHP ↔ MySQL 連線正常。

> **⚠ 測試完刪掉：**
> ```bash
> sudo rm /var/www/html/dbtest.php
> ```
>
> 這個範例為了教學直接把密碼寫在測試檔裡，正式站台不要這樣做。正式應用程式應把資料庫密碼放在 webroot 之外的設定檔、環境變數，或由部署工具/Secret Manager 注入。

**本章驗收：**

- `sudo mysql` 可以登入
- `mysql -u webuser -p mywebdb` 可以用應用帳號登入
- `http://<你的 IP>/dbtest.php` 能顯示 MySQL 版本
- 測試完已刪除 `/var/www/html/dbtest.php`

---

## 7. 防火牆設定（ufw）

Ubuntu 預設使用 `ufw`（Uncomplicated Firewall）。鳥哥原文的 `iptables` 規則在 Ubuntu 上不需要手寫。

### 7.1 確認 ufw 狀態

```bash
sudo ufw status
```

如果顯示 `inactive`，先啟用（**確保 SSH port 已放行再啟用，否則會斷線**）：

```bash
sudo ufw allow OpenSSH
sudo ufw enable
```

### 7.2 放行 Apache

```bash
# 只放 HTTP (80)
sudo ufw allow 'Apache'

# 或放 HTTP + HTTPS (80 + 443)
sudo ufw allow 'Apache Full'
```

查看可用的應用程式 profile：

```bash
sudo ufw app list
# Available applications:
#   Apache
#   Apache Full
#   Apache Secure
#   OpenSSH
```

### 7.3 驗證

```bash
sudo ufw status verbose
```

預期看到：

```
80/tcp (Apache)                ALLOW IN    Anywhere
22/tcp (OpenSSH)               ALLOW IN    Anywhere
```

> **⚠ SELinux vs. AppArmor：**
> 鳥哥原文花了不少篇幅講 SELinux 對 Apache 的影響。Ubuntu 用的是 AppArmor，對 Apache 的預設 profile 通常不需要額外調整。如果遇到權限問題，先檢查檔案的 Linux 檔案權限（`ls -la`、`chown`），再考慮 AppArmor。

---

## 8. HTTPS：Let's Encrypt / Certbot

正式對外網站應該使用 HTTPS。現在最常見的做法是用 Let's Encrypt 簽發免費憑證，再用 Certbot 自動修改 Apache 設定與處理續期。

### 8.1 事前條件

在執行 Certbot 之前，先確認：

- 你有一個真實網域，例如 `example.com`
- DNS A/AAAA record 已指向這台伺服器
- Apache 已能用 HTTP 回應該網域
- 防火牆已放行 80 與 443
- Virtual Host 裡有正確的 `ServerName`

```bash
# 防火牆放行 HTTP + HTTPS
sudo ufw allow 'Apache Full'

# 確認網域目前能打到這台 Apache
curl -I http://example.com
```

### 8.2 安裝 Certbot

Certbot 官方目前較推薦使用 snap 安裝。Ubuntu Server 通常已內建 snapd；若沒有，先安裝：

```bash
sudo apt update
sudo apt install -y snapd
```

安裝 Certbot：

```bash
sudo snap install core
sudo snap refresh core

# 如果曾用 apt 裝過 certbot，先移除舊套件，避免指令混淆
sudo apt remove -y certbot

sudo snap install --classic certbot
sudo ln -sf /snap/bin/certbot /usr/bin/certbot
```

### 8.3 替 Apache 站台簽發憑證

假設你的站台是：

- `example.com`
- `www.example.com`

執行：

```bash
sudo certbot --apache -d example.com -d www.example.com
```

Certbot 會檢查 Apache 設定、申請憑證，並可協助你把 HTTP 轉到 HTTPS。完成後測試：

```bash
curl -I https://example.com
sudo apache2ctl configtest
```

### 8.4 自動續期

Certbot 會安裝自動續期機制。你可以用 dry run 確認續期流程可正常執行：

```bash
sudo certbot renew --dry-run
systemctl list-timers | grep certbot
```

常用查看指令：

```bash
# 查看目前憑證
sudo certbot certificates

# 手動重新載入 Apache
sudo systemctl reload apache2
```

**本章驗收：**

- `https://example.com` 可正常開啟
- `curl -I https://example.com` 回傳 `HTTP/2 200` 或 `HTTP/1.1 200 OK`
- `sudo certbot renew --dry-run` 成功
- `sudo ufw status` 看得到 80/443 已放行

---

## 9. 虛擬主機（Virtual Host）

虛擬主機讓一台伺服器用不同的 `ServerName` 服務多個網站。這是 Apache 最常用的功能之一。

### 9.1 觀念

| 觀念 | 說明 |
|------|------|
| Name-based Virtual Host | 同一個 IP、同一個 port，靠 HTTP `Host` header 區分不同站台 |
| `NameVirtualHost` 指令 | **Apache 2.4 已移除**，不要寫也不能寫 |
| 設定位置 | Ubuntu 上放在 `sites-available/`，用 `a2ensite` 啟用 |

### 9.2 範例：建立兩個站台

**目標：**
- `site-a.local` → 顯示 "Welcome to Site A"
- `site-b.local` → 顯示 "Welcome to Site B"

#### Step 1：建立網頁目錄與內容

```bash
# Site A
sudo mkdir -p /var/www/site-a
echo '<h1>Welcome to Site A</h1>' | sudo tee /var/www/site-a/index.html

# Site B
sudo mkdir -p /var/www/site-b
echo '<h1>Welcome to Site B</h1>' | sudo tee /var/www/site-b/index.html

# 設定擁有者
sudo chown -R www-data:www-data /var/www/site-a /var/www/site-b
```

#### Step 2：建立站台設定檔

```bash
# Site A
sudo tee /etc/apache2/sites-available/site-a.conf <<'EOF'
<VirtualHost *:80>
    ServerName site-a.local
    DocumentRoot /var/www/site-a

    <Directory /var/www/site-a>
        Require all granted
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/site-a-error.log
    CustomLog ${APACHE_LOG_DIR}/site-a-access.log combined
</VirtualHost>
EOF

# Site B
sudo tee /etc/apache2/sites-available/site-b.conf <<'EOF'
<VirtualHost *:80>
    ServerName site-b.local
    DocumentRoot /var/www/site-b

    <Directory /var/www/site-b>
        Require all granted
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/site-b-error.log
    CustomLog ${APACHE_LOG_DIR}/site-b-access.log combined
</VirtualHost>
EOF
```

#### Step 3：啟用站台並套用

```bash
# 啟用兩個站台
sudo a2ensite site-a.conf
sudo a2ensite site-b.conf

# （可選）停用預設站台，避免干擾
sudo a2dissite 000-default.conf

# 語法檢查
sudo apache2ctl configtest

# 套用
sudo systemctl reload apache2
```

#### Step 4：驗證

**方法 A：修改本機 hosts 檔（適合練習機）**

```bash
# Linux/macOS
echo '127.0.0.1 site-a.local site-b.local' | sudo tee -a /etc/hosts

# 測試
curl http://site-a.local
# <h1>Welcome to Site A</h1>

curl http://site-b.local
# <h1>Welcome to Site B</h1>
```

**方法 B：用 curl 指定 Host header（不改 hosts）**

```bash
curl -H 'Host: site-a.local' http://localhost
# <h1>Welcome to Site A</h1>

curl -H 'Host: site-b.local' http://localhost
# <h1>Welcome to Site B</h1>
```

兩個結果不同，就表示虛擬主機設定成功。

### 9.3 常見問題排查

| 問題 | 檢查方式 |
|------|---------|
| 所有站台都顯示同一個頁面 | `apache2ctl -S` 看虛擬主機列表，確認 ServerName 有沒有正確對應 |
| 403 Forbidden | 檢查 `<Directory>` 有沒有 `Require all granted`，以及檔案權限 `ls -la` |
| 站台沒生效 | 確認有 `a2ensite` 啟用 + `systemctl reload apache2` |
| `configtest` 報 FQDN 警告 | 在 `apache2.conf` 加上 `ServerName localhost`（不影響功能但可消除警告） |

```bash
# 查看目前所有虛擬主機的對應關係
sudo apache2ctl -S
```

---

## 10. 常用排錯與驗收清單

LAMP 出問題時，不要只盯著瀏覽器畫面。先把問題拆成「服務是否活著、port 是否有聽、Apache 設定是否正確、PHP 是否有解析、MySQL 是否能登入」。

### 10.1 Apache 排錯

```bash
# 服務狀態
systemctl status apache2

# 最近的 systemd log
journalctl -u apache2 -n 80 --no-pager

# Apache 錯誤 log
sudo tail -f /var/log/apache2/error.log

# 檢查設定語法
sudo apache2ctl configtest

# 查看目前 Virtual Host 對應
sudo apache2ctl -S

# 查看目前載入模組
apache2ctl -M
```

### 10.2 Port 與網路排錯

```bash
# 看 Apache 是否真的在聽 80 / 443
sudo ss -tulpn | grep -E ':80|:443'

# 從本機測 HTTP header
curl -I http://localhost

# 測指定 Host header，不需要改 hosts
curl -I -H 'Host: site-a.local' http://localhost

# 防火牆狀態
sudo ufw status verbose
```

### 10.3 PHP / MySQL 排錯

```bash
# PHP CLI 版本
php -v

# Apache 是否載入 PHP 模組
apache2ctl -M | grep php

# MySQL 服務狀態
systemctl status mysql

# MySQL root socket 登入
sudo mysql

# 應用帳號登入
mysql -u webuser -p mywebdb
```

### 10.4 完整驗收清單

完成本文流程後，至少應確認：

- `curl -I http://localhost` 可回應
- `apache2ctl configtest` 顯示 `Syntax OK`
- `apache2ctl -S` 看得到你的 Virtual Host
- PHP 測試頁可執行，並已刪除測試頁
- MySQL 應用帳號可登入指定資料庫
- PHP 可成功連上 MySQL，並已刪除 `dbtest.php`
- `sudo ufw status` 已放行需要的服務
- 若是正式網域，`https://你的網域` 可正常開啟
- `sudo certbot renew --dry-run` 成功

---

## 11. 附錄：本次不整理的舊內容

以下是鳥哥原文涵蓋、但本教學**刻意跳過或只一句帶過**的內容，附上簡要說明：

| 舊內容 | 為什麼跳過 | 現代替代方案（一句話） |
|--------|-----------|----------------------|
| CGI 程式執行 | 現代 Web 開發幾乎不用 CGI | 用 PHP / Python WSGI / Node.js |
| 個人首頁 `~username` | 多人共用主機的場景已少見 | 如需要：`a2enmod userdir` |
| eAccelerator（PHP 加速器） | 已停止維護 | PHP 7+ 內建 OPcache，`apt install php-opcache` |
| webalizer / awstats（流量分析） | 已被現代工具取代 | GoAccess、Matomo、Google Analytics |
| 舊式 SSL（mod_ssl 手動設定） | 手動產生與維護憑證太繁瑣 | 正式上線用 `certbot`（Let's Encrypt）自動設定 |
| 自製防砍站腳本 | 原文用 shell script 分析 log 封 IP | 用 `fail2ban` 套件，設定更簡單也更可靠 |
| SELinux 設定 | Ubuntu 不用 SELinux | Ubuntu 用 AppArmor，通常不需額外設定 |
| `NameVirtualHost` 指令 | Apache 2.4 已移除 | 直接寫 `<VirtualHost *:80>` 即可 |

---

## 12. 參考資料

- Ubuntu Server documentation: [How to install Apache2](https://documentation.ubuntu.com/server/how-to/web-services/install-apache2/index.html)
- Ubuntu Server documentation: [How to install and configure PHP](https://documentation.ubuntu.com/server/how-to/web-services/install-php/index.html)
- Ubuntu Server documentation: [Firewall](https://ubuntu.com/server/docs/how-to/security/firewalls/)
- Ubuntu Security documentation: [Apache2 version banners](https://documentation.ubuntu.com/security/security-features/network/version-banners/apache2/)
- Certbot official instructions: [Apache on Linux with snap](https://certbot.eff.org/instructions?os=snap&tab=standard&ws=apache)

---

## 快速參考卡

```bash
# === 服務管理 ===
sudo systemctl start apache2
sudo systemctl stop apache2
sudo systemctl restart apache2     # 改模組後用
sudo systemctl reload apache2      # 改設定後用（不斷線）
sudo systemctl status apache2

# === 站台管理 ===
sudo a2ensite mysite.conf          # 啟用站台
sudo a2dissite mysite.conf         # 停用站台

# === 模組管理 ===
sudo a2enmod rewrite               # 啟用模組
sudo a2dismod rewrite              # 停用模組
apache2ctl -M                      # 列出已載入模組

# === 設定檢查 ===
sudo apache2ctl configtest         # 語法檢查
sudo apache2ctl -S                 # 虛擬主機對應表

# === Log ===
sudo tail -f /var/log/apache2/error.log
sudo tail -f /var/log/apache2/access.log

# === 防火牆 ===
sudo ufw allow 'Apache Full'
sudo ufw status verbose

# === HTTPS / Certbot ===
sudo certbot --apache -d example.com -d www.example.com
sudo certbot certificates
sudo certbot renew --dry-run

# === MySQL ===
sudo mysql
mysql -u webuser -p mywebdb
```
