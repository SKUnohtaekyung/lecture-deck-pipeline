#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Gate 0 프로브 — Codex 훅의 실제 이벤트·페이로드 스키마를 실측한다.

PLAN.md §5.0. 이 스크립트는 **아무것도 막지 않는다.** stdin으로 들어온 JSON을
그대로 tmp/codex-hook-probe.jsonl 에 한 줄씩 덧붙이기만 한다.

왜 필요한가: `PreToolUse`/`PostToolUse` 지원은 공식 문서 근거이고, 이 PC에서
실물로 확인된 것은 `Stop` 이벤트뿐이다. 문서만 믿고 강제 설계를 얹으면
「선언과 집행 불일치」(유형⑤)를 새로 만든다. 그래서 먼저 잰다.

제약(PLAN.md §5.1): 표준 라이브러리만 사용한다. 이 저장소에 `.venv`가 없어
훅은 시스템 인터프리터로 실행되며 fontTools/Pillow 가용성을 가정할 수 없다.

사용:
    python .codex/hooks/probe.py --event PreToolUse
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "tmp", "codex-hook-probe.jsonl")


def arg(name, default=""):
    if name in sys.argv:
        i = sys.argv.index(name)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return default


def main():
    raw = ""
    try:
        raw = sys.stdin.read()
    except Exception as exc:  # stdin이 없어도 죽지 않는다
        raw = "<stdin read failed: %s>" % exc

    record = {
        "event_label": arg("--event", "unknown"),
        "argv": sys.argv[1:],
        "cwd": os.getcwd(),
        "stdin_len": len(raw),
    }
    try:
        record["stdin_json"] = json.loads(raw) if raw.strip() else None
        record["stdin_parsed"] = True
    except Exception:
        record["stdin_raw"] = raw[:4000]
        record["stdin_parsed"] = False

    try:
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        with io.open(OUT, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        pass  # 관측 실패가 작업을 막지 않는다

    # 아무것도 차단하지 않는다. 훅 계약이 무엇을 기대하든 안전한 빈 응답을 낸다.
    try:
        sys.stdout.buffer.write(b"{}")
        sys.stdout.buffer.flush()
    except Exception:
        sys.stdout.write("{}")


if __name__ == "__main__":
    main()
