# FRAME 수정 1025 — 진행 상태

정본 `PLAN.md` · 기준 커밋 `9e39489` · 시작 2026-10-25 · 커밋 안 함(U14)

| Phase | 상태 | 검토 ✗ | 반영 | 남은 것 |
|---|---|---|---|---|
| 1 덱 운영 장(O-01 · DL 4 · MHUB) | 완료 | 2(R3 · R5) | 4/4(열기 0 · DL-1 25px textBottom 624 · 링 확대 · 4h.txt 133) | DL-3 3번(사용자 답) |
| 1-A 사실 확인 2건 | 완료 | — | — | DL-3 문구 사용자 답 대기 |
| 2 준비물(CLAUDE.md · 알아서 · ⑧ v3) | 완료 | 3(R2 · R7 · R8) | 8/8(rg: CLAUDE.md·알아서 0 · 「네가 정해」 10파일 · zip 3) | 범위 밖 잔존: 메인과제_유형테스트/prd.md:18 FLIP(원본 gen 없음) |
| 3 덱 실습 장(P8 7장 · 동기화) | 완료 | 5(R1 · R2 · R3 · R6 · R7) | 덱 9/9 + 초안/노트 동기화(build_notes 0 · presenter 0 · 잔존 CLAUDE.md는 사실 문장 8줄뿐) | builder 9건(아래) → writer 동기화(P8 행 · 초안:192 「오늘 만드는 스킬」 · P5:1178/1203 문장 · P9-1 「7장까지·한도」) → rg -c · build_notes/presenter |
| 4 ⑤ 완성 예시 | 완료 | 1(R6 · 확인 필요) | R6 유지(왼쪽 열은 P5-1 기존 글 · 바닥 666) · design.md 64px · AGENTS.md:116 · P5-1 초안/노트 동기화(build_notes 0) | — |
| 5 마감 · 최종 검토 | 완료(미커밋) | 3(U2 · U6 · X3) | U2 profile:77 · 개념노트:123 / U6 profile:25 · 초안 README · gen_app docstring · 초안 O-01 / X3 메타만 바뀐 바이너리 49개 HEAD로 복원(목록 tmp/frame-수정-1025/p5/bin_same.txt) | 사용자 몫 · 확인 필요(아래) |

## STOP-1
- 1 참: CLAUDE.md·CLAUDE.local.md가 없으면 AGENTS.md를 읽음 · v2.1.277 이상(code.claude.com/docs/en/memory) → Phase 3에서 part-03 「(최신 버전)」→「(v2.1.277 이상)」
- **사용자 답(2026-10-25): 「워크 말고 Codex 사용」** → DL-3 제목 「앱을 열고 Codex로 바꿉니다」 · 3번 「왼쪽 위 「ChatGPT ⌄」를 눌러 Codex를 고릅니다(단축키 Alt+3)」 · 링 → ChatGPT 드롭다운 · DL-ALL 「앱을 열고 Codex」. 3-B writer의 DL 멘트도 Codex로
- 2 불명확 → 사용자 질문: Codex는 Work와 별개 화면(learn.chatgpt.com quickstart 「select Codex from the ChatGPT dropdown」 · Windows Alt+3) · 드롭다운 위치 미확인 · help.openai.com 403. DL-3 3번은 「Work를 누릅니다」까지만 유지
- 연구자 후보 문장 「Work 안이 아니라 별도 화면」은 FLIP 꼴이라 쓰지 않음

