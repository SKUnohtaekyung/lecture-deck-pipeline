# -*- coding: utf-8 -*-
"""유형⑤ 「선언과 집행 불일치」 검사의 회귀 테스트.

무엇을 고정하나
--------------
`scripts/verify_declared_vs_enforced.py`가 **헛돌지 않는지**를 고정한다.
이 저장소가 반복해서 겪은 실패는 「검사가 있는데 아무것도 안 잡는」 상태였고,
그건 검사가 없는 것보다 나쁘다(통과로 읽히기 때문이다).

그래서 세 가지를 본다:
  1. **음성 픽스처** — 값이 일치하면 통과하는가
  2. **양성 픽스처** — 값을 어긋나게 만들면 **실제로 FAIL하는가**
  3. **알려진 3건** — 요구된 수용 기준이 등재 전에는 잡히고 등재 후에는 통과하는가
  4. **파싱 0 방어** — 표를 못 읽었는데 「불일치 0」이 나오지 않는가

⚠️ 오탐 방어도 함께 고정한다. deck.css(base) → legibility.css 순서로 실효값이
   결정되므로 `.s-title` 40→38 같은 **의도된 계층**을 불일치로 잡으면 안 된다.
   실제로 초안에서 order를 파일마다 0으로 리셋해 `.s-body`가 19px로 해석되는
   오탐이 났다 — 그 회귀를 막는다.

실행: python -m unittest tests.test_declared_vs_enforced
"""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "verify_declared_vs_enforced.py"


