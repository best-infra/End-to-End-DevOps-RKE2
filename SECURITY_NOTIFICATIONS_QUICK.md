# Security Notifications - Quick Setup Guide

## 🚀 Quick Start (5 minutes)

### Option 1: Slack Only

1. Create Slack webhook at https://api.slack.com/apps
2. Add GitHub secret:
   ```
   SLACK_WEBHOOK_URL = https://hooks.slack.com/services/YOUR/WEBHOOK/URL
   ```
3. Done! Push a change to test.

### Option 2: Email Only (Gmail)

1. Enable 2FA on Gmail
2. Get app password: https://myaccount.google.com/apppasswords
3. Add GitHub secrets:
   ```
   MAIL_SERVER = smtp.gmail.com
   MAIL_PORT = 587
   MAIL_USERNAME = your-email@gmail.com
   MAIL_PASSWORD = your-16-char-app-password
   MAIL_TO = team@example.com
   ```
4. Done! Push a change to test.

### Option 3: Both Slack + Email

Combine the secrets from both options above.

---

## 📊 What Gets Scanned

- ✅ Auth Service Docker image
- ✅ Task Service Docker image
- ✅ Frontend Docker image
- ✅ Nginx Docker image

Severity levels: CRITICAL, HIGH, MEDIUM

---

## 🔔 When Notifications Are Sent

| Severity | Notification Sent? |
|----------|-------------------|
| 🔴 CRITICAL | ✅ Yes |
| 🟠 HIGH | ✅ Yes |
| 🟡 MEDIUM | ❌ No (but included in report) |
| 🔵 LOW | ❌ No |

---

## 🔧 GitHub Secrets Reference

### Slack
```
SLACK_WEBHOOK_URL (required)
```

### Email
```
MAIL_SERVER (required) - e.g., smtp.gmail.com
MAIL_PORT (optional) - default: 587
MAIL_USERNAME (required)
MAIL_PASSWORD (required)
MAIL_TO (required) - can be comma-separated
MAIL_FROM (optional) - defaults to MAIL_USERNAME
```

---

## 📝 Common SMTP Settings

### Gmail
```
MAIL_SERVER: smtp.gmail.com
MAIL_PORT: 587
```

### SendGrid
```
MAIL_SERVER: smtp.sendgrid.net
MAIL_PORT: 587
MAIL_USERNAME: apikey
```

### Office 365
```
MAIL_SERVER: smtp.office365.com
MAIL_PORT: 587
```

### AWS SES
```
MAIL_SERVER: email-smtp.us-east-1.amazonaws.com
MAIL_PORT: 587
```

---

## 🧪 Testing

```bash
# Trigger the pipeline
echo "# Test" >> services/auth-service/README.md
git add .
git commit -m "test: trigger scan"
git push
```

Then check:
1. GitHub Actions → Your workflow run
2. Slack channel (if configured)
3. Email inbox (if configured)
4. Artifacts section for full report

---

## 📂 Where to Find Reports

1. **GitHub Actions Artifacts:**
   - Actions tab → Workflow run → Scroll to Artifacts
   - Download `vulnerability-report`

2. **GitHub Security Tab:**
   - Security → Code scanning alerts
   - View SARIF results

3. **Slack:** Real-time notification with summary

4. **Email:** Full report with all details

---

## ⚡ Troubleshooting

**No notification received?**
- Check if scan found CRITICAL/HIGH vulnerabilities
- Verify secrets are configured correctly
- Check workflow logs for errors
- Ensure Slack webhook is active
- Check email spam folder

**Slack not working?**
```bash
# Test webhook
curl -X POST "$SLACK_WEBHOOK_URL" \
  -H 'Content-Type: application/json' \
  -d '{"text":"Test from CI/CD"}'
```

**Email not working?**
- Check SMTP credentials
- Verify app password (not regular password)
- Check 2FA is enabled
- Look at workflow logs for SMTP errors

---

## 📚 Full Documentation

See [SECURITY_NOTIFICATIONS.md](./SECURITY_NOTIFICATIONS.md) for:
- Detailed configuration
- Customization options
- Report format examples
- Best practices
- Advanced troubleshooting

---

## 🎯 Next Steps

1. ✅ Configure at least one notification method (Slack or Email)
2. ✅ Test by pushing a change
3. ✅ Review the generated report
4. ✅ Set up a process to handle alerts
5. ✅ Monitor regularly and keep images updated
