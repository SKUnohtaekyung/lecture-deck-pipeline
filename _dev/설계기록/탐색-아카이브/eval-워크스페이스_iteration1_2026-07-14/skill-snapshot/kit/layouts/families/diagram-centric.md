# diagram-centric — 시각물(다이어그램/차트)이 주인공, 텍스트는 라벨·캡션으로 최소화한 구도 패밀리

> 이 패밀리는 `.s-full` 풀폭 캔버스 위에 **코드 다이어그램 element 하나**를 무대 전체로 올리고, 문장은 아이브로우·짧은 캡션·노드 라벨 수준으로만 얹는다.
> 주로 맞는 정보 모양: `structure` · `containment` · `mapping` · `flow`. 값은 전부 `정보모양-taxonomy.md` 12개 안에서만 쓴다.
> 모든 항목의 다이어그램은 `charts/diagrams.md`에서 fragment로 따로 골라 **얹는다** — 레이아웃 ≠ 다이어그램(카탈로그-규격 §5).

---

### L-dc-hero — 다이어그램 히어로 / Diagram Hero

- **id**: `L-dc-hero`
- **name**: 다이어그램 히어로 / Diagram Hero
- **composition_family**: `diagram-centric`
- **info_shapes**: `[structure, flow, containment]`
- **when_to_use**: 하나의 다이어그램이 슬라이드의 논지 자체일 때 — 한 장의 그림으로 구조·절차·포함관계를 통째로 보여주고 청중의 시선을 그 그림에 묶고 싶을 때.
- **when_to_avoid**: 다이어그램이 논지의 보조 근거에 불과하고 설명 문장이 주인공일 때(그건 split/top-down로), 또는 시각물이 없이 수치·문장만 있을 때.
- **capacity**: 아이브로우 ≤6어 · 캡션 1줄(≤14어, 22px) · 다이어그램 1개가 캔버스 세로의 ~78%(top 176~672)를 점유. 다이어그램 내부 라벨은 노드당 ≤3어. 콜아웃 0~1.
- **built_on**: `.s-full`, `.s-head`, `.s-eyebrow`, `.accent-bar`, 다이어그램 fragment(`.viz-*`) 1개
- **content_slots**: `eyebrow`, `caption`, `diagram`(fragment)
- **sketch**:
```
┌──────────────────────────────────────────────┐
│ [로고] 브랜드 ── s-line ──────────── 팀명       │  s-head
│  ▍EYEBROW                                      │  s-eyebrow (top 128)
│ ┌────────────────────────────────────────────┐│
│ │                                            ││
│ │            [ 단일 다이어그램 ]               ││  diagram fragment
│ │        구조·절차·포함을 한 장으로           ││  (s-full, ~78% h)
│ │                                            ││
│ └────────────────────────────────────────────┘│
│  한 줄 캡션 — 이 그림이 말하는 것               │  caption 22px
└──────────────────────────────────────────────┘
```
- **coded**: no
- **density_note**: 캡션은 22px/1.78 한 줄 유지, 두 줄 넘으면 어절을 줄여 다이어그램 높이를 침범하지 않게. 다이어그램 라벨은 노드당 ≤3어로 720px 안에서 겹침 없음.
- **source**: https://deckary.com/blog/powerpoint-layout-ideas (verified — "chart fills 70–80% of the slide area", "image fills the entire slide edge-to-edge", 시각이 메시지를 지고 텍스트는 보조)
- **adaptation_note**: 원본의 full-bleed 이미지/차트 지배 아이디어만 차용하고, 배경 사진 대신 `--surface` 위 코드 다이어그램으로 재표현. 헤드라인 오버레이(반투명 검정 박스)는 쓰지 않고 상단 `.s-eyebrow` + 하단 22px 캡션으로 분리해 가독성 하한을 지킨다. 강조는 `--blue` 1곳으로만.

---

### L-dc-annotated — 주석 콜아웃 다이어그램 / Annotated Callout Diagram

