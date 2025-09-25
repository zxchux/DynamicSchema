from __future__ import annotations

import json
from pathlib import Path
from typing import Union
from urllib.parse import urlparse

from src.models import StorageConfig
from pydantic import HttpUrl


class SchemaStorage:
    def __init__(self, config: StorageConfig) -> None:
        self.config = config
        Path(self.config.output_dir).mkdir(parents=True, exist_ok=True)

    def _path_for_url(self, page_url: Union[str, HttpUrl]) -> Path:
        # Convert HttpUrl to string if needed
        url_str = str(page_url)
        parsed = urlparse(url_str)
        domain = parsed.netloc
        path = parsed.path
        segments = [seg for seg in path.split("/") if seg]
        base = Path(self.config.output_dir) / domain
        if not segments:
            return base / "index" / "schema.json"
        last = segments[-1]
        # If last segment has extension, strip it
        if "." in last:
            last = last.split(".", 1)[0]
        dir_path = base.joinpath(*segments[:-1], last)
        return dir_path / "schema.json"

    def save_jsonld_for_url(self, page_url: Union[str, HttpUrl], data: dict) -> Path:
        target = self._path_for_url(page_url)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return target


