from __future__ import annotations
from typing import List

def chunk_text(text: str, max_chars: int = 900, overlap: int = 150) -> List[str]:
    text = (text or "").strip()
    if not text:
        return []

    chunks: List[str] = []
    start = 0
    n = len(text)

    while start < n:
        end = min(start + max_chars, n)
        slice_ = text[start:end]

        cut = max(slice_.rfind("\n\n"), slice_.rfind("\n"), slice_.rfind(". "))
        if cut > 200:
            end = start + cut + 1

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= n:
            break
        start = max(0, end - overlap)

    deduped, seen = [], set()
    for c in chunks:
        key = c[:120]
        if key not in seen:
            seen.add(key)
            deduped.append(c)

    return deduped
