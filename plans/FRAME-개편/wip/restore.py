"""FRAME 작업 원본 복원 — plans/FRAME-개편/wip/ → tmp/frame/ (tmp/는 git에 없다).

저장소 루트에서:  python plans/FRAME-개편/wip/restore.py          (없는 파일만 복사)
                  python plans/FRAME-개편/wip/restore.py --force  (덮어쓰기)
작업 정본은 tmp/frame/ 쪽이다. 세션을 끝낼 때는 --save 로 tmp → wip 를 다시 맞춘 뒤 커밋한다.
"""
import shutil, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
WIP = Path(__file__).resolve().parent
TMP = ROOT / 'tmp' / 'frame'
force = '--force' in sys.argv
save = '--save' in sys.argv
n = skip = 0
for src in WIP.rglob('*'):
    if src.is_dir() or src.name in ('restore.py', 'README.md') or '__pycache__' in src.parts:
        continue
    rel = src.relative_to(WIP)
    a, b = (TMP / rel, src) if save else (src, TMP / rel)
    if save and not a.exists():
        skip += 1; continue
    if not save and b.exists() and not force:
        skip += 1; continue
    b.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(a, b); n += 1
print(f"RESULT: {'save' if save else 'restore'} · 복사 {n} · 건너뜀 {skip}")
