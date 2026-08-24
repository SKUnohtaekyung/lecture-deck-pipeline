#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""개념KB 청크 회수 도구 — 필드 단위로 가리거나 보여준다.

P7 반증 실험(A/B)에서 **A 조건을 자기규율이 아니라 기계로 강제**하려고 만들었다.
"안 보겠다"는 다짐은 강제가 아니다 — 이 저장소의 교훈이 정확히 그것이다.

    --blind   `PPT 소재:`·`필수 진술:`을 **가린 채** 청크를 낸다 (조건 A)
    --full    전부 낸다 (조건 B)

사용:
    python scripts/kb_extract.py 2 --slugs C-IA,C-화면순서 --blind
    python scripts/kb_extract.py 2 --section 5 --index-only
"""
import io
import os
import re
import sys
import argparse

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import _course_paths as CP
except Exception:
    CP = None

HIDDEN = ("PPT 소재", "필수 진술")
# 0판정 가드 — HIDDEN 라벨이 문서에서 개명되면 아래 매치가 전부 0이 되어 --blind가
# 조용히 무력화된다(가려야 할 내용이 그대로 노출돼도 아무 신호가 없다).
# 다만 청크 규약상 `범위:인접`·`범위:보류` 청크는 이 두 필드가 애초에 없다
# (슬라이드 본문 재료가 아니라 강사 질의응답용 — main()의 청크 선별 주석 참조).
# 그 스코프만 골랐을 때의 "가림 0줄"은 정당한 0이다. "라벨 개명"과 "원래 없음"을
# 반드시 구분해야 하므로, 가림 판정은 이 두 스코프를 제외한 청크에서만 센다.
SCOPES_WITHOUT_HIDDEN = ("인접", "보류")


def kb_path(week):
    sess = CP.session_dir(week) if CP else os.path.join("sessions", "%s주차" % week)
    return os.path.join(sess, "자료", "%s주차_개념KB.md" % week)


def chunks(text):
    for part in re.split(r"(?=\n#{1,4}\s*\[C-)", text):
        m = re.match(r"\n#{1,4}\s*\[(C-[^\]]+)\]", part)
        if m:
            yield m.group(1), part


def meta(part, key):
    m = re.search(r"%s:\s*([^|\-]+)" % key, part)
    return m.group(1).strip() if m else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("week")
    ap.add_argument("--slugs", help="콤마 구분")
    ap.add_argument("--section", help="구간 번호")
    ap.add_argument("--blind", action="store_true", help="PPT 소재·필수 진술을 가린다")
    ap.add_argument("--index-only", action="store_true")
    a = ap.parse_args()

    p = kb_path(a.week)
    if not os.path.isfile(p):
        print("개념KB 없음: %s" % p)
        return 2
    text = io.open(p, encoding="utf-8").read()

    want = [s.strip() for s in a.slugs.split(",")] if a.slugs else None
    picked = []
    for slug, part in chunks(text):
        if want and slug not in want:
            continue
        if a.section and a.section not in [x.strip() for x in meta(part, "구간").split(",")]:
            continue
        picked.append((slug, part))

    if a.index_only:
        for slug, part in picked:
            print("%-26s 우선=%-3s 범위=%-4s 구간=%s"
                  % (slug, meta(part, "우선"), meta(part, "범위") or "코어", meta(part, "구간")))
        print("\n총 %d청크" % len(picked))
        return 0

    if a.blind:
        print("=" * 74)
        print("⚠️ BLIND 모드 — `PPT 소재:`·`필수 진술:`을 가렸습니다 (P7 조건 A).")
        print("   가려진 줄은 [가림] 표시로 남깁니다 — 있었다는 사실 자체는 숨기지 않습니다.")
        print("=" * 74)
    masked_total = 0
    core_masked, core_unmasked = [], []  # 0판정 가드 계수 — 범위:인접/보류 제외
    for slug, part in picked:
        out = []
        chunk_masked = 0
        for line in part.splitlines():
            if a.blind and any(("**%s:**" % h) in line for h in HIDDEN):
                which = next(h for h in HIDDEN if ("**%s:**" % h) in line)
                out.append("- **%s:** [가림 — P7 조건 A]" % which)
                chunk_masked += 1
            else:
                out.append(line)
        masked_total += chunk_masked
        if a.blind and meta(part, "범위") not in SCOPES_WITHOUT_HIDDEN:
            (core_masked if chunk_masked else core_unmasked).append(slug)
        print("\n".join(out).strip())
        print()
    print("─" * 74)
    print("%d청크 · 모드=%s" % (len(picked), "BLIND" if a.blind else "FULL"))
    if a.blind:
        judged, unjudged = len(core_masked), len(core_unmasked)
        excluded = len(picked) - judged - unjudged
        print("가림 판정(HIDDEN 라벨 매치): 판정 %d청크(가림 %d줄) · 미판정 %d청크 · "
              "대상외(범위:인접/보류) %d청크" % (judged, masked_total, unjudged, excluded))
        if unjudged:
            print("⚠️ 0판정 의심 — 코어 범위인데 가려진 줄이 0인 청크: %s" % ", ".join(core_unmasked))
            print("   `PPT 소재:`·`필수 진술:` 라벨이 문서에서 바뀌었는지 확인하라 — "
                  "그렇다면 --blind가 무력화된 상태다(가려야 할 내용이 그대로 노출됨).")
            return 1
        if judged == 0:
            print("가림 판정 대상(범위:인접/보류 제외 청크) 없음 — 정당한 0"
                  "(선택된 청크에 코어 범위가 없음)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
