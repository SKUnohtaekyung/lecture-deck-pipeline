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
from scripts.run_deck_checks import RENDER_DEFECT_KEYS
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


_MAP_DECK_A = (
    "<html><body>"
    '<section class="slide cover" data-slide="COVER"><h2 class="s-title">표지 제목</h2></section>'
    '<section class="slide" data-slide="X1"><h2 class="s-title">첫 본문</h2></section>'
    '<section class="slide" data-slide="X2"><h2 class="s-title">둘째 본문</h2></section>'
    "</body></html>"
)
# 재구성 후: 새 슬라이드가 X1 앞에 끼어 쪽번호가 밀린다
_MAP_DECK_B = (
    "<html><body>"
    '<section class="slide cover" data-slide="COVER"><h2 class="s-title">표지 제목</h2></section>'
    '<section class="slide" data-slide="NEW"><h2 class="s-title">끼어든 장</h2></section>'
    '<section class="slide" data-slide="X1"><h2 class="s-title">첫 본문</h2></section>'
    '<section class="slide" data-slide="X2"><h2 class="s-title">둘째 본문</h2></section>'
    "</body></html>"
)


class MapSlidePagesTests(unittest.TestCase):
    """P3(배치3 · 2026-08-17): 쪽↔ID 매핑 왕복 — 재구성으로 쪽이 밀려도 ID는 안정 좌표다."""

    def _mapping(self, html):
        from scripts.map_slide_pages import build_mapping
        with tempfile.NamedTemporaryFile("w", suffix=".html", encoding="utf-8", delete=False) as f:
            f.write(html)
            path = f.name
        try:
            return build_mapping(path)
        finally:
            Path(path).unlink(missing_ok=True)

    def test_roundtrip_pages_shift_but_ids_stay(self):
        rows_a, sha_a, n_a = self._mapping(_MAP_DECK_A)
        rows_b, sha_b, n_b = self._mapping(_MAP_DECK_B)
        self.assertEqual((n_a, n_b), (3, 4))
        page_a = {sid: page for page, sid, _t, _s in rows_a}
        page_b = {sid: page for page, sid, _t, _s in rows_b}
        # 쪽번호는 밀렸다(재구성마다 깨지는 좌표) — X1: 2쪽 → 3쪽
        self.assertEqual(page_a["X1"], 2)
        self.assertEqual(page_b["X1"], 3)
        # ID는 그대로다(안정 좌표) — 스냅샷을 남기면 옛 쪽번호도 번역 가능하다
        self.assertLessEqual(set(page_a) - {"NEW"}, set(page_b))
        # 덱이 바뀌면 sha가 갈려 스냅샷 파일명이 충돌하지 않는다
        self.assertNotEqual(sha_a, sha_b)

    def test_pageno_definition_matches_deck_js(self):
        """쪽번호 = 전체 배열 인덱스+1 (표시 제외 클래스도 자리는 차지 — MEMORY 규칙)."""
        rows, _sha, _n = self._mapping(_MAP_DECK_A)
        pages = [page for page, _sid, _t, _s in rows]
        self.assertEqual(pages, [1, 2, 3])
        cover = rows[0]
        self.assertEqual(cover[1], "COVER")
        self.assertFalse(cover[3], "cover는 «표시 없음»으로 주석돼야 한다")
        self.assertTrue(rows[1][3])

    def test_title_extraction(self):
        rows, _sha, _n = self._mapping(_MAP_DECK_A)
        self.assertEqual(rows[1][2], "첫 본문")


