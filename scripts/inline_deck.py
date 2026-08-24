#!/usr/bin/env python3
"""Build a strict, self-contained deck (CSS, scripts, images, srcset, CSS url())."""
from __future__ import annotations

import argparse
import base64
import mimetypes
import os
import re
import sys
import tempfile
from pathlib import Path
from urllib.parse import unquote, urlsplit

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REMOTE = re.compile(r"^(?:https?:)?//", re.I)

try:  # dual-context import: package (tests) or script (CLI)
    from scripts import font_embed
except ImportError:
    import font_embed


def _find_repo_root(start: Path) -> Path:
    current = start.resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    return current


class Bundler:
    def __init__(self, deck: Path, *, root: Path, offline: bool):
        self.deck = deck.resolve()
        self.base = self.deck.parent
        self.root = root.resolve()
        self.offline = offline
        self.errors: list[str] = []
        self.log: list[str] = []
        self.font_source = font_embed.DEFAULT_FONT
        self.needs_font = False
        self.font_embedded = False

    def _resolve(self, reference: str, base: Path | None = None) -> Path | None:
        clean = unquote(urlsplit(reference).path)
        path = ((base or self.base) / clean).resolve()
        try:
            path.relative_to(self.root)
        except ValueError:
            self.errors.append(f"path escapes repository root: {reference}")
            return None
        if not path.is_file():
            self.errors.append(f"missing local asset: {reference}")
            return None
        return path

    def _data_uri(self, reference: str, base: Path | None = None) -> str:
        if reference.startswith("data:") or reference.startswith("#"):
            return reference
        if REMOTE.match(reference):
            if self.offline:
                self.errors.append(f"offline external dependency: {reference}")
            return reference
        path = self._resolve(reference, base)
        if path is None:
            return reference
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        self.log.append(f"asset inline: {reference}")
        return f"data:{mime};base64,{encoded}"

    def _css(self, css: str, base: Path) -> str:
        if re.search(r"@import\s+", css, re.I):
            self.errors.append(f"CSS @import is not allowed in a standalone bundle: {base}")

        def replace_url(match: re.Match[str]) -> str:
            quote = match.group(1) or ""
            reference = match.group(2).strip()
            return f"url({quote}{self._data_uri(reference, base)}{quote})"

        return re.sub(r"url\(\s*(['\"]?)(.*?)\1\s*\)", replace_url, css, flags=re.I)

    def inline_stylesheets(self, html: str) -> str:
        def replace(match: re.Match[str]) -> str:
            tag = match.group(0)
            rel = _attribute(tag, "rel").lower()
            href = _attribute(tag, "href")
            if "stylesheet" not in rel:
                if self.offline and REMOTE.match(href) and any(token in rel for token in ("preconnect", "dns-prefetch")):
                    self.errors.append(f"offline external dependency: {href}")
                    self.log.append(f"external hint removed: {href}")
                    return ""
                return tag
            if REMOTE.match(href):
                if "pretendard" in href.lower():
                    return tag  # left for embed_font() to replace with a subset @font-face
                if self.offline:
                    self.errors.append(f"offline external dependency: {href}")
                    self.log.append(f"external stylesheet removed: {href}")
                    return ""
                return tag
            path = self._resolve(href)
            if path is None:
                return tag
            try:
                css = path.read_text(encoding="utf-8")
            except (OSError, UnicodeError) as exc:
                self.errors.append(f"cannot read stylesheet {href}: {exc}")
                return tag
            self.log.append(f"CSS inline: {href}")
            return "<style>\n" + self._css(css, path.parent) + "\n</style>"

        return re.sub(r"<link\b[^>]*>", replace, html, flags=re.I)

    def inline_scripts(self, html: str) -> str:
        def replace(match: re.Match[str]) -> str:
            tag, body = match.group(1), match.group(2)
            src = _attribute(tag, "src")
            if not src:
                return match.group(0)
            if REMOTE.match(src):
                if self.offline:
                    self.errors.append(f"offline external script: {src}")
                return match.group(0)
            path = self._resolve(src)
            if path is None:
                return match.group(0)
            try:
                script = path.read_text(encoding="utf-8")
            except (OSError, UnicodeError) as exc:
                self.errors.append(f"cannot read script {src}: {exc}")
                return match.group(0)
            clean_tag = re.sub(r"\s+src\s*=\s*(['\"]).*?\1", "", tag, flags=re.I)
            self.log.append(f"script inline: {src}")
            return f"{clean_tag}{script}</script>"

        return re.sub(r"(<script\b[^>]*>)(.*?)</script>", replace, html, flags=re.I | re.S)

    def inline_media(self, html: str) -> str:
        def replace_tag(match: re.Match[str]) -> str:
            tag = match.group(0)
            tag_name_match = re.match(r"<\s*([a-z0-9]+)", tag, re.I)
            tag_name = tag_name_match.group(1).lower() if tag_name_match else ""
            for attribute in ("src", "poster"):
                value = _attribute(tag, attribute)
                if value:
                    tag = _replace_attribute(tag, attribute, self._data_uri(value))
            srcset = _attribute(tag, "srcset")
            if srcset:
                candidates = [candidate.strip().split(None, 1)[0] for candidate in srcset.split(",") if candidate.strip()]
                converted = [self._data_uri(candidate) for candidate in candidates]
                # A base64 data URL contains a comma, which is also srcset's
                # candidate delimiter. Keep the inlined img fallback instead of
                # emitting a syntactically broken data-URI srcset. Picture source
                # elements are therefore redundant in a standalone bundle.
                if tag_name == "source" and not _attribute(tag, "src"):
                    self.log.append("picture srcset collapsed to img fallback")
                    return ""
                if tag_name == "img" and not _attribute(tag, "src") and converted:
                    tag = re.sub(r"\s*/?>$", f' src="{converted[-1]}">', tag)
                tag = _remove_attribute(tag, "srcset")
            return tag

        return re.sub(r"<(?:img|source|video)\b[^>]*>", replace_tag, html, flags=re.I)

    def inline_css_blocks(self, html: str) -> str:
        html = re.sub(
            r"(<style\b[^>]*>)(.*?)(</style>)",
            lambda match: match.group(1) + self._css(match.group(2), self.base) + match.group(3),
            html,
            flags=re.I | re.S,
        )

        def replace_style(match: re.Match[str]) -> str:
            return match.group(1) + self._css(match.group(2), self.base) + match.group(1)

        return re.sub(r"(?i)(?<=\sstyle=)(['\"])(.*?)\1", replace_style, html)

    def embed_font(self, html: str) -> str:
        """Replace the Pretendard CDN link with an embedded, subset @font-face.

        Runs after CSS is inlined so glyph collection covers ``content:`` text and
        CSS unicode escapes; the subset is computed from the final HTML.
        """
        if not font_embed.PRETENDARD_LINK.search(html):
            return html
        self.needs_font = True
        try:
            style, glyphs, size = font_embed.build_font_style(html, source=self.font_source)
        except font_embed.FontEmbedError as exc:
            self.errors.append(f"cannot embed Pretendard font: {exc}")
            return html
        html = font_embed.PRETENDARD_LINK.sub("", html, count=1)
        if "</head>" in html:
            html = html.replace("</head>", style + "\n</head>", 1)
        else:
            html = style + html
        self.font_embedded = True
        self.log.append(f"font embedded: {size // 1024}KB subset ({glyphs} glyphs)")
        return html

    def validate_slots(self, html: str) -> None:
        """Find every ``<figure class="asset-slot">`` and enforce the image-slot contract.

        0-verdict guard (miss-detection hardening, plans/gate-input-hardening/PLAN.md P1,
        item ``inline_deck.py:209-216``): if the ``asset-slot`` class name ever drifts
        (renamed, typo'd), the ``continue`` below fires for every ``<figure>`` and this
        function silently judges nothing — a zero that looks identical to "this deck has
        no image slots" even though slots exist. ``data-image-purpose``/``data-image-state``
        are an independent secondary signal for slot intent: a repo-wide scan of every
        ``<figure>`` in this codebase (460 elements, 2026-08-24) found zero cases where
        either attribute appears without the ``asset-slot`` class also present. So a
        ``<figure>`` carrying one of those attributes but missing the class is not a
        legitimate "nothing to judge" case — it is evidence the class-based match went
        blind, and is reported as an error instead of being swallowed by ``continue``.
        """
        judged = 0
        blind_spot: list[str] = []
        for match in re.finditer(r"<figure\b([^>]*)>(.*?)</figure>", html, re.I | re.S):
            attributes, body = match.group(1), match.group(2)
            purpose = _attribute(attributes, "data-image-purpose")
            state = _attribute(attributes, "data-image-state")
            if not re.search(r"\basset-slot\b", _attribute(attributes, "class")):
                if purpose or state:
                    blind_spot.append(purpose or state)
                continue
            judged += 1
            if purpose in {"explanatory", "mnemonic"} and (state == "expected" or not re.search(r"<img\b", body, re.I)):
                self.errors.append(f"unresolved required {purpose} image slot")
            if state == "expected" and re.search(r"<img\b[^>]*\bsrc=", body, re.I):
                self.errors.append("expected image slot must not contain an img src")
        if blind_spot:
            self.errors.append(
                f"image-slot validation blind spot: {len(blind_spot)} figure(s) carry "
                f"data-image-purpose/data-image-state ({', '.join(blind_spot[:5])}"
                f"{', ...' if len(blind_spot) > 5 else ''}) but no 'asset-slot' class — "
                f"the class name may have drifted, so required/forbidden-image checks "
                f"({judged} figure(s) judged) are silently skipping them"
            )
        self.log.append(f"image slots judged: {judged}")

    def postcheck(self, html: str) -> None:
        # No fetchable reference may survive an offline build.
        if self.offline:
            for tag in re.findall(r"<(?:link|script|img|source|video)\b[^>]*>", html, re.I):
                for attribute in ("href", "src", "srcset", "poster"):
                    value = _attribute(tag, attribute)
                    if value and REMOTE.search(value):
                        self.errors.append(f"external request remains after bundling: {value}")
            for value in re.findall(r"url\(\s*['\"]?([^)'\"]+)", html, re.I):
                if REMOTE.match(value):
                    self.errors.append(f"external CSS request remains after bundling: {value}")
            if re.search(r"href\s*=\s*['\"][^'\"]*pretendard", html, re.I):
                self.errors.append("external Pretendard font link remains after bundling")
            if self.needs_font and not (
                re.search(r"@font-face", html, re.I)
                and re.search(r"url\(\s*['\"]?data:font/woff2", html, re.I)
            ):
                self.errors.append("self-contained bundle is missing an embedded @font-face")
        for tag in re.findall(r"<(?:link|script|img|source|video)\b[^>]*>", html, re.I):
            for attribute in ("src", "poster"):
                value = _attribute(tag, attribute)
                if value and not value.startswith(("data:", "#")) and not REMOTE.match(value):
                    self.errors.append(f"unbundled local reference remains: {value}")


