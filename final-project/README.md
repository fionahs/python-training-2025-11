# Store Locator API - Final Project

A production-ready Store Locator API built with FastAPI, PostgreSQL, and JWT authentication.

## Features Implemented

### ✅ Core Functionality
- **Store CRUD Operations** - Create, Read, Update (PATCH), Delete stores
- **JWT Authentication** - Login, refresh, logout with 2-token pattern
- **Role-Based Access Control (RBAC)** - Admin, Marketer, Viewer roles with permissions
- **Store Search** - Search by coordinates, address, or postal code with distance calculation
- **Distance Calculation** - Bounding box pre-filter + Haversine formula
- **Password Hashing** - Secure bcrypt hashing
- **Bulk CSV Import** - Upsert stores from CSV with validation and geocoding
- **Rate Limiting** - 100/hour, 10/minute per IP on search endpoints
- **Caching** - In-memory cache for geocoding (30 days) and search results (5 minutes)
- **User Management** - Full CRUD for users (Admin only)

### 🗄️ Database
- PostgreSQL with SQLAlchemy ORM
- 7 tables: stores, users, roles, permissions, role_permissions, refresh_tokens, store_services
- 50 sample stores loaded from CSV
- 3 test users with different roles

### 🔐 Security
- JWT token authentication (Access: 15min, Refresh: 7 days)
- Permission-based authorization
- Password hashing with bcrypt
- Refresh token revocation

---

## Tech Stack

- **Framework**: FastAPI 0.115.5
- **Database**: PostgreSQL (Docker)
- **ORM**: SQLAlchemy 2.0.36
- **Authentication**: PyJWT + python-jose
- **Password Hashing**: bcrypt
- **Distance Calc**: geopy
- **Rate Limiting**: slowapi
- **Testing**: pytest with 77% coverage

---

## Setup Instructions

### 1. Prerequisites
- Python 3.10+
- PostgreSQL (Docker recommended)
- Virtual environment

### 2. Database Setup

Start PostgreSQL with Docker:
```bash
docker start my-postgres
```

Create database:
```bash
docker exec my-postgres psql -U postgres -c "CREATE DATABASE store_locator;"
```

### 3. Install Dependencies

```bash
# Activate virtual environment
source .venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### 4. Environment Configuration

Create `.env` file (or copy from `.env.example`):
```bash
DATABASE_URL=postgresql://postgres:mypassword@localhost:5432/store_locator
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 5. Initialize Database

```bash
python init_db.py
```

This will:
- Create all tables
- Seed roles and permissions
- Create 3 test users
- Load 50 stores from CSV

### 6. Run the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

Server will be running at: `http://localhost:8001`

---

## API Endpoints

### Authentication
- `POST /api/auth/login` - Login (get access & refresh tokens)
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - Logout (revoke refresh token)
- `GET /api/auth/me` - Get current user info

### Stores (Authenticated)
- `GET /api/stores/` - List all stores (requires auth)
- `GET /api/stores/{id}` - Get single store
- `POST /api/stores/` - Create store (Admin/Marketer only)
- `PATCH /api/stores/{id}` - Update store (Admin/Marketer only)
- `DELETE /api/stores/{id}` - Soft delete store (Admin/Marketer only)

### Store Search (Public)
- `POST /api/stores/search` - Search nearby stores (rate limited: 10/min, 100/hour)

### Admin (Admin Only)
- `POST /api/admin/stores/import` - Bulk import stores from CSV (rate limited: 5/hour)
- `POST /api/admin/users` - Create new user
- `GET /api/admin/users` - List all users (paginated)
- `GET /api/admin/users/{id}` - Get single user
- `PUT /api/admin/users/{id}` - Update user (role/status)
- `DELETE /api/admin/users/{id}` - Deactivate user (soft delete)

### Monitoring
- `GET /` - API info
- `GET /health` - Health check
- `GET /cache/stats` - Cache statistics

### Documentation
- `GET /docs` - Swagger UI (interactive API documentation)
- `GET /redoc` - ReDoc documentation

---

## Test Users

| Email | Password | Role | Permissions |
|-------|----------|------|-------------|
| admin@test.com | AdminTest123! | Admin | Full access |
| marketer@test.com | MarketerTest123! | Marketer | Manage stores |
| viewer@test.com | ViewerTest123! | Viewer | Read-only |

---

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_auth.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

### Test Coverage

The test suite includes:
- **Unit Tests** - Distance calculation, password hashing, utilities
- **API Tests** - Authentication, Store CRUD, RBAC, Search
- **Integration Tests** - End-to-end workflows, CSV import

