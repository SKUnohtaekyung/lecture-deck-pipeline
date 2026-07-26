# BASELINE REPORT — CSR-2026-07 (TASK-P0-002)

## 1. 메타

| 항목 | 값 |
|---|---|
| Plan ID / version | `CSR-2026-07` v1.0.0 |
| 기록 일시 | 2026-07-26 |
| 브랜치 | `refactor/create-slides` (main에서 분기) |
| 시작 태그 | `refactor-p0-start` |
| 기준 커밋 | `eb49d2f` (content(2주차): 최종수정계획대로 초안 전면 재집필(phase-3)) |
| 기록 주체 | Opus (메인 오케스트레이터) |

## 2. 인터프리터 확정 ($PY)

| 항목 | 결과 |
|---|---|
| `.venv\Scripts\python.exe` | **없음** |
| 확정 `$PY` | 전역 `python` |
| 버전 | `3.12.10 (tags/v3.12.10:0cc8128, Apr 8 2025) [MSC v.1943 64 bit (AMD64)]` |
| 의존성 확인 | `python -c "import fontTools, PIL"` → 예외 없음 (**OK**) |
| 한글 출력 보전 | 전 명령 실행 전 `$env:PYTHONIOENCODING='utf-8'` 설정 |

이후 모든 Phase의 unittest·검증 명령은 동일하게 전역 `python`을 쓴다.

## 3. 명령별 결과 요약

| # | 명령 | 결과 | exit | 요지 |
|---|---|---|---:|---|
| ① | `python scripts/verify_skill_setup.py` | **FAIL** | 1 | FAIL 2 / PASS 77 (총 79검사). FAIL 2건 전부 메모리 사본 항목 (§7.8 예상과 일치) |
| ② | `python scripts/verify_kit.py` | **PASS** | 0 | FAIL 0 / PASS 6 · kit CSS 정의 클래스 444종 |
| ③ | `python scripts/verify_deck.py sessions/1주차/강의덱.html --parts 6` | **PASS** | 0 | FAIL 0 · WARN 0 · PASS 47 |
| ④ | `python -m unittest tests.test_deck_pipeline tests.test_image_pipeline` | **PASS** | 0 | Ran 25 tests — OK |
| ⑤ | `python scripts/verify_session_docs.py 2 --target 초안` | **FAIL** | 1 | FAIL 1 (`파일:초안.md — 파일 없음`) / PASS 1 — CONTRACT-002 기존 결함(기대값) |

### ①의 FAIL 2건 (원문)

```
FAIL | Codex·Claude MEMORY.md가 없거나 바이트 단위로 불일치
FAIL | Codex·Claude MEMORY.md가 없거나 SHA-256 불일치
RESULT | FAIL | 2개 실패
```

두 항목은 같은 원인(사본 분기)의 두 검사다. P1-001·002에서 포인터 규약으로 교체해 해소한다.

### ⑤의 FAIL 1건 (원문)

```
FAIL | 파일:초안.md — 파일 없음
--- FAIL=1 WARN=0 PASS=1 SKIP=0 ---
```

실물은 `sessions/2주차/2주차_초안.md`(접두어)로 존재한다. 검증기가 무접두어 `초안.md` 정확명만 탐색해 생기는 기존 결함이며 DEC-05·TASK-P3-007에서 해소한다.

## 4. 기존 결함 (§7.8 대조 결과)

| §7.8 항목 | 실측 확인 | 상태 |
|---|---|---|
| `verify_skill_setup.py` 메모리 바이트 동일성 검사 FAIL | **확인됨** — FAIL 2건 | 일치 |
| `.claude` 메모리와 `.agents` 메모리 분기 | **확인됨** — `.claude` 123줄/16,140B · `.agents` 159줄/29,288B · diff 37삽입/1수정 | 일치 |
| `.claude` 사본의 고유 정보 유무 | **고유 정보 0건** — 유일한 `<=` 차이 1줄(미해결 항목 4 "G8 관점 최소치")도 `.agents` 최신본의 구버전 | 일치 (P1-001 진행 조건 충족) |
| `.agents` 메모리 스테일: rgba 오탐 항목 | **확인됨** — `확진된 오탐 1건(2026-07-21)` 문자열 존재 | 일치 (P1-003 대상) |
| `.agents` 메모리 스테일: "편집본 80장·배포본 72장" | **확인됨** — `verify_deck.py 1주차 계약은 **편집본(`강의덱`)=80장 … 배포본=72장` 서술 존재. 실측·현행 코드는 75장·divider 6 | 일치 (P1-003 대상) |
| 1주차 실덱 기존 결함(PART 라벨·이미지 미배선·고아·revision.css 하향·노트 pn-no·666px 20장) | **verify_deck 현행 47검사로는 검출 0** (FAIL 0·WARN 0) — 해당 검사가 아직 없기 때문 | 일치 (P6에서 검증 신설·known_violations 등재 대상) |
| `evals/team-skills-eval.json` 픽스처 설명 스테일 | 미검사(P3-009에서 처리) | — |

## 5. 계획과의 차이

| 항목 | 계획(§7.8) | 실측 | 판정 |
|---|---|---|---|
| `.claude` 메모리 줄 수 | 123줄 | 123줄 | 일치 (줄 수는 Python `count('\n')` 기준. PowerShell `Get-Content .Count`는 119를 반환 — 계수 아티팩트이므로 이후 줄 수 측정은 Python 기준을 쓴다) |
| `.agents` 메모리 줄 수 | 159줄 | 159줄 | 일치 |
| ⑤ verify_session_docs 결과 | FAIL 기대 | FAIL(파일 없음) | 일치 |
| ③ verify_deck 1주차 | 기존 결함 존재하나 현행 검사로 미검출 | FAIL 0·WARN 0·PASS 47 | 일치 — 예상 밖 FAIL 없음(§P0 중단 조건 미해당) |

**중대 불일치 없음.** P0 중단 조건(§Phase P0 중단 조건)에 해당하지 않으므로 P1로 진행한다.

## 6. 회귀 기준본 (TASK-P0-003)

| 항목 | 값 |
|---|---|
| `<REGRESS>` | `C:\Users\miso\AppData\Local\Temp\cs-refactor-regress` |
| `baseline\강의덱.html` | 180,021 B (원본과 바이트 일치) |
| `baseline\강의덱_발표자노트.html` | 31,247 B (원본과 바이트 일치) |
| `work\sessions\1주차\강의덱.초안\` | 9파일 (원본 9파일과 일치) |
| `work\kit\` | 38파일 (원본 38파일과 일치) |
| 저장소 영향 | `git status --short`에 `sessions/1주차/` 0건 (DEC-06 준수) |

### 회귀 하네스 스모크 테스트 (P0에서 선행 확인)

P5-003·P7-001이 의존하는 절차를 착수 시점에 검증했다.

```
python scripts/assemble_deck.py <REGRESS>\work\sessions\1주차\강의덱.초안
  → parts merged: 5 · slide sections: 75 · part-divider sections: 6 · [PASS]
git diff --no-index <REGRESS>\baseline\강의덱.html <REGRESS>\work\sessions\1주차\강의덱.html
  → exit 0 (diff 없음)
```

**현행 shard로 재조립하면 1주차 덱이 바이트 동일하게 재생산된다.** P5·P7의 회귀 판정 기준(diff 0)이 유효함을 확인했다.

## 7. 부록 — 명령 원문 출력

원문은 `BASELINE_OUTPUTS.txt`에 명령별로 그대로 보존한다(요약·가공 없음).
