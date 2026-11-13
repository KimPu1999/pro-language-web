from dataclasses import dataclass
@dataclass(frozen=True)
class RuntimeSpec:
    identifier: str; version: str; filename: str; image: str
RUNTIMES={
    "python":RuntimeSpec("python","3.12","main.py","python@sha256:runner-required"),
    "javascript":RuntimeSpec("javascript","22","main.js","node@sha256:runner-required"),
    "typescript":RuntimeSpec("typescript","5","main.ts","typescript@sha256:runner-required"),
    "java":RuntimeSpec("java","21","Main.java","java@sha256:runner-required"),
    "cpp":RuntimeSpec("cpp","gcc-14","main.cpp","cpp@sha256:runner-required"),
    "php":RuntimeSpec("php","8.3","main.php","php@sha256:runner-required"),
}
def get_runtime(language: str) -> RuntimeSpec:
    try: return RUNTIMES[language]
    except KeyError: raise ValueError("Unsupported language")
