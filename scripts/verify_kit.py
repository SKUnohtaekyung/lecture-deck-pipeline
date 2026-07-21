#!/usr/bin/env python3
"""킷 계약 검증 — 카탈로그 마크업과 kit CSS의 정합성.

왜 필요한가:
  카탈로그(`kit/layouts/catalog.html`·`kit/charts/catalog.html`)는 "해당 ID
  `<section>`을 통째로 복사해 붙이고 내용만 교체"하는 코드 코어다. 그런데
  마크업이 쓰는 클래스가 카탈로그 인라인 `<style>`에만 있으면, 복사한 덱에는
  CSS가 따라오지 않아 **뼈대만 붙는다**. 조립자는 어쩔 수 없이 로컬 `<style>`에
  같은 CSS를 다시 짜게 되고, 덱마다 미세하게 다른 노드 스타일이 누적된다.
  2026-07-19 감사에서 이런 고아 클래스가 31종 발견됐다.

무엇을 강제하는가:
  1. 카탈로그 마크업이 쓰는 모든 클래스는 kit CSS에 정의가 있어야 한다.
  2. 카탈로그에는 인라인 `<style>` 요소를 두지 않는다(정의는 patterns.css로).
  3. 스타터의 파트 전환은 가변 파트 수용 지오메트리 자동 생성기를 유지한다.

사용:
  python scripts/verify_kit.py
"""
from __future__ import annotations

import pathlib
import re
import sys

try:  # Windows cp949 콘솔 대응 (verify_deck.py와 동일 관례)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except AttributeError:  # pragma: no cover — 구버전 파이썬
    pass

ROOT = pathlib.Path(__file__).resolve().parent.parent

KIT_CSS = [
    "kit/styles/deck.css",
    "kit/styles/legibility.css",
    "kit/styles/patterns.css",
]
CATALOGS = [
    "kit/layouts/catalog.html",
    "kit/charts/catalog.html",
]
STARTER = "kit/starter/deck-template.html"

# 마크업에 나타나지만 CSS 정의를 요구하지 않는 클래스.
# 여기에 추가할 땐 반드시 이유를 적는다 — 이 목록이 조용히 자라면 게이트가 무의미해진다.
EXEMPT: set[str] = set()  # (현재 없음)

_fail = 0
_passed = 0


def chk(cond: bool, ok: str, bad: str) -> None:
    global _fail, _passed
    if cond:
        _passed += 1
        print(f"PASS | {ok}")
    else:
        _fail += 1
        print(f"FAIL | {bad}")


def css_class_selectors(text: str) -> set[str]:
    """CSS에서 정의된 클래스 이름을 뽑는다(선언 블록 밖 셀렉터의 .name).

    미지원 문법(이 저장소가 쓰지 않아 정규식을 넓히지 않음):
      `._X`(밑줄로 시작하는 클래스) · `.md\\:flex`(콜론 이스케이프) ·
      `[class~="X"]`(속성 셀렉터). 이런 문법이 새로 쓰이면 오탐 가능.
    """
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    out: set[str] = set()
    for m in re.finditer(r"([^{}]+)\{", text):
        for name in re.findall(r"\.([A-Za-z][\w-]*)", m.group(1)):
            out.add(name)
    return out


def split_html(text: str) -> tuple[str, str, str]:
    """(인라인 style 내용, script 내용, style/script/주석 제거된 마크업)"""
    styles = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", text, flags=re.S))
    scripts = "\n".join(re.findall(r"<script[^>]*>(.*?)</script>", text, flags=re.S))
    markup = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.S)
    markup = re.sub(r"<script[^>]*>.*?</script>", " ", markup, flags=re.S)
    markup = re.sub(r"<!--.*?-->", " ", markup, flags=re.S)
    return styles, scripts, markup


def markup_classes(markup: str) -> set[str]:
    """마크업의 class 속성값에서 클래스 이름을 뽑는다.

    대소문자 무시(`CLASS="값"`)와 따옴표 생략(`class=값`, HTML5에서 공백·
    따옴표·`<`·`>`·backtick이 없으면 유효)을 모두 대응한다.
    """
    out: set[str] = set()
    for m in re.finditer(r'class\s*=\s*"([^"]*)"', markup, flags=re.I):
        out.update(m.group(1).split())
    for m in re.finditer(r"class\s*=\s*'([^']*)'", markup, flags=re.I):
        out.update(m.group(1).split())
    for m in re.finditer(r'class\s*=\s*([^\s"\'=<>`]+)', markup, flags=re.I):
        out.update(m.group(1).split())
    return out


