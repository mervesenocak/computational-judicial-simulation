from pydantic import BaseModel
from typing import List, Optional

class Taraf(BaseModel):
    rol: str
    isim: str

class DavaGirdisi(BaseModel):
    dava_turu: str  # "ozel" | "ceza"
    olay_ozeti: str
    taraflar: Optional[List[Taraf]] = []
    talepler: Optional[List[str]] = []
    deliller: Optional[List[str]] = []
    tarih: Optional[str] = None
    ek_bilgiler: Optional[str] = None