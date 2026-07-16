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


---

### D-gantt — 비례 시간축·간트 / Proportional Timeline (Gantt)

- **id**: `D-gantt`
- **name**: 비례 시간축·간트 / Proportional Timeline (Gantt)
- **kind**: `diagram`
- **info_shapes**: `[flow, numeric]` — 주 모양은 **일정 흐름**(무엇이 언제·얼마나·병렬로 진행되나), 종속 모양은 **numeric**(막대 좌표·길이가 실제 시점·기간에 비례). **D-funnel과 일관 처리**: funnel이 "단계별 물량 감소"라는 비례 성분 때문에 `[flow, numeric]`을 다는 것과 같은 근거로, gantt도 막대가 실제 기간에 비례하므로 numeric을 병기한다. 단 **양 비교가 목적이 아니라** 기간·병렬 관계 전달이 목적이라 by-shape.md에는 **flow 절에만 등재**(funnel과 동형: numeric 절엔 괄호 각주로만). 정확한 양 비교가 목적이면 → `C-column`/`C-hbar`, 부분-전체 비율이면 → `C-pie`.
- **data_shape**: **공통 연속 시간축**(픽셀 위치 ∝ 실제 날짜/시점) 위에 놓인 (a) **기간 막대**(작업마다 시작~종료, 길이=소요) + (b) **마일스톤 점**(기간 0의 시점 사건). 여러 막대가 **세로로 겹쳐 병렬 진행**을 표현. 실제 시점 간격이 화면 간격에 그대로 비례하는 게 핵심 신호 — 3월과 4월 사이 폭 = 4월과 5월 사이 폭. **판별(중요): 축 없이 사건을 등간격으로 나열하고 기간이 없으면 그건 점-사건 타임라인 레이아웃(`L-vf-spine-timeline`)이지 간트가 아니다.** 되돌아 반복하면 cycle, 단계마다 물량이 줄면 funnel, 시점·기간 없이 순서만이면 flow-h/flow-v.
- **when_to_use**: 여러 작업의 **시작·종료·소요·겹침**을 하나의 비례 시간축에서 한눈에 — 프로젝트 일정, 강의 로드맵, 출시 계획, 병렬 워크스트림의 타이밍 관계. "설계와 개발이 언제부터 겹치나", "테스트가 며칠이나 걸리나"처럼 **기간과 병렬성**이 메시지일 때. (소스 재표현: 행=활동, 열=시간축이고 각 활동의 소요가 막대 길이로, 착수=막대 시작·완료=막대 끝으로 그려지며, 병렬로 도는 활동이 세로 겹침으로 드러난다.)
- **when_to_avoid**: 시점만 있고 기간·병렬이 없는 점-사건 나열이면(→ 레이아웃 `L-vf-spine-timeline` 또는 `D-flow-v`), 순서만 있고 실제 시점이 없으면(→ `D-flow-h`/`D-flow-v`), 반복 순환이면(→ `D-cycle`), 작업이 7행을 넘어 막대 행이 세로예산을 초과하면(→ 표로 축약하거나 분할), 시간 간격이 균일해 비례축의 이점이 없고 각 마디에 문장 설명이 길면(→ `L-vf-spine-timeline`), 정확한 양 비교가 목적이면(→ `C-column`/`C-hbar`).
- **capacity**: 작업(막대) 행 **5~6개 여유·7개 상한**. 세로 산식(형제 element와 정합): fragment `.viz-gantt` 높이는 세로예산 548px에서 **host 크롬(`.s-eyebrow` ~40px + 하단 캡션 ~40px = ~80px)을 뺀 ~468px**로 캡(형제 D-radial/D-cycle/D-network가 fragment를 ~500px로 캡하되 gantt는 host가 아이브로우·캡션을 fragment 주위에 얹으므로 그만큼 더 조인다). 그 ~468px에서 축 헤더(눈금 라벨) ~40px를 빼면 막대 플롯 ~428px → 행높이 ~56px(라벨 ≥17px 한 줄 + 막대 두께 ~20px + gap/패딩 ~16px)로 **7행이 물리 상한**(428/56≈7.6, 8행은 gap 붕괴·라벨 겹침). 선택 범례를 넣으면 ~28px를 더 먹어 6행이 상한. 마일스톤 점 ≤6(라벨 겹침 방지). 축 눈금 4~8개(작업 라벨 컬럼 ~220px를 뺀 플롯 ~900px에 등간격, 눈금당 ≥110px라 라벨 ≥17px 한 줄 수용). 작업 라벨 컬럼 폭 ~200~240px(라벨 ≤8자 전각). 막대가 너무 짧아 라벨이 안 들어가는 순간 사건은 마일스톤 점으로 대체.
- **content_slots[]**: `axis_scale`(공통 비례 시간축 — t0~t1, 눈금 4~8개) · `task_bars[]`(각 항목: `label`·`start`·`end`·`emphasis`(강조=blue / 비강조=periwinkle / 지연·리스크=coral)) · `milestones[]`(각: `label`·`date`, `◆` 점 ≤6) · `now_marker`(현재 시점 세로 파선 — 중립 구조 마커) · `caption`(fragment **외부**, host `L-dc-*`가 하단에 얹음). *(§5는 element = 레이아웃 스키마 §4 + 추가필드라 `content_slots[]`를 요구하므로 명시. 형제 diagrams-process 항목들이 `data_shape`로 슬롯을 갈음해 온 관행과 달리 여기선 축·막대·마일스톤·현재선이 뚜렷이 이름난 슬롯이라 명시가 더 정확하다.)*
- **element_vs_slide**: **fragment** = `<div class="viz-gantt" role="img" aria-label="…">` 안에 좌측 작업-라벨 컬럼 + 우측 플롯(공통 시간축). 각 막대는 `div`로 `left:%`(=`(start−t0)/span`)·`width:%`(=`(end−start)/span`)를 시간에 비례 배치, 마일스톤은 같은 좌표계 위 `◆` 점, 현재 시점은 세로 파선. **데모 host(별도 whole-slide)** = 이 fragment를 얹는 whole-slide는 `L-dc-*`(diagram-centric, `.s-full` + `.s-eyebrow` + 하단 캡션) 또는 `top-down`으로 **따로** 구성 — fragment 자체엔 헤더·아이브로우·제목을 넣지 않는다(레이아웃 ≠ 다이어그램, 규격 §5). host 크롬(아이브로우+캡션 ~80px)은 capacity 산식에서 이미 뺐다.
- **placement**: `[diagram-centric, top-down]`
- **built_on**: `.s-full`(host), 플롯 컨테이너(`position:relative`) + 막대 `div`(시간비례 `left`/`width`). **색 문법**: **강조 구간(현재/핵심 작업) = `--blue`**, **비강조 작업 = `--periwinkle`**, **지연·리스크·병목 구간 = `--coral-deep`**(주의 — 코랄은 오직 이 의미에만), 오류·심각 미달 = `--red`. 마일스톤 `◆` = `--blue`(구조 점 — 번호 배지 아님, 민트 fill 3종 규칙 무관), 축·격자선 = `--line`, 눈금·라벨 = `--ink`/`--gray-700`. **현재 시점 세로선 = `--ink` 파선(중립 구조 마커)** — 'today'는 경고가 아니라 위치 표시이므로 코랄을 쓰지 않는다(코랄 이중 의미 방지: 같은 화면의 '지연·리스크'와 색이 겹치면 색=의미가 무너짐). 현재선을 강조하고 싶으면 `--blue` 파선까지만 허용, 코랄은 불가.
  > **구현 메모(2026-07-15, shipped `kit/styles/patterns.css`) — 아래는 설계 당시 CSS 원안, 실제 클래스명은 이 메모가 정본이다:** `grid-template-columns` 대신 `.viz-gantt{display:flex;gap:16px;width:1000px;margin:0 auto}`(고정 너비 필수 — `.dc-stage`가 `align-items:center`로 자식을 shrink-to-fit 시키는데, 절대배치 자손은 부모의 내재적 너비 계산에 기여하지 못해 폭 없는 조상에 `%` 좌표를 얹으면 전부 0으로 붕괴한다; `.viz-radial`/`.viz-cycle` 등 기존 다이어그램도 전부 고정 width라 이 관행을 그대로 따름). 라벨열 `.vg-labels`(`flex:0 0 190px`) + `.vg-lab-spacer`(축 헤더 자리) + `.vg-label`(행당 56px) · 플롯 `.vg-plot`(`position:relative;flex:1 1 auto;padding-right:70px` — 우측 여백은 마일스톤 라벨이 100% 경계 밖으로 안 밀려나게) 안에 `.vg-axis`(`position:relative;height:32px`) + `.vg-tick`(`position:absolute;left:%`) + `.vg-row`(`position:relative;height:56px`) + `.vg-bar`(`position:absolute;top:18px;height:20px;border-radius:var(--r-pill)`, 기본 `--periwinkle`·`.is-key`=`--blue`·`.is-risk`=`--coral-deep`) + `.vg-ms`(마일스톤 라벨, `color:var(--blue)`) + `.vg-now`(`position:absolute;top:32px;bottom:0;border-left:2px dashed var(--ink)` — `.vg-plot` 기준 절대배치라 축 아래부터 마지막 행까지 행 수 무관하게 자동으로 전체 높이를 덮는다, 스펙 원안의 grid-row spanning보다 단순·견고). 데모 `.timing`(**블루** 시점 배지) 규칙과 결이 같다. **navy·그라데이션 금지, raw #hex 금지(흰 글자는 `var(--white)`).**
