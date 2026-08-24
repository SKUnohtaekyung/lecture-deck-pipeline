#!/usr/bin/env python3
"""Independently verify that a built deck is a self-contained, offline-openable file.

This is the standalone enforcement gate for the "최종본" (distributable). It inspects
a finished HTML artifact without rebuilding it, so it can guard files produced earlier
or by other tools. ``scripts/inline_deck.py`` fails closed at build time; this asserts
the same contract on the artifact for CI, evals, and manual checks.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # pragma: no cover
    pass

REMOTE = re.compile(r"^(?:https?:)?//", re.I)
_TAGS = r"(?:link|script|img|source|video|audio|iframe|embed|track)"


def _attr(tag: str, name: str) -> str:
    match = re.search(rf"\b{re.escape(name)}\s*=\s*(['\"])(.*?)\1", tag, re.I | re.S)
    return match.group(2) if match else ""


def self_containment_violations(html: str, *, require_font: bool = True) -> list[str]:
    """Return a list of reasons ``html`` is not a self-contained offline bundle."""
    violations: list[str] = []

    # 1) No fetchable external reference of any kind.
    for tag in re.findall(rf"<{_TAGS}\b[^>]*>", html, re.I):
        for attribute in ("href", "src", "poster"):
            value = _attr(tag, attribute)
            if value and REMOTE.match(value):
                violations.append(f"external {attribute}: {value[:80]}")
        srcset = _attr(tag, "srcset")
        for candidate in srcset.split(","):
            token = candidate.strip().split(None, 1)[0] if candidate.strip() else ""
            if token and REMOTE.match(token):
                violations.append(f"external srcset: {token[:80]}")

    if re.search(r"@import\s+(?:url\(\s*)?['\"]?\s*(?:https?:)?//", html, re.I):
        violations.append("remote @import in CSS")
    for url in re.findall(r"url\(\s*['\"]?([^)'\"]+)", html, re.I):
        if REMOTE.match(url.strip()):
            violations.append(f"external url(): {url.strip()[:80]}")

    # 2) Every media reference must already be inlined (data:) or an in-page anchor.
    for tag in re.findall(r"<(?:img|source|video|audio)\b[^>]*>", html, re.I):
        for attribute in ("src", "poster"):
            value = _attr(tag, attribute)
            if value and not value.startswith(("data:", "#")):
                violations.append(f"non-data {attribute}: {value[:60]}")

    # 3) Font self-containment: no Pretendard CDN link, and an embedded woff2 face.
    if re.search(r"href\s*=\s*['\"][^'\"]*pretendard", html, re.I):
        violations.append("external Pretendard font link present")
    if require_font:
        has_face = re.search(r"@font-face", html, re.I) and re.search(
            r"url\(\s*['\"]?data:font/woff2", html, re.I
        )
        if not has_face:
            violations.append("no embedded @font-face (data:font/woff2)")

    # 4) Inherit the image contract: no unresolved explanatory/mnemonic slot ships.
    for match in re.finditer(r"<figure\b([^>]*)>(.*?)</figure>", html, re.I | re.S):
        attributes, body = match.group(1), match.group(2)
        if "asset-slot" not in _attr(attributes, "class"):
            continue
        purpose = _attr(attributes, "data-image-purpose")
        state = _attr(attributes, "data-image-state")
        if purpose in {"explanatory", "mnemonic"} and (
            state == "expected" or not re.search(r"<img\b", body, re.I)
        ):
            violations.append(f"unresolved required {purpose} image slot")
        if state == "expected" and re.search(r"<img\b[^>]*\bsrc=", body, re.I):
            violations.append("expected image slot contains an img src")

    return violations


def unresolved_scan_gaps(html: str) -> list[str]:
    """0판정 가드(신설·진단 전용) — ``self_containment_violations``의 판정에는 관여하지
    않는다. 위 위반 스캔의 4번 항목은 ``class`` 속성에 ``asset-slot``이 있는 ``<figure>``만
    본다. 그 클래스명이 바뀌면 그 figure는 조용히 스캔 대상에서 빠져, 실제로는 미해결
    슬롯이 있어도 위반 0건(=PASS)으로 보인다(미탐).

    「정말 계약과 무관한 장식용 figure」와 「계약 참여 의도가 있는데 클래스명만 어긋난
    figure」를 자동으로 확실히 가를 수는 없다 — 그래서 위반으로 단정하지 않고, 이미지
    계약의 속성 어휘(``data-image-purpose``/``data-image-state``)가 붙어 있는데도
    ``asset-slot`` 클래스가 없는 figure만 진단으로 표면화한다. 그 속성이 붙어 있다는
    것 자체가 "이 figure는 이미지 슬롯 계약에 참여할 의도였다"는 신호이기 때문이다.
    """
    gaps: list[str] = []
    for match in re.finditer(rf"<figure\b([^>]*)>(.*?)</figure>", html, re.I | re.S):
        attributes = match.group(1)
        cls = _attr(attributes, "class")
        if "asset-slot" in cls:
            continue
        purpose = _attr(attributes, "data-image-purpose")
        state = _attr(attributes, "data-image-state")
        if purpose or state:
            gaps.append(
                f'class="{cls}"에 asset-slot 없음 — data-image-purpose={purpose or "(없음)"} '
                f'data-image-state={state or "(없음)"}는 있어 계약 참여 의도로 보이나 스캔에서 빠짐'
            )
    return gaps


def figure_scan_summary(html: str) -> tuple[int, int]:
    """(판정, 미판정) figure 수 — "판정 N건 · 미판정 M건" 출력용.

    판정 = ``asset-slot`` 클래스로 실제 위반 스캔에 들어간 figure 수.
    미판정 = :func:`unresolved_scan_gaps`가 표면화한, 스캔에서 빠진 figure 수.
    둘 다 아닌 figure(클래스도 없고 이미지계약 속성 신호도 없는 순수 장식용)는 애초에
    이 계약과 무관하므로 어느 쪽에도 세지 않는다.
    """
    judged = 0
    for match in re.finditer(r"<figure\b([^>]*)>", html, re.I):
        if "asset-slot" in _attr(match.group(1), "class"):
            judged += 1
    unjudged = len(unresolved_scan_gaps(html))
    return judged, unjudged


def verify_file(path: Path, *, require_font: bool = True) -> list[str]:
    if not path.is_file():
        return [f"file is missing: {path}"]
    try:
        html = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return [f"cannot read file: {exc}"]
    return self_containment_violations(html, require_font=require_font)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("deck", type=Path, help="built distributable HTML")
    parser.add_argument("--no-require-font", action="store_true", help="skip the embedded @font-face requirement")
    args = parser.parse_args()

    if not args.deck.is_file():
        violations = [f"file is missing: {args.deck}"]
        html = None
    else:
        try:
            html = args.deck.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            violations = [f"cannot read file: {exc}"]
            html = None
        else:
            violations = self_containment_violations(html, require_font=not args.no_require_font)

    if html is not None:
        # 0판정 가드(신설·진단 전용, 위반 판정에는 관여하지 않는다) — unresolved_scan_gaps 참고.
        judged, unjudged = figure_scan_summary(html)
        gaps = unresolved_scan_gaps(html)
        print(f"0판정가드 | 판정 {judged}건 · 미판정 {unjudged}건")
        for gap in gaps[:20]:
            print(f"[WARN] 0판정가드: {gap}")
        if len(gaps) > 20:
            print(f"[WARN] 0판정가드: 외 {len(gaps) - 20}건 생략")

    if violations:
        for violation in violations:
            print(f"[FAIL] {violation}")
        print(f"[FAIL] {args.deck} is not a self-contained distributable ({len(violations)} issue(s))")
        return 1
    size_kb = args.deck.stat().st_size // 1024
    print(f"[PASS] {args.deck} is self-contained ({size_kb}KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
