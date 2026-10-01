import sys
sys.stdout.reconfigure(encoding='utf-8')
p = 'tmp/frame/E1/src/20-components.css'
s = open(p, encoding='utf-8').read()


def rep(a, b, cnt=1):
    global s
    assert a in s, a[:80]
    s = s.replace(a, b, cnt)


# 터미널
rep(".term{ width:100%; }", ".term{ width:100%; }\n    .term.terminal-dark{ border-radius:20px; box-shadow:var(--sh-pop); }")
rep("    .term .copy:focus-visible{ outline:2px dashed var(--white); outline-offset:2px; }",
    "    .term .copy:focus-visible{ outline:2px dashed var(--white); outline-offset:2px; }\n"
    "    /* 펼침 칸 안의 터미널 — .reveal-body p의 글자색 · 여백이 터미널 글자를 덮지 않게(W1 제안 반영) */\n"
    "    .reveal .reveal-body .term .terminal-copy p{ color:inherit; margin:0; }\n"
    "    .reveal .reveal-body .term .terminal-copy p + p{ margin-top:10px; }")

# 창 모형
a = s.index("    /* ── 6. 창 모형")
b = s.index("    /* ── 7. 표")
win = """    /* ── 6. 창 모형(D27 공통 화면 모형 · 파일 창) — 흰 카드 + 약한 그림자. 테두리 선을 쓰지 않는다. 창 하나가 박스 1개 ── */
    .win{ background:var(--t-card); border-radius:20px; box-shadow:var(--sh-card); overflow:hidden; text-align:left; }
    .win-bar{ display:flex; align-items:center; gap:9px; min-height:46px; padding:0 20px; }
    .win-bar i{ flex:0 0 auto; width:10px; height:10px; border-radius:50%; background:var(--gray-400); opacity:.45; }
    .win-bar b{ margin-left:8px; font-size:17px; font-weight:700; color:var(--gray-700); line-height:1.3; }
    .win-body{ padding:4px 22px 20px; }
    .win-url{ position:relative; z-index:0; flex:1 1 auto; margin-left:10px; padding:5px 16px; font-size:17px; font-weight:700; color:var(--gray-700); }
    .win-url::before{ content:""; position:absolute; inset:0; z-index:-1; border-radius:999px; background:var(--blue-soft); }
    .win-side{ position:relative; z-index:0; float:left; width:200px; padding:14px 18px; min-height:100%; }
    .win-side::before{ content:""; position:absolute; inset:0; z-index:-1; background:var(--blue-panel); }
    .win-side p{ margin:0 0 8px; font-size:17px; font-weight:700; color:var(--gray-700); }
    .win.app .win-body{ padding:0; display:grid; grid-template-columns:200px 1fr; }
    .win.app .win-side{ float:none; }
    .win-main{ padding:14px 22px 18px; }
    .drop{ margin:10px 0; padding:22px 16px; text-align:center; font-size:var(--fs-body); font-weight:700; color:var(--gray-700); outline:3px dashed var(--mint); outline-offset:-3px; border-radius:var(--r-md); }
    .slide.pr .drop{ outline-color:var(--pr-fill); color:var(--ink); }
    /* 코드·파일 줄 — 줄 번호 + 본문. 파일 이름 · 경로 · 트리도 본문 글꼴이다(고정폭은 터미널 안에만). .hit 줄은 왼쪽 띠로 표시한다 */
    .code{ margin:0; font-family:inherit; font-size:var(--fs-box-desc); font-weight:600; line-height:1.6; color:var(--gray-700); white-space:pre-wrap; word-break:keep-all; overflow-wrap:anywhere; font-variant-numeric:tabular-nums; }
    .code .l{ display:block; position:relative; min-height:1.6em; padding-left:54px; }
    .code .l > i{ position:absolute; left:0; width:38px; text-align:right; font-style:normal; color:var(--gray-400); }
    .code .l.ref{ color:var(--gray-700); font-weight:600; }
    .code .l.hit, .code .l.on{ color:var(--ink); font-weight:800; }
    .code .l.hit::before, .code .l.on::before{ content:""; position:absolute; left:-12px; top:3px; bottom:3px; width:6px; border-radius:3px; background:var(--mint); }
    .slide.pr .code .l.hit::before, .slide.pr .code .l.on::before{ background:var(--pr-fill); }
    .slide.pr .code .l.on{ color:var(--pr-deep); }
    .code .l.gap{ color:var(--gray-400); }
    .code .dir{ font-weight:800; color:var(--ink); }
    .bubble{ display:block; width:fit-content; max-width:100%; margin:8px 0; padding:10px 18px; border-radius:var(--r-lg); background:var(--blue-soft); font-size:var(--fs-box-desc); line-height:1.45; color:var(--ink); }
    .bubble.me{ margin-left:auto; background:var(--mint-soft); }
    .slide.pr .bubble, .slide.pr .bubble.me{ background:var(--pr-soft); }
    /* 박스 없는 대화 — 작은 라벨 + 글 */
    .say{ position:relative; margin:0 0 18px; padding:0; }
    .say .who{ display:block; margin:0 0 2px; font-size:16px; font-weight:800; line-height:1.4; letter-spacing:.04em; color:var(--gray-400); }
    .say.me .who{ color:var(--mint-deep); }
    .slide.pr .say.me .who{ color:var(--pr-deep); }
    .say p{ margin:0; font-size:var(--fs-body); font-weight:600; line-height:1.55; color:var(--ink); }

"""
s = s[:a] + win + s[b:]

