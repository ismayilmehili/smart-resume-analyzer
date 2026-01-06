from __future__ import annotations

import os
import tempfile
from flask import Flask, jsonify, render_template, request

from backend.parser import extract_pdf, extract_docx, extract_txt_bytes
from backend.services import (
    USER_ID_DEFAULT,
    replace_cv,
    replace_job_description,
    get_resume_text,
    get_jd_text,
    vector_search,
)
from backend.llm import call_llm
from backend.analysis_logs import save_analysis_log, get_analysis_history

app = Flask(__name__, template_folder="templates", static_folder="static")


@app.get("/")
def root():
    return render_template("index.html")


@app.get("/health")
def health():
    return jsonify({"ok": True, "message": "Flask app is running"})


@app.post("/api/resume/upload")
def upload_resume():
    if "file" not in request.files:
        return jsonify({"ok": False, "error": "No file uploaded"}), 400

    f = request.files["file"]
    filename = (f.filename or "").lower()
    data = f.read()

    if filename.endswith(".pdf"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(data)
            path = tmp.name
        try:
            text = extract_pdf(path)
        finally:
            try:
                os.remove(path)
            except Exception:
                pass
    elif filename.endswith(".docx"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            tmp.write(data)
            path = tmp.name
        try:
            text = extract_docx(path)
        finally:
            try:
                os.remove(path)
            except Exception:
                pass
    else:
        text = extract_txt_bytes(data)

    stats = replace_cv(text, user_id=USER_ID_DEFAULT)
    return jsonify({"ok": True, "stats": stats})


@app.post("/api/jd/update")
def update_jd():
    payload = request.get_json(silent=True) or {}
    jd_text = (payload.get("text") or "").strip()
    stats = replace_job_description(jd_text, user_id=USER_ID_DEFAULT)
    return jsonify({"ok": True, "stats": stats})


@app.post("/api/analyze")
def analyze():
    cv_text = get_resume_text(USER_ID_DEFAULT)
    jd_text = get_jd_text(USER_ID_DEFAULT)

    if not cv_text or not jd_text:
        return jsonify({"ok": False, "error": "Upload CV and update JD first."}), 400

    prompt = f"""
You are an expert HR evaluator.

Compare the RESUME and JOB DESCRIPTION and output a concise report in Markdown.
DO NOT output JSON.

Use this structure exactly:

Match score: <0-100>/100

### Strengths
- ...

### Gaps
- ...

### Suggested resume improvements (rewrite 3–6 bullets)
- ...

RESUME:
{cv_text}

JOB DESCRIPTION:
{jd_text}
""".strip()

    report = call_llm("Write the CV vs JD report now.", prompt)

    save_analysis_log(USER_ID_DEFAULT, jd_text, report)
    return jsonify({"ok": True, "report": report})


@app.get("/api/history")
def history():
    items = get_analysis_history(USER_ID_DEFAULT, limit=50)
    for it in items:
        it["_id"] = str(it["_id"])
        if it.get("analysis_time"):
            it["analysis_time"] = it["analysis_time"].isoformat()
    return jsonify({"ok": True, "items": items})
@app.post("/api/history/clear")
def clear_history():
    from backend.analysis_logs import clear_analysis_history
    clear_analysis_history(USER_ID_DEFAULT)
    return jsonify({"ok": True})


@app.post("/api/chat")
def chat():
    payload = request.get_json(silent=True) or {}
    msg = (payload.get("message") or "").strip()
    if not msg:
        return jsonify({"ok": False, "error": "Empty message"}), 400

    # 1) Try vector search
    cv_hits = vector_search("resume_chunks", msg, {"user_id": USER_ID_DEFAULT}, limit=4)
    jd_hits = vector_search("jd_chunks", msg, {"user_id": USER_ID_DEFAULT}, limit=4)

    ctx_parts = []

    if cv_hits:
        ctx_parts.append("CV CONTEXT:\n" + "\n---\n".join(h["text"] for h in cv_hits if h.get("text")))
    if jd_hits:
        ctx_parts.append("JD CONTEXT:\n" + "\n---\n".join(h["text"] for h in jd_hits if h.get("text")))

    context = "\n\n=====\n\n".join(ctx_parts).strip()

    # 2) Fallback if vector search returns nothing
    if not context:
        cv_text = get_resume_text(USER_ID_DEFAULT)
        jd_text = get_jd_text(USER_ID_DEFAULT)

        if not cv_text and not jd_text:
            return jsonify({"ok": True, "reply": "No CV/JD data found yet. Upload CV and update JD first."})

        # keep it short so you don’t burn Gemini quota
        context = f"""
CV (fallback):
{cv_text[:5000]}

JOB DESCRIPTION (fallback):
{jd_text[:5000]}
""".strip()

    reply = call_llm(msg, context)
    return jsonify({"ok": True, "reply": reply})



if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port, debug=True)
