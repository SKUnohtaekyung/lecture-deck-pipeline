# 관계·구조 다이어그램 카탈로그 (Relational / Structural Diagrams)

> **이 파일의 대상**: 위계·포함·매핑을 그리는 **재사용 element(fragment)** 5종 — concentric · venn · tree · pyramid · matrix.
> 이들은 whole-slide가 **아니다**. `.viz-<slug>` fragment로 독립 선언하고, 레이아웃(`../layouts/families/*.md`)을 카탈로그에서 따로 골라 그 안에 **얹는다**. — "레이아웃 ≠ 다이어그램"(카탈로그-규격 §5).
> 판단 축은 [`정보모양-taxonomy.md`](../guide/정보모양-taxonomy.md)의 12 정준 모양. `info_shapes[]` 값은 전부 그 안에서만 쓴다.
> **code-viz 원칙**: 전부 CSS/SVG로 렌더(이미지 아님). 숫자·라벨은 텍스트, 색은 [토큰-치트시트](../guide/토큰-치트시트.md) 문법(구조·주 강조=`--blue` · 코랄=주의·경고 · 레드=오류 · 민트=안전·강조 · 비강조=periwinkle/surface).
> **no-default(의미 기준)**: 아래 어떤 element도 "기본/가장 흔한 차트"로 규정하지 않는다. 5종은 데이터 모양이 다를 때 각각 맞는 동급 도구다.

세로 예산 검산 기준: `.s-full` 콘텐츠 영역 세로 ≈ **548px**(top 118 하단여백 제외), 가용 폭 **1152px**(1280−64−64). 도해는 이 rect 안에 스크롤·오버플로 0으로 들어가야 한다.

---

### D-concentric — 동심 포함도 / Concentric Containment

- **kind**: diagram
- **info_shapes**: `[containment, structure]`
- **data_shape**: **완전 포함**(subset) 위계 — 한 집합이 다른 집합 안에 전부 들어감("A ⊂ B ⊂ C"). 겹침이 아니라 중첩. 링 2~4겹, 각 링은 바깥을 감싸는 상위 범주.
- **when_to_use**: 중심 개념이 더 넓은 범주에 **완전히 속하는** 포함 위계를 보일 때(예: 오늘의 주제 → 상위 분야 → 전체 생태계). 초점 링 하나를 강조해 "여기가 지금 다룰 곳"을 못박을 때.
- **when_to_avoid**: 두 집합이 **부분만** 겹칠 때(→ D-venn), 순서·절차일 때(→ flow element), 대응·연결 매핑일 때(→ D-matrix/네트워크). 링이 **5겹을 넘으면** 안쪽 텍스트가 뭉개져 판독 붕괴 → 부적합.
- **capacity**: 링 **2~4겹**(가독성 하한: 최외곽 지름 ~480px, 각 링 두께 ≥56px여야 라벨 19px가 앉음). 링당 라벨 ≤4어. 강조 링 1개(블루). 5겹↑ 금지.
- **element_vs_slide**: **fragment** = `.viz-concentric`(중첩 원 SVG/`border-radius:50%` div 스택 + 링 라벨). whole-slide 아님. **데모 host(별도 슬라이드)** = `L-ct-concentric`(centered: `.center-msg` 중앙에 얹고 `.cm-title` 축소) 또는 `L-dc-hero`(diagram-centric: 무대 전체). fragment는 host의 `concentric_diagram` 슬롯에 삽입.
- **placement[]**: `[centered, diagram-centric]`
- **built_on**: deck.css 토큰 `--blue`(강조 링) · `--surface`/`--periwinkle`(비강조 링) · `--line`(테두리) · `--ink`(라벨). **신규 CSS 요지**: `.viz-concentric{position:relative;width:480px;height:480px;margin:0 auto}` + `.vc-ring{position:absolute;border-radius:50%;left:50%;top:50%;transform:translate(-50%,-50%);display:grid;place-items:start center}` 겹 크기를 인라인 `width/height`로 축소 스택(480→360→240→120), 라벨은 각 링 상단 안쪽. 강조 링만 `background:var(--blue);color:var(--white)`.
- **a11y**: `role="img"` + `aria-label="동심 포함도: 바깥 <최상위>가 <중간>을, 그 안에 <중심>을 포함"` (링 순서를 바깥→안으로 서술, 빈 라벨 금지).
- **sketch**:
```
        ┌───────────────────────┐
        │  전체 생태계 (surface)  │
        │   ┌─────────────────┐  │
        │   │ 상위 분야(peri) │  │
        │   │   ╔═════════╗   │  │
        │   │   ║ 오늘 ★  ║   │  │  ← 중심 = blue 강조
        │   │   ╚═════════╝   │  │
        │   └─────────────────┘  │
        └───────────────────────┘
```
- **coded**: no
- **source**: https://lucid.co/diagram/venn-diagram/euler-diagram-vs-venn-diagram (verified — "related subsets [can be] nested within other sets", 오일러형 완전 포함은 부분 겹침 벤과 구분)
- **adaptation_note**: 템플릿 그라디언트·3D 링 복제 금지. 오일러 다이어그램의 **완전 중첩** 개념만 차용해 deck.css 토큰으로 재표현 — 강조 링 1곳만 `--blue`, 나머지는 `--surface`/`--periwinkle`로 위계를 만들되 색은 문법대로. 링 라벨은 도해 내부 텍스트(이미지 아님).

