# -*- coding: utf-8 -*-
"""audit_context_budget 경로 유도 회귀 (배치1 P6 · 2026-08-17).

종전에는 PROJECT_KEY가 타인 환경("C--Users-miso-Desktop-template")으로
하드코딩돼 이 저장소에서 상시 미작동했다(ANALYSIS §4). 수리의 핵심이
Windows 경로 → 세션 폴더명 유도라, 그 변환을 여기 고정한다 —
PLAN P6이 지목한 유일한 함정이 «경로 유도 로직의 플랫폼 차이»다.

2026-09-11 추가: 블록 분할 기록 회귀(`_dev/설계기록/토큰감사-2026-09-11.md` §1).
한 응답이 블록마다 한 행씩 기록되는데 load()가 첫 행만 보고 tool_use를 찾아
T3가 오탐(실제 16.0% ↔ 보고 94.7%)했고, 서브에이전트 로그의 누적 output_tokens를
첫 행 값으로 과소 집계했다. 합성 fixture `tests/fixtures/synthetic/sess-split*`로 고정한다.
"""
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from scripts.audit_context_budget import (call_cost, derive_project_key, load,
                                          model_switches, sessions_dir,
                                          subagent_stats)

REPO = Path(__file__).resolve().parent.parent
FIX = REPO / "tests" / "fixtures" / "synthetic"


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


class SplitBlockLoadTests(unittest.TestCase):
    """같은 message.id의 여러 행을 한 호출로 합친다(도구는 모든 행 · usage는 최댓값)."""

    def setUp(self):
        self.calls, self.dup, self.bad = load(str(FIX / "sess-split.jsonl"))

    def test_rows_merge_into_calls(self):
        self.assertEqual(len(self.calls), 3)
        self.assertEqual(self.dup, 3, "첫 행 이후의 반복 행 수")
        self.assertEqual(self.bad, 0)

    def test_tool_use_in_later_row_is_kept(self):
        # 종전: 첫 행(thinking)만 봐서 세 호출 모두 «무도구»였다
        self.assertEqual([c["tools"] for c in self.calls], [["Bash"], [], ["Read"]])

    def test_output_tokens_use_row_maximum(self):
        # 종전: 첫 행 값 5 · 30 · 2
        self.assertEqual([c["out"] for c in self.calls], [40, 30, 25])

    def test_no_tool_cost_share(self):
        total = sum(call_cost(c) for c in self.calls)
        no_tool = sum(call_cost(c) for c in self.calls if not c["tools"])
        self.assertAlmostEqual(no_tool / total * 100, 29.15, places=1)

    def test_average_context_includes_input_and_cache_create(self):
        avg = sum(c["inp"] + c["cc"] + c["cr"] for c in self.calls) / len(self.calls)
        self.assertAlmostEqual(avg, (1102 + 2001 + 3001) / 3)

    def test_model_switch_detected(self):
        self.assertEqual(model_switches(self.calls), [("claude-opus-5", "claude-sonnet-5")])


class SubagentObservationTests(unittest.TestCase):
    """관측 T5·T7 — 서브에이전트 로그 집계와 API 오류 종료 표시."""

    def setUp(self):
        self.subs = {s["file"]: s for s in subagent_stats(str(FIX), "sess-split")}

    def test_both_logs_found_with_meta(self):
        self.assertEqual(set(self.subs), {"agent-aSPLIT0001.jsonl", "agent-aERR00001x.jsonl"})
        self.assertEqual(self.subs["agent-aERR00001x.jsonl"]["desc"], "interrupted worker")

    def test_api_error_flag(self):
        self.assertTrue(self.subs["agent-aERR00001x.jsonl"]["api_error"])
        self.assertFalse(self.subs["agent-aSPLIT0001.jsonl"]["api_error"])

    def test_subagent_cost_uses_merged_rows(self):
        # 입력 10 + 출력 최댓값 20×5 = 110 (종전 첫 행 8이면 50)
        self.assertEqual(self.subs["agent-aSPLIT0001.jsonl"]["cost"], 110)
        self.assertEqual(self.subs["agent-aERR00001x.jsonl"]["cost"], 90)

    def test_missing_subagent_folder_is_empty(self):
        self.assertEqual(subagent_stats(str(FIX), "sess-없음"), [])


if __name__ == "__main__":
    unittest.main()