class RenderNumericVerdictTests(unittest.TestCase):
    """P4(배치3 · 2026-08-17): 렌더 수치 판정 — 고의 위반이 실제로 FAIL하는지 증명.

    임계값 없는 결함형 6종(waiver 베이스라인 초과만 FAIL)과 렌더 WARN 계수의 계약을 고정한다.
    """

    TYPO_OK = {"fontFloor": {"count": 0}, "tracking": {"count": 0},
               "nearMissAnchors": {"dominantClashTotal": 0}}
    # ⚠️ 키를 손으로 나열하지 않는다 — 검출기가 늘 때마다 이 픽스처가 낡아
    # 「전부 0이면 통과」가 실패한다(2026-08-18에 실제로 겪었다: 신설 6종이 빠져
    # 계수 실패로 잡혔다). 누락 키의 fail-closed는 아래
    # `test_missing_total_is_counting_failure_not_zero`가 키 하나를 지워 따로 지킨다.
    ZEROS = {k: 0 for k, _label in RENDER_DEFECT_KEYS}

    def _verdict(self, totals, typo=None, kv=None):
        from scripts.run_deck_checks import numeric_verdicts
        # ⚠️ `typo or …`로 쓰면 빈 dict(계수 실패 픽스처)가 기본값으로 치환된다 — None 판별로.
        return numeric_verdicts(totals, self.TYPO_OK if typo is None else typo, kv or {})

    def test_all_zero_passes_with_zero_warn(self):
        steps, warn, waivers = self._verdict(dict(self.ZEROS))
        self.assertTrue(all(ok for _n, ok, _m in steps))
        self.assertEqual(warn, 0)
        self.assertEqual(waivers, [])

    def test_defect_over_baseline_fails(self):
        steps, _warn, _w = self._verdict(dict(self.ZEROS, lap=2))
        lap = [s for s in steps if s[0] == "렌더 결함 정보요소겹침"]
        self.assertTrue(lap and lap[0][1] is False, "waiver 없는 겹침 2건은 FAIL이어야 한다")

    def test_valid_waiver_demotes_and_counts_as_warn(self):
        kv = {"render_lap": {"count": 2, "reason": "선재 결함 등재", "date": "2026-08-17"}}
        steps, warn, waivers = self._verdict(dict(self.ZEROS, lap=2), kv=kv)
        lap = [s for s in steps if s[0] == "렌더 결함 정보요소겹침"]
        self.assertTrue(lap and lap[0][1] is True)
        self.assertEqual(warn, 1, "강등은 침묵이 아니라 렌더 WARN 1로 세어져야 한다")
        self.assertTrue(any("render_lap" in w for w in waivers))

    def test_waiver_over_baseline_still_fails(self):
        kv = {"render_lap": {"count": 2, "reason": "선재 결함 등재", "date": "2026-08-17"}}
        steps, _warn, _w = self._verdict(dict(self.ZEROS, lap=3), kv=kv)
        lap = [s for s in steps if s[0] == "렌더 결함 정보요소겹침"]
        self.assertTrue(lap and lap[0][1] is False, "waiver count 초과(증가)는 FAIL이어야 한다")

    def test_reasonless_waiver_does_not_work(self):
        kv = {"render_lap": {"count": 2}}
        steps, _warn, _w = self._verdict(dict(self.ZEROS, lap=2), kv=kv)
        lap = [s for s in steps if s[0] == "렌더 결함 정보요소겹침"]
        self.assertTrue(lap and lap[0][1] is False, "무사유 waiver는 작동하지 않아야 한다(P1 규약)")

    def test_missing_total_is_counting_failure_not_zero(self):
        totals = dict(self.ZEROS)
        del totals["wb"]
        steps, _warn, _w = self._verdict(totals)
        wb = [s for s in steps if s[0] == "렌더 결함 어절중간잘림"]
        self.assertTrue(wb and wb[0][1] is False, "수치 누락은 0이 아니라 계수 실패다(눈먼 0 방지)")

    def test_missing_typo_metrics_fails_ratchet_input(self):
        steps, warn, _w = self._verdict(dict(self.ZEROS), typo={})
        self.assertIsNone(warn, "타이포 수치가 없으면 렌더 WARN은 None(계수 실패)이어야 한다")
        count = [s for s in steps if s[0] == "렌더 WARN 계수"]
        self.assertTrue(count and count[0][1] is False)

    def test_warn_sum_includes_typo_and_demotions(self):
        typo = {"fontFloor": {"count": 3}, "tracking": {"count": 2},
                "nearMissAnchors": {"dominantClashTotal": 1}}
        kv = {"render_below": {"count": 1, "reason": "등재", "date": "2026-08-17"}}
        _steps, warn, _w = self._verdict(dict(self.ZEROS, below=1), typo=typo, kv=kv)
        self.assertEqual(warn, 3 + 2 + 1 + 1)


