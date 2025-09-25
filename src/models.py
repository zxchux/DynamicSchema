"""
Data models and schemas for the Dynamic Schema Parser.
"""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
import json


class SchemaProperty(BaseModel):
    """Represents a property within a schema."""
    name: str
    type: str
    description: Optional[str] = None
    required: bool = False
    enum_values: Optional[List[str]] = None
    properties: Optional[Dict[str, 'SchemaProperty']] = None


class SchemaDefinition(BaseModel):
    """Represents a complete schema definition."""
    id: str
    name: str
    type: str
    description: Optional[str] = None
    properties: Dict[str, SchemaProperty] = Field(default_factory=dict)
    extends: Optional[str] = None
    context: str = "https://schema.org"
    source_url: Optional[HttpUrl] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class PageSchema(BaseModel):
    """Represents schemas found on a specific page."""
    url: HttpUrl
    page_title: str
    schemas: List[SchemaDefinition] = Field(default_factory=list)
    raw_html: Optional[str] = None
    extracted_at: datetime = Field(default_factory=datetime.now)
    errors: List[str] = Field(default_factory=list)


class WebsiteSchema(BaseModel):
    """Represents all schemas for an entire website."""
    domain: str
    base_url: HttpUrl
    pages: List[PageSchema] = Field(default_factory=list)
    total_pages: int = 0
    total_schemas: int = 0
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)


class ScrapingConfig(BaseModel):
    """Configuration for web scraping."""
    max_pages: int = 100
    max_depth: int = 3
    delay_between_requests: float = 1.0
    timeout: int = 30
    user_agent: str = "DynamicSchemaParser/1.0"
    follow_redirects: bool = True
    respect_robots_txt: bool = True
    allowed_domains: Optional[List[str]] = None
    excluded_paths: List[str] = Field(default_factory=lambda: [
        "/admin", "/login", "/logout", "/api/", "/static/", "/assets/"
    ])


class StorageConfig(BaseModel):
    """Configuration for schema storage."""
    output_dir: str = "./schemas"
    create_directories: bool = True
    preserve_structure: bool = True
    include_metadata: bool = True
    compression: bool = False
    format: str = "json"  # json, yaml, xml


class Config(BaseModel):
    """Main configuration for the application."""
    scraping: ScrapingConfig = Field(default_factory=ScrapingConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    schema_org_api: str = "https://schema.org/version/latest/schemaorg-current-https.jsonld"
    parallel_workers: int = 5
    log_level: str = "INFO"

