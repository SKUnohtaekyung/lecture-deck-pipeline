#!/usr/bin/env python3
"""D1 검사 — 메인 과제 「AI 활용 습관 점검」 페이지(강사용 · 참가자 틀 · 이어가기).

사용: python plans/FRAME-개편/gen/check_d1.py     (표준 라이브러리만 · node가 있으면 교차 검증을 더한다)
종료코드: 0 전부 통과 · 1 실패 또는 미판정(대상 0) 있음.

판정 항목(성공 기준 ①~④ + 보조 ⑤~⑨)
  ① 외부 URL(http) · 외부 요청 API(fetch 등) 0, script/link 경로가 같은 폴더의 파일
  ② content.js를 파싱해 문항 축 배정 · 유형 4개 · 유형 이름(축 값 조합) · 문항.txt/결과글.txt와의 일치
  ③ app.js의 판정 규칙(THRESHOLD · TYPE_OF · CHOICES)을 파일에서 읽어 같은 규칙으로 축당 2·3·4문항 전수 조합의
     4유형 도달을 센다. node가 있으면 app.js의 judge를 실제로 실행해 전수 결과를 대조한다
  ④ 금지 문구(진단 · 당신은) 0 — 시작안내.md는 작성 안내가 금지 문구를 인용하므로 예외로 세어 따로 보인다
  ⑤ style.css: :root 밖 raw hex 0, :root 색 값이 kit/themes/frame/tokens.css와 같다
  ⑥ 화면 기능 문자열(공통 문구 · 다른 유형 결과 보기 · 내려받기 · 복사 · `>` 제거) 존재
  ⑦ index.html: 스크립트 순서(content.js → app.js) · lang · viewport
  ⑧ API 키 패턴 0
  ⑨ 강사용 ↔ 이어가기 3_공개_시작점의 index.html · style.css · app.js 동일, 참가자 틀 구조
  ⑩ 결과 글이 빈 유형이 판정되거나 「다른 유형 결과 보기」로 열릴 때 대체 문구(EMPTY_RESULT) 경로가 app.js에 있다(정적).
     필수 결과 글은 본인 유형 포함 두 유형 — 이어가기는 T1 · T4만 채우고 T2 · T3는 비운다

「미판정」: 이 검사가 볼 수 없는 것(브라우저 렌더 · 375px · 클릭 · 네트워크)은 메인이 실측한다.
대상이 0건인 항목은 통과가 아니라 미판정이며 실패로 센다.
"""
import itertools
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[3]
COURSE = ROOT / "courses" / "AI_에이전트_실습워크숍_4시간" / "sessions" / "1주차"
INSTR = COURSE / "실습자료_강사용" / "00_AI습관점검"
PART = COURSE / "실습자료" / "실습자료_FRAME" / "00_AI습관점검"
RES2 = COURSE / "실습자료" / "실습자료_FRAME" / "이어가기" / "00_AI습관점검" / "2_제작_시작점"
RES3 = COURSE / "실습자료" / "실습자료_FRAME" / "이어가기" / "00_AI습관점검" / "3_공개_시작점"
TOKENS = ROOT / "kit" / "themes" / "frame" / "tokens.css"
FOLDERS = [INSTR, PART, RES2, RES3]
TEXT_SUFFIX = {".html", ".css", ".js", ".md", ".txt"}

NOTE = "내가 쓴 문항으로 만든 자기 점검입니다. 유형은 지금의 습관을 적은 것이고 바뀔 수 있습니다."
AXIS_KO = {"시작": "start", "마무리": "finish"}
TYPE_IDS = ["T1", "T2", "T3", "T4"]
# 설계서 §2 — 유형 = (시작 값, 마무리 값)
DESIGN_TYPE = {"T1": ("high", "high"), "T2": ("low", "high"), "T3": ("high", "low"), "T4": ("low", "low")}
FORBIDDEN = ["진단", "당신은"]
FORBIDDEN_EXEMPT = {"시작안내.md"}

results = []  # (이름, ok, 판정 건수, 미판정 건수, 메모)


class Check:
    def __init__(self, name):
        self.name = name
        self.judged = 0
        self.unjudged = 0
        self.fails = []
        self.notes = []

    def count(self, n=1):
        self.judged += n

    def need(self, cond, msg):
        self.judged += 1
        if not cond:
            self.fails.append(msg)

    def skip(self, n=1):
        self.unjudged += n

    def done(self):
        ok = not self.fails and self.judged > 0
        memo = "; ".join(self.notes)
        if self.judged == 0:
            memo = ("미판정(대상 0) " + memo).strip()
        results.append((self.name, ok, self.judged, self.unjudged, memo, self.fails))


