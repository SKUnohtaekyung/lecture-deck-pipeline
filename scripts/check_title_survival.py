#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""초안 제목이 덱 화면에서 살아남았는가 (F2)

`report_draft_sync.py`와 무엇이 다른가 — **다른 검사다**
------------------------------------------------------
`report_draft_sync.py`는 «초안 표의 제목 시퀀스»와 «덱 제목 시퀀스»를 정렬해
대조한다. 그래서 잡는 것은 「행이 밀렸다·빠졌다」다. 그런데 실제로 겪은 사고는
그게 아니었다: **제목이 `.s-eyebrow`로 밀려나거나 본문에 자리를 내주어 화면에서
제목 자리를 잃은** 유형(2주차 실측 4건)이다. 이건 시퀀스 대조에서 그냥
`[제목불일치]` 하나로 보이고, 그 리포트는 정렬 artifact 때문에 `[제목불일치]`가
대량이라 진짜 사고가 노이즈에 묻힌다.

이 스크립트가 묻는 것은 하나다:
    **초안이 정한 제목 문자열이 그 슬라이드의 화면 텍스트 어딘가에 남아 있는가.**
어디에 있는지(제목 자리인지 eyebrow인지 본문인지)까지 구분해 보고한다.

⚠️ 지금은 **게이트가 아니다**
---------------------------
계획(F2)의 선행 조건: "오탐률을 먼저 측정해 20% 미만으로 낮춘 뒤 게이트화한다."
그래서 기본 종료코드는 0이고, `--strict`를 줄 때만 소실 건수로 1을 반환한다.
`report_draft_sync.py`가 `sys.exit(1)`이 아예 없어 **항상 통과**하던 것과 달리,
여기서는 강제 경로가 존재하되 기본이 꺼져 있는 상태다.

사용:
    python scripts/check_title_survival.py <주차N>
    python scripts/check_title_survival.py <주차N> --strict     # 소실이 있으면 exit 1
    python scripts/check_title_survival.py <주차N> --show-all   # 살아남은 것까지 전부

종료코드: 0 통과(기본은 항상 0) · 1 --strict에서 소실 발견 · 2 입력 없음
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import unicodedata
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import verify_session_docs as vsd                  # noqa: E402  resolve_draft·parse_tables 재사용
from verify_notes import SlideParser               # noqa: E402  덱 파싱 재사용
import report_draft_sync as rds                    # noqa: E402  초안 표 추출 재사용

ROOT = HERE.parent

# ── 대조 전 정리 ────────────────────────────────────────────────────────
# 초안의 제목 칸에는 화면에 나가지 않는 **제작 표기**가 함께 들어 있다.
# 실측(2주차): `CORE`·`FLEX`·`REC` 구간 태그 · `(선택)`·`(복구)` 꼬리표 ·
#              `(간지)`·`(표지)` 같은 슬라이드 종류 표시.
# 이걸 안 떼고 대조하면 105개 중 85개가 「소실」로 잡힌다(오탐률 81%).
_BACKTICK = re.compile(r"`[^`]*`")
_KIND_PREFIX = re.compile(r"^\s*\((?:간지|표지|마무리|목차|부록)\)\s*")
_TAIL_PAREN = re.compile(r"\s*\((?:선택|복구|예비|보강)[^)]*\)\s*$")
_DECOR = re.compile(r'[\s​·•「」『』《》〈〉«»""\'\'"\'()\[\]{}—–\-~!?.,:;/\\|`]+')


def strip_authoring_marks(s: str) -> str:
    """초안 제목에서 제작 표기를 떼어낸다(화면에 나가지 않는 것들)."""
    s = unicodedata.normalize("NFC", s or "")
    s = _BACKTICK.sub(" ", s)
    s = _KIND_PREFIX.sub("", s)
    s = _TAIL_PAREN.sub("", s)
    return s.strip()


def normalize(s: str) -> str:
    """비교용 정규화 — 공백·장식기호를 지우고 NFC로 맞춘다.
    ⚠️ 글자는 지우지 않는다. 지우면 «다른 제목»이 같아 보여 소실을 놓친다."""
    s = unicodedata.normalize("NFC", s or "")
    return _DECOR.sub("", s).lower()


_TOKEN = re.compile(r"[가-힣]{2,}|[A-Za-z][A-Za-z0-9.\-]{1,}|\d+")


