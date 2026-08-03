# AGENTS.md — create-slides 공통 작업 매뉴얼

> 구 명칭 `/vibecoding-deck`은 2026-07에 `/create-slides`로 개명됐다(DEC-01: 호환 alias 없음).

이 폴더는 **`create-slides` 스킬을 개발·보관**하는 프로젝트다. 루트 `SKILL.md`와 `kit/`·`references/`·`scripts/`가 플랫폼 공통 정본이며, `.agents/skills/create-slides/`와 `.claude/skills/create-slides/`는 이 정본을 로드하는 얇은 탐색 어댑터다. Codex는 이 파일을 직접 읽고, Claude Code는 루트 `CLAUDE.md`의 `@AGENTS.md` import로 같은 규칙을 읽는다. 변하는 현재 상태와 다음 할 일은 여기 두지 말고 `.agents/agent-memory/create-slides/MEMORY.md`의 `## 미해결`에 둔다. 이 파일은 작업 기록이나 변경 로그가 아니다: 새 규칙·반복 버그·인수인계 상태 중 **계속 유효한 것만** 남기며, 관련 작업을 마칠 때 에이전트가 해결 여부를 판정해 해결된 항목은 반드시 삭제한다.

## 구조 (섞지 말 것 · ①②③=스킬 3층, ④=작업물, ⑤=팀 스킬)

- **① 포터블 스킬(루트, 배포 대상)**: `SKILL.md`(진입점) · `kit/` · `references/` · `scripts/` · `입력양식/` · `데모_제작규칙.html` · `outputs/`(레이아웃 아틀라스). 사람용 개요는 `README.md`.
- **② 개발자료 `_dev/`(배포 제외)**: `설계기록/`(빌드·결정 기록 · `탐색-아카이브/` 미채택본). **커리큘럼·콘텐츠 원천은 `courses/<과목>/`로 이관**됨 — 상위 기준 `courses/바이브코딩/커리큘럼_기준안.md` + 주차 상세 `courses/<과목>/sessions/N주차/N주차_강의안설계.md`(옛 인수인계서 역할). `_dev/강의자료/`는 더 이상 쓰지 않는다.
- **③ 플랫폼 어댑터**: `.agents/skills/create-slides/`(Codex) · `.claude/skills/create-slides/`(Claude Code). 공통 규칙을 복제하지 않고 루트 `SKILL.md`만 로드한다. 누적 규칙·버그 정본은 `.agents/agent-memory/create-slides/MEMORY.md` 하나이며 Claude Code도 이 파일을 읽는다. `ui-ux-pro-max`만 각 플랫폼 탐색 위치에 실행 자원과 함께 둔다. `/리서치` 워커의 실행 통제(`Explore` + `sonnet` + 도구 허용목록 + 사후 감사)는 플랫폼마다 수단이 달라 `.claude/skills/리서치/SKILL.md`가 Claude 전용으로 규정하며, 조사 규칙 정본은 `skills/리서치/SKILL.md` 그대로다.
- **④ 주차별 작업물 `courses/<과목>/sessions/`(배포 제외)**: `N주차/`에 그 주차의 `N주차_초안.md`(레거시 무접두어 `초안.md`는 폴백 인식)·`강의덱.html`·`강의덱_발표자노트.html`·`자료/`. 루트 `sessions/`에는 과목 무관 스캐폴딩만 남는다(`_template/`·`_verify/`·`references/`·README) — 새 주차는 `sessions/_template/` 복사, 규약은 `sessions/README.md`. 구경로 `sessions/N주차`도 `scripts/_course_paths.py`가 계속 인식한다(1주차 동결 자료가 참조하므로 폴백 제거 금지). 1주차는 구세대 산출물만 폐기됐고 현행 산출물(초안·덱·노트)은 정본이며 **2026-07-26 사용자 결정으로 동결**됐다 — 수정·재조립하지 않는다.
- **⑤ 팀 워크플로 스킬 `skills/`(배포 제외)**: 강의 제작 팀 역할 스킬 2종(리서치·검토) + 횡단 오케스트레이션 프로토콜 하네스의 정본. ※ `콘텐츠`는 2026-08-03 폐기(실행 이력 0 · 집필은 create-slides가 흡수) — **사람이 초안을 써서 넘기는 경로와 그 스키마(`입력양식/콘텐츠초안템플릿.md`·`references/콘텐츠초안-입력형식.md`)는 살아 있다.** scripts/·sessions/ 규약에 하드 결합된 이식 불가 자산이라 포터블 스킬 배포 복사에서 제외한다. 등재·계약·호출 규약 정본은 `skills/README.md`.

