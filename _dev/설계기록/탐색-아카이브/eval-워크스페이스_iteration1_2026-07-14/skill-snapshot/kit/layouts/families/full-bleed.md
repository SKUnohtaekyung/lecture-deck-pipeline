# full-bleed — 여백 없이 화면을 꽉 채우는 단일 요소(큰 문장·큰 숫자·인용·풀블리드 배경). 컬럼 분할 없음.

> 이 패밀리는 하나의 요소로 캔버스를 지배한다. 컬럼을 나누지 않고, 텍스트/숫자/이미지 중 **하나**가 1280×720을 채운다.
> 주로 맞는 정보 모양: `declaration` · `concept` · `numeric`(big-number) — 인용은 강한 한 문장이므로 `declaration`으로 취급.
> 색 문법 준수: 강조는 `--blue` 1곳, 텍스트 `word-break:keep-all`. 큰 디스플레이 타입이라 본문 하한(22px)은 자동 충족되며, 부속 텍스트(캡션·출처·서브)만 하한을 지키면 된다.

---

### L-fb-statement — 큰 선언 / Full-bleed Statement

- **id**: `L-fb-statement`
- **name**: 큰 선언 / Full-bleed Statement
- **composition_family**: `full-bleed`
- **info_shapes[]**: `[declaration]`
- **when_to_use**: 한 문장짜리 강한 주장·선언으로 좌중을 멈추게 할 때. 파트의 논지를 못 박는 순간.
- **when_to_avoid**: 담을 항목이 둘 이상이거나, 문장을 뒷받침할 데이터·목록·시각이 필요할 때. 설명이 붙어야 이해되는 개념이면 `concept` 계열로.
- **capacity**: 디스플레이 문장 ≤12어(2~3줄, 88~120px). `.hl` 블루 강조 또는 민트 강조 프리미티브를 문맥에 맞게 사용한다. 선택적 eyebrow 1줄(≤4어). 그 외 요소 없음.
- **built_on**: `.s-full` 확장(중앙 정렬 flex), `.center-msg`/`.cm-title`(52px 상향), `.s-eyebrow`, `.hl`
- **content_slots[]**: eyebrow(선택), statement, hl-span(강조 어절)
- **sketch**:
```
┌──────────────────────────────────────────────┐ 1280
│  [EYEBROW]                                     │
│                                                │
│        측정하지 않으면                          │
│        고칠 수 없다.  ← .hl 블루 1곳          │
│                                                │
│                                            720 │
└──────────────────────────────────────────────┘
   중앙 정렬 · 컬럼 분할 없음 · 단일 문장이 캔버스 지배
```
- **coded**: no
- **density_note**: 문장은 88px+ 디스플레이라 본문 하한 자동 충족. eyebrow는 19px 하한 유지. 12어 초과 시 3줄 넘겨 세로 넘침 위험 → 어절 수로 캡.
- **source**: https://www.pptx.gallery/how-to/image-focused-full-bleed-layouts — verified (WebFetch 2026-07-12, "center text on overlay: the classic approach … for impactful statements")
- **adaptation_note**: 원본은 이미지 위 흰 텍스트 오버레이. 여기서는 이미지 없이 `--surface` 또는 흰 배경 + `--black` 잉크로 재표현. 오버레이 대신 순수 타이포. `.cm-title`을 88~120px로 상향하고 강조 어절만 `<span class="hl">`(블루). 드롭섀도 대신 배경 대비로 가독 확보.

---

### L-fb-bignum — 풀블리드 큰 숫자 / Full-bleed Big Number

