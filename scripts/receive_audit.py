#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""렌더 감사 JSON 1회용 POST 수신기 — 브라우저 콘솔 출력을 바이트 그대로 저장한다.

왜
--
`audit_all.js` 출력(9KB+ 이스케이프 문자열)을 콘솔에서 손으로 옮겨 적으면 전사
오류 위험이 있다. 이 수신기는 요청 1건을 받아 `<증거루트>/<주차>/deck-audit.json`
(증거루트 = 과목이 `courses/<과목>/sessions/_verify/`를 선언했으면 그것, 아니면
`sessions/_verify/`)에 그대로 쓰고 즉시 종료한다(상시 서버 아님 · CORS 허용 헤더 포함 — 덱을 서빙하는
8799 오리진에서 fetch로 보낼 수 있다). 절차 정본: references/검증-명령-지도.md §3.

사용
----
    python scripts/receive_audit.py <주차> [--port 8798]     # 백그라운드로 띄운다
    # 브라우저 콘솔에서:
    #   await fetch('http://localhost:8798/', {method:'POST', body: window.__audit})
저장 후 스스로 schema·INVALID를 검사해 결과를 출력한다(최종 판정은 run_deck_checks).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)
try:
    import _course_paths
except Exception:                                # 해석기를 못 읽으면 구경로
    _course_paths = None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("week", help="주차 (예: 1주차) — <증거루트>/<주차>/deck-audit.json 에 저장 (증거루트는 과목별 · 실제 경로는 [대기]/[저장] 줄에 찍힌다)")
    ap.add_argument("--port", type=int, default=8798)
    a = ap.parse_args()

    week = a.week if a.week.endswith("주차") else f"{a.week}주차"
    if _course_paths is None:
        out_dir = os.path.join(ROOT, "sessions", "_verify", week)
    else:
        out_dir, warn = _course_paths.verify_dir_or_legacy(week, ROOT)
        if warn:
            # 과목 미지정 — 종전과 같은 구경로로 가되 **조용히 가지 않는다**.
            print(f"[경고] 과목을 특정하지 못해 구경로로 진행한다: {warn}")
            print(f"       권장: {_course_paths.COURSE_ENV}=<과목명> 을 지정하라")
    out_path = os.path.join(out_dir, "deck-audit.json")

    # ⚠️ 이 스크립트는 **덮어쓴다**(아래 wb). 그래서 쓰기 전에 «덮어쓸 파일이
    #    누구 것인가»를 묻는다. «마커를 선언했는가»가 아니라 **실소유**로 가른다 —
    #    마커 부재를 위험으로 보면 마커를 선언한 적 없는 기존 과목이 전부 멈춘다.
    if _course_paths is not None and os.path.exists(out_path):
        try:
            cur = _course_paths.resolve_course(None, ROOT)
        except _course_paths.AmbiguousCourseError:
            cur = None
        cur_name = os.path.basename(cur) if cur else None
        owner = _course_paths.evidence_owner(out_path)
        if owner and cur_name and owner != cur_name:
            print("[중단] 덮어쓰려는 증거는 «%s»의 덱을 잰 것이고, 이 실행은 «%s»다:\n"
                  "         %s\n"
                  "       그대로 쓰면 다른 과목의 측정분이 소실된다(복구 근거는 git뿐).\n"
                  "       이 과목의 증거 namespace를 먼저 선언하라:\n"
                  "         courses/%s/sessions/_verify/   (용도를 적은 README.md 1개)"
                  % (owner, cur_name, os.path.relpath(out_path, ROOT), cur_name))
            return 2
        if owner is None:
            print("[경고] 기존 증거의 소유 과목을 유도할 수 없다(url 없음) — "
                  "덮어쓰기 전에 %s 를 직접 확인하라"
                  % os.path.relpath(out_path, ROOT))
    os.makedirs(out_dir, exist_ok=True)

    class H(BaseHTTPRequestHandler):
        def do_POST(self):
            n = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(n)
            with open(out_path, "wb") as fh:
                fh.write(body)
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(b"ok")

        def log_message(self, *args):  # noqa: D102 — 조용히
            pass

    print(f"[대기] http://localhost:{a.port}/ — 요청 1건을 받으면 {os.path.relpath(out_path, ROOT)}에 저장 후 종료")
    HTTPServer(("127.0.0.1", a.port), H).handle_request()

    try:
        data = json.load(open(out_path, encoding="utf-8"))
    except Exception as exc:
        print(f"[FAIL] 저장본이 JSON이 아니다: {exc}")
        return 1
    if isinstance(data, dict) and data.get("INVALID"):
        print(f"[FAIL] 측정 무효(INVALID): {data['INVALID']} — 창 크기(≥1280×720)·--scale을 확인하고 재측정하라")
        return 1
    schema = data.get("schema") if isinstance(data, dict) else None
    n_slides = data.get("slideCount") if isinstance(data, dict) else None
    print(f"[저장] {os.path.relpath(out_path, ROOT)} — schema={schema} · slideCount={n_slides}")
    if schema != "deck-audit/1":
        print("[WARN] schema가 deck-audit/1이 아니다 — audit_all.js 출력을 그대로 보냈는지 확인하라")
    print("다음: python scripts/run_deck_checks.py " + week)
    return 0


if __name__ == "__main__":
    sys.exit(main())
