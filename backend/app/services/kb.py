import os
import json
import hashlib
import logging
import math
from typing import List, Dict, Any, Iterable

try:
    import fitz
except Exception:
    fitz = None

try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None

try:
    import faiss
except Exception:
    faiss = None

logger = logging.getLogger(__name__)


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


class DocumentProcessor:
    def __init__(self, path: str):
        self.path = path

    def extract_text(self) -> Dict[int, str]:
        """Return mapping page_num -> text"""
        if self.path.lower().endswith(".pdf"):
            if not fitz:
                raise RuntimeError("PyMuPDF not installed")
            doc = fitz.open(self.path)
            pages = {}
            for i, p in enumerate(doc):
                pages[i + 1] = p.get_text()
            return pages
        else:
            # txt
            with open(self.path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
            return {1: text}


class ChunkingService:
    def __init__(self, chunk_size: int = 800, overlap: int = 100):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_pages(self, pages: Dict[int, str]) -> List[Dict[str, Any]]:
        chunks = []
        for page, text in pages.items():
            text = text.replace("\x0c", "\n")
            # split by paragraphs
            paras = [p.strip() for p in text.split("\n\n") if p.strip()]
            buffer = ""
            for para in paras:
                if len(buffer) + len(para) + 1 <= self.chunk_size:
                    buffer = (buffer + "\n\n" + para).strip()
                else:
                    if buffer:
                        chunks.append({"text": buffer, "page": page})
                    # if para itself too big, split
                    if len(para) > self.chunk_size:
                        step = self.chunk_size - self.overlap
                        for i in range(0, len(para), step):
                            part = para[i:i + self.chunk_size]
                            chunks.append({"text": part, "page": page})
                        buffer = ""
                    else:
                        buffer = para
            if buffer:
                chunks.append({"text": buffer, "page": page})

        # assign chunk ids
        for idx, c in enumerate(chunks):
            c["chunk_id"] = f"chunk_{idx:06d}"
        return chunks


class EmbeddingService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        if SentenceTransformer is None:
            self.model = None
            logger.warning(
                "sentence-transformers not available; embeddings disabled"
            )
        else:
            self.model = SentenceTransformer(model_name)

    def embed(self, texts: Iterable[str]) -> List[List[float]]:
        if not self.model:
            # fallback: simple hashing to floats to keep pipeline runnable
            out = []
            for t in texts:
                h = hashlib.sha256(t.encode("utf-8")).digest()
                vec = [float(x) for x in h[:128]]
                out.append(vec)
            return out
        return self.model.encode(list(texts)).tolist()


class VectorStoreService:
    def __init__(self, index_path: str):
        self.index_path = index_path
        os.makedirs(os.path.dirname(index_path), exist_ok=True)
        self.index = None

    def persist(
        self, vectors: List[List[float]], metadatas: List[Dict[str, Any]]
    ):
        # simple FAISS index per collection
        if faiss is None:
            # write to JSON file as fallback
            out = []
            for v, m in zip(vectors, metadatas):
                out.append({"vector": v, "metadata": m})
            with open(self.index_path, "w", encoding="utf-8") as f:
                json.dump(out, f, ensure_ascii=False, indent=2)
            return

        dim = len(vectors[0])
        idx = faiss.IndexFlatL2(dim)
        import numpy as np

        arr = np.array(vectors).astype('float32')
        idx.add(arr)
        faiss.write_index(idx, self.index_path)
        # persist metadata alongside
        meta_path = self.index_path + ".meta.json"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(metadatas, f, ensure_ascii=False, indent=2)

    def search(self, q_vec: List[float], top_k: int = 10) -> List[Dict[str, Any]]:
        """Search the index. If FAISS is available and index exists, use it;
        otherwise read fallback JSON and compute cosine similarity.
        Returns list of dicts with keys: id, text, source, page, vector, score
        """
        results: List[Dict[str, Any]] = []
        # Try FAISS
        if faiss is not None:
            import numpy as np

            try:
                idx = faiss.read_index(self.index_path)
                # load metadata
                meta_path = self.index_path + ".meta.json"
                metas = []
                if os.path.exists(meta_path):
                    metas = json.loads(open(meta_path, "r", encoding="utf-8").read())
                q = np.array(q_vec).astype('float32').reshape(1, -1)
                D, I = idx.search(q, top_k)
                for dist, idx_i in zip(D[0], I[0]):
                    meta = metas[idx_i] if idx_i < len(metas) else {}
                    results.append({
                        "id": meta.get("chunk_id"),
                        "text": meta.get("text"),
                        "source": meta.get("source"),
                        "page": meta.get("page"),
                        "vector": None,
                        "score": float(1.0 - dist) if dist is not None else 0.0,
                    })
                return results
            except Exception:
                # fall back to JSON below
                results = []

        # JSON fallback: try index_path itself (persist wrote JSON when faiss missing)
        if os.path.exists(self.index_path):
            try:
                arr = json.loads(open(self.index_path, "r", encoding="utf-8").read())
                scored = []
                for item in arr:
                    v = item.get("vector")
                    meta = item.get("metadata") or {}
                    if v is None:
                        continue
                    # compute cosine
                    dot = sum(x * y for x, y in zip(q_vec, v))
                    na = math.sqrt(sum(x * x for x in q_vec))
                    nb = math.sqrt(sum(y * y for y in v))
                    score = 0.0
                    if na and nb:
                        score = dot / (na * nb)
                    scored.append((score, meta, v))
                scored.sort(key=lambda x: -x[0])
                out = []
                for s, meta, v in scored[:top_k]:
                    out.append({
                        "id": meta.get("chunk_id"),
                        "text": meta.get("text"),
                        "source": meta.get("source"),
                        "page": meta.get("page"),
                        "vector": v,
                        "score": float(s),
                    })
                return out
            except Exception:
                return []

        # try known fallback in knowledge_base folder
        try:
            kb_fallback = os.path.join(os.path.dirname(self.index_path), "fallback_vectors.json")
            if os.path.exists(kb_fallback):
                arr = json.loads(open(kb_fallback, "r", encoding="utf-8").read())
                scored = []
                for item in arr:
                    v = item.get("vector")
                    meta = item.get("metadata") or {}
                    if v is None:
                        continue
                    dot = sum(x * y for x, y in zip(q_vec, v))
                    na = math.sqrt(sum(x * x for x in q_vec))
                    nb = math.sqrt(sum(y * y for y in v))
                    score = 0.0
                    if na and nb:
                        score = dot / (na * nb)
                    scored.append((score, meta, v))
                scored.sort(key=lambda x: -x[0])
                out = []
                for s, meta, v in scored[:top_k]:
                    out.append({
                        "id": meta.get("chunk_id"),
                        "text": meta.get("text"),
                        "source": meta.get("source"),
                        "page": meta.get("page"),
                        "vector": v,
                        "score": float(s),
                    })
                return out
        except Exception:
            return []

        return []

