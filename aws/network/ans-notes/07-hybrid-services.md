# 07 Hybrid Services

## AWS Directory Service

**What:** AWS Directory Service 提供 Managed Microsoft AD 或 AD Connector 等模式，讓 AWS 工作負載能使用目錄服務。

**When to use:** WorkSpaces、FSx、需要 AD 認證/授權、Hybrid identity。

**Key Points:**
- Managed Microsoft AD 是 AWS 代管的原生 Microsoft AD，支援 trust、GPO、SSO。
- AD Connector 不儲存目錄資料，只是把 AWS 端驗證代理到 On-prem AD。
- Managed AD 部署在多 AZ，網路中斷時仍能在 AWS 內部維持運作。
- AD Connector 依賴私網連到 On-prem AD，通常走 DX 或 VPN。

**⚠️ 考試陷阱:**
- AD Connector 不是複製一份 AD 到 AWS，它只是轉送驗證。

**✅ 記憶點:**
- `Need trust or AWS-side directory resilience` 想 Managed AD。

## FSx

**What:** FSx 提供受管檔案系統，常考 Windows File Server 與 Lustre。

**When to use:** Windows SMB share、HPC、ML、大量高效能檔案存取。

**Key Points:**
- FSx for Windows File Server 原生支援 SMB、AD、DFS、VSS、KMS、in-transit encryption。
- 可透過 VPC Peering、VPN、DX 存取。
- FSx for Lustre 面向 HPC/ML，低延遲高吞吐，可與 S3 整合。
- Lustre 有 Persistent 與 Scratch 兩種部署模型。

**⚠️ 考試陷阱:**
- 題目若提 Windows ACL/SMB/AD，多半不是 EFS，而是 FSx for Windows。

**✅ 記憶點:**
- `Windows native file share` 想 FSx for Windows。
- `HPC POSIX` 想 FSx for Lustre。

## Storage Gateway

**What:** Storage Gateway 是把 On-prem storage 與 AWS storage 串起來的橋樑。

**When to use:** Migration、備份現代化、資料中心延伸、混合式檔案/區塊/磁帶工作流。

**Key Points:**
- Volume Gateway 有 Stored Mode 與 Cached Mode。
- Stored Mode 主要資料在本地，AWS 做 async backup。
- Cached Mode 主要資料在 AWS，本地只留快取。
- Tape Gateway/VTL 可把傳統備份軟體接到 AWS，封存到 Glacier。
- File Gateway 以 NFS/SMB 呈現檔案，底層對應 S3。

**⚠️ 考試陷阱:**
- 要把舊備份系統無痛接到 AWS 冷存，通常是 Tape Gateway，不是 DataSync。

**✅ 記憶點:**
- `Backup modernize` 想 Tape Gateway。
- `S3-backed file shares` 想 File Gateway。

## WorkSpaces

**What:** WorkSpaces 是受管桌面即服務。

**When to use:** 遠距辦公、受管桌面、需要與 AD/FSx/On-prem 整合。

**Key Points:**
- WorkSpaces 使用 Directory Service 驗證。
- 每個 WorkSpace 會在你的 VPC 中注入 ENI。
- 可依月或依時數計費。
- 可存取 VPC 內資源，也可透過既有 Hybrid 網路進入 On-prem。

**⚠️ 考試陷阱:**
- WorkSpaces 依賴網路與目錄服務，常考 Directory Service 選型。

**✅ 記憶點:**
- `Managed virtual desktop + AD` 想 WorkSpaces。
