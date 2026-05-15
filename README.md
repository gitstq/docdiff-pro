<div align="center">

# 📄 DocDiff Pro

**智能文档差异分析引擎 | Intelligent Document Diff Analysis Engine**

[![Python](https://img.shields.io/badge/Python-3.7%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero-brightgreen.svg)]()
[![Platform](https://img.shields.io/badge/Platform-Cross--Platform-lightgrey.svg)]()

[简体中文](#简体中文) | [繁體中文](#繁體中文) | [English](#english)

</div>

---

## 简体中文

### 🎉 项目介绍

DocDiff Pro 是一款**轻量级、零依赖**的智能文档差异分析工具，专为开发者、文档管理员和内容创作者设计。它能够快速比较多种格式的文档（PDF、Word、Markdown、文本），并以直观的方式展示差异。

**灵感来源**：在文档版本管理和内容审核过程中，经常需要对比不同版本的文档。现有的工具要么过于复杂，要么依赖众多。DocDiff Pro 旨在提供一个**简单、快速、准确**的解决方案。

**自研差异化亮点**：
- ✅ **零依赖设计**：核心功能仅使用 Python 标准库，无需安装额外依赖
- ✅ **多格式支持**：原生支持 PDF、Word、Markdown、HTML、纯文本
- ✅ **语义级差异检测**：不仅比较文本，还能识别语义相似的段落
- ✅ **多格式报告**：生成美观的 HTML、JSON、Markdown 报告
- ✅ **跨平台兼容**：Windows、macOS、Linux 全平台支持

### ✨ 核心特性

| 特性 | 描述 | 状态 |
|------|------|------|
| 📄 **多格式支持** | PDF、DOCX、MD、TXT、HTML | ✅ 已支持 |
| 🧠 **智能对比** | 基于相似度算法的语义级检测 | ✅ 已支持 |
| 📊 **可视化报告** | HTML 报告带颜色标记和统计 | ✅ 已支持 |
| 📦 **零依赖** | 纯 Python 标准库实现 | ✅ 已支持 |
| 🔍 **统一差异** | 类 Git diff 的文本输出 | ✅ 已支持 |
| 📱 **响应式设计** | 支持移动端查看报告 | ✅ 已支持 |
| 🌐 **多语言** | 中文、英文界面支持 | ✅ 已支持 |
| ⚡ **高性能** | 大文件快速处理 | ✅ 已支持 |

### 🚀 快速开始

#### 环境要求

- **Python**: 3.7 或更高版本
- **操作系统**: Windows / macOS / Linux

#### 安装步骤

**方式一：直接下载使用（推荐）**

```bash
# 克隆仓库
git clone https://github.com/gitstq/docdiff-pro.git
cd docdiff-pro

# 直接使用
python docdiff.py doc1.md doc2.md
```

**方式二：通过 pip 安装**

```bash
# 安装核心版本（零依赖）
pip install docdiff-pro

# 安装完整版本（含 PDF/DOCX 增强支持）
pip install docdiff-pro[full]
```

#### 基本使用

```bash
# 比较两个文档并生成 HTML 报告
python docdiff.py document_v1.md document_v2.md -o report.html

# 生成 JSON 格式报告
python docdiff.py doc1.pdf doc2.pdf -f json -o diff.json

# 输出统一差异格式（类似 git diff）
python docdiff.py old.txt new.txt --unified

# 显示详细输出
python docdiff.py file1.docx file2.docx -v
```

### 📖 详细使用指南

#### 命令行参数

```
usage: docdiff [-h] [-o OUTPUT] [-f {html,json,markdown,md}] [-u] [-v] [--version] source target

位置参数:
  source                源文件路径
  target                目标文件路径

可选参数:
  -h, --help            显示帮助信息
  -o, --output          输出报告路径
  -f, --format          报告格式 (默认: html)
  -u, --unified         输出统一差异格式
  -v, --verbose         显示详细输出
  --version             显示版本信息
```

#### 使用示例

**示例 1：比较 Markdown 文档**

```bash
python docdiff.py proposal_v1.md proposal_v2.md -o comparison_report.html
```

生成的 HTML 报告包含：
- 📊 变更统计（新增/删除/修改数量）
- 📝 带颜色标记的差异对比
- 📈 相似度分析
- 📱 响应式布局，支持移动端

**示例 2：批量处理 JSON 输出**

```bash
python docdiff.py doc1.pdf doc2.pdf -f json -o diff_data.json
```

JSON 输出格式便于程序化处理和集成到 CI/CD 流程。

**示例 3：命令行快速对比**

```bash
python docdiff.py old.txt new.txt --unified
```

输出示例：
```diff
--- old.txt
+++ new.txt
@@ -1,3 +1,4 @@
 第一行内容
-旧的内容
+新的内容
+新增的一行
 最后一行
```

### 💡 设计思路与迭代规划

#### 技术选型原因

1. **纯 Python 标准库**：确保零依赖，降低使用门槛，避免依赖冲突
2. **difflib.SequenceMatcher**：Python 内置的序列比较算法，性能优异
3. **Dataclass**：类型安全，代码清晰，便于维护
4. **模块化设计**：解析器、引擎、报告生成器分离，易于扩展

#### 后续功能迭代计划

**v1.1.0（计划中）**
- [ ] 文件夹批量对比
- [ ] 忽略空白字符选项
- [ ] 自定义相似度阈值

**v1.2.0（规划中）**
- [ ] 文档合并功能
- [ ] 冲突解决辅助
- [ ] 版本历史追踪

**v2.0.0（远期规划）**
- [ ] Web 界面
- [ ] 实时协作对比
- [ ] AI 辅助变更摘要

### 📦 打包与部署指南

#### 作为 Python 包使用

```python
from docdiff import DocDiffPro

# 创建实例
docdiff = DocDiffPro()

# 比较文档
result = docdiff.compare("doc1.md", "doc2.md")

# 查看结果
print(result.summary)
print(f"新增: {result.statistics['added']}")
print(f"删除: {result.statistics['removed']}")

# 导出报告
docdiff.export_report(result, "report.html", "html")
```

#### 打包为可执行文件

```bash
# 安装 PyInstaller
pip install pyinstaller

# 打包
pyinstaller --onefile --name docdiff docdiff.py

# 可执行文件位于 dist/docdiff
```

### 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

**提交规范**：
- 🐛 **Bug 修复**: `fix: 修复XXX问题`
- ✨ **新功能**: `feat: 添加XXX功能`
- 📚 **文档更新**: `docs: 更新XXX文档`
- 🔧 **代码重构**: `refactor: 重构XXX模块`

**开发流程**：
1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: 添加某个特性'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 📄 开源协议

本项目采用 [MIT](LICENSE) 协议开源。

---

## 繁體中文

### 🎉 專案介紹

DocDiff Pro 是一款**輕量級、零依賴**的智慧文件差異分析工具，專為開發者、文件管理員和內容創作者設計。它能夠快速比較多種格式的文件（PDF、Word、Markdown、文字），並以直觀的方式展示差異。

**核心優勢**：
- ✅ **零依賴設計**：核心功能僅使用 Python 標準庫
- ✅ **多格式支援**：原生支援 PDF、DOCX、MD、TXT、HTML
- ✅ **語義級差異檢測**：不僅比較文字，還能識別語義相似的段落
- ✅ **多格式報告**：生成美觀的 HTML、JSON、Markdown 報告

### 🚀 快速開始

```bash
# 克隆倉庫
git clone https://github.com/gitstq/docdiff-pro.git
cd docdiff-pro

# 比較兩個文件
python docdiff.py document_v1.md document_v2.md -o report.html
```

### ✨ 核心特性

- 📄 支援 PDF、Word、Markdown、HTML、純文字
- 🧠 基於相似度演算法的語義級檢測
- 📊 視覺化 HTML 報告
- 📦 零依賴，純 Python 標準庫
- 🔍 類 Git diff 的文字輸出

### 📄 開源協議

[MIT](LICENSE) 協議

---

## English

### 🎉 Introduction

DocDiff Pro is a **lightweight, zero-dependency** intelligent document diff analysis tool designed for developers, document managers, and content creators. It quickly compares documents in multiple formats (PDF, Word, Markdown, Text) and displays differences in an intuitive way.

**Key Features**:
- ✅ **Zero Dependencies**: Core functionality uses only Python standard library
- ✅ **Multi-Format Support**: Native support for PDF, DOCX, MD, TXT, HTML
- ✅ **Semantic Diff Detection**: Not just text comparison, but semantic similarity
- ✅ **Multi-Format Reports**: Beautiful HTML, JSON, Markdown reports
- ✅ **Cross-Platform**: Windows, macOS, Linux support

### 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/gitstq/docdiff-pro.git
cd docdiff-pro

# Compare two documents
python docdiff.py document_v1.md document_v2.md -o report.html
```

### ✨ Features

| Feature | Description | Status |
|---------|-------------|--------|
| 📄 **Multi-Format** | PDF, DOCX, MD, TXT, HTML | ✅ Supported |
| 🧠 **Smart Diff** | Semantic detection with similarity algorithm | ✅ Supported |
| 📊 **Visual Reports** | HTML reports with color marking | ✅ Supported |
| 📦 **Zero Dependencies** | Pure Python standard library | ✅ Supported |
| 🔍 **Unified Diff** | Git-like diff output | ✅ Supported |

### 📄 License

[MIT](LICENSE) License

---

<div align="center">

**Made with ❤️ by DocDiff Pro Team**

⭐ Star us on GitHub — it motivates us a lot!

</div>
