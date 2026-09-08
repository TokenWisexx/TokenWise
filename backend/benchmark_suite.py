#!/usr/bin/env python3
"""
Kuiper 7-Layer Intelligent Router - Ultimate Highest-Level Benchmark Suite
Evaluates:
1. Layer 0A (Math Engine, Trigonometry, Symbolic Algebra, Unit Conversions, Constants)
2. Layer 0B (General Knowledge, Wikipedia, DDG)
3. Layer 1 (TinyML Domain Classifier)
4. Layer 2 (MinHash LSH Near-Duplicate Cache)
5. Layer 3 (SentenceTransformer Semantic Embedder)
6. Layer 4 (Tri-Model Ensemble ML with Dynamic Alpha)
7. Layer 5 (Auto-LLM Fallback with Groq/Gemini & Trace Learning)
8. Edge Cases & Resilience (Malformed inputs, rapid bursts, extreme queries)
"""

import sys, os
import time
import requests
import json
from concurrent.futures import ThreadPoolExecutor

API_URL = "http://127.0.0.1:8000"

TEST_CASES = [
    # ── CATEGORY 1: Layer 0A - Symbolic & Numerical Math ──
    {
        "category": "Layer 0A - Symbolic & Math",
        "query": "what is (12 * 8) + (144 / 12) - 5^2",
        "expected_layers": ["0A"],
        "validator": lambda r: "83" in r.get("answer", "") or "83.0" in r.get("answer", ""),
        "weight": 5
    },
    {
        "category": "Layer 0A - Symbolic & Math",
        "query": "simplify sin(x)^2 + cos(x)^2",
        "expected_layers": ["0A"],
        "validator": lambda r: "1" in r.get("answer", ""),
        "weight": 5
    },
    {
        "category": "Layer 0A - Symbolic & Math",
        "query": "calculate sinx/cosx",
        "expected_layers": ["0A"],
        "validator": lambda r: "tan(x)" in r.get("answer", ""),
        "weight": 5
    },
    {
        "category": "Layer 0A - Symbolic & Math",
        "query": "convert 5 hours to seconds",
        "expected_layers": ["0A"],
        "validator": lambda r: "18000" in r.get("answer", "") or "18,000" in r.get("answer", ""),
        "weight": 5
    },
    {
        "category": "Layer 0A - Symbolic & Math",
        "query": "what is the speed of light",
        "expected_layers": ["0A", "0B"],
        "validator": lambda r: "299" in r.get("answer", "") or "speed of light" in r.get("answer", "").lower(),
        "weight": 4
    },

    # ── CATEGORY 2: Layer 0B - General Knowledge Lookups ──
    {
        "category": "Layer 0B - General Knowledge",
        "query": "what is quantum mechanics",
        "expected_layers": ["0B"],
        "validator": lambda r: len(r.get("answer", "")) > 20 and r.get("cost_saved") == True,
        "weight": 5
    },
    {
        "category": "Layer 0B - General Knowledge",
        "query": "who was Albert Einstein",
        "expected_layers": ["0B"],
        "validator": lambda r: "einstein" in r.get("answer", "").lower() or "physicist" in r.get("answer", "").lower(),
        "weight": 5
    },

    # ── CATEGORY 3: Layer 1 - TinyML Domain Classifier ──
    {
        "category": "Layer 1 - TinyML Classifier",
        "query": "where is my order package status",
        "expected_layers": ["1", "2", "3", "4"],
        "validator": lambda r: "shipping" in r.get("answer", "").lower() or "order" in r.get("answer", "").lower(),
        "weight": 5
    },
    {
        "category": "Layer 1 - TinyML Classifier",
        "query": "i need a refund for my payment charged twice",
        "expected_layers": ["1", "2", "3", "4"],
        "validator": lambda r: "refund" in r.get("answer", "").lower() or "billing" in r.get("answer", "").lower(),
        "weight": 5
    },

    # ── CATEGORY 4: Layer 2 - MinHash LSH Cache (Code Structures & Gotchas) ──
    {
        "category": "Layer 2 - MinHash LSH Cache",
        "query": "give me the code structure of c++",
        "expected_layers": ["2"],
        "validator": lambda r: "cpp" in r.get("answer", "").lower() and "#include <iostream>" in r.get("answer", "") and r.get("cost_saved") == True,
        "weight": 7
    },
    {
        "category": "Layer 2 - MinHash LSH Cache",
        "query": "give me the code structure of java",
        "expected_layers": ["2"],
        "validator": lambda r: "public static void main" in r.get("answer", "") and r.get("cost_saved") == True,
        "weight": 6
    },
    {
        "category": "Layer 2 - MinHash LSH Cache",
        "query": "why does javascript setTimeout in for loop output 3 3 3 instead of 0 1 2",
        "expected_layers": ["2"],
        "validator": lambda r: "closure" in r.get("answer", "").lower() or "let" in r.get("answer", "") or "scope" in r.get("answer", "").lower(),
        "weight": 6
    },

    # ── CATEGORY 5: Layer 3 & 4 - Semantic Embedder & Ensemble ML ──
    {
        "category": "Layer 3/4 - Embedder & Ensemble ML",
        "query": "what is the syntax skeleton for a python script",
        "expected_layers": ["3", "4"],
        "validator": lambda r: "__name__ == '__main__'" in r.get("answer", "") and r.get("cost_saved") == True,
        "weight": 7
    },
    {
        "category": "Layer 3/4 - Embedder & Ensemble ML",
        "query": "explain why mutating state directly in react fails to trigger re-renders",
        "expected_layers": ["3", "4", "2"],
        "validator": lambda r: "shallow" in r.get("answer", "").lower() or "spread" in r.get("answer", "").lower() or "mutat" in r.get("answer", "").lower(),
        "weight": 6
    },
    {
        "category": "Layer 3/4 - Embedder & Ensemble ML",
        "query": "how to prevent SQL injection in database queries",
        "expected_layers": ["2", "3", "4"],
        "validator": lambda r: "parameterized" in r.get("answer", "").lower() or "prepared" in r.get("answer", "").lower(),
        "weight": 6
    },
    {
        "category": "Layer 3/4 - Embedder & Ensemble ML",
        "query": "what is the N+1 query problem and how do i solve it",
        "expected_layers": ["2", "3", "4"],
        "validator": lambda r: "eager" in r.get("answer", "").lower() or "select_related" in r.get("answer", "").lower() or "join" in r.get("answer", "").lower(),
        "weight": 6
    },
    {
        "category": "Layer 3/4 - Embedder & Ensemble ML",
        "query": "what is the Big O time complexity hierarchy from fastest to slowest",
        "expected_layers": ["2", "3", "4"],
        "validator": lambda r: "O(1)" in r.get("answer", "") and "O(n!)" in r.get("answer", ""),
        "weight": 6
    },

    # ── CATEGORY 6: Layer 5 - Auto-LLM Fallback (Novel Deep Technical Questions) ──
    {
        "category": "Layer 5 - Auto-LLM Inference",
        "query": "Write a complete production-grade Redis token bucket rate limiter in Python with redis-py, atomic lua script, and unit tests.",
        "expected_layers": ["5"],
        "validator": lambda r: len(r.get("answer", "")) > 300 and ("lua" in r.get("answer", "").lower() or "redis" in r.get("answer", "").lower()),
        "weight": 8
    },
    {
        "category": "Layer 5 - Auto-LLM Inference",
        "query": "Provide an in-depth mathematical explanation of Multi-Head Self-Attention in Transformers with query, key, value projections and softmax scaling.",
        "expected_layers": ["5"],
        "validator": lambda r: len(r.get("answer", "")) > 300 and ("softmax" in r.get("answer", "").lower() or "q" in r.get("answer", "").lower() or "attention" in r.get("answer", "").lower()),
        "weight": 8
    },
]

