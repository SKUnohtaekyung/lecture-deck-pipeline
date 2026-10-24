# -*- coding: utf-8 -*-
"""발표 노트 md → 발표자 노트 HTML (세컨브레인 특강 1주차).

입력(기본)
  courses/세컨브레인_특강/sessions/1주차/1주차_발표노트_실습.md
  courses/세컨브레인_특강/sessions/1주차/1주차_발표노트_개념.md      (없으면 건너뛴다)
  형식:  `## <data-slide ID>` 아래 `- 한 줄` 목록. 줄은 마크다운 원문 그대로 둔다(`**굵게**` · `` `코드` ``).
조립본
  courses/세컨브레인_특강/sessions/1주차/강의덱.html 의 `section.slide[data-slide]` 문서 순서가 장 순서다.
출력(기본)
  courses/세컨브레인_특강/sessions/1주차/강의덱_발표자노트.html
  kit/starter/presenter-notes-template.html 구조: `.pn-slide > .pn-slide-head(span.pn-no + h2.pn-slide-title) + .pn-item.pn-md`.
  · span.pn-no  = 1부터 정수 쪽 번호(inject_presenter.py가 `pn-no - 1`로 장을 찾는다).
  · h2 제목     = 그 장의 첫 h1~h3 글자(inject_presenter.map_notes와 같은 규칙. 제목 없는 장은 장 ID).
  · 줄마다 `<p>` 한 개, 원문 그대로. 발표자 화면 런타임이 `- `·`**`·`` ` ``를 직접 그린다 —
    `<li>`·`<strong>`으로 바꾸면 inject가 태그를 벗길 때 목록 표시와 굵기가 사라진다.
  · 노트 없는 장 = 빈 `.pn-item.pn-md.pn-none` 블록(블록 수 = 장 수). 「노트 없음」은 CSS ::before로 보인다 —
    본문 글자로 넣으면 발표자 화면 노트 칸에 그 글자가 실려 런타임의 빈 노트 안내(눌러서 적습니다)를
    가리고, 발표본 노트 JSON이 `"ID":[]`(노트 없음)인지 글자가 있는지 구분되지 않게 된다.

보고(표준 출력): 「RESULT 장 N · 노트 있음 A · 없음 B · 덱에 없는 노트 C」 + 목록.
쓴 뒤에는 inject_presenter의 파서·매핑으로 같은 파일을 다시 읽어 매핑 수를 확인한다.

    python plans/세컨브레인-특강/tools/build_presenter_notes.py [--check] [--strict]
종료코드: 0 정상 · 1 입력 오류·중복 ID·자기검증 실패(--strict이면 노트 없는 장·덱에 없는 노트도) · 2 인자 오류.
"""
from __future__ import annotations

import argparse
import html as _html
import os
import re
import sys

sys.dont_write_bytecode = True   # 저장소에 __pycache__를 남기지 않는다
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import inject_presenter as ip  # noqa: E402  (슬라이드 스캔·노트 매핑 규칙을 그대로 쓴다)

S = ROOT / "courses" / "세컨브레인_특강" / "sessions" / "1주차"
TEMPLATE = ROOT / "kit" / "starter" / "presenter-notes-template.html"
DEFAULT_NOTES = [S / "1주차_발표노트_실습.md", S / "1주차_발표노트_개념.md"]
DEFAULT_DECK = S / "강의덱.html"
DEFAULT_OUT = S / "강의덱_발표자노트.html"

HEAD_RE = re.compile(r"^##\s+(\S+)\s*$")
EXTRA_CSS = """
  /* 노트 없는 장 — 본문 글자가 아니라 ::before로 보인다(발표본 메타의 「빈 메모」 계수를 지킨다) */
  .pn-item.pn-none{ border-left-color:var(--line); }
  .pn-item.pn-none::before{ content:"노트 없음"; font-size:14px; color:var(--gray-400); }
  .pn-md p{ white-space:pre-wrap; }
"""