def tokens(s: str) -> list[str]:
    """내용어 토큰 — 2자 이상 한글 덩어리 · 영문 낱말 · 숫자."""
    return [t.lower() for t in _TOKEN.findall(unicodedata.normalize("NFC", s or ""))]


def coverage(needle: str, haystack_tokens: set[str]) -> float:
    """needle의 내용어 중 몇 %가 haystack의 **토큰 집합**에 있는가.
    ⚠️ 완전일치·부분문자열이 아니라 **토큰 포함률**로 본다. 제목은 조립하면서
       어순이 바뀌거나 «오늘 이렇게 배웁니다» → «1교시 이렇게 배웁니다»처럼
       한두 낱말이 조정되는데, 그건 소실이 아니라 정상 편집이다.
    ⚠️ 원문 문자열에 대한 부분일치로 세지 않는다 — 「이미지」·「아이콘」 같은
       짧은 낱말이 아무 슬라이드에서나 걸려 무관한 장이 100%로 잡혔다(실측)."""
    nt = tokens(needle)
    if not nt:
        return 0.0
    hit = sum(1 for t in nt if t in haystack_tokens)
    return hit / len(nt)


COVER_TITLE = 0.7      # 제목 자리에서 인정할 토큰 포함률
COVER_SCREEN = 0.8     # 화면 아무 데나에서 인정할 포함률(제목보다 엄격 — 우연 일치 방지)

# ⚠️ 초안 제목 칸은 «제목 — 부제» 또는 «제목 (부연)» 형태가 흔하고, 덱은 그중
#    **앞머리만 제목으로 쓰고 뒤는 본문으로 내린다.** 그건 정상 편집이지 제목
#    강등이 아니다. 실측(2주차): 이걸 구분하지 않으면 C1-2·C1-4·C3-5·M2·M4가
#    전부 「제목 강등」으로 잡히는데 다섯 건 다 오탐이었다.
#      초안 «누구의 어떤 불편인가 — 타깃·페인포인트» → 덱 «누구의 어떤 불편인가»
#      초안 «실습 ⑤ prd.md 만들기 (ChatGPT 초안 → …)» → 덱 «실습 ⑤ prd.md 만들기»
_SUBTITLE_SPLIT = re.compile(r"\s+[—–]\s+|\s*\(")


def title_head(s: str) -> str:
    """«제목 — 부제»·«제목 (부연)»에서 제목 부분만 돌려준다."""
    return _SUBTITLE_SPLIT.split(s, 1)[0].strip() or s


class SlideTextParser(SlideParser):
    """SlideParser가 제목만 모으므로, 슬라이드별 **전체 화면 텍스트**를 함께 모은다."""

    def __init__(self):
        super().__init__()
        self._texts: list[list[str]] = []

    def handle_starttag(self, tag, attrs):
        before = len(self.slides)
        super().handle_starttag(tag, attrs)
        if len(self.slides) > before:
            self._texts.append([])

    def handle_data(self, data):
        super().handle_data(data)
        if self._texts and data and data.strip():
            self._texts[-1].append(data)

    def slide_texts(self) -> list[str]:
        return [" ".join(t) for t in self._texts]


def load_deck(deck_path: Path):
    html = deck_path.read_text(encoding="utf-8")
    p = SlideTextParser()
    p.feed(html)
    p.close()
    texts = p.slide_texts()
    out = []
    for i, sl in enumerate(p.slides):
        title = (sl.get("title") or "").strip()
        text = texts[i] if i < len(texts) else ""
        out.append({
            "sid": sl.get("data_slide") or f"#{i + 1}",
            "title": title,
            "text": text,
            "title_tokens": set(tokens(title)),
            "text_tokens": set(tokens(text)),
        })
    return out


