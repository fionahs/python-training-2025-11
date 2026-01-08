"""
Test configuration and fixtures
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models import User, Role, Permission, Store, store_services
from app.utils.auth import get_password_hash

# Test database URL (using SQLite for testing)
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with the test database"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_roles(db_session):
    """Create test roles and permissions"""
    # Create permissions
    perms = {
        "read:stores": Permission(name="read:stores", description="Read store data"),
        "write:stores": Permission(name="write:stores", description="Create and update stores"),
        "delete:stores": Permission(name="delete:stores", description="Deactivate stores"),
    }
    for perm in perms.values():
        db_session.add(perm)
    db_session.flush()

    # Create roles
    admin_role = Role(name="admin", description="Full access")
    admin_role.permissions = list(perms.values())

    marketer_role = Role(name="marketer", description="Store management")
    marketer_role.permissions = [perms["read:stores"], perms["write:stores"], perms["delete:stores"]]

    viewer_role = Role(name="viewer", description="Read-only")
    viewer_role.permissions = [perms["read:stores"]]

    db_session.add(admin_role)
    db_session.add(marketer_role)
    db_session.add(viewer_role)
    db_session.commit()

    return {
        "admin": admin_role,
        "marketer": marketer_role,
        "viewer": viewer_role
    }


@pytest.fixture(scope="function")
def test_users(db_session, test_roles):
    """Create test users"""
    users = {
        "admin": User(
            email="admin@test.com",
            hashed_password=get_password_hash("AdminTest123!"),
            full_name="Admin User",
            role_id=test_roles["admin"].id
        ),
        "marketer": User(
            email="marketer@test.com",
            hashed_password=get_password_hash("MarketerTest123!"),
            full_name="Marketer User",
            role_id=test_roles["marketer"].id
        ),
        "viewer": User(
            email="viewer@test.com",
            hashed_password=get_password_hash("ViewerTest123!"),
            full_name="Viewer User",
            role_id=test_roles["viewer"].id
        )
    }

    for user in users.values():
        db_session.add(user)
    db_session.commit()

    return users


@pytest.fixture(scope="function")
def test_store(db_session):
    """Create a test store"""
    store = Store(
        store_id="S0001",
        name="Test Store",
        store_type="regular",
        status="active",
        latitude=40.7128,
        longitude=-74.0060,
        address_street="123 Test St",
        address_city="New York",
        address_state="NY",
        address_postal_code="10001",
        address_country="USA",
        phone="212-555-1234",
        hours_mon="09:00-21:00",
        hours_tue="09:00-21:00",
        hours_wed="09:00-21:00",
        hours_thu="09:00-21:00",
        hours_fri="09:00-21:00",
        hours_sat="10:00-20:00",
        hours_sun="10:00-18:00"
    )
    db_session.add(store)
    db_session.flush()

    # Add services
    db_session.execute(
        store_services.insert().values(store_id=store.store_id, service_name="pharmacy")
    )
    db_session.execute(
        store_services.insert().values(store_id=store.store_id, service_name="pickup")
    )
    db_session.commit()

    return store


@pytest.fixture(scope="function")
def admin_token(client, test_users):
    """Get admin access token"""
    response = client.post("/api/auth/login", json={
        "email": "admin@test.com",
        "password": "AdminTest123!"
    })
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def marketer_token(client, test_users):
    """Get marketer access token"""
    response = client.post("/api/auth/login", json={
        "email": "marketer@test.com",
        "password": "MarketerTest123!"
    })
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def viewer_token(client, test_users):
    """Get viewer access token"""
    response = client.post("/api/auth/login", json={
        "email": "viewer@test.com",
        "password": "ViewerTest123!"
    })
    return response.json()["access_token"]
