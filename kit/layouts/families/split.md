# split (좌우분할) — 좌우 비대칭 구도: 한쪽은 글 컬럼, 반대쪽은 시각물 하나. 방향(좌글·우글)을 분산해 편향을 막고, 희소하게·비연속으로만 쓴다.

> composition_family=`split` 항목 4개. 방향 분산: 좌글 2(L-sp-anchor-left, L-sp-golden-left) + 우글 2(L-sp-visual-lead, L-sp-rule-right).
> 주로 맞는 정보 모양: `concept` · `comparison`. split은 어떤 모양에서도 역인덱스 1순위로 올리지 않는다(규격 §6).

---

### L-sp-anchor-left — 좌측 글 앵커 / Left Anchor Split

- **id**: `L-sp-anchor-left`
- **name**: 좌측 글 앵커 / Left Anchor Split
- **composition_family**: `split`
- **composition_shape**: `split-asym`
- **info_shapes[]**: `[concept]`
- **when_to_use**: 하나의 개념을 좌측 글 컬럼에서 서술하고, 우측에 그 개념을 잡아주는 시각물(다이어그램·이미지) 하나를 붙일 때. 글이 주(主), 시각이 그 보조 닻일 때.
- **when_to_avoid**: 항목이 3개 이상 병렬 나열이면(→ grid-mosaic) · 시각물이 주인공이면(→ diagram-centric) · 좌우 대등 비교면(→ comparison-symmetric) · 직전 슬라이드가 이미 split이면(연속 금지).
- **capacity**: 좌 컬럼 560px 기준 — eyebrow 1 + 제목 ≤10어 + 본문 22px 4~5줄 + 콜아웃 ≤1. 우 시각물은 초점 하나(단일 다이어그램 또는 이미지 1). 우측에 캡션 ≤1줄.
- **built_on**: `.s-head`, `.s-body-wrap`(좌 컬럼 left:64 top:132 width:560), `.s-eyebrow`, `.s-title`(+`.hl`), `.s-body`, `.callout`; 우측은 `.s-full` 영역 우반부에 시각 fragment 1개 얹음(right:64 정렬).
- **content_slots[]**: eyebrow, title, body, callout(선택), visual(우), caption(선택)
- **sketch**:
```
┌───────────────────────────────────────────┐
│ [로고] 브랜드 ───────────────────── 팀명    │
│                                             │
│  EYEBROW                    ┌────────────┐  │
│  개념 제목 한 줄            │            │  │
│  ───(accent)               │   시각물   │  │
│  본문 설명 4~5줄이          │  (초점 1)  │  │
│  좌측 560px 컬럼에          │            │  │
│  담긴다. keep-all.          └────────────┘  │
│  [파란 콜아웃 1]              캡션 ≤1줄     │
└───────────────────────────────────────────┘
   ← 좌: 글(主)          우: 시각(보조 닻) →
```
- **coded**: no
- **density_note**: 좌 컬럼 폭 560px·본문 22px/1.78에서 한 줄 ≈24~27자(keep-all), 제목/eyebrow 포함 세로 여유상 본문 5줄이 상한. 우 시각은 세로 ≈480px·가로 ≈540px 박스 안에 하나만—붐비면 시각을 element 카탈로그로 분리.
- **source**: https://www.slidewhizz.com/post/asymmetrical-layouts-in-presentations (WebFetch 확인 2026-07-12 · 열림 · verified) — 비대칭 균형: 한쪽 무거운 요소를 반대쪽 여백·대비로 상쇄, "의도된" 배치로 읽힘.
- **adaptation_note**: 원본은 웹/슬라이드용 자유 비대칭. 재표현 시 원본 복제 없이 deck.css 격자에 고정 — 좌측을 `.s-body-wrap`(560px 고정 컬럼)으로 못박고 우측 시각을 그 여백에 앉힌다. 무게 균형은 원본의 "다른 크기·색"이 아니라 토큰 문법으로: 강조는 블루 1곳(`.hl` 또는 콜아웃), 우 시각은 `--surface` 패널 위에 단색 다이어그램. 40~50대 하한(본문 22px)이 좌 컬럼 줄수를 강제하므로 원본보다 글을 덜 담고 여백을 더 준다.

---

### L-sp-golden-left — 좌측 글 · 황금비 스트립 / Golden 62·38 Left

