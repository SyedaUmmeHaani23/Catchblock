from pathlib import Path
from ..models import Finding, Fix
from .files import _find
from .deps import collect_deps

PLACEHOLDER = "(name each tool and what it did)"
CREDIT_PLACEHOLDER = "(libraries, templates, borrowed code)"
AI_WORDS = ("ai tool", "claude", "chatgpt", "copilot", "gemini", "gemma", "cursor", "llm", "openai", "codex", "windsurf", "aider")

AI_FILES = {".cursor": "Cursor", ".cursorrules": "Cursor", "CLAUDE.md": "Claude", "AGENTS.md": "AI coding agent",
            "GEMINI.md": "Gemini", ".github/copilot-instructions.md": "Copilot", ".aider.conf.yml": "Aider",
            ".windsurfrules": "Windsurf", ".continue": "Continue"}
AI_DEPS = {"openai": "OpenAI", "anthropic": "Claude", "@anthropic-ai/sdk": "Claude", "google-generativeai": "Gemini",
           "@google/generative-ai": "Gemini", "langchain": "LangChain", "llama-index": "LlamaIndex", "ollama": "Ollama",
           "transformers": "Hugging Face", "groq": "Groq", "cohere": "Cohere", "mistralai": "Mistral"}

def detect_ai(root: Path):
    """Returns [{'tool', 'evidence'}]. Signals only: a human must still describe what each tool did."""
    found = {}
    for rel, tool in AI_FILES.items():
        if (root / rel).exists():
            found.setdefault(tool, rel)
    for dep, eco in collect_deps(root).items():
        if dep in AI_DEPS:
            found.setdefault(AI_DEPS[dep], f"dependency {dep}")
    return [{"tool": t, "evidence": e} for t, e in found.items()]

def check_ai_disclosure(root: Path, rules=None):
    if not (rules or {}).get("requirements", {}).get("ai_disclosure", True):
        return None
    p = _find(root, "readme")
    text = p.read_text(encoding="utf-8", errors="ignore").lower() if p else ""
    tools = detect_ai(root)
    ok = any(w in text for w in AI_WORDS) and "credit" in text
    if ok and PLACEHOLDER in text:
        return Finding("disclosure.ai", "Disclosure", "warn", "high", 10,
                       "README still has the AI tools placeholder: fill it in",
                       "Name every AI tool you used. Replace the placeholder with the real list.")
    if ok:
        missing = [t["tool"] for t in tools if t["tool"].split()[0].lower() not in text]
        if missing:
            return Finding("disclosure.ai", "Disclosure", "warn", "high", 10,
                           "AI signals found in the repo but not named in the README: " + ", ".join(missing),
                           "CatchBlock found files or dependencies that point to these AI tools. This is a signal to check, not proof of use.")
        return Finding("disclosure.ai", "Disclosure", "pass", "high", 10, "README lists AI tools and credits",
                       "Being open about AI tools helps reviewers and contributors trust the code, and many projects now require it.")
    lines = "".join(f"- {t['tool']} (detected: {t['evidence']}): say what it did\n" for t in tools)
    return Finding("disclosure.ai", "Disclosure", "fail", "high", 10,
                   "README must list every AI tool used and credit sources" + (f" (detected: {', '.join(t['tool'] for t in tools)})" if tools else ""),
                   "Being open about AI tools helps reviewers and contributors trust the code, and many projects now require it.",
                   Fix("README.md", "## AI tools used\n" + lines + "- " + PLACEHOLDER + "\n\n## Credits\n- " + CREDIT_PLACEHOLDER + "\n", "append"))

def check_credits(root: Path, rules=None):
    deps = collect_deps(root)
    if not deps:
        return None
    p = _find(root, "readme")
    text = p.read_text(encoding="utf-8", errors="ignore").lower() if p else ""
    if CREDIT_PLACEHOLDER in text:
        return Finding("credits.readme", "Disclosure", "warn", "medium", 5, "README credits section is still a placeholder",
                       "Credit the libraries and code you build on. Replace the placeholder with the real list.")
    ok = "credit" in text or "acknowledg" in text
    names = sorted(deps)[:12]
    return Finding("credits.readme", "Disclosure", "pass" if ok else "warn", "medium", 5,
                   "README credits the libraries used" if ok else f"README has no Credits section ({len(deps)} dependencies detected)",
                   "Open-source etiquette expects you to credit the open-source work you build on.",
                   None if ok else Fix("README.md", "## Credits\n" + "".join(f"- {n}\n" for n in names), "append"))
