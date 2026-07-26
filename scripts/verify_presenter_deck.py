#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_presenter_deck.py — 발표본 전용 검증기.

설계 정본: plans/presenter-system-final-plan.md §17.

핵심 원칙
  - **사이드카는 감사 기록이지 검증 정본이 아니다.** 원본과 발표본을 각각 직접 읽어 지문을
    다시 계산하고, ① 두 파일 사이의 불변성 ② 재계산값과 사이드카의 일치를 **모두** 본다.
    사이드카만 믿으면 순환 검증이 된다.
  - 출력은 **PASS/FAIL과 수치만**. 슬라이드 원문·base64를 절대 출력하지 않는다.
  - 각 파일은 한 번만 통째로 읽는다(파일당 1회 스트리밍).

사용:
  python scripts/verify_presenter_deck.py --source <원본.html> --presenter <발표본.html> --meta <사이드카.json>
종료코드: FAIL이 하나라도 있으면 1.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.inject_presenter import (   # noqa: E402  (지문 계산기를 그대로 재사용한다)
    InjectError,
    fingerprint,
    find_deck_range,
)

ALLOWED_PV_ROOTS = (".controls", ".presentation-menu", ".keyboard-help", ".presenter-")
PRINT_MUST_HIDE = (".controls", ".presentation-menu", ".keyboard-help",
                   ".presenter-console", "#blackout", "[data-presenter-preview]")


def _attr(tag_text: str, name: str) -> str | None:
    m = re.search(r"""\b%s\s*=\s*("([^"]*)"|'([^']*)'|([^\s>]+))""" % re.escape(name), tag_text, re.I)
    if not m:
        return None
    return m.group(2) or m.group(3) or m.group(4) or ""


def _style_blocks(html: str) -> str:
    return "\n".join(re.findall(r"<style\b[^>]*>(.*?)</style\s*>", html, re.S | re.I))


def _strip_css_comments(css: str) -> str:
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


def check_pv_tokens(css: str) -> tuple[list[str], dict]:
    """--pv-* 토큰이 라이트·다크 양쪽에 1:1로 정의되고, 스코프를 벗어나지 않는지 본다."""
    fails: list[str] = []
    css = _strip_css_comments(css)

    defined: dict[str, set[str]] = {}
    for theme, body in re.findall(r'\[data-pv-theme="(light|dark)"\][^{]*\{(.*?)\}', css, re.S):
        defined.setdefault(theme, set()).update(re.findall(r"(--pv-[A-Za-z0-9-]+)\s*:", body))
    light, dark = defined.get("light", set()), defined.get("dark", set())
    if not light or not dark:
        fails.append(f"--pv-* 테마 정의 누락 (라이트 {len(light)}개 · 다크 {len(dark)}개)")
    elif light != dark:
        only_l, only_d = sorted(light - dark), sorted(dark - light)
        fails.append(f"--pv-* 라이트/다크 불일치 — 라이트에만 {len(only_l)}개, 다크에만 {len(only_d)}개")

    leaks = []
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
        selector, body = m.group(1).strip(), m.group(2)
        if "--pv-" not in body or selector.startswith("@"):
            continue
        for one in (s.strip() for s in selector.split(",")):
            if one and not any(root in one for root in ALLOWED_PV_ROOTS):
                leaks.append(one)
    if leaks:
        fails.append(f"--pv-* 스코프 이탈 {len(leaks)}건 (허용: .controls · .presentation-menu · "
                     f".keyboard-help · .presenter-*)")
    return fails, {"light": len(light), "dark": len(dark), "leaks": len(leaks)}


