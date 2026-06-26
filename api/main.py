from __future__ import annotations
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings
from api.middleware.auth_middleware import AuthMiddleware
from api.middleware.error_handler import exception_handlers
from api.routers.v1 import (
    families, members, checkins, health_records,
    medications, documents, consultations, escalations,
    timeline, memory, internal
)

app = FastAPI(
    title="MantraOne API",
    version=settings.app_version,
    description="Longitudinal Family Health Memory System",
    exception_handlers=exception_handlers,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuthMiddleware)

@app.get("/health")
async def health_check():
    return {"status": "ok", "version": settings.app_version}

app.include_router(families.router, prefix="/v1/families", tags=["Families"])
app.include_router(members.router, prefix="/v1/members", tags=["Members"])
app.include_router(checkins.router, prefix="/v1/checkins", tags=["Checkins"])
app.include_router(health_records.router, prefix="/v1/health-records", tags=["Health Records"])
app.include_router(medications.router, prefix="/v1/medications", tags=["Medications"])
app.include_router(documents.router, prefix="/v1/documents", tags=["Documents"])
app.include_router(consultations.router, prefix="/v1/consultations", tags=["Consultations"])
app.include_router(escalations.router, prefix="/v1/escalations", tags=["Escalations"])
app.include_router(timeline.router, prefix="/v1/timeline", tags=["Timeline"])
app.include_router(memory.router, prefix="/v1/memory", tags=["Memory"])
app.include_router(internal.router, prefix="/v1/internal", tags=["Internal"])
