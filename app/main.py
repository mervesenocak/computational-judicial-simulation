from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router

app = FastAPI(
    title="Hakim Simülasyonu",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# routes.py içindeki path'ler /web, /analyze... şeklinde olmalı (başında /api OLMAMALI)
app.include_router(router, prefix="/api")


@app.get("/")
def root():
    return {
        "ok": True,
        "ui": "http://127.0.0.1:8000/api/web",
        "swagger": "http://127.0.0.1:8000/docs",
        "openapi": "http://127.0.0.1:8000/openapi.json",
    }
def root():
    return {
        "ok": True,
        "ui": "http://127.0.0.1:8000/api/web",
        "swagger": "http://127.0.0.1:8000/docs",
        "openapi": "http://127.0.0.1:8000/openapi.json",
    }