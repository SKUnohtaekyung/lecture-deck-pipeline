#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""git pre-commit 게이트 — staged 파일 기준으로 조건부 검증을 돌린다.

왜: 이 프로젝트는 지금까지 Claude Code 훅으로만 규칙을 강제해 왔고 Codex 쪽
강제는 0이었다. git 훅은 CLI(Claude Code든 Codex든 사람이 직접 커밋하든)와
무관하게 커밋 시점에 실행되는 유일한 공통 층이라 여기 둔다.

동작 개요:
  1. SKIP_DECK_GATES=1이면 전부 건너뛰고 exit 0 (긴급 탈출구).
  2. `git diff --cached --name-only -z --diff-filter=ACMR`로 staged 목록을
     받는다(NUL 구분 — 한글 파일명이 많아 quotepath 인용 문제를 피한다).
  3. staged 패턴에 따라 조건부로 기존 verify_*.py를 서브프로세스로 돌린다.
  4. 검사 하나가 죽어도(파일 없음·예외) 나머지는 계속 돌리고, 마지막에
     사람이 읽는 한국어 요약과 종합 종료코드를 낸다.

한계(중요): 모든 검사는 **워킹트리에 있는 현재 파일 내용**을 본다. 진짜
staged blob(`git show :path`)이 아니다 — 부분적으로만 add한 파일이 있으면
워킹트리 내용과 staged 내용이 다를 수 있다. stash 등으로 워킹트리를 staged
상태로 맞추는 조작은 사용자의 손대지 않은 변경을 건드릴 위험이 커서 하지
않는다. 이 한계는 README에도 적혀 있다.

python 표준 라이브러리만 사용한다(이 저장소엔 .venv가 없어 훅은 시스템
인터프리터로 돈다).
"""
import hashlib
import os
import re
import subprocess
import sys


# ---------------------------------------------------------------------------
# 출력 — Windows cp949 콘솔에서 한글이 깨지지 않게 UTF-8 바이트로 직접 쓴다.
# (hook_slide_guard.py의 emit()/emit_text()와 같은 이유·같은 방식.)
# ---------------------------------------------------------------------------

def out(text=""):
    try:
        sys.stdout.buffer.write((text + "\n").encode("utf-8"))
        sys.stdout.buffer.flush()
    except Exception:
        try:
            sys.stdout.write(text + "\n")
        except Exception:
            pass


def repo_root():
    """이 스크립트(.githooks/_gate.py) 위치의 부모를 저장소 루트로 본다."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ---------------------------------------------------------------------------
# staged 파일 목록
# ---------------------------------------------------------------------------

def get_staged_files(root):
    """staged(추가/수정/변경/이름유지) 파일 경로 목록. NUL 구분으로 받아
    한글 파일명 인용 문제를 피한다. 실패하면 빈 목록(훅 자체를 죽이지 않음)."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "-z", "--diff-filter=ACMR"],
            cwd=root,
            capture_output=True,
        )
    except Exception:
        return []
    raw = result.stdout or b""
    files = []
    for part in raw.split(b"\x00"):
        if not part:
            continue
        try:
            files.append(part.decode("utf-8").replace("\\", "/"))
        except Exception:
            files.append(part.decode("utf-8", errors="replace").replace("\\", "/"))
    return files


def get_untracked_files(root):
    """추적되지 않는(??) 파일 목록. 훅 인프라 문제로 죽지 않게 실패 시 빈 목록."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain", "-z"],
            cwd=root,
            capture_output=True,
        )
    except Exception:
        return []
    raw = result.stdout or b""
    untracked = []
    for entry in raw.split(b"\x00"):
        if not entry:
            continue
        try:
            text = entry.decode("utf-8", errors="replace")
        except Exception:
            continue
        if len(text) < 4:
            continue
        code = text[:2]
        path = text[3:].replace("\\", "/")
        if code == "??":
            untracked.append(path)
    return untracked


# ---------------------------------------------------------------------------
# 서브스크립트 실행 헬퍼
# ---------------------------------------------------------------------------

class ScriptMissing(Exception):
    pass


def run_script(root, rel_path, args=None, stdin_bytes=None):
    """rel_path 스크립트를 같은 인터프리터(sys.executable)로 실행한다.
    파일이 없으면 ScriptMissing을 던진다(호출부에서 SKIP+WARN 처리).
    반환: (returncode, stdout_text, stderr_text)."""
    script_path = os.path.join(root, rel_path)
    if not os.path.isfile(script_path):
        raise ScriptMissing(rel_path)
    cmd = [sys.executable, script_path] + (args or [])
    result = subprocess.run(
        cmd, cwd=root, capture_output=True, input=stdin_bytes,
    )
    stdout = (result.stdout or b"").decode("utf-8", errors="replace")
    stderr = (result.stderr or b"").decode("utf-8", errors="replace")
    return result.returncode, stdout, stderr


