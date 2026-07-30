#!/usr/bin/env python3
"""verify_deck_quality.py — 완성 덱 내용 품질 게이트(R-QC-01~11, 의존성 0).

사용: python scripts/verify_deck_quality.py <deck.html> [--baseline <deck.html>] [--json <out>] [--strict]

배경(2026-07-26 근본원인 감사, `reports/create-slides-quality/`): `scripts/verify_deck.py`의
~90개 검사는 구조·경로·문법·색·접근성만 재고 "완성된 슬라이드의 내용 품질"을 재는 검사가 0개였다
(`validation_gap_report.md` §A.1). 2주차 저밀도 결함(설명 슬라이드 본문 글자수 중앙값 70자 —
1주차 최종본 156자의 45%)이 모든 기존 게이트를 exit 0으로 통과한 근본 이유다. 이 스크립트는
그 공백을 메운다 — **회귀가 아니라 신규 계약**이므로 기존 `verify_deck.py`의 FAIL 0 게이트는
건드리지 않는다(별도 스크립트로 분리, `validation_gap_report.md` §F 권고).

**임계값은 전부 W1_FINAL(1주차 최종본, 2026-07-26 사용자 동결 당시 유일한 "완성" 기준선) 분포에서
도출했다** — 발명하지 않는다. 도출 방법: `reports/create-slides-quality/deck_quality_metrics.json`의
`per_slide.W1_FINAL`/`per_slide.W2_CURRENT`에서 슬라이드 타입별 지표를 뽑아, "W1_FINAL 슬라이드의
≤15%만 플래그되고 W2_CURRENT 슬라이드의 ≥55%가 플래그되는 백분위"를 탐색했다(스크래치패드
`analyze_metrics_thresholds.py`, 이 파일 하단 THRESH_DERIVATION 상수에 그 결과를 그대로 기록).
일부 지표(컨테이너 희소성이 강한 R-QC-03·비율형 R-QC-05/08)는 이 이중 목표를 동시에 만족하는
값이 존재하지 않았다 — 발명 대신 **실제로 도출된 값과 그 값이 두 목표 중 무엇을 못 채우는지를
그대로 보고**한다(발명 금지 원칙이 목표 강제보다 우선).

분류(슬라이드 type)는 `reports/create-slides-quality/deck_quality_analysis.md` §2의 12분류
우선순위 규칙을 그대로 옮긴다 — 형태소(하이픈 분해) **정확 일치**만 쓴다(부분문자열 매칭 금지).
그 문서가 스팟체크 도중 발견해 수정한 버그 2건을 여기서도 그대로 반영한다:
  버그1: `is-recovery`가 부분문자열 "cover" 때문에 표지로 오분류됨 → 형태소 정확 일치로 해결.
  버그2: `index-entry-slide`가 범용 "index" 키워드에 걸려 구간전환으로 오분류됨 → 그 키워드를
         아예 쓰지 않음(코퍼스 전체에서 이 키워드가 맞은 사례가 이 1건뿐이고 그마저 오분류였다).

심각도: 전부 기본 **WARN**(exit 0 — 신규 게이트가 기존 파이프라인을 막지 않는다). `--strict`를 주면
WARN이 FAIL로 승격되고 종료코드가 1이 된다. R-QC-04(카드 면적 대비 콘텐츠)·R-QC-07(설명 단위
과잉 분할)·R-QC-10(초안→덱 보존율)은 **자동화하지 않는다** — 렌더 치수나 의미 경계 판단이
필요해 문자열 정적 분석으로는 신뢰할 수 없다(오탐 위험 "매우 높음", `validation_gap_report.md` §E).
R-QC-05(동일 layout family 반복률)도 2026-07-27 독립 리뷰에서 **강등됐다** — shipped
`family_signature()`로 실측하면 W1(동결·모범 기준선)이 W2보다 오히려 더 높게 나와(0.181 vs
0.047) 판정 방향이 뒤집힌다. 방향이 안 맞는 게이트는 출하하지 않는다(아래 THRESH_QC05 주석 참고).
R-QC-09(실습 슬라이드 완결성)도 같은 날 **강등됐다** — 두 덱 모두 100% 플래그(W1 5/5·W2 10/10)로
판별력이 0이었다(원인: 완료기준 정규식 결함 + 실습 유형 분류 오차, 아래 코드 주석 참고).
이 다섯은 전부 "사람검토" 안내 줄로만 출력하고 PASS/WARN/FAIL 판정을 내지 않는다.

이 스크립트가 못 하는 것: 브라우저 렌더(카드 실면적·overflow)는 `verify_deck.py`의 안내문과 동일하게
브라우저 실측이 필요하다. 이 스크립트는 정적 텍스트/구조 분석만 한다.
"""
import sys, re, os, argparse, json
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from .verify_deck import (
        parse_document, classes, decoded_text, _slide_elements,
        _strip_hidden_spans, family_signature, count_code_viz, _attr,
    )
except ImportError:
    from verify_deck import (
        parse_document, classes, decoded_text, _slide_elements,
        _strip_hidden_spans, family_signature, count_code_viz, _attr,
    )

# ============================================================================
# 임계값 도출 기록(THRESH_DERIVATION) — 발명 금지, 전부 deck_quality_metrics.json에서 계산.
#   n·flag% 계산 대상: 개념설명(explanation)으로 분류된 슬라이드만(표지·전환·질문 슬라이드는
#   원래 짧아야 하므로 밀도로 판단하지 않는다 — deck_quality_analysis.md §6).
#   W1_FINAL: n=43개 설명 슬라이드(전체 75장) · W2_CURRENT: n=37개 설명 슬라이드(전체 108장).
# ============================================================================
THRESH_QC01_CHARS = 76          # W1_FINAL p10(75.6)을 올림. flag: W1 11.6%(5/43) · W2 62.2%(23/37) — 목표(≤15%/≥55%) 충족
THRESH_QC02_BLOCKS = 5          # W1_FINAL p15(text_leaf_count=5.0). flag: W1 11.6%(5/43) · W2 67.6%(25/37) — 목표 충족
# R-QC-03: 근-빈 컨테이너는 "전체 슬라이드 중 소수만 겪는" 희소 결함이라 어떤 값을 잡아도
#   W2 55%에 못 미친다(전수: any-genuine-near-empty 기준 W1 2.7%(2/75) · W2 24.1%(26/108)).
#   ≤15% 목표는 충족하지만 ≥55% 목표는 이 지표의 성격상 달성 불가능 — 발명 대신 그대로 보고한다.
# R-QC-05: 2026-07-27 독립 리뷰가 지적 — 이 저장소의 shipped family_signature()로 두 덱을
#   **직접 재실행**하면 W1=0.181(임계 0.115 기준 WARN) · W2=0.047(PASS)로 **방향이 뒤집힌다**
#   (offline deck_quality_metrics.json은 다른 family 분류기를 썼다 — 그 분류기 기준으로는
#   W1=0.095·W2=0.140이었지만, 그 수치는 이 스크립트가 실제로 쓰는 family_signature()의 결과가
#   아니다). "좋은 덱이 FAIL하고 나쁜 덱이 PASS"하는 방향 역전 게이트는 출하할 수 없다 —
#   임계값을 아무리 재도출해도 W1_live(0.181) > W2_live(0.047)인 이상 "W1 통과·W2 미달"을
#   만드는 임계값 자체가 존재하지 않는다(대소 관계가 이미 반대). **자동 판정을 접고
#   `[사람검토]` 안내로 강등한다** — 판정 없이 실측값만 보고한다.
# R-QC-01: 2026-07-31 실측에서 방향이 역전돼 있음(W1이 오히려 더 많이 flag되는 사례 관측)이
# 확인됐으나, 판정 로직·임계는 변경하지 않고 하한 안전망으로 그대로 둔다 — 손대지 말라는 지시.
THRESH_QC08_VISUAL_RATIO = 0.55      # 2026-07-31 실측 재도출. 1주차 실측 0.500(18/36)·2주차 0.208(11/53).
                                       # 이전 임계 0.35는 1주차 실측보다 낮아 1주차만 못한 덱도 통과시켰다.
                                       # 기록돼 있던 W1 0.465는 낡은 값이다.
