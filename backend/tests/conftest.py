# tests/conftest.py
import os

# ✅ Force the app to use the same test DB BEFORE app is imported
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid
from datetime import datetime, timezone

from app.routers import api_router  # ✅ Only import router, not app instance
from app.db import Base, get_db

# ✅ IMPORTANT: import models BEFORE create_all so tables register on Base
from app.models.models import Event, Member, MembershipType

# ----------------------------
# ✅ SQLite compat for JSONB
# ----------------------------
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.compiler import compiles

@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "JSON"

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# ✅ Create / drop tables once per test session
@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# ✅ Function-scoped DB session wrapped in a transaction
@pytest.fixture(scope="function")
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()

# ✅ Build test app instance inside fixture
from fastapi import FastAPI

def create_test_app():
    test_app = FastAPI(title="Test Arimala App")
    test_app.include_router(api_router)
    return test_app

@pytest.fixture(scope="function")
def client(db):
    app = create_test_app()

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def test_event(db):
    e = Event(
        id=uuid.uuid4(),
        name="Test Event",
        starts_at=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
    )
    db.add(e)
    db.commit()
    db.refresh(e)
    return e

@pytest.fixture(scope="function")
def test_member(db):
    m = Member(
        id=uuid.uuid4(),
        full_name="Test Member",
        email="test@example.com",
        membership_type=MembershipType.FAMILY,
        pass_id="FAKEPASS123",
        created_at=datetime.now(timezone.utc),
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return m
