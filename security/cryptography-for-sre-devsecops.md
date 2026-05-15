# 給 SRE / DevSecOps 工程師的密碼學筆記

> 更新：2026-05-14
> 定位：Cloud Platform / SRE Engineer with DevSecOps + FinOps capability
> 姊妹篇（理論）：[cryptography-core-theory.md](./cryptography-core-theory.md) — 「為什麼這個算法是安全的、黑盒裡面在做什麼」
> 上層脈絡：[`devops-homelab/security/plan.md`](../../devops-homelab/security/plan.md)、[`devops-homelab/projects/secure-finops-k8s-platform/plan.md`](../../devops-homelab/projects/secure-finops-k8s-platform/plan.md)

這份筆記不是密碼學教科書，也不是 CTF 題解。
它的目標是把「密碼學」這個聽起來像數學家的東西，**轉譯成 SRE / DevSecOps 工程師每天會碰到的決策題**：

- 為什麼 TLS 握手會卡在某個 cipher suite？
- 為什麼 K8s Secret 不是 secret？
- 為什麼憑證輪替（cert rotation）會把 production 弄掛？
- 為什麼 supply chain attack 時代，image signing 變成必修？
- 為什麼 KMS / HSM / Envelope encryption 是雲端架構面試常考？

如果這些問題你回答得不夠順，那這份筆記就是寫給你的。

---

## 目錄

