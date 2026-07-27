# create-slides 검증 공백 감사 — validation_gap_report

읽기 전용 감사. 산출물 경로: `reports/create-slides-quality/validation_gap_report.md`.
병렬 감사가 이미 작성한 `reports/create-slides-quality/deck_quality_metrics.json`(§D의 1차 근거)을 재사용했다.

## A. 기존 게이트 전수 인벤토리

### A.1 `scripts/verify_deck.py` (1671줄) — 개별 검사 전수

| 검사 (메시지 요지) | file:line | 분류 | 잡는 것 | 구조적으로 못 잡는 것 |
|---|---|---|---|---|
| 슬라이드 장수 ≥5 | verify_deck.py:1017 | 구조 | 파이프라인 조립 실패 | 장당 내용량 |
| data-slide 유일성·존재 | verify_deck.py:1025 | 구조 | ID 중복/누락 | 내용 |
| `.s-head`에 `.s-logo` | verify_deck.py:1046 | 구조 | 브랜드 요소 누락 | 내용 |
| 힌트 UI·강사문구 유출 0 | verify_deck.py:1054 | 문법 | 학생본 오염 | 내용 |
| 주차 구조계약(`deck.contract.json`) 슬라이드수/디바이더/순서/종결 | verify_deck.py:1069-1163 | 구조 | 계약 대비 구조 이탈 | 계약 자체가 장수·순서만 규정, 내용량 무관 |
| 고정 슬라이드(cover/s02/s03) 존재 | verify_deck.py:1164 | 구조 | 필수 슬라이드 누락 | 내용 |
| 브랜드 텍스트 VIBECODING | verify_deck.py:1176 | 문법 | 오타 | 내용 |
| part-divider 수 = 파트 수 | verify_deck.py:1182 | 구조 | 디바이더 누락/과다 | 내용 |
| divider 번호 단조증가 | verify_deck.py:1238 | 구조 | 순서 이탈 | 내용 |
| 본문 PART 라벨=직전 divider | verify_deck.py:1245 | 구조 | 라벨 불일치 | 내용 |
| 네비바 존재 | verify_deck.py:1253 | 구조 | 조작 UI 누락 | 내용 |
| PDF 버튼 존재 | verify_deck.py:1254 | 구조 | UI 누락 | 내용 |
| 상세 메뉴 요소 | verify_deck.py:1258 | 구조 | UI 누락 | 내용 |
| deck.css 상속 | verify_deck.py:1262 | 경로·참조 | CSS 미로드 | 내용 |
| legibility 레이어 로드 | verify_deck.py:1263 | 접근성 | 22px 하한 위험 신호(WARN) | 실제 렌더 크기(브라우저 필요) |
| eyebrow PART 중복 없음 | verify_deck.py:1269 | 스타일 | 텍스트 중복 | 내용 |
| 이미지 경로·목적·역할·배치 계약 | verify_deck.py:1286 | 경로·참조 | 매니페스트 스키마 위반 | 이미지가 아예 0장인 경우(계약 자체가 통과) |
| 이미지 배선(ready 슬라이드에 `<img>`) | verify_deck.py:1293-1328 | 경로·참조 | 배선 누락 | 시각화가 카드로 대체된 것(증상 5) — 이미지 슬롯이 없으면 검사 대상 자체가 없음 |
| 구도(레이아웃 family) 다양성 ≥6종 | verify_deck.py:1391 | 구조 | 레이아웃 획일화 | 장수가 늘어도 문턱(6종)이 고정 — 108장에서 21종 통과는 자명(증상 8 실질 미검출) |
| 같은 구도 최장 연속 ≤2 | verify_deck.py:1395 | 구조 | 국소 반복 | 전체 반복률(같은 family가 듬성듬성 반복) |
| raw #hex 등 색 토큰 위반 | verify_deck.py:1421 | 스타일·색 | 색 규칙 위반 | 내용 |
| 인라인 그라디언트/navy/박스표면 | verify_deck.py:1441-1458 | 스타일·색 | 디자인시스템 위반 | 내용 |
| `.an-num` flat, glass 토큰 | verify_deck.py:1470-1474 | 스타일·색 | 디자인시스템 위반 | 내용 |
| 세션 CSS 폰트 ≥22px | verify_deck.py:1496 | 접근성 | 폰트 축소 | computed 렌더값(브라우저 필요) |
| 진행·페이지 자동주입 | verify_deck.py:1505 | 구조 | 주입 누락 | 내용 |
| `[kit]` 토큰/그라디언트/navy/레거시블루/박스표면/토큰값/헤더선/민트강조 등 8종 | verify_deck.py:1536-1604 | 스타일·색 | kit 자체 디자인시스템 위반 | 덱 내용(kit은 배포 자산이지 특정 덱 아님) |
| 코드시각화 aria 라벨 전량 | verify_deck.py:1612 | 접근성 | aria 누락 | 라벨이 있어도 시각화 자체가 있는지는 별도(위 1391) |
| callout 색 <3(색 남용) | verify_deck.py:1621 | 스타일·색 | 색 과다 | 내용 |
| `.hint-reveal`에 `<summary>` | verify_deck.py:1628 | 접근성 | 디스클로저 마크업 누락 | 내용 |
| 원고 아이콘(💬/🗣/👀) 누출 0 | verify_deck.py:1637 | 문법 | 강사 멘트 유출 | 내용 |
| `<br>` 직전 조사 종결 린트(WARN 전용) | verify_deck.py:1656 | 문법 | 줄바꿈 어색함 | 내용 |

