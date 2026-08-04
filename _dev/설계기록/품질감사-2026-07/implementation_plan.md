# 2주차 저밀도 구현 계획

`root_cause_decision.md`의 판정을 전제로 한다. 시스템 수정(A, 모든 주차 공통)과 2주차 한정 수정(B)을 분리하고, 하지 않는 것(C)과 실행 순서(D)를 규정한다.

## A. 시스템 수정 (모든 주차 공통)

| 변경 항목 | 근본 원인 | 수정 파일 | 예상 효과 | 회귀 위험 | 검증 방법 |
|---|---|---|---|---|---|
| A1. 신규 완성 덱 내용 품질 게이트(R-QC-01~09) | H1 — `verify_deck.py` 1671줄 중 내용 품질 검사 0개(`validation_gap_report.md` §A.1) | 신규 `scripts/verify_deck_quality.py`(기존 `verify_deck.py`와 분리 — 이미 1671줄/93KB로 단일 관심사를 넘김, `validation_gap_report.md` §F) | 저밀도 설명 슬라이드·빈 컨테이너·시각자료 부족을 자동 검출 | 임계값을 발명하면 오탐 폭증 → 반드시 W1_FINAL 분포에서 도출(임계값 근거: `validation_gap_report.md` §D, `deck_quality_metrics.json`) | 1단계는 R-QC 전체 WARN 전용(exit 0 유지)로 시작해 기존 파이프라인을 막지 않음(`validation_gap_report.md` §F) |
| A2. 신규 초안 .md 단계 밀도 게이트 | H5 — 2주차는 `.md` 초안 단계에서 이미 저밀도(본문 중앙값 63자, W1최종 122자의 51.6%, `content_pipeline_audit.md` §C) | 신규 `scripts/verify_draft_quality.py`(슬라이드당 본문 글자수·정보 단위 수·노트:본문 비율·교시당 장수 규약 검사) | 결함 발생 지점(계획 직후, 조립 이전)에서 가장 싸게 잡는다 | 정보 단위 판단은 완전 자동화 불가 — 정량 지표(글자수·행수)는 자동, 의미 판단은 사람검토 유지(`validation_gap_report.md` E "R-QC-04·07·10 사람검토") | `2주차_초안.md` 수정 전/후 재실행, W1_FINAL 초안과 분포 비교 |
| A3. 필수 산출물 누락 검출 | H5·H8 — 2주차에서 `콘텐츠_집필노트`·`이미지-에셋.json`·`이미지-프롬프트.md`·`콘텐츠_리뷰.html`가 전부 부재했는데 이를 잡는 게이트가 없어 결함이 무저항 통과(`history_baseline_report.md` §E; `artifact_manifest.md` §D "핵심 공백") | `scripts/verify_session_docs.py` 또는 `verify_deck_quality.py`에 산출물 존재 검사 추가 | 2주차 실패가 보이지 않았던 단일 최대 이유를 제거 | 선택 산출물(발표본·배포본)까지 강제하면 과잉 — `sessions/README.md`의 필수/선택 구분을 그대로 따름 | 신규 주차 파이프라인 실행 후 필수 산출물 체크리스트 자동 리포트 |
| A4. `skills/콘텐츠/SKILL.md` 규칙 강화 | H5 — ⚠️ 2026-07-27 정정: 이탈 기제는 "106장/17.7장 역산"이 아니라 `2주차_최종수정계획.md:13`이 CORE(전원필수) 깊이를 270분에 맞춰 의도적으로 얕게 규정한 것. 전원 필수는 73장(`:16`)이고 교시당 CORE는 13·13·8·13·12·13(`:113-118`)로 스킬 관례(8~11장, `skills/콘텐츠/SKILL.md:75`)를 완만히 이탈, `:120`이 적어 둔 완화 밸브(교시 병합·CORE→FLEX 강등)가 미실행됐고 사유 기록 의무(집필노트)도 이행되지 않음(`content_pipeline_audit.md` Q3, `root_cause_decision.md` 「정정 이력」) | `skills/콘텐츠/SKILL.md` | ① 장수는 시간예산 역산이 아니라 설명 단위에서 결정(안티패턴 명시) ② 교시당 장수 규약 이탈 시 사유 기록 강제 ③ 화면:노트 배분 규칙(주장은 화면, 비유·근거·예시 중 최소 하나는 화면에 남긴다) ④ 부록 강등 금지 대상(예시·근거·주의점은 강등 불가, 심화만 강등 가능) ⑤ 필수 계층(CORE) 깊이를 시간예산에 맞춰 깎지 않는다(R-PLAN-02 신설 — 실제 기제에 대응) | 규칙 추가로 기존 정당한 화면조작 예외(R-DENS-01a)를 침해하지 않도록 예외 조항 유지 필수(`content_pipeline_audit.md` §A) | `tests/test_quality_gates.py`(A7)로 회귀 고정 |
| A5. 루트 `SKILL.md`에 R-DENS-01 always-load 포인터 추가 | H3 — 밀도 하한이 always-load 구 SKILL.md(180줄)에서 조건부 로드 `references/phases/04-조립.md:64`로 이동, ★필수 표기 0건화(`skill_pipeline_audit.md` §A, §C; `FINAL_REPORT.md:83,85`) | 루트 `SKILL.md` | 조건부 로드로 밀려난 밀도 규칙의 가시성 복원 | 최소 침습(1줄 포인터) — 본문 복제 금지(중복 규칙은 리팩터 이전으로 회귀) | `SKILL.md` 라인 diff 리뷰 + `skill_pipeline_audit.md` §A 표의 "밀도 하한 없음" 행이 해소됐는지 재조사 |
| A6. 1주차 인간 보정 원리의 규칙 승격 | H4 — 1주차 주요 수정 5건 중 스킬 환류 1건뿐. PART6 재설계(`fe695a7`/`6b96119`/`c20c10f`)는 `verify_deck.py` 슬라이드 총수 상수만 갱신, 일반 규칙 미승격(`history_baseline_report.md` §D) | `skills/콘텐츠/SKILL.md`·`references/phases/04-조립.md`·`.agents/agent-memory/create-slides/MEMORY.md` | ① 중복 절차 슬라이드는 병합한다 ② 실습 슬라이드는 하위 동작마다 step-card를 준다(한 문장으로 압축 금지, `slide_trace_report.md` STEP6 S45 패턴) ③ 개념 슬라이드는 컨테이너당 완결 문장을 담고 컨테이너 3개 이상을 목표로 한다(`deck_quality_analysis.md` §9 W1_FINAL 모범 패턴) | 과도한 일반화 시 정당한 미니멀 사례(C2-8 등)를 오탐 처리할 위험 — 화면조작·의도된 시각화 대체 예외 명시 | 신규 게이트가 W1_FINAL 모범 슬라이드 5선(`deck_quality_analysis.md` §9)을 PASS시키는지 회귀 확인 |
| A7. `tests/test_quality_gates.py` 신설 | 전체 — 게이트 신뢰성 자체 보증 | 신규 테스트 파일 | 신규 게이트가 수정 전 2주차를 실제로 탐지하고 1주차 최종본은 통과시키는지 회귀 고정 | 테스트 자체가 임계값에 종속 — A1/A2 임계값 변경 시 함께 갱신 필요 | `python -m unittest tests.test_quality_gates` |
| A8. `.agents/agent-memory/create-slides/MEMORY.md` 갱신 | H4 — 미해결 항목·누적 규칙 정합 | `MEMORY.md` | 이번 감사에서 승격된 규칙(A4~A6)과 신규 게이트(A1~A3) 존재를 기록해 다음 주차가 같은 실수를 반복하지 않게 함 | 과거 미해결 항목 중 이미 해소된 것을 남겨두면 다음 세션이 재조사 낭비 — 해결 확인 후 삭제 | `AGENTS.md` "작업 전 필수 읽기" 절차대로 `## 미해결` 재확인 |

