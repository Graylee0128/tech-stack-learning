# Linux NFS 與 FTP 上機學習計畫

**目標：** 用一套可重複的 Linux lab，實際完成 `NFS` 與 `vsftpd` 的安裝、設定、驗證與排錯，並在考前具備基本上機與情境題應對能力。
**完成進度：** `0 / 67`

> 2026-05-07 補充：這份檔案仍維持 NFS / FTP 上機計畫定位。Cloud Platform / SRE 主線的 Linux internals 總綱改放在 [linux-internals-roadmap.md](./linux-internals-roadmap.md)，避免把單一 lab 計畫膨脹成總 roadmap。

## 進度維護規則

- `plan.md`：本主題唯一詳細進度來源
- `logs/YYYY-MM-DD.md`：每次上機的指令、觀察、踩坑、排錯紀錄
- `articles/`：只當參考教材，不當進度追蹤檔

## 目前策略

- 先建立一套最小 Linux lab，再開始 NFS 與 FTP 練習
- 優先追求「能跑起來、能驗證、能排錯」，不是先背完全部觀念
- 每個 phase 都至少包含：安裝或設定、驗證指令、失敗排查
- NFS 先做單機觀察，再做 server/client 互掛
- FTP 先做最小 `vsftpd`，再做 passive mode、chroot、帳號限制

## 建議 lab 路線

- 首選：`1 台 Linux VM + 1 台 Linux VM`
- 次選：`1 台 Linux + 1 個 Docker / container client`
- 可接受：`1 台 Linux` 同時扮演 server / client，先學流程
- 若你用 Windows：優先用 `WSL` 或現成 VM，不建議只停留在紙上

## 學習進度

### Phase 0：建立 Linux lab 環境
- [ ] 確認這次上機用的是哪種環境：`WSL / VM / 實體 Linux / 遠端主機`
- [ ] 確認至少有 1 台可操作的 Linux 主機
- [ ] 若要完整驗證掛載流程，確認有第 2 個 client 環境
- [ ] 確認可使用 `sudo`
- [ ] 確認可執行 `ss`、`systemctl`、`journalctl`
- [ ] 確認可安裝套件：`nfs-utils` 或 `nfs-kernel-server`、`vsftpd`
- [ ] 建立這次 lab 的操作紀錄檔：`logs/YYYY-MM-DD.md`
- [ ] 先記下 lab 拓樸：哪台是 server、哪台是 client、各自 IP

### Phase 1：先看懂 NFS 與 RPC 在機器上長什麼樣
- [ ] 在 server 安裝 NFS 相關套件
- [ ] 啟動 `rpcbind`
- [ ] 啟動 NFS 服務：`nfs-server` 或對應 distro 的服務名
- [ ] 用 `systemctl status rpcbind` 確認服務狀態
- [ ] 用 `systemctl status nfs-server` 或 `service nfs status` 確認服務狀態
- [ ] 用 `rpcinfo -p` 觀察 RPC 註冊資訊
- [ ] 用 `ss -lntup` 或 `netstat -tulnp` 觀察 `111`、`2049` 等 port
- [ ] 在 log 記下：`rpcbind`、`rpc.nfsd`、`rpc.mountd` 各自看到了什麼

### Phase 2：做出第一個可掛載的 NFS 分享
- [ ] 在 server 建立分享目錄，例如 `/srv/nfs/public`
- [ ] 設定基本權限，至少能讓測試用戶讀取
- [ ] 編輯 `/etc/exports`，先做最小可用分享
- [ ] 執行 `exportfs -arv` 套用設定
- [ ] 用 `showmount -e localhost` 驗證 server 確實有匯出目錄
- [ ] 在 client 建立掛載點，例如 `/mnt/nfs-public`
- [ ] 在 client 執行 `mount -t nfs server:/srv/nfs/public /mnt/nfs-public`
- [ ] 用 `mount | grep nfs` 驗證掛載成功
- [ ] 在 client 建立或讀取測試檔案，驗證實際可存取
- [ ] 在 log 記下從 `exports` 到 `mount` 的完整指令鏈

### Phase 3：驗證 NFS 權限模型與 squash 行為
- [ ] 先用預設 `root_squash` 做一次測試
- [ ] 在 client 用 root 身份寫檔，觀察 server 端檔案擁有者
- [ ] 改成 `no_root_squash` 後重新 `exportfs -arv`
- [ ] 再測一次 root 寫入，觀察差異
- [ ] 設定一次 `all_squash`
- [ ] 加上 `anonuid` / `anongid` 做一次匿名映射測試
- [ ] 故意設一個 client UID 與 server 不一致的情境，觀察檔案擁有者
- [ ] 在 log 記下 `root_squash / no_root_squash / all_squash` 的實測差異