def rel(p):
    try:
        return str(Path(p).relative_to(COURSE)).replace(os.sep, "/")
    except ValueError:
        return str(p)


def read(p):
    return Path(p).read_text(encoding="utf-8")


def text_files(folder):
    out = []
    for dp, _, fns in os.walk(folder):
        for fn in sorted(fns):
            if Path(fn).suffix.lower() in TEXT_SUFFIX:
                out.append(Path(dp) / fn)
    return out


# ───────────────────────── JS 객체 리터럴 → JSON ─────────────────────────
def js_to_obj(src):
    m = re.search(r"window\.CHECK_CONTENT\s*=\s*", src)
    if not m:
        raise ValueError("window.CHECK_CONTENT 대입이 없다")
    s = src[m.end():]
    out = []
    i, n = 0, len(s)
    while i < n:
        ch = s[i]
        if ch == '"':
            j = i + 1
            while j < n:
                if s[j] == "\\":
                    j += 2
                    continue
                if s[j] == '"':
                    break
                j += 1
            out.append(s[i:j + 1])
            i = j + 1
        elif ch == "'":
            raise ValueError("작은따옴표 문자열은 지원하지 않는다")
        elif s.startswith("/*", i):
            i = s.index("*/", i) + 2
        elif s.startswith("//", i):
            k = s.find("\n", i)
            i = n if k < 0 else k
        elif ch.isalpha() or ch == "_":
            j = i
            while j < n and (s[j].isalnum() or s[j] == "_"):
                j += 1
            word = s[i:j]
            k = j
            while k < n and s[k] in " \t\r\n":
                k += 1
            out.append('"%s"' % word if k < n and s[k] == ":" else word)
            i = j
        elif ch == ";":
            break
        elif ch == ",":
            k = i + 1
            while k < n and s[k] in " \t\r\n":
                k += 1
            if k < n and s[k] in "}]":
                i += 1
            else:
                out.append(ch)
                i += 1
        else:
            out.append(ch)
            i += 1
    return json.loads("".join(out))


# ───────────────────────── 텍스트 틀 파서 ─────────────────────────
def parse_questions_txt(path):
    axis = None
    qs, headers, comments = [], [], 0
    for raw in read(path).splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#"):
            comments += 1
            continue
        m = re.match(r"^\[(시작|마무리)\]\s*(.*)$", line)
        if m:
            axis = AXIS_KO[m.group(1)]
            headers.append(m.group(1))
            continue
        if axis is None:
            raise ValueError("축 이름 줄 앞에 문항이 있다: " + line)
        qs.append((axis, line))
    return qs, headers, comments


def parse_results_txt(path):
    blocks, cur, comments = {}, None, 0
    for raw in read(path).splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#"):
            comments += 1
            continue
        m = re.match(r"^\[(T[1-4])\]\s*시작:\s*(.+?)\s*·\s*마무리:\s*(.+)$", line)
        if m:
            cur = {"name": m.group(2) + " · " + m.group(3), "요약": "", "한가지": "", "요청문": ""}
            blocks[m.group(1)] = cur
            continue
        if cur is None:
            raise ValueError("유형 줄 앞에 내용이 있다: " + line)
        for label, key in (("요약", "요약"), ("이번 주 해 볼 한 가지", "한가지"), ("요청문 카드", "요청문")):
            mm = re.match(r"^%s\s*:\s*(.*)$" % re.escape(label), line)
            if mm:
                cur[key] = mm.group(1).strip()
                break
        else:
            raise ValueError("알 수 없는 줄: " + line)
    return blocks, comments


