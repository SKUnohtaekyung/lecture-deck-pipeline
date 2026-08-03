#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""기준판 대비 장별 밀도 비교 — 「이 장이 기준판에서 얼마나 멀어졌나」

왜 필요한가
----------
`references/phases/03-레이아웃선택.md`(R-BOX-01)가 기준판 대비 장당 박스 수·
시각자료 보유율을 **비교 기준선**으로 쓰라고 규정했는데, **그것을 계산하는
도구가 없었다.** 사람이 매번 손으로 세야 하면 안 세게 된다 — 이 저장소가
반복해서 겪은 「규칙은 있고 집행은 없다」의 전형이다.

⚠️ **임계로 FAIL시키지 않는다. 비교값이다.** 기준판 표본은 6장으로 작고, 정보
   모양에 따라 적정 박스 수는 다르다. 이 스크립트는 **어디를 사람이 다시 볼지**
   가리킬 뿐이다. 종료코드는 언제나 0이다(입력 오류만 2).

무엇을 비교하나
--------------
`sessions/_verify/<주차>/deck-audit.json`의 `perSlide`(브라우저 실측)를 읽어
장별 [박스 수 · 시각자료 유무 · 글자 수 · 잉크 점유율]을 기준판 값과 나란히 둔다.

⚠️ **박스 수의 「4」와 「5.5」를 섞지 마라** — 세는 정의가 다르다:
   · 사용자 지시의 「한 장 4개」 = 사람이 보는 **내용 박스**(R-QC-16의 계수 층)
   · 여기의 5.5 = `audit_render.js`가 세는 **테두리·배경을 가진 24×24px 이상
     요소 전부**(중첩 요소·배지 포함). 자동으로 더 크게 나온다.
   이 스크립트는 **후자끼리만** 비교한다.

사용:
    python scripts/compare_baseline_panel.py <주차>
    python scripts/compare_baseline_panel.py <주차> --top 20
