#!/usr/bin/env python3
"""verify_deck.py — vibecoding-deck 산출 덱 정적 검증 (측정 우선, 의존성 0).

사용: python scripts/verify_deck.py <deck.html> [--parts N]

정적으로 채점하는 것(브라우저 없이):
  - 슬라이드 수 · 고정 슬라이드(cover/s02/s03/concept-recap) 존재
  - part-divider 수 (= --parts N 이면 일치 검사)
  - 네비 엔진(.navbar) · 상세 메뉴 PDF 출력 버튼(#pdfBtn)
  - deck.css + legibility-40s.css 로드(링크 또는 인라인)
  - 코드 시각화(.viz-*/.code-*/<svg>/막대) vs <img> 개수 (code-viz 우선 원칙)
  - 콘텐츠 슬라이드 구도 다양성: 서로 다른 구조 시그니처 수 · 같은 구도 최장 연속
  - raw #hex 색이 :root/토큰 밖에서 쓰였는지(토큰-only 대략 검사)
  - 덱 인라인 <style>/style= 그라디언트 금지(flat-fill) · 덱 인라인 var(--navy) 금지 · 진행/페이지 자동주입 스크립트(s-pageno+s-part)
  - 표지 3큐브(9면)+코랄 스파크 · 공유 kit CSS의 메인 블루 헤더 선 ·
    민트 강조 프리미티브 · 토큰/민트 배지 무결성
  - 박스 표면 규칙: 흰 fill(--white/--surface-alt) + 근백색 축약 보더(--line) 조합 금지
    (kit CSS + 덱 인라인 <style>/style= 모두 · 방향 지정 border-top/-bottom/-left는 내부 구분선으로 허용)
  - .work-step 수직 중앙 정렬(align-items:center) 계약

브라우저로만 되는 것(오버플로·콘솔·가독성 computed)은 이 스크립트가 안 하고 리마인더만 출력.
종료코드: FAIL 있으면 1, 아니면 0.
"""
import sys, re, os, argparse
from pathlib import Path
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows cp949 콘솔 대응
except Exception:
    pass

FIXED = {"cover": r'class="[^"]*\bcover\b', "s02": r'class="[^"]*\bs02-slide\b',
         "s03": r'class="[^"]*\bs03-slide\b', "recap": r'class="[^"]*\bconcept-recap\b'}

def find_sections(html):
    # <section ... class="slide ...">  → (full_class_attr, inner_html_until_next_section_or_end)
    secs = []
    for m in re.finditer(r'<section[^>]*class="([^"]*\bslide\b[^"]*)"[^>]*>', html):
        start = m.end()
        nxt = html.find("<section", start)
        inner = html[start: nxt if nxt != -1 else len(html)]
        secs.append((m.group(1), inner))
    return secs

def family_signature(cls, inner):
    """콘텐츠 슬라이드의 구조 시그니처(단조 감지용)."""
    sig = []
    # 본문 컨테이너 = 구도 축
    if re.search(r'\bcenter-msg\b', cls) or 'class="center-msg' in inner: sig.append("centered")
    elif 'class="s-body-wrap' in inner: sig.append("split/leftcol")
    elif 'class="s-full' in inner or 'canvas-fill' in cls: sig.append("full")
    else: sig.append("other")
    # 콘텐츠 마커
    if re.search(r'class="[^"]*\bgrid-[23]\b', inner) or 'revenue-grid' in inner: sig.append("grid")
    if 'table' in inner and re.search(r'class="t\b', inner): sig.append("table")
    if re.search(r'class="[^"]*\bviz-', inner) or 'code-chart' in inner or 'code-diagram' in inner or '<svg' in inner: sig.append("viz")
    if 'compare2' in inner: sig.append("compare")
    if 'work-step' in inner or 'flow-step' in inner: sig.append("flow")
    if 'shot-annot' in inner or 'shot-win' in inner: sig.append("shot")
    return "+".join(sig)


# 박스 표면 규칙 예외: 상태 도트·코드/터미널 표면·주석 스크린샷 창·캔버스/문서 루트·@블록
BOX_EXEMPT = re.compile(r'@|\.pd-dot|\.co-bar|\.cover-terminal|\.shot-|\.slide\b|\bbody\b|\bhtml\b|:root')

