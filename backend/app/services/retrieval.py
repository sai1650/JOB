import hashlib
import json
import math
import uuid
from typing import Any, Dict, List, Optional, Tuple

try:
    # Prefer existing embedding/vector services if available
    from app.services.kb import EmbeddingService, VectorStoreService
except Exception:
    EmbeddingService = None  # type: ignore
    VectorStoreService = None  # type: ignore


def _simple_text_hash_vector(text: str, dim: int = 128) -> List[float]:
    h = hashlib.sha256(text.encode("utf-8")).digest()
    vec = []
    for i in range(dim):
        vec.append((h[i % len(h)] / 255.0) * (1 if i % 2 == 0 else -1))
    return vec


def _cosine(a: List[float], b: List[float]) -> float:
    if not a or not b:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


class QueryBuilder:
    """Builds a dynamic retrieval query from candidate, role, and interview context."""

    def build(
        self,
        selected_role: Dict[str, Any],
        candidate_profile: Dict[str, Any],
        interview_stage: Optional[str] = None,
        previous_answers: Optional[List[Dict[str, Any]]] = None,
        knowledge_gaps: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        topics = []
        parts = []

        # Role core topics
        if selected_role:
            role_topics = selected_role.get("core_topics") or []
            topics.extend(role_topics)
            role_title = selected_role.get("title") or "general"
            parts.append("Role: " + str(role_title))

        # Candidate skills/technologies/domains
        skills = candidate_profile.get("extracted_skills") or []
        techs = candidate_profile.get("extracted_technologies") or []
        domains = candidate_profile.get("extracted_domains") or []
        if skills:
            topics.extend(skills)
            parts.append("Skills: " + ", ".join(skills[:8]))
        if techs:
            topics.extend(techs)
            parts.append("Technologies: " + ", ".join(techs[:8]))
        if domains:
            topics.extend(domains)
            parts.append("Domains: " + ", ".join(domains[:8]))

        # Knowledge gaps
        if knowledge_gaps:
            topics.extend(knowledge_gaps)
            parts.append("Knowledge gaps: " + ", ".join(knowledge_gaps))

        # Interview stage influences phrasing
        if interview_stage:
            parts.append("Stage: " + interview_stage)

        # Previous answers summary to avoid repetition
        if previous_answers:
            prev_text = []
            for a in previous_answers[-3:]:
                q = a.get("question") or ""
                ans = a.get("answer") or ""
                prev_text.append(f"Q:{q} A:{ans}")
            parts.append("Previous: " + " || ".join(prev_text))

        # de-dup topics and keep order
        seen = set()
        dedup_topics = []
        for t in topics:
            if not t:
                continue
            key = t.lower() if isinstance(t, str) else str(t)
            if key in seen:
                continue
            seen.add(key)
            dedup_topics.append(t)

        query = " | ".join(parts) if parts else ""

        return {"query": query, "topics": dedup_topics}


class ContextAssembler:
    """Assembles initial candidate chunks from a vector store using the dynamic query and topics."""

    def __init__(self, embedding_service: Optional[Any] = None, vector_store: Optional[Any] = None):
        self.embedding_service = embedding_service
        self.vector_store = vector_store

    def assemble(self, query: str, topics: List[str], top_k: int = 50) -> List[Dict[str, Any]]:
        # Use embedding_service if available, else simple hash-vector
        text_for_embed = query + " | " + (", ".join(topics) if topics else "")
        if self.embedding_service:
            q_vec = self.embedding_service.embed(text_for_embed)
        else:
            q_vec = _simple_text_hash_vector(text_for_embed)

        # Ask the vector store for candidate chunks
        if self.vector_store and hasattr(self.vector_store, "search"):
            results = self.vector_store.search(q_vec, top_k=top_k)
        else:
            # No vector store: return empty
            results = []

        # Expect results as list of dicts: {"id","text","source","page","vector","score"}
        out = []
        for r in results:
            out.append(
                {
                    "id": r.get("id") or str(uuid.uuid4()),
                    "text": r.get("text", ""),
                    "source": r.get("source"),
                    "page": r.get("page"),
                    "vector": r.get("vector"),
                    "score": float(r.get("score", 0.0)),
                }
            )
        return out


class ContextRanker:
    """Re-ranks and filters chunks based on keyword overlap and vector score."""

    def __init__(self, min_score: float = 0.05, topic_boost: float = 0.15):
        self.min_score = min_score
        self.topic_boost = topic_boost

    def _overlap_score(self, text: str, keywords: List[str]) -> float:
        if not keywords:
            return 0.0
        t = text.lower()
        hits = 0
        for k in keywords:
            if not k:
                continue
            if k.lower() in t:
                hits += 1
        return hits / max(1, len(keywords))

    def rank(
        self,
        chunks: List[Dict[str, Any]],
        topics: List[str],
        candidate_profile: Dict[str, Any],
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        skills = (candidate_profile.get("extracted_skills") or []) + (
            candidate_profile.get("extracted_technologies") or []
        )
        domains = candidate_profile.get("extracted_domains") or []
        keywords = skills + domains + topics

        scored = []
        for c in chunks:
            base = c.get("score", 0.0)
            text = c.get("text", "")
            ov = self._overlap_score(text, keywords)
            # Boost = proportional to overlap
            boosted = base + (ov * self.topic_boost)
            c["relevance"] = boosted
            c["overlap"] = ov
            scored.append(c)

        # Filter by absolute minimum score, non-empty text, and require either
        # some keyword overlap or a minimum base vector score to avoid returning
        # clearly irrelevant low-score items.
        filtered = [
            c
            for c in scored
            if c.get("relevance", 0) >= self.min_score
            and c.get("text")
            and (c.get("overlap", 0) > 0 or c.get("score", 0) >= 0.25)
        ]

        # Sort descending
        filtered.sort(key=lambda x: x.get("relevance", 0), reverse=True)

        return filtered[:limit]


class Retriever:
    """High-level retrieval orchestrator.

    Returns a traceable retrieval result linking query->topics->chunks.
    """

    def __init__(
        self,
        embedding_service: Optional[Any] = None,
        vector_store: Optional[Any] = None,
        ranker: Optional[ContextRanker] = None,
    ):
        self.query_builder = QueryBuilder()
        self.assembler = ContextAssembler(embedding_service=embedding_service, vector_store=vector_store)
        self.ranker = ranker or ContextRanker()
        self.vector_store = vector_store

    def retrieve(
        self,
        selected_role: Dict[str, Any],
        candidate_profile: Dict[str, Any],
        interview_stage: Optional[str] = None,
        previous_answers: Optional[List[Dict[str, Any]]] = None,
        knowledge_gaps: Optional[List[str]] = None,
        top_k: int = 10,
    ) -> Dict[str, Any]:
        trace_id = str(uuid.uuid4())
        qb = self.query_builder.build(
            selected_role=selected_role,
            candidate_profile=candidate_profile,
            interview_stage=interview_stage,
            previous_answers=previous_answers,
            knowledge_gaps=knowledge_gaps,
        )

        assembled = self.assembler.assemble(qb.get("query", ""), qb.get("topics", []), top_k=50)

        re_ranked = self.ranker.rank(assembled, qb.get("topics", []), candidate_profile, limit=top_k)

        # Build final chunks output, preserving traceability
        chunks_out = []
        for c in re_ranked:
            chunks_out.append(
                {
                    "id": c.get("id"),
                    "text": c.get("text"),
                    "source": c.get("source"),
                    "page": c.get("page"),
                    "score": float(c.get("score", 0.0)),
                    "relevance": float(c.get("relevance", 0.0)),
                    "overlap": float(c.get("overlap", 0.0)),
                }
            )

        result = {
            "trace_id": trace_id,
            "query": qb.get("query", ""),
            "topics": qb.get("topics", []),
            "chunks": chunks_out,
        }

        return result


__all__ = ["QueryBuilder", "ContextAssembler", "ContextRanker", "Retriever"]
