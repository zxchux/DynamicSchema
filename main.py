import asyncio
import logging
import logging.config
from urllib.parse import urlparse

import click

from config.settings import load_config, get_log_config
from src.scraper import WebsiteCrawler
from src.schema_parser import SchemaAIParser
from src.storage import SchemaStorage


@click.command()
@click.option("--url", required=True, help="Base URL of the website to crawl")
@click.option("--output", default="./schemas", help="Output directory for JSON-LD files")
@click.option("--max-pages", default=None, type=int, help="Maximum number of pages to crawl")
@click.option("--max-depth", default=None, type=int, help="Maximum crawl depth")
@click.option("--config", "config_file", default=None, help="Optional path to JSON config file")
def cli(url: str, output: str, max_pages: int | None, max_depth: int | None, config_file: str | None) -> None:
    """Entry point for the Dynamic Schema Parser CLI."""
    config = load_config(config_file)
    if max_pages is not None:
        config.scraping.max_pages = max_pages
    if max_depth is not None:
        config.scraping.max_depth = max_depth
    config.storage.output_dir = output

    logging.config.dictConfig(get_log_config())
    logger = logging.getLogger("dynamic_schema")

    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise click.ClickException("Invalid URL provided.")

    crawler = WebsiteCrawler(base_url=url, config=config)
    storage = SchemaStorage(config.storage)
    ai_parser = SchemaAIParser()

    async def run() -> None:
        async for page in crawler.iter_pages():
            try:
                jsonld_objects = await ai_parser.extract_or_generate_jsonld(
                    page_url=page.url,
                    html=page.raw_html or "",
                    title=page.page_title,
                )
                for obj in jsonld_objects:
                    storage.save_jsonld_for_url(page.url, obj)
            except Exception as exc:  # noqa: BLE001
                logger.exception("Failed processing %s: %s", page.url, exc)

    asyncio.run(run())


if __name__ == "__main__":
    cli()


