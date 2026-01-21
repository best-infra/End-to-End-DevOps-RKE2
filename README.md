# Task Management System

A production-grade, cloud-native task management application demonstrating modern DevOps practices. This project implements a complete end-to-end pipeline from development to production deployment using containerization, Kubernetes orchestration, GitOps workflows, and comprehensive security hardening.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Technology Stack](#technology-stack)
3. [Project Structure](#project-structure)
4. [Services](#services)
5. [Infrastructure](#infrastructure)
6. [CI/CD Pipeline](#cicd-pipeline)
7. [Security Implementation](#security-implementation)
8. [Monitoring and Observability](#monitoring-and-observability)
9. [Local Development](#local-development)
10. [Kubernetes Deployment](#kubernetes-deployment)
11. [Environment Configuration](#environment-configuration)
12. [API Reference](#api-reference)
13. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

The system follows a microservices architecture pattern with the following components:

```
                                    [Ingress Controller]
                                           |
                    +----------------------+----------------------+
                    |                      |                      |
              [Frontend]            [Auth Service]         [Task Service]
                    |                      |                      |
                    +----------------------+----------------------+
                                           |
                                       [MySQL]
```

**Request Flow:**
1. External traffic enters through the Ingress Controller
2. Nginx routes requests to appropriate backend services based on path
3. Authentication requests are handled by the Auth Service (Node.js)
4. Task operations are processed by the Task Service (Python/Flask)
5. Both services communicate with a shared MySQL database
6. JWT tokens are used for stateless authentication between services

---

## Technology Stack

### Application Layer
| Component | Technology | Version |
|-----------|------------|---------|
| Frontend | React with Vite | 5.x |
| Auth Service | Node.js with Express | 22.x |
| Task Service | Python with Flask | 3.12 |
| Database | MySQL | 8.0 |
| Reverse Proxy | Nginx | 1.27 |

### Infrastructure Layer
| Component | Technology | Purpose |
|-----------|------------|---------|
| Container Runtime | Docker | Application containerization |
| Orchestration | Kubernetes (RKE2) | Container orchestration |
| GitOps | Flux CD | Continuous deployment |
| CI/CD | GitHub Actions | Continuous integration |
| Monitoring | Prometheus + Grafana | Metrics and visualization |
| Security Scanning | Trivy | Vulnerability detection |

### Security Components
| Component | Purpose |
|-----------|---------|
| Helmet | HTTP security headers |
| express-rate-limit | API rate limiting (Node.js) |
| Flask-Limiter | API rate limiting (Python) |
| express-validator | Input validation (Node.js) |
| Pydantic | Input validation (Python) |
| bcrypt | Password hashing |
| JWT | Stateless authentication |

---

## Project Structure

```
.
├── .github/
│   ├── workflows/
│   │   ├── ci-cd-pipeline.yml      # Main CI/CD pipeline
│   │   └── monthly-updates.yml      # Dependency update automation
│   └── dependabot.yml               # Automated dependency updates
├── flux/
│   └── clusters/
│       ├── local/                   # Local environment Flux config
│       ├── staging/                 # Staging environment Flux config
│       └── production/              # Production environment Flux config
├── k8s/
│   ├── base/                        # Base Kubernetes manifests
│   ├── monitoring/                  # Prometheus/Grafana stack
│   └── overlays/
│       ├── local/                   # Local environment overrides
│       ├── staging/                 # Staging environment overrides
│       └── production/              # Production environment overrides
├── services/
│   ├── auth-service/                # Node.js authentication service
│   ├── task-service/                # Python task management service
│   ├── frontend/                    # React frontend application
│   ├── nginx/                       # Nginx reverse proxy
│   └── docker-compose.yml           # Local development composition
└── scripts/
    └── monthly-update.sh            # Manual dependency update script
```

---

## Services

### Auth Service (Node.js/Express)

Handles user authentication and authorization.

**Endpoints:**
| Method | Path | Description | Rate Limit |
|--------|------|-------------|------------|
| POST | /register | User registration | 3/hour |
| POST | /login | User authentication | 5/15min |
| GET | /health | Health check | Unlimited |

**Security Features:**
- Password complexity requirements (12+ characters, mixed case, numbers, symbols)
- Bcrypt password hashing with salt rounds
- JWT token generation with configurable expiry
- Rate limiting to prevent brute force attacks
- Input validation on all endpoints
- Security headers via Helmet middleware

### Task Service (Python/Flask)

Manages task CRUD operations.

**Endpoints:**
| Method | Path | Description | Rate Limit |
|--------|------|-------------|------------|
| GET | /tasks | List user tasks | 100/15min |
| POST | /tasks | Create new task | 20/min |
| PUT | /tasks/{id} | Update task | 100/15min |
| DELETE | /tasks/{id} | Delete task | 100/15min |
| GET | /health | Health check | Unlimited |

**Security Features:**
- JWT token validation on protected routes
- Pydantic models for request validation
- Rate limiting via Flask-Limiter
- SQL injection prevention via parameterized queries

### Frontend (React/Vite)

Single-page application for user interaction.

**Features:**
- Modern React with hooks
- Real-time password strength indicator
- JWT token management
- Responsive design
- Production build optimization via Vite

---

## Infrastructure

### Kubernetes Resources

The application deploys the following Kubernetes resources:

| Resource | Purpose |
|----------|---------|
| Namespace | Logical isolation (tms-app) |
| Deployments | Application workloads |
| Services | Internal networking |
| Ingress | External traffic routing |
| ConfigMaps | Non-sensitive configuration |
| Secrets | Sensitive credentials |
| HorizontalPodAutoscaler | Automatic scaling |
| PodDisruptionBudget | High availability guarantees |
| NetworkPolicy | Pod-to-pod traffic control |
| ServiceAccount/RBAC | Security context and permissions |
| ServiceMonitor | Prometheus metrics collection |

### Horizontal Pod Autoscaling

The HPA configuration maintains application performance under varying load:

| Service | Min Replicas | Max Replicas | CPU Target | Memory Target |
|---------|--------------|--------------|------------|---------------|
| Frontend | 1 | 5 | 70% | 80% |
| Auth Service | 1 | 10 | 70% | 80% |
| Task Service | 1 | 10 | 70% | 80% |

### Resource Allocation

| Service | CPU Request | CPU Limit | Memory Request | Memory Limit |
|---------|-------------|-----------|----------------|--------------|
| Auth Service | 100m | 500m | 128Mi | 512Mi |
| Task Service | 100m | 500m | 128Mi | 512Mi |
| Frontend | 50m | 200m | 64Mi | 256Mi |

---

## CI/CD Pipeline

The GitHub Actions pipeline implements a comprehensive build, test, and deploy workflow.

### Pipeline Stages

**Stage 1: Version Generation**
- Generates semantic version based on run number (MAJOR.MINOR.PATCH)
- Outputs version tag for Docker image tagging

**Stage 2: Change Detection**
- Analyzes which services have changed
- Triggers selective builds only for modified services
- Reduces build time and resource consumption

**Stage 3: Security Scanning**
- Trivy filesystem scan for dependency vulnerabilities
- SARIF report generation for GitHub Security tab integration
- Configurable severity thresholds

**Stage 4: Docker Build and Push**
- Multi-stage Docker builds for optimized image size
- Alpine-based images for minimal attack surface
- Parallel builds for independent services
- Automatic push to Docker Hub registry

**Stage 5: Manifest Update**
- Updates Kubernetes manifests with new image tags
- Commits changes back to repository
- Triggers Flux reconciliation for deployment

**Stage 6: Notifications**
- Slack integration for pipeline status updates
- Success/failure notifications with build details

### Pipeline Triggers

```yaml
on:
  push:
    branches: [master, develop]
    paths:
      - 'services/auth-service/**'
      - 'services/task-service/**'
      - 'services/frontend/**'
      - 'services/nginx/**'
```

---

## Security Implementation

### Authentication and Authorization

**JWT Token Flow:**
1. User authenticates via /login endpoint
2. Server validates credentials against hashed password
3. JWT token generated with user ID and expiration
4. Token returned to client for subsequent requests
5. Protected endpoints validate token on each request

**Password Requirements:**
- Minimum 12 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one numeric digit
- At least one special character

### Rate Limiting Configuration

| Endpoint Category | Window | Max Requests |
|-------------------|--------|--------------|
| Login | 15 minutes | 5 |
| Registration | 1 hour | 3 |
| General API | 15 minutes | 100 |
| Task Creation | 1 minute | 20 |

### Security Headers

The following HTTP security headers are applied via Helmet:

| Header | Value |
|--------|-------|
| Content-Security-Policy | Restrictive CSP directives |
| Strict-Transport-Security | max-age=31536000; includeSubDomains; preload |
| X-Content-Type-Options | nosniff |
| X-Frame-Options | DENY |
| X-XSS-Protection | 1; mode=block |

### Kubernetes Security Context

All pods run with the following security constraints:

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 1000
  allowPrivilegeEscalation: false
  capabilities:
    drop:
      - ALL
  seccompProfile:
    type: RuntimeDefault
```

### Secret Management

Sensitive values are managed via Kubernetes Secrets:

| Secret Name | Contains |
|-------------|----------|
| jwt-secret | JWT signing key |
| db-password | MySQL root password |
| db-username | MySQL username |
| sql-endpoint | MySQL service endpoint |

---

## Monitoring and Observability

### Prometheus Stack

The monitoring infrastructure includes:

- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization dashboards
- **AlertManager**: Alert routing and notifications

### Service Monitors

Custom ServiceMonitor resources collect metrics from:

- Auth Service (/metrics endpoint)
- Task Service (/metrics endpoint)
- Frontend (nginx metrics)

### Health Checks

All services implement health endpoints:

| Service | Endpoint | Interval |
|---------|----------|----------|
| Auth Service | GET /health | 10s |
| Task Service | GET /health | 10s |
| Frontend | GET /health | 10s |

### Kubernetes Probes

| Probe Type | Initial Delay | Period | Timeout | Failure Threshold |
|------------|---------------|--------|---------|-------------------|
| Liveness | 30s | 10s | 5s | 3 |
| Readiness | 10s | 5s | 3s | 3 |

---

## Local Development

### Prerequisites

- Docker and Docker Compose
- Node.js 22.x (for local development)
- Python 3.12 (for local development)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/khaledhawil/End-to-End-DevOps-AWS-Nodejs-Python-MySQL.git
cd End-to-End-DevOps-AWS-Nodejs-Python-MySQL

# Start all services
cd services
docker-compose up -d

# Access the application
# Frontend: http://localhost
# Auth Service: http://localhost:8001
# Task Service: http://localhost:8002
```

### Development Workflow

```bash
# Rebuild specific service after changes
docker-compose up -d --build auth-service

# View logs
docker-compose logs -f auth-service

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

---

## Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (RKE2, EKS, GKE, or similar)
- kubectl configured with cluster access
- Flux CD installed
- Docker Hub account for image registry

### Flux GitOps Setup

```bash
# Bootstrap Flux with your repository
flux bootstrap github \
  --owner=<your-github-username> \
  --repository=End-to-End-DevOps-AWS-Nodejs-Python-MySQL \
  --branch=master \
  --path=./flux/clusters/local \
  --personal

# Verify Flux installation
flux check

# Monitor reconciliation
flux get kustomizations --watch
```

### Manual Deployment

```bash
# Apply base resources
kubectl apply -k k8s/base

# Apply environment-specific overlay
kubectl apply -k k8s/overlays/local

# Verify deployment
kubectl get pods -n tms-app
kubectl get svc -n tms-app
kubectl get ingress -n tms-app
```

### Environment-Specific Configuration

| Environment | Overlay Path | Database | Secrets |
|-------------|--------------|----------|---------|
| Local | k8s/overlays/local | Local MySQL pod | Local secrets.yaml |
| Staging | k8s/overlays/staging | Local MySQL pod | Staging secrets.yaml |
| Production | k8s/overlays/production | AWS RDS | Sealed Secrets |

---

## Environment Configuration

### Required Environment Variables

**Auth Service:**
| Variable | Description | Default |
|----------|-------------|---------|
| PORT | Service port | 8001 |
| DB_HOST | MySQL hostname | - |
| DB_USER | MySQL username | - |
| DB_PASSWORD | MySQL password | - |
| DB_NAME | Database name | task_management |
| JWT_SECRET | Token signing key | - |

**Task Service:**
| Variable | Description | Default |
|----------|-------------|---------|
| PORT | Service port | 8002 |
| DB_HOST | MySQL hostname | - |
| DB_USER | MySQL username | - |
| DB_PASSWORD | MySQL password | - |
| DB_NAME | Database name | task_management |
| JWT_SECRET | Token signing key | - |
| ALLOWED_ORIGINS | CORS allowed origins | localhost |

### GitHub Actions Secrets

| Secret | Purpose |
|--------|---------|
| DOCKER_USERNAME | Docker Hub username |
| DOCKER_TOKEN | Docker Hub access token |
| SLACK_WEBHOOK_URL | Slack notifications (optional) |

---

## API Reference

### Authentication Endpoints

**Register User**
```
POST /register
Content-Type: application/json

{
  "username": "string (3-50 chars, alphanumeric)",
  "password": "string (12+ chars, complexity requirements)"
}

Response: 201 Created
{
  "message": "User registered successfully"
}
```

**Login**
```
POST /login
Content-Type: application/json

{
  "username": "string",
  "password": "string"
}

Response: 200 OK
{
  "token": "jwt-token-string"
}
```

### Task Endpoints

**List Tasks**
```
GET /tasks
Authorization: Bearer <token>

Response: 200 OK
[
  {
    "id": 1,
    "title": "string",
    "description": "string",
    "priority": "low|medium|high",
    "status": "pending|in_progress|completed",
    "created_at": "timestamp"
  }
]
```

**Create Task**
```
POST /tasks
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "string (1-200 chars)",
  "description": "string (1-2000 chars)",
  "priority": "low|medium|high"
}

Response: 201 Created
{
  "message": "Task created successfully",
  "id": 1
}
```

---

## Troubleshooting

### Common Issues

**Pods in CrashLoopBackOff**
```bash
# Check pod logs
kubectl logs -n tms-app <pod-name>

# Check pod events
kubectl describe pod -n tms-app <pod-name>

# Common causes:
# - Missing secrets
# - Database connection failure
# - Invalid JWT_SECRET configuration
```

**Database Connection Errors**
```bash
# Verify MySQL pod is running
kubectl get pods -n tms-app -l app=mysql

# Check MySQL logs
kubectl logs -n tms-app -l app=mysql

# Test connectivity from service pod
kubectl exec -it -n tms-app <auth-pod> -- nc -zv mysql-service 3306
```

**HPA Thrashing (Constant Scaling)**
```bash
# Check HPA status
kubectl get hpa -n tms-app

# Review scaling events
kubectl describe hpa -n tms-app auth-service-hpa

# Solution: Adjust stabilization windows in k8s/base/hpa.yaml
```

**Flux Reconciliation Failures**
```bash
# Check Flux logs
flux logs --level=error

# Force reconciliation
flux reconcile kustomization task-management-system-local

# Suspend and resume
flux suspend kustomization task-management-system-local
flux resume kustomization task-management-system-local
```

### Health Check Commands

```bash
# Full cluster health
kubectl get pods -n tms-app
kubectl get svc -n tms-app
kubectl get ingress -n tms-app
kubectl top pods -n tms-app

# Service-specific health
curl -s http://<ingress-ip>/api/auth/health
curl -s http://<ingress-ip>/api/tasks/health
```

---

## License

This project is licensed under the MIT License.

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes with descriptive messages
4. Push to your fork
5. Open a Pull Request

---

## Author

Khaled Hawil

---

## Acknowledgments

- Kubernetes documentation and community
- Flux CD project maintainers
- GitHub Actions team
- Open source security tools contributors
