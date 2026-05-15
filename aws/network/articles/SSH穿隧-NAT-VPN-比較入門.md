# SSH 穿隧、NAT、VPN 入門比較

## 摘要

SSH 穿隧（SSH Tunneling）、NAT（Network Address Translation）和 VPN（Virtual Private Network）都跟「讓流量透過另一條路到達目的地」有關，所以初學時很容易混在一起。

但它們解決的問題其實不一樣：

- **SSH 穿隧**：借一條 SSH 連線，把某個服務的流量安全地轉送過去。
- **NAT**：改寫 IP / Port，讓內外網封包能互相抵達。
- **VPN**：把一台主機或一整個網段接進另一個私有網路。

如果用一句話抓直覺：

> SSH 穿隧是「臨時開一條安全小通道」，NAT 是「幫封包改地址」，VPN 是「讓你加入另一個網路」。

本文會以 SSH 穿隧為主，再用 NAT 與 VPN 做對照。

---

## 一、先建立共同直覺：為什麼需要「繞一條路」？

很多網路問題都長這樣：

```text
你的電腦
  |
  |  不能直接連
  v
內部服務 / 私有資料庫 / 公司內網 / 雲端 private subnet
```

不能直接連的原因可能很多：

- 服務只開在內網 IP，例如 `10.0.1.25:5432`
- 防火牆不允許外部直接進來
- 資料庫沒有 public IP
- 只有跳板機可以進入內部網段
- 家用網路或公司網路後面有 NAT

這時候就會出現三類常見解法：

```text
SSH Tunnel：透過一台可 SSH 登入的主機轉送特定服務流量
NAT：透過位址轉換，讓私有 IP 可以對外或對內被轉發
VPN：建立一條網路層級的加密連線，讓你像在同一個網路裡
```

它們看起來都像「中間多了一個東西」，但中間那個東西的意義完全不同。

---

## 二、SSH 穿隧是什麼？

SSH 穿隧的核心概念是：

> 既然我已經能安全地 SSH 到某台機器，那我能不能順便把其他 TCP 流量也塞進這條 SSH 連線裡？

答案是可以。

一般 SSH 登入長這樣：

```text
你的電腦 --SSH--> 跳板機 / 遠端主機
```

SSH 穿隧則是：

```text
你的電腦 --SSH 加密連線--> 跳板機 --轉送--> 內部服務
```

例如，你的資料庫在內網：

```text
PostgreSQL: 10.0.1.25:5432
```

你的筆電不能直接連 `10.0.1.25`，但你可以 SSH 到跳板機：

```text
bastion.example.com
```

那你就可以用 SSH tunnel 把本機的 `localhost:15432` 接到內網資料庫的 `10.0.1.25:5432`。

```text
你的電腦 localhost:15432
  |
  | SSH tunnel
  v
bastion.example.com
  |
  v
10.0.1.25:5432
```

對你的資料庫工具來說，它只是在連：

```text
localhost:15432
```

但實際上流量會被 SSH 加密後送到跳板機，再由跳板機轉送到內部資料庫。

---

## 三、SSH 穿隧的三種常見模式

SSH tunnel 最常見有三種模式：

1. Local Port Forwarding
2. Remote Port Forwarding
3. Dynamic Port Forwarding / SOCKS Proxy

### 1. Local Port Forwarding：把遠端服務拉到本機

這是最常用的模式。

用途：

- 從自己電腦連內網資料庫
- 從自己電腦打內部 API
- 從自己電腦開內部管理介面

指令格式：

```bash
ssh -L 本機port:目標服務host:目標服務port user@ssh-server
```

例子：

```bash
ssh -L 15432:10.0.1.25:5432 ubuntu@bastion.example.com
```

意思是：

```text
連到我本機 localhost:15432 的流量
  -> 進入 SSH 連線
  -> 到 bastion.example.com
  -> 再轉到 10.0.1.25:5432
```

這時候你可以把資料庫工具設定成：

```text
Host: localhost
Port: 15432
```

但實際連到的是內網 PostgreSQL。

### 2. Remote Port Forwarding：把本機服務暴露到遠端

Remote forwarding 的方向剛好相反。

它是把你本機或你這邊網路裡的服務，透過遠端 SSH server 的 port 暴露出去。

指令格式：

```bash
ssh -R 遠端port:本機或內部host:本機或內部port user@ssh-server
```

例子：

```bash
ssh -R 18080:localhost:3000 ubuntu@public-server.example.com
```

意思是：

```text
別人連 public-server.example.com:18080
  -> 流量進入 SSH 連線
  -> 回到你的電腦
  -> 轉到 localhost:3000
```

常見用途：

- 臨時展示本機開發中的 web app
- 讓遠端伺服器回連你本機的服務
- 在 NAT 後面暫時暴露服務

