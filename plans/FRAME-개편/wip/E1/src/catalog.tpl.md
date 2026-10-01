# FRAME 컴포넌트 카탈로그 — 1주차 덱 shell의 클래스 체계

이 문서는 `강의덱.초안/shell.html`(E1 · E2 산출물)이 정의한 클래스·속성·엔진 동작을 정리한다. part 파일을 쓰는 작업자는 이 문서의 예시 마크업을 복사해 문구만 바꾼다. 클래스 이름과 구조는 바꾸지 않는다.

- 예시 마크업은 시험 조립(`tmp/frame/E1/t/강의덱.초안/`의 `part-01.html` · `part-02.html`)에 실제로 들어간 섹션이다. 그 조립은 `assemble_deck.py` PASS, 브라우저 조작 시험 47항목 PASS, 렌더 감사 결함형 6종 0이었다(결과는 「등록과 검증」 절의 표).
- 예시의 문구는 초안(`1주차_초안.md`)과 준비물 사양(`준비물_사양.md`)에서 가져왔다. 새 장을 쓸 때는 초안 문구를 원문 그대로 옮긴다.
- 결정표의 레이아웃 열 `F-*` 12종은 이 문서의 절마다 하나씩 대응한다. `L-*`는 kit 레이아웃이라 이 문서 밖(`kit/layouts/families/*.md`)에 있다.

## 절 목록

| 절 | 내용 |
|---|---|
| part 파일 규약 | part 파일에 들어가는 것과 들어가지 않는 것 |
| 모든 장의 공통 틀 | 루트 클래스 · 표준 헤더 · `.s-team` 라벨 · 등장 연출 · 글자 크기와 박스 규칙 |
| 강조 어휘 7종 | `mk` · `mk-solid` · `em-ink` · `em-line` · `em-num` · `em-tag` · `em-ring` |
| F-cover | 표지 |
| F-divider | 블록 간지 |
| 개념 장 틀과 F-concept-fig | 정의 → 비유 → 대응 + 시각 자료 자리 |
| 개념 위젯 API | `data-w="toggle \| step \| pick"` |
| F-slot | 수업 안의 실습 시간 |
| F-hub | 에이전트 실습 허브 |
| 실습 셸 공통 | `pr` 장의 바탕 · 표식 · 머리줄 |
| F-pr-goal · F-pr-steps · F-pr-check · F-pr-fix | 실습 네 장 |
| F-pr-list · F-pr-screen | 메인 과제 전용 |
| F-return | 슬롯 뒤 복귀 장 |
| 부품 | 터미널 창 · 파일 창 · 화면 모형 · 표 · 단계 · 체크 · 타이머 · 펼침 · 복사 · 동그라미 |
| 이동과 복귀 | `data-go` · `data-return` · `data-return-to` · `data-pr` · `data-vt-key` |
| 등록과 검증 | `layout_families` · 고정 슬라이드 마커 · 명령 · 시험 결과 |
| 장 작성 순서와 오류 | 점검 순서와 자주 나는 오류 |
| 알려진 한계 | 미확인과 다른 담당이 정할 것 |

---

## part 파일 규약

- part 파일(`part-01.html` …)에는 `<section class="slide …" data-slide="…">` 블록만 둔다. `<html>` · `<head>` · `<body>` · `<style>` · `<script>`는 넣지 않는다. 스타일과 동작은 전부 shell에 있다.
- 섹션 여는 태그는 `<section class="slide …`로 시작한다. 조립기가 이 문자열로 장 수를 센다. `class`를 다른 속성 뒤로 보내지 않는다.
- `data-slide` 값은 결정표의 ID 그대로다(예: `P1-2`, `M3-4`, `SLOT-A`). 덱 안에서 유일하고, 한 번 정하면 바꾸지 않는다. 이동 링크와 발표자 노트가 이 값에 붙는다.
- 한 섹션이 한 장이다. `<section>` 안에 `<section>`을 넣지 않는다.
- 섹션 앞에 `<!-- ===== ID · 레이아웃 ===== -->` 한 줄 주석을 둘 수 있다. 주석 안에도 💬 👀 🗣 기호를 쓰지 않는다.
- 조립기가 shell의 파트 마커 자리에 part 파일을 파일명 순으로 끼운다(`order.txt`가 있으면 그 순서). shell에는 고정 슬라이드가 없어서 표지(`COVER`)도 part에서 온다.
- 발표자 노트는 덱에 넣지 않는다. 강사 멘트(💬) · 시연 큐(👀)는 `강의덱_발표자노트.html`(E9)에만 간다. 화면에는 💬 👀 🗣 기호도, 「강사 멘트」 같은 문구도 없다.
- 🗣(막힐 때만 펼치는 힌트)는 화면에 접힌 상태로 둔다. `<details class="reveal">`을 쓴다(F-pr-fix 절).
- 초안의 제목과 본문 문구는 원문 그대로 옮긴다. 문구를 줄이거나 나누려면 초안을 먼저 고친다.
- 색은 토큰(`var(--blue)` 등)만 쓴다. raw hex · `rgba()` · 그라디언트 · 색 이름 키워드(`white` 등)는 넣지 않는다. 실습 주홍은 `.slide.pr` 안에서 `var(--pr-deep)` · `var(--pr-fill)` · `var(--pr-soft)` · `var(--pr-line)`으로 쓴다.
- 인라인 `style` 속성은 `--i`(등장 순서) · `--mkd`(형광펜 시작 시각) · `--lc`(실습 왼쪽 칸 폭) · `--dx` `--dy`(표지 모서리) 같은 값 전달과, SVG 안의 토큰 색(`style="fill:var(--mint)"`)에만 쓴다.

---

## 모든 장의 공통 틀

### 루트 클래스

| 결정표 레이아웃 | 쓰는 장 | 루트 `class` | 바탕 | 표준 헤더 |
|---|---|---|---|---|
| F-cover | {{USE:F-cover}} | `slide cover f-cover` | `--paper` | 없음 |
| F-divider | {{USE:F-divider}} | `slide part-divider f-divider` | `--white` | 없음 |
| F-concept-fig · 개념 장 틀 | {{USE:F-concept-fig}} 외 개념 장 | `slide cx-slide f-concept` | `--white` | 있음 |
| F-slot | {{USE:F-slot}} | `slide f-slot` + `data-return-to` | `--white` | 있음 |
| F-hub | {{USE:F-hub}} | `slide f-hub` | `--white` | 있음 |
| F-pr-goal | {{USE:F-pr-goal}} | `slide pr f-goal` | 순백 | 있음 |
| F-pr-steps | {{USE:F-pr-steps}} | `slide pr f-steps` | 순백 | 있음 |
| F-pr-check | {{USE:F-pr-check}} | `slide pr f-check` | 순백 | 있음 |
| F-pr-fix | {{USE:F-pr-fix}} | `slide pr f-fix` | 순백 | 있음 |
| F-pr-list | {{USE:F-pr-list}} | `slide pr f-list` | 순백 | 있음 |
| F-pr-screen | {{USE:F-pr-screen}} | `slide pr f-screen` | 순백 | 있음 |
| F-return | {{USE:F-return}} | `slide pr f-return` | 순백 | 있음 |
| `L-*`(kit) | 그 밖의 장 | kit 카탈로그의 루트 클래스 | `--white` | 있음 |

- `pr`가 실습 바탕(순백) · 왼쪽 주홍 세로 띠 · 주홍 강조색을 켠다. 메인 과제 장(`M*`)도 `pr`다.
- `f-*` 클래스는 구도 이름이다. 같은 이름의 레이아웃끼리 연속하지 않게 하고, 「등록과 검증」 절의 `layout_families`에 등재한다.
- `cover`는 kit의 고정 표지 표식이라 표지 검사와 감사가 그대로 작동한다. `part-divider`는 kit의 파트 전환 표식이라 블록 간지를 파트로 세게 한다. 두 클래스가 kit에서 끌어오는 모양은 `f-cover` · `f-divider` 규칙이 덮는다.

