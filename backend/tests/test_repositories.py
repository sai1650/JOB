import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.base import Base
from app.models.candidate import Candidate
from app.repositories.candidate_repo import CandidateRepository
from app.schemas.candidate import CandidateCreate


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_candidate_crud(db_session):
    repo = CandidateRepository(db_session)
    payload = CandidateCreate(name="Alice", email="alice@example.com")
    created = repo.create(payload)
    assert created.id is not None
    assert created.email == "alice@example.com"

    fetched = repo.get(created.id)
    assert fetched is not None
    assert fetched.email == "alice@example.com"

    by_email = repo.get_by_email("alice@example.com")
    assert by_email is not None
