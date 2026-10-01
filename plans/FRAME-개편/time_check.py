#!/usr/bin/env python3
"""FRAME 결정표 검사기 — 4시간 시간표·구도 반복·허브 링크를 기계로 판정한다(표준 라이브러리만).

사용: python plans/FRAME-개편/time_check.py <결정표.md>

입력 형식(잠김): 마크다운 표 하나. 헤더 줄
  | ID | PART | 블록 | 분 | 종류 | 제목(가) | 정보 모양 | 레이아웃 | 시각 자료 | 애니메이션 | 박스 예산 | 강조 | 이동 링크 |
표 밖 문단과 코드 펜스(``` · ~~~) 안은 무시한다. 열은 헤더 이름으로 찾는다.
  블록  1~4 또는 `허브`(PART 5 실습 장) · 분  숫자(소수 허용)
  종류  표지·운영·개념·체험·실습·메인·허브·전환·마무리
  강조  쉼표로 나열한 형태 이름(mk · mk-solid · em-ink · em-line · em-num · em-tag · em-ring) 또는 `-`
  이동 링크  `→ID` 여러 개(쉼표) 또는 `-`

판정 7항목(각각 PASS/FAIL)
  1 시간 합계   블록 1~4 각각 ≤ 50분 · 1~4 총합 ≤ 200(상한 — 남는 시간은 여유로 둔다 · D34). 블록 `허브` 행은 합계에서 뺀다.
  2 허브 묶음   블록 `허브` 행을 ID 접두(첫 `-`까지, 예 `P1-`)별로 묶어 묶음마다 ≤ 15분.
  3 빈 칸·형식  ID·블록·분·종류·레이아웃이 비었거나(`-` 포함) 값 형식이 어긋나면 FAIL. ID 중복도 FAIL.
  4 레이아웃    `split` 포함 0 · 바로 앞 행과 같은 레이아웃 연속 0.
                예외: 종류가 둘 다 `실습`이거나 둘 다 `허브`이면 같은 실습 셸이라 연속을 허용한다.
  5 이동 링크   모든 `→ID` 대상이 표에 있다. 종류 `허브` 행마다 서로 다른 대상 수 = 4(허브 행 0개도 FAIL).
  6 강조        한 행의 형태 종류 ≤ 2 · 같은 조합이 5행 넘게 연속 0(강조 `-` 행은 연속을 끊는다) ·
                `mk` 포함 행 비율 ≤ 50%(강조 있는 행 기준). 형태 이름이 어휘 밖이면 FAIL.
  7 개념 시각   종류 `개념` 행의 시각 자료 칸이 `-`·빈 칸이 아니다(개념 행 0개도 FAIL).
항목 2·6·7의 「대상 0행」은 통과가 아니라 판정 불가라서 FAIL로 처리한다(눈먼 0 방지).

미판정 칸(계수에 넣지 않고 따로 센다): 필수 5칸의 빈 칸 · 블록/분/종류/강조 값 형식 오류 ·
  강조·이동 링크 칸이 아예 빈 경우(`-`로 취급) · 링크 칸 형식 오류.

출력 마지막 줄: `RESULT 판정 N행 · FAIL K항목 · 미판정 M칸`
종료코드: 0 FAIL 없음 · 1 FAIL 있음 · 2 표 없음/0행/필수 열 없음/읽기 실패(눈먼 0).
"""
import re
import sys
from collections import OrderedDict

KINDS = ["표지", "운영", "개념", "체험", "실습", "메인", "허브", "전환", "마무리"]
FORMS = ["mk", "mk-solid", "em-ink", "em-line", "em-num", "em-tag", "em-ring"]
BLOCKS = ["1", "2", "3", "4"]
HUB = "허브"
DASHES = {"-", "–", "—", "−"}
REQ_COLS = ["ID", "블록", "분", "종류", "레이아웃", "시각 자료", "강조", "이동 링크"]
MUST_FILL = ["ID", "블록", "분", "종류", "레이아웃"]
BLOCK_MAX = 50.0
TOTAL_TARGET = 200.0
TOTAL_TOL = 0.5
BUNDLE_MAX = 15.0
HUB_TARGETS = 4
MAX_FORMS_PER_ROW = 2
MAX_RUN = 5
MK_RATIO_MAX = 0.5
SAME_SHELL_KINDS = {"실습", HUB}
EPS = 1e-9

