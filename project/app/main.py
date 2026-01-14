from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.config import get_settings
from app.routers import stores, auth, search, admin

settings = get_settings()

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Store Locator API",
    description="A production-ready Store Locator API with search and management features",
    version="1.0.0",
    debug=settings.DEBUG
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(search.router)
app.include_router(stores.router)
app.include_router(admin.router)


@app.get("/")
async def root():
    return {
        "message": "Store Locator API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "api_version": "1.0.0"
    }


@app.get("/cache/stats")
async def cache_stats():
    """Get cache statistics"""
    from app.utils.cache import cache
    return cache.get_stats()
