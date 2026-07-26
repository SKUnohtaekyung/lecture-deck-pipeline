#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""inject_presenter.py — 완성된 단일 HTML 덱에 발표 런타임을 주입한다.

설계 정본: plans/presenter-system-final-plan.md §15(멱등·불변·atomic) · §11(노트) · §14.2(게이트).

핵심 원칙
  - 입력은 **이미 완성된 단일 HTML**이다. 조각에서 재생성하지 않으므로 동결된 주차와 충돌하지 않는다.
  - HTML을 파서로 재직렬화하지 않는다. 시작 태그를 정규식으로 스캔해 **원문 바이트를 보존하고
    삽입만** 한다. `.deck` 범위는 문자열 치환 대상에서 원천 제외한다.
  - 주입 전후 지문을 전부 대조해 하나라도 어긋나면 **파일을 쓰지 않는다**(fail-closed).
  - 일반 조립 경로(build_release.py·inline_deck.py)에는 발표자 코드 경로가 존재하지 않는다.
    "자동 삽입 없음"이 플래그 기본값이 아니라 **구조로** 보장된다.

사용:
  python scripts/inject_presenter.py <입력.html> --notes <노트.html> --deck-id <id> \
      --output <발표본.html> --meta <사이드카.json> [--force]
종료코드: 0 성공 / 1 실패(그 경우 출력물은 만들어지지 않는다).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from html import unescape as _html_unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.assemble_deck import _write_atomic          # noqa: E402  (원자적 쓰기 재사용)
from scripts.verify_notes import (                        # noqa: E402  (노트 파서 재사용 — 새 파서를 만들지 않는다)
    NotesParser,
    SlideParser,
    front_match,
    norm_title,
    norm_ws,
)

RUNTIME_VERSION = "1.0.0"
RUNTIME_JS = ROOT / "kit" / "runtime" / "presenter-runtime.js"
RUNTIME_CSS = ROOT / "kit" / "runtime" / "presenter-ui.css"

TAG_RE = re.compile(r"<(/?)([a-zA-Z][\w-]*)((?:[^>\"']|\"[^\"]*\"|'[^']*')*)>", re.S)
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr"}
NOTE_KINDS = {"pn-joke": "joke", "pn-demo": "demo", "pn-hint": "hint"}


class InjectError(Exception):
    """게이트 실패 — 호출부는 파일을 쓰지 않고 종료코드 1로 끝낸다."""


# ──────────────────────────────────────────────────────────────────────────
# HTML 범위 스캔 (재직렬화 없음)
# ──────────────────────────────────────────────────────────────────────────
def _classes(attr_text: str) -> set[str]:
    m = re.search(r"""\bclass\s*=\s*("([^"]*)"|'([^']*)'|([^\s>]+))""", attr_text, re.I)
    if not m:
        return set()
    return set((m.group(2) or m.group(3) or m.group(4) or "").split())


def find_deck_range(html: str) -> tuple[int, int, int, str]:
    """`.deck` 요소의 (시작태그 시작, 내용 시작, 내용 끝, 태그명)을 돌려준다."""
    for m in TAG_RE.finditer(html):
        closing, name, attrs = m.group(1), m.group(2).lower(), m.group(3)
        if closing or name in VOID:
            continue
        if "deck" not in _classes(attrs):
            continue
        depth = 1
        for n in TAG_RE.finditer(html, m.end()):
            n_closing, n_name, n_attrs = n.group(1), n.group(2).lower(), n.group(3)
            if n_name != name or n_name in VOID or n_attrs.rstrip().endswith("/"):
                continue
            depth += -1 if n_closing else 1
            if depth == 0:
                return m.start(), m.end(), n.start(), name
        raise InjectError("`.deck` 요소의 닫는 태그를 찾지 못했습니다.")
    raise InjectError("`.deck` 요소를 찾지 못했습니다 — 덱 HTML이 맞는지 확인하세요.")


