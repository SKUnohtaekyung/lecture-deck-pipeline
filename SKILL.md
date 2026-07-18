---
name: vibecoding-deck
description: >-
  바이브코딩(AI와 함께 코딩) 강의덱·발표자료를 1280×720 HTML 웹덱으로 조립하는 자립형 스킬.
  채워진 콘텐츠 초안(교시별 표·본문·강사 멘트)을 읽어(없으면 자료·브리프로 계획을 먼저 초안·확인)
  방향키 발표·PDF·base64 단일파일 덱과 강사용 발표자 노트 HTML을 만든다. 대상은 40~50대
  초보자(큰 글씨·고대비·친숙한 비유). 이미지보다 코드 차트·다이어그램을 우선하고 실습 화면은
  주석 스크린샷으로 안내한다. "강의덱·세션·발표자료·교육 슬라이드 만들어줘", "다음 주차 덱",
  "이 초안/계획서/자료로 덱 조립", "PPT를 HTML로", "슬라이드에 비교·흐름·수치 차트 추가" 같은
  요청에 쓴다. "템플릿"·"스킬"을 명시하지 않아도, 강의·교육 슬라이드를 만들거나 초안·자료를
  웹덱으로 옮기는 맥락이면 이 스킬을 사용할 것.
  레이아웃은 정보 모양을 판단해 고르며 "좌 글/우 시각" 한 구도로 쏠리지 않는다.
---

# 바이브코딩 강의덱 제작

채워진 **콘텐츠 초안**(`입력양식/콘텐츠초안템플릿.md` — 교시별 `#·슬라이드 제목·본문 문구·비유·멘트` 4열 표 + 아이콘 범례)을 읽어 단일 HTML 웹덱을 조립한다. 1280×720 고정 캔버스, 방향키 발표, `F` 전체화면, 상세 발표 메뉴의 홈·페이지 이동·목록·PDF 출력. **콘텐츠·슬라이드 제목·멘트는 초안이 / 정보 모양 판단·레이아웃·시각화 구현은 스킬이 맡는다.** 초안에 강사 멘트(💬/👀/🗣)가 있으면 별도 **발표자 노트 HTML**도 함께 산출한다.

**킷 구조 (자립 — 외부 import 0):**
```
kit/guide/   정보모양-taxonomy.md · 카탈로그-규격.md · 토큰-치트시트.md · 디자인시스템.md
kit/layouts/ by-shape.md(역인덱스) · families/*.md(캐노니컬 50 · 물리 54, 4개는 구도중복 variant_of로 접힘) · README.md · catalog.html(코드 코어)
kit/charts/  by-shape.md(역인덱스) · charts-*.md · diagrams-*.md · elements-code.md(총 23) · README.md · catalog.html
kit/styles/  deck.css · legibility-40s.css · patterns.css(코드 코어)   kit/starter/ deck-template.html
kit/images/  paper-cut-v1 후보 보드·승인 에셋 중앙 레지스트리
kit/screenshots/  주석 스크린샷 element
kit/starter/ deck-template.html · presenter-notes-template.html(발표자 노트) · logo.svg
references/  조립-리듬-불변요소.md · 이미지-디렉션-프롬프트.md · 이미지-스크린샷-배포.md · 콘텐츠초안-입력형식.md
scripts/     verify_deck.py(검증) · assemble_deck.py(조각→미리보기) · build_release.py(최종본 빌드) · inline_deck.py+verify_distributable.py(인라인·자립성 강제) · font_embed.py(폰트 서브셋)   evals/ evals.json(회귀)
```

---

## §0. 불변 요소 — 그대로 유지 (협상 불가)

