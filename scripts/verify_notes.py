#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_notes.py — 강의덱과 발표자노트 페이지 정합성 검증.

발표자노트 HTML(`N주차_발표자노트.html`)의 각 항목은 `pn-no`(페이지 번호)와
`pn-slide-title`(슬라이드 제목)로 특정 덱 슬라이드를 가리킨다. 이 스크립트는
- 노트가 가리키는 페이지 번호가 실제로 덱에 존재/표시되는 번호인지
- 노트 항목들이 페이지 번호 순서대로(단조 증가) 나열됐는지
- 노트가 적은 제목이 해당 페이지의 실제 슬라이드 제목과 앞부분이 일치하는지
를 대조한다.

페이지 번호 규칙은 하드코딩하지 않고 **대상 덱 자신의 인라인 JS**에서 직접
추출한다. 덱마다 규칙이 다를 수 있다는 것이 실측으로 확인됐다:
  - sessions/1주차/강의덱.html          : cover|concept-recap|closing|no-page-number
  - sessions/_template/강의덱.초안/shell.html : cover|concept-recap|closing (no-page-number 없음)
근거 줄(sessions/1주차/강의덱.html):
  if(!/\\b(cover|concept-recap|closing|no-page-number)\\b/.test(s.className)){
    var pg=document.createElement('div');pg.className='s-pageno';
    pg.textContent=(i+1)+' / '+slides.length;s.appendChild(pg);
  }
슬라이드 배열은 `document.querySelectorAll('.slide')`(문서 순서) 그대로이고,
표시되는 페이지 번호는 그 배열에서의 1-기반 인덱스(i+1)다 — 제외 클래스에
해당하는 슬라이드도 배열 안에서 자리를 차지하지만 번호를 화면에 붙이지 않을
뿐이다(그래서 노트의 표시 번호는 그 인덱스와 정확히 대응한다).

사용:
  python scripts/verify_notes.py <덱.html> <노트.html>
    [--snapshot <경로>] [--baseline <경로>]
종료코드: 불일치(기존 3종 검사 또는 --baseline 회귀) 있으면 1, 없으면 0.

--snapshot/--baseline (멘트 유실 회귀 검사, 2026-08-03 신설)
  기존 3종 검사(부분집합·단조증가·제목전방일치)는 "노트가 가리키는 슬라이드가
  실재하는가"만 본다. 노트 블록 안 실제 멘트(`pn-item`) 개수는 보지 않으므로,
  머지 등으로 멘트 텍스트만 사라져도 통과해 버린다(2026-08-03 실사고: 3-way
  머지로 멘트 4건이 조용히 유실된 채 커밋·푸시됨). 이를 잡기 위해:
    --snapshot <경로> : 현재 노트의 슬라이드별 pn-item 개수 + 총계를 JSON으로 기록.
                        슬라이드 식별자는 (pn-no, 제목) 조합.
    --baseline <경로> : 이전 스냅샷과 대조. 어떤 슬라이드의 pn-item 개수가
                        줄었거나 슬라이드 자체가 사라졌으면 FAIL. 늘어난 것은 통과.
  두 옵션은 각각 독립적으로 켤 수 있고(같이 줘도 됨), 기존 3종 검사의 판정·
  출력·종료코드는 건드리지 않는다 — 순수 추가다.
"""
import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

VOID_ELEMENTS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
    "param", "source", "track", "wbr",
}
HEADING_TAGS = {"h1", "h2", "h3"}

# 노트 블록(`pn-slide`)·항목(`pn-item`) 범위를 찾는 태그 스캐너.
# `inject_presenter.iter_class_blocks`와 동일한 방식(범위 스캔)을 그대로 옮겨 쓴다 —
# 상태 기반 HTMLParser 서브클래스로 깊이를 세면 `<br>` 같은 void 요소에서 깊이가
# 어긋나 항목이 닫히지 않는다(실측: 67개 중 33개만 잡히고 뒤쪽 26블록이 통째로
# 0개가 됐다). verify_notes는 inject_presenter에서 import되는 쪽이라(역방향
# import는 순환) 이 유틸을 별도로 복제해 둔다.
_TAG_RE = re.compile(r"<(/?)([a-zA-Z][\w-]*)((?:[^>\"']|\"[^\"]*\"|'[^']*')*)>", re.S)


def _classes_of(attr_text):
    m = re.search(r"""\bclass\s*=\s*("([^"]*)"|'([^']*)'|([^\s>]+))""", attr_text, re.I)
    if not m:
        return set()
    return set((m.group(2) or m.group(3) or m.group(4) or "").split())


