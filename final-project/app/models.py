from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey, Table, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


# Enums
class StoreType(str, enum.Enum):
    flagship = "flagship"
    regular = "regular"
    outlet = "outlet"
    express = "express"


class StoreStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    temporarily_closed = "temporarily_closed"


class UserStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"


# Association table for store services (many-to-many)
store_services = Table(
    'store_services',
    Base.metadata,
    Column('store_id', String, ForeignKey('stores.store_id', ondelete='CASCADE'), primary_key=True),
    Column('service_name', String, primary_key=True)
)


# Association table for role permissions (many-to-many)
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id', ondelete='CASCADE'), primary_key=True)
)


# Store Model
class Store(Base):
    __tablename__ = "stores"

    store_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    store_type = Column(SQLEnum(StoreType), nullable=False)
    status = Column(SQLEnum(StoreStatus), default=StoreStatus.active, index=True)

    # Location
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)

    # Address
    address_street = Column(String, nullable=False)
    address_city = Column(String, nullable=False)
    address_state = Column(String(2), nullable=False)
    address_postal_code = Column(String(5), nullable=False, index=True)
    address_country = Column(String(3), default="USA")

    # Contact
    phone = Column(String, nullable=True)

    # Hours (stored as strings: "HH:MM-HH:MM" or "closed")
    hours_mon = Column(String, default="closed")
    hours_tue = Column(String, default="closed")
    hours_wed = Column(String, default="closed")
    hours_thu = Column(String, default="closed")
    hours_fri = Column(String, default="closed")
    hours_sat = Column(String, default="closed")
    hours_sun = Column(String, default="closed")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Note: services are stored in the store_services association table
    # We'll access them via a property or join


# User Model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    status = Column(SQLEnum(UserStatus), default=UserStatus.active)

    # Foreign key to role
    role_id = Column(Integer, ForeignKey('roles.id'))

    # Relationships
    role = relationship("Role", back_populates="users")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# Role Model
class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)  # admin, marketer, viewer
    description = Column(String, nullable=True)

    # Relationships
    users = relationship("User", back_populates="role")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")


# Permission Model
class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)  # e.g., "read:stores", "write:stores", "manage:users"
    description = Column(String, nullable=True)

    # Relationships
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")


# RefreshToken Model
class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token_hash = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked = Column(Boolean, default=False)

    # Relationships
    user = relationship("User", back_populates="refresh_tokens")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
