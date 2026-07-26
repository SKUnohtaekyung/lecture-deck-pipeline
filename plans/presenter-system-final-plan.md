# 발표 시스템(Presenter Runtime) 최종 실행 계획

## 1. 문서 목적과 상태

- **목적**: 강의덱 HTML의 발표 시스템(하단 네비 + 발표자 모드)을 kit 공통 런타임으로 정본화하고, 1주차 동결을 지킨 채 발표본을 산출하기까지의 **실행 계획 정본**.
- **상태**: 확정(FINAL). 이 문서가 구현의 정본이며, 구현 에이전트는 추가 아키텍처 설계 없이 §20의 단계를 순서대로 실행한다.
- **작성 근거**: 2026-07-26 기술 감사(대상 `sessions/1주차/1주차_강의안_발표자모드.html`, 58.9MB / 슬라이드 75장) + 사용자 확정 정책 8건 + 외부 보완 의견 A~L 검토.
- **이 문서를 읽는 순서**: §2 목표 → §6 폐기/보존 → §7~§17 설계 → §19~§25 실행. 감사 원문을 다시 읽을 필요는 없다.

---

## 2. 확정된 사용자 목표 (변경 금지)

1. 강사용 최종 전달물은 **외부 의존성 0의 단일 HTML 1개**.
2. 강사는 **`file://` 더블클릭**으로 실행할 수 있어야 한다.
3. 발표자 모드는 **일반 덱 조립 때 자동 생성되지 않는다**.
4. **사용자가 명시적으로 요청한 경우에만** 생성한다.
5. 발표 런타임은 **kit 공통 정본**으로 관리한다.
6. 여러 주차 덱에서 기능·디자인을 **일관되게 재사용**할 수 있어야 한다.
7. **1주차의 기존 조각·일반 덱·배포본은 동결 유지.**
8. 새로운 **발표본만 별도 산출물**로 생성한다.
9. 하단 네비게이션과 발표자 모드는 **하나의 슬라이드 상태**를 공유한다.
10. 발표자 UI에 라이트·다크 모드를 제공하되 **슬라이드 본문 디자인은 불변**.
11. 기존 발표자 노트의 **실제 멘트를 기본 메모로 탑재**한다.
12. 메모는 순번이 아니라 **안정적인 slideId**에 연결한다.
13. **저장 실패를 숨기지 않고 화면에 표시**한다.
14. 공식 지원: **Windows Chrome·Edge, macOS Chrome**.
15. **Safari는 실기기 검증 전까지 미지원**.
16. 1차 제외: Firefox · 모바일 리모컨 · Playwright · 메모 내보내기/가져오기.
17. 팝업 실패 시 **발표자 메모·다음 슬라이드를 청중 화면에 노출 금지**.
18. `/하네스`는 **SOLO 단일 라이터**.
19. **58.9MB HTML·base64를 LLM 컨텍스트로 읽거나 반복 출력 금지.**

---

## 3. 범위와 제외 범위

### 1차 범위
kit 런타임 2파일 신설 · 상태 단일화 · 경량 발표자 팝업 · 노트 기본 탑재 · slideId 메모 · 저장 실패 표시 · 발표 UI 라이트/다크 · 인쇄 정책 · 주입기 + 전용 검증기 · 검증기 신뢰 회복 · 1주차 발표본 1개 산출 · 수동 실기기 검증 · 성능 측정.

### 제외 범위
단일창 발표자 패널 · 메모 내보내기/가져오기 · 기기 간 메모 이전 · 모바일 리모컨 · 슬라이드 본문 다크모드 · 헤드리스 자동화(Playwright) · 파일 크기(58.9MB) 최적화 · **1주차 조각·`강의덱.html`·`강의덱_배포.html`·`강의덱_발표자노트.html`·`1주차_강의안_발표자모드.html` 수정** · `scripts/build_release.py` 수정(§14 판단).

---

## 4. 외부 피드백 수용·수정·거절 기록

