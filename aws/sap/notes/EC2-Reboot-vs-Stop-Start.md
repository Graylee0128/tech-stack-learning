# EC2 重啟 (Reboot) vs 停止再啟動 (Stop/Start)

## 核心邏輯

把 EC2 想像成一間租來的辦公室：

### Reboot（重新啟動）

就像把電腦「重新啟動」，電源沒斷，人也沒離開位子。

- **物理位置**：還是在**同一台實體伺服器 (Same Host)** 上
- **網路地址**：門牌號碼（Private IP）和臨時門牌（Public IP）通通都不會變，綁定的 Elastic IP 也會留著
- **磁碟資料**：EBS 裡的資料當然還在

### Stop/Start（停止再啟動）

就像搬家。先退租（Stop），過一陣子再重新租一間（Start）。

- **物理位置**：AWS 會在機房裡找另一個有空位的**新實體伺服器 (New Host)**
- **網路地址**：原本的 Public IP 會消失（除非用 Elastic IP）。Private IP 除非換 Subnet，否則通常會保留
- **磁碟資料**：EBS 保留，但 Instance Store 資料**永久遺失**

## 對比表（必背）

| 特性 | Reboot | Stop/Start |
|------|--------|------------|
| 實體主機 (Host) | 不變 | **會變** |
| Private IP | 不變 | 不變 |
| Public IP | 不變 | **會變**（除非用 EIP） |
| EBS Volume 資料 | 保留 | 保留 |
| Instance Store 資料 | 保留 | **永久遺失** |
| 收費 | 繼續計費 | 停止期間不計運算費（但收 EBS 費） |

## 考題陷阱

> 選項 D 說：「Reboot 後實例會在一台新的主機電腦上執行」

**錯誤！** 根據 AWS 官方文件：

- **Reboot** → 同一個實體主機
- **Stop/Start** → 才會遷移到另一個實體主機
