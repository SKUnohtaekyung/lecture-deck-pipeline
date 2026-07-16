# 차트·다이어그램 역인덱스 — 정보 모양 → 후보 element

> 정보 모양이 **numeric·comparison·containment·structure·mapping·flow** 일 때, 여기서 **element(차트/다이어그램)** 를 골라 레이아웃(`../layouts/by-shape.md`)에 **얹는다**. 레이아웃 ≠ element.
> (declaration·concept·classification·checklist·screen-operation은 element 없이 레이아웃만.)
> 선택은 **data_shape**가 정한다 — 어떤 element도 기본이 아니다(규격 §1.A).

---

## numeric (수치·비율) — 양·비중·추세
1. `C-column` — 소수 카테고리(3~7) 값 비교, 순서형/시간형 축
2. `C-hbar` — 순위·리더보드 또는 긴 라벨
3. `C-line` — 시계열 추세, 계열 ≤4 정밀 비교
4. `C-pie` / `C-donut` — 부분-전체 비중 ≤6조각 / (+중앙 요약 수치)
5. `C-gauge` — 단일 값 대 목표·범위(달성률·완성도)
6. `C-stacked-bar` — 카테고리별 부분-전체(세그 ≤4)
7. `C-area` — 누적/부피 추세(계열 ≤3)
8. `C-lollipop` — 값이 근접한 항목의 순위 점비교
9. `C-diverging` — 전후·목표대비 발산(양방향)
   *(D-funnel도 numeric 겸: 단계별 물량 감소)*

## comparison (비교) — 두(이상) 대안 견줌
1. `C-column` / `C-hbar` — 항목 값 직접 비교
2. `C-diverging` — 전/후·A/B 대칭 대비
3. `C-lollipop` — 근접값 순위
4. `C-stacked-bar` — 카테고리별 구성 비교
5. `D-venn` — 두 집합의 공통·차이(부분 겹침)
   *(레이아웃 comparison 후보는 `../layouts/by-shape.md` 참조)*

## containment (구성·포함) — 부분-전체·중첩
1. `D-concentric` — 완전 포함(안이 밖에 속함, 초점 링 강조)
2. `D-venn` — 부분 겹침(교집합)
3. `D-tree` — 여러 계층 부분-전체
4. `D-pyramid` — 층위 구성(토대→정점)
5. `D-radial` — 중심이 위성을 아우름

## structure (구조·관계) — 요소 + 관계
1. `D-network` — 노드-링크 관계망(허브·군집)
2. `D-tree` — 위계 트리
3. `D-matrix` — 2축 포지셔닝(사분면)
4. `D-radial` — 중심-방사 구조
5. `D-pyramid` — 층위 구조 · `D-concentric` — 중첩 구조

## mapping (매핑) — A→B 대응
1. `D-matrix` — 2축 조합 → 위치/처방 대응
2. `D-radial` — 중심 ↔ 위성 대응
3. `D-network` — 노드 ↔ 노드 유향 연결
4. `D-flow-h` — 입력 → 출력 파이프라인

## flow (흐름·단계) — 순서·절차
1. `D-flow-h` — 가로 선형 절차(3~6, 좌→우)
2. `D-flow-v` — 세로 절차(단계 설명이 길 때)
3. `D-cycle` — 순환 반복(끝이 곧 시작)
4. `D-funnel` — 수렴·드롭오프(단계별 감소)

---

## element 목록 (fragment 클래스)

| 그룹 | id · fragment | 모양 |
|---|---|---|
| charts-basic | `C-column`·`C-hbar`·`C-stacked-bar`·`C-line`·`C-area` (`.viz-column`·`.viz-hbar`·`.viz-stacked`·`.viz-line`·`.viz-area`) | numeric(+comparison) |
| charts-ratio | `C-pie`·`C-donut`·`C-gauge`·`C-diverging`·`C-lollipop` (`.viz-pie`·`.viz-donut`·`.viz-gauge`/`.viz-progress`·`.viz-diverging`·`.viz-lollipop`) | numeric(+comparison) |
| diagrams-relational | `D-concentric`·`D-venn`·`D-tree`·`D-pyramid`·`D-matrix` (`.viz-<slug>`) | containment·structure·comparison·mapping |
| diagrams-process | `D-radial`·`D-network`·`D-flow-h`·`D-flow-v`·`D-cycle`·`D-funnel` (`.viz-radial`·`.viz-network`·`.viz-flow(-h/-v)`·`.viz-cycle`·`.viz-funnel`) | flow·structure·mapping·containment |

> 전부 `.viz-<slug>` fragment — **whole-slide 클래스로 승격 금지**. 레이아웃의 시각 슬롯(예: `L-ct-figure`의 `figure`, `L-dc-*`의 `diagram`)에 삽입한다.
