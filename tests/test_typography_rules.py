# -*- coding: utf-8 -*-
"""브라우저 JS 검출기(scripts/audit_typography.js)의 **순수 판정 규칙** 회귀 테스트.

왜 이 파일이 필요한가
--------------------
이 저장소에는 Python 게이트용 positive/negative 픽스처가 이미 여럿 있지만
(tests/test_quality_gates.py), **브라우저 JS 검출기용 테스트는 없었다.** 그래서
JS 쪽 판정이 조용히 망가져도 아무도 모른다 — 실제로 audit_render.js는 두 개의
사각지대(이미지가 바닥선 검사에서 통째로 빠짐 · 겹침을 2단계까지만 봄)를 오래
갖고 있었고, 그동안 「이탈 0 · 겹침 0」이 통과로 읽혔다.

무엇을 테스트하고 무엇을 못 하나
-------------------------------
- **테스트한다**: 역할 판정·하한 위반·자간 보정 누락·근-미스 앵커 — DOM이
  필요 없는 순수 규칙. audit_typography.js는 Node에서 require하면 이 규칙만
  노출하도록 만들어져 있다.
- **테스트하지 못한다**: getBoundingClientRect·getClientRects가 필요한 부분
  (실제 레이아웃). 그건 브라우저에서 실측해야 하고, 헤드리스는 DEC-03(2026-07-26
  사용자 결정)으로 도입하지 않는다. 대신 검출기가 fail-closed assert를 갖고 있어
  «측정 무효»와 «결함 없음»이 섞이지 않는다.

실행: python -m unittest tests.test_typography_rules
      (node가 PATH에 없으면 skip한다 — 테스트가 조용히 통과로 보이지 않게 이유를 찍는다)
"""
from __future__ import annotations

import json
import shutil
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DETECTOR = REPO_ROOT / "scripts" / "audit_typography.js"

NODE = shutil.which("node")


def _run_rules(calls):
    """node로 audit_typography.js의 rules를 불러 호출 목록을 실행하고 결과를 돌려준다."""
    script = (
        "const {rules} = require(%s);\n"
        "const calls = %s;\n"
        "const out = calls.map(c => rules[c.fn].apply(rules, c.args));\n"
        "process.stdout.write(JSON.stringify(out));\n"
    ) % (json.dumps(str(DETECTOR)), json.dumps(calls))
    proc = subprocess.run([NODE, "-e", script], capture_output=True, text=True, encoding="utf-8")
    if proc.returncode != 0:
        raise AssertionError("node 실행 실패:\n" + (proc.stderr or ""))
    return json.loads(proc.stdout)


