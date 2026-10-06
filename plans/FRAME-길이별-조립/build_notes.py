#!/usr/bin/env python3
"""FRAME 발표자 노트 재생성 — 초안의 멘트 칸에서 `강의덱_발표자노트.html`을 다시 만든다.

사용: python plans/FRAME-길이별-조립/build_notes.py [--check]

입력(전부 `courses/AI_에이전트_실습워크숍_4시간/sessions/1주차/` 아래)
  1주차_초안.md                      표 행 `| ID | 제목 | 화면 본문 | 강사 멘트 |`
  강의덱.초안/variants/4h.txt         장 순서와 블록
  강의덱.초안/variants/minutes.tsv    장별 분
  강의덱_발표자노트.html              머리(<head> · 범례)를 그대로 물려받는다

멘트 칸 표기(초안 생성 때의 관례를 거꾸로 읽는다)
  **머리말** 문장 …   → 🎙 전체 대본        👀 …  → 시연·관찰     💬 …  → 애드리브
  ⚠ (강사 확인) …    → 말하기 전에 확인     🔑 …  → 강사용 확인   🗣 라벨 — 문구 → 막힐 때 힌트
  <!-- refs: … -->    → 출처               그 밖의 줄 → 📌 요점

`--check`는 파일을 쓰지 않고 장수와 미판정(멘트가 빈 장 · 분이 없는 장)만 센다.
종료코드: 0 정상 · 1 초안에 없는 장이 조립표에 있음 · 2 입력 없음.
"""
import html
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = os.path.join(ROOT, "courses", "AI_에이전트_실습워크숍_4시간", "sessions", "1주차")
DRAFT = os.path.join(S, "1주차_초안.md")
MANIFEST = os.path.join(S, "강의덱.초안", "variants", "4h.txt")
MINUTES = os.path.join(S, "강의덱.초안", "variants", "minutes.tsv")
NOTES = os.path.join(S, "강의덱_발표자노트.html")
HUB = "허브 구간"


def mins(m):
    a, b = int(m), m - int(m)
    if a and b:
        return "%d분 30초" % a
    if b:
        return "30초"
    return "%d분" % a


def e(t):
    t = html.escape(t, quote=False)
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", t)


def read_rows():
    rows = {}
    for line in open(DRAFT, encoding="utf-8").read().splitlines():
        if not re.match(r"\|\s*[A-Z0-9][A-Z0-9-]*\s*\|", line):
            continue
        cells = [c.strip().replace("\x00", "|") for c in line.replace("\\|", "\x00").strip().strip("|").split("|")]
        if len(cells) >= 4:
            rows[cells[0]] = (cells[1], cells[3])
    return rows


def read_manifest():
    blocks = []
    for raw in open(MANIFEST, encoding="utf-8").read().splitlines():
        line = raw.strip()
        if not line or line[0] in "#@":
            continue
        if line.startswith("["):
            name, _, what = line[1:-1].partition(" · ")
            blocks.append({"name": name.strip(), "what": what.strip(), "ids": [], "optional": set(), "extra": []})
        elif line.startswith("+"):
            head, _, label = line[1:].partition(" ")
            blocks[-1]["extra"].append((float(head), label.strip()))
        else:
            sid = line.lstrip("?").split()[0]
            blocks[-1]["ids"].append(sid)
            if line.startswith("?"):
                blocks[-1]["optional"].add(sid)
    return blocks


def read_minutes():
    out = {}
    for raw in open(MINUTES, encoding="utf-8").read().splitlines():
        if raw.strip() and not raw.startswith("#"):
            a, b = raw.split("\t")[:2]
            out[a.strip()] = float(b)
    return out


