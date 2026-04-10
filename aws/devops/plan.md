# AWS DevOps Professional 4 週高強度學習計畫

**目標：** 4 週內以考試通過優先，掌握 AWS DevOps Engineer Professional 高頻題型、核心選型判斷與常見陷阱。

**進度：** `0 / 65`

**主教材：**
- `dop-notes/` 為主線
- `notes/` 與 `articles/` 僅用來補高頻陷阱與理解盲點

**每週節奏：**
- 2 次主題學習，每次 60-75 分鐘
- 1 次題目演練，每次 60 分鐘
- 1 次錯題複盤或輕量 lab，每次 45-60 分鐘

## 學習進度

### Week 1 - SDLC Automation（Domain 1，22%）

- [ ] 讀完 `dop-notes/01-sdlc-automation/cicd.md`
- [ ] 讀完 `dop-notes/01-sdlc-automation/codepipeline.md`
- [ ] 讀完 `dop-notes/01-sdlc-automation/codebuild.md`
- [ ] 讀完 `dop-notes/01-sdlc-automation/codedeploy.md`
- [ ] 讀完 `dop-notes/01-sdlc-automation/codecommit.md`
- [ ] 讀完 `dop-notes/01-sdlc-automation/codeartifact.md`
- [ ] 讀完 `dop-notes/01-sdlc-automation/jenkins.md`
- [ ] 讀完 `dop-notes/01-sdlc-automation/ec2-image-builder.md`
- [ ] 分清 `CodePipeline = 流水線協調者`
- [ ] 分清 `CodeBuild = 編譯 + 測試執行器`
- [ ] 分清 `CodeDeploy = 部署到 EC2 / Lambda / ECS`
- [ ] 分清 `In-place` vs `Blue/Green` 部署差異
- [ ] 分清 `Linear` vs `Canary` vs `AllAtOnce` 流量切換策略
- [ ] 理解 `appspec.yml` 與 `buildspec.yml` 的分工
- [ ] 理解 `CodeArtifact = 私有 package registry`
- [ ] 完成 1 次 SDLC 題型練習
- [ ] 記錄 3 題 CI/CD 題的錯因或判斷依據
- [ ] 題目驗收點：遇到部署題時，能快速判斷選 CodeDeploy 哪種策略

### Week 2 - Configuration Management & IaC（Domain 2，19%）

- [ ] 讀完 `dop-notes/02-configuration-management-and-iac/cloudformation.md`
- [ ] 讀完 `dop-notes/02-configuration-management-and-iac/cdk.md`
- [ ] 讀完 `dop-notes/02-configuration-management-and-iac/ssm.md`
- [ ] 讀完 `dop-notes/02-configuration-management-and-iac/eb.md`
- [ ] 讀完 `dop-notes/02-configuration-management-and-iac/sam.md`
- [ ] 讀完 `dop-notes/02-configuration-management-and-iac/opsworks.md`
- [ ] 讀完 `dop-notes/02-configuration-management-and-iac/service-catalog.md`
- [ ] 讀完 `dop-notes/02-configuration-management-and-iac/appconfig.md`
- [ ] 讀完 `dop-notes/02-configuration-management-and-iac/step-functions.md`
- [ ] 分清 `CloudFormation StackSets = 跨帳號 / 跨 Region 部署`
- [ ] 分清 `Change Sets = 預覽變更`、`Drift Detection = 偵測手動變更`
- [ ] 分清 `SSM Parameter Store` vs `Secrets Manager` 使用場景
- [ ] 分清 `SSM Run Command` vs `SSM State Manager` vs `SSM Automation`
- [ ] 理解 `Elastic Beanstalk` 部署策略（All at once / Rolling / Immutable / Blue-Green）
- [ ] 理解 `AppConfig` 解的是 feature flag 動態推送的問題
- [ ] 完成 1 次 IaC / Config 題型練習
- [ ] 記錄 3 個 CloudFormation 常見陷阱（DependsOn、循環參照、rollback）
- [ ] 題目驗收點：遇到 IaC 題時，能判斷選 CloudFormation、CDK、SSM 還是 EB

### Week 3 - 監控、事件響應與彈性（Domain 3、4、5）

