"""MEMORY.md의 `## 미해결` 본문(스냅샷 150~696행)을 대조표대로 옮긴다.
- LESSON  → MEMORY.md의 `## 이관된 교훈 (2026-10)`
- STATE   → 이력 파일의 「열린 과업의 근거 원문」 절
- ARCHIVE → 이력 파일의 「이력」 절
줄은 고치지 않는다. 사용: python migrate_memory.py <출력 폴더>  (출력 폴더에 MEMORY.md와 이력 파일을 쓴다. 저장소 파일은 건드리지 않는다)
"""
import csv, sys, os, collections
SNAP = "_dev/설계기록/MEMORY-스냅샷-2026-10-08.md"
MAP = "plans/agent-system-audit/memory-migration-map.tsv"
NL = "\r\n"
raw = open(SNAP, encoding="utf-8", newline="").read()
assert raw.endswith(NL) and "\n" not in raw.replace(NL, ""), "스냅샷은 CRLF여야 한다"
L = raw[:-2].split(NL)
assert len(L) == 696 and L[148] == "## 미해결", (len(L), L[148])
dest = {}; unit = {}
for r in csv.DictReader(open(MAP, encoding="utf-8"), delimiter="\t"):
    for n in range(int(r["start"]), int(r["end"]) + 1):
        assert n not in dest; dest[n] = r["dest"]; unit[n] = r["unit"]
assert sorted(dest) == list(range(150, 697))

def blocks(want):
    """want인 연속 줄 묶음을 (시작, 끝) 목록으로."""
    out = []; cur = None
    for n in range(150, 697):
        if dest[n] == want:
            if cur and cur[1] == n - 1: cur[1] = n
            else: cur = [n, n]; out.append(cur)
    return out

def emit(want):
    lines = []
    for a, b in blocks(want):
        body = L[a - 1:b]
        while body and not body[-1].strip(): body.pop()      # 묶음 끝의 빈 줄은 싣지 않는다(빈 줄은 내용이 아니다)
        while body and not body[0].strip(): body.pop(0)
        if not body: continue
        lines.append("<!-- 원 소절: %s · 스냅샷 L%d~%d -->" % (unit[a], a, b))
        lines += body
        lines.append("")
    return lines

OLD7 = "- 작업 시작 전 `## 미해결`을 먼저 읽고, 덱 조립·규칙 변경이면 관련 절 전체를 읽는다."
NEW7 = "- 작업 시작 전 저장소 루트 `STATE.md`의 색인을 먼저 읽고, 덱 조립·규칙 변경이면 이 파일의 관련 절 전체를 읽는다."
assert L[6] == OLD7, L[6]
head = L[:148]; head[6] = NEW7
mem = head + [
    "## 미해결", "",
    "열린 과업의 정본은 저장소 루트 `STATE.md`다. 이 절에는 아무것도 쓰지 않는다.", "",
    "## 이관된 교훈 (2026-10)", "",
    "2026-10-08에 옛 `## 미해결` 절에서 규칙·교훈·함정·프로젝트 지식이 든 줄을 **고치지 않고** 옮겼다. 각 묶음 위의 주석이 원래 소절과 스냅샷 줄 번호를 알려 준다.",
    "여기 섞여 있는 상태 서술(「대기」「미커밋」「N장」 같은 말)은 그 시점의 기록이고 **현재 상태의 정본이 아니다.** 현재 상태는 `STATE.md`다.",
    "함께 있던 역사 기록은 `_dev/설계기록/MEMORY-이력-2026-10.md`, 이관 전 원문 전체는 `_dev/설계기록/MEMORY-스냅샷-2026-10-08.md`에 있다.", "",
] + emit("LESSON")
while mem and not mem[-1].strip(): mem.pop()
arc = [
    "# MEMORY 이력 — 2026-10 이관분", "",
    "`.agents/agent-memory/create-slides/MEMORY.md`의 옛 `## 미해결` 절에서 2026-10-08에 옮긴 줄이다. 줄은 고치지 않았다.",
    "**여기의 상태 서술은 현재 상태의 정본이 아니다. 현재 상태는 저장소 루트 `STATE.md`다.** 규칙·교훈은 `MEMORY.md`의 `## 이관된 교훈 (2026-10)`에 있다.",
    "각 묶음 위의 주석이 원래 소절과 스냅샷(`MEMORY-스냅샷-2026-10-08.md`) 줄 번호를 알려 준다. 대조표는 `plans/agent-system-audit/memory-migration-map.tsv`.", "",
    "## 열린 과업의 근거 원문 (2026-10-08 시점)", "",
    "`STATE.md`의 각 과업이 근거로 삼은 원문이다. 낡은 수치가 섞여 있다. 과업의 현재 상태는 `STATE.md`를 본다.", "",
] + emit("STATE") + ["## 이력", "", "끝난 일의 경과와, 해소되거나 번복된 서술이다.", ""] + emit("ARCHIVE")
while arc and not arc[-1].strip(): arc.pop()

# 자체 검증: 150~696의 공백 아닌 줄이 두 출력에 정확히 원래 횟수만큼, 대조표가 정한 쪽에 있다.
GEN = lambda s: s.startswith("<!-- 원 소절:")
want = {d: collections.Counter(L[n - 1] for n in range(150, 697) if dest[n] == d and L[n - 1].strip()) for d in ("LESSON", "STATE", "ARCHIVE")}
got_mem = collections.Counter(s for s in mem[158:] if s.strip() and not GEN(s))
got_arc = collections.Counter(s for s in arc[10:] if s.strip() and not GEN(s))
extra_arc = {"## 이력", "끝난 일의 경과와, 해소되거나 번복된 서술이다."}
for k in extra_arc: got_arc[k] -= 1
got_arc = +got_arc
assert got_mem == want["LESSON"], (sum(got_mem.values()), sum(want["LESSON"].values()), list((got_mem - want["LESSON"]).items())[:3], list((want["LESSON"] - got_mem).items())[:3])
assert got_arc == want["STATE"] + want["ARCHIVE"], (list((got_arc - want["STATE"] - want["ARCHIVE"]).items())[:3], list((want["STATE"] + want["ARCHIVE"] - got_arc).items())[:3])
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
open(os.path.join(out, "MEMORY.md"), "w", encoding="utf-8", newline="").write(NL.join(mem) + NL)
open(os.path.join(out, "MEMORY-이력-2026-10.md"), "w", encoding="utf-8", newline="").write(NL.join(arc) + NL)
print("MEMORY.md 줄", len(mem), "· 이력 줄", len(arc), "· 옮긴 비공백 줄: LESSON", sum(want["LESSON"].values()), "STATE", sum(want["STATE"].values()), "ARCHIVE", sum(want["ARCHIVE"].values()), "· 자체 검증 통과")