> git으로 관리한다(2026-07-16 초기 커밋, 브랜치 `main`). 의미 있는 변경은 verify 통과 후 커밋해 복구 지점을 만든다. 설계 탐색 산출물 폐기는 관례대로 `_dev/설계기록/`(탐색-아카이브) 이동을 유지한다. 대규모 정리와 대량 갱신은 먼저 영향 범위를 확인한다.

## 작업 전 필수 읽기

1. `.agents/agent-memory/create-slides/MEMORY.md`의 `## 미해결`(현재 상태·다음 할 일)은 무조건 읽는다. 나머지(누적 규칙·하드윈 버그·색 시스템 정본)는 덱 조립·규칙 변경 작업 시 읽는다. 관련 작업을 끝내기 전에는 같은 파일을 다시 확인해, 해결된 미해결 항목과 더는 유효하지 않은 규칙·버그·인수인계 내용을 **반드시 삭제**하고 계속 유효한 내용만 남긴다.
2. 배경이 필요할 때 `_dev/설계기록/구조-및-빌드-기록.md`를 읽는다.
3. `skills/README.md` — 팀 워크플로 스킬(`$리서치`·`$검토`·`$하네스`) 호출 시 계약표·파이프라인 지도·명시 호출 규약을 확인한다.
4. 커리큘럼(`courses/바이브코딩/커리큘럼_기준안.md` + `courses/<과목>/sessions/N주차/N주차_강의안설계.md`) — 해당 주차 파일을 열거나 쓰기 전에, 그 주차 것만 읽는다.
5. 덱 조립·리뷰 요청이면 루트 `SKILL.md`를 적용하고 그 안의 read-path를 순서대로 따른다.
6. `sessions/README.md` — 새 주차 폴더를 만들 때 읽는다.

## 플랫폼별 Skill 호출

- **Codex**: `.agents/skills/create-slides/SKILL.md`가 발견된다. `$create-slides`로 명시 호출하거나 PPT·강의덱·HTML 웹덱 제작 요청으로 자동 호출한다.
- **Claude Code**: `.claude/skills/create-slides/SKILL.md`가 발견된다. `/create-slides`로 명시 호출하거나 같은 자연어 요청으로 자동 호출한다.
- 두 어댑터는 반드시 루트 `SKILL.md`를 완전히 읽고, 그 안의 상대 경로를 저장소 루트 기준으로 해석한다. 어댑터에 디자인 규칙이나 워크플로를 복제하지 않는다.
- 팀 워크플로 스킬 2종(`/리서치`·`/검토`)은 **명시 호출 전용**이다(자동 발동 없음 — "명시 호출"의 정의는 `skills/README.md`가 정본). create-slides만 기존대로 자동 발동을 유지한다. 파이프라인 순서: `/리서치` → `/create-slides`(집필+조립 · 초안이 있으면 ⓐ, 없으면 ⓑ) → `/검토`(횡단).

## 스킬의 역할

채워진 콘텐츠 초안(교시별 표·본문·강사 멘트)을 1280×720 HTML 웹덱으로 조립한다. 대상은 코딩 경험이 없는 입문자 중심의 혼합군이다. 정보 모양을 먼저 판단해 레이아웃과 차트를 고르고, 좌우분할 한 구도로 쏠리지 않게 한다. 이미지보다 코드 시각화를 우선한다. 초안의 제목과 본문을 존중하며 무단 재작성·분할하지 않는다. 강사 멘트가 있으면 발표자 노트 HTML도 별도로 만든다.

## 불변 규칙

디자인 불변 규칙 정본은 `kit/guide/디자인시스템.md`(R-COLOR-01~05·R-EMPH-01·R-TERM-01)와 `kit/guide/토큰-치트시트.md`(R-TYPE-01~03)다. 아래는 요지 색인이며, 어긋나면 정본을 따른다.

