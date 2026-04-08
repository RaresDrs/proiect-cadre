from fastapi import APIRouter, HTTPException
from app.schemas.section import SectionInput, SectionResult
from app.services.section_calc import calculate_section_properties

router = APIRouter(prefix="/sections", tags=["sections"])


@router.post("/properties", response_model=SectionResult)
def get_section_properties(data: SectionInput):
    try:
        return calculate_section_properties(data)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
