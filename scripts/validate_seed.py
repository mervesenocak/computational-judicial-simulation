import glob
import json
from pathlib import Path

PROJE_KOK = Path(__file__).resolve().parents[1]
DATA_LAWS = PROJE_KOK / "data" / "laws"
DATA_CASELAW = PROJE_KOK / "data" / "case_law"

YASAK_IFADELER = {"PLACEHOLDER", "DOLDUR", "TBD", "TODO", ""}

def _json_oku(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _kontrol_deger(field: str, val: str, dosya: str, idx: int):
    v = (val or "").strip()
    if v in YASAK_IFADELER:
        raise ValueError(f"[HATA] {dosya} kayit#{idx} alan '{field}' bos/placeholder olamaz (is_placeholder=false).")

def validate():
    # laws
    for fp in sorted(glob.glob(str(DATA_LAWS / "*.json"))):
        kayitlar = _json_oku(Path(fp))
        for i, k in enumerate(kayitlar):
            if bool(k.get("is_placeholder", False)):
                continue
            # is_placeholder=false ise zorunlular dolu olmalı
            _kontrol_deger("kaynak_kimlik", k.get("kaynak_kimlik", ""), fp, i)
            _kontrol_deger("kanun_adi", k.get("kanun_adi", ""), fp, i)
            _kontrol_deger("madde_no", k.get("madde_no", ""), fp, i)
            _kontrol_deger("madde_metni", k.get("madde_metni", ""), fp, i)
            # yururluk_notu opsiyonel ama sahte olmasın
            yn = (k.get("yururluk_notu") or "").strip()
            if yn in {"PLACEHOLDER", "DOLDUR", "TBD", "TODO"}:
                raise ValueError(f"[HATA] {fp} kayit#{i} yururluk_notu placeholder olamaz (opsiyonelse boş bırak).")

    # case law
    for fp in sorted(glob.glob(str(DATA_CASELAW / "*.json"))):
        kayitlar = _json_oku(Path(fp))
        for i, k in enumerate(kayitlar):
            if bool(k.get("is_placeholder", False)):
                continue
            _kontrol_deger("kaynak_kimlik", k.get("kaynak_kimlik", ""), fp, i)
            _kontrol_deger("daire", k.get("daire", ""), fp, i)
            _kontrol_deger("esas_no", k.get("esas_no", ""), fp, i)
            _kontrol_deger("karar_no", k.get("karar_no", ""), fp, i)
            _kontrol_deger("tarih", k.get("tarih", ""), fp, i)
            _kontrol_deger("ozet", k.get("ozet", ""), fp, i)
            _kontrol_deger("metin_kisa", k.get("metin_kisa", ""), fp, i)

    print("✅ Seed doğrulama: OK (is_placeholder=false kayıtlar dolu).")

if __name__ == "__main__":
    validate()