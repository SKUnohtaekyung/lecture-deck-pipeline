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
    violations = verify_file(args.deck, require_font=not args.no_require_font)
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
