"""조립 진행 실시간 미리보기 — 섹션 파일 · shell이 바뀌면 build_parts --partial → assemble_deck.
열어 둔 덱은 live_deck.ver를 폴링해 새로고침한다(shell의 FRAME 엔진이 아니라 아래 주입 스크립트가 한다 — 미리보기 사본에만 넣는다)."""
import sys, time, pathlib, subprocess
R = pathlib.Path(__file__).resolve().parents[3]
S1 = R / 'courses/AI_에이전트_실습워크숍_4시간/sessions/1주차'
SL = R / 'tmp/frame/E/slides'
OUT = pathlib.Path(__file__).parent
PY = sys.executable
POLL = ('<script>(function(){var v=null;setInterval(function(){fetch("live_deck.ver?"+Date.now()).then(function(r){return r.text()})'
        '.then(function(t){t=t.trim();if(v===null)v=t;else if(t!==v){try{sessionStorage.frameLiveHash=location.hash}catch(e){}location.reload()}})'
        '.catch(function(){})},2000)})();</script>')


def sig():
    fs = list(SL.glob('*.html')) if SL.exists() else []
    fs.append(S1 / '강의덱.초안/shell.html')
    return tuple(sorted((f.name, f.stat().st_mtime) for f in fs if f.exists()))


def once():
    a = subprocess.run([PY, str(R / 'plans/FRAME-개편/gen/build_parts.py'), '--partial'], capture_output=True, text=True, encoding='utf-8')
    b = subprocess.run([PY, str(R / 'scripts/assemble_deck.py'), str(S1 / '강의덱.초안')], capture_output=True, text=True, encoding='utf-8')
    deck = (S1 / '강의덱.html').read_text(encoding='utf-8')
    # 미리보기 사본은 같은 깊이(`tmp/frame/view/`는 깊이가 달라 kit 경로가 깨진다)에 둘 수 없으므로 덱 폴더 옆 tmp가 아니라
    # 저장소 루트 기준 절대 경로로 kit를 참조하게 바꿔 tmp/frame/view/live_deck.html로 쓴다.
    deck = deck.replace('href="../../../../kit/', 'href="/kit/').replace('src="../../../../kit/', 'src="/kit/')
    deck = deck.replace('</body>', POLL + '</body>')
    (OUT / 'live_deck.html').write_text(deck, encoding='utf-8')
    (OUT / 'live_deck.ver').write_text(str(int(time.time() * 1000)), encoding='utf-8')
    last = (a.stdout.strip().splitlines() or ['?'])[-1]
    print(time.strftime('%H:%M:%S'), last[:120], '| assemble', b.returncode, flush=True)


if __name__ == '__main__':
    once()
    if '--watch' in sys.argv:
        s = sig()
        while True:
            time.sleep(3)
            n = sig()
            if n != s:
                s = n
                try: once()
                except Exception as e: print('ERR', e, flush=True)
