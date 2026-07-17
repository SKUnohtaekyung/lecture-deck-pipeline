#!/usr/bin/env python3
"""Prepare a paper-cut PNG without modifying the installed imagegen helper.

The built-in generation path produces a flat chroma background.  This wrapper
validates that source before keying, removes only the border-connected chroma,
repairs semi-transparent RGB from the nearest opaque interior pixel, and crops
the result to a small transparent safety margin.
"""
from __future__ import annotations

import argparse
import math
import os
import statistics
import sys
import tempfile
from collections import deque
from pathlib import Path

try:
    from PIL import Image
except ImportError as exc:  # Pillow is intentionally required only here.
    raise SystemExit("[FAIL] Pillow is required for image asset preparation") from exc


DEFAULT_KEY = (255, 0, 255)


class AssetPreparationError(ValueError):
    """Raised when an input cannot safely be converted to a transparent asset."""


def parse_rgb(value: str) -> tuple[int, int, int]:
    value = value.strip().lstrip("#")
    if len(value) != 6:
        raise argparse.ArgumentTypeError("color must be a six-digit RGB hex value")
    try:
        return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("invalid RGB hex value") from exc


def _max_channel_distance(a: tuple[int, int, int], b: tuple[int, int, int]) -> int:
    return max(abs(a[i] - b[i]) for i in range(3))


