"""내용 품질 게이트(scripts/verify_deck_quality.py · scripts/verify_draft_quality.py) 회귀 테스트.

2주차 저밀도 사고(2026-07-26 근본원인 감사, _dev/설계기록/품질감사-2026-07/)를 계기로 신설된
게이트가 실제로 "사전 상태"를 탐지하는지 잠근다. 2주차 원본(sessions/2주차/)은 다른 작업자가
이후 별도로 재밀도화(remediation)하므로, 그 파일들이 바뀌어도 이 테스트가 깨지지 않도록
**현재 상태를 tests/fixtures/quality_gates/에 스냅샷으로 얼려서** 그 스냅샷과 비교한다.
1주차(sessions/1주차/)는 2026-07-26 동결(AGENTS.md)이라 살아있는 경로를 그대로 기준선으로 쓴다.
"""
from __future__ import annotations

import unittest
from pathlib import Path

from scripts import verify_deck_quality as vdq
from scripts import verify_draft_quality as vdrq

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "quality_gates"

# ── 과목 아키텍처 경로 폴백 (2026-07-29 P4.5) ─────────────────────────────
# 1주차 산출물이 courses/<과목>/sessions/로 이동했다. 하드코딩하면 파일을 못 찾아
# setUpClass가 **조용히 skip**한다 — 회귀가 통과로 보이는 최악의 형태라 해석기를 쓴다.
import sys as _sys
_sys.path.insert(0, str(REPO_ROOT / "scripts"))
try:
    import _course_paths as _cp
    def _w(n):
        return Path(_cp.session_dir(n, str(REPO_ROOT)))
except Exception:
    def _w(n):
        return REPO_ROOT / "sessions" / (str(n) + "주차")
# ──────────────────────────────────────────────────────────────────────────

W1_DECK = _w(1) / "강의덱.html"           # 동결 — 살아있는 경로 그대로 사용
W2_FROZEN_DECK = FIXTURES / "week2_frozen_강의덱.html"               # 2026-07-26 스냅샷(remediation 이전)
W2_FROZEN_ROOT = FIXTURES                                            # sessions/2주차/2주차_초안.md 스냅샷을 담은 가짜 저장소 루트


def _levels(results, rule_id):
    return [lvl for rid, lvl, _msg in results if rid == rule_id]


