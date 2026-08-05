# 지침 생태계 리팩터링 + Codex 강제 패리티 — 실행 계획

> **작성일** 2026-08-05 · **작성** 메인(Opus) 단독 라이터 · **조사** Sonnet 워커 4개 병렬(읽기 전용 `Explore`)
> **근거 플레이북** 루트 `AGENTS_CLAUDE_REFACTORING.md`(2,269줄 전량 정독)
> **작업 전 상태** 브랜치 `main` · 워킹트리 clean(미추적 파일은 플레이북 1개) · HEAD `39659ea`
>
> ⚠️ 이 파일은 **계획서**다. 실행 결과·진행 상태는 여기 쓰지 말고 `PROGRESS.md`에 쓴다(선례: `plans/deck-quality-refactor/`).

---

## 0. 한 줄 요약

**규칙은 이미 충분하다. 없는 것은 「지켜지게 만드는 층」이다.** 이 계획은 ① Codex에 Claude와 동등한 강제 계층을 세우고 ② 두 플랫폼 공통의 최종 증거 층(git 훅)을 신설하며 ③ 그 결과로 자연어 지침(`AGENTS.md`·`CLAUDE.md`)에서 강제로 옮겨간 만큼을 덜어내 컨텍스트 예산을 확보한다.

---

## 1. 목표와 비목표

### 1.1 목표 (측정 가능한 형태로)

| # | 목표 | 측정 |
|---|---|---|
| G1 | Codex에서도 슬라이드 규칙이 **기계적으로** 강제된다 | `.codex/hooks.json`이 `hook_slide_guard.py`를 호출해 컨텍스트 주입 + 차단이 실측 재현됨 |
| G2 | 플랫폼과 무관한 **최종 증거 층**이 존재한다 | `core.hooksPath=.githooks` pre-commit이 Codex·Claude 양쪽 커밋에서 동일 작동 |
| G3 | 강제 규칙의 **정본이 하나**다 | 검사 로직이 `scripts/`에 1벌만 존재(플랫폼별 복제 0) |
| G4 | Codex 지침 예산에 여유가 생긴다 | 결합 바이트 25,547 → **20,000 이하**(32,768 한도의 61% 이하) |
| G5 | `AGENTS.md`·`CLAUDE.md`의 **사실 오류 0** | 아래 §3 「사실 불일치」 6건 전부 해소 |
| G6 | 두 파일 간 **중복 관리 0** | 같은 항목이 두 파일에 동시에 실체로 존재하지 않음(포인터는 허용) |

### 1.2 비목표 (이번에 하지 않는 것)

- **애플리케이션·덱 콘텐츠 수정 없음.** `courses/**` 산출물, `kit/**` 디자인 규칙 값, `scripts/verify_*.py`의 **판정 기준** 자체는 건드리지 않는다.
- **1주차 산출물 동결 유지**(2026-07-26 사용자 결정). 접근조차 하지 않는다.
- **워크트리 3개 유지.** `.claude/worktrees/` 아래 `harness-skill-improvement-plan` / `research-skill-refactor-phase-2` / `week-1-content-addition`은 등재된 git worktree이며 `/리서치` 리팩터링 진행분을 포함한다 — **삭제·정리 금지.**
- **규칙 값 하향 금지.** 불일치를 없애려고 문서 쪽 수치를 낮추지 않는다(AGENTS.md L118 원칙).

### 1.3 작업 모드 선언 (플레이북 §1.2)

| 단계 | 모드 | 근거 |
|---|---|---|
| 이 계획서 작성까지 | **읽기 전용 감사** | 사용자 요청이 "계획을 세우고 md로 만들어" |
| 이후 실행 | **전체 에이전트 환경 최적화** — 지침·설정·Skill·agent·hook 전체 감사 후 수정 | 사용자 요청에 "Codex 강제 패리티"와 "AGENTS/CLAUDE 리팩터링"이 함께 있음 |

- 사소한 정보 부족으로 멈추지 않는다. 다만 되돌리기 어려운 항목은 §11에 `결정 필요`로 남긴다.
- **애플리케이션 코드(덱·kit 값·verify 판정 기준)와 지침 리팩터링을 섞지 않는다**(플레이북 §1.1). 지침이 틀린 원인이 코드에 있으면 「지침 수정 필요」와 「코드 결정 필요」를 분리해 보고한다.

---

## 2. 조사 결과 — 확정된 사실

라벨: `[실측]` 이 저장소·이 PC에서 직접 확인 / `[공식]` 공식 문서 / `[추론]` 해석

### 2.1 Codex는 Claude와 동등한 강제가 **가능하다**

| 수단 | 경로 | 차단 | 컨텍스트 주입 | 근거 |
|---|---|---|---|---|
| Hooks | `<repo>/.codex/hooks.json` | `PreToolUse` → `permissionDecision:"deny"` 또는 exit 2 | `hookSpecificOutput.additionalContext` | `[공식]` + `[실측]` |
| Rules | `~/.codex/rules/*.rules`(Starlark `prefix_rule`) | `decision="forbidden"` | 불가 | `[공식]` + `[실측]` |
| Custom agent | `.codex/agents/*.toml` | `sandbox_mode="read-only"`로 쓰기 자체 차단 | 불가 | `[공식]` + `[실측]` |

