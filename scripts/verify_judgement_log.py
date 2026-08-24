#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""판단 기록 정합 검사 (R-JUDGE-01 게이트) — 집필노트의 출처 추적표·재료 처분표.

왜 필요한가
-----------
2026-07-29에 판단 기록을 `사실/창작` 2분류에서 **F / S / D1 / D2 / E·V** 5분류로 바꿨다.
그중 둘은 기록되지 않으면 아무도 검출할 수 없다:
  - **D2**(분류 기준 생성·축 설계·인과 도출) — 원 사실에 없던 **새 주장**이라 F와 같은
    강도로 검증해야 하는데, 근거를 안 적으면 검증 대상인지조차 알 수 없다.
  - **S**(생략) — 추가는 눈에 띄지만 생략은 안 띈다. 「재료 처분표」가 유일한 검사기다.

무엇을 검사하나
--------------
  FAIL  D2 행에 도출 근거(비고)가 없음        — 무근거 주장이다
  FAIL  처분표 행에 처분값(사용/대체/보류) 없음 — 기록의 목적이 처분이다
  FAIL  등급이 «필수»인데 처분이 «보류»        — 필수 진술은 보류 불가(chunk-schema.md)
  FAIL  등급이 «필수»·처분이 «대체»인데 실현 위치 없음
  WARN  출처 추적표에 S 행이 있음              — S는 처분표에만 기록한다(중복 금지)
  WARN  처분표에 보류 행이 하나도 없음         — 정말 아무것도 안 뺐는지 사람이 대조
  WARN  구판 «사실/창작» 열                    — 강제 마이그레이션하지 않는다
  WARN  4열 계약과 셀 수가 다른 행             — 셀 안의 `|`일 수 있어 FAIL로 올리지 않는다

엣지케이스
---------
- 집필노트가 **없으면 SKIP**한다. 부재는 `verify_draft_quality.py` R-QD-05 소관이고,
  여기서 또 FAIL하면 같은 결함이 두 곳에서 울린다.
- 표 헤더의 열 이름으로 인덱스를 찾는다 — 열 순서가 바뀌어도 동작한다.
- 표가 아예 없으면 그 검사만 SKIP하고 나머지는 계속한다.

사용
----
    python scripts/verify_judgement_log.py 2
    python scripts/verify_judgement_log.py 2 --note <경로>

종료코드: 0 통과/SKIP · 1 FAIL
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
except Exception:
    CP = None

DISPOSITIONS = ("사용", "대체", "보류")
RESULTS = []


def rec(rule, level, msg):
    RESULTS.append((rule, level, msg))


def tables(text):
    """(섹션 제목, 헤더셀, 데이터행목록, 상위 헤딩 breadcrumb) 목록. 마크다운 표를
    섹션과 함께 뽑는다. 앞 3개는 종전과 완전히 같다(check_tracking·check_disposition
    계약 불변). 4번째 breadcrumb는 0판정 가드 전용 추가 필드 — 이 표를 감싸는
    모든 상위 헤딩을 레벨 순으로 ' / '로 이어붙인 문자열이다. 표가 소제목
    (예: `### 4구간`) 바로 아래 있으면 section은 그 소제목뿐이지만, breadcrumb는
    그 위 절(`## 1. 출처 추적표`)까지 포함한다 — 절 제목은 헤더 어휘보다 훨씬 안
    바뀌므로(2주차 실측: 표 헤더 「판단」은 5곳, 절 제목 「출처 추적표」는 1곳뿐이라
    바뀔 표면이 좁다) 헤더 라우팅이 실패했을 때 마지막으로 기댈 근거가 된다."""
    out, section = [], ""
    header, rows = None, []
    stack = []  # [(level:int, text:str)] — 현재 열려 있는 헤딩 경로
    breadcrumb = ""
    for line in text.splitlines():
        h = re.match(r"^(#{1,6})\s+(.*)$", line)
        if h:
            if header:
                out.append((section, header, rows, breadcrumb))
            section, header, rows = h.group(2).strip(), None, []
            level = len(h.group(1))
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, section))
            breadcrumb = " / ".join(t for _, t in stack)
            continue
        s = line.strip()
        if not s.startswith("|"):
            if header and s == "":
                continue
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if re.match(r"^\|?[\s:\-|]+\|?$", s):          # 구분선
            continue
        if header is None:
            header, rows = cells, []
        else:
            rows.append(cells)
    if header:
        out.append((section, header, rows, breadcrumb))
    return out


