# grid-mosaic — 동급 카드/타일을 격자로 훑는 구도 패밀리(2×2·3×2·4×2·bento·gallery). classification·checklist·comparison 모양에 맞춘 8개 레이아웃.

> 판단 축: [`../../guide/정보모양-taxonomy.md`](../../guide/정보모양-taxonomy.md) · 규격: [`../../guide/카탈로그-규격.md`](../../guide/카탈로그-규격.md) · 토큰: [`../../guide/토큰-치트시트.md`](../../guide/토큰-치트시트.md)
> 이 파일의 모든 항목은 `composition_family = grid-mosaic`. 격자는 `.s-full`(left:64 right:64 top:118) 위에 `.grid-2`/`.grid-3` 또는 card-grid로 얹는다. 1280×720에서 스크롤 없이 성립하는 셀 수·폰트 하한을 capacity에 명시.

---

### L-gm-quad — 2×2 사분면 / 2×2 Quadrant

- **id**: `L-gm-quad`
- **name**: 2×2 사분면 / 2×2 Quadrant
- **composition_family**: `grid-mosaic`
- **info_shapes**: `[classification, comparison]`
- **when_to_use**: 동급 항목이 정확히 4개이고, 각 칸이 서로 독립된 소주제(예: SWOT, 목표·진행·리스크·다음 단계)를 담아 한 화면에서 관계를 동시에 조망하고 싶을 때.
- **when_to_avoid**: 항목이 3개거나 5개↑일 때(격자가 비거나 4×2로 넘어감) · 한 축이 다른 축을 강조해야 할 때(비대칭이 필요하면 bento) · 각 칸이 5줄↑ 본문을 요구할 때.
- **capacity**: 4칸, 각 칸 ~560×230px. 칸당 소제목 ≤6어 + 불릿 3~4개(각 ≤10어) 또는 콜아웃 1개. 본문 22px/1.78에서 칸당 최대 6줄.
- **built_on**: `.s-full` + `.grid-2`(2열, 2행 래핑) · 각 칸 `.card`(+`.surface`) · 상단 `.s-eyebrow`/`.s-title`
- **content_slots**: title, (eyebrow), cell×4 { cell_title, cell_body|cell_bullets }
- **sketch**:
```
┌────────────────────────────────────────────┐
│ EYEBROW                                     │
│ 슬라이드 제목 한 줄                          │
│ ┌─────────────────┐ ┌─────────────────┐    │
│ │ ① 소제목         │ │ ② 소제목         │    │
│ │ • 항목 • 항목    │ │ • 항목 • 항목    │    │
│ └─────────────────┘ └─────────────────┘    │
│ ┌─────────────────┐ ┌─────────────────┐    │
│ │ ③ 소제목         │ │ ④ 소제목         │    │
│ │ • 항목 • 항목    │ │ • 항목 • 항목    │    │
│ └─────────────────┘ └─────────────────┘    │
└────────────────────────────────────────────┘
```
- **coded**: no
- **density_note**: 2행이므로 세로 여유 충분 — 본문 22px 하한 무리 없음. 칸당 6줄을 넘기면 4×2 또는 bento로 분산.
- **source**: https://www.thebricks.com/resources/how-to-make-a-quad-slide-in-powerpoint (verified — 4분면 quad slide 구조·SWOT/상태 사분면 용례 확인) · 보조 https://www.presentationgo.com/presentation/tag/2x2-matrix/
- **adaptation_note**: 원본 PPT 사분면은 색면 4블록. 재표현은 회색 `.surface` 카드 4장을 `.grid-2`로 깔고 구조 제목·추천 기준을 `--blue`, 행동·완료 도형을 민트로 쓴다. 본문은 `--ink`, 사분면 구분은 색면 남용 대신 `.line` 테두리+간격으로 만든다.

---

### L-gm-cards-3x2 — 3×2 카드 격자 / 3×2 Card Grid

