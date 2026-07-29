#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_research_chunks.py — 개념 지식베이스(N주차_개념KB.md) 청크 깊이·관점·검색계약 검증

개념KB(sessions/N주차/자료/N주차_개념KB.md)는 그 주차 **사실의 정본**이며 리서치 스킬의
기본 5파일 중 하나다(결과.md는 청크를 가리키는 인덱스층, 출처레지스트리는 원문 정본).
이 스크립트는 청크별 최소 깊이·G8 관점 최소치·청크 인덱스 일치·grep 검색계약을 점검한다.

청크 범위(G9): 메타주석의 선택 키 `범위:`가 `인접`이면 **인접 청크**, 키가 없거나 다른 값이면
**코어 청크**다. 인접 청크(커리큘럼 밖이지만 학생이 배운 직후 바로 묻는 개념)는 얕은 최소깊이만
채우며 비유·워크드 예시·G8 관점 3필드는 면제다.

검사 항목(코어 청크 · 청크 = "## [C-...]" 헤딩 단위):
  - 청크 바로 아래 메타주석 `<!-- 구간:… | 유형:… | 우선:… | 출처:… | 태그:… -->` 존재
    (구간·유형·우선·출처 키 필수 — `우선:`은 G8 관점 최소치 판정 기준)
  - 비유 ≥2 (`**비유`로 시작하는 라인 수)
  - 워크드 예시 ≥1 (`**워크드 예시`로 시작하는 라인 수)
  - 흔한 오해→교정 ≥2 (`**흔한 오해→교정` 헤더 라인 수 또는 `✗ →` 마커 수 중 큰 값)
  - verbatim ≥1 (`**verbatim`으로 시작하는 라인 수)
  - 출처 참조 [S-###] ≥1
  - G8 관점 최소치: `사례(실무)`·`대안·비교`·`한계·반론` 3필드 중
    P0=2개 이상 · P1=1개 이상 · P2=권장(0). 우선순위 파싱 실패 시 P1로 간주한다.
    본문에 `[관점 미확보:` 사유가 적혀 있으면 그 청크의 미달은 WARN으로 완화한다.
  - verbatim 줄 길이 > 300자면 WARN(원문 전문은 출처레지스트리 「출처ID별 verbatim」이 정본)

검사 항목(인접 청크 `범위:인접` · 얕은 최소깊이):
  - 메타주석과 필수 키는 코어와 동일
  - 정의 ≥1 · 초보자 문장 ≥1 · 연결 ≥1 (각각 `**정의`·`**초보자 문장`·`**연결` 라인)
  - 흔한 오해→교정 ≥1 (코어는 ≥2)
  - verbatim ≥1 · [S-###] ≥1
  - 비유·워크드 예시·G8 관점 3필드는 **검사하지 않는다**(면제 — 미달로 잡지 않는다).
    반대로 비유②·워크드 예시·G8 3필드를 **가지고 있으면** WARN(깊이는 코어 청크에 몰아준다)

파일 전체 검사:
  - 주차 바닥선(G8): `대안·비교` 보유 청크 ≥3 · `한계·반론` 보유 청크 ≥3 · `유형:사례` 청크 ≥1
    — **코어 청크만 세어** 판정한다(인접 청크는 G8 면제라 분모·분자 어디에도 넣지 않는다)
  - 인접 물량 상한(G9): 인접 청크 수 ≤ 코어 청크 수 × 0.5. 초과면 WARN(게이트A에서 사용자가
    승인해 늘렸을 수 있으므로 FAIL로 막지 않는다)
  - 「청크 인덱스」 표(RAG 진입점)의 슬러그 목록이 실제 청크 목록과 정확히 일치
    (표는 `| 슬러그 | 표시명 | 구간 | 우선 | 관점 | 범위 |` 6열이지만 첫 열만 읽으므로 열 수와 무관)
  - grep 검색계약 self-test: `구간:`·`유형:`·`태그:`·`[C-` 패턴이 각각 최소 1건 회수되는지
    확인한다(회수 안 되면 하류의 grep 기반 검색이 깨진다는 뜻)

스키마 v1/v2 하위호환 스위치:
  파일 서두에 `KB-스키마: v2` 표기가 있으면 v2, 없으면 v1로 간주한다.
  v1에서는 **G8 관련 검사(청크 관점 최소치·주차 바닥선)·청크 인덱스 표 검사·`우선:` 키 필수화**를
  FAIL이 아니라 WARN으로 강등한다(v1 시절 산출된 기존 KB가 소급 FAIL하지 않게 하는 장치).
  청크 최소깊이(비유·워크드예시·오해·verbatim·[S-###])와 검색계약은 v1·v2 공통으로 FAIL이다.

사용:
  python scripts/verify_research_chunks.py 1
  python scripts/verify_research_chunks.py 1 --root <fixture-dir>   # 자체 테스트

동작:
  - 인자 없이 실행하면 사용법을 출력한다(비-FAIL, exit 0).
  - 대상 파일이 없을 때:
      · 같은 폴더에 `N주차_콘텐츠리서치_결과.md`가 있으면 → FAIL·exit 1
        (리서치 산출이 끝난 주차인데 필수 산출물인 개념KB가 없는 상태 = 거짓 초록 방지)
      · 결과.md도 없으면 아직 리서치를 시작하지 않은 주차이므로 SKIP·exit 0
  - 파일이 있으면 청크별·파일 전체 검사를 수행해 FAIL이 있으면 exit 1, 없으면 exit 0.
"""
import argparse
import re
import sys
from pathlib import Path
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


USAGE = "사용: python scripts/verify_research_chunks.py <주차>  (예: 1, 2)"

CHUNK_HEADER = re.compile(r"^##\s+(\[C-[^\]]*\].*)$", re.MULTILINE)
META_COMMENT = re.compile(r"^<!--\s*(.*?)\s*-->\s*$")
SRC_REF = re.compile(r"\[S-\d+\]")

REQUIRED_META_KEYS = ("구간", "유형", "우선", "출처")
MIN_ANALOGY = 2
MIN_WORKED_EXAMPLE = 1
MIN_MISCONCEPTION = 2
MIN_VERBATIM = 1
MIN_SOURCE_REF = 1

# --- G9 인접 개념 청크 ---------------------------------------------------------
# 메타주석 선택 키 `범위:`. 값이 `인접`이면 인접 청크, 키가 없으면 코어 청크다.
SCOPE_RE = re.compile(r"범위\s*:\s*([^|]*)")
SCOPE_ADJACENT = "인접"
SCOPE_CORE = "코어"

# 인접 청크 필수 필드 접두(코어의 비유·워크드예시 대신 이 3종이 필수다)
ADJACENT_REQUIRED_PREFIXES = ("**정의", "**초보자 문장", "**연결")
ADJACENT_MIN_MISCONCEPTION = 1  # 코어는 2, 인접은 1
ADJACENT_RATIO_MAX = 0.5  # 인접 청크 수 ≤ 코어 청크 수 × 0.5
# 인접 청크에 있으면 안 되는(= 깊이는 코어에 몰아준다) 필드: 비유②·워크드 예시·G8 3필드
ADJACENT_TOO_DEEP_MSG = "인접 청크는 얕게 유지 — 깊이는 코어에"

# --- G8 관점 커버리지 ---------------------------------------------------------
# 청크 본문의 G8 3필드 불릿 접두(라벨: count_prefixed_lines에 넘길 접두 문자열).
# 실제 표기는 `- **사례(실무):**` 처럼 불릿 안 굵게 필드라서, 불릿을 벗긴 뒤 `**사례(실무)`로 비교한다.
BREADTH_FIELDS = {
    "사례(실무)": "**사례(실무)",
    "대안·비교": "**대안·비교",
    "한계·반론": "**한계·반론",
}
MIN_BREADTH_BY_PRIORITY = {"P0": 2, "P1": 1, "P2": 0}
DEFAULT_PRIORITY = "P1"  # 우선순위 파싱 실패 시 관대하게 P1로 간주
UNCOVERED_MARK = "[관점 미확보:"  # 사유를 명시한 경우 미달을 WARN으로 완화

WEEK_FLOOR_ALT = 3  # `대안·비교` 보유 청크 최소
WEEK_FLOOR_LIMIT = 3  # `한계·반론` 보유 청크 최소
WEEK_FLOOR_CASE_TYPE = 1  # 메타주석 `유형:사례` 청크 최소

VERBATIM_WARN_LEN = 300  # verbatim 한 줄이 이보다 길면 원문 전재 의심(WARN)

# --- 스키마 버전 --------------------------------------------------------------
SCHEMA_V2_MARKER = re.compile(r"KB-스키마\s*:\s*v2")
PRIORITY_RE = re.compile(r"우선\s*:\s*(P[012])")
META_TYPE_RE = re.compile(r"유형\s*:\s*([^|]*)")

# --- 청크 인덱스 --------------------------------------------------------------
INDEX_HEADING = re.compile(r"^##\s+청크\s*인덱스\s*$", re.MULTILINE)
NEXT_HEADING = re.compile(r"^##\s+", re.MULTILINE)
INDEX_SLUG = re.compile(r"^\[?(C-[^\]\s|]+)\]?$")

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
    각 청크 = (제목 전문, 본문[헤딩 다음 줄 ~ 다음 헤딩 전 또는 EOF]).

    주의: 서두 「청크 인덱스」 표 본문에도 `C-…` 토큰이 등장하지만 표 행은 `|`로 시작하므로
    `^## [C-` 헤딩 정규식에 걸리지 않는다(표 행을 청크로 오인하지 않는다)."""
    matches = list(CHUNK_HEADER.finditer(text))
    chunks = []
    for i, m in enumerate(matches):
        title = m.group(1).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end]
        chunks.append((title, body))
    return chunks


def file_head(text):
    """서두(첫 청크 헤딩 이전) 영역. 청크가 없으면 파일 전체."""
    m = CHUNK_HEADER.search(text)
    return text[: m.start()] if m else text


def detect_schema_v2(text):
    """파일 서두에 `KB-스키마: v2` 표기가 있으면 v2로 판정한다."""
    return bool(SCHEMA_V2_MARKER.search(file_head(text)))


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


def prefixed_lines(body, prefix):
    """count_prefixed_lines와 같은 방식으로 매칭된 줄들을 (불릿 제거 상태로) 돌려준다."""
    out = []
    for ln in body.splitlines():
        s = BULLET_RE.sub("", ln.strip(), count=1)
        if s.startswith(prefix):
            out.append(s)
    return out


def chunk_priority(meta):
    """메타주석에서 `우선:P0|P1|P2`를 파싱한다. 실패하면 DEFAULT_PRIORITY(관대)."""
    if meta:
        m = PRIORITY_RE.search(meta)
        if m:
            return m.group(1)
    return DEFAULT_PRIORITY


def chunk_scope(meta):
    """메타주석에서 선택 키 `범위:`를 파싱한다(G9).
    값이 `인접`이면 SCOPE_ADJACENT, 키가 없거나 다른 값이면 SCOPE_CORE(기본)."""
    if meta:
        m = SCOPE_RE.search(meta)
        if m and m.group(1).strip().startswith(SCOPE_ADJACENT):
            return SCOPE_ADJACENT
    return SCOPE_CORE


def chunk_is_adjacent(body):
    """청크 본문(메타주석 포함)이 인접 청크인지."""
    meta, _ = check_meta_comment(body)
    return chunk_scope(meta) == SCOPE_ADJACENT


def chunk_breadth(body):
    """청크 본문에 존재하는 G8 3필드 라벨 목록."""
    return [label for label, prefix in BREADTH_FIELDS.items() if count_prefixed_lines(body, prefix) > 0]


def chunk_is_case_type(meta):
    """메타주석 `유형:` 값에 '사례'가 포함되는지."""
    if not meta:
        return False
    m = META_TYPE_RE.search(meta)
    return bool(m) and "사례" in m.group(1)


def check_chunk_depth(title, body, is_v2=True):
    slug = chunk_slug(title)
    fail_lacking = []
    warn_lacking = []

    meta, missing = check_meta_comment(body)
    if meta is None:
        fail_lacking.append(missing[0])
    elif missing:
        hard = [k for k in missing if k != "우선"]
        soft = [k for k in missing if k == "우선"]
        if hard:
            fail_lacking.append(f"메타주석 키 누락({','.join(hard)})")
        if soft:
            # `우선:`은 v2에서만 필수(G8 최소치 판정 기준). v1은 WARN.
            (fail_lacking if is_v2 else warn_lacking).append("메타주석 키 누락(우선)")

    is_adjacent = chunk_scope(meta) == SCOPE_ADJACENT

    n_analogy = count_prefixed_lines(body, "**비유")
    n_worked = count_prefixed_lines(body, "**워크드 예시")
    n_misc_header = count_prefixed_lines(body, "**흔한 오해→교정")
    n_misc_marker = sum(1 for ln in body.splitlines() if "✗" in ln and "→" in ln)
    n_misc = max(n_misc_header, n_misc_marker)

    if is_adjacent:
        # G9 얕은 기준: 정의·초보자 문장·연결 각 ≥1 + 오해 ≥1.
        # 비유·워크드예시·G8 관점은 면제이므로 미달로 잡지 않는다.
        for prefix in ADJACENT_REQUIRED_PREFIXES:
            n_field = count_prefixed_lines(body, prefix)
            if n_field < 1:
                fail_lacking.append(f"{prefix.lstrip('*')} {n_field}/1")
        if n_misc < ADJACENT_MIN_MISCONCEPTION:
            fail_lacking.append(f"흔한 오해→교정 {n_misc}/{ADJACENT_MIN_MISCONCEPTION}")
    else:
        if n_analogy < MIN_ANALOGY:
            fail_lacking.append(f"비유 {n_analogy}/{MIN_ANALOGY}")
        if n_worked < MIN_WORKED_EXAMPLE:
            fail_lacking.append(f"워크드 예시 {n_worked}/{MIN_WORKED_EXAMPLE}")
        if n_misc < MIN_MISCONCEPTION:
            fail_lacking.append(f"흔한 오해→교정 {n_misc}/{MIN_MISCONCEPTION}")

    verbatims = prefixed_lines(body, "**verbatim")
    if len(verbatims) < MIN_VERBATIM:
        fail_lacking.append(f"verbatim {len(verbatims)}/{MIN_VERBATIM}")

    n_srcref = len(SRC_REF.findall(body))
    if n_srcref < MIN_SOURCE_REF:
        fail_lacking.append(f"[S-###] {n_srcref}/{MIN_SOURCE_REF}")

    if is_adjacent:
        # 인접 청크는 G8 면제 — 미달을 잡지 않는다. 대신 얕게 유지되는지만 본다(WARN).
        too_deep = []
        if n_analogy >= MIN_ANALOGY:
            too_deep.append(f"비유 {n_analogy}")
        if n_worked > 0:
            too_deep.append(f"워크드 예시 {n_worked}")
        have = chunk_breadth(body)
        if have:
            too_deep.append("G8 " + "·".join(have))
        if too_deep:
            warn_lacking.append(f"{ADJACENT_TOO_DEEP_MSG}({', '.join(too_deep)})")
    else:
        # G8 관점 최소치
        prio = chunk_priority(meta)
        min_breadth = MIN_BREADTH_BY_PRIORITY.get(prio, MIN_BREADTH_BY_PRIORITY[DEFAULT_PRIORITY])
        have = chunk_breadth(body)
        if len(have) < min_breadth:
            msg = f"G8 관점 {len(have)}/{min_breadth}({prio})"
            if UNCOVERED_MARK in body:
                warn_lacking.append(msg + " · [관점 미확보] 사유 명시")
            elif is_v2:
                fail_lacking.append(msg)
            else:
                warn_lacking.append(msg + " · v1")

    # verbatim 과장(원문 전재) 경고 — v1·v2 무관 항상 WARN
    over = [len(v) for v in verbatims if len(v) > VERBATIM_WARN_LEN]
    if over:
        add(
            f"verbatim길이:{slug}",
            "WARN",
            f"{len(over)}줄 최대 {max(over)}자(>{VERBATIM_WARN_LEN}) — "
            "verbatim 과장 — 원문 전문은 출처레지스트리로",
        )

    if fail_lacking:
        detail = "부족: " + ", ".join(fail_lacking)
        if warn_lacking:
            detail += " | 경고: " + ", ".join(warn_lacking)
        add(f"청크:{slug}", "FAIL", detail)
    elif warn_lacking:
        # 인접 청크의 '너무 깊음' 경고도 여기로 오므로 라벨은 '부족'이 아니라 '경고'다.
        add(f"청크:{slug}", "WARN", "경고: " + ", ".join(warn_lacking))
    else:
        add(f"청크:{slug}", "PASS")
    return not fail_lacking


def check_week_breadth(chunks, is_v2):
    """주차 전체 G8 바닥선: 대안·비교 ≥3 · 한계·반론 ≥3 · 유형:사례 청크 ≥1.

    G9 인접 청크는 G8 면제이므로 **코어 청크만 세어** 판정한다 — 인접 청크가 계수에 섞이면
    얕은 청크로 바닥선을 채운 것처럼 보여 기준이 왜곡된다."""
    status = "FAIL" if is_v2 else "WARN"
    n_alt = 0
    n_limit = 0
    n_case = 0
    for title, body in chunks:
        meta, _ = check_meta_comment(body)
        if chunk_scope(meta) == SCOPE_ADJACENT:
            continue
        have = chunk_breadth(body)
        if "대안·비교" in have:
            n_alt += 1
        if "한계·반론" in have:
            n_limit += 1
        if chunk_is_case_type(meta):
            n_case += 1

    ok = True
    for label, got, floor in (
        ("대안·비교", n_alt, WEEK_FLOOR_ALT),
        ("한계·반론", n_limit, WEEK_FLOOR_LIMIT),
        ("유형:사례", n_case, WEEK_FLOOR_CASE_TYPE),
    ):
        check = f"주차바닥선:{label}"
        if got < floor:
            add(check, status, f"보유 코어 청크 {got}/{floor}" + ("" if is_v2 else " · v1 강등"))
            ok = ok and status != "FAIL"
        else:
            add(check, "PASS", f"보유 코어 청크 {got}/{floor}")
    return ok


def check_adjacent_ratio(chunks, is_v2):
    """G9 물량 상한: 인접 청크 수 ≤ 코어 청크 수 × ADJACENT_RATIO_MAX.

    초과해도 FAIL이 아니라 WARN이다(v1·v2 공통) — 게이트A에서 사용자가 승인해 늘렸을 수 있고,
    그 승인 사실은 개념KB 「변경 이력」에 남는다."""
    n_adj = sum(1 for _, body in chunks if chunk_is_adjacent(body))
    n_core = len(chunks) - n_adj
    ratio_txt = f"{n_adj / n_core * 100:.0f}%" if n_core else "—"
    detail = f"인접 {n_adj} / 코어 {n_core} (비율 {ratio_txt})"
    if n_adj > n_core * ADJACENT_RATIO_MAX:
        add(
            "인접비율",
            "WARN",
            f"{detail} — 상한 {ADJACENT_RATIO_MAX:.0%} 초과 "
            "· 깊이는 코어에 몰아준다(게이트A 승인분이면 「변경 이력」에 근거를 남길 것)",
        )
        return True
    add("인접비율", "PASS", f"{detail} ≤ 상한 {ADJACENT_RATIO_MAX:.0%}")
    return True


def index_section(text):
    """서두 「## 청크 인덱스」 절 본문을 돌려준다. 없으면 None."""
    m = INDEX_HEADING.search(text)
    if not m:
        return None
    start = m.end()
    nxt = NEXT_HEADING.search(text, start)
    return text[start : nxt.start()] if nxt else text[start:]


def index_slugs(section):
    """마크다운 표 첫 열에서 `C-…` 슬러그를 수집한다.
    `[C-토큰]` 대괄호 표기와 맨몸 `C-토큰` 표기를 모두 허용하며,
    구분선(`|---|`)과 헤더 행은 첫 열이 슬러그 형태가 아니므로 자연히 제외된다.

    열 수는 하드코딩하지 않는다 — G9로 `범위` 열이 추가돼 6열이 됐지만 첫 열만 읽으므로
    앞으로 열이 더 늘거나 줄어도 이 파서는 영향을 받지 않는다."""
    slugs = []
    for ln in section.splitlines():
        s = ln.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if not cells:
            continue
        m = INDEX_SLUG.match(cells[0])
        if m:
            slugs.append(m.group(1))
    return slugs


def check_chunk_index(text, chunks, is_v2):
    """「청크 인덱스」 표가 실제 청크 목록과 정확히 일치하는지 확인한다(RAG 진입점 계약)."""
    status = "FAIL" if is_v2 else "WARN"
    section = index_section(text)
    if section is None:
        add(
            "청크인덱스",
            status,
            "「## 청크 인덱스」 절 없음 — RAG 진입점 없음" + ("" if is_v2 else " · v1 강등"),
        )
        return not is_v2

    listed = index_slugs(section)
    listed_set = set(listed)
    actual_set = {chunk_slug(t) for t, _ in chunks}
    only_index = sorted(listed_set - actual_set)
    only_chunk = sorted(actual_set - listed_set)

    if only_index or only_chunk:
        parts = []
        if only_index:
            parts.append(f"인덱스에만 {len(only_index)}건({', '.join(only_index[:8])}{'…' if len(only_index) > 8 else ''})")
        if only_chunk:
            parts.append(f"청크에만 {len(only_chunk)}건({', '.join(only_chunk[:8])}{'…' if len(only_chunk) > 8 else ''})")
        add("청크인덱스", status, "불일치 — " + " / ".join(parts) + ("" if is_v2 else " · v1 강등"))
        return not is_v2

    add("청크인덱스", "PASS", f"{len(listed_set)}행 일치")
    return True


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

    ap = argparse.ArgumentParser(description="개념KB(N주차_개념KB.md) 청크 깊이·관점·검색계약 검증")
    ap.add_argument("week", nargs="?", default=None, help="주차 번호 (예: 1)")
    ap.add_argument("--root", default=None, help="저장소 루트 재정의(자체 테스트용)")
    args = ap.parse_args()

    if not args.week:
        print(USAGE)
        sys.exit(0)

    week = args.week
    root = Path(args.root) if args.root else Path(__file__).resolve().parent.parent
    data_dir = _session_dir(root, week) / "자료"
    target = data_dir / f"{week}주차_개념KB.md"
    research_result = data_dir / f"{week}주차_콘텐츠리서치_결과.md"

    print(f"=== verify_research_chunks {week}주차 ===")

    chunks = []
    text = read(target)
    if text is None:
        if research_result.exists():
            # 거짓 초록 방지: 리서치 산출이 끝난 주차인데 사실 정본이 없다.
            add(
                "개념KB존재",
                "FAIL",
                f"리서치 산출 완료 상태인데 필수 산출물 개념KB 없음 — {research_result.name}는 있고 {target.name}가 없다",
            )
        else:
            print(f"SKIP(개념KB·결과.md 모두 없음 — 리서치 미착수 주차, 정상) | {target}")
            sys.exit(0)
    else:
        is_v2 = detect_schema_v2(text)
        if is_v2:
            add("KB-스키마", "PASS", "v2")
        else:
            add("KB-스키마", "WARN", "v1(서두에 `KB-스키마: v2` 표기 없음) — G8·청크인덱스·우선키 검사를 WARN으로 강등")

        chunks = split_chunks(text)
        if not chunks:
            add("청크수", "FAIL", "'## [C-...]' 청크 헤딩 0개")
        else:
            add("청크수", "PASS", f"{len(chunks)}개")
            # 정보용 카운트(2026-07-27 B2 신설) — PASS/FAIL 판정 아님. `PPT 소재:` 필드는
            # /콘텐츠가 시각자료로 실현해야 할 하류 회수 대상이라, 몇 개나 있는지를 미리
            # 보여줘야 하류가 그 존재 자체를 놓치지 않는다(실현 여부는 이 스크립트의 책임
            # 밖 — verify_draft_quality.py의 R-QD-05 「PPT 소재 처분표」가 그 대조를 맡는다).
            ppt_source_chunks = sum(1 for _title, body in chunks if "PPT 소재" in body)
            add("PPT소재:보유청크(정보용)", "PASS",
                f"{ppt_source_chunks}/{len(chunks)}개 청크에 'PPT 소재' 필드 존재 — "
                "/콘텐츠 집필노트의 「PPT 소재 처분표」에서 전량 사용/대체/보류 처리해야 함")
            for title, body in chunks:
                check_chunk_depth(title, body, is_v2)

        check_week_breadth(chunks, is_v2)
        check_adjacent_ratio(chunks, is_v2)
        check_chunk_index(text, chunks, is_v2)
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
