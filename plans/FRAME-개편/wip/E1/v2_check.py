import sys, json, urllib.parse
sys.path.insert(0, 'tmp/frame/E1')
from common import *
from playwright.sync_api import sync_playwright
from PIL import Image
U = lambda rel: BASE + urllib.parse.quote(rel)
T1, T2 = U('tmp/frame/E1/t/강의덱.html'), U('tmp/frame/E1/t2/강의덱.html')
LIVE = 'http://localhost:8810/tmp/frame/view/live_deck.html'


def audit(pg, url):
    pg.goto(url + '?audit'); pg.wait_for_timeout(1500)
    raw = pg.evaluate("async () => { await document.fonts.ready; return await (await fetch('/scripts/audit_all.js?v='+Date.now())).text().then(eval); }")
    r = json.loads(raw)
    if 'INVALID' in r:
        return {'INVALID': r['INVALID']}
    return {'totals': {k: v for k, v in r['render']['totals'].items() if v}, 'boxes': {x[0]: x[3] for x in r['perSlide'] if x[3]},
            'fontFloor': r['typography']['fontFloor']['count'], 'fontWorst': r['typography']['fontFloor']['worst'][:3],
            'tracking': r['typography']['tracking']['count'], 'trackBy': r['typography']['tracking'].get('byClass'),
            'dead': [d['id'] for d in r['render']['density']['deadZones']]}


with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900}); logs = []
    pg.on('console', lambda m: logs.append((m.type, m.text[:160])) if m.type in ('error', 'warning') else None)
    pg.on('pageerror', lambda e: logs.append(('pageerror', str(e)[:160])))
    print('AUDIT v2 덱', json.dumps(audit(pg, T2), ensure_ascii=False))
    print('AUDIT v1 덱', json.dumps(audit(pg, T1), ensure_ascii=False))
    print('console(audit)', logs); logs.clear()
    # 스크린샷 1280x720 — ?audit 없이 최종 상태 그대로
    pg2 = b.new_page(viewport={'width': 1280, 'height': 720})
    pg2.on('console', lambda m: logs.append((m.type, m.text[:160])) if m.type in ('error', 'warning') else None)
    pg2.on('pageerror', lambda e: logs.append(('pageerror', str(e)[:160])))
    shots = []
    for url, ids in ((T2, None), (T1, ['HUB', 'P1-2'])):
        pg2.goto(url + '?audit'); pg2.wait_for_timeout(1200)
        allids = pg2.evaluate("[...document.querySelectorAll('.deck .slide')].map(s=>s.dataset.slide)")
        for i, sid in enumerate(allids):
            if ids and sid not in ids: continue
            pg2.evaluate(f"window.__deckShow({i})"); pg2.wait_for_timeout(150)
            f = f'tmp/frame/E1/shots/v2_{sid}.png'; pg2.screenshot(path=f); shots.append(f)
    pg2.goto(LIVE); pg2.wait_for_timeout(2500)
    n = pg2.evaluate("document.querySelectorAll('.deck .slide').length")
    print('live deck', LIVE, 'slides', n, 'console', logs)
    b.close()
W, H = 640, 360
im = Image.new('RGB', (W * 3, H * ((len(shots) + 2) // 3)), (200, 200, 200))
for i, f in enumerate(shots):
    im.paste(Image.open(f).convert('RGB').resize((W, H)), ((i % 3) * W, (i // 3) * H))
im.save('tmp/frame/E1/shots/_v2sheet.png'); print(len(shots), 'shots')
