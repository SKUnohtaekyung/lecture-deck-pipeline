#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analyze_agent_usage.py — 에이전트 실행량·토큰·비용 계측기 (읽기 전용)

목적
  Claude Code 세션·워크플로의 원시 트랜스크립트(JSONL)에서 실행량을 집계해,
  리서치 스킬 리팩터링의 파라미터 산정 근거를 만든다.

⚠️ 이 스크립트는 **읽기 전용**이다. 어떤 파일도 생성·수정·삭제하지 않는다.
   로그는 제자리에서 읽는다(계획의 L-1 선택). 복사본을 만들지 않는다.

⚠️ 독립성의 한계
   이 계측기는 잠정 기준선을 산출한 것과 **같은 에이전트**가 작성했다.
   따라서 수치 일치는 "구현 일관성"을 뜻할 뿐 완전한 독립 검증이 아니다.
   아래 「정의·전제」를 사람이 직접 감사해야 최종 신뢰가 성립한다.

사용법
  python scripts/analyze_agent_usage.py                 # 2주차 리서치 기본 대상 + 기준선 대조
  python scripts/analyze_agent_usage.py --no-baseline   # 대조 없이 계측만
  python scripts/analyze_agent_usage.py --session <id> --workflows wf_a,wf_b
  python scripts/analyze_agent_usage.py --projects-dir <경로>
  python scripts/analyze_agent_usage.py --archive <아카이브 JSON 경로>   # 캘리브레이션 구간만
