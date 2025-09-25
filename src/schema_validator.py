"""
Schema.org validation and integration functionality.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin

import requests
from jsonschema import validate, ValidationError, Draft7Validator

from config.settings import get_schema_org_cache_path

logger = logging.getLogger(__name__)


class SchemaOrgValidator:
    """Validates JSON-LD against schema.org definitions."""
    
    def __init__(self):
        self.schema_cache_path = get_schema_org_cache_path()
        self.schema_definitions: Dict[str, Any] = {}
        self._load_schema_definitions()
    
    def _load_schema_definitions(self) -> None:
        """Load schema.org definitions from cache or fetch from source."""
        if self.schema_cache_path.exists():
            try:
                with open(self.schema_cache_path, 'r', encoding='utf-8') as f:
                    self.schema_definitions = json.load(f)
                logger.info("Loaded schema.org definitions from cache")
                return
            except Exception as e:
                logger.warning(f"Failed to load cached schema definitions: {e}")
        
        # Fetch from schema.org if cache doesn't exist or is invalid
        self._fetch_schema_definitions()
    
    def _fetch_schema_definitions(self) -> None:
        """Fetch latest schema.org definitions."""
        try:
            url = "https://schema.org/version/latest/schemaorg-current-https.jsonld"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            self.schema_definitions = response.json()
            
            # Cache the definitions
            self.schema_cache_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.schema_cache_path, 'w', encoding='utf-8') as f:
                json.dump(self.schema_definitions, f, indent=2)
            
            logger.info("Fetched and cached latest schema.org definitions")
        except Exception as e:
            logger.error(f"Failed to fetch schema.org definitions: {e}")
            self.schema_definitions = {}
    
    def validate_jsonld(self, jsonld_data: Dict[str, Any]) -> List[str]:
        """
        Validate JSON-LD data against schema.org definitions.
        
        Args:
            jsonld_data: The JSON-LD object to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        if not isinstance(jsonld_data, dict):
            errors.append("JSON-LD data must be a dictionary")
            return errors
        
        # Check for required @context
        if "@context" not in jsonld_data:
            errors.append("Missing required @context field")
        elif jsonld_data["@context"] != "https://schema.org":
            errors.append("@context must be 'https://schema.org'")
        
        # Check for @type
        if "@type" not in jsonld_data:
            errors.append("Missing required @type field")
        else:
            type_name = jsonld_data["@type"]
            if not self._is_valid_schema_type(type_name):
                errors.append(f"Unknown schema.org type: {type_name}")
        
        # Validate properties if schema definition exists
        if "@type" in jsonld_data and not errors:
            type_name = jsonld_data["@type"]
            schema_def = self._get_schema_definition(type_name)
            if schema_def:
                property_errors = self._validate_properties(jsonld_data, schema_def)
                errors.extend(property_errors)
        
        return errors
    
    def _is_valid_schema_type(self, type_name: str) -> bool:
        """Check if a type name is valid in schema.org."""
        if not self.schema_definitions:
            return True  # Can't validate without definitions
        
        # Look for the type in the schema definitions
        for item in self.schema_definitions.get("@graph", []):
            if item.get("@type") == "rdfs:Class" and item.get("@id") == f"https://schema.org/{type_name}":
                return True
        
        return False
    
    def _get_schema_definition(self, type_name: str) -> Optional[Dict[str, Any]]:
        """Get schema definition for a specific type."""
        if not self.schema_definitions:
            return None
        
        for item in self.schema_definitions.get("@graph", []):
            if item.get("@type") == "rdfs:Class" and item.get("@id") == f"https://schema.org/{type_name}":
                return item
        
        return None
    
    def _validate_properties(self, jsonld_data: Dict[str, Any], schema_def: Dict[str, Any]) -> List[str]:
        """Validate properties against schema definition."""
        errors = []
        
        # This is a simplified validation - in practice, you'd want to
        # implement more comprehensive property validation based on the
        # schema.org definitions
        
        for prop_name, prop_value in jsonld_data.items():
            if prop_name.startswith("@"):
                continue  # Skip JSON-LD keywords
            
            # Check if property is valid for this type
            if not self._is_valid_property_for_type(prop_name, schema_def):
                errors.append(f"Property '{prop_name}' is not valid for type '{jsonld_data.get('@type')}'")
        
        return errors
    
    def _is_valid_property_for_type(self, prop_name: str, schema_def: Dict[str, Any]) -> bool:
        """Check if a property is valid for a given schema type."""
        # This is a simplified check - in practice, you'd traverse the
        # inheritance hierarchy and check all properties
        return True  # For now, assume all properties are valid
    
    def get_schema_types(self) -> List[str]:
        """Get list of available schema.org types."""
        if not self.schema_definitions:
            return []
        
        types = []
        for item in self.schema_definitions.get("@graph", []):
            if item.get("@type") == "rdfs:Class":
                type_id = item.get("@id", "")
                if type_id.startswith("https://schema.org/"):
                    types.append(type_id.replace("https://schema.org/", ""))
        
        return sorted(types)
    
    def get_type_properties(self, type_name: str) -> List[str]:
        """Get properties available for a specific schema type."""
        if not self.schema_definitions:
            return []
        
        # This is a simplified implementation
        # In practice, you'd traverse the inheritance hierarchy
        return []

