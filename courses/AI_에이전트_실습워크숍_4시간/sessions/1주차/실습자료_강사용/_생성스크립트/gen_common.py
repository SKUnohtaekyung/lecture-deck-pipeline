# -*- coding: utf-8 -*-
"""실습 자료 생성 공통 도구 — 워드·엑셀·PPT 파일과 AI용 텍스트 사본을 함께 만든다.

가상 회사: 하루상점(온라인 생활용품 쇼핑몰, 직원 7명). 모든 이름·숫자는 지어낸 것이다.
"""
import csv
import json
import os

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from pptx import Presentation
from pptx.dml.color import RGBColor as PRGB
from pptx.util import Inches, Pt as PPt

HERE = os.path.dirname(os.path.abspath(__file__))
INST = os.path.dirname(HERE)                                  # 실습자료_강사용
BASE = os.path.join(os.path.dirname(INST), '실습자료')          # 실습자료
DATA = os.path.join(INST, '_data')                            # 완성 예시가 쓰는 정답 데이터
COPY = '_AI용_텍스트사본'

COMPANY = '하루상점'
TEAM = {
    '한지우': '대표', '박서준': '운영 팀장', '김나연': '상품기획(MD)', '이도현': '마케팅',
    '최유나': '고객지원(CS)', '정민서': '디자인', '오태호': '물류',
}
KFONT = '맑은 고딕'


def ensure(path):
    os.makedirs(path, exist_ok=True)
    return path


def _kfont(run, size=None, bold=None, color=None):
    run.font.name = KFONT
    run._element.rPr.rFonts.set(qn('w:eastAsia'), KFONT)
    if size:
        run.font.size = Pt(size)
    if bold is not None:
        run.font.bold = bold
    if color:
        run.font.color.rgb = RGBColor(*color)


def write_docx(path, title, blocks, subtitle=None):
    """blocks: ('h', 글) · ('p', 글) · ('b', [항목]) · ('t', [머리], [[행]]) 의 목록.
    같은 내용을 텍스트 사본으로도 돌려준다."""
    doc = Document()
    st = doc.styles['Normal']
    st.font.name = KFONT
    st.element.rPr.rFonts.set(qn('w:eastAsia'), KFONT)
    st.font.size = Pt(10.5)
    h = doc.add_paragraph()
    _kfont(h.add_run(title), size=20, bold=True, color=(0x12, 0x3B, 0x4A))
    lines = ['# ' + title]
    if subtitle:
        p = doc.add_paragraph()
        _kfont(p.add_run(subtitle), size=10, color=(0x66, 0x70, 0x78))
        lines.append(subtitle)
    for b in blocks:
        kind = b[0]
        if kind == 'h':
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(12)
            _kfont(p.add_run(b[1]), size=13.5, bold=True, color=(0x0E, 0x4A, 0x5A))
            lines += ['', '## ' + b[1]]
        elif kind == 'p':
            p = doc.add_paragraph()
            _kfont(p.add_run(b[1]))
            lines.append(b[1])
        elif kind == 'b':
            for item in b[1]:
                p = doc.add_paragraph(style='List Bullet')
                _kfont(p.add_run(item))
                lines.append('- ' + item)
        elif kind == 't':
            head, rows = b[1], b[2]
            tb = doc.add_table(rows=1, cols=len(head))
            tb.style = 'Light Grid Accent 1'
            for i, hd in enumerate(head):
                c = tb.rows[0].cells[i]
                c.text = ''
                _kfont(c.paragraphs[0].add_run(str(hd)), size=10, bold=True)
            for r in rows:
                cells = tb.add_row().cells
                for i, v in enumerate(r):
                    cells[i].text = ''
                    _kfont(cells[i].paragraphs[0].add_run(str(v)), size=10)
            lines.append(' | '.join(str(x) for x in head))
            lines += [' | '.join(str(x) for x in r) for r in rows]
    ensure(os.path.dirname(path))
    doc.save(path)
    return '\n'.join(lines) + '\n'


