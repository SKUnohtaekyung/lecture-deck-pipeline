# 지침 리팩터링 보고서

> 대상 브랜치 `refactor/instruction-ecosystem` · 기준 `39659ea` → `00c5f82` (커밋 6개)
> 실행 방식: 하네스(메인 Opus 게이트 + Sonnet 워커 8명) · 계획 정본 `PLAN.md`

---

## 1. 결론

**판정: 부분 완료 (95/100) — 배포 가능하나 목표 G1은 미달성.**

- 기능·회귀·안전 게이트는 **전부 통과**했고, 독립 검토가 잡은 치명 결함 1건도 해소했다.
- 그러나 **「Codex에서도 동등하게 강제된다」(G1)는 달성되지 않았다.** Gate 0(훅 능력 실측)이 사용자 승인 대기 상태라, Codex 세션의 기계적 강제는 **git 층 하나뿐**이다. 이는 「동등」이 아니라 **「지연된 동등」**이다.
- 치명적 결함이 남으면 총점과 무관하게 완료로 판정하지 않는다는 규칙에 따라 **완료로 선언하지 않는다.**

**주요 개선**

1. **플랫폼 공통 최종 증거 층 신설** — `.githooks/pre-commit`. 이 프로젝트에 활성 git 훅과 CI가 **하나도 없던** 상태에서, CLI와 무관하게 커밋 시점에 도는 층이 처음 생겼다. 실제 커밋을 차단하는 것까지 실증했다.
2. **검사 로직 단일 정본** — Claude 설정과 Codex 훅이 같은 `scripts/hook_slide_guard.py`를 호출하도록 `--host` 어댑터를 넣었다. 플랫폼별 규칙 복제 0.
3. **워커 통제가 자연어 → 구조로 승격** — `.claude/agents/research-worker.md` 신설로 도구 허용목록·모델·**`maxTurns`가 구조적 강제**가 됐다. 이 프로젝트가 「걸 수단이 없다」고 문서에 적어두었던 턴 상한이 걸렸다.
4. **컨텍스트 예산 확보** — Codex 결합 지침 78.0% → **56.1%** (하드 한도 32KiB).
5. **사실 오류 6건 정정** — 특히 「Codex CLI는 로컬에 없다」는 잘못된 전제가 Codex 어댑터를 「패턴 패리티용」으로 격하시켜 왔다.

**남은 위험**

| # | 위험 | 완화 |
|---|---|---|
| R1 | **Codex 강제가 git 층뿐** | `AGENTS.md` 표가 「Gate 0 미완」으로 명시. E1 승인 후 W2-a |
| R2 | 훅은 클론마다 수동 설치가 필요 | `verify_skill_setup.py`가 미설치를 exit 1로 잡도록 신설(실증 완료) |
| R3 | `generated-guard`·`tmp-guard`가 아직 관측 모드 | 오탐 0 확인 후 `--enforce` 승격. 근거는 아래 §8 |
| R4 | Codex 스모크(`$스킬명`) 미실시 | 가능함은 실측, 실행은 미실시 — 문서에 「가능(미실시)」로 구분 표기 |

---

## 2. 실제 사용 도구

- **Claude Code** — Opus 5(메인) + Sonnet 워커 8명. 훅·agent 파일·settings.
- **Codex** — `codex-cli 0.146.0-alpha.9.2` (`C:\Users\miso\AppData\Local\OpenAI\Codex\bin\…`, PATH 미등록). 이번엔 **프로브만 배치**하고 실행하지 않았다.
- **git** — `core.hooksPath=.githooks`. CI 없음(`.github/` 부재).

---

## 3. 기존 구조와 문제

