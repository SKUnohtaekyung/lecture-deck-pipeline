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


def _build_html(draft_dir: Path, variant: str | None = None,
                allow_over_time: bool = False) -> tuple[bool, list[str], list[str], str]:
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
    parts_html = "\n".join(chunks)
    log.append(f"parts merged: {len(parts)} ({', '.join(p.name for p in parts)})")
    if variant:
        errors, parts_html = _select_variant(draft_dir, variant, parts_html, log, allow_over_time)
        if errors:
            return False, errors, log, ""
        title = _variant_title(draft_dir, variant)
        if title:
            shell, swapped = re.subn(r"<title>.*?</title>", lambda _m: f"<title>{title}</title>", shell, count=1, flags=re.S)
            if not swapped:
                return False, ["@title is set but shell.html has no <title>"], log, ""
            log.append(f"title: {title}")
    assembled = shell.replace(MARKER, parts_html, 1)
    # Count real sections, not markup mentioned inside HTML comments/examples.
    visible = re.sub(r"<!--.*?-->", "", assembled, flags=re.S)
    slide_count = visible.count('<section class="slide')
    divider_count = len(re.findall(r"<section\b[^>]*part-divider", visible))
    log.append(f"slide sections: {slide_count}")
    log.append(f"part-divider sections: {divider_count}")
    return True, [], log, assembled


# ── 변형 조립(variants) ──────────────────────────────────────────────────────
# 같은 조각에서 길이·구성이 다른 덱을 뽑는다. 조립표 ``variants/<이름>.txt``가
# 넣을 장을 data-slide ID로 한 줄에 하나씩, 나올 순서대로 적는다.
#   # 주석            [블록 이름]  — 시간 합계를 묶는 단위
#   @limit 50         블록당 상한(분). 없으면 50
#   @title <글>       이 덱의 <title>. 없으면 shell.html 것을 그대로 쓴다
#   +32 실습 ①~③     장 없이 드는 시간(분)
#   <ID> [메모]       넣을 장
#   ?<ID> [메모]      넣되 시간 합계에서 빼는 선택 장
# ``variants/minutes.tsv``(ID<TAB>분)가 있으면 블록 합계를 판정한다.
# ``variants/<이름>.html``이 있으면 그 안의 장이 같은 ID의 장을 대신한다.

_SECTION_TOKEN = re.compile(r"<section\b[^>]*>|</section\s*>", re.S)
_SLIDE_ID = re.compile(r'\bdata-slide="([^"]*)"')
_LINK_TARGET = re.compile(r'\bdata-(?:go|return-to)="([^"]+)"')
DEFAULT_BLOCK_LIMIT = 50.0


def _split_slides(chunk: str) -> tuple[list[tuple[str | None, str]], str, list[str]]:
    """Split a fragment into top-level sections. Returns ([(slide_id, html)], tail, errors).

    Each html keeps the comment/whitespace gap that precedes its section; tail is
    whatever follows the last section.
    """
    comments = [(m.start(), m.end()) for m in re.finditer(r"<!--.*?-->", chunk, flags=re.S)]

    def in_comment(pos: int) -> bool:
        return any(start <= pos < end for start, end in comments)

    slides: list[tuple[str | None, str]] = []
    depth = 0
    cursor = 0
    open_tag = ""
    for token in _SECTION_TOKEN.finditer(chunk):
        if in_comment(token.start()):
            continue
        if token.group().startswith("</"):
            if depth == 0:
                return [], "", ["unbalanced </section> in fragments"]
            depth -= 1
            if depth == 0:
                found = _SLIDE_ID.search(open_tag)
                slides.append((found.group(1) if found else None, chunk[cursor:token.end()]))
                cursor = token.end()
        else:
            if depth == 0:
                open_tag = token.group()
            depth += 1
    if depth != 0:
        return [], "", ["unclosed <section> in fragments"]
    return slides, chunk[cursor:], []


