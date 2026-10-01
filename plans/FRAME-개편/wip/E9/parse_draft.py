# -*- coding: utf-8 -*-
"""초안 표(4열)와 결정표(분 열)를 읽어 행 목록을 만든다. 표준 라이브러리만."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DRAFT = ROOT / "courses/AI_에이전트_실습워크숍_4시간/sessions/1주차/1주차_초안.md"
DECIDE = ROOT / "plans/FRAME-개편/결정표.md"


def split_row(line):
    s = line.strip()
    assert s.startswith("|") and s.endswith("|"), line[:60]
    body = s[1:-1]
    # 표 안의 이스케이프된 파이프(&#124;)는 그대로 둔다. 일반 | 로만 나눈다.
    return [c.strip() for c in body.split("|")]


def read_draft():
    rows = []
    block = None
    for line in DRAFT.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            block = line[3:].strip()
        if not line.startswith("|"):
            continue
        cells = split_row(line)
        if len(cells) != 4:
            continue
        if cells[0] in ("#", "---") or set(cells[0]) <= set("-: "):
            continue
        if cells[0] in ("표기", "항목"):
            continue
        rows.append({"id": cells[0], "title": cells[1], "screen": cells[2], "cue": cells[3], "section": block})
    return rows


def read_decide():
    out = {}
    for line in DECIDE.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = split_row(line)
        if len(cells) < 13 or cells[0] in ("ID", "---") or set(cells[0]) <= set("-: "):
            continue
        out[cells[0]] = {"part": cells[1], "block": cells[2], "min": float(cells[3]), "kind": cells[4], "title": cells[5]}
    return out


if __name__ == "__main__":
    d = read_draft()
    c = read_decide()
    print(len(d), len(c))
    print([r["id"] for r in d if r["id"] not in c], [k for k in c if k not in [r["id"] for r in d]])
    print("order same:", [r["id"] for r in d] == list(c))
    print("C rows:", sum(1 for r in d if r["id"].startswith("C-")), "개념 kind:", sum(1 for v in c.values() if v["kind"] == "개념"))
    from collections import Counter
    print(Counter(v["kind"] for v in c.values()))
    blk = {}
    for k, v in c.items():
        blk.setdefault(v["block"], 0)
        blk[v["block"]] += v["min"]
    print(blk)
