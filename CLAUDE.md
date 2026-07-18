@AGENTS.md

# Claude Code 차이

- Claude Code 프로젝트 스킬 진입점은 `.claude/skills/vibecoding-deck/SKILL.md`다.
- 명시 호출은 `/vibecoding-deck`, 일반 강의덱·교육 슬라이드 요청은 진입점의 `description`으로 자동 호출한다.
- 진입점은 규칙을 복제하지 않는 얇은 어댑터다. 호출되면 저장소 루트 `SKILL.md`를 끝까지 읽고, 그 문서가 가리키는 모든 상대 경로를 저장소 루트 기준으로 해석한다.
- 공통 작업 매뉴얼과 PPT 제작 규칙은 각각 `AGENTS.md`와 루트 `SKILL.md`가 정본이다. `.claude/`에는 Claude Code의 탐색·호출 차이만 둔다.
- Windows에서는 `python`을 사용한다. Claude 전용 `ui-ux-pro-max`를 직접 실행할 때는 저장소 루트에서 `python .claude/skills/ui-ux-pro-max/scripts/search.py ...`를 사용한다.
- 팀 워크플로 스킬 3종(/리서치·/콘텐츠·/검토)은 .claude/skills/의 어댑터로 발견되며 명시 호출 전용이다. 정본과 계약은 루트 skills/README.md.

# 세션 시작 필수 읽기 (프로젝트 지도)

새 세션은 작업 전 아래를 순서대로 훑어 프로젝트 전체 맥락을 잡는다. 재탐색 비용을 줄이는 인덱스다(내용은 각 정본이 소유).

1. `AGENTS.md` — 공통 작업 매뉴얼·폴더 구조(①~⑤층)·불변 규칙. (이미 위에서 import)
2. `.agents/agent-memory/vibecoding-deck/MEMORY.md`의 `## 미해결`(현재 상태와 다음 할 일)은 **무조건** 읽는다. 나머지(누적 규칙·색 시스템 정본)는 덱 조립·규칙 변경 작업 시 읽는다.
3. `skills/README.md` — 팀 워크플로 스킬(`/리서치`·`/콘텐츠`·`/검토`·`/하네스`) **호출 시** 계약표·파이프라인 지도·명시 호출 규약을 확인한다.
4. 커리큘럼: `sessions/바이브코딩_커리큘럼_기준안.md`(전 주차 상위 기준) + `sessions/N주차/N주차_강의안설계.md`(주차 상세, 옛 인수인계서 역할) — **해당 주차 파일을 열거나 쓰기 전에, 그 주차 것만** 읽는다.
5. 루트 `SKILL.md` — 덱 조립 규칙(vibecoding-deck). 덱 작업 시.
6. `sessions/README.md` — 세션 폴더 규약(주차별 산출물 위치). **새 주차 폴더를 만들 때** 읽는다.
