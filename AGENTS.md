# AGENTS.md — vibecoding-deck 공통 작업 매뉴얼

이 폴더는 **`vibecoding-deck` 스킬을 개발·보관**하는 프로젝트다. 루트 `SKILL.md`와 `kit/`·`references/`·`scripts/`가 플랫폼 공통 정본이며, `.agents/skills/vibecoding-deck/`와 `.claude/skills/vibecoding-deck/`는 이 정본을 로드하는 얇은 탐색 어댑터다. Codex는 이 파일을 직접 읽고, Claude Code는 루트 `CLAUDE.md`의 `@AGENTS.md` import로 같은 규칙을 읽는다. 변하는 현재 상태와 다음 할 일은 여기 두지 말고 `.agents/agent-memory/vibecoding-deck/MEMORY.md`의 `## 미해결`에 둔다. 이 파일은 작업 기록이나 변경 로그가 아니다: 새 규칙·반복 버그·인수인계 상태 중 **계속 유효한 것만** 남기며, 관련 작업을 마칠 때 에이전트가 해결 여부를 판정해 해결된 항목은 반드시 삭제한다.

## 구조 (섞지 말 것 · ①②③=스킬 3층, ④=작업물, ⑤=팀 스킬)

- **① 포터블 스킬(루트, 배포 대상)**: `SKILL.md`(진입점) · `kit/` · `references/` · `scripts/` · `입력양식/` · `데모_제작규칙.html` · `outputs/`(레이아웃 아틀라스). 사람용 개요는 `README.md`.
- **② 개발자료 `_dev/`(배포 제외)**: `설계기록/`(빌드·결정 기록 · `탐색-아카이브/` 미채택본). **커리큘럼·콘텐츠 원천은 `sessions/`로 이관**됨 — 상위 기준 `sessions/바이브코딩_커리큘럼_기준안.md` + 주차 상세 `sessions/N주차/N주차_강의안설계.md`(옛 인수인계서 역할). `_dev/강의자료/`는 더 이상 쓰지 않는다.
- **③ 플랫폼 어댑터**: `.agents/skills/vibecoding-deck/`(Codex) · `.claude/skills/vibecoding-deck/`(Claude Code). 공통 규칙을 복제하지 않고 루트 `SKILL.md`만 로드한다. 누적 규칙·버그 정본은 `.agents/agent-memory/vibecoding-deck/MEMORY.md` 하나이며 Claude Code도 이 파일을 읽는다. `ui-ux-pro-max`만 각 플랫폼 탐색 위치에 실행 자원과 함께 둔다. `/리서치` 워커의 실행 통제(`Explore` + `sonnet` + 도구 허용목록 + 사후 감사)는 플랫폼마다 수단이 달라 `.claude/skills/리서치/SKILL.md`가 Claude 전용으로 규정하며, 조사 규칙 정본은 `skills/리서치/SKILL.md` 그대로다.
- **④ 주차별 작업물 `sessions/`(배포 제외)**: `N주차/`에 그 주차의 `초안.md`·`강의덱.html`·`강의덱_발표자노트.html`·`자료/`. 새 주차는 `sessions/_template/` 복사, 규약은 `sessions/README.md`. 1주차 덱·초안은 사용자 판정으로 폐기됐고(`sessions/README.md` "1주차 (예외)" 참고), 1주차는 자료만 남아 있다.
- **⑤ 팀 워크플로 스킬 `skills/`(배포 제외)**: 강의 제작 팀 역할 스킬 3종(리서치·콘텐츠·검토) + 횡단 오케스트레이션 프로토콜 하네스의 정본. scripts/·sessions/ 규약에 하드 결합된 이식 불가 자산이라 포터블 스킬 배포 복사에서 제외한다. 등재·계약·호출 규약 정본은 `skills/README.md`.

> git으로 관리한다(2026-07-16 초기 커밋, 브랜치 `main`). 의미 있는 변경은 verify 통과 후 커밋해 복구 지점을 만든다. 설계 탐색 산출물 폐기는 관례대로 `_dev/설계기록/`(탐색-아카이브) 이동을 유지한다. 대규모 정리와 대량 갱신은 먼저 영향 범위를 확인한다.

## 작업 전 필수 읽기