class RenderAuditFailClosedTests(unittest.TestCase):
    """감사기의 fail-closed assert가 «안 그려진 화면»을 통과시키지 않는지 고정한다.

    2026-08-18 반복측정으로 규명된 결함: `audit_render.js`가 **폰트는** 막으면서
    **이미지는** 막지 않았다. 이미지가 아직 로드되지 않은 상태로 재면 상자가
    찌그러져 결함이 **실제보다 적게** 나온다 — 1주차 실측 `below` 25→23,
    `ovf` 1→0. 틀리는 방향이 「덱이 더 멀쩡해 보이는」 쪽이라 그 수치가 래칫을
    조용히 통과한다(지도 §8.1·§8.2가 기록한 이 저장소의 반복 실패 형태).

    ⚠️ 여기서 검증하는 것은 **선언의 존재**다. 실제 발화는 브라우저에서만
    재현되며 2026-08-18에 실측 확인했다(이미지 38/39 미로드 → INVALID 반환,
    로딩 완료 후 재측정은 정상 측정치와 완전 동일). 헤드리스는 DEC-03으로
    도입하지 않으므로 여기서는 가드가 지워지는 것을 막는 데 집중한다.
    """

    AUDIT_RENDER = Path(__file__).resolve().parent.parent / "scripts" / "audit_render.js"
    AUDIT_ALL = Path(__file__).resolve().parent.parent / "scripts" / "audit_all.js"

    def test_image_readiness_is_asserted_before_measuring(self):
        src = self.AUDIT_RENDER.read_text(encoding="utf-8")
        self.assertIn("document.images", src,
                      "이미지 로드 상태를 보지 않는다 — 미로드 화면을 «결함 없음»으로 통과시킨다")
        self.assertIn("naturalWidth === 0", src,
                      "complete만 보면 «로드는 끝났는데 깨진» 이미지를 놓친다")
        # 검사가 assert 블록 안(=INVALID로 이어지는 자리)에 있어야 의미가 있다
        head = src.split("if (_invalid.length) return", 1)[0]
        self.assertIn("document.images", head,
                      "이미지 검사가 fail-closed assert 블록 밖에 있다 — 측정을 막지 못한다")

    def test_font_assert_still_present(self):
        """이미지 가드를 넣다가 기존 폰트 가드를 밀어내지 않았는지."""
        src = self.AUDIT_RENDER.read_text(encoding="utf-8")
        self.assertIn("fonts.check('16px Pretendard')", src)

    def test_evidence_records_measurement_environment(self):
        """증거에 환경이 없으면 «덱이 바뀐 것»과 «환경이 바뀐 것»을 구분할 수 없다.

        2026-08-17 측정과 2026-08-18 재측정의 `ovf`가 2→1로 달랐는데 원인을
        규명할 수 없었던 이유가 정확히 이것이다.
        """
        src = self.AUDIT_ALL.read_text(encoding="utf-8")
        for key in ("devicePixelRatio", "innerWidth", "userAgent"):
            self.assertIn(key, src, f"증거에 {key}가 기록되지 않는다")

    def test_stored_evidence_carries_env_block(self):
        root = Path(__file__).resolve().parent.parent
        for week in ("1주차", "2주차", "3주차"):
            f = root / "sessions" / "_verify" / week / "deck-audit.json"
            if not f.exists():
                continue
            env = json.loads(f.read_text(encoding="utf-8")).get("env")
            self.assertIsNotNone(env, f"{week} 증거에 env 블록이 없다 — 재측정하라")
            for key in ("dpr", "viewport", "ua", "images"):
                self.assertIn(key, env, f"{week} env에 {key}가 없다")


