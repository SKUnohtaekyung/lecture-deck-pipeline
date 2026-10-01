"""조작 실측 — 1280x720 · 연출 켠 상태(?audit 없음). 항목별 PASS/FAIL 한 줄씩 찍는다."""
import sys, json, time
sys.path.insert(0, 'tmp/frame/E1')
from common import *
from playwright.sync_api import sync_playwright

res = []
def chk(name, ok, detail=''):
    res.append((name, bool(ok), detail)); print(('PASS ' if ok else 'FAIL ') + name + (' — ' + str(detail) if detail != '' else ''))

INIT = """
window.__vt = []; const orig = document.startViewTransition && document.startViewTransition.bind(document);
if (orig) document.startViewTransition = function(cb){ const t0 = performance.now(); const tr = orig(cb);
  tr.finished.then(() => window.__vt.push(Math.round(performance.now() - t0)), () => window.__vt.push(-1)); return tr; };
"""
def active(pg): return pg.evaluate("document.querySelector('.deck .slide.is-active').dataset.slide")
def goto(pg, sid): pg.evaluate("(id)=>window.FRAME.go(id)", sid); pg.wait_for_timeout(60)
def q(pg, js): return pg.evaluate(js)

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={'width': 1280, 'height': 720}, permissions=['clipboard-read', 'clipboard-write'])
    ctx.add_init_script(INIT)
    pg = ctx.new_page(); logs = []
    pg.on('console', lambda m: logs.append((m.type, m.text)) if m.type in ('error', 'warning') else None)
    pg.on('pageerror', lambda e: logs.append(('pageerror', str(e))))
    pg.goto(DECK); pg.wait_for_timeout(1200)

    # 1. 렌더 기본
    vis = q(pg, "[...document.querySelectorAll('.deck .slide')].filter(s=>getComputedStyle(s).display!=='none').length")
    chk('1280x720 보이는 슬라이드 1장', vis == 1, vis)
    n = q(pg, "document.styleSheets.length"); chk('styleSheets 로드(폰트2·kit3·테마1·인라인1 = 7)', n == 7, n)
    loaded = q(pg, "[...document.styleSheets].map(s=>{try{return s.cssRules.length}catch(e){return -1}})")
    chk('모든 styleSheet 규칙 수 > 0(404 없음)', all(x != 0 for x in loaded), loaded)
    sc = q(pg, "getComputedStyle(document.documentElement).getPropertyValue('--scale')"); chk('--scale = 1', sc.strip() == '1', sc)
    tok = q(pg, "getComputedStyle(document.documentElement).getPropertyValue('--blue').trim()"); chk('테마 frame 토큰 적용(--blue #0E4A5A)', tok.lower() == '#0e4a5a', tok)

    # 2. 방향키는 연출을 기다리지 않는다
    goto(pg, 'COVER'); pg.wait_for_timeout(100)
    t0 = time.time(); pg.keyboard.press('ArrowRight'); a1 = active(pg); dt = (time.time() - t0) * 1000
    chk('ArrowRight 즉시 이동(연출 대기 0)', a1 == 'B2-0' and dt < 300, f'{a1} {dt:.0f}ms')
    pg.keyboard.press('ArrowLeft'); chk('ArrowLeft', active(pg) == 'COVER')

    # 3. 허브 4경로 — 카드 클릭 → 실습 ① → 허브로
    paths = {}
    for k, first in (('P1', 'P1-1'), ('P2', 'P2-1'), ('P3', 'P3-1'), ('P4', 'P4-1')):
        goto(pg, 'HUB'); pg.wait_for_timeout(700)
        pg.click(f'.hub-card[data-go="{first}"]'); pg.wait_for_timeout(700)
        ok1 = active(pg) == first
        goto(pg, first if first != 'P1-1' else 'P1-4'); pg.wait_for_timeout(700)
        pg.click('.slide.is-active .back[data-go="HUB"]'); pg.wait_for_timeout(700)
        paths[k] = (ok1, active(pg) == 'HUB')
    chk('허브 4경로: 카드 → 실습 ① → 「허브로」 → 허브', all(a and b_ for a, b_ in paths.values()), paths)
    vt = q(pg, "window.__vt")
    chk('View Transition 실행 8회(카드 4 + 허브로 4) · 길이 0.45초 안팎', len(vt) >= 8 and all(400 <= v <= 700 for v in vt), vt)

    # 4. 슬롯 → 허브 → 복귀(ID 기반)
    q(pg, "sessionStorage.clear()"); goto(pg, 'SLOT-A'); pg.wait_for_timeout(200)
    pg.click('.slot-mini'); pg.wait_for_timeout(700); s1 = active(pg)
    hub_back_vis = q(pg, "!document.querySelector('[data-slide=HUB] [data-return]').hidden")
    pg.click('.hub-card[data-go="P1-1"]'); pg.wait_for_timeout(700)
    goto(pg, 'P1-4'); pg.wait_for_timeout(300); pg.click('.slide.is-active .back'); pg.wait_for_timeout(700)
    done_mark = q(pg, "document.querySelector('[data-slide=HUB] .hub-card[data-pr=P1]').classList.contains('is-done')")
    pg.click('[data-slide=HUB] [data-return]'); pg.wait_for_timeout(700); s2 = active(pg)
    chk('SLOT-A → HUB(슬롯 기억) → 수업으로 돌아가기 → R-A (data-return-to)', s1 == 'HUB' and s2 == 'R-A' and hub_back_vis, (s1, s2, hub_back_vis))
    chk('허브 카드에 진행 표시(is-done)', done_mark)
    goto(pg, 'SLOT-B'); pg.wait_for_timeout(300)
    mark_b = q(pg, "document.querySelector('[data-slide=SLOT-B] .mini-card[data-pr=P1]').classList.contains('is-done')")
    pg.click('[data-slide=SLOT-B] .slot-mini'); pg.wait_for_timeout(700)
    pg.click('[data-slide=HUB] [data-return]'); pg.wait_for_timeout(700); s3 = active(pg)
    chk('SLOT-B → HUB → 돌아가기 → R-B (data-return-to 없이 DOM 다음 장) · 슬롯 B에 A에서 한 실습 표시', s3 == 'R-B' and mark_b, (s3, mark_b))
    q(pg, "sessionStorage.clear()"); goto(pg, 'B2-0'); pg.wait_for_timeout(200); goto(pg, 'HUB'); pg.wait_for_timeout(300)
    hid = q(pg, "document.querySelector('[data-slide=HUB] [data-return]').hidden")
    if not hid:
        pg.click('[data-slide=HUB] [data-return]'); pg.wait_for_timeout(700)
    chk('슬롯을 거치지 않고 허브로 온 경우: 직전 본편 장(B2-0)으로 돌아감', (not hid) and active(pg) == 'B2-0', (hid, active(pg)))

    # 5. 복사 버튼
    goto(pg, 'P1-2'); pg.wait_for_timeout(1000)
    pg.click('.slide.is-active [data-copy]'); pg.wait_for_timeout(200)
    clip = q(pg, "navigator.clipboard.readText()"); lab = pg.inner_text('.slide.is-active [data-copy]')
    chk('복사: `>` 없이 요청문만 · 4줄', clip.startswith('이 폴더의 회의_0312.md') and not clip.startswith('>') and clip.count('\n') == 3 and clip.endswith('저장해 주세요.'), repr(clip[:30]) + ' … ' + repr(clip[-14:]) + f' lines={clip.count(chr(10))+1}')
    chk('복사 버튼 「복사됨」 표시', lab == '복사됨', lab)
    pg.wait_for_timeout(1700); chk('복사됨 1.5초 뒤 「복사」로 복귀', pg.inner_text('.slide.is-active [data-copy]') == '복사')
    goto(pg, 'P1-4'); pg.wait_for_timeout(800); pg.click('.slide.is-active [data-copy]'); pg.wait_for_timeout(200)
    clip2 = q(pg, "navigator.clipboard.readText()")
    chk('복사(고치기 요청문): 자리표시 〈 〉 포함', clip2.startswith('할일표.md의 「〈행의 할 일〉」') and '〈원문의 기한〉' in clip2, repr(clip2[:30]))

    # 6. 타이머
    goto(pg, 'P1-2'); pg.wait_for_timeout(1000)
    t0txt = pg.inner_text('.slide.is-active .timer .tv'); pg.click('.slide.is-active .timer'); pg.wait_for_timeout(2300)
    t1 = pg.inner_text('.slide.is-active .timer .tv'); lbl = pg.inner_text('.slide.is-active .timer .tl')
    pg.click('.slide.is-active .timer'); paused = pg.inner_text('.slide.is-active .timer .tv'); pg.wait_for_timeout(1300)
    t2 = pg.inner_text('.slide.is-active .timer .tv'); lbl2 = pg.inner_text('.slide.is-active .timer .tl')
    chk('타이머 시작 08:00 → 약 2초 경과 · 「멈춤」 표시', t0txt == '08:00' and t1 in ('07:57', '07:58') and '멈춤' in lbl, (t0txt, t1, lbl))
    chk('타이머 멈춤 후 값 유지 · 「이어서」', t2 == paused and '이어서' in lbl2, (paused, t2, lbl2))
    pg.focus('.slide.is-active .timer'); pg.keyboard.press('Enter'); pg.wait_for_timeout(1200); k1 = pg.inner_text('.slide.is-active .timer .tv'); pg.keyboard.press('Space')
    chk('타이머 Enter로 시작 · Space로 멈춤 · 슬라이드 안 넘어감', k1 != paused and active(pg) == 'P1-2', (k1, active(pg)))

    # 7. 단계 클릭 · 체크
    goto(pg, 'P1-2'); pg.wait_for_timeout(1000)
    pg.click('.slide.is-active .flow li:nth-child(1) button')
    st = q(pg, "(()=>{const b=document.querySelector('[data-slide=P1-2] .flow li:nth-child(1) button');return [b.getAttribute('aria-pressed'),b.querySelector('.n').textContent,b.closest('li').classList.contains('done')]})()")
    chk('단계 클릭 완료 표시(aria-pressed · ✓ · .done)', st == ['true', '✓', True], st)
    pg.focus('.slide.is-active .flow li:nth-child(2) button'); pg.keyboard.press('Enter')
    st2 = q(pg, "document.querySelector('[data-slide=P1-2] .flow li:nth-child(2) button').getAttribute('aria-pressed')")
    chk('단계 Enter로 완료 · 슬라이드 안 넘어감', st2 == 'true' and active(pg) == 'P1-2', (st2, active(pg)))
    pg.click('.slide.is-active .flow li:nth-child(1) button')
    chk('단계 다시 누르면 해제(번호 복원)', q(pg, "document.querySelector('[data-slide=P1-2] .flow li:nth-child(1) .n').textContent") == '1')
    goto(pg, 'P1-3'); pg.wait_for_timeout(800); pg.click('.slide.is-active .ck-list li:nth-child(1) button')
    chk('체크 목록 클릭 ☐ → ☑', q(pg, "document.querySelector('[data-slide=P1-3] .ck-list li:nth-child(1) .bx').textContent") == '☑')

    # 8. 펼침 <details>
    goto(pg, 'P1-4'); pg.wait_for_timeout(800)
    o0 = q(pg, "document.querySelector('[data-slide=P1-4] details.reveal').open")
    pg.focus('.slide.is-active details.reveal > summary'); pg.keyboard.press('Enter'); o1 = q(pg, "document.querySelector('[data-slide=P1-4] details.reveal').open")
    pg.keyboard.press('Space'); o2 = q(pg, "document.querySelector('[data-slide=P1-4] details.reveal').open")
    chk('펼침: 처음 닫힘 · Enter로 열림 · Space로 닫힘 · 슬라이드 그대로', (o0, o1, o2) == (False, True, False) and active(pg) == 'P1-4', (o0, o1, o2, active(pg)))
    pg.click('.slide.is-active details.reveal > summary'); pg.wait_for_timeout(100)
    chk('펼침: 클릭으로 열림', q(pg, "document.querySelector('[data-slide=P1-4] details.reveal').open"))

    # 9. 대조선(trace)
    goto(pg, 'P1-3'); pg.wait_for_timeout(1000)
    d0 = q(pg, "document.querySelector('[data-slide=P1-3] .ck-link path').getAttribute('d')")
    pg.click('.slide.is-active tr[data-pick="19"]'); pg.wait_for_timeout(100)
    d1 = q(pg, "document.querySelector('[data-slide=P1-3] .ck-link path').getAttribute('d')")
    on_line = q(pg, "[...document.querySelectorAll('[data-slide=P1-3] [data-line].on')].map(e=>e.dataset.line)")
    chk('대조선: 초기 선 있음 · 행 선택하면 선과 근거 줄이 이동', bool(d0) and bool(d1) and d0 != d1 and on_line == ['19'], (bool(d0), d0 != d1, on_line))
    pg.focus('.slide.is-active tr[data-pick="37"]'); pg.keyboard.press('Enter'); on2 = q(pg, "[...document.querySelectorAll('[data-slide=P1-3] [data-line].on')].map(e=>e.dataset.line)")
    chk('대조선: 키보드(Enter)로 행 선택', on2 == ['37'] and active(pg) == 'P1-3', on2)
    geo = q(pg, """(()=>{const s=document.querySelector('[data-slide=P1-3]');const c=s.querySelectorAll('.ck-link circle');const sr=s.getBoundingClientRect();
      const tb=s.querySelector('table').getBoundingClientRect();return [+c[1].getAttribute('cx'), tb.left-sr.left]})()""")
    chk('대조선 끝점이 표 왼쪽 끝 밖(글자를 가로지르지 않음)', geo[0] < geo[1], geo)

    # 10. 위젯 toggle / pick / step
    goto(pg, 'C-06'); pg.wait_for_timeout(1000)
    a0 = q(pg, "document.querySelector('[data-slide=C-06] .say p span.is-on').textContent")
    pg.click('.slide.is-active [data-toggle]'); pg.wait_for_timeout(100)
    a1_ = q(pg, "[document.querySelector('[data-slide=C-06] [data-w]').dataset.state, document.querySelector('[data-slide=C-06] .say.me p span.is-on').textContent, document.querySelector('[data-slide=C-06] [data-toggle]').textContent, document.querySelector('[data-slide=C-06] [data-toggle]').getAttribute('aria-pressed')]")
    chk('toggle: 초기 「이 문단 어때?」 → 클릭하면 「맞죠?」 질문 · 버튼 글 · aria-pressed', a0 == '이 문단 어때?' and a1_[0] == '1' and '맞죠?' in a1_[1] and '빼기' in a1_[2] and a1_[3] == 'true', a1_)
    pg.focus('.slide.is-active [data-toggle]'); pg.keyboard.press('Space'); chk('toggle: Space로 되돌림 · 슬라이드 그대로', q(pg, "document.querySelector('[data-slide=C-06] [data-w]').dataset.state") == '0' and active(pg) == 'C-06')
    goto(pg, 'C-11'); pg.wait_for_timeout(1000)
    r0 = pg.inner_text('[data-slide=C-11] .wg-read'); docs0 = q(pg, "[...document.querySelectorAll('[data-slide=C-11] rect.v-node.is-on')].length")
    pg.click('.slide.is-active [data-pick="0"]'); pg.wait_for_timeout(100)
    r1 = pg.inner_text('[data-slide=C-11] .wg-read'); on0 = q(pg, "document.querySelector('[data-slide=C-11] [data-pick=\"0\"]').classList.contains('on')")
    pg.focus('.slide.is-active [data-pick="2"]'); pg.keyboard.press('Enter'); r2 = pg.inner_text('[data-slide=C-11] .wg-read')
    chk('pick: 초기(열 번째 53.8) → 첫 번째 75.8 → 키보드 Enter로 스무 번째 63.2 · 슬라이드 그대로', '53.8' in r0 and docs0 == 1 and '75.8' in r1 and on0 and '63.2' in r2 and active(pg) == 'C-11', (r0[:20], docs0, r1[:24], r2[:24]))
    goto(pg, 'C-12'); pg.wait_for_timeout(1000)
    st_js = "[document.querySelector('[data-slide=C-12] [data-w]').dataset.state, document.querySelectorAll('[data-slide=C-12] [data-from].is-on').length, document.querySelectorAll('[data-slide=C-12] .w-dim.is-on').length, document.querySelector('[data-slide=C-12] [data-next]').disabled]"
    s0 = q(pg, st_js)
    for _ in range(3): pg.click('.slide.is-active [data-next]')
    s6 = q(pg, st_js); pg.click('.slide.is-active [data-reset]'); s_r = q(pg, st_js)
    chk('step: 서류 3장 → 더하기 ×3(최대 6에서 멈춤 · 가운데 흐려짐) → 처음으로', s0 == ['3', 3, 0, False] and s6[0] == '6' and s6[1] == 6 and s6[2] == 4 and s6[3] is True and s_r[0] == '3', (s0, s6, s_r))

    goto(pg, 'C-08'); pg.wait_for_timeout(1000)
    def dimstate(): return q(pg, "[document.querySelector('[data-slide=C-08] [data-w]').dataset.state, ...[...document.querySelectorAll('[data-slide=C-08] .w-dim')].map(e=>e.classList.contains('is-on')), document.querySelector('[data-slide=C-08] [data-toggle]').textContent, document.querySelectorAll('[data-slide=C-08] .ring-svg').length]")
    d0s = dimstate(); pg.click('.slide.is-active [data-toggle]'); pg.wait_for_timeout(100); d1s = dimstate()
    chk('전후 토글(C-08): 처음엔 후 강조(전 흐림) · 클릭하면 전 강조(후 흐림) · 버튼 글 · 동그라미 유지', d0s == ['1', True, False, '전 보기', 1] and d1s == ['0', False, True, '후 보기', 1], (d0s, d1s))
    # 10b. 발표 메뉴 · 방향키 · 단축키(kit 엔진 그대로 동작하는가)
    goto(pg, 'COVER'); pg.wait_for_timeout(100)
    pg.keyboard.press('g'); pg.wait_for_timeout(200)
    m_open = q(pg, "!document.getElementById('presentationMenu').hidden"); m_n = q(pg, "document.querySelectorAll('#slideList button').length")
    pg.click('#slideList button:nth-child(14)'); pg.wait_for_timeout(200); m_jump = active(pg)
    pg.keyboard.press('g'); pg.wait_for_timeout(100); pg.fill('#pageInput', '5'); pg.keyboard.press('Enter'); pg.wait_for_timeout(200); m_page = active(pg)
    chk('발표 메뉴: G로 열림 · 목록 22장 · 목록 클릭 이동 · 쪽 번호 입력 이동', m_open and m_n == 22 and m_jump == 'HUB' and m_page == 'C-11', (m_open, m_n, m_jump, m_page))
    pg.keyboard.press('b'); bo = q(pg, "!document.getElementById('blackout').hidden"); pg.keyboard.press('Escape'); bo2 = q(pg, "!document.getElementById('blackout').hidden")
    cnt = q(pg, "document.getElementById('counter').textContent")
    chk('B 화면 가리기 · Esc 해제 · 카운터 「5 / 22」', bo and not bo2 and cnt == '5 / 22', (bo, bo2, cnt))
    pg.keyboard.press('End'); e1 = active(pg); pg.keyboard.press('Home'); e2 = active(pg)
    chk('End · Home 이동', e1 == 'T-APP' and e2 == 'COVER', (e1, e2))
    hashid = pg.evaluate("(()=>{location.hash='#slide=P1-3'; return new Promise(r=>setTimeout(()=>r(location.hash),50))})()")
    pg.goto('about:blank'); pg.goto(DECK + '#slide=P1-3'); pg.wait_for_timeout(800)
    chk('주소 #slide=<ID> 로 열기(ID 기반 · 새로고침해도 그 장)', active(pg) == 'P1-3', active(pg))

    # 11. 동그라미
    goto(pg, 'M3-2'); pg.wait_for_timeout(800)
    rings = q(pg, "[...document.querySelectorAll('[data-slide=M3-2] .ring-svg path')].map(p=>!!p.getAttribute('d'))")
    chk('동그라미 3개(.ring-host) 생성', rings == [True, True, True], rings)

    # 12. 연출 시간 · 무한 반복 없음
    anim = []; inf = 0
    for i in range(22):
        pg.evaluate(f"window.__deckShow({i})"); pg.wait_for_timeout(30)
        r = pg.evaluate("""(i)=>{const S=[...document.querySelectorAll('.deck .slide')][i];
          const an=document.getAnimations().filter(a=>a.effect&&a.effect.target&&S.contains(a.effect.target));
          let end=0,inf=0,max1=0; for(const a of an){const t=a.effect.getComputedTiming(); const e=(t.delay||0)+(t.activeDuration===Infinity?1e9:t.activeDuration); end=Math.max(end,e); max1=Math.max(max1,t.duration||0); if(t.iterations===Infinity) inf++;}
          return [S.dataset.slide, Math.round(end), inf, Math.round(max1), an.length]}""", i)
        anim.append(r); inf += r[2]
    worst = max(a[1] for a in anim); one = max(a[3] for a in anim)
    chk('등장 연출 한 장 ≤ 0.9초 (전 22장)', worst <= 900, f'최대 {worst}ms · ' + ' '.join(f'{a[0]}:{a[1]}' for a in anim))
    chk('한 동작 ≤ 0.6초', one <= 600, f'최대 {one}ms')
    chk('무한 반복 연출 0', inf == 0, inf)
    chk('콘솔 오류·경고 0(연출 켠 조작 전체)', not logs, logs)
    ctx.close()

    # 13. reduced-motion · ?audit · 인쇄 — 즉시 최종 상태
    def final_state_check(ctx_kwargs, url, label, media=None):
        c2 = b.new_context(viewport={'width': 1280, 'height': 720}, **ctx_kwargs); pg2 = c2.new_page(); pg2.goto(url); pg2.wait_for_timeout(1000)
        if media: pg2.emulate_media(media=media)
        bad = []
        for i in range(22):
            pg2.evaluate(f"window.__deckShow({i})"); pg2.wait_for_timeout(40)
            r = pg2.evaluate("""(i)=>{const S=[...document.querySelectorAll('.deck .slide')][i];
              const an=document.getAnimations().filter(a=>a.effect&&a.effect.target&&S.contains(a.effect.target)&&a.playState!=='finished').length;
              const rv=[...S.querySelectorAll('.rv')].filter(e=>getComputedStyle(e).opacity!=='1'||getComputedStyle(e).transform!=='none').length;
              const mk=[...S.querySelectorAll('.mk,.mk-solid')].filter(e=>getComputedStyle(e,'::after').transform!=='none').length;
              return [S.dataset.slide, an, rv, mk]}""", i)
            if r[1] or r[2] or r[3]: bad.append(r)
        c2.close(); chk(label, not bad, bad[:4])
    final_state_check({'reduced_motion': 'reduce'}, DECK, 'prefers-reduced-motion: 전 장 진행 중 애니메이션 0 · .rv/.mk 최종 상태')
    final_state_check({}, DECK + '?audit', '?audit(감사 모드): 전 장 진행 중 애니메이션 0 · 최종 상태')
    final_state_check({}, DECK, '인쇄 미디어: 진행 중 애니메이션 0 · 최종 상태', media='print')
    c3 = b.new_context(viewport={'width': 1280, 'height': 720}, reduced_motion='reduce'); c3.add_init_script(INIT); p3 = c3.new_page(); p3.goto(DECK); p3.wait_for_timeout(1000)
    p3.evaluate("window.FRAME.go('HUB')"); p3.wait_for_timeout(100); p3.click('.hub-card[data-go="P1-1"]'); p3.wait_for_timeout(50)
    chk('reduced-motion: 카드 클릭 즉시 이동 · View Transition 0회', p3.evaluate("document.querySelector('.deck .slide.is-active').dataset.slide") == 'P1-1' and p3.evaluate("window.__vt.length") == 0)
    c3.close()
    b.close()
print('RESULT', sum(1 for r in res if r[1]), '/', len(res), 'PASS')
open('tmp/frame/E1/interact.json', 'w', encoding='utf-8').write(json.dumps(res, ensure_ascii=False))
