# Execution State

- Plan ID: CSR-2026-07
- Plan Version: 1.0.0
- Current Branch: `refactor/create-slides`
- Current Commit: `b04dde2` (P4) → P6 커밋 후 갱신
- Current Phase: **P6 (검증 신설) — 완료, 커밋 대기**
- Last Completed Task: TASK-P6-008
- Active Task: TASK-P6-009 (게이트·커밋)
- Completed Validation:
  - 기준선 5종 기록 완료(BASELINE_REPORT §3 / 원문 BASELINE_OUTPUTS.txt)
  - V-26(동결): `git status --short`에 `sessions/1주차/` 0건 — 통과 (P0·P1)
  - **V-01 통과**: `verify_skill_setup.py` PASS=78 / FAIL=0 (기준선 PASS=77·FAIL=2 → FAIL 2건이 신규 PASS 1건으로 대체. Compare-Object로 다른 검사 집합 변화 0 확인). P2 개명 후 재실행도 PASS=78 / FAIL=0
  - **V-02 통과(P2-012)**: 저장소 전수 `vibecoding-deck` 잔존 81건 / 17파일 — 전량 허용 목록 소속. ⑧군(누락군) 0건, 조사 오류 0건. W-CHECK 독립 수집 + Opus 판정
  - **V-05 통과**: 팀 스킬 10파일 구명 0건, 체이닝 지목이 `/create-slides`로 교체됨
  - **V-20 통과**: evals 3파일 JSON 파싱 무예외, 케이스 수 불변(routing 8 + contract 6 = 14, 전후 동일), `폐기됨` 0건
  - **V-07 통과(충돌 6건 중 5건)**: CONFLICT-001 색 정본 단일화(AGENTS.md → `kit/guide/디자인시스템.md`) · 002 GIF·녹화 DEC-07 문안 · 003 세로예산 단일 표 · 004 charts 6→8(실측 확인) · 005 폰트 하한 단일 표. **CONFLICT-006은 계획대로 P4-002**(단 `kit/guide/토큰-치트시트.md`의 같은 오참조 `§밀도`→`§0-6`은 P3에서 함께 정정)
  - **V-09 통과**: `sessions/README.md`에 `_contracts` 규약 3건·`동결` 3건·`deck.contract.json` 5건
  - **V-10 통과**: `verify_session_docs.py 2 --target 초안` = **7 PASS / 0 FAIL**(기준선 FAIL=1/PASS=1에서 개선). 1주차 실행 시 `INFO: 레거시 무접두어 초안 사용` 폴백 출력 확인
  - **V-11 부분 통과(문서측)**: 토큰-치트시트 R-TYPE-01·02·03 표 신설, 디자인시스템 가독성 표 정정. 코드측 `--fs-*` 정의는 P5-001
  - **회귀 무변화**: `verify_deck.py` 1주차 = 47 PASS / 0 FAIL / 0 WARN (P0 기준선과 동일). unittest 25 tests OK
  - **V-06 통과(P4-006)**: RULE_MIGRATION_MAP 기계 대조 40항 + 중복 방지 2항 전부 OK. 죽은 링크 0(phases 18·SKILL 9). 상세는 `RULE_MIGRATION_MAP.md` 「대조 결과」
  - **V-08 통과**: `.agents` MEMORY에서 `80장|72장|재캡처|666px 초과|family_signature` **전부 0**(KF-2R 잔여 해소). 159 → 138줄
  - **V-12 통과**: `verify_kit.py` PASS · `patterns.css`에 `.terminal-dark` 존재 · `revision.css` diff 0
  - **V-23 통과**: `references/phases/05-시각화.md`에 R-D3-01 존재 · `kit/vendor` 디렉터리 부재(DEC-08 준수)
  - **V-24 통과**: `tests.test_deck_pipeline` + `tests.test_image_pipeline` = 25 tests OK(기준선 동등)
  - **V-13 통과(P6)**: 계약 외부화 후 1주차 = **FAIL 0 · WARN 5 · PASS 51**. 기준선(FAIL 0 · WARN 0 · PASS 47) 대비 FAIL 동등, 검사 +4종. `verify_deck.py`의 1주차 하드코딩 리터럴은 전부 `sessions/_contracts/1주차.deck.contract.json`으로 이전됐고, 계약 없는 주차는 WARN 1건만 남기고 통과(픽스처 테스트로 확인)
  - **V-14 통과**: PART 정합 검사가 1주차 known 15장을 WARN으로 검출(FAIL 0), 고장 픽스처 `broken/part-01.html`에서는 FAIL 산출
  - **V-15 통과**: 이미지 배선 검사가 1주차 known 2건 WARN·고아 14건 WARN, 고장 픽스처 `broken/unwired.json`에서 FAIL(W1)·고아 WARN(W9) 산출
  - **V-17 통과**: 세션 CSS 하한 린트가 1주차 known 셀렉터 3건을 WARN으로 검출(FAIL 0)
  - **V-16 통과**: `scripts/measure_render.js` `node --check` 통과, `references/phases/08-검증.md`에 실행 절차 절 연결(scale=1 선확인·전 장 순회·known_violations 대조). 헤드리스 미도입(DEC-03 준수)
  - **V-18 통과(검출=성공)**: `verify_notes.py` 1주차 = **불일치 36건 / exit 1**. §7.8의 "pn-no 구버전 의심"이 실측으로 **확정**됐다 — 27번 이후 전 구간에서 노트 `pn-no` N의 제목이 덱 N−1의 제목과 일치하는 **일관된 한 칸 밀림**. 1주차 동결이므로 수정하지 않고 기존 결함으로 기록
  - **V-19 통과**: `verify_session_docs.py 2 --target 초안` = **8 PASS**(기존 7 + 신규 번호유일성 106개 전부 유일). `report_draft_sync.py 2`는 덱 부재를 알리고 exit 0(판정 없음 — 규약대로)
  - **V-25 통과**: `tests.test_deck_contract` = **11 tests OK**. 3단 탐색(동폴더·`_contracts` 폴백·부재 WARN)·PART FAIL 재현·배선 FAIL 재현·고아 WARN·접두어 우선/폴백 전부 검증. 픽스처는 1주차 파일을 복사·참조하지 않음(과적합·동결 준수)
  - **V-24 재확인(P6)**: `test_deck_pipeline` + `test_image_pipeline` + `test_deck_contract` = **36 tests OK**
