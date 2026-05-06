# Tech Stack Learning

這個 repo 已精簡成少量仍需要獨立保存的學習區。DevOps/SRE 主線已收斂到
[`devops-homelab`](../devops-homelab/)；TSL 不再維護 Docker、K8s、CI/CD、Terraform、SRE 等平行 topic。

## 保留目錄

```text
tech-stack-learning/
  README.md
  aws/                  # AWS 筆記與認證資料，先保留
  cheatsheet/           # 速查表候選區，先保留
  dsa/                  # DSA、heuristic、solver 學習，先保留
  operating-systems/    # OS、Linux、I/O、NFS / FTP 等基礎筆記，先保留
  projects/             # 舊專案資料，先保留
```

## DevOps/SRE 主線

DevOps/SRE 相關內容已改由 `devops-homelab` 管理：

- Homelab 總入口：[../devops-homelab/README.md](../devops-homelab/README.md)
- Homelab 計畫入口：[../devops-homelab/plan.md](../devops-homelab/plan.md)

## 使用規則

- 新增技術筆記前，先確認是否應該放進 `devops-homelab`。
- AWS / OS / DSA / 舊 projects 先保留，但不主動膨脹。
- DevOps 實作、排錯、部署、監控、IaC、security hardening，全部優先進 homelab。

最後更新：2026-05-06