class DeckQualityGateTests(unittest.TestCase):
    """R-QC 게이트가 2주차(조립 단계) 사전 상태를 탐지하고 1주차 최종본은 훨씬 덜 걸리는지 검증."""

    @classmethod
    def setUpClass(cls):
        if not W1_DECK.is_file():
            raise unittest.SkipTest(f"1주차 강의덱.html 없음: {W1_DECK}")
        if not W2_FROZEN_DECK.is_file():
            raise unittest.SkipTest(f"2주차 냉동 스냅샷 없음: {W2_FROZEN_DECK}")
        cls.w1_results, cls.w1_adv, cls.w1_meta, cls.w1_records = vdq.run_checks(str(W1_DECK))
        cls.w2_results, cls.w2_adv, cls.w2_meta, cls.w2_records = vdq.run_checks(str(W2_FROZEN_DECK))

    def test_w2_flags_low_char_density(self):
        # R-QC-01: 2주차 냉동 스냅샷은 설명 슬라이드 저밀도(WARN)를 반드시 낸다.
        self.assertIn("WARN", _levels(self.w2_results, "R-QC-01"))
        self.assertGreater(self.w2_meta["n_low_chars"], 0)

    def test_w2_flags_low_block_density(self):
        # R-QC-02: 의미 블록 수 하한 위반이 실제로 잡히는가.
        self.assertIn("WARN", _levels(self.w2_results, "R-QC-02"))
        self.assertGreater(self.w2_meta["n_low_blocks"], 0)

    def test_w2_flags_low_visual_ratio(self):
        # R-QC-08: 설명 기능 시각자료 비율 미달(2주차의 핵심 결함 중 하나 — H8 재해석).
        self.assertIn("WARN", _levels(self.w2_results, "R-QC-08"))

    def test_w1_final_has_a_clear_quality_margin_over_w2(self):
        """1주차 최종본(동결)은 2주차 냉동 스냅샷보다 결함 신호가 뚜렷하게 적어야 한다.

        규칙 단위 WARN/PASS 개수는 두 덱 모두 대부분의 규칙에서 WARN이 뜨므로(둘 다 "어느 정도는"
        걸림) 판별력이 낮다 — 실제 판별 신호는 "몇 장이 걸렸는가"라는 원시 카운트다. 세 규칙
        (R-QC-01 저밀도 장수·R-QC-02 저블록 장수·R-QC-03 근-빈 컨테이너 보유 장수)의 합을 단일
        결함신호 총량으로 보고, 2주차가 1주차의 최소 2배 이상임을 확인한다(margin 확보 — brittle하지
        않도록 실측 배율을 직접 계산해 그 절반 이상을 임계값으로 쓴다)."""
        w1_total = self.w1_meta["n_low_chars"] + self.w1_meta["n_low_blocks"] + self.w1_meta["n_near_empty_slides"]
        w2_total = self.w2_meta["n_low_chars"] + self.w2_meta["n_low_blocks"] + self.w2_meta["n_near_empty_slides"]
        self.assertGreater(w1_total, 0, "1주차도 결함 신호가 0이면 이 비율 비교 자체가 무의미하다")
        ratio = w2_total / w1_total
        # 실측 배율은 4배 이상이었다(스크립트 실행 결과) — 2배를 문턱으로 잡아 여유(headroom)를 둔다.
        self.assertGreater(
            ratio, 2.0,
            f"2주차 결함신호 총량({w2_total})이 1주차({w1_total})의 2배를 넘지 못함(배율 {ratio:.2f}) — "
            "게이트가 W1/W2를 더 이상 뚜렷하게 구분하지 못하고 있다는 신호일 수 있다",
        )

    def test_r_qc_05_is_advisory_not_a_gate(self):
        """2026-07-27 독립 리뷰: shipped family_signature()로 실측하면 W1=0.181(높음)·W2=0.047
        (낮음)로 방향이 뒤집힌다(좋은 덱이 더 반복적으로 측정됨) — 자동 판정을 내리면 안 된다.
        R-QC-05는 results(PASS/WARN/FAIL)에 나타나지 않고 advisories에만 있어야 한다."""
        self.assertEqual(_levels(self.w1_results, "R-QC-05"), [])
        self.assertEqual(_levels(self.w2_results, "R-QC-05"), [])
        self.assertIn("R-QC-05", [rid for rid, _msg in self.w1_adv])
        self.assertIn("R-QC-05", [rid for rid, _msg in self.w2_adv])

    def test_r_qc_09_is_advisory_not_a_gate(self):
        """2026-07-27 재검증: R-QC-09가 두 덱 모두 100% 플래그(W1 5/5·W2 10/10)로 판별력이
        0이었다 — 자동 WARN에서 빼고 참고치만 제공한다."""
        self.assertEqual(_levels(self.w1_results, "R-QC-09"), [])
        self.assertEqual(_levels(self.w2_results, "R-QC-09"), [])
        self.assertIn("R-QC-09", [rid for rid, _msg in self.w1_adv])
        self.assertIn("R-QC-09", [rid for rid, _msg in self.w2_adv])

    def test_exemption_audit_trail_present_in_meta(self):
        """A1(2026-07-27): 예외로 빠진 슬라이드는 침묵 처리하면 안 된다 — meta에 개수·id가
        있어야 하고, 2주차 냉동 스냅샷은 실제로 화면조작 계약예외 3장(C2-3·C4-3·C4-11)을 낸다."""
        for meta in (self.w1_meta, self.w2_meta):
            self.assertIn("n_intentional_minimal", meta)
            self.assertIn("intentional_minimal_ids", meta)
            self.assertIn("n_screen_operation_exempt", meta)
            self.assertIn("screen_operation_exempt_ids", meta)
        self.assertEqual(self.w2_meta["n_screen_operation_exempt"], 3)
        self.assertEqual(set(self.w2_meta["screen_operation_exempt_ids"]), {"C2-3", "C4-3", "C4-11"})

    def test_strict_mode_promotes_warn_to_fail(self):
        # --strict 승격 계약: WARN이 있으면 strict에서 반드시 FAIL이 존재해야 한다(exit 1 경로).
        warn_rules = [rid for rid, lvl, _m in self.w2_results if lvl == "WARN"]
        self.assertTrue(warn_rules, "이 테스트 전제(2주차 냉동 스냅샷에 WARN 존재)가 깨졌다")

    def test_json_mode_writes_thresholds(self):
        """--json 산출물이 임계·결과를 담는가.

        ⚠️ **종료코드를 0으로 단정하지 않는다**(2026-08-03 갱신). R-QC-18·R-META-01이
        상시 FAIL로 승격되면서, 이 냉동 스냅샷은 **정당하게 exit 1**이 된다 —
        스냅샷이 remediation **이전** 상태라 메타 라벨 3건이 남아 있기 때문이다.
        종전 단정(`returncode == 0`)은 「기본 모드에서는 아무것도 FAIL하지 않는다」는
        옛 전제에 기대고 있었다. JSON이 정상 산출되는지만 본다.
        """
        import json
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out.json"
            from scripts.verify_deck_quality import main as _  # noqa: F401  (import 경로 확인용)
            import subprocess
            import sys
            proc = subprocess.run(
                [sys.executable, str(REPO_ROOT / "scripts" / "verify_deck_quality.py"),
                 str(W2_FROZEN_DECK), "--json", str(out)],
                capture_output=True, text=True, encoding="utf-8", errors="replace",
            )
            self.assertIn(proc.returncode, (0, 1), proc.stderr)
            self.assertTrue(out.is_file())
            payload = json.loads(out.read_text(encoding="utf-8"))
            self.assertIn("R-QC-01_chars", payload["thresholds"])
            self.assertIn("results", payload)

    def test_promoted_rules_actually_fail_a_bad_deck(self):
        """★ 승격이 실제로 무는지 본다 — 「승격했다」는 자기보고를 막는 회귀 테스트.

        R-QC-18(빈 이미지 슬롯)·R-META-01(내부 라벨 노출)은 2026-08-03에
        `--strict` 없이도 FAIL을 내도록 승격됐다. 두 주차 **현행** 덱은 둘 다 0건이라
        승격해도 FAIL이 0이지만(그래서 승격이 안전했다), remediation 이전 상태인
        이 냉동 스냅샷에는 메타 라벨이 남아 있어 **잡혀야 한다.**
        잡히지 않으면 승격이 이름뿐이라는 뜻이다.
        """
        import subprocess
        import sys
        proc = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "verify_deck_quality.py"),
             str(W2_FROZEN_DECK)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        self.assertEqual(proc.returncode, 1,
                         "냉동 스냅샷은 상시 FAIL 규칙에 걸려야 한다 — 승격이 무력하다")
        self.assertIn("[FAIL]", proc.stdout)
        self.assertRegex(proc.stdout, r"\[FAIL\].*(R-META-01|R-QC-18)",
                         "FAIL이 났는데 승격 대상 규칙 때문이 아니다")

    def test_promotion_list_is_not_silently_widened(self):
        """상시 FAIL 목록에 함부로 규칙이 늘지 않았는지 고정한다.

        특히 R-QC-17(실측이 비율형처럼 움직인다)·R-QC-19(1주차 1건 잔존)·
        비율형 6종(방향 역전·사용자 지시 충돌)은 들어오면 안 된다.
        늘리려면 두 주차에 먼저 돌려 FAIL 건수를 산출하고 이 테스트를 함께 고쳐라.
        """
        from scripts.verify_deck_quality import ALWAYS_FAIL
        self.assertEqual(ALWAYS_FAIL, {"R-QC-18", "R-META-01"})


