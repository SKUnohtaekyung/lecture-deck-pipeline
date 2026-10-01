# -*- coding: utf-8 -*-
"""E9 발표자 노트 HTML 조립기.

입력: 1주차_초안.md(행 순서 = 쪽 번호) · 결정표.md(분) · notes_data.py(손으로 쓴 대본·요점)
출력: sessions/1주차/강의덱_발표자노트.html (--out 으로 바꿀 수 있다)
부수: 숫자·출처 ID 대조 결과(stdout). 표준 라이브러리만.
"""
import html as H
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from parse_draft import ROOT, read_draft, read_decide  # noqa: E402
from notes_data import D  # noqa: E402

OUT = ROOT / "courses/AI_에이전트_실습워크숍_4시간/sessions/1주차/강의덱_발표자노트.html"
CONCEPT_NOTE = ROOT / "courses/AI_에이전트_실습워크숍_4시간/sessions/1주차/자료/개념노트.md"
SOURCES = ROOT / "courses/AI_에이전트_실습워크숍_4시간/sessions/1주차/자료/출처.md"

BLOCK_LABEL = {"1": "블록 1", "2": "블록 2", "3": "블록 3", "4": "블록 4", "허브": "허브 구간"}
FORBID_IN_PRACTICE = ["중간 유실", "환각", "아첨", "컨텍스트", "하네스", "인젝션", "자동화 편향",
                      "외주화", "토큰", "지식 마감일", "규칙 파일", "다음 말 예측"]


# ───────────── 표기 ─────────────
def fmt_min(m):
    whole = int(m)
    sec = int(round((m - whole) * 60))
    if whole == 0 and sec:
        return f"{sec}초"
    if sec:
        return f"{whole}분 {sec}초"
    return f"{whole}분"


def inline(text):
    """`코드` · **굵게**만 지원. 나머지는 이스케이프."""
    out = []
    parts = text.split("`")
    for i, seg in enumerate(parts):
        if i % 2 == 1:
            out.append("<code>" + H.escape(seg, quote=False) + "</code>")
        else:
            e = H.escape(seg, quote=False)
            e = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", e)
            out.append(e)
    return "".join(out)


def clean(s):
    return re.sub(r"\s+", " ", s.replace("<br>", " ")).strip()


# ───────────── 초안 멘트 칸 분해 ─────────────
def parse_cue(cue):
    refs = None
    m = re.search(r"<!--\s*refs:\s*(.*?)\s*-->", cue)
    if m:
        refs = m.group(1).strip()
        cue = cue[:m.start()] + cue[m.end():]
    if refs in ("-", ""):
        refs = None
    cue = cue.replace("<br>", "\n")
    pieces = re.split(r"(👀|💬|🗣)", cue)
    pre = clean(pieces[0])
    segs = {"👀": [], "💬": [], "🗣": []}
    for i in range(1, len(pieces), 2):
        t = clean(pieces[i + 1])
        if t:
            segs[pieces[i]].append(t)
    return {"pre": pre, "demo": segs["👀"], "joke": segs["💬"], "hint": segs["🗣"], "refs": refs}


def parse_hint(t):
    """🗣 한 덩어리 → dict(label, lines|text, mono)"""
    m = re.search(r" — |: ", t)
    if not m:
        return {"label": "", "text": t, "mono": False}
    label, rest = t[:m.start()].strip(), t[m.end():].strip()
    mono = ("완성" in label) or ("카드 예시" in label)
    if not mono:
        return {"label": label, "text": rest, "mono": False}
    if "카드 예시" in label:
        lines = [x.strip() for x in rest.split(" / ")]
    else:
        lines = [rest]
        for key in (" 변경: ", " 확인: ", " 어디서: ", " 보이는 것: ", " 원인을 먼저"):
            nxt = []
            for ln in lines:
                if key in ln:
                    a, b = ln.split(key, 1)
                    nxt += [a, key.strip() + (" " if key.strip().endswith(":") else "") + b]
                else:
                    nxt.append(ln)
            lines = nxt
        lines = [x.strip() for x in lines]
    return {"label": label, "lines": lines, "mono": True}


def pex_answer(screen):
    for ln in screen.split("<br>"):
        ln = ln.strip()
        if ln.startswith("[펼침]"):
            return clean(ln[len("[펼침]"):])
    return None


# ───────────── 조립 ─────────────
def item(cls, label, body, extra=""):
    return (f'    <div class="pn-item {cls}">\n'
            f'      <span class="lbl">{label}</span>\n{body}'
            f'    </div>\n')


