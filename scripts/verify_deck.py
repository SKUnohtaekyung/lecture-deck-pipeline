#!/usr/bin/env python3
"""verify_deck.py — vibecoding-deck 산출 덱 정적 검증 (측정 우선, 의존성 0).

사용: python scripts/verify_deck.py <deck.html> [--parts N] [--release] [--manifest P] [--registry P] [--atlas]

3개 층으로 구성된다(2026-07-19 재설계, 의존성 0 유지 · html.parser는 stdlib):
  L1 HTML 파싱 — html.parser.HTMLParser 기반. 속성 순서·인용부호·속성값 내 '>' 무관,
      classes()는 공백 토큰 정확 분해(파생 클래스 오탐 방지), 엔티티 디코드 텍스트 뷰 제공.
  L2 CSS 수집 — collect_css()가 덱 인라인 <style> + 덱이 실제로 링크한 로컬 CSS를 합산해
      실제 적용되는 CSS를 검사한다. CSS 주석은 검사 전에 제거. 저장소 kit CSS 검사는
      [kit] 접두로 명시 분리(덱이 아니라 저장소를 검사한다는 뜻).
  L3 CSS 규칙 워커 — iter_rules()가 중괄호 균형으로 @media/@supports/@layer 안까지
      재귀 진입, 모든 매칭 블록을 반환(첫 선언만이 아님), longhand를 shorthand로 정규화.

정적으로 채점하는 것(브라우저 없이):
  - 슬라이드 수 · 고정 슬라이드(cover/s02/s03/concept-recap) 존재
  - part-divider 수 (= --parts N 이면 일치 검사)
  - 네비 엔진(.navbar) · 상세 메뉴 PDF 출력 버튼(#pdfBtn)
  - deck.css + legibility.css 로드(링크 또는 인라인)
  - 코드 시각화(.viz-* 또는 data-viz)와 실제 <img> 구성 현황 (로고·표지 SVG는 집계 제외)
  - 콘텐츠 슬라이드 구도 다양성: 서로 다른 구조 시그니처 수 · 같은 구도 최장 연속
  - raw #hex · rgba()/hsl() · CSS 명명색이 CSS·인라인 style=·SVG fill=/stroke=에 쓰였는지(FAIL)
  - 덱 인라인 <style>/style= 그라디언트 금지(flat-fill) · 덱 인라인 var(--navy) 금지(fallback 형태 포함) ·
    진행/페이지 자동주입 스크립트(s-pageno+s-part)
  - 공유 kit CSS의 메인 블루 헤더 선 · 민트 강조 프리미티브 · 토큰/민트 배지 무결성
  - 박스 표면 규칙: 흰 fill(--white/--surface-alt) + 근백색 축약 보더(--line) 조합 금지
    (kit CSS + 덱 인라인 <style>/style= 모두 · 방향 지정 border-top/-bottom/-left는 내부 구분선으로 허용)
  - .work-step · .agenda-item 수직 중앙 정렬(align-items:center) 계약
  - 참조 아틀라스(레이아웃/element 연속 열람용 덱)는 --atlas 플래그로 구도 다양성 검사만 제외

브라우저로만 되는 것(오버플로·콘솔·가독성 computed)은 이 스크립트가 안 하고 리마인더만 출력.
종료코드: FAIL 있으면 1, 아니면 0.
"""
import sys, re, os, argparse, json
from pathlib import Path
from urllib.parse import unquote, urlsplit
from html.parser import HTMLParser
import html as _html_stdlib
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows cp949 콘솔 대응
except Exception:
    pass

# 2026-07-23: S61 삭제로 78장, 제작 과정 4장 연작(data-series) 예외 신설, recap 필수 계약 해제
FIXED = {"cover": "cover", "s02": "s02-slide", "s03": "s03-slide"}

# ============================================================================
# L1 — HTML 파싱 층 (html.parser.HTMLParser 기반)
#   속성 순서·인용부호 종류·속성값 내 '>' 무관. classes()는 정확한 공백 토큰 분해.
# ============================================================================

_VOID_ELEMENTS = {
    'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta',
    'param', 'source', 'track', 'wbr',
}


class ParsedTag:
    """하나의 시작 태그(자기닫힘 포함). attrs는 소문자 키의 dict(값은 원문 그대로)."""
    __slots__ = ('name', 'attrs', 'start', 'end')

    def __init__(self, name, attrs, start, end):
        self.name = name
        self.attrs = attrs
        self.start = start
        self.end = end


class ParsedElement:
    """매칭된 시작~끝 태그 쌍(또는 self-closed/void 요소).
    start/end        = 요소 전체 범위(여는 태그 시작 ~ 닫는 태그 끝).
    inner_start/end   = 여는 태그 끝 ~ 닫는 태그 시작(자식 콘텐츠 범위, void/self-closed는 길이 0)."""
    __slots__ = ('name', 'attrs', 'start', 'end', 'inner_start', 'inner_end')

    def __init__(self, name, attrs, start, end, inner_start, inner_end):
        self.name = name
        self.attrs = attrs
        self.start = start
        self.end = end
        self.inner_start = inner_start
        self.inner_end = inner_end


class _DocCollector(HTMLParser):
    def __init__(self, raw):
        super().__init__(convert_charrefs=True)
        self.raw = raw
        self._line_starts = [0]
        for i, ch in enumerate(raw):
            if ch == '\n':
                self._line_starts.append(i + 1)
        self.tags = []
        self.elements = []
        self._stack = []

    def _offset(self):
        line, col = self.getpos()
        return self._line_starts[line - 1] + col

    @staticmethod
    def _norm_attrs(attrs_list):
        attrs = {}
        for k, v in attrs_list:
            if k is None:
                continue
            attrs[k.lower()] = v if v is not None else ""
        return attrs

    def handle_starttag(self, tag, attrs_list):
        start = self._offset()
        text = self.get_starttag_text() or ('<' + tag + '>')
        end = start + len(text)
        attrs = self._norm_attrs(attrs_list)
        self.tags.append(ParsedTag(tag, attrs, start, end))
        if tag in _VOID_ELEMENTS:
            self.elements.append(ParsedElement(tag, attrs, start, end, end, end))
        else:
            self._stack.append([tag, attrs, start, end])

    def handle_startendtag(self, tag, attrs_list):
        start = self._offset()
        text = self.get_starttag_text() or ('<' + tag + '/>')
        end = start + len(text)
        attrs = self._norm_attrs(attrs_list)
        self.tags.append(ParsedTag(tag, attrs, start, end))
        self.elements.append(ParsedElement(tag, attrs, start, end, end, end))

    def handle_endtag(self, tag):
        pos = self._offset()
        close_end = self.raw.find('>', pos)
        end = close_end + 1 if close_end != -1 else pos
        idx = None
        for i in range(len(self._stack) - 1, -1, -1):
            if self._stack[i][0] == tag:
                idx = i
                break
        if idx is None:
            return  # 매칭되지 않는 닫는 태그 — 무시(관대한 오류 복구)
        while len(self._stack) > idx + 1:
            self._stack.pop()  # 잘못 중첩된 내부 열림은 폐기(오류 복구, 형식이 맞는 덱에는 영향 없음)
        name, attrs, s, inner_start = self._stack.pop()
        self.elements.append(ParsedElement(name, attrs, s, end, inner_start, pos))


def parse_document(raw_html):
    """전체 문서를 파싱해 (tags, elements)를 반환한다.
    tags: 문서 순서의 모든 시작 태그(ParsedTag) 목록.
    elements: 매칭된 시작~끝 요소(ParsedElement) 목록 — 중첩된 비-slide <section>이
              바깥 슬라이드의 inner 범위를 자르지 않도록 스택 기반으로 매칭한다."""
    parser = _DocCollector(raw_html)
    parser.feed(raw_html)
    parser.close()
    return parser.tags, parser.elements


def classes(tag_or_attrs):
    """공백 토큰 정확 분해(부분 문자열 매칭 아님) — part-divider-inner가 part-divider로 안 잡힌다."""
    attrs = tag_or_attrs.attrs if hasattr(tag_or_attrs, 'attrs') else (tag_or_attrs or {})
    return set((attrs.get('class') or '').split())


def decoded_text(raw_html):
    """<script>/<style> 제외(대소문자 무시) + 엔티티 디코드된 텍스트 뷰(이모지 마커 누출 검사용)."""
    stripped = re.sub(r'<(script|style)\b[^>]*>.*?</\1\s*>', '', raw_html, flags=re.S | re.I)
    return _html_stdlib.unescape(stripped)


# ============================================================================
# L2 — CSS 수집 층: 덱에 실제로 적용되는 CSS(인라인 <style> + 링크된 로컬 CSS)
# ============================================================================

class CssBundle:
    """collect_css()의 반환값. all = deck_inline + linked_local(둘 다 주석 제거 후)."""
    __slots__ = ('deck_inline', 'linked_local', 'all', 'raw_byte_count')

    def __init__(self, deck_inline, linked_local, raw_byte_count):
        self.deck_inline = deck_inline
        self.linked_local = linked_local
        self.all = "\n".join(c for c in (deck_inline, linked_local) if c)
        self.raw_byte_count = raw_byte_count


def _strip_css_comments(css_text):
    return re.sub(r'/\*.*?\*/', '', css_text, flags=re.S)


