from fastapi import APIRouter
from app.api.v1 import beams, sections

api_router = APIRouter()
api_router.include_router(beams.router)
api_router.include_router(sections.router)
