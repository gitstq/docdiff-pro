#!/usr/bin/env python3
"""
DocDiff Pro - 智能文档差异分析引擎
安装脚本
"""

from setuptools import setup, find_packages
from pathlib import Path

# 读取README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="docdiff-pro",
    version="1.0.0",
    author="DocDiff Team",
    author_email="docdiff@example.com",
    description="智能文档差异分析引擎 - Intelligent Document Diff Analysis Engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gitstq/docdiff-pro",
    py_modules=["docdiff"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: General",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        # 核心功能零依赖
    ],
    extras_require={
        "pdf": ["PyPDF2>=3.0.0"],
        "docx": ["python-docx>=0.8.11"],
        "full": ["PyPDF2>=3.0.0", "python-docx>=0.8.11"],
        "dev": ["pytest>=7.0.0", "black>=22.0.0", "flake8>=5.0.0", "mypy>=1.0.0"],
    },
    entry_points={
        "console_scripts": [
            "docdiff=docdiff:main",
        ],
    },
    keywords="document diff comparison pdf word markdown text analysis",
    project_urls={
        "Bug Reports": "https://github.com/gitstq/docdiff-pro/issues",
        "Source": "https://github.com/gitstq/docdiff-pro",
        "Documentation": "https://github.com/gitstq/docdiff-pro#readme",
    },
)
