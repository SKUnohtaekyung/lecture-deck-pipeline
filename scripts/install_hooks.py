#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""git core.hooksPath를 저장소 안 .githooks/로 설정하는 설치 스크립트.

왜: git 훅(pre-commit 등)이 저장소를 클론한 사람 모두에게 자동 적용되게 하려면
`core.hooksPath`를 저장소 안 버전관리되는 `.githooks/`로 돌려놔야 한다. git 기본값
(`.git/hooks/`)은 clone에 포함되지 않아 사람마다 따로 설정해야 하고, 그러면 훅이
"있는 사람만 걸리는" 상태가 되어 사실상 강제가 아니게 된다.

사용:
  python scripts/install_hooks.py           # 설정하고 재확인
  python scripts/install_hooks.py --check   # 설정만 확인(바꾸지 않음)

표준 라이브러리(subprocess)만 사용한다. 여러 번 실행해도 안전하다(멱등) —
이미 올바르게 설정돼 있으면 그 사실만 알리고 바꾸지 않는다.
"""
import os
import sys
import subprocess

HOOKS_PATH = ".githooks"


def out(text):
    """stdout이 cp949여도 깨지지 않게 UTF-8 바이트로 직접 쓴다.
    (Windows 콘솔 기본 인코딩에서 print()/write()는 em dash 같은 문자에서
    UnicodeEncodeError로 죽는다 — hook_slide_guard.py의 emit()과 같은 이유.)"""
    try:
        sys.stdout.buffer.write((text + "\n").encode("utf-8"))
        sys.stdout.buffer.flush()
    except Exception:
        try:
            sys.stdout.write(text + "\n")
        except Exception:
            pass


def repo_root():
    """이 스크립트(scripts/install_hooks.py) 위치의 부모를 저장소 루트로 본다.
    실행 디렉터리에 의존하지 않기 위해 git 명령은 전부 이 경로에서 돈다."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_git(args):
    """git 명령을 저장소 루트에서 실행하고 (returncode, stdout) 반환.
    git 자체가 없거나 실행 실패해도 예외를 던지지 않는다."""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=repo_root(),
            capture_output=True,
            text=True,
        )
        return result.returncode, (result.stdout or "").strip()
    except FileNotFoundError:
        return 127, ""


def is_git_repo():
    code, _ = run_git(["rev-parse", "--is-inside-work-tree"])
    return code == 0


def get_hooks_path():
    """현재 설정된 core.hooksPath. 미설정이면 None."""
    code, out = run_git(["config", "--get", "core.hooksPath"])
    if code != 0 or not out:
        return None
    return out


def main():
    check_only = "--check" in sys.argv[1:]

    if not is_git_repo():
        out("git 저장소가 아닙니다: %s (여기서는 훅을 설치할 수 없습니다)" % repo_root())
        sys.exit(1)

    current = get_hooks_path()

    if check_only:
        if current == HOOKS_PATH:
            out("core.hooksPath = %s (정상)" % HOOKS_PATH)
            sys.exit(0)
        out(
            "core.hooksPath = %s (기대값 %s 아님 — "
            "`python scripts/install_hooks.py`로 설정하세요)"
            % (current or "(미설정)", HOOKS_PATH)
        )
        sys.exit(1)

    if current == HOOKS_PATH:
        out("이미 설정되어 있습니다: core.hooksPath = %s" % HOOKS_PATH)
        sys.exit(0)

    code, _ = run_git(["config", "core.hooksPath", HOOKS_PATH])
    if code != 0:
        out("core.hooksPath 설정에 실패했습니다.")
        sys.exit(1)

    verify = get_hooks_path()
    if verify == HOOKS_PATH:
        out("설정 완료: core.hooksPath = %s" % HOOKS_PATH)
        sys.exit(0)
    else:
        out("설정 후 검증에 실패했습니다 (읽은 값: %s)" % (verify or "(미설정)"))
        sys.exit(1)


if __name__ == "__main__":
    main()