def local_linked_css(html_text, deck_path, tags=None):
    """덱이 링크한 로컬 CSS를 읽는다. 외부 URL과 누락 파일은 건너뛴다."""
    if tags is None:
        tags, _ = parse_document(html_text)
    chunks = []
    base = Path(deck_path).resolve().parent
    for tag in tags:
        if tag.name != 'link':
            continue
        href = tag.attrs.get('href')
        if not href:
            continue
        clean = href.split("?", 1)[0].split("#", 1)[0]
        if not clean or re.match(r'^(?:https?:|data:|//)', clean, re.I):
            continue
        try:
            css_path = (base / unquote(clean)).resolve()
        except (OSError, ValueError):
            continue
        if css_path.is_file() and css_path.suffix.lower() == ".css":
            try:
                chunks.append(css_path.read_text(encoding="utf-8"))
            except OSError:
                pass
    return "\n".join(chunks)


def collect_css(html_text, deck_path, tags=None, elements=None):
    """덱에 실제로 적용되는 CSS(인라인 <style> + 로컬 링크 CSS)를 CssBundle로 반환.
    CSS 주석은 반환 전에 제거한다(검사 오탐 원인 제거)."""
    if tags is None or elements is None:
        tags, elements = parse_document(html_text)
    style_chunks = [html_text[el.inner_start:el.inner_end] for el in elements if el.name == 'style']
    deck_inline_raw = "\n".join(style_chunks)
    linked_raw = local_linked_css(html_text, deck_path, tags=tags)
    raw_bytes = len((deck_inline_raw + linked_raw).encode('utf-8', errors='ignore'))
    return CssBundle(_strip_css_comments(deck_inline_raw), _strip_css_comments(linked_raw), raw_bytes)


# ============================================================================
# L3 — CSS 규칙 워커: 중괄호 균형 스캔(@media/@supports/@layer 재귀 진입)
# ============================================================================

_VAR_SPACING_RE = re.compile(r'var\(\s*(--[A-Za-z0-9_-]+)\s*\)')
_VAR_SPACING_FALLBACK_RE = re.compile(r'var\(\s*(--[A-Za-z0-9_-]+)\s*,\s*')


def _normalize_var_spacing(value):
    """var( --x ) → var(--x) 공백 제거(fallback 폼의 콤마 뒤 공백은 보존)."""
    value = _VAR_SPACING_FALLBACK_RE.sub(r'var(\1, ', value)
    value = _VAR_SPACING_RE.sub(r'var(\1)', value)
    return value


def _parse_declarations(body):
    """선언 블록 문자열을 {속성명(소문자): 정규화된 값} dict로 변환.
    뒤 선언이 앞 선언을 덮는다(일반 CSS 캐스케이드와 동일). longhand는 shorthand로 합성한다."""
    decls = {}
    for stmt in body.split(';'):
        stmt = stmt.strip()
        if not stmt or ':' not in stmt:
            continue
        prop, _, val = stmt.partition(':')
        prop = prop.strip().lower()
        val = _normalize_var_spacing(val.strip())
        if prop:
            decls[prop] = val
    if 'background' not in decls and 'background-color' in decls:
        decls['background'] = decls['background-color']
    if 'border' not in decls and all(k in decls for k in ('border-width', 'border-style', 'border-color')):
        decls['border'] = decls['border-width'] + ' ' + decls['border-style'] + ' ' + decls['border-color']
    return decls


def iter_rules(css_text, _at_context=()):
    """(selector_group, decls, raw_body, at_context)를 모든 규칙 블록에 대해 yield.
    @media/@supports/@layer 안까지 재귀 진입하고, 매칭되는 모든 블록을 반환한다(첫 선언만이 아님)."""
    i, n = 0, len(css_text)
    while i < n:
        brace = css_text.find('{', i)
        if brace == -1:
            break
        head = css_text[i:brace].strip()
        depth, j = 1, brace + 1
        while j < n and depth > 0:
            if css_text[j] == '{':
                depth += 1
            elif css_text[j] == '}':
                depth -= 1
            j += 1
        body = css_text[brace + 1:j - 1] if depth == 0 else css_text[brace + 1:]
        if head.startswith('@'):
            at_kind = head.split(None, 1)[0].lower()
            if at_kind in ('@media', '@supports', '@layer'):
                yield from iter_rules(body, _at_context + (head,))
            # 그 외 @-규칙(@font-face/@keyframes/@page 등)은 selector 기반이 아니므로 건너뜀
        elif head:
            yield (head, _parse_declarations(body), body, _at_context)
        i = j
        if depth != 0:
            break


# ── 박스 표면 규칙: 흰 fill(--white/--surface-alt) + 근백색(--line) '축약' 보더 조합 금지 ──
#   예외: 상태 도트·코드/터미널 표면·주석 스크린샷 창·문서 루트.
#   `.slide`는 그 자체(또는 같은 요소의 다른 클래스/의사클래스와 결합)일 때만 예외 —
#   `.slide .foo`처럼 자손 결합자가 붙으면 더 이상 예외가 아니다(2026-07-19 축소, 우회 차단).
_BOX_EXEMPT = re.compile(r'\.pd-dot|\.co-bar|\.cover-terminal|\.shot-|\bbody\b|\bhtml\b|:root\b')
_SLIDE_BARE_RE = re.compile(r'^\.slide(?:[.:#\[][^\s>+~]*)?$')


def _is_box_exempt_selector(sel):
    sel = sel.strip()
    if not sel:
        return True
    if _SLIDE_BARE_RE.match(sel):
        return True
    return bool(_BOX_EXEMPT.search(sel))


def _box_violation_decls(decls):
    bg = (decls.get('background') or '').strip()
    border = (decls.get('border') or '').strip()
    if not re.match(r'^var\(--(?:white|surface-alt)\)', bg):
        return False
    return bool(re.search(r'(?:^|\s)var\(--line\)', border))


def box_surface_violations(css_text):
    """흰 fill(--white/--surface-alt) + 근백색(--line) '축약' 보더 조합 = 박스 표면 규칙 위반.
    방향 지정 보더(border-top/-bottom/-left/-right)는 내부 구분선이라 합법(축약 border만 검사)."""
    bad = []
    for selector_group, decls, _body, _at in iter_rules(css_text):
        if not _box_violation_decls(decls):
            continue
        for sel in selector_group.split(','):
            sel = sel.strip()
            if not sel or _is_box_exempt_selector(sel):
                continue
            bad.append(sel[:40])
    return bad


# ============================================================================
# 색 리터럴 검사: raw #hex / rgba()·hsl() / CSS 명명색 — 토큰(var(--x)) 우회 검사
# ============================================================================

_NAMED_COLORS = frozenset("""
aliceblue antiquewhite aqua aquamarine azure beige bisque black blanchedalmond
blue blueviolet brown burlywood cadetblue chartreuse chocolate coral
cornflowerblue cornsilk crimson cyan darkblue darkcyan darkgoldenrod darkgray
darkgreen darkgrey darkkhaki darkmagenta darkolivegreen darkorange darkorchid
darkred darksalmon darkseagreen darkslateblue darkslategray darkslategrey
darkturquoise darkviolet deeppink deepskyblue dimgray dimgrey dodgerblue
firebrick floralwhite forestgreen fuchsia gainsboro ghostwhite gold goldenrod
gray green greenyellow grey honeydew hotpink indianred indigo ivory khaki
lavender lavenderblush lawngreen lemonchiffon lightblue lightcoral lightcyan
lightgoldenrodyellow lightgray lightgreen lightgrey lightpink lightsalmon
lightseagreen lightskyblue lightslategray lightslategrey lightsteelblue
lightyellow lime limegreen linen magenta maroon mediumaquamarine mediumblue
mediumorchid mediumpurple mediumseagreen mediumslateblue mediumspringgreen
mediumturquoise mediumvioletred midnightblue mintcream mistyrose moccasin
navajowhite navy oldlace olive olivedrab orange orangered orchid
palegoldenrod palegreen paleturquoise palevioletred papayawhip peachpuff peru
pink plum powderblue purple rebeccapurple red rosybrown royalblue saddlebrown
salmon sandybrown seagreen seashell sienna silver skyblue slateblue slategray
slategrey snow springgreen steelblue tan teal thistle tomato turquoise violet
wheat white whitesmoke yellow yellowgreen
""".split())

_HEX_COLOR_RE = re.compile(r'#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{4}|[0-9a-fA-F]{3})\b')
_FUNC_COLOR_RE = re.compile(r'\b(?:rgba?|hsla?)\s*\(')
_WORD_RE = re.compile(r'[a-zA-Z][a-zA-Z-]*')
_URL_FN_RE = re.compile(r'\burl\([^)]*\)', re.I)
_VAR_FN_RE = re.compile(r'\bvar\([^)]*\)', re.I)


def _strip_urls_and_vars(value):
    """url(...)(data: URI 포함)와 var(...)(토큰 참조/폴백) 내부는 리터럴 색 검사 대상이 아니다."""
    value = _URL_FN_RE.sub('', value)
    value = _VAR_FN_RE.sub('', value)
    return value


def _color_literal_hits(value):
    """value 안의 raw hex / rgba()·hsla() / CSS 명명색을 찾는다."""
    if not value:
        return []
    v = _strip_urls_and_vars(value)
    hits = list(_HEX_COLOR_RE.findall(v))
    if _FUNC_COLOR_RE.search(v):
        hits.append('rgba()/hsla()')
    for word in _WORD_RE.findall(v):
        if word.lower() in _NAMED_COLORS:
            hits.append(word)
    return hits


