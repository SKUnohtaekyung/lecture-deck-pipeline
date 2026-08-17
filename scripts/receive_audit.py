#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""렌더 감사 JSON 1회용 POST 수신기 — 브라우저 콘솔 출력을 바이트 그대로 저장한다.

왜
--
`audit_all.js` 출력(9KB+ 이스케이프 문자열)을 콘솔에서 손으로 옮겨 적으면 전사
오류 위험이 있다. 이 수신기는 요청 1건을 받아 `sessions/_verify/<주차>/deck-audit.json`
에 그대로 쓰고 즉시 종료한다(상시 서버 아님 · CORS 허용 헤더 포함 — 덱을 서빙하는
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


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("week", help="주차 (예: 1주차) — sessions/_verify/<주차>/deck-audit.json 에 저장")
    ap.add_argument("--port", type=int, default=8798)
    a = ap.parse_args()

    week = a.week if a.week.endswith("주차") else f"{a.week}주차"
    out_dir = os.path.join(ROOT, "sessions", "_verify", week)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "deck-audit.json")

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
