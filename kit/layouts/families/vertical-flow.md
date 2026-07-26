# vertical-flow — 세로로 흐르는 스텝/타임라인(위→아래) 구도 패밀리. 순서·단계·매핑을 세로축 한 줄기로 쌓아 시선을 위에서 아래로 끌어내린다.

> composition_family = `vertical-flow` · 주 대상 정보 모양: `flow`, `mapping`.
> 공통 골격: `.s-head`(상단 헤더) + `.s-full`(풀폭 본문) 안에 **세로 스텝 스택**. 단계 사이는 파란 아래 커넥터 `↓`로 관계를 명시(토큰 치트시트 §관계 커넥터).
> 1280×720에서 세로 예산은 대략 top:118 → 690, 약 560px. 22px 본문/1.78 기준 한 행이 헤드라인+1줄이면 ≈90–110px → **행 4~5개가 여유, 6개는 한 줄 텍스트에서만**. 모든 항목의 capacity는 이 예산에서 스크롤 없이 성립하도록 잡았다.

---

### L-vf-spine-timeline — 스파인 타임라인(좌우 교차) / Alternating Spine Timeline

- **id**: `L-vf-spine-timeline`
- **name**: 스파인 타임라인(좌우 교차) / Alternating Spine Timeline
- **composition_family**: `vertical-flow`
- **composition_shape**: `flow-vertical`
- **info_shapes**: `[flow]`
- **when_to_use**: 시간·단계가 있는 4개 내외 이벤트를 위→아래로 훑되, 각 마디에 날짜+헤드라인+한 줄 맥락이 붙어 단조로운 한 열보다 리듬이 필요할 때. 중앙 세로 스파인의 점(node)에서 카드가 좌/우로 번갈아 뻗어 시선을 지그재그로 내린다.
- **when_to_avoid**: 마디가 6개를 넘거나 각 마디 설명이 2줄↑이면 좌우 카드가 세로 예산을 초과한다(그땐 단열 스택으로). 순서가 없는 동급 나열(그리드)·양의 비교(차트)에는 부적합.
- **capacity**: 마디 4개 여유·5개 상한(6개는 카드당 헤드라인 1줄+본문 0줄일 때만). 마디당 timing 배지 1 + 헤드라인 ≤7어 + 본문 ≤1줄(22px). 아이콘/번호 원 1.
- **built_on**: `.s-head`, `.s-full`, `.num-circle`(민트 원 노드), `.timing`(날짜 배지), `.card`/`.card.surface`(좌우 카드), 커넥터 `↓`(세로 스파인), `.s-eyebrow`
- **content_slots**: `eyebrow`, `spine_nodes[]`(각: `date`, `headline`, `note`), `left_card`, `right_card`
- **sketch**:
```
┌────────────────────────────────────────────────────┐
│ ▍EYEBROW                                           │  s-head + eyebrow
│                    │(spine)                         │
│  ┌──────────┐     ●  2019                           │  node ①  → 우 카드
│  │          │    ╱                                  │
│         2020 ●  ┌──────────┐                        │  node ② ← 좌 카드
│              │  │  headline │                       │
│  ┌──────────┐●  2021                                │  node ③  → 우 카드
│  │ headline │╲                                      │
│         2022 ●  ┌──────────┐                        │  node ④ ← 좌 카드
│              │  └──────────┘                        │
└────────────────────────────────────────────────────┘
```
- **coded**: no
- **density_note**: 카드 본문 22px/1.78 1줄 유지 시 4마디는 마디간 gap 28px로 560px 안에 수렴. 5마디면 gap 16px·헤드라인만. timing 배지는 19px 하한(eyebrow급) 준수.
- **source**: https://venngage.com/blog/vertical-timeline/ (verified — 중앙 스파인+좌우 교차 마디, 각 마디 date·headline·context, 지그재그 리듬으로 단열 단조 회피 확인)
- **adaptation_note**: 원본(벤게이지 인포그래픽)은 컬러 블록·아이콘이 화려하다. 재표현은 스파인=블루 세로 커넥터, 노드=`.num-circle`, 날짜=`.timing` 블루 배지, 카드=`.card.surface`(블루-패널 배경 + `--blue-line-strong` 테두리)로 톤다운. 강조색은 블루 1계열로 한정(한 슬라이드 1~2곳 규칙), 좌우 카드 폭은 각 ~520px로 잡아 1280 폭 안에서 스파인 중앙정렬. 복제 아님 — 구조(스파인+교차)만 차용.