def ps(texts, cls=""):
    c = f' class="{cls}"' if cls else ""
    return "".join(f"      <p{c}>{inline(t)}</p>\n" for t in texts)


def build():
    rows = read_draft()
    dec = read_decide()
    assert [r["id"] for r in rows] == list(dec), "초안과 결정표의 장 순서가 다르다"
    missing = [r["id"] for r in rows if r["id"] not in D]
    extra = [k for k in D if k not in dec]
    assert not missing and not extra, (missing, extra)

    note_txt = CONCEPT_NOTE.read_text(encoding="utf-8")
    src_txt = SOURCES.read_text(encoding="utf-8")

    # 블록 범위 · 합계
    blocks = {}
    for i, r in enumerate(rows):
        b = dec[r["id"]]["block"]
        e = blocks.setdefault(b, {"first": i + 1, "last": i + 1, "sum": 0.0})
        e["last"] = i + 1
        e["sum"] += dec[r["id"]]["min"]

    problems = []
    stats = {"notes": 0, "scripts": 0, "demo": 0, "joke": 0, "hint": 0, "answer": 0, "caution": 0}
    body = []
    cum = {}
    seen_block = set()

    for i, r in enumerate(rows):
        no = i + 1
        rid = r["id"]
        meta = dec[rid]
        d = D[rid]
        cue = parse_cue(r["cue"])
        is_concept = rid.startswith("C-")

        # 블록 머리
        b = meta["block"]
        if b not in seen_block:
            seen_block.add(b)
            e = blocks[b]
            if b == "허브":
                desc = (f"{BLOCK_LABEL[b]} · {e['first']}~{e['last']}쪽 · 슬롯 A·B에서 강사가 고른 실습 1개를 "
                        f"진행합니다(허브 1분 + 실습 14분 = 슬롯 15분). 행 합계 {fmt_min(e['sum'])}는 실습 4개를 모두 더한 값입니다.")
            else:
                br = "" if b == "4" else " · 블록 뒤 휴식 10분(시간표 밖)"
                desc = (f"{BLOCK_LABEL[b]} · {e['first']}~{e['last']}쪽 · 행 합계 {fmt_min(e['sum'])}(블록 상한 50분){br}")
            body.append(f'  <div class="pn-block">{H.escape(desc, quote=False)}</div>\n')

        # 시간 표기
        mins = meta["min"]
        if b in ("1", "2", "3", "4") and mins > 0:
            cum[b] = cum.get(b, 0.0) + mins
            tm = f"{BLOCK_LABEL[b]} · 이 장 {fmt_min(mins)} · 누적 {fmt_min(cum[b])}"
        elif rid.startswith("BR-"):
            tm = f"{BLOCK_LABEL[b]} 끝 · 휴식 10분(시간표 밖)"
        elif b == "허브":
            tm = f"허브 구간 · 이 장 {fmt_min(mins)}"
        else:
            tm = f"{BLOCK_LABEL[b]} · 이 장 {fmt_min(mins)}"

        items = []
        # 1) 대본 / 요점
        if is_concept:
            paras = "".join(
                f'      <p><span class="tag">{H.escape(lb, quote=False)}</span> {inline(tx)}</p>\n'
                for lb, tx in d["say"])
            items.append(item("pn-joke pn-say", "🎙 전체 대본", paras))
            stats["scripts"] += 1
            say_texts = [tx for _, tx in d["say"]]
        else:
            lis = "".join(f"        <li>{inline(t)}</li>\n" for t in d["say"])
            items.append(item("pn-joke pn-say", "📌 요점", f"      <ul>\n{lis}      </ul>\n"))
            say_texts = list(d["say"])

        # 2) 시연·관찰 + 강사용 정답(👀 안에 묶여 있는 것)
        if is_concept and "demo" not in d:
            problems.append(f"{rid}: 개념 장은 demo를 직접 지정해야 한다")
        demo_src = d["demo"] if "demo" in d else cue["demo"]
        demos, answers = [], []
        for t in demo_src:
            if "강사용 정답:" in t:
                a, b2 = t.split("강사용 정답:", 1)
                if a.strip():
                    demos.append(a.strip())
                answers.append(b2.strip())
            else:
                demos.append(t)
        if demos:
            items.append(item("pn-demo", "👀 시연·관찰", ps(demos)))
            stats["demo"] += len(demos)

        # 2-2) 화면에서 칸을 눌러 읽는 예시 결과 글(M1-1) — 화면 본문 그대로
        if rid == "M1-1":
            ex = [clean(x) for x in r["screen"].split("<br>")]
            ex = [x for x in ex if re.match(r"^(내 생각 먼저|AI 먼저) · (확인하고 씀|그대로 씀) — ", x)]
            assert len(ex) == 4, ex
            items.append(item("pn-demo", "👀 읽을 예시 글(화면과 같음)", ps(ex)))
            stats["demo"] += len(ex)

        # 3) 애드리브
        joke_src = d["joke"] if "joke" in d else cue["joke"]
        if joke_src:
            items.append(item("pn-joke", "💬 애드리브", ps(joke_src)))
            stats["joke"] += len(joke_src)

        # 4) 정답
        pa = pex_answer(r["screen"])
        ans_blocks = []
        for a in answers:
            ans_blocks.append(("강사용 정답", a))
        if pa:
            ans_blocks.append(("화면에 펼쳐지는 정답", pa))
        for lab, a in ans_blocks:
            items.append(item("pn-demo pn-answer", "🔑 정답",
                              f"      <p><strong>{lab}</strong> {inline(a)}</p>\n"))
            stats["answer"] += 1

        # 5) 확인 주의
        if d.get("caution"):
            items.append(item("pn-demo pn-caution", "⚠ 말하기 전에 확인", ps(d["caution"])))
            stats["caution"] += len(d["caution"])

        # 6) 힌트
        for h in cue["hint"]:
            ph = parse_hint(h)
            if ph["mono"]:
                prompt = "\n".join(ph["lines"])
                inner = (f'      <p class="hlabel">{inline(ph["label"])}</p>\n'
                         f'      <div class="prompt">{inline(prompt)}</div>\n')
            else:
                lab = f"<strong>{inline(ph['label'])}</strong> " if ph["label"] else ""
                inner = f"      <p>{lab}{inline(ph['text'])}</p>\n"
            items.append(item("pn-hint", "🗣 막힐 때 힌트", inner))
            stats["hint"] += 1

        refs = cue["refs"]
        if refs:
            refs = " · ".join(x for x in re.split(r"[,\s]+", refs) if x)
        refs_html = (f'    <p class="pn-refs">출처 ID: {H.escape(refs, quote=False)}</p>\n' if refs else "")

        body.append(
            f'  <section class="pn-slide" id="p{no}">\n'
            f'    <div class="pn-slide-head">\n'
            f'      <span class="pn-no">{no}</span>\n'
            f'      <span class="pn-id">{H.escape(rid, quote=False)}</span>\n'
            f'      <h2 class="pn-slide-title">{H.escape(r["title"], quote=False)}</h2>\n'
            f'      <span class="pn-time">{H.escape(tm, quote=False)}</span>\n'
            f'    </div>\n' + "".join(items) + refs_html + '  </section>\n\n')
        stats["notes"] += 1

        # ── 대조 ──
        row_pool = r["screen"] + " " + r["cue"]
        authored = list(say_texts) + list(d.get("caution", [])) + (d["demo"] if "demo" in d else []) + (d["joke"] if "joke" in d else [])
        for t in authored:
            for n in set(re.findall(r"\d[\d,]*(?:\.\d+)?", t)):
                n2 = n.rstrip(",")
                if n2 in row_pool:
                    continue
                if n2 in note_txt or n2 in src_txt or n2 in str(meta):
                    problems.append(f"{rid}: 숫자 {n2} — 초안 행에는 없고 개념노트·출처·결정표에 있음(확인)")
                else:
                    problems.append(f"{rid}: 숫자 {n2} — 어디에도 없음 ← 수정 필요")
            for sid in set(re.findall(r"S\d\d", t)):
                if sid not in row_pool:
                    problems.append(f"{rid}: 출처 {sid} — 초안 행에 없음")
        if meta["kind"] in ("실습", "메인", "허브", "전환"):
            full = " ".join(authored + cue["demo"] + cue["joke"] + cue["hint"])
            for w in FORBID_IN_PRACTICE:
                if w in full:
                    problems.append(f"{rid}({meta['kind']}): 개념 이름 「{w}」 누출")

    return "".join(body), stats, problems, blocks


