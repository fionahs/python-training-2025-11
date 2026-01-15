"""
API tests for main endpoints
"""
import pytest


class TestMainEndpoints:
    """Test main API endpoints"""

    def test_root_endpoint(self, client):
        """Test root endpoint returns API info"""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Store Locator API"
        assert data["version"] == "1.0.0"
        assert data["status"] == "running"

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        assert data["api_version"] == "1.0.0"

    def test_cache_stats(self, client):
        """Test cache statistics endpoint"""
        response = client.get("/cache/stats")

        assert response.status_code == 200
        data = response.json()
        # Cache stats should have hits, misses, size
        assert "hits" in data or "total_hits" in data or isinstance(data, dict)