**verify_deck.py 소계: 구조 16 · 경로·참조 3 · 문법 4 · 스타일·색 13 · 접근성 4 · 오버플로 0 · 내용 품질 0**
(하단 안내문 `verify_deck.py:1666` 자체가 "오버플로·콘솔에러·가독성은 브라우저 측정 필요"라고 명시 — 이 스크립트가 커버 안 함을 스스로 인정.)

### A.2 나머지 스크립트

| 스크립트 | 검사 성격 | 대표 검사 file:line | 분류 | 내용 품질 여부 |
|---|---|---|---|---|
| `scripts/verify_kit.py` | kit CSS 파일 존재·계약 | verify_kit.py:60,123-125,189 | 구조·스타일 | 0 |
| `scripts/verify_skill_setup.py` | Codex/Claude 스킬 진입점 경로 정합 | verify_skill_setup.py:32,35,463,465 | 구조·경로 | 0 |
| `scripts/verify_session_docs.py` | 리서치 5파일 스키마·구간수·항목수·출처ID 해소 | verify_session_docs.py 다수(예: check_research_result:163, check_practice:189, check_registry:246) | 구조(문서) | **자료(리서치) 단계 한정 내용 게이트 존재** — 개수 검사(구간 6개·항목 8개)이지 개념 정확성/깊이 아님 |
| `scripts/verify_research_chunks.py` | 개념KB 청크 깊이·G8 관점(사례/대안/한계)·인접비율 | check_chunk_depth:255, check_week_breadth:354, DOMAIN_SHARE_MAX:52(analyze_agent_usage.py) | **내용 품질(자료 단계)** | **덱에는 대응물 없음** — 리서치 청크의 "관점 다양성"을 재는 유일한 실질 내용 게이트지만 대상이 개념KB 텍스트지 완성된 슬라이드가 아님 |
| `scripts/analyze_agent_usage.py` | 워커 도구·모델 감사(하네스 규율) | section_tool_audit:923 | 구조(프로세스) | 0 |
| `tests/test_deck_pipeline.py` | assemble/inject 파이프라인 기계적 정합(36개 중 다수) | test_missing_marker_and_no_parts_fail:77, test_note_title_mismatch_aborts:261 | 구조 | 0 |
| `tests/test_image_pipeline.py` | 이미지 전처리·인라인·registry 계약 | test_rgba_alpha_and_registry_failures_are_detected:67 | 구조·경로 | 0 |
| `sessions/_verify/1주차/강의덱_발표.meta.json` | 발표자노트 주입 메타 사이드카(데이터, 검사 아님) | — | — | 0 |

**헤드라인: 8개 검증 스크립트 + 2개 테스트 파일 = 약 120개 개별 검사 중 "완성된 슬라이드의 내용 품질"을 재는 검사는 0개.** 유일한 내용형 게이트(`verify_research_chunks.py` G8)는 리서치 산출물(자료 단계)에 있고 덱(조립 단계)에는 대응 게이트가 없다.

## B. 게이트 실제 실행 — 통과 실증

