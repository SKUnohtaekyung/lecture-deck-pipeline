# 2주차 강의덱.초안 — 조각 구성

정본은 이 폴더의 조각이다. `sessions/2주차/강의덱.html`은 생성물이라 **직접 고치면 다음 조립 때 유실된다.**

| 파일 | 내용 | 장수 |
|---|---|---|
| `shell.html` | head·kit CSS 링크·2주차 신규 구도 CSS(`<style id="kit-additions">`)·발표 엔진 JS + 고정 슬라이드 3장(`S01` 표지 · `S02` 도입 · `S03` 아젠다) + `<!-- ::PARTS:: -->` 마커 1개 | 3 |
| `part-01.html` | PART 1 · 1교시 (`P1` divider + `M1` + `C1-1`~`C1-11`) | 13 |
| `part-02.html` | PART 2 · 2교시 (`P2` + `M2` + `C2-1`~`C2-11`) | 13 |
| `part-03.html` | PART 3 · 3교시 (`P3` + `M3` + `C3-1`~`C3-6`) | 8 |
| `part-04.html` | PART 4 · 4교시 (`P4` + `M4` + `C4-1`~`C4-11`) | 13 |
| `part-05.html` | PART 5 · 5교시 (`P5` + `M5` + `C5-1`~`C5-10`) | 12 |
| `part-06.html` | PART 6 · 6교시 (`P6` + `M6` + `C6-1`~`C6-9`) + **마무리 2장**(`END` 6-10 · `THX` 6-11) | 13 |
| `part-07.html` | 예비·확장 전반 (`A1F1`~`A3F4`) — divider 없음 (2026-07-27: `A2F2`는 C1-8 비교표로 흡수·삭제) | 12 |
| `part-08.html` | 예비·확장 후반 (`A4R1`~`A6F3`) — divider 없음 | 20 |
| **합계** | | **107** |

- **divider는 6개**(`P1`~`P6`) → `verify_deck.py --parts 6`.
- **마무리 2장이 왜 shell이 아니라 part-06에 있나**: 조립기는 `<!-- ::PARTS:: -->` 마커를 **하나만** 허용한다. 예비 구획을 THANK YOU 뒤에 두려면 마무리도 파트 조각에 있어야 한다. 6-10·6-11은 원래 6교시 초안 행이므로 자리도 맞다. 렌더 순서는 `… 6교시 → 마무리 → THANK YOU → 예비 33장`.
- **예비·확장 구획**(`w2-annex`)은 상시 흐름이 아니라 필요할 때 `G` 메뉴로 점프해 쓰는 강사용 구획이다. 헤더에 `.s-team`이 없어 `PART n/N` 라벨이 주입되지 않는다(의도). 초안의 `CORE`/`FLEX`/`REC` 분류 태그는 수록 메타데이터라 화면에 노출하지 않는다.
- 2주차 신규 구도 5종(`w2-roadmap`·`w2-practice`·`w2-scope`·`w2-screen`·`w2-slot`)은 `shell.html`의 `<style id="kit-additions">`에 있고, `scripts/verify_deck.py`의 `family_signature()`에 실제 family로 등재돼 있다. 안정화되면 `kit/styles/patterns.css`로 환류한다.

## 명령

```bash
python scripts/assemble_deck.py sessions/2주차/강의덱.초안
python scripts/verify_deck.py sessions/2주차/강의덱.html --parts 6
python scripts/verify_notes.py sessions/2주차/강의덱.html sessions/2주차/강의덱_발표자노트.html
```
