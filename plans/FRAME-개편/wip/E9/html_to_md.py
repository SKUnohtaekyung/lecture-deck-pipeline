# -*- coding: utf-8 -*-
"""발표자 노트 HTML → 텍스트만 추출한 md (tone_lint 입력용). 사용: python html_to_md.py <in.html> <out.md>"""
import re
import sys
from html.parser import HTMLParser


class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []
        self.buf = []
        self.mode = None      # 현재 블록 종류
        self.skip = 0         # style · script · title · 주석은 handle_comment 로 무시
        self.row = []
        self.in_cell = False
        self.no = self.id = self.tm = ""
        self.cap = None

    def flush(self, kind=None):
        t = re.sub(r"\s+", " ", "".join(self.buf)).strip()
        self.buf = []
        if not t:
            return
        k = kind or self.mode
        if k == "h1":
            self.out.append("# " + t)
        elif k == "h2":
            self.out.append("## " + t)
        elif k == "li":
            self.out.append("- " + t)
        else:
            self.out.append(t)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = (a.get("class") or "").split()
        if tag in ("style", "title"):
            self.skip += 1
            return
        if tag in ("h1", "h2", "p", "li", "div", "tr", "section", "ul", "table", "header", "span"):
            if "pn-no" in cls:
                self.flush(); self.cap = "no"; self.buf = []; return
            if "pn-id" in cls:
                self.flush(); self.cap = "id"; self.buf = []; return
            if "pn-time" in cls:
                self.flush(); self.cap = "tm"; self.buf = []; return
            if tag == "span" and "lbl" in cls:
                self.flush(); self.mode = "lbl"; return
            if tag == "span":
                return
        if tag == "h1":
            self.flush(); self.mode = "h1"
        elif tag == "h2":
            self.flush(); self.mode = "h2"
        elif tag == "li":
            self.flush(); self.mode = "li"
        elif tag == "p":
            self.flush(); self.mode = "p"
        elif tag == "div":
            self.flush(); self.mode = "div"
        elif tag == "tr":
            self.row = []
        elif tag in ("td", "th"):
            self.buf = []; self.in_cell = True

    def handle_endtag(self, tag):
        if tag in ("style", "title"):
            self.skip -= 1
            return
        if self.cap and tag == "span":
            t = re.sub(r"\s+", " ", "".join(self.buf)).strip()
            setattr(self, {"no": "no", "id": "id", "tm": "tm"}[self.cap], t)
            if self.cap == "tm":
                self.out.append(f"{self.id} · {self.no}쪽 · {self.tm}")
            self.buf = []; self.cap = None
            return
        if tag == "span" and self.mode == "lbl":
            self.flush("p"); self.mode = None
            return
        if tag in ("td", "th"):
            self.row.append(re.sub(r"\s+", " ", "".join(self.buf)).strip()); self.buf = []; self.in_cell = False
        elif tag == "tr":
            self.out.append("| " + " | ".join(self.row) + " |")
            self.row = []
        elif tag in ("h1", "h2", "p", "li", "div"):
            self.flush(); self.mode = None

    def handle_data(self, d):
        if self.skip:
            return
        self.buf.append(d)


def main():
    src = open(sys.argv[1], encoding="utf-8").read()
    p = P()
    p.feed(src)
    p.flush()
    lines = []
    prev_kind = None
    for ln in p.out:
        kind = "list" if ln.startswith("- ") else ("table" if ln.startswith("|") else "other")
        if lines and not (kind == prev_kind and kind in ("list", "table")):
            lines.append("")
        lines.append(ln)
        prev_kind = kind
    open(sys.argv[2], "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
    print("written", sys.argv[2], len(lines), "lines")


main()