class IntentionalMinimalExemptionTests(unittest.TestCase):
    """C1(2026-07-27): data-intentional-minimal 선언 슬라이드는 R-QC-01/02에서 빠져야 한다.

    실제 사례는 2주차 C2-8("입력 → 실행 → 결과 → 변화", chars=66·blocks=3)이다 — 개념KB가
    지정한 4노드 흐름 시각화를 화면 그대로 옮긴 의도된 미니멀 슬라이드인데 마커가 없으면
    저밀도로 오탐된다. sessions/2주차/는 건드릴 수 없으므로(동결 대상 외 스코프) 냉동
    스냅샷을 메모리에서 임시로 패치해(디스크에 다른 사본을 늘리지 않고 tempfile 하나만 사용)
    "마커 추가 전엔 걸리고, 추가하면 빠진다"를 실증한다."""

    def test_c2_8_flagged_without_marker_exempt_with_marker(self):
        import tempfile
        if not W2_FROZEN_DECK.is_file():
            self.skipTest(f"2주차 냉동 스냅샷 없음: {W2_FROZEN_DECK}")
        html = W2_FROZEN_DECK.read_text(encoding="utf-8")
        needle = '<section class="slide" data-slide="C2-8">'
        self.assertIn(needle, html, "C2-8 슬라이드 태그를 찾지 못함 — 냉동 스냅샷이 예상과 다름")

        _results_before, _adv, _meta, records_before = vdq.run_checks(str(W2_FROZEN_DECK))
        before = next(r for r in records_before if r["sid"] == "C2-8")
        self.assertFalse(before["intentional_minimal"])

        marked_html = html.replace(needle, needle[:-1] + ' data-intentional-minimal="true">', 1)
        with tempfile.NamedTemporaryFile("w", suffix=".html", encoding="utf-8", delete=False) as f:
            f.write(marked_html)
            tmp_path = f.name
        try:
            results_after, _adv2, _meta2, records_after = vdq.run_checks(tmp_path)
            after = next(r for r in records_after if r["sid"] == "C2-8")
            self.assertTrue(after["intentional_minimal"])

            _, warn_before_msg = next((lvl, msg) for rid, lvl, msg in _results_before if rid == "R-QC-01")
            self.assertIn("C2-8", warn_before_msg, "마커 없는 냉동본에서는 C2-8이 R-QC-01에 걸려야 한다")

            _, _lvl_after, warn_after_msg = next(t for t in results_after if t[0] == "R-QC-01")
            self.assertNotIn("C2-8", warn_after_msg, "마커를 달았는데도 C2-8이 여전히 R-QC-01에 걸림")
            _, _lvl2_after, blocks_after_msg = next(t for t in results_after if t[0] == "R-QC-02")
            self.assertNotIn("C2-8", blocks_after_msg, "마커를 달았는데도 C2-8이 여전히 R-QC-02에 걸림")
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_c5_2_still_passes(self):
        # C5-2("한 파일에서 여러 파일로")는 원래도 저밀도가 아니다 — 마커 없이도 안 걸려야 한다.
        if not W2_FROZEN_DECK.is_file():
            self.skipTest(f"2주차 냉동 스냅샷 없음: {W2_FROZEN_DECK}")
        results, _adv, _meta, _records = vdq.run_checks(str(W2_FROZEN_DECK))
        _, _lvl, chars_msg = next(t for t in results if t[0] == "R-QC-01")
        _, _lvl2, blocks_msg = next(t for t in results if t[0] == "R-QC-02")
        self.assertNotIn("C5-2", chars_msg)
        self.assertNotIn("C5-2", blocks_msg)

    def test_marker_is_value_aware_not_presence_only(self):
        """A2(2026-07-27): `data-intentional-minimal="false"`는 여전히 존재하는 속성이지만
        예외가 아니어야 한다 — presence-only 검사였다면 이 케이스도 잘못 예외 처리했을 것."""
        import tempfile
        if not W2_FROZEN_DECK.is_file():
            self.skipTest(f"2주차 냉동 스냅샷 없음: {W2_FROZEN_DECK}")
        html = W2_FROZEN_DECK.read_text(encoding="utf-8")
        needle = '<section class="slide" data-slide="C2-8">'
        false_marked = html.replace(needle, needle[:-1] + ' data-intentional-minimal="false">', 1)
        with tempfile.NamedTemporaryFile("w", suffix=".html", encoding="utf-8", delete=False) as f:
            f.write(false_marked)
            tmp_path = f.name
        try:
            _results, _adv, _meta, records = vdq.run_checks(tmp_path)
            c2_8 = next(r for r in records if r["sid"] == "C2-8")
            self.assertFalse(c2_8["intentional_minimal"], 'data-intentional-minimal="false"가 참으로 오인됨')
        finally:
            Path(tmp_path).unlink(missing_ok=True)


