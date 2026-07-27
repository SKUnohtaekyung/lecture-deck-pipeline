# 2주차 신규개념·차용주장 검증 보고서

> 작성: gap-concept-researcher (Sonnet) · 조사일 2026-07-27
> 방법: WebSearch + WebFetch 1차 출처 직접 열람. 재현 못한 소스는 「검색 실패 로그」에 URL·사유 기재.

---

## TASK 1 — 레퍼런스 PM덱 차용 주장 검증

### 1. MVP 정의 — Eric Ries vs Frank Robinson
- **주장:** MVP는 린스타트업 개념으로 Eric Ries가 만들었다.
- **1차 출처:** Ries — http://www.startuplessonslearned.com/2009/08/minimum-viable-product-guide.html (2009-08-03) / Robinson — https://www.skmurphy.com/blog/2017/04/24/frank-robinsons-minimum-viable-product-definition/
- **실제 내용:** **오귀속 주의.** 용어를 먼저 쓴 사람은 Frank Robinson(SyncDev, **2001년**)이며 그의 정의는 "**the product with maximum ROI divided by risk**" — 위험 대비 최대 ROI를 내는, 크지도 작지도 않은 '적정 크기' 제품이다. Ries는 이 용어를 대중화한 사람으로, 그의 정의는 "**the version of a new product which allows a team to collect the maximum amount of validated learning about customers with the least effort**" — 최소 노력으로 고객에 대한 **검증된 배움**을 최대로 얻는 버전. 두 정의는 강조점이 다르다: Robinson=ROI/리스크 최적화, Ries=학습 최적화(가설 검증). Ries 자신도 "MVP가 아니라도 될 때가 있다"고 단서를 단다.
- **최신성:** 원 정의 자체는 시대 불변(historical fact). evergreen.
- **가르칠 안전한 형태:** "MVP라는 말은 2001년 Frank Robinson이 먼저 썼고(적정 크기·ROI 관점), 2009년 Eric Ries가 린스타트업의 '검증된 학습' 개념으로 대중화했다"처럼 **두 계보를 구분**해 가르친다. "Ries가 만든 용어"라고 단정하면 오귀속.
- **판정: 조건부 사용가능** — Ries 단독 발명자 서술은 금지, 두 출처 병기 시 사용 가능.

### 2. "MVP는 자동차가 아니라 스케이트보드" 비유
- **주장:** Henrik Kniberg가 스케이트보드→자동차 그림으로 MVP를 설명했다.
- **1차 출처:** https://blog.crisp.se/2016/01/25/henrikkniberg/making-sense-of-mvp
- **실제 내용:** 그림 자체는 Kniberg 블로그 게시물(2016)에 실렸고, 스케이트보드→킥보드→자전거→오토바이→자동차 단계별로 **매 단계가 그 자체로 완결된 가치**를 준다는 메타포다. **Kniberg 본인이 흔한 오용을 경고**한다: "The picture is a metaphor. It is not about actual car development, it is about product development in general" — 문맥 없이 그림만 떼어 보면 오해하기 쉽다고 명시. 그는 나아가 'MVP'라는 용어 자체가 모호하다며 **Earliest Testable / Usable / Lovable Product**로 대체할 것을 제안한다 — "Few customers want 'minimum' but most customers want 'early'!"
- **최신성:** 2016년 원 포스트, evergreen(저자 본인이 여전히 재인용).
- **가르칠 안전한 형태:** 그림을 쓰되 "저자 본인이 문맥 없이 보면 오해하기 쉽다고 경고했다"는 단서를 함께 전달하고, "완벽한 자동차의 축소판(스케이트보드=반쪽짜리 차)"이 아니라 "그 자체로 다 타는 탈것"이라는 원래 요지를 정확히 전달한다.
- **판정: 사용가능(조건부 — 원저자의 오용 경고를 함께 전달)**.

