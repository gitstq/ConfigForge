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
  <strong>轻量级多格式配置文件智能转换与合并引擎</strong><br>
  <em>Lightweight Multi-Format Configuration File Intelligent Conversion & Merging Engine</em>
</p>

<p align="center">
  零依赖 · 跨平台 · 多格式支持 · 智能合并 · 配置验证
</p>

---

## 🎉 项目介绍

**ConfigForge** 是一个功能强大的配置文件管理工具，专为开发者和运维工程师设计。它能够智能地在多种配置格式之间进行转换、合并和验证，帮助您轻松管理复杂的项目配置。

### 🎯 解决的痛点

- **格式转换困难**：不同工具和框架使用不同的配置格式，手动转换容易出错
- **配置合并复杂**：多环境配置合并时需要手动处理冲突
- **格式验证缺失**：配置文件缺少类型检查和验证机制
- **依赖臃肿**：现有工具依赖过多，安装体积大

### ✨ 自研差异化亮点

- 🚀 **零依赖设计**：所有解析器均为纯Python实现，无需安装任何第三方库
- 🔄 **多格式互转**：支持 JSON、YAML、TOML、INI、ENV 五种主流格式
- 🧠 **智能合并策略**：支持深度合并、浅层合并、追加合并三种策略
- ✅ **配置验证**：基于Schema的配置验证，支持类型检查、范围验证
- 📊 **差异对比**：直观展示配置变更，方便版本管理
- 🎯 **扁平化处理**：支持嵌套配置的扁平化和反扁平化

---

## ✨ 核心特性

### 🔄 多格式转换

```bash
# JSON → YAML
configforge convert config.json config.yaml

# TOML → ENV
configforge convert settings.toml .env

# YAML → JSON
configforge convert docker-compose.yaml docker-compose.json
```

### 🧠 智能合并

```bash
# 深度合并多个配置文件
configforge merge base.json dev.yaml prod.toml -o merged.json

# 使用追加策略合并列表
configforge merge a.json b.yaml -o result.json --strategy append
```

### 📊 差异对比

```bash
# 对比两个配置文件
configforge diff old-config.json new-config.yaml
```

### ✅ 配置验证

```bash
# 基于Schema验证配置
configforge validate config.json --schema schema.json
```

### 🎯 扁平化处理

```bash
# 将嵌套配置扁平化
configforge flatten config.json -o flat.env

# 将扁平配置还原为嵌套结构
configforge unflatten flat.env -o nested.json
```

---

## 🚀 快速开始

### 📋 环境要求

- **Python**: 3.8 或更高版本
- **操作系统**: Windows / macOS / Linux

### 📦 安装

```bash
# 克隆仓库
git clone https://github.com/gitstq/ConfigForge.git
cd ConfigForge

# 直接运行（零依赖，无需安装）
python configforge.py --help
```

### 🎮 基本使用

```bash
# 查看帮助
python configforge.py --help

# 转换配置文件
python configforge.py convert input.json output.yaml

# 合并配置文件
python configforge.py merge base.yaml override.json -o merged.toml

# 查看配置信息
python configforge.py info config.json
```

---

## 📖 详细使用指南

### 🔄 转换命令 (convert)

将配置文件从一种格式转换为另一种格式：

```bash
configforge convert <input> <output> [options]

# 参数说明
#   input         输入配置文件路径
#   output        输出配置文件路径
#   -i, --input-format   指定输入格式（可选，自动检测）
#   -o, --output-format  指定输出格式（可选，自动检测）
```

**示例**：

```bash
# JSON 转 YAML
configforge convert package.json package.yaml

# TOML 转 ENV
configforge convert pyproject.toml .env

# 指定格式转换
configforge convert config.txt config.json -i ini -o json
```

### 🧠 合并命令 (merge)

合并多个配置文件：

```bash
configforge merge <inputs...> -o <output> [options]

# 参数说明
#   inputs        输入配置文件（支持多个）
#   -o, --output  输出文件路径
#   -s, --strategy  合并策略：deep(深度) | shallow(浅层) | append(追加)
```

**合并策略说明**：

| 策略 | 说明 | 适用场景 |
|------|------|----------|
| `deep` | 递归合并嵌套对象 | 多环境配置合并 |
| `shallow` | 只合并顶层键 | 简单配置覆盖 |
| `append` | 追加列表元素 | 数组类型配置 |

### 📊 差异命令 (diff)

对比两个配置文件的差异：

```bash
configforge diff <file1> <file2>

# 输出示例
# 🟢 + 新增的键
# 🔴 - 删除的键
# 🟡 ~ 修改的键
```

### ✅ 验证命令 (validate)

基于Schema验证配置：

```bash
configforge validate <config> --schema <schema>

# Schema 格式示例
{
  "name": {"type": "string", "required": true},
  "port": {"type": "integer", "min": 1, "max": 65535},
  "debug": {"type": "boolean"}
}
```

### 📋 信息命令 (info)

查看配置文件详细信息：

```bash
configforge info <file>

# 输出示例
📄 Configuration File: config.json
📋 Format: JSON
📊 Total Keys: 15
📁 Nested Levels: 3
```

---

## 💡 设计思路与迭代规划

### 🏗️ 设计理念

1. **零依赖优先**：所有解析器使用纯Python实现，避免依赖地狱
2. **格式无关设计**：统一的内部数据结构，支持任意格式互转
3. **渐进式功能**：核心功能开箱即用，高级功能可选使用

### 🔮 后续迭代计划

- [ ] 支持更多格式：HCL、XML、Properties
- [ ] 添加配置模板功能
- [ ] 支持远程配置源（HTTP/Consul/etcd）
- [ ] 添加配置加密功能
- [ ] 提供Python API供程序调用
- [ ] 支持配置热重载

---

## 📦 打包与部署指南

### 🖥️ 作为CLI工具使用

```bash
# 添加别名（添加到 ~/.bashrc 或 ~/.zshrc）
alias configforge='python /path/to/configforge.py'

# 然后可以直接使用
configforge convert config.json config.yaml
```

### 📦 作为Python模块使用

```python
from configforge import ConfigForge, ConfigFormat

# 创建实例
forge = ConfigForge()

# 加载配置
config = forge.load_file("config.json")

# 转换格式
yaml_content = forge.save_string(config, ConfigFormat.YAML)

# 合并配置
merged = forge.merge("base.json", "override.yaml")

# 验证配置
errors = forge.validate(config, schema)
```

---

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 📝 提交PR

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: 添加新功能'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 🐛 报告问题

请使用 [GitHub Issues](https://github.com/gitstq/ConfigForge/issues) 报告问题，包含：

- 问题描述
- 复现步骤
- 期望结果
- 实际结果
- 环境信息

---

## 📄 开源协议

本项目采用 [MIT License](LICENSE) 开源协议。

---

<p align="center">
  Made with ❤️ by ConfigForge Team
</p>