def scan_slides(html: str, inner_start: int, inner_end: int) -> list[dict]:
    """`.deck` 직계 `<section class="slide ...">`을 문서 순서로 수집한다.

    시작 태그 **원문**과 innerHTML 범위를 그대로 들고 있어, 주입 후 한 글자도 바뀌지 않았음을
    바이트 단위로 재확인할 수 있게 한다."""
    slides: list[dict] = []
    pos = inner_start
    while True:
        m = TAG_RE.search(html, pos)
        if not m or m.start() >= inner_end:
            break
        closing, name, attrs = m.group(1), m.group(2).lower(), m.group(3)
        if closing or name != "section" or "slide" not in _classes(attrs):
            pos = m.end()
            continue
        depth = 1
        end_start = None
        for n in TAG_RE.finditer(html, m.end()):
            if n.group(2).lower() != "section":
                continue
            depth += -1 if n.group(1) else 1
            if depth == 0:
                end_start = n.start()
                break
        if end_start is None:
            raise InjectError(f"슬라이드 {len(slides) + 1}번의 닫는 태그를 찾지 못했습니다.")
        sid = re.search(r"""\bdata-slide\s*=\s*("([^"]*)"|'([^']*)'|([^\s>]+))""", attrs, re.I)
        slides.append({
            "order": len(slides),
            "start_tag": html[m.start():m.end()],
            "inner": html[m.end():end_start],
            "slide_id": (sid.group(2) or sid.group(3) or sid.group(4) or "").strip() if sid else "",
        })
        pos = end_start
    return slides


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def fingerprint(html: str, inner_start: int, inner_end: int) -> dict:
    """주입 전후로 완전히 같아야 하는 값들."""
    slides = scan_slides(html, inner_start, inner_end)
    deck_body = html[inner_start:inner_end]
    imgs = re.findall(r"<img\b((?:[^>\"']|\"[^\"]*\"|'[^']*')*)>", deck_body, re.I)
    srcs = []
    for attrs in imgs:
        m = re.search(r"""\bsrc\s*=\s*("([^"]*)"|'([^']*)'|([^\s>]+))""", attrs, re.I)
        srcs.append(sha(m.group(2) or m.group(3) or m.group(4) or "") if m else "")
    return {
        "slide_count": len(slides),
        "slide_ids": [s["slide_id"] for s in slides],
        "start_tags": [sha(s["start_tag"]) for s in slides],
        "inner_hashes": [sha(s["inner"]) for s in slides],
        "img_count": len(imgs),
        "img_srcs": srcs,
        "build_hash": sha("\n".join(s["slide_id"] + "\x00" + s["inner"] for s in slides)),
        "_slides": slides,
    }


# ──────────────────────────────────────────────────────────────────────────
# 노트 파싱·매핑 (§11) — verify_notes의 파서를 확장해 재사용한다
# ──────────────────────────────────────────────────────────────────────────
def iter_class_blocks(html: str, token: str, start: int = 0, end: int | None = None):
    """class에 `token`을 가진 요소의 (시작, 내용시작, 내용끝)을 문서 순서로 돌려준다.

    상태 기반 파서 대신 **범위 스캔**을 쓴다. HTMLParser 서브클래스로 깊이를 세면
    `<br>` 같은 void 요소에서 깊이가 어긋나 항목이 닫히지 않는다(실측: 1주차 노트에서
    67개 중 33개만 잡히고 뒤쪽 26블록이 통째로 0개로 나왔다)."""
    end = len(html) if end is None else end
    pos = start
    while True:
        m = TAG_RE.search(html, pos)
        if not m or m.start() >= end:
            return
        closing, name, attrs = m.group(1), m.group(2).lower(), m.group(3)
        if closing or name in VOID or token not in _classes(attrs):
            pos = m.end()
            continue
        depth = 1
        inner_end = None
        for n in TAG_RE.finditer(html, m.end()):
            if n.group(2).lower() != name or n.group(2).lower() in VOID:
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