1. **고정 슬라이드**: 표지(`cover`)·도입(`s02-slide`)·아젠다(`s03-slide`)·마무리(`concept-recap`)는 `kit/starter/deck-template.html`의 구조·CSS 그대로. 표지는 `data-cube` 3개(각 3면, 총 polygon 9개)와 코랄 스파크 1개를 반드시 유지한다. 아젠다(`s03-slide`)는 팀명 없는 로고+브랜드+라인 헤더 + 좌측 고정 제목 **"오늘 배우게 될 것"**(초안의 아젠다 행 제목과 무관하게 항상 이 문구 — verify 강제)·민트 바(`.an-bar`)·1~2줄 리드 + 노드-타임라인(`.an-item`을 항목 수만큼 — 파트 수 또는 여정 단계 수, 3~6 권장, 번호=블루 fill 64px 플랫(그림자 금지)·항목 제목 `.an-h`=블루) 구조를, 파트전환(`part-divider`)은 헤더 없이 표지와 동일한 아이소 큐브 클러스터(`.dv-hero`, 9면)+진행 도트(`.pd-dot`)+타이틀 구조를 유지한다. 텍스트 슬롯·이미지만 교체.
2. **하단 네비게이션 바**(`.controls > .navbar`)와 **상세 발표 메뉴**(`.presentation-menu`) — Apple Liquid Glass 원칙을 응용한다. 기본 바는 고투명 재질을 유지하고, 펼쳐지는 상세 메뉴는 배경과 구분되는 **옅은 쿨그레이 반투명 유리**(`--glass-thick`)로 만든다. 강한 배경 블러·채도 보존·얇은 빛 테두리·안쪽 하이라이트·다층 그림자를 함께 쓰며, 완전 투명하거나 불투명한 흰색 패널처럼 만들지 않는다. 상세 메뉴는 현재 제목·한 줄 조작부·슬라이드 목록만 보이는 단순 구조이며 홈·페이지 이동·PDF·단축키를 제공한다. `G`로 열고 `Esc`로 닫는다. `B`는 화면 가리기, `F`는 전체화면이다. **리모컨은 마우스를 움직일 때만 나타난다** — 슬라이드 전환(방향키 등)으로는 노출하지 않아 발표 화면을 깨끗이 유지한다(스타터 JS의 keydown 분기엔 `poke()`를 넣지 않는다).
3. **모든 파트는 파트 전환(`part-divider`) 슬라이드로 시작 — PART 1 포함.** 각 파트 첫 슬라이드 앞에 반드시. **파트 수 = divider 수.** 진행 도트 `is-active`는 현재 파트에, `PART n / N`의 N은 전체 파트 수.
4. **이미지 판정·모드 게이트** — `정보 모양·코드 element 결정 → 이미지 목적 판정 → 중앙 레지스트리에서 승인 에셋 재사용 검색 → generate/transform 수 산출 → IMAGE_MODE 확인` 순서를 지킨다. 판정은 `NO_IMAGE | IMAGE_EXPLANATORY | IMAGE_MNEMONIC | IMAGE_DECORATIVE_OPTIONAL` 네 가지다. 승인 에셋 재사용만으로 충족되거나 신규 작업이 0장이면 모드 질문을 생략한다. 신규 생성·변형이 1장 이상이면 `IMAGE_MODE = generate_now | prompt_only` 중 하나를 확인하고 **답을 받기 전에는 생성·프롬프트 시트 확정·실제 이미지 연결을 시작하지 않는다**. 세부 계약은 [`references/이미지-디렉션-프롬프트.md`](references/이미지-디렉션-프롬프트.md)를 따른다.
5. **템플릿 규칙(v2.1)** — **navy 금지**(어두운=`--ink`) · **그라데이션 금지**(cover 포함) · **번호배지 민트**는 `.num-circle`·`.work-step .n`·`.pd-dot.is-active` **셋만**(다이어그램/플로우 노드·`.timing`은 블루) · **헤더 파트진행**(본문 슬라이드 우측 `PART n/N`+민트 도트, `.s-part` JS 주입) · **하단 페이지네이션**(`n/전체`, `.s-pageno` JS 주입, 표지·마무리 제외). 운영 정본은 shipped `kit/guide/디자인시스템.md`·`kit/guide/토큰-치트시트.md`(설계 배경·전체 명세는 `_dev/설계기록/색시스템-v2-명세.md` — 배포 제외).

> 스타터를 복사하면 1·2가 자동 보존된다. 3은 조립 때 파트 수만큼 배치. 검증(8단계)에서 확인.

---

## 워크플로우 (9단계 — 판단 게이트)

