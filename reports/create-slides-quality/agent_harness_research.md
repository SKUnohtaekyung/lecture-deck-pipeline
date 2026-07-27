# 에이전트·워크플로·하네스 엔지니어링 — 웹 리서치 (Agent A)

> ## ⚠️ 상태: UNVERIFIED · 정본 아님 · `/리서치` 입력 후보
>
> **2026-07-28 사용자 지시로 지위가 강등됐다.** 이 파일은 메인 세션이 직접 dispatch한 general-purpose 워커의 산출물이며, **강의 콘텐츠의 정본이 아니다.** 신규 AI 개념의 정본은 공식 `/리서치` 스킬이 `sessions/2주차/자료/`(개념KB·출처레지스트리 등 5파일)에 산출한다.
>
> - **정확한 상태**: `PARTIAL`이 아니라 **자체 사양 기준으로는 완료**됐다(00:16:38 저장, 255줄·37,016B·SHA-256 `558820f01899…`, §1~§8 전부 존재). 중단된 것은 Agent C이며 C는 **파일을 생성하지 않았다**.
> - **허용 용도**: `/리서치`에 넘길 **선행 조사·후보 출처 모음**.
> - **금지 용도**: 이 파일의 문장을 그대로 개념KB에 복사하는 것. 강의 정의·커리큘럼 결정에 직접 사용하는 것.
> - `/리서치`는 아래 §5 주장·출처 표의 URL을 **다시 열어** 실제 주장과 일치하는지 확인한 뒤 정본화한다.
> - **메인 Opus 교차검증 완료분(이 2건만 독립 확인됨)**: `martinfowler.com/articles/harness-engineering.html`(Böckeler, 2026-04-02)과 `huggingface.co/blog/agent-glossary`(Paniego·Gosthipaty, 2026-05-25)를 메인이 직접 WebFetch해 핵심 문장을 확인했다. 표준화 판정의 근거는 유지된다. 단 **문구 차이 2건**을 기록한다 — ① HF 인용을 메인이 확인한 원문은 `"Claude Code's own docs say it directly: 'Claude Code serves as the agentic harness around Claude.'"`이고 §3.2가 적은 "products like Claude Code, Codex, and Antigravity CLI call the whole thing a harness"와 문장이 다르다(취지는 동일하나 verbatim 아님). ② Fowler 문서의 실행 범주 원문은 `Computational`("deterministic and fast, run by the CPU") vs `Inferential`인데 §3.3은 이를 `Deterministic`으로 적었다. **정본화 시 verbatim은 원문에서 다시 딴다.**
> - 그 외 §5의 나머지 출처는 메인이 독립 확인하지 않았다.

조사일: 2026-07-28. 강의 맥락: 2주차 4교시, 대상 20~40대 비전공자(ChatGPT+Codex 사용 경험자). 정식 용어를 먼저 제시하고 쉬운 설명을 붙이는 방식을 따른다.

---

## §1 조사 범위·중단 기준

- A1(에이전트 vs 워크플로): Anthropic 1차 출처 확보 후 OpenAI·Google 1차 자료로 교차 검증, 어디서 다른지 확인하는 것을 목표로 함. ReAct 원 논문 확보.
- A2(하네스 엔지니어링): **표준화 수준 판정을 최우선**으로 삼음 — 학술 정의인지 벤더 조어인지 실무자 비공식 어휘인지 1차 자료로 직접 확인.
- 중단 조건 적용: 공통 정의(에이전트=모델+도구+환경+상태+행동), 주요 이견(에이전트 정의의 관대함 스펙트럼), 제품별 차이(OpenAI Agents SDK vs Anthropic 체크포인트형), 위험한 오개념(하네스=표준 학술 용어라는 착각) 확보 시점에 각 개념 조사를 종료함.
- 개념당 1차 자료 3~5개 원칙을 지켰고, 블로그 한 곳 표현을 보편 정의로 쓰지 않았다(특히 "하네스"는 최소 3개 독립 출처—Fowler/Osmani/HuggingFace—로 교차 확인).

---

## §2 에이전트 vs 워크플로

### 2.1 Anthropic — "Building Effective Agents" (1차, 확정 출처)

URL: https://www.anthropic.com/engineering/building-effective-agents (조회 2026-07-28)

정의(원문 인용, WebFetch로 확인):
- **워크플로(Workflows)**: "systems where LLMs and tools are orchestrated through predefined code paths."
- **에이전트(Agents)**: "systems where LLMs dynamically direct their own processes and tool usage, maintaining control over how they accomplish tasks."
- 구성요소: "augmented LLM"(retrieval, tools, memory)이 기초 단위이고, "environmental feedback"(tool call 결과나 code execution 결과)이 진행 상황 판단에 쓰인다.
- 인간 개입: 에이전트는 "pause for human feedback at checkpoints or when encountering blockers"할 수 있으며, 코딩 맥락에서 "human review remains crucial for ensuring solutions align with broader system requirements"라고 명시.
- 한계·실패: "Agents' autonomy means higher costs, and the potential for compounding errors." 권고: "extensive testing in sandboxed environments, along with the appropriate guardrails."
- 자율성 프레이밍: Anthropic은 고객마다 "agents"라는 말을 완전자율 시스템으로 쓰는 경우와 미리 정해진 워크플로를 따르는 구현으로 쓰는 경우가 갈린다고 명시하며, 이 모든 변이를 "agentic systems"로 통칭하되 workflows/agents는 아키텍처적으로 구분한다. 권고 원칙: "we recommend finding the simplest solution possible, and only increasing complexity when needed."

