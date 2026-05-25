from fastapi import FastAPI
from app.config import settings
from app.routers import consumers, readings, reports

app = FastAPI(title=settings.app_title, version=settings.app_version)

app.include_router(consumers.router)
app.include_router(readings.router)
app.include_router(reports.router)


@app.get("/")
async def root():
    return {"message": "HeatAccounting API", "version": settings.app_version}


@app.get("/health")
async def health():
    return {"status": "ok"}
