#!/usr/bin/env python3
"""Assemble a preview deck from shell.html + part-*.html fragments.

A draft folder holds editable fragments:
  shell.html    fixed head/JS plus the cover/intro/agenda/recap slots and a
                single ``<!-- ::PARTS:: -->`` marker where the parts belong.
  part-01.html  a part-divider plus that part's ``<section class="slide">`` blocks.
  order.txt     (optional) explicit merge order, one filename per line.

``assemble()`` replaces the marker with the ordered part fragments and writes a
single preview ``강의덱.html`` next to the draft folder. The same assembly feeds
the offline distributable build, so "preview works but release breaks" cannot
happen. Standard library only — no network access, no external dependencies.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile
import time
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

MARKER = "<!-- ::PARTS:: -->"


def _ordered_parts(draft_dir: Path) -> tuple[list[Path], list[str]]:
    """Return the part fragments in merge order, or an error list."""
    order_path = draft_dir / "order.txt"
    if order_path.is_file():
        try:
            lines = order_path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeError) as exc:
            return [], [f"cannot read order.txt: {exc}"]
        names = [line.strip() for line in lines if line.strip()]
        if not names:
            return [], ["order.txt is empty"]
        parts: list[Path] = []
        missing: list[str] = []
        for name in names:
            candidate = draft_dir / name
            if candidate.is_file():
                parts.append(candidate)
            else:
                missing.append(name)
        if missing:
            return [], [f"order.txt lists missing part(s): {', '.join(missing)}"]
        return parts, []
    parts = sorted(draft_dir.glob("part-*.html"), key=lambda p: p.name)
    if not parts:
        return [], ["no part fragments found (need part-*.html or order.txt)"]
    return parts, []


def _build_html(draft_dir: Path) -> tuple[bool, list[str], list[str], str]:
    """Merge shell + parts into one HTML string. Returns (ok, errors, log, html)."""
    log: list[str] = []
    shell_path = draft_dir / "shell.html"
    if not shell_path.is_file():
        return False, [f"missing shell.html in {draft_dir}"], log, ""
    try:
        shell = shell_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return False, [f"cannot read shell.html: {exc}"], log, ""
    marker_count = shell.count(MARKER)
    if marker_count != 1:
        return False, [f"shell.html must contain exactly one '{MARKER}' marker (found {marker_count})"], log, ""
    parts, errors = _ordered_parts(draft_dir)
    if errors:
        return False, errors, log, ""
    chunks: list[str] = []
    for part in parts:
        try:
            chunks.append(part.read_text(encoding="utf-8"))
        except (OSError, UnicodeError) as exc:
            return False, [f"cannot read part {part.name}: {exc}"], log, ""
    assembled = shell.replace(MARKER, "\n".join(chunks), 1)
    # Count real sections, not markup mentioned inside HTML comments/examples.
    visible = re.sub(r"<!--.*?-->", "", assembled, flags=re.S)
    slide_count = visible.count('<section class="slide')
    divider_count = len(re.findall(r"<section\b[^>]*part-divider", visible))
    log.append(f"parts merged: {len(parts)} ({', '.join(p.name for p in parts)})")
    log.append(f"slide sections: {slide_count}")
    log.append(f"part-divider sections: {divider_count}")
    return True, [], log, assembled


def _write_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=path.stem + ".", suffix=path.suffix or ".html", dir=path.parent)
    os.close(fd)
    try:
        Path(temp_name).write_text(text, encoding="utf-8")
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


_LIVERELOAD = """<script data-livereload>
/* dev preview auto-reload — injected only into the --watch --livereload build */
(function () {
  var url = location.href.split('#')[0];
  var last = null;
  function tick() {
    fetch(url, { method: 'HEAD', cache: 'no-store' }).then(function (res) {
      var tag = res.headers.get('Last-Modified') || res.headers.get('ETag') || '';
      if (last !== null && tag && tag !== last) { location.reload(); return; }
      if (tag) { last = tag; }
    }).catch(function () { /* server busy mid-rebuild; retry next tick */ });
  }
  setInterval(tick, 3000);
})();
</script>"""


def _inject_livereload(html: str) -> str:
    if "</body>" in html:
        return html.replace("</body>", _LIVERELOAD + "\n</body>", 1)
    return html + "\n" + _LIVERELOAD + "\n"


def _assemble_once(draft_dir: Path, output: Path, *, livereload: bool = False) -> tuple[bool, list[str], list[str]]:
    ok, errors, log, html = _build_html(draft_dir)
    if not ok:
        return False, errors, log
    if livereload:
        html = _inject_livereload(html)
    try:
        _write_atomic(output, html)
    except OSError as exc:
        return False, [f"cannot write output {output}: {exc}"], log
    log.append(f"written: {output}")
    return True, [], log


def assemble(draft_dir: Path, output: Path | None = None) -> tuple[bool, list[str], list[str]]:
    """Assemble the preview deck. Returns (ok, errors, log)."""
    draft_dir = Path(draft_dir)
    out = Path(output) if output is not None else draft_dir.parent / "강의덱.html"
    return _assemble_once(draft_dir, out)


def _snapshot(draft_dir: Path, skip: Path | None = None) -> dict[str, int]:
    snap: dict[str, int] = {}
    for path in draft_dir.rglob("*"):
        if not path.is_file():
            continue
        resolved = path.resolve()
        if skip is not None and resolved == skip:
            continue
        try:
            snap[str(resolved)] = path.stat().st_mtime_ns
        except OSError:
            pass
    return snap


def _print_result(ok: bool, errors: list[str], log: list[str], output: Path) -> None:
    for item in log:
        print(f"  {item}")
    if ok:
        print(f"[PASS] {output}")
    else:
        for error in errors:
            print(f"[FAIL] {error}")
        print("[FAIL] no preview file was written")


def _watch(draft_dir: Path, output: Path, *, livereload: bool) -> int:
    if not draft_dir.is_dir():
        print(f"[FAIL] draft folder not found: {draft_dir}")
        return 1
    skip = output.resolve()
    ok, errors, log = _assemble_once(draft_dir, output, livereload=livereload)
    _print_result(ok, errors, log, output)
    mode = "watch+livereload" if livereload else "watch"
    print(f"[{mode}] polling {draft_dir} every 0.5s — Ctrl-C to stop")
    prev = _snapshot(draft_dir, skip=skip)
    try:
        while True:
            time.sleep(0.5)
            current = _snapshot(draft_dir, skip=skip)
            if current == prev:
                continue
            prev = current
            ok, errors, log = _assemble_once(draft_dir, output, livereload=livereload)
            stamp = time.strftime("%H:%M:%S")
            if ok:
                slides = next((line for line in log if line.startswith("slide sections")), "reassembled")
                print(f"  [{stamp}] {output.name}: {slides}")
            else:
                print(f"  [{stamp}] FAIL: {errors[0] if errors else 'unknown error'}")
    except KeyboardInterrupt:
        print("\n[watch] stopped")
        return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Assemble a preview deck from shell.html + part-*.html fragments.")
    parser.add_argument("draft_dir", type=Path, help="folder holding shell.html and part-*.html")
    parser.add_argument("--output", type=Path, help="output path (default: <draft_dir>/../강의덱.html)")
    parser.add_argument("--watch", action="store_true", help="re-assemble on fragment changes (0.5s polling)")
    parser.add_argument("--livereload", action="store_true", help="with --watch: inject a 3s auto-reload script into the preview")
    args = parser.parse_args(argv)

    draft_dir = args.draft_dir
    output = args.output if args.output is not None else draft_dir.parent / "강의덱.html"

    if args.livereload and not args.watch:
        print("[WARN] --livereload only applies with --watch; ignoring")

    if args.watch:
        return _watch(draft_dir, output, livereload=args.livereload)

    ok, errors, log = _assemble_once(draft_dir, output)
    _print_result(ok, errors, log, output)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
