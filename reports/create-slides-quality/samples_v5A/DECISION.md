# 5구간 조건 A — 슬라이드 결정표 (G1 제출물)

> **조건 A**: 개념KB의 `PPT 소재:`·`필수 진술:`을 **가린 채** 만들었다. 가림은 자기규율이 아니라 `scripts/kb_extract.py --blind`가 **기계로 강제**했다.
> 대조(구조 일치도 측정)는 **A를 확정한 뒤에만** 한다 — 만들면서 열면 실험이 무너진다.
> 기준 정본: `reports/create-slides-quality/P7_ab_criteria.md` §4-B.

## 사전 점검 7항 (references/phases/02-슬라이드맵.md)

- [x] 1. 정보 모양을 12 정준 모양 중 하나로 적었는가 → 아래 표 3열
- [x] 2. 역인덱스를 실제로 열었는가 — `kit/layouts/by-shape.md` + `kit/charts/by-shape.md` 둘 다
- [x] 3. 레이아웃과 element를 따로 골랐는가 → 4·5열 분리
- [x] 4. 형태를 순서 판별로 정했는가 (R-FORM-01) → 6열
- [x] 5. 강조 3종을 의미로 배정했는가 (R-EMPH-01) → 7열
- [x] 6. 직전 슬라이드와 구도·마무리가 다른가 (R-DEC-01) → 8·9열
- [x] 7. 이미지 4상태를 판정했는가 → 전 장 `NO_IMAGE`(자작 도해·차트로 충족, 생성 0장)

## 결정표 (9열)

| # | 청크 | 정보 모양 | 레이아웃 | element | 형태(R-FORM-01) | 강조 배정 | 마무리 | 동점 근거 |
|---|---|---|---|---|---|---|---|---|
| 1 | `C-IA` | **containment** — 보이는 UI는 IA의 일부 | `L-ct-pyramid` (층위) | 자작 2층 도해 | 산문 — 「보이는 것 ⊂ 결정한 것」은 순서를 못 바꾼다 | mark=«무엇을 어디에 둘지 정하는 일» · underline=IA≠User Flow | 코랄 오해 교정 띠 | containment 1순위가 concentric이나, 여기는 **위/아래 층위**라 pyramid |
| 2 | `C-화면순서` | **flow** — 무엇→입력→실행→결과 | 세로 위계 밴드(자작 · `L-vf-*` 계열) | 화면 모형 + 크기 3단계 | 산문 — 순서를 바꾸면 뜻이 깨진다 | mark=«가장 큰 것은 하나뿐» · text=«3단계» | 없음(밴드가 곧 결론) | flow에 가로 canvas도 있으나 **화면 순서는 세로**라 가로는 뜻이 어긋난다 |
| 3 | `C-화면문구` | **comparison** — ✗문구 ↔ ✓문구 4쌍 | `L-td-mapping-rows` | UI 조각 모형 | 병렬 — 네 쌍의 순서를 바꿔도 뜻이 유지된다 | mark=«버튼은 하는 일을 말한다» · underline=«고치는 법까지» | 민트 좌보더 규칙 | comparison 1순위 side-by-side보다 **1:1 대응**이 이 정보에 곧다 |
| 4 | `C-기본접근성` | **numeric** — 95.9% / 83.9% / 51% | `L-td-compare-bars` | **C-hbar**(차트가 주인공) | 병렬 — 세 실패의 순서는 무관 | mark=«기본 셋만 지켜도» · text=«95.9%» | 블루 띠 | **동점 규칙 ① 차트 주도**(프로필 §4). 수치가 셋이라 카드로 풀면 차트가 장식이 된다 |
| 5 | `C-DESIGN문서` | **concept**(코드 게시) | `L-ct-figure` | **E-code** — 실제 3줄 | 병렬 — 세 항목 순서 무관 | mark=«기준을 넘기는 연습» · underline=«낡는다» | 코랄 한계 스트립 | concept 일반은 element 없으나 **대상이 문서 원문**이라 E-code가 정타 |
| 6 | `C-디자인시스템토큰` | **mapping** — 이름 → 여러 사용처 | `L-dc-radial-hub` | **D-radial** | 병렬 — 사용처 순서 무관 | mark=«한 곳만 고치면» · text=«이름» | 민트 띠 | mapping 1순위 mapping-rows는 3번이 이미 씀 → **직전과 다른 구도**(R-DEC-01)로 radial |

## 구도·마무리 변주 확인

- 구도 6종 **전부 다름**: pyramid / 세로 위계 밴드 / mapping-rows / hbar 차트 / code / radial
- 마무리 6종: 코랄 오해 띠 / 없음 / 민트 좌보더 / 블루 띠 / 코랄 스트립 / 민트 띠 — **검은 배너 0**
- 골격 중복은 class 이름이 아니라 **DOM 구조**로 확인한다(R-PROMO-01) — 렌더 후 측정에서 검사

## 강조 감사

전 장 `.hl-mint-mark` ≤1 · 강조 합계 ≤3. 색 띠 위에는 mark를 얹지 않는다(R-COLOR-02).

## 이미지 판정

전 장 `NO_IMAGE`. 차트·도해는 CSS/SVG 자작이라 생성 0장 — `IMAGE_MODE` 질문 없음(SKILL.md 이미지 판정 게이트).
