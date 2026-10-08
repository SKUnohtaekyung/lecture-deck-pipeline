# baseline — 개편 전 기준 상태 (2026-10-08)

- `git_baseline.txt`: 작업 시작 시 Git 상태.
- `frame_guard.py` / `frame_guard_before.txt`: FRAME 미커밋 작업의 지문과 시작 값(읽기 전용 스크립트).
- `checks/`: 개편 전 회귀 12모듈·`verify_skill_setup`·`verify_declared_vs_enforced` 출력. 셋 다 종료코드 0.
- `logs/*.py`: 세션 로그 재측정 스크립트. `measure.py`가 `~/.claude/projects/`의 로그를 읽어 같은 폴더에 `measure.pkl`을 만들고 `rep1~3.py`가 그것을 읽는다. `measure.pkl`(로그 파생물)은 여기 두지 않았다. 그 대신 2026-10-08에 뽑은 결과를 `rep1_output.txt`~`rep3_output.txt`로 남겼다.
- `memory/`: `MEMORY.md` 소절 분해(워커 산출).

태그 `audit-baseline-2026-10-08`은 커밋 `a979b42`를 가리킨다. 태그는 커밋된 상태만 담으므로, 미커밋 수정이 든 `MEMORY.md`의 원문은 `_dev/설계기록/MEMORY-스냅샷-2026-10-08.md`가 유일한 사본이다.