---

### L-vf-numbered-stack — 번호 스텝 스택(단열) / Numbered Step Stack

- **id**: `L-vf-numbered-stack`
- **name**: 번호 스텝 스택(단열) / Numbered Step Stack
- **composition_family**: `vertical-flow`
- **composition_shape**: `flow-vertical`
- **info_shapes**: `[flow]`
- **when_to_use**: 절차 1→2→3을 한 세로줄로 곧게 쌓아, 각 스텝이 [번호 원][헤드라인 + 한두 줄]로 좌측 정렬돼 읽히길 원할 때. 스텝 사이 파란 `↓`로 순서를 못박는다. 좌우 교차 없이 곧은 열이라 텍스트가 조금 더 들어간다.
- **when_to_avoid**: 스텝이 서로 순서 없이 동급이면(→ 그리드) 또는 두 항목의 우열 비교면(→ 대칭/차트) 쓰지 않는다. 스텝 6개↑ + 각 2줄↑은 세로 예산 초과.
- **capacity**: 스텝 3~4개(본문 ≤2줄) 또는 5개(본문 ≤1줄). 6개는 헤드라인만. 스텝당 `.num-circle` 1 + 헤드라인 ≤8어 + 본문 22px.
- **built_on**: `.s-head`, `.s-full`, `.num-circle`(민트 번호 원), `.s-title`/헤드라인, `.s-body`(22px), 커넥터 `↓`, `.accent-bar`(선택)
- **content_slots**: `eyebrow`, `steps[]`(각: `num`, `headline`, `body`)
- **sketch**:
```
┌────────────────────────────────────────────────────┐
│ ▍EYEBROW                                           │
│ ①  헤드라인 스텝 1                                  │
│ │   본문 한 줄 설명 …………………………                 │
│ ↓                                                  │
│ ②  헤드라인 스텝 2                                  │
│ │   본문 한 줄 설명 …………………………                 │
│ ↓                                                  │
│ ③  헤드라인 스텝 3                                  │
│     본문 한 줄 설명 …………………………                 │
└────────────────────────────────────────────────────┘
```
- **coded**: no
- **density_note**: 본문 2줄 = 22×1.78×2 ≈ 78px. 행 높이 ≈ 헤드라인 28 + 본문 78 + gap 28 ≈ **134px** → 세로 예산 548px에 **4행**(2줄 본문). 5행은 본문 1줄(행 ≈95px×5≈475px), 6행은 헤드라인만. 번호 원 민트 1색.
- **source**: https://www.slidekit.com/six-step-vertical-process-flow-template/ (verified — 번호 스텝이 세로 열로 순차 하강, 컬러 블록으로 단계 구분, 양측 텍스트 박스 확인)
- **adaptation_note**: 원본은 6스텝을 양측 텍스트 박스로 벌린 컬러 블록. 재표현은 번호를 `.num-circle`(민트 원)로, 블록 대신 좌측 정렬 헤드라인+`.s-body`로 납작하게, 단계 구분은 색 블록이 아니라 `↓` 커넥터로. 원본의 양측 배치는 폭을 먹으므로 단열 좌정렬로 눌러 텍스트 여유를 세로로 확보. 색은 블루 단색(색 남용 회피).

---

### L-vf-funnel — 세로 퍼널(수렴 단계) / Vertical Narrowing Funnel

