> 작성: SCRIBE(2026-07-27) — 쓰기 허용 3파일 중 하나로 직접 기록. 이 문서는 `reports/create-slides-quality/` 산출물의 상태를 오케스트레이터가 직접 집계한 값 그대로 기록한다. 이 세션에서 `find`+`stat`+`sha256sum`으로 크기·수정시각·해시 전량을 재계산해 재확인했다. **커밋하지 않는다.**
>
> ⚠️ **파일명 충돌 고지**: 이 저장소는 Windows(NTFS, 대소문자 구분 없음)에서 작업 중이다. 작업 지시가 지정한 경로 `ARTIFACT_MANIFEST.md`(대문자)는 기존에 존재하던 `artifact_manifest.md`(소문자, 20,560B, SHA-256 `38d84ec87986c46c1e856e0bbd949cac95d88fe3a062a26a66bd051409c2bbb2`, "1주차 vs 2주차 정보밀도 조사 6단계 파이프라인 지도" 문서)와 **파일시스템상 동일 파일**이다 — 대소문자만 다른 두 경로가 별개 파일로 공존할 수 없다. 이 문서를 씀으로써 그 구 버전 내용은 **덮어써져 사라진다**(git 미커밋 상태였던 파일이라 이 저장소의 git 이력에는 애초에 없다 — 필요 시 복구할 방법은 이 세션 이전 이 대화의 tool 출력 기록뿐이며, 저장소 자체에는 남지 않는다). 이것은 작업 지시가 `ARTIFACT_MANIFEST.md`를 쓰기 허용 3파일 중 하나로 명시적으로 지정한 데 따른 의도된 결과로 판단해 진행했다 — **다만 이 판단은 SCRIBE가 내린 것이며, 오케스트레이터가 구버전 6단계 지도 내용을 별도로 보존하길 원했다면 재검토가 필요하다.**

# 산출물 매니페스트 — `reports/create-slides-quality/`(2026-07-27 최종 집계)

## 요약

- reports 전체 파일 수 **26**, 합계 **759,210 bytes**, 빈 파일 **0개**(이 세션 `find`+`stat` 재확인, 오케스트레이터 원 집계와 정확히 일치). 이 집계는 `FINAL_DECISION_PACKET.md`와 이 문서 자체를 쓰기 **직전** 시점의 기존 26개 파일 기준이다.
- **복원 파일 3개**(원 에이전트가 파일을 쓰지 않아 대화 기록에서 복원, 인용 표본 검증 완료): `pipeline_depth_contract_audit.md`(8,497B) · `visual_system_revision_plan.md`(7,894B) · `week2_curriculum_options.md`(12,265B). 세 파일 모두 서두에 "이 문서는 … 오케스트레이터가 복원한 것이다. 원 에이전트가 파일을 쓰지 않아 대화에만 존재하던 결과를 보존한 것이며, 인용은 표본 검증됐다"는 동일 고지문이 있음을 이 세션에서 직접 확인했다(`FINAL_DECISION_PACKET.md` §16 하네스 결함 이력과 연동).
- **Git**: 브랜치 `main`, 변경·미추적 총 **29**개 경로(`git status --porcelain` 재실행 재확인), 추적 파일 **18개 +677/−152**(`git diff --stat` 재실행 재확인), `reports/` 전체 **미추적**(`?? reports/` 한 줄).
- **백업 2종 실재**: `sessions/2주차/_backup_2026-07-27/` · `sessions/2주차/_backup_v2_2026-07-27/`(이 세션 `ls` 재확인).
- **PM PDF 4종 실재**: `sessions/references/PM_1.pdf` · `PM_2.pdf` · `PM_3.pdf` · `PM_4.pdf`(이 세션 재확인).
- **2주차 덱 107장**(`sessions/2주차/강의덱.html`의 `<section data-slide="…">` 태그 수, 이 세션에서 정규식 재실행해 재확인 — CSS 선택자 오염을 배제하기 위해 `<section` 접두 패턴으로 한정).
- **개념KB 청크 60개**(`sessions/2주차/자료/2주차_개념KB.md`의 `[C-…]` 헤딩 수, 이 세션에서 재집계).

## 정본·구버전 구분 기준

- **구버전**: `week2_remediation_plan.md`·`sample_before_after.md` — `FAILED_SAMPLE_V1` 관련 산출물이며 사용자 전면 FAIL 판정을 받았다. 배너(정정·경고 고지) 부착됨.
- **부분 대체됨**: `implementation_plan.md`·`week2_full_redesign_plan.md` — 이번 정정(EXTENSION 역전·CORE 12 후보화·자카드 보조지표화 등)으로 일부 내용이 `FINAL_DECISION_PACKET.md`로 대체됐으나 시스템 수정 실행 이력(A1~A8) 등 나머지는 유효.
- **완전 대체(덮어씀)**: `artifact_manifest.md`(소문자, 구) — 위 파일명 충돌 고지 참고. 이 문서(대문자)가 그 자리를 대신한다.
- **정본**: 그 외 전부. 단 각 파일이 자체적으로 표시한 정정 이력(예: `root_cause_decision.md`의 "270분→106장 역산" 정정)은 파일 내부에서 유지된다.

