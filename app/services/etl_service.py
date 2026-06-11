"""
ETL Service for Rick & Morty API.
Implements:
- Extraction with idempotency (upsert using original _id)
- Transformation with Pandas (flattening nested JSONs)
- Loading with idempotency (ON DUPLICATE KEY UPDATE)
- Reset with TRUNCATE (no DROP)
"""
import requests
import pandas as pd
from datetime import date
from typing import List, Dict, Any
from sqlalchemy import text

from app.database import mongo_collection, mysql_engine
from app.config import Config
from app.models.personajes_sql import PersonajeDB, Base

# =================== EXTRACTION (MongoDB) ===================

def extract_and_save_raw(quantity: int) -> int:
    """Extracts characters from Rick & Morty API and saves them to MongoDB."""
    if quantity <= 0:
        return 0
        
    saved_records = 0
    characters = _fetch_from_rick_and_morty_api(quantity)
    
    for character in characters:
        character_id = character.get("id")
        if not character_id:
            continue
        
        result = mongo_collection.update_one(
            {"_id": character_id},
            {"$set": character},
            upsert=True
        )
        if result.matched_count > 0 or result.upserted_id:
            saved_records += 1
            
    return saved_records

def _fetch_from_rick_and_morty_api(quantity: int) -> List[Dict[str, Any]]:
    """Handles pagination for Rick & Morty API."""
    all_characters = []
    page = 1
    base_url = f"{Config.RICK_MORTY_API_BASE_URL}/character"
    
    while len(all_characters) < quantity:
        url = f"{base_url}?page={page}"
        
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        items = data.get("results", [])
        if not items:
            break
        
        all_characters.extend(items)
        
        info = data.get("info", {})
        if not info.get("next"):
            break
        
        page += 1
    
    return all_characters[:quantity]

# =================== TRANSFORMATION AND LOADING (MySQL) ===================

def transform_and_load() -> int:
    """Reads from MongoDB, transforms with Pandas and loads to MySQL."""
    raw_data = list(mongo_collection.find({}, {"_id": 0}))
    if not raw_data:
        print("No data in MongoDB. Run /extract first")
        return 0
    
    df = pd.DataFrame(raw_data)
    df = _transform_dataframe(df)
    
    Base.metadata.create_all(bind=mysql_engine)
    
    processed_records = _load_to_mysql_idempotent(df)
    
    return processed_records

def _transform_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Flattens Rick & Morty JSON for SQL."""
    
    direct_columns = {
        "id": "id_personaje",
        "name": "nombre",
        "status": "estado",
        "species": "especie",
        "gender": "genero",
        "type": "tipo"
    }
    
    result_df = pd.DataFrame()
    for source, destination in direct_columns.items():
        if source in df.columns:
            result_df[destination] = df[source]
        else:
            result_df[destination] = None
    
    if "origin" in df.columns:
        result_df["origen_nombre"] = df["origin"].apply(
            lambda x: x.get("name", "Unknown") if isinstance(x, dict) else "Unknown"
        )
    else:
        result_df["origen_nombre"] = "Unknown"
    
    if "location" in df.columns:
        result_df["ubicacion_nombre"] = df["location"].apply(
            lambda x: x.get("name", "Unknown") if isinstance(x, dict) else "Unknown"
        )
    else:
        result_df["ubicacion_nombre"] = "Unknown"
    
    if "episode" in df.columns:
        result_df["total_episodios"] = df["episode"].apply(
            lambda x: len(x) if isinstance(x, list) else 0
        )
    else:
        result_df["total_episodios"] = 0
    
    if "tipo" in result_df.columns:
        result_df["tiene_tipo_especial"] = result_df["tipo"].apply(
            lambda x: bool(x and x.strip()) if pd.notna(x) else False
        )
    else:
        result_df["tiene_tipo_especial"] = False
    
    result_df["fecha_extraccion"] = date.today()
    
    result_df = result_df.fillna({
        "nombre": "Unknown",
        "estado": "unknown",
        "especie": "Unknown",
        "genero": "unknown",
        "tipo": "",
        "origen_nombre": "Unknown",
        "ubicacion_nombre": "Unknown"
    })
    
    return result_df

def _load_to_mysql_idempotent(df: pd.DataFrame) -> int:
    """Loads DataFrame to MySQL using INSERT ... ON DUPLICATE KEY UPDATE."""
    table_name = PersonajeDB.__tablename__
    
    columns = list(df.columns)
    update_columns = [col for col in columns if col != "id_personaje"]
    
    placeholders = ', '.join([f':{col}' for col in columns])
    update_clause = ', '.join([f'{col} = :{col}' for col in update_columns])
    
    final_query = f"""
        INSERT INTO {table_name} ({', '.join(columns)}) 
        VALUES ({placeholders})
        ON DUPLICATE KEY UPDATE {update_clause}
    """
    
    records = 0
    with mysql_engine.connect() as conn:
        for _, row in df.iterrows():
            values = {col: row[col] for col in columns}
            result = conn.execute(text(final_query), values)
            records += 1 if result.rowcount in (1, 2) else 0
        conn.commit()
    
    return records
