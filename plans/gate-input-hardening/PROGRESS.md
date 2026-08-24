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
| P1 0판정 가드 + 미판정 명시 | 대기 | — |
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
