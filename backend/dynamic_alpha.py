import time
import random

# ── PRICING TIERS ──────────────────────────────────────────────
# Real OpenAI/LLM baseline pricing per 1k tokens
# α adapts to price: higher price -> lower alpha (more queries handled locally)
PRICE_TIERS = {
    "cheap":    {"max_price": 0.002, "alpha": 0.60, "name": "Cheap",     "color": "#10B981"},
    "normal":   {"max_price": 0.010, "alpha": 0.50, "name": "Normal",    "color": "#3B82F6"},
    "expensive":{"max_price": 0.030, "alpha": 0.35, "name": "Expensive", "color": "#F59E0B"},
    "spike":    {"max_price": float('inf'), "alpha": 0.25, "name": "Spike", "color": "#EF4444"},
}

_last_fetch_time  = 0
_cached_price     = 0.008
CACHE_DURATION    = 60  # refetch every 60 seconds

def fetch_current_price():
    """
    Fetch/simulate current LLM market price per 1000 tokens.
    Cached for 60s.
    """
    global _last_fetch_time, _cached_price

    now = time.time()
    if now - _last_fetch_time < CACHE_DURATION:
        return _cached_price

    base_price   = 0.008
    fluctuation  = random.uniform(-0.004, 0.012)
    _cached_price = round(max(0.001, base_price + fluctuation), 4)
    _last_fetch_time = now

    return _cached_price

def get_alpha():
    """
    Returns current α threshold based on live pricing tier.
    Lower α = local models handle more queries (save more).
    Higher α = stricter confidence threshold.
    """
    price = fetch_current_price()

    for tier_name, tier in PRICE_TIERS.items():
        if price <= tier["max_price"]:
            return {
                "alpha":     tier["alpha"],
                "price":     price,
                "tier":      tier_name,
                "tier_name": tier["name"],
                "color":     tier["color"],
                "reasoning": _explain(tier_name, tier["alpha"], price)
            }

    return {
        "alpha": 0.25,
        "price": price,
        "tier": "spike",
        "tier_name": "Spike",
        "color": "#EF4444",
        "reasoning": f"Price spike (${price}/1k tokens) — maximizing local handling (α=0.25)"
    }

def _explain(tier, alpha, price):
    explanations = {
        "cheap":    f"LLM rates cheap (${price}/1k) → strict threshold (α={alpha}) for maximum accuracy",
        "normal":   f"LLM normal market rate (${price}/1k) → balanced routing (α={alpha})",
        "expensive":f"LLM rates elevated (${price}/1k) → looser threshold (α={alpha}) to save costs",
        "spike":    f"LLM rate spike (${price}/1k) → aggressive local handling (α={alpha})",
    }
    return explanations.get(tier, "")

def should_use_surrogate(confidence, alpha=None):
    """
    Decide whether surrogate confidence is above dynamic alpha bar.
    """
    if alpha is None:
        alpha = get_alpha()["alpha"]
    return confidence >= alpha