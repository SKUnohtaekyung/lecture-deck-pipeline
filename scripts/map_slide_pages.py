#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""쪽번호 → data-slide ID 매핑 스냅샷 생성 — 수정요청 접수의 좌표 고정 (P3 · 배치3).

왜 필요한가
----------
사용자는 화면 쪽번호로 말하고, 덱은 ID(data-slide)로 산다. 덱이 재구성되면 쪽번호가
밀려 같은 「46p」가 시점마다 다른 슬라이드를 가리켰다 — 판정 확인불가 172건의 상당
사유이자 오병합의 구조 원인이다(`plans/system-improvement/ANALYSIS.md` §2-기제4).
접수 시점에 이 표를 개정이력에 함께 저장하면 이후 처리·보고·검증을 ID로만 지칭할
수 있다. 사용자는 지금처럼 쪽번호로 말해도 된다 — 번역은 이 표가 한다.

쪽번호의 정의 (정본: 덱 하이드레이션 JS)
---------------------------------------
표시 쪽번호 = **전체 `.slide` 배열의 DOM 인덱스 + 1** (표지 포함).
cover·concept-recap·closing은 화면에 번호가 **표시되지 않을 뿐** 배열 자리는
차지한다(덱 JS가 그 클래스에만 `.s-pageno`를 붙이지 않는다) — 건너뛰며 세지 마라.
이 표에서는 «표시 없음»으로 주석한다.

사용
----
    python scripts/map_slide_pages.py <주차>              # 개정이력/쪽ID매핑_<sha8>.md 생성
    python scripts/map_slide_pages.py <주차> --stdout     # 파일 없이 표만 출력
    python scripts/map_slide_pages.py --deck <경로> [--out <경로>]

파일명이 덱 sha256 앞 8자를 담으므로 같은 덱에서는 같은 파일이 나온다(멱등 —
이미 있으면 다시 쓰지 않는다). 덱이 재구성되면 sha가 갈려 새 스냅샷이 생긴다.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from verify_deck import parse_document, _slide_elements  # noqa: E402

# 덱 JS와 동일한 «번호 미표시» 클래스 집합 — 자리는 차지한다.
_NO_PAGENO_RE = re.compile(r"\b(cover|concept-recap|closing)\b")


def _strip_tags(fragment: str) -> str:
    import html as _h
    txt = re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", _h.unescape(txt)).strip()


def _slide_title(inner_html: str, cls_str: str) -> str:
    """대표 제목: .s-title → 첫 h1~h3 → .pd-title(간지) → 클래스 첫 토큰."""
    m = re.search(r'class="[^"]*\bs-title\b[^"]*"[^>]*>(.*?)</', inner_html, re.S)
    if m and _strip_tags(m.group(1)):
        return _strip_tags(m.group(1))
    m = re.search(r"<h[1-3]\b[^>]*>(.*?)</h[1-3]\s*>", inner_html, re.S | re.I)
    if m and _strip_tags(m.group(1)):
        return _strip_tags(m.group(1))
    m = re.search(r'class="[^"]*\bpd-title\b[^"]*"[^>]*>(.*?)</', inner_html, re.S)
    if m and _strip_tags(m.group(1)):
        return _strip_tags(m.group(1))
    first = (cls_str or "").split()
    return f"({first[1] if len(first) > 1 else (first[0] if first else '무클래스')})"


def build_mapping(deck_path: str):
    """(rows, sha8, n_slides) — rows: (쪽, id, 제목, 표시여부)."""
    with open(deck_path, "rb") as fh:
        raw = fh.read()
    sha8 = hashlib.sha256(raw).hexdigest()[:8]
    html_text = raw.decode("utf-8")
    html_text = re.sub(r"<!--.*?-->", "", html_text, flags=re.S)
    _tags, elements = parse_document(html_text)
    slides = sorted(_slide_elements(elements), key=lambda e: e.start)
    rows = []
    for i, el in enumerate(slides):
        cls_str = el.attrs.get("class") or ""
        sid = el.attrs.get("data-slide") or "(무ID)"
        title = _slide_title(html_text[el.inner_start:el.inner_end], cls_str)
        shown = not _NO_PAGENO_RE.search(cls_str)
        rows.append((i + 1, sid, title, shown))
    return rows, sha8, len(slides)


def render_markdown(deck_rel: str, rows, sha8: str, today: str) -> str:
    out = [
        f"# 쪽 ↔ ID 매핑 스냅샷 (자동 생성 — 수정 금지)",
        "",
        f"- 기준 덱: `{deck_rel}` · **{len(rows)}장** · sha256 `{sha8}` · 생성 {today}",
        "- 쪽번호 = 전체 슬라이드 배열의 순번(표지 포함). «표시 없음» 장은 화면에 번호가",
        "  안 보일 뿐 자리는 차지한다(정본: 덱 하이드레이션 JS).",
        "- **접수 시점 스냅샷이다.** 덱이 재구성되면 `python scripts/map_slide_pages.py <주차>`로",
        "  새로 만든다 — 파일명의 sha가 갈려 옛 표를 덮지 않는다. 이후 처리·보고·검증은",
        "  쪽번호가 아니라 **ID로만** 지칭한다(`입력양식/수정요청접수템플릿.md`).",
        "",
        "| 쪽 | data-slide | 제목 | 비고 |",
        "|---:|---|---|---|",
    ]
    for page, sid, title, shown in rows:
        note = "" if shown else "표시 없음"
        out.append(f"| {page} | `{sid}` | {title} | {note} |")
    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("week", nargs="?", help="주차 (예: 3주차) — --deck을 주면 생략 가능")
    ap.add_argument("--deck", help="덱 경로 직접 지정")
    ap.add_argument("--out", help="출력 경로(기본: <세션>/개정이력/쪽ID매핑_<sha8>.md)")
    ap.add_argument("--stdout", action="store_true", help="파일을 쓰지 않고 표만 출력")
    a = ap.parse_args()

    if a.deck:
        deck = a.deck
        session = os.path.dirname(os.path.abspath(deck))
    elif a.week:
        try:
            import _course_paths
            num = a.week[:-2] if a.week.endswith("주차") else a.week
            session = _course_paths.session_dir(num, ROOT)
        except Exception:
            print("[실패] 주차 경로를 해석하지 못했다 — --deck으로 직접 지정하라")
            return 2
        deck = os.path.join(session, "강의덱.html")
    else:
        ap.print_usage()
        return 2

    if not os.path.exists(deck):
        print(f"[실패] 덱이 없다: {deck}")
        return 2

    rows, sha8, n = build_mapping(deck)
    if n == 0:
        print("[실패] 슬라이드 0장 — 파싱 실패를 성공으로 세지 않는다(눈먼 0 방지)")
        return 1
    deck_rel = os.path.relpath(deck, ROOT).replace("\\", "/")
    md = render_markdown(deck_rel, rows, sha8, _dt.date.today().isoformat())

    if a.stdout:
        print(md)
        return 0

    out = a.out or os.path.join(session, "개정이력", f"쪽ID매핑_{sha8}.md")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    if os.path.exists(out) and not a.out:
        print(f"[멱등] 같은 덱(sha {sha8})의 스냅샷이 이미 있다 — {os.path.relpath(out, ROOT)}")
        print(f"       {n}장 · 접수에는 이 파일을 그대로 쓴다.")
        return 0
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(md)
    print(f"[생성] {os.path.relpath(out, ROOT)} — {n}장 · sha {sha8}")
    print("       접수 템플릿: 입력양식/수정요청접수템플릿.md (이후 지칭은 ID로만)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
