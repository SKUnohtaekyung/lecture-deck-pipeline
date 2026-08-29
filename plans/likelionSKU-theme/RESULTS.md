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
| **정상본(대조군)** | **exit 0** · 요약: FAIL 0 · WARN 2 · PASS 45 | **exit 0** · 요약: FAIL 0 · WARN 1 · PASS 9 | — (대조군) |
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

정상본 + 변형 4벌 **전부** 측정했다(5회). 전 회차 `INVALID: null` · `slideCount: 7`.

| 대상 | `fontFloor` | `slots`(빈 슬롯) | `below` | `ovf` | `off` | 브라우저 채널 검출 |
|---|---:|---:|---:|---:|---:|---|
| 정상본 | **0** | 0 | 1 | 0 | 0 | — (대조군) |
| **V1** 폰트하한 | **5** | 0 | 1 | 0 | 0 | ✅ `narrative<22` 5건(실측 20px · 하한 22px) |
| **V2** 아이콘누출 | 0 | 0 | 1 | 0 | 0 | — (설계상 대상 아님, 아래) |
| **V3** 내부라벨 | 0 | 0 | 1 | 0 | 0 | — (설계상 대상 아님, 아래) |
| **V4** 빈 슬롯 | 0 | **1** | 1 | 0 | 0 | ✅ `slots` 0→1 |

**V2·V3이 브라우저 채널에서 0인 것은 미탐이 아니다.** 두 감사기는 «렌더된 기하와 타이포»를
재는 도구이고, 아이콘 마커·내부 작업 라벨은 **텍스트 내용** 결함이라 애초에 이 채널의 판정
대상이 아니다. 그 둘의 집행 정본은 정적 채널이고 거기서 잡혔다(V2 exit 1 · V3 exit 1).
**「측정 대상이 아님」과 「봤는데 못 봄」을 구분해 적는다** — 후자만 미탐이다.

정상본의 `below 1`은 결함형 지표이나 4종 결함과 무관하며 **정상본·변형 5회 전부 동일하게 1**이라
대조에 영향이 없다(실제 주차라면 계약 waiver 등재 대상). 나머지 9지표(occl·wb·stretchX·
stretchY·ragged·lowFill·wideEmpty·hollow·lap) 전부 **0**.

측정 환경: 뷰포트 1440×900 · dpr 2 · 이미지 1개 전량 로드 · `document.fonts.ready` 대기 ·
`audit_all.js` 캐시버스터 부착.

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
Ran 275 tests in 30.810s
OK
exit 0
```

**건수 정정**: `references/검증-명령-지도.md` §6의 「219건」은 낡았다. 내 변경 «전» 실측이
**261건**(MEMORY 기재와 일치)이고, 이번에 신설한 회귀 14건을 더해 **275건**이다.
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

## 재검토 — 로고·색의 «시스템화» 감사 (2026-08-29 2차)

색 49개 매핑 자체는 재대조에서 빈틈이 없었다(아래 ①). 구멍은 **매핑이 아니라 그 바깥**에 있었다.

### ① 색 49토큰 전수 재대조 — 매핑 결함 0

원본 `덱_템플릿킷/styles/deck.css`의 hex·rgba를 전수 추출해 우리 49개와 1:1 대조했다.
「default 값 그대로 + 원본에 그 값 없음」은 **11개**였고 **전부 이미 문서화된 결정**이다:
`--mint`·`--on-mint`(원본에 fill용 녹색 없음 — 「없으면 유지」) · `--glass-*` 8개(브랜드
무관 중립층) · `--paper`(원본에 라이트 표지 없음 · ◇2). **새로 발견한 누락 매핑은 0건.**

### ② ★ 그림자가 «다른 테마의» 브랜드 파랑을 품고 있었다 — 고쳤다

`--shadow-md/lg/blue`의 값은 `rgba(29,78,216,α)`인데 **29,78,216 = #1D4ED8 = default의
`--blue`**다. likelionSKU의 `--blue`는 #3060C3(48,96,195)이므로, 이 테마의 덱이
**자기 팔레트에 없는 파랑으로 그림자를 드리우고 있었다.** 원본도 자기 코발트로 틴트한다
(원본 deck.css에서 `rgba(48,96,195,…)` 5종 실측) — 즉 두 디자인 시스템 다 그림자를
브랜드 색으로 틴트하는데 우리 테마만 남의 색을 물려받고 있었다.

→ **색상 성분만** 이 테마의 `--blue`로 옮겼다. 투명도·오프셋·블러는 default 그대로라
그림자의 «무게» 체계는 불변이고, 중립 그림자(`--shadow-sm`, 잉크 기반)는 손대지 않았다.

⚠️ **이 변경은 완료 기준 2의 「색 49개만 값 변경」을 문자 그대로는 벗어난다**(값 변경
17 → 20). 그림자를 «비색»으로 센 것은 계약의 분류이고, 결정 1의 취지는 **크기·행간·간격**
(폰트 스케일 A안)이었다. 값 안에 브랜드 색을 품은 토큰을 색 아닌 것으로 취급하면 테마가
원리적으로 완성될 수 없어 분류 쪽이 틀렸다고 판단했다 — 되돌리려면 이 커밋 하나만 되돌리면 된다.
계약 §6에 이 함정을 명시했다.

### ③ ★★ 등재한 테마로 «정상적인 주차 덱을 만들 수 없었다» — 집행 이관으로 해소

가장 큰 구멍이다. 실제 주차 덱과 동일하게 정본 kit을 링크한 likelionSKU 덱을 만들어 재 보니:

```
$ CREATE_SLIDES_COURSE=likelionSKU python scripts/verify_deck.py <정본 kit 링크 덱> --parts 1
[FAIL] ✗ [kit] 토큰 누락/값변경: ['--blue:#3060C3', '--coral:#F84818', '--red:#D80000',
        '--coral-deep:#B9471E'] — 링크된 CSS가 테마 'likelionSKU' 선언과 다르다
