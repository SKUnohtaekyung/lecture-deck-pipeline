#!/usr/bin/env python3
"""최종본 빌드 오케스트레이터 — "최종본 만들어" 트리거의 한 커맨드 구현.

편집본 조각(강의덱.초안/)에서 배포 단일본(강의덱_배포.html)까지:
  1) assemble_deck.py   조각 → 미리보기 통합본(강의덱.html)
  2) verify_deck.py     구조 검증(파트 수 자동 산출, FAIL이면 중단)
  3) inline_deck.py     CSS·이미지 인라인 + Pretendard 서브셋 폰트 임베드(--offline, fail-closed)
  4) verify_distributable.py  자립성 독립 강제 게이트

한 단계라도 실패하면 즉시 중단한다. 통과 전에는 "완성"이 아니다.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # pragma: no cover
    pass

ROOT = Path(__file__).resolve().parents[1]


def _run(script: str, *rest: object) -> int:
    cmd = [sys.executable, str(ROOT / "scripts" / script), *[str(item) for item in rest]]
    print("  $ " + " ".join(str(part) for part in cmd[1:]))
    return subprocess.run(cmd, cwd=str(ROOT)).returncode


def _find_deck_contract(deck_path: Path) -> Path | None:
    """verify_deck.py의 find_deck_contract()와 동일한 3단 탐색(중복 정의 — 서브프로세스 경계라 임포트 대신 복제):
    ① 덱과 같은 폴더의 deck.contract.json ② sessions/_contracts/<덱 부모폴더명>.deck.contract.json ③ 없으면 None."""
    deck_file = deck_path.resolve()
    sibling = deck_file.parent / "deck.contract.json"
    if sibling.is_file():
        return sibling
    named = ROOT / "sessions" / "_contracts" / f"{deck_file.parent.name}.deck.contract.json"
    if named.is_file():
        return named
    return None


def _contract_dividers(preview_path: Path) -> int | None:
    """계약에 dividers 값이 있으면 그 값을 반환하고, 없거나 읽기 실패하면 None(폴백 신호)."""
    contract_path = _find_deck_contract(preview_path)
    if contract_path is None:
        return None
    try:
        contract_data = json.loads(contract_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    deck_contract = (contract_data.get("decks") or {}).get(preview_path.stem)
    if not isinstance(deck_contract, dict) or "dividers" not in deck_contract:
        return None
    return deck_contract["dividers"]


def build_release(
    draft_dir: str | Path,
    *,
    preview: str | Path | None = None,
    output: str | Path | None = None,
    skip_verify_deck: bool = False,
) -> int:
    draft = Path(draft_dir)
    draft = draft if draft.is_absolute() else ROOT / draft
    if not (draft / "shell.html").is_file():
        print(f"[FAIL] 조각 폴더에 shell.html이 없습니다: {draft}")
        return 1
    preview_path = Path(preview) if preview else draft.parent / "강의덱.html"
    output_path = Path(output) if output else draft.parent / "강의덱_배포.html"

    print("1) 조립 (조각 → 미리보기 통합본)")
    if _run("assemble_deck.py", draft, "--output", preview_path):
        print("[FAIL] 조립 실패")
        return 1

    if not skip_verify_deck:
        print("2) 구조 검증 (verify_deck)")
        parts = _contract_dividers(preview_path)
        if parts is None:
            print("WARN: 계약 없음 — parts 자기계산")
            parts = len(re.findall(r"<section[^>]*\bpart-divider\b", preview_path.read_text(encoding="utf-8")))
        if _run("verify_deck.py", preview_path, "--parts", parts):
            print("[FAIL] 구조 검증 실패 — 조각을 고친 뒤 다시 실행하세요")
            return 1

    print("3) 인라인 + 폰트 임베드 (--offline, fail-closed)")
    if _run("inline_deck.py", preview_path, "--offline", "--output", output_path):
        print("[FAIL] 인라인/폰트/강제 빌드 실패")
        return 1

    print("4) 자립성 강제 게이트 (verify_distributable)")
    if _run("verify_distributable.py", output_path):
        print("[FAIL] 자립성 게이트 실패")
        return 1

    size_kb = output_path.stat().st_size // 1024
    print(f"\n[PASS] 최종본 완성: {output_path} ({size_kb}KB)")
    print("       학생에게 이 파일 하나만 주면 오프라인에서 전부 렌더됩니다.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("draft_dir", help="편집본 조각 폴더 (예: sessions/N주차/강의덱.초안)")
    parser.add_argument("--preview", help="조립 미리보기 경로 (기본 <draft>/../강의덱.html)")
    parser.add_argument("--output", help="배포본 경로 (기본 <draft>/../강의덱_배포.html)")
    parser.add_argument("--skip-verify-deck", action="store_true", help="구조 검증 건너뛰기")
    args = parser.parse_args()
    return build_release(
        args.draft_dir,
        preview=args.preview,
        output=args.output,
        skip_verify_deck=args.skip_verify_deck,
    )


if __name__ == "__main__":
    sys.exit(main())
