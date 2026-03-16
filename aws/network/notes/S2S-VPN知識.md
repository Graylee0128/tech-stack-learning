這題考驗的是 AWS Site-to-Site VPN 的 「隧道保活機制 (Keepalive)」 與 「IKE 狀態管理」。

我們先把題目忘掉，我來為你建構這個必備的網路知識：

必備知識一：什麼是 IKE Session？它為什麼會斷？
在 IPsec VPN 的世界裡，IKE (Internet Key Exchange) 是用來建立安全隧道的「談判協定」。
你可以把 IKE 想像成是雙方在「打電話」：

打通電話 (IKE Phase 1 & 2)： 雙方互相確認身分、交換加密金鑰，然後把安全的資料通道（Tunnel）建立起來。

為什麼會掛電話 (IKE Session Ends)？

Idle Timeout (閒置逾時)： 如果這條隧道一段時間沒有任何資料傳輸（沒有流量），設備為了節省資源，就會自動「掛斷電話」，這時 IKE session 就會 down。

這也是為什麼很多企業的地端設備會設定「Keepalive (保活機制)」或不斷地去 Ping 雲端的機器，就是為了讓這通電話一直保持通話中。

必備知識二：誰負責「打電話」？ (Initiator vs. Responder)
這是 AWS VPN 中最常被考出來的經典設定：

預設情況下，AWS 是「接聽方 (Responder)」： AWS 會乖乖坐在那邊等。

地端的 Customer Gateway (CGW) 是「撥打方 (Initiator)」： 必須由地端主動發起第一波流量，或是主動發起 IKE 談判，這條 VPN 隧道才會建立起來。

致命邏輯：如果你從 AWS VPC 內部發起流量想連回地端，但隧道剛好斷了，AWS 不會主動去撥電話，封包就會直接被丟棄。

必備知識三：什麼是 DPD (Dead Peer Detection)？
DPD 就像是「心跳偵測」。當隧道建起來後，雙方會互相發送小封包問：「你還活著嗎？」。如果 AWS 連續幾次都沒收到地端的回應，AWS 就會判定對方「已死亡 (Dead Peer)」。

這時，AWS 提供了三種 DPD Timeout Action (死亡後的處理動作) 供你選擇：

Clear (清除 - 這是預設值)： AWS 會直接掛斷電話，清除 IKE 狀態。AWS 接著會進入「被動等待」模式，直到地端 (CGW) 再次主動打電話過來。

Restart (重啟)： AWS 發現對方死掉後，會清除舊狀態，並且**「AWS 會反客為主，主動嘗試打電話給地端」**來重啟 IKE session。

None (無動作)： AWS 什麼都不做，即使對方死了它還是假裝沒事。這會導致「網路黑洞」，實務上強烈不建議使用。

回頭看第 154 題的解析
現在你具備了完整的背景知識，我們來看這道題目。

現狀： 使用者抱怨連線偶爾會斷掉，工程師發現當連線失敗時，IKE Session 也跟著結束了 (代表隧道斷了)。

任務： 當 IKE Session 斷掉時，你要怎麼把它「叫醒 (bring up)」？


相似點：都是「保持連線活著」
NAT Keepalive        DPD (VPN)
─────────────────    ─────────────────
定時送小封包    ←→   定時送心跳訊號
防止 session 被清掉  防止認定對端已死
被動維持        ←→   主動偵測

但本質目的不同
NAT KeepaliveDPD對抗的問題NAT table 超時被清除對端主機/網路真的掛掉動作送假流量維持 session偵測 → 判斷 → 執行 action斷線後只是 mapping 消失整個 IKE tunnel 需重建主動性被動（只是維持）主動（偵測＋處理）

你說的 350 秒很關鍵！
NAT Session Timeout（常見值）
├── AWS NAT Gateway：350 秒
├── 一般防火牆：30～300 秒
└── 如果沒有 keepalive → NAT mapping 消失 → 流量中斷
這就是為什麼 Site-to-Site VPN 需要雙重保護：
Layer 1：NAT Keepalive
→ 防止中間 NAT 設備清掉 UDP 500/4500 的 mapping

Layer 2：DPD
→ 防止 IKE session 因對端無回應而判定為死亡

實際場景：兩個問題可能同時發生
On-premises ──[NAT]──[Internet]──[AWS VGW]

問題一：NAT table 超時清除（350秒沒流量）
→ 解法：Keepalive 封包（每10秒送一次）

問題二：對端真的沒回應（設備重啟/網路抖動）
→ 解法：DPD Restart 自動重建 tunnel


一句話區分：Keepalive 是「讓中間人記得你們的關係」，DPD 是「確認對方還活著、死了就重新握手」。

理解 IPsec VPN 是如何建立並維持的。它分為兩個階段（Phases）：

1. Phase 1 (IKE Phase 1)
目的：建立一個安全的管理通道。

產出：ISAKMP SA（安全性關聯）。

比喻：雙方先修一條祕密小路，用來商量後面大貨車怎麼開。

2. Phase 2 (IKE Phase 2 / IPsec Phase)
目的：建立用於加密實際數據流量的通道。

產出：IPsec SA。

關鍵點：這裡會協商加密算法（AES256 等）、認證算法（SHA2）、完美轉發安全性（PFS）以及 生命週期（Lifetime）。


Rekey（重密鑰）？
VPN 隧道不是永久不變的。為了安全，每隔一段時間（例如 1 小時）或傳輸一定流量後，Phase 2 的密鑰必須「更換」。這就是 Rekey。

本題痛點：初始化時沒問題，但在 Rekey 時，AWS 端發起的參數與用戶端設備（CGW）預設或支持的參數不匹配，導致 CGW 拒絕連接，隧道隨即中斷。