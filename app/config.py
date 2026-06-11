import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # MongoDB
    MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
    MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
    MONGO_DB = os.getenv("MONGO_DB", "rickmorty_etl")
    MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "personajes_raw")
    
    # MySQL
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DB = os.getenv("MYSQL_DB", "rickmorty_dw")
    
    # API
    RICK_MORTY_API_BASE_URL = os.getenv("RICK_MORTY_API_BASE_URL", "https://rickandmortyapi.com/api")
    
    @staticmethod
    def get_mongo_uri():
        return f"mongodb://{Config.MONGO_HOST}:{Config.MONGO_PORT}/"
    
    @staticmethod
    def get_mysql_uri():
        return f"mysql+mysqlconnector://{Config.MYSQL_USER}:{Config.MYSQL_PASSWORD}@{Config.MYSQL_HOST}:{Config.MYSQL_PORT}/{Config.MYSQL_DB}"