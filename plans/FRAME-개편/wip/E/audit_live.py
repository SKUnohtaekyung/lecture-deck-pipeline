"""메인 점검용 — live 덱 전체 감사 요약(결함 있는 장만). 인자로 ID를 주면 그 장만 걸러 보여 준다."""
import sys, json
from playwright.sync_api import sync_playwright
LIVE = 'http://localhost:8810/tmp/frame/view/live_deck.html'
ids = set(sys.argv[1:])
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.goto(LIVE + '?audit'); pg.wait_for_timeout(1500)
    raw = pg.evaluate("async () => { await document.fonts.ready; return await (await fetch('/scripts/audit_all.js?v='+Date.now())).text().then(eval); }")
    b.close()
r = json.loads(raw)
json.dump(r, open('tmp/frame/E/audit_live.json', 'w', encoding='utf-8'), ensure_ascii=False)
if 'INVALID' in r: print('INVALID', r['INVALID']); sys.exit(1)
rd = r['render']
print('keys', list(r.keys()), '| render', list(rd.keys()))
print('totals', {k: v for k, v in rd['totals'].items() if v})
ty = r['typography']
print('fontFloor', ty['fontFloor']['count'], '| tracking', ty['tracking']['count'], '| slides', len(r['perSlide']))
print('dead', [d['id'] for d in rd['density']['deadZones'] if not ids or d['id'] in ids])
