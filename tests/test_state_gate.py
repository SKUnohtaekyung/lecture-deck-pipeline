#!/usr/bin/env python3
"""STATE.md pre-commit 게이트 회귀 (2026-10-08).

막으려는 것: 열린 과업 색인이 다시 이력 더미가 되는 것. `MEMORY.md`의 `## 미해결`이
547행까지 불어나 끝난 일과 낡은 수치가 섞였던 경위는 `plans/agent-system-audit/`에 있다.

검사 대상은 `.githooks/_gate.py`의 `state_violations`(순수 함수)와 `check_state_file`
(staged 내용을 읽는 배선)이다. 배선 테스트는 저장소 안 `tmp/`에 일회용 git 저장소를 만든다.
"""
from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import unittest
import uuid
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GATE_PATH = REPO_ROOT / ".githooks" / "_gate.py"

_spec = importlib.util.spec_from_file_location("_gate_under_test", str(GATE_PATH))
gate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gate)

HEADER = "| ID | 범위 | 한 줄 상태 | 다음 행동 | 담당 | 상세 위치 | 확인일 |\n|---|---|---|---|---|---|---|\n"


def _row(i: int, date: str = "2026-10-08") -> str:
    return "| S%02d | 공통 | 상태 | 다음 | 에이전트 | 아래 | %s |\n" % (i, date)


def _doc(rows: int = 3, cap: str = "- 상한: 색인 40행, 파일 4KB.\n", date: str = "2026-10-08", pad: int = 0) -> bytes:
    body = "# STATE\n\n" + cap + "\n## 색인\n\n" + HEADER
    body += "".join(_row(i + 1, date) for i in range(rows))
    body += "\n## 상세\n\n" + ("가" * pad) + "\n"
    return body.encode("utf-8")


