# elements-code — 소스코드 게시 element 그룹 (재사용 fragment)

> 이 파일의 항목은 whole-slide가 **아니다**. `.s-full`/`.center-msg` 같은 **레이아웃 위에 얹는 재사용 element(fragment)** 다 — 레이아웃 ≠ element(카탈로그-규격 §5).
> 차트/다이어그램과 별개 그룹인 이유: 카탈로그의 `code-viz`는 *"차트를 코드/SVG로 그린다"*는 뜻이지 **소스코드 게시가 아니다.** 라인번호 + 특정 줄 하이라이트 + 여백 콜아웃으로 "이 줄이 뭘 하나"를 짚는 element가 없어 코드 설명 슬라이드가 회색 `<pre>` 덤프로 떨어졌다. 이 그룹이 그 빈칸을 채운다. **도메인이 바이브코딩이라 최우선.**
> `kind`는 차트/다이어그램의 `chart|diagram`이 아니라 신설 값 **`code`**(소스코드 전시물). 색은 문법: **코드 텍스트 = `--ink` · 배경 = `--surface` · 강조 줄 배경 = `--blue-soft`(옅은 블루) · 콜아웃 번호·리더선 = `--blue`(구조).** 무지개 구문강조 금지 — 강조는 색토큰이 아니라 "강조 줄 배경 + 콜아웃"이 담당(색=의미·평면 유지). 전부 CSS 텍스트로 렌더(이미지 아님).

## fragment 클래스 명명 — `.viz-<slug>` 규칙과 정합
차트/다이어그램과 동일하게 `.viz-<slug>` 베이스를 쓴다(whole-slide 승격 금지).

| slug | fragment 클래스 | 하위 요소 | 얹히는 대표 레이아웃 |
|---|---|---|---|
| code | `.viz-code` | `.co-bar`(파일명/언어 · 선택) · `.co-rows`(3열 grid: 번호·소스·콜아웃) · `.co-row`(`display:contents`, 한 줄) · `.co-row.is-hl`(강조 줄) · `.co-num`/`.co-src` · `.co-note`+`.cn`(여백 콜아웃·블루 번호, 빈 줄은 `:empty`로 구분선 자동 제거) | `L-dc-hero`(diagram-centric 무대 전체) · top-down 패밀리 셸(`.s-full`+`.canvas-fill`, 상단 타이틀 밴드 아래 코드 채움) |

> **구현 메모(2026-07-15, shipped `kit/styles/patterns.css`):** 스펙 원안의 SVG 리더선(`.vc-lead`) 대신, num/src/note 3열을 `.co-rows{display:grid;grid-template-columns:2.6em 1fr minmax(240px,320px)}` + `.co-row{display:contents}`로 흘려 **행 정렬 자체가 리더선** 역할을 하도록 재구현했다 — 좌표 계산 없이 강조 줄 ↔ 콜아웃이 항상 같은 행에서 짝지어져 콘텐츠 교체에 안전하다. 콜아웃 없는 행은 `.co-note`가 빈 `<span>`이라 `:empty` 선택자로 좌측 구분선이 자동으로 사라진다. 아래 `built_on`의 `.vc-*` CSS 스니펫은 설계 당시 원안이며, 실제 클래스명은 위 표의 `.co-*`가 정본이다.

> `.cn`(콜아웃 번호)은 **블루 fill**이다 — 민트 fill 배지는 `.num-circle`·`.work-step .n`·`.pd-dot.is-active` 셋뿐(토큰-치트시트). 코드 콜아웃 번호는 다이어그램/플로우 노드와 같은 부류 → **블루 유지**(구조=블루).

---

### E-code — 주석 코드 블록 / Annotated Code Block

- **id**: `E-code`
- **name**: 주석 코드 블록 / Annotated Code Block
- **kind**: `code`  *(차트/다이어그램이 아닌 신설 element 종. `chart|diagram` 스키마의 3번째 종으로, 소스코드 전시물을 가리킨다.)*
- **info_shapes**: `[concept]`
  - *(rationale: 정보모양-taxonomy 12개 중 이 element가 서비스하는 모양은 `concept`("A란 무엇인가"를 코드 한 조각 + 줄별 설명으로 전달). `screen-operation`의 **주석 문법**(번호·테두리로 특정 지점 지시)을 빌려오지만, `screen-operation`은 "실제 UI 화면 단계(버튼→메뉴→클릭)"라 스크린샷이 대상이고 코드가 아니다 — 그래서 인접일 뿐 값은 `concept`. 코드로 **절차**를 보이면 보조로 `flow`가 겹칠 수 있으나, "이 줄이 뭘 하나"의 주 모양은 개념 설명이다.)*
