"""shell.html 조립 — tmp/frame/E1/src 의 조각 + 기본 경화 5종(백업 shell) + kit 덱 엔진을 합쳐 shell.html을 쓴다.
사용: python tmp/frame/E1/build_shell.py [--out <경로>]   (기본 출력 = 1주차 강의덱.초안/shell.html)
"""
import re, sys, pathlib
sys.stdout.reconfigure(encoding='utf-8')
R = pathlib.Path(__file__).resolve().parents[3]
SRC = R / 'tmp' / 'frame' / 'E1' / 'src'
BACKUP = R / 'tmp' / 'frame' / 'backup' / '강의덱.초안' / 'shell.html'
STARTER = R / 'kit' / 'starter' / 'deck-template.html'
DEFAULT_OUT = R / 'courses' / 'AI_에이전트_실습워크숍_4시간' / 'sessions' / '1주차' / '강의덱.초안' / 'shell.html'
out = pathlib.Path(sys.argv[sys.argv.index('--out') + 1]) if '--out' in sys.argv else DEFAULT_OUT

# ① 기본 경화 5종 — 백업 shell의 29~162줄을 그대로(지우지 말 것)
old = BACKUP.read_text(encoding='utf-8').split('\n')
hard = '\n'.join(old[28:162])
assert '기본 경화 5종' in hard and hard.rstrip().endswith('.roadmap .s-full:has(.rm-visual) .rm-lead{ max-width:760px; }'), 'hardening slice'
assert '.slide[data-slide="W' not in hard, 'hardening block must not hold week-specific IDs'

# ② kit 스타터에서 덱 엔진과 크롬 마크업을 가져온다
st = STARTER.read_text(encoding='utf-8')
chrome_a = st.index('  <!-- 발표 리모컨 + 상세 메뉴')
chrome_b = st.index('  <script>', chrome_a)
chrome = st[chrome_a:chrome_b].rstrip() + '\n'
eng_a = st.index('  <script>', chrome_a)
eng_b = st.index('  </script>', eng_a) + len('  </script>')
engine = st[eng_a:eng_b]

def patch(s, old_s, new_s, count=1):
    assert s.count(old_s) == count, (old_s[:60], s.count(old_s))
    return s.replace(old_s, new_s)

engine = patch(engine, "var storageKey = 'create-slides';  /* ✏️ 덱마다 고유 문자열로 바꾸면 위치 기억이 분리됨 */",
               "var storageKey = 'frame-week1';  /* 덱마다 고유 문자열 — 위치 기억이 분리된다 */")
engine = patch(engine,
"""      var m = String(location.hash || '').match(/slide=(\\d+)/i);
      if (m) return Math.max(0, parseInt(m[1], 10) - 1);""",
"""      var m = String(location.hash || '').match(/slide=(\\d+)/i);
      if (m) return Math.max(0, parseInt(m[1], 10) - 1);
      /* FRAME: #slide=<슬라이드ID> 도 받는다(ID 기반 이동 · 측정 · 수정 요청 접수) */
      var mi = String(location.hash || '').match(/slide=([A-Za-z][\\w-]*)/);
      if (mi) { for (var q = 0; q < slides.length; q++) { if (slides[q].getAttribute('data-slide') === mi[1]) return q; } }""")
engine = patch(engine,
"""      if (!fixed && curPart >= 1 && totalParts >= 1) {
        var team = s.querySelector('.s-head .s-team');
        if (team) {
          var h = '<span class="lbl">PART ' + curPart + ' / ' + totalParts + '</span><span class="dots">';
          for (var d = 1; d <= totalParts; d++) h += '<span class="pd' + (d === curPart ? ' on' : '') + '"></span>';
          team.className = 's-part';
          team.innerHTML = h + '</span>';
        }
      }""",
"""      /* FRAME: 헤더 오른쪽 라벨(.s-team)은 장마다 마크업에 적는다. kit의 PART n/N 도트(.s-part) 자동 주입은 쓰지 않는다 —
         블록 간지(f-divider)가 part-divider 클래스를 함께 달아 verify가 파트로 세게 하되, 본문 헤더는 건드리지 않게 하려는 것이다. */""")
engine = patch(engine, "    fit(); show(initialIndex()); poke();", "    window.__deckShow = show;   /* FRAME 엔진이 이동에 쓴다 */\n    fit(); show(initialIndex()); poke();")

fav = ("<link rel=\"icon\" href=\"data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 48 48'>"
       "<path d='M8 18 V8 H18 M30 8 H40 V18 M40 30 V40 H30 M18 40 H8 V30' fill='none' stroke='%230E4A5A' stroke-width='5'/>"
       "<rect x='19' y='19' width='10' height='10' fill='%237DE0EC'/></svg>\">")

css = ''.join((SRC / n).read_text(encoding='utf-8') for n in ('10-base.css', '20-components.css', '30-layouts.css', '40-v2.css'))
frame_js = (SRC / 'frame.js').read_text(encoding='utf-8')

head = f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=1280">
  <title>FRAME — AI 에이전트 실습 · 4시간</title>
  <!-- 파비콘은 테마 토큰을 쓸 수 없는 유일한 색 자리다 — FRAME 마크(페트롤 틀 + 아쿠아 사각형) -->
  {fav}
  <!-- 폰트: Pretendard(제목·본문) + D2Coding(요청문·코드). 배포본은 사용 글자 서브셋을 임베드한다 -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/wan2land/d2coding/d2coding-full.css">
  <!-- ⚠️ 경로는 «생성물 강의덱.html의 위치» 기준 4단계다(courses/<과목>/sessions/N주차/). 틀려도 정적 검증은 PASS하고
       브라우저에서만 «전 슬라이드 동시 표시 + 로고 0×0»으로 드러난다 — 조립 후 document.styleSheets.length를 확인한다. -->
  <link rel="stylesheet" href="../../../../kit/styles/deck.css">
  <link rel="stylesheet" href="../../../../kit/styles/legibility.css">
  <link rel="stylesheet" href="../../../../kit/styles/patterns.css">
  <link rel="stylesheet" href="../../../../kit/themes/frame/tokens.css">
  <style id="kit-additions">
    /* 이 덱 전용 CSS는 여기 둔다. 새 구도 클래스는 deck.contract.json의 layout_families에 등재한다
       (미등재 구도는 full로 뭉개져 「동일 구도 연속」 FAIL 오탐이 난다). */

{hard}

{css}
  </style>
</head>
<body>
  <div class="deck">
    <!-- ⚠️ 이 덱에는 고정 슬라이드가 없다. 표지(COVER)·블록 간지·허브까지 전부 part-NN.html에서 온다.
         모든 <section class="slide ...">는 data-slide에 결정표 ID를 갖고, 값은 덱 안에서 유일하다(R-SLIDE-ID-01).
         아래 한 줄이 조립기가 part-NN.html을 끼우는 자리다 — 주석 안에 같은 문구를 쓰지 않는다(조립기가 개수를 센다). -->
<!-- ::PARTS:: -->
  </div>

{chrome}
{engine}
{frame_js}</body>
</html>
"""
assert head.count('<!-- ::PARTS:: -->') == 1
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(head, encoding='utf-8')
print('wrote', out, len(head), 'bytes', head.count('\n'), 'lines')
