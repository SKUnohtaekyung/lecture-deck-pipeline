#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""필수 진술 잔존 검사 (R-REQ-01) — 개념KB의 `필수 진술:`이 완성 덱 화면에 남았는가.

왜 필요한가
-----------
2026-07-28에 `[C-하네스구성요소]`의 유보 "이 목록은 확정된 표준이 아닙니다"가 완성
슬라이드에서 사라졌다. 인용은 정확했고 출처 ID도 붙어 있었으므로 **기존 게이트는 전부
통과했다** — 현 파이프라인이 「쓴 것」만 검사하고 「뺀 것」은 검사하지 않기 때문이다.
이 스크립트가 그 공백을 메운다.

무엇을 검사하나
--------------
개념KB에서 `필수 진술:`을 모아, 각 진술의 **핵심어**가 덱의 가시 텍스트에 남았는지 본다.
**완전일치를 요구하지 않는다** — 필수 진술은 "표현은 바꿔도 뜻은 남긴다"가 계약이므로
문장을 그대로 찾으면 정당한 재작성까지 위반으로 잡는다.

판정 3단계:
  충족   — 핵심어의 과반이 화면에 있다
  부분   — 일부만 있다(사람 확인)
  미검출 — 하나도 없다(사람 확인 · `--strict`면 FAIL)

⚠️ **기본은 WARN이다.** 핵심어 매칭은 근사이므로 자동 FAIL은 오탐 위험이 크다. 대신
미검출분을 **사람 확인 목록으로 반드시 출력**한다 — 조용히 넘어가는 것만은 막는다.

제외 규칙 (엣지케이스)
--------------------
- `범위:인접` 청크는 **검사하지 않는다.** 인접 개념(G9)은 애초에 화면이 아니라 강사
  답변용이라, 화면에 없는 것이 정상이다. 넣으면 전부 오탐이 된다.
- 발표자 노트 HTML은 화면이 아니다. 다만 "노트에는 있다"를 따로 표시한다 — 화면에서
  노트로 **이주**한 것과 통째로 사라진 것은 원인이 다르기 때문이다.
- HTML 주석(`<!-- 발표노트: … -->`)·`<script>`·`<style>`은 화면이 아니므로 제거한다.
- 개념KB가 없거나 `필수 진술:`이 0건이면 SKIP한다(아직 승격하지 않은 주차 — 1주차 등).

사용
----
    python scripts/verify_required_statements.py 2
    python scripts/verify_required_statements.py 2 --deck <경로> --notes <경로> --strict

