#!/usr/bin/env python3
"""verify_draft_quality.py — 콘텐츠 초안(.md) 단계 밀도 게이트(R-QD-01~07, 의존성 0).

사용: python scripts/verify_draft_quality.py <주차> [--root <dir>] [--strict]
예:   python scripts/verify_draft_quality.py 2
      python scripts/verify_draft_quality.py 2 --root tests/fixtures/quality_gates  # 자체 테스트용

배경: 2주차 저밀도 결함은 **조립(덱) 단계가 아니라 그 앞 `.md` 초안 단계**에서 이미 확정돼 있었다
(`content_pipeline_audit.md` §C — 초안 본문 글자수 중앙값 63자, 1주차 최종 초안 122자의 51.6%).
결함을 조립 후 덱에서 잡는 것(`verify_deck_quality.py`)보다 **초안 단계에서 먼저 잡는 것이 훨씬
싸다** — 이 스크립트가 그 자리를 채운다.

초안 표 형식은 `입력양식/콘텐츠초안템플릿.md`·`skills/콘텐츠/SKILL.md` §0-1이 정본이다:
`| # | 슬라이드 제목 | 본문 문구 | 비유·멘트 |` 4열 표, 교시(또는 PART)별 `##` 헤더 아래 배치.
이 스크립트는 파일명이 아니라 실제 1주차·2주차 초안 파일을 읽어 그 형식을 그대로 파싱한다.

**임계값은 W1_FINAL(1주차 최종 초안) 분포에서 도출**(발명 금지). 표지(선/간지)·마무리·실습 행은
원래 짧아야 하므로 R-QD-01·03 도출·판정에서 제외한다(`skills/콘텐츠/SKILL.md` §0-6의
screen-operation 예외와 같은 취지 — 정보 밀도 하한은 "설명" 성격의 행에만 의미가 있다).
도출 근거는 하단 THRESH_DERIVATION과 스크래치패드 `analyze_drafts.py`(이 세션 산출, 저장소 밖)에
있다.

심각도: R-QD-01·03·06·07은 WARN(기본, exit 0) — `--strict`로 FAIL 승격. R-QD-04·05는 **항상 FAIL**
(구조적으로 객관적인 검사라 안전 — "이탈 자체"가 아니라 "이탈했는데 사유 기록조차 없음"만 FAIL하고,
필수 산출물 부재도 이분법적 사실이라 오탐 위험이 낮다). R-QD-02(정보 단위 근사치)는 2026-07-27
독립 리뷰에서 **`[사람검토]`로 강등됐다** — 어휘 신호(bold·원문자·`<br>`) 기반 근사치가 W1/W2를
거의 구분하지 못해(3.6% vs 10.7%) 자동 판정으로 쓰기엔 판별력이 부족하다.

**R-QD-01은 목표가 아니라 대리 신호(proxy)다.** `skills/콘텐츠/SKILL.md` §0-6은 "문자수 목표는
두지 않는다 — 리치함은 글자수가 아니라 단위 수"라고 명시한다. R-QD-01의 WARN 문구는 그래서
"글자수를 늘려라"가 아니라 "정보 단위가 부족할 가능성"으로 표현한다(2026-07-27 B2). **화면 조작
안내 행은 R-QD-01/02에서 제외된다**(R-DENS-01a 계약 예외 — `is_screen_operation_row()`, 초안
단계엔 CSS가 없어 제목·본문 어휘로 최선 근사하며 제외된 행은 항상 `[사람검토] R-QD-EXEMPT`로
명시한다).
"""
import argparse
import os
import re
import sys
from pathlib import Path

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


