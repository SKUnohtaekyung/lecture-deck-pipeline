# -*- coding: utf-8 -*-
"""강사용 완성 예시 HTML을 만든다 — templates/*.html 에 정답 데이터(_data/*.json)를 끼운다.
실행: python build_examples.py   (gen_all.py를 먼저 실행해 _data를 만들어 둔다)"""
import os

from gen_common import DATA, INST, ensure

HERE = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(HERE, 'templates')
OUT = ensure(os.path.join(INST, '완성예시'))
JOBS = [('p1.html', 'p1.json', '실습1_실행보드.html'), ('p2.html', 'p2.json', '실습2_세컨드브레인.html'),
        ('p3.html', 'p3.json', '실습3_응대센터.html'), ('p4.html', 'p4.json', '실습4_주간대시보드.html'),
        ('p5.html', None, '실습5_모션그래픽.html'), ('p6.html', 'p6.json', '실습6_안내문.html'), ('p7.html', 'p7.json', '실습7_퀴즈게임.html'),
        ('p8.html', None, '실습8_스킬만들기.html'),
        ('main.html', None, '메인과제_AI습관점검_index.html')]


def main():
    base = open(os.path.join(TPL, 'base.css'), encoding='utf-8').read()
    for tpl, data, out in JOBS:
        src = os.path.join(TPL, tpl)
        if not os.path.exists(src):
            continue
        html = open(src, encoding='utf-8').read().replace('/*__BASE__*/', base)
        if data:
            html = html.replace('/*__DATA__*/', open(os.path.join(DATA, data), encoding='utf-8').read())
        with open(os.path.join(OUT, out), 'w', encoding='utf-8', newline='\n') as f:
            f.write(html)
        print('완성예시/%s  %.0f KB' % (out, len(html.encode('utf-8')) / 1024))


if __name__ == '__main__':
    main()
