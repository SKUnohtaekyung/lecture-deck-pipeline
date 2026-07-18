# charts-ratio — 비율·비중·완성도·순위를 그리는 재사용 차트 element (부분-전체·게이지·발산·순위 그룹)

> 이 파일의 항목은 **whole-slide가 아니라 레이아웃 위에 얹는 재사용 fragment(element)** 다 — 레이아웃 ≠ 다이어그램(카탈로그-규격 §5). 각 항목은 `element_vs_slide`로 fragment(`.viz-<slug>`)를 whole-slide와 분리 선언하고, 얹을 레이아웃은 카탈로그에서 **따로** 골라 그 안에 얹는다.
> 판단 축: [`정보모양-taxonomy.md`](../guide/정보모양-taxonomy.md) 12모양(값은 이 안에서만) · 스키마: [`카탈로그-규격.md §5`](../guide/카탈로그-규격.md) · 토큰·세로예산: [`토큰-치트시트.md`](../guide/토큰-치트시트.md).
> 전부 **코드-viz**(CSS/SVG, 이미지 아님) — 숫자·틱·라벨은 텍스트로 선택·복사 가능. 색은 문법: **강조 조각/값 1곳 `--blue` · 주의·경고 `--coral-deep` · 오류 `--red` · 안전·달성 `--mint-deep` · 비강조는 `--periwinkle`/`--surface`**.
> 캔버스 기준: `.s-full` 사용역 = 폭 1152px(1280−64−64) · 세로 약 548px(top 118 → bottom 54). 아래 capacity는 전부 이 값과 가독성 하한(본문 22px·틱/라벨 ≥19px)에서 스크롤·오버플로 없이 성립하도록 검산했다.
> **no-default**: 어떤 element도 "기본/가장 흔한 차트"로 규정하지 않는다 — 5종은 데이터 모양에 따라 동급으로 갈린다.

---

### C-pie — 파이(부분-전체 조각) / Pie (Part-to-Whole Slices)

- **id**: `C-pie`
- **kind**: chart
- **name**: 파이(부분-전체 조각) / Pie
- **info_shapes**: `[numeric]`
- **data_shape**: 단일 계열의 **부분-전체 비중** — 조각 2~6개, 합 ≈ 100%(하나의 전체를 나눔). 조각 크기가 서로 구분될 때(가장 큰/작은 몫이 논지). 음수·시계열·조각 합이 전체와 다른 데이터에는 부적합.
- **when_to_use**: "무엇이 전체의 몇 %를 차지하나"가 논지이고 한두 조각의 **몫(share)** 을 부각할 때. 정밀 순위보다 "이 조각이 절반이 넘는다/제일 크다" 같은 비율 인상이 핵심일 때.
- **when_to_avoid**: 조각이 6개를 넘거나 크기가 서로 비슷해 눈으로 구분이 안 될 때(→ 정렬 막대/`C-lollipop`), 값이 시계열·연속량일 때(→ column/line), 여러 전체를 비교할 때(파이 여러 개 금지 → 막대). 정밀 값 비교가 필요할 때.
- **capacity**: 조각 **≤6**(권장 3~5). 지름 ~360px(중앙 무대), 세로 548px 안에 지름 + 범례 2줄 수용. 조각 라벨은 조각 안(큰 조각) 또는 우측 범례(작은 조각), 라벨/값 ≥19px. 강조 조각 1개만 `--blue`, 나머지 `--periwinkle`~`--surface` 계조. 조각당 라벨 ≤4어.
- **element_vs_slide**: **fragment** = `.viz-pie`(SVG `<circle>` 하나에 `stroke-dasharray`로 조각을 그리거나 `<path>` 부채꼴, + 우측 `.viz-legend` 텍스트 범례). whole-slide 클래스 아님. **얹는 데모 host = 별도** — 예: `.center-msg`에 얹은 `L-ct-figure`(centered) 또는 `.s-full` 히어로 `L-dc-hero`(diagram-centric). host 레이아웃은 카탈로그에서 따로 선택.
- **placement[]**: `[centered, diagram-centric, split, grid-mosaic]`
- **built_on**: `--blue`(강조 조각)·`--periwinkle`/`--surface`(비강조 계조)·`--line`(테두리)·`--ink`/`--gray-700`(라벨). 텍스트 프리미티브 `.s-eyebrow`·`.pill`(범례 항목). **신규 CSS 요지**: `.viz-pie{display:flex;gap:28px;align-items:center}` + `.viz-pie svg{width:340px;height:340px}`(원 반지름 stroke-dasharray 조각) + `.viz-legend`(항목=색점 12px + 라벨 + 값 19px). SVG라 배율·인쇄에 항상 선명.
- **a11y**: `role="img"` + `aria-label`에 조각·값을 문장으로. 패턴: `aria-label="비중 파이: A 52%, B 28%, C 20%"`. 범례 텍스트는 실제 DOM 텍스트로 중복 제공.
- **sketch**:
```
┌──────────────────────────────────────────────┐
│  ▍EYEBROW                                      │
│        ___                ● A  52%  (강조)     │
│      /  A  \\   ┌legend┐   ● B  28%            │
│     | ▓▓▓▓  |   │      │   ● C  20%            │
│      \\ B C /                                   │
│        ‾‾‾   ← 강조 조각만 블루, 나머지 계조   │
└──────────────────────────────────────────────┘
```
- **coded**: no
- **source**: https://www.practicalreporting.com/blog/2024/7/25/how-many-slices-can-you-put-in-a-pie-chart (WebFetch 검증 2026-07-12, 열림 — "part-to-whole", "fractions of the total"; 조각이 비슷·다수로 라벨될 때 실패) · 보강 https://www.beautiful.ai/blog/battle-of-the-charts-pie-chart-vs-donut-chart (열림 — "don't want to display more than six categories")
- **adaptation_note**: 템플릿의 무지개 3D 파이·그림자 복제 금지. 단일 계열을 SVG 조각으로 재표현하되 **강조 조각 1개만 `--blue`**, 나머지는 `--periwinkle`→`--surface` 무채 계조로 위계를 만든다(색을 데이터 라벨이 아니라 강조에 쓴다). 조각 6 초과·유사 크기면 항목을 정렬 막대(`C-lollipop`)로 넘기고 파이를 쓰지 않는다.