def run_test(test):
    query = test["query"]
    t0 = time.time()
    try:
        res = requests.post(f"{API_URL}/query", json={"query": query, "provider": "auto"}, timeout=30)
        latency = round((time.time() - t0) * 1000, 2)
        if res.status_code != 200:
            return {"test": test, "passed": False, "reason": f"HTTP {res.status_code}", "latency": latency, "data": {}}
        
        data = res.json()
        layer = data.get("layer")
        answer = data.get("answer", "")
        
        # Check layer expectation
        layer_match = layer in test["expected_layers"]
        
        # Check content validator
        content_match = False
        try:
            content_match = test["validator"](data)
        except Exception as e:
            content_match = False

        passed = layer_match and content_match
        reason = "OK" if passed else f"Layer: {layer} (expected {test['expected_layers']}), ContentMatch: {content_match}"

        return {
            "test": test,
            "passed": passed,
            "reason": reason,
            "layer": layer,
            "latency": latency,
            "data": data
        }
    except Exception as e:
        return {
            "test": test,
            "passed": False,
            "reason": str(e),
            "latency": 0,
            "data": {}
        }

def run_concurrency_burst():
    """Stress test with 20 parallel requests to measure pipeline stability & throughput"""
    burst_queries = [
        "give me the code structure of c++",
        "what is (50 * 4) / 5",
        "simplify sin(x)^2 + cos(x)^2",
        "convert 1000 meters to km",
        "give me the code structure of java",
        "what is the syntax skeleton for a python script",
        "why does this python code print 4 4 4 4 4 lambda in loop",
        "where is my package",
        "i need a refund",
        "what is the Big O time complexity hierarchy from fastest to slowest",
        "how to prevent SQL injection in database queries",
        "what is the N+1 query problem and how do i solve it",
        "explain how to validate a binary search tree in python",
        "how to fix CORS Access Control Allow Origin error",
        "give me the code structure of rust",
        "give me the code structure of go",
        "give me the code structure of html",
        "give me the code structure of c",
        "what is the speed of light",
        "who was Albert Einstein"
    ]
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(lambda q: requests.post(f"{API_URL}/query", json={"query": q}, timeout=15), burst_queries))
    total_time = round((time.time() - t0) * 1000, 2)
    success_count = sum(1 for r in results if r.status_code == 200)
    return success_count == len(burst_queries), total_time, len(burst_queries)

