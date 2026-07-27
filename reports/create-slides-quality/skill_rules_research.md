# Skill·AGENTS.md·Codex 규약 리서치 (Agent B)

> ## ⚠️ 상태: UNVERIFIED · 정본 아님 · `/리서치` 입력 후보
>
> **2026-07-28 사용자 지시로 지위가 강등됐다.** 폐기하지는 않되, 이 파일은 **선행 조사 및 후보 출처 모음**이지 강의 콘텐츠의 정본이 아니다. 정본은 공식 `/리서치`가 `sessions/2주차/자료/` 5파일에 산출한다.
>
> - **금지**: 이 파일의 문장을 그대로 개념KB에 복사하는 것.
> - **필수**: 아래 주장들을 `/리서치`에서 **출처를 다시 열어** 실제 주장과 일치하는지 확인한 뒤 정본화한다 — 규칙 파일이 기술적 강제가 아니라 컨텍스트로 작동한다는 점 · 실제 강제가 hooks·sandbox·승인 정책이라는 별도 계층에 있다는 점 · AGENTS.md의 상속·병합 방식 · AGENTS.md 크기 제한 · Skill의 크로스벤더 호환성 · 제품별 Skill 확장 필드 · 현재 저장소의 규칙↔강제 간격 실사용 사례.
> - **파일 실측(2026-07-28 메인 직접 측정)**: 36,616 bytes · 335줄. 이전 인수인계서가 기록한 SHA-256[:12] `c07403ffa21a`는 **이 배너 삽입 이전 값**이다. 배너 삽입으로 해시가 바뀌므로, 이후의 무결성 기준은 **체크포인트 커밋된 현재 파일**로 재설정한다(저장 시점 차이로 추정하지 말 것).
> - **날짜 민감성**: §4는 Codex 문서의 2026-07-27 스냅샷이다. `/리서치` 재검증 시 문서 날짜·제품 버전을 다시 기록한다.

- 조사일: 2026-07-27
- 대상: 바이브코딩 강의 콘텐츠(20~40대 비전공자, ChatGPT + Codex 사용자) — 정식 용어 유지 원칙
- 작성자: Agent B (Sonnet 리서치, 파일 1개만 씀)

---

## §1. 조사 범위·중단 기준

B1(Skill 일반 vs 제품)·B2(AGENTS.md·규칙 파일)·B3(Codex 실제 동작)·B4(강의용 변환)·B5(저장소 대조)를 순서대로 조사했다. 중단 기준(공통 정의·주요 이견·제품별 차이·수업 적용 사례·위험한 오개념 확보)은 각 항목에서 아래처럼 충족했다:

- **Skill**: 공통 정의(agentskills.io) · 주요 이견 없음(Anthropic 발명이 사실상 표준으로 굳음) · 제품별 차이(Claude Code 파일 위치·`disable-model-invocation` 같은 확장 vs Codex `.agents/skills` 위치·`$`/`/skills` 호출) · 위험한 오개념(설명 필드=발동 조건이라는 점을 놓치면 오발동/미발동) 확보.
- **AGENTS.md**: 공식 스펙 원문(agents.md) · Codex 공식 로딩 순서(learn.chatgpt.com) · Claude Code가 이 파일을 **읽지 않는다**는 제품 차이 · "닫는 파일이 이긴다"는 표현이 실제로는 병합(concatenate)이지 override가 아니라는 이견까지 확보.
- **Codex**: 승인·샌드박스 모드 공식 정의, 기본값, AGENTS.md 크기 상한(32 KiB) 확보. 다만 "학생이 실제로 보는 승인 프롬프트의 정확한 화면 문구/버튼 라벨"은 공식 문서에 스크린샷·문구가 없어 §9에 실패 로그로 남긴다.
- **위험한 오개념**은 "규칙 파일=강제"라는 가정이 다층적으로 틀렸다는 것(§8)에서 중단선을 그었다 — 이 한 문장이 B1·B2·B3를 관통하는 가장 위험한 오개념이라 더 파는 대신 근거를 두텁게 쌓았다.

---

## §2. Skill — 일반 개념인가 제품 기능인가

### 2.1 결론부터

**"Skill"은 지금은 사실상 하나의 크로스벤더 제품 표준 이름이다.** 원래는 Anthropic이 만든 Claude 전용 기능이었지만, **agentskills.io**라는 오픈 스펙으로 공개 이관됐고 2026-07 기준 OpenAI Codex·Cursor·GitHub Copilot·VS Code·Gemini CLI·JetBrains Junie 등 30개 이상 도구가 같은 `SKILL.md` 포맷을 채택했다. "재사용 가능한 작업 절차"라는 일반 개념 자체는 새로운 것이 아니지만(런북·플레이북·SOP), **"Skill"이라는 이름과 `SKILL.md` 파일 형식·frontmatter 규격은 특정 표준을 가리키는 고유명사**다.

