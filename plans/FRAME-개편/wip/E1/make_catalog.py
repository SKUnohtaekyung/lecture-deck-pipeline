"""컴포넌트.md 생성 — 산문은 이 파일에, 예시 마크업은 시험 조립에 쓴 섹션(src/sections.json)에서 그대로 가져온다.
사용: python tmp/frame/E1/make_catalog.py  → tmp/frame/E1/컴포넌트.md
"""
import re, json, sys, pathlib
sys.stdout.reconfigure(encoding='utf-8')
R = pathlib.Path(__file__).resolve().parents[3]
E1 = R / 'tmp' / 'frame' / 'E1'
secs = json.loads((E1 / 'src' / 'sections.json').read_text(encoding='utf-8'))

# 결정표에서 레이아웃 → 장 ID 목록
usage = {}
for line in (R / 'plans' / 'FRAME-개편' / '결정표.md').read_text(encoding='utf-8').splitlines():
    c = [x.strip() for x in line.strip().strip('|').split('|')]
    if len(c) >= 13 and re.match(r'^[A-Z][A-Z0-9-]*$', c[0]) and c[7].startswith('F-'):
        usage.setdefault(c[7], []).append(c[0])
U = {k: ' · '.join(v) for k, v in usage.items()}
assert len(usage) == 12, usage.keys()


def ex(sid):
    body = secs[sid].strip()
    return '```html\n' + body + '\n```'


T = open(E1 / 'src' / 'catalog.tpl.md', encoding='utf-8').read()
T = re.sub(r'\{\{EX:([^}]+)\}\}', lambda m: ex(m.group(1)), T)
T = re.sub(r'\{\{USE:([^}]+)\}\}', lambda m: U[m.group(1)], T)
assert '{{' not in T, re.findall(r'\{\{[^}]*\}\}', T)
(E1 / '컴포넌트.md').write_text(T, encoding='utf-8')
print('컴포넌트.md', len(T), 'chars', T.count('\n'), 'lines')
print({k: len(v) for k, v in usage.items()})