- **id**: `L-fb-bignum`
- **name**: 풀블리드 큰 숫자 / Full-bleed Big Number
- **composition_family**: `full-bleed`
- **info_shapes[]**: `[numeric]`
- **when_to_use**: 단 하나의 인상적 지표·통계를 각인시킬 때(성장률·규모·비율 한 개). 비교 없이 그 수치 자체가 메시지.
- **when_to_avoid**: 수치가 2개 이상이거나 추세·비교·부분-전체를 보여야 할 때(그건 chart 계열: bar/line/pie). 맥락 설명이 길게 필요할 때.
- **capacity**: 큰 숫자 1개(≤5자, 200~320px) + 단위/기호 + 라벨 1줄(≤8어) + 선택적 캡션 1줄(≤14어). 그 이상 없음.
- **built_on**: `.s-full` 확장(중앙 정렬), `.cm-title`(숫자용 200px+ 상향), `.cm-sub`(라벨), `.s-eyebrow`, `.hl`
- **content_slots[]**: eyebrow(선택), big-number, unit, label, caption(선택)
- **sketch**:
```
┌──────────────────────────────────────────────┐
│  [EYEBROW: 2026 실측]                          │
│                                                │
│            73%    ← 200~320px, .hl 블루       │
│      진단이 24시간 내 이뤄진 비율               │
│      (전년 41% → 올해 73%)  ← 캡션 선택         │
│                                                │
└──────────────────────────────────────────────┘
   단일 숫자가 무대 지배 · 컬럼 없음
```
- **coded**: no
- **density_note**: 숫자는 200px+라 하한 무관. 라벨은 `.cm-sub`(23px+), 캡션은 `--gray-700` 22px 하한 유지. 숫자 5자 초과(예: 1,234,567)면 가로 넘침 → 자릿수 압축(1.2M)으로 대응.
- **source**: https://www.beautiful.ai/templates/big-number-template — verified (WebFetch 2026-07-12, "add just one statistic and increase the text scale … keep it to one or two words"); 보강 https://www.storydoc.com/slides/big-numbers-slide — verified (WebFetch 2026-07-12, "prominent headline with bold numbers … single-focus")
- **adaptation_note**: 원본은 아이콘·이미지 동반 허용. 여기서는 아이콘 배제, 순수 숫자+라벨로 재표현. 숫자에 `.hl`(블루) 1곳만, 라벨은 `--ink`. 증감 캡션이 있으면 블루 대신 `--mint-deep`(상승 안전) / `--coral-deep`(하락 경고) 색 문법으로 방향 신호. 데이터가 시계열이면 이 항목이 아니라 line 차트로 가라는 경계를 when_to_avoid에 명시.

---

### L-fb-quote — 풀블리드 인용 / Full-bleed Pull Quote

- **id**: `L-fb-quote`
- **name**: 풀블리드 인용 / Full-bleed Pull Quote
- **composition_family**: `full-bleed`
- **info_shapes[]**: `[declaration, concept]`
- **when_to_use**: 권위 있는 인용·증언 한 줄로 논지를 대변할 때. 화자의 말이 곧 슬라이드가 되는 순간.
- **when_to_avoid**: 인용이 길어 여러 문장이 되거나, 여러 사람의 말을 나열/대비해야 할 때(그건 `contrast`/`classification`). 인용을 분석·반박해야 하면 본문 레이아웃으로.
- **capacity**: 인용문 ≤30어(3~4줄, 48~64px) + 큰 따옴표 그래픽 + 출처 귀속 1줄(이름·직함, ≤12어). 인용 2개 이상 불가.
- **built_on**: `.s-full` 확장, `.cm-title`(인용용 48~64px), `.cm-sub`(귀속), `.hl`(핵심 어절), 오버사이즈 `"` 장식
- **content_slots[]**: open-quote-mark, quote-body, hl-span(선택), attribution
- **sketch**:
```
┌──────────────────────────────────────────────┐
│   ❝                                            │
│   완벽한 계획보다                               │
│   측정 가능한 실행이 낫다.  ← 48~64px           │
│                                                │
│              — 김지은, 데이터 리드              │
└──────────────────────────────────────────────┘
   따옴표 그래픽 + 인용 + 귀속 · 단일 블록
```
- **coded**: no
- **density_note**: 인용 48px+로 하한 무관. 귀속은 `--gray-700` 22px 하한. 오버사이즈 따옴표는 `--periwinkle`(비강조 보조)로 배경화, 본문 가독 침범 금지. 30어 초과 시 4줄 넘겨 넘침 → 어절 캡.
- **source**: https://creativepro.com/how-to-attract-attention-pull-quotes/ — verified (WebFetch 2026-07-12, "larger sizing … oversized quotation marks as graphic elements … generous line spacing")
- **adaptation_note**: 원본은 노랑 하이라이트·손글씨 등 자유로운 처리. 여기서는 색 문법을 지켜 핵심 어절만 `.hl`(블루), 나머지는 `--ink`. 하이라이트 대신 굵기/색 대비로 강조. 오버사이즈 따옴표는 `--periwinkle` 장식 글리프로 재표현(원본 이미지 미복제). 라인하이트 1.3~1.4로 조여 디스플레이 인용 리듬 확보.

