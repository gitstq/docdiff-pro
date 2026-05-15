#!/usr/bin/env python3
"""
DocDiff Pro - 智能文档差异分析引擎
Intelligent Document Diff Analysis Engine

A lightweight, zero-dependency document comparison tool supporting
PDF, Word, and Markdown with semantic diff detection.
"""

import argparse
import sys
import os
import re
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import difflib
import tempfile


class ChangeType(Enum):
    """变更类型枚举"""
    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    UNCHANGED = "unchanged"
    MOVED = "moved"


@dataclass
class TextBlock:
    """文本块数据结构"""
    content: str
    line_number: int
    block_id: int
    checksum: str = ""

    def __post_init__(self):
        if not self.checksum:
            self.checksum = hashlib.md5(self.content.encode()).hexdigest()


@dataclass
class DiffChunk:
    """差异块数据结构"""
    change_type: ChangeType
    old_content: str
    new_content: str
    old_line_start: int
    old_line_end: int
    new_line_start: int
    new_line_end: int
    similarity: float = 0.0


@dataclass
class DiffResult:
    """差异分析结果"""
    source_file: str
    target_file: str
    source_format: str
    target_format: str
    chunks: List[DiffChunk]
    statistics: Dict[str, int]
    summary: str = ""


class DocumentParser:
    """文档解析器基类"""

    @staticmethod
    def detect_format(file_path: str) -> str:
        """检测文件格式"""
        ext = Path(file_path).suffix.lower()
        format_map = {
            '.pdf': 'pdf',
            '.docx': 'docx',
            '.doc': 'doc',
            '.md': 'markdown',
            '.markdown': 'markdown',
            '.txt': 'text',
            '.html': 'html',
            '.htm': 'html'
        }
        return format_map.get(ext, 'unknown')

    @staticmethod
    def read_text_file(file_path: str) -> List[TextBlock]:
        """读取纯文本文件"""
        blocks = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='gbk', errors='ignore') as f:
                lines = f.readlines()

        for i, line in enumerate(lines, 1):
            blocks.append(TextBlock(
                content=line.rstrip('\n\r'),
                line_number=i,
                block_id=i
            ))
        return blocks

    @staticmethod
    def read_pdf_file(file_path: str) -> List[TextBlock]:
        """读取PDF文件 - 使用纯Python实现"""
        blocks = []
        try:
            # 尝试使用PyPDF2（如果已安装）
            import PyPDF2
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                line_num = 1
                for page_num, page in enumerate(reader.pages, 1):
                    text = page.extract_text()
                    if text:
                        lines = text.split('\n')
                        for line in lines:
                            if line.strip():
                                blocks.append(TextBlock(
                                    content=line.strip(),
                                    line_number=line_num,
                                    block_id=line_num
                                ))
                                line_num += 1
        except ImportError:
            # 回退到基本文本提取
            blocks = DocumentParser._extract_pdf_text_basic(file_path)
        return blocks

    @staticmethod
    def _extract_pdf_text_basic(file_path: str) -> List[TextBlock]:
        """基础PDF文本提取（无需外部依赖）"""
        blocks = []
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                # 简单的PDF文本提取逻辑
                text = content.decode('latin-1', errors='ignore')
                # 提取括号内的文本（PDF文本通常存储在括号中）
                pattern = r'\(([^)]+)\)'
                matches = re.findall(pattern, text)
                line_num = 1
                for match in matches:
                    # 过滤掉非文本内容
                    if len(match) > 3 and not match.startswith('/'):
                        # 处理PDF转义序列
                        clean_text = match.replace('\\n', '\n').replace('\\r', '').replace('\\t', '\t')
                        for line in clean_text.split('\n'):
                            if line.strip():
                                blocks.append(TextBlock(
                                    content=line.strip(),
                                    line_number=line_num,
                                    block_id=line_num
                                ))
                                line_num += 1
        except Exception as e:
            blocks.append(TextBlock(
                content=f"[PDF解析错误: {str(e)}]",
                line_number=1,
                block_id=1
            ))
        return blocks

    @staticmethod
    def read_docx_file(file_path: str) -> List[TextBlock]:
        """读取Word文档 - 使用纯Python实现"""
        blocks = []
        try:
            # 尝试使用python-docx（如果已安装）
            import docx
            doc = docx.Document(file_path)
            line_num = 1
            for para in doc.paragraphs:
                if para.text.strip():
                    blocks.append(TextBlock(
                        content=para.text.strip(),
                        line_number=line_num,
                        block_id=line_num
                    ))
                    line_num += 1
        except ImportError:
            # 回退到zip/xml解析
            blocks = DocumentParser._extract_docx_text_basic(file_path)
        return blocks

    @staticmethod
    def _extract_docx_text_basic(file_path: str) -> List[TextBlock]:
        """基础DOCX文本提取（使用标准库）"""
        blocks = []
        try:
            import zipfile
            import xml.etree.ElementTree as ET

            with zipfile.ZipFile(file_path, 'r') as z:
                if 'word/document.xml' in z.namelist():
                    xml_content = z.read('word/document.xml')
                    root = ET.fromstring(xml_content)

                    # Word XML命名空间
                    namespaces = {
                        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
                    }

                    line_num = 1
                    # 提取所有文本节点
                    for elem in root.iter():
                        if elem.tag.endswith('}t') and elem.text:
                            text = elem.text.strip()
                            if text:
                                blocks.append(TextBlock(
                                    content=text,
                                    line_number=line_num,
                                    block_id=line_num
                                ))
                                line_num += 1
        except Exception as e:
            blocks.append(TextBlock(
                content=f"[DOCX解析错误: {str(e)}]",
                line_number=1,
                block_id=1
            ))
        return blocks

    @classmethod
    def parse_file(cls, file_path: str) -> Tuple[List[TextBlock], str]:
        """解析文件并返回文本块列表和格式"""
        file_format = cls.detect_format(file_path)

        if file_format == 'pdf':
            blocks = cls.read_pdf_file(file_path)
        elif file_format in ['docx', 'doc']:
            blocks = cls.read_docx_file(file_path)
        elif file_format in ['markdown', 'text', 'html']:
            blocks = cls.read_text_file(file_path)
        else:
            # 尝试作为文本文件读取
            blocks = cls.read_text_file(file_path)

        return blocks, file_format


