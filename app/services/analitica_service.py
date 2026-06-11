"""
Analytics Service for the laboratory.
Implements:
- Dynamic column analysis (automatic type detection, NO hardcoding)
- Dual Profile (MongoDB + MySQL with aligned PK)
- Additional analytics: summary statistics, status analysis, species analysis
"""
import pandas as pd
import numpy as np
from sqlalchemy import inspect, text
from app.database import mysql_engine, mongo_collection
from app.models.personajes_sql import PersonajeDB


# =================== COLUMN MAPPING (English to Spanish) ===================
COLUMN_MAPPING = {
    # English (API) -> Spanish (Database)
    "id": "id_personaje",
    "name": "nombre",
    "status": "estado",
    "species": "especie",
    "gender": "genero",
    "type": "tipo",
    "origin": "origen_nombre",
    "location": "ubicacion_nombre",
    "episodes": "total_episodios",
    "total_episodes": "total_episodios",
    "has_special_type": "tiene_tipo_especial",
    "extraction_date": "fecha_extraccion",
    "created_at": "created_at",
    "last_updated": "last_updated",
    "is_active": "is_active"
}


def map_column_to_spanish(column: str) -> str:
    """Map English column name to Spanish database column name."""
    return COLUMN_MAPPING.get(column, column)


def get_sql_columns_info() -> dict:
    """Get metadata of columns from SQL table"""
    inspector = inspect(mysql_engine)
    columns = inspector.get_columns(PersonajeDB.__tablename__)
    return {col["name"]: col for col in columns}


def load_df_from_sql() -> pd.DataFrame:
    """Load entire SQL table as DataFrame for analysis"""
    return pd.read_sql(f"SELECT * FROM {PersonajeDB.__tablename__}", mysql_engine)