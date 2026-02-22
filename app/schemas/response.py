from pydantic import BaseModel
from typing import Any, Dict, List, Optional

class AtifJSON(BaseModel):
    kaynak_turu: str  # "kanun" | "ictihat"
    kanun_veya_daire: str
    esas_no: Optional[str] = None
    karar_no: Optional[str] = None
    tarih: Optional[str] = None
    madde_no: Optional[str] = None
    ozet: Optional[str] = None
    alinti: str
    kaynak_kimlik: str

class AnalyzeResponse(BaseModel):
    case_type: str  # "ozel" | "ceza"
    decision_text: str
    citations: List[AtifJSON] = []
    scores: Dict[str, Any] = {}
    warnings: List[str] = []