- **id**: `L-gm-cards-3x2`
- **name**: 3×2 카드 격자 / 3×2 Card Grid
- **composition_family**: `grid-mosaic`
- **info_shapes**: `[classification]`
- **when_to_use**: 동급 항목이 6개(제품·기능·아이디어·역할)이고 각각 제목+짧은 설명 한 덩어리로 병렬 나열할 때.
- **when_to_avoid**: 항목 간 우열/추천이 핵심일 때(comparison → matrix나 compare-cards) · 각 카드가 이미지 위주일 때(gallery) · 항목이 4개↓라 3열이 비어 보일 때.
- **capacity**: 6카드(3열×2행), 각 ~370×230px. 카드당 제목 ≤5어 + 설명 ≤3줄(본문 22px). 아이콘/번호 배지 1개 여유.
- **built_on**: `.s-full` + `.grid-3`(2행 래핑) · 각 카드 `.card` · 카드 헤더 라벨 + `.s-body`
- **content_slots**: title, (eyebrow), card×6 { card_title, card_desc, (icon|num) }
- **sketch**:
```
┌────────────────────────────────────────────┐
│ 슬라이드 제목                                │
│ ┌────────┐ ┌────────┐ ┌────────┐            │
│ │ ▣ 제목 │ │ ▣ 제목 │ │ ▣ 제목 │            │
│ │ 설명…  │ │ 설명…  │ │ 설명…  │            │
│ └────────┘ └────────┘ └────────┘            │
│ ┌────────┐ ┌────────┐ ┌────────┐            │
│ │ ▣ 제목 │ │ ▣ 제목 │ │ ▣ 제목 │            │
│ │ 설명…  │ │ 설명…  │ │ 설명…  │            │
│ └────────┘ └────────┘ └────────┘            │
└────────────────────────────────────────────┘
```
- **coded**: no
- **density_note**: 3열이라 카드 폭 370px — 제목은 `word-break:keep-all`로 2줄까지, 설명 3줄이 22px 하한의 실질 상한. 넘치면 4개로 줄이거나 2×2로.
- **source**: https://www.presentationgo.com/presentation/rounded-card-grid-powerpoint/ (verified — 6장 라운드 카드 2×3, 제목 바+본문, 병렬 항목/카테고리 용례 확인)
- **adaptation_note**: 원본은 카드마다 다른 색 헤더 바. 재표현은 색을 걷어내고 6장 모두 `.surface` 통일, 강조는 아이콘 슬롯 또는 `.pill` 하나에만 `--blue`. 라운드/그림자는 deck.css `.card` 프리미티브가 흡수해 raw hex 없이 처리.

---

### L-gm-tiles-4x2 — 4×2 조밀 타일 / 4×2 Compact Tiles

- **id**: `L-gm-tiles-4x2`
- **name**: 4×2 조밀 타일 / 4×2 Compact Tiles
- **composition_family**: `grid-mosaic`
- **info_shapes**: `[classification, checklist]`
- **when_to_use**: 동급 항목이 7~8개로 많고 각 타일이 짧은 라벨(+수치나 아이콘) 정도만 담아 한눈에 전체 집합을 훑을 때(로고 월, 지표 타일, 항목 점검).
- **when_to_avoid**: 타일당 설명 문장이 필요할 때(4×2는 폭 275px라 본문 22px가 2줄이면 꽉 참) · 항목이 6개↓일 때(3×2가 덜 빡빡) · 순서·단계가 중요할 때(flow 계열).
- **capacity**: 8타일(4열×2행), 각 ~275×230px. 타일당 라벨 ≤3어 + 보조 1줄(수치·아이콘). 본문 22px에서 라벨 2줄이 상한.
- **built_on**: `.s-full` + card-grid(4열 flex/grid, gap 16) · 각 타일 `.card.surface` · 라벨 `.s-body strong` · 수치 강조는 `.timing`/`.pill`
- **content_slots**: title, tile×8 { label, (metric|icon) }
- **sketch**:
```
┌────────────────────────────────────────────┐
│ 슬라이드 제목                                │
│ ┌────┐ ┌────┐ ┌────┐ ┌────┐                 │
│ │라벨│ │라벨│ │라벨│ │라벨│                 │
│ └────┘ └────┘ └────┘ └────┘                 │
│ ┌────┐ ┌────┐ ┌────┐ ┌────┐                 │
│ │라벨│ │라벨│ │라벨│ │라벨│                 │
│ └────┘ └────┘ └────┘ └────┘                 │
└────────────────────────────────────────────┘
```
- **coded**: no
- **density_note**: 폭이 좁아 본문 22px 하한이 실질 제약 — 타일은 문장이 아니라 라벨/수치용. 문장이 생기면 즉시 3×2 또는 bento로 승격.
- **source**: https://collage.pi7.org/photo-grid-maker (verified — 4×2 프리셋=8셀 균등 타일, 모든 셀 동일 크기/간격 확인) · 보조 https://slidebazaar.com/templates/three-four-column-cards-powerpoint-google-slides/
- **adaptation_note**: 원본 그리드 도구는 사진 셀. 재표현은 사진 대신 텍스트/수치 타일로 — 8장 `.surface` 균등, 간격 16px 통일. 수치가 있으면 타일당 하나만 `--blue`로 크게, 나머지 라벨은 `--ink`. 한 슬라이드 블루 1~2곳 규칙을 위해 강조 타일은 최대 2개.