def _text_of(html_fragment: str) -> str:
    """태그를 걷어낸 텍스트. `<br>`은 공백으로 바꾼다(제목·본문 모두 같은 규칙)."""
    frag = re.sub(r"<br\s*/?>", " ", html_fragment, flags=re.I)
    frag = re.sub(r"<[^>]+>", "", frag)
    return norm_ws(_html_unescape(frag))


def parse_notes(notes_html: str) -> list[dict]:
    """노트 블록을 (번호, 제목, [{kind, text}])로 읽는다.

    번호·제목은 verify_notes.NotesParser가 이미 검증된 규칙을 갖고 있어 그대로 쓰고,
    항목 본문만 범위 스캔으로 뽑는다. 라벨(`.lbl` — 이모지 포함)은 저장하지 않는다:
    kind 코드만 남기고 표시 문구는 런타임 상수가 붙인다(§11.3)."""
    p = NotesParser()
    p.feed(notes_html)
    p.close()

    per_block: list[list[dict]] = []
    for _s, inner_start, inner_end in iter_class_blocks(notes_html, "pn-slide"):
        items = []
        for i_s, i_inner_start, i_inner_end in iter_class_blocks(
            notes_html, "pn-item", inner_start, inner_end
        ):
            kind = next((NOTE_KINDS[c] for c in _classes(TAG_RE.match(notes_html, i_s).group(3))
                         if c in NOTE_KINDS), None)
            if kind is None:
                continue
            body = notes_html[i_inner_start:i_inner_end]
            # 라벨은 표시 문구라 저장하지 않는다.
            for l_s, _li, _le in iter_class_blocks(body, "lbl"):
                lm = TAG_RE.match(body, l_s)
                if lm:
                    depth = 1
                    for n in TAG_RE.finditer(body, lm.end()):
                        if n.group(2).lower() != lm.group(2).lower():
                            continue
                        depth += -1 if n.group(1) else 1
                        if depth == 0:
                            body = body[:l_s] + body[n.end():]
                            break
                break
            text = _text_of(body)
            if text:
                items.append({"kind": kind, "text": text})
        per_block.append(items)

    return [
        {"raw_no": raw_no, "title": title,
         "items": per_block[i] if i < len(per_block) else []}
        for i, (raw_no, title) in enumerate(p.entries)
    ]


def count_note_blocks(notes_html: str) -> int:
    """노트 파일의 슬라이드 블록 수를 **파서와 독립적으로** 센다.

    파싱 결과끼리 비교하면(entries vs mapped) 파서가 통째로 실패했을 때 0 == 0 으로
    통과해 버린다. §11.2의 소진 어서션이 잡으려는 사고가 정확히 그것이므로 원문에서 센다."""
    return len(re.findall(r'class\s*=\s*"[^"]*\bpn-slide-head\b', notes_html))


