# -*- coding: utf-8 -*-
"""실습 9 · 인스타그램 카드뉴스(Canva) 준비물 폴더(2판 원칙: 완성 도구 HTML 없음 · 코드 틀 0 · md만).
폴더: 품질기준.md · 카드규격.md (templates/p9/ 에서 복사). 에이전트가 인터뷰 · 자료 정리 · 카드 문구 · 디자인 규칙을 만들고, 카드는 학생이 Canva에서 조립한다.
강사용 시연 절차서(templates/p9/시연_절차서.md)는 학생 폴더에 넣지 않고 실습자료_강사용/시연_절차서_카드뉴스.md 로 복사한다.
예시/ 폴더는 만들지 않는다: 「AI 최신 소식」 카드 문구 예시는 날짜와 출처 주소를 확인한 사실만 넣을 수 있고, 그 확인은 수업 전날 강사가 한다(시연 절차서 8번).

한 줄 실행(실습 9만 다시 만든다 — 폴더 · zip · 시연 절차서 복사본):  python gen_p9.py"""
import os
import shutil

from gen_common import BASE, INST, write_text

OUT = os.path.join(BASE, '실습9_카드뉴스')
DEMO_OUT = os.path.join(INST, '시연_절차서_카드뉴스.md')    # 강사용 복사본(학생 폴더 밖)
HERE = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(HERE, 'templates', 'p9')
TEXTS = ('품질기준.md', '카드규격.md')                  # 에이전트가 읽는 md
READ_LIMIT = 15 * 1024                                  # 에이전트 읽기 합계 상한(바이트)
CARD_SPEC_LIMIT = 3 * 1024                              # 카드규격.md 상한(설계 §4)
FORBID = ('.html', '.htm', '.js')                       # 2판 원칙: 완성 도구 · 코드 틀을 넣지 않는다


def read_tpl(path):
    """템플릿 md를 줄바꿈 LF로 읽는다(다른 실습 md와 같게 저장하려고)."""
    with open(path, encoding='utf-8-sig', newline=None) as f:
        return f.read()


def check(out, read_names):
    """html · js 0개 · 카드규격.md 크기 · 시연 절차서가 학생 폴더에 없음 · 에이전트 읽기 합계를 확인한다. (전체 파일 수, 읽기 합계)를 돌려준다."""
    files = [os.path.join(d, f) for d, _, fs in os.walk(out) for f in fs]
    bad = [p for p in files if p.lower().endswith(FORBID)]
    assert not bad, 'html · js 파일이 들어 있다: %s' % bad
    assert not any('시연' in os.path.basename(p) for p in files), '강사용 시연 절차서가 학생 폴더에 들어 있다'
    assert os.path.getsize(os.path.join(out, '카드규격.md')) <= CARD_SPEC_LIMIT, '카드규격.md가 3KB를 넘는다'
    total = sum(os.path.getsize(os.path.join(out, n)) for n in read_names)
    assert total <= READ_LIMIT, '에이전트 읽기 합계 %d바이트가 15KB를 넘는다' % total
    return len(files), total


def main():
    assert os.path.dirname(OUT) == BASE
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)                              # 이전 판의 파일이 남지 않게 폴더째 다시 만든다
    for name in TEXTS:
        write_text(os.path.join(OUT, name), read_tpl(os.path.join(TPL, name)))
    write_text(DEMO_OUT, read_tpl(os.path.join(TPL, '시연_절차서.md')))
    n_files, read_total = check(OUT, TEXTS)
    print('P9 파일 %d개 · html/js 0개 · 에이전트 읽기 %.1f KB(품질기준 + 카드규격) · 시연 절차서는 실습자료_강사용/시연_절차서_카드뉴스.md' % (
        n_files, read_total / 1024))


if __name__ == '__main__':
    # 실습 9만 다시 만든다: 폴더 → zip. gen_all.py는 다른 실습 폴더까지 지우므로 쓰지 않는다.
    main()
    from gen_all import zip_dir
    zip_dir(OUT, OUT + '.zip')
    n = sum(len(fs) for _, _, fs in os.walk(OUT))
    print('zip 실습9_카드뉴스.zip  파일 %d개  %.0f KB' % (n, os.path.getsize(OUT + '.zip') / 1024))
