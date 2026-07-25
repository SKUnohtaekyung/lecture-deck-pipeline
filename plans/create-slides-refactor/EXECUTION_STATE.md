# Execution State

- Plan ID: CSR-2026-07
- Plan Version: 1.0.0
- Current Branch: `refactor/create-slides`
- Current Commit: `eb49d2f` (P0 커밋 전 · 게이트 통과 후 갱신)
- Current Phase: **P0 (기준선 고정)**
- Last Completed Task: TASK-P0-003
- Active Task: TASK-P0-004 (진행 중 → 완료 시 P0 게이트·커밋)
- Completed Validation:
  - 기준선 5종 기록 완료(BASELINE_REPORT §3 / 원문 BASELINE_OUTPUTS.txt)
  - V-26(동결): `git status --short`에 `sessions/1주차/` 0건 — 통과
- Failed Validation:
  - 없음(P0는 기록 Phase). 단 **기준선 자체의 FAIL 2종은 아래 Known Failures로 이월**
- Existing Known Failures:
  - **KF-1 `verify_skill_setup.py` FAIL 2건** — `Codex·Claude MEMORY.md가 없거나 바이트 단위로 불일치` / `… SHA-256 불일치`. 원인: `.claude` 사본(119줄/16,140B)이 `.agents` 정본(159줄/29,447B)에서 분기. 고유 정보 0건 확인. → P1-001·002에서 해소
  - **KF-2 `.agents` 메모리 스테일 2건** — ① `확진된 오탐 1건(2026-07-21)` rgba 항목(코드는 `8c07f2f` `kit_alpha_exempt`로 해소됨) ② `편집본 80장·배포본 72장` 계약 기록(실측·현행 코드는 75장·divider 6). → P1-003에서 해소
  - **KF-3 `verify_session_docs.py 2 --target 초안` FAIL** — `파일:초안.md — 파일 없음`. 실물은 `sessions/2주차/2주차_초안.md`(접두어). → P3-007(DEC-05)에서 해소
  - **KF-4 1주차 실덱 기존 결함(동결·검출 대상)** — PART 라벨 밀림 / 이미지 미배선 3·고아 4 / revision.css 19~21px 8장 / 노트 pn-no 불일치 의심 / 666px 초과 20장. 현행 verify_deck 47검사로는 **검출 0**(해당 검사 부재). → P6에서 검증 신설 + `sessions/_contracts/1주차.deck.contract.json`의 `known_violations` 등재
  - **KF-5 `evals/team-skills-eval.json` 픽스처 설명 스테일** → P3-009에서 해소
  - **P6-005 노트 검사 결과**: 미실행(P6에서 기록)
- Baseline Worktree (P0 시점 `git status --short`):
  ```
  ?? GPT_강의설계_보조에이전트/     ← untracked · 절대 변경 금지 · git clean 전역 실행 금지
  ?? plans/                        ← 이 계획·실행 산출물(P0에서 커밋 대상)
  ```
  추적 파일 미커밋 변경: **0건**
- Open Corrections: 없음
- Files Currently Owned: `plans/create-slides-refactor/{BASELINE_REPORT.md, BASELINE_OUTPUTS.txt, EXECUTION_STATE.md}` (Opus)
- Workers Active: 없음
- Next Task: **TASK-P1-001** (`.claude` 메모리를 3줄 포인터로 교체)
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
| P0 기준선 | 진행 중 | `refactor-p0-start` | — |
| P1 기준선 수리 | 대기 | — | — |
| P2 개명 | 대기 | — | — |
| P3 정본화·충돌·접두어 | 대기 | — | — |
| P4 Core·로드 재편 | 대기 | — | — |
| P5 컴포넌트 | 대기 | — | — |
| P6 검증 신설 | 대기 | — | — |
| P7 회귀·채택 | 대기 | — | — |