---

### L-gm-bento — 벤토 비대칭 격자 / Bento Asymmetric Grid

- **id**: `L-gm-bento`
- **name**: 벤토 비대칭 격자 / Bento Asymmetric Grid
- **composition_family**: `grid-mosaic`
- **info_shapes**: `[classification, numeric]`
- **when_to_use**: 동급 항목들 사이에 하나의 대표(히어로) 항목이 있어 큰 타일 1개 + 작은 타일 여럿으로 크기=중요도의 위계를 주고 싶을 때(대표 KPI + 보조 지표/기능).
- **when_to_avoid**: 모든 항목이 완전 동급이라 위계가 없을 때(2×2/3×2가 정직) · 대칭 비교가 목적일 때(comparison-symmetric) · 히어로 타일이 담을 핵심 한 개가 없을 때.
- **capacity**: 5~6타일(히어로 1 = 2열×2행 span + 소타일 3~4). 히어로 ~560×470px: 제목 ≤8어 + 큰 수치/리드 1개. 소타일 ~275×230px: 라벨 ≤3어 + 1줄.
- **built_on**: `.s-full` + card-grid(CSS grid, 히어로 `grid-column/row: span 2`) · 히어로 `.card` + `.cm-sub`류 · 소타일 `.card.surface`
- **content_slots**: title, hero { hero_title, hero_metric|hero_lead }, tile×3~4 { label, metric }
- **sketch**:
```
┌────────────────────────────────────────────┐
│ 슬라이드 제목                                │
│ ┌───────────────────┐ ┌────────┐ ┌────────┐ │
│ │                   │ │ 라벨   │ │ 라벨   │ │
│ │   히어로 타일      │ └────────┘ └────────┘ │
│ │   큰 수치 / 리드   │ ┌────────┐ ┌────────┐ │
│ │                   │ │ 라벨   │ │ 라벨   │ │
│ └───────────────────┘ └────────┘ └────────┘ │
└────────────────────────────────────────────┘
```
- **coded**: no
- **density_note**: 히어로는 세로 span 2라 큰 숫자(big-number)까지 여유. 소타일은 4×2 타일과 같은 하한(라벨/수치). 블루 강조는 히어로 1곳으로 집중.
- **source**: https://www.saasframe.io/blog/the-bento-layout-trend (verified — 크기 가변 타일=위계, 히어로 강조+보조 소타일 배치 원리 확인) · 보조 https://studiomeyer.io/en/blog/bento-grid-layouts
- **adaptation_note**: 원본 벤토는 색·이미지 풍부한 마케팅 타일. 재표현은 히어로만 강조(블루 수치 또는 `.callout.blue`), 소타일은 `.surface` 무채로 눌러 위계를 색이 아닌 크기로 만든다. 이미지 대신 텍스트/수치 — code-viz 원칙에 맞춰 `<img>` 없이 구성.