- 이벤트 목록 `[공식]`: `SessionStart, SessionEnd, PreToolUse, PermissionRequest, PostToolUse, PreCompact, PostCompact, UserPromptSubmit, SubagentStart, SubagentStop, Stop`
- **동작 중인 실물 사례** `[실측]`: `C:\Users\miso\Desktop\pm-pm-skills-subagent-ai-agent\.codex\` 에 `hooks.json`(`Stop` 이벤트 · PowerShell 스크립트 호출 · `{"decision":"block","reason":...}` 반환) + `agents/*.toml` 5개(전부 `sandbox_mode="read-only"`) + `config.toml`. **추측이 아니라 검증된 템플릿을 복제할 수 있다.**
- 훅 신뢰 `[실측]`: `~/.codex/config.toml`의 `[hooks.state]`에 `"<hooks.json경로>:stop:0:0" → trusted_hash = "sha256:…"`. 훅 내용이 바뀌면 해시가 어긋나 **재승인이 필요**하다 `[추론]` → 계획 단계에 사용자 승인 절차를 명시한다.
- 이 저장소는 `[projects.'c:\users\miso\desktop\template'] trust_level = "trusted"` `[실측]` → 프로젝트 `.codex/` 설정이 **로드된다**.

### 2.2 Codex CLI는 로컬에 있다 — 기존 문서 주장이 틀렸다

- `[실측]` `C:\Users\miso\AppData\Local\OpenAI\Codex\bin\d7e8094cfb76a267\codex.exe` — `codex-cli 0.146.0-alpha.9.2`. PATH에만 없다.
- 서브커맨드에 `exec`(비대화형)·`doctor`(설치·설정 진단)·`review`가 있다 → **로드 그래프 검증과 `$스킬명` 스모크가 실제로 가능하다.**
- ⛔ `skills/README.md:55`의 *"Codex CLI는 로컬에 없어 `$스킬명` 스모크는 미실시"* 는 **사실과 다르다.** 이 문장이 "Codex는 검증 못 한다"는 전제를 프로젝트 전체에 깔아왔다.

### 2.3 컨텍스트 예산이 이미 빡빡하다

| 항목 | 실측 | 한도 | 비율 |
|---|---:|---:|---:|
| `AGENTS.md` | 161줄 / 20,644B | — | — |
| `CLAUDE.md`(원문) | 22줄 / 2,750B | — | — |
| `CLAUDE.md` 실효(import 전개) | **182줄** / 23,382B | 200줄 목표 | 91% |
| Codex 결합(`~/.codex/AGENTS.md` 4,903B + 루트) | **25,547B** | 32,768B | **78%** |

- `~/.codex/config.toml`에 `project_doc_max_bytes` 키가 **없다** `[실측]` → 기본 32KiB가 적용된다.
- **AGENTS.md가 7KB만 더 늘면 잘린다.** 지금은 "여유 있음"이 아니라 "경고선"이다.

### 2.4 부재한 계층 (전부 이 프로젝트에 아예 없음)

`.claude/rules/` · `.claude/agents/` · `.claude/commands/` · `.claude/workflows/` · `.codex/`(지침용) · `.mcp.json` · `PLANS.md` · 하위 디렉터리 `AGENTS.md`/`CLAUDE.md` 전부 · `~/.claude/CLAUDE.md` · **활성 git 훅** · **CI**

→ 특히 **`.claude/agents/` 부재**가 뼈아프다: `.claude/skills/리서치/SKILL.md`가 *"`maxTurns`는 `.claude/agents/` frontmatter 전용이라 이 경로에서는 쓸 수 없다"* 고 스스로 적어놨다. **agent 파일을 만들면 그 한계가 사라진다.**

### 2.5 현행 Claude 훅의 실제 효력 (과대평가하지 말 것)

| 훅 | 이벤트 | 실제 효과 | 구멍 |
|---|---|---|---|
| `checklist` | PreToolUse | 7항 체크리스트 **주입만** | 경로가 `samples_v3`/`강의덱.초안`/`강의덱.html` 밖이면 **완전 미발동** |
| `css-lint` | **PostToolUse** | `{"decision":"block"}` | **이미 써진 뒤**라 쓰기를 못 막는다. 사후 지적만 |
| `course` | PreToolUse | 과목 지침 900자 주입 | `courses/*/슬라이드지침.md`가 **정확히 1개**일 때만. 과목이 2개가 되는 순간 조용히 죽는다 |

세 모드 모두 `try/except: pass`로 감싸여 **실패해도 조용히 통과**한다 `[실측 L165-183]`.

### 2.6 강제되지 않는 규칙 (자연어만 존재)

| 규칙 | AGENTS.md | 기계 강제 |
|---|---|---|
| 임시 파일은 `tmp/`에만 | L136 | **가능**(PreToolUse 경로 검사) — 미구현 |
| `강의덱.html`은 생성물, 직접 수정 금지 | L124 | **가능**(PreToolUse 차단) — 미구현 |
| 덱 고쳤으면 `run_deck_checks.py` | L107 | 부분 가능(pre-commit) — 미구현 |
| 노트 작업은 `verify_notes.py`로 감쌈 | L111 | 부분 가능(pre-commit) — 미구현 |
| 카탈로그·SKILL.md 변경 시 evals 회귀 | L130 | **가능**(pre-commit) — 미구현 |

### 2.7 사실 불일치 (문서 ↔ 실제)

| # | 주장 | 실제 | 심각도 |
|---|---|---|---|
| F1 | `kit/charts/`(**23**) — AGENTS.md:159 | `kit/charts/README.md:17`이 스스로 **"21개 element"** | **높음**(정본끼리 충돌) |
| F2 | `품질감사-2026-07/` **76**파일 — L10 | 실측 **77** | 중간 |
| F3 | `courses/<과목>/sessions/N주차/N주차_강의안설계.md` — L10,22 | **1주차만 존재.** 2주차엔 없음 | 중간(패턴을 일반화해 서술) |
| F4 | *"보통 `.venv\Scripts\python.exe`"* — L131 | **`.venv` 부재.** 단 시스템 `python`에 `fontTools`·`Pillow`가 설치돼 있어 155개 테스트가 통과한다 `[실측]` — 문장이 틀렸을 뿐 실무 영향은 작다 | 낮음(하향 조정) |
| F5 | *"Codex CLI는 로컬에 없어"* — `skills/README.md:55` | **존재**(§2.2) | 높음(전제 오염) |
| F6 | `kit/layouts/`(**50**) — L158 | 파일은 `families/` 8개. 50은 그 안의 항목 수(README와는 일치) | 낮음(표기 모호) |

### 2.8 집행부 결합 지점 (리팩터링 시 깨지면 안 되는 것)

- `[실측]` `scripts/verify_skill_setup.py:421` — `"@AGENTS.md" in CLAUDE.md`를 검사한다. → **CLAUDE.md의 `@AGENTS.md` import는 삭제 불가.**
- `[실측]` `scripts/verify_skill_setup.py:424-433` — 메모리 포인터 규약(`.agents`가 정본, `.claude`는 400B 미만 포인터)을 검사한다. → 메모리 구조 변경 금지.
- `[실측]` `tests/`·`evals/`에서 `AGENTS.md` **본문을 파싱하는 곳은 없다** → 본문 재구성은 자유롭다.

### 2.9 `.gitignore` 충돌 (선행 해결 필수)

`[실측]` `git check-ignore -v` 결과 `.gitignore:2`의 `.codex/`가 `.codex/hooks.json`·`.codex/agents/*`·`.codex/config.toml`을 **전부 커밋 불가**로 막는다. 게다가 **git은 제외된 디렉터리 안으로 내려가지 않으므로 `!.codex/hooks.json` 단순 추가로는 풀리지 않는다.**

수정 형태(반드시 `.codex/*` — 슬래시 단독 아님):

```gitignore
# Codex 런타임(브라우저 프로파일 등 — 쿠키·로그인 데이터, 커밋 금지)
.codex/*
# 단, 아래 지침·강제 설정은 팀 공유 대상이므로 추적한다
!.codex/config.toml
!.codex/hooks.json
!.codex/hooks/
!.codex/agents/
```

### 2.10 로드 그래프 (플레이북 §9) — 작업 전 실측

| CWD | Codex 활성 파일(순서) | Claude 활성 파일(순서) | 누락 위험 |
|---|---|---|---|
| 저장소 루트 | ① `~/.codex/AGENTS.md`(4,903B) → ② `AGENTS.md`(20,644B) | 시작: `CLAUDE.md`(→`@AGENTS.md` 전개) / 지연: 스킬 `SKILL.md`(description 매칭 시) · Write\|Edit 훅 동적 주입 | 없음 |
| `courses/바이브코딩/sessions/2주차` | **동일**(중간·CWD `AGENTS.md` 없음) | **동일**(하위 `CLAUDE.md` 없음) | 주차 설계 문서는 자동 로드 아님 — 라우팅 지시로만 연결 |
| `kit` | **동일** | **동일** | `kit/guide/*` 디자인 정본 자동 로드 아님 — 경로 안내만 |

- **하위 `AGENTS.md`/`CLAUDE.md`가 0개**이므로 플레이북 §3.3이 경고하는 "루트에서 시작한 Codex가 하위 지침을 놓치는" 문제는 **현재 발생하지 않는다.** monorepo용 routing 규칙은 불필요하다.
- ⚠️ **그러나 이 계획이 그 문제를 새로 만들 수 있다.** §6.1이 신설하는 `.claude/rules/deck.md`는 **Claude만 읽고 Codex는 읽지 않는다**(플레이북 §13.3). 대응은 §4 원칙 4 참조.
- `project_doc_max_bytes`·`project_doc_fallback_filenames`·`project_root_markers` 키가 전역 설정에 **없다** → 전부 기본값. Codex 프로젝트 루트는 git 루트로 잡히고, 한도는 32KiB다.

---

## 3. 결함 목록 (플레이북 §12 분류)

### 3.1 치명적 (Critical)

| ID | 결함 | 근거 |
|---|---|---|
| C1 | **보안·품질 금지를 Markdown만으로 강제**(플레이북 §12.1) — Codex 측에 강제 계층이 **0**이다. `tmp/` 금지·생성물 직접수정 금지·evals 회귀 전부 자연어뿐 | §2.5, §2.6 |
| C2 | **개인 절대경로가 git에 커밋됨** — `.claude/launch.json:8`의 `C:/Users/Noh TaeKyung/Desktop/lecture-deck-pipeline`(다른 PC 사용자 경로). 존재하지 않는 디렉터리를 가리키는 서버 설정이 팀 공유 파일에 들어 있다 | `[실측]` |
| C3 | **정본끼리 충돌** — F1(charts 23 vs 21). 어느 쪽을 믿어야 하는지 에이전트가 판정할 수 없다 | §2.7 |

### 3.2 높음 (High)

| ID | 결함 | 근거 |
|---|---|---|
| H1 | **`AGENTS.md`·`CLAUDE.md` 동일 정보 복제 관리**(플레이북 §12.3) — 「작업 전 필수 읽기」 6항 ↔ 「세션 시작 필수 읽기」 6항이 4/6 동일, 나머지 2개는 한쪽에만 있어 **어느 목록이 정본인지 불명** | W2 대조표 |
| H2 | **path-scoped 가능 규칙을 매 세션 무조건 로드**(§12.2) — 「실행과 검증」 43줄 + 사고 이력 37줄 = **80줄(전체의 절반)이 덱 작업 전용**인데 조회·리서치·스킬수정 세션에도 전부 실린다 | AGENTS.md L51-131 |
| H3 | **낡은 전제가 프로젝트 전체를 오염** — F5(Codex CLI 부재 주장)가 "Codex는 검증 불가"라는 결론을 낳고, 그것이 어댑터를 "패턴 패리티용"으로 격하시켰다 | §2.2 |
| H4 | **컨텍스트 예산 78%** — 경고선인데 아무도 측정하지 않고 있었다 | §2.3 |
| H5 | **훅이 조용히 죽는 구조** — `course` 모드는 과목이 2개가 되는 순간 `None`을 받고 침묵한다. 실패가 관측되지 않는다 | §2.5 |

### 3.3 중간 (Medium)

| ID | 결함 |
|---|---|
| M1 | F2·F3·F4·F6 사실 오차 |
| M2 | `scripts/` 19개 중 **3개가 AGENTS.md 미등재**(`verify_distributable`·`verify_image_assets`·`verify_presenter_deck`), `verify_notes.py`는 산문에만 있고 명령블록에 없음 |
| M3 | 「불변 규칙」 절이 `kit/guide/디자인시스템.md` 값을 요약 복제 → 드리프트 위험(이미 `verify_declared_vs_enforced.py`가 8건 불일치를 등재 중) |
| M4 | `.claude/settings.local.json`에 개인 프로젝트("Minseo Portfolio") 명령이 남아 있음 — 미추적이라 유출은 아니나 잔재 |
| M5 | **「모든 작업은 멀티에이전트」형 구조 강제 의심**(플레이북 §12.2) — AGENTS.md L139 *"하네스(실질 작업의 기본 방식)"* 는 첫 줄만 읽으면 무조건 하네스로 읽힌다. 실제로는 뒤에 solo 예외가 붙어 있고 `skills/하네스/SKILL.md` §1이 *"의심스러우면 한 단계 낮춰라"* 로 못박지만, **상시 로드되는 요약 쪽이 더 강하게 읽히는 역전**이 있다. → 표제를 「규모에 따라 선택」으로 바꾸고 solo 조건을 같은 줄에 올린다 |
| M7 | **`.claude/launch.json`의 `scratch-server`가 시스템 스크래치패드를 가리킨다** — `C:/Users/miso/AppData/Local/Temp/claude/.../scratchpad`(이미 끝난 세션 ID). AGENTS.md L136 「임시 파일은 저장소 안 `tmp/`에만」과 정면으로 어긋나는 설정이 팀 공유 파일에 있다. **W-agents 범위(R-A15는 `deck-server`만) 밖이라 미처리 — W2-b에서 함께 제거한다** |
| M6 | **역할 정의와 절차가 스킬 하나에 섞여 있음**(플레이북 §12.2·§3.8) — `skills/리서치`·`skills/검토`가 「팀 역할(해서·준형)」과 「다단계 절차」를 함께 담는다. 절차는 Skill이 맞지만 **역할·모델·도구 권한은 agent 파일이 정본**이어야 한다 → §5.2가 그 분리를 수행한다 |

---

## 4. 목표 구조 — 3층 강제 모델

플레이북 §13.4를 이 프로젝트에 맞게 구체화한다.

```
① 설명층 (자연어)          AGENTS.md ─@import─ CLAUDE.md
   "왜 그런가 · 어디를 봐라"   ↑ 짧게. 사고 이력과 근거는 참조 문서로.

② 강제층 (플랫폼별 설정)    .claude/settings.json  ┐
   "지금 이 도구 호출을 막는다"  .codex/hooks.json     ├→ scripts/hook_slide_guard.py (단일 정본)
                              .claude/agents/*.md   ┐
                              .codex/agents/*.toml  ├→ 워커 도구·모델·쓰기 권한 구조적 제한
③ 증거층 (플랫폼 공통)      .githooks/pre-commit ──→ scripts/ 게이트 실행 (Codex·Claude 무관)
   "커밋 시점에 최종 확인"
```

**핵심 설계 원칙 3가지**

1. **검사 로직은 `scripts/`에 1벌만 둔다.** 플랫폼 설정 파일은 *호출자*일 뿐이다. Claude용 `.claude/settings.json`과 Codex용 `.codex/hooks.json`은 **같은 파이썬 스크립트를 부른다.** (규칙 복제 금지 원칙의 강제층 버전)
2. **페이로드 차이는 스크립트가 흡수한다.** `hook_slide_guard.py`가 Claude 형식(`tool_input.file_path`)과 Codex 형식을 **둘 다 파싱**하고, 출력도 호출자에 맞춰 낸다. 어댑터를 밖에 두면 또 2벌이 된다.
3. **git 훅이 최후의 보루다.** 훅·rules는 플랫폼별로 다르고 우회 가능하지만, `core.hooksPath`는 CLI와 무관하게 커밋 시점에 실행된다. **지금 이 층이 완전히 비어 있다는 것이 가장 큰 구멍이다.**
4. **경로별 지침의 비대칭을 훅으로 메운다.** Claude는 `.claude/rules/`의 `paths:`로 경로별 지침을 지연 로드하지만 **Codex에는 대응 기능이 없다**(플레이북 §5 비교표·§13.3). 이 프로젝트의 해법: **`.claude/rules/deck.md`에는 내용을 담지 않고 라우팅만 두고, 실제 「지금 이 파일을 만질 때 필요한 지침」은 양 플랫폼의 PreToolUse 훅이 `additionalContext`로 주입한다.** 즉 경로 스코프의 정본은 rules 파일이 아니라 **훅의 경로 매칭**이다 — 그래야 한 벌로 양쪽이 같은 것을 받는다.
   - 부수 효과: Gate 0가 실패해 Codex 훅을 못 쓰면 **이 비대칭이 그대로 남는다.** 그 경우 `.claude/rules/deck.md`도 만들지 않고 `references/검증-명령-지도.md` 라우팅 한 벌로 통일한다(한쪽만 잘 되는 상태를 만들지 않는다).

---

## 5. Codex 강제 패리티 — 파일별 상세 설계

### 5.0 ⚠️ Gate 0 — 능력 실증 (다른 모든 것보다 먼저)

`PreToolUse`/`PostToolUse` 지원은 `[공식]` 문서 근거이고, 로컬 실물 사례는 `Stop` 이벤트뿐이다. **문서를 믿고 설계 전체를 얹지 않는다.**

**실증 절차 (필수 · 실패 시 §5.6 폴백으로 전환)**

1. `.codex/hooks.json`에 **프로브 훅**만 먼저 만든다 — `PreToolUse`가 stdin JSON을 그대로 `tmp/codex-hook-probe.json`에 덤프하는 3줄짜리 파이썬.
2. 사용자에게 Codex 세션에서 훅 승인(`/hooks`)을 요청한다. **훅 신뢰는 사용자만 줄 수 있다.**
3. Codex로 아무 파일이나 편집시켜 덤프가 생기는지 확인한다.
4. **판정**
   - 덤프 생성됨 → 페이로드 실제 스키마 확보. §5.1로 진행.
   - `PreToolUse` 미발동 → `PostToolUse`·`Stop`으로 강등하고 §5.6 폴백 비중을 높인다.
   - 훅 자체 미발동 → **Codex 훅 경로 전면 폐기**, git 훅(§5.5)에 전량 위임하고 그 사실을 계획에 기록한다.

> **이 게이트를 통과하기 전에는 §5.1~5.3을 작성하지 않는다.** 문서만 보고 만든 설정 파일은 「선언과 집행 불일치」(유형⑤)를 새로 만드는 짓이다.

### 5.0-R Gate 0 실행 결과 (2026-08-06 · **부분 완료**)

`codex exec --dangerously-bypass-hook-trust`로 실측했다. 이 플래그는 **호출 1회에 한해** 훅을 신뢰 없이 실행하며 `~/.codex/config.toml`의 신뢰 저장소를 **바꾸지 않는다** — 사용자 계정의 보안 설정을 에이전트가 대신 수정하지 않고 측정할 수 있는 경로다.

**확정된 것**

| 항목 | 결과 |
|---|---|
| 저장소 `.codex/hooks.json` 로드 | ✅ 된다(project trust `trusted` 작동) |
| `SessionStart` 발화 | ✅ 페이로드 확인 — `session_id`·`transcript_path`·`cwd`·`hook_event_name`·`model`·`permission_mode`·`source` |
| 훅 실행 시 CWD | ✅ **저장소 루트** → 상대경로(`.codex/hooks/probe.py`)가 해석된다 |
| Codex가 읽는 지침 | ✅ 루트 `AGENTS.md`. 전역 `~/.codex/AGENTS.md`는 보고 목록에 **나타나지 않았다** — §2.3의 결합 바이트 추정은 보수적(과대)이었을 수 있다 |
| 이벤트 목록(타 설정에서 실증) | `UserPromptSubmit` `SessionStart` `PreToolUse` `PermissionRequest` `PostToolUse` **`PostToolUseFailure`** `SubagentStart` `SubagentStop` `PreCompact` `Stop` `SessionEnd` |
| **`PreToolUse`·`PostToolUse` 발화** | ❌ **미확정** — 도구 호출 직전에 계정 사용량 한도 소진 |

**실패로 배운 스키마 제약 2가지 (둘 다 이 작업의 실수였다)**

1. **최상위 필드는 `description`·`hooks` 둘뿐이다.** 넣어둔 `_comment` 때문에 `failed to parse hooks config … unknown field _comment`로 **파일 전체가 파싱 실패해 훅이 하나도 걸리지 않았다.** 그런데도 콘솔에는 `hook: PostToolUse`가 찍혀 성공처럼 보였다 — 전부 **전역 플러그인**(`oh-my-claudecode`)의 훅이었다. 남의 훅 로그를 내 훅의 증거로 오독할 뻔했다.
2. **`PreToolUse`·`PostToolUse`는 `"matcher"`가 없으면 아무것도 매치하지 않는다.** `"matcher": "*"`를 명시해야 한다(형식 근거: 같은 PC에서 동작 중인 플러그인 hooks.json).

**운영 주의**

- `codex exec`는 stdin이 열려 있으면 `Reading additional input from stdin...`에서 멈춘다 → `< /dev/null`.
- `bin/<해시>/codex.exe` 경로는 자동 업데이트로 바뀐다(같은 날 `d7e8094…`→`68de26a…`). 문서에 박지 말고 `~/.codex/config.toml`의 `CODEX_CLI_PATH`를 참조한다.
- **실측이 계정 사용량을 태운다.** 4회 실행으로 한도가 소진됐다(복구 2026-08-10).

**남은 절차**: 한도 복구 후 `tmp/gate0-ok.txt`를 쓰게 하는 1회 실행으로 `PreToolUse`/`PostToolUse` 발화와 페이로드의 **파일 경로 키 이름**만 확인하면 Gate 0가 끝난다. 그 값이 나와야 §5.1의 `matcher` 대상과 `--host codex` 파싱을 확정할 수 있다.

### 5.1 `.codex/hooks.json` (신규)

```jsonc
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "<Codex의 쓰기 도구 이름 — Gate 0에서 실측 확정>",
        "hooks": [
          { "type": "command",
            "command": "python \"scripts/hook_slide_guard.py\" --mode checklist --host codex",
            "commandWindows": "python \"scripts\\hook_slide_guard.py\" --mode checklist --host codex",
            "timeout": 15,
            "statusMessage": "슬라이드 사전 점검 7항 확인" },
          { "…": "--mode course --host codex" },
          { "…": "--mode generated-guard --host codex   ← 신규(§5.4)" },
          { "…": "--mode tmp-guard --host codex         ← 신규(§5.4)" }
        ] } ],
    "PostToolUse": [
      { "matcher": "<동일>",
        "hooks": [ { "…": "--mode css-lint --host codex" } ] } ]
  }
}
```

- `commandWindows` 필드를 반드시 병기한다(로컬 실물 사례가 그렇게 쓰고 있다 `[실측]`).
- **인터프리터 문제(F4)**: `.venv`가 없으므로 `python`은 시스템 인터프리터를 잡는다. 훅이 쓰는 검사는 **표준 라이브러리만** 사용하도록 제한한다(`fontTools`/`Pillow` 의존 금지). 이미 `hook_slide_guard.py`는 `sys/json/re/os`만 쓴다 — 이 제약을 파일 상단에 **명문화**한다.

### 5.2 `.codex/agents/*.toml` (신규 · Claude `.claude/agents/*.md`와 쌍)

`/리서치` 워커 통제를 **양 플랫폼 모두 구조적으로** 만든다.

| 파일 | 역할 | 핵심 필드 |
|---|---|---|
| `.codex/agents/research-worker.toml` | 리서치 조사 워커 | `sandbox_mode = "read-only"` · `model` 고정 · `developer_instructions`에 반환 스키마 |
| `.codex/agents/reviewer.toml` | 독립 검토(읽기 전용) | `sandbox_mode = "read-only"` |
| `.claude/agents/research-worker.md` | 동일 역할 | `tools: Read, Grep, Glob, WebSearch, WebFetch, ToolSearch` · `model: sonnet` · **`maxTurns`** |
| `.claude/agents/instruction-reviewer.md` | 독립 검토 | `tools: Read, Glob, Grep` · `model: sonnet` |

**이 작업의 실질 이득**: `.claude/skills/리서치/SKILL.md`의 「강제 수준」 표에서 **「턴 상한: ❌ 강제 수단 없음」이 「✅ `maxTurns`」로 바뀐다.** 그 표도 함께 갱신해야 한다(짝 파일 — 같은 워커가 고친다).

### 5.3 Codex Rules — 이번엔 **채택하지 않는다**

`~/.codex/rules/*.rules`(Starlark `prefix_rule`)는 **명령 프리픽스 단위 allow/prompt/forbidden**이라 "이 파일을 쓰지 마라" 같은 경로 기반 규칙에 맞지 않는다. 게다가 `paths` 스코프 문법이 문서에서 확인되지 않았다. **판정: 보류.** 필요해지면 별도 사이클에서 재검토한다.

### 5.4 `hook_slide_guard.py` 확장 (신규 모드 2종 + 호스트 어댑터)

| 모드 | 이벤트 | 동작 |
|---|---|---|
| `--mode generated-guard` | PreToolUse | 대상이 `courses/**/강의덱.html`·`강의덱_발표자노트.html`(= `assemble_deck.py` 생성물)이면 **차단**하고 "shard(`강의덱.초안/`)를 고쳐라"를 이유로 반환. 예외: 환경변수 `DECK_EMERGENCY_EDIT=1` |
| `--mode tmp-guard` | PreToolUse | 쓰기 대상 절대경로가 **저장소 밖**(`%TEMP%`·`AppData`·스크래치패드)이면 **차단**. 저장소 안이면 통과. `tmp/` 강제(L136)의 기계화 |
| `--host claude\|codex` | — | 입력 페이로드 파싱과 출력 JSON 형식을 호스트별로 분기. **기본값 `claude`**(하위 호환) |

**설계 주의 (안티패턴 #2 — 계약만 바꾸고 집행기를 안 고침)**
- `generated-guard`는 **1주차 동결 산출물**과 충돌할 수 있다 → 동결 경로는 애초에 편집 대상이 아니므로 차단이 오히려 안전. 그대로 둔다.
- `tmp-guard`는 **이 계획서 자신을 쓰는 것도 막을 수 있다** → 저장소 안이므로 통과. 하지만 서브에이전트가 시스템 스크래치패드에 쓰는 것은 막힌다. **이것이 정확히 의도한 바다**(2026-07-30 워커 4개 전원 이탈 사고).
- 두 모드 다 **먼저 관측 모드(경고만)로 1회 돌려 오탐률을 재고**, 0에 수렴할 때만 차단으로 승격한다. (AGENTS.md L101-106 「검사 범위를 넓힐 때는 오탐률을 함께 재라」)

### 5.5 `.githooks/pre-commit` (신규 · 플랫폼 공통 증거층)

```
git config core.hooksPath .githooks     ← 저장소에 추적되는 훅 디렉터리
```

| 트리거(staged 파일) | 실행 | 실패 시 |
|---|---|---|
| `kit/**` | `verify_kit.py` · `verify_declared_vs_enforced.py` | 커밋 차단 |
| `SKILL.md`·`skills/**`·`.claude/skills/**`·`.agents/skills/**` | `verify_skill_setup.py` | 커밋 차단 |
| `**/*.css` | R-QC-14 정규식(`hook_slide_guard.py --mode css-lint --stdin-paths`) | 커밋 차단 |
| `courses/**/강의덱.html` | shard가 함께 staged 되었는지 확인 | 차단 + "shard를 고쳐라" |
| `courses/**/강의덱_발표자노트.html` | `verify_notes.py` | 차단 |
| 항상 | 저장소 루트에 `tmp/` 밖 미추적 잔재 스캔 | 경고(차단 아님) |

- **`--no-verify` 우회는 인정한다.** 목표는 방탄이 아니라 "잊어버림 방지"다.
- 훅은 **표준 라이브러리 파이썬만** 사용한다(§5.1 인터프리터 제약).
- 설치는 `python scripts/install_hooks.py`(신규) 한 줄로 하고, `verify_skill_setup.py`에 **"`core.hooksPath`가 `.githooks`인가"** 검사를 추가한다 → 설치 자체가 검증된다.

### 5.6 폴백 (Gate 0 실패 시)

Codex 훅이 안 되면: **§5.5의 git 훅에 전량 위임** + `AGENTS.md`에 "Codex 세션은 커밋 전 `python scripts/run_gates.py`를 직접 실행한다"는 라우팅 1줄. 이 경우 **패리티는 「동등」이 아니라 「지연된 동등」**임을 계획서와 최종 보고에 명시한다. 숨기지 않는다.

---

## 6. `AGENTS.md`·`CLAUDE.md` 리팩터링 설계

### 6.1 목표 구조

```
AGENTS.md              ~90줄 / ~11KB   ← 항상 필요한 계약·라우팅만
  ├ Core contract        완료 조건·보고 형식·금지
  ├ 구조 지도            ①~⑤층 (압축)
  ├ 라우팅               "언제 무엇을 열어라" (경로만)
  ├ 강제 계층 안내       "무엇이 기계로 막히는가" ← 신설
  └ 공통 작업 방식       하네스·tmp·리서치