def _load():
    spec = importlib.util.spec_from_file_location("verify_declared_vs_enforced", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


V = _load()


class CascadeResolverTests(unittest.TestCase):
    """실효값 해석 — 오탐의 주된 원인이 여기다."""

    def _rules(self, *files):
        rules, order = [], 0
        for css in files:
            got, order = V.parse_rules(css, f"f{order}", order)
            rules.extend(got)
        return rules

    def test_later_layer_wins_at_equal_specificity(self):
        """deck.css 19px 위에 legibility.css 22px가 오면 **22px가 실효값**이다.

        ⚠️ 실제 회귀: order를 파일마다 0에서 다시 세면 deck.css가 이겨
        「본문이 19px」이라는 오탐이 난다(2026-08-03 실측).
        """
        rules = self._rules(".s-body{ font-size:19px; }", ".s-body{ font-size:22px; }")
        got, _src = V.resolve(rules, [".s-body"], "font-size")
        self.assertEqual(got, "22px")

    def test_intended_layering_is_not_a_mismatch(self):
        """`.s-title` base 40 → 가독성 38. 정본이 38이면 불일치가 아니다."""
        rules = self._rules(".s-title{ font-size:40px; }", ".s-title{ font-size:38px; }")
        got, _ = V.resolve(rules, [".s-title"], "font-size")
        self.assertEqual(got, "38px")

    def test_higher_specificity_beats_order(self):
        rules = self._rules(".x .y{ font-size:30px; }", ".y{ font-size:10px; }")
        got, _ = V.resolve(rules, [".x", ".y"], "font-size")
        self.assertEqual(got, "30px", "명시도가 높은 쪽이 이겨야 한다")

    def test_context_scoped_rule_does_not_leak(self):
        """`.eval-steps .work-step b`는 문맥 규칙이라 일반 `.work-step b`의
        실효값으로 오인되면 안 된다."""
        rules = self._rules(".work-step b{ font-size:18px; }",
                            ".eval-steps .work-step b{ font-size:21px; }")
        got, _ = V.resolve(rules, [".work-step", "b"], "font-size")
        self.assertEqual(got, "18px")

    def test_ancestor_rule_does_not_style_descendant_directly(self):
        """`.s-body`는 `.s-body strong`의 직접 실효값이 아니다."""
        rules = self._rules(".s-body{ font-weight:400; }", ".s-body strong{ font-weight:800; }")
        got, _ = V.resolve(rules, [".s-body", "strong"], "font-weight")
        self.assertEqual(got, "800")

    def test_missing_definition_reports_none(self):
        rules = self._rules(".other{ font-size:10px; }")
        got, src = V.resolve(rules, [".desc"], "font-size")
        self.assertIsNone(got)
        self.assertIsNone(src)


class DeclarationParsingTests(unittest.TestCase):
    def test_parses_role_table_and_token_tables(self):
        md = (REPO_ROOT / "kit" / "guide" / "토큰-치트시트.md").read_text(encoding="utf-8")
        roles = V.parse_declared_roles(md)
        tokens = V.parse_declared_tokens(md)
        self.assertGreater(len(roles), 0, "R-TYPE-01 역할표를 하나도 못 읽었다")
        self.assertGreater(len(tokens), 0, "토큰표를 하나도 못 읽었다")
        names = {r["role"] for r in roles}
        self.assertIn("박스 제목", names)
        self.assertIn("박스 안 설명문", names)

    def test_inline_spacing_scale_is_parsed(self):
        """간격 스케일은 **표가 아니라 인라인 목록**이다.

        ⚠️ 실제 회귀: 표만 읽으면 `--sp-*`가 통째로 빠지고, 「토큰을 못 찾았다」가
        불일치로 잡혀 오탐이 난다(2026-08-03 실측).
        """
        md = (REPO_ROOT / "kit" / "guide" / "토큰-치트시트.md").read_text(encoding="utf-8")
        tokens = V.parse_declared_tokens(md)
        self.assertIn("--sp-18", tokens)
        self.assertEqual(tokens["--sp-18"], "18px")

    def test_role_token_table_is_parsed(self):
        md = (REPO_ROOT / "kit" / "guide" / "토큰-치트시트.md").read_text(encoding="utf-8")
        tokens = V.parse_declared_tokens(md)
        for t in ("--fs-body", "--fs-box-title", "--fs-box-desc"):
            self.assertIn(t, tokens, f"역할 토큰 {t} 를 못 읽었다")


class KnownCaseTests(unittest.TestCase):
    """§3 수용 기준 — 요구된 3건을 실제로 잡는가."""

    @classmethod
    def setUpClass(cls):
        cls.roles, cls.tokens, cls.rules, cls.parsed, cls.findings = V.run()
        cls.keys = {f[0] for f in cls.findings}

    def test_parse_counts_are_nonzero(self):
        """파싱이 깨졌는데 「불일치 0」이 나오는 것을 막는다."""
        self.assertGreater(self.parsed["role_rows"], 0)
        self.assertGreater(self.parsed["tokens"], 0)
        self.assertGreater(self.parsed["css_rules"], 0)

    def test_case1_sp18_vs_kit_gap(self):
        """알려진 1: `--sp-18` 선언 ↔ kit `.grid-2`/`.grid-3` gap:14px."""
        for target in (".grid-2", ".grid-3"):
            key = V.mismatch_key("token", "--sp-18", [target], "gap")
            self.assertIn(key, self.keys, f"{target} gap 불일치를 못 잡았다")
            self.assertIn(key, V.KNOWN, "등재돼 있어야 통과한다")

    def test_case2_box_title_vs_work_step_b(self):
        """알려진 2: 박스 제목 26px 선언 ↔ kit `.work-step b` 18px."""
        key = V.mismatch_key("role", "박스 제목", [".work-step", "b"], "font-size")
        self.assertIn(key, self.keys, "`.work-step b` 불일치를 못 잡았다")
        self.assertIn(key, V.KNOWN)

    def test_case3_role_tokens_reference_audit_runs(self):
        """알려진 3: 역할 토큰의 **참조 실태**를 실제로 센다."""
        declared = [t for t in self.tokens if t.startswith(("--fs-", "--lh-", "--sp-"))]
        self.assertGreater(len(declared), 20, "토큰을 거의 못 읽었다")
        counts = V.token_reference_counts(declared)
        self.assertEqual(len(counts), len(declared))
        # 템플릿 토큰화로 살아난 것이 있어야 한다 — 전부 죽어 있으면 배선이 안 된 것이다
        alive = [t for t in declared if counts[t] > 0]
        self.assertTrue(alive, "선언된 토큰 중 참조되는 것이 하나도 없다 — 죽은 체계다")

    def test_intended_layering_cases_are_not_flagged(self):
        """오탐 방어 — base→가독성 계층은 불일치가 아니다."""
        for role, target in (("본문", [".s-body"]), ("제목", [".s-title"]),
                             ("리드", [".s-lead"]), ("eyebrow", [".s-eyebrow"]),
                             ("표", ["table.t"])):
            key = V.mismatch_key("role", role, target, "font-size")
            self.assertNotIn(key, self.keys,
                             f"의도된 계층({role})을 불일치로 잡았다 — 오탐이다")

    def test_no_unregistered_mismatch(self):
        """현재 상태 고정 — 등재되지 않은 불일치가 있으면 실패한다."""
        new = sorted(k for k in self.keys if k not in V.KNOWN)
        self.assertEqual(new, [],
                         "등재되지 않은 새 불일치:\n  " + "\n  ".join(new))

    def test_every_known_entry_has_a_reason(self):
        for key, reason in V.KNOWN.items():
            self.assertTrue(reason and len(reason) > 20,
                            f"{key} 의 등재 사유가 비어 있거나 너무 짧다")


class PositiveFixtureTests(unittest.TestCase):
    """양성 픽스처 — 어긋나게 만들면 실제로 잡히는가."""

    def test_mismatch_is_detected(self):
        rules, _ = V.parse_rules(".work-step b{ font-size:18px; }", "fixture")
        got, _src = V.resolve(rules, [".work-step", "b"], "font-size")
        self.assertEqual(got, "18px")
        self.assertNotEqual(got, "26px", "선언 26px와 다르므로 불일치여야 한다")

    def test_match_is_not_detected(self):
        """음성 픽스처 — 값이 같으면 통과."""
        rules, _ = V.parse_rules(".work-step b{ font-size:26px; }", "fixture")
        got, _src = V.resolve(rules, [".work-step", "b"], "font-size")
        self.assertEqual(got, "26px")

    def test_parse_failure_is_visible_not_silent(self):
        """표를 못 읽으면 «0건»이 아니라 «0행»으로 드러나야 한다."""
        self.assertEqual(V.parse_declared_roles("표가 없는 문서"), [])
        self.assertEqual(V.parse_declared_tokens("표가 없는 문서"), {})


if __name__ == "__main__":
    unittest.main()
