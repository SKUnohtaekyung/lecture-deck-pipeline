# -*- coding: utf-8 -*-
"""조립본(또는 다른 덱 HTML)의 전 장을 1280×720으로 찍는다 — 가독성 독립 검토용.

    python plans/세컨브레인-특강/tools/shoot_slides.py [--deck 강의덱.html] [--only ID ...]

· 저장소 루트에서 `python -m http.server 8799`가 안 떠 있으면 이 스크립트가 띄웠다가 끝에 끈다(떠 있으면 건드리지 않는다).
· 주소는 `?audit=1`(연출 없이 최종 상태 · --scale 1 고정)로 연다.
· 이동은 `window.__deckShow(i)`가 있고 0·1번 장에서 맞게 동작하면 그것을 쓰고, 아니면 Home → ArrowRight 키로 한다.
  어느 쪽이든 장마다 `.slide.is-active[data-slide]`가 기대한 ID인지 확인한다 — 틀린 장은 저장하되 「이동 불일치」로 센다.
· 저장: tmp/sb/V21-T/shots/NN_<ID>.png (NN = 1부터 쪽 번호). 같은 이름은 덮어쓴다(지우지 않는다).
· 보고: 「RESULT 장 N · 저장 M · 이동 불일치 K · 디렉터리 PNG P」. 장 수 = 저장 수이고 불일치 0이어야 exit 0.
종료코드: 0 전 장 저장 · 1 저장 수 부족/불일치/페이지 오류 · 2 환경 오류(playwright 없음 · 서버 실패).
"""
from __future__ import annotations

import argparse
import re
import socket
import subprocess
import sys

sys.dont_write_bytecode = True   # 저장소에 __pycache__를 남기지 않는다
import time
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_REL = "courses/세컨브레인_특강/sessions/1주차/강의덱.html"
DEFAULT_OUT = ROOT / "tmp" / "sb" / "V21-T" / "shots"
PORT = 8799


def port_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.4)
        return s.connect_ex(("127.0.0.1", port)) == 0


