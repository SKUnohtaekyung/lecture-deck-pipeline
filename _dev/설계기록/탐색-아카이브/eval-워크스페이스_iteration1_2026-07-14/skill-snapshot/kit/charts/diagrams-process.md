# diagrams-process — 관계·절차 다이어그램 element 그룹 (재사용 fragment)

> 이 파일의 항목은 whole-slide가 **아니다**. `.s-full`/`.center-msg` 같은 **레이아웃 위에 얹는 재사용 element(fragment)** 다 — 레이아웃 ≠ 다이어그램(카탈로그-규격 §5).
> 각 항목은 `kind:diagram` · `info_shapes[]`(정보모양-taxonomy 12개 안에서만) · `data_shape`(적합 관계 형태) · `element_vs_slide`(fragment 마크업 ↔ 데모 host 분리) 를 반드시 갖는다.
> 색은 문법: **구조·주 강조는 `--blue` · 코랄=주의·경고 · 레드=오류 · 민트=확인·안전·강조 · 비강조 데이터는 periwinkle.** 전부 CSS/SVG로 렌더(이미지 아님), 숫자·틱·라벨은 텍스트.

## fragment 클래스 명명 — 레이아웃 참조와 정합
`families/*.md`가 이미 참조하는 이름과 반드시 일치시킨다.

| slug | fragment 클래스 | 레이아웃이 참조하는 이름 | 얹히는 대표 레이아웃 |
|---|---|---|---|
| radial | `.viz-radial` | `.viz-radial` (diagram-centric.md:81) | `L-dc-radial-hub` |
| network | `.viz-network` | `.viz-network` (diagram-centric.md:141) | `L-dc-network` |
| flow-h | `.viz-flow.viz-flow-h` | `.viz-flow` (diagram-centric.md:171) | `L-dc-flow-canvas` |
| flow-v | `.viz-flow.viz-flow-v` | (세로 스텝 스택) | `L-vf-*` (vertical-flow) |
| cycle | `.viz-cycle` | — | `L-dc-*` / `L-centered-*` |
| funnel | `.viz-funnel` | — | `L-vf-funnel` / `L-centered-*` |

> `flow-h`·`flow-v`는 **공용 베이스 `.viz-flow`**(= `L-dc-flow-canvas`가 참조하는 이름) + 방향 수식자 `.viz-flow-h`/`.viz-flow-v`. 이렇게 하면 `.viz-<slug>` 규칙과 레이아웃 참조명이 동시에 만족된다.

---

### D-radial — 방사 허브 / Radial Hub

