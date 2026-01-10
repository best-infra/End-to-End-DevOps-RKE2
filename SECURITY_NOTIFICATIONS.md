# Security Vulnerability Notifications

This document explains how to configure email and Slack notifications for security vulnerabilities detected by Trivy scans in the CI/CD pipeline.

## Overview

The CI/CD pipeline automatically:
1. Scans all Docker images with Trivy for CRITICAL, HIGH, and MEDIUM vulnerabilities
2. Generates a detailed vulnerability report
3. Sends notifications to Slack and/or Email when CRITICAL or HIGH vulnerabilities are found
4. Uploads the full report as a GitHub Actions artifact

## Configuration

### Required GitHub Secrets

Configure these secrets in your GitHub repository settings (`Settings` → `Secrets and variables` → `Actions`):

### 1. Slack Notifications

To enable Slack notifications:

1. **Create a Slack Webhook URL:**
   - Go to https://api.slack.com/apps
   - Click "Create New App" → "From scratch"
   - Name your app (e.g., "Security Alerts") and select your workspace
   - Go to "Incoming Webhooks" and activate it
   - Click "Add New Webhook to Workspace"
   - Select the channel where you want to receive alerts
   - Copy the Webhook URL

2. **Add to GitHub Secrets:**
   ```
   Secret Name: SLACK_WEBHOOK_URL
   Value: https://hooks.slack.com/services/YOUR/WEBHOOK/URL
   ```

### 2. Email Notifications

To enable email notifications, add these secrets:

#### Gmail (Recommended for testing)

1. **Enable 2-Step Verification** on your Gmail account
2. **Generate an App Password:**
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other (Custom name)"
   - Name it "GitHub Actions"
   - Copy the 16-character password

3. **Add to GitHub Secrets:**
   ```
   MAIL_SERVER: smtp.gmail.com
   MAIL_PORT: 587
   MAIL_USERNAME: your-email@gmail.com
   MAIL_PASSWORD: your-16-char-app-password
   MAIL_TO: security-team@example.com
   MAIL_FROM: your-email@gmail.com (optional, defaults to MAIL_USERNAME)
   ```

#### Other SMTP Providers

**SendGrid:**
```
MAIL_SERVER: smtp.sendgrid.net
MAIL_PORT: 587
MAIL_USERNAME: apikey
MAIL_PASSWORD: your-sendgrid-api-key
MAIL_TO: security-team@example.com
MAIL_FROM: noreply@yourdomain.com
```

**Office 365:**
```
MAIL_SERVER: smtp.office365.com
MAIL_PORT: 587
MAIL_USERNAME: your-email@company.com
MAIL_PASSWORD: your-password
MAIL_TO: security-team@company.com
MAIL_FROM: your-email@company.com
```

**AWS SES:**
```
MAIL_SERVER: email-smtp.us-east-1.amazonaws.com
MAIL_PORT: 587
MAIL_USERNAME: your-ses-smtp-username
MAIL_PASSWORD: your-ses-smtp-password
MAIL_TO: security-team@example.com
MAIL_FROM: verified-sender@yourdomain.com
```

## Notification Behavior

### When Notifications Are Sent

Notifications are triggered when:
- ✅ Trivy scan finds **CRITICAL** vulnerabilities
- ✅ Trivy scan finds **HIGH** vulnerabilities
- ❌ Only MEDIUM or LOW vulnerabilities (no notification)

### Notification Content

**Slack Message includes:**
- Severity color indicator (red for critical, orange for high)
- Total count of vulnerabilities by severity
- Repository name and branch
- Commit SHA with link
- Timestamp

**Email includes:**
- Full vulnerability report in Markdown format
- Detailed list of all CRITICAL and HIGH vulnerabilities
- Package names, versions, and CVE IDs
- Links to vulnerability details

### Report Format

The vulnerability report includes:
- **Summary:** Total counts by severity
- **Per-Service Breakdown:** Separate sections for auth, task, frontend, and nginx services
- **Vulnerability Details:** CVE IDs, affected packages, installed versions, and descriptions
- **Metadata:** Repository, commit, branch, and scan timestamp

## Example Vulnerability Report

```markdown
# 🔒 Security Vulnerability Report

**Repository:** your-org/your-repo
**Commit:** abc123def456
**Branch:** master
**Scan Date:** 2026-01-10 12:00:00 UTC

---

## 📦 AUTH Service

| Severity | Count |
|----------|-------|
| 🔴 CRITICAL | 2 |
| 🟠 HIGH | 5 |
| 🟡 MEDIUM | 10 |

### 🔴 Critical Vulnerabilities

- **CVE-2024-1234**: openssl (1.1.1k) - Buffer overflow in SSL/TLS implementation
- **CVE-2024-5678**: npm (8.1.0) - Remote code execution vulnerability

### 🟠 High Vulnerabilities

- **CVE-2024-9012**: express (4.17.1) - Path traversal vulnerability
- **CVE-2024-3456**: node (16.14.0) - Denial of service vulnerability
...

---

## 📊 Summary

**Total Vulnerabilities Found:**
- 🔴 Critical: 5
- 🟠 High: 12
- 🟡 Medium: 25
```