def col(header, *names):
    for i, h in enumerate(header):
        clean = h.replace("*", "").strip()
        for n in names:
            if n in clean:
                return i
    return -1


def cell(row, i):
    return row[i].strip() if 0 <= i < len(row) else ""


def check_tracking(section, header, rows):
    """출처 추적표 — 판단 열 5분류, D2 근거, S 중복."""
    ji = col(header, "판단")
    if ji < 0:
        if col(header, "사실/창작") >= 0:
            rec("R-JUDGE-01", "WARN",
                "구판 «사실/창작» 열입니다 — 5분류(F/S/D1/D2/E·V)로 옮기면 D2·S가 추적됩니다. "
                "강제 마이그레이션은 하지 않습니다")
        return
    ni = col(header, "비고")
    si = col(header, "슬라이드#", "슬라이드 #", "#")
    d2 = s_rows = 0
    for r in rows:
        if len(r) != len(header):
            rec("R-JUDGE-01", "WARN",
                "열 수 불일치(%d/%d) — 셀 안의 `|`일 수 있어 FAIL로 올리지 않습니다: %s"
                % (len(r), len(header), " | ".join(r)[:70]))
            continue
        judged = cell(r, ji).replace(" ", "")
        if not judged:
            continue
        if "D2" in judged:
            d2 += 1
            if not cell(r, ni):
                rec("R-JUDGE-01", "FAIL",
                    "D2 행에 도출 근거(비고)가 없습니다 — 근거를 못 적으면 그 행은 D2가 "
                    "아니라 **무근거 주장**입니다: %s" % cell(r, si) or "(번호 없음)")
        if re.search(r"(^|,)S($|,)", judged):
            s_rows += 1
    if s_rows:
        rec("R-JUDGE-01", "WARN",
            "출처 추적표에 S(생략) 행 %d건 — S는 「재료 처분표」에만 기록합니다. "
            "두 곳에 적으면 한쪽만 고쳐질 때 조용히 어긋납니다" % s_rows)
    rec("R-JUDGE-01", "PASS", "출처 추적표 판독: 데이터 %d행 · D2 %d행" % (len(rows), d2))


