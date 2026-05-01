# Redirect-on-Write (ROW) 深度研究

> 本文從底層原理、各系統實作、碎片化、Snapshot、進階議題到限制，全面深入 ROW 機制。適合 DevOps/Cloud/Platform Engineer 建立系統級理解。

## 目錄

- [1. ROW 底層原理與完整工作流程](#1-row-底層原理與完整工作流程)
  - [1.1 Write Operation Step-by-Step](#11-write-operation-step-by-step)
  - [1.2 Pointer/Metadata 傳播（Tree of Blocks）](#12-pointermetadata-傳播tree-of-blocks)
  - [1.3 Free Space Management](#13-free-space-management)
  - [1.4 Garbage Collection / Space Reclamation](#14-garbage-collection--space-reclamation)
- [2. 各系統的 ROW 實作差異](#2-各系統的-row-實作差異)
  - [2.1 ZFS](#21-zfs)
  - [2.2 Btrfs](#22-btrfs)
  - [2.3 NetApp WAFL](#23-netapp-wafl)
  - [2.4 Microsoft ReFS](#24-microsoft-refs)
  - [2.5 NILFS2](#25-nilfs2)
  - [2.6 F2FS](#26-f2fs)
- [3. ROW 的碎片化問題](#3-row-的碎片化問題)
  - [3.1 為什麼 ROW 必然導致碎片化](#31-為什麼-row-必然導致碎片化)
  - [3.2 各系統的碎片化緩解策略](#32-各系統的碎片化緩解策略)
  - [3.3 HDD vs SSD 的碎片化影響差異](#33-hdd-vs-ssd-的碎片化影響差異)
  - [3.4 效能退化的實際數據](#34-效能退化的實際數據)
- [4. ROW 與 Snapshot 的關係](#4-row-與-snapshot-的關係)
  - [4.1 Zero-Cost Snapshots 原理](#41-zero-cost-snapshots-原理)
  - [4.2 Snapshot Deletion 與 Space Reclamation 的複雜度](#42-snapshot-deletion-與-space-reclamation-的複雜度)
  - [4.3 Snapshot Chains 與效能影響](#43-snapshot-chains-與效能影響)
  - [4.4 Writable Snapshots（Clones）](#44-writable-snapshotsclones)
- [5. ROW vs Traditional COW vs WAL](#5-row-vs-traditional-cow-vs-wal)
  - [5.1 I/O Pattern 比較](#51-io-pattern-比較)
  - [5.2 Write Amplification 分析](#52-write-amplification-分析)
  - [5.3 Crash Consistency 比較](#53-crash-consistency-比較)
  - [5.4 何時選擇哪種方法](#54-何時選擇哪種方法)
- [6. ROW 進階議題](#6-row-進階議題)
  - [6.1 Deduplication with ROW（ZFS Dedup）](#61-deduplication-with-rowzfs-dedup)
  - [6.2 Transparent Compression](#62-transparent-compression)
  - [6.3 RAID with ROW](#63-raid-with-row)
  - [6.4 ROW in Virtualization（QCOW2）](#64-row-in-virtualizationqcow2)
  - [6.5 ROW in Databases（LMDB）](#65-row-in-databaseslmdb)
- [7. ROW 的限制與反面案例](#7-row-的限制與反面案例)
  - [7.1 不適合的 Workload](#71-不適合的-workload)
  - [7.2 Database-on-ZFS/Btrfs Tuning](#72-database-on-zfsbtrfs-tuning)
  - [7.3 Write Cliff 問題](#73-write-cliff-問題)
  - [7.4 何時不該使用 ROW](#74-何時不該使用-row)
- [8. 參考資料](#8-參考資料)

---

## 1. ROW 底層原理與完整工作流程

### 1.1 Write Operation Step-by-Step

ROW 的核心原則：**永不覆寫現有資料**。所有寫入操作都導向新的磁碟位置，舊資料原地保留。

```
Step 1: 應用發出 write(fd, buf, size)
        ↓
Step 2: Filesystem 將修改資料暫存於記憶體（transaction buffer / dirty pages）
        ↓
Step 3: Allocator 從 free space map 選取新的空閒區塊
        ↓
Step 4: 新資料寫入新位置（不覆蓋舊區塊）
        ↓
Step 5: 更新指向該資料的 metadata block pointer
        → 但 metadata 本身也是 ROW，所以：
        ↓
Step 6: metadata 也寫到新位置
        → 其父層 metadata 的 pointer 也需更新
        → 逐層向上傳播（COW cascade / ROW cascade）
        ↓
Step 7: 到達 root block（uberblock / superblock）
        → 原子性寫入新的 root pointer
        → 切換檔案系統一致性狀態
        ↓
Step 8: 舊區塊標記為「可回收」（若無 snapshot 引用）
```

**關鍵洞察**：ROW 將「隨機覆寫」轉化為「追加寫入 + 指標更新」。這使得：
- 舊資料天然保留 → Snapshot 近乎免費
- 寫入永遠到新位置 → 崩潰時舊狀態完整
- 但也意味著 → 資料逐漸散佈在磁碟各處（碎片化）

### 1.2 Pointer/Metadata 傳播（Tree of Blocks）

ROW 檔案系統本質上是一棵 **Merkle Tree**（以 ZFS 為例）：

```
                    ┌──────────────┐
                    │  Uberblock   │  ← 根節點（原子性更新）
                    │  TXG=1000    │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │  MOS (Meta   │  ← Meta Object Set
                    │  Object Set) │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ Dataset  │ │ Dataset  │ │ Dataset  │
        │ objset   │ │ objset   │ │ objset   │
        └────┬─────┘ └──────────┘ └──────────┘
             │
        ┌────▼─────┐
        │  dnode   │  ← 類似 inode
        │ (file X) │
        └────┬─────┘
             │
    ┌────────┼────────┐
    ▼        ▼        ▼
┌───────┐┌───────┐┌───────┐
│Block 0││Block 1││Block 2│  ← 實際資料區塊
│ +chk  ││ +chk  ││ +chk  │     每個都帶 checksum
└───────┘└───────┘└───────┘
```

**當修改 Block 1 時的傳播路徑**：

```
1. Block 1' 寫入新位置（含新資料 + 新 checksum）
2. dnode' 寫入新位置（更新 Block 1 的 pointer，重算 checksum）
3. objset' 寫入新位置（更新 dnode 的 pointer）
4. MOS' 寫入新位置（更新 objset 的 pointer）
5. Uberblock' 原子性寫入（更新 MOS 的 pointer，TXG=1001）

→ 修改 1 個資料區塊，需要更新整條路徑上的所有節點
→ 但 tree 的深度通常只有 4-6 層，所以開銷可控
→ 所有未修改的區塊（Block 0, Block 2, 其他 dataset）完全不受影響
```

**Checksum 的角色**：每個 block pointer 中儲存其子區塊的 checksum。這形成了 **self-validating Merkle tree**——從根到葉的每一層都可驗證下一層的完整性。讀取時，ZFS 會自動驗證讀到的資料是否與 parent 中記錄的 checksum 吻合。

### 1.3 Free Space Management

ROW 因為不斷寫到新位置，所以 free space management 至關重要。

#### ZFS: Space Maps + Metaslab Allocator

```
Pool (zpool)
├── vdev 0 (mirror / raidz / ...)
│   ├── Metaslab 0  ← 512MB ~ 16GB 的分區
│   │   └── Space Map (append-only log of alloc/free)
│   ├── Metaslab 1
│   │   └── Space Map
│   └── Metaslab N
│       └── Space Map
└── vdev 1
    └── ...
```

**Space Map 結構**：
- 不是 bitmap（太大、浪費），而是一個 **append-only log**，記錄 alloc/free 事件
- 格式：`<ALLOC|FREE> <offset> <size>` 的序列
- 載入到記憶體時，轉化為 range tree（按 offset 排序的 AVL tree）
- 週期性 **condense**：如果 alloc-free 對太多互相抵消，ZFS 重寫一份壓縮後的 space map

**Metaslab Allocator 策略**：
- **First-Fit**（預設，pool 空間充足時）：找第一個夠大的連續空間，速度快
- **Best-Fit**（pool 碎片化時自動切換）：找最接近所需大小的空間，避免浪費
- 切換閾值：當 metaslab 的 free space 低於 4% 時，從 first-fit 切換到 best-fit
- **log_spacemap** feature（較新版本）：避免頻繁重寫 metaslab space map，改用 pool-level log

**Metaslab Selection**：
- 選擇 metaslab 時考慮：free space 量、碎片化程度、離上次 I/O 的距離
- `spacemap_histogram` feature 記錄每個 metaslab 中各大小等級的連續空閒空間分布

#### Btrfs: Block Groups + Free Space Tree

```
Btrfs 空間管理
├── Block Group (Data)     ← 通常 1GB，對應特定 RAID profile
├── Block Group (Metadata) ← 通常 256MB
├── Block Group (System)   ← 小，存 chunk tree
│
├── Extent Tree            ← 記錄哪些 extent 已分配 + reference count
└── Free Space Tree        ← 快速查找 block group 內的空閒空間
```

- **Extent Tree**：記錄已分配的 byte range、reference count、back reference
- **Free Space Tree**（替代舊的 free space inode cache）：B-tree 結構，快速查找 block group 內的空閒區段
- 分配策略：Btrfs 在 block group 內尋找合適大小的 extent，偏好大的連續區段

### 1.4 Garbage Collection / Space Reclamation

在 ROW 中，舊區塊不會被直接覆寫，因此需要機制來回收不再引用的區塊。

#### 何時舊區塊可以被回收？

```
情境 1：無 Snapshot
  修改區塊 A → 寫入 A' 到新位置 → 更新 pointer → A 立即可回收
  （transaction commit 後，A 的 space 就加回 free space map）

情境 2：有 Snapshot
  Snapshot 仍引用區塊 A → A 不可回收
  只有當所有引用 A 的 snapshot 都被刪除後，A 才可回收
  （透過 reference counting / deadlist 追蹤）

情境 3：Clone（writable snapshot）
  Clone 可能修改了 A 的一部分
  → 需要追蹤 block-level reference count
  → 只有 refcount 降到 0 才能回收
```

#### ZFS 的 Space Reclamation

- **Deadlist**：當檔案被刪除但 snapshot 仍引用時，ZFS 在 deadlist 中記錄這些 block。Deadlist 按 birth txg 排序分成多個 sublist
- **Birth Transaction 比較**：刪除 block 時，ZFS 比較 block 的 birth txg 與下一個最舊 snapshot 的 birth txg。若 block 比 snapshot 新，表示 snapshot 不引用它，可立即回收
- **異步刪除**：Snapshot 刪除操作在 background 異步進行，複雜度為 O(# sublists + # blocks to free)

#### NILFS2 的 Garbage Collection

- NILFS2 使用 user-space daemon `nilfs_cleanerd` 進行 online garbage collection
- 掃描 log segments，找出不再被任何 checkpoint/snapshot 引用的區段
- 將仍然活躍的資料搬移到新的 segment，然後回收舊 segment
- 類似 log-structured filesystem 的 cleaning 問題

---

## 2. 各系統的 ROW 實作差異

### 2.1 ZFS

ZFS 是 ROW 最完整、最複雜的實作，其架構分為多層：

```
┌─────────────────────────────────────┐
│            ZPL (ZFS POSIX Layer)    │  ← POSIX 介面
├─────────────────────────────────────┤
│            ZIL (ZFS Intent Log)    │  ← 同步寫入的 WAL
├─────────────────────────────────────┤
│            DMU (Data Mgmt Unit)    │  ← 物件/交易管理
├─────────────────────────────────────┤
│            ARC (Adaptive Replace   │  ← 讀取快取
│            Cache)                   │
├─────────────────────────────────────┤
│            SPA (Storage Pool       │  ← Pool/vdev/I/O 管理
│            Allocator)               │
├─────────────────────────────────────┤
│            VDEV Layer              │  ← 虛擬裝置抽象
│            (mirror, raidz, ...)    │
└─────────────────────────────────────┘
```

#### Transaction Groups (TXG)

ZFS 將寫入批次化為 **Transaction Groups**，是 ROW 的原子性單位：

```
時間軸：
  ─── TXG 1000 ───── TXG 1001 ───── TXG 1002 ───→
      [syncing]      [quiescing]    [open]
      寫入磁碟中      停止接受新寫入  接受新寫入
                     等待 in-flight
                     操作完成

三階段 Pipeline：
  Open      → 接受新的 write 操作（通常 5-30 秒）
  Quiescing → 凍結，等待所有 in-flight 操作完成
  Syncing   → 將所有 dirty data 寫入磁碟
              最後寫入新 uberblock 完成 commit
```

- Pipeline 化設計：三個 TXG 同時處於不同狀態，提高吞吐量
- `zfs_txg_timeout`（預設 5 秒）控制 TXG 切換頻率
- 若有大量 dirty data，TXG 可能延長到 30 秒

#### ZIL (ZFS Intent Log)

```
同步寫入路徑：
  fsync() → ZIL 記錄 intent log record
          → 立即 flush 到持久化儲存（pool 或 SLOG）
          → 回覆 client "已持久化"
          → 實際 ROW 稍後在 TXG sync 時執行

SLOG (Separate Log device)：
  ┌──────────┐
  │ 高速 NVMe │  ← ZIL 寫到這裡（低延遲）
  │   SLOG    │
  └──────────┘
  實際資料稍後在 TXG sync 時寫入主 pool
  → 若 TXG 成功 commit，ZIL records 可丟棄
  → 若 crash，replay ZIL records 恢復未 commit 的同步寫入
```

#### Block Pointer 結構

ZFS block pointer (`blkptr_t`) 是 **128 bytes** 的結構：

```
blkptr_t (128 bytes)
├── DVA[0]  (Data Virtual Address)
│   ├── vdev ID     ← 在哪個 vdev 上
│   ├── offset      ← vdev 內的偏移量
│   └── gang bit    ← 是否為 gang block
├── DVA[1]  (第二份副本，用於 ditto blocks / mirrors)
├── DVA[2]  (第三份副本)
├── Properties
│   ├── lsize       ← logical size（壓縮前）
│   ├── psize       ← physical size（壓縮後）
│   ├── compression ← 壓縮演算法
│   ├── checksum    ← checksum 演算法
│   ├── type        ← block type (data, indirect, ...)
│   ├── level       ← indirect block 層級
│   └── encrypted   ← 是否加密
├── padding
├── physical birth txg  ← 實體寫入的 TXG
├── logical birth txg   ← 邏輯分配的 TXG
├── fill count          ← 子樹中有多少 non-zero block
└── checksum[4]         ← 256-bit checksum（fletcher4 / SHA-256）
```

**DVA（Data Virtual Address）** 三份的用途：
- 單份：普通資料
- 雙份（ditto blocks）：重要 metadata（自動由 ZFS 決定）
- 三份：最關鍵的 metadata（如 uberblock）

**Embedded Block Pointer**：對於 < 112 bytes 的小資料，直接嵌入 block pointer 本身，避免額外的間接 I/O。

**Gang Block**：當找不到足夠大的連續空間時，ZFS 建立 gang block header（一個 block 裡面放多個 block pointer），將資料拆散到多個小區塊。

#### Uberblock

```
每個 vdev label 包含 128 個 uberblock slot（ring buffer）
每次 TXG commit 時 round-robin 寫入下一個 slot

Uberblock 內容：
├── magic number
├── version
├── txg              ← 此 uberblock 對應的 TXG
├── guid_sum         ← pool 中所有 vdev GUID 的和
├── timestamp
├── rootbp           ← 指向 MOS 的 block pointer
└── software version

Pool import 時的恢復：
  掃描所有 vdev label 的 uberblock ring buffer
  → 找到 txg 最大且 checksum 驗證通過的 uberblock
  → 從該 uberblock 的 rootbp 開始重建整棵 tree
  → 忽略所有 crash 時正在 sync 的未完成 TXG
```

### 2.2 Btrfs

Btrfs 的 ROW 實作基於 **COW-friendly B-trees**：

```
Btrfs 核心 B-tree 結構：
┌──────────────────┐
│    Superblock     │  ← 固定位置（0, 64MB, 256GB）
│  (3 copies fixed) │
└────────┬─────────┘
         │
┌────────▼─────────┐
│    Root Tree      │  ← 所有其他 tree 的入口
│  (tree of trees)  │
└────────┬─────────┘
    ┌────┼────┬────────────┬─────────────┐
    ▼    ▼    ▼            ▼             ▼
┌──────┐┌────────┐┌─────────────┐┌───────────┐┌──────────┐
│FS    ││Extent  ││Checksum     ││Free Space  ││Chunk/Dev │
│Tree  ││Tree    ││Tree         ││Tree        ││Tree      │
│(per  ││        ││             ││            ││          │
│subvol)│        ││             ││            ││          │
└──────┘└────────┘└─────────────┘└────────────┘└──────────┘
```

**B-tree Key 的統一格式**：`(objectid, type, offset)` — 所有 B-tree 共用相同的 key format 和 node format。

**COW B-tree 更新流程**：
1. 修改 leaf node 中的資料
2. Leaf node COW 到新位置
3. Parent internal node 的 pointer 需更新 → Parent 也 COW
4. 一路向上直到 root node
5. Root node 的位置更新在 root tree 中
6. Root tree 的 root 更新在 superblock 中
7. Superblock 原子性寫入（3 個固定位置輪流寫）

**Extent Allocation**：
- Extent tree 記錄所有已分配的 extent（byte range）和 reference count
- Back reference 機制：從 extent 可以反向找到引用它的 tree/file
- Block group 內按 extent 分配，偏好大的連續區段
- Allocator 會考慮 RAID profile（data/metadata 可以有不同的 RAID level）

**Subvolume 實作**：
- 每個 subvolume 是一棵獨立的 FS tree，有自己的 root inode
- Subvolume 之間可以透過 snapshot 共享 extent
- Snapshot = 在 root tree 中增加一個新 entry，指向原 FS tree 的同一個 root node
- Reference count 確保共享的 extent 在任一方修改時 COW

### 2.3 NetApp WAFL

WAFL（Write Anywhere File Layout）是 NetApp ONTAP 儲存系統的核心：

```
WAFL 架構：
┌─────────────────────────────────┐
│          NFS / CIFS / iSCSI     │  ← 前端協議
├─────────────────────────────────┤
│          ONTAP OS               │
├─────────────────────────────────┤
│          WAFL Filesystem        │
│  ┌──────────┐ ┌──────────────┐  │
│  │ NVRAM /  │ │ Block Map    │  │
│  │ NVMEM    │ │ (in file)    │  │
│  │ (NVLOG)  │ │              │  │
│  └──────────┘ └──────────────┘  │
├─────────────────────────────────┤
│          RAID-DP / RAID-TEC     │
├─────────────────────────────────┤
│          Physical Disks         │
└─────────────────────────────────┘
```

**WAFL 的獨特設計**：

1. **Metadata-as-files**：WAFL 將 metadata（包括 inode file、block map、directory）都存為普通檔案，不放在固定位置。唯一固定的是 root inode（inode file 的 inode），稱為 `fsinfo` block
2. **Write Anywhere**：WAFL 可以在任何可用位置寫入，而不是限制在特定區域
3. **NVRAM / NVLOG**：
   - 將 NFS/CIFS 請求先記錄在 NVRAM 中（非揮發記憶體）
   - NVRAM 分為兩個 log（double buffering）
   - 一個 log 滿了 → 切換到另一個 → 觸發 Consistency Point (CP)
4. **Consistency Point (CP)**：
   - 觸發條件：NVRAM 半滿、10 秒定時器、手動觸發
   - CP 將 NVRAM 中累積的修改批次寫入磁碟
   - 寫入時一次性分配所有需要的 block，最佳化磁碟佈局
   - 最後原子性更新 fsinfo block（類似 ZFS uberblock）
5. **Block Map**：
   - 存為檔案（不在固定位置），每個 block 一個 entry
   - Entry 包含：in-use bit + 每個 snapshot 的 in-use bit
   - 可以快速判斷某 block 是否被任何 snapshot 引用

**與 ZFS 的關鍵差異**：
- WAFL 依賴 NVRAM 硬體保證 write ordering → ZFS 純軟體解決
- WAFL 的 CP 類似 ZFS 的 TXG，但更依賴硬體加速
- WAFL 的 block map 是 bitmap-like → ZFS 用 space map log

### 2.4 Microsoft ReFS

ReFS (Resilient File System) 在 Windows Server 上實作 ROW：

```
ReFS 核心特性：
├── Allocate-on-Write（ROW）
│   ├── 所有 metadata 更新都寫到新位置
│   └── 可選擇性地對 file data 也啟用（Integrity Streams）
├── Integrity Streams
│   ├── 對檔案資料啟用 checksum
│   ├── 啟用後所有寫入變成 allocate-on-write
│   └── 讀取時自動驗證 checksum
├── Block Cloning
│   ├── O(1) 的檔案複製（只複製 metadata）
│   ├── 維護 logical cluster 的 reference count
│   └── 寫入共享區域時觸發 allocate-on-write（類似 COW）
└── Block Integrity
    └── Metadata 永遠有 checksum + allocate-on-write
```

**ReFS vs ZFS/Btrfs**：
- ReFS 對 **metadata** 永遠使用 ROW，但對 **data** 是可選的（Integrity Streams）
- 這使 ReFS 在不啟用 Integrity Streams 時有更好的隨機寫入效能
- ReFS 缺少 ZFS 的 pool/vdev 抽象，依賴 Windows Storage Spaces
- ReFS 不支援 transparent compression（ZFS/Btrfs 支援）

**Block Cloning 機制**：
- 多個檔案可以共享相同的 physical clusters
- ReFS 維護每個 logical cluster 的 reference count
- 寫入共享 cluster 時，allocate-on-write 確保其他引用者不受影響
- 用例：Hyper-V checkpoint、dedup、快速檔案複製

### 2.5 NILFS2

NILFS2 是 Linux 上的 **log-structured + ROW 混合**檔案系統：

```
NILFS2 磁碟佈局：
┌────────────┬──────────────────────────────────────┐
│ Superblock │           Log Segments               │
│ (fixed)    │  ┌─────┐┌─────┐┌─────┐     ┌─────┐  │
│            │  │Seg 0 ││Seg 1 ││Seg 2 │ ... │Seg N │  │
│            │  │      ││      ││      │     │      │  │
│            │  └─────┘└─────┘└─────┘     └─────┘  │
└────────────┴──────────────────────────────────────┘
                    ←── 循環寫入方向 ──→
```

**核心概念**：
1. **Log-Structured**：整個磁碟視為 circular buffer，新資料追加到 log 尾端
2. **Continuous Checkpointing**：每幾秒（或每次 sync write）自動建立 checkpoint
3. **Checkpoint vs Snapshot**：
   - Checkpoint：自動建立，可被 garbage collector 回收
   - Snapshot：用戶手動將 checkpoint 提升為 snapshot，永久保留直到明確刪除
4. **Garbage Collection**：
   - User-space daemon `nilfs_cleanerd` 負責
   - 掃描 segment，移動仍活躍的 block 到 log 尾端
   - 回收完全無活躍 block 的 segment
   - 可在 online 狀態下執行

**與純 ROW 的差異**：
- NILFS2 更偏向 log-structured（循序寫入），ROW 是其自然結果
- 不像 ZFS/Btrfs 有複雜的 B-tree 結構，NILFS2 用 log 來組織一切
- GC overhead 是 log-structured 設計的固有代價

### 2.6 F2FS

F2FS (Flash-Friendly File System) 專為 NAND Flash 設計：

```
F2FS 磁碟佈局：
┌──────────┬─────┬─────┬───────┬──────────────────┐
│Superblock│  CP │ SIT │  NAT  │    Main Area      │
│          │Area │Area │ Area  │ (Segments/Sections)│
└──────────┴─────┴─────┴───────┴──────────────────┘

CP  = Checkpoint Area（兩份交替寫入）
SIT = Segment Info Table（每個 segment 的有效 block 數量）
NAT = Node Address Table（node ID → physical address 映射）
```

**F2FS 解決的核心 ROW 問題——Wandering Tree**：

```
傳統 log-structured FS 的 Wandering Tree 問題：
  修改 data block → 更新 direct node → 更新 indirect node
  → 更新 inode → 更新 inode table → ... → 更新 superblock
  （每一層都因為 out-of-place update 而連鎖更新）

F2FS 的解法——NAT（Node Address Table）：
  修改 data block → 更新 direct node（寫到新位置）
  → 只需更新 NAT 中該 node 的地址映射（1 個 entry）
  → 傳播鏈被 NAT 截斷！
```

- **Node Address Table (NAT)**：映射 logical node ID → physical block address
- 修改 node 時，只需更新 NAT entry，不需要向上傳播 pointer 更新
- 大幅減少 write amplification（相比傳統 log-structured FS）

**F2FS 的 Multi-Head Logging**：
- 將 segment 分為 Hot/Warm/Cold 三個類型
- Data 和 Node 各自有三個 active segment（共 6 個 log head）
- Hot：頻繁修改的資料（如 directory entries）
- Cold：很少修改的資料（如 multimedia files）
- 分類有助於 GC 效率：cold segment 需要更少的 cleaning

---

## 3. ROW 的碎片化問題

### 3.1 為什麼 ROW 必然導致碎片化

```
寫入時序圖示：

初始狀態（連續佈局）：
磁碟: [A0][A1][A2][A3][B0][B1][B2][Free][Free][Free]...
       └── File A ──┘  └─ File B ─┘

修改 File A 的 block 1：
磁碟: [A0][old][A2][A3][B0][B1][B2][A1'][Free][Free]...
       ^        ^                    ^
       A 的第0塊  A 的第2塊             A 的新第1塊
                                      （不在原位！）

修改 File B 的 block 0：
磁碟: [A0][old][A2][A3][old][B1][B2][A1'][B0'][Free]...

→ File A: [A0][A2][A3]...[A1'] — 不再連續！
→ File B: [B1][B2]...[B0'] — 也不再連續！
```

**ROW 碎片化的根本原因**：
1. **永不 in-place update**：新版本永遠寫到新位置，舊位置成為 "holes"
2. **Free space 散佈**：被釋放的舊 block 分散在磁碟各處
3. **混合寫入**：來自不同檔案的新 block 交錯排列
4. **Metadata 碎片化**：metadata 也是 ROW，所以 metadata blocks 也散佈

**碎片化的兩個維度**：
- **Data fragmentation**：單個檔案的 block 不連續 → sequential read 變成 random read
- **Free space fragmentation**：可用空間由許多小碎片組成 → 難以分配大的連續區段

### 3.2 各系統的碎片化緩解策略

#### ZFS

| 策略 | 說明 |
|------|------|
| **Metaslab allocator** | 將 vdev 分成大塊 metaslab，在 metaslab 內嘗試連續分配 |
| **First-fit → Best-fit** | 空間充足時 first-fit（快速），碎片化時切換 best-fit（減少浪費） |
| **Spacemap histogram** | 追蹤每個 metaslab 的空閒區段大小分布，優先選擇大連續空間的 metaslab |
| **Gang blocks** | 找不到夠大的連續空間時，用 gang block 拆散（犧牲效能換取可用性） |
| **Recordsize tuning** | 增大 recordsize（如 1MB）可減少 metadata 開銷，但增加小寫入的 amplification |
| **Special vdev** | 將 metadata 分離到獨立高速 vdev，減少 metadata 碎片化的影響 |
| **不提供離線 defrag** | ZFS 目前沒有原生的 defrag 工具（[GitHub Issue #3582](https://github.com/openzfs/zfs/issues/3582)） |

#### Btrfs

| 策略 | 說明 |
|------|------|
| **`autodefrag` mount option** | 自動偵測小的隨機寫入，批次讀取相鄰 block 並重寫為連續 extent |
| **`btrfs filesystem defragment`** | 手動 defrag 指定檔案/目錄 |
| **Extent-based allocation** | 分配以 extent（連續區段）為單位，而非單一 block |
| **Target extent size** | `autodefrag` 嘗試合併小 extent 為更大的 extent（預設最多 64KiB 讀取範圍） |
| **注意事項** | Defrag 會破壞 snapshot 的共享（因為 defrag = 重寫資料到新位置 → reference count 變化） |

#### WAFL (NetApp)

| 策略 | 說明 |
|------|------|
| **Consistency Point 批次分配** | CP 時一次性為所有修改分配 block，可以最佳化佈局 |
| **Write allocation optimization** | WAFL 知道接下來要寫什麼，可以盡量連續分配 |
| **Reallocate command** | ONTAP 提供 `reallocate` 命令來重新組織佈局 |

### 3.3 HDD vs SSD 的碎片化影響差異

| 維度 | HDD | SSD |
|------|-----|-----|
| **Sequential read degradation** | **嚴重**：seek time 15-20ms，碎片化直接影響順序讀取 throughput | **極小**：隨機讀取延遲 ~0.1ms，碎片化影響小 |
| **Random write impact** | 碎片化進一步增加 write 的 seek time | SSD 本身就是隨機寫入友好，但過度碎片化可能影響 FTL 效率 |
| **Metadata fragmentation** | metadata 碎片化使得 `ls`、`find` 等操作變慢 | 影響較小，但仍有記憶體中的 metadata 管理開銷 |
| **Defrag 建議** | **有必要**：尤其是大型循序存取的檔案 | **通常不建議**：defrag 增加額外寫入，加速 SSD 磨損，效能收益小 |
| **碎片化真正的問題** | Seek time 和 rotational latency | Extent metadata 膨脹 → 記憶體消耗增加 |

### 3.4 效能退化的實際數據

來自 ZFS 社群的觀察：

- **Pool 使用率 < 50%**：碎片化影響通常可忽略
- **Pool 使用率 50-80%**：碎片化開始累積，但效能退化通常 < 20%
- **Pool 使用率 > 80%**：效能顯著退化，metaslab allocator 進入 best-fit 模式，CPU 使用率升高
- **Pool 使用率 > 90%**：嚴重退化。每個 metaslab 的空閒空間低於 4% 閾值，allocator 變得非常 CPU intensive，IOPS 大幅下降
- **Pool 使用率 > 95%**：可能觸發 "write cliff"——寫入效能斷崖式下降

Kent 大學的 ZFS 碎片化研究顯示：pool fragmentation 與 random write throughput 存在強相關性，free space 越少，random write 效能下降越明顯。

**Btrfs 碎片化數據**：
- VM images 上的 Btrfs 是碎片化重災區：COW 使得每次 guest write 都寫到新位置
- `autodefrag` 對小型 SQLite 資料庫效果顯著（如 Firefox 的 cookie/history db）
- 大型循序檔案（如 video）在 Btrfs 上的碎片化影響 < 小型隨機寫入檔案

---

## 4. ROW 與 Snapshot 的關係

### 4.1 Zero-Cost Snapshots 原理

ROW 使得 snapshot 幾乎「免費」——因為舊資料從不被覆寫。

```
建立 Snapshot 的實際操作：

ZFS:
  1. 複製 dataset 的 root block pointer（一個 128-byte 結構）
  2. 將新的 snapshot entry 加入 DSL（Dataset and Snapshot Layer）
  3. 增加共享 block 的 reference count
  → O(1) 操作，不論 dataset 多大

Btrfs:
  1. 在 root tree 中新增一個 entry，指向原 FS tree 的 root node
  2. 增加 root node 的 reference count
  → O(1) 操作

WAFL:
  1. 複製 root inode（fsinfo block 的副本）
  2. 在 block map 中設置對應的 snapshot bit
  → O(1) 操作
```

**為什麼傳統 COW snapshot 不是零成本**：
- 傳統 COW snapshot 需要在每次寫入時，先將舊資料複製到 snapshot 區域
- 這是 3 次 I/O（讀舊 + 寫到 snapshot + 寫新資料到原位）
- ROW 的 snapshot 只需要一個指標操作，後續寫入也只需要 1 次 I/O（寫到新位置）

### 4.2 Snapshot Deletion 與 Space Reclamation 的複雜度

Snapshot 建立是 O(1)，但**刪除**是複雜操作：

```
Snapshot 刪除流程（ZFS）：

Snapshot 被刪除時，需要判斷哪些 block 可以回收：

情境分析：
  Block X 只被 Snap-A 引用 → Snap-A 刪除時，X 可回收 ✓
  Block X 被 Snap-A 和 Snap-B 引用 → Snap-A 刪除時，X 不可回收 ✗
  Block X 被 Snap-A 和 active FS 引用 → Snap-A 刪除時，X 不可回收 ✗

ZFS 使用 "birth txg" 來快速判斷：
  if block.birth_txg > next_older_snapshot.creation_txg:
      block 不在 next_older_snapshot 中 → 可回收
  else:
      block 在 next_older_snapshot 中 → 不可回收

Deadlist 機制：
  每個 snapshot 維護一個 deadlist
  Deadlist 記錄「在此 snapshot 之後被 delete 的 block」
  Deadlist 按 birth_txg 分成多個 sublist
  刪除 snapshot 時：
    1. 遍歷 deadlist
    2. 對每個 block 判斷是否可回收（比較 birth_txg）
    3. 可回收的 block 加回 space map
    4. 不可回收的 block 移到上一層 snapshot 的 deadlist
  
  複雜度：O(# sublists + # blocks to free)
  → 這可能非常耗時（大型 snapshot 可能有數百萬 block）
  → ZFS 異步執行，避免阻塞前端操作
```

### 4.3 Snapshot Chains 與效能影響

```
Snapshot chain：
  Active FS → Snap3 → Snap2 → Snap1
               │       │       │
               ▼       ▼       ▼
          [blocks]  [blocks]  [blocks]
             ↑         ↑        ↑
          僅 S3    S2+S3 共享  S1+S2+S3 共享
          引用     引用        引用
```

**Snapshot chain 的效能影響**：

| 影響面向 | 說明 |
|---------|------|
| **讀取效能** | 通常無影響。因為 active FS 有自己的完整 block pointer tree，不需要 "traverse" snapshot chain |
| **寫入效能** | 每次寫入仍然只是 ROW 到新位置，snapshot 的存在不影響寫入路徑 |
| **空間追蹤** | Snapshot 越多，deadlist 越複雜。每個 snapshot 的 unique / referenced / compressratio 計算更昂貴 |
| **刪除複雜度** | 刪除中間的 snapshot 需要將其 deadlist 的部分 block 移到相鄰 snapshot 的 deadlist |
| **Send/Receive** | `zfs send -i snap1 snap3` 的增量 send 需要計算兩個 snapshot 之間的差異 |

**最佳實踐**：
- 避免超過 200-300 個 snapshot per dataset（ZFS 經驗法則）
- 定期刪除不需要的 snapshot，避免 deadlist 膨脹
- 使用 `zfs bookmark` 替代長期保留的 snapshot（bookmark 不佔 data space，只記錄 txg 資訊）

### 4.4 Writable Snapshots（Clones）

```
ZFS Clone：
  zfs clone pool/data@snap1 pool/clone1

  pool/data@snap1  ────→  pool/clone1 (writable)
        │                      │
        ├── 共享所有 block     ├── 可以獨立寫入
        └── (read-only)        └── 寫入觸發 ROW
                                    新 block 只屬於 clone

  Clone 初始不佔額外空間
  → 隨著修改增加，clone 的 unique blocks 增長
  → 原 snapshot 不能被刪除（clone depends on it）
  → 除非執行 "zfs promote" 將 clone 提升為獨立 dataset
```

**Btrfs Writable Snapshots**：
- Btrfs 的 snapshot 天生就是可寫的（subvolume 本質上都一樣）
- 建立 snapshot 時可以選擇 read-only 或 read-write
- Read-write snapshot 即是 clone 的等價物
- 同樣透過 reference counting 管理共享 extent

**Clone 的典型用例**：
- 快速建立開發/測試環境（clone production dataset）
- VM / container 的 thin provisioning
- Feature branch 式的資料管理
- 快速的 database fork

---

## 5. ROW vs Traditional COW vs WAL

### 5.1 I/O Pattern 比較

```
場景：修改一個資料區塊

─── Traditional COW Snapshot ───
  1. READ  原始區塊（從原位讀）
  2. WRITE 原始區塊到 snapshot 預留區域（保護舊資料）
  3. WRITE 新資料到原位（覆蓋）
  = 1 Read + 2 Writes = 3 I/O

─── ROW (Redirect-on-Write) ───
  1. WRITE 新資料到新位置
  2. UPDATE pointer（metadata 也 ROW，但批次處理）
  = 1 Write + metadata update = ~1-2 I/O

─── WAL (Write-Ahead Logging) ───
  1. WRITE log record 到 sequential log（循序追加）
  2. Later: WRITE actual data to final location（checkpoint / apply）
  = 1 Sequential Write + 1 Deferred Random Write = 2 I/O
     （但 log write 是循序的，很快）

─── In-Place Update (傳統) ───
  1. WRITE 新資料覆蓋原位
  = 1 Write = 1 I/O
     （但無 crash consistency，除非加上 journal/WAL）
```

**I/O Pattern 特性**：

| 方法 | Write Pattern | Read Pattern | 寫入放大 | 適合裝置 |
|------|--------------|-------------|---------|---------|
| Traditional COW | Random (3x) | Sequential (原位) | 高 (3x) | 不適合任何 |
| ROW | Random (1x) + metadata cascade | Random (碎片化) | 中 (1x + metadata) | SSD > HDD |
| WAL | Sequential (log) + Random (apply) | Sequential (若資料不動) | 中 (2x 但 log 是 sequential) | 適合 HDD/SSD |
| In-Place | Random (1x) | Sequential (原位) | 低 (1x) | N/A（無保護） |

### 5.2 Write Amplification 分析

```
Write Amplification Factor (WAF) = 實際寫入磁碟的量 / 應用程式請求的寫入量

ROW 的 Write Amplification 來源：

1. Metadata Cascade
   修改 1 個 data block → 需要更新 N 層 metadata block
   N = tree depth（通常 3-6 層）
   每層一個 block（4KB - 128KB）
   
   例：修改 8KB data，tree depth = 4
   WAF = (8KB data + 4 × 16KB metadata) / 8KB = 9x

2. Recordsize Mismatch（ZFS 特有）
   ZFS recordsize=128KB，但只修改 8KB
   → 需要讀取整個 128KB record，修改 8KB，重寫整個 128KB
   WAF = 128KB / 8KB = 16x（未計算 metadata）

3. Compression 的雙面效果
   壓縮可以降低實際寫入量 → 降低 WAF
   但壓縮後 block 大小變化可能需要更多 metadata 更新

4. 對比 WAL
   WAL 的 WAF = 2x（寫 log 1 次 + apply 1 次）
   但 log 是循序寫入，對 HDD 更友好
   
5. 對比傳統 COW
   傳統 COW = 3x（讀舊 + 寫舊到 snapshot + 寫新到原位）
```

**ZFS 的 WAF 實際數據**：
- 大型循序寫入：WAF ≈ 1.1-1.3（metadata overhead 很小）
- 8KB 隨機寫入 + recordsize=128KB：WAF 可達 16x+
- 8KB 隨機寫入 + recordsize=8KB + compression=off：WAF ≈ 2-4x（metadata cascade）
- 8KB 隨機寫入 + recordsize=128KB + compression=lz4：WAF 可降低（因壓縮補償）

### 5.3 Crash Consistency 比較

| 方法 | Crash Consistency 保證 | 恢復機制 | 恢復速度 |
|------|----------------------|---------|---------|
| **ROW** | 永遠一致。Crash 時回到最後一個 committed 的 root pointer（uberblock / superblock） | 掃描 uberblock ring buffer，找最新且 checksum 正確的。不需 fsck | **秒級**（不論 filesystem 大小） |
| **Traditional COW** | 需要額外機制。COW 本身不保證 metadata + data 的原子性 | 取決於實作 | 取決於實作 |
| **WAL** | 一致。Crash 後 replay log 中已 commit 但未 apply 的記錄 | Replay WAL（ARIES 演算法：分析 → redo → undo） | **分鐘級**（與 log 大小成正比） |
| **Journal (ext4)** | 一致（metadata journal）或可選（data journal）。只保護 journal 範圍內的操作 | Replay journal | **秒級**（journal 通常不大） |

**ROW Crash Consistency 的優雅之處**：
```
Crash 發生在 TXG sync 中間：
  - 新 data blocks 已寫入，但 uberblock 尚未更新
  - → 新 data blocks 成為 "orphaned" blocks
  - → 重啟後從舊 uberblock 開始，orphaned blocks 自動成為 free space
  - → 不需要 fsck，不需要 journal replay
  - → 代價：丟失最近一個 TXG 的資料（通常 5-30 秒）
  
  但若有 ZIL/SLOG：
  - 同步寫入的 intent log 在 SLOG 上是持久化的
  - 重啟後 replay ZIL → 恢復同步寫入的資料
  - 只丟失最近的異步寫入
```

### 5.4 何時選擇哪種方法

| 場景 | 推薦方法 | 原因 |
|------|---------|------|
| NAS / 檔案伺服器 | **ROW (ZFS/Btrfs)** | Snapshot、checksum、彈性佈局 |
| OLTP 資料庫 | **WAL** | 循序寫入效能好、write amplification 低 |
| 虛擬化儲存 | **ROW (ZFS zvol)** | Thin provisioning、snapshot、clone |
| 嵌入式系統 | **WAL / Journal** | 記憶體有限，ROW 的 metadata 開銷太大 |
| High-write-rate random I/O | **WAL** | ROW 的碎片化在此場景問題最大 |
| 資料保護為首要 | **ROW (ZFS)** | End-to-end checksum、self-healing |
| SSD-only 環境 | **ROW** | 碎片化對 SSD 影響小，ROW 的隨機寫入不是瓶頸 |
| Archive / cold storage | **ROW** | Snapshot 管理方便、compression 效果好 |

---

## 6. ROW 進階議題

### 6.1 Deduplication with ROW（ZFS Dedup）

ZFS dedup 結合 ROW 運作：

```
Dedup 寫入流程：
  1. 應用寫入 block X
  2. ZFS 計算 X 的 hash（SHA-256 / skein）
  3. 查詢 DDT (Dedup Table)：此 hash 是否已存在？
     ├── 不存在 → 正常 ROW 寫入，DDT 新增 entry
     └── 存在 → 不寫入 data block，增加 reference count
  4. Block pointer 指向已存在的 block（或新寫入的 block）

DDT (Dedup Table) 結構：
  ┌───────────┬──────────────┬──────────┐
  │  Hash     │ Block Pointer │ Ref Count│
  ├───────────┼──────────────┼──────────┤
  │ SHA256-1  │ DVA(vdev,off)│    3     │
  │ SHA256-2  │ DVA(vdev,off)│    1     │
  │ ...       │ ...          │   ...    │
  └───────────┴──────────────┴──────────┘
```

**Classic Dedup 的問題**：
- DDT 必須在記憶體中（ARC），否則每次寫入都要做 random read → 效能災難
- DDT 大小 = block 數量 × ~320 bytes（每個 entry）
- 1TB 資料 / 128KB recordsize = ~8M blocks × 320B ≈ **2.5GB DDT in RAM**
- Pool 越大，DDT 越大，直到超出 ARC 容量 → catastrophic performance degradation

**Fast Dedup（OpenZFS 新方案）**：
- **DDT Log**：不再每次寫入都立即更新 DDT，而是先追加到 log
- **Prefetch**：批次查詢 DDT，減少隨機 I/O
- **Pruning**：自動清理 refcount=1 的 DDT entry（非重複的 block 不需要在 DDT 中）
- **Quota**：限制 DDT 大小，超出後新 block 不做 dedup
- 效能改善：Fast dedup 寫入速度比 classic 快約 41%

**Dedup 的適用場景**：
- VM images（多個 VM 基於同一 base image）
- Backup storage（多個備份有大量重複）
- **不適用**：一般 NAS / 檔案伺服器（dedup ratio 低，overhead 高）

### 6.2 Transparent Compression

ROW 與 compression 天然搭配：

```
ROW + Compression 寫入流程：
  1. 應用寫入 logical block（128KB recordsize）
  2. ZFS 壓縮（lz4 / zstd / gzip）
  3. 壓縮後大小 = physical size（如 48KB）
  4. ROW：將 48KB 寫到新位置
  5. Block pointer 記錄：lsize=128KB, psize=48KB, compression=lz4
  6. 讀取時自動解壓縮
```

**Compression 與 ROW 的協同效應**：
- ROW 寫到新位置 → 反正要新分配空間 → 壓縮不增加額外成本
- In-place update 的檔案系統做 compression 更複雜（壓縮後大小不同，可能需要搬移）
- ROW + compression 可以**減少** write amplification：寫入更少的 physical bytes

**Recordsize 與 Compression 的交互影響**：

| Recordsize | Compression Ratio | 實際節省 | 說明 |
|------------|-------------------|---------|------|
| 128KB | 2:1 (壓到 64KB) | **有節省** | 64KB < 128KB，少寫 64KB |
| 128KB | 1.3:1 (壓到 98KB) | **有節省** | 98KB 需要的 ashift blocks 比 128KB 少 |
| 16KB (ashift=13, 8KB blocks) | 1.3:1 (壓到 12.3KB) | **無節省** | 仍需 2 個 8KB block，ZFS 不壓縮此 record |
| 1MB | 3:1 (壓到 333KB) | **大幅節省** | 大 recordsize + 好壓縮 = 最佳效果 |

**演算法建議**：
- **LZ4**（預設推薦）：極低 CPU overhead，壓縮速度 > 1GB/s。壓縮比較低但幾乎無效能影響
- **Zstd**（進階）：壓縮比好很多（接近 gzip），CPU overhead 中等。Level 1-3 適合一般用途
- **Gzip**：壓縮比最高，CPU overhead 最大。只適合 archival / cold data

### 6.3 RAID with ROW

#### ZFS RAIDZ vs Traditional RAID

```
Traditional RAID-5 Write Hole：
  Disk 0: [D0_new]  ← 寫入成功
  Disk 1: [D1_old]  ← 還沒來得及寫
  Disk 2: [P_new]   ← Parity 已更新
  → 斷電！
  → 重啟後 D1_old + P_new 不一致
  → RAID 不知道哪個是對的 → 資料損毀

ZFS RAIDZ 如何避免 Write Hole：
  1. RAIDZ 使用 variable-width stripes（不是固定 stripe size）
  2. 所有寫入都是 ROW → 不覆蓋現有 stripe
  3. 每個 stripe 是完整的一次寫入（data + parity 一起寫）
  4. TXG commit 確保只有完整的 stripe 被 referenced
  5. Crash 時：未完成的 stripe 不被 uberblock reference → 自動忽略
  → 永遠不會有 parity 不一致的問題
```

**RAIDZ 層級**：

| Level | 名稱 | 容忍磁碟故障數 | 等價 |
|-------|------|-------------|------|
| RAIDZ1 | Single parity | 1 | ~RAID-5 |
| RAIDZ2 | Double parity | 2 | ~RAID-6 |
| RAIDZ3 | Triple parity | 3 | 無等價 |

**RAIDZ 的 ROW 特有特性**：
- Variable-width stripe：每個 write 的 stripe 寬度可以不同，避免 "small write penalty"
- Self-healing：讀取時驗證 checksum，若損毀可從 parity 重建

#### Btrfs RAID

- Btrfs RAID 1/10 是穩定可用的
- Btrfs RAID 5/6 仍然存在 **write hole 問題**（截至 2025 年）
- 原因：Btrfs 的 RAID 5/6 實作未能完全利用 COW 來避免 write hole
- **建議**：生產環境不使用 Btrfs RAID 5/6

### 6.4 ROW in Virtualization（QCOW2）

QCOW2（QEMU Copy-On-Write v2）是虛擬化場景中的 ROW 實作：

```
QCOW2 結構：
┌──────────────┐
│   Header     │  ← magic, version, backing file path
├──────────────┤
│   L1 Table   │  ← 第一層地址映射（variable size）
├──────────────┤
│   L2 Tables  │  ← 第二層地址映射（each = 1 cluster）
├──────────────┤
│   Data       │  ← 實際的 guest data clusters
│   Clusters   │
├──────────────┤
│   Refcount   │  ← 每個 cluster 的 reference count
│   Table      │     （用於 snapshot 和 internal copy-on-write）
└──────────────┘

地址翻譯：
  Guest address → L1 index → L2 table offset → L2 index → Host cluster offset
                  (高位)                        (低位)

Backing File + COW：
  ┌──────────────┐
  │  base.qcow2  │  ← Base image（read-only）
  └──────┬───────┘
         │ backing_file
  ┌──────▼───────┐
  │ overlay.qcow2│  ← 只記錄差異（COW）
  └──────────────┘
  
  讀取 cluster X：
    overlay 有映射 → 從 overlay 讀
    overlay 無映射 → 從 base 讀
  
  寫入 cluster X：
    overlay 已有映射 → 直接寫入 overlay
    overlay 無映射 → 從 base 讀取 cluster → 寫入 overlay → 更新 L2 映射
```

**QCOW2 + ZFS 的組合使用**：
- 在 ZFS 上存放 QCOW2 images = ROW on ROW
- ZFS 的 snapshot 可以替代 QCOW2 的 snapshot 功能
- 建議：使用 ZFS zvol（raw block device）+ qcow2 格式，或直接用 ZFS snapshot

### 6.5 ROW in Databases（LMDB）

LMDB (Lightning Memory-Mapped Database) 使用 ROW B+ Tree：

```
LMDB 設計：
┌─────────────────────────────────┐
│        Memory-mapped file       │
│  ┌──────────┐  ┌──────────┐    │
│  │  Meta 0  │  │  Meta 1  │    │  ← 兩個 meta page 交替使用
│  │ (root ptr)│  │ (root ptr)│    │
│  └──────────┘  └──────────┘    │
│                                 │
│  ┌──────────┐  ┌──────────┐    │
│  │  B+ Tree │  │Free Page │    │  ← Data tree + Freelist tree
│  │  Pages   │  │  Tree    │    │
│  └──────────┘  └──────────┘    │
└─────────────────────────────────┘

寫入流程（Shadow Paging / COW B+ Tree）：
  1. 讀取要修改的 leaf page
  2. COW：將修改後的 leaf 寫到新位置（free page）
  3. Parent page 也 COW（更新 child pointer）
  4. 一路 COW 到 root
  5. 新 root pointer 寫入 meta page（交替使用 Meta 0/1）
  6. fsync() 確保持久化
  → 原子性 commit！

為什麼不需要 WAL：
  - 舊的 meta page 指向舊的 tree → crash 後自動恢復
  - 新的 meta page 指向新的 tree → 只在完全寫入後才切換
  - 任何時刻 crash，都有完整一致的 tree 可用
```

**LMDB 的 ROW 特點**：
- 單一 memory-mapped 文件，整個資料庫就是一個 mmap 區域
- 讀取完全 lock-free（MVCC through COW）
- 單一 writer（避免複雜的並發控制）
- 不做 garbage collection（free page tree 追蹤可用頁面）
- 不需要 compaction、不需要 WAL、不需要 background cleanup

---

## 7. ROW 的限制與反面案例

### 7.1 不適合的 Workload

| Workload | 問題 | 嚴重程度 |
|----------|------|---------|
| **大量小型隨機寫入** | 每次寫入觸發 metadata cascade；碎片化快速累積 | 高 |
| **Database WAL files** | 頻繁的 append + fsync → TXG 頻繁 commit → 高 overhead | 中~高 |
| **VM images on HDD** | Guest OS 的隨機寫入 + ROW 碎片化 + HDD seek = 效能災難 | 高（HDD）|
| **Torrent / P2P 下載** | 大量隨機寫入到檔案的不同位置 → 極度碎片化 | 高 |
| **Real-time / 低延遲需求** | TXG sync 可能造成周期性延遲 spike | 中 |
| **超大單檔頻繁修改** | 如大型資料庫檔案 → recordsize mismatch + WAF 高 | 中~高 |

### 7.2 Database-on-ZFS/Btrfs Tuning

在 ROW 檔案系統上跑資料庫是常見但需要精心調整的場景：

#### PostgreSQL on ZFS — 調校建議

```
ZFS Dataset 設定：
  # Data dataset
  zfs set recordsize=128K pool/pgdata       # 或 32K/64K 平衡 WAF 和壓縮
  zfs set compression=lz4 pool/pgdata       # 幾乎免費的壓縮
  zfs set atime=off pool/pgdata             # 停用 access time 更新
  zfs set xattr=sa pool/pgdata              # extended attributes 存在 inode
  zfs set logbias=latency pool/pgdata       # 偏好低延遲

  # WAL dataset（分離）
  zfs set recordsize=128K pool/pgwal        # WAL 是循序的，大 recordsize ok
  zfs set compression=lz4 pool/pgwal
  zfs set logbias=latency pool/pgwal

PostgreSQL 設定：
  full_page_writes = off     # ZFS ROW 不會 partial write → 不需要
  wal_init_zero = off        # 不需要預先 zero-fill WAL files
```

**核心矛盾與解法**：
- **問題**：PostgreSQL 用 8KB page，ZFS 預設 recordsize=128KB → 修改 1 page = 讀寫整個 128KB record
- **舊建議**：`recordsize=8KB` → 減少 WAF，但壓縮效果大幅降低
- **現代建議**：保持 `recordsize=128KB` + `compression=lz4` → 壓縮帶來的空間節省彌補 WAF 的開銷
- **進階**：`recordsize=32KB` 或 `64KB` 是折衷選擇

#### MySQL/InnoDB on ZFS

```
ZFS 設定：
  zfs set recordsize=16K pool/mysql    # InnoDB 用 16KB page
  zfs set primarycache=metadata pool/mysql  # InnoDB 有自己的 buffer pool
  zfs set compression=lz4 pool/mysql
```

#### Btrfs 上的 Database

- Btrfs 對小型隨機 I/O 的效能不如 ZFS（extX/XFS 更佳）
- 若必須使用，建議：
  - 對 database 目錄設置 `chattr +C`（disable COW for that directory）
  - 或使用 `nodatacow` mount option
  - 代價：失去 checksum 和 snapshot 的資料保護

### 7.3 Write Cliff 問題

"Write Cliff" 是 ROW 檔案系統在特定條件下效能急劇下降的現象：

```
效能曲線（conceptual）：

Throughput
  │
  │  ─────────────────────╮
  │                        ╲
  │                         ╲  ← Write Cliff
  │                          ╲
  │                           ╲────────────
  │
  └────────────────────────────────────────→
  0%        50%        80%  90% 95%    100%
                  Pool Usage

觸發條件：
  1. Pool 使用率 > 80-90%
  2. 嚴重碎片化（fragmentation > 50-60%）
  3. 大量小型隨機寫入
  4. 多個 snapshot 佔用空間
```

**Write Cliff 的內部機制**：
1. **Metaslab selection 困難**：所有 metaslab 都高度碎片化，allocator 耗費大量 CPU 搜尋可用空間
2. **Best-fit allocation 開銷**：碎片化觸發 best-fit 模式，每次分配都要遍歷 space map
3. **Gang block fallback**：找不到連續空間 → 建立 gang block → 更多 metadata → 更多 I/O
4. **TXG sync 延長**：分配困難導致 TXG sync 時間拉長 → 延遲 spike
5. **惡性循環**：更多碎片化 → 更多 metadata → 更多寫入 → 更多碎片化

**避免 Write Cliff 的最佳實踐**：
- **保持 pool 使用率 < 80%**（最保守建議：< 70%）
- 定期清理不需要的 snapshot
- 監控 `zpool list -v` 的 `FRAG` 欄位
- 若碎片化嚴重，考慮 `zpool replace` 或 `zfs send | zfs receive` 重建

### 7.4 何時不該使用 ROW

| 場景 | 更好的選擇 | 原因 |
|------|----------|------|
| **極低延遲需求** | ext4 / XFS | ROW 的 TXG sync 和 metadata cascade 會引入延遲 |
| **小型嵌入式裝置** | ext4 / F2FS | ROW 的記憶體開銷太大（ARC、space maps） |
| **HDD + 大量隨機寫入** | XFS + hardware RAID | ROW 碎片化 + HDD seek = 效能災難 |
| **不需要 snapshot / checksum** | ext4 / XFS | ROW 的複雜度和開銷沒有帶來價值 |
| **高度受限的 SSD** | ext4 / F2FS | ROW 的 write amplification 加速 SSD 磨損 |
| **已有外部資料保護** | 任何簡單 FS | 如果 application layer 已有 checksum + replication，FS 層不需要 |
| **Write-mostly workload + HDD** | XFS + journal | HDD 上的循序寫入（journal/WAL）遠好於 ROW 的隨機寫入 |

**總結判斷框架**：

```
需要 snapshot / clone?
  ├── Yes → ROW (ZFS/Btrfs)
  └── No
       需要 end-to-end data integrity?
       ├── Yes → ROW (ZFS)
       └── No
            Write-heavy random I/O on HDD?
            ├── Yes → XFS / ext4 + RAID
            └── No
                 SSD-based storage?
                 ├── Yes → ROW 可以考慮（碎片化影響小）
                 └── No
                      → XFS / ext4（簡單、成熟、低 overhead）
```

---

## 8. 參考資料

### ZFS Architecture & Internals
- [OpenZFS DeepWiki — Transaction Groups and ZIL](https://deepwiki.com/openzfs/zfs/5.4-transaction-groups-and-zil)
- [OpenZFS DeepWiki — SPA (Storage Pool Allocator)](https://deepwiki.com/openzfs/zfs/3.4-spa-(storage-pool-allocator))
- [OpenZFS DeepWiki — VDEVs and Metaslabs](https://deepwiki.com/openzfs/zfs/5.3-virtual-devices-(vdevs)-and-metaslabs)
- [What ZFS Block Pointers Are and What's in Them](https://utcc.utoronto.ca/~cks/space/blog/solaris/ZFSBlockPointers)
- [OpenZFS Documentation — Read Write Lecture](https://openzfs.org/wiki/Documentation/Read_Write_Lecture)
- [ZFS Features & Concepts (Lustre Wiki PDF)](https://wiki.lustre.org/images/4/49/Beijing-2010.2-ZFS_overview_3.1_Dilger.pdf)
- [How ZFS Snapshots Really Work — Matt Ahrens, BSDCan 2019](https://papers.freebsd.org/2019/BSDCan/ahrens-How_ZFS_Snapshots_Really_Work.files/ahrens-How_ZFS_Snapshots_Really_Work.pdf)

### ZFS Performance & Tuning
- [OpenZFS Workload Tuning Documentation](https://openzfs.github.io/openzfs-docs/Performance%20and%20Tuning/Workload%20Tuning.html)
- [ZFS Fragmentation: Long-term Solutions (GitHub Issue #3582)](https://github.com/openzfs/zfs/issues/3582)
- [Effects of ZFS Fragmentation on Underlying Storage (Kent University)](https://blogs.kent.ac.uk/unseenit/effects-of-zfs-fragmentation-on-underlying-storage/)
- [ZFS Fragmentation Performance Issue Mitigation (TrueNAS)](https://www.truenas.com/community/threads/zfs-fragmentation-performance-issue-mitigation.93899/)
- [ZFS Write Performance and Impact of Fragmentation](https://delphix68.rssing.com/chan-32218646/article7.html)
- [OpenZFS Understanding Transparent Compression (Klara Systems)](https://klarasystems.com/articles/openzfs1-understanding-transparent-compression/)
- [Zstandard Compression in OpenZFS (FreeBSD Foundation)](https://freebsdfoundation.org/wp-content/uploads/2021/05/Zstandard-Compression-in-OpenZFS.pdf)
- [ZFS Optimization Success Stories (Klara Systems)](https://klarasystems.com/articles/zfs-optimization-success-stories/)
- [ZFS Network Management — Metaslabs and Space Maps](http://netmgt.blogspot.com/2012/11/zfs-metaslabs-and-space-maps.html)

### ZFS Deduplication
- [OpenZFS Fast Dedup (Klara Systems)](https://klarasystems.com/articles/introducing-openzfs-fast-dedup/)
- [OpenZFS Dedup Is Good Now and You Shouldn't Use It](https://despairlabs.com/blog/posts/2024-10-27-openzfs-dedup-is-good-dont-use-it/)
- [ZFS Deduplication (TrueNAS Reference)](https://www.truenas.com/docs/references/zfsdeduplication/)
- [ZFS DDT and ZAP (DeepWiki)](https://deepwiki.com/truenas/zfs/3.5-deduplication-(ddt)-and-zap-attribute-processor)

### ZFS Snapshots & Space Management
- [Advanced ZFS Dataset Management: Snapshots, Clones, and Bookmarks (Klara Systems)](https://klarasystems.com/articles/advanced-zfs-dataset-management/)
- [Why ZFS Reports Less Space: Space Accounting Explained (Klara Systems)](https://klarasystems.com/articles/why-zfs-reports-less-available-space-space-accounting-explained/)

### Btrfs
- [Btrfs Design Documentation](https://btrfs.readthedocs.io/en/latest/dev/dev-btrfs-design.html)
- [Btrfs B-trees Documentation](https://btrfs.readthedocs.io/en/latest/dev/dev-btrees.html)
- [Btrfs Internals for Interns](https://internals-for-interns.com/posts/btrfs-filesystem/)
- [Btrfs Defragmentation Documentation](https://btrfs.readthedocs.io/en/latest/Defragmentation.html)
- [Btrfs Subvolumes Documentation](https://btrfs.readthedocs.io/en/latest/Subvolumes.html)
- [Btrfs Wikipedia](https://en.wikipedia.org/wiki/Btrfs)

### NetApp WAFL
- [Write Anywhere File Layout — Wikipedia](https://en.wikipedia.org/wiki/Write_Anywhere_File_Layout)
- [NetApp WAFL, NVRAM and System Memory Cache (FlackBox)](https://www.flackbox.com/netapp-wafl-nvram-system-memory-cache)
- [How Data ONTAP Caches, Assembles and Writes Data](https://bitpushr.wordpress.com/2014/07/28/how-data-ontap-caches-assembles-and-writes-data/)
- [WAFL Technical Report — Princeton CS](https://www.cs.princeton.edu/courses/archive/fall04/cos318/docs/netapp.pdf)
- [What is Consistency Point and Why Does NetApp Use It](https://kb.netapp.com/on-prem/ontap/Perf/Perf-KBs/What_is_Consistency_Point_and_why_does_NetApp_use_it)

### Microsoft ReFS
- [Resilient File System Overview (Microsoft Learn)](https://learn.microsoft.com/en-us/windows-server/storage/refs/refs-overview)
- [ReFS Integrity Streams (Microsoft Learn)](https://learn.microsoft.com/en-us/windows-server/storage/refs/integrity-streams)
- [Block Cloning on ReFS (Microsoft Learn)](https://learn.microsoft.com/en-us/windows-server/storage/refs/block-cloning)

### NILFS2
- [NILFS2 Linux Kernel Documentation](https://docs.kernel.org/filesystems/nilfs2.html)
- [NILFS Wikipedia](https://en.wikipedia.org/wiki/NILFS)
- [What is NILFS?](https://nilfs.sourceforge.io/en/about_nilfs.html)

### F2FS
- [F2FS Linux Kernel Documentation](https://docs.kernel.org/filesystems/f2fs.html)
- [F2FS: A New File System for Flash Storage (USENIX FAST '15)](https://www.usenix.org/system/files/conference/fast15/fast15-paper-lee.pdf)
- [F2FS: A New File System for Flash Storage — The Morning Paper](https://blog.acolyer.org/2015/02/26/f2fs-a-new-file-system-for-flash-storage/)

### ROW vs COW vs WAL
- [Snapshot 101: Copy-on-Write vs Redirect-on-Write (StorageSwiss)](https://storageswiss.com/2016/04/01/snapshot-101-copy-on-write-vs-redirect-on-write/)
- [ZFS & Btrfs are ROW not COW (InfoTinks)](http://infotinks.com/zfs-btrfs-are-row-not-cow-redirect-on-write-not-copy-on-write/)
- [Copy-on-Write — Wikipedia](https://en.wikipedia.org/wiki/Copy-on-write)
- [Write-Ahead Logging — Wikipedia](https://en.wikipedia.org/wiki/Write-ahead_logging)

### RAIDZ & Write Hole
- [ZFS vs Btrfs Architecture Comparison (QNAP Blog)](https://blog.qnap.com/en/core-architecture-and-reliability-comparison-between-zfs-and-btrfs-technical-features-and-real-world-deployment-considerations/)
- [ZFS RAIDZ vs Traditional RAID (Klennet)](https://www.klennet.com/notes/2019-07-04-raid5-vs-raidz.aspx)
- [Write Hole Phenomenon in RAID (RAID Recovery Guide)](https://www.raid-recovery-guide.com/raid5-write-hole.aspx)

### QCOW2 (Virtualization)
- [QCOW2 Format In-Depth (DeepWiki)](https://deepwiki.com/Xilinx/qemu/5.3-qcow2-format-in-depth)
- [QCOW2 Image File Format (QEMU Docs)](https://www.qemu.org/docs/master/interop/qcow2.html)
- [Storage Formats for Virtual Disks (Red Hat)](https://access.redhat.com/documentation/en-us/red_hat_virtualization/4.3/html/technical_reference/qcow2)

### LMDB
- [How LMDB Works (Thomas Wang)](https://xgwang.me/posts/how-lmdb-works/)
- [LMDB — Database of Databases](https://dbdb.io/db/lmdb)
- [Getting Down and Dirty with LMDB (Symas)](https://www.symas.com/post/getting-down-and-dirty-with-lmdb)

### Database on ROW Filesystems
- [Tuning Postgres + ZFS (GitHub Gist)](https://gist.github.com/saurabhnanda/5258207935bf23cd112be292d22f00d5)
- [Everything on Optimizing Postgres on ZFS](https://vadosware.io/post/everything-ive-seen-on-optimizing-postgres-on-zfs-on-linux/)
- [PostgreSQL and ZFS Filesystem Tuning](https://bun.uptrace.dev/postgres/tuning-zfs-aws-ebs.html)
- [Taking a Look at Btrfs for MySQL (Percona)](https://www.percona.com/blog/taking-a-look-at-btrfs-for-mysql/)
- [Benchmark of Ext4, XFS, Btrfs, ZFS with PostgreSQL](https://www.dimoulis.net/posts/benchmark-of-postgresql-with-ext4-xfs-btrfs-zfs/)
