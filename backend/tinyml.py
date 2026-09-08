import re

# ── KEYWORD MAP — precise domain-specific triggers ─────────────
KEYWORD_MAP = {
    "shipping_query":  ["order status", "my order", "my package", "track order", "track package", "delivery status", "shipment", "parcel arrive", "order dispatched", "shipping delay"],
    "refund_request":  ["refund", "money back", "return item", "reimburse", "give back money", "return product", "chargeback"],
    "payment_issue":   ["payment failed", "charged twice", "double billed", "billing issue", "wrong invoice", "card declined", "overcharged", "unauthorized charge"],
    "cancellation":    ["cancel subscription", "cancel my plan", "unsubscribe", "terminate account", "stop subscription", "close my account", "cancel membership"],
    "address_update":  ["delivery address", "shipping address", "change address", "update address", "wrong address", "new address for order"],
    "general_inquiry": ["customer support", "support agent", "talk to human", "contact helpdesk", "customer service", "speak to representative"],
}

# Individual strong keywords with word boundary checks
STRONG_KEYWORDS = {
    "shipping_query":  ["tracking", "courier", "dispatch", "shipment", "parcel"],
    "refund_request":  ["refund", "reimburse", "reimbursement"],
    "payment_issue":   ["overcharged", "double-billed", "overbilling"],
    "cancellation":    ["unsubscribe", "cancellation"],
    "address_update":  [],
    "general_inquiry": ["helpdesk"],
}

CONFIDENCE_THRESHOLD = 0.25

# ── SCORING ────────────────────────────────────────────────────
def extract_scores(text):
    t = text.lower().strip()
    scores = {}
    
    for category, phrases in KEYWORD_MAP.items():
        matched_count = 0
        for phrase in phrases:
            if phrase in t:
                matched_count += 1
        
        # Check strong singular keywords
        for sk in STRONG_KEYWORDS.get(category, []):
            if re.search(rf'\b{re.escape(sk)}\b', t):
                matched_count += 1.5

        scores[category] = matched_count / (len(phrases) * 0.5)

    return scores

# ── PREDICT ────────────────────────────────────────────────────
def predict(text):
    t = text.lower().strip()
    
    # Don't classify math, science, programming, or factual question patterns as TinyML customer queries
    if re.search(r'\b(sin|cos|tan|sqrt|log|matrix|integral|derivative|equation|theorem|python|javascript|code|algorithm|who is|who was|capital of|when was|what is the speed of)\b', t):
        return {
            "label":      None,
            "confidence": 0.0,
            "handled_by": None,
            "pass_on":    True
        }

    scores = extract_scores(t)
    best_label  = max(scores, key=scores.get)
    best_score  = scores[best_label]
    sorted_vals = sorted(scores.values(), reverse=True)
    second_best = sorted_vals[1] if len(sorted_vals) > 1 else 0
    margin      = best_score - second_best

    if best_score >= CONFIDENCE_THRESHOLD and margin > 0.05:
        return {
            "label":      best_label,
            "confidence": round(min(best_score, 1.0), 3),
            "handled_by": "tinyml",
            "pass_on":    False
        }
    else:
        return {
            "label":      None,
            "confidence": round(best_score, 3),
            "handled_by": None,
            "pass_on":    True
        }

# ── TEST ───────────────────────────────────────────────────────
if __name__ == "__main__":
    test_queries = [
        "where is my package",            # → shipping_query   ✅
        "i was charged twice",             # → payment_issue    ✅
        "cancel my plan immediately",      # → cancellation     ✅
        "the quantum flux is unstable",    # → pass on          ❓
        "what is sinx/cosx",               # → pass on to math  ❓
        "who was Isaac Newton",            # → pass on to GK    ❓
        "give me my money back",           # → refund_request   ✅
        "update my delivery address",      # → address_update   ✅
        "track my order please",           # → shipping_query   ✅
        "write a python quicksort",        # → pass on to LLM   ❓
    ]

    print("🔍 TinyML Predictions:\n")
    for query in test_queries:
        result = predict(query)
        if result["pass_on"]:
            print(f"  ❓ '{query}' -> PASS ON")
        else:
            print(f"  ✅ '{query}' -> {result['label']} (conf: {result['confidence']})")