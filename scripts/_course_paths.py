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


class AmbiguousCourseError(RuntimeError):
    """어느 과목인지 특정할 수 없다.

    **조용히 하나를 고르지 않는다.** 2026-08-24 실측에서 이 모듈은 다과목 상황에
    서로 다른 전제 셋을 갖고 있었다 — `profile_path`/`guide_path`는 None(침묵),
    `session_dir`/`contracts_dir`는 가드 없이 첫 매치 채택(**오귀속**: 남의 과목
    N주차를 검증하고 PASS를 낸다), `sessions_roots`만 전부 반환. 침묵과 오귀속은
    둘 다 «검사가 꺼진 것»이 PASS로 보이는 형태이고, 미탐은 아무도 발견하지 못한다.
    그래서 모호하면 조용히 진행하는 대신 여기서 멈춘다."""


COURSE_ENV = "CREATE_SLIDES_COURSE"


def resolve_course(course=None, root=None):
    """과목 디렉터리 하나를 특정한다. → 경로 · 또는 None(courses/ 자체가 없는 구조)

    우선순위: 인자 `course` → 환경변수 `CREATE_SLIDES_COURSE` → 과목이 정확히 1개일 때 그것.
    특정할 수 없으면 `AmbiguousCourseError`를 던진다 — 호출부가 삼키지 말고 죽어야 한다.

    ⚠️ 환경변수는 «14개 스크립트에 --course 플래그를 다는 것»의 이행 경로다. 과목이
    둘 이상이 된 뒤에도 스크립트를 고치지 않고 돌릴 수 있게 한다."""
    root = root or _repo_root()
    dirs = course_dirs(root)
    want = course or os.environ.get(COURSE_ENV) or None
    if want:
        want = os.path.basename(str(want).replace("\\", "/").rstrip("/"))
        hit = [d for d in dirs if os.path.basename(d) == want]
        if len(hit) == 1:
            return hit[0]
        raise AmbiguousCourseError(
            "과목 '%s'을 courses/ 에서 찾을 수 없다. 후보: %s"
            % (want, [os.path.basename(d) for d in dirs] or "(없음)"))
    if not dirs:
        return None                       # courses/ 없는 구조 — 구경로 폴백 세계
    if len(dirs) == 1:
        return dirs[0]
    raise AmbiguousCourseError(
        "과목이 %d개라 어느 것인지 알 수 없다: %s\n"
        "  → 호출부에 course=를 넘기거나 환경변수 %s=<과목명>을 지정하라.\n"
        "  (조용히 첫 과목을 고르면 남의 과목을 검증하고 PASS를 낸다)"
        % (len(dirs), [os.path.basename(d) for d in dirs], COURSE_ENV))


def profile_path(root=None, course=None):
    """과목 프로필. `courses/<과목>/profile.md` 우선, 구경로 `sessions/과목프로필.md` 폴백.

    과목이 모호하면 None이 아니라 `AmbiguousCourseError`다 — 종전에는 None을 줬는데
    호출부가 그것을 「프로필 없음(정상)」으로 소비해 **게이트가 조용히 꺼졌다**."""
    root = root or _repo_root()
    d = resolve_course(course, root)
    news = [os.path.join(d, "profile.md")] if d else []
    news = [p for p in news if os.path.exists(p)]
    return _first_existing(news + [os.path.join(root, LEGACY_SESSIONS, "과목프로필.md")])


def profile_paths(root=None):
    """**모든** 과목 프로필 경로(신경로 전부, 없으면 구경로 1개). 과목 수만큼 돌려준다.

    `profile_path()`는 «하나를 특정»하는 API라 모호하면 예외지만, 이쪽은 «전부 훑는»
    API다 — 격리 검사처럼 과목마다 반복해야 하는 검사가 쓴다. 전수 순회 API가 없어서
    `verify_subject_isolation.py`가 과목 2개가 되는 순간 SKIP→exit 0으로 자멸했다."""
    root = root or _repo_root()
    out = [os.path.join(d, "profile.md") for d in course_dirs(root)]
    out = [p for p in out if os.path.exists(p)]
    if out:
        return out
    legacy = os.path.join(root, LEGACY_SESSIONS, "과목프로필.md")
    return [legacy] if os.path.exists(legacy) else []


def guide_path(root=None, course=None):
    """과목 슬라이드 지침 `courses/<과목>/슬라이드지침.md`. 없으면 None(구경로 없음 — 신설 문서).

    「파일이 없다」와 「어느 과목인지 모른다」는 다른 사건이다 — 후자는 예외로 구분한다."""
    root = root or _repo_root()
    d = resolve_course(course, root)
    if not d:
        return None
    p = os.path.join(d, "슬라이드지침.md")
    return p if os.path.exists(p) else None


def profile_gates(root=None, course=None):
    """프로필 §3-G 「게이트 임계값」을 {키: 문자열값}으로 읽는다.

    표를 스크래핑하지 않고 코드블록의 `키: 값` 줄만 읽는다 — 표 서식이 바뀌어도
    깨지지 않고, 무엇이 기계 판독 대상인지 사람이 눈으로 구분할 수 있다.
    프로필이 없거나 절이 없으면 **빈 dict**다. 호출부는 그때 FAIL을 WARN으로 낮춘다
    (다른 과목 값을 빌려 쓰지 않기 위함)."""
    p = profile_path(root, course)
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


def gate_num(key, default, root=None, cast=float, course=None):
    """임계값 하나를 읽는다. → (값, 프로필에서_왔는가)

    프로필에 없으면 (default, False)를 준다 — 호출부는 False일 때 판정을 WARN으로
    낮추고 그 사실을 보고해야 한다. **조용히 기본값을 쓰지 않는다.**"""
    raw = profile_gates(root, course).get(key)
    if raw is None:
        return default, False
    try:
        return cast(raw), True
    except (TypeError, ValueError):
        return default, False


def gate_range(key, default, root=None, course=None):
    """`8~11` 형태를 (lo, hi)로. → ((lo, hi), 프로필에서_왔는가)"""
    raw = profile_gates(root, course).get(key)
    if raw:
        m = re.match(r"^(\d+)\s*[~\-–]\s*(\d+)$", raw)
        if m:
            return (int(m.group(1)), int(m.group(2))), True
    return default, False


def session_dir(week, root=None, course=None):
    """N주차 폴더. `courses/<과목>/sessions/N주차` 우선, `sessions/N주차` 폴백.

    양쪽 다 없으면 **구경로를 돌려준다** — 호출부가 «없음» 메시지에 쓸 경로가
    필요하고, 신경로를 돌려주면 아직 존재하지 않는 위치를 가리켜 혼란스럽다.

    ⚠️ 종전에는 과목 가드가 **아예 없어** 여러 과목의 같은 주차 폴더 중 정렬순
    첫 매치를 조용히 채택했다. 그 결과는 「검사가 안 된 것」이 아니라 **「다른 과목을
    검사하고 PASS」**여서 침묵보다 나쁘다. 지금은 모호하면 예외다."""
    root = root or _repo_root()
    legacy = os.path.join(root, LEGACY_SESSIONS, "%s주차" % week)
    d = resolve_course(course, root)
    cands = [os.path.join(d, "sessions", "%s주차" % week)] if d else []
    return _first_existing(cands + [legacy]) or legacy


def contracts_dir(root=None, course=None):
    """주차 구조 계약 폴더 `_contracts`. 과목이 모호하면 예외(session_dir과 같은 이유)."""
    root = root or _repo_root()
    d = resolve_course(course, root)
    cands = [os.path.join(d, "sessions", "_contracts")] if d else []
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
