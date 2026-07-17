# MEMORY — vibecoding-deck

> 이 스킬을 다룰 때 누적된 하드윈 지식. 새 작업 전 훑고, 새로 배운 건 여기 갱신.

## 이 스킬이 하는 일
채워진 슬라이드 계획서(MD) → 1280×720 HTML 웹덱 조립(40~50대 대상). 정보 모양을 먼저 판단해 레이아웃/차트를 고른다. 코드 시각화 우선, "좌 글/우 시각" 쏠림 금지(공급+측정으로).

## 핵심 메커니즘 (건드리지 말 것)
- **판단 게이트**: 슬라이드마다 `kit/guide/정보모양-taxonomy.md`의 12 정보모양으로 분류 → `kit/layouts/by-shape.md`·`kit/charts/by-shape.md` 역인덱스에서 후보 → **레이아웃과 element를 따로** 골라 얹음(레이아웃 ≠ 다이어그램).
- **no-default**: 어떤 레이아웃도 "기본/가장 흔한"으로 프레이밍 금지. split(좌우분할)은 역인덱스 후순위·희소·연속 금지. 8패밀리 균형(합 50, split 4=8%).
- **조립 산물**: 조립 전 "슬라이드 결정표"(모양→패밀리→element→직전과 다른가)를 먼저 써서 단조를 코딩 전에 잡는다.

## ⚠️ 반복된 버그 패턴 (검증이 매번 잡음 — 미리 피하라)
1. **한글 전각폭**: 전각 ≈ 1em advance → 큰 디스플레이 텍스트 가로폭 ≈ **글자수 × 폰트px**(숫자·영문 ≈0.55em). 가용 폭 **1152px**. 큰 단어/숫자 capacity는 이 폭으로 산정(전각 240px면 ≤4자).
2. **줄 높이**: 본문 22px × line-height 1.78 ≈ **줄당 39px**, 2줄 ≈ **78px**(50px 아님!). 카드 행 ≈ 헤드라인28 + 본문줄수×39 + gap28. 세로 예산 **548px** → 2줄 본문이면 **4행**이 현실적.
3. **토큰만**: `:root` 밖 raw `#hex` 금지. 흰색은 **`var(--white)`**(`#fff` 아님). 구조·주 강조는 **`--blue`만**, `--blue-soft`는 배경, `--periwinkle`는 비강조 데이터에만. **민트·코랄 fill 위엔 흰 글자 금지** → `--on-mint`/`--on-coral` 짙은 글자. 단, `.hl-mint-mark`은 글자폭만 감싸는 흰 글자 예외.
4. **no-default 검사**: 리터럴 `기본` grep은 오탐(CSS 기본 스타일). "레이아웃을 기본/최다로 규정하는 **문장**" 의미 검사로.
5. **공유 텍스트 클래스를 `<p>`에 직접 붙일 때 기본 마진을 지운다**: `.s-body p{...}`는 자손 선택자라 `<p class="s-body">` 자신에는 적용되지 않는다. UA 기본 단락 마진이 548px 세로 예산을 넘겨도 `overflow:hidden`에 가려질 수 있으므로, 새 컴포넌트에서 `.s-body`·`.s-lead` 등을 `<p>`에 직접 쓰면 해당 스코프에 `margin:0` 또는 의도한 값을 명시하고 브라우저 실측으로 확인한다.

## 색 시스템 v2 (2026-07-13, 확정) — 정본: `_dev/설계기록/색시스템-v2-명세.md`
- **브랜드 3색**: `--blue #1D4ED8`(구조) · `--mint #14B8A6`(행동·안전, fill) · `--coral #F97360`(주의, fill) · `--red #DC2626`(오류). 텍스트/보더는 `--mint-deep #0F766E`·`--coral-deep #C2452F`.
- ⚠️ **navy 사용 금지**(`var(--navy)` 0, 어두운 배경/텍스트는 `--ink`). `--periwinkle`=비강조 데이터만. 옛 토큰(`--cobalt`·`--green`·`--orange`·`--yellow-*`) 렌더 사용처 0.
- **폼 토큰**: `--r-lg20/md14/sm10/pill999` · `--shadow-sm/md/lg/blue`(카드=r-lg+soft shadow) · `--font-mono`(JetBrains Mono, 코드/터미널).
- 차트는 모노강조(블루 1곳 + periwinkle 램프, 무지개 금지).

