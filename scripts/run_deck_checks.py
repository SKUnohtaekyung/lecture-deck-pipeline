#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""덱 검증 러너 — 조립 이후의 검사를 명령 하나로 잇는다.

왜 필요한가 (F9)
---------------
문서 네 곳이 렌더 감사를 「필수」라 적어 두었지만, 실행 경로에는 어디에도 배선돼
있지 않았다. `assemble_deck.py`는 `verify_*`를 호출하지 않고(subprocess 0건),
유일한 자동 훅 `hook_slide_guard.py`는 docstring에 스스로 "실패해도 도구 호출을
막지 않는다"고 적었다. CI도 pre-commit도 없다. 결과적으로 **검증 여부가 전적으로
사람(에이전트)의 기억에 달려 있었고**, 2026-07-31 사고는 그 기억이 실패한 경우다.

설계 원칙
--------
1. **조립기 안에 검증을 심지 않는다.** `assemble_deck.py`는 순수 연결자로 남긴다 —
   조립이 검증 때문에 실패하면 shard 편집 흐름이 끊긴다. 이 러너가 감싼다.
2. **렌더 증거 없이는 0을 반환하지 않는다.** 헤드리스 브라우저는 도입하지 않는다
   (DEC-03 · 2026-07-26 사용자 결정). 그래서 이 러너는 브라우저를 직접 몰지 못한다.
   대신 «브라우저에서 뽑은 감사 JSON»을 요구하고, 그것이 없거나·낡았거나·
   INVALID면 **실패**한다. 이렇게 해야 「필수」가 실제로 필수가 된다.
3. **기존 게이트의 판정을 바꾸지 않는다.** 이 러너는 호출자일 뿐이며, 임계·강등
   규칙은 각 스크립트가 그대로 소유한다.

사용
----
    python scripts/run_deck_checks.py <주차>                  # 예: 2주차
    python scripts/run_deck_checks.py <주차> --assemble       # shard 재조립부터
    python scripts/run_deck_checks.py <주차> --render-only    # 렌더 증거만 판정
    python scripts/run_deck_checks.py <주차> --skip-render    # ⚠️ 렌더 증거 검사 생략
                                                              #   (조립 중간 점검용 —
                                                              #    이 경우 종료코드를 통과
                                                              #    근거로 쓰지 마라)

렌더 증거 만드는 법 (러너가 실패하면 그대로 안내한다)
--------------------------------------------------
    python -m http.server 8799
    # 브라우저로 덱을 열고(창 1280x720 이상) 콘솔에서:
    #   await (await fetch('/scripts/audit_all.js')).text().then(eval)
    # 출력 JSON을 그대로 저장:  sessions/_verify/<주차>/deck-audit.json

증거가 「있다」로 끝나지 않게 하는 장치
------------------------------------
- 파일이 **덱보다 낡으면** 실패한다(덱 고치고 재측정 안 한 경우)
- 감사기가 낸 **INVALID**를 통과로 세지 않는다(--scale=0 등 측정 무효)
- 증거의 **장수와 덱의 장수가 다르면** 실패한다(다른 덱을 잰 경우)
- 다만 **수치 자체로는 FAIL시키지 않는다.** 신설 검사는 WARN으로 시작해
  기준선을 쌓는다 — 러너가 강제하는 것은 «측정을 실제로 했는가»다.

종료코드
--------
  0  통과 — 정적 게이트 + 렌더 증거를 **둘 다** 확인했다
  1  실패 — 게이트 FAIL 또는 렌더 증거 부재/무효/낡음
  2  사용법 오류(주차 폴더 없음·덱 없음·플래그 충돌)
  3  **불완전** — `--skip-render` 또는 `--render-only`로 일부만 돌렸다.
     실패는 아니지만 **통과의 근거로 쓸 수 없다.** 0과 구분되는 이유는,
     부분 실행이 완전 통과로 읽히는 것이 이 저장소가 반복해서 겪은 사고이기
     때문이다(독립 검증 2026-08-03이 실제로 이 구멍을 잡았다).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):          # Windows cp949에서 한글이 죽지 않게
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

