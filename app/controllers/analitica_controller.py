from fastapi import APIRouter, HTTPException, status
from app.services import analitica_service

router = APIRouter(prefix="/api/v1", tags=["Analytics"])

@router.get("/analytics/column/{name}")
async def analyze_column(name: str):
    """
    Endpoint D: Column Analysis
    """
    result = analitica_service.analyze_column(name)
    return result