# ── 초안 행 번호 → 덱 슬라이드 ID 대응 ──────────────────────────────────
# ⚠️ 이것이 이 검사의 **1차 열쇠**다. 제목 문자열은 열쇠가 될 수 없다 —
#    조립하면서 제목을 다시 쓰는 것이 정상이기 때문이다(실측 2주차):
#      초안 «한 줄 정의는 제작 나침반»      → 덱 «한 줄 정의, 제작 기준 한 줄»
#      초안 «결과와 기능은 다릅니다»        → 덱 «기능을 다 만들어도 불편이 …»
#    이걸 텍스트로 대조하면 «다시 쓴 제목»과 «잃어버린 제목»이 구별되지 않는다.
#    번호로 짝을 지은 **다음에** 텍스트를 보면, 비로소 «이 슬라이드가 원래
#    다루기로 한 내용을 아직 다루는가»를 물을 수 있다.
# ⚠️ 번호 칸에도 구간 태그가 붙어 있다 — 실측 2주차의 첫 칸은 "1-2 `CORE`"다.
#    태그를 안 떼면 정규식이 통째로 실패해 **전 행이 「번호대응없음」으로 떨어진다.**
_NUM_BODY = re.compile(r"^(\d+)\s*[-–]\s*([^\s]+)")


def draft_num_to_sid(num: str, sid_set: set[str]) -> str:
    """초안 행 번호에 대응하는 덱 slide id를 찾는다. 없으면 빈 문자열."""
    num = _BACKTICK.sub(" ", num or "").strip()
    m = _NUM_BODY.match(num)
    if not m:
        return ""
    part, body = m.group(1), m.group(2)
    for cand in (f"C{part}-{body}", f"{part}-{body}", body):
        if cand in sid_set:
            return cand
    if body in ("MAP", "맵"):
        return f"M{part}" if f"M{part}" in sid_set else ""
    if body in ("간지",):
        return f"P{part}" if f"P{part}" in sid_set else ""
    return ""


def classify(draft_title: str, slides) -> tuple[str, str, float]:
    """초안 제목이 어디에 남아 있는지 판정한다.
    반환: (상태, 슬라이드ID, 최고 포함률)
      제목자리 — 어느 슬라이드의 **제목 요소**에 남아 있다(정상)
      화면잔존 — 제목 자리는 잃었지만 그 슬라이드 화면 텍스트에는 있다
                 (F2가 잡으려는 유형 — eyebrow로 밀리거나 본문에 흡수된 경우)
      소실     — 덱 어디에서도 찾지 못했다
    """
    clean = strip_authoring_marks(draft_title)
    if not tokens(clean):
        return ("빈제목", "", 0.0)

    best_t, best_t_sid = 0.0, ""
    for s in slides:
        c = coverage(clean, s["title_tokens"])
        if c > best_t:
            best_t, best_t_sid = c, s["sid"]
    if best_t >= COVER_TITLE:
        return ("제목자리", best_t_sid, best_t)

    best_s, best_s_sid = 0.0, ""
    for s in slides:
        c = coverage(clean, s["text_tokens"])
        if c > best_s:
            best_s, best_s_sid = c, s["sid"]
    if best_s >= COVER_SCREEN:
        return ("화면잔존", best_s_sid, best_s)

    return ("소실", best_s_sid, max(best_t, best_s))


