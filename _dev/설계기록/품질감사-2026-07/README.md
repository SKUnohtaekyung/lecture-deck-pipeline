# 품질감사-2026-07 — create-slides 품질 감사와 2주차 재설계 기록

2026-07-26 **2주차 저밀도 사고**를 계기로 시작된 근본원인 감사와, 그 후속 재설계·A/B 실험이 남긴 산출물이다. 76개 파일 1,199,510 bytes, 2026-07-26 ~ 07-29에 생성됐다.

- 이 폴더는 **기록 보관소**다. 현재 규칙이 무엇인지 알고 싶으면 여기가 아니라 `.agents/agent-memory/create-slides/MEMORY.md`(누적 규칙 정본)와 `kit/guide/`(디자인 정본)를 본다.
- 여기 있는 계획서는 **그 시점의 스펙**이다. 나중에 뒤집힌 결정이 그대로 남아 있으니 §정본·구버전 구분을 먼저 본다.
- **2026-08-04에 저장소 루트 `reports/create-slides-quality/`에서 이 위치로 옮겼다**(폴더 통째, 무손실). 옮긴 이유는 §왜 여기로 옮겼나.

## 읽는 순서

| 순서 | 파일 | 무엇 |
|---|---|---|
| 1 | `root_cause_decision.md` | H1~H8 종합 판정 — **왜 2주차가 저밀도가 됐나**의 결론 |
| 2 | `validation_gap_report.md` | 기존 검증 ~120개 중 "완성 덱 내용 품질" 검사가 0개였다는 진단 |
| 3 | `FINAL_DECISION_PACKET.md` | 최종 결정 묶음(45KB) — 위 둘 이후의 판단이 여기서 뒤집힌 것들이 있다 |
| 4 | `ARTIFACT_MANIFEST.md` | 파일별 크기·해시·정본/구버전 표(2026-07-27 시점) |
| — | `WORKING_CONTEXT.md`(91KB) | 세션 진행상태 원장. 통독용이 아니라 **어떤 판단이 언제 뒤집혔는지 추적할 때** 연다 |

## 지금도 인용되는 파일 (지우면 참조가 깨진다)

| 이 폴더의 파일 | 인용하는 쪽 |
|---|---|
| `deck_quality_metrics.json` · `deck_quality_analysis.md` · `validation_gap_report.md` | [`scripts/verify_deck_quality.py`](../../../scripts/verify_deck_quality.py) — **임계값 도출 근거**. 이 게이트의 숫자가 어디서 나왔는지는 여기밖에 없다 |
| `content_pipeline_audit.md` | [`scripts/verify_draft_quality.py`](../../../scripts/verify_draft_quality.py) |
| `root_cause_decision.md` · `implementation_plan.md` | `.agents/agent-memory/create-slides/MEMORY.md` |
| `P7_ab_criteria.md` · `SESSION_HANDOFF_2026-07-27.md` | `skills/리서치/references/chunk-schema.md` |
| `week2_module_plan.md` | `courses/바이브코딩/커리큘럼_기준안.md` (회귀 방지 조항) |
| `week1_visual_benchmark.md` | `courses/바이브코딩/sessions/2주차/강의덱.초안/README.md` |
| `samples_v5A/DECISION.md` · `samples_v5B/DECISION.md` | `_dev/설계기록/탐색-아카이브/2주차/재설계/README.md` |
| `agent_harness_research.md` · `skill_rules_research.md` | 2주차 `자료/` 출처레지스트리·개념KB (둘 다 **선행 조사의 오류를 교정한 기록**으로 인용됨) |

## 정본·구버전 구분

`ARTIFACT_MANIFEST.md` §정본·구버전 구분 기준을 승계한다.

- **구버전** — `week2_remediation_plan.md` · `sample_before_after.md`: `FAILED_SAMPLE_V1` 관련 산출물로 사용자 전면 FAIL 판정을 받았다. **회귀 fixture로 쓰지 않는다.**
- **부분 대체됨** — `implementation_plan.md` · `week2_full_redesign_plan.md`: 일부가 `FINAL_DECISION_PACKET.md`로 대체됐다. 시스템 수정 실행 이력(A1~A8)은 유효.
- **완전 대체** — `artifact_manifest.md`(소문자, 구): Windows 대소문자 미구분 때문에 `ARTIFACT_MANIFEST.md`가 같은 자리를 덮어썼다. 그 문서 서두 고지 참고.
- **정본** — 그 외 전부. 단 각 파일이 자체 표시한 정정 이력은 파일 안에서 유지된다(예: `root_cause_decision.md`의 "270분→106장 역산" 정정).