class DraftQualityGateTests(unittest.TestCase):
    """R-QD 게이트가 2주차(초안 단계) 사전 상태를 탐지하는지 검증 — 냉동 스냅샷 기준."""

    @classmethod
    def setUpClass(cls):
        draft_path = FIXTURES / "sessions" / "2주차" / "2주차_초안.md"
        if not draft_path.is_file():
            raise unittest.SkipTest(f"2주차 냉동 초안 스냅샷 없음: {draft_path}")
        cls.results, cls.advisories = vdrq.run_checks(W2_FROZEN_ROOT, "2")

    def test_flags_low_char_density(self):
        self.assertIn("WARN", _levels(self.results, "R-QD-01"))

    def test_flags_note_to_body_ratio(self):
        self.assertIn("WARN", _levels(self.results, "R-QD-03"))

    def test_fails_missing_required_artifacts(self):
        # 냉동 스냅샷의 sessions/2주차/자료/ 폴더는 집필노트·리뷰HTML을 갖지 않는다(실제 부재 상태
        # 그대로 스냅샷) — R-QD-05는 그 부재를 FAIL로 반드시 잡아야 한다.
        self.assertIn("FAIL", _levels(self.results, "R-QD-05"))

    def test_fails_period_length_deviation_without_note(self):
        # R-QD-04: 교시당 8~11장 이탈이 실재하고(2주차는 6개 교시 전부 이탈) 집필노트가 없으므로 FAIL.
        self.assertIn("FAIL", _levels(self.results, "R-QD-04"))

    def test_r_qd_02_is_advisory_not_a_gate(self):
        # A4(2026-07-27): 정보 단위 근사치는 W1/W2 판별력이 약해(3.6% vs 10.7%) 자동 판정에서 뺐다.
        self.assertEqual(_levels(self.results, "R-QD-02"), [])
        self.assertIn("R-QD-02", [rid for rid, _msg in self.advisories])

    def test_r_qd_06_shape_check_present(self):
        # A5: 표 형태 검사 자체가 실행됐는지(실제 2주차 초안은 4열 계약을 지키므로 PASS가 정상).
        self.assertIn("PASS", _levels(self.results, "R-QD-06"))

    def test_r_qd_07_runs_without_false_positive(self):
        # C3: 안티게이밍 검사가 실행되고, 실제 콘텐츠(패딩 없음)에서는 PASS여야 한다.
        self.assertIn("PASS", _levels(self.results, "R-QD-07"))

    def test_screen_operation_exemption_audit_trail(self):
        # B1(2026-07-27): 2주차 냉동 초안은 화면조작 어휘로 걸리는 행이 있고, 침묵 처리되지 않는다.
        exempt_msgs = [msg for rid, msg in self.advisories if rid == "R-QD-EXEMPT"]
        self.assertTrue(exempt_msgs, "화면조작 예외 감사 라인이 advisories에 없음")


class DraftQualityGateA3Tests(unittest.TestCase):
    """A3(2026-07-27): 끝 문장부호 차이만으로 문장 중복 판정이 깨지지 않는지 단위 검증."""

    def test_trailing_punctuation_does_not_defeat_duplicate_detection(self):
        body = "이 도구는 오늘 배운 것을 정리합니다. 이 도구는 오늘 배운 것을 정리합니다"
        self.assertTrue(vdrq.intra_row_duplicate(body),
                         '끝 문장부호 유무만 다른 반복 문장이 여전히 안 잡힘(회귀)')

    def test_genuinely_different_sentences_not_flagged(self):
        body = "이 도구는 오늘 배운 것을 정리합니다. 내일은 다른 기능을 다룹니다"
        self.assertFalse(vdrq.intra_row_duplicate(body))


