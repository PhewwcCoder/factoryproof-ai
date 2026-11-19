import os
import uuid
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import JSON, DateTime, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

Path('runtime').mkdir(exist_ok=True)
URL = os.getenv('DATABASE_URL', 'sqlite:///./runtime/factoryproof.db')
engine = create_engine(URL, connect_args={'check_same_thread': False} if URL.startswith('sqlite') else {}, pool_pre_ping=True)
SessionLocal = sessionmaker(engine, expire_on_commit=False)


def now():
    return datetime.now(UTC)


def uid():
    return uuid.uuid4().hex


class Base(DeclarativeBase):
    pass


class Record(Base):
    """Tenant-scoped versioned domain records; payload schemas validated at API boundaries."""
    __tablename__ = 'records'
    id: Mapped[str] = mapped_column(String(80), primary_key=True, default=uid)
    tenant: Mapped[str] = mapped_column(String(80), index=True)
    kind: Mapped[str] = mapped_column(String(40), index=True)
    payload: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class User(Base):
    __tablename__ = 'users'
    id: Mapped[str] = mapped_column(String(80), primary_key=True, default=uid)
    email: Mapped[str] = mapped_column(String(254), unique=True)
    password: Mapped[str] = mapped_column(String(300))
    tenant: Mapped[str] = mapped_column(String(80), index=True)
    role: Mapped[str] = mapped_column(String(40))


class Session(Base):
    __tablename__ = 'sessions'
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant: Mapped[str] = mapped_column(String(80), index=True)
    user_id: Mapped[str] = mapped_column(String(80))
    role: Mapped[str] = mapped_column(String(40))
    demo: Mapped[bool]
    expires: Mapped[datetime] = mapped_column(DateTime(timezone=True))


def get_db():
    with SessionLocal() as db:
        yield db


def records(db, tenant, kind):
    return db.query(Record).filter_by(tenant=tenant, kind=kind).order_by(Record.created_at).all()


def serialize(record):
    return {**record.payload, 'id': record.id, 'created_at': record.created_at.isoformat()}
