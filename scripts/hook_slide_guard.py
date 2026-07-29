#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""강의덱 슬라이드 제작 단계 강제 훅 (Claude Code hooks에서 호출).

두 모드:
  --mode checklist  : PreToolUse(Write|Edit) — 슬라이드 파일을 건드리기 직전에
                      사전 점검 7항을 모델 컨텍스트로 주입한다.
  --mode css-lint   : PostToolUse(Write|Edit) — CSS에서 display:block이 후손
                      b/span 선택자에 걸린 회귀를 검출한다(R-QC-14).

왜 훅인가: 규칙 파일(SKILL.md·by-shape.md·디자인시스템.md)에 이미 규칙이 다 있었는데
2026-07-28 표본 작업에서 전부 건너뛰었다. 규칙 파일은 컨텍스트일 뿐 강제가 아니다 —
실제 강제는 이 계층에서만 일어난다.

실패해도 도구 호출을 막지 않는다(예외는 조용히 통과).
"""
import sys
import json
import re
import os


def emit(obj):
    """stdout이 cp949여도 깨지지 않게 UTF-8 바이트로 직접 쓴다.
    (Windows 콘솔 기본 인코딩에서 print()는 UnicodeEncodeError로 조용히 죽는다 —
     실제로 이 훅의 첫 구현이 그렇게 무력화됐다.)"""
    data = json.dumps(obj, ensure_ascii=False)
    try:
        sys.stdout.buffer.write(data.encode("utf-8"))
        sys.stdout.buffer.flush()
    except Exception:
        sys.stdout.write(data)

# 슬라이드 작업으로 간주할 경로 조각
TARGET_HINTS = ("samples_v3", "강의덱.초안", "강의덱.html")

# R-QC-14: 후손 선택자에 display:block — 문장 안 강조(.hl-mint-text 등)까지
# 블록이 되어 줄이 끊긴다. `> b` / `> span`으로 좁혀야 한다.
BAD_BLOCK = re.compile(r"^\.[A-Za-z0-9_-]+ +(b|span)\s*\{[^}]*display\s*:\s*block", re.M)

CHECKLIST = """[슬라이드 제작 사전 점검 7항 — references/phases/02-슬라이드맵.md]
이 파일은 강의덱 슬라이드다. 아래를 통과하지 않았다면 지금 멈추고 먼저 하라.

□ 1. 정보 모양을 12 정준 모양 중 하나로 정했는가       (kit/guide/정보모양-taxonomy.md)
□ 2. 역인덱스를 실제로 열었는가 — layouts + charts 둘 다 (kit/*/by-shape.md · R-LAYOUT-01b)
□ 3. 레이아웃과 element를 따로 골랐는가                 (R-LAYOUT-02a · 레이아웃 ≠ element)
□ 4. 형태를 순서 판별로 정했는가 — 산문/병렬            (R-FORM-01: 순서를 바꿔도 뜻이 유지되는가?)
□ 5. 강조 3종을 의미로 배정했는가                       (R-EMPH-01: mark=결론 1개 / underline=근거 / text=핵심어, 합계 ≤3)
□ 6. 직전 슬라이드와 구도·마무리가 다른가               (R-DEC-01 · 검은 배너 반복 금지)
□ 7. 이미지 4상태를 판정했는가                          (SKILL.md 이미지 판정 게이트)

주의: 전부 박스도, 전부 줄글도 같은 실패다. 판정은 슬라이드마다 한다."""


def read_payload():
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except Exception:
        return {}


def get_path(payload):
    ti = payload.get("tool_input") or {}
    tr = payload.get("tool_response") or {}
    return (ti.get("file_path") or tr.get("filePath") or "") or ""


def is_target(path):
    p = path.replace("\\", "/")
    return any(h in p for h in TARGET_HINTS)


def mode_checklist(path):
    if not is_target(path):
        return
    if not path.lower().endswith((".html", ".css")):
        return
    emit({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": CHECKLIST,
        }
    })


def mode_css_lint(path):
    if not path.lower().endswith(".css"):
        return
    if not is_target(path):
        return
    if not os.path.isfile(path):
        return
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except Exception:
        return
    hits = []
    for m in BAD_BLOCK.finditer(text):
        line_no = text.count("\n", 0, m.start()) + 1
        hits.append("  %d: %s" % (line_no, text[m.start():m.end()].strip()))
    if not hits:
        return
    reason = (
        "R-QC-14 위반 — display:block이 **후손** b/span 선택자에 걸렸습니다.\n"
        "문장 안 강조 스팬(.hl-mint-text 등)까지 블록이 되어 줄이 끊깁니다. "
        "이 버그는 2026-07-28까지 4회 반복됐습니다(.ws-warn b → .vd-case b → "
        ".mt-note b → .fg-card span).\n"
        "직계 자식 선택자로 좁히세요: `.foo > b` / `.foo > span`\n\n" + "\n".join(hits)
    )
    emit({"decision": "block", "reason": reason})


def mode_course(path):
    """과목 경로에서 편집하면 그 과목의 슬라이드 지침을 컨텍스트로 주입한다.

    왜: 지침 파일이 있어도 열지 않으면 없는 것과 같다. 2026-07-28에 개념KB의
    `PPT 소재` 63건이 그렇게 한 번도 회수되지 않았다. 규칙 파일은 컨텍스트일 뿐
    강제가 아니므로, 강제는 이 계층에서만 일어난다."""
    p = path.replace("\\", "/")
    if not any(seg in p for seg in ("/sessions/", "sessions/", "/courses/", "courses/")):
        return
    if not p.lower().endswith((".html", ".md", ".css")):
        return
    try:
        here = os.path.dirname(os.path.abspath(__file__))
        if here not in sys.path:
            sys.path.insert(0, here)
        import _course_paths
        guide = _course_paths.guide_path()
        prof = _course_paths.profile_path()
    except Exception:
        return
    if not guide:
        return
    try:
        with open(guide, encoding="utf-8") as fh:
            text = fh.read()
    except Exception:
        return
    heads = [l.strip() for l in text.splitlines() if l.startswith("## ")]
    m = re.search(r"^##\s*4\..*?$(.*?)(?=^##\s|\Z)", text, re.M | re.S)
    tail = (m.group(1).strip() if m else "")[:900]
    body = [
        "[과목 지침 — 이 과목에서 작업 중입니다]",
        "지침: %s" % guide,
        "프로필: %s" % (prof or "(없음 — 기준선 요구 게이트는 WARN)"),
        "",
        "절: " + " / ".join(h[3:] for h in heads),
        "",
        "확정된 화면 판단(그대로 적용):",
        tail,
        "",
        "⚠️ 대상 서술·범위·관통 문장은 이 지침이 정본이다. 킷의 교육원칙 요약에는 과목 값이 없다.",
    ]
    emit({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": "\n".join(body),
        }
    })


def main():
    mode = ""
    if "--mode" in sys.argv:
        i = sys.argv.index("--mode")
        if i + 1 < len(sys.argv):
            mode = sys.argv[i + 1]
    payload = read_payload()
    path = get_path(payload)
    if not path:
        return
    try:
        if mode == "checklist":
            mode_checklist(path)
        elif mode == "css-lint":
            mode_css_lint(path)
        elif mode == "course":
            mode_course(path)
    except Exception:
        pass


if __name__ == "__main__":
    main()