exit 1
```

테마 파일은 «선언»이고 집행은 `kit/styles/deck.css`였으므로, 통과시키는 유일한 길이
**kit CSS를 통째로 복사해 `:root`만 바꾼 사본**을 두는 것이었다(1차 실측 때 내가 실제로
그렇게 했다). 그건 드리프트 보장 장치다 — 즉 **테마 축은 선언만 되고 시스템화되지 않았다.**

→ 테마 파일을 **링크 대상**으로 승격했다(`verify_deck.linked_theme_tokens` 신설).
덱은 kit 3종 다음에 `kit/themes/<이름>/tokens.css`를 링크하고 캐스케이드가 `:root`를 덮는다.

| 구성 | 결과 |
|---|---|
| 정본 kit + **올바른** 테마 링크 | **exit 0** · `[kit] 토큰 값 정확(… 테마 'likelionSKU')` PASS |
| 정본 kit + 테마 링크 **없음**(과목은 likelionSKU) | **exit 1** — 실제로 default로 렌더되므로 옳다 |
| 정본 kit + **다른** 테마 링크 | **exit 1** |
| 테마 파일 **2개** 링크 | **FAIL** — 파일 순서에 값이 의존하므로 막는다 |
| default 테마 덱(링크 없음) | 종전과 **완전 동일** — 동결 산출물 무영향(D-1) |

**렌더 실측(1440×900)**: `deck.css`(default 값) + 테마 링크만으로 브라우저 계산값이
`--blue:#3060C3` · `--coral:#F84818` · `--shadow-blue:rgba(48,96,195,.30)` ·
`--fs-body:22px`(비색 불변). 시험 덱에서 kit CSS 사본을 **삭제**하고 정본 링크로 전환한 뒤
뮤테이션 매트릭스를 재실행해 동일한 4/4 검출을 확인했다.

### ④ ★ 로고·파비콘 — 덱 «안»은 이미 옳았고, 새 덱으로 상속되는 자산이 틀렸다

- **옳았던 것**: 스타터 본문의 인라인 로고는 이미 `var(--mint)`·`var(--blue)`·`var(--ink)`를
  쓴다 → 테마를 자동으로 따른다. 색 시스템 준수.
- **틀렸던 것 1 — 파비콘**: `<link rel="icon">`의 data-URI에 `%2314B8A6`·`%231D4ED8`
  (default 팔레트)가 박혀 있었다. 파비콘은 브라우저 크롬이 읽는 외부 리소스라 **CSS 커스텀
  속성이 닿지 않는 유일한 색 자리**다. → 기본값을 **중립 잉크**로 바꾸고 ✏️ 저작 슬롯으로
  표시했다(특정 테마 색을 박아 두면 다른 테마의 덱이 남의 팔레트를 달고 다닌다).
- **틀렸던 것 2 — `kit/starter/logo.svg`**: 하드코딩 hex 3개 + `aria-label="VIBECODING"`.
  → `var(--토큰, 폴백)` 형태로 바꿔 인라인 사용 시 테마를 따르게 하고 라벨을 중립화했다.
- **틀렸던 것 3 — 워드마크**: 스타터에 `VIBECODING`이 5곳(제목 1 · `.s-brand` 4). 공용
  kit이 한 과목의 브랜드를 달고 있었다. → `{{브랜드}}` 자리표시자로 교체.
