# 레이아웃 카탈로그

슬라이드 **구도(레이아웃)** 라이브러리. 정보 모양을 판단해 고르며, 좌우분할 쏠림을 **공급 + 측정**으로 억제한다(금지 조항 없이).

## 어떻게 쓰나 (조립 시)
1. 슬라이드의 [정보 모양](../guide/정보모양-taxonomy.md)을 먼저 분류한다(원칙 B).
2. [`by-shape.md`](by-shape.md) 역인덱스에서 그 모양의 **후보 레이아웃**을 본다.
3. **직전 콘텐츠 슬라이드와 같은 패밀리를 피하고**, split은 희소하게(연속 금지) 고른다.
4. 차트/다이어그램이 필요하면 [`../charts/by-shape.md`](../charts/by-shape.md)에서 **element**를 골라 레이아웃에 **얹는다**(레이아웃 ≠ 다이어그램).
5. 항목의 `built_on`·`sketch`·`capacity`대로 조립(코드 코어는 `catalog.html`에서 복사).

## "no default" 헌장
모든 레이아웃은 **동급**이다. 어떤 것도 "기본/가장 흔한/주로 쓰는 레이아웃"으로 서술하지 않는다. 좌우분할(`split`)은 하나의 도구일 뿐 — 역인덱스에서 1순위로 오르지 않고, 균형 캡으로 희소하게 유지된다. 단조는 **금지가 아니라 다양한 공급 + 산출 분포 측정**으로 막는다.

## 8 구도 패밀리 · 균형 감사

| 패밀리 | 파일 | 목표 | 실제 | 대표 정보 모양 |
|---|---|---|---|---|
| full-bleed | [`families/full-bleed.md`](families/full-bleed.md) | 7 | **7** | declaration · numeric · concept |
| centered | [`families/centered.md`](families/centered.md) | 7 | **7** | declaration · concept · containment · structure |
| top-down | [`families/top-down.md`](families/top-down.md) | 8 | **8** | comparison · classification · numeric · mapping |
| grid-mosaic | [`families/grid-mosaic.md`](families/grid-mosaic.md) | 8 | **8** | classification · checklist · comparison |
| diagram-centric | [`families/diagram-centric.md`](families/diagram-centric.md) | 6 | **6** | structure · containment · mapping · flow |
| vertical-flow | [`families/vertical-flow.md`](families/vertical-flow.md) | 5 | **5** | flow · mapping |
| comparison-symmetric | [`families/comparison-symmetric.md`](families/comparison-symmetric.md) | 5 | **5** | comparison · contrast |
| **split** | [`families/split.md`](families/split.md) | **4 (≈8%)** | **4** | concept · comparison *(희소)* |
| **합계** | | **50** | **50** ✓ | |

> **좌우분할 캡 준수**: 50개 중 split은 4개(8%). 방향도 분산(좌글 2 + 우글 2)해 "항상 우측 시각" 편향을 차단.

### 구도 원형(composition shape) 분포 — 관객이 보는 매크로 모양

패밀리(의도)와 **직교**하는 축(규격 §2b). 같은 표·2×2가 여러 패밀리에 흩어져도 관객 눈엔 한 모양이라, **반복 감지·분포 측정은 이 축**으로 한다.

캐노니컬 50 기준(물리 54 = 캐노니컬 50 + `variant_of` 4):

| 구도 | 개수 | · | 구도 | 개수 |
|---|---|---|---|---|
| band-grid | 13 | · | panels-mirror | 4 |
| solo-center | 9 | · | split-asym | 4 |
| stage-figure | 9 | · | band-figure | 2 |
| flow-vertical | 7 | · | image-bleed | 2 |

> **관찰(2026-07-15 접기+확충 후):** 진짜 편향은 좌우가 아니라 세로·좌상단이다(좌우분할은 8%로 균형축). 중복 band-grid 4종을 `variant_of`로 접고 콘텐츠 레이아웃 4종을 순증해 **band-grid 28%→26%**로 완화하며 커버리지를 올렸다. 상세: `_dev/설계기록/`의 매크로 감사 · 구조개편 설계안 · 빈칸 목록.

## 항목 스키마·검증
각 항목의 필드 정의와 검증 체크리스트는 [`../guide/카탈로그-규격.md`](../guide/카탈로그-규격.md) §4·§7. 코드 토큰은 [`../guide/토큰-치트시트.md`](../guide/토큰-치트시트.md).

## 코드 코어 (재현성 — 조립 때 CSS를 새로 안 짜기)
- **`../styles/patterns.css`** — 브라우저 검증된 레이아웃/element CSS 라이브러리(deck.css·legibility **뒤에** 로드). central-contrast·quad·numbered-stack·definition·figure·dc-hero 등.
- **검증된 완성 덱(마크업 실물)**: `데모_제작규칙.html` — 해당 구도 `<section>`을 본떠 조립. (레이아웃/element CSS는 `../styles/patterns.css`에 이미 있음)
- 새 덱이 `scripts/verify_deck.py`를 통과하면 그 섹션 CSS를 patterns.css에 추가해 코드 코어 확장.

## 상태
- [x] 8 패밀리 MD 항목 캐노니컬 50개(물리 54, `variant_of` 4개 구도중복 접기) · 역인덱스 `by-shape.md` · 균형 감사(50/50, split 8%) · 구도 원형 축(§2b) 병기(band-grid 28%→26%)
- [x] 코드 코어 `patterns.css` + `catalog.html` **12항목**(L-fb-statement·L-ct-definition·L-td-table·L-td-metric-row·L-gm-quad·L-cs-central-contrast·L-vf-numbered-stack·L-dc-hero·L-td-glossary·L-td-claim-rationale·L-vf-case-acts·L-gm-pitfalls) — 브라우저 검증: 오버플로0·콘솔0·토큰·aria
- [ ] 나머지 38개 `<section>` catalog.html로 확장(버전 올리며)
