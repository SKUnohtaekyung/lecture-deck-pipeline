# CHANGELOG — vibecoding-deck kit

## 0.7.0-wip — 대상 정의 정정·가독성 레이어 개명 (2026-07-19)
- **대상 정의 정정**: "40~50대 초보자" 표현을 커리큘럼 정본(`sessions/바이브코딩_커리큘럼_기준안.md` §4.1)에 맞춰 "코딩 경험이 없는 입문자 중심의 혼합군(연령·경험 수준 다양)"으로 저장소 전역 정정. 수치·CSS 값은 변경 없음, 근거 문장만 교체.
- **`legibility-40s.css` → `legibility.css` 개명**: 특정 연령대가 아니라 강의장 조건(뒷자리 판독·저조도 대비) 근거로 이름 정정. `git mv` + 참조 전 파일 갱신(`verify_deck.py` 포함).

## 0.6.0-wip — 아젠다 2열·브랜드 영문화·PART eyebrow 폐지 (2026-07-17)
- **이미지 생성 신뢰성·설명력 시스템**: 4상태 판정(`NO_IMAGE | IMAGE_EXPLANATORY | IMAGE_MNEMONIC | IMAGE_DECORATIVE_OPTIONAL`)과 재사용 우선 모드 게이트, 의미 브리프/크로마/native-alpha 프롬프트 분리, 중앙 registry·세션 manifest·expected figure 계약을 도입. `paper-cut-v1`은 투명 오브젝트로 제한하고 기존 디자인보드는 승인 전 생성 참조를 차단.
- **픽셀·배포 검증 강화**: 프로젝트 전용 크로마 래퍼(외곽 균일성·경계 접촉·키 충돌·부분 알파 RGB 복원·tight crop), PNG/해시/계보 검사기, 실제 `.viz-*`·`data-viz`만 세는 덱 검사, 누락·외부 의존·unresolved 슬롯이면 출력하지 않는 strict inline 배포를 추가. 합성 픽셀·prompt_only·장식 배치·`picture/srcset/CSS url()` 회귀를 포함한다.
- **이미지 공개 컴포넌트**: `figure.asset-slot`의 `hero/support/spot`, S02 `has-image` 안전 거터, 주석 스크린샷 22px 배지·캡션과 `figure/figcaption`을 공용 CSS·스타터·데모·아틀라스에 동기화. `cover-object`·`section-overlay`는 승인된 별도 템플릿 전까지 검증 실패.
- **아젠다 2열(an-2col)**: `.an-item` 4개 초과 시 크기 축소 대신 `.an-right.an-2col`로 2열 확장(deck.css §13 신규 4규칙 — `display:block`+`column-count:2` 자동 균형분배, `::after` 커넥터 억제, **상단 정렬=의도된 동작**). ≤4는 1열·미부여. 1주차 덱(6항목) 적용.
- **브랜드 영문화(라벨만)**: 헤더 `.s-brand`·`<title>`·팀명·표지 조직명 → **VIBECODING** (`letter-spacing -.01em→.02em`). 컨텍스트 앵커 치환으로 강의 콘텐츠 개념어 "바이브코딩"(정의 슬라이드 제목·아젠다 항목·간지 부제 등 1주차 6건+발표자노트 1건)은 **원문 유지**. 대상: 1주차 69 · 데모 32 · 스타터 5 · 카탈로그 13+9 · 아틀라스 정적 84+생성기 2곳(8행 head()·91행 표지) · logo.svg aria-label.
- **PART eyebrow 폐지**: 본문 `.s-eyebrow`의 "PART n · 파트명" 형식 삭제(헤더 `.s-part` 진행과 중복) — 1주차 44건 삭제+timing 동거 11건은 `.timing` 배지만 `.s-title` 위 독립 줄로 이설, 데모 11건 삭제. 의미형 eyebrow는 유지. 규칙 문서 교체(조립-리듬 §파트구조·§eyebrow).
- **verify_deck.py 확장**: 브랜드 한글 잔존 FAIL · 아젠다 개수-an-2col 정합 FAIL/WARN · eyebrow `PART n ·` 패턴 FAIL — 3종 네거티브 테스트로 검출 확인.
- **아틀라스**: 프로즌 CSS 통짜 재동기화(프로즌==deck.css 어서션) + s-brand 84건 치환. evals id=1 어서션 3줄 추가.
- **아젠다 v3 — 고정 제목·민트 바·확대·세로 균형(2026-07-17 후속)**: 제목=고정 멘트 **"오늘 배우게 될 것"** + 민트 pill 바 `.an-bar`(96×10) + 리드 1~2줄. `.an-num` 48→64px **플랫(그림자 제거)** · `.an-h` 21→30px **블루** · `.an-d` 17→22px(본문 하한) · 리드 19→24px · 제목 44→48px · 1열 커넥터 좌표 재계산(left31/top32/bottom-48). 코랄 스파크 `.an-spark`는 슬라이드 직속(left:452/top:122)→**`.an-left` 내부 첫 자식**으로 이동 — 고정 제목 "오" 좌상단 대각(left:-28/top:-36) 고정, 세로 중앙을 따라감(마크업 4곳: 1주차·데모·스타터·아틀라스). **2열 an-2col "상단 정렬=의도" 예외 폐지** — `.an-right.an-2col`·`.an-left`에 `height:fit-content`+`margin:auto 0`으로 좌·우 블록 모두 세로 중앙(공통 세로 균형 규칙 편입). verify 신규 3검사: 고정 제목 FAIL(`--parts 0` 카탈로그 제외)·`.an-bar` 부재 FAIL·`.an-num` box-shadow FAIL. 적용: 1주차 덱·데모·스타터·아틀라스(프로즌 CSS 재동기화+s03 마크업), 문서 동기화 6곳(SKILL·조립-리듬·치트시트·디자인시스템·MEMORY·evals).

