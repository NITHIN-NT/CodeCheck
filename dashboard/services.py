from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, List, Tuple

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
from django.conf import settings

MODEL_NAME = "gemini-pro-latest"
logger = logging.getLogger(__name__)


class GeminiAPIError(RuntimeError):
    """Raised when the Gemini API cannot satisfy a review request."""


def detect_code_type(code: str) -> Tuple[str, str]:
    """
    Detect the programming language and framework from code patterns.
    Returns (language, framework) tuple.
    """
    code_lower = code.lower()
    
    # Framework detection (more specific first)
    if re.search(r'\bfrom\s+django\b|\bimport\s+django\b|@csrf_exempt|HttpResponse|models\.Model', code):
        return ("python", "django")
    if re.search(r'\bfrom\s+flask\b|\bimport\s+flask\b|@app\.route|Flask\(', code):
        return ("python", "flask")
    if re.search(r'\bfrom\s+fastapi\b|\bimport\s+fastapi\b|@app\.(get|post|put|delete)', code):
        return ("python", "fastapi")
    if re.search(r'\bimport\s+React\b|useState|useEffect|\.jsx?|export\s+default\s+function', code):
        return ("javascript", "react")
    if re.search(r'\brequire\(|module\.exports|exports\.|process\.env', code) and not re.search(r'\bimport\s+React\b', code):
        return ("javascript", "nodejs")
    if re.search(r'\bfrom\s+express\b|app\.(get|post|put|delete)|router\.', code):
        return ("javascript", "express")
    if re.search(r'\bfrom\s+next\b|getServerSideProps|getStaticProps|next/head', code):
        return ("javascript", "nextjs")
    if re.search(r'\bfrom\s+angular\b|@Component|@Injectable|@NgModule', code):
        return ("typescript", "angular")
    if re.search(r'\bfrom\s+vue\b|export\s+default\s+\{|<template>|@click', code):
        return ("javascript", "vue")
    if re.search(r'package\s+main|func\s+main\(\)|import\s+"fmt"', code):
        return ("go", "go")
    if re.search(r'\buse\s+std::|fn\s+main\(\)|let\s+mut\s+', code):
        return ("rust", "rust")
    if re.search(r'public\s+class|@Entity|@Service|@RestController', code):
        return ("java", "spring")
    if re.search(r'namespace\s+\w+|using\s+System|public\s+class', code):
        return ("csharp", "dotnet")
    
    # Language-only detection
    if re.search(r'\bdef\s+\w+\(|import\s+\w+|from\s+\w+\s+import', code):
        return ("python", "python")
    if re.search(r'\bfunction\s+\w+|const\s+\w+\s*=|let\s+\w+\s*=|var\s+\w+\s*=', code):
        return ("javascript", "javascript")
    if re.search(r'interface\s+\w+|type\s+\w+\s*=|:\s*\w+\s*[=;]', code) and re.search(r'\bconst\s+\w+:|function\s+\w+', code):
        return ("typescript", "typescript")
    if re.search(r'<\?php|function\s+\w+\s*\(|->\w+\(', code):
        return ("php", "php")
    if re.search(r'#include|int\s+main\(|printf\(|std::', code):
        return ("cpp", "cpp")
    
    return ("unknown", "general")


