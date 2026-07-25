"""
CreditMind · 尽调报告 PDF 导出
==============================
把 report_generator 生成的 Markdown 报告转成排版良好的 PDF，
专门用于打印 / 存档。

方案：reportlab + 内置中文字体 STSong-Light（Adobe CID 字体，
无需外部字体文件，离线可用，支持简体中文）。

支持元素：#/##/### 标题、> 引用、--- 分隔线、| 表格 |、- 无序列表、
1. 有序列表、**加粗**、`行内代码`、普通段落。
"""
from __future__ import annotations

import re
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import (
    HRFlowable,
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# 注册中文字体（仅需一次）
pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
CJK = "STSong-Light"

# 去掉 emoji（STSong-Light 无 emoji 字形，否则会显示方框/缺失）
EMOJI_RE = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F02F"
    "\U0001F0A0-\U0001F0FF\U0001F100-\U0001F1FF\U00002190-\U000021FF"
    "\U00002B00-\U00002BFF\U0000FE00-\U0000FE0F\U0000200D]"
)


def _clean(text: str) -> str:
    return EMOJI_RE.sub("", text).replace("\u200b", "")


def _inline(text: str) -> str:
    """转义 HTML 特殊字符，并把 **加粗** / `代码` 转成 reportlab 标签。"""
    text = _clean(text)
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`(.+?)`", r'<font face="Courier">\1</font>', text)
    return text


def _styles():
    base = ParagraphStyle("base", fontName=CJK, fontSize=10.5, leading=16, alignment=TA_LEFT)
    return {
        "title": ParagraphStyle("title", parent=base, fontSize=20, leading=26, spaceAfter=6),
        "h2": ParagraphStyle("h2", parent=base, fontSize=14, leading=20, spaceBefore=12, spaceAfter=4),
        "h3": ParagraphStyle("h3", parent=base, fontSize=11.5, leading=17, spaceBefore=8, spaceAfter=3),
        "body": ParagraphStyle("body", parent=base, spaceAfter=4),
        "quote": ParagraphStyle(
            "quote", parent=base, fontSize=9.5, leading=15, leftIndent=10,
            textColor=colors.HexColor("#444444"),
        ),
        "cell": ParagraphStyle("cell", parent=base, fontSize=9, leading=13),
        "cellh": ParagraphStyle("cellh", parent=base, fontSize=9, leading=13, textColor=colors.white),
    }


def markdown_to_pdf(markdown_text: str) -> bytes:
    """把 Markdown 尽调报告渲染为 PDF 字节流。"""
    st = _styles()
    flow = []
    lines = markdown_text.split("\n")
    i = 0
    n = len(lines)

    while i < n:
        raw = lines[i]
        line = raw.rstrip()

        # 分隔线
        if re.match(r"^-{3,}$", line.strip()):
            flow.append(HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#cccccc"),
                                   spaceBefore=6, spaceAfter=6))
            i += 1
            continue

        # 标题
        m = re.match(r"^(#{1,3})\s+(.*)$", line)
        if m:
            level = len(m.group(1))
            txt = _inline(m.group(2))
            style = {"title": st["title"], "h2": st["h2"], "h3": st["h3"]}[
                "title" if level == 1 else ("h2" if level == 2 else "h3")
            ]
            flow.append(Paragraph(txt, style))
            i += 1
            continue

        # 引用块（多行合并）
        if line.lstrip().startswith(">"):
            buf = []
            while i < n and lines[i].lstrip().startswith(">"):
                buf.append(lines[i].lstrip()[1:].lstrip())
                i += 1
            quote = "<br/>".join(_inline(b) for b in buf if b != "")
            flow.append(Paragraph(quote, st["quote"]))
            flow.append(Spacer(1, 4))
            continue

        # 表格（连续 | 开头行）
        if line.strip().startswith("|"):
            tbl = []
            while i < n and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                tbl.append(cells)
                i += 1
            # 去掉分隔行（第二行形如 |---|---|）
            if len(tbl) >= 2 and all(set(c) <= set("-: ") for c in tbl[1]):
                tbl = [tbl[0]] + tbl[2:]
            if tbl:
                header = tbl[0]
                data = [[Paragraph(_inline(c), st["cellh"]) for c in header]]
                for row in tbl[1:]:
                    data.append([Paragraph(_inline(c), st["cell"]) for c in row])
                t = Table(data, repeatRows=1, hAlign="LEFT")
                t.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bbbbbb")),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f4f6f8")]),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ]))
                flow.append(t)
                flow.append(Spacer(1, 6))
            continue

        # 无序列表
        if re.match(r"^-\s+", line):
            items = []
            while i < n and re.match(r"^-\s+", lines[i].rstrip()):
                items.append(ListItem(Paragraph(_inline(re.sub(r"^-\s+", "", lines[i].rstrip())), st["body"])))
                i += 1
            flow.append(ListFlowable(items, bulletType="bullet", leftIndent=14))
            flow.append(Spacer(1, 4))
            continue

        # 有序列表
        if re.match(r"^\d+\.\s+", line):
            items = []
            while i < n and re.match(r"^\d+\.\s+", lines[i].rstrip()):
                items.append(ListItem(Paragraph(_inline(re.sub(r"^\d+\.\s+", "", lines[i].rstrip())), st["body"])))
                i += 1
            flow.append(ListFlowable(items, bulletType="1", leftIndent=16))
            flow.append(Spacer(1, 4))
            continue

        # 空行
        if line.strip() == "":
            flow.append(Spacer(1, 4))
            i += 1
            continue

        # 普通段落（合并连续非空非特殊行）
        para = _inline(line)
        i += 1
        flow.append(Paragraph(para, st["body"]))

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm,
        topMargin=16 * mm, bottomMargin=16 * mm,
        title="CreditMind 尽调报告",
    )
    doc.build(flow)
    return buffer.getvalue()


if __name__ == "__main__":
    from model_server import CreditMindModel

    model = CreditMindModel.get()
    case = {
        "int_rate": 13.5, "term_months": 36, "tot_hi_cred_lim": 80000,
        "loan_amnt": 200000, "open_rv_24m": 3, "home_ownership": 1,
        "mort_acc": 1, "total_bc_limit": 50000, "num_tl_op_past_12m": 2,
        "mo_sin_rcnt_rev_tl_op": 6, "mo_sin_old_rev_tl_op": 120,
        "mths_since_recent_bc": 6, "verification_status": 1,
        "inq_last_6mths": 3, "emp_length": 5, "mths_since_recent_inq": 2,
        "inq_last_12m": 5, "annual_inc": 300000, "mo_sin_old_il_acct": 60,
    }
    pred = model.explain(case)
    from report_generator import generate_report
    md = generate_report(
        customer_info={"name": "张三", "loan_amnt": 200000, "purpose": "经营周转"},
        features=case, prediction=pred,
        dialogue_summary="客户为深圳电商老板，借款 20 万用于经营周转。",
    )
    pdf = markdown_to_pdf(md)
    with open("demo/test_report.pdf", "wb") as f:
        f.write(pdf)
    print(f"PDF 生成 OK, 大小 {len(pdf)} 字节 -> demo/test_report.pdf")
