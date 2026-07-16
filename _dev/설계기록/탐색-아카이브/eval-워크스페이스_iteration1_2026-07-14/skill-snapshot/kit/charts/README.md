# 차트·다이어그램 카탈로그

레이아웃에 **얹는** 코드 시각화 **element(fragment)** 라이브러리. 전부 CSS/SVG(이미지 아님), 숫자·라벨은 텍스트.

## 차트 vs 다이어그램
- **차트** = 숫자·데이터 시각화(값이 있음): bar·line·pie·gauge·ratio.
- **다이어그램** = 숫자 없이 개념의 관계·구조·흐름: venn·concentric·tree·network·flow·cycle·funnel.

## 어떻게 쓰나
1. 슬라이드 정보 모양이 numeric·comparison·containment·structure·mapping·flow면 [`by-shape.md`](by-shape.md)에서 **element**를 고른다(선택은 `data_shape`가 정함).
2. `../layouts/by-shape.md`에서 그 모양의 **레이아웃(host)** 을 따로 고른다.
3. element fragment(`.viz-<slug>`)를 host 레이아웃의 시각 슬롯에 **얹는다**. **element ≠ whole-slide** — 옛 `.venn-slide`처럼 결합하지 않는다.

## "no default" · 색 문법
어떤 element도 "기본/가장 흔한 차트"가 아니다 — data_shape가 고른다. 색: 주요 구조·주 계열은 `--blue` · 경고 `--coral-deep`/`--red` · 안전·달성 `--mint-deep` · 비강조 데이터는 `--periwinkle`/`--surface`.

## 파일 · 21개 element

| 파일 | element |
|---|---|
| [`charts-basic.md`](charts-basic.md) | C-column · C-hbar · C-stacked-bar · C-line · C-area (5) |
| [`charts-ratio.md`](charts-ratio.md) | C-pie · C-donut · C-gauge · C-diverging · C-lollipop (5) |
| [`diagrams-relational.md`](diagrams-relational.md) | D-concentric · D-venn · D-tree · D-pyramid · D-matrix (5) |
| [`diagrams-process.md`](diagrams-process.md) | D-radial · D-network · D-flow-h · D-flow-v · D-cycle · D-funnel (6) |
| [`by-shape.md`](by-shape.md) | 역인덱스: 모양 → element |

## 적합성 규칙 (핵심)
pie/donut = 부분-전체 ≤6조각·합≈100 · line/area = 시계열(area는 y0 필수) · stacked = 세그 ≤4 · gauge = 단일 값 대 목표 · venn = 겹침 / concentric = 완전 포함 · cycle = 반복(끝→처음) / funnel = 단조 감소. 상세는 각 항목 `data_shape`·`when_to_avoid`.

## 코드 코어 (재현성)
- **`../styles/patterns.css`** — 브라우저 검증된 **fragment CSS**: `D-concentric`·`D-cycle`·`D-radial`·`D-tree`(+ 데모의 `.code-chart`/`.code-diagram`). deck.css·legibility 뒤에 로드.
- 마크업 실물: `데모_제작규칙.html`(막대·매핑·스크린샷). `concentric`·`cycle`·`radial`·`tree`는 `../styles/patterns.css`의 검증된 CSS + `diagrams-*.md` 스펙대로 조립.

## 상태
- [x] 21개 element MD · 역인덱스 `by-shape.md`
- [x] 코드 코어 `patterns.css` + `catalog.html` **6개**(D-concentric·D-cycle·D-radial·D-tree·C-bar·D-mapping) — 브라우저 검증: 오버플로0·콘솔0·aria 6/6
- [ ] 나머지 fragment(pie·line·hbar·gauge 등) catalog.html로 확장
