"""메인 점검용 — ID 목록을 덱에서 한 장씩 새로 열어 ?audit 최종 상태로 캡처한다."""
import sys
from playwright.sync_api import sync_playwright
ids = sys.argv[1:]
U = 'http://localhost:8810/tmp/frame/view/live_deck.html'
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1280, 'height': 720})
    pg.goto(U + '?audit'); pg.wait_for_timeout(1000)
    order = pg.evaluate("[...document.querySelectorAll('section.slide')].map(s=>s.dataset.slide)")
    for i in ids:
        q = b.new_page(viewport={'width': 1280, 'height': 720})
        q.goto(f'{U}?audit#slide={order.index(i)+1}'); q.wait_for_timeout(900)
        q.screenshot(path=f'tmp/frame/E/shots/_main_{i}.png'); q.close()
    b.close()
print('shot', len(ids))