這種模式要特別小心，因為你可能不小心把本機服務開給不該存取的人。

### 3. Dynamic Port Forwarding：把 SSH 變成 SOCKS Proxy

Dynamic forwarding 不指定單一目標服務，而是在本機開一個 SOCKS proxy。

指令格式：

```bash
ssh -D 本機port user@ssh-server
```

例子：

```bash
ssh -D 1080 ubuntu@bastion.example.com
```

意思是：

```text
你的瀏覽器 / 工具
  -> SOCKS proxy localhost:1080
  -> SSH tunnel
  -> bastion.example.com
  -> 再連到外部或內部目標
```

這比較像是「讓部分應用程式透過 SSH server 當出口」。

常見用途：

- 臨時讓瀏覽器透過遠端主機連線
- 測試某個服務從遠端網路看出去的樣子
- 存取只有遠端網路能看到的內部 web 介面

它不像完整 VPN 會改掉整台機器的路由，通常只有設定了 SOCKS proxy 的應用程式會走這條路。

---

## 四、NAT 是什麼？

NAT 的核心不是加密，也不是登入驗證，而是：

> 改寫封包的 IP / Port，讓原本不能直接互通的位址可以透過轉換互通。

最常見的是家用網路：

```text
筆電 192.168.1.10
手機 192.168.1.11
桌機 192.168.1.12
  |
  v
家用路由器 Public IP: 203.0.113.10
  |
  v
Internet
```

內部裝置都是私有 IP，不能直接在網際網路上被路由。

當筆電連到外部網站時，路由器會把封包來源改掉：

```text
原本：
192.168.1.10:51520 -> 93.184.216.34:443

經過 NAT 後：
203.0.113.10:62001 -> 93.184.216.34:443
```

回應回來時，NAT 設備再查表，把流量送回原本的筆電。

```text
93.184.216.34:443 -> 203.0.113.10:62001
  |
  v
NAT 查表
  |
  v
93.184.216.34:443 -> 192.168.1.10:51520
```

所以 NAT 解決的是「地址與連線映射」問題。

它常見於：

- 家用路由器
- 公司出口防火牆
- 雲端 NAT Gateway
- Port forwarding
- 私有子網出網

但要注意：

> NAT 本身不代表流量有加密，也不代表對方有通過身份驗證。

它可能讓內部主機比較不容易直接被外部掃到，但這不等於它是完整安全方案。

---

## 五、VPN 是什麼？

VPN 的核心是：

> 建立一條加密連線，讓你的主機或網段像是加入另一個私有網路。

個人 VPN 常見長這樣：

```text
你的筆電
  |
  | VPN tunnel
  v
公司 VPN Gateway
  |
  v
公司內網
```

連上 VPN 後，你的電腦可能會拿到一個公司內網可識別的 IP，並多出一些路由：

```text
10.0.0.0/8     -> 走 VPN
172.16.0.0/12  -> 走 VPN
其他 Internet  -> 看 VPN 設定，可能走本地，也可能全走 VPN
```

站台對站台 VPN 則是把兩個網路接起來：

```text
公司機房 192.168.0.0/16
  |
  | Site-to-Site VPN
  v
AWS VPC 10.0.0.0/16
```

VPN 通常比 SSH tunnel 更像正式網路架構：

- 可以承載多種服務，不只單一 port
- 可以用路由表決定哪些網段走 VPN
- 可以支援多使用者或多站點
- 可以長期維運與監控

但它也比較重：

- 需要 VPN server / gateway
- 需要使用者、憑證、路由與權限管理
- 設錯可能讓過多內網資源暴露給使用者
- 故障時排查範圍比單一 SSH tunnel 大

---

## 六、三者比較表

| 項目 | SSH 穿隧 | NAT | VPN |
|---|---|---|---|
| 核心用途 | 透過 SSH 轉送特定流量 | 改寫 IP / Port | 建立加密私有網路連線 |
| 主要層級 | 應用層使用方式，底層依賴 TCP/SSH | 網路層 / 傳輸層位址轉換 | 通常是網路層或虛擬網卡層 |
| 是否加密 | 是，走 SSH 加密 | 不一定，NAT 本身不加密 | 通常是 |
| 是否改 IP / Port | 對應用程式來說可能改成 localhost port | 是，這就是核心功能 | 可能會分配 VPN IP 與改路由 |
| 常見範圍 | 單一服務、單一 port、臨時通道 | 出口、入口、私網與公網轉換 | 主機到網路、網路到網路 |
| 使用門檻 | 有 SSH 權限即可開始 | 需要網路設備或雲端路由設定 | 需要 VPN gateway/client/憑證 |
| 適合場景 | 臨時連 DB、跳板機、內部 API 測試 | 私有子網出網、port forwarding | 長期遠端辦公、混合雲、跨站連線 |
| 主要風險 | 權限控管鬆散、port 暴露、難長期治理 | 誤以為 NAT 等於安全、連線狀態表問題 | 權限範圍太大、路由複雜、維運成本較高 |

