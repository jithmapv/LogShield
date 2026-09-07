import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import get_settings
from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def client(tmp_path, monkeypatch):
    engine = create_engine(f"sqlite:///{tmp_path}/test.db", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    app.dependency_overrides[get_db] = lambda: session_factory()
    app.state.test_session_factory = session_factory
    app.state.testing = True
    get_settings.cache_clear()
    monkeypatch.setenv("INGESTION_API_KEY", "test-key")
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    app.state.testing = False
    Base.metadata.drop_all(engine)