from __future__ import annotations

from dataclasses import dataclass
from typing import List
import re

from app.schemas.dava import DavaGirdisi


@dataclass
class PuanKalemi:
    faktor: str
    puan: int
    aciklama: str


@dataclass
class CezaPuanSonucu:
    toplam_puan: int
    oneri: str
    kalemler: List[PuanKalemi]


def _var_mi(metin: str, kelimeler: List[str]) -> bool:
    t = metin.lower()
    return any(k.lower() in t for k in kelimeler)


def _say(metin: str, kelimeler: List[str]) -> int:
    t = metin.lower()
    return sum(1 for k in kelimeler if k.lower() in t)


def ceza_puanla(dava: DavaGirdisi) -> CezaPuanSonucu:
    """
    NOT: Bu puanlama bir 'karar destek/öneri' modelidir.
    Hukuki yorum değildir; deterministik heuristik sinyaller kullanır.
    """
    metin = " ".join(
        [
            dava.olay_ozeti or "",
            " ".join(dava.talepler or []),
            " ".join(dava.deliller or []),
            dava.ek_bilgiler or "",
        ]
    ).strip()
    t = metin.lower()

    kalemler: List[PuanKalemi] = []

    # 1) DELİL GÜCÜ (0-40)
    # objektif/teknik deliller ağırlıklı
    obj = _say(t, ["kamera", "cd", "video", "ses kaydı", "hts", "dna", "parmak izi", "bilirkişi", "rapor", "tutanak"])
    tanik = _say(t, ["tanık", "tanik", "beyan", "görgü"])
    ikrar = 1 if _var_mi(t, ["ikrar", "itiraf", "kabul etti"]) else 0
    celiski = 1 if _var_mi(t, ["çelişki", "celiski", "şüphe", "suphe"]) else 0

    delil_puan = min(40, obj * 10 + tanik * 6 + ikrar * 8 - celiski * 10)
    delil_puan = max(0, delil_puan)
    kalemler.append(
        PuanKalemi(
            "Delil gücü",
            delil_puan,
            f"Objektif={obj}, Tanık={tanik}, İkrar={ikrar}, Şüphe/çelişki={celiski}",
        )
    )

    # 2) MANEVİ UNSUR (-10..+10)
    # kast sinyali +, taksir sinyali -
    kast = 1 if _var_mi(t, ["kasten", "kast", "bilerek", "isteyerek"]) else 0
    taksir = 1 if _var_mi(t, ["taksir", "dikkatsizlik", "ihmal"]) else 0
    manevi = 0
    if kast and not taksir:
        manevi = 10
        ac = "Kast sinyali bulundu."
    elif taksir and not kast:
        manevi = -5
        ac = "Taksir/ihmal sinyali bulundu."
    else:
        ac = "Kast/taksir sinyali net değil."
    kalemler.append(PuanKalemi("Manevi unsur (kast/taksir)", manevi, ac))

    # 3) AĞIRLAŞTIRICILAR (0..35)
    agir = 0
    # daha akademik görünen kurum sinyalleri
    if _var_mi(t, ["silah", "bıçak", "tabanca"]):
        agir += 10
    if _var_mi(t, ["birden fazla", "birden çok", "topluca", "grup"]):
        agir += 6  # iştirak/çoklu fail sinyali
    if _var_mi(t, ["zincirleme", "müteaddit", "tekrar"]):
        agir += 6
    if _var_mi(t, ["planlı", "tasarlayarak"]):
        agir += 8
    if _var_mi(t, ["ağır yaralanma", "hayati tehlike", "kırık", "kalıcı iz"]):
        agir += 8

    agir = min(35, agir)
    kalemler.append(PuanKalemi("Ağırlaştırıcılar", agir, "Metindeki ağırlaştırıcı sinyallerin toplamı."))

    # 4) HAFİFLETİCİLER (0..35) -> negatif uygulanır
    haf = 0
    if _var_mi(t, ["etkin pişmanlık", "etkin pismanlik"]):
        haf += 12
    if _var_mi(t, ["zararı giderdi", "zarari giderdi", "zarar giderildi", "tazmin etti", "ödedi", "odedi"]):
        haf += 10
    if _var_mi(t, ["sabıkasız", "sabikasiz", "ilk kez", "adli sicil kaydı yok"]):
        haf += 6
    if _var_mi(t, ["iyi hal", "iyi hâl", "pişman", "pism an", "özür", "ozur"]):
        haf += 5
    if _var_mi(t, ["teşebbüs", "tesebbus"]):
        haf += 4  # teşebbüs sinyali bazen daha düşük yoğunluk gösterebilir (heuristik)

    haf = min(35, haf)
    kalemler.append(PuanKalemi("Hafifleticiler", -haf, "Metindeki hafifletici sinyallerin toplamı (negatif)."))

    # TOPLAM
    toplam = delil_puan + manevi + agir - haf

    # ÖNERİ HARİTASI (deterministik)
    if delil_puan < 10:
        oneri = "DELİL ZAYIF: beraat/şüpheden sanık yararlanır değerlendirmesi (öneri)"
    elif toplam <= 10:
        oneri = "DÜŞÜK YOĞUNLUK: ceza verilmesine yer olmadığı / düşük yaptırım ihtimali (öneri)"
    elif toplam <= 25:
        oneri = "ORTA YOĞUNLUK: temel ceza + lehe değerlendirmeler (HAGB/erteleme şartları araştırılabilir) (öneri)"
    else:
        oneri = "YÜKSEK YOĞUNLUK: mahkumiyet eğilimi (indirime/kurumlara göre değişir) (öneri)"

    return CezaPuanSonucu(toplam_puan=toplam, oneri=oneri, kalemler=kalemler)