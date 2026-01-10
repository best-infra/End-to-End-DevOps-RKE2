# End-to-End DevOps Task Management System

## Project Overview

This project implements a complete DevOps pipeline for a cloud-native task management application. The system demonstrates modern DevOps practices including containerization, continuous integration and delivery, GitOps deployment, infrastructure as code, and automated security scanning.

The application consists of three microservices: an authentication service (Node.js), a task management service (Python), and a frontend web application (React). These services are containerized, automatically built and scanned for vulnerabilities, and deployed to Kubernetes clusters using GitOps principles with Flux CD.

### Key Capabilities

- Automated CI/CD pipeline with intelligent service change detection
- Container image security scanning with automated notifications
- GitOps-based deployment with automatic synchronization
- Multi-environment support (local, staging, production)
- Service mesh-ready architecture with proper ingress configuration
- Automated Kubernetes manifest updates on image changes

## High-Level Architecture

The system follows a microservices architecture deployed on Kubernetes. The application layer consists of three distinct services that communicate via REST APIs. User requests enter through an Nginx ingress controller which routes traffic based on URL paths to the appropriate backend service.

The authentication service handles user registration and login, issuing JWT tokens for session management. The task service manages CRUD operations for tasks and enforces user-based access control. The frontend provides a single-page application interface built with React. All services connect to a shared MySQL database for persistent storage.

The deployment pipeline uses GitHub Actions for continuous integration, building Docker images on code changes and scanning them for security vulnerabilities. Trivy performs automated security scans and sends notifications when critical or high-severity vulnerabilities are detected. Docker images are pushed to Docker Hub registry and Kubernetes manifests are automatically updated with new image tags.

Flux CD monitors the Git repository for manifest changes and automatically synchronizes the desired state to the Kubernetes cluster. This GitOps approach ensures that the cluster state always matches what is defined in Git, providing audit trails and easy rollback capabilities.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           GitHub Repository                             │
│  ┌──────────────┐  ┌──────────────┐                                    │
│  │  Services    │  │  K8s Manifests│                                    │
│  │  Code        │  │  (Kustomize)  │                                    │
│  └──────────────┘  └──────────────┘                                    │
└─────────────────────────────────────────────────────────────────────────┘
         │                      │
         │ Push                 │ Monitor
         ▼                      ▼
┌─────────────────┐    ┌─────────────────┐
│ GitHub Actions  │    │    Flux CD      │
│   CI/CD         │    │   (GitOps)      │
│                 │    │                 │
│ ├─ Change Det.  │    │ ├─ Git Sync     │
│ ├─ Build Images │    │ ├─ Kustomize    │
│ ├─ Trivy Scan   │    │ └─ Apply K8s    │
│ ├─ Push to Hub  │    │                 │
│ └─ Update K8s   │    │                 │
└─────────────────┘    └─────────────────┘
         │                      │
         │ Images               │ Manifests
         ▼                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      Kubernetes Cluster (RKE2)                          │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────┐      │