### 표준 헤더

표지와 블록 간지를 뺀 모든 장의 첫 자식이다. 로고는 테마 토큰 색을 따른다.

```html
<header class="s-head">
  <svg class="s-logo" viewBox="0 0 48 48" aria-hidden="true"><path d="M8 18 V8 H18 M30 8 H40 V18 M40 30 V40 H30 M18 40 H8 V30" fill="none" style="stroke:var(--blue)" stroke-width="5"/><rect x="19" y="19" width="10" height="10" style="fill:var(--mint)"/></svg><span class="s-brand">FRAME</span>
  <span class="s-line"></span><div class="s-team">블록 2<br>컨텍스트</div>
</header>
```

`.s-team`(오른쪽 위 라벨)은 장 종류마다 정해 둔 글자를 쓴다. PART n/N 도트는 이 덱에서 자동으로 넣지 않는다.

| 장 종류(결정표) | `.s-team` |
|---|---|
| 개념 · 체험 · 운영 · 마무리 | `블록 N` + `<br>` + 주제 이름(6자 이내, 선택) |
| 메인 | `메인 과제` |
| 실습 · 허브 | `에이전트 실습` |
| 슬롯(블록 열이 2 · 3) | `블록 N<br>에이전트 실습` |

### 제목

- 제목은 `<h2 class="s-title">`이다. 발표 메뉴의 목록 이름이 여기서 나온다. 표지는 `<h1>`이다.
- 38px 한 줄에 한글 36자까지 들어간다. 34자 이내로 쓰면 줄이 넘어가지 않는다.
- 개념 · 허브 · 슬롯 장은 제목 위에 `<p class="s-eyebrow">`를 둔다. 실습 장은 머리줄(`.pr-bar`)이 그 자리를 채우므로 eyebrow가 없다.

### 등장 연출

장이 켜질 때 요소가 차례로 나타난다. 마크업에 적는 것은 순서뿐이다.

| 표식 | 동작 | 시간 |
|---|---|---|
| `class="rv"` + `style="--i:N"` | 12px 떠오르며 나타남. N이 클수록 늦다(간격 60ms, 600ms에서 멈춤) | 250ms |
| `.mk` · `.mk-solid`의 `style="--mkd:.45s"` | 형광펜이 왼쪽에서 오른쪽으로 칠해짐. 시작 시각(기본 .3s, 최대 .45s) | 400ms |
| SVG `.a-grow` + `--i` | 막대가 아래에서 자람 | 500ms |
| SVG `.a-fillx` + `--i` | 막대가 왼쪽에서 채워짐 | 500ms |
| SVG `.a-fade` | 0.55초에 나타남(막대 숫자 · 기준선 라벨) | 250ms |
| SVG `.a-pop` + `--i` | 작게 시작해 커짐 | 300ms |
| SVG `.a-draw` + `pathLength="100"` | 선이 그려짐 | 500ms |
| `data-count` | 숫자가 0에서 올라감. 마크업의 글자가 최종 값이다 | 500ms |

- `--i`는 읽는 순서대로(위에서 아래, 왼쪽에서 오른쪽) 0부터 붙인다. 머리줄 · 제목은 `--i:0`이다.
- 한 장의 연출은 850ms 안에서 끝난다(시험 실측 최대 850ms, 한 동작 최대 600ms). 무한 반복 연출은 없다.
- 애니메이션은 시작 상태(`from`)만 정의했다. 끝난 뒤의 모습이 마크업에 적힌 상태다. `?audit` 주소 · `<html class="no-anim">` · `prefers-reduced-motion` · 인쇄에서는 연출 없이 그 상태가 바로 보인다.
- 방향키 이동은 연출을 기다리지 않는다(시험 실측 20ms).

### 글자 크기 규칙

렌더 감사(`audit_typography.js`)는 글자의 길이와 위치로 역할을 판정한다. 클래스 이름은 보지 않는다.

| 글자 덩어리(요소 하나의 직접 글자) | 하한 |
|---|---|
| 한국어 서술 25자 이상 | 22px |
| 24자 이하 | 20px 이상이면 설명문, 그 미만이면 라벨(14px 이상) |
| 표 셀 | 17px |
| `pre` · `code` · `.terminal-copy` · `.terminal-bar` | 적용 안 함 |
| 32px 이상 | 자간 `-.02em` 이하(이 덱 CSS가 큰 글자 클래스에 이미 줬다) |

- 출처와 캡션은 14px다. 요소 하나에 24자를 넘기지 않는다. 길면 `<span>`으로 나눈다(`.cx-src` 예시 참고). 25자 이상을 14px로 두면 하한 위반으로 잡힌다.
- SVG 글자는 viewBox 폭이 그려지는 폭과 같아야 CSS의 px가 실제 px가 된다. 시험 예시는 638px 폭 패널 안에 `viewBox="0 0 594 …"`(배율 1.0)로 그렸다.
- 본문 22px · 박스 안 설명 20px · 제목 26px 위계는 shell의 「기본 경화 5종」이 이미 집행한다. 새 큰 글자 클래스를 만들지 않는다.

### 박스 예산

감사는 배경색 또는 위·왼쪽 테두리가 있고 24×24px 이상인 요소를 박스로 센다. 의사 요소(`::before` · `::after`) · 아래·오른쪽 테두리 · `outline` · SVG 도형은 세지 않는다.

| 부품 | 박스 수 |
|---|---|
| 터미널 창 · 파일 창 · 화면 모형(`.win`) | 1 |
| 개념 그림 패널 `.cx-fig` | 1(`.bare`는 0) |
| 주홍·아쿠아 알약 버튼 `.back` · `.wg-btn` | 1 |
| 텍스트 버튼 `.wg-link` · 목록 · 표 · 세로선 묶음 `.rule` · 강조 7종 | 0 |
| 허브의 카드 · 슬롯의 미니 카드 묶음 `.slot-mini` | 0 · 1 |

결정표 예산은 개념 장 「시각 자료 1 + 박스 ≤ 1」, 실습 장 「박스 ≤ 2」다. 개념 장에서 그림 패널(1)과 알약 버튼(1)을 같이 쓰면 2가 되므로, 패널을 `.bare`로 두거나 버튼을 `.wg-link`로 바꾼다.

---

## 강조 어휘 7종

한 장에 강조 2~4곳, 형태는 최대 2종이다. 한 구절은 12자 이내로 한 줄 안에 넣는다(`mk` · `mk-solid` · `em-line` · `em-tag`는 줄바꿈되지 않는다).

| 클래스 | 쓰는 곳 | 마크업 | 개념 장 | 실습 장 |
|---|---|---|---|---|
| `mk` | 문장 속 핵심 구절 | `<span class="mk" style="--mkd:.45s">앞부분과 끝부분</span>` | 아쿠아 면(글자 아래 절반) | 주홍 면 |
| `mk-solid` | 용어 첫 등장. 장당 1곳 | `<span class="mk-solid">중간 유실</span>` | 아쿠아 면 + 진한 글자 | 주홍 면 + 잉크 |
| `em-ink` | 대비쌍의 한쪽 · 짧은 키워드 | `<span class="em-ink">할 일 표</span>` | 페트롤 글자 800 | 주홍 진한 글자 800 |
| `em-line` | 조건 · 주의 · 바뀌는 지점 | `<span class="em-line">계획</span>` | 페트롤 4px 밑줄 | 주홍 진한 4px 밑줄 |
| `em-num` | 숫자 하나가 요점 | `<span class="em-num">31줄</span>` | 페트롤 · mono · 제목 안에서 1.2배, 본문 1.6배 | 주홍 진한 |
| `em-tag` | 파일 · 버튼 · 메뉴 이름 | `<span class="em-tag">할일표.md</span>` | 연한 페트롤 면 + mono | 옅은 주홍 면 + mono |
| `em-ring` | 표 · 화면 · 터미널 안의 한 칸 | 아래 | 페트롤 선 | 주홍 진한 선(터미널 위는 아쿠아) |