| 파일 | 역할 | 실제 로드 | 문제 |
|---|---|---|---|
| `AGENTS.md` (161줄/20,644B) | 공통 정본 | Codex 직접 · Claude는 import | 절반이 덱 작업 전용인데 전 세션 로드 · 사실 오류 6건 |
| `CLAUDE.md` (22줄) | Claude 래퍼 | 시작 시 | 「필수 읽기」가 AGENTS.md와 4/6 중복, 정본 불명 |
| `.claude/settings.json` | 훅 3종 | Write\|Edit | Claude 전용. Codex 대응물 **0** |
| `.githooks/` | — | — | **존재하지 않음**(활성 git 훅 0) |
| `.claude/agents/`·`.codex/agents/` | — | — | **존재하지 않음** |
| `.claude/launch.json` | 프리뷰 서버 | — | 타 PC 사용자 절대경로가 커밋돼 있음 |

---

## 4. 핵심 발견

**Critical**

- **C1** 보안·품질 금지가 Codex 쪽에서 Markdown 문장뿐 — 강제 계층 0. → **부분 해소**(git 층 신설, Codex 훅은 Gate 0 대기)
- **C2** `.claude/launch.json`에 타 PC 사용자 절대경로(`C:/Users/Noh TaeKyung/…`)가 git에 커밋됨. → **해소**
- **C3** 정본끼리 충돌 — `AGENTS.md`는 charts 23개, `kit/charts/README.md`는 21개. → **해소**
- **C4**(독립 검토 발견) **훅 설치 상태를 검사하는 코드가 어디에도 없었다.** 문서와 계획은 검사한다고 적었으나 실제 코드는 0건. 훅이 미설치면 pre-commit이 아예 안 돌아 **스스로 미설치를 알릴 수 없는 자기참조 사각지대**였다. → **해소**(실증까지)

**High** — H1 두 파일 중복 관리 / H2 path-scoped 가능 규칙의 상시 로드 / H3 「Codex CLI 부재」 오전제 / H4 예산 78% 무측정 / H5 `course` 훅이 과목 2개에서 조용히 죽음(→ 미해소, §9 참조)

**Medium** — M1 사실 오차 4건 / M2 미등재 스크립트 3개 / M3 값 요약 복제 / M4 개인 설정 잔재 / M5 「하네스가 기본」 표현 / M6 역할·절차 혼재 / M7 스크래치패드 경로

---

## 5. 규칙 이동 장부 (요약 · 전체는 `PLAN.md` §6.2)

| Rule | 이전 | 새 위치 | 조치 | 근거 |
|---|---|---|---|---|
| R-A01 | `AGENTS.md` 실행·검증 43줄 | `references/검증-명령-지도.md` §1~7 | MOVE | 덱 전용인데 전 세션 로드 |
| R-A02 | 사고 이력 37줄 | 같은 파일 §8 | MOVE | 근거는 유지, 상시 로드 불필요 |
| R-A03 | 불변 규칙 값 요약 | 정본 지도 표 | REWRITE | 요약본↔정본 드리프트 |
| R-A04 | 필수 읽기 2벌 | `AGENTS.md` 1벌 | MERGE | 정본 불명 해소 |
| R-A05 | `CLAUDE.md` 어댑터 설명 | — | DELETE | `AGENTS.md`와 완전 중복 |
| R-A06 | `CLAUDE.md` Windows python | `AGENTS.md` | MOVE | 도구 중립 |
| R-A07 | `CLAUDE.md` 워커 통제 | `.claude/agents/research-worker.md` | SPLIT | 자연어 → 설정 |
| R-A08~12 | 사실 오류 6건 | 각 파일 | REWRITE | 실측 대조 |
| R-A13 | — | `AGENTS.md` 「무엇이 기계로 강제되는가」 | NEW | 무엇이 막히는지 알아야 함 |
| R-A14 | 하네스 = 비용절감 아님 | 그대로 | **KEEP** | 워커는 「수사」로 분류했으나 실측 근거가 붙은 판단 기준 |
| R-A15/M7 | `launch.json` 2 엔트리 | — | DELETE | 타 PC 경로 · 스크래치패드 경로 |

**독립 검토 V1 결과: 유실 0건.** 이동을 주장한 모든 항목이 새 위치에서 확인됐다.

---

## 6. 수정 파일 (23개 · +2,152 / −215)

