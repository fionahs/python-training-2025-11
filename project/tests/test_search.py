"""
API tests for store search endpoints
"""
import pytest


class TestStoreSearch:
    """Test store search functionality"""

    def test_search_by_coordinates(self, client, test_store):
        """Test searching stores by coordinates"""
        # Search near the test store (40.7128, -74.0060)
        response = client.post("/api/stores/search", json={
            "latitude": 40.7128,
            "longitude": -74.0060,
            "radius_miles": 10
        })

        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "search_location" in data
        assert "total_results" in data
        assert data["search_location"]["type"] == "coordinates"
        assert data["search_location"]["latitude"] == 40.7128
        assert data["search_location"]["longitude"] == -74.0060

    def test_search_with_no_results(self, client, test_store):
        """Test search that returns no results"""
        # Search far away from test store (Tokyo, Japan - far from NYC)
        response = client.post("/api/stores/search", json={
            "latitude": 35.6762,
            "longitude": 139.6503,
            "radius_miles": 1
        })

        assert response.status_code == 200
        data = response.json()
        assert data["total_results"] == 0
        assert len(data["results"]) == 0

    def test_search_missing_coordinates(self, client):
        """Test search without required coordinates"""
        response = client.post("/api/stores/search", json={
            "radius_miles": 10
        })

        assert response.status_code == 422
        # 422 is validation error from Pydantic model_validator

    def test_search_with_filters(self, client, test_store):
        """Test search with service filters"""
        response = client.post("/api/stores/search", json={
            "latitude": 40.7128,
            "longitude": -74.0060,
            "radius_miles": 10,
            "services": ["pharmacy"]
        })

        assert response.status_code == 200
        data = response.json()
        assert "filters_applied" in data
        assert "pharmacy" in data["filters_applied"]["services"]
