from __future__ import annotations
import re
from dataclasses import dataclass
from typing import List, Tuple

from sqlalchemy.orm import Session
from rank_bm25 import BM25Okapi

from app.db.models import KanunMaddesi, Ictihat


def _tokenize(text: str) -> List[str]:
    text = (text or "").lower()
    text = re.sub(r"[^a-zçğıöşü0-9\s]", " ", text, flags=re.IGNORECASE)
    toks = [t for t in text.split() if len(t) >= 2]
    return toks


def _anahtar_kavramlar(text: str) -> List[str]:
    # deterministik, “zamanaşımı/sözleşme/tanık/dekont” gibi kelimeleri özellikle yakalar
    oncelikli = ["zamanaşımı", "zamanasimi", "sözleşme", "sozlesme", "tanık", "tanik", "dekont", "banka", "ödeme", "odeme"]
    text_l = (text or "").lower()
    sec = [k for k in oncelikli if k in text_l]
    # ek olarak en çok geçen bazı tokenlar
    toks = _tokenize(text_l)
    # çok kısa olmayan ve sayısal olmayanlardan en sık geçen 8’i al
    frek: dict[str, int] = {}
    for t in toks:
        if t.isdigit():
            continue
        frek[t] = frek.get(t, 0) + 1
    ek = [t for t, _ in sorted(frek.items(), key=lambda x: x[1], reverse=True)[:8]]
    out = []
    for x in (sec + ek):
        if x not in out:
            out.append(x)
    return out[:12]


@dataclass
class KanunHit:
    id: int
    kaynak_kimlik: str
    kanun_adi: str
    madde_no: str
    madde_metni: str
    score: float


@dataclass
class IctihatHit:
    id: int
    kaynak_kimlik: str
    daire: str
    esas_no: str
    karar_no: str
    tarih: str
    ozet: str
    metin_kisa: str
    score: float


def kanun_ara(db: Session, query_text: str, limit: int = 5) -> List[KanunHit]:
    # placeholder olmayanları al
    rows = db.query(KanunMaddesi).filter(KanunMaddesi.is_placeholder == False).all()  # noqa: E712
    if not rows:
        return []

    docs = [_tokenize(f"{r.kanun_adi} {r.madde_no} {r.madde_metni}") for r in rows]
    bm25 = BM25Okapi(docs)

    q = " ".join(_anahtar_kavramlar(query_text))
    qtok = _tokenize(q)
    scores = bm25.get_scores(qtok)

    ranked = sorted(list(enumerate(scores)), key=lambda x: x[1], reverse=True)[:limit]
    out: List[KanunHit] = []
    for idx, sc in ranked:
        r = rows[idx]
        out.append(
            KanunHit(
                id=r.id,
                kaynak_kimlik=r.kaynak_kimlik,
                kanun_adi=r.kanun_adi,
                madde_no=r.madde_no,
                madde_metni=r.madde_metni,
                score=float(sc),
            )
        )
    return out


def ictihat_ara(db: Session, query_text: str, limit: int = 5) -> List[IctihatHit]:
    rows = db.query(Ictihat).filter(Ictihat.is_placeholder == False).all()  # noqa: E712
    if not rows:
        return []

    docs = [_tokenize(f"{r.daire} {r.esas_no} {r.karar_no} {r.ozet} {r.metin_kisa}") for r in rows]
    bm25 = BM25Okapi(docs)

    q = " ".join(_anahtar_kavramlar(query_text))
    qtok = _tokenize(q)
    scores = bm25.get_scores(qtok)

    ranked = sorted(list(enumerate(scores)), key=lambda x: x[1], reverse=True)[:limit]
    out: List[IctihatHit] = []
    for idx, sc in ranked:
        r = rows[idx]
        out.append(
            IctihatHit(
                id=r.id,
                kaynak_kimlik=r.kaynak_kimlik,
                daire=r.daire,
                esas_no=r.esas_no,
                karar_no=r.karar_no,
                tarih=r.tarih,
                ozet=r.ozet,
                metin_kisa=r.metin_kisa,
                score=float(sc),
            )
        )
    return out


def kaynaklari_getir(db: Session, dava_metin: str) -> Tuple[List[KanunHit], List[IctihatHit]]:
    return kanun_ara(db, dava_metin, limit=5), ictihat_ara(db, dava_metin, limit=5)