---

### C-donut — 도넛(중앙 요약 라벨) / Donut (Center-Label Part-to-Whole)

- **id**: `C-donut`
- **kind**: chart
- **name**: 도넛(중앙 요약 라벨) / Donut
- **info_shapes**: `[numeric]`
- **data_shape**: 파이와 같은 **부분-전체 비중**(조각 2~5, 합≈100%)에 더해, 중앙 구멍에 얹을 **요약 수치 1개**(총합·핵심 몫·전체 증감률 등)가 있을 때. 조각이 2~4개로 적고 하나의 대표 숫자가 함께 강조돼야 할 때 특히.
- **when_to_use**: 비중을 보이면서 **동시에 하나의 KPI(총합·핵심 %)** 를 중앙에 크게 세우고 싶을 때 — "전체 1,250건 중 이 몫" 식으로 몫과 총량을 한 도형에서.
- **when_to_avoid**: 중앙에 세울 요약 수치가 없을 때(그냥 `C-pie`), 조각이 5개를 넘어 얇은 링이 읽히지 않을 때, 정밀 값 비교가 필요할 때(→ 막대). 단일 값 대 목표만 있으면 게이지(`C-gauge`)가 맞다.
- **capacity**: 조각 **≤5**(권장 2~4). 링 두께 ~44px, 외경 ~320px. 중앙 요약 = 큰 숫자 ≤5자(≈40px 800) + 아래 라벨 1줄(≥19px). 범례 우측 ≤5행. 주요 조각과 구조 라벨은 `--blue`, 나머지는 `--periwinkle` 또는 중립으로 두어 판독 순서를 만든다.
- **element_vs_slide**: **fragment** = `.viz-donut`(SVG 두 겹 `<circle>` + `stroke-dasharray` 조각, 중앙 `foreignObject`/겹친 `div`에 `.viz-donut-center` 요약). whole-slide 아님. **얹는 데모 host = 별도** — 예: `.s-full` 격자 타일 `L-gm-bento`(grid-mosaic, 대표 KPI 타일) 또는 `.center-msg` `L-ct-figure`(centered). host는 카탈로그에서 따로 고른다.
- **placement[]**: `[centered, diagram-centric, grid-mosaic, split]`
- **built_on**: `--blue`(강조 조각/중앙 값)·`--periwinkle`/`--surface`(비강조 링)·`--line`·`--ink`/`--gray-700`(중앙 라벨). `.s-eyebrow`·`.pill`(범례). **신규 CSS 요지**: `.viz-donut{position:relative}` + `.viz-donut svg circle{fill:none;stroke-width:44}` + `.viz-donut-center{position:absolute;inset:0;display:grid;place-items:center;text-align:center}`(숫자 40px/800 + 라벨 19px). `C-pie`의 조각 로직 재사용 + 내부 반경만 확보.
- **a11y**: `role="img"` + `aria-label`에 중앙 요약 + 조각. 패턴: `aria-label="도넛: 전체 1,250건 — 완료 62%, 진행 24%, 대기 14%"`. 중앙 숫자·범례는 실제 텍스트로도 존재.
- **sketch**:
```
┌──────────────────────────────────────────────┐
│  ▍EYEBROW                                      │
│         ___                 ● 완료 62% (강조)   │
│       /█████\\    legend     ● 진행 24%         │
│      | 1,250  |              ● 대기 14%         │
│      |  전체  |   ← 중앙 요약 수치 1개           │
│       \\_____/                                   │
└──────────────────────────────────────────────┘
```
- **coded**: no
- **source**: https://www.beautiful.ai/blog/battle-of-the-charts-pie-chart-vs-donut-chart (WebFetch 검증 2026-07-12, 열림 — "use a donut chart so you can take advantage of the space in the middle", "between 2 and 4 categories, go with a donut chart")
- **adaptation_note**: 대시보드 위젯의 네온 그라데이션·그림자 링 복제 금지. 링은 `--periwinkle`/`--surface` 비강조 + 강조 조각 1개 `--blue`로 재표현하고, 중앙 요약은 `.viz-donut-center`에 큰 숫자(≤5자) + 라벨 1줄로 가독성 하한을 지킨다. 조각 강조와 중앙 숫자 중 **블루는 한 곳만** — 둘 다 블루로 칠하지 않는다.