| 명령 | 종료코드 | 요약 |
|---|---|---|
| `verify_deck.py sessions/2주차/강의덱.html --parts 8` | **0** | FAIL 1(part-divider 6≠8 — divider 수 계약 자체가 `--parts 8` 인자와 안 맞는 사용법 오류이지 내용 결함 아님) · WARN 1(`<br>` 조사 린트) · **PASS 47** |
| `verify_deck.py sessions/1주차/강의덱.html --parts 8` | **0** | FAIL 1(동일 원인) · WARN 5 · **PASS 51** |
| `verify_session_docs.py 2 --target 자료` | **0** | FAIL 0 · WARN 0 · PASS 32 · SKIP 1 · `RESULT | PASS` |
| `verify_research_chunks.py 2` | **0** | FAIL 0 · WARN 0 · PASS 71(청크 60개) · `RESULT | PASS` |
| `python -m unittest tests.test_deck_pipeline tests.test_image_pipeline` | **0** | `Ran 36 tests ... OK`(출력 중 보이는 "[FAIL]"·"[FAIL] 출력 경로..." 문자열은 테스트가 의도적으로 유발한 실패 케이스의 콘솔 로그이지 unittest 실패 아님 — 최종 `OK`) |

2주차 덱은 위 **모든 자동 게이트를 exit 0(그린)** 으로 통과했다. `--parts 8` FAIL은 사용 인자(`--parts`)가 실제 파트 수(6)와 다르게 호출됐을 때만 나오는 것으로, W1·W2 동일하게 뜨는 계약-사용 오류이며 내용 품질과 무관하다.

## C. 왜 통과했는가 — 증상별 메커니즘

| 증상 | 담당했어야 할 게이트 | 실제 결과 | 구조적으로 못 잡는 이유 |
|---|---|---|---|
| 1) 저밀도 설명 슬라이드 | (없음. R-DENS-01은 조건부 로드 phase 문서일 뿐 verify 스크립트 아님) | PASS | `references/phases/04-조립.md:64`는 **저작 시점 가이드 텍스트**이지 `verify_deck.py`가 파싱·검증하는 대상이 아니다. 텍스트 글자수를 세는 코드 자체가 verify_deck.py에 없다. |
| 2) 제목+한문장 슬라이드 반복 | 없음 | PASS | verify_deck.py는 슬라이드별 body 텍스트 길이/문장수를 추출하지 않는다(전체를 스캔하는 건 색·클래스·존재여부 정규식뿐, verify_deck.py:1017-1656 어디에도 텍스트 length 계산 없음). |
| 3) 큰 카드에 짧은 라벨 | R-BOX-01/01a·R-BOX-02(저작 규칙, `references/phases/04-조립.md:67-74`) | PASS | 카드 크기 대비 텍스트 비율은 렌더된 박스 치수(브라우저 layout)가 있어야 계산 가능한데, verify_deck.py는 DOM 렌더를 하지 않고 문자열 정규식만 본다. |
| 4) 설명단위 과잉 분절 | 없음 | PASS | "의미 단위"는 문장/개념 경계에 대한 판단이 필요해 정규식으로 셀 수 있는 대상이 아니다(현재 어떤 스크립트도 시도하지 않음). |
| 5) 시각자료가 카드로 대체(덱 `<img>` 0개) | `verify_deck.py:1277`(시각 자료 구성 카운트), `:1293-1328`(이미지 배선) | **PASS**(`시각 자료 구성: 코드 시각화 15 · 이미지 0`) | 1277은 이미지 수를 **보고만** 하고 0이어도 FAIL 조건이 없다(`chk` 호출이 `results.append(("PASS", ...))` 고정 — verify_deck.py:1277). 1293-1328의 배선 검사는 매니페스트에 등재된 슬롯만 검사하는데, 매니페스트 자체에 이미지 슬롯이 없으면(2주차 자료가 이미지 없이 설계됨) 검사할 항목이 0건이라 자동 PASS. |
| 6) 장수 증가에도 깊이 미증가(75→108장) | 없음 | PASS | 장수 상한/깊이 비율 검사가 존재하지 않는다. `chk(n >= 5, ...)`(verify_deck.py:1017)는 하한만 있다. |
| 7) 빈·거의 빈 컨테이너 | 없음 | PASS | 컨테이너 내부 텍스트 유무를 확인하는 코드가 verify_deck.py에 없다(가장 가까운 것은 이미지 배선 검사뿐이며 텍스트 카드는 대상 밖). |
| 8) 동일 레이아웃 반복 | `verify_deck.py:1391`(다양성≥6종), `:1395`(최장연속≤2) | **형식상 PASS**(21종/최장2) | 이 게이트는 "레이아웃 클래스 문자열의 국소 연속"만 보고 문턱이 낮다(6종은 108장 규모에서 자명하게 넘음). 같은 family가 듬성듬성(연속 아니게) 반복되는 "전체 반복률"은 측정하지 않는다 — 예: `same_family_adjacent_ratio`(병렬 감사 JSON, W2=0.140 vs W1_FINAL=0.095)처럼 인접 외 반복은 시야 밖. |

## D. 분포 측정 — 임계값 근거

