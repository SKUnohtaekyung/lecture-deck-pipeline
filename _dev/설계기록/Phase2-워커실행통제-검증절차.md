# Phase 2 워커 실행 통제 — 실측 기록

> 2026-07-23 · 브랜치 `refactor/research-skill` · Claude Code **2.1.207**
> 계획 정본: `C:\Users\miso\.claude\plans\spicy-baking-hammock.md` 「D. Phase 2 요구(§8)」
> **채택: 안 「가」 — `Agent(subagent_type: Explore, model: sonnet)`** (사용자 결정 2026-07-23)
> 규정 위치: `.claude/skills/리서치/SKILL.md` 「워커 실행 통제」

---

## 1. 왜 `.claude/agents/` frontmatter를 쓰지 않는가

1차 시도는 `.claude/agents/research-worker.md`에 `model`·`maxTurns`·`tools`·`disallowedTools`를 두는 안이었다.
**이 환경에서는 검증이 불가능해 폐기했다.**

| 경로 | 시도 | 결과 |
|---|---|---|
| 세션 내 `Agent` 호출 | `.claude/agents/rwtest-full.md` 생성 후 `subagent_type: rwtest-full` | ❌ `Agent type 'rwtest-full' not found. Available agents: claude, claude-code-guide, Explore, general-purpose, Plan, statusline-setup` |
| headless 재실행 | 격리 임시 프로젝트에서 `claude -p ... --model sonnet` | ❌ `Failed to authenticate: OAuth session expired and could not be refreshed` — 샌드박스 해제 후에도 동일. `ANTHROPIC_API_KEY`·`CLAUDE_CODE_OAUTH_TOKEN` 미설정 |

계획이 "공식 문서 설명만으로 통과 처리하지 마라"를 명시하므로 **미검증 상태로 채택하지 않았다.**
그 초안 파일은 삭제했다.

---

## 2. 실측된 환경 사실

프로브 2회. 웹 호출 0. 저장소 파일 변경 0.

| ID | 사실 | 근거 |
|---|---|---|
| **V-1** | 세션 시작 후 생성한 `.claude/agents/`는 **재시작 전까지 탐지되지 않는다** | 위 오류가 내장 6종만 열거 |
| **V-2** | 이 환경의 서브에이전트 생성 도구는 **`Agent`**이며 바닥 이름 **`Task` 도구는 없다**. `TaskCreate`·`TaskGet`·`TaskList`·`TaskOutput`·`TaskStop`·`TaskUpdate`는 백그라운드 작업 관리용 별개 도구 | 세션·워커 도구 목록 |
| **V-3** | **`Agent(model: "sonnet")` → 실제 실행 모델 `claude-sonnet-5`** (2/2). **Opus fallback 0건** | `--tool-audit` 트랜스크립트 측정 |
| **V-4** | headless Claude Code 재실행은 이 환경에서 **인증 불가** | 위 표 |
| **V-5** | **`Explore`는 `Bash`를 실제로 실행한다** — `echo probe1` 성공. 구조적 차단이 아니다 | 프로브 1 |
| **V-6** | `Explore` 도구 집합 = **부모 세션 도구 − {`Agent`, `Artifact`, `ExitPlanMode`, `Edit`, `Write`, `NotebookEdit`}** | 프로브 1의 `TOOLLIST` |
| **V-7** | `Explore`에는 `PowerShell`·브라우저 자동화(`mcp__Claude_Browser__*`)·`Skill`·`ToolSearch`가 있고, `Cron*`·`SendMessage`·`PushNotification`·`RemoteTrigger`·`scheduled-tasks`·`claude-in-chrome` 계열이 **deferred로 접근 가능**하다 | 프로브 1 |
| **V-8** | `Explore`의 시스템 프롬프트가 **스스로** "파일 생성 금지 · `>`/`>>`/heredoc 쓰기 금지"를 강제한다 — 프로브가 Bash 파일쓰기를 **정책상 회피**했다(능력 부재가 아님) | 프로브 1의 2단계 응답 |
| **V-9** | **`claude-code-guide`의 도구는 정확히 `Glob, Grep, Read, WebFetch, WebSearch` 5개이고 deferred 0개다** — Phase 2 허용목록과 **완전 일치** | 프로브 2 |

### V-5·V-7이 뒤집은 것

계획 §7.2는 `Explore`의 구조적 차단을 `Write`·`Edit`·`Agent`·`NotebookEdit`로 적었고 그건 맞다.
**그러나 남는 도구 표면이 예상보다 훨씬 넓다.** 특히:

- **`Bash`·`PowerShell`이 살아 있으므로 `Write` 차단만으로는 파일 쓰기를 막지 못한다.**
- `SendMessage`·`PushNotification`·`RemoteTrigger`·`Cron*`·`scheduled-tasks`는 **외부 전송·영속 설정** 표면이다.

