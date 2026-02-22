import json
import glob
from pathlib import Path
from sqlalchemy.orm import Session

from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.db.models import KanunMaddesi, Ictihat

PROJE_KOK = Path(__file__).resolve().parents[1]
DATA_LAWS = PROJE_KOK / "data" / "laws"
DATA_CASELAW = PROJE_KOK / "data" / "case_law"


def _json_yukle(dosya_yolu: Path):
    with open(dosya_yolu, "r", encoding="utf-8") as f:
        return json.load(f)


def _kanun_ingest(db: Session):
    dosyalar = sorted(glob.glob(str(DATA_LAWS / "*.json")))
    sayac = 0

    for fp in dosyalar:
        kayitlar = _json_yukle(Path(fp))

        if not isinstance(kayitlar, list):
            continue

        for k in kayitlar:
            kimlik = k["kaynak_kimlik"]

            var_mi = db.query(KanunMaddesi).filter(
                KanunMaddesi.kaynak_kimlik == kimlik
            ).first()

            if var_mi:
                continue

            db.add(
                KanunMaddesi(
                    kaynak_kimlik=kimlik,
                    kanun_adi=k["kanun_adi"],
                    madde_no=k["madde_no"],
                    madde_metni=k["madde_metni"],
                    yururluk_notu=k.get("yururluk_notu"),
                    is_placeholder=bool(k.get("is_placeholder", False)),
                )
            )
            sayac += 1

    return sayac


def _ictihat_ingest(db: Session):
    dosyalar = sorted(glob.glob(str(DATA_CASELAW / "*.json")))
    sayac = 0

    for fp in dosyalar:
        kayitlar = _json_yukle(Path(fp))

        if not isinstance(kayitlar, list):
            continue

        for k in kayitlar:
            kimlik = k["kaynak_kimlik"]

            var_mi = db.query(Ictihat).filter(
                Ictihat.kaynak_kimlik == kimlik
            ).first()

            if var_mi:
                continue

            db.add(
                Ictihat(
                    kaynak_kimlik=kimlik,
                    daire=k["daire"],
                    esas_no=k["esas_no"],
                    karar_no=k["karar_no"],
                    tarih=k["tarih"],
                    ozet=k["ozet"],
                    ilgili_maddeler=json.dumps(
                        k.get("ilgili_maddeler", []), ensure_ascii=False
                    ),
                    anahtar_kelimeler=json.dumps(
                        k.get("anahtar_kelimeler", []), ensure_ascii=False
                    ),
                    metin_kisa=k["metin_kisa"],
                    is_placeholder=bool(k.get("is_placeholder", False)),
                )
            )
            sayac += 1

    return sayac


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        k1 = _kanun_ingest(db)
        k2 = _ictihat_ingest(db)
        db.commit()

        print(f"✅ Ingest tamam: {k1} kanun maddesi, {k2} içtihat eklendi.")
        print("ℹ️ Not: is_placeholder=true kayıtlar atıf üretiminde kullanılmayacak.")
    finally:
        db.close()


if __name__ == "__main__":
    main()