# OWASP Top 10 2025 - Web 應用安全漏洞指南

## 📚 什麼是 OWASP Top 10？

**OWASP** = Open Web Application Security Project（開放式 Web 應用安全計畫）

OWASP Top 10 是開發人員和 Web 應用安全的標準參考文件，代表了對 **Web 應用最關鍵安全風險** 的廣泛共識。

**更新頻率**: 每 3-4 年更新一次
**最新版本**: 2025 (更新於 2025年1月)
**上一版本**: 2021

---

## 🎯 OWASP Top 10 2025 完整列表

| 排名 | 漏洞類型 | 英文名稱 | 2021排名 | 狀態 |
|-----|--------|--------|--------|------|
| #1 | 破損的存取控制 | Broken Access Control | #1 | ✅ |
| #2 | 加密失敗 | Cryptographic Failures | #2 | ✅ |
| #3 | 注入攻擊 | Injection | #3 | ⬇️ (降至#5) |
| #4 | 不安全的設計 | Insecure Design | #4 | ⬇️ (降至#6) |
| #5 | 安全設置錯誤 | Security Misconfiguration | #5 | ✅ |
| #6 | 易受攻擊和過時的元件 | Vulnerable and Outdated Components | #6 | ✅ |
| #7 | 身份識別和身份驗證失敗 | Identification and Authentication Failures | #7 | ✅ |
| #8 | 軟體供應鏈缺陷 | Software and Data Integrity Failures | #8 | ✅ |
| #9 | 日誌和監控不足 | Security Logging and Monitoring Failures | #9 | ✅ |
| #10 | 伺服器端請求偽造 (SSRF) | Server-Side Request Forgery (SSRF) | #10 | ✅ |

### 🆕 2025 版本新增或調整

**新進入榜單**:
- **軟體供應鏈缺陷** - 從 2021 年的「易受攻擊和過時的元件」大幅擴展
  - 涵蓋：惡意依賴、被盜用的構建工具、不安全的 CI/CD 管道

