# -*- coding: utf-8 -*-
"""과목 경로 해석기(`scripts/_course_paths.py`)의 다과목 거동 회귀 테스트.

왜 이 파일이 필요한가
--------------------
2026-08-24 실측(`plans/gate-input-hardening/PLAN.md` F4): 이 모듈은 다과목 상황에
대해 **서로 다른 전제 셋**을 갖고 있었고, 그 전제들이 전부 «검사가 꺼진 것»을
PASS처럼 보이게 만들었다.

  - `profile_path`·`guide_path` — 모호하면 `None`. 호출부가 그것을 「없음(정상)」으로
    소비해 게이트가 **조용히 꺼졌다**. `verify_subject_isolation.py`가 그 경로로
    과목 2개가 되는 순간 SKIP → **exit 0**으로 자멸했다.
  - `session_dir`·`contracts_dir` — 가드가 **아예 없어** 정렬순 첫 매치를 조용히 채택.
    결과는 「검사 안 됨」이 아니라 **「다른 과목을 검사하고 PASS」**여서 침묵보다 나쁘다.
  - `sessions_roots` — 전부 반환(유일하게 다과목 안전).

이 저장소의 규율은 「오탐만 재면 반쪽이다 — 미탐도 함께 잰다」이고, 미탐은 PASS로
위장해 아무도 발견하지 못한다. 그래서 **모호하면 시끄럽게 죽는다**를 계약으로 고정한다.

무엇을 테스트하나
----------------
- 과목 1개일 때 **종전과 완전히 같은 경로**를 준다(before/after 불변 — 이 계획의 통과 조건).
- 과목 2개일 때 각 API가 **조용한 오답 대신 예외**를 낸다.
- 명시 지정(인자·환경변수)이 모호성을 해소한다.
- 전수 순회 API(`profile_paths`)가 과목 수만큼 돌려준다.

실행: python -m unittest tests.test_course_paths
"""
from __future__ import annotations

import io
import os
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import _course_paths as cp  # noqa: E402


def _mkcourse(root: Path, name: str, *, profile=True, guide=True, weeks=()) -> Path:
    d = root / "courses" / name
    (d / "sessions").mkdir(parents=True, exist_ok=True)
    if profile:
        with io.open(d / "profile.md", "w", encoding="utf-8") as fh:
            fh.write("# %s\n" % name)
    if guide:
        with io.open(d / "슬라이드지침.md", "w", encoding="utf-8") as fh:
            fh.write("# %s 지침\n" % name)
    for w in weeks:
        (d / "sessions" / ("%s주차" % w)).mkdir(parents=True, exist_ok=True)
    return d


class SingleCourseUnchangedTests(unittest.TestCase):
    """과목 1개 — 종전 동작이 그대로여야 한다(이 계획의 하드 통과 조건)."""

    def setUp(self):
        import tempfile
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        _mkcourse(self.root, "가과목", weeks=(1, 3))

    def tearDown(self):
        self.tmp.cleanup()

    def test_profile_and_guide_resolve(self):
        self.assertTrue(cp.profile_path(str(self.root)).endswith("profile.md"))
        self.assertTrue(cp.guide_path(str(self.root)).endswith("슬라이드지침.md"))

    def test_session_dir_points_into_the_course(self):
        got = cp.session_dir(3, str(self.root)).replace(os.sep, "/")
        self.assertTrue(got.endswith("courses/가과목/sessions/3주차"), got)

    def test_missing_week_falls_back_to_legacy_path_string(self):
        """없는 주차는 예외가 아니라 «구경로 문자열» — 호출부가 «없음» 메시지에 쓴다."""
        got = cp.session_dir(9, str(self.root)).replace(os.sep, "/")
        self.assertTrue(got.endswith("sessions/9주차"), got)

    def test_guide_absent_is_none_not_error(self):
        """「파일이 없다」와 「어느 과목인지 모른다」는 다른 사건이다."""
        os.remove(self.root / "courses" / "가과목" / "슬라이드지침.md")
        self.assertIsNone(cp.guide_path(str(self.root)))


