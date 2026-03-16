【情境掃描】（Scenario Overview）
背景： 公司有 2,000 名員工。老闆決定導入 AWS WorkSpaces（也就是把員工的電腦桌面全部搬到 AWS 雲端上，變成虛擬桌面）。

現況： 員工的帳號密碼目前都存在公司地端機房的 Active Directory (On-premise AD) 裡面。

目標： 你要設計一個架構，讓員工在登入雲端 WorkSpaces 時，能直接使用他們原本的 AD 帳號密碼，而且這個架構必須是「高效且穩定 (effective manner)」的。

2. 【考點定位】（Knowledge Domain）
要達成這個目標，你的架構必須解決兩個層面的問題：

身分驗證層 (Identity)： AWS 怎麼知道要去哪裡查員工的帳號密碼？

網路連線層 (Networking)： 雲端的 AWS 怎麼跟地端的機房安全、快速地連線？

3. 【選項過濾與邏輯拆解】
這題要求選 2 個答案，剛好就是對應上述的兩個層面。

第一層：身分驗證 (選 A 還是 B？)
🎯 A. Deploy an AD Connector (正確)

原理： AD Connector 是 AWS Directory Service 的一種。它的角色就像是一個**「代理人 (Proxy)」**。它自己不存任何密碼，當員工登入 WorkSpaces 時，AD Connector 會把登入請求直接「轉發」回你地端的 AD 去驗證。這完全符合題目「確保使用地端 AD 進行驗證」的要求。

❌ B. Deploy Hosted AD (Managed Microsoft AD)

原理： 雖然 Hosted AD 也可以透過建立「信任關係 (Trust Relationship)」來連接地端 AD，但如果你的唯一目的只是要「用原來的 AD 驗證」，架設一個全新的 Hosted AD 成本太高且架構過於複雜。AD Connector 是最輕量、最直接的做法。

第二層：網路連線 (選 C 還是 D？)
這兩個選項都能把 AWS 跟地端連起來，但為什麼要選 C？關鍵在於題目給的數字：「2,000 employees (兩千名員工)」。

🎯 C. Create a Direct Connect (正確)

原理： Direct Connect (DX) 是實體的企業級專線。WorkSpaces 是虛擬桌面，員工等於是一直在看「遠端串流影片」，這非常吃頻寬，而且對延遲 (Latency) 極度敏感。2,000 人同時連線，只有 DX 這種高頻寬、低延遲的專線能提供「有效 (effective)」的體驗。

❌ D. Create a VPN

原理： Site-to-Site VPN 是走公共網際網路的加密通道。頻寬受限（單個通道通常最多 1.25 Gbps），且延遲不穩定。如果 2,000 人同時透過 VPN 打開虛擬桌面，網路絕對會塞爆，員工的滑鼠游標會卡到讓老闆崩潰。

💡 專家實務總結
結論：這題的正確答案是 A 和 C。

架構師的實務筆記 (Runbook)：
未來在考試或工作中看到 「AWS WorkSpaces (虛擬桌面)」 + 「地端 AD」 + 「大量使用者」 的組合，你的反射動作要是：

AD Connector (做最單純的密碼驗證轉發)。

Direct Connect (保證虛擬桌面的畫面不會卡頓)。