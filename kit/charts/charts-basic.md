# charts-basic — 기본 차트 element (막대·선·영역 계열)

> 이 그룹은 **수치·비율·추세**(`numeric`)를 코드로 그리는 **재사용 element(fragment)** 다. whole-slide가 아니라 레이아웃 위에 **얹는** 조각 — 레이아웃 ≠ 다이어그램(카탈로그-규격 §5).
> 각 항목은 fragment 클래스 `.viz-<slug>` 로 독립 선언되고, 그걸 얹는 **데모 host 슬라이드는 별도**(`element_vs_slide` 필드).
> **code-viz 원칙:** 전부 CSS/SVG로 렌더 — 이미지 아님. 숫자·틱·축·범례 라벨은 전부 텍스트(`word-break:keep-all`).
> **색은 문법:** 강조 계열/막대 1곳만 `--blue`, 비강조는 `--periwinkle`, 축·baseline은 `--line`. 주의·경고=코랄 · 오류=레드 · 달성·안전=민트는 값이 그 뜻일 때만.
> **no-default(의미 기준):** 이 그룹의 어떤 차트도 "기본/가장 흔한 차트"로 규정하지 않는다 — 선택은 `data_shape`가 정한다.
> 세로 예산·행높이·글자폭은 `guide/토큰-치트시트.md` 산식으로 검산(콘텐츠 영역 ≈ 548px, 본문 22px×1.78 ≈ 줄당 39px).

---

### C-column — 세로막대 / Column Chart

- **id**: `C-column`
- **kind**: chart
- **name**: 세로막대 / Column Chart
- **info_shapes**: `[numeric, comparison]`
- **data_shape**: 소수 카테고리(3~7개)의 **단일 값 비교**. 순서가 자연스러운(시간·순서형: 연도·분기·연령대·구간) 축이거나, 카테고리별 한 값의 크기 대소. 값은 절대량·비율 모두 가능(비율이면 합≈100 강제 아님 — pie와 달리 부분-전체 아님).
- **when_to_use**: 3~7개 카테고리의 값을 세로 막대 높이로 한눈에 견줄 때. 특히 축이 **순서형/시간형**이라 좌→우 진행이 논리적일 때(연도별 추세를 이산 구간으로 볼 때 포함).
- **when_to_avoid**: 라벨이 길어 세로축 아래에서 기울어질 때(→ C-hbar), 카테고리가 8개↑라 막대폭이 붕괴할 때, 부분-전체 합≈100 구성을 보일 때(→ C-stacked-bar/donut), 연속 시계열의 매끄러운 추세가 핵심일 때(→ C-line).
- **capacity**: 카테고리 3~7개. 플롯 높이 ~300px(데모 `.cc-plot` 기준) — 최댓값 막대 240~280px, 나머지 비례. 막대폭 ≈92px → 7개도 gap 포함 1152 안. 값 라벨 ≥22px(`.cc-val`)·축 라벨 ≥19px 한 줄(≤5자). **상한 7**(8개↑ 막대폭·라벨 겹침 붕괴). 강조 막대 1개만 `--blue`, 나머지 `--periwinkle`.
- **element_vs_slide**: fragment=`.viz-column`(데모에서 **브라우저 검증된** `.code-chart`/`.cc-plot`/`.cc-bar`/`.cc-fill(.is-key)`/`.cc-val`/`.cc-axis` 마크업을 그대로 사용). ↔ 데모 host 슬라이드는 **별도** — 예: top-down 밴드 레이아웃 `L-td-column-series` 위에 이 fragment를 얹은 whole-slide(그 슬라이드는 레이아웃 카탈로그 항목이지 이 element가 아님).
- **placement**: `[top-down, diagram-centric, grid-mosaic]`
- **built_on**: `.s-full`·`.s-eyebrow`(host) + 데모 프리미티브 `.code-chart`·`.cc-plot`·`.cc-bar`·`.cc-fill`·`.cc-fill.is-key`·`.cc-val`·`.cc-axis`(신규 CSS 불필요 — 데모 그대로 승격). 색 `--blue`/`--periwinkle`, baseline `--line`.
- **a11y**: `role="img"` + `aria-label="세로막대: <카테고리1> <값1>, <카테고리2> <값2> …"`(예: "세로막대: 기획 40퍼센트, 개발 35퍼센트, 검증 25퍼센트").
- **sketch**:
```
┌──────────────────────────────────────────┐
│  ▍EYEBROW                                 │
│   40%                                     │
│   ███   35%                               │
│   ███   ███   25%                         │  .cc-plot (300px)
│   ███   ███   ███                         │  key=blue
│  ─기획──개발──검증──────── baseline(--line) │  .cc-axis 19px
└──────────────────────────────────────────┘
```
- **coded**: no
- **source**: https://www.storytellingwithdata.com/blog/2022/1/21/which-bar-orientation-should-i-use (verified — 세로 컬럼은 순서형/시간형(연령·소득 구간·전후·연도) 좌→우 진행에 적합, "guidelines, not rigid rules")
- **adaptation_note**: 원본은 방향 선택 원칙만 차용. 데모 `.code-chart`(토큰 색 div 막대)로 재표현하고, 강조는 `.cc-fill.is-key` 블루 1곳·나머지 periwinkle. 값은 막대 위 `.cc-val` 텍스트(이미지 아님). 순서형 축이면 정렬을 데이터 순서로 고정(값 내림차순 아님).