def _read_manifest(path: Path) -> tuple[list[tuple[str, list[tuple[str, object]]]], float, list[str]]:
    """Parse a variant manifest into [(block name, [("slide", id) | ("extra", minutes)])]."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        return [], DEFAULT_BLOCK_LIMIT, [f"cannot read {path.name}: {exc}"]
    blocks: list[tuple[str, list[tuple[str, object]]]] = []
    limit = DEFAULT_BLOCK_LIMIT
    errors: list[str] = []
    for number, raw in enumerate(lines, 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            blocks.append((line[1:-1].strip(), []))
            continue
        if line.startswith("@title"):
            continue  # _variant_title()이 읽는다
        if line.startswith("@limit"):
            try:
                limit = float(line.split()[1])
            except (IndexError, ValueError):
                errors.append(f"{path.name}:{number}: @limit needs a number")
            continue
        if not blocks:
            blocks.append(("", []))
        if line.startswith("+"):
            try:
                blocks[-1][1].append(("extra", float(line[1:].split()[0])))
            except (IndexError, ValueError):
                errors.append(f"{path.name}:{number}: '+' needs minutes")
            continue
        if line.startswith("?"):
            blocks[-1][1].append(("optional", line[1:].split()[0]))
            continue
        blocks[-1][1].append(("slide", line.split()[0]))
    if not any(kind != "extra" for _, items in blocks for kind, _ in items):
        errors.append(f"{path.name} lists no slides")
    return blocks, limit, errors


def _variant_title(draft_dir: Path, name: str) -> str | None:
    """The manifest's ``@title`` text, or None when it sets none."""
    try:
        lines = (draft_dir / "variants" / f"{name}.txt").read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError):
        return None
    for raw in lines:
        line = raw.strip()
        if line.startswith("@title"):
            return line[len("@title"):].strip() or None
    return None


