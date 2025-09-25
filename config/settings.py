"""
Configuration management for the Dynamic Schema Parser.
"""

import os
from pathlib import Path
from typing import Optional
from src.models import Config, ScrapingConfig, StorageConfig


def load_config(config_file: Optional[str] = None) -> Config:
    """Load configuration from file or environment variables."""
    
    # Default configuration
    config = Config()
    
    # Override with environment variables
    config.scraping.max_pages = int(os.getenv("MAX_PAGES", config.scraping.max_pages))
    config.scraping.max_depth = int(os.getenv("MAX_DEPTH", config.scraping.max_depth))
    config.scraping.delay_between_requests = float(os.getenv("DELAY_BETWEEN_REQUESTS", config.scraping.delay_between_requests))
    config.scraping.timeout = int(os.getenv("TIMEOUT", config.scraping.timeout))
    config.scraping.user_agent = os.getenv("USER_AGENT", config.scraping.user_agent)
    
    config.storage.output_dir = os.getenv("OUTPUT_DIR", config.storage.output_dir)
    config.storage.create_directories = os.getenv("CREATE_DIRECTORIES", "true").lower() == "true"
    config.storage.preserve_structure = os.getenv("PRESERVE_STRUCTURE", "true").lower() == "true"
    
    config.parallel_workers = int(os.getenv("PARALLEL_WORKERS", config.parallel_workers))
    config.log_level = os.getenv("LOG_LEVEL", config.log_level)
    
    # Load from config file if provided
    if config_file and os.path.exists(config_file):
        import json
        with open(config_file, 'r') as f:
            file_config = json.load(f)
            
        if 'scraping' in file_config:
            for key, value in file_config['scraping'].items():
                if hasattr(config.scraping, key):
                    setattr(config.scraping, key, value)
                    
        if 'storage' in file_config:
            for key, value in file_config['storage'].items():
                if hasattr(config.storage, key):
                    setattr(config.storage, key, value)
    
    return config


def get_schema_org_cache_path() -> Path:
    """Get the path for caching schema.org definitions."""
    cache_dir = Path.home() / ".dynamic_schema" / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / "schema_org.jsonld"


def get_log_config() -> dict:
    """Get logging configuration."""
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "default",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.FileHandler",
                "level": "DEBUG",
                "formatter": "default",
                "filename": "dynamic_schema.log",
                "mode": "a",
            },
        },
        "loggers": {
            "": {
                "level": "DEBUG",
                "handlers": ["console", "file"],
                "propagate": False,
            },
        },
    }