# ───────────────────────── app.js 규칙 읽기 ─────────────────────────
def read_app_rules(app_path):
    src = read(app_path)
    rules = {}
    m = re.search(r"var\s+THRESHOLD\s*=\s*([0-9.]+)\s*;", src)
    rules["threshold"] = float(m.group(1)) if m else None
    tm = re.search(r"var\s+TYPE_OF\s*=\s*\{([^}]*)\}", src)
    type_of = {}
    if tm:
        for k, v in re.findall(r'"([a-z]+,[a-z]+)"\s*:\s*"(T[1-4])"', tm.group(1)):
            type_of[k] = v
    rules["type_of"] = type_of
    cm = re.search(r"var\s+CHOICES\s*=\s*\[(.*?)\];", src, re.S)
    rules["choices"] = (
        [(a, int(b)) for a, b in re.findall(r'label:\s*"([^"]+)"\s*,\s*score:\s*(\d+)', cm.group(1))] if cm else []
    )
    rules["avg_compare"] = bool(re.search(r"sum\s*/\s*count", src)) and bool(re.search(r"avg\s*>=\s*THRESHOLD", src))
    return rules, src


def py_judge(scores_a, scores_b, threshold, type_of):
    """app.js judge와 같은 규칙: 축 평균 >= THRESHOLD 이면 high."""
    def high(sc):
        return len(sc) > 0 and (sum(sc) / len(sc)) >= threshold
    key = ("high" if high(scores_a) else "low") + "," + ("high" if high(scores_b) else "low")
    return type_of[key]


# ───────────────────────── 검사 ─────────────────────────
def check_external():
    c = Check("① 외부 URL · 외부 요청 0")
    pat_url = re.compile(r"http", re.I)
    # CSS url( 은 소문자 그대로만 본다(JS의 URL.createObjectURL(...)은 외부 요청이 아니다)
    pat_api = re.compile(r"\bfetch\s*\(|XMLHttpRequest|sendBeacon|WebSocket|EventSource|@import|(?<![\w.])url\s*\(|\bimport\s*\(")
    files = 0
    for folder in FOLDERS:
        for f in text_files(folder):
            files += 1
            for no, line in enumerate(read(f).splitlines(), 1):
                c.need(not pat_url.search(line), "%s:%d http 포함: %s" % (rel(f), no, line.strip()[:50]))
                c.need(not pat_api.search(line), "%s:%d 외부 요청 API: %s" % (rel(f), no, line.strip()[:50]))
    # index.html의 script/link/img 경로
    for folder in (INSTR, RES3):
        html = read(folder / "index.html")
        refs = re.findall(r'(?:src|href)\s*=\s*"([^"]*)"', html)
        for r in refs:
            if r.startswith("#"):
                continue
            ok = not re.match(r"^([a-z][a-z0-9+.-]*:|//)", r, re.I) and "/" not in r and (folder / r).exists()
            c.need(ok, "%s: 참조 %s 가 같은 폴더의 파일이 아니다" % (rel(folder / "index.html"), r))
    c.notes.append("파일 %d개 · 줄 전수" % files)
    c.done()


def load_content(folder, c):
    p = folder / "content.js"
    try:
        return js_to_obj(read(p))
    except Exception as e:  # noqa: BLE001
        c.need(False, "%s 파싱 실패: %s" % (rel(p), e))
        return None


def type_name(content, tid, type_of):
    for k, v in type_of.items():
        if v == tid:
            a, b = k.split(",")
            return content["axes"]["start"][a] + " · " + content["axes"]["finish"][b]
    return None