class AmbiguousCourseIsLoudTests(unittest.TestCase):
    """과목 2개 — 조용한 오답(None·첫 매치) 대신 예외."""

    def setUp(self):
        import tempfile
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        _mkcourse(self.root, "가과목", weeks=(1, 3))
        _mkcourse(self.root, "나과목", weeks=(1, 3))
        self._saved = os.environ.pop(cp.COURSE_ENV, None)

    def tearDown(self):
        if self._saved is not None:
            os.environ[cp.COURSE_ENV] = self._saved
        else:
            os.environ.pop(cp.COURSE_ENV, None)
        self.tmp.cleanup()

    def test_profile_path_raises_instead_of_returning_none(self):
        with self.assertRaises(cp.AmbiguousCourseError):
            cp.profile_path(str(self.root))

    def test_guide_path_raises(self):
        with self.assertRaises(cp.AmbiguousCourseError):
            cp.guide_path(str(self.root))

    def test_session_dir_raises_instead_of_silently_picking_first(self):
        """가장 위험한 미탐 — 종전에는 «남의 과목 3주차»를 조용히 돌려주고 PASS를 냈다."""
        with self.assertRaises(cp.AmbiguousCourseError):
            cp.session_dir(3, str(self.root))

    def test_contracts_dir_raises(self):
        with self.assertRaises(cp.AmbiguousCourseError):
            cp.contracts_dir(str(self.root))

    def test_profile_gates_propagates_rather_than_returning_empty(self):
        """빈 dict를 주면 호출부가 FAIL을 WARN으로 낮춘다 — 그것도 조용한 무력화다."""
        with self.assertRaises(cp.AmbiguousCourseError):
            cp.profile_gates(str(self.root))

    def test_sessions_roots_still_returns_all(self):
        """전수 순회 API는 모호하지 않다 — 예외 대상이 아니다."""
        roots = cp.sessions_roots(str(self.root))
        self.assertEqual(len(roots), 2, roots)

    def test_explicit_course_argument_resolves(self):
        got = cp.session_dir(3, str(self.root), course="나과목").replace(os.sep, "/")
        self.assertTrue(got.endswith("courses/나과목/sessions/3주차"), got)

    def test_env_var_resolves(self):
        os.environ[cp.COURSE_ENV] = "가과목"
        got = cp.session_dir(3, str(self.root)).replace(os.sep, "/")
        self.assertTrue(got.endswith("courses/가과목/sessions/3주차"), got)

    def test_unknown_course_name_raises(self):
        with self.assertRaises(cp.AmbiguousCourseError):
            cp.profile_path(str(self.root), course="없는과목")

    def test_profile_paths_returns_every_course(self):
        got = cp.profile_paths(str(self.root))
        self.assertEqual(len(got), 2, got)


class NamedCourseAgainstCourselessRootTests(unittest.TestCase):
    """`courses/` 자체가 없는 루트(구경로 폴백 세계)에서는 과목명을 무시하고 None을 준다.

    2026-08-29 정정. 종전에는 인자·환경변수로 과목이 «지정돼 있기만 하면» 후보가
    0개여도 `AmbiguousCourseError`를 던졌다. 그런데 이 예외의 목적은 **오귀속 방지**이고,
    고를 후보가 0개면 남의 과목을 고를 수가 없다 — 막을 사고가 없는 자리에서 죽은 것이다.

    실제 피해: 구경로 합성 픽스처를 읽는 호출(`verify_draft_quality`의 냉동 스냅샷
    테스트)이 **전역 `CREATE_SLIDES_COURSE` 하나 때문에** 통째로 깨졌다. 반대로 후보가
    1개 이상인데 이름이 안 맞는 경우(오타)는 **여전히 던진다** — 아래가 그 쌍을 고정한다.
    """

    def setUp(self):
        import tempfile
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "sessions" / "1주차").mkdir(parents=True)   # 구경로만 있는 루트
        self._saved = os.environ.pop(cp.COURSE_ENV, None)

    def tearDown(self):
        if self._saved is not None:
            os.environ[cp.COURSE_ENV] = self._saved
        else:
            os.environ.pop(cp.COURSE_ENV, None)
        self.tmp.cleanup()

    def test_explicit_course_is_ignored_when_there_are_no_courses(self):
        self.assertIsNone(cp.resolve_course("아무과목", str(self.root)))

    def test_env_course_is_ignored_when_there_are_no_courses(self):
        os.environ[cp.COURSE_ENV] = "아무과목"
        self.assertIsNone(cp.resolve_course(None, str(self.root)))

    def test_session_dir_falls_back_to_legacy_path(self):
        got = cp.session_dir(1, str(self.root), course="아무과목").replace(os.sep, "/")
        self.assertTrue(got.endswith("sessions/1주차"), got)
        self.assertNotIn("courses/", got)

    def test_typo_guard_survives_when_courses_exist(self):
        """후보가 있는데 이름이 안 맞으면 여전히 죽는다 — 완화가 여기까지 번지면 안 된다."""
        _mkcourse(self.root, "가과목", weeks=(1,))
        with self.assertRaises(cp.AmbiguousCourseError):
            cp.resolve_course("없는과목", str(self.root))