- **id**: `L-sp-golden-left`
- **name**: 좌측 글 · 황금비 스트립 / Golden 62·38 Left
- **composition_family**: `split`
- **composition_shape**: `split-asym`
- **info_shapes[]**: `[comparison, concept]`
- **when_to_use**: 좌측 글이 두 대안을 짧게 견주거나(어느 쪽 권함) 한 개념을 서술하고, 우측의 좁은 세로 스트립(38%)에 인물 이미지·세로 미니지표·수직 대비 요소를 세울 때. 62/38의 뚜렷한 주-종 위계가 필요할 때.
- **when_to_avoid**: 좌우가 대등해야 하는 정식 비교면(→ comparison-symmetric 2패널) · 우측에 넣을 게 표·여러 계열이라 좁은 스트립에 안 들어갈 때 · 시각이 주인공이면(→ diagram-centric) · split 연속·과다 시.
- **capacity**: 좌 글 62%(≈760px 영역 중 텍스트 560px) — 제목 ≤10어 + 본문 22px 5~6줄, 또는 2행 비교 요지(각 ≤2줄). 우 스트립 38%(≈380px) — 세로 이미지 1 또는 데이터점 ≤2개짜리 세로 미니-viz 1. 표 금지(좁아서 17px 하한 붕괴).
- **built_on**: `.s-body-wrap`(좌), `.s-eyebrow`, `.s-title`, `.s-body`(`strong`→블루), 우측은 `.s-full` 우측 380px에 세로 fragment(이미지 또는 `.card.surface` 세로 스택); 대비 강조는 블루/코랄 토큰.
- **content_slots[]**: eyebrow, title, body(또는 2행 비교), strip_visual(우, 세로), micro_caption(선택)
- **sketch**:
```
┌───────────────────────────────────────────┐
│ [로고] 브랜드 ───────────────────── 팀명    │
│                                    ┌──────┐ │
│  EYEBROW                           │      │ │
│  제목 한 줄 (권함: B)              │ 세로 │ │
│  ───                               │ 스트 │ │
│  본문/비교 요지 5~6줄.             │  립  │ │
│  strong=블루 강조.               │ 38%  │ │
│  좌 62%가 지배, 우 38%가 종속.     │      │ │
│                                    └──────┘ │
└───────────────────────────────────────────┘
     ← 62% 글(主)              38% 세로시각 →
```
- **coded**: no
- **density_note**: 우 스트립 폭 ≈380px는 본문 22px 두 단어폭—문장 넣지 말고 이미지/세로지표만. 좌 62%는 본문 6줄이 상한(제목·eyebrow 포함 720px 세로 여유). 비교 요지를 2행으로 쓸 땐 각 행 앞에 `.pill` 라벨 + 본문 ≤2줄.
- **source**: https://slidemodel.com/golden-ratio/ (WebFetch 확인 2026-07-12 · 열림 · verified) — 황금비 1:1.618로 캔버스/레이아웃 분할, 1600px÷1.618≈989의 주-종 분할 예시. 62/38 주-종 위계는 이 비율의 직접 산물.
- **adaptation_note**: 원본은 로고·캔버스 비율 도구 설명. 복제 없이 1280 캔버스에 62/38을 근사 — 좌 텍스트 컬럼 560px + 우 스트립 ≈380px(합 940px, 좌우 여백 64+가운데 gap). 황금비 "느낌"만 차용하고 픽셀은 deck.css 격자에 맞춰 반올림. 우 스트립은 원본의 장식이 아니라 정보 요소(세로 지표/인물)로 재기능화하고, 강조 색은 블루 1곳 규칙 유지.

---

### L-sp-visual-lead — 좌측 시각 리드 · 우측 글 / Visual-Lead Right Text

- **id**: `L-sp-visual-lead`
- **name**: 좌측 시각 리드 · 우측 글 / Visual-Lead Right Text
- **composition_family**: `split`
- **composition_shape**: `split-asym`
- **info_shapes[]**: `[concept]`
- **when_to_use**: 시선을 먼저 좌측 시각물에 앉히고 우측 글 컬럼에서 그 개념을 풀어줄 때. 방향을 우글로 잡아 "항상 우측 시각" 편향을 상쇄해야 할 때.
- **when_to_avoid**: 시각이 라벨만 있고 사실상 주인공이면(→ diagram-centric) · 우측에 넣을 항목이 격자로 많으면(→ grid-mosaic) · 좌우 대등 비교면(→ comparison-symmetric) · 직전이 split이면.
- **capacity**: 좌 시각 ≈48%(≈540px) 초점 하나. 우 글 컬럼 ≈480~520px — eyebrow 1 + 제목 ≤9어 + 본문 22px 4~5줄 + 콜아웃 ≤1.
- **built_on**: `.s-head`, `.s-full`(좌반부에 시각 fragment), 우측은 `.s-full` 안 우측 앵커 텍스트 스택(right:64, width≈500)으로 `.s-eyebrow`/`.s-title`/`.s-body`/`.callout` 재사용. `.s-body-wrap`(좌 고정)은 쓰지 않고 미러링.
- **content_slots[]**: visual(좌), eyebrow, title, body, callout(선택)
- **sketch**:
```
┌───────────────────────────────────────────┐
│ [로고] 브랜드 ───────────────────── 팀명    │
│  ┌────────────┐                             │
│  │            │   EYEBROW                   │
│  │   시각물   │   개념 제목 한 줄           │
│  │  (초점 1)  │   ───(accent)               │
│  │            │   본문 설명 4~5줄이         │
│  └────────────┘   우측 컬럼에 담긴다.       │
│    캡션 ≤1줄      [파란 콜아웃 1]           │
└───────────────────────────────────────────┘
   ← 좌: 시각(리드)        우: 글(主) →
```
- **coded**: no
- **density_note**: 우 텍스트 컬럼은 미러 배치라 폭이 좌 `.s-body-wrap`(560)보다 좁은 ≈500px—본문 한 줄 ≈22자, 5줄 상한. 좌 시각은 세로 ≈480px에 초점 하나. 우측 텍스트는 flush-left 유지(오른쪽 정렬 금지, keep-all 가독성).
- **source**: https://speckyboy.com/asymmetrical-split-screens-web-design/ (WebFetch 확인 2026-07-12 · 열림 · verified) — 비대칭 스플릿: 한쪽이 뚜렷이 크고, 좌측이 시선 시작점이라 주 콘텐츠가 오나, 방향은 무게 배분으로 의도 설계.
- **adaptation_note**: 원본은 좌측을 주 콘텐츠로 두는 웹 스플릿. 여기선 방향 분산 목적상 미러 — 좌를 시각 리드, 우를 글로 뒤집는다. deck.css `.s-body-wrap`은 좌 고정이라 그대로 못 쓰고, 우측 텍스트를 `.s-full` 안 우측 앵커 컨테이너(width≈500, right:64)로 새로 앉힌다. 복제 없이 토큰만: 시각은 `--surface` 위 단색, 강조 블루 1곳. 본문 22px 하한이 우 컬럼 줄수를 5줄로 제한.

