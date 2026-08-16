#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
report_draft_sync.py — 초안 4열 표와 덱 슬라이드를 나란히 놓고 보는 대조 리포트.

콘텐츠 초안(`N주차_초안.md`)의 4열 표(#·슬라이드 제목·본문 문구·비유·멘트)와
조립된 덱(`강의덱.html`)의 `.slide` 섹션은 create-slides 조립 과정에서 서로
어긋날 수 있다(슬라이드 삽입·삭제·순서 변경이 한쪽에만 반영되는 경우 등).
이 스크립트는 **판정하지 않는다** — 두 목록을 제목 기준으로 정렬해 나란히
보여주고, 일치/제목 불일치/한쪽에만 있는 행을 표시할 뿐이다. 소유권(어느 쪽이
맞는지) 판단은 사람이 한다.

초안 파일 경로 해석은 scripts/verify_session_docs.py의 resolve_draft()를
그대로 재사용한다(중복 구현 금지). 덱 슬라이드 파싱은 scripts/verify_notes.py의
SlideParser를 재사용한다(같은 이유).

사용:
  python scripts/report_draft_sync.py <주차N>
  python scripts/report_draft_sync.py <주차N> --strict   # 초안에만/덱에만 행이 있으면 exit 1
종료코드:
  기본   — 항상 0(판정 없음 — 소유권 판단은 사람).
  --strict — «초안에만»·«덱에만» 행이 1건이라도 있으면 1 (P1 · 2026-08-17:
  기본 상시-0이 기제3(게이트 OFF 기본값)의 한 사례로 확정돼 러너 편입용 판정
  모드를 신설했다. 제목불일치는 check_title_survival이 정규화해 판정하므로
  여기서는 세지 않는다 — 존재/부재만 본다).
"""
import argparse
import difflib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_session_docs as vsd  # resolve_draft, parse_tables, read 재사용
from verify_notes import SlideParser  # 덱 슬라이드 제목 추출 재사용
import os

# ── 과목 아키텍처 경로 폴백 (2026-07-29 P4.5) ────────────────────────────
# `courses/<과목>/sessions/N주차` 우선, 없으면 구경로 `sessions/N주차`.
# 정본은 scripts/_course_paths.py. 구경로 폴백을 없애지 마라 — 1주차(동결) 자료가
# 메타 헤더에서 구경로를 참조한다.
def _cp():
    try:
        _d = os.path.dirname(os.path.abspath(__file__))
        if _d not in sys.path:
            sys.path.insert(0, _d)
        import _course_paths
        return _course_paths
    except Exception:
        return None


def _session_dir(root, wk):
    m = _cp()
    if m is None:
        return Path(root) / "sessions" / f"{wk}주차"
    return Path(m.session_dir(wk, str(root)))


def _contracts_dir(root):
    m = _cp()
    if m is None:
        return Path(root) / "sessions" / "_contracts"
    d = m.contracts_dir(str(root))
    return Path(d) if d else Path(root) / "sessions" / "_contracts"
# ─────────────────────────────────────────────────────────────────────────



def extract_draft_rows(text):
    """초안의 4열 표(#·슬라이드 제목·본문 문구·비유·멘트)에서 (번호, 제목) 목록을
    표 등장 순서 그대로 뽑는다. 「0. 덱 기본 정보」·「PART 구조」 같은 다른 표는
    헤더에 슬라이드 제목·본문 열이 없어 자동으로 제외된다."""
    rows = []
    for t in vsd.parse_tables(text):
        if not t:
            continue
        hdr = [(c or "") for c in t[0]]
        if not (any("슬라이드 제목" in c for c in hdr) and any("본문" in c for c in hdr)):
            continue
        for r in t[1:]:
            if not r or not (r[0] or "").strip():
                continue
            num = r[0].strip()
            title = r[1].strip() if len(r) > 1 else ""
            rows.append((num, title))
    return rows


def extract_deck_rows(deck_html):
    """덱의 .slide 섹션에서 (data-slide, 제목 텍스트) 목록을 문서 순서 그대로 뽑는다."""
    p = SlideParser()
    p.feed(deck_html)
    p.close()
    rows = []
    for sl in p.slides:
        rows.append((sl.get("data_slide") or "", sl.get("title") or ""))
    return rows


def build_diff(draft_rows, deck_rows):
    """제목 시퀀스 기준으로 difflib 정렬해 (상태, draft_row|None, deck_row|None) 목록을 만든다.
    상태: 일치 / 제목불일치(자리는 맞대응하나 텍스트가 다름) / 초안에만 / 덱에만."""
    draft_titles = [t for _, t in draft_rows]
    deck_titles = [t for _, t in deck_rows]
    sm = difflib.SequenceMatcher(a=draft_titles, b=deck_titles, autojunk=False)
    lines = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                lines.append(("일치", draft_rows[i1 + k], deck_rows[j1 + k]))
        elif tag == "replace":
            n = min(i2 - i1, j2 - j1)
            for k in range(n):
                lines.append(("제목불일치", draft_rows[i1 + k], deck_rows[j1 + k]))
            for k in range(n, i2 - i1):
                lines.append(("초안에만", draft_rows[i1 + k], None))
            for k in range(n, j2 - j1):
                lines.append(("덱에만", None, deck_rows[j1 + k]))
        elif tag == "delete":
            for k in range(i1, i2):
                lines.append(("초안에만", draft_rows[k], None))
        elif tag == "insert":
            for k in range(j1, j2):
                lines.append(("덱에만", None, deck_rows[k]))
    return lines


def fmt_row(row):
    if row is None:
        return "(없음)"
    num, title = row
    return f"{num} | {title}"


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

    ap = argparse.ArgumentParser()
    ap.add_argument("week", help="주차 번호 (예: 2)")
    ap.add_argument("--root", default=None, help="저장소 루트 재정의(자체 테스트용)")
    ap.add_argument("--strict", action="store_true",
                    help="초안에만/덱에만 행이 있으면 exit 1")
    args = ap.parse_args()

    root = Path(args.root) if args.root else Path(__file__).resolve().parent.parent
    wk = args.week
    sess = _session_dir(root, wk)
    deck_path = sess / "강의덱.html"

    print(f"=== report_draft_sync {wk}주차 ===")

    if not deck_path.exists():
        print(f"덱 파일 없음: {deck_path} — 대조할 덱이 아직 없어 리포트를 만들지 않는다.")
        sys.exit(0)

    draft_path = vsd.resolve_draft(sess, wk)
    draft_text = vsd.read(draft_path)
    if draft_text is None:
        print(f"초안 파일 없음: {draft_path}")
        sys.exit(0)
    deck_text = vsd.read(deck_path)

    draft_rows = extract_draft_rows(draft_text)
    deck_rows = extract_deck_rows(deck_text)
    print(f"초안: {draft_path} ({len(draft_rows)}행)")
    print(f"덱  : {deck_path} ({len(deck_rows)}슬라이드)")
    print()

    diff_lines = build_diff(draft_rows, deck_rows)
    counts = {"일치": 0, "제목불일치": 0, "초안에만": 0, "덱에만": 0}
    for status, d_row, k_row in diff_lines:
        counts[status] += 1
        print(f"[{status:6}] 초안: {fmt_row(d_row):50} <-> 덱: {fmt_row(k_row)}")

    print()
    print(
        f"--- 일치={counts['일치']} 제목불일치={counts['제목불일치']} "
        f"초안에만={counts['초안에만']} 덱에만={counts['덱에만']} ---"
    )
    if args.strict:
        drift = counts["초안에만"] + counts["덱에만"]
        if drift:
            print(f"RESULT | FAIL | --strict: 초안에만/덱에만 {drift}건 — "
                  f"소유권을 판정해 초안 또는 덱을 맞추거나, 주차 계약에 "
                  f"draft_sync_baseline waiver(사유·일자)를 등재하라")
            sys.exit(1)
        print("RESULT | PASS | --strict: 초안에만/덱에만 0건")
        sys.exit(0)
    print("RESULT | 판정 없음(사람이 소유권 확인) — 항상 exit 0")
    sys.exit(0)


if __name__ == "__main__":
    main()
