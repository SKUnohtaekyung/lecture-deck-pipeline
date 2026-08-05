#!/usr/bin/env python3
"""Codex/Claude Skill 어댑터와 공통 자원의 정합성을 정적으로 검증한다."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

# T4: 팀 워크플로 스킬 3종(리서치·검토·하네스)의 정본/어댑터 정합 검사용 데이터.
# body_markers는 "이 게이트가 정본 본문에 실제로 문서화됐다"는 증거로 쓰는 문자열이며,
# 동시에 어댑터 본문에는 있으면 안 되는 규칙 복제 방지 마커이기도 하다.
#
# 「콘텐츠」는 2026-08-03에 폐기했다(실행 이력 0 · 집필은 create-slides가 ⓐ/ⓑ로 흡수).
# 폐기 전에 그 파일에만 있던 정본을 전부 옮겼다 — R-PLAN-01/02·R-COMP-01 →
# references/phases/02, R-ANNEX-01·R-ACC-01/02·R-CAL-01·R-DENS-01/02 → phases/04,
# R-EMPH-02 → kit/guide/디자인시스템.md, R-JUDGE-01·집필노트 규격 → 루트 SKILL.md.
# ⚠️ 사람이 초안을 써서 넘기는 ⓐ 경로와 그 스키마(입력양식/콘텐츠초안템플릿.md ·
# references/콘텐츠초안-입력형식.md)는 살아 있다 — 그 파일들을 지우지 마라.
TEAM_SKILLS = {
    "리서치": {"body_markers": ("5개월", "출처 URL", "확인 날짜", "deep-research", "조사 범위")},
    "검토": {"body_markers": ("읽기 전용", "FAIL", "WARN", "검토보고")},
    "하네스": {"body_markers": ("55.2M", "게이트 기준 6종", "allowlist", "단일 라이터", "안티패턴")},
}


class Check:
    def __init__(self) -> None:
        self.failed = 0

    def __call__(self, ok: bool, success: str, failure: str) -> None:
        if ok:
            print(f"PASS | {success}")
        else:
            self.failed += 1
            print(f"FAIL | {failure}")


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def frontmatter(path: Path) -> tuple[str, str]:
    source = text(path)
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", source, re.S)
    if not match:
        return "", ""
    header = match.group(1)
    name_match = re.search(r"(?m)^name:\s*[\"']?([^\"'\n]+)", header)
    desc_match = re.search(r"(?ms)^description:\s*(.*)$", header)
    name = name_match.group(1).strip() if name_match else ""
    description = " ".join(desc_match.group(1).split()) if desc_match else ""
    return name, description


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def comparable_files(base: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in base.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(base).as_posix()
        if rel == "SKILL.md" or rel == "agents/openai.yaml":
            continue
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        if rel == "scripts/search.py":
            source = text(path).replace("agent consumption", "platform consumption")
            source = source.replace("Claude consumption", "platform consumption")
            result[rel] = hashlib.sha256(source.encode("utf-8")).hexdigest()
        else:
            result[rel] = digest(path)
    return result


def contains_all(source: str, needles: tuple[str, ...]) -> bool:
    """Return True when every contract marker is present in *source*."""
    return all(needle in source for needle in needles)


def markdown_files(base: Path) -> list[Path]:
    if not base.is_dir():
        return []
    return [path for path in base.rglob("*.md") if path.is_file()]


def body_only(path: Path) -> str:
    """Return *path*'s text with a leading YAML frontmatter block stripped.

    Mirrors the frontmatter() regex so body-marker checks never accidentally
    match against the name/description fields instead of real content.
    """
    source = text(path)
    match = re.match(r"^---\s*\n.*?\n---\s*\n", source, re.S)
    return source[match.end():] if match else source


def verify_team_skills(check: Check) -> None:
    """T4: 팀 워크플로 스킬 3종(리서치·검토·하네스)의 정본/어댑터 정합 검사.

    T1~T3가 병행 작업 중이므로 실행 시점에 일부 파일이 없어 FAIL이 나는 것은
    정상이다 — 통합 단계에서 리더가 최종 PASS를 확인한다.
    """
    for name, spec in TEAM_SKILLS.items():
        body_markers = spec["body_markers"]

        canonical = ROOT / "skills" / name / "SKILL.md"
        canonical_ok = canonical.is_file()
        canonical_name, canonical_desc = frontmatter(canonical) if canonical_ok else ("", "")
        check(
            canonical_ok and canonical_name == name and bool(canonical_desc),
            f"[{name}] 정본 skills/{name}/SKILL.md 존재 + frontmatter name/description 유효",
            f"[{name}] 정본 skills/{name}/SKILL.md 없음 또는 frontmatter name/description 오류",
        )
        check(
            "명시 호출" in canonical_desc,
            f"[{name}] description에 '명시 호출' 마커 존재",
            f"[{name}] description에 '명시 호출' 마커 없음",
        )
        canonical_body = body_only(canonical) if canonical_ok else ""
        check(
            canonical_ok and contains_all(canonical_body, body_markers),
            f"[{name}] 정본 본문에 필수 게이트 마커 모두 존재",
            f"[{name}] 정본 본문에 필수 게이트 마커 누락(정본 없음 포함): {body_markers}",
        )

        team_adapters = (
            ("Claude Code", ROOT / ".claude" / "skills" / name / "SKILL.md"),
            ("Codex", ROOT / ".agents" / "skills" / name / "SKILL.md"),
        )
        for platform, adapter in team_adapters:
            check(
                adapter.is_file(),
                f"[{name}] {platform} 어댑터 존재",
                f"[{name}] {platform} 어댑터 없음: {adapter}",
            )
            if not adapter.is_file():
                continue
            adapter_name, adapter_desc = frontmatter(adapter)
            check(
                (adapter_name, adapter_desc) == (canonical_name, canonical_desc),
                f"[{name}] {platform} metadata(name/description)가 정본과 문자열 동일",
                f"[{name}] {platform} metadata가 정본과 불일치",
            )
            adapter_body = body_only(adapter)
            expected_ref = f"../../../skills/{name}/SKILL.md"
            check(
                expected_ref in adapter_body,
                f"[{name}] {platform} 어댑터가 정본을 참조",
                f"[{name}] {platform} 어댑터에 {expected_ref} 참조 없음",
            )
            leaked = [marker for marker in body_markers if marker in adapter_body]
            check(
                not leaked,
                f"[{name}] {platform} 어댑터 본문에 규칙 복제 없음",
                f"[{name}] {platform} 어댑터 본문에 정본 마커 복제됨: {leaked}",
            )

        openai_yaml = ROOT / ".agents" / "skills" / name / "agents" / "openai.yaml"
        yaml_source = text(openai_yaml) if openai_yaml.is_file() else ""
        check(
            openai_yaml.is_file()
            and "display_name" in yaml_source
            and "short_description" in yaml_source
            and f"${name}" in yaml_source,
            f"[{name}] Codex agents/openai.yaml 유효 필드 존재",
            f"[{name}] Codex agents/openai.yaml 또는 필수 필드(display_name/short_description/${name}) 누락",
        )

    evals_path = ROOT / "evals" / "team-skills-eval.json"
    allowed_targets = {"리서치", "콘텐츠", "검토", "create-slides", None}
    evals_ok = False
    if evals_path.is_file():
        try:
            payload = json.loads(text(evals_path))
        except json.JSONDecodeError:
            payload = None
        routing = payload.get("routing") if isinstance(payload, dict) else None
        if isinstance(routing, list):
            evals_ok = all(
                isinstance(case, dict) and case.get("expected_skill", "__missing__") in allowed_targets
                for case in routing
            )
    check(
        evals_ok,
        "evals/team-skills-eval.json 존재 + JSON 파싱 성공 + routing expected_skill 값 모두 유효",
        "evals/team-skills-eval.json 없음, JSON 파싱 실패, 또는 routing expected_skill 값이 허용 집합 밖",
    )

    readme_path = ROOT / "skills" / "README.md"
    readme_source = text(readme_path) if readme_path.is_file() else ""
    missing_names = [name for name in TEAM_SKILLS if name not in readme_source]
    check(
        readme_path.is_file() and not missing_names,
        f"skills/README.md가 팀 스킬 {len(TEAM_SKILLS)}종 이름을 모두 등재",
        f"skills/README.md 등재 누락(파일 없음 포함): {missing_names}",
    )


def main() -> int:
    check = Check()
    canonical = ROOT / "SKILL.md"
    check(canonical.is_file(), "공통 SKILL.md 존재", "루트 SKILL.md 없음")
    canonical_name, canonical_desc = frontmatter(canonical)
    check(
        canonical_name == "create-slides" and bool(canonical_desc),
        "공통 frontmatter name/description 유효",
        "공통 frontmatter name/description 오류",
    )

    adapters = {
        "Codex": ROOT / ".agents/skills/create-slides/SKILL.md",
        "Claude Code": ROOT / ".claude/skills/create-slides/SKILL.md",
    }
    for platform, adapter in adapters.items():
        check(adapter.is_file(), f"{platform} 어댑터 존재", f"{platform} 어댑터 없음: {adapter}")
        if not adapter.is_file():
            continue
        name, description = frontmatter(adapter)
        check(
            (name, description) == (canonical_name, canonical_desc),
            f"{platform} metadata가 공통 정본과 일치",
            f"{platform} metadata가 루트 SKILL.md와 불일치",
        )
        body = text(adapter)
        canonical_ref = (adapter.parent / "../../../SKILL.md").resolve()
        check(
            "../../../SKILL.md" in body and canonical_ref == canonical.resolve(),
            f"{platform} 어댑터가 공통 정본을 참조",
            f"{platform} 어댑터의 ../../../SKILL.md 참조가 루트 정본으로 연결되지 않음",
        )
        check(
            "[STYLE CONTRACT: VIBECODING PAPER-CUT v1]" not in body
            and "#F4F8FB" not in body
            and "SUBJECT: [slide-specific subject or metaphor]" not in body,
            f"{platform} 어댑터가 공통 이미지 프롬프트를 복제하지 않음",
            f"{platform} 어댑터에 공통 이미지 프롬프트가 중복됨",
        )

    openai_yaml = ROOT / ".agents/skills/create-slides/agents/openai.yaml"
    yaml_text = text(openai_yaml) if openai_yaml.is_file() else ""
    check(
        openai_yaml.is_file()
        and 'display_name: "' in yaml_text
        and 'short_description: "' in yaml_text
        and "$create-slides" in yaml_text,
        "Codex agents/openai.yaml 유효 필드 존재",
        "Codex agents/openai.yaml 또는 필수 UI metadata 누락",
    )

    required = [
        "references/콘텐츠초안-입력형식.md",
        "references/조립-리듬-불변요소.md",
        "references/이미지-스크린샷-배포.md",
        "references/이미지-디렉션-프롬프트.md",
        "kit/guide/정보모양-taxonomy.md",
        "kit/guide/디자인시스템.md",
        "kit/guide/토큰-치트시트.md",
        "kit/layouts/by-shape.md",
        "kit/charts/by-shape.md",
        "kit/layouts/catalog.html",
        "kit/charts/catalog.html",
        "kit/starter/deck-template.html",
        "kit/starter/presenter-notes-template.html",
        "kit/runtime/presenter-runtime.js",
        "kit/runtime/presenter-ui.css",
        "입력양식/콘텐츠초안템플릿.md",
        "데모_제작규칙.html",
        "scripts/verify_deck.py",
        "scripts/inline_deck.py",
        "scripts/verify_kit.py",
    ]
    missing = [rel for rel in required if not (ROOT / rel).is_file()]
    check(not missing, "공통 read-path 파일 모두 존재", f"공통 read-path 누락: {missing}")

    image_direction = ROOT / "references/이미지-디렉션-프롬프트.md"
    designboard = ROOT / "kit/images/paper-cut-v1/designboard.png"
    image_source = text(image_direction) if image_direction.is_file() else ""
    canonical_source = text(canonical) if canonical.is_file() else ""

    check(
        image_direction.is_file(),
        "이미지 디렉션·프롬프트 정본 존재",
        "references/이미지-디렉션-프롬프트.md 누락",
    )
    check(
        designboard.is_file() and designboard.stat().st_size > 0,
        "paper-cut-v1 디자인보드 존재",
        "kit/images/paper-cut-v1/designboard.png 누락 또는 빈 파일",
    )
    check(
        contains_all(
            canonical_source,
            (
                "references/이미지-디렉션-프롬프트.md",
                "IMAGE_MODE",
                "generate_now",
                "prompt_only",
            ),
        ),
        "루트 SKILL이 이미지 정본과 IMAGE_MODE 두 분기를 참조",
        "루트 SKILL에 이미지 정본/IMAGE_MODE/generate_now/prompt_only 계약 누락",
    )

    prompt_markers = (
        "[STYLE CONTRACT: VIBECODING PAPER-CUT v1]",
        "LEARNING_POINT:",
        "SOURCE_METAPHOR:",
        "METAPHOR_MAPPING:",
        "MUST_SHOW:",
        "MUST_NOT_IMPLY:",
        "ALT_TEXT:",
        "ROLE:",
        "COMPOSITION:",
        "TEXT_SAFE_SIDE:",
        "#F4F8FB",
        "#F3F5F8",
        "#1D4ED8",
        "#EEF3FE",
        "#14B8A6",
        "#0F766E",
        "#F97360",
        "#141821",
        "NO_IMAGE",
        "IMAGE_EXPLANATORY",
        "IMAGE_MNEMONIC",
        "IMAGE_DECORATIVE_OPTIONAL",
        "cover-object",
        "hero",
        "support",
        "spot",
        "section-overlay",
        "genuine alpha",
        "네 모서리가 투명",
        "IMAGE_MODE = generate_now | prompt_only",
        "새로 생성하거나 변형할 이미지는 N장입니다. 어떤 방식으로 진행할까요?",
    )
    check(
        contains_all(image_source, prompt_markers),
        "이미지 정본에 공통 프롬프트·색·역할·알파 QA·모드 질문 계약 존재",
        "이미지 정본의 공통 프롬프트 핵심 계약이 불완전함",
    )
    mode_output_markers = (
        "[OUTPUT CONTRACT: BUILT-IN CHROMA SOURCE]",
        "perfectly uniform solid magenta #FF00FF",
        "[OUTPUT CONTRACT: APPROVED NATIVE ALPHA]",
        "sessions/N주차/자료/images/",
        "sessions/N주차/자료/이미지-에셋.json",
        "이미지-프롬프트.md",
        'data-image-state="expected"',
        "의미·스타일 교정은 1회",
        "알파 문제는 후처리 1회",
        "중단하고 보고",
        "`rejected` 사유를 기록하고 생략",
    )
    check(
        contains_all(image_source, mode_output_markers),
        "이미지 정본에 generate_now·prompt_only 산출 및 중단 계약 존재",
        "이미지 정본의 모드별 도구·저장·중단 계약이 불완전함",
    )

    archive = ROOT / "_dev/설계기록/탐색-아카이브/slide-image-director-premerge"
    active_director = ROOT / "slide-image-director"
    check(
        not archive.exists(),
        "흡수 완료된 slide-image-director 개발 아카이브 제거됨",
        "흡수 완료 후에도 slide-image-director 개발 아카이브가 남아 있음",
    )
    check(
        not active_director.exists(),
        "독립 slide-image-director 활성 폴더 제거됨",
        "루트 slide-image-director 활성 폴더가 남아 있음",
    )

    exclusion_patterns = (
        re.compile(r"likelion.{0,40}(배제|제외|금지|참조하지|상속하지)", re.I | re.S),
        re.compile(r"(배제|제외|금지|참조하지|상속하지).{0,40}likelion", re.I | re.S),
    )
    director_docs = [image_direction] if image_direction.is_file() else []
    if active_director.is_dir():
        director_docs.extend(markdown_files(active_director))
    exclusion_hits = [
        path.relative_to(ROOT).as_posix()
        for path in director_docs
        if any(pattern.search(text(path)) for pattern in exclusion_patterns)
    ]
    check(
        not exclusion_hits,
        "활성 이미지 디렉터 문서에 likelion 배제 규칙 없음",
        f"likelion 배제 규칙 잔존: {exclusion_hits}",
    )

    image_policy_files = [
        canonical,
        ROOT / "references/이미지-스크린샷-배포.md",
        image_direction,
        ROOT / "kit/starter/deck-template.html",
        ROOT / "kit/starter/presenter-notes-template.html",
    ]
    obsolete_policies = ("선택 3D 이미지",)
    obsolete_hits = [
        path.relative_to(ROOT).as_posix()
        for path in image_policy_files
        if path.is_file() and any(policy in text(path) for policy in obsolete_policies)
    ]
    check(
        not obsolete_hits,
        "이미지 관련 정본에 오래된 비생성·3D 정책 없음",
        f"오래된 이미지 정책 잔존: {obsolete_hits}",
    )

    claude_md = text(ROOT / "CLAUDE.md") if (ROOT / "CLAUDE.md").is_file() else ""
    check("@AGENTS.md" in claude_md, "Claude가 AGENTS.md 공통 지침을 import", "CLAUDE.md의 @AGENTS.md import 누락")
    # 메모리 정본은 .agents 하나이며, .claude 쪽은 그것을 가리키는 포인터 파일이다.
    # 사본을 두면 반드시 분기하므로 바이트 동일성 대신 포인터 규약을 검사한다.
    codex_memory = ROOT / ".agents/agent-memory/create-slides/MEMORY.md"
    claude_memory = ROOT / ".claude/agent-memory/create-slides/MEMORY.md"
    pointer_text = text(claude_memory) if claude_memory.is_file() else ""
    check(
        codex_memory.is_file()
        and claude_memory.is_file()
        and ".agents/agent-memory/" in pointer_text
        and len(claude_memory.read_bytes()) < 400
        and not re.search(r"(?m)^## ", pointer_text),
        "메모리 포인터 규약(정본 .agents · .claude는 포인터)",
        "메모리 포인터 규약 위반: 정본·포인터 파일 존재, 포인터가 .agents/agent-memory/ 지목,"
        " 400바이트 미만, '## ' 헤더 0건을 모두 만족해야 한다",
    )

    # git 훅 층 — Codex·Claude와 무관하게 커밋 시점에 도는 유일한 공통 강제 층이다.
    # 훅이 미설치면 pre-commit 자체가 실행되지 않으므로 **스스로 미설치를 알릴 수 없다.**
    # 그래서 설치 여부를 여기서(수동 실행되는 검증기에서) 검사한다.
    # 2026-08-05 독립 검토 지적: 이 검사가 없어 「공통 최종 증거 층」이 조용히
    # 무력화될 수 있었고, 문서는 이미 검사한다고 적고 있었다(선언과 집행 불일치).
    hooks_dir = ROOT / ".githooks"
    pre_commit = hooks_dir / "pre-commit"
    try:
        configured = subprocess.run(
            ["git", "config", "--get", "core.hooksPath"],
            cwd=str(ROOT), capture_output=True, text=True,
        ).stdout.strip().replace("\\", "/").rstrip("/")
    except Exception:
        configured = ""
    check(
        pre_commit.is_file(),
        "git 훅 스크립트 존재(.githooks/pre-commit)",
        ".githooks/pre-commit 없음 — 플랫폼 공통 강제 층이 비어 있다",
    )
    check(
        configured == ".githooks",
        "git 훅 설치됨(core.hooksPath=.githooks)",
        "core.hooksPath가 '.githooks'가 아니다(현재: %r). "
        "`python scripts/install_hooks.py`로 설치하라 — 클론마다 한 번 필요하다"
        % (configured or "미설정",),
    )

    for platform_dir, prefix in (
        (".agents", "python .agents/skills/ui-ux-pro-max/scripts/search.py"),
        (".claude", "python .claude/skills/ui-ux-pro-max/scripts/search.py"),
    ):
        skill = ROOT / platform_dir / "skills/ui-ux-pro-max/SKILL.md"
        source = text(skill) if skill.is_file() else ""
        check(
            skill.is_file()
            and prefix in source
            and "python3 skills/ui-ux-pro-max/scripts/search.py" not in source,
            f"{platform_dir} ui-ux-pro-max Windows 명령 경로 일치",
            f"{platform_dir} ui-ux-pro-max에 잘못된 Python/상대 경로가 남음",
        )
        check(
            "design-system/<project-slug>/MASTER.md" in source
            and "design-system/<project-slug>/pages/" in source,
            f"{platform_dir} ui-ux-pro-max persist 문서가 구현 경로와 일치",
            f"{platform_dir} ui-ux-pro-max persist 출력 경로 문서 불일치",
        )

    codex_ui = ROOT / ".agents/skills/ui-ux-pro-max"
    claude_ui = ROOT / ".claude/skills/ui-ux-pro-max"
    check(
        comparable_files(codex_ui) == comparable_files(claude_ui),
        "ui-ux-pro-max 실행 스크립트·데이터 양 플랫폼 동기화",
        "ui-ux-pro-max 실행 스크립트 또는 데이터가 플랫폼 간 드리프트",
    )

    verify_team_skills(check)

    if check.failed:
        print(f"RESULT | FAIL | {check.failed}개 실패")
        return 1
    print("RESULT | PASS | Codex·Claude Skill 설정 정합")
    return 0


if __name__ == "__main__":
    sys.exit(main())