- **id**: `L-dc-annotated`
- **name**: 주석 콜아웃 다이어그램 / Annotated Callout Diagram
- **composition_family**: `diagram-centric`
- **info_shapes**: `[structure, mapping]`
- **when_to_use**: 하나의 시각물(구조도·화면·부품도)의 **여러 지점**을 번호로 짚어 각 부분이 무엇인지 대응시킬 때 — 부분↔설명 매핑을 리더선으로 명시.
- **when_to_avoid**: 짚을 지점이 1개거나(그냥 히어로), 6개를 넘어 리더선이 교차·혼잡해질 때. 각 주석이 한 줄로 안 끝나고 문단이 필요할 때.
- **capacity**: 중앙 시각물 1개 + 콜아웃 3~5개(`.num-circle` 번호 + 라벨 ≤6어). 리더선 교차 0. 콜아웃 텍스트 22px 한 줄.
- **built_on**: `.s-full`, `.s-eyebrow`, `.num-circle`, `.pill`, 다이어그램 fragment, 리더선(블루 얇은 라인)
- **content_slots**: `eyebrow`, `diagram`(fragment), `callouts[3..5]`(번호+라벨)
- **sketch**:
```
┌──────────────────────────────────────────────┐
│  ▍EYEBROW                                      │
│   ①─────┐        ┌───────────② 라벨            │
│  라벨    │  ┌───────────┐     │                │
│         └──│  중앙 시각물 │────┘                │  diagram + leader
│   ③───────│  (구조/화면) │                      │  lines
│  라벨      └───────────┘──────④ 라벨            │
│                    │                           │
│                    ⑤ 라벨                       │
└──────────────────────────────────────────────┘
```
- **coded**: no
- **density_note**: 콜아웃 라벨 22px, 각 ≤6어로 리더선 끝에 한 줄. 5개까지는 상/좌/우/하 분산 배치로 720px 안에서 겹치지 않음. 번호 원은 `.num-circle` 민트.
- **source**: https://support.microsoft.com/en-us/office/annotate-a-diagram-by-using-callouts-2f3a8780-4bab-45a3-88dc-ad2ac0b79cb9 (verified — 콜아웃 텍스트 박스가 리더선으로 도형에 연결, 대상 도형에 붙어 함께 이동)
- **adaptation_note**: Visio의 노란 컨트롤 핸들·자동 스타일 대신, `.num-circle`(민트 원 번호)로 키를 매기고 얇은 `--blue` 리더선으로 시각물의 지점에 연결. 키형 콜아웃(번호+짧은 라벨)으로 원본 복제 없이 재구성하고, 설명이 길어지면 별도 슬라이드로 분리.

---

### L-dc-radial-hub — 방사형 허브 / Radial Hub

- **id**: `L-dc-radial-hub`
- **name**: 방사형 허브 / Radial Hub
- **composition_family**: `diagram-centric`
- **info_shapes**: `[containment, mapping, structure]`
- **when_to_use**: 하나의 중심 개념에서 여러 요소가 뻗어 나가는 허브-스포크 관계를 보일 때 — 중심이 위성들을 아우르거나(포함) 중심↔위성이 대응(매핑)될 때.
- **when_to_avoid**: 요소 사이에 순서가 있을 때(그건 flow-canvas), 위성이 8개를 넘어 방사선이 빽빽할 때, 또는 중심이 없는 대등 나열일 때(grid-mosaic로).
- **capacity**: 중심 노드 1개(라벨 ≤5어) + 위성 4~7개(각 라벨 ≤4어). 위성 6개까지 원주에 60° 간격으로 균등. 위성당 보조어 ≤1줄.
- **built_on**: `.s-full`, `.s-eyebrow`, `.card.surface`(중심/위성), 방사 커넥터(블루 라인), 다이어그램 fragment(`.viz-radial`)
- **content_slots**: `eyebrow`, `hub`(중심 라벨), `spokes[4..7]`(위성 라벨)
- **sketch**:
```
┌──────────────────────────────────────────────┐
│  ▍EYEBROW                                      │
│        위성A          위성B                     │
│           \    ┌──────┐   /                    │
│      위성F ─── │ 중심   │ ─── 위성C              │  radial hub
│           /    │ 개념   │   \                    │  (spokes)
│           │    └──────┘    │                    │
│        위성E          위성D                     │
└──────────────────────────────────────────────┘
```
- **coded**: no
- **density_note**: 중심 카드는 `--surface`, 위성 라벨 22px. 위성 6개 기준 반지름 ~230px로 1152폭·560높이 안에 원형 배치, 라벨 겹침 0. 커넥터는 블루 얇은 선.
- **source**: https://blog.infodiagram.com/2020/02/key-visual-diagram-structures-processes-in-powerpoint.html (verified — Structure Diagrams: "centric element and all other items put around it" 방사/허브 배열)
- **adaptation_note**: 원본의 centric 배열 개념만 차용, PowerPoint 클립아트 대신 `.card.surface` 노드 + `--blue` 방사 커넥터로 재표현. 중심 강조는 블루 1곳(테두리 또는 라벨), 위성은 `--periwinkle`급 비강조로 위계를 만들되 색은 토큰만 사용.

