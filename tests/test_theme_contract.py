# -*- coding: utf-8 -*-
"""테마 계약 회귀 — 선언(`kit/themes/<이름>/tokens.css`) ↔ 집행(`kit/styles/deck.css`).

왜 이 파일이 필요한가
--------------------
2026-08-24(plans/gate-input-hardening P2)에 테마 축을 신설하면서 현행 99토큰을
`kit/themes/default/tokens.css`에 **등재**했다. 사용자 확정 제약이 「1·2·3주차
산출물·컬러 키트·디자인은 값 하나도 바꾸지 않는다」라 «이동»이 아니라 «복제»다.

값이 두 곳에 있으면 어긋나는 것이 이 저장소의 반복 사고다(지도 §8.4 유형⑤:
정본표가 선언한 값 8건이 kit에서 실현되지 않고 각 주차 shell 오버라이드에만
있었다). 그래서 복제를 허용하는 대신 **드리프트를 회귀로 고정**한다 — 한쪽만
고치면 여기서 즉시 깨진다.

이것은 파이프라인 게이트가 아니라 회귀다. P2의 계약은 「선언만, 집행 변화 없음」
이므로 검사기 거동은 건드리지 않았다.

실행: python -m unittest tests.test_theme_contract
"""
from __future__ import annotations

import io
import re
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DECK_CSS = REPO / "kit" / "styles" / "deck.css"
sys.path.insert(0, str(REPO / "scripts"))
import verify_deck  # noqa: E402

THEMES_DIR = REPO / "kit" / "themes"
DEFAULT_THEME = THEMES_DIR / "default" / "tokens.css"

# G1(2026-08-24 사용자 확정): 테마가 바꿀 수 있는 것은 토큰 «값»뿐이다.
# 구조 셸 어휘는 전 테마 공통 고정 — 브라우저 감사기 2종의 fail-closed와
# 제외 앵커가 이 이름들 위에 서 있다(plans/gate-input-hardening F3).
FROZEN_SHELL_CLASSES = ("slide", "s-head", "s-pageno", "s-title", "asset-slot", "slide-num")


def _root_tokens(text: str) -> dict:
    """`:root { … }`의 `--토큰: 값;`을 순서를 보존해 읽는다."""
    m = re.search(r":root\s*\{(.*?\n)\}", text, re.S)
    if not m:
        return {}
    out = {}
    for name, value in re.findall(r"(--[a-z0-9-]+)\s*:\s*([^;]+);", m.group(1)):
        out[name] = re.sub(r"\s+", " ", value).strip()
    return out


class DefaultThemeMirrorsKitTests(unittest.TestCase):
    """default 테마 선언이 집행부(deck.css :root)와 한 글자도 다르지 않아야 한다."""

    def setUp(self):
        self.enforced = _root_tokens(io.open(DECK_CSS, encoding="utf-8").read())
        self.declared = _root_tokens(io.open(DEFAULT_THEME, encoding="utf-8").read())

    def test_theme_file_exists_and_is_not_empty(self):
        self.assertTrue(DEFAULT_THEME.is_file(), f"없음: {DEFAULT_THEME}")
        self.assertTrue(self.declared, "테마 파일에서 :root 토큰을 하나도 읽지 못했다")

    def test_token_names_match_exactly(self):
        self.assertEqual(sorted(self.declared), sorted(self.enforced),
                         "테마 선언과 deck.css :root의 토큰 «집합»이 다르다")

    def test_token_values_match_exactly(self):
        diff = {k: (self.enforced[k], self.declared[k])
                for k in self.enforced
                if k in self.declared and self.enforced[k] != self.declared[k]}
        self.assertEqual(diff, {}, f"토큰 «값»이 어긋났다(집행, 선언): {diff}")

    def test_token_count_is_the_registered_99(self):
        """계수를 고정한다 — 토큰이 늘거나 줄면 테마 계약 문서도 함께 갱신해야 한다."""
        self.assertEqual(len(self.enforced), 99,
                         "deck.css :root 토큰 수가 99가 아니다 — "
                         "kit/guide/테마-계약.md의 계수와 이 테스트를 함께 갱신하라")


class EveryThemeIsCompleteTests(unittest.TestCase):
    """테마가 늘어나도 «토큰 이름 집합»은 같아야 한다.

    값은 테마마다 다른 것이 정상이지만(그게 테마다), **이름이 빠지면** 그 토큰을
    쓰는 구도가 폴백 없이 깨지거나 브라우저 기본값으로 조용히 내려간다. 이름
    완전성만 전 테마 공통 계약으로 고정한다(값 일치는 default에만 요구).
    """

    def test_all_themes_declare_the_same_token_names(self):
        enforced = set(_root_tokens(io.open(DECK_CSS, encoding="utf-8").read()))
        themes = sorted(p for p in THEMES_DIR.glob("*/tokens.css"))
        self.assertTrue(themes, "kit/themes/ 아래에 테마가 하나도 없다")
        for path in themes:
            with self.subTest(theme=path.parent.name):
                declared = set(_root_tokens(io.open(path, encoding="utf-8").read()))
                self.assertEqual(declared, enforced,
                                 f"테마 '{path.parent.name}'의 토큰 이름 집합이 다르다 "
                                 f"(빠짐 {sorted(enforced - declared)} · "
                                 f"군더더기 {sorted(declared - enforced)})")


