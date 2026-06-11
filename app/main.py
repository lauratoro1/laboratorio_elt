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

# =================== FASTAPI APPLICATION ===================
app = FastAPI(
    title="ETL Lab - Rick & Morty API",
    description="""
    ETL Pipeline with FastAPI, MongoDB and MySQL

    Implemented Features:
    - Idempotent extraction from Rick & Morty API to MongoDB
    - Pandas transformation (flattening nested JSONs)
    - Idempotent MySQL loading with ON DUPLICATE KEY UPDATE
    - Dynamic type detection in column analysis
    - Dual Profile (MongoDB + MySQL with aligned PK)
    - Reset with TRUNCATE (not DROP)
    - 11 columns in MySQL (exceeds minimum of 8)
    """,
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    debug=False
)


# =================== MIDDLEWARES ===================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "0.0.0.0"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware to log all HTTP requests."""
    start_time = time.time()
    
    logger.debug(f"-> {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    
    log_level = logging.INFO if response.status_code < 400 else logging.WARNING
    logger.log(
        log_level, 
        f"{request.method} {request.url.path} - {response.status_code} - {duration:.3f}s"
    )
    
    response.headers["X-Response-Time"] = f"{duration:.3f}s"
    response.headers["X-Service-Version"] = app.version
    
    return response

# =================== EXCEPTION HANDLERS ===================

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handler for HTTP exceptions (400, 404, etc.)"""
    logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail} - Path: {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global handler for unhandled exceptions."""
    logger.critical(f"Unhandled exception: {type(exc).__name__} - {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": str(exc) if app.debug else "An unexpected error occurred. Please contact support.",
            "path": request.url.path,
            "method": request.method
        }
    )


# =================== ROUTERS ===================
app.include_router(etl_controller.router)
app.include_router(analitica_controller.router)