import sys, json
sys.path.insert(0, 'tmp/frame/E1')
from common import *
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1280, 'height': 720})
    pg.goto(DECK + '?audit'); pg.wait_for_timeout(1500)
    js = """(id)=>{ window.FRAME.go(id); const S=document.querySelector('[data-slide='+id+']'); const sr=S.getBoundingClientRect();
      const r=(sel)=>{const e=S.querySelector(sel); if(!e) return null; const b=e.getBoundingClientRect(); return [Math.round(b.left-sr.left),Math.round(b.top-sr.top),Math.round(b.width),Math.round(b.height)]};
      return {main:r('.pr-main'), cols:r('.pr-cols'), left:r('.pr-left'), right:r('.pr-right'), term:r('.term'), title:r('.s-title'), cxmain:r('.cx-main'), cxtext:r('.cx-text'), fig:r('.cx-fig'), ck:r('.ck-top'), cklist:r('.ck-list'), flow:r('.flow'), hubgrid:r('.hub-grid'), slotmain:r('.slot-main')} }"""
    for sid in ('P1-1', 'P1-2', 'P1-3', 'P1-4', 'R-A', 'M3-2', 'M3-4', 'C-11', 'C-06', 'HUB', 'SLOT-A'):
        d = pg.evaluate(js, sid); pg.wait_for_timeout(80)
        print(sid, {k: v for k, v in d.items() if v})
    # 제목 한 줄 글자 수 한도
    pg.evaluate("window.FRAME.go('P1-2')"); pg.wait_for_timeout(100)
    res = pg.evaluate("""()=>{const h=document.querySelector('[data-slide=P1-2] .s-title'); const out={}; const base='가나다라마바사아자차카타파하'; let s='';
      for(let n=20;n<=40;n++){ h.textContent = (base.repeat(4)).slice(0,n); out[n]=h.getBoundingClientRect().height>60?2:1;} return out}""")
    print('제목 한 줄 한도', [n for n, l in res.items() if l == 1][-1])
    # 본문 한 줄 글자 수(22px, .keep 폭 1152)와 터미널(20px 모노) 한 줄 글자 수
    res2 = pg.evaluate("""()=>{const t=document.querySelector('[data-slide=P1-2] .terminal-copy p'); const c=document.createElement('span'); c.style.cssText='font:inherit;position:absolute;visibility:hidden;white-space:nowrap'; t.appendChild(c); c.textContent='가'.repeat(10); const w=c.getBoundingClientRect().width/10; const cs=getComputedStyle(t); const inner=t.getBoundingClientRect().width; c.remove(); return {hangulPx:w, inner:inner, perLine:Math.floor(inner/w), fs:cs.fontSize, lh:cs.lineHeight}}""")
    print('터미널', res2)
    b.close()