## 0.5.0-wip — 박스 표면 규칙 + 넘버 행 수직 중앙 (2026-07-16)
- **박스 표면 규칙 신설**: 흰 캔버스 위 카드/박스의 "흰 fill + `--line` 근백색 보더" 조합 금지(사용자 리포트 — 박스 구분 안 됨). ① 의미 틴트 fill(`--blue-soft` 기본/`--mint-soft`/`--coral-soft`)+계열 보더 또는 ② 흰 fill+유색 보더(`--blue-line-strong`/`--mint-line`/`--coral-line`). deck.css 20곳+patterns.css 7곳+kit-additions 3파일 교체. 신규 토큰 `--mint-line:#C9EAE4`. `.card`=블루-소프트, `.card.surface`=블루-패널(뮤트), `.work-step`=민트-소프트(행동 문법), 촘촘한 그리드(rev-card·lc·metric 등)=흰 fill+블루-라인-스트롱.
- **넘버 행 수직 중앙**: `.work-step`·`.agenda-item` `align-items:start/flex-start`→`center`(원형 배지 대비 텍스트 중앙, `<b>`만 있어도). 고아 마진 픽스 `b:last-child{margin-bottom:0}`(deck.css+patterns.css 양쪽 — 로드 순서상 둘 다 필요). `.s03-slide .an-item`은 커넥터 좌표 전제라 제외.
- **`verify_deck.py` 확장**: 박스 표면 체크(kit CSS+덱 인라인, 방향 보더는 내부 구분선으로 합법) FAIL · `.work-step align-items:center` 계약 FAIL · `need_tokens`+`--mint-line`. 네거티브 테스트로 검출 확인.
- **아틀라스 재동기화**: `outputs/vibecoding-deck-layout-atlas.html` 프로즌 CSS 블록을 현재 deck.css로 통짜 교체(hug-center·concept-recap v2 드리프트 동시 해소).
- **문서**: 색시스템-v2-명세 §1b · 토큰-치트시트 · 디자인시스템 · SKILL.md · 조립-리듬-불변요소 · families 6곳(색 지시 문구) · AGENTS.md · MEMORY.md · evals.
- **데모 콘텐츠 동기화**: `데모_제작규칙.html`에 규칙 ④(박스 표면·수직 중앙 시연 슬라이드 B07b) 추가, ④⑤→⑤⑥ 재번호. 마크업 드리프트 정리 — 폐기된 "슬라이드 계획서·시각화 의도" 용어→콘텐츠 초안, 이미지 핸드오프 문구→generate_now/prompt_only 모드, B11 참조 표→현행 파일명(정보모양-taxonomy·by-shape·조립-리듬-불변요소·이미지-스크린샷-배포), KIT 버전 표기 v0.1→v0.5.

## 0.4.0-wip — 입력 형식 교체: 콘텐츠 초안 (2026-07-14)
- **공식 입력 템플릿 교체**: 옛 13라벨 `시각화 의도` 폼(`입력양식/슬라이드계획서템플릿.md`) 폐기 → **`입력양식/콘텐츠초안템플릿.md`**(교시별 `#·슬라이드 제목·본문 문구·비유·멘트` 4열 표 + 아이콘 범례). 폐기 폼은 `_dev/설계기록/폐기된-슬라이드계획서템플릿.md`로 이동. `시각화 의도` 입력 칸이 없어져 **정보 모양 판단을 스킬이 항상 전담**(taxonomy의 13라벨 조인표 제거, 12 정준 모양 유지).
- **아이콘 라우팅(고정)**: `💬`·`👀`→ HTML 주석(화면 비노출) · `🗣`→ 신규 `.hint-reveal`(접힘 힌트, `kit/styles/deck.css`). 이모지 마커 최종 HTML 누출 금지.
- **발표자 노트 HTML**: 멘트가 있으면 `kit/starter/presenter-notes-template.html` 복제해 `<덱>_발표자노트.html` 별도 산출.
- **`verify_deck.py` 확장**: 아이콘 마커(💬/🗣/👀) 누출 FAIL · `.hint-reveal` summary 부재 WARN.
- **문서**: `references/콘텐츠초안-입력형식.md` 신설(인식·컬럼 매핑·라우팅·PART 확인 절차). SKILL(9단계)·README·evals(콘텐츠초안·아이콘 라우팅 케이스) 갱신. 팀명 입력 제거, PART 매핑은 조립 직전 확인.

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