---

### L-gm-gallery — 갤러리 모자이크 / Gallery Mosaic

- **id**: `L-gm-gallery`
- **name**: 갤러리 모자이크 / Gallery Mosaic
- **composition_family**: `grid-mosaic`
- **info_shapes**: `[classification]`
- **when_to_use**: 이미지/스냅샷이 주인공인 동급 항목 6~8개를 격자로 훑을 때(포트폴리오, 제품 컷, 사례 모음, 팀 소개). 각 타일 = 이미지 + 짧은 캡션.
- **when_to_avoid**: 텍스트 설명이 이미지보다 무거울 때(cards-3x2) · 이미지가 1~2장뿐일 때(centered/split) · 화면 UI 단계 안내일 때(screen-operation).
- **capacity**: 6~8 이미지 타일(3×2 또는 4×2). 타일당 캡션 ≤5어(캡션 `--gray-400` 캡션 톤). 이미지 비율 유지, 타일 ~370×230(3열) 또는 ~275×230(4열).
- **built_on**: `.s-full` + card-grid · 각 타일 이미지 프레임 + 하단 캡션(`.s-body` 축소 또는 caption 톤) · `object-fit:cover`
- **content_slots**: title, tile×6~8 { image, caption }
- **sketch**:
```
┌────────────────────────────────────────────┐
│ 슬라이드 제목                                │
│ ┌────────┐ ┌────────┐ ┌────────┐            │
│ │ [img]  │ │ [img]  │ │ [img]  │            │
│ │ 캡션   │ │ 캡션   │ │ 캡션   │            │
│ └────────┘ └────────┘ └────────┘            │
│ ┌────────┐ ┌────────┐ ┌────────┐            │
│ │ [img]  │ │ [img]  │ │ [img]  │            │
│ │ 캡션   │ │ 캡션   │ │ 캡션   │            │
│ └────────┘ └────────┘ └────────┘            │
└────────────────────────────────────────────┘
```
- **coded**: no
- **density_note**: 캡션은 본문이 아니라 라벨 — 그래도 캡션 폰트가 legibility 캡션 톤을 하회하지 않게. 이미지 6장이면 3×2가 여백 안정, 8장이면 4×2로 조밀.
- **source**: https://slidebazaar.com/templates/mosaic-photo-grid-layout-powerpoint-google-slides/ (verified — 정렬된 사각 이미지 플레이스홀더 모자이크, 포트폴리오/사례/팀 용례 확인) · 보조 https://www.presentations.ai/slide-templates/photo-grid
- **adaptation_note**: 원본은 크기 다른 이미지 모자이크 + 색 오버레이 패널. 재표현은 균등 타일로 정렬(모자이크 불규칙성 대신 `.line` 간격 규칙), 캡션은 무채. 색 오버레이 대신 캡션 텍스트로 정보 전달 — 화면당 블루는 제목 `.hl` 한 곳.

---

### L-gm-checklist — 체크 격자 / Checklist Grid

