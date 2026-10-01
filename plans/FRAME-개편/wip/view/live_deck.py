"""초안 실시간 미리보기 — `1주차_초안.md` 82행을 FRAME 테마 1280×720 슬라이드로 그린다(조립본 아님 · tmp 보기 전용).
`--watch`: 초안 3종이 바뀌면 merge_draft.py → 다시 그리기. 페이지는 live.ver를 2초마다 읽어 바뀌면 새로고침한다."""
import re, html, sys, time, pathlib, subprocess
sys.stdout.reconfigure(encoding='utf-8')
R = pathlib.Path(__file__).resolve().parents[3]; OUT = pathlib.Path(__file__).parent
DRAFT = R / 'courses/AI_에이전트_실습워크숍_4시간/sessions/1주차/1주차_초안.md'
PLAN = R / 'plans/FRAME-개편/결정표.md'
WATCH = [R / 'tmp/frame/draft' / f for f in ('concepts.md', 'main-task.md', 'agent-practice.md')]


def inl(t):
    t = html.escape(t)
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    return t


def body_html(raw):
    """본문 문구 칸 → 줄 단위 블록. [터미널: …] 뒤 줄은 터미널 창, [펼침]은 접힌 칸, [파일: …]은 파일 창."""
    lines = [l for l in raw.split('<br>')]
    out, box = [], None
    def close():
        nonlocal box
        if box: out.append(f'<div class="{box[0]}"><div class="bar">{inl(box[1])}</div><pre>{"<br>".join(inl(x) for x in box[2])}</pre></div>')
        box = None
    for l in lines:
        m = re.match(r'\s*\[(터미널|파일): ([^\]]*)\]\s*(.*)', l)
        if m:
            close(); box = ['term' if m.group(1) == '터미널' else 'file', m.group(2), [m.group(3)] if m.group(3) else []]; continue
        if box and not re.match(r'\s*(\[펼침\]|타이머|대조할 것|계산 기준|다른 곳을|보낸 뒤|아래 요청문|- |\d+\. |\*\*)', l):
            box[2].append(l); continue
        close()
        m = re.match(r'\s*\[펼침\]\s*(.*)', l)
        if m: out.append(f'<details class="reveal"><summary>강사 공개</summary>{inl(m.group(1))}</details>'); continue
        if re.match(r'\s*- ', l): out.append(f'<li>{inl(l.strip()[2:])}</li>'); continue
        m = re.match(r'\s*(\d+)\. (.*)', l)
        if m: out.append(f'<li class="n"><span>{m.group(1)}</span>{inl(m.group(2))}</li>'); continue
        if l.strip(): out.append(f'<p>{inl(l)}</p>')
    close()
    return '\n'.join(out)


def build():
    meta = {}
    for l in PLAN.read_text(encoding='utf-8').split('\n'):
        if re.match(r'^\| [A-Z][A-Z0-9-]* \|', l) and not l.startswith('| ID |'):
            c = [x.strip() for x in l.split('|')[1:-1]]
            meta[c[0]] = {'blk': c[2], 'kind': c[4], 'min': c[3] if len(c) > 3 else ''}
    rows = []
    for l in DRAFT.read_text(encoding='utf-8').split('\n'):
        if re.match(r'^\| [A-Z][A-Z0-9-]* \|', l):
            c = [x.strip() for x in l.split('|')[1:-1]]
            if len(c) == 4: rows.append(c)
    slides = []
    for i, (rid, title, body, note) in enumerate(rows, 1):
        m = meta.get(rid, {})
        kind = m.get('kind', '')
        cls = 'pr' if '실습' in kind else 'cn' if '개념' in kind else 'tr' if '전환' in kind else 'mn'
        blk = m.get('blk', '')
        note = re.sub(r'<!--.*?-->', '', note)
        slides.append(f'''<section class="slide {cls}" id="s{i}" data-i="{i}">
<div class="kick"><span class="id">{rid}</span><span>{html.escape(kind)}</span><span>블록 {html.escape(blk)}</span><span class="no">{i} / {len(rows)}</span></div>
<h1>{inl(title)}</h1><div class="body">{body_html(body)}</div>
<div class="note">{inl(note).replace('&lt;br&gt;', '<br>')}</div></section>''')
    ver = str(int(time.time() * 1000))
    page = f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>FRAME 초안 미리보기</title><link rel="stylesheet" href="../../../kit/themes/frame/tokens.css"><style>{CSS}</style></head><body>
