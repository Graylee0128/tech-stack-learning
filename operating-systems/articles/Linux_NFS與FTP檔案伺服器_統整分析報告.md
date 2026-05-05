# Linux 檔案伺服器：NFS 與 FTP (vsftpd) 統整分析報告

> 來源：鳥哥的 Linux 私房菜 — NFS 伺服器 & FTP 伺服器 (vsftpd)  
> 統整日期：2026-05-04

---

## 目錄

- [一、核心概念對比](#一核心概念對比)
- [二、NFS 伺服器](#二nfs-伺服器)
  - [2.1 運作原理與架構](#21-運作原理與架構)
  - [2.2 RPC 機制](#22-rpc-機制)
  - [2.3 Server 端設定](#23-server-端設定)
  - [2.4 Client 端設定](#24-client-端設定)
  - [2.5 安全性與效能調校](#25-安全性與效能調校)
- [三、FTP 伺服器 (vsftpd)](#三ftp-伺服器-vsftpd)
  - [3.1 FTP 運作原理](#31-ftp-運作原理)
  - [3.2 vsftpd 架構與設定](#32-vsftpd-架構與設定)
  - [3.3 實體帳號設定](#33-實體帳號設定)
  - [3.4 匿名登入設定](#34-匿名登入設定)
  - [3.5 SSL/TLS 加密](#35-ssltls-加密)
  - [3.6 防火牆與安全性](#36-防火牆與安全性)
- [四、選型決策指南](#四選型決策指南)
- [五、常見問題排錯](#五常見問題排錯)

---

## 一、核心概念對比

| 面向 | NFS | FTP (vsftpd) |
|------|-----|--------------|
| **全名** | Network FileSystem | File Transfer Protocol |
| **用途** | 網路檔案系統共享（掛載遠端目錄如本地磁碟） | 檔案上傳/下載傳輸 |
| **傳輸方式** | 透明掛載，如操作本地檔案系統 | 明確的上傳/下載操作 |
| **協定層級** | 基於 RPC，port 111 (rpcbind) + port 2049 (nfs) + 隨機埠 | TCP，port 21 (命令) + port 20 (主動資料) 或隨機埠 (被動) |
| **認證方式** | 基於 UID/GID（無帳密驗證） | 帳號密碼（PAM 模組） |
| **加密** | 無（明碼） | 預設明碼，可啟用 FTPS (SSL/TLS) |
| **適用場景** | Unix/Linux 主機間、Cluster、內網共享 | 對外提供下載、跨平台檔案傳輸 |
| **替代方案** | SAMBA (跨平台)、GlusterFS | SFTP (SSH)、SCP、rsync |

---

## 二、NFS 伺服器

### 2.1 運作原理與架構

```
┌─────────────┐         ┌─────────────────────────────────────────┐
│  NFS Client │         │           NFS Server                     │
│             │         │                                          │
│ /home/nfs/  │◄───────►│  rpcbind (port 111)                      │
│ public/     │  mount  │  rpc.nfsd (port 2049) ← 認證登入         │
│ (掛載點)    │         │  rpc.mountd (隨機port) ← 檔案權限管理    │
│             │         │  rpc.lockd (選用) ← 檔案鎖定             │
│             │         │  rpc.statd (選用) ← 檔案一致性           │
└─────────────┘         └─────────────────────────────────────────┘
```

**核心概念**：NFS Client 將遠端目錄掛載到本地掛載點，之後可像使用本地磁碟一樣操作（cp, mv, rm 等指令全部適用）。

### 2.2 RPC 機制

- **為什麼需要 RPC？** NFS 各 daemon 使用隨機埠口，Client 無法得知要連哪個 port
- **RPC 角色**：rpcbind 固定監聽 port 111，NFS daemon 啟動時向 RPC 註冊埠口
- **連線流程**：
  1. Client → rpcbind (port 111)：查詢 NFS 功能對應的埠口
  2. rpcbind → Client：回報正確埠口
  3. Client → NFS daemon (正確埠口)：開始檔案操作

> **關鍵**：先啟動 rpcbind，再啟動 nfs。若 rpcbind 重啟，所有 RPC 服務都要重啟重新註冊。

### 2.3 Server 端設定

#### 必要軟體

| 軟體 | 功能 |
|------|------|
| `rpcbind` | RPC 主程式，port mapping |
| `nfs-utils` | 提供 rpc.nfsd, rpc.mountd 等 daemon |

#### /etc/exports 語法

```bash
[分享目錄]   [主機1(權限參數)]   [主機2(權限參數)]   ...
```

**主機指定方式**：
- 完整 IP：`192.168.100.10`
- 網段：`192.168.100.0/24` 或 `192.168.100.0/255.255.255.0`
- 主機名稱：`client.example.com`
- 萬用字元：`*.centos.vbird`、`*`

**權限參數**：

| 參數 | 說明 |
|------|------|
| `rw` / `ro` | 可讀寫 / 唯讀 |
| `sync` / `async` | 同步寫入硬碟 / 先暫存記憶體 |
| `root_squash` | 壓縮 Client root 為 nfsnobody（**預設**） |
| `no_root_squash` | 保留 Client root 權限 |
| `all_squash` | 壓縮所有使用者為匿名者 |
| `anonuid=N` | 匿名者的 UID |
| `anongid=N` | 匿名者的 GID |

#### 設定範例

```bash
# /etc/exports
/tmp          *(rw,no_root_squash)
/home/public  192.168.100.0/24(rw)    *(ro)
/home/test    192.168.100.10(rw)
/home/linux   *.centos.vbird(rw,all_squash,anonuid=45,anongid=45)
```

#### 啟動與管理

```bash
# 啟動服務
/etc/init.d/rpcbind start
/etc/init.d/nfs start
/etc/init.d/nfslock start

# 設定開機自動啟動
chkconfig rpcbind on
chkconfig nfs on
chkconfig nfslock on

# 檢視 RPC 註冊狀態
rpcinfo -p localhost

# 修改 /etc/exports 後免重啟
exportfs -arv    # 重新載入分享目錄
exportfs -auv    # 卸載所有分享

# 觀察分享狀態
showmount -e localhost
cat /var/lib/nfs/etab    # 完整權限設定值
```

### 2.4 Client 端設定

#### 手動掛載

```bash
# 1. 啟動 rpcbind
/etc/init.d/rpcbind start

# 2. 查詢可用目錄
showmount -e 192.168.100.254

# 3. 建立掛載點並掛載
mkdir -p /home/nfs/public
mount -t nfs 192.168.100.254:/home/public /home/nfs/public

# 4. 安全掛載（推薦）
mount -t nfs -o nosuid,noexec,nodev,rw 192.168.100.254:/home/public /home/nfs/public

# 5. 卸載
umount /home/nfs/public
```

#### 效能調校參數

| 參數 | 說明 | 推薦值 |
|------|------|--------|
| `bg` | 背景掛載，網路不穩時不阻塞前景 | bg |
| `soft` | timeout 後重複呼叫而非持續呼叫 | soft（一般場景） |
| `hard` | 持續呼叫直到恢復（cluster 場景需要） | hard + intr |
| `intr` | hard 模式下允許中斷 | 搭配 hard 使用 |
| `rsize` / `wsize` | 讀寫 block size (bytes) | 32768 (LAN 環境) |

```bash
# 高效能掛載範例
mount -t nfs -o nosuid,noexec,nodev,rw,bg,soft,rsize=32768,wsize=32768 \
  192.168.100.254:/home/public /home/nfs/public
```

#### 開機自動掛載

```bash
# 不建議寫入 /etc/fstab（網路尚未啟動時會失敗）
# 寫入 /etc/rc.d/rc.local
mount -t nfs -o nosuid,noexec,nodev,rw,bg,soft,rsize=32768,wsize=32768 \
  192.168.100.254:/home/public /home/nfs/public
```

#### autofs 自動掛載（推薦）

用到才掛載，閒置 5 分鐘自動卸載。

```bash
# /etc/auto.master
/home/nfsfile  /etc/auto.nfs

# /etc/auto.nfs
public   -rw,bg,soft,rsize=32768,wsize=32768  192.168.100.254:/home/public
testing  -rw,bg,soft,rsize=32768,wsize=32768  192.168.100.254:/home/test
temp     -rw,bg,soft,rsize=32768,wsize=32768  192.168.100.254:/tmp

# 啟動
/etc/init.d/autofs stop && /etc/init.d/autofs start
```

### 2.5 安全性與效能調校

#### 權限三層檢查

要寫入 NFS 分享目錄，必須同時滿足：
1. **使用者身份 (UID)**：Client UID 在 Server 上的對應身份
2. **NFS 設定權限**：/etc/exports 設定為 rw
3. **檔案系統權限**：目錄/檔案本身的 rwx 權限

#### UID 對應問題

| 情境 | 結果 |
|------|------|
| Client/Server UID 相同且帳號相同 | 正常存取 |
| Client UID=501 (dmtsai)，Server UID=501 (vbird) | Client 以 vbird 身份存取（**危險**） |
| Client UID=501，Server 無 UID=501 | 被壓縮為 nfsnobody |
| Client 為 root (UID=0) | 預設被壓縮為 nfsnobody（root_squash） |

> **最佳實踐**：搭配 NIS 統一帳號管理，確保 UID/GID 一致。

#### 防火牆設定

```bash
# 固定 NFS 相關服務埠口
vim /etc/sysconfig/nfs
RQUOTAD_PORT=1001
LOCKD_TCPPORT=30001
LOCKD_UDPPORT=30001
MOUNTD_PORT=1002

# 重啟後需開放的埠口：111, 2049, 1001, 1002, 30001
iptables -A INPUT -p tcp -s 192.168.100.0/24 -m multiport \
  --dport 111,2049,1001,1002,30001 -j ACCEPT
iptables -A INPUT -p udp -s 192.168.100.0/24 -m multiport \
  --dport 111,2049,1001,1002,30001 -j ACCEPT
```

#### NFS Server 關機注意

若有 Client 仍在連線，關機可能需要等待數小時。關機前：
1. `showmount -a localhost` 查看連線中的 Client
2. 通知 Client 卸載
3. 先關閉 rpcbind 與 nfs 服務
4. 若無法正常關閉，用 `netstat -utlp` 找 PID 後 kill

---

## 三、FTP 伺服器 (vsftpd)

### 3.1 FTP 運作原理

#### 雙通道架構

| 通道 | 用途 | 預設埠口 |
|------|------|----------|
| 命令通道 (Command Channel) | 下達指令（ls, cd, get, put） | port 21 |
| 資料通道 (Data Channel) | 實際檔案傳輸 | port 20 (主動) 或隨機 (被動) |

#### 主動式 vs 被動式連線

```
【主動式 Active】                    【被動式 Passive】
Client                Server         Client                Server
  │                     │              │                     │
  │──port AA → port 21──│              │──port AA → port 21──│
  │   (命令通道建立)     │              │   (命令通道建立)     │
  │                     │              │                     │
  │ 告知 port BB        │              │ 發送 PASV 請求      │
  │──────────────────→  │              │──────────────────→  │
  │                     │              │                     │
  │←─port 20 → port BB─│              │  回報 port PASV     │
  │ Server 主動連 Client│              │←─────────────────── │
  │                     │              │                     │
  │                     │              │──port CC → port PASV│
  │                     │              │ Client 主動連 Server│
```

**NAT 環境問題**：
- 主動式：Server 用 port 20 連 Client，但 NAT 後的 Client 無法被連到 → **失敗**
- 被動式：Client 主動連 Server 的 PASV port → **成功**
- 解決方案：使用被動式，或載入 `ip_nat_ftp` + `ip_conntrack_ftp` 模組

### 3.2 vsftpd 架構與設定

#### 為何選 vsftpd

- **Very Secure FTP Daemon**：安全導向設計
- 以低權限使用者身份執行 daemon
- 利用 chroot() 限制使用者目錄
- 所有額外指令 (dir, ls, cd) 整合在主程式中
- 高權限操作透過受限的上層程序控制

#### 軟體結構

| 檔案/目錄 | 用途 |
|-----------|------|
| `/etc/vsftpd/vsftpd.conf` | 主設定檔（唯一） |
| `/etc/pam.d/vsftpd` | PAM 認證設定 |
| `/etc/vsftpd/ftpusers` | PAM 模組禁止登入名單 |
| `/etc/vsftpd/user_list` | vsftpd 自訂的帳號管控名單 |
| `/etc/vsftpd/chroot_list` | chroot 例外名單（需手動建立） |
| `/usr/sbin/vsftpd` | 執行檔 |
| `/var/ftp/` | 匿名者根目錄 |
| `/var/log/xferlog` | 傳輸記錄 |
| `/var/log/vsftpd.log` | vsftpd 專屬日誌（需額外設定） |

#### vsftpd.conf 核心參數

**伺服器環境**：

```ini
listen=YES                  # standalone 模式
listen_port=21              # 命令通道埠口
connect_from_port_20=YES    # 主動式用 port 20
pasv_enable=YES             # 支援被動式
pasv_min_port=65400         # 被動式埠口範圍
pasv_max_port=65410
use_localtime=YES           # 使用本地時間（重要！）
```

**連線控制**：

```ini
max_clients=50              # 最大同時連線數
max_per_ip=5                # 同 IP 最大連線數
connect_timeout=60          # 主動連線 timeout
accept_timeout=60           # 被動連線 timeout
data_connection_timeout=300 # 資料傳輸 timeout
idle_session_timeout=300    # 閒置 timeout
```

**日誌設定**：

```ini
xferlog_enable=YES
xferlog_file=/var/log/xferlog
xferlog_std_format=YES
dual_log_enable=YES
vsftpd_log_file=/var/log/vsftpd.log
```

### 3.3 實體帳號設定

#### 完整設定範例

```ini
# /etc/vsftpd/vsftpd.conf — 實體帳號專用
anonymous_enable=NO
local_enable=YES
write_enable=YES
local_umask=002
local_max_rate=1000000        # 1MB/s 速限

# chroot 設定（推薦：預設全部 chroot）
chroot_local_user=YES         # 所有人預設 chroot
chroot_list_enable=YES        # 啟用例外名單
chroot_list_file=/etc/vsftpd/chroot_list  # 名單內的人不被 chroot

# 帳號管控
userlist_enable=YES
userlist_deny=YES             # user_list 內的帳號禁止登入
userlist_file=/etc/vsftpd/user_list

# 伺服器環境
use_localtime=YES
dirmessage_enable=YES
listen=YES
pam_service_name=vsftpd
tcp_wrappers=YES
banner_file=/etc/vsftpd/welcome.txt
```

#### SELinux 注意

```bash
# 允許實體帳號讀取家目錄
setsebool -P ftp_home_dir=1
```

#### chroot 邏輯

| chroot_local_user | chroot_list_enable | chroot_list 內的帳號 | 其他帳號 |
|---|---|---|---|
| YES | YES | **不** chroot | chroot |
| YES | NO | — | 全部 chroot |
| NO | YES | chroot | **不** chroot |
| NO | NO | — | 全部不 chroot |

#### 嚴格帳號白名單模式

```ini
userlist_enable=YES
userlist_deny=NO              # 反轉邏輯：名單內的才能登入
userlist_file=/etc/vsftpd/user_list
```

### 3.4 匿名登入設定

#### 完整設定範例

```ini
# /etc/vsftpd/vsftpd.conf — 匿名專用 (如校園 FTP)
anonymous_enable=YES
no_anon_password=YES          # 免輸入密碼
anon_max_rate=1000000         # 1MB/s
local_enable=NO               # 關閉實體帳號

# 連線控制
data_connection_timeout=60
idle_session_timeout=600
max_clients=50
max_per_ip=5

# 上傳控制（僅需下載時全部不開）
# write_enable=YES
# anon_upload_enable=YES
# anon_mkdir_write_enable=YES
# anon_other_write_enable=YES

# 伺服器環境
use_localtime=YES
listen=YES
pasv_min_port=65400
pasv_max_port=65410
```

#### 匿名上傳但不可下載（安全做法）

```ini
write_enable=YES
anon_upload_enable=YES
anon_mkdir_write_enable=YES
chown_uploads=YES             # 上傳後改變擁有者
chown_username=daemon         # 改為 daemon，匿名者 (ftp) 無法讀取
```

```bash
# 建立上傳目錄
mkdir /var/ftp/uploads
chown ftp /var/ftp/uploads

# SELinux 放行
setsebool -P allow_ftpd_anon_write=1
setsebool -P allow_ftpd_full_access=1
```

### 3.5 SSL/TLS 加密

#### 建立憑證

```bash
cd /etc/pki/tls/certs
make vsftpd.pem
cp -a vsftpd.pem /etc/vsftpd/
```

#### 設定參數

```ini
ssl_enable=YES
allow_anon_ssl=NO             # 匿名者不強制加密
force_local_data_ssl=YES      # 實體帳號資料傳輸加密
force_local_logins_ssl=YES    # 實體帳號登入加密
ssl_tlsv1=YES
ssl_sslv2=NO
ssl_sslv3=NO
rsa_cert_file=/etc/vsftpd/vsftpd.pem
```

> **FTPS vs SFTP**：FTPS 僅開放 FTP 功能，不暴露 SSH；SFTP 需要開放 port 22 (sshd)，攻擊面更大。

### 3.6 防火牆與安全性

#### iptables 設定

```bash
# 載入 FTP 追蹤模組
vim /etc/sysconfig/iptables-config
IPTABLES_MODULES="ip_nat_ftp ip_conntrack_ftp"

# 開放埠口
iptables -A INPUT -p TCP --dport 21 --sport 1024:65534 -j ACCEPT
iptables -A INPUT -p TCP --dport 65400:65410 --sport 1024:65534 -j ACCEPT
```

#### 帳號抵擋層級

```
第一層：/etc/vsftpd/ftpusers （PAM 模組，最高優先）
  └─ 系統帳號 (root, bin, daemon...) 寫入此檔案
第二層：/etc/vsftpd/user_list （vsftpd 自訂）
  └─ 依據 userlist_deny 參數決定黑名單或白名單模式
第三層：/etc/hosts.allow, /etc/hosts.deny （TCP Wrappers）
  └─ IP 層級的存取控制
```

---

## 四、選型決策指南

```
需要「檔案系統共享」（像本地磁碟一樣使用）？
  ├─ YES → Unix/Linux 之間 → NFS
  │        跨平台 (Windows) → SAMBA
  └─ NO → 需要「檔案傳輸」功能？
            ├─ 對外公開（匿名下載）→ vsftpd (anonymous)
            ├─ 內部帳號傳輸 → SFTP 優先，vsftpd + FTPS 次選
            └─ 自動化同步 → rsync
```

| 場景 | 推薦方案 | 理由 |
|------|---------|------|
| Linux Cluster 共享 /home | NFS + NIS | 透明掛載、UID 統一管理 |
| 校園軟體鏡像站 | vsftpd (anonymous) | 大量下載、不需帳號 |
| 廠商上傳檔案 | vsftpd + FTPS + chroot | 安全隔離、加密傳輸 |
| 個人/團隊日常傳檔 | SFTP (sshd) | 零額外設定、加密 |
| NAS 跨平台存取 | SAMBA + NFS 並行 | Windows/Mac/Linux 通吃 |

---

## 五、常見問題排錯

### NFS 常見問題

| 症狀 | 可能原因 | 解決方式 |
|------|---------|---------|
| `access denied by server` | Client IP 不在 /etc/exports 允許範圍 | 修改 /etc/exports 加入 Client IP |
| `Connection refused` | Client 端 rpcbind 未啟動 | `service rpcbind start` |
| `Program not registered` | Server 端 nfs 未啟動或 rpcbind 重啟後未重啟 nfs | `service nfs restart` |
| df/ls 指令卡住 30 分鐘 | Server 離線但 Client 用 hard mount | 改用 `soft` 或 `bg` 參數掛載 |
| 檔案擁有者顯示為數字 | Client/Server UID 不一致 | 搭配 NIS 統一帳號，或用 all_squash |
| 可以連但不能寫入 | exports 為 ro 或目錄權限不足 | 檢查 exports + `chmod`/`chown` |

### FTP (vsftpd) 常見問題

| 症狀 | 可能原因 | 解決方式 |
|------|---------|---------|
| 連不上 | iptables 未開放 port 21 | 加入防火牆規則 |
| 登入後 `cannot change directory` | SELinux 阻擋 | `setsebool -P ftp_home_dir=1` |
| `XXX file can't be opened` | vsftpd.conf 指定的檔案不存在 | `touch` 建立對應檔案 |
| 帳號無法登入 | 帳號被列入 ftpusers 或 user_list | 從名單中移除 |
| 無法上傳 | 缺少 `write_enable=YES` 或目錄權限不對 | 檢查設定 + `chmod`/`chown` |
| 時間差 8 小時 | 預設使用 GMT | 加入 `use_localtime=YES` |
| 被動式連線失敗 | 未開放 PASV 埠口範圍 | 設定 `pasv_min/max_port` 並開放防火牆 |
| 匿名上傳失敗 | SELinux 阻擋 | `setsebool -P allow_ftpd_anon_write=1` |

### 通用排錯流程

```
1. 查看日誌
   - NFS: /var/log/messages
   - FTP: /var/log/vsftpd.log, /var/log/xferlog, /var/log/messages

2. 確認服務狀態
   - NFS: rpcinfo -p localhost; showmount -e localhost
   - FTP: netstat -tulnp | grep 21

3. 檢查防火牆
   - iptables -L -n | grep -E '(21|2049|111)'

4. 檢查 SELinux
   - getenforce
   - getsebool -a | grep ftp
   - 查看 /var/log/messages 中的 sealert 提示

5. 檢查檔案系統權限
   - ls -la [目標目錄]
   - 確認 UID/GID 對應
```

---

## 附錄：快速啟動 Cheatsheet

### NFS Server 三步驟

```bash
# 1. 設定分享
echo '/data 192.168.1.0/24(rw,sync,no_root_squash)' >> /etc/exports

# 2. 啟動
systemctl start rpcbind nfs-server

# 3. 驗證
exportfs -v
showmount -e localhost
```

### NFS Client 三步驟

```bash
# 1. 查詢
showmount -e 192.168.1.254

# 2. 掛載
mount -t nfs -o nosuid,noexec,nodev,bg,soft,rsize=32768,wsize=32768 \
  192.168.1.254:/data /mnt/nfs

# 3. 驗證
df -h /mnt/nfs
```

### vsftpd 快速啟動

```bash
# 1. 安裝
yum install vsftpd

# 2. 最小設定
cat > /etc/vsftpd/vsftpd.conf << 'EOF'
listen=YES
local_enable=YES
write_enable=YES
local_umask=022
chroot_local_user=YES
use_localtime=YES
pam_service_name=vsftpd
pasv_min_port=65400
pasv_max_port=65410
EOF

# 3. 啟動
systemctl start vsftpd
setsebool -P ftp_home_dir=1
```