→ 허용목록 5개는 **구조적으로 강제할 수 없다.** 자연어 지시 + **사후 트랜스크립트 감사**가 유일한 수단이다.
V-8 덕분에 실사용에서 파일 쓰기가 일어날 확률은 낮지만, **낮은 확률은 강제가 아니다.**

---

## 3. 감사 수단 (신설)

`scripts/analyze_agent_usage.py --tool-audit` — 기존 계측기에 **추가만** 했다(기존 경로 무변).

```bash
python scripts/analyze_agent_usage.py --tool-audit --session <세션ID>
# --allow "WebSearch,WebFetch,Read,Grep,Glob"   (기본값)
# --expect-model "claude-sonnet-5"              (기본값)
```

- 워커 로그를 **두 배치 방식 모두**에서 찾는다: 직접 `Agent` 호출은 `<세션>/subagents/agent-*.jsonl`,
  Workflow 팬아웃은 `<세션>/subagents/workflows/wf_*/agent-*.jsonl`.
  **직접 호출 경로는 기존 계측기가 보지 못하던 위치다.**
- 종료코드 `0` 통과 / `3` 위반(허용목록 외 도구 **또는** 모델 불일치, Opus는 별도 표기).

### 브레이크가 실제로 작동함을 확인 (positive control)

1.5-B는 "중단선이 한 번도 작동하지 않아 브레이크 자체가 미검증"이라 YELLOW였다. 이번엔 **의도적으로 위반을 만들어** 검출을 확인했다.

```
에이전트              경로      모델               턴  도구 호출
a2342f762f8125d1b   direct   claude-sonnet-5    2  -
afaecdf17b1a90c92   direct   claude-sonnet-5    7  Glob×1, Grep×1, Read×1  ⛔ Bash×1

  ✅ 모델: 전 워커가 claude-sonnet-5
  ⛔ 허용목록 외 도구: afaecdf17b1a90c92 → Bash×1
판정: ❌ 위반 있음                                          (종료코드 3)
```

> ⚠️ 이 `Bash×1`은 **능력 조사를 위해 내가 지시한 것**이며 리서치 실행 중 발생한 위반이 아니다.
> 감사기가 위반을 놓치지 않는지 확인하기 위한 **양성 대조**다.

테스트 6건 추가(합성 fixture `tests/fixtures/synthetic/sess-audit/`, 개인정보 없음):
직접 호출 레이아웃 탐지 · 위반 검출과 종료코드 · Opus fallback 표기 · allowlist 기준 통과 · 허용도구 오검출 없음 · 턴 계수.

---

## 4. Phase 2 요구 대비 달성표

| 계획 요구 | 결과 |
|---|---|
| 모델 지정, `inherit` 금지 | ✅ **구조적** — 호출 파라미터 `model: "sonnet"` → `claude-sonnet-5` 실측 |
| Opus fallback 시 RED | ✅ 감사가 검출·표기. 실측 0건 |
| `Agent` 중첩 차단 (D8) | ✅ **구조적** — `Explore`가 `Agent` 미보유 |
| `Write`·`Edit` 차단 | ✅ **구조적** — 미보유 (단, `Bash`로 우회 가능 → 아래) |
| `Bash` 불허 | ⚠️ **구조적 차단 불가.** 자연어 + 사후 감사 |
| 허용목록 5개로 제한 | ⚠️ **구조적 차단 불가.** 실제 표면은 훨씬 넓다(V-6·V-7) |
| 워커 턴 상한 (D2) | ❌ **미해소.** `maxTurns`는 frontmatter 전용이라 이 경로에 없다 |
| 워커 실행 인프라 (D5) | ✅ 규정 위치·호출 형태·감사 명령 확정 |

**D2는 안 「가」의 알려진 대가다**(사용자가 이 대가를 알고 선택했다). Phase 3에서 측정·기록으로 다룬다.

---

## 5. 사용자 결정 대기 — `claude-code-guide` 관찰 (V-9)

허용목록 5개와 **정확히 일치하는** 내장 서브에이전트가 실재한다.

| | `Explore` (현 채택) | `claude-code-guide` |
|---|---|---|
| 도구 표면 | 넓다 — `Bash`·`PowerShell`·브라우저·알림/스케줄 포함 | **정확히 `Glob, Grep, Read, WebFetch, WebSearch`. deferred 0** |
| 허용목록 강제 | 자연어 + 사후 감사 | **구조적** |
| 용도 적합성 | ✅ 읽기·탐색 전용 범용 조사 | ❌ 시스템 프롬프트가 **Claude Code/SDK/API 질문 답변용**으로 좁다 |
| 위험 | 도구 오용(감사로 사후 검출) | 조사 주제가 Anthropic 문서 쪽으로 **편향**되거나 범위 밖으로 거부될 수 있다 |

**자동 채택하지 않았다.** 실행 수단 변경은 사용자 결정 항목이다.
도구 차단의 확실성이 주제 적합성보다 중요하다면 `claude-code-guide`로 바꿀 수 있고,
그 경우 강의 주제 조사에서 실제로 쓸만한지 **별도 파일럿이 선행돼야 한다.**
