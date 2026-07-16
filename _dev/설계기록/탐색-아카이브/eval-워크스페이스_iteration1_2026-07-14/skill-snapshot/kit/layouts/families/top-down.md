# top-down 패밀리 — 상단 타이틀 밴드 + 하단이 콘텐츠를 세로로 꽉 채우는 구도(좌우 분할 아님). `.s-full`+`.canvas-fill` 위에 세운다.

> composition_family: `top-down` — 전 항목 공통. 밴드(eyebrow·title·accent-bar)가 위, 콘텐츠 캔버스가 아래 남은 세로를 flex로 채운다.
> 맞는 정보 모양: `comparison` · `classification` · `numeric` · `mapping`.
> 격리 렌더 기준 캔버스: `.s-full`(left/right 64, top 118) + `.canvas-fill`(bottom 54) → 콘텐츠 가용 영역 ≈ 1152×548px. 밴드 ≈ 130~150px 소비 후 콘텐츠 ≈ 1152×400px. 스케치·용량은 이 안에서 스크롤 없이 성립하도록 산정.

---

### L-td-table — 정보표 밴드 / Title-band Data Table

- **id**: `L-td-table`
- **name**: 정보표 밴드 / Title-band Data Table
- **composition_family**: `top-down`
- **info_shapes**: `[comparison, classification]`
- **when_to_use**: 항목별 속성을 정렬해 훑거나 대안을 열별로 견줄 때. 밴드 제목이 표가 증명하는 한 줄 인사이트를 말하고, 표가 근거를 준다.
- **when_to_avoid**: 강조할 수치가 1~2개뿐이거나(→ metric-row), 관계가 A→B 대응이라 셀 격자가 과할 때(→ mapping-rows). 셀당 문장이 길어 17px 표 하한을 넘겨야만 담기면 회피.
- **capacity**: 헤더 1행 + 본문 6~7행, 4~5열. 셀당 ≤ 8어(표 17px, 행높이 ≈ 52px 기준 400px에 7~8행).
- **built_on**: `.s-full`, `.canvas-fill`, `.s-eyebrow`, `.s-title`(+`.hl`), `.accent-bar`, `table.t`
- **content_slots**: eyebrow, title, accent, table(thead th, tbody rows)
- **sketch**:
```
┌──────────────────────────────────────────────┐
│ EYEBROW                                       │
│  한 줄 인사이트 제목            ▂▂ accent      │
├──────┬─────────┬─────────┬─────────┬─────────┤
│ 항목 │  A열    │  B열    │  C열    │  D열    │ ← th 블루
├──────┼─────────┼─────────┼─────────┼─────────┤
│ 행1  │   ·     │   ·     │   ·     │   ·     │
│ 행2  │   ·     │   ·     │   ·     │   ·     │
│ 행3  │   ·     │   ·     │   ·     │   ·     │
│ …6행 │   ·     │   ·     │   ·     │   ·     │
└──────┴─────────┴─────────┴─────────┴─────────┘
```
- **coded**: no
- **density_note**: `table.t` td/th 17px 하한 준수, padding 14px. 7행 초과 시 행높이가 52px 아래로 눌려 하한 붕괴 → 6~7행에서 컷. 강조 열 하나만 `th` 블루 배경.
- **source**: https://deckary.com/blog/powerpoint-layout-ideas (verified — action-title 헤드라인 밴드 + 하단 데이터 영역 70~80% 패턴 확인)
- **adaptation_note**: 원본은 PPT Slide Master의 "Title and Content". 복제하지 않고 밴드는 `.s-eyebrow`+`.s-title`(강조어만 `.hl` 블루)+`.accent-bar`로, 표는 `table.t`로 재표현. 원본의 10~12pt 조밀 표는 17px 하한 때문에 열/행을 줄여 담는다. 색은 강조 1열만 블루, 짝수행 연회색(`--surface`).

---