1. `.agents/agent-memory/vibecoding-deck/MEMORY.md`의 `## 미해결`(현재 상태·다음 할 일)은 무조건 읽는다. 나머지(누적 규칙·하드윈 버그·색 시스템 정본)는 덱 조립·규칙 변경 작업 시 읽는다. 관련 작업을 끝내기 전에는 같은 파일을 다시 확인해, 해결된 미해결 항목과 더는 유효하지 않은 규칙·버그·인수인계 내용을 **반드시 삭제**하고 계속 유효한 내용만 남긴다.
2. 배경이 필요할 때 `_dev/설계기록/구조-및-빌드-기록.md`를 읽는다.
3. `skills/README.md` — 팀 워크플로 스킬(`$리서치`·`$콘텐츠`·`$검토`·`$하네스`) 호출 시 계약표·파이프라인 지도·명시 호출 규약을 확인한다.
4. 커리큘럼(`sessions/바이브코딩_커리큘럼_기준안.md` + `sessions/N주차/N주차_강의안설계.md`) — 해당 주차 파일을 열거나 쓰기 전에, 그 주차 것만 읽는다.
5. 덱 조립·리뷰 요청이면 루트 `SKILL.md`를 적용하고 그 안의 read-path를 순서대로 따른다.
6. `sessions/README.md` — 새 주차 폴더를 만들 때 읽는다.

## 플랫폼별 Skill 호출

- **Codex**: `.agents/skills/vibecoding-deck/SKILL.md`가 발견된다. `$vibecoding-deck`으로 명시 호출하거나 PPT·강의덱·HTML 웹덱 제작 요청으로 자동 호출한다.
- **Claude Code**: `.claude/skills/vibecoding-deck/SKILL.md`가 발견된다. `/vibecoding-deck`으로 명시 호출하거나 같은 자연어 요청으로 자동 호출한다.
- 두 어댑터는 반드시 루트 `SKILL.md`를 완전히 읽고, 그 안의 상대 경로를 저장소 루트 기준으로 해석한다. 어댑터에 디자인 규칙이나 워크플로를 복제하지 않는다.
- 팀 워크플로 스킬 3종(`/리서치`·`/콘텐츠`·`/검토`)은 **명시 호출 전용**이다(자동 발동 없음 — "명시 호출"의 정의는 `skills/README.md`가 정본). vibecoding-deck만 기존대로 자동 발동을 유지한다. 파이프라인 순서: `/리서치` → `/콘텐츠` → `/vibecoding-deck` → `/검토`(횡단).

## 스킬의 역할

채워진 콘텐츠 초안(교시별 표·본문·강사 멘트)을 1280×720 HTML 웹덱으로 조립한다. 대상은 코딩 경험이 없는 입문자 중심의 혼합군이다. 정보 모양을 먼저 판단해 레이아웃과 차트를 고르고, 좌우분할 한 구도로 쏠리지 않게 한다. 이미지보다 코드 시각화를 우선한다. 초안의 제목과 본문을 존중하며 무단 재작성·분할하지 않는다. 강사 멘트가 있으면 발표자 노트 HTML도 별도로 만든다.

## 불변 규칙

- 색은 토큰만 사용한다. raw `#hex`, navy, 그라데이션을 쓰지 않는다. 흰색은 `var(--white)`를 쓴다.
- 민트·코랄 fill 위에 흰 글자를 쓰지 않는다. 각각 `--on-mint`, `--on-coral`을 쓴다.
- 민트 fill 번호 배지는 `.num-circle`, `.work-step .n`, `.pd-dot.is-active` 세 종류만 허용한다. 다른 다이어그램·플로우 노드는 블루다.
- 카드/박스 표면은 흰색-온-흰색 금지: 의미 틴트 fill(블루 기본·민트=행동·코랄=주의) + 같은 계열 보더, 또는 흰 fill + 유색 보더(`--blue-line-strong`/`--mint-line`/`--coral-line`). 흰 fill + `--line` 근백색 보더 단독 조합은 verify FAIL. `--line`은 내부 구분선 전용.
- 원형 배지+텍스트 행(`.work-step`·`.agenda-item`)은 텍스트를 배지 기준 수직 중앙(`align-items:center`)에 둔다.
- 조립 전에 `정보 모양 분류 → 역인덱스 → 레이아웃과 element를 별도 선택` 순서를 따른다.
- 직전 슬라이드와 같은 구도를 피하고 split 계열을 희소하게 쓴다.
- 상세·최신 규칙은 `.agents/agent-memory/vibecoding-deck/MEMORY.md`를 정본으로 삼는다.

