from datasketch import MinHash, MinHashLSH
import re

# ── WHAT IS MINHASH? ───────────────────────────────────────────
# MinHash converts text into a set of "shingles" (character n-grams)
# then hashes them into a compact signature.
# Two similar texts → similar signatures → fast near-duplicate detection.
# No embeddings, no API calls — pure hashing, microsecond speed.

# ── CONFIG ─────────────────────────────────────────────────────
NUM_PERM       = 128    # number of hash permutations — higher = more accurate
SIMILARITY_THRESHOLD = 0.5   # Jaccard similarity threshold for a cache hit

# ── TEXT → SHINGLES ────────────────────────────────────────────
def get_shingles(text, k=3):
    """Break text into character k-grams (shingles)
    'hello' → {'hel', 'ell', 'llo'}
    """
    text = text.lower().strip()
    # Normalize programming languages and symbols so c++ != c, c# != c
    text = re.sub(r'\bc\+\+\b', 'cpp', text)
    text = re.sub(r'\bc#\b', 'csharp', text)
    text = text.replace('++', 'pp').replace('#', 'sharp')
    text = re.sub(r'[^\w\s]', '', text)
    return set(text[i:i+k] for i in range(len(text) - k + 1))

# ── TEXT → MINHASH SIGNATURE ───────────────────────────────────
def make_minhash(text):
    m = MinHash(num_perm=NUM_PERM)
    for shingle in get_shingles(text):
        m.update(shingle.encode('utf8'))
    return m

# ── THE CACHE ──────────────────────────────────────────────────
class MinHashCache:
    def __init__(self):
        # LSH = Locality Sensitive Hashing
        # Groups similar MinHash signatures into the same "bucket"
        # Makes search O(1) instead of comparing against every cached item
        self.lsh   = MinHashLSH(threshold=SIMILARITY_THRESHOLD, num_perm=NUM_PERM)
        self.store = {}   # key → (minhash, label, embedding)
        self.counter = 0

    def add(self, text, label, embedding=None):
        """Add a query + its label to the cache"""
        key = f"q_{self.counter}"
        self.counter += 1
        m = make_minhash(text)
        self.lsh.insert(key, m)
        self.store[key] = {
            "text":      text,
            "label":     label,
            "embedding": embedding,
            "minhash":   m
        }
        return key

    def search(self, text):
        """Check if a near-duplicate exists in cache"""
        m       = make_minhash(text)
        results = self.lsh.query(m)

        if not results:
            return None   # cache miss → pass to embedder

        # Pick the most similar result
        best_key  = None
        best_sim  = 0
        for key in results:
            sim = m.jaccard(self.store[key]["minhash"])
            if sim > best_sim:
                best_sim = sim
                best_key = key

        if best_key:
            return {
                "text":       self.store[best_key]["text"],
                "label":      self.store[best_key]["label"],
                "embedding":  self.store[best_key]["embedding"],
                "similarity": round(best_sim, 3),
                "cache_hit":  True
            }
        return None

# ── TEST ───────────────────────────────────────────────────────
if __name__ == "__main__":
    cache = MinHashCache()

    # Simulate past queries already seen and cached
    print("📦 Building cache with past queries...\n")
    past_queries = [
        ("where is my package",        "shipping_query"),
        ("i was billed two times",      "payment_issue"),
        ("cancel my subscription",      "cancellation"),
        ("give me my money back",       "refund_request"),
        ("update my delivery address",  "address_update"),
        ("track my order please",       "shipping_query"),
        ("my payment failed",           "payment_issue"),
    ]
    for text, label in past_queries:
        cache.add(text, label)
        print(f"  Cached: '{text}' → {label}")

    # Now test with NEW incoming queries
    print("\n🔍 Testing cache lookups:\n")
    new_queries = [
        "where is my package?",          # near-duplicate → HIT ✅
        "whre is my pakage",              # typo → HIT ✅
        "i was charged twice",            # similar meaning → HIT ✅
        "please cancel my subscription",  # slight variation → HIT ✅
        "the quantum flux is unstable",   # completely different → MISS ❓
        "where is my order",              # close but different word → depends
        "refund my money",                # similar to refund → HIT ✅
    ]

    for query in new_queries:
        result = cache.search(query)
        if result:
            print(f"  ✅ CACHE HIT: '{query}'")
            print(f"     Matched: '{result['text']}'")
            print(f"     Label:   {result['label']}")
            print(f"     Similarity: {result['similarity']}\n")
        else:
            print(f"  ❓ CACHE MISS: '{query}'")
            print(f"     → Pass to Embedder\n")