THRESH_QC15_FOOT_CALLOUT_RATIO = 0.12  # 1주차 0.083 · 2주차 0.340(2026-07-31 실측). 임계는 1주차 실측에 최소 여유.
THRESH_QC16_BOX_BASED_RATIO = 0.10     # 1주차 0.056 · 2주차 0.226.
# THRESH_QC12_UNDEFINED_TERM_RATIO — 미사용(강등). R-QC-12는 2026-07-31 [사람검토]로
# 강등되어 임계값을 쓰지 않는다(아래 THRESH_DERIVATION 참고).
THRESH_QC17_INCOMPLETE_PRACTICE_RATIO = 0  # 완결성 결함형이라 임계 0. 2주차 0.167(단계 1개짜리 실습 존재).
THRESH_META01_COUNT = 0  # 명백한 결함형 — 내부 작업 라벨이 학생 화면에 남는 것은 절제의 문제가 아니다.
                          # 1주차 0건 · 2주차 3건(2026-07-31 실측).
THRESH_DERIVATION = """\
[임계값 도출 근거 — reports/create-slides-quality/deck_quality_metrics.json 기준, 개념설명 슬라이드만]
  R-QC-01 본문 글자수 < 76자(W1_FINAL p10)          flag률: W1 11.6%(5/43) · W2 62.2%(23/37)      [목표 충족: W1<=15%, W2>=55%]
  R-QC-02 의미 블록 수 < 5개(W1_FINAL p15)           flag률: W1 11.6%(5/43) · W2 67.6%(25/37)      [목표 충족]
  R-QC-03 근-빈 컨테이너 존재(전수, 임계값 없음)      flag률: W1  2.7%(2/75) · W2 24.1%(26/108)     [W1<=15% 충족 · W2>=55%는 지표 성격상 미충족 — 희소 결함이라 그대로 보고]
  R-QC-05 인접 동일family 비율 — [사람검토]로 강등됨(자동 판정 없음, 아래 본문 참고 — 방향 역전 확인됨)
  R-QC-08 설명기능 시각자료 보유 비율 < 0.55(임계, 2026-07-31 재도출) 지표값(높을수록 좋음): 1주차 실측 0.500(18/36) · 2주차 실측 0.208(11/53)
  R-QC-12 — [사람검토]로 강등(2026-07-31). 정의 신호 3종 시도가 7.1%/92.9%/90.5%로
    전부 극단이었고, 첫 등장 탐색의 HTML 주석 오염 버그를 고쳐 71.4%까지 정확해졌으나
    여전히 자동 판정 밴드 밖이라 참고치로만 둔다. 한국어 정의는 표지 없이 성립해 문자열
    판정이 원리적으로 부정확하다. R-QC-05·R-QC-09와 같은 처리.
  R-QC-15 하단 결론 콜아웃 보유율 > 0.12(임계 초과 시 플래그) 1주차 0.083 · 2주차 0.340(2026-07-31 실측)
  R-QC-16 박스 기반 슬라이드 비율 > 0.10(임계)        1주차 0.056 · 2주차 0.226
  R-QC-17 실습 완결성 미달률 > 0(임계)                2주차 0.167(단계 1개짜리 실습 존재)
  R-META-01 메타 표기 잔존 건수 > 0(임계)             1주차 0건 · 2주차 3건(2026-07-31 실측)
"""

CIRCLED = "①②③④⑤⑥⑦⑧⑨⑩"


# ============================================================================
# 슬라이드 타입 분류 — deck_quality_analysis.md §2 우선순위 그대로, 형태소 정확 일치
# ============================================================================

def _morphemes(cls_str):
    out = set()
    for token in (cls_str or "").split():
        out.update(token.split("-"))
        out.add(token)
    return out


_EMPHASIS_TOKENS = {"center-msg", "intro-do", "intro-do-more"}


def classify_slide_type(idx, cls_str, title_text):
    m = _morphemes(cls_str)
    tokens = (cls_str or "").split()
    title = (title_text or "").strip()
    if idx == 0 or "cover" in m:
        return "표지"
    # 감정적 강조(사람 인용구·의지 선언 등) — 2026-07-27 신설. 기존엔 이런 슬라이드가 어떤
    # 유형에도 안 걸려 기본값 개념설명으로 떨어져 밀도로 오판정됐다(예: human-quote-stage가
    # morpheme 'stage' 때문에 프로세스로 먼저 잘못 걸리기도 했다 — 그래서 이 검사를 그보다
    # 먼저 둔다). 밀도(R-QC-01/02)·시각자료(R-QC-08) 판정 모두 대상에서 빠진다(개념설명이 아님).
    if "quote" in m or (_EMPHASIS_TOKENS & set(tokens)):
        return "감정적 강조"
    if "thank" in m or "closing" in m:
        return "요약"
    if {"s02-slide", "s03-slide"} & set(tokens):
        return "구간전환"  # 고정 도입(S02)·아젠다(S03) — 개념설명이 아니라 원래 짧아야 하는 안내 슬라이드
    if m & {"divider", "roadmap", "agenda"}:
        return "구간전환"
    if "practice-intro" in (cls_str or "").split():
        return "실습대기"
    if m & {"annex", "recovery", "pitfalls", "privacy"}:
        return "참고·보조"
    if "compare" in m:
        return "비교"
    if m & {"flow", "cycle", "stage", "lifecycle", "gantt", "proc"}:
        return "프로세스"
    if m & {"practice", "todo", "workspace"}:
        return "실습지시"
    if m & {"result", "report", "showcase", "readiness", "inspection"}:
        return "결과확인"
    if m & {"summary", "recap", "wrap"}:
        return "요약"
    if "w2-slot" in (cls_str or "").split() or re.search(r"[?]\s*$|일까요?\s*$", title):
        return "질문·환기"
    return "개념설명"


