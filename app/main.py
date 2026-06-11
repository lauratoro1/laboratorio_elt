"""
Main application entry point for Rick & Morty ETL Lab.
Includes lifespan management, middleware, exception handlers, and logging.
"""
import time
import platform
import logging
from contextlib import asynccontextmanager
from sqlalchemy import inspect, text

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.exceptions import StarletteHTTPException
from fastapi.responses import JSONResponse

from app.controllers import etl_controller, analitica_controller
from app.database import mysql_engine, mongo_collection
from app.config import Config

# =================== LOGGING CONFIGURATION ===================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# =================== TABLE MANAGEMENT ===================
def ensure_table_exists():
    """
    Creates the table ONLY if it doesn't exist.
    Uses SQLAlchemy inspector to check existence.
    Table: personajes_master (Rick & Morty characters)
    """
    from sqlalchemy import inspect
    
    inspector = inspect(mysql_engine)
    table_name = "personajes_master"
    
    if not inspector.has_table(table_name):
        logger.info(f"Creating {table_name} table...")
        with mysql_engine.connect() as conn:
            with conn.begin():
                conn.execute(text(f"""
                    CREATE TABLE {table_name} (
                        id_personaje INT PRIMARY KEY,
                        nombre VARCHAR(150) NOT NULL,
                        estado VARCHAR(20),
                        especie VARCHAR(50),
                        genero VARCHAR(20),
                        tipo VARCHAR(100),
                        origen_nombre VARCHAR(100),
                        ubicacion_nombre VARCHAR(100),
                        total_episodios INT DEFAULT 0,
                        tiene_tipo_especial BOOLEAN DEFAULT FALSE,
                        fecha_extraccion DATE,
                        is_active BOOLEAN DEFAULT TRUE,
                        last_updated DATETIME,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                conn.execute(text(f"""
                    CREATE INDEX idx_estado ON {table_name}(estado);
                    CREATE INDEX idx_especie ON {table_name}(especie);
                    CREATE INDEX idx_genero ON {table_name}(genero);
                """))
        logger.info(f"Table '{table_name}' created successfully with indexes!")
    else:
        logger.info(f"Table '{table_name}' already exists. No action taken.")


# =================== LIFESPAN MANAGEMENT ===================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles the application lifecycle.
    - Startup: Creates table if needed, logs configuration
    - Shutdown: Cleans up connections
    """
    logger.info("=" * 60)
    logger.info("Starting ETL Lab - Rick & Morty API Application...")
    logger.info(f"MongoDB Database: {Config.MONGO_DB}")
    logger.info(f"MongoDB Collection: {mongo_collection.name}")
    logger.info(f"MySQL Database: {Config.MYSQL_DB}")
    logger.info(f"MySQL Table: personajes_master")
    logger.info(f"API Source: {Config.RICK_MORTY_API_BASE_URL}")
    logger.info("=" * 60)
    
    ensure_table_exists()
    
    yield
    
    logger.info("Shutting down ETL Lab application...")
    logger.info("Closing database connections...")
    mysql_engine.dispose()
    logger.info("Shutdown complete.")