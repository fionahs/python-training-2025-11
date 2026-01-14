from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Request
from sqlalchemy.orm import Session
from typing import List
import csv
import io
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.database import get_db
from app.models import Store, store_services, User
from app.dependencies import require_permission
from app.schemas import BulkImportResponse, StoreImportResult, UserCreate, UserUpdate, UserResponse
from app.utils.geocoding import geocode_address
from app.utils.auth import get_password_hash

router = APIRouter(prefix="/api/admin", tags=["Admin"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/stores/import", response_model=BulkImportResponse)
@limiter.limit("5/hour")  # Strict limit for bulk operations
async def bulk_import_stores(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("write:stores"))
):
    """
    Bulk import stores from CSV file (Admin/Marketer only)

    CSV Format:
    store_id,name,store_type,latitude,longitude,address_street,address_city,address_state,address_postal_code,phone,services,hours_monday,hours_tuesday,hours_wednesday,hours_thursday,hours_friday,hours_saturday,hours_sunday

    - If latitude/longitude are empty, will attempt to geocode from address
    - services should be pipe-separated: "pharmacy|pickup|optical"
    - Upsert logic: Creates new stores or updates existing ones based on store_id

    Returns:
    - created: Number of new stores created
    - updated: Number of existing stores updated
    - failed: List of rows that failed with error messages
    """
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV file"
        )

    # Read file content
    try:
        contents = await file.read()
        csv_text = contents.decode('utf-8')
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error reading file: {str(e)}"
        )

    # Parse CSV
    csv_reader = csv.DictReader(io.StringIO(csv_text))

    # Validate CSV headers
    required_headers = {'store_id', 'name', 'store_type', 'address_street',
                       'address_city', 'address_state', 'address_postal_code'}
    headers = set(csv_reader.fieldnames or [])

    if not required_headers.issubset(headers):
        missing = required_headers - headers
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required CSV columns: {', '.join(missing)}"
        )

    # Process each row
    created_count = 0
    updated_count = 0
    failed_records: List[StoreImportResult] = []

    for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 (header is row 1)
        try:
            # Validate required fields
            if not row.get('store_id') or not row.get('name'):
                failed_records.append(StoreImportResult(
                    row_number=row_num,
                    store_id=row.get('store_id', 'UNKNOWN'),
                    status='failed',
                    error='Missing store_id or name'
                ))
                continue

            # Handle coordinates - geocode if missing
            latitude = row.get('latitude')
            longitude = row.get('longitude')

            if not latitude or not longitude:
                # Attempt geocoding from address
                full_address = f"{row['address_street']}, {row['address_city']}, {row['address_state']} {row['address_postal_code']}"
                geocode_result = geocode_address(full_address)

                if geocode_result:
                    latitude = geocode_result['latitude']
                    longitude = geocode_result['longitude']
                else:
                    failed_records.append(StoreImportResult(
                        row_number=row_num,
                        store_id=row['store_id'],
                        status='failed',
                        error='Could not geocode address and no coordinates provided'
                    ))
                    continue

            # Convert coordinates to float
            try:
                latitude = float(latitude)
                longitude = float(longitude)
            except ValueError:
                failed_records.append(StoreImportResult(
                    row_number=row_num,
                    store_id=row['store_id'],
                    status='failed',
                    error='Invalid latitude or longitude format'
                ))
                continue

            # Validate store_type
            valid_types = ['regular', 'flagship', 'outlet', 'pop-up']
            store_type = row.get('store_type', 'regular').lower()
            if store_type not in valid_types:
                failed_records.append(StoreImportResult(
                    row_number=row_num,
                    store_id=row['store_id'],
                    status='failed',
                    error=f'Invalid store_type. Must be one of: {", ".join(valid_types)}'
                ))
                continue

            # Parse services
            services_str = row.get('services', '')
            services_list = [s.strip() for s in services_str.split('|') if s.strip()]

            # Check if store exists (UPSERT logic)
            existing_store = db.query(Store).filter(Store.store_id == row['store_id']).first()

            if existing_store:
                # UPDATE existing store
                existing_store.name = row['name']
                existing_store.store_type = store_type
                existing_store.latitude = latitude
                existing_store.longitude = longitude
                existing_store.address_street = row['address_street']
                existing_store.address_city = row['address_city']
                existing_store.address_state = row['address_state']
                existing_store.address_postal_code = row['address_postal_code']
                existing_store.phone = row.get('phone', '')
                existing_store.hours_mon = row.get('hours_monday', 'closed')
                existing_store.hours_tue = row.get('hours_tuesday', 'closed')
                existing_store.hours_wed = row.get('hours_wednesday', 'closed')
                existing_store.hours_thu = row.get('hours_thursday', 'closed')
                existing_store.hours_fri = row.get('hours_friday', 'closed')
                existing_store.hours_sat = row.get('hours_saturday', 'closed')
                existing_store.hours_sun = row.get('hours_sunday', 'closed')

                # Update services - delete old ones and add new ones
                db.execute(
                    store_services.delete().where(store_services.c.store_id == row['store_id'])
                )
                for service in services_list:
                    db.execute(
                        store_services.insert().values(
                            store_id=row['store_id'],
                            service_name=service
                        )
                    )

                updated_count += 1

            else:
                # CREATE new store
                new_store = Store(
                    store_id=row['store_id'],
                    name=row['name'],
                    store_type=store_type,
                    status='active',
                    latitude=latitude,
                    longitude=longitude,
                    address_street=row['address_street'],
                    address_city=row['address_city'],
                    address_state=row['address_state'],
                    address_postal_code=row['address_postal_code'],
                    phone=row.get('phone', ''),
                    hours_mon=row.get('hours_monday', 'closed'),
                    hours_tue=row.get('hours_tuesday', 'closed'),
                    hours_wed=row.get('hours_wednesday', 'closed'),
                    hours_thu=row.get('hours_thursday', 'closed'),
                    hours_fri=row.get('hours_friday', 'closed'),
                    hours_sat=row.get('hours_saturday', 'closed'),
                    hours_sun=row.get('hours_sunday', 'closed')
                )
                db.add(new_store)
                db.flush()

                # Add services
                for service in services_list:
                    db.execute(
                        store_services.insert().values(
                            store_id=row['store_id'],
                            service_name=service
                        )
                    )

                created_count += 1

        except Exception as e:
            failed_records.append(StoreImportResult(
                row_number=row_num,
                store_id=row.get('store_id', 'UNKNOWN'),
                status='failed',
                error=str(e)
            ))
            continue

    # Commit all changes
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

    return BulkImportResponse(
        total_rows=created_count + updated_count + len(failed_records),
        created=created_count,
        updated=updated_count,
        failed=len(failed_records),
        failed_records=failed_records
    )


# ============================================================================
# User Management Endpoints (Admin Only)
# ============================================================================

@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("write:users"))  # Admin only
):
    """
    Create a new user (Admin only)

    Requires admin permissions to create users with specific roles.
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash password
    hashed_password = get_password_hash(user_data.password)

    # Create user
    new_user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        role_id=user_data.role_id,
        status="active"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get("/users", response_model=List[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("write:users"))  # Admin only
):
    """
    List all users with pagination (Admin only)
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("write:users"))  # Admin only
):
    """
    Get a single user by ID (Admin only)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


# This works like PATCH because you can update only the fields you want to update.
# For Admin API we use PUT to signify administrative overwrite
@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("write:users"))  # Admin only
):
    """
    Update user role or status (Admin only)

    Can update:
    - full_name
    - role_id (change user role)
    - status (activate/deactivate user)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update only provided fields
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("write:users"))  # Admin only
):
    """
    Deactivate a user (soft delete - Admin only)

    Sets user status to 'inactive' instead of physically deleting the record.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Prevent self-deactivation
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )

    # Soft delete
    user.status = "inactive"
    db.commit()

    return None