def check_disposition(section, header, rows):
    """재료 처분표 — 처분값 존재, 필수 등급의 보류 금지."""
    gi = col(header, "등급")
    di = col(header, "처분", "사용/대체/보류")
    li = col(header, "실현")
    mi = col(header, "재료", "소재")
    if di < 0:
        rec("R-JUDGE-01", "WARN", "「%s」에 처분 열이 없습니다 — 등급·처분 스키마를 확인하세요" % section)
        return
    holds = required = 0
    for r in rows:
        if len(r) != len(header):
            continue
        name = cell(r, mi) or "(이름 없음)"
        disp = cell(r, di).replace(" ", "")
        grade = cell(r, gi).replace("*", "").strip()
        if not disp:
            rec("R-JUDGE-01", "FAIL", "처분값(사용/대체/보류)이 없습니다: %s" % name)
            continue
        if not any(d in disp for d in DISPOSITIONS):
            rec("R-JUDGE-01", "WARN", "처분값이 규약 밖입니다(%s): %s" % (disp, name))
        if "보류" in disp:
            holds += 1
        if "필수" in grade:
            required += 1
            if "보류" in disp:
                rec("R-JUDGE-01", "FAIL",
                    "등급 «필수»인데 처분이 «보류»입니다 — 필수 진술은 표현을 바꿔도 되지만 "
                    "**보류는 불가능**합니다(chunk-schema.md): %s" % name)
            elif "대체" in disp and li >= 0 and not cell(r, li):
                rec("R-JUDGE-01", "FAIL",
                    "등급 «필수»·처분 «대체»인데 실현 위치(슬라이드#)가 없습니다 — "
                    "어디에 남았는지 확인할 수 없습니다: %s" % name)
    if rows and holds == 0:
        rec("R-JUDGE-01", "WARN",
            "처분표에 «보류» 행이 하나도 없습니다 — 정말 아무것도 빼지 않았는지 회수 청크와 "
            "대조하세요. **생략은 기록하지 않으면 검출되지 않습니다**")
    rec("R-JUDGE-01", "PASS",
        "「%s」 판독: %d행 · 필수 %d · 보류 %d" % (section, len(rows), required, holds))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("week")
    ap.add_argument("--note")
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args()

    if a.note:
        note = a.note
    else:
        sess = CP.session_dir(a.week) if CP else os.path.join("sessions", "%s주차" % a.week)
        cand = glob.glob(os.path.join(sess, "자료", "*집필노트*.md"))
        note = cand[0] if cand else os.path.join(sess, "자료", "%s주차_콘텐츠_집필노트.md" % a.week)

    if not os.path.isfile(note):
        print("SKIP  집필노트 없음: %s" % note)
        print("      (부재는 verify_draft_quality.py R-QD-05 소관입니다 — 여기서 또 울리지 않습니다)")
        return 0

    text = io.open(note, encoding="utf-8").read()
    print("집필노트: %s" % os.path.relpath(note))
    print("-" * 74)

    # ── 0판정 가드(2026-08-24) ──────────────────────────────────────────
    # 아래 라우팅은 헤더 어휘("판단"/"처분"/"등급")로만 표를 찾는다. 어휘가
    # 바뀌면 check_tracking/check_disposition이 아예 호출되지 않는데, 그 표가
    # 있었다는 사실 자체가 사라진 채 "표를 못 찾았다" WARN만 남는다 — 이 WARN은
    # "원래 표가 없는 문서"와 "표는 있는데 헤더 어휘가 바뀐 문서"를 구분하지
    # 못한 채 둘 다 exit 0으로 통과시킨다. 절 제목(section)은 헤더보다 훨씬
    # 안 바뀐다 — 「출처 추적표」·「재료 처분표」는 이 파일의 docstring·주석이
    # 반복해 쓰는 고유명사다. 헤더 라우팅에 실패한 표라도 절 제목에 그 낱말이
    # 있으면 "표가 있는데 못 읽었다"로 승격한다(FAIL — nf에 반영돼 기존 exit
    # 코드 규약을 그대로 재사용한다. 새 심각도 체계를 만들지 않는다).
    TRACKING_HINTS = ("추적", "출처")
    DISPOSITION_HINTS = ("처분", "재료")

    seen_tracking = seen_disp = False
    judged_tables = 0
    unmatched = []  # [(section, breadcrumb, kind, header)] — 상위 절 힌트는 있으나 헤더 라우팅 실패
    for section, header, rows, breadcrumb in tables(text):
        joined = " ".join(header)
        if "판단" in joined or "사실/창작" in joined:
            seen_tracking = True
            judged_tables += 1
            check_tracking(section, header, rows)
        elif "처분" in joined or "등급" in joined:
            seen_disp = True
            judged_tables += 1
            check_disposition(section, header, rows)
        elif any(h in breadcrumb for h in TRACKING_HINTS):
            unmatched.append((section, breadcrumb, "출처 추적표", header))
        elif any(h in breadcrumb for h in DISPOSITION_HINTS):
            unmatched.append((section, breadcrumb, "재료 처분표", header))

    for section, breadcrumb, kind, header in unmatched:
        rec("R-JUDGE-01", "FAIL",
            "「%s」 절의 표가 %s로 보이나(상위 절 「%s」 기준) 헤더 어휘(판단/사실창작 "
            "또는 처분/등급)를 찾지 못해 판독하지 못했습니다 — 계수 실패(눈먼 0 방지). "
            "헤더: %s" % (section, kind, breadcrumb, " | ".join(header)))

    if not seen_tracking:
        rec("R-JUDGE-01", "WARN", "출처 추적표를 찾지 못했습니다(판단 열 기준)")
    if not seen_disp:
        rec("R-JUDGE-01", "WARN",
            "「재료 처분표」를 찾지 못했습니다 — 생략(S)과 필수 진술을 검사할 수 없습니다")

    mark = {"FAIL": "✗", "WARN": "△", "PASS": "✓"}
    for rule, lvl, msg in RESULTS:
        print("[%s] %s %s: %s" % (lvl, mark[lvl], rule, msg))
    nf = sum(1 for _, l, _ in RESULTS if l == "FAIL")
    nw = sum(1 for _, l, _ in RESULTS if l == "WARN")
    np_ = sum(1 for _, l, _ in RESULTS if l == "PASS")
    print("-" * 74)
    print("요약: FAIL %d · WARN %d · PASS %d" % (nf, nw, np_))
    print("판정 %d건 · 미판정 %d건" % (judged_tables, len(unmatched)))
    return 1 if nf else 0


if __name__ == "__main__":
    sys.exit(main())
