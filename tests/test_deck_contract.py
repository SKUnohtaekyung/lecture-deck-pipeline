"""주차 구조 계약 외부화·신규 검사 회귀 테스트 (P6).

1주차 실덱에 과적합되지 않도록, 1주차 파일을 복사·참조하지 않는 독립 픽스처
(`tests/fixtures/mini-week/`)로 검사한다. 1주차는 동결(DEC-06)이라 이 테스트에서
읽지도 쓰지도 않는다 — 유일한 예외는 `_contracts` 폴백 **경로 해석** 검증이며,
그조차 파일을 열지 않고 경로만 확인한다.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.assemble_deck import assemble
from scripts.verify_deck import find_deck_contract
from scripts.verify_session_docs import resolve_draft

REPO = Path(__file__).resolve().parent.parent
FIXTURE = REPO / "tests" / "fixtures" / "mini-week" / "9주차"
BROKEN = REPO / "tests" / "fixtures" / "mini-week" / "broken"


def _build(tmp: Path, *, part01: Path | None = None, manifest: Path | None = None,
           contract: bool = True) -> Path:
    """픽스처를 임시 폴더에 복사해 조립하고 덱 경로를 돌려준다.

    part01/manifest 를 주면 그 파일로 갈아끼워 고장 변형을 만든다.
    contract=False 면 계약 파일을 빼서 '계약 없음' 경로를 만든다.
    """
    week = tmp / "9주차"
    shutil.copytree(FIXTURE, week)
    if part01 is not None:
        shutil.copyfile(part01, week / "강의덱.초안" / "part-01.html")
    if manifest is not None:
        shutil.copyfile(manifest, week / "자료" / "이미지-에셋.json")
    if not contract:
        (week / "deck.contract.json").unlink()
    ok, errors, _log = assemble(week / "강의덱.초안")
    assert ok, f"픽스처 조립 실패: {errors}"
    return week / "강의덱.html"


def _verify(deck: Path, parts: int = 2) -> str:
    """verify_deck 을 서브프로세스로 돌려 출력을 돌려준다(기존 테스트 관례)."""
    proc = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "verify_deck.py"), str(deck),
         "--parts", str(parts)],
        capture_output=True, text=True, encoding="utf-8", cwd=str(REPO),
    )
    return (proc.stdout or "") + (proc.stderr or "")


def _lines(out: str, kind: str) -> list[str]:
    return [ln for ln in out.splitlines() if ln.startswith(f"[{kind}]")]


class ContractLookupTests(unittest.TestCase):
    """계약 3단 탐색: ① 동폴더 → ② sessions/_contracts → ③ 없으면 WARN."""

    def test_sibling_contract_is_found_first(self):
        found = find_deck_contract(FIXTURE / "강의덱.html")
        self.assertIsNotNone(found)
        self.assertEqual(found, (FIXTURE / "deck.contract.json").resolve())

    def test_falls_back_to_contracts_directory(self):
        # 1주차 덱은 동폴더에 계약이 없고 sessions/_contracts/1주차… 로 폴백해야 한다.
        # (경로 해석만 확인한다 — 1주차 파일을 열지 않는다.)
        found = find_deck_contract(REPO / "sessions" / "1주차" / "강의덱.html")
        self.assertIsNotNone(found)
        self.assertEqual(found.parent.name, "_contracts")
        self.assertEqual(found.name, "1주차.deck.contract.json")

    def test_missing_contract_returns_none(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertIsNone(find_deck_contract(Path(td) / "없는주차" / "강의덱.html"))

    def test_missing_contract_warns_not_fails(self):
        with tempfile.TemporaryDirectory() as td:
            deck = _build(Path(td), contract=False)
            out = _verify(deck)
        self.assertIn("주차 구조 계약 없음", out)
        self.assertTrue(any("주차 구조 계약 없음" in ln for ln in _lines(out, "WARN")),
                        f"계약 부재는 WARN이어야 한다:\n{out}")
        self.assertFalse(any("주차 구조 계약" in ln for ln in _lines(out, "FAIL")),
                         f"계약 부재를 FAIL로 만들면 안 된다:\n{out}")


class HealthyFixtureTests(unittest.TestCase):
    """정상 픽스처는 신규 검사 4종에서 FAIL이 없어야 한다."""

    def test_healthy_fixture_has_no_part_or_wiring_fail(self):
        with tempfile.TemporaryDirectory() as td:
            out = _verify(_build(Path(td)))
        fails = _lines(out, "FAIL")
        self.assertFalse([ln for ln in fails if "PART 라벨" in ln], f"\n{out}")
        self.assertFalse([ln for ln in fails if "이미지 배선" in ln], f"\n{out}")

    def test_contract_slide_and_divider_counts_match_fixture(self):
        with tempfile.TemporaryDirectory() as td:
            out = _verify(_build(Path(td)))
        contract = json.loads((FIXTURE / "deck.contract.json").read_text(encoding="utf-8"))
        self.assertEqual(contract["decks"]["강의덱"]["slides"], 12)
        self.assertEqual(contract["decks"]["강의덱"]["dividers"], 2)
        self.assertFalse([ln for ln in _lines(out, "FAIL") if "슬라이드" in ln], f"\n{out}")


class BrokenVariantTests(unittest.TestCase):
    """고의 결함 변형은 반드시 FAIL을 내야 한다(검사가 실제로 작동하는지)."""

    def test_part_label_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as td:
            out = _verify(_build(Path(td), part01=BROKEN / "part-01.html"))
        fails = [ln for ln in _lines(out, "FAIL") if "PART 라벨" in ln]
        self.assertTrue(fails, f"라벨 불일치를 FAIL로 잡지 못했다:\n{out}")
        self.assertIn("W1", fails[0])

    def test_unwired_ready_asset_fails(self):
        with tempfile.TemporaryDirectory() as td:
            out = _verify(_build(Path(td), manifest=BROKEN / "unwired.json"))
        fails = [ln for ln in _lines(out, "FAIL") if "이미지 배선" in ln]
        self.assertTrue(fails, f"배선 누락을 FAIL로 잡지 못했다:\n{out}")
        self.assertIn("W1", fails[0])

    def test_orphan_manifest_entry_warns(self):
        with tempfile.TemporaryDirectory() as td:
            out = _verify(_build(Path(td), manifest=BROKEN / "unwired.json"))
        warns = [ln for ln in _lines(out, "WARN") if "고아" in ln]
        self.assertTrue(warns, f"고아 항목을 WARN으로 잡지 못했다:\n{out}")
        self.assertIn("W9", warns[0])


class DraftPrefixTests(unittest.TestCase):
    """DEC-05: `N주차_초안.md` 접두어 우선 · 무접두어 `초안.md` 레거시 폴백."""

    def test_prefixed_draft_wins_over_legacy(self):
        resolved = resolve_draft(FIXTURE, 9)
        self.assertIsNotNone(resolved)
        self.assertEqual(Path(resolved).name, "9주차_초안.md")

    def test_legacy_draft_is_fallback(self):
        with tempfile.TemporaryDirectory() as td:
            week = Path(td) / "9주차"
            week.mkdir()
            (week / "초안.md").write_text("# 레거시", encoding="utf-8")
            resolved = resolve_draft(week, 9)
        self.assertIsNotNone(resolved)
        self.assertEqual(Path(resolved).name, "초안.md")


if __name__ == "__main__":
    unittest.main()