class ReportFreshnessTests(unittest.TestCase):
    """P5(배치4 · 2026-08-17): 보고 신선도 — 고의 낡음이 실제로 잡히는지 먼저 증명."""

    def test_check_report_verdicts(self):
        from scripts.verify_report_freshness import check_report
        self.assertEqual(check_report("- 기준 덱: `x` · **81장** · sha256 `deadbeef`", 81, "deadbeef")[0], "ok")
        self.assertEqual(check_report("- 기준 덱: `x` · **77장** · sha256 `deadbeef`", 81, "deadbeef")[0], "stale")
        self.assertEqual(check_report("- 기준 덱: `x` · **81장** · sha256 `00000000`", 81, "deadbeef")[0], "stale")
        self.assertEqual(check_report("# 조립 보고\n식별자 없음", 81, "deadbeef")[0], "missing")
        self.assertEqual(check_report("# 보고\n[시점 스냅샷 2026-08-17]", 81, "deadbeef")[0], "ok")

    def test_strict_exits_1_on_stale_and_0_on_snapshot_declaration(self):
        import subprocess
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "강의덱.html").write_text(
                '<section class="slide" data-slide="A">x</section>', encoding="utf-8")
            rpt = Path(tmp) / "조립_보고.md"
            rpt.write_text("# 보고 — 식별자 없음(고의 위반)", encoding="utf-8")
            repo_root = Path(__file__).resolve().parent.parent
            cmd = [sys.executable, str(repo_root / "scripts" / "verify_report_freshness.py"),
                   "--session", tmp, "--strict"]
            proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
            self.assertEqual(proc.returncode, 1, proc.stdout)
            rpt.write_text("# 보고\n[시점 스냅샷 2026-08-17]\n", encoding="utf-8")
            proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
            self.assertEqual(proc.returncode, 0, proc.stdout)


class QualityRatchetTests(unittest.TestCase):
    """배치4(2026-08-17): 품질 WARN 래칫 — 고의 증가가 FAIL하는지 증명.

    규칙 임계(프로필 §3-G)는 불변이고, 래칫은 «총계의 조용한 증가»만 막는다(D-2).
    """

    def _report(self, quality, contract):
        import contextlib
        import io as _io
        from scripts.run_deck_checks import Runner
        r = Runner("2주차")
        r.steps = []
        r.warn_struct = 0
        r.warn_quality = quality
        r._contract = lambda: contract
        buf = _io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = r.report(ran_static=True, ran_render=False)
        return code, buf.getvalue()

    def test_increase_over_baseline_fails(self):
        code, out = self._report(1, {"warn_baseline": {"static_gates": 0, "quality": 0, "date": "2026-08-17"}})
        self.assertEqual(code, 1)
        self.assertIn("품질 WARN 증가", out)

    def test_within_baseline_passes(self):
        # 부분 실행(렌더 생략)이라 exit 3(불완전)이 정상 — FAIL(1)이 아니면 래칫 통과다.
        code, out = self._report(0, {"warn_baseline": {"static_gates": 0, "quality": 0, "date": "2026-08-17"}})
        self.assertEqual(code, 3)
        self.assertIn("품질 WARN 래칫", out)

    def test_missing_baseline_fails_with_guidance(self):
        code, out = self._report(0, {"warn_baseline": {"static_gates": 0, "date": "2026-08-17"}})
        self.assertEqual(code, 1)
        self.assertIn("warn_baseline.quality 미등재", out)

    # ── 2026-08-24 (plans/gate-input-hardening P1) — 눈먼 0 방지 ────────────
    def test_count_failure_is_not_reported_as_improvement(self):
        """검사기가 죽어 WARN을 세지 못한 0은 «개선»이 아니다.

        실측(2026-08-24): 과목이 2개가 되어 `verify_deck_quality`가 예외로 죽자
        warn_quality가 0으로 남았고, 래칫이 「품질 WARN 0 ≤ 베이스라인 5 — 개선됨:
        베이스라인을 0으로 낮춰 등재 가능」을 냈다. **크래시가 베이스라인을 낮추라는
        권고를 만든 것이다.** struct 버킷에는 있던 None 경로가 quality에만 없었다."""
        code, out = self._report(None, {"warn_baseline": {"static_gates": 0, "quality": 5,
                                                          "date": "2026-08-17"}})
        self.assertEqual(code, 1, out)
        self.assertIn("품질 WARN 계수 실패", out)
        self.assertNotIn("개선됨", out)
        self.assertIn("계수실패", out)          # 최상단 요약 줄에도 노출

    def test_summary_line_absence_marks_quality_count_failed(self):
        """«요약:» 줄을 못 찾으면 quality 버킷도 None으로 표시된다(struct와 대칭)."""
        from scripts.run_deck_checks import Runner
        r = Runner("2주차")
        r.steps = []
        r._last_out = "여기에는 요약 줄이 없다"
        r._count_summary_warns("내용 품질", "quality")
        self.assertIsNone(r.warn_quality)