- Failed Validation:
  - 없음. 단 **기준선 자체의 FAIL 2종은 아래 Known Failures로 이월**
- Existing Known Failures:
  - ~~**KF-1 `verify_skill_setup.py` FAIL 2건**~~ — **P1-001·002에서 해소됨.** 원인: `.claude` 사본(123줄/16,140B)이 `.agents` 정본(159줄/29,288B)에서 분기. 고유 정보 0건 확인 후 3줄 포인터(129B)로 교체하고, 검사를 바이트·해시 동일성 → 포인터 규약(5조건)으로 교체
  - ~~**KF-2 `.agents` 메모리 스테일 2건**~~ — **P1-003에서 해소됨.** ① rgba 오탐 항목 → `kit_alpha_exempt` 해소 사실 1문장으로 축약해 「브라우저 전수검증」 절로 이동 ② `편집본 80장·배포본 72장` → `편집본·배포본 모두 75장·divider 6(2026-07-24 13차 개정 현행)` (현행 `verify_deck.py` 코드값과 대조 확인)
  - **KF-2R 잔여(P4-005 예정)** — `80장`·`72장` 문자열이 `.agents` 메모리 130·135행(**1주차 상태 블록**)에 남아 있다. P1-003의 "정확한 변경: 위 2건만·다른 항목 무변경" 지시 때문에 P1에서 손대지 않았고, 해당 블록은 **TASK-P4-005 ③이 통째로 삭제**한다. 따라서 V-08(`80장|72장|재캡처|666px 초과` = 0)은 설계대로 **P4 완료 시점에 충족**된다(V-08 범위 = P1·P4)
  - **KF-3 `verify_session_docs.py 2 --target 초안` FAIL** — `파일:초안.md — 파일 없음`. 실물은 `sessions/2주차/2주차_초안.md`(접두어). → P3-007(DEC-05)에서 해소
  - **KF-4 1주차 실덱 기존 결함(동결·검출 대상)** — PART 라벨 밀림 / 이미지 미배선 3·고아 4 / revision.css 19~21px 8장 / 노트 pn-no 불일치 의심 / 666px 초과 20장. 현행 verify_deck 47검사로는 **검출 0**(해당 검사 부재). → P6에서 검증 신설 + `sessions/_contracts/1주차.deck.contract.json`의 `known_violations` 등재
  - ~~**KF-5 `evals/team-skills-eval.json` 픽스처 설명 스테일**~~ — **P3-009에서 해소됨**
  - **KF-6 `evals/evals.json` 케이스 4 성립 불가(신규 발견 · 기존 결함)** — `icon-routing-hint-reveal-and-presenter-notes`가 학생 덱의 접힘 `.hint-reveal`에 `🗣` 원문을 두고 `💬`·`👀`를 HTML 주석으로 넣으라고 어서션하는데, 규칙은 **학생 덱 `.hint-reveal`·이모지 0**(verify FAIL)을 요구한다. `git show refactor-p4-start:SKILL.md` 대조 결과 **개편 전 SKILL.md도 4곳에서 동일한 규칙**이었으므로 **P4 회귀가 아니라 이전 세대 규약이 남은 기존 결함**이다. `evals/evals.json`은 이번 계획의 P4 수정 대상이 아니라 고치지 않고 보고한다 → **후속 작업 후보**
  - **P6-005 노트 검사 결과**: 미실행(P6에서 기록)
