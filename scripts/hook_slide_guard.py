#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""강의덱 슬라이드 제작 단계 강제 훅 (Claude Code / Codex hooks에서 호출).

모드:
  --mode checklist        : PreToolUse(Write|Edit) — 슬라이드 파일을 건드리기 직전에
                            사전 점검 7항을 모델 컨텍스트로 주입한다.
  --mode css-lint         : PostToolUse(Write|Edit) — CSS에서 display:block이 후손
                            b/span 선택자에 걸린 회귀를 검출한다(R-QC-14).
  --mode css-lint --stdin-paths
                          : git 훅용. stdin에서 개행 구분 경로 목록을 읽어 각 .css를
                            검사하고, JSON이 아니라 사람이 읽는 텍스트 리포트를 낸다.
                            위반 있으면 exit 1, 없으면 exit 0. TARGET_HINTS 제한 없음
                            (git에 올라오는 모든 css를 본다).
  --mode course           : 과목 경로 편집 시 그 과목 지침을 컨텍스트로 주입한다.
  --mode generated-guard  : 조립 생성물(강의덱.html 등) 직접 편집을 감지한다.
  --mode tmp-guard        : 저장소 밖(시스템 임시 폴더 등) 쓰기를 감지한다.

공통 플래그:
  --host claude|codex (기본 claude) : 출력 형식 선택. codex는 차단 시 Claude 형식과
                            Codex 추정 형식(permissionDecision)을 한 객체에 함께 낸다
                            — Codex의 실제 페이로드/출력 스키마가 아직 미실측이라
                            **Gate 0 전까지 잠정**으로 양쪽을 만족시킨다.
  --enforce                : generated-guard·tmp-guard를 실제 차단으로 승격한다.
                            기본은 관측(경고 컨텍스트 주입 + tmp/guard-observations.jsonl
                            기록)만 한다 — 오탐률을 먼저 재고 0에 수렴할 때만 차단으로
                            승격한다는 프로젝트 규율(§공통 작업 방식)을 따른다.

왜 훅인가: 규칙 파일(SKILL.md·by-shape.md·디자인시스템.md)에 이미 규칙이 다 있었는데
2026-07-28 표본 작업에서 전부 건너뛰었다. 규칙 파일은 컨텍스트일 뿐 강제가 아니다 —
실제 강제는 이 계층에서만 일어난다.

실패해도 도구 호출을 막지 않는다(예외는 조용히 통과 — css-lint --stdin-paths의
exit 1/0만 예외로, 이건 git 훅의 관문이라 의도된 종료코드다).
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


def emit_text(text):
    """css-lint --stdin-paths 텍스트 리포트용. emit()과 같은 이유로 버퍼에 직접
    UTF-8 바이트를 쓴다 — cp949 콘솔에서 em dash 등에 걸려 죽지 않게 한다."""
    try:
        sys.stdout.buffer.write(text.encode("utf-8"))
        sys.stdout.buffer.flush()
    except Exception:
        try:
            sys.stdout.write(text)
        except Exception:
            pass


def emit_context(text):
    """컨텍스트 주입. host 무관 — Claude·Codex 둘 다 같은 키를 쓴다(잠정 합의)."""
    emit({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": text,
        }
    })


def emit_block(reason, host):
    """차단. host별 출력 형식이 다르다.
    claude: 기존 그대로 {"decision":"block","reason":...}
    codex : 위 형식에 Codex 추정 스키마(permissionDecision)를 얹어 함께 낸다.
            어느 쪽을 실제로 읽는지 미실측이므로 Gate 0 전까지 잠정으로 양쪽 다 낸다."""
    if host == "codex":
        emit({
            "decision": "block",
            "reason": reason,
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            },
        })
    else:
        emit({"decision": "block", "reason": reason})


# 슬라이드 작업으로 간주할 경로 조각 (checklist·css-lint 단일경로 모드에서만 사용)
TARGET_HINTS = ("samples_v3", "강의덱.초안", "강의덱.html")

# R-QC-14: 후손 선택자에 display:block — 문장 안 강조(.hl-mint-text 등)까지
# 블록이 되어 줄이 끊긴다. `> b` / `> span`으로 좁혀야 한다.
BAD_BLOCK = re.compile(r"^\.[A-Za-z0-9_-]+ +(b|span)\s*\{[^}]*display\s*:\s*block", re.M)