---

### L-dc-quadrant — 사분면 매트릭스 / Quadrant Matrix

- **id**: `L-dc-quadrant`
- **name**: 사분면 매트릭스 / Quadrant Matrix
- **composition_family**: `diagram-centric`
- **info_shapes**: `[mapping, structure]`
- **when_to_use**: 두 축(예: 중요도×노력)으로 항목을 4분면에 위치시켜 위치가 곧 판단을 말하게 할 때 — 항목↔좌표 매핑으로 우선순위/포지셔닝을 시각화.
- **when_to_avoid**: 축이 하나거나 연속 추세일 때(numeric 차트로), 항목이 12개를 넘어 점이 뭉칠 때, 또는 4분면에 의미 차이가 없을 때.
- **capacity**: 가로/세로 축 라벨 각 2개(양 끝, ≤3어) + 4분면 이름 각 ≤4어 + 플롯 항목 6~12개(점 라벨 ≤3어). 사분면당 항목 ≤4.
- **built_on**: `.s-full`, `.s-eyebrow`, 축선(블루 십자), `.pill`(플롯 항목), 사분면 배경(`--surface`/`--blue-soft`)
- **content_slots**: `eyebrow`, `axis_x`(양끝 라벨), `axis_y`(양끝 라벨), `quadrant_names[4]`, `items[6..12]`
- **sketch**:
```
┌──────────────────────────────────────────────┐
│  ▍EYEBROW                    ↑ 축Y(고)          │
│        사분면 II    │    사분면 I                │
│         ● 항목      │     ● 항목 ● 항목          │  2x2 matrix
│   축X(저)───────────┼───────────── 축X(고)      │  (plotted pills)
│         ● 항목      │     ● 항목                 │
│        사분면 III   │    사분면 IV               │
│                     ↓ 축Y(저)                   │
└──────────────────────────────────────────────┘
```
- **coded**: no
- **density_note**: 축 라벨 19px eyebrow급, 항목 pill 22px 텍스트. 매트릭스 정사각 ~520×520px가 top 160~680에 들어가 십자축 양끝 라벨까지 720 안에 수용. 강조 항목은 블루 pill 1~2개.
- **source**: https://slidemodel.com/templates/2x2-matrix-quadrants-powerpoint-template/ (verified — 두 수직 축이 4분면 분할, "importance vs. effort", 6~12 항목 배치)
- **adaptation_note**: 중앙 원형 타이틀 도형·클립아트 대신 `--blue` 십자축 + `.pill` 플롯으로 재표현. 사분면 배경은 `--surface`/`--blue-soft` 토큰으로 옅게 구분하고, 추천 사분면만 블루로 강조해 "위치=판단"을 유지. 원본 템플릿 복제 없이 좌표계만 차용.

---

### L-dc-network — 관계 네트워크 맵 / Network Map

