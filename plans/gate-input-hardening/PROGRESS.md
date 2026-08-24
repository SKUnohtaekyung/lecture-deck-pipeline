# 진행 상태 — 게이트 입력 결합·미탐 해소

> 계획 정본은 `PLAN.md`. **이 파일에만 실행 결과·상태를 쓴다**(계획서는 수정하지 않는다 — 2026-08-24 승인 시 보강 2건만 예외로 반영 완료).
> 착수 승인: 2026-08-24 사용자. G1=(a) · G2=(a) · G3·G4·G5 권고안 확정.

## 기준선 (2026-08-24 · 어떤 변경도 하기 전)

**모든 Phase의 통과 조건**: 아래 수치가 before/after 완전 동일. 달라지면 그 Phase는 실패 — 되돌리고 보고.

| 대상 | 기준선 |
|---|---|
| `run_deck_checks.py 1주차` | **exit 0** · verify_deck FAIL 0·WARN 7·PASS 53 · 품질 FAIL 0·WARN 7·PASS 7 · 구조 WARN 래칫 8≤8 · 품질 WARN 래칫 7≤7 |
| `run_deck_checks.py 2주차` | **exit 0** · verify_deck FAIL 0·WARN 1·PASS 59 · 품질 FAIL 0·WARN 8·PASS 6 · 구조 WARN 래칫 2≤2 · 품질 WARN 래칫 8≤8 |
| `run_deck_checks.py 3주차` | **exit 0** · verify_deck FAIL 0·WARN 1·PASS 59 · 품질 FAIL 0·WARN 5·PASS 9 · 구조 WARN 래칫 1≤1 · 품질 WARN 래칫 5≤5 |
| 회귀 10모듈 | **Ran 231 tests · OK · exit 0** |
| `verify_skill_setup` / `verify_kit` / `verify_subject_isolation` / `verify_declared_vs_enforced` / `verify_contract_waivers` | 전부 **exit 0** |
| 스파이크 대조군(3주차 덱 standalone `--parts 6`) | FAIL 0 · WARN 1 · PASS 61 |

원본 출력 보관: `tmp/hardening/baseline/`(휘발 — 수치 정본은 이 표다).

⚠️ 러너 안의 `verify_deck` PASS 계수(53/59/59)는 standalone 실행(61)과 다르다 — 호출 인자가 달라서다. **비교는 러너↔러너, standalone↔standalone으로만 한다.**

---

## Phase 상태

| Phase | 상태 | 커밋 |
|---|---|---|
| P0 경로 층 전제 통일 | **완료** | (아래 기록) |
| P1 0판정 가드 + 미판정 명시 | **완료 · 사용자 판정 1건 대기** | (아래 기록) |
| P2 테마 선언 축 신설 | 대기 | — |
| P3 집행부 테마 파라미터화 | 대기 | — |
| P4 뮤테이션 매트릭스 회귀 승격 **판정만** | 대기 | — |

---

## 실행 기록

### P0 — 경로 층 전제 통일 (2026-08-24 · solo)

**한 것**

| 항목 | 파일 | 내용 |
|---|---|---|
| P0-1 | `scripts/_course_paths.py` | `AmbiguousCourseError` + `resolve_course()` 신설. 전 함수에 `course=` 파라미터. 우선순위 = 인자 → 환경변수 `CREATE_SLIDES_COURSE` → 과목 1개일 때 그것. 모호하면 **예외**. `sessions_roots`는 현행 유지 |
| P0-1b | 〃 | `profile_paths()` 신설 — «전부 훑는» API. 전수 순회 API가 없어서 격리 검사가 자멸했다 |
| P0-2 | `scripts/verify_subject_isolation.py` | `discover_profiles()`로 **과목 전수 순회**. 프로필 0개면 SKIP+exit 0 → **FAIL(exit 2)**. 검사 과목 수·과목별 리터럴 수를 출력에 노출 |
| P0-3 | `scripts/hook_slide_guard.py` | `mode_course`가 편집 경로 `courses/<과목>/`에서 과목을 유도. 실패 시 **침묵 대신 관측 로그**(`course/no-guide`). 차단은 하지 않는다(훅이 도구 호출을 깨지 않게) |
| P0-4 | `scripts/run_deck_checks.py` | 자식 stderr 마지막 **3줄** 출력(종전 1줄) — 다줄 예외의 헤드라인이 잘려 원인이 사라졌다 |
| 회귀 | `tests/test_course_paths.py` **신설 16건** | 과목 1개 불변 4 · 다과목 시끄러운 실패 10 · 격리 검사 생존 2 |
| 문서 | `README.md` · `references/검증-명령-지도.md` | 회귀 **10모듈 → 11모듈**, 신설 사유 등재 |

