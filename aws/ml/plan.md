# AWS Machine Learning Specialty 4 週高強度學習計畫

**目標：** 4 週內以考試通過優先，掌握 AWS Machine Learning Specialty 高頻題型、核心選型判斷與常見陷阱。

**進度：** `0 / 65`

**主教材：**
- `mls-notes/` 為主線
- `notes/` 與 `articles/` 僅用來補高頻陷阱與理解盲點

**每週節奏：**
- 2 次主題學習，每次 60-75 分鐘
- 1 次題目演練，每次 60 分鐘
- 1 次錯題複盤或輕量 lab，每次 45-60 分鐘

## 學習進度

### Week 1 - Data Engineering（Domain 1，20%）

- [ ] 讀完 `mls-notes/01-data-engineering/s3.md`
- [ ] 讀完 `mls-notes/01-data-engineering/kinesis.md`
- [ ] 讀完 `mls-notes/01-data-engineering/glue.md`
- [ ] 讀完 `mls-notes/01-data-engineering/data-stores.md`
- [ ] 讀完 `mls-notes/01-data-engineering/data-pipeline.md`
- [ ] 讀完 `mls-notes/01-data-engineering/aws-batch.md`
- [ ] 讀完 `mls-notes/01-data-engineering/step-functions.md`
- [ ] 讀完 `mls-notes/01-data-engineering/dms.md`
- [ ] 分清 `Kinesis Data Streams` vs `Kinesis Data Firehose` vs `Kinesis Analytics`
- [ ] 分清 `Glue = serverless ETL`，`EMR = managed Hadoop/Spark cluster`
- [ ] 理解 `S3 as data lake` 的常見架構（Landing → Raw → Curated）
- [ ] 理解 `AWS Batch = 批次運算`，適合大規模 ML 訓練 job
- [ ] 完成 1 次 Data Engineering 題型練習
- [ ] 記錄 3 題 Data Pipeline 題的錯因或判斷依據
- [ ] 題目驗收點：遇到資料擷取/轉換題時，能快速判斷選 Kinesis、Glue、EMR 或 Batch

### Week 2 - Exploratory Data Analysis（Domain 2，24%）

- [ ] 讀完 `mls-notes/02-exploratory-data-analysis/data-science-basics.md`
- [ ] 讀完 `mls-notes/02-exploratory-data-analysis/feature-engineering.md`
- [ ] 讀完 `mls-notes/02-exploratory-data-analysis/handling-outliers.md`
- [ ] 讀完 `mls-notes/02-exploratory-data-analysis/emr.md`
- [ ] 讀完 `mls-notes/02-exploratory-data-analysis/athena.md`
- [ ] 讀完 `mls-notes/02-exploratory-data-analysis/quicksight.md`
- [ ] 讀完 `mls-notes/02-exploratory-data-analysis/python-in-data-science-and-lm.md`
- [ ] 分清 `Normalization` vs `Standardization` 的使用時機
- [ ] 分清 `Imputation` vs `Dropping` outlier 的選型邏輯
- [ ] 理解 `Feature Engineering` 的核心手法（binning、encoding、scaling）
- [ ] 理解 `Athena = serverless SQL on S3`，`QuickSight = BI 視覺化`
- [ ] 完成 1 次 EDA 題型練習
- [ ] 記錄 3 個 Feature Engineering 常見考法
- [ ] 題目驗收點：遇到資料前處理題時，能判斷選哪種 encoding / scaling 策略

### Week 3 - Modelling（Domain 3，36%）

- [ ] 讀完 `mls-notes/03-modelling/sagemaker.md`
- [ ] 讀完 `mls-notes/03-modelling/deep-learning.md`
- [ ] 讀完 `mls-notes/03-modelling/other.md`
- [ ] 讀完 `mls-notes/04-higher-level-ai-ml-services/amazon-rekognition.md`
- [ ] 讀完 `mls-notes/04-higher-level-ai-ml-services/amazon-comprehend.md`
- [ ] 讀完 `mls-notes/04-higher-level-ai-ml-services/amazon-lex.md`
- [ ] 讀完 `mls-notes/04-higher-level-ai-ml-services/amazon-forecast.md`
- [ ] 讀完 `mls-notes/04-higher-level-ai-ml-services/amazon-personalize.md`
- [ ] 讀完 `mls-notes/04-higher-level-ai-ml-services/other-ml-services.md`
- [ ] 分清 `XGBoost` vs `Linear Learner` vs `K-Means` 各自適用場景
- [ ] 分清 `Overfitting` 解法：Regularization / Dropout / More Data / Early Stopping
- [ ] 分清 `Precision` vs `Recall` vs `F1` 的選型邏輯（imbalanced dataset）
- [ ] 理解 SageMaker 訓練流程：`S3 → Training Job → Model → Endpoint`
- [ ] 理解 `Built-in algorithms` 的常見選型：regression / classification / clustering / NLP
- [ ] 分清高階 AI 服務選型：`Rekognition = 影像`、`Comprehend = NLP`、`Lex = chatbot`、`Forecast = 時序預測`
- [ ] 完成 1 次 Modelling 題型練習
- [ ] 記錄 3 個 SageMaker 常見考法（hyperparameter tuning、spot training、pipe mode）
- [ ] 題目驗收點：遇到模型選型題時，能快速對應到正確的 SageMaker 演算法或高階服務

### Week 4 - ML Operations + 考前衝刺（Domain 4，20%）

- [ ] 讀完 `mls-notes/05-operations/sagemaker-inner-details.md`
- [ ] 讀完 `mls-notes/05-operations/sagemaker-security.md`
- [ ] 讀完 `mls-notes/05-operations/sagemaker-on-the-edge.md`
- [ ] 讀完 `mls-notes/05-operations/mlops-with-sagemaker-and-k8s.md`
- [ ] 讀完 `mls-notes/05-operations/serverless-inference.md`
- [ ] 讀完 `mls-notes/05-operations/sagemaker-resources.md`
- [ ] 分清 `SageMaker Pipelines = MLOps workflow 自動化`
- [ ] 分清 `SageMaker Model Monitor = 偵測 data drift / model drift`
- [ ] 分清 `Real-time Inference` vs `Batch Transform` vs `Async Inference` vs `Serverless Inference`
- [ ] 理解 `SageMaker Neo = 模型編譯優化`，`SageMaker Edge Manager = 部署到邊緣裝置`
- [ ] 整理 1 份自己的 10 條高頻選型口訣
- [ ] 做完第 1 回模擬題或第 1 組計時練習
- [ ] 做完第 2 回模擬題或第 2 組計時練習
- [ ] 建立 1 份弱點清單
- [ ] 將弱點清單分類成最多 3 類主題
- [ ] 只回補弱點清單中的 3 類主題，不再全面重讀
- [ ] 題目驗收點：能用 10 個高頻關鍵字快速對應到正確服務或架構

### 錯題複盤規則

- [ ] 建立 1 份錯題清單
- [ ] 每題錯題記下題目主題分類：Data Engineering / EDA / Modelling / MLOps
- [ ] 每題錯題都標記成因：服務不熟 / 演算法判斷錯 / 題幹關鍵字漏看
- [ ] 每題錯題都補 1 句正確判斷依據
- [ ] 同類錯誤累積 3 次時，回補對應原筆記
- [ ] 每週至少做 1 次 30 分鐘錯題複盤

### 輕量 Lab 規則

- [ ] 只做高回報 lab：SageMaker Training Job、Kinesis + Glue ETL、SageMaker Endpoint 部署
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
- [ ] 能在情境題中分辨 Data Engineering、EDA、Modelling、MLOps 四大類核心服務的選型邏輯
