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