class StateViolationsTests(unittest.TestCase):
    def test_healthy_document_passes_and_reports_counts(self):
        raw = _doc(rows=3)
        n, size, cap, v = gate.state_violations(raw)
        self.assertEqual((n, size, cap, v), (3, len(raw), 4, []))

    def test_repository_state_file_passes(self):
        """지금 저장소의 STATE.md가 이 게이트를 통과한다(행 수는 눈먼 0이 아니어야 한다)."""
        raw = (REPO_ROOT / "STATE.md").read_bytes()
        n, size, cap, v = gate.state_violations(raw)
        self.assertEqual(v, [])
        self.assertGreater(n, 0)
        self.assertEqual(size, len(raw))

    def test_forty_rows_pass_forty_one_fail(self):
        big_cap = "- 상한: 색인 40행, 파일 64KB.\n"
        self.assertEqual(gate.state_violations(_doc(rows=40, cap=big_cap))[3], [])
        n, _, _, v = gate.state_violations(_doc(rows=41, cap=big_cap))
        self.assertEqual(n, 41)
        self.assertEqual(len(v), 1)
        self.assertIn("상한 40행 초과", v[0])

    def test_size_over_declared_cap_fails(self):
        ok = _doc(rows=1, pad=100)
        self.assertEqual(gate.state_violations(ok)[3], [])
        over = _doc(rows=1, pad=2000)  # 한글 2000자 = 6000바이트 > 4KB
        _, size, cap, v = gate.state_violations(over)
        self.assertGreater(size, cap * 1024)
        self.assertTrue(any("초과" in x and "바이트" in x for x in v))

    def test_size_exactly_at_cap_passes(self):
        base = _doc(rows=1)
        raw = base + b"a" * (4 * 1024 - len(base))
        self.assertEqual(len(raw), 4096)
        self.assertEqual(gate.state_violations(raw)[3], [])
        self.assertTrue(gate.state_violations(raw + b"a")[3])

    def test_missing_cap_declaration_fails(self):
        v = gate.state_violations(_doc(cap=""))[3]
        self.assertTrue(any("크기 상한 선언이 없다" in x for x in v))

    def test_empty_checked_date_fails(self):
        v = gate.state_violations(_doc(rows=2, date=""))[3]
        self.assertEqual(len(v), 2)
        self.assertTrue(all("빈 칸" in x and "확인일" in x for x in v))

    def test_malformed_checked_date_fails(self):
        for bad in ("10월 8일", "2026-10", "확인필요", "미정"):
            v = gate.state_violations(_doc(rows=1, date=bad))[3]
            self.assertTrue(any("확인일" in x for x in v), bad)

    def test_needs_check_marker_is_accepted(self):
        self.assertEqual(gate.state_violations(_doc(rows=2, date="확인 필요"))[3], [])

    def test_empty_cell_other_than_date_fails(self):
        raw = _doc(rows=1).replace("| 상태 |".encode("utf-8"), "|  |".encode("utf-8"))
        v = gate.state_violations(raw)[3]
        self.assertTrue(any("빈 칸" in x and "한 줄 상태" in x for x in v))

    def test_wrong_column_count_fails(self):
        raw = _doc(rows=1) .replace("| 에이전트 |".encode("utf-8"), "|".encode("utf-8"))
        v = gate.state_violations(raw)[3]
        self.assertTrue(any("열 6개" in x for x in v))

    def test_missing_index_table_fails_instead_of_passing_blind(self):
        raw = "# STATE\n\n- 상한: 색인 40행, 파일 4KB.\n\n표가 없다.\n".encode("utf-8")
        n, _, _, v = gate.state_violations(raw)
        self.assertEqual(n, 0)
        self.assertTrue(any("색인 표를 찾지 못했다" in x for x in v))

    def test_renamed_header_fails(self):
        raw = _doc(rows=1).replace("확인일 |".encode("utf-8"), "날짜 |".encode("utf-8"), 1)
        self.assertTrue(any("색인 표를 찾지 못했다" in x for x in gate.state_violations(raw)[3]))

    def test_crlf_document_is_parsed(self):
        raw = _doc(rows=3).replace(b"\n", b"\r\n")
        n, _, _, v = gate.state_violations(raw)
        self.assertEqual((n, v), (3, []))

    # ── 세는 범위를 좁게 잡아 생기는 «눈먼 0» (2026-10-08 검토에서 재현) ──────────
    def test_indented_rows_are_still_counted(self):
        big_cap = "- 상한: 색인 40행, 파일 64KB.\n"
        for indent in (" ", "  ", "   ", "\t"):
            raw = _doc(rows=50, cap=big_cap).replace(b"\n| S", ("\n" + indent + "| S").encode("utf-8"))
            n, _, _, v = gate.state_violations(raw)
            self.assertEqual(n, 50, repr(indent))
            self.assertTrue(any("상한 40행 초과" in x for x in v), repr(indent))

    def test_indented_row_with_empty_date_is_caught(self):
        raw = _doc(rows=3).replace(_row(2).encode("utf-8"), (" " + _row(2, "")).encode("utf-8"))
        n, _, _, v = gate.state_violations(raw)
        self.assertEqual(n, 3)
        self.assertTrue(any("S02" in x and "확인일" in x for x in v), v)

    def test_blank_line_after_header_does_not_hide_rows(self):
        big_cap = "- 상한: 색인 40행, 파일 64KB.\n"
        raw = _doc(rows=50, cap=big_cap).replace(HEADER.encode("utf-8"), (HEADER + "\n").encode("utf-8"))
        n, _, _, v = gate.state_violations(raw)
        self.assertEqual(n, 50)
        self.assertTrue(any("상한 40행 초과" in x for x in v))

    def test_rows_split_across_two_tables_are_summed(self):
        big_cap = "- 상한: 색인 40행, 파일 64KB.\n"
        body = "# STATE\n\n" + big_cap + "\n## 색인\n\n" + HEADER
        body += "".join(_row(i + 1) for i in range(30)) + "\n" + HEADER
        body += "".join(_row(i + 31) for i in range(30)) + "\n## 상세\n"
        n, _, _, v = gate.state_violations(body.encode("utf-8"))
        self.assertEqual(n, 60)
        self.assertTrue(any("상한 40행 초과" in x for x in v))

    def test_rows_without_leading_or_trailing_pipe_are_counted(self):
        """마크다운 표는 행 맨 앞·맨 뒤의 `|`를 생략할 수 있다."""
        big_cap = "- 상한: 색인 40행, 파일 64KB.\n"
        bare = "".join("S%02d | 공통 | 상태 | 다음 | 에이전트 | 아래 | 2026-10-08\n" % (i + 1) for i in range(50))
        body = "# STATE\n\n" + big_cap + "\n## 색인\n\n" + HEADER + bare + "\n## 상세\n"
        n, _, _, v = gate.state_violations(body.encode("utf-8"))
        self.assertEqual(n, 50)
        self.assertTrue(any("상한 40행 초과" in x for x in v))
        one = "# STATE\n\n- 상한: 파일 4KB.\n\n" + HEADER + "S01 | 공통 | 상태 | 다음 | 에이전트 | 아래 | \n"
        n1, _, _, v1 = gate.state_violations(one.encode("utf-8"))
        self.assertEqual(n1, 1)
        # 맨 뒤 `|`를 생략하고 마지막 칸을 비우면 «빈 칸»과 «열 부족»을 구분할 수 없다 — 어느 쪽이든 막는다.
        self.assertTrue(any(x.startswith("S01:") for x in v1), v1)

    def test_prose_without_a_pipe_in_the_index_section_is_ignored(self):
        raw = _doc(rows=2).replace("\n## 상세".encode("utf-8"), "\n표 아래의 설명 문장이다.\n\n## 상세".encode("utf-8"))
        n, _, _, v = gate.state_violations(raw)
        self.assertEqual((n, v), (2, []))

    def test_missing_separator_line_does_not_swallow_first_row(self):
        raw = _doc(rows=2, date="").replace(b"|---|---|---|---|---|---|---|\n", b"")
        n, _, _, v = gate.state_violations(raw)
        self.assertEqual(n, 2)
        self.assertEqual(len([x for x in v if "확인일" in x]), 2)

    def test_tables_in_detail_sections_are_not_counted(self):
        raw = _doc(rows=2) + "### S01\n\n| 항목 | 값 |\n|---|---|\n| a | b |\n".encode("utf-8")
        n, _, _, v = gate.state_violations(raw)
        self.assertEqual((n, v), (2, []))

    def test_escaped_pipe_inside_a_cell_is_not_a_column_break(self):
        raw = _doc(rows=1).replace("| 상태 |".encode("utf-8"), "| a \\| b |".encode("utf-8"))
        self.assertEqual(gate.state_violations(raw)[3], [])

    def test_bom_is_ignored(self):
        body = "﻿" + HEADER + _row(1) + "\n- 상한: 파일 4KB\n"
        n, _, _, v = gate.state_violations(body.encode("utf-8"))
        self.assertEqual((n, v), (1, []))

    def test_cap_declaration_accepts_space_and_decimal(self):
        for cap in ("파일 4 KB", "파일 4.5KB", "파일4KB"):
            self.assertEqual(gate.state_violations(_doc(rows=1, cap="- 상한: %s.\n" % cap))[3], [], cap)
        over = _doc(rows=1, cap="- 상한: 파일 0.1KB.\n")
        self.assertTrue(any("초과" in x for x in gate.state_violations(over)[3]))

    def test_impossible_calendar_dates_fail(self):
        for bad in ("2026-13-45", "2026-02-30", "2026-00-10", "2025-02-29"):
            self.assertTrue(any("확인일" in x for x in gate.state_violations(_doc(rows=1, date=bad))[3]), bad)
        self.assertEqual(gate.state_violations(_doc(rows=1, date="2024-02-29"))[3], [])

    def test_non_utf8_fails(self):
        self.assertTrue(gate.state_violations(b"\xff\xfe\x00bad")[3])


