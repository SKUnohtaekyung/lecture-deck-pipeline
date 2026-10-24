# -*- coding: utf-8 -*-
"""세컨브레인 특강 1주차 — 조립 → 배포본 → 노트 HTML → 발표본 → 검증, 한 명령.

    python plans/세컨브레인-특강/tools/build_presenter.py [--skip-assemble]

단계(하나라도 실패하면 그 단계에서 멈추고 exit 1 · 실패 단계는 출력 마지막 40줄을 그대로 보인다)
  1 assemble_deck.py        강의덱.초안 → 강의덱.html            (--skip-assemble이면 건너뛰고 기존 조립본을 쓴다)
  2 inline_deck.py --offline 강의덱.html → 강의덱_배포.html        (영상 · 글꼴 · 이미지 인라인)
  3 build_presenter_notes.py 발표노트 md → 강의덱_발표자노트.html   (노트 있음/없음/덱에 없는 노트 계수)
  4 inject_presenter.py      배포본 + 노트 → 강의덱_발표.html + 사이드카 meta.json  (--force: 이전 산출물을 덮는다)
  5 verify_presenter_deck.py 배포본 ↔ 발표본 불변성 · 마커 · 노드 수

덱이나 노트를 고치면 발표본까지 다시 만든다(디자인 정본 §17). 이 도구는 kit·scripts를 고치지 않는다.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys

sys.dont_write_bytecode = True   # 저장소에 __pycache__를 남기지 않는다
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
S = ROOT / "courses" / "세컨브레인_특강" / "sessions" / "1주차"
META = ROOT / "courses" / "세컨브레인_특강" / "sessions" / "_verify" / "1주차" / "강의덱_발표.meta.json"
DRAFT = S / "강의덱.초안"
DECK = S / "강의덱.html"
DIST = S / "강의덱_배포.html"
NOTES_HTML = S / "강의덱_발표자노트.html"
PRES = S / "강의덱_발표.html"
DECK_ID = "secondbrain-week1"
TOOLS = Path(__file__).resolve().parent

NOISE = ("asset inline", "CSS inline")        # 성공 때 줄 수만 늘리는 인라인 진행 줄
KEEP = ("RESULT", "[PASS]", "[FAIL]", "[WARN]", "PASS", "FAIL", "WARN", "요약", "written", "노트 ", "자기검증", "건너뜀", "슬라이드", "사이드카")


def rel(p: Path) -> str:
    try:
        return str(p.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(p)


def run(label: str, *args) -> tuple[int, list[str]]:
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
    t0 = time.time()
    r = subprocess.run([sys.executable] + [str(a) for a in args], cwd=ROOT, env=env,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    lines = [x.rstrip() for x in (r.stdout + "\n" + r.stderr).splitlines() if x.strip()]
    print("[%s] exit %d · %.1fs · %s" % (label, r.returncode, time.time() - t0, Path(str(args[0])).name))
    if r.returncode != 0:
        for x in lines[-40:]:            # 원인 줄을 그대로 보인다
            print("    " + x[:300])
    else:
        shown = [x for x in lines if not any(n in x for n in NOISE) and "✓" not in x]   # 개별 통과 줄은 「요약」이 대신한다
        judged = [x for x in shown if any(k in x for k in KEEP)] or shown[-3:]
        for x in judged[-12:]:
            print("    " + x[:240])
    return r.returncode, lines


def main(argv=None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--skip-assemble", action="store_true", help="1단계를 건너뛰고 기존 강의덱.html을 쓴다")
    a = ap.parse_args(argv)

    codes: list[str] = []

    def fail(label: str) -> int:
        print("RESULT 실패 — %s에서 멈춤 · 단계별 종료코드 %s" % (label, " ".join(codes)))
        return 1

    # 1 조립
    if a.skip_assemble:
        if not DECK.is_file():
            print("[1 조립] 건너뛰려 했지만 조립본이 없다: %s" % rel(DECK))
            codes.append("1:없음")
            return fail("1 조립")
        newest = max((p.stat().st_mtime for p in DRAFT.rglob("*") if p.is_file()), default=0)
        stale = newest > DECK.stat().st_mtime
        print("[1 조립] 건너뜀(--skip-assemble) · 기존 %s 사용%s" % (
            rel(DECK), " · WARN: 조각이 조립본보다 새롭다 — 조립본이 낡았을 수 있다" if stale else ""))
        codes.append("1:skip")
    else:
        rc, _ = run("1 조립", ROOT / "scripts" / "assemble_deck.py", DRAFT)
        codes.append("1:%d" % rc)
        if rc:
            return fail("1 조립")

    # 2 배포본
    rc, _ = run("2 배포본", ROOT / "scripts" / "inline_deck.py", DECK, "--offline", "--output", DIST)
    codes.append("2:%d" % rc)
    if rc:
        return fail("2 배포본(inline_deck --offline)")

    # 3 노트 HTML
    rc, note_lines = run("3 노트", TOOLS / "build_presenter_notes.py", "--deck", DECK, "--output", NOTES_HTML)
    codes.append("3:%d" % rc)
    if rc:
        return fail("3 노트")

    # 4 발표본
    rc, _ = run("4 발표본", ROOT / "scripts" / "inject_presenter.py", DIST, "--notes", NOTES_HTML,
                "--deck-id", DECK_ID, "--output", PRES, "--meta", META, "--force")
    codes.append("4:%d" % rc)
    if rc:
        return fail("4 발표본(inject_presenter)")

    # 5 검증
    rc, _ = run("5 검증", ROOT / "scripts" / "verify_presenter_deck.py", "--source", DIST, "--presenter", PRES, "--meta", META)
    codes.append("5:%d" % rc)
    if rc:
        return fail("5 검증(verify_presenter_deck)")

    summary = next((x.strip() for x in note_lines if x.startswith("RESULT")), "RESULT 노트 계수 줄을 읽지 못함(미판정)")
    print("RESULT 통과 · 배포본 %dKB · 발표본 %dKB · 단계별 종료코드 %s" % (
        DIST.stat().st_size // 1024, PRES.stat().st_size // 1024, " ".join(codes)))
    print("  노트: " + summary.replace("RESULT ", "", 1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