def check_print_rules(css: str) -> list[str]:
    fails = []
    blocks = re.findall(r"@media\s+print\s*\{(.*?)\n\}", _strip_css_comments(css), re.S)
    joined = "\n".join(blocks)
    if not joined:
        return ["@media print 블록이 없습니다"]
    missing = [sel for sel in PRINT_MUST_HIDE if sel not in joined]
    if missing:
        fails.append(f"인쇄 제외 규칙 누락: {missing}")
    if "break-after: page" not in joined and "break-after:page" not in joined:
        fails.append("인쇄 블록에 `break-after: page`(1장=1페이지)가 없습니다")
    if "break-after: auto" not in joined and "break-after:auto" not in joined:
        fails.append("마지막 장 `break-after: auto`(빈 페이지 방지)가 없습니다")
    return fails


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # pragma: no cover
        pass

    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", required=True, help="주입 전 원본 단일 HTML")
    ap.add_argument("--presenter", required=True, help="주입된 발표본 HTML")
    ap.add_argument("--meta", required=True, help="사이드카 JSON")
    a = ap.parse_args()

    results: list[tuple[str, str]] = []

    def chk(ok: bool, good: str, bad: str) -> None:
        results.append(("PASS", good) if ok else ("FAIL", bad))

    try:
        src_html = Path(a.source).read_text(encoding="utf-8")
        pv_html = Path(a.presenter).read_text(encoding="utf-8")
        meta = json.loads(Path(a.meta).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[FAIL] 입력을 읽지 못했습니다: {exc}")
        return 1

    # ── 지문 재계산 (사이드카를 믿지 않는다) ──
    try:
        _s, si0, si1, _n = find_deck_range(src_html)
        _p, pi0, pi1, _m = find_deck_range(pv_html)
        before = fingerprint(src_html, si0, si1)
        after = fingerprint(pv_html, pi0, pi1)
    except InjectError as exc:
        print(f"[FAIL] 덱 구조를 해석하지 못했습니다: {exc}")
        return 1

    # ① 외부 참조 0건
    non_data = [u for u in re.findall(r"""\b(?:src|href)\s*=\s*["']([^"']+)["']""", pv_html)
                if not u.startswith(("data:", "#"))]
    chk(not non_data, "외부 src/href(비-data) 0건",
        f"외부 참조 {len(non_data)}건 — 단일 파일 자립성 위반")

    # ② <html> 마커 3속성 + 버전 형식
    html_tag = re.search(r"<html\b[^>]*>", pv_html, re.I)
    html_tag_text = html_tag.group(0) if html_tag else ""
    version = _attr(html_tag_text, "data-presenter-runtime")
    deck_id = _attr(html_tag_text, "data-deck-id")
    build_hash = _attr(html_tag_text, "data-build-hash")
    chk(bool(version and deck_id and build_hash),
        f"<html> 마커 3속성 존재 (deckId={deck_id})",
        "<html>에 data-presenter-runtime·data-deck-id·data-build-hash 중 누락이 있습니다")
    chk(bool(version and re.fullmatch(r"\d+\.\d+\.\d+", version)),
        f"runtimeVersion 형식 유효 ({version})", f"runtimeVersion 형식 오류: {version!r}")

    # ③ 주입 노드 개수 · ⑥ .deck 밖 위치
    node_counts = {}
    for pat, label in ((r"<style\b[^>]*\bdata-presenter-runtime\b", "style"),
                       (r"<script\b[^>]*\bdata-presenter-runtime\b", "script"),
                       (r"<script\b[^>]*\bdata-presenter-notes\b", "notes")):
        spots = [m.start() for m in re.finditer(pat, pv_html, re.I)]
        node_counts[label] = len(spots)
        chk(len(spots) == 1, f"주입 노드 `{label}` 정확히 1개",
            f"주입 노드 `{label}`가 {len(spots)}개 — 중복 주입 의심")
        inside = [s for s in spots if pi0 <= s < pi1]
        chk(not inside, f"주입 노드 `{label}` 가 .deck 밖에 있음",
            f"주입 노드 `{label}`가 .deck 범위 안에 있습니다")

    # ④⑤ 슬라이드 불변성 (원본 ↔ 발표본)
    chk(before["slide_count"] == after["slide_count"],
        f"슬라이드 수 동일 ({after['slide_count']}장)",
        f"슬라이드 수 불일치 — 원본 {before['slide_count']} vs 발표본 {after['slide_count']}")
    chk(before["slide_ids"] == after["slide_ids"], "slideId 시퀀스 동일",
        "slideId 시퀀스가 원본과 다릅니다")
    chk(before["inner_hashes"] == after["inner_hashes"], "슬라이드별 innerHTML 해시 동일",
        f"innerHTML이 바뀐 슬라이드 "
        f"{sum(1 for x, y in zip(before['inner_hashes'], after['inner_hashes']) if x != y)}장")
    chk(before["start_tags"] == after["start_tags"], ".slide 시작 태그 원문 동일",
        f"시작 태그가 바뀐 슬라이드 "
        f"{sum(1 for x, y in zip(before['start_tags'], after['start_tags']) if x != y)}장")
    chk(before["img_count"] == after["img_count"] and before["img_srcs"] == after["img_srcs"],
        f"<img> 개수·src 해시 동일 ({after['img_count']}개)",
        "<img> 개수 또는 src가 원본과 다릅니다")

    # ⑦ 노트 JSON
    block = re.search(r'<script type="application/json" data-presenter-notes>(.*?)</script>', pv_html, re.S)
    note_count = -1
    if not block:
        chk(False, "", "노트 JSON 블록을 찾지 못했습니다")
    else:
        try:
            payload = json.loads(block.group(1))
            notes = payload.get("notes") or {}
            note_count = len(notes)
            chk(True, f"노트 JSON 파싱 성공 ({note_count}개 슬라이드)", "")
            unknown = [k for k in notes if k not in after["slide_ids"]]
            chk(not unknown, "노트 키가 모두 실재 slideId",
                f"실재하지 않는 slideId 키 {len(unknown)}건")
        except json.JSONDecodeError as exc:
            chk(False, "", f"노트 JSON 파싱 실패: {exc}")

    # ⑧⑨ 발표 UI CSS
    css = _style_blocks(pv_html)
    token_fails, token_stats = check_pv_tokens(css)
    chk(not token_fails,
        f"--pv-* 토큰 라이트/다크 1:1 ({token_stats['light']}개) · 스코프 이탈 0",
        " · ".join(token_fails))
    print_fails = check_print_rules(css)
    chk(not print_fails, "인쇄 정책(발표 UI 제외 + 1장=1페이지) 존재", " · ".join(print_fails))

    # ⑩ 재계산 지문 ↔ 사이드카 일치 (불일치 자체가 FAIL)
    mismatches = []
    if meta.get("deckId") != deck_id:
        mismatches.append("deckId")
    if meta.get("runtimeVersion") != version:
        mismatches.append("runtimeVersion")
    if meta.get("buildHash") != before["build_hash"] or build_hash != before["build_hash"]:
        mismatches.append("buildHash")
    if meta.get("slideCount") != after["slide_count"]:
        mismatches.append("slideCount")
    if meta.get("slideIds") != after["slide_ids"]:
        mismatches.append("slideIds")
    if meta.get("imgCount") != after["img_count"]:
        mismatches.append("imgCount")
    expected_hashes = dict(zip(after["slide_ids"], after["inner_hashes"]))
    if meta.get("slideHashes") != expected_hashes:
        mismatches.append("slideHashes")
    if note_count >= 0 and (meta.get("notes") or {}).get("mapped") != note_count:
        mismatches.append("notes.mapped")
    chk(not mismatches, "재계산 지문 ↔ 사이드카 일치",
        f"사이드카 불일치 {len(mismatches)}건: {mismatches} — 사이드카는 감사 기록이므로 "
        "재계산값과 다르면 그 자체가 실패입니다")

    for w in meta.get("warnings") or []:
        results.append(("WARN", w))

    for level, msg in sorted(results, key=lambda r: {"FAIL": 0, "WARN": 1, "PASS": 2}[r[0]]):
        print(f"[{level}] {'✗' if level == 'FAIL' else ('△' if level == 'WARN' else '✓')} {msg}")
    fails = sum(1 for lvl, _ in results if lvl == "FAIL")
    warns = sum(1 for lvl, _ in results if lvl == "WARN")
    print(f"\n요약: FAIL {fails} · WARN {warns} · PASS {len(results) - fails - warns}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