> **조립 전 필수 읽기 (read-path).** 아래를 먼저 읽고 시작한다 — 건너뛰면 규칙 위반·오버플로·토큰 실수가 반복된다(verify가 사후에 잡지만, 조립 전에 막는 게 싸다).
> - **항상**: `references/콘텐츠초안-입력형식.md`(입력·아이콘·PART) · `kit/guide/정보모양-taxonomy.md`(정보 모양) · `kit/guide/디자인시스템.md`+`kit/guide/토큰-치트시트.md`(색·토큰·가독성·헤더) · `references/조립-리듬-불변요소.md`(조립 문법·리듬·불변요소) · `references/이미지-디렉션-프롬프트.md`(필요성·모드·스타일·프롬프트·QA).
> - **후보·스펙**: `kit/layouts/by-shape.md` · (차트 필요 시) `kit/charts/by-shape.md` → 고른 항목 `kit/layouts/families/*.md`·`kit/charts/*.md`.
> - **마크업 복사**: `kit/layouts/catalog.html`·`kit/charts/catalog.html`(코드 코어) — 없는 구도만 `데모_제작규칙.html`.
> - **화면조작이면**: `references/이미지-스크린샷-배포.md`(6단계 — 캡처·파일 배치·배포).
> - **조건부**: 멘트 있으면 `kit/starter/presenter-notes-template.html`(7단계).

### 1. 입력 파악 (3가지 진입)
- **세션 폴더 규약**: `sessions/N주차/초안.md`가 있으면 그것을 콘텐츠 초안으로 읽고, 산출(덱·발표자 노트)도 **같은 폴더**에 쓴다(새 주차 골격 `sessions/_template/` 복사 · 규약 `sessions/README.md`).
- **우선순위**: 현재 사용자 지시 → 채워진 콘텐츠 초안(슬라이드 순서·제목·본문·멘트) → 원본 자료 → 이 스킬의 판단 규칙. 단, 접근성·1280×720 오버플로·고정 슬라이드 불변요소는 항상 지킨다.
- **콘텐츠 초안이면(공식 입력)**: `입력양식/콘텐츠초안템플릿.md` 형식 — 교시별 `#·슬라이드 제목·본문 문구·비유·멘트` 4열 표 + 아이콘 범례 서두. 인식·컬럼 매핑·아이콘 라우팅·PART 매핑의 **고정 절차는 [`references/콘텐츠초안-입력형식.md`](references/콘텐츠초안-입력형식.md)** 를 따른다. 핵심:
  - 제목·본문은 **콘텐츠팀 소유라 재작성 금지**(원문 그대로). 슬라이드 묶음·장수 유지, `분할 허용` 없이 임의 분할 금지 — 수용량 초과면 원인 제시 후 승인받아 분할.
  - **아이콘 라우팅(고정)**: `💬`·`👀`→ HTML 주석(화면 비노출) · `🗣`→ `.hint-reveal`(화면 접힘 힌트). 이모지 문자는 최종 HTML에 남기지 않는다(verify가 FAIL).
  - **정보 모양은 이 형식에 지정 칸이 없다** → 모든 슬라이드를 스킬이 직접 추론(§2).
  - **교시→PART 매핑은 항상 사용자에게 확인**(사용자가 이미 줬으면 수용). 임의 확정 금지.
- **폼 없이 브리프·원자료만 오면**(예: "1주차 자료로 만들어줘"): 먼저 **슬라이드 계획을 초안**(파트·슬라이드별 전달 목적·정보 묶음·정보 모양)해 **사용자 확인을 받고** 조립한다. 확인 없이 즉흥 조립하지 않는다(판단 게이트 우회 방지).
- **한 장만 / 기존 덱에 추가면**: 스캐폴딩 생략하고 2~5단계만(정보 모양 판단 → 레이아웃·element 선택 → 그 `<section>` 하나 조립 → 검증).

### 2. ★ 정보 모양 분류 (판단 게이트 — 이 스킬의 핵심)
슬라이드마다 **레이아웃을 고르기 전에** "이 정보가 무슨 모양이냐"를 먼저 정한다.
- 공식 입력엔 `시각화 의도` 지정 칸이 없으므로, **모든 슬라이드에서** 제목·본문의 동사·구조를 보고 [`kit/guide/정보모양-taxonomy.md`](kit/guide/정보모양-taxonomy.md)의 **12 정준 모양**으로 스킬이 직접 분류한다(taxonomy의 "정보 모양 추론 절차").
- 이 단계를 건너뛰고 즉흥적으로 고르지 않는다. **"좌 글/우 시각"은 기본값이 아니다.**

### 3. 역인덱스로 후보 뽑기
- **레이아웃**: [`kit/layouts/by-shape.md`](kit/layouts/by-shape.md)에서 그 모양의 후보 레이아웃(순위) 확인.
- **element**: 모양이 numeric·structure·containment·flow·mapping·comparison이면 [`kit/charts/by-shape.md`](kit/charts/by-shape.md)에서 차트/다이어그램 element도 확인. **concept이면서 대상이 소스코드**일 때도 확인 — `E-code`(주석 코드 블록)가 여기 등재돼 있다(코드 설명은 회색 `<pre>` 덤프로 도망가기 쉬우니 놓치지 말 것).

