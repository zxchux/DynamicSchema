from __future__ import annotations

import asyncio
import re
from collections import deque
from dataclasses import dataclass
from typing import AsyncGenerator, Iterable
from urllib.parse import urljoin, urlparse

import aiohttp
from bs4 import BeautifulSoup

from src.models import PageSchema, ScrapingConfig, Config


_LINK_SELECTOR = "a[href]"
_ALLOWED_SCHEMES = {"http", "https"}


@dataclass(slots=True)
class CrawledPage:
    url: str
    page_title: str
    raw_html: str


class WebsiteCrawler:
    def __init__(self, base_url: str, config: Config) -> None:
        self.base_url = base_url.rstrip("/")
        self.config: ScrapingConfig = config.scraping
        self._parsed_base = urlparse(self.base_url)

    def _is_same_domain(self, url: str) -> bool:
        parsed = urlparse(url)
        return parsed.scheme in _ALLOWED_SCHEMES and parsed.netloc == self._parsed_base.netloc

    def _normalize(self, url: str) -> str:
        url = url.split("#", 1)[0]
        # Remove typical tracking query params
        url = re.sub(r"([?&])(utm_[^=&]+|fbclid|gclid)=[^&]*", r"\\1", url)
        url = re.sub(r"[?&]+$", "", url)
        return url

    async def _fetch(self, session: aiohttp.ClientSession, url: str) -> CrawledPage | None:
        try:
            async with session.get(url, timeout=self.config.timeout, allow_redirects=self.config.follow_redirects) as resp:
                if resp.status >= 400:
                    return None
                html = await resp.text(errors="ignore")
        except Exception:  # noqa: BLE001
            return None

        soup = BeautifulSoup(html, "lxml")
        title_el = soup.find("title")
        title = title_el.text.strip() if title_el else url
        return CrawledPage(url=url, page_title=title, raw_html=str(soup))

    def _extract_links(self, html: str, base_url: str) -> Iterable[str]:
        soup = BeautifulSoup(html, "lxml")
        for a in soup.select(_LINK_SELECTOR):
            href = a.get("href")
            if not href:
                continue
            absolute = urljoin(base_url, href)
            absolute = self._normalize(absolute)
            if self._is_same_domain(absolute):
                yield absolute

    async def iter_pages(self) -> AsyncGenerator[PageSchema, None]:
        visited: set[str] = set()
        queue: deque[tuple[str, int]] = deque([(self.base_url, 0)])

        headers = {"User-Agent": self.config.user_agent}
        connector = aiohttp.TCPConnector(limit_per_host=8)
        async with aiohttp.ClientSession(headers=headers, connector=connector) as session:
            while queue and len(visited) < self.config.max_pages:
                url, depth = queue.popleft()
                if url in visited or depth > self.config.max_depth:
                    continue

                visited.add(url)
                page = await self._fetch(session, url)
                if page is None:
                    continue

                yield PageSchema(url=url, page_title=page.page_title, raw_html=page.raw_html)

                if depth < self.config.max_depth:
                    for link in self._extract_links(page.raw_html, url):
                        if link not in visited:
                            queue.append((link, depth + 1))

                if self.config.delay_between_requests > 0:
                    await asyncio.sleep(self.config.delay_between_requests)


