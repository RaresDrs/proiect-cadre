from pydantic import BaseModel
from typing import Optional, Literal


class SectionInput(BaseModel):
    shape: Literal['rectangle', 'circle', 'hollow_circle']
    b: Optional[float] = None   # latime (cm)
    h: Optional[float] = None   # inaltime (cm)
    d: Optional[float] = None   # diametru exterior (cm)
    d_inner: Optional[float] = None  # diametru interior pentru inel (cm)


class SectionResult(BaseModel):
    A: float     # arie sectiune (cm2)
    Ix: float    # moment de inertie in raport cu axa x (cm4)
    Iy: float    # moment de inertie in raport cu axa y (cm4)
    Wx: float    # modul de rezistenta la incovoiere (cm3)
    ix: float    # raza de giratie (cm)
    Ip: Optional[float] = None  # moment polar (cm4) — doar pentru cerc
