# Default NACL vs Security Group 行為比較

## 結論速查

| 項目 | Default NACL | Default Security Group |
|------|-------------|----------------------|
| **Inbound** | Allow ALL ✅ | 只允許同 SG 來源 ⚠️ |
| **Outbound** | Allow ALL ✅ | Allow ALL ✅ |
| **Stateful?** | ❌ Stateless | ✅ Stateful |

> EC2 的 **outbound 流量不會被 SG 擋住**（default SG outbound 允許所有流量）。
> 但 **inbound 預設只接受同 SG 內的流量**，外部流量（如 Internet Gateway、NAT Gateway）預設不放行。

---

## NACL 詳細規則

### Default NACL（隨 VPC 自動建立）

像是一扇**永遠開著的門**，不會擋住任何流量。

#### Inbound Rules

| Rule # | Type | Protocol | Port Range | Source | Allow/Deny |
|--------|------|----------|-----------|--------|-----------|
| 100 | All Traffic | All | All | 0.0.0.0/0 | **ALLOW** |
| * | All Traffic | All | All | 0.0.0.0/0 | DENY |

#### Outbound Rules

| Rule # | Type | Protocol | Port Range | Destination | Allow/Deny |
|--------|------|----------|-----------|------------|-----------|
| 100 | All Traffic | All | All | 0.0.0.0/0 | **ALLOW** |
| * | All Traffic | All | All | 0.0.0.0/0 | DENY |

> Rule 100 允許所有流量，`*` deny rule 永遠不會被評估到。

### Custom NACL（你自己按 Create 建立的）

Inbound & Outbound **預設全是 Deny ALL**（只有 `*` deny rule），你必須手動一條一條加規則。這就是常說的「預設拒絕」。

### NACL 共通重點

- NACL 是 **Stateless**：回應流量不會自動放行，需要明確的 outbound rule（含 ephemeral ports）
- 按 **rule number 由小到大**評估，匹配即停止
- Default NACL **不可刪除**，Custom NACL 可刪除

---

## Security Group 詳細規則

### Default SG（AWS 自動建立的）

每個 VPC 自帶一個 Default SG，**不可刪除、但可修改規則**。

#### Inbound Rules

| Source | Protocol | Port Range | 說明 |
|--------|----------|-----------|------|
| sg-xxxxxxxx（**Self**） | All | All | 只允許**同一個 SG 內**的資源互相通訊 |

> 外部流量（如 Internet Gateway、NAT Gateway）預設**不放行**。

#### Outbound Rules

| Destination | Protocol | Port Range | 說明 |
|-------------|----------|-----------|------|
| 0.0.0.0/0 | All | All | 允許所有 IPv4 outbound |
| ::/0 | All | All | 允許所有 IPv6 outbound（有 IPv6 CIDR 時） |

> 這就是為什麼 EC2 的封包**出得去** — outbound 預設全開。

### Custom SG（你自己按 Create 建立的）

| 方向 | 預設規則 | 說明 |
|------|---------|------|
| **Inbound** | **Deny ALL**（完全空的） | 沒有任何規則，全部擋住 |
| **Outbound** | **Allow ALL**（0.0.0.0/0） | AWS 為了方便預設幫你加一條，但**你可以刪掉** |

### SG 共通重點

- SG 是 **Stateful**：如果 outbound 請求被允許，回應流量自動放行（不需要 inbound rule）
- SG **只能設定 allow rule**，不能設定 deny rule
- Default SG **不可刪除**，Custom SG 可刪除

---

## 常見問題排查

### EC2 無法被外部存取？
```
檢查順序：
1. SG Inbound → 是否有允許對應 port 的規則？（最常見原因）
2. NACL Inbound → Default NACL 不擋，Custom NACL 需確認
3. Route Table → 是否有到 IGW 的路由？
4. IGW → 是否已 attach 到 VPC？
```

### EC2 無法存取外部網路？
```
檢查順序：
1. Route Table → 是否有 0.0.0.0/0 指向 IGW 或 NAT GW？
2. SG Outbound → Default 允許所有（通常不是問題）
3. NACL Outbound → Default 允許所有（通常不是問題）
4. NACL Inbound → 回應流量是否被擋？（NACL stateless！）
```

### Default vs Custom 完整比較

| | Default NACL | Custom NACL | Default SG | Custom SG |
|---|---|---|---|---|
| **建立方式** | 隨 VPC 自動建立 | 你手動 Create | 隨 VPC 自動建立 | 你手動 Create |
| **初始 Inbound** | Allow ALL | **Deny ALL** | 同 SG only (Self) | **Deny ALL**（空的） |
| **初始 Outbound** | Allow ALL | **Deny ALL** | Allow ALL | Allow ALL（可刪） |
| **Stateful?** | ❌ Stateless | ❌ Stateless | ✅ Stateful | ✅ Stateful |
| **可刪除？** | ❌ | ✅ | ❌ | ✅ |
| **可設 Deny？** | ✅ | ✅ | ❌ 只能 Allow | ❌ 只能 Allow |

---

## 考試重點

1. **Default NACL = 全開**，Custom NACL = 全關
2. **Default SG inbound = 只允許同 SG**，不是全開！
3. NACL **stateless** → 需要同時設定 inbound + outbound + ephemeral ports
4. SG **stateful** → 只需要設定發起方向的規則
5. SG **不能設定 deny rule**，只能設定 allow rule
6. NACL 按 **rule number 由小到大** 評估，匹配即停止

---

## 參考來源

- [AWS Docs - Network ACLs](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-network-acls.html)
- [AWS Docs - Default Security Group](https://docs.aws.amazon.com/vpc/latest/userguide/default-security-group.html)
- [AWS Docs - Security Groups](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html)
