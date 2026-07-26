"""2단계 파이프라인(조립 · 폰트 서브셋 임베드 · 자립성 강제) 회귀 테스트."""
from __future__ import annotations

import json
import re
import sys
import tempfile
import unittest
from io import BytesIO
from pathlib import Path
from unittest import mock

from fontTools.ttLib import TTFont

from scripts import inject_presenter
from scripts import verify_deck
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


PRESENTER_DECK = (
    "<!doctype html><html lang=\"ko\"><head><meta charset=\"utf-8\">"
    "<style>:root{--sw:1280px;--blue:#1D4ED8}</style></head><body>"
    '<div class="deck">'
    '<section class="slide cover" data-slide="S01"><h1>표지 제목</h1></section>'
    '<section class="slide" data-slide="S02"><h2>두 번째 장</h2>'
    '<img src="data:image/png;base64,AA==" alt="x"></section>'
    '<section class="slide" data-slide="S03"><h2>세 번째 장</h2></section>'
    "</div>"
    '<div class="controls" id="controls"></div>'
    "<script>/* deck engine */</script></body></html>"
)


def _notes(*blocks: str) -> str:
    return "<html><body>" + "".join(blocks) + "</body></html>"


def _note_block(no: str, title: str, kind: str = "pn-joke", text: str = "여기서 멘트") -> str:
    return (
        '<div class="pn-slide"><div class="pn-slide-head">'
        f'<span class="pn-no">{no}</span><h2 class="pn-slide-title">{title}</h2></div>'
        f'<div class="pn-item {kind}"><span class="lbl">LBL</span><p>{text}</p></div></div>'
    )


