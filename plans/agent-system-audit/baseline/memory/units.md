# MEMORY.md 소절 단위 전수 분해 (2026-10-08, 작업 트리 현재본 696줄 / 133,097바이트)

범례: 구성% = a상태 b열린과업 c사용자결정 d역사 e교훈규칙 f프로젝트지식 g포인터 (줄 수 기준 대략) · 분류 제안은 제안일 뿐 · [M]매 작업 [S]해당 영역 [H]역사 [X]삭제해도 손실 없음 · ONLY HERE = 정본(kit/guide·references·SKILL.md·AGENTS.md·skills·scripts·.githooks·tests·evals·과목 profile) grep 0건; "ONLY HERE*" = 비정본(plans·_dev·courses 이력)에만 사본이 있음

## 1. 단위 요약표

| ID | 제목 | 줄 | 바이트 | 구성 a/b/c/d/e/f/g | STILL OPEN | NOT CHECKED | 규칙수 | ONLY HERE (정본 0) | ONLY HERE* | 최근 날짜 | 표식 | 범위 | 분류 제안 |
|---|---|---|---:|---|---:|---:|---:|---:|---:|---|---|---|---|
| U01 | ## 운영 계약 | 5-15 | 1577 | 0/0/0/15/60/10/15 | 0 | 0 | 0 | 0 | 0 | 2026-08-03 | 없음 | 전 과목 공통 | 7-11 [X삭제가능] / 12-14 [H역사] |
| U02 | ## 절대 우선순위 | 16-19 | 165 | 0/0/0/0/0/0/100 | 0 | 0 | 0 | 0 | 0 | - | 없음 | 전 과목 공통 | [X삭제가능] |
| U03a | ## 반복 오답 → 정답 (1/2: 박스·이미지·capacity) | 20-39 | 3191 | 0/0/0/0/85/15/0 | 0 | 0 | 9 | 0 | 0 | 2026-07-26 | 없음 | 인프라(조립 규칙) / 전 과목 | [S덱조립] 일부 [X] |
| U03b | ## 반복 오답 → 정답 (2/2: 줄높이·중복·첫일치) | 40-59 | 4089 | 0/0/0/0/85/15/0 | 0 | 0 | 10 | 1 | 4 | 2026-08-01 | 없음 | 인프라(조립 규칙) / 전 과목 | [S덱조립] |
| U04 | ## 디자인 판단 | 61-69 | 1423 | 0/0/0/0/100/0/0 | 0 | 0 | 7 | 0 | 0 | - | 없음 | 전 과목 공통 | [S덱조립] 다수 [X] |
| U05 | ## 콘텐츠·학생 화면 | 71-80 | 1439 | 0/0/0/0/100/0/0 | 0 | 0 | 8 | 0 | 3 | 2026-07-31 | 없음 | 전 과목 공통 | [S덱조립] |
| U06 | ## 이미지·GUI | 82-89 | 1027 | 0/0/0/0/90/10/0 | 0 | 0 | 6 | 1 | 0 | - | 없음 | 전 과목 공통 | [S덱조립] |
| U07 | ## 텍스트 폭·폰트·여백 | 91-99 | 1363 | 0/0/0/0/100/0/0 | 0 | 0 | 7 | 1 | 3 | 2026-07-30 | 없음 | 전 과목 공통 | [S덱조립] |
| U08 | ## 브랜드·터미널·마무리 | 101-108 | 1148 | 0/0/0/0/100/0/0 | 0 | 0 | 6 | 1 | 1 | 2026-07-30 | 없음 | 바이브코딩 색채 · 일부 전 과목 | [S덱조립] |
| U09a | ## 브라우저 전수검증 (1/2: 절차·scale) | 110-121 | 2580 | 0/0/0/0/90/10/0 | 0 | 0 | 10 | 1 | 1 | 2026-07-26 | 없음 | 인프라(검증 절차) | [S검증] 다수 [X] |
| U09b | ## 브라우저 전수검증 (2/2: 사고·킷 결함·검출기) | 122-132 | 5173 | 0/0/0/10/75/15/0 | 0 | 0 | 11 | 1 | 0 | 2026-07-31 | 없음 | 인프라(검증 절차) | [S검증]/[H] |
| U10 | ## 파이프라인 상류 (리서치·콘텐츠) | 134-147 | 7410 | 0/0/0/10/65/25/0 | 0 | 0 | 12 | 2 | 4 | 2026-07-27 | 없음 | 전 과목(리서치·콘텐츠 단계) | [S리서치] |
| U11 | ## 미해결 (머리·내용 없음) | 149-150 | 14 | 0/0/0/0/0/0/0 | 0 | 0 | 0 | 0 | 0 | - | 없음 | — | [X삭제가능] |
| U12 | ### ▶ FRAME 길이별 조립(2·4·6시간) | 151-155 | 1333 | 40/20/15/0/10/0/15 | 4 | 1 | 1 | 0 | 1 | 2026-10-07 | ▶ | FRAME 과목(AI_에이전트_실습워크숍_4시간) 1주차 | [S FRAME] |
| U13 | ### ▶ FRAME 개편 1주차 전면 교체 | 157-163 | 3112 | 45/10/5/15/10/10/5 | 2 | 2 | 2 | 0 | 1 | 2026-10-03 | ▶ | FRAME 과목 1주차 | [S FRAME]/[H] |
| U14 | ### ▶ 새 과목 바이브코딩_온라인 | 165-174 | 4323 | 30/15/10/10/25/5/5 | 2 | 0 | 4 | 0 | 3 | 2026-09-19 | ▶ | 바이브코딩_온라인 과목 | [S 온라인] 174의 일반 교훈 2건은 [M]후보 |
| U15 | ### ▶ AC3 3차시 — 결과물 중심 재설계 (설계 확인 대기) | 176-178 | 795 | 30/25/20/0/0/15/10 | 0 | 1 | 0 | 0 | 0 | 2026-09-11 | ▶ | AI_코딩_에이전트_입문_3차시 3주차 | [H] (낡음) |
| U16 | ### ▶ AC3 2차시 — prd.md 복원 (병합 대기) | 180-185 | 1218 | 25/20/15/25/10/0/5 | 1 | 1 | 1 | 0 | 1 | 2026-09-11 | ▶ | AI_코딩_에이전트_입문_3차시 2주차 | [H]/[X] |
| U17 | ### ▶ 토큰 재발 방지 — P1 완료·P2~P4 안 함 | 187-194 | 1522 | 20/0/30/25/10/10/5 | 0 | 0 | 0 | 0 | 0 | 2026-09-11 | ▶ | 인프라(계측) | [S 계측] 189 사용자 결정은 [M]후보 |
| U18 | ### ▶ 다음 할 일 — 사용자 결정 2건 | 196-214 | 1917 | 20/10/40/10/0/10/10 | 2 | 0 | 1 | 0 | 1 | 2026-08-29 | ▶ | 인프라(게이트·테마 계약) | [M] 결정 대기분(201-207) / 209-214 [H] |
| U19 | ### ✅ 두 번째 테마 likelionSKU 등재 완료 | 216-236 | 2167 | 25/0/0/15/30/25/5 | 0 | 0 | 3 | 0 | 1 | 2026-08-29 | ✅ | 인프라(테마) / likelionSKU | [S 테마] 220 병합 대기는 낡음 |
| U20 | ### ⚠️ 게이트를 새로 쓰면 «내가 먼저 우회해 본다» | 238-253 | 1621 | 0/0/0/20/80/0/0 | 0 | 0 | 4 | 0 | 1 | 2026-08-29 | ⚠️ | 인프라(게이트 작성) | [M] (게이트 작성 시) |
| U21 | ### ⚠️ 「한 층·한 파일을 고쳤다」와 「규칙을 지켰다」는 다르다 | 255-267 | 1111 | 0/0/0/15/85/0/0 | 0 | 0 | 4 | 0 | 0 | 2026-08-29 | ⚠️ | 인프라(검증 규율) | [M] |
| U22 | ### ⚠️ 테마 적용은 «링크 한 줄»이다 | 269-281 | 1024 | 0/0/0/5/25/60/10 | 0 | 0 | 3 | 0 | 0 | 2026-08-29 | ⚠️ | 인프라(테마) | [X] 대부분 |
| U23 | ### ⚠️ 토큰 계약 개정 — 99 → 100 | 283-297 | 1073 | 0/0/0/10/20/70/0 | 0 | 0 | 3 | 0 | 0 | 2026-08-29 | ⚠️ | 인프라(테마) | [X] |
| U24 | ### ⚠️ 새 테마의 색 시스템 놓치기 쉬운 세 자리 | 299-313 | 1350 | 0/0/0/10/60/30/0 | 0 | 0 | 4 | 0 | 0 | 2026-08-29 | ⚠️ | 인프라(테마) | [X] 대부분 |
| U25 | ### ⚠️ 격리 스캔의 기준은 「상속되는가」다 | 315-326 | 1011 | 0/0/0/20/60/20/0 | 0 | 0 | 2 | 0 | 0 | 2026-08-29 | ⚠️ | 인프라(과목 격리) | [S 격리] |
| U26 | ### ✅ R-QC-14 위반 14건 해소 | 328-354 | 2570 | 0/0/0/35/45/20/0 | 0 | 0 | 4 | 0 | 2 | 2026-08-29 | ✅ | 인프라(CSS 린트) | [H] + 336·345·348 교훈 [M]후보 |
| U27 | ### ⚠️ 다과목 저장소가 된 뒤의 규율 | 356-366 | 1140 | 0/0/0/20/70/10/0 | 0 | 0 | 3 | 0 | 0 | 2026-08-29 | ⚠️ | 인프라(경로층) | [M] |
| U28 | ### ⚠️ .gitignore에 폴더명은 루트 앵커 | 368-373 | 467 | 0/0/0/30/70/0/0 | 0 | 0 | 1 | 0 | 1 | 2026-08-29 | ⚠️ | 인프라 | [M] (1줄 규칙) |
| U29 | ### 📌 문서 불일치 (고치지 않고 기록만) | 375-381 | 658 | 35/30/0/35/0/0/0 | 0 | 0 | 2 | 0 | 1 | - | 📌 | 인프라 | [X] 대부분 낡음 |
| U30 | ### 실험덱 처리 — 종결 | 383-395 | 1378 | 0/10/0/55/25/10/0 | 1 | 0 | 2 | 0 | 0 | 2026-08-23 | 없음 | 인프라 | [H] |
| U31 | ### ✅ 규칙 정본 모순·게이트 구멍 3건 — 전량 해소 | 397-426 | 3657 | 0/0/0/45/25/20/10 | 0 | 0 | 6 | 1 | 0 | 2026-08-23 | ✅ | 인프라 / 바이브코딩 | [H] |
| U32 | ### ⏸ R-BOXFILL-01 상자 채움 검출 6종 | 428-436 | 2473 | 15/25/0/20/25/15/0 | 2 | 0 | 4 | 1 | 0 | 2026-08-18 | ⏸ | 인프라(감사기) | [S 감사기] |
| U33 | ### ⏸ WARN → FAIL 승격 — 보류 | 438-446 | 1861 | 20/45/10/10/15/0/0 | 3 | 0 | 2 | 0 | 0 | 2026-08-18 | ⏸ | 인프라(게이트) | [M] (보류 사유·선행조건 4개) |
| U34 | ### ⏸ Codex 패리티 — 페이로드 스키마 | 448-453 | 893 | 30/20/0/0/0/45/5 | 1 | 0 | 1 | 0 | 0 | 2026-08-18 | ⏸ | 인프라(Codex) | [S Codex] |
| U35 | ### ✅ 렌더 측정 재현성 — 규명·해소 | 455-466 | 2883 | 0/10/0/40/25/25/0 | 1 | 0 | 4 | 0 | 0 | 2026-08-18 | ✅ | 인프라(감사기) | [H]; 461-462 [X] |
| U36 | ### ⏸ 훅 오탐 장부가 휘발된다 | 468-472 | 1049 | 30/30/0/30/10/0/0 | 1 | 0 | 2 | 0 | 0 | 2026-08-18 | ⏸ | 인프라(훅) | [M] (열린 판단 1건) |
| U37 | ### ⏸ 시스템 개선 계획 — 배치1~4 완료·이관만 | 474-482 | 2107 | 30/20/0/20/15/0/15 | 1 | 1 | 5 | 1 | 0 | 2026-08-18 | ⏸ | 인프라 / 바이브코딩 D-1 | [M] 478-479 [S] / 나머지 [H] |
| U38 | ### ⏸ 지침 생태계 리팩터링 — Gate 0 완료 | 484-501 | 4449 | 15/15/0/30/5/35/0 | 3 | 0 | 8 | 1 | 1 | 2026-08-18 | ⏸ | 인프라(Codex·훅) | [S Codex]/[H] |
| U39 | ### ✅ 세션 폴더 덱의 kit CSS 상대경로 | 503-514 | 2948 | 5/0/0/25/50/20/0 | 0 | 0 | 6 | 2 | 0 | 2026-08-03 | ✅ | 인프라(경로·검증) | [M] 505-514 교훈 / 나머지 [X] |
| U40a | ### ★ 2주차 현재 상태 (112장) — 현재 상태부 | 516-537 | 7253 | 30/10/10/25/15/10/0 | 1 | 2 | 9 | 2 | 3 | 2026-08-17 | ★ | 바이브코딩 2주차 | [S 바이브코딩2주차]/[H] |
| U40b | ### ★ 2주차 — 113장 시점 (2026-08-02 PART4↔5 스왑) | 538-569 | 7046 | 0/5/0/55/20/20/0 | 0 | 1 | 9 | 2 | 1 | 2026-08-03 | 없음 | 바이브코딩 2주차 | [H] |
| U41 | ### 2026-08-03 2주차 발표본 산출 — 재발 방지 | 571-593 | 8641 | 10/0/0/25/55/10/0 | 0 | 1 | 16 | 3 | 3 | 2026-08-04 | 없음 | 인프라(발표본) / 바이브코딩 2주차 | [M]/[S 발표본] |
| U42 | ### 2026-07-30 새로 얻은 재발 방지 | 595-602 | 2359 | 0/0/0/10/90/0/0 | 0 | 0 | 6 | 2 | 0 | 2026-07-30 | 없음 | 인프라(조립·측정) | [S 검증] |
| U43 | ### ★ 2026-07-29 확정 (A. 디자인 재현 방식) | 604-619 | 3702 | 0/5/10/25/45/15/0 | 0 | 0 | 6 | 0 | 0 | 2026-08-03 | ★ | 전 과목(kit 정책) | [S kit 정책] 608-612 [X] |
| U44 | ### ★ 2026-07-29 확정 (B. 초안 단계 폐기) | 621-639 | 3936 | 0/10/0/45/25/10/10 | 0 | 1 | 11 | 1 | 1 | 2026-08-03 | 없음 | 전 과목 파이프라인 | [H] + 630·633 교훈 [M]후보 |
| U45 | ### ★ 2026-07-29 확정 (C. 2주차 재설계 15장) | 641-649 | 2275 | 0/15/0/40/20/25/0 | 2 | 0 | 4 | 1 | 2 | 2026-08-03 | 없음 | 바이브코딩 2주차 | [H]; 648·649 열린 2건 [S] |
| U46 | ### ★ 2026-07-29 확정 (D. 그 밖의 미결) | 651-658 | 1833 | 0/15/0/10/60/15/0 | 0 | 1 | 4 | 1 | 0 | 2026-08-03 | 없음 | 전 과목 / 바이브코딩 프로필 | [M] 654·658 사용자 결정 / 657 교훈 |
| U47 | ### ★ 2026-07-29 확정 — 2주차 덱 구조 상수 | 660-667 | 2368 | 0/20/0/20/0/60/0 | 0 | 1 | 4 | 0 | 1 | 2026-07-30 | 없음 | 바이브코딩 2주차 | [S 바이브코딩2주차]/[H] |
| U48 | ### ★ 1주차 동결·발표 시스템(0~9단계) | 669-684 | 5978 | 0/5/0/25/35/35/0 | 0 | 1 | 10 | 2 | 1 | 2026-07-26 | 없음 | 바이브코딩 1주차 / 인프라(발표자 런타임) | [S 발표 시스템] |
| U49 | ### ★ 번호 미결 0~7 + AC3 제작 중단 (686-696) | 686-696 | 4040 | 0/80/0/10/0/0/10 | 0 | 7 | 8 | 0 | 0 | 2026-09-11 | 없음 | 바이브코딩 2주차 / 전 과목 | [H] 다수 낡음; 열린 항목은 NOT CHECKED |

