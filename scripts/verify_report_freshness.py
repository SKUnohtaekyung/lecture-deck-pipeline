#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""보고·결정표 신선도 검사 — 기제6(완료 보고의 노후화) 차단 (P5 · 배치4 2026-08-17).

왜
--
보고·결정표가 「살아 있는 정본」인지 「시점 스냅샷」인지 선언이 없어, 읽는 쪽은
정본으로 믿고 쓰는 쪽은 갱신 의무가 없었다(`plans/system-improvement/ANALYSIS.md`
§2-기제6 — 3주차 조립_보고가 V4-11을 «남겼다»와 «삭제 경위»로 같은 문서에서
자기모순·결정표는 신설 8장을 모름). 실측: 2주차 보고 머리 «98장»(현행 112) ·
3주차 «77장»(현행 81) — 둘 다 조립 중간 시점 스냅샷인데 선언이 없었다.

무엇을 강제하나
--------------
대상 문서(`조립_보고.md` · `*결정표*.md`)의 상단에 둘 중 하나를 요구한다:
  ① 기준 덱 식별자 — «N장» + «sha256 `앞8자`» (쪽ID매핑 스냅샷과 같은 형식)
     → 현행 덱과 대조해 일치하면 통과, 다르면 «낡음»
  ② 시점 스냅샷 선언 — `[시점 스냅샷 YYYY-MM-DD]`
     → 문서가 스스로 시점 기록임을 선언하면 통과(문서 값 낮추기가 아니라 지위 명시)
둘 다 없으면 «미기재»다. 위반 = 미기재 + 낡음.

출구는 두 개뿐이다: 재조립 후 보고를 갱신(식별자 갱신)하거나, 스냅샷을 선언한다.
전면 재작성을 강요하지 않는다(PLAN P5 리스크 절).

사용:
    python scripts/verify_report_freshness.py <주차>            # 리포트(exit 0)
    python scripts/verify_report_freshness.py <주차> --strict   # 위반 >0 → exit 1
    python scripts/verify_report_freshness.py --session <폴더>  # 테스트용 직접 지정
러너(`run_deck_checks.py`)가 «신선도 위반 N건» 줄을 계약 waiver
`report_freshness_baseline`(count)과 대조해 증가만 FAIL한다.
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

HEAD_CHARS = 3000  # 식별자·선언은 문서 머리에 있어야 한다 — 본문 깊숙한 우연 일치를 세지 않는다
_SNAPSHOT_RE = re.compile(r"\[시점 스냅샷[ :·]*\d{4}-\d{2}-\d{2}\]")
_SLIDES_RE = re.compile(r"\*\*(\d+)장\*\*")
_SHA_RE = re.compile(r"sha256\s*`([0-9a-f]{8})`")


def _rel(path: str) -> str:
    return os.path.relpath(path, ROOT).replace(os.sep, "/")


def deck_meta(deck_path: str):
    """(장수, sha8) — 현행 덱의 대조 기준."""
    with open(deck_path, "rb") as fh:
        raw = fh.read()
    sha8 = hashlib.sha256(raw).hexdigest()[:8]
    n = len(re.findall(rb'<section[^>]*\bclass="[^"]*\bslide\b', raw, re.I))
    return n, sha8


def check_report(text: str, deck_slides: int, deck_sha8: str):
    """('ok'|'stale'|'missing', 상세) — 순수 함수(픽스처 테스트 대상)."""
    head = text[:HEAD_CHARS]
    if _SNAPSHOT_RE.search(head):
        return "ok", "시점 스냅샷 선언 — 지위 명시로 통과"
    m_n = _SLIDES_RE.search(head)
    m_s = _SHA_RE.search(head)
    if not (m_n and m_s):
        return "missing", "기준 덱 식별자(«**N장**» + «sha256 `앞8자`») 또는 [시점 스냅샷 YYYY-MM-DD] 선언 없음"
    n, s = int(m_n.group(1)), m_s.group(1)
    if n == deck_slides and s == deck_sha8:
        return "ok", f"기준 덱 일치({n}장 · {s})"
    return "stale", f"낡음 — 문서 {n}장·{s} vs 현행 {deck_slides}장·{deck_sha8}"


def find_reports(session: str):
    pats = [os.path.join(session, "조립_보고.md"),
            os.path.join(session, "*결정표*.md"),
            os.path.join(session, "개정이력", "*결정표*.md")]
    out = []
    for p in pats:
        out.extend(sorted(glob.glob(p)))
    return out


