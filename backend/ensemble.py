import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import cross_val_score
import lightgbm as lgb
from sentence_transformers import SentenceTransformer

# ── SETUP ──────────────────────────────────────────────────────
print("⚙️  Loading embedding model...")
model     = SentenceTransformer('all-MiniLM-L6-v2')
print("✅ Ready\n")

# ── TRAINING DATA (simulated LLM traces) ───────────────────────
training_data = [
    ("where is my order",               "shipping_query"),
    ("track my package please",         "shipping_query"),
    ("i haven't received my delivery",  "shipping_query"),
    ("when will my order arrive",       "shipping_query"),
    ("has my order been dispatched",    "shipping_query"),
    ("where is my package",             "shipping_query"),
    ("what happened to my shipment",    "shipping_query"),
    ("my parcel hasn't arrived",        "shipping_query"),
    ("i want a refund",                 "refund_request"),
    ("give me my money back",           "refund_request"),
    ("i need to return this item",      "refund_request"),
    ("can i get a refund please",       "refund_request"),
    ("please reimburse me",             "refund_request"),
    ("refund my money",                 "refund_request"),
    ("my payment failed",               "payment_issue"),
    ("i was billed two times",          "payment_issue"),
    ("i was charged twice",             "payment_issue"),
    ("billing problem on my card",      "payment_issue"),
    ("wrong amount on my invoice",      "payment_issue"),
    ("double charge on my account",     "payment_issue"),
    ("cancel my subscription",          "cancellation"),
    ("i want to unsubscribe",           "cancellation"),
    ("please stop my plan",             "cancellation"),
    ("terminate my account",            "cancellation"),
    ("cancel my plan immediately",      "cancellation"),
    ("change my delivery address",      "address_update"),
    ("update my address please",        "address_update"),
    ("new address for my order",        "address_update"),
    ("i moved can you update my address","address_update"),
    ("i need help",                     "general_inquiry"),
    ("how do i reset my password",      "general_inquiry"),
    ("what is your return policy",      "general_inquiry"),
    ("explain how this works",          "general_inquiry"),
]

# ── PREPARE DATA ───────────────────────────────────────────────
print("🔢 Embedding training data...")
texts  = [t for t, _ in training_data]
labels = [l for _, l in training_data]

X  = model.encode(texts)        # shape: (n_samples, 384)
le = LabelEncoder()
y  = le.fit_transform(labels)

print(f"   {len(texts)} training samples, {len(le.classes_)} classes")
print(f"   Classes: {list(le.classes_)}\n")

# ── 3 SURROGATE MODELS ─────────────────────────────────────────
clf1 = LogisticRegression(max_iter=1000, C=1.0)          # fast, linear
clf2 = MLPClassifier(hidden_layer_sizes=(128, 64),        # small neural net
                     max_iter=500, random_state=42)
clf3 = lgb.LGBMClassifier(n_estimators=100,              # gradient boosting
                           random_state=42, verbose=-1)

# ── TRAIN ──────────────────────────────────────────────────────
print("🏋️  Training 3 surrogate models...\n")

clf1.fit(X, y)
print("  ✅ Logistic Regression trained")

clf2.fit(X, y)
print("  ✅ MLP Neural Network trained")

clf3.fit(X, y)
print("  ✅ LightGBM trained")

# ── CROSS VALIDATION SCORES ────────────────────────────────────
print("\n📊 Cross-validation accuracy:\n")
for name, clf in [("LogReg", clf1), ("MLP", clf2), ("LightGBM", clf3)]:
    scores = cross_val_score(clf, X, y, cv=3, scoring='accuracy')
    print(f"  {name}: {scores.mean():.2f} ± {scores.std():.2f}")

# ── ENSEMBLE PREDICT ───────────────────────────────────────────
AGREEMENT_THRESHOLD = 2  # at least 2 out of 3 must agree

def ensemble_predict(text):
    vec   = model.encode([text])
    
    # Each model votes
    pred1 = le.inverse_transform(clf1.predict(vec))[0]
    pred2 = le.inverse_transform(clf2.predict(vec))[0]
    pred3 = le.inverse_transform(clf3.predict(vec))[0]
    
    votes     = [pred1, pred2, pred3]
    vote_set  = set(votes)
    
    # Check agreement
    from collections import Counter
    vote_counts  = Counter(votes)
    top_label, top_count = vote_counts.most_common(1)[0]
    
    # Get confidence from LogReg (most calibrated)
    proba     = clf1.predict_proba(vec)[0]
    max_conf  = float(np.max(proba))

    if top_count >= AGREEMENT_THRESHOLD:
        return {
            "label":      top_label,
            "confidence": round(max_conf, 3),
            "votes":      votes,
            "agreement":  f"{top_count}/3",
            "handled_by": "ensemble",
            "pass_on":    False           # ✅ handled
        }
    else:
        return {
            "label":      None,
            "confidence": round(max_conf, 3),
            "votes":      votes,
            "agreement":  "0/3",
            "handled_by": None,
            "pass_on":    True            # ⬇️ send to LLM
        }

# ── TEST ───────────────────────────────────────────────────────
print("\n\n🔍 Ensemble Predictions:\n")
test_queries = [
    "stop my plan",                   # → cancellation
    "has my parcel arrived yet",      # → shipping_query
    "i got double billed",            # → payment_issue
    "i want to send it back",         # → refund_request
    "the quantum flux is unstable",   # → LLM (unknown)
    "i need help with my account",    # → general_inquiry
    "where did my order go",          # → shipping_query
]

for query in test_queries:
    result = ensemble_predict(query)
    if result["pass_on"]:
        print(f"  ⬆️  '{query}'")
        print(f"     → SEND TO LLM (models disagreed: {result['votes']})\n")
    else:
        print(f"  ✅ '{query}'")
        print(f"     → {result['label']} | {result['agreement']} agree | conf: {result['confidence']}")
        print(f"     Votes: {result['votes']}\n")