### L-td-swiss-columns — 스위스 단 밴드 / Swiss Column Band

- **id**: `L-td-swiss-columns`
- **name**: 스위스 단 밴드 / Swiss Column Band
- **composition_family**: `top-down`
- **info_shapes**: `[classification]`
- **when_to_use**: 동급 항목 3개를 밴드 아래 세로 단(column)으로 병렬 훑을 때. 각 단이 소제목 + 짧은 본문으로 독립적으로 읽힌다.
- **when_to_avoid**: 항목이 수치 위주라 텍스트 단이 빈약할 때(→ metric-row/column-series), 또는 항목 간 우열·추천이 있어 대칭 단이 오해를 부를 때. 단당 본문이 5줄을 넘겨야 하면 회피.
- **capacity**: 3단, 단당 소제목 ≤ 6어 + 본문 ≤ 4줄(22px/1.78, 단폭 ≈ 360px에서 줄당 ≈ 14~16자). 4단은 단폭이 좁아 keep-all 줄바꿈이 깨지므로 3단 상한.
- **built_on**: `.s-full`, `.canvas-fill`, `.s-eyebrow`, `.s-title`, `.accent-bar`, `.grid-3`, `.card`(+`.surface`), `.s-body`
- **content_slots**: eyebrow, title, accent, columns[3]{subhead, body}
- **sketch**:
```
┌──────────────────────────────────────────────┐
│ EYEBROW                                       │
│  한 줄 인사이트 제목            ▂▂ accent      │
├────────────┬────────────┬────────────────────┤
│ 소제목 A   │ 소제목 B   │ 소제목 C           │
│ 본문 ~4줄  │ 본문 ~4줄  │ 본문 ~4줄          │
│ …          │ …          │ …                  │
│            │            │                    │
└────────────┴────────────┴────────────────────┘
```
- **coded**: no
- **density_note**: `.grid-3` 12px gap, 단폭 ≈ 360px. `.s-body` 22px/1.78 → 400px 높이에 ≤ 6줄 물리적 한계, 소제목 자리 빼면 본문 4줄 권장. `word-break:keep-all`로 단어 중간 절단 방지.
- **source**: https://swissgrid.posterhouse.org/student-assignment/organizing-mass-materials/ (verified — 모듈러 3·4·5단 그리드로 title→text→caption 위계 조직, 상단 타이틀 아래 단 배치 확인)
- **adaptation_note**: 스위스 모듈러 그리드의 "높은 플로우라인에 타이틀, 아래 단에 텍스트 블록" 위계만 차용. 원본 포스터 조판을 복제하지 않고 밴드=`.s-title`, 단=`.grid-3`+`.card.surface`로 재표현. 원본의 6~12단 밀도는 22px 본문 하한상 3단으로 축약. 강조는 각 소제목 하나만 블루.

---

### L-td-metric-row — 지표 스트립 / KPI Metric Strip