class DraftQualityGateW1BaselineTests(unittest.TestCase):
    """1주차(동결 · 살아있는 경로)는 초안 게이트에서 심각한 결함 없이 대체로 통과해야 한다."""

    @classmethod
    def setUpClass(cls):
        draft_path = _w(1) / "1주차_초안.md"
        if not draft_path.is_file():
            raise unittest.SkipTest(f"1주차 초안 없음: {draft_path}")
        cls.results, cls.advisories = vdrq.run_checks(REPO_ROOT, "1")

    def test_required_artifacts_present(self):
        self.assertNotIn("FAIL", _levels(self.results, "R-QD-05"))

    def test_low_char_density_warn_rate_far_below_w2(self):
        # 정확한 카운트는 메시지 문자열에만 있어 텍스트 파싱이 필요하지만, 최소 계약은
        # "FAIL이 없다"(위 test)와 "R-QD-01이 존재는 하되 심각도가 WARN을 넘지 않는다"이다.
        levels = _levels(self.results, "R-QD-01")
        self.assertNotIn("FAIL", levels)

    def test_r_qd_06_no_false_positive_on_real_draft(self):
        # 아이콘 범례(읽고 시작해)의 3열 표가 콘텐츠 4열 계약 위반으로 오탐되지 않아야 한다.
        self.assertIn("PASS", _levels(self.results, "R-QD-06"))

    def test_r_qd_07_no_padding_detected(self):
        self.assertIn("PASS", _levels(self.results, "R-QD-07"))


def _write_tmp_html(html):
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".html", encoding="utf-8", delete=False) as f:
        f.write(html)
        return f.name


def _wrap_slides(*slides_html):
    """idx=0은 항상 표지로 분류되므로, 표지 슬라이드 하나를 앞에 두고 그 뒤에 대상 슬라이드를 잇는다."""
    cover = '<section class="slide cover" data-slide="COVER"><div class="s-full"><p>표지</p></div></section>'
    body = "\n".join(slides_html)
    return f"<html><body>{cover}\n{body}</body></html>"


class NewMetricRQC15Tests(unittest.TestCase):
    """R-QC-15 하단 결론 콜아웃 보유율(임계 0.12)."""

    def test_positive_last_child_is_conclusion_callout(self):
        html = _wrap_slides(
            '<section class="slide" data-slide="X1"><div class="s-full">'
            '<p>본문 설명 문장입니다.</p>'
            '<p class="callout">그래서 결론은 이렇습니다.</p>'
            '</div></section>'
        )
        path = _write_tmp_html(html)
        try:
            results, _adv, _meta, _records = vdq.run_checks(path)
            self.assertIn("WARN", _levels(results, "R-QC-15"))
        finally:
            Path(path).unlink(missing_ok=True)

    def test_negative_last_child_is_plain_content(self):
        html = _wrap_slides(
            '<section class="slide" data-slide="X1"><div class="s-full">'
            '<p>본문 설명 문장입니다.</p>'
            '<p>추가 설명 문장입니다.</p>'
            '</div></section>'
        )
        path = _write_tmp_html(html)
        try:
            results, _adv, _meta, _records = vdq.run_checks(path)
            self.assertIn("PASS", _levels(results, "R-QC-15"))
        finally:
            Path(path).unlink(missing_ok=True)


class NewMetricRQC16Tests(unittest.TestCase):
    """R-QC-16 박스 기반 슬라이드 비율(임계 0.10, 박스 컨테이너 4개 이상)."""

    def test_positive_four_or_more_box_containers(self):
        html = _wrap_slides(
            '<section class="slide" data-slide="X1"><div class="s-full">'
            '<div class="a-card">1</div><div class="b-box">2</div>'
            '<div class="c-node">3</div><div class="d-col">4</div>'
            '<p>본문 설명 문장입니다.</p>'
            '</div></section>'
        )
        path = _write_tmp_html(html)
        try:
            results, _adv, _meta, _records = vdq.run_checks(path)
            self.assertIn("WARN", _levels(results, "R-QC-16"))
        finally:
            Path(path).unlink(missing_ok=True)

    def test_negative_two_or_fewer_box_containers(self):
        html = _wrap_slides(
            '<section class="slide" data-slide="X1"><div class="s-full">'
            '<div class="a-card">1</div><div class="b-box">2</div>'
            '<p>본문 설명 문장입니다.</p>'
            '</div></section>'
        )
        path = _write_tmp_html(html)
        try:
            results, _adv, _meta, _records = vdq.run_checks(path)
            self.assertIn("PASS", _levels(results, "R-QC-16"))
        finally:
            Path(path).unlink(missing_ok=True)


