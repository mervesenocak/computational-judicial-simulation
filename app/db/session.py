from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.settings import ayarlar

engine = create_engine(
    ayarlar.SQLITE_URL,
    future=True,
    echo=False
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True
)

def db_oturumu():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()