# Agent System Audit — 독립 검증과 개편 명세

> 작성 2026-10-08 · 메인 판단 Opus 5.5 · 위임 3건(Sonnet, 읽기 전용): `MEMORY.md` 소절 분해, Anthropic 문서 재확인, OpenAI·Google 문서 재확인
> 검증 대상: `plans/agent-system-audit/REPORT.md`(2026-10-07, 이하 「이전 보고서」). 이전 보고서는 근거가 아니라 검증 대상으로만 읽었다.
> 이번 단계에서 만든 파일: 이 문서와 `tmp/audit-1008/`(재측정 스크립트·원자료)뿐이다. 지침·스킬·훅·에이전트 정의·코드·FRAME 산출물은 손대지 않았고, 커밋·stash·checkout·정리도 하지 않았다.
> 판정 값: `VERIFIED` / `PARTIALLY VERIFIED` / `CONTRADICTED` / `NOT VERIFIABLE` / `NOT YET CHECKED`. 추론은 `[INFERENCE]`로 표시한다.
> 세션 로그 수치는 이전 워커의 스크립트를 쓰지 않고 새로 쓴 `tmp/audit-1008/logs/measure.py`로 다시 잰 값이다.

작업 시작 시 Git 상태(`tmp/audit-1008/git_baseline.txt`): 브랜치 `main`, HEAD `a979b423`, staged 0, 내용이 다른 추적 파일 100개(+5,998/−1,804), 미추적 11개, `git status` 156줄(그중 45줄은 내용 차이가 없는 `M`), stash 1건(`feat/ac3-w2-prd-reorder`에서 만든 것).

---

## 1. Executive Verdict

**확인된 것**
- `MEMORY.md`의 `## 미해결` 절은 149~696행, 101,592바이트다. `AGENTS.md:46`이 이 절을 "무조건" 읽으라고 적고 있다.
- 세션 시작 기준선은 74,044~77,683토큰이다(저장소 세션 11개).
- FRAME 세션 3개: Skill 호출 0, 과목 지침·사전 점검 훅 주입 0, Agent 호출 6(전부 `frame-builder`, 첫 세션).
- AC3 세션군: Agent 호출 122, 훅 주입 222(과목 지침 213 + 사전 점검 9).
- 9/8 이후 `/리서치`·`/검토`·`/하네스`의 Skill 도구 호출은 0건이다.
- FRAME의 러너·검사기 판정은 2026-10-06 사용자 결정으로 보류 상태다(`plans/FRAME-길이별-조립/재개_인계.md:46`).
- FRAME 렌더 감사 증거는 111장·뷰포트 423×308에서 측정된 것이고, `조립_보고.md`는 9/18자다.
- FRAME 세션은 전부 Opus 5.5, AC3 Claude 세션은 Opus 5와 Fable 5.1이다.
- 공식 문서 인용 46건 중 원문과 어긋난 것은 0건이다.

**틀린 것**
- "`미해결` 약 49k 토큰이 매 작업에 든다" — 메인 세션 13개 중 `MEMORY.md`를 통째로 읽은 세션은 0개다. 실제 유입은 세션당 0~13,150자였다. 49k는 "지침을 글자 그대로 따르면"이라는 가정 값이었다.
- "같은 파일 3회 이상 재독 143건은 낭비" — 건수는 맞지만 AC3 워커 103건 중 범위 지정 없는 전체 재독은 0건이다. 큰 파일을 구간별로 읽은 것이다.
- "R-QC-08이 SVG를 세지 않는 것은 검사기 결함" — `scripts/verify_deck_quality.py:92-94`가 SVG 미집계를 의도된 정의로 적고 있다. `viz-*` 태그를 붙여야 세는 규약이고 FRAME 덱은 태그가 없다.
- "FRAME은 시각 설명력에서 뚜렷이 앞선다" — 근거였던 SVG 개수는 대부분 작은 SVG다. 도형 6개 이상인 SVG만 세면 FRAME은 다른 덱과 같은 범위다.

**부분적으로 맞는 것**
- "FRAME은 시스템을 대부분 우회했다" — 지시 층(스킬·훅 주입·검토 루프)은 쓰지 않았지만 저장소 스크립트는 썼다.
- "사람 턴당 입력 FRAME 3.5M 대 AC3 18.1M" — 산술은 맞다. AC3 값의 75%가 포크 세션 하나에서 나온다.
- "D1~D45는 사용자 잠금 결정" — 문서 자체가 3개를 "메인 판단", 1개를 위임 후 메인 확정으로 적고 있고, 26개는 행별 출처 표기가 없다.
- "8/17 이후 `MEMORY.md`는 줄지 않았다" — 순증은 맞다(+441/−104줄). 소절 순삭제는 1건 있었다.

**판단 불가**
- FRAME 결과물이 이전 결과물보다 품질이 높은가.
- 품질 차이가 있다면 그 원인.
- 9/13~9/30 구간(바이브코딩_온라인, FRAME 47장판, FRAME 계획 수립)의 작업 방식.

이전 보고서의 P0 세 건은 이 검증으로 근거가 바뀌었다. `MEMORY.md` 분리는 토큰 절감이 아니라 상태 정확성 문제로 다시 정의했고(§12), R-QC-08 수정안은 폐기했다(§9).

---

## 2. Evidence Verification Matrix

### 2-1. 지정 검증 항목 C1~C18

| ID | 기존 주장 | 유형 | 기존 근거 | 원자료 재검증 | 판정 | 비고 |
|---|---|---|---|---|---|---|
| C1 | `MEMORY.md` 133KB, `미해결` 약 101.6KB | FILE | 파일 크기 | 149~696행, 101,592B. 그 앞 30,809B | VERIFIED | 작업 트리 기준(미커밋 수정 포함) |
| C2 | `미해결`의 상당수가 완료 항목 | FILE | 제목 표기 17개 | 완료·종결 표기 소절 18개 중 본문에 열린 과업이 남은 것 12개, 낡은 "대기" 서술 2개, 남은 일이 없는 것 4개. 과업 서술 72건 중 STILL OPEN 27, DONE 15, SUPERSEDED 9, 미대조 21 | PARTIALLY VERIFIED | "제목이 완료"와 "끝난 일"은 다르다. 워커 분해, 표본 3건 대조 |
| C3 | `AGENTS.md`가 그 절을 항상 읽게 한다 | FILE | `AGENTS.md:46` | 문장은 있다. 그러나 실제 세션은 통째로 읽지 않았다(전체 Read 0회) | PARTIALLY VERIFIED | 지시는 있고 준수는 없다 |
| C4 | 기준선 74k~77.7k | LOG | 워커 집계 | 74,044~77,683(11개). 86,635(Sonnet 5 세션), 89,578(감사 세션) | VERIFIED | |
| C5 | 저장소 지침 약 9.5k 토큰 | INFERENCE | 바이트 × 0.48 | 세션 첨부 기록: `CLAUDE.md` 1,310자 + `AGENTS.md` 9,875자. 한글 지침 Read 6건의 실측 비율 0.85~0.97토큰/자를 곱하면 9.5k~10.9k | PARTIALLY VERIFIED | 추정치. 직접 측정 수단 없음 |
| C6 | FRAME Skill 호출 0 | LOG | 워커 | 0b1569d9·c93120d9·b6e30e2b 메인 0, 서브에이전트 0 | VERIFIED | |
| C7 | FRAME 훅 주입 0 | LOG | 워커 | 과목 지침·사전 점검 주입 0. 그 밖의 주입 8건은 데스크톱 앱 안내문 | VERIFIED | 훅 프로세스 자체는 실행됐다(출력 없음) |
| C8 | FRAME 서브에이전트 호출 | LOG | 6건 | 6건(`frame-builder`, 0b1569d9). 서브에이전트 API 호출 288회, 입력 41.8M | VERIFIED | 9/30 세션 로그 없음 → 그 구간은 NOT VERIFIABLE |
| C9 | AC3 Agent 122 / 훅 222 | LOG | 워커 | Agent 62+37+8+5+10 = 122. 훅 213+9 = 222 | VERIFIED | 2f7e8a36의 221콜·훅 98건은 671720eb에 복제돼 있어 한쪽만 셈 |
| C10 | 3회 이상 재독 143건 | LOG | 워커 | 건수 143(감사 세션 제외) 일치. 범위 지정 없는 전체 Read가 3회 이상인 것: AC3 워커 0, FRAME `frame-builder` 11, 메인 0 | 건수 VERIFIED · 해석 CONTRADICTED | "낭비"의 근거가 못 된다 |
| C11 | 턴당 입력 3.5M 대 18.1M, 같은 기준인가 | LOG | 워커 | 같은 기준(호출별 입력 합 ÷ 사람 턴). FRAME 175.2M/50. AC3 976.3M/53. AC3 중 728M이 2f7e8a36+671720eb(Fable 5.1, 계획·인프라 작업 포함). 이를 빼면 247.7M/30 = 8.3M | PARTIALLY VERIFIED | 비율은 2.4배~5.2배. 이 지표는 세션 길이에 제곱으로 민감하다 |
| C12 | FRAME 시각 지표 재현 | OUTPUT | SVG 2.13/장, 시각 요소 없는 장 18.9% | 로고 포함 SVG 3.07/장(타 덱 0.93~1.93)으로 개수는 재현. 도형 6개 이상 SVG는 0.30/장·24% 장(AC3-3 0.39·27%, 바이브코딩-3 0.35·30%). SVG6·img·표·pre·canvas 중 하나라도 있는 장 37%(타 덱 21~43%) | 수치 VERIFIED · 해석 NOT VERIFIABLE | 정의에 따라 순위가 바뀐다. CSS로 그린 화면 모형은 어느 정의에도 안 잡힌다 |
| C13 | `verify_deck` FAIL 4는 품질 실패인가 | OUTPUT | 워커 실행 | 재실행(커밋본): 이미지 계약(asset-slot 밖 img), 같은 구도 7연속, raw hex 149, gradient 10. 구도 판정은 슬라이드 대부분을 `other`로 분류한 결과다. hex·gradient는 실제 규칙 위반이다 | PARTIALLY VERIFIED | 규약 위반 2, 분류기 어휘 문제 1, 계약 규약 1. 렌더 결함의 증거는 아니다 |
| C14 | `PLAN.md`가 공통 시스템을 대체 | FILE·LOG | 문서 구조 | PLAN §10은 하네스 §3·§4·§7·§8을 인용하고 create-slides 경로(집필노트, G1/G2)를 쓴다. 대체한 것은 `/리서치`(D14)와 `/검토`(frame-reviewer)다. FRAME 세션의 `references/phases` Read 1회, `AGENTS.md` Read 1회 | PARTIALLY VERIFIED | "대체"가 아니라 "과제 정본 + 공통 스크립트 사용" |
| C15 | D1~D45는 사용자 결정인가 | FILE | PLAN §1 제목 | 행별 표기: 사용자 명시 8(D22·31·32·33·34·37·38·39) + PROGRESS의 D44·D45. 메인 판단 3(D29·30·35). 위임 후 메인 확정 1(D40). 표기 없음 26(§1 머리말 "2026-09-30 대화"에 의존). D41~D43 출처 표기 없음. D36 없음 | PARTIALLY VERIFIED | 9/30 대화 로그가 없어 26개는 NOT VERIFIABLE |
| C16 | 조립 99회·스크린샷 31회의 뜻 | LOG | 정규식 묶음 | Bash 명령 속 스크립트명 집계: `assemble_deck.py` 21, `build_notes.py` 32, `inject_presenter.py` 12, `build_parts.py` 9, `inline_deck.py` 9, `build_release.py` 6, `build_ex5.py` 14. 스크린샷은 `shoot_ids.py` 16 + `sheet.py` 15 | PARTIALLY VERIFIED | 덱 조립 자체는 21회. 99는 여러 빌드 스크립트의 합 |
| C17 | "시스템을 우회했다" | LOG | Skill 0·훅 0 | 쓰지 않은 것: Skill, 훅 주입, 검토 루프, shard 직접 Edit(0건). 쓴 것: `assemble_deck` 21, `verify_deck` 10, `verify_notes` 9, `verify_presenter_deck` 11, `run_deck_checks` 7, `build_release` 6, `audit_context_budget` 4 | PARTIALLY VERIFIED | 지시 층은 비켜 갔고 스크립트 층은 썼다 |
| C18 | 9/8 이후 하네스·리서치·검토 미호출 | LOG | Skill 4건 | Skill 도구: create-slides 2, explain-usage 1, (서브) workflow-authoring 1. 슬래시 명령은 `/model` 9, `/compact` 1뿐. 하네스 문서 Read는 AC3 메인 1회, AC3 워커가 지침 분석용으로 11회 | VERIFIED(호출 기준) | 하네스는 호출 없이 문서 인용으로 쓰인다. "미호출"이 "미사용"은 아니다 |

