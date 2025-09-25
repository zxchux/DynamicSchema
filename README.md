# Dynamic Schema Parser

A scalable solution for building and deploying schema definitions for websites by parsing pages and identifying nested schema architecture referencing schema.org.

## Features

- **Web Scraping**: Parse all pages of a given website
- **Schema.org Integration**: Fetch and validate schema definitions from schema.org
  - Uses embedded JSON-LD when present; otherwise generates with AI (OpenAI)
- **Nested Schema Detection**: Identify complex nested schema architectures
- **Structured Storage**: Store JSON schemas in a directory structure mirroring the website
- **Async Processing**: High-performance concurrent processing
- **CLI Interface**: Easy-to-use command-line interface

## Installation

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
export OPENAI_API_KEY=sk-...
python main.py --url https://example.com --output ./schemas
```

## Project Structure

```
DynamicSchema/
├── main.py                 # CLI entry point
├── src/
│   ├── __init__.py
│   ├── scraper.py         # Web scraping functionality
│   ├── schema_parser.py   # Schema.org integration and parsing
│   ├── storage.py         # JSON storage management
│   └── models.py          # Data models and schemas
├── config/
│   └── settings.py        # Configuration management
├── tests/
│   └── test_schema_parser.py
├── requirements.txt
└── README.md
```

## Architecture

1. **Web Scraper**: Crawls websites and extracts page content
2. **Schema Parser**: Identifies and validates schema.org schemas
   - Uses embedded JSON-LD when present; otherwise generates with AI (OpenAI)
3. **Storage Manager**: Organizes and stores schemas in JSON format
4. **Schema Validator**: Validates JSON-LD against schema.org definitions
5. **CLI Interface**: Provides easy command-line access to all functionality

## Quick Start

1. **Install dependencies:**
   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Set up API key:**
   ```bash
   export OPENAI_API_KEY=sk-your-openai-api-key-here
   ```

3. **Run the parser:**
   ```bash
   python main.py --url https://example.com --output ./schemas
   ```

4. **Or try the example:**
   ```bash
   python run_example.py
   ```

## Features Implemented

✅ **Web Scraping**: Async crawler with configurable depth and page limits  
✅ **AI-Powered Schema Generation**: Uses OpenAI to generate JSON-LD when none exists  
✅ **Schema.org Integration**: Validates against official schema.org definitions  
✅ **Structured Storage**: Saves JSON-LD files mirroring website structure  
✅ **CLI Interface**: Easy-to-use command-line tool  
✅ **Configuration Management**: Environment variables and config files  
✅ **Error Handling**: Comprehensive error handling and logging  
✅ **Testing**: Unit tests for core functionality  
✅ **Examples**: Working examples and documentation