try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# ============================================================================
# 임계값 도출 — sessions/1주차/1주차_초안.md(W1_FINAL) vs sessions/2주차/2주차_초안.md(W2_CURRENT)
#   대상: "0. 덱 기본 정보"(+ 중첩 "파트 구조" 메타 표)·(표지)·(간지)·(마무리)·"실습" 제목 행
#   제외("설명" 성격 행만 — deck 게이트의 개념설명 필터와 같은 취지).
#   W1 n=55행 · W2 n=84행(스크래치패드 실측, 이 파일의 _sections/_parse_rows로 직접 재계산).
# ============================================================================
THRESH_QD01_CHARS = 52           # W1 non-fixed/non-practice 행 분포. flag: W1 3.6%(2/55) · W2 56.0%(47/84) — 목표(<=15%/>=55%) 충족
THRESH_QD02_UNITS = 1            # skills/콘텐츠/SKILL.md:32 "정보 단위 1개 이하 지양" 정책값 그대로 — [사람검토] 강등됨(아래 참고), 자동 판정에는 쓰지 않는다
THRESH_QD03_RATIO = 0.85         # 노트:본문 글자수 비율. flag: W1 3.6%(2/55) · W2 70.2%(59/84) — 목표 충족
THRESH_QD07_ADJACENT_JACCARD = 0.25   # 인접 행 3-gram 자카드 유사도. W1 실측 최댓값 0.190·W2 실측 최댓값 0.124 위 안전마진
THRESH_DERIVATION = """\
[임계값 도출 근거 — sessions/1주차/1주차_초안.md(W1_FINAL) vs sessions/2주차/2주차_초안.md(W2_CURRENT), "0.덱 기본 정보"/(표지)/(간지)/(마무리)/실습 행 제외]
  R-QD-01 본문 글자수 < 52자                 flag률: W1  3.6%(2/55) · W2 56.0%(47/84)  [목표 충족: W1<=15%, W2>=55%]
  R-QD-02 정보 단위(근사치) <= 1개            [사람검토]로 강등됨(자동 판정 없음) — flag률 참고용: W1 3.6%(2/55) · W2 10.7%(9/84), 어휘 기반 근사치라 판별력 부족
  R-QD-03 노트:본문 글자수 비율 > 0.85        flag률: W1  3.6%(2/55) · W2 70.2%(59/84)  [목표 충족]
  R-QD-07 인접 행 근접중복(3-gram 자카드) > 0.25  지표값(낮을수록 좋음, 실측 최댓값): W1 0.190 · W2 0.124 — 현재 두 덱 모두 패딩 없음(안티게이밍 안전망, 목표 %는 해당 없음)
"""


# ============================================================================
# 초안 표 파싱
# ============================================================================

_HEADER_RE = re.compile(r"^(#{1,6})\s+(.*)$")
_SECTION_NUM_RE = re.compile(r"(\d+)\s*교시|PART\s*(\d+)", re.I)
_FIXED_TITLE_RE = re.compile(r"\((?:표지|간지|마무리)\)")


def _sections(text):
    """(레벨2 헤더 텍스트, 그 아래 본문) 목록."""
    out, h, body = [], None, []
    for line in text.splitlines():
        m = _HEADER_RE.match(line)
        if m and len(m.group(1)) == 2:
            if h is not None:
                out.append((h, "\n".join(body)))
            h, body = m.group(2).strip(), []
        elif h is not None:
            body.append(line)
    if h is not None:
        out.append((h, "\n".join(body)))
    return out


def _parse_rows(section_text):
    """(rows, shape_issues). shape_issues: 4열 계약(# | 슬라이드 제목 | 본문 문구 | 비유·멘트)과
    셀 수가 다른 표 행의 원문 일부 — 2026-07-27 독립 리뷰가 지적한 대로, 예전엔 이런 행도
    cells[0:4]를 그대로 집어 엉뚱한 셀을 notes로 배정한 채 조용히 통과시켰다. 이제는 그 값을
    쓰지 않고 R-QD-06으로 보고한다(오탐 위험이 있어 FAIL이 아니라 WARN — 셀 안에 `|`가 들어간
    코드 스니펫처럼 정상인데 셀 수가 달라 보이는 경우가 있을 수 있다)."""
    rows = []
    shape_issues = []
    for line in section_text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        if re.match(r"^\|\s*-+\s*\|", line):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if cells and cells[0] in ("#", ""):
            continue
        if len(cells) != 4:
            shape_issues.append(line[:100])
            continue
        rows.append({"num": cells[0], "title": cells[1], "body": cells[2], "notes": cells[3]})
    return rows, shape_issues