| ID | 판단 | 이유 | 반영 절 |
|---|---|---|---|
| **A** 팝업 수명·bootstrap·HELLO | **수정 수용** | `unload`는 새로고침과 종료를 구분하지 못한다 → 종료 시 닫기 정책은 **새로고침마다 발표자 창을 죽인다**. 원안이 틀렸다. 팝업 내부 bootstrap은 팝업 자신의 JS 컨텍스트에서 실행되므로 부모 재로드 후에도 살아남고, `opener`가 새 부모를 가리키므로 **사용자 제스처 없이** 재연결할 수 있다(`window.open` 재호출은 팝업 차단 위험이 있어 원안이 열등). 단, 재채택 시 **문서를 전부 비우고 다시 그리는 절차**를 명시해야 죽은 리스너가 남지 않는다 | §9 |
| **B** postMessage 역할 | **수정 수용(제3안)** | 전면 postMessage는 슬라이드 DOM 직렬화를 강제해 비싸고, 전면 직접 DOM은 부모 재로드 시 팝업 버튼이 죽은 클로저를 가리킨다. **방향별 단일 경로**가 둘의 장점을 합친다 — 부모→팝업은 직접 DOM(직렬화 0), 팝업→부모는 postMessage(재로드 내성). 방향마다 경로가 정확히 하나라 상태 중복·중복 메시지가 구조적으로 불가능하다 | §9·§8 |
| **C** 식별자 추가 | **수정 수용(6→5)** | 필요성은 유효하나 `presentationSessionId`와 `pairingToken`은 같은 값으로 두 역할을 다 한다(부모가 생성해 팝업 bootstrap에 심고 두 창 밖으로 나가지 않는다). 또한 팝업은 `opener` 하나에만 말을 걸 수 있어 **다른 탭의 부모에 도달하는 것이 구조적으로 불가능**하므로 교차 오연결 방지는 토큰이 아니라 창 이름 고유화로 충분하다 | §10 |
| **D** localStorage/sessionStorage 분리 | **수용(퇴화 정책 추가)** | "이전 발표 타이머·위치가 다음 발표에 남는" 문제를 정확히 해결한다(현행 덱은 `localStorage`에 위치를 저장해 실제로 이 문제가 있다). 단 `file://`에서 sessionStorage 가용성이 보장되지 않으므로 **최선 노력 + 조용한 퇴화**를 명시한다(위치·타이머는 유실돼도 파괴적이지 않다) | §10 |
| **E** 빈 메모 allowlist 제거 | **수정 수용(제3안)** | allowlist 21행은 운영 비용만 늘린다. 그러나 의견대로 "노트 없음=정상"만 두면 **노트 파싱이 통째로 실패해 0건이 나와도 빌드가 통과**한다. allowlist 대신 **노트 항목 100% 소진 어서션**(파일의 `pn-slide` 개수 = 매핑 성공 개수)을 건다. 같은 안전성, 유지 비용 0 | §11 |
| **F** 노트 JSON 안전성 | **수용(전량)** | `</script>` 조기 종료는 실제 파싱 결함이고 비용이 거의 없다. `textContent` 렌더링도 필수 | §11 |
| **G** 사이드카 독립 검증 | **수용** | 스캔 횟수 제한은 **LLM 컨텍스트** 규율이지 Python I/O 예산이 아니다(사용자 지시도 둘을 구분). 사이드카만 믿으면 순환 검증이다. 검증기는 **원본과 발표본을 각각 직접 읽어 재계산**하고, 사이드카와의 불일치 자체를 FAIL로 본다 | §17 |
| **H** 미리보기 복제 안전성 | **수정 수용** | 실측상 `.deck` 안에 외부 리소스·iframe·video·audio가 없다(비-data `src/href` 0건, data URI 40건=이미지39+폰트1). `on*`·per-element `tabindex` 순회는 과잉이다. **최소 집합**(id 제거·script 제거·`aria-hidden`·CSS `pointer-events:none`)으로 같은 효과를 얻는다. 반대로 **폰트는 복사한다**로 원안을 뒤집는다 — 폰트 미복사 시 줄바꿈이 달라져 "다음 슬라이드 미리보기"가 실제 화면과 어긋난다. 폰트는 단일 서브셋 payload로 비용이 이미지보다 훨씬 작다 | §9 |
| **I** 명령 단일화 | **수정 수용(선택지 2 채택·선택지 1 거절)** | `build_release.py`는 **조각 폴더에서 전부 재생성**하므로 1주차에 쓰면 동결을 깬다(목표 #7 위반). 발표본 생성은 반드시 **완성된 단일 파일을 입력**으로 받아야 한다. 또한 `--presenter` 플래그를 일반 빌더에 달지 않으면 "일반 조립에 발표자 코드 없음"이 **플래그 기본값이 아니라 구조로** 보장된다(목표 #3 강화). `build_release.py`를 변경 목록에서 제거 | §14 |
| **J** 출력·사이드카 | **수정 수용** | `강의덱_발표.html`은 기존 `강의덱_배포.html`·`강의덱_발표자노트.html` 규약과 일관된다. 다만 사이드카까지 동결 폴더에 넣으면 추가 파일이 2개가 되므로 **`sessions/_verify/N주차/`로 분리**해 동결 폴더 추가를 전달물 1개로 최소화한다. `--force` 없이 덮어쓰기 금지 수용 | §14·§18 |
| **K** 번들 판별 마커 | **거절** | 신규 번들에 마커를 심으려면 일반 빌드 경로(`inline_deck.py`/`build_release.py`)를 고쳐야 하는데 이는 목표 #3의 폭발 반경을 키우고, **동결된 1주차 배포본에는 마커를 심을 수 없어 내용 기반 경로가 어차피 필요**하다. 두 메커니즘 병존은 검증 규칙만 복잡해진다. 내용 기반 단일 판정으로 파일명 의존 결함(실측: 같은 파일이 이름만 달라 raw색 74↔33, gradient FAIL↔PASS)을 완전히 제거한다 | §16 |
| **L** 체크포인트 3분할 | **수정 수용(경계 조정)** | 3분할은 타당하나 팝업을 A에 넣으면 런타임 골격 없이 팝업을 짤 수 없다. **CP1=0~1(스파이크+검증기 신뢰 회복, go/no-go), CP2=2~6(런타임, fixture 전용), CP3=7~9(주입기+통합+실기기)**로 재단한다. 스파이크는 구현과 섞이면 안 되는 중단 게이트다 | §27 |

---

## 5. 현재 구조 (감사 확정 사실)

- `sessions/1주차/1주차_강의안_발표자모드.html` — 58,911,146 B. `<section class="slide">` **75장, 전부 `.deck` 직계**, `data-slide` 75개 **전부 존재·중복 0**. DOM id 중복 0. 비-data `src/href` **0건**. data URI 40개(PNG 39 + woff2 1), base64 약 41.8MB.
- 스크립트 2개: **A**(덱 런타임, 4254–4331) · **B**(발표자 층, 4333–4524). 두 개의 독립 상태 기계이며, B는 `#nextBtn`/`#prevBtn`을 **프로그램적으로 클릭**해 A를 조종하고 `.deck` MutationObserver로 되받는다.
- 발표자 층은 kit·조각·스타터 어디에도 없다. 이 파일은 동결된 `강의덱_배포.html`의 **수제 파생물**이다.
- `verify_deck.py` 실측: 발표본 **FAIL 3**(raw색 74 · gradient · 폰트) vs 배포본 **FAIL 1**. 이름만 `_배포`로 바꾼 사본에서는 raw색 **33건**, gradient **PASS** → **41건 + gradient는 파일명 때문에 생긴 오탐**, 진짜 위반은 발표자 CSS의 raw 색 33건.
- `sessions/1주차/강의덱_발표자노트.html` — `pn-slide` **54개**, 항목 67개(`pn-joke` 💬 41 · `pn-demo` 👀 19 · `pn-hint` 🗣 7). 덱 75장 중 **21장은 원래 멘트 없음**.
- `scripts/verify_notes.py` — 노트↔슬라이드 매핑이 **이미 구현돼 있다**: `pn-no` = `.slide` 문서 순서의 1-기반 인덱스, 제목 전방일치 대조, 페이지번호 제외 규칙을 덱 JS에서 직접 추출. 재사용 대상 심볼: `SlideParser` · `NotesParser` · `PAGENO_GUARD_RE` · `norm_title` · `front_match`.
- `scripts/assemble_deck.py`의 `_write_atomic(path, text)`(94–103줄) — `tempfile.mkstemp` + `os.replace` 구현. **재사용 대상.**
- `scripts/inline_deck.py`는 HTML 주석을 전부 제거한다(292줄) → **주석 마커는 배포 빌드에서 소멸**. 마커는 속성으로만.
- `references/phases/08-검증.md`: "헤드리스 도구는 도입하지 않는다 — 인앱 브라우저에서 손으로 돌린다." **유지한다.**
- `sessions/_contracts/1주차.deck.contract.json`: `frozen: true`, 강의덱/강의덱_배포 각 75장·divider 6.

---

## 6. 폐기할 구조와 보존할 구조

### 폐기
| 폐기 대상 | 위치 | 사유 |
|---|---|---|
| `?presenter=1` 역할 판별 | 4339·4397–4398 | `file://` 쿼리 신뢰 불가 + 덱 2회 로드의 원인 |
| 같은 URL 재열기 | 4400 | 58.9MB 2회 로드 |
| `goTo`의 버튼 반복 클릭 | 4366–4375 | 1→73 점프 = 72회 전이 |
| `.deck` MutationObserver 되받기 | 4511–4514 | 상태 소유권 불명 |
| blackout MutationObserver | 4515–4519 | B1(발표자 창 `B` → 청중 무변화 + 방향키 사망)의 직접 원인 |
| `BroadcastChannel` | 4347·4361 | `file://` 불투명 origin·중복 메시지 |
| `localStorage` 동기화 키(`syncKey`) | 4341·4362·4504 | 동기화 채널 용도 폐기 |
| 무검증 `postMessage` 수신 | 4503 | source·token 검증으로 교체 |
| 하드코딩 `vibecoding-week-1` / 창 이름 `vibecoding-presenter` | 4340·4400 | 덱 간 충돌 |
| 인덱스 기반 메모 키 | 4495 | slideId로 교체 |
| 발표자 CSS raw hex/rgba 33건 | `.presenter-*` | SKILL ④-1 위반 · 테마화 불가 |
| 하드코딩 단축키 안내 `<dl>` | 안내 마크업 | 런타임 상수에서 생성 |
| `unload`에서 팝업 닫기 | (원안) | 새로고침과 종료를 구분 못 함 |

### 보존 (한 글자도 바꾸지 않는다)
`.deck` 내부 전체 · 슬라이드 마크업·클래스·`data-slide`·인라인 style · 슬라이드 CSS와 색 토큰 · 인쇄 시 색 보존 선언(`print-color-adjust:exact`) · `@page{size:1280px 720px;margin:0}` · 발표 크롬의 클래스명과 외형(`.controls`·`.navbar`·`.presentation-menu`·`.keyboard-help`·`#blackout`) · 1주차 기존 산출물 5종.

---

## 7. 목표 아키텍처

```
[청중 창]  전체 덱 1회 로드 · 유일한 상태 소유자 · 유일한 저장소 기록자
├─ .deck > .slide × N              (런타임이 절대 수정하지 않음)
├─ 발표 크롬                        .controls / .presentation-menu / .keyboard-help / #blackout
├─ <style data-presenter-runtime>   presenter-ui.css 인라인
├─ <script type="application/json" data-presenter-notes>   defaultNote
└─ <script data-presenter-runtime>  presenter-runtime.js 인라인
    ├─ DeckState        index·blackout·theme — 단일 진실 공급원
    ├─ KEYMAP           단축키 상수 1개 → 키 처리 + 도움말 UI 동시 생성
    ├─ NoteStore        defaultNote + savedNote + 저장 상태
    ├─ ThemeStore       발표 UI 스코프 전용
    └─ PresenterLink    팝업 생성·문서 작성·직접 렌더 · HELLO 채택 · 하트비트

[발표자 팝업]  about:blank · 덱 미로드 · 상태 미소유
├─ 부모가 write한 DOM: 현재/다음 미리보기 · 컨트롤 · 메모 · 타이머 · 연결 배지
└─ bootstrap <script>  (팝업 자신의 컨텍스트에서 실행)
    ├─ HELLO 재전송 → 부모 채택 대기
    ├─ UI 이벤트 → opener.postMessage(명령)
    └─ PING/PONG 하트비트 → 끊기면 컨트롤 비활성 + 안내
```

**통신은 방향마다 정확히 하나다.**

| 방향 | 경로 | 내용 |
|---|---|---|
| 부모 → 팝업 | **직접 DOM 조작** | 미리보기 렌더 · 번호·제목 · 메모 값 · 저장 상태 · 타이머 표시 · 연결 배지 · 테마 |
| 팝업 → 부모 | **`opener.postMessage`** | HELLO · PONG · 명령(NEXT/PREV/GOTO/BLACKOUT/TIMER/THEME/NOTE_INPUT/NOTE_RESET/PRINT) |

**런타임 주입 노드는 `.deck` 밖에만 존재한다.**

---

## 8. 상태 모델과 공개 API

```
DeckState = {
  index:     0-based, 0 <= index < slides.length
  blackout:  boolean
  theme:     'light' | 'dark'
  presenter: 'closed' | 'open' | 'lost'
}
```

| API | 계약 |
|---|---|
| `goTo(i)` | 클램프 → `.is-active` 토글 → 구독자 통지 → 팝업 렌더 → 위치 저장(sessionStorage) → `history.replaceState` **최대 1회**(try/catch). **버튼 클릭 흉내 금지** |
| `next()` / `prev()` | `goTo(index±1)`. 경계에서 무동작 |
| `first()` / `last()` | `goTo(0)` / `goTo(n-1)` |
| `setBlackout(v)` / `toggleBlackout()` | `#blackout` 토글. **역할과 무관하게 이 경로 하나** |
| `setTheme(t)` | 발표 UI 스코프에만 적용 + localStorage 저장 |
| `subscribe(fn)` | 하단 네비·목록·팝업이 전부 구독자 |
| `getSlideId(i)` / `getTitle(i)` / `snapshot()` | 조회 전용 |

**불변 조건**
1. 슬라이드 전이는 항상 `goTo` 1회를 통한다.
2. 슬라이드 컬렉션은 **`.deck > .slide`**로만 수집하고 로드 시 1회만 캡처한다(`document.querySelectorAll('.slide')` 금지 — 미리보기 복제본과 충돌).
3. 팝업은 상태를 소유하지 않는다. 모든 변경은 명령 메시지 → 부모 API 호출.
4. 저장소에 쓰는 주체는 **부모 창 하나뿐**이다(팝업은 저장하지 않는다).
5. 모달(메뉴·도움말)이 열려 있거나 blackout이 켜져 있을 때의 키 가드는 **이동 키에만** 적용하고, `Esc`·`B`·`?`·`G`는 항상 동작한다. 단 포커스가 `input`/`textarea`/`select`/`contenteditable`이면 **모든 단축키가 무동작**이다(역할 무관).

---

## 9. 발표자 창 생성·연결·종료·복구 정책

### 9.1 생성
1. 사용자가 "발표자 모드 열기"를 클릭한다(**사용자 제스처 필수**).
2. `sessionId = 난수`. 창 이름 `pv-<deckId>-<sessionId>` (**열 때마다 고유** → 다른 탭의 팝업을 가로채지 않는다).
3. `window.open('', windowName, 'popup=yes,width=1440,height=940')`.
4. 반환값이 `null`이거나 `w.document` 접근이 예외면 → **§9.5 팝업 실패 정책**.
5. 부모가 팝업 문서를 작성한다:
   - `<meta charset>`, `<title>`
   - `presenter-ui.css` 텍스트를 `<style>`로
   - **미리보기 렌더용 kit CSS**: 부모의 인라인 `<style>` 블록 중 `@font-face`를 포함한 블록과 슬라이드 스타일 블록을 그대로 복사한다(§9.6)
   - 발표자 UI DOM
   - **bootstrap `<script>`** — `document.createElement('script')` + `textContent` + `appendChild`로 삽입한다(`innerHTML`으로 넣으면 실행되지 않는다). `sessionId`·`deckId`를 상수로 심는다.
6. 부모가 `sessionStorage['pv:<deckId>:sid'] = sessionId`를 최선 노력으로 기록한다.
7. 부모가 첫 렌더를 직접 수행하고 `presenter='open'`.

### 9.2 정상 운용
- 팝업 bootstrap: 채택 전까지 **2초마다 HELLO**(`{t:'pv', v:1, kind:'HELLO', deckId, sessionId}`)를 `opener.postMessage(msg,'*')`로 보낸다.
- 부모가 ACK하면 HELLO를 멈추고 **3초 PING** 하트비트로 전환한다.
- 부모는 상태가 바뀔 때마다 팝업 DOM을 직접 갱신한다(메시지 없음).
- 팝업 UI 조작은 전부 명령 메시지 1건으로 부모에 전달된다.

### 9.3 검증 규칙
부모가 메시지를 수용하는 조건 — **모두** 만족해야 한다.
1. `data.t === 'pv'` 이고 `data.v === 1`
2. `data.deckId === myDeckId`
3. 채택 후 메시지는 `event.source === adoptedWindow` **그리고** `data.sessionId === currentSessionId`
4. HELLO(미채택 상태)는 `event.source !== window`이고 **현재 채택된 팝업이 없을 때만** 수용한다. 이미 채택돼 있으면 `REJECT{reason:'already-paired'}`로 답하고 팝업은 "다른 발표자 창이 이미 연결됨"을 표시한다.
5. `location.protocol`이 `http:`/`https:`이면 **`event.origin === location.origin`도 검사**한다. `file://`에서는 `origin`이 `"null"`일 수 있으므로 이 검사를 생략하고 1~4만 적용한다.

> 팝업은 `opener` 하나에만 메시지를 보낼 수 있으므로, 다른 탭의 부모에게 도달하는 것은 구조적으로 불가능하다. 교차 오연결 방지의 1차 수단은 이 구조이며 토큰은 2차 방어다.

### 9.4 사건별 동작
| 사건 | 동작 |
|---|---|
| **팝업 새로고침(F5)** | about:blank가 재로드돼 내용·bootstrap이 사라진다. 부모 PING이 2회 연속 실패 → 부모가 `presenter='lost'` 표시 후 **팝업 문서를 처음부터 다시 작성**(§9.1-5). 사용자 조작 불필요 |
| **팝업 닫힘** | `presenterWindow.closed` 감지 → `presenter='closed'`, 배지 갱신. **청중 화면은 아무 변화 없음** |
| **청중 창 새로고침** | **팝업을 닫지 않는다.** 새 부모가 로드되면 팝업 bootstrap의 HELLO가 `opener`(= 새 부모)에 도착 → 부모가 채택 → **팝업 문서를 전부 비우고 다시 작성**(죽은 리스너·낡은 DOM 제거) → 즉시 현재 상태 렌더. `window.open` 재호출이 없으므로 팝업 차단과 무관하다. 부모가 sessionStorage에서 `sid`를 읽지 못하면 첫 유효 HELLO를 채택하고 **새 sessionId를 발급해 팝업을 다시 작성**한다 |
| **청중 창 종료** | 팝업 PING이 실패 → bootstrap이 **모든 컨트롤을 비활성화**하고 "청중 창이 닫혔습니다. 이 창을 닫으세요."를 표시한다. 좀비 창이 낡은 정보로 조작되는 것을 막는다 |
| **팝업이 다른 URL로 이동** | 부모의 DOM 접근 실패 → `lost` + 재연결 버튼(제스처) |
| **발표자 창 중복 요청** | 이미 `open`이면 새로 열지 않고 기존 창을 `focus()` |

### 9.5 팝업 실패 정책 (목표 #17)
1. 발표자 모드 **진입을 취소**한다.
2. 청중 슬라이드 모드는 **아무 변화 없이** 유지한다.
3. 실패 사유를 청중 창의 메뉴 안에 표시한다: "발표자 창을 열지 못했습니다. 브라우저의 팝업 차단을 해제한 뒤 다시 시도하세요."
4. **다시 시도** 버튼을 제공한다.
5. **발표자 메모·다음 슬라이드·타이머 UI를 청중 화면에 절대 생성하지 않는다** — 실패 경로에서는 해당 DOM을 만들지 않는다(숨김이 아니라 미생성).

### 9.6 미리보기 복제 (최소 안전 집합)
- `popup.document.importNode(slideEl, true)`로 현재·다음 슬라이드를 복제.
- 복제본 루트에 `data-presenter-preview` 속성 부여(→ `.deck > .slide` 셀렉터와 절대 충돌하지 않음).
- 처리: ① 하위 `[id]`의 `id` 제거 ② 하위 `<script>` 제거 ③ 호스트에 `aria-hidden="true"` ④ CSS `[data-presenter-preview]{pointer-events:none}`.
- **하지 않는 것**: `on*` 속성 순회 · per-element `tabindex` 부여 · iframe/video/audio/canvas 특수 처리. 실측상 `.deck` 안에 존재하지 않으며, 존재 시 주입기가 WARN을 낸다(§15).
- **폰트**: 부모의 `@font-face` 인라인 `<style>` 블록을 팝업에 **복사한다**. 미복사 시 줄바꿈이 달라져 미리보기가 실제 화면과 어긋난다. 단일 서브셋 payload이므로 비용이 이미지보다 훨씬 작다. §29 측정에서 초과하면 그때 재검토한다.
- 마지막 슬라이드에서 "다음"은 "다음 슬라이드가 없습니다"를 표시한다.

---

## 10. 식별자와 저장소 정책

### 10.1 식별자 5종
| 식별자 | 정의 | 위치 | 저장 키 사용 |
|---|---|---|---|
| `deckId` | 사람이 정한 영구 문자열. 1주차는 **`vibecoding-week-1`** | 계약 파일 + `<html data-deck-id>` | ✅ |
| `slideId` | 슬라이드 영구 ID. **기존 `data-slide` 값을 그대로 채택** | 덱 마크업(이미 존재) | ✅ |
| `sessionId` | 발표 세션 1회용 난수. 창 이름 접미 + 페어링 토큰 **겸용** | 메모리 + sessionStorage(최선 노력) | ❌ |
| `buildHash` | 슬라이드 본문 정규화 해시(SHA-256) | `<html data-build-hash>` + 사이드카 | ❌ **금지** |
| `runtimeVersion` | 런타임 SemVer(초기 `1.0.0`) | `<html data-presenter-runtime>` | ❌ |

### 10.2 slideId 전환 규칙
1. 주입기가 `.deck > .slide`의 `data-slide`를 수집한다.
2. **전부 존재 + 중복 0이면 그대로 slideId로 채택하고 마크업을 한 글자도 바꾸지 않는다.** (1주차 실측: 75/75 존재·중복 0 → **속성 추가 없음**)
3. 누락·중복이 있으면 **주입 중단** + 위치·제목 보고. 자동 부여 금지.
4. 사용자가 명시적으로 지시할 때만, `.slide` **시작 태그에 `data-presenter-sid="<결정론적 값>"` 속성 1개 추가**로 제한한다(innerHTML·순서·수·기존 속성 불변).
5. 미래 덱: `_template` shell과 `references/phases/04-조립.md`에 `data-slide` 필수·유일을 명시하고, `verify_deck.py`에 검사를 추가한다.

### 10.3 저장소 정책
| 데이터 | 저장소 | 키 | 실패 시 |
|---|---|---|---|
| 메모(savedNote) | **localStorage** | `pv:<deckId>:note:<slideId>` | **화면에 명시적으로 경고**(목표 #13) |
| 테마 | **localStorage** | `pv:theme` (덱 무관 전역) | 조용히 기본값 |
| 현재 위치 | **sessionStorage** | `pv:<deckId>:pos` | 조용히 퇴화 — 항상 표지에서 시작 |
| 타이머 | **sessionStorage** | `pv:<deckId>:timer` | 조용히 퇴화 — 새로고침 시 초기화 |
| sessionId | **sessionStorage** | `pv:<deckId>:sid` | 조용히 퇴화 — HELLO 첫 수용 경로로 대체(§9.4) |

- **`buildHash`를 저장 키에 넣지 않는다** — 덱을 재빌드해도 강사 메모가 살아남아야 한다.
- sessionStorage는 탭 단위이고 탭을 닫으면 사라지므로 **이전 발표의 타이머·위치가 다음 발표에 남지 않는다**.
- 저장소는 **부모 창만** 기록한다. 팝업은 어떤 저장소에도 쓰지 않는다.
- `history.replaceState`는 최선 노력(try/catch)이며 **위치 복원의 근거로 쓰지 않는다**.

---

## 11. 노트 파싱·매핑·기본값·편집본 정책

### 11.1 파싱·매핑 (기존 자산 재사용)
`scripts/verify_notes.py`의 `SlideParser` · `NotesParser` · `PAGENO_GUARD_RE` · `norm_title` · `front_match`를 **import 해서 재사용한다. 새 파서를 만들지 않는다.**

1. 노트 파싱 → `(pn-no, 제목, [{kind, text}])`. `kind`는 클래스에서 도출: `pn-joke`→`joke` · `pn-demo`→`demo` · `pn-hint`→`hint`.
2. 덱 파싱 → `index → (slideId, 제목)`.
3. `pn-no - 1`을 인덱스로 매핑하고 **제목 전방일치를 재확인**한다.
4. `slideId → [{kind, text}]`로 변환한다.

### 11.2 실패 게이트 (allowlist 없음)
| 종류 | 정의 | 처리 |
|---|---|---|
| **하드 실패** | `pn-no`가 정수 아님 / 슬라이드 범위 밖 / 제목 전방일치 실패 / 같은 slideId에 2건 이상 매핑 | **빌드 중단.** `pn-no`·노트 제목·덱 제목·slideId·후보를 전부 출력. **자동 추정 매핑 금지** |
| **소진 어서션** | 노트 파일의 `pn-slide` 개수 ≠ 매핑 성공 개수 | **빌드 중단.** 노트 파싱이 통째로 실패해 0건이 나오는 사고를 잡는다(1주차 기대값 **54 = 54**) |
| **정상 빈 메모** | 덱 슬라이드에 대응 노트가 없음 | **정상 통과.** 개수와 slideId 목록만 로그로 보고(1주차 기대 **21장**) |

### 11.3 JSON 안전성 (F 수용)
- 삽입 블록: `<script type="application/json" data-presenter-notes>` — **`.deck` 밖, `</body>` 직전**.
- 직렬화: `json.dumps(..., ensure_ascii=False)` 후 결과 문자열에서 세 문자를 **JSON 유니코드 이스케이프(백슬래시 u 0 0 3 c 형태의 6문자 시퀀스)** 로 치환한다.

  | 원문자 | 치환 결과 (백슬래시 1개 + 다음 5문자) |
  |---|---|
  | `<` (U+003C) | 백슬래시 + `u003c` |
  | `>` (U+003E) | 백슬래시 + `u003e` |
  | `&` (U+0026) | 백슬래시 + `u0026` |

  Python 구현 예: 직렬화 결과 문자열에 대해 `.replace("<", "\\u003c")` 형태로 치환한다(치환 문자열의 백슬래시는 소스에서 이스케이프해야 실제 백슬래시 1개가 된다).

  이렇게 하면 노트 본문에 `</script>`나 `<!--`가 들어 있어도 스크립트 블록이 조기 종료되거나 주석으로 오파싱되지 않는다. JSON 파서가 파싱 시 원래 문자로 복원하므로 값은 손상되지 않는다.
- 삽입 직후 **주입기가 그 블록을 다시 파싱해 유효성과 항목 수를 확인**한다.
- **이모지 문자를 저장하지 않는다.** `kind` 코드만 저장하고 라벨(`💬 강사 설명·애드리브` 등)은 런타임 상수가 붙인다 → `verify_deck.py`의 "아이콘 마커 누출 0" 검사와 충돌하지 않는다.
- 런타임은 노트를 **`textContent`로만** 렌더한다. `innerHTML` 사용 금지.
- `verify_deck.py`의 학생 화면 검사(아이콘·힌트 문구) 예외 범위는 **`data-presenter-notes` 블록 하나로 한정**한다.

### 11.4 기본값·편집본
```
defaultNote[slideId]  HTML 내장 · 읽기 전용
savedNote[slideId]    localStorage · 사용자 편집본
표시값 = savedNote가 있으면 savedNote, 없으면 defaultNote
```
- 편집 시 **300ms debounce** 후 부모가 저장. 저장 결과를 매번 상태 줄에 반영: `저장됨 HH:MM:SS` / `저장 안 됨 — 브라우저가 저장을 막고 있습니다`.
- 저장 실패 시 텍스트는 화면에 유지되고, 창을 닫으면 사라진다는 경고를 함께 표시한다.
- **기본 멘트로 되돌리기** 버튼: 확인 1회 후 `savedNote` 삭제 → `defaultNote` 복원.
- 배지: `기본 멘트` / `수정됨`.
- 슬라이드 이동 시 편집 중이던 값을 **즉시 flush**한 뒤 다음 메모를 로드한다.
- 1차 범위에서 **내보내기·가져오기·기기 간 이전은 구현하지 않는다.**

---

## 12. 테마 범위

- 신설 토큰 네임스페이스 **`--pv-*`**. 슬라이드 토큰(`--ink`·`--blue`·`--mint` 등)을 **참조하지 않는다**(이름이 겹치지 않아야 스코프 이탈을 정적으로 검사할 수 있다).
- 테마 속성은 `<html data-pv-theme="light|dark">`.
- **`--pv-*`의 모든 정의·사용은 `.controls` · `.presentation-menu` · `.keyboard-help` · `.presenter-` 접두 셀렉터 안에만 존재한다.** 하나라도 벗어나면 FAIL.
- 전환: 발표자 팝업의 토글 버튼 + `?` 도움말에 표기. 저장 키 `pv:theme`(전역).
- 초깃값: 저장값 없으면 `prefers-color-scheme`. **저장값이 있으면 항상 저장값이 이긴다.**
- 손상된 저장값은 무시하고 초깃값 규칙으로 복귀.
- **슬라이드 본문에는 어떤 테마 속성도 적용되지 않는다.** `#blackout`은 테마와 무관하게 항상 검정.

---

## 13. PDF·인쇄 정책

- 인쇄 제외: `.controls` · `.presentation-menu` · `.keyboard-help` · `#blackout` · `.presenter-console` · `[data-presenter-preview]`.
- **슬라이드 본문은 기존 디자인·색상을 그대로 유지한다.** 기존 `print-color-adjust:exact` 선언(109줄)을 보존해 배경 그래픽·색을 보존한다. "항상 라이트" 같은 강제 변환은 하지 않는다.
- **1장 = 1페이지 보장**: print 블록에 `.slide{ break-after:page; page-break-after:always; break-inside:avoid; }` 추가, 마지막 슬라이드는 `break-after:auto`로 빈 페이지 방지.
- `@page{size:1280px 720px;margin:0}` 유지.
- 팝업의 PDF 버튼은 `PRINT` 명령을 부모로 보내고 **부모가 `window.print()`** 한다. 팝업 자체는 인쇄하지 않는다.
- **발표 UI 테마는 인쇄 결과에 영향을 주지 않는다** — `--pv-*` 사용 노드가 전부 인쇄에서 제외되므로 구조적으로 보장되며 정적 검사로 확인한다.
- 인쇄 중 발표 상태(현재 슬라이드·blackout)는 변경하지 않는다.

---

## 14. 발표본 생성 명령과 create-slides 연계

### 14.1 명령 (단일 진입점)
```bash
python scripts/inject_presenter.py <입력 단일 HTML> \
  --notes <발표자노트.html> \
  --deck-id <deckId> \
  --output <발표본.html> \
  --meta <사이드카.json> \
  [--force]
```

- **`scripts/build_release.py`는 변경하지 않는다.** 일반 조립 경로에 발표자 코드 경로가 **아예 존재하지 않으므로**, "자동 삽입 없음"이 플래그 기본값이 아니라 **구조로** 보장된다(목표 #3·#4).
- 입력은 **이미 완성된 단일 HTML**이다. 조각에서 재생성하지 않으므로 1주차 동결과 충돌하지 않는다(목표 #7).
- 미래 주차 흐름: `build_release.py` → `강의덱_배포.html` → (사용자 명시 요청) → `inject_presenter.py` → `강의덱_발표.html`.

### 14.2 게이트
1. 입력에 `<html data-presenter-runtime>`이 있으면 **즉시 중단**(멱등).
2. `--output` 경로에 파일이 있고 `--force`가 없으면 **중단**.
3. `--output`이 입력과 같은 경로면 **중단**(원본 덮어쓰기 금지).
4. slideId 검사(§10.2), 노트 게이트(§11.2), 불변 검증(§15) 중 하나라도 실패하면 **파일을 쓰지 않는다**.

### 14.3 스킬 연계
- `SKILL.md` ⑤ 게이트 지도에 **10단계(선택·명시 요청 전용)** 1행 추가.
- `references/phases/10-발표자모드.md` 신설 — 명령·게이트·수동 체크리스트.
- **계약 파일에 승인 기록 필드를 추가하지 않는다.** 사용자의 실행 요청 자체가 승인이다.
- `evals`에 "일반 덱 조립 요청에 발표자 런타임이 삽입되지 않는다" 회귀를 추가한다.

### 14.4 산출 경로
| 산출물 | 경로 |
|---|---|
| 강사 전달물(HTML 1개) | `sessions/1주차/강의덱_발표.html` |
| 사이드카(내부 검증용) | `sessions/_verify/1주차/강의덱_발표.meta.json` |

- 동결 폴더에 추가되는 파일은 **전달물 1개뿐**이다(사용자의 "동결 유지 + 별도 발표본 생성" 결정에 의한 승인된 예외). 사이드카는 `sessions/_verify/`로 분리한다.
- `sessions/README.md`에 발표본·사이드카 규약 2줄을 추가한다.
- 기존 `1주차_강의안_발표자모드.html`은 **보존**한다(삭제·이름 변경 금지 — 후속 과제).

---

## 15. 주입기의 멱등성·불변성·atomic write

`scripts/inject_presenter.py` 처리 순서 (입력 파일을 **1회 스트리밍 읽기**):

1. 입력 읽기 → `<html data-presenter-runtime>` 존재 시 중단.
2. `.deck` 범위를 특정하고, 그 안의 `<section class="slide"...>` **시작 태그를 정규식으로 스캔**해 `(순서, 시작태그 원문, innerHTML 범위)`를 수집한다. **HTML 전체를 파서로 재직렬화하지 않는다** — 원문 바이트를 보존하고 삽입만 한다.
3. slideId 검사(§10.2). `.deck` 안의 `<iframe|video|audio|canvas>` 존재 시 **WARN**(중단 아님, §9.6 근거 기록).
4. `before` 지문 산출: 슬라이드 수 · 순서 · slideId 시퀀스 · 슬라이드별 `innerHTML` SHA-256 · 시작 태그 원문 SHA-256 · `<img>` 개수와 `src` SHA-256 · 전체 `buildHash`.
5. 노트 매핑(§11) → 실패 시 중단.
6. 삽입:
   - `<html>`에 `data-presenter-runtime` · `data-deck-id` · `data-build-hash` 속성 추가
   - `</head>` 직전에 `<style data-presenter-runtime>`
   - `</body>` 직전에 `<script type="application/json" data-presenter-notes>` → `<script data-presenter-runtime>`
   - **`.deck` 범위는 문자열 치환 대상에서 원천 제외한다.**
7. `after` 지문 재산출 → 다음을 **전부** 대조:
   - 슬라이드 수·순서·slideId 시퀀스 동일
   - 슬라이드별 `innerHTML` 해시 동일
   - `.slide` 시작 태그 원문 **완전 동일**(id·class·style·data-* 포함). §10.2-4 예외 적용 시에만 `data-presenter-sid` 1개 추가를 허용하고 그 외 차이는 FAIL
   - `<img>` 개수·`src` 해시 동일
   - 주입 노드 4종이 **`.deck` 범위 밖**에만 존재
   - 노트 JSON 블록 재파싱 성공 + 항목 수 일치
8. 전부 통과할 때만 임시 파일에 쓰고 **atomic replace**한다. `scripts/assemble_deck.py`의 `_write_atomic(path, text)`을 **import 해서 재사용**한다.
9. 사이드카 산출(§17).
10. 실패 시 **임시 파일 삭제 + 최종 경로에 아무것도 쓰지 않음**(fail-closed). 종료코드 1.

---

## 16. 검증기 신뢰 회복

**문제(실측)**: `scripts/verify_deck.py:1342`의 `is_bundle = Path(a.deck).stem.endswith('_배포')`가 kit 유래 색·승인 그라디언트 면제를 **파일명**으로 결정한다. 같은 파일이 이름만 달라 raw색 74↔33, gradient FAIL↔PASS로 갈렸다(gradient 선언은 두 파일이 문자 단위로 동일함을 확인).

**교체(내용 기반 단일 판정)** — 다음을 **모두** 만족하면 번들로 본다.
- 외부 `<link rel="stylesheet">`가 0개
- 인라인 `<style>` 안에 kit `deck.css`의 `:root` 토큰 정의가 존재

이 기준이면 `강의덱_배포.html`·발표본은 True, 외부 CSS를 링크하는 미리보기 `강의덱.html`은 False가 되어 현재 의도를 그대로 재현한다. **K 의견(마커 기반)을 채택하지 않는 이유**: 마커를 심으려면 일반 빌드 경로를 고쳐야 해 폭발 반경이 커지고, 동결된 1주차 배포본에는 마커를 심을 수 없어 내용 기반 경로가 어차피 필요하다.

**함께 처리**
- `sessions/_contracts/1주차.deck.contract.json`의 `decks`에 `강의덱_발표` 항목 등재(75장·divider 6·`known_violations`는 배포본과 동일 상속). 1주차 폴더는 건드리지 않는다.
- `data-presenter-notes` 블록을 학생 화면 검사(아이콘·힌트 문구) 대상에서 제외.
- `.slide` 전원 `data-slide` 보유 + 중복 0 검사 추가.
- **회귀**: `강의덱_배포.html` 판정 결과가 변경 전과 **동일**해야 한다.

**착수 시 확인**: `tests/test_deck_pipeline.py`의 `test_clean_bundle_has_no_violations` · `test_each_violation_class_is_detected` · `test_exempt_is_empty`가 파일명 규약에 의존하는지(해당 테스트 함수만 열어 확인).

**삭제한 비현실적 검증**: "정의되지 않은 전역 참조 0"(정규식으로 보장 불가). 대체 3종:
1. JS 구문 검사 — **착수 시 확인**: Node.js 가용 여부. 가능하면 `node --check`, 불가하면 이 항목은 3번으로만 판정.
2. 런타임이 `getElementById`로 찾는 ID 목록 ↔ 런타임이 생성하는 마크업 문자열 정적 대조.
3. fixture 덱을 브라우저로 1회 열어 **콘솔 에러 0** 확인(수동, `08-검증.md` 절차).

---

## 17. 독립 검증과 사이드카 정책

- **사이드카는 감사 기록(보조 자료)이지 검증 정본이 아니다.**
- `scripts/verify_presenter_deck.py`는 **원본 배포본과 발표본을 각각 직접 읽어 지문을 재계산**하고, ① 두 파일 사이의 불변성 ② 재계산값과 사이드카의 일치를 **모두** 판정한다. 사이드카와 재계산값이 다르면 그 자체로 FAIL.
- 스캔 제한의 정확한 의미: **LLM이 대용량 파일을 읽는 횟수는 0회**다. Python 프로세스의 대용량 읽기는 검증 정확성을 위해 필요한 만큼 허용하되, 각 실행에서 파일당 1회 스트리밍으로 끝낸다.
- 출력은 **PASS/FAIL과 수치만**. 슬라이드 원문·base64를 절대 출력하지 않는다.

사이드카 스키마(`강의덱_발표.meta.json`):
```
{ deckId, runtimeVersion, buildHash, generatedFrom,
  slideCount, slideIds[], slideHashes{slideId: sha256},
  imgCount, notes: { entries, mapped, emptySlides[] },
  injectedNodes[], warnings[] }
```

`verify_presenter_deck.py` 검사 항목:
1. 외부 `src`/`href`(비-data) 0건
2. `<html>` 마커 3속성 존재 · `runtimeVersion` 형식 유효
3. `data-presenter-runtime` 스크립트·스타일 블록이 **각각 정확히 1개**(중복 삽입 0)
4. 슬라이드 수·순서·slideId 시퀀스·슬라이드별 해시가 원본과 동일
5. `.slide` 시작 태그 원문 동일
6. 주입 노드가 `.deck` 밖에만 존재
7. 노트 JSON 블록 파싱 성공 · 항목 수 = 사이드카 값 · 모든 노트 키가 실재 slideId
8. `--pv-*` 토큰 완전성(라이트·다크 양쪽 전량 정의) · 스코프 이탈 0
9. print 블록에 발표 UI 제외 규칙 + `break-after:page` 존재
10. 재계산 지문 ↔ 사이드카 일치

---

## 18. 파일별 변경 계획

### 신설
| 파일 | 내용 |
|---|---|
| `kit/runtime/presenter-runtime.js` | DeckState · KEYMAP 상수 · NoteStore · ThemeStore · PresenterLink · 팝업 bootstrap 소스 문자열 |
| `kit/runtime/presenter-ui.css` | `--pv-*` 토큰(라이트/다크) · 발표 UI · 미리보기 · print 규칙 |
| `scripts/inject_presenter.py` | §15 |
| `scripts/verify_presenter_deck.py` | §17 |
| `references/phases/10-발표자모드.md` | 명령·게이트·체크리스트 |
| `sessions/_verify/1주차/강의덱_발표.meta.json` | 사이드카(9단계 산출물) |
| `sessions/1주차/강의덱_발표.html` | **강사 전달물**(9단계 산출물) |

### 수정
| 파일 | 변경 |
|---|---|
| `scripts/verify_deck.py` | §16 4항목 |
| `sessions/_contracts/1주차.deck.contract.json` | `강의덱_발표` 항목 등재 |
| `sessions/README.md` | 발표본·사이드카 경로 규약 2줄 |
| `SKILL.md` | ⑤ 게이트 지도에 10단계 1행 |
| `references/phases/04-조립.md` | `data-slide` 필수·유일 규칙 |
| `sessions/_template/강의덱.초안/shell.html` | `data-slide` 필수 주석 |
| `scripts/verify_skill_setup.py` | kit 신설 자산 2개 등재 |
| `evals/evals.json` · `evals/trigger-eval.json` | 자동 삽입 없음 회귀 |
| `tests/test_deck_pipeline.py` | 주입 멱등성·불변 fixture 테스트 |
| `.agents/agent-memory/create-slides/MEMORY.md` | 최종 1회 |

### 변경 금지
`scripts/build_release.py` · `scripts/inline_deck.py` · `scripts/assemble_deck.py` · `scripts/verify_notes.py` · `kit/styles/*` · **1주차 기존 산출물 5종**(`강의덱.초안/`·`강의덱.html`·`강의덱_배포.html`·`강의덱_발표자노트.html`·`1주차_강의안_발표자모드.html`).

---

## 19. SOLO `/하네스` 실행 규칙

- **메인 1개(단독). 서브에이전트 0 · 워커 0 · 리뷰어 0 · 병렬 편집 0.**
- `/하네스`는 다음 6개 용도로만 쓴다: ① 파일 allowlist ② 단계 진입·종료 게이트 ③ 실패 시 즉시 중단 ④ 슬라이드 콘텐츠 불변 검증 ⑤ 대용량 파일 읽기 제한 ⑥ 최종 산출물 검증.
- **Git**: 단계별 커밋 계획 없음. 자동 커밋 금지. 되돌림은 ① 신설 파일 삭제 ② 수정 파일은 착수 직전 사본을 스크래치패드에 보관 후 복원. 최종 완료 후 **사용자가 요청할 때만** 커밋.
- 각 단계 종료 시 `git status --short`로 allowlist 밖 변경이 없는지 확인한다(출력은 파일 목록만).

---

## 20. 단계별 실행 계획

> 전 구간 공통 **읽기 금지**: `sessions/1주차/1주차_강의안_발표자모드.html` · `sessions/1주차/강의덱_배포.html` · `sessions/1주차/강의덱.html` — LLM이 직접 열지 않는다(Python 스크립트가 프로그램으로만 읽는다). base64 출력 금지.

### 0단계 — 사전 스파이크 + 미확정 사실 확정 (go/no-go)
- **목적**: 아키텍처 전제 검증 및 `착수 시 확인` 항목 해소.
- **선행 조건**: 없음.
- **읽을 파일**: `scripts/build_release.py`(소형·전체) · `tests/fixtures/mini-week/9주차/강의덱.초안/shell.html` · `scripts/verify_deck.py`의 학생 화면 검사 블록(해당 범위만) · `tests/test_deck_pipeline.py`의 번들 테스트 3개.
- **읽지 않을 파일**: 공통 금지 3종.
- **수정할 파일**: 없음(스파이크 산출물은 스크래치패드에 둔다 — 저장소 밖).
- **작업**:
  1. **스파이크**: 스크래치패드에 임시 HTML 1개를 만들어 `file://`에서 ① `window.open('')` 팝업에 부모가 DOM 접근 가능한가 ② 부모가 삽입한 `<script>`가 팝업에서 실행되는가 ③ 팝업 → `opener.postMessage`가 도달하는가 ④ 부모 새로고침 후 팝업의 HELLO가 새 부모에 도달하는가 ⑤ `sessionStorage`·`localStorage` 사용 가능 여부. **Windows Chrome과 Edge에서 각각 1회.**
  2. Node.js 가용 여부 확인.
  3. fixture 덱 구성 파악(슬라이드 수·`data-slide` 보유).
  4. `python scripts/verify_notes.py sessions/1주차/강의덱.html sessions/1주차/강의덱_발표자노트.html` **1회** 실행 → mismatch 목록 확보(하드 실패인지 제목 표기 차이인지 판정).
  5. `verify_deck.py` 학생 화면 검사가 매칭하는 문구·범위 확인.
- **검증 명령**: 위 4번 1회.
- **예상 성공 결과**: 스파이크 ①~⑤ 전부 가능. 5개 확인 항목 해소.
- **실패 시 행동**: 스파이크 ①②③ 중 하나라도 실패하면 **구현 착수 금지**. §31의 예비안 2개를 근거와 함께 보고하고 사용자 결정을 기다린다. ④만 실패하면 재연결을 수동 버튼 전용으로 축소하고 계획을 그 범위로 조정해 진행한다. ⑤가 실패하면 §10.3의 퇴화 경로로 진행한다.
- **다음 단계 진입 조건**: 스파이크 ①②③ 통과 + 확인 항목 5개 해소.

### 1단계 — 검증기 신뢰 회복
- **목적**: 이후 모든 게이트의 종료코드를 신뢰 가능하게 만든다.
- **선행 조건**: 0단계 통과.
- **읽을 파일**: `scripts/verify_deck.py`의 1330–1400 범위 + 계약 탐색 함수 + `tests/test_deck_pipeline.py` · `tests/test_deck_contract.py`.
- **읽지 않을 파일**: 공통 금지 3종.
- **수정할 파일(allowlist)**: `scripts/verify_deck.py`.
- **보존할 파일**: 그 외 전부. verify_deck의 다른 검사 규칙·출력 포맷·종료코드 규약 불변.
- **변경 내용**: §16의 내용 기반 `is_bundle` 교체 · `data-presenter-notes` 예외 · `data-slide` 검사 추가.
- **검증 명령**:
  ```bash
  python -m unittest tests.test_deck_pipeline tests.test_deck_contract
  python scripts/verify_kit.py
  ```
- **예상 성공 결과**: 두 명령 모두 **종료코드 0**. 기존 테스트 전부 통과.
- **실패 시 행동**: 기존 테스트 1건이라도 실패하면 즉시 중단하고 원인 보고. 계약 파일 등재는 8단계에서 하므로 여기서 하지 않는다.
- **다음 단계 진입 조건**: 위 통과. ⚠️ 이 시점에 대용량 덱으로 확인하지 않는다.

### 2단계 — 런타임 골격 + 토큰
- **목적**: DeckState와 `--pv-*` 토큰 체계 확립.
- **선행 조건**: 1단계 통과.
- **읽을 파일**: 없음(설계는 §8·§12로 충분).
- **읽지 않을 파일**: 공통 금지 3종.
- **수정할 파일(allowlist)**: `kit/runtime/presenter-runtime.js`(신설) · `kit/runtime/presenter-ui.css`(신설).
- **보존할 파일**: `kit/styles/*` 전부.
- **변경 내용**: §8 DeckState 공개 API 전량 · KEYMAP 단일 상수(키·라벨·설명) · §12 토큰 라이트/다크 전량.
- **검증 명령**: JS 구문 검사(0단계 결과에 따름) + 임시 정적 점검 스크립트는 만들지 않고 `verify_presenter_deck.py` 완성 전까지 육안 + 토큰 목록 대조.
- **예상 성공 결과**: 구문 오류 0. 라이트·다크 토큰이 1:1로 대응.
- **실패 시 행동**: 토큰 누락·스코프 이탈이 있으면 다음 단계로 넘어가지 않는다.
- **다음 단계 진입 조건**: 위 통과.

### 3단계 — 팝업 생성·프로토콜·실패 정책
- **목적**: §9 전량 구현.
- **선행 조건**: 2단계 통과.
- **읽을 파일**: 0단계 스파이크 결과 메모(스크래치패드).
- **읽지 않을 파일**: 공통 금지 3종.
- **수정할 파일(allowlist)**: `kit/runtime/presenter-runtime.js` · `kit/runtime/presenter-ui.css`.
- **보존할 파일**: DeckState 공개 API 시그니처.
- **변경 내용**: 팝업 생성·문서 작성·bootstrap 삽입 · HELLO/ACK/PING/PONG · 채택·재채택(문서 전면 재작성) · §9.5 실패 정책(**실패 경로에서 발표자 DOM 미생성**) · 연결 배지.
- **검증 명령**: fixture 덱을 조립해 브라우저로 연다.
  ```bash
  python scripts/assemble_deck.py tests/fixtures/mini-week/9주차/강의덱.초안
  ```
  (경로는 0단계 확인 결과에 따름) → 로컬 서버 없이 `file://`로 직접 연다.
- **예상 성공 결과**: 팝업 열기·닫기·팝업 새로고침·부모 새로고침·팝업 차단 **5종 전부 기대대로**, 콘솔 에러 0.
- **실패 시 행동**: 팝업 차단 시 청중 화면에 발표자 정보가 1픽셀이라도 노출되면 **즉시 중단**(목표 #17).
- **다음 단계 진입 조건**: 5종 통과.

### 4단계 — 네비게이션 통합
- **목적**: 하나의 슬라이드 상태 공유(목표 #9) 및 단축키 결함 제거.
- **선행 조건**: 3단계 통과.
- **읽을 파일**: 없음.
- **읽지 않을 파일**: 공통 금지 3종.
- **수정할 파일(allowlist)**: `kit/runtime/presenter-runtime.js`.
- **보존할 파일**: 발표 크롬 클래스명·외형.
- **변경 내용**: 하단 네비·목록·번호 입력·키보드를 전부 `goTo()`로 통합 · `.deck > .slide` 셀렉터 단일화 · 입력 요소·IME(`e.isComposing`) 가드 · blackout 단일 경로(B1 해소) · KEYMAP에서 도움말 자동 생성 · 전체화면 표준+`webkit` 폴백 + `.catch` + 실패 안내 + `webkitfullscreenchange` 청취.
- **검증 명령**: fixture 브라우저 확인.
- **예상 성공 결과**: 경계 이동·목록 점프 1회 전이 · 입력 중 단축키 무발동 · 발표자 창 `B`가 청중을 가리고 이동이 계속 가능 · 도움말 문구 = 실제 키.
- **실패 시 행동**: 입력창 포커스 중 단축키가 1건이라도 발동하면 중단.
- **다음 단계 진입 조건**: 위 통과.

### 5단계 — 메모
- **목적**: §11.4 구현.
- **선행 조건**: 4단계 통과.
- **읽을 파일**: 없음.
- **읽지 않을 파일**: 공통 금지 3종.
- **수정할 파일(allowlist)**: `kit/runtime/presenter-runtime.js` · `kit/runtime/presenter-ui.css`.
- **변경 내용**: defaultNote/savedNote 이원화 · 300ms debounce · 저장 성공·실패 표시 · 되돌리기 · `기본 멘트`/`수정됨` 배지 · 이동 시 flush · **`textContent` 렌더**. 내보내기·가져오기는 **구현하지 않는다**.
- **검증 명령**: fixture 브라우저 + 저장 차단 상태(시크릿 창) 확인.
- **예상 성공 결과**: 저장 성공 시 시각 표시, 차단 시 명시적 경고, 되돌리기 동작.
- **실패 시 행동**: 저장 실패가 화면에 표시되지 않으면 중단(목표 #13).
- **다음 단계 진입 조건**: 위 통과.

### 6단계 — 테마·인쇄
- **목적**: §12·§13 구현.
- **선행 조건**: 5단계 통과.
- **읽을 파일**: 없음.
- **읽지 않을 파일**: 공통 금지 3종.
- **수정할 파일(allowlist)**: `kit/runtime/presenter-ui.css` · `kit/runtime/presenter-runtime.js`.
- **보존할 파일**: **슬라이드 본문 CSS·색상 일절 불변**. 기존 print 색 보존 선언 유지.
- **변경 내용**: `data-pv-theme` 전환·저장·초깃값 · print 제외 규칙 · `break-after:page`.
- **검증 명령**: fixture 브라우저 + 인쇄 미리보기 육안.
- **예상 성공 결과**: 테마 전환 시 발표 UI만 변화, 슬라이드 무변화. 인쇄 미리보기에서 슬라이드 1장=1페이지, 발표 UI 0.
- **실패 시 행동**: `--pv-*` 사용 규칙이 허용 셀렉터 밖에 1건이라도 있으면 중단.
- **다음 단계 진입 조건**: 위 통과.

### 7단계 — 주입기
- **목적**: §15 구현.
- **선행 조건**: 6단계 통과.
- **읽을 파일**: `scripts/assemble_deck.py`의 `_write_atomic`(94–103) · `scripts/verify_notes.py`(재사용 심볼) · `scripts/inline_deck.py`의 주석 제거 부분(292 부근).
- **읽지 않을 파일**: 공통 금지 3종.
- **수정할 파일(allowlist)**: `scripts/inject_presenter.py`(신설) · `tests/test_deck_pipeline.py`.
- **보존할 파일**: `assemble_deck.py` · `verify_notes.py` · `inline_deck.py` · `build_release.py` 전부 불변.
- **변경 내용**: §15 전량 + §11 매핑·게이트 + §14.2 게이트.
- **검증 명령**:
  ```bash
  python -m unittest tests.test_deck_pipeline
  ```
  (fixture 덱 기반 주입 테스트 포함)
- **예상 성공 결과**: 종료코드 0. ① 주입 후 불변 지문 일치 ② 2회 주입 시 두 번째가 중단(종료코드 1) ③ 노트 하드 실패·소진 불일치 재현 시 중단 ④ 원본 파일 미변경 ⑤ 실패 시 산출물 미생성.
- **실패 시 행동**: 5개 중 1개라도 실패하면 중단.
- **다음 단계 진입 조건**: 위 통과.

### 8단계 — 전용 검증기·문서·계약·eval
- **목적**: 게이트와 계약 정합.
- **선행 조건**: 7단계 통과.
- **읽을 파일**: `sessions/_contracts/1주차.deck.contract.json` · `sessions/README.md` · `SKILL.md` · `scripts/verify_skill_setup.py` · `evals/evals.json`.
- **읽지 않을 파일**: 공통 금지 3종.
- **수정할 파일(allowlist)**: `scripts/verify_presenter_deck.py`(신설) · `references/phases/10-발표자모드.md`(신설) · `sessions/_contracts/1주차.deck.contract.json` · `sessions/README.md` · `SKILL.md` · `references/phases/04-조립.md` · `sessions/_template/강의덱.초안/shell.html` · `scripts/verify_skill_setup.py` · `evals/evals.json` · `evals/trigger-eval.json`.
- **변경 내용**: §17 검증기 · §18 수정 목록.
- **검증 명령**:
  ```bash
  python scripts/verify_skill_setup.py
  python scripts/verify_kit.py
  python -m unittest tests.test_deck_pipeline tests.test_deck_contract
  ```
- **예상 성공 결과**: 전부 종료코드 0. eval에서 "일반 조립 요청 → 발표자 런타임 0" 통과.
- **실패 시 행동**: eval에서 일반 조립에 런타임이 삽입되면 즉시 중단(목표 #3).
- **다음 단계 진입 조건**: 전부 통과.

### 9단계 — 1주차 발표본 생성 + 통합·실기기 검증
- **목적**: 강사 전달물 산출 및 최종 게이트.
- **선행 조건**: 8단계 통과.
- **읽을 파일**: 없음(LLM 기준). Python이 `강의덱_배포.html`·`강의덱_발표자노트.html`을 읽는다.
- **읽지 않을 파일**: 공통 금지 3종 — **여기서도 LLM이 열지 않는다.**
- **수정할 파일(allowlist)**: `sessions/1주차/강의덱_발표.html`(신설) · `sessions/_verify/1주차/강의덱_발표.meta.json`(신설) · `.agents/agent-memory/create-slides/MEMORY.md`.
- **보존할 파일**: **1주차 기존 산출물 5종.** 실행 전후 `git status --short`로 변경 0을 확인한다.
- **변경 내용**: 주입 실행 → 검증 → 수동 체크리스트 → 성능 측정 → MEMORY 기록.
- **검증 명령**:
  ```bash
  python scripts/inject_presenter.py sessions/1주차/강의덱_배포.html \
    --notes sessions/1주차/강의덱_발표자노트.html \
    --deck-id vibecoding-week-1 \
    --output sessions/1주차/강의덱_발표.html \
    --meta sessions/_verify/1주차/강의덱_발표.meta.json

  python scripts/verify_presenter_deck.py \
    --source sessions/1주차/강의덱_배포.html \
    --presenter sessions/1주차/강의덱_발표.html \
    --meta sessions/_verify/1주차/강의덱_발표.meta.json

  python scripts/verify_deck.py sessions/1주차/강의덱_발표.html --parts 6
  git status --short
  ```
- **예상 성공 결과**: 주입 종료코드 0(노트 54/54 소진 · 빈 메모 21장 보고) · 전용 검증기 종료코드 0 · `verify_deck` **신규 FAIL 0**(기존 `.s-body 22px 미만` 1건은 배포본과 동일한 기존 결함) · `git status`에 신규 3파일 외 변경 0.
- **실패 시 행동**: 불변 검증 실패·기존 파일 변경 감지·수동 체크리스트 필수 항목 실패 중 하나라도 발생하면 **신규 파일 2개를 삭제**하고 중단·보고.
- **다음 단계 진입 조건**: 없음(종료). §28 수동표와 §29 측정을 마친 뒤 **최종 보고 1회**.

---

## 21. 단계별 allowlist 요약

| 단계 | allowlist |
|---|---|
| 0 | (없음 — 스크래치패드만) |
| 1 | `scripts/verify_deck.py` |
| 2 | `kit/runtime/presenter-runtime.js` · `kit/runtime/presenter-ui.css` |
| 3 | 2단계와 동일 |
| 4 | `kit/runtime/presenter-runtime.js` |
| 5 | 2단계와 동일 |
| 6 | 2단계와 동일 |
| 7 | `scripts/inject_presenter.py` · `tests/test_deck_pipeline.py` |
| 8 | `scripts/verify_presenter_deck.py` · `references/phases/10-발표자모드.md` · `references/phases/04-조립.md` · `sessions/_contracts/1주차.deck.contract.json` · `sessions/README.md` · `SKILL.md` · `sessions/_template/강의덱.초안/shell.html` · `scripts/verify_skill_setup.py` · `evals/evals.json` · `evals/trigger-eval.json` |
| 9 | `sessions/1주차/강의덱_발표.html` · `sessions/_verify/1주차/강의덱_발표.meta.json` · `.agents/agent-memory/create-slides/MEMORY.md` |

---

## 22. 읽기 금지 파일 (전 단계 공통)

- `sessions/1주차/1주차_강의안_발표자모드.html`
- `sessions/1주차/강의덱_배포.html`
- `sessions/1주차/강의덱.html`
- 임의 파일의 base64 payload 구간

→ LLM이 직접 열지 않는다. 필요한 사실은 이 계획서 §5에 이미 기록돼 있고, 그 외에는 Python 스크립트가 **수·ID·해시만** 출력한다.

---

## 23. 검증 명령 모음

```bash
# 단위·계약
python -m unittest tests.test_deck_pipeline tests.test_deck_contract
python scripts/verify_kit.py
python scripts/verify_skill_setup.py

# 덱 정적 검증
python scripts/verify_deck.py <deck>.html --parts 6

# 노트 정합(0단계 1회)
python scripts/verify_notes.py sessions/1주차/강의덱.html sessions/1주차/강의덱_발표자노트.html

# 발표본 산출·검증(9단계)
python scripts/inject_presenter.py <입력> --notes <노트> --deck-id <id> --output <출력> --meta <사이드카>
python scripts/verify_presenter_deck.py --source <입력> --presenter <출력> --meta <사이드카>

# fixture 조립 (경로는 0단계 확인)
python scripts/assemble_deck.py tests/fixtures/mini-week/9주차/강의덱.초안
```

---

## 24. 예상 성공 결과 요약

| 단계 | 성공 신호 |
|---|---|
| 0 | 스파이크 ①②③ 통과 · 확인 항목 5개 해소 |
| 1 | unittest·verify_kit 종료코드 0, 배포본 판정 불변 |
| 2 | 구문 오류 0 · 토큰 라이트/다크 1:1 |
| 3 | 팝업 5종 시나리오 통과 · 콘솔 에러 0 |
| 4 | 상태 공유·단축키 결함 0 |
| 5 | 저장 성공/실패가 화면에 정확히 표시 |
| 6 | 테마 전환 시 슬라이드 무변화 · 1장=1페이지 |
| 7 | unittest 종료코드 0 · 멱등·불변·fail-closed 5종 통과 |
| 8 | 검증·eval 전부 종료코드 0 |
| 9 | 주입·전용검증 종료코드 0 · verify_deck 신규 FAIL 0 · `git status` 신규 3파일 외 변경 0 |

---

## 25. 실패 시 중단 조건 (공통)

1. 슬라이드 불변 검증 실패
2. 1주차 기존 산출물 5종 중 하나라도 변경 감지
3. 주입 멱등성 위반(마커 중복)
4. 노트 하드 실패 또는 소진 어서션 불일치
5. `verify_deck.py` 신규 FAIL 발생
6. 팝업 실패 경로에서 발표자 정보가 청중 화면에 노출
7. 일반 조립 경로에 발표자 코드 삽입 감지
8. allowlist 밖 파일 변경 감지

**중단 시**: 즉시 작업을 멈추고 ① 어떤 게이트가 ② 어떤 수치로 실패했는지 ③ 되돌린 범위를 보고한다. 우회하거나 게이트를 완화하지 않는다.

---

## 26. 컨텍스트·토큰 절약 규칙

- 58.9MB HTML·base64를 **LLM이 읽지 않는다**. 재출력·재독 금지.
- 관련 script/style은 **범위를 지정해 1회만** 추출하고, 같은 범위를 다시 읽지 않는다.
- 구조 검사는 Python이 **수·ID·해시만** 출력한다.
- **전체 diff 출력 금지** — 변경 hunk만 확인.
- 단계마다 장문 진행 보고를 쓰지 않는다. **검증 결과(종료코드·수치) 우선**, 서술 최소.
- 과거 대화 전체 로그를 다시 읽지 않는다. 이 계획서가 앵커다.
- **최종 보고 1회.**

---

## 27. 체크포인트 / 세션 분할 정책

| CP | 포함 단계 | 종료 조건 | 다음 세션에 넘길 것 |
|---|---|---|---|
| **CP1** | 0 ~ 1 | 스파이크 결과 + 검증기 회귀 0 | 스파이크 결과 5줄 + 변경 파일 1개 |
| **CP2** | 2 ~ 6 | fixture 기준 런타임 전 기능 통과 | 신설 2파일 경로 + 미해결 사항 5줄 이내 |
| **CP3** | 7 ~ 9 | 발표본 산출 + 전 게이트 통과 + 수동표 | 최종 보고 1회 |

- 세션이 바뀌어도 **감사와 아키텍처 조사를 반복하지 않는다.** 이 계획서 §5~§17이 정본이다.
- handoff는 **10줄 이내**로 쓴다.

---

## 28. 수동 실기기 검증표

각 항목을 **Windows Chrome / Windows Edge / macOS Chrome** 3열로 기록한다. 전부 `file://` 더블클릭 실행.

| # | 항목 | 합격 기준 |
|---|---|---|
| 1 | 덱 열기 | 표지 표시, 콘솔 에러 0 |
| 2 | 발표자 창 열기 | 별도 **창**으로 열림, 덱 재로드 없음 |
| 3 | 팝업 차단 상태 | 진입 취소 + 안내 + 다시 시도 버튼. **청중 화면에 메모·다음 슬라이드·타이머 노출 0** |
| 4 | 팝업 허용 후 재시도 | 정상 진입 |
| 5 | 좌우 이동 | 두 창의 번호가 항상 동일 |
| 6 | 목록 점프 | 1회 전이, 지연 없음 |
| 7 | 번호 입력 중 `b`·`g`·`?` | 아무 일도 일어나지 않음 |
| 8 | `B` (청중 창) | 청중 검게, 발표자 창 유지 |
| 9 | `B` (발표자 창) | 청중 검게, 이동 계속 가능 |
| 10 | 팝업 새로고침 | 자동 재구성, 조작 불필요 |
| 11 | 팝업 닫기 | 청중 화면 정상, 배지 `연결 끊김` |
| 12 | **청중 창 새로고침** | 팝업이 살아 있고 자동 재연결 + 문서 재작성 |
| 13 | 청중 창 종료 | 팝업 컨트롤 비활성 + 안내 문구 |
| 14 | 같은 파일 2개 창 | 서로 끌고 다니지 않음 |
| 15 | 메모 편집 | `저장됨` 표시, 재실행 후 유지 |
| 16 | 시크릿/저장 차단 | `저장 안 됨` 경고 표시 |
| 17 | 기본 멘트 되돌리기 | 원문 복원 |
| 18 | 기본 멘트 탑재 | 노트 있는 54장에 멘트 표시, 21장은 빈 칸 |
| 19 | 테마 전환 | 발표 UI만 변경, **슬라이드 무변화** |
| 20 | 전체화면 F / ESC | 진입·복귀, 스케일 정상 |
| 21 | HDMI 확장 | 청중=프로젝터, 발표자=노트북 |
| 22 | HDMI 재연결 | 레이아웃 복구 |
| 23 | 배율 100/125/150% | 잘림 없음 |
| 24 | 절전 복귀 | 연결 정상 또는 재연결 성공 |
| 25 | PDF 저장 | 75장=75페이지, 발표 UI 0, 색 보존 |
| 26 | 인터넷 차단 | 전 기능 동작 |
| 27 | 첫·마지막 장 경계 | 버튼 비활성, 오작동 0 |
| 28 | 새 탭에서 다시 열기 | 표지에서 시작, 이전 타이머 없음 |

**macOS Safari**는 같은 표를 별도 1회 수행해 지원 여부를 확정한다(현재 미지원).

---

## 29. 성능 측정 기준

가벼운 팝업 구조이므로 **측정 전에 BLOCKER로 단정하지 않는다.** Windows Chrome 1회 + macOS Chrome 1회 측정.

| 항목 | 방법 | 1차 목표(가설) | 초과 시 대응 |
|---|---|---|---|
| 발표자 창 열기 | 클릭 → 첫 미리보기 렌더까지 `performance.now()` | < 1,000 ms | 첫 렌더를 다음 프레임으로 이연 |
| 슬라이드 이동 반응 | 키 입력 → 청중 전환 | < 150 ms | `goTo` 내 동기 작업 축소 |
| 미리보기 갱신 | 전환 → 다음 슬라이드 렌더 완료 | < 200 ms | 미리보기를 제목+메모 중심으로 축소 |
| 메모리 증가 | 브라우저 작업 관리자, 팝업 전/후 | < +150 MB | 미리보기 이미지를 placeholder로 치환 |
| 폰트 복사 비용 | 팝업 문서 작성 시간 | 위 항목에 포함 | 폰트 미복사로 전환(미리보기 정확도 저하 감수) |
| 75장 연속 이동 | 끝까지 왕복 1회 | 누적 지연·누수 없음 | 미리보기 캐시 상한 |
| 큰 이미지 슬라이드 | 최대 payload 장 진입 | 위 기준 유지 | 해당 장만 이미지 생략 |

---

## 30. 완료 기준

- 강사 전달물이 **HTML 1개**, 외부 참조 0, `file://` 더블클릭 실행 가능
- 슬라이드 수·순서·slideId·`innerHTML` 해시·`.slide` 시작 태그 원문 **불변**
- 런타임 노드가 **`.deck` 밖에만** 존재
- 발표자 창이 **덱을 재로드하지 않음**
- 두 창의 슬라이드 번호 **항상 일치**
- 팝업 실패 시 **청중 화면에 발표자 정보 노출 0**
- 청중 창 새로고침 후 **자동 재연결**, 청중 창 종료 시 팝업 컨트롤 비활성
- 메모가 **slideId**에 고정되고 노트 54장 멘트가 기본값으로 탑재
- 저장 실패가 화면에 표시
- 발표 UI 라이트·다크 일관, **슬라이드 무변화**
- PDF에 발표 UI 0, **75장=75페이지**, 슬라이드 색 보존
- 재적용 시 중단(멱등), 원본 배포본 미변경
- **일반 조립에 발표자 코드 자동 삽입 0**(eval 고정)
- `verify_deck.py` 신규 FAIL 0 · 전용 검증기 종료코드 0
- 콘솔 에러 0
- **Windows Chrome·Edge + macOS Chrome 수동표 통과**
- §29 측정값 기록 완료
- 1주차 기존 산출물 5종 **변경 0**

---

## 31. 남은 위험

| 위험 | 성격 | 대응 |
|---|---|---|
| **`file://` about:blank 팝업 DOM 접근·스크립트 실행 불가** | 아키텍처 전제 (0단계 판정) | 실패 시 예비안 2개 중 **사용자 결정**: ⓐ 발표자 창용 경량 HTML 1개를 같은 폴더에 함께 산출(단일 HTML 원칙 완화) ⓑ 공식 실행 경로를 로컬 HTTP 서버로 변경 |
| `file://` 로컬 저장 차단 | 브라우저 정책 | 메모 휘발을 화면 경고로 인지. **defaultNote는 파일에 있어 유실되지 않는다** |
| sessionStorage 미가용 | 브라우저 정책 | 위치·타이머가 새로고침 시 초기화(§10.3 퇴화). 파괴적이지 않음 |
| 공식 실행 경로를 저장소 자동 검증이 못 덮음 | 구조적 | §28 수동표가 유일한 근거. 릴리스마다 수행 |
| macOS에서 팝업이 탭으로 열림 | 브라우저 설정 | 설정 안내. 코드로 강제 불가 |
| 듀얼 모니터 자동 배치 불가 | 브라우저 제약 | 창을 손으로 옮긴 뒤 F. 팝업 안내 문구 유지 |
| Safari 미확정 | 검증 미완 | §28 수행 전까지 "미지원" 표기 |
| `defaultNote`가 파일 소스·개발자 도구로 읽힘 | 설계상 수용 | 화면·PDF 노출은 없음. 민감 내용은 메모에 쓰지 않는다 |
| 1주차 노트 pn 불일치(계약 등재) | 기존 결함 | 0단계 판정 결과가 하드 실패면 **9단계를 진행하지 않고 사용자에게 보고**한다(노트 파일은 동결이라 고칠 수 없다) |
| 미리보기 폰트 복사 비용 | 성능 | §29 측정 후 미복사로 전환 가능 |

---

## 32. 후속 과제 (범위 밖)

이미지 최적화로 파일 크기 축소(1주차 동결 해제 필요) · 메모 내보내기·가져오기 · 모바일 리모컨 · 슬라이드 본문 다크모드 · Playwright 재검토 · Firefox 지원 · 1주차 `notes_pn_mismatch` 정합 복구 · 기존 `1주차_강의안_발표자모드.html` 처분 결정 · 2주차 이후 덱에 대한 발표본 산출 · 발표 로그 자동 저장.

---

## 부록 A. 착수 시 확인 항목 (0단계에서 일괄 해소)

| # | 확인 대상 | 확인 방법 | 미해소 시 |
|---|---|---|---|
| 1 | `file://` + about:blank 팝업의 DOM 접근·스크립트 실행·`opener.postMessage`·부모 재로드 후 HELLO | 스크래치패드 임시 HTML 스파이크(Chrome·Edge) | 구현 착수 금지 → §31 예비안 |
| 2 | Node.js 가용 여부 | `node --version` | JS 구문 검사를 브라우저 로드로만 판정 |
| 3 | fixture 덱 경로·슬라이드 수·`data-slide` 보유 | `tests/fixtures/mini-week/9주차/강의덱.초안/` 확인 | 필요한 최소 슬라이드만 추가(확장 금지) |
| 4 | 1주차 `verify_notes` mismatch 실체 | 명령 1회 | 하드 실패면 9단계 보류·보고 |
| 5 | `verify_deck.py` 학생 화면 검사의 매칭 문구·범위 | 해당 검사 블록만 열람 | 예외 범위를 좁게 설정 |
| 6 | `tests/test_deck_pipeline.py` 번들 테스트의 파일명 의존 여부 | 테스트 3개 열람 | 1단계에서 함께 수정 |

## 부록 B. 사용자 결정이 필요한 항목

| # | 항목 | 조건 |
|---|---|---|
| 1 | §31 예비안 ⓐ/ⓑ 선택 | **0단계 스파이크 실패 시에만** 발생 |
| 2 | 1주차 노트 하드 실패 시 처리 | 0단계 확인 4의 결과가 하드 실패일 때만 |

그 외 항목은 전부 확정됐다. 위 2건은 조건부이므로 **0단계 착수를 막지 않는다.**
