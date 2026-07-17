#!/usr/bin/env python3
"""Fast, dependency-free regression checks for the public image contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    raise AssertionError(message)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def fenced_block_after(text: str, heading: str) -> str:
    start = text.find(heading)
    if start < 0:
        fail(f"missing heading: {heading}")
    fence = text.find("```text", start)
    if fence < 0:
        fail(f"missing text block after: {heading}")
    end = text.find("```", fence + len("```text"))
    if end < 0:
        fail(f"unclosed text block after: {heading}")
    return text[fence + len("```text") : end].lower()


def verify_prompt_layers() -> None:
    path = ROOT / "references" / "이미지-디렉션-프롬프트.md"
    text = path.read_text(encoding="utf-8")
    chroma = fenced_block_after(text, "### 5.1 built-in 크로마 원본")
    native = fenced_block_after(text, "### 5.2 승인된 native-alpha 경로")

    if "magenta" not in chroma or "#ff00ff" not in chroma:
        fail("chroma block must require one uniform magenta background")
    for forbidden in ("genuine alpha", "transparent png", "no backdrop"):
        if forbidden in chroma:
            fail(f"chroma block contains native-alpha phrase: {forbidden}")

    if "genuine alpha" not in native or "transparency" not in native:
        fail("native-alpha block must require genuine transparency")
    for forbidden in ("magenta", "chroma", "#ff00ff"):
        if forbidden in native:
            fail(f"native-alpha block contains chroma phrase: {forbidden}")

    for marker in (
        "LEARNING_POINT:",
        "SOURCE_METAPHOR:",
        "METAPHOR_MAPPING:",
        "MUST_SHOW:",
        "MUST_NOT_IMPLY:",
        "ALT_TEXT:",
    ):
        if marker not in text:
            fail(f"semantic brief marker missing: {marker}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_registry() -> None:
    registry_path = ROOT / "kit" / "images" / "paper-cut-v1" / "registry.json"
    registry = read_json(registry_path)
    if registry.get("style_version") != "paper-cut-v1":
        fail("registry style_version must be paper-cut-v1")

    asset_ids = [item.get("asset_id") for item in registry.get("assets", [])]
    if len(asset_ids) != len(set(asset_ids)):
        fail("duplicate Asset ID")

    for board in registry.get("reference_boards", []):
        path = registry_path.parent / board["file"]
        if not path.is_file():
            fail(f"missing reference board: {path}")
        if sha256(path) != board["sha256"]:
            fail(f"reference board hash mismatch: {board['id']}")
        if board["status"] != "approved" and board["generation_reference_allowed"]:
            fail(f"unapproved board permits generation reference: {board['id']}")
        if board["generation_reference_allowed"] and not board.get("paper_preview"):
            fail(f"approved generation board lacks paper preview: {board['id']}")

    for asset in registry.get("assets", []):
        path = registry_path.parent / asset["file"]
        if not path.is_file():
            fail(f"missing registered asset: {asset['asset_id']}")
        if sha256(path) != asset["sha256"]:
            fail(f"asset hash mismatch: {asset['asset_id']}")
        if asset["status"] == "approved":
            if asset["qa"]["pixel"] != "pass" or asset["qa"]["visual"] != "pass":
                fail(f"approved asset lacks passing QA: {asset['asset_id']}")
            lineage = asset.get("lineage", {})
            if "method" not in lineage or "parent_asset_ids" not in lineage:
                fail(f"approved asset lacks lineage: {asset['asset_id']}")


def verify_manifest_template() -> None:
    manifest = read_json(ROOT / "sessions" / "_template" / "자료" / "이미지-에셋.json")
    if manifest.get("schema_version") != "1.0":
        fail("manifest template schema_version must be 1.0")
    if manifest.get("image_mode") != "pending":
        fail("new session manifest must begin pending")
    if manifest.get("slides") != []:
        fail("new session manifest must begin with no slide decisions")


def main() -> int:
    verify_prompt_layers()
    verify_registry()
    verify_manifest_template()
    print("PASS image contract: prompt layers, registry, manifest template")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
