from __future__ import annotations
from functools import lru_cache
from typing import List
from sentence_transformers import SentenceTransformer

@lru_cache(maxsize=1)
def _get_model():
    return SentenceTransformer("all-MiniLM-L6-v2")  # 384 dims

def create_embedding(text: str) -> List[float]:
    text = (text or "").strip()
    if not text:
        return []
    return _get_model().encode(text).tolist()
