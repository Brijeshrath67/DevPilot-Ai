#!/usr/bin/env python3
"""Test every configured LLM provider with a short prompt and report results.

Run: python scripts/test_providers.py [--timeout SECONDS]
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from app.core.providers import LLMProviderRegistry
from app.core.config import settings

registry = LLMProviderRegistry(settings)
PROVIDERS = ["groq", "huggingface", "mistral", "nvidia", "openrouter"]

PROMPT = "Reply with exactly the single word: ok"


def main() -> None:
    results = []
    for name in PROVIDERS:
        service = registry.get_service(name)
        if not service.api_key or service.api_key == "mock_key":
            results.append((name, "SKIPPED", "no API key configured"))
            continue
        try:
            content = service.generate(PROMPT, temperature=0.0, max_tokens=16)
            failed = content.startswith("LLM request failed")
            snippet = (content or "")[:60].replace("\n", " ")
            status = "FAILED" if failed else "OK"
            results.append((name, status, snippet))
        except Exception as exc:  # noqa: BLE001
            results.append((name, "ERROR", str(exc)[:80]))

    print(f"\nTest prompt: {PROMPT!r}\n")
    print(f"{'Provider':<14} {'Status':<8} Output")
    print("-" * 90)
    for name, status, snippet in results:
        print(f"{name:<14} {status:<8} {snippet or ''}")
    ok = sum(1 for _, s, _ in results if s == "OK")
    print(f"\n{ok}/{len(PROVIDERS)} providers returned output.")


if __name__ == "__main__":
    main()