# ============================================================================
# 화면 조작 안내 예외(R-DENS-01a) — 2026-07-27 B1: 이 예외는 `data-intentional-minimal`보다
# 먼저 있던 **표준 계약**이다(`skills/콘텐츠/SKILL.md` §0-6 각주, `references/phases/04-조립.md`
# R-DENS-01a, 커리큘럼 기준안 §6 원칙 9 "한 화면에는 한 단계만 보여준다"). 저작자가 손으로
# 표시하는 예외가 아니라 **정보 모양이 screen-operation이면 자동으로** 밀도 하한 대상에서 빠진다.
# 이 덱들에서 실제로 screen-operation을 구현하는 신호는 family_signature()가 이미 인식하는
# 'shot'(주석 스크린샷 `.shot-annot`/`.shot-win`/`data-asset-kind="screenshot"`)·
# 'screenmock'(w2-screen GUI 모형)·'gui'(codex-gui류 실제 앱 화면 모형)뿐이다(카탈로그 정본:
# `kit/screenshots/주석스크린샷.md`·`kit/guide/정보모양-taxonomy.md`). 2026-07-27 재검증:
# 두 덱 모두 이 family로 걸리는 슬라이드(W1 14·15 / W2 C2-3·C4-3·C4-11)는 전부 글자수가 이미
# 임계값 이상이라(개념 설명을 곁들인 캡처 슬라이드라서) 이 예외가 있든 없든 R-QC-01/02 결과는
# 바뀌지 않는다 — 즉 C2-8("입력→실행→결과→변화" 4노드 흐름도, family='flow')은 실제 UI 화면
# 조작이 아니라 **개념적 흐름 다이어그램**이라 이 계약 예외에 해당하지 않는다(§0-6의
# screen-operation은 "실제 UI 화면 단계"만을 가리킨다 — 정보모양-taxonomy.md 정의). 따라서
# `data-intentional-minimal` 수동 마커는 **여전히 필요하다**(C2-8류의 "개념 흐름을 시각자료로
# 대체" 사례는 이 자동 예외가 커버하지 못하는 별개 사유이기 때문).
_SCREEN_OP_FAMILIES = {"shot", "screenmock", "gui"}


# ============================================================================
# 요소 트리 — parse_document()가 주는 평면 elements 리스트에서 부모/자식 관계를 복원한다
# (완전한 DOM은 아니지만 포함관계 스택 방식으로 "같은 부모의 형제"를 신뢰성 있게 판정한다).
# ============================================================================

def _build_parent_map(elements):
    ordered = sorted(elements, key=lambda e: (e.start, -e.end))
    stack = []
    parent = {}
    for el in ordered:
        while stack and stack[-1].end <= el.start:
            stack.pop()
        parent[el] = stack[-1] if stack else None
        stack.append(el)
    return parent


_CONTAINER_CLASS_RE = re.compile(
    r"(?:^|[\s_])(?:[\w]*card[\w]*|[\w]*box[\w]*|[\w]*panel[\w]*|[\w]*-row|[\w]*-col|"
    r"[\w]*-case|[\w]*-step|[\w]*-side|[\w]*-note|[\w]*-item|[\w]*-tile|[\w]*-cell|[\w]*-slot)(?:$|[\s])"
)
# 순수 장식·JS가 채우는 클래스는 애초에 "콘텐츠 컨테이너 후보"에서 뺀다(오탐 방지 —
# root_cause_decision.md: 빈 컨테이너 33개 전수 조사 결과 27개 .accent-bar(순수 CSS 장식)·
# 6개 .pd-dots(JS가 런타임에 채움) — 진짜 결함 0건이었다).
_DECORATIVE_OR_JS_POPULATED_RE = re.compile(r"(?:^|\s)(?:accent-bar|pd-dots)(?:\s|$)")


def _text_len(html_text, start, end):
    frag = html_text[start:end]
    frag = re.sub(r"<(script|style)\b[^>]*>.*?</\1\s*>", "", frag, flags=re.S | re.I)
    frag = re.sub(r"<[^>]+>", "", frag)
    import html as _h
    frag = _h.unescape(frag)
    return len(re.sub(r"\s+", "", frag))


def _has_image_slot(html_text, start, end):
    frag = html_text[start:end]
    if re.search(r"<img\b", frag, re.I):
        return True
    if re.search(r'role\s*=\s*["\']img["\']', frag, re.I):
        return True
    return False


def find_near_empty_containers(html_text, slide_inner_start, slide_inner_end, elements):
    """슬라이드 안에서 '근-빈' 콘텐츠 컨테이너(같은 부모의 동일 클래스 형제 ≥2 & 텍스트 <10자
    & img/svg role=img 없음)를 찾는다. accent-bar·pd-dots(장식·JS주입)는 후보에서 제외."""
    scoped = [e for e in elements if slide_inner_start <= e.start and e.end <= slide_inner_end]
    parent = _build_parent_map(scoped)
    candidates = []
    for el in scoped:
        cls_str = (el.attrs.get("class") or "")
        if not cls_str:
            if el.name != "article":
                continue
        elif el.name != "article" and not _CONTAINER_CLASS_RE.search(cls_str):
            continue
        if _DECORATIVE_OR_JS_POPULATED_RE.search(cls_str):
            continue
        candidates.append(el)
    groups = {}
    for el in candidates:
        key = (id(parent.get(el)), el.attrs.get("class") or "(bare article)")
        groups.setdefault(key, []).append(el)
    hits = []
    for (_pid, cls_key), members in groups.items():
        if len(members) < 2:
            continue
        for el in members:
            if _has_image_slot(html_text, el.inner_start, el.inner_end):
                continue
            if _text_len(html_text, el.inner_start, el.inner_end) < 10:
                hits.append((cls_key, el))
    return hits


def count_explanatory_visuals(html_text, start, end, tags):
    """viz-* 요소 + <canvas> + 장식/로고가 아닌 <img>. verify_deck.py의 count_code_viz()에
    <canvas>·<img>(비-로고)를 더해 '설명 기능 시각자료'로 확장한다."""
    section = html_text[start:end]
    total = count_code_viz(section)
    total += len(re.findall(r"<canvas\b", section, re.I))
    logo_re = re.compile(r"(?:^|\s)(?:s-logo|brand-logo|favicon|cover-logo)(?:\s|$)", re.I)
    for tag in tags:
        if not (start <= tag.start < end):
            continue
        if tag.name != "img":
            continue
        cls_str = tag.attrs.get("class") or ""
        if logo_re.search(cls_str):
            continue
        aria_hidden = (tag.attrs.get("aria-hidden") or "").strip().lower()
        if aria_hidden == "true":
            continue
        total += 1
    return total


_BOX_CLASS_RE = re.compile(r"(?:^|[\s_])(?:[\w-]*card[\w-]*|[\w-]*callout[\w-]*|[\w-]*-band|[\w-]*-box|[\w-]*-node|[\w-]*-col)(?:$|[\s])")
_FOOT_CALLOUT_RE = re.compile(r"(?:^|\s)(?:[\w-]*callout[\w-]*)(?:\s|$)")
_FOOT_RE = re.compile(r"(?:^|\s)(?:[\w-]*-foot)(?:\s|$)")
_NOTE_RE = re.compile(r"(?:^|\s)(?:[\w-]*-note)(?:\s|$)")


