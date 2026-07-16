# comparison-symmetric — 2~3개 동등 패널(주/부 강조 없음)을 대칭 grid로 나란히 놓아 비교·대비를 한눈에 견주게 하는 구도 패밀리.

> 판단 축: [`정보모양-taxonomy.md`](../../guide/정보모양-taxonomy.md) · 스키마: [`카탈로그-규격.md §4`](../../guide/카탈로그-규격.md) · 토큰: [`토큰-치트시트.md`](../../guide/토큰-치트시트.md)
> 이 패밀리의 핵심 제약: **패널 간 시각 위계 없음**(같은 폭·같은 스타일·같은 무게). 한쪽을 크게/진하게 만들면 split·top-down으로 이탈한 것이다.
> 캔버스 기준: `.s-full` 사용역 = 폭 1152px(1280−64−64), 세로 약 548px(top 118 → bottom 54). 아래 용량은 전부 이 값과 40~50대 폰트 하한(본문 22px·표 17px)에서 스크롤 없이 성립하도록 계산했다.

---

### L-cs-side-by-side — 짝지은 2열 패널 / Paired Side-by-Side Panels

- **id**: `L-cs-side-by-side`
- **name**: 짝지은 2열 패널 / Paired Side-by-Side Panels
- **composition_family**: comparison-symmetric
- **composition_shape**: `panels-mirror`
- **info_shapes**: [comparison, contrast]
- **when_to_use**: 두 대안을 같은 기준 3~4개로 행 정렬해 나란히 견줄 때. 각 기준이 좌우에서 같은 높이에 마주 보게 해 "항목별 우열"을 스캔시키고 싶을 때.
- **when_to_avoid**: 대안이 1개거나 4개 이상일 때. 한쪽을 추천/강조해 무게를 실어야 할 때(→ split이나 top-down). 기준이 8개↑라 표가 더 촘촘히 담길 때(→ L-cs-dual-table).
- **capacity**: 좌우 각 열 = 헤더 1줄(≤6어) + 짝지은 행 3~4개, 행마다 본문 22px 기준 ≤2줄(약 ≤14어). 열 폭 ≈ 569px. 가운데 아이콘 레일은 행당 기호 1개.
- **built_on**: `.s-full`, `.grid-2`, `.card`(+`.surface`), `.s-lead`(열 헤더), `.s-body`, `.pill`, `.accent-bar`(열 헤더 색바)
- **content_slots**: title, left_header, right_header, row_label[×3~4], left_cell[×n], right_cell[×n], center_icon[×n]
- **sketch**:
```
┌──────────────────────────────────────────────┐
│  타이틀 한 줄                                 │
│ ┌─────────────┐  ·  ┌─────────────┐          │
│ │ ▔ A 헤더    │ (◇) │ ▔ B 헤더    │          │
│ ├─────────────┤     ├─────────────┤          │
│ │ 기준1 · 값  │ (◇) │ 기준1 · 값  │          │
│ │ 기준2 · 값  │ (◇) │ 기준2 · 값  │          │
│ │ 기준3 · 값  │ (◇) │ 기준3 · 값  │          │
│ └─────────────┘     └─────────────┘          │
└──────────────────────────────────────────────┘
   좌우 동폭(569px), 가운데 레일이 행을 짝지음
```
- **coded**: no
- **density_note**: 본문 22px/1.78 → 행당 최대 2줄에서 열 세로 548px에 헤더+4행이 여유 있게 들어감. 5행부터 행 높이 압박 → 4행 상한. 색은 좌/우 헤더 accent-bar에만(블루 1곳 원칙 유지, 중립 비교면 양쪽 `--ink`).
- **source**: https://www.presentationgo.com/presentation/side-by-side-comparison-template/ (WebFetch 검증 2026-07-12, 열림 — 3+3 블록·중앙 아이콘 레일·짝 정렬 확인)
- **adaptation_note**: 원본의 그림자 띄운 흰 중앙 패널은 복제하지 않는다. `.grid-2` 두 `.card.surface`로 좌우 동폭을 만들고, 중앙 세로 레일은 별도 요소 없이 grid gap(14px) 위에 얹은 얇은 아이콘 열(각 행 top에 정렬)로 대체. 헤더 구분은 `.accent-bar` 색만 다르게, 폰트 무게·크기는 동일하게 두어 위계 0을 강제. 행 짝맞춤은 좌우 카드 안에서 같은 순서의 `.s-body li`로.