`reports/create-slides-quality/deck_quality_metrics.json`(병렬 감사 산출, 4개 코퍼스: W1_INITIAL/MID/FINAL·W2_CURRENT, `html.parser` 기반 파서, 12건 표본 대조로 분류 정밀도 스팟체크 11/12 일치)를 1차 근거로 쓰고, 그 파일에 없는 유형별 세부는 본 감사가 별도로 `sessions/1주차/강의덱.html`·`sessions/2주차/강의덱.html`을 정규식 파서로 재계산했다(스크립트: 스크래치패드 `measure_slides.py`, 108/75장 모두 verify_deck.py 카운트와 일치 확인됨).

### D.1 개념설명(설명) 슬라이드 본문 글자수 — W1_FINAL vs W2_CURRENT (병렬 감사 JSON `aggregates`)

| 코퍼스 | n | p10 | p25 | median(p50) | p75 | p90 |
|---|---|---|---|---|---|---|
| W1_FINAL(정본, 75장 중 43장 설명) | 43 | 75.6 | 126.0 | 156 | 197.5 | 272.6 |
| W2_CURRENT(108장 중 37장 설명) | 37 | 53.6 | 61.0 | 70 | 91.0 | 119.6 |

W1_FINAL의 `low_density_ratio`(저밀도 판정 비율) = **0.163**(16.3%) vs W2_CURRENT = **0.865**(86.5%) — 같은 저밀도 판정 규칙을 두 덱에 그대로 적용했을 때 5배 이상 격차.

### D.2 임계값 후보와 트레이드오프 (본 감사 자체 계산, 개념설명 유형 한정)

| 후보 임계값(글자수 미만 FAIL) | 근거 | W1_FINAL 플래그율 | W2 플래그율 |
|---|---|---|---|
| 86 (W1_FINAL 유사 p10대) | 최소침습 | 6/56=11%(본 감사 자체 파서 기준, n다름 주의) | 19/36=53% |
| 100 | 완충 | 6/56=11% | 24/36=67% |
| **113.5**(병렬 감사가 채택 — W1_FINAL p15) | "제목+한문장" 판정 임계, `deck_quality_metrics.json:threshold_title_one_sentence_chars` | 낮음(설계상 15%) | 훨씬 높음 |
| 120 | 관대 | 7/56=12% | 31/36=86% |
| 144(W1_FINAL 자체 파서 median 근접) | 과공격 | 14/56=25% | 32/36=89% |

**주의**: 본 감사 자체 파서(공백 제거 문자수, 태그 전체 스트립)와 병렬 감사 파서(leaf-text 기준, container 감지 룰 다름)의 절대 글자수는 다르다(예: 본 감사 W1 개념설명 median=174 vs 병렬 감사 156) — 두 파서 모두 **"W1_FINAL 대비 W2가 현저히 낮다"는 방향과 배율(약 2배)은 일치**하므로 임계값의 존재 근거는 견고하나, 절대 숫자는 채택한 파서에 종속적임을 명시한다. 실제 채택 시 병렬 감사가 이미 산출한 `deck_quality_metrics.json`의 파서·수치를 정본으로 쓸 것을 권고(스팟체크로 정밀도 검증됨).

같은 규칙(1문장·짧은 제목형) 비율: W1_FINAL `title_one_sentence_ratio`=0.093(4/43) vs W2_CURRENT=0.081(3/37) — **이 지표는 W1/W2 차이가 작다**(둘 다 낮음). 즉 "제목+한문장" 자체는 W2에서 두드러진 증상이 아니고(W1_MID가 오히려 0.022로 가장 낮았다가 W1_INITIAL은 0.35로 높았음), 실제 W2 문제는 "제목+한문장"이 아니라 "카드가 여러 개인데 각 카드가 텍스트 없이 거의 비어 있음"(§C 증상 7)에 가깝다 — `empty_container_total`: W1_FINAL=39 vs **W2_CURRENT=79**(거의 2배), `worst_12_w2_slides` 표본(예: `C1-7` 카드 8개 중 각각 <10자, `deck_quality_metrics.json:worst_12_w2_slides[0]`)이 이를 뒷받침한다.

## E. 제안 검증 계약 (요지 — 상세 근거는 파일 본문 참조)