- **id**: `L-vf-funnel`
- **name**: 세로 퍼널(수렴 단계) / Vertical Narrowing Funnel
- **composition_family**: `vertical-flow`
- **composition_shape**: `flow-vertical`
- **info_shapes**: `[flow]`
- **when_to_use**: 위가 넓고 아래로 좁아지는 수렴형 단계(모수→후보→선별→최종)를 세로로 보일 때. 각 층의 폭 자체가 "줄어듦"을 은유하고, 층 오른쪽에 짧은 라벨/수치를 붙인다. 단계마다 남는 양이 줄어드는 흐름 강조.
- **when_to_avoid**: 폭이 줄지 않는 동일 크기 단계(→ 번호 스택)나, 정확한 수치 비교가 핵심이면(→ bar/column 차트) 쓰지 않는다. 층 6개↑는 아래층이 너무 좁아 라벨이 안 들어감.
- **capacity**: 층 3~5개(4~5 권장, 6 상한). 층당 라벨 ≤6어 + 우측 note ≤1줄(22px). 폭은 위 ~760px → 아래 ~300px 선형 축소.
- **built_on**: `.s-head`, `.s-full`, 사다리꼴 층(인라인 SVG 또는 `.card` 폭 축소 스택), `.timing`/`.pill`(우측 수치), `.s-body`(우측 note), 커넥터 `↓`, `.s-eyebrow`
- **content_slots**: `eyebrow`, `stages[]`(각: `label`, `metric`, `note`)
- **sketch**:
```
┌────────────────────────────────────────────────────┐
│ ▍EYEBROW                                           │
│ ┌────────────────────────────┐   1,000  모수        │
│ └──────────────────────────┘  ↓                     │
│   ┌──────────────────────┐     420    후보          │
│   └────────────────────┘    ↓                       │
│     ┌──────────────┐          120    선별           │
│     └────────────┘        ↓                         │
│        ┌────────┐            18     최종            │
│        └────────┘                                   │
└────────────────────────────────────────────────────┘
```
- **coded**: no
- **density_note**: 5층 × 높이 ≈96px(사다리꼴 60 + gap 36) = 560px 이내. 우측 note/수치는 세로 중앙정렬, 22px 유지. 층 채움은 --surface/--periwinkle, 핵심 전환과 구조선은 블루로 둔다.
- **source**: https://www.presentationgo.com/presentation/powerpoint-funnel-diagram-with-5-steps/ (verified — 5단계가 위→아래로 폭 축소, 오른쪽 텍스트 플레이스홀더로 각 단계 라벨, 유입 화살표 확인). 보강: https://www.presentationgo.com/presentation/free-powerpoint-layered-funnel-process-4-stages/ (verified — 4층 적층 퍼널)
- **adaptation_note**: 원본은 곡선 유입 화살표+그라디언트 층. 재표현은 곡선/그라디언트 제거, 층은 단색 사다리꼴(--surface, 강조 최종층만 --blue), 유입 화살표 대신 층 사이 `↓` 단일 커넥터, 수치는 `.timing` 배지·라벨은 `.s-body`. 폭 축소는 토큰 색이 아닌 기하로만 표현해 "색 남용" 회피. 복제 아님.

---

### L-vf-chevron-map — 세로 셰브런 매핑 / Vertical Chevron Mapping

