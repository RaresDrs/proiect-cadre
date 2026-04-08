from pydantic import BaseModel, field_validator
from typing import List, Optional, Dict


class Support(BaseModel):
    x: float       # pozitie pe bara (m) — 0 <= x <= length
    type: int      # 1=articulatie(pin), 2=reazem_mobil(roller), 3=incastrare(fixed)


class PointLoad(BaseModel):
    x: float       # pozitie pe bara (m)
    fx: float = 0.0
    fy: float = 0.0


class BeamInput(BaseModel):
    length: float           # L in metri (> 0)
    angle_deg: float = 0.0  # inclinare bara fata de orizontala (grade)
    supports: List[Support]
    point_loads: List[PointLoad] = []
    distributed_load: float = 0.0   # q uniform (kN/m), pozitiv = in jos
    q_start: float = 0.0            # start pozitie sarcina distribuita (m)
    q_end: Optional[float] = None   # end pozitie (default = length)
    EI: float = 21000.0             # rigiditate la incovoiere (kN*m^2)
    EA: float = 2100000.0           # rigiditate axiala (kN)

    @field_validator('length')
    @classmethod
    def length_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Lungimea barei trebuie sa fie pozitiva')
        return v


class DiagramPoint(BaseModel):
    x: float
    N: float
    V: float
    M: float


class BeamResult(BaseModel):
    reactions: Dict[str, float]    # ex: {"x=0.0_Fy": 50.0, "x=6.0_Fy": 50.0}
    diagrams: List[DiagramPoint]
    max_M: float
    max_V: float
    max_N: float
    deflection: List[Dict[str, float]]  # [{"x": 0.0, "ux": 0.0, "uy": -0.001}]
