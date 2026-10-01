"""E5 계약 — 결정표 순서로 deck.contract.json의 decks · layout_families를 새로 쓴다(known_violations · warn_baseline은 E7 실측 뒤 메인이 채운다 · 기존 값은 옛 47장 덱 기준이라 버린다)."""
import re, json, sys, pathlib
sys.stdout.reconfigure(encoding='utf-8')
R = pathlib.Path(__file__).resolve().parents[3]
S1 = R / 'courses/AI_에이전트_실습워크숍_4시간/sessions/1주차'
ids = []
for l in (R / 'plans/FRAME-개편/결정표.md').read_text(encoding='utf-8').split('\n'):
    if re.match(r'^\| [A-Z][A-Z0-9-]* \|', l) and not l.startswith('| ID |'):
        ids.append(l.split('|')[1].strip())
DIV = ['B2-0', 'B3-0', 'B4-0']
cut = [ids.index(d) for d in DIV]
intro = ids[:cut[0]]
seq = {'BLOCK2': ids[cut[0]:cut[1]], 'BLOCK3': ids[cut[1]:cut[2]], 'BLOCK4+HUB': ids[cut[2]:]}
old = json.loads((S1 / 'deck.contract.json').read_text(encoding='utf-8'))
c = {
    'week': '1주차', 'frozen': False,
    '_readme': 'FRAME 개편(2026-10-01) 82장 덱 구조 계약. 블록 간지 3장이 part-divider(--parts 3). 블록 1은 표지부터 첫 간지 전까지(intro), PART 5 허브 구간은 블록 4 뒤에 붙는다. 규약 정본은 sessions/README.md · 생성 plans/FRAME-개편/gen/build_contract.py.',
    'decks': {'강의덱': {
        'slides': len(ids), 'dividers': len(DIV), 'intro': intro, 'sequences': seq,
        'must_keep': {
            'HUB': '에이전트 실습 4종으로 가는 허브 — 슬롯 A · B에서 들어오고 복귀 장으로 돌아간다',
            'M3-4': '메인 과제의 공개 단계 — 폴더를 끌어다 놓아 주소를 만드는 장(D22)',
            'P1-3': '실습 ③ 확인 — 근거 줄을 원문과 대조하는 방법(정답 비공개)',
            'T-01': '맡길 일과 직접 할 일을 참가자 답으로 나누는 블록 4 토론 장',
        }}},
    'known_violations': {},
    'warn_baseline': {'static_gates': 0, 'quality': 0, 'render': 0, 'date': '2026-10-01', 'note': 'E7 렌더 감사 실측 뒤 갱신한다.'},
    'layout_families': {
        'f-cover': 'cover-frame', 'f-divider': 'divider-frame', 'f-concept': 'concept-fig',
        'f-slot': 'slot', 'f-hub': 'hub',
        'f-goal': 'pr-goal', 'f-steps': 'pr-steps', 'f-check': 'pr-check', 'f-fix': 'pr-fix',
        'f-return': 'pr-return', 'f-list': 'pr-list', 'f-screen': 'pr-screen'},
}
# kit 레이아웃(L-*)이 쓰는 기존 구도 클래스 등재는 옛 계약 값을 그대로 이어받는다(같은 kit 클래스)
for k, v in old.get('layout_families', {}).items(): c['layout_families'].setdefault(k, v)
(S1 / 'deck.contract.json').write_text(json.dumps(c, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
print('contract', len(ids), '장 · intro', len(intro), '· seq', {k: len(v) for k, v in seq.items()}, '· families', len(c['layout_families']))