- **id**: `L-vf-chevron-map`
- **name**: 세로 셰브런 매핑 / Vertical Chevron Mapping
- **composition_family**: `vertical-flow`
- **composition_shape**: `flow-vertical`
- **info_shapes**: `[mapping, flow]`
- **when_to_use**: 각 행이 "주 항목(셰브런) → 그에 대응하는 상세/결과"로 이어지는 A↔B 매핑을 세로로 쌓을 때. 왼쪽 셰브런(번호·라벨)이 오른쪽 상세를 가리키고, 행이 위→아래로 진행하며 순서감도 함께 준다(매핑+흐름 겸용).
- **when_to_avoid**: 대응 관계 없이 그냥 동급 항목 나열이면(→ 그리드), 또는 순서만 있고 좌우 대응이 없으면(→ 번호 스택) 셰브런의 지향성이 과하다. 행 6개↑ + 우측 2줄↑ 초과 금지.
- **capacity**: 행 3~5개(5 상한). 행당 좌측 셰브런 라벨 ≤4어 + 우측 상세 ≤2줄(22px). 번호/아이콘 1.
- **built_on**: `.s-head`, `.s-full`, 셰브런 행(인라인 SVG 화살표 또는 `.pill`+`.num-circle`), `.s-body`(우측 상세), 매핑 커넥터 `→`, `.card.surface`(행 배경), `.s-eyebrow`
- **content_slots**: `eyebrow`, `rows[]`(각: `chevron_label`, `num`, `detail`)
- **sketch**:
```
┌────────────────────────────────────────────────────┐
│ ▍EYEBROW                                           │
│ ▐ ① 라벨 A  ▶ →  대응 상세 A …………………             │
│ ▐ ② 라벨 B  ▶ →  대응 상세 B …………………             │
│ ▐ ③ 라벨 C  ▶ →  대응 상세 C …………………             │
│ ▐ ④ 라벨 D  ▶ →  대응 상세 D …………………             │
│ ▐ ⑤ 라벨 E  ▶ →  대응 상세 E …………………             │
└────────────────────────────────────────────────────┘
```
- **coded**: no
- **density_note**: 5행 × 높이 ≈100px(셰브런 56 + 상세 2줄 여백) = 500px, 560 이내. 좌측 셰브런은 블루, 우측 상세 `.s-body` 22px. `→` 매핑 커넥터로 좌우 결속 명시.
- **source**: https://www.presentationgo.com/presentation/vertical-chevron-list-for-powerpoint/ (verified — 세로 정렬 셰브런 4개, 각 셰브런에 텍스트 박스, 위→아래 진행·번호 단위 확인)
- **adaptation_note**: 원본 셰브런 리스트는 각 셰브런이 독립 항목이지만, 재표현에서 셰브런 우측에 `→` + `.s-body` 상세 슬롯을 붙여 "라벨 → 대응 상세" 매핑 구조로 확장(원본 그대로가 아님). 셰브런은 컬러 남발 대신 블루 단색 + `.num-circle`, 행 배경 `.card.surface`. 화살표 지향성은 순서(flow)까지 겸하므로 info_shapes에 flow 병기.

---

### L-vf-cascade-map — 세로 캐스케이드 매핑 / Cascading Driver Map

