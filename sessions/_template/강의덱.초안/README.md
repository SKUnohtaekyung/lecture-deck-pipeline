# 강의덱.초안 — 편집본 조각(fragments)

대화하며 수정하는 작업본이다. 파트별 조각으로 나눠 국소 편집하고, 조립기가 통합 미리보기 `강의덱.html`을 만든다.

- `shell.html` — head·CSS 링크·발표 엔진 JS와 고정 슬라이드(표지·도입·아젠다·마무리), 그리고 파트가 들어갈 자리 `<!-- ::PARTS:: -->` 마커 한 개. 파트를 여기에 직접 넣지 않는다.
- `part-01.html`, `part-02.html`, … — 파트별 섹션 조각(`part-divider` + 본문 `<section class="slide">`). head/body/html 없이 섹션만.
- `order.txt`(선택) — 병합 순서. 없으면 파일명 오름차순(zero-pad: `part-01`, `part-02`, …). 있으면 한 줄에 파일명 하나씩 그 순서로 병합한다.
- 조립: `python scripts/assemble_deck.py courses/<과목>/sessions/N주차/강의덱.초안` → 상위 폴더에 `강의덱.html` 생성. `--watch`는 저장 시 자동 재조립, `--watch --livereload`는 미리보기 브라우저까지 3초 주기로 자동 새로고침.
- CSS 경로(`../../../../kit/styles/…`)는 **출력 위치 `courses/<과목>/sessions/N주차/강의덱.html` 기준 4단계**다. shell을 다른 깊이로 옮기면 경로를 맞춘다.
  - ⚠️ **경로가 틀려도 정적 검증은 전부 PASS한다.** CSS 404는 브라우저에서만 드러나고(전 슬라이드 동시 표시·로고 0×0), 유일한 정적 신호는 `verify_deck.py`의 「글래스 내비게이션 토큰/효과 없음」 FAIL이다 — 그 FAIL을 「기존 결함」으로 넘기지 말 것. 조립 후 로컬 http로 열어 `document.styleSheets.length`와 «보이는 슬라이드가 1장인지»를 확인한다.
