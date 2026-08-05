@AGENTS.md

# Claude Code 전용

공통 규칙은 위 import가 전부다. 여기에는 **Claude Code에서만 다른 것**만 둔다 — 중복해 적으면 두 파일이 어긋난다.

## 강제 계층

- 훅 배선은 `.claude/settings.json`(PreToolUse `checklist`·`course`·`generated-guard`·`tmp-guard` / PostToolUse `css-lint`)이고, 검사 로직은 전부 `scripts/hook_slide_guard.py` **한 벌**이다. 플랫폼별로 복제하지 않는다.
- 역할·도구·모델 제한은 `.claude/agents/*.md`가 정본이다. `/리서치` 워커는 `research-worker`(tools 화이트리스트 · `model: sonnet` · `maxTurns`)를 쓰고, 실행 후 `python scripts/analyze_agent_usage.py --tool-audit --session <세션ID>`로 감사한다(0 통과 / 3 위반). 규정 상세는 `.claude/skills/리서치/SKILL.md` 「워커 실행 통제」.
- 무엇이 실제로 막히는지는 `AGENTS.md` 「무엇이 기계로 강제되는가」 표가 정본이다.

## 서브에이전트에 규칙이 상속되지 않는다

built-in `Explore`·`Plan`은 속도를 위해 **`CLAUDE.md`와 부모 세션 Git 상태를 로드하지 않는다**(공식 동작). 그 워커가 반드시 지켜야 할 제약(특히 「임시 파일은 저장소 안 `tmp/`에만」)은 **위임 프롬프트에 직접 적어 보낸다.** 다른 서브에이전트는 프로젝트 memory를 로드한다.

## 확인 수단

- 실제로 로드된 지침은 `/context`로 확인한다. 상시 지침이 과다한지는 `/doctor`가 진단한다.
- `@` import는 파일을 나눌 뿐 **컨텍스트를 줄이지 않는다.** 상시 로드에서 빼려면 import가 아니라 «필요할 때 여는 참조 문서»로 옮겨야 한다(예: `references/검증-명령-지도.md`).
- Windows에서 Claude 전용 `ui-ux-pro-max`를 직접 실행할 때는 저장소 루트에서 `python .claude/skills/ui-ux-pro-max/scripts/search.py ...`.
