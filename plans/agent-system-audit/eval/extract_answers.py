"""EV-1 답을 서브에이전트 로그에서 꺼내 저장한다. 사용: python extract_answers.py <접두 pre_v2|post_v2> [--after ISO시각]
프롬프트에 '열지도 인용하지도'가 든 서브에이전트만 고르고, 시작 시각순으로 번호를 붙인다."""
import json, glob, os, sys
P = r"C:\Users\miso\.claude\projects\C--Users-miso-Desktop-Project-template"
prefix = sys.argv[1]
after = sys.argv[sys.argv.index("--after") + 1] if "--after" in sys.argv else ""
before = sys.argv[sys.argv.index("--before") + 1] if "--before" in sys.argv else "9"
rows = []
for f in glob.glob(os.path.join(P, "*", "subagents", "*.jsonl")):
    first = None; last = ""; ts = ""; usage = [0, 0, 0]; seen = set(); tools = 0; reads = []
    for line in open(f, encoding="utf-8", errors="replace"):
        try: d = json.loads(line)
        except Exception: continue
        m = d.get("message") or {}; c = m.get("content")
        if d.get("type") == "user" and first is None:
            first = c if isinstance(c, str) else "".join(x.get("text", "") for x in c if isinstance(x, dict))
            ts = d.get("timestamp", "")
        if d.get("type") == "assistant":
            if m.get("usage") and m.get("id") not in seen:
                seen.add(m.get("id")); u = m["usage"]
                tot = u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0) + u.get("cache_read_input_tokens", 0)
                if usage[0] == 0: usage[0] = tot
                usage[1] += tot; usage[2] += 1
            if isinstance(c, list):
                t = "".join(x.get("text", "") for x in c if x.get("type") == "text")
                if t.strip(): last = t
                for x in c:
                    if x.get("type") == "tool_use":
                        # 서브에이전트는 마지막 답을 text가 아니라 SubagentHandback 도구 입력으로 낼 수 있다.
                        if x["name"] == "SubagentHandback":
                            inp = x.get("input", {}) or {}
                            hb = max((v for v in inp.values() if isinstance(v, str)), key=len, default="")
                            if hb.strip(): last = hb
                            continue
                        tools += 1
                        if x["name"] == "Read": reads.append(os.path.basename(str(x.get("input", {}).get("file_path", ""))))
    if first and "열지도 인용하지도" in first and "지금 열려 있는 일을 정리" in first and after <= ts < before:
        rows.append((ts, last, usage, tools, reads))
rows.sort()
here = os.path.dirname(os.path.abspath(__file__))
for i, (ts, last, usage, tools, reads) in enumerate(rows, 1):
    with open(os.path.join(here, "%s_%d.md" % (prefix, i)), "w", encoding="utf-8") as fh:
        fh.write("<!-- 시작 %s · 첫 호출 입력 %d · 입력 합 %d · API 호출 %d · 도구 호출 %d · Read: %s -->\n\n%s\n" % (ts, usage[0], usage[1], usage[2], tools, ", ".join(reads), last))
    assert last.strip(), "빈 답: " + ts
    print(prefix, i, ts, "chars", len(last), "first", usage[0], "sum", usage[1], "calls", usage[2], "tools", tools, "STATE.md read" if "STATE.md" in reads else "", "MEMORY read x%d" % reads.count("MEMORY.md"))