def main() -> int:
    ap = argparse.ArgumentParser(description="초안 제목이 덱 화면에서 살아남았는지 본다")
    ap.add_argument("week", help="주차 번호 (예: 2)")
    ap.add_argument("--strict", action="store_true", help="소실이 있으면 exit 1")
    ap.add_argument("--show-all", action="store_true", help="제목자리로 살아남은 것까지 출력")
    a = ap.parse_args()

    wk = a.week[:-2] if a.week.endswith("주차") else a.week
    session = rds._session_dir(ROOT, wk)
    deck = session / "강의덱.html"
    if not deck.exists():
        print(f"[입력없음] 덱이 없다: {deck}")
        return 2

    # resolve_draft(sess_dir, wk) — sess_dir는 Path여야 한다(내부에서 / 연산자를 쓴다)
    draft_path = Path(vsd.resolve_draft(Path(session), wk))
    if not draft_path.exists():
        print(f"[입력없음] 초안을 찾을 수 없다: {draft_path}")
        return 2

    draft_rows = rds.extract_draft_rows(Path(draft_path).read_text(encoding="utf-8"))
    slides = load_deck(deck)
    if not draft_rows:
        print(f"[입력없음] 초안에서 «슬라이드 제목» 열을 가진 표를 찾지 못했다: {draft_path}")
        return 2

    sid_set = {s["sid"] for s in slides}
    by_sid = {s["sid"]: s for s in slides}

    buckets: dict[str, list] = {"제목자리": [], "화면잔존": [], "제목교체": [],
                                "슬라이드없음": [], "대응미상": [], "빈제목": []}
    for num, title in draft_rows:
        clean = strip_authoring_marks(title)
        if not tokens(clean):
            buckets["빈제목"].append((num, title, ""))
            continue

        sid = draft_num_to_sid(num, sid_set)
        if sid:
            # ① 번호로 짝이 지어졌다 — 이제 «그 슬라이드가 아직 이 내용을 다루는가»를 묻는다
            s = by_sid[sid]
            # 제목 자리 판정은 «앞머리»로 — 부제가 본문으로 내려간 것은 강등이 아니다
            ct = max(coverage(title_head(clean), s["title_tokens"]),
                     coverage(clean, s["title_tokens"]))
            cx = coverage(clean, s["text_tokens"])
            if ct >= COVER_TITLE:
                buckets["제목자리"].append((num, title, f"{sid} ({ct:.0%})"))
            elif cx >= COVER_SCREEN:
                # ★ F2가 잡으려던 유형: 제목 자리는 잃었는데 내용은 화면에 남았다
                buckets["화면잔존"].append((num, title, f"{sid} 제목{ct:.0%}/화면{cx:.0%}"))
            else:
                # 슬라이드는 있는데 제목도 내용도 다르다 — 조립 중 다시 쓴 경우가 대부분
                buckets["제목교체"].append(
                    (num, title, f"{sid} «{s['title']}» (제목{ct:.0%}/화면{cx:.0%})"))
            continue

        # ② 번호로 짝이 안 지어졌다.
        # ⚠️ 여기서 텍스트만으로 「제목 강등」을 주장하지 않는다. 열쇠 없이 고른
        #    최고점 슬라이드는 근거가 못 된다 — 실측에서 «모바일 폭 확인»이
        #    무관한 C3-N3에 100%로 붙었다. 참고 후보만 달아 사람에게 넘긴다.
        state, tsid, score = classify(title, slides)
        if state == "제목자리":
            buckets["제목자리"].append((num, title, f"{tsid} ({score:.0%}) ※번호대응없음"))
        elif state == "화면잔존":
            buckets["대응미상"].append((num, title, f"후보 {tsid} ({score:.0%})"))
        else:
            buckets["슬라이드없음"].append((num, title, ""))

    total = sum(len(v) for v in buckets.values())
    print(f"초안 {os.path.relpath(draft_path, ROOT)} — 제목 {total}개")
    print(f"덱   {os.path.relpath(deck, ROOT)} — 슬라이드 {len(slides)}장\n")
    for k in ("제목자리", "화면잔존", "제목교체", "슬라이드없음", "대응미상", "빈제목"):
        if buckets[k]:
            print(f"  {k} {len(buckets[k])}")

    if buckets["화면잔존"]:
        print("\n[화면잔존] ★ 제목 자리를 잃고 본문·eyebrow 등으로 내려갔다 — 이 검사의 표적이다")
        for num, title, sid in buckets["화면잔존"]:
            print(f"  · {num} «{title}» → {sid}")
    if buckets["슬라이드없음"]:
        print("\n[슬라이드없음] 대응 슬라이드가 없다 — 삭제가 의도였는지 확인하라")
        for num, title, _ in buckets["슬라이드없음"]:
            print(f"  · {num} «{title}»")
    if a.show_all:
        for k in ("제목교체", "제목자리"):
            if buckets[k]:
                print(f"\n[{k}]")
                for num, title, sid in buckets[k]:
                    print(f"  · {num} «{title}» → {sid}")

    lost = len(buckets["화면잔존"])
    gone = len(buckets["슬라이드없음"])
    print(f"\n제목 강등 {lost}건 · 대응 슬라이드 없음 {gone}건 / 초안 {total}행")
    if not a.strict:
        print("RESULT | 참고 | 게이트 아님 — F2의 선행 조건(오탐률 20% 미만)을 먼저 충족해야 한다")
        return 0
    if lost:
        print(f"RESULT | FAIL | 초안 제목 {lost}개가 제목 자리를 잃었다")
        return 1
    print("RESULT | PASS | 제목 강등 없음")
    return 0


if __name__ == "__main__":
    sys.exit(main())