(머리말 1-4줄 216B + 단위 합 132140B = 132356B / 파일 132401B)

## 2. 단위별 상세

### U01 ## 운영 계약 (L5-15, 1577B)
- 범위: 전 과목 공통 · 분류 제안(제안일 뿐): 7-11 [X삭제가능] / 12-14 [H역사] — 7-10은 AGENTS.md:46·40, SKILL.md:32·78에 동일 규칙 · 12-14는 2주차 실측 근거(R-FEEDBACK-01은 references/phases/08-검증.md:48에 있음)
- 중복 보관: DUPLICATED IN AGENTS.md:46,SKILL.md:32 (partial)

### U02 ## 절대 우선순위 (L16-19, 165B)
- 범위: 전 과목 공통 · 분류 제안(제안일 뿐): [X삭제가능] — SKILL.md:78 「④ 절대 금지 10항」 포인터뿐
- 중복 보관: DUPLICATED IN SKILL.md:78

### U03a ## 반복 오답 → 정답 (1/2: 박스·이미지·capacity) (L20-39, 3191B)
- 범위: 인프라(조립 규칙) / 전 과목 · 분류 제안(제안일 뿐): [S덱조립] 일부 [X] — 9쌍 중 22·24·26·28·32·36 은 references/phases/04-조립.md·SKILL.md에 있음. 34(가로를 키워라)·38(오버라이드 실측 사례)는 사례가 여기에 더 풍부
- 중복 보관: PARTIAL: references/phases/04-조립.md:47-56,80
- 규칙·교훈 문장:
  - L22 박스를 좁혀 강제 줄바꿈하지 않는다 · 폭 먼저 → PARTIAL(일부만 ALSO IN) references/phases/04-조립.md:122-124 (R-TEXT-02 줄바꿈 문맥 경계)
  - L24 글자 넘치면 18-20px로 줄이지 말고 구도 변경 · 22px 하한 → ALSO IN SKILL.md:85 (R-TYPE-01) · AGENTS.md:71
  - L26 정보 적은 장을 빈 카드·큰 여백으로 채우지 않는다 → ALSO IN references/phases/04-조립.md:80
  - L28 모든 장을 좌텍스트/우이미지·같은 카드 격자 금지 → ALSO IN SKILL.md R-LAYOUT-01(:92) · kit/layouts/by-shape.md:20
  - L30 카탈로그는 후보군 — 억지로 맞추지 않는다 → PARTIAL(일부만 ALSO IN) kit/layouts/by-shape.md:20 (카탈로그에 없다는 것이…)
  - L32 이미지 확대는 겹침 0 우선 → ALSO IN SKILL.md:90 (R-IMG-04)
  - L34 이미지 작다→figure 높이가 아니라 가로를 키운다(object-fit contain 레터박스) → PARTIAL(일부만 ALSO IN) kit/CHANGELOG.md:5 · references/phases/04-조립.md:51-56 (가로를 키워라는 ONLY)
  - L36 figure overflow:hidden + img height 명시, 두 rect 높이 대조 → ALSO IN references/phases/04-조립.md:54
  - L38 capacity/density_note를 토큰 기본값으로 산정 금지 — 오버라이드 확인·실측 → PARTIAL(일부만 ALSO IN) kit/layouts/families/top-down.md:328 · vertical-flow.md:212 (override 언급)

### U03b ## 반복 오답 → 정답 (2/2: 줄높이·중복·첫일치) (L40-59, 4089B)
- 범위: 인프라(조립 규칙) / 전 과목 · 분류 제안(제안일 뿐): [S덱조립] — 50(line box)·52·54·56·58은 정본에 없음(ONLY HERE)
- 중복 보관: PARTIAL: SKILL.md:90,86 · 04-조립.md:111
- 규칙·교훈 문장:
  - L40 overflow:hidden으로 숨기고 통과 금지 — scrollWidth 등 측정 → ALSO IN SKILL.md:90
  - L42 박스 안 하단 공백 금지 — space-between/evenly → ALSO IN references/phases/04-조립.md:111-115 (R-BOX-01)
  - L44 콘텐츠 하단 상한 666px · 페이지번호 띠 침범 금지 → ALSO IN SKILL.md:86 (R-TYPE-03)
  - L46 아젠다 N<=6은 1열 · an-2col은 7개 이상 탈출구 → ALSO IN kit/starter/deck-template.html:117 · kit/guide/토큰-치트시트.md:231 · evals/evals.json:22
  - L48 보이는 페이지 번호로 CSS 지정 금지 · data-slide ID → ALSO IN references/phases/04-조립.md:12-16 (R-SLIDE-ID-01)
  - L50 줄 높이는 line box를 소유한 블록이 정한다(inline 요소 line-height 무효) → ONLY HERE*(정본 없음·비정본 사본만) _dev/설계기록/덱-조건-전수목록… 외 정본 없음
  - L52 같은 프롬프트는 입력하는 장·회상하는 장 중복 — grep으로 위치 센다 → ONLY HERE
  - L54 광역 CSS override 금지 — data-slide/전용 클래스로 범위 잠금 → ONLY HERE*(정본 없음·비정본 사본만) _dev/설계기록/덱-조건-전수목록_및_규칙누락감사.html:285 (비정본)
  - L56 블록 이동 시 파일 첫 일치 금지 — data-slide 범위를 먼저 자른다 → ONLY HERE*(정본 없음·비정본 사본만) courses/바이브코딩/…/2주차_PART45_스왑_실행계획.md:108 (역사)
  - L58 원본에서 회수한 블록은 이번 세션 고친 문구를 되돌린다 — 치환 목록 재확인 → ONLY HERE*(정본 없음·비정본 사본만) plans/바이브코딩_온라인/재개_인계.md 등 사례 언급만

### U04 ## 디자인 판단 (L61-69, 1423B)
- 범위: 전 과목 공통 · 분류 제안(제안일 뿐): [S덱조립] 다수 [X] — 63-69 대부분 SKILL.md R-LAYOUT·04-조립.md R-DENS·토큰-치트시트에 있음
- 중복 보관: PARTIAL: SKILL.md:135 · 04-조립.md:70-88 · 토큰-치트시트.md:180-181
- 규칙·교훈 문장:
  - L63 조립 순서: 정보 모양 분류→역인덱스→레이아웃·element→직전 장과 비교 → ALSO IN SKILL.md:102 · AGENTS.md:96 · kit/layouts/by-shape.md
  - L64 좌우분할·카드 반복 금지 · 같은 패밀리 연속 금지 → ALSO IN kit/guide/카탈로그-규격.md:179 · kit/layouts/by-shape.md:20
  - L65 박스 크기는 정보량에 맞춘다 → ALSO IN kit/guide/토큰-치트시트.md:180
  - L66 색 규칙 포인터(R-COLOR) → ALSO IN kit/guide/디자인시스템.md:21 (자체가 포인터)
  - L67 큰 이미지 장: 안전영역·간격 먼저 → PARTIAL(일부만 ALSO IN) kit/guide/토큰-치트시트.md:200,206 (안전영역)
  - L68 게이트 임계를 합격 덱의 하위 분위수에서 뽑지 마라 → ALSO IN SKILL.md:135 · references/phases/04-조립.md:87
  - L69 밀도 요구를 박스 확대로 처리 금지 → ALSO IN kit/guide/토큰-치트시트.md:181 · 04-조립.md:70-88 (R-DENS-03)

### U05 ## 콘텐츠·학생 화면 (L71-80, 1439B)
- 범위: 전 과목 공통 · 분류 제안(제안일 뿐): [S덱조립] — 75·79·80은 SKILL.md/verify_deck_quality에 있음; 73·76·77·78은 정본에 없음(_dev 감사목록에만)
- 중복 보관: PARTIAL: SKILL.md:88 · kit/guide/문체-원칙.md:72
- 규칙·교훈 문장:
  - L73 내부 분류명·제작 메타·검수 용어 학생 화면 노출 금지 → ALSO IN scripts/verify_deck_quality.py (내부 라벨 ALWAYS_FAIL) · SKILL.md:133
  - L74 일반 슬라이드 3–6 정보 단위 → ALSO IN SKILL.md:135 (R-DENS-01) · kit/guide/교육원칙-요약.md:18
  - L75 학생 덱에 hint-reveal·강사 힌트 접힘 금지 → ALSO IN SKILL.md:88 (R-ICON-01)
  - L76 가짜 버튼·동작 안 하는 토글 금지 → ONLY HERE*(정본 없음·비정본 사본만) _dev/설계기록/덱-조건-전수목록…:301 (비정본)
  - L77 완료 기준은 무엇이 열리고 무엇을 확인하면 끝인지 → ONLY HERE*(정본 없음·비정본 사본만) courses/AI_코딩_에이전트_입문_3차시/커리큘럼_기준안.md:65 (과목 한정)
  - L78 제공하지 않은 경력·연락처·링크 만들지 않는다 → ONLY HERE*(정본 없음·비정본 사본만) _dev/설계기록/덱-조건-전수목록…:303 (비정본)
  - L79 제목의 비유를 정규식으로 검출하지 마라(폐기) → ALSO IN kit/guide/문체-원칙.md:72
  - L80 용어 정의 누락을 문자열 표지로 재시도 금지 → ALSO IN scripts/verify_deck_quality.py:225

### U06 ## 이미지·GUI (L82-89, 1027B)
- 범위: 전 과목 공통 · 분류 제안(제안일 뿐): [S덱조립] — 84-88은 03-레이아웃선택.md:125·이미지-디렉션-프롬프트.md:168 부분 중복; 89는 ONLY HERE
- 중복 보관: PARTIAL: references/phases/03-레이아웃선택.md:125
- 규칙·교훈 문장:
  - L84 실제 UI 조작은 실제 캡처 → ALSO IN references/phases/03-레이아웃선택.md:125
  - L85 실제 캡처는 contain·crop 금지·개인정보 가림 → PARTIAL(일부만 ALSO IN) kit/styles/patterns.css:279 · kit/CHANGELOG.md:14
  - L86 CSS GUI는 개념 설명에만 → PARTIAL(일부만 ALSO IN) references/phases/03-레이아웃선택.md:125
  - L87 설명 이미지는 관계·원리를 직접 설명 → PARTIAL(일부만 ALSO IN) SKILL.md:7(description)
  - L88 이미지 투명 여백 때문에 작아 보이면 경계 확인 → ALSO IN references/이미지-디렉션-프롬프트.md:168
  - L89 figure 안 img height:100%+캡션 이탈 — min-height:0·grid row → ONLY HERE