def read_notes(paths: list[Path]):
    """{장 ID: [줄…]}, 건너뛴 파일, 중복 ID, 해석 못 한 `##` 줄을 돌려준다."""
    notes: dict[str, list[str]] = {}
    owner: dict[str, str] = {}
    dups: list[str] = []
    skipped: list[str] = []
    odd: list[str] = []
    for p in paths:
        if not p.is_file():
            skipped.append(p.name)
            continue
        cur = None
        for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if line.startswith("## "):
                m = HEAD_RE.match(line)
                if not m:
                    odd.append("%s:%d %s" % (p.name, n, line[:40]))
                    cur = None
                    continue
                cur = m.group(1)
                if cur in notes:
                    dups.append("%s (%s · %s)" % (cur, owner[cur], p.name))
                    cur = None
                    continue
                notes[cur] = []
                owner[cur] = p.name
            elif cur and line.strip():
                notes[cur].append(line.rstrip())
    return notes, skipped, dups, odd


def slide_title(inner: str) -> str:
    """inject_presenter.map_notes와 같은 규칙: 첫 h1~h3, <br>은 공백, 태그 제거, 공백 정규화."""
    m = re.search(r"<h[123]\b[^>]*>(.*?)</h[123]\s*>", inner, re.S | re.I)
    raw = re.sub(r"<br\s*/?>", " ", m.group(1)) if m else ""
    return ip.norm_ws(_html.unescape(re.sub(r"<[^>]+>", "", raw)))


def read_deck(deck: Path):
    html = deck.read_text(encoding="utf-8")
    _a, i0, i1, _n = ip.find_deck_range(html)
    slides = ip.scan_slides(html, i0, i1)
    tm = re.search(r"<title>(.*?)</title>", html, re.S | re.I)
    title = ip.norm_ws(_html.unescape(tm.group(1))) if tm else "세컨브레인 특강"
    return slides, title


def head_block(deck_title: str, week: str) -> str:
    """템플릿의 <head>(스타일 포함)와 .pn-head를 가져와 자리표시자를 채운다."""
    t = TEMPLATE.read_text(encoding="utf-8")
    cut = t.index('<div class="pn-wrap">')
    head = t[:cut]
    head = head.replace("{{강의명·주차}}", _html.escape("%s · %s" % (deck_title, week)))
    head = head.replace("</style>", EXTRA_CSS + "</style>", 1)
    return head


def build(slides, titles, notes, deck_title, week):
    out = [head_block(deck_title, week), '<div class="pn-wrap">\n\n']
    out.append(
        '  <header class="pn-head">\n'
        '    <div class="pn-kicker">발표자 노트 · %s</div>\n'
        '    <h1 class="pn-title">%s</h1>\n'
        '    <p class="pn-note">발표 중 보는 간결한 노트입니다. 발표본(강의덱_발표.html)의 발표자 화면에 들어가며, '
        '줄마다 마크다운 목록(<code>- </code>)과 굵게(<code>**</code>)로 적습니다.</p>\n'
        '  </header>\n\n' % (_html.escape(week), _html.escape(deck_title))
    )
    for i, s in enumerate(slides, 1):
        sid = s["slide_id"]
        title = titles[i - 1] or sid
        out.append('  <section class="pn-slide" data-slide="%s">\n' % _html.escape(sid, quote=True))
        out.append('    <div class="pn-slide-head">\n      <span class="pn-no">%d</span>\n'
                   '      <h2 class="pn-slide-title">%s</h2>\n    </div>\n' % (i, _html.escape(title)))
        lines = notes.get(sid)
        if lines:
            out.append('    <div class="pn-item pn-md">\n')
            for x in lines:
                out.append("      <p>%s</p>\n" % _html.escape(x, quote=False))
            out.append("    </div>\n")
        else:
            out.append('    <div class="pn-item pn-md pn-none"></div>\n')
        out.append("  </section>\n\n")
    out.append("</div>\n</body>\n</html>\n")
    return "".join(out)


def self_check(out_html: str, slides) -> tuple[bool, str]:
    """inject_presenter와 같은 파서·매핑으로 방금 쓴 HTML을 다시 읽는다."""
    try:
        entries = ip.parse_notes(out_html)
        by_slide, stat = ip.map_notes(slides, entries, ip.count_note_blocks(out_html))
    except ip.InjectError as exc:
        return False, "자기검증 실패 — %s" % str(exc).splitlines()[0]
    ok = stat["entries"] == len(slides) and stat["mapped"] == len(slides)
    filled = sum(1 for v in by_slide.values() if v)
    return ok, "자기검증(inject 파서·매핑) 매핑 %d/%d · 노트 항목이 있는 장 %d · 빈 항목 장 %d" % (
        stat["mapped"], stat["entries"], filled, len(by_slide) - filled)


