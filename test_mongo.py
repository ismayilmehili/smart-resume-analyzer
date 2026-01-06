import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
client = MongoClient(os.environ["MONGODB_URI"])

col = client["ai_db"]["documents"]
col.insert_one({"text": "Hello from Python!", "embedding": [0, 0, 0]})
print("OK ✅ docs:", col.count_documents({}))
