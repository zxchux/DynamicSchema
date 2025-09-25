"""
Example usage of the Dynamic Schema Parser.
"""

import asyncio
import os
from src.scraper import WebsiteCrawler
from src.schema_parser import SchemaAIParser
from src.storage import SchemaStorage
from src.schema_validator import SchemaOrgValidator
from config.settings import load_config


async def example_basic_usage():
    """Basic example of crawling a website and generating schemas."""
    
    # Set up environment
    os.environ["OPENAI_API_KEY"] = "your-api-key-here"
    
    # Load configuration
    config = load_config()
    config.scraping.max_pages = 5  # Limit for example
    config.scraping.max_depth = 2
    
    # Initialize components
    crawler = WebsiteCrawler("https://example.com", config)
    storage = SchemaStorage(config.storage)
    ai_parser = SchemaAIParser()
    validator = SchemaOrgValidator()
    
    print("Starting website crawl...")
    
    # Process each page
    async for page in crawler.iter_pages():
        print(f"Processing: {page.url}")
        
        # Extract or generate JSON-LD
        jsonld_objects = await ai_parser.extract_or_generate_jsonld(
            page_url=page.url,
            html=page.raw_html or "",
            title=page.page_title,
        )
        
        # Validate and save each JSON-LD object
        for i, jsonld_obj in enumerate(jsonld_objects):
            # Validate against schema.org
            errors = validator.validate_jsonld(jsonld_obj)
            if errors:
                print(f"  Validation errors: {errors}")
            else:
                print(f"  Valid JSON-LD generated")
            
            # Save to file
            file_path = storage.save_jsonld_for_url(page.url, jsonld_obj)
            print(f"  Saved to: {file_path}")


async def example_with_custom_config():
    """Example with custom configuration."""
    
    # Custom configuration
    config = load_config()
    config.scraping.max_pages = 10
    config.scraping.delay_between_requests = 0.5
    config.storage.output_dir = "./custom_schemas"
    
    # Initialize with custom config
    crawler = WebsiteCrawler("https://news.ycombinator.com", config)
    storage = SchemaStorage(config.storage)
    ai_parser = SchemaAIParser()
    
    print("Crawling Hacker News...")
    
    page_count = 0
    async for page in crawler.iter_pages():
        page_count += 1
        print(f"Page {page_count}: {page.url}")
        
        # Generate schema
        jsonld_objects = await ai_parser.extract_or_generate_jsonld(
            page_url=page.url,
            html=page.raw_html or "",
            title=page.page_title,
        )
        
        # Save each schema
        for jsonld_obj in jsonld_objects:
            storage.save_jsonld_for_url(page.url, jsonld_obj)
        
        if page_count >= 5:  # Limit for example
            break


def example_validation():
    """Example of validating JSON-LD schemas."""
    
    validator = SchemaOrgValidator()
    
    # Example valid JSON-LD
    valid_schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": "Example Article",
        "author": {
            "@type": "Person",
            "name": "John Doe"
        },
        "datePublished": "2024-01-01"
    }
    
    # Example invalid JSON-LD
    invalid_schema = {
        "@context": "https://schema.org",
        "@type": "InvalidType",
        "invalidProperty": "value"
    }
    
    # Validate schemas
    valid_errors = validator.validate_jsonld(valid_schema)
    invalid_errors = validator.validate_jsonld(invalid_schema)
    
    print(f"Valid schema errors: {valid_errors}")
    print(f"Invalid schema errors: {invalid_errors}")
    
    # List available schema types
    types = validator.get_schema_types()
    print(f"Available schema types: {len(types)}")
    print(f"First 10 types: {types[:10]}")


if __name__ == "__main__":
    print("Dynamic Schema Parser Examples")
    print("=" * 40)
    
    # Run validation example
    print("\n1. Schema Validation Example:")
    example_validation()
    
    # Uncomment to run crawling examples (requires API key)
    # print("\n2. Basic Usage Example:")
    # asyncio.run(example_basic_usage())
    
    # print("\n3. Custom Config Example:")
    # asyncio.run(example_with_custom_config())