## 판단 규칙 v2.1~v2.3 (누적 적용됨 — 조립 시 항상 준수)
- **발표 UI**: 하단 바=`--glass-white` 고투명, 상세 메뉴=`--glass-thick rgba(232,235,240,.76)`. **리모컨은 마우스 이동 시에만**(슬라이드 전환 keydown엔 `poke()` 넣지 않음 — deck-template·layouts/charts catalog·데모·atlas·산출 덱 전부 동기화 완료).
- ⚠️ **번호배지 민트는 `.num-circle`·`.work-step .n`·`.pd-dot.is-active` 셋만**. 다이어그램/플로우 노드·`.timing`은 블루(구조). "번호=민트" 일괄 적용 금지.
- **색=의미(장식 아님)**: 구조=블루. **강조어는 민트가 기본**(`.hl-mint-text`/`-underline`/`-mark`을 문맥에 맞게), 블루 `.hl`은 구조와 결부될 때만 절제 — **한 화면을 파란색으로 도배하지 않는다**.
- **세로 균형(하단 여백 금지)**: `.center-msg`(deck.css)는 자동 세로중앙. `patterns.css`의 `.s-full.fill`(격자 확장)을 정보 적은 `.s-full`에 얹어 캔버스 전체를 쓴다. `.s-full.solo`는 **더 이상 콜아웃을 늘려서 채우지 않는다**(아래 폭 규칙과 통일, 2026-07-15 재설계) — 컨테이너에 `justify-content:center`, 콜아웃은 `.hug-center`와 동일 속성으로 자기 크기 그대로 중앙에.
- **박스 크기=정보량**(상대+절대, 세로+가로 전부 본다):
  - 세로(패딩): 배너 하나만 있어도 세로 패딩 합이 콘텐츠 높이의 **1/3 넘으면 과다** — 1~2줄=12~14px, 3줄↑=16~20px. 실측: `.concept-bottom` 패딩 41%(36/88px)→33%(24/73px).
  - 가로(폭): 짧은 문장 하나 담은 단독 박스를 컨테이너 폭에 억지로 늘리지 않는다 — **`.hug-center`**(`deck.css`: `width:fit-content;max-width:860px;margin:auto;align-self:center;text-align:center`)를 붙인다. `.concept-bottom`·`.s-full.solo > .callout`은 기본 내장. **예외**: 시퀀스 칩(`.concept-flow`)·대비/체크리스트 격자(`cc-grid`·`grid-2/3`) 안 짝 콜아웃은 폭 전체 유지(그게 의미). ⚠️ **`flex-column` 부모(예: `.concept-panel`) 안에선 `width`만으론 안 줄어든다** — `align-items:stretch` 기본값이 이기므로 `align-self`도 필요(`.hug-center`에 포함). 실측: 1주차 덱 콜아웃 15개(격자 짝 14개 제외) 45~83%→17~55%로. 데모 파일 3곳 동일 적용.
  - 조립 중 박스 완성 직후 스스로 자문("내용보다 커 보이나?") + SKILL.md §8 브라우저 검증에도 체크 포함.