CSS = """
  :root{
    --blue:#0E4A5A; --mint-deep:#0F7A64; --coral-deep:#A15C00; --ink:#14202B;
    --gray-700:#33414E; --gray-400:#56636F; --white:#F6F8FA;
    --surface:#EBF0F4; --line:#D5DDE4; --paper:#EEF4F6;
    --blue-soft:#E6F0F3; --mint-soft:#E4F8FA; --coral-soft:#FEF5E3;
    --r-lg:20px; --r-md:14px; --r-pill:999px;
    --font-mono:"D2Coding","JetBrains Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
    --font:"Pretendard",system-ui,-apple-system,"Malgun Gothic",sans-serif;
  }
  *{ box-sizing:border-box; }
  body{ margin:0; padding:32px 20px 64px; background:var(--paper); color:var(--ink);
    font-family:var(--font); line-height:1.6; -webkit-font-smoothing:antialiased; }
  .pn-wrap{ max-width:840px; margin:0 auto; }

  /* 헤더 */
  .pn-head{ border-bottom:2px solid var(--blue); padding-bottom:16px; margin-bottom:28px; }
  .pn-kicker{ font-size:14px; font-weight:800; color:var(--blue); letter-spacing:.02em; }
  .pn-title{ font-size:30px; font-weight:800; margin:6px 0 4px; }
  .pn-note{ font-size:15px; color:var(--gray-700); margin:0 0 6px; }
  .pn-legend{ display:flex; flex-wrap:wrap; gap:8px; margin-top:14px; }
  .pn-legend span{ font-size:13px; font-weight:700; border-radius:var(--r-pill); padding:4px 11px; border:1px solid var(--line); }
  .lg-say{ background:var(--surface); color:var(--blue); }
  .lg-joke{ background:var(--blue-soft); color:var(--blue); }
  .lg-demo{ background:var(--coral-soft); color:var(--coral-deep); }
  .lg-hint{ background:var(--mint-soft); color:var(--mint-deep); }
  .pn-blocks{ border-collapse:collapse; margin-top:14px; font-size:14px; width:100%; }
  .pn-blocks th, .pn-blocks td{ border:1px solid var(--line); padding:5px 10px; text-align:left; background:var(--white); }
  .pn-blocks th{ background:var(--surface); }

  /* 블록 구분 */
  .pn-block{ font-size:14px; font-weight:800; color:var(--blue); background:var(--blue-soft);
    border-radius:var(--r-md); padding:8px 14px; margin:26px 0 12px; }

  /* 슬라이드 블록 */
  .pn-slide{ border:1px solid var(--line); border-radius:var(--r-lg); background:var(--white);
    padding:18px 20px; margin:0 0 16px; break-inside:avoid; }
  .pn-slide-head{ display:flex; flex-wrap:wrap; align-items:baseline; gap:6px 12px; margin-bottom:10px; }
  .pn-no{ flex:0 0 auto; font-size:14px; font-weight:800; color:var(--white); background:var(--blue);
    border-radius:var(--r-pill); padding:3px 11px; }
  .pn-id{ flex:0 0 auto; font-size:13px; font-weight:800; color:var(--blue); background:var(--blue-soft);
    border-radius:var(--r-pill); padding:2px 9px; font-family:var(--font-mono); }
  .pn-slide-title{ font-size:19px; font-weight:800; margin:0; flex:1 1 280px; }
  .pn-time{ flex:0 0 auto; font-size:13px; font-weight:700; color:var(--gray-700); margin-left:auto; }

  /* 멘트 항목 — 종류별 좌측 컬러 바 + 라벨 */
  .pn-item{ border-left:4px solid var(--line); padding:8px 0 8px 14px; margin:8px 0; }
  .pn-item .lbl{ display:inline-block; font-size:12px; font-weight:800; margin-bottom:3px; }
  .pn-item p{ margin:0; font-size:16px; color:var(--gray-700); }
  .pn-item p + p{ margin-top:8px; }
  .pn-item ul{ margin:0; padding-left:20px; font-size:16px; color:var(--gray-700); }
  .pn-item li{ margin:3px 0; }
  .pn-item code{ font-family:var(--font-mono); font-size:14.5px; background:var(--surface); border-radius:6px; padding:0 4px; }
  .pn-item .tag{ display:inline-block; font-size:12px; font-weight:800; color:var(--blue); background:var(--blue-soft);
    border-radius:var(--r-pill); padding:0 8px; margin-right:4px; }
  .pn-joke{ border-left-color:var(--blue); } .pn-joke .lbl{ color:var(--blue); }
  .pn-say{ background:var(--paper); border-radius:0 var(--r-md) var(--r-md) 0; }
  .pn-say p, .pn-say li{ color:var(--ink); }
  .pn-demo{ border-left-color:var(--coral-deep); } .pn-demo .lbl{ color:var(--coral-deep); }
  .pn-answer{ background:var(--coral-soft); border-radius:0 var(--r-md) var(--r-md) 0; }
  .pn-caution{ background:var(--surface); border-radius:0 var(--r-md) var(--r-md) 0; }
  .pn-hint{ border-left-color:var(--mint-deep); background:var(--mint-soft);
    border-radius:0 var(--r-md) var(--r-md) 0; }
  .pn-hint .lbl{ color:var(--mint-deep); }
  .pn-hint .hlabel{ font-size:13px; font-weight:800; color:var(--mint-deep); margin-top:2px; }
  .pn-hint .prompt{ font-family:var(--font-mono); font-size:14.5px; color:var(--ink);
    background:var(--white); border:1px solid var(--line); border-radius:var(--r-md);
    padding:10px 12px; margin-top:4px; white-space:pre-wrap; }
  .pn-refs{ margin:8px 0 0; font-size:12.5px; color:var(--gray-400); }

  @media print{
    body{ background:var(--white); padding:0 8mm; }
    .pn-slide{ box-shadow:none; }
  }
"""