- 아쿠아는 흰 바탕 위 글자색으로 쓰지 않는다. 면으로만 쓴다.
- 문장 전체를 강조하지 않는다. 구절 하나에 한 형태를 건다.
- `mk`의 `--mkd`는 같은 장에서 구절마다 다르게(.25s · .45s) 줘서 차례로 칠해지게 한다.

동그라미(`em-ring`)는 글자 둘레와 SVG 안 두 경우가 있다.

```html
<!-- 글자 둘레: 한 줄짜리 짧은 글자에 .ring-host. 엔진이 장이 켜질 때 손으로 그린 듯한 둥근 선을 만든다 -->
<span class="ring-host">index.html</span>

<!-- SVG 안: 직접 그린 path에 클래스를 단다(pathLength="100"이면 그려지는 연출이 나온다) -->
<path class="em-ring a-draw" pathLength="100" d="…"/>
```

- `.ring-host`는 `display:inline-block`이고 글자가 여러 줄로 꺾이면 둥근 선이 글자 덩어리 전체를 감싼다. 한 줄 안에서만 쓴다.
- 접혀 있던 칸(`data-show`로 숨었다 나타나는 칸)의 동그라미는 그 칸이 보이는 순간 엔진이 다시 그린다.

---

## F-cover

쓰는 장: {{USE:F-cover}}. 네 모서리가 안쪽으로 모이며 나타나고(600ms) 아쿠아 사각형이 커진다. 워드마크는 브랜드 자산(`brand/frame-wordmark.svg`)을 토큰 색(`--blue`)으로 옮긴 인라인 SVG다.

- 구조: 모서리 SVG `.cv-frame`(네 `path.corner` + `rect.core`) · `<h1 class="cv-h1">` 안의 워드마크 SVG `.cv-word` · 부제 `<p class="cv-sub">`. 부제 아래 한 줄이 더 필요하면 `<p class="cv-line">`을 쓴다(선택).
- 헤더 · 쪽 번호가 없다(`cover` 클래스가 쪽 번호 주입을 건너뛴다).
- 워드마크 SVG의 `<defs><clipPath id="frame-band">`는 덱에서 한 번만 쓴다.
- 제목 글자 「FRAME」은 h1 안의 `<span class="sr-only">`에 있다(발표 메뉴 목록 이름 · 제목 생존 검사가 읽는다). SVG에는 `aria-label="FRAME"`이 있다. 「워크숍」 글자는 덱 어디에도 쓰지 않는다.

{{EX:COVER}}

---

## F-divider

쓰는 장: {{USE:F-divider}}. 블록 번호 · 제목 · 4블록 진행 막대. 지나간 블록은 페트롤, 현재 블록은 아쿠아, 남은 블록은 회색이다. 막대가 왼쪽에서 차례로 채워진다.

- 루트 클래스에 `part-divider`를 함께 단다. 검증 스크립트가 블록 간지를 파트로 센다(「등록과 검증」 절).
- 구조: 모서리 장식 `svg.dv-corners` · `.dv-wrap` 안에 `.dv-no`(「블록 2 / 4」) · `h2.dv-title` · 막대 `svg.dv-bar` · 이름 줄 `ol.dv-steps`.
- 막대 SVG는 `viewBox="0 0 928 20"`에 사각형 넷(`x` = 0 · 238 · 476 · 714, 폭 214). 클래스는 `seg done`(지나감) · `seg cur`(현재) · `seg`(남음). 지나간 것과 현재에 `a-fillx`와 `--i`를 붙인다.
- `ol.dv-steps`의 `li`에 현재 블록만 `class="cur"`를 준다.
- 제목은 64px라 한 줄 11자 안팎까지가 안전하다.

{{EX:B2-0}}

---

## 개념 장 틀과 F-concept-fig

쓰는 장: {{USE:F-concept-fig}}. 개념 장은 정의 → 비유 → 대응을 **박스 없이** 쓴다. 세 덩어리는 왼쪽 세로선(`.rule`)으로 묶고, 글자 크기로 위계를 준다. 오른쪽(또는 아래)은 시각 자료 자리다.

- 구조: `.cx-wrap`(세로 flex) 안에 `.cx-top`(eyebrow + 제목) · `.cx-main`(왼쪽 `.cx-text`, 오른쪽 `figure.cx-fig`) · `.cx-src`(출처, 맨 아래).
- `.rule.def`(정의, 23px 600 · 페트롤 선) · `.rule.ana`(비유, 22px · 아쿠아 선) · `.rule.do`(대응, 22px · 회색 선). 각 덩어리 첫 줄은 `<span class="lab">정의</span>`다. 라벨은 19px 800이고 글자는 초안의 **정의** · **비유** · **대응** 표기와 같다.
- 정의에는 강조를 1~2곳(`mk`) 건다. 제목의 용어는 `mk-solid`(장당 1곳)다.
- `.cx-fig`는 면이 있는 그림 패널(박스 1)이다. 박스 예산이 0인 장은 `class="cx-fig bare"`로 면을 뺀다. 그림은 패널 폭 안에 `width:100%`로 들어간다(패널 안쪽 폭 586px).
- 왼쪽 열 폭은 기본 470px다. 그림이 넓어야 하면 `<div class="cx-main" style="grid-template-columns:400px 1fr">`처럼 바꾼다(C-08 예시).
- 용량: 세 덩어리를 합쳐 8줄 이내(정의 3줄 · 비유 3줄 · 대응 2줄 기준). 그보다 길면 바닥선(666px)을 넘는다.
- `.cx-src`는 14px 출처 줄이다. `<span>` 하나에 24자 이내로 쓰고, 여러 개를 이어 쓰면 사이에 「·」가 자동으로 붙는다.
- kit의 `L-*` 레이아웃을 쓰는 개념 장도 정의 · 비유 · 대응은 `.rule` 세 덩어리로 쓴다. 박스 카드로 바꾸지 않는다.

조작 위젯(`data-w`)은 `figure.cx-fig` 안에 둔다. 아래 예시 4개가 위젯 종류별 완성본이다.

**C-11(F-concept-fig) · `pick`** — 막대를 눌러 위치를 고른다. 처음 상태는 「열 번째」다.

{{EX:C-11}}

**C-06 · `toggle`** — 단추로 질문에 「맞죠?」를 붙였다 뺀다. 조작 줄이 그림 위에 있어서 답 길이가 달라져도 단추 자리가 그대로다.

{{EX:C-06}}

**C-12 · `step`** — 서류를 한 장씩 더한다. 처음 상태는 3장이다.

{{EX:C-12}}

**C-08 · `toggle`(전후 강조) + 터미널 + 동그라미** — 터미널 한 창 안에 전과 후를 함께 두고, 단추가 강조할 쪽을 바꾼다. 처음 상태는 「후」이고 그 상태만으로 두 요청문이 모두 읽힌다.

{{EX:C-08}}

---

## 개념 위젯 API

조작하는 SVG · HTML 시각 자료는 세 종류(`toggle` · `step` · `pick`)와 공통 속성으로 만든다. part 파일에 스크립트를 넣을 수 없으므로, 엔진이 읽는 속성만으로 상태를 바꾼다.