def _strip_md(s):
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.I)
    s = re.sub(r"\*\*|`", "", s)
    s = re.sub(r"<[^>]+>", "", s)
    return s


def _char_len(s):
    return len(re.sub(r"\s+", "", _strip_md(s)))


def _info_units(body):
    """정보 단위 근사치 — bold 라벨(**x**) · 원문자(①②…) · <br> 절 중 최댓값.
    skills/콘텐츠/SKILL.md §0-6의 '본문 개념 블록·비유/예시 카드·비교표·오해→교정·체크/콜아웃'
    각 1단위를 완전히 자동화할 수 없어(의미 판단 필요) 어휘 신호로만 근사한다 — 위 THRESH_DERIVATION의
    낮은 판별력 캐비어트를 반드시 함께 읽을 것."""
    clean = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    bolds = re.findall(r"\*\*[^*]+\*\*", clean)
    circled = re.findall(r"[①②③④⑤⑥⑦⑧⑨⑩]", clean)
    brs = [s for s in re.split(r"<br\s*/?>", clean, flags=re.I)
           if re.sub(r"\s+", "", re.sub(r"<[^>]+>", "", s)).strip(" *`")]
    return max(len(bolds), len(circled), len(brs))


def _is_fixed_or_practice(title):
    if _FIXED_TITLE_RE.search(title):
        return True
    if "실습" in title:
        return True
    return False


# ============================================================================
# R-QD-07 — 반복·부풀리기(안티게이밍) 탐지. stdlib만 사용하는 간단한 n-gram 중복 검사다.
# 글자수 하한(R-QD-01)만 있으면 같은 문장을 두 번 쓰거나 앞 행을 살짝 바꿔 붙이는 식으로
# "글자수만" 채우는 회피가 보상받는다 — 이 검사가 그 회피를 잡는다.
# ============================================================================

def _char_trigrams(s):
    s = re.sub(r"\s+", "", s)
    if len(s) < 3:
        return set()
    return {s[i:i + 3] for i in range(len(s) - 2)}


def _jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _sentences(body_stripped):
    parts = re.split(r"[.!?]\s+|\n", body_stripped)
    out = []
    for p in parts:
        t = re.sub(r"\s+", "", p)
        # A3(2026-07-27): 끝 문장부호 유무만 다른 두 문장("A." vs "A")은 여전히 같은 문장이다 —
        # 분할 시점에 구분자로 쓰인 마침표는 이미 지워졌어도, 마지막 조각처럼 뒤에 텍스트가
        # 없어 마침표가 남는 경우가 있어 정규화하지 않으면 중복 판정이 조용히 깨진다.
        t = re.sub(r"[.!?]+$", "", t)
        if len(t) >= 6:
            out.append(t)
    return out


def intra_row_duplicate(body_stripped):
    """같은 행 안에서 문장(6자 이상, 끝 문장부호 무시)이 정확히 중복되면 True — 문장 복붙으로
    글자수만 채우는 패턴."""
    sents = _sentences(body_stripped)
    return len(sents) != len(set(sents))


# ============================================================================
# 화면 조작 안내 예외(R-DENS-01a) — 2026-07-27 B1: `skills/콘텐츠/SKILL.md` §0-6 각주가
# 이미 "화면 조작 안내 슬라이드는 이 하한에서 제외한다"고 규정한다(커리큘럼 기준안 §6 원칙 9).
# 초안(.md) 단계엔 CSS 클래스가 없어 덱 단계(family_signature)만큼 신뢰할 신호가 없다 — 실제
# 관찰된 저작 어휘(제목이 열기/켜기/누르기로 끝나거나, 본문에 버튼·메뉴·권한 요청·허용창처럼
# 화면 UI 요소를 직접 지시하는 표현)로 최선 근사한다. 오탐 위험이 있으므로 예외 적용 결과를
# 항상 R-QD-01 출력에 감사 가능하게 남긴다(침묵 예외 금지 — A1과 같은 원칙).
_SCREEN_OP_TITLE_RE = re.compile(r"(?:열기|켜기|누르기)\s*$")
_SCREEN_OP_BODY_RE = re.compile(r"버튼|메뉴|권한\s*(?:요청|질문)|허용창|창이\s*뜨면")