**고의 위반 증명 (실제 저장소에 2번째 과목을 만들어 관측 후 제거)**

| 관측 | 결과 |
|---|---|
| `verify_subject_isolation` | **exit 0 · 「검사 과목 2개」**(리터럴 9+1=10종) — 두 과목 다 검사. 종전엔 SKIP→exit 0(0개 검사)로 자멸 |
| 하위 스크립트(`verify_deck_quality`·`check_title_survival` 등) | **exit 1 + 원인 메시지 전문**(「과목이 2개라 어느 것인지 알 수 없다: [...] → course= 또는 CREATE_SLIDES_COURSE=」) |
| `run_deck_checks 3주차` | **exit 1**. 러너의 기존 「계수 실패(눈먼 0 방지)」 가드가 정확히 발화 |
| `verify_deck 3주차` | exit 0 · **요약 FAIL 0·WARN 1·PASS 61** — 판정 수 유지, 조용한 생략 없음(덱 경로를 직접 받아 과목 모호성에 걸리지 않는다) |
| `CREATE_SLIDES_COURSE=바이브코딩` 지정 시 | 러너·검사기 전부 **exit 0 복귀** — 14개 스크립트에 `--course`를 달지 않고도 다과목을 돌릴 수 있는 이행 경로 확인 |

**불변 검증 (통과 조건)**

- 러너 1·2·3주차 **exit 0 · 판정 줄 diff 0**(요약·래칫·RESULT 전량 동일)
- 회귀 **247 tests OK**(기준선 231 + 신설 16)
- `verify_skill_setup`·`verify_kit`·`verify_subject_isolation`·`verify_declared_vs_enforced`·`verify_contract_waivers` 전부 exit 0
- 산출물 변경 0건

**P1으로 넘기는 발견 (P0 실행 중 관측)**

- ⚠️ **러너 품질 래칫이 「죽은 검사기」를 「개선」으로 읽는다.** 2과목 상태에서 `verify_deck_quality`가 죽자 WARN 0이 세어졌고, 래칫이 「품질 WARN 0 ≤ 베이스라인 5 — **개선됨: 베이스라인을 0로 낮춰 등재 가능**」을 출력했다. 그 단계 자체는 FAIL이라 전체 exit는 1이지만, **베이스라인을 낮추라는 권고가 크래시에서 나온다.** 계수 실패와 진짜 0을 구분해야 한다 — P1-1 대상에 추가.

### P1 — 0판정 가드 + 미판정 명시 (2026-08-24 · 하네스: 메인 + Sonnet 워커 3기 파일 disjoint)

**메인 담당분** (커밋 `5e014b9`)

| 파일 | 고친 것 |
|---|---|
| `run_deck_checks.py` | ① 덱에서 슬라이드 **0장**을 세면 장수 대조가 통째로 스킵됐다(조건이 falsy 0을 걸러냄) → 계수 실패 FAIL. ② 품질 WARN 버킷에만 계수실패(None) 경로가 없어 **검사기가 죽어 생긴 0을 「개선됨 — 베이스라인을 0으로 낮춰 등재 가능」**으로 권고했다 → struct와 대칭으로 |
| `verify_deck.py` | 계약 키 부재 시 **한 줄도 없이 사라지던** 검사를 「미판정 N건」으로 노출. 판정 계수(FAIL/WARN/PASS)에는 넣지 않아 러너 래칫 불변 |
| `AGENTS.md` | 미탐 절에 집행 1행 — 「판정·미판정 계수를 출력한다 / 대상 0은 통과가 아니라 미판정 / 미판정은 계수 채널에 넣지 않는다」 |
| 회귀 | `test_deck_pipeline` +4(계수실패≠개선 · 눈먼 슬라이드계수) · `test_deck_contract` +2(미판정 노출 · 계수 오염 없음) |

**드러난 것 — 그동안 조용히 미수행이던 검사 5개**: 1주차 `must_keep` · 2주차 `dark_terminal_slides`·`closing_text`·`must_keep` · 3주차 `dark_terminal_slides`.

**워커 담당분** (파일 9개 · 전부 「계수 실패(눈먼 0 방지)」 기존 어휘 재사용)

