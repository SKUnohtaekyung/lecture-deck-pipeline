# -*- coding: utf-8 -*-
"""발표본에 넣는 간결한 노트 — `1주차_발표노트.md` → `강의덱_발표노트.html`.

`강의덱_발표자노트.html`(전체 대본 · build_notes.py)과 따로 둔다. 발표본(`강의덱_발표.html`)의
발표자 화면에는 이 간결한 노트가 들어간다(강조할 것만 · 마크다운 목록).

입력 형식(`1주차_발표노트.md`):
    ## <장 ID>
    - 한 줄
    - **굵게** 한 줄

장 순서 · 제목 · 시간은 build_notes.py와 같은 곳에서 읽는다(4h 조립표 · minutes.tsv · 초안의 제목).
노트 본문은 `pn-item pn-md` 한 덩어리로 내고, 줄마다 `<p>`로 둔다. inject_presenter.py가 줄바꿈을
살려 발표자 화면(글상자)에 그대로 보여 준다.

    python plans/FRAME-길이별-조립/build_presenter_notes.py [--variant 4h-app] [--check]
`--variant 4h-app`은 여행 앱 트랙이다: 1주차_발표노트_여행앱.md → 강의덱_4h-app_발표노트.html
(장 순서 · 제목 · 시간은 4h-app 조립표와 1주차_초안_여행앱.md에서 읽고, 머리는 메인 발표자노트에서 물려받는다).
종료코드: 0 정상 · 1 노트가 없는 장이 있음 · 2 입력 없음 또는 인자 오류.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_notes as bn  # noqa: E402

SRC = os.path.join(bn.S, "1주차_발표노트.md")
OUT = os.path.join(bn.S, "강의덱_발표노트.html")
VARIANT_FILES = {"4h-app": ("1주차_발표노트_여행앱.md", "강의덱_4h-app_발표노트.html")}


def read_md():
    notes, cur = {}, None
    for line in open(SRC, encoding="utf-8").read().splitlines():
        m = re.match(r"##\s+([A-Z0-9][A-Z0-9-]*)\s*$", line)
        if m:
            cur = m.group(1); notes[cur] = []
        elif cur and line.strip():
            notes[cur].append(line.rstrip())
    return notes


def main():
    global SRC, OUT
    check = "--check" in sys.argv[1:]
    variant, err = bn.parse_variant(sys.argv[1:])
    if err:
        print(err); return 2
    bn.configure(variant)
    if variant:
        SRC, OUT = (os.path.join(bn.S, n) for n in VARIANT_FILES[variant])
    if not os.path.isfile(SRC):
        print("입력 없음:", os.path.relpath(SRC, bn.ROOT)); return 2
    notes = read_md()
    order = [sid for b in bn.read_manifest() for sid in b["ids"]]
    missing = [sid for sid in order if not notes.get(sid)]
    extra = [sid for sid in notes if sid not in order]
    lines = sum(len(notes[s]) for s in order if s in notes)
    print("RESULT 발표 노트 %d장 중 %d장 · 줄 %d(장당 %.1f) · 노트 없는 장 %d · 덱에 없는 ID %d%s%s" % (
        len(order), len(order) - len(missing), lines, lines / max(1, len(order) - len(missing)), len(missing), len(extra), " · 변형 %s" % variant if variant else "", " · 쓰지 않음(--check)" if check else ""))
    if missing: print("  노트 없는 장:", ", ".join(missing))
    if extra: print("  덱에 없는 ID:", ", ".join(extra))
    if missing: return 1
    if check: return 0

    # build_notes.py의 틀(머리말 · 구간 · 장 머리)을 그대로 쓰고 본문만 바꾼다
    titles = bn.read_rows()
    bn.read_rows = lambda: {sid: (titles[sid][0], "\n".join(notes[sid])) for sid in order}
    bn.note_items = lambda ment: ('    <div class="pn-item pn-md">\n' + "\n".join("      <p>%s</p>" % bn.e(x) for x in ment.split("\n")) + "\n    </div>")
    bn.NOTES = OUT
    if not variant and not os.path.isfile(OUT):
        open(OUT, "w", encoding="utf-8", newline="\n").write(open(os.path.join(bn.S, "강의덱_발표자노트.html"), encoding="utf-8").read())
    sys.argv = [sys.argv[0]]
    return bn.main()


if __name__ == "__main__":
    sys.exit(main())