---

### L-cs-central-contrast — 중앙 커넥터 대비 2블록 / Central-Connector Contrast

- **id**: `L-cs-central-contrast`
- **name**: 중앙 커넥터 대비 2블록 / Central-Connector Contrast
- **composition_family**: comparison-symmetric
- **composition_shape**: `panels-mirror`
- **info_shapes**: [contrast]
- **when_to_use**: 두 입장/상태의 대립을 긴장으로 보여줄 때(추천 없음). "쓰는 쪽 ↔ 하는 쪽" 같은 이항 대비를 가운데 `≠` 커넥터로 명시하고 싶을 때.
- **when_to_avoid**: 항목별 우열을 여러 기준으로 따질 때(→ L-cs-side-by-side). 한쪽으로 결론을 유도할 때. 대비 주체가 3개↑일 때.
- **capacity**: 좌우 각 블록 = 헤더 ≤6어 + 본문 ≤3줄(22px) + 선택 pill 1개. 중앙 원형 커넥터가 폭을 먹어 각 블록 실폭 ≈ 500px. 문장은 짧게.
- **built_on**: `.s-full`, `.grid-2`, `.card`, `.s-lead`, `.s-body`, `.pill`, 관계 커넥터(가운데 `≠` — 블루 원/기호)
- **content_slots**: title, left_stance_header, left_body, right_stance_header, right_body, connector_symbol, left_tag, right_tag
- **sketch**:
```
┌──────────────────────────────────────────────┐
│  타이틀: 두 입장의 대립                       │
│ ┌────────────┐   ╭───╮   ┌────────────┐      │
│ │ 입장 A      │   │ ≠ │   │ 입장 B      │      │
│ │ 본문 ≤3줄   │   ╰───╯   │ 본문 ≤3줄   │      │
│ │ [태그]      │  (중앙     │ [태그]      │      │
│ └────────────┘   커넥터)   └────────────┘      │
└──────────────────────────────────────────────┘
   좌우 미러 · 가운데 ≠ 로 긴장 명시
```
- **coded**: no
- **density_note**: 본문 22px에서 블록당 3줄이면 세로 여유 충분(블록 높이 ~300px). 색-문법: 대비 강조는 좌/우 카드 border 색만(예: 한쪽 `--ink`, 한쪽 `--blue`) — 어느 쪽도 "정답"으로 안 보이게 채도 대등하게. 중앙 `≠`는 블루 1곳.
- **source**: https://www.presentationgo.com/presentation/central-contrast-comparison-powerpoint-google-slides/ (WebFetch 검증 2026-07-12, 열림 — 중앙 원 커넥터·좌우 미러 블록·색 테두리 대비 확인)
- **adaptation_note**: 원본의 큰 중앙 원+아이콘 프레임을 통째로 복제하지 않는다. `.grid-2` 두 카드를 미러로 놓고, 가운데는 grid gap 위에 블루 `≠` 기호 하나(작은 `.num-circle` 스타일 원)만 얹어 커넥터로. 색 테두리는 토큰(`--ink`/`--blue`)만 쓰고 raw hex 금지. 두 블록의 폰트 크기·무게를 동일하게 고정해 주/부 강조 0을 지킨다.

---

### L-cs-triptych — 동등 3열 트립틱 / Equal Three-Column Triptych