- **id**: `D-radial`
- **name**: 방사 허브 / Radial Hub
- **kind**: `diagram`
- **info_shapes**: `[containment, mapping, structure]`
- **data_shape**: 중심 1개 + 그를 둘러싼 대등 위성 4~7개. **위성 사이에 순서·인과가 없는** 방사(허브-스포크) 관계 — 중심이 위성을 아우르거나(포함) 중심↔위성이 대응(매핑)될 때. 위성끼리 서로 연결되면 그건 network(D-network), 위성에 순서가 있으면 flow/cycle. 비교 규칙: 순환 없음·수렴 없음이 radial의 판별 신호.
- **when_to_use**: 하나의 핵심 개념에서 하위 요소가 뻗어 나가는 구조를 한눈에 — 브레인스토밍 웹, 원인-결과 수집, 한 주제의 구성 요소 나열. (소스: 중심 hub에 "topic, question, project, person, or concept"를 놓고 spoke로 관련 항목을 잇는다.)
- **when_to_avoid**: 위성에 순서가 있을 때(→ flow-h/flow-v), 위성이 서로 얽힐 때(→ network), 위성이 8개를 넘어 방사선이 빽빽할 때(→ grid-mosaic 카드 나열), 중심이 없는 대등 나열일 때.
- **capacity**: 중심 노드 1개(라벨 ≤5어) + 위성 4~7개(각 라벨 ≤4어, 보조 ≤1줄). 위성 6개 기준 반지름 ~230px, 원주 60° 등간격 → 가용 1152×548 안에 라벨 겹침 0. 8개 초과는 가독성 붕괴 → 캡.
- **element_vs_slide**: **fragment** = `<div class="viz-radial" role="img" aria-label="…">` 안에 중심 `.card.surface`(절대배치 중앙) + 위성 `.card`들을 원주 좌표로 배치, 각 위성→중심으로 `--blue` 얇은 커넥터. **데모 host** = 이 fragment를 얹는 whole-slide는 `L-dc-radial-hub`(diagram-centric, `.s-full` + `.s-eyebrow` + 하단 캡션)로 **별도** 구성 — fragment 자체에는 헤더·아이브로우를 넣지 않는다.
- **placement**: `[diagram-centric, centered]`
- **built_on**: `.s-full`(host), `.card`·`.card.surface`(중심/위성 노드), `--blue`/`--line` 커넥터 라인. **신규 CSS 요지**: `.viz-radial{position:relative;height:500px}` + 위성 절대배치 좌표(6분할 `top/left`), 커넥터는 얇은 `--blue` 라인(CSS 도형 또는 인라인 SVG `<line>`). 데모의 `.code-diagram`(root→leaves 매핑)을 1-레벨 방사로 응용 가능.
- **a11y**: `role="img"` + `aria-label="방사 허브: 중심 <중심라벨>, 위성 <위성1>·<위성2>·… (N개)"`. 커넥터·노드는 장식이므로 개별 aria 없음, 전체를 하나의 img로.
- **sketch**:
```
            위성A        위성B
               \   ┌──────┐  /
        위성F ──── │ 중심 │ ──── 위성C
               /   │ 개념 │  \
                   └──────┘
            위성E        위성D
```
- **coded**: no
- **source**: https://lucid.co/blog/hub-and-spoke-diagrams (verified — 중심 hub에 "topic, question, project, person, or concept", "Connect each circle to the central hub with lines, or spokes", 용도: 조직구조·원인결과·브레인스토밍)
- **adaptation_note**: 소스는 spoke 개수 상한을 안 줌 → 가독성 하한(22px)·세로예산(548px) 산식으로 **위성 ≤7** 캡을 우리가 규정(no-default 아님, 물리적 상한). 원본의 wheel 클립아트 대신 `.card`+토큰 커넥터로 재표현, 중심만 `--blue` 강조·위성은 `--periwinkle`급 비강조로 위계.

---

### D-network — 관계 네트워크 / Network (Node-Link)

- **id**: `D-network`
- **name**: 관계 네트워크 / Network (Node-Link)
- **kind**: `diagram`
- **info_shapes**: `[structure, mapping]`
- **data_shape**: 개체(노드) 다수 + 개체 사이 **임의의 연결(엣지)**. 단일 중심이 없고 여러 허브가 있을 수 있는 관계망 — "연결 자체"가 값보다 중요할 때. 방향 있으면 유향(화살표), 가중치 있으면 선 굵기. 판별: 순서가 핵심이면 flow, 단일 중심이면 radial, 위계 트리면 structure의 tree.
- **when_to_use**: 여러 개체가 서로 얽힌 관계를 탐색·해석할 때 — 군집 찾기, 허브(고연결 노드) 식별, 간접 경로 추적. (소스: "interpret the structure of a network … clustering of the nodes, how densely nodes are connected".)
- **when_to_avoid**: 순서·타임라인이 핵심일 때(→ flow-h/flow-v/cycle), 정확한 수치 비교가 목적일 때(→ 막대 차트), 노드가 너무 많아 "hairball"이 될 때(정적 슬라이드는 ≤12).
- **capacity**: 노드 6~12개(라벨 ≤3어) + 엣지. 교차선 최소화 배치, 1152×548 안 라벨 겹침 0. 강조(허브) 노드 1~2개만 `--blue`. 12 초과는 hairball → 캡.
- **element_vs_slide**: **fragment** = `<div class="viz-network" role="img" aria-label="…">` 안에 인라인 SVG(`<line>`/`<circle>` 엣지·노드) 또는 절대배치 `.num-circle`/작은 `.card` 노드 + 라인 엣지. **데모 host** = `L-dc-network`(diagram-centric) whole-slide로 별도 — fragment는 노드-링크 그래프만 담고 아이브로우·범례는 host가 얹는다.
- **placement**: `[diagram-centric]`
- **built_on**: `.s-full`(host), `.num-circle`·`.card`(노드), `--line`/`--periwinkle` 비강조 엣지, `--blue` 강조 엣지·화살표. **신규 CSS 요지**: `.viz-network{position:relative;height:500px}` + 인라인 SVG 레이어(`<svg>` 절대배치, `stroke:var(--line)`, 방향은 `marker-end` 화살표 `var(--blue)`). 가중치는 `stroke-width`.
- **a11y**: `role="img"` + `aria-label="관계 네트워크: 노드 N개(<허브라벨> 중심 연결), 엣지 M개; <핵심관계 1줄 요약>"`. 개별 노드에 aria 부여 금지 — 전체 1 img.
- **sketch**:
```
    (A)───(B)        (E)
      \   / \       /   \
       (C)   (D)──(F)   (G)
         \        │      /
          (H)────(I)───(J)
   범례: → 방향 · 굵기=가중치
```
- **coded**: no
- **source**: https://datavizcatalogue.com/methods/network_diagram.html (verified — "Nodes are drawn as little dots or circles … Links are usually displayed as simple lines", 유향/무향 구분, "become hard to read when there are too many nodes and resemble 'hairballs'")
- **adaptation_note**: 소스의 hairball 한계를 **노드 ≤12 캡**으로 구현. 도구 자동 레이아웃 대신 정적 슬라이드용으로 **교차 최소 수동 배치**를 전제하고, 비강조 엣지는 `--line`, 허브·핵심 경로만 `--blue`로 강조해 정적 이미지에서도 관계가 읽히게.

