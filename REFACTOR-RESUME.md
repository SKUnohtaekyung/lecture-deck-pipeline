# ⚠️ 이 워크트리는 `/리서치` 스킬 리팩터링 전용이다

이 디렉터리는 `C:\Users\miso\Desktop\template` 저장소의 **git worktree**다.
브랜치: `refactor/research-skill` · 기준선: `3d0bba5`

## 시작하기 전에 — 반드시 전문을 읽어라

```
C:\Users\miso\.claude\plans\spicy-baking-hammock.md
```

**요약본이나 이 파일로 대체하지 마라.** 계획 파일에만 있는 것:

- 「⏱ 재개 지점」 — 현재 Phase·커밋 SHA·다음 할 일
- 「📜 무인 실행 지시」 — 승인 범위, Phase 게이트 절차, **GREEN/YELLOW/RED 판정 기준**, 자율 판단 원칙, Phase 2~8 각각의 요구사항, 커밋 규칙, **전체 중단 조건**, 최종 보고 형식
- 「🚫 하드 제약」 — 절대 변경 금지 계약(G1~G9 · 기본 5파일 · `C-슬러그` · `S-###` · 하류 스킬 계약)
- 「📊 잠정 기준선」 — 부분 검증 완료 상태와 정정 이력
- 「⚙️ 환경 사실」 — Claude Code 2.1.207에서 검증된 것과 미검증인 것의 구분

## 절대 규칙 (세부는 계획 파일)

| 금지 | 이유 |
|---|---|
| 원본 `C:\Users\miso\Desktop\template` 수정 | 사용자가 거기서 1주차 덱을 작업 중이다. 읽기 전용 비교 대상 |
| `main` 병합 · `git push` | 승인되지 않았다 |
| `git reset`·`checkout --`·`restore`·`clean`·강제 삭제 | 사용자 작업 손실 위험 |
| 기존 1·2주차 리서치 전체 재실행 | 승인되지 않았다 |
| G1~G9 완화 · 기본 5파일 계약 변경 | 별도 사용자 승인 필요 |
| 미검증 Claude Code 기능 사용 | 2.1.207 기준으로 더미 실행 확인이 선행돼야 한다 |

## 현재 상태

| Phase | 판정 | 커밋 |
|---|---|---|
| 0 작업 격리 | GREEN | — |
| 1 계측 마감 | GREEN | `0f59fe9` |
| 1.5-B 캘리브레이션 | **YELLOW** | `f9f2430` |
| 2 워커 실행 통제 | GREEN | `3cb8027` |
| 3 실행 예산 | GREEN | `6592bf5` |
| 4 컨텍스트·반환 | GREEN | `58e9c5a` |
| 5 SKILL 정본 분리 + 6 회귀 검증 | GREEN | `b1315cc` |
| 7 smoke test (3청크) | **YELLOW** | `83a63d9` |
| **8 확대 검증·판정** | **← 다음 · Phase 7 GREEN이 전제(계획 J절)** | |

## Phase 8 착수 전 사용자 결정

**Phase 7이 YELLOW라 계획 J절상 Phase 8은 아직 열리지 않는다.** 아래 중 하나를 정해야 한다.

1. **YELLOW를 수용하고 Phase 8 진행** — 잔여 사유는 ① 수정된 허용목록으로 처음부터 다시 돌린
   clean run이 없음 ② 동일 URL 재호출 위반 1건(자연어 강제의 한계) ③ 정량 중단선은 이번에도 미도달.
2. **clean run 1회 재실행 후 GREEN 판정** — 비용 약 **4M 처리 토큰**(3청크 기준).
3. **워커 실행 수단 재검토** — `Explore`는 `Bash`·`PowerShell`을 실제로 보유해 허용목록을
   구조적으로 강제하지 못한다(감사로만 검출). `claude-code-guide`는 도구가 정확히 5개로 일치하나
   시스템 프롬프트가 Claude Code 질문용이라 주제 편향 위험이 있다.

미해소로 남은 결함: **D2 워커 턴 상한** — `maxTurns`는 `.claude/agents/` frontmatter 전용이라
이 실행 경로에 없다. §0.5 중단선 + 사후 감사로만 관측한다.

상세 근거: `_dev/설계기록/Phase7-smoke-test-기록.md` · `_dev/설계기록/Phase2-워커실행통제-검증절차.md`

## 검증 명령

```bash
python tests/test_analyze_agent_usage.py            # 계측기 자체 검증 26 PASS
python scripts/analyze_agent_usage.py               # exit 0 = 기준선 대조 통과
python scripts/analyze_agent_usage.py --stoplines   # 비상 중단선 산정
python scripts/verify_research_chunks.py 2          # 하류 회귀
python scripts/verify_session_docs.py 2 --target 자료
python scripts/analyze_agent_usage.py --tool-audit --session <세션ID>  # 워커 도구·모델·동일URL 감사
```

## 롤백

```bash
cd C:/Users/miso/Desktop/template
git worktree remove C:/Users/miso/Desktop/template-research-refactor
git branch -D refactor/research-skill
```

> 이 파일은 리팩터링이 끝나면 삭제한다. `main`에 병합될 파일이 아니다.