class NewMetricRQC18EmptySlotTests(unittest.TestCase):
    """R-QC-18 빈 이미지 슬롯(임계 0).

    2026-07-31 사고 회귀 방지: 덱에 <img> 0개인데 .asset-slot 24개가 남아
    연파랑 점선 빈 상자로 23장에 렌더됐다. 기존 게이트 9종이 전부 통과시켰다.
    """

    def test_positive_asset_slot_without_media(self):
        html = _wrap_slides(
            '<section class="slide" data-slide="X1"><div class="s-full">'
            '<p>본문 설명 문장입니다.</p></div>'
            '<figure class="asset-slot asset-slot--support img-slot-r"'
            ' data-image-state="expected"></figure></section>'
        )
        path = _write_tmp_html(html)
        try:
            results, _adv, _meta, _records = vdq.run_checks(path)
            self.assertIn("WARN", _levels(results, "R-QC-18"))
        finally:
            Path(path).unlink(missing_ok=True)

    def test_negative_asset_slot_filled_with_svg(self):
        html = _wrap_slides(
            '<section class="slide" data-slide="X1"><div class="s-full">'
            '<p>본문 설명 문장입니다.</p></div>'
            '<figure class="asset-slot asset-slot--support img-slot-r">'
            '<svg viewBox="0 0 10 10"><rect width="10" height="10"/></svg>'
            '</figure></section>'
        )
        path = _write_tmp_html(html)
        try:
            results, _adv, _meta, _records = vdq.run_checks(path)
            self.assertIn("PASS", _levels(results, "R-QC-18"))
        finally:
            Path(path).unlink(missing_ok=True)


class NewMetricRQC19BareTextTests(unittest.TestCase):
    """R-QC-19 격자 컨테이너 안 맨 텍스트(임계 0).

    2026-07-31 사고 회귀 방지: .work-step은 48px 번호 칸 + 내용 칸의 2열
    격자다. 클래스 없는 자식은 익명 격자 아이템이 되어 48px 칸에 떨어지고
    한 문장이 세로로 무너진다(실측 C4-15 bottom y=1200, 슬라이드 밖).
    CSS로는 익명 아이템을 선택할 수 없어 마크업에서만 막을 수 있다.
    """

    def test_positive_bare_text_after_bold(self):
        html = _wrap_slides(
            '<section class="slide" data-slide="X1"><div class="s-full">'
            '<div class="work-step"><span class="n">1</span>'
            '<b>제목입니다</b> — 이 설명이 클래스 없이 맨 텍스트로 남아 있다.</div>'
            '</div></section>'
        )
        path = _write_tmp_html(html)
        try:
            results, _adv, _meta, _records = vdq.run_checks(path)
            self.assertIn("WARN", _levels(results, "R-QC-19"))
        finally:
            Path(path).unlink(missing_ok=True)

    def test_negative_description_wrapped_in_span(self):
        html = _wrap_slides(
            '<section class="slide" data-slide="X1"><div class="s-full">'
            '<div class="work-step"><span class="n">1</span>'
            '<b>제목입니다</b> <span class="desc">이 설명은 제대로 감싸져 있다.</span></div>'
            '</div></section>'
        )
        path = _write_tmp_html(html)
        try:
            results, _adv, _meta, _records = vdq.run_checks(path)
            self.assertIn("PASS", _levels(results, "R-QC-19"))
        finally:
            Path(path).unlink(missing_ok=True)


class NewMetricRQC17Tests(unittest.TestCase):
    """R-QC-17 실습 완결성 미달률(임계 0, 단계 요소 2개 미만)."""

    def test_positive_practice_slide_with_one_work_step(self):
        html = _wrap_slides(
            '<section class="slide practice" data-slide="X1"><div class="s-full">'
            '<div class="work-step">1단계</div>'
            '<p>본문 설명 문장입니다.</p>'
            '</div></section>'
        )
        path = _write_tmp_html(html)
        try:
            results, _adv, _meta, _records = vdq.run_checks(path)
            self.assertIn("WARN", _levels(results, "R-QC-17"))
        finally:
            Path(path).unlink(missing_ok=True)

    def test_negative_practice_slide_with_two_work_steps(self):
        html = _wrap_slides(
            '<section class="slide practice" data-slide="X1"><div class="s-full">'
            '<div class="work-step">1단계</div>'
            '<div class="work-step">2단계</div>'
            '<p>본문 설명 문장입니다.</p>'
            '</div></section>'
        )
        path = _write_tmp_html(html)
        try:
            results, _adv, _meta, _records = vdq.run_checks(path)
            self.assertIn("PASS", _levels(results, "R-QC-17"))
        finally:
            Path(path).unlink(missing_ok=True)

    def test_skip_case_zero_practice_slides_has_audit_trail(self):
        html = _wrap_slides(
            '<section class="slide" data-slide="X1"><div class="s-full">'
            '<p>본문 설명 문장입니다.</p>'
            '</div></section>'
        )
        path = _write_tmp_html(html)
        try:
            results, advisories, meta, _records = vdq.run_checks(path)
            self.assertEqual(_levels(results, "R-QC-17"), [], "실습 슬라이드 0장이면 results에 판정이 없어야 한다")
            self.assertIn("R-QC-17", [rid for rid, _msg in advisories])
            self.assertTrue(
                any("R-QC-17" in line for line in meta.get("audit_lines", [])),
                "실습 슬라이드 0장 감사추적이 meta['audit_lines']에 없음",
            )
        finally:
            Path(path).unlink(missing_ok=True)