---

### D-venn — 부분 겹침 벤도 / Partial-Overlap Venn

- **kind**: diagram
- **info_shapes**: `[containment, comparison]`
- **data_shape**: **두(예외적으로 셋) 집합의 부분 겹침** — 각 집합 고유 영역 + 공유 교집합("A와 B가 X를 공유"). 완전 포함 아님, 완전 분리 아님. 교집합에 의미가 실릴 때.
- **when_to_use**: 두 개념이 일부 특성을 **공유**하되 각자 고유 영역도 있음을 보일 때(교집합 = 핵심 메시지). "둘 다에 해당하는 것"을 가운데로 강조.
- **when_to_avoid**: 한쪽이 다른 쪽에 **완전히 포함**될 때(→ D-concentric), 겹침이 없는 대등 나열일 때(→ grid), 집합이 **4개↑**여서 교집합 영역이 조밀·판독 불가일 때. 교집합에 담을 게 없으면(빈 교집합) 벤이 아니라 분리 카드로.
- **capacity**: 집합 **2개 권장**(최대 3). 원 지름 ~300px, 겹침 폭 ~90px. 영역당 라벨 ≤4어, 교집합 라벨 ≤3어. 3원은 교집합 7영역이 되어 각 라벨 ≤2어로만. 4원↑ 금지.
- **element_vs_slide**: **fragment** = `.viz-venn`(반투명 원 2개 SVG 또는 `mix-blend`/`opacity` div + 좌/우/가운데 라벨). whole-slide 아님(옛 `.venn-slide` 안티패턴 대체). **데모 host(별도 슬라이드)** = `L-dc-hero`/`L-ct-figure`(중앙·무대) 또는 `L-sp-visual-lead`(split 우측 시각, 희소). fragment는 host의 diagram/figure 슬롯에 삽입.
- **placement[]**: `[centered, diagram-centric, split]`
- **built_on**: deck.css 토큰 `--blue`(교집합 강조) · `--periwinkle`/`--ice`(두 원, 반투명) · `--ink`(라벨) · `--surface`(배경). **신규 CSS 요지**: `.viz-venn{position:relative;width:520px;height:320px}` + `.vv-set{position:absolute;width:300px;height:300px;border-radius:50%;opacity:.55}` 좌 `left:0`·우 `right:0`, 겹치게 배치. 교집합 라벨은 절대배치 중앙 `.vv-x{color:var(--blue);font-weight:800}`. SVG `<circle>` + `mix-blend-mode:multiply`도 가능.
- **a11y**: `role="img"` + `aria-label="벤 다이어그램: <A>와 <B>, 공유 영역은 <교집합>"` (좌·우·교집합 3영역 서술).
- **sketch**:
```
   ┌──────────────────────────────────┐
   │   ╭─────────╮   ╭─────────╮       │
   │   │   A     │★★★│    B     │       │
   │   │  고유   │공유│   고유   │       │  ★ = 교집합(blue)
   │   ╰─────────╯   ╰─────────╯       │
   │   기획만    둘 다   개발만          │
   └──────────────────────────────────┘
```
- **coded**: no
- **source**: https://creately.com/blog/diagrams/venn-diagrams-vs-euler-diagrams/ (verified — 벤은 "simple set relationships", "difficult to read when representing relationships more than three sets", 부분 겹침·교집합 강조가 오일러 완전포함과 구분)
- **adaptation_note**: 형광 채움·클립아트 복제 금지. 두 원은 `--periwinkle`/`--ice` 반투명으로 비강조, **교집합 라벨만** `--blue`로 메시지를 실어 색 문법을 지킨다. 완전 포함이면 이 element를 쓰지 말고 D-concentric으로 넘긴다(리서치 규칙: venn=부분 겹침, concentric=완전 포함).

