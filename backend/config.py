import os
from dotenv import load_dotenv

# loads .env from project root (current working directory)
load_dotenv()

MONGODB_URI = (os.getenv("MONGODB_URI") or "").strip()
if not MONGODB_URI:
    raise RuntimeError("MONGODB_URI missing in .env")

DB_NAME = (os.getenv("MONGO_DB") or "smart_resume").strip()
VECTOR_INDEX_NAME = (os.getenv("VECTOR_INDEX_NAME") or "vector_index").strip()

GEMINI_API_KEY = (os.getenv("GEMINI_API_KEY") or "").strip()
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY missing in .env")

GEMINI_MODEL = (os.getenv("GEMINI_MODEL") or "gemini-2.5-flash").strip()

# Optional, only needed if you ever run frontend separately.
CORS_ORIGINS = [o.strip() for o in (os.getenv("CORS_ORIGINS") or "*").split(",") if o.strip()]