---

## 七、什麼時候用 SSH tunnel？

SSH tunnel 很適合這些情境：

### 1. 臨時存取內網服務

例如你只是要短時間連一個內網資料庫查問題：

```bash
ssh -L 15432:10.0.1.25:5432 ubuntu@bastion.example.com
```

這比為了單次排查去架 VPN 輕很多。

### 2. 透過跳板機連 private subnet

典型雲端架構：

```text
你的電腦
  |
  v
Bastion Host（public subnet）
  |
  v
Database / Internal API（private subnet）
```

內部服務不開 public IP，只允許跳板機連入。這時 SSH tunnel 是很自然的工具。

### 3. 開發與測試

例如本機要測試 staging 環境中的 private API，或想讓某個工具暫時透過遠端網路出去。

這類情境通常是：

- 時間短
- 人數少
- 目標服務明確
- 不值得建立完整 VPN 架構

SSH tunnel 就很舒服。

---

## 八、什麼時候不要硬用 SSH tunnel？

SSH tunnel 很方便，但不該什麼都拿它解。

### 1. 多人長期存取內網

如果整個團隊每天都要存取很多內網服務，用一堆 SSH tunnel 會很快失控：

- 每個人開的 port 不同
- 權限不好盤點
- tunnel 斷線難監控
- 沒有統一的存取政策

這時通常該考慮：

- VPN
- Zero Trust Network Access
- SSO + Proxy
- PrivateLink / VPC Endpoint 類型的正式架構

### 2. 需要整個網段互通

如果需求是：

```text
公司機房整段 192.168.0.0/16
要跟
雲端 VPC 10.0.0.0/16
互通
```

那 SSH tunnel 就不是合適工具。

這是 VPN、Direct Connect、Transit Gateway、專線或 SD-WAN 這類架構要解的問題。

### 3. 你只是需要私有子網出網

如果問題是：

```text
Private subnet 裡的 EC2 要去 Internet 拉套件
```

那通常不是 SSH tunnel 的場景，而是 NAT Gateway、NAT Instance、VPC Endpoint 或 IPv6 egress 的設計問題。

---

## 九、快速決策：我到底該用哪個？

可以用這個簡化版判斷：

```text
只是我臨時要連某個內部服務？
  -> SSH tunnel

內部主機需要對外連 Internet？
  -> NAT / Egress 架構

外部使用者或兩個網段要長期像同一個私網？
  -> VPN / Zero Trust / 專線

只是要把某個 public port 轉到內部服務？
  -> Port forwarding / DNAT / Load Balancer

需要正式控管很多人的內網存取？
  -> 不要只靠 SSH tunnel，改用集中式存取方案
```

再濃縮成一句：

> 單點、臨時、明確服務，用 SSH tunnel；地址轉換，用 NAT；長期網路互通，用 VPN。

---

## 十、常見誤解

### 誤解一：SSH tunnel 就是 VPN

不完全是。

SSH tunnel 可以做到某些「像 VPN」的效果，例如透過遠端主機存取內部服務。但它通常是針對特定 port 或特定應用程式，不是把整台電腦完整接進內網。

VPN 則通常會改路由、建立虛擬網卡，讓你的主機或網段成為另一個網路的一部分。

### 誤解二：NAT 可以保護流量安全

NAT 不是加密。

NAT 只是改寫 IP / Port。它可能讓內部主機不直接暴露在公網上，但如果你傳的是明文 HTTP，NAT 不會自動幫你變成安全連線。

### 誤解三：只要能 SSH 到機器，就可以任意 tunnel

不一定。

SSH server 可以透過設定限制 port forwarding，例如：

```text
AllowTcpForwarding
PermitOpen
GatewayPorts
```

企業環境也可能要求所有 tunnel 行為都要被審計。SSH tunnel 很方便，但方便也代表它需要被治理。

---

## 結論

SSH 穿隧、NAT、VPN 都是在處理「流量怎麼走」的問題，但它們站的位置不同。

- SSH tunnel 解的是「我能不能借 SSH 安全地連到某個服務」。
- NAT 解的是「封包的地址要怎麼轉換才能進出不同網路」。
- VPN 解的是「兩邊能不能建立一條長期、加密、可路由的私有網路連線」。

學會區分這三者後，很多網路架構問題會清楚很多：

> 不要把 SSH tunnel 當成完整 VPN，也不要把 NAT 當成安全加密；它們都是好工具，但各自只適合解特定形狀的問題。