- **id**: `L-td-metric-row`
- **name**: 지표 스트립 / KPI Metric Strip
- **composition_family**: `top-down`
- **info_shapes**: `[numeric]`
- **when_to_use**: 핵심 지표 3~5개를 밴드 아래 큰 숫자 한 줄로 먼저 보게 할 때. 각 카드가 값 + 라벨 + 전기 대비 델타를 담는다.
- **when_to_avoid**: 지표가 추세(시계열)라 한 시점 숫자로는 부족할 때(→ column-series), 또는 값 하나만 있어 스트립이 허전할 때(→ full-bleed big-number는 이 패밀리 밖). 카드가 6개를 넘으면 회피.
- **capacity**: 한 행 3~5카드. 카드당 큰 숫자 1(48~64px) + 라벨 ≤ 4어(22px) + 델타 ≤ 6어. 5카드 시 카드폭 ≈ 216px.
- **built_on**: `.s-full`, `.canvas-fill`, `.s-eyebrow`, `.s-title`, `.accent-bar`, `.grid-3`, `.card`(+`.surface`), `.pill`
- **content_slots**: eyebrow, title, accent, metrics[3..5]{value, label, delta}
- **sketch**:
```
┌──────────────────────────────────────────────┐
│ EYEBROW                                       │
│  한 줄 인사이트 제목            ▂▂ accent      │
├───────────┬───────────┬───────────┬──────────┤
│   82%     │   1.4M     │  ▲12%     │   3.2x   │ ← 큰 숫자
│  라벨     │  라벨      │  라벨     │  라벨    │
│  Δ 보조   │  Δ 보조    │  Δ 보조   │  Δ 보조  │
└───────────┴───────────┴───────────┴──────────┘
```
- **coded**: no
- **density_note**: 큰 숫자는 40s 하한 위(≥44px), 라벨 22px·델타 캡션 19px 하한. 델타 방향은 민트(개선)·코랄(악화)·레드(미달/오류) 문법. 한 행 유지 위해 카드 ≤ 5.
- **source**: https://www.setproduct.com/blog/dashboard-ui-design (verified — 헤더 아래 KPI 카드 한 줄, 각 카드 = 지표 + 전기 대비 델타, 3~7개, 최상단 시각 비중 최대 확인)
- **adaptation_note**: 대시보드 "헤더→KPI행→차트" 세로 리딩만 차용, UI 크롬은 버린다. 밴드=`.s-title`, KPI행=`.grid-3`/4열 `.card.surface`, 델타=`.pill`(민트/코랄)로 재표현. 원본의 스파크라인·계정 스위처 등은 생략해 숫자에 집중. 블루는 강조 지표 1곳만.

---

### L-td-matrix — 사분면 매트릭스 / Quadrant Matrix

- **id**: `L-td-matrix`
- **name**: 사분면 매트릭스 / Quadrant Matrix
- **composition_family**: `top-down`
- **info_shapes**: `[classification, mapping]`
- **when_to_use**: 두 기준(축)으로 항목을 4칸에 분류하거나, 축 조합이 각 칸의 처방을 정하는 대응을 보일 때. 밴드가 두 축의 의미를 한 줄로 건다.
- **when_to_avoid**: 항목이 5개 이상 병렬이라 2×2로 안 갈릴 때(→ swiss-columns/bento), 또는 축이 하나뿐인 단순 순위일 때(→ compare-bars). 칸당 글이 3줄을 넘으면 회피.
- **capacity**: 4칸(2×2). 칸당 라벨 ≤ 5어 + 본문 ≤ 3줄(22px). 칸 크기 ≈ 560×190px. 축 라벨 4개(각 ≤ 3어).
- **built_on**: `.s-full`, `.canvas-fill`, `.s-eyebrow`, `.s-title`, `.accent-bar`, `.grid-2`, `.card`(+`.surface`), `.num-circle`
- **content_slots**: eyebrow, title, accent, axis_labels[x, y], quadrants[4]{tag, label, body}
- **sketch**:
```
┌──────────────────────────────────────────────┐
│ EYEBROW                                       │
│  한 줄 인사이트 제목            ▂▂ accent      │
├───────────────────────┬──────────────────────┤
│  ① 사분면            │  ② 사분면            │
│  라벨 + 2~3줄        │  라벨 + 2~3줄        │
├───────────────────────┼──────────────────────┤
│  ③ 사분면            │  ④ 사분면            │
│  라벨 + 2~3줄        │  라벨 + 2~3줄        │
└───────────────────────┴──────────────────────┘
```
- **coded**: no
- **density_note**: 2×2 = `.grid-2` 두 줄. 칸 높이 ≈ 190px에 라벨(22px 800) + 본문 3줄이 상한. 축 라벨은 캡션 19px, 밴드와 겹치지 않게 칸 모서리에. 강조 칸(오늘의 처방) 하나만 블루 테두리.
- **source**: https://www.presentationgo.com/presentation/2x2-matrix-model-powerpoint-google-slides/ (verified — 상단 타이틀 + 2행 2열 4사분면, 각 칸 텍스트 플레이스홀더, 16:9 확인)
- **adaptation_note**: 2×2 사분면 골격만 차용. 원본의 컬러 스퀘어·아이콘을 복제하지 않고 `.grid-2`×2 + `.card.surface`, 칸 번호는 `.num-circle`로 재표현. 축 라벨은 `.s-eyebrow` 톤 캡션으로 칸 밖 여백에. 색은 강조 칸 1개만 블루, 나머지 중립 `--surface`.

