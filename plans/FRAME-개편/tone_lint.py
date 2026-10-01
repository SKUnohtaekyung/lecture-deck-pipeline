#!/usr/bin/env python3
"""FRAME 말투 린트 — 금지 7종을 줄 번호와 함께 찾는다(표준 라이브러리만).

사용: python plans/FRAME-개편/tone_lint.py <파일> [<파일> ...]
  .md          코드 펜스(``` · ~~~) 안은 건너뛴다. 제목 줄 = `#` 줄 + 표의 첫 칸.
  .html/.htm   주석·<script>·<style>·태그를 지우고 텍스트 줄로 만든다(원본 줄 번호 유지).
               제목 줄 = h1~h3 안의 텍스트.

금지 7종(사용자 결정 D13)
  SLOGAN     동사구 슬로건 제목(제목 줄, `~고` 연결 + `~기` 끝)
  PERSONIFY  AI 의인화(동료·조수·파트너·비서·부하 직원·AI의 손발)
  HOWTO      「~하는 법」 · 「사용법」 · 「~의 모든 것」
  NUMTITLE   숫자·수사+단위로 시작하는 제목(제목 줄)
  FLIP       뒤집기 대구(「A가 아니라 B」 · 「~것이 아니라」)
  MORAL      끝의 교훈 한 줄 — 휴리스틱(짧은 단정문만 본다. 미탐이 있다)
  ABSTRACT   추상 명사·선언형(「~의 몫입니다」·핵심은·핵심입니다·본질·유일한 기준·열쇠입니다)
「숫자 대비 과장」(예: 5분이 30분을 아낍니다)은 금지로 확정되지 않아 검출하지 않는다.

출력: `파일:줄 [유형] 발췌(40자 이내)` 그리고 마지막 줄 `RESULT ...`.
종료코드: 0 위반 없음 · 1 위반 있음 · 2 판정 0줄(눈먼 0) 또는 입력 읽기 실패.
"""
import html as htmlmod
import re
import sys

TYPES = ["SLOGAN", "PERSONIFY", "HOWTO", "NUMTITLE", "FLIP", "MORAL", "ABSTRACT"]
LABEL = {t: t for t in TYPES}
LABEL["MORAL"] = "MORAL·휴리스틱"

# ---------- 규칙 ----------

# 1) SLOGAN — 제목 줄. 문장 종결이 없고, `~고` 연결 뒤에 `~기`로 끝난다.
def check_slogan(t):
    s = t.strip().rstrip(".!?…~ ")
    if not s.endswith("기"):
        return None
    if re.search(r"(?:니다|어요|아요|세요|해요)$", s):
        return None
    toks = s.replace(",", " ").replace("，", " ").split()
    if len(toks) < 2 or len(toks) > 6:
        return None
    if any(re.search(r"[가-힣]고$", tok) for tok in toks[:-1]):
        return 0
    return None


# 4) NUMTITLE — 제목 줄이 숫자·수사+단위로 시작한다. 단위 뒤에는 조사만 올 수 있다(3개월·3분기 제외).
_NUM_PREFIX = r"(?:딱|단|겨우|단지|오직|고작|총|꼭|약|모두|불과)?\s*"
_NUMERAL = r"(?:\d+(?:[.,]\d+)?|한|두|세|네|다섯|여섯|일곱|여덟|아홉|열|하나|둘|셋|넷|몇)"
_UNIT = (r"(?:가지|군데|곳|개|초|분|시간|단계|원칙|줄|번|문장|장|명|쪽|칸|항목|규칙|점|조각|글자"
         r"|페이지|슬라이드)")
_PART = r"(?:만|이|가|을|를|은|는|의|씩|째|로|마다|까지|부터|짜리|간|이내|에|도|과|와)?"
NUMTITLE_HEAD = re.compile(rf"^{_NUM_PREFIX}{_NUMERAL}\s*{_UNIT}{_PART}(?![가-힣])")
NUMTITLE_MORE = re.compile(rf"^{_NUM_PREFIX}{_NUMERAL}\s*{_UNIT}{_PART}(?![가-힣])(?=\s+\S)")


