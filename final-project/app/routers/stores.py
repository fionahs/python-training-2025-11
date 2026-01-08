from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Store, store_services, User
from app.schemas import StoreResponse, StoreCreate, StoreUpdate
from app.dependencies import get_current_user, require_permission

router = APIRouter(prefix="/api/stores", tags=["Stores"])


@router.get("/", response_model=List[StoreResponse])
def get_all_stores(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("read:stores"))
):
    """Get all stores with pagination (requires authentication)"""
    stores = db.query(Store).offset(skip).limit(limit).all()

    # Fetch services for each store
    result = []
    for store in stores:
        store_dict = store.__dict__.copy()
        # Get services from association table
        services = db.execute(
            store_services.select().where(store_services.c.store_id == store.store_id)
        ).fetchall()
        store_dict['services'] = [s.service_name for s in services]
        result.append(store_dict)

    return result


@router.get("/{store_id}", response_model=StoreResponse)
def get_store(
    store_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("read:stores"))
):
    """Get a single store by ID (requires authentication)"""
    store = db.query(Store).filter(Store.store_id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    # Get services
    services = db.execute(
        store_services.select().where(store_services.c.store_id == store.store_id)
    ).fetchall()

    store_dict = store.__dict__.copy()
    store_dict['services'] = [s.service_name for s in services]

    return store_dict


@router.post("/", response_model=StoreResponse, status_code=status.HTTP_201_CREATED)
def create_store(
    store_data: StoreCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("write:stores"))
):
    """Create a new store (requires write:stores permission - Admin or Marketer only)"""
    # Check if store_id already exists
    existing = db.query(Store).filter(Store.store_id == store_data.store_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Store ID already exists")

    # Extract services
    services_list = store_data.services
    store_dict = store_data.model_dump()
    del store_dict['services']

    # Create store
    new_store = Store(**store_dict)
    db.add(new_store)
    db.flush()

    # Add services
    for service in services_list:
        db.execute(
            store_services.insert().values(
                store_id=new_store.store_id,
                service_name=service
            )
        )

    db.commit()
    db.refresh(new_store)

    result = new_store.__dict__.copy()
    result['services'] = services_list

    return result


@router.patch("/{store_id}", response_model=StoreResponse)
def update_store(
    store_id: str,
    store_data: StoreUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("write:stores"))
):
    """Partially update a store (requires write:stores permission - Admin or Marketer only)"""
    store = db.query(Store).filter(Store.store_id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    # Update only provided fields
    update_data = store_data.model_dump(exclude_unset=True)

    # Handle services separately
    services_list = None
    if 'services' in update_data:
        services_list = update_data.pop('services')
        # Delete existing services
        db.execute(
            store_services.delete().where(store_services.c.store_id == store_id)
        )
        # Add new services
        for service in services_list:
            db.execute(
                store_services.insert().values(
                    store_id=store_id,
                    service_name=service
                )
            )

    # Update store fields
    for field, value in update_data.items():
        setattr(store, field, value)

    db.commit()
    db.refresh(store)

    # Get current services
    if services_list is None:
        services = db.execute(
            store_services.select().where(store_services.c.store_id == store_id)
        ).fetchall()
        services_list = [s.service_name for s in services]

    result = store.__dict__.copy()
    result['services'] = services_list

    return result


@router.delete("/{store_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_store(
    store_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("delete:stores"))
):
    """Soft delete a store (requires delete:stores permission - Admin or Marketer only)"""
    store = db.query(Store).filter(Store.store_id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    # Soft delete
    store.status = "inactive"
    db.commit()

    return None
