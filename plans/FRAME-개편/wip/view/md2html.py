"""설계서 .md → 읽기용 .html(제목·표·목록·인용·코드만). tmp 보기 전용."""
import re, html, pathlib, sys
R = pathlib.Path(__file__).resolve().parents[3]; OUT = pathlib.Path(__file__).parent
SRC = {'결정표': 'plans/FRAME-개편/결정표.md', '처분표': 'plans/FRAME-개편/처분표.md', '습관점검_설계': 'plans/FRAME-개편/습관점검_설계.md',
       '준비물_사양': 'plans/FRAME-개편/준비물_사양.md', '문체기준': 'plans/FRAME-개편/문체기준.md', 'PLAN': 'plans/FRAME-개편/PLAN.md',
       '개념노트': 'courses/AI_에이전트_실습워크숍_4시간/sessions/1주차/자료/개념노트.md', '출처': 'courses/AI_에이전트_실습워크숍_4시간/sessions/1주차/자료/출처.md',
       '리허설_체크리스트': 'plans/FRAME-개편/리허설_체크리스트.md',
       'G1b_제출': 'plans/FRAME-개편/G1b_제출.md',
       '초안': 'courses/AI_에이전트_실습워크숍_4시간/sessions/1주차/1주차_초안.md'}
def inl(t):
    t = html.escape(t).replace('&lt;br&gt;', '<br>')
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'~~(.+?)~~', r'<s>\1</s>', t)
    return re.sub(r'(https?://[^\s<|)]+)', r'<a href="\1" target="_blank">\1</a>', t)
def conv(md):
    out, i, L = [], 0, md.split('\n')
    while i < len(L):
        l = L[i]
        if l.startswith('```'):
            j = i + 1
            while j < len(L) and not L[j].startswith('```'): j += 1
            out.append('<pre>' + html.escape('\n'.join(L[i+1:j])) + '</pre>'); i = j + 1; continue
        if l.startswith('|'):
            rows = []
            while i < len(L) and L[i].startswith('|'):
                if not re.match(r'^\|[\s|:-]+\|$', L[i]): rows.append([c.strip() for c in L[i].split('|')[1:-1]])
                i += 1
            out.append('<div class="tw"><table><thead><tr>' + ''.join(f'<th>{inl(c)}</th>' for c in rows[0]) + '</tr></thead><tbody>' +
                       ''.join('<tr>' + ''.join(f'<td>{inl(c)}</td>' for c in r) + '</tr>' for r in rows[1:]) + '</tbody></table></div>'); continue
        m = re.match(r'^(#{1,4}) (.*)', l)
        if m: out.append(f'<h{len(m.group(1))}>{inl(m.group(2))}</h{len(m.group(1))}>')
        elif l.startswith('>'): out.append(f'<blockquote>{inl(l.lstrip("> "))}</blockquote>')
        elif re.match(r'^\s*[-*] ', l): out.append(f'<li style="margin-left:{len(l)-len(l.lstrip())}em">{inl(re.sub(r"^\s*[-*] ", "", l))}</li>')
        elif re.match(r'^\s*\d+\. ', l): out.append(f'<li class="ol" style="margin-left:{len(l)-len(l.lstrip())}em">{inl(l.strip())}</li>')
        elif l.strip() == '---': out.append('<hr>')
        elif l.strip(): out.append(f'<p>{inl(l)}</p>')
        i += 1
    return '\n'.join(out)
CSS = '''body{margin:0;background:var(--white);color:var(--ink);font-family:Pretendard,"Malgun Gothic",sans-serif;line-height:1.6}
.wrap{max-width:1180px;margin:0 auto;padding:28px 24px 64px} a{color:var(--blue)} .back{font-weight:700}
h1{font-size:28px}h2{font-size:22px;margin-top:32px;border-bottom:2px solid var(--line);padding-bottom:4px}h3{font-size:18px}
blockquote{margin:4px 0;padding:6px 14px;border-left:4px solid var(--blue);background:var(--blue-soft)}
li{list-style:none;padding-left:14px;position:relative}li:before{content:"·";position:absolute;left:2px;font-weight:800}li.ol:before{content:""}
code,pre{font-family:var(--font-mono);font-size:.92em}pre{background:var(--ink);color:#fff;padding:14px;border-radius:8px;white-space:pre-wrap}
.tw{overflow-x:auto}table{border-collapse:collapse;font-size:14px;margin:8px 0}th{background:var(--surface);text-align:left}th,td{padding:6px 8px;border:1px solid var(--line);vertical-align:top}'''
for name, rel in SRC.items():
    md = (R / rel).read_text(encoding='utf-8')
    (OUT / f'{name}.html').write_text(f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{name}</title><link rel="stylesheet" href="../../../kit/themes/frame/tokens.css"><style>{CSS}</style></head><body><div class="wrap"><p><a class="back" href="index.html">← 진행물 목록</a> · 원본 <code>{rel}</code></p>{conv(md)}</div></body></html>', encoding='utf-8')
print(len(SRC), 'pages')