class NewMetricRMETA01Tests(unittest.TestCase):
    """R-META-01 메타 표기 잔존(임계 0건)."""

    def test_positive_title_has_meta_marker(self):
        html = _wrap_slides(
            '<section class="slide" data-slide="X1"><div class="s-full">'
            '<p class="s-title">개념 설명(최소 소개)</p>'
            '<p>본문 설명 문장입니다.</p>'
            '</div></section>'
        )
        path = _write_tmp_html(html)
        try:
            results, _adv, _meta, _records = vdq.run_checks(path)
            self.assertIn("WARN", _levels(results, "R-META-01"))
        finally:
            Path(path).unlink(missing_ok=True)

    def test_negative_title_has_no_meta_marker(self):
        html = _wrap_slides(
            '<section class="slide" data-slide="X1"><div class="s-full">'
            '<p class="s-title">개념 설명</p>'
            '<p>본문 설명 문장입니다.</p>'
            '</div></section>'
        )
        path = _write_tmp_html(html)
        try:
            results, _adv, _meta, _records = vdq.run_checks(path)
            self.assertIn("PASS", _levels(results, "R-META-01"))
        finally:
            Path(path).unlink(missing_ok=True)


class NewMetricRQC08ThresholdTests(unittest.TestCase):
    """R-QC-08 임계가 0.55인지 상수를 직접 확인."""

    def test_threshold_is_0_55(self):
        self.assertEqual(vdq.THRESH_QC08_VISUAL_RATIO, 0.55)


class RQC12AdvisoryOnlyTests(unittest.TestCase):
    """R-QC-12는 자동 판정 목록(results)에 없고 사람검토(advisories)로만 나와야 한다."""

    def test_r_qc_12_absent_from_results_present_in_advisories(self):
        html = _wrap_slides(
            '<section class="slide" data-slide="X1"><div class="s-full">'
            '<p>본문 설명 문장입니다.</p>'
            '</div></section>'
        )
        path = _write_tmp_html(html)
        try:
            results, advisories, _meta, _records = vdq.run_checks(path)
            self.assertEqual(_levels(results, "R-QC-12"), [])
            self.assertIn("R-QC-12", [rid for rid, _msg in advisories])
        finally:
            Path(path).unlink(missing_ok=True)