def map_notes(slides: list[dict], entries: list[dict], expected: int) -> tuple[dict, dict]:
    """`pn-no - 1`을 인덱스로 매핑하고 제목 전방일치를 재확인한다(§11.1).

    하드 실패(정수 아님·범위 밖·제목 불일치·중복 매핑)는 자동 추정 없이 **중단**한다."""
    titles = [norm_ws(re.sub(r"<[^>]+>", " ", s["inner"])) for s in slides]
    heads = []
    for s in slides:
        m = re.search(r"<h[123]\b[^>]*>(.*?)</h[123]\s*>", s["inner"], re.S | re.I)
        raw = re.sub(r"<br\s*/?>", " ", m.group(1)) if m else ""
        heads.append(norm_ws(re.sub(r"<[^>]+>", "", raw)))

    by_slide: dict[str, list[dict]] = {}
    hard: list[str] = []
    mapped = 0

    for e in entries:
        try:
            no = int(e["raw_no"])
        except (TypeError, ValueError):
            hard.append(f"pn-no={e['raw_no']!r} 가 정수가 아님 (제목 {e['title']!r})")
            continue
        idx = no - 1
        if idx < 0 or idx >= len(slides):
            hard.append(f"pn-no={no} 가 슬라이드 범위(1~{len(slides)}) 밖 (제목 {e['title']!r})")
            continue
        deck_title = heads[idx]
        # 덱 슬라이드에 heading이 아예 없으면 대조할 대상이 없다(1주차 S3ASK·S3DO처럼
        # 큰 문장 하나만 있는 전환 슬라이드). 이때만 제목 검사를 건너뛰고 위치로 확정한다.
        # 제목이 있는데 다르면 여전히 하드 실패다 — 게이트를 넓히지 않는다.
        if deck_title and not front_match(norm_title(e["title"]), norm_title(deck_title)):
            hard.append(
                f"pn-no={no} 제목 전방일치 실패 — 노트 {e['title']!r} vs 덱 {deck_title!r} "
                f"(slideId={slides[idx]['slide_id']!r})"
            )
            continue
        sid = slides[idx]["slide_id"]
        if sid in by_slide:
            hard.append(f"slideId={sid!r} 에 2건 이상 매핑됨 (pn-no={no})")
            continue
        by_slide[sid] = e["items"]
        mapped += 1

    if hard:
        raise InjectError(
            "노트 매핑 하드 실패 %d건 — 자동 추정 매핑을 하지 않고 중단합니다.\n  - %s"
            % (len(hard), "\n  - ".join(hard))
        )
    if mapped != expected:
        raise InjectError(
            f"노트 소진 어서션 실패 — 노트 파일의 슬라이드 블록 {expected}개 중 {mapped}개만 "
            f"매핑됐습니다(파싱된 항목 {len(entries)}개). 노트 파싱이 통째로 실패한 사고를 "
            "잡기 위한 게이트입니다."
        )

    empty = [s["slide_id"] for s in slides if s["slide_id"] not in by_slide]
    return by_slide, {"entries": expected, "mapped": mapped, "empty_slides": empty}


def notes_json_block(deck_id: str, by_slide: dict) -> str:
    """`</script>`·`<!--`로 인한 조기 종료를 막기 위해 <, >, & 를 유니코드 이스케이프한다(§11.3)."""
    payload = json.dumps(
        {"version": 1, "deckId": deck_id, "notes": by_slide},
        ensure_ascii=False, separators=(",", ":"),
    )
    payload = payload.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return '<script type="application/json" data-presenter-notes>' + payload + "</script>"


