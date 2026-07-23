#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analyze_agent_usage.py 계측기 자체 검증.

숫자가 맞는지만 보고 계측기를 신뢰하지 않기 위한 테스트다.
입력은 개인정보가 없는 합성 fixture(`tests/fixtures/synthetic/`)만 쓴다.
실제 사용자 로그를 복사하지 않는다.

실행:
    python tests/test_analyze_agent_usage.py
    python -m unittest tests.test_analyze_agent_usage
"""

import hashlib
import io
import os
import re
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCRIPT = os.path.join(ROOT, "scripts", "analyze_agent_usage.py")
FIX = os.path.join(HERE, "fixtures", "synthetic")
SESSION = "sess-test"
WF = "wf_test-001"

FIXTURE_FILES = [
    os.path.join(FIX, f"{SESSION}.jsonl"),
    os.path.join(FIX, SESSION, "subagents", "workflows", WF,
                 "agent-aWORKER01x.jsonl"),
]


def run(*extra):
    """계측기를 subprocess로 실행하고 stdout을 돌려준다."""
    cmd = [sys.executable, SCRIPT,
           "--projects-dir", FIX,
           "--session", SESSION,
           "--workflows", WF,
           "--archive", "",
           "--no-baseline", *extra]
    p = subprocess.run(cmd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=ROOT)
    if p.returncode not in (0, 2):
        raise AssertionError(f"실행 실패 rc={p.returncode}\n{p.stdout}\n{p.stderr}")
    return p.stdout


def fingerprint():
    out = []
    for f in FIXTURE_FILES:
        st = os.stat(f)
        h = hashlib.sha256(io.open(f, "rb").read()).hexdigest()
        out.append((os.path.basename(f), st.st_size, st.st_mtime_ns, h))
    return out


def num(text, pattern):
    m = re.search(pattern, text)
    if not m:
        raise AssertionError(f"패턴 미발견: {pattern}")
    return int(m.group(1).replace(",", ""))


class TestReadOnly(unittest.TestCase):
    """① 원시 로그를 쓰거나 수정하는 코드가 없는지 (정적 검사)"""

    def test_no_write_apis_in_source(self):
        src = io.open(SCRIPT, encoding="utf-8").read()
        # 쓰기·삭제 계열 호출이 전혀 없어야 한다.
        banned = [
            r"open\([^)]*['\"][wax]",      # open(..., 'w'/'a'/'x')
            r"\.write\(",
            r"os\.remove", r"os\.unlink", r"os\.rename", r"os\.replace",
            r"shutil\.", r"os\.makedirs", r"os\.mkdir",
            r"Path\([^)]*\)\.write",
        ]
        for pat in banned:
            hits = [ln for ln in src.splitlines() if re.search(pat, ln)]
            self.assertEqual(hits, [], f"쓰기 계열 호출 발견 ({pat}): {hits}")

    def test_inputs_unchanged_after_run(self):
        before = fingerprint()
        run()
        after = fingerprint()
        self.assertEqual(before, after,
                         "실행 전후 입력 파일의 크기·수정시각·해시가 달라졌다")


class TestAnomalyReporting(unittest.TestCase):
    """② 이상 징후를 조용히 건너뛰지 않는지"""

    def setUp(self):
        self.out = run()

    def test_bad_line_reported(self):
        self.assertIn("파싱 실패 줄        : 1건", self.out)
        self.assertIn("broken json line", self.out,
                      "파싱 실패한 줄의 내용이 보고되지 않았다")

    def test_missing_usage_fields_reported(self):
        self.assertIn("usage 필드 누락", self.out)
        self.assertIn("cache_creation_input_tokens", self.out)
        self.assertIn("cache_read_input_tokens", self.out)

    def test_unknown_model_reported(self):
        self.assertIn("가격표 미등재 모델", self.out)
        self.assertIn("claude-unknown-9", self.out)
        self.assertIn("토큰은 집계, 비용은 제외", self.out)

    def test_assistant_without_usage_counted_separately(self):
        self.assertIn("usage 없는 assistant: 1건", self.out)


class TestTokenAggregation(unittest.TestCase):
    """③ 토큰 집계가 fixture 기대값과 일치하는지"""

    def setUp(self):
        self.out = run()

    def test_totals(self):
        # 메인 1턴: 10 + 100 + 0 + 5 = 115
        # 워커 4턴: (20+200+50+10) + (30+0+0+0) + (5+0+500+0) + (1+0+10+2) = 828
        #   ※ usage 없는 assistant 레코드는 턴으로 세지 않는다
        self.assertRegex(self.out, r"메인\s+1\s+1\s+115")
        self.assertRegex(self.out, r"워커\s+1\s+4\s+828")
        self.assertRegex(self.out, r"합계\s+2\s+5\s+943")

    def test_zero_output_record_included(self):
        # 출력 토큰 0인 레코드도 턴으로 세어야 한다 (워커 4턴에 이미 반영)
        self.assertRegex(self.out, r"워커\s+1\s+4\s")


class TestUrlCanonicalization(unittest.TestCase):
    """④ URL 정규화와 용어 분리"""

    def setUp(self):
        self.out = run()

    def test_canon_rule_printed(self):
        self.assertIn("canonical URL", self.out)
        self.assertIn("쿼리·프래그먼트 제거", self.out)

    def test_terms_are_separated(self):
        # fixture 기대값:
        #   전 에이전트 ① 4회 ② 2고유 ③ 1종류 ④ 2초과
        #   워커만      ① 3회 ② 2고유 ③ 1종류 ④ 1초과
        # trailing slash / www / 대문자 / query / fragment 가 모두
        # https://example.com/a 하나로 접혀야 성립한다.
        self.assertRegex(self.out, r"① 전체 호출 수\s+4\s+3\s+1")
        self.assertRegex(self.out, r"② canonical 고유 URL 수\s+2\s+2\s+0")
        self.assertRegex(self.out, r"③ 중복된 URL '종류' 수\(≥2회\)\s+1\s+1\s+0")
        self.assertRegex(self.out, r"④ 고유 URL 초과 추가 호출 수\(①−②\)\s+2\s+1\s+1")


class TestScopeSelection(unittest.TestCase):
    """⑤ 집계 범위를 명시적으로 선택할 수 있는지"""

    def test_scope_main(self):
        out = run("--scope", "main")
        self.assertIn("[--scope main]", out)
        self.assertIn("2 → 1개 에이전트", out)

    def test_scope_worker(self):
        out = run("--scope", "worker")
        self.assertIn("[--scope worker]", out)
        self.assertIn("2 → 1개 에이전트", out)

    def test_scope_all_is_default(self):
        self.assertNotIn("[--scope", run())


class TestDeterminism(unittest.TestCase):
    """⑥ 동일 입력을 두 번 실행하면 동일 결과"""

    def test_two_runs_identical(self):
        a, b = run(), run()
        self.assertEqual(a, b, "동일 입력에 대해 출력이 달라졌다")


class TestCostSeparation(unittest.TestCase):
    """⑦ 비용표와 토큰 집계 로직이 분리돼 있는지"""

    def test_collect_does_not_use_price_table(self):
        """토큰 집계 함수가 가격표를 참조하지 않아야 한다."""
        src = io.open(SCRIPT, encoding="utf-8").read()
        start = src.index("def collect(")
        end = src.index("def pearson(")
        body = src[start:end]
        # collect()는 미등재 모델 '경고'만 하고 단가를 쓰지 않는다.
        self.assertNotIn("CACHE_WRITE_MULT", body)
        self.assertNotIn("CACHE_READ_MULT", body)
        self.assertNotIn("cost_of", body)

    def test_price_change_does_not_alter_token_counts(self):
        """가격표를 바꿔도 원시 토큰 집계는 동일해야 한다."""
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import importlib
        mod = importlib.import_module("analyze_agent_usage")
        importlib.reload(mod)

        worker = FIXTURE_FILES[1]
        base = mod.collect(worker, "w", "worker", WF)
        tokens_before = (base.inp, base.cc, base.cr, base.out, base.turns)
        cost_before = mod.cost_of("claude-sonnet-5", base.inp, base.cc,
                                  base.cr, base.out)

        mod.PRICE_TABLE["claude-sonnet-5"] = (30.0, 150.0)   # 10배
        again = mod.collect(worker, "w", "worker", WF)
        tokens_after = (again.inp, again.cc, again.cr, again.out, again.turns)
        cost_after = mod.cost_of("claude-sonnet-5", again.inp, again.cc,
                                 again.cr, again.out)

        self.assertEqual(tokens_before, tokens_after,
                         "가격표 변경이 토큰 집계에 영향을 줬다")
        self.assertAlmostEqual(cost_after, cost_before * 10, places=9,
                               msg="가격표 변경이 비용에 반영되지 않았다")


class TestToolAudit(unittest.TestCase):
    """⑧ Phase 2 워커 도구·모델 감사 (--tool-audit)

    안 「가」(Explore + sonnet)에서는 `Bash` 등이 구조적으로 차단되지 않는다.
    이 감사가 유일한 강제 수단이므로, 감사 자체가 위반을 놓치지 않는지 검사한다.
    """

    AUDIT_SESSION = "sess-audit"

    def audit(self, *extra):
        cmd = [sys.executable, SCRIPT, "--tool-audit",
               "--projects-dir", FIX,
               "--session", self.AUDIT_SESSION, *extra]
        p = subprocess.run(cmd, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", cwd=ROOT)
        return p.returncode, p.stdout

    def test_direct_agent_layout_is_discovered(self):
        """직접 `Agent` 호출은 workflows/ 아래가 아니라 subagents/ 바로 밑에 쌓인다."""
        _, out = self.audit()
        self.assertIn("직접 Agent 2개", out)
        self.assertIn("워크플로 0개", out)

    def test_violation_detected_and_exit_code(self):
        rc, out = self.audit()
        self.assertEqual(rc, 3, "위반이 있는데 종료코드가 3이 아니다")
        self.assertIn("Bash×1", out)
        self.assertIn("PowerShell×1", out)
        self.assertIn("판정: ❌ 위반 있음", out)

    def test_opus_fallback_is_called_out(self):
        _, out = self.audit()
        self.assertIn("모델 불일치", out)
        self.assertIn("Opus fallback", out,
                      "Opus 전환이 계획상 RED임을 명시하지 않았다")

    def test_clean_agent_passes_when_scoped_by_allowlist(self):
        """허용목록을 넓히면 같은 로그가 통과해야 한다(감사 기준이 allowlist에서 온다)."""
        rc, out = self.audit("--allow", "WebSearch,WebFetch,Read,Grep,Glob,Bash,PowerShell",
                             "--expect-model", "claude-opus-4-8")
        self.assertIn("허용목록 외 호출 0건", out)
        # 모델 기대치를 opus로 바꾸면 이번엔 sonnet 워커가 불일치로 잡힌다.
        self.assertEqual(rc, 3)
        self.assertIn("claude-sonnet-5", out)

    def test_allowed_tools_are_not_flagged(self):
        _, out = self.audit()
        self.assertRegex(out, r"aCLEAN0001.*Glob×1, Grep×1, Read×1, WebFetch×1, WebSearch×1")
        self.assertNotRegex(out, r"aCLEAN0001.*⛔")

    def test_lead_row_is_observational_not_audited(self):
        """리드(메인)는 Write·Bash를 정당하게 쓰므로 위반으로 잡으면 안 된다."""
        _, out = self.audit("--session", "sess-test")
        self.assertIn("[리드]", out)
        self.assertIn("Read×", out)
        self.assertIn("허용목록 검사 대상이 아니다", out)
        # 리드가 어떤 위반 목록에도 등장하면 안 된다.
        # (sess-test는 워커 모델이 미등재라 종료코드 자체는 3이 정상이다.)
        offenders = [ln for ln in out.splitlines()
                     if "허용목록 외 도구" in ln or "모델 불일치" in ln]
        for ln in offenders:
            self.assertNotIn("[리드]", ln, f"리드가 위반으로 잡혔다: {ln}")
            self.assertNotIn("main", ln, f"리드가 위반으로 잡혔다: {ln}")

    def test_duplicate_url_stopline(self):
        """§0.5 — 동일 canonical URL 재호출은 1회까지. 정규화 후 판정해야 한다."""
        rc, out = self.audit("--session", "sess-dup")
        # 3회 호출이 전부 같은 canonical URL → 재호출 2회 (중단선 1 초과)
        self.assertIn("동일URL재호출×2", out)
        self.assertIn("§0.5 중단선 1", out)
        self.assertEqual(rc, 3, "동일 URL 재호출 초과인데 종료코드가 3이 아니다")

    def test_no_duplicate_url_passes(self):
        _, out = self.audit("--session", "sess-audit")
        self.assertIn("동일 URL 재호출: 중단선(1) 이내", out)

    def test_toolsearch_is_allowed_as_prerequisite(self):
        """WebSearch·WebFetch가 deferred라 ToolSearch 없이는 조사가 불가능하다."""
        import importlib
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        mod = importlib.import_module("analyze_agent_usage")
        importlib.reload(mod)
        self.assertIn("ToolSearch", mod.WORKER_TOOL_ALLOWLIST)
        for banned in ("Bash", "PowerShell", "Write", "Edit", "Agent"):
            self.assertNotIn(banned, mod.WORKER_TOOL_ALLOWLIST,
                             f"{banned}가 허용목록에 들어갔다")

    def test_turns_counted_per_usage_record(self):
        _, out = self.audit()
        self.assertRegex(out, r"aCLEAN0001\s+direct\s+claude-sonnet-5\s+3")
        self.assertRegex(out, r"aBAD00002x\s+direct\s+claude-opus-4-8\s+2")


if __name__ == "__main__":
    unittest.main(verbosity=2)