# ---------------------------------------------------------------------------
# 결과 표현
# ---------------------------------------------------------------------------

class Result(object):
    __slots__ = ("name", "status", "detail")

    def __init__(self, name, status, detail=""):
        self.name = name
        self.status = status  # PASS | FAIL | SKIP | WARN | ERROR
        self.detail = detail


def _tail(text, n=15):
    """스크립트 출력이 길면 마지막 n줄만 보여준다(터미널이 로그로 덮이지 않게)."""
    lines = [l for l in (text or "").splitlines() if l.strip()]
    if len(lines) <= n:
        return "\n".join(lines)
    return "  ... (총 %d줄 중 마지막 %d줄)\n" % (len(lines), n) + "\n".join(lines[-n:])


# ---------------------------------------------------------------------------
# 개별 검사
# ---------------------------------------------------------------------------

def check_kit(root, staged):
    """kit/ 아래 변경 → verify_kit.py → verify_declared_vs_enforced.py."""
    name = "kit 정합성 (verify_kit → verify_declared_vs_enforced)"
    if not any(p.startswith("kit/") for p in staged):
        return Result(name, "SKIP", "staged 안에 kit/ 변경 없음")

    for rel in ("scripts/verify_kit.py", "scripts/verify_declared_vs_enforced.py"):
        try:
            code, stdout, stderr = run_script(root, rel)
        except ScriptMissing:
            return Result(name, "WARN", "%s 없음 — 이 검사를 건너뜀" % rel)
        except Exception as e:
            return Result(name, "ERROR", "%s 실행 중 예외: %s" % (rel, e))
        if code != 0:
            return Result(name, "FAIL", "%s 실패(exit %d)\n%s" % (rel, code, _tail(stdout + stderr)))
    return Result(name, "PASS", "verify_kit·verify_declared_vs_enforced 통과")


def check_skill(root, staged):
    """SKILL.md 또는 skills/·.claude/skills/·.agents/skills/ 아래 변경 → verify_skill_setup.py."""
    name = "스킬 셋업 (verify_skill_setup)"
    hit = any(
        os.path.basename(p) == "SKILL.md" or re.search(r"(^|/)(skills|\.claude/skills|\.agents/skills)/", p)
        for p in staged
    )
    if not hit:
        return Result(name, "SKIP", "staged 안에 SKILL.md/skills 경로 변경 없음")

    rel = "scripts/verify_skill_setup.py"
    try:
        code, stdout, stderr = run_script(root, rel)
    except ScriptMissing:
        return Result(name, "WARN", "%s 없음 — 이 검사를 건너뜀" % rel)
    except Exception as e:
        return Result(name, "ERROR", "%s 실행 중 예외: %s" % (rel, e))
    if code != 0:
        return Result(name, "FAIL", "%s 실패(exit %d)\n%s" % (rel, code, _tail(stdout + stderr)))
    return Result(name, "PASS", "verify_skill_setup 통과")


def check_css(root, staged):
    """*.css 변경 → hook_slide_guard.py --mode css-lint --stdin-paths."""
    name = "CSS lint (R-QC-14 · hook_slide_guard --mode css-lint)"
    css_files = [p for p in staged if p.lower().endswith(".css")]
    if not css_files:
        return Result(name, "SKIP", "staged 안에 .css 변경 없음")

    rel = "scripts/hook_slide_guard.py"
    stdin_bytes = ("\n".join(css_files) + "\n").encode("utf-8")
    try:
        code, stdout, stderr = run_script(
            root, rel, args=["--mode", "css-lint", "--stdin-paths"], stdin_bytes=stdin_bytes,
        )
    except ScriptMissing:
        return Result(name, "WARN", "%s 없음 — 이 검사를 건너뜀" % rel)
    except Exception as e:
        return Result(name, "ERROR", "%s 실행 중 예외: %s" % (rel, e))
    if code != 0:
        return Result(name, "FAIL", _tail(stdout + stderr))
    return Result(name, "PASS", _tail(stdout) or "위반 없음")


