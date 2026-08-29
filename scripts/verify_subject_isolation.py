#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""주제 독립성 검사 — 스킬 본문에 과목 고유 값이 남아 있으면 FAIL.

왜 필요한가
-----------
2026-07-28 실측: 당시 `skills/콘텐츠/SKILL.md`(2026-08-03 폐기) 본문에 과목 고유 값 13곳, `kit/*/by-shape.md`에 3곳.
그 상태로 다른 주제 강의에 이 스킬을 쓰면 **남의 과목 실측치가 규칙으로 강요된다.**
과목 고유 값의 정본은 `courses/<과목>/profile.md`이고, 스킬 본문에는 어느 과목에나 적용되는
규칙만 남아야 한다.

이 검사기가 P1(주제 격리)의 **합격 조건**이다 — 검사기 없이 "다 옮겼다"고 하면 자기보고이고,
이 저장소에서 자기보고는 이미 두 번 틀렸다(청크 P0 승격이 인덱스만 바뀐 채 게이트 통과 /
"6장에 규칙 적용"이 실제로는 강조만 얹음).

무엇을 검사하나
--------------
- **FAIL**: 프로필 §8이 등재한 리터럴이 스킬 본문에 있으면. 격리 후에는 0이어야 한다.
- **WARN**: 회차 지시자(`N주차`). 사고 이력·근거로서의 언급은 **정당하므로** 지우지 않는다
  (규칙의 "왜"가 사라지면 재발 방지력이 죽는다). 사람이 문맥을 확인하라는 신호일 뿐이다.
- frontmatter(`---` 블록)는 검사에서 뺀다 — `description`은 스킬 발견을 좌우하고
  변경 시 `evals/trigger-eval.json` 회귀 확인이 필요해 P1 범위 밖이다.

사용
----
    python scripts/verify_subject_isolation.py
    python scripts/verify_subject_isolation.py --profile courses/<과목>/profile.md

