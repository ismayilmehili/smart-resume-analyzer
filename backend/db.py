import certifi
from pymongo import MongoClient
from backend.config import MONGODB_URI, DB_NAME

_client = MongoClient(
    MONGODB_URI,
    tls=True,
    tlsCAFile=certifi.where(),
    serverSelectionTimeoutMS=30000,
)

_db = _client[DB_NAME]

def col(name: str):
    return _db[name]
