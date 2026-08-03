/* 잉크 기반 전수 렌더 감사
 * 목적: "종료코드는 통과했는데 화면이 비어 보인다"를 기계로 잡는다.
 * 방법: 래퍼/배경을 세지 않고, 실제로 칠해지는 것(텍스트 rect · img/svg/canvas · 테두리 상자)만
 *       1280x720 슬라이드 로컬 좌표로 환산해 16px 격자에 래스터화한다.
 * 산출: 장별 잉크 점유율 · 본문영역 하단/우측 죽은 띠 · 빈 이미지 슬롯 · 껍데기 컨테이너.
 */
(function () {
  var CELL = 16, W = 1280, H = 720;
  var GX = W / CELL, GY = H / CELL;              // 80 x 45
  var BODY_TOP = 118, BODY_BOT = 666, BODY_L = 64, BODY_R = 1216;

  var slides = [].slice.call(document.querySelectorAll('.slide'));
  var out = [];

  function scaleOf(el) {
    var m = getComputedStyle(el).transform;
    if (!m || m === 'none') return 1;
    var n = m.match(/matrix\(([^,]+),/);
    return n ? parseFloat(n[1]) : 1;
  }

  /* ── 측정 유효성 assert (fail-closed · 2026-08-03 신설) ─────────────────
     이 검사가 없으면 「측정이 무효인 상태」와 「결함이 없는 상태」가 구별되지
     않는다. 실제 사고: --scale=0으로 전 장이 0으로 나왔는데 「문제 없음」으로
     읽혔다. 2026-08-03 재현 확인 — 브라우저 창이 작으면 덱 JS의 fit()이
     --scale을 0에 가깝게 계산하고, 그 상태에서 모든 rect가 0이 된다.
     ⚠️ 실패하면 수치를 내지 않고 { INVALID: [...] }를 돌려준다. 이 반환값을
        「결함 0」으로 집계하는 코드를 만들지 마라. */
  if (!slides.length) return JSON.stringify({ INVALID: ['no .slide element found'] });
  document.documentElement.style.setProperty('--scale', 1);
  slides.forEach(function (x) { x.classList.remove('is-active'); });
  slides[0].classList.add('is-active');
  var _pr = slides[0].getBoundingClientRect();
  var _invalid = [];
  if (Math.abs(_pr.width - W) > 0.5) _invalid.push('slide width ' + _pr.width + ' != ' + W);
  if (Math.abs(_pr.height - H) > 0.5) _invalid.push('slide height ' + _pr.height + ' != ' + H);
  var _sv = getComputedStyle(document.documentElement).getPropertyValue('--scale').trim();
  if (_sv && _sv !== '1') _invalid.push('--scale=' + _sv + ' (must be 1)');
  if (location.protocol === 'file:') _invalid.push('file:// 로 열렸다 — 로컬 HTTP 서버를 쓰라');
  if (document.fonts && document.fonts.check('16px Pretendard') !== true) {
    _invalid.push('Pretendard 미로드 — 줄바꿈·폭 측정이 재현되지 않는다');
  }
  if (_invalid.length) return JSON.stringify({ INVALID: _invalid });

  /* 그래픽 요소 판정 — 아래 「바닥선·이탈」 검사가 이미지를 통째로 놓치던
     버그(2026-08-03 규명)를 고치는 데 쓴다. */
  function isGraphic(e) {
    var t = e.tagName;
    return t === 'IMG' || t === 'SVG' || t === 'CANVAS' || t === 'VIDEO'
      || t === 'FIGURE' || t === 'PICTURE';
  }

  for (var i = 0; i < slides.length; i++) {
    slides.forEach(function (x) { x.classList.remove('is-active'); });
    var sl = slides[i];
    sl.classList.add('is-active');

    var sr = sl.getBoundingClientRect();
    var K = scaleOf(sl) || 1;
    var grid = new Uint8Array(GX * GY);

    function mark(r) {
      if (!r || r.width < 1 || r.height < 1) return;
      var x0 = (r.left - sr.left) / K, y0 = (r.top - sr.top) / K;
      var x1 = (r.right - sr.left) / K, y1 = (r.bottom - sr.top) / K;
      if (x1 < 0 || y1 < 0 || x0 > W || y0 > H) return;
      var cx0 = Math.max(0, Math.floor(x0 / CELL)), cx1 = Math.min(GX - 1, Math.floor((x1 - 0.01) / CELL));
      var cy0 = Math.max(0, Math.floor(y0 / CELL)), cy1 = Math.min(GY - 1, Math.floor((y1 - 0.01) / CELL));
      for (var y = cy0; y <= cy1; y++) for (var x = cx0; x <= cx1; x++) grid[y * GX + x] = 1;
    }

    /* 1) 텍스트 잉크 — Range로 실제 글자 상자만 */
    var walker = document.createTreeWalker(sl, NodeFilter.SHOW_TEXT, null);
    var tn, textLen = 0;
    while ((tn = walker.nextNode())) {
      if (!tn.textContent.trim()) continue;
      var pe = tn.parentElement;
      if (!pe) continue;
      var pcs = getComputedStyle(pe);
      if (pcs.visibility === 'hidden' || pcs.display === 'none' || parseFloat(pcs.opacity) === 0) continue;
      if (pe.closest('.s-head') || pe.classList.contains('slide-num') || pe.closest('.slide-num')) continue;
      textLen += tn.textContent.trim().length;
      var rng = document.createRange();
      rng.selectNodeContents(tn);
      var rects = rng.getClientRects();
      for (var k = 0; k < rects.length; k++) mark(rects[k]);
    }

    /* 2) 그래픽 잉크 — 실제 그림 요소만(빈 asset-slot 제외) */
    var gfx = 0;
    [].slice.call(sl.querySelectorAll('img, svg, canvas')).forEach(function (e) {
      if (e.closest('.s-head')) return;
      var r = e.getBoundingClientRect();
      if (r.width < 6 || r.height < 6) return;
      gfx++; mark(r);
    });

    /* 3) 테두리/채움이 있는 상자 — 윤곽만 잉크로 인정(면 전체를 채운 것으로 치지 않는다)
     *    + 박스 대비 정보량: 글자 1자가 차지하는 면적(px²/자). 클수록 "큰 상자에 내용 조금". */
    var boxes = 0, hollow = [], hollowBadge = [], sparse = [];
    [].slice.call(sl.querySelectorAll('*')).forEach(function (e) {
      if (e.closest('.s-head') || e.classList.contains('asset-slot')) return;
      var cs = getComputedStyle(e);
      var bw = parseFloat(cs.borderTopWidth) + parseFloat(cs.borderLeftWidth);
      var bg = cs.backgroundColor;
      var hasBg = bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent';
      if (!(bw > 0 || hasBg)) return;
      var r = e.getBoundingClientRect();
      if (r.width < 24 || r.height < 24) return;
      /* 같은 자리 중첩 상자는 바깥 것만 센다 */
      var pbox = e.parentElement && e.parentElement.closest('*');
      boxes++;
      /* 윤곽 4변만 마킹 */
      mark({ left: r.left, top: r.top, right: r.right, bottom: r.top + 2, width: r.width, height: 2 });
      mark({ left: r.left, top: r.bottom - 2, right: r.right, bottom: r.bottom, width: r.width, height: 2 });
      mark({ left: r.left, top: r.top, right: r.left + 2, bottom: r.bottom, width: 2, height: r.height });
      mark({ left: r.right - 2, top: r.top, right: r.right, bottom: r.bottom, width: 2, height: r.height });

      var t = (e.innerText || '').replace(/\s+/g, '');
      var hasGfx = !!e.querySelector('img,svg,canvas');
      /* 껍데기: 글자 거의 없음
         ⚠️ **번호 배지·표 헤더는 껍데기가 아니다**(2026-08-03 정정). 종전 정의로는
         2주차 186개·1주차 95개가 잡혔는데, 표본을 가르니 76%가 50×50px 미만이었고
         상위 클래스가 전부 번호 배지(.n 52 · .rm-n 26 · .wk-n · .an-num)와 표
         헤더(TH 15)·칩·화살표였다 — 전부 «글자가 적은 것이 정상»인 요소다.
         그 숫자를 밀도 신호로 읽으면 「박스로 화면을 채웠다」를 과대평가한다.
         작은 배지류는 hollowBadge로 따로 세고, hollow는 «내용이 들어가야 할
         크기인데 비어 있는 상자»만 남긴다. */
      if (t.length < 4 && !hasGfx) {
        var wl = r.width / K, hl = r.height / K;
        var cs2 = getComputedStyle(e);
        var isBadge = (wl <= 72 && hl <= 72)                    /* 배지·칩 크기 */
          || e.tagName === 'TH' || e.tagName === 'TD'           /* 표 셀 */
          || parseFloat(cs2.borderTopLeftRadius) >= Math.min(wl, hl) / 2 - 0.5;  /* 원형·pill */
        if (isBadge) hollowBadge.push((e.className || e.tagName).toString().slice(0, 40));
        else hollow.push((e.className || e.tagName).toString().slice(0, 40));
        return;
      }
      /* 저밀도: 상자 면적을 글자수로 나눈 값이 큰 것 (로컬 좌표 기준) */
      if (!hasGfx && t.length >= 4) {
        var areaLocal = (r.width / K) * (r.height / K);
        var perChar = areaLocal / t.length;
        if (perChar > 700 && areaLocal > 20000) {
          sparse.push({ c: (e.className || e.tagName).toString().slice(0, 32), a: Math.round(areaLocal), n: t.length, p: Math.round(perChar) });
        }
      }
    });

    /* 3b) 화면 깨짐 — 넘침 · 본문바닥 초과 · 요소 겹침 · 단어 중간 줄바꿈 */
    var broken = { overflow: [], belowFloor: [], overlap: [], overlapAbs: [], wordBreak: [] };
    [].slice.call(sl.querySelectorAll('*')).forEach(function (e) {
      /* .s-pageno는 바닥선(666) 아래가 정상 위치인 푸터다. 제외하지 않으면
         전 슬라이드가 `s-pageno@698`로 잡혀 진짜 결함이 묻힌다. */
      if (e.closest('.s-head') || e.classList.contains('s-pageno') || e.closest('.s-pageno')) return;
      if (e.scrollHeight - e.clientHeight > 4 && e.clientHeight > 20) {
        var ocs = getComputedStyle(e);
        if (ocs.overflow === 'hidden' || ocs.overflowY === 'hidden' || ocs.overflow === 'auto') {
          broken.overflow.push((e.className || e.tagName).toString().slice(0, 32) + ':' + (e.scrollHeight - e.clientHeight));
        }
      }
      var r = e.getBoundingClientRect();
      if (r.height < 4) return;
      var by = (r.bottom - sr.top) / K;
      var hasOwnText = false;
      for (var q = 0; q < e.childNodes.length; q++) {
        if (e.childNodes[q].nodeType === 3 && e.childNodes[q].textContent.trim()) hasOwnText = true;
      }
      /* ⚠️ 2026-07-31 버그 수정: 종전에는 `by < H`(=720) 조건이 붙어 있어
         슬라이드 밖으로 완전히 나간 요소(y > 720)를 오히려 놓쳤다. 가장 심각한
         경우가 검출에서 빠져 워커들이 "바닥선 초과 0"을 보고하는 원인이 됐다
         (실측: A5F2 y=835 · C4-15 y=1200이 전부 무시됐다).
         이제 바닥선 초과와 슬라이드 이탈을 나눠서 잡는다.

         ⚠️ 2026-08-03 버그 수정 — 두 번째 사각지대: 판정 조건이 `hasOwnText`
         **하나뿐**이라 자기 텍스트 노드가 없는 <img>·<svg>·<figure>는 아무리
         아래로 내려가도 **영원히 잡히지 않았다.** MEMORY는 "텍스트를 가진
         노드와 IMG만 판정 대상"이라 규정했는데 IMG 분기가 구현된 적이 없다.
         그래서 「이탈 0」·「바닥선 초과 0」이 이미지에 대해서는 아무것도
         증명하지 못하는 값이었다. 그래픽 요소를 판정 대상에 넣는다. */
      /* 전면 배경(full-bleed)은 예외 — 슬라이드 전체를 덮는 것이 설계다.
         「바닥선 아래로 내려간 콘텐츠」가 아니라 캔버스 자체이기 때문.
         판정: 슬라이드 폭의 95% 이상 + 상단이 0에 붙어 있음. 이 조건을
         만족하지 않는 히어로·삽화는 예외로 봐주지 않는다(1주차 실측에서
         s00-hero@697 · intro-ai-art@674 · task-shot IMG@683이 여기 걸린다). */
      var gfxNode = isGraphic(e) && r.width >= 6 && r.height >= 6;
      if (gfxNode) {
        var gx = (r.left - sr.left) / K, gy = (r.top - sr.top) / K;
        if (r.width / K >= W * 0.95 && gy <= 2 && gx <= 2) gfxNode = false;
      }
      if ((hasOwnText || gfxNode) && by > BODY_BOT + 2 && by < 4000) {
        var tag = by > H ? '@이탈' : '@';
        broken.belowFloor.push((e.className || e.tagName).toString().slice(0, 32) + tag + Math.round(by));
        if (by > H) broken.offSlide = (broken.offSlide || 0) + 1;
      }
    });
    /* 단어 중간 줄바꿈: 텍스트 노드가 2줄 이상이고 줄 경계가 공백이 아닌 경우 근사 검출 */
    var walker2 = document.createTreeWalker(sl, NodeFilter.SHOW_TEXT, null);
    var t2;
    while ((t2 = walker2.nextNode())) {
      var s2 = t2.textContent;
      if (!s2.trim() || s2.trim().length < 6) continue;
      if (t2.parentElement && t2.parentElement.closest('.s-head')) continue;
      var rg = document.createRange(); rg.selectNodeContents(t2);
      var rcs = rg.getClientRects();
      if (rcs.length < 2) continue;
      /* 각 줄의 끝 글자 인덱스를 찾아 그 다음 글자가 공백인지 본다 */
      for (var li = 0; li < rcs.length - 1; li++) {
        var lo = 0, hi = s2.length, cut = -1;
        while (lo < hi) {
          var mid = (lo + hi) >> 1;
          var r2 = document.createRange();
          r2.setStart(t2, 0); r2.setEnd(t2, mid);
          var rr = r2.getClientRects();
          if (rr.length > li + 1) { hi = mid; } else { lo = mid + 1; }
        }
        cut = lo - 1;
        if (cut > 0 && cut < s2.length - 1) {
          var a1 = s2[cut - 1], b1 = s2[cut];
          if (a1 && b1 && !/[\s​]/.test(a1) && !/[\s​]/.test(b1) && /[가-힣A-Za-z0-9]/.test(a1) && /[가-힣A-Za-z0-9]/.test(b1)) {
            broken.wordBreak.push(s2.slice(Math.max(0, cut - 6), cut) + '/' + s2.slice(cut, cut + 6));
          }
        }
      }
    }
    /* 겹침: 콘텐츠 블록끼리 면적 20% 이상 교차
       ⚠️ 2026-08-03 버그 수정: 종전에는 `.s-full > *, .s-full > * > *`로 **2단계까지만**
          훑었다. 두 가지 결과 — ① `.s-full`이 없는 슬라이드(표지·간지·아젠다·마무리·
          `.s-body-wrap`/`.center-msg` 계열)는 겹침 검사가 **아예 돌지 않았다**
          ② 3단계 이상 중첩된 요소는 보이지 않았는데, 사용자가 두 번 지적한
          「차트×텍스트 겹침」이 대개 그 깊이다.
          이제 슬라이드 전체를 깊이 제한 없이 훑되, 다음으로 오탐을 막는다:
            · 콘텐츠 블록만 본다(자기 텍스트가 있거나 그래픽인 것)
            · 조상-자손 관계는 건너뛴다(중첩은 겹침이 아니다)
            · 장식(aria-hidden)·헤더·페이지번호는 제외

       ⚠️ **인라인 요소를 제외하는 이유(실측으로 확정)**: `<b>`·`<strong>`·`<span>`은
          줄바꿈되면 여러 줄에 걸친 **합집합 상자**가 rect로 나온다. 같은 줄에
          나란히 있는 두 인라인의 상자는 글자가 전혀 겹치지 않는데도 100%
          교차한다. 깊이 제한만 풀고 인라인을 넣었더니 2주차에서 잡힌 7건이
          **전부 오탐**이었다(C1-N2 2 · C4-2 1 · C4-13 2 = 인라인 합집합 상자,
          C5-UIUX-1 2 = 빙산 그림 위 의도된 라벨). 그래서 두 겹으로 좁힌다:
            ① 인라인(display:inline)은 제외 — 상자가 의미를 갖지 않는다
            ② 절대배치(absolute/fixed)가 낀 쌍은 `lapAbs`로 따로 센다 —
               「그림 위 라벨」처럼 의도된 겹침이 대부분이라 참고치로만 둔다.
               정상 흐름(normal flow) 블록끼리의 겹침만 `lap`으로 판정한다 —
               흐름 블록은 원래 겹칠 수 없으므로 겹치면 진짜 결함이다. */
    function overlapCandidate(e) {
      if (e.closest('.s-head') || e.closest('.s-pageno') || e.classList.contains('s-pageno')) return null;
      if (e.getAttribute('aria-hidden') === 'true' || e.closest('[aria-hidden="true"]')) return null;
      var cs = getComputedStyle(e);
      if (cs.visibility === 'hidden' || cs.display === 'none' || parseFloat(cs.opacity) === 0) return null;
      if (cs.display === 'inline') return null;                 /* ① */
      var own = false;
      for (var c = 0; c < e.childNodes.length; c++) {
        if (e.childNodes[c].nodeType === 3 && e.childNodes[c].textContent.trim()) own = true;
      }
      if (!own && !isGraphic(e)) return null;
      var r = e.getBoundingClientRect();
      if (!(r.width > 40 && r.height > 24)) return null;
      e.__abs = (cs.position === 'absolute' || cs.position === 'fixed');   /* ② */
      return e;
    }
    var blocks = [].slice.call(sl.querySelectorAll('*')).map(overlapCandidate).filter(Boolean);
    for (var p = 0; p < blocks.length; p++) for (var q2 = p + 1; q2 < blocks.length; q2++) {
      var A = blocks[p], B = blocks[q2];
      if (A.contains(B) || B.contains(A)) continue;
      var ra = A.getBoundingClientRect(), rb = B.getBoundingClientRect();
      var ix = Math.max(0, Math.min(ra.right, rb.right) - Math.max(ra.left, rb.left));
      var iy = Math.max(0, Math.min(ra.bottom, rb.bottom) - Math.max(ra.top, rb.top));
      var inter = ix * iy;
      if (inter > 0.2 * Math.min(ra.width * ra.height, rb.width * rb.height)) {
        var pair = (A.className || A.tagName).toString().slice(0, 24) + '×' + (B.className || B.tagName).toString().slice(0, 24);
        if (A.__abs || B.__abs) broken.overlapAbs.push(pair);   /* 참고치 — 의도된 오버레이가 많다 */
        else broken.overlap.push(pair);                          /* 판정 — 흐름 블록은 겹칠 수 없다 */
      }
    }
    blocks.forEach(function (e) { delete e.__abs; });

    /* 4) 빈 이미지 슬롯 */
    var emptySlots = [].slice.call(sl.querySelectorAll('.asset-slot')).filter(function (e) {
      return !e.querySelector('img,svg,canvas');
    }).map(function (e) {
      var r = e.getBoundingClientRect();
      return {
        cls: (e.className || '').replace('asset-slot ', ''),
        w: Math.round(r.width / K), h: Math.round(r.height / K),
        x: Math.round((r.left - sr.left) / K), y: Math.round((r.top - sr.top) / K)
      };
    });

    /* 5) 점유율 집계 — 본문영역(118~666 x 64~1216) 기준 */
    function cov(x0, y0, x1, y1) {
      var a = 0, b = 0;
      var cx0 = Math.floor(x0 / CELL), cx1 = Math.floor((x1 - 1) / CELL);
      var cy0 = Math.floor(y0 / CELL), cy1 = Math.floor((y1 - 1) / CELL);
      for (var y = cy0; y <= cy1; y++) for (var x = cx0; x <= cx1; x++) { b++; if (grid[y * GX + x]) a++; }
      return b ? a / b : 0;
    }

    /* 잉크가 실제로 닿는 최하단 y (본문영역 안) */
    var lastRow = BODY_TOP;
    for (var y = Math.floor(BODY_TOP / CELL); y <= Math.floor((BODY_BOT - 1) / CELL); y++) {
      for (var x = Math.floor(BODY_L / CELL); x <= Math.floor((BODY_R - 1) / CELL); x++) {
        if (grid[y * GX + x]) { lastRow = (y + 1) * CELL; break; }
      }
    }
    var lastCol = BODY_L;
    for (var x2 = Math.floor(BODY_L / CELL); x2 <= Math.floor((BODY_R - 1) / CELL); x2++) {
      for (var y2 = Math.floor(BODY_TOP / CELL); y2 <= Math.floor((BODY_BOT - 1) / CELL); y2++) {
        if (grid[y2 * GX + x2]) { lastCol = (x2 + 1) * CELL; break; }
      }
    }

    var title = (sl.querySelector('.s-title') || {}).innerText || '';
    var kind = /M[0-9]$/.test(sl.dataset.slide || '') ? '교시'
      : /이렇게 배웁니다|이렇게배웁니다/.test(title) ? '이렇게배웁니다'
        : /실습|해보기|따라하기|미션/.test(title) ? '실습'
          : /^P[0-9]/.test(sl.dataset.slide || '') ? '파트표지' : '설명';

    out.push({
      i: i,
      id: sl.dataset.slide,
      kind: kind,
      title: title.replace(/\s+/g, ' ').slice(0, 34),
      ink: +cov(BODY_L, BODY_TOP, BODY_R, BODY_BOT).toFixed(3),
      deadBottom: Math.max(0, BODY_BOT - lastRow),
      deadRight: Math.max(0, BODY_R - lastCol),
      txt: textLen,
      gfx: gfx,
      boxes: boxes,
      hollow: hollow.length,          /* 내용이 들어가야 할 크기인데 비어 있는 상자 */
      hollowBadge: hollowBadge.length, /* 번호 배지·표 셀·칩 — 정상. 밀도 신호로 쓰지 마라 */
      sparse: sparse,
      broken: {
        ovf: broken.overflow.length, below: broken.belowFloor.length,
        off: broken.offSlide || 0,          /* 슬라이드(720px) 밖으로 나간 요소 — 최악 등급 */
        lap: broken.overlap.length,          /* 흐름 블록끼리 겹침 — 판정 대상 */
        lapAbs: broken.overlapAbs.length,    /* 절대배치가 낀 겹침 — 참고치(의도된 오버레이 다수) */
        wb: broken.wordBreak.length,
        d: broken.belowFloor.concat(broken.overlap).slice(0, 3).concat(broken.wordBreak.slice(0, 2))
      },
      emptySlots: emptySlots
    });
  }
  return JSON.stringify(out);
})()
