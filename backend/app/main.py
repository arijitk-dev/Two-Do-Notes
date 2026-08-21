import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import accountability, auth, calendar, dashboard, notes, points, reviews, streak, todos
from app.core.config import get_settings
from app.models import note, point_transaction, streak as streak_model, todo, user  # noqa: F401

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)
settings = get_settings()

app = FastAPI(title="Two Do Notes API", version="1.0.0", description="Personal productivity and accountability API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router, prefix="/api/v1")
app.include_router(todos.router, prefix="/api/v1")
app.include_router(notes.router, prefix="/api/v1")
app.include_router(points.router, prefix="/api/v1")
app.include_router(streak.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(calendar.router, prefix="/api/v1")
app.include_router(accountability.router, prefix="/api/v1")
app.include_router(reviews.router, prefix="/api/v1")


@app.get("/health", tags=["system"])
def health():
    return {"status": "ok"}


@app.on_event("startup")
def startup_event():
    logger.info("Two Do Notes API started")
