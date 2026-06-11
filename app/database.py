from pymongo import MongoClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import Config

# MongoDB Connection
mongo_client = MongoClient(Config.get_mongo_uri())
mongo_db = mongo_client[Config.MONGO_DB]
mongo_collection = mongo_db[Config.MONGO_COLLECTION]