### 2-2. 이전 보고서의 그 밖의 핵심 주장

| ID | 기존 주장 | 유형 | 재검증 | 판정 |
|---|---|---|---|---|
| E1 | "삭제 규칙이 집행된 적 없다" | GIT | 8/8 이후 37개 커밋에서 소절 제목 삭제 24줄 중 23줄은 제목 갱신, 순삭제는 `e772c8b` 1건. `###` 소절 6개 → 32개 | PARTIALLY VERIFIED |
| E2 | 스킬 3벌, `ui-ux-pro-max` 데이터 2벌 동일 | FILE | md5 대조: 33개 중 31개 동일. `SKILL.md`·`search.py`만 다르고 `.agents` 쪽에 `openai.yaml` 추가. 각 1.65MB | VERIFIED |
| E3 | 관측 훅(`generated-guard`·`tmp-guard`)은 출력 0건 | LOG | 세션 로그에는 0건. `tmp/guard-observations.jsonl`에는 346줄: 생성물 직접 편집 would-block 66(전부 AC3), 저장소 밖 쓰기 would-block 71 | CONTRADICTED(작동했고 장부에 썼다) |
| E4 | Codex 훅에는 경로 키가 없다 | OFFICIAL-DOC | 원문 `PreToolUse` 입력 표 확인 | VERIFIED |
| E5 | 문서 간 수치 충돌(회귀 10 대 12모듈) | FILE | `tests/test_*.py` 12개. `AGENTS.md:111` "10모듈" | VERIFIED |
| E6 | 차트 21 대 23, kit/guide 5 대 8 등 나머지 충돌 5건 | FILE | 다시 세지 않았다 | NOT YET CHECKED |
| E7 | `AGENTS.md` 블록 분류 31.5/23.8/12.0/26.9/5.8% | FILE | 워커의 정독 판단. 재분류하지 않았다 | NOT YET CHECKED |
| E8 | 사람 교정 비율 FRAME 29% 대 AC3 14% | LOG | 워커 한 명의 수동 분류. 재분류하지 않았다 | NOT YET CHECKED |
| E9 | shard 삭제/추가 비율 FRAME 0.55 | GIT | 다시 계산하지 않았다 | NOT YET CHECKED |
| E10 | 훅 `course`·`checklist`에 중복 억제 없음 | FILE·LOG | 671720eb 한 세션에서 과목 지침 187회 주입(63,206자). 코드 정독은 다시 하지 않았다 | 로그로 VERIFIED |
| E11 | 메인 창이 크다(중앙값 162k~580k) | LOG | 호출당 평균: FRAME 197k·250k·357k, AC3 163k~514k | VERIFIED(평균 기준) |
| E12 | 기준선 중 약 65k는 저장소 밖 | LOG | §4-2 참조. 스킬 목록 51개 중 저장소 스킬은 5개·2,081자 | PARTIALLY VERIFIED |
| E13 | pre-commit 게이트는 우회 불가능한 층 | LOG | 로그에 R-QC-14 CSS lint로 커밋이 막힌 기록. `core.hooksPath=.githooks` | VERIFIED(작동 사례 있음) |
| E14 | 작업별 의무 읽기 58k~185k | INFERENCE | 지침을 전부 따른다는 가정의 계산이다. 실제 세션은 그렇게 읽지 않았다(C3) | 가정 값. 실측 아님 |

---

## 3. Unresolved Questions — 이전 보고서 §18의 10건

| # | 미확인 항목 | 처리 | 결과 |
|---|---|---|---|
| 1 | FRAME 품질에 대한 모델 기여분 | D | NOT VERIFIABLE. §6·§14-4 참조 |
| 2 | 9/30 FRAME 세션 로그 | A | `~/.claude/projects/` 전 폴더를 9/17~10/1 구간으로 훑었다. FRAME 경로가 나오는 파일 0개. 이 PC에는 9/13~9/28의 이 저장소 Claude 세션도 없다. NOT VERIFIABLE. 필요한 것: 그 작업을 한 PC의 세션 로그 |
| 3 | 기준선 약 65k의 구성 | A | PARTIALLY VERIFIED. 세션 시작 첨부 기록으로 문자 수는 나온다(§4-2). 도구 스키마 전문은 로그에 없다. 필요한 것: 대화형 터미널의 `/context` 출력 |
| 4 | 7~8월 작업 방식 | A | PARTIALLY VERIFIED. 총량은 쟀다: 세션 58개, 사람 턴 434, Agent 219, 과목 훅 주입 294, 사전 점검 주입 21, Skill 호출 16. 모델은 Opus 4.8·Opus 5·Fable 5·Sonnet 5가 섞였다. 프롬프트 유형 분류는 NOT YET CHECKED |
| 5 | 사용자가 느낀 "품질"의 축 | D | NOT VERIFIABLE. 필요한 것: 사용자가 좋았다고 보는 장 번호와 이유 |
| 6 | 덱의 사실 오류 여부 | D | NOT VERIFIABLE. 사실 검증은 이 감사 범위 밖이다 |
| 7 | 관측 훅이 조용했나, 기록이 안 됐나 | A | VERIFIED. 표준 출력이 아니라 `tmp/guard-observations.jsonl`에 기록한다(E3) |
| 8 | `ui-ux-pro-max`·`/리서치`·`/검토`의 7~8월 실적 | A | VERIFIED. Skill 호출: 7월 create-slides 3 + vibecoding-deck 3, 리서치 2(+서브 2), 하네스 2, ui-ux-pro-max 1. 8월 하네스 2, create-slides 1. 검토 0. 리서치 산출물은 바이브코딩 1~3주차에 존재(7/29·8/8 커밋). 이름에 "검토"가 든 보고서 파일은 저장소에 없다 |
| 9 | 하위 디렉터리 `AGENTS.md` 지연 로드 | C | VERIFIED(문서). Claude Code는 그 폴더의 파일을 Read할 때만, 그 폴더에 `CLAUDE.md`류가 없을 때만 읽는다. Write·Edit로는 로드되지 않는다 |
| 10 | Codex 세션 중 이 저장소 분량 | A | PARTIALLY VERIFIED. 657개 중 187개(1,353MB)가 template 경로다. `Desktop\template` 176개(7/14~9/7), `Desktop\Project\template` 9개(9/8~9/18: AC3 7개, 바이브코딩_온라인 2개), FRAME 실습1 폴더 1개(10/2). 내용 분석은 NOT YET CHECKED |

---

## 4. Repository Context Architecture — Current

### 4-1. 층별 실제 동작

| 층 | 파일 | 지침상 동작 | 실측 동작 |
|---|---|---|---|
| 상시 | `CLAUDE.md` → `@AGENTS.md` | 매 세션 로드 | 로드됨(1,310 + 9,875자) |
| 메타데이터 | 스킬 목록, 에이전트 목록 | 매 세션 노출 | 스킬 51개 26~27천 자(저장소 스킬 5개 2,081자), 에이전트 목록 3~5천 자 |
| 상태 | `MEMORY.md` `## 미해결` | 무조건 읽기 | 제목 grep 후 구간 읽기. 세션당 0~13천 자 |
| 규칙 | `MEMORY.md` 20~148행 | 덱 조립·규칙 변경 시 | 별도 측정 없음 |
| 스킬 본문 | 루트 `SKILL.md`, `skills/*` | 호출 시 전문 | 9/8 이후 create-slides 2회 |
| 단계 문서 | `references/phases/` | 단계 진입 시 | FRAME 1회 Read |
| 훅 | `hook_slide_guard.py` 5개 모드 | Write·Edit마다 | AC3 주입 222회. FRAME 주입 0회(Bash 경유 편집, 과목에 `슬라이드지침.md` 없음) |
| git | `.githooks/_gate.py` 8개 검사 | 커밋 시 | 차단 사례 있음 |
| 과제 | `plans/<주제>/` | 규정 없음 | FRAME·AC3·온라인 모두 PLAN + 인계 문서 사용 |
| Codex | `.agents/`, `.codex/` | 병행 | AC3에 7개 세션 사용 |