| Rule ID | 측정 | 임계값(근거) | 심각도 | 오탐 위험 | 예외 유형 |
|---|---|---|---|---|---|
| R-QC-01 | 유형별 설명 슬라이드 본문 글자수 | 개념설명 <54자(W2 자체 p10 근사, 완충) → WARN / <구간 미달 다수 시 파트 단위 FAIL 검토 | WARN | 코드 시각화/스크린샷이 텍스트를 대신하는 슬라이드 오탐 가능 | screen-operation(R-DENS-01a), 시각자료 role=explanatory 보유 슬라이드 |
| R-QC-02 | 설명 슬라이드 의미 블록 수 | ≥2개 컨테이너(W1_FINAL median_containers_explanation=4, W2=3 — 완만한 하한) | WARN | 의도적 단일-메시지 슬라이드 오탐 | 표지/전환/요약 |
| R-QC-03 | 거의 빈 컨테이너 탐지 | 같은 클래스 형제 ≥2 & 텍스트 <10자 & `<img>`/`<svg role>` 없음(병렬 감사 정의 그대로) | WARN(픽스 제안까지, FAIL 아님) | 의도적 아이콘-only 카드 오탐(병렬 감사가 이미 "empty-image-slot"을 별도 분리해 이 위험을 줄임) | `-slot` 클래스, 이미지 role 보유 |
| R-QC-04 | 카드 면적 대비 콘텐츠 | — | **사람검토**(자동화 불가, 아래 F 참조) | 매우 높음(DOM 렌더 없이 신뢰 불가) | 전체 |
| R-QC-05 | 동일 레이아웃 전체 반복률 | `same_family_adjacent_ratio` 상한 후보 0.15(W1_FINAL=0.095 근접, W2=0.140은 근접 미달로 판정력 약함 — **가장 약한 후보, 재검토 필요**) | WARN | 정당한 연작 레이아웃(work-step 등) 오탐 | `data-series` 연작 예외(기존 verify_deck.py:1395 관례 준용) |
| R-QC-06 | 제목+한문장 슬라이드 연속 | 연속 2장 이상 | WARN | D.2 확인상 W1/W2 차이가 작아 **판별력 낮음 — 채택 보류 권고** | 표지/전환 |
| R-QC-07 | 설명 단위 과잉 분할 | — | **사람검토**(의미 경계 판단 불가) | 매우 높음 | 전체 |
| R-QC-08 | 설명 기능 시각자료 최소 비율 | 개념설명 슬라이드 중 `visuals_explanatory>0` 비율 ≥10%(W1_FINAL 42/75=56% vs W2 15/108=14% — 완충 하한) | WARN | 텍스트만으로 충분한 개념 오탐 | 실습/전환/표지 |
| R-QC-09 | 실습 슬라이드 완결성(행동·입력·완료기준) | 3필드 키워드 존재 여부(정규식 라벨 매칭 가능 — verify_session_docs.py의 3필드 패턴 재사용) | WARN | 키워드 표현 다양성으로 오탐 큼 | — |
| R-QC-10 | 초안→덱 내용 보존율 | — | **사람검토**(초안 자유서술 vs 덱 표현 변형을 텍스트 매칭으로 신뢰 판정 불가) | 매우 높음 | 전체 |

## F. 구현 형태 (요지)

- **신규 `scripts/verify_deck_quality.py`로 분리** 권고. `verify_deck.py`가 이미 1671줄/93KB로 단일 관심사(구조+스타일+접근성)를 넘겼고, 성격이 다른 "텍스트 의미량" 검사를 섞으면 유지보수·오탐 튜닝이 더 어려워진다.
- CLI: `verify_deck_quality.py <deck>.html --parts N [--week N]`, 종료코드는 기존 관례(`verify_session_docs.py`/`verify_research_chunks.py`와 동일하게 FAIL 있으면 1) 준용하되, **R-QC 전체를 1단계에서는 WARN 전용으로 시작**(exit 0 유지)해 회귀 오탐으로 기존 파이프라인을 막지 않는다.
- 저작 시점 강제는 `references/phases/04-조립.md`(R-DENS-01 옆)에 R-QC 대응 문턱을 명시하고, `AGENTS.md`의 "작업 전 필수 읽기"에 04-조립.md가 조건부 로드임을 감안해 **항상 로드되는 루트 `SKILL.md`에 1줄 포인터**를 추가해야 실효성이 있다(현재 04-조립.md는 always-load 밖).

## 확인불가 항목

- `deck_quality_metrics.json`을 만든 병렬 감사의 원본 파서 스크립트(`analyze_decks.py`, `deck_quality_analysis.md` 서술본)는 이 세션의 스크래치패드 밖에 있어 원문을 읽지 못했다(json의 자체 caveats 절만 인용).
- 브라우저 렌더 기반 카드 실면적·overflow는 로컬 HTTP 서버+JS 측정이 필요해 본 감사(읽기 전용, 서버 기동 없음) 범위에서 실측하지 않았다.
