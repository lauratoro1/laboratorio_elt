from fastapi import APIRouter, HTTPException, status
from app.services import etl_service
from app.views.schemas import (
    ExtraerRequest, ExtraerResponse, 
    TransformarResponse, ResetResponse
)

router = APIRouter(prefix="/api/v1/etl", tags=["ETL"])

# Endpoint de debug para ver qué devuelve reset_system
@router.get("/debug-reset")
async def debug_reset():
    """Debug endpoint to see what reset_system returns"""
    try:
        resultado = etl_service.reset_system()
        return {
            "type": str(type(resultado)),
            "keys": list(resultado.keys()) if isinstance(resultado, dict) else "Not a dict",
            "resultado": resultado
        }
    except Exception as e:
        return {
            "error": str(e),
            "type": str(type(e))
        }

@router.post("/extract", response_model=ExtraerResponse, status_code=status.HTTP_201_CREATED)
async def extract_data(request: ExtraerRequest):
    if request.cantidad <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than 0")
    
    registros = etl_service.extract_and_save_raw(request.cantidad)
    
    return ExtraerResponse(
        mensaje="Data extracted successfully",
        registros_guardados=registros,
        fuente="Rick & Morty API",
        status=201
    )
    


