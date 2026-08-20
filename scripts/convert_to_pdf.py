#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 PowerShell COM 对象批量将 Word 文档转换为 PDF
通过 Python subprocess 调用 PowerShell，避免编码问题
"""

import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent

DOC_LIST = [
    "竞品分析",
    "技术文档",
    "财务预测与商业计划",
    "里程碑规划",
    "风险应对预案",
    "路演演讲稿",
    "答辩QA手册",
    "视频脚本",
    "部署指南",
]

def main():
    print("=" * 60)
    print("  批量转换 Word → PDF")
    print("=" * 60)
    print()

    for doc_name in DOC_LIST:
        docx_path = BASE_DIR / f"{doc_name}.docx"
        pdf_path = BASE_DIR / f"{doc_name}.pdf"

        if not docx_path.exists():
            print(f"⚠️  跳过 {doc_name}：docx文件不存在")
            continue

        # 使用 PowerShell COM 对象转换
        ps_script = f'''
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$doc = $word.Documents.Open("{docx_path}")
$doc.SaveAs("{pdf_path}", 17)
$doc.Close()
$word.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
'''
        try:
            result = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if pdf_path.exists():
                size_kb = pdf_path.stat().st_size / 1024
                print(f"✅ {doc_name}.pdf 已生成 ({size_kb:.1f} KB)")
            else:
                print(f"❌ {doc_name}.pdf 生成失败")
                if result.stderr:
                    print(f"   错误：{result.stderr[:200]}")
        except subprocess.TimeoutExpired:
            print(f"❌ {doc_name}.pdf 转换超时")
        except Exception as e:
            print(f"❌ {doc_name}.pdf 转换异常：{e}")

    print()
    print("=" * 60)
    print("  PDF 转换完成")
    print("=" * 60)


if __name__ == '__main__':
    main()
