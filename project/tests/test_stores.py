"""
API tests for store endpoints with RBAC
"""
import pytest


class TestStoreEndpoints:
    """Test store CRUD endpoints"""

    def test_get_all_stores_with_auth(self, client, admin_token, test_store):
        """Test getting all stores with authentication"""
        response = client.get(
            "/api/stores/",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["store_id"] == "S0001"

    def test_get_all_stores_without_auth(self, client, test_store):
        """Test that getting stores requires authentication"""
        response = client.get("/api/stores/")

        assert response.status_code == 403

    def test_get_single_store(self, client, admin_token, test_store):
        """Test getting a single store"""
        response = client.get(
            "/api/stores/S0001",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["store_id"] == "S0001"
        assert data["name"] == "Test Store"
        assert "pharmacy" in data["services"]

    def test_get_nonexistent_store(self, client, admin_token):
        """Test getting a non-existent store"""
        response = client.get(
            "/api/stores/S9999",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 404

    def test_create_store_as_marketer(self, client, marketer_token):
        """Test that marketer can create stores"""
        new_store = {
            "store_id": "S0002",
            "name": "New Test Store",
            "store_type": "regular",
            "status": "active",
            "latitude": 40.7580,
            "longitude": -73.9855,
            "address_street": "456 Another St",
            "address_city": "New York",
            "address_state": "NY",
            "address_postal_code": "10002",
            "phone": "212-555-5678",
            "services": ["pickup", "returns"]
        }

        response = client.post(
            "/api/stores/",
            json=new_store,
            headers={"Authorization": f"Bearer {marketer_token}"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["store_id"] == "S0002"
        assert data["name"] == "New Test Store"

    def test_create_store_as_viewer_forbidden(self, client, viewer_token):
        """Test that viewer cannot create stores"""
        new_store = {
            "store_id": "S0003",
            "name": "Forbidden Store",
            "store_type": "regular",
            "status": "active",
            "latitude": 40.7580,
            "longitude": -73.9855,
            "address_street": "789 Forbidden St",
            "address_city": "New York",
            "address_state": "NY",
            "address_postal_code": "10003",
            "phone": "212-555-9999",
            "services": []
        }

        response = client.post(
            "/api/stores/",
            json=new_store,
            headers={"Authorization": f"Bearer {viewer_token}"}
        )

        assert response.status_code == 403
        assert "Permission denied" in response.json()["detail"]

    def test_update_store_partial(self, client, marketer_token, test_store):
        """Test partial update (PATCH) of store"""
        update_data = {
            "name": "Updated Store Name",
            "phone": "212-555-0000"
        }

        response = client.patch(
            "/api/stores/S0001",
            json=update_data,
            headers={"Authorization": f"Bearer {marketer_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Store Name"
        assert data["phone"] == "212-555-0000"
        # Other fields should remain unchanged
        assert data["address_city"] == "New York"

    def test_update_store_as_viewer_forbidden(self, client, viewer_token, test_store):
        """Test that viewer cannot update stores"""
        response = client.patch(
            "/api/stores/S0001",
            json={"name": "Should Not Update"},
            headers={"Authorization": f"Bearer {viewer_token}"}
        )

        assert response.status_code == 403

    def test_update_nonexistent_store(self, client, marketer_token):
        """Test updating a non-existent store returns 404"""
        response = client.patch(
            "/api/stores/S9999",
            json={"name": "Does Not Exist"},
            headers={"Authorization": f"Bearer {marketer_token}"}
        )

        assert response.status_code == 404

    def test_delete_store_soft_delete(self, client, marketer_token, test_store):
        """Test soft delete of store"""
        response = client.delete(
            "/api/stores/S0001",
            headers={"Authorization": f"Bearer {marketer_token}"}
        )

        assert response.status_code == 204

    def test_delete_store_as_viewer_forbidden(self, client, viewer_token, test_store):
        """Test that viewer cannot delete stores"""
        response = client.delete(
            "/api/stores/S0001",
            headers={"Authorization": f"Bearer {viewer_token}"}
        )

        assert response.status_code == 403


class TestRBACPermissions:
    """Test Role-Based Access Control"""

    def test_admin_has_all_permissions(self, client, admin_token, test_store):
        """Test that admin can perform all operations"""
        # Read
        response = client.get(
            "/api/stores/",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200

        # Create
        new_store = {
            "store_id": "S9999",
            "name": "Admin Store",
            "store_type": "flagship",
            "status": "active",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "address_street": "100 Admin St",
            "address_city": "New York",
            "address_state": "NY",
            "address_postal_code": "10001",
            "phone": "212-555-1111",
            "services": []
        }
        response = client.post(
            "/api/stores/",
            json=new_store,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 201

    def test_viewer_can_only_read(self, client, viewer_token, test_store):
        """Test that viewer can only read, not write or delete"""
        # Read - should work
        response = client.get(
            "/api/stores/",
            headers={"Authorization": f"Bearer {viewer_token}"}
        )
        assert response.status_code == 200

        # Create - should fail
        new_store = {
            "store_id": "S8888",
            "name": "Viewer Store",
            "store_type": "regular",
            "status": "active",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "address_street": "200 Viewer St",
            "address_city": "New York",
            "address_state": "NY",
            "address_postal_code": "10001",
            "phone": "212-555-2222",
            "services": []
        }
        response = client.post(
            "/api/stores/",
            json=new_store,
            headers={"Authorization": f"Bearer {viewer_token}"}
        )
        assert response.status_code == 403
