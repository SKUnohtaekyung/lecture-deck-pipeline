# 레이아웃 역인덱스 — 정보 모양 → 후보 레이아웃

> **원칙 B의 척추.** 슬라이드의 [정보 모양](../guide/정보모양-taxonomy.md)을 먼저 정하고, 여기서 후보를 뽑아 고른다.
> 규칙: **split(좌우 비대칭) 레이아웃은 어떤 모양에서도 1순위로 두지 않는다**(규격 §6, 원칙 A). 순위는 "그 모양에 얼마나 곧게 맞나"順.
> 차트/다이어그램 **element**가 필요한 모양(numeric·structure·containment·flow·mapping)은 `../charts/by-shape.md`에서 element를 골라 아래 레이아웃에 **얹는다**(레이아웃 ≠ element).

---

## declaration (선언) — 강한 한 문장·질문·키워드
1. `L-fb-statement` — 한 문장 주장이 풀블리드 중앙을 지배
2. `L-ct-statement` — 한 문장 테제, 헤더 유지한 중앙 무대
3. `L-fb-question` / `L-ct-question` — 수사적 질문(답은 다음 장)
4. `L-fb-oneword` — 한 단어/전환 키워드 초대형
5. `L-fb-quote` / `L-ct-quote` — 권위 인용 한 줄
6. `L-fb-photo` — 풀블리드 이미지 + 헤드라인 한 줄
7. `L-fb-caption-band` — 이미지 우세 + 하단 밴드 제목

## concept (개념) — 한 개념 + 보조 시각/정의
1. `L-ct-definition` — 용어 + 정의 한두 문장, 중앙
2. `L-ct-figure` — 개념 + 단일 도해(element 얹음), 중앙
3. `L-fb-caption-band` / `L-fb-photo` — 이미지가 개념 정서를 실을 때
4. `L-fb-quote` — 개념을 대변하는 인용
5. *(후순위·희소)* `L-sp-anchor-left` / `L-sp-visual-lead` / `L-sp-golden-left` / `L-sp-rule-right` — 글+시각 비대칭. **연속 금지·한 덱 소수만**

## comparison (비교) — 두(이상) 대안 정식 견줌
1. `L-cs-side-by-side` — 2대안, 기준별 카드 짝정렬
2. `L-cs-dual-table` — 2옵션 촘촘 표(기준 6~9)
3. `L-cs-triptych` — 3대안 동등 3열
4. `L-cs-before-after` — 전/후 상하 동등 밴드
5. `L-gm-compare-cards` — 3~4 플랜 카드(추천 1 강조 허용)
6. `L-gm-matrix` — 옵션×기준 ✓/✕ 매트릭스
7. `L-td-compare-bars` — 값 비교 양방향 막대
8. `L-td-table` — 밴드 + 데이터표 · `L-gm-quad` — 4항목 사분면
9. *(후순위·희소)* `L-sp-golden-left` / `L-sp-rule-right` — 좌글 짧은 견줌

## contrast (대비) — 두 주체 대립(추천 없음)
1. `L-cs-central-contrast` — 가운데 `≠` 커넥터 미러 2블록
2. `L-cs-side-by-side` — 좌우 미러 2패널
3. `L-cs-before-after` — 전↔후 상하 밴드

## flow (흐름) — 순서·단계 1→2→3
1. `L-vf-numbered-stack` — 번호 스텝 세로 단열
2. `L-vf-spine-timeline` — 좌우 교차 타임라인(4~5 마디)
3. `L-vf-funnel` — 위→아래 수렴 퍼널
4. `L-dc-flow-canvas` — 가로 흐름도(캔버스 폭, 3~6단)
5. `L-vf-chevron-map` — 셰브런(흐름+매핑 겸)
6. `L-dc-hero` — 절차를 한 장 도해로
   *(element: `../charts/by-shape.md` flow — flow-h·flow-v·cycle·funnel)*

## containment (포함) — 부분-전체·중첩
1. `L-ct-concentric` — 동심원(완전 포함, 초점 링 강조)
2. `L-dc-radial-hub` — 허브-스포크(중심이 위성 아우름)
3. `L-ct-pyramid` — 층위 구성 피라미드
4. `L-dc-hero` — 포함관계를 한 도해로
   *(element: `../charts/by-shape.md` containment — venn·concentric·tree)*

## mapping (매핑) — A→B 대응·연결
1. `L-td-mapping-rows` — 좌→우 행 1:1 대응
2. `L-dc-quadrant` — 2축 4분면 위치 매핑
3. `L-vf-cascade-map` — 상위가 하위를 정함(하향)
4. `L-vf-chevron-map` — 세로 라벨→상세
5. `L-dc-radial-hub` — 중심↔위성 대응
6. `L-dc-network` — 노드↔노드 연결망
7. `L-td-matrix` — 축 조합 → 칸 처방 · `L-dc-flow-canvas` — 입력→출력

## classification (분류·나열) — 동급 항목 훑기
1. `L-gm-cards-3x2` — 6항목 카드 격자
2. `L-gm-tiles-4x2` — 7~8 조밀 타일
3. `L-gm-quad` — 4항목 사분면
4. `L-gm-bento` — 히어로 1 + 보조(크기=위계)
5. `L-td-swiss-columns` — 3단 병렬 · `L-td-bento` — 밴드+비대칭 타일
6. `L-gm-gallery` — 이미지 6~8 갤러리
7. `L-gm-matrix` / `L-td-table` / `L-td-matrix` — 속성·기준 정렬

## numeric (수치·비율) — 양·비중·추세
1. `L-fb-bignum` — 단일 인상 지표 초대형
2. `L-td-metric-row` — KPI 3~5 스트립
3. `L-td-column-series` — 연도별 컬럼(추세)
4. `L-td-compare-bars` — 값 비교 막대
5. `L-gm-bento` — 대표 KPI + 보조 지표
   *(element 필수: `../charts/by-shape.md` numeric — bar·column·line·pie·donut·progress)*

## structure (구조·관계) — 요소 + 관계(위계·네트워크)
1. `L-ct-pyramid` — 위계 피라미드
2. `L-dc-network` — 네트워크 관계망
3. `L-dc-radial-hub` — 방사 구조
4. `L-dc-quadrant` — 2축 포지셔닝
5. `L-dc-annotated` — 구조도 + 번호 주석
6. `L-ct-figure` — 단일 구조 도해 · `L-dc-hero` — 구조를 한 장으로
   *(element: `../charts/by-shape.md` structure — tree·matrix·network·pyramid)*

## checklist (체크리스트·격자) — 점검 항목
1. `L-gm-checklist` — 2열 체크(✓/✗) 격자
2. `L-gm-tiles-4x2` — 점검 타일(상태 표식)

## screen-operation (화면 조작) — 실제 UI 단계
> 전용 레이아웃 없음 — **주석 스크린샷 element**(`../screenshots/`, P5)를 아래 host에 얹는다.
1. `L-dc-annotated` — 한 화면의 여러 지점을 번호로 짚음
2. `L-vf-numbered-stack` — 여러 화면 단계를 세로로
3. `L-dc-hero` — 단일 화면 크게

---

## 커버리지 감사

- **12 모양 전부** 후보 ≥2 확보(screen-operation은 host 3 + element).
- **split은 어느 모양에서도 1순위 아님** — concept·comparison에서만 후순위 등장.
- numeric·structure·containment·flow·mapping은 레이아웃 + `../charts/` element **조합**으로 완성.