def check_numtitle(t, allow_bare=True):
    s = re.sub(r"^[\s\"'“”‘’「『\[(]+", "", t)
    s = re.sub(r"^\d+[.)]\s+", "", s)  # 「1. 개요」 같은 절 번호는 벗긴다
    m = (NUMTITLE_HEAD if allow_bare else NUMTITLE_MORE).match(s)
    return 0 if m else None


# 나머지 — 제목·본문 어디서든 찾는다.
GENERAL = [
    ("PERSONIFY", re.compile(
        r"(?:AI|에이전트|모델)\s*(?:의\s*)?(?:동료|손발|팀원)|조수|비서|파트너|부하\s*직원|동료처럼")),
    ("HOWTO", re.compile(
        r"[가-힣]는\s*법(?!칙|률|원|안|적|인|정|규|령|무)|사용법|의\s*모든\s*것")),
    ("FLIP", re.compile(r"(?:이|가|것이|것은)\s*아니라")),
    ("ABSTRACT", re.compile(
        r"의\s*몫(?:입니다|이다|이에요|이며|이고)|몫입니다|핵심(?:은|는|입니다|이다)|본질"
        r"|유일한\s*기준|열쇠(?:입니다|이다|는|가)")),
]


# 6) MORAL — 문단 끝의 짧은 단정문(휴리스틱). 어절 4 이하 · 공백 뺀 18자 이하 · 입니다/이다로 끝 · 숫자 없음.
def moral_text_ok(t):
    if not re.search(r"(?:입니다|이다)[.!]?$", t):
        return False
    if re.search(r"\d", t) or "§" in t:
        return False
    if re.search(r"[.!?…]\s*\S", t):  # 문장이 둘 이상
        return False
    if len(t.replace(" ", "")) > 18 or len(t.split()) > 4:
        return False
    return True


def excerpt(text, start=0, limit=40):
    a = max(0, start - 10)
    pre = 1 if a > 0 else 0
    if len(text) - a <= limit - pre:
        return ("…" if pre else "") + text[a:]
    seg = text[a:a + limit - pre - 1]
    return ("…" if pre else "") + seg + "…"


# ---------- 문서 모델 ----------

class Doc:
    def __init__(self):
        self.judged = 0
        self.fence = 0
        self.empty = 0
        self.script = 0
        self.titles = []   # (줄, 텍스트, allow_bare)
        self.texts = []    # (줄, 텍스트) — 일반 규칙 대상
        self.morals = []   # (줄, 텍스트) — MORAL 후보(문맥 조건 통과분)


def clean_inline(s):
    s = re.sub(r"`[^`]*`", "§", s)
    s = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", s)
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"(\*\*|__|\*|~~)", "", s)
    return re.sub(r"\s+", " ", s).strip()


def strip_comment(s, state):
    out, pos = "", 0
    while True:
        if state:
            j = s.find("-->", pos)
            if j < 0:
                return out, True
            pos, state = j + 3, False
        else:
            i = s.find("<!--", pos)
            if i < 0:
                return out + s[pos:], False
            out += s[pos:i]
            pos, state = i + 4, True


