from app.services.retrieval import Retriever


class FakeStore:
    def __init__(self, items):
        self._items = items

    def search(self, q_vec, top_k=10):
        # ignore q_vec, return pre-packaged items with score field
        return [
            {
                "id": it.get("id"),
                "text": it.get("text"),
                "source": it.get("source"),
                "page": it.get("page"),
                "vector": it.get("vector"),
                "score": it.get("score", 0.5),
            }
            for it in self._items
        ]


def test_retriever_basic():
    items = [
        {
            "id": "1",
            "text": "Python concurrency patterns",
            "source": "kb1",
            "page": 1,
            "vector": [0.1] * 128,
            "score": 0.8,
        },
        {
            "id": "2",
            "text": "Database indexing strategies",
            "source": "kb2",
            "page": 1,
            "vector": [0.2] * 128,
            "score": 0.6,
        },
    ]
    store = FakeStore(items)
    r = Retriever(vector_store=store)
    out = r.retrieve(
        selected_role={"title": "dev"},
        candidate_profile={"extracted_skills": ["python"]},
    )
    assert "chunks" in out
    assert isinstance(out["chunks"], list)
    assert len(out["chunks"]) >= 1