- **id**: `L-cs-triptych`
- **name**: 동등 3열 트립틱 / Equal Three-Column Triptych
- **composition_family**: comparison-symmetric
- **composition_shape**: `panels-mirror`
- **info_shapes**: [comparison]
- **when_to_use**: 세 대안/옵션을 같은 틀로 병렬 비교할 때(3자 견주기). 각 열이 짧은 헤더 + 2~3개 특징을 담아 한눈에 훑게 하고 싶을 때.
- **when_to_avoid**: 대안이 2개일 때(→ 2열 계열). 열마다 담을 내용이 길어 3열 폭(≈374px)에 문장이 넘칠 때. 한 옵션을 추천으로 키워야 할 때.
- **capacity**: 3열 각 폭 ≈ 374px. 열당 헤더 1줄(≤4어) + 항목 2~3개, 각 항목 22px 기준 ≤1줄(≤7어) 또는 짧은 스탯 1 + 캡션 1줄. 열 상단 색바로 구분.
- **built_on**: `.s-full`, `.grid-3`, `.card`(+`.surface`), `.s-lead`, `.s-body`, `.accent-bar`, `.pill`
- **content_slots**: title, col_header[×3], col_item[×3 per col], col_tag[×3]
- **sketch**:
```
┌──────────────────────────────────────────────┐
│  타이틀: 세 옵션 비교                          │
│ ┌────────┐  ┌────────┐  ┌────────┐            │
│ │ ▔ 옵션A │  │ ▔ 옵션B │  │ ▔ 옵션C │            │
│ │ · 특징1 │  │ · 특징1 │  │ · 특징1 │            │
│ │ · 특징2 │  │ · 특징2 │  │ · 특징2 │            │
│ │ [태그]  │  │ [태그]  │  │ [태그]  │            │
│ └────────┘  └────────┘  └────────┘            │
└──────────────────────────────────────────────┘
   3열 동폭(374px) · 위계 없음
```
- **coded**: no
- **density_note**: 좁은 3열이라 본문 22px에서 항목당 1줄이 안전선(2줄이면 3항목에서 세로 압박). `word-break:keep-all`로 한글 어절 유지. 색바(`.accent-bar`)는 세 열 모두 같은 무게, 블루 강조는 슬라이드 전체에서 1곳(예: 헤더 타이틀의 `.hl`)만.
- **source**: https://gridmakerpro.com/grids/design-templates/poster-editorial/ (WebFetch 검증 2026-07-12, 열림 — 동폭 3열·거터·flowline 모듈·병렬 카테고리 구조 확인)
- **adaptation_note**: 에디토리얼 그리드의 이미지-텍스트 혼합 모듈을 그대로 옮기지 않는다. `.grid-3` 세 `.card.surface`로 동폭 3열만 취하고, 각 열은 헤더 색바 + `.s-body` 불릿 2~3로 텍스트 전용화(1280×720에서 이미지 모듈은 세로를 못 버팀). 거터는 grid gap 14px로 고정, 열 폭은 1fr 균등으로 대칭 강제.

---

### L-cs-before-after — 상하 동등 밴드 전/후 / Stacked Before-After Bands

- **id**: `L-cs-before-after`
- **name**: 상하 동등 밴드 전/후 / Stacked Before-After Bands
- **composition_family**: comparison-symmetric
- **composition_shape**: `panels-mirror`
- **info_shapes**: [contrast, comparison]
- **when_to_use**: 두 상태(전 ↔ 후)를 가로 전폭 밴드 둘로 위아래 쌓아 대비할 때. 각 밴드가 넓어 한 줄에 긴 문장/지표행이 들어가야 할 때. 가운데 `↓`로 전이를 명시.
- **when_to_avoid**: 항목별 다기준 비교(→ 열 계열이 스캔 유리). 상태가 3개↑라 밴드가 얇아질 때. 좌우 대비가 개념적으로 더 맞을 때.
- **capacity**: 상/하 밴드 각 세로 ≈ 250px, 폭 1152px 전폭. 밴드당 헤더 1줄(≤5어) + 본문 ≤3줄(22px, 전폭이라 줄당 ≤22어) 또는 지표 3개 나열. 가운데 `↓` 커넥터 1개.
- **built_on**: `.s-full`, `.card`(2단 세로 스택), `.s-lead`, `.s-body`, `.pill`, 관계 커넥터(가운데 `↓`), `.callout`(전=중립/후=green 가능)
- **content_slots**: title, before_header, before_body, after_header, after_body, connector_symbol, metric_pill[×n]
- **sketch**:
```
┌──────────────────────────────────────────────┐
│  타이틀: 전 → 후                              │
│ ┌──────────────────────────────────────────┐ │
│ │ 전(Before) 헤더 · 본문/지표 전폭 ≤3줄     │ │
│ └──────────────────────────────────────────┘ │
│                    ↓  (전이)                  │
│ ┌──────────────────────────────────────────┐ │
│ │ 후(After) 헤더 · 본문/지표 전폭 ≤3줄      │ │
│ └──────────────────────────────────────────┘ │
└──────────────────────────────────────────────┘
   상하 동높이 밴드 · 가운데 ↓
```
- **coded**: no
- **density_note**: 전폭 밴드라 본문 22px에서 줄당 폭이 넓어 3줄이면 밴드 세로 250px에 안착. 두 밴드 높이를 flex로 균등 분할해 위계 0. 색-문법: 후 밴드에만 `.callout.green`(개선/안전)을 절제해 쓰되 전 밴드는 기본 `.callout`(블루-소프트 틴트)로 두어 "값 판단"을 색이 대신 말하게.
- **source**: https://slidemodel.com/templates/tag/before-after/ (WebFetch 검증 2026-07-12, 열림 — 화면 2분할 전/후·주석 화살표로 변화 표시 확인)
- **adaptation_note**: 원본은 좌우 split 예시가 많으나, 이 항목은 **상하 동등 스택**으로 재표현해 split 편향을 피한다(양 밴드 동폭·동높이 → 대칭). 이미지 슬라이더 인터랙션은 정적 덱에 부적합하므로 버리고, 전/후를 두 `.card` 밴드 + 가운데 블루 `↓` 기호로 표현. 지표는 `.pill` 나열로, 표 필요 시 17px 하한 준수.