class DiffEngine:
    """差异分析引擎"""

    @staticmethod
    def calculate_similarity(text1: str, text2: str) -> float:
        """计算两段文本的相似度"""
        if not text1 and not text2:
            return 1.0
        if not text1 or not text2:
            return 0.0

        # 使用SequenceMatcher计算相似度
        matcher = difflib.SequenceMatcher(None, text1, text2)
        return matcher.ratio()

    @staticmethod
    def find_best_match(block: TextBlock, candidates: List[TextBlock],
                       threshold: float = 0.6) -> Optional[Tuple[TextBlock, float]]:
        """在候选列表中找到最佳匹配"""
        best_match = None
        best_score = threshold

        for candidate in candidates:
            similarity = DiffEngine.calculate_similarity(block.content, candidate.content)
            if similarity > best_score:
                best_score = similarity
                best_match = candidate

        if best_match:
            return best_match, best_score
        return None

    @classmethod
    def analyze_diff(cls, source_blocks: List[TextBlock],
                    target_blocks: List[TextBlock]) -> List[DiffChunk]:
        """分析两个文档的差异"""
        chunks = []

        # 创建校验和映射
        source_checksums = {b.checksum: b for b in source_blocks}
        target_checksums = {b.checksum: b for b in target_blocks}

        # 标记已处理的块
        source_processed = set()
        target_processed = set()

        # 首先匹配完全相同的块
        for src_block in source_blocks:
            if src_block.checksum in target_checksums:
                tgt_block = target_checksums[src_block.checksum]
                chunks.append(DiffChunk(
                    change_type=ChangeType.UNCHANGED,
                    old_content=src_block.content,
                    new_content=tgt_block.content,
                    old_line_start=src_block.line_number,
                    old_line_end=src_block.line_number,
                    new_line_start=tgt_block.line_number,
                    new_line_end=tgt_block.line_number,
                    similarity=1.0
                ))
                source_processed.add(src_block.block_id)
                target_processed.add(tgt_block.block_id)

        # 处理剩余的源块（删除或修改）
        for src_block in source_blocks:
            if src_block.block_id in source_processed:
                continue

            # 在目标中查找相似块
            remaining_targets = [b for b in target_blocks
                               if b.block_id not in target_processed]

            match_result = cls.find_best_match(src_block, remaining_targets)

            if match_result:
                tgt_block, similarity = match_result
                chunks.append(DiffChunk(
                    change_type=ChangeType.MODIFIED,
                    old_content=src_block.content,
                    new_content=tgt_block.content,
                    old_line_start=src_block.line_number,
                    old_line_end=src_block.line_number,
                    new_line_start=tgt_block.line_number,
                    new_line_end=tgt_block.line_number,
                    similarity=similarity
                ))
                target_processed.add(tgt_block.block_id)
            else:
                chunks.append(DiffChunk(
                    change_type=ChangeType.REMOVED,
                    old_content=src_block.content,
                    new_content="",
                    old_line_start=src_block.line_number,
                    old_line_end=src_block.line_number,
                    new_line_start=0,
                    new_line_end=0,
                    similarity=0.0
                ))

            source_processed.add(src_block.block_id)

        # 处理剩余的目标块（新增）
        for tgt_block in target_blocks:
            if tgt_block.block_id in target_processed:
                continue

            chunks.append(DiffChunk(
                change_type=ChangeType.ADDED,
                old_content="",
                new_content=tgt_block.content,
                old_line_start=0,
                old_line_end=0,
                new_line_start=tgt_block.line_number,
                new_line_end=tgt_block.line_number,
                similarity=0.0
            ))

        # 按行号排序
        chunks.sort(key=lambda x: (x.old_line_start or x.new_line_start))

        return chunks

    @classmethod
    def generate_unified_diff(cls, source_blocks: List[TextBlock],
                             target_blocks: List[TextBlock],
                             source_name: str = "source",
                             target_name: str = "target") -> str:
        """生成统一差异格式输出"""
        source_lines = [b.content for b in source_blocks]
        target_lines = [b.content for b in target_blocks]

        diff = difflib.unified_diff(
            source_lines,
            target_lines,
            fromfile=source_name,
            tofile=target_name,
            lineterm=''
        )

        return '\n'.join(diff)