---

### C-hbar — 가로막대 / Horizontal Bar Chart

- **id**: `C-hbar`
- **kind**: chart
- **name**: 가로막대 / Horizontal Bar Chart
- **info_shapes**: `[numeric, comparison]`
- **data_shape**: **순위·랭킹** 또는 **긴 라벨**을 가진 명목형(nominal) 카테고리의 단일 값. 값 내림/오름차순 정렬로 리더보드처럼 상위를 부각. 카테고리 간 순서가 임의(이름·유형)라 좌→우 진행이 무의미할 때.
- **when_to_use**: 카테고리 라벨이 길어 세로축에서 기울어질 때, 또는 값 순위를 리더보드로 보여 상위 항목을 강조할 때. 가로 트랙이 라벨 텍스트에 좌측 공간을 넉넉히 준다.
- **when_to_avoid**: 축이 순서형/시간형이라 좌→우 진행이 자연스러울 때(→ C-column), 부분-전체 구성일 때(→ C-stacked-bar), 항목이 8개↑라 세로 예산(548px)을 넘길 때, 연속 추세일 때(→ C-line).
- **capacity**: 6~8행. 행 높이 38px + 행간 ~14px ≈ 52px/행 → 8행 ≈ 416px, 548px 예산 내(라벨·값 포함). 좌측 라벨 열 고정폭 ~320px(긴 라벨 ≤14자 한 줄, `keep-all`), 막대 트랙 ~640px, 값 라벨 막대 끝 ≥19px. **상한 8**(초과 시 세로 예산 초과). 순위 1위(또는 강조 항목)만 `--blue`, 나머지 `--periwinkle`.
- **element_vs_slide**: fragment=`.viz-hbar`(신규 — 행 flex 스택; 각 행 = 라벨(고정폭) + 트랙(`--line` baseline) + `.hb-fill`(width:값%) + 값 텍스트). ↔ 데모 host 슬라이드는 **별도** — 예: `L-td-compare-bars`(양방향은 두 계열) 또는 단일 순위 밴드 위에 얹은 whole-slide.
- **placement**: `[top-down, diagram-centric, split]`
- **built_on**: `.s-full`·`.s-eyebrow`·`.canvas-fill`(host) + **신규 CSS `.viz-hbar`**: `.hb-row{display:flex;align-items:center;gap:14px;height:38px}` · `.hb-label{width:320px;font-weight:800;font-size:22px}` · `.hb-track{flex:1;height:28px;background:var(--surface);border-radius:8px}` · `.hb-fill{height:100%;background:var(--periwinkle);border-radius:8px}` `.hb-fill.is-key{background:var(--blue)}` · `.hb-val{font-weight:800;font-size:19px;color:var(--blue)}`. 토큰만 사용.
- **a11y**: `role="img"` + `aria-label="가로막대 순위: 1위 <라벨> <값>, 2위 <라벨> <값> …"`.
- **sketch**:
```
┌──────────────────────────────────────────┐
│  ▍EYEBROW                                 │
│  서울특별시  ██████████████ 62  ← is-key   │  .hb-row 38px
│  부산광역시  █████████ 41                  │  label 320px +
│  대구광역시  ███████ 33                    │  track(--line)
│  인천광역시  █████ 24                       │  fill periwinkle
│  …최대 8행                                 │
└──────────────────────────────────────────┘
```
- **coded**: no
- **source**: https://depictdatastudio.com/when-to-use-horizontal-bar-charts-vs-vertical-column-charts/ (verified — 가로막대는 명목형·긴 라벨에 적합, "arranged in any order", 값 정렬로 주목 항목을 먼저)
- **adaptation_note**: 원본의 "명목형·긴 라벨·순위 → 가로" 원칙만 차용. 트랙·막대를 토큰 색 div로 재표현(강조 블루 1곳·비강조 periwinkle), 값은 막대 끝 텍스트. 정렬은 값 순(리더보드)으로 두되 강조 항목이 값 1위가 아니면 `.is-key`로 별도 강조.