---

### D-flow-h — 가로 절차 흐름 / Horizontal Process Flow

- **id**: `D-flow-h`
- **name**: 가로 절차 흐름 / Horizontal Process Flow
- **kind**: `diagram`
- **info_shapes**: `[flow]`
- **data_shape**: 시작→끝이 분명한 **선형 순서** 3~6단계, 좌→우 진행. 분기 없거나 ≤1. 각 단계는 이전 단계의 출력이 다음 입력으로 이어지는 파이프라인. 판별: 되돌아 반복하면 cycle, 세로가 나으면 flow-v, 단계마다 물량이 줄면 funnel.
- **when_to_use**: 단계별 프로세스·워크플로우·프로젝트 국면을 좌→우 한 줄로 개괄할 때. (소스: 셰브런은 "point from left to right … indicating the flow or progression of steps", 용도 프로세스 엔지니어링·프로젝트 관리·BPI.)
- **when_to_avoid**: 순환·반복이면(→ cycle), 단계가 8개↑라 가로폭 부족이면(→ flow-v 또는 뱀형), 분기 결정이 많으면(→ 결정 플로차트), 물량 수렴이 핵심이면(→ funnel).
- **capacity**: 단계 노드 3~6개(라벨 ≤4어, 보조 ≤1줄) + `→` 커넥터. 5스텝 가로 1열 = 카드폭 ~190px×5 + 화살표가 1152 안에 수용. 7~8은 뱀형(serpentine) 2열. 세로는 카드 1행이면 548 여유.
- **element_vs_slide**: **fragment** = `<div class="viz-flow viz-flow-h" role="img" aria-label="…">` 안에 `.card.surface` 스텝들을 flex row로 + 사이에 `--blue` `→` 커넥터(+선택 `.timing` 배지). **데모 host** = `L-dc-flow-canvas`(diagram-centric, 캔버스 폭) 또는 `top-down` — 아이브로우·제목은 host가 얹고 fragment는 흐름 띠만.
- **placement**: `[diagram-centric, top-down]`
- **built_on**: `.card.surface`(스텝), `.timing`(단계 배지·블루), `--blue` `→` 커넥터(관계 커넥터 규칙: 흐름=`→`). **신규 CSS 요지**: `.viz-flow{display:flex;gap} .viz-flow-h{flex-direction:row;align-items:center}` + `.viz-flow-h .conn::after{content:"→";color:var(--blue)}`. 데모의 `.work-steps`(세로)와 짝을 이루는 가로판.
- **a11y**: `role="img"` + `aria-label="가로 절차 흐름 N단계: <1단계> → <2단계> → … → <N단계>"`. 화살표는 라벨 텍스트로 표현하고 개별 노드 aria 없음.
- **sketch**:
```
  ┌────┐   ┌────┐   ┌────┐   ┌────┐   ┌────┐
  │ 1  │ → │ 2  │ → │ 3  │ → │ 4  │ → │ 5  │
  │단계│   │단계│   │단계│   │단계│   │단계│
  └────┘   └────┘   └────┘   └────┘   └────┘
   보조     보조     보조     보조     보조
```
- **coded**: no
- **source**: https://www.modernanalyst.com/Careers/InterviewQuestions/tabid/128/ID/6540/What-is-a-Chevron-Process-Diagram.aspx (verified — "chevrons … point from left to right … indicating the flow or progression of steps", 각 원소 "a discrete stage or phase", 용도 BPI·프로젝트 관리)
- **adaptation_note**: PPT 셰브런(뾰족 화살 도형) 대신 `.card.surface` 스텝 + 토큰 `→` 커넥터로 재표현(가독성·정렬 안정). 단계 수가 6을 넘으면 뱀형 2열 또는 flow-v로 넘겨 가로폭 붕괴 방지. 강조는 현재 단계 1곳만 `--blue`.