def start_server(port: int):
    """서버가 이미 있으면 (None, True), 없으면 띄워서 (proc, False)."""
    if port_open(port):
        return None, True
    proc = subprocess.Popen([sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"], cwd=ROOT,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(40):
        if port_open(port):
            return proc, False
        if proc.poll() is not None:
            break
        time.sleep(0.15)
    proc.terminate()
    raise RuntimeError("http.server %d를 띄우지 못했다(다른 프로세스가 점유 중일 수 있다)" % port)


ACTIVE_JS = "() => { const a = document.querySelector('.slide.is-active'); return a ? (a.getAttribute('data-slide') || '') : null; }"


def main(argv=None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--deck", default=DEFAULT_REL, help="저장소 루트 기준 덱 경로(기본: 조립본)")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--port", type=int, default=PORT)
    ap.add_argument("--query", default="audit=1")
    ap.add_argument("--only", nargs="*", help="이 ID들만 찍는다(전수 보고는 하지 않는다)")
    ap.add_argument("--keyboard", action="store_true", help="__deckShow가 있어도 키보드(Home → →)로 이동한다")
    ap.add_argument("--timeout", type=float, default=4.0, help="장 이동 확인 대기(초)")
    a = ap.parse_args(argv)

    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:  # pragma: no cover
        print("[ENV] playwright를 불러오지 못했다: %s" % exc)
        return 2

    deck_rel = a.deck.replace("\\", "/")
    if not (ROOT / deck_rel).is_file():
        print("[FAIL] 덱 파일이 없다: %s" % deck_rel)
        return 1
    try:
        proc, preexisting = start_server(a.port)
    except RuntimeError as exc:
        print("[ENV] %s" % exc)
        return 2
    url = "http://localhost:%d/%s?%s" % (a.port, quote(deck_rel), a.query)
    print("서버 %s · %s" % ("기존 것 사용" if preexisting else "이 스크립트가 띄움", url))

    a.out.mkdir(parents=True, exist_ok=True)
    saved: list[str] = []
    mismatch: list[str] = []
    page_errors: list[str] = []
    nav_mode = "?"
    ids: list[str] = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            ctx = browser.new_context(viewport={"width": 1280, "height": 720}, device_scale_factor=1)
            page = ctx.new_page()
            page.on("pageerror", lambda e: page_errors.append(str(e)[:160]))
            page.goto(url, wait_until="load")
            try:
                page.evaluate("() => document.fonts.ready")
            except Exception:
                pass
            ids = page.evaluate("() => Array.from(document.querySelectorAll('section.slide')).map((s, i) => s.getAttribute('data-slide') || ('slide-' + (i + 1)))")
            n = len(ids)
            if not n:
                print("[FAIL] section.slide를 하나도 찾지 못했다(미판정 — 통과 아님)")
                browser.close()
                return 1

            def wait_active(want: str) -> bool:
                try:
                    page.wait_for_function("w => { const a = document.querySelector('.slide.is-active'); return !!a && (a.getAttribute('data-slide') || '') === w; }",
                                           arg=want, timeout=a.timeout * 1000)
                    return True
                except Exception:
                    return False

            has_show = page.evaluate("() => typeof window.__deckShow === 'function'")
            use_show = False
            if has_show and n > 1 and not a.keyboard:
                page.evaluate("() => window.__deckShow(1)")
                ok1 = wait_active(ids[1])
                page.evaluate("() => window.__deckShow(0)")
                ok0 = wait_active(ids[0])
                use_show = ok0 and ok1
            nav_mode = "__deckShow(i)" if use_show else ("키보드(Home → →)" + (" · __deckShow는 있으나 " + ("--keyboard 지정" if a.keyboard else "0/1번 확인 실패") if has_show else " · __deckShow 없음"))
            print("이동 방식: %s · 장 %d" % (nav_mode, n))

            if not use_show:
                page.keyboard.press("Home")
                wait_active(ids[0])
            want_idx = [i for i, sid in enumerate(ids) if not a.only or sid in a.only]
            if a.only:
                missing = [x for x in a.only if x not in ids]
                if missing:
                    print("[FAIL] --only ID가 덱에 없다: %s" % ", ".join(missing))
                    browser.close()
                    return 1
            for i in range(n):
                sid = ids[i]
                if use_show:
                    if i in want_idx:
                        page.evaluate("i => window.__deckShow(i)", i)
                elif i > 0:
                    page.keyboard.press("ArrowRight")
                if i not in want_idx:
                    if not use_show:
                        wait_active(sid)
                    continue
                if not wait_active(sid):
                    mismatch.append("%02d_%s(활성: %s)" % (i + 1, sid, page.evaluate(ACTIVE_JS)))
                page.wait_for_timeout(120)      # 글꼴·포스터 이미지 배치
                path = a.out / ("%02d_%s.png" % (i + 1, re.sub(r"[^\w.-]", "_", sid)))
                page.screenshot(path=str(path), full_page=False)
                saved.append(path.name)
            browser.close()
    except Exception as exc:
        print("[FAIL] 촬영 중 예외: %s: %s" % (type(exc).__name__, str(exc).splitlines()[0][:200]))
        return 1
    finally:
        if proc is not None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except Exception:
                proc.kill()

    target = len(want_idx)
    on_disk = len(list(a.out.glob("*.png")))
    print("RESULT 장 %d · 대상 %d · 저장 %d · 이동 불일치 %d · 페이지 오류 %d · 디렉터리 PNG %d%s" % (
        len(ids), target, len(saved), len(mismatch), len(page_errors), on_disk,
        "" if on_disk == len(saved) else " (이번에 찍지 않은 PNG가 섞여 있다)"))
    if mismatch:
        print("  이동 불일치(%d): %s" % (len(mismatch), ", ".join(mismatch[:12])))
    for e in page_errors[:3]:
        print("  pageerror: " + e)
    print("  저장 위치: %s" % (a.out.relative_to(ROOT) if a.out.is_relative_to(ROOT) else a.out))
    return 0 if (len(saved) == target and not mismatch) else 1


if __name__ == "__main__":
    sys.exit(main())