---

### L-fb-photo — 풀블리드 사진 오버레이 / Full-bleed Photo Overlay

- **id**: `L-fb-photo`
- **name**: 풀블리드 사진 오버레이 / Full-bleed Photo Overlay
- **composition_family**: `full-bleed`
- **info_shapes[]**: `[declaration, concept]`
- **when_to_use**: 화면 전체를 덮는 이미지가 정서·맥락을 만들고, 그 위에 한 줄 헤드라인이 메시지를 얹을 때. 장면 전환·분위기 각인.
- **when_to_avoid**: 이미지가 없거나 저해상도라 텍스트 대비를 못 낼 때, 또는 이미지 위에 여러 줄/여러 요소를 얹어야 할 때(가독 붕괴). 데이터·목록은 금물.
- **capacity**: 풀블리드 이미지 1장 + 헤드라인 1줄(≤10어, 64~88px) + 선택적 eyebrow(≤4어). 오버레이 텍스트는 단일 블록만.
- **built_on**: `.s-full` 확장(이미지 absolute 풀블리드), 반투명 오버레이(`--ink` 40~60%), `.cm-title`(흰 텍스트), `.s-eyebrow`
- **content_slots[]**: bg-image, scrim-overlay, eyebrow(선택), headline
- **sketch**:
```
┌──────────────────────────────────────────────┐
│▓▓▓▓▓▓▓▓▓ 풀블리드 이미지 ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│
│▓▓▓▓ (--ink 45% scrim 오버레이) ▓▓▓▓▓▓▓▓▓▓▓▓▓▓│
│▓▓▓  [EYEBROW]                            ▓▓▓▓│
│▓▓▓  현장은 대시보드보다 빠르다  ← 흰 64px  ▓▓▓│
│▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│
└──────────────────────────────────────────────┘
   이미지가 캔버스 전체 · 텍스트 오버레이 단일 블록
```
- **coded**: no
- **density_note**: 헤드라인 64px+ 흰 텍스트. 대비 확보 위해 `--ink` 40~60% scrim 필수(투사 환경 가독). eyebrow는 흰색 19px 하한. 이미지 밝은 영역에 텍스트 겹치면 scrim 농도 상향.
- **source**: https://presentationwiz.biz/2014/06/18/powerpoint-design-trend-white-text-on-full-bleed-image/ — verified (WebFetch 2026-07-12, "white text sufficiently contrasted … subtle drop shadow … edge-to-edge photograph")
- **adaptation_note**: 원본은 PowerPoint 드롭섀도로 대비 확보. 여기서는 raw hex 금지 → 토큰 기반 반투명 scrim(`--ink` alpha)로 재표현. 이미지는 자산 슬롯(bg-image)으로 두고 마크업은 오버레이/텍스트만 규정. 강조는 색 문법상 이미지 위에서 블루가 묻히므로 `.hl` 대신 굵기 대비로 처리.

---

### L-fb-caption-band — 하단 캡션 밴드 / Bottom Caption Band

