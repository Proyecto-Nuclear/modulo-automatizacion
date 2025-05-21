from fastapi import FastAPI
from .api import router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Modulo Automatización",
    description="Modulo de automatización para la gestion de procesos",
    version="0.0.1",
)

app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)