- **id**: `L-gm-checklist`
- **name**: 체크 격자 / Checklist Grid
- **composition_family**: `grid-mosaic`
- **info_shapes**: `[checklist]`
- **when_to_use**: 점검·준비·규정 항목을 2열 격자로 나열하고 각 항목에 체크(확인)/엑스(미비) 표식을 붙여 상태를 훑을 때(런치 준비도, 규정 점검, 자격 요건).
- **when_to_avoid**: 항목이 순서를 요구할 때(vertical-flow) · 두 대안의 우열 비교일 때(matrix/compare) · 항목이 3개↓라 격자가 불필요할 때(centered 리스트).
- **capacity**: 6~8 항목(2열×3~4행). 항목당 표식 아이콘 1개 + 라벨 ≤10어(본문 22px). 상태 색: `--mint-deep`(확인)·`--red`(미비) 아이콘에만.
- **built_on**: `.s-full` + `.grid-2` · 각 행 아이콘(체크/엑스) + `.s-body` · 확인/미비는 `--mint-deep`/`--red` 규칙색
- **content_slots**: title, item×6~8 { status_icon, label }
- **sketch**:
```
┌────────────────────────────────────────────┐
│ 슬라이드 제목                                │
│ ┌──────────────────┐ ┌──────────────────┐   │
│ │ ✓ 점검 항목 라벨  │ │ ✓ 점검 항목 라벨  │   │
│ │ ✓ 점검 항목 라벨  │ │ ✗ 점검 항목 라벨  │   │
│ │ ✗ 점검 항목 라벨  │ │ ✓ 점검 항목 라벨  │   │
│ │ ✓ 점검 항목 라벨  │ │ ✓ 점검 항목 라벨  │   │
│ └──────────────────┘ └──────────────────┘   │
└────────────────────────────────────────────┘
```
- **coded**: no
- **density_note**: 2열 4행=8항목이 22px 하한의 안정 상한. 라벨이 2줄로 넘치면 행 높이가 커져 8항목이 720을 넘길 수 있으니 6항목으로 축소.
- **source**: https://www.slidesai.io/blog/how-to-create-a-checklist-in-powerpoint (verified — 항목별 체크박스/체크마크 표식, 준비도·규정 리뷰 용례 확인) · 보조 https://www.presentationgo.com/presentation/tag/checklist/
- **adaptation_note**: 원본은 세로 단일 리스트가 흔하나, 6~8항목을 2열 격자로 재배치해 grid-mosaic로 승격. 색은 문법대로 `--mint-deep`=확인·`--red`=미비 아이콘에만, 라벨 텍스트는 `--ink` 유지. 체크박스 3D 클립아트 등 장식은 제거.

---

### L-gm-compare-cards — 비교 카드 격자 / Comparison Card Grid

- **id**: `L-gm-compare-cards`
- **name**: 비교 카드 격자 / Comparison Card Grid
- **composition_family**: `grid-mosaic`
- **info_shapes**: `[comparison]`
- **when_to_use**: 3~4개 대안(요금제·플랜·공급사)을 각각 한 카드(세로 컬럼)로 세우고, 카드마다 동일 항목 행을 체크로 채워 옆으로 견주며 하나를 추천할 때.
- **when_to_avoid**: 대안이 2개뿐이라 대칭 2패널이 나을 때(comparison-symmetric) · 항목×옵션이 조밀한 표가 필요할 때(matrix) · 추천 없이 단순 나열일 때(cards-3x2).
- **capacity**: 3~4 카드 컬럼, 각 ~360×470(3열) 또는 ~270×470(4열). 카드당 헤더(플랜명+가격) + 특징 행 4~6개(각 체크/엑스 + ≤6어). 추천 카드 1개만 `--blue` 테두리 강조.
- **built_on**: `.s-full` + `.grid-3`(또는 4열 card-grid) · 각 카드 `.card`, 헤더 `.pill`, 특징 행 아이콘 + `.s-body` · 추천 카드 블루 보더
- **content_slots**: title, card×3~4 { plan_name, price, feature_row×4~6 { icon, text }, (recommended_flag) }
- **sketch**:
```
┌────────────────────────────────────────────┐
│ 슬라이드 제목                                │
│ ┌────────┐ ┌────────┐ ┌━━━━━━━━┓            │
│ │ 플랜 A │ │ 플랜 B │ ┃ 플랜 C ┃ ← 추천     │
│ │ ─────  │ │ ─────  │ ┃ ─────  ┃            │
│ │ ✓ 항목 │ │ ✓ 항목 │ ┃ ✓ 항목 ┃            │
│ │ ✗ 항목 │ │ ✓ 항목 │ ┃ ✓ 항목 ┃            │
│ │ ✗ 항목 │ │ ✗ 항목 │ ┃ ✓ 항목 ┃            │
│ └────────┘ └────────┘ ┗━━━━━━━━┛            │
└────────────────────────────────────────────┘
```
- **coded**: no
- **density_note**: 세로 컬럼이라 특징 행 6개까지 22px로 수용. 4열이면 폭 270px라 특징 라벨 ≤6어 유지. 행이 7개↑면 matrix로 전환.
- **source**: https://slidebazaar.com/templates/three-four-column-cards-powerpoint-google-slides/ (verified — 3/4열 카드, 요금표·기능 비교·계층 오퍼링 용례, 카드 가감으로 열 전환 확인) · 보조 https://slidesdepot.com/templates/comparison-chart-powerpoint-google-slides/
- **adaptation_note**: 원본은 카드마다 원색 헤더. 재표현은 카드 본체를 `.surface` 통일하고 구조·추천 테두리와 헤더는 `--blue`로 통일한다. 특징 유무는 `--mint-deep` 체크/`--red` 엑스 문법색. 가격 숫자는 각 카드 헤더에만.