### 공통 규칙

| 자리 | 속성 | 뜻 |
|---|---|---|
| 루트(보통 `figure.cx-fig`) | `data-w="toggle"` · `"step"` · `"pick"` | 위젯 종류 |
| 루트 | `data-state="값"` | 처음 상태. 없으면 toggle·step은 `0`, pick은 `.on`이 붙은 항목 |
| 루트(step) | `data-max="N"` | 최댓값. 이때 `data-next` 단추가 꺼진다 |
| 조작 요소 | `data-toggle` | 상태를 `0` ↔ `1`로 바꾼다 |
| 조작 요소 | `data-set="값"` | 상태를 그 값으로 |
| 조작 요소 | `data-pick="값"` | `data-set`과 같고, 눌린 항목에 `.on`이 붙는다 |
| 조작 요소(step) | `data-next` · `data-prev` · `data-reset` | 1 더하기 · 1 빼기 · 처음 값으로 |
| 조작 요소 | `data-labels="꺼진 글\|켜진 글"` | toggle 단추의 글자를 상태에 따라 바꾼다. 글자는 `.t` 자식이 있으면 거기에 들어간다 |
| 보기 요소 | `data-show="값 값"` | 그 상태일 때만 보인다(나머지는 `display:none`) |
| 보기 요소 | `data-hl="값 값"` | 그 상태일 때 `.is-on` 클래스가 붙는다 |
| 보기 요소(step) | `data-from="n"` | 상태가 n 이상이면 `.is-on`(`.w-in`과 함께 쓰면 나타남) |

- **처음 상태를 마크업에 적는다.** 처음 상태에서 보여야 하는 `data-show` 요소와 `data-from` · `data-hl` 요소에는 `class="… is-on"`을 직접 쓴다. 엔진이 켜지기 전에도, PDF와 배포본에서도 같은 화면이 나오게 한다.
- 조작 줄(단추)은 그림 **위**에 둔다(`<div class="wg-row top">`). 상태가 바뀌어 그림 높이가 달라져도 단추가 움직이지 않는다.
- 표시용 클래스: `.w-in`(`.is-on`이면 나타남, 아니면 투명) · `.w-dim`(`.is-on`이면 30%로 흐려짐) · `.v-bar.is-on` · `.v-node.is-on`(색이 바뀜) · `[data-pick].on > .v-bar`(고른 막대 색). `data-from`을 쓴 요소는 `.w-in` 없이도 `.is-on`일 때만 보인다.
- 키보드: `<button>`은 Enter · Space로 눌린다. SVG 그룹은 `tabindex="0" role="button" aria-label="…"`를 주면 엔진이 Enter · Space를 받는다. 이 키는 슬라이드를 넘기지 않는다. SVG 그룹 안에는 `<rect class="hit">`(투명 조작 영역)을 두면 포커스 테두리가 그 영역에 그려진다.
- 위젯 안에 다른 위젯을 넣지 않는다. 엔진은 가장 가까운 `data-w` 조상만 그 요소의 위젯으로 본다.
- 상태가 바뀌면 루트에서 `frame:widget` 이벤트가 나온다(`detail: {w, state, id}`). 지금은 듣는 쪽이 없다.
- 상태는 페이지를 다시 열 때까지 남는다. 장을 떠났다 돌아와도 그대로다.
- 조작 전 초기 상태에서 정보가 읽혀야 한다. 「눌러야 보이는」 구조로 중요한 정보를 숨기지 않는다. 숨기는 것은 강사가 공개하려는 칸(F-pr-fix의 `details.reveal`)뿐이다.

### SVG 시각 자료 어휘

`svg` 안에서 쓰는 클래스다. 이것만으로 시험 예시의 막대 · 서류 · 문서 띠를 그렸다.

| 클래스 | 용도 |
|---|---|
| `.v-ax` `.v-val` `.v-txt` `.v-txt-lg` `.v-note` `.v-mono` | 글자. 17 · 26 · 20 · 24 · 17 · 18px. `fill`이 토큰이다 |
| `.v-axis` · `.v-base` | 축 선(실선) · 기준선(점선) |
| `.v-edge` · `.v-edge.hi` | 연결선 · 강조 연결선 |
| `.v-bar` · `.v-bar.hi` · `.v-bar.warn` | 막대(비강조 · 강조 페트롤 · 주의 호박) |
| `.v-node` · `.v-node.hi` · `.v-node.is-on` | 칸(흰 바탕 회색 선 · 연한 페트롤 · 켜짐 아쿠아) |
| `.hit` | 투명 조작 영역 |
| `.a-grow` `.a-fillx` `.a-fade` `.a-pop` `.a-draw` | 등장 연출(「모든 장의 공통 틀」 절) |

- 막대 그래프는 세로축 0부터, 데이터는 초안이 정한 값만 쓴다. 보간하거나 만든 수치를 넣지 않는다. 예시 값이면 그림 안에 「예시 값」이라고 쓴다.
- 새 색이 필요하면 `style="fill:var(--토큰)"`을 쓴다. raw hex는 쓰지 않는다.

### 숫자 올라가기

`<span class="em-num" data-count>26%</span>`처럼 `data-count`를 달면 장이 켜질 때 0에서 글자 안의 숫자까지 500ms 동안 올라간다. 끝나면 마크업의 글자로 돌아온다. 요소는 글자만 든 잎이어야 한다.

---

## F-slot

쓰는 장: {{USE:F-slot}}. 수업 흐름 안의 실습 시간 안내 장이다. 미니 카드 넷(허브 축소 모형)을 누르면 허브로 넘어간다. 제목 · 시간 · 이번 시간에 할 실습 · 복귀 안내가 들어간다.

- 루트에 `data-return-to="R-A"`를 단다. 값은 복귀 장의 ID다. 허브의 「수업으로 돌아가기」가 이 값으로 간다. 속성이 없으면 DOM의 다음 장으로 간다(시험에서 SLOT-B로 확인).
- 구조: `.slot-wrap` → `.slot-top`(eyebrow · 제목 · `.slot-lead`) · `.slot-main`(왼쪽 `.slot-text`의 `.rule` 덩어리 셋 · 오른쪽 `button.slot-mini`).
- `button.slot-mini`: `data-go="HUB"` `data-vt-key="hub"`. 안에 `span.mini-card`가 넷이고 각각 `data-pr="P1"`…`"P4"`(허브 카드와 같은 값), `.mini-no`(번호)와 `.mini-name`(실습 이름)을 가진다. 실습을 시작한 카드에는 엔진이 `.is-done`을 붙이고 이름 옆에 ✓가 나온다.
- 허브로 들어갈 때 허브의 `.hub-grid`(`data-vt-key="hub"`)로 이어지는 전환이 0.45초 동안 나온다.
- 용량: `.rule` 덩어리 셋, 각 1~2줄.

{{EX:SLOT-A}}

---

## F-hub

쓰는 장: {{USE:F-hub}}. 카드 넷(번호 · 이름 · 결과물 · 준비물 · 시간 · 전후 픽토그램). 카드를 누르면 그 실습의 ① 목표 장으로 이동한다. 실습 개념 이름은 카드에 쓰지 않는다(D31).

