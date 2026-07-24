# 1주차 PART6 실습 재설계 — 원본 백업 (2026-07-24)

- `shell_실습6주제_원본_2026-07-24.html` = 재설계 직전 shell.html 전체 스냅샷.
- 이 안에 옛 실습 파트(P7 + X00 + X01~X06 여섯 주제)와 그 인라인 CSS(`<style data-part="shell">`의 X01~X06 규칙)가 그대로 있다.
- **복구법**: shell.html의 실습 구역(P7~X06 섹션 + 관련 X01~X06 인라인 CSS)을 이 스냅샷의 해당 부분으로 되돌린 뒤 `python scripts/assemble_deck.py sessions/1주차/강의덱.초안` 재조립. verify 계약(expected_n)도 원복.
- git은 최후 안전망(다중 세션 동시 편집 중이라 이번 작업에서 커밋은 하지 않음).
