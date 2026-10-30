"""OpenRouter models with a free-only gate for both conversation participants."""

import os
import time
from decimal import Decimal
from typing import Any

import httpx
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_openai import ChatOpenAI
from pydantic import Field

DEFAULT_MODEL = "nvidia/nemotron-3.5-lightning:free"
BASE_URL = "https://openrouter.ai/api/v1"
# Shared between the agent and user: stay below the published free-model RPM cap.
RATE_LIMITER = InMemoryRateLimiter(requests_per_second=0.25, max_bucket_size=1)


class FreeChatOpenAI(ChatOpenAI):
    """Retry only transient HTTP errors, before any tool execution occurs."""

    retry_observer: Any = Field(default=None, exclude=True)

    def bind_tools(self, tools, **kwargs):
        kwargs["parallel_tool_calls"] = False
        if any(getattr(tool, "name", None) == "ask_customer" for tool in tools):
            kwargs["tool_choice"] = "required"
        return super().bind_tools(tools, **kwargs)

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        for attempt in range(6):
            try:
                return super()._generate(messages, stop=stop, run_manager=run_manager, **kwargs)
            except Exception as exc:
                status = getattr(exc, "status_code", None)
                if status not in (429, 502, 503, 504) or attempt == 5:
                    raise
                delay = min(20 * (attempt + 1), 60)
                if self.retry_observer:
                    self.retry_observer(status, attempt + 1, delay)
                time.sleep(delay)


def require_free_id(name: str) -> None:
    if name != "openrouter/free" and not name.endswith(":free"):
        raise ValueError("Only openrouter/free or a catalog :free model is allowed.")


def preflight(name: str) -> dict:
    require_free_id(name)
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not key or key == "your-key-here":
        raise ValueError("Set OPENROUTER_API_KEY in .env before running a live task.")
    with httpx.Client(timeout=30) as client:
        response = client.get(f"{BASE_URL}/models")
        response.raise_for_status()
        entry = next((m for m in response.json()["data"] if m["id"] == name), None)
        if entry is None:
            raise ValueError(f"Model is not in the current OpenRouter catalog: {name}")
        prices = entry.get("pricing", {})
        if not {"prompt", "completion"} <= prices.keys() or any(
            Decimal(str(price)) != 0 for price in prices.values()
        ):
            raise ValueError("Refusing a model with nonzero or unknown pricing.")
        if "tools" not in entry.get("supported_parameters", []):
            raise ValueError("Select a free model that supports tool calling.")
    return {"requested_model": name, "pricing": prices,
            "context_length": entry["context_length"]}


def make_model(name: str, on_retry=None) -> ChatOpenAI:
    require_free_id(name)
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not key:
        raise ValueError("OPENROUTER_API_KEY is required (no OpenAI key fallback).")
    return FreeChatOpenAI(
        model=name, api_key=key, base_url=BASE_URL, temperature=0,
        max_tokens=2048, timeout=90, max_retries=0, rate_limiter=RATE_LIMITER,
        retry_observer=on_retry,
        extra_body={"provider": {"max_price": {"prompt": 0, "completion": 0}}},
    )