@unittest.skipIf(NODE is None, "node가 PATH에 없다 — JS 검출기 규칙 테스트를 건너뛴다")
class TypographyRuleTests(unittest.TestCase):
    """결함을 심은 입력을 검출기가 실제로 잡는지 본다(픽스처 관례를 JS로 확장)."""

    def test_module_exports_rules(self):
        out = _run_rules([{"fn": "roleOf", "args": [
            {"chars": 30, "lines": 2, "inCode": False, "inTable": False,
             "fontSize": 20, "text": "이 문장은 학습자가 읽는 한국어 서술문입니다"}]}])
        self.assertEqual(out[0], "narrative")

    # ── 역할 판정 ────────────────────────────────────────────────────
    def test_role_by_content_not_class_name(self):
        """T9의 핵심: 클래스 이름이 아니라 내용으로 역할을 가른다."""
        cases = [
            # (설명, 입력, 기대 역할)
            ("긴 한국어 산문 → 본문",
             {"chars": 30, "lines": 2, "inCode": False, "inTable": False,
              "fontSize": 20, "text": "관찰한 정보를 모아 누구나 읽을 수 있는 화면으로 정리"}, "narrative"),
            ("짧은 박스 설명(20px) → 사용자가 승인한 티어",
             {"chars": 12, "lines": 1, "inCode": False, "inTable": False,
              "fontSize": 20, "text": "무엇을 하는 단계"}, "boxDesc"),
            ("파일 경로는 길어도 산문이 아니다",
             {"chars": 33, "lines": 1, "inCode": False, "inTable": False,
              "fontSize": 13, "text": r"C:\VibeCoding\about-me\index.html"}, "code"),
            ("짧은 영문 장식 태그라인은 산문이 아니다",
             {"chars": 31, "lines": 1, "inCode": False, "inTable": False,
              "fontSize": 8, "text": "LET'S MAKE SOMETHING MEANINGFUL"}, "code"),
            ("표 안은 표 하한",
             {"chars": 30, "lines": 1, "inCode": False, "inTable": True,
              "fontSize": 17, "text": "표 안에 들어간 한국어 설명 문장입니다"}, "table"),
            ("코드 블록은 하한 제외",
             {"chars": 40, "lines": 3, "inCode": True, "inTable": False,
              "fontSize": 15, "text": "const x = 1;"}, "code"),
            ("작은 단독 라벨 → 배지",
             {"chars": 4, "lines": 1, "inCode": False, "inTable": False,
              "fontSize": 12, "text": "필수"}, "badge"),
        ]
        out = _run_rules([{"fn": "roleOf", "args": [c[1]]} for c in cases])
        for (desc, _inp, expected), got in zip(cases, out):
            self.assertEqual(got, expected, f"{desc}: {expected} 기대, {got} 나옴")

    # ── 하한 위반 (D-1 (c) 결정의 집행부) ────────────────────────────
    def test_20px_box_description_passes_but_long_sentence_fails(self):
        """2026-07-31 사용자 결정으로 20px 박스 설명문은 정식이다.
        되돌리지 않되, 같은 20px로 긴 문장을 쓰면 잡아야 한다(D-1 (c))."""
        short = {"chars": 12, "lines": 1, "inCode": False, "inTable": False,
                 "fontSize": 20, "text": "무엇을 하는 단계"}
        long = {"chars": 34, "lines": 2, "inCode": False, "inTable": False,
                "fontSize": 20, "text": "이 단계에서 무엇을 어떻게 하는지 길게 설명하는 문장"}
        out = _run_rules([{"fn": "violatesFloor", "args": [short]},
                          {"fn": "violatesFloor", "args": [long]}])
        self.assertFalse(out[0]["violates"], "승인된 20px 짧은 설명이 위반으로 잡히면 안 된다")
        self.assertEqual(out[0]["role"], "boxDesc")
        self.assertTrue(out[1]["violates"], "20px 긴 문장은 본문 하한(22px) 위반이어야 한다")
        self.assertEqual(out[1]["role"], "narrative")
        self.assertEqual(out[1]["floor"], 22)

    def test_floor_threshold_is_not_zero(self):
        """§0-1: 임계에 0을 쓰지 않는다. 각 티어가 «허용 범위»를 갖는지 확인."""
        out = _run_rules([{"fn": "violatesFloor", "args": [
            {"chars": 30, "lines": 2, "inCode": False, "inTable": False,
             "fontSize": 22, "text": "정확히 하한인 22px 한국어 본문 문장입니다"}]}])
        self.assertFalse(out[0]["violates"], "하한값 자체(22px)는 통과해야 한다")

    # ── 자간 광학 보정 ───────────────────────────────────────────────
    def test_tracking_catches_inherited_absolute_letter_spacing(self):
        """body의 em 자간이 px로 확정돼 상속되면 큰 제목이 보정 없이 렌더된다.
        실측: .pd-title 56px가 -0.32px(-0.0057em) — .cm-title 52px는 -2.08px(-0.04em)."""
        out = _run_rules([
            {"fn": "violatesTracking", "args": [56, -0.32]},   # 보정 누락
            {"fn": "violatesTracking", "args": [52, -2.08]},   # 보정 있음
            {"fn": "violatesTracking", "args": [38, -1.33]},   # -.035em, 보정 있음
            {"fn": "violatesTracking", "args": [22, -0.32]},   # 본문 — 대상 아님
        ])
        self.assertEqual(out, [True, False, False, False])

    # ── 근-미스 앵커 ─────────────────────────────────────────────────
    def test_near_miss_flags_within_5px_but_not_distinct_positions(self):
        """「같은 자리처럼 보이지만 다른 값」만 잡고, 정당한 변형은 남긴다(§6-3)."""
        hist = {"118": 72, "139": 10, "165": 9, "122": 1, "240": 1}
        out = _run_rules([{"fn": "nearMissAnchors", "args": [hist]}])[0]
        self.assertIn(118, out["dominants"])
        values = sorted({m["value"] for m in out["nearMiss"]})
        self.assertEqual(values, [122], "118에서 4px 떨어진 122만 근-미스여야 한다")
        self.assertNotIn(139, values, "지배값은 근-미스가 아니다")
        self.assertNotIn(240, values, "지배값에서 6px 이상 떨어지면 «다른 자리»로 인정한다")

    def test_near_miss_reproduces_chart_top_cluster(self):
        """계획서 §3-4의 핵심 증거 — 차트 상단 231~244 군집이 잡히는지."""
        hist = {"241": 8, "236": 4, "244": 2, "239": 1, "240": 1, "243": 1, "231": 1}
        out = _run_rules([{"fn": "nearMissAnchors", "args": [hist]}])[0]
        self.assertGreaterEqual(len(out["nearMiss"]), 4,
                                "군집 안의 비지배 값들이 근-미스로 잡혀야 한다")

    # ── 독립 검증(2026-08-03)이 잡은 결함의 회귀 테스트 ──────────────
    def test_near_miss_counts_each_value_once(self):
        """결함: 한 값이 인접 지배값 여러 개와 각각 짝지어져 건수가 부풀었다.
        238은 236·241·242 셋 모두와 5px 이내라 종전에는 3건으로 세어졌다."""
        hist = {"236": 4, "241": 5, "242": 3, "238": 1}
        out = _run_rules([{"fn": "nearMissAnchors", "args": [hist]}])[0]
        vals = [m["value"] for m in out["nearMiss"]]
        self.assertEqual(vals.count(238), 1, "한 값은 한 번만 세어야 한다")
        self.assertEqual(out["nearMiss"][0]["dominant"], 238 - 2,
                         "가장 가까운 지배값(236)과 짝지어야 한다")

    def test_dominant_values_clashing_within_5px_are_reported(self):
        """결함: 「자기도 지배값이면 제외」 때문에 236·241처럼 **둘 다 지배값인데
        5px 차이**인 경우가 절대 잡히지 않았다. 그런데 그게 이 검출기가 잡으려는
        문제의 가장 심한 형태다(같은 자리에 규격이 둘)."""
        hist = {"236": 4, "241": 5, "118": 60}
        out = _run_rules([{"fn": "nearMissAnchors", "args": [hist]}])[0]
        self.assertEqual(len(out["dominantClashes"]), 1,
                         "236↔241(5px)이 지배값 충돌로 보고돼야 한다")
        c = out["dominantClashes"][0]
        self.assertEqual(sorted([c["a"], c["b"]]), [236, 241])
        self.assertEqual(c["gap"], 5)

    def test_sentence_containing_a_url_is_still_prose(self):
        """결함: 「경로 문장부호 + 한글 8자 미만 → 코드」 규칙 때문에 URL이 섞인
        **실제 안내문**이 하한 검사를 통째로 빠져나갔다. 이 저장소의 과거 실패가
        전부 「통과로 보이는」 방향이었으므로 가장 위험한 유형이다."""
        cases = [
            ("URL이 섞인 안내문은 문장이다",
             {"chars": 33, "lines": 1, "inCode": False, "inTable": False, "fontSize": 10,
              "text": "https://chat.openai.com/ 에서 접속 확인"}, "narrative"),
            ("경로만 있는 것은 여전히 코드다",
             {"chars": 33, "lines": 1, "inCode": False, "inTable": False, "fontSize": 13,
              "text": r"C:\VibeCoding\about-me\index.html"}, "code"),
            ("경로 + 짧은 라벨도 코드다",
             {"chars": 30, "lines": 1, "inCode": False, "inTable": False, "fontSize": 14,
              "text": r"Codex · C:\VibeCoding\about-me"}, "code"),
        ]
        out = _run_rules([{"fn": "roleOf", "args": [c[1]]} for c in cases])
        for (desc, _inp, expected), got in zip(cases, out):
            self.assertEqual(got, expected, f"{desc}: {expected} 기대, {got} 나옴")

        v = _run_rules([{"fn": "violatesFloor", "args": [cases[0][1]]}])[0]
        self.assertTrue(v["violates"], "10px 안내문이 22px 하한 위반으로 잡혀야 한다")

    def test_code_container_selectors_are_declared_not_buried(self):
        """결함: 「무엇을 코드·터미널로 볼 것인가」가 run() 안 지역 함수에만 있어
        픽스처로 검증할 수 없었다. 2026-08-18 A-0 재판정에서 그 대가가 드러났다 —
        2주차 C3-N3의 터미널 창 **제목줄**(`div.terminal-bar`)이 코드 티어에서
        빠져 있어 「Codex · 내-프로젝트 · 실습 ⑥ 화면 만들기」라는 명사
        브레드크럼이 28자·한글 4낱말이라는 이유로 narrative(22px 하한)로 샜다.
        R-TYPE-01은 「코드·터미널 — 하한 적용 제외」를 이미 규정하고 있었으므로
        정본이 아니라 집행부가 뒤처진 경우다(유형⑤)."""
        out = _run_rules([{"fn": "roleOf", "args": [
            {"chars": 28, "lines": 1, "inCode": True, "inTable": False, "fontSize": 16,
             "text": "Codex · 내-프로젝트 · 실습 ⑥ 화면 만들기"}]}])
        self.assertEqual(out[0], "code", "터미널 크롬은 코드 티어여야 한다")

        script = (
            "const {rules} = require(" + json.dumps(str(DETECTOR)) + "); "
            "process.stdout.write(JSON.stringify(rules.CODE_CONTAINERS || null));"
        )
        proc = subprocess.run([NODE, "-e", script], capture_output=True, text=True,
                              encoding="utf-8")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        sels = json.loads(proc.stdout)
        self.assertIsNotNone(sels, "CODE_CONTAINERS가 rules로 노출돼야 픽스처가 검증할 수 있다")
        for must in ("pre", "code", ".terminal-copy", ".terminal-bar",
                     ".viz-code", ".code-chart", ".code-diagram"):
            self.assertIn(must, sels, f"코드 컨테이너 선언에서 {must}가 빠졌다")

        # 집행부가 선언을 실제로 쓰는지 — 목록만 있고 inCode가 옛 하드코딩이면 무의미하다.
        src = DETECTOR.read_text(encoding="utf-8")
        self.assertIn("rules.CODE_CONTAINERS.some", src,
                      "inCode()가 CODE_CONTAINERS를 쓰지 않는다 — 선언과 집행이 갈라졌다")


