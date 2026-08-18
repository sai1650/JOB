"""Ingest documents under ../knowledge_base into per-role vector stores.

Usage:
    python -m scripts.ingest_knowledge_base

This script is idempotent and will skip already-processed files.
"""
import json
import logging
from pathlib import Path
from app.services.kb import (
    DocumentProcessor,
    ChunkingService,
    EmbeddingService,
    VectorStoreService,
    sha256_file,
)
from app.core.roles import ROLES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ingest")


def ingest(root: Path):
    kb_root = root / "knowledge_base"
    if not kb_root.exists():
        logger.info("Creating knowledge base folders")
        for k in ROLES.keys():
            (kb_root / k).mkdir(parents=True, exist_ok=True)

    chunker = ChunkingService()
    embedder = EmbeddingService()

    for role_id in ROLES:
        role_dir = kb_root / role_id
        if not role_dir.exists():
            continue
        index_file = role_dir / "index.json"
        processed = {}
        if index_file.exists():
            processed = json.loads(index_file.read_text())

        files = list(role_dir.glob("**/*"))
        docs = [
            f
            for f in files
            if f.is_file() and f.suffix.lower() in (".pdf", ".txt")
        ]
        logger.info(f"Role {role_id}: found {len(docs)} documents")

        vectors = []
        metadatas = []
        total_pages = 0
        total_chunks = 0
        for doc in docs:
            try:
                h = sha256_file(str(doc))
            except Exception:
                continue
            if processed.get(str(doc)) == h:
                logger.info(f"Skipping already processed {doc}")
                continue

            logger.info(f"Processing {doc}")
            dp = DocumentProcessor(str(doc))
            pages = dp.extract_text()
            total_pages += len(pages)
            chunks = chunker.chunk_pages(pages)
            total_chunks += len(chunks)
            texts = [c["text"] for c in chunks]
            embeddings = embedder.embed(texts)
            for c, emb in zip(chunks, embeddings):
                meta = {
                    "source": str(doc),
                    "page": c.get("page"),
                    "section": None,
                    "role": role_id,
                    "chunk_id": c.get("chunk_id"),
                }
                vectors.append(emb)
                metadatas.append(meta)

            processed[str(doc)] = h

        # persist vectors for role
        if vectors:
            out_index = (root / "data" / f"{role_id}.index")
            vstore = VectorStoreService(str(out_index))
            vstore.persist(vectors, metadatas)
            logger.info(f"Stored {len(vectors)} vectors for role {role_id}")

        # update index file
        index_file.parent.mkdir(parents=True, exist_ok=True)
        index_file.write_text(json.dumps(processed, indent=2))

        logger.info(
            "Role %s: pages=%s chunks=%s embeddings=%s",
            role_id,
            total_pages,
            total_chunks,
            len(vectors),
        )


if __name__ == "__main__":
    base = Path(__file__).resolve().parents[1]
    ingest(base)
