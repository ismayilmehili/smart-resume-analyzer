from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from backend.db import col

def _utcnow() -> datetime:
    return datetime.now(timezone.utc)

def parse_match_score(report: str) -> Optional[int]:
    if not report:
        return None
    m = re.search(r"match\s*score\s*:\s*(\d{1,3})", report, re.IGNORECASE)
    if not m:
        m = re.search(r"(\d{1,3})\s*/\s*100", report)
    if not m:
        return None
    score = int(m.group(1))
    return max(0, min(100, score))

def save_analysis_log(user_id: str, jd_text: str, report: str) -> str:
    logs = col("analysis_logs")
    doc: Dict[str, Any] = {
        "user_id": user_id,
        "match_score": parse_match_score(report),
        "jd_preview": (jd_text[:400] if jd_text else ""),
        "report": report,
        "analysis_time": _utcnow(),
    }
    res = logs.insert_one(doc)
    return str(res.inserted_id)

def get_analysis_history(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    logs = col("analysis_logs")
    cursor = (
        logs.find(
            {"user_id": user_id},
            {"report": 1, "match_score": 1, "jd_preview": 1, "analysis_time": 1},
        )
        .sort("analysis_time", -1)
        .limit(limit)
    )
    return list(cursor)
def clear_analysis_history(user_id: str):
    col("analysis_logs").delete_many({"user_id": user_id})