---

### L-cs-dual-table — 동등 2옵션 비교표 / Dual-Option Comparison Table

- **id**: `L-cs-dual-table`
- **name**: 동등 2옵션 비교표 / Dual-Option Comparison Table
- **composition_family**: comparison-symmetric
- **composition_shape**: `band-grid`
- **variant_of**: `L-td-table` (구도 중복 접기 · 균형 카운트에서 `L-td-table`으로 집계 — 규격 §2b/§3, 본문 보존)
- **info_shapes**: [comparison]
- **when_to_use**: 두 옵션을 기준 6~9개로 촘촘히 견줄 때. 셀에 ✓/✗·짧은 값·수치를 채워 스캔 비교시키고 싶을 때. 카드보다 표 밀도가 필요할 때.
- **when_to_avoid**: 기준이 3~4개뿐이라 표가 헐거울 때(→ L-cs-side-by-side 카드). 옵션이 3개↑라 열이 좁아질 때(표는 2옵션+라벨열에 최적). 긴 서술이 셀에 들어가야 할 때.
- **capacity**: `table.t` 17px 하한 → 행 높이 ≈ 30px. 세로 548px에 헤더행 1 + 속성행 최대 9~10개. 라벨열(좌) + 옵션열 2개 = 3열. 셀은 ✓/✗·값·≤6어.
- **built_on**: `.s-full`, `.canvas-fill`, `table.t`(th 블루·짝수행 연회색), `.pill`, `.s-eyebrow`
- **content_slots**: title, col_option_head[×2], row_attr_label[×6~9], cell[×2 per row]
- **sketch**:
```
┌──────────────────────────────────────────────┐
│  타이틀: A vs B 기준별 비교                    │
│ ┌───────────┬───────────┬───────────┐        │
│ │ 기준       │ 옵션 A    │ 옵션 B    │  ← th   │
│ ├───────────┼───────────┼───────────┤        │
│ │ 기준1      │    ✓      │    ✗      │        │
│ │ 기준2      │   값      │   값      │        │
│ │ 기준3      │    ✓      │    ✓      │        │
│ │ …(≤9행)    │   …       │   …       │        │
│ └───────────┴───────────┴───────────┘        │
└──────────────────────────────────────────────┘
   옵션 2열 동폭 · 속성 행 · 위계 없음
```
- **coded**: no
- **density_note**: 표 17px 하한 절대 준수, 행 9개까지 세로 548px에 무스크롤. 두 옵션열 폭을 동일(1fr)하게 고정하고 th 스타일도 동일 → 주/부 없음. ✓는 `--mint-deep`, ✗는 `--red`로 색-문법만 빌려 값 판단을 절제 표기(전 셀 컬러링 금지).
- **source**: https://www.nngroup.com/articles/comparison-tables/ (WebFetch 검증 2026-07-12, 열림 — 옵션=열·속성=행·좌측 라벨·✓ 스캔·짧은 텍스트 권고 확인)
- **adaptation_note**: NN/g 권고(옵션 열·속성 행·짧은 셀·행 구분)를 `table.t` 프리미티브로 재표현. 원본의 sticky header·다열 확장은 정적 1280×720엔 불필요하므로 2옵션+라벨 3열로 고정. 색은 토큰만(th=`--th` 블루, ✓=`--mint-deep`/✗=`--red`), raw hex·배경 전열 채색 금지. 두 옵션열 대등 → 어느 쪽도 추천으로 안 보이게.
