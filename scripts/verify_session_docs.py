#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_session_docs.py — 세션 산출물 자동 검증 (1주차 파이프라인 계획 v2 §4.1)

자기선언 PASS를 대체하는 기계 검증. 리서치/콘텐츠 단계 산출물의
스키마·커버리지·D1~D6·출처ID 매핑·[C-슬러그] 포인터 해소·[미검증] 무결성·
초안 형식·중간 산출물 잔존·범위밖 diff를 점검한다.

검사 대상 — 리서치 **기본 5파일** + 초안(파일명 규약: sessions/N주차/):
  자료/N주차_콘텐츠리서치_결과.md      — 교시(구간)별 8항목 ①~⑧ (구간 인덱스층)
  자료/N주차_개념KB.md                  — 사실 정본(청크+ID RAG). 여기서는 **존재 여부와
                                          [C-슬러그] 참조 해소만** 본다. 청크 내부 최소깊이·
                                          G8 관점 검사는 scripts/verify_research_chunks.py 몫.
  자료/N주차_출처레지스트리.md          — 출처ID 표(고유ID·URL·확인일·공신력·구간·접근)
                                          + 「출처ID별 verbatim」 절(원문 정본, 없으면 WARN)
                                          + 도메인 편중·3급/[경험 진술] 0건 WARN(G8 관점 다양성)
  자료/N주차_실습안_검증결과.md         — 실습별 13항목 ①~⑬
  자료/N주차_결정요청사항.md            — 6열 표 + D1~D6
  초안.md                               — 4열 표·아이콘 범례·0번 메타·관통 문장·(선택)
  자료/ 잔존 중간 산출물(심층리서치·_vN 접미·커버리지) — WARN