**판정**: Anthropic 문서는 "workflow vs agent"의 선을 **제어 흐름의 소재(predefined code path vs LLM이 동적으로 결정)**로 긋는다. 이는 자율성 정도(degree)의 문제가 아니라 "누가 다음 단계를 결정하는가"의 이분법에 가깝다.

### 2.2 OpenAI — "A practical guide to building agents" (1차, PDF 원문 확보)

URL: https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf (조회 2026-07-28, PDF 전문 33페이지 직접 읽음)

정의(원문 인용):
- "Agents are systems that **independently** accomplish tasks on your behalf." (4쪽)
- "A workflow is a sequence of steps that must be executed to meet the user's goal... whether that's resolving a customer service issue, booking a restaurant reservation, committing a code change, or generating a report." (4쪽)
- "Applications that integrate LLMs but don't use them to control workflow execution—think simple chatbots, single-turn LLMs, or sentiment classifiers—are not agents." (4쪽)
- 핵심 특성 2가지(원문): (1) "It leverages an LLM to manage workflow execution and make decisions. It recognizes when a workflow is complete and can proactively correct its actions if needed. In case of failure, it can halt execution and transfer control back to the user." (2) "It has access to various tools to interact with external systems... always operating within clearly defined guardrails."
- 구성요소 3가지(7쪽): **Model**("The LLM powering the agent's reasoning and decision-making"), **Tools**("External functions or APIs the agent can use to take action"), **Instructions**("Explicit guidelines and guardrails defining how the agent behaves").
- 오케스트레이션: 단일 에이전트(루프) vs 다중 에이전트(Manager 패턴/Decentralized 핸드오프 패턴) 2대 범주로 구분(13, 17쪽).
- 언제 안 쓰나(6쪽): "Before committing to building an agent, validate that your use case can meet these criteria clearly. Otherwise, a deterministic solution may suffice." — 규칙기반이 감당 못 하는 복잡한 판단·유지보수 어려운 룰셋·비정형 데이터 3가지 기준 제시.
- 인간 개입(31쪽, "Plan for human intervention"): 2대 트리거 — "Exceeding failure thresholds"(재시도 한도 초과 시 에스컬레이션), "High-risk actions"(민감/비가역/고위험 행동은 사람 승인 필요). "For a coding agent, this means handing control back to the user."
- 가드레일 유형(24~28쪽): Relevance classifier, Safety classifier(탈옥/프롬프트 인젝션), PII filter, Moderation, Tool safeguards(read-only/write, 가역성, 금전 영향에 따라 low/medium/high 리스크 등급), Rules-based protections, Output validation. Agents SDK는 "optimistic execution"(가드레일이 메인 실행과 동시에 병렬로 돌다가 위반 시 예외를 던짐) 방식.
- 결론(32쪽): "Agents mark a new era in workflow automation, where systems can reason through ambiguity, take action across tools, and handle multi-step tasks with a high degree of autonomy."

**OpenAI vs Anthropic 차이**: OpenAI는 "독립성(independence)"과 "에이전트가 워크플로 실행을 통제하는가"를 기준으로 삼아 Anthropic과 결이 비슷하지만, OpenAI는 이걸 **정도(gradient, "high degree of independence")**로 표현하는 반면 Anthropic은 **아키텍처 이분법**(predefined path vs dynamic control)으로 표현한다. 또 OpenAI 가이드는 "agent = model + tools + instructions" 3요소로 단순화하는데, Anthropic은 tools/memory/retrieval을 포괄하는 "augmented LLM" 개념 위에 workflow 패턴(prompt chaining, routing, parallelization, orchestrator-worker, evaluator-optimizer)을 얹는 더 세분화된 체계를 쓴다(단, 이 세부 패턴 5종은 이번 조사에서 직접 인용 재확인은 안 했음 — §8 모름 참고).

### 2.3 Google/Kaggle — "Introduction to Agents" 백서 (2차 경유, 1차 원문 직접 확보 실패)

시도한 1차 URL: https://www.kaggle.com/whitepaper-introduction-to-agents — WebFetch가 타이틀만 반환하고 본문을 못 읽음(§7 로그).
대체로 확인한 2차 요약: https://vanducng.dev/2026/01/10/Google-Introduction-to-Agents-Whitepaper-Summary/ (조회 2026-07-28) — **이 URL은 요약자의 정리이지 Google 원문 직접 인용이 아님을 명시**.

요약에 따르면 Google의 정의: "An agent combines models, tools, an orchestration layer, and runtime services which uses the LM in a loop to accomplish a goal." 4대 구성요소를 Model(뇌)·Tools(손)·Orchestration(신경계)·Deployment(몸)로 은유. 자체 제안 자율성 5단계(Level 0 고립 추론 ~ Level 4 자가진화 시스템)도 제시하는데, **이는 Google 자체 제안 프레임워크로 보이며 업계 합의 표준이 아님**(교차 확인 못 함 — 원문 직접 인용 실패로 정확도 보증 안 됨).