- 색은 토큰만 사용한다(raw `#hex`·navy·그라데이션 금지, 흰색은 `var(--white)`) — R-COLOR-01
- 민트·코랄 fill 위에 흰 글자를 쓰지 않는다(`--on-mint`·`--on-coral`) — R-COLOR-02
- 민트 fill 번호 배지는 `.num-circle`·`.work-step .n`·`.pd-dot.is-active` 셋뿐, 다른 노드는 블루 — R-COLOR-03
- 카드/박스 표면은 흰색-온-흰색 금지(흰 fill + `--line` 단독 보더는 verify FAIL, `--line`은 내부 구분선 전용) — R-COLOR-04
- 원형 배지+텍스트 행(`.work-step`·`.agenda-item`)은 텍스트를 배지 기준 수직 중앙에 둔다 — `references/조립-리듬-불변요소.md`
- 조립 전에 `정보 모양 분류 → 역인덱스 → 레이아웃과 element를 별도 선택` 순서를 따르고, 직전 슬라이드와 같은 구도를 피하며 split 계열을 희소하게 쓴다 — R-LAYOUT-01·02(루트 `SKILL.md`)
- 상세·최신 규칙은 `.agents/agent-memory/create-slides/MEMORY.md`를 정본으로 삼는다.

## 실행과 검증

```powershell
python scripts/assemble_deck.py courses/<과목>/sessions/N주차/강의덱.초안   # shard → 강의덱.html 재생성(덮어씀)
python scripts/verify_deck.py <덱>.html --parts N   # N = 그 덱의 part-divider 수(슬라이드 총수 아님 — 1·2주차 모두 6)
python -m http.server
python scripts/inline_deck.py <덱>.html --offline
# Codex
python .agents/skills/ui-ux-pro-max/scripts/search.py ...
# Claude Code
python .claude/skills/ui-ux-pro-max/scripts/search.py ...
python scripts/verify_skill_setup.py
python scripts/verify_kit.py
python scripts/verify_subject_isolation.py   # 스킬 본문에 과목 고유 값이 남아 있으면 FAIL
python scripts/verify_required_statements.py <주차>   # 개념KB 필수 진술이 덱 화면에 남았는가(기본 WARN·--strict FAIL)
python scripts/verify_judgement_log.py <주차>         # 집필노트 판단 기록 정합(D2 근거·처분값·필수 보류 금지)
python -m unittest tests.test_deck_pipeline tests.test_image_pipeline tests.test_quality_gates
# 파이프라인 문서 게이트(리서치·콘텐츠 산출물)
python scripts/verify_session_docs.py <주차> --target 자료   # 기본 5파일 스키마·출처ID·[C-슬러그] 해소
python scripts/verify_research_chunks.py <주차>              # 개념KB 청크 깊이·G8 관점·인덱스 일치
python scripts/analyze_agent_usage.py --tool-audit --session <세션ID>  # 리서치 워커 도구·모델 감사(0 통과 / 3 위반)
# 내용 품질 게이트(WARN 기본·--strict로 FAIL 승격 — 2주차 저밀도 사고 이후 신설, 회귀 아님)
python scripts/verify_draft_quality.py <주차>                # .md 초안 단계: 저밀도·노트과다·교시당 장수·필수 산출물
python scripts/verify_deck_quality.py <덱>.html              # 조립된 덱 단계: 저밀도·근-빈 컨테이너·시각자료 비율·부록 강등
# ★ 덱 검증 러너 — 조립 이후 검사를 한 명령으로 잇는다(렌더 증거 없으면 exit 1)
python scripts/run_deck_checks.py <주차>            # 정적 게이트 + 노트 + 렌더 증거 판정
python scripts/run_deck_checks.py <주차> --assemble --parts N
python scripts/check_title_survival.py <주차>       # 초안 제목이 덱 화면에 살아남았는가(참고)
# 브라우저 렌더 감사(필수 — 종료코드가 못 보는 것을 잡는다)
#   python -m http.server 8799 후 브라우저에서 덱을 열고 콘솔에서:
#     await (await fetch('/scripts/audit_all.js')).text().then(eval)
#   → 출력 JSON을 sessions/_verify/<주차>/deck-audit.json 으로 저장하면
#     run_deck_checks.py가 그것을 증거로 판정한다(없으면 통과시키지 않는다).
#   ⚠️ 창을 1280x720 이상으로 열어라. 작으면 덱 JS가 --scale을 0으로 계산해 전 장이
#      0으로 나오고, 그 상태의 「결함 0」을 통과로 오판한 사고가 있다(2026-08-03 재현).
#      이제 두 감사기가 fail-closed assert로 막고 { INVALID:[...] }를 돌려준다.
#   audit_render.js  잉크 점유율 · 바닥선(666) 초과 · 슬라이드(720) 이탈 · 요소 겹침 ·
#                    단어 중간 줄바꿈 · 박스면적÷글자수 · 빈 asset-slot · 껍데기 컨테이너
#   audit_typography.js  역할별 폰트 하한 · 자간 광학 보정 누락(≥32px) ·
#                    행간 normal 잔존 · 근-미스 앵커(지배값 ±1~5px)
#   audit_all.js     위 둘을 함께 돌려 러너용 압축 증거를 만든다
```

