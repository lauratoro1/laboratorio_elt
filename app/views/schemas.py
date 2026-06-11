from pydantic import BaseModel


class ExtraerRequest(BaseModel):
    cantidad: int = 20
    
    class Config:
        json_schema_extra = {
            "example": {"cantidad": 50}
        }


class ExtraerResponse(BaseModel):
    mensaje: str
    registros_guardados: int
    fuente: str
    status: int


class TransformarResponse(BaseModel):
    mensaje: str
    registros_procesados: int
    tabla_destino: str
    status: int


class ResetResponse(BaseModel):
    mensaje: str
    mongo_docs_eliminados: int
    mysql_rows_eliminados: int
    status: int