---

### L-td-mapping-rows — 대응 행 / Mapping Rows

- **id**: `L-td-mapping-rows`
- **name**: 대응 행 / Mapping Rows
- **composition_family**: `top-down`
- **info_shapes**: `[mapping]`
- **when_to_use**: 좌측 항목이 우측 항목으로 대응·연결됨을 행 단위로 보일 때("이 모델 → 이 지표"). 밴드가 무엇이 무엇을 정하는지 한 줄로 건다.
- **when_to_avoid**: 대응이 아니라 동급 나열일 때(→ swiss-columns), 또는 순서·절차라 흐름 화살표가 세로여야 할 때(vertical-flow 패밀리). 대응 쌍이 7개를 넘으면 회피.
- **capacity**: 5~6 대응 행. 좌·우 각 ≤ 6어(22px), 가운데 커넥터 `→`. 행높이 ≈ 60px 기준 400px에 5~6행.
- **built_on**: `.s-full`, `.canvas-fill`, `.s-eyebrow`, `.s-title`, `.accent-bar`, `.card`(+`.surface`), `.pill`, 관계 커넥터 `→`
- **content_slots**: eyebrow, title, accent, rows[5..6]{left, connector, right}
- **sketch**:
```
┌──────────────────────────────────────────────┐
│ EYEBROW                                       │
│  한 줄 인사이트 제목            ▂▂ accent      │
├──────────────────────────────────────────────┤
│  좌 항목 A   →   우 대응 A                    │
│  좌 항목 B   →   우 대응 B                    │
│  좌 항목 C   →   우 대응 C                    │
│  좌 항목 D   →   우 대응 D                    │
│  …5~6행                                       │
└──────────────────────────────────────────────┘
```
- **coded**: no
- **density_note**: 좌 카드 · 블루 `→` · 우 카드가 한 행. 좌우 텍스트 22px 하한, keep-all. 6행 초과 시 행높이 60px 아래로 눌려 카드 패딩이 붕괴 → 6행 컷. 커넥터만 블루로 관계 명시.
- **source**: https://conceptviz.app/blog/mapping-diagram-complete-guide (verified — 좌 도메인·우 치역을 화살표로 행 단위 대응, 입력↔출력 연결 레이아웃 확인)
- **adaptation_note**: 수학 매핑 다이어그램의 "좌 집합 → 우 집합, 행별 화살표" 대응 은유만 차용. 원본의 타원·교차선을 복제하지 않고 좌/우 `.card.surface` + 가운데 블루 `→`(치트시트 관계 커넥터)로 정렬된 행 매핑으로 재표현. 좌우 정확히 1:1 정렬해 다대다 혼선 방지.

---

### L-td-compare-bars — 비교 막대 / Comparison Bars