- Baseline Worktree (P0 시점 `git status --short`):
  ```
  ?? GPT_강의설계_보조에이전트/     ← untracked · 절대 변경 금지 · git clean 전역 실행 금지
  ?? plans/                        ← 이 계획·실행 산출물(P0에서 커밋 대상)
  ```
  추적 파일 미커밋 변경: **0건**
- Open Corrections: 없음 (P2에서 2건 발생·완결 — `TASK-P2-011-C1` 조사 정정 3곳 / `TASK-P2-012-C1` ⑧군 3파일 교체. 둘 다 C1에서 통과, C2 미사용)

## P2-012 허용 목록 판정 (Opus)

계획 §P2-012의 허용 목록 ①~⑧에 더해 다음을 판정했다.

| 구분 | 파일·건수 | 판정 |
|---|---|---|
| ① `_dev/설계기록/**` | 5파일 11건 | 허용(역사 기록) |
| ② `sessions/1주차/**` 3파일 4건 · `sessions/2주차/**` 1파일 2건 | 6건 | 허용(동결·역사) |
| ③ `GPT_강의설계_보조에이전트/**` | 0건 | 해당 없음(언급 0 확인) |
| ④ `outputs/create-slides-layout-atlas.html` | 4건 | 허용(rename만·내용 무변경 R100 확인) |
| ⑤ `AGENTS.md` 1건 · `skills/README.md` 1건 | 2건 | 허용(개명 병기 — 각 정확히 1건) |
| ⑥ `.agents/agent-memory/create-slides/MEMORY.md` | 3건 | 허용(본문 과거 서술) — **단 1행 H1 제목 `# MEMORY — vibecoding-deck 오답노트`는 아래 이월 항목 참조** |
| ⑦ `kit/CHANGELOG.md` | 2건 | 허용(역사 기록) |
| ⑧ 누락군(교체 대상) | **0건** | `references/이미지-디렉션-프롬프트.md`·`kit/styles/legibility.css`·`scripts/verify_deck.py`·`kit/guide/디자인시스템.md` 전부 교체 완료 |
| **⑨ `plans/create-slides-refactor/**`(신규 판정)** | 53건 | **허용** — 계획서 본문은 §1 "실행 중 이 문서를 수정하지 않는다"가 지배하므로 변경 금지가 정답. 허용 목록에 명시돼 있지 않아 Opus가 추가 판정 |

**이월 1건 → P4-005에서 처리**: `.agents/agent-memory/create-slides/MEMORY.md` 1행 H1 제목이 아직 구명이다. P2-004가 이 파일의 **본문 무변경(R100)** 을 요구해 P2에서 손대지 않았고, P4-005에서 Opus가 같은 파일을 3분할 재작성하므로 그때 `# MEMORY — create-slides 오답노트`로 정정한다.

## 계획과의 차이 (P2 기록)

