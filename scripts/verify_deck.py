#!/usr/bin/env python3
"""verify_deck.py — vibecoding-deck 산출 덱 정적 검증 (측정 우선, 의존성 0).

사용: python scripts/verify_deck.py <deck.html> [--parts N]

정적으로 채점하는 것(브라우저 없이):
  - 슬라이드 수 · 고정 슬라이드(cover/s02/s03/concept-recap) 존재
  - part-divider 수 (= --parts N 이면 일치 검사)
  - 네비 엔진(.navbar) · 상세 메뉴 PDF 출력 버튼(#pdfBtn)
  - deck.css + legibility.css 로드(링크 또는 인라인)
  - 코드 시각화(.viz-* 또는 data-viz) vs 실제 <img> 개수 (로고·표지 SVG는 집계 제외)
  - 콘텐츠 슬라이드 구도 다양성: 서로 다른 구조 시그니처 수 · 같은 구도 최장 연속
  - raw #hex 색이 :root/토큰 밖에서 쓰였는지(토큰-only 대략 검사)
  - 덱 인라인 <style>/style= 그라디언트 금지(flat-fill) · 덱 인라인 var(--navy) 금지 · 진행/페이지 자동주입 스크립트(s-pageno+s-part)
  - 표지 3큐브(9면)+코랄 스파크 · 공유 kit CSS의 메인 블루 헤더 선 ·
    민트 강조 프리미티브 · 토큰/민트 배지 무결성
  - 박스 표면 규칙: 흰 fill(--white/--surface-alt) + 근백색 축약 보더(--line) 조합 금지
    (kit CSS + 덱 인라인 <style>/style= 모두 · 방향 지정 border-top/-bottom/-left는 내부 구분선으로 허용)
  - .work-step 수직 중앙 정렬(align-items:center) 계약

브라우저로만 되는 것(오버플로·콘솔·가독성 computed)은 이 스크립트가 안 하고 리마인더만 출력.
종료코드: FAIL 있으면 1, 아니면 0.
"""
import sys, re, os, argparse, json
from pathlib import Path
from urllib.parse import unquote, urlsplit
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows cp949 콘솔 대응
except Exception:
    pass

FIXED = {"cover": r'class="[^"]*\bcover\b', "s02": r'class="[^"]*\bs02-slide\b',
         "s03": r'class="[^"]*\bs03-slide\b', "recap": r'class="[^"]*\bconcept-recap\b'}

def find_sections(html):
    # <section ... class="slide ...">  → (full_class_attr, inner_html_until_next_section_or_end)
    secs = []
    for m in re.finditer(r'<section[^>]*class="([^"]*\bslide\b[^"]*)"[^>]*>', html):
        start = m.end()
        nxt = html.find("<section", start)
        inner = html[start: nxt if nxt != -1 else len(html)]
        secs.append((m.group(1), inner))
    return secs

def family_signature(cls, inner):
    """콘텐츠 슬라이드의 구조 시그니처(단조 감지용)."""
    sig = []
    # 본문 컨테이너 = 구도 축
    if re.search(r'\bcenter-msg\b', cls) or 'class="center-msg' in inner: sig.append("centered")
    elif 'class="s-body-wrap' in inner: sig.append("split/leftcol")
    elif 'class="s-full' in inner or 'canvas-fill' in cls: sig.append("full")
    else: sig.append("other")
    # 콘텐츠 마커
    if re.search(r'class="[^"]*\bgrid-[23]\b', inner) or 'revenue-grid' in inner: sig.append("grid")
    if 'table' in inner and re.search(r'class="t\b', inner): sig.append("table")
    if re.search(r'class="[^"]*\bviz-', inner) or re.search(r'\bdata-viz(?:\s*=|\s|>)', inner): sig.append("viz")
    if 'compare2' in inner: sig.append("compare")
    if 'work-step' in inner or 'flow-step' in inner: sig.append("flow")
    if 'shot-annot' in inner or 'shot-win' in inner: sig.append("shot")
    return "+".join(sig)


# 박스 표면 규칙 예외: 상태 도트·코드/터미널 표면·주석 스크린샷 창·캔버스/문서 루트·@블록
BOX_EXEMPT = re.compile(r'@|\.pd-dot|\.co-bar|\.cover-terminal|\.shot-|\.slide\b|\bbody\b|\bhtml\b|:root')

def box_surface_violations(css_text):
    """흰 fill(--white/--surface-alt) + 근백색(--line) '축약' 보더 조합 = 박스 표면 규칙 위반.
    방향 지정 보더(border-top/-bottom/-left/-right)는 내부 구분선이라 합법."""
    bad = []
    for m in re.finditer(r'([^{}]+)\{([^}]*)\}', css_text):
        sel, body = m.group(1).strip(), m.group(2)
        if BOX_EXEMPT.search(sel):
            continue
        if not re.search(r'background\s*:\s*var\(--(?:white|surface-alt)\)', body):
            continue
        if re.search(r'(?:^|;)\s*border\s*:[^;]*var\(--line\)', body):
            bad.append(sel.split(',')[0].strip()[:40])
    return bad