## 실행과 검증

```powershell
python scripts/verify_deck.py <덱>.html --parts N
python -m http.server
python scripts/inline_deck.py <덱>.html --offline
# Codex
python .agents/skills/ui-ux-pro-max/scripts/search.py ...
# Claude Code
python .claude/skills/ui-ux-pro-max/scripts/search.py ...
python scripts/verify_skill_setup.py
python scripts/verify_kit.py
python -m unittest tests.test_deck_pipeline tests.test_image_pipeline
# 파이프라인 문서 게이트(리서치·콘텐츠 산출물)
python scripts/verify_session_docs.py <주차> --target 자료   # 기본 5파일 스키마·출처ID·[C-슬러그] 해소
python scripts/verify_research_chunks.py <주차>              # 개념KB 청크 깊이·G8 관점·인덱스 일치
python scripts/analyze_agent_usage.py --tool-audit --session <세션ID>  # 리서치 워커 도구·모델 감사(0 통과 / 3 위반)
```

- 브라우저는 `deck.css`를 캐시하므로 변경 확인 때 링크의 `href`에 `?v=`를 붙인다.
- `file://`로 검증하지 말고 로컬 HTTP 서버를 사용한다.
- 스크린샷보다 JS 측정(`scrollHeight`, computed style)을 우선한다.
- `.hint-reveal`은 닫힘과 강제 열림 상태를 모두 검사한다.
- 카탈로그나 `SKILL.md`를 바꾸면 `evals/evals.json`과 `evals/trigger-eval.json`으로 회귀를 확인한다.
- 위 unittest는 `fontTools`·`Pillow`가 설치된 인터프리터로 실행한다(의존 정본 `requirements-dev.txt`). Windows 로컬에서는 보통 `.venv\Scripts\python.exe`.

## 공통 작업 방식

- 텍스트와 파일 탐색은 `rg`/`rg --files`를 우선한다.
- 기존 사용자 변경을 보존하고, 무관한 파일을 되돌리거나 정리하지 않는다.
- 구현 요청은 수정 후 정적 검증과 가능한 범위의 브라우저 측정을 수행한다.
- **하네스(실질 작업의 기본 방식)**: 다파일·독립 구간·대규모 작업(스킬·계약 재설계, 40장+ 덱, 여러 파일에 걸친 규칙 변경)은 기본으로 하네스로 수행한다. **단일 파일·사소한 편집·조회는 solo로 한다** — 하네스를 걸지 않는다.
  - ⚠️ **비용 절감 도구가 아니다** — 품질·컨텍스트 보존 도구다. 워커는 메인과 컨텍스트를 공유하지 않아 같은 파일을 각자 다시 읽고 총 토큰이 늘 수 있다(실측 근거는 정본 §0).
  - 명분·스케일 사다리·역할 계약·게이트 기준·워커 규율·안티패턴 상세 정본: `skills/하네스/SKILL.md`(명시 호출 `/하네스`·`$하네스`).
- 웹 리서치가 필요한 사실은 검색 후 원문 출처를 확인한다. 외부 쓰기나 게시·전송은 사용자 요청 범위를 넘겨 실행하지 않는다.

## 판단 기준과 파일 지도

- 판단축: `kit/guide/정보모양-taxonomy.md`
- 카탈로그 규칙: `kit/guide/카탈로그-규격.md`
- 토큰·계산식: `kit/guide/토큰-치트시트.md`
- 색·폼 정본: `_dev/설계기록/색시스템-v2-명세.md`
- 레이아웃: `kit/layouts/`(50) + `by-shape.md` + `catalog.html`
- 차트·다이어그램 element: `kit/charts/`(23) + `by-shape.md` + `catalog.html`
- 코드 코어: `kit/styles/patterns.css`, `kit/styles/deck.css`
- 스타터: `kit/starter/deck-template.html`, `kit/starter/presenter-notes-template.html`
