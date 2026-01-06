import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

_client = MongoClient(os.environ["MONGODB_URI"])
_db = _client["smart_resume"]
_jobs = _db["jobs"]

def match_jobs(resume_embedding: list[float], limit: int = 5, num_candidates: int = 100):
    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "embedding",
                "queryVector": resume_embedding,
                "numCandidates": num_candidates,
                "limit": limit
            }
        },
        {
            "$project": {
                "_id": 1,
                "title": 1,
                "company": 1,
                "description": 1,
                "location": 1,
                "score": {"$meta": "vectorSearchScore"}
            }
        }
    ]
    return list(_jobs.aggregate(pipeline))