### 4-2. 세션 시작 첨부 기록(문자 수, 13개 세션 범위)

| 항목 | 문자 수 | 저장소가 정하는가 |
|---|---:|---|
| 스킬 목록 | 26,089~27,597 | 5개(2,081자)만 |
| 시스템 프롬프트 스냅샷 | 11,211~18,563 | 아니다 |
| 지연 도구 목록 | 8,195~13,043 | 아니다 |
| 지침(`CLAUDE.md`+`AGENTS.md`) | 11,224 | 그렇다 |
| MCP 지침 | 3,276~5,297 | 아니다 |
| 에이전트 목록 | 3,059~4,821 | 11개 정의 분량만 |
| 세션 컨텍스트 | 923~3,530 | 아니다 |

문자 수는 토큰이 아니다. 기준선 토큰에서 이 합으로 설명되지 않는 부분(도구 스키마 전문 등)은 로그에 없다.

### 4-3. 문서와 현실이 어긋난 곳(검증된 것만)

- `AGENTS.md:46` "무조건" 대 `AGENTS.md:128` "300줄 넘으면 워커에게". `미해결`은 548줄이다.
- `MEMORY.md:3·9` "완료 표시·날짜별 기록을 남기지 않는다" 대 본문의 ✅ 제목 5개, 날짜 줄 128개, 커밋 해시 줄 13개.
- `MEMORY.md:180·220` "병합 대기" 대 `git branch --merged main`에 두 브랜치가 이미 있다.
- `MEMORY.md:178·696` "3차시 덱 미착수·재개하라" 대 `eb588c1`에서 83장 완성.
- `AGENTS.md:40` "1주차 동결" 대 `sessions/README.md:122` "동결 해제". `MEMORY.md:482`가 스스로 "모순, 사용자 확인 필요"라고 적었다.
- `AGENTS.md:111` "회귀 10모듈" 대 실제 12개.
- FRAME 덱 장수가 `MEMORY.md` 안에 84·99·104·111·119·123으로 함께 적혀 있다.

`MEMORY.md` 안의 모순·번복 쌍은 모두 14개다(`tmp/audit-1008/memory/units.md` §3).

---

## 5. FRAME Workflow — Verified

확인된 것만 적는다. 로그가 있는 구간은 10/1~10/7의 세션 3개다.

| 항목 | 확인된 사실 | 근거 |
|---|---|---|
| 모델 | 메인 Opus 5.5 | 세션 로그 |
| 과제 정본 | `plans/FRAME-개편/PLAN.md`(545줄). 이후 `plans/FRAME-길이별-조립/재개_인계.md` | 파일, 첫 20호출 |
| 시작 시 읽기 | `MEMORY.md` 제목 grep → 진행·인계 문서. 메인의 `MEMORY.md` Read는 3개 세션 합쳐 1회(구간) | 로그 |
| 사람 입력 | 50턴 | 로그 |
| 도구 | Bash 286, Read 65, Write 56, 브라우저 묶음 47, Edit 15, Agent 6 | 로그 |
| 편집 경로 | Edit·Write 대상 중 shard(`part-*.html`) 0건, `tmp/` 45건. 인라인 파이썬 실행 70회 | 로그 |
| 저장소 스크립트 사용 | `assemble_deck` 21, `verify_deck` 10, `verify_notes` 9, `verify_presenter_deck` 11, `run_deck_checks` 7, `build_release` 6 | 로그 |
| 과제 전용 도구 | `time_check.py` 5회 실행. `tone_lint.py`·`time_check.py`·`build_notes.py` 등이 계획 폴더에 있다 | 로그, 파일 |
| 스크린샷 | `shoot_ids.py` 16, `sheet.py` 15 | 로그 |
| 서브에이전트 | 첫 세션 `frame-builder` 6건. `frame-builder`에서 같은 파일 전체 재독 3회 이상이 11건 | 로그 |
| 워커 운용 변경 | 긴 워커 5기 중단 후 10묶음으로 재시작이라고 기록 | `PROGRESS.md:84`(문서 주장. 해당 세션 로그 없음) |
| 게이트 | 10/6 이후 러너·검사기 판정 보류. 10/7 피드백 반영은 "워커를 쓰지 않는다" | `재개_인계.md:46`, `FRAME-피드백-1007/PLAN.md:7` |
| 증거 상태 | 감사 JSON 111장·423×308. 계약 10/6. `조립_보고.md` 9/18. 작업 트리 덱은 그 뒤 변경 | 파일 |
| Codex | 10/2에 `실습자료/실습1_실행보드`를 작업 폴더로 한 세션 1개 | Codex 로그(내용 미분석) |

확인하지 못한 것: 9/18의 47장판 제작, 9/30의 계획 수립과 예시 3장 피드백, 10/1 이전의 Phase A~D 워커 호출. 이 구간은 문서의 자기 서술만 있다.

---

## 6. Causal Limits

| 변수 | FRAME | 비교 작업(AC3) | 통제 여부 | 실제 증거 | 인과 판정 가능 여부 |
|---|---|---|---|---|---|
| 모델 | Opus 5.5 | Opus 5, Fable 5.1 (+Codex GPT 계열 7개 세션) | 통제 안 됨. 완전히 겹침 | 세션 로그 | 불가 |
| 과제 성격 | 신규 제작(47장판 교체) | 기존 덱 보존 변환 | 통제 안 됨 | 계획 문서 | 불가 |
| 사용자 개입량 | 사람 턴 50 | 53 | 턴 수는 비슷. 내용은 다름 | 로그. 유형 분류는 NOT YET CHECKED | 불가 |
| 예시 3장 선승인 | 있었다고 기록 | 없음 | 통제 안 됨 | PLAN 머리말. 해당 세션 로그 없음 | 불가 |
| 과제 계획 문서 | PLAN 545줄 | 제작계획 155KB + 상태장부 | 양쪽 모두 있음 | 파일 | 차이의 원인으로 볼 근거 없음 |
| 잠금 결정표 | D1~D45 | U·M 번호 결정, G00 승인 | 양쪽 모두 있음 | 파일 | 차이의 원인으로 볼 근거 없음 |
| 스크린샷 피드백 | 스크립트 31 + 브라우저 83 | 스크립트 3 + 브라우저 173 | 양쪽 모두 있음 | 로그 | 차이의 원인으로 볼 근거 없음 |
| 서브에이전트 수 | 6 | 122 | 통제 안 됨 | 로그 | 불가 |
| 훅 주입 | 0 | 222 | 통제 안 됨 | 로그 | 불가 |
| Skill 호출 | 0 | 3 | 양쪽 다 거의 없음 | 로그 | 차이의 원인으로 볼 근거 없음 |
| 작업 횟수 | 메인 API 호출 457 | 898 | 통제 안 됨 | 로그 | 불가 |
| 컨텍스트 크기 | 기준선 75~78k, 호출당 평균 197~357k | 기준선 74~75k, 평균 163~514k | 기준선은 같음 | 로그 | 기준선은 원인이 될 수 없다. 창 크기는 불가 |

**현재 데이터로 인과 분리 불가.** 더 앞선 문제가 있다: 결과(품질 차이) 자체가 확인되지 않았다(C12). 원인을 말하려면 먼저 결과를 재는 방법이 있어야 한다.

말할 수 있는 것은 하나다. 세션 기준선과 상시 지침은 두 작업에서 같았으므로, 상시 컨텍스트 구성은 두 작업 사이 차이의 원인이 아니다.

---

## 7. Reusable FRAME Principles

"결과와 관계 증거"는 그 원리가 결과 품질을 올렸다는 증거를 뜻한다. 사용 사실만으로는 채우지 않았다.

| 원리 | FRAME에서 실제 사용? | 결과와 관계 증거 | 비용 | 다른 프로젝트 재사용 가능성 | 판정 |
|---|---|---|---|---|---|
| Sample-first · 예시 3장 승인 | 문서상 예(PLAN v3 머리말). 로그 없음 | 없음. v3 디자인 원칙이 그 피드백에서 나왔다는 문서 기록뿐 | 낮음 | 새 과목·새 테마에 해당 | TEST FIRST |
| 사용자 결정 잠금 | 예(D표) | 없음. AC3에도 있었다 | 낮음 | 높음 | NO EVIDENCE(차별 요인 아님). 단 출처 열은 §11에서 채택 |
| Structure → Copy 분리(G1a/G1b) | 예(`결정표.md`, `G1b_제출.md`) | 없음 | 승인 대기 1회 추가 | 중간 | TEST FIRST |
| Screenshot feedback | 예 | 없음. AC3가 브라우저 호출이 더 많았다 | 중간 | 이미 공통 관행 | NO EVIDENCE(차별 요인 아님) |
| Task-specific PLAN | 예 | 없음. AC3·온라인에도 있었다 | 낮음 | 이미 공통 관행 | NO EVIDENCE(차별 요인 아님) |
| Task-specific lint | 예(`time_check` 5회 실행, R-COPY 3종 통과) | 해당 검사 통과라는 직접 결과만 | 과제마다 제작 | 과제 한정 | TASK-SPECIFIC |
| Context 최소화 | 아니다. 기준선 같고 창 평균도 작지 않다 | — | — | — | NO EVIDENCE |
| Main-agent 중심 · 적은 Subagent | 예(Agent 6) | 품질과의 관계 없음. 토큰은 적었다(C11, 2.4~5.2배) | 낮음 | 높음 | TEST FIRST |
| 시각적 피드백 반복 | 예 | Screenshot feedback과 같다 | — | — | NO EVIDENCE(차별 요인 아님) |