- [ ] 讀完 `dop-notes/03-resilient-cloud-solutions/disaster-recovery.md`
- [ ] 讀完 `dop-notes/03-resilient-cloud-solutions/asg.md`
- [ ] 讀完 `dop-notes/03-resilient-cloud-solutions/lambda.md`
- [ ] 讀完 `dop-notes/03-resilient-cloud-solutions/resilient-architectures.md`
- [ ] 讀完 `dop-notes/04-monitoring-and-logging/cloudwatch.md`
- [ ] 讀完 `dop-notes/04-monitoring-and-logging/opensearch.md`
- [ ] 讀完 `dop-notes/05-incident-and-event-response/eventbridge.md`
- [ ] 讀完 `dop-notes/05-incident-and-event-response/cloudtrail.md`
- [ ] 讀完 `dop-notes/05-incident-and-event-response/sns-sqs.md`
- [ ] 讀完 `dop-notes/05-incident-and-event-response/x-ray.md`
- [ ] 分清 `CloudWatch Metrics` vs `CloudWatch Logs` vs `CloudWatch Alarms`
- [ ] 分清 `CloudTrail = API 呼叫稽核`，`CloudWatch = 運行指標`
- [ ] 分清 `EventBridge = 事件路由`，`SNS = 推播通知`，`SQS = 訊息佇列`
- [ ] 理解 DR 四種策略：`Backup & Restore < Pilot Light < Warm Standby < Multi-Site`
- [ ] 理解 `RTO` vs `RPO` 的選型邏輯
- [ ] 理解 ASG 的 Scheduled / Dynamic / Predictive Scaling 差異
- [ ] 完成 1 次監控 + 事件題型練習
- [ ] 記錄 3 個 CloudWatch 常見考法（custom metrics、log filter、composite alarm）
- [ ] 題目驗收點：遇到監控告警題時，能判斷 CloudWatch、EventBridge、SNS/SQS 如何串接

### Week 4 - 安全合規 + 考前衝刺（Domain 6）

- [ ] 讀完 `dop-notes/06-security-and-compliance/guard-duty.md`
- [ ] 讀完 `dop-notes/06-security-and-compliance/config.md`
- [ ] 讀完 `dop-notes/06-security-and-compliance/control-tower.md`
- [ ] 讀完 `dop-notes/06-security-and-compliance/organizations.md`
- [ ] 讀完 `dop-notes/06-security-and-compliance/iam-identity-center.md`
- [ ] 讀完 `dop-notes/06-security-and-compliance/trusted-advisor.md`
- [ ] 讀完 `dop-notes/06-security-and-compliance/data-protection.md`
- [ ] 分清 `AWS Config = 資源合規狀態追蹤`（Config Rules + Remediation）
- [ ] 分清 `GuardDuty = 威脅偵測`，`Inspector = 弱掃`，`Macie = S3 敏感資料`
- [ ] 分清 `Control Tower = 多帳號治理`，`Organizations = 帳號層次管理`
- [ ] 理解 `SCP = 服務控制策略`，deny 在 IAM Policy 之前生效
- [ ] 整理 1 份自己的 10 條高頻選型口訣
- [ ] 做完第 1 回模擬題或第 1 組計時練習
- [ ] 做完第 2 回模擬題或第 2 組計時練習
- [ ] 建立 1 份弱點清單
- [ ] 將弱點清單分類成最多 3 類主題
- [ ] 只回補弱點清單中的 3 類主題，不再全面重讀
- [ ] 題目驗收點：能用 10 個高頻關鍵字快速對應到正確服務或架構

### 錯題複盤規則

- [ ] 建立 1 份錯題清單
- [ ] 每題錯題記下題目主題分類：SDLC / IaC / Resilience / Monitoring / Incident / Security
- [ ] 每題錯題都標記成因：服務不熟 / 策略判斷錯 / 題幹關鍵字漏看
- [ ] 每題錯題都補 1 句正確判斷依據
- [ ] 同類錯誤累積 3 次時，回補對應原筆記
- [ ] 每週至少做 1 次 30 分鐘錯題複盤

### 輕量 Lab 規則

- [ ] 只做高回報 lab：CodePipeline + CodeDeploy 串接、CloudFormation StackSets、CloudWatch Alarms + EventBridge
- [ ] 單次 lab 控制在 60 分鐘內
- [ ] 超過 60 分鐘的 lab 直接降級成架構圖演練，不追求完整部署
- [ ] lab 前先寫下這次要驗證的 1 個重點
- [ ] lab 完成後記下 1 個選型理由與 1 個常見陷阱

## 驗收標準

- [ ] 完成 4 週學習節奏，且每週都有主題閱讀、題目演練、複盤或輕量 lab
- [ ] 完成 2 回模擬題或等量計時題組
- [ ] 建立並維護 1 份錯題清單
- [ ] 完成 3 次高價值輕量 lab / 架構演練
- [ ] 能口述 10 個高頻選型判斷
- [ ] 能在情境題中分辨 SDLC、IaC、監控、事件響應、安全合規五大類核心服務的選型邏輯
