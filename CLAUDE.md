@AGENTS.md

# Claude Code 차이

- Claude Code 프로젝트 스킬 진입점은 `.claude/skills/vibecoding-deck/SKILL.md`다.
- 명시 호출은 `/vibecoding-deck`, 일반 강의덱·교육 슬라이드 요청은 진입점의 `description`으로 자동 호출한다.
- 진입점은 규칙을 복제하지 않는 얇은 어댑터다. 호출되면 저장소 루트 `SKILL.md`를 끝까지 읽고, 그 문서가 가리키는 모든 상대 경로를 저장소 루트 기준으로 해석한다.
- 공통 작업 매뉴얼과 PPT 제작 규칙은 각각 `AGENTS.md`와 루트 `SKILL.md`가 정본이다. `.claude/`에는 Claude Code의 탐색·호출 차이만 둔다.
- Windows에서는 `python`을 사용한다. Claude 전용 `ui-ux-pro-max`를 직접 실행할 때는 저장소 루트에서 `python .claude/skills/ui-ux-pro-max/scripts/search.py ...`를 사용한다.