---

### D-tree — 위계 트리 / Hierarchy Tree

- **kind**: diagram
- **info_shapes**: `[structure, containment]`
- **data_shape**: **부모→자식 위계**(1:다 분기) — 루트 하나에서 갈라지는 조직도·분류 트리·부분-전체 분해. 계층 2~3단, 노드는 상위가 하위를 거느림.
- **when_to_use**: 요소들이 **위→아래 보고·소속·분해** 관계로 갈라질 때(조직도, 카테고리 분류, "이 큰 것은 이 부분들로 나뉜다"). 분기 구조 자체가 논지일 때.
- **when_to_avoid**: 위계 없는 대등 나열(→ grid), 순서·절차(→ flow), 부분 겹침(→ venn). 노드가 **~12개를 넘거나 4단↑**이면 한 슬라이드에서 선이 교차·라벨 축소로 판독 붕괴 → 서브트리를 별 슬라이드로 분리.
- **capacity**: 계층 **≤3단** · 노드 총 **≤12개**(리프 라벨 ≤4어, 노드 박스 높이 ~56px). 1단 루트 1 + 2단 3~5 + 3단 리프 ≤8. 세로 3단 × (박스56+커넥터40) ≈ 288px로 548 예산 내. 4단↑·13노드↑ 금지.
- **element_vs_slide**: **fragment** = `.viz-tree`(루트 박스 + 블루 커넥터 라인 + 자식 박스 행, 데모_제작규칙.html의 `.code-diagram`/`.cd-root`/`.cd-leaves` 구조 재사용). whole-slide 아님. **데모 host(별도 슬라이드)** = `L-dc-hero`(무대 전체) · `L-dc-annotated`(노드에 번호 주석) · `L-td-*`(top-down: 상단 타이틀 밴드 + 하단 트리). fragment는 host의 `diagram` 슬롯에 삽입.
- **placement[]**: `[diagram-centric, top-down]`
- **built_on**: deck.css 토큰 `--blue`(루트/강조 노드·커넥터) · `--surface`/`--line`(자식 박스) · `--ink`/`--gray-700`(라벨). **재사용 CSS**: `.code-diagram`·`.cd-root`·`.cd-arrow`·`.cd-leaves`(grid 4열)·`.cd-leaf`(이미 브라우저 검증됨). **신규 요지**: 3단이면 `.viz-tree`로 감싸 중간단 `.vt-branch` 행 추가 + 부모-자식을 잇는 `::before` 세로선(`--line`, 강조 경로만 `--blue`).
- **a11y**: `role="img"` + `aria-label="위계 트리: <루트> 아래 <자식1>, <자식2>… , <자식n>"` (루트→각 분기를 순서대로 서술).
- **sketch**:
```
             ┌───────────┐
             │  루트 개념 │            ← blue
             └─────┬─────┘
        ┌──────────┼──────────┐
     ┌──┴──┐   ┌──┴──┐   ┌──┴──┐
     │ 갈래A│   │ 갈래B│   │ 갈래C│     ← surface
     └──┬──┘   └─────┘   └─────┘
    ┌───┴───┐
   리프  리프                          (≤3단·≤12노드)
```
- **coded**: no (단, `.code-diagram` 2단 매핑은 데모에서 검증됨 — 3단 확장분만 신규)
- **source**: https://www.drawio.com/blog/org-charts (verified — "The most important node is almost always placed at the top of the tree", 복잡 분기는 별 페이지 분리 권고 = 노드/단 상한 근거)
- **adaptation_note**: SmartArt·아이콘 조직도 복제 금지. 데모에서 이미 검증된 `.code-diagram` 도형 매핑을 3단 위계로 확장하고, 루트/강조 경로만 `--blue`·나머지 노드는 `--surface`로 위계를 색이 아닌 위치+비강조로 표현. 노드가 캡을 넘으면 서브트리를 별 슬라이드로 나눠 가독성 하한을 지킨다.