def check_content(rules):
    c = Check("② content.js 문항 축 배정 · 유형 4개")
    type_of = rules["type_of"]
    # (폴더, (시작 문항 수, 마무리 문항 수), 텍스트 틀 폴더, 요청문 카드 필수, 결과 글을 채운 유형)
    specs = [
        (INSTR, (4, 4), INSTR, True, set(TYPE_IDS)),
        (RES3, (2, 2), RES2, False, {"T1", "T4"}),  # 이어가기: 두 유형만 채운 최소 완성본
    ]
    for folder, (na, nb), txt_folder, need_prompt, filled in specs:
        data = load_content(folder, c)
        if data is None:
            continue
        label = rel(folder / "content.js")
        axes = data.get("axes", {})
        for ax in ("start", "finish"):
            for k in ("name", "high", "low"):
                c.need(bool(str(axes.get(ax, {}).get(k, "")).strip()), "%s: axes.%s.%s 비어 있음" % (label, ax, k))
        qs = data.get("questions", [])
        assigned = [q for q in qs if q.get("axis") in ("start", "finish") and str(q.get("text", "")).strip()]
        c.need(len(assigned) == len(qs), "%s: 축이 없거나 text가 빈 문항이 있다(%d/%d 배정)" % (label, len(assigned), len(qs)))
        n_start = sum(1 for q in qs if q.get("axis") == "start")
        n_finish = sum(1 for q in qs if q.get("axis") == "finish")
        c.need((n_start, n_finish) == (na, nb), "%s: 축별 문항 수 시작 %d · 마무리 %d (기대 %d/%d)" % (label, n_start, n_finish, na, nb))
        for q in qs:
            c.need(str(q.get("text", "")).rstrip().endswith("다."), "%s: 문항이 「~다.」로 끝나지 않음: %s" % (label, q.get("text")))
        types = data.get("types", {})
        c.need(sorted(types.keys()) == TYPE_IDS, "%s: types 키가 T1~T4가 아님: %s" % (label, sorted(types.keys())))
        names = []
        for tid in TYPE_IDS:
            t = types.get(tid, {})
            pr = str(t.get("prompt", ""))
            if tid in filled:
                c.need(bool(str(t.get("summary", "")).strip()), "%s: %s 요약 비어 있음" % (label, tid))
                c.need(bool(str(t.get("step", "")).strip()), "%s: %s 이번 주 한 가지 비어 있음" % (label, tid))
                c.need(str(t.get("summary", "")).rstrip().endswith("편입니다."), "%s: %s 요약이 「~하는 편입니다.」로 끝나지 않음" % (label, tid))
                if need_prompt:
                    c.need(bool(pr.strip()), "%s: %s 요청문 카드 비어 있음" % (label, tid))
            else:
                c.need(not str(t.get("summary", "")).strip() and not str(t.get("step", "")).strip() and not pr.strip(),
                       "%s: %s는 빈 유형이어야 함(대체 문구 확인용)" % (label, tid))
            c.need(not pr.lstrip().startswith(">"), "%s: %s 요청문이 >로 시작함" % (label, tid))
            names.append(type_name(data, tid, type_of))
        c.need(len(set(names)) == 4 and None not in names, "%s: 유형 이름 4개가 서로 다르지 않음: %s" % (label, names))

        # 텍스트 틀과의 일치
        qtxt, headers, _ = parse_questions_txt(txt_folder / "문항.txt")
        content_q = [(q["axis"], q["text"]) for q in qs]
        c.need(qtxt == content_q, "%s ↔ %s: 문항이 다르다" % (rel(txt_folder / "문항.txt"), label))
        rtxt, _ = parse_results_txt(txt_folder / "결과글.txt")
        c.need(sorted(rtxt.keys()) == TYPE_IDS, "%s: 유형 블록이 T1~T4가 아님" % rel(txt_folder / "결과글.txt"))
        for tid in TYPE_IDS:
            b = rtxt.get(tid)
            t = types.get(tid, {})
            if not b:
                continue
            c.need(b["name"] == names[TYPE_IDS.index(tid)], "%s: %s 머리글 이름 %r ≠ 축 값 조합 %r" % (rel(txt_folder / "결과글.txt"), tid, b["name"], names[TYPE_IDS.index(tid)]))
            c.need(b["요약"] == t.get("summary"), "%s ↔ %s: %s 요약이 다르다" % (rel(txt_folder / "결과글.txt"), label, tid))
            c.need(b["한가지"] == t.get("step"), "%s ↔ %s: %s 이번 주 한 가지가 다르다" % (rel(txt_folder / "결과글.txt"), label, tid))
            c.need(b["요청문"] == str(t.get("prompt", "")).strip(), "%s ↔ %s: %s 요청문이 다르다" % (rel(txt_folder / "결과글.txt"), label, tid))
        c.notes.append("%s: 시작 %d · 마무리 %d 문항, 유형 4개(결과 글 채움 %d · 빈 유형 %d)" % (folder.name, n_start, n_finish, len(filled), 4 - len(filled)))

    # 참가자 틀
    qtxt, headers, comments = parse_questions_txt(PART / "문항.txt")
    c.need(headers == ["시작", "마무리"], "참가자 문항.txt 축 이름 줄이 [시작] [마무리]가 아님: %s" % headers)
    c.need(comments == 3, "참가자 문항.txt 메모 줄이 3줄이 아님(%d)" % comments)
    c.need(qtxt == [], "참가자 문항.txt에 문항이 채워져 있음(%d개)" % len(qtxt))
    rtxt, _ = parse_results_txt(PART / "결과글.txt")
    c.need(sorted(rtxt.keys()) == TYPE_IDS, "참가자 결과글.txt 유형 블록이 T1~T4가 아님")
    for tid in TYPE_IDS:
        b = rtxt.get(tid)
        if b:
            c.need(b["요약"] == "" and b["한가지"] == "" and b["요청문"] == "", "참가자 결과글.txt %s가 비어 있지 않음" % tid)
    # 결과글.txt 메모: 필수 = 본인 유형 포함 두 유형, 나머지와 요청문 카드는 선택
    for f in (INSTR / "결과글.txt", PART / "결과글.txt", RES2 / "결과글.txt"):
        memo = " ".join(ln for ln in read(f).splitlines() if ln.startswith("#"))
        c.need("두 유형" in memo and "꼭" in memo and "선택" in memo and "개선 단계" in memo,
               "%s 메모에 「두 유형은 필수 · 나머지와 요청문 카드는 선택 · 개선 단계」 안내가 없음" % rel(f))
    # 이어가기 결과글.txt: 두 유형만 채움
    rr, _ = parse_results_txt(RES2 / "결과글.txt")
    filled_txt = sorted(t for t, b in rr.items() if b["요약"] and b["한가지"])
    c.need(filled_txt == ["T1", "T4"], "2_제작_시작점 결과글.txt 채운 유형이 T1 · T4가 아님: %s" % filled_txt)
    # 머리글 이름이 강사용 content.js의 축 값 조합과 같다
    inst = load_content(INSTR, c)
    if inst is not None:
        for tid in TYPE_IDS:
            if tid in rtxt:
                c.need(rtxt[tid]["name"] == type_name(inst, tid, type_of), "참가자 결과글.txt %s 머리글 이름이 축 값 조합과 다름" % tid)
    # 시작안내.md
    guide = read(PART / "시작안내.md")
    c.need("1.75" in guide, "시작안내.md에 판정 기준 1.75가 없음")
    c.need("## 진단처럼 쓰지 않기" in guide, "시작안내.md에 「진단처럼 쓰지 않기」 절이 없음")
    sec = guide.split("## 진단처럼 쓰지 않기", 1)[-1].split("\n## ", 1)[0]
    bullets = [ln for ln in sec.splitlines() if ln.strip().startswith("- ")]
    c.need(len(bullets) == 3, "시작안내.md 「진단처럼 쓰지 않기」 점검 줄이 3개가 아님(%d)" % len(bullets))
    c.need("~하는 편입니다" in guide, "시작안내.md에 「~하는 편입니다」 안내가 없음")
    c.need("최소 완성 기준" in guide, "시작안내.md에 최소 완성 기준이 없음")
    c.need("두 유형" in guide and "선택" in guide and "개선 단계" in guide, "시작안내.md에 결과 글 필수(두 유형) · 선택 안내가 없음")
    c.need("아직 쓰지 않은 결과입니다" in guide, "시작안내.md에 빈 유형 화면 문구 안내가 없음")
    c.done()


