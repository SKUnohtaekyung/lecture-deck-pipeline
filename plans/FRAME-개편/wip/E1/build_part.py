"""시험 part 생성 — src/part-test.tpl.html 의 섹션을 ID로 갈라 part-01(수업 구간) · part-02(허브 구간)로 배치한다.
@@H(팀 라벨)@@ 를 표준 헤더 마크업으로 풀고, SLOT-B · R-B · P2-1 · P3-1 · P4-1(허브 4경로 시험용)을 덧붙인다.
사용: python tmp/frame/E1/build_part.py   → tmp/frame/E1/t/강의덱.초안/part-01.html · part-02.html
"""
import re, sys, pathlib
sys.stdout.reconfigure(encoding='utf-8')
E1 = pathlib.Path(__file__).resolve().parent
SRC = E1 / 'src' / 'part-test.tpl.html'
OUT = E1 / 't' / '강의덱.초안'

HEADER = ('<header class="s-head">\n'
          '    <svg class="s-logo" viewBox="0 0 48 48" aria-hidden="true"><path d="M8 18 V8 H18 M30 8 H40 V18 M40 30 V40 H30 M18 40 H8 V30" fill="none" style="stroke:var(--blue)" stroke-width="5"/><rect x="19" y="19" width="10" height="10" style="fill:var(--mint)"/></svg><span class="s-brand">FRAME</span>\n'
          '    <span class="s-line"></span><div class="s-team">{team}</div>\n'
          '  </header>')

text = SRC.read_text(encoding='utf-8')
text = re.sub(r'@@H\((.*?)\)@@', lambda m: HEADER.format(team=m.group(1)), text)

# 섹션(앞 주석 포함) 분리
pat = re.compile(r'(<!-- =+ .*? =+ -->\s*<section class="slide[^>]*data-slide="([^"]+)".*?</section>)', re.S)
secs = {m.group(2): m.group(1) for m in pat.finditer(text)}
order_src = [m.group(2) for m in pat.finditer(text)]
print('template sections:', order_src)

def clone(src_id, new_id, subs):
    s = secs[src_id].replace('data-slide="%s"' % src_id, 'data-slide="%s"' % new_id)
    s = re.sub(r'<!-- =+ %s ' % re.escape(src_id), '<!-- ============ %s ' % new_id, s, count=1)
    for a, b in subs:
        assert a in s, (new_id, a)
        s = s.replace(a, b)
    return s

secs['SLOT-B'] = clone('SLOT-A', 'SLOT-B', [
    (' data-return-to="R-A"', ''),                      # 시험: SLOT-B는 data-return-to가 없다 → 엔진이 DOM의 다음 장(R-B)으로 보낸다
    ('에이전트 실습 시간 A', '에이전트 실습 시간 B'),
    ('01 회의 메모</span> 또는 <span class="em-tag">04 주간 보고서', '02 폴더 정리</span> 또는 <span class="em-tag">03 문의 답장'),
    ('블록 2<br>에이전트 실습', '블록 3<br>에이전트 실습'),
])
secs['R-B'] = clone('R-A', 'R-B', [])

def tiny(pid, n, name, goal):
    return f'''<!-- ============ {pid} · 허브 4경로 시험용 — 실습 {n} ① 목표(최소 마크업) ============ -->
<section class="slide pr f-goal" data-slide="{pid}">
  {HEADER.format(team='에이전트 실습')}
  <div class="pr-wrap">
    <div class="pr-bar"><span class="pr-no">실습 {n}</span><span class="pr-name">{name}</span><span class="pr-steps" aria-label="4단계 중 1단계"><span class="cur" aria-current="step">① 목표</span><span>② 진행</span><span>③ 확인</span><span>④ 고치기</span></span></div>
    <div class="pr-top rv" style="--i:0" data-vt-key="p{n}">
      <h2 class="s-title">{goal}</h2>
    </div>
    <div class="pr-main">
      <button class="back" type="button" data-go="HUB" data-vt-key="p{n}" style="align-self:flex-start">허브로</button>
    </div>
  </div>
</section>
'''
secs['T-APP'] = f'''<!-- ============ T-APP · 앱 창 모형(.win.app) 시험 — 에이전트 앱 화면 ============ -->
<section class="slide pr f-screen" data-slide="T-APP">
  {HEADER.format(team='메인 과제')}
  <div class="pr-wrap">
    <div class="pr-bar"><span class="pr-no">메인 과제</span><span class="pr-name">AI 활용 습관 점검</span><span class="pr-steps" aria-label="4단계 중 1단계"><span class="cur" aria-current="step">① 기획</span><span>② 제작</span><span>③ 공개</span><span>④ 개선</span></span></div>
    <div class="pr-top rv" style="--i:0">
      <h2 class="s-title">에이전트 앱에서 <span class="mk">폴더</span>를 엽니다</h2>
    </div>
    <div class="pr-main">
      <div class="pr-cols" style="--lc:430px">
        <div class="pr-left">
          <ol class="flow" data-w="todo">
            <li class="rv" style="--i:1"><button type="button" aria-pressed="false"><span class="n">1</span><span class="t">에이전트 앱을 엽니다</span></button></li>
            <li class="rv" style="--i:2"><button type="button" aria-pressed="false"><span class="n">2</span><span class="t">폴더 열기 메뉴로 <code>00_AI습관점검</code> 폴더를 엽니다</span></button></li>
            <li class="rv" style="--i:3"><button type="button" aria-pressed="false"><span class="n">3</span><span class="t">왼쪽에 폴더 이름이 보이면 열린 것입니다</span></button></li>
          </ol>
        </div>
        <div class="win app rv" style="--i:2;align-self:start">
          <div class="win-bar"><i></i><i></i><i></i><b>에이전트 앱 · 화면 모형</b></div>
          <div class="win-body">
            <div class="win-side"><p>작업 폴더</p><p class="path">00_AI습관점검</p><p>대화</p><p class="path">새 대화</p></div>
            <div class="win-main">
              <div class="say me"><span class="who">나</span><p>요청문을 붙여 넣고 보냅니다</p></div>
              <div class="say"><span class="who">에이전트</span><p>계획과 승인 요청이 여기에 나옵니다</p></div>
              <p class="win-url">메시지 입력</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>
'''
secs['P2-1'] = tiny('P2-1', 2, '폴더 정리', '흩어진 파일 40개를 규칙대로 폴더에 나눕니다')
secs['P3-1'] = tiny('P3-1', 3, '문의 답장', '문의 12건에 FAQ를 근거로 답장 초안을 씁니다')
secs['P4-1'] = tiny('P4-1', 4, '주간 보고서', '월~금 메모와 매출 표로 주간 보고서를 만듭니다')

part1 = ['COVER', 'B2-0', 'C-06', 'C-08', 'C-11', 'C-12', 'SLOT-A', 'R-A', 'M3-2', 'M3-4', 'BR-1', 'SLOT-B', 'R-B']
part2 = ['HUB', 'P1-1', 'P1-2', 'P1-3', 'P1-4', 'P2-1', 'P3-1', 'P4-1', 'T-APP']
OUT.mkdir(parents=True, exist_ok=True)
for name, ids in (('part-01.html', part1), ('part-02.html', part2)):
    body = '\n\n'.join(secs[i] for i in ids) + '\n'
    (OUT / name).write_text(body, encoding='utf-8')
    print(name, len(ids), 'slides', len(body), 'bytes')
# 카탈로그 생성기가 읽는 전체 섹션 사전
import json
(E1 / 'src' / 'sections.json').write_text(json.dumps(secs, ensure_ascii=False), encoding='utf-8')
