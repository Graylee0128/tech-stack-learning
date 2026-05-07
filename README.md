# Tech Stack Learning

這個 repo 已精簡成少量仍需要獨立保存的學習區。DevOps/SRE / Cloud Platform 主線已收斂到
[`devops-homelab`](../devops-homelab/)；TSL 不再維護 Docker、K8s、CI/CD、Terraform、SRE 等平行 topic。

## 2026-05 定位調整

TSL 現在只保留三類內容：

| 類型 | 定位 |
|---|---|
| OS / Linux Internals | 支撐 production troubleshooting 的底層知識 |
| AWS / Cloud 筆記 | 支撐 cloud architecture、networking、security、FinOps 的認證與知識庫 |
| Applied Algorithms for Systems | 只學對 systems engineering 有實務連結的演算法 |

不再把 Advanced Algorithms 當主線，也不在這裡另開 DevOps、Kubernetes、CI/CD、Terraform、SRE 平行學習路線。

## 保留目錄

```text
tech-stack-learning/
  README.md
  aws/                  # AWS 筆記與認證資料，先保留
  cheatsheet/           # 速查表候選區，先保留
  dsa/                  # Applied Algorithms for Systems，先保留
  operating-systems/    # OS、Linux、I/O、NFS / FTP 等基礎筆記，先保留
  projects/             # 舊專案與封存專案資料，reference only
    _archive/
      tde2.0/           # 舊專案資料，保留為履歷 / 架構參考
```

## AWS 與 Projects 生命週期

| 區域 | 定位 | 規則 |
|---|---|---|
| `aws/devops/` | AWS DevOps reference | 只作為知識庫，未來可抽取到 homelab / portfolio |
| `aws/network/` | Cloud networking active reference | 支撐 VPC、routing、DNS、hybrid networking、K8s networking |
| `aws/security/` | DevSecOps / cloud security reference | 支撐 IAM、GuardDuty、Security Hub、encryption、policy |
| `projects/_archive/tde2.0/` | 舊專案封存 | 不作為目前主線，但可回頭抽履歷素材 |

## DevOps/SRE 主線

DevOps/SRE 相關內容已改由 `devops-homelab` 管理：

- Homelab 總入口：[../devops-homelab/README.md](../devops-homelab/README.md)
- Homelab 計畫入口：[../devops-homelab/plan.md](../devops-homelab/plan.md)

## 使用規則

- 新增技術筆記前，先確認是否應該放進 `devops-homelab`。
- AWS / OS / DSA / 舊 projects 先保留，但不主動膨脹。
- DevOps 實作、排錯、部署、監控、IaC、security hardening，全部優先進 homelab。
- DSA 只新增和 systems 有直接連結的 topic，例如 graph、hashing、consistent hashing、Bloom filter、sketch、queueing、approximation、constraint optimization。
- 舊專案放進 `projects/_archive/`，不再和 active learning 混在一起。

最後更新：2026-05-07
