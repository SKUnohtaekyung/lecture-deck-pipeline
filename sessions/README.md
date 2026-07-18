# sessions/ — 주차별 입력·산출

한 주차(세션)의 **입력 초안·원본 자료·산출 덱·발표자 노트**를 한 폴더에 모은다.
스킬 자산(`kit`·`scripts`·`references`)도 개발자료(`_dev`)도 아닌 **"작업물" 범주** — **배포 대상이 아니다**(스킬을 대상 프로젝트로 복사할 때 제외).

## 주차 폴더 구조
```
sessions/
  _template/              새 주차 시작 시 복사할 빈 골격
  1주차/
    초안.md               채워진 콘텐츠 초안 (입력양식/콘텐츠초안템플릿.md 형식)
    강의덱.초안/           편집본 조각(파트별) — shell.html + part-NN.html (+ order.txt 선택)
    강의덱.html            조립 미리보기(자동 재조립·외부링크 CSS) — 편집 중 통합본 확인용
    강의덱_배포.html        배포 단일본(CSS·이미지·폰트 전부 인라인 — 오프라인 자립)
    강의덱_발표자노트.html   산출 발표자 노트 (멘트 💬/👀/🗣가 있을 때만)
    자료/                 원본 리서치·인수인계·참고 자료
      이미지-에셋.json     슬라이드 이미지 판정·상태 정본
      이미지-프롬프트.md   사람용 프롬프트 대응 문서
      images/             QA를 통과한 실제 PNG
```

## 새 주차 시작 (루트에서)
```bash
cp -r sessions/_template "sessions/2주차"
cp "입력양식/콘텐츠초안템플릿.md" "sessions/2주차/초안.md"   # 빈 공식 템플릿을 초안으로
# → sessions/2주차/초안.md 를 채운 뒤 스킬에 "2주차 덱 만들어줘" 라고 요청
```

## 스킬 입출력 규약 (SKILL.md 1·5·7단계와 연결)
- **입력**: `sessions/N주차/초안.md`를 콘텐츠 초안으로 읽는다. 원본 근거가 필요하면 `sessions/N주차/자료/` 참고.
- **산출(2단계)**: 편집본(조각) → 배포본(단일 자립). 발표자 노트는 같은 폴더에 별도 산출.
  - **편집본** `강의덱.초안/`: 파트별 `shell.html`(head·고정 슬라이드·`<!-- ::PARTS:: -->` 마커·JS) + PART마다 `part-NN.html`. 대화하며 파트 단위로 고친다(조각이 대화형 수정에 빠르고 정확). 미리보기 통합본은 `python scripts/assemble_deck.py sessions/N주차/강의덱.초안`(`--watch`면 저장 시 자동 재조립) → `강의덱.html`(항상 최신). ⚠️ CSS는 `../../kit/styles/…` 상대경로(세션 폴더 2단계 깊이).
  - **배포본** `강의덱_배포.html`: `python scripts/build_release.py sessions/N주차/강의덱.초안` 한 커맨드 = 조립 → `verify_deck` → `inline_deck --offline`(CSS·이미지 인라인 + Pretendard 사용 글자 서브셋 `@font-face` 임베드) → `verify_distributable`(자립성 강제). 외부 의존이 하나라도 남으면 FAIL — 학생에게 이 파일 하나만 줘도 오프라인에서 다 보인다.
  - 조각 없이 단일 `강의덱.html`을 바로 편집하는 옛 방식도 유효하다(→ `inline_deck.py`로 배포). 단, 폰트 자립·자립성 강제는 `build_release.py` 경로에서 보장된다.
- **이미지 계약**: `자료/이미지-에셋.json`은 [`../references/이미지-에셋-manifest.schema.json`](../references/이미지-에셋-manifest.schema.json)을 따르는 상태 정본이다. `NO_IMAGE | IMAGE_EXPLANATORY | IMAGE_MNEMONIC | IMAGE_DECORATIVE_OPTIONAL` 판정, 재사용 Asset ID, 예상 파일, 생성 방식, QA 결과를 기록한다. `prompt_only`의 expected 슬롯에는 실제 `<img>`를 만들지 않는다.

## 팀 스킬 표준 산출 파일

파이프라인 순서는 `/리서치` → `/콘텐츠` → `/vibecoding-deck` → `/검토`(횡단)이며, 스키마·계약·호출 규약의 정본은 루트 [`skills/README.md`](../skills/README.md)다.

- **리서치 3파일 + 종합 요약본** → `자료/`: `N주차_콘텐츠리서치_결과.md` · `N주차_실습안_검증결과.md` · `N주차_결정요청사항.md` · `N주차_리서치_종합정리.md`(사람 읽기용 · 필수)
- **집필노트** → `자료/N주차_콘텐츠_집필노트.md` (`/콘텐츠`가 `초안.md`와 함께 산출)
- **검토보고** → `sessions/N주차/검토보고_YYYY-MM-DD.md` (주차 폴더 직하)

1주차는 규약 도입 前 산출물이라 파일명이 다를 수 있다(스킬은 내용 기준으로 인식).

## 1주차 (예외 — 산출물 폐기됨)
1주차 덱(`1주차_강의덱.html`, 루트 CSS 상대경로)·초안·집필노트·검토보고는 사용자 판정으로 삭제됐다(커밋 `2b6371f`). 그 덱을 예시나 재사용 원본으로 삼지 않는다. 1주차는 자료(`sessions/1주차/자료/`)만 유효하며 콘텐츠 단계부터 다시 만든다. 복원이 필요하면 `git show d89abfb:"경로"`.

2주차부터는 위 규약대로 덱까지 전부 세션 폴더 안에 산출한다.
