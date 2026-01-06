import time
from google import genai
from backend.config import GEMINI_API_KEY, GEMINI_MODEL

client = genai.Client(api_key=GEMINI_API_KEY)

def call_llm(user_message: str, context: str) -> str:
    prompt = f"""
You are a helpful assistant.
Answer using the context below.

Context:
{context}

User question:
{user_message}
""".strip()

    for attempt in range(3):
        try:
            resp = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
            )
            return (resp.text or "").strip()
        except Exception as e:
            msg = str(e)
            if "RESOURCE_EXHAUSTED" in msg or "429" in msg:
                if attempt < 2:
                    time.sleep(2)
                    continue
                return "⚠️ Gemini API quota/rate limit reached. Please try later."
            return f"⚠️ LLM error: {msg}"