### 3. MoSCoW 우선순위
- **주장:** DSDM에서 Dai Clegg가 만들었다.
- **1차 출처:** https://www.agilebusiness.org/dsdm-project-framework/moscow-prioritisation.html
- **실제 내용:** 확인됨. Dai Clegg(1994, Oracle 재직 중 *Case Method Fast-Track*에서 발표)가 고안했고 DSDM(현 Agile Business Consortium)이 채택했다. 공식 정의: **Must Have**="Minimum Usable SubseT — 반드시 전달을 보장하는 최소집합", **Should Have**="중요하지만 없어도 해법이 여전히 유효함(important but not vital)", **Could Have**="있으면 좋지만 덜 중요, 빠져도 영향 작음", **Won't Have (this time)**="이번 타임프레임에는 전달하지 않기로 합의한 것"(다음 회차 배제 아님).
- **최신성:** 공식 프레임워크 문서, evergreen.
- **가르칠 안전한 형태:** 그대로 가르쳐도 되는 몇 안 되는 항목. "Won't = 영원히 안 함"이 아니라 "이번엔 안 함"이라는 뉘앙스만 정확히 전달하면 된다.
- **판정: 사용가능**.

### 4. "결함을 늦게 발견할수록 수정 비용이 급증한다"(Boehm 곡선)
- **주장:** 요구사항 단계에서 잡으면 1, 출시 후 잡으면 100배 등 비용 급증 곡선.
- **1차 출처(비판):** Laurent Bossavit, *The Leprechauns of Software Engineering* 요지(원문 사이트 접속 실패, 아래 검색 실패 로그 참조) / Mountain Goat Software 요약(직접 페치 실패, 검색 스니펫만 확보).
- **실제 내용:** Bossavit의 분석에 따르면 Boehm이 인용한 원 연구들이 **재현 불가능하거나 왜곡 인용**됐고, 심지어 한 연구는 Boehm 주장과 **반대 방향(2:1)** 결과를 보였다고 지적된다. 2006~2014년 171개 프로젝트를 본 최근 실증 연구는 "결함을 일찍 찾을수록 노력이 준다"는 가설을 뒷받침하지 않았고, 애자일·신기술이 곡선을 평탄화했을 가능성을 제기한다. 즉 **구체적 배수(10배·100배 등)는 근거가 약하고, 재현·반박 논쟁이 진행 중**이다.
- **최신성:** 논쟁 진행형 — 확정된 정설 아님.
- **가르칠 안전한 형태:** 숫자·배수를 인용하지 말고, **정성적 원칙만** 가르친다 — "설계 문서(PRD)에서 미리 정하고 조율하는 게, 코드를 다 만들고 나서 뜯어고치는 것보다 대체로 수월하다"는 상식 수준 진술로 대체. "몇 배 든다"는 도표·수치는 쓰지 않는다.
- **판정: 조건부 사용가능(수치 인용 절대 금지, 정성적 원칙만)** — 정본 지시(과제 프롬프트)와 일치.

