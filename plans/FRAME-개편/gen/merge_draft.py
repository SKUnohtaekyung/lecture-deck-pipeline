"""C4 병합 — 초안 3종(개념 · 메인 과제 · 실습)을 결정표 순서로 모아 `1주차_초안.md`를 만든다.
누락 · 중복 · 결정표에 없는 행이 하나라도 있으면 쓰지 않고 exit 1. 다시 돌리면 같은 결과가 나온다."""
import re, sys, pathlib
sys.stdout.reconfigure(encoding='utf-8')
R = pathlib.Path(__file__).resolve().parents[3]
PLAN = R / 'plans/FRAME-개편'
DR = R / 'tmp/frame/draft'
OUT = R / 'courses/AI_에이전트_실습워크숍_4시간/sessions/1주차/1주차_초안.md'
SRC = {'concepts.md': '메인(C1)', 'main-task.md': 'frame-writer(C2a)', 'agent-practice.md': 'frame-writer(C2b)'}


def table_rows(text):
    return [l for l in text.split('\n') if re.match(r'^\| [A-Z][A-Z0-9]*-?[A-Z0-9-]* \|', l) and not l.startswith('| ID |')]


order, meta = [], {}
for l in table_rows((PLAN / '결정표.md').read_text(encoding='utf-8')):
    c = [x.strip() for x in l.split('|')[1:-1]]
    order.append(c[0]); meta[c[0]] = {'part': c[1], 'blk': c[2], 'kind': c[4]}

rows, owner, dup = {}, {}, []
for f, who in SRC.items():
    for l in table_rows((DR / f).read_text(encoding='utf-8')):
        rid = l.split('|')[1].strip()
        if rid in rows: dup.append(rid)
        rows[rid] = l; owner[rid] = who

missing = [i for i in order if i not in rows]
extra = [i for i in rows if i not in meta]
bad_cols = [i for i, l in rows.items() if len(l.split('|')) - 2 != 4]
if missing or extra or dup or bad_cols:
    print('FAIL 누락', missing, '· 결정표 밖', extra, '· 중복', dup, '· 4열 아님', bad_cols)
    sys.exit(1)

sub = re.search(r'> 부제 제안\(O-2[^\n]*', (DR / 'main-task.md').read_text(encoding='utf-8'))
head = f'''# FRAME 1주차 콘텐츠 초안 — AI 에이전트 실습 4시간

> 작성: create-slides(ⓑ 진입 · 2026-10-01) — 개념 파트는 메인, 메인 과제 · 운영 · 실습 파트는 frame-writer가 쓰고 메인이 병합했다(`plans/FRAME-개편/gen/merge_draft.py`).
> 대상: 코딩 경험이 없는 입문자 중심 혼합군 · 온라인(화면 공유) · 4시간(50분 블록 4개 + 휴식 10분 × 3 · 블록 시간은 상한, 남는 시간은 여유 — D34).
> 구조 정본: `plans/FRAME-개편/결정표.md`(장별 분 · 레이아웃 · 시각 자료 · 애니메이션 · 강조). 이 초안은 문구만 담는다.
> 결정: `plans/FRAME-개편/PLAN.md` §1 D1~D39. 특히 D31(실습 · 메인 과제 장에 개념 이름 · 설명 없음) · D32(요청문 = 터미널 UI · 참가자는 zip `요청문/` 폴더에서 복사) · D33(발표 없음) · D38(영상은 소개하지 않음) · D39(결과 글 필수 2개).
{sub.group(0) if sub else '> 부제 제안: (없음)'}

## 읽고 시작해

| 표기 | 뜻 | 처리 |
|---|---|---|
| 💬 | 강사 애드리브 | 발표자 노트에만 |
| 👀 | 시연 · 관찰 큐 | 발표자 노트에만 |
| 🗣 | 막힐 때만 펼치는 힌트 | 화면에 접힘 상태로 |
| `[터미널: 파일 · 이름]` | 요청문 | 화면에 터미널 창으로(D32) · 원문은 zip `요청문/` 폴더(`plans/FRAME-개편/gen/gen_prompts.py`) |
| `[펼침]` | 강사가 눌러 공개하는 정답 표시 | 화면에 접힘 상태로(실습 ④) |
| **정의** · **비유** · **대응** | 개념 장 서식(D11) | 본문 문구의 라벨 — 조립 때 타이포 위계로 |

## 0. 덱 기본 정보

| 항목 | 값 |
|---|---|
| 강의명 | FRAME |
| 주차 / 회차 | 1주차(1회 4시간) |
| 대상 | 코딩 경험이 없는 입문자 중심의 혼합군 |
| 톤 · 용어 수준 | 담백한 설명문(`plans/FRAME-개편/문체기준.md`) |
| 브랜드 | FRAME 로크업 · 테마 `kit/themes/frame/tokens.css` |

'''
TITLE = {'1': '블록 1', '2': '블록 2', '3': '블록 3', '4': '블록 4', '허브': '허브 구간(PART 5) — 슬롯 A · B에서 강사가 고른 실습'}
out, cur = [head], None
for rid in order:
    b = meta[rid]['blk']
    if b != cur:
        out.append(f'\n## {TITLE[b]}\n\n| # | 슬라이드 제목 | 본문 문구 | 비유·멘트 |\n|---|---|---|---|')
        cur = b
    out.append(rows[rid])
OUT.write_text('\n'.join(out) + '\n', encoding='utf-8', newline='\n')
cnt = {}
for rid in order: cnt[owner[rid]] = cnt.get(owner[rid], 0) + 1
print('PASS', OUT.name, len(order), '행 ·', ' · '.join(f'{k} {v}' for k, v in cnt.items()))