### U07 ## 텍스트 폭·폰트·여백 (L91-99, 1363B)
- 범위: 전 과목 공통 · 분류 제안(제안일 뿐): [S덱조립] — 93·94·96·97은 정본에 없음; 95·98·99는 04-조립.md·조립-리듬·검증-명령-지도에 있음
- 중복 보관: PARTIAL: 04-조립.md:122-124 · 검증-명령-지도.md:178
- 규칙·교훈 문장:
  - L93 한글 폭 = 글자 수×폰트 px 사전 계산 → ONLY HERE*(정본 없음·비정본 사본만) plans/typography-grid-system/PLAN.md:536 (비정본)
  - L94 본문 22px 줄높이 1.5–1.7 세로 예산 → ONLY HERE
  - L95 수동 <br>은 구·절 경계에서만 → ALSO IN references/phases/04-조립.md:124 · kit/starter/deck-template.html:117
  - L96 <p>에 .s-body 붙일 때 UA margin 재설정 → ONLY HERE*(정본 없음·비정본 사본만) _dev/설계기록/덱-조건-전수목록…:254
  - L97 제목-본문 등 사이 눈에 보이는 간격 → ONLY HERE*(정본 없음·비정본 사본만) _dev/설계기록/덱-조건-전수목록…:273
  - L98 원형 번호 배지와 텍스트 수직 중앙 정렬 → ALSO IN references/조립-리듬-불변요소.md (AGENTS.md:100 지목)
  - L99 어절 중간 줄바꿈은 조립 후 전수로 잡는다 → ALSO IN references/검증-명령-지도.md:178 · scripts/measure_render.js:232 (wordBreaks)

### U08 ## 브랜드·터미널·마무리 (L101-108, 1148B)
- 범위: 바이브코딩 색채 · 일부 전 과목 · 분류 제안(제안일 뿐): [S덱조립] — 103(VIBECODING 브랜드)은 과목 종속인데 공통 절에 있음 · 106·107은 정본에 없음
- 중복 보관: PARTIAL: 디자인시스템.md:119 · verify_deck_quality.py:420
- 규칙·교훈 문장:
  - L103 본문 .s-head에 .s-logo + VIBECODING 브랜드 → PARTIAL(일부만 ALSO IN) kit/starter/deck-template.html:86 · courses/바이브코딩/profile.md:100
  - L104 표지 터미널 흰 배경 → ALSO IN kit/guide/디자인시스템.md:119
  - L105 검정 터미널 ink 배경 · 프롬프트 민트 → ALSO IN kit/styles/patterns.css:452 · 디자인시스템.md
  - L106 THANK YOU는 덱에서 가장 큰 볼드 타이포 → ONLY HERE*(정본 없음·비정본 사본만) _dev/설계기록/덱-조건-전수목록…:221 (비정본)
  - L107 recap·마무리 헤더 브랜드 대비 → ONLY HERE
  - L108 슬라이드 하단 마무리 한 줄 습관 금지(callout·compare-foot·ch-note) → ALSO IN scripts/verify_deck_quality.py:420 (R-QC-15) · tests/test_quality_gates.py:492

### U09a ## 브라우저 전수검증 (1/2: 절차·scale) (L110-121, 2580B)
- 범위: 인프라(검증 절차) · 분류 제안(제안일 뿐): [S검증] 다수 [X] — 112-119는 references/phases/08-검증.md R-VERIFY-01a~e에 있음; 114·116·121은 ONLY HERE
- 중복 보관: DUPLICATED IN references/phases/08-검증.md:10-65
- 규칙·교훈 문장:
  - L112 조립 후 전체 장 1280×720 순회 + 인앱 크기 → ALSO IN references/phases/08-검증.md:10-12
  - L113 측정 항목 목록(이탈·교차·scroll·잘림·crop·캡션·콘솔) → ALSO IN references/phases/08-검증.md:12
  - L114 overlap 오탐 있어도 전체 감사 생략 금지 → ONLY HERE*(정본 없음·비정본 사본만) _dev/설계기록/덱-조건-전수목록…:349
  - L115 CSS 캐시 버전 갱신 · file:// 아닌 로컬 HTTP → ALSO IN references/phases/08-검증.md:12 · .agents/README.md:19
  - L116 전체 검사·대표 스크린샷 전엔 완료 보고 금지 → PARTIAL(일부만 ALSO IN) references/phases/08-검증.md:12 (완료 전 모든 슬라이드)
  - L117 getBoundingClientRect를 --scale로 나눠 환산 → ALSO IN references/phases/08-검증.md:37-39 (R-VERIFY-01c)
  - L118 래퍼 제외·말단 요소만 측정 → ALSO IN references/phases/08-검증.md:41-43 (R-VERIFY-01d)
  - L119 회귀 여부는 기준선과 대조해서만(git show <커밋>:덱) → ALSO IN references/phases/08-검증.md:63-65 (R-VERIFY-01e)
  - L120 kit_alpha_exempt 해소 (8c07f2f) → ALSO IN scripts/verify_deck.py:748 (kit_alpha_exempt 구현)
  - L121 인앱 --scale 0 → 강제 1 후 측정 → ONLY HERE (scale=0 거짓 보고 — 정본 grep 0건)

### U09b ## 브라우저 전수검증 (2/2: 사고·킷 결함·검출기) (L122-132, 5173B)
- 범위: 인프라(검증 절차) · 분류 제안(제안일 뿐): [S검증]/[H] — 127·129·130·131·132는 검증-명령-지도 §8·scripts에 있음; 122(킷 결함 현존)·123은 현존 결함 기록
- 중복 보관: PARTIAL: 검증-명령-지도.md:176-206 · scripts/audit_render.js:431
- 규칙·교훈 문장:
  - L122 킷 결함 2건(min-height:0·666 초과 값) 환류 대상 → ONLY HERE (결함은 kit CSS에 현존: patterns.css:16·228, deck.css:557·655)
  - L123 킷 컴포넌트 기본 폰트 19~21px — 본문은 22px 하한 → PARTIAL(일부만 ALSO IN) kit/guide/토큰-치트시트.md:88 · kit CSS 값 자체
  - L124 초안 제목이 화면 텍스트에 있는지 기계 대조 → ALSO IN references/검증-명령-지도.md:32,49 · scripts/check_title_survival.py
  - L125 !important 요소를 인라인 토글하면 측정 0 — is-active → PARTIAL(일부만 ALSO IN) kit/styles/deck.css:213 · scripts(is-active 사용)
  - L126 슬라이드 수 불일치 → shard 태그 균형 의심 → PARTIAL(일부만 ALSO IN) scripts/verify_deck.py:791 (코드)
  - L127 종료코드 전부 통과 + 화면 붕괴 — 게이트 통과를 품질 근거로 쓰지 마라 → ALSO IN references/검증-명령-지도.md:176-178 (§8.1)
  - L128 경보를 해석으로 끄지 마라(R-QC-08) → ALSO IN scripts/verify_deck_quality.py:846 (주석)
  - L129 규칙 문장을 바꾸면 집행 CSS/스크립트도 같은 커밋에서 → ALSO IN references/검증-명령-지도.md:202-206 (§8.4) · AGENTS.md:106
  - L130 CSS는 익명 격자 아이템을 선택 못 함 → span.desc (R-QC-19) → ALSO IN scripts/verify_deck_quality.py:871 (R-QC-19) · 검증-명령-지도.md:178
  - L131 검출기 상한 조건이 최악 사례를 통과시킨다(by>666&&by<720) → PARTIAL(일부만 ALSO IN) scripts/audit_render.js:431 (코드; 교훈 문장은 없음)
  - L132 빈 .asset-slot은 연파랑 점선 상자 — R-QC-18 → ALSO IN scripts/verify_deck_quality.py (R-QC-18) · kit/guide/테마-계약.md:45

### U10 ## 파이프라인 상류 (리서치·콘텐츠) (L134-147, 7410B)
- 범위: 전 과목(리서치·콘텐츠 단계) · 분류 제안(제안일 뿐): [S리서치] — 136-140·147은 SKILL.md·skills/리서치·02-슬라이드맵.md에 있음; 141-146은 ONLY HERE
- 중복 보관: PARTIAL: SKILL.md:24-26 · skills/리서치/SKILL.md:35,259 · references/phases/02-슬라이드맵.md:34-37
- 규칙·교훈 문장:
  - L136 사실 정본은 개념KB 하나 · 결과.md는 포인터 · 원문은 출처레지스트리 → ALSO IN SKILL.md:24-26 · skills/리서치/SKILL.md
  - L137 개념KB는 통째로 읽지 않는다 · 청크 인덱스·grep → ALSO IN SKILL.md:26 · skills/README.md:36
  - L138 넓게 조사 = 관점의 폭(G8)+개념 목록 폭(G9) · G9는 강사 답변용 → ALSO IN skills/검토/SKILL.md:71,121 · evals/team-skills-eval.json:28
  - L139 품질 게이트에 금지만 적으면 회피 — 해야 할 것을 함께 → ALSO IN skills/리서치/SKILL.md:35
  - L140 조사 산출물 세대 누적 금지 → 탐색-아카이브 → ALSO IN AGENTS.md:34 · skills/리서치/SKILL.md:259
  - L141 Workflow args는 JSON 객체 — 문자열이면 undefined → ONLY HERE
  - L142 인앱 브라우저는 file:// 보안 제약을 재현 못 함 → 부분검증 강등 → ONLY HERE*(정본 없음·비정본 사본만) tests/fixtures/…/2주차_초안.md:150 (픽스처)
  - L143 외부 그래프는 원 논문이 숫자로 공개한 지점만 그린다 → ONLY HERE*(정본 없음·비정본 사본만) courses/AI_코딩_에이전트_입문_3차시/커리큘럼_기준안.md:71 (사례 언급)
  - L144 같은 논문 조건 겹치는 Figure — 수치 URL과 개념 URL 분리 → ONLY HERE
  - L145 프롬프트 기법 가르칠 땐 검증된 것/안 된 것 슬라이드에 남긴다 → ONLY HERE*(정본 없음·비정본 사본만) FRAME·바이브코딩 초안에 적용 사례만
  - L146 출처 도메인 편중 셀 때 grep -c 금지 — 표 URL 열만 → ONLY HERE*(정본 없음·비정본 사본만) courses/AI_코딩_에이전트_입문_3차시/제작관리/상태장부.md:25
  - L147 2주차 저밀도 최초 결함은 계획 단계 CORE 얕게 · 렌더 결백(R-PLAN-01/02·R-DENS-02) → ALSO IN references/phases/02-슬라이드맵.md:34-37 · SKILL.md:135

### U11 ## 미해결 (머리·내용 없음) (L149-150, 14B)
- 범위: — · 분류 제안(제안일 뿐): [X삭제가능] — 헤더 2줄뿐
- 중복 보관: —

### U12 ### ▶ FRAME 길이별 조립(2·4·6시간) (L151-155, 1333B)
- 범위: FRAME 과목(AI_에이전트_실습워크숍_4시간) 1주차 · 분류 제안(제안일 뿐): [S FRAME] — 상태·결정·남은 일·함정이 plans/FRAME-길이별-조립/재개_인계.md에 더 자세히 있음
- 중복 보관: DUPLICATED IN plans/FRAME-길이별-조립/재개_인계.md §1·§3·§4·§8 (+PROGRESS.md)
- 열린 과업 서술 항목:
  - L151 FRAME 축제 과제 · 6시간 트랙 · 영수증 가계부 실습 미제작 → **STILL OPEN** (courses/.../강의덱.초안/variants/에 6h.txt 없음(2h·4h만); 재개_인계.md §4 P5·P6)
  - L151 FRAME 4시간 덱 변경(119→123장) 미커밋 → **STILL OPEN** (git status: FRAME 과목 M 143건; 마지막 FRAME 커밋 a979b42(111장))
  - L155 FRAME 러너 4h·2h FAIL(정적 4·품질 1·렌더) → **STILL OPEN** (재개_인계.md §1 「러너는 FAIL」(이번에 재실행하지 않음 → 문서 근거))
  - L155 사용자 답 대기: Codex 실행 · 영수증 이미지 · 블록 1 시간 → **STILL OPEN** (재개_인계.md §3 (사용자만 가능))
  - L155 회귀를 CREATE_SLIDES_COURSE 켠 채 돌리면 4건 ERROR → **NOT CHECKED** (재현하지 않음)
- 대기 중 사용자 결정 / 결정 서술:
  - L155 Codex 실행 결과 · 영수증 이미지 10장 · 블록 1(57분) 시간 확인 (재개_인계 §3)
  - L151 (2026-10-06 결정 기록) 2시간 배제 · 메인 과제 허브 · 검사기 판정 보류 — 결정 완료, 대기 아님
- 규칙·교훈 문장:
  - L155 CREATE_SLIDES_COURSE를 켠 채 회귀를 돌리면 4건 ERROR — 변수 없이 → ONLY HERE*(정본 없음·비정본 사본만) plans/FRAME-길이별-조립/재개_인계.md §8, PROGRESS.md