def count_box_containers(html_text, start, end, elements):
    """슬라이드 안에서 박스 컨테이너(class에 card|callout|-band|-box|-node|-col 포함) 개수."""
    scoped = [e for e in elements if start <= e.start and e.end <= end]
    count = 0
    for el in scoped:
        cls_str = el.attrs.get("class") or ""
        if _BOX_CLASS_RE.search(cls_str):
            count += 1
    return count


def find_last_content_child(el, parent_map, children_map):
    """슬라이드 본문 컨테이너(.s-full 우선, 없으면 슬라이드 자신)의 마지막 요소 자식을 찾는다."""
    container = None
    for child in children_map.get(id(el), []):
        cls_str = child.attrs.get("class") or ""
        if re.search(r"(?:^|\s)s-full(?:\s|$)", cls_str):
            container = child
            break
    if container is None:
        container = el
    kids = children_map.get(id(container), [])
    if not kids:
        return None
    return sorted(kids, key=lambda e: e.start)[-1]


def has_conclusion_callout(last_child):
    if last_child is None:
        return False
    cls_str = last_child.attrs.get("class") or ""
    name = last_child.name
    if name == "p" and _FOOT_CALLOUT_RE.search(cls_str):
        return True
    if _FOOT_RE.search(cls_str):
        return True
    if name == "p" and _NOTE_RE.search(cls_str):
        return True
    return False


# ============================================================================
# 실습 슬라이드 완결성(R-QC-09) — 행동·입력·완료기준 키워드 존재 여부(구조 기반, 완전 자동화 불가 명시)
# ============================================================================
_ACTION_RE = re.compile(r"만듭니다|입력합니다|작성합니다|클릭|실행합니다|눌러|요청합니다|고릅니다|선택합니다|엽니다|바꿉니다|확인합니다")
_INPUT_RE = re.compile(r"입력|프롬프트|요청문|한\s*줄|폴더|파일명|버튼")
# 2026-07-27 재검증(R-QC-09 재평가): 실제 저작 관행은 "완성:"처럼 콜론을 붙이지 않고
# `<span class="…tag">완성</span>` 라벨 뒤에 곧장 기준 문장을 잇는다(예: 2주차 C1-5).
# 콜론 필수였던 이전 버전은 이 실제 표기를 0건 매치해 R-QC-09가 항상 실패하는 원인 중
# 하나였다 — 콜론을 선택으로 완화한다(그래도 100% 해소되진 않아 아래에서 강등 결정).
_COMPLETION_RE = re.compile(r"완성(?:\s*[:：])?|완료\s*기준|확인\s*[:：]|~하면\s*끝|끝납니다|보이면\s*성공|성공\s*기준")


def practice_completeness(text):
    return {
        "행동": bool(_ACTION_RE.search(text)),
        "입력": bool(_INPUT_RE.search(text)),
        "완료기준": bool(_COMPLETION_RE.search(text)),
    }


_TRUTHY_VALUES = {"true", "1", "yes", "y"}


def _is_truthy_marker(el, attr_name):
    """A2(2026-07-27): 속성 존재만으로 참으로 보지 않는다 — `attr="false"`도 여전히
    존재는 하므로 `attr_name in el.attrs`만 쓰면 false 값도 참으로 오인한다."""
    if attr_name not in el.attrs:
        return False
    val = (el.attrs.get(attr_name) or "").strip().lower()
    return val in _TRUTHY_VALUES


# ============================================================================
# 메인 검증
# ============================================================================

