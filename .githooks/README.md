# .githooks/ — git pre-commit 게이트

## 왜 이 층이 있는가

이 프로젝트는 지금까지 Claude Code 훅(`.claude/settings.json`)으로만 규칙을 강제해 왔고, Codex 쪽 강제는 0이었다. git 훅은 어느 CLI로 커밋하든(Claude Code·Codex·사람이 터미널에서 직접) 커밋 시점에 실행되는 **유일한 공통 층**이다. 여기 있는 검사가 통과하지 못하면 커밋 자체가 막힌다.

## 설치

```
python scripts/install_hooks.py           # core.hooksPath를 .githooks/로 설정
python scripts/install_hooks.py --check   # 설정만 확인(바꾸지 않음)
```

`_gate.py`는 이 설치 스크립트가 아니라 **개별 클론마다 한 번씩 사람이(또는 세팅 스크립트가) 실행**해야 적용된다 — `core.hooksPath`는 git 설정이라 clone에 자동으로 딸려오지 않는다.

## 검사 표

`pre-commit`은 얇은 진입점이고, 실제 조건 분기는 전부 `_gate.py`(파이썬)에 있다. staged 목록은 `git diff --cached --name-only -z --diff-filter=ACMR`로 받는다.

| staged 패턴 | 실행 | 실패 시 |
|---|---|---|
| `kit/` 아래 변경 | `scripts/verify_kit.py` → `scripts/verify_declared_vs_enforced.py` | 차단 |
| `SKILL.md`(어디든) 또는 `skills/`·`.claude/skills/`·`.agents/skills/` 아래 | `scripts/verify_skill_setup.py` | 차단 |
| `*.css` | `scripts/hook_slide_guard.py --mode css-lint --stdin-paths` | 차단 |
| `courses/**/강의덱.html` | 같은 커밋에 그 덱의 `강의덱.초안/`(shard) 변경이 함께 staged됐는지 확인 | 차단(생성물 단독 커밋 금지) |
| `courses/**/강의덱_발표자노트.html` | 같은 주차 덱 경로를 유도해 `scripts/verify_notes.py` 실행. 경로를 유도할 수 없으면(덱 파일이 없음 등) 건너뛰고 경고만 | 유도 성공 시 차단 / 실패 시 경고만 |
| 항상 | `tmp/` 밖에 쌓인 미추적 잡파일 스캔 | 경고만(차단 아님) |

- 실행할 스크립트가 없으면 그 검사는 건너뛰고 경고한다(하드 실패 금지).
- 검사 하나가 예외로 죽으면 그 검사만 `ERROR`로 표시하고 나머지는 계속 돈다.
- 종료코드: 차단(FAIL) 사유가 1건이라도 있으면 1, 없으면 0.

## 한계 — staged 그대로가 아니라 워킹트리 그대로

모든 검사는 **워킹트리에 있는 현재 파일 내용**을 본다. git의 진짜 staged blob(`git show :path`)이 아니다. 파일을 부분적으로만 `git add`했다면(예: `git add -p`) 워킹트리 내용과 실제로 커밋될 staged 내용이 달라질 수 있고, 그 경우 이 게이트는 워킹트리 쪽 내용으로 판정한다. 워킹트리를 staged 상태에 맞춰 stash하는 식의 조작은 사용자의 손대지 않은 변경을 건드릴 위험이 커서 하지 않는다.

## 우회 방법

- 이번 훅만 건너뛰기: `git commit --no-verify`
- 이번 커밋에서 게이트 전체를 건너뛰기(코드 자체는 그대로 실행되지만 즉시 exit 0): `SKIP_DECK_GATES=1 git commit ...`

우회 가능함을 숨기지 않는다 — 이 층의 목표는 방탄이 아니라 "규칙 파일은 있는데 아무도 안 본다"는 잊어버림을 줄이는 것이다.

## python이 없는 환경

`pre-commit`은 `python`을 먼저 찾고, 없으면 `py`를 시도한다. 둘 다 PATH에 없으면 경고만 출력하고 exit 0 — 훅 인프라 문제로 사용자의 커밋 자체가 불가능해지지 않는다.