ITEM_NAMES = {
    1: "시간 합계",
    2: "허브 실습 묶음",
    3: "빈 칸·값 형식",
    4: "레이아웃 연속",
    5: "이동 링크",
    6: "강조",
    7: "개념 시각 자료",
}


def norm(s):
    s = s.strip().strip("`").strip()
    return re.sub(r"\s+", " ", s)


def is_dash(s):
    return s in DASHES


def is_blank(s):
    """필수 칸의 빈 칸 — 비었거나 대시뿐."""
    return s == "" or is_dash(s)


def fmt(x):
    return f"{x:g}"


def split_row(line):
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|") and not body.endswith("\\|"):
        body = body[:-1]
    return [norm(c.replace("\\|", "|")) for c in re.split(r"(?<!\\)\|", body)]


def is_sep_cells(cells, min_dash):
    return bool(cells) and all(re.fullmatch(r":?-{%d,}:?" % min_dash, c) for c in cells)


def parse_table(text):
    """첫 결정표를 찾아 (헤더, 행 목록, 메모)를 돌려준다. 없으면 (None, [], 메모)."""
    lines = text.splitlines()
    header = None
    idx = {}
    rows = []
    notes = []
    in_fence = False
    in_table = False
    first_after_header = False
    extra_tables = 0
    for no, raw in enumerate(lines, 1):
        st = raw.strip()
        if st.startswith("```") or st.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if not st.startswith("|"):
            in_table = False
            continue
        cells = split_row(st)
        if not in_table:
            if all(c in cells for c in REQ_COLS):
                if header is None:
                    header = cells
                    idx = {c: i for i, c in enumerate(cells)}
                    in_table = True
                    first_after_header = True
                else:
                    extra_tables += 1
            continue
        if first_after_header:
            first_after_header = False
            if is_sep_cells(cells, 1):
                continue
        if is_sep_cells(cells, 3):
            continue
        padded = (cells + [""] * len(header))[: len(header)]
        row = {"line": no, "mismatch": len(cells) != len(header), "ncells": len(cells)}
        for name, i in idx.items():
            row[name] = padded[i]
        rows.append(row)
    if header is None:
        # 헤더는 있는데 필수 열만 빠진 경우를 구분해 알린다
        for raw in lines:
            if raw.strip().startswith("|"):
                c = split_row(raw)
                if "ID" in c and "블록" in c:
                    miss = [x for x in REQ_COLS if x not in c]
                    if miss:
                        notes.append("헤더에 필수 열이 없다: " + ", ".join(miss))
                    break
    if extra_tables:
        notes.append(f"첫 표 뒤에 같은 헤더의 표 {extra_tables}개가 더 있다 — 판정하지 않았다")
    return header, rows, notes


def parse_links(cell):
    """(대상 목록, 형식 오류 여부). 대시·빈 칸은 ([], False)."""
    if cell == "" or is_dash(cell):
        return [], False
    targets = []
    bad = False
    for tok in re.split(r"[,，、]", cell):
        tok = tok.strip()
        if tok == "":
            continue
        m = re.fullmatch(r"→\s*(\S+)", tok)
        if m:
            targets.append(m.group(1))
        else:
            bad = True
    if not targets and not bad:
        bad = True
    return targets, bad


def parse_forms(cell):
    """(형태 집합, 어휘 밖 이름 목록)."""
    if cell == "" or is_dash(cell):
        return [], []
    forms = []
    unknown = []
    for tok in re.split(r"[,，、]", cell):
        tok = tok.strip().strip("`").lstrip(".").strip()
        if tok == "":
            continue
        if tok in FORMS:
            if tok not in forms:
                forms.append(tok)
        else:
            unknown.append(tok)
    return forms, unknown


def parse_minutes(cell):
    s = cell.rstrip("분").strip()
    if re.fullmatch(r"\d+(\.\d+)?", s):
        return float(s)
    return None


