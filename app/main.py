from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI

from app.database import Base, engine, SessionLocal
from app.engine.detector import detect_api_spikes, detect_brute_force, publish_incidents
from app.routers import auth, incidents, logs, webhooks

async def run_detection() -> None:
    db = SessionLocal()
    try:
        incidents_found = detect_brute_force(db) + detect_api_spikes(db)
        await publish_incidents(incidents_found)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(application: FastAPI):
    if getattr(application.state, "testing", False):
        yield
        return

    Base.metadata.create_all(bind=engine)
    scheduler = AsyncIOScheduler()
    scheduler.add_job(run_detection, "interval", seconds=15, id="log-detection")
    scheduler.start()
    try:
        yield
    finally:
        scheduler.shutdown(wait=False)



app = FastAPI(title="LogShield API", version="1.0.0", lifespan=lifespan)
app.include_router(auth.router)
app.include_router(logs.router)
app.include_router(incidents.router)
app.include_router(webhooks.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "LogShield API", "docs": "/docs", "health": "/health"}