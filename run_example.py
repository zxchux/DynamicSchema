#!/usr/bin/env python3
"""
Quick example script to demonstrate the Dynamic Schema Parser.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.scraper import WebsiteCrawler
from src.schema_parser import SchemaAIParser
from src.storage import SchemaStorage
from src.schema_validator import SchemaOrgValidator
from config.settings import load_config


async def run_example():
    """Run a simple example of the schema parser."""
    
    print("🚀 Dynamic Schema Parser Example")
    print("=" * 50)
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Please set OPENAI_API_KEY environment variable")
        print("   export OPENAI_API_KEY=sk-your-key-here")
        return
    
    # Load configuration
    config = load_config()
    config.scraping.max_pages = 3  # Small example
    config.scraping.max_depth = 2
    config.storage.output_dir = "./example_output"
    
    print(f"📁 Output directory: {config.storage.output_dir}")
    print(f"🔍 Max pages: {config.scraping.max_pages}")
    print(f"📏 Max depth: {config.scraping.max_depth}")
    print()
    
    # Initialize components
    crawler = WebsiteCrawler("https://httpbin.org", config)
    storage = SchemaStorage(config.storage)
    ai_parser = SchemaAIParser()
    validator = SchemaOrgValidator()
    
    print("🌐 Starting website crawl...")
    print()
    
    page_count = 0
    schema_count = 0
    
    try:
        async for page in crawler.iter_pages():
            page_count += 1
            print(f"📄 Page {page_count}: {page.url}")
            print(f"   Title: {page.page_title}")
            
            # Extract or generate JSON-LD
            jsonld_objects = await ai_parser.extract_or_generate_jsonld(
                page_url=page.url,
                html=page.raw_html or "",
                title=page.page_title,
            )
            
            if jsonld_objects:
                print(f"   📋 Found {len(jsonld_objects)} schema(s)")
                
                # Process each JSON-LD object
                for i, jsonld_obj in enumerate(jsonld_objects):
                    schema_count += 1
                    
                    # Validate
                    errors = validator.validate_jsonld(jsonld_obj)
                    if errors:
                        print(f"   ⚠️  Schema {i+1} validation errors: {len(errors)}")
                    else:
                        print(f"   ✅ Schema {i+1} is valid")
                    
                    # Save to file
                    file_path = storage.save_jsonld_for_url(page.url, jsonld_obj)
                    print(f"   💾 Saved to: {file_path}")
            else:
                print("   ❌ No schemas found/generated")
            
            print()
            
            if page_count >= config.scraping.max_pages:
                break
    
    except KeyboardInterrupt:
        print("\n⏹️  Crawling interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during crawling: {e}")
    
    print("=" * 50)
    print(f"📊 Summary:")
    print(f"   Pages processed: {page_count}")
    print(f"   Schemas generated: {schema_count}")
    print(f"   Output directory: {config.storage.output_dir}")
    
    if schema_count > 0:
        print("\n🎉 Example completed successfully!")
        print("   Check the output directory for generated JSON-LD files.")
    else:
        print("\n💡 No schemas were generated.")
        print("   This might be due to:")
        print("   - No embedded JSON-LD found")
        print("   - AI generation failed (check API key)")
        print("   - Network issues")


if __name__ == "__main__":
    asyncio.run(run_example())

