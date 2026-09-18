# 렌더 증거 namespace — 바이브코딩 온라인 원데이

이 폴더의 **존재 자체가 선언**이다. `scripts/_course_paths.py`의 `verify_root()`는 «그 과목이 `courses/<과목>/sessions/_verify/`를 만들어 두었는가»로 증거 루트를 가른다 — 만들어 두었으면 여기, 아니면 구경로 `sessions/_verify/`다.

**이 폴더를 지우면 이 과목의 증거가 조용히 구경로로 되돌아가고, 거기엔 바이브코딩 과목의 동결 증거(`1주차`·`2주차`)가 있다.** 폴더를 지우지 마라.

## 파일명 규약

| 파일 | 만드는 것 | 읽는 것 |
|---|---|---|
| `N주차/deck-audit.json` | `scripts/receive_audit.py N주차` (브라우저 POST 수신) | `run_deck_checks.py` · `compare_baseline_panel.py` |
| `N주차/강의덱_발표.meta.json` | `scripts/inject_presenter.py … --meta` (명시 요청 시만) | `verify_presenter_deck.py` |

- `1주차`=오전 덱, `2주차`=오후 덱.
- 두 파일 다 **전달물이 아니라 검증용 감사 기록**이다.
- 스크립트 실행 시 `CREATE_SLIDES_COURSE=바이브코딩_온라인`을 지정한다.