| 항목 | 계획 | 실제 | 처리 |
|---|---|---|---|
| P2-007 앵커 수 | mjs 내 2곳 | **5곳**(파일명 2 + 표지 문구·`<small>`·`<title>` 3) | 객관 통과 기준이 `= 0`이고 §4가 "내부 title은 다음 재빌드 시 반영"이라 했으므로 Opus가 5곳 전량 교체로 판정 |
| P2-009 앵커 수 | AGENTS.md 8곳 | **16건/8줄**(2개 줄에 다중 매치) | 지시가 "전 참조 교체"이므로 전량 처리 |
| 조사(助詞) 결합 | 계획에 없음 | `create-slides`는 모음 종성이라 `은/이/으로` → `는/가/로` 정정 필요 5건 | 개명의 기계적 귀결로 판정해 정정(신규 문안 판단 아님) |
| ⑧군 4파일 수정 Phase | §12 표상 P3·P6 소유 | P2에서 수정 | P2-012 본문이 "발견 시 즉시 교체 지시"를 규정하므로 계획 내 |

## 계획과의 차이 (P6 기록) — 사용자 결정 1건 포함

### PART 정합 검사(TASK-P6-003 ①)의 전제 오류

계획 §7.8·§9 RESULT-001은 1주차 결함을 "PART **라벨 밀림**"으로 보고, P6-003 ①은 본문 `.s-team`의 "PART n"이 직전 divider 위치 인덱스와 일치하는지 검사하라고 규정했다.

**실측 결과 그 전제가 틀렸다.** `sessions/1주차/강의덱.html:1323-1324`의 스타터 JS가 본문 `.s-team`을 런타임에 **통째로 덮어쓴다**:

```js
if(!fixed && curPart>=1 && totalParts>=1){
  var team = s.querySelector('.s-head .s-team');
  ... team.innerHTML = '<span class="lbl">PART '+curPart+' / '+totalParts+'</span>' ...
```

`curPart`는 divider 누적 개수(= 위치 인덱스)다. 따라서 **정적 라벨은 화면에 표시되지 않으며**, 라벨 불일치는 시각적 결함이 아니라 **소스 불일치**다(작성자가 의도한 파트와 실제 배치가 어긋났다는 신호로는 유효).

| 기준 | 1주차 불일치 |
|---|---:|
| 위치 인덱스(계획 정의) | **15장** |
| divider `P` 번호 | 5장 |
| 최초 분석이 등재한 값 | 4장 |

1주차는 divider ID가 `P1·P2·P3·P5·P6·P7`로 **P4가 결번**이라 `P5` 이후 구간의 정적 라벨이 위치 인덱스보다 1 크다.

**→ 사용자 결정(2026-07-26): 「계획대로 유지 + 14건 등재」.** 기대값은 계획 원문대로 위치 인덱스를 쓰고, 1주차 15장을 실측값으로 `known_violations.part_label_sequence`에 등재해 **1주차는 검출만·신규 주차는 FAIL**로 작동하게 했다. 계약 파일에 판정 근거를 `note`로 남겼다.

### 그 밖의 P6 차이

| 항목 | 계획 | 실제 | 처리 |
|---|---|---|---|
| 계약 JSON의 `강의덱_배포` 항목 | `slides`·`dividers`·`intro`만 | 현행 코드는 터미널·THANK YOU 검사도 **두 stem 모두**에 적용 | "현행 코드 값 그대로" 원칙을 우선해 `dark_terminal_slides`·`closing_text`를 배포본에도 기재 |
| `chk(True, ..., warn=True)` 스케치 | 계약 부재 시 WARN | `chk`는 `cond=True`면 항상 PASS라 WARN이 안 나옴 | 워커 지적 채택 — `chk(False, ..., warn=True)`로 실제 WARN 산출 |
| `orphan_manifest_slides` | 4건 | 실측 14건 | 실측값으로 갱신(고아는 등재 여부와 무관하게 항상 WARN이라 게이트 영향 없음) |
| 워커 초기 구현의 기대값 | 위치 인덱스 | divider `P` 번호로 구현 | Opus가 원본 HTML 독립 측정으로 발견해 교정 지시(C1) |

## 계획과의 차이 (P3 기록)

