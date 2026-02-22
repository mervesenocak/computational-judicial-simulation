from __future__ import annotations
from dataclasses import dataclass
from typing import List, Set

from app.schemas.dava import DavaGirdisi

@dataclass
class UnsurKalemi:
    unsur: str
    durum: str  # "SAĞLANDI" | "SAĞLANAMADI" | "VERİ YOK"
    aciklama: str

@dataclass
class TazminatKarari:
    hukum: str  # "KABUL" | "RED" | "KISMEN KABUL" | "KARAR VERİLEMEDİ (VERİ YOK)"
    kalemler: List[UnsurKalemi]
    gerekce_maddeleri: List[str]

def _metin_birlestir(dava: DavaGirdisi) -> str:
    return " ".join(
        [
            dava.olay_ozeti or "",
            " ".join(dava.talepler or []),
            " ".join(dava.deliller or []),
            dava.ek_bilgiler or "",
        ]
    ).lower()

def _sinyal_seti(metin: str) -> Set[str]:
    s: Set[str] = set()

    # Tazminat unsurları sinyalleri
    if any(k in metin for k in ["hukuka aykırı", "hukuka aykir", "haksız", "haksiz"]):
        s.add("hukuka_aykirilik")
    if any(k in metin for k in ["kusur", "ihmal", "dikkatsiz", "kasten", "kasıt", "taksir"]):
        s.add("kusur")
    if any(k in metin for k in ["zarar", "hasar", "maddi zarar", "manevi", "yaralan", "ölüm", "tedavi"]):
        s.add("zarar")
    if any(k in metin for k in ["illiyet", "nedensellik", "sebep-sonuç", "sebep sonuç", "bağlantı"]):
        s.add("illiyet")

    # Delil sinyalleri
    if any(k in metin for k in ["bilirkişi", "rapor", "ekspertiz"]):
        s.add("bilirkisi")
    if any(k in metin for k in ["kamera", "video", "görüntü", "goruntu"]):
        s.add("kamera")
    if any(k in metin for k in ["tanık", "tanik"]):
        s.add("tanik")
    if any(k in metin for k in ["tutanak"]):
        s.add("tutanak")

    return s

def _delil_gucu(sinyaller: Set[str]) -> str:
    # deterministik basit sınıflama (portföy seviyesi)
    guclu = any(k in sinyaller for k in ["bilirkisi", "kamera", "tutanak"])
    orta = "tanik" in sinyaller
    if guclu:
        return "GÜÇLÜ"
    if orta:
        return "ORTA"
    return "ZAYIF"

def tazminat_karar_uret(dava: DavaGirdisi, kaynak_var: bool) -> TazminatKarari:
    """
    Kaynak (kanun/içtihat) yoksa:
      - Özel hukukta atıfsız kesin hüküm kurulmaz -> KARAR VERİLEMEDİ (VERİ YOK)
    Kaynak varsa:
      - Unsur checklist: hukuka aykırılık, kusur, zarar, illiyet
      - Eksik unsur -> RED
      - Unsurlar var ama delil zayıf -> KISMEN KABUL (miktar/illiyet tartışmalı)
      - Hepsi tamam + delil güçlü/orta -> KABUL
    """
    metin = _metin_birlestir(dava)
    sinyaller = _sinyal_seti(metin)
    delil = _delil_gucu(sinyaller)

    kalemler: List[UnsurKalemi] = []
    gerekce: List[str] = []

    # 1) Kaynak kontrolü (audit kuralı)
    if not kaynak_var:
        kalemler = [
            UnsurKalemi("Hukuka Aykırılık", "VERİ YOK", "Mevzuat/emsal veri tabanında bulunamadı."),
            UnsurKalemi("Kusur", "VERİ YOK", "Mevzuat/emsal veri tabanında bulunamadı."),
            UnsurKalemi("Zarar", "VERİ YOK", "Mevzuat/emsal veri tabanında bulunamadı."),
            UnsurKalemi("İlliyet Bağı", "VERİ YOK", "Mevzuat/emsal veri tabanında bulunamadı."),
        ]
        gerekce.append("1) Veri tabanında placeholder olmayan mevzuat/ictihat bulunamadığından atıf üretilememiştir.")
        gerekce.append("2) Özel hukukta, dayanak gösterilemeyen bir değerlendirme ile kesin hüküm kurulamaz.")
        gerekce.append("3) Bu nedenle yalnızca genel çerçeve sunulmuş, hüküm tesis edilememiştir.")
        return TazminatKarari("KARAR VERİLEMEDİ (VERİ YOK)", kalemler, gerekce)

    # 2) Unsurlar (deterministik)
    def unsur_ekle(ad: str, anahtar: str, acik: str) -> bool:
        var = anahtar in sinyaller
        kalemler.append(
            UnsurKalemi(
                ad,
                "SAĞLANDI" if var else "SAĞLANAMADI",
                acik if var else "Metinde bu unsur yönünde yeterli belirti tespit edilemedi.",
            )
        )
        return var

    hukuka_ayk = unsur_ekle("Hukuka Aykırılık", "hukuka_aykirilik", "Metinde hukuka aykırılık/haksızlık yönünde belirti var.")
    kusur = unsur_ekle("Kusur", "kusur", "Metinde kusur (kasıt/taksir/ihmal) yönünde belirti var.")
    zarar = unsur_ekle("Zarar", "zarar", "Metinde zarar (maddi/manevi) yönünde belirti var.")
    illiyet = unsur_ekle("İlliyet Bağı", "illiyet", "Metinde nedensellik/illiyet yönünde belirti var.")

    gerekce.append(f"1) Olay özeti: {dava.olay_ozeti or '(girilmedi)'}")
    gerekce.append(f"2) Talepler: {', '.join(dava.talepler or []) or '(girilmedi)'}")
    gerekce.append(f"3) Deliller: {', '.join(dava.deliller or []) or '(girilmedi)'}")
    gerekce.append(f"4) Delil gücü (heuristic): {delil}")

    # 3) Hüküm mantığı
    if not (hukuka_ayk and kusur and zarar and illiyet):
        gerekce.append("5) Tazminat sorumluluğu unsurlarından en az biri sağlanamadığından talep RED yönünde değerlendirilmiştir.")
        return TazminatKarari("RED", kalemler, gerekce)

    if delil == "ZAYIF":
        gerekce.append("5) Unsurlar metinden anlaşılsa da delil gücü zayıf göründüğünden miktar/illiyet bakımından tam kanaat oluşmamıştır.")
        gerekce.append("6) Bu nedenle KISMEN KABUL (veya ek delil/bilirkişi gerekliliği) yönünde değerlendirilmiştir.")
        return TazminatKarari("KISMEN KABUL", kalemler, gerekce)

    gerekce.append("5) Unsurların tamamı sağlandığından ve delil gücü yeterli göründüğünden KABUL yönünde değerlendirilmiştir.")
    return TazminatKarari("KABUL", kalemler, gerekce)