ADOPT로 판정할 만큼 결과와의 관계가 확인된 원리는 없다. TEST FIRST 3건은 §14의 Eval에 넣었다.

---

## 8. Context Waste — 증명된 것만

| # | 낭비 | 실측 | 규모 |
|---|---|---|---|
| W1 | 같은 과목 지침의 반복 주입 | 671720eb 한 세션에 187회·63,206자. AC3 전체 213회·72,018자, 사전 점검 9회·6,111자 | 세션 창에 누적되고 이후 호출마다 다시 읽힌다 |
| W2 | 긴 세션의 창 누적 | 호출당 평균 입력 163k~514k. 압축은 13개 세션 중 2회 | 입력 합의 대부분 |
| W3 | 서브에이전트의 반복 읽기(FRAME) | `frame-builder` 6기에서 같은 파일 전체 재독 3회 이상 11건, 2회 이상 31건 | 워커 6기 입력 41.8M |
| W4 | 낡은 상태 서술 | `미해결`의 과업 서술 72건 중 DONE 15·SUPERSEDED 9. 모순 쌍 14 | 토큰이 아니라 오판 위험 |

**증명되지 않아 낭비 목록에서 뺀 것**
- `미해결` 통째 읽기(실제로 일어나지 않았다).
- AC3 워커의 재독 103건(구간 읽기다).
- `AGENTS.md` 길이. 기준선의 13~15% 수준으로 추정되고, 줄였을 때의 효과는 재지 않았다.
- 스킬·에이전트 description. 저장소 몫은 스킬 2,081자다.
- AC3의 Opus 워커 사용. 토큰은 컸지만 그 대가로 얻은 품질을 재지 않았으므로 낭비라고 할 수 없다.

---

## 9. Harness / Skill / Hook Verdict

사용량은 Skill 도구 호출 기준이고 괄호는 기간이다.

| 요소 | 해결하려던 문제 | 실제 사용량 | 성공 사례 | 실패 사례 | Context 비용 | 운영비용 | 대체 가능성 | 판정 |
|---|---|---:|---|---|---:|---|---|---|
| 하네스 문서 | 다파일 작업의 분담·게이트 | 호출 4(7~8월), 0(9/8~). FRAME PLAN이 § 번호로 인용 | NOT YET CHECKED | 긴 워커 5기 중단(문서 주장) | 호출 시 21KB. 목록 282자 | 문서 유지 | 과제 PLAN이 같은 규칙을 다시 적고 있다 | NEEDS EVAL |
| `/리서치` | 조사·실습 검증 | 4(7월), 0(9/8~) | 바이브코딩 1~3주차 산출물 존재 | FRAME D14가 명시적으로 배제 | 호출 시 45KB + 스키마 15KB. 목록 523자 | 워커 감사 절차 | 과목 전용 researcher가 대신함 | ON-DEMAND(현행 유지) |
| `/검토` | 산출물 읽기 전용 검토 | 0(전 기간) | 산출물 미발견 | — | 호출 시 34KB. 목록 273자 | — | 과목 전용 reviewer가 대신함 | NEEDS EVAL |
| Reviewer gate(독립 검토 워커) | 작성자 편향 | ac3-reviewer 24, FRAME 0(로그 구간) | NOT YET CHECKED | NOT YET CHECKED | 워커 시작 17~19k | 높음 | 공식 지침이 갈린다(§10) | NEEDS EVAL |
| 훅 `course`·`checklist` | 지침 미준수 방지 | AC3 222회, 7~8월 315회, FRAME 0 | NOT YET CHECKED | 반복 주입(W1). Bash 경유 편집은 못 잡음 | 주입당 309~705자 | 낮음 | 세션당 1회 주입 | SIMPLIFY |
| 훅 `generated-guard`·`tmp-guard`(관측) | 생성물 직접 편집, 저장소 밖 쓰기 | 장부 346줄 | 위반 137건 관측 | 차단하지 않음. 장부가 gitignore | 0 | 낮음 | pre-commit이 생성물 건은 차단 | KEEP(승격 여부는 사용자 결정) |
| 훅 `css-lint` | CSS 회귀 | 주입 0 | pre-commit에서 같은 규칙이 커밋을 막은 기록 | — | 0 | 낮음 | — | KEEP |
| pre-commit 게이트 | 커밋 시점 강제 | 검사 8종 | 차단 사례 있음 | — | 0 | 낮음 | 없음 | KEEP |
| 과목 전용 에이전트 | 역할·도구·모델 제한 | ac3-* 104건, frame-* 6건 | NOT YET CHECKED | 정의 9개가 서로 복사본 | 목록 수천 자, 워커 시작 15~20k | 과목마다 파일 4~5개 | 공통 정의 + 위임문 | MERGE(AC3 종료 확인 뒤) |
| general-purpose | 범용 조사 | 9월 12건, 7~8월 145건 | — | 시작 약 60k | 워커당 60k | 없음 | Explore·전용 정의 | KEEP |
| 스킬 어댑터 | 플랫폼 공통 정본 | — | 3개 플랫폼이 `.agents/skills`를 읽는다(문서) | 리서치 어댑터가 `claude-sonnet-5`를 하드코딩 | 낮음 | 정합 검사 있음 | — | KEEP |
| `ui-ux-pro-max` 2벌 | UI 참고 데이터 | 호출 1, `search.py` 실행 4(7~8월) | NOT YET CHECKED | 2벌 중복 3.3MB | 목록 464자 | 디스크뿐 | 한 벌 + 경로 참조 | KEEP(컨텍스트 비용 없음) |
| create-slides `SKILL.md` | 덱 조립 계약 | 호출 9(전 기간) | 덱 9종 산출 | FRAME은 호출 없이 스크립트만 사용 | 호출 시 22.5KB | 정합 검사 있음 | — | KEEP · 분할은 NEEDS EVAL |
| 검증 스크립트·러너 | 결함 검출 | FRAME 44, AC3 103 실행 | AC3·온라인 감사 증거 | FRAME에서 판정 보류 | 출력 크기만 | 중간 | 없음 | KEEP · FRAME 정합은 §15 TASK-009 |

**이전 보고서 권고 중 폐기하는 것**
- R-QC-08에 SVG를 넣는 수정. 미집계는 의도된 정의이고(C13), FRAME SVG의 다수는 작은 것이라 전부 세면 지표가 부풀려진다(C12).
- 리서치·검토·하네스에 `disable-model-invocation`을 넣어 목록에서 내리는 안. 절감이 1,078자다.
- "하네스를 한 쪽으로 축소". 축소가 품질을 유지하는지 잰 적이 없다.
- "과목 전용 훅 두 개를 배선에서 내린다". 장부에 위반 137건이 잡혀 있다.

---

## 10. Official Guidance Comparison

확인일 2026-10-08. 워커가 원문을 직접 받아 문자열을 대조했다. Anthropic 22건 + OpenAI 12건 + Google 12건 중 CONTRADICTED 0, NOT FOUND 0, 조건 누락 7건이다.

| 주제 | Anthropic(Claude Code) | OpenAI(Codex) | Google(Gemini CLI·Antigravity) | 이 저장소 |
|---|---|---|---|---|
| 상시 지침 길이 | CLAUDE.md 파일당 200줄 미만 목표 | AGENTS.md 합계 32KiB에서 로드 중단. 짧고 정확한 쪽을 권함 | Antigravity: 파일당 24KB, 상시 합계 20,000토큰 | `AGENTS.md` 9,875자. Codex 한도 안 |
| import | `@import`는 컨텍스트를 줄이지 않음. 최대 4단계 | — | `@file` import 지원 | `CLAUDE.md`가 `@AGENTS.md` 한 줄. 문서가 안내하는 패턴 |
| 하위 폴더 지침 | 하위 `CLAUDE.md`는 Read·Write·Edit 시, 하위 `AGENTS.md`는 Read 시에만 | 루트에서 현재 폴더까지 시작 시 이어붙임 | 도구가 접근한 폴더와 그 상위를 그때 스캔 | 미사용 |
| 스킬 | 본문 500줄 미만, 참조는 한 단계. eval 먼저 | 목록 예산 컨텍스트의 2%. `.agents/skills` 스캔 | 이름·설명만 먼저. `.agents/skills` 우선 | 본문 22~45KB. 어댑터→정본→참조 두 단계 |
| 서브에이전트 | CLAUDE.md 계층 로드. `omitClaudeMd`로 끌 수 있음. Explore·Plan은 건너뜀 | 단일 에이전트보다 토큰을 더 쓴다고 명시. 읽기 위주 병렬에 권함 | 격리된 컨텍스트. 하위에는 최소 컨텍스트 | AC3는 쓰기 워커 위주 |
| 훅 | 지침은 권고, 훅은 결정적. exit 2만 차단. 주입은 값당 10,000자 | `PreToolUse` 입력에 경로 키 없음 | `BeforeTool` 입력에 표준 경로 필드 없음 | 저장소의 "Codex 이식 불가" 판정과 일치 |
| 검증·리뷰어 | best-practices: 새 컨텍스트의 리뷰어 권장. Opus 5·Sonnet 5.5 가이드: 검증용 서브에이전트 지시 제거 | — | — | reviewer 게이트 보유 |
| 평가 | 스킬 작성 전 eval, 스킬 없는 기준선과 비교 | 프롬프트 10~20개와 음성 대조군 | 궤적과 최종 응답 두 축 | 라우팅 eval만 있음 |

**조건이 빠졌던 주장(정정)**
- "최신 모델은 강한 지시어에 과민" → 원문은 Opus 4.5·4.6에 대한 서술이다.
- "Sonnet 5.5에서 세션 비용 약 3분의 1 절감" → `max` effort에서 리뷰어 서브에이전트를 막았을 때의 값이다.
- "agent teams 약 7배" → 팀원이 plan mode일 때의 값이다.
- "메인 대화 캐시 1시간" → 구독 플랜 포함 사용량 안에서만이다.
- "OpenAI: 메모리는 조언이지 권위가 아니다" → 전역 메모 노트에 한한다. 구조화된 프로필은 "authoritative"라고 부른다.
- "OpenAI: 모순 지시는 추론 낭비" → 원문은 "불안정"과 "조기 중단"이다.
- "훅이 넣은 컨텍스트는 압축 시 요약에 흡수" → 그렇게 적은 문장이 없다. 철회.

