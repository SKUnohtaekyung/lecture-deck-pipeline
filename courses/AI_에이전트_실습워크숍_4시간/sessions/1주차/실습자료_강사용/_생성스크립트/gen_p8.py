# -*- coding: utf-8 -*-
"""실습 8 · 강의 교안 스킬 v2 — `lecture-deck` 스킬이 들어 있는 준비물 폴더(2판 원칙: 완성 도구 HTML 없음 · 코드 틀 0 · md만).
폴더: 품질기준.md · .agents/skills/lecture-deck/ · .claude/skills/lecture-deck/ (SKILL.md + references/01~05, 두 위치는 같은 파일).
Codex · Antigravity는 작업 폴더의 .agents/skills/<이름>/, Claude Code는 .claude/skills/<이름>/ 을 읽는다 → 설치 단계 없이 두 위치에 미리 넣는다.
원본은 templates/p8_v2/ (품질기준.md · lecture-deck/). 1판(리뷰 답글 스킬 · 스킬_틀 · 답글카드틀.html)은 만들지 않는다.
1판 폴더는 _archive/실습_1판_2026-10-21/ 에 있다. 점으로 시작하는 폴더(.agents · .claude)도 zip에 들어가는지는 실행 끝에 확인한다.

한 줄 실행(실습 8만 다시 만든다 — 폴더 · zip):  python gen_p8.py"""
import os
import shutil
import zipfile

from gen_common import BASE, write_text

OUT = os.path.join(BASE, '실습8_강의교안스킬')
HERE = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(HERE, 'templates', 'p8_v2')
SKILL_SRC = os.path.join(TPL, 'lecture-deck')
SKILL_DIRS = ('.agents/skills/lecture-deck', '.claude/skills/lecture-deck')   # 스킬이 놓이는 두 위치
SKILL_FILES = ('SKILL.md', 'references/01-인터뷰.md', 'references/02-디자인.md', 'references/03-장구성.md',
               'references/04-움직임.md', 'references/05-점검.md')
READ_LIMIT = 15 * 1024                                  # 에이전트 읽기 합계 상한(바이트)
SKILL_MAX_LINES = 120                                   # SKILL.md 줄 수 상한(설계 §3)
FORBID = ('.html', '.htm', '.js')                       # 2판 원칙: 완성 도구 · 코드 틀을 넣지 않는다


def read_tpl(path):
    """템플릿 md를 줄바꿈 LF로 읽는다(다른 실습 md와 같게 저장하려고)."""
    with open(path, encoding='utf-8-sig', newline=None) as f:
        return f.read()


def check(out):
    """html · js 0개 · SKILL.md 줄 수 · 두 스킬 위치가 같은 파일 · 에이전트 읽기 합계를 확인한다. (전체 파일 수, 읽기 합계)를 돌려준다."""
    files = [os.path.join(d, f) for d, _, fs in os.walk(out) for f in fs]
    bad = [p for p in files if p.lower().endswith(FORBID)]
    assert not bad, 'html · js 파일이 들어 있다: %s' % bad
    total = os.path.getsize(os.path.join(out, '품질기준.md'))
    for rel in SKILL_FILES:
        texts = []
        for base in SKILL_DIRS:
            p = os.path.join(out, *(base + '/' + rel).split('/'))
            assert os.path.isfile(p), '스킬 파일이 없다: %s/%s' % (base, rel)
            with open(p, 'rb') as f:
                texts.append(f.read())
        assert texts[0] == texts[1], '두 스킬 위치의 %s가 다르다' % rel
        total += len(texts[0])                          # 에이전트는 한 위치의 스킬만 읽으므로 한 번만 센다
    with open(os.path.join(out, *(SKILL_DIRS[0] + '/SKILL.md').split('/')), encoding='utf-8') as f:
        n_lines = len(f.read().splitlines())
    assert n_lines <= SKILL_MAX_LINES, 'SKILL.md가 %d줄이다(상한 %d줄)' % (n_lines, SKILL_MAX_LINES)
    assert total <= READ_LIMIT, '에이전트 읽기 합계 %d바이트가 15KB를 넘는다' % total
    return len(files), total


def verify_zip(zip_path):
    """zip 안에 두 위치의 SKILL.md(점으로 시작하는 폴더)가 들어 있는지 확인하고 항목 수를 돌려준다."""
    with zipfile.ZipFile(zip_path) as z:
        names = z.namelist()
    for base in SKILL_DIRS:
        want = '%s/%s/SKILL.md' % (os.path.basename(OUT), base)
        assert want in names, 'zip에 %s가 없다' % want
    return len(names)


def main():
    assert os.path.dirname(OUT) == BASE
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)                              # 이전 판의 파일이 남지 않게 폴더째 다시 만든다
    write_text(os.path.join(OUT, '품질기준.md'), read_tpl(os.path.join(TPL, '품질기준.md')))
    for base in SKILL_DIRS:
        for rel in SKILL_FILES:
            write_text(os.path.join(OUT, *(base + '/' + rel).split('/')), read_tpl(os.path.join(SKILL_SRC, *rel.split('/'))))
    n_files, read_total = check(OUT)
    print('P8 v2 파일 %d개 · html/js 0개 · 에이전트 읽기 %.1f KB(품질기준 + SKILL + references 5) · 스킬 위치 2곳(같은 파일 %d개씩)' % (
        n_files, read_total / 1024, len(SKILL_FILES)))


if __name__ == '__main__':
    # 실습 8만 다시 만든다: 폴더 → zip. gen_all.py는 다른 실습 폴더까지 지우므로 쓰지 않는다.
    main()
    from gen_all import zip_dir
    zip_dir(OUT, OUT + '.zip')
    n = verify_zip(OUT + '.zip')
    print('zip 실습8_강의교안스킬.zip  파일 %d개  %.0f KB  (.agents · .claude 스킬 포함 확인)' % (n, os.path.getsize(OUT + '.zip') / 1024))