# 조립 생성물 판정: courses/**/강의덱.html · courses/**/강의덱_발표자노트.html로 끝나는 경로.
GENERATED_DECK_RE = re.compile(r"(^|/)courses/.*/강의덱(_발표자노트)?\.html$")

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

GENERATED_GUARD_REASON = (
    "이 경로는 조립 생성물입니다: {path}\n"
    "강의덱.html·강의덱_발표자노트.html은 scripts/assemble_deck.py가 "
    "강의덱.초안/(shard: shell.html + part-NN.html)에서 만들어 덮어씁니다. "
    "여기를 직접 고쳐도 다음 조립 때 유실됩니다 — shard를 고치고 assemble_deck.py를 다시 돌리세요. "
    "정본 규약은 sessions/README.md. "
    "부득이하게 생성물을 바로 고쳐야 하면 DECK_EMERGENCY_EDIT=1 환경변수로 이 검사를 우회할 수 있습니다."
)

TMP_GUARD_REASON = (
    "이 쓰기 대상이 저장소 밖입니다: {path}\n"
    "임시·중간 파일은 저장소 안 tmp/ 에만 만드세요(이미 .gitignore됨). "
    "시스템 임시 폴더(%TEMP%·AppData·플랫폼 스크래치패드)에 쓰면 세션이 끝난 뒤 회수할 수 없습니다 — "
    "2026-07-30에 서브에이전트 4개가 전부 시스템 임시 폴더에 써서 산출물을 잃은 전례가 있습니다."
)

# 페이로드 재귀 탐색으로 경로를 찾을 때 후보로 볼 키 이름들.
# (Codex 페이로드 스키마는 아직 미실측 — 흔한 후보를 모아 순서 무관하게 첫 매치를 채택한다)
FALLBACK_PATH_KEYS = ("file_path", "filePath", "path", "target_file", "filename", "file")


def _read_stdin_text():
    """stdin을 항상 UTF-8로 읽는다. sys.stdin.read()(텍스트 모드)는 Windows
    기본 로캘(cp949)로 디코드해 한글 경로가 깨진다 — 바이트로 받아 직접
    UTF-8 디코드한다(emit()이 쓰기를 UTF-8로 강제하는 것과 대칭)."""
    try:
        return sys.stdin.buffer.read().decode("utf-8", errors="replace")
    except Exception:
        try:
            return sys.stdin.read()
        except Exception:
            return ""


def read_payload():
    try:
        raw = _read_stdin_text()
        return json.loads(raw) if raw.strip() else {}
    except Exception:
        return {}


