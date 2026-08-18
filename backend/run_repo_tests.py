import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.base import Base
from app.repositories.candidate_repo import CandidateRepository
from app.schemas.candidate import CandidateCreate


def main():
    engine = create_engine("sqlite:///:memory:", echo=False)
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        repo = CandidateRepository(db)
        payload = CandidateCreate(name="Alice", email="alice@example.com")
        created = repo.create(payload)
        assert created.id is not None
        assert created.email == "alice@example.com"

        fetched = repo.get(created.id)
        assert fetched is not None
        assert fetched.email == "alice@example.com"

        by_email = repo.get_by_email("alice@example.com")
        assert by_email is not None

    except AssertionError as e:
        print("Tests failed:", e)
        sys.exit(1)
    finally:
        db.close()

    print("Repository smoke tests passed")


if __name__ == "__main__":
    main()