def enum_types(na, nb, threshold, type_of):
    counts = {t: 0 for t in TYPE_IDS}
    seq = []
    for combo in itertools.product(range(4), repeat=na + nb):
        t = py_judge(combo[:na], combo[na:], threshold, type_of)
        counts[t] += 1
        seq.append(t[1])
    return counts, "".join(seq)


NODE_SCRIPT = r"""
const vm = require("vm"), fs = require("fs");
const w = {};
vm.runInNewContext(fs.readFileSync(process.argv[1], "utf8"), { window: w });
const judge = w.CHECK_APP.judge;
const out = [];
for (const na of [2, 3, 4]) for (const nb of [2, 3, 4]) {
  const n = na + nb;
  const q = [];
  for (let i = 0; i < na; i++) q.push({ axis: "start" });
  for (let i = 0; i < nb; i++) q.push({ axis: "finish" });
  const total = Math.pow(4, n);
  let s = "";
  for (let k = 0; k < total; k++) {
    const a = new Array(n);
    let x = k;
    for (let i = n - 1; i >= 0; i--) { a[i] = x % 4; x = Math.floor(x / 4); }
    s += judge(q, a).type.charAt(1);
  }
  out.push(na + " " + nb + " " + s);
}
console.log(out.join("\n"));
"""