- **id**: `L-fb-caption-band`
- **name**: 하단 캡션 밴드 / Bottom Caption Band
- **composition_family**: `full-bleed`
- **info_shapes[]**: `[concept, declaration]`
- **when_to_use**: 상단은 이미지/비주얼이 지배하고, 하단 약 30% 밴드에 제목+한 줄 설명을 앉혀 안정적으로 라벨링할 때. 이미지 우세 + 최소 설명.
- **when_to_avoid**: 설명이 두 문단 이상 필요하거나 좌우로 정보를 나눠야 할 때(split/top-down로). 밴드가 화면 절반을 넘겨 이미지가 죽으면 이 구도의 이점 소멸.
- **capacity**: 상단 이미지(≈70%) + 하단 밴드(≈30%): 제목 1줄(≤10어, 34~44px) + 서브 1줄(≤20어, 22~24px). 밴드 안 요소 2개까지.
- **built_on**: `.s-full` 확장(상단 이미지 fill), 하단 밴드(`--ink` 솔리드 또는 90% 오버레이), `.s-title`, `.s-body`
- **content_slots[]**: bg-image, bottom-band, band-title, band-sub
- **sketch**:
```
┌──────────────────────────────────────────────┐
│▓▓▓▓▓▓▓▓▓ 이미지 (상단 ~70%) ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│
│▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│
│▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│
│──────────────────────────────────────────────│
│  현장 데이터 파이프라인  ← 44px 흰 제목        │
│  센서 → 게이트웨이 → 대시보드, 지연 2초 이내   │  ← 하단 밴드 30%
└──────────────────────────────────────────────┘
```
- **coded**: no
- **density_note**: 밴드 안 제목 34px+, 서브는 `.s-body` 22px 하한 준수. 밴드 배경은 `--ink` 솔리드라 흰 텍스트 대비 안정. 서브 20어 초과 시 밴드 2줄→30% 초과 → 어절 캡으로 밴드 높이 고정.
- **source**: https://www.pptx.gallery/how-to/image-focused-full-bleed-layouts — verified (WebFetch 2026-07-12, "bottom-third text band: a dark band across the bottom 30% of the slide, with text inside")
- **adaptation_note**: 원본 "dark band 30%"를 토큰으로: 밴드 배경 `--ink` 솔리드, 텍스트 흰색·`--ice`. 이미지는 bg-image 슬롯. 강조가 필요하면 밴드 안에서만 `.hl`(블루) 1곳 — 밴드가 어두워 블루 대비 성립. L-fb-photo와의 차이: 저건 텍스트가 이미지 위를 떠다니고, 이건 이미지/텍스트를 밴드로 물리 분리(세로 30% 캡).

---

### L-fb-oneword — 한 단어 / Single Word