- **a11y**: `role="img"` + `aria-label="비례 시간축 간트: <t0>~<t1> 기간, 작업 N개 — <작업1> <시작1>~<종료1>, <작업2> <시작2>~<종료2>(<작업1>과 병렬), …; 마일스톤 <라벨> <시점>. 오늘 <today>."`. 막대·격자·`◆`·현재선은 장식이므로 개별 aria 없음 — 시작·종료·병렬 관계를 라벨 텍스트로 순서대로 담아 시각 정보를 대체, 전체를 하나의 img로.
- **sketch**:
```
┌────────────────────────────────────────────────────────────────┐
│ ▍EYEBROW · 제목                                (host: L-dc-*)   │  s-head+eyebrow는 host
│  작업 \ 축   1월    2월    3월    4월    5월    6월              │  비례 시간축(등간=실제 등간)
│              ├──────┼──────┼──────┼──────┼──────┼──────┤         │  --line 격자
│  기획       ████████                              ◆ 킥오프      │  ← --blue 강조 막대
│  설계            ▒▒▒▒▒▒▒▒▒▒                                     │  ← periwinkle(설계·개발 병렬)
│  개발                ▒▒▒▒▒▒▒▒▒▒▒▒▒▒                             │      세로 겹침=병렬 진행
│  테스트                        ▒▓▓▒▒▒▒▒   ┆                     │  ← ▓=coral 지연구간 · ┆=--ink 파선(오늘)
│  출시                                    ▒▒▒▒  ◆ 출시           │
│              └ 폭 = (종료−시작)/전체기간 · 좌표 = (시작−t0)/전체 ┘│  캡션은 host
└────────────────────────────────────────────────────────────────┘
   범례: --blue 강조 · periwinkle 비강조 · coral=지연/리스크 · ┆ --ink 파선=오늘(중립)
```
- **coded**: yes — `kit/charts/catalog.html` `data-slide="C-gantt"`, CSS `kit/styles/patterns.css` `.viz-gantt`/`.vg-*`. 브라우저 검증 완료(2026-07-15): 좌표 실측(`getBoundingClientRect`)으로 막대·눈금·마일스톤·현재선 위치가 설계값과 정확히 일치, 오버플로 0, 콘솔 에러 0.
- **density_note**: 작업 라벨 ≥17px(다이어그램 라벨 하한)·축 눈금 ≥17px 한 줄(≤5자). 막대 두께 20px·행 gap ~16px로 **7행이면 ~428px(=468 fragment − 40 축헤더) 안에 수렴**, 6행이 여유(범례 넣으면 6행 상한). 8행은 gap 붕괴·라벨 겹침이라 금지 → 표 축약/분할로 넘긴다. 마일스톤 라벨은 점 우측 1줄 ≥17px, 겹치면 위/아래 교차 배치. host 크롬(아이브로우+캡션 ~80px)은 capacity 산식에서 이미 공제 — fragment는 ~468px를 넘지 않아 548px 안에서 스크롤 없이 성립. 세로 패딩 합이 플롯 높이의 1/3 넘지 않게(토큰 치트시트 세로 규칙). **강조는 `--blue` 1계열로 한정**(한 화면 파랑 도배 금지), 나머지 막대는 `--periwinkle`, 지연·리스크만 `--coral-deep`, 현재선은 `--ink` 파선(코랄 아님).
- **source**: https://datavizcatalogue.com/methods/gantt_chart.html — **verified** (이 실행에서 WebFetch로 실재 확인). 요지 재표현: 행=활동·열=시간축, 막대 길이=활동의 소요(막대 시작=착수·끝=완료), 병렬로 도는 활동이 드러남, 마일스톤은 심볼로 표기, 현재일은 세로선으로 표시. 원문 통구절 복제 아님 — 짧은 귀속 표현만.
- **adaptation_note**: 소스의 **비례 시간축 + 기간 막대 + 병렬 + 마일스톤 + 현재선**을 CSS 절대배치(시간→`left`/`width` 비례)로 재표현(이미지·간트 SW 스크린샷 아님, 시점·기간은 텍스트 라벨). **`L-vf-spine-timeline`과의 결정적 차이를 명문화**: 스파인 타임라인은 *점 사건을 등간격 지그재그로 나열*(축 비례·기간·병렬 없음)인 **레이아웃**, 이 항목은 *실제 간격이 비례하고 막대가 기간·병렬을 담는* **element**. 소스가 상한 미명시 → 가독성 하한(17px)·세로예산(548px − host 크롬 ~80px = fragment ~468px) 산식으로 **작업 ≤7·마일스톤 ≤6** 캡을 우리가 규정(no-default 아님, 물리적 상한). **색은 강조 구간만 `--blue`, 비강조 `--periwinkle`, 지연·병목만 `--coral-deep`, 현재선은 `--ink` 파선(중립)** — 코랄을 '오늘' 표시에 쓰지 않아 코랄=주의라는 문법을 한 화면 안에서 지킨다. navy·그라데이션·민트 fill 배지 미사용. 의존 화살표(소스의 activity 연결선)는 정적 슬라이드 가독성상 기본 생략, 필요 시 `--blue` 얇은 커넥터 1~2개만. **info_shapes는 D-funnel과 동형으로 `[flow, numeric]`** — 등재는 flow 절(비례축이 필요할 때), numeric 절엔 괄호 각주만(양 비교가 목적 아님).
