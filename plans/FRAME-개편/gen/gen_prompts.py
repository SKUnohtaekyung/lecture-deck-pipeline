"""요청문 폴더 생성 — 초안의 「요청문 원문」 섹션에서 zip용 `요청문/*.txt`(참가자용)와 강사용 표준형을 만든다.
참가자용에는 정답 값이 든 표준형을 넣지 않는다(D35 · C2b 판단). 다시 돌리면 같은 결과가 나온다."""
import re, os, pathlib, time, sys
sys.stdout.reconfigure(encoding='utf-8')
R = pathlib.Path(__file__).resolve().parents[3]
DR = R / 'tmp/frame/draft'
S1 = R / 'courses/AI_에이전트_실습워크숍_4시간/sessions/1주차'
OUT = S1 / '실습자료/실습자료_FRAME/요청문'
TOUT = S1 / '실습자료_강사용/요청문_표준형'
MTIME = time.mktime((2026, 3, 30, 9, 0, 0, 0, 0, -1))
HEAD = '# 요청문 — {name}\n# 복사해서 에이전트 앱에 붙여 넣습니다. 〈 〉 자리는 내가 찾은 내용으로 바꿔 씁니다.\n\n'
HEAD1 = '# 요청문 — {name}\n# 복사해서 에이전트 앱에 붙여 넣습니다.\n\n'

def blocks(text):
    """(제목, 본문) — 코드 펜스 바로 앞의 비어 있지 않은 줄을 제목으로 쓴다."""
    out, lines = [], text.split('\n')
    i = 0
    while i < len(lines):
        if lines[i].startswith('```'):
            j = i + 1
            while not lines[j].startswith('```'): j += 1
            k = i - 1
            while k >= 0 and not lines[k].strip(): k -= 1
            out.append((lines[k].strip(), '\n'.join(lines[i + 1:j])))
            i = j + 1
        else:
            i += 1
    return out

def write(path, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body.replace('\r\n', '\n').encode('utf-8'))
    os.utime(path, (MTIME, MTIME))

# 00 — 메인 과제(=== 이름 === 구분이 이미 들어 있다)
mt = (DR / 'main-task.md').read_text(encoding='utf-8')
sec = mt[mt.index('## 요청문 원문'):]
b00 = blocks(sec)
assert len(b00) == 1, len(b00)
write(OUT / '00_AI습관점검.txt', HEAD.format(name='AI 활용 습관 점검') + b00[0][1] + '\n')

# 01~04 — 에이전트 실습
ap = (DR / 'agent-practice.md').read_text(encoding='utf-8')
sec = ap[ap.index('## 요청문 원문'):]
parts = re.split(r'^### (0[1-4]_[^\n]+)\.txt\s*$', sec, flags=re.M)
count = 0
for name, body in zip(parts[1::2], parts[2::2]):
    user, std = [], []
    for title, text in blocks(body):
        if '표준형' in title: std.append(f'=== {title} ===\n{text}')
        else: user.append(f"=== {re.sub(r'\s*[(—].*$', '', title)} ===\n{text}")  # 제작 메모(괄호 · 줄표 뒤)는 참가자 파일에 넣지 않는다
    # 첫 요청과 고쳐 보낼 요청은 파일을 나눈다 — 고치기 틀이 ③ 확인 전에 보이지 않게(C3 검토 13)
    write(OUT / f'{name}.txt', HEAD1.format(name=name) + user[0] + '\n')
    write(OUT / f'{name}_고치기.txt', HEAD.format(name=name + ' · 고쳐 보낼 요청') + '\n\n'.join(user[1:]) + '\n')
    if std: write(TOUT / f'{name}_표준형.txt', '\n\n'.join(std) + '\n')
    count += 1
assert count == 4, count

# 체험 — 같은 문단을 두 가지로 묻기(X-01)
PARA = ('도담수납 고객지원팀에서 알려 드립니다. 다음 주부터 A/S 접수 방법이 바뀝니다. '
        '앞으로는 홈페이지에서 접수해 주시면 되고, 접수하시면 담당자가 빠르게 연락드리겠습니다. '
        '전화 접수도 당분간은 계속 받습니다. 접수하실 때는 주문 번호와 사진을 꼭 함께 보내 주세요. '
        '많은 이용 부탁드립니다.')
X = ('=== 질문 1 — 새 대화에서 ===\n아래 문단은 제가 쓴 건데 정말 잘 쓴 것 같아요. 최고죠?\n\n' + PARA +
     '\n\n=== 질문 2 — 다른 새 대화에서 ===\n아래 문단의 문제점을 세 가지 찾아 줘.\n\n' + PARA + '\n')
write(OUT / '체험_문단.txt', HEAD.format(name='체험 — 같은 문단을 두 가지로 물어보기') + X)

files = sorted(p.name for p in OUT.iterdir())
leak = [p.name for p in OUT.iterdir() if re.search(r'3월 27일|4,620,000|문의_09와 문의_12', p.read_text(encoding='utf-8'))]
print('요청문', len(files), files)
print('표준형(강사용)', sorted(p.name for p in TOUT.iterdir()))
print('정답 값 누출', leak or 0)
sys.exit(1 if leak or len(files) != 10 else 0)
