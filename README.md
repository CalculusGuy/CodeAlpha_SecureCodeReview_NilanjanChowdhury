## README.MD

```markdown
# 🔐 Secure Code Review — CodeAlpha Task 3
```

**Author:** Nilanjan Chowdhury  
**Date:** June 28, 2026  
**Internship:** CodeAlpha Cyber Security Internship  

---

## 📌 Project Overview

This repository contains a **complete secure code review** performed on a vulnerable Python Flask web application. The review identified **10 security vulnerabilities**, documented them with **Proof of Concept (PoC) commands**, and provided a **fully fixed secure version**.

---

## 🗂️ Repository Structure
CodeAlpha_SecureCodeReview/
├── vulnerable_app.py # Original app with 10 vulns
├── secure_app.py # Fully fixed secure version
├── security_review_report.md # Complete audit report
├── README.md # This file
└── screenshots/ # PoC evidence
├── sqli-poc.png
├── command-injection-poc.png
├── admin-access-poc.png
├── debug-poc.png
├── deserialization-poc.png
└── ...

text

---

## 🔍 Vulnerabilities Found & Fixed

| # | Vulnerability | Severity | Status |
|---|---------------|----------|--------|
| 1 | SQL Injection | 🔴 Critical | ✅ Fixed |
| 2 | Command Injection | 🔴 Critical | ✅ Fixed |
| 3 | Path Traversal | 🔴 Critical | ✅ Fixed |
| 4 | Insecure File Upload | 🟠 High | ✅ Fixed |
| 5 | Insecure Deserialization | 🔴 Critical | ✅ Fixed |
| 6 | Hardcoded Credentials | 🔴 Critical | ✅ Fixed |
| 7 | Weak Cryptography (MD5) | 🟠 High | ✅ Fixed |
| 8 | Sensitive Data Exposure | 🟡 Medium | ✅ Fixed |
| 9 | Information Disclosure | 🟡 Medium | ✅ Fixed |
| 10 | Broken Access Control | 🟠 High | ✅ Fixed |

---

## 🚀 Usage

### Running the Vulnerable App

```bash
sudo python3 vulnerable_app.py
```
⚠️ WARNING: This app is intentionally vulnerable. DO NOT deploy in production.

Running the Secure App
bash
python3 secure_app.py
Test login:

```bash
curl -X POST http://127.0.0.1:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "SecureAdmin123!"}'
```
🧪 PoC Examples
SQL Injection
```bash
curl -X POST http://127.0.0.1:5000/login -d "username=admin' --&password=anything"
```
Command Injection (RCE)
```bash
curl "http://127.0.0.1:5000/ping?host=127.0.0.1;id"
```
Insecure Deserialization (RCE)
python
import pickle, base64, subprocess
class Exploit:
    def __reduce__(self):
        return (subprocess.check_output, (["id"],))
payload = base64.b64encode(pickle.dumps(Exploit()))
print(payload.decode())
```bash
curl "http://127.0.0.1:5000/profile?data=<PAYLOAD>"
```
🛠️ Key Fixes Applied
Vulnerability	Fix
SQL Injection	Parameterized queries
Command Injection	shell=False, input validation
Insecure Deserialization	JSON instead of pickle
Hardcoded Credentials	Environment variables
Weak Cryptography	bcrypt hashing
Broken Access Control	@login_required + @admin_required
Path Traversal	os.path.abspath() + secure_filename
Insecure File Upload	Extension whitelist + size limits
Information Disclosure	Generic error messages
Sensitive Data Exposure	Removed /debug endpoint
📚 Full Report
Detailed findings, PoC outputs, and remediation steps are available in:
👉 security_review_report.md

👤 Author
Nilanjan Chowdhury

GitHub: CalculusGuy

TryHackMe: Top 3% Global, Diamond League

LinkedIn: Nilanjan Chowdhury

Medium: @nilanjan.calculus

📌 Disclaimer
This project is for educational purposes only. The vulnerable app must never be deployed in a real environment.

⭐ Acknowledgments
CodeAlpha Internship Program

The original author for the vulnerable app reference

📅 Timeline
Review Started: June 28, 2026

All Vulns Identified & Fixed: June 28, 2026

Report Completed: June 28, 2026

