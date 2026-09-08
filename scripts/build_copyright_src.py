"""软著源代码文档生成（每页50行，前30页+后30页，共60页3000行规范）

用法: python scripts/build_copyright_src.py
产出: docs/软著-源代码文档.docx
"""

from pathlib import Path

from docx import Document
from docx.shared import Pt

ROOT = Path(__file__).resolve().parent.parent
SRC_DIRS = [ROOT / "demo" / "app", ROOT / "demo" / "tests"]
OUT = ROOT / "docs" / "软著-源代码文档.docx"

SOFTWARE_NAME = "义乌小商品出海智能体平台"
VERSION = "V1.0"
LINES_PER_PAGE = 30 * 50  # 前30页
TAIL_LINES = 30 * 50      # 后30页


def collect_source_lines() -> list[str]:
    """按模块顺序收集源代码行，跳过空文件与__pycache__"""
    lines: list[str] = []
    for d in SRC_DIRS:
        for f in sorted(d.rglob("*.py")):
            if "__pycache__" in f.parts:
                continue
            lines.append(f"# ===== 文件: {f.relative_to(ROOT)} =====")
            lines.extend(f.read_text(encoding="utf-8", errors="replace").splitlines())
            lines.append("")  # 文件间隔
    return lines


def build():
    all_lines = collect_source_lines()
    total = len(all_lines)
    if total > LINES_PER_PAGE + TAIL_LINES:
        body = all_lines[:LINES_PER_PAGE] + \
               ["", "# ......（中间部分省略）......", ""] + \
               all_lines[-TAIL_LINES:]
    else:
        body = all_lines

    doc = Document()
    # 页眉：软件名称+版本号
    header = doc.sections[0].header
    hp = header.paragraphs[0]
    hp.text = f"{SOFTWARE_NAME} {VERSION} 源代码"

    for i in range(0, len(body), 50):
        page_lines = body[i:i + 50]
        for ln in page_lines:
            p = doc.add_paragraph()
            run = p.add_run(ln if ln.strip() else " ")
            run.font.name = "Consolas"
            run.font.size = Pt(9)
        # 软著规范：每页恰好50行，不足补空行
        for _ in range(50 - len(page_lines)):
            doc.add_paragraph(" ")
        doc.add_page_break()

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(OUT))
    pages = (len(body) + 49) // 50
    print(f"源代码文档: {OUT}")
    print(f"源码总行数: {total}, 文档页数: {pages}（每页50行）")


if __name__ == "__main__":
    build()