def run_checks(deck_path):
    """(results, meta) — results는 (rule_id, level, message) 튜플 목록."""
    html_raw = Path(deck_path).read_text(encoding="utf-8")
    html_text = re.sub(r"<!--.*?-->", "", html_raw, flags=re.S)
    tags, elements = parse_document(html_text)
    slide_els = sorted(_slide_elements(elements), key=lambda e: e.start)

    results = []  # (rule_id, level, message)
    advisories = []  # (rule_id, message) — 사람검토 전용, PASS/WARN/FAIL 판정 없음
    audit_lines = []  # 검사 미적용 감사추적 안내(신규 5종용)

    parent_map = _build_parent_map(elements)
    children_map = {}
    for el, par in parent_map.items():
        if par is not None:
            children_map.setdefault(id(par), []).append(el)

    records = []
    for idx, el in enumerate(slide_els):
        cls_str = el.attrs.get("class") or ""
        sid = el.attrs.get("data-slide") or f"(순번{idx + 1})"
        title_m = re.search(r'class="[^"]*\bs-title\b[^"]*"[^>]*>(.*?)</', html_text[el.inner_start:el.inner_end], re.S)
        title_text = re.sub(r"<[^>]+>", "", title_m.group(1)) if title_m else ""
        stype = classify_slide_type(idx, cls_str, title_text)
        visible_inner = _strip_hidden_spans(html_text, el.inner_start, el.inner_end, elements)
        family = family_signature(cls_str, visible_inner)
        chars = _text_len(html_text, el.inner_start, el.inner_end)
        # 본문 안전영역 밖(.s-head·pageno 등)까지 포함되지만, R-QC-01/02는 개념설명 유형만
        # 상대비교하므로(같은 방식으로 W1/W2 임계값을 도출) 오차가 상쇄된다.
        near_empty = find_near_empty_containers(html_text, el.inner_start, el.inner_end, elements)
        visuals = count_explanatory_visuals(html_text, el.inner_start, el.inner_end, tags)
        # 저작자 선언 예외(C1, 2026-07-27 신설): 저작자가 의도적으로 희박한 슬라이드로
        # 선언하면(예: 개념KB가 지정한 4노드 흐름 시각화를 화면이 그대로 옮긴 경우) R-QC-01/02
        # 밀도 하한에서 뺀다 — 정확한 슬라이드를 계속 WARN하면 게이트 전체가 무시된다.
        # A2(2026-07-27): 값을 본다 — `data-intentional-minimal="false"`는 예외가 아니다.
        intentional_minimal = _is_truthy_marker(el, "data-intentional-minimal")
        box_count = count_box_containers(html_text, el.inner_start, el.inner_end, elements)
        last_child = find_last_content_child(el, parent_map, children_map)
        has_conclusion = has_conclusion_callout(last_child)
        records.append({
            "idx": idx, "sid": sid, "cls": cls_str, "title": title_text, "type": stype,
            "family": family, "chars": chars, "near_empty": near_empty, "visuals": visuals,
            "intentional_minimal": intentional_minimal, "box_count": box_count,
            "has_conclusion": has_conclusion,
        })

    n_slides = len(records)
    concept_slides = [r for r in records if r["type"] == "개념설명"]
    screen_op_exempt = [r for r in concept_slides if r["family"] in _SCREEN_OP_FAMILIES]
    explanation = [r for r in concept_slides if r["family"] not in _SCREEN_OP_FAMILIES]
    # R-QC-01/02(밀도)만 이 예외를 적용한다 — R-QC-08(시각자료 비율)은 "밀도가 낮아도 되는
    # 슬라이드인가"가 아니라 "시각자료가 있는가"를 재므로 계속 explanation 전체를 본다.
    intentional_minimal_slides = [r for r in explanation if r["intentional_minimal"]]
    density_pool = [r for r in explanation if not r["intentional_minimal"]]

    # ── R-QC-02: 설명 슬라이드 의미 블록(text_leaf) 수 하한 — B2(2026-07-27): 주 신호로 승격 ──
    # (`skills/콘텐츠/SKILL.md`의 목표는 '정보 단위' 수이지 글자수가 아니다 — 이 검사가 그
    # 목표를 가장 직접 재는 지표이므로 보고 순서·우선순위 모두 R-QC-01보다 앞에 둔다.)
    low_blocks = []
    for r in density_pool:
        el = slide_els[r["idx"]]
        leafs = _count_text_leaf(html_text, el.inner_start, el.inner_end)
        r["blocks"] = leafs
        if leafs < THRESH_QC02_BLOCKS:
            low_blocks.append(r)
    if density_pool:
        pct = len(low_blocks) / len(density_pool) * 100
        detail = ", ".join(f'{r["sid"]}({r["blocks"]}개)' for r in low_blocks[:10])
        more = f" 외 {len(low_blocks) - 10}건" if len(low_blocks) > 10 else ""
        results.append(("R-QC-02", "WARN" if low_blocks else "PASS",
                         f"설명 슬라이드 의미 블록 수 <{THRESH_QC02_BLOCKS}개: {len(low_blocks)}/{len(density_pool)}장"
                         f"({pct:.1f}%){' — ' + detail + more if low_blocks else ''}"))
    else:
        results.append(("R-QC-02", "PASS", "설명 슬라이드 없음(검사 대상 0)"))

    # ── R-QC-01: 설명 슬라이드 본문 글자수 하한 — B2(2026-07-27): 목표가 아니라 정보 단위
    # 부족의 **대리 신호(proxy)**일 뿐이다. `skills/콘텐츠/SKILL.md`§0-6은 "문자수 목표는
    # 두지 않는다"고 명시하므로, WARN 문구가 "글자수를 늘려라"로 읽히지 않게 표현한다 —
    # 실제 조치는 R-QC-02(의미 블록 수)로 확인해 정보 단위를 더하는 것이다. ──
    low_chars = [r for r in density_pool if r["chars"] < THRESH_QC01_CHARS]
    if density_pool:
        pct = len(low_chars) / len(density_pool) * 100
        detail = ", ".join(f'{r["sid"]}({r["chars"]}자)' for r in low_chars[:10])
        more = f" 외 {len(low_chars) - 10}건" if len(low_chars) > 10 else ""
        results.append(("R-QC-01", "WARN" if low_chars else "PASS",
                         f"정보 단위가 부족할 가능성(본문 글자수 <{THRESH_QC01_CHARS}자, 목표 아닌 대리 신호): "
                         f"{len(low_chars)}/{len(density_pool)}장({pct:.1f}%) — R-QC-02(의미 블록 수)를 "
                         f"함께 확인하라. 글자수를 늘리는 게 아니라 정보 단위를 더하는 문제다"
                         f"{' — ' + detail + more if low_chars else ''}"))
    else:
        results.append(("R-QC-01", "PASS", "설명 슬라이드 없음(검사 대상 0)"))

    # ── R-QC-03: 근-빈 콘텐츠 컨테이너 탐지(전수 — 희소 결함이라 % 목표 대신 원시 카운트로 보고) ──
    slides_with_near_empty = [r for r in records if r["near_empty"]]
    total_near_empty = sum(len(r["near_empty"]) for r in records)
    if slides_with_near_empty:
        detail = ", ".join(f'{r["sid"]}({len(r["near_empty"])}개)' for r in slides_with_near_empty[:10])
        more = f" 외 {len(slides_with_near_empty) - 10}건" if len(slides_with_near_empty) > 10 else ""
        results.append(("R-QC-03", "WARN",
                         f"근-빈 컨테이너 보유 슬라이드 {len(slides_with_near_empty)}/{n_slides}장"
                         f"(총 {total_near_empty}개, accent-bar·pd-dots 제외) — {detail}{more}"))
    else:
        results.append(("R-QC-03", "PASS", "근-빈 컨테이너 0"))

    # ── R-QC-05: 동일 layout family 전체 반복률 + 최장 연속 ──
    # 2026-07-27 [사람검토]로 강등(자동 PASS/WARN/FAIL 없음) — 위 THRESH_QC05 주석 참고:
    # shipped family_signature() 실측에서 W1(모범)이 W2보다 비율이 더 높게 나와 방향이 뒤집힌다.
    content_records = [r for r in records if r["type"] not in ("표지",)]
    fam_seq = [r["family"] for r in content_records]
    if len(fam_seq) >= 2:
        adjacent_same = sum(1 for a, b in zip(fam_seq, fam_seq[1:]) if a == b)
        ratio = adjacent_same / (len(fam_seq) - 1)
        longest = 1
        cur = 1
        for a, b in zip(fam_seq, fam_seq[1:]):
            cur = cur + 1 if a == b else 1
            longest = max(longest, cur)
        advisories.append(("R-QC-05", f"동일 family 인접쌍 비율(지표값) {ratio:.3f} · 최장 연속 {longest}장 — "
                                       "판정 없음(방향 역전 확인돼 자동 게이트에서 제외, 위 THRESH_QC05 주석 참고). 사람이 직접 판단."))
    else:
        advisories.append(("R-QC-05", "콘텐츠 슬라이드 2장 미만 — 지표 계산 생략"))

    # ── R-QC-08: 설명 기능 시각자료 최소 비율 ──
    if explanation:
        with_visual = sum(1 for r in explanation if r["visuals"] > 0)
        ratio = with_visual / len(explanation)
        level = "WARN" if ratio < THRESH_QC08_VISUAL_RATIO else "PASS"
        results.append(("R-QC-08", level,
                         f"설명 슬라이드 중 시각자료 보유 비율 {ratio:.1%}({with_visual}/{len(explanation)}, "
                         f"임계 {THRESH_QC08_VISUAL_RATIO:.0%})"))
    else:
        results.append(("R-QC-08", "PASS", "설명 슬라이드 없음(검사 대상 0)"))

    # ── R-QC-09: 실습 슬라이드 완결성(행동·입력·완료기준) — 2026-07-27 [사람검토]로 강등 ──
    # 재검증 결과 두 덱 모두 100%(W1 5/5 · W2 10/10) 플래그돼 판별력이 0이었다. 원인 진단:
    # ① 완료기준 정규식이 콜론을 필수로 요구해 실제 저작 표기("완성" 라벨 뒤 콜론 없이 문장
    #    직결)를 아예 못 잡았다(위에서 콜론을 선택으로 완화).
    # ② W1의 "실습지시" 분류 자체가 `workspace` 형태소만으로 걸려 슬라이드 17·21처럼 실제로는
    #    개념 설명("작업공간·폴더·파일 구분하기")인 슬라이드까지 실습으로 오분류했다 —
    #    완료기준이 없는 게 당연한데 결함으로 잡혔다.
    # ①을 고쳐도 나머지(행동/입력 키워드가 못 잡는 동사 활용형 다양성 — "골라"·"제거합니다"
    # 등)까지 다 잡으려면 사실상 열린 한국어 동사활용 목록이 필요해 유지보수 비용 대비
    # 신뢰도가 낮다. 100%로 항상 울리는 규칙은 독자가 리포트 전체를 무시하게 만든다
    # (reviewer 지적) — 자동 판정을 접고 참고 수치만 제공한다.
    practice = [r for r in records if r["type"] == "실습지시"]
    incomplete = []
    for r in practice:
        el = slide_els[r["idx"]]
        text = decoded_text(html_text[el.inner_start:el.inner_end])
        fields = practice_completeness(text)
        missing = [k for k, v in fields.items() if not v]
        if missing:
            incomplete.append((r["sid"], missing))
    if practice:
        detail = ", ".join(f'{sid}(누락:{"/".join(m)})' for sid, m in incomplete[:10])
        advisories.append(("R-QC-09",
                            f"실습 슬라이드 키워드 완결성(참고치, 판정 없음) {len(incomplete)}/{len(practice)}장 "
                            f"미달 — {detail if incomplete else '전부 보유'} (키워드 기반 — 표현 다양성·분류 오차로 "
                            "판별력이 낮아 자동 WARN에서 제외됨, 사람이 직접 확인)"))
    else:
        advisories.append(("R-QC-09", "실습지시 슬라이드 없음(검사 대상 0)"))

    # ── R-QC-11: 부록 강등 검사 — 종결(요약/thank) 슬라이드 이후 슬라이드에 예시·근거·주의점이 있는가 ──
    closing_idx = None
    for i, r in enumerate(records):
        if r["type"] == "요약" and i > 0:
            closing_idx = i
    if closing_idx is not None:
        post = records[closing_idx + 1:]
        demoted_markers = []
        for r in post:
            el = slide_els[r["idx"]]
            text = decoded_text(html_text[el.inner_start:el.inner_end])
            markers = [m for m in ("예시", "주의", "근거", "사례") if m in text or m in r["title"]]
            if markers:
                demoted_markers.append((r["sid"], markers))
        if post:
            if demoted_markers:
                detail = ", ".join(f'{sid}({"/".join(ms)})' for sid, ms in demoted_markers[:10])
                results.append(("R-QC-11", "WARN",
                                 f"종결 슬라이드 뒤 부록 {len(post)}장 중 {len(demoted_markers)}장이 "
                                 f"예시/근거/주의점 마커 보유 — 본류 강등 의심: {detail}"))
            else:
                results.append(("R-QC-11", "PASS", f"종결 뒤 부록 {len(post)}장, 예시/근거/주의점 마커 0"))
        else:
            results.append(("R-QC-11", "PASS", "종결 슬라이드 뒤 부록 없음"))
    else:
        results.append(("R-QC-11", "PASS", "종결(요약) 슬라이드를 찾지 못함 — 부록 위치 판정 생략"))

    # ── R-QC-15: 하단 결론 콜아웃 보유율 ──
    if explanation:
        with_conclusion = [r for r in explanation if r["has_conclusion"]]
        ratio15 = len(with_conclusion) / len(explanation)
        level15 = "WARN" if ratio15 > THRESH_QC15_FOOT_CALLOUT_RATIO else "PASS"
        results.append(("R-QC-15", level15,
                         f"설명 슬라이드 중 하단 결론 콜아웃 보유 비율 {ratio15:.1%}"
                         f"({len(with_conclusion)}/{len(explanation)}, 임계 {THRESH_QC15_FOOT_CALLOUT_RATIO:.0%})"))
    else:
        results.append(("R-QC-15", "PASS", "설명 슬라이드 없음(검사 대상 0)"))

    # ── R-QC-16: 박스 기반 슬라이드 비율(박스 컨테이너 4개 이상) ──
    if explanation:
        box_based = [r for r in explanation if r["box_count"] >= 4]
        ratio16 = len(box_based) / len(explanation)
        level16 = "WARN" if ratio16 > THRESH_QC16_BOX_BASED_RATIO else "PASS"
        detail16 = ", ".join(f'{r["sid"]}({r["box_count"]}개)' for r in box_based[:10])
        more16 = f" 외 {len(box_based) - 10}건" if len(box_based) > 10 else ""
        results.append(("R-QC-16", level16,
                         f"박스 기반 설명 슬라이드(박스 컨테이너 4개 이상) 비율 {ratio16:.1%}"
                         f"({len(box_based)}/{len(explanation)}, 임계 {THRESH_QC16_BOX_BASED_RATIO:.0%})"
                         f"{' — ' + detail16 + more16 if box_based else ''}"))
    else:
        results.append(("R-QC-16", "PASS", "설명 슬라이드 없음(검사 대상 0)"))

    # ── R-QC-17: 실습 완결성 미달률(단계 요소 2개 미만) ──
    practice_slides17 = [
        r for r in records
        if "practice" in _morphemes(r["cls"]) or "실습" in (r["title"] or "")
    ]
    if not practice_slides17:
        advisories.append(("R-QC-17", "실습 슬라이드 0장 — 검사 미적용"))
        audit_lines.append("[감사추적] 실습 슬라이드 0장 — R-QC-17 미적용")
        n_practice17 = 0
        n_incomplete17 = 0
    else:
        incomplete17 = []
        for r in practice_slides17:
            el = slide_els[r["idx"]]
            frag = html_text[el.inner_start:el.inner_end]
            step_count = len(re.findall(r'class="[^"]*\bwork-step\b[^"]*"', frag))
            pr_steps_m = re.search(r'class="[^"]*\bpr-steps\b[^"]*"[^>]*>(.*?)</(?:ol|ul|div)>', frag, re.S)
            if pr_steps_m:
                step_count += len(re.findall(r"<li\b", pr_steps_m.group(1)))
            if step_count < 2:
                incomplete17.append(r["sid"])
        n_practice17 = len(practice_slides17)
        n_incomplete17 = len(incomplete17)
        ratio17 = n_incomplete17 / n_practice17
        level17 = "WARN" if ratio17 > THRESH_QC17_INCOMPLETE_PRACTICE_RATIO else "PASS"
        detail17 = ", ".join(incomplete17[:10])
        results.append(("R-QC-17", level17,
                         f"실습 완결성 미달(단계 요소 <2개) {n_incomplete17}/{n_practice17}장"
                         f"({ratio17:.1%}, 임계 {THRESH_QC17_INCOMPLETE_PRACTICE_RATIO:.0%})"
                         f"{' — ' + detail17 if incomplete17 else ''}"))

    # ── R-META-01: 메타 표기 잔존(내부 작업 라벨이 학생 화면에 남음) ──
    _META_PATTERNS = ["(왜", "(최소", "(예비", "(초안", "(심화", "TODO", "TBD", "※내부"]
    meta_hits = []
    for r in records:
        el = slide_els[r["idx"]]
        text = decoded_text(html_text[el.inner_start:el.inner_end])
        found = [p for p in _META_PATTERNS if p in text or p in (r["title"] or "")]
        if found:
            meta_hits.append((r["sid"], found))
    level_meta = "WARN" if len(meta_hits) > THRESH_META01_COUNT else "PASS"
    detail_meta = ", ".join(f'{sid}({"/".join(fs)})' for sid, fs in meta_hits[:10])
    results.append(("R-META-01", level_meta,
                     f"메타 표기 잔존 슬라이드 {len(meta_hits)}장(임계 {THRESH_META01_COUNT}건 초과 시 플래그)"
                     f"{' — ' + detail_meta if meta_hits else ''}"))

    # ── R-QC-12: 용어 최초 등장 정의 누락률 ──
    concept_kb_path = None
    m_path = re.search(r"(courses/[^/]+/sessions/[^/]+)/", str(deck_path).replace("\\", "/"))
    if m_path:
        subject_week = m_path.group(1)
        week = subject_week.split("/")[-1]
        concept_kb_path = Path(subject_week) / "자료" / f"{week}_개념KB.md"
    if concept_kb_path is None or not concept_kb_path.exists():
        advisories.append(("R-QC-12", "개념KB 없음 — 검사 미적용"))
        audit_lines.append("[감사추적] 개념KB 없음 — R-QC-12 미적용")
    else:
        kb_text = concept_kb_path.read_text(encoding="utf-8")
        display_names = _extract_display_names(kb_text)
        # 2026-07-31 버그 수정: 첫 등장 탐색이 HTML 주석 텍스트를 포함해 오판정했다(덱에 주석 71개).
        # 주석 제거 + 슬라이드 단위 첫 등장으로 교정.
        # (주석은 이미 위 line ~369에서 html_text 생성 시 전체 제거돼 있다 — 이 블록은 그 위에
        # 추가로 "첫 등장을 문서 전체 오프셋이 아니라 슬라이드 단위"로 바꾼다: 문서 전체 오프셋
        # 기준 90자 윈도우는 정의가 같은 슬라이드의 더 뒤쪽 문단에 있으면 놓친다 — 실측: '페르소나'
        # 정의는 첫 등장 지점에서 90자를 훌쩍 넘는 같은 슬라이드 뒷부분에 있었다. 슬라이드 텍스트
        # 전체를 검색 범위로 삼아 이 오탐을 없앤다.
        slide_texts = [decoded_text(html_text[el.inner_start:el.inner_end]) for el in slide_els]
        undefined = []
        seen_terms = []
        for name in display_names:
            found_slide_text = None
            pos = -1
            for stext in slide_texts:
                p = stext.find(name)
                if p >= 0:
                    found_slide_text = stext
                    pos = p
                    break
            if found_slide_text is None:
                continue
            seen_terms.append(name)
            # 정의 신호 탐색은 그 슬라이드의 텍스트 안에서만 한다(슬라이드 경계를 넘지 않는다).
            rest = found_slide_text[pos + len(name):]
            window = found_slide_text[pos:pos + len(name) + 60]
            # 2026-07-31 교정: 정의 신호에서 '입니다'·'—' 제거. 한국어 종결어미·구두점이라 60자
            # 범위에 거의 항상 존재해 정의가 없어도 통과하는 거짓 통과가 났다(교정 전 2주차 7.1%).
            has_marker = any(marker in window for marker in ("란 ", "이란", "라는", "말한다", "뜻", "의미", "= ")) or \
                any(marker in rest for marker in ("란 ", "이란", "라는", "말한다", "뜻", "의미", "= "))
            paren_match = re.match(r"\s*\(([^()]*)\)", rest[:64])
            has_paren_def = bool(paren_match and len(paren_match.group(1).strip()) >= 3)
            # 2026-07-31 3차 교정. 1차(표지+'입니다') 7.1% 과소, 2차(표지만) 92.9% 과대.
            # 한국어 정의는 표지 없이 병치로도 성립하므로 '용어 뒤 문장 경계 + 20자 이상 설명'을
            # 정의로 함께 인정한다. 표시명 일반어 필터도 보강했다.
            after = rest[:90]
            boundary_m = re.match(r"\s*(?:[.—:]|<[^>]*>)\s*([^<]*)", after, re.S)
            tail = re.sub(r"\s+", "", boundary_m.group(1)) if boundary_m else ""
            has_boundary_def = len(tail) >= 20
            if not (has_marker or has_paren_def or has_boundary_def):
                undefined.append(name)
        if seen_terms:
            ratio12 = len(undefined) / len(seen_terms)
            detail12 = ", ".join(undefined[:10])
            more12 = f" 외 {len(undefined) - 10}건" if len(undefined) > 10 else ""
            advisories.append(("R-QC-12",
                             f"용어 최초 등장 정의 누락 후보(참고치, 판정 없음) "
                             f"{len(undefined)}/{len(seen_terms)}"
                             f"{' — ' + detail12 + more12 if undefined else ''} "
                             f"(한국어 정의는 표지 없이 병치로도 성립해 문자열 판정이 부정확하다 — "
                             f"정의 3종 시도가 7.1%/92.9%/90.5%로 극단이었고, 첫 등장 탐색의 HTML 주석 "
                             f"오염 버그를 고쳐 71.4%까지 정확해졌으나 여전히 자동 판정 밴드 밖이라 "
                             f"참고치로만 둔다. 사람이 직접 확인)"))
        else:
            advisories.append(("R-QC-12", "개념KB 표시명이 덱에서 발견되지 않음(검사 대상 0, 참고치)"))

    # ── 사람검토 전용(자동화하지 않음) ──
    advisories.append(("R-QC-04", "카드 면적 대비 텍스트 비율 — 렌더 치수(getBoundingClientRect) 없이는 신뢰 불가. 브라우저 실측 필요."))
    advisories.append(("R-QC-07", "설명 단위 과잉 분할 — 의미 경계 판단이 필요해 정적 분석으로 셀 수 없음. 사람이 직접 확인."))
    advisories.append(("R-QC-10", "초안→덱 내용 보존율 — 자유서술 표현 변형을 텍스트 매칭으로 신뢰 판정할 수 없음. 사람이 직접 대조."))

    meta = {
        "n_slides": n_slides,
        "n_explanation": len(explanation),
        # 회귀 테스트(tests/test_quality_gates.py)가 메시지 문자열을 정규식으로 되읽지 않고
        # 바로 비교할 수 있도록 각 규칙의 원시 플래그 개수를 함께 반환한다(단일 소스 유지).
        "n_low_chars": len(low_chars),
        "n_low_blocks": len(low_blocks),
        "n_near_empty_slides": len(slides_with_near_empty),
        "n_near_empty_total": total_near_empty,
        "n_practice_incomplete": len(incomplete),
        "n_practice": len(practice),
        # A1(2026-07-27) 감사 추적 — R-QC-01/02 밀도 하한에서 빠진 슬라이드는 어떤 사유로든
        # 침묵 처리하지 않는다. 개수와 slide id를 그대로 노출한다.
        "n_intentional_minimal": len(intentional_minimal_slides),
        "intentional_minimal_ids": [r["sid"] for r in intentional_minimal_slides],
        "n_screen_operation_exempt": len(screen_op_exempt),
        "screen_operation_exempt_ids": [r["sid"] for r in screen_op_exempt],
        "audit_lines": audit_lines,  # 검사 미적용 감사추적 안내(신규 5종용) — 기존 4-tuple 반환 형태 보존
    }
    return results, advisories, meta, records


