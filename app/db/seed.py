from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models import KanunMaddesi, Ictihat


def seed_if_empty(db: Session) -> None:
    # DB tamamen boşsa (demo için) birkaç kayıt ekleyelim
    kanun_count = db.query(KanunMaddesi).count()
    ictihat_count = db.query(Ictihat).count()

    if kanun_count == 0:
        db.add_all(
            [
                KanunMaddesi(
                    kanun_adi="TBK",
                    madde_no="49",
                    madde_metni="Kusurlu ve hukuka aykırı bir fiille başkasına zarar veren, bu zararı gidermekle yükümlüdür.",
                    yururluk_notu=None,
                    is_placeholder=False,
                    kaynak_kimlik="tbk-49",
                ),
                KanunMaddesi(
                    kanun_adi="TBK",
                    madde_no="58",
                    madde_metni="Kişilik hakkının zedelenmesinden zarar gören, manevi tazminat isteyebilir.",
                    yururluk_notu=None,
                    is_placeholder=False,
                    kaynak_kimlik="tbk-58",
                ),
            ]
        )

    if ictihat_count == 0:
        db.add(
            Ictihat(
                daire="Yargıtay 4. HD (Demo)",
                esas_no="2020/1",
                karar_no="2020/1",
                tarih="2020-01-01",
                ozet="Haksız fiil sorumluluğunda kusur ve illiyet bağı değerlendirmesi.",
                ilgili_maddeler='["tbk-49"]',
                anahtar_kelimeler='["haksız fiil","kusur","illiyet"]',
                metin_kisa="Haksız fiil sorumluluğunda kusur ve illiyet bağı somut olaya göre belirlenir.",
                is_placeholder=False,
                kaynak_kimlik="y4hd-demo-2020-1",
            )
        )

    if kanun_count == 0 or ictihat_count == 0:
        db.commit()