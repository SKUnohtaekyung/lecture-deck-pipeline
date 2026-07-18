"""2단계 파이프라인(조립 · 폰트 서브셋 임베드 · 자립성 강제) 회귀 테스트."""
from __future__ import annotations

import tempfile
import unittest
from io import BytesIO
from pathlib import Path

from fontTools.ttLib import TTFont

from scripts.assemble_deck import assemble
from scripts.font_embed import (
    DEFAULT_FONT,
    FontEmbedError,
    build_font_style,
    collect_glyphs,
    subset_woff2,
)
from scripts.inline_deck import bundle
from scripts.verify_distributable import self_containment_violations
from scripts import verify_kit


SHELL = (
    "<!doctype html><html><head>"
    '<link rel="stylesheet" href="../../kit/styles/deck.css">'
    '<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard/x.css">'
    "</head><body><div class=\"deck\">"
    '<section class="slide cover" data-slide="S01">표지</section>'
    "<!-- ::PARTS:: -->"
    '<section class="slide concept-recap" data-slide="END">마무리</section>'
    "</div><script>/* nav */</script></body></html>"
)
PART1 = '<section class="slide part-divider" data-slide="P1">파트하나</section>\n<section class="slide">본문</section>'
PART2 = '<section class="slide part-divider" data-slide="P2">파트둘</section>'


def _draft(root: Path, parts: dict[str, str], *, shell: str = SHELL, order=None) -> None:
    (root / "shell.html").write_text(shell, encoding="utf-8")
    for name, body in parts.items():
        (root / name).write_text(body, encoding="utf-8")
    if order is not None:
        (root / "order.txt").write_text("\n".join(order), encoding="utf-8")


class AssembleTests(unittest.TestCase):
    def test_marker_replaced_parts_in_name_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _draft(root, {"part-01.html": PART1, "part-02.html": PART2})
            out = root / "강의덱.html"
            ok, errors, _log = assemble(root, out)
            self.assertTrue(ok, errors)
            html = out.read_text(encoding="utf-8")
            self.assertNotIn("::PARTS::", html)
            self.assertLess(html.index("표지"), html.index("파트하나"))
            self.assertLess(html.index("파트하나"), html.index("파트둘"))
            self.assertLess(html.index("파트둘"), html.index("마무리"))
            self.assertEqual(html.count("part-divider"), 2)

    def test_order_txt_overrides_name_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _draft(root, {"part-01.html": PART1, "part-02.html": PART2}, order=["part-02.html", "part-01.html"])
            out = root / "강의덱.html"
            ok, _errors, _log = assemble(root, out)
            self.assertTrue(ok)
            html = out.read_text(encoding="utf-8")
            self.assertLess(html.index("파트둘"), html.index("파트하나"))

    def test_missing_marker_and_no_parts_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _draft(root, {"part-01.html": PART1}, shell=SHELL.replace("<!-- ::PARTS:: -->", ""))
            ok, errors, _ = assemble(root, root / "o.html")
            self.assertFalse(ok)
            self.assertTrue(errors)

            _draft(root, {"part-01.html": PART1}, shell=SHELL.replace("</head>", "<!-- ::PARTS:: --></head>"))
            ok, _e, _ = assemble(root, root / "o.html")
            self.assertFalse(ok)

            (root / "shell.html").write_text(SHELL, encoding="utf-8")
            for stale in root.glob("part-*.html"):
                stale.unlink()
            ok, _e, _ = assemble(root, root / "o.html")
            self.assertFalse(ok)


class GlyphCollectionTests(unittest.TestCase):
    def test_covers_static_css_content_escape_and_js_literal(self):
        # 렌더 경로 전부: 정적 텍스트 · CSS content · CSS \hex 이스케이프 · JS 리터럴 · ASCII
        html = (
            "<div>정적문장</div>"
            '<style>.a::before{content:"핵심"} .b::before{content:"\\25B8"}</style>'
            '<script>var t = "표지";</script>'
        )
        glyphs = set(collect_glyphs(html))
        for ch in "정적문장핵심표지":
            self.assertIn(ch, glyphs)
        self.assertIn("▸", glyphs)  # ▸ from CSS unicode escape
        self.assertIn("0", glyphs)
        self.assertIn("A", glyphs)


