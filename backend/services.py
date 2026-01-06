from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from backend.db import col
from backend.config import VECTOR_INDEX_NAME
from backend.chunking import chunk_text
from backend.embeddings import create_embedding

USER_ID_DEFAULT = "default"

def _utcnow() -> datetime:
    return datetime.now(timezone.utc)

def replace_cv(cv_text: str, user_id: str = USER_ID_DEFAULT) -> Dict[str, Any]:
    resume_chunks = col("resume_chunks")
    state = col("state")

    chunks = chunk_text(cv_text)
    del_res = resume_chunks.delete_many({"user_id": user_id})

    docs: List[Dict[str, Any]] = []
    now = _utcnow()
    for i, ch in enumerate(chunks, start=1):
        emb = create_embedding(ch)
        if not emb:
            continue
        docs.append({"user_id": user_id, "chunk_id": i, "text": ch, "embedding": emb, "created_at": now})

    if docs:
        resume_chunks.insert_many(docs)

    state.update_one(
        {"user_id": user_id},
        {"$set": {"resume_text": cv_text, "resume_updated_at": now}},
        upsert=True,
    )

    return {"deleted": del_res.deleted_count, "inserted": len(docs), "chunks": len(chunks)}

def replace_job_description(jd_text: str, user_id: str = USER_ID_DEFAULT) -> Dict[str, Any]:
    jd_chunks = col("jd_chunks")
    state = col("state")

    chunks = chunk_text(jd_text)
    del_res = jd_chunks.delete_many({"user_id": user_id})

    docs: List[Dict[str, Any]] = []
    now = _utcnow()
    for i, ch in enumerate(chunks, start=1):
        emb = create_embedding(ch)
        if not emb:
            continue
        docs.append({"user_id": user_id, "chunk_id": i, "text": ch, "embedding": emb, "created_at": now})

    if docs:
        jd_chunks.insert_many(docs)

    state.update_one(
        {"user_id": user_id},
        {"$set": {"jd_text": jd_text, "jd_updated_at": now}},
        upsert=True,
    )

    return {"deleted": del_res.deleted_count, "inserted": len(docs), "chunks": len(chunks)}

def get_resume_text(user_id: str = USER_ID_DEFAULT) -> str:
    s = col("state").find_one({"user_id": user_id}) or {}
    return (s.get("resume_text") or "").strip()

def get_jd_text(user_id: str = USER_ID_DEFAULT) -> str:
    s = col("state").find_one({"user_id": user_id}) or {}
    return (s.get("jd_text") or "").strip()

def vector_search(
    collection_name: str,
    query: str,
    filter_doc: Dict[str, Any],
    limit: int = 4,
    num_candidates: int = 120,
) -> List[Dict[str, Any]]:
    qvec = create_embedding(query)
    if not qvec:
        return []

    c = col(collection_name)

    pipeline = [
        {
            "$vectorSearch": {
                "index": VECTOR_INDEX_NAME,
                "path": "embedding",
                "queryVector": qvec,
                "numCandidates": num_candidates,
                "limit": max(limit * 4, 20),
            }
        },
        {"$match": filter_doc},
        {"$limit": limit},
        {"$project": {"_id": 0, "text": 1, "chunk_id": 1, "score": {"$meta": "vectorSearchScore"}}},
    ]

    return list(c.aggregate(pipeline))
