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

    def test_token_count_is_the_registered_100(self):
        """계수를 고정한다 — 토큰이 늘거나 줄면 테마 계약 문서도 함께 갱신해야 한다."""
        self.assertEqual(len(self.enforced), 100,
                         "deck.css :root 토큰 수가 100가 아니다 — "
                         "kit/guide/테마-계약.md의 계수와 이 테스트를 함께 갱신하라")


class BlueChannelMirrorsBlueTests(unittest.TestCase):
    """`--blue-rgb`는 `--blue`와 «같은 색»이어야 한다 — 한 색이 두 토큰에 산다(2026-08-29).

    왜 두 토큰인가: `rgba()`는 색을 `var()`로 받지 못한다. 그래서 컴포넌트가
    `rgba(<브랜드파랑>,α)`를 쓰려면 **채널값**이 따로 필요하다. 그것이 없어서 kit
    컴포넌트 11곳이 `rgba(29,78,216,α)`를 직접 박고 있었고, 테마를 바꿔도 그 자리만
    default 파랑으로 남았다(적대적 검증 실측).

    ⚠️ 한 색이 두 곳에 사는 순간 어긋난다 — 그게 이 저장소의 반복 사고다.
       그래서 «둘이 같은 색인가»를 회귀로 못박는다. 새 테마는 반드시 둘 다 바꿔야 한다.
    """

    def test_every_theme_keeps_the_two_in_sync(self):
        themes = sorted(p for p in THEMES_DIR.glob("*/tokens.css"))
        self.assertTrue(themes, "kit/themes/ 아래에 테마가 하나도 없다")
        judged = 0
        for path in themes:
            declared = _root_tokens(io.open(path, encoding="utf-8").read())
            with self.subTest(theme=path.parent.name):
                hexv = declared.get("--blue", "")
                chan = declared.get("--blue-rgb", "")
                self.assertRegex(hexv, r"^#[0-9A-Fa-f]{6}$", "--blue 형식이 hex가 아니다")
                m = re.match(r"^\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*$", chan)
                self.assertTrue(m, "--blue-rgb 형식이 'R,G,B'가 아니다: %r" % chan)
                want = tuple(int(hexv[k:k + 2], 16) for k in (1, 3, 5))
                got = tuple(int(g) for g in m.groups())
                self.assertEqual(got, want,
                                 "테마 '%s': --blue-rgb %s 가 --blue %s (%s)와 다른 색이다"
                                 % (path.parent.name, chan, hexv, ",".join(map(str, want))))
                judged += 1
        self.assertEqual(judged, len(themes), "판정 %d건 · 테마 %d개 — 미판정이 섞였다"
                         % (judged, len(themes)))


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


