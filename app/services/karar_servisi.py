from __future__ import annotations
from typing import List, Tuple

from app.schemas.dava import DavaGirdisi
from app.schemas.response import AtifJSON
from app.decision.ozel.tazminat import tazminat_karar_uret
from app.decision.ceza.puanlama import ceza_puanla

# ✅ DB Session + Retrieval (BM25)
from app.db.session import SessionLocal
from app.retrieval.arama import kaynaklari_getir

# ✅ Atıf JSON üretimi (DB'den gelen hit'lerden)
from app.services.atif_uretici import atif_listesi_uret


class KararServisi:
    def __init__(self) -> None:
        pass

    def karar_uret(self, dava: DavaGirdisi) -> Tuple[str, List[AtifJSON], dict, List[str]]:
        """
        Returns:
          decision_text, citations, scores, warnings
        """
        warnings: List[str] = []
        scores: dict = {}

        # ✅ dava metnini birleştir (deterministik)
        dava_metin = " ".join(
            [
                dava.olay_ozeti or "",
                " ".join(dava.talepler or []),
                " ".join(dava.deliller or []),
                dava.ek_bilgiler or "",
            ]
        ).strip()

        # ✅ placeholder olmayan kaynak var mı? BM25 ile ara
        with SessionLocal() as db:
            kanun_hit, ictihat_hit = kaynaklari_getir(db, dava_metin)

        kaynak_var = bool(kanun_hit or ictihat_hit)

        # ✅ citations üret (yalnızca placeholder olmayan hit varsa)
        citations: List[AtifJSON] = atif_listesi_uret(kanun_hit, ictihat_hit) if kaynak_var else []

        if kaynak_var:
            warnings.append(
                f"Kaynak bulundu: {len(kanun_hit)} kanun maddesi, {len(ictihat_hit)} içtihat (placeholder olmayan)."
            )
        else:
            warnings.append("Kaynak bulunamadı (placeholder olmayan kayıt yok). Atıf üretilemez.")

        # -------------------------
        # ÖZEL HUKUK (deterministik)
        # -------------------------
        if dava.dava_turu == "ozel":
            karar = tazminat_karar_uret(dava, kaynak_var=kaynak_var)

            metin: List[str] = []
            metin.append("T.C.\n... MAHKEMESİ\nGEREKÇELİ KARAR TASLAĞI\n")
            metin.append("DAVA: ÖZEL HUKUK (TAZMİNAT - HAKSIZ FİİL)\n")
            metin.append(f"HÜKÜM: {karar.hukum}\n")

            metin.append("GEREKÇE (MADDE MADDE):")
            for i, g in enumerate(karar.gerekce_maddeleri, start=1):
                metin.append(f"{i}) {g}")

            metin.append("\nUNSUR DEĞERLENDİRME TABLOSU:")
            for k in karar.kalemler:
                metin.append(f"- {k.unsur}: {k.durum} | {k.aciklama}")

            # Kaynak varsa kısa listeyi metne de ekleyelim (denetlenebilirlik için)
            if kaynak_var:
                metin.append("\nUYGULANAN MEVZUAT / EMSAL ÖZETİ (DB'den):")
                for c in citations[:8]:
                    if c.kaynak_turu == "kanun":
                        metin.append(f"- {c.kanun_veya_daire} m.{c.madde_no} (kimlik: {c.kaynak_kimlik})")
                    else:
                        metin.append(
                            f"- {c.kanun_veya_daire} E:{c.esas_no} K:{c.karar_no} T:{c.tarih} (kimlik: {c.kaynak_kimlik})"
                        )

            metin.append("\nUyarı: Bu hukuki tavsiye değildir. Eğitim/portföy amaçlı prototiptir.")

            if not kaynak_var:
                warnings.append(
                    "Özel hukuk: Dayanak bulunamadı (placeholder olmayan mevzuat/ictihat yok). "
                    "Bu nedenle hüküm yalnızca genel çerçeve düzeyindedir."
                )

            return "\n".join(metin), citations, scores, warnings

        # -------------------------
        # CEZA HUKUKU (puanlama)
        # -------------------------
        if dava.dava_turu == "ceza":
            sonuc = ceza_puanla(dava)

            scores = {
                "toplam_puan": sonuc.toplam_puan,
                "onerilen_sonuc": sonuc.oneri,
                "kalemler": [k.__dict__ for k in sonuc.kalemler],
            }

            metin: List[str] = []
            metin.append("T.C.\n... MAHKEMESİ\nKARAR ÖNERİSİ (CEZA - PUANLAMA MODELİ)\n")
            metin.append("Not: Bu bir öneridir; nihai karar hâkimin takdirindedir.\n")
            metin.append(f"TOPLAM PUAN: {sonuc.toplam_puan}")
            metin.append(f"ÖNERİ: {sonuc.oneri}\n")

            metin.append("PUAN TABLOSU:")
            for k in sonuc.kalemler:
                metin.append(f"- {k.faktor}: {k.puan} | {k.aciklama}")

            if kaynak_var:
                metin.append("\nMEVZUAT / EMSAL (DB'den bulunanlar):")
                for c in citations[:8]:
                    if c.kaynak_turu == "kanun":
                        metin.append(f"- {c.kanun_veya_daire} m.{c.madde_no} (kimlik: {c.kaynak_kimlik})")
                    else:
                        metin.append(
                            f"- {c.kanun_veya_daire} E:{c.esas_no} K:{c.karar_no} T:{c.tarih} (kimlik: {c.kaynak_kimlik})"
                        )
            else:
                warnings.append(
                    "Ceza için placeholder olmayan mevzuat/ictihat bulunamadı; öneri atıfsızdır (prototip)."
                )

            metin.append("\nUyarı: Bu hukuki tavsiye değildir. Eğitim/portföy amaçlı prototiptir.")
            return "\n".join(metin), citations, scores, warnings

        warnings.append("Geçersiz dava_turu: 'ozel' veya 'ceza' olmalı.")
        return "Geçersiz dava türü.", [], {}, warnings