def _percentile(values: list[int], percentile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    rank = (len(ordered) - 1) * percentile
    low = math.floor(rank)
    high = math.ceil(rank)
    if low == high:
        return float(ordered[low])
    return ordered[low] * (high - rank) + ordered[high] * (rank - low)


def _border_coordinates(width: int, height: int):
    for x in range(width):
        yield x, 0
        if height > 1:
            yield x, height - 1
    for y in range(1, max(1, height - 1)):
        yield 0, y
        if width > 1:
            yield width - 1, y


def validate_chroma_source(
    image: Image.Image,
    *,
    key: tuple[int, int, int] = DEFAULT_KEY,
    border_p95_limit: int = 12,
    key_tolerance: int = 28,
) -> dict[str, float]:
    """Validate uniform border, subject clearance, and interior key collision."""
    rgb = image.convert("RGB")
    width, height = rgb.size
    if width < 3 or height < 3:
        raise AssetPreparationError("source image is too small")
    pixels = rgb.load()
    border = [pixels[x, y] for x, y in _border_coordinates(width, height)]
    median = tuple(int(statistics.median(channel)) for channel in zip(*border))
    deviations = [_max_channel_distance(pixel, median) for pixel in border]
    p95 = _percentile(deviations, 0.95)
    if p95 > border_p95_limit:
        raise AssetPreparationError(
            f"border is not uniform: p95 max-channel deviation {p95:.1f} > {border_p95_limit}"
        )
    if _max_channel_distance(median, key) > key_tolerance:
        raise AssetPreparationError(
            f"border color {median} does not match chroma key {key} within {key_tolerance}"
        )

    key_like = [False] * (width * height)
    for y in range(height):
        for x in range(width):
            key_like[y * width + x] = _max_channel_distance(pixels[x, y], key) <= key_tolerance

    border_non_key = [(x, y) for x, y in _border_coordinates(width, height) if not key_like[y * width + x]]
    if border_non_key:
        raise AssetPreparationError("subject touches the canvas border")

    # Flood-fill background chroma. A key-colored island inside the subject is
    # ambiguous and would punch an unintended hole, so reject it explicitly.
    reached = bytearray(width * height)
    queue: deque[tuple[int, int]] = deque()
    for x, y in _border_coordinates(width, height):
        idx = y * width + x
        if key_like[idx] and not reached[idx]:
            reached[idx] = 1
            queue.append((x, y))
    while queue:
        x, y = queue.popleft()
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= nx < width and 0 <= ny < height:
                idx = ny * width + nx
                if key_like[idx] and not reached[idx]:
                    reached[idx] = 1
                    queue.append((nx, ny))
    collisions = sum(1 for idx, is_key in enumerate(key_like) if is_key and not reached[idx])
    if collisions:
        raise AssetPreparationError(f"subject contains {collisions} chroma-key pixels")
    return {"border_p95": p95, "border_key_distance": float(_max_channel_distance(median, key))}


def _repair_partial_rgb(image: Image.Image) -> Image.Image:
    """Copy nearest opaque interior RGB through each connected alpha component."""
    rgba = image.convert("RGBA")
    width, height = rgba.size
    data = list(rgba.get_flattened_data())
    owner = [-1] * (width * height)
    queue: deque[int] = deque()
    for idx, pixel in enumerate(data):
        if pixel[3] >= 250:
            owner[idx] = idx
            queue.append(idx)
    while queue:
        idx = queue.popleft()
        x, y = idx % width, idx // width
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= nx < width and 0 <= ny < height:
                nidx = ny * width + nx
                if data[nidx][3] > 0 and owner[nidx] < 0:
                    owner[nidx] = owner[idx]
                    queue.append(nidx)
    repaired = []
    for idx, pixel in enumerate(data):
        if 0 < pixel[3] < 255 and owner[idx] >= 0:
            source = data[owner[idx]]
            repaired.append((source[0], source[1], source[2], pixel[3]))
        elif pixel[3] == 0:
            repaired.append((0, 0, 0, 0))
        else:
            repaired.append(pixel)
    rgba.putdata(repaired)
    return rgba


def remove_border_chroma(
    image: Image.Image,
    *,
    key: tuple[int, int, int] = DEFAULT_KEY,
    transparent_tolerance: int = 18,
    opaque_tolerance: int = 72,
) -> Image.Image:
    """Convert chroma distance to alpha, then repair edge RGB."""
    if opaque_tolerance <= transparent_tolerance:
        raise AssetPreparationError("opaque tolerance must exceed transparent tolerance")
    rgb = image.convert("RGB")
    out = Image.new("RGBA", rgb.size)
    converted = []
    span = opaque_tolerance - transparent_tolerance
    for pixel in rgb.get_flattened_data():
        distance = _max_channel_distance(pixel, key)
        if distance <= transparent_tolerance:
            alpha = 0
        elif distance >= opaque_tolerance:
            alpha = 255
        else:
            alpha = round(255 * (distance - transparent_tolerance) / span)
        converted.append((pixel[0], pixel[1], pixel[2], alpha))
    out.putdata(converted)
    return _repair_partial_rgb(out)


def crop_to_alpha(image: Image.Image, padding_ratio: float = 0.05) -> Image.Image:
    """Tight-crop to alpha and add no more than 10% transparent margin per side."""
    if not 0 <= padding_ratio <= 0.10:
        raise AssetPreparationError("padding ratio must be between 0 and 0.10")
    rgba = image.convert("RGBA")
    bbox = rgba.getchannel("A").getbbox()
    if bbox is None:
        raise AssetPreparationError("result is fully transparent")
    left, top, right, bottom = bbox
    subject_w, subject_h = right - left, bottom - top
    pad_x = max(1, round(subject_w * padding_ratio)) if padding_ratio else 0
    pad_y = max(1, round(subject_h * padding_ratio)) if padding_ratio else 0
    crop = rgba.crop((left, top, right, bottom))
    result = Image.new("RGBA", (subject_w + 2 * pad_x, subject_h + 2 * pad_y), (0, 0, 0, 0))
    result.alpha_composite(crop, (pad_x, pad_y))
    return result


def prepare_asset(
    source: Path,
    destination: Path,
    *,
    mode: str = "chroma",
    key: tuple[int, int, int] = DEFAULT_KEY,
    padding_ratio: float = 0.05,
) -> dict[str, float]:
    try:
        with Image.open(source) as opened:
            opened.load()
            image = opened.copy()
    except (OSError, ValueError) as exc:
        raise AssetPreparationError(f"cannot decode source image: {exc}") from exc

    metrics: dict[str, float] = {}
    if mode == "chroma":
        metrics.update(validate_chroma_source(image, key=key))
        prepared = remove_border_chroma(image, key=key)
    elif mode == "native-alpha":
        if image.mode != "RGBA":
            raise AssetPreparationError("native-alpha input must be an actual RGBA image")
        prepared = _repair_partial_rgb(image)
    else:
        raise AssetPreparationError(f"unknown mode: {mode}")
    prepared = crop_to_alpha(prepared, padding_ratio)

    destination = destination.resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=destination.stem + ".", suffix=".png", dir=destination.parent)
    os.close(fd)
    try:
        prepared.save(temp_name, format="PNG", optimize=True)
        os.replace(temp_name, destination)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)
    metrics.update({"width": float(prepared.width), "height": float(prepared.height)})
    return metrics


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--mode", choices=("chroma", "native-alpha"), default="chroma")
    parser.add_argument("--key", type=parse_rgb, default=DEFAULT_KEY)
    parser.add_argument("--padding-ratio", type=float, default=0.05)
    args = parser.parse_args()
    try:
        metrics = prepare_asset(
            args.source,
            args.destination,
            mode=args.mode,
            key=args.key,
            padding_ratio=args.padding_ratio,
        )
    except AssetPreparationError as exc:
        print(f"[FAIL] {exc}")
        return 1
    print(
        f"[PASS] {args.destination} | {int(metrics['width'])}x{int(metrics['height'])}"
        + (f" | border p95={metrics['border_p95']:.1f}" if "border_p95" in metrics else "")
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