def iter_class_blocks(html, token, start=0, end=None):
    """class에 `token`을 가진 요소의 (시작, 내용시작, 내용끝)을 문서 순서로 돌려준다."""
    end = len(html) if end is None else end
    pos = start
    while True:
        m = _TAG_RE.search(html, pos)
        if not m or m.start() >= end:
            return
        closing, name, attrs = m.group(1), m.group(2).lower(), m.group(3)
        if closing or name in VOID_ELEMENTS or token not in _classes_of(attrs):
            pos = m.end()
            continue
        depth = 1
        inner_end = None
        for n in _TAG_RE.finditer(html, m.end()):
            if n.group(2).lower() != name or n.group(2).lower() in VOID_ELEMENTS:
                continue
            if n.group(3).rstrip().endswith("/"):
                continue
            depth += -1 if n.group(1) else 1
            if depth == 0:
                inner_end = n.start()
                break
        if inner_end is None or inner_end > end:
            return
        yield m.start(), m.end(), inner_end
        pos = inner_end


def count_items_per_slide(notes_html):
    """`pn-slide` 블록별 `pn-item` 개수를 문서 순서 리스트로 돌려준다."""
    counts = []
    for _s, inner_start, inner_end in iter_class_blocks(notes_html, "pn-slide"):
        n = sum(1 for _ in iter_class_blocks(notes_html, "pn-item", inner_start, inner_end))
        counts.append(n)
    return counts


def build_snapshot(entries, item_counts):
    """(pn-no, 제목) 조합을 슬라이드 식별자로 삼아 항목 수 스냅샷을 만든다.

    `entries`는 NotesParser가 문서 순서로 뽑은 (raw_no, title) 목록이고, `item_counts`는
    같은 문서 순서로 뽑은 `pn-slide` 블록별 pn-item 개수다. 두 스캔 모두 같은 문서를
    순서대로 훑으므로 위치가 대응한다(inject_presenter.parse_notes와 동일한 전제)."""
    slides = []
    for i, (raw_no, title) in enumerate(entries):
        n = item_counts[i] if i < len(item_counts) else 0
        slides.append({"pn_no": raw_no, "title": title, "items": n})
    return {"slides": slides, "total_items": sum(s["items"] for s in slides)}

# 덱 JS 안에서 s-pageno 생성을 가드하는 조건의 제외 클래스 알터네이션을 직접 뽑는다.
# if(!/\b(A|B|C)\b/.test(s.className)){ ... s-pageno ... } 형태(공백 유무 무관).
PAGENO_GUARD_RE = re.compile(
    r"if\s*\(\s*!\s*/\\b\(([^)]+)\)\\b/\.test\(s\.className\)\s*\)\s*\{[^}]*s-pageno",
    re.DOTALL,
)


def norm_ws(s):
    return re.sub(r"\s+", " ", s).strip()


# 노트 제목의 파트 표지 접두어(`PART 3 · ` 등)와 중점 구분자는 노트 쪽 표기 규약이라
# 덱 제목에는 없다. 비교 전에만 걷어내고, 화면 출력에는 원문을 그대로 쓴다.
NOTE_PART_PREFIX_RE = re.compile(r"^PART\s*\d+\s*[·:\-]\s*")


