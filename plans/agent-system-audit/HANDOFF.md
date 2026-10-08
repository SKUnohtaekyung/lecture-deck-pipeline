# 에이전트 시스템 개편 — 완료 기록

2026-10-08에 끝났다. 모든 Phase가 독립 검토에서 PASS했다. 기준과 판정 기록 전문은 `EXECUTION.md`(끝의 「종결」 절이 요약이다), 명세는 `VERIFICATION_AND_MIGRATION.md`다. **커밋은 하지 않았다.**

## 무엇이 바뀌었나

| 바뀐 것 | 어디 | 효과 |
|---|---|---|
| 열린 일의 정본이 `MEMORY.md`의 `## 미해결`(547줄)에서 `STATE.md`(색인 12행 + 상세)로 | `STATE.md`, `AGENTS.md`·`README.md`·하네스 문서의 포인터 6곳 | 같은 질문 3회에서 사용자 결정 대기 7건 중 찾은 수가 15/21 → 21/21 |
| 옛 `## 미해결`의 원문 414줄을 버리지 않고 교훈과 이력으로 나눔 | `MEMORY.md`의 `## 이관된 교훈 (2026-10)`, `_dev/설계기록/MEMORY-이력-2026-10.md` | 줄 단위 무손실(검토자 전수 대조) |
| `STATE.md` 커밋 게이트 | `.githooks/_gate.py`의 `check_state_file`, `tests/test_state_gate.py` | 색인 40행 초과·선언 크기 초과·확인일 빈 칸이면 커밋 차단 |
| 같은 지침을 한 세션에 되풀이 주입하지 않음 | `scripts/hook_slide_guard.py`, `.claude/settings.json`(압축 때 초기화 훅 1개 추가) | 30분 안에는 다시 넣지 않는다. 압축되면 바로 다시 넣는다. 서브에이전트는 따로 센다 |
| 작은 창에서 잰 렌더 증거를 무효로 처리 | `scripts/receive_audit.py`, `scripts/run_deck_checks.py` | 1280×720 미만 창의 증거는 「측정 무효」. 지금 해당하는 것은 FRAME `1주차/deck-audit.json` 하나 |
| 낡은 수치 정정 | 지도 §6, `AGENTS.md`, `README.md` | 회귀 「10모듈 219건」 → 실제 13모듈 410건 |
| FRAME 검사 FAIL의 분류와 처분 제안 | `frame-gate-reconciliation.md` | 문서만. FRAME 파일은 고치지 않았다 |

## 검증값 (2026-10-08 마지막 확인)

- 회귀 13모듈 `Ran 410 tests … OK`. `verify_skill_setup.py`·`verify_declared_vs_enforced.py` 종료코드 0. `check_state.py` RESULT PASS.
- HEAD `a979b42`, staged 0, stash 1. `frame_guard.py` 출력이 기준선과 같다. `courses/` 아래에 이 작업이 고친 파일 0개.

## 사용자가 정할 것

1. **커밋할지.** 바뀐 파일 목록은 `EXECUTION.md` 「종결」 절에 있다. 커밋 때 `STATE.md` 게이트가 처음으로 실제 pre-commit 경로에서 돈다(지금까지는 함수와 스크립트를 직접 실행해 확인했다).
2. **`STATE.md`의 사용자 몫**(S01~S06, S08~S10).
3. **FRAME**: `frame-gate-reconciliation.md` 「보류를 풀 때의 순서」 1단계 — 강의자료 파일을 고치는 일들이라 물어야 한다.
4. 명세의 TASK-014(완료 과목 전용 에이전트 정리).

## 확인되지 않은 채 남은 것

- 실제 Claude Code에서 압축 때 `SessionStart(compact)` 훅이 도는지, 그때의 `session_id`가 편집 훅과 같은지. 같은 모양의 입력으로 스크립트를 직접 불러서만 시험했다. 다음에 긴 세션에서 압축이 일어난 뒤 과목 파일을 고칠 때 지침이 다시 들어오는지 보면 확인된다.
- `/clear`·resume 뒤에 `session_id`가 유지되는지. 유지되면 30분 안에는 주입이 생략될 수 있다.
- 1280×720이 슬라이드 전체가 창에 들어오는 충분조건인지(브라우저 미확인).
- 토큰 절감은 없다(입력 합 +7%). 기대하지 않는다.

## 주의

- `_dev/설계기록/MEMORY-스냅샷-2026-10-08.md`는 이관 전 `MEMORY.md`의 유일한 사본이다. 커밋하기 전에는 지우지 않는다.
- `migrate_memory.py`를 다시 돌리지 않는다. 돌리면 `MEMORY.md` 3행의 문구 수정이 되돌아간다.
- 지침 주입 간격은 환경변수 `HOOK_REINJECT_MINUTES`로 바꾼다. `0`이면 종전처럼 매번 주입한다.
- `tmp/audit-1007/`, `tmp/audit-1008/`, `tmp/review/`에 근거 자료와 검토자 작업 파일이 있다(gitignore). `frame-gate-reconciliation.md`의 건수 근거가 `tmp/audit-1008/phase6/`에 있으므로, 지우면 `repro.py`의 절차로 다시 만들어야 한다.

## 이 작업에서 정한 작업 규칙

- Phase마다 새 검토자가 판정한다. 검토자는 이전 판정 기록과 다른 검토자의 폴더를 보지 않는다. 같은 Phase에서 FAIL이 3번이면 멈추고 보고한다.
- 전수 확인이 필요한 기준은 줄 단위 장부를 먼저 만들고 검토자가 장부를 공격하게 한다(`state-coverage.tsv`).
- 기계로 셀 수 있는 기준은 스크립트로 묶는다(`check_state.py`).
- 검토 지시문에 「기준 위반」과 「기준 밖 발견」을 구분하라고 적는다.
- 검토가 회귀를 돌리는 동안에는 추적 파일을 고치지 않는다. 이 작업에서 두 번 어겼고 한 번은 검토자의 회귀를 깨뜨렸다.
- 백슬래시가 든 코드를 셸 heredoc으로 쓰지 않는다. 파일로 쓴다.
- `grep -r`은 대상 경로를 지정한다. `.claude/worktrees/`에 옛 사본이 많다.
