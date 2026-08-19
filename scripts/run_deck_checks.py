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
- **수치도 판정한다(P4 · 배치3 2026-08-17).** 결함형 6종(바닥선초과·이탈·겹침·
  어절잘림·오버플로·빈슬롯)은 계약 waiver `render_<지표>` 베이스라인(없으면 0)
  초과 시 FAIL. 타이포·정렬류는 «렌더 WARN»으로 세어 warn_baseline.render 래칫이
  조용한 증가만 막는다(FAIL 승격은 오탐률 실측 후 — WARN 시작 규율). 밀도 계열은
  계속 사람검토다(R-DENS-03). 규약 정본: sessions/README.md 「주차 구조 계약」.

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

from verify_deck import find_deck_contract
from verify_contract_waivers import waiver_entry_valid

EVIDENCE = "deck-audit.json"
_SUMMARY_RE = re.compile(r"요약: FAIL (\d+) · WARN (\d+)")

# ── P4(배치3 · 2026-08-17) 렌더 수치 판정 ────────────────────────────────────
#   «측정을 했는가»(P1까지의 계약)에 «측정값이 계약 안인가»를 더한다.
#   임계값은 이 러너에 없다 — 결함 판정(바닥선 666 · 안전영역 등)은
#   audit_render.js(BODY_* 상수)가 집행하고, 그 선언 정본은
#   kit/guide/한장-참조표.md다(tests/test_declared_vs_enforced.py가 쌍을 고정).
#   러너는 «판정된 결함의 개수»만 소비한다.
RENDER_DEFECT_KEYS = (("below", "바닥선초과"), ("off", "슬라이드이탈"),
                      ("lap", "정보요소겹침"), ("wb", "어절중간잘림"),
                      ("ovf", "오버플로"), ("slots", "빈이미지슬롯"),
                      # ── 2026-08-18 신설 ──────────────────────────────────
                      # 사용자가 반복 지적한 결함 4종을 «사람의 주의력»이 아니라
                      # 종료코드로 막는다. 신규 주차는 waiver가 없으므로 0이 계약이고,
                      # 동결된 1·2·3주차는 D-2대로 계약 waiver로 강등한다.
                      ("occl", "글자가려짐"),
                      ("wideEmpty", "가로꽉채우고빔"), ("stretchX", "가로늘림"),
                      ("stretchY", "세로늘림"), ("lowFill", "채움률미달"),
                      # 짝 검출기 — 위 넷을 «상자를 줄여라»로만 읽으면 격자가 깨진다.
                      # 그 반대 결함을 같은 층에서 잡아 두 규칙이 서로를 붙든다.
                      ("ragged", "형제높이불일치"))


