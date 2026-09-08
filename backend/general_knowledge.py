import re
import threading
import wikipediaapi
from ddgs import DDGS

# ── SETUP ──────────────────────────────────────────────────────
wiki = wikipediaapi.Wikipedia(
    language='en',
    user_agent='Kuiper-App/1.0'
)

DOMAIN_KEYWORDS = [
    "my package", "my order", "my subscription", "my account",
    "my payment", "my card", "my address", "my delivery",
    "refund", "cancel", "charged", "billed", "return",
    "track", "shipping", "dispatch", "invoice",
    # Technical & Software Engineering
    "code structure", "skeleton", "boilerplate", "syntax",
    "c++", "cpp", "python", "java", "rust", "golang", "html",
    "react", "state", "re-render", "closure", "lambda", "settimeout",
    "sql", "injection", "n+1", "big o", "time complexity", "p vs np",
    "isvalidbst", "binary search tree", "rate limiter", "redis",
    "self-attention", "transformer", "lua", "database query", "cors",
    "fastapi", "express", "orm", "algorithm"
]

GK_TRIGGERS = [
    "what is", "what are", "who is", "who was", "who are",
    "tell me about", "explain", "define", "when was", "when is",
    "where is", "capital of", "founder of", "invented by",
    "what does", "history of", "meaning of",
]

STRIP_PHRASES = [
    "what is", "what are", "who is", "who was", "who are",
    "tell me about", "explain", "define", "what do you know about",
    "what was", "where is", "when was", "when is",
    "give me info on", "information about", "what does",
]

# ── THREAD-BASED TIMEOUT ───────────────────────────────────────
def run_with_timeout(fn, args=(), timeout=6):
    """
    Run fn(*args) in a thread with a timeout.
    Returns result or None if timeout exceeded.
    O(1) overhead.
    """
    result = [None]
    def target():
        try:
            result[0] = fn(*args)
        except Exception:
            pass
    t = threading.Thread(target=target, daemon=True)
    t.start()
    t.join(timeout=timeout)
    return result[0]

# ── QUERY CLEANER ──────────────────────────────────────────────
def clean_query(text):
    t = text.lower().strip().rstrip('?.')
    for phrase in STRIP_PHRASES:
        if t.startswith(phrase):
            t = t[len(phrase):].strip()
    return t

# ── CLASSIFIER ─────────────────────────────────────────────────
def is_general_knowledge(text):
    t = text.lower()
    if any(kw in t for kw in DOMAIN_KEYWORDS):
        return False
    return any(t.startswith(trigger) or trigger in t
               for trigger in GK_TRIGGERS)

# ── WIKIPEDIA ──────────────────────────────────────────────────
def _fetch_wikipedia(query):
    topic = clean_query(query)
    page  = wiki.page(topic)
    if page.exists():
        sentences = page.summary.split('. ')
        return '. '.join(sentences[:2]) + '.'
    return None

# ── DUCKDUCKGO ─────────────────────────────────────────────────
def _fetch_duckduckgo(query):
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=1))
        if results:
            return results[0].get('body', None)
    return None

# ── MAIN HANDLER ───────────────────────────────────────────────
def handle(text):
    if not is_general_knowledge(text):
        return {"answer": None, "handled_by": None, "pass_on": True}

    # Try Wikipedia with 6s timeout
    answer = run_with_timeout(_fetch_wikipedia, args=(text,), timeout=6)
    if answer:
        return {
            "answer":     answer,
            "handled_by": "wikipedia",
            "source":     "Wikipedia",
            "pass_on":    False
        }

    # Try DuckDuckGo with 6s timeout
    answer = run_with_timeout(_fetch_duckduckgo, args=(text,), timeout=6)
    if answer:
        return {
            "answer":     answer,
            "handled_by": "duckduckgo",
            "source":     "DuckDuckGo",
            "pass_on":    False
        }

    # Both failed — pass on
    return {"answer": None, "handled_by": None, "pass_on": True}


# ── TEST ───────────────────────────────────────────────────────
if __name__ == "__main__":
    import time
    test_queries = [
        "what is the meaning of life",
        "who is Elon Musk",
        "what is machine learning",
        "what is photosynthesis",
        "where is my package",
        "cancel my subscription",
    ]

    print("🌐 General Knowledge Handler:\n")
    for query in test_queries:
        print(f"  Query: '{query}'")
        start  = time.time()
        result = handle(query)
        ms     = round((time.time()-start)*1000, 1)
        if result["pass_on"]:
            print(f"  ➡️  PASS ON ({ms}ms)\n")
        else:
            print(f"  ✅ [{result['handled_by']}] {result['answer'][:100]} ({ms}ms)\n")