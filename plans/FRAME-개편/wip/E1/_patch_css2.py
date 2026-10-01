import sys, re
sys.stdout.reconfigure(encoding='utf-8')


def edit(path, pairs):
    s = open(path, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (path, a[:70])
        s = s.replace(a, b, 1)
    open(path, 'w', encoding='utf-8').write(s)


edit('tmp/frame/E1/src/10-base.css', [
    ("--sh-card:0 6px 18px rgba(8,50,61,.10);",
     "--t-pr-fill:#FF8A5C; --t-shadow:rgba(8,50,61,.16);\n      --sh-card:0 6px 18px rgba(8,50,61,.10);"),
])
edit('tmp/frame/E1/src/30-layouts.css', [
    (".pv-before .sheet{ fill:var(--t-card); stroke:none; filter:none; }",
     ".pv-before .sheet{ fill:var(--t-card); stroke:none; filter:drop-shadow(0 5px 8px var(--t-shadow)); }"),
    (".loc .page{ fill:var(--t-card); stroke:none; }",
     ".loc .page{ fill:var(--t-card); stroke:none; filter:drop-shadow(0 5px 8px var(--t-shadow)); }"),
])

# 여정 지도 CSS 교체
p = 'tmp/frame/E1/src/40-v2.css'
s = open(p, encoding='utf-8').read()
a = s.index("    .jr-road{ position:absolute;")
b = s.index("    /* .dotgrid(data-n")
new = """    .jr-road{ position:absolute; inset:0; width:100%; height:100%; overflow:visible; }
    .jr-road path{ fill:none; stroke-width:44px; stroke-linecap:round; vector-effect:non-scaling-stroke; }
    .jr-road .base{ stroke:var(--jr-road); } .jr-road .on{ stroke:var(--jr-on); }
    .jr-st{ position:absolute; width:0; height:0; }
    .jr-st .jr-d{ position:absolute; left:0; top:0; display:block; width:22px; height:22px; margin:-11px 0 0 -11px; overflow:visible; }
    .jr-st.now .jr-d{ width:60px; height:60px; margin:-30px 0 0 -30px; }
    .jr-d .ring{ fill:none; stroke:var(--jr-ring); stroke-width:4; } .jr-d .fill{ fill:var(--jr-done); } .jr-d .glow{ fill:var(--t-glow); } .jr-d .core{ fill:var(--mint); }
    .jr-st.next .fill, .jr-st.done .ring{ display:none; }
    .jr-st b{ position:absolute; left:0; top:26px; transform:translateX(-50%); font-size:22px; font-weight:700; line-height:1.3; color:var(--jr-ink); white-space:nowrap; }
    .jr-st.now b{ top:36px; color:var(--jr-now-ink); }
    .jr-tag{ position:absolute; z-index:0; transform:translate(-50%,-100%); padding:6px 14px; font-size:16px; font-weight:800; line-height:1.3; color:var(--on-mint); white-space:nowrap; }
    .jr-tag::before{ content:""; position:absolute; inset:0; z-index:-1; border-radius:999px; background:var(--mint); }

"""
s = s[:a] + new + s[b:]
open(p, 'w', encoding='utf-8').write(s)

# build_shell: 40-v2.css 포함
p = 'tmp/frame/E1/build_shell.py'
s = open(p, encoding='utf-8').read()
a = "('10-base.css', '20-components.css', '30-layouts.css')"
assert a in s
s = s.replace(a, "('10-base.css', '20-components.css', '30-layouts.css', '40-v2.css')")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
