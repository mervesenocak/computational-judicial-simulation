from __future__ import annotations

import traceback

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse

from app.api.routes import router

# ✅ DB: modelleri yükle + tabloları oluştur
from app.db.base import Base
from app.db.session import engine, SessionLocal
import app.db.models  # noqa: F401  (tabloların tanınması için import şart)

# ✅ Seed (DB boşsa demo verisi ekle)
from app.db.seed import seed_if_empty

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

# ✅ Uygulama açılırken tablolar yoksa oluştur + DB boşsa seed bas
@app.on_event("startup")
def on_startup():
    # 1) tablolar
    Base.metadata.create_all(bind=engine)

    # 2) seed (db boşsa birkaç demo kayıt ekle)
    db = SessionLocal()
    try:
        seed_if_empty(db)
    finally:
        db.close()

# ✅ Tüm beklenmeyen hataları JSON olarak döndür (UI res.json patlamasın)
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal Server Error",
            "error": str(exc),
            "path": str(request.url),
        },
    )

# routes.py içindeki path'ler /web, /analyze... şeklinde (başında /api OLMAMALI)
app.include_router(router, prefix="/api")

@app.get("/", include_in_schema=False)
def root():
    # Live demo için ana sayfayı web arayüzüne yönlendir
    return RedirectResponse(url="/api/web")