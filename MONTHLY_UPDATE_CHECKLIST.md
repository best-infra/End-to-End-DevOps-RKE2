# Monthly Dependency Update Checklist

**Schedule:** First Monday of every month  
**Time:** ~1-2 hours  
**Owner:** DevOps/Security Team

---

## 🔄 Automated Process

### Dependabot (Automatic)
- ✅ Runs automatically every month
- ✅ Creates individual PRs for each dependency update
- ✅ Only updates minor/patch versions (not major breaking changes)
- ✅ Includes security advisories in PR description

**Action Required:** Review and merge Dependabot PRs when created

---

## 🛠️ Manual Process (if preferred)

### Option 1: Use the Update Script

```bash
# From project root
./scripts/monthly-update.sh

# Review changes
git diff

# Test locally
docker-compose up --build

# Commit and push
git add .
git commit -m "chore: monthly dependency updates"
git push
```

### Option 2: Manual Updates

#### Auth Service (Node.js)
```bash
cd services/auth-service
npm outdated                    # See what's outdated
npm update                      # Update to latest compatible
npm audit                       # Check vulnerabilities
npm audit fix                   # Auto-fix if possible
npm test                        # Run tests (if available)
cd ../..
```

#### Task Service (Python)
```bash
cd services/task-service
pip list --outdated            # See what's outdated
pip install -U Flask flask-cors mysql-connector-python PyJWT python-dotenv Werkzeug Flask-Limiter pydantic
pip freeze | grep -E "(Flask|flask-cors|mysql-connector-python|PyJWT|python-dotenv|Werkzeug|Flask-Limiter|pydantic)" > requirements.txt
python -m pytest               # Run tests (if available)
cd ../..
```

#### Frontend
```bash
cd services/frontend
npm outdated
npm update
npm audit
npm audit fix
npm run test                   # Run tests (if available)
cd ../..
```

---

## ✅ Monthly Checklist

### Week 1: Dependency Updates

- [ ] **Check Dependabot PRs**
  - Review each PR individually
  - Check for breaking changes in changelogs
  - Merge if safe (minor/patch updates)

- [ ] **Run manual updates** (if Dependabot not enabled)
  ```bash
  ./scripts/monthly-update.sh
  ```

- [ ] **Review changes**
  ```bash
  git diff services/*/package*.json
  git diff services/*/requirements.txt
  ```

- [ ] **Test locally**
  ```bash
  docker-compose up --build
  # Test auth: http://localhost:8001/health
  # Test tasks: http://localhost:8002/health
  # Test frontend: http://localhost:3000
  ```

- [ ] **Check for breaking changes**
  - Read package changelogs
  - Test login/logout
  - Test task creation/deletion
  - Check error messages

- [ ] **Commit and push**
  ```bash
  git add .
  git commit -m "chore: monthly dependency updates - $(date +%Y-%m)"
  git push
  ```

- [ ] **Monitor CI/CD pipeline**
  - Check build success
  - Review vulnerability scan results
  - Verify all tests pass

### Week 2: Base Image Updates

- [ ] **Check for new base images**
  - node:22-alpine → Check for 22.x updates
  - python:3.12-slim → Check for 3.12.x updates
  - nginx:1.27-alpine → Check for 1.27.x updates

- [ ] **Update Dockerfiles if needed**
  ```dockerfile
  FROM node:22-alpine3.20 → node:22-alpine3.21
  FROM python:3.12-slim-bookworm → python:3.12-slim-bookworm
  FROM nginx:1.27-alpine3.20 → nginx:1.27-alpine3.21
  ```

- [ ] **Rebuild images**
  ```bash
  docker-compose build --no-cache
  ```

- [ ] **Test services**
  ```bash
  docker-compose up
  ```

- [ ] **Commit and push**
  ```bash
  git add services/*/Dockerfile
  git commit -m "chore: update base images - $(date +%Y-%m)"
  git push
  ```

### Week 3: Security Review