- **id**: `L-td-compare-bars`
- **name**: 비교 막대 / Comparison Bars
- **composition_family**: `top-down`
- **info_shapes**: `[comparison, numeric]`
- **when_to_use**: 동일 항목들을 두 계열(예: 전/후, A/B)로 견주거나 값 순위를 가로 막대로 보일 때. 밴드가 무엇이 어떻게 이기는지 한 줄로 건다.
- **when_to_avoid**: 계열이 시간축이라 세로 컬럼이 맞을 때(→ column-series), 또는 항목이 표 속성 비교라 셀이 필요할 때(→ table). 항목이 6개를 넘으면 회피.
- **capacity**: 중앙 라벨 열 + 좌우 각 5행까지. 항목 라벨 ≤ 5어, 막대당 값 1. 막대 행높이 ≈ 60px 기준 5~6행.
- **built_on**: `.s-full`, `.canvas-fill`, `.s-eyebrow`, `.s-title`, `.accent-bar`, 코드 막대(`.code-*`/div bar), `.card`
- **content_slots**: eyebrow, title, accent, series_titles[2], rows[5]{left_bar, label, right_bar}
- **sketch**:
```
┌──────────────────────────────────────────────┐
│ EYEBROW                                       │
│  한 줄 인사이트 제목            ▂▂ accent      │
├───────────────┬──────────┬───────────────────┤
│ ███████ 62 │  항목 1  │ 48 ██████         │
│ █████   41 │  항목 2  │ 55 ███████        │
│ ████    33 │  항목 3  │ 61 ████████       │
│ …5행       │          │                    │
└───────────────┴──────────┴───────────────────┘
```
- **coded**: no
- **density_note**: 막대는 이미지 아님 — 코드/div 막대(numeric 규칙 준수). 값 라벨 ≥19px, 항목 라벨 22px. 주요 계열은 블루, 비강조 계열은 periwinkle로 판독 순서를 만든다. 6행 넘으면 막대 두께가 붕괴 → 5~6행 컷.
- **source**: https://www.presentationgo.com/presentation/comparative-bar-charts-powerpoint/ (verified — 중앙 라벨 열 + 좌우 가로 막대, 최대 5항목, 상단 두 계열 타이틀 공간 확인)
- **adaptation_note**: 중앙 라벨 + 양방향 가로 막대(diverging) 구조만 차용. 원본 템플릿 색·형태 복제 없이 밴드=`.s-title`, 막대=토큰 색 div/SVG로 재표현(블루 vs periwinkle). 값은 막대 안/끝 라벨로. 최대 5항목 상한 유지, 좌우 스케일 동일 기준으로.

---

### L-td-column-series — 연도 컬럼 / Year Column Series

- **id**: `L-td-column-series`
- **name**: 연도 컬럼 / Year Column Series
- **composition_family**: `top-down`
- **info_shapes**: `[numeric]`
- **when_to_use**: 한 지표의 연도별(또는 기간별) 추세를 밴드 아래 세로 컬럼으로 보일 때. 밴드가 "매년 X% 증가" 같은 추세 결론을 한 줄로 건다.
- **when_to_avoid**: 계열이 시간이 아닌 항목 순위일 때(→ compare-bars), 또는 한 시점 값만 있을 때(→ metric-row). 컬럼(구간)이 8개를 넘으면 회피.
- **capacity**: 4~7 컬럼(연/구간). 축 라벨 각 ≤ 4자, 값 라벨 선택. 하단 주석 블록 ≤ 컬럼 수, 각 ≤ 8어. 컬럼폭 ≈ 130px(7개 기준).
- **built_on**: `.s-full`, `.canvas-fill`, `.s-eyebrow`, `.s-title`, `.accent-bar`, 코드 컬럼(`.code-*`/SVG), `.card`(주석)
- **content_slots**: eyebrow, title, accent, columns[4..7]{value, axis_label}, annotations[]
- **sketch**:
```
┌──────────────────────────────────────────────┐
│ EYEBROW                                       │
│  한 줄 인사이트 제목            ▂▂ accent      │
├──────────────────────────────────────────────┤
│              ▄        █                       │
│        ▄     █    ▆   █                       │
│   ▂    █  ▅  █    █   █                       │
│  '21  '22 '23 '24 '25 '26                     │
│  [주석 블록 · 연 성장 라벨]                   │
└──────────────────────────────────────────────┘
```
- **coded**: no
- **density_note**: 컬럼은 코드/SVG(이미지 아님, numeric 규칙). 축 라벨 ≥19px, 주석 블록 본문 22px 하한. 최근/강조 연도 컬럼만 블루, 나머지 periwinkle. 8구간 초과 시 컬럼폭이 좁아 라벨이 겹침 → 7 상한.
- **source**: https://slidebazaar.com/templates/minimal-multi-year-column-chart-powerpoint-google-slides/ (verified — 좌상단 타이틀 + 5개 연도 세로 컬럼 + 하단 모듈 주석 블록, 좌→우 리듬 확인)
- **adaptation_note**: "타이틀 밴드 → 세로 컬럼 → 하단 주석 블록" 세로 구조만 차용. 원본의 5색 무지개 막대를 복제하지 않고, 토큰 문법대로 강조 1컬럼만 블루·나머지 periwinkle로 재표현. 주석은 `.card.surface` 모듈. 성장 화살표는 블루 `→` 대신 값 델타 라벨로.

