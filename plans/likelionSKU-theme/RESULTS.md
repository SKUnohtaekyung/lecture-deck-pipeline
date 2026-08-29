# likelionSKU 테마 등재 — 관문 실측 결과

> 실행 2026-08-29 · 브랜치 `feat/likelionsku-theme` · 이슈 [#2](https://github.com/SKUnohtaekyung/lecture-deck-pipeline/issues/2)
> 계획 정본 `PLAN.md` · 등재 조건 정본 `kit/guide/테마-계약.md` §4.
>
> **판정 줄과 종료코드는 실행 원문이다.** 통과하지 않은 것을 통과로 적지 않는다.
> 실행하지 못한 검증은 「실행하지 못한 검증」 절에 사유와 함께 적는다.

## ⓐ 뮤테이션 매트릭스 (계약 §4㉠) — 정상본 PASS ∧ 변형 4/4 검출 · 미탐 0

시험 덱 `tmp/theme-mutation/likelionSKU_시험덱/강의덱.html` (7장 · `--parts 1` ·
`styles/deck.css`의 `:root`를 likelionSKU 토큰으로 치환한 판본을 링크).
전 실행에 `CREATE_SLIDES_COURSE=likelionSKU`. 결함은 정상본 사본에 **하나씩만** 심었다.

### 정적 채널 — 종료코드

| 대상 | `verify_deck.py` | `verify_deck_quality.py` | 검출 |
|---|---|---|---|
| **정상본(대조군)** | **exit 0** · 요약: FAIL 0 · WARN 2 · PASS 44 | **exit 0** · 요약: FAIL 0 · WARN 1 · PASS 9 | — (대조군) |
| **V1** 본문 폰트 하한 미달 | **exit 1** · FAIL 0→1 | exit 0 | ✅ |
| **V2** 원고 아이콘 누출 | **exit 1** · FAIL 0→1 | exit 0 | ✅ |
| **V3** 내부 작업 라벨 누출 | exit 0 · WARN 2→3 | **exit 1** · FAIL 0→1 | ✅ |
| **V4** 빈 `asset-slot` | **exit 1** · FAIL 0→1 | **exit 1** · FAIL 0→2 | ✅ |

### 판정 줄 원문

```
V1  [FAIL] ✗ 세션 CSS .s-body/.s-lead 폰트 22px 미만: ['.s-body']
V2  [FAIL] ✗ 아이콘 마커 ['💬'] 최종 HTML에 잔존 — 학생 덱에서 제거하고 발표자 노트로 라우팅해야 함
V3  [FAIL] ✗ R-META-01: 메타 표기 잔존 슬라이드 1장(임계 0건 초과 시 플래그) — S02(TODO)
    (verify_deck 쪽은 설계상 WARN 전용) [WARN] △ R-META-01 내부 작업 라벨 후보 1건: ['S02:TODO']
V4  [FAIL] ✗ 이미지 계약 위반: explanatory slot is missing img
    [FAIL] ✗ R-QC-18: 빈 이미지 슬롯 1개/1장(임계 0개 — img/svg/canvas 없는 .asset-slot) — S04
```

⚠️ **V3의 검출 층을 정확히 적는다** — `verify_deck.py`의 R-META-01은 **설계상 WARN 전용**
(오탐 가능성 때문에 사람이 판단)이고, **종료코드로 막는 것은 `verify_deck_quality.py`**다
(`ALWAYS_FAIL = {R-QC-18, R-META-01, R-QC-08}`). 「검출됨」을 「exit 1」과 같은 말로 쓰지 않는다.

### 브라우저 채널 — 폰트 하한의 집행 정본

`scripts/audit_all.js`(뷰포트 1440×900 · `document.fonts.ready` + 이미지 로드 대기 ·
캐시버스터). 정본 근거: 정적 린트는 셀렉터 «이름»에만 의존해 판정 범위가 원리적으로 좁고,
집행 정본은 `audit_typography.js`의 `fontFloor`다.

| 대상 | `fontFloor` | byRole | INVALID | slideCount |
|---|---:|---|---|---:|
| 정상본 | **0** | `{}` | null | 7 |
| **V1** | **5** | `narrative<22: 5` (실측 20px · 하한 22px) | null | 7 |

정상본 렌더 결함: `below 1` · 나머지 11지표(off·occl·wb·ovf·slots·stretchX·stretchY·
ragged·lowFill·wideEmpty·hollow) 전부 **0**.

### 대조군을 깨끗하게 만드는 과정에서 나온 실측 2건 (게이트를 고쳤지 기준을 낮추지 않았다)

1. **클래스 없는 `<p>`가 브라우저 기본 16px로 떨어졌다** — 시험 덱 S05 카드 본문 3개(31~33자
   한국어 산문)가 kit 텍스트 클래스 없이 `<p>`로만 쓰여 **16px로 렌더**됐다. 정적 게이트는
   PASS였고(세션 CSS에 선언이 없으니 볼 것이 없다) **브라우저 감사만 잡았다**(`narrative<22: 3`).
   → 카드 본문에 kit 본문 클래스 `.s-body`(22px)를 부여해 해소(0건). **이것이 「정적 PASS가
   화면의 안전을 뜻하지 않는다」의 실물 재현이다.**
2. **표가 시각자료로 집계되지 않았다** — R-QC-08(설명 슬라이드 시각자료 보유 비율)이 33.3%로
   FAIL이었다. 원인은 `table.t`에 `viz-*` 표식이 없어 `count_explanatory_visuals`가 세지
   않은 것. → `viz-table` 태깅으로 해소(화면 무변경 · 집계만). 임계는 건드리지 않았다.

**두 건 다 「덱을 고쳐 대조군을 깨끗하게」 한 것이고, 임계·규칙·검출 범위는 하나도 바꾸지
않았다.** 미탐은 나오지 않았으므로 게이트를 고칠 일은 없었다.

## ⓑ 토큰 값 ↔ 규칙 하한 대조 (계약 §4㉡) — PASS

집행 정본 `scripts/audit_typography.js`의 `TIERS`(narrative 22 · boxDesc 20 · table 17 ·
label 14 · badge 11 · code 0), 선언 정본 `kit/guide/토큰-치트시트.md`.

```
token                value        role  floor verdict vs default
--fs-cover            74px   narrative     22    PASS same
--fs-part             56px   narrative     22    PASS same
--fs-display-lg       64px   narrative     22    PASS same
--fs-display          52px   narrative     22    PASS same
--fs-title            38px   narrative     22    PASS same
--fs-box-title        26px   narrative     22    PASS same
--fs-lead             23px   narrative     22    PASS same
--fs-body             22px   narrative     22    PASS same
--fs-box-desc         20px     boxDesc     20    PASS same
--fs-eyebrow          19px       label     14    PASS same
--fs-table            17px       table     17    PASS same
--fs-caption          14px       label     14    PASS same
--fs-badge            13px       badge     11    PASS same
role-tier judged 13 : PASS 13 · FAIL 0 · UNJUDGED 0
--lh-*    8 tokens · all identical to default: True
--sp-*    8 tokens · all identical to default: True
--fs-N   10 tokens · all identical to default: True
--lh-body = 1.78 (cheatsheet requires 1.78) -> PASS
--sp-4    = 4px (base unit 4px) -> PASS
```

**판정 13 · 미판정 0.** 「대상 계수 0」이 아니라 역할 티어 13개를 전부 판정했다.
비색 50개가 default와 바이트 동일하므로 하한 충족은 default 테마와 동일하게 성립한다.
계약 §4㉡이 경고한 「테마가 스스로 하한 미달을 생산」은 발생하지 않는다.

### 선언↔집행 정합

```
$ python scripts/verify_declared_vs_enforced.py
RESULT | PASS | 새 불일치 0 (등재된 알려진 불일치 8건)
exit 0
```

### 색 대비 — ◇ 파생값 확정의 근거

| 쌍 | 대비 | 판정 |
|---|---:|---|
| `--on-coral` #391106 on `--coral` #F84818 | **4.72** | PASS (WCAG AA 4.5) — 잠정값 #5C1C12는 **3.64로 미달**이라 바꿨다 |
| (참고) default의 같은 자리 #5C1C12 on #F97360 | 4.69 | default 자신의 마진 |
| `--white` on `--blue` #3060C3 | 5.85 | PASS |
| `--white` on `--red` #D80000 | 5.36 | PASS |
| `--white` on `--navy` #233B66 | 11.12 | PASS |
| `--ink` on `--ice` #8EC3FF | 9.64 | PASS |
| `--ink` on `--paper` #F4F8FB | 16.63 | PASS |

## ⓒ 회귀 12모듈 전량 — OK · exit 0

```
$ python -m unittest tests.test_deck_pipeline tests.test_image_pipeline tests.test_quality_gates \
    tests.test_deck_contract tests.test_declared_vs_enforced tests.test_rule_pointers \
    tests.test_typography_rules tests.test_analyze_agent_usage tests.test_audit_context_budget \
    tests.test_hook_guards tests.test_course_paths tests.test_theme_contract
Ran 266 tests in 29.374s
OK
exit 0
```

**건수 정정**: `references/검증-명령-지도.md` §6의 「219건」은 낡았다. 내 변경 «전» 실측이
**261건**(MEMORY 기재와 일치)이고, 이번에 신설한 회귀 5건을 더해 **266건**이다.
지도 수정은 이번 범위 밖이라 하지 않았다.

### 기존 과목(바이브코딩) 무영향 — 러너 3주차 전부 exit 0 · 래칫 전부 불변

| 주차 | RESULT | 구조 WARN | 품질 WARN | 렌더 WARN | exit |
|---|---|---:|---:|---:|---:|
| 1주차 | `RESULT \| PASS \| 정적 게이트 + 렌더 증거 모두 확인` | 8 ≤ 8 | 7 ≤ 7 | 83 ≤ 83 | 0 |
| 2주차 | `RESULT \| PASS \| 정적 게이트 + 렌더 증거 모두 확인` | 2 ≤ 2 | 8 ≤ 8 | 198 ≤ 198 | 0 |
| 3주차 | `RESULT \| PASS \| 정적 게이트 + 렌더 증거 모두 확인` | 1 ≤ 1 | 5 ≤ 5 | 9 ≤ 9 | 0 |

**베이스라인이 하나도 움직이지 않았다** — 2번째 테마·2번째 과목 추가로 인한 회귀 0.

## ⓓ 격리·정합 2종 — 둘 다 exit 0

```
$ python scripts/verify_subject_isolation.py
검사 과목 2개: courses/likelionSKU/profile.md(리터럴 8), courses/바이브코딩/profile.md(리터럴 9)
검사 리터럴 17종 | FAIL 대상 25파일 | WARN 대상 8파일
결과: PASS — 스킬 본문에 과목 고유 값 0건 (WARN 56건은 차단하지 않습니다).
exit 0

$ python scripts/verify_declared_vs_enforced.py
RESULT | PASS | 새 불일치 0 (등재된 알려진 불일치 8건)
exit 0
```

### 테마 해석 실측 — 과목마다 다른 테마가 실제로 잡힌다

```
$ CREATE_SLIDES_COURSE=likelionSKU  → 테마: likelionSKU | 토큰 99 | 사유: (없음) | --blue = #3060C3
$ CREATE_SLIDES_COURSE=바이브코딩    → 테마: default     | 토큰 99 | 사유: (없음) | --blue = #1D4ED8
```

## 단계 F — 다과목 파급과 수정 (커밋 `f2831cd`)

계획 §F가 예고한 `AmbiguousCourseError`가 실제로 3곳에서 발화했다. **기준을 낮추지 않고**
호출부가 과목을 밝히도록 고쳤으며, 예외를 삼키는 방향의 수정은 하지 않았다.

| # | 무엇이 깨졌나 | 어떻게 고쳤나 |
|---|---|---|
| 1 | `verify_deck_quality`·`verify_draft_quality`가 **모듈 최상위**에서 과목 종속 임계를 읽어, 과목이 2개가 되자 **import만으로** 예외가 터졌다(`test_quality_gates` 53건 붕괴) | 적재 시점을 `run_checks()` 진입으로 이동 + `course=` 인자 신설. 최상위에는 「호출부」가 없다 — 그래서 §F의 「호출부 명시」가 성립하려면 시점 이동이 선행이었다 |
| 2 | `test_deck_pipeline`·`test_deck_contract`가 과목 미지정으로 실저장소 경로를 읽었다 | 호출부(테스트)가 「어느 과목의 2주차인가」를 명시 |
| 3 | `resolve_course`가 **후보 0개**인 루트(구경로 폴백 세계)에서도 던져, 합성 픽스처를 읽는 호출이 전역 환경변수 하나로 깨졌다 | 후보 0개면 오귀속이 원리적으로 불가능하므로 과목명을 무시하고 `None`. **후보 ≥1인데 이름이 안 맞으면 여전히 던진다**(오타 보호 유지) |

**회귀 5건 신설** — 이 두 구멍에 회귀가 0개였다:
`NamedCourseAgainstCourselessRootTests` 4건(0개 루트 완화 + 오타 보호 쌍 고정) ·
`GateModulesImportWithoutACourseTests` 1건(과목 미지정 import가 죽지 않는다).

## 범위 밖 발견 (고치지 않고 기록만)

- `kit/styles/deck.css:2` 헤더 주석에 `SKU LIKELION` 문자열이 **이미 존재한다**(그 kit이 원본
  덱에서 파생된 이력). 그래서 프로필 §8에 이 리터럴을 등재하면 격리 검사가 상시 FAIL이 되어
  제외했고, 사유를 프로필 §8 「검사에서 제외한 것과 사유」에 기록했다. `린캔버스`도 같은 파일
  2건(레이아웃 이름)이라 같은 사유로 제외.
- 원본은 그림자를 코발트로 틴트한다(`rgba(48,96,195,…)` 5종). 우리 테마는 완료 기준 2
  (「색 49개만 값 변경」) 때문에 default를 유지했다 — 그림자를 테마 축에 넣을지는 별도 안건.
- `references/검증-명령-지도.md` §6의 회귀 건수 219는 낡았다(실측 261 → 266).