def check_judge(rules):
    c = Check("③ 판정 규칙 동일 · 축당 2·3·4문항 전수 조합 4유형 도달")
    th, type_of = rules["threshold"], rules["type_of"]
    c.need(th == 1.75, "THRESHOLD가 1.75가 아님: %r" % th)
    c.need(type_of == {"%s,%s" % v: k for k, v in DESIGN_TYPE.items()}, "TYPE_OF가 설계서 §2와 다름: %s" % type_of)
    c.need(rules["choices"] == [("거의 없다", 0), ("가끔", 1), ("자주", 2), ("거의 항상", 3)], "CHOICES가 설계서 §3과 다름: %s" % rules["choices"])
    c.need(rules["avg_compare"], "app.js가 「sum / count」와 「avg >= THRESHOLD」 평균 비교를 쓰지 않음")
    if th is None or not type_of:
        c.done()
        return
    # 경계: 2문항 합 3=낮음 · 4=높음 / 4문항 합 6=낮음 · 7=높음
    def high(n, total):
        return total / n >= th
    c.need(not high(2, 3) and high(2, 4), "2문항 경계(3 낮음 · 4 높음)가 맞지 않음")
    c.need(not high(4, 6) and high(4, 7), "4문항 경계(6 낮음 · 7 높음)가 맞지 않음")
    py_seq = {}
    for na in (2, 3, 4):
        for nb in (2, 3, 4):
            counts, seq = enum_types(na, nb, th, type_of)
            py_seq[(na, nb)] = seq
            c.need(all(v > 0 for v in counts.values()), "시작 %d · 마무리 %d 문항: 도달하지 못한 유형 있음 %s" % (na, nb, counts))
            c.need(py_judge((3,) * na, (3,) * nb, th, type_of) == "T1", "전부 최고점이 T1이 아님(%d,%d)" % (na, nb))
            c.need(py_judge((0,) * na, (0,) * nb, th, type_of) == "T4", "전부 0점이 T4가 아님(%d,%d)" % (na, nb))
            c.notes.append("(%d,%d) %s" % (na, nb, " ".join("%s %d" % (t, counts[t]) for t in TYPE_IDS)))
    # 최소 · 최대 문항 수(2·4)의 4유형 계수를 별도로 요약
    # node로 app.js judge를 실제 실행해 같은 전수 결과인지 대조한다
    node = shutil.which("node")
    if node:
        try:
            r = subprocess.run([node, "-e", NODE_SCRIPT, str(INSTR / "app.js")], capture_output=True, text=True, encoding="utf-8", timeout=60)
            if r.returncode != 0:
                c.need(False, "node 실행 실패: %s" % r.stderr.strip()[:120])
            else:
                got = {}
                for ln in r.stdout.strip().splitlines():
                    a, b, s = ln.split(" ")
                    got[(int(a), int(b))] = s
                for key, seq in py_seq.items():
                    c.need(got.get(key) == seq, "node(app.js judge) ≠ python 전수 결과 %s" % (key,))
                c.notes.append("node 교차 검증 %d개 조합 대조" % len(py_seq))
        except Exception as e:  # noqa: BLE001
            c.skip()
            c.notes.append("node 교차 검증 미실행(%s)" % e)
    else:
        c.skip()
        c.notes.append("node 교차 검증 미실행(node 없음)")
    c.done()


def check_forbidden():
    c = Check("④ 금지 문구(진단 · 당신은) 0")
    exempt_hits = []
    for folder in FOLDERS:
        for f in text_files(folder):
            for no, line in enumerate(read(f).splitlines(), 1):
                hit = [w for w in FORBIDDEN if w in line]
                if f.name in FORBIDDEN_EXEMPT:
                    if hit:
                        exempt_hits.append("%s:%d" % (f.name, no))
                    continue
                c.need(not hit, "%s:%d 금지 문구 %s: %s" % (rel(f), no, hit, line.strip()[:50]))
            c.count()
    c.notes.append("예외 %s — 작성 안내가 금지 문구를 인용하는 줄 %d건(%s)" % (",".join(sorted(FORBIDDEN_EXEMPT)), len(exempt_hits), " ".join(exempt_hits)))
    c.done()


def parse_root_colors(css):
    m = re.search(r":root\s*\{(.*?)\n\}", css, re.S)
    body = m.group(1) if m else ""
    return body, dict(re.findall(r"(--[a-z0-9-]+)\s*:\s*(#[0-9A-Fa-f]{3,8})\s*;", body)), (css[: m.start()] + css[m.end():] if m else css)