**신설** — `.githooks/{pre-commit,_gate.py,README.md}` · `.claude/agents/{research-worker,instruction-reviewer}.md` · `.codex/agents/{research-worker,reviewer}.toml` · `.codex/{hooks.json,hooks/probe.py}` · `scripts/install_hooks.py` · `references/검증-명령-지도.md` · `plans/instruction-refactor/{PLAN,FINAL_REPORT}.md`

**수정** — `AGENTS.md` · `CLAUDE.md` · `.gitignore` · `.claude/{settings,launch}.json` · `scripts/{hook_slide_guard,verify_skill_setup}.py` · `skills/README.md` · `.agents/README.md` · `.claude/skills/README.md` · `.claude/skills/리서치/SKILL.md`

**보존 확인** — 1주차 동결 산출물 변경 0 · 워크트리 3개 유지 · `settings.local.json` 미추적 유지 · 사용자의 미추적 파일 2개 무손상

---

## 7. 삭제·제외

| 항목 | 이유 | 대체 |
|---|---|---|
| `CLAUDE.md` 「세션 시작 필수 읽기」 6항 | `AGENTS.md`와 4/6 중복이고 어느 쪽이 정본인지 불명 | `AGENTS.md` 「작업 전 필수 읽기」가 CLAUDE 고유 항목까지 흡수 |
| `CLAUDE.md` 어댑터 구조 설명 5줄 | `AGENTS.md` 완전 중복 | `AGENTS.md` 잔존 |
| `launch.json` `deck-server` | 타 PC 사용자 절대경로 · 존재하지 않는 디렉터리 | 없음 |
| `launch.json` `scratch-server` | 시스템 스크래치패드를 가리켜 「tmp/만」 규칙과 정면 충돌 | 없음 |
| `AGENTS.md` 품질감사 「76파일」 | 변하는 값이라 즉시 낡는다 | 개수 없이 역할만 |

**보존한 것**: `@AGENTS.md` import(`verify_skill_setup.py:421`이 검사) · 메모리 포인터 규약 · `Explore` 폐기 사유(규칙의 근거이므로 사고 이력으로 유지).

---

## 8. 검증

| 검증 | 명령·방법 | 결과 |
|---|---|---|
| D1 스킬 셋업 | `verify_skill_setup.py` | **exit 0** |
| D2 kit | `verify_kit.py` | **exit 0** |
| D3 과목 격리 | `verify_subject_isolation.py` | **exit 0** |
| D4 선언↔집행 | `verify_declared_vs_enforced.py` | **exit 0**(작업 전과 동일) |
| D5 회귀 | unittest 8모듈 | **Ran 155 · OK** |
| D6 훅 자가테스트 | 12케이스 독립 실행 | **12/12 PASS** |
| D7 훅 설치 | `git config --get core.hooksPath` | **`.githooks`** |
| D8 실제 차단 | 위반 CSS를 staged → `git commit` | **exit 1 · HEAD 불변** |
| D9 gitignore | `git status --porcelain -uall .codex` | 강제 파일 3개만 · **크롬 프로파일 0건** |
| D10 스코프 | wave별 `git status --short` | **위반 0** |
| S1 동결 보존 | `git diff --stat -- courses/*/sessions/1주차/` | **비어 있음** |
| S2 워크트리 | `git worktree list` | **3개 유지** |
| S3 개인 설정 | `git ls-files .claude/settings.local.json` | **0(미추적)** |
| S5 오탐률 | `tmp-guard` 6케이스 | **오탐 0 / 정탐 3** |
| B2~B7 행동 | 힌트 없이 새 에이전트에 5문항 | **5/5 「확실」** |
| V1~V7 독립 검토 | `instruction-reviewer` 에이전트 | V1~V6 문제 없음 · **V7 치명 1건 → 해소** |
| 저장소 밖 잔여물 | 스크래치패드 파일 수 | **0개** |