---

### D-flow-v — 세로 절차 흐름 / Vertical Process Flow

- **id**: `D-flow-v`
- **name**: 세로 절차 흐름 / Vertical Process Flow
- **kind**: `diagram`
- **info_shapes**: `[flow]`
- **data_shape**: 위→아래로 흐르는 **선형 순서** 3~6단계(각 단계에 설명 문장이 붙어 flow-h보다 텍스트가 길 때 유리). 캐스케이드형 절차·하향 위계·타임라인. 판별: 순서 반복이면 cycle, 짧은 라벨만이면 flow-h가 가로로 더 압축적, 물량 수렴이면 funnel.
- **when_to_use**: 절차·how-to·전략 국면을 각 단계 설명과 함께 세로로 쌓아 보일 때, 문서형 판독·하향 체인. (소스: "streamlined flow from top to bottom", 레시피·how-to·과학 절차·조직 지휘체계에 적합.)
- **when_to_avoid**: 순환·반복이면(→ cycle), 라벨이 짧아 가로가 공간 효율적이면(→ flow-h), 물량이 단계마다 줄면(→ funnel), 순서 없는 대등 나열이면(→ grid-mosaic).
- **capacity**: 단계 3~6개, 각 행 ≈ 헤드라인(~28px)+본문 1~2줄(39~78px)+패딩(~28px) ≈ 95~134px → 548px 세로예산에 **4~5행**이 현실적(본문 2줄이면 4행, 1줄이면 5~6행). 단계 사이 `↓` 커넥터. 6 초과는 스크롤 위험 → 캡.
- **element_vs_slide**: **fragment** = `<div class="viz-flow viz-flow-v" role="img" aria-label="…">` 안에 `.card`/`.work-step` 스텝을 세로 스택 + 사이 `--blue` `↓`, 각 스텝에 `.num-circle` 번호. **데모 host** = `vertical-flow` 패밀리 레이아웃(`L-vf-*`)로 별도 — 데모덱의 `.work-steps` 마크업이 이 fragment의 검증된 원형.
- **placement**: `[vertical-flow, top-down]`
- **built_on**: `.work-step`/`.card`(스텝), `.num-circle`(번호·민트), `--blue` `↓` 커넥터(관계 커넥터: 검증/아래=`↓`). **신규 CSS 요지**: `.viz-flow-v{flex-direction:column;gap}` + 스텝 사이 `↓`. 데모 `.work-steps`(제작규칙.html:214) 재사용 — 이미 브라우저 검증됨.
- **a11y**: `role="img"` + `aria-label="세로 절차 흐름 N단계: 1 <라벨> → 2 <라벨> → … → N <라벨>"`.
- **sketch**:
```
  ① 단계 라벨 ─ 보조 설명
        ↓
  ② 단계 라벨 ─ 보조 설명
        ↓
  ③ 단계 라벨 ─ 보조 설명
        ↓
  ④ 단계 라벨 ─ 보조 설명
```
- **coded**: no
- **source**: https://edrawmax.wondershare.com/flowchart/vertical-flowchart.html (verified — "streamlined flow from top to bottom", 용도 레시피·how-to·과학 절차·지휘체계, "understand the whole process just by going through the vertical flow diagram")
- **adaptation_note**: 소스의 top-to-bottom 절차 개념을 데모덱 `.work-steps`(민트 번호 원 + 스텝)로 재표현 — 이미 검증된 CSS라 신규 위험 0. 세로예산 산식으로 **≤6 스텝**(본문 길면 ≤4) 캡. flow-h와 짝: 라벨이 길면 v, 짧으면 h.

