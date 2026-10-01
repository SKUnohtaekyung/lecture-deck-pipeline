"""스크린샷 — ?audit(연출 없음) 상태로 전 장을 찍는다. 인자: 슬라이드 ID(없으면 전부)."""
import sys
sys.path.insert(0, 'tmp/frame/E1')
from common import *
from playwright.sync_api import sync_playwright
ids = sys.argv[1:]
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1280, 'height': 720})
    logs = []
    pg.on('console', lambda m: logs.append((m.type, m.text)) if m.type in ('error', 'warning') else None)
    pg.on('pageerror', lambda e: logs.append(('pageerror', str(e))))
    pg.goto(DECK + '?audit'); pg.wait_for_timeout(1500)
    all_ids = pg.evaluate("[...document.querySelectorAll('.deck .slide')].map(s=>s.dataset.slide)")
    for i, sid in enumerate(all_ids):
        if ids and sid not in ids: continue
        pg.evaluate(f"window.__deckShow({i})"); pg.wait_for_timeout(200)
        pg.screenshot(path=f'tmp/frame/E1/shots/{i+1:02d}_{sid}.png')
    b.close()
print('slides', len(all_ids), 'logs', logs)
