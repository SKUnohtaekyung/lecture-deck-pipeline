"""상태 스크린샷 — 인자: 슬라이드ID 클릭셀렉터 출력이름"""
import sys
sys.path.insert(0, 'tmp/frame/E1')
from common import *
from playwright.sync_api import sync_playwright
sid, sel, name = sys.argv[1:4]
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1280, 'height': 720})
    logs = []
    pg.on('console', lambda m: logs.append((m.type, m.text)) if m.type in ('error', 'warning') else None)
    pg.on('pageerror', lambda e: logs.append(('pageerror', str(e))))
    pg.goto(DECK); pg.wait_for_timeout(1200)
    pg.evaluate("(id)=>window.FRAME.go(id)", sid); pg.wait_for_timeout(1200)
    for s in sel.split('|'):
        pg.click(f'.slide.is-active {s}'); pg.wait_for_timeout(900)
    pg.screenshot(path=f'tmp/frame/E1/shots/{name}.png'); b.close()
print(logs)
