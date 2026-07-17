#!/usr/bin/env python3
"""Decode and verify transparent PNG assets, registry, and session references."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable

try:
    from PIL import Image
except ImportError as exc:  # Pillow is intentionally required only here.
    raise SystemExit("[FAIL] Pillow is required for image asset verification") from exc


VALID_STATUSES = {"approved", "candidate", "rejected", "retired"}


@dataclass
class ImageReport:
    path: str
    ok: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    width: int = 0
    height: int = 0
    alpha_bbox: tuple[int, int, int, int] | None = None
    sha256: str = ""
    fringe_ratio: float = 0.0

    def fail(self, message: str) -> None:
        self.ok = False
        self.errors.append(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def inspect_png(
    path: Path,
    *,
    min_width: int = 320,
    min_height: int = 240,
    max_margin_ratio: float = 0.10,
    max_fringe_ratio: float = 0.005,
) -> ImageReport:
    report = ImageReport(str(path))
    if not path.is_file():
        report.fail("file is missing")
        return report
    try:
        if path.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
            report.fail("file is not a PNG")
            return report
        with Image.open(path) as image:
            image.load()
            report.width, report.height = image.size
            if image.format != "PNG":
                report.fail("decoder format is not PNG")
            if image.mode != "RGBA":
                report.fail(f"actual pixel mode is {image.mode}, expected RGBA")
                return report
            rgba = image.copy()
    except (OSError, ValueError) as exc:
        report.fail(f"PNG decode failed: {exc}")
        return report

    report.sha256 = sha256_file(path)
    if report.width < min_width or report.height < min_height:
        report.fail(f"resolution {report.width}x{report.height} is below {min_width}x{min_height}")
    alpha = rgba.getchannel("A")
    extrema = alpha.getextrema()
    if extrema == (0, 0):
        report.fail("image is fully transparent")
        return report
    if extrema == (255, 255):
        report.fail("image is fully opaque")
        return report
    corners = [alpha.getpixel((0, 0)), alpha.getpixel((report.width - 1, 0)),
               alpha.getpixel((0, report.height - 1)), alpha.getpixel((report.width - 1, report.height - 1))]
    if any(value != 0 for value in corners):
        report.fail(f"transparent corners required, got alpha={corners}")
    bbox = alpha.getbbox()
    report.alpha_bbox = bbox
    if bbox:
        left, top, right, bottom = bbox
        margins = (
            left / report.width,
            top / report.height,
            (report.width - right) / report.width,
            (report.height - bottom) / report.height,
        )
        if any(value > max_margin_ratio + 1e-9 for value in margins):
            report.fail("transparent margin exceeds 10% on at least one side")

    visible = 0
    fringed = 0
    for red, green, blue, a in rgba.get_flattened_data():
        if a == 0:
            continue
        visible += 1
        # Residual chroma from the built-in magenta-key path.
        if red >= 180 and blue >= 180 and min(red, blue) - green >= 40:
            fringed += 1
    report.fringe_ratio = fringed / visible if visible else 0.0
    if report.fringe_ratio > max_fringe_ratio:
        report.fail(
            f"magenta fringe ratio {report.fringe_ratio:.4f} exceeds {max_fringe_ratio:.4f}"
        )
    return report


def _asset_entries(registry: Any) -> list[dict[str, Any]]:
    if isinstance(registry, list):
        return [item for item in registry if isinstance(item, dict)]
    if isinstance(registry, dict):
        for key in ("assets", "entries"):
            value = registry.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    return []


def _asset_id(entry: dict[str, Any]) -> str:
    return str(entry.get("id") or entry.get("asset_id") or "").strip()


def _asset_path(entry: dict[str, Any]) -> str:
    return str(entry.get("file") or entry.get("path") or entry.get("src") or "").strip()


def _lineage_present(entry: dict[str, Any]) -> bool:
    lineage = entry.get("lineage", entry.get("provenance"))
    if isinstance(lineage, str):
        return bool(lineage.strip())
    if isinstance(lineage, dict):
        return bool(lineage)
    if isinstance(lineage, list):
        return bool(lineage)
    return False


def validate_registry_document(data: Any) -> tuple[list[dict[str, Any]], list[str]]:
    """Validate the portable registry contract at runtime without jsonschema."""
    errors: list[str] = []
    if not isinstance(data, dict):
        return [], ["registry root must be an object"]
    if data.get("schema_version") != "1.0":
        errors.append("registry schema_version must be '1.0'")
    root_style = data.get("style_version")
    if not isinstance(root_style, str) or not root_style.strip():
        errors.append("registry style_version must be a nonempty string")
    if not isinstance(data.get("reference_boards"), list):
        errors.append("registry reference_boards must be an array")
    if not isinstance(data.get("assets"), list):
        return [], errors + ["registry assets must be an array"]

    entries = [item for item in data["assets"] if isinstance(item, dict)]
    if len(entries) != len(data["assets"]):
        errors.append("registry assets may contain objects only")
    common_required = {
        "asset_id", "file", "sha256", "style_version", "role", "aspect_ratio",
        "text_safe_side", "lineage", "status", "qa", "notes",
    }
    for offset, entry in enumerate(entries):
        asset_id = _asset_id(entry) or f"entry {offset}"
        missing = sorted(common_required - set(entry))
        if missing:
            errors.append(f"{asset_id}: missing required fields {missing}")
        if not (isinstance(entry.get("metaphor"), str) and entry["metaphor"].strip()) and not (
            isinstance(entry.get("purpose"), str) and entry["purpose"].strip()
        ):
            errors.append(f"{asset_id}: missing purpose or semantic metaphor metadata")
        style = entry.get("style_version")
        if style not in {root_style, "paper-cut-v1"}:
            errors.append(f"{asset_id}: style_version does not match registry style")
        if entry.get("status") not in VALID_STATUSES:
            errors.append(f"{asset_id}: invalid status {entry.get('status')!r}")
        if entry.get("role") not in {"hero", "support", "spot"}:
            errors.append(f"{asset_id}: invalid role")
        if not re.fullmatch(r"[0-9]+:[0-9]+", str(entry.get("aspect_ratio", ""))):
            errors.append(f"{asset_id}: invalid aspect_ratio")
        if entry.get("text_safe_side") not in {"left", "right", "top", "none"}:
            errors.append(f"{asset_id}: invalid text_safe_side")
        if not re.fullmatch(r"[a-f0-9]{64}", str(entry.get("sha256", ""))):
            errors.append(f"{asset_id}: sha256 must be 64 lowercase hex characters")

        lineage = entry.get("lineage")
        if not isinstance(lineage, dict):
            errors.append(f"{asset_id}: lineage must be an object")
        else:
            lineage_missing = {"method", "parent_asset_ids", "source_prompt_id"} - set(lineage)
            if lineage_missing:
                errors.append(f"{asset_id}: lineage missing {sorted(lineage_missing)}")
            if lineage.get("method") not in {"generate", "transform", "import"}:
                errors.append(f"{asset_id}: invalid lineage method")
            if not isinstance(lineage.get("parent_asset_ids"), list):
                errors.append(f"{asset_id}: parent_asset_ids must be an array")

        qa = entry.get("qa")
        if not isinstance(qa, dict):
            errors.append(f"{asset_id}: qa must be an object")
        else:
            qa_missing = {"pixel", "visual", "approved_at"} - set(qa)
            if qa_missing:
                errors.append(f"{asset_id}: qa missing {sorted(qa_missing)}")
            if qa.get("pixel") not in {"pass", "fail", "pending"} or qa.get("visual") not in {
                "pass", "fail", "pending"
            }:
                errors.append(f"{asset_id}: invalid qa status")
            if entry.get("status") == "approved" and (
                qa.get("pixel") != "pass" or qa.get("visual") != "pass" or not qa.get("approved_at")
            ):
                errors.append(f"{asset_id}: approved asset requires passing pixel/visual QA and approved_at")
    return entries, errors


def load_registry(path: Path) -> tuple[dict[str, dict[str, Any]], list[str]]:
    errors: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {}, [f"registry cannot be read: {exc}"]
    entries, contract_errors = validate_registry_document(data)
    errors.extend(contract_errors)
    indexed: dict[str, dict[str, Any]] = {}
    for offset, entry in enumerate(entries):
        asset_id = _asset_id(entry)
        if not asset_id:
            errors.append(f"registry entry {offset} has no asset id")
            continue
        if asset_id in indexed:
            errors.append(f"duplicate asset id: {asset_id}")
            continue
        if not _lineage_present(entry):
            errors.append(f"{asset_id}: missing lineage")
        indexed[asset_id] = entry
    return indexed, errors


def _manifest_refs(value: Any) -> Iterable[tuple[str, str | None]]:
    if isinstance(value, dict):
        asset_id = value.get("asset_id") or value.get("registry_id")
        if isinstance(asset_id, str) and asset_id.strip():
            src = value.get("src") or value.get("file") or value.get("expected_file")
            yield asset_id.strip(), str(src).strip() if src else None
        for nested in value.values():
            yield from _manifest_refs(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _manifest_refs(nested)


def verify_registry(
    registry_path: Path,
    *,
    manifests: Iterable[Path] = (),
    root: Path | None = None,
    min_width: int = 320,
    min_height: int = 240,
) -> tuple[list[ImageReport], list[str]]:
    registry, errors = load_registry(registry_path)
    asset_root = root.resolve() if root else registry_path.resolve().parent
    reports: list[ImageReport] = []
    for asset_id, entry in registry.items():
        if entry.get("status") != "approved":
            continue
        relative = _asset_path(entry)
        if not relative:
            errors.append(f"{asset_id}: approved asset has no file")
            continue
        path = (asset_root / relative).resolve()
        try:
            path.relative_to(asset_root)
        except ValueError:
            errors.append(f"{asset_id}: file escapes registry root")
            continue
        report = inspect_png(path, min_width=min_width, min_height=min_height)
        reports.append(report)
        expected_hash = str(entry.get("sha256") or entry.get("hash") or "").removeprefix("sha256:")
        if not expected_hash:
            errors.append(f"{asset_id}: approved asset has no sha256")
        elif report.sha256 and report.sha256.lower() != expected_hash.lower():
            errors.append(f"{asset_id}: sha256 mismatch")

    for manifest_path in manifests:
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"manifest {manifest_path}: cannot be read: {exc}")
            continue
        for asset_id, src in _manifest_refs(manifest):
            entry = registry.get(asset_id)
            if entry is None:
                errors.append(f"manifest {manifest_path}: unknown asset id {asset_id}")
                continue
            if entry.get("status") in {"rejected", "retired"}:
                errors.append(f"manifest {manifest_path}: references {entry.get('status')} asset {asset_id}")
            registered = _asset_path(entry)
            if src and registered and Path(src).as_posix().endswith(Path(registered).as_posix()) is False:
                errors.append(f"manifest {manifest_path}: {asset_id} path does not match registry")
    return reports, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("images", nargs="*", type=Path)
    parser.add_argument("--registry", type=Path)
    parser.add_argument("--manifest", type=Path, action="append", default=[])
    parser.add_argument("--root", type=Path)
    parser.add_argument("--min-width", type=int, default=320)
    parser.add_argument("--min-height", type=int, default=240)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    reports = [inspect_png(path, min_width=args.min_width, min_height=args.min_height) for path in args.images]
    errors: list[str] = []
    if args.registry:
        registry_reports, registry_errors = verify_registry(
            args.registry,
            manifests=args.manifest,
            root=args.root,
            min_width=args.min_width,
            min_height=args.min_height,
        )
        reports.extend(registry_reports)
        errors.extend(registry_errors)
    if args.json:
        print(json.dumps({"images": [asdict(report) for report in reports], "errors": errors}, ensure_ascii=False, indent=2))
    else:
        for report in reports:
            if report.ok:
                print(f"[PASS] {report.path} | {report.width}x{report.height} | fringe={report.fringe_ratio:.4f}")
            else:
                for error in report.errors:
                    print(f"[FAIL] {report.path}: {error}")
        for error in errors:
            print(f"[FAIL] {error}")
    return 1 if errors or any(not report.ok for report in reports) else 0


if __name__ == "__main__":
    sys.exit(main())