def main(argv=None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--deck", type=Path, default=DEFAULT_DECK, help="조립본 강의덱.html")
    ap.add_argument("--notes", type=Path, nargs="+", default=DEFAULT_NOTES, help="노트 md(여러 개 가능 · 없는 파일은 건너뜀)")
    ap.add_argument("--output", type=Path, default=DEFAULT_OUT, help="강의덱_발표자노트.html")
    ap.add_argument("--week", default="1주차")
    ap.add_argument("--check", action="store_true", help="계수만 보고 파일을 쓰지 않는다")
    ap.add_argument("--strict", action="store_true", help="노트 없는 장·덱에 없는 노트가 있으면 exit 1")
    a = ap.parse_args(argv)

    if not a.deck.is_file():
        print("[FAIL] 조립본이 없다: %s" % a.deck)
        return 1
    try:
        slides, deck_title = read_deck(a.deck)
    except ip.InjectError as exc:
        print("[FAIL] 조립본을 해석하지 못했다: %s" % exc)
        return 1
    if not slides:
        print("[FAIL] 조립본에서 슬라이드를 하나도 찾지 못했다(미판정 — 통과 아님): %s" % a.deck)
        return 1
    ids = [s["slide_id"] for s in slides]
    if "" in ids or len(set(ids)) != len(ids):
        print("[FAIL] data-slide 누락 또는 중복이 있다 — 조립본부터 고쳐야 한다")
        return 1

    notes, skipped, dups, odd = read_notes([Path(p) for p in a.notes])
    for k in skipped:
        print("  건너뜀(파일 없음): %s" % k)
    if odd:
        print("[FAIL] 해석하지 못한 `##` 줄 %d개: %s" % (len(odd), " | ".join(odd[:5])))
        return 1
    if dups:
        print("[FAIL] 노트 ID 중복 %d개: %s" % (len(dups), ", ".join(dups)))
        return 1
    if not notes:
        print("[FAIL] 노트 md에서 `## <ID>` 블록을 하나도 읽지 못했다(미판정 — 통과 아님)")
        return 1

    have = [i for i in ids if notes.get(i)]
    none = [i for i in ids if not notes.get(i)]
    empty_blocks = [i for i in ids if i in notes and not notes[i]]   # `##`만 있고 줄이 없는 블록
    orphan = [i for i in notes if i not in set(ids)]
    lines = sum(len(notes[i]) for i in have)
    print("RESULT 장 %d · 노트 있음 %d · 없음 %d · 덱에 없는 노트 %d · 노트 줄 %d(장당 %.1f)%s" % (
        len(ids), len(have), len(none), len(orphan), lines, lines / max(1, len(have)), " · 쓰지 않음(--check)" if a.check else ""))
    if none:
        print("  노트 없는 장(%d): %s" % (len(none), ", ".join(none)))
    if empty_blocks:
        print("  `##`만 있고 줄이 없는 블록(없음으로 셈): %s" % ", ".join(empty_blocks))
    if orphan:
        print("  덱에 없는 노트(%d · 발표본에 들어가지 않음): %s" % (len(orphan), ", ".join(orphan)))

    titles = [slide_title(s["inner"]) for s in slides]
    headless = [s["slide_id"] for s, t in zip(slides, titles) if not t]
    if headless:
        print("  h1~h3 없는 장 %d(제목은 장 ID로 쓴다): %s" % (len(headless), ", ".join(headless)))

    out_html = build(slides, titles, notes, deck_title, a.week)
    ok, msg = self_check(out_html, slides)
    print("  " + msg)
    if not ok:
        return 1
    if not a.check:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        tmp = a.output.with_name(a.output.name + ".tmp")
        tmp.write_text(out_html, encoding="utf-8", newline="\n")
        os.replace(tmp, a.output)
        try:
            shown = str(a.output.resolve().relative_to(ROOT)).replace("\\", "/")
        except ValueError:
            shown = a.output
        print("  쓴 파일: %s (%dKB · pn-slide %d블록)" % (shown, len(out_html.encode("utf-8")) // 1024, out_html.count('class="pn-slide"')))
    if a.strict and (none or orphan):
        print("[FAIL] --strict: 노트 없는 장 %d · 덱에 없는 노트 %d" % (len(none), len(orphan)))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
