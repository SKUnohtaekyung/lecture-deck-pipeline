# centered 패밀리 — 중앙 무대에 단일 메시지/도해, 좌우 대칭 여백, `.center-msg` 기반.

> composition_family = `centered`. 판단 축: [`../../guide/정보모양-taxonomy.md`](../../guide/정보모양-taxonomy.md) · 규격: [`../../guide/카탈로그-규격.md`](../../guide/카탈로그-규격.md) §4 · 토큰: [`../../guide/토큰-치트시트.md`](../../guide/토큰-치트시트.md).
> 이 패밀리는 화면 정중앙에 **하나의** 주장·개념·도해를 두고 좌우 여백을 대칭으로 남긴다. 컬럼 분할(split) 아님. 1280×720에서 세로 스크롤 없이 성립하도록 용량을 잡았다.

---

### L-ct-statement — 큰 중앙 선언 / Centered Statement

- **id**: `L-ct-statement`
- **name**: 큰 중앙 선언 / Centered Statement
- **composition_family**: `centered`
- **composition_shape**: `solo-center`
- **info_shapes**: `[declaration]`
- **when_to_use**: 한 문장짜리 강한 주장·테제를 좌중이 멈춰 읽게 할 때. 문장 자체가 곧 슬라이드일 때.
- **when_to_avoid**: 담을 항목이 2개 이상이거나, 데이터·비교·단계가 얽힐 때(→ grid-mosaic·comparison-symmetric·vertical-flow). 문장이 20어를 넘어 세 줄을 초과하면 부적합.
- **capacity**: 제목 ≤14어(52px에서 2~3줄) + 아래 보조 콜아웃 0~1개(≤2줄). 그 이상은 담기지 않음.
- **built_on**: `.center-msg-a` · `.center-msg` · `.cm-title`(`.hl`로 핵심어 블루 1곳) · `.callout`(선택, `.blue`)
- **content_slots**: `title`, `callout?`
- **sketch**:
```
┌──────────────────────────────────────────────┐
│  s-head: [로고] 브랜드 ───────────── 팀명       │
│                                                │
│            우리는 이미 답을                     │
│          알고 있다 — 실행이 [문제]다            │  ← 중앙, cm-title 52px, .hl 1곳
│                                                │
│          [ 콜아웃: 한 줄 보조 명제 ]            │  ← 선택 1개
│                                                │
│                                        p.7      │
└──────────────────────────────────────────────┘
```
- **coded**: no
- **density_note**: cm-title 52px는 본문 하한(23px)을 크게 상회. 콜아웃 본문은 22px 유지. 좌우 max-width 700px로 한 줄 글자수를 억제해 3줄 이내 보장.
- **source**: https://a1slides.com/powerpoint-layout-composition-design-principles/ (verified — "한 슬라이드 하나의 핵심 메시지 + 하나의 지배적 요소" 원칙 확인)
- **adaptation_note**: 원본은 웹 아티클의 서술일 뿐 복제 대상 아님. deck.css `.center-msg-a`에 문장을 넣고 핵심어는 `<span class="hl">` 또는 민트 강조 프리미티브로 처리한다. 배경 이미지·큰 오버레이 없이 흰 캔버스 + 텍스트만으로 여백을 무기화. 하단 콜아웃은 메시지 수용량 안에서 필요한 만큼만 둔다.

---

### L-ct-question — 중앙 질문 프레임 / Centered Question Frame

- **id**: `L-ct-question`
- **name**: 중앙 질문 프레임 / Centered Question Frame
- **composition_family**: `centered`
- **composition_shape**: `solo-center`
- **info_shapes**: `[declaration]`
- **when_to_use**: 파트를 여는 큰 질문("정말 Z할까?")을 던지고, 서브라벨로 맥락을, 콜아웃으로 방향을 살짝 줄 때.
- **when_to_avoid**: 질문에 곧바로 표·차트로 답해야 할 때(→ top-down·comparison). 질문이 10어를 넘어 64px에서 두 줄을 초과하면 부적합. 서술형 개념 설명에는 `L-ct-definition`을 쓸 것.
- **capacity**: 서브라벨(cm-sub) 1줄 ≤8어 + 질문(cm-title 64px) ≤10어(1~2줄) + 콜아웃 ≤1개(≤2줄).
- **built_on**: `.center-msg-b` · `.cm-sub` · `.cm-title`(`.hl`) · `.callout`
- **content_slots**: `sub`, `title`, `callout?`
- **sketch**:
```
┌──────────────────────────────────────────────┐
│  s-head ─────────────────────────────          │
│                                                │
│        맥락 서브라벨 (cm-sub 24px)             │
│                                                │
│         왜 아무도 [이것]을                      │  ← cm-title 64px, .hl
│           바꾸지 않았나?                        │
│                                                │
│        [ 콜아웃: 오늘 답할 방향 한 줄 ]        │
│                                                │
└──────────────────────────────────────────────┘
```
- **coded**: no
- **density_note**: cm-title 64px·cm-sub 24px 모두 하한 초과. max-width 760px로 질문 한 줄 폭 제한. 콜아웃 본문 24px(center 문맥 상향).
- **source**: https://slidemodel.com/powerpoint-title-slide-examples/ (verified — 중앙 정렬 큰 타이틀 + 중앙 서브타이틀이 격식·명료성 맥락에 적합하다고 서술)
- **adaptation_note**: 원본은 표지/섹션 타이틀 예시. 여기선 표지 아님 — 본문 슬라이드의 "질문 던지기"로 재표현. `.center-msg-b`의 sub→맥락, title→질문, callout→방향. 물음표는 텍스트로, 장식 도형 없이 여백으로 무게를 준다.

