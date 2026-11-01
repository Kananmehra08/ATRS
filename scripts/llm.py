"""Single entry point for LLM interactions supporting Google Gemini and Anthropic.

Logs every call and its token consumption to data/usage_log.csv for auditability.
"""
import os
import sys
import csv
import time
from datetime import datetime, timezone

# Ensure project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def log_usage(log_path: str, model: str, input_tokens: int, output_tokens: int, prompt_chars: int, response_chars: int):
    """Log an LLM API call's token and character metrics to a CSV file."""
    os.makedirs(os.path.dirname(os.path.abspath(log_path)), exist_ok=True)
    file_exists = os.path.exists(log_path) and os.path.getsize(log_path) > 0

    with open(log_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "timestamp_utc",
                "model",
                "input_tokens",
                "output_tokens",
                "total_tokens",
                "prompt_chars",
                "response_chars",
            ])
        writer.writerow([
            datetime.now(timezone.utc).isoformat(),
            model,
            input_tokens,
            output_tokens,
            input_tokens + output_tokens,
            prompt_chars,
            response_chars,
        ])


def call_gemini(prompt: str, model: str, api_key: str) -> tuple[str, int, int]:
    """Call Google Gemini API via REST endpoint with automatic fallback across models."""
    import requests

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    models_to_try = [model, "gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.8-flash"]
    seen = set()
    candidate_models = [m for m in models_to_try if not (m in seen or seen.add(m))]

    for m in candidate_models:
        clean_model = m.replace("models/", "")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{clean_model}:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": config.TEMPERATURE,
                "maxOutputTokens": config.MAX_TOKENS,
            },
        }

        for attempt in range(1, 4):
            try:
                resp = requests.post(url, json=payload, timeout=90)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if not candidates:
                        return "", 0, 0
                    parts = candidates[0].get("content", {}).get("parts", [])
                    text = "".join(p.get("text", "") for p in parts)
                    usage = data.get("usageMetadata", {})
                    in_tokens = usage.get("promptTokenCount", 0)
                    out_tokens = usage.get("candidatesTokenCount", 0)
                    return text, in_tokens, out_tokens
                elif resp.status_code in (429, 503):
                    wait_time = 3 * attempt
                    print(f"       [{clean_model} status {resp.status_code}] Waiting {wait_time}s (attempt {attempt}/3)...")
                    time.sleep(wait_time)
                    continue
                else:
                    break
            except requests.RequestException:
                time.sleep(2 * attempt)

    raise RuntimeError("Failed to obtain response from Gemini API across fallback models.")


def call_anthropic(prompt: str, model: str, api_key: str) -> tuple[str, int, int]:
    """Call Anthropic Claude API via Anthropic SDK."""
    import anthropic

    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not configured.")

    client = anthropic.Anthropic(api_key=api_key)
    msg = client.messages.create(
        model=model,
        max_tokens=config.MAX_TOKENS,
        temperature=config.TEMPERATURE,
        messages=[{"role": "user", "content": prompt}],
    )
    text = "".join(b.text for b in msg.content if getattr(b, "type", None) == "text")
    in_tokens = getattr(msg.usage, "input_tokens", 0) if hasattr(msg, "usage") else 0
    out_tokens = getattr(msg.usage, "output_tokens", 0) if hasattr(msg, "usage") else 0
    return text, in_tokens, out_tokens


def call_llm(prompt: str, log_path: str = None) -> str:
    """Send prompt to the active LLM provider and log token consumption."""
    target_log = log_path or config.USAGE_LOG_PATH

    if config.PROVIDER == "gemini":
        text, in_tokens, out_tokens = call_gemini(prompt, config.MODEL, config.GEMINI_API_KEY)
    elif config.PROVIDER == "anthropic":
        key = config.ANTHROPIC_API_KEY or os.getenv("ANTHROPIC_API_KEY")
        text, in_tokens, out_tokens = call_anthropic(prompt, config.MODEL, key)
    else:
        raise ValueError(f"Unknown LLM provider: {config.PROVIDER}")

    log_usage(
        log_path=target_log,
        model=config.MODEL,
        input_tokens=in_tokens,
        output_tokens=out_tokens,
        prompt_chars=len(prompt),
        response_chars=len(text),
    )

    return text


if __name__ == "__main__":
    print(f"llm.py configured with Provider: {config.PROVIDER}, Model: {config.MODEL}")
    print("Testing call_llm with prompt: 'Reply with OK' ...")
    test_res = call_llm("Reply with OK")
    print(f"Response: {test_res.strip()}")
    print(f"Usage logged to: {config.USAGE_LOG_PATH}")