Current coverage: **77%** of core business logic

Generate coverage report:
```bash
# Terminal report
pytest tests/ --cov=app --cov-report=term

# HTML report (opens in browser)
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```

---

## Example API Requests

### 1. Login
```bash
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@test.com", "password": "AdminTest123!"}'
```

### 2. Get All Stores (Authenticated)
```bash
curl -X GET http://localhost:8001/api/stores/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 3. Search Stores by Coordinates
```bash
curl -X POST http://localhost:8001/api/stores/search \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 28.5813,
    "longitude": -81.3862,
    "radius_miles": 50
  }'
```

### 4. Create Store (Marketer/Admin)
```bash
curl -X POST http://localhost:8001/api/stores/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "store_id": "S9999",
    "name": "New Store",
    "store_type": "regular",
    "status": "active",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "address_street": "123 Main St",
    "address_city": "New York",
    "address_state": "NY",
    "address_postal_code": "10001",
    "phone": "212-555-1234",
    "services": ["pharmacy", "pickup"]
  }'
```

### 5. Bulk Import Stores (Admin Only)
```bash
curl -X POST http://localhost:8001/api/admin/stores/import \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -F "file=@sample_import.csv"
```

### 6. Search Stores by Address
```bash
curl -X POST http://localhost:8001/api/stores/search \
  -H "Content-Type: application/json" \
  -d '{
    "address": "123 Main St, Orlando, FL",
    "radius_miles": 25,
    "services": ["pharmacy"],
    "open_now": true
  }'
```

---

## Architecture

### Distance Calculation Method

Uses **Bounding Box + Haversine Formula** approach:

1. **Calculate Bounding Box** - Quick pre-filter using lat/lon ranges
2. **SQL Filter** - `WHERE latitude BETWEEN ... AND longitude BETWEEN ...`
3. **Exact Distance** - Haversine formula via geopy for filtered stores
4. **Sort & Filter** - Return results within radius, sorted by distance

This is more efficient than calculating distance for every store in the database.

### Authentication Flow

1. User logs in with email/password
2. Server validates credentials
3. Server generates access token (15min) + refresh token (7 days)
4. Client stores tokens
5. Client sends access token with each request
6. When access token expires, use refresh token to get new access token
7. On logout, refresh token is revoked

### RBAC Implementation

- **Admin**: Full access to all endpoints
- **Marketer**: Can manage stores (create, update, delete) but not users
- **Viewer**: Read-only access to stores

Implemented via:
- `roles` table - Defines roles
- `permissions` table - Defines permissions
- `role_permissions` junction table - Maps roles to permissions
- `require_permission()` dependency - Checks user permissions before endpoint access

---

## Project Structure

```
final-project/
├── app/
│   ├── main.py              # FastAPI app
│   ├── config.py            # Configuration
│   ├── database.py          # Database connection
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── dependencies.py      # Auth dependencies
│   ├── routers/
│   │   ├── auth.py          # Auth endpoints
│   │   ├── stores.py        # Store CRUD
│   │   └── search.py        # Store search
│   └── utils/
│       ├── auth.py          # Password hashing
│       ├── jwt.py           # JWT utilities
│       ├── distance.py      # Distance calculations
│       └── geocoding.py     # Geocoding utilities
├── tests/
│   ├── conftest.py          # Test fixtures
│   ├── test_auth.py         # Auth tests
│   ├── test_stores.py       # Store CRUD & RBAC tests
│   └── test_utils.py        # Unit tests
├── init_db.py               # Database initialization
├── requirements.txt         # Dependencies
├── .env                     # Environment variables
└── README.md                # This file
```

---

---

## Deployment to Render

### Required Files (Already Created)

- ✅ `Procfile` - Tells Render how to start the app
- ✅ `runtime.txt` - Python version (3.11.0)
- ✅ `requirements.txt` - Dependencies
- ✅ `.env.example` - Environment variables template

### Step 1: Prepare Your Code

**If you don't have write access to the repository (e.g., it's someone else's repo):**
1. Fork the repository on GitHub (click "Fork" button)
2. Update your local remote to point to your fork:
   ```bash
   git remote set-url origin https://github.com/YOUR_USERNAME/python-training-2025-11.git
   ```

**Commit and push your code:**
```bash
cd final-project
git add .
git commit -m "Complete Store Locator API - ready for deployment

- All 19 requirements implemented
- Caching (geocoding + search results)
- User management endpoints
- Rate limiting
- Bulk CSV import
- 77% test coverage
- Deployment files (Procfile, runtime.txt)
- Complete documentation in README"

