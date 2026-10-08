# STATE.md의 기계 검사(읽기 전용). Phase 2의 S2-1·2·3·4·8과 대조 장부의 완전성, I1·I2·I3을 한 번에 본다.
# 사용: python plans/agent-system-audit/check_state.py   (저장소 루트에서, 위반이 있으면 종료코드 1)
import csv, hashlib, io, math, os, re, subprocess, sys

ROOT = os.getcwd()
AUD = os.path.join(ROOT, "plans", "agent-system-audit")
HEAD = "a979b423489f42d8449615453511175b77690a80"
MEM_SHA = "6dc4aa1c5ad33592be2d2f64c4dae10d88859bc41dfb2bc152fc97243687e159"
COLS = ["ID", "범위", "한 줄 상태", "다음 행동", "담당", "상세 위치", "확인일"]
bad = []


def rd(*p, **k):
    return io.open(os.path.join(*p), encoding="utf-8", **k).read()


def tsv(name):
    return list(csv.DictReader(io.open(os.path.join(AUD, name), encoding="utf-8"), delimiter="\t"))


def report(key, ok, msg):
    print("%s %s — %s" % (key, "PASS" if ok else "FAIL", msg))
    if not ok:
        bad.append(key)


raw = io.open(os.path.join(ROOT, "STATE.md"), "rb").read()
text = raw.decode("utf-8").replace("\r\n", "\n")
lines = text.split("\n")

# S2-1 색인 표
hdr = next(i for i, l in enumerate(lines) if l.startswith("| ID |"))
cols = [c.strip() for c in lines[hdr].strip("|").split("|")]
rows = []
for l in lines[hdr + 2:]:
    if not l.startswith("|"):
        break
    rows.append([c.strip() for c in l.strip().strip("|").split("|")])
empty = sum(1 for r in rows for c in r if not c)
dates = [r[-1] for r in rows]
date_ok = all(re.fullmatch(r"\d{4}-\d{2}-\d{2}|확인 필요", d) for d in dates)
report("S2-1", cols == COLS and all(len(r) == 7 for r in rows) and empty == 0 and date_ok,
       "열 %d개 · 행 %d · 빈 칸 %d · 확인일 형식 %s" % (len(cols), len(rows), empty, "정상" if date_ok else "위반"))

# S2-2 행 수와 items.tsv
ids = [r[0] for r in rows]
items = [r["id"] if "id" in r else list(r.values())[0] for r in tsv("memory-migration-items.tsv")]
miss = [i for i in items if i not in ids]
report("S2-2", len(rows) <= 40 and not miss, "색인 %d행(상한 40) · items.tsv %d건 중 색인에 없는 것 %d" % (len(rows), len(items), len(miss)))

# S2-3 상세와 근거 줄 범위
sect = {}
cur = None
for l in lines:
    m = re.match(r"### (S\d+) ", l)
    if m:
        cur = m.group(1)
        sect[cur] = []
    elif cur:
        sect[cur].append(l)
mp = tsv("memory-migration-map.tsv")
snap = rd(ROOT, "_dev", "설계기록", "MEMORY-스냅샷-2026-10-08.md", newline="").split("\r\n")
out_of_range = []
no_src = []
for i in ids:
    body = "\n".join(sect.get(i, []))
    m = re.search(r"근거 원문: 스냅샷 ([^.\n]*?)행", body)
    if not m:
        no_src.append(i)
        continue
    cover = set()
    for a, b in re.findall(r"(\d+)(?:~(\d+))?", m.group(1)):
        cover.update(range(int(a), int(b or a) + 1))
    for r in mp:
        if r["item"].strip() == i:
            for n in range(int(r["start"]), int(r["end"]) + 1):
                if snap[n - 1].strip() and n not in cover:
                    out_of_range.append((i, n))
report("S2-3", not no_src and not out_of_range and all(i in sect for i in ids),
       "상세 %d개 · 근거 줄 표기 없는 것 %d · 범위 밖 대조표 줄 %d %s" % (len(sect), len(no_src), len(out_of_range), out_of_range[:5]))

