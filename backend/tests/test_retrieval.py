from app.services.retrieval import Retriever


class MockVectorStore:
    def __init__(self):
        # Example chunks: one relevant to python, one irrelevant
        self.chunks = [
            {
                "id": "c1",
                "text": "This section explains advanced Python list comprehensions and generators.",
                "source": "kb/python_notes.pdf",
                "page": 12,
                "vector": [0.1, 0.2, 0.3],
                "score": 0.8,
            },
            {
                "id": "c2",
                "text": "Company HR policy and holiday schedule.",
                "source": "kb/hr.pdf",
                "page": 2,
                "vector": [0.01, 0.02, 0.03],
                "score": 0.1,
            },
            {
                "id": "c3",
                "text": "SQL performance tuning and EXPLAIN ANALYZE examples.",
                "source": "kb/sql_tuning.pdf",
                "page": 5,
                "vector": [0.3, 0.1, 0.05],
                "score": 0.6,
            },
        ]

    def search(self, q_vec, top_k=50):
        # Return all chunks with their score preserved
        return self.chunks[:top_k]


def test_retriever_filters_and_ranks():
    vector_store = MockVectorStore()
    retriever = Retriever(vector_store=vector_store)

    selected_role = {"title": "Backend Engineer", "core_topics": ["systems", "apis"]}
    candidate_profile = {
        "extracted_skills": ["Python"],
        "extracted_technologies": ["Postgres"],
        "extracted_domains": ["finance"],
    }

    res = retriever.retrieve(
        selected_role=selected_role,
        candidate_profile=candidate_profile,
        interview_stage="screening",
        previous_answers=None,
        knowledge_gaps=["distributed systems"],
        top_k=5,
    )

    assert "trace_id" in res
    assert "query" in res
    assert isinstance(res.get("chunks"), list)

    # c1 (python) and c3 (sql) should be present; c2 (hr) is irrelevant and low-score and should be filtered out
    ids = [c["id"] for c in res["chunks"]]
    assert "c1" in ids
    assert "c3" in ids
    assert "c2" not in ids

    # c1 (python) should rank above c3 because candidate knows Python
    if len(res["chunks"]) >= 2:
        assert ids.index("c1") < ids.index("c3")