# ── 0판정 가드(2026-08-24) ───────────────────────────────────────────────
# find_reports()는 파일명 관례(조립_보고.md·*결정표*.md)를 하드코딩한다. 다른
# 명명이면 reports=[]가 되고, 그동안은 이것과 "이 세션엔 보고류가 정말 하나도
# 없다"를 구분하지 못한 채 똑같이 "위반 0건"으로 통과시켰다. find_missed()는
# 파일명과 무관하게 check_report()가 신뢰하는 것과 같은 식별자 신호(머리
# HEAD_CHARS 안의 «**N장**»+sha256 또는 [시점 스냅샷 ...])를 직접 찾는다 —
# "이 문서는 신선도 추적 대상으로 설계됐다"는 저자 의도 신호이므로 파일명이
# 달라도 잡힌다. 탐색 범위는 find_reports()와 똑같은 두 위치(세션 루트·
# 개정이력)로 맞춘다 — 범위를 넓히면(예: 자료/) 판정 대상 자체가 달라져
# "판정 기준을 손대지 않는다"는 잠긴 결정을 어기게 된다.
def looks_like_report_text(text: str) -> bool:
    head = text[:HEAD_CHARS]
    return bool(_SNAPSHOT_RE.search(head) or (_SLIDES_RE.search(head) and _SHA_RE.search(head)))


def find_candidates(session: str):
    """find_reports()와 같은 두 디렉터리에서 `*.md`를 전부 훑는다(파일명 무관)."""
    out = []
    for d in (session, os.path.join(session, "개정이력")):
        if os.path.isdir(d):
            out.extend(sorted(glob.glob(os.path.join(d, "*.md"))))
    return out


def find_missed(session: str, reports: list) -> list:
    """식별자 신호는 있지만 find_reports()의 파일명 관례에 안 걸린 문서 — 미판정 후보."""
    known = set(os.path.normcase(os.path.abspath(p)) for p in reports)
    missed = []
    for path in find_candidates(session):
        if os.path.normcase(os.path.abspath(path)) in known:
            continue
        try:
            text = open(path, encoding="utf-8").read()
        except (OSError, UnicodeDecodeError):
            continue
        if looks_like_report_text(text):
            missed.append(path)
    return missed


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("week", nargs="?", help="주차 (예: 3주차)")
    ap.add_argument("--session", help="세션 폴더 직접 지정(테스트용)")
    ap.add_argument("--strict", action="store_true", help="위반 >0이면 exit 1")
    a = ap.parse_args()

    if a.session:
        session = a.session
    elif a.week:
        try:
            import _course_paths
            num = a.week[:-2] if a.week.endswith("주차") else a.week
            session = _course_paths.session_dir(num, ROOT)
        except Exception:
            print("[실패] 주차 경로를 해석하지 못했다 — --session으로 직접 지정하라")
            return 2
    else:
        ap.print_usage()
        return 2

    deck = os.path.join(session, "강의덱.html")
    reports = find_reports(session)
    missed = find_missed(session, reports)
    if not reports:
        if missed:
            print(f"[미판정] 신선도 식별자(«**N장**»+sha256 또는 [시점 스냅샷 ...])를 가진 "
                  f"문서 {len(missed)}건을 찾았으나 명명 관례(조립_보고.md·*결정표*.md)와 "
                  f"달라 자동 판정 대상에서 빠졌다 — «정말 보고류가 없음»과는 다르다:")
            for p in missed:
                print(f"  - {_rel(p)}")
            print(f"판정 0건 · 미판정 {len(missed)}건")
            print("신선도 위반 0건(판정 대상 0건 — 위 미판정 문서는 이 수치에 포함되지 않았다)")
            return 1 if a.strict else 0
        print("[입력없음] 보고류 문서 0건(조립_보고.md·*결정표*) — 판정 대상 없음")
        print("판정 0건 · 미판정 0건")
        print("신선도 위반 0건")
        return 0
    if not os.path.exists(deck):
        print(f"[실패] 덱이 없어 대조 불가: {deck}")
        return 2

    n, sha8 = deck_meta(deck)
    print(f"현행 덱: {n}장 · sha256 `{sha8}`")
    bad = 0
    for path in reports:
        rel = os.path.relpath(path, ROOT).replace("\\", "/")
        try:
            text = open(path, encoding="utf-8").read()
        except (OSError, UnicodeDecodeError) as exc:
            print(f"[FAIL] {rel} — 읽기 실패: {exc}")
            bad += 1
            continue
        verdict, detail = check_report(text, n, sha8)
        mark = {"ok": "PASS", "stale": "FAIL", "missing": "FAIL"}[verdict]
        if verdict != "ok":
            bad += 1
        print(f"[{mark}] {rel} — {detail}")
    if missed:
        print(f"\n[미판정] 명명 관례 밖이라 위 판정에서 빠진 신선도 식별자 문서 {len(missed)}건:")
        for p in missed:
            print(f"  - {_rel(p)}")
    print(f"\n판정 {len(reports)}건 · 미판정 {len(missed)}건")
    print(f"신선도 위반 {bad}건 (출구: 재조립 후 식별자 갱신 또는 [시점 스냅샷 YYYY-MM-DD] 선언 — 규약 sessions/README.md)")
    return 1 if (a.strict and (bad or missed)) else 0


if __name__ == "__main__":
    sys.exit(main())
