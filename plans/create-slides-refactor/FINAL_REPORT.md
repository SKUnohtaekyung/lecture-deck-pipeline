# /create-slides 리팩토링 최종 보고

- **계획 버전**: CSR-2026-07 v1.0.0 / **완료 Phase**: P0~P7 (8/8)
- **브랜치**: `refactor/create-slides` (main 미병합·미push)
- **최종 커밋**: `907a634` + 본 보고 커밋
- **작성일**: 2026-07-26

---

## 1. 변경 규모

`git diff main --shortstat` = **81 files changed, 4,902 insertions(+), 596 deletions(-)**

| 구분 | 수 | 비고 |
|---|---:|---|
| 수정(M) | 45 | 계획 예상 49파일 이내 |
| 신규(A) | 30 | phases 9 · 계획 산출물 5 · 스크립트 3 · 테스트 1 · 픽스처 9 · 어댑터 재배치 2 |
| 이동(R) | 4 | 아래 표 |
| 삭제(D) | 2 | **실제 삭제 아님** — 유사도가 낮아 git이 rename으로 짝짓지 못한 이동의 구경로(`openai.yaml`, `.claude` 메모리 사본→3줄 포인터) |

### 이동 4건
| 구경로 | 신경로 | 유사도 |
|---|---|---|
| `.claude/skills/vibecoding-deck/SKILL.md` | `.claude/skills/create-slides/SKILL.md` | 99% |
| `.agents/skills/vibecoding-deck/SKILL.md` | `.agents/skills/create-slides/SKILL.md` | 98% |
| `.agents/agent-memory/vibecoding-deck/MEMORY.md` | `.agents/agent-memory/create-slides/MEMORY.md` | 72% |
| `outputs/vibecoding-deck-layout-atlas.html` | `outputs/create-slides-layout-atlas.html` | 100%(내용 무변경) |

---

## 2. 해결한 문제 ID

| 분류 | ID | 결과 |
|---|---|---|
| 개명 | NAME-001·002·003 | 기능·문서 참조 전량 교체. 잔존은 허용 목록(역사 기록)뿐 |
| 개명 보존 | NAME-004 | `_dev/**`·`sessions/**`·`kit/CHANGELOG.md` 역사 기록 무오염 |
| 중복 | DUP-001 | 규칙 본문 중복 0 — RULE_MIGRATION_MAP 42항 대조 OK |
| 충돌 | CONFLICT-001~006 | 6건 전부 해소(001~005는 P3, 006은 P4) |
| 메모리 | MEMORY-001·002·003 | 포인터 규약 전환 · 스테일 2건 정정 · 3분할(159→138줄) |
| 로드 | LOAD-001·002·003 | Core Contract화 + phases/ 9파일 조건부 로드 |
| 계약 | CONTRACT-001·002 | 1주차 계보 정정 · 초안 접두어 규약 공식화 |
| 구조 | STRUCT-001·002 | `--fs-*` 9종 정의 · `.terminal-dark` kit 승격 |
| 검증 | VERIFY-001~006 | 렌더 측정·계약 외부화·`--parts` 자기참조·초안 diff·노트 정합·eval 픽스처 |
| 관찰 | OBS-01~10 | 규칙 통합 또는 검증 신설로 처리(§9 추적표대로) |

**미해결 0건.** 범위 밖으로 명시 분리한 항목은 §6.

---

## 3. 검증 결과 (P7 재실행 기준)

| 검증 | 기준선(P0) | 최종(P7) | 판정 |
|---|---|---|---|
| `verify_skill_setup.py` | PASS 77 / **FAIL 2** | **PASS 78 / FAIL 0** | 개선(기준선 결함 해소) |
| `verify_kit.py` | PASS | PASS | 동등 |
| `verify_deck.py` 1주차 | FAIL 0 · WARN 0 · PASS 47 | **FAIL 0 · WARN 5 · PASS 51** | 동등 + 검사 4종 신설 |
| `verify_session_docs.py 2 --target 초안` | **FAIL 1** / PASS 1 | **PASS 8 / FAIL 0** | 개선 |
| `verify_session_docs.py 2 --target 자료` | — | PASS 32 / FAIL 0 / SKIP 1 | 정상 |
| `unittest` | 25 tests OK | **36 tests OK** | 동등 + 11건 신설 |

**1주차 신규 WARN 5건은 전부 기존 결함의 "검출"이며 회귀가 아니다** — 계약의 `known_violations`에 등재돼 FAIL이 아닌 WARN으로 나온다. 같은 결함이 신규 주차에서는 FAIL로 작동함을 고장 픽스처로 확인했다.

