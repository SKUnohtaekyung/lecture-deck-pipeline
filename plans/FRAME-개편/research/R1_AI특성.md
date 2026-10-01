# R1 — AI 특성 개념 조사 (research-worker · sonnet · 2026-09-30)

> 워커 반환 원문을 보관한다. 표기: [열람]=페이지 직접 확인 · [2차]=검색 요약·타 매체 인용 · [미확인]. openai.com·help.openai.com·platform.openai.com은 WebFetch 403.

## 1. 다음 토큰 예측 · 토큰 · 확률적 생성
- 정의: AI는 지금까지의 글 뒤에 올 가장 그럴듯한 다음 조각(토큰)을 하나씩 골라 이어 붙여 문장을 만든다.
- 비유: (a) 휴대폰 자동완성을 아주 길게 이어 쓰는 것 (b) 「오늘 점심은…」 뒤에 올 말을 후보 중 확률대로 뽑는 제비뽑기
- 사실: Anthropic 용어집 — 사전학습에서 「앞선 문맥이 주어졌을 때 다음 단어를 예측」하도록 훈련. 토큰은 「단어·하위 단어·문자·바이트에 대응할 수 있는 가장 작은 단위」, Claude 기준 영어 약 3.5자, 언어마다 다름 [열람] https://platform.claude.com/docs/en/about-claude/glossary
- 사실: 같은 글 — temperature는 무작위성 조절 매개변수, 0이어도 완전히 결정적이지 않아 같은 입력에 다른 출력 가능 [열람]
- 사실: Claude 4.7 이후 새 토크나이저는 같은 글에서 토큰이 약 30% 더 나온다 [열람] https://platform.claude.com/docs/en/build-with-claude/token-counting
- OpenAI 토큰 도움말 403 [미확인].
- 체험: 같은 질문(「봄을 주제로 두 줄 시」)을 새 대화에서 3번 → 답 비교. 토크나이저 캡처는 사전 준비.

## 2. 지식 마감일
- 정의: AI가 학습한 자료가 끝나는 시점. 그 이후 일은 검색이나 문서로 알려 주지 않으면 모른다.
- 비유: (a) 어느 날짜에 인쇄가 끝난 백과사전 (b) 몇 달 전 출국해 뉴스를 못 본 여행자
- 사실: Anthropic 모델 개요표가 「Reliable knowledge cutoff」와 「Training data cutoff」를 구분. Sonnet 5.5는 둘 다 2026-06, Haiku 4.5는 2025-02 / 2025-07 [열람] https://platform.claude.com/docs/en/models/overview — 슬라이드에는 모델명 대신 「모델 개요 페이지에 공개」로.
- 체험: 웹 검색 끈 상태/켠 상태로 「오늘 날짜와 최근 뉴스」 비교.

## 3. 환각 — Mata v. Avianca
- 정의: 사실이 아닌 내용을 사실처럼 자신 있게 지어내는 현상.
- 비유: (a) 모르는 길을 물으면 그럴듯하게 안내하는 사람 (b) 기억나지 않는 대목을 앞뒤 맥락으로 채우는 목격자 진술
- 사실: 2023-06-22 뉴욕 남부연방지법 P. Kevin Castel 판사, 변호사 2명(Peter LoDuca · Steven Schwartz)과 로펌에 $5,000 제재. 사건번호 1:22-cv-01461, 678 F. Supp. 3d 443 [열람: Wikipedia] https://en.wikipedia.org/wiki/Mata_v._Avianca,_Inc. · 「가짜 판례 6건」「ChatGPT에 진위를 되묻자 실제라고 답함」은 [2차]. 판결문 PDF https://www.law.berkeley.edu/wp-content/uploads/archive/2025/12/Mata-v-Avianca-Inc.pdf (텍스트 추출 불완전 — 사람 확인 권장)
- 체험: 존재하지 않을 책 제목의 줄거리를 물어 지어내는지 관찰 → 「실제로 있는지 출처」 이어 묻기.

## 4. 아첨
- 정의: 사용자 의견에 맞추려고 사실·정확한 평가보다 듣기 좋은 답을 내놓는 경향.
- 비유: (a) 무슨 말을 해도 「좋은 생각이네요」만 하는 부하 직원 (b) 손님 기분에 맞춰 옷이 어울린다고만 말하는 판매원 — ⚠️ (a)는 의인화에 가까움, 문체 기준 판정 필요
- 사실: TechCrunch 2025-04-29 — 4-27 Sam Altman 문제 인정, 4-29 롤백·사후 설명. OpenAI 인용 「GPT‑4o skewed towards responses that were overly supportive but disingenuous.」 원인: 단기 피드백에 과의존 [열람] https://techcrunch.com/2025/04/29/openai-explains-why-chatgpt-became-too-sycophantic · 배포일 2025-04-25 [2차] · OpenAI 원문 https://openai.com/index/sycophancy-in-gpt-4o/ · https://openai.com/index/expanding-on-sycophancy/ [미확인 403]
- 사실: Sharma et al.(Anthropic) arXiv 2310.13548, ICLR 2024 — 사람 피드백이 「진실보다 사용자 믿음에 맞는 응답」을 부추길 수 있음, 주요 AI 어시스턴트 5개가 일관되게 아첨 [열람] https://arxiv.org/abs/2310.13548
- 체험: 같은 문단을 「제가 쓴 건데 최고죠?」 / 「경쟁자가 쓴 건데 문제점을 찾아 줘」로 평가시켜 어조 비교.