def norm_title(s):
    """제목 비교용 정규화: 파트 접두어 제거 → 중점 구분자 제거 → 공백 축약.

    `<br>`은 각 파서가 이미 공백으로 치환해 넣는다(덱은 줄바꿈으로 시각적 분리를
    하지만 노트는 ` · `로 잇는 경우가 있어, 구분자를 지워야 같은 제목으로 맞는다).
    """
    s = NOTE_PART_PREFIX_RE.sub("", s)
    s = s.replace("·", " ")
    # 공백을 전부 지운다. 덱 제목은 영문/국문 두 줄을 <br> 없이 별도 span으로 쌓기도
    # 하고(`Prompt Engineering` + `프롬프트 엔지니어링`), 노트는 같은 제목을 ` · `로
    # 잇는다. 줄바꿈·구분자 표기 차이로 오탐이 나지 않게 공백 자체를 비교에서 뺀다.
    return re.sub(r"\s+", "", s)


def front_match(a, b):
    """전방(앞부분) 일치: 둘 중 짧은 쪽 길이만큼 앞부분이 같은가."""
    n = min(len(a), len(b))
    if n == 0:
        return a == b
    return a[:n] == b[:n]


class SlideParser(HTMLParser):
    """`.slide` 클래스 요소를 문서 순서로 수집하고, 각 슬라이드의 첫 h1/h2/h3
    textContent(공백 정규화, JS의 text.replace(/\\s+/g,' ').trim()과 동일)를
    제목으로 추출한다. 슬라이드 판정은 CSS 클래스 셀렉터와 동일하게 공백분해
    토큰 정확 일치(`slide` 자체가 토큰이어야 함 — `s02-slide` 는 별개 토큰이라
    미해당), 페이지번호 제외판정은 JS와 동일하게 원문 class 속성 문자열에 대한
    \\b 정규식 테스트로 한다(용도가 다르므로 방식도 다르게 재현)."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.slides = []  # [{"classes_raw":str, "classes_set":set, "data_slide":str, "title":str|None}]
        self._open_stack = []  # [(tag, slide_ref|None)]
        self._heading_stack = []  # [None | {"buf":[str], "slide":dict}]

    def _current_slide(self):
        for _, ref in reversed(self._open_stack):
            if ref is not None:
                return ref
        return None

    def handle_starttag(self, tag, attrs_list):
        self._open(tag, attrs_list, self_closing=(tag in VOID_ELEMENTS))

    def handle_startendtag(self, tag, attrs_list):
        self._open(tag, attrs_list, self_closing=True)

    def _open(self, tag, attrs_list, self_closing):
        attrs = {}
        for k, v in attrs_list:
            if k:
                attrs[k.lower()] = v if v is not None else ""
        classes_raw = attrs.get("class") or ""
        classes_set = set(classes_raw.split())
        slide_ref = None
        if "slide" in classes_set:
            slide_ref = {
                "classes_raw": classes_raw,
                "classes_set": classes_set,
                "data_slide": attrs.get("data-slide", ""),
                "title": None,
            }
            self.slides.append(slide_ref)
        if not self_closing:
            self._open_stack.append((tag, slide_ref))
        if tag == "br" and self._heading_stack and self._heading_stack[-1] is not None:
            # 덱 제목은 <br>로 줄을 나눈다. 공백을 넣지 않으면 앞뒤 어절이 붙어
            # ('페이지를만들고') 노트와 오탐 불일치가 난다.
            self._heading_stack[-1]["buf"].append(" ")
        if tag in HEADING_TAGS:
            enclosing = self._current_slide()
            if enclosing is not None and enclosing["title"] is None:
                self._heading_stack.append({"buf": [], "slide": enclosing})
            else:
                self._heading_stack.append(None)

    def handle_endtag(self, tag):
        if tag in HEADING_TAGS and self._heading_stack:
            entry = self._heading_stack.pop()
            if entry is not None and entry["slide"]["title"] is None:
                entry["slide"]["title"] = norm_ws("".join(entry["buf"]))
        for i in range(len(self._open_stack) - 1, -1, -1):
            if self._open_stack[i][0] == tag:
                del self._open_stack[i:]
                break

    def handle_data(self, data):
        if self._heading_stack and self._heading_stack[-1] is not None:
            self._heading_stack[-1]["buf"].append(data)


class NotesParser(HTMLParser):
    """발표자노트의 `div.pn-slide-head` 안 `span.pn-no`(번호)와
    `h2.pn-slide-title`(제목)을 문서 순서 쌍으로 수집한다."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.entries = []  # [(raw_no:str, title:str)]
        self._active = False
        self._cur_no = None
        self._capturing_no = False
        self._capturing_title = False
        self._no_buf = []
        self._title_buf = []

    def handle_starttag(self, tag, attrs_list):
        attrs = {}
        for k, v in attrs_list:
            if k:
                attrs[k.lower()] = v if v is not None else ""
        classes = set((attrs.get("class") or "").split())
        if tag == "div" and "pn-slide-head" in classes:
            self._active = True
            self._cur_no = None
        elif self._active and tag == "span" and "pn-no" in classes:
            self._capturing_no = True
            self._no_buf = []
        elif self._active and tag == "h2" and "pn-slide-title" in classes:
            self._capturing_title = True
            self._title_buf = []
        elif tag == "br" and self._capturing_title:
            self._title_buf.append(" ")

    def handle_endtag(self, tag):
        if tag == "span" and self._capturing_no:
            self._cur_no = norm_ws("".join(self._no_buf))
            self._capturing_no = False
        elif tag == "h2" and self._capturing_title:
            title = norm_ws("".join(self._title_buf))
            self._capturing_title = False
            if self._active and self._cur_no is not None:
                self.entries.append((self._cur_no, title))
            self._active = False

    def handle_data(self, data):
        if self._capturing_no:
            self._no_buf.append(data)
        elif self._capturing_title:
            self._title_buf.append(data)


