# -*- coding: utf-8 -*-
"""PreToolUse 훅(`scripts/hook_slide_guard.py`)의 판정 회귀 테스트.

왜 이 파일이 필요한가
--------------------
훅은 `AGENTS.md` 「무엇이 기계로 강제되는가」 표에 **강제 계층**으로 올라 있는데,
2026-08-18까지 **회귀 테스트가 0개였다.** 검증은 `tmp/test_gate.py`라는 임시
스크립트로만 있었고 `tmp/`는 `.gitignore`돼 있어 클론에 남지 않는다. 즉 강제
계층이 조용히 망가져도 아무 게이트가 울리지 않는 상태였다.

무엇을 테스트하나
----------------
- `tmp-guard`의 **오탐 예외**(에이전트 영속 메모리) — 넓게 뚫리지 않았는지 함께 본다.
- 관측 모드가 **차단하지 않는다**는 계약과, `--enforce`가 실제로 차단한다는 계약.

⚠️ 여기서 «통과»는 「훅이 이 경로를 어떻게 판정하는가」까지다. 호스트(Claude
Code·Codex)가 그 출력을 실제로 존중하는지는 이 테스트의 범위가 아니다 —
Codex 쪽은 페이로드에 파일 경로 키 자체가 없다(2026-08-18 Gate 0 실측).

실행: python -m unittest tests.test_hook_guards
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
HOOK = REPO_ROOT / "scripts" / "hook_slide_guard.py"

sys.path.insert(0, str(REPO_ROOT / "scripts"))
from hook_slide_guard import is_persistent_agent_memory  # noqa: E402


def _home() -> str:
    return os.path.abspath(os.path.expanduser("~")).replace(os.sep, "/")


def _run_hook(path: str, *extra: str):
    """훅을 실제 프로세스로 돌려 (stdout, returncode)를 돌려준다."""
    payload = json.dumps({"tool_input": {"file_path": path}})
    proc = subprocess.run(
        [sys.executable, str(HOOK), "--mode", "tmp-guard", *extra],
        input=payload, capture_output=True, text=True, encoding="utf-8",
        cwd=str(REPO_ROOT),
    )
    return proc.stdout or "", proc.returncode


class TmpGuardAllowlistTests(unittest.TestCase):
    """오탐 예외가 «좁게» 뚫렸는지 — 넓게 뚫는 것이 이 저장소의 전형적 실패다."""

    def test_agent_memory_dir_is_allowed(self):
        """2026-08-17 관측 모드가 잡은 1건. 시스템이 지정한 영속 경로이므로 오탐이다."""
        for p in (
            _home() + "/.claude/projects/C--Users-miso-Desktop-template/memory/x.md",
            _home() + "/.claude/projects/other-key/memory/nested/y.md",
        ):
            self.assertTrue(is_persistent_agent_memory(p), f"허용돼야 한다: {p}")

    def test_allowlist_does_not_open_the_home_directory(self):
        """예외를 「홈 전체」로 넓히면 규칙이 사실상 사라진다 — 그 회귀를 막는다."""
        for p in (
            _home() + "/.claude/projects/key/other/x.md",   # memory/ 가 아니다
            _home() + "/.claude/projects/key.md",           # 프로젝트 키 층이 없다
            _home() + "/.claude/settings.json",
            _home() + "/memory/x.md",                       # projects/ 를 안 거쳤다
            _home() + "/x.md",
            "C:/Windows/Temp/x.txt",
            "/tmp/x.txt",
        ):
            self.assertFalse(is_persistent_agent_memory(p), f"막혀야 한다: {p}")

    def test_allowed_path_produces_no_warning(self):
        out, code = _run_hook(_home() + "/.claude/projects/k/memory/z.md")
        self.assertEqual(code, 0)
        self.assertNotIn("저장소 밖", out, "허용 경로인데 경고가 나왔다")

    def test_outside_path_still_warns_in_observe_mode(self):
        """예외를 넣다가 검출 자체를 죽이지 않았는지 — 정탐이 살아 있어야 한다."""
        out, code = _run_hook("C:/Windows/Temp/x.txt")
        self.assertEqual(code, 0, "관측 모드는 차단하지 않는다")
        self.assertIn("저장소 밖", out)
        self.assertIn("관측 모드", out, "관측 모드임이 출력에 드러나야 한다")
        self.assertNotIn('"decision": "block"', out, "관측 모드가 차단하면 계약 위반이다")

    def test_enforce_blocks_outside_path(self):
        out, _ = _run_hook("C:/Windows/Temp/x.txt", "--enforce")
        self.assertIn("block", out, "--enforce는 실제로 차단해야 한다")

    def test_enforce_does_not_block_allowed_path(self):
        out, _ = _run_hook(_home() + "/.claude/projects/k/memory/z.md", "--enforce")
        self.assertNotIn("block", out, "허용 경로는 승격 후에도 통과해야 한다")

    def test_inside_repo_path_is_silent(self):
        out, code = _run_hook(str(REPO_ROOT / "tmp" / "scratch.txt"))
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), "", "저장소 안 쓰기는 아무 말도 하지 않는다")


if __name__ == "__main__":
    unittest.main()