def is_screen_operation_row(title, body_stripped):
    return bool(_SCREEN_OP_TITLE_RE.search((title or "").strip())) or bool(_SCREEN_OP_BODY_RE.search(body_stripped))


def resolve_draft(sess_dir, wk):
    prefixed = sess_dir / f"{wk}주차_초안.md"
    if prefixed.exists():
        return prefixed
    legacy = sess_dir / "초안.md"
    return legacy


# ============================================================================
# 검사
# ============================================================================

def run_checks(root, wk):
    results = []  # (rule_id, level, message)
    advisories = []  # (rule_id, message) — 사람검토 전용, PASS/WARN/FAIL 판정 없음
    sess = _session_dir(root, wk)
    draft_path = resolve_draft(sess, wk)
    if not draft_path.exists():
        results.append(("R-QD-00", "FAIL", f"초안 파일 없음: {draft_path}"))
        return results, advisories

    text = draft_path.read_text(encoding="utf-8")
    sections = _sections(text)

    all_rows = []
    all_shape_issues = []
    section_row_counts = {}  # 교시/PART 라벨 -> 행 수(고정/실습 제외 없이 전체 카운트)
    for header, body in sections:
        # "0. 덱 기본 정보"(+ 중첩된 "### 파트/PART 구조" 메타 표)는 슬라이드 콘텐츠가 아니라
        # 덱 메타데이터다 — `항목|값`·`파트|묶는 교시|제목|한 줄 설명` 표가 우연히 4열이라
        # 콘텐츠 표와 같은 파서에 걸리므로 명시적으로 건너뛴다(입력양식/콘텐츠초안템플릿.md 0번 구조).
        if re.match(r"^0[.\s]", header) or "덱 기본 정보" in header:
            continue
        if "읽고 시작해" in header:
            # 아이콘 범례 서두(§0-1) — 3열 표(표기|뜻|처리) 등 콘텐츠 4열 계약과 무관한 안내 표를
            # 담을 수 있다. R-QD-06(표 형태 계약) 오탐을 막기 위해 콘텐츠 섹션에서 제외한다.
            continue
        rows, shape_issues = _parse_rows(body)
        all_shape_issues.extend(f"{header}: {line}" for line in shape_issues)
        m = _SECTION_NUM_RE.search(header)
        if m:
            section_row_counts[header] = len(rows)
        for r in rows:
            r["_section"] = header
            all_rows.append(r)

    scored_rows = []
    for r in all_rows:
        if _is_fixed_or_practice(r["title"]):
            continue
        b = _char_len(r["body"])
        if not b:
            continue
        n = _char_len(r["notes"])
        ratio = n / b if b else 0.0
        units = _info_units(r["body"])
        body_stripped = _strip_md(r["body"])
        screen_op = is_screen_operation_row(r["title"], body_stripped)
        scored_rows.append({**r, "chars": b, "note_chars": n, "ratio": ratio, "units": units,
                             "screen_operation": screen_op})

    # B1(2026-07-27): 화면 조작 안내 행은 R-QD-01(밀도)에서 뺀다(계약 예외, R-DENS-01a) —
    # R-QD-03·06·07은 밀도 판정이 아니라 노트배분·형태·반복 검사라 이 예외를 적용하지 않는다.
    screen_op_rows = [r for r in scored_rows if r["screen_operation"]]
    density_rows = [r for r in scored_rows if not r["screen_operation"]]
    if screen_op_rows:
        advisories.append(("R-QD-EXEMPT",
                            f"화면 조작 안내 계약예외(R-DENS-01a)로 R-QD-01 밀도 판정에서 제외된 행 "
                            f"{len(screen_op_rows)}개: " + ", ".join(r["num"] for r in screen_op_rows[:10])))

    # ── R-QD-01: 슬라이드당 본문 글자수 하한 — B2(2026-07-27): 목표가 아니라 정보 단위 부족의
    # 대리 신호(proxy)일 뿐이다(`skills/콘텐츠/SKILL.md` §0-6 "문자수 목표는 두지 않는다"). ──
    low = [r for r in density_rows if r["chars"] < THRESH_QD01_CHARS]
    if density_rows:
        pct = len(low) / len(density_rows) * 100
        detail = ", ".join(f'{r["num"]}({r["chars"]}자)' for r in low[:10])
        more = f" 외 {len(low) - 10}건" if len(low) > 10 else ""
        results.append(("R-QD-01", "WARN" if low else "PASS",
                         f"정보 단위가 부족할 가능성(본문 글자수 <{THRESH_QD01_CHARS}자, 목표 아닌 대리 신호): "
                         f"{len(low)}/{len(density_rows)}행({pct:.1f}%) — 글자수를 늘리는 게 아니라 정보 단위를 "
                         f"더하는 문제다(§0-6)"
                         f"{' — ' + detail + more if low else ''}"))
    else:
        results.append(("R-QD-01", "PASS", "검사 대상 행 없음"))

    # ── R-QD-02: 정보 단위 수 3~6(근사치) — 2026-07-27 [사람검토]로 강등(자동 판정 없음) ──
    # 어휘 신호(bold·원문자·<br>) 근사치가 W1/W2를 거의 구분 못 해(3.6% vs 10.7%) 자동 WARN으로
    # 쓰면 실효성보다 오탐 소음이 크다. 판정 없이 참고 수치만 보고한다.
    thin = [r for r in density_rows if r["units"] <= THRESH_QD02_UNITS]
    if density_rows:
        pct = len(thin) / len(density_rows) * 100
        advisories.append(("R-QD-02",
                            f"정보 단위(근사치) <={THRESH_QD02_UNITS}개: {len(thin)}/{len(density_rows)}행"
                            f"({pct:.1f}%) — 어휘 기반 근사치라 판별력이 약해 판정 없이 참고치만 제공(SKILL.md §0-6은 사람이 직접 확인, 화면조작 예외행 제외)"))
    else:
        advisories.append(("R-QD-02", "검사 대상 행 없음"))

    # ── R-QD-06: 표 형태 계약(4열) 위반 탐지 — 2026-07-27 독립 리뷰 지적(A5) ──
    if all_shape_issues:
        detail = " | ".join(all_shape_issues[:5])
        more = f" 외 {len(all_shape_issues) - 5}건" if len(all_shape_issues) > 5 else ""
        results.append(("R-QD-06", "WARN",
                         f"4열 계약과 다른 표 행 {len(all_shape_issues)}건 — 열이 밀려 엉뚱한 셀이 "
                         f"본문/노트로 잘못 배정될 수 있어 해당 행은 R-QD-01/02/03/07 계산에서 제외됨: {detail}{more}"))
    else:
        results.append(("R-QD-06", "PASS", "모든 표 행이 4열 계약과 일치"))

    # ── R-QD-07: 반복·부풀리기(안티게이밍) 탐지 ──
    intra_dup = [r for r in scored_rows if intra_row_duplicate(_strip_md(r["body"]))]
    tris = [_char_trigrams(_strip_md(r["body"])) for r in scored_rows]
    adjacent_hits = []
    for i in range(len(tris) - 1):
        ratio = _jaccard(tris[i], tris[i + 1])
        if ratio > THRESH_QD07_ADJACENT_JACCARD:
            adjacent_hits.append((scored_rows[i]["num"], scored_rows[i + 1]["num"], ratio))
    if intra_dup or adjacent_hits:
        parts = []
        if intra_dup:
            parts.append(f"행내 문장중복 {len(intra_dup)}건: " + ", ".join(r["num"] for r in intra_dup[:8]))
        if adjacent_hits:
            parts.append(f"인접행 근접중복 {len(adjacent_hits)}건: " +
                          ", ".join(f'{a}~{b}(비율{r:.2f})' for a, b, r in adjacent_hits[:8]))
        results.append(("R-QD-07", "WARN", "반복·부풀리기 의심 — " + " · ".join(parts)))
    else:
        results.append(("R-QD-07", "PASS", "행내 문장중복 0 · 인접행 근접중복(임계 "
                                            f"{THRESH_QD07_ADJACENT_JACCARD}) 0"))

    # ── R-QD-03: 노트:본문 글자수 비율 상한 ──
    heavy_note = [r for r in scored_rows if r["ratio"] > THRESH_QD03_RATIO]
    if scored_rows:
        pct = len(heavy_note) / len(scored_rows) * 100
        detail = ", ".join(f'{r["num"]}(비율{r["ratio"]:.2f})' for r in heavy_note[:10])
        more = f" 외 {len(heavy_note) - 10}건" if len(heavy_note) > 10 else ""
        results.append(("R-QD-03", "WARN" if heavy_note else "PASS",
                         f"노트:본문 비율 >{THRESH_QD03_RATIO}: {len(heavy_note)}/{len(scored_rows)}행"
                         f"({pct:.1f}%) — 화면이 아니라 발표자 노트로 내용이 이주하고 있다는 신호"
                         f"{' — ' + detail + more if heavy_note else ''}"))
    else:
        results.append(("R-QD-03", "PASS", "검사 대상 행 없음"))

    # ── R-QD-04: 교시당 장수 규약(8~11) 이탈 시 사유가 집필노트에 기록됐는가 (FAIL) ──
    note_path = sess / "자료" / f"{wk}주차_콘텐츠_집필노트.md"
    note_exists = note_path.exists()
    deviations = {h: n for h, n in section_row_counts.items() if not (8 <= n <= 11)}
    if deviations:
        detail = ", ".join(f'{h}({n}장)' for h, n in deviations.items())
        if note_exists:
            results.append(("R-QD-04", "WARN",
                             f"교시당 장수 규약(8~11) 이탈 {len(deviations)}건 — {detail} "
                             f"(집필노트 존재: {note_path.name} — 사유 기록 여부는 사람이 확인)"))
        else:
            results.append(("R-QD-04", "FAIL",
                             f"교시당 장수 규약(8~11) 이탈 {len(deviations)}건({detail})인데 "
                             f"집필노트({note_path})가 없어 사유 기록 자체를 확인할 수 없음"))
    else:
        results.append(("R-QD-04", "PASS", f"모든 교시/PART가 규약(8~11장) 범위 안 ({len(section_row_counts)}개 구간)"))

    # ── R-QD-05: 필수 산출물 존재 검사 ──
    materials = sess / "자료"
    review_html_candidates = [sess / f"{wk}주차_콘텐츠_리뷰.html", materials / f"{wk}주차_콘텐츠_리뷰.html"]
    review_html = next((p for p in review_html_candidates if p.exists()), None)
    # 집필노트·리뷰HTML은 skills/콘텐츠/SKILL.md 8단계가 무조건 산출 항목으로 못박는다(리뷰HTML은 "필수" 명시) → FAIL.
    if note_exists:
        results.append(("R-QD-05", "PASS", f"집필노트 존재: {note_path}"))
        # B3(2026-07-27): 집필노트가 있으면 「PPT 소재 처분표」 섹션도 있어야 한다 — 개념KB의
        # `PPT 소재:` 필드가 화면/부록/노트 중 어디로 실현됐는지(사용/대체/보류)를 대조하는 표다.
        # 표 안 내용의 완결성은 기계 판단 불가(사람검토) — 섹션 존재만 WARN으로 검사한다.
        note_text = note_path.read_text(encoding="utf-8")
        # 2026-07-29: 「PPT 소재 처분표」가 「재료 처분표」로 확장·개명됐다(필수 진술 + 생략 기록 흡수).
        # 옛 이름 문서도 계속 통과해야 하므로 공통 어간 "처분표"로 검사한다.
        if "처분표" in note_text:
            results.append(("R-QD-05", "PASS", "집필노트에 「재료 처분표」(옛 「PPT 소재 처분표」) 섹션 존재"))
        else:
            results.append(("R-QD-05", "WARN",
                             "집필노트에 「재료 처분표」 섹션 없음(skills/콘텐츠/SKILL.md 집필노트 규격) — "
                             "개념KB의 PPT 소재·필수 진술이 화면/부록/노트 어디에도 실현 여부를 대조받지 "
                             "못했을 위험. 생략(판단 5분류 S) 기록도 이 표가 유일한 검사기다"))
    else:
        results.append(("R-QD-05", "FAIL", f"집필노트 없음(필수, skills/콘텐츠/SKILL.md 8단계): {note_path}"))
    if review_html:
        results.append(("R-QD-05", "PASS", f"콘텐츠 리뷰 HTML 존재: {review_html}"))
    else:
        results.append(("R-QD-05", "FAIL",
                         f"콘텐츠 리뷰 HTML 없음(필수, skills/콘텐츠/SKILL.md 8단계 '(필수)'): "
                         f"{review_html_candidates[0]} 또는 {review_html_candidates[1]}"))
    # 이미지-에셋.json·이미지-프롬프트.md는 skills/콘텐츠/SKILL.md의 산출물 목록에 없다 —
    # create-slides SKILL.md ⑥ 이미지 단계(조립 이후)의 산출물이라 초안 단계 필수로 강제하면
    # 정상적인 파이프라인 순서(콘텐츠 → create-slides)에서도 상시 FAIL이 된다. WARN으로 강등한다.
    for label, fname in (("이미지-에셋.json", "이미지-에셋.json"), ("이미지-프롬프트.md", "이미지-프롬프트.md")):
        p = materials / fname
        if p.exists():
            results.append(("R-QD-05", "PASS", f"{label} 존재: {p}"))
        else:
            results.append(("R-QD-05", "WARN",
                             f"{label} 없음: {p} (선택 — create-slides 조립 단계의 이미지 판정 산출물이라 "
                             f"콘텐츠 초안 단계에서는 아직 없을 수 있음. 조립 전에는 정상)"))

    return results, advisories


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("week", help="주차 번호(예: 2)")
    ap.add_argument("--root", default=None, help="저장소 루트 재정의(자체 테스트용)")
    ap.add_argument("--strict", action="store_true", help="WARN을 FAIL로 승격(기본은 WARN·exit 0, R-QD-04/05는 항상 FAIL 유지)")
    a = ap.parse_args()

    root = Path(a.root) if a.root else Path(__file__).resolve().parent.parent
    results, advisories = run_checks(root, a.week)

    print(THRESH_DERIVATION)
    print(f"=== verify_draft_quality: {a.week}주차 (root={root}) ===")
    effective = []
    for rule_id, level, msg in results:
        eff = level
        if a.strict and level == "WARN":
            eff = "FAIL"
        effective.append((rule_id, eff, msg))
        mark = {"PASS": "✓", "WARN": "△", "FAIL": "✗"}[eff]
        print(f"[{eff}] {mark} {rule_id}: {msg}")

    print("\n-- 사람검토(자동화 불가, 판정 없음) --")
    for rule_id, msg in advisories:
        print(f"[사람검토] · {rule_id}: {msg}")

    fails = sum(1 for _r, lvl, _m in effective if lvl == "FAIL")
    warns = sum(1 for _r, lvl, _m in effective if lvl == "WARN")
    passes = sum(1 for _r, lvl, _m in effective if lvl == "PASS")
    print(f"\n요약: FAIL {fails} · WARN {warns} · PASS {passes}"
          f"{' (--strict: WARN→FAIL 승격됨)' if a.strict else ' (기본 모드: R-QD-01/03/06/07 WARN은 exit 0, R-QD-04/05는 항상 FAIL 반영)'}")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