**결론**: Google 쪽은 원문 직접 인용에 실패해 신뢰도가 Anthropic·OpenAI보다 낮다. 강의 자료에는 OpenAI·Anthropic 1차 인용을 우선 사용하고 Google은 "구성요소 은유(뇌/손/신경계/몸)" 정도만 참고자료로 쓰되 출처 신뢰도가 낮음을 명시할 것.

### 2.4 계획·도구호출·관찰·반복 루프 — ReAct 원 논문

URL: https://arxiv.org/abs/2210.03629 (조회 2026-07-28, abstract 확인)

- 저자: Shunyu Yao, Jeffrey Zhao, Dian Yu, Nan Du, Izhak Shafran, Karthik Narasimhan, Yuan Cao. 제출: 2022-10-06(v1).
- 초록 원문: "their abilities for reasoning (e.g. chain-of-thought prompting) and acting (e.g. action plan generation) have primarily been studied as separate topics." ReAct의 핵심: "reasoning traces help the model induce, track, and update action plans as well as handle exceptions, while actions allow it to interface with external sources, such as knowledge bases or environments, to gather additional information."
- 선행연구 대비 개선: "ReAct overcomes issues of hallucination and error propagation prevalent in chain-of-thought reasoning by interacting with a simple Wikipedia API."
- **이것이 오늘날 "에이전트 루프"(계획→도구호출→관찰→반복)라 불리는 패턴의 원 논문이다.** OpenAI Agents SDK의 `Runner.run()` while-loop, Anthropic의 "augmented LLM" 루프 모두 이 ReAct 패턴의 실무 구현이다(단, 두 벤더 문서 모두 ReAct를 명시적으로 인용하지는 않음 — 이는 이번 조사에서 확인 못한 연결고리이므로 강의 자료에서 "ReAct가 이 루프의 학술적 기원"이라 말하되 "OpenAI/Anthropic이 ReAct를 직접 인용하지는 않는다"는 점은 구분해서 전달할 것).

### 2.5 자율성의 정도 — 합의된 분류 체계 여부

URL: https://arxiv.org/abs/2506.12469 "Levels of Autonomy for AI Agents" (조회 2026-07-28, abstract 확인)

- 저자: K. J. Kevin Feng, David W. McDonald, Amy X. Zhang. 제출 2025-06-14.
- 초록 원문: "We argue that an agent's level of autonomy can be treated as a deliberate design decision... In this work, we define five levels of escalating agent autonomy, characterized by the roles a user can take when interacting with an agent: operator, collaborator, consultant, approver, and observer."
- **판정**: 이 논문 자체가 "새 프레임워크를 제안한다(we define)"는 언어를 쓴다는 것은 **기존에 합의된 표준 분류 체계가 없었다**는 뜻이다. 자동차 자율주행의 SAE J3016(레벨 0~5)처럼 산업 전체가 채택한 표준이 AI 에이전트에는 아직 없다. Google의 자체 5단계(§2.3, 2차 경유라 신뢰도 낮음)도 이 논문과 별개의, 서로 다른 5단계 체계다 — 즉 **"5단계"라는 숫자만 같을 뿐 벤더/논문마다 기준이 다르다.**
- 강의 전달: "자율성은 정도의 문제이고 합의된 단일 표준 척도는 없다"고 정확히 전달해야 하며, 특정 벤더의 레벨 체계를 정설처럼 가르치면 안 된다.

---

## §3 하네스 엔지니어링 — 표준화 수준 판정 (최우선 발견)

### 3.1 결론부터: **벤더/실무자 조어이며, 학술 표준이 아니다. 업계 자체도 "용어가 아직 안 굳었다"고 명시적으로 인정한다.**

가장 결정적인 증거는 Hugging Face의 용어집(§3.2)이 "terminology fragmentation"(용어 파편화)을 이유로 들어 자체 정리를 낸 것 자체다 — **표준이 있었다면 이런 글이 나올 이유가 없다.**

### 3.2 Hugging Face "Harness, Scaffold, and the AI Agent Terms Worth Getting Right" (1차급 — 업계 용어 상태에 대한 메타 권위 자료)

URL: https://huggingface.co/blog/agent-glossary (조회 2026-07-28, WebFetch로 확인)
저자: Sergio Paniego, Aritra Roy Gosthipaty (128명 이상 기여). 게시일: 2026-05-25.

원문 핵심:
- "Many of these terms don't have universally accepted definitions yet, and different frameworks use the same word differently." — **표준화 안 됐다는 명시적 선언.**
- 저자들이 제안하는 구분: **Scaffold** = "The behavior-defining layer around the model: system prompt, tool descriptions, how the model's responses get parsed, what it remembers across steps (context management)." / **Harness** = "The execution layer inside the agent: it calls the model, handles its tool calls, decides when to stop."
- 그러나 동시에: "products like Claude Code, Codex, and Antigravity CLI call the whole thing a harness" — 즉 **실제 제품들은 이 구분을 지키지 않고 harness를 포괄 용어로 쓴다.** 저자들도 이를 "표준 강제"가 아니라 "논의를 쉽게 하기 위한 실용적 정신모형(practical mental model)"이라 자기 규정한다.
- 촉발 배경: 2026 ICLR 학회에서 관찰된 용어 혼란(전문 자료 원문 확인은 못했고 WebFetch 요약에 포함된 문구 — §8 모름 처리 필요할 수도 있으니 강의에서 "ICLR 2026에서 혼란이 있었다"는 세부는 재확인 없이 확정 사실처럼 쓰지 말 것).

