# -*- coding: utf-8 -*-
"""실습 5 · 모션그래픽 v3 — 「내 주제 소개 영상」 준비물 폴더(2판 원칙: 완성 도구 HTML 없음 · 코드 틀 0 · md와 자료만).
폴더: 품질기준.md · 모션이름표.md(templates/p5_v3/ 에서 복사) · 예시/(하루상점 「데일리 쿡」 소개글 · 가격표 · 체험단 설문 결과 + _AI용_텍스트사본/).
학생은 인터뷰로 규칙 파일(AGENTS.md · CLAUDE.md)과 design.md를 만들고 영상.html을 처음부터 만든다. 주제가 없는 사람만 예시/ 자료를 쓴다.
자료의 함정: 소개글은 「열에 아홉」이라고 쓰지만 설문 결과는 120명 가운데 104명(87%)이다. 담당자 메모의 「주방용품 1위」는 근거 자료가 없다.
1판의 영상도구.html 템플릿(p5_kit.html · p5.html)과 1판 폴더는 _archive/실습_1판_2026-10-21/ 에 있다.

한 줄 실행(실습 5만 다시 만든다 — 폴더 · zip):  python gen_p5.py"""
import os
import shutil

from gen_common import BASE, COPY, copy_xlsx, write_docx, write_text, write_xlsx

OUT = os.path.join(BASE, '실습5_모션그래픽')
EX = os.path.join(OUT, '예시')
HERE = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(HERE, 'templates', 'p5_v3')
TEXTS = ('품질기준.md', '모션이름표.md')               # 에이전트가 읽는 md(예시 자료는 따로 센다)
READ_LIMIT = 15 * 1024                                  # 에이전트 읽기 합계 상한(바이트)
FORBID = ('.html', '.htm', '.js')                       # 2판 원칙: 완성 도구 · 코드 틀을 넣지 않는다


def read_tpl(path):
    """템플릿 md를 줄바꿈 LF로 읽는다(다른 실습 md와 같게 저장하려고)."""
    with open(path, encoding='utf-8-sig', newline=None) as f:
        return f.read()


def check(out, read_names):
    """폴더 안 html · js 개수(0이어야 함)와 에이전트 읽기 합계를 확인한다. (전체 파일 수, 읽기 합계)를 돌려준다."""
    files = [os.path.join(d, f) for d, _, fs in os.walk(out) for f in fs]
    bad = [p for p in files if p.lower().endswith(FORBID)]
    assert not bad, 'html · js 파일이 들어 있다: %s' % bad
    total = sum(os.path.getsize(os.path.join(out, n)) for n in read_names)
    assert total <= READ_LIMIT, '에이전트 읽기 합계 %d바이트가 15KB를 넘는다' % total
    return len(files), total


PRICES = [('도마', 18900, '양면 · 미끄럼 방지 받침'), ('집게', 9900, '한 손 잠금 · 실리콘 끝'), ('계량컵', 12900, '500mL · 눈금이 안쪽에')]
SET_PRICE = 36900
SURVEY = [('그렇다', 104), ('보통이다', 11), ('아니다', 5)]
REVIEWS = ['도마 받침 덕분에 밀리지 않아요', '집게를 한 손으로 잠글 수 있어 편합니다', '계량컵 눈금이 안쪽에 있어 위에서 보여요', '색이 차분해서 주방에 두기 좋아요',
           '설거지가 쉬워졌습니다', '도마가 생각보다 가볍습니다', '서랍 한 칸이 비었어요', '선물용으로도 괜찮겠어요', '집게 끝이 팬을 긁지 않아요', '세 가지만 있어도 충분했습니다']