class EveryThemeMeetsTypeFloorsTests(unittest.TestCase):
    """등재 조건 ㉡(토큰 값 ↔ R-TYPE-01 역할별 하한)을 **회귀로** 고정한다(2026-08-29 신설).

    왜 필요한가 — 종전에 ㉡은 «등재 시점에 사람이 한 번 돌리는 절차»였다(계약 §4㉡).
    절차는 잊히고, 잊히면 계약 §4㉡이 경고한 바로 그 일이 일어난다:
    **테마가 스스로 하한 미달을 생산하면 그 테마로 만든 모든 덱이 첫날부터 FAIL한다.**
    `EveryThemeIsCompleteTests`는 토큰 «이름»만 보므로 값이 22 → 14로 떨어져도 통과한다.

    하한의 정본은 **집행부**(`scripts/audit_typography.js`의 `TIERS`)에서 읽는다 —
    여기 숫자를 복제하면 그 복제본이 정본과 어긋나는 것이 이 저장소의 반복 사고다.
    """

    #: 하한을 «직접» 지는 역할 토큰 → audit_typography.js TIERS의 티어 이름
    FLOOR_BEARING = {
        "--fs-body": "narrative",
        "--fs-lead": "narrative",
        "--fs-box-desc": "boxDesc",
        "--fs-table": "table",
        "--fs-caption": "label",
        "--fs-eyebrow": "label",
        "--fs-badge": "badge",
    }
    #: 본문보다 커야 하는 디스플레이 계열 — 본문 하한(narrative) 아래로 내려가면 안 된다
    ABOVE_BODY = ("--fs-cover", "--fs-part", "--fs-display-lg", "--fs-display",
                  "--fs-title", "--fs-box-title")

    @classmethod
    def setUpClass(cls):
        js = io.open(REPO / "scripts" / "audit_typography.js", encoding="utf-8").read()
        m = re.search(r"rules\.TIERS\s*=\s*\{(.*?)\};", js, re.S)
        assert m, "audit_typography.js에서 TIERS 블록을 찾지 못했다 — 집행 정본 위치가 바뀌었나?"
        cls.floors = {k: int(v) for k, v in
                      re.findall(r"(\w+)\s*:\s*\{\s*floor:\s*(\d+)", m.group(1))}
        assert cls.floors, "TIERS를 파싱하지 못했다"

    def test_floors_were_read_from_the_enforcer(self):
        """하한을 못 읽었는데 통과하면 «아무것도 안 본» PASS다 — 눈먼 0 방지."""
        for tier in ("narrative", "boxDesc", "table", "label", "badge"):
            self.assertIn(tier, self.floors, "집행부에서 %s 티어를 못 읽었다" % tier)

    def test_every_theme_meets_every_role_floor(self):
        themes = sorted(p for p in THEMES_DIR.glob("*/tokens.css"))
        self.assertTrue(themes, "kit/themes/ 아래에 테마가 하나도 없다")
        judged = 0
        for path in themes:
            declared = _root_tokens(io.open(path, encoding="utf-8").read())
            with self.subTest(theme=path.parent.name):
                for token, tier in self.FLOOR_BEARING.items():
                    self.assertIn(token, declared, token)
                    px = int(re.match(r"(\d+)", declared[token]).group(1))
                    judged += 1
                    self.assertGreaterEqual(
                        px, self.floors[tier],
                        "테마 '%s'의 %s = %dpx 가 %s 하한 %dpx 미만이다 — "
                        "이 테마로 만든 모든 덱이 첫날부터 FAIL한다(계약 §4㉡)"
                        % (path.parent.name, token, px, tier, self.floors[tier]))
                for token in self.ABOVE_BODY:
                    self.assertIn(token, declared, token)
                    px = int(re.match(r"(\d+)", declared[token]).group(1))
                    judged += 1
                    self.assertGreaterEqual(
                        px, self.floors["narrative"],
                        "테마 '%s'의 %s = %dpx 가 본문 하한 %dpx 미만이다"
                        % (path.parent.name, token, px, self.floors["narrative"]))
        # 「대상 계수 0」은 통과가 아니라 미판정이다(AGENTS 2026-08-24 집행).
        expect = len(themes) * (len(self.FLOOR_BEARING) + len(self.ABOVE_BODY))
        self.assertEqual(judged, expect,
                         "판정 %d건 · 기대 %d건 — 미판정이 섞였다" % (judged, expect))