### 3.3 Martin Fowler 사이트 — Birgitta Böckeler, "Harness engineering for coding agent users" (실무자 1차급, 매우 인용도 높은 채널)

URL: https://martinfowler.com/articles/harness-engineering.html (조회 2026-07-28, WebFetch로 확인)
저자: Birgitta Böckeler(ThoughtWorks). 게시일: 2026-04-02.

원문 핵심:
- "Agent = Model + Harness"라는 등식을 기초로 삼되, 코딩 에이전트에 좁혀 정의한다.
- 구성요소를 **Guides(피드포워드 통제)**: 문서(AGENTS.md, architecture.md), 스킬·지시문, 계산 도구(코드 모드, LSP 연동), 스크립트·설정 / **Sensors(피드백 통제)**: 정적 분석(린터·타입체커·ArchUnit 테스트), AI 기반 리뷰 에이전트, 테스트 스위트·뮤테이션 테스트, 커스텀 검증 메커니즘 — 2범주로 나눈다.
- **Deterministic(CPU가 빠르게 실행) vs Inferential(의미론적 분석, AI 코드 리뷰)** 구분을 명시적으로 강조.
- 저자 스스로 "an emerging informal term" 취급 — "Building this outer harness is emerging as an ongoing engineering practice, not a one-time configuration."라고 하여 **이것이 확립된 학문적 개념이 아니라 형성 중인 실무 관행**임을 인정.

### 3.4 Addy Osmani(Google 엔지니어) 블로그 — 용어 기원 추적

URL: https://addyosmani.com/blog/agent-harness-engineering/ (조회 2026-07-28, WebFetch로 확인). 게시일: 2026-04-19.

- **저자가 직접 출처를 밝힘**: "Viv Trivedy coined the term _harness engineering_." — 즉 이 용어는 특정 개인이 만든 조어이며, Anthropic·OpenAI 같은 회사의 공식 정의도 아니다. (Viv Trivedy가 누구인지, 어느 소속인지는 이번 조사에서 추가 검증 못함 — §8 모름.)
- "Agent = Model + Harness. If you're not the model, you're the harness." "every piece of code, configuration, and execution logic that isn't the model itself."
- 구성요소로 나열: 시스템 프롬프트·스킬 파일(CLAUDE.md, AGENTS.md), 도구·스킬·MCP 서버 설명, 인프라(파일시스템·샌드박스·브라우저), 오케스트레이션 로직(서브에이전트 스폰·핸드오프·라우팅), 훅·미들웨어, 관찰가능성(로그·트레이스·미터링).
- "Harness-as-a-Service"·"model-harness training loop" 등은 저자가 "여러 코딩 에이전트(Claude Code, Cursor, Codex, Aider, Cline)에 걸쳐 수렴 중인 관행"이라 주장하나, **이는 저자 개인의 관찰·주장이지 검증된 산업 표준 조사가 아니다.**

### 3.5 METR — "scaffolding"이 이 분야에서 더 오래되고 실제로 학술 평가 방법론에 쓰이는 용어

URL: https://metr.org/evaluations/gpt-4o-report/ (조회 2026-07-28, WebFetch로 확인). 게시일: 2024-08-07.

원문:
- "our methodology involves using **scaffolding programs** to make **agents** out of language models."
- "All the agents used in this report are derived from essentially the same scaffolding program with only minor modifications. This scaffolding is relatively simple, providing the agent with only bash, python, and answer-submission tools."
- "It is nonetheless plausible that many of the agents' mistakes could be fixed or avoided through better scaffolding and finetuning."
- 관련 개념 **elicitation**: "We refer to the process of iteratively modifying an agent in an attempt to improve its performance as elicitation." — 패치 실험에서 스캐폴딩을 수동으로 고쳐 실패했던 10건 중 4건을 성공시킴 → **스캐폴딩 개선이 같은 모델에서 더 많은 능력을 이끌어낼 수 있다(capability elicitation)는 것을 METR이 실증**.

**판정**: "scaffolding"은 "harness"보다 먼저(2024년부터 METR 보고서에 반복 등장) AI 안전성/역량평가 커뮤니티에서 자리잡은 용어다. "harness"는 2026년 들어 코딩 에이전트 실무자 사이에서 급부상한 더 최근의 유행어(neologism)로 보이며, 두 용어가 가리키는 대상은 겹치지만 기원 커뮤니티가 다르다(evals 커뮤니티=scaffolding, 코딩에이전트 실무=harness).

### 3.6 학술 문헌 진입 여부 — arXiv 서베이/논문 확인

- **"Code as Agent Harness"** (arXiv:2605.18747, 제출 2026-05-18, 저자 Xuying Ning, Katherine Tieu, Dongqi Fu 외 39인) — 조회 2026-07-28. 초록 원문: "We frame this shift through the lens of agent harnesses and introduce code as agent harness: a unified view that centers code as the basis for agent infrastructure." 이 논문은 "harness"를 **정의하지 않고 이미 통용되는 개념으로 전제**하고 쓴다.
- **"Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"** (arXiv:2604.25850, 제출 2026-04-28, 저자 Jiahang Lin 외) — 조회 2026-07-28. "Harnesses are now central to coding-agent performance, mediating how models interact with tools and execution environments." 역시 **용어를 정의하지 않고 기정사실처럼 사용**하며, 자동화 대상이 "a manual craft"(harness engineering)라고 서술 — 즉 이 논문도 "harness engineering이 수작업 실무 관행"이라는 전제를 깔고 있다(학술적으로 확립된 정의가 있다고 주장하지 않음).
- **판정**: 2026년 상반기에 "agent harness"라는 표현이 arXiv 논문 제목·본문에 등장하기 시작했다는 것은 **용어가 학계로 확산되고 있다는 증거**이지, **오래 확립된 학술 용어라는 증거는 아니다.** 두 논문 모두 정의를 내리지 않고 이미 유통되는 실무 용어를 그대로 받아썼다.