- **줄바꿈은 문맥 경계에서**: 수동 `<br>`은 단어를 끊지 않고 구·절 경계(조사·어미가 앞줄에 매달리지 않게).
- 기타 확정 규칙: eyebrow=`--blue-soft` 배경 pill(본문 슬라이드만) · accent-bar 64×5px · work-step padding11px/gap10px · 헤더 파트진행(`.s-part`)·하단 페이지네이션(`.s-pageno`) JS 자동주입 · 그라데이션 금지(cover 포함) · 민트·코랄 fill 위 흰 글자 금지(`.hl-mint-mark` 예외).
- ⚠️ **박스 표면 규칙(2026-07-16, verify 강제)**: 흰 캔버스 위 카드/박스는 ① 의미 틴트 fill(구조=`--blue-soft` 기본 / 행동=`--mint-soft` / 주의=`--coral-soft`)+계열 보더 또는 ② 흰 fill+유색 보더(`--blue-line-strong`/`--mint-line`(신규 #C9EAE4)/`--coral-line`). **흰 fill+`--line` 근백색 보더 단독 조합 금지**(verify가 kit CSS+덱 인라인 모두 FAIL). `--line`은 내부 구분선(방향 보더·표 셀선) 전용. 예외: 코드/터미널 표면·`.shot-*`·`.pd-dot`·표. 매핑: `.card`=블루-소프트 · `.card.surface`=블루-패널(뮤트, `--surface` 아님 — 토큰 값 재조정 금지) · `.work-step`=민트-소프트 · 촘촘한 그리드(rev-card·cmp·lc·risk·metric·mapc·concept-card·다이어그램 노드)=흰 fill+블루-라인-스트롱(블루 도배 방지). 정본: 색시스템-v2-명세 §1b.
- ⚠️ **넘버 행 수직 중앙(2026-07-16, verify 강제)**: `.work-step`·`.agenda-item`=`align-items:center`(원형 배지 대비 텍스트 중앙 — 본문 `<span>` 없이 `<b>`만 있어도). 고아 마진은 `b:last-child{margin-bottom:0}`을 **deck.css와 patterns.css(`.eval-steps` 스코프) 양쪽**에 둬야 함(로드 순서상 patterns.css가 이김). **`.s03-slide .an-item`은 예외** — `::after` 커넥터 좌표가 상단 정렬 전제.
- ✅ **atlas 프로즌 CSS 재동기화 완료(2026-07-16)**: 박스 표면 규칙 반영 시 통짜 교체 — 그간 미반영이던 세로/가로 균형 변경분(hug-center·concept-recap v2)도 함께 해소. 이후 kit CSS 구조 변경 시 §프로즌 CSS 드리프트 절차 반복 필요. (2026-07-17 an-2col 반영 시 재실행 — 프로즌==deck.css 어서션 포함. 같은 날 아젠다 v3 반영 시 3차 재실행 — splice 스크립트+동일 어서션. ⚠️ 생성기 리빌드 불가 상태, `## 미해결` 참조.)
- ⚠️ **아젠다 2열 an-2col(2026-07-17, verify 강제)**: `.an-item` 4개 초과 시 **크기 축소 금지** → `.an-right`에 `an-2col` 부여(deck.css §13 — `display:block`이 핵심, column-count는 flex에서 무효). column-count:2가 임의 N 자동 균형분배(5→3+2, 6→3+3). **2열도 수직 중앙(v3 — `height:fit-content`+`margin:auto 0` 절대배치 밴드 중앙, 옛 "상단 정렬 예외" 폐지)·`::after` 커넥터 끔**. ≤4는 1열·미부여(WARN). 1열 `.an-item::after` 좌표(배지 64px 기준 left:31/top:32/bottom:-48)·`.an-track{display:none}`은 불변.
- ⚠️ **아젠다 v3(2026-07-17, verify 강제)**: 제목=고정 멘트 **"오늘 배우게 될 것"**(48px, 초안 아젠다 행 제목과 무관하게 항상 이 문구 — 초안 문서는 안 고침). 제목 아래 민트 pill 바 `.an-bar`(96×10)+리드 1~2줄(장문 금지). **코랄 스파크 `.an-spark`는 `.an-left` 내부 첫 자식(마크업 고정)** — 제목 "오" 좌상단 대각(left:-28/top:-36, 글리프까지 좌19px·상32px), 세로 중앙을 따라감. 슬라이드 직속 옛 배치(left:452/top:122) 금지. `.an-num` 64px **플랫(box-shadow 금지)**·`.an-h` 30px **블루**(구조색 — "블루 도배 금지"(위 v2.1)와 무관, 사용자 확정이므로 되돌리지 말 것)·`.an-d` 22px(본문 하한 충족)·리드 24px(2026-07-17 "글씨 작다" 피드백로 1차 26/19/19에서 상향). 좌측 `.an-left`도 세로 중앙(`margin:auto 0`). verify 신규 2검사: ① s03 제목 고정 문구(--parts 0 카탈로그 모드 스킵) ② `.an-num` box-shadow 금지(kit CSS+덱 인라인). 스타터·데모 마크업 동기화 완료(아틀라스는 프로즌 CSS 재동기화 절차 참조).
- ⚠️ **브랜드 표기(2026-07-17)**: 헤더/표지 `.s-brand`·`<title>`·팀명·조직명 = **VIBECODING**(영문, letter-spacing .02em). **강의 콘텐츠 속 개념어 "바이브코딩"은 원문 유지**(1주차 덱 6건: 103·318 주석, 182 an-d, 224 pd-sub, 325 def-term, 326 cm-title / 발표자노트 L83) — 블라인드 replace_all 금지, 컨텍스트 앵커 치환만. 아틀라스 **생성기**(build_layout_atlas.mjs)에 브랜드 리터럴 2곳(8행 head()·91행 표지) — 정적 HTML만 고치면 리빌드 시 회귀.
- ⚠️ **본문 eyebrow PART 형식 금지(2026-07-17, verify 강제)**: `.s-eyebrow`에 "PART n · 파트명"을 쓰지 않는다(헤더 `.s-part` 진행과 중복). 의미형 eyebrow만 허용. 활동 `.timing` 배지는 eyebrow가 아니라 **`.s-title` 바로 위 독립 줄**에 단독 배치(inline-block+margin으로 CSS 수정 0). `.pd-eyebrow`(파트전환, `PART n/N` 슬래시 포맷)는 별개 클래스 — 대상 아님.

## 표지 v4 — 라이트 지오메트리 (최종·2026-07-13) — 탐색사: `_dev/설계기록/탐색-아카이브/`
- 배경=`--paper #F4F8FB`(브랜드-화이트, 블루 언더톤) + 블루 도트그리드(그라데 아님). 도형=아이소메트릭 3단 큐브 스택(`data-cube`×3·polygon×9, fill=토큰)+코랄 스파크 1. 큐브면=blue-soft(top)/blue(left)/mint(right).
- 슬롯: `.cover-geo`·`.cover-lead`(`>_` 없음)·`.cover-title .ko`(강조 `.hl`=`--mint-deep`)·`.cover-terminal`(`>_`+주차 핵심 한 문장 요청+민트 캐럿)·`.cover-presenter`. 캐럿은 터미널 박스에만(제목엔 없음).
- **폰트**: Pretendard만(모노 CDN 미로드) — 모노 폰트 전면 금지(한글이 모노폭에 물려 어색).
- 재사용 도형 어휘: 아이소 큐브·오프셋 링/벤·벤토(파트구분·본문 확장 시 축소·재배치). `.closing`(다크)은 옵션 대안, 기본 마무리=`concept-recap`.

## 아젠다·파트전환 v2 (최종·2026-07-14) — 탐색사: `_dev/설계기록/탐색-아카이브/`
- **아젠다**(`.s03-slide`): 헤더=로고+브랜드+라인만(팀명 제거, 라인 flex:1 확장). 본문=좌 `.an-left`(제목+3줄 인트로)+우 `.an-right`(flex 세로 타임라인, `.an-item`을 항목 수만큼 반복 — **노드 수 고정 아님**, 권장 3~6, 연결선은 `::after` 자동). `.an-num`=48px **블루 fill**(구조 노드, 민트 아님).
- **파트전환**(`.part-divider`): 헤더 전체 제거(풀캔버스 히어로). `.dv-hero`=표지와 동일 토큰 아이소 큐브 3개(9면)+코랄 스파크. `.pd-dots`→`.pd-eyebrow`("PART n/N")→`.pd-title`(96px nowrap, **12자 이내 권장**)→`.pd-sub`.
- ⚠️ **`.pd-dot`/`.pd-dot.is-active` 셀렉터명 변경 금지** — verify가 이 셀렉터를 민트 배지 정규식 검사 대상으로 쓴다.
- `deck.css`를 외부링크하는 실 덱은 이 마크업 변경의 영향을 받는다(데모 파일 등 — 이미 동기화 완료).

## ⚠️ 프로즌 CSS 드리프트 (2026-07-14 · `outputs/vibecoding-deck-layout-atlas.html`)
`deck.css`를 **인라인/얼려 복사**한 산출물(outputs/ 스냅샷)은 kit 원본이 바뀌어도 자동으로 안 따라옴 → 구조적 CSS 규칙 변경 시 이 파일 내장 CSS 블록(`/* SKU LIKELION */`~`/* layout atlas additions */`)을 **현재 deck.css로 통짜 재동기화**할 것. 반대로 **외부 링크** 파일(`데모_제작규칙.html`)은 CSS는 최신이나 마크업이 드리프트 → "CSS 얼림"·"마크업 얼림" 둘 다 체크. (최근 재동기화: 2026-07-16 박스 표면 규칙 패스 — 아틀라스=CSS 통짜 교체(1~17행 유지 + deck.css 전문 + `/* layout atlas additions */` 이후 유지), 데모=마크업 콘텐츠 동기화(규칙 ④ 슬라이드 추가·계획서/시각화 의도→콘텐츠 초안·이미지 모드 문구·B11 참조 표·v0.5).)

## concept-recap v2 — 풀폭 상하 밴드 (2026-07-15 · 재사용 템플릿 조건)
마무리 슬라이드가 `.concept-panel{width:700px}` 좌측 컬럼 고정이라 우측 ~460px가 항상 비었던 문제. 10안 시안(`_dev/설계기록/탐색-아카이브/마무리_초안_10안.html`) 중 **"상하 3단 풀폭"**을 "**계속 재사용할 템플릿**" 조건으로 채택 — 좌우분할·1:1 노드-카드 결합·고정 그리드 좌표 안은 카드/단계 개수가 덱마다 달라지면 코드를 다시 짜야 해 재사용 부적합.
- **구조**: `.concept-panel`(`position:absolute;left/right:64;top:118;bottom:54`+`flex-direction:column;justify-content:center;gap:20px`)이 4밴드(`.concept-top`(eyebrow+title+lead 래퍼, 신규)·`.concept-flow`·`.concept-cards`·`.concept-bottom`)를 세로로 쌓는다.
- **N-agnostic(핵심)**: `.concept-flow span{flex:1}`로 단계 수 자동 등분. `.concept-cards{grid-template-columns:repeat(auto-fit,minmax(230px,1fr))}`(옛 `1fr 1fr` 하드코딩 교체)로 카드 수에 맞춰 열 자동 재분배 — 브라우저 DOM 교체로 3/4/6카드·6단계 전부 오버플로 0·풀폭 유지 실증.
- **동기화 완료**: `kit/styles/deck.css`(정본)·`kit/starter/deck-template.html`·`데모_제작규칙.html`·`1주차_강의덱.html`. verify 무회귀·브라우저 오버플로 0.
- **탐색 아카이브**: `마무리_초안_10안.html`(V1~V10) → `_dev/설계기록/탐색-아카이브/`.

## ⚠️ 버그 #4·#5 — 콘텐츠 클래스가 `.slide` 지오메트리 가로챔 (해결됨 2026-07-14)
콘텐츠 레이아웃 클래스(`.atlas-*` 등, `display:grid`/`position:absolute;top/left` 지정)를 **슬라이드 section 자체에 직접** 붙이면, 같은 특이도의 원본 `.slide` 규칙을 소스순서로 이겨 → 여러 슬라이드 동시표시·박스 대각선 오프셋을 유발. **고침**: `kit/styles/deck.css` §2에서 `.slide`가 소유한 지오메트리 속성 전체(`display/position/top/left/transform`)를 `!important`로 통째 봉인. **교훈**: 콘텐츠 클래스는 section이 아니라 내부 wrapper div에만 — "엔진이 소유한 속성 집합"을 통째로 방어할 것.

## kit 참조본·데모 파일 v4 동기화 (2026-07-14, 완료)
`charts/catalog.html` 표지·`데모_제작규칙.html`(표지·글래스나브·raw hex)를 v4/색시스템v2로 동기화 완료.
- ⚠️ **카탈로그 검증 주의**: `catalog.html`류는 카탈로그이지 완성 덱이 아니므로 `--parts 0`으로 실행하고 표지·토큰·민트배지 검사만 해석한다. 외부 `deck.css`의 글래스 토큰을 못 읽던 오탐은 2026-07-16에 `verify_deck.py`가 로컬 링크 CSS를 읽도록 수정해 해소했다.

## 입력 형식 — 콘텐츠 초안 (2026-07-14 교체, 현재 공식 형식)
공식 입력은 **`입력양식/콘텐츠초안템플릿.md`**(교시별 `#·슬라이드 제목·본문 문구·비유·멘트` 4열 표 + 아이콘 범례). 옛 13라벨 `시각화 의도` 폼은 폐기(`_dev/설계기록/폐기된-슬라이드계획서템플릿.md`로 이동 — no-git 저장소라 삭제 대신 이동 원칙).
- **의미: 정보 모양 판단을 스킬이 항상 전담**(`시각화 의도` 입력 칸이 없음). PART 매핑도 템플릿에 안 채움 → **조립 직전 스킬이 항상 확인**(하드코딩 금지). 덱 메타: 팀명 필드 제거(PART 진행률로 대체), 로고=고정 자산.
- ⚠️ **아이콘 라우팅(고정)**: `💬`(농담)·`👀`(시연 큐) → **HTML 주석**(`<!-- 발표노트: … -->`) · `🗣`(막힐 때만 예시) → **`.hint-reveal`**(접힘 힌트, 인쇄해도 접힘=네이티브 `<details>` 기본). 한 셀에 여러 아이콘이면 분리 라우팅. **이모지 문자는 최종 HTML에 남기면 안 됨** — `verify_deck.py`가 FAIL로 잡는다.
- **`.hint-reveal`은 `deck.css` 소관**(patterns.css 아님). 네이티브 `<details>/<summary>`, JS 0. **솔리드 `--mint` fill 안 씀**(닫힘=`--surface`, 열림 body=`--mint-soft`) → 민트 배지 3종 규칙과 무관. 본문 22px 하한 미적용(보조 18px).
- ⚠️ **`.hint-reveal` 오버플로 함정**: 브라우저 검증이 **닫힌 상태만** 훑으면 열림 시 548px 초과를 놓친다. SKILL.md §8에 "닫힌+강제로 연 상태 둘 다 검사" 명문화. 긴 프롬프트가 특히 위험.
- **발표자 노트 HTML**: 멘트(💬/👀/🗣)가 있으면 `kit/starter/presenter-notes-template.html`을 복제해 `<덱>_발표자노트.html`을 메인 덱과 별개로 산출. **🗣는 펼친 상태**(강사는 미리 다 봐야 함). deck.css 링크 안 함(자립 문서), 이모지 잔존 허용(verify는 덱에만 적용).
- **콘텐츠 소유권**: 초안의 `슬라이드 제목`·`본문 문구`는 재작성 금지. "제목은 결론으로"는 스킬이 직접 짓는 제목(형식 없는 브리프 경로)에만 적용.

## 검증 (측정 우선)
- 정적: `python scripts/verify_deck.py <덱>.html --parts N` — 슬라이드·파트전환=파트수·코드viz vs 이미지·구도 다양성·같은 구도 연속·토큰·**아이콘 마커 누출(💬/🗣/👀 FAIL)**·**힌트 리빌 summary(WARN)**.
- 브라우저: 오버플로(`scrollW/H ≤ client`)·콘솔0·본문22px. **로컬 http 서버 필수**(패널은 `file://` 차단). 스크린샷은 느리고 불안정 → 측정 우선.

## 멀티에이전트 (Codex 협업 도구)
- 40장 이상의 덱처럼 독립 구간이 큰 빌드는 병렬 서브에이전트를 사용한다. 메인이 먼저 전역 결정표를 확정하고 각 빌더에는 담당 원문과 결정행만 전달한다.
- 웹 리서치 담당은 검색 결과에서 원문 출처를 확인한다. 검증 담당은 읽기 전용으로 정적 규칙·오버플로·콘솔 오류를 보고하고 산출물을 직접 고치지 않는다. 파이프라인은 `build → integrate → verify`다.
- 마지막 통합, 구도 연속성, 파트 수, 회귀 검증은 메인 에이전트가 책임진다. 협업 도구가 없거나 작업이 작으면 같은 절차를 단일 에이전트가 순차 실행한다.

## 파일 지도
- **입력 형식(공식)**: `입력양식/콘텐츠초안템플릿.md` + 상세 절차 `references/콘텐츠초안-입력형식.md`. (실례: `sessions/1주차/초안.md`. 주차별 입력·산출은 `sessions/N주차/` — 규약 `sessions/README.md`.)
- 판단축·규격·토큰: `kit/guide/`. 카탈로그: `kit/layouts/`(캐노니컬 50, 물리 54 — `variant_of` 4개 접힘)·`kit/charts/`(23) + 각 `by-shape.md`. 구도 반복은 패밀리와 별개인 `composition_shape` 축으로도 확인한다.
- 코드 코어: `kit/styles/patterns.css`(검증된 CSS) · `데모_제작규칙.html`(마크업 예시). 범용 컴포넌트(`.callout`·`.pill`·`.hint-reveal` 등)는 `kit/styles/deck.css`.
- 스타터: `kit/starter/deck-template.html`(deck.css→legibility→patterns.css 순 로드) · `kit/starter/presenter-notes-template.html`(발표자 노트, 자립 문서).
- **탐색 아카이브**: `_dev/설계기록/탐색-아카이브/` — 표지·아젠다·파트전환·색시스템·마무리 초안 HTML 전부. 배포 대상(①층) 아님, 참고용.

## 1주차 강의덱 — 첫 실전 조립 (2026-07-15)
초안 73행(`sessions/1주차/초안.md` — 이후 `입력양식/`에서 세션 폴더로 이관, 규약 `sessions/README.md`)을 메인(Opus)+교시별 Sonnet 빌더 7 병렬로 조립. 산출: 루트 `1주차_강의덱.html`(73장, 외부 kit CSS 링크)·`_발표자노트.html`. **2·3주차 재사용 패턴:**
- **구조 매핑**: 도입부=파트 밖 인트로(표지·s02·아젠다=여정노드·본문). **간지 슬라이드=파트전환**(pd-title 12자 축약, 간지 원문=pd-sub). "(마무리)"행=concept-recap. **교시=PART**(사용자 확인).
- **병렬 빌드 열쇠**: 메인이 조립 전 **전역 결정표**(#·정보모양·시그니처·element·힌트)로 다양성을 덱 전체 확정(청크경계 넘어 maxrun≤2). 빌더엔 공유 `builder-spec.md`(반환형식·헤더 규칙·SIG별 마크업·토큰·아이콘·오버플로 산식)+교시별 결정행·원문. "결정표대로만". PART본문=`.s-team` 포함(JS가 PART배지 주입), 도입본문(0-x)=s-team 생략.
- ⚠️ **family_signature `<svg` 오검**: 헤더 로고 SVG 때문에 시그니처가 전 본문에 "viz" 균일 추가 → maxrun 판정엔 무영향. 다양성 WARN(`distinct≥content//2`)은 60+장 덱 상시·무시 가능, **실제 FAIL은 maxrun≤2뿐**.
- **오버플로 교훈**: 6줄 `eval-steps`는 기본 사이징 +49px 초과 → `.eval-steps.compact6`(gap 8·pad 8/16·n 40·b 20). 긴 힌트는 `.plain-lines.compact .plain-line.one-line`(라벨+값 flex 한 줄).
- **재사용 규칙**: ❌/✅→모노 `✕`(callout.red)·`✓`(callout.green/`.hl-mint-text`)+색문법(PDF 안전). 🗣→hint-reveal(원문).

## HIGH 빈칸 6종 확충 — 코드 구현 완료 (2026-07-15)
- element: `E-code`(주석 코드 블록)·`D-gantt`(비례 시간축). `E-code`는 concept이면서 대상이 소스코드일 때 element 역인덱스를 확인해야 발견된다.
- layout: `L-td-glossary`·`L-td-claim-rationale`·`L-vf-case-acts`·`L-gm-pitfalls`. `patterns.css`와 카탈로그에 구현되어 있다.
- 중복 4개는 `variant_of`로 비파괴 접어 캐노니컬 균형을 유지한다.
- 절대배치 자손만 있는 다이어그램은 shrink-to-fit 부모 안에서 폭이 0으로 붕괴할 수 있으므로 `.viz-gantt`처럼 명시적 폭과 중앙 정렬을 둔다.

## git 도입 (2026-07-16)
저장소를 git으로 초기화(브랜치 `main`, 초기 커밋 = 전체 스냅샷). **의미 있는 변경은 verify 통과 후 커밋해 복구 지점을 만든다.** `.omc/` 런타임 상태는 `.gitignore`로 제외(`.omc/skills/`만 커밋 예외). 이전의 "커밋 이력 없음 → 삭제 대신 이동" 전제는 해소됐으나, 설계 탐색 산출물의 `탐색-아카이브/` 이동 관례는 탐색 이력 가독성을 위해 유지.

## 새세션-시작.md 아카이브 (2026-07-16)
`_dev/설계기록/새세션-시작.md`는 3세션 릴레이 빌드(`세션프롬프트_3세션.md`)의 인수인계용 문서였고, 릴레이 종료 후 갱신 주체가 없어 스테일해짐("첫 실전 덱 미조립"·"SKILL.md 8단계" 등 실제와 불일치) → `_dev/설계기록/탐색-아카이브/`로 이동. **현재 상태·다음 할 일 정본은 이 파일의 `## 미해결` 하나다**(AGENTS.md 필수 읽기·상태 위치 참조도 같이 갱신됨). ⚠️ 상태를 복제하는 문서를 새로 만들지 말 것 — 갱신 주체 없는 복제본은 반드시 썩는다.

## 팀 워크플로 스킬 3종 도입 (2026-07-17)
- **⑤층 신설**: `skills/{리서치,콘텐츠,검토}/SKILL.md` 정본 + 양 플랫폼 얇은 어댑터 + Codex `agents/openai.yaml`. 팀 역할(해서·혜린·준형)의 스킬화. 등재·계약·**"명시 호출" 3항 정의** 정본 = `skills/README.md`. 명시 호출 전용(보통명사 "검토해줘"는 비발동) — 기계 강제가 아닌 honor-system(오케스트레이터 체이닝 보존 트레이드오프, skills/README에 기록).
- **산출물 스키마는 발명 금지 — 인수인계서 `#7 제출 형식` 세습**: 리서치=3파일(교시별 8항목/실습별 13항목/결정 6열표, `sessions/N주차/자료/`), 콘텐츠=`초안.md`(콘텐츠초안템플릿 4열 표)+집필노트, 검토=`검토보고_YYYY-MM-DD.md`(`sessions/N주차/` 직하, 읽기 전용·발견 3요소·종합판정 기준표).
- **verify_skill_setup.py TEAM_SKILLS 범용 루프**(추가 전용): 정본-어댑터 frontmatter 문자열 일치·어댑터 규칙 복제 금지(body_markers 부재)를 기계 강제. ⚠️ 어댑터 본문에 마커 리터럴("deep-research"·"읽기 전용" 등)을 쓰면 FAIL — 의미는 우회 표현으로 전달.
- **eval**: `evals/team-skills-eval.json`(routing 8 + contract 6, 수동 채점 절차 note에 명기). worktree 계약 테스트 6/6 PASS(2026-07-17). ⚠️ **worktree 테스트는 커밋된 파일만 상속** — 미커밋 신규 스킬은 worktree에 없다(테스트 전 코어 커밋 필수. 전례: 1차 배치 전원 BLOCKED → 코어 커밋 33434a7 후 재실행).
- **검토 스킬 실전 성과(도입 당일)**: 1주차 덱에서 정적 verify가 못 잡는 소유권 위반 검출 → 수정 완료(간지 부제 재작성 2곳 원문 복원, 4-3 멘트 노출→주석+발표자노트, 1-8 본문 원문 복원, 2-7 멘트 의역 콜아웃 제거). 인수인계서 §6 결정 9건이 무기록 확정된 파이프라인 단절 발견 → `1주차_결정요청사항.md` 소급 생성(총괄 확인 대기).
- 테스트발 개선 3건 반영: 리서치 게이트A 범위표 형식·상세안 없는 주차 역산-제안 규칙 / 콘텐츠 폴더 생성은 게이트A 통과 후 / 검토 종합판정 기준표(통과=FAIL 0·조건부=국소 FAIL·재작업=구조 계약 위반).

## 장식 목적 이미지 허용 (2026-07-17)
- 이미지 게이트(`references/이미지-디렉션-프롬프트.md` §3) 완화: 설명력 증대 외에 **장식 목적**(시각적 리듬·생동감)도 `IMAGE_REQUIRED` 사유로 인정.
- 제약(숫자 상한 없이 재량+가이드 문구로 통제): 표지(`cover-object`) 제외, 적용 역할은 `section-overlay`·`support`·`spot`만, 같은 덱에서 드물게·비연속, 이미 차트가 있는 슬라이드엔 추가 금지.
- `generate_now`/`prompt_only` 확인 질문(§5)은 변경 없음 — 장식 목적이어도 매번 그대로 받는다. 코드 시각화 우선 원칙(AGENTS.md 30행)도 불변, 기본값은 여전히 `NO_IMAGE`.

## 이미지 에셋 파이프라인 v1 (2026-07-17, 커밋 f819bf6) — 계약·검증 정본
- **판정 4상태**: `NO_IMAGE | IMAGE_EXPLANATORY | IMAGE_MNEMONIC | IMAGE_DECORATIVE_OPTIONAL`. 순서=정보모양·코드 element 결정 → 목적 판정 → 중앙 레지스트리 `approved` 재사용 검색 → 신규 generate/transform 수 산출 → IMAGE_MODE 확인(신규 0장이면 질문 생략). 설명·기억 판정엔 의미 브리프 6키(LEARNING_POINT/SOURCE_METAPHOR/METAPHOR_MAPPING/MUST_SHOW/MUST_NOT_IMPLY/ALT_TEXT)+구성요소 3~5개·핵심관계 1개 필수.
- **프롬프트 2경로 배타**: built-in 크로마 원본=균일 마젠타 `#FF00FF`만(native-alpha 문구 금지), 승인 native-alpha=진짜 투명만(magenta/chroma 문구 금지). `evals/verify_image_contract.py`가 `이미지-디렉션-프롬프트.md` §5.1/§5.2 text 블록으로 기계 강제. `verify_skill_setup.py` 프롬프트 마커도 이 6키+3상태+출력계약으로 갱신.
- **정본 2층**: 중앙 승인=`kit/images/paper-cut-v1/registry.json`(+`registry.schema.json`), 세션 실행=`sessions/N주차/자료/이미지-에셋.json`(+`references/이미지-에셋-manifest.schema.json`). `_template/자료/`에 빈-슬라이드 manifest+프롬프트 문서 시드. `designboard.png`=candidate·`generation_reference_allowed=false`(계약 일치 새 보드+`--paper` 합성 미리보기 승인 전까지 생성 참조 금지).
- **HTML 계약**: `<figure class="asset-slot asset-slot--{hero|support|spot}" data-image-purpose=…>`. 활성 역할 3종만. 설명/기억=관계설명 한국어 `alt` 필수, 장식=`alt="" aria-hidden="true"`. prompt_only=`<img>` 없이 `data-image-state="expected" data-expected-src`만 → 개발덱 깨진 이미지 0, 배포(release/inline)는 unresolved 설명·기억 슬롯이면 FAIL. 표지 고정(큐브 9면 유지)·`cover-object`/`section-overlay` 미승인. 장식=파트당 ≤1·비연속·차트/다이어그램 슬라이드와 동시 금지.
- **스크립트(Pillow 필요)**: `prepare_image_asset.py`(크로마 프리플라이트=균일 경계·키 충돌 거부, 경계연결 flood-fill 키잉, 부분알파 RGB 최근접 복구, 알파 타이트크롭 ≤10% 여백) · `verify_image_assets.py`(PNG/RGBA/투명 네모서리/여백/마젠타 프린지 + 레지스트리 계약 + manifest 참조). `verify_deck.py`에 `image_contract_checks`·`count_code_viz` 추가(회귀 없음 — 1주차 이미지 계약 11 PASS). `inline_deck.py`=asset-slot/`<picture>`/srcset/CSS `url()` 인라인 + 오프라인 외부의존 차단.
- **검증 커맨드**: `python -m unittest tests.test_image_pipeline`(14 PASS) · `python evals/verify_image_contract.py`(프롬프트층·레지스트리·manifest 템플릿) · `python scripts/verify_image_assets.py --registry kit/images/paper-cut-v1/registry.json`. `evals/image-contract-eval.json`=수동 채점 9케이스(routing/contract). ⚠️ `verify_image_contract.py`는 아직 독립 실행 — 통합 러너 미연결.

## 미해결 (상태·TODO 정본)
- ✅ **이미지 에셋 파이프라인 v1 커밋 완료**(2026-07-17, f819bf6) — 전용 섹션 참조. 후속: (a) 레지스트리 `assets` 비어 있음(실전 덱 생성 때 채워짐, 블로커 아님) (b) `designboard.png` candidate→계약 일치 새 보드+`--paper` 미리보기 승인 필요 (c) `evals/verify_image_contract.py` 통합 러너 미연결. ⚠️ 미커밋 상태로 방치돼 있던 WIP였음 — 이후 큰 WIP는 verify 통과 즉시 복구지점 커밋(미해결에도 기록).
- ✅ **로고 확정**(2026-07-13) → V-마크(민트 왼팔·블루 오른팔·잉크 접점) 인라인 `<svg class="s-logo">`. 사이징=`deck.css .s-logo`(40)/`.cover-head .s-logo`(60). 표준자산 `kit/starter/logo.svg`. 전 파일 스윕 완료(2026-07-14).
- 항목별 `catalog.html`(목표 캐노니컬 50+element 23=73 `<section>`) 미완 — 현재 layouts 14·charts 9(≈32%). patterns.css 시드 + 1주차 실전 덱(verify 통과 73장)의 섹션 역수확으로 확장.
- 차트 스펙 잔여 대비 팔로업 — 밝은 램프 위 텍스트(피라미드처럼).
- (WSL/맥) description 자동최적화(`run_loop.py`).
- **1주차 결정요청 9건 총괄 확인 대기** — `sessions/1주차/자료/1주차_결정요청사항.md`(소급 기록). 승인/수정 지시 후 해당 행에 결정일 추기.
- 1-4 대비 패널 라벨("골라주기/새로 만들어주기" — 멘트 유래 텍스트의 시각화 사용) 경계 사례 — 시각화 재량 vs 라우팅 엄격 적용, 총괄 판단 필요.
- 초안.md 서두 "약 60장" vs 실제 73행 불일치 + `(선택)` 태그 0건(검토보고 W3, 담당 콘텐츠).
- **아틀라스 생성기 리빌드 불가(2026-07-17 발견)** — `outputs/build_layout_atlas.mjs`의 개수 어서션(50 layouts/21 elements)이 현재 카탈로그(물리 54/22)와 불일치해 `node` 실행이 즉시 실패. 생성기를 variant_of 접힘 반영으로 갱신하거나 어서션을 조정해야 함. 그 전까지 프로즌 CSS 재동기화는 splice 스크립트(deck.css 헤더~`/* layout atlas additions */` 구간 통짜 교체+어서션)로 수행.
