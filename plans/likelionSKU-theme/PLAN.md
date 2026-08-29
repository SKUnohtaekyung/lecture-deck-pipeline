# likelionSKU 테마 등재 — 실행 계획

> **상태: 사용자 승인 대기 (승인 전 구현 금지)**
> 작성 2026-08-29 · 브랜치 `feat/likelionsku-theme`(승인 후 생성) · main 병합·push는 별도 승인 후에만.
> 조사 정본: 이 계획의 근거가 된 likelionSKU 폴더 전수 조사는 2026-08-29 세션에서 워커 4개로 수행
> (스킬 105줄 + references 4파일 + scripts 3파일 / 덱_템플릿킷 전 파일 / 세션 2개 전 문서·덱).

## 0. 배경과 목표

`likelionSKU/`(저장소 루트, 302MB 중첩 git 저장소)는 SKU 멋쟁이사자처럼 UX/UI Team의
강의덱 제작 시스템이다 — 우리 create-slides와 동형 구조(스킬+템플릿킷+세션), 동일 물리
기반(1280×720 · Pretendard · 방향키 발표), 고유 디자인 정체성(코발트 팔레트 · clay v2 이미지).

**목표**: 이 디자인 정체성을 우리 시스템의 **두 번째 테마 `likelionSKU`로 등재**한다.
수용 구조는 이미 존재한다 — 테마 축(`kit/themes/`, 2026-08-24 P2~P3)과 테마 계약
(`kit/guide/테마-계약.md`) §5가 「두 번째 테마를 만들어도 된다」로 갱신된 상태다.
등재 조건은 계약 §4의 관문 2종(뮤테이션 매트릭스 · 토큰↔하한 대조)이며,
그 통과가 「검증된 테마」의 정의다.

## 1. 사용자 확정 결정사항 (2026-08-29 — 재저울질 금지)

| # | 결정 | 내용 |
|---|---|---|
| 1 | 폰트 스케일 A안 | **색 토큰 49개만** likelionSKU 팔레트로 교체. 크기·행간·간격 등 비색 50개는 default 값 유지(R-TYPE-01 하한 준수). 원본의 19px 본문 재현은 하지 않는다 |
| 2 | 원본 보존 | `likelionSKU/`는 삭제하지 않는다. 필요한 것만 `kit/themes/` + `courses/`로 추출해 **우리 쪽을 정본**으로 삼고, 폴더는 참조용 원본으로 보존(gitignore) |
| 3 | 브랜치 | 작업은 `feat/likelionsku-theme`에서. main 병합·push는 사용자 승인 후에만 |
| 4 | 과목 폴더명 | **`courses/likelionSKU/`** (테마명·원본 폴더명과 동일 — 추적 용이, ASCII 경로 안전) |

## 2. 범위

**포함**: 격리 커밋(단계 0) · 테마 토큰(A) · 과목 프로필(B) · clay v2 이미지 규약(C) ·
등재 관문 2종(E) · 회귀 전량 + 다과목 파급 수정(F) · 문서 마감(G).

**제외**:
- **레이아웃 24종 이식 안 함**(사용자 확정 D). venn·actor·lean·risk·metric·map·price 등
  원본 고유 구도는 실제 덱 제작 시 주차 계약 `layout_families`에 등재해 쓰고(R-LAYOUT-03),
  **서로 다른 과목 2회 이상 사용** 후 kit 승격 검토(R-PROMO-01).
- 원본 저장소 자체의 문제(BM 덱 "WEEK 11" 잔존값, `dist/` 구버전, 바이브 `_redirects`가
  없는 파일 참조)는 우리 범위 밖 — 발견사항으로 §11에 기록만 한다.
- 세션 산출물(BM·바이브 덱)을 우리 `courses/`로 옮기지 않는다 — 다른 파이프라인의 완성물이다.
- `sessions/references/`의 기존 미추적 PNG 2개 — 이번 작업과 무관, 건드리지 않는다.

## 3. 단계별 상세