### 3.7 관련 용어 지형: harness vs scaffold vs agent runtime vs framework

여러 벤더 블로그(Credal.ai, Salesforce, LangChain 공식 문서 등, 검색 스니펫으로만 확인 — WebFetch 직접 검증 안 함, §7 로그)에서 공통적으로 제시하는 3층 모델:
- **Framework**(LangChain, LangGraph 등): 에이전트를 조립하는 코드 라이브러리.
- **Runtime**: 에이전트가 실제로 실행되는 인프라 격리·거버넌스 계층("Lambda for agents"라는 비유가 반복됨).
- **Harness**: 위 둘을 감싸고 워크플로·가드레일·배포 통합을 더하는 층.
- 이 3층 구분 역시 **1차 벤더 문서 하나로 검증하지 않았으므로 강의에서 "업계가 합의한 3층 모델"이라 가르치면 안 된다.** LangChain 공식 문서(docs.langchain.com/oss/python/concepts/products)를 직접 fetch하지 못했다 — §7.

### 3.8 프롬프트 엔지니어링·컨텍스트 엔지니어링과의 관계

URL: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents (조회 2026-07-28, WebFetch로 확인). 게시일: 2025-09-29 (Anthropic 공식, 500K+ 조회수라는 2차 보도 있음 — 조회수 수치 자체는 검증 안 함).

원문 핵심:
- **컨텍스트 엔지니어링 정의**: "the set of strategies for curating and maintaining the optimal set of tokens (information) during LLM inference, including all the other information that may land there outside of the prompts." 더 넓게는 "the art and science of curating what will go into the limited context window from that constantly evolving universe of possible information."
- **프롬프트 엔지니어링과의 차이**: 프롬프트 엔지니어링은 "methods for writing and organizing LLM instructions for optimal outcomes"로 1회성 작업에 가깝고, 컨텍스트 엔지니어링은 "curation phase happens each time we decide what to pass to the model"이라는 반복적 과정이며 "system instructions, tools, Model Context Protocol (MCP), external data, message history, etc." 전체 상태를 관리한다.
- 시스템 프롬프트: "extremely clear and use simple, direct language"이되 "brittle if-else hardcoded prompts"와 "overly general" 사이 균형.
- 도구: "self-contained, robust to error, and extremely clear with respect to their intended use."
- 메모리: 에이전트가 "notes persisted to memory outside of the context window"를 유지해 "persistent memory with minimal overhead"를 얻는다.
- **에이전틱 루프**를 이 문서는 단순하게 "LLMs autonomously using tools in a loop"라고 정의.

**판정**: 컨텍스트 엔지니어링은 Anthropic이 2025-09 공식 블로그로 낸 **비교적 명확히 정의된 개념**이며(하네스보다 훨씬 더 단일 출처가 명료함), "하네스"의 구성요소 중 "Guides/시스템 프롬프트·도구·메모리" 부분과 상당히 겹친다. 즉 **컨텍스트 엔지니어링 ⊂ 하네스(실무자 정의상)** 관계로 볼 수 있다 — 하네스가 더 넓은 우산 용어(실행 로직·권한·관찰가능성까지 포함)이고 컨텍스트 엔지니어링은 그 중 "모델에 무엇을 보여줄지" 부분에 집중한다.

### 3.9 구성요소별 1차 근거 vs 실무 관행 구분표

| 구성요소 | 1차 근거 있음 | 실무 관행/미검증 |
|---|---|---|
| 목표(goal) | Anthropic·OpenAI 둘 다 명시(에이전트가 워크플로 완료를 인식) | - |
| 도구(tools) | Anthropic·OpenAI·Fowler·Osmani 전원 명시 | - |
| 컨텍스트/메모리 | Anthropic "context engineering" 블로그(1차, 명확) | HF 글로서리의 "scaffold=메모리" 구분은 저자 제안일 뿐 |
| 규칙/지시문(instructions) | OpenAI 3요소 중 하나로 명시 | - |
| 권한(permissions) | Fowler article에 명시(guides 범주) | 표준화된 권한모델 명세는 확인 못함 |
| 검증(verification/evals) | METR scaffolding-elicitation 실증, OpenAI guardrails 챕터 | - |
| 기록(observability/logs) | Osmani 블로그에 명시 | 1차 학술 근거는 못 찾음(§8) |
| 복구(recovery/checkpoint) | Anthropic "pause for human feedback at checkpoints" | 정형화된 "체크포인트 표준"은 확인 못함 |
| 스킬(skills) | Osmani·Fowler 둘 다 언급(스킬 파일) | 벤더별 구현이 전혀 다름(Claude Code Skills vs 기타) — 표준 스펙 없음 |

---

## §4 강의용 변환 재료