class ReportGenerator:
    """报告生成器"""

    @staticmethod
    def generate_statistics(chunks: List[DiffChunk]) -> Dict[str, int]:
        """生成统计信息"""
        stats = {
            'total_chunks': len(chunks),
            'added': 0,
            'removed': 0,
            'modified': 0,
            'unchanged': 0,
            'moved': 0
        }

        for chunk in chunks:
            if chunk.change_type == ChangeType.ADDED:
                stats['added'] += 1
            elif chunk.change_type == ChangeType.REMOVED:
                stats['removed'] += 1
            elif chunk.change_type == ChangeType.MODIFIED:
                stats['modified'] += 1
            elif chunk.change_type == ChangeType.UNCHANGED:
                stats['unchanged'] += 1
            elif chunk.change_type == ChangeType.MOVED:
                stats['moved'] += 1

        return stats

    @staticmethod
    def generate_summary(chunks: List[DiffChunk], stats: Dict[str, int]) -> str:
        """生成变更摘要"""
        total_changes = stats['added'] + stats['removed'] + stats['modified']

        if total_changes == 0:
            return "✅ 两个文档完全相同，无变更。"

        summary_parts = []
        if stats['added'] > 0:
            summary_parts.append(f"新增 {stats['added']} 处内容")
        if stats['removed'] > 0:
            summary_parts.append(f"删除 {stats['removed']} 处内容")
        if stats['modified'] > 0:
            summary_parts.append(f"修改 {stats['modified']} 处内容")

        return f"📊 发现 {total_changes} 处变更：" + "，".join(summary_parts)

    @classmethod
    def generate_html_report(cls, result: DiffResult) -> str:
        """生成HTML格式报告"""
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DocDiff Pro - 差异分析报告</title>
    <style>
        :root {{
            --color-added: #d4edda;
            --color-added-border: #28a745;
            --color-removed: #f8d7da;
            --color-removed-border: #dc3545;
            --color-modified: #fff3cd;
            --color-modified-border: #ffc107;
            --color-unchanged: #f8f9fa;
            --text-primary: #212529;
            --text-secondary: #6c757d;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: var(--text-primary);
            background: #f5f5f5;
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 2rem;
            margin-bottom: 10px;
        }}

        .header p {{
            opacity: 0.9;
        }}

        .summary {{
            padding: 20px 30px;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
        }}

        .summary h2 {{
            margin-bottom: 15px;
            color: var(--text-primary);
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}

        .stat-card {{
            background: white;
            padding: 15px;
            border-radius: 6px;
            text-align: center;
            border-left: 4px solid;
        }}

        .stat-card.added {{ border-left-color: var(--color-added-border); }}
        .stat-card.removed {{ border-left-color: var(--color-removed-border); }}
        .stat-card.modified {{ border-left-color: var(--color-modified-border); }}
        .stat-card.unchanged {{ border-left-color: #6c757d; }}

        .stat-number {{
            font-size: 1.8rem;
            font-weight: bold;
            color: var(--text-primary);
        }}

        .stat-label {{
            color: var(--text-secondary);
            font-size: 0.9rem;
            margin-top: 5px;
        }}

        .files-info {{
            padding: 20px 30px;
            background: white;
            border-bottom: 1px solid #dee2e6;
        }}

        .file-comparison {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 20px;
            flex-wrap: wrap;
        }}

        .file-box {{
            background: #f8f9fa;
            padding: 15px 25px;
            border-radius: 6px;
            text-align: center;
        }}

        .file-box .label {{
            font-size: 0.8rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            margin-bottom: 5px;
        }}

        .file-box .name {{
            font-weight: 600;
            color: var(--text-primary);
        }}

        .arrow {{
            font-size: 1.5rem;
            color: var(--text-secondary);
        }}

        .diff-content {{
            padding: 30px;
        }}

        .diff-block {{
            margin-bottom: 20px;
            border-radius: 6px;
            overflow: hidden;
        }}

        .diff-header {{
            padding: 10px 15px;
            font-weight: 600;
            font-size: 0.85rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .diff-block.added .diff-header {{
            background: var(--color-added);
            color: var(--color-added-border);
        }}

        .diff-block.removed .diff-header {{
            background: var(--color-removed);
            color: var(--color-removed-border);
        }}

        .diff-block.modified .diff-header {{
            background: var(--color-modified);
            color: var(--color-modified-border);
        }}

        .diff-block.unchanged .diff-header {{
            background: #e9ecef;
            color: #6c757d;
        }}

        .diff-body {{
            padding: 15px;
            background: white;
            border: 1px solid #dee2e6;
            border-top: none;
        }}

        .diff-line {{
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 0.9rem;
            line-height: 1.5;
            padding: 3px 0;
            white-space: pre-wrap;
            word-break: break-all;
        }}

        .diff-line.old {{
            color: #721c24;
            text-decoration: line-through;
            opacity: 0.7;
        }}

        .diff-line.new {{
            color: #155724;
        }}

        .line-numbers {{
            display: flex;
            gap: 10px;
            color: var(--text-secondary);
            font-size: 0.75rem;
        }}

        .similarity-badge {{
            background: rgba(255,255,255,0.5);
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.75rem;
        }}

        .footer {{
            padding: 20px 30px;
            text-align: center;
            color: var(--text-secondary);
            font-size: 0.85rem;
            border-top: 1px solid #dee2e6;
        }}

        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 1.5rem;
            }}

            .stats-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}

            .file-comparison {{
                flex-direction: column;
            }}

            .arrow {{
                transform: rotate(90deg);
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📄 DocDiff Pro</h1>
            <p>智能文档差异分析报告</p>
        </div>

        <div class="summary">
            <h2>📊 变更概览</h2>
            <p>{result.summary}</p>
            <div class="stats-grid">
                <div class="stat-card added">
                    <div class="stat-number">{result.statistics['added']}</div>
                    <div class="stat-label">新增</div>
                </div>
                <div class="stat-card removed">
                    <div class="stat-number">{result.statistics['removed']}</div>
                    <div class="stat-label">删除</div>
                </div>
                <div class="stat-card modified">
                    <div class="stat-number">{result.statistics['modified']}</div>
                    <div class="stat-label">修改</div>
                </div>
                <div class="stat-card unchanged">
                    <div class="stat-number">{result.statistics['unchanged']}</div>
                    <div class="stat-label">未变更</div>
                </div>
            </div>
        </div>

        <div class="files-info">
            <div class="file-comparison">
                <div class="file-box">
                    <div class="label">源文件</div>
                    <div class="name">{os.path.basename(result.source_file)}</div>
                    <small>({result.source_format.upper()})</small>
                </div>
                <div class="arrow">→</div>
                <div class="file-box">
                    <div class="label">目标文件</div>
                    <div class="name">{os.path.basename(result.target_file)}</div>
                    <small>({result.target_format.upper()})</small>
                </div>
            </div>
        </div>

        <div class="diff-content">
            <h2 style="margin-bottom: 20px;">📝 详细差异</h2>
"""

        # 添加差异块
        for chunk in result.chunks:
            if chunk.change_type == ChangeType.UNCHANGED:
                continue  # 跳过未变更的内容

            change_type_class = chunk.change_type.value
            change_type_label = {
                ChangeType.ADDED: "➕ 新增",
                ChangeType.REMOVED: "➖ 删除",
                ChangeType.MODIFIED: "✏️ 修改",
                ChangeType.MOVED: "📦 移动"
            }.get(chunk.change_type, "未知")

            line_info = ""
            if chunk.old_line_start > 0:
                line_info += f"源文件第{chunk.old_line_start}行"
            if chunk.new_line_start > 0:
                if line_info:
                    line_info += " → "
                line_info += f"目标文件第{chunk.new_line_start}行"

            similarity_html = ""
            if chunk.similarity > 0 and chunk.similarity < 1:
                similarity_pct = int(chunk.similarity * 100)
                similarity_html = f'<span class="similarity-badge">相似度: {similarity_pct}%</span>'

            html += f"""
            <div class="diff-block {change_type_class}">
                <div class="diff-header">
                    <span>{change_type_label} - {line_info}</span>
                    {similarity_html}
                </div>
                <div class="diff-body">
"""

            if chunk.old_content and chunk.change_type != ChangeType.ADDED:
                html += f'<div class="diff-line old">{chunk.old_content}</div>'

            if chunk.new_content and chunk.change_type != ChangeType.REMOVED:
                html += f'<div class="diff-line new">{chunk.new_content}</div>'

            html += """
                </div>
            </div>
"""

        html += f"""
        </div>

        <div class="footer">
            <p>由 DocDiff Pro 生成 | 报告生成时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>
"""

        return html

    @classmethod
    def generate_json_report(cls, result: DiffResult) -> str:
        """生成JSON格式报告"""
        report_data = {
            'source_file': result.source_file,
            'target_file': result.target_file,
            'source_format': result.source_format,
            'target_format': result.target_format,
            'summary': result.summary,
            'statistics': result.statistics,
            'chunks': [
                {
                    'change_type': chunk.change_type.value,
                    'old_content': chunk.old_content,
                    'new_content': chunk.new_content,
                    'old_line_start': chunk.old_line_start,
                    'old_line_end': chunk.old_line_end,
                    'new_line_start': chunk.new_line_start,
                    'new_line_end': chunk.new_line_end,
                    'similarity': round(chunk.similarity, 4)
                }
                for chunk in result.chunks
            ]
        }

        return json.dumps(report_data, ensure_ascii=False, indent=2)

    @classmethod
    def generate_markdown_report(cls, result: DiffResult) -> str:
        """生成Markdown格式报告"""
        md = f"""# 📄 DocDiff Pro - 差异分析报告

## 📊 变更概览

{result.summary}

### 统计信息

| 类型 | 数量 |
|------|------|
| ➕ 新增 | {result.statistics['added']} |
| ➖ 删除 | {result.statistics['removed']} |
| ✏️ 修改 | {result.statistics['modified']} |
| ✅ 未变更 | {result.statistics['unchanged']} |

## 📁 文件信息

- **源文件**: `{result.source_file}` ({result.source_format.upper()})
- **目标文件**: `{result.target_file}` ({result.target_format.upper()})

## 📝 详细差异

"""

        for chunk in result.chunks:
            if chunk.change_type == ChangeType.UNCHANGED:
                continue

            change_emoji = {
                ChangeType.ADDED: "➕",
                ChangeType.REMOVED: "➖",
                ChangeType.MODIFIED: "✏️",
                ChangeType.MOVED: "📦"
            }.get(chunk.change_type, "❓")

            line_info = ""
            if chunk.old_line_start > 0:
                line_info += f"源文件第{chunk.old_line_start}行"
            if chunk.new_line_start > 0:
                if line_info:
                    line_info += " → "
                line_info += f"目标文件第{chunk.new_line_start}行"

            md += f"\n### {change_emoji} {chunk.change_type.value.upper()} - {line_info}\n\n"

            if chunk.similarity > 0 and chunk.similarity < 1:
                md += f"> 相似度: {int(chunk.similarity * 100)}%\n\n"

            if chunk.old_content and chunk.change_type != ChangeType.ADDED:
                md += f"**删除的内容:**\n```\n{chunk.old_content}\n```\n\n"

            if chunk.new_content and chunk.change_type != ChangeType.REMOVED:
                md += f"**新增的内容:**\n```\n{chunk.new_content}\n```\n\n"

        md += f"\n---\n\n*由 DocDiff Pro 生成 | 报告生成时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"

        return md


class DocDiffPro:
    """DocDiff Pro 主类"""

    def __init__(self):
        self.parser = DocumentParser()
        self.engine = DiffEngine()
        self.reporter = ReportGenerator()

    def compare(self, source_path: str, target_path: str) -> DiffResult:
        """比较两个文档"""
        # 解析源文件
        source_blocks, source_format = self.parser.parse_file(source_path)

        # 解析目标文件
        target_blocks, target_format = self.parser.parse_file(target_path)

        # 分析差异
        chunks = self.engine.analyze_diff(source_blocks, target_blocks)

        # 生成统计
        statistics = self.reporter.generate_statistics(chunks)

        # 生成摘要
        summary = self.reporter.generate_summary(chunks, statistics)

        return DiffResult(
            source_file=source_path,
            target_file=target_path,
            source_format=source_format,
            target_format=target_format,
            chunks=chunks,
            statistics=statistics,
            summary=summary
        )

    def export_report(self, result: DiffResult, output_path: str,
                     format_type: str = 'html') -> str:
        """导出报告"""
        if format_type == 'html':
            content = self.reporter.generate_html_report(result)
        elif format_type == 'json':
            content = self.reporter.generate_json_report(result)
        elif format_type == 'markdown' or format_type == 'md':
            content = self.reporter.generate_markdown_report(result)
        else:
            raise ValueError(f"不支持的报告格式: {format_type}")

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return output_path


def create_cli():
    """创建命令行接口"""
    parser = argparse.ArgumentParser(
        prog='docdiff',
        description='DocDiff Pro - 智能文档差异分析引擎',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s doc1.pdf doc2.pdf                    # 比较两个PDF文档
  %(prog)s old.md new.md -o report.html         # 生成HTML报告
  %(prog)s file1.txt file2.txt -f json          # 生成JSON格式报告
  %(prog)s doc.docx doc.md --unified            # 输出统一差异格式
        """
    )

    parser.add_argument('source', help='源文件路径')
    parser.add_argument('target', help='目标文件路径')
    parser.add_argument('-o', '--output', help='输出报告路径')
    parser.add_argument('-f', '--format', choices=['html', 'json', 'markdown', 'md'],
                       default='html', help='报告格式 (默认: html)')
    parser.add_argument('-u', '--unified', action='store_true',
                       help='输出统一差异格式（类似git diff）')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='显示详细输出')
    parser.add_argument('--version', action='version', version='%(prog)s 1.0.0')

    return parser


def main():
    """主函数"""
    parser = create_cli()
    args = parser.parse_args()

    # 验证文件存在
    if not os.path.exists(args.source):
        print(f"❌ 错误: 源文件不存在: {args.source}", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(args.target):
        print(f"❌ 错误: 目标文件不存在: {args.target}", file=sys.stderr)
        sys.exit(1)

    # 创建DocDiff实例
    docdiff = DocDiffPro()

    if args.verbose:
        print(f"🔍 正在比较文档...")
        print(f"   源文件: {args.source}")
        print(f"   目标文件: {args.target}")

    try:
        # 执行比较
        result = docdiff.compare(args.source, args.target)

        if args.verbose:
            print(f"\n✅ 比较完成!")
            print(f"\n{result.summary}")
            print(f"\n详细统计:")
            print(f"  - 新增: {result.statistics['added']}")
            print(f"  - 删除: {result.statistics['removed']}")
            print(f"  - 修改: {result.statistics['modified']}")
            print(f"  - 未变更: {result.statistics['unchanged']}")

        # 输出统一差异格式
        if args.unified:
            source_blocks, _ = DocumentParser.parse_file(args.source)
            target_blocks, _ = DocumentParser.parse_file(args.target)
            unified_diff = DiffEngine.generate_unified_diff(
                source_blocks, target_blocks,
                args.source, args.target
            )
            print(unified_diff)
            return

        # 生成报告
        if args.output:
            output_path = docdiff.export_report(result, args.output, args.format)
            print(f"\n📄 报告已保存: {output_path}")
        else:
            # 默认输出到控制台
            if args.format == 'json':
                print(ReportGenerator.generate_json_report(result))
            else:
                print(ReportGenerator.generate_markdown_report(result))

    except Exception as e:
        print(f"❌ 错误: {str(e)}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
