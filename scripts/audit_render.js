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
    var boxes = 0, hollow = [], sparse = [];
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
      /* 껍데기: 글자 거의 없음 */
      if (t.length < 4 && !hasGfx) {
        hollow.push((e.className || e.tagName).toString().slice(0, 40));
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
    var broken = { overflow: [], belowFloor: [], overlap: [], wordBreak: [] };
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
         이제 바닥선 초과와 슬라이드 이탈을 나눠서 잡는다. */
      if (hasOwnText && by > BODY_BOT + 2 && by < 4000) {
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
    /* 겹침: 형제 레벨 블록끼리 면적 20% 이상 교차 */
    var blocks = [].slice.call(sl.querySelectorAll('.s-full > *, .s-full > * > *')).filter(function (e) {
      var r = e.getBoundingClientRect(); return r.width > 40 && r.height > 24;
    });
    for (var p = 0; p < blocks.length; p++) for (var q2 = p + 1; q2 < blocks.length; q2++) {
      var A = blocks[p], B = blocks[q2];
      if (A.contains(B) || B.contains(A)) continue;
      var ra = A.getBoundingClientRect(), rb = B.getBoundingClientRect();
      var ix = Math.max(0, Math.min(ra.right, rb.right) - Math.max(ra.left, rb.left));
      var iy = Math.max(0, Math.min(ra.bottom, rb.bottom) - Math.max(ra.top, rb.top));
      var inter = ix * iy;
      if (inter > 0.2 * Math.min(ra.width * ra.height, rb.width * rb.height)) {
        broken.overlap.push((A.className || A.tagName).toString().slice(0, 24) + '×' + (B.className || B.tagName).toString().slice(0, 24));
      }
    }

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
      hollow: hollow.length,
      sparse: sparse,
      broken: {
        ovf: broken.overflow.length, below: broken.belowFloor.length,
        off: broken.offSlide || 0,          /* 슬라이드(720px) 밖으로 나간 요소 — 최악 등급 */
        lap: broken.overlap.length, wb: broken.wordBreak.length,
        d: broken.belowFloor.concat(broken.overlap).slice(0, 3).concat(broken.wordBreak.slice(0, 2))
      },
      emptySlots: emptySlots
    });
  }
  return JSON.stringify(out);
})()