### 4-A. 에이전트 vs 워크플로

- **실제 문제 상황**: 학생이 Codex에게 "이 버그 고쳐줘" 시켰더니 파일을 하나만 고치고 끝내는 경우(워크플로적 동작)와, 알아서 여러 파일을 뒤지고 테스트를 돌리고 실패하면 다른 방법을 시도하는 경우(에이전트적 동작)의 차이를 겪었을 것.
- **정식 용어**: 워크플로(workflow) / 에이전트(agent) / 오케스트레이션(orchestration) / 가드레일(guardrails) / 휴먼인더루프(human-in-the-loop).
- **정확한 정의**: Anthropic — 워크플로는 "미리 정해진 코드 경로로 LLM과 도구를 조율", 에이전트는 "LLM이 스스로 자신의 프로세스와 도구 사용을 동적으로 지휘". OpenAI — 에이전트는 "독립적으로 과업을 완수하는 시스템"이며 3요소(모델·도구·지시문)로 구성.
- **쉬운 설명**: 워크플로는 "레시피를 그대로 따라 요리하는 사람", 에이전트는 "냉장고 사정을 보고 레시피를 스스로 바꿔가며 요리하는 사람".
- **구조도로 그릴 관계**: Input → [Instructions/Tools/Guardrails/Hooks 다이아몬드] → Agent → Output 순환 루프(OpenAI 가이드 14쪽 다이어그램을 단순화해 재현 가능. 정확한 재현이 아니라 "느낌"만 빌리고 저작권상 원본 재사용 금지 — 새로 그릴 것).
- **비슷한 개념과 비교**: RPA(규칙기반 자동화) vs 에이전트 — RPA는 "if 조건이면 정확히 이 클릭"인 반면 에이전트는 판단이 들어감. 챗봇(단발 응답) vs 에이전트(다단계 실행+도구 호출) — OpenAI 원문 "simple chatbots, single-turn LLMs... are not agents"를 그대로 인용 가능.
- **언제 쓰나/안 쓰나**: OpenAI 6쪽 기준표(복잡한 판단·유지보수 어려운 룰셋·비정형 데이터 → 에이전트, 아니면 결정론적 해법으로 충분) 그대로 활용 가능.
- **실제 사례**: OpenAI 가이드의 결제 사기 탐지 비유(체크리스트형 규칙엔진 vs 노련한 수사관형 에이전트, 5쪽)를 각색해 학생 상황(자동 커밋봇 vs Codex 에이전트 모드)으로 치환.
- **실패 사례**: Anthropic — "Agents' autonomy means higher costs, and the potential for compounding errors." OpenAI — 재시도 한도 초과, 고위험 행동(환불 승인·결제) 시 반드시 사람 개입.
- **시연 후보**: ChatGPT의 단발 질문(워크플로적) vs Codex의 "파일 여러 개 스스로 뒤지며 테스트까지 돌리는" 모습(에이전트적)을 화면 녹화로 대비.
- **학습자 적용 후보**: 자신이 만든 웹페이지 프로젝트에서 "이건 에이전트가 처리했다/이건 그냥 규칙이었다"를 구분해보게 하기.
- **검증 방법**: "누가 다음 행동을 결정했는가?"(사람이 미리 정한 코드 경로 vs LLM이 그 순간 결정) 질문으로 워크플로/에이전트 구분 자가진단.

### 4-B. 하네스 엔지니어링