| 항목 | 계획 | 실제 | 처리 |
|---|---|---|---|
| **R-COLOR-03 앵커 부재** | P3-003이 "기존 규칙 항목에 ID만 병기"를 지시(배지 3종 규칙이 디자인시스템.md에 있다고 전제) | 디자인시스템.md에 **배지 3종 규칙이 아예 없었다**(당시 `kit/guide/토큰-치트시트.md`·AGENTS.md에만 존재) | §9가 R-COLOR-03의 정본을 디자인시스템.md로 지정하고 P3-001이 AGENTS.md를 그 정본 참조로 바꿨으므로, **문구 창작 없이 기존 문장을 전사**해 배치했다. ⚠️ **사용자 검토 요청 항목** |
| P3-005 앵커 문자열 | `catalog.html 6개` | 실제는 `` `catalog.html` **6개** `` (마크다운 강조 포함) | 동일 대상이라 그대로 진행 |
| charts README `aria 6/6` | 계획 범위 밖 | 6→8 정정 후 같은 줄에 `aria 6/6`이 남아 모순 | 실측(코어 8종 전부 `aria-label` 보유) 확인 후 `aria 8/8`로 정정 |
| P3-004 대조표 추가 모순 | "DEC-07 문안 1건" 전제 | 대조표에서 **반대·오인용 5건 추가 발견**(연령대 서술·오인용·제외 목록 5항 누락·소제목) | 계획의 "Opus가 개별 Correction 여부 판단"에 따라 **전량 정정**(§9 CONFLICT-002 완료 조건 = "대조표 모순 0"). 정본은 읽기만 함 |
| `kit/guide/토큰-치트시트.md`의 `§밀도` | CONFLICT-006은 SKILL.md만 지목 | 치트시트에도 동일 오참조 존재 | 같은 파일을 재작성 중이었고 `§0-6`이 실재 절임을 확인해 함께 정정 |
| W-DOCS 폴백 병기 위치 | "파일당 첫 등장 위치" | `skills/콘텐츠/SKILL.md`의 첫 등장은 frontmatter `description` | **본문 첫 등장으로 이동 승인** — `verify_skill_setup`이 정본↔어댑터 description 문자열 동일성을 강제하므로 description 변경은 라우팅 위험 |
- Files Currently Owned: `.claude/agent-memory/vibecoding-deck/MEMORY.md` · `.agents/agent-memory/vibecoding-deck/MEMORY.md` · `scripts/verify_skill_setup.py` · `plans/create-slides-refactor/**` (전부 Opus)
- Workers Active: 없음
- Next Task: **TASK-P6-001** (`sessions/_contracts/1주차.deck.contract.json` 작성 — 현행 `verify_deck.py` 하드코딩 값 기계 이전)
- Resume Instructions:
  1. `MASTER_EXECUTION_PLAN.md` → 이 파일 순으로 읽고 Next Task부터 재개한다(이전 대화 재독 금지).
  2. 검증 명령 실행 전 `$env:PYTHONIOENCODING='utf-8'`을 설정한다.
  3. Phase 시작마다 `git tag refactor-p<N>-start`, Phase 게이트 통과 후 Opus만 커밋한다.

## 실행 환경 고정값

| 필드 | 값 |
|---|---|
| `$PY` | 전역 `python` 3.12.10 (`.venv` 없음 · fontTools·Pillow 확인됨) |
| `<REGRESS>` | `C:\Users\miso\AppData\Local\Temp\cs-refactor-regress` |
| `<REGRESS>\baseline\` | 1주차 강의덱.html(180,021B)·강의덱_발표자노트.html(31,247B) |
| `<REGRESS>\work\` | `sessions\1주차\강의덱.초안\`(9파일) + `kit\`(38파일) — 재조립 가능 구조(P0 스모크 diff 0 확인) |
| 출력 인코딩 | 전 명령 `$env:PYTHONIOENCODING='utf-8'` |

## Phase 진행 표

| Phase | 상태 | 태그 | 커밋 |
|---|---|---|---|
| P0 기준선 | **완료** | `refactor-p0-start` | `b551fad` |
| P1 기준선 수리 | **완료** | `refactor-p1-start` | `1165a9a` |
| P2 개명 | **완료** | `refactor-p2-start` | `93aa644` |
| P3 정본화·충돌·접두어 | **완료** | `refactor-p3-start` | `82ac406` |
| P4 Core·로드 재편 | **완료** | `refactor-p4-start` | (아래 커밋) |
| P5 컴포넌트 | **완료** | `refactor-p5-start` | `84fe173` |
| P6 검증 신설 | 대기 | — | — |
| P7 회귀·채택 | 대기 | — | — |