---

### L-ct-quote — 중앙 인용 / Centered Pull-Quote

- **id**: `L-ct-quote`
- **name**: 중앙 인용 / Centered Pull-Quote
- **composition_family**: `centered`
- **composition_shape**: `solo-center`
- **info_shapes**: `[declaration]`
- **when_to_use**: 외부 권위·현장 목소리·핵심 인용문 한 개를 중앙에 크게 걸고 출처를 밑에 붙일 때.
- **when_to_avoid**: 인용이 문단 길이(30어 초과)로 길거나 두 개 이상을 나란히 보일 때(→ comparison-symmetric). 자기 주장은 인용이 아니므로 `L-ct-statement`.
- **capacity**: 인용문 ≤30어(약 40px에서 3~4줄) + 출처 1줄(이름·소속). 인용 1개만.
- **built_on**: `.center-msg` · `.cm-title`(크기 축소 변형, `.hl`로 결정적 구절) · 출처는 `.cm-sub`/`.pill` 재사용 · 좌측 블루 `.accent-bar`로 인용 마크 대용
- **content_slots**: `quote`, `attribution`
- **sketch**:
```
┌──────────────────────────────────────────────┐
│  s-head ─────────────────────────────          │
│                                                │
│  ▎ "우리는 도구를 바꾼 게 아니라              │  ← accent-bar + 인용 ~40px
│  ▎  일하는 방식을 [바꿨다]."                   │     .hl 1곳
│                                                │
│           — 이름, 소속/직책                     │  ← 출처 1줄, gray-700
│                                                │
└──────────────────────────────────────────────┘
```
- **coded**: no
- **density_note**: 인용 40px·출처는 gray-700 22px 이상 유지(캡션 하한 준수). 짧은 인용만 중앙 정렬(길면 좌정렬로 전환 — 소스 권고 반영), 3~4줄에서 컷.
- **source**: https://www.inknarrates.com/post/quote-slide (verified — 짧은 인용은 중앙 정렬이 안전, 출처는 작게 하위, 여백 극대화 권고)
- **adaptation_note**: 사진 배경·따옴표 그래픽 복제 금지. `.center-msg` 안에서 왼쪽 `.accent-bar`(블루)를 인용 부호 대용으로 세우고 인용문은 `.cm-title` 축소 변형, 출처는 `.cm-sub` 또는 `.pill`. 결정적 한 구절만 `.hl`.

---

### L-ct-definition — 중앙 개념 정의 / Centered Definition

- **id**: `L-ct-definition`
- **name**: 중앙 개념 정의 / Centered Definition
- **composition_family**: `centered`
- **composition_shape**: `solo-center`
- **info_shapes**: `[concept]`
- **when_to_use**: 하나의 용어·개념을 중앙에 크게 세우고 그 정의를 한두 문장으로 붙여 "A란 무엇인가"를 못박을 때.
- **when_to_avoid**: 두 개념을 대비·비교할 때(→ contrast·comparison), 또는 정의가 3문장 넘게 길어 콜아웃이 5줄을 넘을 때(→ top-down 본문). 절차 설명이면 vertical-flow.
- **capacity**: 용어(cm-title) 1~3어 + 상위 라벨(cm-sub) ≤5어 + 정의 콜아웃 ≤2문장(22~24px에서 3~4줄) + 특성 `.pill` 0~3개.
- **built_on**: `.center-msg-b` · `.cm-sub`(용어 분류 라벨) · `.cm-title`(용어, `.hl`) · `.callout.blue`(정의) · `.pill`(특성 태그, 선택)
- **content_slots**: `sub`, `title`, `definition`, `pills?`
- **sketch**:
```
┌──────────────────────────────────────────────┐
│  s-head ─────────────────────────────          │
│                                                │
│            상위 분류 라벨 (cm-sub)             │
│              바이브코딩                         │  ← cm-title, .hl
│                                                │
│   [ 정의: 의도를 자연어로 말하면 도구가        │  ← callout.blue, 22~24px
│     코드를 구성하는 작업 방식. (≤2문장) ]      │
│        [·특성A] [·특성B] [·특성C]              │  ← pill 0~3
│                                                │
└──────────────────────────────────────────────┘
```
- **coded**: no
- **density_note**: 정의 콜아웃 본문 22px 이상(center 문맥 24px 허용), 3~4줄에서 컷. pill은 15px지만 라벨 보조라 하한 예외 아님 — 핵심 정의는 콜아웃이 담당.
- **source**: https://www.prezent.ai/slides/definition (verified — 용어 + 간결한 정의 + 예시/맥락을 구조화해 시각적으로 담는 정의 슬라이드 포맷 확인)
- **adaptation_note**: 템플릿 마켓의 카드 스타일 복제 금지. `.center-msg-b`의 sub=분류, title=용어(핵심어 `.hl`), 정의는 `.callout.blue` 한 개로 2문장 캡. 특성은 `.pill` 최대 3개로 나열하되 정의 본문을 대체하지 않게.

