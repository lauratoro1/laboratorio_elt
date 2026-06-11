from pydantic import BaseModel
from typing import Optional, Dict, Any

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


class AnalisisCategoricoResponse(BaseModel):
    column: str
    type: str
    unique_values: int
    distribution: Dict[str, int]
    most_common: str
    nulls: int


class AnalisisNumericoResponse(BaseModel):
    column: str
    type: str
    min: float
    max: float
    mean: float
    median: float
    std_dev: float
    nulls: int


class AnalisisFechaResponse(BaseModel):
    column: str
    type: str
    min: str
    max: str
    range_days: int
    nulls: int


class AnalisisBooleanoResponse(BaseModel):
    column: str
    type: str
    true: int
    false: int
    nulls: int


class PerfilDualResponse(BaseModel):
    id: int
    mongo_view: Optional[Dict[str, Any]] = None
    sql_view: Optional[Dict[str, Any]] = None
    warning: Optional[str] = None


class SummaryStatisticsResponse(BaseModel):
    total_characters: int
    unique_species: int
    unique_statuses: int
    avg_episodes: float
    max_episodes: int
    date_range: Dict[str, Optional[str]]
    status_distribution: Dict[str, int]
    top_species: Dict[str, int]


class StatusAnalysisResponse(BaseModel):
    Alive: Dict[str, Any]
    Dead: Dict[str, Any]
    unknown: Dict[str, Any]


class SpeciesAnalysisResponse(BaseModel):
    species: Dict[str, Any]