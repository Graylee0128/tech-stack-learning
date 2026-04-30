# Copy on Write (COW) 及相關機制完整比較

> COW 是一種「延遲複製」的最佳化策略，廣泛應用於 OS 核心、檔案系統、容器化、資料庫、程式語言等層面。本文整理 COW 及所有相關機制的原理、應用場景與比較。

## 目錄

- [1. COW (Copy on Write)](#1-cow-copy-on-write)
  - [1.1 OS Kernel 層：fork() 與 mmap](#11-os-kernel-層fork-與-mmap)
  - [1.2 檔案系統層：Btrfs、ZFS、overlay2](#12-檔案系統層btrfszfsoverlay2)
  - [1.3 程式語言層：Rust、Swift、Go](#13-程式語言層rustswiftgo)
- [2. 相關/對比機制](#2-相關對比機制)
  - [2.1 Eager Copy (Deep Copy)](#21-eager-copy-deep-copy)
  - [2.2 Reference Counting](#22-reference-counting)
  - [2.3 MVCC (Multi-Version Concurrency Control)](#23-mvcc-multi-version-concurrency-control)
  - [2.4 Structural Sharing](#24-structural-sharing)
  - [2.5 Memory-Mapped I/O (mmap)](#25-memory-mapped-io-mmap)
  - [2.6 Overlay Filesystem](#26-overlay-filesystem)
  - [2.7 Shadow Paging](#27-shadow-paging)
  - [2.8 Redirect-on-Write (ROW)](#28-redirect-on-write-row)
- [3. 關鍵比較表](#3-關鍵比較表)
- [4. 延伸閱讀](#4-延伸閱讀)

---

## 1. COW (Copy on Write)

### 核心原理

COW 是一種**延遲最佳化策略**：當資源被「複製」時，系統不立即複製，而是共享原始資料。**只有在某一方嘗試修改時，才真正建立副本。** 如果從未發生寫入，複製就永遠不會發生。

```
┌─────────┐     ┌─────────┐
│ Process A│     │ Process B│
│  (讀取)  │     │  (讀取)  │
└────┬─────┘     └────┬─────┘
     │                │
     └───────┬────────┘
             ▼
      ┌─────────────┐
      │  共享記憶體頁  │   ← 標記為 read-only
      │  (一份實體)   │
      └─────────────┘

         ── Process B 寫入 ──

┌─────────┐     ┌─────────┐
│ Process A│     │ Process B│
│  (讀取)  │     │  (讀寫)  │
└────┬─────┘     └────┬─────┘
     │                │
     ▼                ▼
┌─────────┐     ┌─────────┐
│  原始頁   │     │  複製頁   │   ← 寫入觸發 page fault → 核心複製
└─────────┘     └─────────┘
```

### 1.1 OS Kernel 層：fork() 與 mmap

#### fork() 的 COW 機制

1. 父行程呼叫 `fork()`，核心**不複製**父行程的實體記憶體頁
2. 核心將父行程的頁面映射到子行程的 page table，兩者的 PTE 都標記為 **read-only**
3. 當任一行程寫入共享頁時，觸發 **page fault**，核心的 `do_wp_page()` 處理器：
   - 分配新的實體頁面
   - 複製共享頁面的內容
   - 更新寫入行程的 PTE 指向新頁面（設為可寫）
   - 另一行程的 PTE 仍指向原始頁面
4. 如果另一行程後來寫入同一頁且 refcount = 1，核心直接設為可寫（不需複製）

**經典應用：`fork() + exec()`**
- 子行程 fork 後立即 exec 載入新程式，父行程的記憶體頁從未被寫入
- COW 避免了完全不必要的記憶體複製 → 極快的行程建立

#### mmap 與 COW 的關係

| 映射類型 | COW 行為 |
|---------|---------|
| `MAP_PRIVATE`（私有映射） | **使用 COW**：讀取來自 page cache，寫入觸發 COW 建立私有副本 |
| `MAP_SHARED`（共享映射） | **不使用 COW**：寫入直接進入 page cache，所有映射者可見 |

共享函式庫就是這樣運作的：多個行程共享 `.text` 段的相同實體頁面，COW 保護寫入。

> **安全案例 — Dirty COW (CVE-2016-5195)**
> Linux 核心 COW page fault 處理器中的 race condition 漏洞，允許本地權限提升。攻擊者利用權限檢查與複製執行之間的時間窗口，展示了 COW 實作的安全關鍵性。

### 1.2 檔案系統層：Btrfs、ZFS、overlay2

#### Btrfs COW

- 所有 metadata 和 data 儲存在 B-tree 中
- 修改區塊時，Btrfs 將新版本寫入**磁碟上的新位置**（永不覆寫原位）
- 修改從葉節點向上 COW：父指標需更新 → 父也被 COW → 一路到根節點
- 單一 superblock 寫入原子性切換檔案系統狀態（不需 journal replay）
- **Snapshot 幾乎瞬間完成**：只需複製根指標。Snapshot 和原始資料共享所有區塊，僅隨變更而分歧

#### ZFS COW

- 整個檔案系統建構為 **Merkle tree**，每個區塊包含子區塊的 checksum
- 所有寫入都到新位置，uberblock（根指標）原子性更新
- 內建 checksumming、snapshots、clones、send/receive replication
- COW 直接實現事務語意，不需獨立的 journal

#### Docker overlay2

```
Container View (unified)        ← 使用者看到的合併視圖
        │
   ┌────┴────┐
   ▼         ▼
upperdir    lowerdir (read-only)
(可寫層)    (映像層，可多層堆疊)
```

- Image layers 為唯讀（lowerdir），容器獲得薄的可寫層（upperdir）
- **讀取路徑**：直接從 lower layer 提供檔案，無需複製
- **寫入路徑（COW）**：首次修改時，**整個檔案**從 lowerdir 複製到 upperdir（"copy-up"），再在 upper layer 中就地修改
- 支援 **page cache sharing**：多個容器讀取相同檔案共享單一 page cache 條目

### 1.3 程式語言層：Rust、Swift、Go

#### Rust `Cow<T>`（Clone on Write）

```rust
use std::borrow::Cow;

fn process(input: Cow<str>) -> Cow<str> {
    if input.contains("bad") {
        // 需要修改 → 觸發 clone，轉為 Owned
        let cleaned = input.replace("bad", "good");
        Cow::Owned(cleaned)
    } else {
        // 不需修改 → 保持 Borrowed，零成本
        input
    }
}
```

- 列舉型別，兩個變體：`Borrowed(&'a T)` 和 `Owned(T)`
- 呼叫 `.to_mut()` 在 Borrowed 時 clone 資料並切換為 Owned
- 注意：Rust 的 `Cow` 是 "clone on write"（用 `Clone` trait），不是 "copy on write"（`Copy` trait）

#### Swift 值型別與 COW

```swift
var arr1 = [1, 2, 3]    // 底層 buffer refcount = 1
var arr2 = arr1          // 共享 buffer，refcount = 2（便宜）
arr2.append(4)           // refcount > 1 → 觸發 COW，arr2 獲得獨立副本
```

- `Array`、`Dictionary`、`Set`、`String` 都是 value types，內部使用 COW
- 賦值時只共享 buffer reference（便宜），mutation 且 refcount > 1 時才深度複製

#### Go Slices（無自動 COW）

```go
original := []int{1, 2, 3, 4, 5}
slice := original[1:3]   // 共享底層 array，不複製
slice[0] = 99            // ⚠️ 直接修改共享 array！original[1] 也變成 99
```

- Go slice 透過 header struct（pointer、length、capacity）共享底層 array
- **Go 沒有自動 COW**：切片操作不複製，append 超過 capacity 才分配新 array
- 需要手動 `copy()` 才能安全隔離

---

## 2. 相關/對比機制

### 2.1 Eager Copy (Deep Copy)

**原理**：複製時立即複製整個資料結構的每一個 byte，不論是否會被修改。

| 出現場景 | 範例 |
|---------|------|
| Python | `copy.deepcopy()` |
| JavaScript | `structuredClone()` |
| C | `memcpy()` |
| 資料庫 | `CREATE TABLE ... AS SELECT` |

| 優點 | 缺點 |
|------|------|
| 完全隔離，無共享狀態 | 前期成本高（時間 + 記憶體） |
| 無 page fault 開銷 | 若副本幾乎不修改則浪費 |
| 可預測的延遲 | 大資料結構耗時 |

**vs COW 的選擇**：
- 大部分資料會被修改 → Eager Copy
- 需要可預測延遲（無突發 page fault）→ Eager Copy
- 資料量小，複製成本可忽略 → Eager Copy
- 讀取為主，很少修改 → COW
- 記憶體受限 → COW
- `fork() + exec()` 場景 → COW 完勝

### 2.2 Reference Counting

**原理**：每個物件維護一個計數器，記錄指向它的引用數量。建立引用時 +1，銷毀時 -1。計數歸零時立即釋放。

| 出現場景 | 實作 |
|---------|------|
| Swift | ARC (Automatic Reference Counting) |
| Rust | `Rc<T>` / `Arc<T>`（原子引用計數） |
| Python | CPython 物件系統（refcount + cycle collector） |
| C++ | `std::shared_ptr` |
| 檔案系統 | inode link count、ZFS/Btrfs extent refcount |

**與 COW 的關係**：**互補機制**。COW 使用 reference count 來判斷：
- refcount = 1 → 獨佔，可直接寫入（不需複製）
- refcount > 1 → 共享中，寫入需先複製

Swift 的 COW 實作明確呼叫 `isKnownUniquelyReferenced()` 來做此判斷。

### 2.3 MVCC (Multi-Version Concurrency Control)

**原理**：資料庫維護每筆資料的多個版本，讀取者看到一致的 snapshot，不阻擋寫入者；寫入者建立新版本，不阻擋讀取者。

#### PostgreSQL 實作

```
Transaction 100: INSERT row → xmin=100, xmax=∞
Transaction 200: UPDATE row → 舊 tuple xmax=200, 新 tuple xmin=200
Transaction 150 (在 200 commit 前開始): 只看到 xmin=100 的版本
```

- 每筆 row 有 `xmin`（建立的 transaction ID）和 `xmax`（刪除/更新的 transaction ID）
- `UPDATE` 在 table heap 中建立**新的 row 版本**，舊版本保留到 `VACUUM` 回收
- 缺點：dead tuples 累積，需定期 VACUUM

#### MySQL InnoDB 實作

- 聚集索引只保留最新版本
- 舊版本存在 **undo logs**（rollback segments）中
- 重建舊版本需逆向套用 undo log 條目
- purge threads 在無交易需要時清理 undo logs

**與 COW 的比較**：

| 面向 | COW | MVCC |
|------|-----|------|
| 主要目的 | 記憶體/儲存效率 | 並行控制（讀寫不互鎖） |
| 何時建立新版本 | 只在寫入共享資源時 | 每次寫入（每筆交易） |
| 誰看到舊版本 | 沒人（refcount=0 即釋放） | 並行讀取者（snapshot isolation） |
| 清理機制 | 立即（refcount 歸零時） | 延遲（VACUUM / purge） |
| 粒度 | 記憶體頁 / 磁碟區塊 | 資料庫 row / tuple |
| 交集 | ZFS/Btrfs snapshot = COW + 類 MVCC 行為 | PostgreSQL 新 tuple 保留舊版 ≈ COW 概念 |

### 2.4 Structural Sharing

**原理**：修改不可變資料結構時，建立新的根節點，**重用所有未修改的子樹**。只有從葉到根的修改路徑會新分配。

```
原始 tree:          修改 node D 後:
    A                    A'  ← 新
   / \                  / \
  B   C        →       B   C'  ← 新
 / \                  / \
D   E                D'  E     ← D' 是新的，E 被重用
                     (B 也被重用)
```

| 出現場景 | 說明 |
|---------|------|
| Clojure persistent vectors/maps | HAMT（Hash Array Mapped Trie），32-way 分支。更新一個元素只複製 ~log32(N) 個節點 |
| Immutable.js | JavaScript 實作，同 HAMT 方式 |
| **Git 物件模型** | commit → tree → blob。改一個檔案只建立新的 blob + 沿路的 tree，未改的子樹共享 |
| React/Redux | state 更新透過 structural sharing，啟用 `===` 引用相等性檢查 |

**與 COW 的比較**：

| 面向 | COW | Structural Sharing |
|------|-----|-------------------|
| 粒度 | 頁/區塊（粗粒度） | 樹節點（細粒度） |
| 觸發方式 | 硬體 page fault / fs write | 應用層級的更新操作 |
| 版本管理 | 二元（共享 or 已複製） | 完整歷史（所有版本可存取） |
| 適用場景 | 大型扁平資料（array、pages） | 階層式資料（tree、map） |
| 代表系統 | OS kernel、檔案系統 | 函式語言資料結構、Git |

### 2.5 Memory-Mapped I/O (mmap)

**原理**：將檔案直接映射到行程的虛擬位址空間。對該記憶體區域的讀寫透過 page fault 和 page cache 自動轉譯為檔案 I/O。

| 出現場景 | 範例 |
|---------|------|
| 資料庫 buffer pool | SQLite、LMDB |
| 共享函式庫載入 | `.so` / `.dll` 透過 mmap |
| IPC 共享記憶體 | `mmap` + `MAP_SHARED` |

**與 COW 的關係**：mmap 和 COW 緊密耦合。
- `MAP_PRIVATE` → 使用 COW（讀取共享 page cache，寫入觸發 COW 建立私有副本）
- `MAP_SHARED` → 不使用 COW（寫入直接到 page cache）
- `fork()` + `mmap` = 子行程繼承映射 + COW 語意

### 2.6 Overlay Filesystem

**原理**：將多個目錄疊加為單一掛載點。底層為唯讀，上層捕獲所有修改，呈現「聯合」視圖。

**與 COW 的比較**：OverlayFS 是**檔案層級**的 COW 機制。

| 面向 | Overlay FS (Docker) | Block-level COW (ZFS/Btrfs) |
|------|---------------------|-----------------------------|
| COW 粒度 | **整個檔案**（copy-up） | 區塊（通常 4KB-128KB） |
| 改 1 byte | 複製整個檔案到 upper layer | 只複製該區塊 |
| 複雜度 | 簡單 | 較複雜 |
| 效能特性 | 大檔案 copy-up 昂貴 | 更精細，但有碎片化問題 |

### 2.7 Shadow Paging

**原理**：維護兩個 page table——"shadow"（已提交的穩定狀態）和 "current"（進行中的修改）。寫入進入新頁面。Commit 時，current 原子性取代 shadow。Crash 時，shadow 提供即時恢復。

| 出現場景 | 範例 |
|---------|------|
| 早期資料庫 | System R |
| SQLite | rollback journal 模式（概念類似） |
| CouchDB | append-only B-tree + 原子性根指標切換 |
| LMDB | shadow paging + COW B-trees |

**與 COW 的關係**：Shadow paging **就是** COW 應用於資料庫頁面。

**vs WAL（Write-Ahead Logging）**：
| 面向 | Shadow Paging | WAL |
|------|--------------|-----|
| 寫入模式 | 隨機（新頁面散佈磁碟） | 循序（append to log） |
| 恢復 | 即時（用 shadow table） | 需 replay log（ARIES 演算法） |
| 效能 | 較差（碎片化） | 較佳（循序寫入） |
| 現代採用 | 較少（LMDB、CouchDB） | 主流 RDBMS |

### 2.8 Redirect-on-Write (ROW)

**原理**：不同於傳統 COW snapshot（讀舊區塊 → 複製到 snapshot 區 → 覆寫原位），ROW 將新資料直接寫到**新位置**，更新指標。舊區塊自然保留給 snapshot。

**I/O 比較**：

```
傳統 COW snapshot:
  1. Read（讀舊區塊）
  2. Write（複製到 snapshot 區）
  3. Write（寫新資料到原位）
  = 3 次 I/O

ROW:
  1. Read（讀舊區塊到 cache）
  2. Write（寫新資料到新位置）
  = 2 次 I/O（或 cache hit 時只 1 次 Write）
```

| 出現場景 | 範例 |
|---------|------|
| NetApp | ONTAP / WAFL (Write Anywhere File Layout) |
| ZFS、Btrfs | 所有寫入都是 ROW |
| Microsoft | ReFS |

> **注意**：ZFS、Btrfs 技術上是 ROW，但通常被稱為 "COW 檔案系統"。嚴格區分：
> - 傳統 COW = 複製舊資料到別處，然後覆寫原位
> - ROW = 寫新資料到新位置，保留舊資料原位

---

## 3. 關鍵比較表

### 全機制總覽

| 機制 | 核心思想 | 粒度 | 主要目的 | 代表系統 |
|------|---------|------|---------|---------|
| **COW** | 共享直到寫入才複製 | 頁/區塊 | 記憶體/儲存效率 | Linux fork()、Btrfs、ZFS |
| **Eager Copy** | 立即完整複製 | 完整物件 | 完全隔離 | memcpy、deepcopy |
| **Ref Counting** | 計數引用，歸零釋放 | 物件 | 記憶體管理 | Swift ARC、Rust Rc/Arc |
| **MVCC** | 多版本並存，snapshot 隔離 | Row/tuple | 並行控制 | PostgreSQL、MySQL InnoDB |
| **Structural Sharing** | 重用未修改子樹 | 樹節點 | 不可變資料效率 | Git、Clojure、Immutable.js |
| **mmap** | 檔案映射為記憶體 | 頁 | 零複製 I/O | 共享函式庫、LMDB |
| **Overlay FS** | 多層聯合掛載 | 整個檔案 | 容器隔離 | Docker overlay2 |
| **Shadow Paging** | 雙 page table 原子切換 | 資料庫頁 | 崩潰恢復 | LMDB、CouchDB |
| **ROW** | 新資料寫新位置 | 區塊 | 減少 snapshot I/O | ZFS、Btrfs、WAFL |

### Docker overlay2 vs OS fork() COW

| 面向 | Docker overlay2 | OS fork() |
|------|----------------|-----------|
| COW 粒度 | 整個檔案（copy-up） | 記憶體頁（通常 4KB） |
| 觸發時機 | 首次寫入 lower layer 的檔案 | 首次寫入共享頁面 |
| 共享方式 | 多容器共享 image layers | 父子行程共享記憶體頁 |
| 隔離方式 | 每個容器一個 upper layer | 每個行程獨立 page table |
| 效能關注點 | 大檔案 copy-up 昂貴 | 大量小寫入 = 大量 page fault |

---

## 4. 延伸閱讀

### OS / Kernel
- [Linux Kernel COW Fork (HackMD)](https://hackmd.io/@linD026/Linux-kernel-COW-fork)
- [Dirty COW 漏洞解析](https://chao-tic.github.io/blog/2017/05/24/dirty-cow)
- [Linux Page Faults, mmap, userfaultfd](https://www.shayon.dev/post/2026/65/linux-page-faults-mmap-and-userfaultfd/)

### 檔案系統
- [Btrfs Internals](https://internals-for-interns.com/posts/btrfs-filesystem/)
- [ZFS COW & Snapshots](https://www.open-e.com/blog/copy-on-write-snapshots/)
- [Snapshot 101: COW vs ROW](https://storageswiss.com/2016/04/01/snapshot-101-copy-on-write-vs-redirect-on-write/)

### Docker / 容器
- [Docker OverlayFS Storage Driver](https://docs.docker.com/engine/storage/drivers/overlayfs-driver/)
- [Deep Dive into Docker Union Filesystem](https://martinheinz.dev/blog/44)

### 程式語言
- [Rust Cow 官方文件](https://doc.rust-lang.org/std/borrow/enum.Cow.html)
- [Using Cow in Rust (LogRocket)](https://blog.logrocket.com/using-cow-rust-efficient-memory-utilization/)

### 資料庫
- [PostgreSQL MVCC 官方文件](https://www.postgresql.org/docs/current/mvcc-intro.html)
- [How MVCC Works (Vlad Mihalcea)](https://vladmihalcea.com/how-does-mvcc-multi-version-concurrency-control-work/)
- [Database Recovery: Shadow Paging to ARIES](https://sookocheff.com/post/databases/write-ahead-logging/)