def head_html(blocks, stats):
    rows = []
    desc = {"1": "개념 · 자료 받기 · 문항 쓰기", "2": "결과 글 · 에이전트 실습 A · 점검 화면",
            "3": "화면 수정 · 에이전트 실습 B · 공개 주소", "4": "서로 써 보기 · 고치기 · 시연 · 마무리",
            "허브": "실습 4종(01~04) · 슬롯 A·B에서 1개씩"}
    for b in ("1", "2", "3", "4", "허브"):
        e = blocks[b]
        rows.append(f"      <tr><td>{BLOCK_LABEL[b]}</td><td>{e['first']}~{e['last']}쪽</td>"
                    f"<td>{fmt_min(e['sum'])}</td><td>{desc[b]}</td></tr>")
    return f"""  <header class="pn-head">
    <div class="pn-kicker">발표자 노트 · 1주차</div>
    <h1 class="pn-title">FRAME — AI 에이전트 실습 4시간</h1>
    <p class="pn-note">강사용 참고 문서입니다. 쪽 번호는 덱의 장 순서와 같고, 덱은 82장입니다. 82장 모두에 노트가 있습니다.</p>
    <p class="pn-note">ID가 C-로 시작하는 개념 장 20장은 전체 대본(🎙)이고, 나머지는 요점(📌)입니다. 대본은 화면의 정의 → 비유 → 근거 → 대응 순서를 따르므로 그대로 읽어도 됩니다.</p>
    <p class="pn-note">수강생 화면(덱)에는 💬 애드리브 · 👀 시연 큐 · 🔑 정답이 보이지 않고, 🗣 힌트는 접힌 상태로 들어갑니다. 여기서는 모두 펼쳐 둡니다.</p>
    <div class="pn-legend">
      <span class="lg-say">🎙 전체 대본 · 📌 요점</span>
      <span class="lg-joke">💬 애드리브</span>
      <span class="lg-demo">👀 시연·관찰 큐 · 🔑 강사용 정답 · ⚠ 확인</span>
      <span class="lg-hint">🗣 막힐 때 힌트(수강생 화면엔 접힘)</span>
    </div>
    <table class="pn-blocks">
      <tr><th>구간</th><th>쪽</th><th>행 합계</th><th>내용</th></tr>
{chr(10).join(rows)}
    </table>
    <p class="pn-note">시간은 결정표의 「분」 열 값입니다. 블록 상한은 50분이고, 남는 시간은 여유입니다. 휴식 10분 세 번은 시간표 밖입니다.</p>
  </header>
"""


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else OUT
    body, stats, problems, blocks = build()
    doc = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>발표자 노트 — FRAME 1주차</title>
<!--
  발표자 노트 — FRAME 1주차 (E9)
  형식: kit/starter/presenter-notes-template.html. 덱 82장과 같은 순서이며 pn-no = 덱 쪽 번호.
  · 🎙 전체 대본(개념 장 C-*) · 📌 요점(그 밖의 장)은 class pn-joke pn-say — 발표 런타임에서는 「강사 설명·애드리브」로 읽힌다.
  · 🔑 강사용 정답 · ⚠ 확인은 class pn-demo 와 보조 class(pn-answer · pn-caution)를 함께 쓴다.
  · 🗣는 여기선 펼친 상태. 1280×720 캔버스 제약 없음. deck.css를 링크하지 않는다.
-->
<style>{CSS}</style>
</head>
<body>
<div class="pn-wrap">

{head_html(blocks, stats)}
{body}</div>
</body>
</html>
"""
    out.write_text(doc, encoding="utf-8", newline="\n")
    print(f"쓴 파일: {out}")
    print("통계:", stats)
    print(f"대조 메모 {len(problems)}건")
    for p in problems:
        print("  -", p)


if __name__ == "__main__":
    main()