---

### D-cycle — 순환 루프 / Cycle

- **id**: `D-cycle`
- **name**: 순환 루프 / Cycle
- **kind**: `diagram`
- **info_shapes**: `[flow]`
- **data_shape**: **끝이 처음으로 되돌아가는** 반복 절차 3~7단계(이상적 4~6). 세 조건 충족 시: 뚜렷한 단계 + 고정 순서 + **반복**. 마지막 출력이 첫 입력으로 피드백. 판별: 시작·끝이 분명하고 한 번에 끝나면 flow-h/flow-v, 분기 결정이 있으면 결정 플로차트(cycle은 단일 경로 가정).
- **when_to_use**: 지속 반복되는 프로세스 — PDCA·지속개선·수명주기·자연 순환처럼 "끝이 곧 시작"임을 즉시 드러낼 때. (소스: "the end of a process flow extends to the beginning … a repeating cycle with no beginning and end".)
- **when_to_avoid**: 한 번 실행하고 멈추는 선형 절차면(→ flow-h/flow-v), 분기 결정이 있으면(→ 플로차트), 단계가 8개↑라 원호 조각이 너무 좁아 라벨이 안 들어갈 때.
- **capacity**: 단계 3~7개(라벨 ≤4어), 원주 등간격. 6단계 = 60° 간격·반지름 ~220px가 1152×548 안에 수용, 각 단계 사이 곡선 `↻` 화살표. **8단계 초과 금지**(조각이 너무 좁아짐 — 소스 근거).
- **element_vs_slide**: **fragment** = `<div class="viz-cycle" role="img" aria-label="…">` 안에 단계 `.card`를 원주 절대배치 + 순환 방향 `--blue` 곡선 화살표(인라인 SVG `path` arc + `marker-end`). **데모 host** = `L-dc-*`(diagram-centric) 또는 `centered` whole-slide로 별도 — fragment는 링만.
- **placement**: `[diagram-centric, centered]`
- **built_on**: `.card`/`.card.surface`(단계 노드), `--blue` 곡선 화살표. **신규 CSS 요지**: `.viz-cycle{position:relative;height:500px}` + 단계 절대배치(원주 좌표) + 인라인 SVG `<path>` 호(arc)에 `marker-end` 화살표 `var(--blue)`. 중앙에 선택적 `.pill` 루프명.
- **a11y**: `role="img"` + `aria-label="순환 루프 N단계(반복): <1> → <2> → … → <N> → 다시 <1>"`. "다시 처음으로"를 라벨에 명시해 순환성 전달.
- **sketch**:
```
            ┌───────↻ 단계1 ───────┐
        단계5                      단계2
          │        (루프명)          │
        단계4                      단계3
            └───────────────────────┘
              (마지막 → 다시 처음)
```
- **coded**: no
- **source**: https://venngage.com/blog/cycle-diagram/ (verified — "visualizing repetitive steps … the end of a process flow extends to the beginning, which makes it a repeating cycle with no beginning and end"; 예시 PDCA 4단계~SDLC 7단계)
- **adaptation_note**: 소스는 상한 미명시 → 별도 검색 근거("avoid for processes with more than 8 stages — each segment becomes too narrow to label")로 **≤7 캡**. PPT 원형 클립아트 대신 `.card` 노드 + 토큰 곡선 화살표. 순환 방향은 `--blue` 하나로만, 노드는 비강조 유지. flow와 구분: 되돌아오는 화살표 유무가 판별 신호.

---

### D-funnel — 수렴 퍼널 / Funnel

