"""
Tests for the Dynamic Schema Parser.
"""

import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
from src.schema_parser import SchemaAIParser, _extract_embedded_jsonld
from src.schema_validator import SchemaOrgValidator
from src.storage import SchemaStorage
from src.models import StorageConfig


class TestSchemaParser:
    """Test cases for schema parsing functionality."""
    
    def test_extract_embedded_jsonld(self):
        """Test extraction of embedded JSON-LD from HTML."""
        html_with_jsonld = """
        <html>
        <head>
            <script type="application/ld+json">
            {
                "@context": "https://schema.org",
                "@type": "Article",
                "headline": "Test Article"
            }
            </script>
        </head>
        <body>Content</body>
        </html>
        """
        
        result = _extract_embedded_jsonld(html_with_jsonld)
        assert len(result) == 1
        assert result[0]["@type"] == "Article"
        assert result[0]["headline"] == "Test Article"
    
    def test_extract_embedded_jsonld_multiple(self):
        """Test extraction of multiple JSON-LD objects."""
        html_with_multiple = """
        <html>
        <head>
            <script type="application/ld+json">
            {"@context": "https://schema.org", "@type": "Article", "headline": "Article 1"}
            </script>
            <script type="application/ld+json">
            {"@context": "https://schema.org", "@type": "Person", "name": "John Doe"}
            </script>
        </head>
        </html>
        """
        
        result = _extract_embedded_jsonld(html_with_multiple)
        assert len(result) == 2
        assert result[0]["@type"] == "Article"
        assert result[1]["@type"] == "Person"
    
    def test_extract_embedded_jsonld_invalid(self):
        """Test handling of invalid JSON-LD."""
        html_with_invalid = """
        <html>
        <head>
            <script type="application/ld+json">
            { invalid json }
            </script>
        </head>
        </html>
        """
        
        result = _extract_embedded_jsonld(html_with_invalid)
        assert len(result) == 0
    
    @pytest.mark.asyncio
    async def test_ai_generate_fallback(self):
        """Test AI generation when no embedded JSON-LD exists."""
        parser = SchemaAIParser()
        
        # Mock the AI client
        with patch('src.schema_parser.AsyncOpenAI') as mock_openai:
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client
            
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = '{"@context": "https://schema.org", "@type": "Article", "headline": "AI Generated"}'
            mock_client.chat.completions.create.return_value = mock_response
            
            result = await parser.extract_or_generate_jsonld(
                page_url="https://example.com",
                html="<html><body>Content</body></html>",
                title="Test Page"
            )
            
            assert len(result) == 1
            assert result[0]["@type"] == "Article"
            assert result[0]["headline"] == "AI Generated"


class TestSchemaValidator:
    """Test cases for schema validation functionality."""
    
    def test_validate_jsonld_valid(self):
        """Test validation of valid JSON-LD."""
        validator = SchemaOrgValidator()
        
        valid_schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": "Test Article"
        }
        
        errors = validator.validate_jsonld(valid_schema)
        assert len(errors) == 0
    
    def test_validate_jsonld_missing_context(self):
        """Test validation with missing @context."""
        validator = SchemaOrgValidator()
        
        invalid_schema = {
            "@type": "Article",
            "headline": "Test Article"
        }
        
        errors = validator.validate_jsonld(invalid_schema)
        assert "Missing required @context field" in errors
    
    def test_validate_jsonld_missing_type(self):
        """Test validation with missing @type."""
        validator = SchemaOrgValidator()
        
        invalid_schema = {
            "@context": "https://schema.org",
            "headline": "Test Article"
        }
        
        errors = validator.validate_jsonld(invalid_schema)
        assert "Missing required @type field" in errors
    
    def test_validate_jsonld_wrong_context(self):
        """Test validation with wrong @context."""
        validator = SchemaOrgValidator()
        
        invalid_schema = {
            "@context": "https://example.com",
            "@type": "Article",
            "headline": "Test Article"
        }
        
        errors = validator.validate_jsonld(invalid_schema)
        assert "@context must be 'https://schema.org'" in errors


class TestStorage:
    """Test cases for storage functionality."""
    
    def test_path_generation(self):
        """Test path generation for different URLs."""
        config = StorageConfig(output_dir="./test_schemas")
        storage = SchemaStorage(config)
        
        # Test root URL
        path = storage._path_for_url("https://example.com/")
        assert str(path).endswith("example.com/index/schema.json")
        
        # Test nested URL
        path = storage._path_for_url("https://example.com/blog/post")
        assert str(path).endswith("example.com/blog/post/schema.json")
        
        # Test URL with file extension
        path = storage._path_for_url("https://example.com/page.html")
        assert str(path).endswith("example.com/page/schema.json")
    
    def test_save_jsonld(self):
        """Test saving JSON-LD to file."""
        import tempfile
        import os
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config = StorageConfig(output_dir=temp_dir)
            storage = SchemaStorage(config)
            
            test_data = {
                "@context": "https://schema.org",
                "@type": "Article",
                "headline": "Test Article"
            }
            
            file_path = storage.save_jsonld_for_url("https://example.com/test", test_data)
            
            assert os.path.exists(file_path)
            
            with open(file_path, 'r') as f:
                saved_data = json.load(f)
            
            assert saved_data == test_data


if __name__ == "__main__":
    pytest.main([__file__])