def parse_md(text):
    doc = Doc()
    lines = text.splitlines()
    info = []  # (종류, 텍스트) — 종류: fence·empty·heading·table·list·para
    in_fence, fch, flen, in_comment = False, "", 0, False
    for raw in lines:
        s = raw.strip()
        if in_fence:
            doc.fence += 1
            if re.fullmatch(rf"{re.escape(fch)}{{{flen},}}", s):
                in_fence = False
            info.append(("fence", ""))
            continue
        m = re.match(r"^(`{3,}|~{3,})", s)
        if m:
            in_fence, fch, flen = True, m.group(1)[0], len(m.group(1))
            doc.fence += 1
            info.append(("fence", ""))
            continue
        s, in_comment = strip_comment(s, in_comment)
        s = s.strip()
        if not s or re.fullmatch(r"[-*_=\s|:]+", s):
            doc.empty += 1
            info.append(("empty", ""))
            continue
        hm = re.match(r"^#{1,6}\s+(.*?)\s*#*\s*$", s)
        if hm:
            t = clean_inline(hm.group(1))
            info.append(("heading", t) if t else ("empty", ""))
            if not t:
                doc.empty += 1
            continue
        if s.startswith("|"):
            cells = [clean_inline(c) for c in s.strip("|").split("|")]
            t = " | ".join(c for c in cells if c)
            if not t:
                doc.empty += 1
                info.append(("empty", ""))
            else:
                info.append(("table", t + "\x00" + (cells[0] if cells else "")))
            continue
        q = re.sub(r"^(?:>\s*)+", "", s)
        lm = re.match(r"^(?:[-*+]|\d+[.)])\s+(.*)$", q)
        kind = "list" if lm else "para"
        t = clean_inline(lm.group(1) if lm else q)
        if not t:
            doc.empty += 1
            info.append(("empty", ""))
        else:
            info.append((kind, t))

    n = len(info)
    for i, (kind, t) in enumerate(info):
        ln = i + 1
        if kind in ("fence", "empty"):
            continue
        doc.judged += 1
        if kind == "heading":
            doc.titles.append((ln, t, True))
            doc.texts.append((ln, t))
        elif kind == "table":
            row, first = t.split("\x00")
            doc.texts.append((ln, row))
            if first:
                doc.titles.append((ln, first, False))
        else:
            doc.texts.append((ln, t))
            if kind == "para":
                j = i - 1
                while j >= 0 and info[j][0] == "empty":
                    j -= 1
                has_prev = j >= 0 and info[j][0] != "heading"
                nxt = info[i + 1][0] if i + 1 < n else None
                if has_prev and nxt in (None, "empty", "heading", "fence") and moral_text_ok(t):
                    doc.morals.append((ln, t))
    return doc


_INLINE = {"span", "b", "strong", "i", "em", "u", "mark", "a", "code", "small", "sub", "sup",
           "abbr", "kbd", "s", "del", "ins", "tspan", "font"}
_TAG = re.compile(r"<(/?)([A-Za-z][A-Za-z0-9:-]*)((?:\"[^\"]*\"|'[^']*'|[^>\"'])*)>")


def parse_html(src):
    doc = Doc()
    n = len(src)
    kind = ["b"] * n

    def setk(a, b, k):
        for i in range(a, b):
            if src[i] != "\n" and kind[i] == "b":
                kind[i] = k

    for m in re.finditer(r"<!--.*?-->", src, re.S):
        setk(m.start(), m.end(), "x")
    for m in re.finditer(r"<script\b[^>]*>.*?</script\s*>", src, re.S | re.I):
        setk(m.start(), m.end(), "s")
    for m in re.finditer(r"<style\b[^>]*>.*?</style\s*>", src, re.S | re.I):
        setk(m.start(), m.end(), "s")
    for m in re.finditer(r"<![^>]*>", src):
        setk(m.start(), m.end(), "x")
    for m in _TAG.finditer(src):
        setk(m.start(), m.end(), "i" if m.group(2).lower() in _INLINE else "x")

    sid = [0] * n
    nsid = 0
    for m in re.finditer(r"<h([1-3])\b[^>]*>(.*?)</h\1\s*>", src, re.S | re.I):
        # 주석·스크립트 안의 h 태그는 안쪽 글자가 이미 'x'·'s'로 표시돼 있어 여기서 걸러진다
        if not any(kind[i] == "b" for i in range(m.start(2), m.end(2))):
            continue
        nsid += 1
        for i in range(m.start(2), m.end(2)):
            sid[i] = nsid
            if kind[i] == "b":
                kind[i] = "t"

    title_parts = {}   # sid -> [문자...]
    title_first = {}   # sid -> 첫 텍스트 줄
    line_no = 1
    b_buf, t_buf, has_s = [], [], False
    line_entries = []  # (줄, 본문, 제목텍스트)

    def flush():
        nonlocal b_buf, t_buf, has_s
        body = re.sub(r"\s+", " ", htmlmod.unescape("".join(b_buf))).strip()
        tit = re.sub(r"\s+", " ", htmlmod.unescape("".join(t_buf))).strip()
        if body or tit:
            doc.judged += 1
            line_entries.append((line_no, body, tit))
        elif has_s:
            doc.script += 1
        else:
            doc.empty += 1
        b_buf, t_buf, has_s = [], [], False

    for i, ch in enumerate(src):
        if ch == "\n":
            flush()
            line_no += 1
            if sid[i]:
                title_parts.setdefault(sid[i], []).append(" ")
            continue
        k = kind[i]
        if sid[i]:
            parts = title_parts.setdefault(sid[i], [])
            if k == "t":
                parts.append(ch)
                if not ch.isspace():
                    title_first.setdefault(sid[i], line_no)
            elif k == "x" or k == "s":
                parts.append(" ")
        if k == "b":
            b_buf.append(ch)
            t_buf.append(" ")
        elif k == "t":
            t_buf.append(ch)
            b_buf.append(" ")
        elif k == "i":
            pass
        else:
            b_buf.append(" ")
            t_buf.append(" ")
            if k == "s":
                has_s = True
    flush()

    for s_id, parts in title_parts.items():
        text = re.sub(r"\s+", " ", htmlmod.unescape("".join(parts))).strip()
        if text and s_id in title_first:
            doc.titles.append((title_first[s_id], text, True))

    prev_is_body = False
    for ln, body, tit in line_entries:
        if tit:
            doc.texts.append((ln, tit))
        if body:
            doc.texts.append((ln, body))
        if body and not tit and prev_is_body and moral_text_ok(body):
            doc.morals.append((ln, body))
        prev_is_body = bool(body) and not tit
    return doc


