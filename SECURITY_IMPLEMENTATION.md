# Security Implementation Guide

## Overview

This document describes the comprehensive security measures implemented across all layers of the Task Management System, from CI/CD pipeline to Kubernetes runtime.

## Security Layers

### 1. CI/CD Pipeline Security

#### Image Building Security
- **Provenance Attestation**: BuildKit provenance enabled for supply chain security
- **SBOM Generation**: Software Bill of Materials (SBOM) generated in SPDX format for every image
- **Multi-Scanner Approach**: 
  - Trivy for vulnerability scanning (CRITICAL, HIGH, MEDIUM)
  - Grype for SBOM-based vulnerability detection
  - Secret scanning in filesystem before image build

#### Security Scanning
```yaml
# Trivy scans: SARIF + JSON formats
- Vulnerabilities (CVE database)
- Misconfigurations
- Secrets in code
- License compliance

# Grype scans: SBOM analysis
- Known vulnerabilities in dependencies
- Transitive dependency risks
```

#### Build-Time Checks
- Security configuration validation
- Best practices verification (non-root user, minimal layers)
- Secrets detection before image creation
- Dependency analysis and tracking

#### Artifacts
- Vulnerability reports (SARIF for GitHub Security, JSON for parsing)
- SBOM files for audit and compliance
- Security scan results for each service

### 2. Container Security

#### Base Image Hardening
```dockerfile
# Alpine Linux base with specific version
FROM node:20-alpine3.19

# Security updates applied
RUN apk update && apk upgrade --no-cache

# Non-root user
USER node
```

#### Security Features
- **Minimal base images**: Alpine Linux (5MB base) and Debian Slim
- **Version pinning**: Specific image tags (not `latest` in production)
- **Security patches**: Automatic OS package updates during build
- **Layer optimization**: Multi-stage builds to minimize attack surface
- **No unnecessary packages**: Production dependencies only

### 3. Kubernetes Pod Security

#### Security Context (Pod Level)
```yaml
securityContext:
  runAsNonRoot: true          # Prevent root execution
  runAsUser: 1000             # Specific UID
  fsGroup: 1000               # File system group
  seccompProfile:
    type: RuntimeDefault      # Secure computing mode
```

#### Security Context (Container Level)
```yaml
securityContext:
  allowPrivilegeEscalation: false  # Prevent privilege escalation
  readOnlyRootFilesystem: true     # Immutable filesystem (where possible)
  runAsNonRoot: true                # Enforce non-root
  runAsUser: 1000                   # Specific UID
  capabilities:
    drop:
      - ALL                          # Drop all Linux capabilities
    add:
      - NET_BIND_SERVICE             # Only for nginx (port 80)
```

### 4. Network Security

#### Network Policies

**Default Deny All**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
spec:
  podSelector: {}  # Applies to all pods
  policyTypes:
  - Ingress
  - Egress
```

**Service-Specific Policies**

Frontend:
- Ingress: Only from ingress-nginx namespace
- Egress: Only to auth-service (8001), task-service (8002), and DNS

Auth Service:
- Ingress: Only from frontend and ingress-nginx
- Egress: Only to MySQL (3306) and DNS

Task Service:
- Ingress: Only from frontend and ingress-nginx
- Egress: Only to MySQL (3306) and DNS

MySQL:
- Ingress: Only from auth-service and task-service
- Egress: Only DNS (no external connections)

### 5. Access Control (RBAC)

#### Service Accounts
Each service runs with dedicated service account:
- `frontend-sa`
- `auth-service-sa`
- `task-service-sa`
- `mysql-sa`

#### Role-Based Access
```yaml
# Secret reader role
rules:
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get", "list"]
  resourceNames: ["tms-app-secrets"]  # Specific secret only
```

**Bindings:**
- auth-service-sa → secret-reader role
- task-service-sa → secret-reader role
- frontend-sa → no secret access (runs nginx only)

### 6. Resource Management

#### Resource Limits
```yaml
resources:
  requests:
    memory: "128Mi"    # Guaranteed allocation
    cpu: "100m"
  limits:
    memory: "512Mi"    # Maximum allowed
    cpu: "500m"
```

**Purpose:**
- Prevent resource exhaustion attacks
- Ensure fair resource distribution
- Enable horizontal pod autoscaling
- Protect cluster stability

#### Health Checks
```yaml
livenessProbe:         # Restart unhealthy pods
  httpGet:
    path: /health
    port: 8001
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:        # Remove from load balancer when not ready
  httpGet:
    path: /health
    port: 8001
  initialDelaySeconds: 10
  periodSeconds: 5
```

### 7. High Availability Security

#### Pod Disruption Budgets
```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
spec:
  minAvailable: 1      # Always maintain 1 pod during disruptions
  selector:
    matchLabels:
      app: frontend
```

**Protection Against:**
- Node drains
- Cluster upgrades
- Manual deletions
- Evictions

### 8. Secret Management

#### Current Implementation
```yaml
# Kubernetes Secrets
- Environment variable injection
- Base64 encoding
- Namespace isolation
- RBAC-controlled access
```

#### Recommended Production Enhancements
- External Secrets Operator + HashiCorp Vault
- Sealed Secrets for Git-stored encrypted secrets
- AWS Secrets Manager / Azure Key Vault integration
- Secret rotation policies
- Audit logging of secret access

### 9. Database Security

#### MySQL Configuration
```yaml
# Authentication
- mysql_native_password plugin
- Strong password requirements
- User-specific credentials

