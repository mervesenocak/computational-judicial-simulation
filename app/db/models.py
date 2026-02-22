from sqlalchemy import Integer, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class KanunMaddesi(Base):
    __tablename__ = "kanun_maddeleri"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    kanun_adi: Mapped[str] = mapped_column(String(255))
    madde_no: Mapped[str] = mapped_column(String(50))
    madde_metni: Mapped[str] = mapped_column(Text)

    # ✅ ingest.py bunu gönderiyor, o yüzden modelde bulunmalı
    yururluk_notu: Mapped[str | None] = mapped_column(String(255), nullable=True)

    is_placeholder: Mapped[bool] = mapped_column(Boolean, default=False)
    kaynak_kimlik: Mapped[str] = mapped_column(String(255), unique=True)


class Ictihat(Base):
    __tablename__ = "ictihatlar"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    daire: Mapped[str] = mapped_column(String(255))
    esas_no: Mapped[str] = mapped_column(String(100))
    karar_no: Mapped[str] = mapped_column(String(100))
    tarih: Mapped[str] = mapped_column(String(20))

    ozet: Mapped[str] = mapped_column(Text)
    ilgili_maddeler: Mapped[str] = mapped_column(Text)     # JSON string
    anahtar_kelimeler: Mapped[str] = mapped_column(Text)   # JSON string
    metin_kisa: Mapped[str] = mapped_column(Text)

    is_placeholder: Mapped[bool] = mapped_column(Boolean, default=False)
    kaynak_kimlik: Mapped[str] = mapped_column(String(255), unique=True)