│  │                    Nginx Ingress Controller                  │      │
│  │            (Routes: /, /api/auth/*, /api/tasks/*)           │      │
│  └─────────────────────────────────────────────────────────────┘      │
│         │                      │                        │               │
│         │ /                    │ /api/auth/*            │ /api/tasks/*  │
│         ▼                      ▼                        ▼               │
│  ┌────────────┐       ┌────────────────┐      ┌────────────────┐     │
│  │  Frontend  │       │  Auth Service  │      │  Task Service  │     │
│  │  (React)   │       │  (Node.js)     │      │  (Python)      │     │
│  │  Port: 80  │       │  Port: 8001    │      │  Port: 8002    │     │
│  │  Nginx     │       │  Express.js    │      │  Flask         │     │
│  └────────────┘       └────────────────┘      └────────────────┘     │
│         │                      │                        │               │
│         └──────────────────────┼────────────────────────┘              │
│                                ▼                                        │
│                      ┌──────────────────┐                              │
│                      │   MySQL 8.0      │                              │
│                      │   Port: 3306     │                              │
│                      │   Persistent Vol │                              │
│                      └──────────────────┘                              │
│                                                                         │
│  Namespace: tms-app                                                    │
└─────────────────────────────────────────────────────────────────────────┘

External Services:
- Docker Hub: Container image registry
- Slack: Vulnerability notifications (optional)
- SMTP: Email notifications (optional)
```

## Tools and Technologies

### Container and Orchestration
- **Docker**: Container runtime for building and packaging microservices
- **Kubernetes (RKE2 1.34.3)**: Container orchestration platform for service deployment and management
- **Kustomize**: Kubernetes native configuration management for multi-environment deployments

### CI/CD and GitOps
- **GitHub Actions**: Continuous integration and delivery automation
- **Flux CD v2**: GitOps continuous delivery operator for Kubernetes
- **Trivy**: Vulnerability scanner for container images and dependencies

### Application Stack
- **Node.js 20 Alpine**: Runtime for authentication service
- **Python 3.11 Slim**: Runtime for task management service
- **React 18 + Vite**: Frontend framework and build tool
- **Nginx 1.25 Alpine**: Web server and reverse proxy
- **Express.js**: Node.js web application framework
- **Flask**: Python web application framework

### Data and Storage
- **MySQL 8.0**: Relational database for persistent storage
- **Kubernetes Persistent Volumes**: Storage abstraction for database data

### Networking and Security
- **Nginx Ingress Controller**: HTTP(S) load balancer and ingress management
- **JWT (JSON Web Tokens)**: Stateless authentication mechanism
- **bcrypt**: Password hashing library
- **Docker Hub**: Container image registry

### Configuration Management
- **RKE2**: Lightweight Kubernetes distribution for production workloads
- **Kustomize**: Declarative Kubernetes configuration management

## Why These Tools Were Chosen

### Kubernetes and RKE2
Kubernetes provides container orchestration, automatic scaling, self-healing, and declarative configuration management. RKE2 was chosen as it is a lightweight, security-focused Kubernetes distribution that meets enterprise security requirements while running efficiently on both development and production environments.

### GitOps with Flux CD
Flux CD enables declarative, Git-centric deployment workflows. Every change to the cluster state is tracked in Git, providing complete audit trails and enabling rollback to any previous state. Flux automatically reconciles cluster state with Git every minute, eliminating configuration drift and manual kubectl commands.

### GitHub Actions with Change Detection
GitHub Actions provides native integration with the source repository and executes workflows in response to code changes. The pipeline implements intelligent change detection using path filters, building and scanning only the services that have changed. This reduces build times and resource consumption while maintaining fast feedback loops.

### Trivy Security Scanner
Trivy scans container images, filesystems, and Git repositories for vulnerabilities, misconfigurations, and secrets. It supports multiple output formats including SARIF for GitHub Security integration and JSON for automated parsing. The scanner runs as part of the CI pipeline, blocking deployments of images with critical vulnerabilities.

### Kustomize for Configuration Management
Kustomize provides Kubernetes-native configuration management without requiring templates or additional tooling. It uses a base configuration with environment-specific overlays, allowing configuration reuse while maintaining clear separation between environments. This approach reduces duplication and makes environment differences explicit.

### Microservices Architecture
The application is decomposed into separate authentication, task management, and frontend services. This separation allows independent scaling, deployment, and technology choices for each service. Teams can work on different services concurrently without coordination overhead. Service failures are isolated and do not cascade to the entire application.

### RKE2 Kubernetes Distribution
RKE2 is a security-focused Kubernetes distribution that meets US Federal Government security compliance requirements. It includes hardened configurations by default, uses containerd as the runtime, and provides automatic certificate rotation. RKE2 is production-ready while remaining lightweight enough for edge and development environments.

### MySQL for Persistence
MySQL provides ACID transactions, referential integrity through foreign keys, and mature replication capabilities. The relational model naturally represents the user-task relationship in the application domain. MySQL's wide adoption ensures extensive tooling, documentation, and operational expertise availability.

### Alpine Linux Base Images
Alpine Linux images are significantly smaller than Debian or Ubuntu-based images, reducing attack surface, storage requirements, and image pull times. Alpine uses musl libc and busybox, resulting in base images under 5MB. Security updates can be applied quickly due to the minimal package count.

### JWT for Authentication
JWT enables stateless authentication, eliminating server-side session storage and allowing horizontal scaling without session affinity. Tokens contain claims that services can verify cryptographically without database lookups. The standard is widely supported across languages and frameworks.

## Repository Structure

```
.
├── .github/
│   └── workflows/
│       └── ci-cd-pipeline.yml              # Main CI/CD workflow with change detection
│
├── flux/
│   ├── README.md                           # Flux configuration documentation
│   └── clusters/
│       ├── local/                          # Local environment Flux config
│       │   ├── git-repository.yaml         # Git source definition
│       │   └── kustomization-app.yaml      # Kustomization application
│       ├── staging/                        # Staging environment Flux config
│       └── production/                     # Production environment Flux config
│
├── k8s/
│   ├── base/                               # Base Kubernetes manifests
│   │   ├── namespace.yaml                  # Namespace definition (tms-app)
│   │   ├── mysql-configmap.yaml            # MySQL configuration
│   │   ├── users-deployment.yaml           # Auth service deployment
│   │   ├── users-service.yaml              # Auth service ClusterIP
│   │   ├── logout-deployment.yaml          # Task service deployment
│   │   ├── logout-service.yaml             # Task service ClusterIP
│   │   ├── frontend-deployment.yaml        # Frontend deployment
│   │   ├── frontend-service.yaml           # Frontend ClusterIP
│   │   └── kustomization.yaml              # Base kustomization
│   └── overlays/
│       ├── local/                          # Local environment overlay
│       │   ├── kustomization.yaml          # Local kustomization
│       │   ├── ingress.yaml                # Ingress routes (split)
│       │   ├── mysql-deployment.yaml       # MySQL StatefulSet
│       │   ├── mysql-service.yaml          # MySQL ClusterIP
│       │   ├── mysql-pvc.yaml              # Persistent volume claim
│       │   └── secrets.yaml                # Local secrets (not in production)
│       ├── staging/                        # Staging environment overlay
│       └── production/                     # Production environment overlay
│           ├── kustomization.yaml
│           ├── ingress.yaml│
├── services/
│   ├── docker-compose.yml                  # Local development compose file
│   ├── init-db.sql                         # Database initialization script
│   ├── README.md                           # Services documentation
│   ├── auth-service/
│   │   ├── Dockerfile                      # Auth service container
│   │   ├── package.json                    # Node.js dependencies
│   │   └── server.js                       # Express.js application
│   ├── task-service/
│   │   ├── Dockerfile                      # Task service container
│   │   ├── requirements.txt                # Python dependencies
│   │   └── app.py                          # Flask application
│   └── frontend/
│       ├── Dockerfile                      # Frontend container (multi-stage)
│       ├── package.json                    # React dependencies
│       ├── vite.config.js                  # Vite configuration
│       ├── nginx.conf                      # Nginx configuration
│       └── src/
│           ├── main.jsx                    # React entry point
│           ├── App.jsx                     # Main App component
│           └── pages/
│               ├── Login.jsx               # Login page component
│               ├── Register.jsx            # Registration page component
│               └── Dashboard.jsx           # Task dashboard component
│
├── nginx-project.conf                      # Nginx configuration example
├── RKE_cluster.yaml                        # RKE2 cluster configuration
└── README.md                               # This file
```

## Deployment Architecture Flow

### Development to Production Flow

1. **Code Development**: Developers work on service code in the `services/` directory and commit changes to feature branches.

2. **Pull Request**: When ready, developers create pull requests to merge into the master branch. The CI pipeline runs automatically on pull requests to validate changes.

3. **Change Detection**: GitHub Actions uses path filters to detect which services have changed. Only modified services proceed through the build pipeline.

4. **Container Build**: Each changed service is built into a Docker image using multi-stage builds to minimize image size. The build process:
   - Pulls the appropriate base image (Node.js, Python, Nginx)
   - Installs dependencies
   - Copies application code
   - Applies security patches to the base operating system

5. **Security Scanning**: Trivy scans each built image in two formats:
   - SARIF format uploaded to GitHub Security for issue tracking
   - JSON format parsed to generate vulnerability reports
   - Scans check for CRITICAL, HIGH, and MEDIUM severity vulnerabilities

6. **Vulnerability Notification**: If CRITICAL or HIGH vulnerabilities are detected:
   - A detailed Markdown report is generated listing all CVEs
   - Slack notification sent with summary counts
   - Email notification sent with full vulnerability details
   - Report uploaded as workflow artifact for later review

7. **Image Registry Push**: Successfully scanned images are tagged with both the Git commit SHA and `latest` tag, then pushed to Docker Hub registry.

8. **Manifest Update**: The CI pipeline updates Kubernetes deployment manifests with new image tags using sed commands. Updated manifests are committed back to the Git repository with `[skip ci]` to prevent recursion.

9. **GitOps Sync**: Flux CD polls the Git repository every minute. When it detects manifest changes:
   - Pulls the updated Kustomize configurations
   - Applies the appropriate overlay for the environment
   - Updates Kubernetes resources in the cluster
   - Performs health checks on updated deployments

10. **Rolling Update**: Kubernetes performs rolling updates of deployments:
    - New pods are created with the updated image
    - Health checks verify pod readiness
    - Old pods are terminated only after new pods are healthy
    - Zero-downtime deployment is achieved

11. **Service Exposure**: Nginx Ingress Controller routes external traffic:
    - Frontend requests (`/`) go to the frontend service
    - Auth API requests (`/api/auth/*`) go to the auth service
    - Task API requests (`/api/tasks/*`) go to the task service

### Environment Separation

Environments are separated using Kustomize overlays. Each environment has its own directory under `k8s/overlays/` containing environment-specific configurations. The base directory contains common resources shared across all environments. This approach ensures consistency while allowing environment-specific customization of replicas, resources, ingress rules, and secrets.

### Continuous Monitoring

Flux CD continuously monitors both the Git repository and the cluster state. If manual changes are made to the cluster, Flux automatically reverts them to match the Git state within one minute. This prevents configuration drift and ensures the cluster always matches the declared desired state in Git.

## Prerequisites:

### Required Tools

- **Kubernetes Cluster**: RKE2 1.28+ or any Kubernetes distribution 1.28+
- **kubectl**: Kubernetes command-line tool version 1.28+
- **Git**: Version control system version 2.30+
- **Docker**: Container runtime version 20.10+ (for local testing)
- **Flux CLI**: Flux command-line tool version 2.0+ (optional but recommended)

### Optional Tools

- **GitHub CLI**: For managing GitHub resources from command line
- **k9s**: Terminal-based Kubernetes UI for easier cluster management
- **kubectx/kubens**: Context and namespace switcher for kubectl

### Required Accounts

- **GitHub Account**: For repository access and GitHub Actions
- **Docker Hub Account**: For container image storage (or configure private registry)

### Required Permissions

- Kubernetes cluster admin permissions for installing Flux and creating namespaces
- GitHub repository write permissions for updating Kubernetes manifests
- Docker Hub push permissions for uploading container images

### System Requirements

- **CPU**: Minimum 4 cores recommended for running local Kubernetes cluster
- **Memory**: Minimum 8GB RAM, 16GB recommended
- **Storage**: Minimum 50GB available disk space for container images and persistent volumes
- **Network**: Internet connectivity for pulling base images and pushing to registries

## Step-by-Step Deployment Guide

### Step 1: Clone the Repository

**What this step does**: Downloads the project source code to your local machine, including all service code, Kubernetes manifests, CI/CD configurations, and documentation.

**Why this step is required**: You need local access to the repository to configure secrets, modify configurations for your environment, and access the Kubernetes manifests for deployment.

**Commands**:
```bash
git clone https://github.com/khaledhawil/End-to-End-DevOps-AWS-Php-MySQL.git
cd End-to-End-DevOps-AWS-Php-MySQL
```

**Expected output**: Git will display clone progress and create a directory containing the repository contents.

### Step 2: Configure GitHub Secrets

**What this step does**: Sets up encrypted secrets in GitHub that the CI/CD pipeline uses for authentication to Docker Hub, Slack, and email services.

**Why this step is required**: The GitHub Actions workflow needs credentials to push images to Docker Hub and send vulnerability notifications. Without these secrets, the pipeline cannot publish container images or notify you of security issues.

**What would break if skipped**: The build pipeline will succeed locally but fail when pushing images to the registry. You will not receive vulnerability notifications via Slack or email.

**Commands**:
Navigate to your GitHub repository settings and add the following secrets:

Required secrets:
```
DOCKER_USERNAME: Your Docker Hub username
DOCKER_PASSWORD: Your Docker Hub password or access token
```

Optional secrets for vulnerability notifications:
```
SLACK_WEBHOOK_URL: Slack incoming webhook URL
MAIL_SERVER: SMTP server address (e.g., smtp.gmail.com)
MAIL_PORT: SMTP port (default: 587)
MAIL_USERNAME: Email username for SMTP authentication
MAIL_PASSWORD: Email password or app password
MAIL_TO: Comma-separated recipient email addresses
```

**Commands**:
Navigate to your GitHub repository settings and add the following secrets:

Required secrets:
```
DOCKER_USERNAME: Your Docker Hub username
DOCKER_PASSWORD: Your Docker Hub password or access token
```

Optional secrets for vulnerability notifications:
```
SLACK_WEBHOOK_URL: Slack incoming webhook URL
MAIL_SERVER: SMTP server address (e.g., smtp.gmail.com)
MAIL_PORT: SMTP port (default: 587)
MAIL_USERNAME: Email username for SMTP authentication
MAIL_PASSWORD: Email password or app password
MAIL_TO: Comma-separated recipient email addresses
```

### Step 3: Verify Kubernetes Cluster Access

**What this step does**: Confirms that kubectl is properly configured to communicate with your Kubernetes cluster and that you have administrative permissions.

**Why this step is required**: All subsequent deployment steps require a functioning connection to the Kubernetes cluster. Without cluster access, you cannot deploy any resources.

**What would break if skipped**: Every kubectl command will fail with connection errors or authentication failures.

**Commands**:
```bash
kubectl cluster-info
kubectl get nodes
kubectl version --short
```

**Expected output**:
```
Kubernetes control plane is running at https://your-cluster-api:6443
CoreDNS is running at https://your-cluster-api:6443/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy

NAME           STATUS   ROLES                       AGE   VERSION
node-1         Ready    control-plane,etcd,master   30d   v1.34.3+rke2r1
node-2         Ready    worker                      30d   v1.34.3+rke2r1

Client Version: v1.28.4
Server Version: v1.34.3+rke2r1
```

### Step 4: Install Flux CD

**What this step does**: Installs the Flux CD operator components into your Kubernetes cluster. Flux consists of several controllers that manage GitOps synchronization, Kustomize builds, and source repository monitoring.

**Why this step is required**: Flux is the GitOps engine that continuously monitors the Git repository and synchronizes Kubernetes resources. Without Flux, you would need to manually run kubectl apply every time you make changes.

**What would break if skipped**: Kubernetes manifests would need manual deployment. Automatic synchronization from Git to cluster would not occur. You would lose audit trails, rollback capabilities, and drift detection.

**Commands**:
```bash
# Install Flux CLI (if not already installed)
curl -s https://fluxcd.io/install.sh | sudo bash

# Verify Flux CLI installation
flux --version

# Bootstrap Flux in your cluster
flux install

# Verify Flux components are running
kubectl get pods -n flux-system
```

**Expected output**:
```
flux version 2.2.2

✚ generating manifests
✔ manifests build completed
► installing components in flux-system namespace
✔ install completed
◎ verifying installation

NAME                                        READY   STATUS    RESTARTS   AGE
helm-controller-5f7f8b9b9d-abc12           1/1     Running   0          30s
kustomize-controller-6f8c7d9b8d-def34      1/1     Running   0          30s
notification-controller-5b9d8c7b6d-ghi56   1/1     Running   0          30s
source-controller-7c8d9b6c5d-jkl78         1/1     Running   0          30s
```

### Step 5: Configure Flux Git Repository Source

**What this step does**: Creates a Flux GitRepository resource that defines where Flux should monitor for Kubernetes manifest changes. This resource tells Flux the repository URL, branch, and synchronization interval.

**Why this step is required**: Flux needs to know which Git repository contains the Kubernetes manifests and how frequently to check for changes. Without this configuration, Flux has no source to monitor.

**What would break if skipped**: Flux would not know where to find Kubernetes manifests. No automatic synchronization would occur. Manual kubectl apply would be required for all deployments.

**Commands**:
```bash
# Apply the Git repository source for your environment (local/staging/production)
kubectl apply -f flux/clusters/local/git-repository.yaml

# Verify the GitRepository resource is created and syncing
flux get sources git

# Check for any reconciliation errors
kubectl describe gitrepository tms-app-repo -n flux-system
```

**Expected output**:
```
NAME            REVISION        SUSPENDED       READY   MESSAGE
tms-app-repo    master@sha1:abc latest revision    True    stored artifact for revision 'master@sha1:abc123'
```

**Important**: Ensure the branch name in `git-repository.yaml` matches your repository's default branch (master, main, etc.).

### Step 6: Apply Flux Kustomization

**What this step does**: Creates a Flux Kustomization resource that defines which directory in the Git repository contains Kubernetes manifests and how to build them. This resource configures the overlay path, target namespace, and health checks.

**Why this step is required**: The GitRepository resource only monitors for changes. The Kustomization resource actually applies those changes to the cluster using Kustomize. It defines which manifests to apply and how to validate successful deployment.

**What would break if skipped**: Flux would detect changes in Git but never apply them to the cluster. Your applications would not be deployed or updated automatically.

**Commands**:
```bash
# Apply the Kustomization resource
kubectl apply -f flux/clusters/local/kustomization-app.yaml

# Verify the Kustomization is reconciling
flux get kustomizations

# Check deployment status
kubectl get kustomization tms-app -n flux-system

# Monitor Flux reconciliation logs
flux logs --follow
```

**Expected output**:
```
NAME            REVISION        SUSPENDED       READY   MESSAGE
tms-app         master@sha1:abc False           True    Applied revision: master@sha1:abc123

Kustomization/flux-system.tms-app - stored artifact for revision 'master@sha1:abc123'
Kustomization/flux-system.tms-app - Health check passed
```

### Step 7: Create Application Namespace

**What this step does**: Creates a dedicated Kubernetes namespace called `tms-app` for all application resources. Namespaces provide logical isolation between different applications or environments within the same cluster.

**Why this step is required**: Kubernetes uses namespaces for resource organization, access control, and quota management. Deploying resources without a namespace would place them in the default namespace, mixing them with other workloads.

**What would break if skipped**: Resource deployment would fail because the manifests reference the `tms-app` namespace which does not exist. Alternatively, resources might deploy to the default namespace, causing organizational and security issues.

**Note**: If you applied the Flux Kustomization in Step 6, Flux will automatically create this namespace based on `k8s/base/namespace.yaml`. You can verify it exists:

**Commands**:
```bash
# Check if namespace was created by Flux
kubectl get namespace tms-app

# If not created, manually create it
kubectl apply -f k8s/base/namespace.yaml

# Verify namespace is active
kubectl get namespace tms-app -o yaml
```

**Expected output**:
```
NAME      STATUS   AGE
tms-app   Active   30s
```

### Step 8: Configure Secrets

**What this step does**: Creates a Kubernetes Secret containing sensitive configuration data including MySQL credentials and JWT signing keys. Secrets are base64-encoded and stored in etcd.

**Why this step is required**: Application services need database credentials to connect to MySQL and secret keys to sign JWT tokens. Hardcoding these values in container images or manifests is a security risk. Kubernetes Secrets provide a mechanism to inject sensitive data at runtime.

**What would break if skipped**: All services would fail to start. The auth service cannot sign tokens without JWT_SECRET. Both auth and task services cannot connect to the database without DB_PASS. Health checks would fail and pods would restart continuously.

**Commands**:
```bash
# For local/staging environments, the secrets are included in the overlay
# Verify the secrets file exists
cat k8s/overlays/local/secrets.yaml

# Secrets are automatically applied by Flux when the Kustomization is reconciled
# Verify secrets were created
kubectl get secrets -n tms-app

# View secret structure (values are base64-encoded)
kubectl describe secret tms-app-secrets -n tms-app
```

**Important**: For production environments, do not commit secrets to Git. Use external secret management:
- Sealed Secrets for encrypted secrets in Git
- External Secrets Operator to sync from AWS Secrets Manager
- Manual secret creation outside of GitOps

**Production secret creation example**:
```bash
kubectl create secret generic tms-app-secrets \
  --from-literal=DB_PASSWORD='your-secure-password' \
  --from-literal=JWT_SECRET='your-jwt-secret-key' \
  -n tms-app
```

### Step 9: Deploy MySQL Database

**What this step does**: Deploys a MySQL 8.0 database as a StatefulSet with persistent storage. The deployment includes a ConfigMap for MySQL configuration, a PersistentVolumeClaim for data storage, and a ClusterIP Service for internal networking.

**Why this step is required**: The application requires a MySQL database to store user accounts and tasks. The database must be deployed before application services because services will fail health checks if they cannot establish database connections.

**What would break if skipped**: Auth and task services would fail to start with database connection errors. Users could not register or log in. No data persistence would be available.

**Note**: If you applied Flux Kustomization in Step 6, MySQL is automatically deployed from `k8s/overlays/local/mysql-*.yaml`. Verify deployment:

**Commands**:
```bash
# Check if MySQL was deployed by Flux
kubectl get statefulset -n tms-app
kubectl get pvc -n tms-app
kubectl get service mysql -n tms-app

# Monitor MySQL pod startup
kubectl get pods -n tms-app -l app=mysql -w

# Check MySQL logs
kubectl logs -n tms-app -l app=mysql --tail=50

# Verify MySQL is ready
kubectl exec -it -n tms-app mysql-0 -- mysql -u root -p -e "SELECT VERSION();"
```

**Expected output**:
```
NAME    READY   AGE
mysql   1/1     2m

NAME                 STATUS   VOLUME                                     CAPACITY
mysql-data-mysql-0   Bound    pvc-abc123-def4-5678-90ab-cdef12345678   10Gi

NAME    TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
mysql   ClusterIP   10.43.123.456   <none>        3306/TCP   2m

mysql-0   1/1     Running   0          2m

VERSION()
8.0.35
```

### Step 10: Initialize Database Schema

**What this step does**: Executes SQL commands to create the database schema including users and tasks tables with appropriate columns, indexes, and foreign key constraints.

**Why this step is required**: The application code expects specific database tables to exist. Without the schema, INSERT and SELECT queries will fail with "table does not exist" errors.

**What would break if skipped**: User registration would fail when trying to insert into the users table. Task creation would fail when trying to insert into the tasks table. Application would return 500 Internal Server Error.

**Commands**:
```bash
# Copy the initialization script to the MySQL pod
kubectl cp services/init-db.sql tms-app/mysql-0:/tmp/init-db.sql

# Execute the SQL script
kubectl exec -it -n tms-app mysql-0 -- mysql -u root -prootpassword < /tmp/init-db.sql

# Or connect interactively and run commands manually
kubectl exec -it -n tms-app mysql-0 -- mysql -u root -prootpassword

# Verify tables were created
kubectl exec -it -n tms-app mysql-0 -- mysql -u root -prootpassword -e "USE task_management; SHOW TABLES;"

# Verify table structure
kubectl exec -it -n tms-app mysql-0 -- mysql -u root -prootpassword -e "USE task_management; DESCRIBE users; DESCRIBE tasks;"
```

**Expected output**:
```
Tables_in_task_management
users
tasks

Field           Type            Null    Key     Default
id              int             NO      PRI     NULL
username        varchar(50)     NO      UNI     NULL
password        varchar(255)    NO              NULL
email           varchar(100)    YES     UNI     NULL
created_at      timestamp       YES             CURRENT_TIMESTAMP

Field           Type            Null    Key     Default
id              int             NO      PRI     NULL
user_id         int             NO      MUL     NULL
title           varchar(255)    NO              NULL
description     text            YES             NULL
status          enum            YES             pending
priority        enum            YES             medium
due_date        date            YES             NULL
created_at      timestamp       YES             CURRENT_TIMESTAMP
updated_at      timestamp       YES             CURRENT_TIMESTAMP
```

### Step 11: Deploy Application Services

**What this step does**: Deploys the three microservices (auth, task, frontend) as Kubernetes Deployments with their corresponding ClusterIP Services. Each deployment pulls container images from Docker Hub and creates pods running the service code.

**Why this step is required**: The application services are the core of the system. Without these deployments, there is no application to access. Each service handles specific functionality and must be running for the application to work.

**What would break if skipped**: Users cannot access the application. No web interface would be available. API endpoints would not respond. The ingress controller would return 503 Service Unavailable errors.

**Note**: If Flux is managing the deployment, these resources are automatically applied from `k8s/base/`. Verify deployment:

**Commands**:
```bash
# Check if services were deployed by Flux
kubectl get deployments -n tms-app
kubectl get services -n tms-app

# Monitor pod startup and readiness
kubectl get pods -n tms-app -w

# Check auth service
kubectl logs -n tms-app -l app=users-service --tail=20
kubectl exec -it -n tms-app -l app=users-service -- wget -O- http://localhost:8001/health

# Check task service
kubectl logs -n tms-app -l app=logout-service --tail=20
kubectl exec -it -n tms-app -l app=logout-service -- wget -O- http://localhost:8002/health

# Check frontend
kubectl logs -n tms-app -l app=frontend --tail=20
kubectl exec -it -n tms-app -l app=frontend -- wget -O- http://localhost:80

# Verify all pods are running and ready
kubectl get pods -n tms-app -o wide
```

**Expected output**:
```
NAME                              READY   STATUS    RESTARTS   AGE
users-service-abc123-def45        1/1     Running   0          3m
logout-service-ghi678-jkl90       1/1     Running   0          3m
frontend-mno123-pqr45             1/1     Running   0          3m
mysql-0                           1/1     Running   0          5m

NAME              TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)    AGE
users-service     ClusterIP   10.43.100.10     <none>        8001/TCP   3m
logout-service    ClusterIP   10.43.100.20     <none>        8002/TCP   3m
frontend          ClusterIP   10.43.100.30     <none>        80/TCP     3m
mysql             ClusterIP   10.43.100.40     <none>        3306/TCP   5m
```

### Step 12: Deploy Nginx Ingress Controller

**What this step does**: Installs the Nginx Ingress Controller which acts as a reverse proxy and load balancer. The controller watches for Ingress resources and configures Nginx to route external traffic to the appropriate backend services.

**Why this step is required**: Without an ingress controller, services are only accessible within the cluster. External users cannot reach the application. The ingress controller provides the entry point for HTTP traffic from outside the cluster.

**What would break if skipped**: The application would not be accessible from outside the cluster. The Ingress resource would exist but have no controller to implement it. Users could not access the web interface.

**Commands**:
```bash
# Install Nginx Ingress Controller using kubectl
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.9.5/deploy/static/provider/cloud/deploy.yaml

# Wait for ingress controller pods to be ready
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=120s

# Verify ingress controller is running
kubectl get pods -n ingress-nginx
kubectl get service -n ingress-nginx

# Check ingress controller logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/component=controller --tail=50
```

**Expected output**:
```
NAME                                       READY   STATUS    RESTARTS   AGE
ingress-nginx-controller-abc123-def45     1/1     Running   0          2m
ingress-nginx-admission-create-xyz78      0/1     Completed 0          2m
ingress-nginx-admission-patch-rst90       0/1     Completed 0          2m

NAME                                 TYPE           CLUSTER-IP      EXTERNAL-IP      PORT(S)
ingress-nginx-controller             LoadBalancer   10.43.200.10    10.205.144.151   80:30080/TCP,443:30443/TCP
ingress-nginx-controller-admission   ClusterIP      10.43.200.20    <none>           443/TCP
```

Note the EXTERNAL-IP for the ingress controller. This is the IP address you will use to access the application.

### Step 13: Configure Ingress Routes

**What this step does**: Creates Ingress resources that define URL path routing rules. The configuration routes requests to `/` to the frontend, `/api/auth/*` to the auth service, and `/api/tasks/*` to the task service.

**Why this step is required**: The ingress controller needs explicit rules to know which backend service should handle each request. Without Ingress resources, the controller does not know how to route traffic even though services exist.

**What would break if skipped**: All HTTP requests would return 404 Not Found. The ingress controller has no routing configuration. Services are running but unreachable from outside the cluster.

**Note**: If Flux is managing deployments, Ingress resources are automatically applied from `k8s/overlays/local/ingress.yaml`. Verify:

**Commands**:
```bash
# Check if Ingress resources were created by Flux
kubectl get ingress -n tms-app

# View detailed ingress configuration
kubectl describe ingress -n tms-app

# Check ingress addresses
kubectl get ingress -n tms-app -o wide

# Test ingress routing (replace with your ingress IP)
INGRESS_IP=$(kubectl get ingress -n tms-app tms-frontend-ingress -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "Application URL: http://$INGRESS_IP"

# Test each route
curl -I http://$INGRESS_IP/
curl -I http://$INGRESS_IP/api/auth/health
curl -I http://$INGRESS_IP/api/tasks/health
```

**Expected output**:
```
NAME                   CLASS   HOSTS   ADDRESS          PORTS   AGE
tms-ingress            nginx   *       10.205.144.151   80      5m
tms-frontend-ingress   nginx   *       10.205.144.151   80      5m

HTTP/1.1 200 OK
Server: nginx
Content-Type: text/html

HTTP/1.1 200 OK
Content-Type: application/json
```

### Step 14: Verify Deployment

**What this step does**: Performs comprehensive checks to ensure all components are deployed correctly and functioning. This includes checking pod status, service endpoints, database connectivity, and application functionality.

**Why this step is required**: Individual component deployment does not guarantee the entire system works end-to-end. This verification step confirms that services can communicate with each other and the database, and that the full application stack is operational.

**Commands**:
```bash
# Check all resources in the namespace
kubectl get all -n tms-app

# Verify pod health and readiness
kubectl get pods -n tms-app -o wide

# Check service endpoints have pod IPs assigned
kubectl get endpoints -n tms-app

# Test database connectivity from auth service
kubectl exec -it -n tms-app -l app=users-service -- nc -zv mysql 3306

# Test database connectivity from task service
kubectl exec -it -n tms-app -l app=logout-service -- nc -zv mysql 3306

# Check logs for errors
kubectl logs -n tms-app -l app=users-service --tail=20 | grep -i error
kubectl logs -n tms-app -l app=logout-service --tail=20 | grep -i error
kubectl logs -n tms-app -l app=frontend --tail=20 | grep -i error

# Verify Flux reconciliation status
flux get kustomizations
flux get sources git

# Check for any events indicating problems
kubectl get events -n tms-app --sort-by='.lastTimestamp' | tail -20
```

**Expected output**: All pods showing READY 1/1 and STATUS Running, all services showing endpoint IPs, database connection tests succeeding, no error messages in logs, Flux showing READY True.

## Post-Deployment Verification

### Functional Testing

Navigate to the application URL in a web browser using the ingress IP address:

```
http://<INGRESS_IP>/
```

#### Test User Registration

1. Click "Register" or navigate to the registration page
2. Enter a username, email, and password
3. Submit the registration form
4. Verify successful registration message appears
5. Check database for new user:
```bash
kubectl exec -it -n tms-app mysql-0 -- mysql -u root -prootpassword -e "USE task_management; SELECT id, username, email FROM users;"
```

#### Test User Login

1. Navigate to the login page
2. Enter registered username and password
3. Submit login form
4. Verify redirect to dashboard page
5. Check browser developer tools for JWT token in localStorage

#### Test Task Creation

1. While logged in to the dashboard
2. Create a new task with title and description
3. Submit the task creation form
4. Verify task appears in the task list
5. Check database for new task:
```bash
kubectl exec -it -n tms-app mysql-0 -- mysql -u root -prootpassword -e "USE task_management; SELECT * FROM tasks;"
```

#### Test Task Operations

1. Mark a task as completed by clicking the status toggle
2. Edit a task by clicking the edit button
3. Delete a task by clicking the delete button
4. Verify all operations reflect in the UI immediately
5. Refresh the page and verify changes persist

### API Testing

Test the REST API endpoints directly using curl:

```bash
# Get ingress IP
INGRESS_IP=$(kubectl get ingress -n tms-app tms-frontend-ingress -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Test health endpoints
curl http://$INGRESS_IP/api/auth/health
curl http://$INGRESS_IP/api/tasks/health

# Register a test user
curl -X POST http://$INGRESS_IP/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"testpass123"}'

# Login and get JWT token
TOKEN=$(curl -s -X POST http://$INGRESS_IP/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass123"}' | jq -r '.token')

echo "Token: $TOKEN"

# Create a task
curl -X POST http://$INGRESS_IP/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Task","description":"Test Description","priority":"high"}'

# Get all tasks
curl http://$INGRESS_IP/api/tasks \
  -H "Authorization: Bearer $TOKEN"

# Update task status (replace 1 with actual task ID)
curl -X PATCH http://$INGRESS_IP/api/tasks/1/status \
  -H "Authorization: Bearer $TOKEN"

# Delete a task (replace 1 with actual task ID)
curl -X DELETE http://$INGRESS_IP/api/tasks/1 \
  -H "Authorization: Bearer $TOKEN"
```

### Performance Testing

Monitor resource usage and response times:

```bash
# Check pod resource usage
kubectl top pods -n tms-app

# Monitor pod CPU and memory over time
watch kubectl top pods -n tms-app

# Check service response times
time curl -s http://$INGRESS_IP/ > /dev/null
time curl -s http://$INGRESS_IP/api/auth/health > /dev/null
time curl -s http://$INGRESS_IP/api/tasks/health > /dev/null

# Load test with ab (Apache Bench)
ab -n 100 -c 10 http://$INGRESS_IP/
ab -n 100 -c 10 http://$INGRESS_IP/api/auth/health
```

### GitOps Verification

Test that Flux properly syncs changes from Git:

```bash
# Make a trivial change to a manifest
kubectl edit deployment -n tms-app frontend
# Change replica count from 1 to 2

# Wait for Flux reconciliation (default 1 minute)
sleep 60

# Verify Flux reverted the change back to Git state
kubectl get deployment frontend -n tms-app -o jsonpath='{.spec.replicas}'
# Should show 1, not 2

# Check Flux reconciliation events
flux events --for Kustomization/tms-app -n flux-system
```

Expected behavior: Flux automatically reverts manual changes to match the Git repository state within one minute.

## Common Issues and Troubleshooting

### Issue: Pods stuck in ImagePullBackOff

**Symptoms**: Pods show status ImagePullBackOff or ErrImagePull.

**Cause**: Kubernetes cannot pull the container image from Docker Hub. Common reasons include invalid image names, missing images in the registry, or authentication failures.

**Diagnosis**:
```bash
kubectl describe pod -n tms-app <pod-name>
kubectl get events -n tms-app | grep -i "failed to pull"
```

**Resolution**:
1. Verify image exists in Docker Hub
2. Check image name and tag in deployment manifest
3. Ensure image name matches Docker Hub repository
4. For private registries, create image pull secret:
```bash
kubectl create secret docker-registry regcred \
  --docker-server=https://index.docker.io/v1/ \
  --docker-username=<username> \
  --docker-password=<password> \
  -n tms-app
```
5. Reference secret in deployment:
```yaml
spec:
  imagePullSecrets:
  - name: regcred
```

### Issue: Pods stuck in CrashLoopBackOff

**Symptoms**: Pods repeatedly restart and show status CrashLoopBackOff.

**Cause**: The container process exits immediately after starting. Common reasons include application errors, missing environment variables, or failed database connections.

**Diagnosis**:
```bash
kubectl logs -n tms-app <pod-name>
kubectl logs -n tms-app <pod-name> --previous
kubectl describe pod -n tms-app <pod-name>
```

**Resolution**:
1. Check logs for error messages
2. Verify all required environment variables are set
3. Verify secrets are properly created and mounted
4. Test database connectivity:
```bash
kubectl exec -it -n tms-app mysql-0 -- mysql -u taskuser -prootpassword -e "SHOW DATABASES;"
```
5. Check application configuration matches environment

### Issue: Database connection refused

**Symptoms**: Service logs show "ECONNREFUSED" or "Can't connect to MySQL server" errors.

**Cause**: MySQL service is not running, not ready, or services cannot resolve the MySQL hostname.

**Diagnosis**:
```bash
kubectl get pods -n tms-app -l app=mysql
kubectl logs -n tms-app -l app=mysql
kubectl get service mysql -n tms-app
kubectl get endpoints mysql -n tms-app
```

**Resolution**:
1. Verify MySQL pod is running and ready
2. Check MySQL logs for startup errors
3. Verify service has endpoint IPs assigned
4. Test DNS resolution from app pod:
```bash
kubectl exec -it -n tms-app -l app=users-service -- nslookup mysql
```
5. Verify MySQL is listening on port 3306:
```bash
kubectl exec -it -n tms-app mysql-0 -- netstat -tlnp | grep 3306
```

### Issue: 404 errors for API endpoints

**Symptoms**: Frontend loads but API requests return 404 Not Found.

**Cause**: Ingress routing is misconfigured or services are not properly labeled.

**Diagnosis**:
```bash
kubectl get ingress -n tms-app -o yaml
kubectl describe ingress -n tms-app
kubectl get service -n tms-app -o wide
kubectl get endpoints -n tms-app
```

**Resolution**:
1. Verify ingress paths match API request paths
2. Check service selectors match pod labels
3. Verify services have endpoint IPs assigned
4. Test service directly from within cluster:
```bash
kubectl run test --rm -it --image=curlimages/curl -- curl http://users-service.tms-app:8001/api/auth/health
kubectl run test --rm -it --image=curlimages/curl -- curl http://logout-service.tms-app:8002/api/tasks/health
```

### Issue: Flux not syncing changes

**Symptoms**: Changes pushed to Git do not appear in the cluster after several minutes.

**Cause**: Flux controllers are not running, GitRepository is suspended, or reconciliation has failed.

**Diagnosis**:
```bash
flux get sources git
flux get kustomizations
kubectl get pods -n flux-system
flux logs --follow
kubectl describe gitrepository -n flux-system tms-app-repo
kubectl describe kustomization -n flux-system tms-app
```

**Resolution**:
1. Verify Flux pods are running in flux-system namespace
2. Check GitRepository resource shows READY True
3. Check Kustomization resource shows READY True
4. Review Flux logs for reconciliation errors
5. Force reconciliation:
```bash
flux reconcile source git tms-app-repo
flux reconcile kustomization tms-app
```
6. Verify Git branch name matches repository default branch

### Issue: Frontend shows blank white page

**Symptoms**: Accessing the application URL shows a white page with no content.

**Cause**: Frontend assets are not loading due to incorrect nginx configuration or ingress rewrite rules breaking asset paths.

**Diagnosis**:
```bash
kubectl logs -n tms-app -l app=frontend
curl -I http://<INGRESS_IP>/
curl http://<INGRESS_IP>/ | grep -i "script\|link"
```

**Resolution**:
1. Check browser developer console for 404 errors on JS/CSS files
2. Verify ingress does not have rewrite-target annotation for frontend routes
3. Check nginx.conf in frontend container has correct try_files directive
4. Verify frontend service is running:
```bash
kubectl exec -it -n tms-app -l app=frontend -- wget -O- http://localhost:80
```

### Issue: JWT authentication fails

**Symptoms**: Login succeeds but subsequent API calls return 401 Unauthorized.

**Cause**: JWT_SECRET environment variable is missing, different between services, or tokens are malformed.

**Diagnosis**:
```bash
kubectl get secret tms-app-secrets -n tms-app -o jsonpath='{.data.JWT_SECRET}' | base64 -d
kubectl exec -it -n tms-app -l app=users-service -- env | grep JWT
kubectl exec -it -n tms-app -l app=logout-service -- env | grep JWT
```

**Resolution**:
1. Verify JWT_SECRET is set in secrets
2. Ensure both auth and task services use the same JWT_SECRET
3. Check token is being sent in Authorization header:
```bash
# In browser developer tools:
localStorage.getItem('token')
```
4. Verify token format: should be three base64 sections separated by dots

### Issue: Persistent volume claim pending

**Symptoms**: MySQL pod stuck in Pending state, PVC shows status Pending.

**Cause**: No persistent volume available or no storage class configured for dynamic provisioning.

**Diagnosis**:
```bash
kubectl get pvc -n tms-app
kubectl describe pvc -n tms-app mysql-data-mysql-0
kubectl get pv
kubectl get storageclass
```

**Resolution**:
1. Check if storage class exists:
```bash
kubectl get storageclass
```
2. If no storage class, create one or use local-path-provisioner:
```bash
kubectl apply -f https://raw.githubusercontent.com/rancher/local-path-provisioner/v0.0.24/deploy/local-path-storage.yaml
```
3. Update PVC to use available storage class
4. For RKE2, default local-path storage class should exist automatically

## Security Considerations

### Container Image Security

All container images undergo automated security scanning using Trivy. Scans detect vulnerabilities in base images, application dependencies, and system packages. Images with critical vulnerabilities should not be deployed to production environments.

Base images are regularly updated to include security patches. Alpine Linux and Debian Slim images are used to minimize attack surface. Multi-stage builds ensure build tools are not present in production images.

### Secret Management

Kubernetes Secrets are used to store sensitive data including database passwords and JWT signing keys. In local and staging environments, secrets are stored in Git for convenience. This is acceptable for development but must never be done for production.

Production secrets should be managed using external secret management systems such as HashiCorp Vault, Azure Key Vault, or sealed secrets. The External Secrets Operator can synchronize secrets from these systems into Kubernetes.

Alternatively, Sealed Secrets can encrypt secrets before committing to Git, allowing GitOps workflows while maintaining security. The Sealed Secrets controller decrypts secrets in the cluster using a private key that never leaves the cluster.

### Network Security

Services communicate within the cluster using ClusterIP services which are not externally accessible. Only the ingress controller exposes ports to the outside network. This limits the attack surface to a single entry point.

Network policies can be implemented to further restrict pod-to-pod communication. For example, only the auth and task services should be able to connect to the MySQL service. The frontend should not have direct database access.

### Authentication and Authorization

JWT tokens provide stateless authentication between the frontend and backend services. Tokens contain user identity claims and are signed with a secret key to prevent tampering. Services verify token signatures before processing requests.

Passwords are hashed using bcrypt before storage in the database. Bcrypt is a slow hashing algorithm designed to resist brute force attacks. Plaintext passwords are never stored or logged.

### Database Security

MySQL connections use native password authentication. For production deployments, consider using TLS encrypted connections between services and the database. MySQL 8.0 supports SSL/TLS connections with certificate-based authentication.

Database user permissions should follow the principle of least privilege. Application users should not have administrative privileges. Separate read-only users should be created for reporting or analytics workloads.

### CI/CD Security

**Multi-Layer Scanning**: The CI/CD pipeline implements comprehensive security scanning at multiple stages:

1. **Trivy Vulnerability Scanning**: Scans images for CVE vulnerabilities (CRITICAL, HIGH, MEDIUM severity levels)
2. **SBOM Generation**: Creates Software Bill of Materials (SBOM) in SPDX-JSON format for supply chain transparency
3. **Grype Scanning**: Analyzes SBOM for known vulnerabilities in dependencies
4. **Secret Scanning**: Detects hardcoded secrets in source code before image build
5. **Configuration Scanning**: Validates container security best practices

**Build Security Features**:
- **Provenance Attestation**: BuildKit provenance enabled to verify build authenticity
- **SBOM Artifacts**: Generated for every image to track all dependencies
- **Scan Reports**: SARIF format uploaded to GitHub Security, JSON format for parsing and alerting
- **Build Isolation**: Workflows run in ephemeral runners with no production access

**Workflow Security**:
- GitHub Actions secrets are encrypted and restricted to administrators
- Dependency pinning with hash verification (uses/actions@v5.0.0)
- Minimal workflow permissions (contents: read, security-events: write)
- No hardcoded credentials in workflow files

### Kubernetes Security

**Network Policies**: Zero-trust networking with default-deny rules:
- Default deny-all ingress and egress traffic
- Frontend: Only accepts traffic from ingress-nginx, only connects to auth/task services
- Auth/Task Services: Only accepts traffic from frontend/ingress, only connects to MySQL
- MySQL: Only accepts traffic from auth/task services, no external connections
- DNS: Explicitly allowed for all pods that need external resolution

**RBAC (Role-Based Access Control)**:
- Dedicated service accounts for each service (frontend-sa, auth-service-sa, task-service-sa, mysql-sa)
- Least-privilege access: Only auth/task services can read secrets
- Role bindings limit secret access to specific secret names (tms-app-secrets only)
- Frontend service account has no secret access (runs static nginx)

**Pod Security**:
```yaml
securityContext:
  runAsNonRoot: true             # Prevents root execution
  runAsUser: 1000                # Specific non-privileged UID
  fsGroup: 1000                  # File system group ownership
  seccompProfile:
    type: RuntimeDefault         # Secure computing mode restrictions
  allowPrivilegeEscalation: false # Prevents gaining additional privileges
  readOnlyRootFilesystem: true    # Immutable container filesystem (where possible)
  capabilities:
    drop: [ALL]                   # Drop all Linux capabilities by default
    add: [NET_BIND_SERVICE]       # Only add required capabilities (nginx port 80)
```

**Resource Protection**:
- CPU and memory requests/limits defined for all pods
- Prevents resource exhaustion attacks
- Enables fair resource distribution
- PodDisruptionBudgets ensure minimum 1 replica during voluntary disruptions

**Health Monitoring**:
- Liveness probes: Restart unhealthy pods automatically
- Readiness probes: Remove pods from load balancer when not ready
- Health check endpoints: /health for auth (8001) and task (8002) services
- MySQL probes: mysqladmin ping with appropriate thresholds

### Ingress Security

The ingress controller terminates HTTP traffic. For production deployments, configure TLS certificates to enable HTTPS. Let's Encrypt can provide free automated certificates using cert-manager.

Rate limiting should be configured on the ingress controller to prevent denial of service attacks. Authentication can be required at the ingress level using basic auth or OAuth2 proxies.

**Production TLS Configuration**:
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/limit-rps: "10"
    nginx.ingress.kubernetes.io/limit-connections: "5"
spec:
  tls:
  - hosts:
    - yourdomain.com
    secretName: tms-tls-cert
```

### Comprehensive Security Documentation

For complete security implementation details, see [SECURITY_IMPLEMENTATION.md](./SECURITY_IMPLEMENTATION.md):
- All security layers (CI/CD, Container, Kubernetes, Network, Application)
- Security testing procedures
- Compliance standards (CIS, OWASP, PCI DSS, GDPR)
- Incident response procedures
- Security checklist and audit trail
- Continuous improvement metrics

## Best Practices

### GitOps Workflow

All infrastructure and application changes must go through Git pull requests. This provides code review, approval workflows, and audit trails. Manual kubectl commands should only be used for debugging, never for making persistent changes.

Use feature branches for development work. Merge to master or main branch only after review and testing. Tag releases in Git to enable easy rollback to known good states.

### Environment Separation

Use separate Kustomize overlays for each environment. Never share secrets between environments. Production should use different databases, registries, and infrastructure than development or staging.

Implement promotion workflows where changes are tested in development and staging before reaching production. Use branch protections to prevent direct commits to production environment branches.

### Monitoring and Observability

Deploy metrics collection using Prometheus and visualization using Grafana. Monitor pod CPU, memory, and restart counts. Set up alerts for high resource usage or frequent crashes.

Implement centralized logging using Fluentd or Fluent Bit to ship logs to Elasticsearch or Loki. Correlation IDs should be added to logs to trace requests across services.

Implement health check endpoints in all services. Kubernetes uses these endpoints for liveness and readiness probes. Failed health checks trigger pod restarts or removal from service load balancing.

### Resource Management

Define CPU and memory requests and limits for all pods. Requests ensure scheduling on nodes with sufficient resources. Limits prevent pods from consuming excessive resources and affecting other workloads.

Configure horizontal pod autoscaling based on CPU or custom metrics. This automatically adds or removes pod replicas based on load. Vertical pod autoscaling can adjust resource requests over time.

### Backup and Disaster Recovery

Implement regular database backups. For MySQL on Kubernetes, use tools like Velero for volume snapshots or mysqldump for logical backups. Test backup restoration regularly.

Document the complete deployment process including all external dependencies. Store documentation in the Git repository alongside code. Disaster recovery procedures should be tested periodically.

### Dependency Management

Keep base images and application dependencies up to date. Security vulnerabilities are frequently discovered in libraries and frameworks. Automated tools like Dependabot can create pull requests for dependency updates.

Pin image versions to specific tags rather than using latest. This ensures reproducible deployments and prevents unexpected changes. Use semantic versioning and update tags deliberately.

### High Availability

Run multiple replicas of each service for redundancy. Configure pod anti-affinity rules to spread replicas across different nodes. This prevents a single node failure from taking down a service.

Use rolling update strategies for deployments. Configure appropriate maxUnavailable and maxSurge parameters to maintain capacity during updates. Implement proper health checks to detect failed pods quickly.

## Cleanup / Uninstall Steps

### Remove Application Resources

To remove the application while keeping Flux and Kubernetes infrastructure:

```bash
# Delete the Flux Kustomization (this removes all app resources)
kubectl delete kustomization tms-app -n flux-system

# Verify resources are being removed
kubectl get all -n tms-app

# Manually delete namespace if needed
kubectl delete namespace tms-app

# Delete persistent volumes (WARNING: destroys database data)
kubectl delete pvc --all -n tms-app
kubectl get pv | grep tms-app | awk '{print $1}' | xargs kubectl delete pv
```

### Remove Flux CD

To remove Flux GitOps system:

```bash
# Uninstall Flux
flux uninstall --silent

# Verify Flux resources are removed
kubectl get all -n flux-system
kubectl get namespace flux-system

# Delete namespace if it still exists
kubectl delete namespace flux-system
```

### Remove Nginx Ingress Controller

To remove the ingress controller:

```bash
# Delete ingress controller resources
kubectl delete -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.9.5/deploy/static/provider/cloud/deploy.yaml

# Verify removal
kubectl get all -n ingress-nginx
kubectl delete namespace ingress-nginx
```

### Complete Cleanup

To remove everything including the namespace:

```bash
# Delete application namespace (removes all resources in it)
kubectl delete namespace tms-app

# Delete Flux
flux uninstall --silent
kubectl delete namespace flux-system

# Delete ingress controller
kubectl delete namespace ingress-nginx

# Verify all resources are removed
kubectl get namespaces
kubectl get pv
```

### Clean Docker Images Locally

To remove locally built images:

```bash
# List all task-manager images
docker images | grep task-manager

# Remove specific images
docker rmi khaledhawil/task-manager-auth:latest
docker rmi khaledhawil/task-manager-task:latest
docker rmi khaledhawil/task-manager-frontend:latest
docker rmi khaledhawil/task-manager-nginx:latest

# Or remove all at once (if no other images share the name pattern)
docker images | grep task-manager | awk '{print $3}' | xargs docker rmi -f

# Clean up dangling images
docker image prune -a
```

### Remove Git Repository Clone

To remove the local repository:

```bash
cd ..
rm -rf End-to-End-DevOps-AWS-Php-MySQL
```

### Important Notes

- Deleting persistent volumes destroys all database data irreversibly
- Ensure you have backups before removing production resources
- Some cloud resources may incur costs until explicitly deleted
- Removing namespaces automatically removes all resources within them
- PersistentVolumes may need manual deletion even after PVC removal depending on reclaim policy
