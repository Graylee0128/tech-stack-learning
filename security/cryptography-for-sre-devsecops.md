# 給 SRE / DevSecOps 工程師的密碼學筆記

> 更新：2026-05-15 (v2 — Part 分區、新增 5 章 IR/Observability/FinOps/Audit Log/Compliance、補 §3-§8 細節、加 Appendix 面試題庫 + on-call cheat sheet)
> 定位：Cloud Platform / SRE Engineer with DevSecOps + FinOps capability
> 姊妹篇（理論）：[cryptography-core-theory.md](./cryptography-core-theory.md) — 「為什麼這個算法是安全的、黑盒裡面在做什麼」
> 上層脈絡：[`devops-homelab/security/plan.md`](../../devops-homelab/security/plan.md)、[`devops-homelab/projects/secure-finops-k8s-platform/plan.md`](../../devops-homelab/projects/secure-finops-k8s-platform/plan.md)

---

## v2 改動摘要

| 變動 | 內容 |
|---|---|
| **結構重排** | 全書分 6 個 Part：為什麼 / 場景手冊 / Cloud-K8s / SRE 主軸 / 進階 / 學習與 Portfolio |
| **新增章** | §9 IR Playbook、§10 Observability、§11 FinOps、§12 Verifiable Log、§13 Compliance |
| **大幅擴充** | §3（cert rotation + cipher suite + OCSP/SNI/ECH）、§4（rotation + Vault Shamir）、§5（SPIFFE/DPoP）、§6（SLSA L3/VEX/GUAC）、§7（GCP + Azure） |
| **新增 Appendix** | A 面試題庫、B on-call cheat sheet、C 與理論篇交叉地圖 |

這篇不是密碼學教科書，也不是 CTF 題解。
它的目標是把「密碼學」這個聽起來像數學家的東西，**轉譯成 SRE / DevSecOps 工程師每天會碰到的決策題**：

- 為什麼 TLS 握手會卡在某個 cipher suite？
- 為什麼 K8s Secret 不是 secret？
- 為什麼憑證輪替（cert rotation）會把 production 弄掛？
- 為什麼 supply chain attack 時代，image signing 變成必修？
- 為什麼 KMS / HSM / Envelope encryption 是雲端架構面試常考？
- **(v2 新增) 私鑰外洩 24 小時 playbook 怎麼跑？**
- **(v2 新增) 加密成本怎麼算？KMS request 為什麼會 spike？**

如果這些問題你回答得不夠順，那這份筆記就是寫給你的。

---

## 目錄