def _hex_only_hits(value):
    """[kit] 검사 전용 — raw hex만 잡는다(rgba/명명색은 결정 3의 측정 범위 밖).
    스킵 규칙: url(...)/var(...) 내부."""
    if not value:
        return []
    return list(_HEX_COLOR_RE.findall(_strip_urls_and_vars(value)))


def find_color_violations(css_text, *, hex_only=False):
    """CSS 텍스트(주석 제거·규칙 단위)에서 raw 색 리터럴 사용을 찾는다.
    :root 블록과 커스텀 프로퍼티 정의 줄(--name: ...)은 토큰 정의이므로 검사 대상이 아니다."""
    hits = []
    scan = _hex_only_hits if hex_only else _color_literal_hits
    for selector_group, decls, _body, _at in iter_rules(css_text):
        selectors = [s.strip() for s in selector_group.split(',')]
        if any(s == ':root' or s.startswith(':root') for s in selectors if s):
            continue
        for prop, val in decls.items():
            if prop.startswith('--'):
                continue  # 커스텀 프로퍼티 정의(토큰) 줄은 검사 대상이 아니다
            hits.extend(scan(val))
    return hits


def _style_attr_declarations(tags):
    """(tag, decls) — style="..." 속성이 있는 모든 요소(따옴표 종류 무관, L1이 이미 해석)."""
    out = []
    for tag in tags:
        style_val = tag.attrs.get('style')
        if style_val:
            out.append((tag, _parse_declarations(style_val)))
    return out


# ============================================================================
# 슬라이드 <section> 탐색 — find_sections()/_slide_section_ranges()는 같은
# 슬라이드 집합을 반환하도록 통일한다(2026-07-19, 중첩 비-slide <section>이
# 바깥 슬라이드 inner를 자르는 문제 · 이중 구현 불일치 문제 동시 해결).
# ============================================================================

def _slide_elements(elements):
    return [el for el in elements if el.name == 'section' and 'slide' in classes(el.attrs)]


def find_sections(html_text, elements=None):
    """(class_attr_string, inner_html) — class 토큰에 'slide'가 있는 모든 <section>.
    inner_html은 해당 section의 실제 매칭 닫는 태그까지만(중첩된 비-slide <section>이 있어도
    안 잘린다)."""
    if elements is None:
        _, elements = parse_document(html_text)
    return [(el.attrs.get('class') or '', html_text[el.inner_start:el.inner_end])
            for el in _slide_elements(elements)]


def _slide_section_ranges(html_text, elements=None):
    """(start, end, class_attr_string, opening_tag_text) — 슬라이드 섹션의 전체 범위.
    find_sections()와 동일한 슬라이드 집합에서 파생된다(defect ⑧: 단일 소스)."""
    if elements is None:
        _, elements = parse_document(html_text)
    return [(el.start, el.end, el.attrs.get('class') or '', html_text[el.start:el.end])
            for el in _slide_elements(elements)]


def _strip_hidden_spans(html_text, start, end, elements):
    """[start,end) 범위에서 hidden/aria-hidden="true" 요소의 텍스트를 제거한 문자열을 반환한다
    (결정 1c: 시그니처 스푸핑 차단 — 숨김 요소로 구도 마커를 조작하지 못하게)."""
    hidden_spans = []
    for el in elements:
        if el.start < start or el.end > end:
            continue
        attrs = el.attrs
        if 'hidden' in attrs or (attrs.get('aria-hidden', '').strip().lower() == 'true'):
            hidden_spans.append((el.start, el.end))
    if not hidden_spans:
        return html_text[start:end]
    hidden_spans.sort()
    merged = []
    for s, e in hidden_spans:
        if merged and s <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append((s, e))
    out, cur = [], start
    for s, e in merged:
        if s > cur:
            out.append(html_text[cur:s])
        cur = max(cur, e)
    if cur < end:
        out.append(html_text[cur:end])
    return "".join(out)


def family_signature(cls, inner):
    """콘텐츠 슬라이드의 *실제 구도 family* 시그니처(단조 감지용).

    예전 덱의 ``s-full``/``s-body-wrap``만 보던 구현은 커스텀 레이아웃을 전부
    ``full`` 또는 ``other``로 뭉개 3연속을 오탐했다. 여기서는 장식 클래스나
    슬라이드 ID가 아니라, 화면의 배치 방식을 결정하는 layout 컴포넌트를
    안정된 family(terminal/browser/tree/gui/bands/flow 등)로 정규화한다.
    같은 family를 CSS 클래스 이름만 바꿔 우회하지 못하도록 세부 클래스별로
    고유 시그니처를 만들지 않는다.
    """
    haystack = cls + "\n" + inner

    def has_class(*names):
        return any(re.search(r'class=["\'][^"\']*(?<![\w-])' + re.escape(name) +
                             r'(?![\w-])[^"\']*["\']', haystack, re.I)
                   or re.search(r'(?:^|\s)' + re.escape(name) + r'(?:\s|$)', cls)
                   for name in names)

    # 강한 시각 family부터 판별한다. 아래 순서는 terminal 안의 bar/body 같은
    # 내부 구조가 grid/flow로 잘못 분류되지 않게 하는 우선순위이기도 하다.
    if has_class('intro-do', 'intro-do-more', 'center-msg', 'thank-you'):
        return 'centered'
    if has_class('terminal-dark', 'dark-terminal', 'terminal-explain-layout',
                 'request-terminal-layout', 'detailed-prompt-layout'):
        return 'terminal'
    if has_class('portfolio-showcase', 'portfolio-browser', 'browser-result-frame',
                 'completion-browser', 'browser-result-slide'):
        return 'browser'
    if has_class('folder-tree-gui', 'project-tree-layout', 'project-tree-visual'):
        return 'tree'
    if has_class('breadcrumb-track', 'breadcrumb-guide-layout',
                 'workspace-breadcrumb-slide', 'workspace-compare'):
        return 'breadcrumb'
    if re.search(r'data-asset-kind=["\']screenshot["\']', inner, re.I) or has_class('shot-annot', 'shot-win'):
        return 'shot'
    if has_class('codex-gui', 'codex-app-gui', 'codex-open-layout', 'extension-gui',
                 'drive-open-slide', 'folder-create-layout', 'app-guide-layout',
                 'file-request-layout', 'verify-file-layout', 'path-inspection-layout',
                 'final-location-layout'):
        return 'gui'
    if has_class('workspace-map-layout'):
        return 'map'
    # 플롯 차트(축·계열·눈금)는 카드/밴드와 시선 흐름이 근본적으로 달라 별도 family다.
    if has_class('lm-chart', 'viz-line', 'viz-column', 'viz-hbar', 'viz-area'):
        return 'chart'
    if has_class('llm-agent-bands', 'context-memory-bands', 'request-four-bands',
                 'dl-rows', 'pf-list', 'sy-cases'):
        return 'bands'
    if has_class('coding-terms'):
        return 'timeline'
    if has_class('compare2', 'cc-grid', 'request-compare-panels', 'change-scope-grid',
                 'tool-roles', 'privacy-layout', 'human-compare'):
        return 'compare'
    if (has_class('journey-week-grid', 'grid-2', 'grid-3', 'app-types-grid',
                  'readiness-grid', 'scope-layout', 'required-conditions-layout',
                  'eng-four', 'privacy-tiers')
            or 'revenue-grid' in inner):
        return 'grid'
    if has_class('eval-steps'):
        return 'steps'
    if (has_class('role-flow-layout', 'lifecycle-flow', 'risk-flow', 'plan-mode-layout',
                  'viz-flow-ph', 'change-refresh-flow')
            or re.search(r'\bdata-viz(?:\s*=|\s|>)', inner)
            or has_class('work-step', 'flow-step')):
        return 'flow'
    if has_class('intro-ai-era'):
        return 'asym'
    if 'table' in inner and re.search(r'class=["\']t\b', inner):
        return 'table'
    if has_class('s-body-wrap'):
        return 'split/leftcol'
    if has_class('s-full') or 'canvas-fill' in cls:
        return 'full'
    return 'other'


def diversity_need(n):
    """결정 1b — 절대·상한 램프. 비례 임계값은 어휘집 크기와 덱 길이를 혼동하는 범주 오류다."""
    if n < 12: return 3
    if n < 24: return 4
    if n < 40: return 5
    return 6


def _attr(tag, name):
    match = re.search(rf'\b{re.escape(name)}\s*=\s*(["\'])(.*?)\1', tag, re.I | re.S)
    return match.group(2) if match else None


def _is_remote(reference):
    return bool(re.match(r'^(?:https?:)?//', reference or '', re.I))


def _local_reference(reference, base):
    if not reference or reference.startswith(('data:', '#')) or _is_remote(reference):
        return None
    return (base / unquote(urlsplit(reference).path)).resolve()


def _srcset_references(value):
    for candidate in (value or '').split(','):
        pieces = candidate.strip().split(None, 1)
        if pieces:
            yield pieces[0]


def _figure_slots(html):
    slots = []
    for match in re.finditer(r'<figure\b([^>]*)>(.*?)</figure>', html, re.I | re.S):
        attrs, body = match.group(1), match.group(2)
        classes_str = _attr(attrs, 'class') or ''
        if re.search(r'\basset-slot\b', classes_str):
            slots.append((attrs, body, classes_str))
    return slots