- **data_shape**: 짧은 HTML·CSS·JavaScript 코드 한 조각(HTML 태그·CSS 규칙·JavaScript 동작) + **특정 줄 몇 개**를 지목해 설명. 줄들 사이에 순서·인과가 핵심이 아니라 "이 줄의 역할"이 초점일 때. 판별: 순서 절차가 핵심이면 flow-v(단계 스택), UI 화면 조작이면 screen-operation(주석 스크린샷), 코드를 배경 분위기로만 깔면 full-bleed 코드(주석 없음), 값 비교면 차트.
- **when_to_use**: 실제 코드 한 조각을 띄우고 **특정 줄을 짚어** "이 줄이 무엇을 하는지" 초보에게 풀이할 때 — 바이브코딩이 만든 HTML·CSS·JavaScript 코드 읽기, CSS 규칙의 역할 설명, JavaScript 동작 한 줄 해설. (소스: Material for MkDocs — `hl_lines`로 "Specific lines can be highlighted", code annotations는 "a comfortable and friendly way to attach arbitrary content to specific sections of code blocks by adding numeric markers".)
- **when_to_avoid**: 코드가 ~12줄을 넘겨 한 화면에 안 들어갈 때(→ 발췌·다중 슬라이드), 특정 줄을 지목하지 않고 통째로만 보일 때(→ 주석 없는 코드 패널/full-bleed), 대상이 코드가 아니라 UI 화면 단계일 때(→ `screen-operation` 주석 스크린샷), 터미널 명령·출력 로그일 때(→ 터미널 블록), 줄별 설명이 초보에게 과부하면(→ 개념 흐름 flow-v로 추상화). **어떤 element도 기본이 아니다** — data_shape가 "코드 + 지목할 줄"일 때만 고른다.
- **capacity**: 코드 **6~12줄**(줄당 ≤~50자, 초과 시 줄바꿈 위험) + **강조 줄 ≤4** + **여백 콜아웃 ≤4**(각 ≤2줄·≤18어, **풀이 텍스트 ≥17px** — 다이어그램 라벨/캡션 하한 준수). 선택적 상단 `.vc-bar`(파일명/언어) 1줄(≥17px). 강조가 5줄↑이면 "강조가 곧 평문"이 되어 무의미 → 캡. (산식: 코드 mono 20px×line-height 1.6 ≈ 32px/줄 → 세로예산 548px에서 패널 여백·`.vc-bar` 제하면 물리적으로 ≤12줄.)
- **content_slots**: `filename_bar`(선택 · 파일명/언어) · `code_lines[6..12]`(`.vc-line`, 라인번호 gutter 포함) · `highlight_lines[≤4]`(`.is-hl` 지목 줄) · `callouts[≤4]`(`.cn` 블루 번호 + 풀이 ≤2줄) · `lead_lines`(강조 줄↔콜아웃 잇는 블루 리더선)
- **element_vs_slide**: **(필수)** **fragment** = `<div class="viz-code" role="img" aria-label="…">` — 내부는 좌측 코드 패널(`.vc-gutter` 라인번호 + `.vc-line`들, 지목 줄에 `.is-hl`)과 우측 여백 콜아웃(`.vc-callout`, 각 `.cn` 블루 번호 + 짧은 풀이)을 `.vc-lead` 얇은 블루 리더선으로 잇는다. fragment 자체엔 아이브로우·슬라이드 제목을 넣지 않는다. **데모 host(whole-slide)** = 이 fragment를 얹는 슬라이드는 **실재 레이아웃** `L-dc-hero`(diagram-centric, `.s-full`+`.s-eyebrow` 무대 전체에 코드 fragment를 stage-figure로 얹고 하단 22px 캡션)로 별도 구성한다 — 다른 element가 실재 host를 참조하듯(D-radial→`L-dc-radial-hub`) 코드 fragment는 `L-dc-hero`를 host로 삼는다. 상단 타이틀 밴드가 필요하면 **top-down 패밀리 셸**(`.s-full`+`.canvas-fill`, 밴드 아래 코드 채움)에도 그대로 얹힌다(패밀리 셸이지 신규 ID 아님). **`L-dc-code`라는 레이아웃은 존재하지 않는다 — 명명 금지.** "레이아웃 ≠ element."
- **placement**: `[L-dc-hero]` (+ top-down 패밀리 셸 `.s-full`+`.canvas-fill`; 신규 레이아웃 신설 없음)
- **built_on**: `.s-full`(host), `--surface`(패널 배경) · `--ink`(코드 텍스트) · `--font-mono`(JetBrains Mono) · `--gray-400`(라인번호 gutter·비강조) · `--blue-soft`(강조 줄 배경) · `--blue`(콜아웃 번호 fill·리더선) · `--r-md`(패널 라운드) · `--shadow-md`(카드 그림자). **신규 CSS 요지**: `.viz-code{background:var(--surface);border-radius:var(--r-md);box-shadow:var(--shadow-md);font-family:var(--font-mono);color:var(--ink);position:relative;display:grid;grid-template-columns:1fr auto}` · 코드 열은 `.vc-line{display:flex}` + `.vc-num{color:var(--gray-400);width:2.4em;text-align:right}` · 강조 `.vc-line.is-hl{background:var(--blue-soft)}` · 여백 `.vc-callout{...}` 안 `.cn{background:var(--blue);color:var(--white);border-radius:var(--r-pill)}`(블루 원, 흰 숫자 = 어두운 fill 위 흰 글자라 대비 OK) · 리더선 `.vc-lead{height:1px;background:var(--blue)}`(또는 인라인 SVG `<line stroke="var(--blue)">`). 데모의 `.code-diagram`/`.mono`(`--font-mono` 게시 규칙)와 같은 코드-텍스트 원칙을 재사용.
- **a11y**: `role="img"` + `aria-label="주석 코드 블록(<언어> <파일명>, N줄): 강조 <n>번째 줄 = <풀이1>, <m>번째 줄 = <풀이2> …"`. 콜아웃 번호·리더선·라인번호 gutter는 장식이므로 개별 aria 없음, 전체를 하나의 img로. *(대안: 코드를 스크린리더가 실제로 읽어야 하면 코드 열은 실제 텍스트로 두고 콜아웃만 `aria-hidden`; 기본형은 카탈로그 관례대로 1 img.)*
- **sketch**:
```
┌──────────────────────────────────────────────────────────┐
│  index.html                                (파일명 바·선택) │
│ ┌──────────────────────────────┐                          │
│ │ 1  <!DOCTYPE html>            │                          │
│ │ 2  <meta charset="UTF-8">     │                          │
│ │ 3    <h1>안녕하세요...</h1> ░░ │ ──①── 화면에 무엇이 들어가는지 정한다 │
│ │ 4    <style>                  │                          │
│ │ 5      h1 { color: teal; }░░░ │ ──②── 색과 크기를 꾸민다   │
│ │ 6    </style>                 │                          │
│ │ 7    <button onclick=...>░░░░ │ ──③── 누르면 반응하게 만든다 │
│ │ 8  </html>                    │                          │
│ └──────────────────────────────┘   └ 얇은 블루 리더선       │
│   ░░ = 강조 줄(blue-soft 배경)   ①②③ = 블루 콜아웃 번호      │
└──────────────────────────────────────────────────────────┘
```
- **coded**: yes — `kit/charts/catalog.html` `data-slide="C-code"`(host 셸 `L-dc-hero` 패턴 재현), CSS `kit/styles/patterns.css` `.viz-code`/`.co-*`. 브라우저 검증 완료(2026-07-15): 오버플로 0(`.dc-stage` 456×1152 안), 콘솔 에러 0.
- **density_note**: 코드 텍스트는 **본문(22px 하한)이 아니라 별도 코드-디스플레이 종**이므로 mono **20px**가 하한(등폭·라인번호 정렬을 위해 서술 본문과 분리 관리 — 22px 하한 예외를 여기서 명시적으로 정당화). 콜아웃 풀이·`.vc-bar`는 다이어그램 라벨/캡션에 해당해 **≥17px** 하한을 못박는다(그 아래로 눌리지 않음). 산식 32px/줄 × ≤12줄 + `.vc-bar` 1줄이 세로예산 **548px** 안에 들어가 **스크롤 0**. 강조 줄·콜아웃은 최대(강조 ≤4, 콜아웃 ≤4)에서도 리더선 교차 없이 우측 여백에 수용. 가독성 하한(코드 20px·라벨 17px)을 하회하지 않음.
- **source**: https://squidfunk.github.io/mkdocs-material/reference/code-blocks/ (verify pending — 본 실행에서 WebFetch 재확인 못 함; 라인번호 `linenums` · `hl_lines` 줄 강조 · code annotations 번호 마커 세 기능을 확증하는 안정 페이지로 알려짐, 원본 복제 아님·재표현만)
- **adaptation_note**: 소스는 라인번호 · `hl_lines` 줄 강조 · 번호 마커 주석 **세 기능을 확증**하는 영감일 뿐(원본 복제 아님). Material의 클릭-펼침 툴팁 주석 대신, 정적 슬라이드용으로 **여백 콜아웃 + 얇은 블루 리더선**(항상 펼쳐진 상태)으로 재표현 — 발표·인쇄에서 전부 보이게. 소스의 다색 구문강조(syntax highlight)는 **채택 안 함**: 강의장 가독성·평면 토큰 시스템·"색=의미" 헌장에 맞춰 코드는 `--ink` 단색, 강조는 오직 강조 줄 배경(`--blue-soft`) + 콜아웃이 담당. 콜아웃 번호는 민트가 아니라 **블루**(구조), 세로예산 548px·mono 20px 산식으로 **≤12줄·강조 ≤4** 캡을 우리가 규정(no-default 아님, 물리적 상한).