class GateModulesImportWithoutACourseTests(unittest.TestCase):
    """과목 종속 임계를 **import 시점에** 읽으면 다과목 저장소에서 모듈이 죽는다.

    2026-08-29 실측: `verify_deck_quality`·`verify_draft_quality`가 모듈 최상위에서
    `_load_profile_gates()`를 불렀고, 과목이 2개가 되는 순간 **import만으로**
    `AmbiguousCourseError`가 터져 `tests.test_quality_gates` 전체(53건)가 무너졌다.
    적재 시점을 `run_checks()` 진입으로 옮겼고, 이 테스트가 그 자리를 고정한다.
    """

    def test_import_does_not_require_a_course(self):
        import importlib
        import subprocess
        import sys as _sys
        repo = Path(__file__).resolve().parent.parent
        env = dict(os.environ)
        env.pop(cp.COURSE_ENV, None)          # 과목을 «지정하지 않은» 상태를 강제한다
        env["PYTHONIOENCODING"] = "utf-8"
        code = ("import sys; sys.path.insert(0, r'%s');"
                " import verify_deck_quality, verify_draft_quality; print('OK')"
                % (repo / "scripts"))
        proc = subprocess.run([_sys.executable, "-c", code], capture_output=True,
                              text=True, encoding="utf-8", cwd=str(repo), env=env)
        self.assertEqual(proc.returncode, 0,
                         "과목 미지정 import가 죽었다: %s" % (proc.stderr or ""))
        self.assertIn("OK", proc.stdout or "")