### 단계 0 — 격리 커밋 ★다른 무엇보다 먼저 (메인 직접)

1. `git checkout -b feat/likelionsku-theme`
2. `.gitignore`에 `likelionSKU/` 추가
3. 이 계획 파일(`plans/likelionSKU-theme/PLAN.md`)과 함께 **단독 커밋**

**왜 먼저인가**: `likelionSKU/`는 `.git` 302MB를 품은 중첩 저장소다. 어떤 스테이징 실수보다
먼저 차단벽을 세운다. **메인 직접인 이유**: 2줄 편집 + 커밋, 위임 오버헤드가 작업보다 크다.

### 단계 A — `kit/themes/likelionSKU/tokens.css` 신설 (메인 solo)

`kit/themes/default/tokens.css`(99토큰)를 복사해 **색 49개의 값만** 교체. 토큰 이름
집합·순서·비색 50개 값은 그대로 — `tests/test_theme_contract.py`의
`EveryThemeIsCompleteTests`가 이름 집합 완전성을 검사한다.

**담당 근거**: 49개 값 매핑은 판단이 무겁고 토큰이 가벼운 정밀 편집(AGENTS 「하네스 — solo」
기준)이고, 원본 팔레트 조사 결과가 이미 메인 컨텍스트에 있다. 워커에 넘기면 원본
재독 비용만 늘고 매핑 판단은 어차피 메인이 게이트해야 한다.

**작성 규율**:
- 파일 헤더 주석에 브랜드 문자열("SKU LIKELION"·"멋쟁이사자처럼"·"아기사자" 등)을 넣지
  않는다 — `verify_subject_isolation.py`가 `kit/themes/*/tokens.css`를 **FAIL 스캔 대상**으로
  보므로 프로필 §8 리터럴과 충돌한다(§61~70 `SCAN_FAIL`).
- 새 토큰을 만들지 않는다(이름 집합 동결). 원본의 `--yellow-soft`/`--yellow-line` 등
  우리 토큰 집합에 없는 색은 **버린다** — 필요해지면 별도 계약 갱신 안건이다.

**색 49개 매핑표** (◆ = 원본 실존 값 채택 · ◇ = 코발트 기준 재파생(구현 시 확정) · ─ = 변경 없음):