# ---------- 검사 ----------

def lint(doc):
    found = {}  # (줄, 유형) -> 발췌

    def add(ln, typ, ex):
        found.setdefault((ln, typ), ex)

    for ln, t, allow_bare in doc.titles:
        if check_slogan(t) is not None:
            add(ln, "SLOGAN", excerpt(t))
        if check_numtitle(t, allow_bare) is not None:
            add(ln, "NUMTITLE", excerpt(t))
    for ln, t in doc.texts:
        for typ, rx in GENERAL:
            m = rx.search(t)
            if m:
                add(ln, typ, excerpt(t, m.start()))
    for ln, t in doc.morals:
        add(ln, "MORAL", excerpt(t))
    order = {t: i for i, t in enumerate(TYPES)}
    return sorted(found.items(), key=lambda kv: (kv[0][0], order[kv[0][1]]))


def main(argv):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    if not argv:
        print("사용: python plans/FRAME-개편/tone_lint.py <파일> [<파일> ...]", file=sys.stderr)
        print("RESULT 판정 0줄 · 입력 파일 없음 — PASS 아님")
        return 2

    counts = {t: 0 for t in TYPES}
    judged = fence = empty = script = 0
    read_fail = 0
    for path in argv:
        try:
            with open(path, "rb") as f:
                text = f.read().decode("utf-8-sig")
        except (OSError, UnicodeDecodeError) as e:
            print(f"{path}: 읽기 실패 — {e}", file=sys.stderr)
            read_fail += 1
            continue
        is_html = path.lower().endswith((".html", ".htm"))
        doc = parse_html(text) if is_html else parse_md(text)
        judged += doc.judged
        fence += doc.fence
        empty += doc.empty
        script += doc.script
        for (ln, typ), ex in lint(doc):
            counts[typ] += 1
            print(f"{path}:{ln} [{LABEL[typ]}] {ex}")

    k = sum(counts.values())
    by = "·".join(f"{t} {counts[t]}" for t in TYPES)
    reasons = f"코드 펜스 {fence}·스크립트·스타일 {script}·빈 텍스트 {empty}"
    unjudged = fence + script + empty
    tail = "MORAL은 휴리스틱(짧은 단정문만 본다)"
    if judged == 0:
        print(f"RESULT 판정 0줄 · 미판정 {unjudged}줄({reasons}) · 눈먼 0 — PASS 아님")
        return 2
    print(f"RESULT 판정 {judged}줄 · 위반 {k}건({by}) · 미판정 {unjudged}줄({reasons}) · {tail}")
    if read_fail:
        return 2
    return 1 if k else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