try:
    import _course_paths
except Exception:                                # pragma: no cover - 경로 헬퍼가 없으면 폴백
    _course_paths = None

EVIDENCE = "deck-audit.json"


def _week_num(week: str) -> str:
    """`2` 와 `2주차` 를 모두 받는다 — 저장소 안에서 두 표기가 섞여 쓰인다."""
    return week[:-2] if week.endswith("주차") else week


def _session_dir(week_num: str) -> str:
    if _course_paths is not None:
        try:
            return _course_paths.session_dir(week_num, ROOT)
        except Exception:
            pass
    return os.path.join(ROOT, "courses", "바이브코딩", "sessions", f"{week_num}주차")


def _rel(p: str) -> str:
    try:
        return os.path.relpath(p, ROOT).replace("\\", "/")
    except Exception:
        return p


class Runner:
    def __init__(self, week: str):
        self.num = _week_num(week)
        self.week = f"{self.num}주차"
        self.session = _session_dir(self.num)
        self.deck = os.path.join(self.session, "강의덱.html")
        self.shard = os.path.join(self.session, "강의덱.초안")
        self.notes = os.path.join(self.session, "강의덱_발표자노트.html")
        self.verify_dir = os.path.join(ROOT, "sessions", "_verify", self.week)
        self.steps: list[tuple[str, bool, str]] = []

    # ── 단계 실행 ────────────────────────────────────────────────────
    def _py(self, name: str, script: str, *args: str, allow_warn: bool = True) -> bool:
        cmd = [sys.executable, os.path.join(HERE, script), *args]
        print(f"\n=== {name} ===\n$ {' '.join(_rel(c) if os.path.sep in c else c for c in cmd)}")
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                              encoding="utf-8", errors="replace")
        tail = (proc.stdout or "").rstrip().splitlines()[-6:]
        for line in tail:
            print("  " + line)
        if proc.stderr and proc.returncode != 0:
            print("  [stderr] " + (proc.stderr or "").strip().splitlines()[-1])
        ok = proc.returncode == 0
        self.steps.append((name, ok, "" if ok else f"exit {proc.returncode}"))
        return ok

    def assemble(self) -> bool:
        if not os.path.isdir(self.shard):
            self.steps.append(("조립", False, f"shard 폴더 없음: {_rel(self.shard)}"))
            return False
        return self._py("조립 (assemble_deck)", "assemble_deck.py", _rel(self.shard))

    def static_gates(self, parts: str | None) -> bool:
        ok = True
        args = [_rel(self.deck)]
        if parts:
            args += ["--parts", parts]
        ok &= self._py("정적 게이트 (verify_deck)", "verify_deck.py", *args)
        ok &= self._py("내용 품질 (verify_deck_quality)", "verify_deck_quality.py", _rel(self.deck))
        if os.path.exists(self.notes):
            ok &= self._py("발표자 노트 (verify_notes)", "verify_notes.py",
                           _rel(self.deck), _rel(self.notes))
        else:
            self.steps.append(("발표자 노트", True, "노트 없음 — 건너뜀"))
        return ok

    # ── 렌더 증거 판정 (이 러너의 존재 이유) ──────────────────────────
    def _load_evidence(self, fname: str) -> tuple[object | None, str]:
        path = os.path.join(self.verify_dir, fname)
        if not os.path.exists(path):
            return None, f"없음 — {_rel(path)}"
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
        except Exception as exc:
            return None, f"JSON 파싱 실패 — {exc}"
        if os.path.exists(self.deck) and os.path.getmtime(path) < os.path.getmtime(self.deck):
            age = (os.path.getmtime(self.deck) - os.path.getmtime(path)) / 60.0
            return None, (f"덱보다 낡았다 — 덱 수정 {age:.0f}분 후에도 재측정하지 않았다. "
                          f"({_rel(path)})")
        # 검출기의 fail-closed 반환을 통과로 세지 않는다
        if isinstance(data, dict) and data.get("INVALID"):
            return None, "측정 무효(INVALID): " + "; ".join(map(str, data["INVALID"]))
        return data, ""

    def render_evidence(self) -> bool:
        data, err = self._load_evidence(EVIDENCE)
        if err:
            self.steps.append(("렌더·타이포 감사", False, err))
            print("\n" + "─" * 68)
            print(f"렌더 증거가 없거나 무효다 — {err}")
            print("브라우저에서 직접 측정해야 한다(헤드리스 미도입 · DEC-03):")
            print("  1) python -m http.server 8799")
            print(f"  2) 브라우저로 http://localhost:8799/{_rel(self.deck)} 를 연다")
            print("     ⚠️ 창을 1280x720 이상으로 — 작으면 덱 JS가 --scale을 0으로 계산하고,")
            print("        그 상태의 「결함 0」은 측정 무효다(감사기가 INVALID로 막는다)")
            print("  3) 콘솔에서:")
            print("     await (await fetch('/scripts/audit_all.js')).text().then(eval)")
            print(f"  4) 출력 JSON을 그대로 저장: {_rel(os.path.join(self.verify_dir, EVIDENCE))}")
            print("─" * 68)
            return False

        d = data if isinstance(data, dict) else {}
        if d.get("schema") != "deck-audit/1":
            self.steps.append(("렌더·타이포 감사", False,
                               f"스키마가 다르다: {d.get('schema')!r} — audit_all.js 출력을 그대로 저장하라"))
            return False

        r = (d.get("render") or {}).get("totals") or {}
        t = d.get("typography") or {}
        n_slides = d.get("slideCount")

        # 덱의 실제 장수와 증거의 장수가 다르면 다른 덱을 잰 것이다
        deck_slides = None
        if os.path.exists(self.deck):
            with open(self.deck, encoding="utf-8") as fh:
                # `class="slide` 부분일치로 세면 `.slide-num` 같은 이웃 클래스까지 잡힌다
                # (실측: 110장 덱이 111로 세어졌다). 섹션 태그의 slide 낱말만 센다.
                deck_slides = len(re.findall(
                    r'<section[^>]*\bclass="[^"]*\bslide\b', fh.read(), re.I))
        if deck_slides and n_slides and abs(deck_slides - n_slides) > 0:
            self.steps.append(("렌더·타이포 감사", False,
                               f"장수 불일치 — 덱 {deck_slides}장 vs 증거 {n_slides}장. 다른 덱을 쟀거나 낡았다"))
            return False

        line1 = (f"렌더 {n_slides}장 — 바닥선초과 {r.get('below')} · 이탈 {r.get('off')} · "
                 f"겹침 {r.get('lap')}(참고 abs {r.get('lapAbs')}) · 어절잘림 {r.get('wb')} · "
                 f"빈슬롯 {r.get('slots')}")
        nma = t.get("nearMissAnchors") or {}
        line2 = (f"타이포 — 폰트하한위반 {(t.get('fontFloor') or {}).get('count')} · "
                 f"자간보정누락 {(t.get('tracking') or {}).get('count')} · "
                 f"행간 normal {t.get('lineHeightNormal')} · "
                 f"근-미스앵커 {nma.get('total')}"
                 f"(지배값충돌 {nma.get('dominantClashTotal', '?')})")
        print(f"\n=== 렌더·타이포 감사 (audit_all) ===\n  {line1}\n  {line2}")
        for o in ((d.get("render") or {}).get("offenders") or [])[:8]:
            print(f"    · {o.get('id')}: " + " ".join(map(str, o.get("d") or [])))
        self.steps.append(("렌더·타이포 감사", True, line1 + " / " + line2))

        # ⚠️ 여기서 임계로 FAIL시키지 않는다. 신설 검사는 WARN으로 시작하고 기준선을
        #    먼저 쌓는다(§0-1: 요청을 금지 규칙으로 바꾸지 않는다). 러너가 강제하는
        #    것은 «측정을 실제로 했는가»이지 «수치가 0인가»가 아니다.
        return True

    def report(self, ran_static: bool, ran_render: bool) -> int:
        """⚠️ 이 함수의 성공 메시지를 «항상 같은 문자열»로 두지 마라.
        독립 검증(2026-08-03)이 잡은 결함: 종전에는 어떤 플래그로 돌렸든
        「정적 게이트 + 렌더 증거 모두 확인」을 출력했다. `--render-only`로
        정적 게이트를 건너뛴 실행도 그 문구와 함께 exit 0을 냈다 —
        **부분 실행이 완전 통과로 읽히는** 정확히 그 실패 유형이다."""
        print("\n" + "=" * 68)
        print(f"러너 요약 — {self.week}")
        print("=" * 68)
        failed = 0
        for name, ok, note in self.steps:
            mark = "PASS" if ok else "FAIL"
            if not ok:
                failed += 1
            print(f"  [{mark}] {name}" + (f" — {note}" if note else ""))
        if failed:
            print(f"\nRESULT | FAIL | {failed}개 단계 실패 — 위 안내대로 처리하라")
            return 1

        did = [n for n, f in (("정적 게이트", ran_static), ("렌더 증거", ran_render)) if f]
        skipped = [n for n, f in (("정적 게이트", ran_static), ("렌더 증거", ran_render)) if not f]
        if skipped:
            # 부분 실행은 0을 반환하지 않는다 — docstring이 약속한 계약이다.
            print(f"\nRESULT | 불완전 | {' + '.join(did)}만 확인 — "
                  f"{' · '.join(skipped)}는 실행하지 않았다")
            print("        이 실행의 종료코드를 «통과»의 근거로 쓰지 마라(exit 3).")
            return 3
        print("\nRESULT | PASS | 정적 게이트 + 렌더 증거 모두 확인")
        return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="덱 조립 이후 검사를 한 명령으로 잇는다")
    ap.add_argument("week", help="주차 (예: 2주차)")
    ap.add_argument("--assemble", action="store_true", help="shard에서 덱을 먼저 재조립한다")
    ap.add_argument("--parts", help="verify_deck의 part-divider 수")
    ap.add_argument("--render-only", action="store_true", help="렌더 증거만 판정한다")
    ap.add_argument("--skip-render", action="store_true",
                    help="⚠️ 렌더 증거 검사를 생략한다(조립 중간 점검용). "
                         "이 경우 종료코드를 통과 근거로 쓰지 마라")
    a = ap.parse_args()

    if a.render_only and a.skip_render:
        print("[사용법] --render-only 와 --skip-render 는 함께 쓸 수 없다")
        return 2

    r = Runner(a.week)
    if not os.path.isdir(r.session):
        print(f"[실패] 주차 폴더를 찾을 수 없다: {_rel(r.session)}")
        return 2

    ran_static = not a.render_only
    ran_render = not a.skip_render

    if ran_static:
        if a.assemble:
            r.assemble()
        if not os.path.exists(r.deck):
            print(f"[실패] 덱이 없다: {_rel(r.deck)} — --assemble 로 먼저 조립하라")
            return 2
        r.static_gates(a.parts)

    if ran_render:
        r.render_evidence()
    else:
        r.steps.append(("렌더 감사", True,
                        "⚠️ --skip-render 로 생략됨 — 이 실행은 렌더 무결성을 증명하지 않는다"))

    return r.report(ran_static, ran_render)


if __name__ == "__main__":
    sys.exit(main())