def note_items(ment):
    """멘트 칸 한 개를 노트 블록 HTML로 바꾼다."""
    refs = re.findall(r"<!--\s*refs:\s*(.*?)\s*-->", ment)
    ment = re.sub(r"\s*<!--.*?-->", "", ment)
    out = []
    for part in [p.strip() for p in ment.split("<br>") if p.strip()]:
        if part.startswith("👀"):
            out.append('    <div class="pn-item pn-demo">\n      <span class="lbl">👀 시연·관찰</span>\n      <p>%s</p>\n    </div>' % e(part[1:].strip()))
        elif part.startswith("💬"):
            out.append('    <div class="pn-item pn-joke">\n      <span class="lbl">💬 애드리브</span>\n      <p>%s</p>\n    </div>' % e(part[1:].strip()))
        elif part.startswith("⚠"):
            text = re.sub(r"^⚠\s*(\(강사 확인\))?\s*", "", part)
            out.append('    <div class="pn-item pn-demo pn-caution">\n      <span class="lbl">⚠ 말하기 전에 확인</span>\n      <p>%s</p>\n    </div>' % e(text))
        elif part.startswith("🔑"):
            out.append('    <div class="pn-item pn-demo pn-answer">\n      <span class="lbl">🔑 강사용 확인</span>\n      <p>%s</p>\n    </div>' % e(part[1:].strip()))
        elif part.startswith("🗣"):
            label, _, text = part[1:].strip().partition(" — ")
            out.append('    <div class="pn-item pn-hint">\n      <span class="lbl">🗣 막힐 때 힌트</span>\n      <p class="hlabel">%s</p>\n      <div class="prompt">%s</div>\n    </div>' % (e(label), e(text.replace(" / ", "\n"))))
        elif part.startswith("**"):
            pairs = re.findall(r"\*\*(.+?)\*\*\s*(.*?)(?=\s*\*\*.+?\*\*|$)", part)
            body = "\n".join('      <p><span class="tag">%s</span> %s</p>' % (e(a), e(b.strip())) for a, b in pairs)
            out.append('    <div class="pn-item pn-joke pn-say">\n      <span class="lbl">🎙 전체 대본</span>\n%s\n    </div>' % body)
        else:
            sentences = [s for s in re.split(r"(?<=[다요]\.)\s+", part) if s]
            body = "\n".join("        <li>%s</li>" % e(s) for s in sentences)
            out.append('    <div class="pn-item pn-joke pn-say">\n      <span class="lbl">📌 요점</span>\n      <ul>\n%s\n      </ul>\n    </div>' % body)
    for r in refs:
        out.append('    <p class="pn-refs">출처: %s</p>' % e(r))
    return "\n".join(out)


