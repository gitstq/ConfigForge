<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/Zero%20Dependencies-✓-brightgreen?style=for-the-badge" alt="Zero Dependencies">
</p>

<p align="center">
  <a href="README.md">简体中文</a> | <a href="README_EN.md">English</a> | <a href="README_TW.md">繁體中文</a>
</p>

<h1 align="center">🔧 ConfigForge</h1>

<p align="center">
  <strong>Lightweight Multi-Format Configuration File Intelligent Conversion & Merging Engine</strong>
</p>

<p align="center">
  Zero Dependencies · Cross-Platform · Multi-Format Support · Smart Merging · Config Validation
</p>

---

## 🎉 Introduction

**ConfigForge** is a powerful configuration file management tool designed for developers and DevOps engineers. It intelligently converts, merges, and validates configuration files across multiple formats, helping you manage complex project configurations with ease.

### 🎯 Problems Solved

- **Format Conversion Challenges**: Different tools and frameworks use different configuration formats, making manual conversion error-prone
- **Complex Configuration Merging**: Multi-environment configuration merging requires manual conflict resolution
- **Lack of Format Validation**: Configuration files lack type checking and validation mechanisms
- **Bloated Dependencies**: Existing tools have too many dependencies and large installation sizes

### ✨ Unique Features

- 🚀 **Zero Dependencies**: All parsers are implemented in pure Python, no third-party libraries required
- 🔄 **Multi-Format Conversion**: Supports JSON, YAML, TOML, INI, ENV - five mainstream formats
- 🧠 **Smart Merge Strategies**: Supports deep merge, shallow merge, and append merge strategies
- ✅ **Configuration Validation**: Schema-based validation with type checking and range validation
- 📊 **Diff Comparison**: Intuitively display configuration changes for easy version management
- 🎯 **Flattening Support**: Supports flattening and unflattening of nested configurations

---

## ✨ Core Features

### 🔄 Multi-Format Conversion

```bash
# JSON → YAML
configforge convert config.json config.yaml

# TOML → ENV
configforge convert settings.toml .env

# YAML → JSON
configforge convert docker-compose.yaml docker-compose.json
```

### 🧠 Smart Merging

```bash
# Deep merge multiple configuration files
configforge merge base.json dev.yaml prod.toml -o merged.json

# Merge lists using append strategy
configforge merge a.json b.yaml -o result.json --strategy append
```

### 📊 Diff Comparison

```bash
# Compare two configuration files
configforge diff old-config.json new-config.yaml
```

### ✅ Configuration Validation

```bash
# Validate configuration based on Schema
configforge validate config.json --schema schema.json
```

### 🎯 Flattening

```bash
# Flatten nested configuration
configforge flatten config.json -o flat.env

# Restore flattened config to nested structure
configforge unflatten flat.env -o nested.json
```

---

## 🚀 Quick Start

### 📋 Requirements

- **Python**: 3.8 or higher
- **OS**: Windows / macOS / Linux

### 📦 Installation

```bash
# Clone the repository
git clone https://github.com/gitstq/ConfigForge.git
cd ConfigForge

# Run directly (zero dependencies, no installation needed)
python configforge.py --help
```

### 🎮 Basic Usage

```bash
# Show help
python configforge.py --help

# Convert configuration file
python configforge.py convert input.json output.yaml

# Merge configuration files
python configforge.py merge base.yaml override.json -o merged.toml

# View configuration info
python configforge.py info config.json
```

---

## 📖 Detailed Usage Guide

### 🔄 Convert Command

Convert configuration files from one format to another:

```bash
configforge convert <input> <output> [options]

# Arguments
#   input         Input configuration file path
#   output        Output configuration file path
#   -i, --input-format   Specify input format (optional, auto-detected)
#   -o, --output-format  Specify output format (optional, auto-detected)
```

**Examples**:

```bash
# JSON to YAML
configforge convert package.json package.yaml

# TOML to ENV
configforge convert pyproject.toml .env

# Specify format conversion
configforge convert config.txt config.json -i ini -o json
```

### 🧠 Merge Command

Merge multiple configuration files:

```bash
configforge merge <inputs...> -o <output> [options]

# Arguments
#   inputs        Input configuration files (supports multiple)
#   -o, --output  Output file path
#   -s, --strategy  Merge strategy: deep | shallow | append
```

**Merge Strategy Description**:

| Strategy | Description | Use Case |
|----------|-------------|----------|
| `deep` | Recursively merge nested objects | Multi-environment config merging |
| `shallow` | Only merge top-level keys | Simple config override |
| `append` | Append list elements | Array-type configurations |

### 📊 Diff Command

Compare differences between two configuration files:

```bash
configforge diff <file1> <file2>

# Output example
# 🟢 + Added keys
# 🔴 - Removed keys
# 🟡 ~ Modified keys
```

### ✅ Validate Command

Validate configuration based on Schema:

```bash
configforge validate <config> --schema <schema>

# Schema format example
{
  "name": {"type": "string", "required": true},
  "port": {"type": "integer", "min": 1, "max": 65535},
  "debug": {"type": "boolean"}
}
```

### 📋 Info Command

View detailed configuration file information:

```bash
configforge info <file>

# Output example
📄 Configuration File: config.json
📋 Format: JSON
📊 Total Keys: 15
📁 Nested Levels: 3
```

---

## 💡 Design Philosophy & Roadmap

### 🏗️ Design Principles

1. **Zero Dependencies First**: All parsers implemented in pure Python to avoid dependency hell
2. **Format-Agnostic Design**: Unified internal data structure supporting arbitrary format conversion
3. **Progressive Features**: Core features work out-of-the-box, advanced features optional

### 🔮 Future Roadmap

- [ ] Support more formats: HCL, XML, Properties
- [ ] Add configuration template functionality
- [ ] Support remote configuration sources (HTTP/Consul/etcd)
- [ ] Add configuration encryption
- [ ] Provide Python API for programmatic use
- [ ] Support configuration hot reload

---

## 📦 Packaging & Deployment

### 🖥️ Using as CLI Tool

```bash
# Add alias (add to ~/.bashrc or ~/.zshrc)
alias configforge='python /path/to/configforge.py'

# Then use directly
configforge convert config.json config.yaml
```

### 📦 Using as Python Module

```python
from configforge import ConfigForge, ConfigFormat

# Create instance
forge = ConfigForge()

# Load configuration
config = forge.load_file("config.json")

# Convert format
yaml_content = forge.save_string(config, ConfigFormat.YAML)

# Merge configurations
merged = forge.merge("base.json", "override.yaml")

# Validate configuration
errors = forge.validate(config, schema)
```

---

## 🤝 Contributing

We welcome all forms of contributions!

### 📝 Submitting PRs

1. Fork this repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add new feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Create a Pull Request

### 🐛 Reporting Issues

Please use [GitHub Issues](https://github.com/gitstq/ConfigForge/issues) to report problems, including:

- Problem description
- Steps to reproduce
- Expected result
- Actual result
- Environment information

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<p align="center">
  Made with ❤️ by ConfigForge Team
</p>