"""
from __future__ import annotations

import argparse
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# ── 기준판 (2주차 5구간 C5-1~C5-6 · 2026-08-03 실측) ─────────────────────
# 2주차는 이 6장을 먼저 확정하고 그 기준으로 나머지를 제작했다(사용자 확인).
# A/B 실험(B 5승 1패)으로 연출이 확정된 판이다.
# ⚠️ 다른 과목·다른 덱에 이 값을 규칙으로 물려주지 마라 — 한 과목의 실측치다.
#    기준선이 없는 새 과목은 FAIL이 아니라 «비교 없음»으로 시작한다.
BASELINE = {
    "name": "2주차 5구간 기준판 C5-1~C5-6 (6장)",
    "boxes": 5.5,        # 장당 박스 수(audit_render 계수)
    "chars": 234,        # 장당 글자 수
    "visual_ratio": 0.67,  # 시각자료 보유율(V-B 정의)
}
# 참고 집단 — 같은 덱의 나머지가 기준판에서 얼마나 멀어졌는지
REFERENCE = {
    "나머지 본문(81장)": {"boxes": 7.4, "chars": 297, "visual_ratio": 0.65},
    "교시 로드맵(5장)": {"boxes": 12.6, "chars": 284, "visual_ratio": 0.00},
}


def _week(w: str) -> str:
    return w if w.endswith("주차") else f"{w}주차"


def load(week: str):
    path = os.path.join(ROOT, "sessions", "_verify", _week(week), "deck-audit.json")
    if not os.path.exists(path):
        print(f"[입력없음] 렌더 증거가 없다: {os.path.relpath(path, ROOT)}")
        print("  브라우저에서 만들어라:")
        print("    python -m http.server 8799   (창 1280x720 이상)")
        print("    await (await fetch('/scripts/audit_all.js')).text().then(eval)")
        return None, path
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    if data.get("INVALID"):
        print(f"[측정무효] {data['INVALID']}")
        return None, path
    return data, path


def bar(v, ref, width=18):
    """기준판 대비 비율을 막대로. ref의 2배를 폭 끝으로 잡는다."""
    if not ref:
        return ""
    n = max(0, min(width, int(round(v / (ref * 2) * width))))
    return "█" * n + "·" * (width - n)


def main() -> int:
    ap = argparse.ArgumentParser(description="기준판 대비 장별 밀도 비교(판정 없음)")
    ap.add_argument("week", help="주차 (예: 3 또는 3주차)")
    ap.add_argument("--top", type=int, default=15, help="가장 멀어진 장 몇 개를 볼까")
    a = ap.parse_args()

    data, path = load(a.week)
    if data is None:
        return 2
    raw = data.get("perSlide") or []
    cols = data.get("perSlideCols")
    if not raw or not cols:
        print(f"[입력없음] perSlide가 없다 — audit_all.js를 최신본으로 다시 돌려라: {path}")
        return 2
    # 증거는 크기를 줄이려고 «열 이름 + 배열 행»으로 실린다
    rows = [dict(zip(cols, r)) for r in raw]

    # 고정 슬라이드는 별도 좌표계라 비교 대상이 아니다(표지·도입·아젠다·간지·마무리).
    # ⚠️ **data-slide 접두어로 가르지 않는다.** 실측: 1주차에 `PAL1`·`PAL2`·`PAL3`라는
    #    본문 슬라이드가 있어 「P로 시작하면 간지」 규칙이 셋을 통째로 빼 버렸다.
    #    audit_render.js가 **클래스로 판정한** fixed 플래그를 쓴다.
    if "fixed" in (cols or []):
        body = [r for r in rows if not r.get("fixed")]
    else:
        print("[경고] 증거에 fixed 플래그가 없다(낡은 audit_all.js) — 고정 슬라이드가"
              " 비교에 섞인다. audit_all.js를 다시 돌려라.")
        body = rows
    if not body:
        body = rows

    n = len(body)
    avg_box = sum(r.get("boxes") or 0 for r in body) / n
    avg_chars = sum(r.get("txt") or 0 for r in body) / n
    vis = sum(1 for r in body if (r.get("gfx") or 0) > 0) / n

    print(f"덱: {data.get('url', '?')}")
    print(f"비교 대상: 본문 {n}장 (고정 슬라이드 제외)")
    print(f"기준판: {BASELINE['name']}\n")

    print(f"{'지표':<16}{'이 덱':>9}{'기준판':>9}   {'차이':>8}")
    print("-" * 48)
    for label, key, cur, base in (
        ("장당 박스 수", "boxes", avg_box, BASELINE["boxes"]),
        ("장당 글자 수", "chars", avg_chars, BASELINE["chars"]),
        ("시각자료 보유율", "visual_ratio", vis, BASELINE["visual_ratio"]),
    ):
        d = cur - base
        pctd = (d / base * 100) if base else 0
        fmt = "{:>9.2f}" if key != "chars" else "{:>9.0f}"
        print(f"{label:<16}" + fmt.format(cur) + fmt.format(base)
              + f"   {pctd:>+7.0f}%")

    print("\n참고 — 같은 축의 다른 집단(2주차 실측):")
    for k, v in REFERENCE.items():
        print(f"  {k:<18} 박스 {v['boxes']:>5.1f} · 글자 {v['chars']:>4} · 시각자료 {v['visual_ratio']:.2f}")

    # ── 가장 멀어진 장 ────────────────────────────────────────────────
    scored = sorted(body, key=lambda r: -(r.get("boxes") or 0))
    print(f"\n박스가 많은 장 상위 {min(a.top, len(scored))} (기준판 {BASELINE['boxes']})")
    print(f"{'ID':<12}{'박스':>5}{'시각':>5}{'글자':>6}{'잉크':>7}  기준판 대비")
    for r in scored[:a.top]:
        gfx = r.get("gfx") or 0
        mark = "  " if gfx else " ⚠"      # 박스 많은데 시각자료 0
        print(f"{str(r.get('id') or '')[:11]:<12}{r.get('boxes') or 0:>5}"
              f"{gfx:>5}{r.get('txt') or 0:>6}{(r.get('ink') or 0):>7.2f}  "
              f"{bar(r.get('boxes') or 0, BASELINE['boxes'])}{mark}")

    # ★ 가장 위험한 조합
    risky = [r for r in body if (r.get("boxes") or 0) >= 4 and (r.get("gfx") or 0) == 0]
    print(f"\n★ 박스 4개 이상 + 시각자료 0 : {len(risky)}장 / {n}장 ({len(risky)/n:.0%})")
    if risky:
        print("   박스로 화면을 채웠을 가능성 — 사람이 다시 본다(R-BOX-01 · R-DENS-03)")
        for r in risky[:a.top]:
            print(f"   · {r.get('id')}  박스 {r.get('boxes')} · 글자 {r.get('txt')} · 잉크 {(r.get('ink') or 0):.2f}")

    # 반비례 신호 — 2주차 기제의 재발 여부
    hi = [r for r in body if (r.get("boxes") or 0) >= avg_box]
    lo = [r for r in body if (r.get("boxes") or 0) < avg_box]
    if hi and lo:
        vh = sum(1 for r in hi if (r.get("gfx") or 0) > 0) / len(hi)
        vl = sum(1 for r in lo if (r.get("gfx") or 0) > 0) / len(lo)
        print(f"\n박스 많은 장의 시각자료 보유 {vh:.0%} vs 적은 장 {vl:.0%}")
        if vh < vl - 0.10:
            print("   ⚠️ **반비례한다** — 박스가 시각자료 자리를 밀어내는 2주차 기제가 재발했다.")
            print("      실측 선례: 박스 슬라이드 5.6%→22.6%(4배)인 동안 시각자료 50.0%→20.8%.")
        else:
            print("   반비례 신호 없음.")

    print("\nRESULT | 비교 | 판정 아님 — 임계로 막지 않는다. 사람이 볼 자리를 가리킬 뿐이다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
