from __future__ import annotations

import re
from typing import List, Tuple, Optional
from datetime import date

from app.schemas.dava import DavaGirdisi, Taraf


def _temizle(s: str) -> str:
    s = (s or "").replace("\x00", " ").strip()
    s = re.sub(r"\s+", " ", s)
    return s


def _liste_bul(metin: str, anahtarlar: List[str]) -> List[str]:
    """
    Metinde anahtar kelimeler geçiyorsa "sinyal" olarak listeler.
    (Deterministik ve basit.)
    """
    metin_l = metin.lower()
    out: List[str] = []
    for a in anahtarlar:
        if a.lower() in metin_l:
            out.append(a)
    return out


def _dava_turu_tahmin(metin: str) -> Tuple[str, List[str]]:
    """
    Çok basit ve deterministik sınıflama:
    - 'sanık', 'katılan', 'tck', 'hagb', 'beraat' -> ceza
    - 'davacı', 'davalı', 'tbk', 'tazminat', 'alacak', 'kira' -> ozel
    """
    w: List[str] = []
    t = metin.lower()

    ceza_sinyal = sum(1 for k in ["sanık", "katılan", "tck", "hagb", "beraat", "mahkumiyet", "iddianame"] if k in t)
    ozel_sinyal = sum(1 for k in ["davacı", "davalı", "tbk", "tazminat", "alacak", "kira", "sözleşme", "icra"] if k in t)

    if ceza_sinyal > ozel_sinyal:
        return "ceza", w
    if ozel_sinyal > ceza_sinyal:
        return "ozel", w

    w.append("Dava türü metinden net anlaşılamadı; varsayılan 'ozel' seçildi.")
    return "ozel", w


def _taraflari_cek(metin: str) -> Tuple[List[Taraf], List[str]]:
    """
    Çok basit regex: 'Davacı: X', 'Davalı: Y', 'Sanık: Z', 'Katılan: T'
    Bulamazsa boş döner.
    """
    warnings: List[str] = []
    taraflar: List[Taraf] = []
    patterns = [
        ("davacı", r"(?:davacı|davaci)\s*[:\-]\s*(.+)"),
        ("davalı", r"(?:davalı|davali)\s*[:\-]\s*(.+)"),
        ("sanık", r"(?:sanık|sanik)\s*[:\-]\s*(.+)"),
        ("katılan", r"(?:katılan|katilan)\s*[:\-]\s*(.+)"),
    ]

    for rol, pat in patterns:
        m = re.search(pat, metin, flags=re.IGNORECASE)
        if m:
            isim = _temizle(m.group(1))
            # isim çok uzunsa kırp
            isim = isim[:80]
            taraflar.append(Taraf(rol=rol, isim=isim))

    if not taraflar:
        warnings.append("Taraflar metinden otomatik çıkarılamadı (Davacı/Davalı/Sanık/Katılan etiketleri bulunamadı).")

    return taraflar, warnings


def metinden_dava_girdisi_uret(metin: str, dava_turu_override: Optional[str] = None) -> Tuple[DavaGirdisi, List[str]]:
    """
    Upload metninden DavaGirdisi üretir. (Best-effort, deterministik.)
    """
    warnings: List[str] = []
    metin = _temizle(metin)

    dava_turu, w1 = _dava_turu_tahmin(metin)
    warnings.extend(w1)

    if dava_turu_override in ("ozel", "ceza"):
        dava_turu = dava_turu_override
        warnings.append(f"Dava türü kullanıcı seçimine göre '{dava_turu_override}' olarak zorlandı.")

    taraflar, w2 = _taraflari_cek(metin)
    warnings.extend(w2)

    # talepler/deliller için sinyal sözlükleri (genişletilebilir)
    ozel_talepler = _liste_bul(metin, ["maddi tazminat", "manevi tazminat", "alacak", "kira", "itirazın iptali"])
    ceza_talepler = _liste_bul(metin, ["hagb", "erteleme", "beraat", "ceza verilmesine yer olmadığı", "indirim"])

    deliller = _liste_bul(metin, ["tanık", "kamera", "dekont", "bilirkişi", "rapor", "whatsapp", "sms", "hts", "dna"])

    talepler = ozel_talepler if dava_turu == "ozel" else ceza_talepler

    # olay_ozeti: metnin ilk kısmını kısa özet gibi kullan
    olay_ozeti = metin[:1200]
    if len(metin) > 1200:
        warnings.append("Olay özeti otomatik çıkarıldı (metin uzun olduğu için ilk 1200 karakter alındı).")

    dava = DavaGirdisi(
        dava_turu=dava_turu,
        olay_ozeti=olay_ozeti,
        taraflar=taraflar or None,
        talepler=talepler or None,
        deliller=deliller or None,
        tarih=str(date.today()),
        ek_bilgiler=None,
    )

    return dava, warnings