### U13 ### ▶ FRAME 개편 1주차 전면 교체 (L157-163, 3112B)
- 범위: FRAME 과목 1주차 · 분류 제안(제안일 뿐): [S FRAME]/[H] — 84장 상태는 낡음(99→111→123장); 결정 D1~D45는 plans/FRAME-개편/PLAN·PROGRESS에 있음
- 중복 보관: DUPLICATED IN plans/FRAME-개편/PLAN.md,PROGRESS.md; plans/FRAME-길이별-조립/재개_인계.md
- 열린 과업 서술 항목:
  - L157 감사 신호 정리 · 최종 조립 · 전수 검증 · Phase F → **NOT CHECKED** (최종 조립은 DONE(59fd6c2·1b96d17·a979b42); 감사 신호 정리·Phase F는 PROGRESS.md 마지막 갱신 10-01 이후 기록 없음)
  - L159 G1b 제출 → GR(사용자 리허설) → Phase E 조립 → **SUPERSEDED** (조립은 99→123장으로 실행됨(커밋 3개); GR 수행 여부는 NOT CHECKED)
  - L159 profile §3-G 장수 갱신 → **NOT CHECKED** (재개_인계 §4 P7: profile.md 미손; git status는 profile.md M — 상충)
  - L159 콘텐츠 리뷰 HTML 생성 → **DONE IN REPO** (courses/AI_에이전트_실습워크숍_4시간/sessions/1주차/1주차_콘텐츠_리뷰.html 존재)
  - L161 러너의 보고 신선도 · 렌더 증거 · WARN 래칫 FAIL 미해결 → **STILL OPEN** (재개_인계 §1 러너 FAIL)
  - L161 build_release.py는 verify_deck FAIL 4건으로, inline_deck --offline은 D2Coding CDN 링크로 실패(기존 배포본 삭제) → **STILL OPEN** (재개_인계 §1 4차 갱신: build_release는 D2Coding 링크에서 멈춤; build_presenter.py가 우회)
  - L163 G1(초안 검토) 전에는 덱을 조립하지 않는다 → **SUPERSEDED** (덱 조립 완료(커밋 3개))
- 규칙·교훈 문장:
  - L163 아쿠아 #7DE0EC 흰 배경 글자 금지(1.4:1) 면 전용 → ALSO IN kit/themes/frame/tokens.css:15,29 · courses/AI_에이전트_실습워크숍_4시간/brand/README.md:9
  - L161 build_release 실패하면 기존 배포본을 지운다 · D2Coding CDN → ONLY HERE*(정본 없음·비정본 사본만) plans/FRAME-길이별-조립/재개_인계.md §1

### U14 ### ▶ 새 과목 바이브코딩_온라인 (L165-174, 4323B)
- 범위: 바이브코딩_온라인 과목 · 분류 제안(제안일 뿐): [S 온라인] 174의 일반 교훈 2건은 [M]후보 — 상태·결정은 plans/바이브코딩_온라인/재개_인계.md·PLAN.md에 있음; 174의 cssRules·revision.css 캐시 교훈은 인계에도 있으나 일반 규칙으로는 정본에 없음
- 중복 보관: DUPLICATED IN plans/바이브코딩_온라인/재개_인계.md,PLAN.md,1차시-수정1·2-PLAN.md (rules 167,174: partially)
- 존재하지 않는 참조: tmp/vco-2주차/ (gitignore된 tmp — 부재)
- 열린 과업 서술 항목:
  - L165 2차시 피드백·캡처 대기(사용자) → **STILL OPEN** (courses/바이브코딩_온라인 마지막 커밋 0592309(9/19); 이후 변경 없음)
  - L174 오전·오후 덱 사용자 캡처 일괄 교체 → G2 → 배포본 → **STILL OPEN** (러너 잔여 R-QC-08 = 캡처 대기(제목 L165); 이후 커밋 없음)
  - L174 푸시는 작업 종료 후 → **DONE IN REPO** (acd0330·0592309 ∈ origin/main; main..origin 차이 0)
  - L174 오전 덱 90장·캡처 14슬롯(K2~K10·K15) 서술 → **SUPERSEDED** (제목 L165와 courses/바이브코딩_온라인/sessions/1주차/강의덱.html = 81 section)
- 대기 중 사용자 결정 / 결정 서술:
  - L165 2차시 피드백·캡처(사용자 제공)
- 규칙·교훈 문장:
  - L167 감사기 우회 금지(lowFill 안쪽 여백) — 화면 변화 없음이면 우회 의심 · waiver → ONLY HERE*(정본 없음·비정본 사본만) plans/바이브코딩_온라인/재개_인계.md · PLAN.md
  - L174 revision.css 링크라 CSS만 고치면 sha 불변·옛 CSS 캐시 — cssRules 대조 → ONLY HERE*(정본 없음·비정본 사본만) plans/바이브코딩_온라인/재개_인계.md · 1차시-수정1/2-PLAN.md
  - L174 CSS 기계 편집 시 브라우저 cssRules.length 전후 대조(:is 쉼표 절단) → ONLY HERE*(정본 없음·비정본 사본만) plans/바이브코딩_온라인/1차시-수정1-PLAN.md (cssRules)
  - L174 과목 전용 sessions/_verify를 만든다(없으면 루트 _verify로 해석) → ALSO IN sessions/README.md:10-14

### U15 ### ▶ AC3 3차시 — 결과물 중심 재설계 (설계 확인 대기) (L176-178, 795B)
- 범위: AI_코딩_에이전트_입문_3차시 3주차 · 분류 제안(제안일 뿐): [H] (낡음) — 본문이 「덱·초안 미착수」인데 repo는 83장 조립 완료(eb588c1, 9/12)
- 중복 보관: DUPLICATED IN plans/3차시-결과물중심-재설계/PLAN.md,EXECUTION.md
- 열린 과업 서술 항목:
  - L178 3차시 결과물 중심 재설계: 덱·초안·실습예제 미착수, 사용자 확인 뒤 S1부터 → **DONE IN REPO** (ad240c7 · 132ebfc · bc3eefc · eb588c1(9/12 「83장·렌더 결함 0·러너 PASS」) ∈ main; 3주차 강의덱 83 section)
  - L178 열린 결정 O-01~O-04 → **NOT CHECKED** (plans/3차시-결과물중심-재설계/PLAN.md 미대조)
- 대기 중 사용자 결정 / 결정 서술:
  - L178 3차시 설계 사용자 확인(S1 착수) — 이후 실행되어 낡음

### U16 ### ▶ AC3 2차시 — prd.md 복원 (병합 대기) (L180-185, 1218B)
- 범위: AI_코딩_에이전트_입문_3차시 2주차 · 분류 제안(제안일 뿐): [H]/[X] — 브랜치는 병합·push 끝남; 잔여 1건(죽은 CSS 1줄)만 현존
- 중복 보관: DUPLICATED IN plans/2차시-prd-복원/{PLAN,PROGRESS,합격기준}.md
- 열린 과업 서술 항목:
  - L182 feat/ac3-w2-prd-reorder main 병합·push 사용자 판단 대기 → **DONE IN REPO** (git rev-list main..브랜치 = 0 · tip eb588c1 ∈ origin/main)
  - L184 shell.html:311 N-16 전용 죽은 CSS 1줄 → **STILL OPEN** (.../2주차/강의덱.초안/shell.html:311 존재; part-*.html에 data-slide="N-16" 0건)
  - L184 C3-N2 새 제목과 하단 결론 문장 동일 뜻(삭제 검토) → **NOT CHECKED** (part-04.html:158-164에 C3-N2 존재, 하단 문장 미확인)
  - L184 커리큘럼 2차시 실습 6(기사 검증) 전담 장 없음 → **SUPERSEDED** (사용자 결정으로 수용(본문 명시))
- 대기 중 사용자 결정 / 결정 서술:
  - L182 ac3 브랜치 병합·push 판단 — 이미 병합됨
- 규칙·교훈 문장:
  - L185 인앱 브라우저 해시만 바꾸면 슬라이드 안 바뀜 → hash+reload → ONLY HERE*(정본 없음·비정본 사본만) plans/2차시-prd-복원/PROGRESS.md 등

### U17 ### ▶ 토큰 재발 방지 — P1 완료·P2~P4 안 함 (L187-194, 1522B)
- 범위: 인프라(계측) · 분류 제안(제안일 뿐): [S 계측] 189 사용자 결정은 [M]후보 — 근거·원인 A~H는 _dev/설계기록/토큰감사-2026-09-11.md
- 중복 보관: DUPLICATED IN _dev/설계기록/토큰감사-2026-09-11.md
- 열린 과업 서술 항목:
  - L189 P2·P3·P4 및 AC3 미완 후속은 재개하지 않는다 → **SUPERSEDED** (사용자 결정(2026-09-11) 자체가 종결 선언)
  - L192 P1 커밋은 사용자 요청 시 → **DONE IN REPO** (제목·커밋 88414d3 ∈ main (제목과 모순))
  - L193 과거 --tool-audit PASS 재감사 여부 사용자 판단 → **SUPERSEDED** (L189 결정이 «재개하지 않음»)
- 대기 중 사용자 결정 / 결정 서술:
  - L193 과거 --tool-audit 재감사 여부 (L189 결정으로 종결)

### U18 ### ▶ 다음 할 일 — 사용자 결정 2건 (L196-214, 1917B)
- 범위: 인프라(게이트·테마 계약) · 분류 제안(제안일 뿐): [M] 결정 대기분(201-207) / 209-214 [H] — 결정 ①②의 선택지는 plans/gate-input-hardening/PROGRESS.md 「사용자 판정 필요」에 있음(대기 사실 자체는 여기가 정본 위치)
- 중복 보관: DUPLICATED IN plans/gate-input-hardening/{PLAN,PROGRESS}.md
- 열린 과업 서술 항목:
  - L201 결정 ①: verify_draft_quality 3주차 R-QD-04 «미판정 WARN» 변경 수용(집계 불변과 양립 불가) → **STILL OPEN** (plans/gate-input-hardening/PROGRESS.md 끝이 「사용자 결정」에서 멈춤; 이후 verify_draft_quality 변경 커밋 f2831cd뿐)
  - L206 결정 ②: 뮤테이션 매트릭스 회귀 승격(조건부 권고) → **STILL OPEN** (tests/에 뮤테이션 매트릭스 모듈 없음(grep 0); PROGRESS.md 「실행하지 않고 여기서 멈춘다」)
- 대기 중 사용자 결정 / 결정 서술:
  - L201 결정 ① R-QD-04 미판정 WARN 변경 수용 여부 (선택지 4개)
  - L206 결정 ② 뮤테이션 매트릭스 회귀 승격 여부(권고: 조건부 승격)
- 규칙·교훈 문장:
  - L204 엄격한 집계 불변과 미탐 수정은 원리적으로 양립 불가 → ONLY HERE*(정본 없음·비정본 사본만) plans/gate-input-hardening/PROGRESS.md

### U19 ### ✅ 두 번째 테마 likelionSKU 등재 완료 (L216-236, 2167B)
- 범위: 인프라(테마) / likelionSKU · 분류 제안(제안일 뿐): [S 테마] 220 병합 대기는 낡음 — 브랜치는 병합됨; 233·236 교훈은 plans/likelionSKU-theme/RESULTS.md에 있으나 일반 규칙으론 ONLY HERE
- 중복 보관: DUPLICATED IN plans/likelionSKU-theme/{PLAN,RESULTS}.md; kit/guide/테마-계약.md
- 열린 과업 서술 항목:
  - L220 feat/likelionsku-theme main 병합·push 사용자 승인 대기 → **DONE IN REPO** (브랜치 ahead 0 · tip 3f31745 ∈ origin/main; kit/themes/likelionSKU/ 존재)
- 대기 중 사용자 결정 / 결정 서술:
  - L220 likelionsku 브랜치 병합·push 승인 — 이미 병합됨
- 규칙·교훈 문장:
  - L229 새 테마 대비 파생값(--on-coral)은 다시 계산 → ALSO IN kit/themes/likelionSKU/tokens.css:21 · SKILL.md:83 · 디자인시스템.md:16
  - L233 클래스 없는 <p>는 브라우저 기본 16px — 정적 PASS≠화면 안전 → PARTIAL(일부만 ALSO IN) scripts/verify_deck_quality.py:871 (R-QC-19: 클래스 없는 텍스트)
  - L236 표는 viz-* 표식 없으면 시각자료로 세지 않는다(R-QC-08) → ONLY HERE*(정본 없음·비정본 사본만) plans/likelionSKU-theme/RESULTS.md · plans/2차시-prd-복원/합격기준.md

### U20 ### ⚠️ 게이트를 새로 쓰면 «내가 먼저 우회해 본다» (L238-253, 1621B)
- 범위: 인프라(게이트 작성) · 분류 제안(제안일 뿐): [M] (게이트 작성 시) — 240은 verify_deck.py:2037 주석에, 251은 테마-계약.md에 일부; 248·252 규율은 ONLY HERE
- 중복 보관: PARTIAL: scripts/verify_deck.py:2037 · 테마-계약.md:3
- 규칙·교훈 문장:
  - L240 새 게이트는 내가 먼저 우회해 본다(순서·주석·인라인·비활성·상위 셀렉터) → ALSO IN scripts/verify_deck.py:2037 (6가지 우회 목록 주석)
  - L248 문서에 적은 게이트 거동은 한 줄이라도 실행해 확인 → ONLY HERE*(정본 없음·비정본 사본만) _dev/…/R12-자체점검.md (무관 언급)
  - L251 자기 게이트에도 뮤테이션을 건다 → PARTIAL(일부만 ALSO IN) kit/guide/테마-계약.md:3 (뮤테이션 근거)
  - L252 규모가 크면 적대적 서브에이전트를 붙이는 값 → PARTIAL(일부만 ALSO IN) kit/guide/테마-계약.md:17 · .claude/agents/ac3-reviewer.md:11

### U21 ### ⚠️ 「한 층·한 파일을 고쳤다」와 「규칙을 지켰다」는 다르다 (L255-267, 1111B)
- 범위: 인프라(검증 규율) · 분류 제안(제안일 뿐): [M] — 266 마지막 줄 「대상 계수 0은 미판정」은 AGENTS.md:71-72에 있음; 1-3 사례는 ONLY HERE
- 중복 보관: PARTIAL: AGENTS.md:71-72 · .githooks/README.md:24
- 규칙·교훈 문장:
  - L259 토큰을 고쳤으면 그 리터럴 값을 집행층 전체에서 grep(--shadow rgba 11곳) → ALSO IN kit/guide/테마-계약.md:157-162
  - L261 pre-commit은 스테이징된 .css만 본다 → kit 전체 린트 → ALSO IN .githooks/README.md:24 · scripts/hook_slide_guard.py:10,33
  - L263 --mode css-lint --path의 exit 0은 조용히 건너뜀 — 판정은 --stdin-paths만 → PARTIAL(일부만 ALSO IN) scripts/hook_slide_guard.py:106 (--path 힌트 조기 반환 코멘트)
  - L266 고친 직후 ①값 전역 재grep ②전 대상 검사기 ③판정 건수 확인(대상 0=미판정) → ALSO IN AGENTS.md:71-72 (눈먼 0 · 미판정)

