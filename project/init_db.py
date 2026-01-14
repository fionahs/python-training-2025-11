"""
Database initialization script
Creates all tables and seeds initial data
"""
import csv
import os
from sqlalchemy.orm import Session
from app.database import engine, Base, SessionLocal
from app.models import Store, User, Role, Permission, role_permissions, store_services
from app.utils.auth import get_password_hash


def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created successfully!")


def seed_roles_and_permissions(db: Session):
    """Create default roles and permissions"""
    print("\nSeeding roles and permissions...")

    # Create permissions
    permissions_data = [
        {"name": "read:stores", "description": "Read store data"},
        {"name": "write:stores", "description": "Create and update stores"},
        {"name": "delete:stores", "description": "Deactivate stores"},
        {"name": "import:stores", "description": "Bulk import stores"},
        {"name": "read:users", "description": "Read user data"},
        {"name": "write:users", "description": "Create and update users"},
        {"name": "delete:users", "description": "Deactivate users"},
    ]

    permissions = {}
    for perm_data in permissions_data:
        perm = db.query(Permission).filter(Permission.name == perm_data["name"]).first()
        if not perm:
            perm = Permission(**perm_data)
            db.add(perm)
            db.flush()
        permissions[perm_data["name"]] = perm

    # Create roles with permissions
    roles_data = [
        {
            "name": "admin",
            "description": "Full access to all resources",
            "permissions": list(permissions.values())
        },
        {
            "name": "marketer",
            "description": "Can manage stores but not users",
            "permissions": [
                permissions["read:stores"],
                permissions["write:stores"],
                permissions["delete:stores"],
                permissions["import:stores"]
            ]
        },
        {
            "name": "viewer",
            "description": "Read-only access to stores",
            "permissions": [permissions["read:stores"]]
        }
    ]

    roles = {}
    for role_data in roles_data:
        role = db.query(Role).filter(Role.name == role_data["name"]).first()
        if not role:
            perms = role_data.pop("permissions")
            role = Role(**role_data)
            role.permissions = perms
            db.add(role)
            db.flush()
        roles[role_data["name"]] = role

    db.commit()
    print("✓ Roles and permissions created!")
    return roles


def seed_users(db: Session, roles: dict):
    """Create default test users"""
    print("\nSeeding users...")

    users_data = [
        {
            "email": "admin@test.com",
            "password": "AdminTest123!",
            "full_name": "Admin User",
            "role": roles["admin"]
        },
        {
            "email": "marketer@test.com",
            "password": "MarketerTest123!",
            "full_name": "Marketer User",
            "role": roles["marketer"]
        },
        {
            "email": "viewer@test.com",
            "password": "ViewerTest123!",
            "full_name": "Viewer User",
            "role": roles["viewer"]
        }
    ]

    for user_data in users_data:
        existing_user = db.query(User).filter(User.email == user_data["email"]).first()
        if not existing_user:
            hashed_pw = get_password_hash(user_data.pop("password"))
            role = user_data.pop("role")
            user = User(
                **user_data,
                hashed_password=hashed_pw,
                role_id=role.id
            )
            db.add(user)
            print(f"  Created user: {user_data['email']}")

    db.commit()
    print("✓ Users created!")


def load_stores_from_csv(db: Session, csv_file: str):
    """Load stores from CSV file"""
    if not os.path.exists(csv_file):
        print(f"✗ Warning: CSV file not found at {csv_file}")
        return

    print(f"\nLoading stores from {csv_file}...")

    with open(csv_file, 'r') as file:
        csv_reader = csv.DictReader(file)
        count = 0

        for row in csv_reader:
            # Check if store already exists
            existing_store = db.query(Store).filter(Store.store_id == row['store_id']).first()
            if existing_store:
                continue

            # Parse services
            services_list = row['services'].split('|') if row['services'] else []

            # Create store
            store = Store(
                store_id=row['store_id'],
                name=row['name'],
                store_type=row['store_type'],
                status=row['status'],
                latitude=float(row['latitude']),
                longitude=float(row['longitude']),
                address_street=row['address_street'],
                address_city=row['address_city'],
                address_state=row['address_state'],
                address_postal_code=row['address_postal_code'],
                address_country=row['address_country'],
                phone=row['phone'],
                hours_mon=row['hours_mon'],
                hours_tue=row['hours_tue'],
                hours_wed=row['hours_wed'],
                hours_thu=row['hours_thu'],
                hours_fri=row['hours_fri'],
                hours_sat=row['hours_sat'],
                hours_sun=row['hours_sun']
            )
            db.add(store)
            db.flush()

            # Add services to association table
            for service in services_list:
                db.execute(
                    store_services.insert().values(
                        store_id=store.store_id,
                        service_name=service.strip()
                    )
                )

            count += 1

        db.commit()
        print(f"✓ Loaded {count} stores!")


def main():
    """Run all initialization steps"""
    print("=" * 50)
    print("DATABASE INITIALIZATION")
    print("=" * 50)

    # Create tables
    create_tables()

    # Create database session
    db = SessionLocal()

    try:
        # Seed roles and permissions
        roles = seed_roles_and_permissions(db)

        # Seed users
        seed_users(db, roles)

        # Load stores (from data directory)
        load_stores_from_csv(db, "data/stores_50.csv")
        load_stores_from_csv(db, "data/stores_1000.csv")

        print("\n" + "=" * 50)
        print("✓ DATABASE INITIALIZED SUCCESSFULLY!")
        print("=" * 50)
        print("\nTest Users:")
        print("  Admin:    admin@test.com / AdminTest123!")
        print("  Marketer: marketer@test.com / MarketerTest123!")
        print("  Viewer:   viewer@test.com / ViewerTest123!")
        print("=" * 50)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