| 워커 | 파일 | 가드 기준(정당한 0과의 구분 신호) |
|---|---|---|
| A-1 | `verify_notes.py` | `entries` 0건인데 `<h2>`는 있음 |
| A-1 | `verify_report_freshness.py` | 보고 파일 매치 0건인데 같은 범위에 식별자 신호(`**N장**`+sha256 / `[시점 스냅샷]`) 존재 |
| A-1 | `verify_judgement_log.py` | 헤더 어휘 라우팅 실패했는데 상위 헤딩 breadcrumb에 「추적/출처」·「처분/재료」 힌트 존재 |
| A-2 | `verify_session_docs.py` | `used_chunks==0`인데 개념KB·원문 존재 |
| A-2 | `verify_draft_quality.py` | 교시/PART 인식 0건인데 콘텐츠성 `##` 헤더 존재 |
| A-2 | `verify_distributable.py` | `data-image-purpose/state`는 있는데 `asset-slot` 클래스 없음 (진단 전용 — `violations`에 넣지 않아 종료코드 불변) |
| A-3 | `inline_deck.py` | 〃 (전량 실측: 실물 figure 460개 중 해당 0건이라 독립 신호로 안전) |
| A-3 | `kb_extract.py` | `--blind`에서 코어 청크의 가림 판정/미판정 계수, 미판정>0이면 exit 1 |
| A-3 | `hook_slide_guard.py` | `CANDIDATE_HINT="강의덱"` 신설 — `TARGET_HINTS` 미매치인데 강의덱류로 보이는 경로를 **관측 로그로만** 기록(차단·주입 없음, `TARGET_HINTS`·`is_target` 무변경) |

**메인 반대신문 — 워커 보고를 읽지 않고 신호를 직접 봤다**

- `verify_notes` 독립 재현: 정상 `판정 78건·미판정 0건`(exit 0) / `pn-`→`zz-` 개명 사본 `OK=0/0 · 판정 0건·미판정 78건` **FAIL**(exit 1). 종전에는 `OK=0/0`이 그대로 통과였다
- `inline_deck` 실물 exit 0 · `image slots judged: 1` · `kb_extract 3 --blind` 실물 exit 0 · `verify_report_freshness`/`verify_judgement_log` 1·2·3주차 전부 exit 0 — **오탐 0**
- 훅 diff 직접 확인: `TARGET_HINTS`·`is_target()`·`mode_course`·`--enforce` 무변경(추가만 34줄)
- 워커 잔여물 정리: A-1이 남긴 `tmp/probe_copy` 없음, `tmp/guard-observations.jsonl`에 실제 관측 2건(휘발 경로라 보존)

**불변 검증**: 러너 1·2·3주차 **exit 0 · 판정 diff 0**(요약·래칫·RESULT 전량) · 회귀 **253 OK** · 정적 5종 exit 0 · 산출물 변경 0건.

**⚠️ 사용자 판정 필요 — 판정이 바뀐 유일한 지점 1건**

`verify_draft_quality 3주차` standalone 집계가 바뀐다(러너는 불변):

| | 구버전 | 신버전 |
|---|---|---|
| R-QD-04 | `[PASS] ✓ 모든 회차가 규약(8~11장) 범위 안 **(0개 구간)**` | `[WARN] △ [0판정가드:미판정] 교시/PART 인식 0건 — 콘텐츠성 ## 헤더 10개 있음` |
| 요약 | FAIL 2 · WARN 2 · **PASS 5** | FAIL 2 · **WARN 3** · PASS 4 |
| 종료코드 | 1 | 1 (불변) |

원인은 3주차 초안이 `PART-01`(하이픈)을 쓰는데 `_SECTION_NUM_RE`는 `PART \d+`(공백)만 본다는 것 — **R-QD-04는 3주차를 한 번도 판정한 적이 없다.**
⚠️ **엄격한 집계 불변과 이 미탐 수정은 원리적으로 양립하지 않는다** — 거짓 PASS 자체가 집계의 일부이기 때문이다. 되돌리려면 「0개 구간인데 PASS」로 복귀해야 한다.
선택지: (a) 현행 유지 — 미판정을 WARN으로 노출 **(권고)** (b) 계수 채널에서 빼고 비계수 「미판정」 줄로만(그래도 PASS 5→4는 남는다) (c) 되돌림 (d) 정규식을 `PART[-\s]*\d+`로 확장 — 단 이는 «가드 추가»가 아니라 «판정 범위 변경»이라 오탐률 실측이 선행이다.
