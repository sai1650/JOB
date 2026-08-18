"""Simple retrieval demo that loads stored vectors (fallback JSON) and
returns top-k by naive cosine similarity when FAISS not available.
"""
import json
import math
from pathlib import Path


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def retrieve(role_id: str, query_vec, top_k=5, data_root: Path = None):
    data_root = data_root or Path(__file__).resolve().parents[1]
    path = data_root / "data" / f"{role_id}.index.meta.json"
    if not path.exists():
        # try fallback json
        fallback = (
            data_root / "knowledge_base" / role_id / "fallback_vectors.json"
        )
        if not fallback.exists():
            print("No vectors for role", role_id)
            return []
        arr = json.loads(fallback.read_text())
        results = []
        for item in arr:
            vec = item["vector"]
            score = cosine(query_vec, vec)
            results.append((score, item["metadata"]))
        results.sort(key=lambda x: -x[0])
        return results[:top_k]

    metas = json.loads(path.read_text())
    # without FAISS, we cannot read vectors; this demo returns metadata only
    return [(1.0, m) for m in metas[:top_k]]


if __name__ == "__main__":
    import sys

    role = sys.argv[1] if len(sys.argv) > 1 else "backend_engineer"
    # dummy random query vector
    q = [1.0] * 128
    res = retrieve(role, q)
    for s, m in res:
        print(s, m)