### Part I — 為什麼學 + 核心地圖
- [§0 TL;DR — 一頁速覽](#tldr)
- [§1 為什麼 SRE / DevSecOps 一定要學密碼學](#why-crypto)
- [§2 密碼學核心地圖（六塊積木）](#crypto-map)

### Part II — 場景手冊
- [§3 TLS / mTLS / 憑證鏈：你每天在用的密碼學](#tls)
- [§4 Secrets、KMS、Envelope Encryption](#secrets-kms)
- [§5 Identity、JWT、OIDC、SPIFFE、簽章](#identity)
- [§6 Supply Chain Security：image signing、SBOM、Sigstore、SLSA、VEX](#supply-chain)

### Part III — Cloud / K8s 對照
- [§7 Cloud / Kubernetes 對應地圖（AWS / GCP / Azure）](#cloud-k8s-map)
- [§8 常見錯誤與決策原則](#pitfalls)

### Part IV — SRE 主軸三大新章
- [§9 Cryptographic Incident Response Playbook](#ir-playbook)
- [§10 Cryptographic Observability](#observability)
- [§11 Cryptographic FinOps](#finops)

### Part V — 進階主題
- [§12 Audit Log 與 Verifiable Log 設計](#verifiable-log)
- [§13 Compliance & Regulatory Mapping](#compliance)

### Part VI — 學習與 Portfolio
- [§14 學習路線：先實務、再原理、最後進階](#learning-path)
- [§15 Portfolio 任務：接到 Secure FinOps Platform for K8s](#portfolio)
- [§16 參考資源](#references)

### Appendices
- [A 面試題庫（Cloud / SRE / DevSecOps / FinOps）](#interview-qa)
- [B On-call Cheat Sheet（openssl / AWS CLI / kubectl）](#cheatsheet)
- [C 與理論篇的交叉地圖](#crossref)

---

<a id="tldr"></a>

# Part I — 為什麼學 + 核心地圖

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
| **(v2) Incident 必備？** | Cert 過期 / key 外洩 / KMS 誤刪的 24 小時 playbook |
| **(v2) 監控必看？** | Cert expiry、KMS API anomaly、TLS handshake failure、JWT validation 失敗率 |
| **(v2) FinOps 角度？** | KMS request 計費、CloudHSM 月費、SSE-KMS vs SSE-S3 成本差距 |
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
| **FinOps** | 能評估「加密成本」：KMS API 呼叫費用、HSM 月費、TLS terminate 的 CPU 成本 — **見 §11** |
| **SRE on-call** | Cert 過期、KMS 誤刪、key 外洩時 24 小時 playbook — **見 §9** |
| **Observability** | Cert expiry probe、KMS audit、TLS failure metrics — **見 §10** |

這不是另一條學習主線，而是**讓你既有的雲端技術棧獲得「為什麼」的解釋力**。
面試官最在意的不是你會勾哪個 checkbox，而是你能不能在 incident 當下講出「這個 cert 為什麼會 expire、為什麼 rotate 後 mTLS 整片掛掉」。

### 1.3 工作場景驅動：什麼時候你會用到？

| 場景 | 你會被問什麼 | 對應章節 |
|---|---|---|
| TLS 憑證過期，服務掛了 | 怎麼監控？怎麼 graceful rotate？為什麼 staple OCSP？ | §3 + §9.A + §10.1 |
| 客戶端 mTLS 失敗 | 是 CA chain 不對？SAN 不對？clock skew？trust store？ | §3 + §9 + Appendix B |
| K8s ServiceAccount token 被打包進 image | 為什麼這是漏洞？怎麼用 projected token 修？ | §5 |
| GitHub Actions secret 外洩 | 為什麼 OIDC federation 比 long-lived AWS key 安全？ | §5 + §9.H |
| 客戶問 GDPR / ISO27001 | 「我們的資料是怎麼加密的？key 誰持有？rotation 政策？」 | §13 |
| FinOps 報表暴漲 | KMS request 計費為什麼會 spike？怎麼快取 data key？ | §11 |
| Image 來源不明 | 怎麼證明這個 image 是我們 CI 產出的？SLSA level 是多少？ | §6 |
| **私鑰外洩** | 24 小時 playbook：detect→contain→rotate→post-mortem | §9.B / §9.E |
| **KMS CMK 誤刪** | 7-30 天 grace period 內救回 / 影響盤點 | §9.C |
| **Audit 怎麼證明 log 沒被竄改** | Append-only + Merkle 化的 verifiable log | §12 |

每一題背後都不是「裝個工具就好」，而是「先理解原理，再做工程決策，並備好失敗 playbook」。

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

> 想看每塊積木「為什麼安全」「黑盒內部結構」→ 直接翻[理論篇](./cryptography-core-theory.md) §4-§12。
> 這節只給工程師需要的「決策面向」。

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

# Part II — 場景手冊

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

### 3.4 Cert Rotation Playbook（v2 新增）

**Cert rotation 不是「換一張」，是設計題**。production 真正會踩的坑：

#### 場景 A：單一 server cert（最簡單）

```text
T-30 天：監控告警「Cert 即將到期」
T-7 天：自動 renew（ACME / cert-manager）
T-3 天：deploy 新 cert → reload server（nginx -s reload / k8s ingress 自動）
T-1 天：仍未 renew 觸發 PagerDuty
```

**關鍵：** server 必須支援「graceful reload」而非「restart」（避免斷線）。

#### 場景 B：mTLS 雙邊（client + server）

雙邊同時換 cert 容易出事 — **必須先 rollout 雙重 trust**：

```text
Phase 1：server 仍持舊 cert，但 trust store 加入「新 client CA」（同時信新舊）
Phase 2：client 換新 cert + 新 priv key（仍能被 server 接受）
Phase 3：server 換新 cert + trust store 移除舊 CA
Phase 4：所有舊 cert 撤銷
```

每個 phase 之間留「驗證期」（24 小時 - 7 天視 SLO）。
**反 pattern：** 同一個 deployment window 雙邊一起換 → 任一邊 deploy 慢就整個 mTLS 失敗。

#### 場景 C：service mesh mTLS

Istio / Linkerd / Cilium 自動 rotate workload cert（預設 24 小時）。
你要關心的：
- root / intermediate CA 的 rotation（每 5-10 年）
- mesh control plane cert 的 rotation
- 跨 cluster federation 時 trust bundle 同步

#### 場景 D：root CA rotation（最痛）

Root cert 過期是「整片 internet 級災難」。歷史案例：
- 2020 年 AddTrust External CA Root 過期 → Roku、Stripe 部分服務掛
- 2021 年 Let's Encrypt 切換 root → 舊 Android 裝置（< 7.1.1）斷線

**內部 PKI 的 root rotation playbook：**
1. 新舊 root 並行至少 1 年
2. 所有 client trust store 同時信兩個 root
3. 新簽 leaf 用新 root
4. 觀察舊 root 流量 → 零後才停舊 root

### 3.5 mTLS — 雙向驗證

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
- service mesh 把這層自動化（SPIFFE / SPIRE 是這領域的標準身分，見 §5.6）

### 3.6 Let's Encrypt / ACME — 自動化憑證

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

### 3.7 OCSP / CRL / OCSP Stapling（v2 新增）

Cert 提前撤銷怎麼通知 client？三種機制：

| 機制 | 怎麼運作 | 問題 |
|---|---|---|
| **CRL（Certificate Revocation List）** | CA 公佈「已撤銷的 cert 列表」，client 下載比對 | 列表太大（幾 MB）、client 不愛拉 |
| **OCSP（Online Certificate Status Protocol）** | Client 問 CA「這張 cert 有效嗎？」 | Client → CA 直連 = 隱私洩漏 + 延遲 |
| **OCSP Stapling** | Server 主動拿 OCSP response「釘」在 TLS 握手裡 | 解掉隱私 + 延遲，**現代標配** |

**Must-Staple 擴展（RFC 7633）：** Cert 帶 must-staple flag → client 強制要求 stapling，沒有就拒絕。

**nginx OCSP Stapling 配置：**

```nginx
ssl_stapling on;
ssl_stapling_verify on;
ssl_trusted_certificate /etc/nginx/ssl/chain.pem;
resolver 1.1.1.1 8.8.8.8 valid=300s;
```

**現代趨勢：** Google、Apple 都在淡出 OCSP，轉用「short-lived cert」（90 天 → 7 天 → 24 小時）+ CT log 監控。Let's Encrypt 2024 公告 7 天 cert 路線圖。

### 3.8 SNI 與 ECH（v2 新增）

**SNI（Server Name Indication）：** TLS 握手時 client 告訴 server「我要連 api.example.com」，讓 server 在同 IP 上 host 多個 domain。

問題：**SNI 是明文的** → 中間人能看出你要連哪個 domain（即使無法解密內容）。

**ECH（Encrypted Client Hello, RFC 9460）：** 把整個 ClientHello（含 SNI）加密。
- 需要 CDN / server 端支援
- Cloudflare 2023 起預設啟用
- Chrome / Firefox 2024 預設啟用
- 對「躲過國家級網路檢查」有真實意義

### 3.9 TLS Termination — 在哪一層？

| 位置 | 適合場景 | 取捨 |
|---|---|---|
| CDN（Cloudflare、CloudFront） | 公開網站、全球分發 | 不用管 cert，但內部要再 TLS（end-to-end） |
| Load Balancer（ALB、NLB） | 多 service 共用 cert | cert 在 LB，後端 plaintext or 再加密 |
| Ingress Controller（nginx-ingress、Envoy） | K8s 場景 | 集中管理 cert，cert-manager 自動化 |
| Service Mesh sidecar（Istio、Linkerd） | mTLS east-west | 每 pod 各自 terminate，cert 自動 rotate |
| 應用伺服器自己（nginx、Caddy） | 單機、簡單服務 | 完全自主，但要自己管 cert |

**現代多數正確選擇：** CDN/LB terminate 外部 TLS → Service Mesh re-encrypt 內部 mTLS（zero-trust）。

### 3.10 Cipher Suite 真實配置（v2 新增）

**TLS 1.3 cipher suite 只剩 5 個**，配置幾乎沒爭議：

```text
TLS_AES_128_GCM_SHA256        # 必選
TLS_AES_256_GCM_SHA384        # 必選
TLS_CHACHA20_POLY1305_SHA256  # 行動裝置友善
TLS_AES_128_CCM_SHA256        # IoT
TLS_AES_128_CCM_8_SHA256      # IoT 受限環境
```

**TLS 1.2 仍要支援時，現代推薦清單（Mozilla intermediate）：**

```text
ECDHE-ECDSA-AES128-GCM-SHA256
ECDHE-RSA-AES128-GCM-SHA256
ECDHE-ECDSA-AES256-GCM-SHA384
ECDHE-RSA-AES256-GCM-SHA384
ECDHE-ECDSA-CHACHA20-POLY1305
ECDHE-RSA-CHACHA20-POLY1305
DHE-RSA-AES128-GCM-SHA256
DHE-RSA-AES256-GCM-SHA384
```

**nginx 配置範本：**

```nginx
ssl_protocols TLSv1.2 TLSv1.3;
ssl_prefer_server_ciphers off;
ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384';
ssl_session_timeout 1d;
ssl_session_cache shared:SSL:50m;
ssl_session_tickets off;
ssl_stapling on;
ssl_stapling_verify on;
add_header Strict-Transport-Security "max-age=63072000" always;
```

**用 [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/) 永遠是首選**（避免人為錯誤）。

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
| AWS Secrets Manager / SSM Parameter Store | 純 AWS 環境 | 整合最順，按次計費（見 §11） |

**面試經典題：「為什麼不直接把 .env 放 git？」**

答案要層次清楚：
1. 一旦進 git 歷史就拔不掉（rotation 才是補救）
2. 沒有 RBAC、沒有 audit log
3. fork / mirror / 備份會擴散
4. CI logs、container layer 容易帶出去
5. 正確做法是 secret 放管理系統，CI 透過短期 token 拉取

### 4.3 Secret Backend Decision Tree（v2 新增）

```text
你的環境是？
├── 純 AWS、單帳號 → AWS Secrets Manager（含 rotation Lambda）
├── 純 AWS、敏感度低、量大 → SSM Parameter Store SecureString（便宜 25×，見 §11）
├── 純 GCP → GCP Secret Manager
├── 純 Azure → Azure Key Vault
├── 多雲 / 自架 → HashiCorp Vault
├── GitOps + 純 K8s → Sealed Secrets（簡單）或 SOPS（更 flexible）
├── K8s + 任一 backend → External Secrets Operator（統一介面）
└── 高合規（金融、政府）→ Vault Enterprise + HSM / CloudHSM
```

### 4.4 KMS 與 Envelope Encryption — 雲端面試必考

**為什麼不直接用 KMS 加密大檔案？**
- KMS 有大小限制（AWS KMS 4 KB）
- KMS 每次 call 都計費（FinOps 上不可忽視，見 §11）
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

### 4.5 Key Lifecycle — 一張你必須背的表

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
- 怎麼知道誰還在用舊 key？（CloudTrail / audit log，見 §10）
- 自動化還是手動？

### 4.6 Secret Rotation 真實做法（v2 新增）

#### AWS Secrets Manager auto-rotation Lambda

```text
Secret 設定 RotationLambdaArn + RotationRules{AutomaticallyAfterDays: 30}

Lambda 跑四步：
  1. createSecret    → 產新 secret pending
  2. setSecret       → 在目標 service（如 RDS）設新 password
  3. testSecret      → 用新 password 連線測試
  4. finishSecret    → 把 pending 標為 current

失敗會 rollback 到舊版
```

AWS 提供標準 Lambda 模板（RDS / Aurora / DocumentDB / Redshift / 自訂）。

#### Database password rotation 的 grace period

**反 pattern：** rotate → DB 立刻只認新 password → app 仍持舊 password → 全掛。

**正確 pattern（雙重接受）：**

```text
T+0    DB 新增「user_v2」帳號，仍保留 user_v1
T+1h   Secret 切到 user_v2 → app 漸進連到新 user
T+24h  確認沒有 user_v1 連線後，刪除 user_v1
```

或用 **dynamic secrets（Vault 風）**：每次連線拿全新 short-lived 帳號，沒有 rotation 概念。

#### Cert / signing key rotation

- TLS server cert：見 §3.4 playbook
- Image signing key：Cosign keyless（每次都新 cert）天然解掉這問題
- JWT signing key：JWKS 用 `kid` 區分新舊，client 自動拉新 key

### 4.7 Vault 災難復原與 Shamir 設計（v2 新增）

> 對應理論篇 §19 Threshold Cryptography。

Vault 啟動時 **「sealed」狀態** — master key 已加密，需要 unseal。
預設用 **Shamir Secret Sharing (3-of-5)**：

```text
master key 被切成 5 個 share
任 3 個 share 可重組 master key 解封 Vault

vault operator init                     # 初始化，產 5 個 share
vault operator unseal <share-1>
vault operator unseal <share-2>
vault operator unseal <share-3>         # 第 3 個 share 後 unseal 完成
```

**Production 設計：**

| 角色 | 持有 share 數 |
|---|---|
| Security Lead | 1 |
| Platform Lead | 1 |
| Infra Lead | 1 |
| 兩位 SRE on-call rotation | 各 1 |

**災難復原 playbook：**
- 2 人遺失 share → 仍可 unseal（4 → 3 仍夠）
- 3 人遺失 share → **永久無法 unseal**，必須從備份重建
- → 必須有 **encrypted backup** 與 **regular DR drill**

**進階：Auto-Unseal**
- 把 master key 用 cloud KMS 加密 → Vault 啟動時自動向 KMS 要解密
- 用 AWS KMS / GCP KMS / Azure Key Vault / HSM
- **但你仍要備份 KMS CMK** — 兩層套娃

#### Sealed Secrets 的災難（v2 新增）

Sealed Secrets controller 用 cluster 內的 private key 解密 SealedSecret。
**這把 private key 遺失 = 所有 SealedSecret 變垃圾**。

```bash
# 災難復原前必做：備份 controller key
kubectl get secret -n kube-system sealed-secrets-key -o yaml > sealed-secrets-key.yaml

# 把這個 secret 存到 HSM / 離線保險箱
```

每 30 天 controller 會 rotate 新 key（保留舊 key 解密）；不要把舊 key 從 controller 移除。

### 4.8 Multi-Region / Cross-Account KMS（v2 新增）

#### AWS Multi-Region Keys (MRK)

```text
us-east-1 KMS key  ←─ replica ─→  eu-west-1 KMS key
       └── 同 key ID 前綴 mrk-xxx，可互相 decrypt
```

**用途：** Active-Active multi-region 部署、災難復原、跨區資料庫複製。
**注意：** Replicate 只複製 key material，**KMS policy 各 region 獨立**。

#### Cross-Account KMS

讓 Account B 用 Account A 的 KMS key：

```json
{
  "Sid": "AllowCrossAccountUse",
  "Effect": "Allow",
  "Principal": {"AWS": "arn:aws:iam::ACCOUNT-B:role/some-role"},
  "Action": ["kms:Decrypt", "kms:GenerateDataKey"],
  "Resource": "*",
  "Condition": {
    "StringEquals": {"aws:SourceAccount": "ACCOUNT-B"}
  }
}
```

**反 pattern：** 開太寬讓整個 Account B 任何 role 都能解 → 應該限到具體 role ARN。

---

<a id="identity"></a>

## 5. Identity、JWT、OIDC、SPIFFE、簽章

身分驗證是 DevSecOps 的核心。這節把 JWT / OIDC / SAML / SPIFFE 從密碼學角度講清楚。

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

### 5.3 GitHub Actions → AWS OIDC 完整範例（v2 新增）

#### AWS IAM Trust Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {
      "Federated": "arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com"
    },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": {
        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
      },
      "StringLike": {
        "token.actions.githubusercontent.com:sub": "repo:myorg/myrepo:ref:refs/heads/main"
      }
    }
  }]
}
```

**關鍵 condition：**
- `aud` 必須限制 → 否則別人 repo 也能用
- `sub` 應該嚴限到 **repo + branch + workflow**

#### GitHub Actions Workflow

```yaml
permissions:
  id-token: write  # 必須！讓 Actions 能拿 OIDC token
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/github-actions
          aws-region: us-east-1
      # 之後 AWS CLI 自動用短期 token
```

### 5.4 JWKS Rotation in Production（v2 新增）

JWKS endpoint 範例：

```json
{
  "keys": [
    {
      "kid": "key-2026-05",
      "kty": "RSA",
      "alg": "RS256",
      "use": "sig",
      "n": "...",
      "e": "AQAB"
    },
    {
      "kid": "key-2026-02",
      "kty": "RSA",
      "alg": "RS256",
      "use": "sig",
      "n": "...",
      "e": "AQAB"
    }
  ]
}
```

**Rotation pattern：**

```text
T-7 天：產新 key，加進 JWKS（但仍簽舊 token）
T+0    切簽章 → 新 token 用新 kid
T+7 天：所有 token 都 expired → 從 JWKS 移除舊 key
```

**Client 端必須：**
- 用 `kid` 找對 key（不要 hardcode）
- 快取 JWKS 但有 TTL（5-15 分鐘）
- key 找不到時 refetch JWKS（不是直接拒絕）

### 5.5 PKCE — Public Client 必修（v2 新增）

OAuth 2.0 的 authorization code flow 設計給「有 secret 的 server」用。
mobile app、SPA 沒辦法存 client secret → 容易被攔截 code 換 token。

**PKCE (Proof Key for Code Exchange, RFC 7636)：**

```text
1. Client 產 code_verifier (random)
2. Client 算 code_challenge = SHA256(code_verifier)
3. 發 auth request 帶 code_challenge
4. IdP 回 code
5. Client 換 token 時帶 code_verifier
6. IdP 驗 SHA256(code_verifier) == 之前的 code_challenge
```

**OAuth 2.1 把 PKCE 列為強制**（不再是 optional）。

### 5.6 SPIFFE / SPIRE — Service Identity 標準（v2 新增）

**問題：** Microservice 互相驗身分用什麼？JWT 太大、mTLS cert 怎麼發？
**SPIFFE (Secure Production Identity Framework For Everyone)：** 給 service 的「身分標準」。

#### SPIFFE ID

```text
spiffe://example.org/ns/production/sa/payment-service
spiffe://example.org/ns/production/sa/order-service
```

像 URI 的 service identity，跨 K8s / VM / serverless。

#### SVID (SPIFFE Verifiable Identity Document)

兩種形式：
- **X.509-SVID**：X.509 cert，SAN 帶 SPIFFE ID → 直接做 mTLS
- **JWT-SVID**：JWT，sub claim 帶 SPIFFE ID → 給 HTTP API 用

#### SPIRE — SPIFFE 的實作

```text
SPIRE Server
  └── 信任 root（CA）
  └── 註冊 entry: "spiffe://example.org/ns/prod/sa/payment" → 對應到 "node X 上的 pod label app=payment"

SPIRE Agent（每 node 一個）
  └── 證明 node 身分（attestation）
  └── 把 SVID 發給 workload

Workload
  └── 透過 Workload API socket 拿 SVID
  └── 用 SVID 做 mTLS 連別的 service
```

**真實場景：** Istio、Linkerd、Cilium 內部用 SPIFFE 概念（但封裝起來不暴露給 user）。
**Greenfield 場景：** 直接跑 SPIRE + Envoy → 自製 zero-trust 平台。

### 5.7 DPoP — 比 Bearer Token 安全（v2 新增）

**問題：** OAuth bearer token 被偷 → 攻擊者直接用。沒有「token 屬於誰」的綁定。

**DPoP (Demonstrating Proof of Possession, RFC 9449)：**

```text
1. Client 產 ephemeral key pair
2. 拿 access token 時把 public key 綁進 token（cnf claim）
3. 每次 API call 帶 DPoP header = JWT(method, URL, timestamp) 用 priv key 簽
4. Server 驗 DPoP signature + 比對 token 裡的 public key
```

→ **token 被偷沒用，沒 priv key 偽造不出 DPoP header**。

**現代趨勢：** Apple、Google 已在某些 API 採用；OAuth 2.1 把 DPoP 列為推薦。

### 5.8 SAML — 為什麼還沒死

SAML 用 XML 簽章（XML-DSig），密碼學上比 JWT 古老但仍主流：

- 企業 SSO（Okta、ADFS、Azure AD）依然 SAML 為主
- AWS IAM Identity Center 同時支援 SAML 與 OIDC
- XML 簽章有歷史悠久的 XML signature wrapping 漏洞，library 設定很重要

對你而言：知道兩個共存即可，新東西優先用 OIDC + JWT。

### 5.9 SSH key — 你每天在用的非對稱密碼學

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

## 6. Supply Chain Security：image signing、SBOM、Sigstore、SLSA、VEX

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

> Rekor 的密碼學內部結構（Merkle tree / STH / inclusion proof）見[理論篇 §18](./cryptography-core-theory.md#ads)。

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

### 6.4 SLSA — 供應鏈成熟度框架完整版（v2 擴充）

SLSA（Supply-chain Levels for Software Artifacts）。

| Level | 具體要求 |
|---|---|
| **L1** | Build 有 documented process<br>產 provenance（人類可讀即可）<br>**做完 = 比沒做強** |
| **L2** | Build 在 hosted service（GitHub Actions / GitLab CI）<br>provenance 由該 service 簽章<br>provenance 包含 source revision、build config<br>**入門合理目標** |
| **L3** | Source / build 隔離（不同 trust boundary）<br>無人能 inject runtime（hermetic build）<br>provenance 由「隔離的 signer」簽（不是 build runner 自己）<br>**真實企業目標** |
| **L4** | 兩人 code review<br>完全 hermetic + reproducible build<br>**Google internal 等級** |

**對你 portfolio 的合理目標：L2，能宣稱 L3 加分**。

**SLSA L2 落地步驟：**
1. 用 GitHub Actions 跑 build（hosted CI ✓）
2. 用 `slsa-github-generator` action 自動產 provenance
3. provenance 由 GitHub OIDC 簽章（不是 build runner 自己手動）
4. provenance 上傳到 GHCR 與 Rekor

### 6.5 in-toto — Attestation 的標準（v2 新增）

**in-toto** 是 attestation 的「標準格式」。Cosign attestation 內部就是 in-toto。

```json
{
  "_type": "https://in-toto.io/Statement/v1",
  "subject": [{
    "name": "ghcr.io/me/myapp",
    "digest": {"sha256": "abc123..."}
  }],
  "predicateType": "https://slsa.dev/provenance/v1",
  "predicate": {
    "buildDefinition": {
      "buildType": "https://github.com/actions/runner",
      "externalParameters": {
        "workflow": {
          "ref": "refs/heads/main",
          "repository": "https://github.com/me/myapp"
        }
      }
    },
    "runDetails": {
      "builder": {"id": "https://github.com/actions/runner"},
      "metadata": {"invocationId": "..."}
    }
  }
}
```

**Predicate Type** 是擴展點：
- `https://slsa.dev/provenance/v1` — SLSA provenance
- `https://spdx.dev/Document` — SBOM
- `https://in-toto.io/attestation/vuln/v0.1` — vulnerability scan result
- `https://in-toto.io/attestation/test-result/v0.1` — test 結果

→ 任何「關於這個 artifact 的可驗證聲明」都用 in-toto attestation 包裝。

### 6.6 VEX — 「我們有但不受影響」的密碼學承諾（v2 新增）

**問題場景：** Log4Shell 出來，掃描器報你的 image「有 log4j 2.14.0 漏洞」。
但你**檢查過了**，你的程式碼沒走到漏洞 code path（例如沒用 lookup feature）。
怎麼向別人證明這件事？

**VEX (Vulnerability Exploitability eXchange)：** 結構化聲明 + 簽章。

```json
{
  "@context": "https://openvex.dev/ns/v0.2.0",
  "@id": "https://example.com/vex/CVE-2021-44228",
  "author": "security@example.com",
  "timestamp": "2026-05-15T00:00:00Z",
  "statements": [{
    "vulnerability": {"name": "CVE-2021-44228"},
    "products": [{"@id": "pkg:oci/myapp@sha256:abc"}],
    "status": "not_affected",
    "justification": "vulnerable_code_not_in_execute_path",
    "impact_statement": "log4j is bundled but JNDI lookup is disabled via system property"
  }]
}
```

**Status 五種：** `not_affected` / `affected` / `fixed` / `under_investigation`。

VEX 配合 Cosign attestation 簽章 → 不可偽造的「我們已 triage 過」聲明 → 客戶 / auditor 可信。

### 6.7 GUAC — 把 SBOM 變 Graph（v2 新增）

**問題：** 一個 image 的 SBOM 有 500 個套件，全公司 1000 個 image 怎麼查「哪些用到 X 套件」？

**GUAC (Graph for Understanding Artifact Composition)** 把所有 SBOM / VEX / attestation 灌進圖資料庫：

```text
GUAC 能回答：
  - 哪些 image 含 log4j？
  - 我們用到哪個版本？分布如何？
  - 哪些 image 用了未經 review 的 maintainer 上傳的版本？
  - 修這個漏洞影響哪些 deployment？
```

底層用 Trillian + Neo4j / DGraph。**這是 Log4Shell 後的「supply chain BI」工具**。

### 6.8 Policy Gate — Kyverno / OPA Gatekeeper

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

### 6.9 Vulnerability Triage Workflow（v2 新增）

CVE 發布後 24 小時你做什麼：

```text
T+0：CVE 發布
  └── 自動：Trivy / Grype 跑全公司 image 掃描
  └── 自動：GUAC 查「哪些 deployment 受影響」
  └── 通知：Slack #security-alerts

T+1h：嚴重度評估
  └── CVSS score + EPSS（exploit prediction）+ KEV catalog（已知被利用？）
  └── 你的「實際暴露」：internet-facing? 認證後? 內網?
  └── 決定：P0 (24h) / P1 (7d) / P2 (30d) / P3 (next quarter)

T+2h：VEX 評估
  └── 看 code path，是否真的受影響？
  └── 若 "not_affected" → 寫 VEX 簽章 → 結案
  └── 若 "affected" → 進入修補流程

T+24h（P0）：
  └── 修補 image / 重新 build / Cosign 簽
  └── 漸進 rollout（canary → 10% → 100%）
  └── 更新 VEX (status: fixed)
  └── Post-mortem：哪裡可以更早 detect？

工具鏈：
  - 掃描：Trivy / Grype / Snyk
  - 排序：EPSS、CISA KEV
  - 追蹤：Jira / GitHub Security Advisories
  - VEX：Cosign attestation
```

---

<a id="cloud-k8s-map"></a>

# Part III — Cloud / K8s 對照

## 7. Cloud / Kubernetes 對應地圖（AWS / GCP / Azure）

把上面所有概念對應到三大雲 + K8s，**這張表是面試前的速查**。

### 7.1 AWS

| 概念 | AWS 服務 | 你要記住的事 |
|---|---|---|
| 公網 TLS 憑證 | ACM | 託管、自動 renew、**不能 export priv key**，只能配 ELB / CloudFront / API Gateway |
| 私有 PKI | ACM Private CA | 內網 mTLS 用、按 CA + 簽張數計費 |
| 對稱 key 管理 | KMS（symmetric CMK） | envelope encryption 的中心，按 request 計費（見 §11） |
| 非對稱 key | KMS asymmetric CMK | 簽 / 驗、加密 / 解密；不能拿來搭 TLS |
| Secrets | Secrets Manager / SSM Parameter Store | SM 有 rotation，SSM 便宜但 rotation 要自己做 |
| 短期憑證 | STS、IAM role、AssumeRole | 短期 token 是雲端身分的主軸 |
| OIDC federation | IAM Identity Provider | GitHub Actions / EKS IRSA 都靠它 |
| 加密磁碟 / S3 | EBS encryption / S3 SSE-KMS、SSE-S3、SSE-C | 預設 KMS envelope；SSE-C 要自己管 key |
| CloudHSM | 硬體 HSM | 法規場景（FIPS 140-2 L3）、自己持 key |
| Audit | CloudTrail（KMS / Secrets Manager 都會記） | 加密事件可追溯 |
| 多區複製 key | KMS MRK | Active-Active multi-region |

### 7.2 GCP（v2 新增）

| 概念 | GCP 服務 | 對照 AWS |
|---|---|---|
| 公網 TLS 憑證 | Google-managed SSL certs | ≈ ACM |
| 私有 PKI | CA Service | ≈ ACM Private CA |
| 對稱 key 管理 | Cloud KMS | ≈ AWS KMS |
| 非對稱 key | Cloud KMS asymmetric | ≈ AWS KMS asymmetric |
| Secrets | Secret Manager | ≈ AWS Secrets Manager（但無原生 rotation Lambda） |
| 短期憑證 | Service Account + Workload Identity Federation | ≈ STS + IAM OIDC |
| OIDC federation | Workload Identity Pools | ≈ IAM Identity Provider |
| 加密磁碟 / Storage | CMEK (Customer-Managed Encryption Key) / CSEK (Customer-Supplied) | ≈ SSE-KMS / SSE-C |
| HSM | Cloud HSM（KMS 的 HSM-backed tier） | ≈ CloudHSM 但更整合 |
| Audit | Cloud Audit Logs | ≈ CloudTrail |
| 多區 | Multi-region keys | ≈ MRK |

**GKE 特有：** Workload Identity 讓 K8s ServiceAccount 直接映射 GCP Service Account（無需 secret 中介）。

### 7.3 Azure（v2 新增）

| 概念 | Azure 服務 | 對照 AWS |
|---|---|---|
| 公網 TLS 憑證 | App Service Managed Cert / Key Vault Cert | ≈ ACM |
| 私有 PKI | Key Vault Cert + Private CA | ≈ ACM Private CA |
| 對稱 / 非對稱 key + Secrets | **Azure Key Vault**（一站式） | ≈ KMS + Secrets Manager 合一 |
| 短期憑證 | Managed Identity（System / User-assigned） | ≈ IAM role |
| OIDC federation | Workload Identity Federation | ≈ IAM Identity Provider |
| 加密磁碟 / Storage | Storage Service Encryption（SSE） + Customer-Managed Key | ≈ SSE-KMS |
| HSM | Managed HSM | ≈ CloudHSM |
| Audit | Azure Monitor + Activity Log | ≈ CloudTrail |
| 多區 | Multi-region Key Vault (with replication) | ≈ MRK |

**AKS 特有：** Pod-managed Identity / Workload Identity，類似 IRSA。

### 7.4 Kubernetes（雲中立）

| 概念 | K8s 元件 / 工具 | 你要記住的事 |
|---|---|---|
| API server ↔ kubelet | 內建 TLS / mTLS | kubeconfig 裡的 cert 過期是常見災難 |
| Pod ↔ Pod TLS | Service mesh（Istio / Linkerd） | mTLS by default、SPIFFE ID 為身分 |
| 公網 / 內網 TLS | Ingress + cert-manager | 自動簽 cert（Let's Encrypt or Private CA） |
| Secret encryption-at-rest | etcd encryption provider | 沒設定的話 etcd 是 base64 |
| Secret 來源 | External Secrets Operator | 把 Vault / AWS SM / GCP SM / Azure KV 變成 K8s Secret |
| GitOps secret | Sealed Secrets / SOPS | secret 上 git 才安全的兩條路 |
| ServiceAccount token | projected token（OIDC） | 短期、bound to pod、可給 AWS IRSA / GCP WI / Azure WI / Vault |
| Image signing | Cosign + Kyverno policy | admission 層擋未簽 image |
| Pod 限制 | Pod Security Admission | privileged / runAsRoot 限制 |
| Audit | API server audit log | 誰 get 了哪個 secret |

### 7.5 Terraform / IaC

| 場景 | 做法 |
|---|---|
| State file 加密 | S3 backend + SSE-KMS + versioning + DynamoDB lock（AWS）<br>GCS + Cloud KMS + state locking（GCP）<br>Azure Blob + RBAC + soft delete（Azure） |
| 不把 secret 寫進 `.tf` | 用 `data.aws_secretsmanager_secret_version`、TF_VAR_、SOPS |
| Provider 認證 | OIDC（GitHub Actions assume role），不要 long-lived AK |
| Module 完整性 | 用 registry 或 git tag + checksum 驗證 |
| Drift detection | 加密狀態下 plan 出現差異要警覺 |

### 7.6 Linux Host（你的 RHEL 主場）

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

### 8.4 Cipher 配置反 pattern（v2 新增）

**真實 PR review 會看到的錯誤：**

**反 pattern 1：nginx 用 `HIGH` 預設**

```nginx
# ❌ 太籠統，可能包含 weak cipher
ssl_ciphers HIGH:!aNULL:!MD5;

# ✅ 用 Mozilla intermediate 字串明確列出
ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:...';
```

**反 pattern 2：K8s ingress annotation 沒關 TLS 1.0**

```yaml
# ❌
nginx.ingress.kubernetes.io/ssl-protocols: "TLSv1 TLSv1.1 TLSv1.2 TLSv1.3"

# ✅
nginx.ingress.kubernetes.io/ssl-protocols: "TLSv1.2 TLSv1.3"
```

**反 pattern 3：Go 啟用 InsecureSkipVerify**

```go
// ❌
client := &http.Client{
    Transport: &http.Transport{
        TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
    },
}

// ✅ 真的有 private CA 就加入 trust pool
caCert, _ := os.ReadFile("private-ca.pem")
pool := x509.NewCertPool()
pool.AppendCertsFromPEM(caCert)
client := &http.Client{
    Transport: &http.Transport{
        TLSClientConfig: &tls.Config{RootCAs: pool},
    },
}
```

**反 pattern 4：Java 預設 keystore 用 SHA-1 / JKS**

```bash
# ❌ JKS 老格式
keytool -genkey -keystore old.jks -storetype JKS

# ✅ PKCS12 + 強 hash
keytool -genkey -keystore new.p12 -storetype PKCS12 \
        -keyalg RSA -keysize 4096 -sigalg SHA256withRSA
```

**反 pattern 5：Python requests 不驗 cert**

```python
# ❌
requests.get("https://...", verify=False)

# ✅
requests.get("https://...", verify="/path/to/ca-bundle.pem")
```

---

<a id="ir-playbook"></a>

# Part IV — SRE 主軸三大新章

## 9. Cryptographic Incident Response Playbook

> 對應 NIST SP 800-61 IR 四階段：**Detect → Contain → Eradicate → Recover → Lessons Learned**。
> 這章是面試 SRE / on-call 最容易考的「24 小時 playbook」。

### 9.A Scenario A：Cert 即將到期 / 已過期

#### Detect

```text
✓ Prometheus / Datadog 告警：「cert expires in 30 / 7 / 1 day」
✓ 用戶 504 / 502 報修
✓ Status page automation 偵測到 SSL handshake 失敗
```

#### Contain（已過期，分鐘級）

```bash
# 1. 確認真的過期了
openssl s_client -connect api.example.com:443 -servername api.example.com 2>&1 | grep -E 'Not After|verify'

# 2. 若有舊但仍有效的 cert backup → 立刻替換
kubectl -n prod create secret tls api-cert --cert=backup.crt --key=backup.key --dry-run -o yaml | kubectl apply -f -

# 3. 重啟 / reload service
kubectl -n prod rollout restart deployment/api
```

#### Eradicate（30 分鐘）

```bash
# 1. 強制 ACME renew（cert-manager）
kubectl -n prod delete certificaterequest --all
kubectl -n prod annotate certificate api-cert cert-manager.io/issue-temporary-certificate-

# 2. 監控 renew 過程
kubectl -n prod describe certificate api-cert

# 3. 驗證新 cert
openssl s_client -connect api.example.com:443 -servername api.example.com -showcerts
```

#### Recover（2 小時）

- 加 cert expiry monitor 確保不會再發生（見 §10.1）
- 把 cert renew 日期推早到 30 天（cert-manager 預設）
- 確認 CDN / LB cache 已更新

#### Lessons Learned

- 為什麼 alarm 沒提前響？
- 為什麼 auto-renew 沒運作？rate limit？DNS-01 challenge 失敗？
- 是否有「cert expiry SLO」？

### 9.B Scenario B：Private Key 外洩（GitHub push / laptop 遺失）

#### Detect

```text
✓ git-secrets / gitleaks 掃描 hit
✓ truffleHog 在 commit history 找到
✓ 用戶或工程師回報
✓ GitHub 主動掃描通知
```

#### Contain（10 分鐘）

```bash
# 1. 立刻撤銷 key（不是先 rotate 再撤）
# - SSH key: 從 authorized_keys 移除
# - TLS cert: 用 CA 撤銷（OCSP）
# - JWT signing key: 從 JWKS 移除
# - AWS access key: aws iam delete-access-key
# - SaaS API token: 在該 SaaS console 撤銷

# 2. 確認沒人正在用該 key
# 看 access log / audit log 找最後使用時間
```

#### Eradicate（1 小時）

```bash
# 1. 換新 key
ssh-keygen -t ed25519 -f new_key
# 或 cert-manager rotate, 或 KMS rotate, 等等

# 2. 推到所有 consumer
ansible-playbook deploy-new-key.yaml

# 3. 若 key 已進 git history → BFG / git-filter-repo 清除
git filter-repo --invert-paths --path leaked-key.pem
git push --force --all

# 4. 通知所有 fork 也要清除（git filter-repo 不會自動同步 fork）
```

#### Recover（24 小時）

- 把 leak 時間到 detect 時間之間的所有「該 key 簽出的 / 加密的 / 認證的」事件 audit 一遍
- 評估是否有資料被解密 / 被偽造簽章 / 被誤用權限
- 若是 signing key → 重簽過去產出的 artifact，廢棄舊簽章

#### Lessons Learned

- pre-commit hook 為什麼沒擋？
- key 為什麼會出現在 repo？
- 是否有 secret scanning 在 CI？
- 是否該改用 short-lived（OIDC）取代 long-lived key？

### 9.C Scenario C：KMS CMK 被誤刪

#### Detect

```text
✓ CloudTrail 事件：ScheduleKeyDeletion
✓ 用戶報「資料解不開了」
✓ 應用 KMS API 開始 throwing AccessDeniedException
```

#### Contain（**爭取 grace period**）

```bash
# AWS KMS scheduled deletion 有 7-30 天 grace period
# 1. 立刻 cancel deletion
aws kms cancel-key-deletion --key-id <key-id>

# 2. 確認 key 狀態回到 Enabled
aws kms describe-key --key-id <key-id>
```

**如果已過 grace period，key 永久喪失** → 該 key 加密的所有資料**永遠解不開**。

#### Eradicate / Recover

- 若有 KMS replica key (MRK) → 用 replica 解（key material 一樣）
- 若有 cross-region backup（資料用不同 region key 重新加密過）→ 從 backup 恢復
- 否則：資料喪失，啟動 disaster recovery 從上游 source 重建

#### Lessons Learned

- 為什麼 root user 能 schedule deletion？應該有 SCP block
- 多 region key 是否啟用？
- backup 策略是否覆蓋 KMS key 喪失情境？

### 9.D Scenario D：Secret 確認外洩（DB password / API key in Secrets Manager）

類似 9.B 但範圍更小（不是 priv key，是 application secret）。

```text
Contain:
  - rotate secret（手動或 auto-rotation Lambda）
  - 確保 grace period（雙重接受，§4.6）

Eradicate:
  - 撤銷舊 secret（在 DB / SaaS 端）
  - 確認所有 consumer 拿到新 secret

Recover:
  - audit 該 secret 的所有 access log
  - 評估是否有非預期使用

Lessons:
  - secret 為什麼能被讀到？RBAC 太寬？
  - secret 為什麼進 git / log？
  - 是否該改用 short-lived dynamic secret？
```

### 9.E Scenario E：Signing Private Key 外洩

最嚴重情境之一。Cosign / GPG / Sigstore（私鑰）外洩 → 攻擊者可偽造「合法簽章」。

```text
Contain（小時級）:
  - 撤銷 signing cert（OCSP / Rekor 標記）
  - 在 admission policy 加 deny rule：拒絕該 cert 簽的所有 image
  - 推到所有 cluster

Eradicate（24 小時）:
  - 產新 signing key（或改 keyless，從此不再有長期 priv key）
  - 重簽所有 production image
  - 重新 deploy

Recover（7 天）:
  - audit 所有用該 key 簽過的 image
  - 確認沒有來路不明的簽章
  - 用 Rekor inclusion proof 證明哪些是真實簽章

Lessons:
  - 為什麼不用 keyless？
  - signing 環境是否與 dev / prod 隔離？
```

→ 這就是為什麼 **Cosign keyless** 是現代首選 — 沒有長期 priv key 可被偷。

### 9.F Scenario F：SSH Host Key Mismatch

```text
SSH client warning: "WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!"

可能原因：
  A. 真正 MITM 攻擊
  B. server 重建（rebuild），host key 重產
  C. AMI / image 沒持久化 host key

Triage:
  1. 看 console: 真的是同一台機器嗎？(uptime / instance ID)
  2. 用 AWS SSM Session Manager 進入（不靠 SSH）確認指紋
  3. 與 known_hosts backup 比對

Resolve（B / C 情境）：
  - 確認是合法 rebuild → 移除 known_hosts 舊 entry
  - 未來：用 SSH CA 簽 host cert，rebuild 後仍是同 cert（不需更新 known_hosts）

Resolve（A 情境）：
  - 立即斷網該機器
  - forensics
  - 隔離 + 重建
```

### 9.G Scenario G：TLS 降級警報觸發

```text
Detect:
  - WAF / IDS 警報「detected TLS 1.0 / weak cipher」
  - Mozilla Observatory / SSL Labs 評分降低
  - User 回報「我手機/老瀏覽器連不上」（反向）

Triage:
  - 是真的攻擊還是某 client 太舊？
  - 看 access log: 來自哪個 user agent / IP？
  - 比例多少？

Resolve:
  - 若是攻擊 → 把該 IP 加 blocklist，調查
  - 若是舊 client → 評估是否該繼續支援
    - 公司內網工具：升級 client
    - 公開 API：可能要做兼容期 + EOL 公告
```

### 9.H Scenario H：AWS Access Key 在公開 Repo 被掃到

AWS 自己有自動掃描 GitHub，會發 email + 自動 quarantine。

```text
T+0 mins：AWS 偵測到 key 在 GitHub
T+5 mins：AWS attach quarantine policy（你的 key 變只能 list 自己）
T+5 mins：AWS 發信給 root + IAM user owner
T+5 mins：Bot 開始掃 git history 找這把 key

你的 24 小時 playbook：
T+10 mins:
  - 確認 quarantine 已生效
  - delete access key: aws iam delete-access-key --access-key-id AKIA...
  - 看 CloudTrail：key 被誰用過？用做什麼？

T+1h:
  - 評估損失：被建什麼 resource? 被存什麼資料?
  - 若有 EC2 / RDS 被建 → 是 crypto miner，立刻 terminate
  - billing alert 是否觸發？

T+24h:
  - 確認 git history 清除
  - 全 org 跑 git-secrets / trufflehog 掃描
  - 教育：用 OIDC（§5.3）取代 long-lived key
  - 啟用 GuardDuty「AccessKey discovered in public repo」detector

Post-mortem:
  - 為什麼 pre-commit hook 沒擋？
  - 為什麼 long-lived key 還存在？
  - SCP / IAM 是否該禁用 access key 建立？
```

### 9.X 通用 IR 原則

| 階段 | 通用原則 |
|---|---|
| **Detect** | 越早越好；monitoring 是錢但比 incident 便宜（見 §10） |
| **Contain** | 寧可過度（service degrade）也不要 propagate；priv key 永遠先撤再 rotate |
| **Eradicate** | 不只是換新 key — 要把「中毒範圍」清乾淨 |
| **Recover** | Grace period + canary，不要一次全切 |
| **Lessons Learned** | Blameless post-mortem；補 detection 比追責任更重要 |

---

<a id="observability"></a>

## 10. Cryptographic Observability

**SRE 主軸是「能監控、能告警、能 debug」。** 密碼學監控不該是事後諸葛。

### 10.1 Cert Expiry Monitoring

#### Prometheus blackbox_exporter

```yaml
# blackbox.yml
modules:
  http_2xx_tls:
    prober: http
    timeout: 10s
    http:
      tls_config:
        insecure_skip_verify: false

# Prometheus scrape config
- job_name: 'tls_probe'
  metrics_path: /probe
  params:
    module: [http_2xx_tls]
  static_configs:
    - targets:
      - https://api.example.com
      - https://web.example.com
  relabel_configs:
    - source_labels: [__address__]
      target_label: __param_target
    - source_labels: [__param_target]
      target_label: instance
    - target_label: __address__
      replacement: blackbox-exporter:9115
```

關鍵 metric：`probe_ssl_earliest_cert_expiry`

```promql
# Alert 30 天前
(probe_ssl_earliest_cert_expiry - time()) / 86400 < 30

# Alert 7 天前（more critical）
(probe_ssl_earliest_cert_expiry - time()) / 86400 < 7
```

#### cert-manager 內建 metrics

```promql
# 還剩多久過期
certmanager_certificate_expiration_timestamp_seconds

# Cert 是否就緒
certmanager_certificate_ready_status
```

#### 全公司 cert inventory

不能只監控你知道的 endpoint。**用 Certificate Transparency log 反查公司所有 domain 的 cert**：

```bash
# crt.sh API
curl 'https://crt.sh/?q=%25.example.com&output=json' | jq -r '.[].name_value' | sort -u
```

→ 對任何公司 domain 自動發現「有人簽過的 cert」，比對是否有未授權的（也是攻擊 detect）。

### 10.2 KMS API 使用異常偵測

```text
CloudTrail Event:
  - Decrypt 次數突增？(可能是攻擊者在 batch 解密外洩資料)
  - GenerateDataKey 從新地區？(可能 credential 被偷)
  - DeleteKey / DisableKey?(可能是內部威脅)
  - GrantToken 新增？(權限擴張)
```

CloudWatch Alarm 範例：

```yaml
KMSDecryptAnomaly:
  Type: AWS::CloudWatch::Anomaly Detector
  Properties:
    Metric:
      MetricName: NumberOfDecryptRequests
      Namespace: AWS/KMS
      Dimensions:
        - Name: KeyId
          Value: <key-id>
    Stat: Sum
```

→ 自動學 baseline，偏離兩個標準差就告警。

### 10.3 TLS Handshake Failure Rate

#### Envoy / Istio

```promql
# 失敗率
rate(envoy_listener_ssl_fail{}[5m]) / rate(envoy_listener_ssl_handshake{}[5m])

# 拆解原因
sum by (failure_reason) (rate(envoy_listener_ssl_fail[5m]))
```

常見 failure reason：
- `BAD_CERT_HASH_VALUE`：cert chain 問題
- `CIPHER_NEGOTIATION_FAILED`：cipher 不相容
- `HOSTNAME_VERIFICATION_FAILED`：SAN 不對

#### nginx

```nginx
log_format ssl '$remote_addr $ssl_protocol $ssl_cipher $ssl_session_reused';
access_log /var/log/nginx/ssl.log ssl;
```

然後用 promtail / fluent-bit 解析成 metric。

### 10.4 JWT Validation Failure

```promql
# JWT 驗證失敗率（應用層自己 expose）
rate(jwt_validation_failures_total{reason="expired"}[5m])
rate(jwt_validation_failures_total{reason="invalid_signature"}[5m])
rate(jwt_validation_failures_total{reason="invalid_audience"}[5m])
```

**Invalid signature 突增 → 可能是 JWKS rotation 未同步**（見 §5.4）。
**Expired 突增 → 可能 client clock skew、token TTL 太短**。

### 10.5 HSM / KMS 連線健康

```text
✓ HSM cluster member 數量
✓ HSM cluster latency p99
✓ KMS API throttle rate（被 AWS rate limit 了？）
✓ KMS API error rate
```

Datadog / CloudWatch 都有現成 dashboard。

### 10.6 Secret Access Audit

#### Vault audit device

```bash
vault audit enable file file_path=/var/log/vault_audit.log
```

每次 read / write secret 都會 log。送到 ELK / Splunk 做 SIEM：

```text
SIEM rules:
  - Single user reads > 50 secrets in 1 min → alert（可能是 credential 被盗）
  - Off-hours secret read → alert（誰 3am 在動 prod secret？）
  - Failed secret read > 10 in 5 min → alert（暴力嘗試？）
```

#### AWS Secrets Manager CloudTrail

```bash
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=EventName,AttributeValue=GetSecretValue \
  --start-time $(date -d '24 hours ago' -Iseconds)
```

### 10.7 Sigstore Rekor 監控

如果用 Cosign 簽 image，**監控 Rekor 出現未授權簽章**：

```text
✓ 訂閱 Rekor 全量 STH（Signed Tree Head）
✓ 對「subject = *@yourcompany.com」的新 entry 自動檢查
✓ 是否來自合法 CI workflow？
```

→ 攻擊者偷簽 image 也會留在 Rekor，monitor 就能 detect。

### 10.8 推薦 Dashboard 結構

對你 portfolio 的 Grafana dashboard，建議分四個 row：

```text
Row 1: TLS / Cert Health
  - All certs by days_to_expiry (color: red < 7d, yellow < 30d, green)
  - TLS handshake success rate per service
  - Top 10 ciphers in use（看有沒有 legacy）

Row 2: Secrets / KMS
  - KMS Decrypt rate (with anomaly band)
  - Secrets Manager GetSecretValue per role
  - Vault audit log error rate

Row 3: Identity / JWT
  - JWT validation failures by reason
  - OIDC token issuance per IdP
  - Active sessions per user

Row 4: Supply Chain
  - Unsigned images deployed (should be 0)
  - SBOM scan results: CVE exposure
  - Rekor unauthorized entries
```

→ 這就是「Cryptographic Observability Dashboard」，可以直接寫進履歷。

---

<a id="finops"></a>

## 11. Cryptographic FinOps

**對應 CLAUDE.md 你的職涯主軸「FinOps capability」**。加密成本在大規模部署不可忽視。

### 11.1 AWS KMS Pricing 拆解

```text
Customer-Managed CMK:    $1/月/key
API Request (encrypt/decrypt/GenerateDataKey):
  - $0.03 per 10,000 requests（標準）
  - $0.10 per 10,000 requests（symmetric outside region）

Asymmetric CMK API:      $0.15 per 10,000 requests（更貴）

CloudHSM:                ~$1.45/小時 × cluster size（最少 2 個 HSM 高可用）
                       = ~$2,100/月 起跳

External Key Store (XKS): $0.03 per request + 自己付外部 HSM
```

### 11.2 為什麼 Envelope Encryption 省錢

**反 pattern：** 1 萬個檔案各自呼 KMS encrypt
```text
10,000 requests × $0.03 / 10,000 = $0.03（單次）
但每月跑 100 次 → $3/月，且高延遲
```

**Envelope pattern：** 一個 DEK 加密 1 萬檔案，DEK 用 KMS 加密一次
```text
1 request × $0.03 / 10,000 = $0.000003（單次）
省 10,000×
```

**DEK 快取：**

```text
Application:
  Cache: DEK + remaining_uses + expiry
  
  encrypt(data):
    if cache.valid():
      use cached DEK
    else:
      DEK, encrypted_DEK = kms.GenerateDataKey()
      cache.set(DEK, max_uses=100, ttl=300s)
    
    return AES-GCM(data, DEK), encrypted_DEK
```

→ 在合理 max_uses（如 100）下省 ~99% KMS call。
→ AWS Encryption SDK / Tink 都有內建 cache 機制。

### 11.3 CloudHSM vs KMS — 何時 tipping point

```text
KMS：$1/key/月 + $0.03/10K request
HSM：$2,100/月 起，無限請求

Tipping point:
  $2,100 / $0.03 × 10,000 = 7 億 requests/月
  ÷ 30 天 = 2,300 萬/天
  ÷ 86,400 秒 = 270 request/sec

→ 持續 > 270 req/sec 才考慮 HSM
```

**真實考量除了成本：**
- 法規（FIPS 140-2 L3）只能用 HSM
- 自己持 key（KMS 是 AWS 持 key material，HSM 是你持）
- HSM 有 dedicated tenancy → 安全等級高

### 11.4 Secrets Manager vs SSM Parameter Store

```text
Secrets Manager:
  - $0.40/secret/月
  - $0.05 per 10,000 API call
  - 含 rotation Lambda（自動化）

SSM Parameter Store SecureString:
  - Standard tier: 免費（限 4KB, 10K params）
  - Advanced tier: $0.05/parameter/月 + $0.05 per 10,000 API call
  - 沒有原生 rotation（要自己寫）

10,000 secrets：
  - SM: $4,000/月
  - SSM Advanced: $500/月
  - SSM Standard（限免費 quota）: $0/月
```

**決策原則：**
- 需要自動 rotation → SM
- 大量配置但敏感度低 → SSM SecureString
- 跨 region replication 內建 → SM

### 11.5 S3 加密成本對比

100 TB S3 / 一年：

| 加密方式 | 成本面 |
|---|---|
| **SSE-S3**（AES-256, AWS-managed key） | 無額外加密成本，只付 storage |
| **SSE-KMS**（CMK） | 每次 PUT/GET 都呼叫 KMS → 100M PUT × $0.03/10K = $300/月 KMS 費用 |
| **SSE-KMS + Bucket Key**（envelope at bucket level） | KMS call 減 99% → ~$3/月 |
| **SSE-C**（client-supplied key） | 無 KMS 費，但你自己管 key（風險） |

**Bucket Key（2020 年加的功能）必開**：把 SSE-KMS 成本降到接近 SSE-S3。

### 11.6 TLS Termination CPU 成本

```text
nginx 跑 TLS termination：
  - RSA-2048 handshake: ~1500 ops/sec/core
  - ECDSA P-256 handshake: ~5000 ops/sec/core（3× 快）
  - AES-NI 啟用後 bulk encrypt 幾乎 free

100K RPS TLS termination：
  - 用 RSA：需要 ~70 cores
  - 用 ECDSA：需要 ~20 cores
  → ECDSA 省 70% CPU 成本
```

→ 從 RSA cert 切到 ECDSA cert 是純 win（除非極舊 client 不支援）。

### 11.7 Cross-Region Key Replication 成本

```text
AWS KMS MRK:
  - Replica key 本身: $1/月（每 region）
  - Cross-region replicate event: 免費
  - API call: 各 region 各自計費

10 regions × $1 = $10/月 額外
```

成本不大，但 **跨 region request 不會被計費為「out-of-region」**（這是 MRK 的最大 FinOps 優勢）。

### 11.8 KMS Quota 與 Throttling

```text
AWS KMS 預設 quota：
  - Symmetric cryptographic ops: 5,500 req/sec
  - Decrypt: 1,200 req/sec
  - 可申請提高

Throttle 後果：
  - API 回 ThrottlingException
  - 應用層該 retry with exponential backoff
  - 真的 quota 不夠 → 開 case 提高，或檢視是否該用 envelope cache
```

### 11.9 FinOps Dashboard 建議

```text
Row 1: KMS 成本
  - KMS request 數 per service (top 10)
  - KMS cost per service / 月
  - Anomaly: 突然超過 baseline 兩倍

Row 2: Secret 管理成本
  - SM secrets 總數 vs SSM 總數
  - 哪些 secret 從未被讀（candidate for cleanup）

Row 3: TLS 成本
  - nginx CPU% for TLS handshake
  - Cert types: RSA vs ECDSA 分布
  - Potential savings if migrate all to ECDSA

Row 4: 加密相關 storage
  - S3 SSE-KMS 大小（with Bucket Key on?）
  - EBS encrypted 比例
  - Snapshot 加密狀態
```

### 11.10 FinOps 真實 Lab（portfolio 用）

**Lab：「為 Observable E-commerce Platform 做加密成本分析」**

```text
1. 列出所有用 KMS 的元件（EBS / RDS / S3 / Secrets / Logs）
2. 跑 cost explorer 拉一個月 KMS 費用 by service
3. 找出 top 3 cost driver
4. 提出 optimization plan：
   - 開 Bucket Key
   - 加 DEK cache
   - RSA → ECDSA cert migration
   - 整併重複 secret
5. 估算節省金額
6. 寫成 1-page proposal（如同對 CTO 報告）
```

→ 這個 Lab 直接證明你能講「Cloud Platform + FinOps + 加密成本」的故事。

---

<a id="verifiable-log"></a>

# Part V — 進階主題

## 12. Audit Log 與 Verifiable Log 設計

> 對應理論篇 §18 Authenticated Data Structures。
> 應用篇要回答：「我怎麼設計一個 audit log，讓 auditor 能驗證沒被竄改？」

### 12.1 普通 Audit Log 不夠

```text
傳統 audit log:
  - 寫入 file / DB / CloudWatch
  - 假設「沒人能改」

問題：
  - 有 root / DB admin 的人可以改
  - 法規（SOX、SOC 2、PCI）要 tamper-evident
  - 出事時你怎麼證明 log 沒被改？
```

### 12.2 三層 audit log 成熟度

| 等級 | 機制 | 防誰 |
|---|---|---|
| **L1 普通 log** | 寫檔案 / CloudWatch | 不防 |
| **L2 append-only** | S3 Object Lock / WORM storage | 防 admin 改 |
| **L3 hash chain** | 每條 log 帶前一條 hash → 改任一條就會被偵測 | 防 admin 改 + 證明連續性 |
| **L4 Merkle log** | 整批 log 進 Merkle tree，定期發 Signed Tree Head | 防一切（包含 log service 本身） |

### 12.3 Hash Chain — 簡單版

```python
entry_n = {
  "timestamp": "...",
  "event": "...",
  "user": "...",
  "prev_hash": SHA256(entry_{n-1} serialized),
  "self_hash": SHA256(this_entry without self_hash)
}
```

**驗證：** 從第一條開始重算每條 hash，看 prev_hash 是否符合。**改任何一條都會破壞 chain。**

**部署：** 把這條 chain 存 immutable storage（S3 Object Lock），無人能改。

### 12.4 Merkle Log — Trillian / Rekor 風格

對應理論篇 §18.2-18.4。

```text
1. 每條 log 變成 Merkle tree 的 leaf
2. 定期（如每秒）發 Signed Tree Head (STH):
   STH = sign({root_hash, tree_size, timestamp})
3. 公開 STH（HTTP endpoint、blockchain、或 mailing list）
4. 任何人可：
   - 拿 inclusion proof 驗某條 log 確實在 tree 裡（log_n hash）
   - 拿 consistency proof 驗新 STH 是舊 STH 的延續（log_n hash）
```

**自己跑 verifiable log：用 Google Trillian**

```text
Trillian 元件：
  - Trillian Log Server (核心 Merkle tree)
  - Trillian Log Signer (產 STH)
  - Personality（你寫的 API gateway，定義 leaf format）

部署：
  - PostgreSQL / MySQL / Spanner 當 backend storage
  - gRPC API 寫入 leaf
  - HTTP gateway 查 STH / proof
```

### 12.5 真實場景

| 場景 | 設計 |
|---|---|
| **Compliance audit log**（SOC 2 / PCI） | Hash chain 進 S3 Object Lock，每天 hash 提交到外部 timestamping service |
| **Production deploy audit** | 每次 deploy 寫 Trillian log，含 git SHA / image digest / approver |
| **Customer-visible audit log** | Merkle log + 客戶可拉 inclusion proof（透明度賣點） |
| **Image signing audit** | 直接用 Rekor（公開 instance 或自架） |
| **Database 改動審計** | DB trigger → 寫 hash chain log |

### 12.6 對 SRE / DevSecOps 的 Lab

**Lab：「在 Observable E-commerce 上加 verifiable deploy log」**

```text
1. 跑一個 Trillian instance（用 Helm chart）
2. 寫一個 GitHub Actions step：每次 deploy 完寫一條 leaf
   leaf = {
     "timestamp": "...",
     "git_sha": "...",
     "image_digest": "sha256:...",
     "approver": "github_username",
     "environment": "production"
   }
3. Dashboard：
   - 拉 STH，顯示 tree size + 最新 root
   - 給每次 deploy 一個 inclusion proof URL
4. 演習：嘗試竄改 → 用 consistency proof 偵測
```

→ 這就是「supply chain audit」portfolio 級別的展示。

### 12.7 為什麼這對你的職涯重要

- **合規類面試**（金融 / 醫療 / 政府）必問 audit log 設計
- **SRE platform** 要能證明 deploy 流程不可篡改
- **DevSecOps** 的 audit trail 直接接到這
- **接到[理論篇 §18](./cryptography-core-theory.md#ads)** Merkle tree 的工程落地

---

<a id="compliance"></a>

## 13. Compliance & Regulatory Mapping

> 求職關鍵字密度高的一章。面試金融 / 醫療 / 政府 / 上市公司必問。

### 13.1 FIPS 140-2 / 140-3

**FIPS 140-2 / 140-3** 是美國 NIST 對「加密模組」的安全標準。

| Level | 要求 | 例子 |
|---|---|---|
| L1 | 基本加密 + 文件 | 一般軟體 |
| L2 | role-based authentication + tamper evidence | 多數 HSM |
| L3 | strong identity + tamper resistance | AWS CloudHSM、YubiKey |
| L4 | 抗物理攻擊 + 環境保護 | 軍規 |

**對你的意義：**
- 政府 / 國防 / 金融上市公司常要求 **「使用 FIPS 140-2 L3 認證的加密」**
- AWS KMS 是 FIPS 140-2 L2（部分 L3）；CloudHSM 是 L3
- 用 P-256 / RSA / SHA-2 → 通過；用 X25519 / Ed25519 → **目前還沒 FIPS 認證**（2025 NIST 正在加入）

### 13.2 PCI DSS 4.0 加密要求

2024 年 4.0 生效，重點變化：

```text
✗ SHA-1 完全禁用（4.0 之前還允許過渡）
✗ TLS 1.0 / 1.1 完全禁用
✓ 強制 strong cryptography for cardholder data
✓ Encryption key management 必須包含：
  - Key generation
  - Key distribution
  - Key storage
  - Key rotation（≤ 1 年）
  - Key destruction
✓ Tokenization / FPE 取代明文 PAN（信用卡號）
✓ End-of-life cryptographic protocol 必須有 migration plan
```

**對 SRE 的對應：**
- TLS termination 設定強制 1.2+
- DB 內信用卡欄位用 FPE（FF1 / FF3）
- KMS rotation 啟用 365 天

### 13.3 GDPR Article 32 — 加密的法律要求

```text
"處理個資時應採取適當技術措施，**特別是加密**"
```

GDPR 沒指定具體算法，但實務 audit 看的：
- Encryption at rest（DB、S3、backup）
- Encryption in transit（TLS）
- Key management（誰持 key？rotation？）
- Pseudonymisation（tokenization）

**重要：** 加密做了不等於免責，但能大幅降低 breach 罰款（最高 4% global revenue）。

### 13.4 SOC 2 Type II — Crypto Controls

SOC 2 Trust Service Criteria 與密碼學相關：

| TSC | Control | 你怎麼證明 |
|---|---|---|
| **CC6.1** | Logical access controls | RBAC + MFA + audit log |
| **CC6.6** | Encryption of transmitted data | TLS 1.2+ 強制 + cert monitoring（§10.1） |
| **CC6.7** | Encryption of stored data | KMS / SSE 普及率 dashboard |
| **CC6.8** | Key management | Vault / KMS rotation policy + audit |
| **CC7.2** | Anomaly detection | KMS API monitoring（§10.2） |

**Auditor 會要：** screenshots / logs / runbooks 證明你**真的**有做、不是書面而已。

### 13.5 HIPAA Security Rule

醫療資料：

```text
§164.312(a)(2)(iv) — Encryption and Decryption (addressable)
§164.312(e)(2)(ii) — Encryption (in transit) (addressable)
```

「Addressable」≠ 「optional」 — 你要嘛做，要嘛文件記錄「為什麼不做且用什麼替代」。
實務上：等於 mandatory。

### 13.6 ISO 27001 Annex A.10 (Cryptography)

```text
A.10.1.1 — Policy on the use of cryptographic controls
A.10.1.2 — Key management
```

簡短但要求 organization 有：
- **書面密碼學政策**（哪些資料要加密、用什麼算法、key lifecycle）
- **key management policy**

→ 寫一份「Cryptographic Policy v1」放 wiki，就是 SRE / DevSecOps 履歷的硬核產出。

### 13.7 各國 / 各產業綜合對照

| 法規 / 標準 | 必修加密 | Rotation 要求 |
|---|---|---|
| PCI DSS 4.0 | 卡號 + 認證資料 | ≤ 1 年 |
| HIPAA | PHI（健康資訊） | best practice |
| GDPR | 個資（PII） | best practice |
| SOC 2 | 「customer data」 | controlled |
| ISO 27001 | 依風險 assessment | 書面政策 |
| FedRAMP | All government data | FIPS 140-2 L3 |
| 中國《個資法》PIPL | 個資 | 強制 |
| 台灣《個資法》 | 個資 | 規範性指引 |
| 日本 APPI | 個資 | 規範性指引 |
| 韓國 PIPA | 個資 | 規範性指引 |

### 13.8 Export Control 基礎

「加密算法」歷史上是美國 export control 管制品（ITAR / EAR）。
**現在大部分密碼學軟體已 export 自由化**，但仍有：
- 不要把含強加密的軟體賣 / 提供給 OFAC 制裁國家
- 部分 high-end HSM 仍受管制
- 自己開 SaaS 跨國服務時注意

**對工程師的實務：** 用 mainstream library（OpenSSL / Go crypto / libsodium）沒 export 問題。

### 13.9 履歷怎麼寫

```text
Implemented cryptographic controls aligned with SOC 2 Type II (CC6.1, CC6.6-6.8),
PCI DSS 4.0, and ISO 27001 Annex A.10. Designed TLS 1.3-only baseline,
KMS-based envelope encryption, automated cert rotation via cert-manager,
and verifiable audit logging using Trillian Merkle log.
```

關鍵字密度高、可審計、與職涯主軸（Cloud Platform + DevSecOps + FinOps）一致。

---

<a id="learning-path"></a>

# Part VI — 學習與 Portfolio

## 14. 學習路線：先實務、再原理、最後進階

我給你的順序刻意**反教科書**：教科書從數學起手，工程師應該從場景起手。

### Phase 1 — 把你天天用的東西看懂（2-3 週）

目標：能在面試講出「TLS 握手在幹嘛、KMS envelope 怎麼運作」。

- [ ] 用 `openssl s_client` 解一次大型網站的 TLS chain
- [ ] 把 nginx HTTPS 設定從零跑通，包含 Let's Encrypt + auto-renew
- [ ] 用 `jwt.io` 拆一個真實 JWT，自己用 RS256 簽 / 驗一次
- [ ] 在 AWS console 玩 KMS：create CMK、encrypt / decrypt，看 CloudTrail
- [ ] 跑一次 SSE-KMS S3 物件，理解 envelope 在哪一層
- [ ] 在 K8s 用 cert-manager 自動發 cert 給 Ingress
- [ ] **(v2)** 走一次 §9 的 IR playbook 模擬：手動讓 cert 過期，照 playbook 修

### Phase 2 — 補概念（2-3 週）

目標：能看懂 RFC 摘要、能在 design review 講「為什麼選這個演算法」。

- [ ] 讀過[理論篇 Part I（§1-§3）](./cryptography-core-theory.md)建立數學直覺
- [ ] 讀過 *Real World Cryptography（David Wong）* 的前半
- [ ] 跑過一次 [Cryptopals Set 1-2](https://cryptopals.com/)（理解 padding oracle 與 ECB）
- [ ] 對 TLS 1.3 的 [RFC 8446](https://datatracker.ietf.org/doc/html/rfc8446) 至少讀 §1-2 + §4 摘要

### Phase 3 — DevSecOps 場景深掘（3-4 週）

目標：portfolio 能講「我做了 supply chain hardening」。

- [ ] 在 homelab 跑 Cosign keyless signing + Rekor 驗證
- [ ] 用 Syft 產 SBOM、用 Grype 驗 CVE、簽 SBOM 成 in-toto attestation
- [ ] 在 K8s 跑 Kyverno policy：只接受簽過名的 image
- [ ] 部署 cert-manager + private CA，自己發 mTLS cert
- [ ] EKS IRSA / GitHub Actions OIDC：把長期 AWS key 從 CI 移除
- [ ] 部署 External Secrets Operator 連 AWS Secrets Manager
- [ ] 寫一份 secret inventory（哪些 secret 存在哪、誰管、多久輪）
- [ ] **(v2)** 部署 Trillian + 自製 deploy audit log（§12.6 Lab）
- [ ] **(v2)** 寫一份「KMS 成本分析」proposal（§11.10 Lab）

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

## 15. Portfolio 任務：接到 Secure FinOps Platform for K8s

把這份筆記「落地」到 `devops-homelab/projects/secure-finops-k8s-platform/`，
讓密碼學知識變成可以寫進履歷、可以 demo 給面試官的真實作品。

### 15.1 對應 [secure-finops-k8s-platform/plan.md](../../devops-homelab/projects/secure-finops-k8s-platform/plan.md) 的可插入點

| Plan 中現有任務 | 加上密碼學能力後變什麼 |
|---|---|
| GitHub Actions / GHCR / ArgoCD GitOps 閉環 | + Cosign signing + Kyverno verify + SBOM attestation |
| Trivy image scan、SBOM | + Sigstore attestation + SLSA L2 provenance + VEX |
| secret inventory 與 rotation note | + KMS envelope flow 圖 + External Secrets Operator + Vault Shamir DR drill |
| K8s RBAC、NetworkPolicy、Pod Security | + projected ServiceAccount token + IRSA-like 短期 token + SPIFFE 對照 |
| OPA / Kyverno guardrails | + 只允許簽過名 image、阻擋 default ServiceAccount |
| AWS 對照（IAM、Cost Explorer、GuardDuty） | + KMS / ACM / Secrets Manager / IAM OIDC 對應表 + GCP/Azure |
| **(v2) FinOps** | + Cryptographic FinOps 成本分析（§11.10） |
| **(v2) SRE 主軸** | + Incident Response Playbook（§9）+ Observability dashboard（§10） |
| **(v2) Compliance** | + SOC 2 / PCI DSS / ISO 27001 mapping（§13） |
| **(v2) Audit** | + Trillian verifiable deploy log（§12.6） |

### 15.2 建議新增的 lab 任務（10 個，可挑著做）

1. **Lab A：Cosign keyless 簽 + Kyverno 驗** ⭐
2. **Lab B：External Secrets + AWS Secrets Manager** ⭐
3. **Lab C：cert-manager + 私有 CA + mTLS**
4. **Lab D：etcd encryption + KMS provider mock**
5. **Lab E：SBOM + supply-chain dashboard**
6. **Lab F：GitHub Actions OIDC → AWS IAM role** ⭐
7. **(v2) Lab G：Cryptographic FinOps 成本分析 proposal** ⭐⭐
8. **(v2) Lab H：Trillian verifiable deploy audit log** ⭐
9. **(v2) Lab I：Cert expiry monitoring + IR playbook drill** ⭐
10. **(v2) Lab J：Vault Shamir unseal + DR drill**

⭐ = 履歷亮點優先

### 15.3 履歷敘事建議

> Designed and implemented end-to-end supply-chain security for a Kubernetes homelab platform, including Cosign keyless signing with Sigstore/Rekor, SBOM attestation with in-toto/SLSA L2 provenance, Kyverno admission policies enforcing verified-image-only deployment, and GitHub Actions OIDC-based AWS authentication eliminating all long-lived cloud credentials. Built cryptographic observability dashboard tracking cert expiry, KMS API anomalies, and TLS handshake failures. Conducted KMS cost analysis identifying $XK/month savings via envelope encryption optimization and ECDSA cert migration. Deployed Trillian-backed verifiable audit log for deployment events, enabling tamper-evident compliance audit (aligned with SOC 2 CC6 and ISO 27001 A.10).

對應到 JD 關鍵字：DevSecOps、Supply Chain Security、Zero Trust、KMS、Image Signing、OIDC、FinOps、SOC 2、SRE Observability。

---

<a id="references"></a>

## 16. 參考資源

**書（給工程師的，不是教科書）：**

- *Real World Cryptography*，David Wong — 工程師密碼學第一本就讀這本
- *Cryptography Engineering*，Ferguson / Schneier / Kohno — 偏理論但仍可讀
- *Bulletproof TLS and PKI*，Ivan Ristić — TLS / PKI 唯一一本
- *Serious Cryptography*，JP Aumasson — 想再深入時讀
- *Site Reliability Engineering*（Google） — SRE 主線
- *Securing DevOps*，Julien Vehent — DevSecOps 工程

**官方文件 / 標準：**

- [RFC 8446 (TLS 1.3)](https://datatracker.ietf.org/doc/html/rfc8446)
- [RFC 7519 (JWT)](https://datatracker.ietf.org/doc/html/rfc7519)
- [RFC 8555 (ACME)](https://datatracker.ietf.org/doc/html/rfc8555)
- [RFC 9449 (DPoP)](https://datatracker.ietf.org/doc/html/rfc9449)
- [RFC 6962 (Certificate Transparency)](https://datatracker.ietf.org/doc/html/rfc6962)
- [NIST SP 800-57（Key Management）](https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final)
- [NIST SP 800-61（Incident Response）](https://csrc.nist.gov/pubs/sp/800/61/r2/final)
- [SLSA spec](https://slsa.dev/)
- [in-toto](https://in-toto.io/)
- [OpenVEX](https://openvex.dev/)
- [SPIFFE / SPIRE](https://spiffe.io/)

**雲端 / K8s 文件：**

- [AWS KMS developer guide](https://docs.aws.amazon.com/kms/latest/developerguide/) — envelope encryption 那節必讀
- [Kubernetes Encrypting Secret Data at Rest](https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/)
- [cert-manager docs](https://cert-manager.io/docs/)
- [Sigstore docs](https://docs.sigstore.dev/)
- [Cosign quickstart](https://docs.sigstore.dev/cosign/signing/quickstart/)
- [Kyverno verifyImages](https://kyverno.io/docs/policy-types/verify-images/)
- [Trillian](https://github.com/google/trillian)
- [GUAC](https://guac.sh/)

**動手練習：**

- [Cryptopals](https://cryptopals.com/) — 經典 8 set
- [Sigstore the easy way](https://docs.sigstore.dev/quickstart/quickstart-cosign/)
- [AWS Cryptography Specialty 證照官方教材](https://aws.amazon.com/certification/certified-security-specialty/) — 進階目標可以考慮

**Side line（不在主線）：**

- 量子密碼學：[NIST PQC](https://csrc.nist.gov/projects/post-quantum-cryptography) — 知道 ML-KEM / ML-DSA 已標準化即可
- Zero-knowledge：純興趣，跟你主線無關

---

<a id="interview-qa"></a>

# Appendix A：面試題庫

> 對應你的求職主軸（台 / 日 / 韓 Cloud / DevOps / SRE / Platform Engineer）。
> 每題給「面試官想聽什麼」與「對應章節」。

## A.1 Cloud Platform / Cloud Architecture 題

### Q1：請解釋 AWS KMS 的 envelope encryption。
**面試官想聽：** Plaintext → DEK (AES-GCM) → DEK 由 CMK 加密 → 存 ciphertext + encrypted DEK → 讀回時 KMS 解 DEK → DEK 解資料。
**進階：** 為什麼這比直接 KMS encrypt 大檔案好？（4 KB 限制、API 費用、延遲）
**對應：** §4.4、§11.2

### Q2：ACM 與 KMS 差在哪？什麼時候用哪個？
**面試官想聽：** ACM 給公網 TLS cert（不能 export priv key，只能配 ELB/CloudFront/API GW）；KMS 是通用 key 管理（symmetric + asymmetric）。
**對應：** §7.1

### Q3：S3 SSE-S3 / SSE-KMS / SSE-C 差別？
**面試官想聽：** 持 key 的 entity（AWS / 你的 KMS CMK / 你自己提供）、成本、audit trail 差異。Bucket Key 必開降 KMS cost。
**對應：** §7.1、§11.5

### Q4：GitHub Actions 連 AWS 怎麼做最安全？
**面試官想聽：** OIDC federation + IAM role + condition limit (sub = repo + branch)，不存 long-lived access key。
**對應：** §5.3

### Q5：你怎麼設計跨 region key 管理？
**面試官想聽：** AWS KMS MRK（multi-region keys），各 region replica；policy 仍 region-scope。
**對應：** §4.8

### Q6：GCP Workload Identity 與 AWS IRSA 有什麼類似？
**面試官想聽：** 兩者都是「K8s ServiceAccount 透過 OIDC federation 換 cloud 短期憑證」。對照 GCP Workload Identity 與 EKS IRSA 都用同一個概念。
**對應：** §5.2、§7.2

## A.2 SRE / On-call 題

### Q7：你發現某個 service cert 還剩 1 天到期，怎麼處理？
**面試官想聽：** §9.A playbook：confirm → backup cert 替換 → cert-manager force renew → 監控 → post-mortem。
**對應：** §9.A

### Q8：production 突然開始 mTLS 握手失敗，你怎麼 debug？
**面試官想聽：** 先確認時鐘（clock skew）、看 cert chain 完整性、SAN 是否對、CA bundle 是否同步、是否雙邊一邊先換 cert（§3.4 場景 B）。
**對應：** §3.3、§3.4

### Q9：如果你的 KMS CMK 不小心被 schedule deletion，怎麼救？
**面試官想聽：** 7-30 天 grace period 內 `aws kms cancel-key-deletion`；過期就永久喪失 → 啟動 DR。
**對應：** §9.C

### Q10：你怎麼監控 cert 即將過期？
**面試官想聽：** Prometheus blackbox_exporter + `probe_ssl_earliest_cert_expiry`；或 cert-manager metric；30 / 7 / 1 天三級告警。
**對應：** §10.1

### Q11：你會怎麼監控 KMS API 異常？
**面試官想聽：** CloudWatch Anomaly Detector on Decrypt rate；CloudTrail 寄到 SIEM；針對特定 role 的 KMS 用量設 baseline。
**對應：** §10.2

### Q12：JWT 驗證 failure rate 突然升高，可能原因？
**面試官想聽：** JWKS rotation 未同步、client clock skew、攻擊（暴力 token forge）、library 版本 bug。
**對應：** §10.4

## A.3 DevSecOps 題

### Q13：解釋 Sigstore Cosign keyless signing 為什麼比 GPG 好。
**面試官想聽：** OIDC + 短期 cert (Fulcio) + 透明日誌 (Rekor) → 不用管 priv key、攻擊者偷簽全世界看得到。
**對應：** §6.2

### Q14：SLSA 是什麼？L2 與 L3 差在哪？
**面試官想聽：** Supply-chain Levels for Software Artifacts。L2 需要 hosted CI 簽 provenance；L3 加上 builder isolation + hermetic build。
**對應：** §6.4

### Q15：怎麼設計「只接受簽過名 image」的 K8s policy？
**面試官想聽：** Kyverno verifyImages with keyless attestor，限定 issuer + subject regex。Admission controller 層擋。
**對應：** §6.8

### Q16：你的供應鏈被報「有 log4j 漏洞」，怎麼處理？
**面試官想聽：** §6.9 完整 triage workflow：scan → impact assessment → VEX 判斷 → CVSS+EPSS → P0/P1/P2 SLA → fix + canary → post-mortem。
**對應：** §6.6、§6.9

### Q17：K8s Secret 預設安全嗎？怎麼真正保護？
**面試官想聽：** base64 不是加密 → etcd encryption-at-rest (KMS provider) + RBAC + Pod Security + 不要 log。
**對應：** §4.1

### Q18：SPIFFE / SPIRE 解決什麼問題？
**面試官想聽：** Service-to-service identity，跨 K8s/VM/serverless 統一身分（SPIFFE ID）+ 自動 mTLS cert (X.509-SVID)。
**對應：** §5.6

### Q19：你怎麼設計 deploy audit log 讓 auditor 信？
**面試官想聽：** Hash chain（簡單）或 Merkle log（強）+ Signed Tree Head + 外部 timestamp；用 Trillian 跑。
**對應：** §12

## A.4 FinOps 題

### Q20：你怎麼降低 AWS KMS 成本？
**面試官想聽：** DEK caching、S3 Bucket Key 開啟、整併重複 secret、評估從 SSE-KMS → SSE-S3 是否可接受、monitor 哪些 service 是 cost driver。
**對應：** §11.2、§11.5

### Q21：CloudHSM 與 KMS 怎麼選？
**面試官想聽：** Tipping point ~270 req/sec；法規（FIPS L3）強制 HSM；自持 key 要 HSM；其他預設用 KMS。
**對應：** §11.3

### Q22：1 萬 secret 你會用 Secrets Manager 還是 SSM？成本怎麼算？
**面試官想聽：** SM $4000/月 vs SSM Advanced $500/月 vs SSM Standard 免費 quota。決策看：是否需要 rotation、敏感度、跨 region。
**對應：** §11.4

### Q23：你的 nginx CPU 跑很高，TLS handshake 占大部分，怎麼降？
**面試官想聽：** 從 RSA-2048 cert 換 ECDSA P-256（3× 快）；啟用 session reuse；考慮 TLS offload 到 LB / CDN。
**對應：** §11.6

## A.5 Compliance 題

### Q24：客戶要求 SOC 2 / ISO 27001 audit，你怎麼準備加密相關 controls？
**面試官想聽：** §13.4 SOC 2 CC6.1/6.6-6.8 對應到 RBAC + TLS 1.2+ + KMS rotation + observability dashboard；ISO 27001 A.10 要書面 cryptographic policy。
**對應：** §13.4、§13.6

### Q25：PCI DSS 4.0 對加密有什麼新要求？
**面試官想聽：** SHA-1 完全禁、TLS 1.0/1.1 禁、key rotation ≤ 1 年、PAN tokenization / FPE。
**對應：** §13.2

### Q26：FIPS 140-2 L3 對你的技術選型有什麼限制？
**面試官想聽：** 必須 CloudHSM 或經認證 HSM；X25519/Ed25519 目前還沒 FIPS 認證（需用 P-256 / RSA 替代）。
**對應：** §13.1

## A.6 進階 / 加分題

### Q27：Post-quantum 對你目前架構的威脅是什麼？
**面試官想聽：** RSA / ECC 受 Shor 攻擊；對稱 (AES-256) 加倍 key 即可。Harvest-now-decrypt-later 威脅長保密期資料。轉 hybrid (X25519 + ML-KEM)。
**對應：** §16（理論篇 §16）

### Q28：你怎麼設計 Vault 的 DR / unseal？
**面試官想聽：** Shamir 3/5 預設、5 個 admin 分持、定期 DR drill、Auto-Unseal with KMS（簡化但仍要備 KMS）。
**對應：** §4.7

### Q29：ECDSA 跟 Ed25519 你選哪個？為什麼？
**面試官想聽：** Ed25519 deterministic nonce（不依賴 RNG）+ constant-time + 快 + 小簽章；但 FIPS 還沒認 → 政府場景仍用 ECDSA P-256。
**對應：** §2.4

### Q30：你怎麼說明 forward secrecy 給非技術主管？
**面試官想聽：** 「即使我們的 server private key 哪天被偷了，過去截獲的網路封包仍解不開，因為當時的會話 key 是當下臨時產的、用完就丟。」
**對應：** §3.1

---

<a id="cheatsheet"></a>

# Appendix B：On-call Cheat Sheet

> 印一張貼螢幕邊。出事翻得到。

## B.1 openssl 瑞士刀

```bash
# === 看遠端 server cert ===
openssl s_client -connect HOST:443 -servername HOST -showcerts < /dev/null

# 簡短版（只看到期日 + SAN）
echo | openssl s_client -connect HOST:443 -servername HOST 2>/dev/null \
  | openssl x509 -noout -dates -ext subjectAltName

# === 看本地 cert ===
openssl x509 -in cert.pem -noout -text                    # 全文
openssl x509 -in cert.pem -noout -dates                   # 到期日
openssl x509 -in cert.pem -noout -subject -issuer         # 簡短
openssl x509 -in cert.pem -noout -ext subjectAltName      # SAN

# === 驗證 chain ===
openssl verify -CAfile root.pem -untrusted intermediate.pem leaf.pem

# === 看 key ===
openssl rsa -in key.pem -noout -text                      # RSA priv key
openssl ec  -in key.pem -noout -text                      # EC priv key
openssl pkey -in key.pem -noout -text                     # 通用

# === 比對 cert 與 key 是否對應 ===
openssl x509 -in cert.pem -noout -modulus | openssl md5
openssl rsa  -in key.pem  -noout -modulus | openssl md5
# 兩個 md5 一樣 → 對應

# === 產自簽 cert（測試用）===
openssl req -x509 -newkey ec -pkeyopt ec_paramgen_curve:P-256 \
  -keyout key.pem -out cert.pem -days 365 -nodes \
  -subj '/CN=test.local' -addext 'subjectAltName=DNS:test.local'

# === OCSP 查詢 ===
openssl ocsp -issuer issuer.pem -cert leaf.pem -url http://ocsp.example.com -text

# === 看 cipher suites ===
openssl ciphers -v 'ECDHE+AESGCM'                         # 列符合的
nmap --script ssl-enum-ciphers -p 443 HOST                # 對遠端掃描
```

## B.2 AWS CLI 加密相關

```bash
# === KMS ===
aws kms list-keys
aws kms describe-key --key-id KEY_ID
aws kms list-aliases
aws kms encrypt --key-id KEY_ID --plaintext fileb://input.txt --output text --query CiphertextBlob | base64 -d > out.bin
aws kms decrypt --ciphertext-blob fileb://out.bin --output text --query Plaintext | base64 -d
aws kms generate-data-key --key-id KEY_ID --key-spec AES_256

# === Cancel deletion（救命指令）===
aws kms cancel-key-deletion --key-id KEY_ID

# === Secrets Manager ===
aws secretsmanager get-secret-value --secret-id NAME --query SecretString --output text
aws secretsmanager rotate-secret --secret-id NAME
aws secretsmanager list-secrets

# === ACM ===
aws acm list-certificates
aws acm describe-certificate --certificate-arn ARN
aws acm request-certificate --domain-name example.com --validation-method DNS

# === CloudTrail KMS 事件 ===
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=ResourceName,AttributeValue=KEY_ARN \
  --start-time $(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%S)

# === IAM access key（外洩處理）===
aws iam list-access-keys --user-name USER
aws iam delete-access-key --user-name USER --access-key-id AKIA...
aws iam list-attached-user-policies --user-name USER
```

## B.3 kubectl secret / cert 相關

```bash
# === 看 Secret ===
kubectl get secret -A
kubectl get secret NAME -n NS -o yaml
kubectl get secret NAME -n NS -o jsonpath='{.data.KEY}' | base64 -d

# === 創建 TLS Secret ===
kubectl create secret tls api-cert --cert=cert.pem --key=key.pem -n NS

# === cert-manager ===
kubectl get certificate -A
kubectl describe certificate NAME -n NS
kubectl get certificaterequest -A
kubectl logs -n cert-manager deployment/cert-manager

# === 強制 cert 重簽 ===
kubectl annotate certificate NAME -n NS \
  cert-manager.io/issue-temporary-certificate-

# === Cosign verify ===
cosign verify IMAGE@sha256:DIGEST \
  --certificate-identity-regexp ".*@example.com" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com"

# === Kyverno policy check ===
kubectl get clusterpolicy
kubectl describe clusterpolicy NAME

# === ServiceAccount token (debug) ===
kubectl create token SA_NAME -n NS --duration=10m
```

## B.4 通用 IR Commands

```bash
# === Git 找洩漏 ===
gitleaks detect --source . --report-format json
trufflehog git file://.

# === 從 git history 清除洩漏檔案 ===
git filter-repo --invert-paths --path leaked-key.pem
# 或 BFG Repo-Cleaner
java -jar bfg.jar --delete-files leaked-key.pem
git push --force --all

# === Vault ===
vault operator unseal SHARE
vault audit enable file file_path=/var/log/vault_audit.log
vault token revoke -accessor ACCESSOR

# === SSH 移除舊 host key ===
ssh-keygen -R HOST
```

## B.5 健康檢查清單（出事前）

- [ ] 所有 production cert 在 monitoring？
- [ ] cert-manager auto-renew 跑得起來？
- [ ] KMS 啟用 audit log + alert？
- [ ] 所有 long-lived AWS key 已移除（用 OIDC 取代）？
- [ ] Vault unseal share 5 人都還在公司？
- [ ] Sealed Secrets controller key 已備份到離線？
- [ ] Cosign 簽章 admission policy 是 Enforce 不是 Audit？
- [ ] Pre-commit hook 含 gitleaks / detect-secrets？
- [ ] 有 IR runbook 寫好？演習過嗎？

---

<a id="crossref"></a>

# Appendix C：與理論篇的交叉地圖

| 應用篇 § | 理論篇對應 |
|---|---|
| §2 核心地圖 | 理論篇 §4-§12 |
| §3 TLS / mTLS | 理論篇 §11 (KEX) + §13 (TLS internal) |
| §4 Secrets / KMS | 理論篇 §7 (AEAD) + §12 (KDF) + §19 (Vault Shamir) |
| §5 JWT / OIDC / SPIFFE | 理論篇 §8 (MAC) + §10 (Sig) |
| §6 Supply Chain | 理論篇 §10 (Sig) + §15 (Provable) + §18 (Merkle / Rekor) |
| §8 反 pattern | 理論篇 §14 (Attack taxonomy) |
| §9 IR Playbook | 全部章節 — 出事時翻得到底層原理 |
| §10 Observability | 理論篇 §14 (Attack) + §18 (Merkle for audit) |
| §11 FinOps | 理論篇 §7 (Envelope), §12 (KDF cache) |
| §12 Verifiable Log | 理論篇 §18 (Auth Data Structures) |
| §13 Compliance | 理論篇 §15 (Provable, FIPS 模型) |
| 後量子顧慮 | 理論篇 §16 (PQC) |
| ZK / 區塊鏈興趣 | 理論篇 §17 (ZK) |
| Vault unseal / threshold | 理論篇 §19 (Threshold) |

兩篇可以分開讀，但**應用篇有疑問時翻理論篇對應章節，理解會立刻深一層**。
這就是「會用」和「會解釋」的差距。

---

## v2 後記

從 v1 (921 行) 升級到 v2 (~2400 行) 的目標不是「多寫一倍」，而是**把這份筆記從「為了讀懂密碼學而寫的場景版」升級成「SRE / DevSecOps 工作完整手冊」**：

- §9 IR Playbook 把「出事時做什麼」變得可執行
- §10 Observability 把「事前監控」變成可落地的 PromQL / Dashboard
- §11 FinOps 直接接到你的職涯主軸「Cloud Platform + DevSecOps + **FinOps**」
- §12 Verifiable Log 接到理論篇 §18 Merkle，補上 audit / compliance 的密碼學工程實現
- §13 Compliance 把求職關鍵字（SOC 2 / PCI / ISO 27001 / FIPS）整理成可用清單
- Appendix A 30 題面試題庫 + Appendix B on-call cheat sheet 直接是「為你的工作 / 求職寫的工具」

如果你把這兩篇（v2 理論篇 + v2 應用篇）一起讀完，**Cloud Platform + SRE + DevSecOps + FinOps 四個面向的密碼學能力都到位**。
剩下的就是 Portfolio 與 Lab 落地。