- **id**: `L-dc-network`
- **name**: 관계 네트워크 맵 / Network Map
- **composition_family**: `diagram-centric`
- **info_shapes**: `[structure, mapping]`
- **when_to_use**: 여러 개체가 서로 얽힌 관계망(위계 아닌 네트워크)을 보여줄 때 — 노드↔노드 연결 자체가 논지이고, 어느 노드가 허브인지 드러내고 싶을 때.
- **when_to_avoid**: 단일 중심의 방사 구조일 때(radial-hub로), 노드가 ~12개를 넘어 선이 교차·혼잡해질 때, 순서·절차가 핵심일 때(flow로).
- **capacity**: 노드 6~12개(라벨 ≤3어) + 엣지. 교차선 최소화 배치. 방향이 있으면 블루 화살표, 가중치는 선 굵기로. 강조 노드 1~2개.
- **built_on**: `.s-full`, `.s-eyebrow`, 노드(`.num-circle`/작은 `.card`), 엣지(블루/회색 라인), 다이어그램 fragment(`.viz-network`)
- **content_slots**: `eyebrow`, `nodes[6..12]`, `edges`, `legend`(선택, ≤2줄)
- **sketch**:
```
┌──────────────────────────────────────────────┐
│  ▍EYEBROW                                      │
│    (A)───(B)        (E)                         │
│      \   / \       /   \                        │  node-link
│       (C)   (D)──(F)   (G)                      │  network
│         \        │      /                       │
│          (H)────(I)───(J)                       │
│  legend: → 방향 · 굵기=가중치                    │
└──────────────────────────────────────────────┘
```
- **coded**: no
- **density_note**: 노드 라벨 22px(짧으면 `.num-circle` 안 번호+범례). 12노드 기준 선 교차를 재배치로 최소화, 1152×560 안에서 라벨 겹침 0. 범례는 하단 19~22px 한 줄.
- **source**: https://think.design/services/data-visualization-data-design/network-diagram/ (verified — "nodes (circles) and links (lines)", 방향/가중치 4변형, 노드 과다 시 혼잡)
- **adaptation_note**: SmartArt·아이콘 템플릿 대신 `.card`/`.num-circle` 노드와 토큰 색 엣지로 재표현. 방향은 `--blue` 화살표, 비강조 엣지는 `--line`/`--periwinkle`. 노드 수를 캡(≤12) 안으로 두어 정적 슬라이드에서 선이 읽히게 하고, 허브 노드만 블루로 강조.

---

### L-dc-flow-canvas — 흐름 캔버스 / Flow Canvas

- **id**: `L-dc-flow-canvas`
- **name**: 흐름 캔버스 / Flow Canvas
- **composition_family**: `diagram-centric`
- **info_shapes**: `[flow, mapping]`
- **when_to_use**: 절차·파이프라인 1→2→3→…을 캔버스 전체를 가로지르는 하나의 흐름도로 보일 때 — 단계 사이 입력→출력 대응까지 화살표로 명시.
- **when_to_avoid**: 단계가 세로 스텝/타임라인이 더 맞을 때(vertical-flow로), 단계가 8개를 넘어 가로 폭이 부족할 때, 순서 없는 대등 나열일 때.
- **capacity**: 단계 노드 3~6개(라벨 ≤4어, 보조 ≤1줄) + 블루 화살표. 6단계는 가로 1열, 7~8은 뱀형(serpentine) 2열. 분기 ≤1.
- **built_on**: `.s-full`, `.s-eyebrow`, `.timing`(단계 배지), `.card.surface`(스텝), 화살표 커넥터(`→`, 블루), 다이어그램 fragment(`.viz-flow`)
- **content_slots**: `eyebrow`, `steps[3..6]`(라벨+보조), `connectors`(→)
- **sketch**:
```
┌──────────────────────────────────────────────┐
│  ▍EYEBROW                                      │
│                                                │
│  ┌────┐   ┌────┐   ┌────┐   ┌────┐   ┌────┐    │
│  │ 1  │ → │ 2  │ → │ 3  │ → │ 4  │ → │ 5  │    │  flow-h
│  │단계│   │단계│   │단계│   │단계│   │단계│    │  (canvas-wide)
│  └────┘   └────┘   └────┘   └────┘   └────┘    │
│   보조     보조     보조     보조     보조       │
└──────────────────────────────────────────────┘
```
- **coded**: no
- **density_note**: 스텝 라벨 22px, 보조 1줄. 5스텝 가로 1열은 카드폭 ~190px×5+화살표가 1152 안에 수용. 7~8스텝은 뱀형으로 2열, 세로 720 안에서 두 행이 겹치지 않음. 화살표는 블루.
- **source**: https://blog.infodiagram.com/2020/02/key-visual-diagram-structures-processes-in-powerpoint.html (verified — Flow Charts: linear progression(chevron/enumeration), "flow between stages"(cycles), 단계 시각화)
- **adaptation_note**: 원본의 chevron/enumeration 흐름 개념만 차용, PPT 셰브런 대신 `.card.surface` 스텝 + `.timing` 배지 + `--blue` `→` 커넥터로 재표현. 관계 커넥터 규칙(흐름 `→`)을 따르고, 단계 수가 캡을 넘으면 세로 스텝(vertical-flow 패밀리)으로 넘긴다.
