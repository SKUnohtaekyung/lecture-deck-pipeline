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
              check_contract_waivers, check_tmp_litter]
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
