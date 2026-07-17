#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_session_docs.py — 세션 산출물 자동 검증 (1주차 파이프라인 계획 v2 §4.1)

자기선언 PASS를 대체하는 기계 검증. 리서치/콘텐츠 단계 산출물의
스키마·커버리지·D1~D6·출처ID 매핑·[미검증] 무결성·초안 형식·범위밖 diff를 점검한다.

검사 대상(파일명 규약: sessions/N주차/):
  자료/N주차_콘텐츠리서치_결과.md      — 교시(구간)별 8항목 ①~⑧
  자료/N주차_실습안_검증결과.md         — 실습별 13항목 ①~⑬
  자료/N주차_결정요청사항.md            — 6열 표 + D1~D6
  자료/N주차_출처레지스트리.md          — 출처ID 표(고유ID·URL·확인일·공신력·구간·접근)
  초안.md                               — 4열 표·아이콘 범례·0번 메타·관통 문장·(선택)

출처 모델: 모든 사실 문장은 [S-###] 출처ID로 레지스트리와 연결. 내부 설계 근거도
등록(예: S-000=v4 강의안설계). 커버리지 빈칸은 [미검증]/[미확인]/[확인불가]/[예외승인] 태그로만 허용.

사용:
  python scripts/verify_session_docs.py 1 --target 자료
  python scripts/verify_session_docs.py 1 --target 초안
  python scripts/verify_session_docs.py 1 --target all --base <git-ref>
  python scripts/verify_session_docs.py 1 --root <fixture-dir>     # 자체 테스트
종료코드: FAIL 있으면 1, 없으면 0.
"""
import argparse
import re
import subprocess
import sys
from fnmatch import fnmatch
from pathlib import Path

CIRC8 = "①②③④⑤⑥⑦⑧"
CIRC13 = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬"
ALLOW_TAGS = ("[미검증]", "[미확인]", "[확인불가]", "[예외승인")
SRC_REF = re.compile(r"\[(S-\d{3,})\]")

ALLOWLIST = {
    "자료": ["sessions/*주차/자료/*", ".omc/*"],
    "초안": ["sessions/*주차/초안.md", "sessions/*주차/자료/*집필노트*", ".omc/*"],
    "검토": ["sessions/*주차/검토보고_*.md", ".omc/*"],
}

results = []  # (check, status, detail)


def add(check, status, detail=""):
    results.append((check, status, detail))


def read(p):
    try:
        return p.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        return None


def split_sections(text, hashes=2):
    hre = re.compile(r"^(#{1,6})\s+(.*)$")
    out, h, body = [], None, []
    for line in text.splitlines():
        m = hre.match(line)
        if m and len(m.group(1)) == hashes:
            if h is not None:
                out.append((h, "\n".join(body)))
            h, body = m.group(2).strip(), []
        elif h is not None:
            body.append(line)
    if h is not None:
        out.append((h, "\n".join(body)))
    return out


def has_meta(text):
    return ("작성일" in text) and ("대상" in text) and ("기준" in text)


def missing_markers(body, markers):
    return [c for c in markers if c not in body]


def empty_markers(body, markers):
    pos = sorted((i, ch) for i, ch in enumerate(body) if ch in markers)
    empt = []
    for idx, (p, ch) in enumerate(pos):
        end = pos[idx + 1][0] if idx + 1 < len(pos) else len(body)
        chunk = body[p + 1:end]
        if any(t in chunk for t in ALLOW_TAGS):
            continue
        txt = re.sub(r"[\*\_`>#\-\|:：\.\s]", "", chunk)
        if len(txt) < 15:
            empt.append(ch)
    return empt


def parse_tables(text):
    tbls, rows = [], []
    for line in text.splitlines():
        if re.match(r"^\s*\|", line):
            rows.append([c.strip() for c in line.strip().strip("|").split("|")])
        elif rows:
            tbls.append(rows)
            rows = []
    if rows:
        tbls.append(rows)
    clean = []
    for t in tbls:
        clean.append([r for r in t if not all(re.fullmatch(r":?-{2,}:?", (c or "").strip()) for c in r)])
    return clean


def check_research_result(text):
    tag = "콘텐츠리서치"
    if not has_meta(text):
        add(f"{tag}:메타헤더", "FAIL", "작성일·기준·대상 헤더 누락")
    else:
        add(f"{tag}:메타헤더", "PASS")
    secs = [(h, b) for h, b in split_sections(text) if "구간" in h]
    if len(secs) < 6:
        add(f"{tag}:구간수", "FAIL", f"구간 섹션 {len(secs)}개(<6)")
    else:
        add(f"{tag}:구간수", "PASS", f"{len(secs)}구간")
    for h, b in secs:
        miss = missing_markers(b, CIRC8)
        emp = empty_markers(b, CIRC8)
        if miss:
            add(f"{tag}:{h}:8항목", "FAIL", f"누락 {''.join(miss)}")
        elif emp:
            add(f"{tag}:{h}:8항목", "FAIL", f"빈칸 {''.join(emp)}")
        else:
            add(f"{tag}:{h}:8항목", "PASS")
        if "③" in b and not SRC_REF.search(b):
            add(f"{tag}:{h}:출처", "FAIL", "③ 사실 확인에 출처ID [S-###] 없음")
    if "탈락" not in text:
        add(f"{tag}:탈락로그", "WARN", "부록 탈락 자료 로그 없음")


def check_practice(text):
    tag = "실습검증"
    if not has_meta(text):
        add(f"{tag}:메타헤더", "FAIL", "메타 헤더 누락")
    else:
        add(f"{tag}:메타헤더", "PASS")
    secs = [(h, b) for h, b in split_sections(text) if "실습" in h]
    if not secs:
        add(f"{tag}:실습섹션", "FAIL", "실습 섹션(## …실습…) 0개")
    else:
        add(f"{tag}:실습섹션", "PASS", f"{len(secs)}개")
    for h, b in secs:
        miss = missing_markers(b, CIRC13)
        emp = empty_markers(b, CIRC13)
        if miss:
            add(f"{tag}:{h}:13항목", "FAIL", f"누락 {''.join(miss)}")
        elif emp:
            add(f"{tag}:{h}:13항목", "FAIL", f"빈칸 {''.join(emp)}")
        else:
            add(f"{tag}:{h}:13항목", "PASS")
    if "[미검증]" not in text:
        add(f"{tag}:미검증표기", "WARN", "실측 위임 [미검증] 표기가 하나도 없음")
    else:
        add(f"{tag}:미검증표기", "PASS")
    if "사람입력" not in text and "실측/" not in text:
        add(f"{tag}:사람입력참조", "WARN", "사람 실측 파일(자료/실측/…사람입력.md) 참조 없음")
    else:
        add(f"{tag}:사람입력참조", "PASS")


def check_decision(text):
    tag = "결정요청"
    if not has_meta(text):
        add(f"{tag}:메타헤더", "FAIL", "메타 헤더 누락")
    else:
        add(f"{tag}:메타헤더", "PASS")
    dec_tbl = None
    for t in parse_tables(text):
        if t and any("결정" in c for c in t[0]) and any("후보" in c for c in t[0]):
            dec_tbl = t
            break
    if not dec_tbl:
        add(f"{tag}:표", "FAIL", "결정 항목·후보 6열 표 없음")
        return
    ncol = len(dec_tbl[0])
    if ncol < 6:
        add(f"{tag}:표열수", "FAIL", f"{ncol}열(<6): 결정항목|후보|장점|위험|추천|근거")
    else:
        add(f"{tag}:표열수", "PASS", f"{ncol}열")
    body = "\n".join("|".join(r) for r in dec_tbl[1:])
    missing_d = [f"D{i}" for i in range(1, 7) if not re.search(rf"\bD{i}\b", body)]
    if missing_d:
        add(f"{tag}:D1~D6", "FAIL", f"누락 {', '.join(missing_d)}")
    else:
        add(f"{tag}:D1~D6", "PASS")


def check_registry(text):
    tag = "출처레지스트리"
    ids = set()
    reg_tbl = None
    for t in parse_tables(text):
        if t and any(("출처" in c or "ID" in c) for c in t[0]):
            reg_tbl = t
            break
    if not reg_tbl:
        add(f"{tag}:표", "FAIL", "출처ID 표 없음")
        return ids
    if len(reg_tbl[0]) < 6:
        add(f"{tag}:표열수", "FAIL", f"{len(reg_tbl[0])}열(<6): ID|URL|확인일|공신력|구간|접근")
    else:
        add(f"{tag}:표열수", "PASS", f"{len(reg_tbl[0])}열")
    empty_rows = 0
    for r in reg_tbl[1:]:
        m = re.match(r"(S-\d{3,})", r[0])
        if m:
            ids.add(m.group(1))
        if any((not (c or "").strip()) for c in r[:6]) and not any(any(tg in c for tg in ALLOW_TAGS) for c in r):
            empty_rows += 1
    add(f"{tag}:ID수집", "PASS" if ids else "WARN", f"{len(ids)}개 ID")
    if empty_rows:
        add(f"{tag}:빈칸", "FAIL", f"빈 셀 행 {empty_rows}개")
    return ids


def check_draft(text):
    tag = "초안"
    ok = True
    if not any(("슬라이드 제목" in ln and "본문" in ln) for ln in text.splitlines()):
        add(f"{tag}:4열표", "FAIL", "헤더(#·슬라이드 제목·본문 문구·비유·멘트) 없음")
        ok = False
    else:
        add(f"{tag}:4열표", "PASS")
    if "💬" in text and "🗣" in text:
        add(f"{tag}:아이콘범례", "PASS")
    else:
        add(f"{tag}:아이콘범례", "WARN", "아이콘 범례(💬/👀/🗣) 불완전")
    if "덱 기본 정보" in text or "0. 덱" in text:
        add(f"{tag}:0번메타", "PASS")
    else:
        add(f"{tag}:0번메타", "WARN", "0번 덱 기본 정보 표 없음")
    n_pierce = len(re.findall(r"사람이 (검토|결정)", text))
    add(f"{tag}:관통문장", "PASS" if n_pierce else "WARN", f"관통 문장 {n_pierce}회")
    add(f"{tag}:선택태그", "PASS" if "(선택)" in text else "WARN", "(선택) 태그 유무")
    return ok


def check_scope(base, target):
    try:
        out = subprocess.run(
            ["git", "diff", "--name-status", base],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
    except (OSError, subprocess.SubprocessError) as e:
        add("범위diff", "WARN", f"git diff 실행 불가: {e}")
        return
    allow = ALLOWLIST.get(target, [])
    if not allow:
        add("범위diff", "SKIP", f"target={target} allowlist 없음")
        return
    off = []
    for line in out.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        st, path = parts[0], parts[-1]
        if not any(fnmatch(path, a) or path.startswith(a.rstrip("*")) for a in allow):
            off.append(f"{st} {path}")
    if off:
        add("범위diff", "WARN", "범위밖 변경: " + "; ".join(off[:8]))
    else:
        add("범위diff", "PASS", "allowlist 내")


def main():
    try:  # Windows 콘솔(cp949)에서 —·이모지·한글 출력 깨짐/크래시 방지
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("week", help="주차 번호 (예: 1)")
    ap.add_argument("--target", default="all", choices=["자료", "초안", "all"])
    ap.add_argument("--root", default=None, help="저장소 루트 재정의(자체 테스트용)")
    ap.add_argument("--base", default=None, help="범위밖 diff 비교 git ref")
    args = ap.parse_args()

    root = Path(args.root) if args.root else Path(__file__).resolve().parent.parent
    wk = args.week
    sess = root / "sessions" / f"{wk}주차"
    data = sess / "자료"
    files = {
        "result": data / f"{wk}주차_콘텐츠리서치_결과.md",
        "practice": data / f"{wk}주차_실습안_검증결과.md",
        "decision": data / f"{wk}주차_결정요청사항.md",
        "registry": data / f"{wk}주차_출처레지스트리.md",
        "draft": sess / "초안.md",
    }

    reg_ids, used_refs = set(), set()

    if args.target in ("자료", "all"):
        for key, chk in (("result", check_research_result), ("practice", check_practice), ("decision", check_decision)):
            txt = read(files[key])
            if txt is None:
                add(f"파일:{files[key].name}", "FAIL", "파일 없음")
            else:
                chk(txt)
                if key == "result":
                    used_refs |= {m.group(1) for m in SRC_REF.finditer(txt)}
        rtxt = read(files["registry"])
        if rtxt is None:
            add(f"파일:{files['registry'].name}", "FAIL", "파일 없음")
        else:
            reg_ids = check_registry(rtxt)

    if args.target in ("초안", "all"):
        dtxt = read(files["draft"])
        if dtxt is None:
            add(f"파일:{files['draft'].name}", "SKIP" if args.target == "all" else "FAIL", "파일 없음")
        else:
            check_draft(dtxt)
            used_refs |= {m.group(1) for m in SRC_REF.finditer(dtxt)}

    # 출처ID 상호 참조: 사용된 [S-###]가 레지스트리에 실재하는가
    if used_refs or reg_ids:
        dangling = sorted(used_refs - reg_ids)
        if dangling:
            add("출처매핑:참조해소", "FAIL", f"레지스트리에 없는 출처ID {', '.join(dangling)}")
        else:
            add("출처매핑:참조해소", "PASS", f"참조 {len(used_refs)}개 전부 해소")

    if args.base:
        check_scope(args.base, "자료" if args.target == "all" else args.target)

    # 출력
    order = {"FAIL": 0, "WARN": 1, "SKIP": 2, "PASS": 3}
    results.sort(key=lambda r: order.get(r[1], 9))
    n = {"FAIL": 0, "WARN": 0, "PASS": 0, "SKIP": 0}
    print(f"=== verify_session_docs {wk}주차 (target={args.target}) ===")
    for check, status, detail in results:
        n[status] = n.get(status, 0) + 1
        line = f"{status:4} | {check}"
        if detail:
            line += f" — {detail}"
        print(line)
    print(f"--- FAIL={n['FAIL']} WARN={n['WARN']} PASS={n['PASS']} SKIP={n['SKIP']} ---")
    result = "FAIL" if n["FAIL"] else "PASS"
    print(f"RESULT | {result}")
    sys.exit(1 if n["FAIL"] else 0)


if __name__ == "__main__":
    main()