def box_surface_violations(css_text):
    """흰 fill(--white/--surface-alt) + 근백색(--line) '축약' 보더 조합 = 박스 표면 규칙 위반.
    방향 지정 보더(border-top/-bottom/-left/-right)는 내부 구분선이라 합법."""
    bad = []
    for m in re.finditer(r'([^{}]+)\{([^}]*)\}', css_text):
        sel, body = m.group(1).strip(), m.group(2)
        if BOX_EXEMPT.search(sel):
            continue
        if not re.search(r'background\s*:\s*var\(--(?:white|surface-alt)\)', body):
            continue
        if re.search(r'(?:^|;)\s*border\s*:[^;]*var\(--line\)', body):
            bad.append(sel.split(',')[0].strip()[:40])
    return bad

def local_linked_css(html, deck_path):
    """덱이 링크한 로컬 CSS를 읽는다. 외부 URL과 누락 파일은 건너뛴다."""
    chunks = []
    base = Path(deck_path).resolve().parent
    for href in re.findall(r'<link\b[^>]*\bhref=["\']([^"\']+)["\'][^>]*>', html, re.I):
        clean = href.split("?", 1)[0].split("#", 1)[0]
        if not clean or re.match(r'^(?:https?:|data:|//)', clean, re.I):
            continue
        css_path = (base / clean).resolve()
        if css_path.is_file() and css_path.suffix.lower() == ".css":
            try:
                chunks.append(css_path.read_text(encoding="utf-8"))
            except OSError:
                pass
    return "\n".join(chunks)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("deck"); ap.add_argument("--parts", type=int, default=None)
    a = ap.parse_args()
    try:
        html = open(a.deck, encoding="utf-8").read()
    except OSError as e:
        print(f"[FAIL] 파일 열기: {e}"); sys.exit(1)

    results = []  # (level, msg)  level in PASS/WARN/FAIL
    def chk(cond, ok, bad, warn=False):
        results.append(("PASS" if cond else ("WARN" if warn else "FAIL"), ok if cond else bad))

    secs = find_sections(html)
    n = len(secs)
    chk(n >= 5, f"슬라이드 {n}장", f"슬라이드 {n}장 — 너무 적음(고정 4 + 본문 필요)")

    for key, pat in FIXED.items():
        chk(re.search(pat, html) is not None, f"고정 슬라이드 {key} 존재", f"고정 슬라이드 {key} 없음")

    # 표지 불변요소: 3개 큐브(data-cube) × 각 3면 = polygon 9개, 코랄 스파크 1개
    cover_inner = next((inner for cls, inner in secs if re.search(r'\bcover\b', cls)), '')
    cube_count = len(re.findall(r'<g\b[^>]*\bdata-cube=', cover_inner))
    cover_faces = len(re.findall(r'<polygon\b', cover_inner))
    spark_count = len(re.findall(r'<circle\b[^>]*fill="var\(--coral\)"', cover_inner))
    chk(cube_count == 3 and cover_faces == 9 and spark_count >= 1,
        "표지 3큐브·9면·코랄 스파크 유지",
        f"표지 도형 불완전: cube={cube_count}, polygon={cover_faces}, coral spark={spark_count}")

    dividers = len(re.findall(r'class="[^"]*\bpart-divider\b', html))
    if a.parts is not None:
        chk(dividers == a.parts, f"part-divider {dividers} = 파트 {a.parts}",
            f"part-divider {dividers} ≠ 파트 {a.parts} (모든 파트 앞 divider 필수)")
    else:
        chk(dividers >= 1, f"part-divider {dividers}개", "part-divider 없음", warn=True)

    chk('class="navbar"' in html or "id=\"controls\"" in html, "네비 엔진 존재", "네비바(.navbar) 없음")
    chk('id="pdfBtn"' in html or "id='pdfBtn'" in html or 'dl-btn' in html,
        "PDF 버튼 존재", "PDF 버튼(#pdfBtn 또는 .dl-btn) 없음")
    nav_detail_ids = ('menuBtn', 'homeBtn', 'pageInput', 'slideList', 'pdfBtn')
    nav_detail_ok = all((f'id="{item}"' in html or f"id='{item}'" in html) for item in nav_detail_ids)
    chk(nav_detail_ok, "상세 발표 메뉴(홈·이동·목록·PDF) 존재", "상세 메뉴 기능 요소 누락")
    rendered_css = html + "\n" + local_linked_css(html, a.deck)
    chk('--glass-white' in rendered_css and re.search(r'backdrop-filter\s*:\s*blur', rendered_css),
        "흰색 글래스 내비게이션 토큰 존재", "글래스 내비게이션 토큰/효과 없음")

    css_ok = 'deck.css' in html or ('<style' in html and '--blue' in html)
    leg_ok = 'legibility-40s.css' in html or ('<style' in html and 'legibility' in html) or ('font-size:22px' in html)
    chk(css_ok, "deck.css 상속(링크/인라인)", "deck.css 미로드")
    chk(leg_ok, "40~50대 가독성 레이어 로드", "legibility-40s 미로드(본문 22px 하한 위험)", warn=True)

    imgs = len(re.findall(r'<img\b', html))
    viz = len(re.findall(r'class="[^"]*\bviz-', html)) + len(re.findall(r'\bcode-(chart|diagram)\b', html)) + len(re.findall(r'<svg\b', html))
    chk(viz >= imgs, f"코드 시각화 {viz} ≥ 이미지 {imgs} (code-viz 우선)",
        f"이미지 {imgs} > 코드 시각화 {viz} — 코드 우선 원칙 위배 소지", warn=True)

    # 콘텐츠 슬라이드(고정/divider 제외) 다양성
    content = [(c, inr) for (c, inr) in secs
               if not re.search(r'\b(cover|s02-slide|s03-slide|part-divider|concept-recap|closing)\b', c)]
    sigs = [family_signature(c, inr) for (c, inr) in content]
    distinct = len(set(sigs))
    maxrun, run = 1, 1
    for i in range(1, len(sigs)):
        run = run + 1 if sigs[i] == sigs[i-1] else 1
        maxrun = max(maxrun, run)
    is_reference_atlas = 'atlas-slide' in html and 'LAYOUT ATLAS' in html
    if content and not is_reference_atlas:
        chk(distinct >= max(3, len(content)//2),
            f"구도 다양성: {distinct}종 / 본문 {len(content)}장",
            f"구도 다양성 낮음: {distinct}종 / 본문 {len(content)}장 (단조 위험)", warn=True)
        chk(maxrun <= 2, f"같은 구도 최장 연속 {maxrun} (≤2)",
            f"같은 구도 {maxrun}연속 — 3연속 금지 위배 (시그니처 반복: {sigs})")
    elif content:
        chk(True, "참조 아틀라스: 50 레이아웃·21 element 연속열람용 다양성 검사 제외", "")

    # 토큰-only 대략 검사: <style>/인라인 style 안 raw #hex
    #   스킵 규칙(둘 중 하나면 스킵): (1) :root{...} 블록 내부  (2) 토큰 정의 줄(첫 ':' 앞부분에 '--' 포함)
    #   → inline_deck.py로 deck.css가 통째로 인라인돼도 토큰 정의(:root 내부·--name:#hex)는 오탐 안 나게.
    style_blocks = re.findall(r'<style[^>]*>(.*?)</style>', html, re.S)
    inline_styles = re.findall(r'style="([^"]*)"', html)
    hexhits = []
    for blk in style_blocks:
        in_root = False
        for ln in blk.splitlines():
            if ':root' in ln and '{' in ln:
                in_root = True
            head = ln.split(':', 1)[0]          # 첫 콜론 앞 = 셀렉터/속성명 영역
            if in_root or '--' in head:          # :root 블록 안이거나 토큰 정의 줄이면 스킵
                if in_root and '}' in ln:        # :root 블록 종료 감지
                    in_root = False
                continue
            hexhits += re.findall(r'#[0-9a-fA-F]{3,6}\b', ln)
    for st in inline_styles:
        hexhits += re.findall(r'#[0-9a-fA-F]{3,6}\b', st)
    chk(len(hexhits) == 0, "토큰만 사용(raw #hex 0)",
        f"raw #hex {len(hexhits)}건({sorted(set(hexhits))[:6]}) — var(--token)로 교체", warn=True)

    # ── 덱 자체 <style>/인라인 style 그라디언트 금지 (flat-fill 원칙) ──
    deck_style_text = "\n".join(style_blocks) + "\n" + "\n".join(inline_styles)
    dgrad = len(re.findall(r'\b(?:linear|radial|conic)-gradient', deck_style_text))
    chk(dgrad == 0, "덱 인라인 그라디언트 0 (flat-fill)",
        f"덱 <style>/style=에 gradient {dgrad}건 — flat-fill 원칙 위배")

    # ── 덱 자체 <style>/인라인 style var(--navy) 금지 (navy는 v2 팔레트 제외) ──
    dnavy = len(re.findall(r'var\(\s*--navy\s*\)', deck_style_text))
    chk(dnavy == 0, "덱 인라인 var(--navy) 0",
        f"덱 <style>/style=에 var(--navy) {dnavy}건 — navy 사용 금지(어두운 배경/텍스트는 --ink)")

    # ── 덱 자체 박스 표면 규칙: 흰 fill + 근백색(--line) 축약 보더 조합 금지 ──
    deck_box_bad = box_surface_violations("\n".join(style_blocks))
    for st in inline_styles:
        if re.search(r'background\s*:\s*var\(--(?:white|surface-alt)\)', st) and \
           re.search(r'(?:^|;)\s*border\s*:[^;]*var\(--line\)', st):
            deck_box_bad.append('style="' + st[:40] + '…"')
    chk(not deck_box_bad, "덱 인라인 박스 표면 규칙 준수(흰 fill+--line 보더 0)",
        f"덱 인라인 흰 fill+근백색 보더 박스 {deck_box_bad} — 틴트 fill 또는 유색 보더(--blue-line-strong 등)로 교체")

    # ── 진행도트·페이지번호 자동 주입 스크립트 존재 (s-pageno + s-part) ──
    scripts = " ".join(re.findall(r'<script[^>]*>(.*?)</script>', html, re.S))
    inject_ok = ('s-pageno' in scripts) and ('s-part' in scripts)
    chk(inject_ok, "진행·페이지 자동주입(s-pageno+s-part) 존재",
        "s-pageno/s-part 자동주입 스크립트 없음 — 페이지번호·파트도트 누락 위험", warn=True)

    # ── 공유 kit CSS(deck.css · patterns.css) 무결성: 스크립트 위치 기준 해석(cwd·덱경로 무관) ──
    _here = os.path.dirname(os.path.abspath(__file__))
    def _read_css(*parts):
        p = os.path.join(_here, *parts)
        try:
            return open(p, encoding='utf-8').read()
        except OSError:
            return None
    deckcss = _read_css('..', 'kit', 'styles', 'deck.css')
    patterns = _read_css('..', 'kit', 'styles', 'patterns.css')
    kit_css = "\n".join(c for c in (deckcss, patterns) if c is not None)

    if deckcss is not None or patterns is not None:
        # (1) 그라디언트 0 (deck.css + patterns.css)
        kgrad = len(re.findall(r'\b(?:linear|radial|conic)-gradient', kit_css))
        chk(kgrad == 0, "kit CSS 그라디언트 0 (flat-fill)",
            f"kit CSS에 gradient {kgrad}건 — flat-fill 원칙 위배")
        # (2) var(--navy) 미사용 (정의 줄 --navy: 는 매칭 안 됨 → 허용)
        knavy = len(re.findall(r'var\(\s*--navy\s*\)', kit_css))
        chk(knavy == 0, "var(--navy) 미사용", f"var(--navy) {knavy}건 사용 — v2 팔레트 제외 대상")
        # (2b) 새 구조 요소는 보조 블루(ice/electric)가 아니라 --blue를 사용한다.
        css_without_root = re.sub(r':root\s*\{.*?\}', '', kit_css, flags=re.S)
        legacy_blue = len(re.findall(r'var\(\s*--(?:ice|electric)\s*\)', css_without_root))
        chk(legacy_blue == 0, "레거시 보조 블루(ice/electric) 렌더 사용 0",
            f"var(--ice)/var(--electric) {legacy_blue}건 — 구조·주 강조는 --blue만 사용")
        # (2c) 박스 표면 규칙: 흰 카드가 근백색 --line 보더만으로 구분되면 안 된다(2026-07-16).
        kit_box_bad = box_surface_violations(kit_css)
        chk(not kit_box_bad, "kit CSS 박스 표면 규칙 준수(흰 fill+--line 축약보더 0)",
            f"흰 fill+근백색 보더 박스 {kit_box_bad} — 틴트 fill 또는 유색 보더(--blue-line-strong/--mint-line/--coral-line)로 교체")

    if deckcss is not None:
        # (3) :root 토큰 값 정확성(부분문자열 매칭 · 공백정규화 · hex 대소문자 무시)
        rootm = re.search(r':root\s*\{(.*?)\}', deckcss, re.S)
        root_norm = re.sub(r'\s+', '', rootm.group(1)).lower() if rootm else ''
        need_tokens = ['--blue:#1D4ED8', '--mint:#14B8A6', '--coral:#F97360', '--red:#DC2626',
                       '--mint-deep:#0F766E', '--coral-deep:#C2452F',
                       '--on-mint', '--on-coral', '--r-lg:20px', '--font-mono', '--mint-line']
        miss_tokens = [t for t in need_tokens if re.sub(r'\s+', '', t).lower() not in root_norm]
        chk(not miss_tokens, f"토큰 값 정확(deck.css :root, {len(need_tokens)}개 확인)",
            f"토큰 누락/값변경: {miss_tokens}")
        # (3b) 헤더 선과 민트 강조 프리미티브는 공용 CSS 계약을 지킨다.
        def css_block(selector):
            m = re.search(r'(?:^|[}\n;,{])\s*' + selector + r'\s*\{([^}]*)\}', deckcss)
            return re.sub(r'\s+', '', m.group(1)) if m else ''
        sline = css_block(r'\.s-line')
        chk('background:var(--blue)' in sline, "상단 헤더 선은 main blue(--blue)",
            ".s-line이 --blue 배경이 아님")
        mint_mark = css_block(r'\.hl-mint-mark')
        mark_need = ['display:inline-block', 'background:var(--mint)', 'color:var(--white)',
                     'padding:03px1px', 'border-radius:0']
        missing_mark = [x for x in mark_need if x not in mint_mark]
        chk(not missing_mark, "민트 글자폭 강조(.hl-mint-mark) 계약 유지",
            f".hl-mint-mark 계약 누락: {missing_mark}")
        shape_mint = css_block(r'\.shape-mint')
        chk('background:var(--mint)!important' in shape_mint and 'color:var(--on-mint)!important' in shape_mint,
            "민트 도형 강조(.shape-mint) 계약 유지", ".shape-mint의 민트 fill/on-mint 글자 계약 누락")
        # (3c) 넘버 행 정렬 계약: .work-step은 배지 기준 텍스트 수직 중앙(2026-07-16)
        ws = css_block(r'\.work-step')
        chk('align-items:center' in ws, "넘버 행 수직 중앙(.work-step align-items:center) 유지",
            ".work-step이 align-items:center가 아님 — 원형 배지 대비 텍스트 중앙 정렬 규칙 위반")
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
        chk(not bad_badge, "민트 배지 3종 background:var(--mint) 유지",
            f"민트 배지 색 이탈(background:var(--mint) 아님): {bad_badge}")

    # a11y: role="img"(코드 시각화)마다 비어있지 않은 aria-label
    role_img = len(re.findall(r'role="img"', html))
    labeled = len(re.findall(r'role="img"[^>]*aria-label="[^"]+"', html)) + \
              len(re.findall(r'aria-label="[^"]+"[^>]*role="img"', html))
    labeled = min(labeled, role_img)
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
    #   <script>/<style> 제외한 마크업에서 코드포인트 탐지 → 남아 있으면 조립 실수(FAIL).
    body_wo_code = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', html, flags=re.S)
    leaked = [m for m in ('\U0001F4AC', '\U0001F5E3', '\U0001F440') if m in body_wo_code]  # 💬 🗣 👀
    leak_names = {'\U0001F4AC': '💬', '\U0001F5E3': '🗣', '\U0001F440': '👀'}
    chk(not leaked, "원고 아이콘 마커(💬/🗣/👀) 누출 0",
        f"아이콘 마커 {[leak_names[m] for m in leaked]} 최종 HTML에 잔존 — 조립 시 라우팅(주석/.hint-reveal) 후 제거해야 함")

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
