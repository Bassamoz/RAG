"""Only the identity/tenant/store foundation; provider owns auth schema and passwords."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "app"}
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    auth_subject: Mapped[UUID] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Tenant(Base):
    __tablename__ = "tenants"
    __table_args__ = {"schema": "app"}
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(160))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Membership(Base):
    __tablename__ = "memberships"
    __table_args__ = (
        CheckConstraint("role IN ('tenant_owner','tenant_admin','support_agent','analyst')"),
        CheckConstraint("status IN ('active','suspended')"),
        {"schema": "app"},
    )
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("app.tenants.id"), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("app.users.id"), primary_key=True)
    role: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(16), server_default="active")


class Store(Base):
    __tablename__ = "stores"
    __table_args__ = (UniqueConstraint("tenant_id", "id"), {"schema": "app"})
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("app.tenants.id"))
    name: Mapped[str] = mapped_column(String(160))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