- 구조: `.hub-wrap` → `.hub-top`(eyebrow · 제목 · `.hub-lead`) · `.hub-grid`(2×2, `data-vt-key="hub"`) · `.hub-foot`(왼쪽 안내 한 줄, 오른쪽 `button.back[data-return]`).
- 카드: `button.hub-card`에 `data-go="P1-1"`(그 실습 ①의 ID) · `data-vt-key="p1"` · `data-pr="P1"`. 안에 `.hub-no` · `.hub-body`(`.hub-name` · `.hub-meta` 둘 · `.hub-done` ✓) · `svg.hub-pic`(전 → 후 픽토그램 132×64).
- `.hub-meta`는 20px이고 한 줄 24자 이내다. 파일 이름은 `em-tag`로 감싼다.
- 카드를 누른 실습에는 `.is-done`이 붙어 번호가 초록으로 바뀌고 「✓ 진행함」이 나온다.
- `data-return` 단추(수업으로 돌아가기)는 슬롯을 거쳐 왔으면 그 슬롯의 복귀 장으로, 슬롯을 거치지 않았으면 직전에 본 본편 장으로 간다. 갈 곳이 없으면 숨는다.

{{EX:HUB}}

---

## 실습 셸 공통

`pr` 장의 공통 뼈대다. 실습 표식 넷이 함께 켜진다.

1. 왼쪽 주홍 세로 띠(`.slide.pr::before`, 14px)
2. 「실습 N」 또는 「메인 과제」 라벨(`.pr-no`)
3. 타이머(`.timer`, F-pr-steps와 F-return)
4. 단계 번호(`.flow .n`)

구조는 모든 `pr` 장이 같다.

```html
<section class="slide pr f-steps" data-slide="P1-2">
  <header class="s-head">…</header>
  <div class="pr-wrap">
    <div class="pr-bar">…</div>            <!-- 머리줄 -->
    <div class="pr-top rv" style="--i:0">  <!-- 제목(+ 선택 lead) -->
      <h2 class="s-title">…</h2>
    </div>
    <div class="pr-main">…</div>           <!-- 레이아웃별 본문 -->
  </div>
</section>
```

- 머리줄: `<span class="pr-no">실습 1</span><span class="pr-name">회의 메모</span><span class="pr-steps" aria-label="4단계 중 2단계">…</span>`. 실습 장의 단계는 `① 목표 ② 진행 ③ 확인 ④ 고치기`, 메인 과제 장은 `① 기획 ② 제작 ③ 공개 ④ 개선`이다. 현재 단계에 `class="cur" aria-current="step"`을 준다(굵게 + 밑줄 + 주홍 선).
- `.pr-top`은 제목과 선택 lead(`<p class="pr-lead">`, 22px, 2줄 이내)를 담는다. lead는 F-pr-goal에만 둔다. lead가 있으면 본문 높이가 줄어든다.
- 본문 높이: lead 없을 때 454px(y 212~666), lead 한 줄이면 414px, 두 줄이면 약 380px. 모든 내용이 666px 안에 들어가야 한다.
- `.pr-cols`는 왼쪽 칸과 오른쪽 칸(`--lc`로 왼쪽 폭을 바꾼다, 기본 540px)을 나눈다. `.pr-left` · `.pr-right`가 그 안의 세로 흐름이다. `.tail` 클래스를 단 요소는 칸 아래쪽에 붙는다.
- 실습 장에는 개념 이름 · 개념 설명 · 개념 연결을 쓰지 않는다(D31).

---

## F-pr-goal

쓰는 장: {{USE:F-pr-goal}}. ① 목표. 결과물의 전후 미리보기(왼쪽 원본 → 오른쪽 결과)와 시간 · 준비물 · 결과물 세 칸.

- 본문: `.pv`(3열 격자: `svg.pv-before` 392px · `svg.pv-arrow` 96px · 결과 창) 아래에 `dl.meta3`(시간 · 준비물 · 결과물).
- 결과 창은 `.win.file`(파일 창)에 표를 넣었다. 표는 행 3개 안쪽이면 창이 세로로 넘치지 않는다.
- 왼쪽 원본 그림은 자유 SVG(392×250)다. 파일 이름은 `.fn`(mono 17px), 줄은 `.ln`, 핵심 줄은 `.ln.hot`(주홍)이다.
- `.meta3`: 시간은 `dd.big`(mono 40px), 결과물은 `.mk`로 강조한다.
- 제목의 대상에는 `em-ink`, lead의 파일 이름에는 `em-tag`를 썼다.
- 박스 1(결과 창).

{{EX:P1-1}}

---

## F-pr-steps

쓰는 장: {{USE:F-pr-steps}}. ② 진행. 단계 목록(왼쪽) · 요청문 터미널(오른쪽) · 타이머(왼쪽 아래) · 이어가기 안내(오른쪽 아래).

- 왼쪽: `ol.flow[data-w="todo"]` 안 `li > button > span.n + span.t`. 단계를 누르면 번호가 ✓로 바뀌고 글자가 회색이 된다. 다시 누르면 돌아온다. 네 단계 이내, 단계 하나는 2줄 이내(한 줄 21자 안팎, 42자 이내)다. 단계 글에 파일 이름을 넣을 때는 `<code>`를 쓴다.
- 타이머: `button.timer[data-min="8"]`(분 값은 속성). 안의 `.tv`(시간)와 `.tl`(상태 글)은 엔진이 바꾼다.
- 오른쪽: `.term.terminal-dark`(터미널 창)와 `p.keep.tail`(이어가기 안내 한 줄). 터미널은 「부품」 절을 본다.
- 터미널 용량: 본문 20px mono에서 한 줄 26자(한글), 본문 영역에 들어가는 줄은 9줄 안팎(이어가기 안내를 넣으면 9줄, 안 넣으면 11줄). 한글 기준 약 230자까지다. 더 길면 `term`의 글자가 커서 바닥선을 넘는다.
- lead는 두지 않는다(세로 공간).
- 박스 1(터미널). 메인 과제의 `F-pr-steps`(M1-2 · M4-1 등)도 같은 구조다.

{{EX:P1-2}}

---

## F-pr-check

쓰는 장: {{USE:F-pr-check}}. ③ 확인. 위쪽에 대조할 것(원문 창 + 결과 표 등), 아래쪽에 체크 목록.

- 본문: `.ck-top`(2열 격자, 위 칸 높이가 남는 만큼 늘어나고 내용은 세로 가운데) 다음에 `ul.ck-list.tail[data-w="todo"]`. 체크 항목은 한 줄 50자 이내, 3개 이내다. 눌러서 ☐ → ☑.
- **대조선**(실습 ③ 전용): `.ck-top[data-w="trace"]` 안에 왼쪽 원문 창(`.win.file`, 줄마다 `<span class="l ref" data-line="키">`)과 오른쪽 표(`<tr data-pick="키" tabindex="0" role="button">`). 행을 고르면 그 행의 키와 같은 `data-line` 줄이 강조(`.on`)되고 점선 대조선이 그려진다. 선은 행 왼쪽 끝에서 멈춰 글자를 가로지르지 않는다. 처음 선택은 `<tr class="on" aria-pressed="true">`와 `<span class="l ref on">`으로 적는다.
  - 대조선용 `svg.ck-link`는 **`<section>`의 마지막 자식**이다(`.pr-wrap` 밖). 안에 `path.a-draw`(`pathLength="100"`, `d=""`)와 `circle` 둘을 둔다. 엔진이 좌표를 채운다.
  - 이 장은 대조 방법만 보인다. 정답 표시 · ✕ · 강조된 오류 행을 넣지 않는다(D35).
  - 표는 열 3개(본문 14자 이내 · 기한 · 근거)까지 폭이 맞는다. `grid-template-columns:460px 1fr`로 왼쪽 창 폭을 정했다.
  - 원문 창 용량: 원문 줄 3개(각 2줄 이내)와 생략 표시 `⋮` 2개, 합쳐 8줄까지다. 이보다 길면 아래 체크 목록이 666px를 넘는다. 체크 항목은 3개 이내다.