class RunnerContractTests(unittest.TestCase):
    """`scripts/run_deck_checks.py`의 fail-closed 계약 회귀 테스트.

    독립 검증(2026-08-03)이 잡은 결함: 부분 실행(`--skip-render`·`--render-only`)이
    exit 0을 내고, 성공 메시지가 어떤 플래그를 썼든 「정적 게이트 + 렌더 증거 모두
    확인」으로 하드코딩돼 있었다. **부분 실행이 완전 통과로 읽히는** 바로 그 실패다.
    현재 저장소에서는 두 주차 모두 노트 검사가 선재 실패라 CLI로는 이 경로가
    가려진다 — 그래서 단위 테스트로 고정한다.
    """

    def _runner(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "run_deck_checks", REPO_ROOT / "scripts" / "run_deck_checks.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        r = mod.Runner("2")
        r.steps = [("정적 게이트", True, ""), ("렌더·타이포 감사", True, "")]
        return r

    def test_full_run_returns_zero(self):
        self.assertEqual(self._runner().report(ran_static=True, ran_render=True), 0)

    def test_skip_render_never_returns_zero(self):
        code = self._runner().report(ran_static=True, ran_render=False)
        self.assertNotEqual(code, 0, "렌더 증거 없이 0을 반환하면 안 된다")
        self.assertEqual(code, 3)

    def test_render_only_never_returns_zero(self):
        code = self._runner().report(ran_static=False, ran_render=True)
        self.assertNotEqual(code, 0, "정적 게이트를 건너뛰고 0을 반환하면 안 된다")
        self.assertEqual(code, 3)

    def test_failure_beats_partial(self):
        r = self._runner()
        r.steps.append(("무언가", False, "실패"))
        self.assertEqual(r.report(ran_static=True, ran_render=False), 1)


if __name__ == "__main__":
    unittest.main()