## 파일별 상세

각 행은 이 SCRIBE 세션이 이 문서를 쓰기 **직전** 시점의 상태를 기록한다. `WORKING_CONTEXT.md`는 이 세션에서 §F·§E·§H를 갱신했으므로 실제 해시는 이 문서 작성 이후 바뀐다(정상 — 아래 표는 갱신 전 스냅샷).

| 경로 | 크기 | 수정 시각 | SHA-256(갱신 전) | 정본·구버전 | 비고 |
|---|---:|---|---|---|---|
| `WORKING_CONTEXT.md` | 74,451B | 2026-07-27 03:26:28 | `4468e6f1ebe7a731e855b40e86d2213578a00ef21b715f4c4f96161c13672d18` | 정본 | 진행 상태 단일 정본 — 이 SCRIBE 세션이 §F·§E·§H를 갱신함. 이 표의 값은 갱신 **전** |
| `artifact_manifest.md`(소문자, 구) | 20,560B | 2026-07-27 01:54:12 | `38d84ec87986c46c1e856e0bbd949cac95d88fe3a062a26a66bd051409c2bbb2` | **완전 대체(덮어씀)** | 6단계 파이프라인 지도 — 파일명 충돌로 이 문서가 같은 경로를 대체함(상단 고지 참고) |
| `content_pipeline_audit.md` | 37,450B | 2026-07-27 00:57:27 | `cbe4ced2376203109c70c4911352c6e31fd46193f06ef8aeb7461153af803f07` | 정본 | 콘텐츠 파이프라인 1~3단계 감사 |
| `deck_quality_analysis.md` | 15,649B | 2026-07-26 23:23:19 | `70768486868fb6988366ae8b1dbb7ca94968642061606b3779e3e74bc571fb87` | 정본 | 정량 파서 분석(서술) |
| `deck_quality_metrics.json` | 190,335B | 2026-07-26 23:21:44 | `9ce39023e719463aa76842513aaf710f198c133293cd2c94a981ec019cf1976a` | 정본 | 정량 파서 원시 수치 JSON — reports/ 중 최대 용량 파일 |
| `history_baseline_report.md` | 24,220B | 2026-07-26 23:17:36 | `aae16ff40cd367ba2a91f6a0cb666e084db092b99ba87206a263e34195cc6c42` | 정본 | 1·2주차 개정 이력 대조 |
| `implementation_plan.md` | 10,502B | 2026-07-27 00:56:53 | `44c8848d8201b43463e6c0101ffb4ea81e0bdef2a89119685bcb5a883a15cc4b` | **부분 대체됨** | 시스템 수정 A1~A8 + 2주차 한정 B1~B6 — A1~A8 구현 이력은 유효, B계열(107장 유지 전제)은 이번 정정으로 재검토 대상 |
| `new_concept_research.md` | 18,773B | 2026-07-27 15:41:15 | `f68fa7c1b9eb2fcd6af5545660ca34be86667e4e4c0531ca5a169e570e70629c` | 정본 | `FINAL_DECISION_PACKET.md` §9의 직접 근거 — TASK1~3 |
| `pipeline_depth_contract_audit.md` | 8,497B | 2026-07-27 15:17:03 | `947f61a75da5b66a2bb935e16dc0cc004afb3581d21a01ca8aa8129e84d2cec2` | 정본 | **복원 파일** — §13 직접 근거 |
| `pipeline_refactor_plan.md` | 25,553B | 2026-07-27 15:10:08 | `88b3119e54a3a0785bb858ebb4935413ef9e5a556fb1e26f7e64ef0b58a3ac4f` | 정본 | §13 직접 근거(4개 스킬 최소 변경안) |
| `reference_pedagogy_audit.md` | 24,733B | 2026-07-27 14:48:48 | `58dc138f5cfd4001b380accde45406a4357469b6440d7def309f179a02653ec8` | 정본 | PM 레퍼런스 교육학 감사 |
| `remediation_constraint_audit.md` | 19,554B | 2026-07-27 02:00:12 | `f8d101808dbb9ee288a947d36c9d1e63768b3c48308c67c5161c9ec1420d59e7` | 정본 | 보정 실패 숨은 제약 감사(V1 차단 제약 원인 확정) |
| `root_cause_decision.md` | 14,849B | 2026-07-27 00:56:38 | `f4132540db29ac22925bbf4a7b3b716c5712158e48afd1198cbfe634f2d30c0d` | 정본(자체 정정 이력 포함) | H1~H8 종합 판정 |
| `sample_before_after.md` | 8,623B | 2026-07-27 01:49:24 | `7bd79f998eb4339d3b05c047872baa32928c17b8c18d1ab3bb9e3826dda356df` | **구버전** | `FAILED_SAMPLE_V1` 근거 — 사용자 전면 FAIL 판정, 회귀 fixture로 쓰지 않음 |
| `skill_pipeline_audit.md` | 19,404B | 2026-07-26 23:12:49 | `17e41ee08bd992901c941b60e42ae39e33518cbdc2215fd50b0fde45a50a0647` | 정본 | create-slides 조립단계 감사 |
| `slide_trace_report.md` | 24,951B | 2026-07-26 23:28:49 | `230b871f748468e4ad6d6ff59f015051579c6732ee2d7afbd1105e9e7ed29fca` | 정본(자체 정정 포함) | 10개 표본 손실 지점 추적, 노트 라우팅 출처 오귀속 자체 정정 |
| `validation_gap_report.md` | 18,409B | 2026-07-26 23:25:46 | `83fd915109d9edd492d11b1a4de221d9aa1aeb9c98d3beb747b1f0e2a110fa62` | 정본 | 기존 검증 공백 인벤토리 |
| `visual_system_revision_plan.md` | 7,894B | 2026-07-27 15:17:53 | `cfe850111ff6ecbbcba862d0023302bda8a397a5d80ddfda68ac27defe90cdf5` | 정본 | **복원 파일** — §12 직접 근거 |
| `week1_visual_benchmark.md` | 24,213B | 2026-07-27 02:06:20 | `1e2b4403872862db14f137597782b929c86e32c41a109c4f9510345853a08a71` | 정본 | 1주차 Part3 19장 전수분석 + 표본 매핑 |
| `week2_concept_depth_map.md` | 27,700B | 2026-07-27 14:49:55 | `6a56fc33028987651e28f87bf7e7ce2fb06ec4e135269ce3c4f9a53607231eac` | 정본 | §5·§9 직접 근거 — 주요28/보조32 |
| `week2_curriculum_options.md` | 12,265B | 2026-07-27 15:57:06 | `c31b949a688114f50e850de2d6a7485364345e0a6e32ab4ddc38c2d6631f5f6f` | 정본 | **복원 파일** — §5·§6·§7·§8·§14·§15 직접 근거(CORE 12·균형안 모듈표·원형 클러스터) |
| `week2_duplication_audit.md` | 15,045B | 2026-07-27 15:43:32 | `9323e85c44c874bda5006b4339705360dbce7542829ce27dbfa57b22303669d0` | 정본 | §10 직접 근거 |
| `week2_extension_plan.md` | 15,114B | 2026-07-27 15:52:25 | `3c0a3503c1641d08e827caee63f4d5211cad2bab926765c172d655e8268312a0` | 정본 | §7·§8·§15 직접 근거(EXTENSION 105분 인벤토리) |
| `week2_full_redesign_plan.md` | 23,228B | 2026-07-27 15:07:27 | `1a82c00f1701b746fbb4f1eecfe7a499d7bf189b0f4e59a8d76cb374f6f733de` | **부분 대체됨** | 이번 정정(EXTENSION 역전 등)으로 일부 전제가 재검토 대상 |
| `week2_module_plan.md` | 27,318B | 2026-07-27 14:55:56 | `a3954455bb994a6dd8da755b7cafe3c81098168909b5858db56c1a876536ba45` | 정본 | §8·§15 직접 근거(6모듈 45분 활동표) — **위험: 이 파일의 모듈별 균등 45분 배분이 `week2_curriculum_options.md` §D 라벨(48/45/50/42/40/45)과 불일치, `FINAL_DECISION_PACKET.md` §16 참고** |
| `week2_remediation_plan.md` | 49,920B | 2026-07-27 01:01:22 | `f7de2b0e4a5381d9b9697069108d5deac22a9f3d9b72451d2d9a54bf55591f4e` | **구버전** | 108장 전수 트리아지 — V1 차단 제약의 실제 출처(`:377,403`)로 확정됨(`remediation_constraint_audit.md`). reports/ 중 최대 용량 `.md` 파일 |

## 크기 총계 재검산

위 26개 파일(신규 `FINAL_DECISION_PACKET.md`·이 문서 자체는 제외) 크기 합계: **759,210 bytes** — 오케스트레이터 원 집계와 바이트 단위로 일치.
