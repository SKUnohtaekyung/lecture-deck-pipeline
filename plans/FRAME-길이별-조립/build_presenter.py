# -*- coding: utf-8 -*-
"""4시간 덱의 배포본과 발표본을 한 번에 다시 만든다.

    python plans/FRAME-길이별-조립/build_presenter.py

순서
  1) assemble_deck.py        조각 → 강의덱.html
  2) inline_deck.py --offline 강의덱.html → 강의덱_배포.html(단일 파일)
       shell.html의 D2Coding 웹 글꼴 링크는 오프라인 묶음에 넣을 수 없어, 임시 사본에서 그 한 줄을 빼고 묶는다.
       (요청문 글꼴은 기기의 기본 고정폭 글꼴로 보인다. `build_release.py`는 이 링크에서 멈춘다.)
  3) verify_distributable.py  배포본 자립성
  4) build_presenter_notes.py 1주차_발표노트.md → 강의덱_발표노트.html(간결한 노트)
  5) inject_presenter.py      배포본 + 간결한 노트 → 강의덱_발표.html
verify_deck.py(구조 검증)는 돌리지 않는다 — 2026-10-06 「검사기 보류」 결정.
종료코드: 0 전부 통과 · 1 어느 단계든 실패(그 단계에서 멈춘다).
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = os.path.join(ROOT, "courses", "AI_에이전트_실습워크숍_4시간", "sessions", "1주차")
META = os.path.join(ROOT, "courses", "AI_에이전트_실습워크숍_4시간", "sessions", "_verify", "1주차", "강의덱_발표.meta.json")
DECK_ID = "workshop-4h-diagnostic"
FONT_LINK = '  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/wan2land/d2coding/d2coding-full.css">'


def run(*args):
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable] + list(args), cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
    tail = [x for x in (r.stdout + r.stderr).splitlines() if x.strip() and "asset inline" not in x and "CSS inline" not in x][-4:]
    print("  exit %d · %s" % (r.returncode, os.path.basename(args[0])))
    for x in tail: print("    " + x[:200])
    return r.returncode


def main():
    deck, dist, pres = (os.path.join(S, n) for n in ("강의덱.html", "강의덱_배포.html", "강의덱_발표.html"))
    tmp = os.path.join(S, "강의덱.__bundle.html")
    if run("scripts/assemble_deck.py", os.path.join(S, "강의덱.초안")): return 1
    html = open(deck, encoding="utf-8", newline="").read()
    if html.count(FONT_LINK) != 1:
        print("  D2Coding 링크를 찾지 못했다(shell.html이 바뀌었는지 확인)"); return 1
    open(tmp, "w", encoding="utf-8", newline="").write(html.replace(FONT_LINK + "\r\n", "").replace(FONT_LINK + "\n", ""))
    try:
        if run("scripts/inline_deck.py", tmp, "--offline", "--output", dist): return 1
    finally:
        if os.path.exists(tmp): os.remove(tmp)
    if run("scripts/verify_distributable.py", dist): return 1
    if run("plans/FRAME-길이별-조립/build_presenter_notes.py"): return 1
    if run("scripts/inject_presenter.py", dist, "--notes", os.path.join(S, "강의덱_발표노트.html"), "--deck-id", DECK_ID, "--output", pres, "--meta", META, "--force"): return 1
    print("RESULT 배포본 %dKB · 발표본 %dKB" % (os.path.getsize(dist) // 1024, os.path.getsize(pres) // 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main())
