# AGENTS.md — vibecoding-deck 공통 작업 매뉴얼

이 폴더는 **`vibecoding-deck` 스킬을 개발·보관**하는 프로젝트다. 루트 `SKILL.md`와 `kit/`·`references/`·`scripts/`가 플랫폼 공통 정본이며, `.agents/skills/vibecoding-deck/`와 `.claude/skills/vibecoding-deck/`는 이 정본을 로드하는 얇은 탐색 어댑터다. Codex는 이 파일을 직접 읽고, Claude Code는 루트 `CLAUDE.md`의 `@AGENTS.md` import로 같은 규칙을 읽는다. 변하는 현재 상태와 다음 할 일은 여기 두지 말고 `.agents/agent-memory/vibecoding-deck/MEMORY.md`의 `## 미해결`에 둔다.

## 구조 (섞지 말 것 · ①②③=스킬 3층, ④=작업물, ⑤=팀 스킬)

- **① 포터블 스킬(루트, 배포 대상)**: `SKILL.md`(진입점) · `kit/` · `references/` · `scripts/` · `입력양식/` · `데모_제작규칙.html` · `outputs/`(레이아웃 아틀라스). 사람용 개요는 `README.md`.
- **② 개발자료 `_dev/`(배포 제외)**: `설계기록/`(빌드·결정 기록 · `탐색-아카이브/` 미채택본). **커리큘럼·콘텐츠 원천은 `sessions/`로 이관**됨 — 상위 기준 `sessions/바이브코딩_커리큘럼_기준안.md` + 주차 상세 `sessions/N주차/N주차_강의안설계.md`(옛 인수인계서 역할). `_dev/강의자료/`는 더 이상 쓰지 않는다.
- **③ 플랫폼 어댑터**: `.agents/skills/vibecoding-deck/`(Codex) · `.claude/skills/vibecoding-deck/`(Claude Code). 공통 규칙을 복제하지 않고 루트 `SKILL.md`만 로드한다. 누적 규칙·버그 정본은 `.agents/agent-memory/vibecoding-deck/MEMORY.md` 하나이며 Claude Code도 이 파일을 읽는다. `ui-ux-pro-max`만 각 플랫폼 탐색 위치에 실행 자원과 함께 둔다.
- **④ 주차별 작업물 `sessions/`(배포 제외)**: `N주차/`에 그 주차의 `초안.md`·`강의덱.html`·`강의덱_발표자노트.html`·`자료/`. 새 주차는 `sessions/_template/` 복사, 규약은 `sessions/README.md`. 1주차 덱만 루트 CSS 상대경로 때문에 예외적으로 루트 `1주차_강의덱.html`을 유지한다.
- **⑤ 팀 워크플로 스킬 `skills/`(배포 제외)**: 강의 제작 팀 역할 스킬 3종(리서치·콘텐츠·검토)의 정본. scripts/·sessions/ 규약에 하드 결합된 이식 불가 자산이라 포터블 스킬 배포 복사에서 제외한다. 등재·계약·호출 규약 정본은 `skills/README.md`.

> git으로 관리한다(2026-07-16 초기 커밋, 브랜치 `main`). 의미 있는 변경은 verify 통과 후 커밋해 복구 지점을 만든다. 설계 탐색 산출물 폐기는 관례대로 `_dev/설계기록/`(탐색-아카이브) 이동을 유지한다. 대규모 정리와 대량 갱신은 먼저 영향 범위를 확인한다.

## 작업 전 필수 읽기

1. `.agents/agent-memory/vibecoding-deck/MEMORY.md` — 누적 규칙, 하드윈 버그, 색 시스템 정본, 그리고 현재 상태·다음 할 일(`## 미해결`). 같은 실수를 반복하지 않도록 반드시 읽는다.
2. 배경이 필요할 때 `_dev/설계기록/구조-및-빌드-기록.md`를 읽는다.
3. 덱 조립·리뷰 요청이면 루트 `SKILL.md`를 적용하고 그 안의 read-path를 순서대로 따른다.

## 플랫폼별 Skill 호출

- **Codex**: `.agents/skills/vibecoding-deck/SKILL.md`가 발견된다. `$vibecoding-deck`으로 명시 호출하거나 PPT·강의덱·HTML 웹덱 제작 요청으로 자동 호출한다.
- **Claude Code**: `.claude/skills/vibecoding-deck/SKILL.md`가 발견된다. `/vibecoding-deck`으로 명시 호출하거나 같은 자연어 요청으로 자동 호출한다.
- 두 어댑터는 반드시 루트 `SKILL.md`를 완전히 읽고, 그 안의 상대 경로를 저장소 루트 기준으로 해석한다. 어댑터에 디자인 규칙이나 워크플로를 복제하지 않는다.
- 팀 워크플로 스킬 3종(`/리서치`·`/콘텐츠`·`/검토`)은 **명시 호출 전용**이다(자동 발동 없음 — "명시 호출"의 정의는 `skills/README.md`가 정본). vibecoding-deck만 기존대로 자동 발동을 유지한다. 파이프라인 순서: `/리서치` → `/콘텐츠` → `/vibecoding-deck` → `/검토`(횡단).