- [ ] **Review .trivyignore**
  - Remove fixed CVEs
  - Add new false positives with justification
  - Document acceptance criteria

- [ ] **Check for critical vulnerabilities**
  ```bash
  # Run local scan if you have Trivy installed
  trivy image your-registry/task-manager-auth:latest --severity CRITICAL,HIGH
  ```

- [ ] **Review security advisories**
  - GitHub Security Advisories
  - npm security advisories
  - Python CVE database

- [ ] **Update VULNERABILITY_POLICY.md**
  - Document new threats
  - Update accepted risks
  - Review quarterly goals

### Week 4: Documentation & Planning

- [ ] **Update security documentation**
  - Document any new security measures
  - Update incident response procedures
  - Review access controls

- [ ] **Review failed login attempts**
  ```bash
  kubectl logs -n tms-app deployment/auth-service | grep "Invalid credentials" | wc -l
  ```

- [ ] **Check rate limit hits**
  ```bash
  kubectl logs -n tms-app deployment/auth-service | grep "Rate limit exceeded" | wc -l
  ```

- [ ] **Plan next month's improvements**
  - Any new security features needed?
  - Any performance issues?
  - Any monitoring gaps?

---

## 📊 Success Metrics

### Track these monthly:

| Metric | Target | Current | Trend |
|--------|--------|---------|-------|
| Critical CVEs (YOUR code) | 0 | ? | ↓ |
| High CVEs (YOUR code) | < 5 | ? | ↓ |
| Total CVEs (all) | < 500 | 832 | ↓ |
| Failed login attempts | < 100/month | ? | → |
| Rate limit hits | < 50/month | ? | → |
| Dependency updates | All up-to-date | ? | ✓ |

### Update spreadsheet:
```
Month | Critical | High | Total | Base Image Version | Notes
------|----------|------|-------|-------------------|-------
Jan 2026 | 3 | 155 | 832 | node:22-alpine3.20 | Initial audit
Feb 2026 | ? | ? | ? | ? | After first update
```

---

## 🚨 Emergency Updates (Outside Monthly Cycle)

If you discover a **CRITICAL** vulnerability being exploited in the wild:

1. **Immediate:** Create hotfix branch
   ```bash
   git checkout -b hotfix/critical-vulnerability
   ```

2. **Update affected package**
   ```bash
   # Example for Node.js
   cd services/auth-service
   npm install package@fixed-version
   ```

3. **Test quickly**
   ```bash
   docker-compose up --build
   # Quick smoke test
   ```

4. **Deploy immediately**
   ```bash
   git commit -m "fix: critical security vulnerability in package-name (CVE-2024-XXXX)"
   git push
   ```

5. **Notify team**
   - Slack/email notification
   - Document in incident log
   - Schedule post-mortem

---

## 💡 Tips & Best Practices

### Do:
- ✅ Read changelogs before updating
- ✅ Test locally before pushing
- ✅ Update one service at a time
- ✅ Keep dependency updates small and frequent
- ✅ Document breaking changes

### Don't:
- ❌ Update all dependencies at once
- ❌ Skip testing after updates
- ❌ Ignore breaking change warnings
- ❌ Update major versions without review
- ❌ Update in production directly

---

## 📞 Questions & Issues

**Common Issues:**

1. **"npm audit fix breaks my app"**
   - Review what changed: `git diff package-lock.json`
   - Revert specific package: `npm install package@old-version`
   - Report issue to package maintainer

2. **"pip upgrade causes conflicts"**
   - Use constraints: `pip install package==version`
   - Check compatibility matrix
   - Consider virtual environment for testing

3. **"Too many Dependabot PRs"**
   - Reduce `open-pull-requests-limit` in `.github/dependabot.yml`
   - Group updates by service
   - Use monthly schedule instead of weekly

---

**Last Updated:** January 21, 2026  
**Next Review:** February 1, 2026  
**Owner:** DevOps Team
