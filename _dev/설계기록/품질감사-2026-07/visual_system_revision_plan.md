> 이 문서는 2026-07-27 감사 에이전트의 반환 내용을 오케스트레이터가 복원한 것이다. 원 에이전트가 파일을 쓰지 않아 대화에만 존재하던 결과를 보존한 것이며, 인용은 표본 검증됐다.

## §A 그림자 감사
| 위치 | 대상 | 금지 해당 | 대체안 |
|---|---|---|---|
| `deck.css:105` | 발표모드 `.slide` 무대 | 애매(뷰어 크롬) | **사용자 확인 필요** |
| `deck.css:127,131,134,141,147,154,156,159,166,169` | 하단 리모컨·키보드도움말(Liquid Glass) | 애매 | **사용자 확인 필요**; `디자인시스템.md:76-77`이 명문화 중이라 규칙 충돌부터 정리 |
| `deck.css:298` `.card` | 카드 구분용 | 금지 | 그림자 제거 + `--line`/`--blue-line` 1px 보더 + soft fill |
| `deck.css:349,353,369` `.shot-frame`/`.shot-badge`/`.shot-row.on` | 스샷 프레임·배지 | 금지 | 보더+배경대비, 배지는 채움색+굵기 |
| `deck.css:433,518` `.cover-terminal`/`.pd-cube` | 터미널·큐브 drop-shadow | 금지 | 보더/면대비 |
| `deck.css:607~927`(9곳) | 1주차 전용 카드·배지 패밀리 | 금지(대량) | 보더+fill. **`deck.css:720` `.actor-card`가 이미 그림자 없이 성립 — 선례** |
| `patterns.css:32,44,57,62,79,93,108,140,333,335,349,358,362,378,391,393,423,436,455`(19곳) | 코드시각화 + "Week 1 extension" 카드군 | 대부분 금지. **`patterns.css:335` `.fl-node.key`가 p19 파란 부유박스의 정확한 원인** | 강조는 fill+보더로 |
| `shell.html:30,59,77,105,111,140,176,215,230,252`(10곳) | 2주차 신규 구도 10종 전량 | 금지 | 낙폭 작음(`shadow-sm/md` 위주) |

**1주차 비교 — 회귀 아님**: 1주차 덱에 인라인 `box-shadow` 14곳. `patterns.css:374` 주석이 "Week 1 extension"이라 명시 — 그림자는 1주차가 만들어 공유 kit에 정본화한 기존 관행이며 수정 범위는 `kit/styles/*.css` 전체. 1주차 산출물은 동결이라 손대지 않되, kit 수정은 1주차 생성물에 소급되지 않는다.

## §B 레이아웃 반복 측정
| | 고유 family | 「카드N+하단배너」 | 최장 연속 동일 family |
|---|---|---|---|
| 1주차(74/75) | **51종** | 2/74 = **2.7%** | 4장(의도된 비유블록) |
| 2주차 core(75/108) | **22종** | 18/75 = **24.0%** | 2장 |
| 2주차 전체(107) | — | 22/107 = 20.6% | — |
평결: 2주차가 약 **9배** 반복적. 단 연속 반복이 아니라 **비연속 고빈도 재사용** — 설명 화면 4장 중 1장꼴로 「정의/리드 + 카드 2~3개 + 하단 전체폭 `callout`」 레시피 재사용. 현행 인접 검사로는 원리적으로 못 잡는다.

## §C V2 6장 Keep/Drop
- p7 `w2-target`: KEEP 3단 스캐폴드+앵커화살표 / DROP `tg-case` 카드그림자(`shell.html:140`), 이미지 박스가 카드처럼 도킹됨
- p13 `w2-typecard`: KEEP 실제 스샷 병치 아이디어 / DROP `.tc-shot`(`shell.html:177`) 100px 레터박스 회색 필러, 3+2 비대칭 행높이 불일치. **근본 원인은 레이아웃이 아니라 원본 스샷 종횡비 불일치 — 통일 비율 재크롭 선행 필수**
- p14 `w2-analogy`: **전체 DROP**. 사용자가 명시 거부한 "가로 이미지 슬롯 먼저, 내용 끼움" 구조 그대로. 재사용 원리 없음
- p19 `w2-itr`: KEEP 경고선행 원리(S3ITR 계승) / DROP `fl-node.key` 파란 부유박스, 두 행이 동일 박스-화살표-박스 반복이라 복붙처럼 읽힘
- p35 `w2-handoff`: **6개 중 최강**. S3HUM 원리 정확 계승, 배경색만으로 분리 충분 / DROP `.hf-panel` 그림자(`shell.html:230`)뿐
- p58 `w2-stepwarn`: KEEP 경고선행+3단계 / DROP 박스 폭(~1150px)이 내용(~550px) 대비 과대해 민트 빈 면 절반. 빈 공간을 카드 크기로 메우지 말고 실콘텐츠로 채울 것

