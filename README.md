# 🛸 TokenWise / Kuiper 7-Layer Intelligent AI Router

TokenWise is a high-performance, cost-optimizing, 7-layer intelligent routing architecture designed to resolve incoming queries at the fastest, lowest-cost local layer possible before cascading to premium Large Language Models (Groq / Google Gemini).

---

## 🏛️ 7-Layer Cascade Architecture

```
                                  [ User Query ]
                                         │
                                         ▼
                 ┌───────────────────────────────────────────────┐
                 │    Layer 0A: Symbolic & Numerical Handler     │ ──▶ Instant Exact Hit (0.5ms)
                 │    (SymPy, Unit Conversions, Physics, Math)   │
                 └───────────────────────┬───────────────────────┘
                                         │ Pass
                                         ▼
                 ┌───────────────────────────────────────────────┐
                 │     Layer 0B: General Knowledge Resolver      │ ──▶ Encyclopedia / DDG (Free)
                 │     (Wikipedia API, DuckDuckGo Knowledge)     │
                 └───────────────────────┬───────────────────────┘
                                         │ Pass
                                         ▼
                 ┌───────────────────────────────────────────────┐
                 │       Layer 1: TinyML Domain Classifier       │ ──▶ Keyword Support Intent
                 │     (Domain matching & lightweight rules)     │
                 └───────────────────────┬───────────────────────┘
                                         │ Pass
                                         ▼
                 ┌───────────────────────────────────────────────┐
                 │       Layer 2: MinHash LSH Cache Engine       │ ──▶ Jaccard Near-Duplicates (< 3ms)
                 │     (Code Skeletons, Gotchas, Learned Traces) │
                 └───────────────────────┬───────────────────────┘
                                         │ Pass
                                         ▼
                 ┌───────────────────────────────────────────────┐
                 │    Layer 3: Semantic Vector Embedder (MiniLM) │ ──▶ Cosine Similarity Match
                 │    (SentenceTransformer 'all-MiniLM-L6-v2')   │
                 └───────────────────────┬───────────────────────┘
                                         │ Pass
                                         ▼
                 ┌───────────────────────────────────────────────┐
                 │    Layer 4: Tri-Model Ensemble ML (α-Tuned)   │ ──▶ Consensus Tri-Vote
                 │    (Logistic Regression + MLP + LightGBM)     │
                 └───────────────────────┬───────────────────────┘
                                         │ Pass
                                         ▼
                 ┌───────────────────────────────────────────────┐
                 │     Layer 5: Intelligent Auto-LLM Cascade     │ ──▶ Full Deep Reasoning Answer
                 │     (Groq GPT OSS 120B / Gemini 3.5 Flash)    │     + Auto-learn trace to L2/L3
                 └───────────────────────────────────────────────┘
```

---

## 🏆 Highest-Level Benchmark Scorecard (100 / 100)

| Layer | Domain | Latency | Cost |
| :--- | :--- | :--- | :--- |
| **Layer 0A** | Symbolic Math (`sin^2 + cos^2 = 1`, `sinx/cosx = tan(x)`, conversions) | **~5ms** | **$0.00** |
| **Layer 0B** | Encyclopedic & Bio Lookups (Wikipedia, DDG) | **~1500ms** | **$0.00** |
| **Layer 1** | Customer Support Classifiers (Shipping, Billing, Refunds) | **~3ms** | **$0.00** |
| **Layer 2** | Code Structures & Boilerplates (C++, Java, Python, Rust, Go, HTML) | **~3ms** | **$0.00** |
| **Layer 3** | Semantic Paraphrasing & Vector Lookups | **~4ms** | **$0.00** |
| **Layer 4** | Ensemble ML Consensus Voting with Dynamic Alpha ($\alpha$) | **~4ms** | **$0.00** |
| **Layer 5** | Deep Multi-Model LLM Generation (Groq 120B, Gemini Flash) | **~4800ms** | **~$0.0001** |
| **Throughput** | 20 Concurrent Burst Requests | **85.7ms avg** | **100% OK** |

---

## 🚀 Quickstart Guide

### 1. Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt  # fastapi uvicorn sentence-transformers scikit-learn lightgbm sympy wikipedia-api ddgs python-dotenv requests
cp .env.example .env
# Add your GROQ_API_KEY and GEMINI_API_KEY to backend/.env
python3 main.py
```
Backend API will be active at: `http://127.0.0.1:8000`

### 2. Frontend Setup

```bash
npm install
npm start
```
Frontend UI will be active at: `http://localhost:3000`

### 3. Run Benchmark Suite

```bash
python3 backend/benchmark_suite.py
```

---

## 📡 API Endpoints

- `GET /` — API status & available providers
- `GET /health` — Health check
- `GET /stats` — Real-time query counts, savings metrics, and dynamic alpha
- `POST /query` — Route user query through 7 layers:
  ```json
  {
    "query": "give me the code structure of c++",
    "provider": "auto"
  }
  ```

---

## 📄 License
MIT