- ⚠️ **종료코드가 통과했다고 화면이 멀쩡한 것이 아니다.** 2026-07-31 사고: `verify_deck`·
  `verify_deck_quality`가 FAIL 0으로 통과한 덱에서 실제로는 단어 중간 줄바꿈 250건,
  한 문장이 48px 칸에 갇힌 사례 13건, 22px 하한 미만 242건, 슬라이드 밖으로 480px
  밀려난 요소, 빈 이미지 슬롯 24개가 화면에 있었다. **조립 후에는 반드시 브라우저에서
  `scripts/audit_render.js`를 돌려 전수 측정한다.** 정적 검사로 승격할 수 있는 것은
  `R-QC-18`(빈 슬롯)·`R-QC-19`(격자 안 맨 텍스트)로 `verify_deck_quality.py`에 넣었다.
- ⚠️ **검출기의 「0」이 눈먼 범위 안의 0일 수 있다.** 2026-08-03 규명: `audit_render.js`가
  ① `hasOwnText` 조건 때문에 `<img>`·`<figure>`·`<svg>`를 바닥선·이탈 검사에서 **통째로
  빼고** ② 겹침을 `.s-full` 2단계까지만 봐서 최소 17장은 아예 검사하지 않았다. 둘 다 고친
  뒤 재측정하니 1주차 바닥선 초과가 **17 → 25건**으로 늘었다(전부 이미지 계열). 검사 범위를
  넓힐 때는 **오탐률을 함께 재라** — 겹침 검사를 깊이만 풀었더니 2주차에서 잡힌 7건이 전부
  오탐이어서(인라인 요소의 합집합 상자), 인라인 제외 + 절대배치 분리로 좁혀야 했다.
- **덱을 고쳤으면 `run_deck_checks.py`를 돌려라.** 렌더 증거가 없거나·덱보다 낡았거나·
  INVALID면 종료코드 1이다. 「필수」를 사람 기억에 맡기지 않기 위한 장치다.

- ⚠️ **`courses/<과목>/sessions/N주차/강의덱.html`은 생성물이다.** 정본은 `강의덱.초안/`의 `shell.html`(head·고정 슬라이드·`<!-- ::PARTS:: -->` 마커·JS) + `part-NN.html`이고, `assemble_deck.py`가 이를 합쳐 덱을 **덮어쓴다**. 덱을 직접 고치면 다음 조립 때 유실되고, 생성물에만 있는 슬라이드는 조립 즉시 사라진다. 수정은 shard에 하고 조립한다(급히 덱을 고쳤다면 같은 내용을 shard에도 반영). 규약 상세는 `sessions/README.md`.
- 생성물과 shard가 어긋났다면 shard를 하나씩 맞추지 말고, 완성된 `강의덱.html`을 파트 경계로 잘라 shard를 재생성한 뒤 조립 결과를 조립 전 사본과 diff해 검증한다. 조립 전에는 반드시 현재 덱 사본을 떠둔다.
- 브라우저는 `deck.css`를 캐시하므로 변경 확인 때 링크의 `href`에 `?v=`를 붙인다.
- `file://`로 검증하지 말고 로컬 HTTP 서버를 사용한다.
- 스크린샷보다 JS 측정(`scrollHeight`, computed style)을 우선한다.
- `.hint-reveal`은 닫힘과 강제 열림 상태를 모두 검사한다.
- 카탈로그나 `SKILL.md`를 바꾸면 `evals/evals.json`과 `evals/trigger-eval.json`으로 회귀를 확인한다.
- 위 unittest는 `fontTools`·`Pillow`가 설치된 인터프리터로 실행한다(의존 정본 `requirements-dev.txt`). Windows 로컬에서는 보통 `.venv\Scripts\python.exe`.

