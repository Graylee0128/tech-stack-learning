# 混合雲 DNS 解析 (Hybrid DNS Resolution)

> AWS Network 題型 - 整理中


Route 53 Resolver Rule


BIND 伺服器

魔術 IP（169.254.169.253）

AWS Well-Architected 的核心精神：託管化 (Managed Service)。
AWS 希望你將 DNS 解析的控制權從「自建 EC2 (BIND)」轉向「雲原生服務 (Route 53 Resolver)」

原本用 BIND 是為了要解析 「地端 (On-premises)」 的域名。如果你把 DNS 改回 AWS 原生，EC2 雖然看得到 EFS 了，卻會變成看不見地端伺服器。

把 VPC 的 DHCP Options Set 改回 AmazonProvidedDNS

為了補足「改回原生 DNS」後的缺口，我們需要一個機制讓 AWS DNS (169.254.169.253) 知道：「嘿！如果遇到地端的域名，請幫我轉發出去問地端的 DNS。」

Outbound Endpoint 的角色： 它是一個出口，讓 AWS 的原生 DNS 請求可以「打出去」到 VPC 外部（地端或中央 BIND）。

Forwarding Rule (轉發規則)： 你設定一條規則說「遇到 corp.internal 就走 Outbound Endpoint」。

RAM (資源共享)： 為了讓組織內的所有 VPC 都具備這個「自動轉發」能力，你用 RAM 把這條規則分享出去。