# -*- coding: utf-8 -*-
"""audit_context_budget 경로 유도 회귀 (배치1 P6 · 2026-08-17).

종전에는 PROJECT_KEY가 타인 환경("C--Users-miso-Desktop-template")으로
하드코딩돼 이 저장소에서 상시 미작동했다(ANALYSIS §4). 수리의 핵심이
Windows 경로 → 세션 폴더명 유도라, 그 변환을 여기 고정한다 —
PLAN P6이 지목한 유일한 함정이 «경로 유도 로직의 플랫폼 차이»다.
"""
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from scripts.audit_context_budget import derive_project_key, sessions_dir

REPO = Path(__file__).resolve().parent.parent


class DeriveProjectKeyTests(unittest.TestCase):
    def test_windows_path_with_space(self):
        # 실측 근거: 이 저장소의 실제 세션 폴더명(~/.claude/projects 실재 확인)
        self.assertEqual(
            derive_project_key(r"C:\Users\Noh TaeKyung\Desktop\lecture-deck-pipeline"),
            "C--Users-Noh-TaeKyung-Desktop-lecture-deck-pipeline")

    def test_hyphens_survive_and_specials_collapse_per_char(self):
        # 문자 단위 치환이다 — 연속 특수문자를 하나로 합치지 않는다(: + \ = '--')
        self.assertEqual(derive_project_key(r"C:\a b\c-d"), "C--a-b-c-d")

    def test_posix_path(self):
        self.assertEqual(derive_project_key("/home/user/proj"), "-home-user-proj")


class SessionsDirTests(unittest.TestCase):
    def test_default_derives_from_repo_root(self):
        d = sessions_dir()
        self.assertTrue(d.replace("\\", "/").endswith(
            "/.claude/projects/" + derive_project_key(str(REPO))))

    def test_missing_project_dir_exits_2(self):
        # 존재하지 않는 프로젝트를 지정하면 조용히 0을 내지 않고 2로 끝난다.
        proc = subprocess.run(
            [sys.executable, str(REPO / "scripts" / "audit_context_budget.py"),
             "--list", "--project-dir", str(REPO / "없는-프로젝트-경로")],
            capture_output=True, text=True, encoding="utf-8", cwd=str(REPO))
        self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)

    def test_project_dir_flag_requires_value(self):
        proc = subprocess.run(
            [sys.executable, str(REPO / "scripts" / "audit_context_budget.py"),
             "--list", "--project-dir"],
            capture_output=True, text=True, encoding="utf-8", cwd=str(REPO))
        self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()
