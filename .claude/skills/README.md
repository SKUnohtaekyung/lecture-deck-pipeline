# Claude Code 프로젝트 스킬

Claude Code는 `.claude/skills/<name>/SKILL.md`를 프로젝트 스킬로 발견한다. 명시 호출은 `/<name>`이고, 일반 요청은 `description`이 구체적으로 일치할 때 자동 호출된다. 새 세션에서 탐색·호출을 확인한다.

## create-slides 구성

```text
.claude/skills/create-slides/SKILL.md  # Claude Code 탐색용 얇은 어댑터
../../../SKILL.md                        # PPT 제작 규칙의 공통 정본
```

어댑터는 루트 `SKILL.md`와 같은 `name`·`description`만 가지고, 호출 후 공통 정본을 끝까지 읽도록 지시한다. PPT 조건·디자인 규칙·참조 목록을 어댑터에 복제하지 않는다. 공통 정본에 적힌 `kit/`, `references/`, `scripts/`, `입력양식/`, `evals/` 상대 경로는 모두 저장소 루트 기준으로 해석한다.

루트 전체를 `.claude/skills/create-slides/` 아래에 다시 복사하거나, 저장소 루트를 그 하위 경로로 가리키는 junction·심볼릭 링크를 만들지 않는다. 이 저장소에서는 어댑터가 공통 정본을 직접 읽으므로 복사와 링크가 필요 없다.

## Windows 실행

저장소 루트에서 `python`을 사용한다.

```powershell
python scripts/verify_deck.py <덱>.html --parts N
python scripts/inline_deck.py <덱>.html --offline
python -m http.server
python .claude/skills/ui-ux-pro-max/scripts/search.py ...
```

## 검증 체크리스트

- 폴더명과 frontmatter `name`이 `create-slides`로 일치하는가
- 어댑터 `description`이 루트 `SKILL.md`와 동일한가
- `../../../SKILL.md`가 실제 루트 공통 정본을 가리키는가
- `/create-slides` 명시 호출과 일반 강의덱 요청의 자동 호출이 새 세션에서 동작하는가
- 공통 문서의 상대 경로가 어댑터 폴더가 아니라 저장소 루트에서 해석되는가

## 팀 워크플로 스킬

리서치·검토 어댑터의 정본은 루트 `skills/<이름>/SKILL.md` — 등재·계약·호출 규약은 `skills/README.md` 참조(여기에 복제하지 않는다). 횡단 오케스트레이션 프로토콜 `하네스`(파이프라인 역할 아님)도 같은 방식의 어댑터를 `.claude/skills/하네스/`에 둔다.
