# -*- coding: utf-8 -*-
"""실습 8 · 스킬을 만드는 실습 v3 — 준비물 폴더에는 md 세 파일뿐이다(스킬은 참가자가 에이전트와 함께 오늘 만든다).
폴더: 품질기준.md · 규칙예시.md · 디자인시스템_틀.md (templates/p8_v3/ 에서 복사). 스킬 폴더(.agents · .claude) · SKILL.md · references/ 는 만들지 않는다.
참가자의 에이전트가 .agents/skills/lecture-deck/SKILL.md 와 references/design-systems/ · memory/ 를 실습 중에 만든다.
v2(스킬이 미리 들어 있던 판)의 원본은 실습자료_강사용/_archive/실습8_2판_2026-10-25/ 로 옮겼다(2026-10-25 · 이 스크립트는 읽지 않는다). 1판 폴더는 _archive/실습_1판_2026-10-21/ 에 있다.

한 줄 실행(실습 8만 다시 만든다 — 폴더 · zip):  python gen_p8.py"""
import os
import shutil
import zipfile

from gen_common import BASE, write_text

OUT = os.path.join(BASE, '실습8_강의교안스킬')
HERE = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(HERE, 'templates', 'p8_v3')
FILES = ('품질기준.md', '규칙예시.md', '디자인시스템_틀.md')   # 폴더와 zip에 들어가는 파일 전부
FORBID_EXT = ('.html', '.htm', '.js')                       # 2판 원칙: 완성 도구 · 코드 틀을 넣지 않는다
FORBID_TOP = ('.agents', '.claude', 'SKILL.md', 'references', 'memory')   # 참가자가 만들 것은 미리 넣지 않는다


def read_tpl(path):
    """템플릿 md를 줄바꿈 LF로 읽는다(다른 실습 md와 같게 저장하려고)."""
    with open(path, encoding='utf-8-sig', newline=None) as f:
        return f.read()


def check(out):
    """폴더에 FILES 세 개만 있고 스킬 자리(.agents · .claude · SKILL.md · references)와 html · js가 없는지 확인한다.
    (전체 파일 수, 세 파일 바이트 합계)를 돌려준다."""
    names = sorted(os.path.relpath(os.path.join(d, f), out).replace(os.sep, '/') for d, _, fs in os.walk(out) for f in fs)
    assert names == sorted(FILES), '파일이 세 개가 아니다: %s' % names
    top = os.listdir(out)
    bad_top = [n for n in top if n in FORBID_TOP]
    assert not bad_top, '미리 넣으면 안 되는 것이 있다: %s' % bad_top
    bad_ext = [n for n in names if n.lower().endswith(FORBID_EXT)]
    assert not bad_ext, 'html · js 파일이 들어 있다: %s' % bad_ext
    return len(names), sum(os.path.getsize(os.path.join(out, n)) for n in names)


def verify_zip(zip_path):
    """zip 항목이 폴더 이름 아래 세 파일뿐인지 확인하고 항목 수를 돌려준다."""
    with zipfile.ZipFile(zip_path) as z:
        names = z.namelist()
    want = sorted('%s/%s' % (os.path.basename(OUT), f) for f in FILES)
    assert sorted(names) == want, 'zip 항목이 세 파일이 아니다: %s' % names
    return len(names)


def main():
    assert os.path.dirname(OUT) == BASE
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)                              # 이전 판의 파일이 남지 않게 폴더째 다시 만든다
    for name in FILES:
        write_text(os.path.join(OUT, name), read_tpl(os.path.join(TPL, name)))
    n_files, total = check(OUT)
    print('P8 v3 파일 %d개 · 스킬 폴더 0개 · html/js 0개 · 에이전트 읽기 %.1f KB(%s)' % (n_files, total / 1024, ' + '.join(FILES)))


if __name__ == '__main__':
    # 실습 8만 다시 만든다: 폴더 → zip. gen_all.py는 다른 실습 폴더까지 지우므로 쓰지 않는다.
    main()
    from gen_all import zip_dir
    zip_dir(OUT, OUT + '.zip')
    n = verify_zip(OUT + '.zip')
    print('zip 실습8_강의교안스킬.zip  파일 %d개  %.1f KB  (md 세 파일만 확인)' % (n, os.path.getsize(OUT + '.zip') / 1024))
