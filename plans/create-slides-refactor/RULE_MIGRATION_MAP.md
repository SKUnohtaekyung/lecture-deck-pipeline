# RULE MIGRATION MAP — CSR-2026-07 (TASK-P4-001)

루트 `SKILL.md`(개편 전 180줄)의 **모든 규칙성 문장**과 §9 규칙 인벤토리 R-* 전량을 행으로 등재한다.
이 표가 P4의 유일한 대조 기준이다. **여기 없는 문장을 임의로 삭제하지 않는다.**

- 처리 분류: `Core 잔류`(신 SKILL.md에 남음) / `phases-0N 이동`(전사) / `정본 참조화`(본문 삭제 + 규칙 ID 참조로 대체) / `MEMORY 승격` / `삭제`
- 개편 전 원문 회수: `git show refactor-p4-start:SKILL.md`
- 대조 상태: `OK`=신위치에서 문구 확인됨 / `대기`=P4-002·003 수행 전

## A. §0 불변 요소 — 엔진·브랜드 계약 (SKILL.md L34~42)

| # | 규칙 ID | 원문 위치(앵커) | 처리 | 신위치 | 대조 |
|---|---|---|---|---|---|
| A1 | R-FIX-01 | `고정 슬라이드의 불변 범위` — 표지·도입·아젠다·마무리의 엔진 hook·V 로고·`VIBECODING` 브랜드 유지 | Core 잔류(요지 1줄) + phases-04 이동(상세) | SKILL Core ⑤ · `references/phases/04-조립.md` | 대기 |
| A2 | R-FIX-01a | `스타터의 텍스트·구도·장식은 기본값이지 불변 구조가 아니다` — 사용자 명시 시 안전영역·가독성·브랜드·엔진 hook 범위에서 변경 | phases-04 이동 | phases/04 | 대기 |
| A3 | R-PART-01 | `파트전환(part-divider)은 헤더 없이 진행 도트(.pd-dot)와 파트 타이틀 hook을 유지` | Core 잔류(요지) + phases-04 | Core ⑤ · phases/04 | 대기 |
| A4 | R-NAV-01 | `하단 네비게이션 바`~`poke()`를 넣지 않는다` — Liquid Glass·`--glass-thick`·G/Esc/B/F 단축키·마우스 이동 시에만 리모컨 노출 | phases-04 이동(전문) | phases/04 | 대기 |
| A5 | **R-PART-01** | `모든 파트는 파트 전환(part-divider) 슬라이드로 시작 — PART 1 포함` · `파트 수 = divider 수` | **Core 잔류** | Core ⑤ | 대기 |
| A6 | **R-PART-02** | `스타터 JS가 divider의 DOM 순서를 읽어 진행 도트, PART n / N, 지오메트릭 큐브를 자동 생성` · 큐브 수 = 현재 파트 번호 · `파트 SVG·도트·분모를 조각 파일에 하드코딩하지 않는다` | phases-04 이동 + P6 검증 신설 | phases/04 · `verify_deck.py` 신규 검사 | 대기 |
| A7 | R-TERM-02 | (P4-003 확정 문안 전사) 파트 도입 도형의 정본 용어는 **지오메트릭 큐브** — `정육각형`·`아이소 큐브` 표기 금지 | phases-04 이동(계획 문안 전사) | phases/04 | 대기 |
| A8 | R-IMG-01 | `이미지 판정·모드 게이트` — 판정 순서 5단계 + 4상태(`NO_IMAGE`/`IMAGE_EXPLANATORY`/`IMAGE_MNEMONIC`/`IMAGE_DECORATIVE_OPTIONAL`) | Core 잔류(4상태·게이트 순서 요약만) + phases-06 이동(상세) | Core ⑤ · phases/06 | 대기 |
| A9 | R-IMG-01a | `승인 에셋 재사용만으로 충족되거나 신규 작업이 0장이면 질문하지 않는다` · `generate_now 권한이 주어진 것으로 보고 재질문하지 않는다` · 모호할 때만 1회 질문 | phases-06 이동 | phases/06 | 대기 |
| A10 | R-COLOR-01·03 | `템플릿 규칙(v2.1)` — navy 금지 · 그라데이션 금지 · 번호배지 민트 3종 | **정본 참조화** | `kit/guide/디자인시스템.md`(R-COLOR-01·03) · Core ④에 금지항으로 요지 | 대기 |
| A11 | R-HEAD-01 | `헤더 파트진행`(`.s-part` JS 주입) · `하단 페이지네이션`(`.s-pageno` JS 주입, 표지·마무리 제외) | phases-04 이동 | phases/04 | 대기 |
| A12 | — | `운영 정본은 shipped kit/guide/디자인시스템.md·토큰-치트시트.md` | Core 잔류(정본 우선순위) | Core ③ | 대기 |
| A13 | — | `스타터를 복사하면 1·2가 자동 보존된다. 3은 조립 때 파트 수만큼 배치. 검증(8단계)에서 확인.` | phases-04 이동 | phases/04 | 대기 |

## B. 개요·소유권 (SKILL.md L15~30)

| # | 규칙 ID | 원문 위치(앵커) | 처리 | 신위치 | 대조 |
|---|---|---|---|---|---|
| B1 | — | 스킬 정의: 콘텐츠 초안 → 단일 HTML 웹덱 · 1280×720 · 방향키 · `F` · 발표 메뉴 | Core 잔류(요지) | Core 서두 | 대기 |
| B2 | **R-OWN-01** | `새 덱의 콘텐츠·슬라이드 제목·멘트는 초안이 / 정보 모양 판단·레이아웃·시각화 구현은 스킬이 맡는다` | **Core 잔류** | Core ④ | 대기 |
| B3 | **R-OWN-01a** | `사용자가 기존 덱의 문구·구조·레이아웃 수정을 명시하면 그 지시가 초안 소유권보다 우선` | **Core 잔류** | Core ③·④ | 대기 |
| B4 | R-NOTE-01 | `강사 멘트(💬/👀/🗣)가 있으면 학생 덱에 노출하지 않고 별도 발표자 노트 HTML에만 산출` | Core 잔류(요지) + phases-07 | Core ② · phases/07 | 대기 |
| B5 | — | `킷 구조 (자립 — 외부 import 0)` 트리 10줄 | phases 서두 분산 + Core ⑤ 포인터 | Core ⑤ · 각 phases 서두 | 대기 |

## C. read-path (SKILL.md L48~55) — 조건부 로드로 전환

| # | 규칙 ID | 원문 위치(앵커) | 처리 | 신위치 | 대조 |
|---|---|---|---|---|---|
| C1 | R-EDU-01 | `가장 먼저: kit/guide/교육원칙-요약.md` — 대상 정의·언어 범위·교육 원칙 | Core 잔류(포인터) | Core ⑤ 1단계 | 대기 |
| C2 | R-EDU-01a | `sessions/바이브코딩_커리큘럼_기준안.md이 정본이며, 요약본과 충돌하면 언제나 정본이 이긴다` · 정본 변경 시 요약본 동반 수정 · 배포 자립성 때문에 read-path 필수로 걸지 않음 | Core 잔류 | Core ③ | 대기 |
| C3 | — | `항상` 목록 5파일(콘텐츠초안-입력형식·정보모양-taxonomy·디자인시스템·토큰-치트시트·조립-리듬·이미지-디렉션) | **조건부 로드로 재편** — 단계별 phases 서두로 분산 | phases/01·02·03·04·06 서두 | 대기 |
| C4 | — | `후보·스펙` / `마크업 복사` / `화면조작이면` / `조건부(멘트)` | phases-03·05·06·07 이동 | 각 phases 서두 | 대기 |
| C5 | **LOAD-002** | `references/이미지-디렉션-프롬프트.md`(283줄) 상시 로드 | Core에는 요약만 · 본문 진입은 phases/06 | Core ⑤ · phases/06 | 대기 |

## D. 1단계 입력 파악 (SKILL.md L57~67)

| # | 규칙 ID | 원문 위치(앵커) | 처리 | 신위치 | 대조 |
|---|---|---|---|---|---|
| D1 | **R-IN-01** | `세션 폴더 규약: sessions/N주차/초안.md` → **DEC-05 반영**: `N주차_초안.md` 우선·`초안.md` 레거시 폴백 · 산출도 같은 폴더 | **Core 잔류(입력 계약)** | Core ① | 대기 |
| D2 | **R-OWN-01b** | `우선순위: 현재 사용자 지시 → 콘텐츠 초안 → 원본 자료 → 이 스킬의 판단 규칙` · `접근성·1280×720 오버플로·엔진·브랜드 계약은 항상 지킨다` | **Core 잔류** | Core ③ | 대기 |
| D3 | R-IN-02 | `콘텐츠 초안이면(공식 입력)` 4열 표 + 아이콘 범례 · 고정 절차는 `references/콘텐츠초안-입력형식.md` | Core 잔류(요지) + phases-01 | Core ① · phases/01 | 대기 |
| D4 | **R-OWN-01c** | `제목·본문은 콘텐츠팀 소유라 임의 재작성하지 않는다` · 장수는 사용자 계획 · 수용량 초과 시 원인·선택지 제시 | **Core 잔류** | Core ④ | 대기 |
| D5 | **R-KB-01** | `조건부 KB 회수(초안 행에 <!-- refs: C-… -->가 있을 때만)` — 해당 청크만 grep 회수 · **개념KB 통째 Read 금지** · 본문 재작성에 쓰지 않음 · 충돌 시 보고 | **Core 잔류(요지)** + phases-01(상세) | Core ① · phases/01 | 대기 |
| D6 | R-KB-02 | `회수한 청크가 범위:인접이면 본문 슬라이드로 만들지 않는다` — 발표자 노트로만 | phases-01 이동 | phases/01 | 대기 |
| D7 | **R-ICON-01** | `아이콘 라우팅(고정)`: 💬·👀·🗣 학생 덱 표시 금지 · `.hint-reveal`·`강사 힌트`·`막힐 때만 보기`·`완성 예시 보기` 0 · 이모지 문자도 0(verify FAIL) | **Core 잔류(금지항)** + phases-01 | Core ④ · phases/01 | 대기 |
| D8 | — | `정보 모양은 이 형식에 지정 칸이 없다 → 모든 슬라이드를 스킬이 직접 추론(§2)` | phases-01·02 이동 | phases/01·02 | 대기 |
| D9 | — | `교시→PART 매핑`은 이미 있으면 그대로 · 모호한 경계만 1회 확인 | phases-01 이동 | phases/01 | 대기 |
| D10 | R-IN-03 | `폼 없이 브리프·원자료만 오면` → 슬라이드 계획 초안 먼저 | Core 잔류(3진입 중 하나) + phases-01 | Core ① · phases/01 | 대기 |
| D11 | R-IN-04 | `한 장만 / 기존 덱에 추가면` → 2~5단계만 | Core 잔류(3진입 중 하나) + phases-01 | Core ① · phases/01 | 대기 |
| D12 | **R-OWN-02** | (신규 경계 명문화 — CONTENT-001) 비유-정의 순서 등 **콘텐츠 계층 문제는 덱이 고치지 않고 보고한다** | Core 잔류 + phases-01 | Core ④ · phases/01 | 대기 |

## E. 2·3·4단계 판단 게이트 (SKILL.md L69~94)

| # | 규칙 ID | 원문 위치(앵커) | 처리 | 신위치 | 대조 |
|---|---|---|---|---|---|
| E1 | **R-LAYOUT-01** | `레이아웃을 고르기 전에 "이 정보가 무슨 모양이냐"를 먼저 정한다` · 12 정준 모양 분류 | **Core 잔류(게이트 지도)** + phases-02 | Core ⑤ · phases/02 | 대기 |
| E2 | **R-LAYOUT-01a** | `이 단계를 건너뛰고 즉흥적으로 고르지 않는다` · `"좌 글/우 시각"은 기본값이 아니다` | **Core 잔류** | Core ④·⑤ | 대기 |
| E3 | R-LAYOUT-01b | 3단계 역인덱스: `kit/layouts/by-shape.md` 후보 · numeric·structure·containment·flow·mapping·comparison이면 `kit/charts/by-shape.md`도 · **concept+소스코드면 `E-code`** | phases-03 이동 | phases/03 | 대기 |
| E4 | R-DEC-01 | `조립 전에 슬라이드 결정표를 먼저 쓴다` + 6열 표 형식(#·정보 모양·구도 패밀리·element·이미지 판정·직전과 다른 패밀리) | phases-03 이동 | phases/03 | 대기 |
| E5 | **R-LAYOUT-02** | `직전 콘텐츠 슬라이드와 같은 구도 패밀리를 피한다` · `split(좌우 비대칭)은 희소하게, 연속 금지` | **Core 잔류** | Core ④·⑤ | 대기 |
| E6 | R-LAYOUT-02a | `레이아웃 ≠ 다이어그램` — element를 골라 레이아웃에 얹는다(예: containment → `L-ct-concentric` + `D-concentric`) | phases-03 이동 | phases/03 | 대기 |
| E7 | R-LAYOUT-02b | 선택 검증: `data_shape`·`when_to_use`·`when_to_avoid` | phases-03 이동 | phases/03 | 대기 |
| E8 | R-NOTE-01a | `🗣가 있던 슬라이드는 결정표에 발표자 노트 메모` · 결정표는 내부 기준 · 모호한 선택만 확인 | phases-03 이동 | phases/03 | 대기 |
| E9 | R-IMG-01b | 이미지 4상태 판정 시점 · 장식 이미지는 사용자 명시 시에만 · **파트당 최대 1장·비연속·차트/다이어그램과 동시 사용 금지** · `registry.json` approved 우선 검색 | phases-06 이동(+phases-03에서 판정 시점 1줄) | phases/06 · phases/03 | 대기 |
| E10 | R-IMG-01c | IMAGE_MODE 2선택지 질문 문안(`1. 이미지 바로 생성 / 2. 프롬프트만 제작`) | phases-06 이동 | phases/06 | 대기 |
| E11 | R-IMG-01d | 모드 답 대기 중에도 이미지 비의존 조립·점검 계속 · 0장이거나 자율 권한이면 질문 없이 진행 + 판정·Asset ID·`NO_IMAGE` 이유를 결정표와 `자료/이미지-에셋.json`에 기록 | phases-06 이동 | phases/06 | 대기 |
| E12 | **R-IMG-03** | (신규) 저정보 슬라이드는 좌설명/우이미지 구성 우선 검토 — **빈 공간 채우기용 금지는 유지** | phases-03 신설 | phases/03 | 대기 |

## F. 5단계 조립 (SKILL.md L96~111)

| # | 규칙 ID | 원문 위치(앵커) | 처리 | 신위치 | 대조 |
|---|---|---|---|---|---|
| F1 | R-ASM-01 | `kit/starter/deck-template.html` 기반 · `patterns.css`를 deck.css·legibility **뒤에** 로드 | phases-04 이동 | phases/04 | 대기 |
| F2 | R-FIX-01b | 고정 슬라이드 조립 시 엔진 hook·브랜드 보존 · `.dv-hero`·`.pd-dots`·`.pd-eyebrow`는 **빈 hook** · `hydratePartDivider()`가 자동 반영 | phases-04 이동 | phases/04 | 대기 |
| F3 | R-ASM-02 | 본문 슬라이드: 카탈로그 코어 우선 검토하되 **제한되면 독립 구도 설계 가능**(토큰·가독성·안전영역 계약 준수) · 정보량 부족 시 빈 카드 대신 GUI·다이어그램·캡처·이미지로 보강 · **코드 시각화는 유력한 선택지이지 절대 우선 규칙이 아니다** | phases-05 이동 | phases/05 | 대기 |
| F4 | R-ASM-03 | `카탈로그는 "코어 + 변형" 설계` — 레이아웃 54·element 23은 추천 어휘집, 마크업 코어는 **레이아웃 12·차트 8** · 없으면 가까운 코어 변형 · 근거 1줄 결정표 | phases-05 이동 | phases/05 | 대기 |
| F5 | **R-LAYOUT-03** | ⚠️ `환류 규칙(재사용 가능한 신규 구도)` — 일반 패턴이면 `catalog.html`·`patterns.css`에 환류 후 `verify_kit.py` · 맥락 의존 구도는 세션 CSS에 좁게 스코프 | phases-05 이동 + **카탈로그-규격.md 승격**(family 레지스트리) | phases/05 · `kit/guide/카탈로그-규격.md` | 대기 |
| F6 | R-COLOR-01·R-TYPE-01·R-TYPE-03 | `토큰만 사용` · `가독성 하한(본문 22px·표 17px)` · `색은 문법` · `오버플로 0(세로예산 548px·행높이 계산식)` | **정본 참조화** (수치는 R-TYPE-01·03 표가 정본) | 디자인시스템·토큰-치트시트 · Core ④ 요지 | 대기 |
| F7 | R-ICON-01a | 조립 시 아이콘 라우팅 반영(중복 서술) | **정본 참조화**(D7과 중복) | Core ④ | 대기 |
| F8 | R-TEXT-01 | `채울 수 있는 레이아웃은 본문 안전 영역을 적극 사용` · centered·full-bleed는 의도적 여백 유지 | phases-04 이동 | phases/04 | 대기 |
| F9 | R-IMG-02a | 이미지 슬롯 계약: `<figure class="asset-slot asset-slot--hero" data-image-purpose="explanatory">` · 역할은 `hero|support|spot`뿐 · 설명·기억 이미지는 한국어 `alt` 필수 · 장식은 `alt="" aria-hidden="true"` · `prompt_only`는 `data-image-state="expected"`+`data-expected-src` · `cover-object`·`section-overlay` 사용 금지 | phases-06 이동 | phases/06 | 대기 |
| F10 | **R-IMG-04** | ⚠️ `이미지 잘림·겹침 0(확대·밀도·구도 취향보다 우선)` — **잘림**(figure vs img `getBoundingClientRect().height` 실측 · `overflow:hidden`으로 가리는 것은 해결 아님) | **Core 잔류(금지항)** + phases-04 상세 | Core ④ · phases/04 | 대기 |
| F11 | R-IMG-04a | **겹침**: 이미지 경계 상자가 형제 텍스트와 1px도 교차 금지 · 안전영역 좌우 64–1216·하단 ≤666 · 확대와 겹침 충돌 시 **언제나 겹침 0** | Core 잔류(요지) + phases-04 | Core ④ · phases/04 | 대기 |
| F12 | R-IMG-04b | `object-fit:contain` 레터박스 함정 — 박스 높이를 키우면 빈 여백만 커짐 · `naturalWidth/naturalHeight` 비율 선비교 | phases-04 이동 | phases/04 | 대기 |
| F13 | — | `조립 문법·리듬·불변요소 상세: references/조립-리듬-불변요소.md` | Core 잔류(포인터) | Core ⑤ · phases/04 | 대기 |
| F14 | **R-OUT-01** | `산출 위치·2단계 구조` — 편집본은 `강의덱.초안/`에 조각(`shell.html`+`part-NN.html`) · `assemble_deck.py` → `강의덱.html` · kit CSS는 `../../kit/styles/…` · 최종본은 9단계 | **Core 잔류(출력 계약)** | Core ② | 대기 |

## G. 6·7단계 이미지·노트 (SKILL.md L113~122)

| # | 규칙 ID | 원문 위치(앵커) | 처리 | 신위치 | 대조 |
|---|---|---|---|---|---|
| G1 | R-IMG-01e | 이미지 정본 3계층: 중앙 승인 `kit/images/paper-cut-v1/registry.json` · 세션 실행 `자료/이미지-에셋.json` · 사람용 `이미지-프롬프트.md` · **상세 계약을 이 문서나 어댑터에 복제하지 않는다** | phases-06 이동 | phases/06 | 대기 |
| G2 | R-IMG-05 | 기본 표지는 스타터 큐브 구도 · 생성 이미지는 S02부터 · `paper-cut-v1`은 투명 오브젝트 전용 | phases-06 이동 | phases/06 | 대기 |
| G3 | R-IMG-06 | `generate_now` 절차: 에셋별 개별 호출 · built-in은 균일 마젠타 크로마 · native-alpha는 진짜 투명 · **의미·스타일 교정 1회·알파 재시도 1회** · 초과 시 설명·기억은 중단·보고, 장식은 반려 기록 후 생략 · 통과본만 `자료/images/`에 저장·등록 | phases-06 이동 | phases/06 | 대기 |
| G4 | R-IMG-07 | `prompt_only` 절차: `이미지-프롬프트.md`·`이미지-에셋.json` 기록 · `<img src>` 두지 않음 · **배포는 unresolved 설명·기억 슬롯 때문에 실패해야 한다** | phases-06 이동 | phases/06 | 대기 |
| G5 | R-SHOT-01 | `screen-operation`은 이미지 모드와 별개 — 실제 화면은 사용자 캡처, overlay는 `kit/screenshots/` 주석 스크린샷 킷 | phases-06 이동 | phases/06 | 대기 |
| G6 | — | 참고: 💬/🗣/👀 라우팅은 1·5단계 소관 | phases-06 이동(1줄) | phases/06 | 대기 |
| G7 | **R-NOTE-01b** | 발표자 노트 산출: 멘트 1개라도 있으면 `presenter-notes-template.html` 복제 → `<덱이름>_발표자노트.html` · 슬라이드 순서대로 번호·제목+멘트 · **`🗣`는 펼친 상태**(수강생 화면과 반대) · 같은 폴더 | Core 잔류(요지) + phases-07 이동 | Core ② · phases/07 | 대기 |
| G8 | **R-NOTE-01c** | (MEMORY 승격) `pn-no`는 보이는 페이지 번호와 일치 · 구성 변경 시 삽입 지점 이후 재번호 · **재번호는 스크립트로 일괄 처리**(손으로 하면 충돌) · 끝나면 덱 `data-slide` ↔ 노트 `pn-no` 기계 대조 | **MEMORY 승격 → phases-07** | phases/07 | 대기 |

## H. 8·9단계 검증·배포 (SKILL.md L124~133)

| # | 규칙 ID | 원문 위치(앵커) | 처리 | 신위치 | 대조 |
|---|---|---|---|---|---|
| H1 | **R-VERIFY-01** | ① 정적 검증: `python scripts/verify_deck.py <덱>.html --parts N` 항목 나열 | **Core 잔류(필수 게이트)** + phases-08 | Core ⑥ · phases/08 | 대기 |
| H2 | **R-VERIFY-01a** | ② 브라우저 전수 검사(스크립트가 못 재는 것): 로컬 http · **모든 슬라이드**를 1280×720과 실제 크기에서 순회 · descendant rect 캔버스 내 · 형제 교차 0 · `object-fit:contain`·crop · `scrollWidth/Height ≤ client` · 콘솔 0 · Pretendard · 본문 22px · 표준 로고 · 검정 터미널 본문 `var(--white)` · `.hint-reveal` 0 · **박스 패딩 과다 확인** | **Core 잔류(요지)** + phases-08 이동(전문) | Core ⑥ · phases/08 | 대기 |
| H3 | R-VERIFY-01b | `스크린샷은 정적이라 불안정·느림 → 측정 우선, 스크린샷은 증빙 최소` | phases-08 이동 | phases/08 | 대기 |
| H4 | R-VERIFY-01c | (MEMORY 승격) `getBoundingClientRect()` 값을 `--scale`로 나눠 덱 좌표 환산 · 반환에 scale 동봉해 1인지 확인 | **MEMORY 승격 → phases-08** | phases/08 · `measure_render.js` | 대기 |
| H5 | R-VERIFY-01d | (MEMORY 승격) **래퍼를 빼고 말단 요소만 잰다** — 자식 있고 자기 텍스트 없는 노드 제외, 텍스트 노드와 `IMG`만 판정 | **MEMORY 승격 → phases-08** | phases/08 · `measure_render.js` | 대기 |
| H6 | R-VERIFY-01e | (MEMORY 승격) 회귀 여부는 기준선 대조로만 판단 | **MEMORY 승격 → phases-08** | phases/08 | 대기 |
| H7 | **R-DIST-01** | 9단계 배포: `build_release.py` 한 커맨드 = 조립→verify_deck→inline_deck --offline→verify_distributable | **Core 잔류** | Core ⑥ · phases/09 | 대기 |
| H8 | **R-DIST-01a** | **강제 게이트**: 외부 `<link/script href=http>` 0 · 모든 `src`/`url()` `data:` · 임베드 `@font-face` 존재 + Pretendard CDN 부재 · unresolved 설명·기억 슬롯 0 · **fail-closed** | **Core 잔류** | Core ⑥ · phases/09 | 대기 |
| H9 | R-DIST-01b | 빌드된 배포본은 손대지 말고 **조각을 고쳐 재빌드**(폰트 서브셋 재계산) | Core 잔류(금지항) + phases-09 | Core ④ · phases/09 | 대기 |

## I. 참조 지도 표 (SKILL.md L137~159)

| # | 규칙 ID | 원문 위치(앵커) | 처리 | 신위치 | 대조 |
|---|---|---|---|---|---|
| I1 | — | 20행 참조 지도 표(파일 ↔ 언제) | **Core ⑤ 게이트 지도로 압축**(각 단계 1줄 + phases 포인터) + 각 phases 서두에 해당 행 전사 | Core ⑤ · phases/01~09 | 대기 |

## J. 핵심 규칙 요약 20항 (SKILL.md L161~180)

| # | 규칙 ID | 원문 위치(앵커) | 처리 | 신위치 | 대조 |
|---|---|---|---|---|---|
| J1 | R-DENS-01 | `밀도: 저밀도 최소주의 폐기 → 정보 단위 3~6개` · 정본은 `skills/콘텐츠/SKILL.md` **§0-6**(CONFLICT-006 해소) | phases-04 이동 | phases/04 | 대기 |
| J2 | R-DENS-01a | ⚠️ `screen-operation 예외` — 한 슬라이드 = 조작 단계 1개 · 밀도 하한 미적용 · 단계 3개면 3장 · **단계와 지점 혼동 금지**(지점 1~3) | phases-04 이동 | phases/04 | 대기 |
| J3 | **R-LAYOUT-02c** | `no-default: 모든 레이아웃·element는 동급. 정보 모양이 고른다. 좌우분할은 희소·비연속` | **Core 잔류** | Core ④ | 대기 |
| J4 | **R-EMPH-01** | `색은 의미(장식 아님)` — 구조는 `--blue` · **강조어는 민트 계열이 기본** · `.hl` 절제 · 한 화면 파랑 도배 금지 · `--blue-soft`=배경 · `--periwinkle`=비강조 | **정본 참조화** (P3-003에서 선택표로 확정) | `kit/guide/디자인시스템.md` R-EMPH-01 | 대기 |
| J5 | R-BOX-01 | `세로 균형(하단 여백 금지)` — 위로 몰고 아래 비우지 않음 · `.center-msg`·`.s-full.fill`·`.s-full.solo` · 오버플로 0과 동시 | phases-04 이동 | phases/04 | 대기 |
| J6 | R-BOX-01a | ⚠️ **박스 안쪽에도 같은 규칙** — `justify-content:space-between/space-evenly`+flex column으로 균등하게 늘림 · 나란한 박스는 전부 같은 방식 | phases-04 이동 | phases/04 | 대기 |
| J7 | **R-TYPE-03a** | `페이지번호·푸터 영역 침범 0` — `.s-pageno`(right:56/bottom:22)·`.s-foot` · **콘텐츠 하단 ≤666px** · 폰트를 줄이지 말고 행·열·이미지·레이아웃을 다시 잡음 · **`overflow:hidden`으로 가려 통과 금지**, `getBoundingClientRect().bottom` 실측 | **Core 잔류(금지항)** + 수치 정본은 R-TYPE-03 | Core ④ · 토큰-치트시트 | 대기 |
| J8 | R-BOX-02 | `박스 크기 = 정보량 비례` · 격자 편차 크면 bento·가변 행높이 | phases-04 이동 | phases/04 | 대기 |
| J9 | R-BOX-02a | ⚠️ **패딩 절대 기준** — 세로 패딩 합이 콘텐츠 높이의 1/3 초과면 과함 · 1~2줄 12~14px, 3줄↑ 16~20px · **만드는 순간에 자문** · 실측 사례(`.concept-bottom` 41%→33%) | phases-04 이동 | phases/04 | 대기 |
| J10 | R-BOX-03 | ⚠️ **폭 절대 기준(대칭 규칙)** — 짧은 단독 박스는 `.hug-center` · 예외: 시퀀스 칩·짝 격자 · `flex-direction:column`이면 `align-self`도 변경 · 실측 사례(76% 빈 공간 → 282px) | phases-04 이동 | phases/04 | 대기 |
| J11 | **R-TEXT-02** | `줄바꿈은 문맥 경계` — 수동 `<br>`은 구·절 경계에서(조사·어미가 앞줄에 매달리지 않게) · 양쪽 줄길이 균형 | phases-04 이동 + P6 br 린트 신설 | phases/04 · `verify_deck.py` WARN | 대기 |
| J12 | **R-COLOR-01·02** | `navy 금지 · 그라데이션 금지 · 민트·코랄 fill 위 흰 글자 금지` · **`.hl-mint-mark` 예외** | **정본 참조화** | 디자인시스템 R-COLOR-01·02 · Core ④ 요지 | 대기 |
| J13 | **R-COLOR-03** | `번호배지 민트 = .num-circle·.work-step .n·.pd-dot.is-active만` | **정본 참조화** | 디자인시스템 R-COLOR-03 | 대기 |
| J14 | **R-COLOR-04** | `박스 표면은 흰색-온-흰색 금지` + 2택 + `--line` 단독 금지 + 예외(코드/터미널·주석 스크린샷·`.pd-dot`·표) | **정본 참조화** | 디자인시스템 R-COLOR-04 · Core ④ 요지 | 대기 |
| J15 | R-BOX-04 | `넘버 행 수직 중앙` — `.work-step`·`.agenda-item` `align-items:center`(verify 강제) | **정본 참조화** | `references/조립-리듬-불변요소.md` | 대기 |
| J16 | R-HEAD-01a | `헤더 파트진행`·`하단 페이지네이션` 자동 주입 · 운영 정본 지목 | **정본 참조화** | 디자인시스템 · phases/04 | 대기 |
| J17 | R-CONN-01 | `가운데 커넥터` — 파란 `→`(흐름)·`⊃`(포함)·`≠`(대비)·`↓`(검증) | **정본 참조화**(치트시트에 이미 존재) | `kit/guide/토큰-치트시트.md` | 대기 |
| J18 | **R-ICON-01b** | 아이콘 라우팅 재서술 + PART·이미지 모드·결정표 재질문 규칙 | **Core 잔류**(D7과 통합) | Core ④ | 대기 |
| J19 | **R-OWN-01d** | `콘텐츠 소유권` 재서술 — 한 장은 **정보 묶음**을 담고, 줄 수·수용량은 자동 분할 명령이 아니라 오버플로 경고 기준 | **Core 잔류**(B2·D4와 통합) | Core ④ | 대기 |

## K. 신설 규칙 (이번 리팩토링에서 계획이 정한 문안 — 창작 아님)

| # | 규칙 ID | 출처 | 처리 | 신위치 | 대조 |
|---|---|---|---|---|---|
| K1 | **R-D3-01** | 계획 §8.7 D3.js 정책 전문(DEC-08) | phases-05 신설(계획 문안 전사) | phases/05 | 대기 |
| K2 | **R-IMG-02** | 계획 §8.8 — manifest `ready`+필수 판정 자산은 덱에 배선, 고아는 보고 | phases-06 + P6 verify_deck 검사 | phases/06 · `verify_deck.py` | 대기 |
| K3 | **R-VERIFY-02** | 계획 §8.6 — 주차 구조 계약 3단 탐색 | `sessions/README.md`(P3-006 완료) + P6 verify_deck | sessions/README.md · `verify_deck.py` | **OK**(P3-006) |
| K4 | **R-TYPE-01·02·03** | DEC-04 + 계획 §8.9 | 토큰-치트시트 단일 표(P3-002 완료) + deck.css `--fs-*`(P5-001 완료) | 토큰-치트시트 · deck.css | **OK** |
| K5 | **R-EMPH-01** | 계획 §8.4 선택표 | 디자인시스템 신설(P3-003 완료) | 디자인시스템 | **OK** |
| K6 | **R-TERM-01** | 계획 §8.4 | 디자인시스템 신설(P3-003 완료) | 디자인시스템 | **OK** |
| K7 | **R-COLOR-01~05** | 계획 §9 | 디자인시스템 ID 부여(P3-003 완료) | 디자인시스템 | **OK** |
| K8 | **R-EDU-01** | 계획 §9 | 커리큘럼 기준안 정본 유지 + 교육원칙-요약 재생성(P3-004 완료) | 교육원칙-요약 | **OK** |
| K9 | **R-LAYOUT-03** | 계획 §8.5 — family 레지스트리 MEMORY 승격 | 카탈로그-규격.md(P4-005) | `kit/guide/카탈로그-규격.md` | 대기 |

## L. MEMORY 처리 (§8.5 — TASK-P4-005)

| # | 대상 | 처리 | 신위치 | 대조 |
|---|---|---|---|---|
| L1 | `## 절대 우선순위` 1~5 | **승격 → Core ④** 후 참조 1줄로 축약 | Core ④ | 대기 |
| L2 | `## 디자인 판단` 절의 정본 중복 4항 | **정본 참조화**(규칙 ID) | 디자인시스템 | 대기 |
| L3 | `family_signature()`는 레이아웃 컴포넌트 레지스트리 / `data-series` 예외 | **승격 전사 → 카탈로그-규격.md**(R-LAYOUT-03) 후 원문 삭제 | `kit/guide/카탈로그-규격.md` | 대기 |
| L4 | 노트 재번호 요령(`pn-no` 스크립트 일괄) | **승격 → phases/07**(G8) 후 삭제 | phases/07 | 대기 |
| L5 | 브라우저 전수검증 규율(scale 환산·래퍼 제외·기준선 대조) | **승격 → phases/08**(H4·H5·H6) 후 원문 유지 여부는 P4-005에서 판정 | phases/08 | 대기 |
| L6 | 1주차 상태 항목(`재캡처 5건`·`배포본 재빌드는 보류`·`하단 666px 초과가 20장`·`## 1주차 덱에서 계속 유효한 계약` 절의 슬라이드 ID 상세) | **삭제** → `1주차는 2026-07-26 사용자 결정으로 동결 — 계약은 sessions/_contracts/1주차.deck.contract.json` 1줄로 대체 | — | 대기 |
| L7 | `현재 상태 — 1주차 편집본은 80장` 블록 · `배포본 …72장 버전` | **삭제**(L6에 포함) — KF-2R 잔여 해소 지점 | — | 대기 |
| L8 | H1 제목 `# MEMORY — vibecoding-deck 오답노트` | **정정** → `create-slides` (P2-012 이월분) | — | 대기 |
| L9 | `## 파이프라인 상류` 절 | **유지**(이동은 범위 밖) | — | **OK** |
| L10 | 2주차 활성 상태 블록 | **유지** | — | **OK** |
| L11 | 반복 오답→정답 · 운영 계약 | **유지**(잔류 핵심) | — | **OK** |