**공식 지침 충돌 → Repository 특화 Eval 필요**
1. 독립 리뷰어: Claude Code best-practices는 권하고, Opus 5·Sonnet 5.5 프롬프팅 문서는 검증용 서브에이전트 지시를 빼라고 한다. 이 저장소의 reviewer 워커가 어느 쪽에 해당하는지는 문서로 정할 수 없다. → §14 ablation A2.
2. 리뷰어 보고 범위: "정확성에 영향 주는 것만" 대 "전부 보고시키고 따로 거르라". → 현행 유지, Eval 대상.

---

## 11. Proposed Context Architecture

설계 원칙: 검증된 문제에만 손을 댄다. 검증된 문제는 넷이다 — 낡은 상태 서술(W4), 지시와 실제 읽기의 불일치(C3), 반복 훅 주입(W1), FRAME 검증 층의 보류 상태(§5). `AGENTS.md` 축소, 스킬 분할, 하네스 축소는 효과가 측정되지 않았으므로 구조에 넣지 않는다.

| 구분 | 파일 | 역할 | 누가 읽는가 | 언제 | 예상 크기 | SoT 여부 | 업데이트 책임 | 최대 크기 | Archive 조건 |
|---|---|---|---|---|---|---|---|---|---|
| A Always-on | `AGENTS.md`(+`CLAUDE.md`) | 공통 행동 규칙 | 모든 세션·워커 | 자동 | 현행 9,875자 | 그렇다 | 규칙 변경 작업자 | Codex 32KiB | 해당 없음 |
| B Router | `AGENTS.md` 안의 「작업 전 읽기」 절 | 작업 유형별 첫 문서 안내 | 모든 세션 | 자동 | 10줄 안팎 | 포인터 | 위와 같음 | — | — |
| D Active State | `STATE.md`(신설) | 열린 과업의 색인과 상세 | 모든 세션 | 색인 표는 작업 시작 시, 상세는 해당 과업일 때 | 색인 30행 안팎 + 상세 | 그렇다(열린 과업에 한해) | 과업을 닫는 세션 | 색인 40행, 파일 16KB | 닫힌 과업은 행을 지운다 |
| C Task-specific | `plans/<주제>/PLAN.md`·`재개_인계.md` | 과제별 결정·상태 | 그 과제 세션 | STATE가 가리킬 때 | 현행 | 그렇다(그 과제) | 그 과제 세션 | 규정 안 함 | 과제 종료 시 |
| C Task-specific | `MEMORY.md`(규칙 절만 남김) | 재발 방지 규칙·교훈 | 덱 조립·규칙 변경 세션 | 해당 작업 시 | 약 30.8KB + 이관분 | 그렇다(다른 정본에 없는 규칙) | 규칙을 얻은 세션 | 규정 안 함(§18) | 정본으로 승격 확인 시 |
| C Task-specific | `SKILL.md`, `references/`, `kit/guide/`, `skills/` | 도메인 정본 | 해당 작업 | 현행 | 현행 | 그렇다 | 현행 | 현행 | — |
| E Archive | `_dev/설계기록/MEMORY-이력-2026-10.md`(신설) | `미해결`에서 나온 역사·종결 기록 원문 | 필요한 사람 | 검색 시 | 약 60~70KB | 아니다 | 이관 작업자 | 없음 | — |
| F Evidence | `courses/*/sessions/_verify/`, `plans/agent-system-audit/baseline/` | 감사 JSON·측정값 | 검증 작업 | 필요 시 | — | 측정값의 정본 | 측정한 세션 | — | — |

`STATE.md` 색인 행의 열: `ID | 범위(과목·인프라) | 한 줄 상태 | 다음 행동 | 담당(사용자/에이전트) | 상세 위치 | 확인일`. `확인일`은 그 행을 저장소 현실과 마지막으로 대조한 날이다. 낡은 서술(W4)을 드러내는 열이다.

FRAME PLAN에서 채택하는 것은 결정표의 **출처 열** 하나다. C15에서 결정 49행 중 26행의 출처를 가릴 수 없었다. 새 과제의 결정표에는 `출처(사용자 지시 원문 위치 / 에이전트 판단)` 열을 둔다. 이것은 품질 원리가 아니라 추적 가능성 요건이다.

---

## 12. Information Migration Map

`MEMORY.md`를 역할별로 나눈 결과다(`tmp/audit-1008/memory/units.md`. 워커 분해. 표본 3건 대조에서 "여기에만 있음" 판정 2건이 오탐이었다 — 정본에도 있었다. 그래서 아래 계획은 **삭제 판단에 그 분류를 쓰지 않는다**).

| 정보 유형 | 현재 위치 | 분량 | 필요 빈도 | 이동처 | 방식 |
|---|---|---|---|---|---|
| 운영 계약 | 5~19행 | 1.7KB | 항상 | `MEMORY.md`에 유지. 7행만 `STATE.md`를 가리키게 수정 | 유지 |
| 규칙·교훈(기존 절) | 20~148행 | 약 29KB | 덱 조립·규칙 변경 시 | 유지 | 유지 |
| 열린 과업 | `미해결` 곳곳, 25건 | 해당 줄 약 11~13KB | 항상(색인만) | `STATE.md` | 다시 씀(원문은 Archive에 그대로) |
| 대조하지 못한 과업 서술 | `미해결`, 21건 | — | 항상(색인만) | `STATE.md`에 `확인 필요` 상태로 | 다시 씀 |
| 대기 중인 사용자 결정 | 155·165·201·206·434·444·482행 등 | — | 항상 | `STATE.md`, 담당 = 사용자 | 다시 씀 |
| 규칙·교훈(`미해결` 안, ⚠️ 소절과 본문 속 문장) | U20·U21·U24~U28·U39·U41·U42·U46 등 | 약 20KB | 가끔 | `MEMORY.md`에 새 절 `## 이관된 교훈 (2026-10)` | 원문 그대로 이동 |
| 프로젝트 지식 | U22·U23·U34·U47 등 | 약 6KB | 가끔 | 위와 같은 절 | 원문 그대로 이동 |
| 작업 역사·종결 기록 | U26·U30·U31·U35·U40b·U44·U45·U49 등 | 약 45KB | 역사 보관 | `_dev/설계기록/MEMORY-이력-2026-10.md` | 원문 그대로 이동 |
| 낡은 상태 서술(DONE 15·SUPERSEDED 9) | 여러 소절 | — | 삭제 가능 | Archive에 원문으로만 남김. `STATE.md`에는 넣지 않음 | 이동 |
| 과목별 현재 상태(FRAME·온라인·AC3) | U12~U16 | 약 11KB | 그 과목 작업 시 | 이미 `plans/*/재개_인계.md`에 있음. `STATE.md`에는 포인터 행 | 포인터 |

어느 소절이 어느 칸인지는 TASK-003의 대조표가 정한다. 원칙은 하나다: **`미해결`의 모든 줄은 `STATE.md`·`MEMORY.md` 새 절·Archive 셋 중 한 곳에 원문으로 존재해야 한다.** 다시 쓰는 것은 `STATE.md` 색인뿐이고, 그 원문도 Archive에 남는다.

규칙 255개의 중복 정리(정본에 이미 있는 142건 제거)는 이번 개편 범위에서 뺀다. 건별 확인 없이 지우면 유실 위험이 있다(§18).

---

## 13. Token Budget

| 구분 | 현재 | 개선안 | 변화 | 성격 |
|---|---:|---:|---|---|
| 세션 기준선 | 74.0k~77.7k | 같음 | 없음 | 실측. 이번 개편은 상시 층 크기를 바꾸지 않는다 |
| 상태 읽기(세션당) | 0~13,150자 | `STATE.md` 색인 약 3~4KB + 해당 상세 | 비슷하거나 약간 증가 | 현재는 실측. 개선안은 설계 값 |
| 과목 지침 훅 주입 | 편집마다 309~705자. 최대 187회/세션 | 세션·과목당 1회 | 긴 편집 세션에서 수만 자 감소 | 현재는 실측. 감소폭은 편집 횟수에 달렸다 |
| 워커 시작 크기 | 15~20k(전용), 약 60k(범용) | 같음 | 없음 | 실측 |
| 작업별 의무 읽기(가정 계산) | 58k~185k | — | — | 실측이 아니다. 비교에서 뺀다 |

이 개편은 토큰 절감 계획이 아니다. 측정으로 뒷받침되는 토큰 감소는 훅 주입 한 줄뿐이다. 상태 층 개편의 목적은 낡은 서술과 모순을 없애는 것이고, 토큰은 중립이다.

입력 합의 대부분은 긴 세션의 창 누적이다(W2). 이것은 지침 구조가 아니라 세션 운영의 문제이고, 세션 분리를 강제하는 수단은 이번 명세에 넣지 않았다(효과를 잰 자료가 없다).

---

## 14. Evaluation Design

### 14-1. Baseline

개편 전에 TASK-001로 현재 `main`의 값을 남긴다. 측정은 세션 JSONL에서 `tmp/audit-1008/logs/measure.py`로 뽑는다.

### 14-2. 과제 3종

| 과제 | 내용 | 성격 | 정답 판정 |
|---|---|---|---|
| EV-1 재개 | 새 세션에서 "지금 열려 있는 일 중 내가 정해야 할 것을 알려 줘" | 조회 | TASK-003 대조표의 사용자 대기 항목과 일치하는 수, 낡은 항목을 열린 것으로 말한 수 |
| EV-2 지정 수정 | 동결되지 않은 덱의 사본에서 지정 3건 수정(문구 1, 배치 1, 삭제 1) | 기존 결과물 수정 | 지정 3건 반영, 그 밖의 변경 0(`git diff --stat`), `verify_deck` 판정이 전과 같음 |
| EV-3 규칙 변경 | 문서 한 곳과 그 집행 스크립트를 함께 고치는 작은 변경(예: 회귀 모듈 수 표기 정정) | 코드·문서 수정 | `verify_declared_vs_enforced.py` 통과, 회귀 12모듈 통과 |