DECK_HTML_RE = re.compile(r"(^|/)courses/[^/]+/sessions/[^/]+/강의덱\.html$")
NOTES_HTML_RE = re.compile(r"(^|/)courses/[^/]+/sessions/[^/]+/강의덱_발표자노트\.html$")


def check_deck_generated(root, staged):
    """courses/**/강의덱.html 단독 staged → shard(강의덱.초안/)가 같이 staged됐는지 확인."""
    name = "덱 생성물 동반 (강의덱.html ↔ 강의덱.초안/)"
    deck_paths = [p for p in staged if DECK_HTML_RE.search(p)]
    if not deck_paths:
        return Result(name, "SKIP", "staged 안에 courses/**/강의덱.html 변경 없음")

    problems = []
    for deck_path in deck_paths:
        week_dir = deck_path.rsplit("/", 1)[0]
        shard_prefix = week_dir + "/강의덱.초안/"
        if not any(p.startswith(shard_prefix) for p in staged):
            problems.append(deck_path)

    if problems:
        detail = (
            "다음 강의덱.html은 생성물입니다. 같은 커밋에 강의덱.초안/(shard) 변경이 없습니다:\n"
            + "\n".join("  - %s" % p for p in problems)
            + "\n생성물이다. shard를 고치고 scripts/assemble_deck.py를 돌려라."
        )
        return Result(name, "FAIL", detail)
    return Result(name, "PASS", "staged 강의덱.html %d건 모두 shard 동반" % len(deck_paths))


def check_notes(root, staged):
    """courses/**/강의덱_발표자노트.html staged → 같은 주차 강의덱.html을 유도해 verify_notes.py."""
    name = "발표자노트 정합 (verify_notes)"
    notes_paths = [p for p in staged if NOTES_HTML_RE.search(p)]
    if not notes_paths:
        return Result(name, "SKIP", "staged 안에 강의덱_발표자노트.html 변경 없음")

    results = []
    for notes_path in notes_paths:
        deck_path = notes_path[: -len("강의덱_발표자노트.html")] + "강의덱.html"
        notes_full = os.path.join(root, notes_path)
        deck_full = os.path.join(root, deck_path)
        if not os.path.isfile(notes_full) or not os.path.isfile(deck_full):
            results.append(("WARN", "%s ↔ %s 경로를 유도할 수 없음(파일 없음) — 건너뜀" % (notes_path, deck_path)))
            continue
        rel = "scripts/verify_notes.py"
        try:
            code, stdout, stderr = run_script(root, rel, args=[deck_path, notes_path])
        except ScriptMissing:
            results.append(("WARN", "%s 없음 — 이 검사를 건너뜀" % rel))
            continue
        except Exception as e:
            results.append(("ERROR", "%s 실행 중 예외: %s" % (rel, e)))
            continue
        if code != 0:
            results.append(("FAIL", "%s ↔ %s 불일치(exit %d)\n%s" % (deck_path, notes_path, code, _tail(stdout + stderr))))
        else:
            results.append(("PASS", "%s ↔ %s 정합" % (deck_path, notes_path)))

    # 종합: FAIL > ERROR > WARN > PASS 순으로 대표 상태를 뽑는다.
    order = {"FAIL": 0, "ERROR": 1, "WARN": 2, "PASS": 3}
    results.sort(key=lambda r: order.get(r[0], 9))
    worst_status = results[0][0]
    detail = "\n".join("[%s] %s" % r for r in results)
    return Result(name, worst_status, detail)


def check_contract_waivers(root, staged):
    """deck.contract.json staged → verify_contract_waivers.py (무사유 waiver 거부 · P1)."""
    name = "계약 waiver 스키마 (verify_contract_waivers)"
    hit = any(p.endswith("deck.contract.json") for p in staged)
    if not hit:
        return Result(name, "SKIP", "staged 안에 deck.contract.json 변경 없음")

    rel = "scripts/verify_contract_waivers.py"
    try:
        code, stdout, stderr = run_script(root, rel)
    except ScriptMissing:
        return Result(name, "WARN", "%s 없음 — 이 검사를 건너뜀" % rel)
    except Exception as e:
        return Result(name, "ERROR", "%s 실행 중 예외: %s" % (rel, e))
    if code != 0:
        return Result(name, "FAIL", "무사유·무일자 waiver는 커밋할 수 없다(exit %d)\n%s"
                      % (code, _tail(stdout + stderr)))
    return Result(name, "PASS", "waiver 스키마(사유·일자) 전건 유효")