### Phase 4：把 NFS 驗證做到可排錯
- [ ] 用 `rpcinfo -p server` 從 client 端查看 server RPC 服務
- [ ] 用 `showmount -e server` 從 client 端查看分享目錄
- [ ] 故意把 `/etc/exports` 主機條件寫錯一次，重現 `access denied`
- [ ] 看懂錯誤後修正 exports 並重新驗證
- [ ] 練習卸載：`umount /mnt/nfs-public`
- [ ] 練習重新掛載並加上常見選項：`nosuid,noexec,nodev`
- [ ] 比較 `/etc/fstab` 與手動掛載的差異
- [ ] 若環境允許，試一次 `autofs` 或至少看懂它的用途
- [ ] 用 `journalctl` 或系統日誌查一次 NFS 相關訊息
- [ ] 在 log 記下你自己的 NFS 排錯順序

### Phase 5：做出第一個可登入的 vsftpd
- [ ] 在 server 安裝 `vsftpd`
- [ ] 啟動 `vsftpd` 服務
- [ ] 用 `systemctl status vsftpd` 確認服務啟動
- [ ] 用 `ss -lntp | grep :21` 驗證 port `21` 已監聽
- [ ] 建立 1 個本機測試帳號
- [ ] 在 `/etc/vsftpd/vsftpd.conf` 設成最小可用：禁止匿名、允許 local user、允許寫入
- [ ] 用 FTP client 或 `ftp` 指令實測登入、列目錄、上傳下載
- [ ] 在 log 記下 `vsftpd.conf` 最小可用設定與第一輪驗證結果

### Phase 6：把 FTP 做到 passive、chroot、帳號管控
- [ ] 在 `vsftpd.conf` 啟用 passive mode
- [ ] 設定 `pasv_min_port` 與 `pasv_max_port`
- [ ] 重新啟動 `vsftpd` 並驗證被動式可用
- [ ] 設定 `chroot_local_user=YES`
- [ ] 驗證一般帳號登入後被限制在家目錄
- [ ] 用 `chroot_list` 做 1 個例外帳號測試
- [ ] 用 `ftpusers` 或 `user_list` 擋掉 1 個測試帳號
- [ ] 在 log 記下 passive mode、chroot、黑白名單的實測結果

### Phase 7：安全性、日誌與考前情境排錯
- [ ] 找出 `vsftpd` 相關日誌檔位置
- [ ] 看一次 NFS 相關日誌或 `journalctl` 輸出
- [ ] 若環境有防火牆，檢查 `111`、`2049`、`21` 與 passive port range
- [ ] 若環境有 SELinux，執行 `getenforce` 與 `getsebool -a | grep ftp`
- [ ] 故意製造 1 個 FTP 失敗情境，例如禁止登入或 chroot 異常
- [ ] 故意製造 1 個 NFS 失敗情境，例如 exports 條件不符
- [ ] 用你自己的固定順序完成兩題排錯，並寫進 log

## 建議操作順序

1. 先完成 `Phase 0 ~ Phase 2`，把 NFS 最小流程跑通
2. 再做 `Phase 3 ~ Phase 4`，把 NFS 權限與排錯手感建立起來
3. 接著做 `Phase 5 ~ Phase 6`，把 `vsftpd` 最小可用與進階限制做出來
4. 最後做 `Phase 7`，把日誌、防火牆、SELinux、情境題串起來

## 第一輪驗收標準

- [ ] 已有 1 套可操作的 Linux lab
- [ ] 已能在 server 上看見 `rpcbind` 與 NFS 服務狀態
- [ ] 至少 1 個 NFS 分享可成功被 client 掛載
- [ ] 已實測 `root_squash` 與 `no_root_squash` 的差異
- [ ] 已能用 `rpcinfo`、`showmount`、`mount` 做基本驗證
- [ ] 至少 1 個 `vsftpd` 帳號可成功登入與傳檔

## 第二輪驗收標準

- [ ] 已能完成 passive mode 設定與驗證
- [ ] 已能完成 `chroot` 與例外帳號設定
- [ ] 已能用 `ftpusers` 或 `user_list` 控制登入
- [ ] 已能用固定順序回答 NFS / FTP 排錯題
- [ ] 已完成至少 2 份上機紀錄於 `logs/`
- [ ] 已能用自己的 lab 結果解釋 NFS 與 FTP 的核心差異
