import numpy as np
from app.schemas.section import SectionInput, SectionResult


def calculate_section_properties(data: SectionInput) -> SectionResult:
    """
    Calculeaza proprietatile geometrice ale sectiunii transversale.
    Formule extrase din app.py modul Rezistenta Materialelor (liniile 951-1116).
    """
    if data.shape == 'rectangle':
        b, h = data.b, data.h
        A = b * h
        Ix = b * h**3 / 12
        Iy = h * b**3 / 12
        Wx = Ix / (h / 2)
        ix = float(np.sqrt(Ix / A))
        return SectionResult(A=A, Ix=Ix, Iy=Iy, Wx=Wx, ix=ix)

    elif data.shape == 'circle':
        d = data.d
        r = d / 2
        A = float(np.pi * r**2)
        Ix = float(np.pi * d**4 / 64)
        Iy = Ix
        Wx = Ix / r
        ix = d / 4
        Ip = float(np.pi * d**4 / 32)
        return SectionResult(A=A, Ix=Ix, Iy=Iy, Wx=Wx, ix=ix, Ip=Ip)

    elif data.shape == 'hollow_circle':
        d, di = data.d, data.d_inner
        A = float(np.pi * (d**2 - di**2) / 4)
        Ix = float(np.pi * (d**4 - di**4) / 64)
        Iy = Ix
        Wx = Ix / (d / 2)
        ix = float(np.sqrt(Ix / A))
        Ip = float(np.pi * (d**4 - di**4) / 32)
        return SectionResult(A=A, Ix=Ix, Iy=Iy, Wx=Wx, ix=ix, Ip=Ip)

    else:
        raise ValueError(f"Forma sectiunii '{data.shape}' nu este implementata inca")
