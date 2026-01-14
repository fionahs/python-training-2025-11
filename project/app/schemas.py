from pydantic import BaseModel, EmailStr, Field, model_validator
from typing import Optional, List
from datetime import datetime
from app.models import StoreType, StoreStatus, UserStatus


# Store Schemas
class StoreBase(BaseModel):
    name: str
    store_type: StoreType
    status: StoreStatus = StoreStatus.active
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    address_street: str
    address_city: str
    address_state: str = Field(..., min_length=2, max_length=2)
    address_postal_code: str = Field(..., min_length=5, max_length=5)
    address_country: str = Field(default="USA", min_length=3, max_length=3)
    phone: Optional[str] = None
    services: List[str] = []
    hours_mon: str = "closed"
    hours_tue: str = "closed"
    hours_wed: str = "closed"
    hours_thu: str = "closed"
    hours_fri: str = "closed"
    hours_sat: str = "closed"
    hours_sun: str = "closed"


class StoreCreate(StoreBase):
    store_id: str


class StoreUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    services: Optional[List[str]] = None
    status: Optional[StoreStatus] = None
    hours_mon: Optional[str] = None
    hours_tue: Optional[str] = None
    hours_wed: Optional[str] = None
    hours_thu: Optional[str] = None
    hours_fri: Optional[str] = None
    hours_sat: Optional[str] = None
    hours_sun: Optional[str] = None


class StoreResponse(StoreBase):
    store_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str
    role_id: int


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role_id: Optional[int] = None
    status: Optional[UserStatus] = None


class UserResponse(UserBase):
    id: int
    status: UserStatus
    role_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Authentication Schemas
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None
    role: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


# Store Search Schemas
class StoreSearchRequest(BaseModel):
    # One of these is required
    address: Optional[str] = None
    postal_code: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)

    # Filters
    radius_miles: float = Field(default=10, ge=0, le=100)
    services: Optional[List[str]] = None
    store_types: Optional[List[StoreType]] = None
    open_now: Optional[bool] = None

    @model_validator(mode='after')
    def validate_lat_lon_pair(self):
        if (self.latitude is not None and self.longitude is None) or \
           (self.longitude is not None and self.latitude is None):
            raise ValueError('Both latitude and longitude must be provided together')

        # Validate at least one search method provided
        if not any([self.address, self.postal_code, self.latitude]):
            raise ValueError('At least one of address, postal_code, or latitude/longitude must be provided')

        return self


class StoreSearchResult(BaseModel):
    store: StoreResponse
    distance_miles: float
    is_open_now: bool


class StoreSearchResponse(BaseModel):
    results: List[StoreSearchResult]
    search_location: dict
    filters_applied: dict
    total_results: int


# Bulk Import Schemas
class StoreImportResult(BaseModel):
    row_number: int
    store_id: str
    status: str  # 'created', 'updated', or 'failed'
    error: Optional[str] = None


class BulkImportResponse(BaseModel):
    total_rows: int
    created: int
    updated: int
    failed: int
    failed_records: List[StoreImportResult]