def main():
    check = "--check" in sys.argv[1:]
    for p in (DRAFT, MANIFEST, MINUTES, NOTES):
        if not os.path.isfile(p):
            print("입력 없음:", os.path.relpath(p, ROOT))
            return 2
    rows, blocks, minutes = read_rows(), read_manifest(), read_minutes()
    order = [sid for b in blocks for sid in b["ids"]]
    missing = [sid for sid in order if sid not in rows]
    if missing:
        print("초안에 없는 장:", ", ".join(missing))
        return 1
    empty = [sid for sid in order if not rows[sid][1].strip()]
    no_min = [sid for b in blocks if b["name"] != HUB for sid in b["ids"] if sid not in minutes]
    scripts = sum(1 for sid in order if rows[sid][1].lstrip().startswith("**"))
    pos = {sid: n + 1 for n, sid in enumerate(order)}
    total = len(order)

    old = open(NOTES, encoding="utf-8").read()
    head = old[:old.index('<p class="pn-note">')]
    o = [head.rstrip("\n")]
    o.append('    <p class="pn-note">강사용 참고 문서입니다. 쪽 번호는 덱의 장 순서와 같고, 덱은 %d장입니다. %d장 모두에 노트가 있습니다(표지는 쪽 번호가 없어 「표지」로 표시).</p>' % (total, total))
    o.append('    <p class="pn-note">개념 장 %d장은 전체 대본(🎙)이고, 나머지는 요점(📌)입니다. 대본은 화면의 정의 → 비유 → 근거 → 대응 순서를 따르므로 그대로 읽어도 됩니다.</p>' % scripts)
    keep = re.findall(r'    <p class="pn-note">(?:수강생 화면|실습은 일곱).*?</p>\n', old)
    o.extend(k.rstrip("\n") for k in keep)
    legend = re.search(r'    <div class="pn-legend">.*?</div>\n', old, re.S)
    o.append(legend.group(0).rstrip("\n"))
    o.append('    <table class="pn-blocks">\n      <tr><th>구간</th><th>쪽</th><th>장 합계</th><th>내용</th></tr>')
    sums = {}
    for b in blocks:
        a, z = pos[b["ids"][0]], pos[b["ids"][-1]]
        base = sum(minutes.get(sid, 0) for sid in b["ids"] if sid not in b["optional"])
        extra = sum(x for x, _ in b["extra"])
        if b["name"] == HUB:
            label = "실습 하나에 47분(개념 장이 있는 실습은 2분이 더 있음)"
        elif extra:
            label = "%s(본 장 %s + %s)" % (mins(base + extra), mins(base), " · ".join("%s %s" % (l, mins(x)) for x, l in b["extra"]))
        else:
            label = mins(base)
        sums[b["name"]] = label
        o.append("      <tr><td>%s</td><td>%d~%d쪽</td><td>%s</td><td>%s</td></tr>" % (b["name"], a, z, e(label), e(b["what"])))
    o.append("    </table>")
    o.append('    <p class="pn-note">블록 상한은 55분이고(2026-10-06 조정), 휴식 10분 세 번은 시간표 밖입니다. 늦어지면 강사 시연 두 장(D-01 · D-02)을 건너뜁니다.</p>')
    o.append("  </header>\n")
    for b in blocks:
        o.append('  <div class="pn-block">%s · %d~%d쪽 · %s</div>' % (b["name"], pos[b["ids"][0]], pos[b["ids"][-1]], e(sums[b["name"]])))
        cum = 0.0
        for sid in b["ids"]:
            title, ment = rows[sid]
            m = minutes.get(sid, 0)
            if sid.startswith("BR-"):
                t = "%s · 휴식 10분(시간표 밖)" % b["name"]
            elif b["name"] == HUB:
                t = "허브 구간 · 이 장 %s" % mins(m) if m else "허브 구간"
            elif sid in b["optional"]:
                t = "%s · 이 장 %s · 시간이 남을 때만" % (b["name"], mins(m))
            else:
                cum += m
                t = "%s · 이 장 %s · 누적 %s" % (b["name"], mins(m), mins(cum))
            no = pos[sid]
            title = re.sub(r"<br\s*/?>", " ", title)
            if sid == "COVER":
                o.append('  <section class="pn-pre" id="p%d">\n    <div class="pn-pre-head">\n      <span class="pn-pre-tag">표지</span>\n      <span class="pn-id">%s</span>\n      <h3 class="pn-pre-title">%s</h3>\n      <span class="pn-time">%s</span>\n    </div>\n%s\n  </section>\n' % (no, sid, e(title), t, note_items(ment)))
            else:
                o.append('  <section class="pn-slide" id="p%d">\n    <div class="pn-slide-head">\n      <span class="pn-no">%d</span>\n      <span class="pn-id">%s</span>\n      <h2 class="pn-slide-title">%s</h2>\n      <span class="pn-time">%s</span>\n    </div>\n%s\n  </section>\n' % (no, no, sid, e(title), t, note_items(ment)))
    o.append("</div>\n</body>\n</html>\n")
    if not check:
        open(NOTES, "w", encoding="utf-8", newline="\n").write("\n".join(o))
    print("RESULT 노트 %d장 · 전체 대본 %d장 · 미판정 %d건(멘트 빈 장 %d · 분 없는 장 %d)%s" % (
        total, scripts, len(empty) + len(no_min), len(empty), len(no_min), " · 쓰지 않음(--check)" if check else ""))
    if empty:
        print("  멘트 빈 장:", ", ".join(empty))
    if no_min:
        print("  분 없는 장:", ", ".join(no_min))
    return 0


if __name__ == "__main__":
    sys.exit(main())
