from __future__ import annotations

import json
import os
from typing import Any, List

from bs4 import BeautifulSoup


def _extract_embedded_jsonld(html: str) -> List[dict[str, Any]]:
    soup = BeautifulSoup(html, "lxml")
    results: List[dict[str, Any]] = []
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            data = json.loads(script.string or "{}")
            if isinstance(data, list):
                results.extend([obj for obj in data if isinstance(obj, dict)])
            elif isinstance(data, dict):
                results.append(data)
        except Exception:  # noqa: BLE001
            continue
    return results


_SYSTEM_PROMPT = (
    "You are a web semantics expert. Given an HTML page, produce a valid JSON-LD "
    "object using schema.org vocabulary that best represents the primary content. "
    "Return ONLY a JSON object (no prose). Use '@context': 'https://schema.org'. "
    "Include '@type', 'url', 'name', and 'description' when possible, and nest related entities."
)


class SchemaAIParser:
    def __init__(self) -> None:
        self._provider = os.getenv("AI_PROVIDER", "openai").lower()
        self._model = os.getenv("AI_MODEL", "gpt-4o-mini")

    async def _ai_generate(self, page_url: str, html: str, title: str) -> List[dict[str, Any]]:
        # Lazy import so that dependency is optional
        from openai import AsyncOpenAI  # type: ignore

        client = AsyncOpenAI()
        prompt = (
            f"URL: {page_url}\n"
            f"Title: {title}\n"
            "HTML (truncated to relevant parts may be okay):\n\n" + html
        )
        resp = await client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        content = resp.choices[0].message.content or "{}"
        try:
            obj = json.loads(content)
            if isinstance(obj, dict):
                return [obj]
            if isinstance(obj, list):
                return [o for o in obj if isinstance(o, dict)]
        except Exception:  # noqa: BLE001
            return []
        return []

    async def extract_or_generate_jsonld(self, page_url: str, html: str, title: str) -> List[dict[str, Any]]:
        existing = _extract_embedded_jsonld(html)
        if existing:
            return existing

        # Fallback to AI generation if no embedded JSON-LD exists
        try:
            return await self._ai_generate(page_url=page_url, html=html, title=title)
        except Exception:
            return []