---

### L-ct-figure — 중앙 단일 도해 / Centered Single Figure

- **id**: `L-ct-figure`
- **name**: 중앙 단일 도해 / Centered Single Figure
- **composition_family**: `centered`
- **composition_shape**: `stage-figure`
- **info_shapes**: `[concept, structure]`
- **when_to_use**: 하나의 개념/구조를 설명하는 도해(코드-viz·SVG) 한 개를 중앙에 세우고 제목 한 줄 + 캡션으로 감쌀 때.
- **when_to_avoid**: 도해가 주인공이라 라벨만 남고 텍스트 프레임이 불필요할 때(→ diagram-centric). 도해가 없이 글만 있으면 `L-ct-statement`/`L-ct-definition`. 여러 도해 병치는 grid-mosaic.
- **capacity**: 제목 1행(≤10어) + 도해 1개(노드/요소 ≤6개, 높이 ≤440px·폭 ≤760px) + 캡션 ≤2줄. 도해는 1개만.
- **built_on**: `.center-msg`(상단 축소 `.cm-title` 제목) + 중앙 도해 **element**(charts.md의 코드-viz/SVG fragment를 얹음, 예 `D-*`) + 캡션은 `.cm-sub`/gray-700
- **content_slots**: `title`, `figure`, `caption?`
- **sketch**:
```
┌──────────────────────────────────────────────┐
│  s-head ─────────────────────────────          │
│         제목 한 줄 (cm-title 축소)             │
│              ┌───────────────┐                 │
│              │   단일 도해     │                │  ← 중앙 코드-viz/SVG
│              │  (≤6 요소)     │                 │     좌우 대칭 여백
│              └───────────────┘                 │
│          캡션 한두 줄 (gray-700)               │
│                                                │
└──────────────────────────────────────────────┘
```
- **coded**: no
- **density_note**: 도해 폭 760px·높이 440px로 잡으면 제목(위)·캡션(아래) 합쳐 720px 안에 세로 스크롤 없이 안착. 캡션은 gray-700 22px 이상.
- **source**: https://www.storydoc.com/presentation-slides/hero-slide (verified — 지배적 중앙 비주얼 + 볼드 헤드라인 + 간결 서브타이틀 조합으로 단일 임팩트 구성)
- **adaptation_note**: 스톡 히어로 이미지 복제 금지 — `<img>` 대신 코드-viz/SVG element를 중앙에 배치(규격 §7 코드-viz 규칙). 도해 fragment는 charts.md에서 별도 카탈로그(element_vs_slide 분리), 이 레이아웃은 그 위에 제목·캡션 프레임만 제공.

---

### L-ct-concentric — 중앙 동심원 / Centered Concentric

