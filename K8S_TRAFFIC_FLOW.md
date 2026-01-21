# Kubernetes Traffic Flow Architecture

Complete request flow diagram showing how user authentication and task operations traverse the Kubernetes cluster.

---

## Complete Traffic Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                    USER DEVICE                                   │
│                              (Browser / Mobile App)                              │
└──────────────────────────────────┬───────────────────────────────────────────────┘
                                   │
                                   │ HTTP Request
                                   │ (http://10.205.144.151)
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            KUBERNETES CLUSTER                                    │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                        INGRESS CONTROLLER                                 │  │
│  │                    (nginx-ingress / traefik)                              │  │
│  │                                                                           │  │
│  │  • SSL/TLS Termination                                                    │  │
│  │  • Path-based Routing                                                     │  │
│  │  • Load Balancing                                                         │  │
│  │  • Rate Limiting (Optional)                                               │  │
│  └──────────┬────────────────────────────┬───────────────────────────────────┘  │
│             │                            │                                       │
│             │ Routes:                    │ Routes:                               │
│             │ /                          │ /api/auth/*                           │
│             │ /login                     │ /api/tasks/*                          │
│             │ /register                  │                                       │
│             │ /dashboard                 │                                       │
│             │                            │                                       │
│             ▼                            ▼                                       │
│  ┌──────────────────────┐    ┌──────────────────────┐    ┌──────────────────┐  │
│  │  Frontend Service    │    │ Auth Service         │    │ Task Service     │  │
│  │  (ClusterIP)         │    │ (ClusterIP)          │    │ (ClusterIP)      │  │
│  │  Port: 80            │    │ Port: 8001           │    │ Port: 8002       │  │
│  └──────────┬───────────┘    └──────────┬───────────┘    └────────┬─────────┘  │
│             │                            │                          │            │
│             │ Load Balance               │ Load Balance             │            │
│             │ via Endpoints              │ via Endpoints            │            │
│             │                            │                          │            │
│             ▼                            ▼                          ▼            │
│  ┌──────────────────────┐    ┌──────────────────────┐    ┌──────────────────┐  │
│  │  Frontend Pod(s)     │    │ Auth Service Pod(s)  │    │ Task Service     │  │
│  │  ┌────────────────┐  │    │ ┌────────────────┐   │    │ Pod(s)           │  │
│  │  │ Nginx          │  │    │ │ Node.js        │   │    │ ┌──────────────┐ │  │
│  │  │ (Static Files) │  │    │ │ Express        │   │    │ │ Python       │ │  │
│  │  │                │  │    │ │                │   │    │ │ Flask        │ │  │
│  │  │ - index.html   │  │    │ │ - /register    │   │    │ │              │ │  │
│  │  │ - App.jsx      │  │    │ │ - /login       │   │    │ │ - GET /tasks │ │  │
│  │  │ - Dashboard    │  │    │ │ - /verify      │   │    │ │ - POST /tasks│ │  │
│  │  │                │  │    │ │                │   │    │ │ - PUT /tasks │ │  │
│  │  │ HPA: 1-5       │  │    │ │ Rate Limiter   │   │    │ │ - DEL /tasks │ │  │
│  │  │ Replicas       │  │    │ │ Helmet         │   │    │ │              │ │  │
│  │  │                │  │    │ │ CORS           │   │    │ │ Rate Limiter │ │  │
│  │  └────────────────┘  │    │ │                │   │    │ │ CORS         │ │  │
│  │                      │    │ │ HPA: 1-10      │   │    │ │ Pydantic     │ │  │
│  │                      │    │ │ Replicas       │   │    │ │              │ │  │
│  │                      │    │ └────────────────┘   │    │ │ HPA: 1-10    │ │  │
│  │                      │    │                      │    │ │ Replicas     │ │  │
│  │                      │    │                      │    │ └──────────────┘ │  │
│  └──────────────────────┘    └──────────┬───────────┘    └────────┬─────────┘  │
│                                         │                          │            │
│                                         │ MySQL Queries            │            │
│                                         │ (SELECT, INSERT)         │            │
│                                         │                          │            │
│                                         ▼                          ▼            │
│                              ┌────────────────────────────────────┐             │
│                              │      MySQL Service                 │             │
│                              │      (ClusterIP)                   │             │
│                              │      Port: 3306                    │             │
│                              └──────────────┬─────────────────────┘             │
│                                             │                                   │
│                                             ▼                                   │
│                              ┌────────────────────────────────────┐             │
│                              │      MySQL Pod                     │             │
│                              │      ┌──────────────────────────┐  │             │
│                              │      │ MySQL 8.0               │  │             │
│                              │      │                         │  │             │
│                              │      │ Tables:                 │  │             │
│                              │      │ - users                 │  │             │
│                              │      │   (id, username, pass)  │  │             │
│                              │      │ - tasks                 │  │             │
│                              │      │   (id, user_id, title)  │  │             │
│                              │      │                         │  │             │
│                              │      │ Persistent Volume       │  │             │
│                              │      │ (10Gi Storage)          │  │             │
│                              │      └──────────────────────────┘  │             │
│                              └────────────────────────────────────┘             │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## User Login Flow (Detailed)

```
┌─────────┐                                                           ┌──────────┐
│  User   │                                                           │ Database │
└────┬────┘                                                           └─────┬────┘
     │                                                                      │
     │ 1. Open http://10.205.144.151/login                                 │
     ├─────────────────────────────────────────────►                       │
     │                                              Ingress Controller     │
     │                                                     │                │
     │                                                     ▼                │
     │                                              Routes to               │
     │                                              Frontend Service        │
     │                                                     │                │
     │                                                     ▼                │
     │                                              Frontend Pod            │
     │                                              (Nginx serves           │
     │                                               login.html)            │
     │                                                     │                │
     │ 2. HTML Page Returned                              │                │
     │◄────────────────────────────────────────────────────                │
     │                                                                      │
     │ 3. User enters credentials                                          │
     │    {username: "user1", password: "Pass123!@#"}                      │
     │    JavaScript validation checks:                                    │
     │    - Password length >= 12                                          │
     │    - Contains uppercase, lowercase, number, special char            │
     │                                                                      │
     │ 4. POST /api/auth/login                                             │
     │    {username: "user1", password: "Pass123!@#"}                      │
     ├─────────────────────────────────────────────►                       │
     │                                              Ingress Controller     │
     │                                                     │                │
     │                                                     ▼                │
     │                                              Routes /api/auth/*      │
     │                                              to Auth Service         │
     │                                                     │                │
     │                                                     ▼                │
     │                                              Auth Service Pod        │
     │                                              (Node.js/Express)       │
     │                                                     │                │
     │                                              5. Rate Limit Check     │
     │                                                 (5 req/15min)        │
     │                                                     │                │
     │                                              6. Input Validation     │
     │                                                 (express-validator)  │
     │                                                     │                │
     │                                              7. Query Database       │
     │                                                     │                │
     │                                                     ├──────────────► │
     │                                                     │ SELECT * FROM  │
     │                                                     │ users WHERE    │
     │                                                     │ username=?     │
     │                                                     │                │
     │                                              8. User Record          │
     │                                                     │◄───────────────┤
     │                                                     │                │
     │                                              9. Compare Password     │
     │                                                 bcrypt.compare()     │
     │                                                     │                │
     │                                              10. Generate JWT        │
     │                                                  Token               │
     │                                                  {                   │
     │                                                   userId: 1,         │
     │                                                   exp: 24h           │
     │                                                  }                   │
     │                                                     │                │
     │ 11. Return JWT Token                               │                │
     │◄────────────────────────────────────────────────────                │
     │    {token: "eyJhbGc..."}                                             │
     │                                                                      │
     │ 12. Store token in localStorage                                     │
     │     Navigate to /dashboard                                          │
     │                                                                      │
     ▼                                                                      │
   Done                                                                     │
```

---

## Task Creation Flow (Detailed)

```
┌─────────┐                                                           ┌──────────┐
│  User   │                                                           │ Database │
└────┬────┘                                                           └─────┬────┘
     │                                                                      │
     │ User is logged in with JWT token in localStorage                    │
     │                                                                      │
     │ 1. Click "Create Task" button                                       │
     │    Fill form:                                                       │
     │    - Title: "Complete DevOps Project"                               │
     │    - Description: "Implement CI/CD pipeline"                        │
     │    - Priority: "high"                                               │
     │                                                                      │
     │ 2. POST /api/tasks                                                  │
     │    Headers: {Authorization: "Bearer eyJhbGc..."}                    │
     │    Body: {                                                          │
     │      title: "Complete DevOps Project",                              │
     │      description: "Implement CI/CD pipeline",                       │
     │      priority: "high"                                               │
     │    }                                                                 │
     ├─────────────────────────────────────────────►                       │
     │                                              Ingress Controller     │
     │                                                     │                │
     │                                                     ▼                │
     │                                              Routes /api/tasks/*     │
     │                                              to Task Service         │
     │                                                     │                │
     │                                                     ▼                │
     │                                              Task Service Pod        │
     │                                              (Python/Flask)          │
     │                                                     │                │
     │                                              3. Rate Limit Check     │
     │                                                 (20 req/min)         │
     │                                                     │                │
     │                                              4. Verify JWT Token     │
     │                                                 jwt.decode()         │
     │                                                     │                │
     │                                              5. Extract userId       │
     │                                                 from token           │
     │                                                 userId = 1           │
     │                                                     │                │
     │                                              6. Validate Input       │
     │                                                 (Pydantic)           │
     │                                                 - title: 1-200 chars│
     │                                                 - desc: 1-2000 chars│
     │                                                 - priority: enum     │
     │                                                     │                │
     │                                              7. Insert into DB      │
     │                                                     │                │
     │                                                     ├──────────────► │
     │                                                     │ INSERT INTO    │
     │                                                     │ tasks          │
     │                                                     │ (user_id,      │
     │                                                     │  title,        │
     │                                                     │  description,  │
     │                                                     │  priority,     │
     │                                                     │  status)       │
     │                                                     │ VALUES         │
     │                                                     │ (1, '...', ... │
     │                                                     │  'pending')    │
     │                                                     │                │
     │                                              8. Insert ID            │
     │                                                     │◄───────────────┤
     │                                                     │ taskId = 42    │
     │                                                     │                │
     │ 9. Success Response                                │                │
     │◄────────────────────────────────────────────────────                │
     │    {                                                                 │
     │      message: "Task created successfully",                           │
     │      id: 42                                                          │
     │    }                                                                 │
     │                                                                      │
     │ 10. Update UI                                                       │
     │     Fetch tasks again to refresh list                               │
     │                                                                      │
     │ 11. GET /api/tasks                                                  │
     │     Headers: {Authorization: "Bearer eyJhbGc..."}                   │
     ├─────────────────────────────────────────────►                       │
     │                                              Task Service Pod        │
     │                                                     │                │
     │                                              12. Query Database      │
     │                                                     │                │
     │                                                     ├──────────────► │
     │                                                     │ SELECT * FROM  │
     │                                                     │ tasks WHERE    │
     │                                                     │ user_id = 1    │
     │                                                     │                │
     │                                              13. Task List           │
     │                                                     │◄───────────────┤
     │                                                     │                │
     │ 14. Return Tasks Array                             │                │
     │◄────────────────────────────────────────────────────                │
     │    [{                                                                │
     │      id: 42,                                                         │
     │      title: "Complete DevOps Project",                               │
     │      description: "Implement CI/CD pipeline",                        │
     │      priority: "high",                                               │
     │      status: "pending",                                              │
     │      created_at: "2026-01-21T..."                                    │
     │    }, ...]                                                           │
     │                                                                      │
     │ 15. Render tasks in UI                                              │
     │                                                                      │
     ▼                                                                      │
   Done                                                                     │
```

---

## Network Policy Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         KUBERNETES NETWORK POLICIES                      │
│                         (Zero-Trust Model)                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  1. Default Deny All                                                    │
│     ┌────────────────────────────────────────────────────────────────┐  │
│     │ All pods: DENY all ingress and egress by default              │  │
│     └────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  2. Frontend Network Policy                                             │
│     ┌────────────────────────────────────────────────────────────────┐  │
│     │ Ingress:                                                       │  │
│     │   - FROM: kube-system namespace (Ingress Controller)          │  │
│     │   - PORT: 80/TCP                                               │  │
│     │                                                                │  │
│     │ Egress:                                                        │  │
│     │   - TO: kube-system (DNS)                                      │  │
│     │   - PORT: 53/UDP, 53/TCP                                       │  │
│     │   - TO: auth-service, task-service                             │  │
│     │   - PORT: 8001/TCP, 8002/TCP                                   │  │
│     └────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  3. Auth Service Network Policy                                         │
│     ┌────────────────────────────────────────────────────────────────┐  │
│     │ Ingress:                                                       │  │
│     │   - FROM: kube-system namespace (Ingress Controller)          │  │
│     │   - FROM: frontend pods                                        │  │
│     │   - PORT: 8001/TCP                                             │  │
│     │                                                                │  │
│     │ Egress:                                                        │  │
│     │   - TO: kube-system (DNS)                                      │  │
│     │   - PORT: 53/UDP, 53/TCP                                       │  │
│     │   - TO: mysql pod                                              │  │
│     │   - PORT: 3306/TCP                                             │  │
│     └────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  4. Task Service Network Policy                                         │
│     ┌────────────────────────────────────────────────────────────────┐  │
│     │ Ingress:                                                       │  │
│     │   - FROM: kube-system namespace (Ingress Controller)          │  │
│     │   - FROM: frontend pods                                        │  │
│     │   - PORT: 8002/TCP                                             │  │
│     │                                                                │  │
│     │ Egress:                                                        │  │
│     │   - TO: kube-system (DNS)                                      │  │
│     │   - PORT: 53/UDP, 53/TCP                                       │  │
│     │   - TO: mysql pod                                              │  │
│     │   - PORT: 3306/TCP                                             │  │
│     └────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  5. MySQL Network Policy                                                │
│     ┌────────────────────────────────────────────────────────────────┐  │
│     │ Ingress:                                                       │  │
│     │   - FROM: auth-service pods                                    │  │
│     │   - FROM: task-service pods                                    │  │
│     │   - PORT: 3306/TCP                                             │  │
│     │                                                                │  │
│     │ Egress:                                                        │  │
│     │   - TO: kube-system (DNS)                                      │  │
│     │   - PORT: 53/UDP, 53/TCP                                       │  │
│     └────────────────────────────────────────────────────────────────┘  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Request Path Summary

### Login Request Path
```
User Browser
    ↓
[HTTP] http://10.205.144.151/api/auth/login
    ↓
Ingress Controller (nginx-ingress)
    ↓
[Path: /api/auth/*] → Auth Service (ClusterIP 10.x.x.x:8001)
    ↓
Load Balancer selects Pod
    ↓
Auth Service Pod (192.168.x.x:8001)
    ↓
Express.js Middleware Chain:
    1. trust proxy
    2. helmet (security headers)
    3. rate limiter (5/15min)
    4. CORS check
    5. body parser
    6. input validation
    ↓
MySQL Service (ClusterIP 10.x.x.x:3306)
    ↓
MySQL Pod (192.168.x.x:3306)
    ↓
Query: SELECT * FROM users WHERE username = ?
    ↓
[Response] User record with hashed password
    ↓
bcrypt.compare(password, hash)
    ↓
jwt.sign({userId, exp})
    ↓
[HTTP 200] {token: "eyJhbGc..."}
    ↓
User Browser (stores in localStorage)
```

### Task Creation Request Path
```
User Browser (with JWT in Authorization header)
    ↓
[HTTP] POST http://10.205.144.151/api/tasks
    ↓
Ingress Controller (nginx-ingress)
    ↓
[Path: /api/tasks/*] → Task Service (ClusterIP 10.x.x.x:8002)
    ↓
Load Balancer selects Pod
    ↓
Task Service Pod (192.168.x.x:8002)
    ↓
Flask Middleware Chain:
    1. ProxyFix (trust proxy)
    2. rate limiter (20/min)
    3. CORS check
    4. JWT verification
    5. Pydantic validation
    ↓
MySQL Service (ClusterIP 10.x.x.x:3306)
    ↓
MySQL Pod (192.168.x.x:3306)
    ↓
Query: INSERT INTO tasks (user_id, title, description, priority, status)
       VALUES (?, ?, ?, ?, 'pending')
    ↓
[Response] taskId = 42
    ↓
[HTTP 201] {message: "Task created", id: 42}
    ↓
User Browser (updates UI)
```

---

## Security Layers in Traffic Flow

```
┌──────────────────────────────────────────────────────────────┐
│                     SECURITY LAYERS                          │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Layer 1: Network Level (Kubernetes)                        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ • Network Policies (Zero-trust)                        │ │
│  │ • Service mesh isolation                               │ │
│  │ • No direct pod-to-pod communication                   │ │
│  └────────────────────────────────────────────────────────┘ │
│                            ↓                                 │
│  Layer 2: Ingress Level                                     │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ • SSL/TLS termination                                  │ │
│  │ • Path-based routing rules                             │ │
│  │ • Rate limiting (optional)                             │ │
│  └────────────────────────────────────────────────────────┘ │
│                            ↓                                 │
│  Layer 3: Application Level (Auth Service)                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ • Helmet security headers                              │ │
│  │ • CORS validation                                      │ │
│  │ • Rate limiting:                                       │ │
│  │   - Login: 5/15min                                     │ │
│  │   - Register: 3/hour                                   │ │
│  │   - General: 100/15min                                 │ │
│  │ • Input validation (express-validator)                │ │
│  │ • Password complexity check                            │ │
│  │ • Bcrypt hashing (10 salt rounds)                     │ │
│  │ • JWT token generation (24h expiry)                   │ │
│  └────────────────────────────────────────────────────────┘ │
│                            ↓                                 │
│  Layer 4: Application Level (Task Service)                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ • CORS validation                                      │ │
│  │ • Rate limiting: 20/min for task creation             │ │
│  │ • JWT token verification                               │ │
│  │ • Pydantic data validation                             │ │
│  │ • SQL injection prevention (parameterized queries)    │ │
│  └────────────────────────────────────────────────────────┘ │
│                            ↓                                 │
│  Layer 5: Database Level                                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ • Network policy (only services can connect)          │ │
│  │ • Authentication required                              │ │
│  │ • Persistent volume encryption                         │ │
│  │ • Regular backups                                      │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## Pod-to-Pod Communication

```
┌──────────────────────────────────────────────────────────────────┐
│                    KUBERNETES NAMESPACE: tms-app                  │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Frontend Pod (192.168.1.10)                                     │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ Can communicate with:                                       │ │
│  │ • DNS (kube-system)              → 53/UDP, 53/TCP          │ │
│  │ • Auth Service (via Service)     → 8001/TCP                │ │
│  │ • Task Service (via Service)     → 8002/TCP                │ │
│  │                                                             │ │
│  │ Cannot communicate with:                                    │ │
│  │ • MySQL directly                 → BLOCKED                  │ │
│  │ • Other namespaces               → BLOCKED                  │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  Auth Service Pod (192.168.1.20)                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ Can communicate with:                                       │ │
│  │ • DNS (kube-system)              → 53/UDP, 53/TCP          │ │
│  │ • MySQL (via Service)            → 3306/TCP                │ │
│  │                                                             │ │
│  │ Cannot communicate with:                                    │ │
│  │ • Frontend                       → BLOCKED                  │ │
│  │ • Task Service                   → BLOCKED                  │ │
│  │ • Other namespaces               → BLOCKED                  │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  Task Service Pod (192.168.1.30)                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ Can communicate with:                                       │ │
│  │ • DNS (kube-system)              → 53/UDP, 53/TCP          │ │
│  │ • MySQL (via Service)            → 3306/TCP                │ │
│  │                                                             │ │
│  │ Cannot communicate with:                                    │ │
│  │ • Frontend                       → BLOCKED                  │ │
│  │ • Auth Service                   → BLOCKED                  │ │
│  │ • Other namespaces               → BLOCKED                  │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  MySQL Pod (192.168.1.40)                                        │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ Can receive from:                                           │ │
│  │ • Auth Service                   → 3306/TCP                │ │
│  │ • Task Service                   → 3306/TCP                │ │
│  │                                                             │ │
│  │ Cannot receive from:                                        │ │
│  │ • Frontend                       → BLOCKED                  │ │
│  │ • External sources               → BLOCKED                  │ │
│  │ • Other namespaces               → BLOCKED                  │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## High Availability & Load Balancing

```
                        [User Request]
                              |
                              ▼
                    ┌─────────────────┐
                    │ Ingress         │
                    │ Controller      │
                    │ (HA: 3 replicas)│
                    └────────┬────────┘
                             │
                 ┌───────────┼───────────┐
                 │           │           │
                 ▼           ▼           ▼
         ┌──────────┐ ┌──────────┐ ┌──────────┐
         │  Auth    │ │  Auth    │ │  Auth    │
         │  Pod 1   │ │  Pod 2   │ │  Pod 3   │
         │  (HPA)   │ │  (HPA)   │ │  (HPA)   │
         └────┬─────┘ └────┬─────┘ └────┬─────┘
              │            │            │
              └────────────┼────────────┘
                           │
                     MySQL Service
                    (Single Master)
                           │
                           ▼
                    ┌─────────────┐
                    │   MySQL     │
                    │   Pod       │
                    │             │
                    │ Persistent  │
                    │ Volume      │
                    └─────────────┘

HPA Behavior:
┌─────────────────────────────────────────────────────────┐
│ Service      | Min | Max | Scale Up  | Scale Down      │
├─────────────────────────────────────────────────────────┤
│ Frontend     |  1  |  5  | CPU > 70% | CPU < 50% (5m)  │
│ Auth Service |  1  | 10  | CPU > 70% | CPU < 50% (5m)  │
│ Task Service |  1  | 10  | CPU > 70% | CPU < 50% (5m)  │
└─────────────────────────────────────────────────────────┘
```

---

## Monitoring & Observability Flow

```
┌────────────────────────────────────────────────────────────────┐
│                    MONITORING NAMESPACE                         │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐         ┌──────────────┐                    │
│  │ Prometheus   │◄────────│ServiceMonitor│                    │
│  │              │         │              │                    │
│  │ Scrapes:     │         │ Targets:     │                    │
│  │ - /metrics   │         │ - auth svc   │                    │
│  │   every 30s  │         │ - task svc   │                    │
│  └──────┬───────┘         │ - frontend   │                    │
│         │                 └──────────────┘                    │
│         │                                                      │
│         │ Stores metrics:                                     │
│         │ • http_requests_total                               │
│         │ • http_request_duration_seconds                     │
│         │ • process_cpu_seconds_total                         │
│         │ • nodejs_heap_size_used_bytes                       │
│         │                                                      │
│         ▼                                                      │
│  ┌──────────────┐                                             │
│  │  Grafana     │                                             │
│  │              │                                             │
│  │ Dashboards:  │                                             │
│  │ - Cluster    │                                             │
│  │ - Nodes      │                                             │
│  │ - Pods       │                                             │
│  │ - Services   │                                             │
│  └──────────────┘                                             │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## Complete End-to-End Example

**Scenario:** User "john" logs in and creates a task

```
Time    | Component           | Action
--------|--------------------|-----------------------------------------
T+0s    | User Browser       | Navigate to http://10.205.144.151/login
T+0.1s  | Ingress            | Route to Frontend Service
T+0.2s  | Frontend Pod       | Serve login.html
T+0.3s  | User Browser       | Render login page
        |                    |
T+10s   | User               | Enter username: john, password: MyP@ss123456
T+10.1s | Frontend JS        | Validate password strength locally
T+10.2s | User Browser       | POST /api/auth/login
T+10.3s | Ingress            | Route to Auth Service (10.x.x.x:8001)
T+10.4s | Auth Pod           | Check rate limit (5/15min) ✓
T+10.5s | Auth Pod           | Validate input (express-validator) ✓
T+10.6s | Auth Pod           | Query MySQL: SELECT * FROM users WHERE username='john'
T+10.7s | MySQL Pod          | Return user record {id:5, username:'john', password:'$2a$10...'}
T+10.8s | Auth Pod           | bcrypt.compare('MyP@ss123456', '$2a$10...') ✓
T+10.9s | Auth Pod           | jwt.sign({userId:5, exp:now+24h})
T+11.0s | Auth Pod           | Return {token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'}
T+11.1s | User Browser       | Store token in localStorage
T+11.2s | User Browser       | Navigate to /dashboard
        |                    |
T+20s   | User               | Click "Create Task"
T+20.1s | User               | Fill: title="Deploy to Prod", desc="...", priority="high"
T+20.2s | User Browser       | POST /api/tasks (with Authorization header)
T+20.3s | Ingress            | Route to Task Service (10.x.x.x:8002)
T+20.4s | Task Pod           | Check rate limit (20/min) ✓
T+20.5s | Task Pod           | Verify JWT token ✓
T+20.6s | Task Pod           | Extract userId=5 from token
T+20.7s | Task Pod           | Validate input (Pydantic) ✓
T+20.8s | Task Pod           | INSERT INTO tasks (user_id,title,description,priority,status)
        |                    | VALUES (5,'Deploy to Prod','...','high','pending')
T+20.9s | MySQL Pod          | Execute INSERT, return taskId=101
T+21.0s | Task Pod           | Return {message:"Task created", id:101}
T+21.1s | User Browser       | Update UI, show new task
        |                    |
T+21.2s | Prometheus         | Scrape metrics from all pods
T+21.3s | Grafana            | Update dashboards with latest data
```

---

## Summary

This architecture demonstrates:

1. **Zero-Trust Networking** - Network policies enforce explicit allow rules
2. **Defense in Depth** - Multiple security layers (network, ingress, application, database)
3. **Scalability** - HPA ensures pods scale based on load
4. **High Availability** - Multiple replicas with load balancing
5. **Observability** - Prometheus metrics and Grafana dashboards
6. **GitOps** - All infrastructure as code, managed via Flux CD
7. **Security** - Rate limiting, input validation, JWT authentication, bcrypt hashing