def main():
    try:  # Windows 콘솔(cp949) 깨짐/크래시 방지
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

    ap = argparse.ArgumentParser()
    ap.add_argument("deck", help="강의덱.html 경로")
    ap.add_argument("notes", help="강의덱_발표자노트.html 경로")
    ap.add_argument("--snapshot", help="현재 노트의 슬라이드별 pn-item 개수 + 총계를 JSON으로 기록할 경로")
    ap.add_argument("--baseline", help="이전 --snapshot 결과와 대조해 멘트 총량 회귀(감소·소실)를 검사할 경로")
    args = ap.parse_args()

    deck_path = Path(args.deck)
    notes_path = Path(args.notes)

    try:
        deck_html = deck_path.read_text(encoding="utf-8")
    except OSError as e:
        print(f"FAIL: 덱 파일을 읽을 수 없음: {deck_path} ({e})")
        sys.exit(1)
    try:
        notes_html = notes_path.read_text(encoding="utf-8")
    except OSError as e:
        print(f"FAIL: 노트 파일을 읽을 수 없음: {notes_path} ({e})")
        sys.exit(1)

    print(f"=== verify_notes ===")
    print(f"deck : {deck_path}")
    print(f"notes: {notes_path}")

    guard_m = PAGENO_GUARD_RE.search(deck_html)
    if not guard_m:
        print("FAIL: 덱 JS에서 s-pageno 생성 가드 조건(if(!/\\b(...)\\b/.test(s.className)){...s-pageno...})을 "
              "찾지 못했다 — 페이지 번호 규칙을 추측하지 않고 중단한다.")
        sys.exit(1)
    exclude_alt = guard_m.group(1)
    exclude_re = re.compile(r"\b(" + exclude_alt + r")\b")
    print(f"pageno 제외 클래스(덱 JS에서 직접 추출): {exclude_alt}")

    slide_parser = SlideParser()
    slide_parser.feed(deck_html)
    slide_parser.close()
    slides = slide_parser.slides

    if not slides:
        print("FAIL: 덱에서 .slide 요소를 하나도 찾지 못했다.")
        sys.exit(1)

    # 표시 페이지 번호 -> (슬라이드 인덱스, 제목). i(0-based)+1이 화면 번호.
    # 제외 클래스 슬라이드도 배열 안 자리를 차지하지만 화면에 번호를 안 붙일 뿐이므로
    # "화면에 실제 표시되는 번호 집합"과 "번호->제목 전체 매핑"을 분리해 둔다.
    deck_title_by_no = {}
    deck_visible_nos = set()
    for i, sl in enumerate(slides):
        no = i + 1
        deck_title_by_no[no] = sl["title"] if sl["title"] is not None else ""
        if not exclude_re.search(sl["classes_raw"]):
            deck_visible_nos.add(no)

    print(f"deck slides: {len(slides)}개 (표시 페이지번호 {len(deck_visible_nos)}개)")

    notes_parser = NotesParser()
    notes_parser.feed(notes_html)
    notes_parser.close()
    entries = notes_parser.entries
    print(f"notes entries: {len(entries)}개")

    # ── 0판정 가드(2026-08-24) ──────────────────────────────────────────
    # entries는 pn-slide-head/pn-no/pn-slide-title 클래스명에 의존해 모은다.
    # 그 클래스명이 통째로 바뀌면 entries가 조용히 빈 리스트가 되고, 아래
    # 계산은 전부 0/0으로 맞아떨어져 "불일치 없음"과 구분되지 않는 가짜 PASS를
    # 낸다(2026-08-24 실측). <h2> 태그는 pn-slide-title과 무관하게 남는(태그
    # 이름 자체는 클래스명이 아니다) 독립 신호이고, 실측으로도 거의 1:1 대응한다
    # (1주차 51 vs entries 52 · 2주차 112 vs 113 · 3주차 78 vs 79 — 각각 -1은
    # 문서 자체의 대표 제목 h2 하나). entries가 0인데 <h2>는 있다면 "노트가
    # 원래 비어 있다"가 아니라 "구조를 못 읽었다"로 본다 — run_deck_checks.py의
    # "계수 실패(눈먼 0 방지)"와 같은 사고방식(AGENTS.md 참조).
    h2_count = len(re.findall(r"<h2\b", notes_html, re.I))
    unjudged = (not entries) and h2_count > 0
    if unjudged:
        print(f"UNJUDGED | pn-slide-head/pn-no/pn-slide-title 항목이 0개인데 노트 문서 안에 "
              f"<h2> 태그가 {h2_count}개 있다 — 슬라이드 제목으로 보이는 내용이 있는데도 "
              f"하나도 못 찾았다는 뜻이다. pn-* 클래스명이 바뀌었는지 확인하라(가짜 PASS 방지).")
    print()

    mismatches = []
    ok = 0

    # ① 부분집합 검사 + ③ 제목 전방일치 검사 (번호가 파싱 가능한 것만)
    parsed_entries = []
    for raw_no, title in entries:
        try:
            no = int(raw_no)
        except ValueError:
            mismatches.append(f"[번호형식] pn-no='{raw_no}' 이(가) 정수가 아님 (제목: {title!r})")
            continue
        parsed_entries.append((no, raw_no, title))

    for no, raw_no, title in parsed_entries:
        if no not in deck_visible_nos:
            if no in deck_title_by_no:
                mismatches.append(
                    f"[부분집합] 노트 pn-no={raw_no} — 덱에 존재하는 슬라이드지만 "
                    f"page-number 제외 클래스라 화면에 번호가 표시되지 않음 "
                    f"(슬라이드 제목: {deck_title_by_no[no]!r})"
                )
            else:
                mismatches.append(
                    f"[부분집합] 노트 pn-no={raw_no} — 덱 슬라이드 배열 범위 밖(전체 {len(slides)}개)"
                )
            continue
        ok += 1
        deck_title = deck_title_by_no.get(no, "")
        if not front_match(norm_title(title), norm_title(deck_title)):
            mismatches.append(
                f"[제목전방일치] pn-no={raw_no} — 노트 제목 {title!r} vs 덱 제목 {deck_title!r}"
            )

    # ② 단조 증가 검사 (정수로 파싱된 것만, 원래 등장 순서 그대로)
    prev = None
    prev_raw = None
    for no, raw_no, title in parsed_entries:
        if prev is not None and no <= prev:
            mismatches.append(
                f"[단조증가] pn-no={raw_no} 이(가) 이전 pn-no={prev_raw} 이후에 증가하지 않음"
            )
        prev, prev_raw = no, raw_no

    for m in mismatches:
        print(f"MISMATCH | {m}")

    print()

    # (1) 항목(pn-item) 0개 블록 리포트 — WARN 전용, 판정(mismatches/종료코드)에는 영향 없음.
    # 블록은 있으나 멘트가 하나도 없는 슬라이드를 잡는다(emptySlides는 "블록 자체가
    # 매핑 안 된 슬라이드"만 세서 이 경우를 놓친다 — inject_presenter.py map_notes 참고).
    item_counts = count_items_per_slide(notes_html)
    snapshot = build_snapshot(entries, item_counts)
    zero_blocks = [s for s in snapshot["slides"] if s["items"] == 0]
    if zero_blocks:
        print(f"WARN | 항목(pn-item) 0개인 슬라이드 {len(zero_blocks)}개:")
        for s in zero_blocks:
            print(f"  WARN | pn-no={s['pn_no']} — {s['title']!r}")
    else:
        print("WARN | 항목(pn-item) 0개인 슬라이드: 없음")
    print()

    # (2) --snapshot: 현재 노트의 슬라이드별 pn-item 개수 + 총계를 JSON으로 기록.
    if args.snapshot:
        snap_path = Path(args.snapshot)
        try:
            snap_path.write_text(
                json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        except OSError as e:
            print(f"FAIL: 스냅샷을 쓸 수 없음: {snap_path} ({e})")
            sys.exit(1)
        print(
            f"SNAPSHOT | 저장: {snap_path} "
            f"(슬라이드 {len(snapshot['slides'])}개 · 항목 총 {snapshot['total_items']}개)"
        )
        print()

    # (2) --baseline: 이전 스냅샷과 대조해 멘트 총량 회귀(감소·소실)를 검사.
    # 슬라이드 식별자는 (pn-no, 제목) 조합 — 늘어난 것은 통과, 줄었거나 슬라이드
    # 자체가 사라졌으면 FAIL.
    regression_fails = []
    if args.baseline:
        baseline_path = Path(args.baseline)
        try:
            baseline_raw = baseline_path.read_text(encoding="utf-8")
        except OSError as e:
            print(f"FAIL: 베이스라인 스냅샷을 읽을 수 없음: {baseline_path} ({e})")
            sys.exit(1)
        try:
            baseline_data = json.loads(baseline_raw)
        except json.JSONDecodeError as e:
            print(f"FAIL: 베이스라인 스냅샷 JSON 파싱 실패: {baseline_path} ({e})")
            sys.exit(1)

        current_by_key = {(s["pn_no"], s["title"]): s["items"] for s in snapshot["slides"]}
        for b in baseline_data.get("slides", []):
            key = (b.get("pn_no"), b.get("title"))
            prev_n = b.get("items", 0)
            if key not in current_by_key:
                regression_fails.append(
                    f"[슬라이드소실] pn-no={b.get('pn_no')} — {b.get('title')!r} "
                    f"(이전 항목 {prev_n}개) — 현재 노트에 이 슬라이드가 없음"
                )
                continue
            cur_n = current_by_key[key]
            if cur_n < prev_n:
                regression_fails.append(
                    f"[항목감소] pn-no={b.get('pn_no')} — {b.get('title')!r} — "
                    f"이전 {prev_n}개 → 현재 {cur_n}개"
                )

        for r in regression_fails:
            print(f"REGRESSION | {r}")
        print()
        print(
            f"--- REGRESSION={len(regression_fails)} "
            f"(baseline={baseline_path}, baseline 항목 총 {baseline_data.get('total_items', '?')}개 "
            f"→ 현재 항목 총 {snapshot['total_items']}개) ---"
        )
        print()

    print(f"--- MISMATCH={len(mismatches)} OK={ok}/{len(parsed_entries)} ---")
    print(f"판정 {len(parsed_entries)}건 · 미판정 {h2_count if unjudged else 0}건")
    total_fail = len(mismatches) + len(regression_fails)
    if unjudged:
        result = "FAIL(미판정 — entries 0건인데 노트에 <h2> 있음. pn-* 클래스명을 확인하라)"
    elif total_fail:
        result = "FAIL(불일치 있음)"
    else:
        result = "PASS(불일치 없음)"
    print(f"RESULT | {result}")
    sys.exit(1 if (total_fail or unjudged) else 0)


if __name__ == "__main__":
    main()