def count_code_viz(html):
    """Count explicit visualization owner elements once, even with two markers."""
    count = 0
    for tag in re.findall(r'<[a-z][^>]*>', html, re.I):
        classes_str = _attr(tag, 'class') or ''
        if re.search(r'(?:^|\s)viz-[a-z0-9_-]+(?:\s|$)', classes_str, re.I) or re.search(
            r'\bdata-viz(?:\s*=|\s|>)', tag, re.I
        ):
            count += 1
    return count


def validate_manifest_document(data):
    """Validate the session image-manifest contract at runtime."""
    errors = []
    if not isinstance(data, dict):
        return ['manifest root must be an object']
    required_root = {'schema_version', 'session', 'image_mode', 'slides'}
    missing_root = sorted(required_root - set(data))
    if missing_root:
        errors.append(f'manifest missing required fields {missing_root}')
    if data.get('schema_version') != '1.0':
        errors.append("manifest schema_version must be '1.0'")
    if not isinstance(data.get('session'), str) or not data.get('session', '').strip():
        errors.append('manifest session must be a nonempty string')
    if data.get('image_mode') not in {'not_required', 'reuse_only', 'generate_now', 'prompt_only', 'pending'}:
        errors.append('manifest image_mode is invalid')
    slides = data.get('slides')
    if not isinstance(slides, list):
        errors.append('manifest slides must be an array')
        return errors

    required_slide = {
        'slide_id', 'part', 'decision', 'decision_reason', 'purpose', 'role', 'brief',
        'expected_file', 'method', 'asset_id', 'parent_asset_ids', 'prompt_id', 'status', 'qa',
    }
    decisions = {
        'NO_IMAGE': 'none',
        'IMAGE_EXPLANATORY': 'explanatory',
        'IMAGE_MNEMONIC': 'mnemonic',
        'IMAGE_DECORATIVE_OPTIONAL': 'decorative',
    }
    for index, slide in enumerate(slides):
        prefix = f'manifest slide {index}'
        if not isinstance(slide, dict):
            errors.append(f'{prefix} must be an object')
            continue
        missing = sorted(required_slide - set(slide))
        if missing:
            errors.append(f'{prefix} missing required fields {missing}')
        decision = slide.get('decision')
        purpose = slide.get('purpose')
        if decision not in decisions:
            errors.append(f'{prefix} decision is invalid')
        elif purpose != decisions[decision]:
            errors.append(f'{prefix} decision-purpose mismatch')
        if purpose not in {'none', 'explanatory', 'mnemonic', 'decorative'}:
            errors.append(f'{prefix} purpose is invalid')
        role = slide.get('role')
        status = slide.get('status')
        method = slide.get('method')
        if role not in {'none', 'hero', 'support', 'spot'}:
            errors.append(f'{prefix} role is invalid')
        if status not in {'not_needed', 'expected', 'processing', 'ready', 'rejected', 'blocked'}:
            errors.append(f'{prefix} status is invalid')
        if method not in {'none', 'reuse', 'generate', 'transform'}:
            errors.append(f'{prefix} method is invalid')
        if decision == 'NO_IMAGE':
            if role != 'none' or status != 'not_needed' or method != 'none' or slide.get('expected_file') is not None:
                errors.append(f'{prefix} NO_IMAGE state is inconsistent')
        elif role not in {'hero', 'support', 'spot'} or not isinstance(slide.get('expected_file'), str) or not slide.get('expected_file'):
            errors.append(f'{prefix} image decision requires active role and expected_file')
        if not isinstance(slide.get('parent_asset_ids'), list):
            errors.append(f'{prefix} parent_asset_ids must be an array')
        if not isinstance(slide.get('brief'), dict) or not isinstance(slide.get('qa'), dict):
            errors.append(f'{prefix} brief and qa must be objects')
    return errors