신규 제작 과제는 넣지 않는다. 산출물 품질을 객관적으로 재는 지표가 없다(C12).

### 14-3. Metric(측정 가능한 것만)

| 범주 | Metric | 출처 |
|---|---|---|
| Context | 첫 API 호출 입력 | 로그 |
| Context | 첫 Edit·Write 전까지의 입력 합 | 로그 |
| Context | 총 입력, 호출당 평균 입력 | 로그 |
| Context | 같은 파일 전체 Read 2회 이상 건수 | 로그 |
| Behavior | Agent 호출 수, 도구 호출 수 | 로그 |
| Behavior | 훅 주입 횟수·문자 수 | 로그 |
| Output | 과제별 정답 판정(위 표) | diff, 스크립트 종료코드 |
| Output | 범위 밖 변경 파일 수 | `git status --short` |
| Cost | 출력 토큰, 경과 시간 | 로그 |

metric에서 뺀 것: "관련 없는 컨텍스트 비율"(판정 기준이 없다), "사용자 수정 요구량"(단발 과제에서는 생기지 않는다), "불필요한 위임"(판정 기준이 없다).

각 과제를 조건당 3회 돌린다. 3회의 범위가 조건 간 차이보다 크면 "차이 없음"으로 적는다.

### 14-4. 모델 A/B 실험의 타당성

| 질문 | 답 |
|---|---|
| 1. 같은 모델 버전을 고를 수 있는가 | NOT YET CHECKED. 로그상 `claude-opus-5`의 마지막 사용은 9/12다. 지금 선택 가능한지는 사용자가 모델 선택 화면에서 확인해야 한다 |
| 2. 같은 Task를 재현할 수 있는가 | FRAME 과제는 불가. 사람 턴 50개와 로그 없는 9/30 대화가 입력이었다 |
| 3. 입력 Context를 같게 통제할 수 있는가 | 가능. 같은 커밋의 새 worktree, 같은 프롬프트 |
| 4. 사용자 피드백을 같게 만들 수 있는가 | 불가. 피드백 없는 단발 과제로만 설계할 수 있다 |
| 5. 객관적 metric이 있는가 | 없다. 정적 지표는 정의에 따라 순위가 바뀐다(C12). 사람의 블라인드 평가가 필요하다 |
| 6. 비용 대비 정보 가치 | 단발 과제의 결과는 "피드백 없는 한 번의 제작에서 모델 차이"만 말한다. FRAME의 품질 원인은 설명하지 못한다 |

**현재 환경에서는 FRAME 품질의 원인을 가르는 유효한 A/B test 불가.** 2·4·5번이 충족되지 않는다. 1번이 참이고 사용자가 블라인드 평가를 맡는다면 "단발 슬라이드 6장, 모델 2종 × 3회"의 좁은 실험은 설계할 수 있다. 그 실험이 답하는 질문은 위 6번에 적은 것뿐이다. 이번 명세에는 넣지 않았다.

### 14-5. Ablation 후보(Eval 틀이 선 뒤)

| ID | 변경 | 과제 | 볼 것 |
|---|---|---|---|
| A1 | 훅 주입 매번 대 세션당 1회 | EV-2 | 범위 밖 변경, 규칙 위반, 주입 문자 수 |
| A2 | reviewer 워커 있음 대 없음 | EV-3 | 정답 판정, 총 입력 |
| A3 | 메인 단독 대 writer 워커 위임 | EV-2 | 정답 판정, 총 입력 |

---

## 15. Migration Tasks

모든 Task는 FRAME 미커밋 파일과 겹치지 않게 설계했다. 유일한 예외는 `MEMORY.md`다 — 이 파일에는 FRAME 작업의 미커밋 수정이 들어 있다(TASK-003의 Dependency 참조).

### TASK-001 — Baseline 고정

- **Goal**: 개편 전 상태와 측정값을 되돌릴 수 있게 남긴다.
- **Evidence**: 이전 보고서의 원자료가 gitignore된 `tmp/`에만 있다.
- **Files**: 신설 `plans/agent-system-audit/baseline/`(복사본), git 태그.
- **Current behavior**: 재측정 스크립트와 결과가 `tmp/audit-1008/`에 있다.
- **Target behavior**: `baseline/`에 `git_baseline.txt`, `logs/measure.py`, `logs/rep1.py`~`rep3.py`, `memory/units.md`, `memory/only_here.json`이 있고, 태그 `audit-baseline-2026-10-08`이 `a979b42`를 가리킨다.
- **Exact changes**: 위 파일 복사. `git tag audit-baseline-2026-10-08 a979b42`.
- **Preserve**: 작업 트리의 미커밋 변경 전부. 태그는 HEAD 커밋에만 건다.
- **Do not change**: 작업 트리, stash, 브랜치.
- **Dependency**: 없음.
- **Risk**: 없음(추가만 한다).
- **Verification**: `git status --short | wc -l`이 복사한 파일 수만큼만 늘었다. `git rev-parse audit-baseline-2026-10-08`이 `a979b423…`이다.
- **Rollback**: `git tag -d audit-baseline-2026-10-08`, `baseline/` 삭제.
- **Priority**: P0.

### TASK-002 — `MEMORY.md` 원문 스냅샷

- **Goal**: 이관 전 `MEMORY.md` 전문을 검색 가능한 파일로 남긴다.
- **Evidence**: 정보 유실이 이 개편의 최대 위험이다. 워커 분류에 오탐이 있었다(§12).
- **Files**: 신설 `_dev/설계기록/MEMORY-스냅샷-2026-10-08.md`.
- **Current behavior**: 원문은 `MEMORY.md`에만 있고 미커밋 수정이 섞여 있다.
- **Target behavior**: 스냅샷이 작업 트리의 `MEMORY.md`와 바이트 단위로 같다(머리에 출처 한 줄을 붙인다면 그 줄만 다르다).
- **Exact changes**: 파일 복사.
- **Preserve**: 원본 `MEMORY.md`는 건드리지 않는다.
- **Do not change**: `MEMORY.md`.
- **Dependency**: TASK-001.
- **Risk**: 없음.
- **Verification**: 두 파일의 sha256이 같다(머리 줄을 붙였으면 그 줄을 뺀 나머지).
- **Rollback**: 스냅샷 삭제.
- **Priority**: P0.

### TASK-003 — `미해결` 소절 대조표 확정

- **Goal**: `미해결` 548줄 각각의 이동처를 사람이 검토할 수 있는 표로 확정한다.
- **Evidence**: C2, §12. `units.md`는 워커 산출이고 과업 21건이 미대조다.
- **Files**: 신설 `plans/agent-system-audit/memory-migration-map.md`.
- **Current behavior**: `units.md`(49단위)가 분류 제안을 담고 있다.
- **Target behavior**: 표의 각 행이 `줄 범위 | 유형 | 이동처(STATE / MEMORY 새 절 / Archive) | 근거`를 갖고, 줄 범위의 합집합이 149~696행 전체를 빈틈없이 덮는다.
- **Exact changes**: `units.md`를 바탕으로 표 작성. 미대조 과업 21건은 저장소에서 대조하고, 못 한 것은 `확인 필요`로 둔다. `STILL OPEN` 25건은 각각 다시 확인한다.
- **Preserve**: 사용자 결정 대기 항목(155·165·201·206·434·444·482행), 동결 관련 서술, `--accent-note` 미등재 결정(658행).
- **Do not change**: `MEMORY.md`, `AGENTS.md`.
- **Dependency**: TASK-002. FRAME 미커밋 작업의 처리(커밋할지 여부)는 사용자가 정한다 — `MEMORY.md`에 미커밋 수정이 있어서, 이 표의 줄 번호는 그 시점의 파일 기준으로 다시 맞춰야 한다.
- **Risk**: 줄 번호가 이후 편집으로 밀린다. 대응: 표 머리에 대상 파일의 sha256을 적는다.
- **Verification**: 스크립트로 줄 범위 합집합이 149~696과 같고 겹침이 없음을 확인. 사용자가 표를 승인.
- **Rollback**: 표 파일 삭제.
- **Priority**: P1.

### TASK-004 — `STATE.md` 생성

- **Goal**: 열린 과업의 단일 색인을 만든다.
- **Evidence**: W4(모순 14쌍, 낡은 서술 24건), C3.
- **Files**: 신설 `STATE.md`(저장소 루트).
- **Current behavior**: 열린 과업이 `미해결` 32개 소절에 흩어져 있고 낡은 서술과 섞여 있다.
- **Target behavior**: 색인 표(열은 §11) + 과업별 상세 블록. 색인 40행 이하, 파일 16KB 이하.
- **Exact changes**: TASK-003 표에서 이동처가 STATE인 줄로 색인과 상세를 쓴다. 과목 상태는 `plans/*/재개_인계.md`를 가리키는 포인터 행으로 둔다. 모든 행에 확인일을 적는다.
- **Preserve**: TASK-003의 Preserve 항목 전부.
- **Do not change**: `MEMORY.md`(아직 그대로 둔다. 이 시점에는 두 곳에 함께 있다).
- **Dependency**: TASK-003.
- **Risk**: 색인을 쓰다가 조건·단서가 빠진다. 대응: 상세 블록에 원문 줄 번호를 적는다.
- **Verification**: TASK-003 표의 STATE 행 수와 `STATE.md` 색인 행 수가 대응한다. EV-1을 `STATE.md`만 주고 돌려 사용자 대기 항목을 전부 답하는지 본다.
- **Rollback**: `STATE.md` 삭제.
- **Priority**: P1.

### TASK-005 — `미해결` 본문 이관

