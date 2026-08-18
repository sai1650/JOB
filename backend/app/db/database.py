import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.base import Base

logger = logging.getLogger("candidate_screening.db")

# SQLAlchemy engine & session (initially point to configured DB)
engine = create_engine(settings.DATABASE_URL, future=True)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine,
)


def _ensure_sqlite_columns():
    """Backfill legacy SQLite databases missing newer columns."""
    if getattr(engine, "dialect", None) and engine.dialect.name != "sqlite":
        return

    table_columns = {
        "interview_sessions": {
            "strategy_state": "JSON",
        },
        "interview_answers": {
            "evaluation": "JSON",
        },
        "interview_reports": {
            "report": "JSON",
        },
    }

    with engine.begin() as conn:
        for table_name, columns in table_columns.items():
            try:
                existing = conn.exec_driver_sql(
                    f"PRAGMA table_info({table_name})"
                ).fetchall()
            except Exception:
                continue

            existing_names = {row[1] for row in existing}
            for column_name, column_type in columns.items():
                if column_name in existing_names:
                    continue
                conn.exec_driver_sql(
                    (
                        f"ALTER TABLE {table_name} ADD COLUMN "
                        f"{column_name} {column_type}"
                    )
                )


def init_db():
    """Initialize DB tables. If the configured Postgres DB is unreachable
    (e.g. Docker not running), fall back to a local SQLite file for dev.
    """
    global engine, SessionLocal
    try:
        # attempt a real connection
        with engine.connect():
            pass
    except Exception as exc:  # pragma: no cover - environment dependent
        logger.warning(
            "Primary database unavailable (%s). Falling back to SQLite.",
            exc,
        )
        engine = create_engine("sqlite:///./dev.db", future=True)
        SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
            bind=engine,
        )

    # create tables if they don't exist (useful for dev)
    Base.metadata.create_all(bind=engine)
    _ensure_sqlite_columns()


# Ensure DB is initialized at import time so tests that hit endpoints
# without FastAPI startup handlers still get a usable fallback (SQLite).
try:
    init_db()
except Exception:
    # swallow errors during import-time initialization
    pass