def check_css():
    c = Check("⑤ style.css 색은 토큰만 · 값은 tokens.css와 같다")
    css = read(INSTR / "style.css")
    body, colors, rest = parse_root_colors(css)
    c.need(bool(body), ":root 블록이 없음")
    hexes = re.findall(r"#[0-9A-Fa-f]{3,8}\b", re.sub(r"/\*.*?\*/", "", rest, flags=re.S))
    c.need(not hexes, ":root 밖 raw hex %d건: %s" % (len(hexes), hexes[:5]))
    tokens = dict(re.findall(r"(--[a-z0-9-]+)\s*:\s*(#[0-9A-Fa-f]{3,8})\s*;", read(TOKENS)))
    shared = 0
    for name, val in colors.items():
        if name in tokens:
            shared += 1
            c.need(val.upper() == tokens[name].upper(), "%s: %s ≠ tokens.css %s" % (name, val, tokens[name]))
    for must in ("--blue", "--mint", "--white", "--ink"):
        c.need(must in colors, "%s 가 :root에 없음" % must)
    c.need(colors.get("--blue", "").upper() == "#0E4A5A" and colors.get("--mint", "").upper() == "#7DE0EC"
           and colors.get("--white", "").upper() == "#F6F8FA" and colors.get("--ink", "").upper() == "#14202B",
           "페트롤 · 아쿠아 · 배경 · 본문 값이 지시와 다름")
    # 아쿠아는 글자 색으로 쓰지 않는다: `color: var(--mint)` 는 어두운 면 위 기호(.prompt)만 허용
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", rest):
        sel, decl = m.group(1).strip(), m.group(2)
        if re.search(r"(?<![-\w])color\s*:\s*var\(--mint\)", decl):
            c.need(sel in (".prompt",), "아쿠아가 글자 색으로 쓰임: %s" % sel)
    # index.html · app.js의 raw hex
    for f in (INSTR / "index.html", INSTR / "app.js"):
        h = re.findall(r"#[0-9A-Fa-f]{6}\b|#[0-9A-Fa-f]{3}\b", read(f))
        c.need(not h, "%s에 raw hex %s" % (rel(f), h[:3]))
    c.notes.append(":root 색 %d개 중 tokens.css 대조 %d개" % (len(colors), shared))
    c.done()


def check_features(app_src):
    c = Check("⑥ 화면 기능 문자열")
    c.need(NOTE in app_src, "공통 문구가 app.js에 없음")
    for s in ("다른 유형 결과 보기", "결과 내려받기", "new Blob(", "a.download", "navigator.clipboard.writeText", "execCommand(\"copy\")", "\"복사\""):
        c.need(s in app_src, "app.js에 %r 없음" % s)
    c.need(r"replace(/^\s*>\s?/" in app_src, "요청문 앞 `>` 제거가 app.js에 없음")
    c.need("copyText(text," in app_src, "복사가 정리된 text(> 없음)를 쓰지 않음")
    c.need('aria-expanded' in app_src and 'role", "alert"' in app_src, "접근성 속성(aria-expanded · alert)이 없음")
    c.need("type = \"radio\"" in app_src or "type=\"radio\"" in app_src, "라디오 입력이 없음(키보드 조작)")
    css = read(INSTR / "style.css")
    c.need(":focus-visible" in css, "style.css에 :focus-visible 없음")
    c.need("font-family: var(--font-sans)" in css and "system-ui" in css, "시스템 글꼴 스택이 없음")
    c.need("overflow-wrap" in css and "minmax(0, 1fr)" in css, "가로 넘침 방지 규칙(overflow-wrap · minmax(0,1fr))이 없음")
    c.done()


