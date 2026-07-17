# 강의덱.초안 — 편집본 조각(fragments)

대화하며 수정하는 작업본이다. 파트별 조각으로 나눠 국소 편집하고, 조립기가 통합 미리보기 `강의덱.html`을 만든다.

- `shell.html` — head·CSS 링크·발표 엔진 JS와 고정 슬라이드(표지·도입·아젠다·마무리), 그리고 파트가 들어갈 자리 `<!-- ::PARTS:: -->` 마커 한 개. 파트를 여기에 직접 넣지 않는다.
- `part-01.html`, `part-02.html`, … — 파트별 섹션 조각(`part-divider` + 본문 `<section class="slide">`). head/body/html 없이 섹션만.
- `order.txt`(선택) — 병합 순서. 없으면 파일명 오름차순(zero-pad: `part-01`, `part-02`, …). 있으면 한 줄에 파일명 하나씩 그 순서로 병합한다.
- 조립: `python scripts/assemble_deck.py sessions/N주차/강의덱.초안` → 상위 폴더에 `강의덱.html` 생성. `--watch`는 저장 시 자동 재조립, `--watch --livereload`는 미리보기 브라우저까지 3초 주기로 자동 새로고침.
- CSS 경로(`../../kit/styles/…`)는 출력 위치 `sessions/N주차/강의덱.html` 기준이다. shell을 다른 깊이로 옮기면 경로를 맞춘다.