## 스킬의 역할

채워진 콘텐츠 초안(교시별 표·본문·강사 멘트)을 1280×720 HTML 웹덱으로 조립한다. 대상은 40~50대 초보자다. 정보 모양을 먼저 판단해 레이아웃과 차트를 고르고, 좌우분할 한 구도로 쏠리지 않게 한다. 이미지보다 코드 시각화를 우선한다. 초안의 제목과 본문을 존중하며 무단 재작성·분할하지 않는다. 강사 멘트가 있으면 발표자 노트 HTML도 별도로 만든다.

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
```

- 브라우저는 `deck.css`를 캐시하므로 변경 확인 때 링크의 `href`에 `?v=`를 붙인다.
- `file://`로 검증하지 말고 로컬 HTTP 서버를 사용한다.
- 스크린샷보다 JS 측정(`scrollHeight`, computed style)을 우선한다.
- `.hint-reveal`은 닫힘과 강제 열림 상태를 모두 검사한다.
- 카탈로그나 `SKILL.md`를 바꾸면 `evals/evals.json`과 `evals/trigger-eval.json`으로 회귀를 확인한다.

## 공통 작업 방식

- 텍스트와 파일 탐색은 `rg`/`rg --files`를 우선한다.
- 기존 사용자 변경을 보존하고, 무관한 파일을 되돌리거나 정리하지 않는다.
- 구현 요청은 수정 후 정적 검증과 가능한 범위의 브라우저 측정을 수행한다.
- **하네스(실질 작업의 기본 방식)**: 다파일·독립 구간·대규모 작업(스킬·계약 재설계, 40장+ 덱, 여러 파일에 걸친 규칙 변경)은 기본으로 하네스로 수행한다. **단일 파일·사소한 편집·조회는 solo로 한다** — 하네스를 걸지 않는다. 상세 정본은 `skills/하네스/SKILL.md`(명시 호출 `/하네스`).
  - ⚠️ **명분(오해 금지)**: 하네스는 **품질·컨텍스트 보존** 도구다. **비용 절감 도구가 아니다** — 워커는 컨텍스트를 공유하지 않아 같은 파일을 각자 다시 읽고 총 토큰이 몇 배로 는다. 실측(2026-07-18 파이프라인 재설계): Opus 캐시읽기 55.2M·비용 72%가 **메인 창 재독**에서 발생했고 Sonnet 워커는 28%뿐이었다. **비용을 아끼려고 하네스를 걸지 않는다.**
  - **역할(하네스가 걸린 동안에만 적용)**: 메인(Opus)=전역 결정표 확정·분해·위임·**게이트(반려/통과)**·통합·회귀. **파일을 직접 편집하지 않는다.** 워커(Sonnet)=모든 실제 편집.
  - **게이트는 기계 신호 우선**: `verify_*.py` 종료코드·요약 1줄로 판정한다. 산출물 전문 재독은 **계약·불변 규칙이 걸린 경우에만** — 재독이 메인 창을 키워 비용을 만든다.
  - **대량 팬아웃은 조건부**: **토큰이 무겁고 판단이 가벼운** 일(대량 탐색·기계적 변환)에만 워커를 늘린다. 판단이 무겁고 토큰이 가벼운 일(문서 정밀 편집 등)은 **solo가 정답**이다 — 오버헤드가 이득을 넘는다.
  - **Opus 리뷰어(architect·critic)는 기본 미사용**: 되돌리기 어렵거나 계약·스키마를 바꾸는 작업에만 1회.
  - **워커 규율**: 워커마다 편집 허용 파일 목록(allowlist)을 준다. 같은 파일은 **단일 라이터로 직렬화**한다. wave마다 `git status --short`로 변경 귀속을 확인한다(스코프 밖 삭제 사고 예방). 워커는 자기 소관 밖 변경을 되돌리지 않고 보고한다.
  - **메인 창 규율(토큰 실절감은 여기서 난다)**: 메인은 큰 파일을 직접 읽지 않는다 · 워커 보고는 **10줄 이내**로 지시한다 · 완료 통지마다 상태 메시지를 쓰지 않는다 · 컨텍스트가 150k를 넘으면 세션을 분리한다(인계는 MEMORY).
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