### 회귀 (§18 3축)
- **P7-001 1주차 재조립**: 최신 `kit/`·`scripts/`로 저장소 밖 임시 폴더에서 재조립 → 착수 전 기준선과 **`git diff --no-index` = 0**. P5의 kit 변경이 렌더 결과를 바꾸지 않음이 확인됨.
- **P7-002 구조 회귀**: 위 표 전 항목 기대값 일치.
- **P7-003 수동 회귀**: `SKILL.md` frontmatter diff가 **`name:` 한 줄뿐 — description 완전 무변경**(자동 발동 트리거 보존). 런타임 확인: 이 세션의 사용 가능 스킬 목록에 `create-slides`가 동일 description으로 등재되고 `vibecoding-deck`은 사라졌다. evals 3파일 구명 잔존 0·케이스 수 불변.

### 신규 fixture 결과
`tests.test_deck_contract` = **11 tests OK**
- 계약 3단 탐색(동폴더 인식 · `sessions/_contracts` 폴백 · 부재 시 **WARN**이고 FAIL 아님)
- `broken/part-01.html` → PART 라벨 불일치 **FAIL 재현**
- `broken/unwired.json` → 배선 누락 **FAIL 재현** + 고아 **WARN 재현**
- `resolve_draft` 접두어 우선 / 레거시 폴백(INFO)

픽스처는 1주차 파일을 복사·참조하지 않는 독립 저작물이며, 문안은 전부 placeholder다(과적합·동결 준수).

---

## 4. 토큰·로드량 전후 (V-22)

| 구분 | 기준선(p0 실측) | 최종 | 감축 |
|---|---:|---:|---:|
| 항상-로드 집합 | **229,530 B (224.2 KB)** · 15파일 | **49,998 B (48.8 KB)** · 4파일 | **78.2%** |

구 `SKILL.md`는 "조립 전 항상 필수(★)" 6파일을 지정했다. 신 Core Contract는 **★ 지정이 0건**이고, 모든 규칙 문서를 9단계 게이트 지도에서 단계별로 지목한다. 무조건 로드되는 것은 엔트리 4파일(`CLAUDE.md`·`AGENTS.md`·`MEMORY.md`·`SKILL.md`)뿐이다.

- `SKILL.md` 38,585 B → **12,786 B** (66.9% 감소)
- `MEMORY.md` 29,288 B → **22,852 B** (3분할·승격·동결 정리)

목표 40% 대비 **78.2%**로 크게 상회.

---

## 5. 보존한 기존 결함 (수정하지 않음 — DEC-06 동결)

`sessions/_contracts/1주차.deck.contract.json`의 `known_violations`에 등재해 **검출만** 한다.

| 항목 | 실측 | 비고 |
|---|---|---|
| PART 라벨 불일치 | **15장** | 계획 최초 추정 4장 → 실측 15장으로 정정 |
| 이미지 배선 누락(ready) | 2장 (`29`·`30`) | |
| manifest 고아 | **14건** | 계획 최초 추정 4건 → 실측 14건으로 정정 |
| 세션 CSS 22px 미만 | 3 셀렉터 | 의도된 20px 위계 포함 |
| 발표자 노트 pn-no 불일치 | **36건 (exit 1)** | 계획의 "구버전 의심"이 **확정**됨 — 27번 이후 전 구간에서 노트 `pn-no` N의 제목이 덱 N−1과 일치하는 일관된 한 칸 밀림 |
| 하단 666px 초과 20장 | 미측정 | 동결·기지 결함이라 이번 실행에서 재측정하지 않음(V-16 단서대로) |

---

## 6. 후속 작업 (이번 실행 범위 밖)

1. `GPT_강의설계_보조에이전트/` 파생 사본(untracked, md 10개)의 규칙 갱신 검토 — 정본이 크게 바뀌었으므로 대조 필요
2. D3 벤더 파일(`kit/vendor/d3.min.js`) — 첫 실수요 시(DEC-08)
3. `--fs-*` 소급 치환 — 이번엔 정의만 추가, 기존 선언 무변경
4. `skills/콘텐츠/SKILL.md`에 "정의→쉬운 설명→비유" 순서 규칙(CONTENT-001 상류 해법 — 팀 결정)
5. `kit/layouts/families/*.md` 5파일의 폰트·밀도 인용(27px·44px·548px) 정정
6. **1주차 발표자 노트 pn-no 한 칸 밀림** — 동결 해제 시 `verify_notes.py`로 재대조 후 일괄 재번호

---

## 7. 계획과 실제의 차이 (전량)