- **id**: `D-funnel`
- **name**: 수렴 퍼널 / Funnel
- **kind**: `diagram`
- **info_shapes**: `[flow, numeric]`
- **data_shape**: **단계마다 물량이 줄어드는** 선형 절차 3~6단계 — 위 넓고 아래 좁음, 폭(또는 수치)이 각 단계 잔존량. 사용자가 순차로만 통과(중간 진입·역행·스킵 없음)할 때. 단계 값은 단조 감소가 이상적. 판별: 진입/스킵/역행이 있으면 퍼널이 오해 유발(→ Sankey), 물량 불변이면 그냥 flow-h/flow-v, 부분-전체 비율이면 pie/donut(≤6조각·합≈100).
- **when_to_use**: 전환·드롭오프를 보일 때 — 방문→상세→장바구니→결제→구매, 채용 지원→오퍼, SaaS 온보딩. 어느 단계에서 얼마나 이탈하는지 병목을 폭의 급격한 좁아짐으로 짚을 때. (소스: 폭이 "the number of users at each stage", "narrow, indicating a reduction … in a linear flow".)
- **when_to_avoid**: 사용자가 단계를 건너뛰거나 역행·중간 진입할 때(→ Sankey), 단계가 10개↑거나 단계 간 감소가 미미해 폭 차이가 안 보일 때(→ 표/워터폴), 3단계 미만이면 굳이 퍼널 아님.
- **capacity**: 단계 3~6개(라벨 ≤4어 + 수치·%). 각 밴드 높이 ~70~90px → 548 세로예산에 **5~6밴드** 수용. 폭은 단계값 비례(단조 감소). 값·%는 텍스트로 밴드 안/옆. 10 초과는 폭 차이 소멸 → 캡.
- **element_vs_slide**: **fragment** = `<div class="viz-funnel" role="img" aria-label="…">` 안에 단계 밴드(`div`)를 세로 스택, 각 밴드 `width`를 단계값에 비례(`clip-path`로 사다리꼴 가능) + 숫자·% 텍스트. **데모 host** = `L-vf-funnel`(vertical-flow) 또는 `centered` whole-slide로 별도 — fragment는 수렴 밴드만.
- **placement**: `[vertical-flow, centered, diagram-centric]`
- **built_on**: 밴드 `div`(폭 비례) + `--periwinkle`(비강조 단계)·`--blue`(강조/최종 전환 1곳)·`--coral-deep`(급락·병목 주의)·`--red`(심각 미달·오류 단계). 수치는 `.cc-val`급 텍스트. **신규 CSS 요지**: `.viz-funnel{display:flex;flex-direction:column;align-items:center} .viz-funnel .band{width:var(--w);…}` + 선택 `clip-path:polygon()`로 사다리꼴. 데모 `.code-chart`(막대) 색·수치 텍스트 규칙 재사용.
- **a11y**: `role="img"` + `aria-label="수렴 퍼널 N단계: <1단계> <값1>, <2단계> <값2>, … <N단계> <값N>(전환율 …%)"`. 각 단계 값을 라벨에 순서대로 담아 폭 정보를 텍스트로 대체.
- **sketch**:
```
  ┌───────────────────────────┐  방문 10,000
   └─────────────────────────┘   상세  6,200
     └─────────────────────┘     장바구니 2,800
       └─────────────────┘       결제  1,400   ◀ 급락(코랄=주의)
         └─────────────┘         구매    900
```
- **coded**: no
- **source**: https://www.explo.co/blog/understanding-funnel-charts-what-is-a-funnel-chart (verified — "width of the segments … indicates the number of users at each stage", "segments usually narrow, indicating a reduction", "progressive nature … in a linear flow", "at least three stages"; 용도 sales·web analytics·recruitment)
- **adaptation_note**: 소스의 폭=잔존량·선형 수렴 개념을 CSS 밴드 폭 비례로 재표현(이미지 아님, 값은 텍스트). "사용자가 스킵/역행하면 오해"라는 소스 경고를 `when_to_avoid`에 반영(→ Sankey). 급락·병목 단계는 `--coral-deep`로 주의, 심각 미달·오류만 `--red`, 나머지는 `--periwinkle`, 핵심 전환은 `--blue`로 구조를 드러낸다.