출처 모델: 모든 사실 문장은 [S-###] 출처ID로 레지스트리와 연결. 내부 설계 근거도
등록(예: S-000=v4 강의안설계). 커버리지 빈칸은 [미검증]/[미확인]/[확인불가]/[예외승인] 태그로만 허용.
사실 모델: 결과.md·초안.md는 사실을 재서술하지 않고 [C-슬러그]로 개념KB 청크를 가리키는
포인터층이다 — 죽은 포인터는 곧 사실 소실이므로 FAIL로 막는다.

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
from collections import Counter
from fnmatch import fnmatch
from pathlib import Path
from urllib.parse import urlparse
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


CIRC8 = "①②③④⑤⑥⑦⑧"
CIRC13 = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬"
ALLOW_TAGS = ("[미검증]", "[미확인]", "[확인불가]", "[예외승인")
SRC_REF = re.compile(r"\[(S-\d{3,})\]")
CHUNK_REF = re.compile(r"\[C-[^\]\s]+\]")                       # 인라인 포인터 [C-슬러그]
CHUNK_REFS_COMMENT = re.compile(r"<!--\s*refs:\s*([^>]*?)-->")  # 초안 근거추적 주석
CHUNK_HEADING = re.compile(r"^##\s+\[(C-[^\]\s]+)\]", re.MULTILINE)  # 개념KB 청크 헤딩
URL_IN_CELL = re.compile(r"https?://[^\s)\]]+")
DOMAIN_SHARE_MAX = 0.40  # 리서치 §0 G8: 최다 도메인 40% 초과면 관점이 좁다는 신호
# 리서치 SKILL 7단계 수명 규칙 — 자료/에 남으면 안 되는 중간 산출물 파일명 패턴
LEFTOVER_PATTERNS = (
    ("심층리서치", re.compile(r"심층리서치")),
    ("버전접미", re.compile(r"_v\d+\.md$")),
    ("커버리지", re.compile(r"커버리지")),
)

ALLOWLIST = {
    "자료": ["sessions/*주차/자료/*", "courses/*/sessions/*주차/자료/*", ".omc/*"],
    "초안": ["sessions/*주차/초안.md", "sessions/*주차/*초안.md", "sessions/*주차/자료/*집필노트*", "courses/*/sessions/*주차/*초안.md", "courses/*/sessions/*주차/자료/*집필노트*", ".omc/*"],
    "검토": ["sessions/*주차/검토보고_*.md", "courses/*/sessions/*주차/검토보고_*.md", ".omc/*"],
}

results = []  # (check, status, detail)


def add(check, status, detail=""):
    results.append((check, status, detail))


def read(p):
    try:
        return p.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        return None


_DRAFT_FALLBACK_LOGGED = set()  # 폴백 INFO 중복 출력 방지(경로별 1회)


def resolve_draft(sess_dir, wk):
    """초안 파일 경로 해석: `N주차_초안.md`(접두어) 우선, 없으면 `초안.md`(레거시)로 폴백.
    레거시 파일이 실제로 존재할 때만 폴백 사실을 INFO로 1회 알린다(그 경로 기준 중복 없음).
    둘 다 없으면 조용히 무접두어 경로를 반환해 기존과 동일하게 '파일 없음' FAIL로 이어지게 둔다."""
    prefixed = sess_dir / f"{wk}주차_초안.md"
    if prefixed.exists():
        return prefixed
    legacy = sess_dir / "초안.md"
    if legacy.exists() and legacy not in _DRAFT_FALLBACK_LOGGED:
        _DRAFT_FALLBACK_LOGGED.add(legacy)
        print(f"INFO: 레거시 무접두어 초안 사용: {legacy}")
    return legacy


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


def collect_chunk_refs(text):
    """개념KB 청크 포인터 수집: 인라인 `[C-슬러그]` + 초안 근거추적 주석 `<!-- refs: C-a,C-b -->`.
    주석 안은 대괄호 없이 맨몸 슬러그로 적힐 수 있어 별도 파싱한다."""
    refs = {m.group(0)[1:-1].strip() for m in CHUNK_REF.finditer(text)}
    for m in CHUNK_REFS_COMMENT.finditer(text):
        for tok in m.group(1).split(","):
            tok = tok.strip().strip("[]").strip()
            if tok.startswith("C-") and len(tok) > 2:
                refs.add(tok)
    return {r for r in refs if r}


def check_research_result(text):
    tag = "콘텐츠리서치"
    if not has_meta(text):
        add(f"{tag}:메타헤더", "FAIL", "작성일·기준·대상 헤더 누락")
    else:
        add(f"{tag}:메타헤더", "PASS")
    secs = [(h, b) for h, b in split_sections(text) if re.match(r"^\d+\s*구간", h)]
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
    secs = [(h, b) for h, b in split_sections(text) if re.match(r"^실습\s*\d", h)]
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
    hdr = [(c or "") for c in reg_tbl[0]]
    url_i = next((i for i, c in enumerate(hdr) if "URL" in c.upper()), 1)
    cred_i = next((i for i, c in enumerate(hdr) if "공신력" in c), 3)
    empty_rows = 0
    domains, tier3 = Counter(), 0
    for r in reg_tbl[1:]:
        m = re.match(r"(S-\d{3,})", r[0])
        if m:
            ids.add(m.group(1))
            cell = r[url_i] if url_i < len(r) else ""
            u = URL_IN_CELL.search(cell)
            if u:  # 외부 출처만 집계(내부 설계 문서 S-000·S-001 등은 경로라 제외)
                netloc = urlparse(u.group(0)).netloc.lower()
                if netloc:
                    domains[netloc] += 1
            cred = r[cred_i] if cred_i < len(r) else ""
            if "3급" in cred or "[경험 진술]" in cred:
                tier3 += 1
        if any((not (c or "").strip()) for c in r[:6]) and not any(any(tg in c for tg in ALLOW_TAGS) for c in r):
            empty_rows += 1
    add(f"{tag}:ID수집", "PASS" if ids else "WARN", f"{len(ids)}개 ID")
    if empty_rows:
        add(f"{tag}:빈칸", "FAIL", f"빈 셀 행 {empty_rows}개")

    # 원문 정본 절: verbatim 전문은 레지스트리에만 둔다(개념KB는 핵심 한 문장 사본)
    if re.search(r"^#{1,6}.*verbatim", text, re.MULTILINE | re.IGNORECASE):
        add(f"{tag}:verbatim절", "PASS")
    else:
        add(f"{tag}:verbatim절", "WARN", "레지스트리가 원문 정본 — 「출처ID별 verbatim」 절 권장")

    # G8 관점 다양성: 도메인 편중·3급/[경험 진술] 유무 (기존 주차 소급 FAIL 방지로 WARN)
    total = sum(domains.values())
    if not total:
        add(f"{tag}:도메인편중", "SKIP", "외부 URL 출처 0건")
    else:
        top = domains.most_common(3)
        summary = "상위3: " + ", ".join(f"{d} {c}/{total}({c / total * 100:.0f}%)" for d, c in top)
        share = top[0][1] / total
        if share > DOMAIN_SHARE_MAX:
            add(f"{tag}:도메인편중", "WARN",
                f"최다 도메인 {top[0][0]} {share * 100:.0f}% > {DOMAIN_SHARE_MAX * 100:.0f}%"
                f" — 관점 편중 신호(G8) · {summary}")
        else:
            add(f"{tag}:도메인편중", "PASS", f"최다 {share * 100:.0f}% ≤ {DOMAIN_SHARE_MAX * 100:.0f}% · {summary}")
    if tier3:
        add(f"{tag}:3급·경험진술", "PASS", f"{tier3}건")
    else:
        add(f"{tag}:3급·경험진술", "WARN",
            "공신력 열에 3급·[경험 진술] 0건 — 관점 B(실무 사례)·C·D 재료 부족 신호(G8)")
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


def check_draft_slide_numbers(text):
    """초안 4열 표(#·슬라이드 제목·본문 문구·비유·멘트)의 # 열(슬라이드 번호)이
    주차 전체에서 유일한지 검사한다. 번호가 중복되면 report_draft_sync.py의
    초안 대 덱 대조나 create-slides 조립에서 어느 행을 가리키는지 모호해진다."""
    tag = "초안"
    seen = Counter()
    for t in parse_tables(text):
        if not t:
            continue
        hdr = [(c or "") for c in t[0]]
        if not (any("슬라이드 제목" in c for c in hdr) and any("본문" in c for c in hdr)):
            continue
        for r in t[1:]:
            if not r or not (r[0] or "").strip():
                continue
            m = re.match(r"^(\S+)", r[0].strip())
            if m:
                seen[m.group(1)] += 1
    dups = sorted(k for k, v in seen.items() if v > 1)
    if dups:
        add(f"{tag}:번호유일성", "FAIL",
            "중복 슬라이드 번호: " + ", ".join(f"{k}×{seen[k]}" for k in dups))
    else:
        add(f"{tag}:번호유일성", "PASS", f"{len(seen)}개 번호 전부 유일")


def check_leftovers(data_dir, wk, template_dir=None):
    """리서치 SKILL 7단계 수명 규칙: 조사 과정의 중간 산출물(심층리서치 원본·버전 사본·
    커버리지 대조표)은 자료/에 남기지 않는다. 사람이 직접 쓴 문서를 오탐할 수 있어 WARN."""
    tag = "잔존물"
    if not data_dir.is_dir():
        add(f"{tag}:중간산출물", "SKIP", f"{data_dir.name}/ 없음")
        return
    keep = {
        f"{wk}주차_콘텐츠리서치_결과.md",
        f"{wk}주차_개념KB.md",
        f"{wk}주차_출처레지스트리.md",
        f"{wk}주차_실습안_검증결과.md",
        f"{wk}주차_결정요청사항.md",
        "이미지-에셋.json",
        "이미지-프롬프트.md",
    }
    if template_dir and template_dir.is_dir():  # _template/자료/ 유래 파일(주차 접두 유무 무관)
        for tp in template_dir.iterdir():
            keep.add(tp.name)
            keep.add(f"{wk}주차_{tp.name}")
    hits = []
    for p in sorted(data_dir.glob("*.md")):
        if p.name in keep or p.name.replace(f"{wk}주차_", "", 1) in keep:
            continue
        why = [label for label, rx in LEFTOVER_PATTERNS if rx.search(p.name)]
        if why:
            hits.append(f"{p.name} ({'·'.join(why)})")
    if hits:
        add(f"{tag}:중간산출물", "WARN",
            f"{len(hits)}건 잔존 — 리서치 SKILL 7단계 수명 규칙: "
            f"_dev/설계기록/탐색-아카이브/{wk}주차/로 이동 또는 삭제: " + "; ".join(hits))
    else:
        add(f"{tag}:중간산출물", "PASS", "중간 산출물 잔존 없음")


def check_capability_claims(root, wk):
    """자기투사(리서치 §0 G6) 휴리스틱: 'AI/제품이 관찰·캡처를 못 한다'류 능력 단정을
    WARN으로 surface한다. 기계는 판정하지 않고 표면화만 — 능력 vs 범위 구분은 사람이 확인."""
    # 관찰·지각 대상 바로 뒤(~12자)에 부정이 오는 경우만 → "AI가 화면을 못 본다"류 능력 단정.
    # 프록시미티로 "Codex 위치 못 찾음 … 실측 필요"처럼 주어가 학생인 오탐을 배제.
    neg = ("못", "할 수 없", "없", "불가", "안 돼", "안 됨", "안됨")
    obs_re = re.compile(r"캡처|스크린샷|화면|관찰|실측")
    targets = [
        ("콘텐츠리서치", _session_dir(root, wk) / "자료" / f"{wk}주차_콘텐츠리서치_결과.md"),
        ("실습안", _session_dir(root, wk) / "자료" / f"{wk}주차_실습안_검증결과.md"),
        ("종합정리", _session_dir(root, wk) / "자료" / f"{wk}주차_리서치_종합정리.md"),
        ("초안", resolve_draft(_session_dir(root, wk), wk)),
    ]
    hits = []
    for label, p in targets:
        t = read(p)
        if not t:
            continue
        for i, line in enumerate(t.splitlines(), 1):
            for m in obs_re.finditer(line):
                if any(n in line[m.end():m.end() + 12] for n in neg):
                    hits.append(f"{label}:{i} «{line.strip()[:50]}»")
                    break
    if hits:
        add("자기투사:능력클레임", "WARN", "능력 vs 범위 확인 필요(G6): " + " / ".join(hits[:6]))
    else:
        add("자기투사:능력클레임", "PASS", "관찰·캡처 능력 단정 라인 없음")


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
    sess = _session_dir(root, wk)
    data = sess / "자료"
    files = {
        "result": data / f"{wk}주차_콘텐츠리서치_결과.md",
        "kb": data / f"{wk}주차_개념KB.md",
        "practice": data / f"{wk}주차_실습안_검증결과.md",
        "decision": data / f"{wk}주차_결정요청사항.md",
        "registry": data / f"{wk}주차_출처레지스트리.md",
        "draft": resolve_draft(sess, wk),
    }

    reg_ids, used_refs = set(), set()
    used_chunks = set()
    kb_text = read(files["kb"])

    if args.target in ("자료", "all"):
        for key, chk in (("result", check_research_result), ("practice", check_practice), ("decision", check_decision)):
            txt = read(files[key])
            if txt is None:
                add(f"파일:{files[key].name}", "FAIL", "파일 없음")
            else:
                chk(txt)
                if key == "result":
                    used_refs |= {m.group(1) for m in SRC_REF.finditer(txt)}
                    used_chunks |= collect_chunk_refs(txt)
        # 개념KB는 기본 5파일 중 사실 정본 — 존재만 강제하고, 청크 내부 깊이·G8 관점은
        # verify_research_chunks.py 담당(역할 중복 금지).
        if kb_text is None:
            add(f"파일:{files['kb'].name}", "FAIL", "파일 없음")
        else:
            add("개념KB:존재", "PASS",
                f"청크 {len(CHUNK_HEADING.findall(kb_text))}개 (내부 깊이·G8은 verify_research_chunks.py)")
        rtxt = read(files["registry"])
        if rtxt is None:
            add(f"파일:{files['registry'].name}", "FAIL", "파일 없음")
        else:
            reg_ids = check_registry(rtxt)
        check_leftovers(data, wk, root / "sessions" / "_template" / "자료")
        stext = read(data / f"{wk}주차_리서치_종합정리.md")
        if stext is None:
            add("종합정리:존재(선택)", "SKIP", "N주차_리서치_종합정리.md 없음 — 선택 산출물(사용자가 요청할 때만 산출)")
        else:
            add("종합정리:존재(선택)", "PASS")
            add("종합정리:성격표기", "PASS" if ("정본" in stext and ("요약" in stext or "종합" in stext)) else "WARN", "서두에 '정본은 기본 5파일' 명시 권장")

    if args.target in ("초안", "all"):
        dtxt = read(files["draft"])
        if dtxt is None:
            add(f"파일:{files['draft'].name}", "SKIP" if args.target == "all" else "FAIL", "파일 없음")
        else:
            check_draft(dtxt)
            check_draft_slide_numbers(dtxt)
            used_refs |= {m.group(1) for m in SRC_REF.finditer(dtxt)}
            used_chunks |= collect_chunk_refs(dtxt)

    # 출처ID 상호 참조: 사용된 [S-###]가 레지스트리에 실재하는가
    if used_refs or reg_ids:
        dangling = sorted(used_refs - reg_ids)
        if dangling:
            add("출처매핑:참조해소", "FAIL", f"레지스트리에 없는 출처ID {', '.join(dangling)}")
        else:
            add("출처매핑:참조해소", "PASS", f"참조 {len(used_refs)}개 전부 해소")

    # 청크 포인터 상호 참조: 결과.md·초안.md가 쓴 [C-슬러그]가 개념KB에 실재하는가.
    # 결과.md가 포인터층이 된 이상 죽은 포인터는 곧 사실 소실이다.
    if kb_text is None:
        add("개념KB:참조해소", "SKIP", "개념KB 없음 — 존재 검사가 이미 FAIL")
    elif used_chunks:
        kb_slugs = {m.group(1) for m in CHUNK_HEADING.finditer(kb_text)}
        dead = sorted(used_chunks - kb_slugs)
        if dead:
            add("개념KB:참조해소", "FAIL",
                f"개념KB에 없는 청크 슬러그 {len(dead)}개: " + ", ".join(dead))
        else:
            add("개념KB:참조해소", "PASS", f"참조 {len(used_chunks)}개 전부 해소")

    check_capability_claims(root, args.week)

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