## 공통 작업 방식

- 텍스트와 파일 탐색은 `rg`/`rg --files`를 우선한다.
- **임시·중간 파일은 저장소 안 `tmp/`에만 만든다.** 시스템 임시 폴더(`%TEMP%`·`AppData`·플랫폼 스크래치패드)에 작업 스크립트·측정 결과·캡처를 두지 않는다. `tmp/`는 이미 `.gitignore`에 있다. **서브에이전트에게도 이 제약을 프롬프트에 명시해 전달한다** — 지시하지 않으면 각자 시스템 임시 폴더를 쓴다(2026-07-30 실제 발생: 워커 4개가 전부 밖에 썼다). 작업 종료 시 밖에 남은 파일이 **0개인지 세어 확인한다**. 옮기는 것은 정리가 아니다.
- 기존 사용자 변경을 보존하고, 무관한 파일을 되돌리거나 정리하지 않는다.
- 구현 요청은 수정 후 정적 검증과 가능한 범위의 브라우저 측정을 수행한다.
- **하네스(실질 작업의 기본 방식)**: 다파일·독립 구간·대규모 작업(스킬·계약 재설계, 40장+ 덱, 여러 파일에 걸친 규칙 변경)은 기본으로 하네스로 수행한다. **단일 파일·사소한 편집·조회는 solo로 한다** — 하네스를 걸지 않는다.
  - ⚠️ **비용 절감 도구가 아니다** — 품질·컨텍스트 보존 도구다. 워커는 메인과 컨텍스트를 공유하지 않아 같은 파일을 각자 다시 읽고 총 토큰이 늘 수 있다(실측 근거는 정본 §0).
  - 명분·스케일 사다리·역할 계약·게이트 기준·워커 규율·안티패턴 상세 정본: `skills/하네스/SKILL.md`(명시 호출 `/하네스`·`$하네스`).
- 웹 리서치가 필요한 사실은 검색 후 원문 출처를 확인한다. 외부 쓰기나 게시·전송은 사용자 요청 범위를 넘겨 실행하지 않는다.

## 과목 프로필 (2026-07-29 신설)

- **스킬 본문에는 과목 고유 값을 두지 않는다.** 강의명·대상·관통 문장·회차 구조·장수/밀도 기준선·표현 취향·브랜드·커리큘럼 정본 경로는 전부 `courses/<과목>/profile.md`에 있다(스키마 `입력양식/과목프로필템플릿.md`).
- **한 과목의 실측치를 다른 과목의 규칙으로 물려주지 않는다.** 기준선이 없는 새 과목은 FAIL이 아니라 **WARN으로 시작**한다.
- 사고 이력·실측치는 규칙의 **근거**이므로 스킬에 남긴다 — 격리 대상은 운영 파라미터뿐이다.
- 검사: `python scripts/verify_subject_isolation.py` (프로필 §8이 등재한 리터럴이 스킬 본문에 있으면 FAIL).

## 판단 기준과 파일 지도

- 판단축: `kit/guide/정보모양-taxonomy.md`
- 카탈로그 규칙: `kit/guide/카탈로그-규격.md`
- 토큰·계산식: `kit/guide/토큰-치트시트.md`
- 색·폼 정본: `kit/guide/디자인시스템.md` (설계 배경: `_dev/설계기록/색시스템-v2-명세.md` — 역사 기록)
- 레이아웃: `kit/layouts/`(50) + `by-shape.md` + `catalog.html`
- 차트·다이어그램 element: `kit/charts/`(23) + `by-shape.md` + `catalog.html`
- 코드 코어: `kit/styles/patterns.css`, `kit/styles/deck.css`
- 스타터: `kit/starter/deck-template.html`, `kit/starter/presenter-notes-template.html`