def local_linked_css(html, deck_path):
    """덱이 링크한 로컬 CSS를 읽는다. 외부 URL과 누락 파일은 건너뛴다."""
    chunks = []
    base = Path(deck_path).resolve().parent
    for href in re.findall(r'<link\b[^>]*\bhref=["\']([^"\']+)["\'][^>]*>', html, re.I):
        clean = href.split("?", 1)[0].split("#", 1)[0]
        if not clean or re.match(r'^(?:https?:|data:|//)', clean, re.I):
            continue
        css_path = (base / clean).resolve()
        if css_path.is_file() and css_path.suffix.lower() == ".css":
            try:
                chunks.append(css_path.read_text(encoding="utf-8"))
            except OSError:
                pass
    return "\n".join(chunks)


def _attr(tag, name):
    match = re.search(rf'\b{re.escape(name)}\s*=\s*(["\'])(.*?)\1', tag, re.I | re.S)
    return match.group(2) if match else None


def _is_remote(reference):
    return bool(re.match(r'^(?:https?:)?//', reference or '', re.I))


def _local_reference(reference, base):
    if not reference or reference.startswith(('data:', '#')) or _is_remote(reference):
        return None
    return (base / unquote(urlsplit(reference).path)).resolve()


def _srcset_references(value):
    for candidate in (value or '').split(','):
        pieces = candidate.strip().split(None, 1)
        if pieces:
            yield pieces[0]


def _figure_slots(html):
    slots = []
    for match in re.finditer(r'<figure\b([^>]*)>(.*?)</figure>', html, re.I | re.S):
        attrs, body = match.group(1), match.group(2)
        classes = _attr(attrs, 'class') or ''
        if re.search(r'\basset-slot\b', classes):
            slots.append((attrs, body, classes))
    return slots


def count_code_viz(html):
    """Count explicit visualization owner elements once, even with two markers."""
    count = 0
    for tag in re.findall(r'<[a-z][^>]*>', html, re.I):
        classes = _attr(tag, 'class') or ''
        if re.search(r'(?:^|\s)viz-[a-z0-9_-]+(?:\s|$)', classes, re.I) or re.search(
            r'\bdata-viz(?:\s*=|\s|>)', tag, re.I
        ):
            count += 1
    return count


def _slide_section_ranges(html):
    """Return (start, end, classes, opening_tag) for quoted HTML slide sections."""
    openings = []
    for match in re.finditer(r'<section\b[^>]*>', html, re.I):
        classes = _attr(match.group(0), 'class') or ''
        if re.search(r'(?:^|\s)slide(?:\s|$)', classes):
            openings.append((match.start(), classes, match.group(0)))
    ranges = []
    for index, (start, classes, tag) in enumerate(openings):
        end = openings[index + 1][0] if index + 1 < len(openings) else len(html)
        ranges.append((start, end, classes, tag))
    return ranges


def validate_manifest_document(data):
    """Validate the session image-manifest contract at runtime."""
    errors = []
    if not isinstance(data, dict):
        return ['manifest root must be an object']
    required_root = {'schema_version', 'session', 'image_mode', 'slides'}
    missing_root = sorted(required_root - set(data))
    if missing_root:
        errors.append(f'manifest missing required fields {missing_root}')
    if data.get('schema_version') != '1.0':
        errors.append("manifest schema_version must be '1.0'")
    if not isinstance(data.get('session'), str) or not data.get('session', '').strip():
        errors.append('manifest session must be a nonempty string')
    if data.get('image_mode') not in {'not_required', 'reuse_only', 'generate_now', 'prompt_only', 'pending'}:
        errors.append('manifest image_mode is invalid')
    slides = data.get('slides')
    if not isinstance(slides, list):
        errors.append('manifest slides must be an array')
        return errors

    required_slide = {
        'slide_id', 'part', 'decision', 'decision_reason', 'purpose', 'role', 'brief',
        'expected_file', 'method', 'asset_id', 'parent_asset_ids', 'prompt_id', 'status', 'qa',
    }
    decisions = {
        'NO_IMAGE': 'none',
        'IMAGE_EXPLANATORY': 'explanatory',
        'IMAGE_MNEMONIC': 'mnemonic',
        'IMAGE_DECORATIVE_OPTIONAL': 'decorative',
    }
    for index, slide in enumerate(slides):
        prefix = f'manifest slide {index}'
        if not isinstance(slide, dict):
            errors.append(f'{prefix} must be an object')
            continue
        missing = sorted(required_slide - set(slide))
        if missing:
            errors.append(f'{prefix} missing required fields {missing}')
        decision = slide.get('decision')
        purpose = slide.get('purpose')
        if decision not in decisions:
            errors.append(f'{prefix} decision is invalid')
        elif purpose != decisions[decision]:
            errors.append(f'{prefix} decision-purpose mismatch')
        if purpose not in {'none', 'explanatory', 'mnemonic', 'decorative'}:
            errors.append(f'{prefix} purpose is invalid')
        role = slide.get('role')
        status = slide.get('status')
        method = slide.get('method')
        if role not in {'none', 'hero', 'support', 'spot'}:
            errors.append(f'{prefix} role is invalid')
        if status not in {'not_needed', 'expected', 'processing', 'ready', 'rejected', 'blocked'}:
            errors.append(f'{prefix} status is invalid')
        if method not in {'none', 'reuse', 'generate', 'transform'}:
            errors.append(f'{prefix} method is invalid')
        if decision == 'NO_IMAGE':
            if role != 'none' or status != 'not_needed' or method != 'none' or slide.get('expected_file') is not None:
                errors.append(f'{prefix} NO_IMAGE state is inconsistent')
        elif role not in {'hero', 'support', 'spot'} or not isinstance(slide.get('expected_file'), str) or not slide.get('expected_file'):
            errors.append(f'{prefix} image decision requires active role and expected_file')
        if not isinstance(slide.get('parent_asset_ids'), list):
            errors.append(f'{prefix} parent_asset_ids must be an array')
        if not isinstance(slide.get('brief'), dict) or not isinstance(slide.get('qa'), dict):
            errors.append(f'{prefix} brief and qa must be objects')
    return errors


