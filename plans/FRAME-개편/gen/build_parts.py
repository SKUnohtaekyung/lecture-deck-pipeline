"""E4 묶기 — 장별 섹션 파일(`tmp/frame/E/slides/<ID>.html`)을 결정표 순서 · PART별로 모아 `강의덱.초안/part-0N.html`을 쓴다.
검사(하나라도 걸리면 쓰지 않고 exit 1): 누락 · 결정표 밖 파일 · 파일마다 <section> 정확히 1개 · data-slide = 파일 ID
· 발표자 기호(💬 👀 🗣) · 초안 표기 잔존([터미널: · [펼침] · [파일: · <br> 문자열 그대로) · 제목 보존(초안 제목이 섹션 안에 그대로 있는가) · 🗣 힌트 수 ≤ 접힌 칸 수."""
import re, sys, html, pathlib
sys.stdout.reconfigure(encoding='utf-8')
R = pathlib.Path(__file__).resolve().parents[3]
SL = R / 'tmp/frame/E/slides'
S1 = R / 'courses/AI_에이전트_실습워크숍_4시간/sessions/1주차'
OUT = S1 / '강의덱.초안'
PLAN = R / 'plans/FRAME-개편/결정표.md'
DRAFT = S1 / '1주차_초안.md'


def rows(path, ncol=None):
    out = []
    for l in path.read_text(encoding='utf-8').split('\n'):
        if re.match(r'^\| [A-Z][A-Z0-9-]* \|', l) and not l.startswith('| ID |'):
            c = [x.strip() for x in l.split('|')[1:-1]]
            if ncol is None or len(c) == ncol: out.append(c)
    return out


order = [(c[0], c[1]) for c in rows(PLAN)]
title = {c[0]: c[1] for c in rows(DRAFT, 4)}
hints = {c[0]: (c[2] + c[3]).count('🗣') for c in rows(DRAFT, 4)}  # 본문 · 멘트 열의 🗣(범례: 화면에 접힌 칸) = 화면에 접힌 칸으로 넣을 힌트 수


def plain(t):
    t = re.sub(r'<[^>]+>', '', t)
    return re.sub(r'\s+', ' ', html.unescape(t)).strip()


PARTIAL = '--partial' in sys.argv  # 미리보기용: 없는 장은 초안 제목으로 「작성 중」 자리표를 넣는다(검사 FAIL을 내지 않는다 · 최종 조립에는 쓰지 않는다)
fails, parts = [], {}
files = {p.stem: p for p in SL.glob('*.html')} if SL.exists() else {}
if not files and not PARTIAL:
    print('RESULT: 미판정 — 섹션 파일 0개'); sys.exit(2)
for rid, part in order:
    p = files.get(rid)
    if not p:
        if PARTIAL:
            t = html.escape(plain(title.get(rid, rid).replace('**', '')))
            parts.setdefault(part, []).append(f'<!-- {rid} -->\n'
                                              f'<section class="slide wip" data-slide="{rid}"><header class="s-head"><span class="s-brand">FRAME</span></header>'
                                              f'<p class="s-eyebrow">{rid} · 작성 중</p><h2 class="s-title">{t}</h2></section>')
            continue
        fails.append(f'누락 {rid}'); continue
    s = p.read_text(encoding='utf-8').strip()
    n = len(re.findall(r'<section\b', s))
    if n != 1: fails.append(f'{rid}: <section> {n}개')
    m = re.search(r'<section\b[^>]*\bdata-slide="([^"]+)"', s)
    if not m or m.group(1) != rid: fails.append(f'{rid}: data-slide {m.group(1) if m else "없음"}')
    for sym in ('💬', '👀', '🗣', '[터미널:', '[펼침]', '[파일:', '&lt;br&gt;'):
        if sym in s: fails.append(f'{rid}: 초안 표기 잔존 「{sym}」')
    if hints.get(rid, 0) > s.count('<details'): fails.append(f'{rid}: 🗣 힌트 {hints[rid]}개인데 접힌 칸(<details>) {s.count("<details")}개')
    want = plain(title.get(rid, '').replace('**', ''))
    if want and want not in plain(s): fails.append(f'{rid}: 초안 제목 없음 「{want[:30]}」')
    parts.setdefault(part, []).append(f'<!-- {rid} -->\n{s}')
extra = sorted(set(files) - {r for r, _ in order})
if extra: fails.append(f'결정표 밖 파일 {extra}')
if fails:
    for f in fails[:40]: print('  FAIL', f)
    print(f'RESULT: FAIL · 판정 {len(order)}장 · 위반 {len(fails)}건')
    if not PARTIAL: sys.exit(1)  # 미리보기(--partial)는 위반을 보여 주고 그대로 묶는다

for old in OUT.glob('part-*.html'): old.unlink()
for part, secs in sorted(parts.items()):
    (OUT / f'part-{int(part):02d}.html').write_text('\n\n'.join(secs) + '\n', encoding='utf-8', newline='\n')
(OUT / 'order.txt').unlink(missing_ok=True)
print(f'RESULT: {"PARTIAL" if PARTIAL else "PASS"} · 완성 {sum(1 for r, _ in order if r in files)}/{len(order)} · 판정 {len(order)}장 · part {len(parts)}개(' + ' · '.join(f'{k}={len(v)}' for k, v in sorted(parts.items())) + ')')