- **실제 문제 상황**: 학생이 Codex/Claude Code를 쓰면서 "왜 어떤 프로젝트에선 AI가 똑똑하게 일하고 어떤 프로젝트에선 헤매나"를 경험했을 것 — 답은 모델 차이가 아니라 그 프로젝트에 갖춰진 AGENTS.md, 테스트, 도구 설명 등 "주변 장치"의 차이다.
- **정식 용어(주의: 비표준임을 반드시 명시)**: 하네스(harness)/스캐폴딩(scaffolding)/에이전트 런타임(agent runtime). **"하네스"는 아직 업계 표준 용어가 아니며, Hugging Face조차 2026-05 "용어가 아직 합의되지 않았다"고 공식 선언했다는 점을 먼저 말해야 한다.**
- **정확한 정의(출처별로 다르다는 것 자체가 핵심 메시지)**: METR(2024, 더 오래됨) — "scaffolding programs... make agents out of language models"(bash/python/제출 도구 등 실행 골격). Fowler/Böckeler(2026) — "Agent = Model + Harness", Guides(문서·스킬·도구)+Sensors(린터·테스트·AI리뷰)로 구성. Osmani(2026, Viv Trivedy 조어 인용) — "모델이 아닌 모든 것"(코드·설정·실행로직 전체). Hugging Face(2026) — scaffold(모델이 보는 것을 결정)와 harness(실행을 결정)를 개념적으로 분리하되, 실제 제품들은 이 구분 없이 "harness"로 통칭한다고 인정.
- **쉬운 설명**: 에이전트가 "선수"라면 하네스는 "경기장·장비·코치의 지시사항·심판 규칙"에 해당한다는 비유(장비=도구, 코치 지시=시스템 프롬프트·AGENTS.md, 심판 규칙=가드레일, 경기 기록=관찰가능성).
- **구조도로 그릴 관계**: 중심에 Model, 그 바깥을 감싸는 원에 Harness(하위 항목: 지시문/도구/권한/메모리/검증/관찰가능성/복구), 그 바깥에 Runtime(샌드박스·인프라). "Model이 작아도 하네스가 좋으면 성능이 올라간다"는 METR 실증(패치 실험 10건 중 4건 성공)을 화살표로 표시.
- **비슷한 개념과 비교**: 프롬프트 엔지니어링(1회성 텍스트 작업) vs 컨텍스트 엔지니어링(매 턴 무엇을 모델에 보여줄지 계속 큐레이션하는 과정, Anthropic 2025-09 정의) vs 하네스 엔지니어링(그 위에 실행 로직·권한·관찰가능성까지 포괄하는 더 넓은 실무 개념). 세 용어 중 컨텍스트 엔지니어링만 Anthropic이라는 단일 신뢰 출처의 명확한 정의가 있고, 하네스는 여러 출처가 서로 다르게 쓴다.
- **언제 쓰나/안 쓰나**: 장기실행·다단계 코딩 에이전트를 실무에 투입할 때(AGENTS.md, 테스트 스위트, 권한 스코프 설계가 실제로 필요) 유용한 사고 프레임. 단발성 질문-답변용 챗봇에는 이 개념을 굳이 안 써도 됨.
- **실제 사례**: 이 저장소 자체가 좋은 예시 — `AGENTS.md`(지시문/가드), `scripts/verify_*.py`(검증/센서), `.claude/skills/`(스킬 어댑터) 구조가 정확히 Fowler의 Guides+Sensors 모델과 대응된다(강사가 자기 프로젝트를 직접 보여줄 수 있음).
- **실패 사례**: METR — 스캐폴딩이 부실하면(도구 3개뿐인 단순 스캐폴딩) 모델이 잘 아는 문제도 실패. 하네스 없이 "그냥 좋은 모델만 쓰면 되지"라는 생각이 위험한 오개념(§6).
- **시연 후보**: 같은 모델에 AGENTS.md 없이 작업 시키기 vs AGENTS.md 있는 상태로 작업 시키기 비교(이 저장소 자체가 실제 사례).
- **학습자 적용 후보**: 자신의 프로젝트에 "이 작업엔 어떤 하네스 요소(문서/테스트/도구설명)가 필요할까"를 표로 채워보기.
- **검증 방법**: "이 용어를 쓴 사람이 회사 공식 문서인지, 개인 블로그인지, 학술 논문인지"를 학생이 구분하는 연습(출처 판별 자체가 이 개념의 핵심 학습 포인트).

---

## §5 주장·출처 표

| 주장 | 출처 | URL | 유형 | 조회일 |
|---|---|---|---|---|
| 워크플로="predefined code paths", 에이전트="LLMs dynamically direct their own processes" | Anthropic, "Building Effective Agents" | anthropic.com/engineering/building-effective-agents | 1차(공식 엔지니어링 블로그) | 2026-07-28 |
| 에이전트는 "systems that independently accomplish tasks", 3요소=Model+Tools+Instructions | OpenAI, "A practical guide to building agents" (PDF 원문 33p) | cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf | 1차(공식 백서) | 2026-07-28 |
| ReAct: reasoning traces + acting를 인터리빙, chain-of-thought의 환각/오류전파 극복 | Yao et al., "ReAct" | arxiv.org/abs/2210.03629 | 1차(학술 논문, 2022) | 2026-07-28 |
| 자율성 5단계(operator~observer)는 저자들이 새로 제안한 프레임워크(기존 표준 없음) | Feng, McDonald, Zhang, "Levels of Autonomy for AI Agents" | arxiv.org/abs/2506.12469 | 1차(학술 논문, 2025) | 2026-07-28 |
| "많은 (하네스/스캐폴드) 용어가 아직 보편적으로 합의된 정의가 없다" | Hugging Face, "Harness, Scaffold, and the AI Agent Terms Worth Getting Right" | huggingface.co/blog/agent-glossary | 1차급(업계 메타 자료, 2026-05-25) | 2026-07-28 |
| "harness engineering"은 Viv Trivedy가 만든 조어 | Addy Osmani 블로그 | addyosmani.com/blog/agent-harness-engineering | 실무자 블로그(2차 성격, 2026-04-19) | 2026-07-28 |
| Agent = Model + Harness; Guides(문서·스킬·도구)+Sensors(린터·테스트) 2범주 | Birgitta Böckeler, Martin Fowler 사이트 | martinfowler.com/articles/harness-engineering.html | 실무자 1차급(저명 채널, 2026-04-02) | 2026-07-28 |
| "scaffolding programs... make agents out of language models"(도구=bash/python/제출만) | METR, GPT-4o 평가 보고서 | metr.org/evaluations/gpt-4o-report | 1차(평가기관 공식, 2024-08-07) | 2026-07-28 |
| 컨텍스트 엔지니어링="curating optimal set of tokens", 프롬프트엔지니어링과 달리 매 턴 반복되는 과정 | Anthropic, "Effective context engineering for AI agents" | anthropic.com/engineering/effective-context-engineering-for-ai-agents | 1차(공식 블로그, 2025-09-29) | 2026-07-28 |
| "Code as Agent Harness"·"Agentic Harness Engineering" 두 논문 모두 harness를 정의 없이 기정사실처럼 사용 | arXiv 2605.18747 / 2604.25850 | arxiv.org/abs/2605.18747 , arxiv.org/abs/2604.25850 | 1차(학술 서베이/논문, 2026) | 2026-07-28 |