class IsolationScanCoversInheritedKitAssetsTests(unittest.TestCase):
    """새 덱으로 «상속»되는 kit 자산이 격리 스캔 범위 안에 있는가 (2026-08-29 신설).

    미탐이었다. 종전 스캔 범위는 문서(.md)와 테마 선언뿐이라, **복사돼 새 덱이 되는
    스타터**와 **모든 덱에 링크되는 공용 CSS**는 아무도 보지 않았다. 실측 결과 공용
    kit에 한 과목의 브랜드가 31곳 있었는데 게이트는 내내 PASS였다 — 오탐은 시끄러워서
    발견되지만 미탐은 PASS로 위장한다.

    편입 기준은 «그 파일의 내용이 새 과목의 덱으로 상속되는가»다. 아틀라스(열람용)와
    CHANGELOG(변경 이력)는 상속되지 않으므로 일부러 뺐다 — 범위를 넓히는 것이 목적이
    아니라 «상속 경로»를 덮는 것이 목적이다.
    """

    def setUp(self):
        import importlib
        import sys as _s
        repo = Path(__file__).resolve().parent.parent
        _s.path.insert(0, str(repo / "scripts"))
        self.vsi = importlib.import_module("verify_subject_isolation")
        self.repo = repo

    def test_starter_and_shared_styles_are_scanned(self):
        covered = set(self.vsi.expand(self.vsi.SCAN_FAIL) + self.vsi.expand(self.vsi.SCAN_WARN))
        for path in ("kit/starter/deck-template.html", "kit/starter/logo.svg",
                     "kit/styles/deck.css"):
            self.assertIn(path, covered,
                          "상속되는 kit 자산이 스캔 범위 밖이다 — 미탐 구간: %s" % path)

    def test_reference_only_assets_stay_out_of_scope(self):
        """열람용 아틀라스·변경 이력까지 끌어들이면 예시·이력이 전부 잡혀 소음이 된다."""
        covered = set(self.vsi.expand(self.vsi.SCAN_FAIL) + self.vsi.expand(self.vsi.SCAN_WARN))
        for path in ("kit/layouts/catalog.html", "kit/CHANGELOG.md"):
            self.assertNotIn(path, covered, path)

    def test_scan_actually_flags_a_planted_literal(self):
        """범위에 넣는 것과 «실제로 잡는 것»은 다르다 — 심어서 확인한다."""
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / "deck-template.html"
            f.write_text("<title>강의덱 — 어떤과목브랜드</title>", encoding="utf-8")
            hits, _rounds = self.vsi.scan([str(f)], ["어떤과목브랜드"])
            self.assertEqual(len(hits), 1, hits)

    #: 공용 kit에 «알려진» 과목 리터럴 — (파일, 리터럴). 새 누출은 이 목록에 없으므로 실패한다.
    #
    # 2026-08-29 현재 **비어 있다.** 한때 `kit/styles/deck.css`의 두 줄(파일 헤더의 조직명 ·
    # `.s-brand` 트래킹 근거 주석)이 있었고, 그것을 고치려면 같은 파일의 **선행 R-QC-14
    # 위반 11건**을 먼저 풀어야 했다(pre-commit이 `.css` 스테이징 시 막는다). 같은 날 그
    # 11건을 직계 선택자로 좁혀 해소한 뒤 주석도 정리해 0이 됐다.
    #
    # ⚠️ 「아직 못 고쳤다」를 **0으로 반올림하지 않는다.** 목록으로 두면 ① 남은 누출이
    #    계속 보이고 ② 새 누출은 즉시 실패하며 ③ 고쳤는데 목록에 남아 있으면 그것도 실패한다.
    KNOWN_KIT_LEAKS = set()

    def test_shared_kit_has_no_unknown_course_literal(self):
        """상속 경로의 누출은 «알려진 것»뿐이어야 한다 — 새 누출은 실패한다."""
        lits = []
        for prof in self.vsi.discover_profiles() or []:
            lits.extend(self.vsi.read_profile_literals(prof) or [])
        inherited = [p for p in self.vsi.expand(self.vsi.SCAN_WARN)
                     if p.startswith("kit/")]
        self.assertTrue(inherited, "상속 자산 스캔 대상이 비었다 — 범위 설정 오류")
        hits, _rounds = self.vsi.scan(inherited, lits)
        found = {(path, lit) for path, _ln, lit, _ctx in hits}
        new_leaks = found - self.KNOWN_KIT_LEAKS
        self.assertEqual(new_leaks, set(),
                         "공용 kit에 새 과목 리터럴이 새어 들어왔다: %s" % (sorted(new_leaks),))
        fixed = self.KNOWN_KIT_LEAKS - found
        self.assertEqual(fixed, set(),
                         "누출이 해소됐다 — KNOWN_KIT_LEAKS에서 지워라: %s" % (sorted(fixed),))


class SubjectIsolationSurvivesMultiCourseTests(unittest.TestCase):
    """`verify_subject_isolation.py`가 다과목에서 자멸하지 않는가 (F4 최상급 사례)."""

    def test_discover_profiles_uses_the_all_courses_api(self):
        import verify_subject_isolation as vsi
        found = vsi.discover_profiles()
        self.assertIsNotNone(found)
        self.assertTrue(found, "실제 저장소에서 프로필을 하나도 못 찾았다")

    def test_no_profile_is_failure_not_silent_pass(self):
        """입력이 없는 검사는 통과가 아니라 미판정 — 종전에는 SKIP + exit 0이었다."""
        import verify_subject_isolation as vsi
        saved = vsi.discover_profiles
        try:
            vsi.discover_profiles = lambda: []
            saved_argv = sys.argv[:]
            sys.argv = ["verify_subject_isolation.py"]
            try:
                rc = vsi.main()
            finally:
                sys.argv = saved_argv
            self.assertEqual(rc, 2, "프로필 0개인데 통과로 보고했다")
        finally:
            vsi.discover_profiles = saved


if __name__ == "__main__":
    unittest.main()