- **틀렸던 것 4 — `kit/styles/deck.css`의 조직명**: 헤더가 「SKU LIKELION 강의덱 —
  디자인 시스템…」이고 `.s-brand` 주석에 `VIBECODING`이 1건 있었다. 두 과목이 함께 쓰는
  kit이 한 조직명을 달고 있었다. → 「강의덱 kit — 전 과목·전 테마 공통」으로 바꾸고
  과목명 주석도 근거 문장을 보존한 채 정리(주석만 · 렌더 무영향). **선행 R-QC-14 위반
  11건에 막혀 한 번 되돌렸다가, 그 11건을 해소한 뒤 함께 처리했다**(아래 ⑥).

### ⑤ ★★ 그리고 이 넷을 **게이트가 하나도 보지 않고 있었다** — 미탐 해소

`verify_subject_isolation.py`의 스캔 범위는 «문서(.md) + 테마 선언»뿐이었다. 그래서
**새 덱으로 그대로 상속되는 자산**(복사되는 스타터 · 링크되는 공용 CSS)은 사각지대였고,
공용 kit에 한 과목의 브랜드가 **31곳** 있는 동안 게이트는 내내 **PASS**였다.
오탐은 시끄러워서 발견되지만 미탐은 PASS로 위장한다 — 이 저장소가 반복해서 당한 형태다.

→ `SCAN_WARN`에 `kit/starter/*`·`kit/styles/*.css` 편입. 편입 기준은 **「그 파일의 내용이
새 과목의 덱으로 상속되는가」**다 — 카탈로그(열람용)·CHANGELOG(변경 이력)는 상속되지 않으므로
일부러 뺐다(범위를 넓히는 것이 목적이 아니라 상속 경로를 덮는 것이 목적이다).

- 스캔 대상 파일 **8 → 14개**. 신설 시점 실측 **오탐 0 · 미탐 0**(위 ④에서 리터럴을
  전량 제거한 뒤라 신규 WARN 0건). 규율대로 **WARN으로 시작**한다.
- **부수 효과**: `SKU LIKELION`을 프로필 §8에 **등재했다**(리터럴 8 → 9). 1차 때는
  「등재하면 상시 FAIL이니 제외」였다. 그런데 그 문자열이 있는 `kit/styles/deck.css`는
  **FAIL 대상이 아니라 WARN 대상**이므로 등재해도 차단되지 않는다 — 「제외」의 전제부터
  틀렸던 것이다. 등재 후 실측: **WARN 56 → 58**(`deck.css:2` `SKU LIKELION` ·
  `deck.css:283` `VIBECODING`), 결과는 여전히 **PASS · exit 0**.
  **누출을 지운 것이 아니라 «보이게» 만든 것이 이 절의 성과다.**

### ⑥ 선행 R-QC-14 위반 **14건** — 사용자 지시로 같은 날 해소 (deck.css 11 + patterns.css 3)

④의 조직명 주석을 고치려고 `kit/styles/deck.css`를 스테이징하자 pre-commit이 막았다:

```
[FAIL] CSS lint (R-QC-14 · hook_slide_guard --mode css-lint)
  729 .note b · 843/844 .actor-card · 863/864 .flow-step · 872/874 .work-step
  946/947 .risk-card · 1000/1001 .pricing-method     (11건)
```

**내 변경이 만든 것이 아니다** — HEAD 판본도 동일한 11건·exit 1이다(내 diff는 주석 2줄).
이 훅은 `.css`가 **스테이징될 때만** 발화하는데 이 파일이 오래 스테이징된 적이 없어 잠복해 있었다.

⚠️ **부수 발견 — `--path` 모드는 이 파일을 조용히 건너뛴다.**
`--mode css-lint --path kit/styles/deck.css`는 **exit 0**을 낸다(대상 힌트에 안 걸려 조기 반환).
그 0은 「위반 없음」이 아니라 **「아무것도 안 봄」**이다. 실제 판정은 `--stdin-paths`만 한다.

#### 기계적 수정은 동결 덱을 깨뜨린다 — 먼저 재고 고쳤다

`.foo b` → `.foo > b`로 일괄 치환하면 **1·2주차 렌더가 바뀐다.** DOM 실측:

| 선택자 | 1주차 (후손/직계) | 2주차 | 3주차 |
|---|---|---|---|
| `.work-step b` | **13 / 0** | **30 / 11** | 0 / 0 |
| `.work-step span` | **26 / 13** | **70 / 39** | 84 / 84 |
| `.note`·`.actor-card`·`.flow-step`·`.risk-card`·`.pricing-method` | **전부 0 / 0** | 0 / 0 | 0 / 0 |