def write_xlsx(path, sheets):
    """sheets: [(시트 이름, [머리], [[행]], {열 번호: 폭})]. 시트별 CSV 문자열 목록을 돌려준다."""
    wb = Workbook()
    wb.remove(wb.active)
    out = []
    fill = PatternFill('solid', fgColor='0E4A5A')
    for name, head, rows, *rest in sheets:
        widths = rest[0] if rest else {}
        ws = wb.create_sheet(name)
        ws.append(head)
        for c in ws[1]:
            c.font = Font(name=KFONT, bold=True, color='FFFFFF')
            c.fill = fill
            c.alignment = Alignment(horizontal='center', vertical='center')
        for r in rows:
            ws.append(r)
        for row in ws.iter_rows(min_row=2):
            for c in row:
                c.font = Font(name=KFONT, size=10)
                if isinstance(c.value, (int, float)) and abs(c.value) >= 1000:
                    c.number_format = '#,##0'
                if isinstance(c.value, str) and len(c.value) > 30:
                    c.alignment = Alignment(wrap_text=True, vertical='top')
        for i in range(1, len(head) + 1):
            ws.column_dimensions[get_column_letter(i)].width = widths.get(i, 14)
        ws.freeze_panes = 'A2'
        out.append((name, head, rows))
    ensure(os.path.dirname(path))
    wb.save(path)
    return out


def write_pptx(path, slides):
    """slides: [(제목, [글머리])] 또는 (제목, [글머리], 표=(머리, 행)). 텍스트 사본을 돌려준다."""
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    lines = []
    for n, s in enumerate(slides, 1):
        title, bullets = s[0], s[1]
        table = s[2] if len(s) > 2 else None
        sl = prs.slides.add_slide(prs.slide_layouts[6])
        bar = sl.shapes.add_shape(1, 0, 0, prs.slide_width, Inches(1.15))
        bar.fill.solid()
        bar.fill.fore_color.rgb = PRGB(0x0E, 0x4A, 0x5A)
        bar.line.fill.background()
        tx = sl.shapes.add_textbox(Inches(0.6), Inches(0.22), Inches(12), Inches(0.8)).text_frame
        r = tx.paragraphs[0].add_run()
        r.text = title
        r.font.size, r.font.bold, r.font.name = PPt(30), True, KFONT
        r.font.color.rgb = PRGB(0xFF, 0xFF, 0xFF)
        body = sl.shapes.add_textbox(Inches(0.7), Inches(1.5), Inches(12 if not table else 5.6), Inches(5.4)).text_frame
        body.word_wrap = True
        for i, b in enumerate(bullets):
            p = body.paragraphs[0] if i == 0 else body.add_paragraph()
            rr = p.add_run()
            rr.text = '• ' + b
            rr.font.size, rr.font.name = PPt(20), KFONT
            p.space_after = PPt(10)
        lines += ['', '[슬라이드 %d] %s' % (n, title)] + ['- ' + b for b in bullets]
        if table:
            head, rows = table
            shp = sl.shapes.add_table(len(rows) + 1, len(head), Inches(6.6), Inches(1.6), Inches(6.2), Inches(0.45) * (len(rows) + 1))
            for i, hd in enumerate(head):
                shp.table.cell(0, i).text = str(hd)
            for ri, row in enumerate(rows, 1):
                for ci, v in enumerate(row):
                    shp.table.cell(ri, ci).text = str(v)
            for row in shp.table.rows:
                for c in row.cells:
                    for p in c.text_frame.paragraphs:
                        for rr in p.runs:
                            rr.font.size, rr.font.name = PPt(14), KFONT
            lines.append(' | '.join(str(x) for x in head))
            lines += [' | '.join(str(x) for x in r) for r in rows]
    ensure(os.path.dirname(path))
    prs.save(path)
    return '\n'.join(lines).strip() + '\n'


def write_text(path, text):
    ensure(os.path.dirname(path))
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)


def write_csv(path, head, rows):
    ensure(os.path.dirname(path))
    with open(path, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(head)
        w.writerows(rows)


def copy_xlsx(folder, stem, sheets):
    """엑셀의 시트마다 CSV 사본을 만든다."""
    for name, head, rows in sheets:
        write_csv(os.path.join(folder, COPY, '%s__%s.csv' % (stem, name)), head, rows)


def dump(name, obj):
    ensure(DATA)
    with open(os.path.join(DATA, name), 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)


def won(n):
    return format(int(round(n)), ',') + '원'
