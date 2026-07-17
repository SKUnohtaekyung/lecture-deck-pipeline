from __future__ import annotations

import json
import hashlib
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from scripts.inline_deck import bundle
from scripts.prepare_image_asset import (
    AssetPreparationError,
    remove_border_chroma,
    validate_chroma_source,
)
from scripts import verify_deck
from scripts.verify_deck import image_contract_checks
from scripts.verify_image_assets import inspect_png, load_registry, verify_registry


MAGENTA = (255, 0, 255)


class ChromaPreparationTests(unittest.TestCase):
    def test_partial_alpha_rgb_is_restored_from_opaque_interior(self):
        colors = [(244, 248, 251), (29, 78, 216), (20, 184, 166), (249, 115, 96)]
        for color in colors:
            image = Image.new("RGB", (120, 100), MAGENTA)
            y = 50
            for offset, coverage in enumerate((0.25, 0.50, 0.75)):
                image.putpixel(
                    (20 + offset, y),
                    tuple(round(MAGENTA[c] * (1 - coverage) + color[c] * coverage) for c in range(3)),
                )
            for x in range(23, 85):
                image.putpixel((x, y), color)
            opaque_distance = max(abs(color[c] - MAGENTA[c]) for c in range(3))
            result = remove_border_chroma(
                image,
                transparent_tolerance=2,
                opaque_tolerance=opaque_distance,
            )
            for x in (20, 21, 22):
                pixel = result.getpixel((x, y))
                self.assertGreater(pixel[3], 0)
                self.assertLess(pixel[3], 255)
                self.assertEqual(pixel[:3], color)

    def test_preflight_rejects_nonuniform_border_and_key_collision(self):
        nonuniform = Image.new("RGB", (80, 80), MAGENTA)
        for x in range(20):
            nonuniform.putpixel((x, 0), (255, 80, 255))
        with self.assertRaises(AssetPreparationError):
            validate_chroma_source(nonuniform)

        collision = Image.new("RGB", (80, 80), MAGENTA)
        for y in range(20, 60):
            for x in range(20, 60):
                collision.putpixel((x, y), (244, 248, 251))
        collision.putpixel((40, 40), MAGENTA)
        with self.assertRaisesRegex(AssetPreparationError, "chroma-key"):
            validate_chroma_source(collision)