references/검증-명령-지도.md   (신규)  ← 실행·검증 명령 43줄 + 사고 이력 37줄 전량 이관
CLAUDE.md              ~14줄          ← @AGENTS.md + Claude 고유 6줄
.claude/rules/deck.md  (신규)         ← paths: courses/**/강의덱*, kit/** → 위 지도로 라우팅 + Claude 고유 주의
```

⚠️ **컨텍스트 감소를 정직하게 셀 것** (플레이북 §4.4·§14.3)
`@import`는 파일만 나눌 뿐 컨텍스트를 **줄이지 않는다.** 이 계획의 감소분이 진짜인 이유는 이관 대상이 **import되지 않는 별도 참조 파일**(`references/검증-명령-지도.md`)로 가기 때문이다 — 필요할 때 열어서 읽는 파일이지 매 세션 실리는 파일이 아니다. **만약 `CLAUDE.md`에 `@references/…`를 추가하는 형태로 바꾸면 감소는 0이 된다. 그렇게 하지 않는다.**

⚠️ **상위·하위를 모순으로 설계하지 않는다** (플레이북 §4.3)
Claude는 충돌 시 **임의로 하나를 고를 수 있다.** `.claude/rules/deck.md`에 `AGENTS.md`와 다른 말을 적지 않는다. 상위는 범용 원칙("변경 영역에 정의된 가장 가까운 검증 명령을 쓴다"), 하위는 **비충돌적 세부화**("이 영역의 검증 명령은 X다")로만 쓴다.

⚠️ **`project_doc_max_bytes`를 올려서 해결하지 않는다** (플레이북 §3.5)
한도 상향은 마지막 수단이다. 순서대로 ① 중복 제거 ② 코드에서 추론 가능한 내용 제거 ③ 하위 범위 이동 ④ 절차를 Skill로 ⑤ 긴 참고자료를 경로 안내로 축소 ⑥ 중요한 규칙을 상단 배치 — 이 여섯을 다 하고도 넘칠 때만 재논의한다. **이번엔 ①②⑤⑥으로 충분하다.**

### 6.2 규칙 이동 장부

| ID | 현재 위치 | 내용 | 판정 | 목표 위치 | 근거 |
|---|---|---|---|---|---|
| R-A01 | AGENTS L51-93 | 실행·검증 명령 43줄 | **MOVE** | `references/검증-명령-지도.md` + AGENTS에 포인터 3줄 | H2. 덱 작업 전용인데 전 세션 로드 |
| R-A02 | AGENTS L95-131 | 사고 이력·⚠️ 블록 37줄 | **MOVE** | 같은 파일(근거 절) | H2. 근거는 유지하되 상시 로드 불필요 |
| R-A03 | AGENTS L39-47 | 불변 규칙 요지 색인 9줄 | **REWRITE** | AGENTS에 **포인터 2줄**로 축약 | M3. 값 복제는 드리프트 원인. 정본은 `kit/guide/` |
| R-A04 | AGENTS L17-24 ↔ CLAUDE L13-22 | 필수 읽기 목록 2벌 | **MERGE** | AGENTS 1벌 | H1. **CLAUDE 쪽을 삭제**하고 AGENTS 목록에 CLAUDE에만 있던 항목을 흡수 |
| R-A05 | CLAUDE L5-8,10 | 어댑터 구조 설명 | **DELETE** | — | AGENTS L11,28-31과 완전 중복. 삭제 근거 기록 |
| R-A06 | CLAUDE L9 | Windows `python` 사용 | **MOVE** | AGENTS(도구 중립) | Codex도 Windows다. Claude 고유가 아님 |
| R-A07 | CLAUDE L11 | 리서치 워커 Explore+sonnet | **SPLIT** | 강제 → `.claude/agents/research-worker.md` / 안내 1줄만 CLAUDE 잔류 | §5.2. 자연어를 설정으로 |
| R-A08 | AGENTS L159 | `kit/charts/`(23) | **REWRITE** | **21**로 정정 | F1 |
| R-A09 | AGENTS L10 | 품질감사 76파일 | **REWRITE** | 77 또는 **개수 제거** | F2. 개수는 변하므로 안 적는 편이 낫다 |
| R-A10 | AGENTS L10,22 | `N주차_강의안설계.md` | **REWRITE** | "주차별로 있을 수도 없을 수도 있다(1주차만 존재)" | F3 |
| R-A11 | AGENTS L131 | `.venv\Scripts\python.exe` | **REWRITE** | `.venv` 부재 실측 반영 + 훅은 표준 라이브러리만 | F4 |
| R-A12 | `skills/README.md:55` | Codex CLI 부재 주장 | **REWRITE** | 존재 + `codex exec` 스모크 절차 | F5·H3 |
| R-A13 | — | 강제 계층 안내 | **NEW** | AGENTS 신설 절 | C1. "무엇이 기계로 막히는가"를 에이전트가 알아야 한다 |
| R-A14 | AGENTS L139-141 | 하네스 = 비용절감 아님 | **KEEP** | 그대로 | 워커가 "수사"로 분류했으나 **실측 근거가 붙은 판단 기준**이다. 유지 |
| R-A15 | `.claude/launch.json:3-9` | 타 PC 절대경로 | **DELETE** | 해당 엔트리 제거 | C2 |

### 6.3 절대 건드리지 않는 것

- `CLAUDE.md` 1행 `@AGENTS.md` — `verify_skill_setup.py:421`이 검사(§2.8)
- 메모리 포인터 구조(`.agents` 정본 / `.claude` 400B 미만) — `verify_skill_setup.py:424-433`
- 어댑터 frontmatter `name`·`description` 동일성 — `verify_skill_setup.py` 전반

### 6.4 규칙 이동·삭제 기록 형식 (플레이북 §10.2)

삭제·이동은 **한 건도 예외 없이** 아래 형식으로 `PROGRESS.md`에 남긴다. 형식이 없는 삭제는 리뷰어(V1)가 FAIL 처리한다.

```text
R-A05 삭제
이유: AGENTS.md L11,28-31과 완전 중복 (플레이북 §10.2 「다른 활성 규칙과 완전 중복」)
대체: 없음 (AGENTS.md 쪽이 정본으로 잔존)
보존 영향: 없음 — CLAUDE.md 독자도 @AGENTS.md 전개로 동일 내용을 받는다
```

**삭제 허용 조건**(하나 이상 충족 + 보존 위험 없음): 저장소와 불일치 / 다른 활성 규칙과 완전 중복 / 코드·CI가 이미 강제 / 일반 상식 / 일회성 상태 / 검증 불가능한 수사 / 존재하지 않는 경로·도구 / 더 적절한 위치로 이동 완료.

### 6.5 새로 쓸 문장의 형식 (플레이북 §14.4·§14.5·§14.6)

**공식**: `[적용 범위] + [해야 할 행동] + [구체 방법] + [예외·안전 경로] + [검증 증거]`

> ⚠️ **이것은 사고의 뼈대이지 출력 문법이 아니다.** 결과물에 `[범위]+[행동]+…` 같은 **대괄호와 `+` 기호를 그대로 찍지 마라.** 다섯 요소가 자연스러운 한국어 문장 안에 **들어 있으면** 된다. (2026-08-05 실측: 워커 1명이 이 공식을 표기법으로 오독해 `.claude/agents/research-worker.md`를 대괄호 나열로 작성했다. 워커 프롬프트에도 이 단서를 함께 넣는다.)

| 금지 | 대신 |
|---|---|
| `- 덱을 신중하게 검증한다` (관찰 불가) | `- 덱을 고쳤으면 `run_deck_checks.py <주차>`를 실행하고 종료코드를 보고한다. 렌더 증거가 없으면 exit 1이다.` |
| `- 직접 편집 금지` (이유·대안 없음) | `- `강의덱.html`은 `assemble_deck.py` 생성물이라 다음 조립 때 유실된다. 수정은 `강의덱.초안/`의 shard에 하고 조립한다.` |

**삭제·변환 대상 어휘**: 「최고 품질」 「완벽하게」 「항상 신중하게」 「깔끔하게」 「필요하면 테스트」 「적절히 검토」.

> 단, **실측 근거가 붙은 판단 기준은 수사가 아니다.** 예: "하네스는 비용 절감 도구가 아니다"는 55.2M 캐시읽기 실측에 근거한 행동 지침이므로 유지한다(§6.2 R-A14).

### 6.6 규칙 목적지 결정 질문 (플레이북 §11.1)

장부의 각 행은 아래를 **순서대로** 물어 목적지를 정한다. 앞에서 걸리면 뒤는 묻지 않는다.

1. 모든 관련 세션이 항상 알아야 하는가? → `AGENTS.md`
2. 특정 경로·파일 유형에서만 필요한가? → 훅 경로 매칭(양 플랫폼) + `.claude/rules/`
3. 여러 단계를 따라야 하는 절차인가? → Skill 또는 `references/`
4. 특정 역할·모델·도구 권한이 필요한가? → `.claude/agents/` · `.codex/agents/`
5. 반드시 차단·실행되어야 하는가? → 훅 · `.githooks/pre-commit`
6. 개인에게만 필요한가? → `settings.local.json`(미추적)
7. 현재 작업에만 필요한가? → `plans/` (지속 지침에 넣지 않는다)
8. 외부 시스템 접근이 필요한가? → MCP (현재 해당 없음)

---

## 7. 하네스 실행 계획

`skills/하네스/SKILL.md` 판정: **대형**(계약·설정 다도메인 변경) → 웨이브 + 단일 라이터 직렬화 + 리뷰어 1회.

### 7.1 웨이브 분해 (파일 disjoint 보장)

| Wave | 워커 | 모델 | allowlist (이것만) | 게이트 |
|---|---|---|---|---|
| **W0** | 메인 solo | Opus | `.gitignore` · `.codex/hooks-probe.json` | Gate 0 실증(§5.0). **사용자 훅 승인 필요** |
| **W1-a** | 워커1 | sonnet | `scripts/hook_slide_guard.py` · `scripts/install_hooks.py`(신규) | `python scripts/hook_slide_guard.py --mode css-lint` 자가 테스트 · 기존 3모드 회귀 |
| **W1-b** | 워커2 | sonnet | `.githooks/pre-commit` · `.githooks/README.md` | 훅 설치 후 더미 커밋 시도 → 차단 확인 |
| **W2-a** | 워커3 | sonnet | `.codex/hooks.json` · `.codex/agents/*.toml` · `.codex/README.md` | JSON/TOML 파싱 + `codex doctor` |
| **W2-b** | 워커4 | sonnet | `.claude/agents/*.md` · `.claude/settings.json` · `.claude/launch.json` | JSON 파싱 · R-A15 반영 |
| **W3** | **메인 단독** | Opus | `AGENTS.md` · `CLAUDE.md` · `references/검증-명령-지도.md` · `.claude/rules/deck.md` | 판단이 무겁고 토큰이 가벼운 일 → **하네스 §6-6에 따라 solo** |
| **W4** | 워커5 | sonnet | `skills/README.md` · `.claude/skills/리서치/SKILL.md` · `.agents/README.md` · `.claude/skills/README.md` | `verify_skill_setup.py` |
| **W5** | 리뷰어 | sonnet(읽기전용) | **없음(수정 금지)** | 독립 검토(§8) |

### 7.2 워커 규율 (프롬프트에 반드시 넣을 것)

- **allowlist 밖 변경 금지. 밖의 변경을 발견하면 되돌리지 말고 보고.**
- **임시 파일은 저장소 안 `tmp/`에만.** 시스템 임시 폴더·스크래치패드 금지. (2026-07-30 워커 4개 전원 이탈 전례)
- **보고는 10줄 이내.** 산문 보고서 금지.
- 완료 시 `git status --short` 귀속 확인 후 보고.

### 7.3 짝 파일 주의 (같은 워커가 함께 고쳐야 하는 것)

| 짝 | 이유 |
|---|---|
| `hook_slide_guard.py` ↔ `.codex/hooks.json`·`.claude/settings.json` | 새 모드 이름이 양쪽에 동시에 있어야 함 → **W1-a가 스크립트, W2가 호출자. 순서 의존 → W1-a 완료 후 W2 착수** |
| `.claude/agents/research-worker.md` ↔ `.claude/skills/리서치/SKILL.md` 「강제 수준」 표 | agent 파일이 생기면 표의 `maxTurns ❌`가 거짓이 됨 → **W4가 표를 고치되, W2-b 완료 후** |
| `install_hooks.py` ↔ `verify_skill_setup.py` 신규 검사 | 설치와 검증이 짝 → **W1-a가 둘 다** |

### 7.4 하지 말 것

- 같은 파일을 두 워커에 나눠 주기 (전례: 후행 쓰기가 선행 변경을 덮음)
- 메인이 큰 파일을 직접 읽기 (전례: Opus 캐시읽기 55.2M)
- 워커 자기보고를 게이트 없이 수용
- 병렬화 금지 대상(플레이북 §13.5): **같은 파일 동시 수정 · 동일 명령 반복 실행 · 공통 정본을 각 워커가 따로 재작성 · 순차 의존이 강한 단계**

### 7.5 ⚠️ `Explore`·`Plan` 서브에이전트는 `CLAUDE.md`를 읽지 않는다 (플레이북 §4.12)

`[공식]` Claude Code의 built-in `Explore`·`Plan`은 **빠른 탐색을 위해 `CLAUDE.md`와 부모 세션 Git 상태를 생략한다.** 다른 서브에이전트는 일반적으로 프로젝트 memory를 로드한다.

**이 계획에 미치는 영향**

- 이 계획의 조사 워커 4개는 전부 `Explore`였다 → **AGENTS.md의 「tmp/ 제약」을 자동으로 알지 못했다.** 실제로 프롬프트에 명시했기 때문에 지켜졌고, 저장소 밖 잔여물이 0개였다.
- 따라서 AGENTS.md L136의 *"서브에이전트에게도 이 제약을 프롬프트에 명시해 전달한다"* 는 **막연한 조심이 아니라 공식 동작에 대한 정확한 대응**이다 → `KEEP`, 그리고 **왜 필요한지(Explore가 CLAUDE.md를 생략함)를 한 줄로 덧붙인다.**
- W1-a~W5 워커에도 동일하게 적용한다. 아래 템플릿에 이미 포함돼 있다.

### 7.6 워커 프롬프트 템플릿 (그대로 사용)

```text
너는 Sonnet 실행 워커다. 저장소 루트: C:\Users\miso\Desktop\template

## 편집 허용 파일 (allowlist — 이것만. 삭제·다른 파일 변경 금지)
- <파일1>
- <파일2>

## 잠긴 결정 (변경 금지)
<메인이 확정한 스키마·형식·값 — 계획서 §N 발췌>

## 작업
<무엇을 어디에. 구체적으로>

## 규율 (전부 준수)
- allowlist 밖은 건드리지 마라. 밖의 변경을 발견하면 되돌리지 말고 보고하라.
- 임시·중간 파일은 저장소 안 `tmp/`에만 만들어라. 시스템 임시 폴더·%TEMP%·AppData·
  스크래치패드에 쓰지 마라. (너는 부모 세션의 CLAUDE.md를 상속받지 않으므로 이 제약이
  여기 적혀 있지 않으면 너에게 존재하지 않는다.)
- 새로 쓰는 문장은 [적용 범위]+[행동]+[방법]+[예외]+[검증 증거] 형식을 따르고,
  "적절히"·"신중하게"·"완벽하게" 같은 관찰 불가 어휘를 쓰지 마라.
- 삭제·이동한 규칙은 계획서 §6.4 형식으로 기록하라.

## 완료 후
1. <verify 명령> 실행 → 종료코드 보고
2. `git status --short`로 allowlist 밖 변경 0건 확인
3. **10줄 이내**로 보고: 변경 요약 · 검증 결과 · 막힌 점
```

---

## 8. 검토 기준 (독립 리뷰어 W5)

수정에 참여하지 않은 Sonnet 리뷰어에게 **git diff와 실제 파일만** 주고 아래를 확인시킨다. 이전 분석을 전제로 주지 않는다.

| # | 검토 항목 | 판정 방법 |
|---|---|---|
| V1 | **보존 규칙 누락** — 삭제·이동된 규칙이 전부 새 위치에서 추적되는가 | §6.2 장부 대 diff 대조. 장부에 없는 삭제가 1건이라도 있으면 FAIL |
| V2 | **상충 지침** — 같은 주제에 대해 두 파일이 다른 말을 하는가 | 이동된 절의 키워드로 전 저장소 grep |
| V3 | **존재하지 않는 명령·경로** — 새로 쓴 문서의 모든 백틱 경로가 실존하는가 | 경로 추출 → `test -e` 전수 |
| V4 | **잘못된 로드 가정** — "Codex가 하위 AGENTS.md를 자동 로드한다" 같은 오해가 새로 들어갔는가 | 로드 관련 문장 전수 확인 |
| V5 | **자연어 의존 잔존** — §2.6의 5개 규칙 중 강제로 옮기지 못한 것이 명시돼 있는가 | "미강제"로 표기됐는지 확인. 조용히 넘어갔으면 FAIL |
| V6 | **불필요한 상시 컨텍스트** — AGENTS.md에 덱 작업 전용 내용이 남아 있는가 | 절 단위로 "이게 리서치 세션에도 필요한가" 판정 |
| V7 | **집행부 미수정**(안티패턴 #2) — 규칙을 바꿨는데 검증 스크립트를 안 고친 곳 | `verify_skill_setup.py` 검사 항목 대 변경 파일 대조 |

> **V7 실제 발견(2026-08-05 · 치명 · 해소됨).** 독립 리뷰어가 잡았다: `references/검증-명령-지도.md:72`는 `verify_skill_setup.py`가 「훅 설치 상태」를 검사한다고 적었고 이 계획 §5.5도 그렇게 약속했는데, **실제 코드에는 `githooks`·`hooksPath` 검사가 0건**이었다. 즉 이번 리팩터링이 세운 「플랫폼 공통 최종 증거 층」이 **미설치 상태로 조용히 무력화될 수 있는데 그걸 감지할 장치가 없었다** — 그리고 훅이 미설치면 pre-commit 자체가 안 돌아 **스스로 미설치를 알릴 수도 없다**(자기참조 사각지대).
> 이 리팩터링이 경계하던 「선언과 집행 불일치」(유형⑤)를 **강제 계층 자신에 대해** 저지른 사례다.
> 조치: `verify_skill_setup.py`에 `core.hooksPath == .githooks` + `.githooks/pre-commit` 존재 검사 2건을 추가. **훅을 일부러 해제해 exit 1을 재현하고 재설치 후 exit 0을 확인**했다.

**리뷰어 프롬프트 금기**: "이전 분석이 맞는지 확인하라"고 쓰지 않는다. 확증 편향을 부른다. 대신 *"이전 분석을 전제하지 말고 현재 git diff와 실제 활성 지침 파일을 독립 검토하라"* 로 시작한다(플레이북 §15.7).

### 8.1 읽기 전용 행동 검증 시나리오 (플레이북 §15.5) — 문법이 아니라 **행동**을 본다

리팩터링 후 **새 세션**에서 아래를 실행한다. "파일을 수정하지 말라"를 매번 명시한다. 정적 검사가 통과해도 이 시나리오가 실패하면 리팩터링 실패다.

| ID | 플랫폼 | 프롬프트 | 통과 기준 |
|---|---|---|---|
| **B1** | 양쪽 | "파일을 수정하지 말고 현재 활성 지침 파일을 넓은 범위부터 좁은 범위 순으로 나열하고, 각각 어떤 범위에 적용되는지와 충돌 가능성을 표시하라." | §2.10 로드 그래프와 일치. 충돌 0 보고 |
| **B2** | 양쪽 | "파일을 수정하지 말고 2주차 덱을 고친 뒤 실행해야 할 검증 명령을 근거 파일과 함께 보고하라." | `run_deck_checks.py`와 렌더 증거 요구를 **스스로 찾아낸다**(이관 후에도 라우팅이 작동하는지 확인) |
| **B3** | 양쪽 | "파일을 수정하지 말고 `강의덱.html`을 바꾸려면 어떤 원본과 생성기를 고쳐야 하는지 설명하라." | shard(`강의덱.초안/`) + `assemble_deck.py`를 지목 |
| **B4** | 양쪽 | "실제로 만들지는 말고, 임시 측정 스크립트를 어디에 두어야 하는지와 그 이유를 답하라." | 저장소 안 `tmp/`를 지목 |
| **B5** | 양쪽 | "코드를 수정하지 말고 이 프로젝트에서 작업 완료를 선언하기 전에 필요한 증거를 나열하라." | §9.4 증거 목록과 실질적으로 일치 |
| **B6** | **Codex** | `codex exec "활성 지침 소스를 순서대로 나열하고 파일을 수정하지 마라"` | `~/.codex/AGENTS.md` → 루트 `AGENTS.md` 순서를 정확히 보고 |

> **B2·B3이 이 리팩터링의 진짜 시험대다.** 80줄을 `references/`로 옮겼는데 에이전트가 그 파일을 못 찾으면, 줄 수만 줄고 규칙은 사라진 것이다(플레이북 §0 「줄 수 감소 자체는 성공이 아니다」).

---

## 9. 완료 기준 (Definition of Done)

> **모두 통과해야 완료다. 하나라도 미달이면 미완료로 보고한다.**
> 치명적 결함이 하나라도 남으면 나머지 점수와 무관하게 **완료 아님**(플레이북 §16).

### 9.1 기능 게이트 (기계 판정 · 종료코드)

| # | 검증 | 통과 기준 |
|---|---|---|
| D1 | `python scripts/verify_skill_setup.py` | exit 0 |
| D2 | `python scripts/verify_kit.py` | exit 0 |
| D3 | `python scripts/verify_subject_isolation.py` | exit 0 |
| D4 | `python scripts/verify_declared_vs_enforced.py` | exit 0 (**작업 전 실측 = 0**) |
| D5 | `python -m unittest` 8모듈 전체 | `Ran 155 tests … OK` (**작업 전 실측 = 155 OK / 31.4s**). 일부만 돌리지 않는다 |
| D6 | `python scripts/hook_slide_guard.py --mode css-lint` 자가 테스트 | 위반 CSS → `decision:block` / 정상 CSS(`> b`) → 무출력 |
| D7 | `git config core.hooksPath` | `.githooks` |
| D8 | 더미 위반 커밋 시도 | pre-commit이 **차단**(exit≠0) |
| D9 | `.gitignore` negation | `git check-ignore .codex/hooks.json` → **미매치**(추적 가능) |
| D10 | `git status --short` | allowlist 밖 변경 **0건** |

### 9.2 강제 패리티 게이트 (실측 판정)

| # | 검증 | 통과 기준 |
|---|---|---|
| P1 | Gate 0 실증 결과가 문서화됨 | `PROGRESS.md`에 페이로드 덤프 실물 또는 "미지원" 판정이 기록됨 |
| P2 | Codex 세션에서 슬라이드 파일 편집 시 체크리스트 주입 | **실측 확인**(Codex로 재현). 불가하면 §5.6 폴백 적용 + 그 사실 명시 |
| P3 | Codex 세션에서 `강의덱.html` 직접 편집 시도 | **차단됨** 또는 폴백(pre-commit 차단)으로 잡힘 |
| P4 | 저장소 밖 경로 쓰기 시도 | 두 플랫폼 모두 차단 또는 경고 관측 |
| P5 | 「강제 계층 대응표」가 문서에 존재 | Claude 수단 ↔ Codex 수단 ↔ 공통(git) 3열 표 |
| P6 | **미달성 항목이 은폐되지 않음** | 동등하지 못한 항목이 있으면 "지연된 동등" 또는 "미강제"로 **명시** |

### 9.3 컨텍스트·품질 게이트 (수치 판정)

| # | 지표 | 작업 전 | 목표 |
|---|---|---:|---|
| Q1 | `AGENTS.md` 바이트 | 20,644 | ~~≤ 12,000~~ → **실측 13,491 (−34.6%) · 미달 1,491B** |
| Q2 | Codex 결합 바이트(전역 포함) | 25,547 | **≤ 20,000** → **실측 18,394 = 한도의 56.1% · 달성** |
| Q3 | `CLAUDE.md` 실효 줄 수 | 182 | ~~≤ 110~~ → **실측 155 · 미달** |

> **Q1·Q3 미달을 숨기지 않고 기록한다.** 두 값은 콘텐츠 인벤토리를 알기 전에 정한 자체 목표였고, 남은 분량은 전부 **항상 필요한 계약·라우팅**이다(완료 정의 · 강제 계층 표 · 필수 읽기 · 정본 지도). 여기서 더 줄이려면 규칙을 지워야 하는데, 그것은 이 계획 §16의 첫 줄(「줄 수 감소는 성공이 아니다」)을 위반한다.
> **구속력 있는 제약은 Q2 하나다** — Codex 32KiB는 초과 시 지침이 잘리는 하드 한도이고, 78.0% → 56.1%로 여유가 생겼다. Claude 공식 기준은 **파일당 200줄 미만**이며 `AGENTS.md` 134줄·`CLAUDE.md` 22줄로 각각 충족한다(Q3의 「실효 155」는 import 전개 합계로, 공식 기준보다 엄격한 자체 지표였다).
> **목표를 사후에 낮춘 것이 아니라, 미달을 미달로 보고하고 근거를 남긴다.**
| Q4 | 두 파일 간 중복 항목 | 6+ | **0**(포인터 제외) |
| Q5 | 사실 불일치(§2.7) | 6 | **0** |
| Q6 | 근거 없는 명령·경로 | — | **0**(V3 전수 통과) |
| Q7 | 미등재 `scripts/` | 3 | 0 또는 **의도적 제외 사유 기록** |
| Q8 | 충돌 규칙(상위↔하위, 도구 간) | 0 | **0 유지** |
| Q9 | 추상·관찰불가 규칙 | — | **0**(§6.5 어휘 목록 grep) |
| Q10 | path-scoped로 전환한 규칙 | 0 | 덱·kit 영역(훅 경로 매칭 + rules) |
| Q11 | 참조 문서로 이관한 절차 | 0 | 「실행과 검증」 43줄 + 사고 이력 37줄 |
| Q12 | agent 파일로 이동한 역할 | 0 | **4**(`.claude/agents/` 2 + `.codex/agents/` 2) |
| Q13 | 강제 설정으로 이동한 정책 | 0 | **≥3**(생성물 보호·tmp 격리·evals 회귀) |
| Q14 | 미검증 항목 | — | **명시됨**(0을 목표로 하지 않는다 — 숨기지 않는 것이 목표) |

> ⚠️ **Q1~Q3이 목표에 도달했는데 B2·B3(§8.1)이 실패하면 실패다.** 바이트가 줄었지만 규칙이 도달하지 않은 상태다.

### 9.4 증거 게이트 (플레이북 §1.3)

완료 보고에 아래가 **전부** 있어야 한다. 하나라도 없으면 완료 아님.

- [ ] 수정 대상 파일 목록
- [ ] 수정 전후 diff (`git diff --stat` + 핵심 파일 전문 diff)
- [ ] **활성 지침 로드 경로 확인** — Claude `/context`(+ 필요 시 `/doctor`의 `CLAUDE.md` trim 제안) + Codex `codex exec "현재 활성 지침 파일을 순서대로 나열하라"` 결과. 로드 시점·이유까지 봐야 하면 **`InstructionsLoaded` 훅**으로 기록한다
- [ ] **행동 검증 시나리오 B1~B6 결과**(§8.1) — 정적 통과만으로는 증거가 되지 않는다
- [ ] 실제 검증 명령의 존재 확인 (V3 전수 결과)
- [ ] 보존 규칙 추적표 (§6.2 장부에 실제 이동 위치 기입)
- [ ] 충돌 규칙 처리 결과
- [ ] **실행한 검증 명령과 실제 출력** (요약 아님 · 종료코드 포함)
- [ ] **실행하지 못한 검증과 그 이유** — 숨기지 않는다
- [ ] 남은 위험 · 사용자 결정 필요 항목
- [ ] 워커별 `git status --short` 귀속 확인 결과
- [ ] **저장소 밖 잔여 파일 0개 확인** (옮긴 것은 정리가 아니다)

### 9.5 회귀 안전 게이트

| # | 확인 |
|---|---|
| S1 | 1주차 동결 산출물 **미변경** (`git diff --stat courses/*/sessions/1주차/` 가 비어 있음) |
| S2 | 워크트리 3개 **그대로 등재** (`git worktree list` 3+1행) |
| S3 | `.claude/settings.local.json` **미추적 유지** |
| S4 | 새 훅이 **기존 정상 작업을 막지 않음** — 정상 shard 편집 1회가 통과하는지 실측 |
| S5 | 오탐률 측정 결과 기록 (`generated-guard`·`tmp-guard` 관측 모드 결과) |

### 9.6 품질 점수표 (플레이북 §16) — 최종 판정용

| 항목 | 배점 | 이 프로젝트에서의 판정 기준 |
|---|---:|---|
| 사실 정확성 | 25 | §2.7 불일치 6건 해소 + V3 경로 전수 통과 |
| 범위 정확성 | 15 | 규칙이 §6.6 결정 질문대로 배치됨 · 개인 설정이 공유 파일에 없음 |
| 실행 가능성 | 15 | 모든 명령이 실측 존재 · 완료 조건이 종료코드로 판정됨 |
| 충돌 없음 | 10 | Q8 = 0 · 상위·하위 모순 없음 |
| 컨텍스트 효율 | 10 | Q1·Q2·Q3 달성 **且** B2·B3 통과 |
| 안전성 | 10 | 강제층 분리 · `.gitignore` negation이 쿠키 데이터를 노출하지 않음(D9) |
| 보존성 | 5 | V1 전수 통과 · 장부에 없는 삭제 0 |
| 유지보수성 | 5 | §15 추가·삭제 조건과 점검 시점이 문서화됨 |
| 검증 증거 | 5 | §9.4 증거 11종 전부 제출 |

**판정**: 90~100 배포 가능 / 80~89 경미한 개선 후 사용 / 70~79 중요 결함 잔존 / 70 미만 재수행.
**치명적 결함(§3.1)이 하나라도 남으면 총점과 무관하게 완료 아님.**

---

## 10. 리스크와 롤백

| 리스크 | 확률 | 영향 | 대응 |
|---|---|---|---|
| Codex `PreToolUse` 미지원 | 중 | 큼 | **Gate 0가 사전 차단.** §5.6 폴백 |
| 훅 해시 재승인을 사용자가 못 함 | 중 | 큼 | 훅 승인은 **사용자 전용 행위** — 계획에 승인 요청 시점을 명시 |
| `tmp-guard`가 정상 작업을 막음 | 중 | 중 | 관측 모드 선행 · 오탐 0 확인 후 승격 |
| pre-commit이 느려 개발 흐름 방해 | 중 | 중 | staged 경로 기반 조건 실행 · 무거운 검사는 pre-push로 |
| AGENTS.md 축약 중 규칙 유실 | 중 | **큼** | §6.2 장부 + V1 전수 대조. **장부에 없는 삭제 금지** |
| `.gitignore` negation 실수로 쿠키·로그인 데이터 커밋 | 낮 | **매우 큼** | D9 검사 + `git status`로 `.codex/` 아래 추가되는 파일 **눈으로 확인 후** 커밋 |

**롤백**: 각 Wave 종료 시 verify 통과분을 커밋해 복구 지점을 만든다. 전체 되돌림은 `git revert`(reset 아님 — 워크트리 3개가 걸려 있다).

---

## 11. 사용자 결정 필요 (ESCALATE)

작업 전에 답이 필요한 것은 **1건뿐**이고, 나머지는 진행 중 확인이면 된다.

| # | 항목 | 왜 사용자만 결정할 수 있나 | 기본값(무응답 시) |
|---|---|---|---|
| **E1** | **Codex 훅 승인** — Gate 0 프로브와 최종 훅을 `/hooks`로 신뢰해야 동작 | 훅 신뢰는 사용자 계정의 보안 결정이다. 에이전트가 대신할 수 없다 | 승인 없으면 §5.6 폴백(git 훅 전량 위임)으로 자동 전환 |
| E2 | `.claude/launch.json`의 타 PC 엔트리 삭제 | 사용자의 다른 환경에서 쓰던 설정일 수 있음 | **삭제**(존재하지 않는 경로 · C2) |
| E3 | `AGENTS_CLAUDE_REFACTORING.md` 최종 처분 | 플레이북은 상시 지침이 아니다(문서 스스로 그렇게 규정) | `_dev/설계기록/`으로 이관 + 미추적 유지 |
| E4 | pre-commit 차단 강도 | 팀 개발 흐름에 대한 취향 | 위 표대로(차단 5종 + 경고 1종) |

---

## 12. 실행 순서 요약

```
E1 확인 → W0 Gate 0 실증 ─┬─ 통과 → W1-a → W1-b ─┐
                          └─ 실패 → §5.6 폴백    ├→ W2-a·W2-b(병렬) → W3(메인 solo)
                                                  ┘                      → W4 → W5 리뷰 → DoD 판정 → 보고