> "Agent Skills are a lightweight, open format for extending AI agent capabilities with specialized knowledge and workflows... The Agent Skills format was originally developed by Anthropic, released as an open standard, and has been adopted by a growing number of agent products." — [agentskills.io](https://agentskills.io) (fetched 2026-07-27)

### 2.2 스펙 최소 요건 (1차 근거)

`SKILL.md`는 폴더 하나 + 필수 `SKILL.md` 파일(선택적으로 `scripts/`·`references/`·`assets/`)로 구성되며, frontmatter에 **`name`**(소문자·숫자·하이픈만, 64자 이하, "anthropic"/"claude" 등 예약어 금지)과 **`description`**(비어있지 않음, 1024자 이하)이 **필수**다. 본문(Instructions)은 스펙상 자유 형식이며, "입력·절차·산출물·검증"이라는 4요소 자체가 스펙에 강제된 것은 아니다.

> "Every Skill requires a SKILL.md file with YAML frontmatter... **Required fields:** name and description" — [Claude Platform Docs, Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) (fetched 2026-07-27)

"검증(feedback loop)"·"워크플로 체크리스트"·"plan-validate-execute" 같은 요소는 **베스트 프랙티스 가이드의 실무 권고**이지 스펙 필수 요건이 아니다 — 이 구분은 정확히 지켜야 한다.

> "**Common pattern:** Run validator → fix errors → repeat. This pattern greatly improves output quality." / "Create verifiable intermediate outputs... the 'plan-validate-execute' pattern" — [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) (fetched 2026-07-27)

### 2.3 프롬프트 템플릿 vs Skill — 1차 근거 있는 실제 구분

이건 실무 folklore가 아니라 **1차 문서가 명시적으로 대비시키는 구분**이다:

> "Unlike prompts (conversation-level instructions for one-off tasks), Skills load on demand, so you don't have to repeat the same guidance across conversations." — [Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)

핵심 차이축: (a) **로딩 시점** — 프롬프트는 매번 대화에 새로 입력해야 하지만 Skill은 파일로 존재해 필요할 때 자동 로드됨(progressive disclosure 3단계: 이름/설명 상시 로드 → 트리거 시 본문 로드 → 필요 시 번들 자료 로드). (b) **일회성 vs 재사용** — 프롬프트는 "이번 한 번"의 지시, Skill은 "이후 매번" 쓰이는 절차.

### 2.4 프로젝트 규칙(CLAUDE.md/AGENTS.md)과 Skill의 차이 — 1차 근거

Claude Code 공식 문서가 정확히 이 경계를 규정한다:

> "Create a skill when you keep pasting the same instructions, checklist, or multi-step procedure into chat, or when a section of CLAUDE.md has grown into a procedure rather than a fact. Unlike CLAUDE.md content, a skill's body loads only when it's used, so long reference material costs almost nothing until you need it." — [Extend Claude with skills](https://code.claude.com/docs/en/skills) (fetched 2026-07-27)

> "If an entry is a multi-step procedure or only matters for one part of the codebase, move it to a skill or a path-scoped rule instead." — 같은 문서

즉 구분축은 **"사실(fact)이냐 절차(procedure)냐"** + **"항상 필요하냐 특정 상황에만 필요하냐"**다. 규칙 파일은 매 세션 전량 로드(컨텍스트 상시 점유), Skill은 트리거될 때만 로드(컨텍스트 온디맨드).

### 2.5 너무 크다/너무 세밀하다 — 문서화 vs 추정

- **너무 큰 Skill**: 문서화됨(정량 기준 있음). "Keep SKILL.md body under 500 lines for optimal performance. If your content exceeds this, split it into separate files." — [best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices). "Avoid deeply nested references... Keep references one level deep from SKILL.md"도 같은 문서의 명시 규칙.
- **너무 세밀한(과다 분할) Skill**: **1차 문서에 명시적 경고는 찾지 못했다.** "vague names 피하기"·"일관된 명명 규칙"은 있지만 "Skill을 너무 잘게 쪼개면 나쁘다"는 정량/정성 경고는 공식 문서에서 발견하지 못했음(§10 모름 처리). 다만 discovery 메커니즘상(설명 필드로 매칭) 지나치게 많은 유사 Skill은 설명 문구가 겹쳐 오발동 가능성이 논리적으로 따라오지만, 이는 1차 문서의 명시적 진술이 아니라 아키텍처로부터의 추론이므로 강의에서는 "추정"으로 표시해야 한다.

### 2.6 사용 조건 · 비사용 조건 (1차 근거)

**사용**: 같은 절차를 반복 붙여넣고 있을 때, CLAUDE.md의 한 섹션이 사실이 아니라 절차로 자라났을 때, 특정 코드베이스 일부에서만 쓰이는 다단계 작업일 때(위 2.4 인용).
**비사용/대안**: "항상 알아야 할 사실"(빌드 명령·컨벤션)은 규칙 파일에, "특정 파일 타입에만 적용"은 path-scoped rule에, "즉시 실행 액션(배포·커밋처럼 부작용 있는 것)"은 `disable-model-invocation: true`로 자동 트리거를 막고 수동 호출(`/name`)로만 열어야 한다는 것도 명시됨(§6 저장소 대조에서 실사용 확인).

### 2.7 제품별 차이 요약

| 항목 | Claude (Claude Code/claude.ai/API) | OpenAI Codex |
|---|---|---|
| 파일 형식 | `SKILL.md` + frontmatter(name/description) — 동일 표준 | `SKILL.md` + frontmatter(name/description) — 동일 표준("Skills build on the open agent skills standard") |
| 배치 위치(Claude Code) | `~/.claude/skills/`(개인) · `.claude/skills/`(프로젝트) | `.agents/skills`(저장소) · `$HOME/.agents/skills`(사용자) · `/etc/codex/skills`(관리자) · 시스템 번들 |
| 발동 | 이름/설명 상시 로드 후 관련성 매칭 시 자동 로드, 또는 `/skill-name` 수동 | `$` 멘션 또는 `/skills` 명령으로 명시 선택(explicit), 또는 설명 매칭 자동(implicit) |
| Claude Code 확장 기능 | `disable-model-invocation`(자동발동 차단)·`user-invocable`(메뉴 노출 제어)·subagent 실행(`context: fork`)·동적 컨텍스트 주입 — 표준을 넘어선 벤더 확장 | 문서에서 동급 확장 기능 명시 없음(§10) |
| Claude API/claude.ai 사전탑재 | pptx/xlsx/docx/pdf 4종 pre-built Skill 제공 | 해당 없음(§10, 확인 안 됨) |

출처: [Extend Claude with skills](https://code.claude.com/docs/en/skills), [Codex Build skills](https://learn.chatgpt.com/docs/build-skills) (원래 URL `developers.openai.com/codex/skills`에서 308 리다이렉트, 둘 다 2026-07-27 fetch).

---

## §3. AGENTS.md·프로젝트 규칙 파일 — 실제 규약

### 3.1 AGENTS.md 공식 스펙 (agents.md — 정본)

> "AGENTS.md is a simple, open format for guiding coding agents... a README for agents: a dedicated, predictable place to provide the context and instructions to help AI coding agents work on your project." — [agents.md](https://agents.md/) (fetched 2026-07-27)

**배치**: 저장소 루트. 모노레포는 "Place another AGENTS.md inside each package."
**중첩·우선순위 (정확한 인용)**: **"Agents automatically read the nearest file in the directory tree, so the closest one takes precedence."** 그리고 **"The closest AGENTS.md to the edited file wins; explicit user chat prompts override everything."**

이 두 문장이 이 리서치에서 가장 정확도가 중요한 인용이다 — "가장 가까운 파일이 이긴다"와 "명시적 채팅 프롬프트가 전부를 이긴다"는 순서(우선순위) 문제이지, 규칙 파일이 사용자 지시보다 우위에 있다는 뜻이 아니다.

**권장 섹션**: 프로젝트 개요·빌드/테스트 명령·코드 스타일·테스트 지침·보안 고려사항·커밋/PR 가이드라인.
**지원 도구**: OpenAI Codex·Google Jules·Factory·Aider·goose·VS Code·Devin·GitHub Copilot·Cursor·Zed·Warp·JetBrains Junie 등 20개 이상, 6만 개 이상 오픈소스 프로젝트가 채택(agents.md 자체 통계 — 갱신 시점 불명, §10).

### 3.2 Codex의 실제 로딩 규칙 (1차, learn.chatgpt.com — developers.openai.com에서 308 리다이렉트)

> "Codex builds an instruction chain... **Global scope** (Codex home, default `~/.codex`): Reads `AGENTS.override.md` if present; otherwise `AGENTS.md`. Uses only the first non-empty file. **Project scope** (Git root to current directory): Walks the path checking each directory for `AGENTS.override.md`, then `AGENTS.md`... **Merge order**: Files concatenate from root down with blank lines. Files closer to your current directory override earlier guidance because they appear later in the combined prompt." — [Codex AGENTS.md guide](https://learn.chatgpt.com/docs/agent-configuration/agents-md) (fetched 2026-07-27)

중요한 정확성 포인트: Codex는 여러 계층의 AGENTS.md를 **override가 아니라 concatenate(누적 병합)** 한다. "가까운 파일이 이긴다"는 실제로는 "가까운 파일이 프롬프트 뒤쪽(더 최근 읽힌 위치)에 온다"는 것이지, 상위 파일 내용이 삭제되는 게 아니다. 강의에서 "가까운 게 이긴다"고만 말하면 오해를 유발한다 — "뒤에 와서 더 강하게 반영된다"가 더 정확하다.

**크기 상한**: `project_doc_max_bytes` 기본값 32 KiB — 합산 크기가 이 상한에 도달하면 이후 파일은 추가되지 않는다. **빈 파일은 무시**된다.

### 3.3 CLAUDE.md — Claude Code 공식 스펙 (1차, code.claude.com)

**AGENTS.md와의 관계 — 가장 중요한 제품 차이:**

> "Claude Code reads `CLAUDE.md`, not `AGENTS.md`. If your repository already uses `AGENTS.md` for other coding agents, create a `CLAUDE.md` that imports it so both tools read the same instructions without duplicating them." — [How Claude remembers your project](https://code.claude.com/docs/en/memory) (fetched 2026-07-27)

권장 패턴은 정확히 `@AGENTS.md` import 한 줄 + 그 아래 Claude 전용 섹션 — **이 리포지토리의 `CLAUDE.md`가 정확히 이 패턴을 쓰고 있음**(§6에서 확인).

**로드 위치와 순서 (넓은 범위 → 좁은 범위, 뒤에 온 것이 최신 컨텍스트)**:
1. Managed policy (조직, OS별 고정 경로) — 항상 적용, 개별 설정으로 제외 불가
2. `~/.claude/CLAUDE.md` (사용자, 전 프로젝트)
3. `./CLAUDE.md` 또는 `./.claude/CLAUDE.md` (프로젝트, 팀 공유)
4. `./CLAUDE.local.md` (개인, git 무시 권장)

> "All discovered files are concatenated into context rather than overriding each other... instructions closer to where you launched Claude are read last." — 같은 문서

이 역시 Codex와 마찬가지로 **override가 아니라 concatenate**다. 크기 권고: "target under 200 lines per CLAUDE.md file"(강제 아님, 준수도(adherence) 저하 경고만 있음).

### 3.4 크로스벤더 표준 여부 — 명확히

- **AGENTS.md**: 사실상 크로스벤더 오픈 포맷(20+ 도구 지원, agents.md가 정본). **단, Claude Code는 예외** — CLAUDE.md라는 자사 파일명을 쓰고 AGENTS.md는 import를 통해서만 간접 지원한다.
- **CLAUDE.md**: Claude Code(및 Anthropic 생태계) 전용, 벤더 로컬 규약.
- **결론**: "규칙 파일 하나로 모든 도구가 통한다"는 말은 반은 맞고 반은 틀리다 — AGENTS.md 자체는 크로스벤더지만, Claude Code 사용자는 반드시 `CLAUDE.md`(또는 심볼릭 링크/`@AGENTS.md` import)를 별도로 두어야 한다. Windows에서는 관리자 권한 없이 심볼릭 링크가 안 되므로 공식 문서도 "use the `@AGENTS.md` import instead"를 명시한다 — 이 저장소가 Windows 환경이라는 점에서 특히 관련 있는 사실.

### 3.5 위험한 오개념 — "규칙 파일이 있으면 에이전트가 반드시 읽고 따른다"

**공식 문서가 스스로 부정한다:**

> "Claude treats them as context, not enforced configuration. To block an action regardless of what Claude decides, use a PreToolUse hook instead." — [How Claude remembers your project](https://code.claude.com/docs/en/memory)

> "CLAUDE.md content is delivered as a user message after the system prompt, not as part of the system prompt itself. Claude reads it and tries to follow it, but there's no guarantee of strict compliance, especially for vague or conflicting instructions." — 같은 문서

> "AGENTS.md is not a long-term memory system and it does not learn automatically. It is a static instruction file loaded at startup." — (2차 요약이지만 Codex 공식 가이드 톤과 일치, 아래 §9 참고)

즉 규칙 파일은 **"약속"이지 "강제"가 아니다.** 강제하려면 Claude Code의 경우 hooks(`PreToolUse`), Codex의 경우 sandbox mode(기술적 실행 제약, §4)를 써야 한다 — 이 구분(소프트 컨텍스트 vs 하드 기술 제약)이 수업에서 가장 강조해야 할 위험한 오개념이다.

---

## §4. Codex 실제 동작 (수업에서 학생이 쓰는 도구) — 날짜 민감성 있음

⚠️ **날짜 민감성 경고**: 아래는 2026-07-27 fetch 시점(`learn.chatgpt.com` — `developers.openai.com` 도메인이 308로 리다이렉트됨, 즉 문서 사이트 자체가 최근 이전됨)의 스냅샷이다. Codex는 승인 정책 옵션(예: `auto_review`)이 최근 추가된 것으로 보이는 등 변화가 빠른 영역이므로, 강의 제작 시점에 재확인을 권장한다.

### 4.1 컨텍스트 읽기

Codex는 세션 시작 시 1회(실행당 1회, TUI 기준 보통 세션당 1회) AGENTS.md 인스트럭션 체인을 구성한다 — §3.2 참고. 작업 시작 전에 이미 컨텍스트로 포함된다.

### 4.2 승인(approval) / 샌드박스(sandbox) 모드 — 정확한 이중 축

공식 문서가 명시하는 이중 레이어 구조:

> "Sandbox mode" controls **what Codex can do technically** when executing model-generated commands; "Approval policy" determines **when Codex must ask you before it executes an action**. — [Codex agent approvals & security](https://learn.chatgpt.com/docs/agent-approvals-security) (fetched 2026-07-27)

**샌드박스 모드**:
- `workspace-write`: "Codex can read files, make edits, and run commands in the workspace"
- `read-only`: 읽기·질의응답만
- `danger-full-access`(별칭 `--yolo`): "No sandbox; no approvals"

**승인 정책**:
- `on-request`: 특정 액션마다 승인 요청
- `never`: 승인 프롬프트 완전 비활성
- `untrusted`: "Codex runs only known-safe read operations automatically"
- `auto_review`: 리뷰어 에이전트를 거쳐 승인 라우팅

**기본값(신규 사용자가 실제로 보는 것)**: 폴더 유형에 따라 Codex가 자동 추천 — **버전관리(git) 폴더는 "Auto" 모드**(= `workspace-write` + `on-request`), **비버전관리 폴더는 `read-only`**. 네트워크 접근은 기본적으로 꺼져 있다("By default, the agent runs with network access turned off").

**승인이 필요한 트리거**: 워크스페이스 밖 파일 편집, 네트워크 접근, 신뢰되지 않은 명령 실행, 파괴적 주석이 달린 MCP/앱 도구 호출.

⚠️ **§9로 넘긴 항목**: 학생이 실제로 화면에서 보는 승인 다이얼로그의 정확한 문구·버튼 라벨(예: "Approve"/"Deny" 같은 텍스트)은 공식 문서 텍스트에 스크린샷/문구 인용이 없어 확인하지 못했다 — 강의 시연 슬라이드는 실제 스크린샷을 새로 캡처해야 한다(공식 문서 인용만으로 화면 문구를 단정하지 말 것).

### 4.3 Codex의 하드 제약 vs Claude의 소프트 컨텍스트 — 핵심 대비

Codex의 sandbox mode는 **기술적으로 실행을 차단하는 하드 제약**이다(예: `read-only`에서는 파일 쓰기가 실제로 불가능). 반면 AGENTS.md/CLAUDE.md는 **컨텍스트로 전달되는 소프트 지시**다(§3.5). 이 비대칭이 §8의 핵심 위험한 오개념과 직결된다 — "AGENTS.md에 '이 폴더는 건드리지 마'라고 적으면 안전하다"는 가정은 틀렸다. 실제 안전장치는 sandbox/승인 정책(기술적 강제)이지 규칙 파일(맥락 제공)이 아니다.

---

## §5. 강의용 변환 재료

### 5.1 개념별 변환 표 (요지)

| 개념 | 실제 문제 상황 | 정식 용어 | 쉬운 설명 | 언제 쓰나 | 언제 안 쓰나 | 실패 사례(오개념) |
|---|---|---|---|---|---|---|
| Skill | 매번 같은 작업 절차를 채팅에 복붙 | Agent Skill (SKILL.md, agentskills.io 오픈 표준) | "AI에게 주는 매뉴얼 폴더" — 필요할 때만 펼쳐 읽는 참고서 | 반복 절차, 특정 상황에만 필요한 다단계 작업 | 매 세션 항상 필요한 사실(→ 규칙 파일), 1회성 지시(→ 그냥 프롬프트) | "설명만 잘 써두면 항상 자동으로 켜진다"→ description 매칭 실패 시 미발동 |
| AGENTS.md | 팀마다 다른 도구에 규칙을 각각 설명해야 함 | AGENTS.md (agents.md 오픈 스펙) | "AI 동료를 위한 README" | 여러 AI 코딩 도구를 함께 쓸 때 공통 규칙 두는 곳 | Claude Code 전용 규칙(→ CLAUDE.md), 1회성 요청 | "적어두면 AI가 무조건 지킨다"→ 컨텍스트일 뿐, 강제 아님(§3.5) |
| CLAUDE.md | Claude Code가 AGENTS.md를 안 읽음 | CLAUDE.md | "Claude 전용 README, `@AGENTS.md`로 기존 규칙을 불러올 수 있다" | Claude Code 프로젝트 규칙 | 다른 도구와 공유할 규칙의 유일한 정본으로 삼는 것(→ AGENTS.md에 두고 import) | "심볼릭 링크로 연결하면 끝"→ Windows에서 관리자 권한 필요, `@import` 권장 |
| Codex 승인모드 | 학생이 "허용" 버튼을 왜 눌러야 하는지 모름 | 승인 정책(approval policy) + 샌드박스 모드(sandbox mode) | "샌드박스=할 수 있는 일의 울타리, 승인=울타리 밖으로 나갈 때마다 묻는 것" | 기본 Auto 모드로 시작, 위험한 작업만 승인 | 신뢰 안 되는 저장소에서 `--yolo`/`danger-full-access` | "승인 안 눌러도 안전할 것"→ 신뢰 안 된 코드가 워크스페이스 밖·네트워크 접근 시도 시 승인 없인 못 나감(안전장치 실재) |

### 5.2 최소 예시 — AGENTS.md (슬라이드용, 1차 근거 기반)

agents.md 권장 섹션(§3.1)을 그대로 따른 최소 예시 — 발명이 아니라 스펙이 권장하는 필드만 채웠다:

```markdown
# AGENTS.md

## 프로젝트 개요
할 일 목록 웹앱. React + Node.js.

## 빌드·테스트 명령
- 설치: `npm install`
- 테스트: `npm test`
- 실행: `npm run dev`

## 코드 스타일
- 들여쓰기 2칸, 세미콜론 사용
- 컴포넌트는 `src/components/`에 위치

## 커밋 메시지
- `feat:`, `fix:`, `docs:` 접두어 사용
```

출처: 섹션 구성은 agents.md의 "Popular choices include: Project overview / Build and test commands / Code style guidelines / Testing instructions / Security considerations / Commit messages or pull request guidelines"를 그대로 따름(§3.1).

### 5.3 최소 예시 — SKILL.md (슬라이드용, 1차 근거 기반)

Claude 공식 문서의 "Skill structure" 예시(§2.2 인용)를 그대로 축소 인용:

```markdown
---
name: writing-commit-messages
description: git diff를 분석해 커밋 메시지를 생성한다. 사용자가 커밋 메시지 작성이나 스테이징된 변경사항 리뷰를 요청할 때 사용한다.
---

# 커밋 메시지 작성

## 절차
1. git diff를 읽고 변경 내용을 요약한다
2. `type(scope): 설명` 형식으로 제목을 쓴다
3. 필요하면 본문에 이유를 덧붙인다
```

출처: frontmatter 필수 필드(name/description)와 "third person으로 쓸 것"·"무엇을 하는지 + 언제 쓰는지 모두 포함" 규칙은 [best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)의 "Writing effective descriptions"를 따름(§2.2, §2.6).

### 5.4 구조도 후보

- **로딩 순서 다이어그램**: Managed policy → User(`~/.claude/CLAUDE.md`) → Project(`./CLAUDE.md`) → Local(`./CLAUDE.local.md`) — 화살표는 "먼저 읽힘 → 나중에 읽힘(더 최근 컨텍스트)" 방향으로, "이긴다"는 표현 대신 "뒤에 와서 더 강하게 반영"으로 라벨링(§3.3 정확성 포인트).
- **Skill 3단계 progressive disclosure**: 이름/설명(항상) → 본문(트리거 시) → 번들 자료/스크립트(필요 시) — 토큰 비용 3단 막대그래프(§2.2 표 활용, Level 1 ~100 tokens / Level 2 <5k tokens / Level 3 0 until accessed).
- **Codex 이중 축**: X축 샌드박스(read-only/workspace-write/danger-full-access), Y축 승인정책(never/on-request/untrusted) — 교차점에 "Auto 모드(초심자 기본값)" 표시.

### 5.5 검증 방법 (학습자가 스스로 확인)

- Claude Code: `/context` 명령으로 실제 로드된 Memory files 목록 확인(§3.3, "run /context and check the list under Memory files").
- Codex: `/permissions` 명령으로 read-only 전환 가능 여부 확인(§3.2 인접 자료).

---

## §6. 저장소 실사용 대조 (읽기 전용)

이 저장소(`C:\Users\miso\Desktop\template`)의 실제 사용 패턴을 공식 스펙과 대조했다.

### 6.1 CLAUDE.md ↔ AGENTS.md — 공식 권장 패턴과 정확히 일치

저장소 루트 `CLAUDE.md`는 파일 첫 줄이 `@AGENTS.md`이고 그 아래 "# Claude Code 차이" 섹션이 이어진다. 이것은 §3.3에서 인용한 공식 권장 패턴,

> "create a `CLAUDE.md` that imports it so both tools read the same instructions without duplicating them... `@AGENTS.md` ## Claude Code [Claude-specific instructions]"

과 **정확히 동일한 구조**다 — 가공되지 않은 실제 사례로 슬라이드에 쓸 수 있다. AGENTS.md는 이 저장소에서 "정본"(Codex가 직접 읽는 파일), CLAUDE.md는 그 위에 얇게 얹힌 "Claude Code 차이"만 담은 어댑터라는 설계도 스펙의 "closest wins"/"nearest file" 개념과 결이 같다(다만 이 저장소는 중첩 AGENTS.md가 아니라 단일 루트 파일 + 플랫폼별 얇은 어댑터 구조를 쓴다는 점에서 agents.md의 모노레포 다중 AGENTS.md 패턴과는 다르다 — 저장소는 "한 정본 + 어댑터"이지 "레이어별 AGENTS.md 중첩"이 아니다).

### 6.2 `.claude/skills/*/SKILL.md` ↔ 공식 Skill 표준 — frontmatter 요건 충족, 확장 필드는 미사용

`.claude/skills/create-slides/SKILL.md`를 읽은 결과 frontmatter에 `name`·`description`만 있고(§2.2 필수 요건 충족), Claude Code 확장 필드(`disable-model-invocation`·`user-invocable`)는 create-slides에는 없다 — 즉 create-slides는 **자동 발동을 의도적으로 유지**한다("PPT 조건이나 디자인 규칙을 추가·변경하지 않는다"는 순수 어댑터 역할).

### 6.3 `skills/README.md` — 공식 확장 필드를 정확히 인지하고 "의도적으로 미채택"

가장 흥미로운 대조점이다. `skills/README.md`는 다음과 같이 적는다:

> "기계적 차단(`disable-model-invocation`)은 (c)항 스킬 체이닝까지 죽이므로 채택하지 않았다."

`disable-model-invocation`은 §2.7·§6.2에서 확인했듯 **실제로 존재하는 Claude Code 공식 frontmatter 필드**다(자동 발동을 막고 `/name`으로만 호출하게 강제). 저장소는 이 기술적 강제 수단의 존재를 정확히 인지한 채, "팀 스킬 3종(리서치·콘텐츠·검토)은 명시 호출 전용"이라는 규칙을 **기술적 강제가 아니라 관례(honor-system)로만 규정**하기로 의식적으로 선택했다고 스스로 밝힌다. 이는 §3.5·§4.3에서 확인한 "규칙 파일=소프트 컨텍스트, 진짜 강제는 별도 기술 수단"이라는 공식 문서의 구도를 저장소가 정확히 이해하고 그 트레이드오프를 명시적으로 감수한 사례 — 강의에서 "관례적 보증과 기술적 강제의 차이"를 설명할 실제 사례로 쓸 수 있다.

### 6.4 팀 스킬(`skills/콘텐츠/SKILL.md`) — CLAUDE.md와 Skill의 역할 분리가 실제로 작동

`skills/콘텐츠/SKILL.md`(집필 스킬)는 §0 불변 규칙·8단계 워크플로·산출물 규격까지 담아 500줄을 훌쩍 넘는 긴 절차 문서다. 이는 공식 문서가 구분한 "사실(fact, 항상 필요) vs 절차(procedure, 필요할 때만)" 축(§2.4)에서 명백히 "절차" 쪽이며, `AGENTS.md`(공통 매뉴얼·불변 규칙 요지)에는 "상세·최신 규칙은 `.agents/agent-memory/create-slides/MEMORY.md`를 정본으로 삼는다"처럼 포인터만 두고 본문을 옮겨두지 않는다 — 규칙 파일은 짧게, 절차는 스킬/참조 문서로 분리하라는 공식 권고(§2.4·§3.3 200줄 권장)와 실사용이 일치한다.

### 6.5 발견되지 않은 것

`.claude/skills/`에서 공식 `references/`·`assets/` 디렉터리 활용은 `_template`에서만 예시로 존재하고(`references/example-reference.md`), 실제 배포 스킬(`create-slides`)은 그 대신 저장소 루트의 `kit/`·`references/`·`scripts/`를 참조하는 얇은 어댑터 구조를 쓴다 — 스펙이 강제하지 않는 자유도이므로 이견이 아니라 정상적인 구조 선택이다.

---

## §7. 주장·출처 표

| 주장 | 정의 유형 | 출처(URL) | 1차 여부 | 공통 합의 | 논쟁·제품 차이 | 강의 사용 위치 |
|---|---|---|---|---|---|---|
| Agent Skills는 Anthropic이 만든 오픈 표준, SKILL.md=폴더+frontmatter(name/description 필수) | 정의 | https://agentskills.io | 1차(표준 정본) | 합의 | 없음(Claude·Codex·Cursor·Copilot 등 동일 포맷) | §2.1, §5.3 |
| "Unlike prompts... Skills load on demand" — 프롬프트와 Skill의 차이 | 정의·비교 | https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview | 1차 | 합의 | 없음 | §2.3, §5.1 |
| "move it to a skill or a path-scoped rule instead" — CLAUDE.md와 Skill의 경계 | 규약 | https://code.claude.com/docs/en/skills | 1차 | 합의(Claude Code 한정) | Codex엔 이 정확한 경계 문서화 없음(§10) | §2.4, §5.1 |
| SKILL.md 본문 500줄 권장, 참조는 1단계 깊이만 | 실무 권고 | https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices | 1차 | 합의 | "너무 세밀한 분할"의 명시적 경고는 못 찾음(§2.5) | §2.5, §6.4 |
| "The closest AGENTS.md... takes precedence"·"explicit user chat prompts override everything" | 규약 | https://agents.md/ | 1차(스펙 정본) | 합의 | Codex 구현은 override가 아니라 concatenate(§3.2)로, 표현과 실제 동작 뉘앙스 차이 있음 | §3.1, §5.4, §8 |
| Codex AGENTS.md 로딩 — global(override 우선) → project(nearest, concatenate), 32 KiB 상한 | 규약 | https://learn.chatgpt.com/docs/agent-configuration/agents-md (원 URL developers.openai.com/codex/guides/agents-md, 308 리다이렉트) | 1차 | 합의 | — | §3.2, §5.4 |
| "Claude Code reads CLAUDE.md, not AGENTS.md" — import 패턴 권장 | 규약 | https://code.claude.com/docs/en/memory | 1차 | 합의 | 벤더 로컬(Claude Code만 해당) | §3.3, §3.4, §6.1 |
| CLAUDE.md/AGENTS.md는 "context, not enforced configuration" | 위험한 오개념 반박 | https://code.claude.com/docs/en/memory | 1차 | 합의 | — | §3.5, §4.3, §8 |
| Codex 샌드박스(기술 제약) vs 승인정책(요청 시점) 이중 축, 기본값 Auto(git repo)/read-only(비git) | 규약 | https://learn.chatgpt.com/docs/agent-approvals-security (원 URL developers.openai.com/codex/agent-approvals-security, 308 리다이렉트) | 1차 | 합의 | 날짜 민감(§4 경고) | §4.2, §5.1, §5.4 |
| `disable-model-invocation: true` — Claude Code 자동발동 차단 frontmatter 필드 | 정의 | https://code.claude.com/docs/en/skills (persisted fetch) | 1차 | 합의 | Codex에 동급 필드 문서화 확인 못함(§10) | §6.3 |
| AGENTS.md가 "Agentic AI Foundation / Linux Foundation" 산하 표준이라는 주장 | 거버넌스 주장 | 2차 요약(WebSearch, 원출처 불명확 — asdlc.io류) | **2차, 미확인** | 불명 | agents.md 자체 페이지 fetch에서는 이 거버넌스 문구를 확인하지 못함 | 사용 보류(§9) |

---

## §8. 위험한 오개념

1. **"AGENTS.md/CLAUDE.md에 규칙을 적어두면 AI가 반드시 지킨다."** — 공식 문서가 명시적으로 부정: "Claude treats them as context, not enforced configuration"(§3.5). 실제 강제는 hooks(Claude Code)나 sandbox/승인 정책(Codex) 같은 별도 기술 계층에서만 일어난다. 이 저장소의 팀 스킬 명시 호출 규약조차 "honor-system"임을 스스로 인정한다(§6.3) — 교육 자료가 "규칙 파일=안전장치"라고 가르치면 위험하다.
2. **"가장 가까운 AGENTS.md가 이긴다 = 상위 파일 내용이 사라진다."** — 실제로는 override가 아니라 concatenate다(§3.2, §3.3). 상위 규칙은 여전히 컨텍스트에 남아있고, 가까운 파일이 "더 나중에·더 눈에 띄게" 반영될 뿐이다. 두 규칙이 충돌하면 AI가 임의로 하나를 고를 수 있다는 경고도 공식 문서에 있다("Claude may pick one arbitrarily").
3. **"Skill 설명(description)만 잘 써두면 항상 자동으로 잘 켜진다."** — description은 시스템 프롬프트에 상시 포함되는 매칭 신호일 뿐이며(§2.2 Level 1), 다른 Skill 설명과 겹치거나 모호하면 오발동·미발동이 일어난다. best-practices 문서 전체가 이 discovery 실패를 줄이려는 저작 가이드다.
4. **"Claude Code는 AGENTS.md를 그냥 읽는다."** — 아니다. **읽지 않는다.** `CLAUDE.md`만 읽으며 AGENTS.md를 쓰려면 반드시 `@AGENTS.md` import(또는 심볼릭 링크, Windows에선 관리자 권한 필요)를 걸어야 한다(§3.3). "AGENTS.md 하나면 모든 AI 도구에서 통한다"는 말을 무비판적으로 가르치면 학생이 Claude Code에서 규칙이 안 먹히는 걸 겪고 혼란스러워한다.
5. **"승인 프롬프트에서 '허용'을 누르지 않으면 아무 일도 안 일어나서 안전하다."** — 이건 맞는 방향이지만, 반대로 "Auto 모드가 기본이니 뭘 눌러도 워크스페이스 안에서는 괜찮다"는 안일함도 위험하다. 워크스페이스 밖 파일·네트워크 접근·파괴적 MCP 도구 호출은 Auto 모드에서도 승인을 요구하도록 설계되어 있다(§4.2) — 이 경계선(워크스페이스 안/밖)을 학생에게 명확히 짚어줘야 한다.
6. **"Skill 표준은 Anthropic/Claude 전용 기능이다."** — 더 이상 사실이 아니다(§2.1). 학생이 "Claude 스킬"이라고만 알고 있으면 Codex의 `$`/`/skills` 호출을 이해 못한다 — 같은 파일 포맷을 도구마다 다른 위치·다른 호출 방식으로 쓴다는 점을 짚어야 한다.

---

## §9. 조사 실패 로그

- `https://developers.openai.com/codex/skills` — 308 리다이렉트 → `https://learn.chatgpt.com/docs/build-skills`(대체 fetch 성공, 인용에 반영).
- `https://developers.openai.com/codex/agent-approvals-security` — 308 리다이렉트 → `https://learn.chatgpt.com/docs/agent-approvals-security`(대체 fetch 성공).
- `https://developers.openai.com/codex/guides/agents-md` — 308 리다이렉트 → `https://learn.chatgpt.com/docs/agent-configuration/agents-md`(대체 fetch 성공). **참고**: `developers.openai.com` 도메인이 통째로 `learn.chatgpt.com`으로 이전된 것으로 보임 — 이 자체가 "최근 변경" 신호이므로 §4 날짜 민감성 경고에 반영했다.
- Codex 실제 승인 다이얼로그의 화면 문구(버튼 라벨 등) — 공식 텍스트 문서에는 스크린샷/정확한 UI 문구 인용이 없어 확보하지 못함. 강의 시연용 스크린샷은 별도로 직접 캡처해야 함(§4.2 끝에 명시).
- "AGENTS.md가 Linux Foundation 산하 Agentic AI Foundation이 관리한다"는 거버넌스 주장 — WebSearch 요약에서만 나왔고 agents.md 정본 페이지의 실제 fetch 텍스트에서는 이 문구를 확인하지 못함. 2차 출처 미상이라 §7 표에 "미확인"으로 표시하고 본문 채택 보류.
- "너무 세밀하게 쪼갠 Skill이 왜 나쁜가"에 대한 1차 문서의 명시적 경고 — 검색·fetch한 범위(overview·best-practices·agentskills.io) 안에서 찾지 못함. 추가로 Anthropic 엔지니어링 블로그 원문 전체를 정독하면 나올 수도 있으나, 이번 조사에서는 WebSearch 요약까지만 확인했고 전문 fetch는 시간상 하지 않았다(§10 모름 처리, 필요시 추가 조사 여지 있음).

---

## §10. 모름

- Codex가 `.agents/skills`에서 Skill을 "implicit(자동)"으로 트리거할 때, Claude Code의 `disable-model-invocation` 같은 "수동 호출 전용으로 강제" 필드가 있는지 — 확인 못함.
- Claude API/claude.ai의 사전탑재 Skill(pptx/xlsx/docx/pdf) 4종이 Codex 쪽에도 동급으로 존재하는지 — 확인 못함(Codex 문서 fetch 범위에서 언급 없음).
- Codex 승인 다이얼로그의 정확한 UI 텍스트·버튼 라벨(스크린샷 수준) — §9 참고, 별도 캡처 필요.
- "너무 세밀하게 쪼갠 Skill"의 폐해에 대한 1차 문서 존재 여부 — §9 참고, 추가 조사 여지 있음.
- agents.md 표준의 정확한 거버넌스 주체(Linux Foundation 산하설의 진위) — §9 참고, 미확인.
- 6만 개 이상 프로젝트 채택·20개 이상 도구 지원이라는 agents.md 통계의 최신 갱신 시점 — 페이지 자체에 타임스탬프 없음.

---

## 파일 메타

- 파일: `reports/create-slides-quality/skill_rules_research.md`
- 다른 파일은 수정하지 않았다(읽기 전용 대조는 `AGENTS.md`·`skills/README.md`·`skills/콘텐츠/SKILL.md`·`.claude/skills/create-slides/SKILL.md`·`.claude/skills/_template/SKILL.md.template`만 Read).