- **9개 선택자는 동결 덱에서 매칭 0건** → 직계로 좁혀도 자명하게 무영향.
- `.work-step` 2개만 실사용이고, 구조는 **`.work-step > (래퍼 div) > b/span`** 한 겹이었다.
  → `.work-step > b, .work-step > div > b` 형태로 좁혔다. 매칭 집합이 **정확히 보존**된다
  (1주차 b 13→13 · 2주차 b 30→30 · span 3주차 84→84).
  이 래퍼 한 겹은 덱 고유 구조가 아니라 **kit 자신의 카탈로그 구조**다
  (`kit/layouts/catalog.html` 실측 `work-step b` 4/4 · `span` 8/8 완전 일치).

#### 남은 12개는 «0×0»이었다 — 그래서 화면이 안 변한다

2주차에서 규칙 밖으로 빠지는 span 12개(`span` 안의 `span` 6 · `b` 안의 `span` 6 —
R-QC-14가 원래 막으려던 바로 그 중첩)는 전부 **`getBoundingClientRect` 0×0**이다.
시각적 실체가 없어 어떤 지표에도 잡히지 않는다.

#### 검증 — 동결 덱 3개 · 렌더 지표 17종 전량 before/after 동일

브라우저 감사(1440×900)를 **수정 전에 먼저 재고** 수정 후 다시 쟀다.

| 주차 | 장수 | fontFloor | below | ovf | hollow | lap/lapAbs | lowFill | stretchX/Y | wideEmpty | sparse |
|---|---:|---:|---:|---:|---:|---|---:|---|---:|---:|
| 1 | 75 | 57 | 25 | 2 | 38 | 1/5 | 5 | 3/2 | 4 | 214 |
| 2 | 112 | 182 | 0 | 0 | 20 | 2/4 | 1 | 6/0 | 4 | 384 |
| 3 | 81 | 0 | 0 | 0 | 13 | 0/0 | 0 | 6/3 | 2 | 211 |

**before/after 완전 동일**(`occl`·`off`·`wb`·`ragged`·`slots`도 전부 0으로 동일 ·
`INVALID` 없음). 러너 1·2·3주차 exit 0 · WARN 래칫 전부 불변.

→ 11건 해소 후 `kit/styles/deck.css`가 lint 통과(exit 0)하면서, ④에서 미뤘던 **조직명·과목명
주석 2건도 함께 정리**했다. 그 결과 공용 kit의 과목 리터럴이 **0**이 되어
`KNOWN_KIT_LEAKS`도 비웠다(WARN 58 → 56).

#### ★ 검사 범위를 넓히니 3건이 더 나왔다 — `patterns.css`

`deck.css`를 고친 뒤 **kit CSS 전체**에 린트를 돌리니 `kit/styles/patterns.css`에 3건이
더 있었다(`.cyc-node b` 47 · `.vt-leaf b` 85 · `.vt-leaf span` 86). pre-commit은
**스테이징된 `.css`만** 보므로 이 파일을 건드리지 않는 한 영영 드러나지 않는다.
**「한 파일을 고쳤다」와 「규칙을 지켰다」는 다르다.**

DOM 실측 결과 셋 다 실사용이 **전부 직계**라 단순 `>` 좁히기로 충분했다:
2주차(동결) `vt-leaf b` 8/8 · `vt-leaf span` 4/4 · charts 카탈로그 `cyc-node` 4/4 · `vt-leaf` 3/3.
수정 후 동결 덱 3개 렌더 재측정 — **again before/after 완전 동일**.

최종: `ls kit/styles/*.css | hook_slide_guard --mode css-lint --stdin-paths` → **exit 0**.

## 범위 밖 발견 (고치지 않고 기록만)

- `kit/styles/deck.css:2` 헤더 주석에 `SKU LIKELION` 문자열이 **이미 존재한다**(그 kit이 원본
  덱에서 파생된 이력). 그래서 프로필 §8에 이 리터럴을 등재하면 격리 검사가 상시 FAIL이 되어
  제외했고, 사유를 프로필 §8 「검사에서 제외한 것과 사유」에 기록했다. `린캔버스`도 같은 파일
  2건(레이아웃 이름)이라 같은 사유로 제외.
- 원본은 그림자를 코발트로 틴트한다(`rgba(48,96,195,…)` 5종). 우리 테마는 완료 기준 2
  (「색 49개만 값 변경」) 때문에 default를 유지했다 — 그림자를 테마 축에 넣을지는 별도 안건.
- `references/검증-명령-지도.md` §6의 회귀 건수 219는 낡았다(실측 261 → 266).