```

각 Wave 종료 시: `git status --short` 귀속 확인 → 해당 게이트 실행 → 통과분 커밋.

**전체 종료 시**: 회귀 스위트 8모듈 전량 → 행동 검증 B1~B6(§8.1) → §9 DoD 5종 판정 → §9.6 점수 산출 → §13 형식으로 `FINAL_REPORT.md` → `MEMORY.md`의 `## 미해결` 갱신(해결된 항목 삭제).

---

## 13. 최종 보고서 형식 (플레이북 §18) — 완료 시 이 골격으로 제출

`plans/instruction-refactor/FINAL_REPORT.md`에 아래 10절을 **빈 절 없이** 채운다. 해당 없는 절은 삭제하지 말고 "해당 없음 + 이유"를 쓴다.

```md
# 지침 리팩터링 보고서
## 1. 결론          — 판정(점수·등급) / 주요 개선 / 남은 위험
## 2. 실제 사용 도구 — Codex 버전 / Claude Code / git 훅
## 3. 기존 구조      — 표: 파일 | 역할 | 실제 로드 | 문제
## 4. 핵심 발견      — Critical / High / Medium / Low
## 5. 규칙 이동 장부  — 표: Rule ID | 이전 위치 | 새 위치 | 조치 | 근거
## 6. 수정 파일      — 파일 / 변경 / 보존
## 7. 삭제·제외      — 항목 / 이유 / 대체   (§6.4 형식)
## 8. 검증          — 표: 검증 | 명령·방법 | 실제 결과(종료코드 포함)
## 9. 미검증·결정 필요 — 항목 / 이유 / 필요한 결정
## 10. 최종 점수     — §9.6 9항목 배점 + 총점
```

