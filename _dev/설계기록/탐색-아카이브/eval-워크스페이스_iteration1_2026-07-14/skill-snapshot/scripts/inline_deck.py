#!/usr/bin/env python3
"""inline_deck.py — 웹덱을 단일 파일로 배포 (CSS 인라인 + 이미지 base64). 의존성 0.

사용: python scripts/inline_deck.py <덱>.html [--offline]
  - 로컬 <link rel="stylesheet"> → <style>로 인라인 (deck.css·legibility·patterns 등)
  - 로컬 <img src> → data: URI (base64)
  - --offline: 외부(http) 링크(Pretendard CDN 등) 제거 → 시스템 폰트 폴백(맑은 고딕)
출력: <덱>_배포.html (원본 불변). 목표 용량 3~8MB.
"""
import sys, os, re, base64, argparse, mimetypes
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("deck")
    ap.add_argument("--offline", action="store_true", help="외부(http) 링크 제거(폰트 시스템 폴백)")
    a = ap.parse_args()

    base = os.path.dirname(os.path.abspath(a.deck))
    try:
        html = open(a.deck, encoding="utf-8").read()
    except OSError as e:
        print(f"[FAIL] {e}"); sys.exit(1)
    log = []

    def repl_link(m):
        tag, href = m.group(0), m.group(1)
        if href.startswith(("http://", "https://", "//")):
            if a.offline:
                log.append("외부 CSS/폰트 제거: " + href); return ""
            return tag  # CDN 유지
        path = os.path.normpath(os.path.join(base, href.split("?")[0]))
        if os.path.isfile(path):
            log.append("CSS 인라인: " + href)
            return "<style>\n" + open(path, encoding="utf-8").read() + "\n</style>"
        log.append("CSS 못찾음(유지): " + href); return tag

    # rel-before-href, href-before-rel 두 순서 모두
    html = re.sub(r'<link\b[^>]*rel="stylesheet"[^>]*href="([^"]+)"[^>]*>', repl_link, html)
    html = re.sub(r'<link\b[^>]*href="([^"]+)"[^>]*rel="stylesheet"[^>]*>', repl_link, html)

    def repl_img(m):
        tag, src = m.group(0), m.group(1)
        if src.startswith(("http://", "https://", "data:", "//")):
            return tag
        path = os.path.normpath(os.path.join(base, src.split("?")[0]))
        if os.path.isfile(path):
            mime = mimetypes.guess_type(path)[0] or "image/png"
            b = base64.b64encode(open(path, "rb").read()).decode("ascii")
            log.append("이미지 인라인: " + src + f" ({len(b)//1024}KB b64)")
            return tag.replace('src="' + src + '"', 'src="data:' + mime + ";base64," + b + '"')
        log.append("이미지 못찾음(유지): " + src); return tag

    html = re.sub(r'<img\b[^>]*src="([^"]+)"[^>]*>', repl_img, html)

    out = re.sub(r'\.html$', '_배포.html', a.deck)
    if out == a.deck:
        out = a.deck + "_배포.html"
    open(out, "w", encoding="utf-8").write(html)

    for l in log:
        print("  " + l)
    kb = os.path.getsize(out) // 1024
    print(f"\n생성: {out} ({kb}KB)")
    if kb > 8000:
        print("※ 8MB 초과 — 이미지 다운스케일 권장(Pillow 필요, 이 스크립트는 미포함).")
    if not a.offline and ("cdn.jsdelivr" in html or "http" in re.findall(r'<link[^>]*>', html).__str__()):
        print("※ Pretendard 폰트는 CDN 유지(온라인 필요). 완전 오프라인은 --offline.")


if __name__ == "__main__":
    main()