### 5. Pain Point 판정 3기준(빈도·강도·대안)
- **주장:** 페인포인트를 빈도·강도·대안(경쟁 대안 유무)의 3기준으로 판정한다.
- **1차 출처:** 확립된 단일 출처 없음 — PainOnSocial(https://painonsocial.com/blog/pain-point-metrics), Kaizenko(https://www.kaizenko.com/five-questions-to-evaluate-whether-a-pain-point-is-worth-solving/) 등 다수 실무 블로그가 유사하지만 조금씩 다른 조합을 쓴다.
- **실제 내용:** 빈도(frequency)·강도(intensity/severity)는 여러 출처에서 반복되는 핵심 두 축이지만, 셋째 축은 출처마다 다르다 — reach(도달 인원), willingness-to-pay(지불 의향), solvability(해결 가능성) 등으로 갈리며 "대안(경쟁 대안 유무)"을 명시한 표준화된 원전은 찾지 못했다. **학계·업계가 합의한 정식 프레임워크가 아니라, 강의·컨설팅용으로 흔히 재구성되는 휴리스틱**이다.
- **최신성:** 계속 변형되는 실무 관행, 원전 고정 안 됨.
- **가르칠 안전한 형태:** "이건 확립된 이론이 아니라, 페인포인트를 빠르게 걸러보는 질문 3가지"라고 **출처를 명시하지 않고 실용적 체크리스트로만** 제시한다. "OO이 만든 프레임워크"처럼 권위를 붙이지 않는다.
- **판정: 조건부 사용가능(강의용 정리로 명시, 학술적 근거처럼 인용 금지)**.

---

## TASK 2 — 바이브코딩 갭 개념

### 1. AGENTS.md
- **1차 출처:** https://agents.md/ (Agentic AI Foundation / Linux Foundation 산하)
- **현재 동작:** 저장소 루트에 두는 게 기본, 큰 프로젝트는 하위 패키지마다 추가 배치 가능("Place another AGENTS.md inside each package"). **우선순위 = 편집 대상 파일에 가장 가까운 AGENTS.md가 이긴다**("the closest one takes precedence"), 그리고 **사용자의 명시 채팅 지시가 이 모든 것보다 우선**한다. 내용은 자유 형식 Markdown — 빌드/테스트 명령, 코드 스타일, "새 팀원에게 말해줄 모든 것". Codex·Cursor·Copilot·Gemini CLI·Aider·Windsurf·Zed 등 20종 이상 도구가 읽는다.
- **커리큘럼 대조:** 2주차 KB `[C-AGENTS문서]`(구간5, P1)에 이미 있음 — 기존 커버리지에 **정확도 보강 여지**: 현재 KB가 "가장 가까운 파일 우선" 규칙과 "사용자 채팅이 파일보다 우선" 규칙까지 명시했는지 원문(sessions/2주차/자료/2주차_개념KB.md L798 이하)을 대조 필요(본 조사는 해당 블록 본문까지는 열지 않음 — 후속 확인 권고).
- **판정: 사용가능(이미 커버리지 존재, 우선순위 규칙 정확도만 재확인 권고)**.

### 2. Codex 사용 흐름 (승인·샌드박스)
- **1차 출처:** https://learn.chatgpt.com/docs/agent-approvals-security (구 URL developers.openai.com/codex/... 은 308로 이 주소로 영구 리다이렉트됨 — 공식 문서 이전 확인)
- **현재 동작:** 기본 프리셋은 **"Auto"** = 샌드박스 `workspace-write` + 승인정책 `on-request`. 이 조합에서 Codex는 **작업 폴더 안** 파일 읽기·수정·명령 실행은 승인 없이 자동으로 하고, **작업 폴더 밖 파일 수정·네트워크 접근·샌드박스 탈출 가능성이 있는 동작**에서만 멈춰 승인을 요청한다. 그 외 `read-only`(질문·읽기만, 변경엔 항상 승인 필요), `danger-full-access`(`--yolo`, 모든 제한 해제 — 비권장)가 있다.
- **커리큘럼 대조:** 1주차 KB `[C-코딩에이전트]`가 "구체적 승인 경계는 2구간(C-권한승인)의 몫"이라 명시 위임해 뒀음 — 이 조사 결과가 그 위임된 상세 근거로 바로 쓸 수 있다.
- **판정: 사용가능** — "기본값=Auto=폴더 안은 자동, 폴더 밖·네트워크만 물어봄"으로 가르치면 정확하고 안전.

### 3. `file://` 직접 열기의 제약
- **1차 출처:** MDN 동일-출처 정책 — https://developer.mozilla.org/en-US/docs/Web/Security/Defenses/Same-origin_policy
- **정확한 현재 설명:** "최신 브라우저는 `file:///` 스킴으로 연 파일의 오리진을 대개 **불투명 오리진(opaque origin)** 으로 취급한다. 즉 같은 폴더의 다른 파일을 불러와도 같은 오리진으로 간주되지 않아 **CORS 오류**를 유발할 수 있다." 단, URL 명세는 파일의 오리진 처리를 **구현체 종속(implementation-dependent)** 이라 규정하며, 브라우저에 따라 같은 폴더/하위폴더 파일을 동일 오리진처럼 취급하기도 한다(이는 보안 함의가 있음, CVE-2019-11730 언급). `type="module"` 스크립트는 CORS 활성 요청으로 fetch되므로 `file://`에서는 오리진이 `null`로 취급돼 거의 항상 차단된다.
- **최신성:** MDN 현행 문서(진행형 웹표준 서술).
- **가르칠 안전한 형태:** "브라우저마다 file://를 다루는 방식이 100% 통일돼 있지 않지만, 대부분은 폴더 안 파일끼리도 서로 다른 출처로 보고 막는다 — 그래서 module 스크립트·fetch가 file://에서 깨지는 걸 '버그'가 아니라 '보안 설계'로 이해해야 한다"로 가르치면 정확. "모든 브라우저가 항상 이렇게 동작한다"는 절대적 단정은 피한다(명세가 구현체 종속이라 명시).
- **커리큘럼 대조:** 2주차 KB `[C-file프로토콜]`·`[C-기술제한]`·`[C-브라우저직접실행]`에 이미 있음 — 이 조사로 "구현체 종속" 뉘앙스를 보강할 여지.
- **판정: 사용가능(이미 커버리지, 정밀도만 보강)**.

### 4. 초보자가 AI 코딩 도구에서 자주 겪는 실패 유형
- **1차 출처 탐색 결과:** **단일 권위 있는 분류체계 없음.** 학술적으로 가까운 것은 Perry et al., *Do Users Write More Insecure Code with AI Assistants?* (ACM CCS 2023, https://arxiv.org/abs/2211.03622) — AI 어시스턴트를 쓴 참가자가 5문항 중 4개에서 **더 안전하지 않은 코드**를 작성했고, 동시에 **자기 코드가 안전하다고 더 확신**했다는 실증 결과(스탠퍼드·UCSD). 다만 이 연구는 **보안 취약점**에 초점이라 2주차(서버 없는 정적 페이지, 보안 표면 거의 없음)에는 적합도가 낮다.
- 그 외 "9 Failure Modes"(beginnersinai.org), "10 Failure Modes"(codewithrigor.com), "8 Failure Patterns"(augmentcode.com) 등은 **모두 벤더/실무자 블로그**로, 동료심사 연구가 아니다. 다만 여러 독립 출처가 유사한 범주로 수렴한다: 엣지케이스 누락, 보이지 않는 요구사항 놓침, 그럴듯해 보여 검토 없이 수용("looks right"), 좁은 범위의 임시방편 수정.
- **가르칠 안전한 형태:** "정식으로 확립된 분류는 아니지만, 실무자들이 공통으로 지적하는 패턴"이라는 단서를 달고 **1~2개(엣지케이스 누락·검토 없이 수용)만** 뽑아 쓴다. 벤더 블로그의 "N가지 실패 유형" 표를 그대로 권위 있는 자료처럼 인용하지 않는다.
- **판정: 조건부 사용가능(출처를 "실무 관찰"로 명시, 학술 근거처럼 포장 금지) / Perry et al.은 Task 3로 — 보안 초점이라 이 강의 범위 밖**.

### 5. 컨텍스트 길이·대화 누적에 따른 품질 저하 — U자 곡선 인용 검증
- **1주차 인용 대상:** `sessions/1주차/강의덱.초안/part-03.html`(L51-59)의 "Lost in the Middle / 중간 유실 현상" — 문서 20개 중 정답 위치별 정확도 75.8%(1번째)→53.8%(10번째)→63.2%(20번째), 무문서 기준선 56.1%.
- **1차 출처:** Liu et al., *Lost in the Middle: How Language Models Use Long Contexts*, TACL 12:157–173 (2024) / arXiv:2307.03172 — https://arxiv.org/abs/2307.03172
- **검증 결과:** arXiv 초록에서 논문 정체성·저자진(Liu, Lin, Hewitt, Paranjape, Bevilacqua, Petroni, Percy Liang)과 **U자형 성능 곡선 주장**("performance is often highest when relevant information occurs at the beginning or end... significantly degrades when models must access relevant information in the middle")을 직접 확인함. **부록 G Table 6의 정확한 5개 수치(75.8/57.2/53.8/55.4/63.2, 닫힌책 기준선 56.1)는 PDF 표 추출 실패로 이번 조사에서 독립 재확인하지 못했다**(아래 실패 로그). 다만 저장소 자체 출처레지스트리(`1주차_출처레지스트리.md` S-225)가 이미 "논문이 공개한 지점은 이 5개뿐, 나머지 15개는 보간·추정하지 않는다"는 신중한 각주를 달아둔 상태 — **인용 방식 자체는 이미 모범적으로 정확**하다.
- **판정: 사용가능** — 논문 정체성·핵심 주장은 확인됨. 수치 자체의 독립 재검증은 미완(로그 참조)이나 기존 인용이 이미 과장 방지 조치(보간 금지 각주)를 취하고 있어 위험 낮음.

### 6. 작업을 검증 가능한 단계로 나누기
- **1차 출처:** Anthropic, *Building Effective Agents* — https://www.anthropic.com/engineering/building-effective-agents (이미 1주차 KB에 S-106으로 등재됨)
- **현재 동작:** "프롬프트 체이닝(prompt chaining)"으로 태스크를 고정된 하위작업 시퀀스로 쪼개고, 각 LLM 호출이 이전 결과물을 처리하게 해 정확도를 높인다 — "작업을 쉽게·깔끔하게 고정 하위작업으로 나눌 수 있을 때" 적합하다고 명시.
- **커리큘럼 대조:** 이미 1주차 `[C-...]` 어딘가(또는 2주차 `[C-Task분할]`)에서 다루고 있을 가능성이 높음 — S-106이 이미 정본 출처로 등재돼 있어 **신규 출처 추가 불필요**, 기존 인용을 재사용하면 됨.
- **판정: 사용가능(신규 조사 불필요 — 이미 커버리지 존재)**.

---

## TASK 3 — 넣지 않아야 할 것

| 개념 | 사유 |
|---|---|
| Boehm 비용곡선의 구체적 배수(10배·100배 등) | 반박·재현실패 논쟁 진행형 — 숫자 인용 자체가 위험(Task 1-④ 참조) |
| Perry et al. 보안취약점 연구(ACM CCS 2023) | 2주차는 서버 없는 정적 페이지라 보안 표면이 거의 없음 — 대상 행동과 무관 |
| "AI 코딩 실패 9/10가지 유형" 식 벤더 블로그 표 전체 | 동료심사 없는 마케팅성 목록을 권위 있는 분류체계처럼 가르치면 과대포장 |
| Context rot(Chroma 연구) 구체 수치 | 1주차가 이미 "컨텍스트 로트"를 다루고 있고(Anthropic 공식문서 근거), Chroma의 별도 벤치마크 수치까지 얹으면 2주차 범위(정적 페이지 제작)에 불필요한 심화 |
| Pain Point 3기준의 "확립된 프레임워크" 서술 | 단일 원전이 없어 학술적 권위를 부여하면 오귀속(Task 1-⑤) |
| MoSCoW 외 확장 변형(예: MoSCoW+숫자 가중치, RICE 등 타 우선순위 기법) | 2주차는 스코핑 판단 하나만 필요 — 여러 우선순위 기법 비교는 입문자 인지부하만 늘림 |
| AGENTS.md의 세부 스펙 진화사(과거 버전과의 차이, 거버넌스 변천사) | 입문자에게는 "루트에 두고, 가까운 게 이긴다"만 필요 — 거버넌스 역사는 불필요 |
| Codex 승인모드의 `danger-full-access`(`--yolo`) 상세 사용법 | 입문자에게 권장되지 않는 위험 모드를 굳이 가르칠 필요 없음(존재만 언급하거나 생략) |

---

## 검색 실패 로그

| URL | 실패 사유 | 대응 |
|---|---|---|
| https://www.leprechaunsofsoftwareengineering.com/blog/2014/03/03/... (Bossavit, Boehm곡선 비판 원문) | DNS 실패(ENOTFOUND) — 도메인이 이전/폐쇄된 것으로 보임 | WebSearch 스니펫으로만 요지 확보(2차 인용), 정본 아님을 표기함 |
| https://www.mountaingoatstore.com/blog/the-cost-of-change-curve-is-outdated (Mountain Goat Software) | ECONNRESET(연결 재설정) — 재시도 안 함(효율상 검색 스니펫으로 대체) | WebSearch 결과 요지만 사용 |
| https://cs.stanford.edu/~nfliu/papers/lost-in-the-middle.arxiv2023.pdf (Lost in the Middle 원문 PDF) | WebFetch가 PDF를 텍스트로 파싱하지 못해 Table 6(부록 G) 수치를 추출 못함 — 논문 정체성·초록 주장은 arXiv abstract 페이지로 별도 확인함 | 저장소 자체 출처레지스트리(S-225)의 기존 verbatim 인용을 그대로 신뢰 — 그쪽이 이미 "5개 지점만 공개, 보간 금지" 각주를 갖추고 있어 위험 낮다고 판단 |

---

## 미확인 항목(후속 필요)

- 2주차 KB `[C-AGENTS문서]`·`[C-file프로토콜]`·`[C-기술제한]` 본문 전체(L798+, L770+, L729+)를 이번 조사에서 끝까지 읽지 않음 — "우선순위 규칙"·"구현체 종속" 뉘앙스가 이미 들어있는지는 덱 조립 전 별도 확인 권고.