def image_contract_checks(html, deck_path, *, release=False, manifest_path=None, registry_path=None):
    """Return static image-contract violations and informational notes."""
    errors, notes = [], []
    base = Path(deck_path).resolve().parent
    html = re.sub(r"<!--.*?-->", "", html, flags=re.S)  # commented example markup is not live

    # Broken local image references include picture/srcset, but prompt_only slots
    # deliberately have no img src and are handled separately below.
    for tag in re.findall(r'<(?:img|source)\b[^>]*>', html, re.I):
        for name in ('src',):
            reference = _attr(tag, name)
            path = _local_reference(reference, base)
            if path is not None and not path.is_file():
                errors.append(f'missing local image: {reference}')
        for reference in _srcset_references(_attr(tag, 'srcset')):
            path = _local_reference(reference, base)
            if path is not None and not path.is_file():
                errors.append(f'missing local srcset image: {reference}')

    allowed_roles = {'hero', 'support', 'spot'}
    allowed_purposes = {'explanatory', 'mnemonic', 'decorative'}
    slots = _figure_slots(html)
    expected_required = 0
    expected_total = 0
    for attrs, body, classes in slots:
        purpose = (_attr(attrs, 'data-image-purpose') or '').lower()
        state = (_attr(attrs, 'data-image-state') or 'ready').lower()
        role_match = re.search(r'\basset-slot--([a-z0-9-]+)\b', classes)
        role = role_match.group(1) if role_match else (_attr(attrs, 'data-image-role') or '')
        kind = (_attr(attrs, 'data-asset-kind') or 'paper-cut-v1').lower()
        img = re.search(r'<img\b[^>]*>', body, re.I | re.S)
        if purpose not in allowed_purposes:
            errors.append(f'asset slot has invalid image purpose: {purpose or "missing"}')
        if role not in allowed_roles:
            errors.append(f'asset slot has inactive or invalid role: {role or "missing"}')
        if kind not in {'paper-cut-v1', 'screenshot', 'photo', 'user-provided'}:
            errors.append(f'asset slot has invalid asset kind: {kind}')
        if kind == 'paper-cut-v1' and role not in allowed_roles:
            errors.append('paper-cut-v1 cannot use cover-object or section-overlay')
        if state == 'expected':
            expected_total += 1
            if img and _attr(img.group(0), 'src'):
                errors.append('prompt_only expected slot must not emit an img src')
            if not _attr(attrs, 'data-expected-src'):
                errors.append('expected slot is missing data-expected-src')
            if purpose in {'explanatory', 'mnemonic'}:
                expected_required += 1
        elif purpose in {'explanatory', 'mnemonic'}:
            if not img:
                errors.append(f'{purpose} slot is missing img')
            else:
                src = _attr(img.group(0), 'src')
                if not src or not src.strip():
                    errors.append(f'{purpose} ready image requires nonempty src')
                alt = _attr(img.group(0), 'alt')
                if not alt or not alt.strip():
                    errors.append(f'{purpose} image requires relational alt text')
        elif purpose == 'decorative':
            if img:
                alt = _attr(img.group(0), 'alt')
                hidden = (_attr(img.group(0), 'aria-hidden') or '').lower()
                if alt != '' or hidden != 'true':
                    errors.append('decorative image requires alt="" and aria-hidden="true"')
    if release and expected_total:
        errors.append(f'unresolved required/expected image slots: {expected_total}')
    elif expected_required:
        if not release:
            notes.append(f'prompt_only expected slots: {expected_required} (development only)')

    # S02 uses a dedicated width contract when it contains a ready hero/support image.
    section_ranges = _slide_section_ranges(html)
    for start, end, classes, _tag in section_ranges:
        section = html[start:end]
        if re.search(r'\bs02-slide\b', classes):
            ready_wide_slot = False
            for figure_tag in re.findall(r'<figure\b[^>]*>', section, re.I):
                figure_classes = _attr(figure_tag, 'class') or ''
                role_match = re.search(r'\basset-slot--(hero|support)\b', figure_classes)
                state = (_attr(figure_tag, 'data-image-state') or 'ready').lower()
                if role_match and state == 'ready':
                    ready_wide_slot = True
                    break
            if ready_wide_slot and not re.search(r'\bhas-image\b', classes):
                errors.append('S02 ready hero/support image requires section class has-image')

    # Content images are public components, never bare img tags. Fixed logos are exempt.
    slot_spans = [match.span() for match in re.finditer(r'<figure\b[^>]*class=["\'][^"\']*\basset-slot\b[^"\']*["\'][^>]*>.*?</figure>', html, re.I | re.S)]
    for image_match in re.finditer(r'<img\b[^>]*>', html, re.I):
        position = image_match.start()
        containing_section = None
        for start, end, classes, tag in section_ranges:
            if start <= position < end:
                containing_section = (start, end, classes, tag)
                break
        if containing_section is None or any(start <= position < end for start, end in slot_spans):
            continue
        image_classes = _attr(image_match.group(0), 'class') or ''
        if re.search(r'(?:^|\s)(?:s-logo|brand-logo|favicon|cover-logo)(?:\s|$)', image_classes, re.I):
            continue
        errors.append('content img outside asset-slot; screenshots require figure.asset-slot kind=screenshot')

    # Decorative images: one per part, never consecutive, never with a code viz.
    decorative_indexes, by_part, part = [], {}, 0
    for index, (start, end, classes, _tag) in enumerate(section_ranges):
        section = html[start:end]
        if re.search(r'\bpart-divider\b', classes):
            part += 1
        if re.search(r'data-image-purpose\s*=\s*["\']decorative["\']', section, re.I):
            decorative_indexes.append(index)
            by_part[part] = by_part.get(part, 0) + 1
            if count_code_viz(section):
                errors.append(f'decorative image shares slide {index + 1} with code visualization')
    if any(b == a + 1 for a, b in zip(decorative_indexes, decorative_indexes[1:])):
        errors.append('decorative images may not appear on consecutive slides')
    for part_number, count in by_part.items():
        if count > 1:
            errors.append(f'part {part_number} has {count} decorative images (maximum 1)')

    # Optional HTML/manifest/registry cross-check. Only explicit asset IDs are
    # matched, avoiding guesses for user-provided photos and screenshots.
    manifest = None
    if manifest_path:
        try:
            manifest = json.loads(Path(manifest_path).read_text(encoding='utf-8'))
            errors.extend(validate_manifest_document(manifest))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f'image manifest cannot be read: {exc}')
    registry = None
    if registry_path:
        try:
            registry = json.loads(Path(registry_path).read_text(encoding='utf-8'))
            try:
                from .verify_image_assets import verify_registry
            except ImportError:
                from verify_image_assets import verify_registry
            registry_reports, registry_errors = verify_registry(Path(registry_path))
            errors.extend(f'image registry: {error}' for error in registry_errors)
            for report in registry_reports:
                errors.extend(f'image registry: {error}' for error in report.errors)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f'image registry cannot be read: {exc}')
    entries = []
    if isinstance(registry, dict) and isinstance(registry.get('assets'), list):
        entries = registry['assets']
    registry_by_id = {str(item.get('id') or item.get('asset_id')): item for item in entries if isinstance(item, dict)}
    for attrs, body, _classes in slots:
        asset_id = _attr(attrs, 'data-asset-id')
        if not asset_id:
            continue
        entry = registry_by_id.get(asset_id)
        if registry is not None and entry is None:
            errors.append(f'HTML references unknown registry asset: {asset_id}')
        elif entry and entry.get('status') != 'approved':
            errors.append(f'HTML references non-approved asset: {asset_id}')
        elif entry:
            img = re.search(r'<img\b[^>]*>', body, re.I | re.S)
            src = _attr(img.group(0), 'src') if img else _attr(attrs, 'data-expected-src')
            registered = str(entry.get('file') or entry.get('path') or '')
            if src and registered and not Path(src).as_posix().endswith(Path(registered).as_posix()):
                errors.append(f'HTML path for {asset_id} does not match registry')
    if manifest is not None:
        manifest_text = json.dumps(manifest, ensure_ascii=False)
        for attrs, _body, _classes in slots:
            asset_id = _attr(attrs, 'data-asset-id')
            if asset_id and asset_id not in manifest_text:
                errors.append(f'HTML asset {asset_id} is missing from session manifest')
    return errors, notes

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("deck"); ap.add_argument("--parts", type=int, default=None)
    ap.add_argument("--release", action="store_true", help="배포 기준으로 expected 필수 슬롯을 실패 처리")
    ap.add_argument("--manifest", help="세션 자료/이미지-에셋.json 경로")
    ap.add_argument("--registry", help="중앙 이미지 registry.json 경로")
    a = ap.parse_args()
    try:
        html = open(a.deck, encoding="utf-8").read()
    except OSError as e:
        print(f"[FAIL] 파일 열기: {e}"); sys.exit(1)
    html = re.sub(r"<!--.*?-->", "", html, flags=re.S)  # commented markup (examples, presenter notes) is not live

    results = []  # (level, msg)  level in PASS/WARN/FAIL
    def chk(cond, ok, bad, warn=False):
        results.append(("PASS" if cond else ("WARN" if warn else "FAIL"), ok if cond else bad))

    secs = find_sections(html)
    n = len(secs)
    chk(n >= 5, f"슬라이드 {n}장", f"슬라이드 {n}장 — 너무 적음(고정 4 + 본문 필요)")

    for key, pat in FIXED.items():
        chk(re.search(pat, html) is not None, f"고정 슬라이드 {key} 존재", f"고정 슬라이드 {key} 없음")

    # 표지 불변요소: 3개 큐브(data-cube) × 각 3면 = polygon 9개, 코랄 스파크 1개
    cover_inner = next((inner for cls, inner in secs if re.search(r'\bcover\b', cls)), '')
    cube_count = len(re.findall(r'<g\b[^>]*\bdata-cube=', cover_inner))
    cover_faces = len(re.findall(r'<polygon\b', cover_inner))
    spark_count = len(re.findall(r'<circle\b[^>]*fill="var\(--coral\)"', cover_inner))
    chk(cube_count == 3 and cover_faces == 9 and spark_count >= 1,
        "표지 3큐브·9면·코랄 스파크 유지",
        f"표지 도형 불완전: cube={cube_count}, polygon={cover_faces}, coral spark={spark_count}")

    # ── 브랜드 표기: 헤더/표지 .s-brand는 영문 VIBECODING (2026-07-17) ──
    brand_texts = re.findall(r'<span class="[^"]*\bs-brand\b[^"]*"[^>]*>(.*?)</span>', html, re.S)
    bad_brand = [t for t in brand_texts if '바이브코딩' in t]
    chk(not bad_brand, "브랜드 텍스트 VIBECODING(영문)",
        f".s-brand에 한글 브랜드 잔존 {len(bad_brand)}건 — VIBECODING으로 교체")

    dividers = len(re.findall(r'class="[^"]*\bpart-divider\b', html))
    if a.parts is not None:
        chk(dividers == a.parts, f"part-divider {dividers} = 파트 {a.parts}",
            f"part-divider {dividers} ≠ 파트 {a.parts} (모든 파트 앞 divider 필수)")
    else:
        chk(dividers >= 1, f"part-divider {dividers}개", "part-divider 없음", warn=True)

    # ── 아젠다 2열 규칙: an-item 4개 초과면 .an-right에 an-2col 필수(크기 축소 금지) (2026-07-17) ──
    s03_inner = next((inner for cls, inner in secs if re.search(r'\bs03-slide\b', cls)), None)
    if s03_inner is not None:
        an_items = len(re.findall(r'class="[^"]*\ban-item\b[^"]*"', s03_inner))
        m03 = re.search(r'<div class="([^"]*\ban-right\b[^"]*)"', s03_inner)
        an_right_cls = m03.group(1) if m03 else ''
        if an_items > 4:
            chk('an-2col' in an_right_cls, f"아젠다 {an_items}항목 → an-2col 적용(2열 확장)",
                f"아젠다 {an_items}항목(>4)인데 an-2col 없음 — 크기 축소 대신 .an-right에 an-2col 부여")
        elif an_items > 0:
            chk('an-2col' not in an_right_cls, f"아젠다 {an_items}항목 → 1열 유지",
                f"아젠다 {an_items}항목(≤4)인데 an-2col 불필요 적용", warn=True)

        # ── 아젠다 v3: 제목 고정 멘트 + 민트 바 (2026-07-17) ──
        #   .an-title이 있는 아젠다에만 적용. 카탈로그(--parts 0)는 검사 제외(MEMORY 규약).
        m_title = re.search(r'<h2 class="[^"]*\ban-title\b[^"]*"[^>]*>(.*?)</h2>', s03_inner, re.S)
        if m_title is not None and a.parts != 0:
            title_txt = re.sub(r'<[^>]+>', '', m_title.group(1)).strip()
            chk(title_txt == '오늘 배우게 될 것', '아젠다 제목 고정 멘트 "오늘 배우게 될 것"',
                f'아젠다 제목 "{title_txt}" — 고정 멘트 "오늘 배우게 될 것"으로(자유 작성 금지)')
            chk('an-bar' in s03_inner, "아젠다 민트 바(.an-bar) 존재",
                "아젠다 .an-bar 없음 — 고정 제목 아래 민트 pill 바 필수")

    chk('class="navbar"' in html or "id=\"controls\"" in html, "네비 엔진 존재", "네비바(.navbar) 없음")
    chk('id="pdfBtn"' in html or "id='pdfBtn'" in html or 'dl-btn' in html,
        "PDF 버튼 존재", "PDF 버튼(#pdfBtn 또는 .dl-btn) 없음")
    nav_detail_ids = ('menuBtn', 'homeBtn', 'pageInput', 'slideList', 'pdfBtn')
    nav_detail_ok = all((f'id="{item}"' in html or f"id='{item}'" in html) for item in nav_detail_ids)
    chk(nav_detail_ok, "상세 발표 메뉴(홈·이동·목록·PDF) 존재", "상세 메뉴 기능 요소 누락")
    rendered_css = html + "\n" + local_linked_css(html, a.deck)
    chk('--glass-white' in rendered_css and re.search(r'backdrop-filter\s*:\s*blur', rendered_css),
        "흰색 글래스 내비게이션 토큰 존재", "글래스 내비게이션 토큰/효과 없음")

    # ── 아젠다 배지 플랫: .an-num 선언에 box-shadow 금지 (2026-07-17, kit CSS+덱 인라인 모두) ──
    an_num_shadow = re.findall(r'\.an-num\b[^{]*\{[^}]*box-shadow[^}]*\}', rendered_css)
    chk(not an_num_shadow, ".an-num 플랫(box-shadow 없음)",
        f".an-num 선언에 box-shadow {len(an_num_shadow)}건 — v3 플랫 배지(그림자 제거)")

    css_ok = 'deck.css' in html or ('<style' in html and '--blue' in html)
    leg_ok = 'legibility.css' in html or ('<style' in html and 'legibility' in html) or ('font-size:22px' in html)
    chk(css_ok, "deck.css 상속(링크/인라인)", "deck.css 미로드")
    chk(leg_ok, "강의장 가독성 레이어 로드", "legibility 미로드(본문 22px 하한 위험)", warn=True)

    # ── 본문 eyebrow의 PART 중복 금지: 헤더 .s-part(PART n/N)가 위치를 전담 (2026-07-17) ──
    #   .pd-eyebrow(파트전환, 'PART n/N' 슬래시 포맷)는 별개 클래스라 스캔 대상 아님.
    eyebrow_texts = re.findall(r'<p class="[^"]*\bs-eyebrow\b[^"]*"[^>]*>(.*?)</p>', html, re.S)
    part_dup = [re.sub(r'<[^>]+>', '', t).strip()[:30] for t in eyebrow_texts if re.search(r'PART\s*\d+\s*·', t)]
    chk(not part_dup, "본문 eyebrow에 PART n·파트명 중복 없음",
        f".s-eyebrow에 PART 형식 잔존 {part_dup[:5]} — 헤더 .s-part와 중복(삭제 대상)")

    imgs = len(re.findall(r'<img\b', html))
    # Header logos, cover cubes, and annotation SVGs are not code visualizations.
    # Only explicit .viz-* or data-viz ownership is counted.
    viz = count_code_viz(html)
    chk(viz >= imgs, f"코드 시각화 {viz} ≥ 이미지 {imgs} (code-viz 우선)",
        f"이미지 {imgs} > 코드 시각화 {viz} — 코드 우선 원칙 위배 소지", warn=True)

    image_errors, image_notes = image_contract_checks(
        html,
        a.deck,
        release=a.release,
        manifest_path=a.manifest,
        registry_path=a.registry,
    )
    chk(not image_errors, "이미지 경로·목적·역할·배치 계약 준수",
        "이미지 계약 위반: " + " | ".join(image_errors))
    for note in image_notes:
        results.append(("WARN", note))

    # 콘텐츠 슬라이드(고정/divider 제외) 다양성
    content = [(c, inr) for (c, inr) in secs
               if not re.search(r'\b(cover|s02-slide|s03-slide|part-divider|concept-recap|closing)\b', c)]
    sigs = [family_signature(c, inr) for (c, inr) in content]
    distinct = len(set(sigs))
    maxrun, run = 1, 1
    for i in range(1, len(sigs)):
        run = run + 1 if sigs[i] == sigs[i-1] else 1
        maxrun = max(maxrun, run)
    is_reference_atlas = 'atlas-slide' in html and 'LAYOUT ATLAS' in html
    if content and not is_reference_atlas:
        chk(distinct >= max(3, len(content)//2),
            f"구도 다양성: {distinct}종 / 본문 {len(content)}장",
            f"구도 다양성 낮음: {distinct}종 / 본문 {len(content)}장 (단조 위험)", warn=True)
        chk(maxrun <= 2, f"같은 구도 최장 연속 {maxrun} (≤2)",
            f"같은 구도 {maxrun}연속 — 3연속 금지 위배 (시그니처 반복: {sigs})")
    elif content:
        chk(True, "참조 아틀라스: 50 레이아웃·21 element 연속열람용 다양성 검사 제외", "")

    # 토큰-only 대략 검사: <style>/인라인 style 안 raw #hex
    #   스킵 규칙(둘 중 하나면 스킵): (1) :root{...} 블록 내부  (2) 토큰 정의 줄(첫 ':' 앞부분에 '--' 포함)
    #   → inline_deck.py로 deck.css가 통째로 인라인돼도 토큰 정의(:root 내부·--name:#hex)는 오탐 안 나게.
    style_blocks = re.findall(r'<style[^>]*>(.*?)</style>', html, re.S)
    inline_styles = re.findall(r'style="([^"]*)"', html)
    hexhits = []
    for blk in style_blocks:
        in_root = False
        for ln in blk.splitlines():
            if ':root' in ln and '{' in ln:
                in_root = True
            head = ln.split(':', 1)[0]          # 첫 콜론 앞 = 셀렉터/속성명 영역
            if in_root or '--' in head:          # :root 블록 안이거나 토큰 정의 줄이면 스킵
                if in_root and '}' in ln:        # :root 블록 종료 감지
                    in_root = False
                continue
            hexhits += re.findall(r'#[0-9a-fA-F]{3,6}\b', ln)
    for st in inline_styles:
        hexhits += re.findall(r'#[0-9a-fA-F]{3,6}\b', st)
    chk(len(hexhits) == 0, "토큰만 사용(raw #hex 0)",
        f"raw #hex {len(hexhits)}건({sorted(set(hexhits))[:6]}) — var(--token)로 교체", warn=True)

    # ── 덱 자체 <style>/인라인 style 그라디언트 금지 (flat-fill 원칙) ──
    deck_style_text = "\n".join(style_blocks) + "\n" + "\n".join(inline_styles)
    dgrad = len(re.findall(r'\b(?:linear|radial|conic)-gradient', deck_style_text))
    chk(dgrad == 0, "덱 인라인 그라디언트 0 (flat-fill)",
        f"덱 <style>/style=에 gradient {dgrad}건 — flat-fill 원칙 위배")

    # ── 덱 자체 <style>/인라인 style var(--navy) 금지 (navy는 v2 팔레트 제외) ──
    dnavy = len(re.findall(r'var\(\s*--navy\s*\)', deck_style_text))
    chk(dnavy == 0, "덱 인라인 var(--navy) 0",
        f"덱 <style>/style=에 var(--navy) {dnavy}건 — navy 사용 금지(어두운 배경/텍스트는 --ink)")

    # ── 덱 자체 박스 표면 규칙: 흰 fill + 근백색(--line) 축약 보더 조합 금지 ──
    deck_box_bad = box_surface_violations("\n".join(style_blocks))
    for st in inline_styles:
        if re.search(r'background\s*:\s*var\(--(?:white|surface-alt)\)', st) and \
           re.search(r'(?:^|;)\s*border\s*:[^;]*var\(--line\)', st):
            deck_box_bad.append('style="' + st[:40] + '…"')
    chk(not deck_box_bad, "덱 인라인 박스 표면 규칙 준수(흰 fill+--line 보더 0)",
        f"덱 인라인 흰 fill+근백색 보더 박스 {deck_box_bad} — 틴트 fill 또는 유색 보더(--blue-line-strong 등)로 교체")

    # ── 진행도트·페이지번호 자동 주입 스크립트 존재 (s-pageno + s-part) ──
    scripts = " ".join(re.findall(r'<script[^>]*>(.*?)</script>', html, re.S))
    inject_ok = ('s-pageno' in scripts) and ('s-part' in scripts)
    chk(inject_ok, "진행·페이지 자동주입(s-pageno+s-part) 존재",
        "s-pageno/s-part 자동주입 스크립트 없음 — 페이지번호·파트도트 누락 위험", warn=True)

    # ── 공유 kit CSS(deck.css · patterns.css) 무결성: 스크립트 위치 기준 해석(cwd·덱경로 무관) ──
    _here = os.path.dirname(os.path.abspath(__file__))
    def _read_css(*parts):
        p = os.path.join(_here, *parts)
        try:
            return open(p, encoding='utf-8').read()
        except OSError:
            return None
    deckcss = _read_css('..', 'kit', 'styles', 'deck.css')
    patterns = _read_css('..', 'kit', 'styles', 'patterns.css')
    kit_css = "\n".join(c for c in (deckcss, patterns) if c is not None)

    if deckcss is not None or patterns is not None:
        # (1) 그라디언트 0 (deck.css + patterns.css)
        kgrad = len(re.findall(r'\b(?:linear|radial|conic)-gradient', kit_css))
        chk(kgrad == 0, "kit CSS 그라디언트 0 (flat-fill)",
            f"kit CSS에 gradient {kgrad}건 — flat-fill 원칙 위배")
        # (2) var(--navy) 미사용 (정의 줄 --navy: 는 매칭 안 됨 → 허용)
        knavy = len(re.findall(r'var\(\s*--navy\s*\)', kit_css))
        chk(knavy == 0, "var(--navy) 미사용", f"var(--navy) {knavy}건 사용 — v2 팔레트 제외 대상")
        # (2b) 새 구조 요소는 보조 블루(ice/electric)가 아니라 --blue를 사용한다.
        css_without_root = re.sub(r':root\s*\{.*?\}', '', kit_css, flags=re.S)
        legacy_blue = len(re.findall(r'var\(\s*--(?:ice|electric)\s*\)', css_without_root))
        chk(legacy_blue == 0, "레거시 보조 블루(ice/electric) 렌더 사용 0",
            f"var(--ice)/var(--electric) {legacy_blue}건 — 구조·주 강조는 --blue만 사용")
        # (2c) 박스 표면 규칙: 흰 카드가 근백색 --line 보더만으로 구분되면 안 된다(2026-07-16).
        kit_box_bad = box_surface_violations(kit_css)
        chk(not kit_box_bad, "kit CSS 박스 표면 규칙 준수(흰 fill+--line 축약보더 0)",
            f"흰 fill+근백색 보더 박스 {kit_box_bad} — 틴트 fill 또는 유색 보더(--blue-line-strong/--mint-line/--coral-line)로 교체")

    if deckcss is not None:
        # (3) :root 토큰 값 정확성(부분문자열 매칭 · 공백정규화 · hex 대소문자 무시)
        rootm = re.search(r':root\s*\{(.*?)\}', deckcss, re.S)
        root_norm = re.sub(r'\s+', '', rootm.group(1)).lower() if rootm else ''
        need_tokens = ['--blue:#1D4ED8', '--mint:#14B8A6', '--coral:#F97360', '--red:#DC2626',
                       '--mint-deep:#0F766E', '--coral-deep:#C2452F',
                       '--on-mint', '--on-coral', '--r-lg:20px', '--font-mono', '--mint-line']
        miss_tokens = [t for t in need_tokens if re.sub(r'\s+', '', t).lower() not in root_norm]
        chk(not miss_tokens, f"토큰 값 정확(deck.css :root, {len(need_tokens)}개 확인)",
            f"토큰 누락/값변경: {miss_tokens}")
        # (3b) 헤더 선과 민트 강조 프리미티브는 공용 CSS 계약을 지킨다.
        def css_block(selector):
            m = re.search(r'(?:^|[}\n;,{])\s*' + selector + r'\s*\{([^}]*)\}', deckcss)
            return re.sub(r'\s+', '', m.group(1)) if m else ''
        sline = css_block(r'\.s-line')
        chk('background:var(--blue)' in sline, "상단 헤더 선은 main blue(--blue)",
            ".s-line이 --blue 배경이 아님")
        mint_mark = css_block(r'\.hl-mint-mark')
        mark_need = ['display:inline-block', 'background:var(--mint)', 'color:var(--white)',
                     'padding:03px1px', 'border-radius:0']
        missing_mark = [x for x in mark_need if x not in mint_mark]
        chk(not missing_mark, "민트 글자폭 강조(.hl-mint-mark) 계약 유지",
            f".hl-mint-mark 계약 누락: {missing_mark}")
        shape_mint = css_block(r'\.shape-mint')
        chk('background:var(--mint)!important' in shape_mint and 'color:var(--on-mint)!important' in shape_mint,
            "민트 도형 강조(.shape-mint) 계약 유지", ".shape-mint의 민트 fill/on-mint 글자 계약 누락")
        # (3c) 넘버 행 정렬 계약: .work-step은 배지 기준 텍스트 수직 중앙(2026-07-16)
        ws = css_block(r'\.work-step')
        chk('align-items:center' in ws, "넘버 행 수직 중앙(.work-step align-items:center) 유지",
            ".work-step이 align-items:center가 아님 — 원형 배지 대비 텍스트 중앙 정렬 규칙 위반")
        # (4) 민트 배지 셀렉터가 background:var(--mint) 유지 (다른 노드 셀렉터는 검사 안 함)
        badge_sels = [r'\.num-circle', r'\.work-step\s+\.n', r'\.pd-dot\.is-active']
        bad_badge = []
        for sel in badge_sels:
            m = re.search(r'(?:^|[}\n;,{])\s*' + sel + r'\s*(\{)', deckcss)
            block = ''
            if m:
                s = m.start(1)
                e = deckcss.find('}', s)
                block = re.sub(r'\s+', '', deckcss[s:e if e != -1 else len(deckcss)])
            if 'background:var(--mint)' not in block:
                bad_badge.append(sel.replace('\\', ''))
        chk(not bad_badge, "민트 배지 3종 background:var(--mint) 유지",
            f"민트 배지 색 이탈(background:var(--mint) 아님): {bad_badge}")

    # a11y: role="img"(코드 시각화)마다 비어있지 않은 aria-label
    role_img = len(re.findall(r'role="img"', html))
    labeled = len(re.findall(r'role="img"[^>]*aria-label="[^"]+"', html)) + \
              len(re.findall(r'aria-label="[^"]+"[^>]*role="img"', html))
    labeled = min(labeled, role_img)
    if role_img:
        chk(labeled >= role_img, f"코드시각화 aria 라벨: {labeled}/{role_img}",
            f"role=img {role_img}개 중 aria-label 있는 건 {labeled}개 — 나머지 라벨 없음(접근성)")

    # 색은 문법: 콘텐츠 슬라이드당 서로 다른 callout 색이 3종↑이면 색 남용 경고
    overcolor = []
    for i, (c, inr) in enumerate(content):
        cols = set(re.findall(r'callout\s+(blue|green|orange|red|yellow)', inr))
        if len(cols) >= 3:
            overcolor.append(str(i + 1) + ':' + '/'.join(sorted(cols)))
    chk(len(overcolor) == 0, "색 남용 없음(슬라이드당 callout 색 <3)",
        f"색 과다 슬라이드 {overcolor} — 경고색은 실제 의미가 있을 때만 사용하도록 원칙 재검토", warn=True)

    # ── 힌트 리빌(.hint-reveal): <summary> 존재 확인 (빈 disclosure = 접근성/사용성 위험) ──
    hint_blocks = re.findall(r'<details[^>]*class="[^"]*\bhint-reveal\b[^"]*"[^>]*>(.*?)</details>', html, re.S)
    if hint_blocks:
        no_summary = sum(1 for b in hint_blocks if '<summary' not in b)
        chk(no_summary == 0, f"힌트 리빌 {len(hint_blocks)}개 모두 <summary> 있음",
            f".hint-reveal {no_summary}개에 <summary> 없음 — 펼침 트리거 없는 빈 힌트(접근성)", warn=True)

    # ── 원고 아이콘 마커 누출 금지 (💬/🗣/👀는 조립 시 라우팅되고 최종 HTML엔 남으면 안 됨) ──
    #   <script>/<style> 제외한 마크업에서 코드포인트 탐지 → 남아 있으면 조립 실수(FAIL).
    body_wo_code = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', html, flags=re.S)
    leaked = [m for m in ('\U0001F4AC', '\U0001F5E3', '\U0001F440') if m in body_wo_code]  # 💬 🗣 👀
    leak_names = {'\U0001F4AC': '💬', '\U0001F5E3': '🗣', '\U0001F440': '👀'}
    chk(not leaked, "원고 아이콘 마커(💬/🗣/👀) 누출 0",
        f"아이콘 마커 {[leak_names[m] for m in leaked]} 최종 HTML에 잔존 — 조립 시 라우팅(주석/.hint-reveal) 후 제거해야 함")

    # 출력
    order = {"FAIL": 0, "WARN": 1, "PASS": 2}
    for lvl, msg in sorted(results, key=lambda r: order[r[0]]):
        mark = {"PASS": "✓", "WARN": "△", "FAIL": "✗"}[lvl]
        print(f"[{lvl}] {mark} {msg}")
    fails = sum(1 for l, _ in results if l == "FAIL")
    warns = sum(1 for l, _ in results if l == "WARN")
    print(f"\n요약: FAIL {fails} · WARN {warns} · PASS {len(results)-fails-warns}")
    print("※ 오버플로·콘솔에러·가독성(computed)은 브라우저 측정 필요: "
          "python -m http.server 후 슬라이드별 scrollWidth/Height ≤ client, 콘솔 에러 0 확인.")
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
