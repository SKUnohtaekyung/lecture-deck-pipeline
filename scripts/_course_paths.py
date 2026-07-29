# -*- coding: utf-8 -*-
"""과목 아키텍처 경로 해석기 — 신경로 우선, 구경로 폴백.

왜 필요한가
-----------
2026-07-29 P4.5에서 `courses/<과목>/` 상위 구조를 도입했다. 그런데 기존 경로 규약
(`sessions/N주차/`)에 스크립트 12파일·문서 35파일·산출물 221파일이 하드결합돼 있어
한 번에 끊으면 어디가 깨졌는지 좁히기 어렵다. 그래서 **두 단계로 나눈다**:

  1단계(지금) — `courses/<과목>/`에 profile·슬라이드지침을 두고, 모든 경로 조회를
                 이 모듈로 통과시킨다. 실제 산출물은 아직 `sessions/`에 있다.
  2단계(다음) — `sessions/N주차/`를 `courses/<과목>/sessions/`로 옮긴다. 이 모듈이
                 이미 양쪽을 보므로 스크립트는 고치지 않아도 된다.

⚠️ **구경로 폴백을 없애지 마라.** 1주차 자료 4파일이 메타 헤더에서 구경로를 참조하는데
1주차는 수정 금지(동결)다. 폴백을 지우면 그 참조가 영구히 깨진다.
"""
import io
import os
import re

COURSES_DIR = "courses"
LEGACY_SESSIONS = "sessions"


def _repo_root(start=None):
    """이 파일 기준 저장소 루트(scripts/의 부모)."""
    here = os.path.dirname(os.path.abspath(start or __file__))
    return os.path.dirname(here)


def course_dirs(root=None):
    """`courses/<과목>/` 목록. 없으면 빈 리스트."""
    root = root or _repo_root()
    base = os.path.join(root, COURSES_DIR)
    if not os.path.isdir(base):
        return []
    out = []
    for name in sorted(os.listdir(base)):
        p = os.path.join(base, name)
        if os.path.isdir(p) and not name.startswith(("_", ".")):
            out.append(p)
    return out


def _first_existing(candidates):
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return None


def profile_path(root=None):
    """과목 프로필. `courses/*/profile.md` 우선, 구경로 `sessions/과목프로필.md` 폴백.

    과목이 여럿이면 첫 번째를 쓰지 않고 None을 돌려준다 — 어느 과목인지 모른 채
    한쪽 기준선을 적용하면 «남의 과목 실측치를 물려받는» 바로 그 실패다."""
    root = root or _repo_root()
    news = [os.path.join(d, "profile.md") for d in course_dirs(root)]
    news = [p for p in news if os.path.exists(p)]
    if len(news) > 1:
        return None
    return _first_existing(news + [os.path.join(root, LEGACY_SESSIONS, "과목프로필.md")])


def guide_path(root=None):
    """과목 슬라이드 지침 `courses/*/슬라이드지침.md`. 없으면 None(구경로 없음 — 신설 문서)."""
    root = root or _repo_root()
    news = [os.path.join(d, "슬라이드지침.md") for d in course_dirs(root)]
    news = [p for p in news if os.path.exists(p)]
    return news[0] if len(news) == 1 else None


def profile_gates(root=None):
    """프로필 §3-G 「게이트 임계값」을 {키: 문자열값}으로 읽는다.

    표를 스크래핑하지 않고 코드블록의 `키: 값` 줄만 읽는다 — 표 서식이 바뀌어도
    깨지지 않고, 무엇이 기계 판독 대상인지 사람이 눈으로 구분할 수 있다.
    프로필이 없거나 절이 없으면 **빈 dict**다. 호출부는 그때 FAIL을 WARN으로 낮춘다
    (다른 과목 값을 빌려 쓰지 않기 위함)."""
    p = profile_path(root)
    if not p:
        return {}
    try:
        with io.open(p, encoding="utf-8") as fh:
            text = fh.read()
    except (OSError, UnicodeDecodeError):
        return {}
    m = re.search(r"^###\s*3-G\..*?$(.*?)(?=^#{2,3}\s|\Z)", text, re.M | re.S)
    if not m:
        return {}
    out = {}
    for line in m.group(1).splitlines():
        line = line.strip()
        if line.startswith(("|", ">", "#")) or "`" in line:
            continue                                  # 표·인용·본문 줄은 건너뛴다
        mm = re.match(r"^([A-Za-z가-힣_]+)\s*:\s*(\S+)\s*$", line)
        if mm:
            out[mm.group(1)] = mm.group(2)
    return out


def gate_num(key, default, root=None, cast=float):
    """임계값 하나를 읽는다. → (값, 프로필에서_왔는가)

    프로필에 없으면 (default, False)를 준다 — 호출부는 False일 때 판정을 WARN으로
    낮추고 그 사실을 보고해야 한다. **조용히 기본값을 쓰지 않는다.**"""
    raw = profile_gates(root).get(key)
    if raw is None:
        return default, False
    try:
        return cast(raw), True
    except (TypeError, ValueError):
        return default, False


def gate_range(key, default, root=None):
    """`8~11` 형태를 (lo, hi)로. → ((lo, hi), 프로필에서_왔는가)"""
    raw = profile_gates(root).get(key)
    if raw:
        m = re.match(r"^(\d+)\s*[~\-–]\s*(\d+)$", raw)
        if m:
            return (int(m.group(1)), int(m.group(2))), True
    return default, False


def session_dir(week, root=None):
    """N주차 폴더. `courses/*/sessions/N주차` 우선, `sessions/N주차` 폴백.

    양쪽 다 없으면 **구경로를 돌려준다** — 호출부가 «없음» 메시지에 쓸 경로가
    필요하고, 신경로를 돌려주면 아직 존재하지 않는 위치를 가리켜 혼란스럽다."""
    root = root or _repo_root()
    legacy = os.path.join(root, LEGACY_SESSIONS, "%s주차" % week)
    cands = [os.path.join(d, "sessions", "%s주차" % week) for d in course_dirs(root)]
    return _first_existing(cands + [legacy]) or legacy


def contracts_dir(root=None):
    """주차 구조 계약 폴더 `_contracts`."""
    root = root or _repo_root()
    cands = [os.path.join(d, "sessions", "_contracts") for d in course_dirs(root)]
    return _first_existing(cands + [os.path.join(root, LEGACY_SESSIONS, "_contracts")])


def sessions_roots(root=None):
    """세션 트리 루트 전부(신·구). glob 패턴을 만들 때 쓴다."""
    root = root or _repo_root()
    out = [os.path.join(d, "sessions") for d in course_dirs(root)]
    out = [p for p in out if os.path.isdir(p)]
    legacy = os.path.join(root, LEGACY_SESSIONS)
    if os.path.isdir(legacy):
        out.append(legacy)
    return out


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    r = _repo_root()
    print("repo root      :", r)
    print("course dirs    :", [os.path.relpath(d, r) for d in course_dirs(r)])
    p = profile_path(r)
    print("profile        :", os.path.relpath(p, r) if p else None)
    g = guide_path(r)
    print("slide guide    :", os.path.relpath(g, r) if g else None)
    print("contracts      :", os.path.relpath(contracts_dir(r), r) if contracts_dir(r) else None)
    for w in (1, 2, 3):
        print("session %s주차   :" % w, os.path.relpath(session_dir(w, r), r))