---

## §6 위험한 오개념

1. **"하네스는 업계 표준 학술 용어다"** — 틀림. Hugging Face 자체가 "아직 보편 합의 정의가 없다"고 명시했고(§3.2), 용어를 처음 쓴 사람도 특정 개인(Viv Trivedy, Osmani 블로그 주장)으로 거슬러 올라간다. 특정 회사·개인의 조어를 정설처럼 가르치면 안 된다.
2. **"에이전트는 워크플로보다 항상 더 좋은 상위 개념이다"** — 틀림. Anthropic·OpenAI 둘 다 "결정론적 워크플로로 충분하면 에이전트를 쓰지 말라"고 명시적으로 경고한다(복잡성·비용·오류누적 증가).
3. **"좋은 모델만 있으면 하네스는 안 중요하다"** — 틀림. METR의 패치 실험(동일 모델, 스캐폴딩만 수정 → 실패 10건 중 4건 성공)이 정반대를 보여준다.
4. **"자율성 레벨은 SAE 자율주행처럼 업계가 합의한 0~5단계 표준이 있다"** — 틀림. Feng et al.(2025)의 5단계와 Google 백서(2차 경유)의 5단계는 서로 다른 기준의 별개 제안이다. "5단계"라는 숫자가 같다고 같은 체계가 아니다.
5. **"harness와 scaffold는 같은 뜻이다" 또는 "완전히 다른 뜻이다"라고 단정** — 둘 다 위험. Hugging Face는 개념적으로 분리하려 시도하지만 동시에 "실제 제품(Claude Code, Codex 등)은 이 구분 없이 harness로 통칭한다"고 인정한다. 정답은 "출처마다 다르게 쓴다"는 것 자체다.
6. **"ReAct 논문이 OpenAI/Anthropic의 공식 인용 출처다"** — 확인 안 됨. ReAct가 에이전트 루프의 학술적 기원인 것은 맞지만, 이번 조사에서 Anthropic·OpenAI 문서가 ReAct를 직접 인용하는 것은 확인하지 못했다(§8). 이 연결을 "공식적으로 인정된 계보"처럼 가르치면 과장이다.

---

## §7 조사 실패 로그

| 시도 URL | 사유 |
|---|---|
| https://www.kaggle.com/whitepaper-introduction-to-agents | WebFetch가 페이지 타이틀만 반환하고 본문(백서 실제 텍스트)을 가져오지 못함(SPA/동적 로딩 추정). 2차 요약(vanducng.dev)으로 대체했으나 원문 검증 불가 상태로 표시함. |
| https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/ | HTTP 403 Forbidden. 대신 cdn.openai.com의 PDF 직링크를 Read 도구로 직접 읽어 원문 확보(성공). |
| WebSearch 쿼리 "agent harness" OR "coding agent harness" scaffolding (1차 시도) | "Web search error: unavailable" — 도구 일시 장애. 재시도로 다른 쿼리는 성공. |
| WebSearch 쿼리 OpenAI guide "what is an agent" quote (일부 시도) | 동일하게 일시 unavailable 응답 후 재시도 성공. |
| https://metr.org/research/ | 페이지에 "scaffolding" 언급은 있으나(GPT-4o 77개 태스크 등) 정의 문장 자체는 없음 — 대신 metr.org/evaluations/gpt-4o-report/를 직접 fetch해 정의 문장 확보(성공). |
| LangChain 공식 문서(docs.langchain.com/oss/python/concepts/products), Credal.ai, Salesforce 블로그 (harness vs runtime vs framework 3층 모델 출처) | 검색 스니펫으로만 확인, WebFetch로 직접 검증하지 않음. §3.7에 "1차 검증 안 됨"으로 명시 처리. |
| Hugging Face 블로그의 "ICLR 2026에서 관찰된 혼란" 언급 | WebFetch 요약에 포함된 문구를 그대로 전달했으나 원문 전체 재확인은 안 함 — 세부 사실(구체적으로 ICLR에서 무슨 일이 있었는지)은 검증 안 된 상태. |

---

## §8 모름

- Anthropic의 5대 워크플로 패턴(prompt chaining, routing, parallelization, orchestrator-worker, evaluator-optimizer) 각각의 정확한 원문 정의 — 이번 조사에서 재확인 안 함(§2.1에서 초록 수준 요약만 확인, 세부 패턴별 원문 인용 미실시).
- Viv Trivedy의 소속·"harness engineering" 조어의 최초 발행 시점·매체 — Osmani 블로그의 주장만 확인, 1차 출처(Trivedy 본인 글)는 못 찾음.
- Google Kaggle 백서의 정확한 원문 인용(정의·자율성 5단계) — 2차 요약에만 의존, 원문 직접 검증 실패.
- LangChain 공식 문서의 "framework/runtime/harness" 3층 모델 정확한 원문 — 검색 스니펫만 확인.
- "체크포인트"·"복구(recovery)" 개념에 대한 학술적으로 확립된 표준 정의 존재 여부 — Anthropic 문서의 "pause at checkpoints" 언급 외에 더 정교한 1차 자료를 찾지 못함.
- ReAct 논문을 Anthropic·OpenAI 공식 문서가 실제로 인용하는지 여부 — 확인 못함(§6-6 참고).
