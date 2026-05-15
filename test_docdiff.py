#!/usr/bin/env python3
"""
DocDiff Pro - 单元测试
"""

import unittest
import tempfile
import os
import sys
from docdiff import (
    DocumentParser, DiffEngine, ReportGenerator,
    TextBlock, DiffChunk, ChangeType, DiffResult, DocDiffPro
)


class TestTextBlock(unittest.TestCase):
    """测试TextBlock类"""

    def test_block_creation(self):
        """测试文本块创建"""
        block = TextBlock(content="Hello World", line_number=1, block_id=1)
        self.assertEqual(block.content, "Hello World")
        self.assertEqual(block.line_number, 1)
        self.assertEqual(block.block_id, 1)
        self.assertTrue(block.checksum)  # 校验和应自动生成

    def test_checksum_consistency(self):
        """测试校验和一致性"""
        block1 = TextBlock(content="Test", line_number=1, block_id=1)
        block2 = TextBlock(content="Test", line_number=2, block_id=2)
        self.assertEqual(block1.checksum, block2.checksum)


class TestDocumentParser(unittest.TestCase):
    """测试文档解析器"""

    def test_detect_format(self):
        """测试格式检测"""
        self.assertEqual(DocumentParser.detect_format("test.pdf"), "pdf")
        self.assertEqual(DocumentParser.detect_format("test.docx"), "docx")
        self.assertEqual(DocumentParser.detect_format("test.md"), "markdown")
        self.assertEqual(DocumentParser.detect_format("test.txt"), "text")
        self.assertEqual(DocumentParser.detect_format("test.unknown"), "unknown")

    def test_read_text_file(self):
        """测试文本文件读取"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Line 1\nLine 2\nLine 3")
            temp_path = f.name

        try:
            blocks = DocumentParser.read_text_file(temp_path)
            self.assertEqual(len(blocks), 3)
            self.assertEqual(blocks[0].content, "Line 1")
            self.assertEqual(blocks[1].content, "Line 2")
            self.assertEqual(blocks[2].content, "Line 3")
        finally:
            os.unlink(temp_path)

    def test_parse_file_text(self):
        """测试解析文本文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Title\n\nContent here")
            temp_path = f.name

        try:
            blocks, format_type = DocumentParser.parse_file(temp_path)
            self.assertEqual(format_type, "markdown")
            self.assertGreaterEqual(len(blocks), 2)  # 至少2行（标题+内容）
        finally:
            os.unlink(temp_path)


class TestDiffEngine(unittest.TestCase):
    """测试差异引擎"""

    def test_calculate_similarity_identical(self):
        """测试相同文本的相似度"""
        similarity = DiffEngine.calculate_similarity("hello", "hello")
        self.assertEqual(similarity, 1.0)

    def test_calculate_similarity_different(self):
        """测试不同文本的相似度"""
        similarity = DiffEngine.calculate_similarity("hello", "world")
        self.assertLess(similarity, 1.0)
        self.assertGreaterEqual(similarity, 0.0)

    def test_calculate_similarity_empty(self):
        """测试空文本的相似度"""
        self.assertEqual(DiffEngine.calculate_similarity("", ""), 1.0)
        self.assertEqual(DiffEngine.calculate_similarity("hello", ""), 0.0)

    def test_analyze_diff_identical(self):
        """测试相同文档的差异分析"""
        blocks = [TextBlock(content="Line 1", line_number=1, block_id=1)]
        chunks = DiffEngine.analyze_diff(blocks, blocks)

        unchanged_chunks = [c for c in chunks if c.change_type == ChangeType.UNCHANGED]
        self.assertEqual(len(unchanged_chunks), 1)

    def test_analyze_diff_added(self):
        """测试新增内容的差异分析"""
        source = [TextBlock(content="Line 1", line_number=1, block_id=1)]
        target = [
            TextBlock(content="Line 1", line_number=1, block_id=1),
            TextBlock(content="Line 2", line_number=2, block_id=2)
        ]
        chunks = DiffEngine.analyze_diff(source, target)

        added_chunks = [c for c in chunks if c.change_type == ChangeType.ADDED]
        self.assertEqual(len(added_chunks), 1)
        self.assertEqual(added_chunks[0].new_content, "Line 2")

    def test_analyze_diff_removed(self):
        """测试删除内容的差异分析"""
        source = [
            TextBlock(content="Line 1", line_number=1, block_id=1),
            TextBlock(content="Line 2", line_number=2, block_id=2)
        ]
        target = [TextBlock(content="Line 1", line_number=1, block_id=1)]
        chunks = DiffEngine.analyze_diff(source, target)

        removed_chunks = [c for c in chunks if c.change_type == ChangeType.REMOVED]
        self.assertEqual(len(removed_chunks), 1)
        self.assertEqual(removed_chunks[0].old_content, "Line 2")