def check_empty_path(app_src):
    c = Check("⑩ 결과 글이 빈 유형 → 대체 문구 경로(정적)")
    msg = "아직 쓰지 않은 결과입니다. 결과 글을 채우면 이 자리에 나옵니다."
    c.need('var EMPTY_RESULT = "%s";' % msg in app_src, "EMPTY_RESULT 상수가 지시 문구와 다름")
    c.need("function hasResult(" in app_src and "function typeData(" in app_src, "hasResult · typeData 함수가 없음")
    # 판정 결과 화면 · 다른 유형 영역 · 내려받기 본문 세 경로에서 모두 쓴다(정의 1 + 사용 3)
    c.need(len(re.findall(r"\bEMPTY_RESULT\b", app_src)) >= 4, "EMPTY_RESULT 사용 경로가 3곳(결과 · 다른 유형 · 내려받기)이 아님")
    c.need(len(re.findall(r"\bhasResult\(", app_src)) >= 4, "hasResult 분기가 3곳(결과 · 다른 유형 · 내려받기)이 아님")
    c.need(app_src.count("c.types[") == 1, "typeData 밖에서 c.types[...]를 직접 읽음(키가 없으면 오류) %d곳" % app_src.count("c.types["))
    c.need(".summary(요약)가 비어" not in app_src and ".step(이번 주 해 볼 한 가지)가 비어" not in app_src, "validate()가 빈 결과 글을 오류로 막음")
    c.need(re.search(r'^      resultView\.appendChild\(el\("p", "note", NOTE\)\);', app_src, re.M) is not None,
           "공통 문구가 showResult 최상위 줄에서 붙지 않음(빈 유형일 때 빠질 수 있음)")
    c.need(".empty-result" in read(INSTR / "style.css"), "style.css에 .empty-result 없음")
    c.done()


def check_index():
    c = Check("⑦ index.html 구조")
    for folder in (INSTR, RES3):
        html = read(folder / "index.html")
        name = rel(folder / "index.html")
        c.need('<html lang="ko">' in html, "%s: lang=ko 없음" % name)
        c.need('name="viewport"' in html, "%s: viewport 없음" % name)
        a, b = html.find('src="content.js"'), html.find('src="app.js"')
        c.need(0 < a < b, "%s: content.js → app.js 순서가 아님" % name)
    c.done()


def check_keys():
    c = Check("⑧ API 키 패턴 0")
    pat = re.compile(r"sk-[A-Za-z0-9]{8,}|api[_-]?key|apikey|secret|bearer |authorization|AIza[0-9A-Za-z_-]{10,}", re.I)
    for folder in FOLDERS:
        for f in text_files(folder):
            for no, line in enumerate(read(f).splitlines(), 1):
                c.need(not pat.search(line), "%s:%d 키 패턴: %s" % (rel(f), no, line.strip()[:50]))
    c.done()


def check_copies():
    c = Check("⑨ 강사용 ↔ 3_공개_시작점 페이지 동일 · 구조")
    for fn in ("index.html", "style.css", "app.js"):
        c.need((INSTR / fn).read_bytes() == (RES3 / fn).read_bytes(), "%s 가 강사용과 다름" % fn)
    expected = {
        INSTR: {"index.html", "style.css", "app.js", "content.js", "문항.txt", "결과글.txt"},
        PART: {"문항.txt", "결과글.txt", "시작안내.md"},
        RES2: {"문항.txt", "결과글.txt"},
        RES3: {"index.html", "style.css", "app.js", "content.js"},
    }
    for folder, names in expected.items():
        have = {p.name for p in folder.iterdir() if p.is_file()} if folder.exists() else set()
        c.need(have == names, "%s 파일 %s ≠ 기대 %s" % (rel(folder), sorted(have), sorted(names)))
    c.done()


def main():
    missing = [rel(f) for f in FOLDERS if not f.exists()]
    if missing:
        print("FAIL 폴더 없음: %s" % missing)
        print("RESULT FAIL")
        return 1
    rules, app_src = read_app_rules(INSTR / "app.js")
    check_external()
    check_content(rules)
    check_judge(rules)
    check_forbidden()
    check_css()
    check_features(app_src)
    check_index()
    check_keys()
    check_copies()
    check_empty_path(app_src)

    bad = 0
    for name, ok, judged, unjudged, memo, fails in results:
        print("%s %s — 판정 %d건 · 미판정 %d건%s" % ("PASS" if ok else "FAIL", name, judged, unjudged, (" · " + memo) if memo else ""))
        if not ok:
            bad += 1
            for f in fails[:8]:
                print("    - " + f)
            if len(fails) > 8:
                print("    - … 외 %d건" % (len(fails) - 8))
    print("미판정(이 검사 밖): 브라우저 렌더 · 375px 가로 넘침 · 클릭 · 내려받기 · 복사 · 네트워크 탭 — 메인이 실측")
    print("RESULT %s (항목 %d · FAIL %d)" % ("PASS" if bad == 0 else "FAIL", len(results), bad))
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