- **id**: `L-fb-oneword`
- **name**: 한 단어 / Single Word
- **composition_family**: `full-bleed`
- **info_shapes[]**: `[declaration]`
- **when_to_use**: 한 단어(또는 2~3어 짧은 구)를 초대형으로 띄워 개념의 이름·전환어·키워드를 각인시킬 때. 파트 키워드, 한 호흡의 강조.
- **when_to_avoid**: 그 단어를 설명·정의해야 이해되는 경우(→ `concept`, centered), 또는 키워드가 3개 이상 병렬일 때(→ `classification`, grid). 문장이 필요하면 L-fb-statement로.
- **capacity**: 초대형 단어 1개 — 한글 전각 기준 **폰트를 글자수에 맞춰 스케일**(3자≈360px · 4~5자≈220px). **5자 초과(전각) 단어는 이 구도 부적합** → L-fb-statement로. + 선택적 eyebrow/kicker 1줄(≤4어). 부속 문장 없음.
- **built_on**: `.s-full` 확장(중앙), `.cm-title`(240px+ 상향), `.s-eyebrow`, `.hl`
- **content_slots[]**: eyebrow/kicker(선택), word
- **sketch**:
```
┌──────────────────────────────────────────────┐
│                                                │
│         [PART 02 — 실행]  ← eyebrow            │
│                                                │
│           측정          ← 240~360px            │
│                                                │
│                                                │
└──────────────────────────────────────────────┘
   단일 단어가 캔버스 압도 · 여백이 무대
```
- **coded**: no
- **density_note**: 한글 전각 가로폭 ≈ 글자수×폰트px, 가용 폭 1152px → **폰트를 글자수에 맞춰 스케일**(5자면 ≤220px, 3자면 ≤360px; 고정 240~360px 금지). 6자↑는 폭 초과라 이 구도 회피(→ L-fb-statement). eyebrow 19px 하한. 여백 넉넉히 두어 단어를 고립.
- **source**: https://creativepro.com/typographic-guidelines-for-kickass-presentations/ — verified (WebFetch 2026-07-12, "keep text large … more slides with less type … embrace white space"); 보강 https://visme.co/blog/keynote-presentation-examples/ — verified ("most slides contained one word or a short phrase in a big font size")
- **adaptation_note**: 원본 지침(한 단어·큰 폰트·화이트스페이스)을 토큰으로: 배경 흰색/`--surface`, 단어 `--black`, 강조 필요 시 단어 일부만 `.hl`(블루). 장식 배제, 순수 타이포+여백. kicker는 `--blue` eyebrow로 문맥 표시. 이미지·아이콘 없음이 L-fb-photo와의 경계.

---

### L-fb-question — 풀블리드 질문 / Full-bleed Question

- **id**: `L-fb-question`
- **name**: 풀블리드 질문 / Full-bleed Question
- **composition_family**: `full-bleed`
- **info_shapes[]**: `[declaration]`
- **when_to_use**: 수사적 질문 한 줄로 청중의 사고를 열 때("정말 Z할까?"). 도입 훅, 파트 전환의 문제 제기, 답을 다음 슬라이드로 미루는 순간.
- **when_to_avoid**: 질문에 곧바로 답·옵션·데이터를 같은 화면에 붙여야 할 때(→ comparison/numeric). 질문이 여러 개 나열되면 이 구도 아님. 진술이면 L-fb-statement로.
- **capacity**: 질문문 1개(≤14어, 2줄, 72~96px) + 물음표 강조 + 선택적 서브(≤10어, 22~24px). 질문 2개 이상 불가.
- **built_on**: `.s-full` 확장(중앙), `.cm-title`(질문용 72~96px), `.cm-sub`(선택 서브), `.hl`(핵심 어절 또는 `?`)
- **content_slots[]**: question, hl-span(선택), sub(선택)
- **sketch**:
```
┌──────────────────────────────────────────────┐
│                                                │
│      우리는 무엇을                              │
│      측정하지 않고 있나?  ← 72~96px, ? 강조     │
│                                                │
│      (답은 다음 장에)  ← 서브 선택              │
│                                                │
└──────────────────────────────────────────────┘
   단일 질문이 무대 지배 · 중앙 정렬
```
- **coded**: no
- **density_note**: 질문 72px+로 하한 무관. 서브는 `.cm-sub`/`--gray-700` 22px 하한. 14어 초과 시 2줄 넘겨 넘침 → 어절 캡. 물음표 또는 핵심 어절 1곳만 `.hl`(블루)로 시선 유도.
- **source**: https://visme.co/blog/keynote-presentation-examples/ — verified (WebFetch 2026-07-12, "series of what-if questions … thought-provoking prompts … slides are supporting actors, the story is the star")
- **adaptation_note**: 원본은 "what if" 수사 질문으로 청중 반향 유도. 여기서는 질문문을 `.cm-title` 72~96px로 중앙 배치, 물음표나 핵심 어절만 `.hl`(블루). 답을 얹지 않는 게 규율 — 답/데이터를 붙이려는 유혹은 when_to_avoid로 차단. L-fb-statement(진술)와 쌍을 이루되, 종결부호(?)와 열린 사고 유도가 구별점.
