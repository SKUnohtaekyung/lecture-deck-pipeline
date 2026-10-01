"""FRAME 개편 진행물 보기 페이지 — 결정표를 표로 그리고 예시 덱·설계서로 잇는다(tmp 전용)."""
import re, html, pathlib
R = pathlib.Path(__file__).resolve().parents[3]; D = R / 'plans/FRAME-개편'
s = (D / '결정표.md').read_text(encoding='utf-8')
rows = [[c.strip() for c in l.split('|')[1:-1]] for l in s.split('\n') if l.startswith('| ') and not l.startswith('|---')]
head, body = rows[0], rows[1:]
KIND = {'개념':'k-c','실습':'k-p','메인':'k-m','허브':'k-h','체험':'k-x','운영':'k-o','전환':'k-t','표지':'k-t','마무리':'k-t'}
def inline(t): return re.sub(r'`([^`]+)`', r'<code>\1</code>', html.escape(t))
tr = []
prev = None
for r in body:
    blk = r[2]
    if blk != prev:
        mins = sum(float(x[3]) for x in body if x[2] == blk)
        label = f'블록 {blk}' if blk != '허브' else '허브 구간(PART 5) — 슬롯 A·B 15분 안에서'
        tr.append(f'<tr class="blk"><td colspan="9">{label} · {len([x for x in body if x[2]==blk])}장 · {mins:g}분</td></tr>'); prev = blk
    tr.append('<tr><td class="id">{}</td><td class="num">{}</td><td><span class="kind {}">{}</span></td><td class="ttl">{}</td><td>{}</td><td class="mono">{}</td><td>{}</td><td>{}</td><td class="mono">{}</td></tr>'.format(
        r[0], r[3], KIND.get(r[4], ''), r[4], inline(r[5]), r[6], r[7], inline(r[8]), inline(r[9]), inline(r[11])))
docs = [('G1b 제출 — 검토할 것 · 결정 요청 4개', 'G1b_제출.html'), ('리허설 체크리스트 — GR용', '리허설_체크리스트.html'), ('문구 초안 — 82장 전체(병합본 · 작업 중)', '초안.html'), ('예시 v2 — 개념 · 허브 · 실습 1(6장)', '../../../plans/FRAME-개편/prototype/예시v2.html'),
        ('계획서 PLAN', 'PLAN.html'), ('처분표', '처분표.html'),
        ('습관점검 설계', '습관점검_설계.html'), ('준비물 사양', '준비물_사양.html'),
        ('문체 기준', '문체기준.html'), ('개념노트', '개념노트.html'),
        ('출처', '출처.html')]
page = f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>FRAME 개편 진행물</title>
<link rel="stylesheet" href="../../../kit/themes/frame/tokens.css">
<style>
body{{margin:0;background:var(--white);color:var(--ink);font-family:Pretendard,"Malgun Gothic",sans-serif;letter-spacing:-.01em}}
.wrap{{max-width:1320px;margin:0 auto;padding:32px 24px 64px}}
h1{{margin:0 0 4px;font-size:30px}} .sub{{color:var(--gray-700);margin:0 0 20px}}
.docs{{display:flex;flex-wrap:wrap;gap:10px;margin:0 0 28px;padding:0;list-style:none}}
.docs a{{display:inline-block;padding:10px 16px;border-radius:10px;background:var(--blue-soft);color:var(--blue);font-weight:700;text-decoration:none}}
.docs li:first-child a{{background:var(--blue);color:#fff}}
table{{width:100%;border-collapse:collapse;font-size:14px}}
th{{position:sticky;top:0;background:var(--surface);text-align:left;padding:8px;border-bottom:2px solid var(--gray-400);font-size:13px}}
td{{padding:7px 8px;border-bottom:1px solid var(--line);vertical-align:top}}
tr.blk td{{background:var(--ink);color:#fff;font-weight:800;font-size:15px;padding:10px}}
.id{{font-family:var(--font-mono);font-weight:700;white-space:nowrap}} .num{{text-align:right;font-family:var(--font-mono)}} .ttl{{font-weight:600;min-width:240px}}
.mono{{font-family:var(--font-mono);font-size:12px;color:var(--gray-700)}} code{{font-family:var(--font-mono);font-size:.92em}}
.kind{{display:inline-block;padding:2px 8px;border-radius:6px;font-size:12px;font-weight:800;white-space:nowrap;background:var(--surface)}}
.k-c{{background:var(--mint);color:var(--on-mint)}} .k-p{{background:#FF8A5C;color:var(--ink)}} .k-m{{background:#FFEDE5;color:#B8431F}}
.k-h{{background:var(--blue);color:#fff}} .k-x{{background:var(--coral-soft);color:var(--coral-deep)}}
</style></head><body><div class="wrap">
<h1>FRAME 개편 — 지금까지 만든 것</h1>
<p class="sub">결정표 {len(body)}장 · 블록마다 50분(휴식 제외 200분) · 2026-10-01 기준. 예시 덱은 방향키로 넘기고, 허브 카드 1번 · 막대 · 표 행 · 복사 버튼을 눌러 볼 수 있습니다.</p>
<ul class="docs">{''.join(f'<li><a href="{h}" target="_blank">{html.escape(t)}</a></li>' for t,h in docs)}</ul>
<table><thead><tr><th>ID</th><th>분</th><th>종류</th><th>제목(가)</th><th>정보 모양</th><th>레이아웃</th><th>시각 자료</th><th>애니메이션</th><th>강조</th></tr></thead>
<tbody>{''.join(tr)}</tbody></table></div></body></html>'''
(pathlib.Path(__file__).parent / 'index.html').write_text(page, encoding='utf-8'); print('rows', len(body))
