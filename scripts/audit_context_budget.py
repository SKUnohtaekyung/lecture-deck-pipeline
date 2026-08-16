#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""컨텍스트 예산 감사 — 메인 창이 왜 커졌는지 판정한다 (읽기 전용).

`analyze_agent_usage.py`가 «얼마나 썼는가»를 재는 총량 계측기라면, 이 스크립트는
«왜 커졌는가»를 짚는다. 비용의 지배 항목이 캐시 읽기(창 재청구)이므로, 창을
키운 원인을 출처별로 분해하고 판정 기준 T1~T6으로 위반을 종료코드에 싣는다.

왜 필요한가 (2026-08-06 감사):
  - 비용의 70.8%가 «창 재청구»였다. 창은 102k → 462k로 4.5배 자랐다.
  - 도구를 부르지 않는 «말하는 턴»이 호출의 2/3, 비용의 67.7%였다.
  - 창을 채운 1위는 Bash 도구 결과(내용의 35.5%)였다 — 대부분 종료코드 한 줄이면
    충분했던 출력이다.
  - 그런데 이 사실들은 «규칙 문서에 적어두는 것»만으로는 다음 세션이 상속하지
    못한다. 그래서 측정 가능한 판정기로 만든다.

판정 기준(정본: `_dev/설계기록/토큰감사-2026-08-06.md` §1)
  T1 단발 캐시 재생성 > 50,000        (재생성은 읽기의 12.5배 단가)
  T2 평균 컨텍스트   > 200,000        (하네스 §4의 150k 규정 + 여유)
  T3 무도구 턴 비용 비중 > 50%
  T4 호출 간격 > 3,600초              (프롬프트 캐시 TTL 1시간)
  T6 계측 신뢰 — `analyze_agent_usage.py`가 중복제거를 하는가 (정적 확인)
  TS 단일 출처가 창 내용의 30% 초과   (S1: 한 종류가 창을 지배하면 그것부터 줄인다)

  ⚠️ T6은 «원시 로그의 중복 배수»가 아니다. 로그가 응답 1건을 블록마다 반복
     기록하는 것은 정상이고, 이 감사기도 계측기도 중복제거를 하므로 그 배수는
     항상 2 안팎이다 — 그것을 위반으로 세면 **항상 발화하는 무의미한 기준**이
     된다(초안에서 실제로 그랬다). T6이 묻는 것은 «집계기가 그 함정을 처리하고
     있는가»이고, 답은 코드에 있으므로 정적으로 확인한다.

  ※ T5(메인 대 워커)는 워커 사이드카 로그가 있어야 재므로 여기서 다루지 않는다.
     `analyze_agent_usage.py`의 D절이 담당한다.

사용:
    python scripts/audit_context_budget.py <session-id>
    python scripts/audit_context_budget.py <session-id> --json
    python scripts/audit_context_budget.py --list        # 세션 목록(최근순)
    python scripts/audit_context_budget.py --list --project-dir <경로>  # 다른 프로젝트 지정

