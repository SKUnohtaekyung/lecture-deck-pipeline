"""배포본(단일 파일)에서 허브 이동 · 복귀 · 복사 · 위젯이 동작하는가."""
import sys, urllib.parse
sys.path.insert(0, 'tmp/frame/E1')
from common import *
from playwright.sync_api import sync_playwright
URL = BASE + urllib.parse.quote('tmp/frame/E1/vt/test_nod2_배포.html')
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 1280, 'height': 720}, permissions=['clipboard-read', 'clipboard-write']); pg = ctx.new_page(); logs = []
    pg.on('console', lambda m: logs.append((m.type, m.text)) if m.type in ('error', 'warning') else None); pg.on('pageerror', lambda e: logs.append(str(e)))
    pg.goto(URL); pg.wait_for_timeout(1200)
    act = lambda: pg.evaluate("document.querySelector('.deck .slide.is-active').dataset.slide")
    out = {}
    out['styleSheets'] = pg.evaluate("document.styleSheets.length"); out['links'] = pg.evaluate("document.querySelectorAll('link[rel=stylesheet]').length")
    pg.evaluate("window.FRAME.go('SLOT-A')"); pg.wait_for_timeout(200); pg.click('.slot-mini'); pg.wait_for_timeout(700); out['slot->hub'] = act()
    pg.click('.hub-card[data-go="P1-1"]'); pg.wait_for_timeout(700); out['hub->P1-1'] = act()
    pg.evaluate("window.FRAME.go('P1-4')"); pg.wait_for_timeout(300); pg.click('.slide.is-active .back'); pg.wait_for_timeout(700)
    pg.click('[data-slide=HUB] [data-return]'); pg.wait_for_timeout(700); out['return'] = act()
    pg.evaluate("window.FRAME.go('P1-2')"); pg.wait_for_timeout(800); pg.click('.slide.is-active [data-copy]'); pg.wait_for_timeout(200)
    out['copy'] = pg.evaluate("navigator.clipboard.readText()")[:20]
    pg.evaluate("window.FRAME.go('C-11')"); pg.wait_for_timeout(600); pg.click('.slide.is-active [data-pick="0"]'); out['pick'] = pg.inner_text('[data-slide=C-11] .wg-read')[:16]
    out['fontface_embedded'] = pg.evaluate("document.fonts.check('16px Pretendard')")
    out['logs'] = logs
    print(out); b.close()
