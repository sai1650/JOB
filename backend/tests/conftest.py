import shutil

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.db.database as dbmod
from app.models.base import Base
from app.main import app


@pytest.fixture(scope="session")
def tmp_dir(tmp_path_factory):
    d = tmp_path_factory.mktemp("data")
    yield d
    shutil.rmtree(str(d), ignore_errors=True)


@pytest.fixture(scope="session")
def test_db(tmp_path_factory):
    # create a temporary sqlite file and point app database to it
    db_file = tmp_path_factory.mktemp("db") / "test.sqlite"
    url = f"sqlite:///{db_file}"
    engine = create_engine(url, future=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # replace module engine and session
    dbmod.engine = engine
    dbmod.SessionLocal = SessionLocal

    # create tables
    Base.metadata.create_all(bind=engine)

    yield {
        "engine": engine,
        "url": url,
        "session_factory": SessionLocal,
    }


@pytest.fixture
def client(test_db):
    with TestClient(app) as c:
        yield c


@pytest.fixture
def mock_llm(monkeypatch):
    """Provide helper to stub LLM call behaviors."""

    def _set(return_value=None, side_effect=None):
        def fake(prompt):
            if side_effect:
                raise side_effect
            if callable(return_value):
                return return_value(prompt)
            return return_value

        def _gen(self, p, max_tokens=512):
            return fake(p)

        monkeypatch.setattr("app.services.llm.LLMClient.generate", _gen)

    return _set