- **id**: `L-vf-cascade-map`
- **name**: 세로 캐스케이드 매핑 / Cascading Driver Map
- **composition_family**: `vertical-flow`
- **composition_shape**: `flow-vertical`
- **info_shapes**: `[mapping]`
- **when_to_use**: 위의 상위 항목(원칙·모델·상위 지표)이 아래 항목을 결정·규정하는 "위가 아래를 정한다"식 하향 매핑을, 좌측 세로 스파인에서 노드가 우측 결과로 분기하며 아래로 흐르게 보일 때. 각 노드가 하위 결과를 가리키는 A→B 대응이 반복.
- **when_to_avoid**: 상위→하위 결정 관계가 없이 그냥 순서만이면(→ 번호 스택), 또는 부분-전체 포함이면(→ containment 다이어그램) 쓰지 않는다. 노드 5개↑는 분기 라인이 엉킴.
- **capacity**: 노드 3~4개(결과 카드 ≤2줄). **5개는 결과 카드 ≤1줄**. 노드당 상위 라벨 ≤5어 + 우측 결과 카드(22px). 스파인 커넥터는 `↓`(하강) + 분기 `→`.
- **built_on**: `.s-head`, `.s-full`, 좌측 세로 스파인(`↓` 커넥터), `.num-circle`(노드), `.card.surface`(우측 결과), 분기 커넥터 `→`, `.s-body`, `.s-eyebrow`
- **content_slots**: `eyebrow`, `spine`, `nodes[]`(각: `driver_label`, `result_card`)
- **sketch**:
```
┌────────────────────────────────────────────────────┐
│ ▍EYEBROW                                           │
│ ●─ 상위 A ──→ ┌───────────────────────────┐         │
│ │            │ 결과/지표 A ……………………       │        │
│ ↓            └───────────────────────────┘         │
│ ●─ 상위 B ──→ ┌───────────────────────────┐         │
│ │            │ 결과/지표 B ……………………       │        │
│ ↓            └───────────────────────────┘         │
│ ●─ 상위 C ──→ ┌───────────────────────────┐         │
│              │ 결과/지표 C ……………………       │        │
│              └───────────────────────────┘         │
└────────────────────────────────────────────────────┘
```
- **coded**: no
- **density_note**: 카드 2줄=78px, 노드 행 ≈128px(카드+gap) → 4노드 512px(548 이내). **5노드는 카드 1줄(행 ≈100px)로 낮춰 500px**. 좌측 스파인 노드 민트, 우측 카드 `.card.surface` + `.s-body` 22px. `↓`·`→` 커넥터는 블루 계열, 굵기로 위계.
- **source**: https://www.presentationgo.com/presentation/spine-node-process-powerpoint-diagram/ (verified — 세로 스파인이 백본, 곡선 커넥터로 노드 분기, 5스텝·노드가 초점 확인)
- **adaptation_note**: 원본 spine-node는 좌→우 읽힘의 프로세스지만, 재표현은 스파인을 좌측 세로축으로 고정하고 각 노드가 우측 결과 카드로 분기하는 "상위→하위 매핑"으로 의미 전환(원본 복제 아님). 곡선 커넥터는 직선 `→`로 단순화, 노드=`.num-circle`, 결과=`.card.surface`. 강조는 블루 1계열, 커넥터 위계는 색이 아니라 굵기로. 순서 은유보다 결정 관계가 주이므로 info_shapes=mapping 단독.


---

### L-vf-case-acts — 사례 3막 카드(상황·행동·결과) / Case Story in Acts

- **id**: `L-vf-case-acts`
- **name**: 사례 3막 카드(상황·행동·결과) / Case Story in Acts
- **composition_family**: `vertical-flow`
- **composition_shape**: `flow-vertical`
- **info_shapes**: `[concept, flow]`
  - *rationale*: 이 슬라이드가 존재하는 이유(**주 모양 = `concept`**)는 "추상 주장·개념을 **단일 사례 하나**로 접지"하는 것이다 — 절차 안내도, 대안 우열도 아니다. 다만 그 한 사례를 **상황→행동→결과**의 시간 순서로 풀기 때문에 `flow` *형식*을 빌린다. taxonomy는 한 슬라이드에 모양이 둘 이상일 때 병기를 허용하고(선례: `L-vf-chevron-map`=`[mapping, flow]`), sketch·`↓` 커넥터·순서 구조가 flow 차원을 명백히 갖는데 이를 누락하면 by-shape 색인을 왜곡한다. 그래서 **주 `concept` · 보조 `flow`**로 정직하게 병기한다(정보 모양 ≠ 표현 형식 원칙: 왜 존재하나=concept, 어떻게 읽히나=flow).
  - *concept vs flow 경계(중복 방어)*: 같은 flow-vertical 구도인 `L-vf-numbered-stack`은 **주 모양이 flow**(누구나 따라 하는 반복 가능 절차 1→2→3)다. 이 항목은 **주 모양이 concept**(재현 불가능한 *한 사례*의 이야기로 추상을 접지)라 방향이 반대다.