종료코드: 0 위반 없음 / 1 위반 있음 / 2 입력 오류
표준 라이브러리만 사용한다(훅·git 훅에서 호출될 수 있다).
"""
import io
import json
import os
import re
import sys

# ── 프로젝트 세션 폴더 유도 (배치1 P6 · 2026-08-17) ─────────────────────────
# 종전에는 PROJECT_KEY가 타인 환경("C--Users-miso-Desktop-template")으로
# 하드코딩돼 이 저장소에서 상시 미작동했다(ANALYSIS §4 — 기제3의 한 사례).
# Claude Code는 세션 로그를 ~/.claude/projects/<키>/ 아래 두고, 키는 프로젝트
# 절대경로의 영숫자 외 문자를 전부 '-'로 치환한 것이다. 실측 근거: 이 저장소
# C:\Users\Noh TaeKyung\Desktop\lecture-deck-pipeline
# → C--Users-Noh-TaeKyung-Desktop-lecture-deck-pipeline (실재 폴더 확인).

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(HERE)


def derive_project_key(path):
    """프로젝트 절대경로 → Claude Code 세션 폴더명."""
    return re.sub(r"[^A-Za-z0-9]", "-", path)


def sessions_dir(project_dir=None):
    """세션 로그 폴더. 기본은 이 저장소 루트에서 유도한다."""
    target = os.path.abspath(project_dir or REPO_ROOT)
    return os.path.join(os.path.expanduser("~"), ".claude", "projects",
                        derive_project_key(target))

T1_CACHE_CREATE = 50_000
T2_AVG_CONTEXT = 200_000
T3_NOTOOL_COST = 50.0
T4_GAP_SECONDS = 3_600
TS_SOURCE_SHARE = 30.0

# 비용 가중치(입력단가=1 기준). 출력은 Opus 계열 기준 입력의 5배.
W_INPUT, W_CACHE_CREATE, W_CACHE_READ, W_OUTPUT = 1.0, 1.25, 0.1, 5.0


def out(s=""):
    try:
        sys.stdout.buffer.write((s + "\n").encode("utf-8"))
    except Exception:
        print(s)


def parse_ts(s):
    """timestamp를 epoch 초로. 실패하면 None(조용히 넘기지 않고 호출부가 판단)."""
    if not s:
        return None
    try:
        import datetime
        return datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
    except Exception:
        return None


def load(path):
    """usage를 가진 assistant 레코드를 message.id로 중복제거해 돌려준다.

    중복제거를 하지 않으면 같은 API 호출이 콘텐츠 블록 수만큼 계수된다
    (실측 2.05배). 그 배수 자체가 T6 판정값이다.
    """
    seen, calls, dup, bad = set(), [], 0, 0
    with io.open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                bad += 1
                continue
            msg = rec.get("message")
            if not isinstance(msg, dict):
                continue
            usage = msg.get("usage")
            if not isinstance(usage, dict):
                continue
            mid = msg.get("id")
            if mid is not None:
                if mid in seen:
                    dup += 1
                    continue
                seen.add(mid)
            tools = [b.get("name", "?") for b in (msg.get("content") or [])
                     if isinstance(b, dict) and b.get("type") == "tool_use"]
            calls.append({
                "inp": usage.get("input_tokens", 0) or 0,
                "cc": usage.get("cache_creation_input_tokens", 0) or 0,
                "cr": usage.get("cache_read_input_tokens", 0) or 0,
                "out": usage.get("output_tokens", 0) or 0,
                "tools": tools,
                "ts": parse_ts(rec.get("timestamp")),
            })
    return calls, dup, bad


def content_sources(path):
    """창을 채운 내용을 출처별 문자 수로 분해한다.

    토큰이 아니라 문자로 센다 — 토크나이저를 흉내내지 않기 위해서다. 한국어는
    문자당 약 1.09 토큰으로 영어(약 0.25)의 4배가 넘으므로, 비중 비교에는
    문자 수로 충분하고 절대 토큰 추정은 하지 않는다.
    """
    src = {}
    names = {}
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
            content = msg.get("content")
            role = msg.get("role")
            if role == "assistant" and isinstance(content, list):
                for b in content:
                    if not isinstance(b, dict):
                        continue
                    t = b.get("type")
                    if t == "text":
                        src["응답 텍스트"] = src.get("응답 텍스트", 0) + len(b.get("text", ""))
                    elif t == "thinking":
                        src["사고"] = src.get("사고", 0) + len(b.get("thinking", ""))
                    elif t == "tool_use":
                        names[b.get("id")] = b.get("name", "?")
            elif role == "user" and isinstance(content, list):
                for b in content:
                    if not isinstance(b, dict):
                        continue
                    if b.get("type") == "tool_result":
                        nm = names.get(b.get("tool_use_id"), "?")
                        c = b.get("content")
                        n = len(c) if isinstance(c, str) else sum(
                            len(x.get("text", "")) for x in (c or []) if isinstance(x, dict))
                        key = "도구결과: " + nm
                        src[key] = src.get(key, 0) + n
                    elif b.get("type") == "text":
                        src["사용자·시스템"] = src.get("사용자·시스템", 0) + len(b.get("text", ""))
            elif role == "user" and isinstance(content, str):
                src["사용자·시스템"] = src.get("사용자·시스템", 0) + len(content)
    return src


def main():
    argv = sys.argv[1:]
    project_dir = None
    if "--project-dir" in argv:
        i = argv.index("--project-dir")
        if i + 1 >= len(argv):
            out("--project-dir 뒤에 경로가 필요하다")
            return 2
        project_dir = argv[i + 1]
        del argv[i:i + 2]
    base_dir = sessions_dir(project_dir)
    if not os.path.isdir(base_dir):
        out("세션 폴더가 없다: %s" % base_dir)
        out("(프로젝트 경로가 다르면 --project-dir <경로>로 지정)")
        return 2
    if "--list" in argv:
        files = [f for f in os.listdir(base_dir) if f.endswith(".jsonl")]
        files.sort(key=lambda f: os.path.getmtime(os.path.join(base_dir, f)), reverse=True)
        for f in files[:20]:
            size = os.path.getsize(os.path.join(base_dir, f)) / 1e6
            out("%7.1fMB  %s" % (size, f[:-6]))
        return 0
    sids = [a for a in argv if not a.startswith("--")]
    if not sids:
        out("사용법: python scripts/audit_context_budget.py <session-id> [--json]")
        out("        python scripts/audit_context_budget.py --list [--project-dir <경로>]")
        return 2
    path = os.path.join(base_dir, sids[0] + ".jsonl")
    if not os.path.isfile(path):
        out("세션 로그를 찾을 수 없다: %s" % path)
        return 2

    calls, dup, bad = load(path)
    if not calls:
        out("집계할 호출이 없다")
        return 2
    n = len(calls)
    cost = lambda c: (c["inp"] * W_INPUT + c["cc"] * W_CACHE_CREATE
                      + c["cr"] * W_CACHE_READ + c["out"] * W_OUTPUT)
    total_cost = sum(cost(c) for c in calls) or 1.0
    avg_ctx = sum(c["cr"] for c in calls) / n
    no_tool = [c for c in calls if not c["tools"]]
    no_tool_cost = sum(cost(c) for c in no_tool) / total_cost * 100
    dup_ratio = (n + dup) / n

    t1 = [(i + 1, c["cc"]) for i, c in enumerate(calls) if c["cc"] > T1_CACHE_CREATE]
    gaps = []
    for i in range(1, n):
        a, b = calls[i - 1]["ts"], calls[i]["ts"]
        if a and b and (b - a) > T4_GAP_SECONDS:
            gaps.append((i + 1, b - a, calls[i]["cc"]))

    # TS — 창을 채운 출처 분해. 단일 출처가 30%를 넘으면 그것부터 줄인다.
    src = content_sources(path)
    tot_chars = sum(src.values()) or 1
    top_src = sorted(src.items(), key=lambda kv: -kv[1])
    ts_hits = [(k, v / tot_chars * 100) for k, v in top_src
               if v / tot_chars * 100 > TS_SOURCE_SHARE]

    # T6 — 계측기가 중복제거를 하는지 정적 확인(원시 로그의 중복 배수가 아니다).
    analyzer = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "analyze_agent_usage.py")
    try:
        src_text = io.open(analyzer, encoding="utf-8", errors="replace").read()
        t6_ok = ("seen_msg_ids" in src_text) and ('msg.get("id")' in src_text)
    except Exception:
        t6_ok = False

    viol = []
    if t1:
        viol.append("T1")
    if avg_ctx > T2_AVG_CONTEXT:
        viol.append("T2")
    if no_tool_cost > T3_NOTOOL_COST:
        viol.append("T3")
    if gaps:
        viol.append("T4")
    if not t6_ok:
        viol.append("T6")
    if ts_hits:
        viol.append("TS")

    if "--json" in argv:
        out(json.dumps({
            "calls": n, "duplicate_records": dup, "dup_ratio": round(dup_ratio, 3),
            "avg_context": int(avg_ctx), "no_tool_cost_pct": round(no_tool_cost, 1),
            "t1_spikes": len(t1), "t4_gaps": len(gaps), "violations": viol,
        }, ensure_ascii=False))
        return 1 if viol else 0

    out("=" * 66)
    out("컨텍스트 예산 감사 — %s" % sids[0])
    out("=" * 66)
    out("실제 모델 호출 %d회 (중복 레코드 %d건 제외 · 배수 %.2f)" % (n, dup, dup_ratio))
    if bad:
        out("⚠️ 파싱 실패 줄 %d건" % bad)
    out("")
    out("[비용 분해] 입력단가=1 · 출력 5배 · 캐시생성 1.25배 · 캐시읽기 0.1배")
    for lbl, v in (("캐시 읽기(창 재청구)", sum(c["cr"] * W_CACHE_READ for c in calls)),
                   ("출력", sum(c["out"] * W_OUTPUT for c in calls)),
                   ("캐시 생성", sum(c["cc"] * W_CACHE_CREATE for c in calls)),
                   ("신규 입력", sum(c["inp"] * W_INPUT for c in calls))):
        out("  %-22s %6.1f%%" % (lbl, v / total_cost * 100))
    out("")
    out("[창을 채운 것] 문자 수 기준 상위 8  (한국어는 문자당 약 1.09토큰 — 영어의 4배)")
    for k, v in top_src[:8]:
        pct = v / tot_chars * 100
        out("  %-26s %10d  %5.1f%%%s" % (k, v, pct, "  ← TS 초과" if pct > TS_SOURCE_SHARE else ""))
    out("")
    out("[판정]")
    out("  T1 단발 재생성 >%s      : %s" % (f"{T1_CACHE_CREATE:,}",
        ("위반 %d회 (최대 %s)" % (len(t1), f"{max(x[1] for x in t1):,}")) if t1 else "OK"))
    out("  T2 평균 컨텍스트 >%s   : %s (%s)" % (f"{T2_AVG_CONTEXT:,}",
        "위반" if avg_ctx > T2_AVG_CONTEXT else "OK", f"{int(avg_ctx):,}"))
    out("  T3 무도구 턴 비용 >%.0f%%     : %s (%.1f%% · %d/%d회)" % (
        T3_NOTOOL_COST, "위반" if no_tool_cost > T3_NOTOOL_COST else "OK",
        no_tool_cost, len(no_tool), n))
    out("  T4 호출 간격 >%ds     : %s" % (T4_GAP_SECONDS,
        ("위반 %d회 (최대 %.1f시간)" % (len(gaps), max(g[1] for g in gaps) / 3600)) if gaps else "OK"))
    out("  TS 단일 출처 >%.0f%%         : %s" % (TS_SOURCE_SHARE,
        ("위반 — " + ", ".join("%s %.1f%%" % (k, p) for k, p in ts_hits)) if ts_hits else "OK"))
    out("  T6 계측기 중복제거       : %s (analyze_agent_usage.py 정적 확인)" % (
        "OK" if t6_ok else "위반 — 중복제거 없음. 이 배수만큼 과대 보고된다"))
    out("     (참고: 원시 로그의 중복 배수 %.2f는 정상이다 — 위반이 아니다)" % dup_ratio)
    out("")
    if viol:
        out("RESULT | FAIL | 위반 %s" % ", ".join(viol))
        out("        조치는 `_dev/설계기록/토큰감사-2026-08-06.md` §4 (S1~S6)")
    else:
        out("RESULT | PASS | 위반 없음")
    return 1 if viol else 0


if __name__ == "__main__":
    sys.exit(main())
