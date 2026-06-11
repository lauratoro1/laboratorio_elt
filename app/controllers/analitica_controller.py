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

@router.get("/profile/{id}")
async def dual_profile(id: int):
    """
    Endpoint E: Dual Profile
    """
    result = analitica_service.get_dual_profile(id)
    
    if result is None:
        raise HTTPException(
            status_code=404, 
            detail=f"Record with ID {id} not found in any database"
        )
    
    return result

@router.get("/analytics/summary")
async def get_summary_statistics():
    """Get summary statistics"""
    return analitica_service.get_summary_statistics()