def image_contract_checks(html, deck_path, *, release=False, manifest_path=None, registry_path=None):
    """Return static image-contract violations and informational notes."""
    errors, notes = [], []
    base = Path(deck_path).resolve().parent
    html = re.sub(r"<!--.*?-->", "", html, flags=re.S)  # commented example markup is not live

    # Broken local image references include picture/srcset, but prompt_only slots
    # deliberately have no img src and are handled separately below.
    for tag in re.findall(r'<(?:img|source)\b[^>]*>', html, re.I):
        for name in ('src',):
            reference = _attr(tag, name)
            path = _local_reference(reference, base)
            if path is not None and not path.is_file():
                errors.append(f'missing local image: {reference}')
        for reference in _srcset_references(_attr(tag, 'srcset')):
            path = _local_reference(reference, base)
            if path is not None and not path.is_file():
                errors.append(f'missing local srcset image: {reference}')

    allowed_roles = {'hero', 'support', 'spot'}
    allowed_purposes = {'explanatory', 'mnemonic', 'decorative'}
    slots = _figure_slots(html)
    expected_required = 0
    expected_total = 0
    for attrs, body, classes_str in slots:
        purpose = (_attr(attrs, 'data-image-purpose') or '').lower()
        state = (_attr(attrs, 'data-image-state') or 'ready').lower()
        role_match = re.search(r'\basset-slot--([a-z0-9-]+)\b', classes_str)
        role = role_match.group(1) if role_match else (_attr(attrs, 'data-image-role') or '')
        kind = (_attr(attrs, 'data-asset-kind') or 'paper-cut-v1').lower()
        img = re.search(r'<img\b[^>]*>', body, re.I | re.S)
        if purpose not in allowed_purposes:
            errors.append(f'asset slot has invalid image purpose: {purpose or "missing"}')
        if role not in allowed_roles:
            errors.append(f'asset slot has inactive or invalid role: {role or "missing"}')
        if kind not in {'paper-cut-v1', 'screenshot', 'photo', 'user-provided'}:
            errors.append(f'asset slot has invalid asset kind: {kind}')
        if kind == 'paper-cut-v1' and role not in allowed_roles:
            errors.append('paper-cut-v1 cannot use cover-object or section-overlay')
        if state == 'expected':
            expected_total += 1
            if img and _attr(img.group(0), 'src'):
                errors.append('prompt_only expected slot must not emit an img src')
            if not _attr(attrs, 'data-expected-src'):
                errors.append('expected slot is missing data-expected-src')
            if purpose in {'explanatory', 'mnemonic'}:
                expected_required += 1
        elif purpose in {'explanatory', 'mnemonic'}:
            if not img:
                errors.append(f'{purpose} slot is missing img')
            else:
                src = _attr(img.group(0), 'src')
                if not src or not src.strip():
                    errors.append(f'{purpose} ready image requires nonempty src')
                alt = _attr(img.group(0), 'alt')
                if not alt or not alt.strip():
                    errors.append(f'{purpose} image requires relational alt text')
        elif purpose == 'decorative':
            if img:
                alt = _attr(img.group(0), 'alt')
                hidden = (_attr(img.group(0), 'aria-hidden') or '').lower()
                if alt != '' or hidden != 'true':
                    errors.append('decorative image requires alt="" and aria-hidden="true"')
    if release and expected_total:
        errors.append(f'unresolved required/expected image slots: {expected_total}')
    elif expected_required:
        if not release:
            notes.append(f'prompt_only expected slots: {expected_required} (development only)')

    # S02 uses a dedicated width contract when it contains a ready hero/support image.
    section_ranges = _slide_section_ranges(html)
    for start, end, classes_str, _tag in section_ranges:
        section = html[start:end]
        if re.search(r'\bs02-slide\b', classes_str):
            ready_wide_slot = False
            for figure_tag in re.findall(r'<figure\b[^>]*>', section, re.I):
                figure_classes = _attr(figure_tag, 'class') or ''
                role_match = re.search(r'\basset-slot--(hero|support)\b', figure_classes)
                state = (_attr(figure_tag, 'data-image-state') or 'ready').lower()
                if role_match and state == 'ready':
                    ready_wide_slot = True
                    break
            if ready_wide_slot and not re.search(r'\bhas-image\b', classes_str):
                errors.append('S02 ready hero/support image requires section class has-image')

    # Content images are public components, never bare img tags. Fixed logos are exempt.
    slot_spans = [match.span() for match in re.finditer(r'<figure\b[^>]*class=["\'][^"\']*\basset-slot\b[^"\']*["\'][^>]*>.*?</figure>', html, re.I | re.S)]
    for image_match in re.finditer(r'<img\b[^>]*>', html, re.I):
        position = image_match.start()
        containing_section = None
        for start, end, classes_str, tag in section_ranges:
            if start <= position < end:
                containing_section = (start, end, classes_str, tag)
                break
        if containing_section is None or any(start <= position < end for start, end in slot_spans):
            continue
        image_classes = _attr(image_match.group(0), 'class') or ''
        if re.search(r'(?:^|\s)(?:s-logo|brand-logo|favicon|cover-logo)(?:\s|$)', image_classes, re.I):
            continue
        errors.append('content img outside asset-slot; screenshots require figure.asset-slot kind=screenshot')

    # Decorative images: one per part, never consecutive, never with a code viz.
    decorative_indexes, by_part, part = [], {}, 0
    for index, (start, end, classes_str, _tag) in enumerate(section_ranges):
        section = html[start:end]
        if re.search(r'\bpart-divider\b', classes_str):
            part += 1
        if re.search(r'data-image-purpose\s*=\s*["\']decorative["\']', section, re.I):
            decorative_indexes.append(index)
            by_part[part] = by_part.get(part, 0) + 1
            if count_code_viz(section):
                errors.append(f'decorative image shares slide {index + 1} with code visualization')
    if any(b == a + 1 for a, b in zip(decorative_indexes, decorative_indexes[1:])):
        errors.append('decorative images may not appear on consecutive slides')
    for part_number, count in by_part.items():
        if count > 1:
            errors.append(f'part {part_number} has {count} decorative images (maximum 1)')

    # Optional HTML/manifest/registry cross-check. Only explicit asset IDs are
    # matched, avoiding guesses for user-provided photos and screenshots.
    manifest = None
    if manifest_path:
        try:
            manifest = json.loads(Path(manifest_path).read_text(encoding='utf-8'))
            errors.extend(validate_manifest_document(manifest))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f'image manifest cannot be read: {exc}')
    registry = None
    if registry_path:
        try:
            registry = json.loads(Path(registry_path).read_text(encoding='utf-8'))
            try:
                from .verify_image_assets import verify_registry
            except ImportError:
                from verify_image_assets import verify_registry
            registry_reports, registry_errors = verify_registry(Path(registry_path))
            errors.extend(f'image registry: {error}' for error in registry_errors)
            for report in registry_reports:
                errors.extend(f'image registry: {error}' for error in report.errors)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f'image registry cannot be read: {exc}')
    entries = []
    if isinstance(registry, dict) and isinstance(registry.get('assets'), list):
        entries = registry['assets']
    registry_by_id = {str(item.get('id') or item.get('asset_id')): item for item in entries if isinstance(item, dict)}
    for attrs, body, _classes in slots:
        asset_id = _attr(attrs, 'data-asset-id')
        if not asset_id:
            continue
        entry = registry_by_id.get(asset_id)
        if registry is not None and entry is None:
            errors.append(f'HTML references unknown registry asset: {asset_id}')
        elif entry and entry.get('status') != 'approved':
            errors.append(f'HTML references non-approved asset: {asset_id}')
        elif entry:
            img = re.search(r'<img\b[^>]*>', body, re.I | re.S)
            src = _attr(img.group(0), 'src') if img else _attr(attrs, 'data-expected-src')
            registered = str(entry.get('file') or entry.get('path') or '')
            if src and registered and not Path(src).as_posix().endswith(Path(registered).as_posix()):
                errors.append(f'HTML path for {asset_id} does not match registry')
    if manifest is not None:
        manifest_text = json.dumps(manifest, ensure_ascii=False)
        for attrs, _body, _classes in slots:
            asset_id = _attr(attrs, 'data-asset-id')
            if asset_id and asset_id not in manifest_text:
                errors.append(f'HTML asset {asset_id} is missing from session manifest')
    return errors, notes

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("deck"); ap.add_argument("--parts", type=int, default=None)
    ap.add_argument("--release", action="store_true", help="배포 기준으로 expected 필수 슬롯을 실패 처리")
    ap.add_argument("--manifest", help="세션 자료/이미지-에셋.json 경로")
    ap.add_argument("--registry", help="중앙 이미지 registry.json 경로")
    ap.add_argument("--atlas", action="store_true", help="참조 아틀라스 덱(레이아웃/element 연속 열람용): 구도 다양성·연속 검사 제외")
    a = ap.parse_args()
    try:
        html = open(a.deck, encoding="utf-8").read()
    except OSError as e:
        print(f"[FAIL] 파일 열기: {e}"); sys.exit(1)
    html = re.sub(r"<!--.*?-->", "", html, flags=re.S)  # commented markup (examples, presenter notes) is not live

    tags, elements = parse_document(html)
    elements_by_start = {el.start: el for el in elements}

    results = []  # (level, msg)  level in PASS/WARN/FAIL
    def chk(cond, ok, bad, warn=False):
        results.append(("PASS" if cond else ("WARN" if warn else "FAIL"), ok if cond else bad))

    slide_els = _slide_elements(elements)
    ordered_slides = sorted(slide_els, key=lambda el: el.start)
    secs = find_sections(html, elements=elements)
    n = len(secs)
    chk(n >= 5, f"슬라이드 {n}장", f"슬라이드 {n}장 — 너무 적음(고정 4 + 본문 필요)")

    # ── 학생 덱 공통 계약: --parts N(N>0)일 때만 적용 ──
    # 카탈로그/아틀라스는 --parts 0을 사용하므로 힌트·헤더 데모를 허용한다.
    is_student_deck = a.parts is not None and a.parts > 0
    if is_student_deck:
        missing_header_logos = []
        for slide in ordered_slides:
            slide_id = slide.attrs.get('data-slide') or '(data-slide 없음)'
            headers = [el for el in elements
                       if el.name == 'header'
                       and slide.inner_start <= el.start < slide.inner_end
                       and 's-head' in classes(el.attrs)]
            if any(not any(
                header.inner_start <= tag.start < header.inner_end and 's-logo' in classes(tag.attrs)
                for tag in tags
            ) for header in headers):
                missing_header_logos.append(slide_id)
        chk(not missing_header_logos,
            "학생 덱 모든 .s-head에 표준 .s-logo 존재",
            f".s-head 안 .s-logo 누락 슬라이드: {missing_header_logos}")

        student_text = decoded_text(html)
        hint_classes = [tag.start for tag in tags if 'hint-reveal' in classes(tag.attrs)]
        banned_hint_labels = [label for label in ('강사 힌트', '막힐 때만 보기', '완성 예시 보기')
                              if label in student_text]
        chk(not hint_classes and not banned_hint_labels,
            "학생 덱 힌트 UI·강사용 문구 0",
            f"학생 덱 금지 힌트 잔존: hint-reveal {len(hint_classes)}개, 문구 {banned_hint_labels}")

    # ── 1주차 학생 덱 전용 계약(2026-07-21) ──
    # 다른 주차·카탈로그·발표자 노트에 오작동하지 않도록 파일 위치와 정본 파일명을 함께 본다.
    # 새 S01A/B/C의 존재 자체를 판별 조건으로 쓰면 누락된 덱이 검사를 우회하므로 경로를 기준으로 한다.
    # 2026-07-22: 편집본 구성 개편(79장/PART 5, S00 표지 신설). 배포본은 재빌드 전까지 72장/PART 6 유지.
    deck_file = Path(a.deck).resolve()
    is_week1_student_deck = (
        deck_file.parent.name == '1주차'
        and deck_file.stem in {'강의덱', '강의덱_배포'}
    )
    if is_week1_student_deck:
        slide_ids = [el.attrs.get('data-slide') or '' for el in ordered_slides]
        if deck_file.stem == '강의덱':
            # 편집본: S00 표지 신설 + PART divider 1장 감소로 79장.
            # 2026-07-22 2차: S39A·W04 삭제, 실습 PART 6 표지 신설 → 79장/divider 6.
            # 2026-07-23: 세션 요약(S61, concept-recap closing) 삭제로 78장.
            # 2026-07-23 2차: PART 3에 프롬프트·컨텍스트 엔지니어링, 구조적 한계(LM·SY),
            #   아첨 방지 요청문, 판단은 사람, "해.", 반복 수정 7장 신설로 85장.
            # 2026-07-23 3차: PART 3 간지 뒤에 S3MAP 흐름 안내를 추가해 86장.
            # 2026-07-24 4차: S3HUM 뒤에 도입 화면을 되짚는 S3ASK를 추가해 87장.
            # 2026-07-24 5차: S28A 성공 기준 슬라이드를 사용자 요청으로 삭제해 86장.
            expected_n, expected_dividers = 86, 6
            intro_expected = ['S00', 'S01', 'S01A', 'S01B', 'S01C']
        else:
            # 배포본(강의덱_배포): 2026-07-21) 48p(S39) 뒤에 완성 목표 쇼케이스 S39A를 추가해 71 → 72장.
            expected_n, expected_dividers = 72, 6
            intro_expected = ['S01', 'S01A', 'S01B', 'S01C']

        chk(n == expected_n,
            f"1주차 학생 덱({deck_file.stem}) 슬라이드 {expected_n}장",
            f"1주차 학생 덱({deck_file.stem}) 슬라이드 {n}장 ≠ {expected_n}장")

        intro_len = len(intro_expected)
        chk(slide_ids[:intro_len] == intro_expected,
            f"도입 {' → '.join(intro_expected)} 순서 유지",
            f"도입 슬라이드 순서 오류: {slide_ids[:intro_len]} (필요 {intro_expected})")

        if deck_file.stem == '강의덱':
            # 페이지 번호가 아니라 안정적인 data-slide ID로 PART 3의 학습 흐름을 고정한다.
            # S3MAP은 PART 3 간지 직후에 놓여야 하며, 이후의 핵심 전개도 같은 순서를 유지한다.
            part3_expected = ['P3', 'S3MAP', 'S3PE', 'S3LM', 'S3CE', '18', 'S3SY',
                              'S3SYP', 'S3HUM', 'S3ASK', 'S3DO', 'S3ITR']
            try:
                part3_start = slide_ids.index('P3')
            except ValueError:
                part3_actual = []
            else:
                part3_actual = slide_ids[part3_start:part3_start + len(part3_expected)]
            chk(part3_actual == part3_expected,
                f"PART 3 ID 순서 유지({' → '.join(part3_expected)})",
                f"PART 3 ID 순서 오류: {part3_actual} (필요 {part3_expected})")

        week1_dividers = sum(1 for el in ordered_slides if 'part-divider' in classes(el.attrs))
        chk(week1_dividers == expected_dividers,
            f"1주차 PART divider {expected_dividers}장",
            f"1주차 PART divider {week1_dividers}장 ≠ {expected_dividers}장")

        # 검정 터미널 두 장은 HTML 구조에서 dark + white-copy 계약을 명시해야 한다.
        # 현재 컴포넌트 명명(`.terminal-dark > .terminal-copy`)과 새 전용 명명
        # (`.dark-terminal.terminal-white-copy`)을 모두 허용하되, 둘 중 한 계약은 완결돼야 한다.
        terminal_contract_errors = []
        slide_by_id = {el.attrs.get('data-slide'): el for el in ordered_slides}
        for target_id in ('32',):
            target = slide_by_id.get(target_id)
            if target is None:
                terminal_contract_errors.append(f'{target_id}: 슬라이드 없음')
                continue
            terminal_tags = [tag for tag in tags
                             if target.inner_start <= tag.start < target.inner_end
                             and classes(tag.attrs) & {'dark-terminal', 'terminal-dark'}]
            if not terminal_tags:
                terminal_contract_errors.append(f'{target_id}: dark terminal class 없음')
                continue
            white_copy_ok = any('terminal-white-copy' in classes(tag.attrs) for tag in terminal_tags)
            if not white_copy_ok:
                white_copy_ok = any(
                    terminal_el is not None and any(
                        terminal_el.inner_start <= tag.start < terminal_el.inner_end
                        and 'terminal-copy' in classes(tag.attrs)
                        for tag in tags
                    )
                    for terminal_el in (elements_by_start.get(terminal.start) for terminal in terminal_tags)
                )
            if not white_copy_ok:
                terminal_contract_errors.append(f'{target_id}: white-copy contract class 없음')
        chk(not terminal_contract_errors,
            "32 검정 터미널 dark/white-copy 계약",
            "검정 터미널 계약 위반: " + " | ".join(terminal_contract_errors))

        last_slide = ordered_slides[-1] if ordered_slides else None
        last_text = (html[last_slide.inner_start:last_slide.inner_end] if last_slide is not None else '')
        chk(last_slide is not None and 'THANK YOU' in decoded_text(last_text),
            "마지막 슬라이드 THANK YOU 유지",
            f"마지막 슬라이드({slide_ids[-1] if slide_ids else '없음'})에 THANK YOU 없음")

    for key, marker in FIXED.items():
        found = any(marker in classes(el.attrs) for el in slide_els)
        chk(found, f"고정 슬라이드 {key} 존재", f"고정 슬라이드 {key} 없음")

    # ── 브랜드 표기: 헤더/표지 .s-brand는 영문 VIBECODING (2026-07-17) ──
    #   class 토큰 정확 매치(속성 순서 무관) + 실제 매칭된 닫는 태그까지의 내부 텍스트.
    brand_texts = []
    for tag in tags:
        if tag.name != 'span' or 's-brand' not in classes(tag.attrs):
            continue
        el = elements_by_start.get(tag.start)
        if el is not None:
            brand_texts.append(html[el.inner_start:el.inner_end])
    bad_brand = [t for t in brand_texts if '바이브코딩' in t]
    chk(not bad_brand, "브랜드 텍스트 VIBECODING(영문)",
        f".s-brand에 한글 브랜드 잔존 {len(bad_brand)}건 — VIBECODING으로 교체")

    # ── part-divider 수: <section> 클래스 토큰 정확 매치(따옴표 종류 무관) ──
    dividers = sum(1 for el in slide_els if 'part-divider' in classes(el.attrs))
    if a.parts is not None:
        chk(dividers == a.parts, f"part-divider {dividers} = 파트 {a.parts}",
            f"part-divider {dividers} ≠ 파트 {a.parts} (모든 파트 앞 divider 필수)")
    else:
        chk(dividers >= 1, f"part-divider {dividers}개", "part-divider 없음", warn=True)

    if dividers:
        dynamic_part_geometry = all(
            marker in html
            for marker in (
                "function partGeometry(n)",
                "function hydratePartDivider(s,index,total)",
                "data-geometry-count",
                "points=partGeometry(index)",
            )
        )
        chk(
            dynamic_part_geometry,
            "파트 번호 기반 지오메트리·도트 자동 생성기 존재",
            "파트 전환 자동 생성기 누락(partGeometry/hydratePartDivider)",
        )

    # ── 네비 엔진: class 토큰 정확 매치(속성 순서 무관, <nav class="navbar glass"> 통과) ──
    navbar_ok = any('navbar' in classes(t.attrs) for t in tags) or any(t.attrs.get('id') == 'controls' for t in tags)
    chk(navbar_ok, "네비 엔진 존재", "네비바(.navbar) 없음")
    chk('id="pdfBtn"' in html or "id='pdfBtn'" in html or 'dl-btn' in html,
        "PDF 버튼 존재", "PDF 버튼(#pdfBtn 또는 .dl-btn) 없음")
    nav_detail_ids = ('menuBtn', 'homeBtn', 'pageInput', 'slideList', 'pdfBtn')
    nav_detail_ok = all((f'id="{item}"' in html or f"id='{item}'" in html) for item in nav_detail_ids)
    chk(nav_detail_ok, "상세 발표 메뉴(홈·이동·목록·PDF) 존재", "상세 메뉴 기능 요소 누락")

    css_ok = 'deck.css' in html or ('<style' in html and '--blue' in html)
    leg_ok = 'legibility.css' in html or ('<style' in html and 'legibility' in html) or ('font-size:22px' in html)
    chk(css_ok, "deck.css 상속(링크/인라인)", "deck.css 미로드")
    chk(leg_ok, "강의장 가독성 레이어 로드", "legibility 미로드(본문 22px 하한 위험)", warn=True)

    # ── 본문 eyebrow의 PART 중복 금지: 헤더 .s-part(PART n/N)가 위치를 전담 (2026-07-17) ──
    #   .pd-eyebrow(파트전환, 'PART n/N' 슬래시 포맷)는 별개 클래스라 스캔 대상 아님.
    eyebrow_texts = re.findall(r'<p class="[^"]*\bs-eyebrow\b[^"]*"[^>]*>(.*?)</p>', html, re.S)
    part_dup = [re.sub(r'<[^>]+>', '', t).strip()[:30] for t in eyebrow_texts if re.search(r'PART\s*\d+\s*·', t)]
    chk(not part_dup, "본문 eyebrow에 PART n·파트명 중복 없음",
        f".s-eyebrow에 PART 형식 잔존 {part_dup[:5]} — 헤더 .s-part와 중복(삭제 대상)")

    # ── 시각 자료 구성 현황: 코드 시각화와 이미지는 정보 모양에 따라 동급 선택 ──
    # 로고/파비콘/표지 로고는 어느 쪽도 아니므로 img 집계에서 제외한다.
    LOGO_CLASSES = {'s-logo', 'brand-logo', 'favicon', 'cover-logo'}
    imgs = sum(1 for t in tags if t.name == 'img' and not (classes(t.attrs) & LOGO_CLASSES))
    viz = count_code_viz(html)
    results.append(("PASS", f"시각 자료 구성: 코드 시각화 {viz} · 이미지 {imgs} (정보 모양 기준)"))

    image_errors, image_notes = image_contract_checks(
        html,
        a.deck,
        release=a.release,
        manifest_path=a.manifest,
        registry_path=a.registry,
    )
    chk(not image_errors, "이미지 경로·목적·역할·배치 계약 준수",
        "이미지 계약 위반: " + " | ".join(image_errors))
    for note in image_notes:
        results.append(("WARN", note))

    # 콘텐츠 슬라이드(고정/divider 제외) 다양성
    content_els = [el for el in slide_els if not (classes(el.attrs) &
                   {'cover', 's02-slide', 's03-slide', 'part-divider', 'concept-recap', 'closing'})]
    content = [(el.attrs.get('class') or '', html[el.inner_start:el.inner_end]) for el in content_els]
    sigs = []
    for el, (cls, _inr) in zip(content_els, content):
        visible_inner = _strip_hidden_spans(html, el.inner_start, el.inner_end, elements)
        sigs.append(family_signature(cls, visible_inner))
    distinct = len(set(sigs))
    # 실제 덱에서 divider·고정 슬라이드가 끼면 시각 흐름도 끊긴다. 콘텐츠만
    # 압축한 목록에서 양쪽 파트의 마지막/첫 슬라이드를 붙여 세지 않는다.
    sig_by_start = {el.start: sig for el, sig in zip(content_els, sigs)}
    series_by_start = {el.start: (el.attrs.get('data-series') or '').strip() for el in content_els}

    # 2026-07-23(재수정): 연속 검사용 시그니처는 패밀리보다 data-series를 우선한다.
    # 런을 패밀리 시그니처로 먼저 묶으면, 연작 바로 옆에 우연히 같은 패밀리인 비연작
    # 슬라이드가 붙었을 때 런이 연작보다 커져 "런 전체가 같은 series"가 아니게 되고
    # 예외가 통째로 무력화된다(게이트 반려 사유). data-series가 있으면 그 값으로 런
    # 시그니처를 대체해 연작과 우연한 동일 패밀리를 애초에 다른 런으로 분리한다.
    # data-series가 없는 슬라이드는 기존 패밀리 시그니처를 그대로 쓴다.
    run_sig_by_start = {
        start: (f'series:{series}' if series else sig_by_start[start])
        for start, series in series_by_start.items()
    }

    # 시그니처 연속 런을 실제 문서 순서로 구성한다(고정/디바이더 슬라이드가 끼면 런이 끊긴다).
    runs = []  # [{'run_sig', 'length': N}]
    cur_run_sig, cur_len = None, 0
    for slide in sorted(slide_els, key=lambda el: el.start):
        run_sig = run_sig_by_start.get(slide.start)
        if run_sig is None:
            if cur_len:
                runs.append({'run_sig': cur_run_sig, 'length': cur_len})
            cur_run_sig, cur_len = None, 0
            continue
        if run_sig == cur_run_sig:
            cur_len += 1
        else:
            if cur_len:
                runs.append({'run_sig': cur_run_sig, 'length': cur_len})
            cur_run_sig, cur_len = run_sig, 1
    if cur_len:
        runs.append({'run_sig': cur_run_sig, 'length': cur_len})

    # 의도된 연작(인접 슬라이드가 같은 data-series 값을 공유)은 같은 구도 연속 카운트를
    # 올리지 않는다 — data-series 없는 슬라이드는 기존 규칙 그대로 적용된다.
    # 조용한 우회가 되지 않도록 예외가 적용된 구간은 항상 로그로 남긴다.
    maxrun = 0
    series_exempt_notes = []
    for run_info in runs:
        length = run_info['length']
        run_sig = run_info['run_sig']
        if length > 1 and run_sig.startswith('series:'):
            series_exempt_notes.append(f'data-series="{run_sig[len("series:"):]}" {length}장')
            continue
        maxrun = max(maxrun, length)

    is_reference_atlas = a.atlas
    if content and not is_reference_atlas:
        need = diversity_need(len(content))
        chk(distinct >= need,
            f"구도 다양성: {distinct}종 / 본문 {len(content)}장(필요 {need})",
            f"구도 다양성 낮음: {distinct}종 / 본문 {len(content)}장(필요 {need}, 단조 위험)", warn=True)
        series_suffix = f" · 연작 예외: {' · '.join(series_exempt_notes)}" if series_exempt_notes else ""
        chk(maxrun <= 2, f"같은 구도 최장 연속 {maxrun} (≤2){series_suffix}",
            f"같은 구도 {maxrun}연속 — 3연속 금지 위배 (시그니처 반복: {sigs}){series_suffix}")
    elif content:
        chk(True, "참조 아틀라스(--atlas): 다양성·연속 검사 제외(50 레이아웃·21 element 연속열람용)", "")

    # ── L2 CSS 수집: 덱 인라인 <style> + 덱이 실제로 링크한 로컬 CSS(주석 제거) ──
    bundle = collect_css(html, a.deck, tags=tags, elements=elements)
    style_attr_decls = _style_attr_declarations(tags)

    if bundle.raw_byte_count == 0:
        results.append(("WARN", "덱 CSS를 0바이트 읽음 — CSS 검사 미수행"))
    else:
        # ── raw #hex · rgba()/hsl() · CSS 명명색: CSS 규칙 + style=(따옴표 무관) + SVG fill=/stroke= ──
        color_hits = find_color_violations(bundle.deck_inline)
        for _tag, decls in style_attr_decls:
            for prop, val in decls.items():
                if not prop.startswith('--'):
                    color_hits.extend(_color_literal_hits(val))
        for t in tags:
            color_hits.extend(_color_literal_hits(t.attrs.get('fill')))
            color_hits.extend(_color_literal_hits(t.attrs.get('stroke')))
        chk(len(color_hits) == 0, "토큰만 사용(raw #hex 0)",
            f"raw #hex/rgba·hsl()/명명색 {len(color_hits)}건({sorted(set(map(str, color_hits)))[:6]}) — var(--token)로 교체")

        # ── 덱 자체 <style>/인라인 style 그라디언트 금지 (flat-fill 원칙) ──
        dgrad = len(re.findall(r'\b(?:linear|radial|conic)-gradient', bundle.deck_inline))
        for _tag, decls in style_attr_decls:
            for val in decls.values():
                dgrad += len(re.findall(r'\b(?:linear|radial|conic)-gradient', val))
        chk(dgrad == 0, "덱 인라인 그라디언트 0 (flat-fill)",
            f"덱 <style>/style=에 gradient {dgrad}건 — flat-fill 원칙 위배")

        # ── 덱 자체 <style>/인라인 style var(--navy) 금지 (fallback 폼 var(--navy, ...) 포함) ──
        navy_re = re.compile(r'var\(\s*--navy\s*(?:,[^)]*)?\)')
        dnavy = len(navy_re.findall(bundle.deck_inline))
        for _tag, decls in style_attr_decls:
            for val in decls.values():
                dnavy += len(navy_re.findall(val))
        chk(dnavy == 0, "덱 인라인 var(--navy) 0",
            f"덱 <style>/style=에 var(--navy) {dnavy}건 — navy 사용 금지(어두운 배경/텍스트는 --ink)")

        # ── 덱 자체 박스 표면 규칙: 흰 fill + 근백색(--line) 축약 보더 조합 금지 ──
        deck_box_bad = box_surface_violations(bundle.deck_inline)
        for tag, decls in style_attr_decls:
            if _box_violation_decls(decls):
                deck_box_bad.append('style="' + (tag.attrs.get('style') or '')[:40] + '…"')
        chk(not deck_box_bad, "덱 인라인 박스 표면 규칙 준수(흰 fill+--line 보더 0)",
            f"덱 인라인 흰 fill+근백색 보더 박스 {deck_box_bad} — 틴트 fill 또는 유색 보더(--blue-line-strong 등)로 교체")

        # ── 아젠다 배지 플랫: .an-num 선언에 box-shadow 금지 (kit CSS+덱 인라인 모두, @media 안까지) ──
        an_num_bad = 0
        for selector_group, decls, _body, _at in iter_rules(bundle.all):
            if 'box-shadow' not in decls:
                continue
            for sel in selector_group.split(','):
                if re.search(r'(?<![\w-])\.an-num(?![\w-])', sel):
                    an_num_bad += 1
                    break
        chk(an_num_bad == 0, ".an-num 플랫(box-shadow 없음)",
            f".an-num 선언에 box-shadow {an_num_bad}건 — v3 플랫 배지(그림자 제거)")

        # ── 흰색 글래스 내비게이션 토큰 존재(kit CSS에 정의 → 링크된 로컬 CSS까지 합산해 검사) ──
        chk('--glass-white' in bundle.all and re.search(r'backdrop-filter\s*:\s*blur', bundle.all),
            "흰색 글래스 내비게이션 토큰 존재", "글래스 내비게이션 토큰/효과 없음")

    # ── 진행도트·페이지번호 자동 주입 스크립트 존재 (s-pageno + s-part) ──
    scripts = " ".join(re.findall(r'<script[^>]*>(.*?)</script>', html, re.S))
    inject_ok = ('s-pageno' in scripts) and ('s-part' in scripts)
    chk(inject_ok, "진행·페이지 자동주입(s-pageno+s-part) 존재",
        "s-pageno/s-part 자동주입 스크립트 없음 — 페이지번호·파트도트 누락 위험", warn=True)

    # ── [kit] 공유 kit CSS(deck.css · patterns.css · legibility.css) 무결성:
    #     스크립트 위치 기준 해석(cwd·덱경로 무관) — 덱이 아니라 저장소 kit을 검사한다. ──
    _here = os.path.dirname(os.path.abspath(__file__))
    def _read_css(*parts):
        p = os.path.join(_here, *parts)
        try:
            return open(p, encoding='utf-8').read()
        except OSError:
            return None
    kit_files = {
        'deck.css': ('..', 'kit', 'styles', 'deck.css'),
        'patterns.css': ('..', 'kit', 'styles', 'patterns.css'),
        'legibility.css': ('..', 'kit', 'styles', 'legibility.css'),
    }
    kit_sources = {}
    for label, rel_parts in kit_files.items():
        file_text = _read_css(*rel_parts)
        kit_sources[label] = file_text
        if file_text is None:
            results.append(("WARN", f"[kit] {label} 읽기 실패 — 관련 검사 생략"))
    deckcss = kit_sources['deck.css']
    patterns = kit_sources['patterns.css']
    legibility = kit_sources['legibility.css']
    kit_css = _strip_css_comments("\n".join(c for c in (deckcss, patterns, legibility) if c is not None))

    if kit_css:
        # (0) [kit] raw #hex 0 (결정 3 — 측정 범위와 일치: hex만, rgba/명명색은 대상 아님)
        kit_hex_hits = find_color_violations(kit_css, hex_only=True)
        chk(not kit_hex_hits, "[kit] 토큰만 사용(raw #hex 0)",
            f"[kit] raw #hex {len(kit_hex_hits)}건({sorted(set(kit_hex_hits))[:6]}) — var(--token)로 교체")
        # (1) 그라디언트 0 (deck.css + patterns.css + legibility.css)
        kgrad = len(re.findall(r'\b(?:linear|radial|conic)-gradient', kit_css))
        chk(kgrad == 0, "[kit] CSS 그라디언트 0 (flat-fill)",
            f"[kit] CSS에 gradient {kgrad}건 — flat-fill 원칙 위배")
        # (2) var(--navy) 미사용(fallback 폼 포함, 정의 줄 --navy: 는 매칭 안 됨 → 허용)
        navy_re = re.compile(r'var\(\s*--navy\s*(?:,[^)]*)?\)')
        knavy = len(navy_re.findall(kit_css))
        chk(knavy == 0, "[kit] var(--navy) 미사용", f"[kit] var(--navy) {knavy}건 사용 — v2 팔레트 제외 대상")
        # (2b) 새 구조 요소는 보조 블루(ice/electric)가 아니라 --blue를 사용한다(fallback 폼 포함).
        css_without_root = re.sub(r':root\s*\{.*?\}', '', kit_css, flags=re.S)
        legacy_blue_re = re.compile(r'var\(\s*--(?:ice|electric)\s*(?:,[^)]*)?\)')
        legacy_blue = len(legacy_blue_re.findall(css_without_root))
        chk(legacy_blue == 0, "[kit] 레거시 보조 블루(ice/electric) 렌더 사용 0",
            f"[kit] var(--ice)/var(--electric) {legacy_blue}건 — 구조·주 강조는 --blue만 사용")
        # (2c) 박스 표면 규칙: 흰 카드가 근백색 --line 보더만으로 구분되면 안 된다(2026-07-16).
        kit_box_bad = box_surface_violations(kit_css)
        chk(not kit_box_bad, "[kit] 박스 표면 규칙 준수(흰 fill+--line 축약보더 0)",
            f"[kit] 흰 fill+근백색 보더 박스 {kit_box_bad} — 틴트 fill 또는 유색 보더(--blue-line-strong/--mint-line/--coral-line)로 교체")

    if deckcss is not None:
        # (3) :root 토큰 값 정확성(부분문자열 매칭 · 공백정규화 · hex 대소문자 무시)
        rootm = re.search(r':root\s*\{(.*?)\}', deckcss, re.S)
        root_norm = re.sub(r'\s+', '', rootm.group(1)).lower() if rootm else ''
        need_tokens = ['--blue:#1D4ED8', '--mint:#14B8A6', '--coral:#F97360', '--red:#DC2626',
                       '--mint-deep:#0F766E', '--coral-deep:#C2452F',
                       '--on-mint', '--on-coral', '--r-lg:20px', '--font-mono', '--mint-line']
        miss_tokens = [t for t in need_tokens if re.sub(r'\s+', '', t).lower() not in root_norm]
        chk(not miss_tokens, f"[kit] 토큰 값 정확(deck.css :root, {len(need_tokens)}개 확인)",
            f"[kit] 토큰 누락/값변경: {miss_tokens}")
        # (3b) 헤더 선과 민트 강조 프리미티브는 공용 CSS 계약을 지킨다.
        def css_block(selector):
            m = re.search(r'(?:^|[}\n;,{])\s*' + selector + r'\s*\{([^}]*)\}', deckcss)
            return re.sub(r'\s+', '', m.group(1)) if m else ''
        sline = css_block(r'\.s-line')
        chk('background:var(--blue)' in sline, "[kit] 상단 헤더 선은 main blue(--blue)",
            "[kit] .s-line이 --blue 배경이 아님")
        mint_mark = css_block(r'\.hl-mint-mark')
        mark_need = ['display:inline-block', 'background:var(--mint)', 'color:var(--white)',
                     'padding:03px1px', 'border-radius:0']
        missing_mark = [x for x in mark_need if x not in mint_mark]
        chk(not missing_mark, "[kit] 민트 글자폭 강조(.hl-mint-mark) 계약 유지",
            f"[kit] .hl-mint-mark 계약 누락: {missing_mark}")
        shape_mint = css_block(r'\.shape-mint')
        chk('background:var(--mint)!important' in shape_mint and 'color:var(--on-mint)!important' in shape_mint,
            "[kit] 민트 도형 강조(.shape-mint) 계약 유지", "[kit] .shape-mint의 민트 fill/on-mint 글자 계약 누락")
        # (3c) 넘버 행 정렬 계약: .work-step은 배지 기준 텍스트 수직 중앙(2026-07-16)
        ws = css_block(r'\.work-step')
        chk('align-items:center' in ws, "[kit] 넘버 행 수직 중앙(.work-step align-items:center) 유지",
            "[kit] .work-step이 align-items:center가 아님 — 원형 배지 대비 텍스트 중앙 정렬 규칙 위반")
        # (3d) 아젠다 행 정렬 계약: .agenda-item도 배지 기준 텍스트 수직 중앙(결정 2 — 이미 준수 중, 강제만 추가).
        #      문서화된 예외 .s03-slide .an-item(커넥터 좌표 전제)은 별개 셀렉터라 이 검사에 끌려오지 않는다.
        agenda_item = css_block(r'\.agenda-item')
        chk('align-items:center' in agenda_item, "[kit] 아젠다 행 수직 중앙(.agenda-item align-items:center) 유지",
            "[kit] .agenda-item이 align-items:center가 아님 — 원형 배지 대비 텍스트 중앙 정렬 규칙 위반")
        # (4) 민트 배지 셀렉터가 background:var(--mint) 유지 (다른 노드 셀렉터는 검사 안 함)
        badge_sels = [r'\.num-circle', r'\.work-step\s+\.n', r'\.pd-dot\.is-active']
        bad_badge = []
        for sel in badge_sels:
            m = re.search(r'(?:^|[}\n;,{])\s*' + sel + r'\s*(\{)', deckcss)
            block = ''
            if m:
                s = m.start(1)
                e = deckcss.find('}', s)
                block = re.sub(r'\s+', '', deckcss[s:e if e != -1 else len(deckcss)])
            if 'background:var(--mint)' not in block:
                bad_badge.append(sel.replace('\\', ''))
        chk(not bad_badge, "[kit] 민트 배지 3종 background:var(--mint) 유지",
            f"[kit] 민트 배지 색 이탈(background:var(--mint) 아님): {bad_badge}")

    # a11y: role="img"(코드 시각화)마다 비어있지 않은 aria-label (속성 기반, 값 안의 '>' 무관)
    role_img_tags = [t for t in tags if (t.attrs.get('role') or '').strip() == 'img']
    role_img = len(role_img_tags)
    labeled = sum(1 for t in role_img_tags if (t.attrs.get('aria-label') or '').strip())
    if role_img:
        chk(labeled >= role_img, f"코드시각화 aria 라벨: {labeled}/{role_img}",
            f"role=img {role_img}개 중 aria-label 있는 건 {labeled}개 — 나머지 라벨 없음(접근성)")

    # 색은 문법: 콘텐츠 슬라이드당 서로 다른 callout 색이 3종↑이면 색 남용 경고
    overcolor = []
    for i, (c, inr) in enumerate(content):
        cols = set(re.findall(r'callout\s+(blue|green|orange|red|yellow)', inr))
        if len(cols) >= 3:
            overcolor.append(str(i + 1) + ':' + '/'.join(sorted(cols)))
    chk(len(overcolor) == 0, "색 남용 없음(슬라이드당 callout 색 <3)",
        f"색 과다 슬라이드 {overcolor} — 경고색은 실제 의미가 있을 때만 사용하도록 원칙 재검토", warn=True)

    # ── 힌트 리빌(.hint-reveal): <summary> 존재 확인 (빈 disclosure = 접근성/사용성 위험) ──
    hint_blocks = re.findall(r'<details[^>]*class="[^"]*\bhint-reveal\b[^"]*"[^>]*>(.*?)</details>', html, re.S)
    if hint_blocks:
        no_summary = sum(1 for b in hint_blocks if '<summary' not in b)
        chk(no_summary == 0, f"힌트 리빌 {len(hint_blocks)}개 모두 <summary> 있음",
            f".hint-reveal {no_summary}개에 <summary> 없음 — 펼침 트리거 없는 빈 힌트(접근성)", warn=True)

    # ── 원고 아이콘 마커 누출 금지 (💬/🗣/👀는 조립 시 라우팅되고 최종 HTML엔 남으면 안 됨) ──
    #   <script>/<style> 제외(대소문자 무시) + 엔티티 디코드된 텍스트에서 코드포인트 탐지
    #   → HTML 엔티티(&#128172; 등)로 우회해도 잡힌다.
    body_wo_code = decoded_text(html)
    leaked = [m for m in ('\U0001F4AC', '\U0001F5E3', '\U0001F440') if m in body_wo_code]  # 💬 🗣 👀
    leak_names = {'\U0001F4AC': '💬', '\U0001F5E3': '🗣', '\U0001F440': '👀'}
    chk(not leaked, "원고 아이콘 마커(💬/🗣/👀) 누출 0",
        f"아이콘 마커 {[leak_names[m] for m in leaked]} 최종 HTML에 잔존 — 학생 덱에서 제거하고 발표자 노트로 라우팅해야 함")

    # 출력
    order = {"FAIL": 0, "WARN": 1, "PASS": 2}
    for lvl, msg in sorted(results, key=lambda r: order[r[0]]):
        mark = {"PASS": "✓", "WARN": "△", "FAIL": "✗"}[lvl]
        print(f"[{lvl}] {mark} {msg}")
    fails = sum(1 for l, _ in results if l == "FAIL")
    warns = sum(1 for l, _ in results if l == "WARN")
    print(f"\n요약: FAIL {fails} · WARN {warns} · PASS {len(results)-fails-warns}")
    print("※ 오버플로·콘솔에러·가독성(computed)은 브라우저 측정 필요: "
          "python -m http.server 후 슬라이드별 scrollWidth/Height ≤ client, 콘솔 에러 0 확인.")
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