## M. 조립-리듬-불변요소.md 참조화 (TASK-P4-004)

| # | 대상 | 처리 | 신위치 | 대조 |
|---|---|---|---|---|
| M1 | 흰-온-흰 표면 서술 | **정본 참조화** → `→ R-COLOR-04(kit/guide/디자인시스템.md)` | 디자인시스템 | 대기 |
| M2 | navy·그라데이션 금지 서술 | **정본 참조화** → R-COLOR-01 | 디자인시스템 | 대기 |
| M3 | on-민트/on-코랄 서술 | **정본 참조화** → R-COLOR-02 | 디자인시스템 | 대기 |
| M4 | 배지 3종 서술 | **정본 참조화** → R-COLOR-03 | 디자인시스템 | 대기 |
| M5 | 수직 중앙 서술 | **유지**(이 문서가 R-BOX-04 정본 — J15) | — | 대기 |
| M6 | 조립 문법·리듬 고유 내용 | **유지·무변경** | — | 대기 |

---

## 분류 불가 문장

**없음.** SKILL.md 180줄의 모든 규칙성 문장이 위 A~J에 등재됐다(§21 중단 조건 미해당).

## 대조 결과 (TASK-P4-006 · 2026-07-26)

기계 대조 40항(Core 잔류 16 · phases 이동 15 · 정본 참조화·승격 9) + 중복 방지 2항을 실행했다.

