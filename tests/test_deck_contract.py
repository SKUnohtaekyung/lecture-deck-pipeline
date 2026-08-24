"""주차 구조 계약 외부화·신규 검사 회귀 테스트 (P6).

1주차 실덱에 과적합되지 않도록, 1주차 파일을 복사·참조하지 않는 독립 픽스처
(`tests/fixtures/mini-week/`)로 검사한다. 1주차는 동결(DEC-06)이라 이 테스트에서
읽지도 쓰지도 않는다 — `_contracts` 폴백 검증도 예외가 아니다: 1주차가
`courses/바이브코딩/sessions/1주차/`로 이관되며 동폴더에 `deck.contract.json`이
생겨 더는 ② `sessions/_contracts` 폴백을 타지 않으므로(① 동폴더에서 이미 찾는다),
1주차 실경로에 기대는 대신 tempdir 합성 픽스처 + `_contracts_dir` 패치로 폴백
"동작 자체"를 검증한다(`find_deck_contract`의 `repo_root`가 `__file__` 기준으로
고정돼 있어 순수 tempdir만으로는 ② 분기를 재현할 수 없다).
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

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
    return _verify_rc(deck, parts)[0]


def _verify_rc(deck: Path, parts: int = 2) -> tuple[str, int]:
    """출력 + 종료코드 — P1 검사는 exit 1까지 확인해야 한다(눈먼 0 방지)."""
    proc = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "verify_deck.py"), str(deck),
         "--parts", str(parts)],
        capture_output=True, text=True, encoding="utf-8", cwd=str(REPO),
    )
    return (proc.stdout or "") + (proc.stderr or ""), proc.returncode


def _build_mutated(tmp: Path, mutate=None, draft_append: str | None = None) -> Path:
    """픽스처를 복사한 뒤 계약(JSON)·초안을 변형해 조립한다 — P1 고의 불일치용."""
    week = tmp / "9주차"
    shutil.copytree(FIXTURE, week)
    if mutate is not None:
        cpath = week / "deck.contract.json"
        data = json.loads(cpath.read_text(encoding="utf-8"))
        mutate(data)
        cpath.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    if draft_append:
        draft = week / "9주차_초안.md"
        draft.write_text(draft.read_text(encoding="utf-8") + draft_append, encoding="utf-8")
    ok, errors, _log = assemble(week / "강의덱.초안")
    assert ok, f"픽스처 조립 실패: {errors}"
    return week / "강의덱.html"


def _lines(out: str, kind: str) -> list[str]:
    return [ln for ln in out.splitlines() if ln.startswith(f"[{kind}]")]


class ContractLookupTests(unittest.TestCase):
    """계약 3단 탐색: ① 동폴더 → ② sessions/_contracts → ③ 없으면 WARN."""

    def test_sibling_contract_is_found_first(self):
        found = find_deck_contract(FIXTURE / "강의덱.html")
        self.assertIsNotNone(found)
        self.assertEqual(found, (FIXTURE / "deck.contract.json").resolve())

    def test_falls_back_to_contracts_directory(self):
        # 동폴더에 deck.contract.json이 없고, _contracts 디렉터리에
        # <부모폴더명>.deck.contract.json이 있으면 그걸 찾아야 한다(② 분기).
        # 1주차 실경로에 기대지 않는 합성 tempdir 픽스처로 검증한다. repo_root는
        # find_deck_contract 내부에서 __file__ 기준으로 고정돼 매개변수화할 수
        # 없으므로, ②단이 조회하는 _contracts_dir()만 패치해 tempdir을 가리키게
        # 한다 — find_deck_contract 자체(①→②→③ 탐색 순서·조기 반환 조건)는
        # 손대지 않는다.
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            contracts_dir = td_path / "_contracts"
            contracts_dir.mkdir()
            week_dir = td_path / "9주차"
            week_dir.mkdir()
            deck_path = week_dir / "강의덱.html"
            deck_path.write_text("<html></html>", encoding="utf-8")
            # 동폴더에는 일부러 deck.contract.json을 두지 않는다(① 미스를 강제).
            contract_path = contracts_dir / "9주차.deck.contract.json"
            contract_path.write_text("{}", encoding="utf-8")

            with mock.patch("scripts.verify_deck._contracts_dir", return_value=contracts_dir):
                found = find_deck_contract(deck_path)

            self.assertIsNotNone(found)
            self.assertEqual(found.parent.name, "_contracts")
            self.assertEqual(found.name, "9주차.deck.contract.json")
            # Windows tempdir는 8.3 단축 경로(NOHTAE~1)로 올 수 있어 문자열 비교가
            # 환경 의존으로 깨진다(2026-08-17 실측 — 변경 전 커밋에서도 동일 실패).
            # 같은 파일인지는 양쪽을 canonicalize해 비교한다.
            self.assertEqual(found.resolve(), contract_path.resolve())

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


class PreservationGateTests(unittest.TestCase):
    """P1 보존 게이트(2026-08-17): 공동화 금지 · 양방향 완전성 · 절대사수 · waiver 스키마.

    각 고의 불일치가 실제로 exit 1을 내는지(검사가 도는지)부터 증명한다 —
    근거: plans/system-improvement/ANALYSIS.md §2-기제3 (V1-04 무검사 소실).
    """

    def test_healthy_fixture_passes_preservation_gate(self):
        with tempfile.TemporaryDirectory() as td:
            out, rc = _verify_rc(_build(Path(td)))
        self.assertEqual(rc, 0, f"정상 픽스처가 FAIL했다:\n{out}")
        self.assertFalse([ln for ln in _lines(out, "FAIL")], f"\n{out}")
        self.assertIn("계약 공동화 없음", out)

    def test_hollow_sequences_fails(self):
        with tempfile.TemporaryDirectory() as td:
            out, rc = _verify_rc(_build_mutated(
                Path(td), lambda d: d["decks"]["강의덱"].update(sequences={})))
        self.assertEqual(rc, 1)
        self.assertTrue([ln for ln in _lines(out, "FAIL") if "계약 공동화" in ln], f"\n{out}")

    def test_missing_slides_key_fails(self):
        with tempfile.TemporaryDirectory() as td:
            out, rc = _verify_rc(_build_mutated(
                Path(td), lambda d: d["decks"]["강의덱"].pop("slides")))
        self.assertEqual(rc, 1)
        self.assertTrue([ln for ln in _lines(out, "FAIL")
                         if "계약 공동화" in ln and "slides 키 부재" in ln], f"\n{out}")

    def test_contract_only_id_fails(self):
        with tempfile.TemporaryDirectory() as td:
            out, rc = _verify_rc(_build_mutated(
                Path(td), lambda d: d["decks"]["강의덱"]["sequences"]["PART2"].append("W9")))
        self.assertEqual(rc, 1)
        fails = [ln for ln in _lines(out, "FAIL") if "계약에 있는데 덱에 없음" in ln]
        self.assertTrue(fails, f"소실 방향을 FAIL로 잡지 못했다:\n{out}")
        self.assertIn("W9", fails[0])

    def test_deck_only_id_fails(self):
        with tempfile.TemporaryDirectory() as td:
            out, rc = _verify_rc(_build_mutated(
                Path(td), lambda d: d["decks"]["강의덱"]["sequences"]["PART2"].remove("W6")))
        self.assertEqual(rc, 1)
        fails = [ln for ln in _lines(out, "FAIL") if "덱에 있는데 계약에 없음" in ln]
        self.assertTrue(fails, f"무단 추가 방향을 FAIL로 잡지 못했다:\n{out}")
        self.assertIn("W6", fails[0])

    def test_valid_waiver_demotes_to_warn(self):
        def mutate(d):
            d["decks"]["강의덱"]["sequences"] = {}
            d["known_violations"]["contract_hollow"] = {
                "reason": "테스트 베이스라인", "date": "2026-08-17"}
        with tempfile.TemporaryDirectory() as td:
            out, rc = _verify_rc(_build_mutated(Path(td), mutate))
        self.assertEqual(rc, 0, f"유효 waiver가 강등되지 않았다:\n{out}")
        self.assertTrue([ln for ln in _lines(out, "WARN")
                         if "waiver 'contract_hollow' 적용" in ln], f"\n{out}")

    def test_waiver_without_date_is_not_honored(self):
        def mutate(d):
            d["decks"]["강의덱"]["sequences"] = {}
            d["known_violations"]["contract_hollow"] = {"reason": "사유만 있고 일자 없음"}
        with tempfile.TemporaryDirectory() as td:
            out, rc = _verify_rc(_build_mutated(Path(td), mutate))
        self.assertEqual(rc, 1, f"무일자 waiver가 강등돼 버렸다(무사유 탈출구):\n{out}")
        self.assertTrue([ln for ln in _lines(out, "WARN") if "무효 waiver" in ln], f"\n{out}")

    def test_waiver_scope_does_not_cover_future_ids(self):
        # 포괄 waiver 금지 — slides 목록 밖 위반은 waiver가 있어도 FAIL이어야 한다.
        def mutate(d):
            seq = d["decks"]["강의덱"]["sequences"]["PART2"]
            seq.remove("W5")
            seq.remove("W6")
            d["known_violations"]["coverage_deck_only"] = {
                "slides": ["W5"], "reason": "W5만 등재", "date": "2026-08-17"}
        with tempfile.TemporaryDirectory() as td:
            out, rc = _verify_rc(_build_mutated(Path(td), mutate))
        self.assertEqual(rc, 1)
        self.assertTrue([ln for ln in _lines(out, "FAIL")
                         if "덮지 않는 ID" in ln and "W6" in ln], f"\n{out}")

    def test_must_keep_missing_fails_and_waiver_demotes(self):
        with tempfile.TemporaryDirectory() as td:
            out, rc = _verify_rc(_build_mutated(
                Path(td), lambda d: d["decks"]["강의덱"].update(must_keep={"W9": "테스트"})))
        self.assertEqual(rc, 1)
        self.assertTrue([ln for ln in _lines(out, "FAIL") if "절대사수 ID 소실" in ln], f"\n{out}")

        def mutate(d):
            d["decks"]["강의덱"]["must_keep"] = {"W9": "테스트"}
            d["known_violations"]["must_keep_missing"] = {
                "slides": ["W9"], "reason": "소실 이력 등재", "date": "2026-08-17"}
        with tempfile.TemporaryDirectory() as td:
            out, rc = _verify_rc(_build_mutated(Path(td), mutate))
        self.assertEqual(rc, 0, f"\n{out}")

    def test_draft_marker_requires_must_keep_migration(self):
        with tempfile.TemporaryDirectory() as td:
            out, rc = _verify_rc(_build_mutated(
                Path(td), draft_append="\n> **절대 사수** — 1-1(테스트)\n"))
        self.assertEqual(rc, 1)
        self.assertTrue([ln for ln in _lines(out, "FAIL")
                         if "must_keep" in ln and "이관하라" in ln], f"\n{out}")


class UnjudgedContractKeyTests(unittest.TestCase):
    """계약 키가 없으면 해당 검사가 **한 줄도 내지 않고 사라지던** 문제.

    실측(2026-08-24 · plans/gate-input-hardening F4): 3주차는 `dark_terminal_slides`가,
    1주차는 `must_keep`이 계약에 없어 관련 검사가 조용히 생략됐다. WARN조차 아니어서
    화면에서 「위반 0건」과 「아무것도 안 봄」이 구분되지 않았다. 지금은 «미판정»으로
    센다 — 단, **판정 계수(FAIL/WARN/PASS)는 건드리지 않는다**(러너 래칫 불변).
    """

    def test_missing_key_is_listed_as_unjudged(self):
        with tempfile.TemporaryDirectory() as td:
            deck = _build_mutated(Path(td), mutate=lambda d: (d["decks"]["강의덱"]
                                                              .pop("dividers", None)))
            out, _rc = _verify_rc(deck)
        self.assertIn("미판정", out)
        self.assertIn("dividers", out)

    def test_unjudged_does_not_change_verdict_counts(self):
        """미판정이 늘어도 요약 줄의 FAIL/WARN/PASS 계수는 그대로여야 한다."""
        with tempfile.TemporaryDirectory() as td:
            base, _ = _verify_rc(_build_mutated(Path(td) / "a"))
        with tempfile.TemporaryDirectory() as td:
            mut, _ = _verify_rc(_build_mutated(Path(td) / "b",
                                               mutate=lambda d: (d["decks"]["강의덱"]
                                                                 .pop("dividers", None))))
        pat = re.compile(r"요약: FAIL (\d+) · WARN (\d+) · PASS (\d+)")
        mb, mm = pat.search(base), pat.search(mut)
        self.assertIsNotNone(mb)
        self.assertIsNotNone(mm)
        # dividers 검사 1건이 사라졌으므로 PASS가 1 줄어드는 것은 정상이다.
        # 확인하려는 것은 «미판정 줄이 계수 채널을 오염시키지 않는가»다.
        self.assertEqual(mb.group(1), mm.group(1), "미판정 때문에 FAIL 계수가 바뀌었다")
        self.assertEqual(mb.group(2), mm.group(2), "미판정 때문에 WARN 계수가 바뀌었다")


class WaiverLintTests(unittest.TestCase):
    """scripts/verify_contract_waivers.py — 무사유 waiver 거부 스키마의 정본."""

    def _lint(self, kv) -> list[str]:
        from scripts.verify_contract_waivers import lint_contract
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "deck.contract.json"
            p.write_text(json.dumps({"known_violations": kv}, ensure_ascii=False),
                         encoding="utf-8")
            return lint_contract(str(p))

    def test_valid_entry_passes(self):
        self.assertEqual(self._lint({"k": {"reason": "사유", "date": "2026-08-17"}}), [])

    def test_missing_date_fails(self):
        self.assertTrue(self._lint({"k": {"reason": "사유"}}))

    def test_empty_reason_fails(self):
        self.assertTrue(self._lint({"k": {"reason": " ", "date": "2026-08-17"}}))

    def test_bad_date_format_fails(self):
        self.assertTrue(self._lint({"k": {"reason": "사유", "date": "26-08-17"}}))


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