### 4. 레이아웃과 element를 따로 선택 (다양성 규칙)
조립 전에 **슬라이드 결정표**를 먼저 쓴다 — 판단을 눈에 보이게 만들어 원칙 B를 실제로 강제하고, 단조를 *코딩 전에* 잡는다:

| # | 정보 모양 | 구도 패밀리 | element(선택) | 이미지 판정·역할 | 직전과 다른 패밀리? |
|---|---|---|---|---|---|
| B01 | flow | vertical-flow | D-flow-v | `NO_IMAGE` · 코드 흐름으로 충분 | (첫 본문) |
| B02 | concept | centered | — | `IMAGE_EXPLANATORY` · `hero` · 재사용 검색 | ✓ 다름 |

- **직전 콘텐츠 슬라이드와 같은 구도 패밀리를 피한다.** split(좌우 비대칭)은 희소하게, **연속 금지**.
- 차트/다이어그램이 필요하면 **element를 골라 레이아웃에 얹는다** — 레이아웃 ≠ 다이어그램(옛 venn-slide처럼 결합하지 않음). 예: `containment` → 레이아웃 `L-ct-concentric` + element `D-concentric`.
- 선택은 각 항목의 `data_shape`·`when_to_use`·`when_to_avoid`로 검증.
- `🗣`가 있던 슬라이드는 결정표에 **`힌트카드`** 메모를 남겨, element 선택 때 `.hint-reveal` 배치를 놓치지 않게 한다. 이 결정표(정보 모양·PART·힌트카드 유무)를 **조립 전 사용자에게 확인**받는다.
- 코드 element 후보까지 결정한 뒤 [`references/이미지-디렉션-프롬프트.md`](references/이미지-디렉션-프롬프트.md)의 기준으로 네 상태 중 하나를 판정한다. 장식 이미지는 사용자가 시각적 풍부함을 명시한 경우에만 `IMAGE_DECORATIVE_OPTIONAL` 후보가 되며, 파트당 최대 1장·비연속·차트/다이어그램과 동시 사용 금지다. 이어 `kit/images/paper-cut-v1/registry.json`에서 `approved` 에셋을 먼저 찾고, 재사용으로 충족되지 않는 generate/transform 수가 1장 이상이며 요청에 모드가 없으면 아래 **두 선택지만 정확히 제시하고 답을 기다린다**:
  > 이미지가 필요한 슬라이드는 N장입니다. 어떤 방식으로 진행할까요?  
  > 1. 이미지 바로 생성 — 생성·투명화·검수 후 덱에 삽입  
  > 2. 프롬프트만 제작 — 파일명과 슬롯, 생성용 프롬프트 시트만 작성
- 이 게이트의 답을 받기 전에는 5단계 조립으로 넘어가지 않는다. 신규 생성·변형이 0장이면 슬라이드별 판정과 재사용 Asset ID 또는 `NO_IMAGE` 이유를 결정표와 `자료/이미지-에셋.json`에 남기고 질문 없이 진행한다.