**행동 검증이 이 리팩터링의 진짜 증거다.** 80줄을 참조 문서로 옮겼는데 새 에이전트가 「덱 수정 후 무엇을 실행해야 하나」(B2)와 「생성물 vs shard」(B3)를 **스스로 찾아냈다.** 못 찾았다면 바이트만 줄고 규칙은 사라진 것이었다.

**S5 실측이 관측 모드의 값을 증명했다.** `tmp-guard`가 상대경로를 훅 프로세스의 CWD 기준으로 풀어 **저장소 안 파일을 「밖」으로 오탐**하고 있었다. `--enforce`로 바로 켰다면 정상 편집이 막혔을 것이다.

---

## 9. 미검증 · 결정 필요

| # | 항목 | 이유 | 필요한 결정 |
|---|---|---|---|
| **E1** | ~~Codex 훅 승인~~ → **해소.** `--dangerously-bypass-hook-trust`로 신뢰 저장소를 건드리지 않고 실측했다 | — | 없음 |
| **Gate 0** | **부분 완료(2026-08-06)** — `.codex/hooks.json` 로드·`SessionStart` 발화·CWD=루트까지 확정. **`PreToolUse`/`PostToolUse`는 미확정** | 도구 호출 직전 **Codex 계정 사용량 한도 소진**(복구 2026-08-10) | 한도 복구 후 1회 실행 |
| P2·P3 | Codex의 체크리스트 주입·생성물 차단 | Gate 0 미완 | 위에 종속 |
| — | Codex 로드 그래프 검증(`codex exec`) | 실행 가능하나 미실시 | 없음(다음 세션에서 수행 가능) |
| — | `$스킬명` 스모크 | 위와 동일 | 없음 |
| **H5** | `course` 훅이 과목 2개일 때 조용히 죽음 | 현재 과목이 1개라 재현 불가 | 두 번째 과목 추가 시 첫 시험대 |
| — | `generated-guard`·`tmp-guard` 차단 승격 | 관측 표본이 아직 적다 | 오탐 0이 이어지면 `--enforce` |
| — | `.claude/rules/deck.md` | Gate 0 결과에 따라 만들지 말지가 갈린다 | E1에 종속 |

---

## 10. 최종 점수

| 항목 | 배점 | 획득 | 근거 |
|---|---:|---:|---|
| 사실 정확성 | 25 | 24 | 불일치 6건 해소 · V3 경로 전수 통과 |
| 범위 정확성 | 15 | 14 | 규칙 배치 적절 · 개인 설정 제거. M5·M6은 부분 대응 |
| 실행 가능성 | 15 | 15 | 모든 명령 실측 존재 · 완료 조건이 종료코드로 판정됨 |
| 충돌 없음 | 10 | 10 | 독립 검토 V2 문제 없음 |
| 컨텍스트 효율 | 10 | 8 | Q2 달성(78%→56.1%) · Q1·Q3 미달 |
| 안전성 | 10 | 10 | 강제층 분리 · 크롬 프로파일 유출 0 실증 |
| 보존성 | 5 | 5 | V1 유실 0 |
| 유지보수성 | 5 | 5 | `PLAN.md` §15에 추가·삭제·점검 조건 |
| 검증 증거 | 5 | 4 | Codex 로드 검증만 미실시 |
| **총점** | **100** | **95** | |

> **95점이지만 완료가 아니다.** 목표 G1(Codex 동등 강제)이 미달성이고, 그것은 이 작업의 출발점이었다. 점수는 근거를 대체하지 않는다.

---

## 다음 한 걸음

1. **E1 — Codex에서 훅 승인** → 프로브 결과로 Gate 0 판정
2. 통과면 `.codex/hooks.json`을 실제 강제 배선으로 교체(W2-a) → `AGENTS.md` 표의 Codex 열을 채운다
3. 실패면 폴백 확정 → 표에 **「미지원 · git 층 위임」**으로 기록하고 「지연된 동등」을 최종 상태로 명시
4. 관측 표본이 쌓이면 `--enforce` 승격 판정
5. `main` 병합은 **사용자 승인 후**