**排名變化**:
- **注入攻擊** (#3 → #5) - 雖然仍是危險的漏洞，但優先級下降
- **不安全的設計** (#4 → #6) - 反映產業逐漸採用安全設計原則

---

## 📋 OWASP Top 10 詳細解析

### #1 破損的存取控制 (Broken Access Control)

**定義**:
應用程式未能正確驗證和授權用戶操作，允許用戶訪問他們不應該有權限的資源或執行他們不應該執行的操作。

**常見場景**:
```
❌ 用戶可以直接修改 URL 存取他人的帳戶
❌ 普通用戶可以執行管理員功能
❌ 用戶 ID 在 URL 中可被修改 (如 /user/123 → /user/456)
❌ 無法驗證用戶對某資源的所有權
❌ 功能級存取控制不足
```

**實例**:
```
原始 URL: https://api.example.com/profile/user123/data
攻擊者修改為: https://api.example.com/profile/user456/data
結果: 直接訪問了其他用戶的私人數據
```

**預防措施**:
- ✅ 實施強大的存取控制機制（如 RBAC - 角色基礎存取控制）
- ✅ 默認拒絕訪問（Deny by default）
- ✅ 每次請求都驗證用戶權限
- ✅ 避免在 URL 中直接暴露用戶 ID
- ✅ 使用 UUID 或 token 替代 ID
- ✅ 為 API 實施限流和授權檢查

---

### #2 加密失敗 (Cryptographic Failures)

**定義**:
敏感數據在傳輸、存儲或處理時未能得到妥善保護，導致數據被洩露或篡改。

**常見場景**:
```
❌ 使用過時的加密算法（如 MD5、SHA-1）
❌ 密碼以明文形式存儲
❌ 敏感數據傳輸時未使用 HTTPS
❌ SSL/TLS 配置不當
❌ 硬編碼密鑰或密碼
❌ 缺少加密金鑰管理策略
```

**實例**:
```
SQL 中的密碼存儲：
❌ 不良: password = "password123"
✅ 良好: password_hash = bcrypt("password123", salt)
```

**預防措施**:
- ✅ 所有傳輸使用 HTTPS (TLS 1.2+)
- ✅ 密碼使用強加密演算法 (bcrypt, Argon2, PBKDF2)
- ✅ 敏感數據在靜止時加密
- ✅ 定期更新加密協議
- ✅ 妥善管理加密金鑰（不硬編碼）
- ✅ 禁用 HTTP，強制 HTTPS

---

### #3 注入攻擊 (Injection)

**定義**:
不信任的數據被解釋為代碼並執行，導致攻擊者可以修改或執行意外的操作。

**主要類型**:

#### 🔴 SQL 注入 (SQL Injection)
```sql
-- 用戶輸入: ' OR '1'='1
-- 原意: SELECT * FROM users WHERE username = '用戶名' AND password = '密碼'
-- 實際執行: SELECT * FROM users WHERE username = '' OR '1'='1' AND password = ''
-- 結果: 返回所有用戶！
```

**影響**: 讀取、修改、刪除數據庫內容

#### 🔴 跨網站指令碼 (XSS - Cross-Site Scripting)
```html
<!-- 用戶輸入: <script>alert('hacked')</script> -->
<!-- 如果未經過濾，該指令碼會在其他用戶的瀏覽器中執行 -->
<!-- 可能盜取 cookies、session 或重定向到釣魚網站 -->
```

**影響**: 盜取用戶 session、重定向到惡意網站、資料竊取

#### 🔴 OS 注入 (Command Injection)
```bash
# 用戶輸入: ; rm -rf /
# 原意: ping google.com
# 實際: ping google.com; rm -rf /
```

**預防措施**:
- ✅ 使用參數化查詢 (Prepared Statements)
  ```python
  # ❌ 不良
  query = f"SELECT * FROM users WHERE id = {user_id}"

  # ✅ 良好
  query = "SELECT * FROM users WHERE id = ?"
  cursor.execute(query, (user_id,))
  ```
- ✅ 輸入驗證與白名單
- ✅ 輸出編碼 (HTML encoding)
- ✅ 使用 ORM 框架
- ✅ 最小化權限原則

---

### #4 不安全的設計 (Insecure Design)

**定義**:
在設計階段就存在安全缺陷，而不是實現過程中的編碼錯誤。

**常見場景**:
```
❌ 無密碼重置機制
❌ 無防暴力破解措施
❌ 無資料驗證機制
❌ 無審計日誌
❌ 單點故障設計
❌ 沒有威脅建模
```

**預防措施**:
- ✅ 進行威脅建模
- ✅ 在架構層面考慮安全
- ✅ 實施安全設計模式
- ✅ 定期進行安全評審
- ✅ 實施防暴力破解機制
- ✅ 建立完整的審計日誌

---

### #5 安全設置錯誤 (Security Misconfiguration)

**定義**:
系統、框架、數據庫或伺服器的安全設置不當，導致未授權訪問或信息洩露。

**常見場景**:
```
❌ 使用默認認證憑證 (admin/admin)
❌ 不必要的服務或端口開放
❌ 調試模式啟用在生產環境
❌ 詳細的錯誤信息洩露敏感信息
❌ 過時的軟件和依賴
❌ 不安全的 HTTP 標頭
```

**預防措施**:
- ✅ 立即更改默認認證
- ✅ 最小化權限原則（關閉不需要的服務）
- ✅ 在生產環境禁用調試模式
- ✅ 設置安全的 HTTP 標頭
  ```
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  Strict-Transport-Security: max-age=31536000
  ```
- ✅ 定期更新依賴
- ✅ 建立設置檢查清單

---

### #6 易受攻擊和過時的元件 (Vulnerable and Outdated Components)

**定義**:
使用已知存在漏洞的過時庫、框架或依賴。

**常見場景**:
```
❌ 使用已有公開 CVE 的舊版本庫
❌ 沒有追蹤依賴的安全更新
❌ 使用不再維護的開源項目
❌ 沒有進行依賴掃描
```

**實例**:
```
package.json 中的舊版本:
"dependencies": {
  "lodash": "3.0.0"  // ❌ 存在已知漏洞
}

npm audit 會警告此漏洞
```

**預防措施**:
- ✅ 定期更新依賴
- ✅ 使用工具掃描漏洞 (npm audit, OWASP Dependency-Check)
- ✅ 只使用受維護的依賴
- ✅ 監控安全公告
- ✅ 實施自動化的安全掃描

---

### #7 身份識別和身份驗證失敗 (Identification and Authentication Failures)

**定義**:
身份驗證機制實現不當，導致攻擊者可以冒充合法用戶。

**常見場景**:
```
❌ 允許弱密碼
❌ 無多因素認證 (MFA)
❌ Session ID 可預測
❌ 密碼重置流程不安全
❌ 無密碼強度要求
❌ 無帳戶鎖定機制（防暴力破解）
```

**預防措施**:
- ✅ 強制強密碼要求
- ✅ 實施 MFA (多因素認證)
- ✅ 使用安全的 Session 管理
- ✅ 隨機化 Session ID
- ✅ 實施帳戶鎖定（N 次失敗後）
- ✅ 安全的密碼重置機制
- ✅ 監控異常登入活動

---

### #8 軟體和數據完整性失敗 (Software and Data Integrity Failures)

**定義**:
軟件更新、CI/CD 管道或數據在傳輸時缺乏完整性檢查，導致可能的篡改。

**常見場景**:
```
❌ 從不可信源下載依賴
❌ 無簽名的依賴
❌ 不安全的 CI/CD 管道
❌ 被盜用的包管理器帳戶
❌ 無完整性校驗
```

**實例**:
```
2023 年: XZ Utils 後門事件
被盜用的帳戶在流行的 Linux 工具中植入惡意代碼
```

**預防措施**:
- ✅ 使用數位簽名驗證軟件
- ✅ 只從官方來源下載依賴
- ✅ 實施安全的 CI/CD 管道
- ✅ 進行代碼評審
- ✅ 使用軟件物料清單 (SBOM - Software Bill of Materials)
- ✅ 監控供應鏈威脅

---

### #9 日誌和監控不足 (Security Logging and Monitoring Failures)

**定義**:
缺乏充分的日誌記錄和監控，導致無法檢測或響應安全事件。

**常見場景**:
```
❌ 登入失敗未記錄
❌ 無異常活動檢測
❌ 日誌可被刪除或篡改
❌ 未監控高風險操作
❌ 無關鍵事件警報
```

**預防措施**:
- ✅ 記錄所有身份驗證嘗試
- ✅ 記錄高風險操作 (删除、修改權限等)
- ✅ 集中式日誌管理 (ELK Stack、Splunk)
- ✅ 實施警報機制
- ✅ 定期審查日誌
- ✅ 保護日誌不被篡改
- ✅ 保持足夠的日誌保留期

---

### #10 伺服器端請求偽造 (Server-Side Request Forgery - SSRF)

**定義**:
應用程式從用戶控制的輸入獲取遠程資源，而未驗證該 URL，導致攻擊者可以訪問內部資源。

**常見場景**:
```
❌ 接受用戶提供的 URL 並獲取內容
❌ 無 URL 驗證
❌ 可訪問內部 IP 地址
❌ 可訪問元數據服務（AWS IMDSv1）
```

**實例**:
```
應用程式功能: 根據提供的 URL 獲取圖片
用戶輸入: http://internal-admin-panel.local/config
結果: 應用程式獲取並返回內部配置信息
```

**預防措施**:
- ✅ 驗證和過濾用戶提供的 URL
- ✅ 禁止訪問本地和私有 IP 地址
  ```
  127.0.0.1, 192.168.*, 10.0.0.0/8, 172.16.0.0/12
  ```
- ✅ 使用 URL 白名單
- ✅ 禁用不必要的 HTTP 重定向跟隨
- ✅ 檢查文件協議 (禁止 file://)
- ✅ 使用 DNS 重新綁定防護

---

## 🛡️ 通用防禦策略

### 1️⃣ 安全開發生命週期 (SDLC)
```
需求分析 (威脅建模)
    ↓
設計 (安全架構)
    ↓
編碼 (安全編碼實踐)
    ↓
測試 (SAST, DAST, 滲透測試)
    ↓
部署 (安全配置)
    ↓
維護 (日誌、監控、補丁管理)
```

### 2️⃣ 輸入驗證與輸出編碼
```
信任邊界:
外部輸入 (用戶、API、文件)
    ↓ 驗證與清理
內部處理
    ↓ 編碼
輸出 (HTML、SQL、命令)
```

### 3️⃣ 最小權限原則 (Principle of Least Privilege)
- 用戶只有執行其職能所需的最低權限
- 應用程式運行於最小權限級別
- 數據庫帳戶只有必要的權限

### 4️⃣ 深度防禦 (Defense in Depth)
```
多層安全:
第一層: 網路 (防火牆、WAF)
第二層: 應用 (身份驗證、授權)
第三層: 數據 (加密、備份)
第四層: 監控 (日誌、告警)
```

---

## 📊 OWASP Top 10 對開發者的影響

### 按角色的重點

**後端開發**:
- 🔴 #1 破損的存取控制
- 🔴 #3 注入攻擊
- 🔴 #7 身份驗證失敗

**前端開發**:
- 🔴 #3 XSS 攻擊
- 🔴 #5 安全設置錯誤
- 🔴 #8 不安全的依賴

**DevOps/基礎設施**:
- 🔴 #5 安全設置錯誤
- 🔴 #6 易受攻擊的元件
- 🔴 #9 日誌和監控

**全棧**:
- 🔴 #2 加密失敗
- 🔴 #4 不安全的設計
- 🔴 #10 SSRF

---

## 🧪 如何測試和驗證

### OWASP 提供的資源

1. **OWASP ZAP** - 免費的 Web 應用安全掃描工具
2. **Burp Suite** - 專業的滲透測試工具
3. **OWASP Testing Guide** - 詳細的測試方法論

### 常用命令示例

```bash
# 用 OWASP ZAP 進行掃描
zaproxy -cmd -quickurl http://example.com -quickout report.html

# 用 npm audit 檢查依賴漏洞
npm audit

# 用 OWASP Dependency-Check
dependency-check --project "MyApp" --scan /path/to/app
```

---

## 📚 進一步學習資源

### 官方資源
- [OWASP Top 10:2025 官方文檔](https://owasp.org/Top10/2025/)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)

### 在線學習平台
- [OWASP WebGoat](https://owasp.org/www-project-webgoat/) - 交互式學習平台
- [HackTheBox](https://www.hackthebox.com/) - 實踐安全挑戰
- [TryHackMe](https://tryhackme.com/) - 初學者友善的安全課程

### 相關認證
- **CEH** (Certified Ethical Hacker)
- **OSCP** (Offensive Security Certified Professional)
- **Security+** (CompTIA Security+)

---

## 🔗 相關資源連結

- [OWASP 官方網站](https://owasp.org/)
- [OWASP Top 10:2025](https://owasp.org/Top10/2025/)
- [CWE/SANS Top 25](https://cwe.mitre.org/top25/)
- [黑暗執行緒 - OWASP 十大筆記](https://blog.darkthread.net/blog/owasp-top-10-n-cwe-top-25/)

---

## 📝 快速參考表

| # | 漏洞 | 高風險指標 | 防禦優先 |
|---|-----|---------|--------|
| 1 | 破損的存取控制 | 無授權檢查 | 🔴 必須 |
| 2 | 加密失敗 | HTTP 傳輸敏感數據 | 🔴 必須 |
| 3 | 注入攻擊 | 未驗證的用戶輸入 | 🔴 必須 |
| 4 | 不安全的設計 | 無威脅建模 | 🟡 重要 |
| 5 | 安全設置錯誤 | 默認憑證 | 🔴 必須 |
| 6 | 易受攻擊的元件 | 過時依賴 | 🔴 必須 |
| 7 | 身份驗證失敗 | 無 MFA | 🔴 必須 |
| 8 | 數據完整性失敗 | 無簽名檢查 | 🟡 重要 |
| 9 | 監控不足 | 無日誌記錄 | 🟡 重要 |
| 10 | SSRF | 無 URL 驗證 | 🟡 重要 |

---

## 🚀 實踐檢查清單

在開發應用時，檢查以下項目：

- [ ] 實施強大的存取控制
- [ ] 所有敏感數據使用 HTTPS
- [ ] 密碼使用強加密演算法
- [ ] 使用參數化查詢防止 SQL 注入
- [ ] 輸出編碼防止 XSS
- [ ] 更改所有默認認證
- [ ] 禁用調試模式在生產環境
- [ ] 定期更新依賴
- [ ] 實施 MFA
- [ ] 建立完整的日誌和監控
- [ ] 進行威脅建模
- [ ] 定期進行安全測試

---

**最後更新**: 2026-02-26
**版本**: OWASP Top 10:2025
**來源**: [OWASP 官方文檔](https://owasp.org/Top10/2025/)