def check_tmp_litter(root, staged):
    """항상 실행 — tmp/ 밖 미추적 잡파일 스캔. 차단 아님, 경고만."""
    name = "저장소 잡파일 스캔 (tmp/ 밖 미추적 파일)"
    untracked = get_untracked_files(root)
    litter = [p for p in untracked if not p.startswith("tmp/")]
    if not litter:
        return Result(name, "PASS", "tmp/ 밖 미추적 파일 없음")
    shown = litter[:10]
    more = "" if len(litter) <= 10 else "\n  ... 외 %d건" % (len(litter) - 10)
    detail = (
        "tmp/ 밖에 미추적 파일이 있습니다(차단 아님 — 참고만):\n"
        + "\n".join("  - %s" % p for p in shown) + more
    )
    return Result(name, "WARN", detail)


# 동결 렌더 증거 — 사용자 결정(2026-07-26 · 2026-08-17)으로 수정 금지인 산출물.
# 값의 출처는 T00 실측 기록(courses/*/제작관리/시작기준선.json)이고, 여기 둔 것은
# 그 사실의 **집행 복사본**이다. 경로에 과목명이 없어 과목 격리를 깨지 않는다.
# 갱신 조건: 사용자가 동결을 해제하고 재측정을 승인했을 때만, 그 결정과 함께 바꾼다.
# ⚠️ 값은 **워킹트리 바이트**의 sha256이다(git blob이 아니다). 이 저장소는
#    core.autocrlf=true라 사이드카 2파일의 blob(LF)과 워킹트리(CRLF)가 다르다 —
#    실측: 1주차 사이드카 blob 7,615B / 워킹트리 7,814B. 그래서 blob 바이트를 이
#    표에 직접 대조하면 **오탐**이 난다. staged 쪽은 아래 _blob_id 두 개를 서로
#    비교해 «스테이지 내용이 워킹트리와 다른가»만 묻는다.
FROZEN_EVIDENCE = {
    "sessions/_verify/1주차/deck-audit.json":
        "3b8636bbe76344eef11f24a1de4f2d9c0f955441f2b87441ad0ad963f69de8de",
    "sessions/_verify/1주차/강의덱_발표.meta.json":
        "09fbdba699557a978836e8c1af8e293a7e1d4e87200573b404f1197b4cce61bc",
    "sessions/_verify/2주차/deck-audit.json":
        "1c4ffbe3ee5d3fe04bf73e468b84dfd50d756c58f4a2edb7db0df09de1bece8a",
    "sessions/_verify/2주차/강의덱_발표.meta.json":
        "4d59bed312fe405e4cdd3fbf06c5c728dac84a46c75113233a8118b13a91a4df",
    "sessions/_verify/3주차/deck-audit.json":
        "968e9d3fdf7add6657eea22537939329b95f57e10232d1036ebe07e40857861e",
}


def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _commit_tree_root(fallback):
    """지금 **커밋 중인** 워킹트리의 루트. worktree 미탐을 닫는다(D10).

    `repo_root()`는 `.githooks/_gate.py`의 **파일 위치**로 루트를 잡는다. 그런데
    `core.hooksPath`가 메인 저장소의 `.githooks`를 가리키면(절대경로 설정·공유
    config·linked worktree) worktree에서 커밋해도 훅 파일은 메인 것이라, 그 규칙
    그대로면 **메인 저장소의 동결 파일을 해싱**하고 worktree 쪽 훼손을 통과시킨다.
    그것은 오탐이 아니라 **미탐**이고, 미탐은 PASS로 위장해 아무도 발견하지 못한다.
    커밋 대상 트리는 `git rev-parse --show-toplevel`이 정확히 답한다(훅 실행 시
    cwd는 그 트리의 최상위다 — 그래서 cwd를 넘기지 않고 상속한다).
    """
    try:
        r = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                           capture_output=True)
        if r.returncode == 0:
            top = (r.stdout or b"").decode("utf-8", errors="replace").strip()
            if top and os.path.isdir(top):
                return os.path.normpath(top)
    except Exception:
        pass
    return fallback


def _blob_id(root, args):
    """git이 계산한 blob id 1개. 실패하면 None(«비교 불가»이지 «같음»이 아니다)."""
    try:
        r = subprocess.run(["git"] + args, cwd=root, capture_output=True)
    except Exception:
        return None
    if r.returncode != 0:
        return None
    out = (r.stdout or b"").decode("utf-8", errors="replace").strip()
    return out or None