| 토큰 | default | → likelionSKU | 구분 · 근거 |
|---|---|---|---|
| `--blue` | #1D4ED8 | **#3060C3** | ◆ 코발트 주 강조(화면 UI용 — 이미지용 #0066CC와 별개, §C 참조) |
| `--electric` | #6BA5FF | **#2F6BF8** | ◆ 표지 일렉트릭 |
| `--ice` | #A9C6FF | **#8EC3FF** | ◆ 아이스블루(헤더 라인) |
| `--periwinkle` | #93A7E8 | **#92ADF1** | ◆ 비강조 보조 |
| `--navy` | #16277A | **#233B66** | ◆ 깊이·다크 층 |
| `--coral` | #F97360 | **#F84818** | ◆ 원본 오렌지(경고 fill) |
| `--coral-deep` | #C2452F | **#B9471E** | ◆ 원본 orange-bold |
| `--red` | #DC2626 | **#D80000** | ◆ 원본 레드 |
| `--mint` | #14B8A6 | #14B8A6 | ─ 원본에 fill용 녹색 실존값 없음(원본 녹색은 콜아웃 전용) — 「없으면 유지」 원칙 |
| `--mint-deep` | #0F766E | #0F766E | ─ **원본 `--green`과 이미 동일** |
| `--on-mint` | #083B36 | #083B36 | ─ 대비 파생값, 원본 대응 없음 |
| `--on-coral` | #5C1C12 | ◇ | coral이 #F84818로 바뀌므로 대비 재검토 후 확정(잠정 유지) |
| `--blue-soft` | #EEF3FE | **#EEF2FF** | ◆ 원본 blue-soft |
| `--mint-soft` | #E9F8F5 | **#E8F7F5** | ◆ 원본 green-soft |
| `--coral-soft` | #FEF0ED | **#FFF1EA** | ◆ 원본 orange-soft |
| `--red-soft` | #FDECEC | **#FFF1F0** | ◆ 원본 red-soft |
| `--th` | #EEF3FE | **#F2F5FB** | ◆ 원본 표 헤더 |
| `--cover-bg` | #101E52 | **#1A1A1A** | ◆ 원본 다크 클로징 배경 |
| `--paper` | #F4F8FB | ◇ | 표지 라이트 배경. 원본 표지는 다크지만 **구도는 전 테마 공통 라이트 유지**(어휘·구도 동결) — 아이스 언더톤으로 재파생(잠정 #F5F9FF), 대비 검토 후 확정 |
| `--white` `--black` `--ink` | #FFFFFF/#000000/#141821 | 동일 | ─ 원본 값과 이미 일치 |
| `--gray-700` `--gray-400` | #4F4F4F/#9A9A9A | 동일 | ─ 원본 값과 이미 일치 |
| `--surface` `--line` | #F3F5F8/#E5E8F0 | 동일 | ─ 원본 값과 이미 일치 |
| `--surface-alt` `--surface-row` | #FBFCFF/#FCFDFF | 유지 | ─ 원본 대응 없음(중립 파생) |
| `--surface-recap` | #F8FBFF | #F8FBFF | ─ **원본 concept-recap 배경과 이미 동일** |
| `--blue-line` | #DCE4FF | #DCE4FF | ─ 원본 보조값에 실존(동일) |
| `--blue-line-strong` | #CDDBFF | ◇ | 코발트 기준 재파생(잠정 유지) |
| `--blue-panel` | #F5F8FF | #F5F8FF | ─ 원본 보조값에 실존(동일) |
| `--blue-panel-alt` | #F4F8FF | #F4F8FF | ─ 원본 보조값에 실존(동일) |
| `--blue-panel-strong` | #EAF0FF | #EAF0FF | ─ 원본 보조값에 실존(동일) |
| `--coral-line` | #FBD8CF | **#FFD9C7** | ◆ 원본 보조값 |
| `--red-line` | #FFD0CC | #FFD0CC | ─ 원본 보조값과 이미 동일 |
| `--mint-line` | #C9EAE4 | **#C9EBE6** | ◆ 원본 보조값 |
| `--on-dark-muted` | #D6DBE2 | #D6DBE2 | ─ 원본 보조값과 이미 동일 |
| `--on-dark-caption` | #9AA2AE | #9AA2AE | ─ 원본 보조값과 이미 동일 |
| `--on-blue-muted` | #DCE9FF | #DCE9FF | ─ 원본 보조값과 이미 동일 |
| `--blue-overlay` | rgba(238,242,255,.92) | ◇ | blue-soft(#EEF2FF) 기준 미세 조정(잠정 rgba(238,242,255,.92) 유지) |
| `--glass-*` 8종 | (화이트·잉크 기반 rgba) | 유지 | ─ 브랜드 무관 중립층 — 재파생 실익 없음 |

> 표에 없는 색 토큰은 없다(위 49개가 전부). ◇ 4건은 구현 시 대비 확인 후 확정하고
> 확정값·근거를 이 파일에 추기한다.

**비색 50개** — 전부 default 값 유지(결정 1): 캔버스 2(`--sw` `--sh`) · 라운드 4(`--r-*`) ·
그림자 4(`--shadow-*` — 단 블루틴트 rgba의 **색 성분**은 코발트 기준 재파생 여부를 구현 시
판단하되, 그림자는 계약 계수상 비색이므로 **기본은 유지**) · `--font-mono` 1 ·
폰트 스케일 10(`--fs-N`) · 역할 티어 13(`--fs-cover`~`--fs-badge`) · 행간 8(`--lh-*`) ·
간격 8(`--sp-*`).

**단계 검증**: `python -m unittest tests.test_theme_contract` — 이름 집합 일치
(`EveryThemeIsCompleteTests`)와 default 불변(`DefaultThemeMirrorsKitTests`) 동시 확인.

### 단계 B — 과목 프로필 신설 (워커 · sonnet · effort **medium**)

산출물: `courses/likelionSKU/profile.md` — 스키마 정본 `입력양식/과목프로필템플릿.md`의
전 절(§1~§8)을 따른다.

| 절 | 채울 내용 (원본 출처) |
|---|---|
| §1 과목 기본 | 과목명 likelionSKU(SKU 멋쟁이사자처럼 UX/UI 트랙) · 대상 "대학 1~3학년 비즈니스 비전공 아기사자" · 회차 단위 "세션" · 단일 세션 60~90분 (출처: `세션/BM_수익모델/README.md` · `_컨텍스트_타겟과커리큘럼.md`) |
| §2 규모 기준선 | 세션당 26~33장 계획 → 실제 30~31장 (출처: BM 덱 30장 실측 · 바이브 덱 31장 실측 — **원본 덱 실측이므로 출처 명기 시 기준선 자격 충족**. 출처를 못 채우는 항목은 공란+WARN 시작 — 다른 과목 값을 빌리지 않는다) |
| §3 밀도 기준선 | 실측 근거를 특정할 수 있는 항목만. 없으면 공란(WARN) |
| §4 표현 취향 | 원본 횡단 규칙: "색은 문법"(코발트=강조 1~2개 · 오렌지·레드=경고 전용 · 동시 강조 금지) · 제목은 주제가 아니라 **결론** · 같은 레이아웃 3연속 금지 · 가운데 커넥터로 관계 명시(→ ⊃ ≠ ↓) (출처: `00_레이아웃-선택가이드.md` · `references/deck-assembly.md`) |
| §5 브랜드·자산 | 워드마크 "SKU LIKELION" · 팀 라벨 "UX/UI Team · Official LIKELION at SKU" · 로고: 원본 `덱_템플릿킷/img/logo.png` 경로 기록(복사 여부는 §11-리스크4 참조) · **테마: `likelionSKU`** (포인터 한 줄 — 값 복제 금지) |
| §6 도구·제품 맥락 | Codex·Google Antigravity(바이브 세션) · 린캔버스·BMC(BM 세션) |
| §7 소급 면제 | 해당 없음(신설 과목 — 빈 표 유지) |
| §8 격리 리터럴 | "SKU LIKELION" · "아기사자" · "멋쟁이사자처럼" · "UX/UI Team" 등 브랜드 문자열. ⚠️ **과목 폴더명 문자열 "likelionSKU"는 등재하지 않는다** — 테마 폴더명(`kit/themes/likelionSKU/`)과 동일 문자열이라 「모든 출현이 운영 파라미터」 조건을 채우지 못한다(등재 시 tokens.css 헤더·계약 문서의 테마명 표기가 전부 FAIL로 오탐) |

**담당 근거**: 원본 문서 2~3개(~250줄) 재독 + 스키마 채우기 — 독립적·자기완결적이라 워커에
적합, 메인 창을 원본 재독으로 불리지 않는다. **effort medium 근거**: 스키마 준수 문서
작성으로 창의 판단은 적으나, 격리 원칙(어디에 무엇을 넣으면 안 되는지 — §5 값 복제 금지,
§8 등재 조건)의 이해가 필요해 low로는 부족하다.

**단계 검증**: `python scripts/verify_subject_isolation.py` (다과목 전수 순회는
`profile_paths()`가 담당 — 2026-08-24 P0에서 이미 대비됨).

### 단계 C — clay v2 이미지 규약 이식 (워커 · sonnet · effort **low**)

산출물: `courses/likelionSKU/이미지규약-clay-v2.md`. 원본
`덱_템플릿킷/images/공통이미지프롬프트.md`(96줄)와
`.claude/skills/likelion-deck/references/image-and-deploy.md`(38줄)에서 이식:

1. **4블록 프롬프트 계약** — 블록1 STYLE·MATERIAL&PALETTE(soft 3D clay · matte plastic +
   frosted-glass · 흰/회/파랑 앵커 + 보조 액센트 5~10%) / 블록2 SUBJECT·COMPOSITION(교체
   대상은 여기뿐 · subject 우측, 좌측 35~40% 텍스트용 비움 · 무이목구비) / 블록3
   RENDER(완전 투명 PNG · 받침·배경 금지 · 1:1) / 블록4 NEGATIVE(읽히는 글자·숫자·한글·로고
   금지 · 포토리얼·플랫벡터·애니 금지)
2. **⚠️ "두 코발트" 구분을 명시 절로**: 화면 UI 코발트 = `#3060C3`(테마 토큰 `--blue`) vs
   **이미지 프롬프트 코발트 = `#0066CC`**(+ ice `#8EC3FF` · navy `#233B66`). 원본이 의도적으로
   이원화한 값이다(`image-and-deploy.md` 명시) — 합치면 안 된다.
3. 네이밍 규칙 `s<NN>_<concept-kebab>[-<style-version>][-transparent].png` · 배치 클래스 짝 ·
   특수 슬롯(도입 이미지 · concept-recap 배경 `-bg` 16:9 예외) · 배포 목표 3~8MB.

**담당 근거**: 원문 이식·재구성 위주의 기계적 작업 — B와 파일이 달라 **병렬 실행**(단일
라이터 충족). **effort low 근거**: 판단 부하가 낮은 전사·구조화 작업이다.

### 단계 D — 레이아웃 24종: 이번에 이식하지 않음

§2 「제외」에 기록한 대로. 이 계획에서는 결정 사실만 남긴다.

### 단계 E — 등재 관문 2종 (테마 계약 §4 — 2종 모두 통과해야 등재)

#### E① 뮤테이션 매트릭스

「PASS가 나왔다」는 증거가 아니다 — **결함을 심었는데도 PASS면 그 게이트는 눈이 먼 것**이다
(계약 §4㉠). 선행 사례: `plans/gate-input-hardening/PLAN.md` §0(3주차 82장 미니 루트 실측).

1. **시험 덱 조립** (워커 · sonnet · effort **high**): `tmp/theme-mutation/likelionSKU_시험덱/`
   안에 최소 규모(6~8장) 덱. 요구 표면: 긴 산문 본문 슬라이드(결함① 심을 자리) · 카드형 ·
   표 · `asset-slot` 포함 슬라이드(결함④ 자리). 준수: 구조 셸 동결 어휘(`slide` `s-head`
   `s-pageno` `slide-num` `s-title` `asset-slot`) · kit 공통 클래스만 사용 · likelionSKU 토큰
   값으로 셸 오버라이드. **effort high 근거**: 이 덱의 어휘·계약 준수가 곧 측정 유효성이다 —
   조립 실수가 게이트 실측을 오염시키면 관문 전체를 다시 돌아야 한다(4개 워커 작업 중
   유일하게 품질이 결과의 성립 조건).
2. **결함 변형 4벌 제작** (메인 직접): 정상본 사본에 결함을 **하나씩** 심는다 —
   V1 본문 폰트 하한 미달(긴 산문을 22px 미만으로) · V2 원고 아이콘 누출 · V3 내부 작업
   라벨 누출 · V4 빈 `asset-slot`. **메인인 이유**: 결함의 위치·형태 정밀도가 측정 유효성을
   결정하므로 게이트 담당자가 직접 심는다(각 2~3줄 편집이라 위임 실익도 없다).
3. **게이트 실측** (메인): `CREATE_SLIDES_COURSE=likelionSKU` 지정 하에 정상본 1 + 변형 4에
   검증 실행. 명령 정본은 `references/검증-명령-지도.md` §2(verify_deck·러너)·§3(브라우저
   렌더·타이포 감사) — 여기 복제하지 않는다. 판정 줄·종료코드 원문을 결과 문서에 수집.

**판정 기준**: 정상본 PASS ∧ 변형 **4/4 검출**. 미검출(미탐)이 나오면 **게이트를 고친다** —
결함을 빼거나 기준을 낮추지 않는다. 검사기를 고치게 되면 「판정 건수·미판정 건수 출력」
규율(AGENTS 2026-08-24 집행)을 따른다.

#### E② 토큰 값 ↔ 규칙 하한 대조 (메인)

테마의 `--fs-*`·`--lh-*`·`--sp-*`를 R-TYPE-01 역할별 하한(본문 22 · 박스 설명 20 · 표 17 ·
라벨 14 · 배지 11 — 정본 `kit/guide/토큰-치트시트.md`)과 대조. A안 설계상 default 값
유지라 자동 충족이 **예상**되지만, 예상을 결과로 쓰지 않는다 — 실측 대조표를 결과 문서에
남긴다. 아울러 `python scripts/verify_declared_vs_enforced.py`로 선언↔집행 정합 확인.

### 단계 F — 회귀 전량 + 다과목 파급 수정 (메인)

- 회귀 **12모듈 전량**(총 219건 — 목록·명령 정본: `references/검증-명령-지도.md` §6.
  일부만 돌리면 나머지 게이트가 검증되지 않는다).
- `python scripts/verify_subject_isolation.py` · `python scripts/verify_declared_vs_enforced.py`.

**예상 파급(미리 밝힘)**: `courses/`가 2과목이 되는 순간 `_course_paths.resolve_course()`는
과목 미지정 호출에 `AmbiguousCourseError`를 던진다(2026-08-24 P0 — **의도된 fail-loud**,
조용히 첫 과목을 고르면 남의 과목을 검증하고 PASS를 내기 때문). 기존 테스트·스크립트 중
과목 미지정으로 실 저장소를 읽는 경로가 있으면 새로 깨질 수 있다.

**수정 방침(사용자 규율)**: 기준을 낮추지 않는다. 테스트가 다중 과목을 올바르게 다루도록
고친다 — 호출부에 과목 명시(`CREATE_SLIDES_COURSE` 또는 `course=` 인자) 또는 전수 순회
API(`profile_paths()`) 전환. **AmbiguousCourseError를 삼키는 방향의 수정은 금지**(그 예외가
바로 미탐 방지 장치다). 수정 파일·내용 전부 최종 보고에 포함.

### 단계 G — 마감 (메인)

1. 관문 실측 결과를 `plans/likelionSKU-theme/RESULTS.md`로 기록(판정 줄 원문 · 종료코드 ·
   미탐/오탐 계수).
2. `.agents/agent-memory/create-slides/MEMORY.md` 갱신 — `## 미해결`에서 해결 항목 삭제,
   테마 등재 사실 등재. 사용자 memory(`~/.claude/.../memory/`)에도 등재 사실 1줄.
3. `kit/guide/테마-계약.md`는 원칙 문서라 테마명 열거가 없으면 수정 불요 — 확인만 한다.
4. **저장소 밖 임시 파일 0개 확인**(시험 덱·변형본 전부 `tmp/` 안 — 옮기는 것이 아니라
   처음부터 밖에 만들지 않는다). `git status --short`로 범위 밖 변경 0건 확인.

## 4. 완료 기준 (산출물 단위 — "다 했다")

| # | 산출물 | 상태 조건 |
|---|---|---|
| 1 | `.gitignore` | `likelionSKU/` 등재, 단계 0 단독 커밋 완료 |
| 2 | `kit/themes/likelionSKU/tokens.css` | 99토큰 · 이름 집합이 `deck.css :root`와 완전 일치 · 색 49개만 값 변경 · 헤더에 브랜드 문자열 없음 |
| 3 | `courses/likelionSKU/profile.md` | 스키마 §1~§8 전 절 존재 · §5 `테마: likelionSKU` 포인터 · §8 리터럴(과목 폴더명 제외) |
| 4 | `courses/likelionSKU/이미지규약-clay-v2.md` | 4블록 계약 + 두 코발트 구분 절 + 네이밍·배치 규칙 |
| 5 | `plans/likelionSKU-theme/PLAN.md`(본 문서) + `RESULTS.md` | 관문 실측 원문 기록 |
| 6 | 테스트 다과목 수정본(발생 시) | 수정 파일·내용이 최종 보고에 명시 |
| 7 | memory 2곳 갱신 | agent-memory `## 미해결` 정리 + 사용자 memory 인덱스 |
| 8 | 커밋 | 전 변경이 `feat/likelionsku-theme`에 단계별 커밋(§9) · **push 없음** |

## 5. 성공 기준 (실측 단위 — "제대로 됐다")

| # | 기준 | 증거 형태 |
|---|---|---|
| ⓐ | 뮤테이션 매트릭스: 정상본 PASS ∧ 변형 **4/4 검출** | 5회 실행의 판정 줄·종료코드 원문(RESULTS.md) |
| ⓑ | 토큰↔하한 대조: R-TYPE-01 전 항목 충족 | 대조표(RESULTS.md) |
| ⓒ | 회귀 12모듈 219건 **전량 PASS** — 2번째 테마·2번째 과목 추가로 인한 회귀 0 | 모듈별 실행 결과·종료코드 |
| ⓓ | `verify_subject_isolation.py` · `verify_declared_vs_enforced.py` PASS | 종료코드 |
| ⓔ | 저장소 밖 임시 파일 **0개** · `git status --short`에 범위 밖 변경 0건 | 종료 시 계수 확인 |

실행하지 못한 검증이 생기면 **못 한 사실과 이유**를 보고에 적는다(완료의 정의 5항).

## 6. 담당 배정 요약 (독립성 · 병렬성 · 게이트 필요성 기준)

| 단계 | 담당 | 모델·effort | 한 줄 근거 |
|---|---|---|---|
| 0 격리 커밋 | 메인 | — | 2줄 편집, 위임 오버헤드 > 작업 |
| A 테마 토큰 | 메인 solo | — | 판단 무겁고 토큰 가벼움 + 조사 결과가 메인 컨텍스트에 이미 있음 |
| B 프로필 | 워커 | sonnet · **medium** | 독립·자기완결(원본 ~250줄 재독을 메인 창에서 격리); 스키마 준수 + 격리 원칙 이해 필요라 low 부족 |
| C clay v2 | 워커 | sonnet · **low** | 기계적 이식·전사; B와 파일 달라 **병렬** |
| E①-1 시험 덱 | 워커 | sonnet · **high** | 어휘·계약 준수가 측정 유효성의 성립 조건 — 조립 실수 = 관문 재실측 |
| E①-2 결함 심기 | 메인 | — | 결함 위치·형태 정밀도가 측정을 결정 — 게이트 담당자가 직접 |
| E①-3·E② 실측 | 메인 | — | 게이트 판정은 메인 몫(하네스 규율) |
| F 회귀·파급 수정 | 메인 | — | 실패 원인 판단·테스트 수정은 저장소 규율 이해 필요 |
| G 마감 | 메인 | — | memory 정리·보고는 위임 불가 |

## 7. 워커 규율 (모든 워커 프롬프트에 그대로 명시)

1. **임시·중간 파일은 저장소 안 `tmp/`에만 만든다.** 시스템 임시 폴더(`%TEMP%`·`AppData`·
   플랫폼 스크래치패드)에 두지 않는다.
2. **단일 라이터 allowlist** — 아래 파일 외 쓰기 금지:
   - 워커B: `courses/likelionSKU/profile.md` 1개
   - 워커C: `courses/likelionSKU/이미지규약-clay-v2.md` 1개
   - 워커E①: `tmp/theme-mutation/` 아래만
3. 읽기는 자유(원본 `likelionSKU/` 포함). 원본 파일은 **읽기 전용** — 수정 금지.
4. 반환은 3천 자 이내 요약 + 산출물 경로. 확인하지 않은 것을 사실처럼 쓰지 않는다.

## 8. 검증 명령 (단계별 — 전체 정본은 지도)

| 시점 | 명령 |
|---|---|
| A 직후 | `python -m unittest tests.test_theme_contract` |
| B 직후 | `python scripts/verify_subject_isolation.py` |
| E① | 지도 §2·§3 (verify_deck · run_deck_checks · 브라우저 감사) — `CREATE_SLIDES_COURSE=likelionSKU` |
| E② | 하한 대조(토큰-치트시트 대조표) + `python scripts/verify_declared_vs_enforced.py` |
| F | 회귀 12모듈(지도 §6 — 모듈 명시 실행, discover 불가) + 격리·정합 2종 |

## 9. 커밋 계획 (단계별 복구 지점)

1. `chore(격리): likelionSKU/ gitignore 등재 + 테마 등재 계획` — 단계 0 + PLAN.md
2. `feat(테마): likelionSKU 테마 신설 — 색 49토큰 교체, 비색 50토큰 default 유지` — 단계 A
3. `feat(과목): likelionSKU 과목 프로필 + clay v2 이미지 규약` — 단계 B·C
4. `test(테마): likelionSKU 등재 관문 2종 실측 + 다과목 파급 수정` — 단계 E·F (테스트 수정 발생 시 사유를 본문에)
5. `docs(memory): likelionSKU 테마 등재 기록` — 단계 G

각 커밋은 관련 verify 통과 후에만. main 병합·push 없음.

## 10. 리스크와 대응

| # | 리스크 | 대응 |
|---|---|---|
| 1 | 2과목 진입으로 `AmbiguousCourseError`가 기존 테스트·훅에서 신규 발화 | §F 방침 — 호출부에 과목 명시/전수 순회 전환. 예외를 삼키는 수정 금지 |
| 2 | 격리 리터럴 오탐(테마명 = 과목명 동일 문자열) | 과목 폴더명 문자열을 §8에 등재하지 않음 + tokens.css 헤더에 브랜드 문자열 배제 |
| 3 | 뮤테이션에서 미탐 발견(게이트가 결함을 못 봄) | 게이트를 고친다(결함 제거·기준 인하 금지). 검사기 수정 시 판정/미판정 계수 출력 규율 준수 |
| 4 | 로고 파일: 원본은 gitignore 대상이라 경로 참조 시 배포·조립에서 끊길 수 있음 | 프로필에는 원본 경로를 기록하되, 실제 덱 제작이 시작되는 시점에 `courses/likelionSKU/자산/`으로 복사 반입(이번 범위에서는 참조 기록만 — 바이너리 반입은 덱 작업 때 판단) |
| 5 | ◇ 파생 4건의 값 판단 오류 | 확정 시 대비 확인 + 이 문서에 확정값·근거 추기. 뮤테이션 시험 덱이 실사용 검증을 겸함 |
| 6 | 회귀 환경 결손(fontTools 등) | 지도 §6 경고 준수 — 로드 실패는 SKIP이 아니라 복구 후 재실행 |

## 11. 부수 발견 (이번 범위 밖 — 기록만)

원본 저장소 자체의 문제로, 우리 작업 대상이 아니다. 사용자가 원본을 손볼 때 참고:
- BM 덱 표지 "WEEK 11."·"11주차 기획시간!" — 16주차 세션인데 템플릿 잔존값
- `세션/BM_수익모델/dist/` 배포본이 루트 배포본보다 15시간 구버전
- `세션/바이브코딩/_redirects`가 존재하지 않는 `바이브코딩_강의덱_배포.html`을 참조
- `.omc/project-memory.json`의 projectRoot가 옛 경로(`Desktop\BM`)
- 스타터가 참조하는 `img/slides/s02_intro.png` 미존재(주제별 신규 생성 전제 — 의도된 공백)