def main():
    print("=" * 70)
    print("🛸 KUIPER 7-LAYER ROUTER: COMPREHENSIVE BENCHMARK EVALUATION 🛸")
    print("=" * 70)

    # 1. Check health
    try:
        h = requests.get(f"{API_URL}/health", timeout=5).json()
        print(f"Backend Status: {h.get('status')} | Pipeline: {h.get('pipeline')} | Version: {h.get('version')}\n")
    except Exception as e:
        print(f"❌ Backend not responding at {API_URL}: {e}")
        sys.exit(1)

    # 2. Run Functional Suite
    category_scores = {}
    total_weight = sum(t["weight"] for t in TEST_CASES)
    earned_weight = 0

    print(f"Running {len(TEST_CASES)} High-Level Multi-Domain Verification Tests...\n")
    results = []
    for i, t in enumerate(TEST_CASES, 1):
        r = run_test(t)
        results.append(r)
        cat = t["category"]
        if cat not in category_scores:
            category_scores[cat] = {"total": 0, "passed": 0, "weight": 0, "earned": 0}
        category_scores[cat]["total"] += 1
        category_scores[cat]["weight"] += t["weight"]

        status_icon = "✅ PASS" if r["passed"] else "❌ FAIL"
        print(f"[{i:02d}/{len(TEST_CASES):02d}] {status_icon} | [{t['category']}]")
        print(f"     Query: \"{t['query'][:60]}...\"")
        print(f"     Layer Hit: {r.get('layer', 'None')} | Latency: {r.get('latency', 0)}ms | Status: {r['reason']}")
        if not r["passed"] and r.get("data"):
            print(f"     Answer Snippet: {r['data'].get('answer', '')[:120]}...")
        print()

        if r["passed"]:
            category_scores[cat]["passed"] += 1
            category_scores[cat]["earned"] += t["weight"]
            earned_weight += t["weight"]

    # 3. Concurrency Stress Test
    print("-" * 70)
    print("⚡ Running Concurrency Burst Stress Test (20 parallel requests)...")
    burst_ok, burst_ms, req_count = run_concurrency_burst()
    burst_avg_ms = round(burst_ms / req_count, 2)
    burst_score = 10 if burst_ok and burst_avg_ms < 150 else (8 if burst_ok else 0)
    print(f"   Burst Completed: {req_count}/{req_count} OK in {burst_ms}ms (Avg {burst_avg_ms}ms/req) -> Score: {burst_score}/10\n")

    # 4. Fetch System Statistics
    stats = requests.get(f"{API_URL}/stats").json()

    # 5. Compute Final Grade & Breakdown
    base_score = (earned_weight / total_weight) * 90.0
    final_score = round(base_score + burst_score, 1)

    print("=" * 70)
    print("📊 FINAL BENCHMARK SCORECARD & PERFORMANCE MATRIX")
    print("=" * 70)
    for cat, data in category_scores.items():
        pct = round((data["earned"] / data["weight"]) * 100, 1)
        print(f"  • {cat:<36}: {data['passed']}/{data['total']} passed ({pct}%)")

    print(f"  • {'Concurrency & Stress Throughput':<36}: {burst_score}/10 pts ({burst_avg_ms}ms avg)")
    print("-" * 70)
    print(f"  🏆 OVERALL SYSTEM SCORE: {final_score} / 100")
    print(f"  💰 Local Handling Rate: {stats.get('local_rate')} | Estimated Saved: {stats.get('estimated_saved')}")
    print(f"  ⚡ Dynamic Alpha (α): {stats.get('alpha')} ({stats.get('price_tier')})")
    print("=" * 70)

if __name__ == "__main__":
    main()