- **Goal**: `MEMORY.md`에서 상태·역사를 빼고 규칙 문서로 만든다.
- **Evidence**: §12.
- **Files**: `.agents/agent-memory/create-slides/MEMORY.md`, 신설 `_dev/설계기록/MEMORY-이력-2026-10.md`.
- **Current behavior**: `MEMORY.md` 696줄, `미해결` 548줄.
- **Target behavior**: `MEMORY.md` = 1~148행 + 새 절 `## 이관된 교훈 (2026-10)`(원문 이동분) + `## 미해결`(한 줄: "`STATE.md`를 본다"). 역사·종결 기록은 Archive에 원문으로 있다.
- **Exact changes**: TASK-003 표의 이동처대로 줄을 옮긴다. 문장을 고치지 않는다. `MEMORY.md:7`을 "작업 시작 전 `STATE.md`의 색인을 읽는다"로 바꾼다.
- **Preserve**: `미해결`의 모든 줄이 세 곳 중 하나에 있어야 한다.
- **Do not change**: `MEMORY.md` 20~148행의 내용. 규칙 중복 정리는 하지 않는다.
- **Dependency**: TASK-004.
- **Risk**: 줄 누락. 대응: 아래 검증.
- **Verification**: 스냅샷(TASK-002)의 149~696행 각 줄이 `STATE.md` 상세·`MEMORY.md`·Archive 중 한 곳에 그대로 있는지 스크립트로 전수 대조(색인으로 다시 쓴 줄은 Archive에 원문이 있어야 한다). `verify_skill_setup.py` 종료코드 0. 회귀 12모듈 통과.
- **Rollback**: `git checkout` 대상은 `MEMORY.md` 한 파일이다. 단 그 파일에 미커밋 수정이 있었다면 스냅샷(TASK-002)에서 되살린다.
- **Priority**: P1.

### TASK-006 — 읽기 지시를 `STATE.md`로 돌린다

- **Goal**: 지시와 실제 동작을 맞춘다.
- **Evidence**: C3. `AGENTS.md:46` 대 `AGENTS.md:128`.
- **Files**: `AGENTS.md`(11·46·130행), `README.md:207`, `skills/하네스/SKILL.md:234`.
- **Current behavior**: 다섯 곳이 `MEMORY.md`의 `## 미해결`을 상태 정본으로 가리킨다.
- **Target behavior**: 다섯 곳이 `STATE.md`를 가리킨다. `AGENTS.md:46`은 "`STATE.md` 색인 표를 읽는다. 상세는 맡은 과업의 것만"이 된다.
- **Exact changes**: 다섯 줄의 경로와 문구 교체. `plans/`·`_dev/`·`courses/` 안의 옛 언급(12개 폴더)은 과거 기록이므로 고치지 않는다.
- **Preserve**: `AGENTS.md:46`의 뒷부분("나머지 절은 덱 조립·규칙 변경 작업일 때"), 종료 전 재확인 의무.
- **Do not change**: `AGENTS.md`의 다른 절. 길이 축소는 이 Task가 아니다.
- **Dependency**: TASK-005.
- **Risk**: Codex가 같은 `AGENTS.md`를 읽는다. 문구가 바뀌어도 크기는 32KiB 아래다.
- **Verification**: `grep -rn "## 미해결" AGENTS.md README.md skills`가 0줄. `verify_declared_vs_enforced.py` 종료코드 0. 새 세션의 첫 10개 도구 호출에 `STATE.md` Read가 있다.
- **Rollback**: 세 파일을 `git checkout`.
- **Priority**: P1.

### TASK-007 — `STATE.md` 크기·형식 게이트

- **Goal**: 상태 파일이 다시 이력 문서가 되지 않게 한다.
- **Evidence**: E1(두 달간 소절 순삭제 1건, 6개 → 32개).
- **Files**: `.githooks/_gate.py`(검사 함수 1개 추가), `tests/`에 테스트 1개.
- **Current behavior**: 검사 8종에 상태 파일 검사가 없다.
- **Target behavior**: `STATE.md`가 staged일 때 색인 40행 초과, 16KB 초과, 확인일 열이 빈 행이 있으면 차단한다. 탈출구는 기존 `SKIP_DECK_GATES=1`이다.
- **Exact changes**: `check_state_file(root, staged)`를 추가하고 `main()`에 등록. 판정 줄에 행 수와 바이트를 찍는다.
- **Preserve**: 기존 검사 8종의 동작과 출력.
- **Do not change**: `hook_slide_guard.py`.
- **Dependency**: TASK-004.
- **Risk**: 한도가 실제 열린 과업 수보다 작을 수 있다. 대응: TASK-004의 실제 행 수를 보고 한도를 정한다.
- **Verification**: 41행 픽스처로 종료코드 1, 40행으로 0. 회귀 13모듈 통과.
- **Rollback**: 함수와 테스트 삭제.
- **Priority**: P1.

### TASK-008 — 확인된 문서 불일치 정정

- **Goal**: 검증된 수치·경로 오류를 고친다.
- **Evidence**: E5, §4-3.
- **Files**: `AGENTS.md:111`, `README.md`(회귀 모듈 수, `/콘텐츠` 현역 표기).
- **Current behavior**: "회귀 10모듈", `/콘텐츠` 현역.
- **Target behavior**: 실제와 같다(12모듈, `/콘텐츠` 폐기).
- **Exact changes**: 해당 줄만 수정. 차트 21 대 23 등 E6의 5건은 먼저 실제 값을 세고 나서 고친다.
- **Preserve**: 나머지 문장.
- **Do not change**: 동결 대 동결 해제 모순(`AGENTS.md:40` 대 `sessions/README.md:122`). 사용자 결정 사항이다.
- **Dependency**: 없음.
- **Risk**: 낮음.
- **Verification**: `ls tests/test_*.py | wc -l`과 문서 수치가 같다. `verify_declared_vs_enforced.py` 종료코드 0.
- **Rollback**: 두 파일 `git checkout`.
- **Priority**: P2.

### TASK-009 — FRAME 검증 FAIL 분류 설계

- **Goal**: 보류 중인 FRAME 게이트를 다시 켤 수 있도록 FAIL 각각의 처분을 정한다.
- **Evidence**: C13, §5.
- **Files**: 신설 `plans/agent-system-audit/frame-gate-reconciliation.md`. (FRAME 산출물과 `deck.contract.json`은 이 Task에서 건드리지 않는다.)
- **Current behavior**: 커밋본 기준 `verify_deck` FAIL 4, 품질 FAIL 1. 사용자 결정으로 보류.
- **Target behavior**: FAIL마다 `실위반(고칠 것) / 계약 등재(waiver) / 검사기 어휘 추가` 중 하나와 근거가 적힌 문서.
- **Exact changes**: (1) raw hex 149건의 위치별 분류 (2) gradient 10건 (3) asset-slot 밖 img 목록 (4) 구도 `other` 문제 — FRAME 구도 클래스를 분류기에 등록할지 (5) `viz-*` 미태그 도해 목록.
- **Preserve**: 다른 과목의 검사 결과. 임계를 낮추지 않는다.
- **Do not change**: FRAME 덱·shard, 검사기 코드.
- **Dependency**: 없음. 실행은 FRAME 미커밋 작업이 정리된 뒤가 맞다(그 정리는 사용자 몫).
- **Risk**: 낮음(문서만).
- **Verification**: 문서의 건수 합이 `verify_deck` 출력의 건수와 같다.
- **Rollback**: 문서 삭제.
- **Priority**: P1.

### TASK-010 — 렌더 감사 뷰포트 하한

- **Goal**: 잘못된 창 크기에서 잰 증거가 통과로 쓰이지 않게 한다.
- **Evidence**: FRAME `deck-audit.json`의 뷰포트 423×308. 다른 덱은 1280×720 이상.
- **Files**: 증거를 받는 스크립트(`scripts/receive_audit.py` 또는 `run_deck_checks.py` — 구현 전에 어느 쪽이 뷰포트를 읽는지 확인).
- **Current behavior**: 423×308 증거가 저장돼 있다. 러너가 이를 거르는지는 NOT YET CHECKED.
- **Target behavior**: 뷰포트가 1280×720 미만이면 "미판정"으로 처리하고 PASS·FAIL 계수에 넣지 않는다.
- **Exact changes**: 먼저 현재 거동을 확인한다. 이미 거르면 이 Task는 닫는다.
- **Preserve**: 기존 9개 덱의 판정.
- **Do not change**: 감사 JSON 파일.
- **Dependency**: 없음.
- **Risk**: 기존 증거 중 하한 미달이 더 있으면 그 덱이 미판정으로 바뀐다(현재는 FRAME뿐이다).
- **Verification**: FRAME 증거로 "미판정" 1건, 나머지 8개 덱은 변화 없음.
- **Rollback**: 해당 스크립트 `git checkout`.
- **Priority**: P2.

### TASK-011 — 과목 지침 훅 주입을 세션당 1회로

- **Goal**: 같은 글의 반복 주입을 없앤다.
- **Evidence**: W1.
- **Files**: `scripts/hook_slide_guard.py`(`course`·`checklist` 모드), `tests/test_hook_guards.py`.
- **Current behavior**: 조건에 맞는 Edit·Write마다 주입한다.
- **Target behavior**: 세션 ID와 과목(또는 모드) 조합당 한 번만 주입한다.
- **Exact changes**: 훅 입력의 `session_id`를 키로 `tmp/hook-state/<session_id>.json`에 주입 기록을 남기고, 있으면 빈 출력으로 끝낸다. 구현 전에 훅 입력에 `session_id`가 오는지 실제 페이로드로 확인한다.
- **Preserve**: `css-lint`, `generated-guard`, `tmp-guard`의 동작. 첫 주입의 문구.
- **Do not change**: `.claude/settings.json` 배선.
- **Dependency**: A1 ablation의 기준선(TASK-012)을 먼저 잰다.
- **Risk**: 압축 뒤 첫 주입이 창에서 사라질 수 있다. 공식 문서에 훅 주입의 압축 후 처리가 적혀 있지 않다(§10). 대응: 압축 이벤트 뒤 1회 재주입할지는 A1 결과를 보고 정한다.
- **Verification**: 같은 shard를 3번 편집하는 테스트에서 주입 1회. `test_hook_guards.py` 통과.
- **Rollback**: 스크립트와 테스트 `git checkout`.
- **Priority**: P2.