---

### D-pyramid — 층위 피라미드 / Level Pyramid

- **kind**: diagram
- **info_shapes**: `[structure, containment]`
- **data_shape**: **정적 층위 위계** — 아래(넓음=많음/기반) → 위(좁음=적음/정점)로 쌓인 3~5층. 각 층이 상위를 떠받치는 토대 관계 또는 비중 위계(예: 매슬로우, 역할 티어). **흐름·전환 아님**.
- **when_to_use**: 층이 **떠받침/포함/비중**의 정적 위계를 이룰 때 — "아래가 기반, 위로 갈수록 좁아짐". 토대→정점 서사, 층별 점증 설명.
- **when_to_avoid**: 단계 사이 **전환·감소(전환율·이탈)**를 보일 때 → 그건 **funnel**(flow element)이지 pyramid 아님(리서치: pyramid=정적 위계, funnel=순차 프로세스). 층이 **6층↑**이면 상단 층 높이가 라벨 하한 미달로 붕괴. 대등 나열도 부적합.
- **capacity**: 층 **3~5층**(각 층 높이 ≥84px여야 22px 라벨+비중이 앉음, 5층×~100px≈500px로 548 내). 층당 라벨 ≤5어 + 보조 ≤1줄. 강조 층 1개(블루). 6층↑ 금지.
- **element_vs_slide**: **fragment** = `.viz-pyramid`(사다리꼴 층 스택 — `clip-path:polygon` 삼각 또는 폭 점감 div 3~5개 + 층 라벨). whole-slide 아님. **데모 host(별도 슬라이드)** = `L-ct-pyramid`(centered: `.center-msg` 중앙 + 우측 `.callout` 주석) 또는 `L-dc-hero`. fragment는 host의 `pyramid_diagram` 슬롯에 삽입.
- **placement[]**: `[centered, diagram-centric]`
- **built_on**: deck.css 토큰 `--blue`(강조 층) · `--surface`/`--periwinkle`(층 계조, 비강조) · `--ink`(비강조 층 라벨)/`--white`(강조 층 라벨) · `--line`. **신규 CSS 요지**: `.viz-pyramid{display:flex;flex-direction:column;align-items:center;gap:6px}` + `.vp-level{height:88px;display:grid;place-items:center;color:var(--ink);font-weight:800}`(비강조 층은 `--periwinkle`/`--surface`로 밝으므로 라벨은 짙은 `--ink`) 각 층 `width`를 인라인으로 점증(정점 240px → 기반 640px), 강조 층만 `.vp-level.is-key{background:var(--blue);color:var(--white)}`, 나머지 `--periwinkle`/`--surface`. 삼각 외곽은 `clip-path`.
- **a11y**: `role="img"` + `aria-label="층위 피라미드: 기반 <최하층>부터 정점 <최상층>까지 <n>층"` (아래→위 순서로 층 서술).
- **sketch**:
```
              ╱───╲
             ╱ 정점 ╲            ← 좁음(적음)
            ╱───────╲
           ╱  중간층  ╲   ★ 강조 = blue
          ╱───────────╲
         ╱   토대·기반   ╲       ← 넓음(많음/기반)
        ╱───────────────╲
              (3~5층)
```
- **coded**: no
- **source**: https://www.spotfire.com/learn-connect/glossary/what-is-a-pyramid-chart (verified — "show a hierarchical structure", "need to remain very simple… extra layers… quickly make it cluttered", 프로세스 흐름은 funnel로 = pyramid와 구분)
- **adaptation_note**: 3D·그림자 피라미드 템플릿 복제 금지. 층 계조는 `--periwinkle`→`--surface` 토큰으로 옅게, **강조 층 1곳만** `--blue`. 층 사이에 전환/감소 서사가 있으면 이 element를 쓰지 말고 funnel(flow) element로 넘긴다. 층 라벨·비중은 도해 내부 텍스트(이미지 아님).

---

### D-matrix — 2축 사분면 매트릭스 / 2-Axis Quadrant Matrix

