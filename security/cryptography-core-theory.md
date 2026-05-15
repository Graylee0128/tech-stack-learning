# 密碼學核心理論：給想看清楚黑盒裡面的工程師

> 更新：2026-05-15 (v2 — Part 分區、新增 4 章、大幅擴充 §3/§13/§15/§17、補自測題與 timeline)
> 姊妹篇：[cryptography-for-sre-devsecops.md](./cryptography-for-sre-devsecops.md)（應用篇）
> 定位：「為什麼這個算法是安全的？」「黑盒裡面到底在做什麼？」

---

## v2 改動摘要

| 變動 | 內容 |
|---|---|
| **結構重排** | 全書分 6 個 Part：基礎 / 對稱 / 公鑰 / 安全分析 / 進階 / 工程閱讀 |
| **新增章** | §18 Authenticated Data Structures、§19 Threshold Cryptography & Secret Sharing |
| **大幅擴充** | §3（security level + birthday + GNFS）、§13（TLS 1.3 key tree 解釋）、§15（reduction walkthrough）、§17（ZK simulator + R1CS pipeline） |
| **補充段落** | §1.6 worked computations、§11.5 Noise Framework、§16 SIS / FO transform |
| **教學工具** | 每章末加 🎯 自測題、Appendix B 密碼學工程史 timeline |

---

## 0. 序：為什麼工程師值得看懂理論

應用篇回答的是 **「我該選哪個、放哪裡、怎麼接到 K8s」**。
這篇回答的是 **「為什麼 AES 不會被破？為什麼 ECDH 安全？為什麼 nonce 重用會炸？」**

工程師看密碼學理論的合理深度是：

```text
不需要 → 自己證明算法安全、發 paper、設計新算法
需要   → 能讀懂 RFC / 標準文件的安全性聲明
       → 能講出「這個算法靠什麼 hard problem」
       → 能在 incident review 抓出「這個用法違反了哪個 assumption」
       → 能判斷 LLM、SO 答案是不是在說鬼話
```

理論的價值不在「會證明」，而在於建立**直覺地圖**：

- 看到 `AES-ECB` 馬上知道為什麼錯，不用查
- 看到「我們自己 wrap 一層 SHA256 來簽 token」馬上知道為什麼炸
- 聽到 quantum computing 來了，知道哪些東西要換、哪些不用慌
- 看到 ZK-proof 行銷文案，能判斷它在唬還是真的有用

---

## 目錄

