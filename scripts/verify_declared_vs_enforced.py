#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""선언과 집행 불일치 검출 — 유형⑤ 기계화

무엇을 잡나
----------
**규칙 문서가 선언한 값**과 **kit CSS의 실효값**이 다른 상태를 잡는다.
문서만 읽으면 「됐다」로 보이는데 코드가 안 따라와 있는 경우다.

이 저장소가 반복해서 겪은 유형이다:
  · R-TYPE-02d가 `--sp-18`을 「카드·박스 사이 여백」으로 등재했는데
    `deck.css`의 `.grid-2`·`.grid-3`는 여전히 `gap:14px`
  · R-TYPE-01이 박스 제목을 「26px/800」으로 못박았는데
    `deck.css`의 `.work-step b`는 여전히 `font-size:18px`
  · `--fs-N` 9종이 참조 0건으로 죽어 있던 것이 이 전체 작업의 출발점이었다
실효값은 각 주차 shell 오버라이드에만 있어, **kit을 직접 쓰거나 다른 과목에
배포하면 원상복귀**한다. 그 상태를 잡는 것이 이 검사의 목적이다.

설계 — verify_deck.py의 known_violations 관례를 그대로 쓴다
----------------------------------------------------------
  · 이미 아는 불일치는 **사유와 함께 등재**하고 통과시킨다
  · **등재되지 않은 새 불일치만 FAIL** 한다
  → 「지금 상태를 고정」하면서 「앞으로의 재발을 막는다」

⚠️ 오탐을 막기 위한 3가지
------------------------
1. **레이어 순서를 안다.** deck.css(base) → legibility.css(가독성) → patterns.css
   순으로 로드되고 **실효값은 캐스케이드가 정한다**(명시도 → 순서).
   예: `.s-title`은 base 40px인데 legibility가 38px로 덮고 정본도 38px다 —
   이건 **의도된 계층**이지 불일치가 아니다.
2. **의도된 차이와 미배선을 가른다.** 판정 기준은 하나: **정본표가 말하는 값이
   어느 레이어에서든 실현되는가.** 40→38은 실현됐고, 26 vs 18은 실현되지 않았다.
3. **주차 shell 오버라이드는 집행부로 치지 않는다.** 그게 문제의 핵심이다.

⚠️ **파싱이 깨졌는데 「불일치 0」이 나오는 것을 막는다.** 파싱 건수를 함께
   출력하고, 0이면 **실패**시킨다. 조용한 0은 이 작업이 없애려는 「눈먼 0」이다.

사용:
    python scripts/verify_declared_vs_enforced.py
    python scripts/verify_declared_vs_enforced.py --list   # 전수 목록(등재분 포함)