- **변형**: `.ck-top`은 대조선 없이도 쓴다. 안에 넣을 것만 바꾼다 — 문항 전/후 예시(M1-3 · M1-5) · 결과 화면 모형 + 동그라미(M2-3 · M2-6) · 로그인 화면 모형(M3-3) · 주소창 모형(M3-5) · 판정표(M4-2).
- 박스 1(원문 창 또는 화면 모형).

{{EX:P1-3}}

---

## F-pr-fix

쓰는 장: {{USE:F-pr-fix}}. ④ 고치기. 찾은 곳 표시(접힘) · 고쳐 보낼 요청문 터미널 · 허브로 돌아가는 단추.

- `.pr-cols`(`style="--lc:500px"`). 왼쪽: 안내 한 줄 `p.fx-lead`와 `details.reveal`. 오른쪽: `.term`과 `button.back.tail`.
- **`details.reveal`**(강사가 눌러 공개하는 칸): `<summary>`에 「찾은 곳」과 `.hint`(「강사가 눌러 공개」), 본문은 `.reveal-body`. 처음에는 닫혀 있고 Enter · Space · 클릭으로 열린다. 열리면 `.hint`가 사라진다. 초안의 `[펼침]` 표기가 이 칸이고, 🗣 힌트도 같은 모양으로 접어 둔다.
  - 안에 원문 위치 그림(`svg.loc`, 150×210)과 글을 `.reveal-row`(2열)로 둘 수 있다.
  - 본문의 요점은 `em-line` 또는 `em-num`으로 잡는다.
- 터미널의 자리표시(〈 〉)는 `<span class="ph">〈행의 할 일〉</span>`로 감싼다(연한 아쿠아 굵은 글자). 복사하면 〈 〉가 그대로 들어가 사용자가 바꿔 쓴다.
- `button.back`: `data-go="HUB"` `data-vt-key="p1"`(허브의 같은 키 카드로 돌아가는 전환). 주홍 알약이다. 글자는 「허브로」.
- 박스 2(터미널 · 단추). M1-6 · M2-5 · M4-5처럼 터미널이나 펼침이 없는 ④는 있는 부품만 쓴다.

{{EX:P1-4}}

---

## F-pr-list

쓰는 장: {{USE:F-pr-list}}. 폴더 트리(파일 창) · 확인할 곳 동그라미 · 체크 목록 · 공개 범위 한 줄.

- `.pr-cols`(`style="--lc:380px"`). 왼쪽 `.win.file` 안 `pre.code`의 줄(`<span class="l">`)에 트리를 쓴다(`├ └` 문자). 동그라미를 칠 이름은 `<span class="ring-host">`로 감싼다(최대 3곳).
- 오른쪽: 체크 목록(`ul.ck-list[data-w="todo"]`)과 아래쪽 공개 범위 안내(`p.keep.tail`).
- 항목 머리는 `em-tag`(키 · 실명 · 파일 이름)로 잡는다.
- 박스 1(파일 창).

{{EX:M3-2}}

---

## F-pr-screen

쓰는 장: {{USE:F-pr-screen}}. 브라우저 화면 모형(D27 공통 화면 모형) + 단계 목록 + 타이머.

- `.pr-cols`(`style="--lc:430px"`). 왼쪽은 F-pr-steps와 같은 단계 목록과 타이머. 오른쪽은 `.win.browser`(창 바 + 주소줄 `span.win-url` + `.win-body`).
- 화면 안 표시는 번호 글자(①②③, `<b>`)와 `.drop`(끌어다 놓는 영역, 점선 `outline`), `.path`(주소), `em-tag`(단추 이름)로 한다. 면이나 테두리를 더하지 않는다(박스가 늘어난다).
- 화면의 글자는 도구 화면을 베끼지 않은 공통 표기다. 실제 도구의 메뉴 이름은 사용자 리허설(GR) 뒤에 정한다.
- `.drop`의 글자는 22px다(25자 이상이면 본문 하한이 적용된다).
- 박스 1(창).

{{EX:M3-4}}

---

## F-return

쓰는 장: {{USE:F-return}}. 슬롯이 끝난 뒤 점검 페이지 폴더로 돌아오는 장이다. F-pr-steps와 같은 구조에 이어가기 위치 칸이 들어간다.

- 루트 `slide pr f-return`. 머리줄은 메인 과제 표기(`메인 과제` · `AI 활용 습관 점검` · `① 기획 ② 제작 …`)다.
- 왼쪽: 단계 셋(`ol.flow`) + 타이머. 오른쪽: 터미널 + `div.resume.tail.rule`(`.lab`=「이어가기 위치」, `p.path`=폴더 경로).
- `.resume`는 박스 없이 왼쪽 세로선으로 묶는다. 경로는 `.path`(mono 굵게)다.
- 박스 1(터미널).

{{EX:R-A}}

---

## 부품

### 터미널 창 (D32)

요청문은 터미널 창으로 보인다. kit의 `.terminal-dark`(검정 면)에 `.term`(자리 · 글자)을 더한다.

```html
<div class="term terminal-dark rv" style="--i:2">
  <div class="terminal-bar"><span></span><span></span><span></span><b>요청문/01_회의메모.txt · 첫 요청</b><button class="copy" type="button" data-copy>복사</button></div>
  <div class="terminal-copy"><p><span class="terminal-prompt">&gt;</span> 요청문 첫 줄…<br>둘째 줄…<span class="terminal-cursor" aria-hidden="true"></span></p></div>
</div>
```

- 창 점 셋은 빈 `<span>` 셋이다. 제목 `<b>`은 요청문 파일 이름과 구간(`· 첫 요청`)이다.
- `data-copy` 단추를 누르면 `.terminal-copy`의 글자가 클립보드에 복사된다. 앞의 `>`(`.terminal-prompt`)와 커서(`.terminal-cursor`)는 빠지고, `<br>`는 줄바꿈이 된다. 버튼 글자가 「복사됨」으로 바뀌었다가 1.5초 뒤 돌아온다. 클립보드를 쓸 수 없는 환경에서는 `execCommand('copy')`로 대신한다.
- 복사 단추가 필요 없는 설명용 터미널(개념 장의 전/후 그림)은 단추 없이 쓴다.
- 글자 크기: 기본 20px(`.term`), 요청문이 짧으면 `class="term lg …"`로 22px. 터미널 글자는 하한 검사에서 빠진다.
- 한 창 안에 구간이 둘이면 `.terminal-copy`를 둘로 나누고 첫째에 `sep`(아래 선)를 준다. 구간 이름 표시는 `<span class="tc-tag">전</span>`이다.
- 자리표시(〈 〉)는 `<span class="ph">…</span>`.
- 요청문 원문은 zip의 `요청문/` 폴더 파일과 같아야 한다(`plans/FRAME-개편/gen/gen_prompts.py`가 정본).

### 파일 창과 화면 모형 (D27)

```html
<div class="win file">
  <div class="win-bar"><i></i><i></i><i></i><b>회의_0312.md</b></div>
  <div class="win-body"><pre class="code"><span class="l ref" data-line="19"><i>19</i>줄 내용</span><span class="l gap"><i>⋮</i></span><span class="l hit"><i>31</i>강조 줄</span></pre></div>
</div>
```