class AssetVerifierTests(unittest.TestCase):
    def test_rgba_alpha_and_registry_failures_are_detected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            valid = Image.new("RGBA", (400, 300), (0, 0, 0, 0))
            for y in range(20, 280):
                for x in range(20, 380):
                    valid.putpixel((x, y), (29, 78, 216, 255))
            valid_path = root / "valid.png"
            valid.save(valid_path)
            self.assertTrue(inspect_png(valid_path).ok)

            opaque_path = root / "opaque.png"
            Image.new("RGBA", (400, 300), (29, 78, 216, 255)).save(opaque_path)
            report = inspect_png(opaque_path)
            self.assertFalse(report.ok)
            self.assertIn("fully opaque", " ".join(report.errors))

            transparent_path = root / "transparent.png"
            Image.new("RGBA", (400, 300), (0, 0, 0, 0)).save(transparent_path)
            self.assertIn("fully transparent", " ".join(inspect_png(transparent_path).errors))

            low_res_path = root / "low-res.png"
            low_res = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
            low_res.putpixel((32, 32), (29, 78, 216, 255))
            low_res.save(low_res_path)
            self.assertIn("below", " ".join(inspect_png(low_res_path).errors))

            missing_report = inspect_png(root / "missing.png")
            self.assertIn("missing", " ".join(missing_report.errors))
            corrupt_path = root / "corrupt.png"
            corrupt_path.write_bytes(b"not-a-png")
            self.assertIn("not a PNG", " ".join(inspect_png(corrupt_path).errors))

            rgb_path = root / "rgb.png"
            Image.new("RGB", (400, 300), (29, 78, 216)).save(rgb_path)
            self.assertIn("expected RGBA", " ".join(inspect_png(rgb_path).errors))

            registry_path = root / "registry.json"
            registry_path.write_text(
                json.dumps(
                    {
                        "assets": [
                            {"id": "same", "status": "approved", "style_version": "paper-cut-v1"},
                            {"id": "same", "status": "approved", "style_version": "paper-cut-v1"},
                        ]
                    }
                ),
                encoding="utf-8",
            )
            _entries, errors = load_registry(registry_path)
            self.assertTrue(any("duplicate asset id" in error for error in errors))
            self.assertTrue(any("missing lineage" in error for error in errors))

    def test_registry_runtime_contract_hash_and_retired_reference(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            image = Image.new("RGBA", (400, 300), (0, 0, 0, 0))
            for y in range(20, 280):
                for x in range(20, 380):
                    image.putpixel((x, y), (29, 78, 216, 255))
            image.save(root / "asset.png")
            digest = hashlib.sha256((root / "asset.png").read_bytes()).hexdigest()
            base_asset = {
                "file": "asset.png",
                "sha256": digest,
                "style_version": "paper-cut-v1",
                "metaphor": "입력에서 출력으로 이동하는 경로",
                "role": "hero",
                "aspect_ratio": "4:3",
                "text_safe_side": "left",
                "lineage": {"method": "generate", "parent_asset_ids": [], "source_prompt_id": "P-001"},
                "qa": {"pixel": "pass", "visual": "pass", "approved_at": "2026-07-17T00:00:00Z"},
                "notes": "fixture",
            }
            approved = dict(base_asset, asset_id="ASSET-001", status="approved", sha256="0" * 64)
            retired = dict(base_asset, asset_id="ASSET-002", status="retired")
            rejected = dict(base_asset, asset_id="ASSET-003", status="rejected")
            registry_path = root / "registry.json"
            registry_path.write_text(
                json.dumps(
                    {
                        "schema_version": "1.0",
                        "style_version": "paper-cut-v1",
                        "reference_boards": [],
                        "assets": [approved, retired, rejected],
                    }
                ),
                encoding="utf-8",
            )
            manifest_path = root / "manifest.json"
            manifest_path.write_text(
                json.dumps({"slides": [{"asset_id": "ASSET-002"}, {"asset_id": "ASSET-003"}]}),
                encoding="utf-8",
            )
            _reports, errors = verify_registry(registry_path, manifests=[manifest_path])
            self.assertTrue(any("sha256 mismatch" in error for error in errors))
            self.assertTrue(any("retired asset" in error for error in errors))
            self.assertTrue(any("rejected asset" in error for error in errors))

            malformed_path = root / "malformed-registry.json"
            malformed_path.write_text(
                json.dumps({"schema_version": "2.0", "style_version": "", "assets": [
                    {"asset_id": "ASSET-003", "status": "approved", "file": "asset.png"}
                ]}),
                encoding="utf-8",
            )
            _entries, malformed_errors = load_registry(malformed_path)
            self.assertTrue(any("schema_version" in error for error in malformed_errors))
            self.assertTrue(any("missing" in error or "style_version" in error for error in malformed_errors))


class DeckAndBundleTests(unittest.TestCase):
    def test_prompt_only_is_safe_in_development_and_blocked_in_release(self):
        html = """
        <section class="slide">
          <figure class="asset-slot asset-slot--hero" data-image-purpose="explanatory"
            data-image-state="expected" data-expected-src="자료/images/map.png"></figure>
        </section>
        """
        errors, notes = image_contract_checks(html, "deck.html", release=False)
        self.assertEqual(errors, [])
        self.assertTrue(notes)
        release_errors, _ = image_contract_checks(html, "deck.html", release=True)
        self.assertTrue(any("unresolved required" in error for error in release_errors))
        self.assertNotIn("<img", html)

    def test_invalid_manifest_and_ready_slot_contracts_fail(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest_path = root / "manifest.json"
            manifest_path.write_text("{}", encoding="utf-8")
            html = """
            <section class="slide s02-slide">
              <figure class="asset-slot asset-slot--hero" data-image-purpose="explanatory"
                data-image-state="ready"><img alt="입력과 출력의 관계"></figure>
            </section>
            <section class="slide"><img src="data:image/png;base64,AA==" alt="screenshot"></section>
            """
            errors, _ = image_contract_checks(html, root / "deck.html", manifest_path=manifest_path)
            self.assertTrue(any("manifest" in error for error in errors))
            self.assertTrue(any("nonempty src" in error for error in errors))
            self.assertTrue(any("has-image" in error for error in errors))
            self.assertTrue(any("outside asset-slot" in error for error in errors))

    def test_single_quoted_s02_cannot_bypass_has_image_contract(self):
        html = """
        <section class='slide s02-slide'>
          <figure class='asset-slot asset-slot--hero' data-image-purpose='explanatory'
            data-image-state='ready'><img src='data:image/png;base64,AA==' alt='입력과 출력의 관계'></figure>
        </section>
        """
        errors, _ = image_contract_checks(html, "deck.html")
        self.assertTrue(any("has-image" in error for error in errors))

    def test_single_quoted_section_cannot_bypass_bare_content_img_contract(self):
        html = """
        <section class='slide content-slide'>
          <img src='data:image/png;base64,AA==' alt='주석 스크린샷'>
        </section>
        """
        errors, _ = image_contract_checks(html, "deck.html")
        self.assertTrue(any("outside asset-slot" in error for error in errors))

    def test_release_blocks_expected_decorative_and_viz_is_counted_once(self):
        html = """
        <section class="slide">
          <div class="viz-flow" data-viz="flow"></div>
          <figure class="asset-slot asset-slot--spot" data-image-purpose="decorative"
            data-image-state="expected" data-expected-src="optional.png"></figure>
        </section>
        """
        errors, _ = image_contract_checks(html, "deck.html", release=True)
        self.assertTrue(any("unresolved" in error for error in errors))
        self.assertEqual(getattr(verify_deck, "count_code_viz")(html), 1)

    def test_decorative_consecutive_and_viz_collision_fail(self):
        slot = (
            '<figure class="asset-slot asset-slot--spot" data-image-purpose="decorative">'
            '<img src="data:image/png;base64,AA==" alt="" aria-hidden="true"></figure>'
        )
        html = (
            '<section class="slide"><div class="viz-flow" data-viz="flow"></div>' + slot + '</section>'
            '<section class="slide">' + slot + '</section>'
        )
        errors, _ = image_contract_checks(html, "deck.html")
        self.assertTrue(any("shares slide" in error for error in errors))
        self.assertTrue(any("consecutive" in error for error in errors))

    def test_inline_handles_picture_srcset_and_css_url(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / ".git").mkdir()
            image = Image.new("RGBA", (20, 20), (0, 0, 0, 0))
            image.putpixel((10, 10), (29, 78, 216, 255))
            image.save(root / "asset.png")
            (root / "deck.css").write_text(".hero{background:url('asset.png')}", encoding="utf-8")
            deck = root / "deck.html"
            deck.write_text(
                """<html><head>
                <link rel="stylesheet" href="deck.css">
                </head><body><picture><source srcset="asset.png 1x, asset.png 2x">
                <img src="asset.png" alt="관계를 설명"></picture>
                <figure class="asset-slot asset-slot--hero" data-image-purpose="explanatory">
                <img src="asset.png" alt="입력에서 출력으로 이어지는 관계"></figure>
                </body></html>""",
                encoding="utf-8",
            )
            output = root / "out.html"
            ok, errors, _ = bundle(deck, output=output, offline=True, root=root)
            self.assertTrue(ok, errors)
            rendered = output.read_text(encoding="utf-8")
            self.assertNotIn("src=\"asset.png", rendered)
            self.assertNotIn("srcset=", rendered)
            self.assertGreaterEqual(rendered.count("data:image/png;base64,"), 3)

    def test_inline_refuses_remote_stylesheet_without_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            deck = root / "deck.html"
            deck.write_text(
                '<link rel="preconnect" href="https://fonts.example">'
                '<link rel="stylesheet" href="https://fonts.example/font.css">',
                encoding="utf-8",
            )
            output = root / "out.html"
            ok, errors, _ = bundle(deck, output=output, offline=True, root=root)
            self.assertFalse(ok)
            self.assertFalse(output.exists())
            self.assertGreaterEqual(sum("offline external dependency" in error for error in errors), 2)

    def test_inline_removes_stale_output_on_failure(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            deck = root / "deck.html"
            deck.write_text('<script src="https://cdn.example/app.js"></script>', encoding="utf-8")
            output = root / "out.html"
            output.write_text("stale", encoding="utf-8")
            ok, errors, _ = bundle(deck, output=output, offline=True, root=root)
            self.assertFalse(ok)
            self.assertTrue(errors)
            self.assertFalse(output.exists())

    def test_inline_refuses_unresolved_required_slot_without_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            deck = root / "deck.html"
            deck.write_text(
                '<figure class="asset-slot asset-slot--hero" data-image-purpose="mnemonic" '
                'data-image-state="expected" data-expected-src="missing.png"></figure>',
                encoding="utf-8",
            )
            output = root / "out.html"
            ok, errors, _ = bundle(deck, output=output, offline=True, root=root)
            self.assertFalse(ok)
            self.assertFalse(output.exists())
            self.assertTrue(any("unresolved required" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
