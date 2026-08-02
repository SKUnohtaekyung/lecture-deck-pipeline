# 2주차 강의덱.초안 — 조각 구성

정본은 이 폴더의 조각이다. `sessions/2주차/강의덱.html`은 생성물이라 **직접 고치면 다음 조립 때 유실된다.**

| 파일 | 내용 | 장수 |
|---|---|---|
| `shell.html` | head·kit CSS 링크·2주차 신규 구도 CSS(`<style id="kit-additions">`)·발표 엔진 JS + 고정 슬라이드 4장(`S01` 표지 · `S02` 도입 · `S02B` 주차 개요 · `S03` 아젠다) + `<!-- ::PARTS:: -->` 마커 1개 | 4 |
| `part-01.html` | PART 1 · 1교시 (`P1` divider + `M1` + 본편) | 17 |
| `part-02.html` | PART 2 · 2교시 (`P2` + `M2` + 본편) | 17 |
| `part-03.html` | PART 3 · 3교시 (`P3` + `M3` + 본편) | 14 |
| `part-04.html` | PART 4 · 4교시 · **화면과 핵심 기능** (`P4` + `M5` + 본편) | 23 |
| `part-05.html` | PART 5 · 5교시 · **AI 작업 시스템** (`P5` + `M4` + 본편) | 23 |
| `part-06.html` | PART 6 · 6교시 (`P6` + 본편) + **마무리**(`THX`) | 13 |
| `part-07.html` | 비어 있음 — 예비·확장 슬라이드는 전량 본편으로 흡수·삭제됐다(2026-07-31 P4). 조립기는 0장 파일도 정상 병합한다. | 0 |
| `part-08.html` | 비어 있음 (위와 같음) | 0 |
| **합계** | | **111** |

**2026-08-02 슬라이드수정요청 3차**: 옛 108장(PDF) 기준 지적 반영 — 삭제 2(`C1-7`·`C1-11P`) · 순서 변경 4(`C1-N1`↔`C1-1` · `C1-6`→실습①앞 · `C2-N3`→`C2-8`뒤 · `C3-N4`→3교시→5교시 `C4-15`뒤) · 문구 정정 다수. 113 → 111장. part-01 19→17 · part-03 15→14(`C3-N4` 이관) · part-05 22→23(`C3-N4` 편입). 신규 family `w2-flow3`(`C2-N3`) 1종 추가 등재. 계획·근거는 대화 세션 기록, 상세는 `deck.contract.json`의 `decks.강의덱.note`.

- **divider는 6개**(`P1`~`P6`) → `verify_deck.py --parts 6`. divider ID는 **위치와 단조 증가해야** 한다(`verify_deck.py`의 «PART divider 번호 단조성» 검사 — `known_violations`로 강등 불가). 2026-08-02 PART4↔5 스왑에서 divider ID 두 개(`P4`·`P5`)를 함께 교환한 이유다.
- **2026-08-02 PART4↔5 스왑**: 파트 내용을 파일째 맞바꿔 «part-NN = N번째 파트» 규약을 유지했다. **본문 슬라이드의 `data-slide` ID는 바꾸지 않았다** — 그래서 4교시에 `C5-*`·`M5`가, 5교시에 `C4-*`·`M4`가 있다(노트·이미지 매니페스트가 ID로 슬라이드를 지목하므로 ID 유지가 안전하다). divider만 예외로 교환했다.
- **마무리 2장이 왜 shell이 아니라 part-06에 있나**: 조립기는 `<!-- ::PARTS:: -->` 마커를 **하나만** 허용한다. 예비 구획을 THANK YOU 뒤에 두려면 마무리도 파트 조각에 있어야 한다. 6-10·6-11은 원래 6교시 초안 행이므로 자리도 맞다. 렌더 순서는 `… 6교시 → 마무리 → THANK YOU → 예비 33장`.
- **예비·확장 구획**(`w2-annex`)은 상시 흐름이 아니라 필요할 때 `G` 메뉴로 점프해 쓰는 강사용 구획이다. 헤더에 `.s-team`이 없어 `PART n/N` 라벨이 주입되지 않는다(의도). 초안의 `CORE`/`FLEX`/`REC` 분류 태그는 수록 메타데이터라 화면에 노출하지 않는다.
- 2주차 신규 구도(`w2-roadmap`·`w2-practice`·`w2-scope`·`w2-screen`·`w2-slot`·`w2-flow3` 등 39종)는 `shell.html`의 `<style id="kit-additions">`에 CSS가 있고, **`courses/바이브코딩/sessions/2주차/deck.contract.json`의 `layout_families`**에 실제 family로 등재돼 있다(주차 종속 family는 범용 `verify_deck.py`가 아니라 여기 산다 — 2026-07-29 리팩터). 미등재 클래스는 전부 `full`로 뭉개져 「같은 구도 3연속」이 오탐된다(2026-08-02 `C2-N3` 이동 때 실제로 겪음 — `w2-flow3` 등재로 해소). 안정화되면 `kit/styles/patterns.css`로 환류한다.
- **2026-07-27 샘플 재설계 신규 구도 6종**(`w2-target`·`w2-typecard`·`w2-analogy`·`w2-itr`·`w2-handoff`·`w2-stepwarn` — p7/p13/p14/p19/p35/p58)도 같은 방식으로 `shell.html` kit-additions + `verify_deck.py` family_signature()에 등재했다. 배경: `reports/create-slides-quality/week1_visual_benchmark.md`의 S3CE/S3PRV/29/S3ITR/S3HUM/S3MAP 원리를 이식.

## 명령

```bash
python scripts/assemble_deck.py sessions/2주차/강의덱.초안
python scripts/verify_deck.py sessions/2주차/강의덱.html --parts 6
python scripts/verify_notes.py sessions/2주차/강의덱.html sessions/2주차/강의덱_발표자노트.html
```