## 구경로 → 신경로 대응표 (2026-08-04 이동)

**규칙 하나로 해소된다** — 파일 이름과 폴더 구조는 그대로다.

```
reports/create-slides-quality/<무엇이든>
  → _dev/설계기록/품질감사-2026-07/<무엇이든>
```

옛 문서에 남은 구경로 인용은 **그 시점 기록이라 고치지 않았다**([2주차 개정이력 README](../../../courses/바이브코딩/sessions/2주차/개정이력/README.md)와 같은 방침). 아래가 구경로를 그대로 담고 있는 문서다.

| 문서 | 지점 | 왜 안 고쳤나 |
|---|---|---|
| `courses/바이브코딩/sessions/2주차/개정이력/2주차_최종결정본.html` | 4곳 | 2026-07-29 **확정 덱 스냅샷** — 내용을 고치면 스냅샷이 아니게 된다 |
| `courses/바이브코딩/sessions/2주차/자료/2주차_출처레지스트리.md:764` | 1곳 | 2026-07-28 verbatim 대조 기록 |
| `courses/바이브코딩/sessions/2주차/자료/2주차_개념KB.md:118` | 1곳 | 개정 이력 행(`reports/…/` 축약형) |
| `_dev/설계기록/탐색-아카이브/2주차/재설계/NEXT_SESSION_PROMPT.md:80` | 1곳 | 그 시점 세션 지시문 |
| 이 폴더 내부 문서 17개 | 29곳 | 자기 구경로 언급. 폴더를 쪼개지 않았으므로 위 규칙으로 그대로 해소된다 |

**살아있는 규칙·코드 11지점은 신경로로 갱신됐다**(위 §지금도 인용되는 파일의 인용처 전부).

## 폴더 구성

| 계열 | 파일 |
|---|---|
| **감사·분석** (07-26) | `deck_quality_analysis.md` · `deck_quality_metrics.json`(190KB, 최대) · `validation_gap_report.md` · `skill_pipeline_audit.md` · `history_baseline_report.md` · `slide_trace_report.md` · `content_pipeline_audit.md` |
| **근본원인·결정** (07-27) | `root_cause_decision.md` · `FINAL_DECISION_PACKET.md` · `remediation_constraint_audit.md` · `pipeline_depth_contract_audit.md` · `ai_claim_ledger.md` · `phase1_evidence_map.md` |
| **계획** | `implementation_plan.md` · `pipeline_refactor_plan.md` · `quality_reproduction_plan.md` · `visual_system_revision_plan.md` · `week2_*`(재설계·확장·모듈·중복감사·개념깊이맵 등 10종) |
| **조사** | `agent_harness_research.md` · `skill_rules_research.md` · `new_concept_research.md` · `reference_pedagogy_audit.md` · `week1_visual_benchmark.md` |
| **세션 운영** | `WORKING_CONTEXT.md` · `SESSION_HANDOFF_2026-07-27.md` · `ARTIFACT_MANIFEST.md` · `AGENT_DISPATCH_SPECS.md` |
| **샘플 덱 3세트** | `samples_v3/`(15) · `samples_v5A/`(10) · `samples_v5B/`(10) + `AB_compare.html` — v5A/v5B는 A/B 실험 후보이며 판정 결과는 `P7_ab_criteria.md`, 채택본은 `_dev/설계기록/탐색-아카이브/2주차/재설계/`에 병합돼 있다 |

## 왜 여기로 옮겼나

루트 `reports/`는 [AGENTS.md](../../../AGENTS.md)의 ①~⑤층 구조 규정에 **등재된 적이 없는 폴더**였다. 내용물은 `_dev/설계기록/`(빌드·설계 결정 기록, 배포 제외)과 성격이 같고, 같은 사건의 채택본은 이미 `_dev/설계기록/탐색-아카이브/2주차/재설계/`에 있어 한 사건의 기록이 두 곳으로 쪼개져 있었다.

`탐색-아카이브/`(미채택본 자리)가 아니라 `설계기록/` 바로 아래에 둔 이유는, 여기 있는 문서 상당수가 **채택돼 현재 게이트의 근거로 살아 있기** 때문이다.