- **kind**: diagram
- **info_shapes**: `[mapping, structure]`
- **data_shape**: **두 직교 축**(예: 중요도×노력, 영향×긴급)으로 항목을 4분면에 **위치=판단**으로 매핑. 각 항목이 (x,y) 좌표를 갖고 사분면 소속이 곧 처방. 연속 추세 아님.
- **when_to_use**: 항목을 **두 기준으로 동시에** 평가해 포지셔닝/우선순위를 보일 때 — "위치가 곧 결정"(예: 지금할 것/버릴 것). 사분면별 처방이 다를 때.
- **when_to_avoid**: 축이 **하나거나 연속량 추세**일 때(→ numeric 차트: bar/line), 항목이 **~12개↑**로 점이 뭉칠 때, 4분면 의미 차이가 없을 때(→ grid). 정밀 수치 비교엔 부적합(위치는 상대적).
- **capacity**: 항목 **6~12개**(사분면당 ≤4, 점 라벨 ≤3어). 매트릭스 정사각 ~520×520px가 top 160~680에 들어가 십자축 양끝 라벨까지 548+ 예산 내. 축 라벨 각 2개(양끝 ≤3어) + 사분면 이름 ≤4어. 13항목↑ 금지.
- **element_vs_slide**: **fragment** = `.viz-matrix`(블루 십자축 + 4분면 배경 + 플롯된 `.pill` 항목). whole-slide 아님. **데모 host(별도 슬라이드)** = `L-dc-quadrant`(diagram-centric: 축+플롯 무대) 또는 `L-td-matrix`(top-down: 상단 타이틀 밴드 + 하단 2×2 칸). fragment는 host의 matrix/quadrant 슬롯에 삽입.
- **placement[]**: `[diagram-centric, top-down]`
- **built_on**: deck.css 토큰 `--blue`(십자축·추천 사분면 pill) · `--surface`/`--blue-soft`(사분면 배경 계조) · `--periwinkle`(비강조 pill) · `--ink`(축 라벨). 프리미티브 `.pill`(플롯 항목) 재사용. **신규 CSS 요지**: `.viz-matrix{position:relative;width:520px;height:520px;margin:0 auto}` + 십자축 `::before/::after`(2px `--blue` 라인, 50%), 4분면 배경 `.vm-q{position:absolute;width:50%;height:50%}`, 항목은 절대배치 `.pill` 좌표.
- **a11y**: `role="img"` + `aria-label="2축 매트릭스: 가로 <x축>, 세로 <y축>. <사분면>에 <항목들>"` (축 2개 + 강조 사분면 서술).
- **sketch**:
```
                 ↑ 중요도(고)
        ┌────────────┬────────────┐
        │  재검토     │  ★지금 할 것 │  ★ = blue 강조
        │  ● 항목     │  ● ●        │
   노력저├────────────┼────────────┤노력고
        │  버릴 것    │  나중        │
        │  ● 항목     │  ● 항목      │
        └────────────┴────────────┘
                 ↓ 중요도(저)
```
- **coded**: no
- **source**: https://www.productplan.com/glossary/2x2-prioritization-matrix (verified — "importance" 세로축·"effort" 가로축, 4사분면 "High value, low effort" 등, 항목을 위치로 우선순위화)
- **adaptation_note**: 중앙 원형 타이틀·클립아트 템플릿 복제 금지. 좌표계만 차용해 `--blue` 십자축 + `.pill` 플롯으로 재표현, 사분면 배경은 `--surface`/`--blue-soft`로 옅게 구분하고 **추천 사분면 pill만** `--blue`로 "위치=판단"을 강조. 정밀 수치가 핵심이면 numeric 차트로 넘긴다.

---

## 그룹 커버리지 메모

- **containment**: D-concentric(완전 포함) · D-venn(부분 겹침) · D-tree/D-pyramid(부분-전체 위계) — 겹침 형태로 분기.
- **structure**: D-tree(분기 위계) · D-pyramid(층위) · D-matrix(2축 포지셔닝).
- **mapping**: D-matrix(항목↔좌표).
- 5종 모두 `.viz-<slug>` fragment(레이아웃 아님) · `role="img"`+aria-label · CSS/SVG 렌더 · 구조·주 강조에는 `--blue` 토큰 사용.
- 적합성 분기 요지: **완전 포함 → concentric**, **부분 겹침 → venn**, **분기 위계 → tree**, **정적 층위(전환이면 funnel) → pyramid**, **2축 위치 매핑(1축·연속이면 numeric) → matrix**.