class TestReportGenerator(unittest.TestCase):
    """测试报告生成器"""

    def test_generate_statistics(self):
        """测试统计信息生成"""
        chunks = [
            DiffChunk(ChangeType.ADDED, "", "new", 0, 0, 1, 1),
            DiffChunk(ChangeType.REMOVED, "old", "", 1, 1, 0, 0),
            DiffChunk(ChangeType.UNCHANGED, "same", "same", 2, 2, 2, 2),
        ]
        stats = ReportGenerator.generate_statistics(chunks)

        self.assertEqual(stats['added'], 1)
        self.assertEqual(stats['removed'], 1)
        self.assertEqual(stats['unchanged'], 1)

    def test_generate_summary_no_changes(self):
        """测试无变更时的摘要"""
        chunks = [DiffChunk(ChangeType.UNCHANGED, "same", "same", 1, 1, 1, 1)]
        stats = ReportGenerator.generate_statistics(chunks)
        summary = ReportGenerator.generate_summary(chunks, stats)
        self.assertIn("完全相同", summary)

    def test_generate_summary_with_changes(self):
        """测试有变更时的摘要"""
        chunks = [
            DiffChunk(ChangeType.ADDED, "", "new", 0, 0, 1, 1),
            DiffChunk(ChangeType.REMOVED, "old", "", 1, 1, 0, 0),
        ]
        stats = ReportGenerator.generate_statistics(chunks)
        summary = ReportGenerator.generate_summary(chunks, stats)
        self.assertIn("新增", summary)
        self.assertIn("删除", summary)


class TestDocDiffPro(unittest.TestCase):
    """测试DocDiffPro主类"""

    def setUp(self):
        """设置测试环境"""
        self.docdiff = DocDiffPro()

        # 创建临时测试文件
        self.temp_files = []

    def tearDown(self):
        """清理测试环境"""
        for temp_file in self.temp_files:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def _create_temp_file(self, content, suffix='.txt'):
        """创建临时文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False) as f:
            f.write(content)
            self.temp_files.append(f.name)
            return f.name

    def test_compare_identical_files(self):
        """测试比较相同文件"""
        content = "Line 1\nLine 2\nLine 3"
        file1 = self._create_temp_file(content)
        file2 = self._create_temp_file(content)

        result = self.docdiff.compare(file1, file2)

        self.assertEqual(result.source_file, file1)
        self.assertEqual(result.target_file, file2)
        self.assertEqual(result.statistics['added'], 0)
        self.assertEqual(result.statistics['removed'], 0)

    def test_compare_different_files(self):
        """测试比较不同文件"""
        file1 = self._create_temp_file("Line 1\nLine 2")
        file2 = self._create_temp_file("Line 1\nLine 3")

        result = self.docdiff.compare(file1, file2)

        self.assertGreater(
            result.statistics['modified'] + result.statistics['removed'] + result.statistics['added'],
            0
        )

    def test_export_report_html(self):
        """测试导出HTML报告"""
        file1 = self._create_temp_file("Line 1")
        file2 = self._create_temp_file("Line 2")

        result = self.docdiff.compare(file1, file2)

        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as f:
            output_path = f.name
            self.temp_files.append(output_path)

        exported_path = self.docdiff.export_report(result, output_path, 'html')

        self.assertTrue(os.path.exists(exported_path))
        with open(exported_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('<!DOCTYPE html>', content)
            self.assertIn('DocDiff Pro', content)

    def test_export_report_json(self):
        """测试导出JSON报告"""
        file1 = self._create_temp_file("Line 1")
        file2 = self._create_temp_file("Line 2")

        result = self.docdiff.compare(file1, file2)

        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            output_path = f.name
            self.temp_files.append(output_path)

        exported_path = self.docdiff.export_report(result, output_path, 'json')

        self.assertTrue(os.path.exists(exported_path))
        with open(exported_path, 'r', encoding='utf-8') as f:
            import json
            data = json.load(f)
            self.assertIn('statistics', data)
            self.assertIn('chunks', data)


class TestIntegration(unittest.TestCase):
    """集成测试"""

    def test_full_workflow(self):
        """测试完整工作流程"""
        docdiff = DocDiffPro()

        # 创建测试文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f1:
            f1.write("# Document\n\nOriginal content here.")
            file1 = f1.name

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f2:
            f2.write("# Document\n\nUpdated content here.\n\nNew section added.")
            file2 = f2.name

        try:
            # 比较文档
            result = docdiff.compare(file1, file2)

            # 验证结果
            self.assertIsNotNone(result.summary)
            self.assertGreater(len(result.chunks), 0)

            # 生成报告
            with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as f:
                report_path = f.name

            docdiff.export_report(result, report_path, 'html')
            self.assertTrue(os.path.exists(report_path))

            with open(report_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn('DocDiff Pro', content)
                self.assertIn('变更概览', content)

            os.unlink(report_path)

        finally:
            os.unlink(file1)
            os.unlink(file2)


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestTextBlock))
    suite.addTests(loader.loadTestsFromTestCase(TestDocumentParser))
    suite.addTests(loader.loadTestsFromTestCase(TestDiffEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestReportGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestDocDiffPro))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
