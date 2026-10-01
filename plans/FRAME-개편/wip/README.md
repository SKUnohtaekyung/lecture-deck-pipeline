# FRAME 작업 원본 스냅샷 (2026-10-01 중단 지점)

`tmp/`는 git에 올라가지 않아, 이어서 작업하는 데 필요한 원본만 여기 둔다. **작업은 `tmp/frame/`에서 한다** — 스크립트 경로가 전부 그쪽을 본다.

- 복원: `python plans/FRAME-개편/wip/restore.py` (없는 파일만) · `--force` 덮어쓰기
- 저장: `python plans/FRAME-개편/wip/restore.py --save` (tmp → wip, 이미 있는 파일만 갱신)

| 폴더 | 내용 |
|---|---|
| `E/slides/` | 슬라이드 82장 원본(ID별 section 파일) — `gen/build_parts.py`가 읽는다 |
| `E/` | 워커 지침(`공통지침.md` · `v2_요약.md`) · `shoot_ids.py` · `v2/_워커프롬프트_템플릿.md` |
| `E1/src/` · `E1/build_shell.py` | 셸 CSS/JS 소스와 빌더 → `강의덱.초안/shell.html` |
| `E1/shots/_v2sheet.png` | 워커가 보는 모양 기준 그림(보라 · 노랑 면은 폐기) |
| `E9/` | 발표자 노트 생성기 |
| `view/` | 8810 서버(`serve_live.py`) · 자동 조립(`live_assemble.py`) · 승인된 디자인 프리뷰 |
| `draft/` | 문구 초안 조각 |

상태와 재개 절차는 `../PROGRESS.md` 맨 끝 「⏸ 중단 지점」.