class PaletteGateResistsBypassTests(unittest.TestCase):
    """팔레트 검사가 «파일 텍스트»가 아니라 «적용되는 CSS»를 보는지 고정한다(2026-08-29).

    적대적 검증에서 **화면은 틀린 색인데 게이트는 PASS**인 덱을 6가지로 만들 수 있었다.
    전부 같은 뿌리였다 — 검사가 링크된 `deck.css`의 «텍스트»에서 기대문자열을 substring
    으로 찾았기 때문이다. 아래가 그 6가지를 각각 고정한다. 하나라도 통과하면 미탐이다.
    """

    def _build(self, root, head_extra="", theme_value="#3060C3"):
        (root / "kit" / "styles").mkdir(parents=True, exist_ok=True)
        (root / "kit" / "styles" / "deck.css").write_text(
            ":root{ --blue:#1D4ED8; --mint:#14B8A6; }", encoding="utf-8")
        (root / "kit" / "themes" / "cobalt").mkdir(parents=True, exist_ok=True)
        (root / "kit" / "themes" / "cobalt" / "tokens.css").write_text(
            ":root{ --blue:%s; --mint:#14B8A6; }" % theme_value, encoding="utf-8")
        deck = root / "강의덱.html"
        deck.write_text("<html><head>" + head_extra + "</head><body></body></html>",
                        encoding="utf-8")
        return deck

    def setUp(self):
        import tempfile
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)
        self.KIT = '<link rel="stylesheet" href="kit/styles/deck.css">'
        self.THEME = '<link rel="stylesheet" href="kit/themes/cobalt/tokens.css">'

    def _eff(self, deck):
        eff, offenders, skipped = verify_deck.effective_palette(
            deck.read_text(encoding="utf-8"), str(deck), {"--blue", "--mint"})
        return eff, offenders, skipped

    def test_correct_order_gives_the_theme_value(self):
        """대조군 — 올바른 덱은 테마 값이 이겨야 한다(오탐 방지)."""
        deck = self._build(self.root, self.KIT + self.THEME)
        eff, offenders, _ = self._eff(deck)
        self.assertEqual(eff.get("--blue"), "#3060C3")
        self.assertEqual(offenders, [])

    def test_reversed_link_order_yields_the_default_value(self):
        """★ 테마를 먼저 링크하면 화면은 default다 — 검사도 그렇게 봐야 한다."""
        deck = self._build(self.root, self.THEME + self.KIT)
        eff, _o, _s = self._eff(deck)
        self.assertEqual(eff.get("--blue"), "#1D4ED8",
                         "링크 순서를 무시하면 «화면은 default인데 PASS»가 된다")

    def test_inline_style_root_override_is_seen(self):
        """덱 인라인 <style>의 :root 재정의를 못 보면 무엇이든 덮어쓸 수 있다."""
        deck = self._build(self.root,
                           self.KIT + self.THEME + "<style>:root{--blue:#FF00FF}</style>")
        eff, _o, _s = self._eff(deck)
        self.assertEqual(eff.get("--blue"), "#FF00FF")

    def test_non_root_selector_is_reported_as_offender(self):
        """.deck{--blue:…}는 하위 전체를 바꾸는데 documentElement의 computed 값은 정상이라
        수동 점검조차 속는다 — 그래서 «:root 밖 선언» 자체를 위반으로 본다."""
        deck = self._build(self.root,
                           self.KIT + self.THEME + "<style>.deck{--blue:#00FF00}</style>")
        _e, offenders, _s = self._eff(deck)
        self.assertTrue(any(tok == "--blue" for _sel, tok in offenders), offenders)

    def test_comment_cannot_forge_the_expected_value(self):
        """주석에 기대값을 넣어 substring 매칭을 속이던 우회."""
        (self.root / "kit" / "themes" / "fake").mkdir(parents=True)
        (self.root / "kit" / "themes" / "fake" / "tokens.css").write_text(
            ":root{ /* --blue:#3060C3 */ --blue:#000000; --mint:#14B8A6; }", encoding="utf-8")
        deck = self._build(
            self.root,
            self.KIT + '<link rel="stylesheet" href="kit/themes/fake/tokens.css">')
        eff, _o, _s = self._eff(deck)
        self.assertEqual(eff.get("--blue"), "#000000",
                         "주석을 제거하지 않으면 가짜 테마가 통과한다")

    def test_disabled_and_print_only_links_do_not_count(self):
        """링크는 있는데 화면에 적용되지 않는 경우 — 값은 반영되지 않고 사유가 남아야 한다."""
        for extra in ('<link rel="stylesheet" href="kit/themes/cobalt/tokens.css" disabled>',
                      '<link rel="stylesheet" href="kit/themes/cobalt/tokens.css" media="print">'):
            with self.subTest(extra=extra):
                deck = self._build(self.root, self.KIT + extra)
                eff, _o, skipped = self._eff(deck)
                self.assertEqual(eff.get("--blue"), "#1D4ED8")
                self.assertTrue(skipped, "건너뛴 사유가 기록되지 않으면 조용한 통과다")


class UnresolvedThemeIsUnjudgedTests(unittest.TestCase):
    """활성 테마를 특정하지 못하면 «미판정»이어야 한다 — default로 가정하면 항등식 PASS다.

    종전에는 과목이 모호하거나 프로필 §5 표기가 흔들리면 조용히 `default`로 떨어졌다.
    `kit/themes/default/tokens.css`는 항상 읽히므로 토큰 dict가 비지 않고, 호출부는
    dict가 빌 때만 미판정을 기록한다 — 그래서 **해석 실패가 어디에도 안 남은 채**
    deck.css(default 하드코딩)와 default 테마를 대조하는 항등식이 됐다.
    적대적 검증에서 두 경로로 독립 재현됐다.
    """

    def test_ambiguous_course_returns_empty_tokens_not_default(self):
        import os
        from unittest import mock
        with mock.patch.dict(os.environ, {"CREATE_SLIDES_COURSE": "존재하지않는과목"}):
            name, tokens, why = verify_deck.load_active_theme(str(REPO / "scripts"))
        self.assertEqual(tokens, {}, "해석 실패인데 토큰을 돌려주면 항등식 PASS가 된다")
        self.assertEqual(name, "")
        self.assertIn("특정할 수 없다", why)


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
