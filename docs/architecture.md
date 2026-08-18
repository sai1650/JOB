# Architecture

High-level architecture for Candidate Screening AI:

- frontend: React SPA that communicates with backend via REST APIs.
- backend: FastAPI service responsible for business logic, database access, and future AI integrations.
- db: PostgreSQL for persistence.
- knowledge_base: store for documents and embeddings (planned).

Separation of concerns: API layer, services, repositories, ai modules.
