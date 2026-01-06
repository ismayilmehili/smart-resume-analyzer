# 🧠 Smart Resume Analyzer + AI Job Matcher (MVP)

A modern AI-driven web app that helps job seekers:
- upload a CV (PDF/DOCX/TXT),
- paste a Job Description,
- run an AI Job-Fit analysis (CV vs JD),
- chat with an assistant grounded in your CV + JD,
- and keep a history of past analyses in MongoDB.

This is an MVP built with **Flask + MongoDB Atlas (Vector Search) + Gemini + Sentence-Transformers**.

---

## ✨ Features

✅ **Upload CV** (PDF/DOCX/TXT)  
- Extracts text
- Chunks it
- Generates embeddings
- Saves to MongoDB (overwrites previous CV)

✅ **Paste Job Description**  
- Chunk + embed + store in MongoDB (overwrites previous JD)

✅ **AI Fit Analysis**  
- Generates a friendly CV-vs-JD report (Markdown)
- Saves the result to `analysis_logs` (history)

✅ **History**
- View previous analyses (timestamp + score + JD preview)
- Delete all history (optional)

✅ **Chat (RAG)**
- Ask questions grounded in stored CV + JD chunks
- Uses MongoDB vector search to retrieve relevant context
- Uses Gemini to answer based on that context

---

## 🧱 Tech Stack

- **Backend:** Python, Flask
- **Database:** MongoDB Atlas + Atlas Vector Search
- **Embeddings:** `sentence-transformers` (`all-MiniLM-L6-v2`, 384-dim)
- **LLM:** Google Gemini API (`google-genai`)
- **Frontend:** HTML + CSS + vanilla JS (served by Flask)

---

## 📁 Project Structure (recommended)

smart-resume-analyzer/
├─ app.py # Flask app entrypoint (serves UI + API)
├─ requirements.txt
├─ .env # local only (NOT committed)
├─ backend/
│ ├─ init.py
│ ├─ config.py # reads env vars
│ ├─ db.py # mongo client + helper
│ ├─ embeddings.py # embedding model wrapper
│ ├─ chunking.py # chunking logic
│ ├─ parser.py # PDF/DOCX/TXT extraction
│ ├─ services.py # replace CV/JD + vector search helpers
│ ├─ llm.py # Gemini call with safe error handling
│ ├─ analysis_logs.py # save/load/clear analysis history
├─ templates/
│ └─ index.html # UI page
└─ static/
├─ style.css # UI styling
└─ app.js # UI logic + API calls


> Note: Your actual structure may vary slightly — the key is that Flask looks for `templates/` and `static/` at the project root.

---

## ✅ Prerequisites

- Python 3.10+ (you’re using 3.12)
- MongoDB Atlas cluster
- Atlas **Vector Search index**
- Gemini API key

---

## 🔐 Environment Variables

Create a `.env` file in the project root:

```env
MONGODB_URI="mongodb+srv://<user>:<pass>@<cluster>/<db>?retryWrites=true&w=majority"
MONGO_DB="smart_resume"
VECTOR_INDEX_NAME="vector_index"

GEMINI_API_KEY="YOUR_KEY"
GEMINI_MODEL="gemini-2.5-flash"


🧠 MongoDB Atlas Vector Search Index

Your chunks collections store:

text (string)

embedding (array of floats, 384 dims)

Create a vector index in Atlas Search for each chunk collection you query (example names depend on your code):

resume_chunks

jd_chunks

optionally jobs if you do job retrieval

Vector index basics:

path: embedding

dimensions: 384

similarity: cosine (recommended)

▶️ Run Locally
1) Create and activate a virtual environment
python -m venv ai-env
source ai-env/bin/activate

2) Install dependencies
pip install -r requirements.txt

3) Run the app
python app.py


Open:

http://127.0.0.1:8000

🧪 API Endpoints (MVP)

GET /health → backend status

POST /api/resume/upload → upload CV and replace stored CV chunks

POST /api/jd/update → replace stored JD chunks

POST /api/analyze → AI fit analysis + save to history

GET /api/history → list analysis history

POST /api/history/clear → delete all history

POST /api/chat → chat grounded in CV + JD context

👤 Author

Ismayil Mahili
GitHub: https://github.com/ismayilmehili

LinkedIn: https://linkedin.com/in/ismayil-mahili