## §D 투명 PNG 배치 레시피 6종 (1주차 근거)
1. **코너 도킹** — `deck.css:322-331` `asset-slot--hero/support/spot`, `position:absolute`. 카드 없이 화면 모서리에 떠서 텍스트와 별개 레이어. 예 S00 hero, S07, S09
2. **그리드 셀 임베드** — `patterns.css:378,426,440`. PNG가 카드 상단 고정폭 슬롯을 채워 "이미지 파트"가 됨. 예 `journey-week-card`(132px), `app-type-card`
3. **배경 베드** — `s05a-data-design-background-v1.png` + `asset-slot--hero`. 전경 목업 뒤 풀블리드 텍스처, z-레이어링
4. **실사 스샷 + 원문자 캡션** — `data-asset-kind="screenshot"` + `<figcaption>①…`. 일러스트가 아닌 실제 OS/앱 화면을 hero로
5. **캐릭터 모티프 반복** — `character-art` 수식자, s45/s46/s50/s56에 동일 스타일 재사용하되 위치를 `--lower-left`/`--center-right`로 달리해 반복감 회피
6. **라벨 붙은 개념 다이어그램 PNG** — `data-viz="issue-type-check"`/`"week-file-structure"`. CSS 대신 PNG를 support 슬롯에 배치, 텍스트 불릿과 나란히

## §E 13개 화면모양 → 패밀리 매핑
이미지중심=`L-fb-photo`/`L-ct-figure`+레시피1·3(Extend) · 좌우비교=`L-cs-side-by-side`(Extend, 그림자만 제거) · 전후비교=`L-cs-before-after`(Extend, C5-10에 직접) · 과정흐름=`L-vf-numbered-stack`/`D-flow-h`(Extend, w2-stepwarn 폭 버그 선수정) · 실제화면=`L-dc-annotated`+레시피4(Extend) · 그래프=`kit/charts/` numeric군(Extend, 미사용) · **대화사례=신규 `L-vf-dialogue`(New, kit에 채팅버블 CSS 없음)** · 전체폭정보=`L-dc-flow-canvas`/`L-td-swiss-columns`(Extend) · **개념관계도=w2-handoff를 `L-dc-labeled-connector`로 승격(New)** · 고밀도설명=`L-td-table`/`L-td-glossary`(Extend) · 체크리스트=`L-gm-checklist`/`L-gm-pitfalls`(Extend) · 단계별시연=`L-dc-annotated`+`by-shape.md:106` 기존 규칙(Extend) · 투명PNG결합=단일 패밀리 아님, §D 6레시피를 `kit/guide/`에 배치 가이드로 신설
**레이아웃 리듬 규칙**: 클러스터 안에서 동일 shape 2회 연속 금지, 정의 다음엔 flow나 comparison, 그 다음은 image-lead나 checklist로 교대. §B가 밝힌 문제가 비연속 과다재사용이므로 인접 검사가 아니라 **클러스터 단위 shape 카운트 상한**(예: 6장 교시 안에서 동일 family 2회 초과 금지)으로 걸어야 한다.

## §F 얇은 콘텐츠 기계적 감지 신호
`verify_draft_quality.py`의 `_info_units()`는 판별력 부족으로 사람검토 강등 이력이 있다(같은 파일 25행). 따라서 서술 밀도가 아니라 **구조 자격 요건**으로 건다:
> 슬라이드가 `L-ct-definition` 이상의 레이아웃(카드행·다이어그램·비교)을 받으려면 초안 행에 다음 중 **2개 이상**이 출처 행번호와 함께 있어야 한다 — ① 대비쌍(나쁜예/좋은예·A/B) ② 구체적 앵커(숫자·실명·시나리오) ③ 인과절("왜냐하면"/"~하지 않으면") ④ 개념KB `PPT 소재:` 명시 시각. 2개 미만이면 카드grid+배너로 여백을 채우지 말고 `[콘텐츠 재작업 필요: 부족 요소 N개]`를 shard 주석에 남기고 `/콘텐츠`로 반려한다.
보완: `is_card2col_banner_pattern` 휴리스틱(카드류 ≥2 + `callout`류 배너)을 R-QC-09로 편입해 "카드+배너인데 본문 총량 임계 이하"를 자동 WARN.

## §G 사용자 지시와 다른 점
1. **카드 전면금지의 뉘앙스** — `week1_visual_benchmark.md` 반례가 "카드 반복이 죄가 아니라 항목 간 숨은 결정축을 형태가 지우는 게 죄"라 명시. 항목이 진짜 독립·병렬이면 카드 그리드 허용해야 함
2. **무대·리모컨 그림자 범위** — 슬라이드 콘텐츠가 아니라 뷰어 크롬이라 신규 규칙 대상인지 불명확, 사용자 확인 필요
3. **p13 결함 원인** — 레이아웃이 아니라 원본 스샷 종횡비 불일치. 자료(재크롭) 선행 없이는 레이아웃만 고쳐도 안 풀림