# 표
a = s.index("    /* ── 7. 표")
b = s.index("    /* ── 8. 조작 요소")
tbl = """    /* ── 7. 표 — 선 없이 머리 글자 색 + 줄 사이 여백. 고른 행은 옅은 면(inset 그림자)으로 표시한다 ── */
    .ftbl{ width:100%; border-collapse:separate; border-spacing:0; }
    .ftbl th, .ftbl td{ text-align:left; padding:10px 12px; font-size:var(--fs-box-desc); font-weight:500; line-height:1.3; color:var(--ink); vertical-align:middle; }
    .ftbl th{ font-size:var(--fs-table); font-weight:800; color:var(--mint-deep); white-space:nowrap; }
    .slide.pr .ftbl th{ color:var(--pr-deep); }
    .ftbl td.src{ font-size:18px; font-weight:600; color:var(--gray-700); white-space:nowrap; }
    .ftbl .x{ color:var(--red); font-weight:800; }
    .ftbl tr[data-pick]{ cursor:pointer; }
    .ftbl tr[data-pick]:focus-visible{ outline:2px dashed var(--ink); outline-offset:-2px; }
    .ftbl tr[data-pick] td{ color:var(--gray-700); }
    .ftbl tr[data-pick].on td{ color:var(--ink); font-weight:700; box-shadow:inset 0 0 0 100px var(--blue-soft); }
    .slide.pr .ftbl tr[data-pick].on td{ box-shadow:inset 0 0 0 100px var(--pr-soft); }
    .ftbl tr[data-pick].on td:first-child{ border-radius:12px 0 0 12px; }
    .ftbl tr[data-pick].on td:last-child{ border-radius:0 12px 12px 0; }
    .slide.pr .ftbl tr[data-pick].on td.due{ color:var(--pr-deep); font-weight:800; }
    .ftbl-cap{ display:block; margin:0 0 4px; font-size:var(--fs-caption); font-weight:700; color:var(--gray-700); }

"""
s = s[:a] + tbl + s[b:]

# flow / timer
rep(".flow .n{ font-family:var(--font-mono); font-size:44px; font-weight:800; line-height:1; letter-spacing:-.03em; color:var(--pr-deep); text-align:center; }   /* 표식 ④ 단계 번호 */",
    ".flow .n{ font-size:44px; font-weight:800; line-height:1; letter-spacing:-.03em; font-variant-numeric:tabular-nums; color:var(--pr-deep); text-align:center; }   /* 표식 ④ 단계 번호 */")
rep(".flow .t{ font-size:var(--fs-body); font-weight:600; line-height:1.5; padding-top:4px; }",
    ".flow .t{ font-size:var(--fs-body); font-weight:500; line-height:1.5; padding-top:4px; }\n    .flow .t b{ font-weight:800; color:var(--pr-deep); }")
rep(".timer .tv{ font-family:var(--font-mono); font-size:56px; font-weight:700; line-height:1; letter-spacing:-.03em; color:var(--pr-deep); }",
    ".timer .tv{ font-size:56px; font-weight:800; line-height:1; letter-spacing:-.03em; font-variant-numeric:tabular-nums; color:var(--pr-deep); }")
rep("    .timer.big .tv{ font-size:120px; }",
    "    .timer.big .tv{ font-size:120px; }\n    .timer.sm{ gap:10px; }                                   /* 제목 줄 오른쪽의 작은 타이머(W1 제안 반영) */\n    .timer.sm .tv{ font-size:34px; }\n    .timer.sm .tl{ font-size:17px; }")

# reveal
a = s.index("    /* [펼침] — 강사가")
b = s.index("    /* 돌아가기·이동 버튼")
rv = """    /* [펼침] — 강사가 눌러서 공개하는 칸. <details>라 Enter/Space로 열린다. 닫힌 동안은 본문을 배치에서 뺀다 */
    .reveal{ position:relative; padding:0; }
    .reveal::before{ content:none; }
    .reveal:not([open]) > .reveal-body{ display:none; }    /* 이 줄이 없으면 Chromium이 닫힌 details 자식의 배치를 유지해 감사가 겹침 · 가려짐으로 잡는다(W2 실측) */
    .reveal > summary{ position:relative; z-index:0; display:inline-flex; align-items:baseline; gap:10px; padding:8px 20px; list-style:none; cursor:pointer; font-size:var(--fs-lead); font-weight:800; line-height:1.3; color:var(--pr-deep, var(--blue)); }
    .reveal > summary::after{ content:""; position:absolute; inset:0; z-index:-1; border-radius:999px; background:var(--pr-soft, var(--blue-soft)); }
    .reveal > summary::-webkit-details-marker{ display:none; }
    .reveal > summary::before{ content:"▸"; font-size:var(--fs-eyebrow); }
    .reveal[open] > summary::before{ content:"▾"; }
    .reveal > summary .hint{ font-size:var(--fs-box-desc); font-weight:500; color:var(--gray-700); }
    .reveal[open] > summary .hint{ display:none; }
    .reveal .reveal-body{ margin-top:10px; }
    .reveal .reveal-body p{ margin:0 0 8px; font-size:var(--fs-body); line-height:1.55; color:var(--ink); }
    /* 위에 겹쳐 뜨는 펼침 패널 — .reveal.pop. 폭은 style="--rw:740px". 흰 카드 + 그림자, 열린 동안만 자리를 차지한다 */
    .reveal.pop > .reveal-body{ position:absolute; left:0; top:100%; z-index:6; margin-top:10px; width:var(--rw,700px); padding:16px 20px; background:var(--t-card); border-radius:22px; box-shadow:var(--sh-pop); }
"""
s = s[:a] + rv + s[b:]
open(p, 'w', encoding='utf-8').write(s)
print('ok')