종료코드: 0 통과(WARN 있어도 0) · 1 FAIL · 2 프로필 없음/스키마 불량
"""
import io
import os
import re
import sys
import glob
import argparse

if hasattr(sys.stdout, "reconfigure"):          # Windows cp949에서 한글이 죽지 않게
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def discover_profiles():
    """검사할 과목 프로필 **전부**. 과목이 N개면 N개를 돌려준다.

    ⚠️ 2026-08-24 이전에는 `profile_path()` 하나만 봤고, 과목이 2개가 되면 그것이
    None을 주는 바람에 존재하지 않는 플레이스홀더 경로 → `SKIP` → **exit 0**이었다.
    다과목을 지키라고 만든 게이트가 다과목이 되는 바로 그 순간 스스로 꺼진 것이다.
    (`plans/gate-input-hardening/PLAN.md` F4)"""
    try:
        import _course_paths
        root = _course_paths._repo_root()
        return [os.path.relpath(p, root).replace(os.sep, "/")
                for p in _course_paths.profile_paths(root)]
    except Exception as exc:                     # 모듈 자체가 못 읽히면 조용히 넘기지 않는다
        print("FAIL  과목 경로 해석기를 읽을 수 없습니다: %s" % exc)
        return None

# 스킬 본문 — 여기서 발견되면 FAIL
SCAN_FAIL = [
    "SKILL.md",
    "skills/*/SKILL.md",
    "kit/guide/*.md",
    "kit/layouts/by-shape.md",
    "kit/charts/by-shape.md",
    "references/phases/*.md",
    # 테마는 과목 사이를 옮겨 다니는 공유 자산이다(과목:테마 = N:1) — 과목 고유 값이
    # 섞이면 그 테마를 쓰는 다른 과목이 남의 값을 물려받는다. 2026-08-24 P3.
    "kit/themes/*/tokens.css",
]
# 예시·서식 문서 — 발견돼도 WARN (예시에 과목명이 있는 것은 교육상 유용할 수 있다)
SCAN_WARN = [
    "references/*.md",
    "입력양식/*.md",
    # ── kit 자산 (2026-08-29 신설 · 미탐 해소) ────────────────────────────────
    # 종전 스캔 범위는 «문서»(.md)와 테마 선언뿐이었다. 그래서 **새 덱에 그대로
    # 상속되는 자산**은 아무도 보지 않았고, 실측 결과 공용 kit에 한 과목의 브랜드가
    # 31곳 있었다(스타터 워드마크 5 · 로고 aria-label 1 · 파비콘 default 팔레트 ·
    # deck.css 헤더 1 · 카탈로그 23). 게이트는 그동안 PASS였다 — 전형적인 미탐이다.
    #
    # 편입 기준은 «그 파일의 내용이 새 과목의 덱으로 상속되는가»다:
    #   starter/*      → 복사돼 새 덱이 된다              → 편입
    #   styles/*.css   → 링크돼 모든 덱에 적용된다        → 편입
    #   catalog.html   → 열람용 아틀라스(상속 안 됨)      → 제외
    #   CHANGELOG.md   → 변경 이력(사고 이력은 정당)      → 제외
    #
    # WARN으로 시작한다 — 이 저장소 규율대로 오탐률을 먼저 재고 0에 수렴할 때 FAIL로
    # 승격한다. 신설 시점 실측: 편입 대상 오탐 0 · 미탐 0(브랜드 리터럴 전량 제거 완료).
    "kit/starter/*",
    "kit/styles/*.css",
]
EXCLUDE_DIRS = ("sessions/", "_dev/", ".agents/", ".claude/", "evals/")
# 문서 전체가 과목 종속 산출물이라 격리 대상이 아니라 재분류 대상인 파일.
# 사유는 `courses/<과목>/profile.md` §8 「검사에서 제외한 것과 사유」가 정본이다.
EXCLUDE_FILES = ("kit/guide/교육원칙-요약.md",)

ROUND_RE = re.compile(r"\d+\s*주차")
FM_RE = re.compile(r"\A---\n.*?\n---\n", re.S)


def strip_frontmatter(text):
    """frontmatter를 같은 줄 수의 빈 줄로 바꿔 행번호를 보존한다."""
    m = FM_RE.match(text)
    if not m:
        return text
    return "\n" * m.group(0).count("\n") + text[m.end():]


def read_profile_literals(path):
    """프로필 §8 「격리 검사용 리터럴」의 불릿을 읽는다."""
    if not os.path.isfile(path):
        return None
    text = io.open(path, encoding="utf-8").read()
    m = re.search(r"^##\s*8\..*?격리 검사용 리터럴.*?$(.*?)(?=^##\s|\Z)",
                  text, re.M | re.S)
    if not m:
        return []
    out = []
    for line in m.group(1).splitlines():
        line = line.strip()
        if line.startswith("- "):
            lit = line[2:].split("  #")[0].strip().strip("`")
            if lit:
                out.append(lit)
    return out


def expand(patterns):
    files = []
    for pat in patterns:
        for p in glob.glob(pat):
            p = p.replace(os.sep, "/")
            if any(p.startswith(d) for d in EXCLUDE_DIRS) or p in EXCLUDE_FILES:
                continue
            if p not in files:
                files.append(p)
    return files


def scan(files, literals):
    fails, rounds = [], []
    for path in files:
        try:
            body = strip_frontmatter(io.open(path, encoding="utf-8").read())
        except (OSError, UnicodeDecodeError):
            continue
        for i, line in enumerate(body.splitlines(), 1):
            for lit in literals:
                if lit in line:
                    fails.append((path, i, lit, line.strip()[:90]))
            if ROUND_RE.search(line):
                rounds.append((path, i, line.strip()[:90]))
    return fails, rounds


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", default=None,
                    help="한 과목만 검사한다. 생략하면 courses/ 아래 과목 전부.")
    args = ap.parse_args()

    profiles = [args.profile] if args.profile else discover_profiles()
    if profiles is None:
        return 2
    if not profiles:
        # 종전에는 SKIP + exit 0이었다 — 「입력이 없다」를 「통과」로 보고하는 형태다.
        print("FAIL  검사할 과목 프로필이 하나도 없습니다 (courses/*/profile.md · sessions/과목프로필.md).")
        print("      입력이 없는 검사는 통과가 아니라 미판정입니다"
              " — 입력양식/과목프로필템플릿.md로 프로필을 만드세요.")
        return 2

    literals, per_course = [], []
    for prof in profiles:
        lits = read_profile_literals(prof)
        if lits is None:
            print("FAIL  과목 프로필을 읽을 수 없습니다: %s" % prof)
            return 2
        if not lits:
            print("FAIL  프로필에 「## 8. 격리 검사용 리터럴」 절이 없거나 비었습니다: %s"
                  % prof)
            return 2
        per_course.append((prof, len(lits)))
        for lit in lits:
            if lit not in literals:
                literals.append(lit)

    print("검사 과목 %d개: %s"
          % (len(per_course), ", ".join("%s(리터럴 %d)" % (p, n) for p, n in per_course)))

    fail_files = expand(SCAN_FAIL)
    warn_files = expand(SCAN_WARN)
    warn_files = [f for f in warn_files if f not in fail_files]

    fails, rounds = scan(fail_files, literals)
    soft, _ = scan(warn_files, literals)

    print("검사 리터럴 %d종 | FAIL 대상 %d파일 | WARN 대상 %d파일"
          % (len(literals), len(fail_files), len(warn_files)))
    print("-" * 66)

    for path, ln, lit, ctx in fails:
        print("FAIL  %s:%d  <%s>\n      %s" % (path, ln, lit, ctx))
    for path, ln, lit, ctx in soft:
        print("WARN  %s:%d  <%s>  (예시·서식 문서)" % (path, ln, lit))

    if rounds:
        print("\nWARN  회차 지시자 %d건 — 사고 이력·근거면 정당합니다. 문맥만 확인하세요."
              % len(rounds))
        for path, ln, ctx in rounds[:12]:
            print("      %s:%d  %s" % (path, ln, ctx))
        if len(rounds) > 12:
            print("      … 외 %d건" % (len(rounds) - 12))

    print("-" * 66)
    if fails:
        print("결과: FAIL %d건 — 과목 고유 값이 스킬 본문에 남아 있습니다." % len(fails))
        return 1
    print("결과: PASS — 스킬 본문에 과목 고유 값 0건"
          " (WARN %d건은 차단하지 않습니다)." % (len(soft) + len(rounds)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