"""

from __future__ import annotations

import argparse
import collections
import glob
import io
import json
import math
import os
import statistics
import sys
from urllib.parse import urlsplit, urlunsplit

# ─────────────────────────────────────────────────────────────────────────────
# 정의·전제 — 「기준선 대조 처리 규칙」의 대조 5항목과 1:1 대응한다.
#   대조① 파서 동작        → PARSE_RULE
#   대조② 턴의 정의        → TURN_RULE
#   대조③ 캐시 토큰 집계   → TOKEN_RULE
#   대조④ 로그 누락        → 실행 시 「B. 로그 인벤토리」가 대상 외 워크플로를 경고
#   대조⑤ 모델 가격표      → PRICE_TABLE / PRICE_ASOF / CACHE_MULTIPLIER
# ─────────────────────────────────────────────────────────────────────────────

PARSE_RULE = (
    "JSONL을 한 줄씩 읽어 json.loads에 성공한 레코드만 사용한다. "
    "레코드의 message가 dict인 경우만 집계 대상으로 삼는다. "
    "파싱 실패 줄은 건너뛰되 그 수를 보고한다(조용한 누락 금지)."
)

TURN_RULE = (
    "1턴 = message.usage 필드를 가진 assistant 레코드 1건. "
    "즉 '모델 응답 1회'를 센다. 한 응답이 여러 tool_use 블록을 담을 수 있으므로 "
    "턴 수 != 툴 호출 수다. 툴 호출은 tool_use 블록 단위로 따로 센다. "
    "대안 정의(툴 호출 수 / HTTP 요청 수)를 쓰면 값이 달라진다 — 대조 시 이 항목을 먼저 확인할 것."
)

TOKEN_RULE = (
    "usage의 4개 필드를 그대로 합산한다: "
    "input_tokens(신규 입력) + cache_creation_input_tokens(캐시 생성) + "
    "cache_read_input_tokens(캐시 읽기) + output_tokens(출력). "
    "'총 처리 토큰'은 이 4개의 합이며 고유 토큰 수가 아니다 — "
    "캐시 읽기는 이전 턴의 컨텍스트가 재청구된 것이라 중복 계수된다. "
    "이 값은 처리량 지표이지 비용 지표가 아니다(비용은 단가 배수를 적용한 E절 참조)."
)

URL_CANON_RULE = (
    "canonical URL = scheme를 https로 통일, 호스트 소문자화 + 선행 'www.' 제거, "
    "경로 끝 '/' 제거(빈 경로는 '/'), 쿼리·프래그먼트 제거. "
    "이 규칙에 따라 중복 판정이 달라지므로 대조 시 명시할 것."
)

# 가격표 — 출처: claude-api 스킬 캐시본. 단위 $/MTok.
PRICE_ASOF = "2026-06-24"
PRICE_TABLE = {
    "claude-opus-4-8": (5.0, 25.0),
    "claude-opus-4-7": (5.0, 25.0),
    "claude-opus-4-6": (5.0, 25.0),
    "claude-sonnet-5": (3.0, 15.0),   # 정가. 도입가($2/$10, ~2026-08-31)는 적용하지 않음
    "claude-sonnet-4-6": (3.0, 15.0),
    "claude-fable-5": (10.0, 50.0),
    "claude-haiku-4-5": (1.0, 5.0),
}
CACHE_WRITE_MULT = 1.25   # 5분 TTL 캐시 쓰기 = 입력 단가 × 1.25
CACHE_READ_MULT = 0.10    # 캐시 읽기 = 입력 단가 × 0.1

COST_FORMULA = (
    "비용 = 신규입력×입력단가 + 캐시생성×입력단가×1.25 + "
    "캐시읽기×입력단가×0.1 + 출력×출력단가"
)

COST_CAVEAT = (
    "API 정가 환산 추정치이며 구독 플랜의 실제 청구액이 아니다. "
    "캐시 쓰기 배수는 5분 TTL 기준이다(1시간 TTL이면 2.0)."
)

# ─────────────────────────────────────────────────────────────────────────────
# 기본 대상 — 2주차 리서치 실행
# ─────────────────────────────────────────────────────────────────────────────

DEFAULT_PROJECTS_DIR = os.path.expanduser(
    "~/.claude/projects/C--Users-miso-Desktop-template"
)
DEFAULT_SESSION = "23c53893-1fa0-4239-b7d3-e23df646cdcc"
DEFAULT_WORKFLOWS = [
    "wf_7ab0d31d-b8b",   # 1차 팬아웃 (리서치 워커 14 + 실습 구축 2)
    "wf_bc18c30a-630",   # R15 보강 (모델 전환 중 고아)
    "wf_e66bb006-0d1",   # R15 보강 (sonnet 재실행, 사용자 중단)
    "wf_5a31448a-a31",   # R15 보강 (최종 채택)
]
DEFAULT_ARCHIVE = "_dev/설계기록/탐색-아카이브/2주차/wg2e6h3ua_1차팬아웃_원본결과.json"

# 낭비로 분류하는 워크플로(산출물이 채택되지 않은 실행)
DISCARDED_WORKFLOWS = {"wf_bc18c30a-630", "wf_e66bb006-0d1"}

# ─────────────────────────────────────────────────────────────────────────────
# 잠정 기준선 — 계획 파일 rev.2 「잠정 기준선」 표의 값.
# 확정 근거가 아니라 대조 대상이다. 불일치 시 어느 쪽도 임의 채택하지 않는다.
# ─────────────────────────────────────────────────────────────────────────────

PROVISIONAL_BASELINE = {
    "main_agents": 1,
    "main_turns": 321,
    "main_total": 83_134_129,
    "worker_agents": 19,
    "worker_turns": 1_169,
    "worker_total": 95_664_147,
    "grand_total": 178_798_276,
    "cache_read": 166_037_288,
    "cache_creation": 11_205_220,
    "output": 1_408_902,
    "input": 146_866,
    "worker_turn_min": 42,
    "worker_turn_median": 58,
    "worker_turn_max": 89,
    # ── 아래는 rev.2 대조에서 정정됨(rev.3). 정정 사유는 CORRECTIONS 참조 ──
    "worker_first_cc_mean": 35_044.63,      # ⓐ 1턴 캐시생성 평균 (독립 검증 완료)
    "worker_first_prompt_mean": 41_199.79,  # 첫 턴 관측 입력량 평균 = 782,796/19
    "worker_first_cr_mean": 6_153.16,       # 첫 턴 cache read 평균 = 116,910/19
    "webfetch_worker": 212,                 # ① 호출 수(워커만)
    "webfetch_all": 214,                    # ① 호출 수(전 에이전트)
    "websearch_all": 145,
    "url_unique_all": 193,                  # ② canonical 고유 URL 수
    "dup_url_kinds_worker": 15,             # ③ 중복 URL '종류' 수(워커만)
    "dup_url_kinds_all": 16,                # ③ 중복 URL '종류' 수(전 에이전트)
    "url_dup_worker": 19,                   # ④ 고유 URL 초과 추가 호출 수(워커만)
    "url_dup_all": 21,                      # ④ 고유 URL 초과 추가 호출 수(전 에이전트)
    "returns": 17,
    "returns_chars": 155_962,
    "discarded_tokens": 7_521_130,        # 정정: 7,505,311은 출력 토큰 누락(산술 오류)
    "cost_total": 198.73,
    "cost_main": 86.14,
    "cost_worker": 112.59,
}

# rev.2 → rev.3 정정 기록. 계획 파일 「잠정 기준선」과 반드시 동기화할 것.
CORRECTIONS = [
    ("워커 시작 컨텍스트 평균", "35,045", "35,044.63",
     "반올림 vs 절사 차이. 참값은 665,848/19 = 35,044.63. "
     "기준선이 반올림값을 확정치처럼 적었다. 정수 비교 대신 허용오차 비교로 전환."),
    ("WebFetch 호출", "212", "212(워커만) / 214(전 에이전트)",
     "기준선은 워커만 집계했으나 범위를 명시하지 않았다. "
     "메인 에이전트가 WebFetch를 2회 직접 호출했다(리드의 Sites 출처 재확인). "
     "값이 틀린 게 아니라 범위 표기가 없던 것 — 두 범위를 분리 등재."),
    ("중복 URL 호출", "19", "19(워커만) / 21(전 에이전트)",
     "위와 같은 원인. 메인의 2회 fetch가 워커가 이미 연 URL이라 "
     "고유 URL은 193으로 불변인 채 중복만 2 증가."),
    ("폐기된 실행 토큰", "7,505,311", "7,521,130",
     "산술 오류. wf_bc18c30a-630 합산 시 출력 토큰 15,819을 누락했다. "
     "(wf_e66bb006-0d1은 정상 합산돼 있었음 — 수동 집계의 비일관성)"),
    ("'워커 시작 컨텍스트' 지표 자체", "단일 지표 35,044.63",
     "첫 턴 cache creation / cache read / 관측 입력량 세 값으로 분리",
     "**독립 검증에서 새로 발견된 정의 결함.** 19개 워커 중 5개가 1턴부터 "
     "캐시읽기 23,382을 받았다(형제 워커가 먼저 같은 프리픽스를 캐시에 올림). "
     "cache_creation만 세면 이들의 실제 시작 프롬프트를 과소평가한다. "
     "'시작 컨텍스트'라는 단일 표현을 쓰지 말고 네 값을 구분해 인용한다. 산술 자체는 양쪽 다 검증됨."),
]


# ─────────────────────────────────────────────────────────────────────────────
# 수집
# ─────────────────────────────────────────────────────────────────────────────

class AgentStat:
    __slots__ = ("label", "kind", "wf", "turns", "inp", "cc", "cr", "out",
                 "first_cc", "first_prompt", "first_cr", "tools", "models", "fetch_urls",
                 "queries", "returns", "bad_lines", "ctx_seq", "no_usage_msgs")

    def __init__(self, label, kind, wf=""):
        self.label = label
        self.kind = kind          # "main" | "worker"
        self.wf = wf
        self.turns = 0
        self.inp = self.cc = self.cr = self.out = 0
        # ⚠️ 1턴 지표는 두 가지를 반드시 구분한다.
        #   first_cc     = 1턴의 cache_creation_input_tokens
        #   first_prompt = 1턴의 (input + cache_creation + cache_read)
        # 형제 워커가 먼저 같은 프리픽스를 캐시에 올려두면 1턴부터 cache_read가
        # 잡힌다(2주차 실측: 19개 중 5개가 1턴에 23,382 캐시읽기).
        # 이때 first_cc는 실제 시작 프롬프트를 **과소평가**한다.
        self.first_cc = None
        self.first_prompt = None
        self.first_cr = None
        self.tools = collections.Counter()
        self.models = collections.Counter()
        self.fetch_urls = []      # 원본 URL 문자열
        self.queries = []
        self.returns = []         # StructuredOutput 입력 직렬화 길이(문자)
        self.bad_lines = 0
        self.no_usage_msgs = 0    # usage 없는 assistant 레코드 수(경고용)
        self.ctx_seq = []         # 턴별 프롬프트 크기(cc+cr)

    @property
    def total(self):
        return self.inp + self.cc + self.cr + self.out

    @property
    def prompt_total(self):
        """턴마다 모델이 읽은 입력의 총합(캐시 생성 + 캐시 읽기)."""
        return self.cc + self.cr


# 실행 중 수집되는 이상 징후. 조용히 넘기지 않고 마지막에 전부 보고한다.
UNKNOWN = {
    "models": collections.Counter(),                # 가격표 미등재 모델
    "missing_usage_fields": collections.Counter(),  # usage에 빠진 필드 조합
    "bad_lines": [],                                # (파일, 줄번호, 앞 80자)
}


def canon_url(u: str) -> str:
    try:
        s = urlsplit(u.strip())
        host = s.netloc.lower()
        if host.startswith("www."):
            host = host[4:]
        path = s.path.rstrip("/") or "/"
        return urlunsplit(("https", host, path, "", ""))
    except Exception:
        return u.strip()


def collect(path: str, label: str, kind: str, wf: str = "") -> AgentStat:
    st = AgentStat(label, kind, wf)
    with io.open(path, encoding="utf-8", errors="replace") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                st.bad_lines += 1
                UNKNOWN["bad_lines"].append(
                    (os.path.basename(path), lineno, line[:80]))
                continue
            msg = rec.get("message")
            if not isinstance(msg, dict):
                continue

            usage = msg.get("usage")
            if usage:                                   # ← TURN_RULE
                st.turns += 1
                missing = [k for k in ("input_tokens",
                                       "cache_creation_input_tokens",
                                       "cache_read_input_tokens",
                                       "output_tokens") if k not in usage]
                if missing:
                    UNKNOWN["missing_usage_fields"][tuple(missing)] += 1
                inp = usage.get("input_tokens", 0) or 0
                cc = usage.get("cache_creation_input_tokens", 0) or 0
                cr = usage.get("cache_read_input_tokens", 0) or 0
                out = usage.get("output_tokens", 0) or 0
                st.inp += inp
                st.cc += cc
                st.cr += cr
                st.out += out
                st.ctx_seq.append(cc + cr)
                if st.first_cc is None:
                    st.first_cc = cc
                    st.first_cr = cr
                    st.first_prompt = inp + cc + cr
                model = msg.get("model") or "?"
                st.models[model] += 1
                if model not in PRICE_TABLE:
                    UNKNOWN["models"][model] += 1
            elif msg.get("role") == "assistant":
                st.no_usage_msgs += 1

            content = msg.get("content")
            if isinstance(content, list):
                for blk in content:
                    if not (isinstance(blk, dict) and blk.get("type") == "tool_use"):
                        continue
                    name = blk.get("name")
                    st.tools[name] += 1
                    inputs = blk.get("input") or {}
                    if name == "WebFetch" and inputs.get("url"):
                        st.fetch_urls.append(inputs["url"])
                    elif name == "WebSearch" and inputs.get("query"):
                        st.queries.append(inputs["query"])
                    elif name == "StructuredOutput":
                        st.returns.append(
                            len(json.dumps(inputs, ensure_ascii=False))
                        )
    return st


def pearson(xs, ys):
    n = len(xs)
    if n < 2:
        return float("nan")
    mx, my = sum(xs) / n, sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return num / (dx * dy) if dx and dy else float("nan")


def cost_of(model, inp, cc, cr, out):
    """모델별 API 정가 환산. 미등재 모델은 None(집계에서 제외하고 별도 보고)."""
    if model not in PRICE_TABLE:
        return None
    pin, pout = PRICE_TABLE[model]
    return (inp * pin
            + cc * pin * CACHE_WRITE_MULT
            + cr * pin * CACHE_READ_MULT
            + out * pout) / 1e6


# ─────────────────────────────────────────────────────────────────────────────
# 출력
# ─────────────────────────────────────────────────────────────────────────────

def hr(title):
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


def section_definitions():
    hr("A. 정의·전제 (대조 5항목 — 사람이 감사할 것)")
    print(f"[대조①] 파서 동작\n    {PARSE_RULE}\n")
    print(f"[대조②] 턴의 정의\n    {TURN_RULE}\n")
    print(f"[대조③] 캐시 토큰 집계\n    {TOKEN_RULE}\n")
    print(f"[대조④] 로그 누락\n    B절의 인벤토리가 대상 외 워크플로를 경고한다.\n")
    print(f"[대조⑤] 모델 가격표 (기준일 {PRICE_ASOF}, $/MTok)")
    for m, (a, b) in sorted(PRICE_TABLE.items()):
        print(f"    {m:22} 입력 ${a:<6} 출력 ${b}")
    print(f"    캐시 쓰기 배수 {CACHE_WRITE_MULT} · 캐시 읽기 배수 {CACHE_READ_MULT}")
    print(f"    {COST_FORMULA}")
    print(f"    ※ {COST_CAVEAT}\n")
    print(f"[URL 정규화]\n    {URL_CANON_RULE}")


def section_inventory(projects_dir, session, workflows, main_path, worker_files):
    hr("B. 로그 인벤토리 (대조④ 로그 누락)")
    print(f"projects-dir : {projects_dir}")
    print(f"session      : {session}")
    print(f"메인 로그    : {'OK' if main_path else '없음'}  {main_path or ''}")
    print()
    print(f"{'워크플로':22}{'에이전트':>8}  상태")
    for wf in workflows:
        n = len(worker_files.get(wf, []))
        mark = "대상(폐기분)" if wf in DISCARDED_WORKFLOWS else "대상"
        print(f"{wf:22}{n:>8}  {mark}")

    # 대상 외 워크플로 탐지
    wf_root = os.path.join(projects_dir, session, "subagents", "workflows")
    found = set()
    if os.path.isdir(wf_root):
        found = {d for d in os.listdir(wf_root)
                 if os.path.isdir(os.path.join(wf_root, d))}
    extra = sorted(found - set(workflows))
    if extra:
        print()
        print("⚠️ 이 세션에 있으나 대상에 포함되지 않은 워크플로:")
        for e in extra:
            n = len(glob.glob(os.path.join(wf_root, e, "agent-*.jsonl")))
            print(f"    {e}  (에이전트 {n})  ← 누락 여부 확인 필요")
    else:
        print("\n대상 외 워크플로: 없음 (세션 내 전수 포함)")


def section_agents(stats):
    hr("C. 에이전트별 실행량")
    hdr = (f"{'구분':6}{'워크플로':16}{'에이전트':11}{'턴':>5}{'툴':>5}"
           f"{'fetch':>6}{'srch':>5}{'신규입력':>10}{'캐시생성':>11}"
           f"{'캐시읽기':>12}{'출력':>9}")
    print(hdr)
    print("-" * len(hdr))
    for s in sorted(stats, key=lambda x: (x.kind != "main", -x.cr)):
        print(f"{s.kind:6}{s.wf[:15]:16}{s.label:11}{s.turns:5}"
              f"{sum(s.tools.values()):5}{s.tools.get('WebFetch', 0):6}"
              f"{s.tools.get('WebSearch', 0):5}{s.inp:10,}{s.cc:11,}"
              f"{s.cr:12,}{s.out:9,}")
    section_anomalies(stats)


def section_anomalies(stats):
    """이상 징후를 조용히 넘기지 않고 전부 보고한다."""
    print("\n[이상 징후 — 조용한 누락 방지]")
    bad = sum(s.bad_lines for s in stats)
    print(f"  파싱 실패 줄        : {bad}건")
    for f, ln, snip in UNKNOWN["bad_lines"][:10]:
        print(f"      {f}:{ln}  {snip}")
    if bad > 10:
        print(f"      … 외 {bad-10}건")

    nu = sum(s.no_usage_msgs for s in stats)
    print(f"  usage 없는 assistant: {nu}건 (턴으로 세지 않음)")

    mf = UNKNOWN["missing_usage_fields"]
    print(f"  usage 필드 누락     : {sum(mf.values())}건")
    for combo, n in mf.most_common():
        print(f"      누락 {list(combo)} → {n}건 (0으로 처리)")

    um = UNKNOWN["models"]
    print(f"  가격표 미등재 모델  : {len(um)}종")
    for m, n in um.most_common():
        print(f"      {m} ({n}턴) → 토큰은 집계, 비용은 제외")


def agg(stats, kind=None):
    sel = [s for s in stats if kind is None or s.kind == kind]
    return {
        "agents": len(sel),
        "turns": sum(s.turns for s in sel),
        "inp": sum(s.inp for s in sel),
        "cc": sum(s.cc for s in sel),
        "cr": sum(s.cr for s in sel),
        "out": sum(s.out for s in sel),
        "total": sum(s.total for s in sel),
    }


def section_totals(stats):
    hr("D. 집계")
    m, w, a = agg(stats, "main"), agg(stats, "worker"), agg(stats)
    print(f"{'구분':8}{'에이전트':>8}{'턴':>7}{'총 처리 토큰':>16}{'비중':>8}")
    for name, d in (("메인", m), ("워커", w), ("합계", a)):
        pct = f"{d['total']/a['total']*100:.1f}%" if a["total"] else "-"
        print(f"{name:8}{d['agents']:>8}{d['turns']:>7}{d['total']:>16,}{pct:>8}")

    hr("E. 토큰 종류별 — 처리량 비중과 비용 비중은 다르다")
    tot = a["total"]
    rows = [("캐시 읽기", a["cr"], CACHE_READ_MULT),
            ("캐시 생성", a["cc"], CACHE_WRITE_MULT),
            ("출력", a["out"], None),
            ("신규 입력", a["inp"], 1.0)]
    print(f"{'종류':10}{'토큰':>16}{'처리량 비중':>12}")
    for name, v, _ in rows:
        print(f"{name:10}{v:>16,}{(v/tot*100 if tot else 0):>11.1f}%")
    return m, w, a


def section_cost_from_files(files, label):
    """파일을 다시 순회하며 모델별 토큰을 분해해 비용을 환산한다."""
    per = collections.defaultdict(lambda: collections.Counter())
    for path in files:
        with io.open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                msg = rec.get("message")
                if not isinstance(msg, dict):
                    continue
                u = msg.get("usage")
                if not u:
                    continue
                k = msg.get("model") or "?"
                per[k]["inp"] += u.get("input_tokens", 0) or 0
                per[k]["cc"] += u.get("cache_creation_input_tokens", 0) or 0
                per[k]["cr"] += u.get("cache_read_input_tokens", 0) or 0
                per[k]["out"] += u.get("output_tokens", 0) or 0
                per[k]["turns"] += 1
    print(f"\n[{label}]")
    print(f"{'모델':22}{'턴':>6}{'신규입력':>10}{'캐시생성':>11}"
          f"{'캐시읽기':>12}{'출력':>9}{'환산$':>10}")
    sub = 0.0
    unpriced = []
    for k, v in sorted(per.items(), key=lambda x: -x[1]["cr"]):
        c = cost_of(k, v["inp"], v["cc"], v["cr"], v["out"])
        if c is None:
            unpriced.append(k)
            cs = "n/a"
        else:
            sub += c
            cs = f"{c:.2f}"
        print(f"{k:22}{v['turns']:>6}{v['inp']:>10,}{v['cc']:>11,}"
              f"{v['cr']:>12,}{v['out']:>9,}{cs:>10}")
    print(f"{'소계':22}{'':>6}{'':>10}{'':>11}{'':>12}{'':>9}{sub:>10.2f}")
    if unpriced:
        print(f"  ⚠️ 가격표 미등재(비용 제외): {', '.join(unpriced)}")
    return sub, per


def _url_scope(stats, kind):
    """kind=None이면 전 에이전트, 'worker'면 워커만."""
    sel = [s for s in stats if kind is None or s.kind == kind]
    fetch = [(s.label, u) for s in sel for u in s.fetch_urls]
    queries = [q for s in sel for q in s.queries]
    canon = [(a, canon_url(u)) for a, u in fetch]
    uniq = {c for _, c in canon}
    by_url = collections.Counter(c for _, c in canon)
    agents_per = collections.defaultdict(set)
    for a, c in canon:
        agents_per[c].add(a)
    # ⚠️ 용어를 엄격히 분리한다 — 혼동하면 서로 다른 수가 같은 이름으로 인용된다.
    #   calls          ① 전체 호출 수
    #   unique_urls    ② canonical 고유 URL 수
    #   dup_url_kinds  ③ 2회 이상 호출된 URL '종류' 수
    #   excess_calls   ④ 고유 URL을 초과한 추가 호출 수 (= ① − ②)
    # ③과 ④는 다른 값이다. 2주차 워커 기준 ③=15, ④=19.
    return {
        "calls": len(fetch),
        "unique_urls": len(uniq),
        "dup_url_kinds": sum(1 for n in by_url.values() if n > 1),
        "excess_calls": len(canon) - len(uniq),
        "cross_agent_urls": sum(1 for s in agents_per.values() if len(s) > 1),
        "search": len(queries),
        "search_uniq": len(set(queries)),
        "by_url": by_url,
        "agents_per": agents_per,
    }


def section_urls(stats):
    """⚠️ 집계 범위(전 에이전트 vs 워커만)에 따라 값이 달라진다 — 둘 다 보고한다."""
    hr("F. URL — 검색·원문 확인·중복")
    allsc = _url_scope(stats, None)
    wsc = _url_scope(stats, "worker")
    print(f"canonical 정규화 규칙: {URL_CANON_RULE}\n")
    if not allsc["calls"]:
        print("WebFetch 호출 없음")
        return {"all": allsc, "worker": wsc}

    print("⚠️ 집계 범위와 용어에 따라 값이 달라진다. 인용 시 둘 다 명시할 것.\n")
    print(f"{'지표':34}{'전 에이전트':>14}{'워커만':>12}{'메인 기여':>12}")
    print("-" * 72)
    for key, name in (
            ("calls", "① 전체 호출 수"),
            ("unique_urls", "② canonical 고유 URL 수"),
            ("dup_url_kinds", "③ 중복된 URL '종류' 수(≥2회)"),
            ("excess_calls", "④ 고유 URL 초과 추가 호출 수(①−②)"),
            ("cross_agent_urls", "  에이전트 간 중복 URL 종류"),
            ("search", "  WebSearch 호출"),
            ("search_uniq", "  고유 쿼리")):
        print(f"{name:34}{allsc[key]:>14}{wsc[key]:>12}"
              f"{allsc[key]-wsc[key]:>12}")

    def _pct(d):
        return (f"{d['excess_calls']/d['calls']*100:.1f}%"
                if d["calls"] else "해당 없음(호출 0)")
    print(f"\n📌 ③과 ④는 다른 값이다. '중복률'이라는 말은 쓰지 않는다 —")
    print(f"   ④/① (초과 호출 비율): 전 에이전트 {_pct(allsc)} · "
          f"워커만 {_pct(wsc)}")
    if allsc["search"]:
        print(f"   검색:원문확인(전체) = 1 : {allsc['calls']/allsc['search']:.2f}")

    if allsc["calls"] != wsc["calls"]:
        print(f"\n📌 메인 에이전트가 WebFetch를 {allsc['calls']-wsc['calls']}회 직접 호출했다 "
              f"— 워커가 이미 연 URL을 리드가 재확인한 계층 간 중복"
              f"(고유 URL은 {wsc['unique_urls']}→{allsc['unique_urls']}로 불변).")

    print("\n상위 중복 URL (전 에이전트 기준):")
    for u, n in allsc["by_url"].most_common(8):
        if n > 1:
            print(f"  {n}회 (에이전트 {len(allsc['agents_per'][u])}명)  {u[:78]}")
    return {"all": allsc, "worker": wsc}


def section_returns(stats):
    hr("G. 워커 반환물 (메인 컨텍스트 유입량)")
    sizes = [n for s in stats for n in s.returns]
    if not sizes:
        print("StructuredOutput 반환 없음")
        return {}
    print(f"반환 건수 : {len(sizes)}")
    print(f"합계      : {sum(sizes):,}자")
    print(f"min / median / max : {min(sizes):,} / "
          f"{statistics.median(sizes):,.0f} / {max(sizes):,}")
    print(f"\n※ 토큰 환산은 하지 않는다 — 한글 토크나이저 비율이 확정되지 않았다.")
    print(f"  (문자 수만 확정치로 쓰고, 토큰 추정이 필요하면 count_tokens로 별도 측정)")
    return {"returns": len(sizes), "chars": sum(sizes)}


def section_correlation(stats):
    hr("H. 상관 (⚠️ 상관이지 인과가 아니다)")
    ws = [s for s in stats if s.kind == "worker"]
    if len(ws) < 3:
        print("워커 3개 미만 — 상관 생략")
        return
    T = [s.turns for s in ws]
    CR = [s.cr for s in ws]
    CC = [s.cc for s in ws]
    F = [s.tools.get("WebFetch", 0) for s in ws]
    print(f"n = {len(ws)} 워커")
    print(f"  턴 수   vs 캐시읽기 : r = {pearson(T, CR):+.3f}")
    print(f"  턴 수²  vs 캐시읽기 : r = {pearson([t*t for t in T], CR):+.3f}")
    print(f"  fetch   vs 캐시생성 : r = {pearson(F, CC):+.3f}")
    print(f"  fetch   vs 캐시읽기 : r = {pearson(F, CR):+.3f}")
    print(f"  턴 수   vs 캐시생성 : r = {pearson(T, CC):+.3f}")
    print()
    ts = sorted(T)
    print(f"워커 턴 분포     : min {ts[0]} / median {statistics.median(ts):.0f} / "
          f"mean {statistics.mean(ts):.1f} / max {ts[-1]}")
    fcc = [s.first_cc or 0 for s in ws]
    fpr = [s.first_prompt or 0 for s in ws]
    warm = sum(1 for s in ws if (s.first_cr or 0) > 0)
    tot_prompt = sum(s.prompt_total for s in ws)
    tot_turns = sum(T)

    fcr = [s.first_cr or 0 for s in ws]
    print(f"\n[첫 턴 지표 — 네 값을 서로 구분해 인용한다]")
    print(f"  첫 턴 cache creation 평균 : {statistics.mean(fcc):,.2f} "
          f"(min {min(fcc):,} / max {max(fcc):,})")
    print(f"  첫 턴 cache read 평균     : {statistics.mean(fcr):,.2f} "
          f"(비0 워커 {sum(1 for v in fcr if v)}/{len(ws)})")
    print(f"  첫 턴 관측 입력량 평균    : {statistics.mean(fpr):,.2f} "
          f"(min {min(fpr):,} / max {max(fpr):,})   ← 신규입력+캐시생성+캐시읽기")
    if warm:
        print(f"  ⚠️ 워커 {warm}/{len(ws)}개가 **1턴부터 캐시읽기**를 받았다"
              f"(형제 워커가 먼저 같은 프리픽스를 캐시에 올림).")
        print(f"     → ⓐ는 이들의 실제 시작 프롬프트를 과소평가한다. "
              f"'시작 컨텍스트'라는 단일 표현을 쓰지 말고 네 값을 구분해 인용한다.")
    if tot_turns:
        print(f"\n[전체 턴별 실제 usage 합계 — 측정값]")
        print(f"  워커 캐시생성 합계 : {sum(s.cc for s in ws):,}")
        print(f"  워커 캐시읽기 합계 : {sum(s.cr for s in ws):,}")
        print(f"  워커 입력 총합     : {tot_prompt:,}  (턴당 평균 {tot_prompt/tot_turns:,.0f})")
        print()
        print("  ⛔ '첫 턴 평균 × 전체 턴 수'는 비용 귀속값으로 쓰지 않는다.")
        print("     1턴 값이 매 턴 그대로 재청구된다는 가정이 성립하지 않고"
              "(컨텍스트는 턴마다 커진다),")
        print("     그 곱은 baseline 비중도 고정 시작 비용도 아니다. "
              "산술 참고값으로만 취급한다.")
        print("     사용 금지 표현: '워커 고유 시작 비용', '전체 비용의 NN%'")


def percentile(sorted_vals, q):
    """선형보간 백분위수. numpy 없이 계산한다."""
    if not sorted_vals:
        return 0.0
    if len(sorted_vals) == 1:
        return float(sorted_vals[0])
    pos = (len(sorted_vals) - 1) * q
    lo = int(math.floor(pos))
    hi = min(lo + 1, len(sorted_vals) - 1)
    frac = pos - lo
    return sorted_vals[lo] * (1 - frac) + sorted_vals[hi] * frac


def section_stoplines(stats):
    """§7.4 비상 중단선 — 과거 워커 분포에서 P95와 max를 모두 계산한다.

    ⚠️ 비상 중단선은 **최종 정책 예산이 아니다.** 폭주 방지용 브레이크다.
    ⚠️ 과거 분포는 **워커 1명이 청크 여러 개를 담당한** 실행에서 나왔다.
       청크 1개 단위 실행에 그대로 적용하면 느슨하다 — 그래서 브레이크로만 쓴다.
    """
    hr("K. 비상 중단선 산정 (§7.4) — 정책 예산 아님")
    ws = [s for s in stats if s.kind == "worker"]
    if not ws:
        print("워커 없음 — 생략")
        return {}
    print(f"표본: 과거 워커 {len(ws)}개 (각 워커가 청크 여러 개를 담당한 실행)")
    print("규칙: P95와 max를 모두 계산 → 더 보수적(낮은) 값 사용.")
    print("      단 n이 작아 P95가 불안정하면 max를 사용한다(임의 여유 배수 금지).")
    print()

    metrics = {
        "agentic turns": [s.turns for s in ws],
        "WebSearch": [s.tools.get("WebSearch", 0) for s in ws],
        "WebFetch": [s.tools.get("WebFetch", 0) for s in ws],
        "처리 토큰": [s.total for s in ws],
        "동일 URL 재호출": [
            len(s.fetch_urls) - len({canon_url(u) for u in s.fetch_urls})
            for s in ws],
    }
    n = len(ws)
    unstable = n < 30      # P95 안정성 기준
    print(f"{'지표':18}{'min':>10}{'median':>11}{'P95':>13}{'max':>13}{'채택':>13}")
    print("-" * 78)
    out = {}
    for name, vals in metrics.items():
        sv = sorted(vals)
        p95 = percentile(sv, 0.95)
        mx = sv[-1]
        chosen = mx if unstable else min(p95, mx)
        out[name] = dict(min=sv[0], median=statistics.median(sv),
                         p95=p95, max=mx, chosen=chosen)
        print(f"{name:18}{sv[0]:>10,}{statistics.median(sv):>11,.0f}"
              f"{p95:>13,.1f}{mx:>13,}{chosen:>13,.0f}")
    print()
    print(f"n={n} < 30 → **P95 불안정으로 판단, historical max를 채택**"
          if unstable else f"n={n} → P95 채택")
    print()
    print("⚠️ G8 최소 관점 확보 하한과의 관계")
    print("   P0는 A + (B/C/D 중 2) = 최소 3개 관점이 필요하고, 관점마다 최소 1개")
    print("   출처를 확인해야 하므로 **fetch 하한은 청크당 최소 3회**다.")
    print(f"   채택된 fetch 중단선 {out['WebFetch']['chosen']:.0f}회는 이 하한보다 크므로 "
          f"G8 달성을 막지 않는다.")
    print()
    print("⚠️ 중단선 도달 시 그 표본은 `right-censored`로 기록한다.")
    print("   완료값·실패값의 평균에 정상 표본처럼 넣지 않는다.")
    return out


def section_calibration(archive_path):
    """캘리브레이션 입력: P0/P1/P2별 조사량, 채택률, 접근 실패율, 내용 불일치율."""
    hr("I. 캘리브레이션 입력 (Phase 3 예산 산정 근거)")
    if not archive_path or not os.path.exists(archive_path):
        print(f"아카이브 없음 — 건너뜀 ({archive_path})")
        return
    obj = json.load(io.open(archive_path, encoding="utf-8"))
    res = (obj.get("result") or {}).get("research") or []
    if not res:
        print("research 배열 없음 — 건너뜀")
        return

    prio_chunks = collections.Counter()
    scope_chunks = collections.Counter()
    per_worker = []
    adopted, rejected = 0, 0
    cred = collections.Counter()
    access = collections.Counter()
    reasons = collections.Counter()

    for w in res:
        chunks = w.get("chunks") or []
        reg = w.get("registry") or []
        rej = w.get("rejected") or []
        pc = collections.Counter(c.get("priority", "?") for c in chunks)
        for k, v in pc.items():
            prio_chunks[k] += v
        for c in chunks:
            scope_chunks[c.get("scope", "?")] += 1
        adopted += len(reg)
        rejected += len(rej)
        for r in reg:
            cred[str(r.get("cred", "?"))] += 1
            access[str(r.get("access", "?")).split("(")[0].strip()] += 1
        for r in rej:
            s = str(r.get("reason", ""))
            if "403" in s or "429" in s or "봇차단" in s:
                reasons["접근 차단(403/429)"] += 1
            elif "페이월" in s or "paywall" in s.lower():
                reasons["페이월"] += 1
            elif "신선도" in s or "발행" in s:
                reasons["신선도 위반"] += 1
            elif "등급" in s or "3급" in s:
                reasons["등급 미달"] += 1
            elif "불일치" in s or "원문에 없" in s:
                reasons["내용 불일치"] += 1
            else:
                reasons["기타"] += 1
        per_worker.append((w.get("worker", "?"), len(chunks), len(reg), len(rej), pc))

    print(f"아카이브 워커 수: {len(res)}  (⚠️ 1차 팬아웃 분만 포함 — R15 보강 3회는 미포함)")
    print(f"\n청크 우선순위 분포: " +
          " · ".join(f"{k} {v}" for k, v in sorted(prio_chunks.items())))
    print(f"청크 범위 분포    : " +
          " · ".join(f"{k} {v}" for k, v in sorted(scope_chunks.items())))

    total_src = adopted + rejected
    print(f"\n출처 후보 총계 : {total_src}")
    print(f"  채택        : {adopted} ({adopted/total_src*100:.1f}%)")
    print(f"  탈락        : {rejected} ({rejected/total_src*100:.1f}%)")
    print(f"\n탈락 사유별:")
    for k, v in reasons.most_common():
        print(f"  {k:20} {v:3}건  (후보 대비 {v/total_src*100:.1f}%)")
    print(f"\n채택 출처 공신력 등급: " +
          " · ".join(f"{k} {v}" for k, v in sorted(cred.items())))
    print(f"채택 출처 접근 상태  : " +
          " · ".join(f"{k} {v}" for k, v in sorted(access.items())[:5]))

    print(f"\n{'워커':22}{'청크':>5}{'채택':>5}{'탈락':>5}  우선순위 구성")
    for name, nc, na, nr, pc in per_worker:
        comp = ",".join(f"{k}:{v}" for k, v in sorted(pc.items()))
        print(f"{name[:21]:22}{nc:>5}{na:>5}{nr:>5}  {comp}")

    print("\n⚠️ 우선순위별 fetch 상한을 이 표에서 직접 도출할 수 없다.")
    print("   워커 1명이 여러 우선순위의 청크를 섞어 담당했고, fetch 호출은")
    print("   워커 단위로만 기록되어 청크 단위 귀속이 불가능하다.")
    print("   → Phase 3의 우선순위별 상한은 이 데이터만으로 확정하지 말고,")
    print("      Phase 7 파일럿에서 청크 단위로 실측해 정하는 것을 권고한다.")


def section_baseline(m, w, a, url, ret, stats, cost_main, cost_worker,
                     discarded_tokens):
    hr("J. 잠정 기준선 대조 (일치 → 승격 / 불일치 → 임의 채택 금지)")
    if CORRECTIONS:
        print("※ rev.2 대조에서 발견된 기준선 결함 4건이 rev.3으로 정정되어 있다:")
        for name, old, new, why in CORRECTIONS:
            print(f"   · {name}: {old} → {new}")
            print(f"     사유: {why}")
        print()
    B = PROVISIONAL_BASELINE
    ws = [s for s in stats if s.kind == "worker"]
    turns = sorted(s.turns for s in ws) or [0]

    checks = [
        ("메인 에이전트 수", m["agents"], B["main_agents"]),
        ("메인 턴", m["turns"], B["main_turns"]),
        ("메인 총 처리 토큰", m["total"], B["main_total"]),
        ("워커 에이전트 수", w["agents"], B["worker_agents"]),
        ("워커 턴", w["turns"], B["worker_turns"]),
        ("워커 총 처리 토큰", w["total"], B["worker_total"]),
        ("전체 총 처리 토큰", a["total"], B["grand_total"]),
        ("캐시 읽기", a["cr"], B["cache_read"]),
        ("캐시 생성", a["cc"], B["cache_creation"]),
        ("출력", a["out"], B["output"]),
        ("신규 입력", a["inp"], B["input"]),
        ("워커 턴 min", turns[0], B["worker_turn_min"]),
        ("워커 턴 median", int(statistics.median(turns)), B["worker_turn_median"]),
        ("워커 턴 max", turns[-1], B["worker_turn_max"]),
        ("①호출수(워커만)", url["worker"]["calls"], B["webfetch_worker"]),
        ("①호출수(전 에이전트)", url["all"]["calls"], B["webfetch_all"]),
        ("WebSearch(전 에이전트)", url["all"]["search"], B["websearch_all"]),
        ("②고유URL(전 에이전트)", url["all"]["unique_urls"], B["url_unique_all"]),
        ("③중복URL종류(워커만)", url["worker"]["dup_url_kinds"],
         B["dup_url_kinds_worker"]),
        ("③중복URL종류(전 에이전트)", url["all"]["dup_url_kinds"],
         B["dup_url_kinds_all"]),
        ("④초과호출(워커만)", url["worker"]["excess_calls"], B["url_dup_worker"]),
        ("④초과호출(전 에이전트)", url["all"]["excess_calls"], B["url_dup_all"]),
        ("반환 건수", ret.get("returns", 0), B["returns"]),
        ("반환 문자 수", ret.get("chars", 0), B["returns_chars"]),
        ("폐기된 실행 토큰", discarded_tokens, B["discarded_tokens"]),
    ]

    print(f"{'항목':26}{'계측':>16}{'잠정 기준선':>16}{'판정':>8}")
    print("-" * 66)
    fails = []
    for name, got, exp in checks:
        ok = (got == exp)
        if not ok:
            fails.append((name, got, exp))
        print(f"{name:26}{got:>16,}{exp:>16,}{'일치' if ok else '불일치':>8}")

    # 실수 비교는 허용오차 적용 (반올림 차이를 불일치로 보지 않는다)
    floats = [
        ("첫 턴 cache creation 평균", statistics.mean([s.first_cc or 0 for s in ws]),
         B["worker_first_cc_mean"], 0.5),
        ("첫 턴 cache read 평균", statistics.mean([s.first_cr or 0 for s in ws]),
         B["worker_first_cr_mean"], 0.5),
        ("첫 턴 관측 입력량 평균", statistics.mean([s.first_prompt or 0 for s in ws]),
         B["worker_first_prompt_mean"], 0.5),
        ("환산 비용 메인($)", cost_main, B["cost_main"], 0.01),
        ("환산 비용 워커($)", cost_worker, B["cost_worker"], 0.01),
        ("환산 비용 합계($)", cost_main + cost_worker, B["cost_total"], 0.01),
    ]
    for name, got, exp, tol in floats:
        ok = abs(got - exp) <= tol
        if not ok:
            fails.append((name, round(got, 2), exp))
        print(f"{name:26}{got:>16.2f}{exp:>16.2f}{'일치' if ok else '불일치':>8}")

    print()
    if not fails:
        print("판정: ✅ 전 항목 수치 일치")
        print()
        print("  그러나 **기준선 상태는 「부분 검증 완료」이며 최종 승격은 보류**한다:")
        print("    · 독립 재현 완료      : 23건 (계측기가 기준선을 건드리지 않고 재현)")
        print("    · 잠정 정정 후 일치   : 그 외 (계측기에 맞춰 기준선을 고침 = 순환)")
        print("    · 이 계측기는 기준선 작성자와 **같은 에이전트**가 만들었다")
        print("  → 최종 승격 조건: A절 정의를 사람이 감사 + 정정분의 별도 방법 재확인")
        return True

    print(f"판정: ❌ **독립 재현 실패** — 불일치 {len(fails)}건")
    for name, got, exp in fails:
        print(f"    · {name}: 계측 {got:,} vs 기준선 {exp:,}")
    print("\n필수 조치 (계획 「기준선 대조 처리 규칙」):")
    print("  1. 어느 쪽도 임의 채택하지 않는다")
    print("  2. 대조 5항목 점검 — ①파서 ②턴 정의 ③캐시 집계 ④로그 누락 ⑤가격표")
    print("  3. 원인 미해결 시 **Phase 2 이후 전면 중단**")
    print("  4. 기존 수치가 틀렸다면 계획 파일의 기준선을 먼저 정정하고 재승인 요청")
    return False


# ─────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────────────
# Phase 2 — 워커 실행 통제 감사 (읽기 전용)
#
# 안 「가」(Explore + sonnet)에서는 `Write`·`Edit`·`NotebookEdit`·`Agent`만
# 구조적으로 차단된다. 나머지 불허 도구(`Bash` 등)는 **프롬프트 수준 지시**일 뿐이므로
# 사후 트랜스크립트 감사로만 강제할 수 있다. 이 감사가 그 강제 수단이다.
#
# ⚠️ 워커 자기보고는 정본이 아니다(1.5-B 실측: 자기보고 11 vs 트랜스크립트 12).
# ─────────────────────────────────────────────────────────────────────────────

WORKER_TOOL_ALLOWLIST = ("WebSearch", "WebFetch", "Read", "Grep", "Glob")
EXPECTED_WORKER_MODEL = "claude-sonnet-5"
AUDIT_EXIT_VIOLATION = 3


def discover_worker_logs(pdir, session):
    """워커 트랜스크립트를 두 배치 방식 모두에서 찾는다.

    · 직접 `Agent` 도구 호출 → `<session>/subagents/agent-*.jsonl`
    · Workflow 팬아웃        → `<session>/subagents/workflows/wf_*/agent-*.jsonl`
    """
    sub = os.path.join(pdir, session, "subagents")
    direct = sorted(glob.glob(os.path.join(sub, "agent-*.jsonl")))
    wf = sorted(glob.glob(os.path.join(sub, "workflows", "*", "agent-*.jsonl")))
    return direct, wf


def section_tool_audit(pdir, session, allow, expect_model):
    """워커별 모델·턴·도구 사용을 감사한다. 위반이 있으면 True를 돌려준다."""
    hr("G. 워커 도구·모델 감사 (Phase 2 실행 통제)")
    print(f"허용 도구 : {', '.join(allow)}")
    print(f"기대 모델 : {expect_model}")
    print("계측 정본 : 트랜스크립트 (워커 자기보고는 참고용)")
    print("턴 정의   : 1턴 = usage 보유 assistant 레코드 1건 (TURN_RULE과 동일)")

    direct, wf = discover_worker_logs(pdir, session)
    print(f"\n대상 로그 : 직접 Agent {len(direct)}개 · 워크플로 {len(wf)}개")
    files = [(f, "direct") for f in direct] + [(f, "workflow") for f in wf]
    if not files:
        print("\n대상 워커 로그 없음 — 감사할 것이 없다.")
        return False

    allow_set = set(allow)
    print("\n%-20s %-9s %-18s %5s  %s"
          % ("에이전트", "경로", "모델", "턴", "도구 호출"))
    print("-" * 100)

    tool_violations = []
    model_violations = []
    for path, origin in files:
        label = os.path.basename(path)[6:-6]
        st = collect(path, label, "worker", origin)
        models = ",".join(sorted(st.models)) or "?"
        bad = {t: n for t, n in st.tools.items() if t not in allow_set}
        good = {t: n for t, n in st.tools.items() if t in allow_set}
        shown = ", ".join(f"{t}×{n}" for t, n in sorted(good.items())) or "-"
        if bad:
            shown += "  ⛔ " + ", ".join(f"{t}×{n}" for t, n in sorted(bad.items()))
            tool_violations.append((label, bad))
        if any(m != expect_model for m in st.models):
            model_violations.append((label, models))
        print("%-20s %-9s %-18s %5d  %s"
              % (label, origin, models, st.turns, shown))

    print()
    if model_violations:
        for label, models in model_violations:
            opus = "opus" in models.lower()
            print(f"  ⛔ 모델 불일치: {label} → {models}"
                  + ("   **Opus fallback — 계획상 RED**" if opus else ""))
    else:
        print(f"  ✅ 모델: 전 워커가 {expect_model}")

    if tool_violations:
        for label, bad in tool_violations:
            print(f"  ⛔ 허용목록 외 도구: {label} → "
                  + ", ".join(f"{t}×{n}" for t, n in sorted(bad.items())))
        print("\n판정: ❌ 위반 있음 — 워커가 허용되지 않은 도구를 호출했다.")
        print("      안 「가」는 이 도구들을 구조적으로 막지 못한다."
              " 프롬프트 지시와 이 감사가 유일한 강제 수단이다.")
    else:
        print("  ✅ 도구: 허용목록 외 호출 0건")

    return bool(tool_violations or model_violations)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(
        description="에이전트 실행량·토큰·비용 계측기 (읽기 전용)")
    ap.add_argument("--projects-dir", default=DEFAULT_PROJECTS_DIR)
    ap.add_argument("--session", default=DEFAULT_SESSION)
    ap.add_argument("--workflows", default=",".join(DEFAULT_WORKFLOWS),
                    help="쉼표 구분. 'all'이면 세션 내 전 워크플로")
    ap.add_argument("--archive", default=DEFAULT_ARCHIVE)
    ap.add_argument("--no-baseline", action="store_true",
                    help="잠정 기준선 대조 생략")
    ap.add_argument("--stoplines", action="store_true",
                    help="§7.4 비상 중단선 산정 절을 출력한다")
    ap.add_argument("--scope", choices=["all", "main", "worker"], default="all",
                    help="집계 범위를 명시적으로 선택 (기본 all). "
                         "main/worker 선택 시 기준선 대조는 자동 생략된다")
    ap.add_argument("--tool-audit", action="store_true",
                    help="워커 도구·모델 감사만 수행한다(Phase 2 실행 통제). "
                         f"위반 시 종료코드 {AUDIT_EXIT_VIOLATION}")
    ap.add_argument("--allow", default=",".join(WORKER_TOOL_ALLOWLIST),
                    help="--tool-audit 허용 도구 목록(쉼표 구분)")
    ap.add_argument("--expect-model", default=EXPECTED_WORKER_MODEL,
                    help="--tool-audit 기대 워커 모델 ID")
    args = ap.parse_args()

    pdir = os.path.expanduser(args.projects_dir)

    if args.tool_audit:
        allow = tuple(x.strip() for x in args.allow.split(",") if x.strip())
        section_definitions()
        bad = section_tool_audit(pdir, args.session, allow, args.expect_model)
        return AUDIT_EXIT_VIOLATION if bad else 0
    main_path = os.path.join(pdir, f"{args.session}.jsonl")
    if not os.path.exists(main_path):
        main_path = None

    wf_root = os.path.join(pdir, args.session, "subagents", "workflows")
    if args.workflows == "all":
        workflows = sorted(os.listdir(wf_root)) if os.path.isdir(wf_root) else []
    else:
        workflows = [x.strip() for x in args.workflows.split(",") if x.strip()]

    worker_files = {}
    for wf in workflows:
        worker_files[wf] = sorted(glob.glob(os.path.join(wf_root, wf, "agent-*.jsonl")))

    section_definitions()
    section_inventory(pdir, args.session, workflows, main_path, worker_files)

    stats = []
    if main_path:
        stats.append(collect(main_path, "main", "main", "(session)"))
    for wf in workflows:
        for f in worker_files[wf]:
            stats.append(collect(f, os.path.basename(f)[6:15], "worker", wf))

    if args.scope != "all":
        before = len(stats)
        stats = [x for x in stats if x.kind == args.scope]
        print(f"\n[--scope {args.scope}] 집계 범위를 명시적으로 제한한다: "
              f"{before} → {len(stats)}개 에이전트.")
        print("  기준선 대조는 전 범위 기준이므로 자동 생략된다.")
        args.no_baseline = True

    if not stats:
        print("\n집계 대상 없음 — 종료")
        return 1

    section_agents(stats)
    m, w, a = section_totals(stats)

    hr("E-2. 비용 환산 (모델별)")
    print(f"기준일 {PRICE_ASOF} · {COST_FORMULA}")
    print(f"※ {COST_CAVEAT}")
    cost_main = 0.0
    if main_path:
        cost_main, _ = section_cost_from_files([main_path], "메인 에이전트")
    all_worker_files = [f for wf in workflows for f in worker_files[wf]]
    cost_worker, _ = section_cost_from_files(all_worker_files, "워커")
    print(f"\n총 API 정가 환산: ${cost_main + cost_worker:.2f} "
          f"(메인 ${cost_main:.2f} + 워커 ${cost_worker:.2f})")

    # 폐기분 낭비
    discarded = [s for s in stats if s.wf in DISCARDED_WORKFLOWS]
    discarded_tokens = sum(s.total for s in discarded)
    if discarded:
        print(f"\n[폐기된 실행] {len(discarded)}개 에이전트 · {discarded_tokens:,} 토큰 "
              f"({discarded_tokens/a['total']*100:.1f}%) — 산출물 미채택")
        for s in discarded:
            print(f"    {s.wf:18} {s.label}  {s.total:,}"
                  f"  (신규{s.inp:,}+생성{s.cc:,}+읽기{s.cr:,}+출력{s.out:,})")

    url = section_urls(stats)
    ret = section_returns(stats)
    section_correlation(stats)
    if args.stoplines:
        section_stoplines(stats)
    section_calibration(args.archive)

    if not args.no_baseline:
        ok = section_baseline(m, w, a, url, ret, stats, cost_main, cost_worker,
                              discarded_tokens)
        return 0 if ok else 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