- **id**: `L-ct-concentric`
- **name**: 중앙 동심원 / Centered Concentric
- **composition_family**: `centered`
- **composition_shape**: `stage-figure`
- **info_shapes**: `[containment]`
- **when_to_use**: 한 요소가 다른 것에 완전히 속하는 부분-전체/동심 위계를 중앙 동심원으로 보이고, 오늘의 초점 링을 강조할 때.
- **when_to_avoid**: 두 집합이 부분만 겹칠 때(→ venn), 대응·연결 관계일 때(→ mapping), 순서가 있는 절차일 때(→ flow). 링이 5겹 넘으면 판독 붕괴 → 부적합.
- **capacity**: 링 ≤4겹 + 중심 1개 + 각 링 라벨 ≤4어 + 제목 1행(선택). 강조 링 1개만 블루, 나머지 회색.
- **built_on**: `.center-msg` + 중앙 동심원 **element**(charts.md `D-concentric` fragment) + 제목 `.cm-title`(축소) + 링 라벨은 도해 내부 텍스트
- **content_slots**: `title?`, `concentric_diagram`, `ring_labels`
- **sketch**:
```
┌──────────────────────────────────────────────┐
│  s-head ─────────────────────────────          │
│          제목 한 줄 (선택)                     │
│                ╭─────────────╮                 │
│              ╭─┤  외곽 링    ├─╮               │  ← ≤4겹
│              │ │ ╭───────╮   │ │               │
│              │ │ │ 중심  │   │ │               │  ← 초점 링만 블루
│              │ │ ╰───────╯   │ │               │
│              ╰─┤            ├─╯               │
│                ╰─────────────╯                 │
└──────────────────────────────────────────────┘
```
- **coded**: no
- **density_note**: 동심원 지름 ≤440px로 잡아 720px 세로 안착. 링 라벨은 각 링 위/옆에 배치, 캡션 하한(22px) 유지. 강조는 블루 1겹으로 제한.
- **source**: https://slidemodel.com/templates/three-concentric-circles-powerpoint-diagram/ (verified — 중심 개념을 안쪽 원에 두고 바깥 링이 관련·주변을 감싸는 포함 위계, 링별 강조 슬라이드 방식 확인)
- **adaptation_note**: 템플릿 색·그림자 복제 금지. `D-concentric` 코드/SVG element를 `.center-msg` 중앙에 얹고, 강조 링만 `--blue`·나머지 `--surface`/`--periwinkle`(색 문법). 도해는 charts.md에서 element_vs_slide로 독립 선언, 이 레이아웃은 중앙 무대와 제목만 담당.

---

### L-ct-pyramid — 중앙 위계 피라미드 / Centered Pyramid

- **id**: `L-ct-pyramid`
- **name**: 중앙 위계 피라미드 / Centered Pyramid
- **composition_family**: `centered`
- **composition_shape**: `stage-figure`
- **info_shapes**: `[structure, containment]`
- **when_to_use**: 층위가 있는 위계·구성(토대→상위)을 중앙 피라미드로 세우고, 각 층에 짧은 라벨·우측 콜아웃을 붙일 때.
- **when_to_avoid**: 층 간 관계가 위계가 아니라 순환·흐름일 때(→ cycle·flow), 네트워크·매트릭스형 구조일 때(→ diagram-centric). 층이 5단 넘으면 라벨이 뭉개져 부적합.
- **capacity**: 층 ≤4단 + 각 층 라벨 ≤4어 + 우측 콜아웃 각 ≤1줄(선택) + 제목 1행(선택).
- **built_on**: `.center-msg` + 중앙 피라미드 **element**(charts.md `D-pyramid` fragment) + 층 라벨은 도해 내부 · 우측 주석은 `.callout`(짧게) · 강조 층 `--blue`
- **content_slots**: `title?`, `pyramid_diagram`, `level_labels`, `side_notes?`
- **sketch**:
```
┌──────────────────────────────────────────────┐
│  s-head ─────────────────────────────          │
│          제목 한 줄 (선택)                     │
│                  ╱╲                            │
│                 ╱ 3╲   ── 콜아웃: 상위 한 줄   │  ← ≤4단
│                ╱────╲                          │
│               ╱  2   ╲  ── 콜아웃: 중간 한 줄  │
│              ╱────────╲                        │
│             ╱    1     ╲ ── 콜아웃: 토대 한 줄 │
│            ╱────────────╲                      │
└──────────────────────────────────────────────┘
```
- **coded**: no
- **density_note**: 피라미드 높이 ≤440px·밑변 ≤520px로 잡고 우측 콜아웃은 한 줄씩. 층 라벨·콜아웃 모두 22px 이상. 강조 층 1개만 블루.
- **source**: https://slidemodel.com/templates/3-level-pyramid-diagram-powerpoint-template/ (verified — 단일 중앙 피라미드 3층 위계, 층별 텍스트박스·개별 강조로 점증 설명 확인)
- **adaptation_note**: 3D·그림자 템플릿 복제 금지. `D-pyramid` 코드/SVG element를 `.center-msg` 중앙에 배치, 각 층 색은 `--surface`/`--periwinkle`·강조 층만 `--blue`. 우측 주석은 `.callout`을 한 줄로 압축(관계 커넥터 `→` 없이 위계는 도해 자체로). 도해는 charts.md에서 element_vs_slide 분리.

---

## 커버 요약 (이 파일 내부 감사용)

- 항목 7개: `L-ct-statement` · `L-ct-question` · `L-ct-quote` · `L-ct-definition` · `L-ct-figure` · `L-ct-concentric` · `L-ct-pyramid`
- info_shapes 커버: `declaration`(3) · `concept`(2) · `containment`(2) · `structure`(2) — 패밀리 정의의 4개 모양 전부 커버.
- 전 항목 `when_to_avoid` 명시, `source`는 열림 확인(verified) 1개 이상.
