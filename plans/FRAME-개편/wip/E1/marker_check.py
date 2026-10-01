"""verify_deck FIXED 마커(s02-slide · s03-slide)를 일반 장에 달아도 화면이 바뀌지 않는가 — 전후 스크린샷 픽셀 비교."""
import sys, urllib.parse, io
sys.path.insert(0, 'tmp/frame/E1')
from common import *
from playwright.sync_api import sync_playwright
from PIL import Image, ImageChops
s = open('tmp/frame/E1/t/강의덱.html', encoding='utf-8').read()
a = '<section class="slide cx-slide f-concept" data-slide="C-06">'; b = '<section class="slide pr f-return" data-slide="R-A">'
assert a in s and b in s
s2 = s.replace(a, a.replace('f-concept', 'f-concept s02-slide')).replace(b, b.replace('f-return', 'f-return s03-slide'))
open('tmp/frame/E1/vt/marker.html', 'w', encoding='utf-8').write(s2)
U2 = BASE + urllib.parse.quote('tmp/frame/E1/vt/marker.html')
def shot(pg, url, sid):
    pg.goto(url + '?audit'); pg.wait_for_timeout(1200); pg.evaluate("(id)=>window.FRAME.go(id)", sid); pg.wait_for_timeout(300)
    return Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
with sync_playwright() as p:
    br = p.chromium.launch(); pg = br.new_page(viewport={'width': 1280, 'height': 720})
    for sid in ('C-06', 'R-A'):
        i1 = shot(pg, DECK, sid); i2 = shot(pg, U2, sid)
        bbox = ImageChops.difference(i1, i2).getbbox()
        print(sid, '픽셀 차이 영역:', bbox)
    br.close()