### U22 ### ⚠️ 테마 적용은 «링크 한 줄»이다 (L269-281, 1024B)
- 범위: 인프라(테마) · 분류 제안(제안일 뿐): [X] 대부분 — 테마-계약.md §6(:111-112)과 tests/test_theme_contract.py에 있음
- 중복 보관: DUPLICATED IN kit/guide/테마-계약.md:111-112; tests/test_theme_contract.py:136
- 규칙·교훈 문장:
  - L273 테마 적용은 링크 한 줄(deck.css + themes/<이름>/tokens.css) 규약 → ALSO IN kit/guide/테마-계약.md:111-112 (§6)
  - L279 default 테마 덱은 테마 링크 줄을 넣지 않는다(D-1) → ALSO IN kit/guide/테마-계약.md:111
  - L281 테마 링크 없음·틀린 테마·2개 링크는 FAIL (ThemeStylesheetLinkTests) → ALSO IN tests/test_theme_contract.py:136

### U23 ### ⚠️ 토큰 계약 개정 — 99 → 100 (L283-297, 1073B)
- 범위: 인프라(테마) · 분류 제안(제안일 뿐): [X] — 테마-계약.md:11-20 · tokens.css · BlueChannelMirrorsBlueTests
- 중복 보관: DUPLICATED IN kit/guide/테마-계약.md:11-20
- 규칙·교훈 문장:
  - L285 rgba()는 var()를 못 받음 → --blue-rgb 채널 토큰 → ALSO IN kit/guide/테마-계약.md:14-20
  - L293 계수: 색 50·비색 50=100 · 3곳 모두 → ALSO IN kit/guide/테마-계약.md:11
  - L295 --blue와 --blue-rgb는 같은 색 — BlueChannelMirrorsBlueTests → ALSO IN kit/guide/테마-계약.md:19 · tests/test_theme_contract.py

### U24 ### ⚠️ 새 테마의 색 시스템 놓치기 쉬운 세 자리 (L299-313, 1350B)
- 범위: 인프라(테마) · 분류 제안(제안일 뿐): [X] 대부분 — 테마-계약.md:130,140,147 · likelionSKU/tokens.css:21
- 중복 보관: DUPLICATED IN kit/guide/테마-계약.md:130-147
- 규칙·교훈 문장:
  - L303 그림자 색 성분만 자기 --blue로 · 투명도·오프셋 유지 → ALSO IN kit/guide/테마-계약.md:130
  - L306 파비콘은 CSS 변수가 닿지 않는 유일한 색 자리 · 중립 잉크 → ALSO IN kit/guide/테마-계약.md:140
  - L309 대비 파생값 재계산(4.69→3.64) → ALSO IN kit/themes/likelionSKU/tokens.css:21
  - L312 덱 안 인라인 로고는 var(--mint)/(--blue) 사용이 옳다 → ALSO IN kit/guide/테마-계약.md:147

### U25 ### ⚠️ 격리 스캔의 기준은 「상속되는가」다 (L315-326, 1011B)
- 범위: 인프라(과목 격리) · 분류 제안(제안일 뿐): [S 격리] — verify_subject_isolation.py:73 · likelionSKU/profile.md:106에 반영
- 중복 보관: DUPLICATED IN scripts/verify_subject_isolation.py:73; courses/likelionSKU/profile.md:100-106
- 규칙·교훈 문장:
  - L319 격리 스캔 기준은 상속되는가(SCAN_WARN에 starter·styles 편입) → ALSO IN scripts/verify_subject_isolation.py:73 · courses/likelionSKU/profile.md:106
  - L324 등재하면 FAIL이니 리터럴을 빼자 — 전제부터 확인 → ALSO IN courses/likelionSKU/profile.md:100-106

### U26 ### ✅ R-QC-14 위반 14건 해소 (L328-354, 2570B)
- 범위: 인프라(CSS 린트) · 분류 제안(제안일 뿐): [H] + 336·345·348 교훈 [M]후보 — 수정 완료; 「일괄 치환이 동결 덱을 깨뜨린다」는 plans/likelionSKU-theme/RESULTS.md 외 정본에 없음
- 중복 보관: DUPLICATED IN plans/likelionSKU-theme/RESULTS.md (partial)
- 규칙·교훈 문장:
  - L330 R-QC-14 deck.css 후손 b/span → 직계 → ALSO IN .githooks/_gate.py:200 · AGENTS.md:62 (R-QC-14 집행)
  - L336 .foo b→.foo > b 일괄 치환은 동결 덱을 깨뜨린다(work-step 한 겹) → ONLY HERE*(정본 없음·비정본 사본만) plans/likelionSKU-theme/RESULTS.md
  - L345 CSS 수정 검증: 브라우저 감사를 수정 전에 먼저 재고 후에 다시(before/after) → ONLY HERE*(정본 없음·비정본 사본만) plans/likelionSKU-theme/RESULTS.md
  - L348 한 파일만 고치고 끝내지 마라 — kit CSS 전체 린트 · pre-commit은 스테이징만 → PARTIAL(일부만 ALSO IN) .githooks/README.md:24 (스테이징 .css만)

### U27 ### ⚠️ 다과목 저장소가 된 뒤의 규율 (L356-366, 1140B)
- 범위: 인프라(경로층) · 분류 제안(제안일 뿐): [M] — scripts/_course_paths.py docstring·verify_deck_quality.py:131에 코드로 있음
- 중복 보관: DUPLICATED IN scripts/_course_paths.py:55-86 (code docstring)
- 규칙·교훈 문장:
  - L360 과목 종속 임계를 import 시점에 읽지 마라 — run_checks 진입에서 → ALSO IN scripts/verify_deck_quality.py:131 (주석)
  - L363 resolve_course는 후보 0개면 None, 1개 이상 불일치면 던진다 → ALSO IN scripts/_course_paths.py:55-73
  - L365 스크립트 실행 시 과목을 밝혀라 CREATE_SLIDES_COURSE → ALSO IN scripts/_course_paths.py:66

### U28 ### ⚠️ .gitignore에 폴더명은 루트 앵커 (L368-373, 467B)
- 범위: 인프라 · 분류 제안(제안일 뿐): [M] (1줄 규칙) — ONLY HERE (plans/likelionSKU-theme/PLAN.md에 사실 언급)
- 중복 보관: —
- 규칙·교훈 문장:
  - L370 .gitignore에 폴더명은 루트 앵커(/likelionSKU/) → ONLY HERE*(정본 없음·비정본 사본만) plans/likelionSKU-theme/PLAN.md

### U29 ### 📌 문서 불일치 (고치지 않고 기록만) (L375-381, 658B)
- 범위: 인프라 · 분류 제안(제안일 뿐): [X] 대부분 낡음 — 377 해소 · 378 해소 · 380 번복(U24와 모순)
- 중복 보관: —
- 존재하지 않는 참조: kit/styles/deck.css:2 (SKU LIKELION 리터럴 — 제거됨)
- 열린 과업 서술 항목:
  - L377 검증-명령-지도 §6 회귀 건수 219 낡음 → **DONE IN REPO** (references/검증-명령-지도.md §6에 건수 서술 없음(219·266 grep 0))
  - L378 deck.css:2에 SKU LIKELION 리터럴 존재 → **DONE IN REPO** (kit/styles/deck.css에 리터럴 없음(grep 0); L354가 제거 기록)
  - L380 그림자를 테마 축에 넣을지 별도 안건 → **SUPERSEDED** (L283-304: --blue-rgb(1d86f88)로 그림자 색이 테마에서 파생됨 — 이 서술과 모순)
- 규칙·교훈 문장:
  - L377 검증-명령-지도 §6 회귀 건수 219 낡음→266 → ALSO IN (해소 — 지도에서 건수 서술 삭제됨)
  - L380 그림자를 테마 축에 넣을지는 별도 계약 안건 → ONLY HERE*(정본 없음·비정본 사본만) plans/likelionSKU-theme/PLAN.md (낡음)

### U30 ### 실험덱 처리 — 종결 (L383-395, 1378B)
- 범위: 인프라 · 분류 제안(제안일 뿐): [H] — 실험 산출물 삭제 완료; 393-395 관찰 후보 2건만 미완
- 중복 보관: —
- 존재하지 않는 참조: 강의덱_실험.html, 강의덱_실험_검토보고.html, plans/week2-plain-deck/, plans/deck-ampm-split/ (전부 의도적 삭제)
- 열린 과업 서술 항목:
  - L395 R-QC-05 사람검토 / R-QC-17 임계 0% WARN 승격(1·2·3주차 실측 선행) → **STILL OPEN** (verify_deck_quality.py 마지막 변경 8/29(f2831cd), 승격 흔적 없음)
- 규칙·교훈 문장:
  - L390 파이프라인 밖 덱은 게이트 사각지대 발견에 유효 — 필요하면 새로 만든다 → ALSO IN references/phases/08-검증.md:31
  - L393 R-QC-05 사람검토에 머무름 · R-QC-17 임계 0% WARN — 승격 후보 관찰 → PARTIAL(일부만 ALSO IN) scripts/verify_deck_quality.py (R-QC-05/17 현 거동)

### U31 ### ✅ 규칙 정본 모순·게이트 구멍 3건 — 전량 해소 (L397-426, 3657B)
- 범위: 인프라 / 바이브코딩 · 분류 제안(제안일 뿐): [H] — 결과는 profile.md·scripts·AGENTS.md:71·tests에 반영; 근거는 plans/rule-gap-fix/PLAN.md
- 중복 보관: DUPLICATED IN plans/rule-gap-fix/PLAN.md; AGENTS.md:71; tests/test_quality_gates.py
- 존재하지 않는 참조: plans/system-improvement/잔여작업-완결-지시문.md (의도적 삭제)
- 규칙·교훈 문장:
  - L402 제목 규칙 B안: 정식 용어는 취향·게이트 아님, §3 덱_스텝제목_서술형_상한은 별개 → ALSO IN courses/바이브코딩/profile.md §3-§4
  - L406 배포처 Netlify→ChatGPT Sites · 커리큘럼 기준안 소급 수정 안 함 → ALSO IN courses/바이브코딩/슬라이드지침.md §2 외
  - L410 R-QC-15 _FOOT_RE가 s-foot까지 세던 오탐 → _STRUCT_BAND_RE → ALSO IN scripts/verify_deck_quality.py:414-419
  - L413 22px 린트가 셀렉터 이름 의존 → 미판정 개수를 판정 문구에 찍는다 → ALSO IN AGENTS.md:71 · scripts/verify_deck.py:1317
  - L418 오탐만 재면 반쪽 — 미탐도 함께 잰다(AGENTS.md 등재) → ALSO IN AGENTS.md:71
  - L426 이월 사유를 진짜 블록과 구분해 적는다 — 등재가 완료의 대체물이 되지 않게 → ONLY HERE

### U32 ### ⏸ R-BOXFILL-01 상자 채움 검출 6종 (L428-436, 2473B)
- 범위: 인프라(감사기) · 분류 제안(제안일 뿐): [S 감사기] — 선언 정본 kit/guide/한장-참조표.md:76-95; 열린 판단 2건은 ONLY HERE
- 중복 보관: DUPLICATED IN kit/guide/한장-참조표.md:76-95; scripts/audit_render.js
- 열린 과업 서술 항목:
  - L434 BOXFILL 그룹 키를 넓힐 것인가(판단 대기) → **STILL OPEN** (scripts/audit_render.js 마지막 변경 bc20335(8/19))
  - L435 「축소 재현/데모 내부」 티어 부재(R-TYPE-01 공백과 한 원인) → **STILL OPEN** (검증-명령-지도.md:61-66 동일 선행조건; 신규 주차 입력 없음)
- 대기 중 사용자 결정 / 결정 서술:
  - L434 BOXFILL 그룹 키 확대 여부
- 규칙·교훈 문장:
  - L432 BOXFILL 판정 단위는 형제 한 벌 · 반대 결함 ragged를 같은 층에 → ALSO IN kit/guide/한장-참조표.md:76-78
  - L433 새 터미널·창 mock 구도는 CODE_BOX에 등재 → ALSO IN kit/guide/한장-참조표.md:95
  - L434 그룹 키(부모+태그+첫 클래스) 확장 판단 대기 → ONLY HERE
  - L435 축소 재현/데모 내부 티어 부재 → ALSO IN references/검증-명령-지도.md:61-66

### U33 ### ⏸ WARN → FAIL 승격 — 보류 (L438-446, 1861B)
- 범위: 인프라(게이트) · 분류 제안(제안일 뿐): [M] (보류 사유·선행조건 4개) — 판정 정본은 references/검증-명령-지도.md:55-66 「A-1 판정」
- 중복 보관: DUPLICATED IN references/검증-명령-지도.md:55-66
- 열린 과업 서술 항목:
  - L444 선행조건 ② kit 기본값이 22px 하한을 스스로 만족하게(사용자 결정) → **STILL OPEN** (kit/styles/deck.css·patterns.css 마지막 변경 8/29(--blue-rgb)뿐)
  - L445 선행조건 ③ 품질 게이트에서 사람검토 범주 분리 → **STILL OPEN** (verify_deck_quality.py 변경 없음(8/29))
  - L443 선행조건 ① 마커 티어 신설(신규 주차 입력 대기) → **STILL OPEN** (= U32 L435와 동일 항목)
