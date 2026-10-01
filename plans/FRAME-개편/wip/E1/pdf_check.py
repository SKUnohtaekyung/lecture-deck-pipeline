import sys, re
sys.path.insert(0, 'tmp/frame/E1')
from common import *
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1280, 'height': 720})
    pg.goto(DECK); pg.wait_for_timeout(1500)
    pre = pg.evaluate("""(()=>{const s=document.querySelector('[data-slide=P1-3]');return [s.querySelector('.ck-link path').getAttribute('d').length>10, document.querySelectorAll('[data-slide=M3-2] .ring-svg path').length]})()""")
    data = pg.pdf(width='1280px', height='720px', print_background=True, margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'})
    open('tmp/frame/E1/vt/test.pdf', 'wb').write(data)
    n = len(re.findall(rb'/Type\s*/Page[^s]', data))
    print('PDF pages', n, 'bytes', len(data), '· 방문 전 P1-3 대조선 경로·M3-2 동그라미:', pre)
    b.close()
