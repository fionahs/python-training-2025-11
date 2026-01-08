# Rate Limiting Test Guide

## 🚦 Rate Limits Implemented

### Search Endpoint
- **Endpoint**: `POST /api/stores/search`
- **Limits**:
  - 10 requests per minute
  - 100 requests per hour
- **Response when exceeded**: HTTP 429 (Too Many Requests)

### Login Endpoint
- **Endpoint**: `POST /api/auth/login`
- **Limit**: 5 requests per minute (stricter to prevent brute force attacks)
- **Response when exceeded**: HTTP 429 (Too Many Requests)

### Bulk Import Endpoint
- **Endpoint**: `POST /api/admin/stores/import`
- **Limit**: 5 requests per hour (very strict for bulk operations)
- **Response when exceeded**: HTTP 429 (Too Many Requests)

---

## 🧪 How to Test in Postman

### Test 1: Search Rate Limit (10/minute)

1. Create a search request:
   ```
   POST http://localhost:8001/api/stores/search
   Body (JSON):
   {
     "latitude": 40.7128,
     "longitude": -74.0060,
     "radius_miles": 10
   }
   ```

2. **Click Send 11 times rapidly**

3. **Expected Results**:
   - First 10 requests: `200 OK` with store results
   - 11th request: `429 Too Many Requests` with message:
     ```json
     {
       "error": "Rate limit exceeded: 10 per 1 minute"
     }
     ```

4. **Response Headers** (on all requests):
   - `X-RateLimit-Limit`: 10
   - `X-RateLimit-Remaining`: (counts down from 10 to 0)
   - `X-RateLimit-Reset`: Unix timestamp when limit resets
   - `Retry-After`: Seconds to wait before retrying

5. Wait 1 minute and the limit will reset

---

### Test 2: Login Rate Limit (5/minute)

1. Create a login request:
   ```
   POST http://localhost:8001/api/auth/login
   Body (JSON):
   {
     "email": "admin@test.com",
     "password": "AdminTest123!"
   }
   ```

2. **Click Send 6 times rapidly**

3. **Expected Results**:
   - First 5 requests: `200 OK` with tokens
   - 6th request: `429 Too Many Requests`

---

### Test 3: Bulk Import Rate Limit (5/hour)

This is harder to test quickly, but:
1. Upload a CSV file 6 times within an hour
2. The 6th upload should be blocked with `429 Too Many Requests`

---

## 📊 Rate Limit Headers

Every response includes these headers:

```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1704312000
Retry-After: 43
```

- **X-RateLimit-Limit**: Maximum requests allowed
- **X-RateLimit-Remaining**: Requests left in this time window
- **X-RateLimit-Reset**: Unix timestamp when limit resets
- **Retry-After**: Seconds until you can try again

---

## 🔍 Why Rate Limiting?

### Security Benefits:
1. **Prevents Brute Force**: Login limited to 5/min prevents password guessing
2. **Prevents DoS**: Search limited to 10/min prevents server overload
3. **Resource Protection**: Bulk import limited to 5/hour prevents database abuse
4. **Fair Usage**: Ensures all users get access to the API

### Production Considerations:
- Rate limits are per IP address
- In production, you might want to:
  - Use Redis for distributed rate limiting across servers
  - Have different limits for authenticated vs public users
  - Implement API keys with custom rate limits per client
  - Whitelist certain IPs (e.g., your own services)

---

## 🛠 Implementation Details

**Library**: slowapi (FastAPI rate limiting extension)

**Key Features**:
- Automatic rate limit tracking per IP
- Clear error messages when exceeded
- Standard HTTP 429 status code
- Rate limit info in response headers
- Multiple limits can stack (e.g., 10/min AND 100/hour)

**Code Example**:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/search")
@limiter.limit("10/minute")
@limiter.limit("100/hour")
def search_stores(request: Request, ...):
    # Your endpoint logic
```

When both limits are applied, the stricter one wins (whichever is exceeded first).
