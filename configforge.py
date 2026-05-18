#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ConfigForge - Lightweight Multi-Format Configuration File Intelligent Conversion & Merging Engine
轻量级多格式配置文件智能转换与合并引擎

A zero-dependency CLI tool for converting, merging, and validating configuration files
across multiple formats (JSON, YAML, TOML, INI, ENV).
"""

__version__ = "1.0.0"
__author__ = "ConfigForge Team"
__license__ = "MIT"

import os
import sys
import json
import re
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import io

# ============================================================================
# Configuration Format Types
# ============================================================================

class ConfigFormat(Enum):
    """Supported configuration file formats."""
    JSON = "json"
    YAML = "yaml"
    TOML = "toml"
    INI = "ini"
    ENV = "env"
    AUTO = "auto"


@dataclass
class ConfigEntry:
    """Represents a single configuration entry."""
    key: str
    value: Any
    source: str = "unknown"
    line_number: int = 0
    comments: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "value": self.value,
            "source": self.source,
            "line_number": self.line_number,
            "comments": self.comments
        }


@dataclass
class ConfigDiff:
    """Represents a difference between two configurations."""
    key: str
    old_value: Any
    new_value: Any
    diff_type: str  # "added", "removed", "modified"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "diff_type": self.diff_type
        }


# ============================================================================
# JSON Parser (Zero Dependency)
# ============================================================================

class JSONParser:
    """Zero-dependency JSON parser with comment support."""
    
    @staticmethod
    def remove_comments(content: str) -> str:
        """Remove JavaScript-style comments from JSON."""
        # Remove single-line comments
        content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
        # Remove multi-line comments
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        return content
    
    @staticmethod
    def parse(content: str) -> Dict[str, Any]:
        """Parse JSON content."""
        try:
            cleaned = JSONParser.remove_comments(content)
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON parse error: {e}")
    
    @staticmethod
    def stringify(data: Dict[str, Any], indent: int = 2) -> str:
        """Convert dict to JSON string."""
        return json.dumps(data, indent=indent, ensure_ascii=False, default=str)


# ============================================================================
# YAML Parser (Zero Dependency - Simplified)
# ============================================================================

class YAMLParser:
    """Zero-dependency YAML parser (simplified implementation)."""
    
    @staticmethod
    def parse(content: str) -> Dict[str, Any]:
        """Parse YAML content (simplified)."""
        result = {}
        current_key = None
        current_indent = 0
        indent_stack = [result]
        
        lines = content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Skip empty lines and comments
            if not line.strip() or line.strip().startswith('#'):
                i += 1
                continue
            
            # Calculate indent
            indent = len(line) - len(line.lstrip())
            stripped = line.strip()
            
            # Handle key-value pairs
            if ':' in stripped and not stripped.startswith('-'):
                colon_pos = stripped.index(':')
                key = stripped[:colon_pos].strip()
                value_part = stripped[colon_pos + 1:].strip()
                
                # Determine value
                if value_part:
                    value = YAMLParser._parse_value(value_part)
                else:
                    # Check if next line is indented (nested object or list)
                    if i + 1 < len(lines):
                        next_line = lines[i + 1]
                        next_indent = len(next_line) - len(next_line.lstrip())
                        if next_indent > indent:
                            value = {}
                        else:
                            value = None
                    else:
                        value = None
                
                # Navigate to correct nesting level
                while indent < current_indent and len(indent_stack) > 1:
                    indent_stack.pop()
                    current_indent -= 2
                
                # Set the value
                current_dict = indent_stack[-1]
                if isinstance(current_dict, dict):
                    current_dict[key] = value
                    if isinstance(value, dict):
                        indent_stack.append(value)
                        current_indent = indent + 2
            
            # Handle list items
            elif stripped.startswith('- '):
                item_value = YAMLParser._parse_value(stripped[2:].strip())
                current_dict = indent_stack[-1]
                if not isinstance(current_dict, list):
                    # Convert to list if needed
                    parent = indent_stack[-2] if len(indent_stack) > 1 else result
                    for k, v in parent.items():
                        if v is current_dict:
                            parent[k] = [item_value]
                            indent_stack[-1] = parent[k]
                            break
                else:
                    current_dict.append(item_value)
            
            i += 1
        
        return result
    
    @staticmethod
    def _parse_value(value_str: str) -> Any:
        """Parse a YAML value string."""
        value_str = value_str.strip()
        
        # Remove quotes
        if (value_str.startswith('"') and value_str.endswith('"')) or \
           (value_str.startswith("'") and value_str.endswith("'")):
            return value_str[1:-1]
        
        # Boolean
        if value_str.lower() in ('true', 'yes', 'on'):
            return True
        if value_str.lower() in ('false', 'no', 'off'):
            return False
        
        # None
        if value_str.lower() in ('null', '~', 'none'):
            return None
        
        # Number
        try:
            if '.' in value_str:
                return float(value_str)
            return int(value_str)
        except ValueError:
            pass
        
        # List
        if value_str.startswith('[') and value_str.endswith(']'):
            items = [YAMLParser._parse_value(i.strip()) for i in value_str[1:-1].split(',') if i.strip()]
            return items
        
        return value_str
    
    @staticmethod
    def stringify(data: Dict[str, Any], indent: int = 2) -> str:
        """Convert dict to YAML string."""
        return YAMLParser._dict_to_yaml(data, 0, indent)
    
    @staticmethod
    def _dict_to_yaml(data: Any, level: int, indent: int) -> str:
        """Recursively convert dict to YAML."""
        spaces = ' ' * (level * indent)
        result = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, dict):
                    result.append(f"{spaces}{key}:")
                    result.append(YAMLParser._dict_to_yaml(value, level + 1, indent))
                elif isinstance(value, list):
                    result.append(f"{spaces}{key}:")
                    for item in value:
                        if isinstance(item, dict):
                            result.append(f"{spaces}{' ' * indent}-")
                            result.append(YAMLParser._dict_to_yaml(item, level + 2, indent))
                        else:
                            result.append(f"{spaces}{' ' * indent}- {YAMLParser._format_value(item)}")
                else:
                    result.append(f"{spaces}{key}: {YAMLParser._format_value(value)}")
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    result.append(f"{spaces}-")
                    result.append(YAMLParser._dict_to_yaml(item, level + 1, indent))
                else:
                    result.append(f"{spaces}- {YAMLParser._format_value(item)}")
        
        return '\n'.join(result)
    
    @staticmethod
    def _format_value(value: Any) -> str:
        """Format a value for YAML output."""
        if isinstance(value, bool):
            return 'true' if value else 'false'
        if value is None:
            return 'null'
        if isinstance(value, str):
            if ' ' in value or ':' in value or '#' in value:
                return f'"{value}"'
            return value
        return str(value)


# ============================================================================
# TOML Parser (Zero Dependency - Simplified)
# ============================================================================

class TOMLParser:
    """Zero-dependency TOML parser (simplified implementation)."""
    
    @staticmethod
    def parse(content: str) -> Dict[str, Any]:
        """Parse TOML content."""
        result = {}
        current_section = result
        current_section_name = None
        
        for line in content.split('\n'):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Section header [section] or [section.subsection]
            if line.startswith('[') and line.endswith(']'):
                section_path = line[1:-1].split('.')
                current_section = result
                for part in section_path:
                    if part not in current_section:
                        current_section[part] = {}
                    current_section = current_section[part]
                continue
            
            # Key-value pair
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = TOMLParser._parse_value(value.strip())
                current_section[key] = value
        
        return result
    
    @staticmethod
    def _parse_value(value_str: str) -> Any:
        """Parse a TOML value string."""
        value_str = value_str.strip()
        
        # String
        if value_str.startswith('"') and value_str.endswith('"'):
            return value_str[1:-1]
        if value_str.startswith("'") and value_str.endswith("'"):
            return value_str[1:-1]
        
        # Boolean
        if value_str.lower() == 'true':
            return True
        if value_str.lower() == 'false':
            return False
        
        # Number
        try:
            if '.' in value_str:
                return float(value_str)
            return int(value_str)
        except ValueError:
            pass
        
        # Array
        if value_str.startswith('[') and value_str.endswith(']'):
            items = [TOMLParser._parse_value(i.strip()) for i in value_str[1:-1].split(',') if i.strip()]
            return items
        
        return value_str
    
    @staticmethod
    def stringify(data: Dict[str, Any]) -> str:
        """Convert dict to TOML string."""
        result = []
        TOMLParser._dict_to_toml(data, result, [])
        return '\n'.join(result)
    
    @staticmethod
    def _dict_to_toml(data: Dict[str, Any], result: List[str], path: List[str]) -> None:
        """Recursively convert dict to TOML."""
        simple_items = []
        complex_items = []
        
        for key, value in data.items():
            if isinstance(value, dict):
                complex_items.append((key, value))
            else:
                simple_items.append((key, value))
        
        # Write simple items first
        if simple_items and path:
            result.append(f"[{'.'.join(path)}]")
        
        for key, value in simple_items:
            result.append(f"{key} = {TOMLParser._format_value(value)}")
        
        # Write complex items (nested tables)
        for key, value in complex_items:
            TOMLParser._dict_to_toml(value, result, path + [key])
    
    @staticmethod
    def _format_value(value: Any) -> str:
        """Format a value for TOML output."""
        if isinstance(value, bool):
            return 'true' if value else 'false'
        if value is None:
            return '""'
        if isinstance(value, str):
            return f'"{value}"'
        if isinstance(value, list):
            items = [TOMLParser._format_value(i) for i in value]
            return f"[{', '.join(items)}]"
        return str(value)


# ============================================================================
# INI Parser (Zero Dependency)
# ============================================================================

class INIParser:
    """Zero-dependency INI parser."""
    
    @staticmethod
    def parse(content: str) -> Dict[str, Any]:
        """Parse INI content."""
        result = {}
        current_section = 'default'
        result[current_section] = {}
        
        for line_num, line in enumerate(content.split('\n'), 1):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#') or line.startswith(';'):
                continue
            
            # Section header
            if line.startswith('[') and line.endswith(']'):
                current_section = line[1:-1].strip()
                if current_section not in result:
                    result[current_section] = {}
                continue
            
            # Key-value pair
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = INIParser._parse_value(value.strip())
                result[current_section][key] = value
        
        # Flatten if only default section
        if list(result.keys()) == ['default']:
            return result['default']
        
        return result
    
    @staticmethod
    def _parse_value(value_str: str) -> Any:
        """Parse an INI value string."""
        value_str = value_str.strip()
        
        # Remove quotes
        if (value_str.startswith('"') and value_str.endswith('"')) or \
           (value_str.startswith("'") and value_str.endswith("'")):
            return value_str[1:-1]
        
        # Boolean
        if value_str.lower() in ('true', 'yes', 'on', '1'):
            return True
        if value_str.lower() in ('false', 'no', 'off', '0'):
            return False
        
        # Number
        try:
            if '.' in value_str:
                return float(value_str)
            return int(value_str)
        except ValueError:
            pass
        
        return value_str
    
    @staticmethod
    def stringify(data: Dict[str, Any]) -> str:
        """Convert dict to INI string."""
        result = []
        
        # Check if data has sections
        has_sections = any(isinstance(v, dict) for v in data.values())
        
        if has_sections:
            for section, values in data.items():
                if isinstance(values, dict):
                    result.append(f"[{section}]")
                    for key, value in values.items():
                        result.append(f"{key} = {INIParser._format_value(value)}")
                    result.append("")
                else:
                    result.append(f"{section} = {INIParser._format_value(values)}")
        else:
            for key, value in data.items():
                result.append(f"{key} = {INIParser._format_value(value)}")
        
        return '\n'.join(result)
    
    @staticmethod
    def _format_value(value: Any) -> str:
        """Format a value for INI output."""
        if isinstance(value, bool):
            return 'true' if value else 'false'
        if value is None:
            return '""'
        if isinstance(value, str):
            if ' ' in value or '#' in value or ';' in value:
                return f'"{value}"'
            return value
        return str(value)


# ============================================================================
# ENV Parser (Zero Dependency)
# ============================================================================

class ENVParser:
    """Zero-dependency ENV parser."""
    
    @staticmethod
    def parse(content: str) -> Dict[str, Any]:
        """Parse ENV content."""
        result = {}
        
        for line in content.split('\n'):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Key-value pair
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = ENVParser._parse_value(value.strip())
                result[key] = value
        
        return result
    
    @staticmethod
    def _parse_value(value_str: str) -> Any:
        """Parse an ENV value string."""
        value_str = value_str.strip()
        
        # Remove quotes
        if (value_str.startswith('"') and value_str.endswith('"')) or \
           (value_str.startswith("'") and value_str.endswith("'")):
            return value_str[1:-1]
        
        # Boolean
        if value_str.lower() in ('true', 'yes', 'on', '1'):
            return True
        if value_str.lower() in ('false', 'no', 'off', '0'):
            return False
        
        # Number
        try:
            if '.' in value_str:
                return float(value_str)
            return int(value_str)
        except ValueError:
            pass
        
        return value_str
    
    @staticmethod
    def stringify(data: Dict[str, Any]) -> str:
        """Convert dict to ENV string."""
        result = []
        
        for key, value in data.items():
            result.append(f"{key}={ENVParser._format_value(value)}")
        
        return '\n'.join(result)
    
    @staticmethod
    def _format_value(value: Any) -> str:
        """Format a value for ENV output."""
        if isinstance(value, bool):
            return 'true' if value else 'false'
        if value is None:
            return '""'
        if isinstance(value, str):
            if ' ' in value or '#' in value:
                return f'"{value}"'
            return value
        return str(value)


# ============================================================================
# Main ConfigForge Engine
# ============================================================================

class ConfigForge:
    """Main configuration file conversion and merging engine."""
    
    PARSERS = {
        ConfigFormat.JSON: JSONParser,
        ConfigFormat.YAML: YAMLParser,
        ConfigFormat.TOML: TOMLParser,
        ConfigFormat.INI: INIParser,
        ConfigFormat.ENV: ENVParser,
    }
    
    EXTENSIONS = {
        '.json': ConfigFormat.JSON,
        '.yaml': ConfigFormat.YAML,
        '.yml': ConfigFormat.YAML,
        '.toml': ConfigFormat.TOML,
        '.ini': ConfigFormat.INI,
        '.env': ConfigFormat.ENV,
    }
    
    def __init__(self):
        self.config: Dict[str, Any] = {}
        self.entries: List[ConfigEntry] = []
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def detect_format(self, file_path: str) -> ConfigFormat:
        """Detect configuration format from file extension."""
        path = Path(file_path)
        ext = path.suffix.lower()
        # Handle .env files (no extension, just filename)
        if ext == '' and path.name.lower() == '.env':
            return ConfigFormat.ENV
        return self.EXTENSIONS.get(ext, ConfigFormat.JSON)
    
    def load_file(self, file_path: str, format: ConfigFormat = ConfigFormat.AUTO) -> Dict[str, Any]:
        """Load a configuration file."""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        if format == ConfigFormat.AUTO:
            format = self.detect_format(file_path)
        
        content = path.read_text(encoding='utf-8')
        return self.load_string(content, format)
    
    def load_string(self, content: str, format: ConfigFormat) -> Dict[str, Any]:
        """Parse configuration from string."""
        parser = self.PARSERS.get(format)
        if not parser:
            raise ValueError(f"Unsupported format: {format}")
        
        return parser.parse(content)
    
    def save_file(self, data: Dict[str, Any], file_path: str, format: ConfigFormat = ConfigFormat.AUTO) -> None:
        """Save configuration to file."""
        if format == ConfigFormat.AUTO:
            format = self.detect_format(file_path)
        
        content = self.save_string(data, format)
        Path(file_path).write_text(content, encoding='utf-8')
    
    def save_string(self, data: Dict[str, Any], format: ConfigFormat) -> str:
        """Convert configuration to string."""
        parser = self.PARSERS.get(format)
        if not parser:
            raise ValueError(f"Unsupported format: {format}")
        
        return parser.stringify(data)
    
    def convert(self, input_path: str, output_path: str, 
                input_format: ConfigFormat = ConfigFormat.AUTO,
                output_format: ConfigFormat = ConfigFormat.AUTO) -> bool:
        """Convert configuration file from one format to another."""
        try:
            data = self.load_file(input_path, input_format)
            self.save_file(data, output_path, output_format)
            return True
        except Exception as e:
            self.errors.append(f"Conversion error: {e}")
            return False
    
    def merge(self, *config_paths: str, strategy: str = "deep") -> Dict[str, Any]:
        """Merge multiple configuration files."""
        result = {}
        
        for path in config_paths:
            try:
                data = self.load_file(path)
                result = self._merge_dicts(result, data, strategy)
            except Exception as e:
                self.warnings.append(f"Failed to load {path}: {e}")
        
        return result
    
    def _merge_dicts(self, base: Dict[str, Any], override: Dict[str, Any], 
                     strategy: str = "deep") -> Dict[str, Any]:
        """Merge two dictionaries."""
        result = base.copy()
        
        for key, value in override.items():
            if key in result:
                if strategy == "deep" and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = self._merge_dicts(result[key], value, strategy)
                elif strategy == "append" and isinstance(result[key], list) and isinstance(value, list):
                    result[key] = result[key] + value
                else:
                    result[key] = value
            else:
                result[key] = value
        
        return result
    
    def diff(self, config1: Dict[str, Any], config2: Dict[str, Any]) -> List[ConfigDiff]:
        """Compare two configurations and return differences."""
        diffs = []
        
        all_keys = set(config1.keys()) | set(config2.keys())
        
        for key in all_keys:
            if key not in config1:
                diffs.append(ConfigDiff(key, None, config2[key], "added"))
            elif key not in config2:
                diffs.append(ConfigDiff(key, config1[key], None, "removed"))
            elif config1[key] != config2[key]:
                diffs.append(ConfigDiff(key, config1[key], config2[key], "modified"))
        
        return diffs
    
    def validate(self, config: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
        """Validate configuration against a schema."""
        errors = []
        
        for key, rules in schema.items():
            if rules.get("required", False) and key not in config:
                errors.append(f"Missing required key: {key}")
                continue
            
            if key in config:
                value = config[key]
                expected_type = rules.get("type")
                
                if expected_type:
                    type_map = {
                        "string": str,
                        "integer": int,
                        "float": (int, float),
                        "boolean": bool,
                        "list": list,
                        "dict": dict,
                    }
                    expected = type_map.get(expected_type)
                    if expected and not isinstance(value, expected):
                        errors.append(f"Key '{key}' has wrong type: expected {expected_type}, got {type(value).__name__}")
                
                if "min" in rules and isinstance(value, (int, float)):
                    if value < rules["min"]:
                        errors.append(f"Key '{key}' is below minimum: {value} < {rules['min']}")
                
                if "max" in rules and isinstance(value, (int, float)):
                    if value > rules["max"]:
                        errors.append(f"Key '{key}' exceeds maximum: {value} > {rules['max']}")
                
                if "pattern" in rules and isinstance(value, str):
                    if not re.match(rules["pattern"], value):
                        errors.append(f"Key '{key}' doesn't match pattern: {rules['pattern']}")
        
        return errors
    
    def flatten(self, config: Dict[str, Any], separator: str = ".") -> Dict[str, Any]:
        """Flatten nested configuration."""
        result = {}
        
        def _flatten(obj: Any, prefix: str = ""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_key = f"{prefix}{separator}{key}" if prefix else key
                    _flatten(value, new_key)
            elif isinstance(obj, list):
                for i, value in enumerate(obj):
                    new_key = f"{prefix}{separator}{i}" if prefix else str(i)
                    _flatten(value, new_key)
            else:
                result[prefix] = obj
        
        _flatten(config)
        return result
    
    def unflatten(self, config: Dict[str, Any], separator: str = ".") -> Dict[str, Any]:
        """Unflatten configuration with dot notation keys."""
        result = {}
        
        for key, value in config.items():
            parts = key.split(separator)
            current = result
            
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            current[parts[-1]] = value
        
        return result


# ============================================================================
# CLI Interface
# ============================================================================

class ConfigForgeCLI:
    """Command-line interface for ConfigForge."""
    
    def __init__(self):
        self.forge = ConfigForge()
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser."""
        parser = argparse.ArgumentParser(
            prog="configforge",
            description="🔧 ConfigForge - Lightweight Multi-Format Configuration File Intelligent Conversion & Merging Engine",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Convert JSON to YAML
  configforge convert config.json config.yaml
  
  # Convert TOML to ENV
  configforge convert settings.toml .env
  
  # Merge multiple configs
  configforge merge base.json override.yaml -o merged.json
  
  # Compare two configs
  configforge diff old.json new.json
  
  # Validate config
  configforge validate config.json --schema schema.json
  
  # Flatten nested config
  configforge flatten config.json -o flat.env
"""
        )
        
        parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__}')
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Convert command
        convert_parser = subparsers.add_parser('convert', help='Convert configuration file format')
        convert_parser.add_argument('input', help='Input configuration file')
        convert_parser.add_argument('output', help='Output configuration file')
        convert_parser.add_argument('-i', '--input-format', choices=['json', 'yaml', 'toml', 'ini', 'env'],
                                   help='Input format (auto-detected if not specified)')
        convert_parser.add_argument('-o', '--output-format', choices=['json', 'yaml', 'toml', 'ini', 'env'],
                                   help='Output format (auto-detected if not specified)')
        
        # Merge command
        merge_parser = subparsers.add_parser('merge', help='Merge multiple configuration files')
        merge_parser.add_argument('inputs', nargs='+', help='Input configuration files')
        merge_parser.add_argument('-o', '--output', required=True, help='Output file')
        merge_parser.add_argument('-s', '--strategy', choices=['deep', 'shallow', 'append'],
                                 default='deep', help='Merge strategy (default: deep)')
        
        # Diff command
        diff_parser = subparsers.add_parser('diff', help='Compare two configuration files')
        diff_parser.add_argument('file1', help='First configuration file')
        diff_parser.add_argument('file2', help='Second configuration file')
        diff_parser.add_argument('-f', '--format', choices=['json', 'yaml', 'toml', 'ini', 'env'],
                                help='Output format for diff')
        
        # Validate command
        validate_parser = subparsers.add_parser('validate', help='Validate configuration file')
        validate_parser.add_argument('config', help='Configuration file to validate')
        validate_parser.add_argument('-s', '--schema', required=True, help='Schema file')
        
        # Flatten command
        flatten_parser = subparsers.add_parser('flatten', help='Flatten nested configuration')
        flatten_parser.add_argument('input', help='Input configuration file')
        flatten_parser.add_argument('-o', '--output', help='Output file')
        flatten_parser.add_argument('--separator', default='.', help='Key separator (default: .)')
        
        # Unflatten command
        unflatten_parser = subparsers.add_parser('unflatten', help='Unflatten configuration')
        unflatten_parser.add_argument('input', help='Input configuration file')
        unflatten_parser.add_argument('-o', '--output', help='Output file')
        unflatten_parser.add_argument('--separator', default='.', help='Key separator (default: .)')
        
        # Info command
        info_parser = subparsers.add_parser('info', help='Show configuration file info')
        info_parser.add_argument('file', help='Configuration file')
        
        return parser
    
    def run(self, args: List[str] = None) -> int:
        """Run CLI with arguments."""
        parser = self.create_parser()
        opts = parser.parse_args(args)
        
        if not opts.command:
            parser.print_help()
            return 0
        
        try:
            if opts.command == 'convert':
                return self._cmd_convert(opts)
            elif opts.command == 'merge':
                return self._cmd_merge(opts)
            elif opts.command == 'diff':
                return self._cmd_diff(opts)
            elif opts.command == 'validate':
                return self._cmd_validate(opts)
            elif opts.command == 'flatten':
                return self._cmd_flatten(opts)
            elif opts.command == 'unflatten':
                return self._cmd_unflatten(opts)
            elif opts.command == 'info':
                return self._cmd_info(opts)
        except Exception as e:
            print(f"❌ Error: {e}", file=sys.stderr)
            return 1
        
        return 0
    
    def _cmd_convert(self, opts) -> int:
        """Handle convert command."""
        input_format = ConfigFormat(opts.input_format) if opts.input_format else ConfigFormat.AUTO
        output_format = ConfigFormat(opts.output_format) if opts.output_format else ConfigFormat.AUTO
        
        if self.forge.convert(opts.input, opts.output, input_format, output_format):
            print(f"✅ Converted {opts.input} → {opts.output}")
            return 0
        else:
            for error in self.forge.errors:
                print(f"❌ {error}", file=sys.stderr)
            return 1
    
    def _cmd_merge(self, opts) -> int:
        """Handle merge command."""
        result = self.forge.merge(*opts.inputs, strategy=opts.strategy)
        self.forge.save_file(result, opts.output)
        print(f"✅ Merged {len(opts.inputs)} files → {opts.output}")
        return 0
    
    def _cmd_diff(self, opts) -> int:
        """Handle diff command."""
        config1 = self.forge.load_file(opts.file1)
        config2 = self.forge.load_file(opts.file2)
        
        diffs = self.forge.diff(config1, config2)
        
        if not diffs:
            print("✅ No differences found")
            return 0
        
        print(f"📋 Found {len(diffs)} differences:\n")
        
        for diff in diffs:
            if diff.diff_type == "added":
                print(f"  🟢 + {diff.key}: {diff.new_value}")
            elif diff.diff_type == "removed":
                print(f"  🔴 - {diff.key}: {diff.old_value}")
            else:
                print(f"  🟡 ~ {diff.key}: {diff.old_value} → {diff.new_value}")
        
        return 0
    
    def _cmd_validate(self, opts) -> int:
        """Handle validate command."""
        config = self.forge.load_file(opts.config)
        schema = self.forge.load_file(opts.schema)
        
        errors = self.forge.validate(config, schema)
        
        if not errors:
            print("✅ Configuration is valid")
            return 0
        
        print(f"❌ Found {len(errors)} validation errors:\n")
        for error in errors:
            print(f"  • {error}")
        
        return 1
    
    def _cmd_flatten(self, opts) -> int:
        """Handle flatten command."""
        config = self.forge.load_file(opts.input)
        flat = self.forge.flatten(config, opts.separator)
        
        if opts.output:
            self.forge.save_file(flat, opts.output)
            print(f"✅ Flattened config → {opts.output}")
        else:
            print(self.forge.save_string(flat, ConfigFormat.ENV))
        
        return 0
    
    def _cmd_unflatten(self, opts) -> int:
        """Handle unflatten command."""
        config = self.forge.load_file(opts.input)
        unflat = self.forge.unflatten(config, opts.separator)
        
        if opts.output:
            self.forge.save_file(unflat, opts.output)
            print(f"✅ Unflattened config → {opts.output}")
        else:
            print(self.forge.save_string(unflat, ConfigFormat.JSON))
        
        return 0
    
    def _cmd_info(self, opts) -> int:
        """Handle info command."""
        config = self.forge.load_file(opts.file)
        format_type = self.forge.detect_format(opts.file)
        
        flat = self.forge.flatten(config)
        
        print(f"📄 Configuration File: {opts.file}")
        print(f"📋 Format: {format_type.value.upper()}")
        print(f"📊 Total Keys: {len(flat)}")
        print(f"📁 Nested Levels: {self._count_levels(config)}")
        print(f"\n📋 Keys:")
        for key in sorted(flat.keys())[:20]:
            print(f"  • {key}: {type(flat[key]).__name__}")
        
        if len(flat) > 20:
            print(f"  ... and {len(flat) - 20} more keys")
        
        return 0
    
    def _count_levels(self, obj: Any, level: int = 0) -> int:
        """Count maximum nesting level."""
        if isinstance(obj, dict):
            if not obj:
                return level
            return max(self._count_levels(v, level + 1) for v in obj.values())
        elif isinstance(obj, list):
            if not obj:
                return level
            return max(self._count_levels(item, level + 1) for item in obj)
        return level


def main():
    """Main entry point."""
    cli = ConfigForgeCLI()
    sys.exit(cli.run())


if __name__ == "__main__":
    main()
