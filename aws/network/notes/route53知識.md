
快速知識對照
Route 53 路由策略原理適用場景LatencyAWS 實測各 Region 延遲，導向最快的全球用戶，追求最低延遲 ✅Weighted按比例分流（如 70/30）A/B 測試、流量控制Geolocation按用戶地理位置導向法規/內容差異需求Multivalue回傳多個 IP，client 自選簡單負載，非真正智能路由

關鍵區分：Latency vs Geolocation
Geolocation：「你在日本 → 導向東京」
             地理位置近 ≠ 延遲最低（網路路徑不同）

Latency：    「測試結果東京 20ms、新加坡 35ms → 導向東京」
             直接以實際延遲決定 ✅

題目關鍵字："optimal response time" = 最低延遲 = Latency routing


C 為什麼錯？

Multivalue 只是回傳多個 IP
client 端自己測延遲再選 → 這個邏輯不在 Route 53 控制範圍
增加 client 端複雜度，不是 DNS 層解法


答案：B ✅

Latency routing = Route 53 替用戶量好延遲再指路，用戶不需要做任何事。
所以route53默認策略是啥?下午4:20Route 53 默認策略：Simple Routing

Simple Routing 特性
DNS Query → Route 53 → 直接回傳紀錄值
特性說明無智能判斷不看延遲、不看地理位置、不看權重單筆紀錄一個 hostname → 一個或多個 IP多個 IP隨機回傳其中一個（client 隨機拿到）無 Health Check不會自動排除故障節點

各策略一覽對比
Simple      → 無腦指向固定目標
Weighted    → 按比例分流（A/B test）
Latency     → 導向延遲最低的 Region
Geolocation → 按用戶所在國家/地區
Geoproximity→ 按地理距離（可偏移）
Failover    → 主掛了自動切備援
Multivalue  → 回傳多個 IP + Health Check

簡單記憶
只有一台伺服器？         → Simple
要灰度發布/測試？        → Weighted  
全球部署追求速度？        → Latency
法規要求流量在特定國家？  → Geolocation
主備容災？               → Failover

Simple 就是「我不管你從哪來、網路好不好，反正就給你這個 IP」——適合單 Region 小專案，一旦全球化就要升級策略。