# 강의덱.초안 — 바이브코딩 온라인 원데이 · 오후 편집본 조각(fragments)

대화하며 수정하는 작업본이다. 파트별 조각으로 나눠 국소 편집하고, 조립기가 통합 미리보기 `강의덱.html`을 만든다.

## 이 덱의 기반 (G1 Q1·Q2 · 2026-09-15 W0)

- `shell.html`·`revision.css`는 **AC2** `courses/AI_코딩_에이전트_입문_3차시/sessions/2주차/강의덱.초안/`에서 가져왔다. `revision.css`는 원본과 바이트 동일(3797행)로 시작했다. 템플릿 잔존 파일(고정 장 X·M1·S01·S02·S03·END · part-01 P1·M1)은 교체했다.
- 고정 장은 3장이다: `B0-01`(cover) · `B0-02`(w2-week) · `B0-03`(s03-slide). 마무리 `B7-15` THANK YOU는 `part-07.html` 끝에 있다(계약 `closing_text`).
- ⚠️ **로드 순서가 오전 덱과 반대다.** 이 셸은 `<style id="kit-additions">` 다음에 `revision.css`를 로드한다(오전 덱은 `revision.css` 다음 kit-additions). 오전 조각의 CSS를 옮길 때 같은 명시도 규칙의 승패가 뒤집힐 수 있다.
- 조각 담당: `part-01`·`part-02` W1 · `part-03`·`part-05` W2 · `part-04` W3 · `part-06`·`part-07` W4. `shell.html` 고정 장은 W1.
- **`revision.css`는 메인 단일 라이터다.** 웨이브는 전용 CSS를 저장소 `tmp/vco-2주차/wave-N.css`로 내고 메인이 «오후 이식» 구획으로 병합한다. part 파일 안에 `<style>`을 두지 않는다.
- 웨이브 공통 인계와 신규 구도 결정: `tmp/vco-2주차/W0-기록.md`. 조각 대응 정본: `../조립_보고.md` §2.

## 파일 규약

- `shell.html` — head·CSS 링크·발표 엔진 JS와 고정 슬라이드, 그리고 파트가 들어갈 자리 `<!-- ::PARTS:: -->` 마커 한 개. 파트를 여기에 직접 넣지 않는다.
  - ⚠️ `<style id="kit-additions">` 안의 **「기본 경화 5종」 블록을 지우지 마라.** ① 본문 22px 하한 회복 ② 박스 제목 26/800 · 설명 20/500 위계 ③ 카드 간 여백 18px ④ 빈 이미지 슬롯 표시 억제 ⑤ 교시 로드맵(`.roadmap`) 골격. 값의 정본은 `kit/guide/토큰-치트시트.md`(R-TYPE-01·03)다. (AC2 셸에 템플릿과 같은 내용으로 들어 있어 따로 병합하지 않았다.)
  - 이 덱이 **새 박스 구도**를 만들면 그 제목·설명 셀렉터를 ②의 목록에 **추가**해야 위계가 적용된다.
  - **`../deck.contract.json`의 `layout_families`에 등재할 것**: 이 덱이 새로 만든 구도 클래스 전부. 미등재 구도는 `full`로 뭉개져 「동일 구도 연속」 FAIL 오탐이 난다.
- `part-01.html` … `part-07.html` — 파트별 섹션 조각(`part-divider` + 본문 `<section class="slide">`). head/body/html 없이 섹션만. 간지 `data-slide`는 `P1`~`P7`(초안 `B1-01`~`B7-01`)이다.
- `order.txt`(선택) — 병합 순서. 없으면 파일명 오름차순.
- 조립: `python scripts/assemble_deck.py courses/바이브코딩_온라인/sessions/2주차/강의덱.초안` → 상위 폴더에 `강의덱.html` 생성. `--watch`는 저장 시 자동 재조립, `--watch --livereload`는 미리보기 자동 새로고침.
- CSS 경로 `../../../../kit/styles/…`는 **출력 위치 `courses/바이브코딩_온라인/sessions/2주차/강의덱.html` 기준 4단계**이고, `강의덱.초안/revision.css`도 같은 출력 위치 기준이다.
  - ⚠️ **경로가 틀려도 정적 검증은 전부 PASS한다.** CSS 404는 브라우저에서만 드러난다(전 슬라이드 동시 표시·로고 0×0). 조립 후 로컬 http로 열어 `document.styleSheets.length`와 «보이는 슬라이드가 1장인지»를 확인한다.
  - ⚠️ CSS를 기계 편집하면 브라우저 `document.styleSheets[i].cssRules.length`를 전후 대조한다(오전 덱 `:is(…)` 절단 사고 — verify_deck은 FAIL 0으로 통과했다).