### TASK-012 — Eval 기준선 측정

- **Goal**: 개편 전 값을 남긴다.
- **Evidence**: §14.
- **Files**: 신설 `plans/agent-system-audit/eval/`(과제 프롬프트 3개, 측정 스크립트, 결과표).
- **Current behavior**: 측정 스크립트가 `tmp/`에 있다.
- **Target behavior**: EV-1~EV-3을 현재 `main`에서 3회씩 돌린 결과표.
- **Exact changes**: 과제는 별도 worktree에서 돌린다(작업 트리의 FRAME 변경과 섞이지 않게).
- **Preserve**: 작업 트리.
- **Do not change**: 지침 파일.
- **Dependency**: TASK-001.
- **Risk**: 3회로는 분산이 크다. 결과표에 범위를 함께 적는다.
- **Verification**: 결과표에 조건·회차·metric 값이 빠짐없이 있다.
- **Rollback**: 폴더와 worktree 삭제.
- **Priority**: P1.

### TASK-013 — 개편 후 재측정

- **Goal**: TASK-004~007의 효과를 잰다.
- **Files**: `plans/agent-system-audit/eval/` 결과표에 추가.
- **Dependency**: TASK-006, TASK-012.
- **Verification**: 통과 기준 — EV-1에서 낡은 항목을 열린 것으로 말한 수가 줄고, EV-2·EV-3의 정답 판정이 기준선보다 나빠지지 않는다. 나빠지면 §17의 순서로 되돌린다.
- **Rollback**: 측정이므로 없음.
- **Priority**: P1.

### TASK-014 — 완료 과목 에이전트 정의 정리(사용자 확인 필요)

- **Goal**: 끝난 과목의 정의를 목록에서 내린다.
- **Evidence**: `feat/ac3-w2-prd-reorder`가 main에 병합돼 있다. 3차시 덱은 `eb588c1`에서 완성됐다. 정의 9개의 유사도가 높다.
- **Files**: `.claude/agents/ac3-*.md` 4개.
- **Current behavior**: 매 세션 에이전트 목록에 노출된다.
- **Target behavior**: 사용자가 AC3 종료를 확인하면 `_dev/설계기록/agents-archive/`로 옮긴다.
- **Do not change**: `frame-*.md`(진행 중인 과목이다).
- **Dependency**: 사용자 확인.
- **Risk**: AC3 재개 시 다시 필요하다. 옮기는 것이므로 복구할 수 있다.
- **Verification**: 새 세션의 에이전트 목록에 `ac3-*`가 없다. `verify_skill_setup.py` 종료코드 0.
- **Rollback**: 파일을 되옮긴다.
- **Priority**: P3.

### 명세에 넣지 않은 것과 이유

| 이전 보고서의 Task | 처리 | 이유 |
|---|---|---|
| `AGENTS.md`를 120줄로 축소 | 보류 | 효과 측정 없음. 저장소 지침은 기준선의 일부다 |
| R-QC-08에 SVG 포함 | 폐기 | C12·C13 |
| 리서치·검토·하네스를 목록에서 내림 | 폐기 | 절감 1,078자 |
| 관측 훅 2종 배선 해제 | 폐기 | 장부에 위반 137건 |
| 루트 `SKILL.md` 5k 분할 | 보류 | 9/8 이후 호출 2회. 분할의 효과를 잴 과제가 없다 |
| 하네스 한 쪽 축소 | 보류 | NEEDS EVAL |
| 예시 3장 선승인을 기본 관문으로 | 보류 | TEST FIRST. 신규 제작 품질을 잴 지표가 없다 |
| 기준선 구성 측정 | 사용자 몫으로 이관 | `/context`는 대화형 터미널에서만 된다(§18) |

---

## 16. Dependency Graph

```
TASK-001 Baseline
   ├─▶ TASK-002 MEMORY 스냅샷 ─▶ TASK-003 대조표 ─▶ TASK-004 STATE.md ─┬─▶ TASK-005 본문 이관 ─▶ TASK-006 읽기 지시 ─┐
   │                              (사용자 승인)                          └─▶ TASK-007 게이트                         │
   └─▶ TASK-012 Eval 기준선 ──────────────────────────────────────────────────────────────────────────────────────┴─▶ TASK-013 재측정
                    └─▶ TASK-011 훅 1회 주입

독립: TASK-008 불일치 정정 · TASK-009 FRAME FAIL 분류 · TASK-010 뷰포트 하한
사용자 확인 뒤: TASK-014
```

지시문의 기본 순서(Stage 0~6)와 다른 점
- Stage 1(Always-on / On-demand 분리)을 건너뛴다. 상시 층을 바꿀 측정 근거가 없다.
- Stage 6(Eval)의 기준선 측정을 Stage 2 앞으로 당겼다. 개편 뒤에는 "이전 값"을 잴 수 없다.
- Stage 5(Quality gates)는 FRAME 미커밋 작업과 묶여 있어 설계 문서(TASK-009)까지만 하고 구현은 사용자 결정 뒤로 뺐다.

사용자 결정이 선행돼야 하는 지점: TASK-003의 승인, FRAME 미커밋 파일의 처리(특히 `MEMORY.md`), TASK-014.

---

## 17. Rollback Strategy

- 복구 지점은 태그 `audit-baseline-2026-10-08`(커밋 `a979b42`)과 `MEMORY-스냅샷-2026-10-08.md`다. 태그는 커밋된 상태만 담는다. 작업 트리의 미커밋 변경은 태그에 없으므로, `MEMORY.md`의 미커밋 수정분은 스냅샷 파일이 유일한 사본이다.
- 되돌리는 순서는 적용의 역순이다: TASK-006(세 파일 checkout) → TASK-005(`MEMORY.md`를 스냅샷으로 복원, Archive 삭제) → TASK-007(함수·테스트 삭제) → TASK-004(`STATE.md` 삭제).
- TASK-004까지는 추가만 하므로 언제든 파일을 지우면 된다. 되돌리기 어려워지는 지점은 TASK-005다. 그 전에 TASK-003의 사용자 승인을 받는다.
- 되돌림 판단 기준: TASK-013에서 EV-2·EV-3의 정답 판정이 기준선보다 나빠지거나, TASK-005의 전수 대조에서 한 줄이라도 빠진다.
- 이 명세의 어떤 Task도 `git reset`, `git stash`, 브랜치 삭제, FRAME 파일의 checkout을 쓰지 않는다.

---

## 18. Remaining Unknowns

| # | 모르는 것 | 상태 | 판단에 필요한 것 |
|---|---|---|---|
| 1 | FRAME 결과물이 이전보다 품질이 높은가 | NOT VERIFIABLE | 사용자가 좋다고 본 장과 이유, 또는 렌더 화면의 블라인드 비교 |
| 2 | 품질 차이의 원인 | NOT VERIFIABLE | 1번이 먼저다 |
| 3 | 9/13~9/30의 작업 방식 | NOT VERIFIABLE | 그 작업을 한 PC의 세션 로그 |
| 4 | 기준선 중 로그에 없는 부분의 구성 | NOT VERIFIABLE(로그로는) | `/context` 출력 |
| 5 | `claude-opus-5`를 지금 고를 수 있는가 | NOT YET CHECKED | 모델 선택 화면 |
| 6 | 낡은 상태 서술이 실제 오판을 일으킨 사례 | NOT YET CHECKED | 세션 로그에서 낡은 항목을 근거로 한 행동을 찾는 조사 |
| 7 | 사람 프롬프트 유형 분포(교정 비율) | NOT YET CHECKED | 두 번째 판정자의 재분류 |
| 8 | `AGENTS.md` 블록별 필요성 | NOT YET CHECKED | 블록을 뺀 조건의 Eval |
| 9 | 문서 수치 충돌 5건(차트 수 등) | NOT YET CHECKED | 실제 값 계수(TASK-008에서 한다) |
| 10 | 규칙 255개 중 정본과 중복인 것 | PARTIALLY VERIFIED | 건별 대조. 워커 판정은 142건이고 그중 약 70건만 본문 확인 |
| 11 | Codex 세션 187개의 작업 내용 | NOT YET CHECKED | 로그 분석(1.35GB) |
| 12 | reviewer 워커·Opus 쓰기 워커의 품질 기여 | NOT VERIFIABLE(현재 자료로는) | ablation A2·A3 |
| 13 | 훅 주입이 규칙 준수를 실제로 높이는가 | NOT VERIFIABLE(현재 자료로는) | ablation A1 |
| 14 | 러너가 뷰포트 하한 미달 증거를 이미 거르는가 | NOT YET CHECKED | 스크립트 확인(TASK-010 첫 단계) |
| 15 | 훅 입력에 `session_id`가 오는가 | NOT YET CHECKED | 실제 페이로드 확인(TASK-011 첫 단계) |
| 16 | `/검토` 스킬의 산출물이 다른 이름으로 존재하는가 | NOT YET CHECKED | 스킬 문서의 산출 파일명 규약 확인 |

---

## 부록 — 재검증 원자료

| 내용 | 경로 |
|---|---|
| Git 기준 상태 | `tmp/audit-1008/git_baseline.txt` |
| 세션 로그 재측정 스크립트·결과 | `tmp/audit-1008/logs/`(`measure.py`, `rep1.py`~`rep3.py`, `codex.py`, `measure.pkl`) |
| `MEMORY.md` 49단위 분해, 모순 14쌍, 규칙 255개 판정 | `tmp/audit-1008/memory/`(`units.md`, `only_here.json`, `rule_hits.json`) |
| 덱 SVG 재계수 | `tmp/audit-1008/svg.py` |
| FRAME 커밋본 `verify_deck` 출력 | `tmp/audit-1008/vd_frame.txt` |
| `ui-ux-pro-max` 두 벌 md5 | `tmp/audit-1008/ux_claude.md5`, `ux_agents.md5` |
| OpenAI·Google 원문 사본 | `tmp/audit-1008/docs/` |

`tmp/`는 gitignore 대상이다. TASK-001이 필요한 파일을 `plans/agent-system-audit/baseline/`으로 옮긴다.