_GENERIC_WORDS = {
    "구분", "유형", "가능", "없음", "항목", "내용", "설명", "예시", "참고", "비고", "기타",
    "작동", "축", "즉시", "높음", "낮음", "고정", "시점", "매번", "상태", "결과", "방법",
    "기준", "조건", "범위", "순서", "단계", "확인", "정리",
}


def _extract_display_names(kb_text):
    """개념KB 「청크 인덱스」 표에서 '표시명' 열만 추출해 개념 용어 필터를 적용한다."""
    names = []
    lines = kb_text.splitlines()
    header_idx = None
    col_idx = None
    for i, line in enumerate(lines):
        if "|" not in line:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if header_idx is None and "표시명" in cells:
            header_idx = i
            col_idx = cells.index("표시명")
            continue
        if header_idx is None:
            continue
        if i == header_idx + 1 and re.match(r"^:?-{2,}", cells[0] if cells else ""):
            continue
        if col_idx is None or col_idx >= len(cells):
            # 표가 끝났으면(다음 헤더 등장 전까지) 계속 스캔; 셀 부족 행은 건너뛴다
            if not line.strip().startswith("|"):
                header_idx = None
            continue
        name = cells[col_idx].strip()
        if not name or name.startswith(":") or set(name) <= {"-", ":"}:
            continue
        if " vs " in name:
            continue
        if "·" in name:
            continue
        if len(name) > 12:
            continue
        if name in _GENERIC_WORDS:
            continue
        names.append(name)
    # 중복 제거(순서 보존)
    seen = set()
    out = []
    for n in names:
        if n not in seen:
            seen.add(n)
            out.append(n)
    return out