---

### C-stacked-bar — 누적막대 / Stacked Bar Chart

- **id**: `C-stacked-bar`
- **kind**: chart
- **name**: 누적막대 / Stacked Bar Chart
- **info_shapes**: `[numeric, comparison]`
- **data_shape**: **카테고리별 부분-전체 구성** — 각 막대가 하나의 전체이고 세그먼트가 그 부분(합=막대 총량). 카테고리 3~6개 × 세그먼트 ≤4. 100% 모드면 전 막대 동일 길이(세그먼트=구성비, 합≈100). 총량 비교와 구성 비교를 **동시에** 볼 때.
- **when_to_use**: 여러 카테고리 각각의 총량과 그 내부 구성(부분 비중)을 한 그림에서 견줄 때. 예산 배분·설문 응답 분포처럼 "합도 부분도 중요"할 때. 시간축에 얹으면 구성 변화 추세도.
- **when_to_avoid**: 세그먼트가 5개↑라 색 구분·라벨이 붕괴할 때(소스: 최대 4), baseline이 다른 중간 세그먼트끼리 정밀 비교가 핵심일 때(공통 기준선 없음 → small multiples/C-column), 단일 값 비교뿐일 때(→ C-column/C-hbar).
- **capacity**: 막대(카테고리) 3~6개 × **세그먼트 ≤4**(소스 하한 준수). 막대폭 ≈120px(세로형) 또는 100% 가로 스택. 범례 ≤4항목 한 줄(19px). 세그먼트 값 라벨은 세그먼트 두께 ≥28px일 때만 인라인, 아니면 범례로 이관. **상한: 세그먼트 4·막대 6**. 강조 세그먼트 1개만 블루, 나머지는 periwinkle→surface 톤 램프.
- **element_vs_slide**: fragment=`.viz-stacked`(신규 — 각 막대 = 세그먼트 flex 스택(세로) 또는 100% width 스택; 세그먼트 배경은 토큰 톤 램프 + 범례). ↔ 데모 host 슬라이드는 **별도** — 예: `L-td-column-series`(구성 밴드) 또는 `comparison-symmetric` 2패널 위에 얹은 whole-slide.
- **placement**: `[top-down, diagram-centric, comparison-symmetric]`
- **built_on**: `.s-full`·`.s-eyebrow`(host) + **신규 CSS `.viz-stacked`**: `.st-bars{display:flex;justify-content:space-around;align-items:flex-end;height:300px}` · `.st-bar{width:120px;display:flex;flex-direction:column}` · `.st-seg{width:100%;font-size:19px;font-weight:800;color:var(--white);display:grid;place-items:center}` (배경: `--blue`/`--periwinkle`/`--surface` 램프) · `.st-legend`(`.pill` 재사용 가능) · `.st-axis`(`.cc-axis` 재사용). 토큰만.
- **a11y**: `role="img"` + `aria-label="누적막대: <카테고리>는 <세그먼트A> <값>, <세그먼트B> <값> … (합 <총량>) …"`.
- **sketch**:
```
┌──────────────────────────────────────────┐
│  ▍EYEBROW              [■기획 ■개발 ■검증] │  st-legend
│   ┌──┐   ┌──┐   ┌──┐                       │
│   │검│   │검│   │검│  ← periwinkle          │  st-bar 120px
│   │개│   │개│   │개│  ← surface             │  seg ≤4
│   │기│   │기│   │기│  ← blue(key)         │  세그 라벨 ≥28px時
│  ─1분기─2분기─3분기──── baseline            │  st-axis 19px
└──────────────────────────────────────────┘
```
- **coded**: no
- **source**: https://analysisfunction.civilservice.gov.uk/support/communicating-analysis/introduction-to-data-visualisation-e-learning/module-7-stacked-bar-charts/ (verified — 부분-전체에 적합, "maximum of four stacks")
- **adaptation_note**: 원본의 "4 세그먼트 상한"(소스)에 더해, 누적막대의 공통 baseline 부재(중간 세그먼트 비교 정밀도 저하)라는 일반 원리를 capacity에 반영. 세그먼트 색은 무지개가 아니라 토큰 톤 램프(주요 계열=블루 → 비강조=periwinkle → surface)로 위계를 만든다. 중간 세그먼트 정밀 비교가 필요하면 이 element를 버리고 C-column small multiples 권장을 adaptation으로 명시.

