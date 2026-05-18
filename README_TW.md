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
  <strong>輕量級多格式設定檔智慧轉換與合併引擎</strong><br>
  <em>Lightweight Multi-Format Configuration File Intelligent Conversion & Merging Engine</em>
</p>

<p align="center">
  零依賴 · 跨平台 · 多格式支援 · 智慧合併 · 設定驗證
</p>

---

## 🎉 專案介紹

**ConfigForge** 是一個功能強大的設定檔管理工具，專為開發者和維運工程師設計。它能夠智慧地在多種設定格式之間進行轉換、合併和驗證，幫助您輕鬆管理複雜的專案設定。

### 🎯 解決的痛點

- **格式轉換困難**：不同工具和框架使用不同的設定格式，手動轉換容易出錯
- **設定合併複雜**：多環境設定合併時需要手動處理衝突
- **格式驗證缺失**：設定檔缺少型別檢查和驗證機制
- **依賴臃腫**：現有工具依賴過多，安裝體積大

### ✨ 自研差異化亮點

- 🚀 **零依賴設計**：所有解析器均為純 Python 實現，無需安裝任何第三方函式庫
- 🔄 **多格式互轉**：支援 JSON、YAML、TOML、INI、ENV 五種主流格式
- 🧠 **智慧合併策略**：支援深度合併、淺層合併、追加合併三種策略
- ✅ **設定驗證**：基於 Schema 的設定驗證，支援型別檢查、範圍驗證
- 📊 **差異對比**：直觀展示設定變更，方便版本管理
- 🎯 **扁平化處理**：支援巢狀設定的扁平化和反扁平化

---

## ✨ 核心特性

### 🔄 多格式轉換

```bash
# JSON → YAML
configforge convert config.json config.yaml

# TOML → ENV
configforge convert settings.toml .env

# YAML → JSON
configforge convert docker-compose.yaml docker-compose.json
```

### 🧠 智慧合併

```bash
# 深度合併多個設定檔
configforge merge base.json dev.yaml prod.toml -o merged.json

# 使用追加策略合併列表
configforge merge a.json b.yaml -o result.json --strategy append
```

### 📊 差異對比

```bash
# 對比兩個設定檔
configforge diff old-config.json new-config.yaml
```

### ✅ 設定驗證

```bash
# 基於 Schema 驗證設定
configforge validate config.json --schema schema.json
```

### 🎯 扁平化處理

```bash
# 將巢狀設定扁平化
configforge flatten config.json -o flat.env

# 將扁平設定還原為巢狀結構
configforge unflatten flat.env -o nested.json
```

---

## 🚀 快速開始

### 📋 環境要求

- **Python**: 3.8 或更高版本
- **作業系統**: Windows / macOS / Linux

### 📦 安裝

```bash
# 複製儲存庫
git clone https://github.com/gitstq/ConfigForge.git
cd ConfigForge

# 直接執行（零依賴，無需安裝）
python configforge.py --help
```

### 🎮 基本使用

```bash
# 查看幫助
python configforge.py --help

# 轉換設定檔
python configforge.py convert input.json output.yaml

# 合併設定檔
python configforge.py merge base.yaml override.json -o merged.toml

# 查看設定資訊
python configforge.py info config.json
```

---

## 📖 詳細使用指南

### 🔄 轉換命令 (convert)

將設定檔從一種格式轉換為另一種格式：

```bash
configforge convert <input> <output> [options]

# 參數說明
#   input         輸入設定檔路徑
#   output        輸出設定檔路徑
#   -i, --input-format   指定輸入格式（可選，自動檢測）
#   -o, --output-format  指定輸出格式（可選，自動檢測）
```

**範例**：

```bash
# JSON 轉 YAML
configforge convert package.json package.yaml

# TOML 轉 ENV
configforge convert pyproject.toml .env

# 指定格式轉換
configforge convert config.txt config.json -i ini -o json
```

### 🧠 合併命令 (merge)

合併多個設定檔：

```bash
configforge merge <inputs...> -o <output> [options]

# 參數說明
#   inputs        輸入設定檔（支援多個）
#   -o, --output  輸出檔案路徑
#   -s, --strategy  合併策略：deep(深度) | shallow(淺層) | append(追加)
```

**合併策略說明**：

| 策略 | 說明 | 適用場景 |
|------|------|----------|
| `deep` | 遞迴合併巢狀物件 | 多環境設定合併 |
| `shallow` | 只合併頂層鍵 | 簡單設定覆蓋 |
| `append` | 追加列表元素 | 陣列型別設定 |

### 📊 差異命令 (diff)

對比兩個設定檔的差異：

```bash
configforge diff <file1> <file2>

# 輸出範例
# 🟢 + 新增的鍵
# 🔴 - 刪除的鍵
# 🟡 ~ 修改的鍵
```

### ✅ 驗證命令 (validate)

基於 Schema 驗證設定：

```bash
configforge validate <config> --schema <schema>

# Schema 格式範例
{
  "name": {"type": "string", "required": true},
  "port": {"type": "integer", "min": 1, "max": 65535},
  "debug": {"type": "boolean"}
}
```

### 📋 資訊命令 (info)

查看設定檔詳細資訊：

```bash
configforge info <file>

# 輸出範例
📄 Configuration File: config.json
📋 Format: JSON
📊 Total Keys: 15
📁 Nested Levels: 3
```

---

## 💡 設計思路與迭代規劃

### 🏗️ 設計理念

1. **零依賴優先**：所有解析器使用純 Python 實現，避免依賴地獄
2. **格式無關設計**：統一的內部資料結構，支援任意格式互轉
3. **漸進式功能**：核心功能開箱即用，進階功能可選使用

### 🔮 後續迭代計劃

- [ ] 支援更多格式：HCL、XML、Properties
- [ ] 新增設定範本功能
- [ ] 支援遠端設定來源（HTTP/Consul/etcd）
- [ ] 新增設定加密功能
- [ ] 提供 Python API 供程式呼叫
- [ ] 支援設定熱重載

---

## 📦 打包與部署指南

### 🖥️ 作為 CLI 工具使用

```bash
# 新增別名（新增到 ~/.bashrc 或 ~/.zshrc）
alias configforge='python /path/to/configforge.py'

# 然後可以直接使用
configforge convert config.json config.yaml
```

### 📦 作為 Python 模組使用

```python
from configforge import ConfigForge, ConfigFormat

# 建立實例
forge = ConfigForge()

# 載入設定
config = forge.load_file("config.json")

# 轉換格式
yaml_content = forge.save_string(config, ConfigFormat.YAML)

# 合併設定
merged = forge.merge("base.json", "override.yaml")

# 驗證設定
errors = forge.validate(config, schema)
```

---

## 🤝 貢獻指南

我們歡迎所有形式的貢獻！

### 📝 提交 PR

1. Fork 本儲存庫
2. 建立特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交變更 (`git commit -m 'feat: 新增新功能'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 建立 Pull Request

### 🐛 回報問題

請使用 [GitHub Issues](https://github.com/gitstq/ConfigForge/issues) 回報問題，包含：

- 問題描述
- 重現步驟
- 預期結果
- 實際結果
- 環境資訊

---

## 📄 開源協議

本專案採用 [MIT License](LICENSE) 開源協議。

---

<p align="center">
  Made with ❤️ by ConfigForge Team
</p>