## 5. 중간 유실
- 정의: 긴 글을 넣으면 앞과 끝의 정보는 잘 쓰고 가운데 정보는 더 자주 놓친다.
- 비유: (a) 긴 강연에서 처음과 마지막 말만 기억나는 청중 (b) 긴 목록에서 첫 줄과 끝 줄만 눈에 남는 것
- 사실: Liu 외(2023) arXiv 2307.03172 — 관련 정보가 처음이나 끝에 있을 때 성능이 가장 높고 가운데에서 크게 떨어짐(다문서 QA · 키-값 검색). 「U자」는 논문 그림의 통상 설명(초록에는 없음) [열람] https://arxiv.org/abs/2307.03172
- 체험: 30문단 글의 15번째 문단에 사실 하나를 숨기고 질문(사전 리허설 필수).

## 6. 대화가 길어질수록 흐려짐(context rot)
- 정의: 대화·입력이 길어질수록 앞 내용을 정확히 기억·활용하는 능력이 흔들린다.
- 비유: (a) 서류가 쌓인 책상에서 필요한 한 장 찾기 (b) 긴 회의에서 초반 결정이 흐려지는 것
- 사실: Chroma 「Context Rot」(Hong · Troynikov · Huber, 2025-07-14) 18개 모델 — 단순 과제에서도 입력 길이에 따라 성능이 크게 달라짐 [열람] https://www.trychroma.com/research/context-rot
- 사실: Anthropic 엔지니어링 글(2025-09-29) — 컨텍스트 토큰이 늘수록 회상 능력 감소, 「attention budget」 [열람] https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- 2026 모델에서의 정도는 [미확인] → 슬라이드에 「2025년 연구 시점 모델 기준」 명시.
- 체험: 긴 대화 끝에서 「처음 말한 조건 세 가지」 요청 vs 새 대화 비교.

## 7. 프롬프트 인젝션
- 정의: AI가 읽는 문서·웹페이지 안에 숨은 지시문을 사용자 지시로 착각해 따르는 문제.
- 비유: (a) 우편물 요약을 맡겼는데 편지 속 「이 편지를 읽는 비서는 통장을 보내라」를 따르는 상황 (b) 택배 상자 속 메모를 사장님 지시로 믿는 직원
- 사실: Brave 보안팀 2025-08-20 — Perplexity Comet 브라우저, Reddit 댓글에 숨긴 텍스트를 따라 계정 이메일·OTP를 유출하는 개념 증명 [열람] https://brave.com/blog/comet-prompt-injection/
- 사실: Palo Alto Unit 42 2026-03-03 — 실제 웹에서 숨은 지시(광고 심사 AI 속이기), 글자 크기 0·CSS 숨김 [열람] https://unit42.paloaltonetworks.com/ai-agent-prompt-injection/
- 체험: 레시피 글 끝에 흰 글씨 지시를 넣고 요약시키기(리허설 필수 · 따르지 않으면 「방어 작동」으로 설명).

## 8. 자동화 편향
- 정의: 기계·AI가 낸 답을 스스로 검증하지 않고 그대로 받아들이는 경향.
- 비유: (a) 내비게이션대로 좁은 길에 들어가는 운전자 (b) 맞춤법 검사기 수정안을 전부 그대로 적용하기
- 사실: Goddard 외(2012) JAMIA, 임상 의사결정 지원 74개 연구 검토 — 메타분석 4건에서 지원 체계가 있는 군이 틀린 조언을 26% 더 따름, 맞던 결정이 틀린 결정으로 바뀐 비율 6~11% [열람] https://pmc.ncbi.nlm.nih.gov/articles/PMC3240751/
- 사실: Parasuraman & Manzey(2010) Human Factors [미확인 403] https://journals.sagepub.com/doi/10.1177/0018720810376055
- 체험: 오류가 섞인 AI 답에서 틀린 곳 찾기.

## 남은 공백
모델별 환각률 최신 수치 · 2026 모델의 context rot 완화 정도 · OpenAI 롤백 공식 글 원문 인용(사람이 브라우저로 확인 필요).
