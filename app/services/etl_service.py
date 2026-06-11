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