def _read_minutes(path: Path) -> tuple[dict[str, float], list[str]]:
    minutes: dict[str, float] = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        return {}, [f"cannot read {path.name}: {exc}"]
    for number, raw in enumerate(lines, 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        cells = line.split("\t")
        try:
            minutes[cells[0].strip()] = float(cells[1])
        except (IndexError, ValueError):
            return {}, [f"{path.name}:{number}: expected 'ID<TAB>minutes'"]
    return minutes, []


def _select_variant(draft_dir: Path, name: str, parts_html: str, log: list[str],
                    allow_over_time: bool = False) -> tuple[list[str], str]:
    """Pick and order slides per ``variants/<name>.txt``. Returns (errors, html)."""
    variants_dir = draft_dir / "variants"
    manifest_path = variants_dir / f"{name}.txt"
    if not manifest_path.is_file():
        return [f"missing variant manifest: {manifest_path}"], ""
    blocks, limit, errors = _read_manifest(manifest_path)
    if errors:
        return errors, ""

    slides, tail, errors = _split_slides(parts_html)
    if errors:
        return errors, ""
    unnamed = sum(1 for slide_id, _ in slides if slide_id is None)
    if unnamed:
        return [f"{unnamed} top-level section(s) have no data-slide id; a variant cannot place them"], ""
    pool: dict[str, str] = {}
    for slide_id, html in slides:
        if slide_id in pool:
            return [f"duplicate data-slide id in fragments: {slide_id}"], ""
        pool[slide_id] = html

    override_path = variants_dir / f"{name}.html"
    replaced = 0
    if override_path.is_file():
        try:
            override_slides, _, errors = _split_slides(override_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError) as exc:
            return [f"cannot read {override_path.name}: {exc}"], ""
        if errors:
            return [f"{override_path.name}: {error}" for error in errors], ""
        for slide_id, html in override_slides:
            if slide_id is None:
                return [f"{override_path.name}: a section has no data-slide id"], ""
            replaced += slide_id in pool
            pool[slide_id] = html

    chosen = [value for _, items in blocks for kind, value in items if kind != "extra"]
    missing = [slide_id for slide_id in chosen if slide_id not in pool]
    if missing:
        return [f"{manifest_path.name} lists unknown slide(s): {', '.join(missing)}"], ""
    repeated = sorted({slide_id for slide_id in chosen if chosen.count(slide_id) > 1})
    if repeated:
        return [f"{manifest_path.name} lists slide(s) twice: {', '.join(repeated)}"], ""

    html = "".join(pool[slide_id] for slide_id in chosen) + tail
    dangling = sorted({target for target in _LINK_TARGET.findall(re.sub(r"<!--.*?-->", "", html, flags=re.S))
                       if target not in chosen})
    if dangling:
        return [f"variant '{name}' links to slide(s) it leaves out: {', '.join(dangling)}"], ""

    log.append(f"variant '{name}': {len(chosen)} of {len(pool)} slides (left out {len(pool) - len(chosen)}, replaced {replaced})")

    minutes_path = variants_dir / "minutes.tsv"
    if not minutes_path.is_file():
        log.append("time check: skipped (no variants/minutes.tsv)")
        return [], html
    minutes, errors = _read_minutes(minutes_path)
    if errors:
        return errors, ""
    over: list[str] = []
    unjudged = 0
    optional = 0
    for block_name, items in blocks:
        total = 0.0
        for kind, value in items:
            if kind == "extra":
                total += float(value)  # type: ignore[arg-type]
            elif kind == "optional":
                optional += 1
            elif value in minutes:
                total += minutes[value]  # type: ignore[index]
            else:
                unjudged += 1
        label = block_name or "(unnamed block)"
        log.append(f"  time [{label}]: {total:g} / {limit:g} min")
        if total > limit:
            over.append(f"{label} {total:g} > {limit:g}")
    # 분이 없는 장은 합계에 0으로 들어가므로 따로 센다(눈먼 통과 방지).
    log.append(f"time check: {len(blocks)} block(s) judged · over limit {len(over)} · unjudged slides {unjudged} · optional slides {optional}")
    if over and allow_over_time:
        log.append(f"[WARN] block limit exceeded but allowed: {'; '.join(over)}")
    elif over:
        return [f"variant '{name}' exceeds the block limit: {'; '.join(over)}"], ""
    return [], html


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


def _assemble_once(draft_dir: Path, output: Path, *, livereload: bool = False,
                   variant: str | None = None, allow_over_time: bool = False) -> tuple[bool, list[str], list[str]]:
    ok, errors, log, html = _build_html(draft_dir, variant, allow_over_time)
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


def _default_output(draft_dir: Path, variant: str | None) -> Path:
    return draft_dir.parent / (f"강의덱_{variant}.html" if variant else "강의덱.html")


def assemble(draft_dir: Path, output: Path | None = None, variant: str | None = None,
             allow_over_time: bool = False) -> tuple[bool, list[str], list[str]]:
    """Assemble the preview deck. Returns (ok, errors, log)."""
    draft_dir = Path(draft_dir)
    out = Path(output) if output is not None else _default_output(draft_dir, variant)
    return _assemble_once(draft_dir, out, variant=variant, allow_over_time=allow_over_time)


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


def _watch(draft_dir: Path, output: Path, *, livereload: bool, variant: str | None = None,
           allow_over_time: bool = False) -> int:
    if not draft_dir.is_dir():
        print(f"[FAIL] draft folder not found: {draft_dir}")
        return 1
    skip = output.resolve()
    ok, errors, log = _assemble_once(draft_dir, output, livereload=livereload, variant=variant,
                                     allow_over_time=allow_over_time)
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
            ok, errors, log = _assemble_once(draft_dir, output, livereload=livereload, variant=variant,
                                     allow_over_time=allow_over_time)
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
    parser.add_argument("--variant", help="assemble only the slides listed in variants/<name>.txt "
                                          "(default output: <draft_dir>/../강의덱_<name>.html)")
    parser.add_argument("--allow-over-time", action="store_true",
                        help="with --variant: write the deck even if a block exceeds its time limit (prints WARN)")
    parser.add_argument("--watch", action="store_true", help="re-assemble on fragment changes (0.5s polling)")
    parser.add_argument("--livereload", action="store_true", help="with --watch: inject a 3s auto-reload script into the preview")
    args = parser.parse_args(argv)

    draft_dir = args.draft_dir
    output = args.output if args.output is not None else _default_output(draft_dir, args.variant)

    if args.livereload and not args.watch:
        print("[WARN] --livereload only applies with --watch; ignoring")

    if args.watch:
        return _watch(draft_dir, output, livereload=args.livereload, variant=args.variant,
                      allow_over_time=args.allow_over_time)

    ok, errors, log = _assemble_once(draft_dir, output, variant=args.variant, allow_over_time=args.allow_over_time)
    _print_result(ok, errors, log, output)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