INTRO = [
    ('h', '1. 하루상점'),
    ('p', '하루상점은 「매일 쓰는 것을, 조금 더 좋게」 만드는 온라인 생활용품점입니다. 2026년 여름 신상품으로 「데일리 쿡」 3종을 냅니다.'),
    ('h', '2. 왜 세 가지인가'),
    ('p', '지난 3월 고객 설문에서 「주방에서 가장 자주 쓰는 도구」를 물었습니다. 가장 많이 꼽힌 것은 도마 · 집게 · 계량컵이었습니다. 서랍 속 도구는 많지만 자주 쓰는 것은 세 가지였습니다.'),
    ('h', '3. 제품'),
    ('b', ['도마 — 양면으로 쓰고, 미끄럼 방지 받침이 달려 있습니다.', '집게 — 한 손으로 잠그고, 끝이 실리콘입니다.', '계량컵 — 500mL이고, 눈금이 안쪽에 있어 위에서 읽습니다.',
           '가격은 가격표.xlsx를 따릅니다. 세 가지를 묶은 세트가 있습니다.']),
    ('h', '4. 먼저 써 본 분들'),
    ('p', '사전 체험단 120명이 2주 동안 써 봤습니다. 열에 아홉이 다시 사고 싶다고 답했습니다. 후기 가운데 「서랍 한 칸이 비었어요」라는 말이 기억에 남습니다. 자세한 숫자는 체험단_설문결과.xlsx에 있습니다.'),
    ('h', '5. 출시'),
    ('p', '출시일은 2026년 6월 15일(월) 오전 10시입니다. 하루상점 자사몰에서 판매합니다.'),
    ('h', '담당자 메모(이도현)'),
    ('b', ['영상 길이는 30초 안팎. 자사몰 첫 화면과 인스타그램에 올립니다.', '「주방용품 1위」 같은 문구를 넣으면 좋겠습니다. 근거 자료는 아직 없습니다.']),
]


def main():
    assert os.path.dirname(OUT) == BASE
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)                              # 이전 판의 파일이 남지 않게 폴더째 다시 만든다
    for name in TEXTS:
        write_text(os.path.join(OUT, name), read_tpl(os.path.join(TPL, name)))
    txt = write_docx(os.path.join(EX, '신상품_소개글.docx'), '여름 신상품 「데일리 쿡」 소개글(영상 제작용)', INTRO,
                     '2026-05-28(목) · 작성 김나연(상품기획) · 검토 이도현(마케팅)')
    write_text(os.path.join(EX, COPY, '신상품_소개글.txt'), txt)
    total_price = sum(p for _, p, _ in PRICES)
    rows = [[n, p, f] for n, p, f in PRICES] + [['세 가지 세트', SET_PRICE, '도마 + 집게 + 계량컵 (낱개 합계 %s원)' % format(total_price, ',')]]
    copy_xlsx(EX, '가격표', write_xlsx(os.path.join(EX, '가격표.xlsx'), [('가격표', ['품목', '판매가(원)', '특징'], rows, {1: 16, 2: 14, 3: 44})]))
    copy_xlsx(EX, '체험단_설문결과', write_xlsx(os.path.join(EX, '체험단_설문결과.xlsx'), [
        ('다시 사고 싶은가', ['응답', '응답 수(명)'], [[a, n] for a, n in SURVEY], {1: 16, 2: 14}),
        ('후기', ['번호', '후기'], [[i + 1, r] for i, r in enumerate(REVIEWS)], {1: 8, 2: 50}),
    ]))
    n_files, read_total = check(OUT, TEXTS)
    total = sum(n for _, n in SURVEY)
    pct = round(SURVEY[0][1] / total * 100)
    print('P5 v3 파일 %d개 · html/js 0개 · 에이전트 읽기 %.1f KB(품질기준 + 모션이름표) · 예시 소개자료 3개 · 체험단 %d명 · 다시 사고 싶다 %d%%' % (
        n_files, read_total / 1024, total, pct))


if __name__ == '__main__':
    # 실습 5만 다시 만든다: 폴더 → zip. gen_all.py는 다른 실습 폴더까지 지우므로 쓰지 않는다.
    main()
    from gen_all import zip_dir
    zip_dir(OUT, OUT + '.zip')
    n = sum(len(fs) for _, _, fs in os.walk(OUT))
    print('zip 실습5_모션그래픽.zip  파일 %d개  %.0f KB' % (n, os.path.getsize(OUT + '.zip') / 1024))