def numeric_verdicts(totals: dict, typo: dict, kv: dict):
    """(steps, warn_render, waivers) — 순수 함수로 분리해 픽스처 테스트를 가능하게 한다.

    결함형 6종: 실측 > 계약 waiver `render_<지표>`(count·reason·date)의 count
    베이스라인(없으면 0)이면 FAIL — P1 waiver 규약과 같은 «증가만 FAIL» 계약.
    타이포·정렬류(폰트하한·자간·정렬충돌)는 FAIL이 아니라 «렌더 WARN»으로 세고,
    래칫(warn_baseline.render)이 조용한 증가만 막는다(WARN 시작 — 오탐률 실측 후 승격).
    """
    steps: list[tuple[str, bool, str]] = []
    waivers: list[str] = []
    demoted = 0
    for key, label in RENDER_DEFECT_KEYS:
        n = totals.get(key)
        name = f"렌더 결함 {label}"
        if not isinstance(n, int):
            steps.append((name, False, f"수치 없음(totals.{key}) — 계수 실패(눈먼 0 방지)"))
            continue
        entry = kv.get(f"render_{key}")
        baseline = 0
        if entry is not None and waiver_entry_valid(entry) and isinstance(entry.get("count"), int):
            baseline = entry["count"]
            waivers.append(f"render_{key}(count {baseline} · {entry.get('date')})")
        if n > baseline:
            steps.append((name, False,
                          f"{n}건 > 베이스라인 {baseline} — 화면을 고쳐 재측정하거나 "
                          f"계약 waiver 'render_{key}'의 count를 사유와 함께 갱신하라"))
        elif n:
            steps.append((name, True, f"{n}건 ≤ waiver {baseline} — 등재 강등(렌더 WARN으로 센다)"))
            demoted += 1
        elif baseline:
            steps.append((name, True, f"0건 ≤ waiver {baseline} — 개선됨: waiver를 내리거나 삭제 가능"))
    ff = (typo.get("fontFloor") or {}).get("count")
    tr = (typo.get("tracking") or {}).get("count")
    cl = (typo.get("nearMissAnchors") or {}).get("dominantClashTotal")
    if all(isinstance(v, int) for v in (ff, tr, cl)):
        warn_render: int | None = ff + tr + cl + demoted
        steps.append(("렌더 WARN 계수", True,
                      f"폰트하한위반 {ff} · 자간보정누락 {tr} · 정렬지배값충돌 {cl} · "
                      f"waiver 강등 {demoted} → 렌더 WARN {warn_render}"))
    else:
        warn_render = None
        steps.append(("렌더 WARN 계수", False,
                      "타이포 수치 누락(fontFloor/tracking/dominantClashTotal) — 계수 실패(눈먼 0 방지)"))
    return steps, warn_render, waivers


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
        # ── P1(2026-08-17) 구조 WARN 래칫 — «세어지지 않는 WARN은 침묵과 같다» ──
        #   waiver 강등분을 포함한 구조 WARN 총계를 요약 최상단에 노출하고,
        #   계약 warn_baseline 대비 증가하면 그 자체를 FAIL로 잡는다.
        self.warn_struct: int | None = 0     # verify_deck·verify_notes (None=계수 실패)
        # 배치4(2026-08-17): 품질 WARN도 래칫 대상 — 게이트 임계·강등은 여전히
        # verify_deck_quality 소관(WARN 기본·프로필 §3-G)이고, 러너는 «총계의 조용한
        # 증가»만 막는다(D-2: 기존은 봐주고 신규만 잡는다).
        self.warn_quality = 0                # verify_deck_quality (warn_baseline.quality 래칫)
        # P4(배치3): 렌더 WARN(타이포·정렬 + waiver 강등분) — warn_baseline.render 래칫 대상
        self.warn_render: int | None = 0
        self._render_measured = False        # 증거가 유효해 수치 판정까지 간 경우에만 래칫
        self.waivers_applied: list[str] = []
        self._last_out = ""

    def _contract(self) -> dict:
        path = find_deck_contract(self.deck)
        if path is None:
            return {}
        try:
            with open(path, encoding="utf-8") as fh:
                return json.load(fh)
        except Exception:
            return {}

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
        self._last_out = proc.stdout or ""
        self.steps.append((name, ok, "" if ok else f"exit {proc.returncode}"))
        return ok

    def _count_summary_warns(self, gate_label: str, bucket: str) -> None:
        """직전 _py 출력의 «요약: FAIL n · WARN n» 줄에서 WARN을 센다.
        줄이 없으면 계수 실패를 FAIL로 남긴다 — 조용한 0은 눈먼 0이다."""
        m = _SUMMARY_RE.search(self._last_out)
        if not m:
            self.steps.append((f"{gate_label} WARN 계수", False,
                               "«요약:» 줄을 찾지 못해 WARN을 세지 못했다"))
            if bucket == "struct":
                self.warn_struct = None
            return
        n = int(m.group(2))
        if bucket == "struct":
            if self.warn_struct is not None:
                self.warn_struct += n
        else:
            self.warn_quality += n

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
        self._count_summary_warns("verify_deck", "struct")
        ok &= self._py("내용 품질 (verify_deck_quality)", "verify_deck_quality.py", _rel(self.deck))
        self._count_summary_warns("verify_deck_quality", "quality")
        kv = self._contract().get("known_violations") or {}
        if os.path.exists(self.notes):
            name = "발표자 노트 (verify_notes)"
            ok_notes = self._py(name, "verify_notes.py", _rel(self.deck), _rel(self.notes))
            if self.warn_struct is not None:
                self.warn_struct += len(re.findall(r"(?m)^\[WARN\]", self._last_out))
            if not ok_notes:
                # notes_pn_mismatch waiver 소비 — 등재만 되고 소비처가 없어 verify_notes가
                # 상시 FAIL하던 것을 러너 count 래칫으로 잇는다(P1 · 2026-08-17).
                # 실측 MISMATCH가 waiver count 이하일 때만 강등하고, 초과분은 FAIL이다.
                m = re.search(r"--- MISMATCH=(\d+)", self._last_out)
                entry = kv.get("notes_pn_mismatch")
                if (m and entry is not None and waiver_entry_valid(entry)
                        and isinstance(entry.get("count"), int)
                        and int(m.group(1)) <= entry["count"]):
                    self.steps[-1] = (name, True,
                                      f"MISMATCH {m.group(1)}건 ≤ waiver notes_pn_mismatch "
                                      f"count {entry['count']}({entry.get('date')}) — 등재 강등")
                    self.waivers_applied.append(
                        f"notes_pn_mismatch(count {entry['count']} · {entry.get('date')})")
                    if self.warn_struct is not None:
                        self.warn_struct += 1   # 강등도 WARN으로 센다 — 침묵 금지
                else:
                    ok = False
        else:
            self.steps.append(("발표자 노트", True, "노트 없음 — 건너뜀"))
        ok &= self._draft_gates(kv)
        return ok

    # ── P1(2026-08-17) 초안 생존·동기화 게이트 편입 ──────────────────────
    #   기제3(게이트 OFF 기본값)의 두 사례를 러너로 끌어온다. 판정은 러너가
    #   한다: 실측 건수를 계약 waiver의 count 베이스라인과 비교해 «증가»만
    #   FAIL한다(waiver 없으면 베이스라인 0 = 1건이라도 FAIL). 스크립트의
    #   --strict는 단독 실행·테스트용으로 남는다.
    def _draft_gates(self, kv: dict) -> bool:
        ok = True
        for label, script, wkey, count_re in (
            ("초안 제목 생존 (check_title_survival)", "check_title_survival.py",
             "title_survival_baseline", r"제목 강등 (\d+)건"),
            ("초안-덱 동기화 (report_draft_sync)", "report_draft_sync.py",
             "draft_sync_baseline", r"초안에만=(\d+) 덱에만=(\d+)"),
            # P5(배치4 · 2026-08-17): 보고·결정표 신선도 — 기제6(보고 노후화) 차단.
            # 출구 두 개(재조립 후 식별자 갱신 / 시점 스냅샷 선언)는 스크립트 docstring 참조.
            ("보고 신선도 (verify_report_freshness)", "verify_report_freshness.py",
             "report_freshness_baseline", r"신선도 위반 (\d+)건"),
        ):
            self._py(label, script, self.num)
            out = self._last_out
            # 입력없음(초안·덱 부재) — 판정 불가를 명시하고 넘어간다
            if ("[입력없음]" in out) or ("파일 없음" in out):
                self.steps[-1] = (label, True, "초안/덱 없음 — 건너뜀(판정 아님)")
                continue
            m = re.search(count_re, out)
            if not m:
                self.steps[-1] = (label, False, "건수 줄을 찾지 못했다 — 계수 실패(눈먼 0 방지)")
                ok = False
                continue
            n = sum(int(g) for g in m.groups())
            entry = kv.get(wkey)
            baseline = 0
            if entry is not None and waiver_entry_valid(entry) and isinstance(entry.get("count"), int):
                baseline = entry["count"]
                self.waivers_applied.append(f"{wkey}(count {baseline} · {entry.get('date')})")
            if n > baseline:
                self.steps[-1] = (label, False,
                                  f"드리프트 {n}건 > 베이스라인 {baseline} — 소유권을 판정해 "
                                  f"맞추거나 계약 waiver '{wkey}'의 count를 사유와 함께 갱신하라")
                ok = False
            else:
                note = f"드리프트 {n}건 ≤ 베이스라인 {baseline}"
                if n < baseline:
                    note += f" — 개선됨: 베이스라인을 {n}으로 낮춰 등재 가능"
                self.steps[-1] = (label, True, note)
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
        # ★ 밀도 — 「박스로 화면을 채웠는가」를 보는 축. 종전 압축본에는 이 수치가
        #   하나도 실리지 않아, 러너를 통과해도 저밀도를 판정할 근거가 없었다.
        dens = (d.get("render") or {}).get("density") or {}
        ink = dens.get("ink") or {}
        n_slides_i = n_slides or 1
        bh = dens.get("boxHeavyNoVisualCount", "?")
        line3 = (f"밀도 — 잉크 중앙값 {ink.get('median')} (하위10% {ink.get('p10')}) · "
                 f"★박스4개↑+시각자료0 {bh}장 · 저밀도상자 {(r.get('sparse'))} · "
                 f"빈상자 {r.get('hollow')}(배지 {r.get('hollowBadge')} 제외)")
        print(f"\n=== 렌더·타이포 감사 (audit_all) ===\n  {line1}\n  {line2}\n  {line3}")
        for o in ((d.get("render") or {}).get("offenders") or [])[:8]:
            print(f"    · {o.get('id')}: " + " ".join(map(str, o.get("d") or [])))
        # ★ 「사람이 다시 볼 자리」 — 임계로 막지 않고 이름으로 지목한다.
        #   판정이 아니라 보고다. 저밀도 자체는 결함이 아니고, 의도된 것인지
        #   아닌지는 사람이 가른다(R-DENS-03).
        # ⚠️ 목록은 감사기가 상한을 두고 자른다. **자른 사실을 반드시 밝힌다** —
        #   「20장」으로 찍히면 실제 51장이 20장으로 읽힌다. 조용한 절단이
        #   「다 봤다」로 읽히는 것이 이 저장소가 반복해서 겪은 실패다.
        for label, key, count_key, fmt in (
            ("박스만 있고 시각자료가 없는 장", "boxHeavyNoVisual", "boxHeavyNoVisualCount",
             lambda r: f"{r[0]}  박스 {r[1]} · 잉크 {r[2]}"),
            ("잉크는 낮은데 박스는 많은 장(큰 빈 상자 의심)", "lowInkManyBoxes", None,
             lambda r: f"{r[0]}  잉크 {r[1]} · 박스 {r[2]}"),
            ("교시 로드맵인데 시각자료 0", "roadmapNoVisual", None,
             lambda r: f"{r[0]}  박스 {r[1]}"),
            ("껍데기 상자가 2개 이상인 장", "hollowSlides", None,
             lambda r: f"{r[0]}  빈상자 {r[1]}"),
            ("정보 모양의 1순위가 시각물인데 시각자료 0", "visualShapeNoVisual", None,
             lambda r: f"{r[0]}  모양 {r[1]} · 박스 {r[2]}"),
            ("이 덱에서 가장 얇은 장(상대값·기준 미달 아님)", "thinnest", None,
             lambda r: f"{r[0]}  잉크 {r[1]} · 박스 {r[2]} · 시각 {r[3]} · 글자 {r[4]}"),
        ):
            rows = dens.get(key) or []
            if not rows:
                continue
            total = dens.get(count_key) if count_key else None
            shown = min(5, len(rows))
            head = f"    ★ {label}: {total if total is not None else len(rows)}장"
            hidden = (total if total is not None else len(rows)) - shown
            if hidden > 0:
                head += f" (아래 {shown}장만 표시 · {hidden}장 생략)"
            print(head)
            for row in rows[:5]:
                print(f"       · {fmt(row)}")
        # ⚠️ 「측정 불가」를 「0건」으로 읽지 않게 명시한다.
        cov = dens.get("shapeCoverage")
        if isinstance(cov, list) and len(cov) == 2:
            got, tot = cov
            if tot and got == 0:
                print(f"    ⚠️ 정보 모양 기록 0/{tot}장 — 「모양 대비 시각자료」 신호는 "
                      f"**측정 불가**다(0건이 아니다). 슬라이드에 data-shape를 적어라(R-BOX-01b).")
            elif tot and got < tot:
                print(f"    ⚠️ 정보 모양 기록 {got}/{tot}장 — 나머지 {tot - got}장은 "
                      f"「모양 대비 시각자료」 신호의 검사 밖이다.")
        if isinstance(bh, int) and bh:
            print(f"       → 사람이 다시 본다(R-BOX-01·R-DENS-03). 비교: "
                  f"python scripts/compare_baseline_panel.py {self.num}")
        self.steps.append(("렌더·타이포 감사", True, line1 + " / " + line2 + " / " + line3))

        # ── P4(배치3 · 2026-08-17) 렌더 수치 판정 ──
        # 종전의 «수치 자체로는 FAIL시키지 않는다»는 이 지점에서 폐기됐다(ANALYSIS
        # §2-기제3·5 — 수치는 산출되는데 게이트가 안 쓰는 상태가 기제3의 한 사례였다).
        # WARN 시작 규율은 타이포·정렬류에만 남고, 결함형 6종은 waiver 없으면 0이 계약이다.
        # 밀도(density) 계열은 계속 판정하지 않는다 — 저밀도가 의도인지는 사람이 가른다(R-DENS-03).
        v_steps, warn_render, v_waivers = numeric_verdicts(
            r, t, self._contract().get("known_violations") or {})
        self.steps.extend(v_steps)
        self.waivers_applied.extend(v_waivers)
        self.warn_render = warn_render
        self._render_measured = True
        return all(ok for _n, ok, _m in v_steps)

    def report(self, ran_static: bool, ran_render: bool) -> int:
        """⚠️ 이 함수의 성공 메시지를 «항상 같은 문자열»로 두지 마라.
        독립 검증(2026-08-03)이 잡은 결함: 종전에는 어떤 플래그로 돌렸든
        「정적 게이트 + 렌더 증거 모두 확인」을 출력했다. `--render-only`로
        정적 게이트를 건너뛴 실행도 그 문구와 함께 exit 0을 냈다 —
        **부분 실행이 완전 통과로 읽히는** 정확히 그 실패 유형이다."""
        print("\n" + "=" * 68)
        print(f"러너 요약 — {self.week}")
        print("=" * 68)
        # ── 구조 WARN 래칫(P1) — 최상단 노출. 세어지지 않는 WARN은 침묵과 같다 ──
        if ran_static:
            wb = self._contract().get("warn_baseline") or {}
            base = wb.get("static_gates")
            ws = "계수실패" if self.warn_struct is None else self.warn_struct
            base_q = wb.get("quality")
            print(f"경고 — 구조 WARN {ws}"
                  + (f" (베이스라인 {base} · {wb.get('date')})" if isinstance(base, int)
                     else " (베이스라인 미등재)")
                  + f" · 품질 WARN {self.warn_quality}"
                  + (f" (베이스라인 {base_q})" if isinstance(base_q, int)
                     else " (베이스라인 미등재)"))
            if self.waivers_applied:
                print("waiver 적용 " + str(len(self.waivers_applied)) + "건: "
                      + " · ".join(self.waivers_applied))
            if self.warn_struct is None:
                self.steps.append(("구조 WARN 래칫", False, "WARN 계수 실패 — 위 계수 단계 참조"))
            elif not isinstance(base, int):
                self.steps.append(("구조 WARN 래칫", False,
                                   f"계약에 warn_baseline 미등재 — 실측 {self.warn_struct}을 "
                                   f"{{\"static_gates\": N, \"date\": \"YYYY-MM-DD\"}}로 등재하라"))
            elif self.warn_struct > base:
                self.steps.append(("구조 WARN 래칫", False,
                                   f"구조 WARN 증가 {base} → {self.warn_struct} — 원인을 없애거나 "
                                   f"베이스라인을 사유와 함께 갱신하라(조용한 증가 금지)"))
            else:
                note = f"구조 WARN {self.warn_struct} ≤ 베이스라인 {base}"
                if self.warn_struct < base:
                    note += f" — 개선됨: 베이스라인을 {self.warn_struct}로 낮춰 등재 가능"
                self.steps.append(("구조 WARN 래칫", True, note))
            # ── 품질 WARN 래칫(배치4 · 2026-08-17) — D-2 «기존은 봐주고 신규만 잡는다» ──
            #    규칙 임계(프로필 §3-G 상한 0)는 불변이다: 새 과목은 처음부터 임계 0으로
            #    시작하고, 이 래칫은 이 주차 총계의 조용한 증가만 막는다.
            if not isinstance(base_q, int):
                self.steps.append(("품질 WARN 래칫", False,
                                   f"계약에 warn_baseline.quality 미등재 — 실측 {self.warn_quality}을 "
                                   f"사유(분해)와 함께 등재하라"))
            elif self.warn_quality > base_q:
                self.steps.append(("품질 WARN 래칫", False,
                                   f"품질 WARN 증가 {base_q} → {self.warn_quality} — 원인을 없애거나 "
                                   f"베이스라인을 사유와 함께 갱신하라(조용한 증가 금지)"))
            else:
                note_q = f"품질 WARN {self.warn_quality} ≤ 베이스라인 {base_q}"
                if self.warn_quality < base_q:
                    note_q += f" — 개선됨: 베이스라인을 {self.warn_quality}로 낮춰 등재 가능"
                self.steps.append(("품질 WARN 래칫", True, note_q))
        # ── 렌더 WARN 래칫(P4) — 증거가 유효해 수치 판정까지 간 경우에만 ──
        #    (증거 부재·무효면 그 단계가 이미 FAIL이라 래칫으로 겹쳐 잡지 않는다)
        if ran_render and self._render_measured:
            wbm = self._contract().get("warn_baseline") or {}
            base_r = wbm.get("render")
            wr = "계수실패" if self.warn_render is None else self.warn_render
            print(f"경고 — 렌더 WARN {wr}"
                  + (f" (베이스라인 {base_r} · {wbm.get('date')})" if isinstance(base_r, int)
                     else " (베이스라인 미등재)"))
            if self.warn_render is None:
                self.steps.append(("렌더 WARN 래칫", False, "계수 실패 — 위 «렌더 WARN 계수» 단계 참조"))
            elif not isinstance(base_r, int):
                self.steps.append(("렌더 WARN 래칫", False,
                                   f"계약에 warn_baseline.render 미등재 — 실측 {self.warn_render}을 "
                                   f"warn_baseline에 \"render\": N으로 등재하라(date 갱신 포함)"))
            elif self.warn_render > base_r:
                self.steps.append(("렌더 WARN 래칫", False,
                                   f"렌더 WARN 증가 {base_r} → {self.warn_render} — 원인을 없애거나 "
                                   f"베이스라인을 사유와 함께 갱신하라(조용한 증가 금지)"))
            else:
                note = f"렌더 WARN {self.warn_render} ≤ 베이스라인 {base_r}"
                if self.warn_render < base_r:
                    note += f" — 개선됨: 베이스라인을 {self.warn_render}로 낮춰 등재 가능"
                self.steps.append(("렌더 WARN 래칫", True, note))
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