### 5. 조립
`kit/starter/deck-template.html`을 기반으로(검증된 CSS는 `kit/styles/patterns.css`를 deck.css·legibility **뒤에** 로드하면 재사용 — 매번 새로 짜지 않는다):
- 고정 1·2·3·마무리 텍스트 교체, 파트 수만큼 `part-divider` 배치.
- 본문 슬라이드: **먼저 [`kit/layouts/catalog.html`](kit/layouts/catalog.html)·[`kit/charts/catalog.html`](kit/charts/catalog.html)(코드 코어)에서 해당 ID `<section>`/fragment를 복사**(patterns.css가 CSS 자동 적용). 카탈로그에 없는 구도만 `데모_제작규칙.html`의 같은 구도 마크업 + `families/*.md`·`charts/*.md` 스펙으로 조립 — **빈 스펙만으로 처음부터 코딩하지 말 것**(오버플로·토큰 실수의 원인). 차트/다이어그램 element(`.viz-*`)는 레이아웃 시각 슬롯에 삽입.
- **토큰만 사용**([`kit/guide/토큰-치트시트.md`](kit/guide/토큰-치트시트.md)) · **가독성 하한**(본문 22px·표 17px) · **색은 문법**(구조·주 강조 블루, 행동·안전 민트, 주의 코랄, 오류 레드) · **오버플로 0**(세로예산 548px·행높이 계산식).
- **아이콘 라우팅 반영**: `🗣` 슬라이드는 본문 슬롯에 `.hint-reveal`(`kit/styles/deck.css`) — 안전망 예시 원문 그대로, 레이아웃 무관 삽입. `💬`·`👀`는 `<!-- 발표노트: … -->` 주석으로. **이모지 문자 자체는 마크업에 남기지 않는다.**
- 채울 수 있는 레이아웃은 본문 안전 영역을 적극 사용한다. 단, centered·일부 full-bleed처럼 여백 자체가 메시지인 구도는 의도적 여백을 유지한다.
- 이미지 슬롯은 `<figure class="asset-slot asset-slot--hero" data-image-purpose="explanatory" ...>` 계약을 사용하고 활성 역할은 `hero | support | spot`뿐이다. 설명·기억 이미지는 관계를 설명하는 한국어 `alt`가 필수이며 장식 이미지는 `alt="" aria-hidden="true"`다. `prompt_only`는 `<img>`를 만들지 않고 figure에 `data-image-state="expected" data-expected-src="…"`만 둔다. `cover-object`·`section-overlay`는 승인된 별도 템플릿 변형이 없으므로 사용하지 않는다.
- 조립 문법·리듬·불변요소 상세: [`references/조립-리듬-불변요소.md`](references/조립-리듬-불변요소.md).
- **산출 위치·2단계 구조**: 편집본은 `sessions/N주차/강의덱.초안/`에 **파트별 조각**으로 쓴다 — `shell.html`(head·고정 슬라이드·`<!-- ::PARTS:: -->` 마커·JS) + PART마다 `part-NN.html`(`sessions/_template/강의덱.초안/` 골격 복사). 대화형 수정은 조각이 빠르고 정확하다. 미리보기 통합본은 `python scripts/assemble_deck.py sessions/N주차/강의덱.초안`(`--watch` 자동 재조립) → `강의덱.html`. kit CSS 링크는 `../../kit/styles/…`(세션 폴더 2단계). 최종 단일 자립본은 9단계 `build_release.py`.

### 6. 이미지 모드 실행 · 스크린샷 핸드오프
- 이미지 판정·의미 브리프·출력 경로별 프롬프트·재사용·투명 PNG QA는 [`references/이미지-디렉션-프롬프트.md`](references/이미지-디렉션-프롬프트.md)를 따른다. 중앙 승인 정본은 `kit/images/paper-cut-v1/registry.json`, 세션 실행 정본은 `sessions/N주차/자료/이미지-에셋.json`, 사람용 대응 문서는 `이미지-프롬프트.md`다. 상세 계약을 이 문서나 플랫폼 어댑터에 복제하지 않는다.
- 기본 표지는 고정 큐브 9면을 유지하고 생성 이미지를 넣지 않는다. 생성 이미지는 S02부터 검토하며, `paper-cut-v1`은 투명 오브젝트 전용이다. 사진·풀블리드는 사용자 제공 자산 또는 별도 승인 스타일만 사용한다.
- **`generate_now`**: 에셋별 초기 생성은 한 번씩 별도 호출한다. built-in 경로는 **균일 마젠타 배경만** 요구하는 크로마 원본 프롬프트를 쓰며 native alpha 문구를 섞지 않는다. 승인된 native-alpha 경로는 **진짜 투명 배경만** 요구하고 크로마 문구를 섞지 않는다. 의미·스타일 교정은 1회, 알파 후처리 재시도는 1회까지다. 이후 설명·기억 이미지는 중단·보고하고, 장식 이미지는 반려 기록 후 생략한다. 통과한 최종 PNG만 `sessions/N주차/자료/images/`에 저장·등록·연결한다.
- **`prompt_only`**: `sessions/N주차/자료/이미지-프롬프트.md`와 `이미지-에셋.json`에 의미 브리프·역할·예상 파일·프롬프트를 기록한다. HTML figure는 `data-image-state="expected"`와 `data-expected-src`만 가지며 실제 `<img src>`는 두지 않는다. 개발 덱에서는 깨진 이미지가 없어야 하고 배포는 unresolved 설명·기억 슬롯 때문에 실패해야 한다.
- 화면 조작 안내(`screen-operation`)는 이미지 모드와 별개다. 실제 화면은 사용자가 캡처하고, 번호·테두리 overlay는 **주석 스크린샷** 킷([`kit/screenshots/`](kit/screenshots/))으로 구현한다. 파일 배치·캡처·배포 상세는 [`references/이미지-스크린샷-배포.md`](references/이미지-스크린샷-배포.md)를 따른다.
- 참고: 초안의 `💬`/`🗣`/`👀`는 텍스트라 이 단계 대상이 아니다 — 라우팅은 1·5단계·[`references/콘텐츠초안-입력형식.md`](references/콘텐츠초안-입력형식.md).

