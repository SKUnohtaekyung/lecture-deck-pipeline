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
import os

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
