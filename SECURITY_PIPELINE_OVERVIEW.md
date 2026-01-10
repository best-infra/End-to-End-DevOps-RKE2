# CI/CD Pipeline with Security Notifications

## Pipeline Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         GitHub Push/PR Trigger                          │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Job 1: detect-changes                                                  │
│  ├─ Check which services changed (auth/task/frontend/nginx)            │
│  └─ Output: Service change flags                                       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
    ┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐
    │ Job 2:            │ │ Job 3:            │ │ Jobs 4-5:         │
    │ build-auth        │ │ build-task        │ │ build-frontend    │
    │                   │ │                   │ │ build-nginx       │
    │ ├─ Build image    │ │ ├─ Build image    │ │ ├─ Build image    │
    │ ├─ Trivy SARIF    │ │ ├─ Trivy SARIF    │ │ ├─ Trivy SARIF    │
    │ ├─ Trivy JSON  📊 │ │ ├─ Trivy JSON  📊 │ │ ├─ Trivy JSON  📊 │
    │ ├─ Upload SARIF   │ │ ├─ Upload SARIF   │ │ ├─ Upload SARIF   │
    │ ├─ Upload JSON    │ │ ├─ Upload JSON    │ │ ├─ Upload JSON    │
    │ └─ Push image     │ │ └─ Push image     │ │ └─ Push image     │
    └───────────────────┘ └───────────────────┘ └───────────────────┘
                    │               │               │
                    └───────────────┼───────────────┘
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Job 6: vulnerability-notification  🔒                                  │
│  ├─ Download all Trivy JSON results                                    │
│  ├─ Parse vulnerabilities (CRITICAL/HIGH/MEDIUM)                       │
│  ├─ Generate vulnerability report (Markdown)                           │
│  ├─ Count by severity: CRITICAL, HIGH, MEDIUM                          │
│  ├─ Send Slack notification 💬 (if CRITICAL/HIGH found)                │
│  ├─ Send Email notification 📧 (if CRITICAL/HIGH found)                │
│  └─ Upload vulnerability report artifact                               │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Job 7: update-k8s-manifests                                            │
│  ├─ Download image tag artifacts                                       │
│  ├─ Update K8s deployment manifests with new tags                      │
│  └─ Commit and push changes [skip ci]                                  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Job 8: pipeline-summary                                                │
│  └─ Generate GitHub Actions summary with all results                   │
└─────────────────────────────────────────────────────────────────────────┘
```

## New Features Added ✨

### 1. Dual Format Trivy Scans
- **SARIF format:** Uploaded to GitHub Security → Code Scanning
- **JSON format:** Used for parsing and notifications

### 2. Vulnerability Collection & Parsing
- Collects results from all services
- Counts vulnerabilities by severity (CRITICAL, HIGH, MEDIUM)
- Generates detailed Markdown report with:
  - Summary statistics
  - Per-service breakdown
  - CVE IDs and package details
  - Vulnerability descriptions

### 3. Slack Notifications 💬
Sends when CRITICAL or HIGH vulnerabilities found:
```
🔴 Security Vulnerabilities Detected
Security scan found vulnerabilities in your-org/your-repo

Critical: 5    High: 12
Medium: 25     Branch: master
Commit: abc123def456
```

### 4. Email Notifications 📧
Sends full vulnerability report via email:
- Formatted Markdown converted to HTML
- Complete CVE list with details
- High priority flag
- Customizable SMTP settings

### 5. Artifacts & Reports
- `trivy-auth-results`: JSON scan for auth service
- `trivy-task-results`: JSON scan for task service
- `trivy-frontend-results`: JSON scan for frontend
- `trivy-nginx-results`: JSON scan for nginx
- `vulnerability-report`: Combined Markdown report

## Configuration Required

### For Slack (Optional):
```
SLACK_WEBHOOK_URL
```

### For Email (Optional):
```
MAIL_SERVER
MAIL_PORT (default: 587)
MAIL_USERNAME
MAIL_PASSWORD
MAIL_TO
MAIL_FROM (optional)
```

### GitHub Secrets Location
Repository → Settings → Secrets and variables → Actions → New repository secret

## Notification Triggers

| Severity Level | Included in Report | Triggers Notification |
|---------------|-------------------|----------------------|
| 🔴 CRITICAL   | ✅ Yes            | ✅ Yes               |
| 🟠 HIGH       | ✅ Yes            | ✅ Yes               |
| 🟡 MEDIUM     | ✅ Yes            | ❌ No                |
| 🔵 LOW        | ❌ No             | ❌ No                |

## Report Contents

### Summary Section
- Total vulnerabilities by severity
- Repository and commit information
- Scan timestamp

### Per-Service Sections
For each service (auth, task, frontend, nginx):
- Vulnerability count table
- List of CRITICAL vulnerabilities with CVE IDs
- List of HIGH vulnerabilities with CVE IDs
- Package names and versions
- Brief descriptions

### Example Entry
```
- CVE-2024-1234: openssl (1.1.1k) - Buffer overflow in SSL/TLS
```

## Benefits

1. **Immediate Awareness:** Get notified as soon as vulnerabilities are found
2. **Detailed Reports:** Full CVE information for remediation
3. **Multiple Channels:** Slack for quick alerts, Email for detailed review
4. **Historical Tracking:** All reports saved as artifacts
5. **GitHub Integration:** SARIF results in Security tab
6. **Automated:** No manual checking required
7. **Flexible:** Configure Slack, Email, or both

## Next Steps

1. Configure secrets (see SECURITY_NOTIFICATIONS_QUICK.md)
2. Push a change to trigger the pipeline
3. Check notifications and reports
4. Set up a process for handling security alerts
5. Regularly review and update vulnerable packages

## Additional Documentation

- **Quick Start:** [SECURITY_NOTIFICATIONS_QUICK.md](./SECURITY_NOTIFICATIONS_QUICK.md)
- **Full Guide:** [SECURITY_NOTIFICATIONS.md](./SECURITY_NOTIFICATIONS.md)
- **CI/CD Overview:** [GITHUB_ACTIONS_GUIDE.md](./GITHUB_ACTIONS_GUIDE.md)