---

### C-gauge — 게이지·프로그레스(단일 비율/완성도) / Gauge & Progress (Single Ratio)

- **id**: `C-gauge`
- **kind**: chart
- **name**: 게이지·프로그레스(단일 비율/완성도) / Gauge & Progress
- **info_shapes**: `[numeric]`
- **data_shape**: **단일 값 1개 대 목표/범위**(0~100% 또는 min~max) — 달성률·완성도·진척·점유율. 임계 구간(안전/주의/위험)이 있으면 색 존으로. 반원 아크(게이지) 또는 가로 바(프로그레스) 변형. 비교 대상이 여러 개거나 목표가 없으면 부적합.
- **when_to_use**: 하나의 결정적 숫자를 **목표/한도 대비 위치**로 즉시 읽히고 싶을 때 — "80% 달성", "예산 62% 소진". 임계값(민트≥목표·코랄 주의·레드 미달)으로 좋고/나쁨을 색으로 전할 때.
- **when_to_avoid**: 측정할 명확한 목표·범위가 없을 때, 여러 항목을 나란히 비교할 때(게이지 여러 개 금지 → 막대/`C-lollipop`), 부분-전체 구성이 논지일 때(→ pie/donut). 추세를 볼 때(→ line/column).
- **capacity**: 게이지/바 **1개**(한 슬라이드 KPI 스트립이면 최대 3~4개까지 나란히, 각 독립 값). 아크 반원 폭 ~420px 또는 가로 바 폭 ≤900px·높이 28px. 중앙/우측 큰 값 ≤5자(≈48px 800) + 목표·범위 끝값 라벨(0·목표·100) ≥19px. 존 색 ≤3(민트/코랄/레드).
- **element_vs_slide**: **fragment** = `.viz-gauge`(SVG 반원 아크 2겹: 배경 트랙 + 값 아크 `stroke-dasharray`, 중앙 값 텍스트) **또는** 가로 변형 `.viz-progress`(트랙 `div` + 채움 `div` + 목표 눈금). whole-slide 아님. **얹는 데모 host = 별도** — 예: `.s-full` KPI 스트립 `L-td-metric-row`(top-down) 또는 단일 초대형 `L-fb-bignum`(full-bleed)에 보조로, 또는 `L-gm-bento` 타일. host는 카탈로그에서 따로 고른다.
- **placement[]**: `[top-down, grid-mosaic, centered, full-bleed]`
- **built_on**: `--mint-deep`/`--mint-soft`(달성·안전 존)·`--coral-deep`(주의)·`--red`(미달)·`--blue`(중립 강조 값)·`--surface`/`--line`(트랙)·`--ink`(값). `.timing`(목표 배지)·`.s-eyebrow`. **신규 CSS 요지**: `.viz-gauge svg` 반원 아크(반지름 큰 원 절반 + `stroke-linecap:round`) · `.viz-progress{height:28px;border-radius:14px;background:var(--surface)}` + `.viz-progress > i{display:block;height:100%;border-radius:14px;background:var(--blue)}` + 목표 눈금 `.viz-progress .goal{position:absolute}`. 값·목표는 텍스트.
- **a11y**: `role="img"` + `aria-label`에 값·목표·상태. 패턴: `aria-label="달성률 게이지: 80% (목표 75% 초과 — 안전)"`. 값·라벨은 실제 텍스트.
- **sketch**:
```
┌──────────────────────────────────────────────┐
│  ▍EYEBROW                                      │
│          ╭────────────╮                        │
│        ╭─╯    80%      ╰─╮   ← 반원 아크 게이지  │
│       0│  달성 (목표75) │100                     │
│                                                │
│   또는 ▶ [■■■■■■■■□□] 80%  │목표             │  가로 프로그레스
└──────────────────────────────────────────────┘
```
- **coded**: no
- **source**: https://blacklabel.net/blog/data-visualization/chart-types/get-up-to-speed-with-gauge-charts/ (WebFetch 검증 2026-07-12, 열림 — "a single metric on a predefined range", "perfect for showing progress toward a goal", "avoid gauge charts if there's no specific goal", "side-by-side gauges are visually cluttered and hard to compare")
- **adaptation_note**: 스큐어모픽 속도계 눈금·바늘 그림자 복제 금지. 반원 아크 + 값 텍스트로 재표현하고, **존 색은 문법대로** — 달성/안전 `--mint-deep`, 주의 `--coral-deep`, 미달 `--red`, 목표가 중립이면 값 아크만 `--blue`. 여러 항목 비교로 번지면 게이지를 버리고 정렬 막대로 넘긴다(1값-1목표 원칙).