---

## 14. 플레이북 중 **적용하지 않는 것**과 그 이유

플레이북의 기능을 전부 쓰는 것이 목표가 아니다. 아래는 검토 후 **의도적으로 제외**했다. 나중에 "왜 안 썼나"를 다시 묻지 않기 위해 근거를 남긴다.

| 플레이북 항목 | 판정 | 이유 |
|---|---|---|
| `AGENTS.override.md` (§3.4) | **비적용** | 한시적 대체 장치다. 이 프로젝트에 마이그레이션·특수 환경이 없고, override는 같은 디렉터리 `AGENTS.md`를 **통째로 가려** 사고 위험만 늘린다 |
| 하위 디렉터리 `AGENTS.md`/`CLAUDE.md` (§13.2) | **비적용** | monorepo가 아니다. 하위 지침 0개인 현 구조에서 Codex의 CWD 문제도 발생하지 않는다(§2.10). 경로별 지침은 훅 매칭으로 해결한다 |
| `claudeMdExcludes` (§4.8) | **비적용** | 제외할 하위 `CLAUDE.md`가 없다 |
| `## Code Review Rules` (§3.7) | **비적용** | GitHub 원격·CI가 없다(`.github/` 부재 실측). 원격을 붙이면 그때 재검토 |
| Codex Rules `*.rules` (§3.8) | **보류** | 명령 프리픽스 단위 allow/forbidden이라 경로 기반 규칙에 맞지 않고, `paths` 스코프 문법이 문서에서 확인되지 않았다(§5.3) |
| `project_doc_max_bytes` 상향 (§3.5) | **비적용** | 한도 상향은 마지막 수단. ①②⑤⑥으로 목표 달성 가능(§6.1) |
| `.mcp.json` (§4.12) | **비적용** | 외부 시스템 접근 요구가 없다 |
| `CLAUDE.local.md` (§4.2) | **비적용** | 개인 설정은 이미 `.claude/settings.local.json`(미추적)이 담당한다. 계층을 늘리면 로드 순서만 복잡해진다 |
| `--add-dir` 추가 디렉터리 memory (§4.9) | **비적용** | 저장소 밖 참조가 없다 |
| `.claude/output-styles/` · `.claude/commands/` | **비적용** | 현재 필요 없음 |