- 대기 중 사용자 결정 / 결정 서술:
  - L444 kit 22px 하한 만족화 vs 동결 호환(D-1) 양립 방식
- 규칙·교훈 문장:
  - L440 WARN→FAIL 승격 판정 정본은 지도 §2 A-1 표 · 보류 → ALSO IN references/검증-명령-지도.md:55
  - L443 승격 선행조건 ①마커 티어 ②kit 22px ③사람검토 분리 ④BOXFILL 그룹 → ALSO IN references/검증-명령-지도.md:66

### U34 ### ⏸ Codex 패리티 — 페이로드 스키마 (L448-453, 893B)
- 범위: 인프라(Codex) · 분류 제안(제안일 뿐): [S Codex] — AGENTS.md:63,75 표와 plans/instruction-refactor/FINAL_REPORT.md, .codex/hooks/probe.py
- 중복 보관: DUPLICATED IN AGENTS.md:63,75; plans/instruction-refactor/FINAL_REPORT.md
- 열린 과업 서술 항목:
  - L452 Codex 경로 파싱 어댑터 → **STILL OPEN** (.codex/hooks/에 probe.py뿐)
- 규칙·교훈 문장:
  - L450 Codex PreToolUse에 파일 경로 키 없음 → 파싱 어댑터 필요 → ALSO IN AGENTS.md:63,75

### U35 ### ✅ 렌더 측정 재현성 — 규명·해소 (L455-466, 2883B)
- 범위: 인프라(감사기) · 분류 제안(제안일 뿐): [H]; 461-462 [X] — 절차 수정은 references/검증-명령-지도.md:64 · scripts/audit_all.js:184 에 반영
- 중복 보관: DUPLICATED IN references/검증-명령-지도.md:64; scripts/audit_all.js:184; tests/test_deck_pipeline.py:647
- 열린 과업 서술 항목:
  - L464 2026-08-17의 ovf 2 원인 미확인 → **STILL OPEN** (재현 불가로 기록(원인 미확인이 최종 서술))
- 규칙·교훈 문장:
  - L457 렌더 감사기는 결정적 — 흔든 것은 절차 결함 2건(이미지 로딩·환경 미기록) → ALSO IN tests/test_deck_pipeline.py:647 · 검증-명령-지도.md:64
  - L461 이미지 로딩을 기다리지 않으면 결함이 적게 나온다 — audit_render 이미지 assert → ALSO IN references/검증-명령-지도.md:64
  - L462 증거에 측정 환경(env 블록)을 기록 — diff에서 env 변화는 덱 변화로 읽지 마라 → ALSO IN scripts/audit_all.js:184
  - L466 지도 §3: audit_all.js fetch에 캐시버스터 ?v=Date.now() no-store → PARTIAL(일부만 ALSO IN) references/검증-명령-지도.md §3 (절차 수정 반영)

### U36 ### ⏸ 훅 오탐 장부가 휘발된다 (L468-472, 1049B)
- 범위: 인프라(훅) · 분류 제안(제안일 뿐): [M] (열린 판단 1건) — tmp/guard-observations.jsonl는 여전히 gitignore (346줄)
- 중복 보관: DUPLICATED IN scripts/hook_slide_guard.py:25,257 (comment); tests/test_hook_guards.py
- 열린 과업 서술 항목:
  - L470 훅 관측 장부를 추적되는 경로로 옮길지 판단 → **STILL OPEN** (git check-ignore: tmp/guard-observations.jsonl ← .gitignore:16 (현재 346줄, 여전히 휘발))
- 대기 중 사용자 결정 / 결정 서술:
  - L470 훅 관측 장부를 추적 경로로 옮길지
- 규칙·교훈 문장:
  - L470 훅 관측 장부 tmp/guard-observations.jsonl이 gitignore라 휘발 → PARTIAL(일부만 ALSO IN) scripts/hook_slide_guard.py:25,257 (휘발 문제 자체는 ONLY)
  - L472 에이전트 영속 메모리 쓰기는 오탐 예외(is_persistent_agent_memory) → ALSO IN scripts/hook_slide_guard.py:229 · tests/test_hook_guards.py

### U37 ### ⏸ 시스템 개선 계획 — 배치1~4 완료·이관만 (L474-482, 2107B)
- 범위: 인프라 / 바이브코딩 D-1 · 분류 제안(제안일 뿐): [M] 478-479 [S] / 나머지 [H] — 계획 정본 plans/system-improvement/ · 집행 규약 sessions/README.md
- 중복 보관: DUPLICATED IN plans/system-improvement/{ANALYSIS,PLAN,P7-판정}.md; courses/바이브코딩/profile.md:121
- 열린 과업 서술 항목:
  - L480 이관 ① P7 과목 오버라이드(테마) 층 정식화 → **DONE IN REPO** (kit/guide/테마-계약.md · kit/themes/{default,likelionSKU,frame} · c733758(8/24))
  - L480 이관 ② P3 접수 절차(쪽↔ID) 실사용 검증 → **DONE IN REPO** (courses/바이브코딩_온라인/sessions/1주차/개정이력/쪽ID매핑_*.md 4건)
  - L482 w1·w3 배포본 verify_deck FAIL 1(kit 유래 .s-body) 선재 → **NOT CHECKED** (재실행하지 않음)
  - L482 sessions/README.md 「1주차 (동결 해제…)」와 AGENTS 동결 서술 모순(사용자 확인) → **STILL OPEN** (sessions/README.md:122 「동결 해제」 vs AGENTS.md:40 「동결」 — 둘 다 현존)
- 대기 중 사용자 결정 / 결정 서술:
  - L482 sessions/README 「동결 해제」 vs AGENTS 「동결」 서술 모순 확인
- 규칙·교훈 문장:
  - L476 시스템 개선 계획 정본 plans/system-improvement/ · 집행 규약 정본은 sessions/README 주차 구조 계약 → ALSO IN references/검증-명령-지도.md:49 · sessions/README.md (주차 구조 계약)
  - L478 바이브코딩 과목은 3주차로 완결(D-1) — 산출물 수정 금지 · 계약은 예외 → ALSO IN courses/바이브코딩/profile.md:121 · AGENTS.md:40 · 테마-계약.md:111
  - L479 V1-04 종결(미복구 확정) — 복구를 다시 제안하지 마라 → ALSO IN courses/바이브코딩/profile.md:121 · scripts/verify_contract_waivers.py:9
  - L480 새 과목 착수 시점 이관 2건: P7 테마 층 정식화 · P3 접수 절차 실사용 → PARTIAL(일부만 ALSO IN) plans/theme-ui-expansion/REQUIREMENTS.md §8 (비정본)
  - L482 선재 2건: w1·w3 배포본 verify_deck FAIL 1 · sessions/README 동결 서술 모순 → ONLY HERE

### U38 ### ⏸ 지침 생태계 리팩터링 — Gate 0 완료 (L484-501, 4449B)
- 범위: 인프라(Codex·훅) · 분류 제안(제안일 뿐): [S Codex]/[H] — Gate 0 상세는 plans/instruction-refactor/FINAL_REPORT.md
- 중복 보관: DUPLICATED IN plans/instruction-refactor/FINAL_REPORT.md; AGENTS.md:63; .agents/README.md:21
- 열린 과업 서술 항목:
  - L452 Codex 경로 파싱 어댑터(U34와 동일) → **STILL OPEN** (위와 동일)
  - L486 로컬 브랜치 refactor/instruction-ecosystem 삭제 가능(병합됨) → **STILL OPEN** (git branch --list에 현존, ahead 0)
  - L500 generated-guard·tmp-guard 관측 → --enforce 승격(오탐 0 확인 후) → **STILL OPEN** (.claude/settings.json statusMessage가 여전히 「(관측)」)
  - L501 다음 과목 추가 시 course 훅이 조용히 죽는다 → **DONE IN REPO** (courses 5개; 8856fa5(8/24) 「조용한 오답→시끄러운 실패」 — 훅 침묵 거동 자체는 NOT CHECKED)
- 규칙·교훈 문장:
  - L486 refactor/instruction-ecosystem 병합 완료·잔존 브랜치 삭제 무방 → ONLY HERE*(정본 없음·비정본 사본만) plans/instruction-refactor/FINAL_REPORT.md
  - L492 Codex PreToolUse 페이로드 키 목록(실측) → PARTIAL(일부만 ALSO IN) AGENTS.md:63 · .codex/hooks/probe.py:3
  - L496 콘솔의 hook Completed는 실행 증거가 아니다 — 산출물로 판정 → ONLY HERE
  - L497 Codex hooks.json 함정: 최상위 description·hooks만 · matcher "*" 필수 → ALSO IN .agents/README.md:21
  - L498 codex exec stdin 열려 있으면 멈춤 < /dev/null · CODEX_CLI_PATH → ALSO IN skills/README.md:57-61
  - L499 훅은 클론마다 install_hooks.py 한 번 — 미설치면 verify_skill_setup exit 1 → ALSO IN .githooks/README.md:10-14
  - L500 generated-guard·tmp-guard 관측 모드 — enforce 전 오탐 0 확인 → ALSO IN AGENTS.md:70
  - L501 다음 과목이 추가되면 course 훅이 조용히 죽는다(guide_path 정확히 1개) → ALSO IN scripts/_course_paths.py:59 (주석)

### U39 ### ✅ 세션 폴더 덱의 kit CSS 상대경로 (L503-514, 2948B)
- 범위: 인프라(경로·검증) · 분류 제안(제안일 뿐): [M] 505-514 교훈 / 나머지 [X] — SKILL.md:32 · sessions/README.md:50 · sessions/_template README:12-13에 반영
- 중복 보관: DUPLICATED IN SKILL.md:32; sessions/README.md:50; sessions/_template/강의덱.초안/README.md:12-13
- 규칙·교훈 문장:
  - L505 덱의 kit CSS 상대경로 ../../../../kit/styles/ (4단계) → ALSO IN SKILL.md:32 · sessions/README.md:50 · sessions/_template/강의덱.초안/README.md:12
  - L507 kit CSS 404는 정적 게이트 PASS · 글래스 내비게이션 FAIL이 유일한 신호 → ALSO IN scripts/verify_deck.py:685 · sessions/_template README:13
  - L510 재조립 전 무수정 조립 먼저 해 drift 분리 측정 → ONLY HERE
  - L511 보존 판정은 body 이후 해시+섹션별 해시 → ONLY HERE
  - L512 배포본·발표본은 kit CSS 인라인이라 경로 버그 영향 없음 → PARTIAL(일부만 ALSO IN) scripts/verify_distributable.py:52
  - L514 덱을 만들면 로컬 http로 열어 styleSheets.length와 보이는 슬라이드 1장 확인 → ALSO IN sessions/_template/강의덱.초안/README.md:13

### U40a ### ★ 2주차 현재 상태 (112장) — 현재 상태부 (L516-537, 7253B)
- 범위: 바이브코딩 2주차 · 분류 제안(제안일 뿐): [S 바이브코딩2주차]/[H] — 조립_보고.md §10·§11에 있음; 526·530·543은 04-조립.md R-MOVE-01에 있음
- 중복 보관: DUPLICATED IN courses/바이브코딩/sessions/2주차/조립_보고.md; references/phases/04-조립.md:89-103
- 열린 과업 서술 항목:
  - L519 C4-H1 겹침 2건(render_lap waiver count 2) → **STILL OPEN** (courses/바이브코딩/sessions/2주차/deck.contract.json에 render_lap 존재(grep 2))
  - L531 초안에만 남은 행 1-9·1-10 판정 → **NOT CHECKED** (—)
  - L533 사용자 보류 Q2·Q3·Q9·Q10 → **NOT CHECKED** (개정이력/2주차_수정요청_v2_실행계획.md에 Q 표 있으나 번호 체계가 달라 대조 불가)
  - L536 브라우저 전수 미측정(바닥선 초과 3장) → **DONE IN REPO** (본문이 2026-08-04 렌더 감사 below 0으로 해소 확인 기록)
- 대기 중 사용자 결정 / 결정 서술:
  - L533 사용자 보류 Q2·Q3·Q9·Q10 (다음 세션이 상기시킬 것)
- 규칙·교훈 문장:
  - L525 컬러 2장은 R-COLOR-01 예외 · --sw-* 두 장 스코프 → ONLY HERE*(정본 없음·비정본 사본만) courses/바이브코딩/sessions/2주차/조립_보고.md
  - L526 발표자 노트는 장을 지우면 통째로 밀린다 — 덱 장 삭제·이동 시 노트 재조립 → ALSO IN references/phases/04-조립.md:95 (R-MOVE-01 ①)
  - L527 R-COLOR-06 강조색 예산 2장 한도(C5-5+A3F2) → ALSO IN kit/guide/디자인시스템.md:25 (R-COLOR-06)
  - L528 표로 바꾸기 전에 세로 예산부터 재라 → ONLY HERE
  - L529 C1-8 폐기 — 다시 살리지 마라 → ONLY HERE*(정본 없음·비정본 사본만) courses/바이브코딩/sessions/2주차/개정이력/… (C1-8 폐기 기록)
  - L530 매니페스트 JSON은 텍스트 수술(재직렬화 바이트 불일치) — 왕복 검사 먼저 → ALSO IN references/phases/04-조립.md:100 (R-MOVE-01 ⑥)
  - L532 같은 구도 3연속 가짜 — layout_families 등재 · 이웃 family 재확인 → ALSO IN 04-조립.md:98 (③) · kit/guide/테마-계약.md:31
  - L533 사용자 보류 Q2·Q3·Q9·Q10 → ONLY HERE
  - L534 삭제가 남긴 자국 3건 → ONLY HERE*(정본 없음·비정본 사본만) courses/바이브코딩/sessions/2주차/개정이력/