---

### C-diverging — 발산 막대(전후·A/B 대칭) / Diverging Bars (Before-After · A/B)

- **id**: `C-diverging`
- **kind**: chart
- **name**: 발산 막대(전후·A/B 대칭) / Diverging Bars
- **info_shapes**: `[numeric, comparison]`
- **data_shape**: **공통 기준선(0·중립·목표)에서 양방향으로 발산**하는 항목별 값 — 전/후, A/B, gain/loss, 목표 대비 초과/미달, Likert(동의↔반대). 항목마다 좌(음/전/반대)·우(양/후/동의) 대칭 막대. 데이터에 **자연스러운 대립 방향이 없고 전부 양수**면 부적합(그냥 막대로).
- **when_to_use**: 여러 항목에서 **양쪽으로 갈리는 방향성**(늘었나/줄었나, 찬성/반대, 목표 위/아래)을 기준선 하나로 즉시 스캔시킬 때. 항목별 우열이 아니라 "어느 쪽으로, 얼마나 벌어졌나"가 논지일 때.
- **when_to_avoid**: 모든 값이 같은 부호(대립 없음)일 때(→ 단순 막대/`C-lollipop`), 부분-전체 비중일 때(→ pie/donut), 단일 값일 때(→ gauge), 항목이 8개를 넘어 세로가 부족할 때.
- **capacity**: 항목 **≤7행**(권장 4~6). 세로예산 548px ÷ 행높이(막대 34px + gap 22px ≈ 56px) → 7행 ≈ 392px + 축·범례 여유. 좌우 최대 폭 각 ~430px(중앙 기준선 기준). 값 라벨 막대 끝 ≥19px. 한 방향(예: 개선/양)만 `--mint-deep` 또는 `--blue`, 반대 방향 `--coral-deep`/`--red` 또는 `--periwinkle` — 방향=색.
- **element_vs_slide**: **fragment** = `.viz-diverging`(항목 행마다 중앙 기준선 기준 좌/우 두 `.viz-bar`, 가운데 항목 라벨 열). whole-slide 아님. **얹는 데모 host = 별도** — 예: `.s-full` `L-td-compare-bars`(top-down, 값 비교 밴드) 또는 `L-dc-hero`(diagram-centric). host는 카탈로그에서 따로 고른다. 데모_제작규칙의 `.code-chart`/`.cc-*`(가로 막대 로직) 재사용 가능.
- **placement[]**: `[top-down, diagram-centric, comparison-symmetric]`
- **built_on**: `--mint-deep`(개선/양)·`--coral-deep`/`--red`(악화/음)·`--blue`(중립 강조)·`--periwinkle`(비강조)·`--line`(기준선·축)·`--ink`(라벨). 기존 `.code-chart`/`.cc-fill` 재사용. **신규 CSS 요지**: `.viz-diverging{display:grid;grid-template-columns:1fr auto 1fr}`(좌 막대 | 라벨 | 우 막대) + 중앙 `border-left:2px solid var(--line)` 기준선 + `.viz-bar`(높이 34px, 좌측은 `justify-self:end`·`flex-direction:row-reverse`). 값은 텍스트.
- **a11y**: `role="img"` + `aria-label`에 항목별 방향·값. 패턴: `aria-label="전후 발산 막대: 응답속도 -40%(개선), 비용 +12%(악화), 만족도 +25%(개선)"`. 항목·값은 실제 텍스트.
- **sketch**:
```
┌──────────────────────────────────────────────┐
│  ▍EYEBROW              │0(기준선)              │
│         ■■■■■ -40% │ 응답속도 │                │  ← 좌=개선(민트)
│               ■■ │ 비용     │ +12% ■■          │  ← 우=악화(코랄)
│           ■■■ -18%│ 오류율   │                 │
│                   │ 만족도   │ +25% ■■■■        │
│       (좌 음/전)   라벨   (우 양/후)             │
└──────────────────────────────────────────────┘
```
- **coded**: no
- **source**: https://datavizcatalogue.com/blog/chart-snapshot-diverging-bar-charts/ (WebFetch 검증 2026-07-12, 열림 — "comparison of two opposing or diverging perspectives, such as agree or disagree, for or against", "not suitable for visualising neutral dimensions or continuous data")
- **adaptation_note**: 원본의 스택형 Likert 그라데이션 복제 금지 — 여기선 항목당 좌/우 단일 발산 막대로 단순화. **방향을 색 문법에 매핑**: 개선/양 `--mint-deep`(또는 중립 강조 `--blue`), 악화/음 `--coral-deep`/`--red`, 비강조 `--periwinkle`. 기준선(0/목표)은 `--line` 2px로 명시. 전부 같은 부호면 발산 구조를 버리고 단순 정렬 막대로.

