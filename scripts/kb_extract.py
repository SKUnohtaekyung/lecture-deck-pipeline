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
    for slug, part in picked:
        out = []
        for line in part.splitlines():
            if a.blind and any(("**%s:**" % h) in line for h in HIDDEN):
                which = next(h for h in HIDDEN if ("**%s:**" % h) in line)
                out.append("- **%s:** [가림 — P7 조건 A]" % which)
            else:
                out.append(line)
        print("\n".join(out).strip())
        print()
    print("─" * 74)
    print("%d청크 · 모드=%s" % (len(picked), "BLIND" if a.blind else "FULL"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