- **when_to_use**: 추상 주장·개념 뒤에 **하나의 실제 사례**를 붙여 설득할 때, 그 사례를 본문 불릿이 아니라 **상황 → 행동 → 결과 3막**의 세로 밴드로 구조화해 "무슨 상황에서 → 무엇을 했고 → 어떻게 됐다"를 순서대로 읽히고 싶을 때. 각 막은 **역할 이름표**(상황/행동/결과 — 번호가 아니라 서사적 배역)를 단 **닫힌 장면 카드**(`.card.surface` 밴드)로 감싸 세 막을 이질적 장면으로 구분하고, 밴드 사이 파란 `↓`가 인과의 진행을 못박는다.
- **when_to_avoid**: 사례가 여러 개라 병렬로 훑어야 할 때(→ 그리드 `L-gm-*`). 두 대안·두 입장의 정식 견줌/대립일 때(→ `comparison-symmetric`, 이 레이아웃엔 우열 위계가 없다). **누구나 재현하는 반복 절차**(따라 하는 1→2→3 스텝)일 때는 `L-vf-numbered-stack`이 맞다 — 이 항목은 *한 사례의 이야기*이지 처방된 단계 목록이 아니다(구별 표식: 여기엔 번호·`.num-circle`이 없고 **이름 붙은 배역 pill**만, 각 막이 닫힌 장면 카드; numbered-stack은 번호 원 + 열린 스파인). 추상 접지가 목적이 아니라 용어 정의 한 도해면(→ centered `L-ct-definition`/`L-ct-figure`). 막이 4개↑로 늘어 서사 초점이 흐려지거나 각 막 본문이 3줄↑이면 세로 예산 초과.
- **capacity**: 막(act) **정확히 3개**(상황·행동·결과 서사 아크 — 가변 N 아님). 막당 역할 `.pill`(≤4어·헤드라인과 같은 줄) + 헤드라인 `.s-lead` ≤7어(1줄) + 본문 `.s-body` 22px **≤2줄**. 막 사이 `↓` 커넥터 1개씩. `eyebrow` 1 + (선택)`lead_in` 추상 주장 1줄. 번호 배지·`.num-circle` 미사용. 4막↑ 금지.
- **built_on**: `.s-head`, `.s-full`, `.s-eyebrow`, `.card.surface`(각 막 장면 밴드), `.pill`(역할 이름표: 상황/행동/결과 — **블루**, 구조 라벨), `.s-lead`(막 헤드라인 — `.ca-act` 안에서 **22px**로 오버라이드), `.s-body`(막 본문 — `.ca-act` 안에서 **19px**로 오버라이드), 커넥터 `↓`(막 사이 인과, **블루**), `.hl-mint-text`(결과 막의 핵심어 절제 강조 · 민트딥 **글자**), (선택)`.s-title`/`lead_in` 추상 주장 1줄
- **content_slots**: `eyebrow`, `lead_in`(선택·1줄 추상 주장), `acts[]`(각: `role_label`(상황/행동/결과), `headline`, `body`), `connector`(`↓`)
- **sketch**:
```
┌────────────────────────────────────────────────────┐
│ ▍EYEBROW                                           │  s-head + s-eyebrow
│ (선택) 추상 주장 한 줄 …………………………                │  lead_in (1줄)
│ ┌────────────────────────────────────────────────┐ │
│ │ [상황]  헤드라인 …………                          │ │  act ①  card.surface
│ │  본문 22px ≤2줄 ……………………………                 │ │  pill=블루(배역·무번호)
│ └────────────────────────────────────────────────┘ │
│                     ↓  (인과)                       │  블루 커넥터
│ ┌────────────────────────────────────────────────┐ │
│ │ [행동]  헤드라인 …………                          │ │  act ②
│ │  본문 22px ≤2줄 ……………………………                 │ │
│ └────────────────────────────────────────────────┘ │
│                     ↓                               │
│ ┌────────────────────────────────────────────────┐ │
│ │ [결과]  헤드라인 …………  (핵심어 .hl-mint-text)    │ │  act ③  민트 글자 절제
│ │  본문 22px ≤2줄 ……………………………                 │ │
│ └────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────┘
   단일 사례 · 세로 3막(상황→행동→결과) · 좌우분할 아님
   번호 없음(배역 pill=블루) · 각 막 닫힌 장면 카드 ← numbered-stack과 구별
```
- **coded**: yes — `kit/layouts/catalog.html` `data-slide="L-vf-case-acts"`. 브라우저 검증 완료(2026-07-15): 오버플로 0(`.s-full` 548px 예산 내), 콘솔 에러 0.
- **density_note**: **아래 수치는 브라우저 실측(2026-07-26 · `.s-full` 548.0 / top 118)**이며, 이전 판의 산정(헤드라인 27px·본문 22px 전제)은 `.ca-act` 오버라이드를 반영하지 않아 폐기됐다. 타이틀 블록(`.s-eyebrow` 32.5 + `.s-title` 46.4 + accent-bar 5 + 마진) = **111.9px** → `.ca-stack` 가용 **436.1px**. 막 `.ca-act`(패딩 10×2, 헤드라인 `.s-lead` 22px → 렌더 26.5, 본문 `.s-body` 19px → 줄당 33.8) 실측 = **본문 1줄 124.3px · 2줄 158.1px**, `↓` 커넥터 `.ca-down` 19px, 스택 gap 4. — **3막(기본)은 각 막 본문 1줄이 상한이다**: 3×124.3 + 2×19 + gap 16 = **426.9 ≤ 436.1** ✓(여유 ~9px). **어느 한 막이라도 본문 2줄이면 460.8px로 `.s-full` 하단을 19.6px 초과**하고, 세 막 모두 2줄이면 528.4px로 **87.2px 초과**한다(실측 오버플로). 본문이 2줄 필요하면 막을 **2개로 줄인다**(2×158.1 + 19 + gap 12 = 347.2 ≤ 436.1 ✓). `lead_in`(선택 `.ca-lead` 1줄 = 실측 22.5px)을 쓰면 가용이 그만큼 줄어 3막 1줄 구성의 여유(~9px)가 사라지므로 3막에서는 병용하지 않는다. 역할 `.pill`은 19px 하한(eyebrow급) 준수, 헤드라인과 같은 줄. **민트 fill 배지 3종(`.num-circle`·`.work-step .n`·`.pd-dot.is-active`) 어느 것도 미사용** — 역할 라벨·`↓`는 블루(구조), 결과 막의 성공 뉘앙스는 `.hl-mint-text`(민트딥 글자) 또는 `.card.surface` + `--mint-deep` 보더로만(민트 fill 위 흰 글자 없음).
- **source**: https://www.themuse.com/advice/star-interview-method (verified 2026-07-15, WebFetch 실개봉 — STAR(Situation·Task·Action·Result) 4단 서사가 "잘 푼다" 같은 **추상 주장을 한 구체 사례의 순서 있는 이야기**로 전환함을 확인: Situation=장면 설정, Task=책임·목표, Action=취한 단계, Result=측정된 성과)
- **adaptation_note**: STAR은 인터뷰 답변용 프레임이라 원문을 복제하지 않고 **구조(추상 주장 → 순차 구체 서사)만** 차용한다. 4단(Situation·Task·Action·Result)을 덱 맥락의 **3막**으로 압축(상황=Situation+Task 통합 · 행동=Action · 결과=Result), 각 막을 `.card.surface` 세로 스택 + `↓` 인과 커넥터로 재표현. 원본의 인터뷰 화법·불릿 나열은 버리고 역할 `.pill`(무번호 배역)+헤드라인+`.s-body`로 납작하게. 색은 토큰만: 역할 라벨·`↓`=블루(구조), 결과 막만 `.hl-mint-text`/`--mint-deep`로 성공·접지를 절제 강조(fill·raw hex·`.num-circle` 금지).