# Network
- ClusterIP service (internal only)
- Network policy restrictions
- No external access
```

#### Recommended Enhancements
```sql
-- SSL/TLS connections
REQUIRE SSL

-- Limited privileges
GRANT SELECT, INSERT, UPDATE, DELETE ON task_management.* TO 'appuser'@'%';

-- Connection encryption
--ssl-ca=/path/to/ca.pem
--ssl-cert=/path/to/client-cert.pem
--ssl-key=/path/to/client-key.pem
```

### 10. Application Security

#### Node.js (Auth Service)
```javascript
// Security headers
helmet()

// Rate limiting
rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100
})

// Input validation
validator.isEmail(email)

// Password hashing
bcrypt.hash(password, 10)

// JWT security
jsonwebtoken.sign({}, secret, { expiresIn: '24h' })
```

#### Python (Task Service)
```python
# Input validation
from flask import request
from werkzeug.security import check_password_hash

# SQL injection prevention
cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))

# CORS configuration
CORS(app, origins=['https://yourdomain.com'])

# Security headers
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    return response
```

### 11. Ingress Security

#### TLS/SSL Configuration (Production)
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - yourdomain.com
    secretName: tms-tls-cert
```

#### Rate Limiting
```yaml
annotations:
  nginx.ingress.kubernetes.io/limit-rps: "10"
  nginx.ingress.kubernetes.io/limit-connections: "5"
```

#### Additional Headers
```yaml
nginx.ingress.kubernetes.io/configuration-snippet: |
  more_set_headers "X-Frame-Options: DENY";
  more_set_headers "X-Content-Type-Options: nosniff";
  more_set_headers "X-XSS-Protection: 1; mode=block";
```

## Security Checklist

### CI/CD
- [ ] Vulnerability scanning enabled (Trivy + Grype)
- [ ] SBOM generation configured
- [ ] Secret scanning active
- [ ] Build provenance enabled
- [ ] SARIF upload to GitHub Security
- [ ] Notifications configured (Slack/Email)
- [ ] Critical vulnerability blocking enabled

### Container Images
- [ ] Non-root user configured
- [ ] Specific version tags (no `latest`)
- [ ] Security updates applied
- [ ] Minimal base images
- [ ] Multi-stage builds
- [ ] No secrets in images
- [ ] Health check endpoints implemented

### Kubernetes
- [ ] Network policies deployed
- [ ] RBAC configured
- [ ] Service accounts assigned
- [ ] Security contexts defined
- [ ] Resource limits set
- [ ] Health probes configured
- [ ] PodDisruptionBudgets created
- [ ] Read-only filesystems (where possible)
- [ ] Capability dropping enabled

### Database
- [ ] Strong passwords
- [ ] Network policy restrictions
- [ ] User privilege limitation
- [ ] SSL/TLS connections (production)
- [ ] Backup encryption
- [ ] Audit logging enabled

### Application
- [ ] Input validation
- [ ] Output encoding
- [ ] SQL injection prevention
- [ ] XSS protection
- [ ] CSRF protection
- [ ] Rate limiting
- [ ] Security headers
- [ ] Dependency scanning
- [ ] Regular updates

### Monitoring
- [ ] Security audit logs
- [ ] Failed authentication alerts
- [ ] Anomaly detection
- [ ] Resource usage monitoring
- [ ] Network traffic analysis
- [ ] Vulnerability report review

## Security Testing

### Automated Tests
```bash
# Kubernetes security audit
kubectl auth can-i --list

# Network policy testing
kubectl exec -it test-pod -- nc -zv service 8001

# RBAC testing
kubectl auth can-i get secrets --as=system:serviceaccount:tms-app:frontend-sa

# Container scanning
trivy image khaledhawil/task-manager-auth:latest

# SBOM generation
syft khaledhawil/task-manager-auth:latest -o spdx-json
```

### Manual Testing
- Penetration testing
- Security code review
- Dependency audit
- Configuration review
- Incident response drills

## Compliance

### Standards Addressed
- CIS Kubernetes Benchmark
- OWASP Top 10
- PCI DSS (for payment processing, if applicable)
- GDPR (data protection)
- SOC 2 (security controls)

### Audit Trail
- All deployments via GitOps (Git commit history)
- RBAC audit logs
- Network policy enforcement logs
- Security scan results archived
- Incident response documentation

## Incident Response

### Security Incident Procedure
1. **Detection**: Monitoring alerts, scan results, user reports
2. **Containment**: Network isolation, pod termination, service suspension
3. **Investigation**: Log analysis, root cause identification
4. **Remediation**: Patch deployment, configuration changes
5. **Recovery**: Service restoration, verification testing
6. **Post-Incident**: Documentation, lessons learned, preventive measures

### Emergency Contacts
- Security team: security@company.com
- On-call engineer: pagerduty.com/oncall
- Incident commander: Define rotation

## Continuous Improvement

### Regular Activities
- Weekly: Review vulnerability scan results
- Monthly: Security patch updates
- Quarterly: Security audit, penetration testing
- Annually: Compliance certification, disaster recovery drill

### Metrics
- Mean time to detect (MTTD)
- Mean time to respond (MTTR)
- Vulnerability remediation time
- Security scan coverage
- Failed authentication attempts

## References

- [Kubernetes Security Best Practices](https://kubernetes.io/docs/concepts/security/)
- [OWASP Kubernetes Top 10](https://owasp.org/www-project-kubernetes-top-ten/)
- [CIS Benchmarks](https://www.cisecurity.org/benchmark/kubernetes)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
