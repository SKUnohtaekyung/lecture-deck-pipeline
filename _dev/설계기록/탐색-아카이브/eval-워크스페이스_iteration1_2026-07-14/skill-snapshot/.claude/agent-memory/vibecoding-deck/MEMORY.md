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
3. **토큰만**: `:root` 밖 raw `#hex` 금지. 흰색은 **`var(--white)`**(`#fff` 아님). 구조·주 강조로 보이는 블루 요소는 **`--blue`만** 사용하고 `--blue-soft`는 배경, `--periwinkle`는 비강조 데이터에만 쓴다. 민트는 행동·성공·안전과 일반 강조에 쓴다. **민트·코랄 fill 위엔 흰 글자 금지** → `--on-mint`/`--on-coral` 짙은 글자. 단, `.hl-mint-mark`은 글자폭만 감싸는 흰 글자 예외다.
4. **no-default 검사**: 리터럴 `기본` grep은 오탐(CSS 기본 스타일). "레이아웃을 기본/최다로 규정하는 **문장**" 의미 검사로.

## 색 시스템 v2 (적용됨 — 2026-07-13)
이전 코발트 파생 시스템을 **전면 개명**해 교체(사용자 결정: `_dev/설계기록/탐색-아카이브/디자인시스템_선택안.html` A1–G1, 근거 `ui-ux-pro-max` 스킬). 전체 명세: `_dev/설계기록/색시스템-v2-명세.md`.
- **브랜드 3색**: `--blue #1D4ED8`(구조) · `--mint #14B8A6`(행동·성공·안전, fill) · `--coral #F97360`(주의·경고, fill) · `--red #DC2626`(오류). 텍스트/보더는 `--mint-deep #0F766E`·`--coral-deep #C2452F`.
- **개명 맵**: `--cobalt`→`--blue` · `--green`→`--mint-deep`(`-soft`→`--mint-soft`) · `--orange`→`--coral-deep`(`-soft`→`--coral-soft`) · `--yellow-*` 폐지. `navy/periwinkle/ice/electric/th/blue-soft/red`는 **이름 유지·값만** 변경(navy #16277A·peri #93A7E8·ice #A9C6FF·electric #6BA5FF·cover-bg #101E52).
  - ⚠️ **navy는 사용 금지**(정의만 남김, `var(--navy)` 0; 어두운 배경/텍스트는 `--ink`). 차트 비강조 램프도 `periwinkle→surface`(navy 없음).
- **전면 개명(별칭 없음)**: 렌더 코드는 옛 토큰(`--cobalt`·`--green`·`--orange`·`--yellow-*`) 사용처 0 — 명세의 별칭 블록은 역사적 기록. 조립은 새 토큰만.
- **섀도우**: 코발트 틴트 `rgba(48,96,195)` → 블루 `rgba(29,78,216)` 전량. 신규 `--shadow-sm/md/lg/blue`.
- **신규 토큰**: 라운드 `--r-lg20/md14/sm10/pill` · 코드폰트 `--font-mono`(JetBrains Mono).
- 차트는 모노강조 계승(강조 `--blue` 1곳 + `--periwinkle` 램프, 무지개 금지).

### v2.1 템플릿 (적용됨 — 조립 시 준수)
- **발표 UI 재질**: 하단 기본 바는 `--glass-white` 고투명 Liquid Glass, 상세 메뉴는 `--glass-thick rgba(232,235,240,.76)` 옅은 쿨그레이 반투명 유리. 상세 메뉴를 완전 투명 또는 순백 불투명 패널로 만들지 않는다.
- ⚠️ **번호배지 분리**(가장 흔한 오적용): 민트 fill 배지는 `.num-circle`·`.work-step .n`·`.pd-dot.is-active` **셋만**. 다이어그램/플로우 노드(`.cyc-node .cn`·`.vt-root`·`.rad-hub`·`.rad-sat .tag`·`.flow-step .n`·`.rev-no`·`.quad-card .qn`·`.lc-n`)와 `.timing`은 **블루 유지**(블루=구조). "번호=민트" 일괄 금지.
- **eyebrow = 태그**: `.s-eyebrow`는 `--blue-soft` 배경 pill(본문 슬라이드만; 고정 슬라이드는 plain). 상단 `.s-line`은 `--blue`.
- **accent-bar = 슬림 64×5px**.
- **work-step 조임**: padding 11px / gap 10px.
- **헤더 파트진행**: 본문 슬라이드 우측 = `PART n/N` + 진행 도트(현재 파트=민트), JS가 `.s-part` 주입(divider 기준 자동). 고정 슬라이드(표지·도입·아젠다·마무리)는 팀명 유지.
- **하단 페이지네이션**: `n/전체`, JS가 `.s-pageno` 주입, 표지·마무리 제외.
- **그라데이션 금지**(cover 포함) · **민트·코랄 fill 위 흰 글자 금지**(`--on-mint`/`--on-coral`). 단, `.hl-mint-mark`은 글자폭만 감싸는 흰 글자 예외다.
- **폼 토큰**: `--r-lg20/md14/sm10/pill999` · `--shadow-sm/md/lg/blue`(카드=r-lg+soft shadow) · 코드폰트 `--font-mono`(JetBrains Mono).

### 표지 v4 — 라이트 지오메트리 (최종 · 2026-07-13 · F1 다크네이비 대체)
사용자 반복 결정으로 최종 확정. 진화: F1 다크네이비 폐기 → M3(흰·모노프롬프트) → **최종 = 브랜드-화이트 + 아이소메트릭 도형**. 탐색 히스토리(전부 `_dev/설계기록/탐색-아카이브/`로 이동, 2026-07-14): `표지_초안_20종.html` → `표지_병합_16x02_무드.html`(M3) → `표지_수정_도형_3안.html` → `표지_지오메트리_10안.html` → `표지_지오메트리_G1G8G9_10안.html`(I2 채택) → `표지_1주차_최종.html`.
- **배경 = 브랜드-화이트 `--paper #F4F8FB`**(순백 아님, 블루 언더톤+민트 조화) + **블루 도트그리드**(SVG `<circle>` fill, 그라데 아님). ⚠️ `--paper` 값이 옛 `#FAFAF7`(warm)→`#F4F8FB`(cool)로 **바뀜**.
- **모노 폰트 전면 제거**(사용자 지시 "그 폰트 사용 금지" — 한글이 모노폭에 물려 어색). 전부 **Pretendard**. `>_`만 기호로 유지. **결과물 문구도 제거**(사용자 지시).
- **도형 = 아이소메트릭 3단 큐브 스택**(빌드업 은유) + **최상단 큐브 위 코랄 점 스파크**. `<svg class="cover-geo">`에는 `data-cube` 3개와 polygon 9개가 있어야 한다. **fill=`var(--토큰)`**(raw hex 금지 — verify 통과 필수). 큐브면=blue-soft(top)/blue(left)/mint(right).
- 슬롯: `.cover-geo`(SVG 도형) · `.cover-lead`(상단 키커, Pretendard, **`>_` 없음**) · `.cover-title .ko`(강조어 `.hl`=초록/`--mint-deep`, **캐럿 없음**) · **`.cover-terminal`**(M2 터미널 박스: `--surface` 배경+`--line` 보더+`--r-md`, `>_`(mint-deep)+**주차 핵심을 AI에 한 문장 요청**+`.cur` 민트 깜빡 캐럿, Pretendard) · `.cover-presenter`. **캐럿=제목→터미널 박스로 이동**(사용자 지시). **삭제됨**: `.cover-meta`·`.cover-prompt`·`.cover-outcome`·`.cover-tick`·제목 `.cur`.
- `deck.css` §11 + 스타터 표지 마크업 교체. **verify FAIL 0·WARN 0·PASS 21**(cover SVG=코드시각화라 이미지>코드 WARN도 해소) + 브라우저(브랜드-화이트 244,248,251·제목 ink 92px·`>_` mint-deep·민트 캐럿·코랄 점 cy256·오버플로0·모노0).
- **전체 이미지 무드 = "클린 라이트 + 지오메트리 액센트"**: 브랜드-화이트 베이스 + 블루(메인)/민트(서브) 도형 + 코랄은 작은 점 하나만. 반복 모티프(`>_` 리드·아이소/링/벤토 기하·민트 캐럿). 이미지=브라우저 크롬 프레임(라이트·플랫·여백, 3D 사진·헤비그라데·무지개 금지).
- 후보 도형언어(재사용): **벤토(G1)·오프셋 링/벤(G8, 개선안=민트-소프트 렌즈)·아이소(G9)**. 파트구분·본문 확장 시 이 기하 어휘를 축소·재배치.
- `--cover-bg #101E52`·`.closing`(다크)은 옵션 대안으로만 잔존(기본 마무리=라이트 `concept-recap`). navy 사용 0.
- ⚠️ **폰트 원칙**: 덱 외부 의존성=Pretendard만(모노 CDN 미로드).

### 아젠다·파트전환 v2 — 지오메트리 확장 (최종 · 2026-07-14 · 표지 도형언어 상속)
사용자가 "발표자·팀명 없애고 도형 언어를 파트로 확장" 지시 → ui-ux-pro-max 근거로 아젠다 10안·파트전환(디바이더) 10+30안(화이트/블루/초록 배경 확장 포함, 세션한도로 일부 미완) 생성 → **아젠다=`ag_node`(노드-타임라인)·파트전환=`dv_iso`(아이소 큐브 클러스터)** 확정, 둘 다 흰(`--paper`) 배경판 그대로 채택(블루·초록 배경 실험은 미채택 — 참고용 `슬라이드_파트전환_컬러확장_30종.html`으로만 잔존).
- **아젠다(`.s03-slide`)**: 헤더 = 로고+브랜드+`.s-line`만, **팀명(`.s-team`) 제거**(라인이 `flex:1`로 자동 확장). 본문 = 좌 `.an-left`(제목 `.an-title` + 3줄 인트로 `.an-intro`, 강조어 `.hl`=`--mint-deep`) + 우 `.an-right`(세로 트랙 `.an-track` + 4개 `.an-item.i1~i4`, 각 `.an-num`(48px 원, **블루 fill+흰 글자** — 구조 노드 규칙, 민트 아님) + `.an-body`(`.an-h`+`.an-d`)) + 장식 점 `.an-spark`(코랄, 제목 위 고정 위치). 구 `.s03-list`/`.agenda-item`/`.s-body-wrap` 조합은 폐기(§6의 `.num-circle`/`.agenda-item` 정의 자체는 다른 커스텀 슬라이드용으로 유지).
- **파트전환(`.part-divider`)**: **헤더 전체 제거**(로고·브랜드·팀명·발표자 전부 미노출 — 풀캔버스 중앙 히어로). 배경 그래픽 `.dv-hero`(SVG, position:absolute inset:0 z-index:0) = 표지 `.cover-geo`와 **동일 토큰의 아이소메트릭 큐브 3개**(9면, blue-soft/blue/mint) + 코랄 스파크. 그 아래 중앙정렬로 `.pd-dots`(top:410) → `.pd-eyebrow`("PART n/N", top:452) → `.pd-title`(96px·**nowrap**·top:490, ⚠️ 12자 이내 권장 — 1152px÷96px) → `.pd-sub`(24px·width:920·top:628, 강조어 `.hl`=`--mint-deep`).
  - ⚠️ **`.pd-dot`/`.pd-dot.is-active` 셀렉터명은 절대 변경 금지** — `verify_deck.py`가 `.pd-dot.is-active{background:var(--mint)}`를 **최상위(비중첩) 셀렉터**로 정규식 검사(민트 배지 3종 중 하나, §6 `css_block()` 참조). 시각은 텍스트 없는 작은 원(10px/활성 12px)으로 단순화(숫자 라벨 제거) — `font-size:0;color:transparent`로 잔여 텍스트도 방어.
- **verify FAIL 0 관련**(단, `--glass-white`/`backdrop-filter` 인라인 체크는 스타터가 CSS를 외부 링크하므로 **기존부터 별개로 FAIL** — 이번 변경과 무관, 스타터의 의도된 구조) · **PASS 26**(민트 배지 3종 포함) + 브라우저 측정(양쪽 슬라이드 오버플로 0·팀명 없음 확인·아젠다 배지 블루 fill·디바이더 도트 민트 fill·큐브 9면·코랄 스파크·모노 0·페이지번호와 겹침 없음, `#slide=N` 해시 대신 `nextBtn.click()`으로 슬라이드 전환해야 실측 가능 — 해시만 바꾸면 엔진이 재계산 안 함).
- 탐색 히스토리(참고용, 미채택 잔존, `_dev/설계기록/탐색-아카이브/`로 이동, 2026-07-14): `슬라이드_아젠다_초안10.html`·`슬라이드_파트전환_초안10.html`(1차 20안 — ag_node/dv_iso 원안 포함) → `슬라이드_파트전환_컬러확장_30종.html`(2차 30안, 화이트/블루/초록 배경 확장 — 세션한도로 8건 미완, 결국 1차 원안 흰 배경판 채택으로 미사용). ⚠️ 2차 30안 파일은 **디스크에 실물이 없음**(생성 스크립트가 "wrote" 로그만 남기고 파일이 남지 않음 — 재확인/재생성 필요시 참고).
- ⚠️ **전역 CSS 공유 주의**: `deck.css`를 외부 링크하는 다른 실제 덱은 이 변경의 영향을 받는다. `데모_제작규칙.html`(SKILL.md "5단계 마크업 본뜨기" 참조 파일, 실 4파트 덱)이 옛 `.pd-wrap`/`.s03-list`/`.agenda-item`/팀명 헤더를 쓰고 있어 **함께 동기화**(S03 1개+P1~P4 4개, 실 콘텐츠 보존) — verify(`--parts 4`) PASS 25(민트배지3종·part-divider4=파트4 포함) + 브라우저(5개 슬라이드 전부 오버플로0). `outputs/vibecoding-deck-layout-atlas.html`은 CSS를 자체 인라인하는 독립 스냅샷이라 **당시엔 영향 없음(구버전 잔존)**이라 적었으나, 바로 다음 세션에서 이 파일이 "최종안"으로 지정되며 실제로 동기화됨 — 아래 "프로즌 CSS 복사본 드리프트" 항목 참조. `PPT_레이아웃_템플릿_스킬_가이드.html`은 이후 미사용 판정으로 `_dev/설계기록/탐색-아카이브/`로 이동됨.
  - 이 verify 패스에서 **무관한 사전 FAIL 3건 발견**(내가 만든 게 아님, 손대지 않음): 이 데모의 표지가 v4 이전 구버전(큐브 0)·상세 발표 메뉴 없음(구형 미니 네비만)·글래스 토큰 없음 — 표지 v4·글래스 네비 롤아웃 때 이 파일이 누락된 것으로 보임. 새 작업으로 분리 필요.

### ⚠️ 프로즌 CSS 복사본 드리프트 (발견 2026-07-14 · `outputs/vibecoding-deck-layout-atlas.html`)
`outputs/vibecoding-deck-layout-atlas.html`(50레이아웃+21element 전체를 훑어보는 101슬라이드 참조덱, 자체 `<style>`에 deck.css를 **통째로 얼려 복사**해둠 — 외부 링크 아님)가 사용자에 의해 "지금 결정된 최종안"으로 지정됨. 아젠다·파트전환 마크업 업데이트 + **치명적 렌더링 버그** 신고("전체 슬라이드가 깨짐") 두 가지를 함께 처리:
1. **렌더링 버그(모든 슬라이드 영향)**: 파일 끝 "layout atlas additions" 블록에 `@media screen{.deck .slide{transform:scale(var(--scale,1)) translate(-50%,-50%)!important}}`가 있었음 — 원본(§2)의 올바른 순서 `translate(-50%,-50%) scale(...)`를 **반전**시킨 `!important` 중복 패치. transform 함수 순서가 뒤바뀌면 스케일이 1보다 클 때(=1280×720보다 큰 모니터 전부) 슬라이드가 좌상단으로 밀림 — 오프셋 계산식은 정확히 `(뷰포트/2)×(1-scale)`이라 화면이 클수록 더 심하게 깨짐(1920×1080 실측: 정확히 -320px/-180px 밀림, 계산과 100% 일치). **고침**: 이 중복 패치 전체 삭제(원본 §2 규칙만으로 이미 충분·정상 동작, display:none/block 부분도 원본과 중복이라 같이 제거).
2. **아젠다·파트전환 마크업 미반영**: 이 파일의 s03-slide 1개(제목·인트로·4항목 실 콘텐츠)와 part-divider 17개(각기 다른 PART라벨·제목·부제, 진행도트 최대 17개)를 정규식 기반 파이썬 스크립트로 새 `an-*`/`dv-hero`+`pd-*` 구조로 일괄 치환(실 콘텐츠 보존).
3. **⚠️ 진짜 근본 원인은 따로 있었다**: 마크업만 바꾸고 나니 아젠다는 멀쩡했지만 파트전환 17개 전부가 요소들이 아래로 쌓여 밀리는 2차 버그 발생 — 원인은 이 파일의 **얼린 CSS가 §13·§14 신 규칙(`position:absolute` 좌표 기반) 이전 버전**이었기 때문(`.dv-hero` 셀렉터 자체가 존재하지 않았고, `.pd-dots`/`.pd-eyebrow`/`.pd-title`/`.pd-sub`가 구버전 flex-column `.pd-wrap` 자식 방식 그대로 남아있어 새 마크업과 안 맞음). **고침**: 이 파일의 내장 CSS 블록(`/* SKU LIKELION 강의덱 */`부터 `/* layout atlas additions */` 직전까지)을 **현재 `kit/styles/deck.css` 전체로 통짜 교체**해 동기화.
- **교훈**: `deck.css`를 **외부 링크가 아니라 인라인/얼려서 복사**해두는 산출물(이런 "outputs/" 스냅샷들)은 kit 원본이 바뀌어도 자동으로 따라오지 않는다 — 향후 §13/§14류 규칙을 또 바꾸면 이 얼린 파일도 **반드시 함께** kit/styles/deck.css로 재동기화할 것. `데모_제작규칙.html`은 반대로 **외부 링크**라 자동으로 최신 CSS를 받되, 그래서 오히려 마크업 쪽(§13/§14 구조 불일치)이 깨지는 정반대 실패 모드였음(위 항목 참조) — 요컨대 "CSS 얼림"과 "마크업 얼림"은 서로 다른 종류의 드리프트를 유발하니 둘 다 체크해야 한다.
- **검증**: `verify_deck.py --parts 17` FAIL 0·WARN 0·PASS 29. 브라우저: 1920×1080에서 센터링 완전 정확(0,0)~(1920,1080) 확인(버그 전엔 (-320,-180)~(1600,900)이었음) + **전체 101슬라이드 walk 오버플로 0**(아젠다·파트전환 18장뿐 아니라 나머지 레이아웃/element 예시 슬라이드까지 전부) + 콘솔 에러 0 + 모노폰트 0.

### ⚠️ 4번째로 발견된 버그 — `display` 우선순위 충돌 (여러 슬라이드 동시 표시)
사용자가 스크린샷으로 "슬라이드 두 개가 겹쳐 보인다"(예: 19/101과 70/101이 동시에) 신고 → `.is-active`는 확인상 항상 1개뿐인데(`activeCount:1`), 실제 `display!=='none'` 요소는 **12개**였음(`visibleCount:12`). 원인: 이 아틀라스 파일의 예시 슬라이드 `<section class="slide atlas-slide atlas-centered">`처럼, **콘텐츠 레이아웃용 클래스(`.atlas-fb`·`.atlas-centered`·`.atlas-split` 등, `display:grid` 지정) 가 슬라이드 section 자체에도 직접 붙어 있어서**, 같은 특이도(단일 클래스)의 원본 `.slide{display:none}`을 **소스 순서상 나중에 온다는 이유만으로** 이겨버림(일부는 최상단 patch에서 아예 `display:flex!important`로도 있었음). `.is-active` 토글과 무관하게 이 클래스가 붙은 슬라이드는 항상 보임 → 여러 슬라이드가 각자 다른 위치에 겹쳐 보임(사용자가 본 대각선 그림자 = 각 슬라이드의 개별 box-shadow가 겹친 것).
- **고침**: `kit/styles/deck.css` §2의 핵심 토글에 `!important` 추가 — `.slide{...display:none!important;}` / `.slide.is-active{display:block!important;}`. 콘텐츠 클래스가 무엇을 지정하든 항상 이기도록 엔진 불변식을 강화. 아틀라스 파일은 재동기화(§ 위 "프로즌 CSS 드리프트" 스크립트 재실행)로 자동 반영.
- **검증**: 101슬라이드 전체 walk에서 매 스텝 `visibleCount===1` 확인(`badVisCount:0`) + 오버플로 0 + 콘솔 에러 0. `kit/starter`·`데모_제작규칙`도 재검증(기존 FAIL만 유지, 신규 회귀 없음).
- **교훈**: 콘텐츠 레이아웃 클래스(`.atlas-*`, 그리고 앞으로 추가될 비슷한 것들)를 슬라이드 section 자체에 직접 붙이는 패턴은 `display` 충돌 위험이 있다. 근본적으로는 그 클래스들을 section 자체가 아니라 내부 wrapper div에만 붙이는 게 맞지만, 이미 101장에 퍼져 있어 재구조화 대신 엔진 쪽(`!important`)에서 방어했다.

### ⚠️ 5번째로 발견된 버그 — `position`/`top`/`left`/`transform` 우선순위 충돌 (같은 근본 원인의 재발)
4번째 버그를 고친 직후 사용자가 스크린샷으로 "슬라이드 20,21,22,25,26,27,28 등이 화면 절반만 잘려 보인다" 재신고. 측정: `.is-active`는 1개뿐(4번째 버그 재발 아님)인데, 해당 슬라이드들의 **박스 자체 위치**가 어긋나 있었음 — 예상 중앙정렬 `(0,0)~(1920,1080)` 대신 실측 `l:-896, t:-392, w:1920, h:1080`(크기는 정상, 위치만 대각선으로 밀림).
- **원인**: 4번째와 **완전히 같은 근본 패턴**. `.atlas-fb,.atlas-centered,.atlas-top,.atlas-grid,.atlas-diagram,.atlas-vflow,.atlas-compare,.atlas-split{position:absolute;left:64px;right:64px;top:155px;bottom:78px}`(내부 콘텐츠 div용 규칙)가 이번에도 `<section class="slide atlas-slide atlas-centered">`처럼 **슬라이드 section 자체에** 직접 붙어 있어, 원본 `.slide{position:absolute;top:50%;left:50%}`를 소스순서상 나중이라는 이유로 이겨버림. 그 위에 `.slide`의 `transform:translate(-50%,-50%) scale(1.5)`는 그대로 적용되니 `top:155px,left:64px` 기준으로 계산한 최종 위치 `(64-960, 155-540)=(-896,-385)`가 나옴 — 실측(-896,-392)과 사실상 일치(7px 오차는 bottom/height 과잉제약 처리 차이).
- **고침**: `kit/styles/deck.css` §2 `.slide`의 `position`·`top`·`left`·`transform`에도 전부 `!important` 추가(이전엔 `display`만 봉인했었음). 재동기화 스크립트로 아틀라스 파일 반영.
- **재발 방지 확인**: 아틀라스 CSS 전체(`atlas-*`/`photo-slot`/`element-wrap` 등 콘텐츠 클래스 14종)를 정적 스캔해 `.slide`가 쓰는 나머지 속성(`z-index`·`overflow`·`background`·`width`·`height`·`margin`·`padding`)과 겹치는 게 더 있는지 확인 → **0건**(display·position·top·left·transform 4개만 실제 충돌했었고 전부 봉인됨).
- **검증**: 101슬라이드 전체 walk에서 `visibleCount`·박스 크기/중앙정렬·콘텐츠 오버플로 **3중 체크 전부 0건 이탈**(1920×1080, 버그 재현 뷰포트와 동일 조건) + 콘솔 에러 0. `verify_deck.py --parts 17` FAIL 0·WARN 0·PASS 29 유지.
- **교훈 갱신**: "콘텐츠 클래스가 슬라이드 section에 직접 붙어 `.slide`의 속성을 가로챈다"는 같은 원인이 **속성마다 따로** 터졌다(먼저 display, 그다음 position류). `.slide` 규칙이 소유한 모든 지오메트리 속성(`position/top/left/transform/display`)을 한 번에 `!important`로 봉인해 이 클래스 전체의 재발을 막았다 — 하나씩 땜질하지 말고 "엔진이 소유한 속성 집합"을 통째로 방어하는 게 맞다.

## 검증 (측정 우선)
- 정적: `python scripts/verify_deck.py <덱>.html --parts N` — 슬라이드·파트전환=파트수·코드viz vs 이미지·구도 다양성·같은 구도 연속·토큰.
- 브라우저: 오버플로(`scrollW/H ≤ client`)·콘솔0·본문22px. **로컬 http 서버 필수**(브라우저 패널은 `file://` 차단). 스크린샷은 느리고 불안정 → 측정 우선.

## 멀티에이전트 (Workflow 툴)
- 빌드+웹리서치 = `agentType:'general-purpose'`(WebSearch→WebFetch로 소스 확인), 검증 = `agentType:'Explore'`(읽기전용), effort `'high'`. pipeline(build→verify).
- **주의**: `args`는 JSON 값으로 넘겨라(배열을 문자열로 주면 `Array.isArray` 실패 → 파일럿이 전량 실행됨. 실제로 겪음).
- 커스텀 `.claude/agents`는 삭제됨 — 현재는 general-purpose/Explore + 인라인 프롬프트로 돈다.

## 파일 지도
- 판단축·규격·토큰: `kit/guide/`. 카탈로그: `kit/layouts/`(50)·`kit/charts/`(21) + 각 `by-shape.md`.
- 코드 코어: `kit/styles/patterns.css`(검증된 CSS) · `데모_제작규칙.html`(마크업 예시).
- 스타터: `kit/starter/deck-template.html`(deck.css→legibility→patterns.css 순 로드).
- **탐색 아카이브**: `_dev/설계기록/탐색-아카이브/`(2026-07-14 정리) — 표지·아젠다·파트전환·색시스템 초안 HTML 11개 + 이들을 iframe으로 모아 보던 고아 인덱스 `PPT_레이아웃_템플릿_스킬_가이드.html`. 전부 **SKILL.md/README.md/CLAUDE.md 어디서도 참조하지 않는 미채택 탐색본**이라 루트(배포 대상 ①층)에서 개발자료 ②층으로 이동. 인덱스 페이지의 `데모_제작규칙.html`·`kit/*/catalog.html` 참조 경로는 `../../../`로 보정 완료.

## 미해결
- ✅ **로고 확정**(2026-07-13) → V-마크(민트 왼팔 18px·블루 오른팔 19px·잉크 접점 r9.5=팔끝 캡과 일치·수직기준 26°) 인라인 `<svg class="s-logo">`(토큰색)를 헤더에 삽입. 사이징=`deck.css .s-logo`(40)/`.cover-head .s-logo`(60), `flex:0 0 auto` 추가. `.logo-ph` 폐지(patterns.css·스타터). 파비콘=data-URI(hex). 표준자산 `kit/starter/logo.svg`. 스윕 완료(2026-07-14): 데모(14)·layouts/catalog(9)·charts/catalog(7)·표지_1주차_실전/최종(각1)·references 스니펫까지 전부 V-마크 교체(토큰검사 PASS). `logo-ph` 잔존=이 MEMORY·patterns.css 주석(역사적 언급)뿐.
- 항목별 `catalog.html`(붙여쓰는 전 71 `<section>`) 미완 — patterns.css 시드에서 확장.