### U40b ### ★ 2주차 — 113장 시점 (2026-08-02 PART4↔5 스왑) (L538-569, 7046B)
- 범위: 바이브코딩 2주차 · 분류 제안(제안일 뿐): [H] — 스왑 계획은 courses/바이브코딩/sessions/2주차/개정이력/2주차_PART45_스왑_실행계획.md
- 중복 보관: DUPLICATED IN courses/바이브코딩/sessions/2주차/개정이력/2주차_PART45_스왑_실행계획.md
- 존재하지 않는 참조: 자료/images/s13_mvp-*.png (의도적 삭제), 2주차_이미지-프롬프트.md (자료/ 아래에 존재)
- 열린 과업 서술 항목:
  - L567 미완: 콘텐츠 리뷰 HTML · 실제 이미지 14장 → **NOT CHECKED** (L648과 같은 항목 — 리뷰 HTML은 courses/바이브코딩/sessions/2주차에 부재(온라인 과목에만 존재))
- 규칙·교훈 문장:
  - L544 divider ID는 파트 재배치 시 함께 교환 — 단조성 검사(known_violations 강등 불가) → ALSO IN references/phases/04-조립.md:96 (R-MOVE-01 ②)
  - L543 본문 data-slide ID는 전량 유지 · 번호 안 밀고 새 번호 → ALSO IN references/phases/04-조립.md:12-16 (R-SLIDE-ID-01)
  - L545 파트를 옮기면 목차(S03) 세로 예산 — 항목 1줄 39자 → ALSO IN references/phases/04-조립.md:97 (R-MOVE-01 ④)
  - L549 완료 기준 어미는 「…확인합니다」(사용자 확정) → ONLY HERE (정본 grep 0건: kit/guide·references·슬라이드지침)
  - L551 예시 프롬프트 = 컨텍스트 엔지니어링 형식 · 민트는 학생이 채우는 칸 전용 → ONLY HERE (정본 grep 0건; 2주차 shell CSS .fill 규칙에만 구현)
  - L554 프롬프트 장 세로 예산 terminal-copy 9줄 → ONLY HERE*(정본 없음·비정본 사본만) courses/바이브코딩/sessions/2주차/조립_보고.md
  - L556 실습은 «실습 장 + 다음 장 예시 프롬프트» 한 모양(예외 A4R1) → PARTIAL(일부만 ALSO IN) kit/layouts/by-shape.md:43
  - L558 재번호는 뒤에서 지울수록 싸다 / 치환 시 원문자 보호 → ALSO IN references/phases/04-조립.md:99 (R-MOVE-01 ⑤)
  - L565 끼워 넣기 ID 규약 — 번호를 밀지 않는다 → PARTIAL(일부만 ALSO IN) references/phases/04-조립.md:12-16 (R-SLIDE-ID-01)

### U41 ### 2026-08-03 2주차 발표본 산출 — 재발 방지 (L571-593, 8641B)
- 범위: 인프라(발표본) / 바이브코딩 2주차 · 분류 제안(제안일 뿐): [M]/[S 발표본] — 587-588은 07-발표자노트.md:13-23에 있음; 577·579·582·585·586·590은 ONLY HERE
- 중복 보관: PARTIAL: references/phases/07-발표자노트.md:13-23 · 04-조립.md:95
- 열린 과업 서술 항목:
  - L593 체크리스트 8항목 최종 판정은 실제 Windows Chrome·Edge에서 사람이 → **NOT CHECKED** (—)
- 규칙·교훈 문장:
  - L575 발표본 deckId 불변(바꾸면 강사 메모 유실) → PARTIAL(일부만 ALSO IN) kit/runtime/presenter-runtime.js:117 (코드)
  - L576 덱·노트 고치면 발표본 재주입 — 동기화 대상에 발표본 항상 → PARTIAL(일부만 ALSO IN) tests/test_deck_pipeline.py:924 (재주입 회귀)
  - L577 판정은 meta.json diff가 아니라 멘트 원문 grep → ONLY HERE
  - L579 build_release.py는 1단계에서 강의덱.html을 덮어쓴다 → --preview 같은 폴더 임시 이름 → ONLY HERE
  - L580 폰트 임베드 fontTools+brotli 필요 · 인터프리터 고정 금지 → ALSO IN references/검증-명령-지도.md:6
  - L581 verify_presenter_deck 외부참조 검사 data-expected-src 오탐 → (?<![\w-]) → ALSO IN scripts/verify_presenter_deck.py (수정 반영)
  - L582 배포본·발표본은 verify_deck에서 .s-body 22px FAIL이 정상 기준선 → ONLY HERE*(정본 없음·비정본 사본만) courses/바이브코딩/sessions/2주차/조립_보고.md
  - L583 발표본 판정 근거는 verify_presenter_deck(슬라이드 불변 지문) → ALSO IN scripts/inject_presenter.py:433,457 (slideHashes)
  - L585 R-META-01 TBD FAIL은 base64 오탐 — 정본 강의덱.html에서 본다 → ONLY HERE*(정본 없음·비정본 사본만) courses/바이브코딩/sessions/2주차/조립_보고.md
  - L586 대용량 산출물 git 추적 정책 전환 — 배포본·발표본 추적 중 → ONLY HERE*(정본 없음·비정본 사본만) (git 이력 · AGENTS 계열 서술 없음)
  - L587 노트 머지에서 상대 쪽 멘트를 텍스트 집합으로 판정 금지 — 제목+멘트로 → ALSO IN references/phases/07-발표자노트.md:13-15 (R-NOTE-02)
  - L588 노트 작업은 착수 전 --snapshot, 끝나고 --baseline → ALSO IN references/phases/07-발표자노트.md:13-23
  - L590 장이 삭제되면 멘트는 이웃 장으로 옮겨져 있을 수 있다 → ONLY HERE
  - L591 meta.json은 노트 내용을 담지 않는다 — 노트 바뀌면 meta 같아도 재주입 → PARTIAL(일부만 ALSO IN) scripts/inject_presenter.py:438 (코드)
  - L592 emptySlides 0 ≠ 모든 장에 항목 — pn-item 0개 장 직접 센다 → PARTIAL(일부만 ALSO IN) scripts/verify_notes.py (pn-item 0 WARN, L588)
  - L593 팝업 차단 시 청중 화면 메모 누출 0 실측 · 체크리스트 8항목은 실기기 → PARTIAL(일부만 ALSO IN) kit/runtime/presenter-runtime.js:621,953 (코드)

### U42 ### 2026-07-30 새로 얻은 재발 방지 (L595-602, 2359B)
- 범위: 인프라(조립·측정) · 분류 제안(제안일 뿐): [S 검증] — 599·601은 코드·스크립트에 반영; 597·602 ONLY HERE
- 중복 보관: PARTIAL: scripts/map_slide_pages.py:15 · kit/guide/디자인시스템.md:105
- 규칙·교훈 문장:
  - L597 워커 산출물 <style> 정규식 — 설명문의 <style> 글자에 걸림 · 1쌍 확인 → ONLY HERE
  - L598 측정용 .slide display:block 강제는 레이아웃을 부순다 — is-active 토글 → PARTIAL(일부만 ALSO IN) kit/styles/deck.css:213 (코드)
  - L599 .s-pageno를 666 검사에서 제외 → ALSO IN kit/guide/디자인시스템.md:105 · 테마-계약.md:43
  - L600 노트를 덱과 맞출 때 제목으로 짝짓지 마라 — ID 순서 1:1 · 덮어쓰기 전 사본 → ALSO IN references/phases/07-발표자노트.md:10 (R-NOTE-01c)
  - L601 표시 페이지 번호 = DOM 인덱스+1 (cover·closing도 자리 차지) → ALSO IN scripts/map_slide_pages.py:15
  - L602 이미지 슬롯 겹침은 글자 범위가 아니라 요소 박스로 판정 → ONLY HERE

### U43 ### ★ 2026-07-29 확정 (A. 디자인 재현 방식) (L604-619, 3702B)
- 범위: 전 과목(kit 정책) · 분류 제안(제안일 뿐): [S kit 정책] 608-612 [X] — kit을 키우지 않는다·2회 이상 승격: 테마-계약.md:31-33·by-shape.md:20-43·SKILL.md:104에 있음
- 중복 보관: DUPLICATED IN kit/guide/테마-계약.md:31-33; kit/layouts/by-shape.md:20,26,42-43
- 열린 과업 서술 항목:
  - L618 미실행 작업 3: 프로필 §4 「정식 용어」·「출처 비표시」가 과목 종속인지 재검토 → **SUPERSEDED** (「정식 용어」는 L402-405 B안으로 종결; 「출처 비표시」는 NOT CHECKED)
- 규칙·교훈 문장:
  - L608 kit을 키우지 않는다 — 카탈로그 적극 확장 금지, 신규 구도는 계약 layout_families → ALSO IN kit/guide/테마-계약.md:31 · kit/layouts/by-shape.md:26
  - L612 kit 승격은 서로 다른 과목 2회 이상(R-PROMO-01) → ALSO IN kit/guide/테마-계약.md:33 (R-PROMO-01)
  - L614 마무리 변주 판정 절차: 파트 닫는 슬라이드 DOM 골격 인접 대조 → ALSO IN kit/layouts/by-shape.md:42
  - L616 확정 기록 있는 동일 골격은 결함 아님(예시 프롬프트 템플릿 고정) → ALSO IN kit/layouts/by-shape.md:43
  - L618 미실행 3: 프로필 §4 정식 용어·출처 비표시가 과목 종속인지 재검토 → NOT CHECKED
  - L619 연출 아이디어 출처는 개념KB PPT 소재 — 기본 참조 의무 → ALSO IN SKILL.md:24,28

### U44 ### ★ 2026-07-29 확정 (B. 초안 단계 폐기) (L621-639, 3936B)
- 범위: 전 과목 파이프라인 · 분류 제안(제안일 뿐): [H] + 630·633 교훈 [M]후보 — 폐기 완료·이관처는 skills/README.md:24, AGENTS.md:41,82
- 중복 보관: DUPLICATED IN skills/README.md:24; AGENTS.md:41,82; SKILL.md:23-24
- 존재하지 않는 참조: skills/콘텐츠/SKILL.md, .claude/skills/콘텐츠, .agents/skills/콘텐츠 (폐기·삭제)
- 열린 과업 서술 항목:
  - L637 R-QD-01/03/07을 덱 단계(R-QC-01/02)로 이관 검토 → **NOT CHECKED** (verify_deck_quality.py에 R-QC-01/02 존재하나 이관 판정 기록 미확인)
  - L639 skills/README 계약표·verify_skill_setup 팀 스킬 갱신 → **DONE IN REPO** (TEAM_SKILLS = 리서치·검토·하네스(콘텐츠 제거); skills/콘텐츠 부재)
- 규칙·교훈 문장:
  - L625 /콘텐츠 폐기 — 입력양식·콘텐츠초안-입력형식·verify_draft_quality 살아 있음 → ALSO IN AGENTS.md:41 · skills/README.md:24
  - L627 파이프라인 /리서치→/create-slides→/검토 3단 → ALSO IN AGENTS.md:82
  - L629 ⓐ 경로·스키마 지우지 마라 · 파일명 「콘텐츠」는 폐기 아님 → ALSO IN AGENTS.md:41 · SKILL.md:23-24
  - L630 스킬을 지우기 전에 그 파일에만 있는 정본을 rg 전수 조사 → ONLY HERE*(정본 없음·비정본 사본만) skills/README.md:24 (결과만)
  - L632 이관처 맵(R-PLAN·R-ANNEX·R-ACC·R-CAL·R-DENS→phases) → ALSO IN skills/README.md:24
  - L633 요약하면 예외 조건·반례가 빠져 판정 불가 — 요지만 읽고 판정 가능한지 기준 → ONLY HERE (요지 작성 시 판정 가능성 기준 — 정본 grep 0건)
  - L634 verify_skill_setup TEAM_SKILLS 이름 하드코딩 → ALSO IN scripts/verify_skill_setup.py:32
  - L635 evals 재배정 R2/C4 · C3 삭제 → ALSO IN evals/team-skills-eval.json
  - L637 verify_draft_quality R-QD-01/03/07은 유용 — 덱 단계로 이관 검토 → ALSO IN courses/바이브코딩/profile.md:33
  - L638 이관 시 로드량 회귀 주의 — 통째로 복사 말고 요지+포인터 → ALSO IN references/phases/08-검증.md:61
  - L639 skills/README 계약표·verify_skill_setup 팀 스킬 4종 검사 갱신 → ALSO IN (완료 — TEAM_SKILLS 갱신됨)

### U45 ### ★ 2026-07-29 확정 (C. 2주차 재설계 15장) (L641-649, 2275B)
- 범위: 바이브코딩 2주차 · 분류 제안(제안일 뿐): [H]; 648·649 열린 2건 [S] — 편입 완료; 아카이브는 _dev/설계기록/탐색-아카이브/2주차/재설계/
- 중복 보관: —
- 존재하지 않는 참조: 재설계/4구간/samples.css (이동·아카이브됨)
- 열린 과업 서술 항목:
  - L648 2주차_콘텐츠_리뷰.html 미산출(R-QD-05 FAIL 1건) → **STILL OPEN** (courses/바이브코딩/sessions/2주차/에 파일 부재(find 결과: 온라인 과목에만 존재))
  - L649 덱 4파일 CSS 주석이 옛 경로 재설계/4구간/samples.css를 출처로 적음 → **STILL OPEN** (강의덱.html·_발표·_배포·shell.html 4파일에 문자열 현존(grep -l))