class ThemeStylesheetLinkTests(unittest.TestCase):
    """테마 파일이 «링크 대상»으로 승격된 뒤의 거동을 고정한다(2026-08-29).

    왜 이 테스트가 생겼나 — 두 번째 테마를 등재하고 나서야 드러난 구멍이다.
    테마 파일은 «선언»이고 집행은 `kit/styles/deck.css`였다. 그래서 등재된 테마로
    **정상적인 주차 덱을 만들 수 없었다**: 실제 주차 덱처럼 정본 kit을 링크하면
    `deck.css :root`가 default 팔레트라 「[kit] 토큰 값 정확」이 FAIL했다(실측
    `--blue:#3060C3` 외 4건). 통과시키는 유일한 길이 kit CSS 전체를 복사해 `:root`만
    바꾼 사본을 두는 것이었는데, 그건 드리프트 보장 장치다.

    이제 덱은 `deck.css` 다음에 `kit/themes/<이름>/tokens.css`를 링크하고 캐스케이드가
    `:root`를 덮는다. default 테마 덱은 아무것도 더 링크하지 않으므로 **기존 동결
    산출물의 렌더는 바뀌지 않는다**(D-1).
    """

    def _deck(self, root, links):
        tags = "".join('<link rel="stylesheet" href="%s">' % h for h in links)
        deck = root / "강의덱.html"
        deck.write_text("<html><head>" + tags + "</head><body></body></html>",
                        encoding="utf-8")
        return deck

    def setUp(self):
        import tempfile
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "kit" / "themes" / "코발트").mkdir(parents=True)
        (self.root / "kit" / "themes" / "코발트" / "tokens.css").write_text(
            ":root{ --blue:#3060C3; }", encoding="utf-8")
        (self.root / "kit" / "styles").mkdir(parents=True)
        (self.root / "kit" / "styles" / "tokens.css").write_text(
            ":root{ --blue:#000000; }", encoding="utf-8")   # themes/ 밖 동명 파일
        self.addCleanup(self.tmp.cleanup)

    def test_linked_theme_is_found_with_its_name(self):
        deck = self._deck(self.root, ["kit/themes/코발트/tokens.css"])
        got = verify_deck.linked_theme_tokens(deck.read_text(encoding="utf-8"), str(deck))
        self.assertEqual([n for n, _ in got], ["코발트"])
        self.assertIn("#3060C3", got[0][1])

    def test_no_theme_link_returns_empty(self):
        """default 테마 덱 — 아무것도 더 링크하지 않는다. 종전 거동 그대로여야 한다."""
        deck = self._deck(self.root, ["kit/styles/deck.css"])
        self.assertEqual(
            verify_deck.linked_theme_tokens(deck.read_text(encoding="utf-8"), str(deck)), [])

    def test_tokens_css_outside_themes_dir_is_not_a_theme(self):
        """`themes/` 밖의 동명 파일을 테마로 오인하면 엉뚱한 팔레트가 기대값이 된다."""
        deck = self._deck(self.root, ["kit/styles/tokens.css"])
        self.assertEqual(
            verify_deck.linked_theme_tokens(deck.read_text(encoding="utf-8"), str(deck)), [])

    def test_remote_stylesheet_is_ignored(self):
        deck = self._deck(self.root, ["https://cdn.example/themes/x/tokens.css"])
        self.assertEqual(
            verify_deck.linked_theme_tokens(deck.read_text(encoding="utf-8"), str(deck)), [])

    def test_two_theme_links_are_reported_so_the_gate_can_fail(self):
        """둘을 링크하면 어느 값이 이기는지 파일 순서에 의존한다 — 게이트가 막아야 한다."""
        (self.root / "kit" / "themes" / "다른").mkdir(parents=True)
        (self.root / "kit" / "themes" / "다른" / "tokens.css").write_text(
            ":root{ --blue:#111111; }", encoding="utf-8")
        deck = self._deck(self.root, ["kit/themes/코발트/tokens.css",
                                      "kit/themes/다른/tokens.css"])
        got = verify_deck.linked_theme_tokens(deck.read_text(encoding="utf-8"), str(deck))
        self.assertEqual(len(got), 2, got)


class ThemeContractDocTests(unittest.TestCase):
    """계약 문서가 실재하고, 동결 어휘를 실제로 등재하고 있는가."""

    CONTRACT = REPO / "kit" / "guide" / "테마-계약.md"

    def test_contract_doc_exists(self):
        self.assertTrue(self.CONTRACT.is_file(), f"없음: {self.CONTRACT}")

    def test_every_frozen_shell_class_is_listed(self):
        text = io.open(self.CONTRACT, encoding="utf-8").read()
        missing = [c for c in FROZEN_SHELL_CLASSES if c not in text]
        self.assertEqual(missing, [],
                         f"동결 어휘가 계약 문서에 없다: {missing} — "
                         "브라우저 감사기의 fail-closed가 이 이름들 위에 서 있다")

    def test_frozen_shell_classes_are_actually_used_by_the_auditors(self):
        """문서가 «실재하지 않는 이름»을 동결하고 있지 않은지 역방향으로 확인한다.

        선언이 집행과 무관해지는 것이 이 저장소의 유형⑤ 사고다 — 동결 목록이
        감사기가 실제로 보는 이름인지 확인한다."""
        auditors = "\n".join(
            io.open(REPO / "scripts" / name, encoding="utf-8").read()
            for name in ("audit_render.js", "audit_typography.js"))
        orphan = [c for c in FROZEN_SHELL_CLASSES if c not in auditors]
        self.assertEqual(orphan, [],
                         f"감사기가 쓰지 않는 이름을 동결하고 있다: {orphan}")


if __name__ == "__main__":
    unittest.main()
