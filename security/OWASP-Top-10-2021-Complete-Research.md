# OWASP Top 10 (2021) - Complete Research Guide

> Source: Official OWASP Top 10 GitHub repository (`github.com/OWASP/Top10`)
> Research Date: 2026-03-30
> Status: OWASP Top 10 2021 is the established reference. OWASP Top 10 2025 has been released as the successor.

---

## Table of Contents

- [Overview](#overview)
- [A01:2021 - Broken Access Control](#a012021---broken-access-control)
- [A02:2021 - Cryptographic Failures](#a022021---cryptographic-failures)
- [A03:2021 - Injection](#a032021---injection)
- [A04:2021 - Insecure Design](#a042021---insecure-design)
- [A05:2021 - Security Misconfiguration](#a052021---security-misconfiguration)
- [A06:2021 - Vulnerable and Outdated Components](#a062021---vulnerable-and-outdated-components)
- [A07:2021 - Identification and Authentication Failures](#a072021---identification-and-authentication-failures)
- [A08:2021 - Software and Data Integrity Failures](#a082021---software-and-data-integrity-failures)
- [A09:2021 - Security Logging and Monitoring Failures](#a092021---security-logging-and-monitoring-failures)
- [A10:2021 - Server-Side Request Forgery (SSRF)](#a102021---server-side-request-forgery-ssrf)
- [Changes: 2017 to 2021](#changes-2017-to-2021)
- [OWASP Top 10 2025 - What Changed](#owasp-top-10-2025---what-changed)
- [OWASP Top 10 and DevOps/Cloud/Infrastructure Security](#owasp-top-10-and-devopscloudinfrastructure-security)
- [Detection Tools Summary](#detection-tools-summary)

---

## Overview

The OWASP Top 10 is the most widely recognized standard for web application security risks. The 2021 edition was data-driven: 8 of the 10 categories were selected from contributed data (500,000+ applications tested), and 2 categories were selected from a community survey of AppSec professionals.

Key methodology changes in 2021:
- Shifted from ~30 prescribed CWEs to ~400 CWEs analyzed
- Used incidence rate (% of apps affected) instead of frequency (count of findings)
- Focused on **root causes** rather than **symptoms** (e.g., "Cryptographic Failures" instead of "Sensitive Data Exposure")
- Used CVSS exploit/impact scores for risk ranking

---

## A01:2021 - Broken Access Control

| Metric | Value |
|--------|-------|
| CWEs Mapped | 34 |
| Avg Incidence Rate | 3.81% |
| Total Occurrences | 318,487 |
| Total CVEs | 19,013 |
| 2017 Position | #5 (moved up to #1) |

### What It Is

Access control enforces policies so that users cannot act outside their intended permissions. When access controls fail, users can view/modify data they should not have access to, or perform actions beyond their privilege level.

### Common Vulnerable Patterns

- **Violating least privilege / deny-by-default**: Access is available to anyone instead of being restricted to specific roles
- **IDOR (Insecure Direct Object References)**: Viewing/editing another user's account by changing an ID parameter
- **Missing API access controls**: No authorization checks on POST, PUT, DELETE endpoints
- **URL/parameter tampering**: Bypassing checks by modifying the URL, internal state, or HTML
- **Privilege escalation**: Acting as admin when logged in as a regular user
- **JWT/token manipulation**: Replaying, tampering with JWTs or cookies to elevate privileges
- **CORS misconfiguration**: Allowing API access from unauthorized origins
- **Force browsing**: Accessing authenticated/privileged pages without proper credentials

### Real-World Attack Examples

**Scenario 1 - IDOR via URL parameter:**
```
https://example.com/app/accountInfo?acct=notmyacct
```
Attacker modifies the `acct` parameter to access any user's account because the application does not verify ownership.

**Scenario 2 - Force browsing to admin pages:**
```
https://example.com/app/admin_getappInfo
```
A non-admin or unauthenticated user directly accesses admin functionality.

### Prevention Strategies

1. **Deny by default** - Except for public resources, deny all access by default
2. **Centralized access control** - Implement access control mechanisms once and reuse throughout the application
3. **Record ownership enforcement** - Model access controls should enforce record ownership, not trust user input
4. **Disable directory listing** - Ensure `.git`, backup files, and metadata are not in web roots
5. **Log access control failures** - Alert admins on repeated failures
6. **Rate limit APIs** - Minimize harm from automated attacks
7. **Invalidate sessions on logout** - Use short-lived JWTs; follow OAuth standards for revocation
8. **Functional testing** - Include access control unit and integration tests

### Detection Tools

- **Burp Suite** (manual/automated access control testing)
- **OWASP ZAP** (automated scanning for access control issues)
- **Postman/curl** (manual API testing for missing authorization)
- **SonarQube** (SAST - detects missing authorization annotations)
- **Semgrep** (custom rules for access control patterns)

---

## A02:2021 - Cryptographic Failures

| Metric | Value |
|--------|-------|
| CWEs Mapped | 29 |
| Avg Incidence Rate | 4.49% |
| Total Occurrences | 233,788 |
| Total CVEs | 3,075 |
| 2017 Position | #3 as "Sensitive Data Exposure" (renamed, moved to #2) |

### What It Is

Failures related to cryptography (or the absence of it) that lead to exposure of sensitive data. Previously called "Sensitive Data Exposure," which was a symptom rather than a root cause. The 2021 name focuses on the underlying cryptographic failures.

### Common Vulnerable Patterns

- **Data transmitted in cleartext** (HTTP, SMTP, FTP without TLS)
- **Weak/old cryptographic algorithms** (MD5, SHA1, DES, RC4)
- **Default or weak crypto keys**; keys checked into source code
- **Missing encryption enforcement** (no HSTS header)
- **Unvalidated server certificates** (ignoring TLS certificate chain)
- **IV reuse or insecure modes** (ECB mode, predictable IVs)
- **Passwords used as crypto keys** without a key derivation function
- **Unsalted/fast password hashes** (MD5/SHA1 for passwords)
- **Deprecated padding schemes** (PKCS#1 v1.5)

### Real-World Attack Examples

**Scenario 1 - Database auto-decryption + SQLi:**
An application encrypts credit card numbers in the database using automatic database encryption. A SQL injection flaw retrieves them in cleartext because the database auto-decrypts on retrieval.

**Scenario 2 - HTTPS downgrade attack:**
A site supports weak encryption. An attacker on an insecure WiFi network downgrades HTTPS to HTTP, intercepts requests, steals the session cookie, and hijacks the user's session.

**Scenario 3 - Unsalted password hashes:**
The password database uses unsalted or simple hashes. An attacker retrieves it via a file upload flaw and cracks all passwords using rainbow tables or GPU-accelerated brute force.

### Prevention Strategies

1. **Classify data** by sensitivity (privacy laws, regulatory requirements, business needs)
2. **Don't store sensitive data unnecessarily** - Discard ASAP; use tokenization or truncation
3. **Encrypt all sensitive data at rest** using strong algorithms
4. **Encrypt all data in transit** with TLS + forward secrecy; enforce via HSTS
5. **Use strong password hashing** - Argon2, scrypt, bcrypt, or PBKDF2 with salt and work factor
6. **Use authenticated encryption** (e.g., AES-GCM) instead of plain encryption
7. **Use CSPRNG** for initialization vectors; never reuse IVs for a given key
8. **Avoid deprecated functions** - No MD5, SHA1, PKCS#1 v1.5
9. **Disable caching** for responses containing sensitive data
10. **Generate keys cryptographically randomly**; store as byte arrays in memory

### Detection Tools

- **SSL Labs** (TLS configuration testing: `ssllabs.com/ssltest`)
- **testssl.sh** (CLI tool for TLS/SSL cipher testing)
- **OWASP Dependency Check** (identifies weak crypto libraries)
- **SonarQube / Semgrep** (SAST - detects weak hash usage, hardcoded keys)
- **Hashcat/John the Ripper** (offensive - test password hash strength)
- **Mozilla Observatory** (HTTP security headers including HSTS)

---

## A03:2021 - Injection

| Metric | Value |
|--------|-------|
| CWEs Mapped | 33 |
| Avg Incidence Rate | 3.37% |
| Total Occurrences | 274,228 |
| Total CVEs | 32,078 |
| 2017 Position | #1 (dropped to #3) |

### What It Is

An application is vulnerable when user-supplied data is not validated, filtered, or sanitized, and is used directly in queries, commands, or interpreters. This includes SQL injection, NoSQL injection, OS command injection, LDAP injection, XSS (now merged into this category), ORM injection, and Expression Language injection.

### Common Vulnerable Patterns

- **String concatenation in SQL queries** instead of parameterized queries
- **Dynamic queries without context-aware escaping**
- **Hostile data in ORM search parameters** extracting extra records
- **User input directly in OS commands** (e.g., `exec("ping " + userInput)`)
- **Unescaped user input in HTML output** (XSS - now part of Injection in 2021)
- **LDAP filter construction with user input**
- **Server-side template injection** (SSTI)

### Real-World Attack Examples

**Scenario 1 - SQL Injection via string concatenation:**
```java
String query = "SELECT * FROM accounts WHERE custID='" + request.getParameter("id") + "'";
```
Attacker sends: `' UNION SELECT SLEEP(10);--` to extract all records or cause DoS.

**Scenario 2 - ORM injection (HQL):**
```java
Query HQLQuery = session.createQuery("FROM accounts WHERE custID='" + request.getParameter("id") + "'");
```
Even ORM frameworks are vulnerable when queries are built via concatenation.

**Scenario 3 - XSS (now part of A03):**
User input reflected in HTML without encoding allows script execution in victim's browser.

### Prevention Strategies

1. **Use parameterized queries / prepared statements** (the #1 defense)
2. **Use safe APIs** that avoid the interpreter entirely (ORMs with parameterized interfaces)
3. **Positive server-side input validation** (allowlists, not denylists)
4. **Escape special characters** using interpreter-specific escape syntax for residual dynamic queries
5. **Use LIMIT and other SQL controls** to prevent mass data disclosure
6. **Integrate SAST/DAST/IAST into CI/CD** to catch injection before production

### Detection Tools

- **SQLMap** (automated SQL injection detection and exploitation)
- **OWASP ZAP** (DAST - automated injection scanning)
- **Burp Suite** (manual/automated injection testing)
- **SonarQube / Semgrep / CodeQL** (SAST - detect concatenation patterns)
- **Snyk Code** (SAST in CI/CD pipeline)
- **ESLint security plugins** (detect potential XSS in JavaScript)

---

## A04:2021 - Insecure Design

| Metric | Value |
|--------|-------|
| CWEs Mapped | 40 |
| Avg Incidence Rate | 3.00% |
| Total Occurrences | 262,407 |
| Total CVEs | 2,691 |
| 2017 Position | NEW in 2021 |

### What It Is

A broad category representing missing or ineffective security controls at the **design** level. Distinct from implementation bugs: an insecure design cannot be fixed by a perfect implementation, because the necessary security controls were never designed in the first place. This category calls for more threat modeling, secure design patterns, and reference architectures.

### Common Vulnerable Patterns

- **No threat modeling** during design phase
- **Missing business logic security controls** (rate limiting, anti-bot, anti-fraud)
- **No segregation of tenants** in multi-tenant applications
- **Security-through-obscurity** as the primary defense
- **Client-side enforcement of server-side security** (trusting the client)
- **Missing plausibility checks** across application tiers
- **Knowledge-based authentication** (security questions) for credential recovery
- **No resource consumption limits** per user/service

### Real-World Attack Examples

**Scenario 1 - Weak credential recovery:**
A credential recovery workflow uses "security questions," which violates NIST 800-63b. Multiple people can know the answers, making this fundamentally insecure by design.

**Scenario 2 - Business logic abuse:**
A cinema chain allows group booking discounts with max 15 attendees before requiring a deposit. Attackers book 600 seats across all locations simultaneously, causing massive revenue loss.

**Scenario 3 - Missing anti-bot design:**
A retail e-commerce site has no protection against scalper bots buying high-demand products. The design never accounted for automated purchasing behavior.

### Prevention Strategies

1. **Use a Secure Development Lifecycle (SDLC)** with AppSec professionals
2. **Threat modeling** for critical authentication, access control, business logic, and key flows
3. **Establish a library of secure design patterns** ("paved road" components)
4. **Integrate security language into user stories** (misuse cases alongside use cases)
5. **Plausibility checks at every tier** (frontend through backend)
6. **Write unit/integration tests for threat model resistance**
7. **Segregate tenants** robustly by design throughout all tiers
8. **Limit resource consumption** by user or service
9. **Leverage OWASP SAMM** for structuring secure software development

### Detection Tools

- **Microsoft Threat Modeling Tool** (threat modeling)
- **OWASP Threat Dragon** (open-source threat modeling)
- **IriusRisk** (automated threat modeling)
- **Architecture review / manual design review** (most effective)
- **OWASP SAMM** (maturity model assessment)
- **Business logic testing** (manual penetration testing)

---

## A05:2021 - Security Misconfiguration

| Metric | Value |
|--------|-------|
| CWEs Mapped | 20 |
| Avg Incidence Rate | 4.51% |
| Total Occurrences | 208,387 |
| Total CVEs | 789 |
| 2017 Position | #6 (moved up to #5; now includes A4:2017 XXE) |

### What It Is

Missing or incorrect security hardening across the application stack. Includes unnecessary features enabled, default credentials unchanged, overly informative error messages, missing security headers, outdated security features, and insecure cloud service permissions. The former XXE (XML External Entities) category from 2017 is now merged here.

### Common Vulnerable Patterns

- **Improperly configured cloud permissions** (e.g., open S3 buckets)
- **Unnecessary features enabled** (ports, services, pages, accounts, privileges)
- **Default accounts/passwords unchanged** (admin/admin)
- **Verbose error messages** exposing stack traces to users
- **Missing security headers** (CSP, X-Frame-Options, X-Content-Type-Options)
- **Outdated security features** disabled or not configured on upgraded systems
- **Insecure framework/library settings** (Struts, Spring, ASP.NET defaults)
- **XML External Entity (XXE)** processing enabled (merged from 2017 A4)

### Real-World Attack Examples

**Scenario 1 - Unremoved sample applications:**
The production server retains sample applications with known vulnerabilities. Attacker exploits the admin console with default credentials.

**Scenario 2 - Directory listing enabled:**
Server directory listing is not disabled. Attacker lists directories, finds and downloads compiled Java classes, decompiles them, and discovers access control flaws.

**Scenario 3 - Verbose error messages:**
Application returns detailed stack traces including component versions that are known to be vulnerable.

**Scenario 4 - Open cloud storage:**
A cloud service provider has default sharing permissions open to the internet, allowing public access to sensitive data.

### Prevention Strategies

1. **Repeatable hardening process** - Automated, identical configuration across dev/QA/prod (with different credentials)
2. **Minimal platform** - Remove unnecessary features, components, documentation, samples
3. **Regular configuration review** - Part of patch management; review cloud permissions (S3 buckets, etc.)
4. **Segmented application architecture** - Containerization, cloud security groups, ACLs
5. **Security headers** - Send CSP, HSTS, X-Frame-Options, X-Content-Type-Options
6. **Automated verification** - Verify configuration effectiveness in all environments
7. **CIS Benchmarks** - Follow Center for Internet Security hardening guides

### Detection Tools

- **ScoutSuite** (multi-cloud security auditing - AWS, Azure, GCP)
- **Prowler** (AWS security best practices assessment)
- **CIS-CAT** (CIS Benchmark compliance scanning)
- **AWS Config / Azure Policy / GCP Security Command Center** (cloud misconfig detection)
- **Nessus / OpenVAS** (vulnerability scanning including misconfigurations)
- **Mozilla Observatory** (HTTP security header scanning)
- **OWASP ZAP** (misconfiguration detection)
- **tfsec / checkov / trivy** (IaC security scanning for Terraform/CloudFormation)

---

## A06:2021 - Vulnerable and Outdated Components

| Metric | Value |
|--------|-------|
| CWEs Mapped | 3 |
| Avg Incidence Rate | 8.77% |
| Total Occurrences | 30,457 |
| Total CVEs | 0 (default weight 5.0 used) |
| 2017 Position | #9 as "Using Components with Known Vulnerabilities" (moved to #6) |

### What It Is

Using software components (libraries, frameworks, OS, runtime environments) that are vulnerable, unsupported, or out of date. This is the only category with no CVEs directly mapped to its CWEs, reflecting the difficulty of testing and assessing this risk.

### Common Vulnerable Patterns

- **Unknown component versions** - Not tracking client-side and server-side dependencies (including transitive dependencies)
- **Outdated or unsupported software** (OS, web server, DBMS, libraries, runtime)
- **No regular vulnerability scanning** or subscription to security bulletins
- **Delayed patching** - Monthly/quarterly patching cycles leaving exposure windows
- **No compatibility testing** for updated/patched libraries
- **Unsecured component configurations**

### Real-World Attack Examples

**Scenario 1 - Struts 2 RCE (CVE-2017-5638):**
The Apache Struts 2 remote code execution vulnerability enabled arbitrary code execution on the server. This vulnerability was blamed for the Equifax breach (143 million records compromised).

**Scenario 2 - Unpatched IoT devices:**
IoT devices running vulnerable firmware (e.g., Heartbleed-affected OpenSSL) remain exposed because patching is difficult or impossible. The Shodan search engine can locate these devices.

**Scenario 3 - Log4Shell (CVE-2021-44228):**
The Log4j vulnerability allowed remote code execution via a crafted log message. Affected millions of Java applications worldwide.

### Prevention Strategies

1. **Remove unused dependencies** - Unnecessary features, components, files, documentation
2. **Continuous inventory** - Track all component versions using tools (OWASP Dependency Check, retire.js)
3. **Monitor vulnerability sources** - CVE, NVD, GitHub Advisory Database
4. **Use Software Composition Analysis (SCA)** - Automate dependency vulnerability scanning
5. **Obtain components from official sources** - Prefer signed packages
6. **Monitor unmaintained libraries** - Deploy virtual patches if patching is not possible
7. **Ongoing patch management plan** - For the lifetime of the application

### Detection Tools

- **OWASP Dependency Check** (Java, .NET)
- **Snyk** (multi-language SCA)
- **npm audit / yarn audit** (Node.js)
- **pip-audit / safety** (Python)
- **Dependabot** (GitHub automated dependency updates)
- **Renovate** (automated dependency update PRs)
- **Retire.js** (JavaScript library vulnerability detection)
- **Trivy** (container and dependency scanning)
- **Grype / Syft** (SBOM generation and vulnerability scanning)
- **OWASP CycloneDX** (SBOM standard)

---

## A07:2021 - Identification and Authentication Failures

| Metric | Value |
|--------|-------|
| CWEs Mapped | 22 |
| Avg Incidence Rate | 2.55% |
| Total Occurrences | 132,195 |
| Total CVEs | 3,897 |
| 2017 Position | #2 as "Broken Authentication" (dropped to #7) |

### What It Is

Weaknesses in user identity verification, authentication, and session management. Previously called "Broken Authentication," the category was broadened to include identification failures. The drop from #2 to #7 reflects the increased availability of standardized authentication frameworks.

### Common Vulnerable Patterns

- **Credential stuffing allowed** - No protection against automated login attempts with known credential lists
- **Brute force permitted** - No rate limiting on authentication endpoints
- **Default/weak passwords** - "Password1," "admin/admin" accepted
- **Weak credential recovery** - Knowledge-based answers, insecure forgot-password flows
- **Plaintext or weakly hashed passwords** stored in databases
- **Missing MFA** (multi-factor authentication)
- **Session ID in URL**
- **Session ID reused after login** (session fixation)
- **Sessions not invalidated** on logout or after inactivity

### Real-World Attack Examples

**Scenario 1 - Credential stuffing:**
Application has no automated threat protection. Attacker uses lists of breached credentials to test valid username/password combinations at scale.

**Scenario 2 - Password-only authentication:**
Organization relies on password rotation and complexity requirements, which actually encourages weak/reused passwords. NIST 800-63 recommends dropping rotation requirements and using MFA instead.

**Scenario 3 - Improper session timeout:**
User accesses an application on a public computer, closes the browser tab without logging out, and an attacker uses the same browser an hour later to access the still-active session.

### Prevention Strategies

1. **Implement MFA** - Prevents credential stuffing, brute force, and stolen credential reuse
2. **No default credentials** - Especially for admin accounts
3. **Weak password checks** - Test against top 10,000 worst passwords list
4. **NIST 800-63b compliant** password policies (no forced rotation; length over complexity)
5. **Harden against account enumeration** - Same response messages for all outcomes
6. **Rate limit login attempts** - Progressive delays; alert on credential stuffing detection
7. **Server-side session management** - New random session ID with high entropy after login; invalidate on logout/idle/absolute timeout
8. **Session IDs not in URL** - Securely stored, HttpOnly, Secure, SameSite cookies

### Detection Tools

- **Burp Suite Intruder** (credential stuffing / brute force testing)
- **Hydra / Medusa** (offensive - password brute force)
- **OWASP ZAP** (authentication testing)
- **Have I Been Pwned API** (check passwords against breach databases)
- **SonarQube** (SAST - detect weak session management patterns)
- **Nuclei** (template-based vulnerability scanning including auth issues)

---

## A08:2021 - Software and Data Integrity Failures

| Metric | Value |
|--------|-------|
| CWEs Mapped | 10 |
| Avg Incidence Rate | 2.05% |
| Total Occurrences | 47,972 |
| Total CVEs | 1,152 |
| 2017 Position | NEW (absorbs A8:2017 Insecure Deserialization) |

### What It Is

Code and infrastructure that does not protect against integrity violations. Includes: relying on untrusted plugins/libraries/CDNs, insecure CI/CD pipelines allowing unauthorized code/access, auto-update mechanisms without integrity verification, and insecure deserialization (formerly its own category in 2017).

### Common Vulnerable Patterns

- **Unsigned software updates** - Updates applied without verifying digital signatures
- **Untrusted package sources** - npm, Maven dependencies from unverified repositories
- **Insecure CI/CD pipelines** - Insufficient segregation, access control, and configuration
- **No code/configuration review process** - Malicious code can enter the pipeline unchecked
- **Insecure deserialization** - Accepting serialized objects from untrusted sources
- **CDN compromise risk** - Including JavaScript/CSS from third-party CDNs without integrity checks (no SRI)

### Real-World Attack Examples

**Scenario 1 - Unsigned firmware updates:**
Home routers and IoT devices do not verify firmware updates via signatures. Attackers upload malicious firmware with no remediation mechanism.

**Scenario 2 - SolarWinds supply chain attack (2020):**
Nation-state attackers compromised SolarWinds' build process and injected malicious code into Orion updates. 18,000+ organizations received the trojanized update; ~100 were actively exploited. One of the most significant supply chain attacks in history.

**Scenario 3 - Insecure deserialization in Java:**
A React app sends serialized user state to Spring Boot microservices. Attacker recognizes the `rO0` Java object signature (base64) and uses Java Serial Killer to achieve remote code execution.

**Scenario 4 - CodeCov bash uploader compromise (2021):**
Attackers modified the CodeCov bash uploader script to exfiltrate CI/CD environment variables (including secrets and tokens) from customers' CI pipelines.

### Prevention Strategies

1. **Digital signatures** - Verify software/data is from expected source and unaltered
2. **Trusted repositories** - Use internal known-good repositories for high-risk profiles
3. **Software supply chain security tools** - OWASP Dependency Check, OWASP CycloneDX, Sigstore
4. **Code review process** - Review code and configuration changes before merging
5. **CI/CD pipeline security** - Proper segregation, configuration, access control
6. **Integrity checks for serialized data** - Digital signatures or checksums; never send unsigned serialized data to untrusted clients
7. **Subresource Integrity (SRI)** - For CDN-hosted resources in HTML

### Detection Tools

- **Sigstore / Cosign** (software signing and verification)
- **OWASP CycloneDX** (SBOM for supply chain visibility)
- **in-toto** (software supply chain integrity framework)
- **SLSA framework** (Supply-chain Levels for Software Artifacts)
- **Snyk / Socket.dev** (dependency integrity and malicious package detection)
- **ysoserial** (offensive - Java deserialization payload generation)
- **GitGuardian / TruffleHog** (detect secrets in CI/CD)

---

## A09:2021 - Security Logging and Monitoring Failures

| Metric | Value |
|--------|-------|
| CWEs Mapped | 4 |
| Avg Incidence Rate | 6.51% |
| Total Occurrences | 53,615 |
| Total CVEs | 242 |
| 2017 Position | #10 as "Insufficient Logging & Monitoring" (moved to #9) |

### What It Is

Insufficient logging, detection, monitoring, and active response that prevents organizations from detecting, escalating, and responding to active breaches. Without adequate logging and monitoring, breaches cannot be detected. The average time to detect a breach is approximately 200+ days.

### Common Vulnerable Patterns

- **Auditable events not logged** (logins, failed logins, high-value transactions)
- **Inadequate or unclear log messages** for warnings and errors
- **Application/API logs not monitored** for suspicious activity
- **Logs stored only locally** (not centralized)
- **No alerting thresholds or escalation processes**
- **Penetration tests and DAST scans don't trigger alerts**
- **No real-time or near-real-time attack detection**
- **Log data visible to users or attackers** (information leakage)
- **Log injection vulnerabilities** (log data not properly encoded)

### Real-World Attack Examples

**Scenario 1 - Undetected multi-year breach:**
A children's health plan provider could not detect a breach due to no logging or monitoring. Attackers accessed and modified 3.5 million children's health records. The breach may have been ongoing since 2013 -- over 7 years undetected.

**Scenario 2 - Third-party cloud provider breach:**
A major Indian airline had a data breach involving 10+ years of passenger data (passports, credit cards). The breach occurred at a third-party cloud provider who only notified the airline after some time.

**Scenario 3 - Payment application exploit:**
A major European airline suffered a breach where attackers harvested 400,000+ customer payment records via payment application vulnerabilities. The airline was fined 20 million GBP under GDPR.

### Prevention Strategies

1. **Log all critical events** - Logins, failed logins, access control failures, server-side input validation failures with sufficient user context
2. **Use consumable log format** - Structured logging (JSON) that log management tools can easily ingest
3. **Encode log data** - Prevent log injection attacks
4. **Audit trails for high-value transactions** - Append-only tables or immutable logs to prevent tampering
5. **Centralized log management** - Ship logs to a central SIEM (don't store only locally)
6. **Effective monitoring and alerting** - DevSecOps teams should detect and respond to suspicious activities quickly
7. **Incident response plan** - Adopt NIST 800-61r2 or similar

### Detection Tools

- **ELK Stack** (Elasticsearch, Logstash, Kibana - log aggregation and analysis)
- **Splunk** (SIEM and log management)
- **Datadog / Grafana Loki** (cloud-native logging and monitoring)
- **AWS CloudTrail + CloudWatch** / **Azure Monitor** / **GCP Cloud Logging** (cloud-native)
- **OWASP ModSecurity Core Rule Set** (WAF with logging)
- **Falco** (runtime security monitoring for containers/Kubernetes)
- **Wazuh** (open-source SIEM and XDR)

---

## A10:2021 - Server-Side Request Forgery (SSRF)

| Metric | Value |
|--------|-------|
| CWEs Mapped | 1 |
| Avg Incidence Rate | 2.72% |
| Total Occurrences | 9,503 |
| Total CVEs | 385 |
| 2017 Position | NEW (added from community survey #1) |

### What It Is

SSRF flaws occur when a web application fetches a remote resource without validating the user-supplied URL. Attackers coerce the application to send crafted requests to unexpected destinations, even behind firewalls, VPNs, or network ACLs. The severity is increasing due to cloud services and complex architectures (particularly cloud metadata services).

### Common Vulnerable Patterns

- **URL fetching without validation** - Application fetches user-supplied URLs without allowlist
- **Access to internal services** - Application can reach internal networks, localhost, or cloud metadata
- **Cloud metadata endpoint access** - `http://169.254.169.254/` on AWS/GCP/Azure
- **Port scanning via SSRF** - Mapping internal network topology through the application
- **Protocol smuggling** - Using `file://`, `dict://`, `gopher://` schemes

### Real-World Attack Examples

**Scenario 1 - Internal port scanning:**
If the network is unsegmented, attackers map internal networks and determine open/closed ports by observing connection timing in SSRF responses.

**Scenario 2 - Local file access:**
Attacker uses `file:///etc/passwd` or `http://localhost:28017/` to access local files or internal services.

**Scenario 3 - Cloud metadata theft (Capital One breach pattern):**
Attacker accesses `http://169.254.169.254/latest/meta-data/iam/security-credentials/` to steal IAM role credentials from the cloud metadata service. This pattern was used in the Capital One breach (2019).

**Scenario 4 - Internal service compromise:**
Attacker abuses internal services via SSRF to conduct further RCE or DoS attacks against backend systems.

### Prevention Strategies

**Network Layer:**
1. **Segment remote resource access** - Isolate URL fetching functionality in separate networks
2. **Deny-by-default firewall rules** - Block all but essential intranet traffic
3. **Log all accepted and blocked network flows**

**Application Layer:**
1. **Sanitize and validate all client-supplied input**
2. **Positive allow list** - Enforce URL schema, port, and destination allowlists
3. **Don't send raw responses to clients** - Prevent information leakage
4. **Disable HTTP redirections** - Prevent redirect-based bypasses
5. **URL consistency awareness** - Guard against DNS rebinding and TOCTOU attacks

**Never rely on deny lists or regex alone** - Attackers have extensive bypass techniques.

**Additional:**
- Don't deploy security-relevant services on front-facing systems
- Use IMDSv2 on AWS (requires session token for metadata access)

### Detection Tools

- **Burp Suite Collaborator** (SSRF detection via out-of-band interactions)
- **SSRFmap** (automated SSRF exploitation)
- **OWASP ZAP** (SSRF scanning)
- **Nuclei** (SSRF detection templates)
- **Cloud metadata protection** - AWS IMDSv2, GCP metadata concealment, Azure IMDS restrictions

---

## Changes: 2017 to 2021

### Category Movement Map

| 2017 | | 2021 |
|------|-|------|
| A1: Injection | --> | A3: Injection (dropped, now includes XSS) |
| A2: Broken Authentication | --> | A7: Identification and Authentication Failures (renamed, dropped) |
| A3: Sensitive Data Exposure | --> | A2: Cryptographic Failures (renamed to root cause) |
| A4: XML External Entities (XXE) | --> | Merged into A5: Security Misconfiguration |
| A5: Broken Access Control | --> | A1: Broken Access Control (rose to #1) |
| A6: Security Misconfiguration | --> | A5: Security Misconfiguration (now includes XXE) |
| A7: Cross-Site Scripting (XSS) | --> | Merged into A3: Injection |
| A8: Insecure Deserialization | --> | Merged into A8: Software and Data Integrity Failures |
| A9: Using Components with Known Vulns | --> | A6: Vulnerable and Outdated Components (renamed) |
| A10: Insufficient Logging & Monitoring | --> | A9: Security Logging and Monitoring Failures (renamed) |

### Three New Categories in 2021

1. **A04: Insecure Design** - Entirely new; focuses on design-level security flaws, not implementation bugs
2. **A08: Software and Data Integrity Failures** - New category; absorbs "Insecure Deserialization" and adds CI/CD pipeline integrity, supply chain concerns
3. **A10: Server-Side Request Forgery (SSRF)** - New; added from community survey vote #1

### Key Themes in the 2017-to-2021 Shift

- **Root cause over symptom**: "Sensitive Data Exposure" became "Cryptographic Failures"; "Broken Authentication" became "Identification and Authentication Failures"
- **Consolidation**: XSS merged into Injection; XXE merged into Security Misconfiguration; Insecure Deserialization merged into Software and Data Integrity Failures
- **Shift-left emphasis**: Insecure Design category pushes security into architecture/design phase
- **Supply chain awareness**: Software and Data Integrity Failures reflects the post-SolarWinds reality
- **Cloud-native threats**: SSRF added to recognize cloud metadata and internal service attack vectors
- **Data-driven methodology**: Incidence rate based on 500K+ applications; CVSS exploit/impact scoring

---

## OWASP Top 10 2025 - What Changed

The OWASP Top 10 2025 has been officially released (owasp.org now redirects to 2025). Here is the updated list and key changes:

### 2025 Category List

| # | 2025 Category | 2021 Equivalent |
|---|---------------|-----------------|
| A01 | Broken Access Control | A01:2021 (same) |
| A02 | Security Misconfiguration | A05:2021 (moved up from #5) |
| A03 | **Software Supply Chain Failures** | Evolved from A06:2021 + A08:2021 |
| A04 | Cryptographic Failures | A02:2021 (moved down from #2) |
| A05 | Injection | A03:2021 (moved down from #3) |
| A06 | Insecure Design | A04:2021 (moved down from #4) |
| A07 | Authentication Failures | A07:2021 (renamed) |
| A08 | Software or Data Integrity Failures | A08:2021 (similar) |
| A09 | Security Logging and Alerting Failures | A09:2021 (renamed: "Alerting" replaces "Monitoring") |
| A10 | **Mishandling of Exceptional Conditions** | NEW (replaces SSRF) |

### Key Changes in 2025

1. **Security Misconfiguration surged to #2** - Reflects the explosion of cloud misconfigurations, IaC complexity, and highly configurable software
2. **Software Supply Chain Failures is a new standalone category (#3)** - Evolved from "Vulnerable and Outdated Components" but now covers the entire supply chain: IDE security, code repository integrity, build pipeline hardening, artifact verification, transitive dependencies, and separation of duty
3. **SSRF was removed as a standalone category** - Likely absorbed into other categories
4. **Mishandling of Exceptional Conditions is new (#10)** - Focuses on improper error handling, failing open, logic bugs, NULL pointer dereferences, race conditions, and unhandled exceptions
5. **Logging category renamed** from "Monitoring" to "Alerting" - Emphasizes active alerting over passive monitoring
6. **Injection dropped from #3 to #5** - Reflecting improved framework-level protections

---

## OWASP Top 10 and DevOps/Cloud/Infrastructure Security

The OWASP Top 10 is traditionally web-application-focused, but many categories have direct relevance to DevOps, Cloud Engineering, and Infrastructure/Platform Engineering roles:

### Direct Cloud/Infrastructure Relevance by Category

| OWASP Category | DevOps/Cloud/Infra Relevance |
|----------------|------------------------------|
| **A01: Broken Access Control** | IAM policies, S3 bucket policies, RBAC in Kubernetes, least-privilege service accounts, cross-account access |
| **A02: Cryptographic Failures** | TLS termination at load balancers, certificate management (ACM, Let's Encrypt), KMS key rotation, secrets management (Vault, AWS Secrets Manager), encryption at rest for EBS/S3/RDS |
| **A03: Injection** | SQL injection in database-backed services, OS command injection in automation scripts, template injection in IaC (Terraform variable interpolation) |
| **A04: Insecure Design** | Network architecture design (VPC segmentation, private subnets), zero-trust architecture, threat modeling for infrastructure |
| **A05: Security Misconfiguration** | THE most relevant category: cloud security groups, NACLs, S3 public access, database public endpoints, default credentials on services, Docker/K8s misconfigurations, IaC drift |
| **A06: Vulnerable Components** | Base image vulnerabilities (Docker), outdated AMIs, unpatched OS packages, Terraform provider vulnerabilities, Helm chart dependencies |
| **A07: Auth Failures** | Service-to-service authentication, API key management, OAuth/OIDC for infrastructure APIs, SSO configuration, K8s service account tokens |
| **A08: Integrity Failures** | CI/CD pipeline security (GitHub Actions, GitLab CI), artifact signing, container image signing (Cosign/Notary), IaC integrity, GitOps pull-based deployment |
| **A09: Logging Failures** | CloudTrail/CloudWatch/VPC Flow Logs, centralized logging (ELK/Datadog), K8s audit logs, alerting on security events, incident response |
| **A10: SSRF** | Cloud metadata service attacks (IMDSv1), VPC endpoint design, internal service mesh security, network segmentation |

### Key DevOps/Cloud Security Practices Mapped to OWASP

**Infrastructure as Code (IaC) Security:**
- Scan Terraform/CloudFormation with tfsec, checkov, trivy, or Bridgecrew
- Maps to: A05 (Misconfiguration), A04 (Insecure Design)

**Container Security:**
- Scan images with Trivy, Grype; use minimal base images; sign images with Cosign
- Maps to: A06 (Vulnerable Components), A08 (Integrity Failures)

**CI/CD Pipeline Security:**
- Secure GitHub Actions workflows, restrict permissions, pin action versions, use OIDC for cloud access
- Maps to: A08 (Integrity Failures), A01 (Access Control)

**Secrets Management:**
- Use Vault/AWS Secrets Manager/Azure Key Vault; never hardcode secrets; rotate credentials
- Maps to: A02 (Cryptographic Failures), A05 (Misconfiguration)

**Cloud IAM:**
- Least privilege, no wildcard permissions, use conditions/boundaries, enable MFA
- Maps to: A01 (Access Control), A07 (Auth Failures)

**Network Security:**
- VPC segmentation, private subnets for databases, NACLs, security groups, IMDSv2
- Maps to: A05 (Misconfiguration), A10 (SSRF), A04 (Insecure Design)

**Monitoring and Incident Response:**
- Enable CloudTrail, VPC Flow Logs, K8s audit logs; centralize in SIEM; set up alerts
- Maps to: A09 (Logging Failures)

### Related OWASP Projects for DevOps/Cloud

| Project | Focus |
|---------|-------|
| **OWASP Cloud-Native Application Security Top 10** | Cloud-native specific risks |
| **OWASP Docker Security Cheat Sheet** | Container security |
| **OWASP Kubernetes Security Cheat Sheet** | K8s-specific security |
| **OWASP CI/CD Security Top 10** | CI/CD pipeline risks |
| **OWASP Infrastructure as Code Security Cheat Sheet** | IaC security |
| **OWASP API Security Top 10** | API-specific risks (complementary to Top 10) |

---

## Detection Tools Summary

### By Tool Type

**SAST (Static Application Security Testing):**
- SonarQube, Semgrep, CodeQL, Checkmarx, Fortify, Snyk Code

**DAST (Dynamic Application Security Testing):**
- OWASP ZAP, Burp Suite, Nuclei, Acunetix, Qualys WAS

**IAST (Interactive Application Security Testing):**
- Contrast Security, Hdiv Security

**SCA (Software Composition Analysis):**
- OWASP Dependency Check, Snyk, Dependabot, Renovate, Trivy, Grype

**IaC Security Scanning:**
- tfsec, checkov, trivy, Bridgecrew, KICS

**Cloud Security Posture Management (CSPM):**
- Prowler, ScoutSuite, AWS Security Hub, Azure Defender, GCP Security Command Center

**Container Security:**
- Trivy, Grype, Falco, Cosign/Notary, Docker Bench Security

**Secrets Detection:**
- GitGuardian, TruffleHog, detect-secrets, gitleaks

**SIEM / Monitoring:**
- ELK Stack, Splunk, Datadog, Wazuh, Grafana Loki

### By OWASP Category

| Category | Primary Tools |
|----------|--------------|
| A01: Access Control | Burp Suite, ZAP, Semgrep, manual testing |
| A02: Crypto Failures | SSL Labs, testssl.sh, SonarQube, Mozilla Observatory |
| A03: Injection | SQLMap, ZAP, Burp Suite, SonarQube, CodeQL |
| A04: Insecure Design | Threat Dragon, Microsoft TMT, IriusRisk, manual review |
| A05: Misconfiguration | ScoutSuite, Prowler, CIS-CAT, tfsec, checkov |
| A06: Vulnerable Components | Dependency Check, Snyk, Trivy, Dependabot, Grype |
| A07: Auth Failures | Burp Suite, Hydra, ZAP, Have I Been Pwned API |
| A08: Integrity Failures | Sigstore/Cosign, CycloneDX, in-toto, Socket.dev |
| A09: Logging Failures | ELK, Splunk, CloudTrail, Wazuh, Falco |
| A10: SSRF | Burp Collaborator, SSRFmap, Nuclei, ZAP |
