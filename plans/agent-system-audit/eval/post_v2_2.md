<!-- 시작 2026-10-07T18:23:39.821Z · 첫 호출 입력 60753 · 입력 합 1537030 · API 호출 12 · 도구 호출 20 · Read: MEMORY.md, PROGRESS.md, PLAN.md, 재개_인계.md, STATE.md, PROGRESS.md, 재개_인계.md -->

열린 일 정리 (읽기만 함, 수정 0). 정본은 STATE.md 색인(L16~27)이고 아래는 거기에 원자료를 대조한 것.
경로 약칭: 인계F=plans/FRAME-길이별-조립/재개_인계.md, 인계V=plans/바이브코딩_온라인/재개_인계.md

[1] 사용자 결정·자료가 있어야 진행
- FRAME 답 3건: Codex로 축제 앱·영상 실습 실행 결과, 영수증 이미지 10장, 무료 Codex·Antigravity의 이미지 읽기 여부 (인계F:52-54, STATE:37)
- FRAME 육안 확인: 새 장 모양·인쇄(PDF)·발표자 창 줄바꿈 (인계F:16,22). 세 도구 실행(영상·스킬 실습) 대기 (인계F:60-61)
- FRAME 4시간 덱 개편분 커밋은 시킬 때만 (STATE:35, git status에 145건 가량 미커밋)
- FRAME 도구 리허설(GR) 수행 여부 (STATE:39, plans/FRAME-개편/PLAN.md:118)
- 바이브코딩_온라인: 캡처 14슬롯 일괄 제공 → 교체 → G2 → 배포본 (인계V:55-95, STATE:51)
- S03 AC3 2차시 잔여 2건: 처리 여부. 사실 확인함: shell.html:311에 N-16 CSS가 있는데 part-01~09에 해당 슬라이드 0건 (STATE:58-60)
- S04 게이트 입력 결합 결정 2건: R-QD-04 미판정 WARN 수용 (a~d) / 뮤테이션 매트릭스 핵심 4셀 조건부 승격 (plans/gate-input-hardening/PROGRESS.md:110-122, 172-205)
- S05 kit 22px 하한 기본값, R-BOXFILL-01 그룹 키 (STATE:73)
- S06 훅 관측 장부 경로 이동: scripts/hook_slide_guard.py:25,259,275는 tmp/ 안 (STATE:80-85)
- S07 병합 끝난 로컬 브랜치 삭제 확인: git branch --merged main에 12개 (STATE:93)
- S08 1주차 동결 충돌: AGENTS.md:40(동결)과 sessions/README.md:122(동결 해제) 중 현행 확인 (STATE:99-101)
- S09 보류 질문 Q2·Q3·Q9·Q10, S10 실기기 확인 (plans/presenter-system-final-plan.md:776-800 검증표) (STATE:114-127)

[2] 사용자 입력 없이 에이전트가 할 수 있는 일
- S07 Codex 경로 파싱 어댑터 구현: .codex/hooks/에 probe.py뿐 (STATE:22,91). 관측 훅 승격은 오탐 0 확인 뒤
- S05 품질 게이트에서 사람 검토 범주를 별도 채널로 분리 (STATE:75)
- S11 번호 미결 8건 현황 확인 (STATE:129-140), S13 닫을 수 있는지 판정 (STATE:148), S09·S10의 "확인 필요" 항목 현황 확인
- FRAME 마무리 (STATE:41): profile.md:40,47의 회차당_장수_범위 7~14가 개편 전 값. 조립_보고.md·1주차_콘텐츠_리뷰.html·자료/이미지-에셋.json은 9-18자(50장 기준). deck.contract.json과 2h 덱이 현 덱과 어긋남 (인계F:16). 단 러너 판정 보류 결정(인계F:46)은 지킨다
- FRAME 스킬 실습 출처 등재·개념노트 항목 (plans/FRAME-길이별-조립/PROGRESS.md 말미, 인계F:61), 유형 테스트 prd.md를 생성 스크립트에 넣기 (인계F:28), 안 쓰는 이미지 정리 (인계F:22)
- FRAME 6시간 트랙: variants/6h.txt 없음 확인. 공공데이터 준비물·API/MCP 장 제작 (인계F:62,78, 공식 문서 확인 필요)
- 아래 [3]의 낡은 서술 정정

[3] 끝났거나 낡았는데 열린 것처럼 적힌 것
- 인계V:28,31 "오전 90장", "오후 초안 사용자 확인 대기"와 §3-2(L97-102 초안 작성부터): 같은 문서 L33과 STATE:50(81장·106장)에서 초안·G1·조립은 끝남
- plans/FRAME-개편/PROGRESS.md:81 "G1b 사용자 검토 대기", :101-107 "Phase E 마무리 (82장)", :120 시간표 재설계 결정 대기, MEMORY.md:163 "남은 일: G1b → GR → Phase E": PLAN.md:52 D40이 G1b를 위임했고 Phase E는 이후 커밋·123장(인계F:14)으로 진행됨
- 인계F:63 P6 "선택 주체 미정"(STATE:38도 확인 필요): 같은 문서 :23과 :37에서 허브(MHUB)로 구현·확정. 유형 테스트 부분도 :23에서 완료
- 인계F:26 "블록 1 57분, 확인 전": 인계F:14의 최신 값은 61.5·59·45·35.5분(상한 62)
- plans/FRAME-피드백-1007/PLAN.md:156-163 "확인받을 것" 6건: 같은 문서 :3이 반영 완료. 허브 레퍼런스는 :4에 HUD 없는 검은 우주로 정해짐
- plans/likelionSKU-theme/PLAN.md:3 "사용자 승인 대기": RESULTS.md가 2026-08-29 실행 결과를 담고 kit/themes/likelionSKU 존재
- plans/instruction-refactor/FINAL_REPORT.md:13,28 "Gate 0 승인 대기": AGENTS.md:76에 2026-08-18 실측 완료
- plans/rule-gap-fix/PLAN.md:97 MEMORY 미해결 갱신: 계획은 :3에서 실행 완료. 그 절은 MEMORY.md:149-151에서 STATE.md로 이관됨

제외: plans/agent-system-audit/, tmp/는 지시대로 열지 않음. 실행·검증 명령은 돌리지 않았고, 위는 파일 내용과 git status·git branch 조회에 근거함.