---

### C-line — 꺾은선 / Line Chart

- **id**: `C-line`
- **kind**: chart
- **name**: 꺾은선 / Line Chart
- **info_shapes**: `[numeric]`
- **data_shape**: **연속량의 시계열 추세** — x축이 시간/연속 구간, y가 값. 계열 1~4개의 방향·변곡·교차를 정밀 비교. y축 0에서 시작하지 않아도 됨(구간 확대 허용). 이산 카테고리 비교가 아니라 매끄러운 추세가 핵심일 때.
- **when_to_use**: 시간에 따른 값의 추세·변동을 보이거나, 여러 계열의 추세를 정밀 비교(교차·추월 포함)할 때. 데이터 포인트가 많아 막대로는 촘촘해질 때.
- **when_to_avoid**: x가 이산 소수 카테고리라 개별 값 비교가 핵심일 때(→ C-column), 누적 총량·부피 강조가 목적일 때(→ C-area), 계열이 5개↑라 스파게티가 될 때, 부분-전체 구성일 때(→ C-stacked-bar).
- **capacity**: 계열 ≤4(스파게티 회피), x 시점 4~12개. 플롯 SVG 높이 ~300px·폭 ~640px. 축 라벨 ≥19px, 데이터 포인트 마커 선택. **상한 4계열**(초과 시 선 교차로 판독 붕괴). 강조 계열 1개 `--blue`(굵게)·나머지 `--periwinkle`. 값 라벨은 끝점/변곡점만 선택적.
- **element_vs_slide**: fragment=`.viz-line`(신규 — inline SVG: `<polyline>` stroke, `<circle>` 마커, `<text>` 축/값 라벨, `<line>` 축). ↔ 데모 host 슬라이드는 **별도** — 예: `L-td-column-series` 자리의 추세 host 또는 `centered` 무대 위에 얹은 whole-slide.
- **placement**: `[top-down, diagram-centric, centered]`
- **built_on**: `.s-full`·`.s-eyebrow`(host) + **신규 CSS/SVG `.viz-line`**: inline `<svg viewBox="0 0 640 320">` · `.ln-axis{stroke:var(--line);stroke-width:2}` · `.ln-series{fill:none;stroke:var(--periwinkle);stroke-width:3}` `.ln-series.is-key{stroke:var(--blue);stroke-width:4}` · `.ln-dot{fill:var(--blue)}` · `.ln-label{font-size:19px;font-weight:800;fill:var(--ink)}`. 좌표는 코드 계산, 이미지 아님. 토큰만.
- **a11y**: `role="img"` + `aria-label="꺾은선 추세: <계열>은 <시작시점> <값>에서 <끝시점> <값>으로 <증가/감소> …"`.
- **sketch**:
```
┌──────────────────────────────────────────┐
│  ▍EYEBROW                                 │
│  값│           ●──────●  ← is-key(blue) │  svg 640×320
│    │      ●───╱   ●───╱                    │  polyline
│    │  ●──╱  ●─╱        ← periwinkle        │  dots
│    └──┬───┬───┬───┬───┬── (--line axis)   │  축 19px
│      '22 '23 '24 '25 '26                   │
└──────────────────────────────────────────┘
```
- **coded**: no
- **source**: https://inforiver.com/insights/line-charts-vs-area-charts-8-key-differences/ (verified — 선은 추세 강조·다계열 정밀 비교·교차/추월에 적합, y축 0 불필요, area보다 많은 계열 수용)
- **adaptation_note**: 원본의 "선=추세·정밀·다계열" 구분을 그대로 채택. SVG polyline을 토큰 색으로 재표현(강조 계열 블루 굵게 1곳·나머지 periwinkle). 라벨·틱은 `<text>`로(이미지 아님). y축 확대가 오해를 부를 값이면 0 기준으로 조정하는 판단을 adaptation에 명시.

