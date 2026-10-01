"""audit_all.js 실행(감사 모드 ?audit) — 전체 증거 JSON을 tmp/frame/E1/audit.json에 저장하고 요약을 찍는다."""
import sys, json
sys.path.insert(0, 'tmp/frame/E1')
from common import *
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    logs = []
    pg.on('console', lambda m: logs.append((m.type, m.text)) if m.type in ('error', 'warning') else None)
    pg.on('pageerror', lambda e: logs.append(('pageerror', str(e))))
    pg.goto(DECK + '?audit'); pg.wait_for_timeout(1500)
    pg.evaluate("document.fonts.ready")
    raw = pg.evaluate("async () => { await document.fonts.ready; await Promise.all([...document.images].map(i => i.complete ? null : new Promise(r => { i.onload = i.onerror = r; }))); return await (await fetch('/scripts/audit_all.js?v='+Date.now())).text().then(eval); }")
    b.close()
open('tmp/frame/E1/audit.json', 'w', encoding='utf-8').write(raw)
r = json.loads(raw)
if 'INVALID' in r:
    print('INVALID', r['INVALID']); sys.exit(2)
print('keys', list(r.keys()))
print('totals', r['render']['totals'])
print('boxes', [[x[0], x[3]] for x in r['perSlide']] if 'perSlide' in r else None)
print('dead', r['render']['density']['deadZones'])
ty = r['typography']
print('fontFloor', ty['fontFloor']['count'], ty['fontFloor'].get('worst', [])[:8])
print('tracking', ty['tracking']['count'], ty['tracking'].get('byClass'))
print('render offenders', r['render'].get('offenders', [])[:10])
print('console', logs)