| 클래스 | 뜻 |
|---|---|
| `.win.file` | 파일 창. 제목은 mono(파일 이름) |
| `.win.browser` | 브라우저 창. 제목줄에 `span.win-url`(주소) |
| `.win.app` | 앱 창. `.win-body`가 `.win-side`(왼쪽 200px) + `.win-main` 격자 |
| `.code` > `.l` | 코드·파일 줄. `i`는 줄 번호(왼쪽 고정폭). `.ref`(참조 줄) · `.hit`(강조 줄, 주홍/페트롤 띠) · `.on`(대조선이 가리키는 줄) · `.gap`(생략 ⋮) · `.dir`(폴더 이름) |
| `.drop` | 끌어다 놓는 영역(점선 `outline`) |
| `.bubble` · `.bubble.me` | 채팅 말풍선(박스 1씩). 개념 장에서는 박스 없는 `.say`(아래)를 쓴다 |
| `.say` · `.say.me` | 박스 없는 대화. `span.who`(「질문」 · 「AI 답」) + `p` |

- 창 바깥 테두리만 박스 1개다. 창 안에 면이나 테두리를 더하지 않는다.
- `.code`는 줄바꿈을 보존하는 `pre`다. 줄(`span.l`)을 이어 붙여 쓰면 줄 사이 빈 줄이 생기지 않는다.
- 도구 화면은 CSS 공통 모형이다. 실제 캡처가 생기면 창 안 내용을 이미지로 바꾼다(O-4).
- 앱 창 모형 완성본은 시험 전용 슬라이드 `T-APP`이다. 왼쪽 `.win-side`(작업 폴더 · 대화 목록)와 오른쪽 `.win-main`(대화 `.say` + 입력줄 `p.win-url`)으로 나눈다. 대화는 `.say`로 써서 박스가 늘지 않게 했다.

{{EX:T-APP}}

### 표

`table.ftbl`. 머리 17px 800, 본문 20px, 아래 가는 줄만 있다. `td.src`는 mono 18px(근거 열), `.ftbl-cap`은 표 위 파일 이름 캡션이다. 결과 표는 파일 창(`.win.file`) 안에 넣거나, 대조선 장에서는 창 없이 쓴다. `tr[data-pick]`은 눌리는 행이다.

### 단계 · 체크 · 타이머

```html
<ol class="flow" data-w="todo">
  <li class="rv" style="--i:1"><button type="button" aria-pressed="false"><span class="n">1</span><span class="t">단계 글 <code>파일.txt</code></span></button></li>
</ol>

<ul class="ck-list" data-w="todo">
  <li class="rv" style="--i:3"><button type="button" aria-pressed="false"><span class="bx" aria-hidden="true">☐</span><span class="t">확인할 것</span></button></li>
</ul>

<button class="timer" type="button" data-min="8" aria-label="타이머 8분 — 누르면 시작, 다시 누르면 멈춤"><span class="tv">08:00</span><span class="tl">▶ 시작</span></button>
```

- `data-w="todo"` 목록은 `li > button[aria-pressed]`다. 누르면 `aria-pressed`와 `li.done`이 바뀌고 `.n`은 ✓, `.bx`는 ☑가 된다.
- 타이머는 `data-min`(분, 소수 가능: `1.5`)이 있는 요소면 어디든 된다. `.tv`(mm:ss)가 시간이고 `.tl`이 상태 글이다. 처음 시간은 엔진이 `data-min`에서 만든다(마크업의 `.tv` 글자는 같은 값으로 적는다). 눌러서 시작 → 멈춤(「▶ 이어서」) → 0이 되면 「끝 · 다시 시작」. 타이머마다 따로 돌고 장을 옮겨도 계속 간다.
- 큰 타이머(쉬는 시간): `class="timer big"`(숫자 120px). 아래 `BR-1`은 kit `.center-msg` 안에 `button.timer.big[data-min="10"]`을 넣었다.

{{EX:BR-1}}

### 전후 토글

전과 후를 나란히 두고 강조만 바꾸거나(C-08 예시), 한 자리에서 교체하는(C-06 예시) 두 방식이 있다. 둘 다 `data-w="toggle"`이다. 전후 글자를 바꾸는 단추는 `data-labels="후 보기|전 보기"`처럼 상태별 글을 준다.

### 펼침

`details.reveal`(F-pr-fix 절). `<details>`라서 키보드 Enter · Space로 열고 닫는다. 인쇄할 때는 그 시점의 열림 상태로 나온다.

### 버튼

| 클래스 | 모양 | 박스 |
|---|---|---|
| `.back` | 알약 면(실습 주홍, 그 밖 아쿠아). 이동 · 돌아가기 | 1 |
| `.wg-btn` | 알약 면(페트롤). 개념 위젯 조작 | 1 |
| `.wg-link` | 밑줄 글자. 개념 위젯 조작 | 0 |
| `.copy` | 터미널 제목줄의 밑줄 글자 | 0 |

---

## 이동과 복귀

이동은 전부 슬라이드 ID로 한다. 번호를 쓰지 않는다.

| 속성 | 자리 | 뜻 |
|---|---|---|
| `data-go="ID"` | 버튼 · 카드 등 눌리는 요소 | 그 ID의 장으로 이동 |
| `data-vt-key="키"` | 출발 요소와 도착 장의 요소 | 같은 키끼리 공유 요소 전환(View Transition 0.45초). 도착 장에 같은 키가 없으면 전환 없이 바로 이동 |
| `data-return` | 허브의 「수업으로 돌아가기」 | 기억한 슬롯의 복귀 장으로 이동 |
| `data-return-to="ID"` | 슬롯 섹션 | 그 슬롯에서 나갈 때 기억해 둘 복귀 장 ID. 없으면 DOM의 다음 장 |
| `data-pr="P1"` | 허브 카드 · 슬롯 미니 카드 | 실습 묶음 이름. 카드를 누르면 「진행함」으로 기억해 `.is-done` 표시 |

- 흐름: 슬롯(SLOT-A) → 미니 카드 클릭 → 허브(출발 슬롯 기억) → 카드 클릭 → 실습 ① → (진행) → ④의 「허브로」 → 허브 → 「수업으로 돌아가기」 → 복귀 장(R-A).
- 슬롯을 거치지 않고 허브에 온 경우(발표 메뉴 · 쪽 번호 등): 「수업으로 돌아가기」는 허브 · 실습 밖에서 마지막으로 본 장으로 간다. 그런 장이 없으면 단추가 숨는다.
- 기억은 `sessionStorage`(`frame.origin` · `frame.done`)에 있다. 새로고침해도 남고 탭을 닫으면 사라진다.
- 주소 `#slide=ID`(예: `#slide=P1-3`)로 그 장을 바로 연다. 종전 `#slide=번호`도 된다.
- 허브 구간(PART 5)은 선형 덱에서 맨 뒤에 붙는다. PDF에서는 링크가 동작하지 않고 장이 순서대로 나온다.
- 배포본에서도 이동 · 복귀 · 복사 · 위젯이 동작한다(시험: 단일 파일 배포본에서 확인, D2Coding CDN 링크 제외).

---

## 등록과 검증

### layout_families (E5 계약에 등재)

`deck.contract.json`의 `layout_families`에 아래를 그대로 넣는다. 등재하지 않으면 새 구도가 전부 `other`로 묶여 「동일 구도 연속」 오탐이 난다.

```json
"layout_families": {
  "f-cover": "cover-frame", "f-divider": "divider-frame", "f-concept": "concept-fig",
  "f-slot": "slot", "f-hub": "hub",
  "f-goal": "pr-goal", "f-steps": "pr-steps", "f-check": "pr-check", "f-fix": "pr-fix",
  "f-return": "pr-return", "f-list": "pr-list", "f-screen": "pr-screen"
}
```

- `terminal-dark`가 든 장은 계약보다 먼저 `terminal` 구도로 판정된다. 터미널이 있는 실습 장(② · ④ · 복귀)이 이어서 3번 나오지 않게 순서를 본다.
- 개념 장 틀(`f-concept`)을 쓰는 장이 3장 연속이면 「3연속 금지」에 걸린다.