---

## 15. 유지보수 규칙 (플레이북 §26~§28) — 리팩터링 후 이 상태를 지키는 법

### 15.1 규칙을 **추가**해도 되는 조건

아래 중 하나가 관찰된 뒤에만 추가한다. **예상만으로 추가하지 않는다.**
같은 실수 2회 반복 / 같은 지적 반복 / 신규 참여자가 반드시 알아야 하는 비직관적 제약 / 에이전트가 파일은 찾지만 과도하게 많이 읽음 / 완료 보고와 실제 결과가 반복 불일치 / 회귀 원인이 지침 부재로 확인 / 하위 영역에 루트 규칙이 잘못 적용.

추가 **전에** 묻는다: ① 코드·훅·linter로 강제할 수 있는가 ② Skill이나 경로 규칙이 더 맞는가 ③ 개인 memory가 맞는가 ④ 현재 작업에만 필요한가(→ `plans/`).

> 이 프로젝트에는 이미 같은 취지의 `R-FEEDBACK-01`(같은 지적 2회 이상이면 규칙층으로 승격)이 있다. **둘은 같은 규칙이므로 하나로 합치고 `references/phases/08-검증.md`를 정본으로 삼는다.**

### 15.2 규칙을 **삭제**하는 조건

§6.4의 8개 조건과 동일. 삭제 시 §6.4 형식 기록 필수.