## B. 2주차 한정 수정

| 변경 항목 | 근본 원인 | 수정 파일 | 예상 효과 | 회귀 위험 | 검증 방법 |
|---|---|---|---|---|---|
| B1. 저밀도 개념 슬라이드 재밀도화 | H5 — 노트:본문 비율 W2 1.20 vs W1 0.31(`slide_trace_report.md` Q2), 이미 노트에 있는 비유·근거·예시(노트 총 8,298자, `content_pipeline_audit.md` Q2)를 화면으로 승격 | `sessions/2주차/강의덱.초안/part-NN.html` shard | 저밀도 설명 슬라이드(§7 최저밀도 12선, `deck_quality_analysis.md`) 개선 | **새 사실 창작 금지**, 자료·노트에 있는 내용만 사용 | A1 게이트 재실행 + 회귀 diff(조립 전 사본과 대조) |
| B2. 부록 33장 중 예시·주의점·근거 재통합 | H5 — CORE/FLEX/REC 분류가 예시(7)·주의점(8)·근거(1) 계열을 체계적으로 CORE 밖으로 밀어냄(`content_pipeline_audit.md` §F, Q4) | `sessions/2주차/2주차_초안.md`(FLEX/REC 표기 재분류) → shard 재반영 | 16장(예시7+주의점8+근거1)을 본류로 재통합하거나 관련 CORE 슬라이드에 병합 | 심화(11건) 강등은 유지 — 과도한 부록 해체는 270분 시간예산과 충돌 가능 | `2주차_최종수정계획.md` 장수 배분과 재조정 정합 확인 |
| B3. 과잉 분할 병합 | H5 — 슬라이드 수만 68% 증가(63→106)하고 본문 총량은 오히려 감소(8,611→6,755자, `content_pipeline_audit.md` Q2) | shard | 한 설명 단위가 쪼개진 구간을 합침 | 병합 후 슬라이드 수가 `deck.contract.json` 계약과 어긋나지 않도록 재조정 | `verify_deck.py` 구조계약 재통과 확인 |
| B4. 미구현 시각자료 구현 | H8 — 개념KB "PPT 소재"가 지정했으나 구현 안 된 4항목: 강수확률/CB Insights 차트(C1-4), 자판기 vs 주방 대조(C1-9), 자체점검 vs 사용자테스트 2열표(C6-1), 한줄정의 vs 슬로건 2열 대조표(C1-6)(`slide_trace_report.md` STEP5) | shard(CSS/SVG 다이어그램 추가) | 설명 기능 시각자료 W2 15개 → 확충(W1최종 42개 참고치, `deck_quality_analysis.md` §3) | 이미지 파이프라인 산출물이 없으므로 실제 이미지가 아니라 CSS/SVG 다이어그램으로 구현 — 신규 이미지 자산 파이프라인을 임기응변으로 새로 만들지 않음 | 신규 viz 요소 `kit/charts/catalog.html` 등재 여부 확인 |
| B5. shard 우선 수정, 조립은 스크립트로 | 운영 규칙 — `강의덱.html`은 생성물, `part-NN.html`이 정본(`AGENTS.md` "⚠️ sessions/N주차/강의덱.html은 생성물이다") | `sessions/2주차/강의덱.초안/part-NN.html` → `python scripts/assemble_deck.py sessions/2주차/강의덱.초안` | 직접 수정으로 인한 유실 방지 | 덱 직접 수정 금지 위반 시 다음 조립 때 전량 유실(`deck-html-is-generated-edit-shards` 메모리 기록 사고 사례) | 조립 후 조립 전 사본과 diff |
| B6. 변경 전 백업 | 운영 안전장치 | `sessions/2주차/강의덱.html` 등 조립 전 사본 | 잘못된 수정의 복구 지점 확보 | 없음 | 백업 파일 존재 확인 |

## C. 하지 않는 것

- 1주차 산출물 일절 수정 금지(2026-07-26 사용자 결정으로 동결, `AGENTS.md` "1주차는 구세대 산출물만 폐기됐고 현행 산출물은 정본이며 … 동결됐다").
- 글자 수를 늘리기 위한 문장 부풀리기·사실 중복 금지.
- 자료·노트에 근거가 없는 내용 창작 금지.
- 기존 테스트·게이트 완화 또는 임계값 조작 금지.
- 특정 주차 하드코딩 금지.
- 장수를 목표 숫자에 맞추기 금지(장수는 설명 단위의 결과 — H5가 지적한 "시간예산 역산" 안티패턴의 재발 방지).

## D. 실행 순서

1. A1~A3, A7 (게이트 신설 + 회귀 고정) → 독립 검토
2. A4~A6, A8 (규칙 환류) → 독립 검토
3. 2주차 표본 재생성(대표 슬라이드 묶음) → 품질·회귀 이중 검토 게이트
4. 통과 시에만 B1~B6 전체 적용
5. 최종 전수 품질 검사 + 독립 회귀 감사
