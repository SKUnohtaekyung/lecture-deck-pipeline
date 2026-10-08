"""FRAME 미커밋 작업이 그대로인지 확인한다(불변 조건 I2). 읽기 전용.
출력: 추적 파일 diff의 sha256, 미추적 파일 내용의 sha256, 파일 수."""
import subprocess, hashlib, os, sys
PATHS = ["courses/AI_에이전트_실습워크숍_4시간", "plans/FRAME-길이별-조립", "plans/FRAME-개편",
         "plans/FRAME-피드백-1007", "kit/runtime", "scripts/inject_presenter.py", "sites"]
def run(args):
    return subprocess.run(["git", "-c", "core.quotepath=off"] + args, capture_output=True).stdout
diff = run(["diff", "--"] + PATHS)
names = run(["diff", "--name-only", "--"] + PATHS).decode("utf-8").split("\n")
unt = sorted(x for x in run(["ls-files", "--others", "--exclude-standard", "--"] + PATHS).decode("utf-8").split("\n") if x)
h = hashlib.sha256()
files = []
for p in unt:
    if os.path.isdir(p):  # 미추적 폴더(중첩 저장소 등)는 안의 파일을 걷는다. .git은 뺀다.
        for d, dn, fn in os.walk(p):
            dn[:] = sorted(x for x in dn if x != ".git")
            files += [os.path.join(d, f).replace("\\", "/") for f in sorted(fn)]
    else:
        files.append(p)
for p in files:
    h.update(p.encode("utf-8"))
    with open(p, "rb") as fh:
        h.update(hashlib.sha256(fh.read()).digest())
print("tracked_diff_sha256", hashlib.sha256(diff).hexdigest())
print("tracked_diff_files", len([n for n in names if n]))
print("untracked_sha256", h.hexdigest())
print("untracked_files", len(files))
print("HEAD", run(["rev-parse", "HEAD"]).decode().strip())
print("staged", len([x for x in run(["diff", "--cached", "--name-only"]).decode().split("\n") if x]))
print("stash", len([x for x in run(["stash", "list"]).decode().split("\n") if x]))
