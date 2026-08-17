#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""계약 waiver 스키마 lint — «무사유 waiver 거부»의 정본 (P1 · 2026-08-17).

왜
--
2026-08 시스템 분석(plans/system-improvement/ANALYSIS.md §2-기제3)이 확정한 패턴:
게이트를 끄는 탈출구(계약 키 비우기 · WARN 기본값)가 **사유 기록 없이 조용히
상시화**된다. 3주차 계약의 `"sequences": {}` 공동화로 절대사수 슬라이드 V1-04가
기록 없이 소실됐다. 탈출구 자체는 금지하지 않는다 — AGENTS.md 규율대로 **숨기지
않고, 기록에 남고, 세어질 수 있게** 한다.

무엇을 강제하나
--------------
deck.contract.json의 `known_violations` 각 항목에:
  - `reason`: 비어 있지 않은 사유 문자열 (필수)
  - `date`  : YYYY-MM-DD (필수)
`warn_baseline`(run_deck_checks 구조 WARN 래칫 기준선)이 있으면:
  - `static_gates`: 정수 · `date`: YYYY-MM-DD

집행 계층
--------
  ① verify_deck.py — 이 모듈의 `waiver_entry_valid()`로 판정해, 무효 waiver는
     **아예 강등하지 않는다**(FAIL 유지). 스키마 로직은 여기 한 벌뿐이다.
  ② .githooks/_gate.py — deck.contract.json이 staged면 이 스크립트를 돌려
     위반 시 커밋을 차단한다.

검사 범위: courses/**/deck.contract.json · sessions/_contracts/*.deck.contract.json ·
sessions/_template/deck.contract.json. tests/·tmp/·_보관*은 제외한다(픽스처는
고의 위반을 담을 수 있고, 보관본은 동결 기록이다).

사용:
    python scripts/verify_contract_waivers.py
종료코드: 0 통과 · 1 스키마 위반 · 2 검사 대상 0건(눈먼 0 방지 — 경로가 깨진 것)
"""
from __future__ import annotations

import json
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_SKIP_DIRS = {".git", "tmp", "tests", "node_modules", "_dev"}


def waiver_entry_valid(entry) -> bool:
    """waiver 항목 유효성 — reason(비어 있지 않음) + date(YYYY-MM-DD).

    verify_deck.py가 강등 여부를 정할 때 그대로 쓴다. 여기 기준을 낮추면
    무사유 waiver가 다시 작동하게 되므로, 완화는 이 파일에서만·사유와 함께.
    """
    if not isinstance(entry, dict):
        return False
    reason = entry.get("reason")
    date = entry.get("date")
    if not isinstance(reason, str) or not reason.strip():
        return False
    if not isinstance(date, str) or not _DATE_RE.match(date):
        return False
    return True


def find_contracts(root: str):
    found = []
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs
                   if d not in _SKIP_DIRS and not d.startswith("_보관")]
        for f in files:
            if f == "deck.contract.json" or f.endswith(".deck.contract.json"):
                found.append(os.path.join(base, f))
    return sorted(found)


def lint_contract(path: str):
    """(문제 목록) — 비어 있으면 통과."""
    problems = []
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except Exception as exc:
        return [f"JSON 파싱 실패: {exc}"]

    kv = data.get("known_violations")
    if kv is not None and not isinstance(kv, dict):
        return ["known_violations가 객체가 아님"]
    for key, entry in (kv or {}).items():
        if not isinstance(entry, dict):
            problems.append(f"waiver '{key}': 객체가 아님(사유·일자를 담을 수 없음)")
            continue
        if not waiver_entry_valid(entry):
            problems.append(
                f"waiver '{key}': reason(비어 있지 않은 사유)·date(YYYY-MM-DD) 필수 — "
                f"현재 reason={entry.get('reason')!r} date={entry.get('date')!r}")

    wb = data.get("warn_baseline")
    if wb is not None:
        if not isinstance(wb, dict) or not isinstance(wb.get("static_gates"), int) \
                or not (isinstance(wb.get("date"), str) and _DATE_RE.match(wb["date"])):
            problems.append(
                "warn_baseline: {static_gates: 정수, date: YYYY-MM-DD} 형식이어야 함 — "
                f"현재 {wb!r}")
        # 렌더·품질 WARN 래칫 기준선(P4 배치3 · 배치4) — 선택 키이나, 있으면 정수여야 한다.
        # 형식이 깨진 채 두면 러너가 «미등재»로 읽어 FAIL하므로 여기서 먼저 잡는다.
        else:
            for opt_key, label in (("render", "렌더"), ("quality", "품질")):
                if opt_key in wb and not isinstance(wb.get(opt_key), int):
                    problems.append(
                        f"warn_baseline.{opt_key}: 정수여야 함({label} WARN 래칫 기준선) — 현재 {wb.get(opt_key)!r}")
    return problems


def main() -> int:
    contracts = find_contracts(ROOT)
    if not contracts:
        print("검사 대상 deck.contract.json 0건 — 탐색 경로가 깨졌다(눈먼 0 방지)")
        return 2
    bad = 0
    for path in contracts:
        rel = os.path.relpath(path, ROOT).replace("\\", "/")
        problems = lint_contract(path)
        if problems:
            bad += 1
            print(f"[FAIL] {rel}")
            for p in problems:
                print(f"    - {p}")
        else:
            print(f"[PASS] {rel}")
    print(f"\nRESULT | {'FAIL' if bad else 'PASS'} | 계약 {len(contracts)}건 중 위반 {bad}건")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