<header><b>FRAME 1주차 — 초안 실시간 미리보기</b><span>{len(rows)}장 · 조립본이 아니라 문구 확인용 · 초안이 바뀌면 자동 갱신</span>
<span class="btns"><button onclick="mode('grid')">전체 보기</button><button onclick="mode('one')">한 장씩(←→)</button><label><input type="checkbox" onchange="document.body.classList.toggle('shownote',this.checked)"> 강사 멘트</label></span><span id="st"></span></header>
<main id="deck" class="grid">{''.join(slides)}</main>
<script>
const V="{ver}";let cur=+(location.hash.slice(2)||1);const S=[...document.querySelectorAll('.slide')];
function mode(m){{deck.className=m;if(m=='one')go(cur);}}
function go(n){{cur=Math.max(1,Math.min(S.length,n));S.forEach(s=>s.classList.toggle('on',+s.dataset.i==cur));history.replaceState(0,'','#s'+cur);if(deck.className=='grid')S[cur-1].scrollIntoView({{block:'center'}});}}
S.forEach(s=>s.onclick=()=>{{cur=+s.dataset.i;if(deck.className=='grid')mode('one');}});
addEventListener('keydown',e=>{{if(e.key=='ArrowRight'||e.key==' ')go(cur+1);if(e.key=='ArrowLeft')go(cur-1);if(e.key=='Escape')mode('grid');}});
try{{if(sessionStorage.m)mode(sessionStorage.m);}}catch(e){{}}go(cur);
setInterval(async()=>{{try{{const t=(await (await fetch('live.ver?'+Date.now())).text()).trim();if(t&&t!=V){{try{{sessionStorage.m=deck.className}}catch(e){{}}location.reload();}}else st.textContent='최신 · '+new Date().toLocaleTimeString();}}catch(e){{st.textContent='서버 응답 없음';}}}},2000);
</script></body></html>'''
    (OUT / 'live.html').write_text(page, encoding='utf-8')
    (OUT / 'live.ver').write_text(ver, encoding='utf-8')
    return len(rows)


CSS = '''
body{margin:0;background:#E6ECEF;font-family:Pretendard,"Malgun Gothic",sans-serif;color:var(--ink)}
header{position:sticky;top:0;z-index:5;display:flex;gap:16px;align-items:center;flex-wrap:wrap;padding:10px 20px;background:var(--navy);color:#fff;font-size:14px}
header .btns{display:flex;gap:8px;align-items:center;margin-left:auto}header button{font:inherit;padding:4px 10px;border-radius:6px;border:1px solid #fff5;background:#fff1;color:#fff;cursor:pointer}
#st{opacity:.7;font-size:12px}
.slide{width:1280px;height:720px;box-sizing:border-box;padding:56px 72px;background:var(--white);position:relative;overflow:hidden;box-shadow:0 2px 10px #0002;border-radius:4px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(512px,1fr));gap:24px;padding:24px}
.grid .slide{zoom:.4;cursor:pointer}.grid .slide.on{outline:10px solid var(--mint)}
.one{display:flex;justify-content:center;padding:24px}.one .slide{display:none}.one .slide.on{display:block}
@media (max-width:1330px){.one .slide.on{zoom:calc(100vw / 1330px)}}
.kick{display:flex;gap:14px;font-size:17px;color:var(--gray-700,#555);margin-bottom:18px}.kick .id{font-weight:800;color:var(--blue)}.kick .no{margin-left:auto}
h1{margin:0 0 26px;font-size:40px;line-height:1.25;letter-spacing:-.02em;color:var(--navy)}
.body{font-size:24px;line-height:1.55}.body p{margin:0 0 10px}.body li{list-style:none;margin:0 0 8px;padding-left:22px;position:relative}
.body li:before{content:"·";position:absolute;left:4px;font-weight:900}.body li.n:before{content:none}.body li.n span{display:inline-block;width:30px;font-weight:800;color:var(--blue)}
.term,.file{margin:10px 0 14px;border-radius:10px;overflow:hidden;font-size:19px}.term{background:#0B1F26;color:#E6F3F5}.file{background:var(--surface,#EEF3F5);border:1px solid var(--line)}
.term .bar,.file .bar{padding:6px 14px;font-size:14px;opacity:.8;border-bottom:1px solid #fff2}.term pre,.file pre{margin:0;padding:12px 16px;white-space:pre-wrap;font-family:var(--font-mono)}
.reveal{margin:8px 0;padding:8px 14px;border:2px dashed var(--coral);border-radius:8px;font-size:20px}.reveal summary{cursor:pointer;font-weight:700;color:var(--coral-deep)}
.slide.cn{background:var(--white)}.slide.cn .kick .id{color:var(--mint-deep)}
.slide.pr{background:#fff;border-top:14px solid #E8622C}.slide.tr{background:var(--blue);color:#fff}.slide.tr h1{color:#fff}.slide.tr .kick,.slide.tr .kick .id{color:#CFE7EC}
.note{display:none;position:absolute;left:0;right:0;bottom:0;max-height:40%;overflow:auto;padding:12px 72px;background:#FFF8E6;border-top:2px solid var(--coral);font-size:16px;line-height:1.5;color:#3D2400}
.shownote .note{display:block}
'''

if __name__ == '__main__':
    print('rows', build())
    if '--watch' in sys.argv:
        last = [p.stat().st_mtime for p in WATCH]
        while True:
            time.sleep(1.5)
            now = [p.stat().st_mtime for p in WATCH]
            if now != last:
                last = now
                r = subprocess.run([sys.executable, str(R / 'plans/FRAME-개편/gen/merge_draft.py')], capture_output=True, text=True, encoding='utf-8')
                print(time.strftime('%H:%M:%S'), r.stdout.strip()[:80], '→ rows', build(), flush=True)