### 7. 발표자 노트 HTML 산출 (멘트가 있으면)
- 초안에 `💬`/`👀`/`🗣`가 하나라도 있으면 `kit/starter/presenter-notes-template.html`을 복제해 **`<덱이름>_발표자노트.html`**을 만든다 — 슬라이드 순서대로 번호·제목 + 그 슬라이드의 멘트를 종류별로 나열. **`🗣`는 펼쳐진 상태**로(강사는 안전망 예시를 미리 다 봐야 하므로 — 수강생 화면과 반대). 메인 덱과 별개 파일(같은 폴더에 둔다 — 세션 폴더면 `sessions/N주차/`).

### 8. 검증 (측정 우선 — 스크립트 먼저)
**① 정적 검증 스크립트로 어서션 자동 채점**: `python scripts/verify_deck.py <덱>.html --parts N` — 슬라이드·고정슬라이드·**part-divider=파트수**·네비/PDF·deck.css+legibility·**코드시각화 vs 이미지**·**구도 다양성·같은 구도 연속**·토큰(raw #hex)·**아이콘 마커 누출(💬/🗣/👀)**·**힌트 리빌 `<summary>`**를 한 번에.
**② 브라우저로 오버플로·콘솔·가독성**(스크립트가 못 재는 것): 로컬 http 서버 서빙(패널은 `file://` 불가) 후 슬라이드별 `scrollWidth/Height ≤ client`(오버플로 0) · 콘솔 에러 0 · Pretendard 로드 · 본문 22px. **`.hint-reveal`이 있는 슬라이드는 닫힌 상태 + 강제로 연 상태 둘 다 오버플로 검사**(548px 세로예산은 열림 상태에서 초과할 수 있고, 기본 DOM 훑기로는 안 잡힌다). **박스 패딩 과다도 이 단계에서 확인**: 배너·콜아웃·카드 눈에 띄면 `offsetHeight` vs `padding:0` 임시적용 시 높이를 비교해 패딩 비중을 재본다(1/3 넘으면 줄임 — §핵심 규칙 참조).
- 스크린샷은 정적이라 불안정·느림 → **측정 우선, 스크린샷은 증빙 최소**.

### 9. 배포 — 단일 자립 파일 (강제)
학생 배포본은 CSS·이미지·**폰트**가 전부 인라인/임베드된 단일 HTML이어야 한다(오프라인에서 파일 하나로 완전 렌더).
- **한 커맨드**: `python scripts/build_release.py sessions/N주차/강의덱.초안` = 조립 → `verify_deck` → `inline_deck --offline`(CSS·이미지 인라인 + Pretendard **사용 글자 서브셋** `@font-face` 임베드) → `verify_distributable`(자립성 강제) → `강의덱_배포.html`.
- **강제 게이트**: 외부 `<link/script href=http>` 0 · 모든 `src`/`url()` `data:` · 임베드 `@font-face` 존재 + Pretendard CDN 부재 · unresolved 설명·기억 슬롯 0. 하나라도 위반하면 파일을 쓰지 않는다(fail-closed) — 통과 전엔 "완성"이 아니다.
- 빌드된 배포본은 손대지 말고 **조각을 고쳐 재빌드**한다(폰트 서브셋이 매 빌드 최종 텍스트에서 재계산되므로 글자 누락이 없다). 이미지 스크린샷·주석 상세: `references/이미지-스크린샷-배포.md`.

---

## 참조 지도 (단계별 · ★=조립 전 항상 필수)

| 파일 | 언제 |
|---|---|
| `references/콘텐츠초안-입력형식.md` ★ | **1단계 — 콘텐츠 초안(교시표) 인식·아이콘 라우팅·PART 매핑·발표자 노트** |
| `kit/guide/정보모양-taxonomy.md` ★ | **2단계 판단 게이트 — 정보 모양 분류, 항상** |
| `kit/guide/디자인시스템.md` ★ | **색 팔레트·문법·헤더·가독성 규칙(shipped 정본) — 조립 전 항상** |
| `kit/guide/토큰-치트시트.md` ★ | **색 토큰·세로예산·행높이 계산 — 조립 시 항상** |
| `references/조립-리듬-불변요소.md` ★ | **조립 문법·파트·색문법·리듬·불변요소 — 조립 전 항상** |
| `kit/layouts/by-shape.md` · `kit/charts/by-shape.md` | 3단계 후보 뽑기 |
| `kit/layouts/families/*.md` · `kit/charts/*.md` | 고른 항목의 스펙(built_on·capacity·sketch) |
| `kit/layouts/catalog.html` · `kit/charts/catalog.html` | 5단계 — 코드 코어 `<section>`/fragment 복사 |
| `kit/guide/카탈로그-규격.md` | 스키마·검증 체크리스트·no-default 헌장 |
| `references/이미지-디렉션-프롬프트.md` | 4·6단계 — 이미지 필요성·`IMAGE_MODE`·paper-cut-v1·프롬프트·에셋 재사용·QA 정본 |
| `references/이미지-스크린샷-배포.md` | 6·9단계 — 이미지 파일 배치·주석 스크린샷·단일파일 배포 |
| `kit/starter/presenter-notes-template.html` | 7단계 — 발표자 노트 HTML 복제 원본 |
| `데모_제작규칙.html` | 5단계 — 완성 덱의 실제 마크업을 본뜰 때 |
| `scripts/verify_deck.py` | 8단계 — 정적 검증 자동 채점 |
| `scripts/assemble_deck.py` | 5·8단계 — 조각(`강의덱.초안/`) → 미리보기 통합본 조립(`--watch`) |
| `scripts/build_release.py` | 9단계 — 최종본 빌드(조립→검증→인라인→자립성 강제) |
| `scripts/inline_deck.py` · `verify_distributable.py` · `font_embed.py` | 9단계 — CSS·이미지 인라인 + 폰트 서브셋 임베드 · 자립성 강제 게이트 |

## 핵심 규칙 (요약)
- **밀도**: 저밀도 최소주의 폐기 → 정보 단위 3~6개(물리 한도 내). 정본은 콘텐츠 스킬 §밀도.
- **no-default**: 모든 레이아웃·element는 동급. 정보 모양이 고른다. 좌우분할은 희소·비연속.
- **색은 의미(장식 아님)**: 구조(헤더 선·`.accent-bar`·`.s-eyebrow`·다이어그램/플로우 노드·표 헤더·UI)는 `--blue`. **강조어(제목·본문의 결론·핵심 단어)는 민트 계열이 기본** — `.hl-mint-text`(글자)·`.hl-mint-underline`(밑줄)·`.hl-mint-mark`(글자폭 배경)을 문맥에 맞게. 블루 글자 강조(`.hl`)는 절제하고 **한 화면을 파란색으로 도배하지 않는다**(강조가 전부 블루면 색이 의미를 잃음). `--blue-soft`=배경, `--periwinkle`=비강조 데이터.
- **세로 균형(하단 여백 금지)**: 콘텐츠를 위로 몰아 아래를 크게 비우지 않는다. 정보가 적으면 세로 중앙정렬(`.center-msg`는 자동)·`.s-full.fill`(격자·표 확장)·`.s-full.solo`(콜아웃 하나를 아래 중앙에 크게)로 캔버스 720 전체를 균형 있게. 오버플로 0과 동시에.
- **박스 크기 = 정보량 비례**: 한 줄 박스를 억지로 크게, 여러 줄 박스를 억지로 작게 만들지 않는다 — **내용이 많아지면 박스도 그만큼 커진다(크기를 내용에 맞추는 것이지 내용을 줄이라는 뜻이 아니다)**. 격자 정보량 편차가 크면 bento·가변 행높이로 균형.
  - ⚠️ **패딩도 절대 기준으로 본다**(격자 상대비교뿐 아니라 박스 하나만 있어도): 세로 패딩 합이 콘텐츠 자체 높이의 **1/3을 넘으면 과하다** — 줄인다. 눈대중: 1~2줄 배너·콜아웃은 세로 패딩 **12~14px**, 3줄 이상이면 16~20px. 조립 중 박스를 완성하면 곧바로 "이 패딩, 내용보다 커 보이나?"를 자문한다(완성 후 리뷰가 아니라 **만드는 순간에** 적용). 실측 사례: `.concept-bottom`이 18px×2=36px 패딩으로 콘텐츠 52px 대비 41%를 차지해 커 보였음 → 12px×2=24px(33%)로 줄여 박스 88→73px.
  - ⚠️ **폭도 절대 기준으로 본다(높이 규칙과 대칭)**: 짧은 문장 하나 담은 단독 박스(배너·단일 콜아웃 등)를 부모 컨테이너 폭에 맞춰 억지로 늘리지 않는다 — 텍스트가 필요한 만큼만 폭을 잡고 **`.hug-center`**(`kit/styles/deck.css`, `width:fit-content;max-width:860px` + 가운데 정렬)를 붙인다. `.concept-bottom`은 이 동작이 기본 내장. **예외**: 시퀀스를 표현하는 요소(`.concept-flow` 같은 진행 단계 칩)와 짝을 이루는 격자 요소(대비 `cc-grid`·체크리스트 `grid-2/3` 안의 콜아웃)는 폭 전체를 쓰는 것 자체가 의미이므로 붙이지 않는다. **주의**: 부모가 `flex-direction:column`이면(예: `.concept-panel`) `width`만 바꿔선 안 줄어든다 — flex의 `align-items:stretch` 기본값이 이기므로 `align-self`도 같이 바꿔야 한다(`.hug-center`에 이미 포함). 실측 사례: `.concept-bottom`이 폭 1152px 중 76%(870px)가 빈 공간이었음 → 282px로 줄여 가운데 정렬.
- **줄바꿈은 문맥 경계**: 수동 `<br>`은 단어를 끊지 않고 구·절 경계에서(조사·어미가 앞줄에 매달리지 않게). 가독성·양쪽 줄길이 균형을 함께 본다.
- **navy 금지 · 그라데이션 금지**(cover 포함) · 민트·코랄 fill 위 흰 글자 금지(`--on-mint`/`--on-coral`). 단, 글자폭만 감싸는 `.hl-mint-mark`은 흰 글자를 쓰는 예외다.
- **번호배지 민트 = `.num-circle`·`.work-step .n`·`.pd-dot.is-active`만**(다이어그램/플로우 노드·`.timing`은 블루=구조).
- **박스 표면은 흰색-온-흰색 금지**: 카드/박스는 ① 의미 틴트 fill(구조=`--blue-soft` 기본 / 행동=`--mint-soft` / 주의=`--coral-soft`) + 같은 계열 보더, 또는 ② 흰 fill + **명확한 유색 보더**(`--blue-line-strong`/`--mint-line`/`--coral-line`) 중 하나. **흰 fill + `--line` 근백색 보더 단독 구분 금지**(verify FAIL). `--line`은 박스 내부 구분선 전용. 예외: 코드/터미널 표면·주석 스크린샷 창·`.pd-dot`·표.
- **넘버 행 수직 중앙**: 원형 배지+텍스트 행(`.work-step`·`.agenda-item`)은 텍스트를 배지 기준 수직 중앙에 둔다(`align-items:center`, verify 강제). 본문 `<span>` 없이 제목 `<b>`만 넣어도 중앙.
- **헤더 파트진행**(본문 우측 `PART n/N`+민트 도트) · **하단 페이지네이션**(`n/전체`) 자동 주입. 색·헤더 규칙 운영 정본은 `kit/guide/디자인시스템.md`(설계 배경: `_dev/설계기록/색시스템-v2-명세.md`, 배포 제외).
- **가운데 커넥터**: 두 요소를 이을 땐 파란 `→`(흐름)·`⊃`(포함)·`≠`(대비)·`↓`(검증).
- **아이콘 라우팅(고정)**: `💬`·`👀`→ HTML 주석(화면 비노출) · `🗣`→ `.hint-reveal`(접힘 힌트, 인쇄해도 접힘). 이모지 문자는 최종 HTML에 남기지 않는다(verify FAIL). PART 매핑·정보 모양 판단은 매번 사용자 확인.
- **콘텐츠 소유권**: 초안의 `슬라이드 제목`·`본문 문구`는 재작성하지 않는다. "제목은 결론으로"는 **스킬이 직접 짓는 제목**(형식 없는 브리프 경로)에만 적용 — 초안이 준 질문형 제목은 그대로 둔다. 한 장은 초안이 정한 **정보 묶음**을 담고, 줄 수·수용량은 자동 분할 명령이 아니라 오버플로 경고 기준이다.
