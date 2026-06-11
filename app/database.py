from pymongo import MongoClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import Config

# MongoDB Connection
mongo_client = MongoClient(Config.get_mongo_uri())
mongo_db = mongo_client[Config.MONGO_DB]
mongo_collection = mongo_db[Config.MONGO_COLLECTION]

# MySQL Connection
mysql_engine = create_engine(Config.get_mysql_uri(), echo=False)
MySQLSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=mysql_engine)

def get_mysql_db() -> Session:
    db = MySQLSessionLocal()
    try:
        yield db
    finally:
        db.close()
