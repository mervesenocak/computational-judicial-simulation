from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

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


@app.get("/", include_in_schema=False)
def root():
    # Live demo için ana sayfayı web arayüzüne yönlendir
    return RedirectResponse(url="/api/web")