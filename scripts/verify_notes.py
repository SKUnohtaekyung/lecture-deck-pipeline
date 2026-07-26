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
종료코드: 불일치 있으면 1, 없으면 0.
"""
import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

VOID_ELEMENTS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
    "param", "source", "track", "wbr",
}
HEADING_TAGS = {"h1", "h2", "h3"}

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
    print(f"--- MISMATCH={len(mismatches)} OK={ok}/{len(parsed_entries)} ---")
    result = "FAIL(불일치 있음)" if mismatches else "PASS(불일치 없음)"
    print(f"RESULT | {result}")
    sys.exit(1 if mismatches else 0)


if __name__ == "__main__":
    main()