# S2-4 경로 실재
names = set()
for r, ds, fs in os.walk(ROOT):
    ds[:] = [d for d in ds if d not in (".git", "node_modules", "tmp", "__pycache__")]
    for n in fs + ds:
        names.add(n)
toks = sorted(set(re.findall(r"`([^`\n]+)`", text)))
checked = 0
unresolved = []
for t in toks:
    if re.search(r"[\s<>*|=]|^--|^[A-Za-z0-9_]+$|~", t) and not os.path.exists(os.path.join(ROOT, t)):
        continue  # 명령·식별자·값
    if "/" not in t and "." not in t:
        continue
    if t.startswith(".") and "/" not in t or "://" in t:
        continue  # CSS 셀렉터 · URL 스킴
    checked += 1
    if os.path.exists(os.path.join(ROOT, t.rstrip("/"))):
        continue
    if t.rstrip("/").split("/")[-1] in names:
        continue  # 과목 폴더 기준 상대 경로
    unresolved.append(t)
allowed = {"6h.txt", "_dev/설계기록/MEMORY-이력-2026-10.md"}  # 없다고 적은 파일 · 이관 뒤에 생길 파일
unresolved = [u for u in unresolved if u not in allowed]
report("S2-4", not unresolved, "경로 모양 토큰 %d개 · 실재하지 않는 것 %d %s" % (checked, len(unresolved), unresolved))

# S2-8 크기 상한
size = len(raw)
cap = math.ceil(size * 1.25 / 1024)
m = re.search(r"파일 (\d+)KB\(.*?크기 (\d+)바이트", text)
report("S2-8", bool(m) and int(m.group(1)) == cap and int(m.group(2)) == size,
       "실제 %d바이트 · 계산 상한 %dKB · 문서 표기 %s" % (size, cap, m.groups() if m else None))

# 대조 장부(S2-6의 입력): item이 붙은 비공백 줄이 전부 장부에 있는가
cov = {int(r["line"]): r for r in tsv("state-coverage.tsv")}
want = set()
for r in mp:
    if r["item"].strip() not in ("", "-"):
        want.update(n for n in range(int(r["start"]), int(r["end"]) + 1) if snap[n - 1].strip())
blank = [n for n, r in cov.items() if not r["disposition"].strip() or not r["where_in_STATE"].strip()]
report("장부", want == set(cov) and not blank,
       "대상 %d줄 · 장부 %d줄 · 빠진 줄 %s · 남는 줄 %s · 빈 처리 %d" % (len(want), len(cov), sorted(want - set(cov)), sorted(set(cov) - want), len(blank)))


def git(*a):
    return subprocess.run(["git"] + list(a), cwd=ROOT, capture_output=True).stdout.decode("utf-8", "replace").strip()


# I1 · I2 · I3
staged = [x for x in git("diff", "--cached", "--name-only").split("\n") if x]
stash = [x for x in git("stash", "list").split("\n") if x]
report("I1", git("rev-parse", "HEAD") == HEAD and not staged and len(stash) == 1,
       "HEAD %s · staged %d · stash %d" % (git("rev-parse", "--short", "HEAD"), len(staged), len(stash)))
fg = subprocess.run([sys.executable, os.path.join(AUD, "baseline", "frame_guard.py")], cwd=ROOT, capture_output=True).stdout.decode("utf-8", "replace")
before = rd(AUD, "baseline", "frame_guard_before.txt")
report("I2", fg.split() == before.split(), "frame_guard 출력이 기준선과 %s" % ("같다" if fg.split() == before.split() else "다르다"))
snap_sha = hashlib.sha256(io.open(os.path.join(ROOT, "_dev", "설계기록", "MEMORY-스냅샷-2026-10-08.md"), "rb").read()).hexdigest()
report("스냅샷", snap_sha == MEM_SHA, "스냅샷 sha256 %s…" % snap_sha[:8])

print("RESULT %s (위반 %d)" % ("FAIL" if bad else "PASS", len(bad)))
sys.exit(1 if bad else 0)