종료코드: 0 통과/SKIP · 1 미검출이 있고 --strict
"""
import io
import os
import re
import sys
import glob
import argparse

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import _course_paths as CP
except Exception:                                    # 해석기 없이도 최소 동작
    CP = None

# 한국어 조사·어미 꼬리. 형태소 분석기 없이(의존성 0) 근사한다 — 긴 것부터 벗긴다.
_TAILS = ("입니다", "습니다", "합니다", "됩니다", "니다", "이다", "에서", "으로",
          "에게", "까지", "부터", "라고", "이라", "은", "는", "이", "가", "을", "를",
          "의", "에", "도", "만", "과", "와", "로", "며", "고")
# 의미 없는 고빈도어 — 핵심어에서 뺀다.
#
# ⚠️ **어미만 남은 토큰을 반드시 뺀다(2026-07-29 실측 수정).** 초판은 `합니다`·`됩니다`를
#    핵심어로 잡아, 회귀 fixture인 `[C-하네스구성요소]`의 유보를 «충족»으로 오판했다 —
#    그 유보는 덱에 실제로 **없었다.** 검사기가 자기 회귀 사례를 놓치면 존재 이유가 없다.
_STOP = {"것이", "것은", "그것", "이것", "저것", "수가", "때문", "그리고", "하지만",
         "그러나", "여기", "거기", "아니", "않다", "않습", "있다", "없다", "한다",
         "된다", "같다", "우리", "모두", "매우", "정말", "다시", "바로", "아직",
         # ── 어미·기능어(단독으로는 아무 뜻이 없다) ──
         "합니다", "됩니다", "입니다", "습니다", "니다", "이다", "하는", "되는",
         "있습니다", "없습니다", "아닙니다", "않습니다", "합니", "됩니", "것이지",
         "하면", "되면", "지만", "면서", "라고", "이라", "대로", "만큼", "처럼",
         "위해", "통해", "대해", "관해", "무엇", "어떤", "이런", "그런", "저런"}
# 어미로 끝나는 토큰은 명사구가 아니다 — 접미 패턴으로도 한 번 더 거른다.
_ENDING_RE = re.compile(r"(합니다|됩니다|입니다|습니다|니다|해야|하면|되면|지만|면서)$")


def _strip_tail(tok):
    for t in _TAILS:
        if len(tok) > len(t) + 1 and tok.endswith(t):
            return tok[: -len(t)]
    return tok


def keywords(sentence, want=4):
    """진술에서 핵심어를 뽑는다. `**강조**`가 있으면 그것을 최우선으로 쓴다."""
    bold = re.findall(r"\*\*([^*]+)\*\*", sentence)
    src = " ".join(bold) if bold else sentence
    src = re.sub(r"[«»\"'“”‘’(),.…·—\-–/]", " ", src)
    src = re.sub(r"\*\*|`", "", src)
    out = []
    for raw in src.split():
        tok = _strip_tail(raw.strip())
        if len(tok) < 2 or tok in _STOP or _ENDING_RE.search(tok):
            continue
        if not re.search(r"[가-힣A-Za-z0-9]", tok):
            continue
        if tok not in out:
            out.append(tok)
    out.sort(key=len, reverse=True)
    return out[:want]


def verdict(kws, hit):
    """충족/부분/미검출 판정.

    **앵커 규칙**: 가장 긴(가장 변별력 있는) 핵심어가 화면에 없으면 절대 «충족»이 아니다.
    짧고 흔한 낱말 여러 개가 우연히 걸려 과반을 넘기는 오탐을 막는다 — 초판이 정확히
    그렇게 회귀 fixture를 놓쳤다."""
    if not hit:
        return "미검출"
    anchor = kws[0]                                  # keywords()가 길이 내림차순 정렬
    if anchor in hit and len(hit) * 2 >= len(kws):
        return "충족"
    return "부분"


def visible_text(html):
    """화면에 실제로 보이는 텍스트만 남긴다(주석·스크립트·태그 제거 후 공백 제거)."""
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.S | re.I)
    t = re.sub(r"<!--.*?-->", " ", t, flags=re.S)       # 발표노트 주석은 화면이 아니다
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"&nbsp;|&#160;", " ", t)
    t = re.sub(r"&[a-zA-Z#0-9]+;", "", t)
    return re.sub(r"\s+", "", t)


def collect_statements(kb_text):
    """(슬러그, 진술, 인접여부) 목록."""
    out = []
    for chunk in re.split(r"(?=\n#{1,4}\s*\[C-)", kb_text):
        m = re.match(r"\n#{1,4}\s*\[(C-[^\]]+)\]", chunk)
        if not m:
            continue
        adjacent = bool(re.search(r"범위:\s*인접", chunk))
        for sm in re.finditer(r"^-\s*\*\*필수 진술:\*\*\s*(.+)$", chunk, re.M):
            stmt = sm.group(1).strip()
            if stmt and not stmt.startswith("…"):
                out.append((m.group(1), stmt, adjacent))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("week")
    ap.add_argument("--deck")
    ap.add_argument("--notes")
    ap.add_argument("--kb")
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args()

    sess = a.kb and os.path.dirname(a.kb) or (
        CP.session_dir(a.week) if CP else os.path.join("sessions", "%s주차" % a.week))
    kb = a.kb or os.path.join(sess, "자료", "%s주차_개념KB.md" % a.week)
    if not os.path.isfile(kb):
        print("SKIP  개념KB 없음: %s" % kb)
        return 0

    stmts = collect_statements(io.open(kb, encoding="utf-8").read())
    core = [s for s in stmts if not s[2]]
    adj = [s for s in stmts if s[2]]
    if not core:
        print("SKIP  `필수 진술:` 0건 — 아직 승격하지 않은 주차입니다 (인접 %d건은 애초에 검사 대상 아님)"
              % len(adj))
        return 0

    decks = [a.deck] if a.deck else sorted(
        p for p in glob.glob(os.path.join(sess, "*.html"))
        if "발표자노트" not in p and "리뷰" not in p)
    if not decks:
        print("SKIP  덱 없음: %s" % sess)
        return 0
    notes = [a.notes] if a.notes else sorted(glob.glob(os.path.join(sess, "*발표자노트*.html")))

    screen = "".join(visible_text(io.open(d, encoding="utf-8").read()) for d in decks)
    note_txt = "".join(visible_text(io.open(n, encoding="utf-8").read()) for n in notes if os.path.isfile(n))

    print("개념KB: %s" % os.path.relpath(kb))
    print("덱    : %s" % ", ".join(os.path.relpath(d) for d in decks))
    print("필수 진술 %d건(코어) · 인접 %d건은 검사 제외" % (len(core), len(adj)))
    print("-" * 74)

    missing, partial, met = [], [], []
    for slug, stmt, _ in core:
        kws = keywords(stmt)
        if not kws:
            continue
        hit = [k for k in kws if k.replace(" ", "") in screen]
        in_note = [k for k in kws if k.replace(" ", "") in note_txt]
        rec = (slug, stmt, kws, hit, in_note)
        v = verdict(kws, hit)
        (met if v == "충족" else partial if v == "부분" else missing).append(rec)

    for slug, stmt, kws, hit, _ in met:
        print("충족  [%s] %d/%d — %s" % (slug, len(hit), len(kws), stmt[:52]))
    for slug, stmt, kws, hit, note in partial:
        print("부분  [%s] %d/%d — %s" % (slug, len(hit), len(kws), stmt[:52]))
        print("      찾음=%s · 못찾음=%s%s"
              % (hit, [k for k in kws if k not in hit],
                 " · 노트에는 있음" if note else ""))

    # 사람 확인 목록에는 «미검출»뿐 아니라 «부분»도 넣는다 — 부분은 정의상 **앵커(가장
    # 변별력 있는 핵심어)가 화면에 없다**는 뜻이고, 그게 바로 유보가 사라졌을 때의 모습이다.
    # 초판은 부분을 목록에서 빼, 회귀 fixture가 화면에 표시만 되고 «확인해야 할 것»으로는
    # 올라오지 않았다.
    need = missing + partial
    if need:
        print()
        print("★ 사람 확인 목록 %d건 (미검출 %d · 부분 %d)" % (len(need), len(missing), len(partial)))
        print("  `필수 진술`은 표현을 바꿔도 되지만 **보류는 불가능**하다(chunk-schema.md).")
        print("  아래가 정말 화면에 없다면 그 슬라이드는 미완성이다.")
        for slug, stmt, kws, hit, note in need:
            tag = "미검출" if not hit else "부분(앵커 없음)"
            print("  - [%s] %s — %s" % (slug, tag, stmt))
            print("      핵심어=%s · 화면에서 찾음=%s%s"
                  % (kws, hit or "없음",
                     "  ⚠️ 발표자 노트에는 있음(화면→노트 이주)" if note else ""))

    print("-" * 74)
    print("결과: 충족 %d · 부분 %d · 미검출 %d" % (len(met), len(partial), len(missing)))
    if missing and a.strict:
        print("      --strict: 미검출을 FAIL로 판정합니다.")
        return 1
    if missing or partial:
        print("      기본 모드는 WARN입니다 — 핵심어 매칭은 근사라 자동 FAIL은 오탐 위험이 큽니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
