#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_research_chunks.py — 개념 지식베이스(N주차_개념KB.md) 청크 깊이·검색계약 검증

리서치 산출물에 additive로 추가되는 청크+ID 지식베이스 파일
(sessions/N주차/자료/N주차_개념KB.md)의 청크별 최소 깊이와 grep 검색계약을 점검한다.
이 파일은 기존 3파일(콘텐츠리서치 결과·실습안 검증결과·결정요청사항) 스키마에
더해지는 additive 산출물이며, 아직 만들어지지 않은 주차에는 존재하지 않을 수 있다.

검사 항목(청크 = "## [C-...]" 헤딩 단위):
  - 청크 바로 아래 메타주석 `<!-- 구간:… | 유형:… | 우선:… | 출처:… | 태그:… -->` 존재
    (구간·유형·출처 키 필수)
  - 비유 ≥2 (`**비유`로 시작하는 라인 수)
  - 워크드 예시 ≥1 (`**워크드 예시`로 시작하는 라인 수)
  - 흔한 오해→교정 ≥2 (`**흔한 오해→교정` 헤더 라인 수 또는 `✗ →` 마커 수 중 큰 값)
  - verbatim ≥1 (`**verbatim`으로 시작하는 라인 수)
  - 출처 참조 [S-###] ≥1

grep 검색계약 self-test: 파일 전체에서 `구간:`·`유형:`·`태그:`·`[C-` 패턴이
각각 최소 1건 회수되는지 확인한다(회수 안 되면 하류의 grep 기반 검색이 깨진다는 뜻).

사용:
  python scripts/verify_research_chunks.py 1
  python scripts/verify_research_chunks.py 1 --root <fixture-dir>   # 자체 테스트

동작:
  - 인자 없이 실행하면 사용법을 출력한다(비-FAIL, exit 0).
  - 대상 파일(sessions/N주차/자료/N주차_개념KB.md)이 없으면 그 주차가 아직 개념KB를
    만들지 않은 정상 상태이므로 SKIP을 출력하고 exit 0.
  - 파일이 있으면 청크별 검사를 수행해 FAIL이 있으면 exit 1, 없으면 exit 0.
"""
import argparse
import re
import sys
from pathlib import Path

USAGE = "사용: python scripts/verify_research_chunks.py <주차>  (예: 1, 2)"

CHUNK_HEADER = re.compile(r"^##\s+(\[C-[^\]]*\].*)$", re.MULTILINE)
META_COMMENT = re.compile(r"^<!--\s*(.*?)\s*-->\s*$")
SRC_REF = re.compile(r"\[S-\d+\]")

REQUIRED_META_KEYS = ("구간", "유형", "출처")
MIN_ANALOGY = 2
MIN_WORKED_EXAMPLE = 1
MIN_MISCONCEPTION = 2
MIN_VERBATIM = 1
MIN_SOURCE_REF = 1

# grep 검색계약 self-test 대상 패턴(라벨: 정규식)
SEARCH_CONTRACT_PATTERNS = {
    "구간:": re.compile(r"구간:"),
    "유형:": re.compile(r"유형:"),
    "태그:": re.compile(r"태그:"),
    "[C-": re.compile(r"\[C-"),
}

results = []  # (check, status, detail)


def add(check, status, detail=""):
    results.append((check, status, detail))


def read(p):
    try:
        return p.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        return None


def split_chunks(text):
    """'## [C-...]' 헤딩 기준으로 청크 분리.
    각 청크 = (제목 전문, 본문[헤딩 다음 줄 ~ 다음 헤딩 전 또는 EOF])."""
    matches = list(CHUNK_HEADER.finditer(text))
    chunks = []
    for i, m in enumerate(matches):
        title = m.group(1).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end]
        chunks.append((title, body))
    return chunks


def chunk_slug(title):
    m = re.match(r"\[(C-[^\]]*)\]", title)
    return m.group(1) if m else title[:30]


def check_meta_comment(body):
    """청크 바로 아래(빈 줄은 건너뜀) 메타주석 존재 여부와 필수 키를 확인한다.
    반환: (메타주석 내용 또는 None, 누락 키 목록 또는 사유 목록)"""
    for ln in body.splitlines():
        if not ln.strip():
            continue
        m = META_COMMENT.match(ln.strip())
        if not m:
            return None, ["메타주석 없음(청크 바로 아래 줄이 <!-- --> 형식 아님)"]
        inner = m.group(1)
        missing = [k for k in REQUIRED_META_KEYS if f"{k}:" not in inner]
        return inner, missing
    return None, ["메타주석 없음(본문 없음)"]


BULLET_RE = re.compile(r"^[-*+]\s+")


def count_prefixed_lines(body, prefix):
    """줄 앞의 마크다운 불릿 기호(-·*·+  뒤에 공백)를 벗겨낸 뒤 접두 문자열을 비교한다.
    실제 청크는 '- **비유①:** …'처럼 불릿 안에 굵게 필드를 쓰므로 불릿을 벗기지 않으면
    '**비유'로 시작하는지 검사할 때 전부 놓친다."""
    n = 0
    for ln in body.splitlines():
        s = BULLET_RE.sub("", ln.strip(), count=1)
        if s.startswith(prefix):
            n += 1
    return n


def check_chunk_depth(title, body):
    slug = chunk_slug(title)
    lacking = []

    meta, missing = check_meta_comment(body)
    if meta is None:
        lacking.append(missing[0])
    elif missing:
        lacking.append(f"메타주석 키 누락({','.join(missing)})")

    n_analogy = count_prefixed_lines(body, "**비유")
    if n_analogy < MIN_ANALOGY:
        lacking.append(f"비유 {n_analogy}/{MIN_ANALOGY}")

    n_worked = count_prefixed_lines(body, "**워크드 예시")
    if n_worked < MIN_WORKED_EXAMPLE:
        lacking.append(f"워크드 예시 {n_worked}/{MIN_WORKED_EXAMPLE}")

    n_misc_header = count_prefixed_lines(body, "**흔한 오해→교정")
    n_misc_marker = sum(1 for ln in body.splitlines() if "✗" in ln and "→" in ln)
    n_misc = max(n_misc_header, n_misc_marker)
    if n_misc < MIN_MISCONCEPTION:
        lacking.append(f"흔한 오해→교정 {n_misc}/{MIN_MISCONCEPTION}")

    n_verbatim = count_prefixed_lines(body, "**verbatim")
    if n_verbatim < MIN_VERBATIM:
        lacking.append(f"verbatim {n_verbatim}/{MIN_VERBATIM}")

    n_srcref = len(SRC_REF.findall(body))
    if n_srcref < MIN_SOURCE_REF:
        lacking.append(f"[S-###] {n_srcref}/{MIN_SOURCE_REF}")

    if lacking:
        add(f"청크:{slug}", "FAIL", "부족: " + ", ".join(lacking))
    else:
        add(f"청크:{slug}", "PASS")
    return not lacking


def check_search_contract(text):
    """grep 검색계약 self-test: 구간:·유형:·태그:·[C- 패턴이 파일 전체에서
    최소 1건씩 회수되는지 확인한다."""
    ok = True
    for label, pat in SEARCH_CONTRACT_PATTERNS.items():
        n = len(pat.findall(text))
        if n < 1:
            add(f"검색계약:{label}", "FAIL", "0건 회수(grep 실패)")
            ok = False
        else:
            add(f"검색계약:{label}", "PASS", f"{n}건")
    return ok


def main():
    try:  # Windows 콘솔(cp949)에서 화살표·이모지·한글 출력 깨짐/크래시 방지
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

    ap = argparse.ArgumentParser(description="개념KB(N주차_개념KB.md) 청크 깊이·검색계약 검증")
    ap.add_argument("week", nargs="?", default=None, help="주차 번호 (예: 1)")
    ap.add_argument("--root", default=None, help="저장소 루트 재정의(자체 테스트용)")
    args = ap.parse_args()

    if not args.week:
        print(USAGE)
        sys.exit(0)

    week = args.week
    root = Path(args.root) if args.root else Path(__file__).resolve().parent.parent
    target = root / "sessions" / f"{week}주차" / "자료" / f"{week}주차_개념KB.md"

    print(f"=== verify_research_chunks {week}주차 ===")

    text = read(target)
    if text is None:
        print(f"SKIP(파일 없음 — 정상) | {target}")
        sys.exit(0)

    chunks = split_chunks(text)
    if not chunks:
        add("청크수", "FAIL", "'## [C-...]' 청크 헤딩 0개")
    else:
        add("청크수", "PASS", f"{len(chunks)}개")
        for title, body in chunks:
            check_chunk_depth(title, body)

    check_search_contract(text)

    order = {"FAIL": 0, "WARN": 1, "SKIP": 2, "PASS": 3}
    results.sort(key=lambda r: order.get(r[1], 9))
    n = {"FAIL": 0, "WARN": 0, "PASS": 0, "SKIP": 0}
    for check, status, detail in results:
        n[status] = n.get(status, 0) + 1
        line = f"{status:4} | {check}"
        if detail:
            line += f" — {detail}"
        print(line)
    print(f"--- 총 청크={len(chunks)} FAIL={n['FAIL']} WARN={n['WARN']} PASS={n['PASS']} ---")
    result = "FAIL" if n["FAIL"] else "PASS"
    print(f"RESULT | {result}")
    sys.exit(1 if n["FAIL"] else 0)


if __name__ == "__main__":
    main()
