# -*- coding: utf-8 -*-
"""실습 자료 전체를 다시 만들고 zip 아홉 개(메인 과제 1 + 실습 8)로 묶는다.
실행: python gen_all.py   (필요: openpyxl · python-docx · python-pptx)"""
import os
import shutil
import zipfile

import gen_p1
import gen_p2
import gen_p3
import gen_p4
import gen_p5
import gen_p6
import gen_p7
import gen_p8
from gen_common import BASE, write_text

MAIN = os.path.join(BASE, '메인과제_AI습관점검')

PRD = """# PRD — AI 활용 습관 점검 앱

PRD는 「무엇을 만들지 적은 한 장짜리 문서」입니다. 에이전트는 이 문서를 읽고 앱을 만듭니다.
`1. 내가 정하는 것`을 채우고, 에이전트의 질문에 답하면서 `3` · `4`를 완성합니다.

## 1. 내가 정하는 것

- 누가 쓰나(대상):
- 어떤 장면의 습관을 점검하나(예: 보고서 쓸 때 · 자료 찾을 때 · 고객에게 답할 때):
- 결과를 본 사람이 무엇을 얻어 가나:
- 말투와 분위기(예: 담백하게 · 친근하게 · 격식 있게):

## 2. 정해진 것(수업 공통)

- 한 줄 설명: 문항 10개에 답하면 내 AI 활용 습관이 네 유형 가운데 어디에 가까운지 보여 주는 한 페이지 앱
- 질문 축 두 개
  - 시작: AI를 켜기 전에 내 생각을 먼저 두는가 → 높으면 「내 생각 먼저」, 낮으면 「AI 먼저」
  - 마무리: 받은 답을 쓰기 전에 확인하는가 → 높으면 「확인하고 씀」, 낮으면 「그대로 씀」
- 유형 네 개: 내 생각 먼저 · 확인하고 씀 / AI 먼저 · 확인하고 씀 / 내 생각 먼저 · 그대로 씀 / AI 먼저 · 그대로 씀
- 문항: 축마다 5개, 모두 10개. 「~한다」로 끝나는 한 문장이고 한 문항에 행동 하나
- 보기: 거의 없다 0 · 가끔 1 · 자주 2 · 거의 항상 3
- 판정: 축마다 점수 평균이 1.75 이상이면 높은 쪽
- 결과 글: 유형마다 요약(「~하는 편입니다」) + 이번 주에 해 볼 한 가지 + 이 유형에게 권하는 요청 한 줄
- 사람을 평가하지 않습니다. 「당신은 ~한 사람입니다」 대신 「~하는 편입니다」로 씁니다

## 3. 문항(에이전트와 대화하며 채웁니다)

### 시작 축
1.
2.
3.
4.
5.

### 마무리 축
1.
2.
3.
4.
5.

## 4. 유형별 결과 글(에이전트와 대화하며 채웁니다)

### 내 생각 먼저 · 확인하고 씀
- 요약:
- 이번 주 해 볼 한 가지:
- 권하는 요청 한 줄:

### AI 먼저 · 확인하고 씀
- 요약:
- 이번 주 해 볼 한 가지:
- 권하는 요청 한 줄:

### 내 생각 먼저 · 그대로 씀
- 요약:
- 이번 주 해 볼 한 가지:
- 권하는 요청 한 줄:

### AI 먼저 · 그대로 씀
- 요약:
- 이번 주 해 볼 한 가지:
- 권하는 요청 한 줄:

## 5. 화면 조건

- `index.html` 한 파일로 만듭니다. 더블클릭하면 브라우저에서 열리고 인터넷 연결 없이도 동작합니다
- 첫 화면(제목 · 한 줄 설명 · 시작 버튼) → 문항 화면(한 화면에 한 문항 · 진행 표시) → 결과 화면
- 결과 화면: 유형 이름 · 두 축 위의 내 위치 그림 · 요약 · 이번 주 해 볼 한 가지 · 권하는 요청 한 줄(복사 버튼) · 다시 하기 · 다른 유형 보기
- 색 · 글꼴 · 모서리 같은 모양은 `design.md`를 따릅니다
- 휴대폰 폭(375px)에서도 가로로 넘치지 않습니다
- 이름 · 연락처 같은 개인 정보는 받지 않고, 답은 어디에도 보내지 않습니다

## 6. 에이전트가 지킬 것

**인터뷰하는 순서**

1. 사용자가 「1. 내가 정하는 것」을 말하면, 들은 내용을 두세 문장으로 되짚어 맞는지 확인합니다. 비어 있으면 채우지 말고 묻습니다.
2. 부족한 것을 한 번에 하나씩 묻습니다. 답이 모호하면 꼬리 질문을 합니다(예: 「보고서」라고 하면 어떤 보고서인지, 그 가운데 AI를 가장 많이 쓰는 대목은 어디인지). 질문은 다섯 번 안팎이면 충분합니다.
3. 사용자가 답하기 어려워하면 선택지를 두세 개 보여 줍니다.
4. 다 물었으면 「이렇게 이해했고, prd.md를 이렇게 바꾸겠습니다」를 먼저 보여 주고, 승인을 받은 뒤에 고칩니다.
5. 문항과 결과 글은 초안을 두 가지씩 보여 주고 사용자가 고릅니다.
6. 사용자가 고르거나 고친 문장은 바꾸지 않습니다. 바꾸고 싶으면 먼저 이유를 말하고 허락을 받습니다.

**만들 때**

- 앱을 만들기 전에 계획을 먼저 보여 줍니다. 사용자가 승인하기 전에는 어떤 파일도 만들거나 고치지 않습니다.
- 다 만든 뒤에는 이 문서와 `design.md` 가운데 지키지 못한 것이 있는지 스스로 확인해 알려 줍니다.
"""


def zip_dir(folder, zip_path):
    if os.path.exists(zip_path):
        os.remove(zip_path)
    root = os.path.dirname(folder)
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
        for d, _, files in os.walk(folder):
            for f in sorted(files):
                p = os.path.join(d, f)
                z.write(p, os.path.relpath(p, root))


def main():
    for name in ('실습1_실행보드', '실습2_세컨드브레인', '실습3_응대센터', '실습4_주간대시보드',
                 '실습5_모션그래픽', '실습6_안내문', '실습7_퀴즈게임', '실습8_스킬만들기', '메인과제_AI습관점검'):
        p = os.path.join(BASE, name)
        if os.path.isdir(p):
            shutil.rmtree(p)
    write_text(os.path.join(MAIN, 'prd.md'), PRD)
    gen_p1.main()
    gen_p2.main()
    gen_p3.main()
    gen_p4.main()
    gen_p5.main()
    gen_p6.main()
    gen_p7.main()
    gen_p8.main()
    for name in sorted(os.listdir(BASE)):
        p = os.path.join(BASE, name)
        if os.path.isdir(p):
            zip_dir(p, p + '.zip')
            n = sum(len(f) for _, _, f in os.walk(p))
            print('zip %s.zip  파일 %d개  %.0f KB' % (name, n, os.path.getsize(p + '.zip') / 1024))


if __name__ == '__main__':
    main()
