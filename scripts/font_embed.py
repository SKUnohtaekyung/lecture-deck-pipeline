#!/usr/bin/env python3
"""Subset the vendored Pretendard variable font to the glyphs a deck actually uses
and return a self-contained ``@font-face`` block.

Glyph collection runs against the *fully inlined* deck HTML so that text which only
appears after CSS is inlined (``content:"핵심"``), CSS unicode escapes
(``content:"\\25B8"`` -> ▸), and JS string literals injected at runtime
(``'표지'``, ``'PART ' + n``) are all covered. Missing a glyph is the only real
failure mode, so collection deliberately over-includes (printable ASCII is always
kept) — extra glyphs only cost a few bytes.
"""
from __future__ import annotations

import base64
import re
from io import BytesIO
from pathlib import Path

DEFAULT_FONT = Path(__file__).resolve().parents[1] / "kit" / "fonts" / "PretendardVariable.woff2"

# A stylesheet <link> whose href points at the Pretendard web font (CDN).
PRETENDARD_LINK = re.compile(
    r"<link\b[^>]*\bhref\s*=\s*(['\"])[^'\"]*pretendard[^'\"]*\1[^>]*>", re.I
)
# data: URIs (image/font bytes) must not be mined for text glyphs.
_BASE64_BLOB = re.compile(r"data:[^;,\s'\"()]*;base64,[A-Za-z0-9+/=\s]+", re.I)
# CSS unicode escapes inside content:"\25B8" style declarations.
_CSS_HEX_ESCAPE = re.compile(r"\\([0-9A-Fa-f]{1,6})")


class FontEmbedError(RuntimeError):
    """Raised when a subset cannot be produced (missing deps or source font)."""


def collect_glyphs(html: str) -> str:
    """Return every character that could render in ``html`` as a sorted string."""
    text = _BASE64_BLOB.sub(" ", html)
    chars: set[str] = set(text)
    for match in _CSS_HEX_ESCAPE.finditer(text):
        try:
            chars.add(chr(int(match.group(1), 16)))
        except (ValueError, OverflowError):
            continue
    chars |= {chr(code) for code in range(0x20, 0x7F)}  # ASCII base (JS-injected digits/punct)
    return "".join(sorted(c for c in chars if c.isprintable() and c != "﻿"))


def subset_woff2(text: str, *, source: Path = DEFAULT_FONT) -> bytes:
    """Subset ``source`` (a variable woff2) to ``text`` and return woff2 bytes.

    The wght variation axis is retained so a single face renders every weight.
    """
    if not source.is_file():
        raise FontEmbedError(f"font source is missing: {source}")
    try:
        from fontTools import subset
        from fontTools.ttLib import TTFont
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise FontEmbedError("fonttools (with brotli) is required to embed fonts") from exc

    options = subset.Options()
    options.flavor = "woff2"
    options.desubroutinize = True
    font = TTFont(str(source))
    subsetter = subset.Subsetter(options=options)
    subsetter.populate(text=text)
    subsetter.subset(font)
    buffer = BytesIO()
    font.save(buffer)
    return buffer.getvalue()


def font_face_css(woff2: bytes, *, family: str = "Pretendard") -> str:
    """Return an ``@font-face`` rule embedding ``woff2`` as a data URI."""
    encoded = base64.b64encode(woff2).decode("ascii")
    return (
        "@font-face{font-family:'" + family + "';"
        "font-style:normal;font-weight:100 900;font-display:swap;"
        "src:url(data:font/woff2;base64," + encoded + ") format('woff2');}"
    )


def build_font_style(html: str, *, source: Path = DEFAULT_FONT, family: str = "Pretendard") -> tuple[str, int, int]:
    """Subset to the glyphs used in ``html`` and return (``<style>`` block, glyph count, byte size)."""
    glyphs = collect_glyphs(html)
    woff2 = subset_woff2(glyphs, source=source)
    return "<style>" + font_face_css(woff2, family=family) + "</style>", len(glyphs), len(woff2)