def _count_text_leaf(html_text, start, end):
    """8자 이상 직접 텍스트를 가진 leaf 노드 수(의미 블록 근사치). deck_quality_analysis.md의
    'blocks'(text_leaf_count) 정의를 재현 — <br> 분할 + 최소 컨테이너 태그 텍스트를 합산한다."""
    frag = html_text[start:end]
    frag = re.sub(r"<(script|style)\b[^>]*>.*?</\1\s*>", "", frag, flags=re.S | re.I)
    frag = re.sub(r"<(header)\b[^>]*>.*?</\1\s*>", "", frag, flags=re.S | re.I)
    # 태그 경계를 <br>과 동일한 분리자로 취급해 리프 텍스트 조각을 센다.
    parts = re.split(r"<[^>]+>", frag)
    import html as _h
    count = 0
    for p in parts:
        t = re.sub(r"\s+", "", _h.unescape(p))
        if len(t) >= 8:
            count += 1
    return count


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("deck")
    ap.add_argument("--baseline", help="비교용 기준 덱(예: sessions/1주차/강의덱.html) — 참고용, 판정에는 영향 없음")
    ap.add_argument("--json", help="결과를 JSON으로도 저장할 경로")
    ap.add_argument("--strict", action="store_true", help="WARN을 FAIL로 승격(기본은 WARN·exit 0)")
    a = ap.parse_args()

    try:
        results, advisories, meta, records = run_checks(a.deck)
        audit_lines = meta.get("audit_lines", [])
    except OSError as e:
        print(f"[FAIL] 파일 열기: {e}")
        sys.exit(1)

    print(THRESH_DERIVATION)
    print(f"=== verify_deck_quality: {a.deck} (슬라이드 {meta['n_slides']}장 · 설명유형 {meta['n_explanation']}장) ===")

    # A1(2026-07-27): R-QC-01/02 밀도 하한에서 빠진 슬라이드는 사유·개수·id를 항상 명시한다 —
    # 침묵 예외는 그 자체로 허점이다.
    exempt_total = meta["n_intentional_minimal"] + meta["n_screen_operation_exempt"]
    if exempt_total:
        parts = []
        if meta["n_screen_operation_exempt"]:
            parts.append(f"화면조작 계약예외(R-DENS-01a) {meta['n_screen_operation_exempt']}장: "
                          + ", ".join(meta["screen_operation_exempt_ids"]))
        if meta["n_intentional_minimal"]:
            parts.append(f"저작자 선언(data-intentional-minimal) {meta['n_intentional_minimal']}장: "
                          + ", ".join(meta["intentional_minimal_ids"]))
        print(f"[감사추적] R-QC-01/02 밀도 하한에서 제외된 설명 슬라이드 {exempt_total}장 — " + " · ".join(parts))
    else:
        print("[감사추적] R-QC-01/02 밀도 하한 제외 대상 0장")

    for line in audit_lines:
        print(line)

    effective = []
    for rule_id, level, msg in results:
        eff = level
        if a.strict and level == "WARN":
            eff = "FAIL"
        effective.append((rule_id, eff, msg))
        mark = {"PASS": "✓", "WARN": "△", "FAIL": "✗"}[eff]
        print(f"[{eff}] {mark} {rule_id}: {msg}")

    print("\n-- 사람검토(자동화 불가, 판정 없음) --")
    for rule_id, msg in advisories:
        print(f"[사람검토] · {rule_id}: {msg}")

    if a.baseline:
        try:
            base_results, _adv, base_meta, _rec = run_checks(a.baseline)
            base_warn = sum(1 for _r, lvl, _m in base_results if lvl == "WARN")
            cur_warn = sum(1 for _r, lvl, _m in results if lvl == "WARN")
            print(f"\n-- 기준(baseline) 비교: {a.baseline} --")
            print(f"baseline WARN {base_warn}(슬라이드 {base_meta['n_slides']}장) vs 대상 WARN {cur_warn}(슬라이드 {meta['n_slides']}장)")
        except OSError as e:
            print(f"[WARN] baseline 읽기 실패: {e}")

    fails = sum(1 for _r, lvl, _m in effective if lvl == "FAIL")
    warns = sum(1 for _r, lvl, _m in effective if lvl == "WARN")
    passes = sum(1 for _r, lvl, _m in effective if lvl == "PASS")
    print(f"\n요약: FAIL {fails} · WARN {warns} · PASS {passes}"
          f"{' (--strict: WARN→FAIL 승격됨)' if a.strict else ' (기본 모드: WARN은 exit 0)'}")

    if a.json:
        payload = {
            "deck": a.deck,
            "meta": meta,
            "results": [{"rule": r, "level": lvl, "message": m} for r, lvl, m in effective],
            "advisories": [{"rule": r, "message": m} for r, m in advisories],
            "thresholds": {
                "R-QC-01_chars": THRESH_QC01_CHARS,
                "R-QC-02_blocks": THRESH_QC02_BLOCKS,
                "R-QC-08_visual_ratio": THRESH_QC08_VISUAL_RATIO,
                "R-QC-15_foot_callout_ratio": THRESH_QC15_FOOT_CALLOUT_RATIO,
                "R-QC-16_box_based_ratio": THRESH_QC16_BOX_BASED_RATIO,
                "R-QC-17_incomplete_practice_ratio": THRESH_QC17_INCOMPLETE_PRACTICE_RATIO,
                "R-META-01_count": THRESH_META01_COUNT,
                # R-QC-05·R-QC-12는 임계값이 없다(사람검토로 강등 — 위 THRESH_QC05/QC12 주석 참고).
            },
        }
        Path(a.json).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