| # | 항목 | 처리 |
|---|---|---|
| 1 | **PART 정합 검사의 전제 오류** — 계획은 정적 `.s-team` 라벨이 화면에 표시된다고 보았으나, 덱 JS가 런타임에 위치 인덱스로 덮어쓴다(`강의덱.html:1323-1324`). 라벨 불일치는 시각 결함이 아니라 소스 불일치다 | **사용자 결정**으로 계획 정의(위치 인덱스) 유지 + 1주차 15장 실측 등재. 계약에 판정 근거를 `note`로 명시 |
| 2 | `chk(True, …, warn=True)` 스케치가 실제로는 PASS를 냄 | `chk(False, …, warn=True)`로 교정 — 계약 부재가 실제 WARN이 되게 |
| 3 | 계약 JSON의 `강의덱_배포` 항목이 계획보다 넓음 | 현행 코드가 터미널·THANK YOU를 두 stem 모두에 적용하므로 "현행 값 기계 이전" 원칙을 우선 |
| 4 | `known_violations` 실측치가 계획 추정과 다름(라벨 4→15, 고아 4→14) | 실측값으로 등재 + 차이를 `note`에 기록 |
| 5 | 고장 픽스처 사양 | 계획 스케치(`divider P1→P3`, `덱에 없는 slide_id`)는 각각 단조증가 통과·고아 WARN 경로라 **FAIL을 재현하지 못한다**. 재현 대상이 FAIL이므로 라벨 불일치·미배선으로 바꿔 구성하고 파일 주석에 사유 기록 |
| 6 | 픽스처 슬라이드 수 | 계획 스케치 8 → 실제 **12**(고정 슬라이드 4장을 포함한 현실적 최소 덱) |
| 7 | `verify_notes.py` 제목 비교 오탐 | 워커 초판이 `<br>`·`PART n ·` 접두어·`·` 구분자를 정규화하지 않아 오탐 3건 발생 → Opus가 비교용 정규화 추가(표시 문자열은 원문 유지) |
| 8 | **P6-005~007 워커 실행이 API 세션 한도로 중단** | Opus가 직접 완료. P7-004 독립 검증도 워커 대신 Opus가 읽기 전용 명령으로 수행 — **§13 워커 배치와 다른 유일한 실행상 차이**이며, 검증 명령·기준은 계획 그대로 |
| 9 | `.claude` 메모리 사본 줄 수 | 계획 123줄 → 실측 119줄(고유 정보 0건은 계획대로) |

**계획 밖 파일 수정 0건.** `_dev/` 변경 1건은 계획이 명시한 유일한 예외(색시스템v2 배너, TASK-P3-005).

---

## 8. §22 최종 완료 기준 체크

| # | 기준 | 결과 |
|---|---|---|
| ① | DEC-01~08 전부 반영 | ✅ 8/8 |
| ② | §9 문제·관찰 ID 전량 처리 기록 | ✅ §2 |
| ③ | R-* 32종 정본 연결(V-06) | ✅ RULE_MIGRATION_MAP 대조 OK |
| ④ | 계획 밖 변경 0(V-26) | ✅ |
| ⑤ | 정본 단일화·중복 본문 0(V-06) | ✅ |
| ⑥ | 충돌 규칙 0(V-07) | ✅ 6/6 해소 |
| ⑦ | 이름 참조 누락 0(V-02) | ✅ 누락군 0건 |
| ⑧ | 어댑터 정합(V-01·03·04) | ✅ (Codex 스모크는 관례대로 미실시 기록) |
| ⑨ | 기존 테스트 전 PASS(V-24) | ✅ 25→36 OK |
| ⑩ | 신규 fixture 전 PASS(V-25) | ✅ 11 OK |
| ⑪ | 1주차 신규 회귀 0(V-13·P7-001) | ✅ diff 0 |
| ⑫ | 토큰·로드 측정 기록(V-22) | ✅ 78.2% |
| ⑬ | Opus 최종 diff 검토 완료 | ✅ |
| ⑭ | 독립 검증 결과 검토(P7-004) | ✅ (실행 주체 차이는 §7-8) |
| ⑮ | push·merge 미실행 | ✅ |

---

## 9. 롤백 가능 지점

`refactor-p0-start` · `p1` · `p2` · `p3` · `p4` · `p5` · `p6` · `p7-start` (8개 태그)

| 커밋 | Phase |
|---|---|
| `b551fad` | P0 기준선 |
| `1165a9a` | P1 기준선 수리 |
| `93aa644` | P2 개명 |
| `82ac406` | P3 정본화·충돌 해소 |
| `84fe173` | P5 컴포넌트 |
| `b04dde2` | P4 Core·로드 재편 |
| `907a634` | P6 검증 신설 |

전체 폐기 시 `git checkout main` (브랜치는 보존 — 삭제는 사용자 결정).

---

## 10. 사용자 승인 필요 항목

1. **`main` 병합** — 미실행
2. **`push`** — 미실행
3. **브랜치 처분**(병합 후 삭제 여부)

> 계획 §19대로 push·merge는 사용자 명시 승인 전까지 실행하지 않는다. 현재 모든 변경은 `refactor/create-slides` 브랜치에만 존재한다.