---

### C-lollipop — 롤리팝·점 순위(희소 비교) / Dot-Lollipop Ranking (Sparse Compare)

- **id**: `C-lollipop`
- **kind**: chart
- **name**: 롤리팝·점 순위(희소 비교) / Dot-Lollipop Ranking
- **info_shapes**: `[numeric, comparison]`
- **data_shape**: **1 범주축 × 1 수치**의 항목별 값을 정렬한 **순위/점 비교** — 값이 서로 비슷해 굵은 막대가 뭉개지거나 단조로울 때, 얇은 스템 + 점으로 순위(내림차순)를 깔끔히. 두 시점 비교면 점 2개(덤벨/dot-plot). 여러 값·분포(오차)면 부적합.
- **when_to_use**: 항목이 여러 개인 **단일 측정치의 순위**를 정렬해 "제일 높은/낮은 것"과 간격을 스캔시킬 때. 막대가 잉크로 무거워지거나 값들이 근접해 막대 길이 차가 안 보일 때의 가벼운 대안.
- **when_to_avoid**: 부분-전체 비중일 때(→ pie/donut), 정렬이 불가·무의미할 때(→ 그냥 막대), 항목당 값이 여럿(분포·오차)일 때(→ box/violin), 시계열 연속량일 때(→ line). 정밀 길이 비교가 최우선일 때(→ 막대).
- **capacity**: 항목 **≤10행**(정렬 필수, 권장 5~8). 세로예산 548px ÷ 행높이(점 지름 18px + 라벨 + gap ≈ 48px) → 10행 ≈ 480px. 값축 폭 ~760px, 항목 라벨 좌측 열 ≤8어. 점/값 ≥19px. 강조 항목(1위 또는 대상) 1개만 `--blue` 점, 나머지 `--periwinkle`. 스템 `--line`.
- **element_vs_slide**: **fragment** = `.viz-lollipop`(항목 행마다 좌측 라벨 + 스템 라인 + 끝 `.viz-dot` + 값 텍스트; 정렬은 마크업 순서). 두 시점이면 점 2개 + 연결선(덤벨). whole-slide 아님. **얹는 데모 host = 별도** — 예: `.s-full canvas-fill` `L-td-table`/`L-td-metric-row` 자리 또는 `L-dc-hero`(diagram-centric), 우측 시각으로 `split`. host는 카탈로그에서 따로 고른다.
- **placement[]**: `[top-down, diagram-centric, split]`
- **built_on**: `--blue`(강조 점 1개)·`--periwinkle`(비강조 점)·`--line`(스템·축)·`--ink`/`--gray-700`(라벨·값)·덤벨 비교면 두 점 `--periwinkle`↔`--blue`. `.s-eyebrow`·`.pill`. **신규 CSS 요지**: `.viz-lollipop{display:flex;flex-direction:column;gap:14px}` + 행 `.viz-lolli{display:grid;grid-template-columns:180px 1fr auto;align-items:center}` + 스템 `.viz-stem{height:2px;background:var(--line)}` + `.viz-dot{width:18px;height:18px;border-radius:50%}`. 스템 폭 = 값 비례. 값은 텍스트.
- **a11y**: `role="img"` + `aria-label`에 순위·값. 패턴: `aria-label="순위 롤리팝(내림차순): 서울 42, 부산 31, 대구 27, 인천 19"`. 항목·값은 실제 텍스트로 존재.
- **sketch**:
```
┌──────────────────────────────────────────────┐
│  ▍EYEBROW                                      │
│  서울   ●━━━━━━━━━━━━━━━━━━  42  (강조=블루)   │
│  부산   ●━━━━━━━━━━━━  31                        │
│  대구   ●━━━━━━━━━━  27                          │
│  인천   ●━━━━━━  19                              │
│         (정렬 내림차순 · 얇은 스템 + 점)          │
└──────────────────────────────────────────────┘
```
- **coded**: no
- **source**: https://www.data-to-viz.com/graph/lollipop.html (WebFetch 검증 2026-07-12, 열림 — "a barplot, where the bar is transformed in a line and a dot", "excels when many bars share similar heights", "Order your groups ... following their values") · 보강 https://datavizcatalogue.com/ (롤리팝/점 비교)
- **adaptation_note**: 원본의 다색 점·굵은 스템 복제 금지. 스템은 `--line` 얇게, 점은 비강조 `--periwinkle`, 주요 대상·순위·구조선은 `--blue`로 둔다. 반드시 값 내림차순 정렬(무정렬이면 순위 논지가 깨져 막대로 되돌린다). 두 시점 비교는 덤벨(점 2개 + 연결선)로 확장하되 색은 `--periwinkle`↔`--blue` 두 톤만.

---

## 커버리지 메모 (이 그룹)

- **모두 code-viz**(SVG/CSS) — 이미지 0, 숫자·라벨은 텍스트. 색은 문법(구조·주 강조 블루 · 주의·경고 코랄 · 오류 레드 · 안전·달성 민트 · 비강조 periwinkle).
- **부분-전체**(`C-pie`·`C-donut`) · **단일 비율**(`C-gauge`) · **방향 발산**(`C-diverging`) · **순위 점비교**(`C-lollipop`) — 데이터 모양별로 갈리며 어느 것도 기본이 아님(no-default).
- 전부 `numeric` 계열(+ 발산·순위는 `comparison` 겸). `../charts/by-shape.md`의 numeric/comparison 아래에 등재해 레이아웃 host와 조합한다(레이아웃 ≠ element).
- fragment 클래스는 전부 `.viz-<slug>` — `.viz-pie`·`.viz-donut`·`.viz-gauge`(+`.viz-progress`)·`.viz-diverging`·`.viz-lollipop`. whole-slide 클래스로 승격 금지.
