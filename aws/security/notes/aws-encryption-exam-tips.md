# AWS 加密考法對比

## 三種加密考法對比

### 1️⃣ Encrypt at Rest
**關鍵字：** data at rest, stored data, encryption at rest

**考法場景：**
- "Company must ensure all data stored is encrypted"

**服務對應：**
- S3 → SSE-S3 / SSE-KMS
- EBS → KMS encryption
- RDS → encryption at rest
- DynamoDB → encryption at rest

**答題方向：** 看存在哪裡 → 對應服務的 encryption 設定

### 2️⃣ Encrypt in Transit
**關鍵字：** encrypted in transit, secure communication, HTTPS

**考法場景：**
- "Ensure all traffic between clients and servers is encrypted"

**架構示例：**
```
Client --[TLS]-→ ALB (解密OK) --[TLS]-→ EC2
```

**答題方向：** ALB + HTTPS listener，或 ACM 憑證即可

### 3️⃣ No Decryption at Intermediate Points
**關鍵字：** end-to-end encryption, no decryption at intermediate, pass-through

**考法場景：**
- "Traffic must remain encrypted at all stages, no decryption allowed in between"

**架構示例：**
```
Client --[TLS]-→ NLB (透傳) --[TLS]-→ EC2
                  ↑
             看不到內容
```

**答題方向：** NLB + TCP listener

## 一張表總結

| 類型 | 關鍵字 | 答案方向 |
|------|--------|---------|
| at rest | stored, at rest | KMS, SSE |
| in transit | encrypted in transit, HTTPS | ALB + HTTPS |
| end-to-end | no decryption, all stages | NLB + TCP |

## 金句
**加密題先問自己「誰可以解密、在哪裡解密」，答案自然浮現。**

---

## ANS 考試加密考法的層次

### Level 1 → 基礎加密
**傳輸加密位置：** at rest / in transit / end-to-end
**工具：** ALB HTTPS, NLB TCP, KMS

### Level 2 → 進階身份驗證
**mTLS：** 雙向憑證驗證（client + server 都要出示憑證）
**工具：** ALB mTLS listener, ACM Private CA

**典型考法：**
```
"Company requires mutual authentication between clients and servers"
→ ALB + mTLS + ACM Private CA
```

### Level 3 → 架構信任模型
**ZTN (Zero Trust Network)：**
- 不信任任何節點，每次都驗證身份
- 最小化風險半徑（minimize blast radius）

**工具：** IAM, mTLS, VPC Lattice, PrivateLink

**典型考法：**
```
"Never trust, always verify, minimize blast radius"
→ VPC Lattice / PrivateLink + IAM Auth + mTLS
```

## 學習建議
這三層要分開刷，ANS 考 mTLS 和 ZTN 的題目不多，但出現就是送分題，**概念清楚就拿到**。