## Viewing Reports

### GitHub Actions UI

1. Go to your repository → `Actions` tab
2. Click on a completed workflow run
3. Scroll to "Artifacts" section
4. Download `vulnerability-report` artifact

### GitHub Security Tab

SARIF files are automatically uploaded to GitHub Security:
1. Go to your repository → `Security` tab
2. Click on "Code scanning alerts"
3. View detailed vulnerability information

## Testing Notifications

To test your notification setup:

1. **Make a small change** to trigger the pipeline:
   ```bash
   echo "# Test change" >> services/auth-service/README.md
   git add .
   git commit -m "test: trigger security scan"
   git push
   ```

2. **Check the workflow:**
   - Go to Actions tab
   - Wait for the "Vulnerability Notification" job to complete
   - Check your Slack channel or email inbox

3. **Troubleshooting:**
   - If no notification received, check the workflow logs
   - Verify secrets are correctly configured
   - Ensure the scan found CRITICAL or HIGH vulnerabilities
   - Check Slack channel permissions
   - Verify email server settings

## Customization

### Change Notification Threshold

Edit [.github/workflows/ci-cd-pipeline.yml](.github/workflows/ci-cd-pipeline.yml):

```yaml
# Currently sends on CRITICAL or HIGH
- name: Send Slack notification
  if: steps.parse-vulns.outputs.total_critical > 0 || steps.parse-vulns.outputs.total_high > 0

# To send on MEDIUM as well:
- name: Send Slack notification
  if: steps.parse-vulns.outputs.total_critical > 0 || steps.parse-vulns.outputs.total_high > 0 || steps.parse-vulns.outputs.total_medium > 0
```

### Change Scan Severity Levels

Edit the Trivy scan steps:

```yaml
# Currently scans for CRITICAL, HIGH, MEDIUM
severity: 'CRITICAL,HIGH,MEDIUM'

# To include LOW:
severity: 'CRITICAL,HIGH,MEDIUM,LOW'

# To only scan CRITICAL:
severity: 'CRITICAL'
```

### Customize Slack Message

Modify the `Send Slack notification` step in the workflow to change:
- Message format
- Color coding
- Additional fields
- Emoji indicators

### Add Multiple Recipients

For email, use comma-separated addresses:
```
MAIL_TO: security@example.com,devops@example.com,admin@example.com
```

For Slack, create multiple webhook secrets and add separate notification steps.

## Troubleshooting

### Slack Notifications Not Received

1. **Verify webhook URL:**
   ```bash
   curl -X POST "$SLACK_WEBHOOK_URL" \
     -H 'Content-Type: application/json' \
     -d '{"text":"Test message from GitHub Actions"}'
   ```

2. **Check workflow logs** for error messages
3. **Verify channel permissions** for the webhook
4. **Check if the app is still installed** in your workspace

### Email Notifications Not Received

1. **Check spam/junk folder**
2. **Verify SMTP credentials:**
   - Try logging into the mail server manually
   - Check if the account is locked
   - Verify 2FA is configured correctly

3. **Check workflow logs** for SMTP errors
4. **Test SMTP connection:**
   ```bash
   openssl s_client -starttls smtp -connect smtp.gmail.com:587
   ```

### No Vulnerabilities Detected

If your images are clean (no CRITICAL/HIGH vulnerabilities):
1. This is good! Your images are secure
2. Notifications only trigger on CRITICAL/HIGH vulnerabilities
3. Check the workflow artifacts for the full report including MEDIUM severity

### Workflow Fails

1. **Check required secrets are configured**
2. **Verify JSON parsing** - ensure Trivy results are valid
3. **Check artifact download** - ensure scan results are uploaded
4. **Review workflow logs** for specific error messages

## Best Practices

1. **Monitor regularly:** Check security alerts weekly even without notifications
2. **Act quickly:** Address CRITICAL vulnerabilities within 24 hours
3. **Update dependencies:** Keep base images and packages up to date
4. **Review reports:** Don't ignore MEDIUM severity vulnerabilities
5. **Test notifications:** Verify your setup works before relying on it
6. **Document process:** Create runbooks for handling security alerts
7. **Track remediation:** Use GitHub Issues to track vulnerability fixes

## Additional Resources

- [Trivy Documentation](https://aquasecurity.github.io/trivy/)
- [GitHub Actions Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Slack Incoming Webhooks](https://api.slack.com/messaging/webhooks)
- [SMTP Configuration Guide](https://mailtrap.io/blog/smtp-commands-and-responses/)
- [CVE Database](https://cve.mitre.org/)
- [National Vulnerability Database](https://nvd.nist.gov/)