def check_frozen_evidence(root, staged):
    """동결 렌더 증거 5파일이 바뀌었는지 — staged 여부와 무관하게 워킹트리를 본다.

    staged만 보면 «덮어쓰고 add하지 않은» 상태를 놓친다. 그 상태로 다른 파일을
    커밋하면 소실이 커밋 이력에 남지 않은 채 워킹트리에만 남는다. 반대로 워킹트리만
    보면 «훼손분을 add해 두고 워킹트리는 되돌린» 경우를 놓친다 — 그래서 스테이지도
    본다. 다만 스테이지는 sha256 표와 직접 대조하지 않는다(autocrlf 때문에 blob과
    워킹트리 바이트가 달라 오탐이 난다 — 위 주석). 대신 «스테이지 blob id»와
    «워킹트리를 그대로 blob으로 만들었을 때의 id»가 같은지만 묻는다.
    """
    name = "동결 렌더 증거 불변 (sessions/_verify)"
    root = _commit_tree_root(root)
    changed, missing, staged_bad, unjudged = [], [], [], []
    for rel, want in sorted(FROZEN_EVIDENCE.items()):
        full = os.path.join(root, rel.replace("/", os.sep))
        if not os.path.isfile(full):
            missing.append(rel)
            continue
        if _sha256_file(full) != want:
            changed.append(rel)
        idx = _blob_id(root, ["rev-parse", ":" + rel])
        wt = _blob_id(root, ["hash-object", "--", rel])
        if idx is None or wt is None:
            unjudged.append(rel)          # 「같다」가 아니라 「못 봤다」
        elif idx != wt:
            staged_bad.append(rel)
    if missing or changed or staged_bad:
        detail = "동결 산출물이 바뀌었습니다(사용자 결정으로 수정 금지):\n"
        detail += "".join("  - 삭제/부재: %s\n" % p for p in missing)
        detail += "".join("  - 내용 변경: %s\n" % p for p in changed)
        detail += "".join("  - 스테이지 내용이 워킹트리와 다름: %s\n" % p for p in staged_bad)
        if unjudged:
            detail += "".join("  - 스테이지 대조 미판정(blob id 조회 실패): %s\n" % p
                              for p in unjudged)
        detail += "검사 대상 트리: %s\n" % root
        detail += ("git checkout -- <경로> 로 되돌리세요. 재측정이 정말 필요하면 "
                   "사용자 결정을 먼저 받고 이 표의 sha256을 함께 갱신하세요.")
        return Result(name, "FAIL", detail)
    return Result(name, "PASS",
                  "동결 증거 %d파일 sha256 일치 (판정 %d · 스테이지 대조 미판정 %d) — 트리 %s"
                  % (len(FROZEN_EVIDENCE), len(FROZEN_EVIDENCE), len(unjudged), root))


# ---------------------------------------------------------------------------
# 메인
# ---------------------------------------------------------------------------

def main():
    root = repo_root()

    if os.environ.get("SKIP_DECK_GATES") == "1":
        out("SKIP_DECK_GATES=1 — pre-commit 게이트 전체를 건너뜁니다.")
        return 0

    staged = get_staged_files(root)

    out("=== pre-commit 게이트 ===")
    if not staged:
        out("[SKIP] staged 파일 없음 — 검사할 대상이 없습니다.")
        out("종료코드: 0")
        return 0

    checks = [check_kit, check_skill, check_css, check_deck_generated, check_notes,
              check_contract_waivers, check_frozen_evidence, check_tmp_litter]
    results = []
    for check in checks:
        try:
            results.append(check(root, staged))
        except Exception as e:
            results.append(Result(check.__name__, "ERROR", "검사 자체가 예외로 죽음: %s" % e))

    for r in results:
        out("")
        out("[%s] %s" % (r.status, r.name))
        if r.detail:
            for line in r.detail.splitlines():
                out("    " + line)

    blocking = [r for r in results if r.status == "FAIL"]
    warns = [r for r in results if r.status in ("WARN", "ERROR")]

    out("")
    out("--------------------------------")
    if blocking:
        out("총평: 차단 사유 %d건 (경고/오류 %d건). 위 [FAIL] 항목을 고치고 다시 커밋하세요." % (len(blocking), len(warns)))
        out("우회: 급하면 `git commit --no-verify`, 이번 커밋만 전체 게이트를 건너뛰려면 `SKIP_DECK_GATES=1 git commit ...`.")
        out("종료코드: 1")
        return 1

    out("총평: 차단 사유 없음 (경고/오류 %d건)." % len(warns))
    out("종료코드: 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