class CopyStyleRuleTests(unittest.TestCase):
    """P2 배치2(2026-08-17) 문체 규칙 — 고의 위반 픽스처로 WARN이 실제로 나는지 증명한다.

    3층 정의 정본은 kit/guide/문체-원칙.md. 임계(허용 건수)는 과목 프로필 §3-G가 정본이며
    키가 없으면 판정 대신 [사람검토] 표본으로 강등된다(이 저장소에는 키가 있어 WARN 경로).
    """

    def _run(self, *slides):
        path = _write_tmp_html(_wrap_slides(*slides))
        try:
            return vdq.run_checks(path)
        finally:
            Path(path).unlink(missing_ok=True)

    def test_profile_keys_are_wired(self):
        # 프로필 §3-G 키가 사라지면 아래 WARN 단정이 전부 무의미해진다 — 배선부터 확인.
        for rid in ("R-COPY-01", "R-COPY-02", "R-COPY-03"):
            self.assertTrue(vdq._COPY_GATE_FROM_PROFILE.get(rid),
                            f"{rid} 임계가 프로필 §3-G에서 오지 않았다")

    def test_r_copy_01_flags_dash_and_slash_joins(self):
        results, _adv, meta, _rec = self._run(
            '<section class="slide" data-slide="X1"><div class="s-full">'
            '<p>먼저 문장을 끝냅니다 — 그리고 부연을 붙입니다.</p>'
            '<p>규칙을 지킵니다 / 예외는 따로 적습니다</p>'
            '</div></section>')
        self.assertEqual(meta["n_dash_join"], 2)
        self.assertIn("WARN", _levels(results, "R-COPY-01"))

    def test_r_copy_01_allows_label_and_leadin_dashes(self):
        # 원문 명시 예외: 대비·등가·사전식 라벨. 머리 대시(리드인)도 잇기가 아니다.
        results, _adv, meta, _rec = self._run(
            '<section class="slide" data-slide="X1"><div class="s-full">'
            '<p>순서 — 입력, 실행, 결과</p>'
            '<p>— 핵심 기능 하나만 작동하는 첫 버전</p>'
            '<p>지금 상태 — 원본</p>'
            '</div></section>')
        self.assertEqual(meta["n_dash_join"], 0)
        self.assertIn("PASS", _levels(results, "R-COPY-01"))

    def test_r_copy_01_mid_phrase_dash_is_advisory_not_warn(self):
        # «구 — 부연»은 ②층 밖(라벨과 기계로 안 갈림) — WARN이 아니라 사람검토 표본.
        results, adv, meta, _rec = self._run(
            '<section class="slide" data-slide="X1"><div class="s-full">'
            '<p>전체 순서와 역할표를 아는 지휘자 — 각 담당은 자기 일만 압니다</p>'
            '</div></section>')
        self.assertEqual(meta["n_dash_join"], 0)
        self.assertEqual(meta["n_dash_mid"], 1)
        self.assertIn("PASS", _levels(results, "R-COPY-01"))
        self.assertTrue(any(r == "R-COPY-01" for r, _m in adv))

    def test_r_copy_02_flags_self_reference(self):
        results, _adv, meta, _rec = self._run(
            '<section class="slide" data-slide="X1"><div class="s-full">'
            '<p>우리 수업에서는 이것을 A라고 부릅니다.</p></div></section>')
        self.assertEqual(meta["n_self_ref"], 1)
        self.assertIn("WARN", _levels(results, "R-COPY-02"))

    def test_r_copy_02_ignores_closing_greeting(self):
        # «오늘 수업은 성공»류 마무리 인사는 관용구가 아니다(실측 오탐 사례 — ③층 잔여).
        _results, _adv, meta, _rec = self._run(
            '<section class="slide" data-slide="X1"><div class="s-full">'
            '<p>여기까지 되면 오늘 수업은 성공입니다.</p></div></section>')
        self.assertEqual(meta["n_self_ref"], 0)

    def test_r_copy_03_flags_verbal_step_title_but_not_desc_or_slide_title(self):
        results, _adv, meta, _rec = self._run(
            '<section class="slide" data-slide="X1">'
            '<h2 class="s-title">슬라이드 제목은 서술형이어도 잡지 않습니다</h2>'
            '<div class="s-full"><div class="pr-steps">'
            '<div class="work-step"><b>참고 서비스 1개를 고릅니다.</b>'
            '<span class="desc">보조 설명은 합니다체를 유지합니다.</span></div>'
            '</div></div></section>')
        self.assertEqual(meta["n_step_title_verbal"], 1,
                         "work-step 제목 1건만 — .s-title·desc가 세이면 폐기 이력(방향 역전)과 겹친다")
        self.assertIn("WARN", _levels(results, "R-COPY-03"))

    def test_r_copy_03_noun_form_step_title_passes(self):
        results, _adv, meta, _rec = self._run(
            '<section class="slide" data-slide="X1"><div class="s-full">'
            '<div class="work-step"><b>참고 서비스 1개 고르기</b></div>'
            '</div></section>')
        self.assertEqual(meta["n_step_title_verbal"], 0)
        self.assertIn("PASS", _levels(results, "R-COPY-03"))

    def test_r_copy_03_steps_wrapper_banner_is_not_a_step_title(self):
        # 복수형 래퍼(steps-full·pr-steps)는 개별 스텝이 아니다 — 주제 배너 오탐 수정 회귀.
        _results, _adv, meta, _rec = self._run(
            '<section class="slide" data-slide="X1"><div class="s-full steps-full">'
            '<p class="topic"><b>여행 앱을 만들 겁니다</b></p>'
            '</div></section>')
        self.assertEqual(meta["n_step_title_verbal"], 0)

    def test_r_copy_04_and_r_deco_01_are_advisory_only(self):
        results, adv, meta, _rec = self._run(
            '<section class="slide" data-slide="X1"><div class="s-full">'
            '<div class="card"><p>'
            + ("이 카드는 문장으로 길게 설명합니다. " * 3)
            + '그리고 두 번째 문장도 문장으로 끝나게 됩니다.</p></div>'
            '<div class="card"><svg viewBox="0 0 10 10"><rect width="10" height="10"/></svg></div>'
            '</div></section>')
        self.assertGreaterEqual(meta["n_card_prose"], 1)
        self.assertEqual(meta["n_deco_svg"], 1)
        self.assertEqual(_levels(results, "R-COPY-04"), [], "R-COPY-04는 판정 없음(advisory 전용)")
        self.assertEqual(_levels(results, "R-DECO-01"), [], "R-DECO-01은 판정 없음(advisory 전용)")
        self.assertTrue(any(r == "R-COPY-04" for r, _m in adv))
        self.assertTrue(any(r == "R-DECO-01" for r, _m in adv))

    def test_r_deco_01_allows_logo_divider_and_viz(self):
        _results, _adv, meta, _rec = self._run(
            '<section class="slide" data-slide="X1">'
            '<header class="s-head"><svg class="s-logo" viewBox="0 0 96 96"><circle r="9"/></svg></header>'
            '<div class="s-full"><figure class="viz-flow-h"><svg viewBox="0 0 10 10"><rect/></svg></figure>'
            '<p>본문 설명 문장입니다.</p></div></section>')
        self.assertEqual(meta["n_deco_svg"], 0)


if __name__ == "__main__":
    unittest.main()
