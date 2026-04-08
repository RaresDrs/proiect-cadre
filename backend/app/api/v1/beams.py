from fastapi import APIRouter, HTTPException
from app.schemas.beam import BeamInput, BeamResult
from app.services.beam_solver import solve_beam

router = APIRouter(prefix="/beams", tags=["beams"])


@router.post("/solve", response_model=BeamResult)
def calculate_beam(data: BeamInput):
    try:
        return solve_beam(data)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))