### 15.3 정기 점검 시점

- 새 과목(`courses/<과목>/`) 추가 시 — **`course` 훅이 과목 2개에서 조용히 죽는다**(§2.5 H5). 이때가 첫 시험대다
- `scripts/` 게이트 추가·변경 시 — `references/검증-명령-지도.md` 동기화
- Codex·Claude Code 주요 버전 변경 시 — 훅 이벤트명·페이로드 스키마 재확인(플레이북 §36)
- 새 Skill·agent 도입 시 — `verify_skill_setup.py` 검사 범위 확장 여부
- 반복적인 에이전트 실패 관찰 시

**점검 항목**: 실제 명령 / stale 경로 / 로드 그래프 / import / 줄·바이트 예산 / 충돌 / local 파일 추적 여부 / 설정과 자연어 규칙의 중복 / agent 모델·도구 / Skill 발견 경로.

### 15.4 최신성 주의 (플레이북 §36)

이 계획의 Codex 관련 `[공식]` 근거는 **2026-08-05 기준**이다. Codex는 alpha 버전(`0.146.0-alpha.9.2`)이라 **훅 이벤트명·페이로드·custom agent 스키마가 바뀔 수 있다.** 실행 착수 시점에 Gate 0(§5.0)로 **다시 실측**하고, 문서 예시보다 **로컬 실행 결과를 우선**한다.

---

## 16. 이 계획이 스스로에게 거는 규율

- **줄 수 감소는 성공이 아니다.** 규칙이 사라지거나 이동한 곳에서 로드되지 않으면 실패다(플레이북 §0).
- **"고쳤다"로 끝내지 않는다.** 등재 위치를 반드시 적는다(R-FEEDBACK-01).
- **실행하지 못한 검증은 실행하지 못했다고 쓴다.** 통과로 쓰지 않는다.
- **문서 값을 낮춰 불일치를 없애지 않는다.**
- 이 계획서의 판단 중 워커 보고와 다른 것은 §6.2 R-A14처럼 **근거와 함께 명시**했다.