### 고정 슬라이드 마커 (`s02-slide` · `s03-slide`)

`verify_deck.py`는 `s02-slide`와 `s03-slide` 클래스를 가진 장이 덱에 있어야 PASS한다(`FIXED` 상수라서 계약으로 끌 수 없다). 이 덱에는 고정 도입 · 아젠다 장이 없다. 두 클래스를 일반 장 둘의 `class`에 덧붙이면 검사가 통과하고, shell CSS가 kit의 배치 규칙을 되돌려 놓아서 화면이 바뀌지 않는다. 시험에서 `C-06`에 `s02-slide`, `R-A`에 `s03-slide`를 달고 전후 스크린샷을 비교해 픽셀 차이가 없었다(`tmp/frame/E1/marker_check.py`). 어느 장에 달지는 E5(메인)가 정한다.

### 명령

```powershell
python scripts/assemble_deck.py courses/AI_에이전트_실습워크숍_4시간/sessions/1주차/강의덱.초안
$env:CREATE_SLIDES_COURSE = "AI_에이전트_실습워크숍_4시간"      # 과목이 여럿이라 verify_deck의 계약 탐색에 필요하다
python scripts/verify_deck.py courses/AI_에이전트_실습워크숍_4시간/sessions/1주차/강의덱.html --parts 3
```

- `--parts N`의 N은 `part-divider` 클래스 섹션의 수다. shell은 `f-divider`(B2-0 · B3-0 · B4-0) 셋에 이 클래스를 달았으므로 3이다. PLAN E6의 `--parts 5`는 part 파일 수로 읽힌다 — 그대로 넣으면 FAIL하므로 E5/E6에서 정한다.
- 브라우저 측정은 저장소 루트에서 `python -m http.server 8799`를 띄우고, 주소에 `?audit`를 붙여 연 뒤 `scripts/audit_all.js`를 돌린다(`references/검증-명령-지도.md` §3). `?audit`는 연출 없이 최종 상태를 재게 한다.

### 시험 조립 결과 (`tmp/frame/E1/t/`)

| 항목 | 결과 |
|---|---|
| 조립 | `assemble_deck.py` PASS, 22장 · part 2개(`part-01` 13장 · `part-02` 9장) |
| 보이는 슬라이드 · styleSheets | 1장 · 7개(폰트 2 · kit 3 · 테마 1 · 인라인 1), 규칙 수 0인 시트 없음 |
| 조작 | 47항목 PASS(`tmp/frame/E1/interact.py`) |
| 렌더 감사(`audit_all.js`, `?audit`) | 바닥선 초과 · 이탈 · 겹침 · 어절 잘림 · 오버플로 · 빈 슬롯 전부 0, 폰트 하한 0, 자간 0, 빈 상자 0, 가려짐 0 |
| 밀도 계열 | sparse 10(터미널 · 창 · 미니 카드가 글자 수에 비해 넓음 — 사람 검토 범주), lowFill 0 |
| `verify_deck.py --parts 1` | 계약 없이: FAIL 3(s02 마커 없음 · s03 마커 없음 · 같은 구도 4연속). 두 마커 + `layout_families` 등재 + 구도가 이어지지 않게 재배열한 사본: FAIL 0 · WARN 1(계약에 덱 항목 없음) · PASS 48 |
| 배포본 | `inline_deck.py --offline`: D2Coding 링크가 있는 원본은 FAIL, 그 링크를 뺀 사본은 PASS. 사본에서 허브 이동 · 복귀 · 복사 · 위젯 동작 |
| PDF | `page.pdf()` 22쪽. 방문하지 않은 장의 대조선 경로 · 동그라미 존재 |

---

## 장 작성 순서와 오류

1. 결정표에서 ID · 레이아웃 · 박스 예산 · 강조 열을 읽는다.
2. 이 문서의 해당 절 예시를 복사해 `data-slide`와 루트 클래스를 확인한다.
3. 표준 헤더의 `.s-team`을 정한다.
4. 제목 · 본문 문구를 초안 원문 그대로 옮긴다. 제목은 34자 이내.
5. `rv`와 `--i`를 읽는 순서로 붙인다.
6. 강조를 2~4곳 고른다(형태 2종 이내).
7. 용량을 센다(터미널 9줄 · 개념 텍스트 8줄 · 단계 4개 · 체크 3개).
8. 💬 👀 🗣 기호와 강사 멘트가 없는지, 색이 토큰뿐인지 본다.
9. 조립해 열고 1280×720에서 한 장씩 본다. 바닥선(666px) 아래로 내려간 것이 없어야 한다.

자주 나는 오류.

| 증상 | 원인 |
|---|---|
| 글자가 14px인데 감사가 「서술문 하한 위반」으로 잡음 | 한 요소의 글자가 25자 이상 |
| 터미널 파일 이름이 중간에서 끊김 | 터미널은 공백에서만 줄이 바뀐다. 파일 이름이 한 줄 폭(26자)보다 길면 끊긴다 |
| 대조선이 안 그려짐 | `svg.ck-link`가 `.pr-wrap` 안에 있거나, `data-pick`과 `data-line`의 키가 다름 |
| 위젯이 처음에 비어 보임 | 처음 상태의 요소에 `is-on`을 쓰지 않았고 `data-state`가 없음 |
| 동그라미가 없음 | `.ring-host`가 접힌 칸 안에 있음(보이면 그려진다) 또는 글자가 없음 |
| 박스가 예산을 넘음 | `.wg-btn` · `.bubble` · `.cx-fig` 면이 겹쳤음 — 박스 예산 표를 본다 |
| 애니메이션이 끝나도 흐림 | `.rv` 요소에 직접 `opacity`를 줌 |

---

## 알려진 한계

- **오프라인 배포본**: `inline_deck.py --offline`이 D2Coding CDN 링크(`d2coding-full.css`)에서 `offline external dependency`로 FAIL한다. shell은 지시대로 그 링크를 갖고 있다. 링크를 지운 사본으로는 배포본이 만들어지고 이동 · 복사 · 위젯이 동작했다(Pretendard는 서브셋이 임베드된다). D2Coding은 `kit/fonts`에 없고 `font_embed.py`가 Pretendard만 다룬다. E10에서 D2Coding를 넣는 방법을 정해야 한다. 글꼴이 없으면 `--font-mono`의 다음 후보(JetBrains Mono → 시스템 mono)로 그려진다.
- **verify_deck 고정 슬라이드**: `s02-slide` · `s03-slide` 마커가 필요하다(위 절).
- **`--parts` 값**: PLAN의 5는 part 파일 수로 보이며 `part-divider` 수와 다르다.
- **View Transition**: 탭이 숨겨진 상태(화면 공유로 창이 가려진 경우 등)에서는 브라우저가 전환을 취소해 즉시 이동한다. 기능은 같다.
- **PDF**: 링크와 위젯은 동작하지 않고 처음 상태로 인쇄된다. 대조선과 동그라미는 엔진이 인쇄 전에 그려 둔다(시험: PDF 22쪽 · 방문하지 않은 장의 대조선 경로 존재).
- **밀도 WARN**: 터미널 창 · 미니 카드 묶음은 글자 수에 비해 면이 넓어 `sparse`로 잡힌다. 실습 요청문은 본래 그렇다. 사람 검토 범주로 두거나 계약 waiver에 사유를 적는다(메인).
- **화면 모형의 글자**: F-pr-screen 예시의 화면 글자(폴더를 여기에 놓습니다 등)는 공통 표기다. 실제 도구 메뉴 이름은 미확인이고 GR 리허설 뒤에 바뀐다.
- **개념 장의 예시 대화**(C-06)와 요청문(C-08)은 시험용 문구다. 실제 문구는 초안을 따른다.