## 메모
- **사용자 지시(2026-10-25): 서브에이전트 추론도 high까지만 · Opus는 품질이 확실히 오르는 일만.** 이후 호출은 builder/writer/reviewer에 effort "high" 명시 · Opus는 5-B 최종 검토(U1~U14 원문 대조)만 · 4-A builder는 지시 전 xhigh로 시작됨
- P2 writer: gen_all 0 · CLAUDE.md/알아서/tone 0 · ⑧ zip 3파일. 「확인하는 법」→「확인 방법」(tone HOWTO 충돌) · gen_app `--texts-only` 추가 · 시연_절차서_카드뉴스.md(gen_p9 생성물) 2줄 · 실습1~7 바이너리 재생성
- P1 builder: assemble 0 · 133장 · 4h cmp 동일 · DL 4 · 새 CSS 2 · 새 hex 0(var(--red) 재사용) · 원본 캡처 3 삭제 · 이미지-에셋.json 스키마 전체 형식
- P1 측정(브라우저 · 0.8 축소 보정): O-01 · DL-1~ALL · MHUB 넘침 0 · sw1280 sh720 · 22px 미만은 기존 class(kick18 · 캡션 P18=P1-1 · pill17)뿐. 인앱 창 숨김 → 스크린샷 불가 → clerk Playwright 캡처(tmp/frame-수정-1025/p1/shots/) → 육안: 동그라미 5개 위치 맞음 · MHUB 2카드 가운데 · O-01 여백 정상 · 좌표 수정 불요
- P1 검토 반영 안 함(판단): 「Mac은 macOS용 단추」(공식 문서상 macOS·Windows 앱) · 「시작 메뉴」(PLAN 장 글) · 링 색 --red #B3124E(기존 토큰) · O-01 inline margin 72px(육안 정상)
- P3-A: 4h 136장 · 4h-app 49장 assemble 0 · 새 CSS 0 · 측정 12장 넘침 0 · txtB ≤666(P8-3B 666) · 「맡기」 잔존 8줄은 다른 뜻 동사(part-01 · 03 · 04) — 「맡기려면」만 대상으로 판단 · CLAUDE.md는 part-01 1 + part-03 2(도구 표 사실 · v2.1.277 문장)
- P3 캡처 육안(tmp/frame-수정-1025/p3/shots/): DL-3 링 ChatGPT 메뉴 위 · P8-1/3/3B 기존 스타일 · 반영 대기: DL-3 칩 「ChatGPT ⌄」의 ⌄가 아래첨자 v처럼 보임 → 칩은 「ChatGPT」만 + 「메뉴」
- P3-B: build_notes --check 0(136) · presenter --check 0 · 잔존 CLAUDE.md 초안 3/노트 2(사실) · 「맡기」 초안 3/노트 2(장 글과 같은 일반 동사) · 범위 밖 둠: 초안 머리 시간표 10-21 기준
- P3 보정: part-05 「다섯 개」→네 개 · P5-2/P9-2 기본값 라벨 → 보기(P9-2 1줄 측정 확인) · DL-3 칩 ⌄ 제거 · 4h-app 덱 개수 말(실제 4파일) · 여행앱 초안/노트 CLAUDE.md·사실 문장(v2.1.277) · build_notes --check 4h/4h-app 0(단 --check는 글 대조 안 함 → rg로 대조)
- P3 빌드: build_notes 4h 136 · 4h-app 49 exit 0 · build_presenter 4h(배포 7650KB) · 4h-app(3374KB) exit 0 · 초안/노트 「⌄ · 기본값 라벨」 0
- P3 검토 → builder 9건(part-05): :991 의인화 수동 · P8-1 「받은 실습 폴더의 준비물」 · P8-2 뼈대 「내 강의」「디자인 시스템」 절 + 「7단계 + 점검 조건」 · P8-2B 디자인 시스템 정의 + 시안 더블클릭 + 「예를 들어 줘」 · P8-2C A3 시작 요청 · P8-2D 승인 · P8-3B 「일곱 조건 + 내가 정한 세 가지」(바닥 666 — 줄 늘리지 않음) · P8-3 「B1~B7 = 1~7단계」 · memory 「폴더 안 주제별 파일」
- P3 검토 반영 안 함(판단): R1(c) 요청문(PLAN 지정 · 「단계마다 승인」) · 비유 차이(기존 장) · 타이머 75분(U8) · P3:99 문장(PLAN 지정) · DL-2 Mac 경로 → 사용자 몫
- profile.md:115 ⑧ 행을 v3로 고침(메인 · 완료)
- Agent 분류기 무응답 2회 뒤 3번째에 builder 발송됨
- P4-A: 완성예시/실습5_모션그래픽/ 4파일 · 영상.html 9.9KB · 외부 0 · 30.0초 6장면 · 대비 15.56/9.15 · 최소 노출 1.90초 · 강조색 #0E4A5A(원본 docx·xlsx 색) · 36,900 · 104/120=87% · 캡처 t=19.5 · 미확인: getDisplayMedia file:// · 장면1→2 겹침
- P4 캡처: 1280×720 전체 캡처는 세로 영상이 작고 단추가 커서 버림 → #stage만 t=1.5 · 19.5 · 28 세 장면 합성 1400×874(p5.png 74KB · 육안 확인)
- P5-B 문서(메인): STATE.md S14 축제 → U6 폐기 · S01 축제 2줄 삭제 · S16 신설 · CODEX_PROMPT §C 표 행 · 블록 · 「TourAPI 신청」 삭제(백업 tmp/frame-수정-1025/CODEX_PROMPT.bak.md) · 재개_인계 §1 P5 행 + 「수정 1025」 행 · agent-memory MEMORY.md FRAME 규칙 1줄
- P5-A: fest 속성 18 삭제 · 대리시험 2 삭제 · p8_v2 → _archive · README ⑤ 행 · unittest 410 OK · build_notes/presenter 4h·4h-app 0 · tone part-01 3 · 초안 6 · 노트 7(모두 기존) · 메인 보정: gen_p8 docstring · 초안 README 축제 · 조립_보고 장 수
- U11 후속(사용자 결정 2026-10-25): memory/<주제>.md 유지 + 이름 규칙 「띄어쓰기 없이 · 새 강의는 memory 목록부터 확인」을 품질기준 A4 · B1 · P8-2D(측정 바닥 561) · 초안/노트에 반영 · gen_all · notes · presenter 0
- 후속(사용자 2026-10-25): ⑤ 리모션 — 품질기준 · 노트에 「설치 없이」 줄(writer) · P5-3에 리모션 안내 2문장(builder · 공식 확인: React 영상 · MP4 렌더 · Node.js · 영리 4명+ 회사 라이선스 · 「더 좋은 품질」 공식 근거 없음 → 「프레임 단위 MP4 · 녹화 끊김 영향 없음」으로 씀) · 완성 예시 영상 업그레이드 완료(Opus high · 우와 포인트 14 · 30.0초 · 최저 대비 5.13 · 외부 0 · 콘솔 오류 0) · p5.png 재합성(t=12.5 · 19.0 · 29.5 · 484KB) · P5-1/P5-3/P8-2D 측정 통과 · 빌드 · 410 OK
- 최종 확인 필요(사용자): 메인 과제 DS-4 요청 「색 방향 세 가지 추천해 줘」 · 여행앱 AGENTS.md 「기본값 표시」 문장 없음 · 사용자 원본 캡처 3장은 1400px 축소본만 남음 · DL-2 Mac 경로 없음 · 2h 덱 CLAUDE.md(U14 잠김)
- P3 writer 몫: 초안·발표노트의 「스킬이 미리 들어 있다」 옛 서술