class CheckStateFileWiringTests(unittest.TestCase):
    """staged 내용을 읽는지 — 작업 트리가 아니라 index를 본다."""

    def setUp(self):
        self.repo = REPO_ROOT / "tmp" / ("state-gate-test-" + uuid.uuid4().hex)
        self.repo.mkdir(parents=True)
        self._git("init", "-q")
        self._git("config", "user.email", "t@example.invalid")
        self._git("config", "user.name", "t")
        self._git("config", "core.autocrlf", "false")
        self._cwd = os.getcwd()
        os.chdir(str(self.repo))  # 게이트는 커밋 중인 트리를 cwd에서 찾는다

    def tearDown(self):
        os.chdir(self._cwd)

        def _force(func, path, _exc):
            os.chmod(path, 0o700)
            func(path)

        shutil.rmtree(str(self.repo), onerror=_force)

    def _git(self, *args):
        subprocess.run(["git", *args], cwd=str(self.repo), check=True, capture_output=True)

    def _stage(self, raw: bytes):
        (self.repo / "STATE.md").write_bytes(raw)
        self._git("add", "STATE.md")

    def test_not_staged_is_reported_as_not_applicable(self):
        r = gate.check_state_file(str(self.repo), ["README.md"])
        self.assertEqual(r.status, "SKIP")
        self.assertIn("해당 없음", r.detail)

    def test_staged_healthy_passes_with_counts(self):
        raw = _doc(rows=3)
        self._stage(raw)
        r = gate.check_state_file(str(self.repo), ["STATE.md"])
        self.assertEqual(r.status, "PASS")
        self.assertIn("색인 3행", r.detail)
        self.assertIn("%d바이트" % len(raw), r.detail)

    def test_staged_violation_blocks_with_counts(self):
        self._stage(_doc(rows=41, cap="- 상한: 색인 40행, 파일 64KB.\n"))
        r = gate.check_state_file(str(self.repo), ["STATE.md"])
        self.assertEqual(r.status, "FAIL")
        self.assertIn("색인 41행", r.detail)

    def test_reads_index_not_working_tree(self):
        self._stage(_doc(rows=41, cap="- 상한: 색인 40행, 파일 64KB.\n"))
        (self.repo / "STATE.md").write_bytes(_doc(rows=1))  # 작업 트리만 고침 — stage 안 함
        r = gate.check_state_file(str(self.repo), ["STATE.md"])
        self.assertEqual(r.status, "FAIL", "작업 트리가 아니라 staged 내용을 판정해야 한다")

    def test_staged_deletion_warns(self):
        """삭제는 게이트의 staged 목록(ACMR)에 없다 — 그 목록 그대로 넘겨도 경고가 나와야 한다."""
        self._stage(_doc(rows=1))
        self._git("commit", "-q", "-m", "x", "--no-verify")
        self._git("rm", "-q", "STATE.md")
        staged = gate.get_staged_files(str(self.repo))
        self.assertNotIn("STATE.md", staged)
        r = gate.check_state_file(str(self.repo), staged)
        self.assertEqual(r.status, "WARN")
        self.assertIn("삭제", r.detail)

    def test_check_is_registered_in_main(self):
        src = GATE_PATH.read_text(encoding="utf-8")
        self.assertRegex(src, r"checks = \[[^\]]*check_state_file[^\]]*\]")


if __name__ == "__main__":
    unittest.main()