def label(r):
    rid = r["ID"] if r["ID"] and not is_dash(r["ID"]) else "ID 없음"
    return f"L{r['line']}[{rid}]"


def prefix_of(rid):
    m = re.match(r"^(.*?-)", rid)
    return m.group(1) if m else rid


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    if len(sys.argv) != 2:
        print("사용: python plans/FRAME-개편/time_check.py <결정표.md>")
        print("RESULT 판정 0행 · FAIL 0항목 · 미판정 0칸")
        return 2
    path = sys.argv[1]
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            text = f.read()
    except (OSError, UnicodeDecodeError) as e:
        print(f"입력 읽기 실패: {path} ({e})")
        print("RESULT 판정 0행 · FAIL 0항목 · 미판정 0칸")
        return 2

    header, rows, notes = parse_table(text)
    print(f"time_check — {path}")
    for n in notes:
        print(f"[경고] {n}")
    if header is None or not rows:
        why = "결정표 헤더를 찾지 못했다" if header is None else "표에 데이터 행이 0행이다"
        print(f"판정 불가: {why} (눈먼 0 — 통과가 아니다)")
        print("RESULT 판정 0행 · FAIL 0항목 · 미판정 0칸")
        return 2

    fails = {i: [] for i in ITEM_NAMES}
    info = {i: "" for i in ITEM_NAMES}
    unj = {"필수 빈 칸": 0, "형식 오류": 0, "강조·링크 빈 칸": 0}

    # ---- 행 정규화 ----
    ids_seen = {}
    for r in rows:
        r["kind"] = r["종류"]
        r["blk"] = r["블록"]
        r["min"] = parse_minutes(r["분"]) if not is_blank(r["분"]) else None
        r["forms"], r["unknown_forms"] = parse_forms(r["강조"])
        r["links"], r["bad_links"] = parse_links(r["이동 링크"])
        r["layout_key"] = "" if is_blank(r["레이아웃"]) else r["레이아웃"].lower()

    # ---- 3. 빈 칸·값 형식 ----
    f3 = fails[3]
    for r in rows:
        if r["mismatch"]:
            f3.append(f"{label(r)} 열 수 {r['ncells']}개 (헤더 {len(header)}개)")
        for col in MUST_FILL:
            if is_blank(r[col]):
                f3.append(f"{label(r)} {col} 빈 칸")
                unj["필수 빈 칸"] += 1
        if not is_blank(r["블록"]) and r["블록"] not in BLOCKS and r["블록"] != HUB:
            f3.append(f"{label(r)} 블록 값 「{r['블록']}」 (1~4 · 허브만 허용)")
            unj["형식 오류"] += 1
        if not is_blank(r["분"]) and r["min"] is None:
            f3.append(f"{label(r)} 분 값 「{r['분']}」 (숫자 아님)")
            unj["형식 오류"] += 1
        if not is_blank(r["종류"]) and r["종류"] not in KINDS:
            f3.append(f"{label(r)} 종류 값 「{r['종류']}」 (어휘 밖)")
            unj["형식 오류"] += 1
        if r["강조"] == "":
            unj["강조·링크 빈 칸"] += 1
        if r["이동 링크"] == "":
            unj["강조·링크 빈 칸"] += 1
        if not is_blank(r["ID"]):
            ids_seen.setdefault(r["ID"], []).append(r)
    for rid, rs in ids_seen.items():
        if len(rs) > 1:
            f3.append(f"ID 중복 「{rid}」 " + " · ".join(f"L{x['line']}" for x in rs))
    info[3] = (
        f"필수 5칸 빈 칸 {unj['필수 빈 칸']} · 형식 오류 {unj['형식 오류']} · "
        f"ID 중복 {sum(1 for rs in ids_seen.values() if len(rs) > 1)} (빈 칸은 미판정에도 센다)"
    )

    # ---- 1. 시간 합계 ----
    sums = OrderedDict((b, 0.0) for b in BLOCKS)
    counts = OrderedDict((b, 0) for b in BLOCKS)
    for r in rows:
        if r["blk"] in sums and r["min"] is not None:
            sums[r["blk"]] += r["min"]
            counts[r["blk"]] += 1
    total = sum(sums.values())
    for b in BLOCKS:
        if sums[b] > BLOCK_MAX + EPS:
            fails[1].append(f"블록 {b} 합계 {fmt(sums[b])}분 > {fmt(BLOCK_MAX)}분")
    if total > TOTAL_TARGET + TOTAL_TOL + EPS:   # D34(2026-10-01): 200분은 상한이다. 남는 시간은 여유로 둔다
        fails[1].append(f"블록 1~4 총합 {fmt(total)}분 > {fmt(TOTAL_TARGET)}분")
    hub_rows_minutes = sum(r["min"] for r in rows if r["blk"] == HUB and r["min"] is not None)
    info[1] = (
        " · ".join(f"블록{b} {fmt(sums[b])}분(여유 {fmt(BLOCK_MAX - sums[b])} · {counts[b]}행)" for b in BLOCKS)
        + f" · 총합 {fmt(total)}분 · 여유 {fmt(TOTAL_TARGET - total)}분 (기준: 각 ≤{fmt(BLOCK_MAX)} · 총 ≤{fmt(TOTAL_TARGET)} · "
        + f"허브 행 {fmt(hub_rows_minutes)}분은 합계에서 뺐다)"
    )

    # ---- 2. 허브 실습 묶음 ----
    bundles = OrderedDict()
    for r in rows:
        if r["blk"] == HUB and r["min"] is not None and not is_blank(r["ID"]):
            b = bundles.setdefault(prefix_of(r["ID"]), [0.0, 0])
            b[0] += r["min"]
            b[1] += 1
    if not bundles:
        fails[2].append("블록 `허브` 행 0개 — 판정 대상이 없다")
    for pre, (m, n) in bundles.items():
        if m > BUNDLE_MAX + EPS:
            fails[2].append(f"묶음 {pre} {fmt(m)}분 > {fmt(BUNDLE_MAX)}분")
    info[2] = (
        " · ".join(f"{pre} {fmt(m)}분({n}행)" for pre, (m, n) in bundles.items()) or "묶음 0"
    ) + f" (기준: 묶음마다 ≤{fmt(BUNDLE_MAX)}분)"

    # ---- 4. 레이아웃 ----
    n_split = n_same = n_exempt = 0
    for r in rows:
        if "split" in r["레이아웃"].lower():
            n_split += 1
            fails[4].append(f"{label(r)} 레이아웃 「{r['레이아웃']}」에 split")
    for prev, cur in zip(rows, rows[1:]):
        if not prev["layout_key"] or prev["layout_key"] != cur["layout_key"]:
            continue
        if prev["kind"] == cur["kind"] and cur["kind"] in SAME_SHELL_KINDS:
            n_exempt += 1
            continue
        n_same += 1
        fails[4].append(
            f"{label(prev)}→{label(cur)} 같은 레이아웃 「{cur['레이아웃']}」 연속 (종류 {prev['kind']}→{cur['kind']})"
        )
    info[4] = (
        f"split {n_split} · 연속 동일 {n_same} · 예외 허용 {n_exempt}쌍 "
        "(예외: 종류 `실습`끼리 · `허브` 행끼리는 같은 실습 셸이라 연속 허용)"
    )

    # ---- 5. 이동 링크 ----
    id_set = set(ids_seen)
    n_links = n_broken = 0
    for r in rows:
        if r["bad_links"]:
            fails[5].append(f"{label(r)} 이동 링크 형식 오류 「{r['이동 링크']}」 (`→ID` 나열 또는 `-`)")
            unj["형식 오류"] += 1
        for t in r["links"]:
            n_links += 1
            if t not in id_set:
                n_broken += 1
                fails[5].append(f"{label(r)} 끊긴 링크 →{t}")
    hub_rows = [r for r in rows if r["kind"] == HUB]
    if not hub_rows:
        fails[5].append("종류 `허브` 행 0개 — 링크 대상 수를 판정할 수 없다")
    hub_desc = []
    for r in hub_rows:
        distinct = list(OrderedDict.fromkeys(r["links"]))
        hub_desc.append(f"{label(r)} 대상 {len(distinct)}개")
        if len(distinct) != HUB_TARGETS:
            fails[5].append(f"{label(r)} 종류 `허브` 행의 링크 대상 {len(distinct)}개 (기준 {HUB_TARGETS})")
    info[5] = (
        f"링크 {n_links}개 · 끊김 {n_broken} · 허브 행 {len(hub_rows)}개"
        + (" (" + " · ".join(hub_desc) + ")" if hub_desc else "")
        + f" (기준: 끊김 0 · 허브 행 대상 수 {HUB_TARGETS})"
    )

    # ---- 6. 강조 ----
    for r in rows:
        if r["unknown_forms"]:
            fails[6].append(f"{label(r)} 강조 어휘 밖 「{', '.join(r['unknown_forms'])}」")
            unj["형식 오류"] += 1
        if len(r["forms"]) > MAX_FORMS_PER_ROW:
            fails[6].append(f"{label(r)} 한 행에 형태 {len(r['forms'])}종 ({', '.join(r['forms'])})")
    longest = 0
    i = 0
    while i < len(rows):
        combo = frozenset(rows[i]["forms"])
        if not combo:
            i += 1
            continue
        j = i
        while j + 1 < len(rows) and frozenset(rows[j + 1]["forms"]) == combo:
            j += 1
        run = j - i + 1
        longest = max(longest, run)
        if run > MAX_RUN:
            fails[6].append(
                f"{label(rows[i])}부터 같은 조합 「{', '.join(rows[i]['forms'])}」 {run}행 연속 (기준 ≤{MAX_RUN})"
            )
        i = j + 1
    with_emp = [r for r in rows if r["forms"]]
    mk_rows = [r for r in with_emp if "mk" in r["forms"]]
    if not with_emp:
        fails[6].append("강조가 있는 행 0개 — mk 비율을 판정할 수 없다")
        ratio_txt = "mk 비율 판정 불가(강조 행 0)"
    else:
        ratio = len(mk_rows) / len(with_emp)
        ratio_txt = f"mk {len(mk_rows)}/{len(with_emp)}행 = {ratio * 100:.1f}%"
        if ratio > MK_RATIO_MAX + EPS:
            fails[6].append(f"mk 비율 {ratio * 100:.1f}% > {MK_RATIO_MAX * 100:.0f}% ({len(mk_rows)}/{len(with_emp)}행)")
    info[6] = (
        f"{ratio_txt} · 같은 조합 최장 연속 {longest}행 "
        f"(기준: 행당 ≤{MAX_FORMS_PER_ROW}종 · 연속 ≤{MAX_RUN}행 · mk ≤{MK_RATIO_MAX * 100:.0f}% · 강조 `-` 행은 연속을 끊는다)"
    )

    # ---- 7. 개념 행 시각 자료 ----
    concept = [r for r in rows if r["kind"] == "개념"]
    if not concept:
        fails[7].append("종류 `개념` 행 0개 — 판정 대상이 없다")
    empty_vis = 0
    for r in concept:
        if is_blank(r["시각 자료"]):
            empty_vis += 1
            fails[7].append(f"{label(r)} 개념 행의 시각 자료 칸이 `{r['시각 자료'] or '빈 칸'}`")
    info[7] = f"개념 {len(concept)}행 · 시각 자료 없음 {empty_vis}행"

    # ---- 출력 ----
    n_fail = 0
    for i in ITEM_NAMES:
        ok = not fails[i]
        if not ok:
            n_fail += 1
        print(f"[{i}] {ITEM_NAMES[i]} · {'PASS' if ok else 'FAIL'} · {info[i]}")
        for msg in fails[i]:
            print(f"    - {msg}")
    m_total = sum(unj.values())
    print(
        f"미판정 {m_total}칸 = 필수 빈 칸 {unj['필수 빈 칸']} + 형식 오류 {unj['형식 오류']} + "
        f"강조·링크 빈 칸 {unj['강조·링크 빈 칸']} (FAIL/PASS 계수에는 넣지 않는다)"
    )
    print(f"RESULT 판정 {len(rows)}행 · FAIL {n_fail}항목 · 미판정 {m_total}칸")
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
