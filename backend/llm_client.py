import os
import re
import json
import time
import requests
from dotenv import load_dotenv

load_dotenv()

# Default Keys (loaded from environment or .env file)
INBUILT_GROQ_KEY   = os.getenv("GROQ_API_KEY", "")
INBUILT_GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")

# Model configurations
GROQ_MODELS = ["openai/gpt-oss-120b", "qwen/qwen3.8-27b", "openai/gpt-oss-20b", "groq/compound"]
GEMINI_MODELS = ["gemini-3.5-flash", "gemini-3.6-flash", "gemini-3.5-flash-lite", "gemini-flash-latest"]

SYSTEM_PROMPT = (
    "You are Kuiper AI, an expert, highly intelligent reasoning assistant. "
    "Provide thorough, accurate, and beautifully structured responses with markdown formatting. "
    "When explaining concepts, write comprehensive explanations, complete code snippets, step-by-step logic, or bullet points as appropriate. "
    "Never truncate your answers artificially."
)

def select_optimal_provider(prompt):
    """
    Intelligent Auto-Selector:
    Evaluates prompt complexity, intent, length, and subject matter to pick the best model.
    """
    p = prompt.lower().strip()

    # Keywords indicating need for large context, deep analytical reasoning, or comprehensive essays -> Gemini
    gemini_triggers = [
        "in detail", "comprehensive", "deep dive", "elaborate", "essay", "analysis",
        "compare and contrast", "pros and cons", "step by step", "breakdown",
        "detailed explanation", "philosophical", "history of", "summarize the article",
        "why is", "why do", "discuss the implications", "architecture"
    ]
    if any(trigger in p for trigger in gemini_triggers) or len(p.split()) > 30:
        return "gemini", "gemini-3.5-flash", "Gemini 3.5 Flash (Deep Analytical Reasoning & Large Context)"

    # Coding, algorithms, quick technical questions, translations, direct queries -> Groq (Ultra-fast inference)
    return "groq", "openai/gpt-oss-120b", "Groq GPT OSS 120B (Ultra-Fast High-Throughput Inference)"

def call_groq(prompt, api_key=None, model=None, max_tokens=2048):
    key = api_key or INBUILT_GROQ_KEY
    if not key:
        raise ValueError("Groq API key not provided")

    selected_model = model or GROQ_MODELS[0]
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": selected_model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.4,
        "max_tokens": max_tokens
    }

    start = time.time()
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    latency_ms = round((time.time() - start) * 1000, 2)

    if resp.status_code != 200:
        for alt_model in GROQ_MODELS[1:]:
            payload["model"] = alt_model
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            if resp.status_code == 200:
                selected_model = alt_model
                break
        
        if resp.status_code != 200:
            raise RuntimeError(f"Groq API Error ({resp.status_code}): {resp.text}")

    data = resp.json()
    content = data["choices"][0]["message"]["content"].strip()
    usage = data.get("usage", {})
    total_tokens = usage.get("total_tokens", len(prompt.split()) + len(content.split()))
    
    prompt_tokens = usage.get("prompt_tokens", len(prompt.split()))
    completion_tokens = usage.get("completion_tokens", len(content.split()))
    cost = round((prompt_tokens * 0.00015 / 1000) + (completion_tokens * 0.0006 / 1000), 6)

    return {
        "answer": content,
        "provider": "groq",
        "model": selected_model,
        "latency_ms": latency_ms,
        "tokens": total_tokens,
        "cost": max(cost, 0.00005)
    }

def call_gemini(prompt, api_key=None, model=None, max_tokens=3072):
    key = api_key or INBUILT_GEMINI_KEY
    if not key:
        raise ValueError("Gemini API key not provided")

    model_candidates = [model] if model else GEMINI_MODELS
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": f"{SYSTEM_PROMPT}\n\nUser Question:\n{prompt}"}]}],
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": max_tokens
        }
    }

    start = time.time()
    last_error = None
    for cand in model_candidates:
        if not cand:
            continue
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{cand}:generateContent?key={key}"
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            if resp.status_code == 200:
                latency_ms = round((time.time() - start) * 1000, 2)
                data = resp.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    text = "".join(p.get("text", "") for p in parts).strip()
                    usage = data.get("usageMetadata", {})
                    total_tokens = usage.get("totalTokenCount", len(prompt.split()) + len(text.split()))
                    cost = round(total_tokens * 0.00015 / 1000, 6)
                    return {
                        "answer": text,
                        "provider": "gemini",
                        "model": cand,
                        "latency_ms": latency_ms,
                        "tokens": total_tokens,
                        "cost": max(cost, 0.00005)
                    }
            else:
                last_error = resp.text
        except Exception as e:
            last_error = str(e)

    raise RuntimeError(f"Gemini API Error: {last_error}")

def call_llm(prompt, provider="auto", api_key=None, model=None, max_tokens=2048):
    """
    Unified LLM caller with Automatic Optimal Model Selection & Full-Length Output.
    """
    provider_str = (provider or "auto").lower().strip()
    selection_reason = None

    # Handle Automatic Model Selection
    if provider_str in ["auto", "smart", "intelligent", ""]:
        selected_provider, selected_model, selection_reason = select_optimal_provider(prompt)
        provider_str = selected_provider
        if not model:
            model = selected_model

    # Execute Selected Provider with seamless fallback
    if provider_str == "groq":
        try:
            res = call_groq(prompt, api_key=api_key, model=model, max_tokens=max_tokens)
            if selection_reason:
                res["selection_reason"] = selection_reason
            return res
        except Exception as e:
            print(f"Groq failed ({e}), falling back to Gemini...")
            try:
                res = call_gemini(prompt, api_key=None, max_tokens=max_tokens)
                res["selection_reason"] = f"Auto-Fallback to Gemini ({e})"
                return res
            except Exception as e2:
                raise RuntimeError(f"Both Groq and Gemini failed: {e} | {e2}")

    elif provider_str == "gemini":
        try:
            res = call_gemini(prompt, api_key=api_key, model=model, max_tokens=max_tokens)
            if selection_reason:
                res["selection_reason"] = selection_reason
            return res
        except Exception as e:
            print(f"Gemini failed ({e}), falling back to Groq...")
            try:
                res = call_groq(prompt, api_key=None, max_tokens=max_tokens)
                res["selection_reason"] = f"Auto-Fallback to Groq ({e})"
                return res
            except Exception as e2:
                raise RuntimeError(f"Both Gemini and Groq failed: {e} | {e2}")

    else:
        try:
            return call_groq(prompt, api_key=api_key, model=model, max_tokens=max_tokens)
        except Exception:
            return call_gemini(prompt, api_key=api_key, max_tokens=max_tokens)
