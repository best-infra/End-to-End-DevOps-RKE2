const express = require('express')
const bcrypt = require('bcryptjs')
const jwt = require('jsonwebtoken')
const mysql = require('mysql2/promise')
const cors = require('cors')
const helmet = require('helmet')
const rateLimit = require('express-rate-limit')
const { body, validationResult } = require('express-validator')
const cookieParser = require('cookie-parser')
require('dotenv').config()

const app = express()
const PORT = process.env.PORT || 8001

// Trust proxy - required for rate limiting behind ingress/nginx
app.set('trust proxy', 1)

// CI/CD Pipeline Full Test - January 2026 v1.0.0 // // 
// This service now includes automated builds and security scanning
// Testing multi-service deployment

// Security headers
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", 'data:', 'https:'],
    },
  },
  hsts: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true
  }
}))

// Rate limiting
const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // 5 attempts per window
  message: 'Too many login attempts, please try again later',
  standardHeaders: true,
  legacyHeaders: false,
})

const registerLimiter = rateLimit({
  windowMs: 60 * 60 * 1000, // 1 hour
  max: 3, // 3 registrations per hour per IP
  message: 'Too many accounts created, please try again later',
  standardHeaders: true,
  legacyHeaders: false,
})

const generalLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // 100 requests per window
  standardHeaders: true,
  legacyHeaders: false,
})

// Apply general rate limiter to all routes
app.use(generalLimiter)

// Enhanced CORS configuration - restrict to specific origins in production
const allowedOrigins = process.env.ALLOWED_ORIGINS 
  ? process.env.ALLOWED_ORIGINS.split(',') 
  : ['http://localhost:5173', 'http://localhost:3000']

app.use(cors({
  credentials: true,
  origin: (origin, callback) => {
    // Allow requests with no origin (like mobile apps or curl requests)
    if (!origin) return callback(null, true)
    
    if (allowedOrigins.indexOf(origin) !== -1 || process.env.NODE_ENV === 'development') {
      callback(null, true)
    } else {
      callback(new Error('Not allowed by CORS'))
    }
  },
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
}))
app.use(express.json({ limit: '10mb' }))
app.use(cookieParser())

// Logging middleware
app.use((req, res, next) => {
  // Don't log sensitive data in production
  if (process.env.NODE_ENV !== 'production') {
    console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`)
  }
  next()
})

// Database connection pool
const pool = mysql.createPool({
  host: process.env.DB_HOST || 'mysql',
  user: process.env.DB_USER || 'root',
  password: process.env.DB_PASS || 'password',
  database: process.env.DB_NAME || 'task_manager',
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0
})

// Validation middleware
const validateUsername = body('username')
  .trim()
  .isLength({ min: 3, max: 30 })
  .withMessage('Username must be between 3 and 30 characters')
  .matches(/^[a-zA-Z0-9_-]+$/)
  .withMessage('Username can only contain letters, numbers, underscores, and hyphens')

const validatePassword = body('password')
  .isLength({ min: 12 })
  .withMessage('Password must be at least 12 characters')
  .matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/)
  .withMessage('Password must contain uppercase, lowercase, number, and special character')

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'auth-service' })
})

// Register endpoint
app.post('/api/auth/register', 
  registerLimiter,
  validateUsername,
  validatePassword,
  async (req, res) => {
    // Validate input
    const errors = validationResult(req)
    if (!errors.isEmpty()) {
      return res.status(400).json({ error: errors.array()[0].msg })
    }

    const { username, password } = req.body

    try {
      const hashedPassword = await bcrypt.hash(password, 10)
      
      const [result] = await pool.execute(
        'INSERT INTO users (username, password) VALUES (?, ?)',
        [username, hashedPassword]
      )

      res.status(201).json({ message: 'User registered successfully', userId: result.insertId })
    } catch (error) {
      if (error.code === 'ER_DUP_ENTRY') {
        return res.status(409).json({ error: 'Username already exists' })
      }
      console.error('Registration error:', error.message)
      res.status(500).json({ error: 'Registration failed' })
    }
  }
)

// Login endpoint
app.post('/api/auth/login', 
  loginLimiter,
  body('username').trim().notEmpty(),
  body('password').notEmpty(),
  async (req, res) => {
    // Validate input
    const errors = validationResult(req)
    if (!errors.isEmpty()) {
      return res.status(400).json({ error: 'Username and password required' })
    }

    const { username, password } = req.body

    try {
      const [users] = await pool.execute(
        'SELECT * FROM users WHERE username = ?',
        [username]
      )

      // Use constant-time comparison to prevent timing attacks
      const user = users[0]
      const isValidPassword = user ? await bcrypt.compare(password, user.password) : false

      // Generic error message to prevent username enumeration
      if (!user || !isValidPassword) {
        return res.status(401).json({ error: 'Invalid credentials' })
      }

      // Ensure JWT_SECRET is set
      if (!process.env.JWT_SECRET) {
        console.error('CRITICAL: JWT_SECRET not set')
        return res.status(500).json({ error: 'Server configuration error' })
      }

      const token = jwt.sign(
        { userId: user.id, username: user.username },
        process.env.JWT_SECRET,
        { expiresIn: '24h' }
      )

      res.json({ token, userId: user.id, username: user.username })
    } catch (error) {
      console.error('Login error:', error.message)
      res.status(500).json({ error: 'Login failed' })
    }
  }
)

// Verify token endpoint
app.post('/api/auth/verify', async (req, res) => {
  const token = req.headers.authorization?.split(' ')[1]

  if (!token) {
    return res.status(401).json({ error: 'No token provided' })
  }

  try {
    if (!process.env.JWT_SECRET) {
      console.error('CRITICAL: JWT_SECRET not set')
      return res.status(500).json({ error: 'Server configuration error' })
    }
    
    const decoded = jwt.verify(token, process.env.JWT_SECRET)
    res.json({ valid: true, userId: decoded.userId, username: decoded.username })
  } catch (error) {
    res.status(401).json({ error: 'Invalid token' })
  }
})

// Get user profile
app.get('/api/auth/profile', async (req, res) => {
  const token = req.headers.authorization?.split(' ')[1]

  if (!token) {
    return res.status(401).json({ error: 'No token provided' })
  }

  try {
    if (!process.env.JWT_SECRET) {
      console.error('CRITICAL: JWT_SECRET not set')
      return res.status(500).json({ error: 'Server configuration error' })
    }
    
    const decoded = jwt.verify(token, process.env.JWT_SECRET)
    
    const [users] = await pool.execute(
      'SELECT id, username, created_at FROM users WHERE id = ?',
      [decoded.userId]
    )

    if (users.length === 0) {
      return res.status(404).json({ error: 'User not found' })
    }

    res.json(users[0])
  } catch (error) {
    console.error('Profile fetch error:', error.message)
    res.status(500).json({ error: 'Failed to fetch profile' })
  }
})

// Error handling middleware
app.use((err, req, res, next) => {
  // Don't leak error details in production
  if (process.env.NODE_ENV === 'production') {
    console.error('Unhandled error:', err.message)
    res.status(500).json({ error: 'Internal server error' })
  } else {
    console.error('Unhandled error:', err)
    res.status(500).json({ error: 'Internal server error', details: err.message })
  }
})

app.listen(PORT, () => {
  console.log(`Auth service running on port ${PORT}`)
  console.log(`Database: ${process.env.DB_HOST || 'mysql'}/${process.env.DB_NAME || 'task_manager'}`)
})