class SubsetTests(unittest.TestCase):
    def test_subset_is_valid_woff2_retains_axis_and_shrinks(self):
        woff2 = subset_woff2("가나다라ABC0123", source=DEFAULT_FONT)
        self.assertEqual(woff2[:4], b"wOF2")
        self.assertLess(len(woff2), DEFAULT_FONT.stat().st_size)
        font = TTFont(BytesIO(woff2))
        self.assertIn("fvar", font)  # wght 변수축 유지
        self.assertIn(ord("가"), font.getBestCmap())

    def test_build_font_style_emits_data_woff2_face(self):
        style, glyphs, size = build_font_style("<div>가나다</div>", source=DEFAULT_FONT)
        self.assertIn("@font-face", style)
        self.assertIn("data:font/woff2;base64,", style)
        self.assertGreater(glyphs, 0)
        self.assertGreater(size, 0)

    def test_missing_source_raises(self):
        with self.assertRaises(FontEmbedError):
            subset_woff2("가", source=Path("does-not-exist.woff2"))


class BundleFontTests(unittest.TestCase):
    def test_bundle_embeds_font_drops_cdn_and_ignores_commented_img(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".git").mkdir()
            (root / "deck.css").write_text('.a::before{content:"핵심"}', encoding="utf-8")
            deck = root / "deck.html"
            deck.write_text(
                "<html><head>"
                '<link rel="stylesheet" href="deck.css">'
                '<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard/x.css">'
                "</head><body><div>가나다 본문</div>"
                '<!-- <img src="자료/images/missing.png" alt="x"> 예시 주석 -->'
                "</body></html>",
                encoding="utf-8",
            )
            out = root / "out.html"
            ok, errors, _log = bundle(deck, output=out, offline=True, root=root)
            self.assertTrue(ok, errors)
            html = out.read_text(encoding="utf-8")
            self.assertIn("@font-face", html)
            self.assertIn("data:font/woff2;base64,", html)
            self.assertNotIn("jsdelivr", html)  # CDN link gone (font-family:'Pretendard' name may remain)
            self.assertNotIn("missing.png", html)  # commented img neither inlined nor failed
            self.assertEqual(self_containment_violations(html), [])  # fully self-contained


class DistributableGateTests(unittest.TestCase):
    CLEAN = (
        "<html><head><style>@font-face{font-family:Pretendard;"
        'src:url(data:font/woff2;base64,AAAA) format("woff2")}</style></head>'
        '<body><img src="data:image/png;base64,AA==" alt="x"></body></html>'
    )

    def test_clean_bundle_has_no_violations(self):
        self.assertEqual(self_containment_violations(self.CLEAN), [])

    def test_each_violation_class_is_detected(self):
        self.assertTrue(any("external" in v for v in self_containment_violations('<link rel="stylesheet" href="https://x/y.css">')))
        self.assertTrue(any("non-data" in v for v in self_containment_violations('<img src="a.png">', require_font=False)))
        self.assertTrue(any("font-face" in v for v in self_containment_violations("<div>x</div>")))
        self.assertTrue(any("Pretendard" in v for v in self_containment_violations('<link href="a-pretendard.css">', require_font=False)))
        self.assertTrue(any("unresolved" in v for v in self_containment_violations(
            '<figure class="asset-slot" data-image-purpose="explanatory" data-image-state="expected"></figure>',
            require_font=False,
        )))


class VerifyKitExemptTests(unittest.TestCase):
    def test_exempt_is_empty(self):
        # EXEMPT가 조용히 자라면 verify_kit.py의 고아 클래스 게이트가 무의미해진다.
        # 추가할 땐 반드시 이유를 적고(verify_kit.py 주석 참고) 이 테스트를 함께 갱신한다.
        self.assertEqual(verify_kit.EXEMPT, set())


if __name__ == "__main__":
    unittest.main()