class InjectPresenterTests(unittest.TestCase):
    """발표 런타임 주입기: 멱등 · 슬라이드 불변 · 노트 게이트 · fail-closed."""

    def _inject(self, deck=PRESENTER_DECK, notes=None, deck_id="wk-test"):
        return inject_presenter.inject(deck, deck_id=deck_id, notes_html=notes, source_name="src.html")

    def test_injection_preserves_slides_and_places_nodes_outside_deck(self):
        notes = _notes(_note_block("02", "두 번째 장"))
        out, meta = self._inject(notes=notes)

        # 슬라이드 지문이 한 글자도 변하지 않았다.
        _s, i0, i1, _n = inject_presenter.find_deck_range(PRESENTER_DECK)
        before = inject_presenter.fingerprint(PRESENTER_DECK, i0, i1)
        _s2, j0, j1, _n2 = inject_presenter.find_deck_range(out)
        after = inject_presenter.fingerprint(out, j0, j1)
        for key in ("slide_count", "slide_ids", "start_tags", "inner_hashes", "img_count", "img_srcs", "build_hash"):
            self.assertEqual(before[key], after[key], key)

        # 마커 3종 + 주입 노드가 .deck 밖에만 있다.
        self.assertIn('data-presenter-runtime="1.0.0"', out)
        self.assertIn('data-deck-id="wk-test"', out)
        self.assertIn("data-build-hash=", out)
        for pat in (r"<style[^>]*data-presenter-runtime", r"<script[^>]*data-presenter-runtime",
                    r"<script[^>]*data-presenter-notes"):
            spots = [m.start() for m in re.finditer(pat, out)]
            self.assertEqual(len(spots), 1, pat)
            self.assertFalse(j0 <= spots[0] < j1, f"{pat} 가 .deck 안에 있음")

        # 노트가 slideId에 붙고, 이모지·라벨은 저장되지 않는다.
        self.assertEqual(meta["notes"], {"entries": 1, "mapped": 1, "emptySlides": ["S01", "S03"]})
        block = re.search(r'data-presenter-notes>(.*?)</script>', out, re.S).group(1)
        payload = json.loads(block)
        self.assertEqual(payload["notes"], {"S02": [{"kind": "joke", "text": "여기서 멘트"}]})
        self.assertNotIn("LBL", block)

    def test_notes_json_escapes_script_terminator(self):
        # 노트 원문에는 엔티티로 적혀 있고, 파서가 실제 문자로 복원한다.
        # 그 상태로 JSON에 실리면 스크립트 블록이 조기 종료되므로 주입기가 이스케이프해야 한다.
        notes = _notes(_note_block("02", "두 번째 장",
                                   text="닫는태그 &lt;/script&gt; 와 &amp; 그리고 &lt;!-- 주석"))
        out, _meta = self._inject(notes=notes)
        block = re.search(r'data-presenter-notes>(.*?)</script>', out, re.S).group(1)
        for ch in ("<", ">", "&"):
            self.assertNotIn(ch, block)                       # 원문자는 블록에 남지 않는다
        text = json.loads(block)["notes"]["S02"][0]["text"]
        self.assertIn("</script>", text)                      # 값은 손상되지 않는다
        self.assertIn("&", text)
        self.assertIn("<!--", text)

    def test_second_injection_aborts(self):
        out, _ = self._inject()
        with self.assertRaises(inject_presenter.InjectError):
            self._inject(deck=out)

    def test_note_title_mismatch_aborts(self):
        notes = _notes(_note_block("02", "전혀 다른 제목"))
        with self.assertRaises(inject_presenter.InjectError):
            self._inject(notes=notes)

    def test_headingless_slide_skips_title_check_but_others_still_gate(self):
        # 제목(h1~h3)이 없는 전환 슬라이드는 대조할 대상이 없어 제목 검사를 건너뛴다.
        deck = PRESENTER_DECK.replace('<h2>세 번째 장</h2>', '<p class="big">해.</p>')
        out, meta = self._inject(deck=deck, notes=_notes(_note_block("03", "해.")))
        self.assertEqual(meta["notes"]["mapped"], 1)
        # 제목이 있는 슬라이드는 여전히 하드 실패다(게이트를 넓히지 않았다).
        with self.assertRaises(inject_presenter.InjectError):
            self._inject(deck=deck, notes=_notes(_note_block("02", "엉뚱한 제목")))

    def test_note_out_of_range_aborts(self):
        with self.assertRaises(inject_presenter.InjectError):
            self._inject(notes=_notes(_note_block("99", "두 번째 장")))

    def test_note_exhaustion_mismatch_aborts(self):
        # pn-slide-head는 2개인데 파서가 1개만 뽑는 상황(두 번째 블록에 번호가 없다) → 중단.
        broken = _notes(
            _note_block("02", "두 번째 장"),
            '<div class="pn-slide"><div class="pn-slide-head">'
            '<h2 class="pn-slide-title">세 번째 장</h2></div></div>',
        )
        self.assertEqual(inject_presenter.count_note_blocks(broken), 2)
        with self.assertRaises(inject_presenter.InjectError):
            self._inject(notes=broken)

    def test_missing_or_duplicate_slide_id_aborts(self):
        with self.assertRaises(inject_presenter.InjectError):
            self._inject(deck=PRESENTER_DECK.replace(' data-slide="S03"', ""))
        with self.assertRaises(inject_presenter.InjectError):
            self._inject(deck=PRESENTER_DECK.replace('data-slide="S03"', 'data-slide="S02"'))

    def test_cli_is_fail_closed_and_leaves_source_untouched(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "강의덱_배포.html"
            src.write_text(PRESENTER_DECK, encoding="utf-8")
            before = src.read_bytes()
            out = root / "강의덱_발표.html"
            meta = root / "meta.json"
            bad = root / "notes.html"
            bad.write_text(_notes(_note_block("02", "전혀 다른 제목")), encoding="utf-8")

            argv = ["inject_presenter.py", str(src), "--notes", str(bad),
                    "--deck-id", "wk-test", "--output", str(out), "--meta", str(meta)]
            with mock.patch.object(sys, "argv", argv):
                self.assertEqual(inject_presenter.main(), 1)
            self.assertFalse(out.exists(), "실패 시 산출물이 만들어지면 안 된다")
            self.assertFalse(meta.exists())
            self.assertEqual(src.read_bytes(), before, "원본이 변경되면 안 된다")

            # 정상 경로 → 산출 후 재실행은 --force 없이 거부된다.
            good = root / "good.html"
            good.write_text(_notes(_note_block("02", "두 번째 장")), encoding="utf-8")
            argv[3] = str(good)
            with mock.patch.object(sys, "argv", argv):
                self.assertEqual(inject_presenter.main(), 0)
            self.assertTrue(out.exists() and meta.exists())
            self.assertEqual(src.read_bytes(), before)
            with mock.patch.object(sys, "argv", argv):
                self.assertEqual(inject_presenter.main(), 1)

    def test_output_path_equal_to_input_aborts(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "deck.html"
            src.write_text(PRESENTER_DECK, encoding="utf-8")
            argv = ["inject_presenter.py", str(src), "--deck-id", "wk",
                    "--output", str(src), "--meta", str(Path(tmp) / "m.json")]
            with mock.patch.object(sys, "argv", argv):
                self.assertEqual(inject_presenter.main(), 1)


class PresenterNotesExemptionTests(unittest.TestCase):
    """주입한 노트 JSON 블록이 학생 화면 검사(아이콘 마커 누출)에 걸리지 않아야 한다."""

    def test_notes_block_is_excluded_from_icon_leak_scan(self):
        html = ('<html><body><script type="application/json" data-presenter-notes>'
                '{"notes":{"S1":[{"kind":"joke","text":"x"}]}}</script>'
                '<p>\U0001F4AC</p></body></html>')
        self.assertNotIn("kind", verify_deck.decoded_text(html))     # script 블록은 통째로 빠진다
        self.assertIn("\U0001F4AC", verify_deck.decoded_text(html))  # 본문의 이모지는 그대로 잡힌다


class VerifyKitExemptTests(unittest.TestCase):
    def test_exempt_is_empty(self):
        # EXEMPT가 조용히 자라면 verify_kit.py의 고아 클래스 게이트가 무의미해진다.
        # 추가할 땐 반드시 이유를 적고(verify_kit.py 주석 참고) 이 테스트를 함께 갱신한다.
        self.assertEqual(verify_kit.EXEMPT, set())


if __name__ == "__main__":
    unittest.main()