| 검사 | 결과 |
|---|---|
| Core 잔류 행이 신 `SKILL.md`에 존재 | **16/16 OK** (초회 2건 누락 → E5 split 규칙·J3 no-default를 원문 문구로 보완 후 통과) |
| phases 이동 행이 신위치에 존재 | **15/15 OK** |
| 정본 참조화·승격 행이 신 정본에 존재 | **9/9 OK** |
| 정본 참조화 대상의 **본문 중복이 phases에 재생성되지 않음** | **2/2 OK**(navy 원문·흰-온-흰 원문 모두 phases에 없음) |
| phases 내부 상대 링크 | 18개 전부 실존, **죽은 링크 0** |
| 신 `SKILL.md` 링크 | 9개 전부 실존, **죽은 링크 0** |
| `verify_skill_setup.py` | **78 PASS / 0 FAIL** (초회 1건 FAIL — Core 재작성에서 `IMAGE_MODE` 두 분기 참조가 빠짐 → 복원 후 통과) |

**전 행 대조 상태 = OK.** 위 표가 각 행의 `대기` 표기를 대체한다.

### evals/evals.json 9케이스 재채점

| 결과 | 케이스 |
|---|---|
| 신 구조에서 **성립** | 1·2·3·5·6·7·8·9 (8건) |
| **성립 불가** | **4** `icon-routing-hint-reveal-and-presenter-notes` |

케이스 4는 `🗣` 원문을 학생 덱의 접힘 `.hint-reveal`에 두고 `💬`·`👀`를 HTML 주석으로 넣으라고 어서션한다. 그러나 규칙은 **학생 덱의 `.hint-reveal`·이모지 0**(verify FAIL)을 요구한다.

**이것은 P4 회귀가 아니라 기존 결함이다** — `git show refactor-p4-start:SKILL.md`로 대조한 결과 개편 **전** SKILL.md도 네 곳에서 동일하게 "학생 덱 `.hint-reveal` 0"을 규정하고 있었다. evals.json 케이스 4가 그 이전 세대의 규약(힌트 접힘 UI 허용)에 머물러 있다. `evals/evals.json`은 이번 계획의 P4 수정 대상이 아니므로 **고치지 않고 보고**한다(§4 후속 작업 후보).

## 요약

| 처리 | 행 수 |
|---|---:|
| Core 잔류 | 24 |
| phases-0N 이동 | 45 |
| 정본 참조화 | 14 |
| MEMORY 승격 | 5 |
| 삭제 | 3 |
| 유지(무변경) | 5 |