class BlindSlideCountTests(unittest.TestCase):
    """덱에서 슬라이드를 «0장» 셌을 때 장수 대조가 통째로 건너뛰어지던 문제.

    종전 조건이 `if deck_slides and n_slides`라 `deck_slides == 0`이 falsy로 걸러졌다.
    「0장을 셌다」와 「덱이 없다」는 다른 사건이고, 전자는 검사가 눈이 먼 상태다.
    (plans/gate-input-hardening P1 · 2026-08-24)
    """

    def _runner_with_deck(self, html, evidence):
        import json
        import os
        import tempfile
        from scripts.run_deck_checks import Runner
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        deck = os.path.join(td.name, "강의덱.html")
        with open(deck, "w", encoding="utf-8") as fh:
            fh.write(html)
        vdir = os.path.join(td.name, "_verify")
        os.makedirs(vdir, exist_ok=True)
        with open(os.path.join(vdir, "deck-audit.json"), "w", encoding="utf-8") as fh:
            json.dump(evidence, fh)
        r = Runner("2주차")
        r.steps = []
        r.deck = deck
        r.verify_dir = vdir
        return r

    def _evidence(self, slide_count):
        return {"schema": "deck-audit/1", "slideCount": slide_count,
                "render": {"totals": {}}, "typography": {}}

    _MSG = "슬라이드를 한 장도 세지 못했다"

    def test_zero_slides_counted_is_a_failure_not_a_skip(self):
        r = self._runner_with_deck("<html><body>슬라이드 마크업이 없다</body></html>",
                                   self._evidence(80))
        ok = r.render_evidence()
        self.assertFalse(ok)
        self.assertTrue(any(self._MSG in (s[2] or "") for s in r.steps), r.steps)

    def test_matching_slide_count_still_proceeds(self):
        """오탐 방지 — 정상 덱은 **이 가드에** 걸리지 않는다.

        (증거 스텁이 최소라 다른 «눈먼 0» 가드는 정상적으로 발화한다. 그것은
        이 테스트의 대상이 아니므로 단언을 이 가드의 메시지로 좁힌다.)"""
        html = "".join('<section class="slide">x</section>' for _ in range(3))
        r = self._runner_with_deck(html, self._evidence(3))
        r.render_evidence()
        self.assertFalse(any(self._MSG in (s[2] or "") for s in r.steps), r.steps)


if __name__ == "__main__":
    unittest.main()