git push origin main
```

### Step 2: Create PostgreSQL Database

1. **Sign up/Login** at [render.com](https://render.com)
2. Click **"New +"** → **"PostgreSQL"**
3. Fill in:
   - **Name**: `store-locator-db`
   - **Database**: `store_locator`
   - **Region**: Oregon (US West) or closest to you
   - **PostgreSQL Version**: 15
   - **Plan**: Free
4. Click **"Create Database"**
5. ⚠️ **IMPORTANT**: Copy the **Internal Database URL** from the database info page
   - Format: `postgresql://user:password@hostname/database`
   - You'll need this in Step 4

### Step 3: Create Web Service

1. Click **"New +"** → **"Web Service"**
2. **Connect GitHub repository**:
   - Click "Connect a repository"
   - Authorize Render to access your GitHub
   - Select your repository
3. Configure the service:
   - **Name**: `store-locator-api` (or your choice)
   - **Region**: Same as database (Oregon US West)
   - **Branch**: `main`
   - **Root Directory**: Leave blank (or `final-project` if repo root is different)
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: Free

### Step 4: Add Environment Variables

In the web service settings, scroll to **"Environment Variables"** and add:

| Key | Value |
|-----|-------|
| `DATABASE_URL` | Paste Internal URL from Step 2 |
| `SECRET_KEY` | Generate below ⬇️ |
| `ALGORITHM` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `15` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` |
| `GEOCODING_USER_AGENT` | `store-locator-app` |
| `DEBUG` | `False` |

**Generate SECRET_KEY** (run locally):
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 5: Deploy

1. Click **"Create Web Service"**
2. Render will automatically:
   - Clone your repo
   - Install dependencies
   - Start your FastAPI app
3. **Wait 3-5 minutes** for build to complete
4. Look for **"Your service is live 🎉"** message

### Step 6: Initialize Database

After deployment succeeds:

1. Go to your web service in Render dashboard
2. Click **"Shell"** tab (top right)
3. Run this command:
   ```bash
   python init_db.py
   ```

This will:
- Create all 7 database tables
- Seed roles (Admin, Marketer, Viewer) and permissions
- Create 3 test users
- Load 50 sample stores from CSV

### Step 7: Test Your Live API

Your API is now live at: `https://your-app-name.onrender.com`

**Test health endpoint:**
```bash
curl https://your-app-name.onrender.com/health
```

**Test login:**
```bash
curl -X POST https://your-app-name.onrender.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@test.com", "password": "AdminTest123!"}'
```

**Visit interactive API docs:**
```
https://your-app-name.onrender.com/docs
```

### Post-Deployment Checklist

- [ ] Health endpoint returns `{"status": "healthy"}`
- [ ] Login works and returns tokens
- [ ] Store search endpoint works
- [ ] Swagger UI docs accessible at `/docs`
- [ ] Database has 50 stores and 3 users
- [ ] Rate limiting works (try 15+ search requests quickly)
- [ ] All RBAC permissions work correctly

### Important Notes

**Free Tier Limitations:**
- Service sleeps after 15 minutes of inactivity
- 30-second cold start when waking up
- 512 MB RAM, limited CPU
- Database storage limited to 1 GB

**Automatic Deployments:**
- Render auto-deploys when you push to GitHub
- Each push to `main` branch triggers a new deployment

**View Logs:**
- Click "Logs" tab in Render dashboard
- Real-time logs show all API requests and errors

### Troubleshooting

| Issue | Solution |
|-------|----------|
| Build fails | Check `Procfile` exists, verify `requirements.txt` complete |
| Database connection error | Use **Internal** Database URL (not External) |
| 404 on all endpoints | Check logs for startup errors, verify `app/main.py` path |
| Service sleeps | Normal on free tier, first request wakes it up |
| Slow response | Free tier has limited resources, upgrade for better performance |

### Production Improvements (Optional)

For production use, consider:
1. **Upgrade to paid tier** ($7/month) for always-on service
2. **Update CORS** in `app/main.py` - change `allow_origins=["*"]` to specific domains
3. **Change test user passwords** or remove them
4. **Enable database backups** (automatic on paid tier)
5. **Add Redis** for persistent caching
6. **Monitor uptime** with UptimeRobot or similar

---

## Author

Built as a final project for Python training program.

**Framework Choice**: FastAPI
**CSV Processing**: Python built-in `csv` module
**Database**: PostgreSQL with SQLAlchemy ORM