def _find_path_recursive(obj, keys):
    """페이로드 전체를 재귀 순회해 keys 중 하나이고 값이 문자열인 첫 항목을 찾는다.
    각 단계에서 그 단계의 키들을 먼저 보고, 없으면 자식으로 내려간다."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in keys and isinstance(v, str) and v:
                return v
        for v in obj.values():
            if isinstance(v, (dict, list)):
                found = _find_path_recursive(v, keys)
                if found:
                    return found
    elif isinstance(obj, list):
        for item in obj:
            found = _find_path_recursive(item, keys)
            if found:
                return found
    return None


def get_path(payload):
    """경로 추출. 1) 기존 Claude 키 우선 2) 실패하면 호스트 무관 재귀 탐색
    3) 그래도 없으면 빈 문자열(기존처럼 조용히 종료).
    payload가 dict가 아닌 경우(top-level 배열 등 비정형 페이로드)도 죽지 않는다."""
    top = payload if isinstance(payload, dict) else {}
    ti = top.get("tool_input") or {}
    tr = top.get("tool_response") or {}
    if not isinstance(ti, dict):
        ti = {}
    if not isinstance(tr, dict):
        tr = {}
    p = ti.get("file_path") or tr.get("filePath")
    if isinstance(p, str) and p:
        return p
    try:
        found = _find_path_recursive(payload, FALLBACK_PATH_KEYS)
    except Exception:
        found = None
    return found or ""


def is_target(path):
    p = path.replace("\\", "/")
    return any(h in p for h in TARGET_HINTS)


def is_persistent_agent_memory(abs_path):
    """`<home>/.claude/projects/<프로젝트키>/memory/` 아래인가.

    ⚠️ 오탐 판정 (2026-08-18). 관측 모드가 2026-08-17 세션에서 이 디렉터리 쓰기를
    `would-block`으로 잡았다. **오탐이다** — 이 규칙이 막으려는 해악은
    TMP_GUARD_REASON이 스스로 밝히듯 「세션이 끝난 뒤 회수할 수 없다」인데,
    에이전트 메모리 디렉터리는 정반대로 **세션마다 다시 읽히도록 시스템이 지정한
    영속 저장소**다. 임시 폴더가 아니므로 규칙의 사정거리 밖이다.

    ⚠️ 홈 디렉터리를 통째로 여는 것이 아니다 — `.claude/projects/<키>/memory/`
    **아래만** 통과시킨다. `~/.claude/` 다른 곳이나 `~/` 직하는 그대로 걸린다.
    (오탐을 없애려고 검사 범위를 넓게 깎으면 검출기가 눈이 머는 쪽으로 망가진다 —
     `references/검증-명령-지도.md` §8.2.)
    """
    home = os.path.abspath(os.path.expanduser("~")).replace("\\", "/").rstrip("/")
    base = (home + "/.claude/projects").lower()
    norm = os.path.normpath(abs_path).replace("\\", "/")
    if not norm.lower().startswith(base + "/"):
        return False
    rest = norm[len(base) + 1:].split("/")
    return len(rest) >= 2 and rest[1] == "memory"


def get_repo_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def log_observation(mode, path, verdict, reason=""):
    """관측 1건을 tmp/guard-observations.jsonl에 덧붙인다.

    오탐률을 재기 위한 로그다. **건수만 세면 오탐률을 계산할 수 없다** —
    「무엇을 왜 걸었는가」가 있어야 사람이 오탐/정탐을 판정할 수 있기 때문에
    모드·경로·판정·사유를 함께 남긴다. (첫 구현이 `{}`만 기록해 6줄이 전부
    빈 객체였다. 그 상태로는 차단 승격 근거를 만들 수 없다.)

    타임스탬프는 넣지 않는다 — `Date`/`time` 호출 없이도 순서는 파일 순서로
    충분하고, 훅은 매 편집마다 도므로 가볍게 유지한다.
    """
    try:
        log_dir = os.path.join(get_repo_root(), "tmp")
        os.makedirs(log_dir, exist_ok=True)
        rec = {"mode": mode, "path": path, "verdict": verdict}
        if reason:
            rec["reason"] = reason[:300]
        with open(os.path.join(log_dir, "guard-observations.jsonl"), "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception:
        pass


def mode_checklist(path):
    if not is_target(path):
        return
    if not path.lower().endswith((".html", ".css")):
        return
    emit_context(CHECKLIST)


def scan_css_violations(path):
    """CSS 파일에서 BAD_BLOCK 위반을 찾아 (line_no, snippet) 목록을 반환한다.
    파일이 없거나 읽을 수 없으면 빈 목록(예외를 삼킨다)."""
    if not os.path.isfile(path):
        return []
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except Exception:
        return []
    hits = []
    for m in BAD_BLOCK.finditer(text):
        line_no = text.count("\n", 0, m.start()) + 1
        hits.append((line_no, text[m.start():m.end()].strip()))
    return hits


def mode_css_lint(path, host):
    if not path.lower().endswith(".css"):
        return
    if not is_target(path):
        return
    hits = scan_css_violations(path)
    if not hits:
        return
    reason = (
        "R-QC-14 위반 — display:block이 **후손** b/span 선택자에 걸렸습니다.\n"
        "문장 안 강조 스팬(.hl-mint-text 등)까지 블록이 되어 줄이 끊깁니다. "
        "이 버그는 2026-07-28까지 4회 반복됐습니다(.ws-warn b → .vd-case b → "
        ".mt-note b → .fg-card span).\n"
        "직계 자식 선택자로 좁히세요: `.foo > b` / `.foo > span`\n\n"
        + "\n".join("  %d: %s" % (ln, sn) for ln, sn in hits)
    )
    emit_block(reason, host)


def mode_css_lint_stdin():
    """git 훅용: stdin의 개행 구분 경로 목록에서 .css만 검사해 텍스트 리포트를 낸다.
    JSON을 내지 않는다. 위반 있으면 exit 1, 없으면 exit 0. TARGET_HINTS 제한 없음
    (git에 올라오는 모든 css를 본다)."""
    raw = _read_stdin_text()
    paths = [line.strip() for line in raw.splitlines() if line.strip()]

    report = []
    any_violation = False
    for path in paths:
        if not path.lower().endswith(".css"):
            continue
        hits = scan_css_violations(path)
        if hits:
            any_violation = True
            report.append("%s:" % path)
            for line_no, snippet in hits:
                report.append("  %d: %s" % (line_no, snippet))

    if any_violation:
        header = (
            "R-QC-14 위반 — display:block이 후손 b/span 선택자에 걸린 CSS가 있습니다.\n"
            "직계 자식 선택자로 좁히세요: `.foo > b` / `.foo > span`\n"
        )
        emit_text(header + "\n".join(report) + "\n")
        sys.exit(1)
    else:
        emit_text("css-lint: 위반 없음\n")
        sys.exit(0)


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
    emit_context("\n".join(body))


def mode_generated_guard(path, host, enforce):
    """조립 생성물(강의덱.html·강의덱_발표자노트.html) 직접 편집을 감지한다.
    예외: shard 폴더(강의덱.초안) · DECK_EMERGENCY_EDIT=1 · tests/fixtures.
    기본은 관측(경고 컨텍스트 + 기록)만 하고, --enforce일 때만 실제 차단한다."""
    p = path.replace("\\", "/")
    if "강의덱.초안" in p:
        return
    if "tests/fixtures" in p:
        return
    if os.environ.get("DECK_EMERGENCY_EDIT") == "1":
        return
    if not GENERATED_DECK_RE.search(p):
        return
    reason = GENERATED_GUARD_REASON.format(path=path)
    if enforce:
        emit_block(reason, host)
    else:
        emit_context("[관측 모드 — 아직 차단 아님. --enforce로 승격 전까지는 경고만]\n" + reason)
        log_observation("generated-guard", path, "would-block", reason)


def mode_tmp_guard(path, host, enforce):
    """쓰기 대상이 저장소 루트 밖이면 위반. 저장소 루트는 이 스크립트 위치의
    부모(scripts/의 부모)로 계산한다. 기본은 관측만, --enforce일 때만 차단."""
    repo_root = os.path.abspath(get_repo_root())
    # ⚠️ 상대경로는 **저장소 루트 기준**으로 푼다. os.path.abspath()만 쓰면 훅
    # 프로세스의 CWD 기준이 되는데, 훅이 어디서 실행될지는 호스트가 정하므로
    # 저장소 안 파일(plans/x.md)이 「밖」으로 잡히는 오탐이 난다.
    # 2026-08-05 관측 모드에서 실제로 재현됐다 — 차단으로 승격했다면 정상 편집이
    # 막혔을 것이다. `../밖.txt` 같은 이탈은 normpath가 그대로 잡아낸다.
    abs_path = os.path.abspath(path if os.path.isabs(path) else os.path.join(repo_root, path))
    try:
        common = os.path.commonpath([repo_root, abs_path])
    except ValueError:
        common = None
    if common == repo_root:
        return
    # 저장소 밖이지만 «시스템 지정 영속 경로»면 통과 — 오탐 장부에 allow로 남긴다.
    # 「걸지 않았다」를 조용히 넘기지 않기 위해서다: 승격(--enforce) 판단은
    # would-block과 allow의 비율로 하며, allow가 기록되지 않으면 분모가 사라진다.
    if is_persistent_agent_memory(abs_path):
        log_observation("tmp-guard", path, "allow",
                        "에이전트 영속 메모리(<home>/.claude/projects/<키>/memory/) — "
                        "2026-08-18 오탐 확정")
        return
    reason = TMP_GUARD_REASON.format(path=path)
    if enforce:
        emit_block(reason, host)
    else:
        emit_context("[관측 모드 — 아직 차단 아님. --enforce로 승격 전까지는 경고만]\n" + reason)
        log_observation("tmp-guard", path, "would-block", reason)


def _flag_value(argv, name, default=None):
    if name in argv:
        i = argv.index(name)
        if i + 1 < len(argv):
            return argv[i + 1]
    return default


def main():
    argv = sys.argv[1:]
    mode = _flag_value(argv, "--mode", "")
    host = _flag_value(argv, "--host", "claude")
    enforce = "--enforce" in argv
    stdin_paths = "--stdin-paths" in argv

    if mode == "css-lint" and stdin_paths:
        mode_css_lint_stdin()
        return

    payload = read_payload()
    path = get_path(payload)
    if not path:
        return
    try:
        if mode == "checklist":
            mode_checklist(path)
        elif mode == "css-lint":
            mode_css_lint(path, host)
        elif mode == "course":
            mode_course(path)
        elif mode == "generated-guard":
            mode_generated_guard(path, host, enforce)
        elif mode == "tmp-guard":
            mode_tmp_guard(path, host, enforce)
    except Exception:
        pass


if __name__ == "__main__":
    main()
