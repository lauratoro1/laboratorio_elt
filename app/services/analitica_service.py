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

def analyze_column(column: str) -> dict:
    """
    Dynamic column analysis - AUTOMATIC TYPE DETECTION.
    Accepts English column names (maps to Spanish database columns).
    
    Supports 4 types:
    - Categorical (text with repeated values)
    - Numeric (INT, FLOAT, DECIMAL, etc.)
    - Date (DATE, DATETIME)
    - Boolean (BOOL, BOOLEAN, TINYINT(1))
    """
    # Map English column name to Spanish database column
    db_column = map_column_to_spanish(column)
    
    # Validate column exists
    columns_info = get_sql_columns_info()
    if db_column not in columns_info:
        valid_columns = list(columns_info.keys())
        raise ValueError(f"Column '{column}' (mapped to '{db_column}') does not exist. Valid columns: {valid_columns}")
    
    # Load data
    df = load_df_from_sql()
    
    # Check if dataframe is empty
    if df.empty:
        raise ValueError("No data in the table. Please run /transform first.")
    
    if db_column not in df.columns:
        raise ValueError(f"Column '{db_column}' not found in dataframe")
    
    series = df[db_column]
    sql_type = str(columns_info[db_column]["type"])
    
    nulls = int(series.isna().sum())
    
    # ===== DYNAMIC TYPE DETECTION =====
    
    # 1. Date Type (DATE, DATETIME)
    if "DATE" in sql_type.upper() or "DATETIME" in sql_type.upper():
        series_clean = pd.to_datetime(series, errors='coerce')
        min_val = series_clean.min()
        max_val = series_clean.max()
        range_days = (max_val - min_val).days if pd.notna(min_val) and pd.notna(max_val) else 0
        return {
            "column": column,
            "type": "date",
            "min": str(min_val.date()) if pd.notna(min_val) else None,
            "max": str(max_val.date()) if pd.notna(max_val) else None,
            "range_days": range_days,
            "nulls": nulls
        }
    
    # 2. Boolean Type (BOOL, BOOLEAN, TINYINT(1))
    if "BOOL" in sql_type.upper() or "TINYINT" in sql_type.upper():
        true_count = int(((series == True) | (series == 1)).sum())
        false_count = int(((series == False) | (series == 0)).sum())
        return {
            "column": column,
            "type": "boolean",
            "true": true_count,
            "false": false_count,
            "nulls": nulls
        }
    
    # 3. Numeric Type (INT, FLOAT, DECIMAL, BIGINT)
    numeric_types = ["INT", "FLOAT", "DECIMAL", "BIGINT", "DOUBLE", "NUMERIC"]
    if any(t in sql_type.upper() for t in numeric_types):
        series_num = pd.to_numeric(series, errors='coerce')
        if series_num.isna().all():
            return {
                "column": column,
                "type": "numeric",
                "min": 0,
                "max": 0,
                "mean": 0,
                "median": 0,
                "std_dev": 0,
                "nulls": len(series_num)
            }
        return {
            "column": column,
            "type": "numeric",
            "min": float(series_num.min()),
            "max": float(series_num.max()),
            "mean": float(series_num.mean()),
            "median": float(series_num.median()),
            "std_dev": float(series_num.std()),
            "nulls": int(series_num.isna().sum())
        }
    
    # 4. Default: Categorical (VARCHAR, CHAR, TEXT)
    series_clean = series.dropna()
    
    if len(series_clean) == 0:
        return {
            "column": column,
            "type": "categorical",
            "unique_values": 0,
            "distribution": {},
            "most_common": None,
            "nulls": nulls
        }
    
    unique_values = series_clean.nunique()
    distribution = series_clean.value_counts().head(10).to_dict()
    most_common = str(series_clean.mode()[0]) if not series_clean.mode().empty else "N/A"
    
    return {
        "column": column,
        "type": "categorical",
        "unique_values": int(unique_values),
        "distribution": {str(k): int(v) for k, v in distribution.items()},
        "most_common": most_common,
        "nulls": nulls
    }
def get_dual_profile(character_id: int) -> dict:
    """
    Returns the same record from MongoDB and MySQL.
    Aligned PK: _id in Mongo = id_personaje in MySQL.
    
    Handles 3 cases:
    1. Record in both databases -> 200 OK with both views
    2. Record in only one database -> 200 OK with warning
    3. Record in neither -> None (404)
    """
    result = {
        "id": character_id,
        "mongo_view": None,
        "sql_view": None,
        "warning": None
    }
    
    # 1. Query MongoDB (using _id = character_id)
    mongo_doc = mongo_collection.find_one({"_id": character_id})
    if mongo_doc:
        if "_id" in mongo_doc:
            mongo_doc["_id"] = mongo_doc["_id"]
        result["mongo_view"] = mongo_doc
    
    # 2. Query MySQL
    with mysql_engine.connect() as conn:
        query = text(f"""
            SELECT * FROM {PersonajeDB.__tablename__} 
            WHERE id_personaje = :id
        """)
        db_result = conn.execute(query, {"id": character_id})
        row = db_result.fetchone()
        if row:
            result["sql_view"] = dict(row._mapping)
    
    # 3. Determine warning if inconsistency
    if result["mongo_view"] and not result["sql_view"]:
        result["warning"] = "Record exists in MongoDB but not in MySQL. Possibly /transform has not been executed or the record failed transformation."
    elif not result["mongo_view"] and result["sql_view"]:
        result["warning"] = "Record exists in MySQL but not in MongoDB. Inconsistency in the pipeline."
    elif not result["mongo_view"] and not result["sql_view"]:
        return None
    
    return result
# =================== ADDITIONAL ANALYTICS ===================

def get_summary_statistics() -> dict:
    """
    Service 3: Get comprehensive summary statistics for the entire dataset.
    Returns data with English column names.
    """
    df = load_df_from_sql()
    
    if df.empty:
        return {
            "total_characters": 0,
            "unique_species": 0,
            "unique_statuses": 0,
            "avg_episodes": 0,
            "max_episodes": 0,
            "date_range": {"from": None, "to": None},
            "status_distribution": {},
            "top_species": {}
        }
    
    with mysql_engine.connect() as conn:
        result = conn.execute(text(f"""
            SELECT 
                COUNT(*) as total_characters,
                COUNT(DISTINCT especie) as unique_species,
                COUNT(DISTINCT estado) as unique_statuses,
                AVG(total_episodios) as avg_episodes,
                MAX(total_episodios) as max_episodes,
                MIN(fecha_extraccion) as first_extraction,
                MAX(fecha_extraccion) as last_extraction
            FROM {PersonajeDB.__tablename__}
        """))
        stats = dict(result.fetchone()._mapping)
    
    # Status distribution (convert to English)
    status_dist = df["estado"].value_counts().to_dict()
    
    # Species distribution (top 5)
    species_dist = df["especie"].value_counts().head(5).to_dict()
    
    return {
        "total_characters": stats["total_characters"] or 0,
        "unique_species": stats["unique_species"] or 0,
        "unique_statuses": stats["unique_statuses"] or 0,
        "avg_episodes": round(stats["avg_episodes"], 2) if stats["avg_episodes"] else 0,
        "max_episodes": stats["max_episodes"] or 0,
        "date_range": {
            "from": str(stats["first_extraction"]) if stats["first_extraction"] else None,
            "to": str(stats["last_extraction"]) if stats["last_extraction"] else None
        },
        "status_distribution": {str(k): int(v) for k, v in status_dist.items()},
        "top_species": {str(k): int(v) for k, v in species_dist.items()}
    }