- 규칙·교훈 문장:
  - L644 편입 때 클래스 이름 w5b-*→w2-* 통일 — 제목+클래스 양쪽으로 확인 → ONLY HERE*(정본 없음·비정본 사본만) courses/바이브코딩/sessions/2주차 조립_보고 (클래스 개명 기록)
  - L645 계약의 죽은 등재 layout_families는 주기적으로 덱과 대조 → ONLY HERE*(정본 없음·비정본 사본만) courses/바이브코딩/sessions/2주차 deck.contract.json
  - L648 2주차_콘텐츠_리뷰.html 미산출(R-QD-05 FAIL) → ALSO IN SKILL.md:132 · references/phases/04-조립.md:67 (게이트 존재; 파일 미산출은 열린 과업)
  - L649 덱 4파일 CSS 주석이 옛 경로 samples.css를 출처로 적음 → ONLY HERE

### U46 ### ★ 2026-07-29 확정 (D. 그 밖의 미결) (L651-658, 1833B)
- 범위: 전 과목 / 바이브코딩 프로필 · 분류 제안(제안일 뿐): [M] 654·658 사용자 결정 / 657 교훈 — 결정(교육원칙-요약 kit 유지 · --accent-note 안 함)은 다른 곳에 없음(ONLY HERE)
- 중복 보관: —
- 열린 과업 서술 항목:
  - L653 evals/trigger-eval.json 수동 회귀 미실시 → **NOT CHECKED** (trigger-eval.json 마지막 변경 7/26(bd41359); 실행 기록 미확인)
- 규칙·교훈 문장:
  - L653 evals/trigger-eval.json 수동 회귀 미실시 → ALSO IN courses/바이브코딩/profile.md:143 (면제 기록)
  - L654 교육원칙-요약.md는 kit에 그대로 — 다시 옮기자고 하지 마라 → PARTIAL(일부만 ALSO IN) SKILL.md:47 (「다시 옮기자」 금지 결정은 ONLY)
  - L657 ~는 과목 종속이다류 판정은 원문을 열어 과목 리터럴을 세라 → ALSO IN tests/test_course_paths.py:279
  - L658 --accent-note kit 등재 안 한다 — 다시 제안하지 마라 → ONLY HERE (결정: --accent-note kit 등재 안 함 — 정본 grep 0건)

### U47 ### ★ 2026-07-29 확정 — 2주차 덱 구조 상수 (L660-667, 2368B)
- 범위: 바이브코딩 2주차 · 분류 제안(제안일 뿐): [S 바이브코딩2주차]/[H] — 구성 정본은 sessions/2주차/강의덱.초안/README.md
- 중복 보관: DUPLICATED IN courses/바이브코딩/sessions/2주차/강의덱.초안/README.md (per L662)
- 열린 과업 서술 항목:
  - L666 미산출: 배포본·발표본·집필노트·리뷰HTML → **DONE IN REPO** (2주차 강의덱_배포·발표.html 존재(L575) · 집필노트 존재(L647); 리뷰 HTML만 STILL OPEN(L648))
  - L667 B1·B2·B3·B5는 다른 작업자가 별도 수행 → **NOT CHECKED** (—)
- 규칙·교훈 문장:
  - L661 예비·확장 구획은 THANK YOU 뒤 별도(w2-annex) → ONLY HERE*(정본 없음·비정본 사본만) courses/바이브코딩/sessions/2주차/강의덱.초안/README.md
  - L662 조립기 마커는 1개뿐 — END·THX는 part-06 끝 → ALSO IN references/검증-명령-지도.md:19 · sessions/README.md:50
  - L663 patterns.css 환류 폐기 — 1회 사용분 환류는 R-PROMO-01 위반 → ALSO IN kit/guide/테마-계약.md:33 · SKILL.md:104
  - L664 신규 구도는 verify_deck family 레지스트리에도 등재 · generic 폴백보다 먼저 → ALSO IN kit/guide/카탈로그-규격.md:175-179 (R-LAYOUT-03)

### U48 ### ★ 1주차 동결·발표 시스템(0~9단계) (L669-684, 5978B)
- 범위: 바이브코딩 1주차 / 인프라(발표자 런타임) · 분류 제안(제안일 뿐): [S 발표 시스템] — 발표 시스템 정본 plans/presenter-system-final-plan.md · kit/runtime/*
- 중복 보관: DUPLICATED IN plans/presenter-system-final-plan.md; kit/runtime/presenter-runtime.js
- 존재하지 않는 참조: sessions/_contracts/, 초안.md, screenshot/, 초안_미리보기.md (이동·정리됨)
- 열린 과업 서술 항목:
  - L673 수동 실기기표(Windows Edge·macOS Chrome 열)와 §29 성능 측정 → **NOT CHECKED** (—)
- 규칙·교훈 문장:
  - L670 덱 산출물 회귀 게이트는 발표본 사이드카 slideHashes 대조 → ALSO IN scripts/inject_presenter.py:433 (slideHashes)
  - L671 verify_deck --parts N의 N은 divider 수 → PARTIAL(일부만 ALSO IN) SKILL.md:118 / 검증-명령-지도 --parts 언급 (N=divider 수 문장은 ONLY)
  - L674 노트 정합 복구 승인 · 멘트 본문 전량 보존 → ONLY HERE*(정본 없음·비정본 사본만) courses/바이브코딩/sessions/1주차 조립 기록
  - L675 노트 항목 파서는 상태 기반 HTMLParser 금지 — 범위 스캔(iter_class_blocks) → ALSO IN scripts/inject_presenter.py:153 (iter_class_blocks)
  - L676 노트 블록은 section.pn-slide — rindex("</div>") 금지 → ALSO IN kit/starter/presenter-notes-template.html:15,45
  - L677 file:// 청중 창 새로고침 시 opaque origin — 좀비 팝업 자폐 + 1클릭 재열기 → ALSO IN kit/runtime/presenter-runtime.js:627
  - L678 발표 런타임 결함 4종(배율 min(w/h)·타이머·rebind 재조회·data-pv-window) → ALSO IN kit/runtime/presenter-runtime.js:757 (data-pv-window) 외
  - L679 16:9 박스와 임의 비율 컨테이너는 남는 공간 — 오른쪽(노트)이 흡수 → ONLY HERE
  - L683 --registry kit/images/... 붙이면 unknown registry asset FAIL — 기존 상태 → PARTIAL(일부만 ALSO IN) scripts/verify_deck.py:4 (사용법만)
  - L684 연작 이미지는 그룹 총 높이를 맞춘다 → ONLY HERE

### U49 ### ★ 번호 미결 0~7 + AC3 제작 중단 (686-696) (L686-696, 4040B)
- 범위: 바이브코딩 2주차 / 전 과목 · 분류 제안(제안일 뿐): [H] 다수 낡음; 열린 항목은 NOT CHECKED — 7개 번호 항목이 2주차 시점(7/22~8/3) 서술 — 3주차·후속 작업이 이후 진행
- 중복 보관: —
- 열린 과업 서술 항목:
  - L686 2주차 리서치 사람 실측 9건(Plus Sites·D6·D10) → **NOT CHECKED** (실측 양식 courses/바이브코딩/sessions/2주차/자료/실측/2주차_앱조작_사람입력.md 존재; 채움 여부 미확인)
  - L687 verify_deck 신뢰도 잔여 재감사 → **NOT CHECKED** (—)
  - L688 report_draft_sync: ① exit 1 부재 ② 초안 제목이 화면 텍스트에 있는지 검사 → **DONE IN REPO** (scripts/report_draft_sync.py에 sys.exit(1) 1곳; scripts/check_title_survival.py 존재 (부분))
  - L691 2주차 계약 정합 잔여(복구 기준 필드 · _template 슬롯 · 리뷰 HTML allowlist) → **NOT CHECKED** (—)
  - L692 G8 유형:사례 하한 3주차에서 판단 → **NOT CHECKED** (3주차 산출 완료 이후 판단 기록 미확인)
  - L693 배포 파이프라인 실전 검증 · --livereload → **NOT CHECKED** (assemble_deck.py에 livereload 코드 존재; 실서버 검증 기록 미확인)
  - L694 이미지 파이프라인 통합 잔여(candidate 검수·이미지 계약 → 러너) → **NOT CHECKED** (—)
  - L695 아틀라스·코어 자산 정합(생성기 개수 어서션 · 코어 차트 세트) → **NOT CHECKED** (—)
  - L696 AC3 3차시 제작 중단(9/11 세션 한도) — 재개 정본 재개_인계.md → **SUPERSEDED** (L189 결정 + eb588c1(9/12 83장 완성); 재개_인계.md는 9/11 00:43 작성본 그대로(낡음))
- 규칙·교훈 문장:
  - L686 2주차 리서치 사람 실측 9건 대기(Plus Sites·D6·D10) → NOT CHECKED
  - L687 verify_deck 신뢰도 잔여 재감사 · PASS를 전수검증 대체로 쓰지 않는다 → PARTIAL(일부만 ALSO IN) references/phases/08-검증.md:78
  - L688 report_draft_sync는 항상 통과(exit 1 없음) · 필요 검사는 초안 제목이 화면 텍스트에 있는가 → ALSO IN references/검증-명령-지도.md:33,49 · scripts/check_title_survival.py
  - L691 2주차 계약 정합 잔여(복구 기준 필드·_template 슬롯·리뷰HTML allowlist) → NOT CHECKED
  - L692 G8 유형:사례 하한만 재검토 → ALSO IN evals/team-skills-eval.json:33 · scripts/verify_research_chunks.py:36
  - L693 배포 파이프라인 실전 검증 · --livereload → NOT CHECKED
  - L694 이미지 파이프라인 통합 잔여(candidate 검수·이미지 계약 검증을 러너에) → NOT CHECKED
  - L695 아틀라스·코어 자산 정합 — 생성기 개수 어서션 → NOT CHECKED

## 3. 파일 내 모순·번복 쌍

- C1: L180·182 「병합 대기」 + L220 「main 병합·push 승인 대기」 | repo: feat/ac3-w2-prd-reorder · feat/likelionsku-theme 모두 ahead 0, tip이 origin/main 포함 | 판정: 번복(repo가 사실)
- C2: L151 제목 「119장 미커밋」 · L153 「123장 미커밋」 · L157 제목 「84장」 · L161 「99장」 · 인계 「111장 a979b42 커밋」 | 같은 FRAME 덱의 장수가 6개 값(84/99/104/111/119/123)으로 공존 | 판정: 층층이 쌓인 상태 — 제목(L157)은 낡음
- C3: L643 「「동결」도 더는 없다」 · L669 「1주차 동결 해제」 vs L478 「D-1 1·2·3주차 산출물 수정 금지」 · L482 「서술 모순(사용자 확인 필요)」 vs AGENTS.md:40 「동결」 | MEMORY 안에서 동결 해제/유지가 3겹, AGENTS.md와도 불일치 | 판정: 미해결 모순(L482가 스스로 지목)
- C4: L122 「킷 결함 2건 — patterns.css 환류 대상」 vs L663 「patterns.css 환류 항목은 폐기」 | kit CSS 결함은 현존(patterns.css:16, deck.css:557·655) | 판정: 환류는 폐기·결함은 방치 — 두 서술 병존
- C5: L378 「SKU LIKELION 리터럴을 등재할 수 없다(상시 FAIL)」 vs L324-326 「등재 후 WARN 56→58 PASS」 | 같은 파일 안 정반대 결론 | 판정: L378이 낡음(L354: deck.css 리터럴 제거됨)
- C6: L380-381 「그림자를 테마 축에 넣을지는 별도 안건」 vs L283-304 「--blue-rgb로 그림자 색을 테마에서 파생(1d86f88)」 |  | 판정: L380이 낡음
- C7: L178 「3차시 덱·초안 미착수」 · L189 「AC3 미완 후속 재개 안 함」 · L696 「제작 중단 — 재개_인계 읽기」 | repo: eb588c1(9/12) 83장 조립 완료 | 판정: 번복(repo가 사실); L696의 재개 지시는 L189와도 충돌
- C8: L192 「P1 커밋은 사용자 요청 시」 vs L187 제목 「커밋 88414d3」 |  | 판정: 제목이 사실
- C9: L3·L9 「커밋 기록·완료 표시·날짜별 작업 기록으로 보존하지 않는다」 vs 실제: 커밋 해시 13줄 · 날짜 128줄(697줄 중) · ✅ 제목 5개 · 취소선 6줄(481·580·584·586·643·655) | 헤더 규약과 본문 관행이 반대 | 판정: 관행이 규약을 어김
- C10: L14 「환류 규칙에 집행 절차 없음」 vs references/phases/08-검증.md:48 R-FEEDBACK-01(2026-08-03 신설) |  | 판정: L14의 «문제»는 일부 해소(절차 존재)
- C11: L476·480 「남은 것은 이관 항목뿐」 vs 이관 ①②가 repo에서 이미 구현 | 테마 계약(8/24-29) · 쪽ID매핑 4건 | 판정: 낡음
- C12: L518 「112장이 최신」 vs L524 「현행 110장」 vs L535 「110장 기준 재실측」 | 같은 절 안에서 「폐기」 표시와 함께 보존 | 판정: L518이 사실
- C13: L174 「오전 90장·캡처 14슬롯」 vs L165 제목 「1차시 81장」 | 같은 ### 안 | 판정: 제목이 사실(81 section)
- C14: L567 「미완: 콘텐츠 리뷰 HTML」 · L648 「미산출」 (같은 항목 반복) | 파일 부재 확인 | 판정: 일관(둘 다 열림)