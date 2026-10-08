# -*- coding: utf-8 -*-
"""PreToolUse 훅(`scripts/hook_slide_guard.py`)의 판정 회귀 테스트.

왜 이 파일이 필요한가
--------------------
훅은 `AGENTS.md` 「무엇이 기계로 강제되는가」 표에 **강제 계층**으로 올라 있는데,
2026-08-18까지 **회귀 테스트가 0개였다.** 검증은 `tmp/test_gate.py`라는 임시
스크립트로만 있었고 `tmp/`는 `.gitignore`돼 있어 클론에 남지 않는다. 즉 강제
계층이 조용히 망가져도 아무 게이트가 울리지 않는 상태였다.

무엇을 테스트하나
----------------
- `tmp-guard`의 **오탐 예외**(에이전트 영속 메모리) — 넓게 뚫리지 않았는지 함께 본다.
- 관측 모드가 **차단하지 않는다**는 계약과, `--enforce`가 실제로 차단한다는 계약.

⚠️ 여기서 «통과»는 「훅이 이 경로를 어떻게 판정하는가」까지다. 호스트(Claude
Code·Codex)가 그 출력을 실제로 존중하는지는 이 테스트의 범위가 아니다 —
Codex 쪽은 페이로드에 파일 경로 키 자체가 없다(2026-08-18 Gate 0 실측).

실행: python -m unittest tests.test_hook_guards
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
HOOK = REPO_ROOT / "scripts" / "hook_slide_guard.py"

sys.path.insert(0, str(REPO_ROOT / "scripts"))
from hook_slide_guard import is_persistent_agent_memory  # noqa: E402


def _home() -> str:
    return os.path.abspath(os.path.expanduser("~")).replace(os.sep, "/")


def _run_hook(path: str, *extra: str):
    """훅을 실제 프로세스로 돌려 (stdout, returncode)를 돌려준다."""
    payload = json.dumps({"tool_input": {"file_path": path}})
    proc = subprocess.run(
        [sys.executable, str(HOOK), "--mode", "tmp-guard", *extra],
        input=payload, capture_output=True, text=True, encoding="utf-8",
        cwd=str(REPO_ROOT),
    )
    return proc.stdout or "", proc.returncode


class TmpGuardAllowlistTests(unittest.TestCase):
    """오탐 예외가 «좁게» 뚫렸는지 — 넓게 뚫는 것이 이 저장소의 전형적 실패다."""

    def test_agent_memory_dir_is_allowed(self):
        """2026-08-17 관측 모드가 잡은 1건. 시스템이 지정한 영속 경로이므로 오탐이다."""
        for p in (
            _home() + "/.claude/projects/C--Users-miso-Desktop-template/memory/x.md",
            _home() + "/.claude/projects/other-key/memory/nested/y.md",
        ):
            self.assertTrue(is_persistent_agent_memory(p), f"허용돼야 한다: {p}")

    def test_allowlist_does_not_open_the_home_directory(self):
        """예외를 「홈 전체」로 넓히면 규칙이 사실상 사라진다 — 그 회귀를 막는다."""
        for p in (
            _home() + "/.claude/projects/key/other/x.md",   # memory/ 가 아니다
            _home() + "/.claude/projects/key.md",           # 프로젝트 키 층이 없다
            _home() + "/.claude/settings.json",
            _home() + "/memory/x.md",                       # projects/ 를 안 거쳤다
            _home() + "/x.md",
            "C:/Windows/Temp/x.txt",
            "/tmp/x.txt",
        ):
            self.assertFalse(is_persistent_agent_memory(p), f"막혀야 한다: {p}")

    def test_allowed_path_produces_no_warning(self):
        out, code = _run_hook(_home() + "/.claude/projects/k/memory/z.md")
        self.assertEqual(code, 0)
        self.assertNotIn("저장소 밖", out, "허용 경로인데 경고가 나왔다")

    def test_outside_path_still_warns_in_observe_mode(self):
        """예외를 넣다가 검출 자체를 죽이지 않았는지 — 정탐이 살아 있어야 한다."""
        out, code = _run_hook("C:/Windows/Temp/x.txt")
        self.assertEqual(code, 0, "관측 모드는 차단하지 않는다")
        self.assertIn("저장소 밖", out)
        self.assertIn("관측 모드", out, "관측 모드임이 출력에 드러나야 한다")
        self.assertNotIn('"decision": "block"', out, "관측 모드가 차단하면 계약 위반이다")

    def test_enforce_blocks_outside_path(self):
        out, _ = _run_hook("C:/Windows/Temp/x.txt", "--enforce")
        self.assertIn("block", out, "--enforce는 실제로 차단해야 한다")

    def test_enforce_does_not_block_allowed_path(self):
        out, _ = _run_hook(_home() + "/.claude/projects/k/memory/z.md", "--enforce")
        self.assertNotIn("block", out, "허용 경로는 승격 후에도 통과해야 한다")

    def test_inside_repo_path_is_silent(self):
        out, code = _run_hook(str(REPO_ROOT / "tmp" / "scratch.txt"))
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), "", "저장소 안 쓰기는 아무 말도 하지 않는다")



# ── 같은 주입을 세션 안에서 되풀이하지 않는다(2026-10-08) ────────────────
import hashlib  # noqa: E402
import shutil  # noqa: E402
import time  # noqa: E402
import uuid  # noqa: E402

STATE_DIR = REPO_ROOT / "tmp" / "hook-state"
COURSE_A = "courses/바이브코딩/sessions/2주차/2주차_초안.md"
COURSE_B = "courses/바이브코딩_온라인/sessions/1주차/1주차_초안.md"
DECK = "courses/바이브코딩/sessions/2주차/강의덱.초안/part-01.html"


def _state_file(session_id: str, agent_id=None) -> Path:
    """훅이 이 세션(·에이전트)에 쓰는 상태 파일 — 이름은 원문 ID의 해시다."""
    ident = json.dumps([session_id, agent_id], ensure_ascii=True)
    return STATE_DIR / (hashlib.sha256(ident.encode("ascii")).hexdigest()[:32] + ".json")


def _run_mode(mode: str, path: str, session_id=None, env=None, agent_id=None):
    """checklist·course 훅을 실제 프로세스로 돌려 (stdout, returncode)를 돌려준다."""
    payload = {"tool_input": {"file_path": path}}
    if session_id is not None:
        payload["session_id"] = session_id
    if agent_id is not None:
        payload["agent_id"] = agent_id
    full_env = dict(os.environ)
    full_env.pop("CREATE_SLIDES_COURSE", None)
    full_env.pop("HOOK_REINJECT_MINUTES", None)
    full_env.update(env or {})
    proc = subprocess.run(
        [sys.executable, str(HOOK), "--mode", mode],
        input=json.dumps(payload).encode("utf-8"), capture_output=True,
        cwd=str(REPO_ROOT), env=full_env,
    )
    return proc.stdout.decode("utf-8"), proc.returncode


class InjectOncePerSessionTests(unittest.TestCase):
    def setUp(self):
        self.sids = []

    def tearDown(self):
        for path in self.sids:
            try:
                path.unlink()
            except OSError:
                shutil.rmtree(path, ignore_errors=True)

    def _sid(self, agent_id=None) -> str:
        sid = "test-" + uuid.uuid4().hex
        self.sids.append(_state_file(sid))
        if agent_id is not None:
            self.sids.append(_state_file(sid, agent_id))
        return sid

    def test_course_injects_once_per_session(self):
        sid = self._sid()
        baseline, _ = _run_mode("course", COURSE_A)
        first, rc1 = _run_mode("course", COURSE_A, sid)
        second, rc2 = _run_mode("course", COURSE_A, sid)
        self.assertIn("과목 지침", first)
        self.assertEqual(first, baseline, "첫 주입 문구는 종전과 같아야 한다")
        self.assertEqual(second, "")
        self.assertEqual((rc1, rc2), (0, 0))

    def test_checklist_injects_once_per_session(self):
        sid = self._sid()
        baseline, _ = _run_mode("checklist", DECK)
        first, _ = _run_mode("checklist", DECK, sid)
        second, _ = _run_mode("checklist", DECK, sid)
        self.assertTrue(first)
        self.assertEqual(first, baseline)
        self.assertEqual(second, "")

    def test_other_session_injects_again(self):
        a, _ = _run_mode("course", COURSE_A, self._sid())
        b, _ = _run_mode("course", COURSE_A, self._sid())
        self.assertTrue(a)
        self.assertEqual(a, b)

    def test_other_course_injects_in_same_session(self):
        sid = self._sid()
        a, _ = _run_mode("course", COURSE_A, sid)
        b, _ = _run_mode("course", COURSE_B, sid)
        b2, _ = _run_mode("course", COURSE_B, sid)
        self.assertTrue(a)
        self.assertTrue(b)
        self.assertNotEqual(a, b)
        self.assertEqual(b2, "")

    def test_modes_do_not_share_a_key(self):
        sid = self._sid()
        _run_mode("course", DECK, sid)
        out, _ = _run_mode("checklist", DECK, sid)
        self.assertTrue(out, "course 주입이 checklist 주입을 막으면 안 된다")

    def test_no_session_id_injects_every_time(self):
        a, _ = _run_mode("course", COURSE_A)
        b, _ = _run_mode("course", COURSE_A)
        self.assertTrue(a)
        self.assertEqual(a, b)

    def test_reinjects_after_interval(self):
        sid = self._sid()
        _run_mode("course", COURSE_A, sid)
        state = _state_file(sid)
        data = json.loads(state.read_text(encoding="utf-8"))
        self.assertEqual(len(data), 1)
        key = next(iter(data))
        data[key] = time.time() - 31 * 60
        state.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        again, _ = _run_mode("course", COURSE_A, sid)
        self.assertIn("과목 지침", again, "간격(기본 30분)이 지나면 다시 주입해야 한다")

    def test_interval_zero_restores_old_behaviour(self):
        sid = self._sid()
        env = {"HOOK_REINJECT_MINUTES": "0"}
        a, _ = _run_mode("course", COURSE_A, sid, env)
        b, _ = _run_mode("course", COURSE_A, sid, env)
        self.assertTrue(a)
        self.assertEqual(a, b)

    def test_broken_state_file_fails_open(self):
        sid = self._sid()
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        _state_file(sid).write_text("{not json", encoding="utf-8")
        out, rc = _run_mode("course", COURSE_A, sid)
        self.assertIn("과목 지침", out)
        self.assertEqual(rc, 0)

    def test_unwritable_state_fails_open(self):
        """상태를 쓸 수 없으면(같은 이름의 폴더가 자리를 막음) 매번 주입하고 죽지 않는다."""
        sid = self._sid()
        blocker = _state_file(sid)
        blocker.mkdir(parents=True, exist_ok=True)
        try:
            a, rc1 = _run_mode("course", COURSE_A, sid)
            b, rc2 = _run_mode("course", COURSE_A, sid)
        finally:
            shutil.rmtree(blocker, ignore_errors=True)
        self.assertIn("과목 지침", a)
        self.assertEqual(a, b)
        self.assertEqual((rc1, rc2), (0, 0))

    def test_session_id_cannot_escape_state_dir(self):
        tail = uuid.uuid4().hex
        sid = "../../" + tail
        self.sids.append(_state_file(sid))
        out, _ = _run_mode("course", COURSE_A, sid)
        again, _ = _run_mode("course", COURSE_A, sid)
        self.assertTrue(out)
        self.assertEqual(again, "")
        self.assertTrue(_state_file(sid).is_file(), "상태는 tmp/hook-state/ 안의 해시 이름 파일에만 쓴다")
        for stray in (REPO_ROOT.parent / (tail + ".json"), REPO_ROOT / (tail + ".json"),
                      REPO_ROOT / "tmp" / (tail + ".json")):
            self.assertFalse(stray.exists(), str(stray))

    def test_similar_session_ids_do_not_collide(self):
        """글자를 걸러 이름을 만들면 `a/b`와 `a:b`가 한 파일을 써서 뒤 세션이 첫 주입을 놓친다."""
        tail = uuid.uuid4().hex
        a, b = "x/" + tail, "x:" + tail
        self.sids += [_state_file(a), _state_file(b)]
        first, _ = _run_mode("course", COURSE_A, a)
        other, _ = _run_mode("course", COURSE_A, b)
        self.assertTrue(first)
        self.assertEqual(other, first, "다른 세션의 첫 호출은 주입돼야 한다")

    def test_subagent_gets_its_own_first_injection(self):
        """서브에이전트는 창이 따로다 — 부모가 받은 지침이 서브에이전트의 첫 주입을 막으면 안 된다."""
        sid = self._sid(agent_id="agent-1")
        self.sids.append(_state_file(sid, "agent-2"))
        parent, _ = _run_mode("course", COURSE_A, sid)
        child, _ = _run_mode("course", COURSE_A, sid, agent_id="agent-1")
        child_again, _ = _run_mode("course", COURSE_A, sid, agent_id="agent-1")
        sibling, _ = _run_mode("course", COURSE_A, sid, agent_id="agent-2")
        parent_again, _ = _run_mode("course", COURSE_A, sid)
        self.assertTrue(parent)
        self.assertEqual(child, parent)
        self.assertEqual(child_again, "")
        self.assertEqual(sibling, parent)
        self.assertEqual(parent_again, "")

    def test_separator_lookalike_session_id_does_not_collide_with_agent(self):
        """세션 ID에 구분자 모양을 넣어도 (세션, 에이전트) 쌍의 파일과 겹치지 않는다."""
        tail = uuid.uuid4().hex
        fake = tail + "\x00agent:A"
        self.sids += [_state_file(fake), _state_file(tail, "A"), _state_file(tail)]
        first, _ = _run_mode("course", COURSE_A, tail, agent_id="A")
        other, _ = _run_mode("course", COURSE_A, fake)
        self.assertTrue(first)
        self.assertEqual(other, first)
        self.assertNotEqual(_state_file(fake), _state_file(tail, "A"))

    def test_unencodable_session_ids_do_not_collide(self):
        """UTF-8로 못 옮기는 글자(짝 없는 서러게이트)가 `?`로 뭉개져 겹치면 안 된다."""
        tail = uuid.uuid4().hex
        ids = [tail + "?", tail + "\ud800", tail + "\ud801"]
        self.sids += [_state_file(i) for i in ids]
        self.assertEqual(len({_state_file(i) for i in ids}), 3)
        payloads = []
        for i in ids:
            body = json.dumps({"tool_input": {"file_path": COURSE_A}, "session_id": i}).encode("ascii")
            env = dict(os.environ)
            env.pop("CREATE_SLIDES_COURSE", None)
            env.pop("HOOK_REINJECT_MINUTES", None)
            proc = subprocess.run([sys.executable, str(HOOK), "--mode", "course"], input=body,
                                  capture_output=True, cwd=str(REPO_ROOT), env=env)
            payloads.append((proc.stdout.decode("utf-8"), proc.returncode))
        self.assertTrue(all(out and rc == 0 for out, rc in payloads), "셋 다 첫 호출에서 주입돼야 한다")

    def test_non_finite_interval_falls_back_to_default(self):
        for value in ("inf", "-inf", "nan", "1e999", "abc", ""):
            sid = self._sid()
            env = {"HOOK_REINJECT_MINUTES": value}
            first, _ = _run_mode("course", COURSE_A, sid, env)
            second, _ = _run_mode("course", COURSE_A, sid, env)
            self.assertTrue(first, value)
            self.assertEqual(second, "", value)
            state = _state_file(sid)
            data = json.loads(state.read_text(encoding="utf-8"))
            key = next(iter(data))
            data[key] = time.time() - 31 * 60
            state.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            again, _ = _run_mode("course", COURSE_A, sid, env)
            self.assertEqual(again, first, "%r — 31분 뒤에는 다시 주입돼야 한다(기본 30분)" % value)

    def test_state_is_written_only_after_the_injection_is_emitted(self):
        """기록이 주입보다 먼저면 출력 실패 때 기록만 남는다 — 소스의 순서를 고정한다."""
        src = HOOK.read_text(encoding="utf-8")
        for emit, mark in (('emit_context(CHECKLIST)', 'mark_injected(session_id, "checklist")'),
                           ('emit_context("\\n".join(body))', 'mark_injected(session_id, inject_key)')):
            self.assertIn(emit, src)
            self.assertIn(mark, src)
            self.assertLess(src.index(emit), src.index(mark))
        start = src.index("def injected_recently(")
        self.assertNotIn("open(state_path, \"w\"", src[start:src.index("def mark_injected(")])

    def test_non_string_session_id_injects_every_time(self):
        a, _ = _run_mode("course", COURSE_A, 12345)
        b, _ = _run_mode("course", COURSE_A, 12345)
        self.assertTrue(a)
        self.assertEqual(a, b)


def _run_reset(session_id=None, extra=None):
    """SessionStart(compact)가 부르는 reset-state를 실제 프로세스로 돌린다."""
    payload = {"hook_event_name": "SessionStart", "source": "compact"}
    if session_id is not None:
        payload["session_id"] = session_id
    payload.update(extra or {})
    env = dict(os.environ)
    env.pop("CREATE_SLIDES_COURSE", None)
    proc = subprocess.run(
        [sys.executable, str(HOOK), "--mode", "reset-state"],
        input=json.dumps(payload).encode("utf-8"), capture_output=True,
        cwd=str(REPO_ROOT), env=env,
    )
    return proc.stdout.decode("utf-8"), proc.stderr.decode("utf-8", "replace"), proc.returncode


class ResetStateAfterCompactionTests(unittest.TestCase):
    """압축되면 넣어 둔 지침이 창에서 사라진다 — 기록을 지워 다음 편집에서 다시 넣게 한다."""

    def setUp(self):
        self.paths = []

    def tearDown(self):
        for path in self.paths:
            try:
                path.unlink()
            except OSError:
                pass

    def _sid(self, *agents) -> str:
        sid = "test-" + uuid.uuid4().hex
        self.paths.append(_state_file(sid))
        for agent in agents:
            self.paths.append(_state_file(sid, agent))
        return sid

    def test_reset_makes_next_edit_inject_again(self):
        sid = self._sid()
        first, _ = _run_mode("course", COURSE_A, sid)
        _run_mode("checklist", DECK, sid)
        self.assertEqual(_run_mode("course", COURSE_A, sid)[0], "")
        out, err, rc = _run_reset(sid)
        self.assertEqual((out, err, rc), ("", "", 0), "SessionStart의 stdout은 컨텍스트에 들어간다 — 비어 있어야 한다")
        self.assertFalse(_state_file(sid).exists())
        self.assertEqual(_run_mode("course", COURSE_A, sid)[0], first)
        self.assertTrue(_run_mode("checklist", DECK, sid)[0])

    def test_reset_leaves_other_sessions_and_subagents_alone(self):
        sid = self._sid("agent-1")
        other = self._sid()
        _run_mode("course", COURSE_A, sid)
        _run_mode("course", COURSE_A, sid, agent_id="agent-1")
        _run_mode("course", COURSE_A, other)
        _run_reset(sid)
        self.assertFalse(_state_file(sid).exists())
        self.assertTrue(_state_file(sid, "agent-1").is_file())
        self.assertTrue(_state_file(other).is_file())
        self.assertEqual(_run_mode("course", COURSE_A, other)[0], "")

    def test_reset_without_usable_session_id_does_nothing(self):
        sid = self._sid()
        _run_mode("course", COURSE_A, sid)
        for bad in (None, "", "   ", 123, ["x"]):
            out, err, rc = _run_reset(bad)
            self.assertEqual((out, err, rc), ("", "", 0), repr(bad))
        self.assertTrue(_state_file(sid).is_file())

    def test_reset_with_no_state_yet_is_silent(self):
        out, err, rc = _run_reset(self._sid())
        self.assertEqual((out, err, rc), ("", "", 0))

    def test_reset_prunes_only_stale_state_files(self):
        sid = self._sid()
        stale, fresh = self._sid(), self._sid()
        for s in (stale, fresh):
            _run_mode("course", COURSE_A, s)
        old = time.time() - 8 * 24 * 3600
        os.utime(str(_state_file(stale)), (old, old))
        keep = STATE_DIR / ("keep-" + uuid.uuid4().hex + ".txt")
        keep.write_text("x", encoding="utf-8")
        os.utime(str(keep), (old, old))
        self.paths.append(keep)
        _run_reset(sid)
        self.assertFalse(_state_file(stale).exists(), "7일 넘게 안 쓰인 상태 파일은 치운다")
        self.assertTrue(_state_file(fresh).is_file())
        self.assertTrue(keep.is_file(), ".json이 아닌 파일은 건드리지 않는다")

    def test_reset_hook_is_wired_for_compaction_only(self):
        settings = json.loads((REPO_ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
        entries = settings["hooks"]["SessionStart"]
        self.assertEqual([e["matcher"] for e in entries], ["compact"])
        commands = [h["command"] for e in entries for h in e["hooks"]]
        self.assertEqual(len(commands), 1)
        self.assertIn("--mode reset-state", commands[0])


if __name__ == "__main__":
    unittest.main()