---

### L-sp-rule-right — 좌 시각 · 세로 룰 · 우 글 / Ruled Panel Right Text

- **id**: `L-sp-rule-right`
- **name**: 좌 시각 · 세로 룰 · 우 글 / Ruled Panel Right Text
- **composition_family**: `split`
- **composition_shape**: `split-asym`
- **info_shapes[]**: `[comparison, concept]`
- **when_to_use**: 좌측에 고립·정제된 시각 하나를 세로 구분 룰로 딱 끊고, 우측 flush-left 글에서 개념 서술 또는 짧은 견줌을 할 때. 스위스풍 격자·명료한 경계가 필요할 때(우글 방향).
- **when_to_avoid**: 좌우 요소가 대등해 룰이 "대칭 2패널"처럼 읽혀야 하면(→ comparison-symmetric) · 시각이 라벨만 있고 주인공이면(→ diagram-centric) · 여러 항목 격자면(→ grid-mosaic) · split 연속.
- **capacity**: 좌 시각 패널 ≈48% 고립 요소 하나(이미지·기하·단일 다이어그램). 우 글 ≈480px — eyebrow 1 + 제목 ≤10어 + 본문 22px 4~5줄. 가운데 1px `--line` 세로 룰. 비교로 쓸 땐 우측 2행 각 ≤2줄.
- **built_on**: `.s-full`(좌 시각 패널), 가운데 세로 구분선(`--line` 1px 룰), 우측 텍스트 스택 `.s-eyebrow`/`.s-title`/`.s-body`(right:64, width≈480), 필요 시 `.pill` 비교 라벨.
- **content_slots[]**: panel_visual(좌), rule(중앙), eyebrow, title, body(또는 2행 비교)
- **sketch**:
```
┌───────────────────────────────────────────┐
│ [로고] 브랜드 ───────────────────── 팀명    │
│  ┌────────────┐│                            │
│  │            ││  EYEBROW                   │
│  │   고립된   ││  개념/견줌 제목            │
│  │   시각     ││  ───                       │
│  │  (단일)    ││  본문 flush-left           │
│  │            ││  ragged-right 4~5줄.       │
│  └────────────┘│  좌우를 세로 룰이 끊음.    │
│         세로 룰 →│                          │
└───────────────────────────────────────────┘
   ← 좌: 시각 패널    │룰│   우: 글(主) →
```
- **coded**: no
- **density_note**: 세로 룰은 `--line`(#E5E8F0) 1px—시선 경계만, 색 강조 아님. 우 글 컬럼 ≈480px에 본문 22px 5줄 상한, 제목은 `.s-title` 44px 2줄까지. 좌 패널 시각은 하나만—여러 요소면 element 카탈로그로 분리하고 이 슬라이드엔 대표 하나.
- **source**: https://www.printmag.com/featured/swiss-style-principles-typefaces-designers/ (WebFetch 확인 2026-07-12 · 열림 · verified) — 스위스 스타일: 수학적 격자, 비대칭 배치, 사진>일러스트, 명료·객관. 세로 격자 분할과 고립된 강한 시각이 원리적 뿌리.
- **adaptation_note**: 원본은 스위스 격자 이론(룰·flush-left·고립 이미지). 복제 없이 원리만 차용 — 가운데 `--line` 세로 룰로 좌 시각/우 글을 끊고, 우 텍스트는 flush-left ragged-right(오른정렬 금지). 구조·주 강조는 deck.css의 `--blue`로 통일한다. 우글 방향이라 텍스트 컬럼을 우측 앵커로 미러 배치, 40~50대 하한(22px)에서 우 컬럼 줄수 5줄을 수용량 경고로 사용한다.
