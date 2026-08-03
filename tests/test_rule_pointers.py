# -*- coding: utf-8 -*-
"""규칙 문서가 **실재하지 않는 것을 지목하지 않는지** 검사한다.

왜 이 파일이 필요한가
--------------------
이 저장소가 반복해서 겪은 실패다:
  · `kit/guide/토큰-치트시트.md` R-TYPE-01이 `.proc-analogy`·`.wk-title` 등
    **kit에 정의가 없는 셀렉터 5종**을 지목하고 있었다(2026-08-03 정정).
  · `kit/guide/카탈로그-규격.md`가 "구도 분포 측정"을 용도로 선언했으나 그
    측정을 하는 스크립트가 **0건**이었다(2026-08-03 정정).
  · 그리고 그 정정을 하던 세션이 **같은 실수를 새 규칙에서 반복**했다 —
    `references/phases/03-레이아웃선택.md`의 R-BOX-01 매핑표가 정보 모양으로
    `procedure`를 썼는데, 정준 12종에 그런 이름은 없다.

세 번째 사례가 결정적이다. 사람이 주의해서 막을 수 있는 문제가 아니다.
「규칙이 있는 것처럼 보이는데 아무 데도 걸리지 않는」 상태를 기계로 막는다.

실행: python -m unittest tests.test_rule_pointers
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TAXONOMY = REPO_ROOT / "kit" / "guide" / "정보모양-taxonomy.md"
CHARTS_BY_SHAPE = REPO_ROOT / "kit" / "charts" / "by-shape.md"
PHASES = REPO_ROOT / "references" / "phases"


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def canonical_shapes() -> set[str]:
    """정보모양-taxonomy.md의 「12 정준 정보 모양」 표에서 id 열을 읽는다."""
    text = _read(TAXONOMY)
    body = text.split("## 12 정준 정보 모양", 1)[1].split("\n---", 1)[0]
    ids = set()
    for line in body.splitlines():
        m = re.match(r"\|\s*`([a-z][a-z-]*)`\s*\|", line.strip())
        if m:
            ids.add(m.group(1))
    return ids


def catalog_element_ids() -> set[str]:
    """kit/charts/by-shape.md의 element 목록에서 `C-*`·`D-*`·`E-*` id를 읽는다."""
    return set(re.findall(r"`([CDE]-[a-z0-9-]+)`", _read(CHARTS_BY_SHAPE)))


class TaxonomyPointerTests(unittest.TestCase):
    def test_taxonomy_has_twelve_shapes(self):
        shapes = canonical_shapes()
        self.assertEqual(len(shapes), 12,
                         f"정준 정보 모양은 12종이어야 한다 — 읽은 값: {sorted(shapes)}")

    def test_phase_docs_only_name_canonical_shapes(self):
        """단계 문서가 백틱으로 감싼 정보 모양 이름은 12종 안에 있어야 한다.

        ⚠️ 검사 대상을 «백틱 + 정보 모양 표에 실제로 있는 이름과 같은 형태»로
        좁힌다. 아무 단어나 잡으면 오탐이 폭발해 아무도 안 보게 된다.
        여기서는 **정보 모양처럼 생겼는데 정준이 아닌 것**만 잡는다.
        """
        canon = canonical_shapes()
        # 정보 모양 자리에서만 쓰이는 표현 — 이 목록에 없으면 오탐 위험이 커진다
        shape_like = {
            "procedure", "process", "sequence", "hierarchy", "relation",
            "definition", "example", "summary", "list", "table", "quote",
        }
        offenders = []
        for path in sorted(PHASES.glob("*.md")):
            text = _read(path)
            for lineno, line in enumerate(text.splitlines(), 1):
                for token in re.findall(r"`([a-z][a-z-]{3,})`", line):
                    if token in canon:
                        continue
                    if token in shape_like:
                        offenders.append(f"{path.name}:{lineno} `{token}`")
        self.assertEqual(offenders, [],
                         "정준 12종에 없는 정보 모양 이름을 지목한다 — "
                         "kit/guide/정보모양-taxonomy.md 참고:\n  " + "\n  ".join(offenders))

    def test_named_elements_exist_in_catalog(self):
        """단계 문서가 지목하는 `C-*`·`D-*`·`E-*` element가 카탈로그에 실재해야 한다."""
        known = catalog_element_ids()
        self.assertIn("C-column", known, "카탈로그 파싱이 깨졌다")
        offenders = []
        for path in sorted(PHASES.glob("*.md")):
            for lineno, line in enumerate(_read(path).splitlines(), 1):
                for token in re.findall(r"`([CDE]-[a-z0-9-]+)`", line):
                    if token not in known:
                        offenders.append(f"{path.name}:{lineno} `{token}`")
        self.assertEqual(offenders, [],
                         "kit/charts/by-shape.md에 없는 element를 지목한다:\n  "
                         + "\n  ".join(offenders))

    def test_every_catalog_element_is_reachable_from_the_mapping_table(self):
        """킷에 있는데 표가 **한 번도 안 가리키는** element가 없어야 한다.

        가리켜지지 않은 element는 제작자가 **영영 못 보는 선택지**가 된다 —
        「없는 것을 지목한다」의 반대 방향 결함이고, 「시각 요소를 우선하라」는
        규칙을 조용히 무력화한다(쓸 수 있는 시각물을 모르면 박스로 간다).
        """
        known = catalog_element_ids()
        text = _read(PHASES / "03-레이아웃선택.md")
        table = text.split("### 2단계", 1)[1].split("### 3단계", 1)[0]
        named = set(re.findall(r"`([CDE]-[a-z0-9-]+)`", table))
        orphans = sorted(known - named)
        self.assertEqual(orphans, [],
                         "킷에 있는데 R-BOX-01 표가 가리키지 않는 element "
                         f"({len(orphans)}/{len(known)}):\n  " + "\n  ".join(orphans))

    def test_box_mapping_table_rows_are_all_canonical(self):
        """R-BOX-01 매핑표의 **모든 행**이 정준 모양을 지목해야 한다.

        ⚠️ 위 `test_phase_docs_only_name_canonical_shapes`만으로는 부족하다 —
        실제 결함(`procedure`)은 백틱 없이 `procedure(실습 절차)`로 쓰여 있어
        그 검사를 빠져나갔다. 표의 첫 칸을 직접 본다.
        """
        canon = canonical_shapes()
        text = _read(PHASES / "03-레이아웃선택.md")
        table = text.split("### 2단계", 1)[1].split("### 3단계", 1)[0]
        offenders = []
        for line in table.splitlines():
            line = line.strip()
            if not line.startswith("|") or line.startswith("|---"):
                continue
            first = line.split("|")[1].strip()
            if not first or "정보 모양" in first:      # 헤더 행
                continue
            m = re.match(r"`([a-z][a-z-]*)`", first)
            if not m or m.group(1) not in canon:
                offenders.append(first[:40])
        self.assertEqual(offenders, [],
                         "매핑표 첫 칸이 정준 정보 모양(백틱 표기)이 아니다:\n  "
                         + "\n  ".join(offenders))

    def test_box_mapping_table_covers_every_shape(self):
        """R-BOX-01 매핑표가 12종을 **전부** 다뤄야 한다.

        빠진 모양이 있으면 그 모양을 만난 제작자는 「박스가 맞는가」를 물을
        근거를 못 얻는다 — 규칙이 조용히 적용되지 않는 구멍이 된다.
        """
        text = _read(PHASES / "03-레이아웃선택.md")
        table = text.split("### 2단계", 1)[1].split("### 3단계", 1)[0]
        missing = sorted(s for s in canonical_shapes() if f"`{s}`" not in table)
        self.assertEqual(missing, [],
                         f"R-BOX-01 매핑표에 빠진 정보 모양: {missing}")


if __name__ == "__main__":
    unittest.main()
