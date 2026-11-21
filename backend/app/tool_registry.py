"""The only implementations that the catalog is allowed to select.

Database records contain a key from this registry; they never contain an
import path or executable source.  This keeps editorial data separate from
the application code boundary.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class RegisteredTool:
    implementation_key: str
    category_slug: str
    category_name: str
    category_description: str
    name: str
    slug: str
    short_description: str
    full_description: str
    icon_key: str
    route_path: str
    tags: tuple[str, ...]
    display_order: int
    is_featured: bool = False


TOOL_REGISTRY = {
    "json_formatter": RegisteredTool("json_formatter", "data", "Data", "Inspect and transform structured data locally.", "JSON Formatter", "json-formatter", "Format JSON and inspect syntax errors locally.", "Format JSON in your browser without uploading the payload.", "braces", "/tools/json-formatter", ("json", "format", "data"), 10, True),
    "json_validator": RegisteredTool("json_validator", "data", "Data", "Inspect and transform structured data locally.", "JSON Validator", "json-validator", "Validate JSON without uploading the payload.", "Check whether a JSON document is valid and get a readable error when it is not.", "check", "/tools/json-validator", ("json", "validate", "data"), 20),
    "base64_encoder": RegisteredTool("base64_encoder", "text", "Text", "Small text transformations for everyday development.", "Base64 Encoder", "base64", "Encode text locally for development experiments.", "Encode text with the browser Web API. Input stays in this browser tab.", "binary", "/tools/base64", ("encoding", "base64", "text"), 30),
    "uuid_generator": RegisteredTool("uuid_generator", "security", "Security", "Safe identifiers and inspection helpers.", "UUID Generator", "uuid", "Generate a browser-side UUID with the Web Crypto API.", "Generate standards-based random UUIDs using the browser Web Crypto API.", "fingerprint", "/tools/uuid", ("uuid", "ids", "security"), 40),
    "code_playground": RegisteredTool("code_playground", "code", "Code", "Local, browser-safe developer practice tools.", "Code Playground", "code-playground", "Practice with a browser-safe code playground.", "Use the existing learning playground boundary for supported examples. Server-side arbitrary code execution is never performed by this catalog.", "code", "/tools/code-playground", ("code", "practice", "sandbox"), 50, True),
}

APPROVED_IMPLEMENTATION_KEYS = frozenset(TOOL_REGISTRY)


def category_definitions() -> list[dict]:
    seen: dict[str, RegisteredTool] = {}
    for item in TOOL_REGISTRY.values():
        seen.setdefault(item.category_slug, item)
    return [
        {"slug": slug, "name": item.category_name, "description": item.category_description, "icon_key": "wrench", "display_order": index * 10}
        for index, (slug, item) in enumerate(sorted(seen.items()))
    ]


def tool_definitions() -> list[RegisteredTool]:
    return sorted(TOOL_REGISTRY.values(), key=lambda item: item.display_order)