def script_classes(script_text: str) -> set[str]:
    """`<script>`의 `classList.add(...)`/`classList.toggle(...)`로 부여되는 클래스.

    `split_html()`이 마크업에서 `<script>`를 통째로 지우므로, 지우기 전에
    이 함수로 스크립트 텍스트에서 먼저 뽑아야 한다.
    """
    out: set[str] = set()
    for call in re.finditer(
        r"classList\s*\.\s*(?:add|toggle)\s*\(([^)]*)\)", script_text, flags=re.I
    ):
        args = call.group(1)
        for lit in re.finditer(r"""(['"])((?:(?!\1).)*)\1""", args):
            out.update(lit.group(2).split())
    return out


def main() -> int:
    missing_css = [p for p in KIT_CSS if not (ROOT / p).exists()]
    if missing_css:
        print(f"FAIL | kit CSS 파일 없음: {', '.join(missing_css)}")
        print("--- FAIL=1 PASS=0 ---")
        print("RESULT | FAIL | 킷 계약 검증")
        return 1

    defined: set[str] = set()
    for rel in KIT_CSS:
        defined |= css_class_selectors((ROOT / rel).read_text(encoding="utf-8"))
    print(f"INFO | kit CSS 정의 클래스 {len(defined)}종 "
          f"({', '.join(pathlib.Path(p).name for p in KIT_CSS)})")

    for rel in CATALOGS:
        path = ROOT / rel
        if not path.exists():
            chk(False, "", f"{rel} 없음")
            continue
        text = path.read_text(encoding="utf-8")
        styles, scripts, markup = split_html(text)
        used = markup_classes(markup) | script_classes(scripts)

        orphans = sorted(c for c in used if c not in defined and c not in EXEMPT)
        chk(
            not orphans,
            f"{rel} — 마크업 클래스 {len(used)}종 전부 kit CSS에 정의됨",
            f"{rel} — kit CSS에 정의 없는 클래스 {len(orphans)}종: {', '.join(orphans)}"
            f"\n       → 정의를 kit/styles/patterns.css로 옮겨라. 카탈로그를 복사한 덱에서 "
            f"뼈대만 붙는다.",
        )

        chk(
            not styles.strip(),
            f"{rel} — 인라인 <style> 없음",
            f"{rel} — 인라인 <style>이 있다({len(styles.split(chr(10)))}줄). "
            f"카탈로그 CSS는 patterns.css에 둔다 — 인라인은 복사한 쪽에 따라가지 않는다.",
        )

    starter_path = ROOT / STARTER
    if not starter_path.exists():
        chk(False, "", f"{STARTER} 없음")
    else:
        starter = starter_path.read_text(encoding="utf-8")
        dynamic_part_contract = all(
            marker in starter
            for marker in (
                "function partGeometry(n)",
                "function hydratePartDivider(s,index,total)",
                "data-geometry-count",
                "d<=total",
                "points=partGeometry(index)",
            )
        )
        chk(
            dynamic_part_contract,
            f"{STARTER} — 가변 파트 지오메트리 자동 생성 계약 유지",
            f"{STARTER} — partGeometry/hydratePartDivider 자동 생성 계약 누락",
        )

        empty_hooks = bool(
            re.search(r'<svg\s+class="dv-hero"[^>]*>\s*<!--.*?-->\s*</svg>', starter, flags=re.S)
        ) and bool(re.search(r'<div\s+class="pd-dots"[^>]*>\s*<!--.*?-->\s*</div>', starter, flags=re.S))
        chk(
            empty_hooks,
            f"{STARTER} — 파트 SVG·도트가 빈 자동생성 hook",
            f"{STARTER} — 파트 SVG·도트를 하드코딩하지 말고 빈 hook으로 둘 것",
        )

    print(f"--- FAIL={_fail} PASS={_passed} ---")
    verdict = "PASS" if _fail == 0 else "FAIL"
    print(f"RESULT | {verdict} | 킷 계약 검증(카탈로그 ↔ kit CSS)")
    return 0 if _fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
