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