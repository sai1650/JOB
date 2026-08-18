import os
import json


def _ensure_fallback_kb():
    base = os.path.join(os.path.dirname(__file__), "..", "app")
    kb_dir = os.path.join(base, "knowledge_base", "default")
    os.makedirs(kb_dir, exist_ok=True)
    path = os.path.join(kb_dir, "fallback_vectors.json")
    sample = [
        {
            "vector": [0.1] * 128,
            "metadata": {
                "chunk_id": "c1",
                "text": "Generators and iterators in Python",
                "source": "kb/python.pdf",
                "page": 10,
            },
        }
    ]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(sample, f)


def test_full_interview_lifecycle(client):
    _ensure_fallback_kb()

    # upload resume -> create candidate
    files = {"file": ("resume.txt", "Python\nGenerators\n", "text/plain")}
    data = {"name": "Candidate", "email": "c@example.com"}
    r = client.post("/api/resume/upload", data=data, files=files)
    assert r.status_code == 200
    cid = r.json()["candidate_id"]

    # create interview
    payload = {"candidate_id": cid, "selected_role": "default"}
    r = client.post("/api/interviews", json=payload)
    assert r.status_code == 200
    sid = r.json()["session_id"]

    # get current question
    r = client.get(f"/api/interviews/{sid}/current-question")
    assert r.status_code in (200, 404)
    if r.status_code == 404:
        # No question generated; fail here to highlight issue
        assert False, "No initial question generated"
    payload = r.json()
    q = payload["question"]
    qid = q.get("id")
    assert q.get("text")
    assert payload["progress"]["current"] >= 1

    # submit an answer
    ans = {
        "question_id": qid,
        "answer_text": "I would use generators to lazily produce values.",
    }
    r = client.post(f"/api/interviews/{sid}/answer", json=ans)
    assert r.status_code == 200
    r.json().get("answer_id")

    # duplicate submission should be rejected
    r2 = client.post(f"/api/interviews/{sid}/answer", json=ans)
    assert r2.status_code == 409

    # advance to next question
    r = client.post(f"/api/interviews/{sid}/next")
    assert r.status_code == 200

    # complete interview
    r = client.post(f"/api/interviews/{sid}/complete")
    assert r.status_code == 200

    # completed session should reject new answers
    r = client.post(f"/api/interviews/{sid}/answer", json=ans)
    assert r.status_code == 400

    # fetch report
    r = client.get(f"/api/interviews/{sid}/report")
    assert r.status_code == 200
    rep = r.json()
    assert rep.get("session_id") == sid
    assert "generated_report" in rep


def test_init_db_repairs_missing_strategy_state_column(tmp_path):
    import app.db.database as dbmod
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    db_file = tmp_path / "stale.sqlite"
    engine = create_engine(f"sqlite:///{db_file}", future=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    dbmod.engine = engine
    dbmod.SessionLocal = SessionLocal

    with engine.begin() as conn:
        conn.exec_driver_sql(
            """
            CREATE TABLE interview_sessions (
                id VARCHAR(36) PRIMARY KEY,
                candidate_id VARCHAR(36) NOT NULL,
                selected_role VARCHAR(255),
                status VARCHAR(50) NOT NULL,
                current_question_index INTEGER,
                started_at DATETIME,
                completed_at DATETIME
            )
            """
        )

    dbmod.init_db()

    with engine.begin() as conn:
        cols = [
            row[1]
            for row in conn.exec_driver_sql(
                "PRAGMA table_info(interview_sessions)"
            ).fetchall()
        ]

    assert "strategy_state" in cols
