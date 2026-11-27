"""Server-side AI provider boundary."""

from dataclasses import dataclass, field
import json
import re
import time
from typing import Iterable

import httpx

from .config import settings


@dataclass
class AIChunk:
    text: str
    done: bool = False
    usage: dict[str, int] = field(default_factory=dict)


class ProviderUnavailable(Exception):
    def __init__(self, message: str, code: str = "provider_unavailable"):
        super().__init__(message)
        self.code = code


class AIProvider:
    name = "disabled"
    model = "disabled"

    def stream(self, system: str, context: str, messages: list[dict[str, str]]) -> Iterable[AIChunk]:
        raise ProviderUnavailable("AI tutor provider is not configured", "provider_not_configured")


class MockProvider(AIProvider):
    name = "mock"
    model = "mock-model"

    def stream(self, system: str, context: str, messages: list[dict[str, str]]) -> Iterable[AIChunk]:
        # The mock exists for deterministic tests only and is never selected by default.
        yield AIChunk("[Mock provider response for automated tests.]", done=True, usage={"input_tokens": 0, "output_tokens": 7})


class OpenAIResponsesProvider(AIProvider):
    """Streaming adapter for the OpenAI Responses API."""

    name = "openai"

    def __init__(self, api_key: str, model: str, timeout: int, base_url: str):
        if not api_key:
            raise ProviderUnavailable("OpenAI provider is not configured", "provider_not_configured")
        self.model = model
        self.timeout = timeout
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def stream(self, system: str, context: str, messages: list[dict[str, str]]) -> Iterable[AIChunk]:
        payload = {"model": self.model, "instructions": system, "input": messages, "stream": True}
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        try:
            with httpx.Client(timeout=httpx.Timeout(self.timeout, connect=min(self.timeout, 10))) as client:
                response = client.stream("POST", f"{self.base_url}/responses", headers=headers, json=payload)
                with response as stream:
                    if stream.status_code == 401:
                        raise ProviderUnavailable("The configured AI provider rejected its credentials", "provider_auth_failed")
                    if stream.status_code == 429:
                        raise ProviderUnavailable("The AI provider rate limit was reached", "provider_rate_limited")
                    if stream.status_code >= 500:
                        raise ProviderUnavailable("The AI provider is temporarily unavailable", "provider_upstream_error")
                    if stream.status_code >= 400:
                        raise ProviderUnavailable("The AI provider rejected the tutor request", "provider_request_rejected")
                    event_name = ""
                    usage: dict[str, int] = {}
                    for raw_line in stream.iter_lines():
                        line = raw_line.strip()
                        if not line:
                            event_name = ""
                            continue
                        if line.startswith("event:"):
                            event_name = line[6:].strip()
                            continue
                        if not line.startswith("data:"):
                            continue
                        raw_data = line[5:].strip()
                        if raw_data == "[DONE]":
                            yield AIChunk("", done=True, usage=usage)
                            return
                        try:
                            data = json.loads(raw_data)
                        except json.JSONDecodeError:
                            continue
                        event_type = event_name or data.get("type", "")
                        if event_type == "response.output_text.delta":
                            delta = data.get("delta", "")
                            if delta:
                                yield AIChunk(delta)
                        if event_type in {"response.completed", "response.incomplete"}:
                            response_data = data.get("response", data)
                            response_usage = response_data.get("usage", {}) if isinstance(response_data, dict) else {}
                            usage = {"input_tokens": int(response_usage.get("input_tokens", 0) or 0), "output_tokens": int(response_usage.get("output_tokens", 0) or 0)}
                            yield AIChunk("", done=True, usage=usage)
                            return
                    yield AIChunk("", done=True, usage=usage)
        except ProviderUnavailable:
            raise
        except httpx.TimeoutException as exc:
            raise ProviderUnavailable("The AI provider timed out", "provider_timeout") from exc
        except httpx.HTTPError as exc:
            raise ProviderUnavailable("The AI provider could not be reached", "provider_network_error") from exc


def get_provider() -> AIProvider:
    if not settings.ai_enabled or settings.ai_provider == "disabled":
        return AIProvider()
    if settings.ai_provider == "mock":
        return MockProvider()
    if settings.ai_provider == "openai":
        return OpenAIResponsesProvider(settings.openai_api_key, settings.ai_model, settings.ai_request_timeout_seconds, settings.ai_openai_base_url)
    raise ProviderUnavailable("Configured AI provider is not supported", "provider_unsupported")


def redact(text: str) -> str:
    value = re.sub(r"(?i)(OPENAI_API_KEY|sk-[A-Za-z0-9_-]{12,})", "[redacted]", text)
    return value[: settings.ai_max_input_chars]


def estimate_tokens(text: str) -> int:
    return max(0, len(text) // 4)


def elapsed_ms(start: float) -> int:
    return max(0, round((time.monotonic() - start) * 1000))