---

### L-td-bento — 벤토 타일 밴드 / Bento Tile Band

- **id**: `L-td-bento`
- **name**: 벤토 타일 밴드 / Bento Tile Band
- **composition_family**: `top-down`
- **info_shapes**: `[classification]`
- **when_to_use**: 병렬 항목 여러 개를 크기가 다른 타일로 밴드 아래 채우되, 히어로 타일 하나에 대표 항목을 실을 때. 항목 위계가 순차가 아니라 병렬일 때.
- **when_to_avoid**: 항목이 완전 동급이라 크기 차이가 오해를 부를 때(→ swiss-columns 균등 단), 또는 한 문장 값 진술이 필요할 때(centered/full-bleed 패밀리). 타일이 8개를 넘으면 회피.
- **capacity**: 6~7 타일(히어로 1 + 소형 5~6). 히어로 ≈ 영역 40%, 소형 타일당 라벨 ≤ 4어 + 단문 1줄(22px). 최소 타일 ≈ 260×130px.
- **built_on**: `.s-full`, `.canvas-fill`, `.s-eyebrow`, `.s-title`, `.accent-bar`, CSS grid 타일(span), `.card`(+`.surface`), `.pill`
- **content_slots**: eyebrow, title, accent, hero_tile{label, body}, tiles[5..6]{label, fact}
- **sketch**:
```
┌──────────────────────────────────────────────┐
│ EYEBROW                                       │
│  한 줄 인사이트 제목            ▂▂ accent      │
├─────────────────────────┬────────────────────┤
│                         │   타일 2           │
│   히어로 타일 (대)      ├────────────────────┤
│                         │   타일 3           │
├───────────┬─────────────┴────────────────────┤
│  타일 4   │  타일 5     │  타일 6            │
└───────────┴─────────────┴────────────────────┘
```
- **coded**: no
- **density_note**: 12열 grid에 span으로 타일 크기 분배(hero 6~7열×2행, 소형 3~4열). 최소 타일도 라벨 22px + 1줄이 상한 — 그 이하로 조밀해지면 하한 붕괴. 히어로 타일 하나만 블루 강조, 나머지 `--surface` 중립.
- **source**: https://www.wearedevelopers.com/en/magazine/682/building-a-bento-grid-layout-with-modern-css-grid-682 (verified — 12열 공유 그리드에 span/dense로 히어로+소형 비대칭 타일 배치 확인)
- **adaptation_note**: 벤토의 "공유 12열 그리드 + 비대칭 span 타일" 골격만 차용. Apple/SaaS 랜딩 비주얼을 복제하지 않고 `.card.surface` 타일 + grid span으로 재표현. 히어로에 대표 항목·소형에 단일 사실 하나씩. 40s 하한 탓에 6~7 타일로 제한(원본 landing의 9+ 타일 밀도는 축약).
