#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test suite for ConfigForge."""

import os
import sys
import json
import tempfile
import unittest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from configforge import (
    ConfigForge, ConfigFormat, JSONParser, YAMLParser, 
    TOMLParser, INIParser, ENVParser
)


class TestJSONParser(unittest.TestCase):
    """Test JSON parser."""
    
    def test_parse_simple(self):
        """Test parsing simple JSON."""
        content = '{"name": "test", "value": 123}'
        result = JSONParser.parse(content)
        self.assertEqual(result["name"], "test")
        self.assertEqual(result["value"], 123)
    
    def test_parse_nested(self):
        """Test parsing nested JSON."""
        content = '{"database": {"host": "localhost", "port": 5432}}'
        result = JSONParser.parse(content)
        self.assertEqual(result["database"]["host"], "localhost")
        self.assertEqual(result["database"]["port"], 5432)
    
    def test_stringify(self):
        """Test JSON stringify."""
        data = {"name": "test", "value": 123}
        result = JSONParser.stringify(data)
        parsed = json.loads(result)
        self.assertEqual(parsed, data)


class TestYAMLParser(unittest.TestCase):
    """Test YAML parser."""
    
    def test_parse_simple(self):
        """Test parsing simple YAML."""
        content = "name: test\nvalue: 123"
        result = YAMLParser.parse(content)
        self.assertEqual(result["name"], "test")
        self.assertEqual(result["value"], 123)
    
    def test_parse_nested(self):
        """Test parsing nested YAML."""
        content = "database:\n  host: localhost\n  port: 5432"
        result = YAMLParser.parse(content)
        self.assertEqual(result["database"]["host"], "localhost")
    
    def test_stringify(self):
        """Test YAML stringify."""
        data = {"name": "test", "value": 123}
        result = YAMLParser.stringify(data)
        self.assertIn("name:", result)
        self.assertIn("test", result)


class TestTOMLParser(unittest.TestCase):
    """Test TOML parser."""
    
    def test_parse_simple(self):
        """Test parsing simple TOML."""
        content = 'name = "test"\nvalue = 123'
        result = TOMLParser.parse(content)
        self.assertEqual(result["name"], "test")
        self.assertEqual(result["value"], 123)
    
    def test_parse_section(self):
        """Test parsing TOML with sections."""
        content = '[database]\nhost = "localhost"\nport = 5432'
        result = TOMLParser.parse(content)
        self.assertEqual(result["database"]["host"], "localhost")
    
    def test_stringify(self):
        """Test TOML stringify."""
        data = {"name": "test", "value": 123}
        result = TOMLParser.stringify(data)
        self.assertIn('name = "test"', result)


class TestINIParser(unittest.TestCase):
    """Test INI parser."""
    
    def test_parse_simple(self):
        """Test parsing simple INI."""
        content = "name = test\nvalue = 123"
        result = INIParser.parse(content)
        self.assertEqual(result["name"], "test")
        self.assertEqual(result["value"], 123)
    
    def test_parse_section(self):
        """Test parsing INI with sections."""
        content = "[database]\nhost = localhost\nport = 5432"
        result = INIParser.parse(content)
        self.assertEqual(result["database"]["host"], "localhost")
    
    def test_stringify(self):
        """Test INI stringify."""
        data = {"name": "test", "value": 123}
        result = INIParser.stringify(data)
        self.assertIn("name = test", result)


class TestENVParser(unittest.TestCase):
    """Test ENV parser."""
    
    def test_parse_simple(self):
        """Test parsing simple ENV."""
        content = "NAME=test\nVALUE=123"
        result = ENVParser.parse(content)
        self.assertEqual(result["NAME"], "test")
        self.assertEqual(result["VALUE"], 123)
    
    def test_stringify(self):
        """Test ENV stringify."""
        data = {"NAME": "test", "VALUE": 123}
        result = ENVParser.stringify(data)
        self.assertIn("NAME=test", result)


class TestConfigForge(unittest.TestCase):
    """Test ConfigForge main engine."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.forge = ConfigForge()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_detect_format(self):
        """Test format detection."""
        self.assertEqual(self.forge.detect_format("config.json"), ConfigFormat.JSON)
        self.assertEqual(self.forge.detect_format("config.yaml"), ConfigFormat.YAML)
        self.assertEqual(self.forge.detect_format("config.toml"), ConfigFormat.TOML)
        self.assertEqual(self.forge.detect_format("config.ini"), ConfigFormat.INI)
        self.assertEqual(self.forge.detect_format(".env"), ConfigFormat.ENV)
    
    def test_convert_json_to_yaml(self):
        """Test JSON to YAML conversion."""
        json_file = os.path.join(self.temp_dir, "test.json")
        yaml_file = os.path.join(self.temp_dir, "test.yaml")
        
        # Create JSON file
        with open(json_file, 'w') as f:
            json.dump({"name": "test", "value": 123}, f)
        
        # Convert
        result = self.forge.convert(json_file, yaml_file)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(yaml_file))
    
    def test_merge_configs(self):
        """Test config merging."""
        file1 = os.path.join(self.temp_dir, "base.json")
        file2 = os.path.join(self.temp_dir, "override.json")
        
        with open(file1, 'w') as f:
            json.dump({"a": 1, "b": 2}, f)
        with open(file2, 'w') as f:
            json.dump({"b": 3, "c": 4}, f)
        
        result = self.forge.merge(file1, file2)
        self.assertEqual(result["a"], 1)
        self.assertEqual(result["b"], 3)
        self.assertEqual(result["c"], 4)
    
    def test_diff_configs(self):
        """Test config diff."""
        config1 = {"a": 1, "b": 2, "c": 3}
        config2 = {"a": 1, "b": 3, "d": 4}
        
        diffs = self.forge.diff(config1, config2)
        
        diff_keys = {d.key for d in diffs}
        self.assertIn("b", diff_keys)  # modified
        self.assertIn("c", diff_keys)  # removed
        self.assertIn("d", diff_keys)  # added
    
    def test_flatten(self):
        """Test config flattening."""
        config = {"database": {"host": "localhost", "port": 5432}}
        flat = self.forge.flatten(config)
        
        self.assertEqual(flat["database.host"], "localhost")
        self.assertEqual(flat["database.port"], 5432)
    
    def test_unflatten(self):
        """Test config unflattening."""
        flat = {"database.host": "localhost", "database.port": 5432}
        unflat = self.forge.unflatten(flat)
        
        self.assertEqual(unflat["database"]["host"], "localhost")
        self.assertEqual(unflat["database"]["port"], 5432)
    
    def test_validate(self):
        """Test config validation."""
        config = {"name": "test", "age": 25}
        schema = {
            "name": {"type": "string", "required": True},
            "age": {"type": "integer", "min": 0, "max": 150}
        }
        
        errors = self.forge.validate(config, schema)
        self.assertEqual(len(errors), 0)
        
        # Test invalid
        invalid_config = {"name": 123, "age": 200}
        errors = self.forge.validate(invalid_config, schema)
        self.assertGreater(len(errors), 0)


if __name__ == "__main__":
    unittest.main()