# ──────────────────────────────────────────────────────────────────────────
# 주입
# ──────────────────────────────────────────────────────────────────────────
def inject(html: str, *, deck_id: str, notes_html: str | None, source_name: str) -> tuple[str, dict]:
    if re.search(r"<html\b[^>]*\bdata-presenter-runtime\b", html, re.I):
        raise InjectError("이미 발표 런타임이 주입된 파일입니다(멱등 게이트) — 원본 배포본을 입력하세요.")

    tag_start, inner_start, inner_end, _name = find_deck_range(html)
    before = fingerprint(html, inner_start, inner_end)
    slides = before["_slides"]
    if not slides:
        raise InjectError("`.deck` 안에서 슬라이드를 하나도 찾지 못했습니다.")

    # slideId 게이트 (§10.2) — 누락·중복이면 자동 부여 없이 중단한다.
    missing = [s["order"] + 1 for s in slides if not s["slide_id"]]
    seen: dict[str, int] = {}
    dups = []
    for s in slides:
        if s["slide_id"] and s["slide_id"] in seen:
            dups.append(f"{s['slide_id']!r}(#{seen[s['slide_id']] + 1}, #{s['order'] + 1})")
        elif s["slide_id"]:
            seen[s["slide_id"]] = s["order"]
    if missing or dups:
        raise InjectError(
            "slideId 게이트 실패 — data-slide 누락 %d장(위치 %s) · 중복 %s. 자동 부여하지 않습니다."
            % (len(missing), missing[:10], dups[:10] or "없음")
        )

    warnings: list[str] = []
    deck_body = html[inner_start:inner_end]
    for risky in ("iframe", "video", "audio", "canvas"):
        n = len(re.findall(r"<%s\b" % risky, deck_body, re.I))
        if n:
            warnings.append(f"`.deck` 안에 <{risky}> {n}개 — 미리보기 복제 시 동작을 확인하세요(§9.6).")

    # 노트 (§11)
    by_slide: dict = {}
    note_stats = {"entries": 0, "mapped": 0, "empty_slides": [s["slide_id"] for s in slides]}
    if notes_html is not None:
        entries = parse_notes(notes_html)
        by_slide, note_stats = map_notes(slides, entries, count_note_blocks(notes_html))

    css = RUNTIME_CSS.read_text(encoding="utf-8")
    js = RUNTIME_JS.read_text(encoding="utf-8")

    style_block = "<style data-presenter-runtime>\n%s\n</style>\n" % css
    script_block = (
        "%s\n<script data-presenter-runtime>\n%s\nwindow.PresenterRuntime.boot(%s);\n</script>\n"
        % (notes_json_block(deck_id, by_slide), js, json.dumps({"deckId": deck_id}, ensure_ascii=False))
    )

    # ── 삽입: `.deck` 범위는 치환 대상에서 원천 제외한다 ──
    head_close = html.rfind("</head>", 0, inner_start)
    if head_close < 0:
        raise InjectError("`</head>`를 `.deck` 앞에서 찾지 못했습니다.")
    body_close = html.rfind("</body>")
    if body_close < inner_end:
        raise InjectError("`</body>`를 `.deck` 뒤에서 찾지 못했습니다.")

    html_tag = re.search(r"<html\b((?:[^>\"']|\"[^\"]*\"|'[^']*')*)>", html, re.I)
    if not html_tag or html_tag.end() > head_close:
        raise InjectError("`<html>` 시작 태그를 찾지 못했습니다.")

    marker_attrs = (
        ' data-presenter-runtime="%s" data-deck-id="%s" data-build-hash="%s" data-pv-theme="light"'
        % (RUNTIME_VERSION, deck_id, before["build_hash"])
    )

    out = (
        html[:html_tag.end() - 1] + marker_attrs + html[html_tag.end() - 1:head_close]
        + style_block + html[head_close:body_close] + script_block + html[body_close:]
    )

    # ── 주입 후 지문 재산출 → 전량 대조 ──
    n_start, n_inner_start, n_inner_end, _n = find_deck_range(out)
    after = fingerprint(out, n_inner_start, n_inner_end)
    for key in ("slide_count", "slide_ids", "start_tags", "inner_hashes", "img_count", "img_srcs", "build_hash"):
        if before[key] != after[key]:
            raise InjectError(
                f"불변 검증 실패 — `{key}`가 주입 전후로 달라졌습니다. 파일을 쓰지 않고 중단합니다."
            )

    # 주입 노드는 `.deck` 밖에만 있어야 한다.
    for pat, label in ((r"<style\b[^>]*\bdata-presenter-runtime\b", "style"),
                       (r"<script\b[^>]*\bdata-presenter-runtime\b", "script"),
                       (r"<script\b[^>]*\bdata-presenter-notes\b", "notes")):
        spots = [m.start() for m in re.finditer(pat, out, re.I)]
        if len(spots) != 1:
            raise InjectError(f"주입 노드 `{label}`가 {len(spots)}개입니다(정확히 1개여야 함).")
        if n_inner_start <= spots[0] < n_inner_end:
            raise InjectError(f"주입 노드 `{label}`가 `.deck` 범위 안에 있습니다.")

    # 노트 JSON 블록 재파싱 + 항목 수 확인
    block = re.search(r'<script type="application/json" data-presenter-notes>(.*?)</script>', out, re.S)
    if not block:
        raise InjectError("노트 JSON 블록을 다시 찾지 못했습니다.")
    try:
        reparsed = json.loads(block.group(1))
    except json.JSONDecodeError as exc:
        raise InjectError(f"노트 JSON 블록 재파싱 실패: {exc}") from exc
    if len(reparsed.get("notes") or {}) != len(by_slide):
        raise InjectError("노트 JSON 항목 수가 매핑 결과와 다릅니다.")
    for sid in (reparsed.get("notes") or {}):
        if sid not in before["slide_ids"]:
            raise InjectError(f"노트 키 {sid!r}가 실재하지 않는 slideId입니다.")

    meta = {
        "deckId": deck_id,
        "runtimeVersion": RUNTIME_VERSION,
        "buildHash": before["build_hash"],
        "generatedFrom": source_name,
        "slideCount": before["slide_count"],
        "slideIds": before["slide_ids"],
        "slideHashes": dict(zip(before["slide_ids"], before["inner_hashes"])),
        "imgCount": before["img_count"],
        "notes": {
            "entries": note_stats["entries"],
            "mapped": note_stats["mapped"],
            "emptySlides": note_stats["empty_slides"],
        },
        "injectedNodes": ["html@data-presenter-runtime", "style@data-presenter-runtime",
                          "script@data-presenter-notes", "script@data-presenter-runtime"],
        "warnings": warnings,
    }
    return out, meta


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # pragma: no cover
        pass

    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("deck", help="입력 단일 HTML(완성된 배포본)")
    ap.add_argument("--notes", help="발표자 노트 HTML(생략하면 기본 멘트 없이 주입)")
    ap.add_argument("--deck-id", required=True, help="영구 deckId (예: vibecoding-week-1)")
    ap.add_argument("--output", required=True, help="발표본 출력 경로")
    ap.add_argument("--meta", required=True, help="사이드카 JSON 경로")
    ap.add_argument("--force", action="store_true", help="기존 출력물 덮어쓰기 허용")
    a = ap.parse_args()

    src = Path(a.deck)
    out_path = Path(a.output)
    meta_path = Path(a.meta)

    try:
        if not src.is_file():
            raise InjectError(f"입력 파일이 없습니다: {src}")
        if out_path.resolve() == src.resolve():
            raise InjectError("출력 경로가 입력과 같습니다 — 원본 덮어쓰기는 금지입니다.")
        if out_path.exists() and not a.force:
            raise InjectError(f"출력 경로에 파일이 이미 있습니다(--force 없이는 덮어쓰지 않습니다): {out_path}")

        html = src.read_text(encoding="utf-8")
        notes_html = Path(a.notes).read_text(encoding="utf-8") if a.notes else None
        result, meta = inject(html, deck_id=a.deck_id, notes_html=notes_html, source_name=src.name)
    except InjectError as exc:
        print(f"[FAIL] {exc}")
        return 1

    _write_atomic(out_path, result)
    _write_atomic(meta_path, json.dumps(meta, ensure_ascii=False, indent=2) + "\n")

    print(f"[PASS] 주입 완료: {out_path} ({out_path.stat().st_size // 1024}KB)")
    print(f"       슬라이드 {meta['slideCount']}장 · 불변 지문 일치 · buildHash {meta['buildHash'][:12]}…")
    print(f"       노트 {meta['notes']['mapped']}/{meta['notes']['entries']} 매핑 · "
          f"빈 메모 {len(meta['notes']['emptySlides'])}장")
    for w in meta["warnings"]:
        print(f"       [WARN] {w}")
    print(f"       사이드카: {meta_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