- [0. TL;DR — 一頁速覽](#tldr)
- [1. 為什麼 SRE / DevSecOps 一定要學密碼學](#why-crypto)
- [2. 密碼學核心地圖（六塊積木）](#crypto-map)
- [3. TLS / mTLS / 憑證鏈：你每天在用的密碼學](#tls)
- [4. Secrets、KMS、Envelope Encryption](#secrets-kms)
- [5. Identity、JWT、OIDC、簽章](#identity)
- [6. Supply Chain Security：image signing、SBOM、Sigstore](#supply-chain)
- [7. Cloud / Kubernetes 對應地圖](#cloud-k8s-map)
- [8. 常見錯誤與決策原則](#pitfalls)
- [9. 學習路線：先實務、再原理、最後進階](#learning-path)
- [10. Portfolio 任務：接到 Secure FinOps Platform for K8s](#portfolio)
- [11. 參考資源](#references)

---

<a id="tldr"></a>

## 0. TL;DR — 一頁速覽

| 問題 | 答案（一行版） |
|---|---|
| 為什麼要學？ | SRE/DevSecOps 每天都在用 TLS、JWT、KMS、image signing；不懂原理就只會抄 YAML |
| 學到多深就夠用？ | 不用會推導算法，但要會「選 algorithm、判斷風險、設計 key lifecycle、看懂 RFC 的摘要欄」 |
| 第一個要學的概念？ | **Hash** 不是加密；MAC 才是「驗證」；Signature 才是「驗證 + 不可否認」 |
| 第一個要懂的場景？ | TLS 1.3 握手：ECDHE → AEAD → certificate chain → SNI → ALPN |
| K8s Secret 是 secret 嗎？ | 預設不是，只是 base64；要靠 etcd encryption + KMS provider + Sealed Secrets / SOPS / External Secrets |
| 最常被問的決策？ | 「Secrets 放哪？」「symmetric 還是 asymmetric？」「key 多久輪一次？」「self-signed 還是 ACM？」 |
| 進階能力？ | image signing（Cosign / Sigstore）、SLSA provenance、SBOM、policy gate（Kyverno / OPA） |
| 不用碰？ | 自己實作 cipher、自己設計 protocol、量子密碼學數學（除非你轉做 security research） |

---

<a id="why-crypto"></a>

## 1. 為什麼 SRE / DevSecOps 一定要學密碼學

### 1.1 你不是研究員，但你是「密碼學的使用者 + 把關者」

工程師可分三層：

```text
數學家 / 研究員 → 設計 algorithm（AES、SHA-3、ECC、ML-KEM）
協定設計者     → 把 algorithm 組成 protocol（TLS、IKE、SSH、OIDC）
工程師（你）   → 部署、維運、整合、選擇、把關
```

你不需要會推導 AES 的 S-box，但你需要：

- 知道 **TLS 1.2 vs 1.3 差在哪、為什麼面試會問**
- 知道 **AES-GCM 比 AES-CBC 安全在哪、什麼時候不能用 GCM**
- 知道 **ECDSA 跟 Ed25519 為什麼後者比較常被推薦**
- 知道 **bcrypt / scrypt / argon2id 為什麼比 SHA256 適合存密碼**
- 知道 **「我的 cert 是怎麼從 root CA 一路簽到 leaf」**

這些不是學究議題，是 SRE on-call 排錯與 DevSecOps audit 會直接撞到的問題。

### 1.2 從你的職涯主軸來看 — 為什麼這條線值得投資

對照你目前的方向（AWS SAA、Linux、Terraform、K8s 進行中，往 Platform / SRE 收斂）：

| 你的能力 | 密碼學知識補進去後變什麼 |
|---|---|
| AWS（IAM、KMS、ACM、Secrets Manager） | 從「會勾選 console」升級到「能解釋為什麼 KMS 用 envelope encryption、為什麼 ACM 不能 export private key」 |
| Terraform | 能設計 secret pipeline，懂得 `state` 為什麼必須加密、`tfvars` 為什麼不該進 git |
| Linux RHEL | 看得懂 `/etc/ssl`、`openssl s_client` debug、SSH key pair、auditd 與簽章日誌 |
| Kubernetes | 能解釋 cert-manager、ServiceAccount token、mTLS service mesh、image signing、Secrets encryption-at-rest |
| FinOps | 能評估「加密成本」：KMS API 呼叫費用、HSM 月費、TLS terminate 的 CPU 成本 |

這不是另一條學習主線，而是**讓你既有的雲端技術棧獲得「為什麼」的解釋力**。
面試官最在意的不是你會勾哪個 checkbox，而是你能不能在 incident 當下講出「這個 cert 為什麼會 expire、為什麼 rotate 後 mTLS 整片掛掉」。

### 1.3 工作場景驅動：什麼時候你會用到？

| 場景 | 你會被問什麼 |
|---|---|
| TLS 憑證過期，服務掛了 | 怎麼監控？怎麼 graceful rotate？為什麼 staple OCSP？ |
| 客戶端 mTLS 失敗 | 是 CA chain 不對？SAN 不對？clock skew？trust store？ |
| K8s ServiceAccount token 被打包進 image | 為什麼這是漏洞？怎麼用 projected token 修？ |
| GitHub Actions secret 外洩 | 為什麼 OIDC federation 比 long-lived AWS key 安全？ |
| 客戶問 GDPR / ISO27001 | 「我們的資料是怎麼加密的？key 誰持有？rotation 政策？」 |
| FinOps 報表暴漲 | KMS request 計費為什麼會 spike？怎麼快取 data key？ |
| Image 來源不明 | 怎麼證明這個 image 是我們 CI 產出的？SLSA level 是多少？ |

每一題背後都不是「裝個工具就好」，而是「先理解原理，再做工程決策」。

---

<a id="crypto-map"></a>

## 2. 密碼學核心地圖（六塊積木）

把密碼學想成六塊樂高積木。後面所有 protocol（TLS、SSH、JWT、Cosign）都是這六塊的不同組合。

```text
┌──────────────────────────────────────────────────────┐
│ 1. Hash         單向、定長指紋          SHA-256 / SHA-3 │
│ 2. MAC          帶 key 的指紋（驗完整性） HMAC-SHA256    │
│ 3. Symmetric    對稱加密（兩端共用 key）  AES-GCM / ChaCha20 │
│ 4. Asymmetric   非對稱（公鑰/私鑰）       RSA / ECDH / ECDSA │
│ 5. Signature    非對稱簽章（驗來源+完整） Ed25519 / RSA-PSS │
│ 6. KDF / RNG    從密碼/熵衍生 key        HKDF / Argon2id │
└──────────────────────────────────────────────────────┘
```

### 2.1 Hash — 一切的起點

**性質：**
- 任意長度輸入 → 固定長度輸出
- 單向（不可反推）
- 一點點變動 → 完全不同的輸出（avalanche effect）
- 抗碰撞（找不到兩個輸入產生一樣 hash）

**SRE 場景：**

| 用途 | 算法 |
|---|---|
| 檔案完整性（download SHA-256） | SHA-256 |
| Git commit ID | SHA-1（即將汰換到 SHA-256） |
| Container image digest | SHA-256（`sha256:abc...`） |
| ETag / content-addressable storage | SHA-256 |
| 密碼儲存 | ❌ **不要用 SHA-256**，要用 Argon2id / bcrypt（見 §2.6） |

**重要區分：Hash ≠ 加密。** Hash 不可逆、沒有 key。它只能「驗證一個東西是不是你預期那個」，不能拿來保護機密。

### 2.2 MAC — 帶 key 的 hash

MAC（Message Authentication Code）= Hash + Key。

**為什麼需要 MAC？**

Hash 只能驗「資料沒變」，不能驗「資料是誰發的」。
攻擊者可以同時改資料 + 改 hash。

MAC 需要 key，攻擊者沒有 key 就改不出新的 MAC。

**最常見：HMAC-SHA256。**

**SRE 場景：**
- AWS API 簽章（`AWS4-HMAC-SHA256`）
- Webhook 簽章（GitHub webhook 的 `X-Hub-Signature-256`）
- JWT 的 HS256 算法
- session cookie 防竄改

### 2.3 Symmetric Encryption — 對稱加密

兩端共用同一把 key，速度快，但「key 怎麼交換」是難題。

**現代首選：AEAD（Authenticated Encryption with Associated Data）**

```text
AEAD = Encrypt + MAC 一次完成
代表：AES-GCM、ChaCha20-Poly1305
```

**為什麼一定要 AEAD？**

舊的 AES-CBC 只加密、不驗完整性，要另外加 MAC，順序錯了會出現 padding oracle attack（POODLE、Lucky13 等實戰漏洞）。
AEAD 把這兩件事綁在一起做完，少一個犯錯空間。

**SRE 場景：**
- TLS 1.3 的 record layer（強制 AEAD）
- LUKS / dm-crypt（磁碟加密）
- VPN（WireGuard 用 ChaCha20-Poly1305）
- 應用層 envelope encryption 的「資料加密」那一層

**注意：nonce 不能重複。** AES-GCM 同一把 key 下重複用同一個 nonce，可以直接被破。所以 nonce 通常用 counter 或 random + sequence。

### 2.4 Asymmetric — 非對稱密鑰

每個人有一對 key：**public key（公開）+ private key（自己藏）**。

兩種用途：

1. **加密 / 金鑰交換（Key Exchange）：** 用對方 public key 加密 → 只有對方 private key 解得開。代表：RSA-OAEP、ECDH。
2. **簽章（Signature）：** 用自己 private key 簽 → 任何人用你 public key 都可以驗。代表：RSA-PSS、ECDSA、Ed25519。

**現代推薦：**

| 用途 | 推薦 | 為什麼 |
|---|---|---|
| Key exchange | **X25519**（ECDH on Curve25519） | 安全、快、抗 side channel |
| Signature | **Ed25519** | 比 ECDSA 安全（不需要隨機 nonce）、快、key 短 |
| 與舊系統相容 | RSA-2048 / RSA-3072 | 還沒淘汰但運算慢、key 長 |
| **不要用** | RSA-1024、SHA-1、ECDSA with bad RNG | 已不安全 |

**為什麼非對稱不直接用來加密大資料？**

因為慢。實務上一律 **「非對稱交換 key，對稱加密內容」**（hybrid encryption）。TLS、PGP、Envelope encryption 全部都是這個模式。

### 2.5 Signature — 簽章

**簽章 = 加上「不可否認性（non-repudiation）」**

MAC 雙方共用 key，誰都可以偽造，所以無法在法律意義上「證明是誰發的」。
簽章用 private key 簽，private key 只有你有，所以你發的東西別人偽造不出來。

**SRE / DevSecOps 場景：**
- TLS 憑證（CA 用 private key 簽 leaf cert）
- JWT 的 RS256 / ES256
- container image signing（Cosign 用 ECDSA 或 Ed25519）
- Git commit signing（GPG / SSH）
- package signing（apt repo、rpm repo）
- SBOM、SLSA provenance attestation

### 2.6 KDF / RNG — 密鑰衍生與隨機數

**KDF（Key Derivation Function）：把「密碼」或「共享 secret」變成「對稱 key」。**

兩種用途：

1. **Password hashing：** 從使用者密碼產出儲存用的「慢 hash」。代表：**Argon2id**（首選）、bcrypt、scrypt。為什麼慢是好事？因為攻擊者也要慢。
2. **Key derivation：** 從 master secret 衍生多支 key。代表：**HKDF（HMAC-based KDF）**。TLS 1.3、Signal Protocol 都用它。

**RNG / Entropy：**
- 一切密碼學的基礎都靠「夠隨機」
- Linux：`/dev/urandom`、`getrandom(2)`
- 容器 / VM 的 entropy 不足是早年的真實 bug（boot 時 SSH host key 太弱）
- 雲端：依賴 hypervisor 的 RDRAND、virtio-rng

**常見錯誤：** 用 `rand()`、`Math.random()` 生 token 或 nonce — **永遠錯**。生產 token 必用 `crypto/rand`（Go）、`secrets`（Python）、`crypto.randomBytes`（Node）。

---

<a id="tls"></a>

## 3. TLS / mTLS / 憑證鏈：你每天在用的密碼學

TLS 是你每天 debug 最多次、但最常被「魔法解釋」的協定。
這節把它拆成 SRE 真的會碰到的決策點。

### 3.1 TLS 1.2 vs 1.3 — 為什麼大家都在升級

| 比較 | TLS 1.2 | TLS 1.3 |
|---|---|---|
| 握手 RTT | 2-RTT | 1-RTT（0-RTT 可選） |
| Cipher suite | 大雜燴，可選 weak cipher | 只剩 5 個 AEAD-only |
| Key exchange | RSA / DHE / ECDHE | **強制 ECDHE / DHE**（forward secrecy） |
| Forward secrecy | 可選 | 強制 |
| 簽章在握手 | 對 ClientHello/ServerHello 簽 | 對 transcript 簽，防降級 |
| SNI 加密 | 明文 | ECH（Encrypted Client Hello，新版） |

**面試重點 — Forward Secrecy：** 即使日後 server private key 外洩，**過去抓的封包也解不開**，因為當時的 session key 是 ECDHE 臨時產生、用完即丟。這是現代 TLS 的核心安全保證。

### 3.2 一次 TLS 1.3 握手在做什麼

```text
Client                                          Server
  |--- ClientHello ----------------------------->|
  |    + key_share (ECDHE pub)                   |
  |    + cipher_suites                           |
  |    + SNI（要連哪個域名）                       |
  |    + ALPN（http/1.1, h2, h3）                |
  |                                              |
  |<-- ServerHello -------------------------------|
  |    + key_share（ECDHE pub）                   |
  |    + cipher chosen                           |
  |<-- {EncryptedExtensions}                     |
  |<-- {Certificate}（chain）                    |
  |<-- {CertificateVerify}（用 priv key 簽 transcript）
  |<-- {Finished}                                |
  |                                              |
  |--- {Finished} ------------------------------>|
  |======= Application Data（AEAD 加密）========|
```

握手結束時：
- 雙方算出同一把 session key（透過 ECDHE）
- Client 驗過 Server 憑證鏈
- 後續所有資料用 AEAD（AES-GCM 或 ChaCha20-Poly1305）加密

### 3.3 憑證鏈 — 為什麼面試官愛問

```text
Root CA (self-signed)        ←  存在 OS / 瀏覽器 trust store
  └── Intermediate CA        ←  CA 用這把日常簽，root 離線保管
        └── Leaf cert        ←  你的 server cert
              + SAN = api.example.com, *.example.com
```

**SRE 排錯重點：**

| 症狀 | 可能原因 |
|---|---|
| `unable to get local issuer certificate` | 沒帶 intermediate；要 `fullchain.pem` 而不是只有 `cert.pem` |
| `certificate is not yet valid` | clock skew，常見於容器或 VM 時間飄移 |
| `hostname does not match` | SAN（Subject Alternative Name）沒涵蓋；現代 client 早已不看 CN |
| `unknown CA` | 你的 client 沒裝 root CA（私有 PKI 場景） |
| 突然 502 / TLS 握手失敗 | 憑證過期了，沒做監控 |

**debug 三件套：**

```bash
# 看一個 server 真實送出的 chain
openssl s_client -connect api.example.com:443 -servername api.example.com -showcerts

# 看 leaf cert 的 SAN 與到期日
openssl x509 -in cert.pem -noout -text | grep -E 'Subject:|DNS:|Not After'

# 驗整條 chain
openssl verify -CAfile root.pem -untrusted intermediate.pem leaf.pem
```

### 3.4 mTLS — 雙向驗證

TLS：client 驗 server。
mTLS：server **也** 驗 client。

**SRE 場景：**
- service mesh（Istio、Linkerd 用 mTLS 做 zero-trust east-west）
- Kubernetes API server ↔ kubelet
- internal microservices 之間
- B2B API（特別是金融）

**痛點：**
- client cert 要怎麼發？怎麼輪替？
- private CA 要怎麼維護？
- service mesh 把這層自動化（SPIFFE / SPIRE 是這領域的標準身分）

### 3.5 Let's Encrypt / ACME — 自動化憑證

ACME 是 Let's Encrypt 推的 RFC 8555 protocol。核心邏輯：

```text
1. Client 產一對 key pair
2. 向 ACME server 申請：「我要 api.example.com 的 cert」
3. ACME server 回挑戰：
   - HTTP-01：在 http://api.example.com/.well-known/acme-challenge/... 放檔案
   - DNS-01：在 _acme-challenge.api.example.com 加 TXT record
4. Client 完成挑戰
5. ACME server 簽 cert 給 Client
6. 90 天到期前，自動 renew
```

**為什麼 DNS-01 更強：**
- 可以簽 wildcard（`*.example.com`）
- 不用對外 expose 80 port
- 適合內網服務

**K8s 場景：** cert-manager + ClusterIssuer + Ingress annotation，自動 issue + auto-renew。
**AWS 場景：** ACM 完全託管，但 **不能 export private key**，所以只能配合 ELB / CloudFront / API Gateway 用；EC2 上你自己跑的 nginx 拿不到。

---

<a id="secrets-kms"></a>

## 4. Secrets、KMS、Envelope Encryption

「Secrets 放哪？」是 DevSecOps 面試最常見的開放題。
答案不是某個工具，而是一套 **decision framework**。

### 4.1 K8s Secret 不是 secret

預設行為：
- etcd 裡是 **base64**，不是加密
- 任何能 `get secrets` 的人都能讀
- node 上 mount 成 tmpfs，能 exec 進 pod 就拿得到

**要達到「真的有保護」需要四層：**

1. **etcd encryption-at-rest**：API server 啟用 `--encryption-provider-config`，搭配 KMS provider
2. **RBAC**：嚴格限制誰能 `get / list / watch secrets`
3. **Pod 隔離**：Pod Security Standards / NetworkPolicy 限制 lateral movement
4. **不要把 secret 印進 log 或 env dump**

### 4.2 Secrets 的決策矩陣

| 工具 | 適用情境 | 取捨 |
|---|---|---|
| K8s Secret（原生） | 簡單 lab、與 ConfigMap 同層級管理 | 沒加密層、沒輪替、沒 audit |
| Sealed Secrets | GitOps：把加密後的 secret 放 git 是安全的 | 控制器離線無法解、key 管理仍要做 |
| SOPS（Mozilla） | terraform / ansible / git-friendly | 跨工具好用、需配 KMS / age key |
| External Secrets Operator | secret 真正住在外部（Vault、AWS SM、GCP SM） | 邏輯乾淨，但多一個依賴 |
| HashiCorp Vault | 大型組織、動態 secret、PKI | 強大但運維成本不低 |
| AWS Secrets Manager / SSM Parameter Store | 純 AWS 環境 | 整合最順，按次計費 |

**面試經典題：「為什麼不直接把 .env 放 git？」**

答案要層次清楚：
1. 一旦進 git 歷史就拔不掉（rotation 才是補救）
2. 沒有 RBAC、沒有 audit log
3. fork / mirror / 備份會擴散
4. CI logs、container layer 容易帶出去
5. 正確做法是 secret 放管理系統，CI 透過短期 token 拉取

### 4.3 KMS 與 Envelope Encryption — 雲端面試必考

**為什麼不直接用 KMS 加密大檔案？**
- KMS 有大小限制（AWS KMS 4 KB）
- KMS 每次 call 都計費（FinOps 上不可忽視）
- 延遲高

**Envelope Encryption（信封加密）：**

```text
Plaintext (10 GB)
  └── 用 Data Key（DEK，本地產生）── AES-GCM ─→ Ciphertext (10 GB)
                                                     |
        DEK                                          |
         └── 用 KMS 的 CMK ────加密─→ Encrypted DEK  |
                                                     ↓
                                       存：Encrypted DEK + Ciphertext
```

讀回來時：
1. 把 Encrypted DEK 丟給 KMS decrypt → 拿回 DEK
2. 用 DEK 解 Ciphertext

**好處：**
- KMS 只處理小小的 DEK，CPU 與費用都小
- DEK 可以快取（限期）省 KMS call
- CMK 不離開 KMS，誰拿到 Encrypted DEK 沒 KMS 權限也沒用

**AWS 真實案例：** S3 SSE-KMS、EBS encryption、RDS encryption、Secrets Manager 全都是 envelope。
**K8s 場景：** etcd encryption provider 用 KMS 就是這個架構（kube-apiserver 端 cache DEK）。

### 4.4 Key Lifecycle — 一張你必須背的表

| 階段 | 動作 | 注意 |
|---|---|---|
| Generation | HSM / KMS 產生，不離開硬體 | 不要自己用程式碼 random |
| Distribution | 透過短期 token、IAM role、OIDC | 不要靠長期 access key |
| Usage | 最小權限，按用途分 key | 一支 key 不要既加密又簽章 |
| Rotation | 定期輪替（30/90/365 天） | 新舊 key 共存期要設計好 |
| Revocation | 立即停權，audit who used it | 不只是停用，還要追溯影響 |
| Destruction | KMS schedule deletion（7-30 天） | 一旦刪除，加密資料就永久喪失 |

**Rotation 不只是「換 key」，是設計題：**
- 舊 key 還要能解過去資料嗎？（通常要）
- 在 rotation grace period 內，新舊 key 都能驗 / 解嗎？
- 怎麼知道誰還在用舊 key？（CloudTrail / audit log）
- 自動化還是手動？

---

<a id="identity"></a>

## 5. Identity、JWT、OIDC、簽章

身分驗證是 DevSecOps 的核心。這節把 JWT / OIDC / SAML 從密碼學角度講清楚。

### 5.1 JWT — 結構與密碼學在哪

```text
HEADER.PAYLOAD.SIGNATURE

eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJ1c2VyMSJ9.MEUCIQ...
   base64url(JSON)   base64url(claims)    base64url(signature)
```

**HEADER：** `{"alg":"RS256","typ":"JWT"}`
**PAYLOAD：** `{"sub":"user1","iss":"...","aud":"...","exp":..., "iat":...}`
**SIGNATURE：** 對 `HEADER.PAYLOAD` 做 MAC 或簽章

**算法分兩派：**

| 類型 | 算法 | Key | 用途 |
|---|---|---|---|
| **對稱（MAC）** | HS256 | 兩端共用 shared secret | 同一個服務內部、簡單情境 |
| **非對稱（Signature）** | RS256 / ES256 / EdDSA | issuer 持 private key，consumer 持 public key | OIDC、跨服務、IdP 模式 |

**JWT 安全陷阱（面試經典）：**

1. **`alg: none` 攻擊** — 老 library 會接受 `{"alg":"none"}` 直接放行
2. **算法混淆** — 偽造 `alg: HS256`，把 server 的 RSA public key 當作 HMAC secret
3. **沒驗 `exp` / `aud` / `iss`** — token 是有效的但本不該在這個 service 用
4. **不對稱 key 選 RS256 時 key 太短** — 至少 2048 bits

### 5.2 OIDC — 從密碼學角度看

OIDC = OAuth 2.0 + Identity Layer（用 JWT 表達身分）。

```text
[User] ─── login ──→ [IdP（Google / Keycloak / GitHub / AWS Cognito / Azure AD）]
                          │
                          │ 1. 驗證身分
                          │ 2. 簽 ID Token（JWT，RS256）
                          ↓
[Your App] ←── ID Token + Access Token
   │
   └── 用 IdP 的 public key（JWKS endpoint）驗簽
```

**SRE / DevSecOps 場景**（這是現代 cloud 的關鍵）：

| 情境 | OIDC 角色 |
|---|---|
| GitHub Actions → AWS | Actions 是 IdP，AWS IAM 信任它，**短期 token 換 IAM role** |
| GitLab CI → AWS / GCP | 同上 |
| Vault → K8s | K8s ServiceAccount JWT 給 Vault，換 secret |
| AWS EKS IRSA | ServiceAccount token 經由 OIDC provider 換 IAM role |
| GCP Workload Identity | 一樣概念 |

**為什麼這比「把 access key 存 secret」好？**
- 沒有長期 secret，鑰匙根本不存在
- IdP 端可以 audit 誰換了 token
- IAM 策略可以限制「只接受來自這個 repo 的這個 branch」

### 5.3 SAML — 為什麼還沒死

SAML 用 XML 簽章（XML-DSig），密碼學上比 JWT 古老但仍主流：

- 企業 SSO（Okta、ADFS、Azure AD）依然 SAML 為主
- AWS IAM Identity Center 同時支援 SAML 與 OIDC
- XML 簽章有歷史悠久的 XML signature wrapping 漏洞，library 設定很重要

對你而言：知道兩個共存即可，新東西優先用 OIDC + JWT。

### 5.4 SSH key — 你每天在用的非對稱密碼學

```text
ssh-keygen -t ed25519 -C "you@host"
↓
~/.ssh/id_ed25519      (private key，自己藏)
~/.ssh/id_ed25519.pub  (public key，丟到伺服器的 authorized_keys)
```

**為什麼推 Ed25519 不推 RSA：**
- 比 RSA-2048 安全（128-bit 等級 vs 112-bit）
- key 更短（68 字元 vs 540 字元）
- 簽章速度快
- 沒有 RNG 弱點（ECDSA 那種）

**進階：**
- SSH certificate（用 CA 簽，比 authorized_keys 列表好維運）
- agent forwarding 的風險（jump host 上有人能用你的 key）
- hardware key（YubiKey + ssh-ed25519-sk）

---

<a id="supply-chain"></a>

## 6. Supply Chain Security：image signing、SBOM、Sigstore

SolarWinds、Log4Shell、xz-utils backdoor 之後，**供應鏈安全變成 DevSecOps 必修**。
這節是最有「現代感」、面試最有差異化的部分。

### 6.1 為什麼 supply chain 是密碼學問題

核心問題：「我跑的這個 binary / image，真的是我們團隊產的嗎？」

如果沒有簽章與可驗證的 build provenance：
- 攻擊者可以悄悄塞 backdoor 到上游 npm / PyPI / DockerHub
- CI/CD 流水線本身被入侵（typosquatting、dependency confusion）
- registry 被替換（mirror、registry poisoning）

**解法 = 用密碼學簽章把「來源 → build → artifact」綁起來。**

### 6.2 Cosign / Sigstore — 把簽 image 變簡單

傳統做法：你要自己管 GPG / X.509 key，怎麼用、怎麼輪、怎麼撤銷都麻煩。

**Sigstore 的革新：keyless signing**

```text
1. 你用 OIDC 登入（Google / GitHub / Microsoft）
2. Fulcio CA 短期簽一張只活 10 分鐘的憑證給你
3. 用這張憑證簽 image
4. 簽章 + 憑證紀錄丟到 Rekor（透明日誌，append-only）
5. 任何人可以查 Rekor 驗證「這個 image 是誰、什麼時候簽的」
```

短期 cert → 不用管私鑰，過期就死。
透明日誌 → 攻擊者就算偷簽，全世界都看得到。

**典型 CI/CD 整合：**

```bash
# 在 GitHub Actions 裡（OIDC token 自動可用）
cosign sign --yes ghcr.io/me/myapp@sha256:abc...

# 部署前驗證
cosign verify ghcr.io/me/myapp@sha256:abc... \
  --certificate-identity-regexp ".*@example.com" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com"
```

### 6.3 SBOM — 你裝了什麼

SBOM（Software Bill of Materials）= 一份 image / artifact 內所有套件、版本、licence 的清單。

**為什麼重要：**
- Log4Shell 那一週，「我們有沒有用到 log4j 2.x？」這個問題沒人答得出來
- 有 SBOM 之後，你可以 grep 出全公司影響面

**工具：**
- Syft（產 SBOM）
- Grype / Trivy（拿 SBOM 比對 CVE）
- 格式：SPDX、CycloneDX

**進階：把 SBOM 簽起來** — 用 Cosign attestation，讓 SBOM 本身也不可竄改。

### 6.4 SLSA — 供應鏈成熟度框架

SLSA（Supply-chain Levels for Software Artifacts，Google 推、現由 OpenSSF 維護）把成熟度分四級：

| Level | 重點 |
|---|---|
| L1 | Build 有 documented process，產 provenance |
| L2 | Provenance 由 hosted build service（GitHub Actions、GitLab CI）簽 |
| L3 | Source / build 隔離、無人能 inject、provenance 不可偽造 |
| L4 | Two-person review、hermetic build、reproducible build |

對你的 portfolio 來說：**做到 L2 已經比 99% 的小團隊強**，且可以寫進履歷。

### 6.5 Policy Gate — Kyverno / OPA Gatekeeper

光簽章沒用，還要在「部署當下」強制驗證。

```yaml
# Kyverno 例：只允許簽過名的 image 進 cluster
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-signed-images
spec:
  validationFailureAction: Enforce
  rules:
    - name: verify-signature
      match:
        any:
          - resources:
              kinds: [Pod]
      verifyImages:
        - imageReferences: ["ghcr.io/me/*"]
          attestors:
            - entries:
                - keyless:
                    issuer: "https://token.actions.githubusercontent.com"
                    subject: "https://github.com/me/myapp/.github/workflows/*"
```

這個 policy 把「密碼學驗證」變成 **admission controller 層的 SRE/Platform 守門**。

---

<a id="cloud-k8s-map"></a>

## 7. Cloud / Kubernetes 對應地圖

把上面所有概念對應到你既有的技術棧，**這張表是面試前的速查**。

### 7.1 AWS

| 概念 | AWS 服務 | 你要記住的事 |
|---|---|---|
| 公網 TLS 憑證 | ACM | 託管、自動 renew、**不能 export priv key**，只能配 ELB / CloudFront / API Gateway |
| 私有 PKI | ACM Private CA | 內網 mTLS 用、按 CA + 簽張數計費 |
| 對稱 key 管理 | KMS（symmetric CMK） | envelope encryption 的中心，按 request 計費 |
| 非對稱 key | KMS asymmetric CMK | 簽 / 驗、加密 / 解密；不能拿來搭 TLS |
| Secrets | Secrets Manager / SSM Parameter Store | SM 有 rotation，SSM 便宜但 rotation 要自己做 |
| 短期憑證 | STS、IAM role、AssumeRole | 短期 token 是雲端身分的主軸 |
| OIDC federation | IAM Identity Provider | GitHub Actions / EKS IRSA 都靠它 |
| 加密磁碟 / S3 | EBS encryption / S3 SSE-KMS、SSE-S3、SSE-C | 預設 KMS envelope；SSE-C 要自己管 key |
| CloudHSM | 硬體 HSM | 法規場景（FIPS 140-2 L3）、自己持 key |
| Audit | CloudTrail（KMS / Secrets Manager 都會記） | 加密事件可追溯 |

### 7.2 Kubernetes

| 概念 | K8s 元件 / 工具 | 你要記住的事 |
|---|---|---|
| API server ↔ kubelet | 內建 TLS / mTLS | kubeconfig 裡的 cert 過期是常見災難 |
| Pod ↔ Pod TLS | Service mesh（Istio / Linkerd） | mTLS by default、SPIFFE ID 為身分 |
| 公網 / 內網 TLS | Ingress + cert-manager | 自動簽 cert（Let's Encrypt or Private CA） |
| Secret encryption-at-rest | etcd encryption provider | 沒設定的話 etcd 是 base64 |
| Secret 來源 | External Secrets Operator | 把 Vault / AWS SM 變成 K8s Secret |
| GitOps secret | Sealed Secrets / SOPS | secret 上 git 才安全的兩條路 |
| ServiceAccount token | projected token（OIDC） | 短期、bound to pod、可給 AWS IRSA / Vault |
| Image signing | Cosign + Kyverno policy | admission 層擋未簽 image |
| Pod 限制 | Pod Security Admission | privileged / runAsRoot 限制 |
| Audit | API server audit log | 誰 get 了哪個 secret |

### 7.3 Terraform / IaC

| 場景 | 做法 |
|---|---|
| State file 加密 | S3 backend + SSE-KMS + versioning + DynamoDB lock |
| 不把 secret 寫進 `.tf` | 用 `data.aws_secretsmanager_secret_version`、TF_VAR_、SOPS |
| Provider 認證 | OIDC（GitHub Actions assume role），不要 long-lived AK |
| Module 完整性 | 用 registry 或 git tag + checksum 驗證 |
| Drift detection | 加密狀態下 plan 出現差異要警覺 |

### 7.4 Linux Host（你的 RHEL 主場）

| 工具 / 路徑 | 用途 |
|---|---|
| `/etc/ssl/certs/`、`update-ca-trust` | 系統 trust store；自己加私有 CA 走這裡 |
| `openssl s_client / x509 / verify / req` | TLS / 憑證的 debug 瑞士刀 |
| `ssh-keygen -t ed25519` | 不要再產 RSA-2048 了 |
| `dm-crypt / LUKS` | 全磁碟加密（AES-XTS） |
| `gpg --sign / --verify` | 套件簽章、敏感檔簽章 |
| `auditd` | 把「誰碰了 key」記下來，配合 ELK 變成輕量 SIEM |

---

<a id="pitfalls"></a>

## 8. 常見錯誤與決策原則

這節整理「能拿來在 PR review、code review、設計 review 直接引用」的判斷依據。

### 8.1 Algorithm 選擇 — 一個簡單原則：跟著現代預設走

| 任務 | 用 | 不要用 |
|---|---|---|
| Hash 完整性 | SHA-256、SHA-3 | MD5、SHA-1 |
| Password 儲存 | **Argon2id**（首選）、bcrypt、scrypt | SHA-256、MD5、未加 salt 的任何 hash |
| 對稱加密 | AES-GCM、ChaCha20-Poly1305（AEAD） | AES-CBC 沒 MAC、AES-ECB、DES、3DES |
| 簽章 | Ed25519、ECDSA P-256、RSA-PSS | RSA-PKCS#1 v1.5、ECDSA with bad RNG |
| Key exchange | X25519、ECDH P-256 | DH-1024、RSA key transport |
| Random / token | `crypto/rand`、`secrets`、`crypto.randomBytes` | `Math.random()`、`rand()`、time-based |
| KDF | HKDF、Argon2id | 自己拼 SHA(SHA(SHA(...))) |
| TLS 版本 | 1.3，最低 1.2 | 1.0、1.1、SSL v3 |
| JWT alg | RS256、ES256、EdDSA | none、HS256 mix RS256 |

### 8.2 Key & Cert Lifecycle 的設計題

每個 key / cert 都要回答：

1. **Generation：** 哪裡產？誰能用？
2. **Storage：** 在哪？誰能讀？備份在哪？
3. **Usage：** 用在哪些場景？每個場景一支還是共用？
4. **Rotation：** 多久輪一次？grace period 多長？怎麼自動化？
5. **Revocation：** 出事了怎麼撤？多快？影響哪些 component？
6. **Monitoring：** 還剩多久過期？誰用過？

寫設計文件時這六題每題都要答得出來。

### 8.3 常見地雷

| 反 pattern | 為什麼錯 | 正確做法 |
|---|---|---|
| 把 `.env` push 到 git | 一進 history 就拔不掉 | secret 進 secret manager，CI 用 OIDC 拉 |
| TLS 1.0 / 1.1 沒關 | 已知不安全 | 強制 TLS 1.2+，最好 1.3 |
| 自己實作 crypto | 一定會錯 | 用 vetted library |
| 用 SHA-256 存密碼 | GPU 一秒幾億 hash | Argon2id |
| ECDSA 隨機 nonce 重複 | 直接洩漏 private key（PS3 事件） | Ed25519，或用 RFC 6979 deterministic |
| 不驗 cert（`InsecureSkipVerify`） | MITM 大開門 | 真的有 self-signed 就把 cert 加 trust |
| AWS access key 寫死在 image | 一被偷影響全公司 | IAM role + STS + OIDC |
| K8s Secret 不加 etcd encryption | etcd 備份 = 全部 secret | 啟用 KMS provider |
| 把 KMS key policy 開太寬 | 全 account 都能 decrypt | 最小權限、限定 source ARN |
| Cosign 簽完不驗 | 等於沒簽 | admission policy 強制驗 |

---

<a id="learning-path"></a>

## 9. 學習路線：先實務、再原理、最後進階

我給你的順序刻意**反教科書**：教科書從數學起手，工程師應該從場景起手。

### Phase 1 — 把你天天用的東西看懂（2-3 週）

目標：能在面試講出「TLS 握手在幹嘛、KMS envelope 怎麼運作」。

- [ ] 用 `openssl s_client` 解一次大型網站的 TLS chain
- [ ] 把 nginx HTTPS 設定從零跑通，包含 Let's Encrypt + auto-renew
- [ ] 用 `jwt.io` 拆一個真實 JWT，自己用 RS256 簽 / 驗一次
- [ ] 在 AWS console 玩 KMS：create CMK、encrypt / decrypt，看 CloudTrail
- [ ] 跑一次 SSE-KMS S3 物件，理解 envelope 在哪一層
- [ ] 在 K8s 用 cert-manager 自動發 cert 給 Ingress

### Phase 2 — 補概念（2-3 週）

目標：能看懂 RFC 摘要、能在 design review 講「為什麼選這個演算法」。

- [ ] 讀過一次：[Cryptography Engineering（Ferguson, Schneier, Kohno）](https://www.schneier.com/books/cryptography-engineering/) 的前 6 章（不要被章節嚇到，挑重點讀）
- [ ] 跑過一次：[Cryptopals Set 1-2](https://cryptopals.com/)（很經典，理解「為什麼 ECB 爛、padding oracle 怎麼運作」）
- [ ] 看完 [Real World Cryptography（David Wong）](https://www.manning.com/books/real-world-cryptography) 的前半（這本是「給工程師的」聖經）
- [ ] 對 TLS 1.3 的 [RFC 8446](https://datatracker.ietf.org/doc/html/rfc8446) 至少讀 §1-2 + §4 摘要

### Phase 3 — DevSecOps 場景深掘（3-4 週）

目標：portfolio 能講「我做了 supply chain hardening」。

- [ ] 在 homelab 跑 Cosign keyless signing + Rekor 驗證
- [ ] 用 Syft 產 SBOM、用 Grype 驗 CVE
- [ ] 在 K8s 跑 Kyverno policy：只接受簽過名的 image
- [ ] 部署 cert-manager + private CA，自己發 mTLS cert
- [ ] EKS IRSA / GitHub Actions OIDC：把長期 AWS key 從 CI 移除
- [ ] 部署 External Secrets Operator 連 AWS Secrets Manager
- [ ] 寫一份 secret inventory（哪些 secret 存在哪、誰管、多久輪）

### Phase 4 — 進階與選修

選自己有興趣的方向；不一定全做。

| 方向 | 內容 |
|---|---|
| Service mesh + SPIFFE | Istio mTLS 一條龍、SPIRE 身分管理 |
| Vault 深入 | dynamic secret、PKI engine、Transit engine |
| Post-quantum | ML-KEM / ML-DSA 已標準化，TLS 開始 hybrid，知道意思就好 |
| Confidential computing | SEV / TDX / Nitro Enclave、attestation |
| Zero-knowledge proof（淺嚐） | 知道用途即可，不是 SRE 主線 |
| FIPS 140-2 / 140-3 | 進金融 / 政府 / 醫療有差 |

**避免：** 拿密碼學去做 Web3 / 通用區塊鏈研究 / 純數學論文 — 那是另一條路線，跟 Cloud Platform 主軸沒交集。

---

<a id="portfolio"></a>

## 10. Portfolio 任務：接到 Secure FinOps Platform for K8s

把這份筆記「落地」到 `devops-homelab/projects/secure-finops-k8s-platform/`，
讓密碼學知識變成可以寫進履歷、可以 demo 給面試官的真實作品。

### 10.1 對應 [secure-finops-k8s-platform/plan.md](../../devops-homelab/projects/secure-finops-k8s-platform/plan.md) 的可插入點

| Plan 中現有任務 | 加上密碼學能力後變什麼 |
|---|---|
| GitHub Actions / GHCR / ArgoCD GitOps 閉環 | + Cosign signing + Kyverno verify + SBOM attestation |
| Trivy image scan、SBOM | + Sigstore attestation + SLSA L2 provenance |
| secret inventory 與 rotation note | + KMS envelope flow 圖 + External Secrets Operator |
| K8s RBAC、NetworkPolicy、Pod Security | + projected ServiceAccount token + IRSA-like 短期 token |
| OPA / Kyverno guardrails | + 只允許簽過名 image、阻擋 default ServiceAccount |
| AWS 對照（IAM、Cost Explorer、GuardDuty） | + KMS / ACM / Secrets Manager / IAM OIDC 對應表 |

### 10.2 建議新增的 lab 任務（4-6 個，可挑著做）

1. **Lab A：Cosign keyless 簽 + Kyverno 驗**
   把 Observable E-commerce Platform 的 image 在 GitHub Actions 用 Cosign 簽，在 k3s 用 Kyverno policy 強制驗證。**Demo 點：** 攻擊者推一個沒簽的 image 進 GHCR，admission 直接擋掉。

2. **Lab B：External Secrets + AWS Secrets Manager（或 SOPS for offline）**
   把 DB 密碼從 K8s Secret 改成 ESO 拉。**Demo 點：** rotate 一次 → 不重啟 pod，30 秒內生效。

3. **Lab C：cert-manager + 私有 CA + mTLS**
   在 k3s 跑 cert-manager，自簽一個 CA，給三個 microservice 發 client/server cert，互相 mTLS。**Demo 點：** 拔掉一個 client cert → 連線立刻斷。

4. **Lab D：etcd encryption + KMS provider mock**
   啟用 K8s encryption-at-rest，用 `kms-plugin-mock` 或 [`sealed-secrets`](https://github.com/bitnami-labs/sealed-secrets) 模擬 envelope。**Demo 點：** dump etcd raw → 看 secret 是密文。

5. **Lab E：SBOM + supply-chain dashboard**
   Syft 產 SBOM、Grype 比對 CVE、結果丟 Prometheus，寫一個「CVE exposure by service」Grafana panel。**Demo 點：** 模擬 Log4Shell 入侵時的 blast radius 分析。

6. **Lab F：GitHub Actions OIDC → AWS IAM role**
   把所有 CI 的 AWS long-lived key 砍掉，全部走 OIDC。**Demo 點：** 把 access key 從 secret 拿掉、CI 還是能 deploy。

### 10.3 履歷敘事建議

把這些 lab 收斂成一段履歷上的 bullet（中英對照）：

> Designed and implemented end-to-end supply-chain security for a Kubernetes homelab platform, including Cosign keyless signing with Sigstore/Rekor, SBOM attestation, Kyverno admission policies, GitHub Actions OIDC-based AWS authentication, and KMS envelope encryption with External Secrets Operator. Eliminated all long-lived cloud credentials from CI and enforced verified-image-only deployment as cluster policy.

對應到 JD 關鍵字：DevSecOps、Supply Chain Security、KMS、Image Signing、OIDC、Zero Trust。

---

<a id="references"></a>

## 11. 參考資源

**書（給工程師的，不是教科書）：**

- *Real World Cryptography*，David Wong — 工程師密碼學第一本就讀這本
- *Cryptography Engineering*，Ferguson / Schneier / Kohno — 偏理論但仍可讀
- *Bulletproof TLS and PKI*，Ivan Ristić — TLS / PKI 唯一一本
- *Serious Cryptography*，JP Aumasson — 想再深入時讀
- *The Manga Guide to Cryptography* — 不要笑，給入門很好

**官方文件 / 標準：**

- [RFC 8446 (TLS 1.3)](https://datatracker.ietf.org/doc/html/rfc8446)
- [RFC 7519 (JWT)](https://datatracker.ietf.org/doc/html/rfc7519)
- [RFC 8555 (ACME)](https://datatracker.ietf.org/doc/html/rfc8555)
- [NIST SP 800-57（Key Management）](https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final)
- [SLSA spec](https://slsa.dev/)
- [in-toto](https://in-toto.io/)

**雲端 / K8s 文件：**

- [AWS KMS developer guide](https://docs.aws.amazon.com/kms/latest/developerguide/) — envelope encryption 那節必讀
- [Kubernetes Encrypting Secret Data at Rest](https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/)
- [cert-manager docs](https://cert-manager.io/docs/)
- [Sigstore docs](https://docs.sigstore.dev/)
- [Cosign quickstart](https://docs.sigstore.dev/cosign/signing/quickstart/)
- [Kyverno verifyImages](https://kyverno.io/docs/policy-types/verify-images/)

**動手練習：**

- [Cryptopals](https://cryptopals.com/) — 經典 8 set
- [Sigstore the easy way](https://docs.sigstore.dev/quickstart/quickstart-cosign/)
- [AWS Cryptography Specialty 證照官方教材](https://aws.amazon.com/certification/certified-security-specialty/) — 進階目標可以考慮（但不必為了它而學）

**Side line（不在主線）：**

- 量子密碼學：[NIST PQC](https://csrc.nist.gov/projects/post-quantum-cryptography) — 知道 ML-KEM / ML-DSA 已標準化，TLS 已開始 hybrid 即可
- Zero-knowledge：[zkbook](https://github.com/RustCrypto) ecosystem — 純興趣，跟你主線無關

---

## 後記 — 怎麼用這份筆記

這份筆記不是一次讀完的東西。建議用法：

1. **第一遍 skim**：把 §0 TL;DR + §2 核心地圖 + §7 對應地圖讀過一次，建立全景
2. **第二遍對照場景**：每次工作 / lab 撞到密碼學問題（cert 過期、JWT 不驗、secret 該放哪），翻到對應章節對照
3. **第三遍轉成 portfolio**：照 §10 把 lab 一個一個跑完，寫進 [`devops-homelab`](../../devops-homelab/)
4. **持續更新**：發現新地雷或新工具 → 直接加進 §8 或 §6

最終目標：你在面試或 incident review 講出「我選 Ed25519 是因為...」「我設計這個 rotation 流程是因為...」「我們 image 簽章用 keyless 是因為...」時，每句話背後都有清楚的工程理由 — 那就代表這份筆記發揮作用了。
