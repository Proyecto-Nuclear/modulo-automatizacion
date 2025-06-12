from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api import router

app = FastAPI(
    title="Modulo Automatización",
    description="Modulo de automatización para la gestion de procesos",
    version="0.0.1",
)

app.include_router(router, prefix="/api/v1", tags=["horarios"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)