---

### L-gm-matrix — 특징 매트릭스 격자 / Feature Matrix Grid

- **id**: `L-gm-matrix`
- **name**: 특징 매트릭스 격자 / Feature Matrix Grid
- **composition_family**: `grid-mosaic`
- **info_shapes**: `[comparison, classification]`
- **when_to_use**: 여러 옵션(열)을 여러 기준(행)에 걸쳐 체크/엑스 셀로 교차 평가해, 어느 옵션이 어떤 기준을 만족하는지 격자 한 장으로 훑을 때(기능 비교표, 공급사 평가).
- **when_to_avoid**: 옵션마다 설명 문단이 필요할 때(compare-cards) · 기준이 1~2개뿐이라 표가 과할 때 · 수치 추세가 핵심일 때(numeric 차트).
- **capacity**: ~5 옵션 열 × ~6 기준 행(헤더 포함 표 ~1152×470). 셀은 ✓/✕ 또는 짧은 값. 기준 라벨 ≤8어. 표 폰트 17px 하한 준수.
- **built_on**: `.s-full` + `table.t`(th 블루 배경·800, 짝수행 연회색) · 셀 아이콘 `--mint-deep`/`--red` · 헤더 행=옵션, 첫 열=기준
- **content_slots**: title, matrix { col_header×~5(옵션), row×~6 { criterion, cell×~5 { ✓|✕|값 } } }
- **sketch**:
```
┌────────────────────────────────────────────┐
│ 슬라이드 제목                                │
│ ┌──────────┬─────┬─────┬─────┬─────┐        │
│ │ 기준\옵션 │  A  │  B  │  C  │  D  │        │
│ ├──────────┼─────┼─────┼─────┼─────┤        │
│ │ 기준 1    │  ✓  │  ✗  │  ✓  │  ✓  │        │
│ │ 기준 2    │  ✗  │  ✓  │  ✓  │  ✗  │        │
│ │ 기준 3    │  ✓  │  ✓  │  ✗  │  ✓  │        │
│ │ 기준 4    │  ✓  │  ✗  │  ✓  │  ✓  │        │
│ └──────────┴─────┴─────┴─────┴─────┘        │
└────────────────────────────────────────────┘
```
- **coded**: no
- **density_note**: 표 17px 하한이 실질 제약 — 5열×6행이 1280×720 안정 상한. 셀은 문장 아닌 표식/짧은 값. 열이 6개↑거나 셀에 문장이 들어가면 가독성 붕괴 → 옵션 수를 줄이거나 compare-cards로.
- **source**: https://www.slidekit.com/comparison-matrix-template/ (verified — 열=옵션·행=기준, 최대 5옵션, Yes/No 셀 표식, 공급사·요금 평가 용례 확인) · 보조 https://slidesdepot.com/templates/comparison-chart-powerpoint-google-slides/
- **adaptation_note**: 원본 매트릭스의 색면 셀을 deck.css `table.t`로 재표현 — 헤더행만 블루, 본문 셀은 무채, 만족/불만족은 `--mint-deep` ✓ / `--red` ✕ 아이콘으로만 색을 얹어 문법(민트=확인·레드=미달)을 지킨다. 짝수행 연회색은 `.t` 프리미티브로 가독성 확보.
