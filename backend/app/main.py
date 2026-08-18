from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import (
    health,
    candidates,
    resume,
    roles,
    interview_sessions,
    auth,
)
from app.api.routes import interviews
from app.db.database import init_db
from app.middleware.rate_limiter import SimpleRateLimiterMiddleware

app = FastAPI(title=settings.APP_NAME)


@app.get("/")
def root():
    return {
        "message": "🤖 Candidate Screening AI Backend",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }


# CORS
origins = (
    [o.strip() for o in settings.CORS_ALLOW_ORIGINS.split(",")]
    if settings.CORS_ALLOW_ORIGINS
    else ["*"]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# simple rate limiter
app.add_middleware(
    SimpleRateLimiterMiddleware,
    max_requests=settings.RATE_LIMIT_REQUESTS,
    window_seconds=settings.RATE_LIMIT_WINDOW,
)

app.include_router(health.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(candidates.router, prefix="/api")
app.include_router(resume.router, prefix="/api")
app.include_router(roles.router, prefix="/api")
app.include_router(interview_sessions.router, prefix="/api")
app.include_router(interviews.router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    init_db()
