# .agents — Codex 프로젝트 설정

이 폴더는 저장소의 공통 Skill과 프로젝트 전용 기능을 Codex가 탐색하도록 연결하는 플랫폼 어댑터다. PPT 제작 규칙의 공통 정본은 루트 `SKILL.md`와 그 파일이 가리키는 `kit/`, `references/`, `scripts/`이며, 플랫폼별 진입점에는 이 규칙을 복제하지 않는다.

## 구성

- `skills/vibecoding-deck/`: Codex 탐색용 얇은 어댑터. 루트 `SKILL.md`를 완전히 읽고 저장소 루트를 기준으로 공통 참조와 스크립트를 사용한다.
- `skills/리서치/`·`skills/콘텐츠/`·`skills/검토/`: 팀 워크플로 스킬 3종의 Codex 얇은 어댑터. 각 정본은 저장소 루트 `skills/<이름>/SKILL.md`이며, `$리서치`처럼 명시 호출로만 발동한다(하단 "팀 워크플로 스킬" 참조).
- `skills/하네스/`: 횡단 오케스트레이션 프로토콜(파이프라인 역할 아님)의 Codex 얇은 어댑터. 정본은 저장소 루트 `skills/하네스/SKILL.md`이며, `$하네스`로 명시 호출한다.
- `skills/ui-ux-pro-max/`: Codex용 디자인 근거 Skill. `SKILL.md`, 검색 스크립트, 디자인 데이터가 함께 들어 있다.
- `skills/_template/`: 새 프로젝트 스킬을 만들 때 복사하는 Codex 규격 골격.
- `agent-memory/vibecoding-deck/MEMORY.md`: 양 플랫폼이 함께 읽는 누적 규칙·버그의 단일 정본. Codex는 루트 `AGENTS.md`의 필수 읽기 경로로, Claude Code는 `CLAUDE.md`의 `@AGENTS.md` import를 통해 같은 경로를 따른다.

루트 `AGENTS.md`는 공통 프로젝트 지침 정본이며 저장소 구조, 불변 규칙, 실행·검증 절차를 제공한다. `CLAUDE.md`에는 `@AGENTS.md` import와 Claude Code 차이만 둔다.

## 의도적으로 옮기지 않은 파일

- `.claude/settings.json`: Claude의 도구 권한 문법이다. Codex 권한은 실행 환경과 승인 정책이 관리한다.
- `.claude/launch.json`: Claude 임시 scratch 서버의 절대 경로를 담고 있어 이식성이 없다. 필요할 때 `python -m http.server`를 실행한다.

## 공통 정본과 동기화 원칙

- PPT 제작 조건과 디자인 규칙은 루트 `SKILL.md` 및 그 참조 파일에서만 수정한다. `.agents/skills/vibecoding-deck/SKILL.md`에는 Codex 탐색 메타데이터와 공통 정본을 여는 절차만 둔다.
- 어댑터의 `name`과 `description`은 루트 `SKILL.md`의 frontmatter와 동일하게 유지한다.
- `ui-ux-pro-max`의 데이터나 스크립트를 플랫폼별로 유지할 때는 양쪽 사본을 함께 갱신한다.
- 누적 규칙은 `.agents/agent-memory/vibecoding-deck/MEMORY.md`만 갱신한다. `.claude/agent-memory/.../MEMORY.md`는 이 정본을 가리키는 포인터이므로 규칙을 복제하지 않는다.

## Windows 실행

저장소 루트의 PowerShell에서 `python`을 사용한다.

```powershell
python scripts/verify_deck.py <덱>.html --parts N
python scripts/inline_deck.py <덱>.html --offline
python .agents/skills/ui-ux-pro-max/scripts/search.py ...
python scripts/verify_skill_setup.py
```

## 팀 워크플로 스킬

이 폴더의 `skills/리서치/`·`skills/콘텐츠/`·`skills/검토/` 어댑터 정본은 저장소 루트 `skills/<이름>/SKILL.md`다. 등재·계약·호출 규약은 루트 `skills/README.md` 참조(여기에 복제하지 않는다). 횡단 프로토콜 `skills/하네스/`도 같은 원칙을 따른다.
