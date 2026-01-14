"""
Unit tests for utility functions
"""
import pytest
from app.utils.distance import calculate_bounding_box, calculate_distance, is_store_open_now
from app.utils.auth import get_password_hash, verify_password
from datetime import datetime


class TestDistanceUtils:
    """Test distance calculation utilities"""

    def test_calculate_bounding_box(self):
        """Test bounding box calculation"""
        bbox = calculate_bounding_box(40.7128, -74.0060, 10)

        assert "min_lat" in bbox
        assert "max_lat" in bbox
        assert "min_lon" in bbox
        assert "max_lon" in bbox

        # Check that bounding box is symmetric around center
        assert abs((bbox["max_lat"] - bbox["min_lat"]) / 2 - (40.7128 - bbox["min_lat"])) < 0.01

    def test_calculate_distance(self):
        """Test Haversine distance calculation"""
        # Distance from NYC to Philadelphia (approx 80 miles)
        nyc_lat, nyc_lon = 40.7128, -74.0060
        philly_lat, philly_lon = 39.9526, -75.1652

        distance = calculate_distance(nyc_lat, nyc_lon, philly_lat, philly_lon)

        # Should be approximately 80 miles
        assert 75 < distance < 85

    def test_calculate_distance_same_point(self):
        """Test distance between same point is zero"""
        distance = calculate_distance(40.7128, -74.0060, 40.7128, -74.0060)
        assert distance < 0.01  # Essentially zero


class TestAuthUtils:
    """Test authentication utilities"""

    def test_password_hashing(self):
        """Test password hashing"""
        password = "TestPassword123!"
        hashed = get_password_hash(password)

        # Hash should be different from original
        assert hashed != password

        # Should be able to verify
        assert verify_password(password, hashed) is True

    def test_password_verification_fails(self):
        """Test wrong password fails verification"""
        password = "TestPassword123!"
        hashed = get_password_hash(password)

        assert verify_password("WrongPassword", hashed) is False

    def test_different_hashes_for_same_password(self):
        """Test that same password produces different hashes (due to salt)"""
        password = "TestPassword123!"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        assert hash1 != hash2
        # But both should verify
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True