종료코드: 0 통과 · 1 등재되지 않은 불일치 발견 · 2 파싱 실패(입력 이상)
"""
from __future__ import annotations

import argparse
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

CHEATSHEET = os.path.join(ROOT, "kit", "guide", "토큰-치트시트.md")
# ⚠️ 로드 순서 그대로. 덱 shell의 <link> 순서와 같아야 한다.
KIT_CSS = ["deck.css", "legibility.css", "patterns.css"]


# ══════════════════════════════════════════════════════════════════════
# CSS 파싱 · 캐스케이드 해석
# ══════════════════════════════════════════════════════════════════════
def strip_comments(css: str) -> str:
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


def parse_rules(css: str, origin: str, start_order: int = 0):
    """(selector, {prop: value}, origin, order) 목록. @media 블록 내부도 편다.

    ⚠️ `start_order`로 **파일을 가로지르는 전역 순서**를 유지한다. 파일마다 0에서
       다시 세면 캐스케이드가 깨진다 — 실측 사고: legibility.css의 `.s-body`
       22px가 deck.css의 19px에 져서 「본문이 19px」이라는 오탐이 났다.
       로드 순서(deck → legibility → patterns)가 곧 우선순위다.
    """
    css = strip_comments(css)
    rules = []
    order = start_order
    # @media / @supports 의 여는 중괄호를 지워 내부 규칙을 평평하게 만든다.
    # (kit에는 미디어쿼리별 분기 설계가 없으므로 평탄화가 안전하다)
    css = re.sub(r"@(?:media|supports)[^{]*\{", "", css)
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
        sel_group, body = m.group(1).strip(), m.group(2)
        if not sel_group or sel_group.startswith("@"):
            continue
        decls = {}
        for d in body.split(";"):
            if ":" not in d:
                continue
            k, _, v = d.partition(":")
            decls[k.strip().lower()] = v.strip()
        if not decls:
            continue
        for sel in sel_group.split(","):
            sel = " ".join(sel.split())
            if not sel:
                continue
            order += 1
            rules.append((sel, decls, origin, order))
    return rules, order


_COMBINATOR = re.compile(r"\s*[>+~]\s*|\s+")


def tokens_of(selector: str):
    """셀렉터를 결합자 기준 토큰 목록으로. `>`·`+`·`~`는 모두 「조상/형제 조건」으로 본다."""
    return [t for t in _COMBINATOR.split(selector.strip()) if t]


def specificity(selector: str):
    """(id, class/attr/pseudo-class, element/pseudo-element). 근사치지만 kit 범위에선 충분하다."""
    s = selector
    a = len(re.findall(r"#[\w-]+", s))
    b = len(re.findall(r"\.[\w-]+", s)) + len(re.findall(r"\[[^\]]+\]", s))
    b += len(re.findall(r"(?<!:):(?!:)[a-z-]+", s))
    c = len(re.findall(r"(?:^|[\s>+~(])([a-z][\w-]*)", s))
    c += len(re.findall(r"::[a-z-]+", s))
    return (a, b, c)


def rule_applies(rule_sel: str, target_tokens: list[str]) -> bool:
    """rule이 target 요소에 **직접** 적용되는가.

    판정: rule의 토큰 목록이 target 토큰 목록의 **부분수열이면서 마지막이 일치**.
    · `.work-step b`  ↔ target ['.work-step','b']            → 적용
    · `.eval-steps .work-step b` ↔ 같은 target                → 미적용(조상 조건 추가)
    · `.s-body`      ↔ target ['.s-body','strong']           → 미적용(strong을 직접 겨냥하지 않음)
    이렇게 해야 「특정 문맥에서만 도는 규칙」을 전역 실효값으로 오인하지 않는다.
    """
    rt = tokens_of(rule_sel)
    if not rt or rt[-1] != target_tokens[-1]:
        return False
    i = 0
    for t in target_tokens:
        if i < len(rt) and rt[i] == t:
            i += 1
    return i == len(rt)


def resolve(rules, target_tokens: list[str], prop: str):
    """target 요소에 실제로 적용되는 prop의 실효값과 출처. 없으면 (None, None)."""
    best = None
    for sel, decls, origin, order in rules:
        if prop not in decls:
            continue
        if not rule_applies(sel, target_tokens):
            continue
        key = (specificity(sel), order)
        if best is None or key > best[0]:
            best = (key, decls[prop], f"{origin}  `{sel}`")
    return (best[1], best[2]) if best else (None, None)


# ══════════════════════════════════════════════════════════════════════
# 선언 파싱 — kit/guide/토큰-치트시트.md
# ══════════════════════════════════════════════════════════════════════
def _cells(line: str):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def parse_declared_roles(md: str):
    """R-TYPE-01 표에서 (역할, 셀렉터들, 실효값) 을 읽는다."""
    if "R-TYPE-01" not in md:
        return []
    body = md.split("R-TYPE-01", 1)[1].split("## R-TYPE-02", 1)[0]
    out = []
    for line in body.splitlines():
        if not line.strip().startswith("|") or line.strip().startswith("|---"):
            continue
        c = _cells(line)
        if len(c) < 5 or c[0] in ("역할",):
            continue
        role = re.sub(r"\*\*", "", c[0]).strip()
        sels = re.findall(r"`([^`]+)`", c[1])
        eff = re.sub(r"\*\*", "", c[3]).strip()
        if not sels or not eff or eff == "—":
            continue
        out.append({"role": role, "selectors": sels, "declared": eff})
    return out


def parse_declared_tokens(md: str):
    """토큰 → 선언 값.

    두 가지 표기를 모두 읽는다:
      · 표 행:      | `--fs-body` | **22px** | 본문 | …
      · 인라인 목록: `--sp-4` · `--sp-8` · … **`--sp-18`**(카드·박스 사이) …
    ⚠️ 간격 스케일(R-TYPE-02d)은 표가 아니라 인라인 목록이다. 표만 읽으면
       `--sp-*`가 통째로 빠지고, 그러면 「토큰을 못 찾았다」가 **불일치**로
       잡혀 오탐이 된다(실측 사고).
    """
    out = {}
    for line in md.splitlines():
        m = re.match(r"\|\s*`(--[\w-]+)`\s*\|\s*\*{0,2}([^|*]+?)\*{0,2}\s*\|", line.strip())
        if m:
            out[m.group(1)] = m.group(2).strip()
    # 인라인 목록 — 이름에 값이 들어 있는 스케일 토큰(`--sp-18` → 18px)
    for name in re.findall(r"`(--sp-(\d+))`", md):
        out.setdefault(name[0], f"{name[1]}px")
    return out


def token_reference_counts(tokens):
    """토큰이 **참조**되는 횟수(정의는 빼고). kit + 신규 주차 템플릿만 센다.

    ⚠️ 주차 shell(courses/**/강의덱.초안)은 세지 않는다 — 주차 오버라이드는
       집행부가 아니다(kit을 직접 쓰면 원상복귀하는 상태를 잡는 것이 목적).
    """
    scan = []
    for base, pats in ((os.path.join(ROOT, "kit"), (".css", ".html")),
                       (os.path.join(ROOT, "sessions", "_template"), (".html",))):
        for dirpath, _dirs, files in os.walk(base):
            for f in files:
                if f.endswith(pats):
                    scan.append(os.path.join(dirpath, f))
    counts = {t: 0 for t in tokens}
    for p in scan:
        try:
            with open(p, encoding="utf-8") as fh:
                txt = fh.read()
        except OSError:
            continue
        for t in tokens:
            counts[t] += len(re.findall(r"var\(\s*" + re.escape(t) + r"\s*[,)]", txt))
    return counts


# ══════════════════════════════════════════════════════════════════════
# 검사 명세 — 「정본표의 어느 행이 어느 요소의 어느 속성으로 실현되어야 하는가」
# ══════════════════════════════════════════════════════════════════════
# ⚠️ 이 표가 검사의 **판단 부분**이다. 문서의 셀렉터 문자열을 그대로 믿지 않고,
#    「그 역할이 실제로 어느 요소에 걸려야 하는가」를 여기에 명시한다.
#    문서가 바뀌면 위 파서가 값을 다시 읽으므로 값은 여기 하드코딩하지 않는다.
PX = r"(\d+(?:\.\d+)?)px"
LH = r"line-height\s*(\d+(?:\.\d+)?)"
WT = r"weight\s*(\d+)"

ROLE_CHECKS = [
    # (역할표의 역할명, 검사할 요소 토큰, 속성, 기대값 추출기)
    ("본문", [".s-body"], "font-size", PX),
    ("본문", [".s-body"], "line-height", LH),
    ("본문(center 계열)", [".center-v", ".s-body"], "font-size", PX),
    ("리드", [".s-lead"], "font-size", PX),
    ("제목", [".s-title"], "font-size", PX),
    ("eyebrow", [".s-eyebrow"], "font-size", PX),
    ("표", ["table.t"], "font-size", PX),
    ("박스 제목", [".work-step", "b"], "font-size", PX),
    ("박스 제목", [".card", "h3"], "font-size", PX),
    ("박스 제목", [".cc-side", "h3"], "font-size", PX),
    ("박스 제목", [".work-step", "b"], "font-weight", WT),
    ("박스 안 설명문", [".desc"], "font-size", PX),
    ("박스 안 설명문", [".desc"], "font-weight", WT),
    ("본문 강조", [".s-body", "strong"], "font-weight", WT),
]

# 토큰이 「그 용도의 요소」에 실제로 배선됐는가.
TOKEN_WIRING_CHECKS = [
    # (토큰, 용도 설명, 검사할 요소 토큰, 속성)
    ("--sp-18", "카드·박스 사이 여백", [".grid-2"], "gap"),
    ("--sp-18", "카드·박스 사이 여백", [".grid-3"], "gap"),
]


# ══════════════════════════════════════════════════════════════════════
# 알려진 불일치 등재 — 사유 없이 추가하지 마라
# ══════════════════════════════════════════════════════════════════════
# 형식: 키 -> 사유. 키는 아래 mismatch_key()가 만든다.
# ⚠️ **등재는 「고쳤다」가 아니라 「지금은 못 고친다」는 기록이다.** 사유에
#    「왜 못 고치는가」와 「언제 재판정하는가」를 반드시 적는다.
KNOWN = {
    "role:박스 제목:.work-step b:font-size":
        "소급 범위 밖(FINDINGS L). kit을 26px로 올리면 1주차 .work-step 24곳이 "
        "함께 움직여 사실상 소급 적용이고 D-4(신규 주차만)와 충돌한다. "
        "신규 주차는 sessions/_template의 경화 블록으로 26px를 받는다. S8에서 재판정.",
    "role:박스 제목:.card h3:font-size":
        "kit에 `.card h3` 규칙이 아예 없다(정의 0건). 신설하면 .card를 쓰는 "
        "1·2주차 슬라이드가 전부 움직인다 — 소급이다. S8에서 재판정.",
    "role:박스 제목:.cc-side h3:font-size":
        "kit은 25px, 정본은 26px — 1px 차이다. patterns.css:95를 고치면 "
        "1·2주차의 .cc-side 슬라이드가 움직인다. S8에서 재판정.",
    "role:박스 안 설명문:.desc:font-size":
        "kit에 `.desc` 규칙이 없다 — 2주차 shell과 sessions/_template에만 있다. "
        "kit에 신설하면 .desc를 쓰는 기존 슬라이드가 움직인다. S8에서 재판정.",
    "role:박스 제목:.work-step b:font-weight":
        "kit에 `.work-step b`의 font-weight 선언이 없다. `<b>`는 브라우저 기본이 "
        "bold(700)라 정본의 800이 실현되지 않는다. kit에 800을 넣으면 `.work-step`을 "
        "쓰는 1주차 24곳·2주차 다수가 함께 굵어진다 — 소급이다. "
        "신규 주차는 템플릿 경화 블록 ②가 800을 준다. S8에서 재판정.",
    "role:박스 안 설명문:.desc:font-weight":
        "kit에 `.desc` 규칙 자체가 없어 weight가 상속(400)된다. 정본은 500이다. "
        "kit에 신설하면 `.desc`를 쓰는 기존 슬라이드가 움직인다 — 소급이다. "
        "신규 주차는 템플릿 경화 블록 ②가 500을 준다. S8에서 재판정.",
    "token:--sp-18:.grid-2:gap":
        "소급 범위 밖(FINDINGS L). kit gap을 18px로 올리면 1주차 .grid-* 6곳이 "
        "움직인다. 신규 주차는 템플릿 경화 블록에서 18px를 받는다. S8에서 재판정.",
    "token:--sp-18:.grid-3:gap":
        "소급 범위 밖(FINDINGS L). `.grid-2`와 같은 사유다 — kit gap을 18px로 "
        "올리면 1주차의 `.grid-3` 5곳이 함께 움직인다. 신규 주차는 템플릿 경화 "
        "블록에서 `var(--sp-18)`로 18px를 받는다. S8 소급 판정에서 재판정.",
}


def mismatch_key(kind, name, target, prop):
    return f"{kind}:{name}:{' '.join(target)}:{prop}"


# ══════════════════════════════════════════════════════════════════════
def run():
    with open(CHEATSHEET, encoding="utf-8") as fh:
        md = fh.read()
    roles = parse_declared_roles(md)
    tokens = parse_declared_tokens(md)

    rules = []
    order = 0
    for name in KIT_CSS:                    # ⚠️ 로드 순서대로. order를 이어 센다.
        path = os.path.join(ROOT, "kit", "styles", name)
        with open(path, encoding="utf-8") as fh:
            got, order = parse_rules(fh.read(), name, order)
        rules.extend(got)

    parsed = {"role_rows": len(roles), "tokens": len(tokens), "css_rules": len(rules)}
    findings = []          # (key, 설명, 선언, 실효, 출처)

    role_by_name = {}
    for r in roles:
        role_by_name.setdefault(r["role"], r)

    for role_name, target, prop, extract in ROLE_CHECKS:
        decl = role_by_name.get(role_name)
        if not decl:
            findings.append((f"missing-decl:{role_name}",
                             f"정본표에서 역할 「{role_name}」 행을 찾지 못했다(표 구조 변경?)",
                             "?", "?", "—"))
            continue
        m = re.search(extract, decl["declared"])
        if not m:
            continue
        want = float(m.group(1))
        unit = "px" if extract is PX else ""
        got_raw, src = resolve(rules, target, prop)
        got = None
        if got_raw:
            gm = re.search(r"(\d+(?:\.\d+)?)", got_raw)
            got = float(gm.group(1)) if gm else None
        # 「하한」 성격이면 이상이면 통과. 하한은 크기에만 적용한다 —
        # weight·line-height에 「하한」을 적용하면 의미가 달라진다.
        is_floor = (extract is PX) and ("하한" in decl["declared"] or "≥" in decl["declared"])
        ok = got is not None and (got >= want if is_floor else abs(got - want) < 0.01)
        if not ok:
            findings.append((mismatch_key("role", role_name, target, prop),
                             f"역할 「{role_name}」 — {' '.join(target)} 의 {prop}",
                             f"{want:g}{unit}" + ("(하한)" if is_floor else ""),
                             (f"{got:g}{unit}" if got is not None else "정의 없음"),
                             src or "—"))

    for tok, purpose, target, prop in TOKEN_WIRING_CHECKS:
        if tok not in tokens:
            findings.append((f"missing-token:{tok}",
                             f"정본표에서 토큰 {tok} 을 찾지 못했다", "?", "?", "—"))
            continue
        m = re.search(r"(\d+(?:\.\d+)?)px", tokens[tok])
        if not m:
            continue
        want = float(m.group(1))
        got_raw, src = resolve(rules, target, prop)
        gm = re.search(r"(\d+(?:\.\d+)?)px", got_raw or "")
        got = float(gm.group(1)) if gm else None
        if got is None or abs(got - want) > 0.01:
            findings.append((mismatch_key("token", tok, target, prop),
                             f"토큰 {tok}({purpose}) — {' '.join(target)} 의 {prop}",
                             f"{want:g}px",
                             (f"{got:g}px" if got is not None else "정의 없음"),
                             src or "—"))

    return roles, tokens, rules, parsed, findings


def main() -> int:
    ap = argparse.ArgumentParser(description="선언 값과 kit 집행부 실효값의 불일치 검출")
    ap.add_argument("--list", action="store_true", help="등재된 불일치까지 전부 출력")
    a = ap.parse_args()

    roles, tokens, rules, parsed, findings = run()

    print("선언과 집행 불일치 검사 (유형⑤)")
    print(f"  파싱: 역할표 {parsed['role_rows']}행 · 토큰 {parsed['tokens']}개 · "
          f"kit CSS 규칙 {parsed['css_rules']}개")

    # ⚠️ 파싱이 깨졌는데 「불일치 0」이 나오는 것을 막는다.
    if parsed["role_rows"] == 0 or parsed["tokens"] == 0 or parsed["css_rules"] == 0:
        print("\n[실패] 파싱 결과가 0이다 — 「불일치 0」이 아니라 **아무것도 못 읽은 것**이다.")
        print("       정본표 구조나 CSS 경로가 바뀌었는지 확인하라.")
        return 2

    new = [f for f in findings if f[0] not in KNOWN]
    old = [f for f in findings if f[0] in KNOWN]

    def show(rows, head):
        if not rows:
            return
        print(f"\n{head}")
        for key, desc, want, got, src in rows:
            print(f"  · {desc}")
            print(f"      선언 {want}  vs  집행 {got}      [{src}]")
            if key in KNOWN:
                print(f"      등재 사유: {KNOWN[key]}")

    show(new, "[FAIL] 등재되지 않은 새 불일치")
    if a.list:
        show(old, "[등재됨] 알려진 불일치 — 통과시킨다")
    elif old:
        print(f"\n[등재됨] 알려진 불일치 {len(old)}건 — `--list`로 상세 확인")

    # 토큰 배선 실태 — 죽은 체계를 만들지 않았는지
    declared = [t for t in tokens if t.startswith(("--fs-", "--lh-", "--sp-"))]
    counts = token_reference_counts(declared)
    dead = sorted(t for t in declared if counts[t] == 0)
    print(f"\n토큰 배선: 선언 {len(declared)}개 중 참조 0건 **{len(dead)}개**")
    if dead:
        print("  " + " ".join(dead))
        print("  ⚠️ 참조 0건 토큰은 코드에 아무 영향도 주지 못한다. 선언만 있는 체계다.")

    if new:
        print(f"\nRESULT | FAIL | 새 불일치 {len(new)}건 — 고치거나 사유와 함께 KNOWN에 등재하라")
        print("        ⚠️ 「문서 쪽 값을 낮춰」 맞추지 마라. 문서가 맞고 코드가 안 따라온 것이면")
        print("           검출만 하고 소급 판정으로 넘긴다.")
        return 1
    print(f"\nRESULT | PASS | 새 불일치 0 (등재된 알려진 불일치 {len(old)}건)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
