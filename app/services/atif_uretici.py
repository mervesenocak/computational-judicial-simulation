from __future__ import annotations
from typing import List

from app.schemas.response import AtifJSON
from app.retrieval.arama import KanunHit, IctihatHit


def _alinti_kisalt(text: str, max_len: int = 260) -> str:
    t = (text or "").strip().replace("\n", " ")
    if len(t) <= max_len:
        return t
    return t[: max_len - 3] + "..."


def kanundan_atif(hit: KanunHit) -> AtifJSON:
    # kanun maddesinden kısa alıntı üret
    return AtifJSON(
        kaynak_turu="kanun",
        kanun_veya_daire=hit.kanun_adi,
        esas_no=None,
        karar_no=None,
        tarih=None,
        madde_no=str(hit.madde_no),
        ozet=None,
        alinti=_alinti_kisalt(hit.madde_metni),
        kaynak_kimlik=hit.kaynak_kimlik,
    )


def ictihattan_atif(hit: IctihatHit) -> AtifJSON:
    # içtihattan kısa alıntı üret (özet + kısa metin)
    alinti = hit.ozet or hit.metin_kisa or ""
    return AtifJSON(
        kaynak_turu="ictihat",
        kanun_veya_daire=hit.daire,
        esas_no=hit.esas_no,
        karar_no=hit.karar_no,
        tarih=hit.tarih,
        madde_no=None,
        ozet=_alinti_kisalt(hit.ozet, 240) if hit.ozet else None,
        alinti=_alinti_kisalt(alinti),
        kaynak_kimlik=hit.kaynak_kimlik,
    )


def atif_listesi_uret(kanun_hit: List[KanunHit], ictihat_hit: List[IctihatHit]) -> List[AtifJSON]:
    # sıralı şekilde dön (önce kanun sonra içtihat)
    out: List[AtifJSON] = []
    for h in kanun_hit:
        out.append(kanundan_atif(h))
    for h in ictihat_hit:
        out.append(ictihattan_atif(h))
    return out