---

### C-area — 영역 / Area Chart

- **id**: `C-area`
- **kind**: chart
- **name**: 영역 / Area Chart
- **info_shapes**: `[numeric]`
- **data_shape**: **추세 + 부피/누적 강조** — 시계열 곡선 아래를 채워 총량·크기를 부각. 단일 영역이거나 누적(stacked) ≤3 계열로 부분-전체 추세를 동시에. y축 **0에서 시작 필수**(면적이 크기를 대표). 합산 관계(예: 매출=부문 합)일 때.
- **when_to_use**: 한 계열의 부피·누적 크기를 강조하거나, 소수 계열의 합산(부분→전체) 추세를 누적 영역으로 볼 때. 값 변동폭이 커서 면적으로 규모 차이를 드러낼 때.
- **when_to_avoid**: 계열이 3개↑라 상위 레이어가 하위를 가릴 때(occlusion, 소스: ~2), 여러 계열의 정밀 추세 비교가 핵심일 때(→ C-line), y축을 0에서 못 시작할 때, 이산 카테고리 비교일 때(→ C-column).
- **capacity**: 단일 영역 또는 누적 ≤3 계열(소스: 실질 최대 ~2, 투명도로 완화). y축 0 시작 필수. SVG 플롯 ~300px. 축 라벨 ≥19px. **상한 3계열**(초과 시 하위 레이어 은폐 → 회피). 강조 영역 1개 `--blue`(반투명 채움)·보조 `--periwinkle`(반투명).
- **element_vs_slide**: fragment=`.viz-area`(신규 — inline SVG: `<path>` 채움(baseline=y0 닫힘) + `<polyline>` 상단 stroke + `<text>` 라벨). ↔ 데모 host 슬라이드는 **별도** — 예: `L-td-column-series` 자리의 누적 추세 host 또는 `diagram-centric` 무대 위에 얹은 whole-slide.
- **placement**: `[top-down, diagram-centric]`
- **built_on**: `.s-full`·`.s-eyebrow`(host) + **신규 CSS/SVG `.viz-area`**: inline `<svg viewBox="0 0 640 320">` · `.ar-fill{fill:var(--blue);fill-opacity:.18}` `.ar-fill.aux{fill:var(--periwinkle);fill-opacity:.22}` · `.ar-line{fill:none;stroke:var(--blue);stroke-width:3}` · `.ar-axis{stroke:var(--line);stroke-width:2}` · `.ar-label{font-size:19px;font-weight:800;fill:var(--ink)}`. baseline은 y=0 고정. 토큰만.
- **a11y**: `role="img"` + `aria-label="영역 추세: <계열>의 누적 규모가 <시작> <값>에서 <끝> <값>으로 증가 …"`.
- **sketch**:
```
┌──────────────────────────────────────────┐
│  ▍EYEBROW                                 │
│  값│        ╱▔▔▔▔▔▔▔●  ← ar-line(blue)  │  svg 640×320
│    │    ╱▓▓▓▓▓▓▓▓▓▓▓  ← ar-fill .18       │  path fill
│    │╱▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  (y0 baseline 필수)  │  누적 ≤3
│    └──┬───┬───┬───┬──── (--line axis)     │  축 19px
│      '23 '24 '25 '26                       │
└──────────────────────────────────────────┘
```
- **coded**: no
- **source**: https://www.fusioncharts.com/blog/line-charts-vs-area-charts/ (verified — 영역은 합산 관계·부분-전체(누적 영역)·데이터셋 변화 지시에 적합, 계열 2개 초과 시 occlusion으로 아래 레이어 은폐)
- **adaptation_note**: 원본의 "합산·누적·occlusion 한계"를 capacity(≤3, 실질 2)에 반영. 채움은 토큰 반투명(블루 .18 강조·periwinkle 보조)으로 재표현하고 상단 선은 블루. y=0 baseline을 코드로 고정해 면적이 규모를 정직하게 대표하게 함. 정밀 다계열 비교가 필요하면 C-line으로 넘김을 명시.
