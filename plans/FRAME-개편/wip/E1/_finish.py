import re, sys, pathlib, subprocess, os
sys.stdout.reconfigure(encoding='utf-8')
R = pathlib.Path(__file__).resolve().parents[3]
E1 = R / 'tmp/frame/E1'

# 1) .facts 보조 클래스(프리뷰 수정안 3의 「만들 것 · 준비물 · 시간」 줄) — 40-v2.css 끝에
p = E1 / 'src/40-v2.css'
s = p.read_text(encoding='utf-8')
if '.facts' not in s:
    s += """
    /* .facts — 라벨 + 값 줄 목록(만들 것 · 준비물 · 시간). 면 · 선 없이 글자 위계만 */
    .facts{ margin:26px 0 0; display:grid; gap:14px; }
    .facts .f{ display:grid; grid-template-columns:88px 1fr; margin:0; }
    .facts dt{ padding-top:3px; font-size:17px; font-weight:800; line-height:1.4; color:var(--gray-400); }
    .facts dd{ margin:0; font-size:var(--fs-lead); font-weight:500; line-height:1.5; color:var(--ink); }
"""
    p.write_text(s, encoding='utf-8')

# 2) v2 시험 덱 t2 — shell + part-03(v2 장 7개)
HEADER = ('<header class="s-head">\n'
          '    <svg class="s-logo" viewBox="0 0 48 48" aria-hidden="true"><path d="M8 18 V8 H18 M30 8 H40 V18 M40 30 V40 H30 M18 40 H8 V30" fill="none" style="stroke:var(--blue)" stroke-width="5"/><rect x="19" y="19" width="10" height="10" style="fill:var(--mint)"/></svg><span class="s-brand">FRAME</span>\n'
          '    <span class="s-line"></span><div class="s-team">{team}</div>\n'
          '  </header>')
t = (E1 / 'src/part-v2.tpl.html').read_text(encoding='utf-8')
t = re.sub(r'@@H\((.*?)\)@@', lambda m: HEADER.format(team=m.group(1)), t)
d = E1 / 't2/강의덱.초안'
d.mkdir(parents=True, exist_ok=True)
(d / 'part-01.html').write_text(t, encoding='utf-8')

# 3) 셸 재생성(과정 경로 + 시험 덱 둘 다) + 조립
py = sys.executable
subprocess.run([py, str(E1 / 'build_shell.py')], check=True)
subprocess.run([py, str(E1 / 'build_shell.py'), '--out', str(E1 / 't/강의덱.초안/shell.html')], check=True, stdout=subprocess.DEVNULL)
subprocess.run([py, str(E1 / 'build_shell.py'), '--out', str(d / 'shell.html')], check=True, stdout=subprocess.DEVNULL)
for dd in ('t', 't2'):
    r = subprocess.run([py, str(R / 'scripts/assemble_deck.py'), str(E1 / dd / '강의덱.초안')], capture_output=True, text=True, encoding='utf-8')
    print(dd, r.stdout.strip().splitlines()[-1])
