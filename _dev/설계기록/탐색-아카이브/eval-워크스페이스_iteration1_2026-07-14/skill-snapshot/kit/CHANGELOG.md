# CHANGELOG — vibecoding-deck kit

## 0.3.0-wip — 완결성 패스 (skill-creator 2차 감사 후속)
- **코드 코어 `catalog.html`**: `kit/layouts`(8항목)·`kit/charts`(6개=4다이어그램+막대+매핑) 병렬 빌드+적대검증 → **브라우저 렌더 검증**(오버플로0·콘솔0·토큰·aria). 팬텀 참조·소실된 다이어그램 마크업 문제 해결.
- **회귀 스위트** `evals/evals.json`(현실 프롬프트 3 + 어서션) · `evals/trigger-eval.json`(트리거 쿼리 14).
- **배포 스크립트** `scripts/inline_deck.py`(CSS 인라인·이미지 base64 → 단일파일).
- **`verify_deck.py` 확장**: aria 라벨·색 남용(callout 3색↑) 검사 추가.
- **SKILL 보강**: 1단계 3진입(채운 폼 / 느슨한 브리프→초안·확인 / 단일 슬라이드), catalog.html 참조 정합, description 트리거 확장(발표자료·PPT→HTML·느슨브리프 등, 440자).
- **`CLAUDE.md`** 신설(개발 프로젝트 온보딩·3층 구조·테스트).

## 0.2.0-wip
- **판단 축**: `kit/guide/정보모양-taxonomy.md`(12 정준 정보모양 + 입력폼 13라벨 매핑) 신설 — 원칙 B의 척추.
- **규격·헌장**: `kit/guide/카탈로그-규격.md`(스키마·8 구도 패밀리·균형표·검증 체크리스트·no-default 헌장) · `kit/guide/토큰-치트시트.md`(657줄 deck.css 압축 + 세로예산·행높이·글자폭 계산식 + `--white`).
- **레이아웃 카탈로그**: `kit/layouts/families/*.md` **50개 항목**(8 패밀리, 균형 50/50, split 8% 캡·방향 분산) + `by-shape.md` 역인덱스 + `README.md`. 웹 리서치·소스 WebFetch 검증·deck.css 토큰 재표현.
- **차트/다이어그램 카탈로그**: `kit/charts/{charts-basic,charts-ratio,diagrams-relational,diagrams-process}.md` **21개 element**(code-viz·element_vs_slide 분리·a11y) + `by-shape.md` + `README.md`.
- **스타터 덱**: `kit/starter/deck-template.html`(자립·고정슬라이드+엔진, 브라우저 검증: 5슬라이드·오버플로0·에러0).
- **SKILL 본문 재작성**: 8단계 판단 게이트 워크플로우(정보 모양 분류 → 역인덱스 → 레이아웃+element 분리 선택 → 조립 → 검증).
- **references**: `조립-리듬-불변요소.md` · `이미지-스크린샷-배포.md`. `kit/screenshots/주석스크린샷.md`(데모 `.shot-annot` 승격).
- **하네스**: `.claude/settings.json`(권한 allowlist) · `.claude/agents/`(layout-researcher·catalog-builder·catalog-verifier). 멀티에이전트 병렬 빌드 + 적대 검증.
- 데모 `데모_제작규칙.html`의 `.code-chart`/`.code-diagram`/`.shot-annot`를 카탈로그로 승격 경로 확립.
- **코드 코어 시드** `kit/styles/patterns.css`: 검증된 완성 덱에서 수확한 레이아웃/element CSS(concentric·cycle·radial·tree + central-contrast·quad·numbered-stack·definition 등), raw hex→토큰 정리. deck.css·legibility 뒤 로드.
- **검증 스크립트** `scripts/verify_deck.py`(의존성 0): 슬라이드·파트전환=파트수·코드viz vs 이미지·구도 다양성·같은 구도 연속·토큰을 정적 채점.
- **P6 엔드투엔드 검증**: 1주차 자료로 with-skill 덱 조립 → baseline 대비 **다양성·코드시각화·구조 3축 모두 우세**(with-skill 6구도·연속0·코드viz4·이미지0·오버플로0 vs baseline 구도1종·같은구도3연속·part-divider0·네비없음). `verify_deck.py` 독립 재검증: with-skill PASS13/FAIL0, baseline FAIL8.
- **skill-creator 자가 감사 → 치명 결함 3건 수정**: 재현성 공백(patterns.css + 검증덱 지목) · 검증 반복작업(verify_deck.py) · 판단 게이트 미강제(SKILL 슬라이드 결정표).
- **구조 정리**: `_참고_likelion`·eval 산출(baseline/with-skill)·잉여 `.gitkeep`·미사용 커스텀 에이전트 삭제. 강의자료 → `_dev/강의자료/`, 설계기록 → `_dev/설계기록/`, `.claude/agent-memory/` 신설(누적 지식).

## 0.1.0-wip
- 자립형 패키지 골격 생성 (`template/`).
- likelion `deck.css` 컬러·기본 골격 **자립 복사**(657줄, import 아님).
- 40~50대 가독성 레이어 `legibility-40s.css` v0.1 추가.
- 입력 양식 `입력양식/슬라이드계획서템플릿.md` 배치.
- 강의 자료 `_개발참고/`로 정리 (설계·테스트용, 배포 제외).
- 적응용 참고본 `_참고_likelion/` 추가 (스타터·카탈로그·skill references·scripts).
- 새 대화 인수인계 `_시작하기_새대화.md` 작성.
- (예정) 헤더 로고·팀명 · 레이아웃 확장 · 코드차트 · 주석 스크린샷 · 스크립트 · SKILL 본문 · evals.
