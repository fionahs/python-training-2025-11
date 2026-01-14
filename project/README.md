# Store Locator API 2nd Implementation

A high-performance, production-ready Store Locator service built with a modular **Pro Architecture** using FastAPI, PostgreSQL, and SQLAlchemy. This project is a complete re-implementation designed for maximum scalability, security, and verification.

---

## 🚀 Tech Stack & Design
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Asynchronous, Type-safe)
- **Database**: [PostgreSQL](https://www.postgresql.org/) with [SQLAlchemy 2.0](https://www.sqlalchemy.org/)
- **Geospatial**: [Geopy](https://geopy.readthedocs.io/) (Haversine Formula) & Bounding Box Optimization
- **Security**: [Jose](https://python-jose.readthedocs.io/) (JWT), [Bcrypt](https://pypi.org/project/bcrypt/) (Hashing), [SlowAPI](https://slowapi.readthedocs.io/) (Rate Limiting)
- **Caching**: Specialized In-memory cache with TTL (Redis-ready)

---

## 🛠️ Quick Start

### 1. Environment Setup
```bash
# Clone and enter the project directory
cd project

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your DATABASE_URL and SECRET_KEY
```

### 2. Database Initialization
```bash
# Create schema, seed roles/permissions, create test users, and load initial stores
python init_db.py
```

### 3. Run the FastAPI Service
```bash
uvicorn app.main:app --reload
```
The API will be live at `http://localhost:8000`. Explore interactive docs at `/docs`.

---

## 🧪 Verification Strategy (The Postman Playbook)

This strategy ensures that 100% of the requirements in `project_description.md` are met. We prioritize **Postman** for end-to-end functional validation.

### Phase 1: Authentication & RBAC Security
*Test security boundaries and token management.*

1. **Admin Login** (`POST /api/auth/login`)
    - *Requirement*: JWT 2-Token Pattern.
    - **Request JSON**:
      ```json
      {
        "email": "admin@test.com",
        "password": "AdminTest123!"
      }
      ```

2. **Verify Identity** (`GET /api/auth/me`)
    - *Requirement*: JWT Authentication.
    - *Note*: Use `Authorization: Bearer <access_token>` header.

3. **Viewer Role Check** (`PATCH /api/stores/S0001`)
    - *Requirement*: RBAC Isolation.
    - *Note*: Login as `viewer@test.com` first, then try to modify a store.
    - **Request JSON**:
      ```json
      {
        "name": "Updated Store Name"
      }
      ```
    - *Expected*: `403 Forbidden` ("Permission denied").

4. **Token Refresh** (`POST /api/auth/refresh`)
    - *Requirement*: 7-Day Refresh Link.
    - **Request JSON**:
      ```json
      {
        "refresh_token": "YOUR_REFRESH_TOKEN_HERE"
      }
      ```
    - *Expert Note*: Uncheck the Authorization header in Postman because if you have the refresh token, you should be able to get a new session even if your access token is already expired or missing.

5. **Logout Revocation** (`POST /api/auth/logout`)
    - *Requirement*: Token Revocation.

### Phase 2: Public Store Search (Public)
*Test as an unauthenticated user.*

1. **Geocode Search** (`POST /api/stores/search`)
    - *Requirement*: Search by full address.
    - **Request JSON**:
      ```json
      {
        "address": "100 Cambridge St, Boston, MA",
        "radius_miles": 10
      }
      ```

2. **ZIP Code Search** (`POST /api/stores/search`)
    - *Requirement*: Search by postal code.
    - **Request JSON**:
      ```json
      {
        "postal_code": "02114",
        "radius_miles": 5
      }
      ```

3. **Coordinate Search** (`POST /api/stores/search`)
    - *Requirement*: Search by Lat/Lon.
    - **Request JSON**:
      ```json
      {
        "latitude": 42.3555,
        "longitude": -71.0602,
        "radius_miles": 5
      }
      ```

4. **Advanced Filters (AND Logic for Services)** (`POST /api/stores/search`)
    - *Requirement*: `services[]` (AND) - Store must have ALL listed services.
    - **Request JSON**:
      ```json
      {
        "address": "Chicago, IL",
        "radius_miles": 50,
        "services": ["pharmacy"] // AND: Checks for 'pharmacy'. Try adding 'bakery' to refine.
      }
      ```

5. ** Store search with OR logic** (`POST /api/stores/search`)
    - **Request JSON**:
      ```json
      {
        "address": "San Francisco, CA",
        "radius_miles": 50,
        "store_types": ["flagship", "outlet"]
      }
      ```

6. **Cache Stats** (`GET /cache/stats`)
    - *Requirement*: Cache hit/miss ratio.
    - *Note*: Check `GET /cache/stats`.
This project used in-memory caching.

### Phase 3: Internal CRUD & Batch Import
*Test as Admin or Marketer.*

1. **Create Store** (`POST /api/stores/`)
    - *Requirement*: Auto-geocode if coordinates missing.
    - **Request JSON**:
      ```json
      {
        "store_id": "S9999",
        "name": "New Terminal Store",
        "store_type": "regular",
        "status": "active",
        "address_street": "123 Main St",
        "address_city": "New York",
        "address_state": "NY",
        "address_postal_code": "10001",
        "phone": "212-555-1234",
        "services": ["pharmacy", "pickup"]
      }
      ```

2. **Partial Update (PATCH)** (`PATCH /api/stores/S9999`)
    - *Requirement*: Support PATCH method for partial updates.
    - **Request JSON**:
      ```json
      {
        "phone": "212-555-9999",
        "services": ["pharmacy", "pickup", "returns"]
      }
      ```

3. **Soft Delete** (`DELETE /api/stores/S9999`)
    - *Requirement*: Deactivate store (soft delete). Soft delete means the store will remain in the DB but be marked status: inactive.


4. **Bulk CSV Upsert** (`POST /api/admin/stores/import`)
    - *Requirement*: Upsert stores from CSV with validation.
    - *Note*: Select `form-data` in Postman, key `file`, choose `stores_1000.csv`.


### Phase 4: Production Hardening
- **Rate Limiting**: Rapidly hit `/api/stores/search` 15 times.
    - *Verify*: HTTP `429 Too Many Requests` triggered.
- **Caching**: Check `GET /cache/stats`.
    - *Verify*: Hit/Miss ratio reflects search efficiency.


### Phase 5: User Management (Admin Only)
*Test as Admin (admin@test.com).*

1.  **List Users** (`GET /api/admin/users`)
    - *Requirement*: List all registered users.
    - *Note*: Use this to find the `role_id` (usually 1=Admin, 2=Marketer, 3=Viewer).

2.  **Create User** (`POST /api/admin/users`)
    - *Requirement*: Create a new staff member.
    - **Request JSON**:
      ```json
      {
        "email": "new.staff@test.com",
        "full_name": "New Staff Member",
        "password": "SecurePassword123!",
        "role_id": 2
      }
      ```

3.  **Update User** (`PUT /api/admin/users/{user_id}`)
    - *Requirement*: Change role or status.
    - **Request JSON**:
      ```json
      {
        "full_name": "Promoted Staff Member",
        "role_id": 1
      }
      ```

4.  **Deactivate User** (`DELETE /api/admin/users/{user_id}`)
    - *Requirement*: Soft delete (status=inactive).

---

## 🏗️ Architecture Insight

### Distance Calculation (Pro Method)
Following Requirement 1.4, we implement a **Double-Layer Filter**:
1. **Database Layer (SQL)**: Uses a calculated Bounding Box to prune the stores list by 90%+ using indexes.
2. **Logic Layer (Python)**: Uses the **Haversine Formula** (via Geopy) to calculate millisecond-accurate distances for the remaining candidates.

### Modular File Map
- `/app/routers`: Logic-free API definitions.
- `/app/utils`: High-math and high-security utility functions.
- `/app/dependencies`: Reusable RBAC and Database injectors.
- `/app/schemas`: Rigid Pydantic models for strict I/O validation.

---

## 🔑 Test Users Reference
| Role | Email | Password |
| :--- | :--- | :--- |
| **Admin** | `admin@test.com` | `AdminTest123!` |
| **Marketer** | `marketer@test.com` | `MarketerTest123!` |
| **Viewer** | `viewer@test.com` | `ViewerTest123!` |