### Part I — 基礎 Foundations
- [§1 數學最小集：你只需要這麼多](#math)
- [§2 資訊理論與隨機性](#info-theory)
- [§3 計算複雜度與單向函數](#complexity)

### Part II — 對稱密碼學 Symmetric Cryptography
- [§4 Hash function 內部結構](#hash)
- [§5 Block cipher 內部結構](#block-cipher)
- [§6 Stream cipher](#stream-cipher)
- [§7 AEAD：authenticated encryption 的構造](#aead)
- [§8 MAC 的理論](#mac)

### Part III — 公鑰密碼學 Public-Key Cryptography
- [§9 公鑰密碼學的數學基礎](#pkc-math)
- [§10 數位簽章理論](#signatures)
- [§11 密鑰交換、KEM 與 Noise 框架](#kex)
- [§12 KDF 與 password hashing 的設計](#kdf)
- [§13 TLS 1.3 的內部 key schedule](#tls-internal)

### Part IV — 安全分析 Security Analysis
- [§14 攻擊類型 taxonomy](#attacks)
- [§15 Provable Security 完整版](#provable)

### Part V — 進階主題 Advanced Topics
- [§16 Post-Quantum Cryptography](#pqc)
- [§17 Zero-Knowledge Proofs 完整入門](#zk)
- [§18 Authenticated Data Structures（新章）](#ads)
- [§19 Threshold Cryptography & Secret Sharing（新章）](#threshold)

### Part VI — 工程閱讀指南 Engineering Reading Guide
- [§20 怎麼讀 RFC 和密碼學 paper](#how-to-read)
- [§21 結語與進階閱讀](#closing)

### Appendices
- [A：詞彙對照表](#glossary)
- [B：密碼學工程史 timeline（新）](#timeline)
- [C：與應用篇的交叉地圖](#crossref)

---

# Part I — 基礎

<a id="math"></a>

## 1. 數學最小集：你只需要這麼多

工程師讀密碼學最大的卡關點是「數學」。
但其實你只需要四個概念就能讀懂 80% 的算法：**模運算、群、有限體、橢圓曲線**。

### 1.1 模運算 (Modular Arithmetic)

```text
a mod n 意思是「a 除以 n 的餘數」
17 mod 12 = 5      （想像時鐘）
(7 + 8) mod 12 = 3
(7 × 8) mod 12 = 4
```

**為什麼密碼學愛用模運算？**
- 結果永遠落在 `[0, n-1]`，是個有界集合
- 在有界集合裡可以做「反向難、正向易」的運算（trapdoor 的核心）
- 整數運算自然支援，CPU 友善

**重要恆等式：**

| 名稱 | 公式 | 用在 |
|---|---|---|
| Fermat 小定理 | `a^(p-1) ≡ 1 (mod p)`，p 為質數，gcd(a,p)=1 | RSA 證明、Miller-Rabin |
| Euler 定理 | `a^φ(n) ≡ 1 (mod n)`，gcd(a,n)=1 | RSA 為什麼能 decrypt |
| 中國剩餘定理 (CRT) | 一組同餘方程有唯一解 mod 乘積 | RSA 解密加速 |
| Bezout | `gcd(a,b) = ax + by`，可用擴展歐幾里得算 | 算模逆元 `a^(-1) mod n` |

**φ(n) 是什麼？** Euler totient：小於 n 且和 n 互質的數的個數。
若 `n = p × q`（兩個質數），則 `φ(n) = (p-1)(q-1)` — RSA 整個建在這上面。

### 1.2 群 (Group) — 工程師的直覺

群 = **一個集合 + 一個運算**，滿足四個條件：

1. **封閉**：a · b 還在集合裡
2. **結合**：(a · b) · c = a · (b · c)
3. **單位元**：存在 e 使得 a · e = a
4. **反元素**：每個 a 都有 a⁻¹ 使得 a · a⁻¹ = e

**為什麼工程師要知道群？** 因為現代密碼學幾乎所有非對稱算法都建在某個群上：

| 群 | 用在 |
|---|---|
| `(Z/nZ)*` 模 n 的可逆元群 | RSA |
| `(Z/pZ)*` 模質數 p 的乘法群 | 古典 DH |
| 橢圓曲線點群 `E(F_p)` | ECDH、ECDSA、Ed25519 |
| Lattice 的「模塊」（technically 不是群） | Kyber、Dilithium |

**生成元 (generator)：** 群 G 的元素 g，如果 G 中每個元素都能寫成 `g^k`，g 就是生成元。
**循環群 (cyclic)：** 有生成元的群。密碼學主要用循環群（DH、ECC 都是）。
**群階 (order)：** 群中元素的個數。Lagrange 定理：任一元素的階整除群階。
→ **ECDSA 的 nonce 必須在 `[1, n-1]`**（n 是基點 G 的階），因為 `nG = O`（無窮遠點）。

**離散對數 (Discrete Log)：** 給你 `g`, `h = g^k mod p`，求 k。
正向 `g^k` 算得快（quick exponentiation），反向求 k 很慢 — **這就是 DH / ECDH 的安全基礎**。

### 1.3 有限體 (Finite Field, GF)

體 = 群 + 「乘法也有反元素」（除了零）。
有限體就是元素數量有限的體。

兩種你會遇到的：

**GF(p)：模 p 的整數集合，p 是質數。**
- 加 / 減 / 乘 / 除（除了零）都封閉
- 古典 DH、RSA、P-256 曲線都建在某個 GF(p) 上

**GF(2^n)：二元多項式體。**
- 元素是「次數小於 n 的二元多項式」
- AES 的 S-box 與 MixColumns 建在 **GF(2^8)** 上，模不可約多項式 `m(x) = x^8 + x^4 + x^3 + x + 1`
- GHASH（GCM 的核心）建在 **GF(2^128)** 上

**為什麼用 GF(2^n)？** 因為「加法 = XOR」，硬體實作快到不行。

### 1.4 橢圓曲線 (Elliptic Curve, EC) — 直覺先於數學

橢圓曲線是滿足以下方程的點 `(x, y)` 集合（在某個體上）：

```text
y² = x³ + ax + b   （Weierstrass 形式）
```

**為什麼工程師要會 EC？**
- ECC 用比 RSA 小 10 倍的 key 達到同等安全（256-bit ECC ≈ 3072-bit RSA）
- 現代 TLS / SSH / VPN / signing 全面 ECC 化
- 行動裝置、IoT、低功耗場景幾乎只用 ECC

**橢圓曲線「加法」（不是普通加法）：**

```text
給兩點 P, Q：
1. 畫直線通過 P, Q
2. 直線與曲線交第三點 R'
3. 把 R' 對 x 軸翻過去 → 得 R = P + Q
```

聽起來怪？這是定義出來的，重點是它構成一個**群**。
有了群，就有 `kP = P + P + ... + P` (k 次) → **scalar multiplication（純量乘）**。

**代數公式（不同情況下）：**

```text
情況 A：P ≠ Q（P, Q 不互為負）
  s = (y_Q - y_P) / (x_Q - x_P) mod p
  x_R = s² - x_P - x_Q  mod p
  y_R = s(x_P - x_R) - y_P  mod p

情況 B：P = Q（點倍乘 doubling）
  s = (3x_P² + a) / (2y_P) mod p
  x_R = s² - 2x_P  mod p
  y_R = s(x_P - x_R) - y_P  mod p

情況 C：x_P = x_Q 但 y_P = -y_Q → P + Q = O（無窮遠點，群的單位元）
```

**橢圓曲線離散對數 (ECDLP)：**
給你 P 和 `Q = kP`，求 k → 沒人會。
這就是 ECDH / ECDSA / Ed25519 的安全來源。

**現代主流曲線：**

| 曲線 | 公式 / 體 | 安全等級 | 用途 |
|---|---|---|---|
| Curve25519 | Montgomery: `y² = x³ + 486662x² + x` over GF(2²⁵⁵ − 19) | 128-bit | X25519 (ECDH) |
| Ed25519 | Twisted Edwards 等價形式 | 128-bit | EdDSA |
| secp256r1 (P-256) | NIST 標準 Weierstrass over GF(p₂₅₆) | 128-bit | TLS、ACME、AWS KMS |
| secp384r1 (P-384) | 同上但 384 bit | 192-bit | 高安全等級 |
| secp256k1 | `y² = x³ + 7` | 128-bit | Bitcoin、Ethereum |

**為什麼 Curve25519 比 P-256 受好評？**
- 公式更簡單，實作不容易出 timing bug
- 沒有「special / corner case」（P-256 有 point at infinity 處理）
- 25519 系列的 RNG 風險低（EdDSA 用 deterministic nonce）
- DJB 設計時專門挑了「不容易被官方後門」的參數

### 1.5 你可以「知道存在」但不必深究的

| 數學物件 | 用在 | 對 SRE 的需要度 |
|---|---|---|
| Pairing (bilinear map) | BLS 簽章、ZK-SNARK | 知道名字 |
| Lattice（格） | Kyber、Dilithium（後量子） | 看 §16 |
| Polynomial ring `Z_q[x]/(x^n + 1)` | Ring-LWE | 知道存在 |
| Error correcting codes | McEliece（後量子） | 知道存在 |
| Isogeny | SIDH（已被破）、CSIDH | 略過 |

### 1.6 跑一個具體計算（worked examples）

光看公式不會算，這節示範三個工程師會在密碼學 code 裡看到的真實運算。

#### 例 1：用擴展歐幾里得求 7⁻¹ mod 11

我們要找 `x` 使 `7x ≡ 1 (mod 11)`。

**Step 1：跑歐幾里得演算法求 gcd(7, 11)**

```text
11 = 7 × 1 + 4
 7 = 4 × 1 + 3
 4 = 3 × 1 + 1
 3 = 1 × 3 + 0   → gcd = 1（因為互質才存在逆元）
```

**Step 2：反向回代，把 1 表示成 7 與 11 的線性組合**

```text
1 = 4 − 3 × 1
  = 4 − (7 − 4) × 1       = 2·4 − 1·7
  = 2·(11 − 7) − 1·7      = 2·11 − 3·7
```

**所以 `−3 × 7 ≡ 1 mod 11` → `7⁻¹ ≡ −3 ≡ 8 (mod 11)`**

驗證：`7 × 8 = 56 = 5 × 11 + 1` ✓

這 5 行運算就是 RSA `d = e⁻¹ mod φ(n)`、ECDSA 簽章公式裡 `k⁻¹` 計算、模逆元的整個機制。

#### 例 2：GF(2⁸) 上的 xtime（AES MixColumns 的基本操作）

AES 把 byte 視為 GF(2⁸) 元素，乘法是「多項式相乘後再 mod m(x) = x⁸ + x⁴ + x³ + x + 1」。

**xtime(a)** = `a × {02}` 在 GF(2⁸) 上，工程實作只要兩步：

```text
1. a 左移 1 bit
2. 若原本 MSB（bit 7）為 1 → XOR 0x1B
```

跑 `{57} × {02}`：

```text
{57} = 01010111
左移 1：10101110 = {AE}
MSB 原本是 0 → 不 XOR
結果 = {AE}
```

跑 `{87} × {02}`：

```text
{87} = 10000111
左移 1：00001110（MSB 溢出）
MSB 原本是 1 → XOR 0x1B
00001110 ⊕ 00011011 = 00010101 = {15}
```

任意 byte 乘任意 byte，可以拆成 xtime 與 XOR 的組合。
這就是為什麼 AES 在沒有 AES-NI 的平台仍能跑得不慢 — 整個乘法可以 lookup table 化（256-byte xtime table）。

#### 例 3：secp256k1 上的點加法

選兩點 P = (1, 2)、Q = (3, 4) 在某虛構小曲線 `y² = x³ + 7 mod 11`（玩具版 secp256k1）。

實際上 (1, 2) 不在此曲線上（驗：`2² = 4 ≠ 1³ + 7 = 8 mod 11`），但流程一樣。

假設我們有合法兩點 P = (x_P, y_P), Q = (x_Q, y_Q)，用情況 A 公式：

```text
s = (y_Q - y_P) × (x_Q - x_P)⁻¹  mod p
x_R = s² - x_P - x_Q  mod p
y_R = s × (x_P - x_R) - y_P  mod p
```

**真實 secp256k1：** p ≈ 2²⁵⁶ - 2³² - 977，基點 G 的 x ≈ 0x79BE667E F9DCBBAC...，所有計算都在 256-bit 大數模 p 下進行。

**為什麼 Curve25519 用 Montgomery 形式 + Montgomery ladder？**
Montgomery ladder 對每個 bit 都做同樣的兩個操作（add + double），無條件分支 → **constant-time，抗 timing attack**。Weierstrass 公式遇到 special cases 必須 branch，實作容易漏 timing 防護。

---

### 🎯 §1 自測

1. 為什麼 RSA 私鑰 `d` 存在的前提是 `e` 與 `φ(n)` 互質？（提示：§1.1 模逆元存在條件）
2. 用擴展歐幾里得算 5⁻¹ mod 7。
3. ECDSA 的 nonce k 為什麼不能是 0 或 n？（提示：§1.2 群階）
4. 在 GF(2⁸) 算 `{53} × {04}`。（提示：xtime 兩次）
5. 為什麼 P-256 的實作比 Curve25519 更容易寫出 timing bug？（提示：§1.4 special case）

---

<a id="info-theory"></a>

## 2. 資訊理論與隨機性

### 2.1 Shannon Entropy — 資訊量的數學

Shannon 1948 年提出：

```text
H(X) = -Σ p(x) log₂ p(x)
```

直覺：H(X) 是「平均要幾個 bit 才能描述 X 的結果」。

- 公平硬幣：H = 1 bit
- 公平 256 面骰：H = 8 bits
- 永遠正面的硬幣：H = 0 bits

**為什麼密碼學在意 entropy？**
- Key 的 entropy = 真實安全強度（256-bit key 但只有 40-bit entropy 沒意義）
- Password 強度 = entropy（這就是 zxcvbn、xkcd 936 那張圖在算的）
- RNG 的源頭必須有足夠 entropy

**Min-entropy vs Shannon entropy：**
密碼學更在意 **min-entropy** `H_∞ = -log₂(max_x p(x))`。
原因：攻擊者只需要猜「最可能那個」，平均值沒意義。

### 2.2 Perfect Secrecy 與一次性密碼本 (OTP)

Shannon 證明：**唯一**達到「絕對安全」的算法是 OTP（One-Time Pad）：

```text
ciphertext = plaintext XOR key   （key 真隨機、和 plaintext 一樣長、只用一次）
```

**為什麼絕對安全？** 對任何 ciphertext，所有 plaintext 都是等概率可能的。
**為什麼不實用？**
- key 要跟 plaintext 一樣長 → 你能安全傳 key 就能直接傳 plaintext
- key 不能重複用（重用會 catastrophic：兩個 ciphertext XOR = 兩個 plaintext XOR，露陷）
- 真隨機 key 很難量產

**所有「實用」密碼學都是在「強度」與「效率」之間做的妥協。**

### 2.3 隨機性的三個層次

```text
┌─────────────────────────────────────────────────┐
│ 1. True Random (TRNG)                            │
│    來自物理熵源：熱噪、雜訊、量子事件、user input    │
│    Linux: /dev/random (blocking)                 │
│                                                  │
│ 2. PRG (Pseudo-Random Generator)                 │
│    從短 seed 拉出長序列；數學上「看起來」隨機         │
│    舊式：LCG、Mersenne Twister（不適合密碼學）      │
│                                                  │
│ 3. CSPRG (Cryptographically Secure PRG)         │
│    PRG + 「即使看完前 n 個輸出，第 n+1 個也猜不到」  │
│    Linux: /dev/urandom、getrandom(2)             │
│    程式：crypto/rand、secrets、crypto.randomBytes │
└─────────────────────────────────────────────────┘
```

**為什麼 `/dev/urandom` 就夠？**
歷史上有「`urandom` 不夠安全要用 `random`」的迷思。現代 Linux（boot 後 entropy pool 飽和）兩者輸出品質一致；`urandom` 不會阻塞，是預設正確選擇。`random` 阻塞反而造成 boot-time 服務 hang。

**CSPRG 設計範例：Linux 的 ChaCha20-based RNG**
從 4.8 之後，kernel RNG 內部就是用 ChaCha20 當 PRG，定期混入新熵 reseeding。

**NIST SP 800-90A** 列出三個 approved CSPRG：
- HMAC_DRBG
- HASH_DRBG
- CTR_DRBG（AES-CTR-based）

> 還有一個叫 **Dual_EC_DRBG** 被 NSA 後門過、已撤銷 — 這是「不要盲目相信 NIST」的歷史教材。

### 2.4 隨機性測試

你不能用看的判斷一串 bit 是不是「夠隨機」。
NIST SP 800-22 給了 15 個統計測試（monobit、runs、approximate entropy、Maurer's universal、…），但這些只能查出「明顯不隨機」，不能證明「真的隨機」。

**Dieharder / TestU01 BigCrush** 是更嚴的工具集。

對 SRE 的實務啟示：
- 永遠用 OS 提供的 CSPRG，不要自己拼
- 不要相信 hardware RNG 直接輸出（要 whiten + 混入 software pool）
- 不要拿 `time()` 當 seed

---

### 🎯 §2 自測

1. 一個 16 字元、只用小寫字母的密碼，entropy 有幾 bit？是否「夠強」？
2. 為什麼 OTP 的 key 不能重複使用？舉一個具體攻擊。
3. 為什麼 `Math.random()` 不能拿來產 session token？（提示：§2.3 三層）
4. Dual_EC_DRBG 的故事教我們什麼工程教訓？

---

<a id="complexity"></a>

## 3. 計算複雜度與單向函數

### 3.1 P / NP / BQP — 30 秒版本

- **P**：可在多項式時間內解的問題
- **NP**：「答案給你你能在多項式時間驗證」的問題
- **NP-hard / NP-complete**：NP 中最難的一類
- **BQP**：量子電腦能在多項式時間內解的問題

**密碼學依賴的 trust：**
- 我們相信 `P ≠ NP`（沒人證明，但所有實驗都支持）
- 我們相信某些問題「不在 P 裡」（但很多也不在 NP-complete 裡，更像是介於中間）

### 3.2 One-Way Function (OWF) — 密碼學的最基本假設

一個函數 `f` 是 **單向函數**，如果：

```text
正向 f(x) → y    容易 (poly time)
反向 y → x       困難 (super-poly time)
```

**沒人證明過 OWF 存在。** 整個現代密碼學是「假設」OWF 存在的建築。
如果某天有人證明 OWF 不存在，**所有對稱與非對稱密碼學都倒掉**（包含這份筆記 99% 的內容）。

候選的 OWF：
- 大數質因數分解（factoring）
- 離散對數（DLOG）
- 橢圓曲線離散對數（ECDLP）
- 格上的 LWE / SVP 問題
- Hash function（被假設是 OWF）

### 3.3 Trapdoor Function — 公鑰密碼學的根

Trapdoor function = OWF + 「但如果你有 trapdoor 那個秘密，就能反向」。

```text
f(x) → y                正向 easy
y → x  without trap     hard
y → x  with trap        easy
```

**RSA 是經典 trapdoor：** 把訊息 m 用 `c = m^e mod n` 加密。
- 不知道 `p, q`（n 的兩個質因數）→ 求 m 是 hard problem
- 知道 `p, q` → 用 CRT 與 Fermat 快速求 m

公鑰 = `(e, n)`、私鑰 = `(p, q)` 或等價的 `d`。

### 3.4 密碼學依賴的 hard problem 清單

| 問題 | 描述 | 用於 | 量子安全？ |
|---|---|---|---|
| Integer Factorization | 給 N=pq，求 p,q | RSA | ❌（Shor） |
| DLOG mod p | 給 g, g^x mod p，求 x | 古典 DH、DSA | ❌（Shor） |
| ECDLP | 給 P, kP，求 k | ECDH、ECDSA、Ed25519 | ❌（Shor） |
| SVP / CVP (lattice) | 在 lattice 找最短/最近向量 | Kyber、Dilithium | ✅（目前） |
| LWE / Ring-LWE | 解帶噪音的線性方程 | 同上 | ✅ |
| SIS / Module-SIS | 找短整數解使 As=0 | Dilithium、Falcon | ✅ |
| Syndrome Decoding (code) | 解碼 random linear code | McEliece | ✅ |
| MQ (multivariate quadratic) | 解多變量二次方程組 | Rainbow（已被破） | 部分 |
| Hash 抗碰撞 | 找兩個輸入產生同 hash | SPHINCS+（PQC 簽章） | ✅（Grover 只把成本減半） |
| Isogeny walking | 兩個 elliptic curve 之間的同源映射 | SIDH（已被破）、CSIDH | ? |

### 3.5 Security Level — 「128-bit 安全」到底是什麼

工程師看到 RFC 寫「This scheme provides 128 bits of security」要看得懂。

**定義：** 攻擊者要破這個 scheme 預期需要 **2^128 次基本操作**。

**為什麼 128 bit 是「夠用」的標竿？**

| 操作次數 | 換算（2026 年量級） | 意義 |
|---|---|---|
| 2^10 ≈ 10³ | 一台 PC 一毫秒 | 玩具 |
| 2^20 ≈ 10⁶ | 一台 PC 一秒 | 線上即時破 |
| 2^30 ≈ 10⁹ | 一台 PC 一分鐘 | 字典攻擊弱密碼 |
| 2^40 ≈ 10¹² | 一台 GPU 一小時 | DES (1990s 已可) |
| 2^56 | DES brute force（1998 EFF 機器 22 小時） | 不再安全 |
| 2^64 | 大型雲端 cluster 一個月 | 邊緣 |
| 2^80 | 國家級對手不可行（舊標準） | 已退役 |
| 2^85 | Bitcoin 全網一天 hash 數 | 真實世界規模 |
| 2^100 | 全人類運算能力多年 | 不可能 |
| 2^128 | **永遠不可行的現代標準** | AES-128、X25519、SHA-256 collision |
| 2^192 | AES-192、SHA-384 collision | 量子保險 |
| 2^256 | 物理極限附近（Landauer 限制） | 不必再多 |

**Landauer 限制：** 翻一個 bit 至少要消耗 `kT ln 2` 能量（k=Boltzmann 常數）。即使把太陽所有能量都拿來算 2^256，宇宙都會先冷掉。

**所以「128-bit 安全」就是工業界的「足夠就好」標準** — 經典攻擊不可能，量子攻擊也只把成本減半（變 64-bit，仍勉強撐得住）。
**256-bit 安全**是「我要對抗量子也綽綽有餘」的設定。

### 3.6 Birthday Bound：為什麼 collision 只要 2^(n/2)

**生日悖論**：23 個人裡兩人同生日的機率超過 50%（直覺說該要 183 人）。

**數學推導：**

從 N 個桶隨機抽 q 個樣本，至少有兩個落在同桶的機率：

```text
P(collision) ≈ 1 - exp(-q² / 2N)
```

設 P = 1/2，解出：

```text
q ≈ √(2N · ln 2) ≈ 1.177 √N
```

對 n-bit hash，N = 2^n，所以 collision 出現的 q ≈ 2^(n/2)。

**工程後果：**

| Hash | 抗碰撞強度 | 安全等級 |
|---|---|---|
| MD5 (128-bit) | 2^64 | 已破（2004 起持續被攻破） |
| SHA-1 (160-bit) | 2^80 | 已破（2017 SHAttered） |
| SHA-256 (256-bit) | 2^128 | 安全 |
| SHA-384 (384-bit) | 2^192 | 量子安全餘裕 |
| SHA-512 (512-bit) | 2^256 | 過度安全 |

**這就是為什麼想要「128-bit collision 等級」hash 必須至少 256-bit output。**

另一個 birthday 應用：**GCM nonce 重複**。隨機 96-bit nonce 在 2^48 次加密後有顯著碰撞概率 → 為什麼大規模 GCM 部署必須用 deterministic nonce 或 GCM-SIV。

### 3.7 GNFS 與「RSA-2048 為什麼只值 112-bit 安全」

RSA 的安全靠「大數質因數分解難」。**最佳已知經典算法**是 General Number Field Sieve (GNFS)：

```text
GNFS 複雜度：L_N(1/3, c) = exp((c + o(1)) · (ln N)^(1/3) · (ln ln N)^(2/3))
```

這是 **sub-exponential**（次指數）— 比 brute force `2^(N bits)` 快很多，但比 polynomial 慢。

**對應實際安全等級：**

| RSA modulus | GNFS 操作數 | 等效 bits of security |
|---|---|---|
| RSA-1024 | ~2^80 | 80 (已不安全) |
| RSA-2048 | ~2^112 | **112** |
| RSA-3072 | ~2^128 | 128 |
| RSA-7680 | ~2^192 | 192 |
| RSA-15360 | ~2^256 | 256 |

**為什麼 RSA-2048 = 112-bit 而不是 2048-bit？**
因為攻擊者不需要 brute force 整個 2^2048 space — 跑 GNFS 只需要 ~2^112 操作。

**這也是為什麼 ECC-256 ≈ RSA-3072：**
ECDLP 沒有 sub-exp 算法（只有 generic group 算法 Pollard rho，複雜度 √(group order) = 2^128 for 256-bit curve）。
所以 ECC 用更短的 key 達到同等安全。

**對 SRE 的實務啟示：**
- 法規寫「RSA 至少 2048 bit」其實是「至少 112-bit 等級」
- 想要真正 128-bit 安全的 RSA 需要 3072+
- 想要 future-proof + quantum 過渡安全 → ECC + hybrid PQC

---

### 🎯 §3 自測

1. 一個「2^96 操作」的攻擊，現實中是「可行」還是「不可行」？理由？
2. 為什麼 SHA-256 的「抗碰撞」是 128-bit 而不是 256-bit？
3. 如果某人說「我用了 4096-bit RSA 比 256-bit ECC 安全」，這對嗎？
4. 「假設 OWF 存在」這句話為什麼是整個密碼學的「信仰中心」？

---

# Part II — 對稱密碼學

<a id="hash"></a>

## 4. Hash function 內部結構

### 4.1 安全性質的三個層次

Hash function `H: {0,1}* → {0,1}^n` 的標準三項安全：

| 性質 | 攻擊者目標 | 預期成本 |
|---|---|---|
| **Preimage resistance** | 給 `y`，找 `x` 使 `H(x) = y` | 2^n |
| **2nd-preimage resistance** | 給 `x`，找 `x' ≠ x` 使 `H(x') = H(x)` | 2^n |
| **Collision resistance** | 找任意 `x ≠ x'` 使 `H(x) = H(x')` | 2^(n/2)（生日攻擊） |

**Collision 為什麼只要 2^(n/2)？** 見 §3.6 birthday bound 推導。
所以「想對抗 collision 到 128-bit 等級，hash 要至少 256-bit」 — 這就是為什麼現代 hash 是 256 bit 起跳。

### 4.2 Merkle–Damgård 構造（SHA-1 / SHA-2 家族）

```text
M = M₁ ∥ M₂ ∥ ... ∥ Mₖ   （切成固定長度 block，後面 pad 長度）

IV → f(IV, M₁) → h₁ → f(h₁, M₂) → h₂ → ... → hₖ = H(M)

f 是「compression function」：固定大小輸入 → 固定大小輸出
```

**精髓：**
- 一切從固定的 IV 開始
- 把訊息切塊，逐塊壓進「state」
- 最後 state 就是 hash

**MD 構造的著名缺陷：Length Extension Attack**

若你知道 `H(M)`，**即使不知道 M**，你也可以算出 `H(M ∥ padding ∥ M')` 的值（M' 是你選的）。

**為什麼？** 因為 H(M) 就是最後 state，攻擊者把它當新 IV，繼續餵 M' 進去就行。

**工程後果：** 不要把 `H(secret ∥ message)` 當作 MAC（這是早年 Flickr / Vine 等公司的 API 漏洞）。
**正確做法：** 用 HMAC（看 §8）。

**哪些 hash 受影響？** MD5、SHA-1、SHA-256、SHA-512。
**哪些不受影響？** SHA-3（sponge）、BLAKE2、BLAKE3、SHA-512/256（截斷後的版本）。

### 4.3 Sponge 構造（SHA-3 / Keccak）

```text
state = r ∥ c    （rate + capacity，總長 b）

吸收 (absorb)：       擠出 (squeeze)：
M₁ → state XOR → f →  → output ← state
M₂ → state XOR → f →  → output ← f(state)
M₃ → state XOR → f →  ...
```

- **rate (r)**：每次吸入 / 擠出的 bit 數
- **capacity (c)**：留給安全性的「保留區」，攻擊者碰不到
- 安全強度 ≈ c / 2

**為什麼 SHA-3 不怕 length extension？**
最後輸出只「擠出 rate 部分」，capacity 那段攻擊者拿不到 → 無法繼續餵新訊息。

**Keccak 一家**支援多種輸出長度（SHA3-224 / 256 / 384 / 512、SHAKE128 / 256 變長輸出）。

### 4.4 為什麼 SHA-256 「還沒倒」

SHA-256 是 SHA-2 家族成員，2001 年 NIST 標準化，至今 25 年。
最佳已知攻擊：對簡化版 (reduced rounds) 有理論優勢，**完整 64 round 對碰撞仍要 2^128 操作**。

實務上你應該：
- 完整性 / 數位簽章 / Merkle tree / image digest → SHA-256 完全夠用
- 高安全等級或要 future-proof → SHA-512 / SHA-3-512
- 性能極致 → BLAKE3（比 SHA-256 快 5-10 倍，且 parallel friendly）

### 4.5 BLAKE2 / BLAKE3

- BLAKE2：基於 ChaCha-like permutation 的 hash，速度比 SHA-256 快、安全等同
- BLAKE3：更激進的 Merkle tree 架構，原生支援 parallelism、streaming、KDF、XOF
- 為什麼不是主流？因為產業慣性 — 銀行、護照、TLS cert 都用 SHA-2

### 4.6 工程連結

| 場景 | 用什麼 hash |
|---|---|
| Git commit | SHA-1 → 正在過渡到 SHA-256 |
| Container image digest | SHA-256 |
| Merkle tree (S3 ETag, Bitcoin block) | SHA-256（詳見 §18） |
| Password hashing | **不要用 hash function**，用 KDF（§12） |
| HMAC | SHA-256 / SHA-512 |
| TLS handshake transcript | SHA-256 / SHA-384 |
| Sigstore Rekor entry | SHA-256（詳見 §18） |

---

### 🎯 §4 自測

1. 為什麼 SHA-256 的 length extension 不是「漏洞」但 `H(secret ∥ msg)` 當 MAC 是漏洞？
2. 若有人發明 2^110 的 SHA-256 碰撞算法，會是現實威脅嗎？（提示：對照 §3.5）
3. SHA-3 為什麼設計成「不能 length extension」是有意而非偶然？
4. 為什麼 BLAKE3 對 streaming 場景特別有優勢？

---

<a id="block-cipher"></a>

## 5. Block cipher 內部結構

Block cipher = 「把 n-bit plaintext block 在 key 控制下確定性地映射到 n-bit ciphertext block」的可逆函數。

兩大設計家族：**Feistel** 和 **SPN（Substitution-Permutation Network）**。

### 5.1 Feistel Network (DES、Blowfish、Camellia、GOST)

```text
把 block 切兩半 L₀ ∥ R₀

每 round：
  L_{i+1} = R_i
  R_{i+1} = L_i XOR F(R_i, K_i)

優點：F 不必可逆，因為「左右交換」確保可逆
缺點：每 round 只動一半，要更多 round
```

DES 是 16 round Feistel。3DES = 三次 DES，56-bit × 3 = 名義 168-bit 但實際 ~112-bit 安全。
現在 DES / 3DES 都已淘汰（NIST 2023 年正式撤銷 3DES）。

### 5.2 AES (Rijndael) — 現代 SPN 代表

AES 是 SPN 結構，2001 年取代 DES。
版本：AES-128 / AES-192 / AES-256（差別在 key 長度與 round 數）。

**Block 大小固定 128 bit（16 byte）**，組成 4×4 byte 矩陣：

```text
state =  [ b0  b4  b8  b12 ]
         [ b1  b5  b9  b13 ]
         [ b2  b6  b10 b14 ]
         [ b3  b7  b11 b15 ]
```

**每一 round 四個操作：**

#### SubBytes — 非線性
每個 byte 經過 8×8 S-box 替換。S-box 在 GF(2⁸) 上做「取乘法逆元 + 仿射變換」。
**目的：** 引入非線性，破壞差分 / 線性攻擊。

具體：對輸入 byte b，先算 `b⁻¹` in GF(2⁸)（0 映到 0），然後做仿射：

```text
b'_i = b_i XOR b_{(i+4) mod 8} XOR b_{(i+5) mod 8} XOR b_{(i+6) mod 8} XOR b_{(i+7) mod 8} XOR c_i
其中 c = 0x63
```

實務上 S-box 是 256-byte lookup table（不用即時計算逆元）。

#### ShiftRows — 行內位移
第 i 列向左 shift i 位。**目的：** 把 byte 之間打散，讓一個 byte 影響擴散。

#### MixColumns — 行間混合
每一行（4 byte）視為 GF(2⁸) 上的多項式，乘以固定多項式 `{03}x³ + {01}x² + {01}x + {02}`。

矩陣形式：

```text
[ s'₀ ]   [ 02 03 01 01 ]   [ s₀ ]
[ s'₁ ] = [ 01 02 03 01 ] · [ s₁ ]
[ s'₂ ]   [ 01 01 02 03 ]   [ s₂ ]
[ s'₃ ]   [ 03 01 01 02 ]   [ s₃ ]
```

（所有乘法在 GF(2⁸) 上，用 §1.6 的 xtime 實作）
**目的：** 高擴散 — 一個 byte 改變後 4 個 byte 全變。

#### AddRoundKey — 拌入 key
每 byte XOR roundkey 對應 byte。

```text
AES-128 流程：
  AddRoundKey (round 0)
  9 × [ SubBytes → ShiftRows → MixColumns → AddRoundKey ]
  最後 round: [ SubBytes → ShiftRows → AddRoundKey ]   （沒有 MixColumns）

AES-192 = 12 round
AES-256 = 14 round
```

**Avalanche effect：** AES 設計目標是 plaintext 改 1 bit → ciphertext 變 ~50% bit。
經 2 round 後，每個 ciphertext byte 都受所有 plaintext byte 影響 (full diffusion)。

### 5.3 Key Schedule

AES 從 master key 衍生出 (N_r + 1) × 128 bit roundkeys。
AES-128 衍生過程使用 SubBytes、Rcon、循環左移。

**AES-256 反而有過 key schedule 弱點：** 相關 key 攻擊在 9-round AES-256 簡化版可被破，但對 14-round 完整版**仍然不可實作**。實務上 AES-256 仍是安全的。

### 5.4 為什麼 AES 撐了 25 年沒倒

- 設計簡潔，公開審查徹底（NIST 全球公開競賽選出）
- SPN 結構 → 抗差分 / 線性攻擊
- 沒有可疑常數（每個常數都有公開推導）
- 廣泛硬體加速（Intel AES-NI 從 2010 年起內建）
- 25 年來最佳攻擊仍是 brute force

### 5.5 Modes of Operation — block cipher 怎麼用

Block cipher 只能加密「**一個 block**」。資料超過 16 byte 就需要 mode。

#### ECB (Electronic Codebook) — 永遠不要用

```text
C_i = E_K(P_i)
```

**致命缺陷：** 一樣的 P_i 永遠產同一個 C_i → 暴露資料模式。
看那張「Linux Tux 用 ECB 加密還是看得出輪廓」的圖，就是這個原因。

#### CBC (Cipher Block Chaining)

```text
C_i = E_K(P_i XOR C_{i-1})
C_0 = E_K(P_0 XOR IV)
```

**好處：** 同 plaintext → 不同 ciphertext（因為 chain）
**陷阱：**
- IV 必須隨機（不能 predictable，BEAST attack）
- padding 必填（PKCS#7） → padding oracle attack 風險
- 不能 parallel（每塊依賴前塊）

#### CTR (Counter Mode)

```text
C_i = P_i XOR E_K(nonce ∥ counter_i)
```

把 block cipher 變成 stream cipher。
**好處：** parallel、random access、不用 padding
**陷阱：** nonce + counter 一定不能重複用 → 重複 = 兩 ciphertext XOR 得 plaintext XOR（OTP 重用災難）

#### GCM (Galois Counter Mode) — AEAD

GCM = CTR（加密）+ GMAC（驗完整）。
**這是現代預設選擇。** 細節在 §7。

#### XTS — 磁碟加密專用

LUKS / dm-crypt / BitLocker 用 XTS-AES。設計成對「sector-based random-access write」友善，每個 sector 用獨立 tweak。

#### Format-Preserving Encryption (FPE) — PCI 場景

NIST FF1 / FF3-1 把信用卡號（16 位數字）加密後**仍是 16 位數字** → 不破壞既有 schema 與資料庫長度限制。
用在金融 / 支付場景的 tokenization。

#### 不要用的 mode：OFB、CFB（已過時，沒比 CTR 好但更複雜）

### 5.6 為什麼 ECB 那張企鵝圖

```text
原圖（Tux）：       ECB 加密：           CBC / CTR 加密：
  ┌────────┐         ┌────────┐          ┌────────┐
  │ 企鵝臉  │   →    │ 仍像企鵝 │   vs   │ 純雜訊  │
  │ 大色塊  │         │ 大色塊  │          │        │
  └────────┘         └────────┘          └────────┘
```

直覺：圖像「大色塊」對應「同樣 16-byte 區段」→ ECB 把它們映射到同樣 ciphertext → 形狀就洩漏了。

---

### 🎯 §5 自測

1. AES SubBytes 為什麼是「非線性」的關鍵？拿掉它會發生什麼？
2. 為什麼 CBC 的 IV 需要「不可預測」而 CTR 的 nonce 只需要「不重複」？
3. AES-128 的 round 數 (10)、AES-256 的 round 數 (14)，差距由什麼決定？
4. XTS 與 GCM 為什麼用在不同場景？哪個適合磁碟、哪個適合網路？
5. 信用卡 PCI tokenization 為什麼不直接用 AES-GCM 而要用 FF1？

---

<a id="stream-cipher"></a>

## 6. Stream cipher

Stream cipher = 「用 key 產一條長 keystream，和 plaintext XOR 即加密」。
邏輯上是 OTP 的「實用近似」 — 把短 key 變長 keystream。

### 6.1 RC4 — 為什麼被淘汰

RC4 簡單、快，曾經是 SSL 與 WEP 的主力。
但**初始 keystream 有 bias**（前面幾百 byte 不均勻），加上其他統計弱點，2015 年正式被 IETF 禁止用於 TLS。
WEP 用 RC4 + IV reuse → WEP 整個被破。

**教訓：** stream cipher 對「key / nonce reuse」極度敏感。

### 6.2 ChaCha20 — 現代主力

DJB 設計，2008 年。WireGuard、QUIC、TLS 1.3 都支援。
為什麼大家愛它：
- 純軟體實作快（不依賴 AES-NI 也很快）→ 行動裝置 / IoT 友善
- 結構簡單清晰
- 抗 timing attack（沒有 table lookup）

**ChaCha20 內部結構：**

```text
4×4 word matrix（每 word 32 bit，共 512 bit state）：

[ "expa" "nd 3" "2-by" "te k" ]   ← constant
[ key0   key1   key2   key3   ]   ← 256-bit key 前半
[ key4   key5   key6   key7   ]   ← 256-bit key 後半
[ counter nonce0 nonce1 nonce2 ] ← counter + 96-bit nonce
```

**Quarter Round** 是核心操作：

```text
QR(a, b, c, d):
  a += b; d ^= a; d <<<= 16
  c += d; b ^= c; b <<<= 12
  a += b; d ^= a; d <<<= 8
  c += d; b ^= c; b <<<= 7
```

每 round 對 column / diagonal 各做一次 QR。
20 round（10 column + 10 diagonal）後，state 變 keystream block。

只用 +、XOR、shift — 沒有乘法、沒有 S-box、沒有 table lookup。
這就是它在 ARM / 行動裝置上比 AES 快的原因。

### 6.3 與 Poly1305 配對成 AEAD

ChaCha20-Poly1305 是 TLS 1.3 必選 cipher。詳見 §7。

---

### 🎯 §6 自測

1. ChaCha20 為什麼「軟體實作快」是它的核心競爭力？
2. 為什麼 stream cipher 一旦 nonce reuse 比 block cipher CBC 更致命？
3. WireGuard 選 ChaCha20-Poly1305 而非 AES-GCM，可能的考量是什麼？

---

<a id="aead"></a>

## 7. AEAD：authenticated encryption 的構造

### 7.1 為什麼要 AEAD

純加密只保證「機密性」(confidentiality)，但不保證「完整性」(integrity) 與「真實性」(authenticity)。

不驗完整性會發生什麼？
- **Bit-flipping attack**：CTR 模式下，攻擊者翻一個 ciphertext bit → 對應 plaintext bit 也翻。
- **Padding oracle**：CBC 不驗 MAC 時，server 回 "padding 錯誤" 的 timing 差 → 漸進解出 plaintext（POODLE、Lucky13）。

**AEAD（Authenticated Encryption with Associated Data）一次做完三件事：**
- Encrypt plaintext → ciphertext
- Authenticate ciphertext → tag
- Authenticate associated data（不加密但要驗，例如 header）→ 也綁進 tag

API 長這樣：

```text
encrypt(key, nonce, AD, plaintext) → ciphertext ∥ tag
decrypt(key, nonce, AD, ciphertext ∥ tag) → plaintext or REJECT
```

### 7.2 構造模式：Encrypt-then-MAC (EtM)

```text
ciphertext = Enc_K1(plaintext)
tag = MAC_K2(ciphertext ∥ AD)
```

EtM 被證明在「IND-CCA」安全（後面 §15 會講），是 generic 安全的構造。
**MAC-then-Encrypt (MtE)** 與 **Encrypt-and-MAC (E&M)** 都有過漏洞紀錄（SSL 用 MtE 留下 padding oracle 漏洞）。

### 7.3 AES-GCM — CTR + GHASH

```text
CTR 部分：
  C_i = P_i XOR AES_K(IV ∥ counter_i)

GHASH 部分（GF(2¹²⁸) 上的多項式 hash）：
  H = AES_K(0¹²⁸)
  GHASH(AD, C) = ((AD_1 · H + AD_2) · H + ... ) · H + ... · H

tag = GHASH(AD, C) XOR AES_K(IV ∥ 0)
```

**特性：**
- CTR 部分可平行
- GHASH 也可平行（PCLMULQDQ 指令加速）
- 在 Intel AES-NI + PCLMUL 下極快
- **致命陷阱**：nonce 重用 = 災難。
  - 同 key 同 nonce → keystream 重複（broken）
  - 更糟：兩個 ciphertext + 同 nonce → 可解 GHASH 的 H → forge 任意訊息
- nonce 預設 96 bit，但「random nonce」遇到大量訊息會生日碰撞（在 ~2^48 訊息後）
  - 解法：**Deterministic nonce**（counter）或用 **AES-GCM-SIV**（nonce-misuse-resistant）

### 7.4 ChaCha20-Poly1305

```text
keystream = ChaCha20(key, nonce, counter)
ciphertext = plaintext XOR keystream

Poly1305:
  r, s = ChaCha20_block(key, nonce, counter=0) 切兩半
  Poly1305 在 prime field GF(2¹³⁰ - 5) 上做多項式 evaluation
  tag = (Σ block_i · r^i) mod p + s
```

**特點：**
- ChaCha20 + Poly1305 都是純軟體高速
- Poly1305 也是 nonce-sensitive（同 nonce + 同 key → forge）
- TLS 1.3 / WireGuard / QUIC 都把它列為必選

### 7.5 AES-GCM-SIV — 修「nonce misuse」災難

SIV (Synthetic IV) mode 從 plaintext + AD 算出 IV，所以即使 nonce 重複，只要 plaintext 不同 IV 仍不同。
**權衡：** 雙倍 pass plaintext（先算 SIV、再加密），慢一些；但對「nonce 管理難」的場景（多 instance 並發）非常重要。

> RFC 8452 標準化。AWS Encryption SDK、Google Tink 都支援。

### 7.6 Key Commitment — 2022 後的新關切

傳統 AEAD 沒承諾「key 唯一」 — 攻擊者可能構造一段 ciphertext，**用兩把不同 key 解出兩個不同合法 plaintext**。
這在 Facebook attachment「同一個訊息對不同人顯示不同內容」攻擊裡被實際利用。
解法：UtC (Universal-to-Committing)、CTX 等「key committing」AEAD 構造。

---

### 🎯 §7 自測

1. 為什麼 GCM 的 nonce reuse 比 CTR 的 nonce reuse 後果更嚴重？
2. AES-GCM-SIV 雙倍 pass 換來什麼安全屬性？
3. Encrypt-then-MAC 為什麼比 MAC-then-Encrypt 安全？舉一個 MtE 的真實漏洞。
4. Key commitment 為什麼是「2022 後才被廣泛關注」？

---

<a id="mac"></a>

## 8. MAC 的理論

### 8.1 安全定義：EUF-CMA

**Existential Unforgeability under Chosen Message Attack：**
攻擊者即使能對任意訊息 query 你的 MAC（chosen message），他仍**無法**對任何「沒 query 過」的訊息產出合法 tag。

這是 MAC 的標準安全目標。HMAC、Poly1305、GMAC 都在這定義下被證明安全（在合理假設下）。

### 8.2 HMAC 構造

直接的 `H(key ∥ message)` 對 Merkle-Damgård hash 不安全（length extension）。
HMAC 解掉這問題：

```text
HMAC(K, M) = H( (K' XOR opad) ∥ H( (K' XOR ipad) ∥ M ) )

opad = 0x5C 重複, ipad = 0x36 重複, K' = padded key
```

**直覺：** 兩層 hash，外層 hash 把內層輸出再壓一次 → length extension 無法穿透外層。

**為什麼選 0x5C / 0x36？** 兩者 XOR = 0x6A（半多半少 bit）→ 確保 inner / outer 用的「實質 key」差異最大。

### 8.3 Poly1305 — 一次性 MAC

Poly1305 本身設計成「one-time MAC」：同一個 `r, s` 對只能用一次。
所以每次配 ChaCha20 都會 re-derive 新的 r, s（用不同 nonce）。

### 8.4 GMAC — GCM 的 MAC 部分

GMAC = GHASH + 一層 AES 加密 mask。
GMAC 對「key + nonce 重用」極度敏感（同 §7.3）。

### 8.5 CBC-MAC 與 KMAC

- **CBC-MAC：** 用 CBC 模式加密但只保留最後一個 block 當 tag。**只對「固定長度」訊息安全**；變長度有 length extension 風險。CMAC（OMAC）修了這問題。
- **KMAC：** SHA-3 家族的原生 MAC，直接吸收 key + message，不需要 HMAC 兩層 hack。

### 8.6 工程啟示

- 自己寫 MAC = 99% 會錯（length extension、timing leak、key reuse）
- 永遠 `hmac.compare_digest()` 而不是 `==`（timing attack）
- key 至少 128 bit，最好 256 bit

---

### 🎯 §8 自測

1. 為什麼 HMAC 的 inner / outer 必須用「不同」padding？
2. CBC-MAC 對變長度訊息為什麼不安全？
3. `if hmac1 == hmac2:` 為什麼是漏洞？

---

# Part III — 公鑰密碼學

<a id="pkc-math"></a>

## 9. 公鑰密碼學的數學基礎

### 9.1 RSA：完整數學

**設定：**
1. 選兩個大質數 `p, q`（各 1024 bit 起跳，現代建議 1536 / 2048 bit）
2. `n = p · q`
3. `φ(n) = (p-1)(q-1)`
4. 選 `e` 與 `φ(n)` 互質（常用 65537 = 2¹⁶ + 1）
5. 算 `d = e⁻¹ mod φ(n)`
6. 公鑰 = `(n, e)`，私鑰 = `(n, d)` 或 `(p, q, d)`

**加密 / 解密：**
- 加密：`c = m^e mod n`
- 解密：`m = c^d mod n`

**為什麼解得回來？**
因為 `c^d = m^(ed) mod n`，而 `ed ≡ 1 mod φ(n)`，由 Euler 定理 `m^(ed) ≡ m mod n`。

**簽章：** 私鑰簽 = `s = H(m)^d mod n`，公鑰驗 = `H(m) =? s^e mod n`。

**為什麼 e = 65537？**
- 它是 Fermat 質數 `F_4 = 2^16 + 1`，binary 是 `10000000000000001` → 只有 17 個 bit，其中 2 個 1
- 公鑰運算 `m^e` 只要 16 次 squaring + 1 次 multiplication → 快
- 比 e=3 安全（小指數攻擊不可行）

### 9.2 CRT 解密加速（為什麼私鑰存 p, q 不只是 d）

RSA 解密 `c^d mod n` 用平方乘法要 ~2048 次 mod n 乘法。
**用 CRT 可以加速 4×：**

```text
d_p = d mod (p-1)
d_q = d mod (q-1)
q_inv = q⁻¹ mod p

解密 c:
  m_p = c^d_p mod p
  m_q = c^d_q mod q
  h = q_inv · (m_p - m_q) mod p
  m = m_q + h · q
```

兩次小指數的 modexp（mod p, mod q）比一次大 modexp 快得多。
這就是為什麼 OpenSSL 把 priv key 存成 `(n, e, d, p, q, d_p, d_q, q_inv)` 而不只是 `(n, d)`。

**Trade-off：** 速度換來 fault-injection 風險。攻擊者讓 m_p 或 m_q 算錯 → 從錯誤輸出反推 p, q（Bleichenbacher 1996）。
**防禦：** 算完用公鑰驗一次（multiplicative blinding 或 result verification）。

### 9.3 Textbook RSA 不安全 — 為什麼要 OAEP / PSS

Textbook RSA `c = m^e` 有多個致命問題：
1. **確定性** → 同訊息同 c → 字典攻擊
2. **可乘性 (homomorphism)**：`(m₁ · m₂)^e = m₁^e · m₂^e` → chosen ciphertext attack
3. **小 e 攻擊**：若 e=3、m 很小，可能 `m^3 < n` → 直接開立方根

**OAEP (Optimal Asymmetric Encryption Padding)：**

```text
seed = random
maskedDB = (m ∥ padding) XOR MGF(seed)
maskedSeed = seed XOR MGF(maskedDB)
ciphertext = RSA_encrypt( maskedSeed ∥ maskedDB )
```

讓 RSA 的輸入隨機化 + 結構化 → 抗 chosen ciphertext。

**PSS (Probabilistic Signature Scheme)：** 簽章版本的隨機化 padding。比舊的 PKCS#1 v1.5 安全。

**所以**：用 RSA 一定要寫清楚是 `RSA-OAEP` 還是 `RSA-PSS`，不要寫 `RSA`。

### 9.4 Diffie-Hellman 密鑰交換

```text
公開：質數 p、生成元 g
Alice 選秘密 a，發送 A = g^a mod p
Bob   選秘密 b，發送 B = g^b mod p
共享 = A^b = B^a = g^(ab) mod p
```

竊聽者看到 `A, B` 但要算 `g^ab` 需要解 DLOG，被認為是 hard。

**現代 DH 參數：**
- `p` 至少 2048 bit（NIST 已淡出 1024-bit DH，被 Logjam 攻擊重創）
- 用 RFC 7919 標準化的 prime（叫 FFDHE） — 不要自己選 prime

**Small subgroup attack：**
若 g 的階含小因子，攻擊者把 A 替換成小階元素 → 把對方拉進小子群 → 用 brute force 算 secret。
**防禦：** 用 safe prime（p = 2q+1，q 也是質數）或標準曲線。

### 9.5 ECC：把 DH 搬到橢圓曲線

```text
公開：曲線 E、基點 G、群階 n
Alice 選秘密 a，發送 A = aG
Bob   選秘密 b，發送 B = bG
共享 = aB = bA = abG
```

需要解 ECDLP（給 A、G 求 a）。
**256-bit ECC 相當於 3072-bit RSA / DH**。

### 9.6 Curve25519 vs P-256 — 詳細對比

| 面向 | Curve25519 | P-256 (secp256r1) |
|---|---|---|
| 曲線方程 | `y² = x³ + 486662x² + x` (Montgomery) | 一般 Weierstrass |
| 體 | GF(2²⁵⁵ − 19) | GF(NIST_P256) |
| 設計者 | DJB（公開） | NIST（部分常數來源不透明） |
| 實作複雜度 | 簡單，幾乎不可能寫錯 | 高，常 timing leak |
| Point at infinity 處理 | 不需要 | 需要 |
| 標準 | RFC 7748 | FIPS 186-4 |
| 適合場景 | 新建系統、行動 / IoT | FIPS / 政府 / 已有 X.509 PKI |

**選擇邏輯：**
- 新系統首選 Curve25519 / Ed25519
- 必須 FIPS 140-2 合規 → P-256
- 不要自己實作曲線運算，用 `libsodium` / `cryptography`（Python）

### 9.7 Point Compression 與 Twist Attack

EC 公鑰是 `(x, y)`，但給定 x，y 只有兩個可能值（互為負）。
所以**壓縮表示** = `x ∥ sign_bit(y)`，省一半空間。
TLS / X.509 的 EC 公鑰都用 compressed form。

**Twist attack：** 攻擊者送一個「不在曲線上」的點，引你做運算 → 落到 twist curve（弱曲線）洩漏私鑰。
Curve25519 用 Montgomery ladder 天然抗 twist；P-256 必須先驗證點在曲線上。

---

### 🎯 §9 自測

1. 為什麼 RSA 私鑰存 (p, q) 而不只是 (n, d) 能加速 4×？
2. Textbook RSA 的「homomorphic 性質」為什麼是漏洞？舉一個 chosen ciphertext 攻擊。
3. 對 RSA 為什麼選 e=65537 而不是 e=3 或 e=2^17+1？
4. Small subgroup attack 怎麼避免？

---

<a id="signatures"></a>

## 10. 數位簽章理論

### 10.1 安全定義：EUF-CMA（簽章版）

和 MAC 一樣的概念：攻擊者能 query 你對任意 message 簽，但他**不能對任何 query 過的 message 產合法簽章**。

更強版本：**SUF-CMA (Strong Unforgeability)** — 連對同一個已簽 message 產出「不同的合法簽章」都不行。
EdDSA 滿足 SUF-CMA；ECDSA 只滿足 EUF-CMA（簽章 (r, s) 與 (r, -s mod n) 都合法 → malleability）。

### 10.2 RSA-PSS 詳解

RSA-PSS = RSA + PSS padding。
PSS 用一個 mask generation function (MGF)、random salt、hash → 確保即使對同訊息簽兩次也產生不同簽章 → 抗 forgery。

```text
sign(m):
  H = hash(m)
  salt = random()
  M' = padding ∥ H ∥ salt
  H' = hash(M')
  PS = padding
  DB = PS ∥ 0x01 ∥ salt
  maskedDB = DB XOR MGF(H')
  EM = maskedDB ∥ H' ∥ 0xbc
  signature = EM^d mod n
```

複雜但可證安全。**現代簽章 RSA 一律用 PSS，不要用 v1.5。**

### 10.3 ECDSA — 為什麼 nonce 是命門

```text
sign(m, priv key d):
  z = hash(m) 取前 N bits
  k = random in [1, n-1]      ← 致命的 k
  R = kG
  r = R.x mod n
  s = k⁻¹ (z + r·d) mod n
  signature = (r, s)
```

**Nonce 重用 = 死刑：**

若兩次用同 `k` 簽兩個不同 message m₁, m₂：

```text
s₁ = k⁻¹(z₁ + rd)
s₂ = k⁻¹(z₂ + rd)
→ s₁ - s₂ = k⁻¹(z₁ - z₂)
→ k = (z₁ - z₂) / (s₁ - s₂) mod n
→ d = (s₁·k - z₁) / r
```

私鑰直接洩漏。**真實案例：**
- Sony PlayStation 3 (2010)：firmware 簽章用固定 k → ECDSA private key 被反推
- Bitcoin 早期錢包：低品質 RNG → 多次同 k → 比特幣被偷
- Java SecureRandom on Android (2013)：bug 導致同 k → BTC 錢包被掏

**解法：RFC 6979 deterministic nonce**
`k = HMAC(d, hash(m) ∥ counter)` — k 從 priv key 和 message 推導，不依賴 RNG。

### 10.4 EdDSA / Ed25519 — 從設計就避開 RSA / ECDSA 的坑

Ed25519 設計亮點：

1. **Deterministic by design**：
   `r = SHA-512(prefix ∥ message) mod n`，prefix 從 priv key 派生
   → 沒有 RNG，沒有 nonce 重用風險

2. **無分支運算**：實作對所有輸入走相同路徑 → 抗 timing attack

3. **Curve25519 + Edwards 形式**：點加法公式對所有點通用（無 special case）

4. **小 signature**：64 byte（vs ECDSA P-256 約 71 byte）

5. **快**：簽 / 驗都比 ECDSA 快

**為什麼後量子時代它仍會被換掉？** ECDLP 在量子電腦下可被 Shor 算法破。
但在 quantum 普及前（推測 15-20+ 年），Ed25519 仍是主力。

### 10.5 Schnorr Signature 與 Taproot

Schnorr signature 數學上比 ECDSA 簡單也安全（可在 GGM 下證明 EUF-CMA），但因為過去專利原因（已於 2008 過期），ECDSA 反而先廣泛採用。

```text
sign(m, sk = x):
  k = random or HMAC-derived
  R = kG
  e = H(R ∥ pk ∥ m)
  s = k + e · x  mod n
  signature = (R, s)

verify(m, pk, (R, s)):
  e = H(R ∥ pk ∥ m)
  check sG =? R + e · pk
```

**為什麼比 ECDSA 好？**
- 更乾淨的安全性證明
- **支援 signature aggregation**：n 個簽 (m_i, σ_i) 可合併成單一 σ_agg → 大幅省空間
- 沒有 ECDSA 的 malleability 問題

**Bitcoin Taproot (BIP-340)** 在 2021 年部署 Schnorr signature，原因之一就是 aggregation 省空間。

> Schnorr identification（互動式 ZK proof）的細節搬到 §17 zero-knowledge，因為它是 ZK 的入門範例。

### 10.6 BLS Signature 與 Pairing 入門

BLS（Boneh-Lynn-Shacham, 2001）建在 **pairing-friendly elliptic curve** 上。

**Pairing** = 雙線性映射 `e: G₁ × G₂ → G_T`，滿足：

```text
e(aP, bQ) = e(P, Q)^(ab)
```

**BLS 簽章流程：**

```text
sign(m, sk = x):
  σ = x · H(m)   （H: msg → G₁ 是 hash-to-curve）

verify(m, pk = xG₂, σ):
  e(σ, G₂) =? e(H(m), pk)
```

**最大優勢 — Aggregation：**

n 個簽 (pk_i, σ_i) 對「不同訊息 m_i」可合併：

```text
σ_agg = Σ σ_i
verify: ∏ e(H(m_i), pk_i) =? e(σ_agg, G₂)
```

→ 一個 verify 驗 n 個簽章。

**真實用途：**
- **Ethereum 2.0 (Beacon Chain)**：每 slot 上萬 validator 簽 → 用 BLS aggregation 壓成一個
- **Drand（隨機 beacon）**：threshold BLS 產生公開可驗證的隨機
- **Chia**：用 BLS 取代 ECDSA

**代價：** Pairing 計算比 ECC scalar mult 慢 ~50×，且簽章驗證需要 2+ pairing 運算。

---

### 🎯 §10 自測

1. 同一 `k` 簽兩個不同 message，私鑰怎麼被反推？寫出代數步驟。
2. 為什麼 Ed25519 不需要 RFC 6979？
3. Schnorr signature aggregation 在 Bitcoin Taproot 解決什麼問題？
4. BLS 的 pairing 為什麼讓 aggregation 如此漂亮？

---

<a id="kex"></a>

## 11. 密鑰交換、KEM 與 Noise 框架

### 11.1 Key Encapsulation Mechanism (KEM)

KEM 比「key exchange」更抽象：

```text
KEM.Encaps(pk) → (ciphertext, K)
KEM.Decaps(sk, ciphertext) → K
```

Sender 拿 receiver public key、產一個 random K + ciphertext，送 ciphertext 給 receiver；receiver 用 priv key 解出同樣 K。

**為什麼後量子時代愛 KEM？** 因為 lattice-based 算法天然是 KEM 形式（NIST 選 ML-KEM 而不是 lattice DH）。

### 11.2 Authenticated Key Exchange (AKE)

純 DH 沒有「對方是誰」的保證 → MITM。
AKE 把身分驗證綁進 KEX：

- **Static-Static DH**：兩方都用長期 key（缺 forward secrecy）
- **Ephemeral-Static DH (ES-DH)**：一方臨時、一方長期（有部分 FS）
- **Ephemeral-Ephemeral + sign**：兩方都臨時，再用 long-term key 簽（TLS 1.3 走這條）

### 11.3 Triple DH（Signal 協定）

Signal 的 X3DH 用四把 key 做三次 DH 組成共享：

```text
Alice keys: identity IK_A, ephemeral EK_A
Bob keys:   identity IK_B, signed prekey SPK_B, one-time prekey OPK_B

DH1 = DH(IK_A, SPK_B)
DH2 = DH(EK_A, IK_B)
DH3 = DH(EK_A, SPK_B)
DH4 = DH(EK_A, OPK_B)   # 若有
SK  = KDF(DH1 ∥ DH2 ∥ DH3 ∥ DH4)
```

**達成：** 雙方身分驗證 + forward secrecy + 「Bob 不在線也能初始化」。
**用在：** Signal、WhatsApp、Facebook Messenger Secret Conversations。

### 11.4 Pre-Shared Key (PSK) 模式

如果雙方已經有共享 secret（如初次配對），可以省掉公鑰運算。
TLS 1.3 的 session resumption 用 PSK；WireGuard 可以選用 PSK 提升後量子過渡安全。

### 11.5 Noise Protocol Framework — 現代協定的「pattern 語言」

**動機：** TLS、IPsec、SSH 都各自實作 AKE，每個都自有歷史包袱與設計缺陷。
**Noise** 由 Trevor Perrin（Signal 共同作者）2016 年提出，把 AKE 抽象成「pattern」。

**Pattern 字串：** 用兩個小寫字母表示「兩方 key 配置」：

| 字母 | 意義 |
|---|---|
| **N** | 沒有 static key（只用 ephemeral） |
| **K** | 有 static key，**對方事先知道**（Known） |
| **X** | 有 static key，握手中傳給對方（transmitted） |
| **I** | 有 static key，**第一個訊息就傳**（immediate） |

組合成 `<initiator><responder>`：

| Pattern | initiator 用什麼 | responder 用什麼 | 例子 |
|---|---|---|---|
| **NN** | 只 ephemeral | 只 ephemeral | 匿名雙方，無身分（如雜訊通道） |
| **NK** | 只 ephemeral | static known | 連已知 server（類似 TLS 連已知 cert） |
| **KK** | static known | static known | 雙方已知對方身分（IoT pairing） |
| **IK** | static immediate | static known | initiator 1-msg 揭身分 |
| **XX** | static transmitted | static transmitted | 雙方握手中互換身分（最通用） |

**真實系統：**
- **WireGuard**：用 **Noise_IK_25519_ChaChaPoly_BLAKE2s** — initiator 一開始就用 responder 已知 pubkey
- **WhatsApp**：register 用 XX，日常用 IK
- **Lightning Network**：用 Noise_XK

**為什麼工程師要知道 Noise？**
- 新建 P2P 協定不要自己拼，直接套 Noise pattern
- 看 WireGuard 等系統的 spec 時，「Noise_IK_25519_ChaChaPoly_BLAKE2s」一行就告訴你完整的 KEX 設計
- 比 TLS 簡單 100×（沒有 cert chain、沒有 cipher negotiation）

### 11.6 KEM Combiner — Hybrid 怎麼合

後量子過渡期，工業界用「同時跑古典 + 後量子」兩個 KEM：

```text
ss_classical = X25519(sk_c, pk_c)
ss_pq        = ML-KEM.Decaps(sk_pq, ct_pq)

hybrid_secret = KDF(ss_classical ∥ ss_pq ∥ transcript)
```

**安全保證（IND-CCA combiner theorem）：** 只要兩 KEM 之一安全，整體 hybrid secret 即安全。

**為什麼這設計重要？**
- ML-KEM 是新算法（2024 標準化），安全餘裕較淺
- X25519 已 well-vetted
- 兩個都安全 = 確定安全；ML-KEM 哪天被破，仍有 X25519 撐
- 2025 Cloudflare、Google、AWS TLS 預設啟用 X25519MLKEM768

---

### 🎯 §11 自測

1. 純 Ephemeral-Ephemeral DH 為什麼仍需要身分驗證？沒驗會發生什麼？
2. WireGuard 為什麼選 IK pattern 而不是 XX？想想 trade-off。
3. KEM combiner 的「only one needs to be secure」是什麼意思？舉一個 X25519 + ML-KEM 情境。
4. Noise pattern KK 比 XX 省什麼？犧牲了什麼？

---

<a id="kdf"></a>

## 12. KDF 與 password hashing 的設計

### 12.1 兩種 KDF：要分清楚

| 類型 | 目的 | 代表 |
|---|---|---|
| **KBKDF (Key-based KDF)** | 從高熵 secret 衍生多支 key | HKDF |
| **PBKDF (Password-based KDF)** | 從低熵密碼衍生 key（要慢！） | PBKDF2 / scrypt / Argon2 |

**搞混了會出大事：**
- 拿 HKDF 處理密碼 → 太快，攻擊者 GPU 一秒幾億猜
- 拿 Argon2 衍生 session key → 不必要的 CPU / 記憶體成本

### 12.2 HKDF — Extract + Expand

RFC 5869，TLS 1.3 / Signal / Noise protocol 的核心 KDF。

```text
Extract:   PRK = HMAC(salt, IKM)         # 把任何形狀的 input 「正規化」成均勻 PRK
Expand:    OKM = HMAC(PRK, info ∥ counter)  # 從 PRK 拉任意長度輸出
```

**精髓：** 兩段式 — Extract「壓平 entropy」、Expand「延伸長度」。

**典型用法：**

```text
master_secret → HKDF.Extract(salt=randoms, master)
                   → HKDF.Expand("client write key") → key_c
                   → HKDF.Expand("server write key") → key_s
                   → HKDF.Expand("handshake key")    → ...
```

### 12.3 PBKDF2 — 簡單但太快

```text
DK = PBKDF2(P, S, c, dkLen)
   = T_1 ∥ T_2 ∥ ... ∥ T_l

T_i = F(P, S, c, i)
F(P, S, c, i):
  U_1 = HMAC(P, S ∥ INT_BE(i))
  U_2 = HMAC(P, U_1)
  ...
  U_c = HMAC(P, U_{c-1})
  return U_1 XOR U_2 XOR ... XOR U_c
```

`c` 是 iteration 次數，目的是讓計算「慢」。
**問題：** PBKDF2 對 GPU / ASIC 友善 — 攻擊者用便宜硬體大規模並行猜密碼。
NIST 還在用（FIPS 合規），但**不再是新系統首選**。

### 12.4 scrypt — 加入記憶體硬度

```text
scrypt(P, S, N, r, p, dkLen):
  1. PBKDF2-SHA256 derive initial big buffer
  2. 用 ROMix（隨機讀寫大 buffer）反覆操作
  3. 最後再 PBKDF2 壓成輸出
```

**設計目標：** 強制使用大量記憶體 → GPU / ASIC 的記憶體頻寬變成瓶頸 → 攻擊成本暴增。

### 12.5 Argon2 — 當前最佳選擇

2015 年 Password Hashing Competition 冠軍。
三個變體：
- **Argon2d**：data-dependent memory access（最快、抗 GPU 但有 timing leak）
- **Argon2i**：data-independent（抗 side channel）
- **Argon2id**：混合 — **首選**

參數：
- `m`：記憶體（KiB）
- `t`：iteration 次數
- `p`：parallelism

**建議：** 至少 64 MiB 記憶體 + 3 iteration（OWASP 2023）。

### 12.6 為什麼 password hashing 一定要「慢 + 大」

**Threat model：**
- 你的 DB 被偷了
- 攻擊者要用 hash 反查密碼
- 攻擊者用大量 GPU / ASIC / cloud 並行

只有「慢」還不夠（ASIC 一秒可做 trillion 次 SHA256）；要加「記憶體硬度」讓硬體變大、變貴。
這就是 Argon2id 對比 SHA256 的根本優勢。

---

### 🎯 §12 自測

1. HKDF Extract 與 Expand 為什麼要拆兩段？合在一起會有什麼問題？
2. 為什麼 PBKDF2 在 GPU 上「太友善」？
3. Argon2 的「記憶體硬度」具體攻擊成本怎麼算？

---

<a id="tls-internal"></a>

## 13. TLS 1.3 的內部 key schedule

應用篇講過握手流程；這節是「key 從哪裡來、為什麼這樣設計」。

### 13.1 Key 派生樹（RFC 8446 §7.1 完整版）

```text
                          0
                          |
                          v
            PSK ->  HKDF-Extract = Early Secret
                          |
                          +-----> Derive-Secret(., "ext binder" | "res binder", "")
                          |                      = binder_key
                          +-----> Derive-Secret(., "c e traffic", ClientHello)
                          |                      = client_early_traffic_secret
                          +-----> Derive-Secret(., "e exp master", ClientHello)
                          |                      = early_exporter_master_secret
                          v
                   Derive-Secret(., "derived", "")
                          |
                          v
   (EC)DHE -> HKDF-Extract = Handshake Secret
                          |
                          +-----> Derive-Secret(., "c hs traffic",
                          |                     ClientHello...ServerHello)
                          |                     = client_handshake_traffic_secret
                          +-----> Derive-Secret(., "s hs traffic",
                          |                     ClientHello...ServerHello)
                          |                     = server_handshake_traffic_secret
                          v
                   Derive-Secret(., "derived", "")
                          |
                          v
            0 -> HKDF-Extract = Master Secret
                          |
                          +-----> Derive-Secret(., "c ap traffic",
                          |                     ClientHello...server Finished)
                          |                     = client_application_traffic_secret_0
                          +-----> Derive-Secret(., "s ap traffic", ...)
                          |                     = server_application_traffic_secret_0
                          +-----> Derive-Secret(., "exp master", ...)
                                                = exporter_master_secret
```

### 13.2 每根 secret 為什麼存在

| Secret | 為什麼存在 |
|---|---|
| **Early Secret** | 給 PSK / 0-RTT 模式用；只有 PSK 才有實質輸入，否則用 0 |
| **binder_key** | 證明 client 真的擁有 PSK；防止攻擊者拿 ticket 偽裝 |
| **client_early_traffic_secret** | 加密 0-RTT 資料（client 在收到 server response 前就送的資料） |
| **early_exporter_master_secret** | 給上層 protocol（如 EAP-TLS）派生 0-RTT 用 key |
| **Handshake Secret** | 從 ECDHE shared secret 派生；保護握手剩餘訊息 |
| **client/server handshake_traffic_secret** | 加密 EncryptedExtensions、Certificate、Finished 等 |
| **Master Secret** | 握手完成後的最終根 |
| **application_traffic_secret_0** | 加密真正資料的起始 key（之後可以 rotate） |
| **exporter_master_secret** | 給上層 protocol 拿來派生「TLS 通道綁定」用 key |

### 13.3 Key Separation 原則

注意每一步都用**不同 label 字串**做 HKDF.Expand：`"c hs traffic"`、`"s hs traffic"`、`"c ap traffic"`...

**為什麼？** Domain separation — 同樣的 input keying material，配不同 label 派出**統計獨立**的 key。
否則「同 key 不同用途」是經典反 pattern（同 RSA key 既加密又簽章會出事）。

### 13.4 Transcript Hash — 防降級的關鍵

每個 Derive-Secret 呼叫的 `Messages` 參數是「**目前為止所有握手訊息的 hash**」。

```text
Derive-Secret(Secret, Label, Messages) = 
    HKDF-Expand-Label(Secret, Label, Transcript-Hash(Messages), Hash.length)
```

**為什麼這設計？**
- 攻擊者若改任一握手訊息 → transcript hash 變 → 雙方派出的 secret 不同 → Finished 訊息驗不過 → 連線斷
- 這就是 TLS 1.3 為什麼**強制防降級**：cipher suite 協商、版本協商都被綁進 transcript

### 13.5 0-RTT 的 Trade-off

```text
[Client]                          [Server]
ClientHello + 0-RTT data →
                              ← ServerHello + ...
```

Client 不等 server 回應就送資料 → 省一個 RTT，網頁載入快。

**但代價：**
- **沒有 forward secrecy 對 0-RTT 資料**（用 PSK 派生，PSK 被破則 0-RTT 資料可解）
- **可 replay**：攻擊者把 0-RTT 訊息錄下來重送，server 無法分辨

**應用層的責任：** 只在「idempotent」操作（如 GET）用 0-RTT，**絕對不要對 POST / 付款 用**。

### 13.6 Post-Handshake Key Update

`application_traffic_secret_0` 不是永久的。可以隨時：

```text
new_secret = HKDF-Expand-Label(current_secret, "traffic upd", "", Hash.length)
```

→ 在不重新握手的情況下 rotate key。
用於長連線（HTTP/2、gRPC streaming）防止「同 key 加密過多資料」（GCM 在 2^48 訊息後 nonce 碰撞）。

### 13.7 Exporter Master Secret 的妙用

`exporter_master_secret` 是 RFC 8446 給上層的「掛勾」：

```text
TLS-Exporter(label, context, length) = 
    HKDF-Expand-Label(exporter_master_secret, label, context, length)
```

任何上層 protocol 可以拿這個函數派生自己用的 key，**綁定到當前 TLS session**。

**用例：**
- EAP-TLS：用 exporter 派生 EAP key
- WebRTC DTLS-SRTP：派生 SRTP master key
- QUIC：派生 packet protection key（QUIC v1 用了類似機制）

這就是「channel binding」的密碼學基礎 — 上層證明它與 TLS session 是同一條通道。

---

### 🎯 §13 自測

1. 為什麼 Handshake Secret 派生時 ECDHE shared secret 進來，但 Master Secret 派生時又進來個 0？
2. 若有人把 cipher suite 協商從 AEAD 改成 CBC，TLS 1.3 怎麼擋？
3. 為什麼 0-RTT 不適合付款 API？
4. Post-handshake key update 解決什麼具體問題？(提示：§7.3 GCM nonce 生日)
5. 如果應用層想做「channel binding」（防 MITM 中繼），用 TLS 的哪個 secret？

---

# Part IV — 安全分析

<a id="attacks"></a>

## 14. 攻擊類型 taxonomy

理論安全 ≠ 實作安全。**95% 真實漏洞來自實作而非演算法**。

### 14.1 Side Channel — 從「執行行為」洩漏

| 子類 | 怎麼洩漏 |
|---|---|
| **Timing** | 計算時間長短依賴秘密（branch、table lookup、變長迴圈） |
| **Cache** | CPU cache hit/miss 反映 access pattern（FLUSH+RELOAD、PRIME+PROBE） |
| **Power** | 量電流變化讀 priv key（DPA — Differential Power Analysis） |
| **EM** | 電磁輻射反映運算 |
| **Acoustic** | 聽 CPU 線圈嘯叫（真的） |
| **Speculative execution** | Spectre / Meltdown 那一票 |

**著名案例：**
- OpenSSL ECDSA timing attack（多次）
- Intel SGX 被 cache attack 破
- Lucky13、CRIME、BREACH 都是 timing / compression side channel

**防禦：**
- Constant-time code（無 branch on secret、無 secret-dependent table）
- `mem_cmp` 用 `crypto.timingSafeEqual` / `hmac.compare_digest`
- 不要寫 `if password == stored:` 直接 ==

### 14.2 Fault Injection — 主動破壞硬體

故意讓晶片運算錯：超頻、低電壓、laser、雷射 glitch、電磁 glitch。
RSA-CRT signing：故意讓其中一個 CRT 分支算錯 → 從錯誤輸出反推 priv key。
**防禦：** 雙重計算 / 自驗、shielded chip。

**RowHammer：** 反覆讀某個 DRAM row 引發鄰近 row 翻 bit，可用來改 kernel page、提權。

### 14.3 Padding Oracle Attack

對 CBC 模式：server 解密後如 padding 不對會回不同錯誤 / timing → 攻擊者可逐 byte 解出 plaintext（POODLE、Lucky13）。

**防禦：**
- 用 AEAD（GCM / ChaCha20-Poly1305）
- 必須用 CBC 時，error 訊息常數時間統一

### 14.4 Length Extension Attack

如 §4.2 — 攻擊者用 `H(M)` 算 `H(M ∥ pad ∥ M')`。
**防禦：** 用 HMAC、不要用 SHA-256 直接拼 MAC、改用 SHA-3 / BLAKE2/3。

### 14.5 Replay Attack

攻擊者錄下合法請求，事後 replay。
**防禦：** Nonce、timestamp、序號、TLS session 內含序號。

**TLS 1.3 的 0-RTT 容易 replay** — 應用層必須要不可重複（idempotent）才能用 0-RTT。

### 14.6 Downgrade Attack

攻擊者強迫對方用較弱 cipher / protocol（DROWN、FREAK、Logjam、POODLE）。
**防禦：**
- TLS 1.3 transcript hash 把握手所有訊息綁進簽章 → 改動會破壞 verify
- HSTS（HTTP Strict-Transport-Security）
- 完全停用舊 protocol

### 14.7 Cross-Protocol Attack

把對 A protocol 的 oracle 用在 B protocol（DROWN：用 SSLv2 server 破 TLS）。
**防禦：** 絕對不在同一 key 上跑兩個 protocol。

### 14.8 Implementation Bugs — 看歷史學乖

| 案例 | 教訓 |
|---|---|
| Heartbleed (CVE-2014-0160) | 沒做 bounds check → 讀 64KB OpenSSL memory |
| Debian OpenSSL RNG (2008) | 改 code 把 entropy 削掉 → SSH key 全可預測 |
| Apple goto fail (2014) | 重複 `goto fail` → TLS cert 不被驗 |
| KRACK (2017) | WPA2 nonce reuse on retransmission |
| ROBOT (2017) | RSA-PKCS#1 v1.5 Bleichenbacher 復活 |
| Curve25519 PoC implementation bugs | 即使是好曲線，實作錯也炸 |
| Log4Shell (2021) | 不是密碼學但點出 supply chain 風險 |
| xz-utils backdoor (2024) | 上游 maintainer 社工 + 隱蔽後門 |

**啟示：** 一切信任**經過時間考驗的 library** — libsodium、Tink、Ring、cryptography（Python）、Bouncy Castle、Go crypto。

---

### 🎯 §14 自測

1. 為什麼 `strcmp(provided_token, real_token)` 是 timing 漏洞？怎麼修？
2. Padding oracle 的「逐 byte 解」是怎麼做到的？大致原理。
3. TLS 1.3 對降級攻擊的根本防護是什麼？(提示：§13.4)
4. xz-utils 後門教我們「不只是 code 問題，還是什麼問題」？

---

<a id="provable"></a>

## 15. Provable Security 完整版

不是要你會證明，是要你**看懂 paper / RFC 寫的 security claim**，**並且能評估它的強度**。

### 15.1 Security Game — 對手與規則

定義「攻擊者贏」的條件，然後證明「贏的機率 ≤ negligible」。

```text
Game IND-CPA:
  Setup: challenger 跑 KeyGen → (pk, sk)，把 pk 給 attacker A
  Query phase: A 對 oracle 問任意 encrypt query
  Challenge: A 提交 m_0, m_1（等長）；challenger 翻硬幣 b，回 ciphertext = Enc(m_b)
  Guess: A 輸出 b'
  Win: b' = b

攻擊者優勢 Adv = |Pr[b' = b] - 1/2|

如果 Adv ≤ negligible（在 security parameter 下），則 scheme IND-CPA 安全
```

### 15.2 Reduction — 把難題綁起來

「如果我能破 A，那我能破 B」。
若 B 被認為 hard，則 A 也是 hard。

例：證明「ECDSA 簽章 EUF-CMA」 → 把它 reduce 到「ECDLP hard」。

### 15.3 主要安全等級

| 名稱 | 全名 | 對應對手能力 |
|---|---|---|
| **IND-CPA** | Indistinguishability under Chosen Plaintext | 攻擊者能 query encrypt |
| **IND-CCA1** | + non-adaptive Chosen Ciphertext | + 預先 query decrypt（challenge 前） |
| **IND-CCA2** | + adaptive CCA | + 持續 query decrypt（除了 challenge 自己） |
| **EUF-CMA** | Existential Unforgeability under CMA | 對 MAC / 簽章 |
| **SUF-CMA** | Strong Unforgeability under CMA | 比 EUF 更嚴：不能修改已有合法 signature |
| **INT-CTXT** | Integrity of Ciphertext | 攻擊者無法偽造任何被接受的 ciphertext |
| **AE / AEAD** | Authenticated Encryption | IND-CPA + INT-CTXT |

**現代 AEAD 的目標：IND-CCA2 + INT-CTXT**。

### 15.4 走一次完整 reduction：ElGamal IND-CPA ⇐ DDH

這是密碼學教科書最經典的 walkthrough。看完你會對「reduction 是什麼」有具體感覺。

#### Setup

**ElGamal 加密：**
```text
Setup: 公開 cyclic group G, generator g, order q
KeyGen: sk = x ← random in [1, q-1]
        pk = h = g^x
Encrypt(pk, m):
  r ← random
  return (c_1, c_2) = (g^r, h^r · m) = (g^r, g^(xr) · m)
Decrypt(sk, (c_1, c_2)):
  return c_2 / c_1^x = (g^(xr) · m) / g^(xr) = m
```

**DDH 假設（Decisional Diffie-Hellman）：** 給 `(g, g^a, g^b, Z)`，區分 `Z = g^(ab)` 還是 `Z = random` 是 hard。

#### Reduction goal

假設攻擊者 A 能以優勢 ε 破 ElGamal IND-CPA。
**我們建構 B**，用 A 當 sub-routine，以**同樣優勢 ε** 破 DDH。

#### 構造 B

```text
B 收到 DDH challenge (g, X, Y, Z)，要判斷 Z 是 g^(ab) 還是 random

Step 1: B 設定 ElGamal 公鑰 pk = X（B 不知道對應 sk = a）
Step 2: B 把 pk 給 A，啟動 A 的 IND-CPA game
Step 3: A 提交挑戰 (m_0, m_1)
Step 4: B 隨機選 b ∈ {0, 1}，回 ciphertext = (Y, Z · m_b)
Step 5: A 輸出猜測 b'
Step 6: B 輸出「DDH」若 b' = b，否則輸出「random」
```

#### 分析

**情況 1：Z = g^(ab) 真的是 DH value**

則 `ciphertext = (Y, Z · m_b) = (g^b, g^(ab) · m_b) = (g^b, X^b · m_b) = (g^b, pk^b · m_b)`

→ 這是 ElGamal 對 m_b 在隨機 r=b 下的**合法加密**！

→ A 看到的是真實 IND-CPA game

→ A 以優勢 ε 猜對 b'，即 `Pr[b' = b | Z = DH] = 1/2 + ε`

**情況 2：Z 是均勻 random**

則 `Z · m_b` 也是均勻 random（因為 Z 是均勻、與 m_b 獨立）

→ Ciphertext **完全不洩漏 m_b 資訊**（資訊論意義）

→ A 任何優勢都不可能 > 0，即 `Pr[b' = b | Z = random] = 1/2`

#### 合起來看 B 的優勢

```text
Adv_B(DDH) = | Pr[B 輸出"DDH" | Z=DH] - Pr[B 輸出"DDH" | Z=random] |
           = | Pr[b'=b | Z=DH] - Pr[b'=b | Z=random] |
           = | (1/2 + ε) - 1/2 |
           = ε
```

→ **B 解 DDH 的優勢 = A 破 ElGamal IND-CPA 的優勢**

#### 結論

```text
若 DDH hard（沒有 ε-優勢算法），則 ElGamal IND-CPA 安全（沒有 ε-優勢攻擊）。
```

**這就是 reduction。** 把一個新 scheme 的安全性「reduce」到一個已被廣泛相信的 hard problem。
讀 paper 的核心技能是判斷：
- 它 reduce 到哪個 problem？
- 那個 problem 真的 hard 嗎？
- Reduction 緊不緊（loss factor）？

### 15.5 Tightness — Reduction 的「品質」

不是所有 reduction 都一樣好。

**Tight reduction：** Adv_B ≈ Adv_A（兩者差距是小常數）
**Loose reduction：** Adv_B ≈ Adv_A / q（q 是 attacker 的 query 數，可能 2^60）

**為什麼影響你？**

假設你想要 128-bit 安全，scheme reduce 到 problem P：
- Tight reduction → P 給 128-bit 安全足夠
- Loose reduction（loss = 2^60）→ **需要 P 給 188-bit 安全**才夠

→ Loose reduction 必須用更大的 key。

**著名例子：**
- Schnorr signature 在 ROM 下證明是 loose（Forking Lemma），參數要選大
- BLS 在 GGM + ROM 下是 tight

讀 paper 看到 "tight" 或 "tightness loss factor" 字眼 → 它在講這件事。

### 15.6 Concrete Security — 把「漸近」翻成「我該幾 bit」

教科書常說「在 negligible 機率以外安全」，但工程師需要具體數字。

**Concrete security 推導範例（HMAC）：**

```text
HMAC EUF-CMA Adv ≤ q² / 2^n + q · Adv_PRF(H)

其中：
  n = hash output bits
  q = attacker 的 query 數
```

對 HMAC-SHA-256（n=256），假設 attacker 做 2^64 query：
```text
Adv ≤ 2^128 / 2^256 + 2^64 · Adv_PRF(SHA-256)
    ≈ 2^-128 + 2^64 · ε
```

只要 SHA-256 是 reasonable PRF，HMAC-SHA-256 給接近 128-bit 安全。

**KS / FIPS 給的「至少 N bit」是這個計算的結論，不是 hash output bits。**

### 15.7 Multi-Instance Security

證明「一個 user 安全」≠「一百萬 user 都安全」。

**舉例：** 對 password hashing，攻擊者拿到 N 個 hash，破第一個的成本是 1/N（任一個破即可）→ 安全等級降 log₂ N bit。

**真實案例：** Adobe 2013 洩漏 1.5 億組 unsalted SHA-1 password hash → 大量帳號被破。

→ **加 salt** 把每個 user 變獨立 instance，攻擊不可平均攤。

### 15.8 模型對比：ROM vs Standard vs GGM

| 模型 | 假設 | 用在 |
|---|---|---|
| **Standard Model** | 只用標準假設（DDH、LWE） | 學術理想 |
| **Random Oracle Model (ROM)** | 把 hash 視為真 random oracle | 大多數實用 scheme（PSS、OAEP、Schnorr、Ed25519、Fiat-Shamir） |
| **Generic Group Model (GGM)** | 攻擊者只能透過「群運算 oracle」操作群元素 | BLS、Schnorr 的緊證明 |
| **Ideal Cipher Model (ICM)** | 把 block cipher 視為真隨機 permutation | AES-based KDF / MAC |

**ROM 不是真實世界，但被廣泛接受。** 有些算法只在 ROM 下可證、在 standard model 下不可證 — 這不代表不安全，只代表「我們相信 hash function 夠像 random oracle」。

**警告：** 有少數人造算法在 ROM 下安全、在任何具體 hash 下都不安全（uninstantiable scheme）。
但實務上沒人用這種；標準算法都是「ROM 下證明 + 在實際 hash 下相信」的組合。

---

### 🎯 §15 自測

1. 走一次 ElGamal → DDH reduction 的關鍵直覺是什麼？為什麼「Z 是 random 時 ciphertext 不洩漏」？
2. 一個 reduction 的 tightness loss = 2^40，要達 128-bit 安全，底層 hard problem 要幾 bit？
3. 為什麼 password hashing 必須 salt？用 multi-instance 概念解釋。
4. ROM 與真實世界差在哪？為什麼工業界仍接受 ROM 證明？
5. INT-CTXT 和 EUF-CMA 在概念上有什麼差別？

---

# Part V — 進階主題

<a id="pqc"></a>

## 16. Post-Quantum Cryptography

### 16.1 為什麼 quantum 威脅 RSA / ECC

Shor's algorithm（1994）：量子電腦能在多項式時間內：
- 對 N 做質因數分解
- 求離散對數

→ **RSA、DH、ECDH、ECDSA、Ed25519 全部破。**

Grover's algorithm（1996）：量子電腦能在 √N 時間內搜尋。
→ 對稱密碼學「強度減半」：AES-128 變 64-bit 等級（太弱），**AES-256 變 128-bit 等級（仍夠）**。
→ Hash 也類似：SHA-256 抗碰撞變 2^64（不夠強），SHA-512 變 2^128（仍夠）。

**結論：**
- 對稱 / hash：**加倍 key / output 長度即可**（AES-128 → AES-256，SHA-256 → SHA-384/512）
- 非對稱：**整套換掉**

### 16.2 Shor's algorithm 直覺

Shor 把「因數分解」轉成「找週期函數的週期」。
量子電腦用 Quantum Fourier Transform 能高效找週期 → 因此能解 factoring / DLOG。

需要約 **多少量子位元？** 對 RSA-2048：需要約 4000-20000 個 fault-tolerant logical qubits。
2026 年現實：IBM 約 1000+ physical qubits，但 logical qubit 數仍很少。**沒人知道何時 RSA-2048 真的會被破** — 估計 10-25 年。

### 16.3 NIST 後量子標準化結果（2024）

| 算法 | 類型 | 用途 | 標準名稱 |
|---|---|---|---|
| **Kyber** | Module-LWE | KEM | **ML-KEM** (FIPS 203) |
| **Dilithium** | Module-LWE / Module-SIS | 簽章 | **ML-DSA** (FIPS 204) |
| **SPHINCS+** | Hash-based | 簽章（保底） | **SLH-DSA** (FIPS 205) |
| **Falcon** | NTRU lattice | 簽章 | **FN-DSA**（將標準化） |

### 16.4 Lattice 是什麼

```text
Lattice L = {a₁v₁ + a₂v₂ + ... + aₙvₙ : aᵢ ∈ Z}
          = 由 basis 向量「整數線性組合」生成的點陣
```

**Hard problems：**
- **SVP (Shortest Vector Problem)**：找 lattice 中最短非零向量
- **CVP (Closest Vector Problem)**：給點 t，找 lattice 中離 t 最近的點
- **LWE (Learning With Errors)**：解線性方程組 `A·s + e = b`，e 是小 noise
- **SIS (Short Integer Solution)**：給 A，找非零短整數 z 使 `Az ≡ 0 mod q`

LWE 形式：
```text
A 是 m × n 矩陣
s 是 n 維秘密向量
e 是 m 維小 error
給你 (A, b)，求 s → hard
```

直覺：解一般 `As = b` 用 Gaussian elimination 就行（多項式時間）。
但加上小 noise `e` 後，error 被線性運算「放大」到完全破壞，反而 hard。

### 16.5 LWE 家族地圖

| 變體 | Sample 形式 | 用在 | 取捨 |
|---|---|---|---|
| **Plain LWE** | A 是 m×n 隨機矩陣 | 學術 | key 大、慢 |
| **Ring-LWE** | A 從 `R_q = Z_q[x]/(x^n+1)` 抽 | NewHope (deprecated) | 結構性 → 快、key 小，但攻擊面更窄 |
| **Module-LWE** | LWE over module（介於 plain 與 ring 之間） | **Kyber, Dilithium** | 平衡 — NIST 選這個 |
| **SIS / Module-SIS** | 找短解 | Dilithium 簽章 | LWE 的「對偶」問題 |

**為什麼 NIST 選 Module-LWE 而非 Ring-LWE？**
- Ring-LWE 的代數結構太多 → 擔心未來被找出特殊攻擊
- Module-LWE 用「rank > 1 module」減少結構性 → 更保守
- 性能上 Module-LWE 仍快得多於 plain LWE

### 16.6 ML-KEM (Kyber) 簡化版

```text
Setup: 公開矩陣 A（從 seed 派生）
Keygen:
  s, e ← small Gaussian noise
  t = As + e         （public key = (A, t)）
  priv key = s

Encaps（用 pk 加密 random K）：
  r, e_1, e_2 ← small noise
  u = Aᵀr + e_1
  v = tᵀr + e_2 + encode(K)
  ciphertext = (u, v)

Decaps（用 sk 解 K）：
  K' = decode( v - sᵀu )
       ≈ decode( tᵀr + e_2 + encode(K) - sᵀ(Aᵀr + e_1) )
       ≈ decode( encode(K) + 小noise )
       = K
```

**為什麼安全？** 攻擊者看到 `(A, t = As + e)`，要求 s → LWE hard。
**參數：** Kyber-768 達 NIST Level 3（約 AES-192 等級）。

### 16.7 Fujisaki-Okamoto Transform — CPA → CCA 的關鍵

ML-KEM 的「naive 版」只 IND-CPA 安全（攻擊者不能 query decryption）。
但實務上 KEM 需要 IND-CCA2（攻擊者可以 query）。

**FO Transform 把 CPA-PKE 變 CCA-KEM：**

```text
Original CPA-PKE: Enc(pk, m; r) → ct

FO-transformed KEM:
  Encaps(pk):
    m ← random
    r = H(m, pk)              # derandomize
    ct = PKE.Enc(pk, m; r)
    K = G(m)                  # key = hash of m
    return (ct, K)

  Decaps(sk, ct):
    m' = PKE.Dec(sk, ct)
    r' = H(m', pk)
    ct' = PKE.Enc(pk, m'; r') # re-encrypt
    if ct == ct': return G(m')
    else:         return G(s, ct)  # implicit reject 用 secret
```

**關鍵技巧：**
1. **Derandomize**：把 random r 從 m 派生 → encryption 變確定性
2. **Re-encrypt 驗證**：解密後重新加密，比對 ciphertext → 防 chosen-ciphertext
3. **Implicit reject**：失敗回 random key（用 secret 派生）→ 不洩漏「成功/失敗」signal

**Kyber 的 ML-KEM 就是用 FO 包 CPA-PKE 而來的 CCA-KEM。**

### 16.8 SPHINCS+ — Hash-based 簽章

完全只用 hash function。安全只依賴「hash collision resistance」。
代價：簽章很大（8-50 KB），但**最保守、最不依賴新假設**。
用途：作為 lattice-based 簽章的「保底」option。

### 16.9 過渡策略：Hybrid

不要直接從 RSA / ECDH 跳到 ML-KEM。
業界做法：**Hybrid KEM** — 同時跑 X25519 + ML-KEM，把兩邊 shared secret 合併（細節見 §11.6）。

**Cloudflare、Google、AWS** 從 2023-2025 陸續在 TLS 1.3 啟用 X25519+ML-KEM hybrid（標準叫 X25519MLKEM768）。

### 16.10 對 SRE 的實務意義

- 不用慌；現在不會被破
- 但 **"harvest now, decrypt later"** 威脅真實（攻擊者今天抓封包，未來解開）
- 高敏感 / 長保密期資料應該開始評估 hybrid
- 新建系統選 cipher 時，留 hybrid 路徑（很多 library 已支援）
- 簽章相對沒急 — 簽完當下驗證就好，量子來臨前重簽即可

---

### 🎯 §16 自測

1. 為什麼 AES-256 在量子時代仍夠，但 RSA-2048 完全要換？
2. Module-LWE 比 Ring-LWE 在 NIST 眼中的優勢是什麼？
3. FO transform 的「re-encrypt 驗證」為什麼能擋 CCA 攻擊？
4. "Harvest now, decrypt later" 對哪些資料才是真實威脅？
5. 為什麼簽章的後量子過渡沒有 KEM 那麼急？

---

<a id="zk"></a>

## 17. Zero-Knowledge Proofs 完整入門

### 17.1 三個性質

ZK proof 系統要滿足：

| 性質 | 意義 |
|---|---|
| **Completeness** | 真陳述 → Verifier 一定接受 |
| **Soundness** | 假陳述 → Verifier 幾乎一定拒絕（除可忽略概率） |
| **Zero-Knowledge** | Verifier 除了「陳述為真」外**學不到任何資訊** |

ZK 是 Goldwasser / Micali / Rackoff 1985 年提出，2012 年 Goldwasser 拿圖靈獎。

### 17.2 Schnorr Identification — 經典 3-message ZK

證明「我知道 priv key x 使 P = xG」而不洩漏 x：

```text
1. Prover 選 r，發 R = rG       (commitment)
2. Verifier 送 challenge c (random)
3. Prover 發 s = r + cx           (response)
4. Verifier 驗 sG =? R + cP
```

**為什麼 verify 成立？**
```text
sG = (r + cx)G = rG + cxG = R + cP ✓
```

### 17.3 為什麼 Schnorr 是「真 ZK」？Simulator Argument

**ZK 的形式定義：** 存在一個 **simulator** S，**不知道 witness x**，但能產出與真實互動「不可區分」的 transcript。

**Schnorr 的 simulator：**

```text
S（沒有 x）想偽造一個 transcript (R, c, s)：

Step 1: 隨機選 s ← random
Step 2: 隨機選 c ← random
Step 3: 反算 R = sG - cP

→ Transcript (R, c, s) 滿足 sG = R + cP ✓
```

**和真實互動的分布相同嗎？**

| 元素 | 真實 | Simulator |
|---|---|---|
| R | rG，r 均勻 → R 均勻 | sG - cP，s 均勻 → R 均勻 |
| c | Verifier 給 random | S 直接 random |
| s | r + cx | random |

**所有三個元素的聯合分布完全一樣** → Verifier 看到的 transcript 沒任何「需要知道 x」的訊息。
→ **ZK 證畢。**

**這個 simulator argument 是所有 ZK 證明的核心 paradigm。**

### 17.4 Fiat-Shamir Transform — 把互動式變非互動式

Schnorr identification 需要 Verifier 出 challenge。
把 challenge 改成 `c = H(R ∥ public_data)` → Prover 自己算 challenge → 變成**非互動式簽章**！

```text
sign(m, sk = x):
  r ← random
  R = rG
  c = H(R ∥ pk ∥ m)
  s = r + cx
  return (R, s)

verify(m, pk, (R, s)):
  c = H(R ∥ pk ∥ m)
  check sG =? R + c·pk
```

→ **這就是 Schnorr signature**（§10.5）。
→ Fiat-Shamir 是 ZK-SNARK、ECDSA、EdDSA 的共同基礎技術。

**安全代價：** Fiat-Shamir 在 ROM 下安全（hash 視為 random oracle）；標準模型下沒有對應證明。

### 17.5 從 Schnorr 到 SNARK — 通用計算的 ZK

Schnorr 只證「知道某個 discrete log」。**SNARK** 證「我跑某個任意計算得到某個結果」。

**Pipeline：**

```text
Step 1: 你的計算 (e.g., "我有 x 使 SHA256(x) = h")
   ↓
Step 2: 表達成 arithmetic circuit（只用 + 和 ×）
   ↓
Step 3: 轉成 R1CS (Rank-1 Constraint System)
   每個 constraint: (a·w) × (b·w) = c·w
   其中 w 是 witness vector
   ↓
Step 4: 轉成 QAP (Quadratic Arithmetic Program)
   把 R1CS 用多項式編碼
   ↓
Step 5: 用 polynomial commitment + Fiat-Shamir 產 SNARK
```

### 17.6 R1CS 範例

要證「我知道 x 使 x³ + x + 5 = 35」（答案是 x = 3）：

```text
分解計算：
  v1 = x · x     (= x²)
  v2 = v1 · x    (= x³)
  v3 = v2 + x    (= x³ + x)
  out = v3 + 5

R1CS（每行是一個 constraint A_i·w · B_i·w = C_i·w，w 是 witness）：
  w = (1, out, x, v1, v2, v3)
  
  (x)(x) = v1     →  A = [0,0,1,0,0,0], B = [0,0,1,0,0,0], C = [0,0,0,1,0,0]
  (v1)(x) = v2    →  A = [0,0,0,1,0,0], B = [0,0,1,0,0,0], C = [0,0,0,0,1,0]
  (v2 + x)(1) = v3 → A = [0,0,1,0,1,0], B = [1,0,0,0,0,0], C = [0,0,0,0,0,1]
  (v3 + 5)(1) = out → A = [5,0,0,0,0,1], B = [1,0,0,0,0,0], C = [0,1,0,0,0,0]
```

Prover 知道 w，要證「所有 constraint 都滿足」**而不揭露 w 的私密部分**。

### 17.7 QAP 與 Polynomial Commitment

R1CS 的 m 條 constraint 可用 Lagrange interpolation 編碼成三個多項式 `A(x), B(x), C(x)`。
Witness w 滿足所有 constraint ⟺ 存在多項式 H 使：

```text
A(x) · B(x) − C(x) = H(x) · Z(x)
```

其中 Z(x) 是「在所有 constraint 點等於 0」的多項式。

**Polynomial Commitment：** 把多項式「承諾」到一個短 commitment（單個 group element），日後在任一點 z 開啟並證明值正確。

**KZG (Kate) Commitment 直覺：**

```text
Setup（一次性 trusted）：產 [1, s, s², ..., s^d] in G_1 + [1, s] in G_2，銷毀 s
Commit(p): C = p(s) in G_1（用 setup 算，不需知道 s）
Open(p, z): proof π = (p(s) - p(z)) / (s - z) in G_1
Verify(C, z, y, π): e(C - [y]_1, [1]_2) =? e(π, [s - z]_2)
```

驗證用 pairing 一次完成。
**這個 trusted setup 銷毀 s 是「ceremony」做的事 — Zcash 著名的 "Powers of Tau" 就是這個。**

### 17.8 ZK 系統地圖

| 系統 | Trusted Setup | Proof 大小 | Verify 時間 | 量子安全？ | 特色 |
|---|---|---|---|---|---|
| **Groth16** (2016) | per-circuit | ~200 bytes | ~ms | ❌ | 最小 proof，但每改 circuit 要新 setup |
| **PLONK** (2019) | universal | ~500 bytes | ~ms | ❌ | 一次 setup 適用所有 circuit |
| **Halo2** (2020) | **無** | ~10 KB | ~10ms | ❌ | recursion friendly |
| **STARK** (2018) | **無** | ~100 KB | ~100ms | ✅ | 用 hash，量子安全 |
| **Bulletproofs** | 無 | O(log n) | O(n) | ❌ | 適合 range proof |

### 17.9 Trusted Setup Ceremony — 為什麼是個事件

Groth16 / KZG 都需要「一次性 trusted setup」，產出「toxic waste」（如 KZG 的 s）必須銷毀。
**如果 s 沒銷毀**：擁有者可以偽造任意證明。

**Powers of Tau：** Zcash 2018 辦的多人 ceremony，~90 人輪流貢獻隨機性，每人銷毀自己那份 → 只要**任一人**真的銷毀，整體 setup 就安全。
**Ethereum KZG Ceremony 2023：** ~14 萬人參加，目前最大規模。

### 17.10 工程實用情境

- **Zcash / Tornado Cash**：隱私交易（不揭露金額、來源）
- **zk-rollup**（StarkNet、zkSync、Scroll）：壓縮 L1 交易成本
- **Cloudflare Privacy Pass**：證明「我不是 bot」而不揭身分
- **Identity proof**（年齡驗證不揭身分證號）
- **Apple PCC (Private Cloud Compute, 2024)**：用 ZK 證明 server 跑的是 attested 版本

### 17.11 對 SRE 的需要度

- 知道 ZK 是什麼、能解什麼問題 ✓
- 能讀懂 ZK 系統地圖（§17.8 表）✓
- 不必自己實作 SNARK
- 不必當 web3 信徒

---

### 🎯 §17 自測

1. Simulator argument 為什麼能「證明沒洩漏 witness」？直覺講一遍。
2. Fiat-Shamir 在 ROM 下安全，這個假設真實世界算合理嗎？
3. R1CS 為什麼能表達「任意計算」？什麼計算不能表達？
4. Groth16 vs STARK，要做以太坊 L2 rollup 你會選哪個？理由？
5. Powers of Tau ceremony 為什麼讓 ~14 萬人參加？只要 1 人銷毀就夠了嗎？

---

<a id="ads"></a>

## 18. Authenticated Data Structures（新章）

**Authenticated Data Structures (ADS)** = 資料結構 + 密碼學承諾 → 「外包儲存但仍能驗證」。
**這是 Git、Bitcoin、IPFS、Certificate Transparency、Sigstore Rekor 的共同底層。**
應用篇 §6 講過 Cosign + Rekor，這章補上「Rekor 的 Merkle tree 到底怎麼運作」。

### 18.1 Merkle Tree — 一張圖看懂

```text
                root = H(H(0,1), H(2,3))
                       /                \
                H(0,1)                  H(2,3)
                /    \                  /    \
            H(d_0)  H(d_1)          H(d_2)  H(d_3)
              |      |                |      |
            data_0  data_1          data_2  data_3
```

每個 leaf 是 data 的 hash；每個 internal node 是「兩個 child hash 接起來再 hash」。
**Root hash 一個 256-bit value 就承諾了所有 leaf 的內容。**

### 18.2 Inclusion Proof — O(log n) 大小

證明 `data_2 ∈ tree`，給：
- `data_2` 本身
- 兄弟路徑：`H(d_3), H(0,1)`

Verifier 重算：
```text
H_3' = H(data_2)
H_{2,3}' = H(H_3' ∥ H(d_3))
root' = H(H(0,1) ∥ H_{2,3}')

check root' == known_root ?
```

**只有 log₂ n 個 hash** → 對 10 億 leaf 的 tree，proof 只要 30 個 hash。

### 18.3 Consistency Proof — Append-Only 證據

CT (Certificate Transparency) 風格的 log 需要證明：
**「舊 root R_n 對應的 n-leaf tree，是新 root R_m 對應的 m-leaf tree 的前綴」**（n < m）。

這保證 log 不能被「改寫歷史」，只能 append。

```text
給 R_n 和 R_m，consistency proof 是 O(log m) 個 hash
讓 verifier 能重建出兩個 root，確認 R_n 是 R_m 的子樹
```

### 18.4 Certificate Transparency (CT)

RFC 6962。**所有 web cert 都進公開 log，任何人可審計。**

**核心元件：**

| 元件 | 角色 |
|---|---|
| **Log** | append-only Merkle tree 儲存所有 cert |
| **STH (Signed Tree Head)** | log 的當前 root 簽名 `{root, size, timestamp}` |
| **SCT (Signed Certificate Timestamp)** | log 對「我會把這 cert 加入 tree」的承諾 |
| **Monitor** | 持續抓 STH、檢查可疑 cert |
| **Auditor** | 拿 inclusion + consistency proof 驗 log 沒作弊 |

**工程意義：**
- 你的 domain 被誤簽 cert → CT log 會出現該 cert → Monitor 抓到 → 你能 detect MITM
- 2018 起 Chrome 強制所有公開 cert 必須在 CT log

### 18.5 Sigstore Rekor — Supply Chain 的 CT

Rekor 是 supply chain 版本的 CT log。每次用 Cosign 簽 image 都會在 Rekor 留紀錄：

```text
Rekor entry:
  - artifact hash (image digest)
  - signature
  - public key / cert
  - timestamp

→ 全部 hash 後成為 Rekor Merkle tree 的一個 leaf
→ 每段時間發布 STH
```

**為什麼這安全？**
- 攻擊者偷簽 image → 必須出現在 Rekor → 全世界看得到
- 沒出現在 Rekor 的簽章不會被 Kyverno policy 接受
- 即使攻擊者控制 Rekor 一段時間，inclusion proof + consistency proof 可審計

**底層實作：Google Trillian** — 通用 verifiable log 引擎。

### 18.6 其他 Merkle 應用

| 系統 | 怎麼用 Merkle |
|---|---|
| **Git** | Commit = Merkle DAG（tree object + parent commits）→ commit hash 承諾整個歷史 |
| **Bitcoin** | 每 block 把交易組成 Merkle tree → block header 只存 root |
| **IPFS** | Merkle DAG of file chunks → content-addressable |
| **ZFS / Btrfs** | Merkle hash tree 驗每個 block 完整性 → 抗 silent corruption |
| **Update Framework (TUF)** | Merkle 化的 metadata 簽章 |
| **DynamoDB Streams** | Merkle tree 提供「我看到哪一段」的 cursor |

### 18.7 Sparse Merkle Tree — 鍵值版本

普通 Merkle tree 是「list」的承諾。**Sparse Merkle Tree (SMT)** 是「map」的承諾：

```text
key → leaf 位置 = H(key) 對應的 path
未存在的 key 對應「全零 leaf」
證明「key 不存在」 = 證明對應 path 是全零
```

**用途：** Ethereum state tree、Trillian、Verkle tree（Ethereum 未來方向）。

### 18.8 工程啟示

- 設計 verifiable log → 不要從零造，用 Trillian / Rekor
- 設計 audit log → Merkle 化能讓 log 不可變
- 看到 "Merkle root" 字眼 → 它就是「全部資料的 hash 指紋」
- log_n inclusion proof 是 distributed system 的「省頻寬」絕招

---

### 🎯 §18 自測

1. Merkle tree 的 inclusion proof 為什麼是 log_n 大小，不是 n？
2. Consistency proof 解決什麼問題？沒有它的 log 為什麼有風險？
3. 為什麼 CT 同時需要 inclusion proof 和 consistency proof？只有一個夠嗎？
4. Sparse Merkle Tree 與普通 Merkle Tree 的差別？
5. 應用篇 Cosign keyless 簽章驗證流程裡，Rekor 扮演哪一步？(提示：應用篇 §6.2)

---

<a id="threshold"></a>

## 19. Threshold Cryptography & Secret Sharing（新章）

**Threshold cryptography** = 把私鑰拆成 n 份，需要 ≥ k 份才能用 / 重建。
這是 Vault unseal、HSM 備份、多人簽章 wallet、Ethereum validator、Drand 隨機 beacon 的共同基礎。

### 19.1 動機 — 單點失效是密碼學的根本問題

```text
單一私鑰 →
  - 持有者背叛
  - 持有者死亡 / 失聯
  - 硬碟壞掉
  - 駭客入侵
  → 全部資產 / 系統失守
```

**Threshold 解法：**
- 「需要 3/5 高管同意才能動公司金庫」
- 「Vault 啟動要 3 個 admin 各拿自己的 key shard」
- 「Ethereum block 要 2/3 validator 簽」

### 19.2 Shamir's Secret Sharing — 數學最美的密碼學構造

Adi Shamir 1979 年提出。**用「多項式插值」實現 (k, n)-threshold。**

#### 構造

要分享 secret `s`：

```text
1. 選一個次數 k-1 的多項式 f(x)，使 f(0) = s
   f(x) = s + a_1·x + a_2·x² + ... + a_{k-1}·x^{k-1}
   (a_1, ..., a_{k-1} 隨機)

2. 給每個 party i：share = (i, f(i))
3. 任 k 個 share 可用 Lagrange interpolation 重建 f(0) = s
4. 任 k-1 個 share 對 s 毫無資訊（資訊論意義）
```

#### Lagrange 重建公式

```text
給 k 個 share (x_1, y_1), ..., (x_k, y_k)：

s = f(0) = Σ_{i=1}^{k} y_i · Π_{j ≠ i} (0 - x_j) / (x_i - x_j)
```

#### 具體例：(2, 3)-threshold

要分享 `s = 1234`：

```text
選多項式 f(x) = 1234 + 5678·x  (隨機 a_1 = 5678)

Share 1 = (1, f(1)) = (1, 6912)
Share 2 = (2, f(2)) = (2, 12590)
Share 3 = (3, f(3)) = (3, 18268)
```

任兩個 share 可重建。例如用 Share 1 + Share 3：

```text
s = 6912 · (0-3)/(1-3) + 18268 · (0-1)/(3-1)
  = 6912 · (3/2) + 18268 · (-1/2)
  = 10368 - 9134
  = 1234 ✓
```

#### 真實工具：HashiCorp Vault Unseal

Vault 啟動時要 unseal：
- 預設 `(3, 5)` Shamir：5 個 admin 各拿一個 share，需 3 個才能解密 master key
- 可調為其他比例（甚至 `(1, 1)` 開發環境用）

**這就是「公司金庫要 3 個高管簽」的密碼學落地。**

### 19.3 Threshold Signatures — 從 Shamir 到「不重建也能簽」

Shamir 的限制：**重建時要把 share 集中**，重建瞬間 secret 暴露在某台機器上。

**Threshold Signature Scheme (TSS)：**
- n 個 party 各持 share
- 簽章時各自算「partial signature」
- 組合 partial signature 得到合法簽章
- **整個過程 secret 永遠不被重建**

#### Threshold BLS — 最漂亮的版本

BLS（§10.6）天然支援 threshold：

```text
每個 party i 持有 sk_i（Shamir share of x）

Sign(m):
  σ_i = sk_i · H(m)                              # partial sig
  
Combine (給 k 個 partial σ_i):
  σ = Σ λ_i(0) · σ_i                              # Lagrange 加權
    = Σ λ_i(0) · sk_i · H(m)
    = (Σ λ_i(0) · sk_i) · H(m)
    = x · H(m)                                    # 等價於用 x 直接簽
```

**Lagrange 在指數上做 → 一氣呵成、不需要互動。**

**真實用途：**
- **Drand**：分散式隨機 beacon，threshold BLS 產可驗證 random
- **Ethereum 2 beacon chain**：每 epoch 驗證 BLS aggregation
- **Filecoin**：sector commitment 用 BLS threshold

#### Threshold ECDSA — 困難的版本

ECDSA 的簽章公式 `s = k⁻¹(z + rd)` 含「除法 + 乘法 + 加法」，不能像 BLS 那樣天然分散。
需要複雜的 **multi-party computation (MPC)** 協定：

- **GG18 / GG20** (Gennaro-Goldfeder)：兩階段 — DKG 產生 share，互動簽章
- **CGGMP21**：改進版，較少 round
- **DKLs**：基於 OT (oblivious transfer)

商業 wallet 用：
- **Fireblocks**、**ZenGo**、**Coinbase MPC**
- AWS / GCP 部分 KMS 內部用 MPC

### 19.4 Distributed Key Generation (DKG)

Shamir 假設「有可信 dealer 產 secret 再分」。
**DKG** 解決「沒有 dealer，n 個人合作產生 threshold key，過程中沒人看過整把 secret」。

**Pedersen DKG（簡化）：**

```text
每個 party i 選自己的多項式 f_i(x)，f_i(0) = s_i

每個 party 把 f_i(j) 傳給 party j（私下）
每個 party 廣播 commit 到 coefficient（用 Pedersen commitment）

最終 share = Σ f_i(j) 對 party j
整體 secret = Σ s_i 沒人知道
```

**真實用途：** Ethereum 2 validator key 產生、Drand 啟動 ceremony、Coinbase MPC custody。

### 19.5 BIP-340 Schnorr Aggregation 與 MuSig

Bitcoin Taproot 引入 Schnorr signature → 支援 **n-of-n aggregation**：

```text
公開 aggregated pubkey: P = P_1 + P_2 + ... + P_n
n 個人合作簽 → 對外看就像一個簽章

優點：
  - 區塊鏈上看不出有幾個人簽（隱私）
  - 簽章大小不變（省 fee）
  - 比 multi-sig script 簡單
```

**MuSig / MuSig2** 是無中介的 n-of-n Schnorr 協定（2 round）。
**FROST** 是 k-of-n threshold Schnorr（更通用）。

### 19.6 工程地圖

| 工具 / 系統 | 用什麼 |
|---|---|
| HashiCorp Vault unseal | Shamir Secret Sharing (3/5 default) |
| AWS CloudHSM 災難備份 | Shamir Secret Sharing |
| Ethereum 2 validator | BLS threshold |
| Drand random beacon | BLS threshold + DKG |
| Bitcoin Taproot | Schnorr aggregation (BIP-340) |
| Fireblocks / ZenGo wallet | Threshold ECDSA (GG / DKLs / CGGMP) |
| Filecoin | BLS threshold + DKG |
| Coinbase Custody | MPC (内部) |
| Tor consensus | Threshold signature |

### 19.7 對 SRE / DevSecOps 的應用

最直接的場景：

1. **Vault unseal 設計**：你的 prod Vault unseal 是 `(1, 1)`（一個 key 一個人）還是 `(3, 5)`（5 個 admin 持 share）？
2. **Disaster recovery**：HSM master key 怎麼備份？單一持有人 vs Shamir 分發
3. **CI/CD 簽章**：是否考慮用 threshold signing 取代「一個 long-lived priv key」
4. **多人 deploy approval**：基於 threshold sig 的部署 gate（比 webhook + JWT 更嚴）

對 portfolio：**Lab — Vault Shamir unseal demo + 災難復原演練** 是面試容易聊的題目。

---

### 🎯 §19 自測

1. Shamir (2, 3) 的 share 1 + share 2 怎麼重建 secret？走一次 Lagrange。
2. 為什麼 Threshold BLS 比 Threshold ECDSA 「漂亮」？
3. DKG 解決 Shamir 的什麼弱點？
4. Bitcoin Taproot 的 Schnorr aggregation 帶來的「隱私」好處是什麼？
5. 用 Threshold 觀點重新看「single private key on a server」這個設計，問題在哪？

---

# Part VI — 工程閱讀指南

<a id="how-to-read"></a>

## 20. 怎麼讀 RFC 和密碼學 paper

讀標準文件是密碼學工程師的核心技能。

### 20.1 RFC 結構

| 章節 | 你要看什麼 |
|---|---|
| Abstract | 一句話定位 |
| 1. Introduction | Motivation、用語 |
| 2-3. Definitions | Notation、Terminology |
| 4-5. Protocol | 主要規格（最長） |
| Security Considerations | **必讀**：threat model、known attacks、deployment caveats |
| IANA Considerations | 註冊新名稱（可略） |
| References | Normative（必須遵守）vs Informative（補充） |

### 20.2 Paper 結構

```text
Abstract → Introduction → Preliminaries（數學基礎） → Construction → Security Proof → Performance → Conclusion
```

工程師可以：
1. 先看 Abstract + Introduction
2. 直接跳到 **Construction** 看算法步驟
3. 看 **Security 段**了解 threat model 與 reduction
4. 跳過 Proof 細節
5. 看 Performance 段判斷實用性

### 20.3 第一份建議讀的 RFC

| RFC | 主題 | 為什麼推 |
|---|---|---|
| 8446 | TLS 1.3 | 必修 |
| 5869 | HKDF | 短、清楚、現代 KDF 設計典範 |
| 7748 | Elliptic Curves (X25519/X448) | 兩頁定義一個現代算法 |
| 8032 | EdDSA | 同上 |
| 6979 | Deterministic ECDSA | 解掉一整類漏洞的 hack |
| 8439 | ChaCha20-Poly1305 | 看清楚 stream cipher + MAC 怎麼組 |
| 8017 | RSA PKCS#1 v2.2（含 OAEP / PSS） | RSA 標準化的歷史傷痕都在裡面 |
| 6962 | Certificate Transparency | 第一份 verifiable log 標準 |
| 9180 | HPKE (Hybrid Public Key Encryption) | 現代 KEM 設計典範 |

讀完這幾份，再去看你工作裡接觸的 RFC，會發現「看得懂了」。

### 20.4 怎麼挑 paper 讀

| 來源 | 質量 |
|---|---|
| IACR ePrint Archive | 大部分密碼學 paper 的預印本 |
| CRYPTO / EUROCRYPT / ASIACRYPT | 三大頂級會議 |
| Real World Crypto (RWC) | 工程友善、不要求數學功力 |
| USENIX Security / CCS / S&P | 系統安全 + 密碼學交叉 |

避開：商業白皮書、區塊鏈專案論文（除非有頂會 backing）、自費 journal。

---

### 🎯 §20 自測

1. 看到 RFC 中 "MUST"、"SHOULD"、"MAY" 各代表什麼？
2. 為什麼 paper 的 Performance section 對工程師可能比 Proof section 重要？
3. ePrint 跟正式發表 paper 的差別是什麼？

---

<a id="closing"></a>

## 21. 結語與進階閱讀

### 21.1 學完這份能講什麼

對應到應用篇 §1 的場景題，現在你可以多回答：

| 應用篇問的 | 理論篇給你的答案 |
|---|---|
| 為什麼 TLS 1.3 比 1.2 安全？ | Forward secrecy 強制 + AEAD-only + transcript hash 防降級 + key schedule 用 HKDF |
| 為什麼 ECDSA nonce 重用會死？ | 兩條方程兩個未知數 → 一行代數解出 priv key |
| 為什麼 K8s Secret 用 base64 不算加密？ | 加密需要 key + 算法；base64 是編碼，誰都能 decode |
| 為什麼 KMS 用 envelope？ | KMS 只處理小 DEK，DEK 再對稱加密大資料，省 API call 與時間 |
| 為什麼 Cosign keyless 能取代 GPG key 管理？ | 短期 cert + 透明日誌（Rekor / Merkle tree）取代「長期 priv key 加 trust」 |
| 為什麼 Argon2id 比 SHA256 適合存密碼？ | 記憶體硬度讓 GPU/ASIC 攻擊成本暴增 |
| 為什麼後量子過渡用 hybrid？ | KEM combiner theorem：只要任一安全就整體安全 |
| Vault unseal 為什麼預設 3/5？ | Shamir secret sharing：避免單點 + 容錯 |

### 21.2 進階書 / 課

| 推薦 | 內容 |
|---|---|
| Real World Cryptography (David Wong) | 工程師密碼學第一本 |
| Cryptography Engineering (Ferguson/Schneier/Kohno) | 偏理論但仍可讀 |
| Serious Cryptography (Aumasson) | 比 Real World Crypto 更深一點 |
| A Graduate Course in Applied Cryptography (Boneh & Shoup, 免費 PDF) | 學術版聖經 |
| Stanford CS255 / CS355 / CS355P (lecture notes 都開放) | 學術課程 |
| Cryptopals Challenges | 最有名的動手課 |
| zkbook (zero-knowledge proofs MOOC) | ZK 系統免費課 |

### 21.3 一句話總結

密碼學的進步是「把不可能變可能、把可能變實用、把實用變安全」的反覆迭代。
你不需要會發明算法，但你應該能在 incident 當下站在那行 `Cipher.getInstance("AES")` 前面，**指出為什麼這樣寫是錯的**。

那就是工程師讀密碼學理論的價值。

---

<a id="glossary"></a>

## Appendix A：詞彙對照表

| 縮寫 / 術語 | 全名 / 中文 | 用在 |
|---|---|---|
| ADS | Authenticated Data Structures | Merkle tree、CT log |
| AEAD | Authenticated Encryption with Associated Data | GCM、Poly1305 |
| AES | Advanced Encryption Standard | 對稱加密標準 |
| AKE | Authenticated Key Exchange | TLS 1.3、Signal |
| ASN.1 | Abstract Syntax Notation One | X.509、PKCS |
| BLS | Boneh-Lynn-Shacham 簽章 | Pairing-based、Ethereum 2、Drand |
| BQP | Bounded-error Quantum Polynomial | 量子複雜度類 |
| CA | Certificate Authority | PKI |
| CMK | Customer Master Key | AWS KMS |
| CRT | Chinese Remainder Theorem / Certificate Revocation Token | 數論定理、CT log |
| CSPRG | Cryptographically Secure PRG | 安全偽隨機 |
| CSR | Certificate Signing Request | cert 簽發流程 |
| CT | Certificate Transparency | RFC 6962 |
| DEK | Data Encryption Key | envelope encryption |
| DH | Diffie-Hellman | 密鑰交換 |
| DKG | Distributed Key Generation | 無 dealer 的 threshold key |
| DLOG | Discrete Logarithm | 數學 hard problem |
| DSA | Digital Signature Algorithm | 簽章 |
| ECC | Elliptic Curve Cryptography | 橢圓曲線密碼學 |
| ECDH | Elliptic Curve Diffie-Hellman | 密鑰交換 |
| ECDLP | Elliptic Curve DLOG Problem | hard problem |
| ECDSA | Elliptic Curve DSA | 簽章 |
| EUF-CMA | Existential Unforgeability under Chosen Message Attack | MAC / Sig 安全定義 |
| FFDHE | Finite-Field DH (RFC 7919) | 標準化 DH 參數 |
| FHE | Fully Homomorphic Encryption | 加密狀態運算 |
| FO | Fujisaki-Okamoto | CPA→CCA transform |
| Forward Secrecy | 前向安全性 | 重要 protocol 性質 |
| FPE | Format-Preserving Encryption | PCI / 金融 |
| GCM | Galois Counter Mode | AES-GCM |
| GF | Galois Field (有限體) | AES、GCM |
| GGM | Generic Group Model | 證明模型 |
| HKDF | HMAC-based KDF | TLS 1.3、Signal |
| HMAC | Hash-based MAC | 常用 MAC |
| HPKE | Hybrid Public Key Encryption (RFC 9180) | 現代 KEM |
| HSM | Hardware Security Module | 硬體 key |
| IND-CPA / CCA | Indistinguishability under CPA / CCA | 安全定義 |
| INT-CTXT | Integrity of Ciphertext | AEAD 安全屬性 |
| JWS / JWE / JWT | JSON Web Sig / Encryption / Token | OIDC |
| KEM | Key Encapsulation Mechanism | 後量子主要形式 |
| KZG | Kate-Zaverucha-Goldberg commitment | PLONK、Ethereum |
| KDF | Key Derivation Function | HKDF、Argon2 |
| LWE | Learning With Errors | lattice-based 基礎 |
| MAC | Message Authentication Code | HMAC、GMAC |
| MGF | Mask Generation Function | OAEP、PSS |
| ML-KEM | Module-Lattice KEM | 後量子 (Kyber) |
| ML-DSA | Module-Lattice DSA | 後量子 (Dilithium) |
| MPC | Multi-Party Computation | Threshold ECDSA、Coinbase Custody |
| OAEP | Optimal Asymmetric Encryption Padding | RSA padding |
| OCSP | Online Certificate Status Protocol | cert 撤銷 |
| OWF | One-Way Function | 理論基石 |
| PBKDF | Password-Based KDF | PBKDF2 / scrypt / Argon2 |
| PKI | Public Key Infrastructure | CA、cert chain |
| PLONK | Universal SNARK | ZK-rollup |
| PoX | Powers of x ceremony (Tau) | Trusted setup |
| PRF | Pseudo-Random Function | block cipher 內部 |
| PRG | Pseudo-Random Generator | RNG |
| PSS | Probabilistic Signature Scheme | RSA signature padding |
| QAP | Quadratic Arithmetic Program | SNARK pipeline |
| R1CS | Rank-1 Constraint System | SNARK pipeline |
| ROM | Random Oracle Model | 證明模型 |
| RSA | Rivest-Shamir-Adleman | 非對稱經典 |
| SCT | Signed Certificate Timestamp | CT log |
| SHA | Secure Hash Algorithm | SHA-2、SHA-3 |
| SIS | Short Integer Solution | Lattice hard problem (Dilithium) |
| SLH-DSA | Stateless Hash-based DSA | 後量子 (SPHINCS+) |
| SMT | Sparse Merkle Tree | 鍵值版本 |
| SPHINCS+ | Hash-based 簽章 | 後量子 |
| STH | Signed Tree Head | CT / Rekor |
| SVP | Shortest Vector Problem | lattice hard problem |
| TSS | Threshold Signature Scheme | MPC wallet |
| XOF | eXtendable Output Function | SHAKE128/256 |
| ZK | Zero-Knowledge | 零知識證明 |

---

<a id="timeline"></a>

## Appendix B：密碼學工程史 timeline（新）

| 年 | 事件 | 為什麼重要 |
|---|---|---|
| 1883 | Kerckhoffs' 原則：「algorithm 公開，安全靠 key」 | 現代密碼學第一原理 |
| 1949 | Shannon 證明 perfect secrecy = OTP | 資訊論密碼學奠基 |
| 1976 | Diffie-Hellman + 新密碼學方向 | 公鑰密碼學誕生 |
| 1977 | RSA | 第一個 trapdoor 函數 |
| 1978 | McEliece (code-based 後量子候選) | 量子安全雛形 |
| 1985 | ECC 提出（Koblitz & Miller 獨立） | 公鑰小型化 |
| 1985 | ZK proof (Goldwasser-Micali-Rackoff) | ZK 起源 |
| 1991 | PGP | 端到端加密進入大眾 |
| 1993 | SHA-0 | NSA 設計（後改 SHA-1） |
| 1994 | Shor's algorithm | 量子威脅 RSA / ECC |
| 1996 | Grover's algorithm | 量子威脅對稱加密 |
| 1998 | EFF DES Cracker 22 小時破 DES | 56-bit 死刑 |
| 1998 | NESSIE / AES competition 開始 | 取代 DES |
| 2000 | Rijndael 選為 AES | 25 年標準 |
| 2001 | AES FIPS 197 | 對稱加密黃金標準 |
| 2004 | SHA-0 碰撞被破 | 警告燈 |
| 2005 | Wang 等發表 SHA-1 碰撞理論 | SHA-1 開始倒數 |
| 2008 | Bitcoin 白皮書 | 普及 Merkle / ECDSA / hash |
| 2008 | Debian OpenSSL RNG bug | 工程實作教訓 |
| 2009 | Gentry FHE | 加密狀態運算可行 |
| 2013 | Snowden / Dual_EC_DRBG 後門曝光 | 不要盲信標準 |
| 2014 | Heartbleed (CVE-2014-0160) | 開源密碼學品質警鐘 |
| 2014 | Apple "goto fail" | 一行 bug 毀掉 TLS |
| 2015 | NIST 啟動 PQC 競賽 | 量子過渡開始 |
| 2015 | Logjam (DH-1024 被破) | 標準參數要升級 |
| 2017 | SHA-1 SHAttered (Google) | SHA-1 死刑 |
| 2017 | KRACK (WPA2) | nonce reuse 真實案例 |
| 2018 | TLS 1.3 RFC 8446 | AEAD-only + FS 強制 |
| 2018 | WireGuard | Noise framework 落地 |
| 2018 | Powers of Tau ceremony (Zcash) | ZK trusted setup 範本 |
| 2020 | Sigstore / Cosign 啟動 | Supply chain crypto 元年 |
| 2021 | Bitcoin Taproot (Schnorr/MAST) | 公鏈用 Schnorr |
| 2022 | NIST PQC 選定 Kyber / Dilithium / Falcon / SPHINCS+ | PQC 標準化 |
| 2023 | Ethereum KZG ceremony（~14 萬人） | 史上最大 trusted setup |
| 2023 | Cloudflare 部署 X25519+Kyber hybrid TLS | PQC 進 production |
| 2024 | NIST FIPS 203/204/205（ML-KEM / ML-DSA / SLH-DSA） | 後量子正式標準 |
| 2024 | xz-utils backdoor | 供應鏈攻擊新高度 |
| 2024 | Apple PCC 用 ZK + TEE | 大廠採用 attestation |
| 2025 | Chrome 預設啟用 X25519MLKEM768 | PQC 進入瀏覽器主流 |

---

<a id="crossref"></a>

## Appendix C：與應用篇的交叉地圖

| 應用篇 § | 理論篇對應 |
|---|---|
| §2 核心地圖 | §4 (Hash) + §5 (Block) + §6 (Stream) + §7 (AEAD) + §8 (MAC) + §9 (PKC) + §10 (Sig) + §12 (KDF) |
| §3 TLS / mTLS | §11 (KEX) + §13 (TLS internal) |
| §4 Secrets / KMS | §7 (AEAD) + §12 (KDF) + §19 (Vault Shamir) |
| §5 JWT / OIDC | §8 (MAC) + §10 (Sig) |
| §6 Supply chain / Cosign | §10 (Sig) + §15 (Provable) + §18 (Merkle / Rekor) |
| §8 反 pattern | §14 (Attack taxonomy) |
| § 後量子顧慮 | §16 (PQC) |
| § ZK / 區塊鏈興趣 | §17 (ZK) |
| § 進階：Vault unseal、threshold | §19 (Threshold) |

兩篇可以分開讀，但**應用篇有疑問時翻理論篇對應章節，理解會立刻深一層**。
這就是「會用」和「會解釋」的差距。

---

## v2 後記

從 v1 (1617 行) 升級到 v2 (~3500+ 行) 的目標不是「多寫一倍」，而是**把「目錄式章節」變成「真的能拿來重新組裝知識」的內容**：

- §3 不再只給「P/NP 是什麼」，而是給你「128-bit 安全 = 永遠不可行」的尺規
- §13 不再只貼 RFC 圖，而是告訴你每根 secret 為什麼存在
- §15 不再只列名詞，而是走完一次 ElGamal → DDH 完整 reduction
- §17 不再只說 "ZK exists"，而是告訴你 simulator argument、R1CS pipeline、ZK 系統如何選
- §18 / §19 兩個新章補上 Merkle / threshold — 直接對應應用篇 §6 (Sigstore) 和 §4 (Vault) 的密碼學底層

如果你照這個結構讀過一遍，**面試 / incident review / paper reading 三個場景的「為什麼」回答能力會升一個檔次**。