def build_prompt(language: str, framework: str) -> str:
    """Build a dynamic prompt based on detected language and framework."""
    
    framework_contexts = {
        "django": "Focus on Django-specific patterns: ORM queries (N+1, select_related, prefetch_related), middleware, views (class-based vs function-based), security (CSRF, XSS, SQL injection), template rendering, and Django best practices.",
        "flask": "Focus on Flask patterns: route decorators, request handling, blueprint organization, database sessions, security (CSRF, input validation), and Flask extensions.",
        "fastapi": "Focus on FastAPI patterns: Pydantic models, dependency injection, async/await usage, OpenAPI documentation, request/response validation, and performance optimization.",
        "react": "Focus on React patterns: hooks usage (useState, useEffect, useMemo, useCallback), component structure, props drilling, state management, re-renders, performance (React.memo, useMemo), and JSX best practices.",
        "nodejs": "Focus on Node.js patterns: async/await vs callbacks, error handling, event loop blocking, memory leaks, module patterns (CommonJS vs ES6), and Node.js best practices.",
        "express": "Focus on Express.js patterns: middleware usage, route organization, error handling, request validation, security (helmet, CORS), and Express best practices.",
        "nextjs": "Focus on Next.js patterns: SSR vs SSG, API routes, image optimization, routing, data fetching (getServerSideProps, getStaticProps), and Next.js best practices.",
        "angular": "Focus on Angular patterns: component lifecycle, dependency injection, RxJS observables, change detection, services, modules, and Angular best practices.",
        "vue": "Focus on Vue.js patterns: reactivity system, computed properties, watchers, component composition, Vuex/Pinia state management, and Vue best practices.",
        "go": "Focus on Go patterns: goroutines, channels, error handling, interfaces, package organization, and Go idioms.",
        "rust": "Focus on Rust patterns: ownership, borrowing, lifetimes, error handling (Result, Option), memory safety, and Rust best practices.",
        "spring": "Focus on Spring patterns: dependency injection, annotations, transaction management, REST controllers, service layer, and Spring best practices.",
        "dotnet": "Focus on .NET patterns: async/await, LINQ, dependency injection, Entity Framework, controllers, and .NET best practices.",
        "python": "Focus on Python patterns: PEP 8, type hints, list comprehensions, generators, exception handling, and Pythonic code.",
        "javascript": "Focus on JavaScript patterns: ES6+ features, async/await, closures, scope, hoisting, and modern JavaScript best practices.",
        "typescript": "Focus on TypeScript patterns: type safety, interfaces, generics, strict mode, and TypeScript best practices.",
        "php": "Focus on PHP patterns: PSR standards, namespaces, type declarations, error handling, and modern PHP practices.",
        "cpp": "Focus on C++ patterns: memory management, RAII, STL usage, smart pointers, and modern C++ practices.",
    }
    
    framework_guidance = framework_contexts.get(framework, "Focus on general code quality, best practices, and maintainability.")
    
    performance_contexts = {
        "django": "ORM queries, database optimization, select_related/prefetch_related, query optimization",
        "react": "Component re-renders, virtual DOM efficiency, bundle size, lazy loading",
        "nodejs": "Event loop blocking, memory usage, async operations, I/O efficiency",
        "express": "Middleware performance, route optimization, database queries",
        "nextjs": "SSR/SSG performance, image optimization, bundle size, API route efficiency",
        "python": "List comprehensions, generator expressions, algorithm efficiency",
        "javascript": "Event loop, async operations, memory leaks, bundle optimization",
        "general": "Algorithm efficiency, memory usage, I/O operations",
    }
    
    perf_guidance = performance_contexts.get(framework, performance_contexts.get(language, "general performance considerations"))
    
    return f"""
You are an elite software architect performing code review for {framework.upper() if framework != "general" else language.upper()} code. 
Produce a JSON object with this schema:
{{
  "detected_tech": {{
    "language": "{language}",
    "framework": "{framework}"
  }},
  "summary": {{
    "overview": "one paragraph explaining key issues and sentiment",
    "highlights": ["bullet point", "..."],
    "next_steps": ["action item", "..."]
  }},
  "critical": [{{"title": "", "details": "", "severity": "critical|high|medium"}}],
  "best_practices": [{{"title": "", "details": "", "status": "met|partial|missing"}}],
  "performance": [{{"title": "", "details": "", "impact": "{perf_guidance}"}}],
  "strengths": ["short bullet", "..."]
}}

Context:
{framework_guidance}

Performance focus: {perf_guidance}

Rules:
- Answer in valid JSON only. Do not wrap with markdown fences.
- Limit each list to at most 5 items, sorted by severity/impact.
- Reference concrete code snippets or line numbers when possible.
- Adapt your review to {framework.upper() if framework != "general" else language.upper()} conventions and best practices.
"""


def analyze_code(code: str) -> Dict[str, Any]:
    """Send the provided code to Gemini and return a normalized review payload."""
    if not settings.GEMINI_API_KEY:
        raise GeminiAPIError("Gemini API key is missing. Set GEMINI_API_KEY in your environment.")

    # Detect code type
    language, framework = detect_code_type(code)
    logger.info(f"Detected code type: {language}/{framework}")
    
    # Build dynamic prompt
    prompt = build_prompt(language, framework)

    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel(MODEL_NAME)

    try:
        response = model.generate_content(
            [prompt, f"Code snippet to review:\n```code\n{code}\n```"],
            generation_config={"response_mime_type": "application/json", "temperature": 0.25},
        )
    except google_exceptions.GoogleAPIError as exc:  # pragma: no cover - network layer
        logger.exception("Gemini API responded with error")
        detail = getattr(exc, "message", str(exc)) or exc.__class__.__name__
        raise GeminiAPIError(f"Gemini API request failed: {detail}") from exc
    except Exception as exc:  # pragma: no cover - network layer
        logger.exception("Gemini API client raised unexpected error")
        raise GeminiAPIError(f"Gemini API request failed: {exc}") from exc

    payload = (response.text or "").strip()
    if not payload:
        raise GeminiAPIError("Gemini API returned an empty response.")

    try:
        raw = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise GeminiAPIError("Gemini API responded with malformed JSON.") from exc

    # Ensure detected_tech is included
    if "detected_tech" not in raw:
        raw["detected_tech"] = {"language": language, "framework": framework}

    return _normalize_review(raw)


def _normalize_review(data: Dict[str, Any]) -> Dict[str, Any]:
    def _ensure_list(items: Any) -> List[Any]:
        return items if isinstance(items, list) else []

    def _ensure_dict(value: Any) -> Dict[str, Any]:
        return value if isinstance(value, dict) else {}

    detected_tech = _ensure_dict(data.get("detected_tech"))
    summary = _ensure_dict(data.get("summary"))
    return {
        "detected_tech": {
            "language": detected_tech.get("language", "unknown"),
            "framework": detected_tech.get("framework", "general"),
        },
        "summary": {
            "overview": summary.get("overview", "No summary provided."),
            "highlights": _ensure_list(summary.get("highlights")),
            "next_steps": _ensure_list(summary.get("next_steps")),
        },
        "critical": _sanitize_issue_list(data.get("critical"), ("title", "details", "severity")),
        "best_practices": _sanitize_issue_list(
            data.get("best_practices"), ("title", "details", "status")
        ),
        "performance": _sanitize_issue_list(
            data.get("performance"), ("title", "details", "impact")
        ),
        "strengths": [str(item) for item in _ensure_list(data.get("strengths")) if str(item).strip()],
    }


def _sanitize_issue_list(items: Any, fields: tuple[str, str, str]) -> List[Dict[str, str]]:
    sanitized: List[Dict[str, str]] = []
    if not isinstance(items, list):
        return sanitized

    for item in items:
        if not isinstance(item, dict):
            continue
        sanitized.append({field: str(item.get(field, "")).strip() for field in fields})
    return sanitized

