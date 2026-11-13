from dataclasses import dataclass
from typing import Iterator
from .config import settings
@dataclass
class AIChunk:
    text: str
    done: bool = False
class ProviderUnavailable(Exception): pass
class AIProvider:
    name="disabled"; model="disabled"
    def stream(self, system: str, context: str, messages: list[dict[str,str]]) -> Iterator[AIChunk]: raise ProviderUnavailable("AI provider is unavailable")
class MockProvider(AIProvider):
    name="mock"; model="mock-model"
    def stream(self, system: str, context: str, messages: list[dict[str,str]]) -> Iterator[AIChunk]:
        yield AIChunk("[Mock provider response for automated tests.]", True)
def get_provider() -> AIProvider:
    if not settings.ai_enabled or settings.ai_provider=="disabled": return AIProvider()
    if settings.ai_provider=="mock": return MockProvider()
    raise ProviderUnavailable("Configured AI provider is not implemented or unavailable")
def redact(text: str) -> str:
    return text.replace("OPENAI_API_KEY", "[redacted-key-name]").replace("sk-", "[redacted-token]")