def _attribute(tag: str, name: str) -> str:
    match = re.search(rf"\b{re.escape(name)}\s*=\s*(['\"])(.*?)\1", tag, re.I | re.S)
    return match.group(2) if match else ""


def _replace_attribute(tag: str, name: str, value: str) -> str:
    return re.sub(
        rf"(\b{re.escape(name)}\s*=\s*)(['\"])(.*?)\2",
        lambda match: match.group(1) + match.group(2) + value + match.group(2),
        tag,
        count=1,
        flags=re.I | re.S,
    )


def _remove_attribute(tag: str, name: str) -> str:
    return re.sub(
        rf"\s+\b{re.escape(name)}\s*=\s*(['\"])(.*?)\1",
        "",
        tag,
        count=1,
        flags=re.I | re.S,
    )


def bundle(deck: Path, *, output: Path, offline: bool, root: Path | None = None) -> tuple[bool, list[str], list[str]]:
    deck = deck.resolve()
    root_path = (root or _find_repo_root(deck.parent)).resolve()
    output = output.resolve()
    try:
        output.relative_to(root_path)
    except ValueError:
        return False, [f"output escapes repository root: {output}"], []
    if output == deck:
        return False, ["output must not overwrite the source deck"], []

    def remove_stale(errors: list[str]) -> None:
        if output.is_file():
            try:
                output.unlink()
            except OSError as exc:
                errors.append(f"cannot remove stale output {output}: {exc}")

    try:
        html = deck.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors = [f"cannot read deck: {exc}"]
        remove_stale(errors)
        return False, errors, []
    html = re.sub(r"<!--.*?-->", "", html, flags=re.S)  # commented examples must not be inlined/validated
    bundler = Bundler(deck, root=root_path, offline=offline)
    bundler.validate_slots(html)
    html = bundler.inline_stylesheets(html)
    html = bundler.inline_scripts(html)
    html = bundler.inline_media(html)
    html = bundler.inline_css_blocks(html)
    html = bundler.embed_font(html)
    bundler.postcheck(html)
    if bundler.errors:
        remove_stale(bundler.errors)
        return False, bundler.errors, bundler.log

    output.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=output.stem + ".", suffix=".html", dir=output.parent)
    os.close(fd)
    try:
        Path(temp_name).write_text(html, encoding="utf-8")
        os.replace(temp_name, output)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)
    return True, [], bundler.log


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("deck", type=Path)
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--root", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or args.deck.with_name(args.deck.stem + "_배포.html")
    ok, errors, log = bundle(args.deck, output=output, offline=args.offline, root=args.root)
    for item in log:
        print(f"  {item}")
    if not ok:
        for error in errors:
            print(f"[FAIL] {error}")
        print("[FAIL] no deployment file was written")
        return 1
    size_kb = output.stat().st_size // 1024
    print(f"[PASS] created: {output} ({size_kb}KB)")
    if size_kb > 8000:
        print("[WARN] bundle exceeds 8MB; downscale source images")
    return 0


if __name__ == "__main__":
    sys.exit(main())
