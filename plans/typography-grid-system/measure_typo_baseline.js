/* 타이포그래피·공간 기준선 전수 측정 — S0
 * 계획서: plans/typography-grid-system/PLAN.md §3 · §12-3
 *
 * 목적: 계획서 §3의 실측치를 「재현 가능하게」 다시 뽑는다. audit_render.js는
 *       잉크 점유율·바닥선·겹침을 보고, 이 스크립트는 그것이 보지 않는
 *       computed 타이포(폰트·행간·자간)와 앵커 좌표 분포를 본다.
 *
 * 실행 (반드시 이 순서 — 조건 하나라도 어기면 스크립트가 스스로 중단한다):
 *   1) 저장소 루트에서  python -m http.server 8799
 *   2) 브라우저로 http://localhost:8799/courses/<과목>/sessions/N주차/강의덱.html
 *   3) 뷰포트를 1280x720 이상으로 (덱 JS가 --scale을 창 크기로 계산한다)
 *   4) 콘솔:  await (await fetch('/plans/typography-grid-system/measure_typo_baseline.js')).text().then(eval)
 *
 * ⚠️ 측정 유효성(§12-3): 이 스크립트는 --scale을 1로 강제하고 슬라이드 rect가
 *    1280x720인지, Pretendard가 실제로 로드됐는지 확인한 뒤에만 측정한다.
 *    확인에 실패하면 { INVALID: ... }를 돌려주며 수치를 내지 않는다
 *    (과거 --scale=0 상태로 전 장 0이 나와 「문제 없음」으로 오판한 사고 있음).
 *    실제로 이 브라우저 창의 초기 상태가 --scale=0 이었다 — 항상 확인하라.
 */
(function () {
  var W = 1280, H = 720;
  var BODY_TOP = 118, BODY_BOT = 666, BODY_L = 64, BODY_R = 1216;

  /* ── 0) 측정 유효성 assert ─────────────────────────────────────── */
  document.documentElement.style.setProperty('--scale', 1);
  var slides = [].slice.call(document.querySelectorAll('.slide'));
  if (!slides.length) return JSON.stringify({ INVALID: 'no .slide found' });
  slides.forEach(function (x) { x.classList.remove('is-active'); });
  slides[0].classList.add('is-active');
  var probeRect = slides[0].getBoundingClientRect();
  var invalid = [];
  if (Math.abs(probeRect.width - W) > 0.5) invalid.push('slide width ' + probeRect.width + ' != 1280');
  if (Math.abs(probeRect.height - H) > 0.5) invalid.push('slide height ' + probeRect.height + ' != 720');
  var scaleVar = getComputedStyle(document.documentElement).getPropertyValue('--scale').trim();
  if (scaleVar !== '1') invalid.push('--scale=' + scaleVar);
  var pretendard = document.fonts ? document.fonts.check('16px Pretendard') : null;
  if (pretendard !== true) invalid.push('Pretendard not loaded (check=' + pretendard + ')');
  if (invalid.length) return JSON.stringify({ INVALID: invalid });

  /* ── 공통 판정 ────────────────────────────────────────────────── */
  /* 「텍스트 요소」= 자기 자식으로 비어 있지 않은 텍스트 노드를 가진 보이는 요소.
     audit_render.js의 hasOwnText 판정과 같은 정의를 쓴다(집계 정의 공유 — F13). */
  function ownText(e) {
    var s = '';
    for (var i = 0; i < e.childNodes.length; i++) {
      if (e.childNodes[i].nodeType === 3) s += e.childNodes[i].textContent;
    }
    return s.trim();
  }
  function visible(e) {
    var cs = getComputedStyle(e);
    if (cs.visibility === 'hidden' || cs.display === 'none' || parseFloat(cs.opacity) === 0) return null;
    return cs;
  }
  /* 헤더·페이지번호는 기존 검사들이 일괄 제외한다(§12-3: 기존 예외 승계) */
  function chromeExcluded(e) {
    return !!(e.closest('.s-head') || e.closest('.s-pageno') || e.classList.contains('s-pageno')
      || e.closest('.slide-num') || e.classList.contains('slide-num'));
  }
  /* §3-1의 「표·코드·헤더 제외」 */
  function tableOrCode(e) {
    return !!(e.closest('table') || e.closest('pre') || e.closest('code')
      || e.tagName === 'CODE' || e.tagName === 'PRE'
      || e.closest('.terminal-copy') || e.closest('.viz-code') || e.closest('.code-chart')
      || e.closest('.code-diagram'));
  }
  function bump(o, k) { o[k] = (o[k] || 0) + 1; }
  function bumpN(o, k, n) { o[k] = (o[k] || 0) + n; }
  function round1(v) { return Math.round(v * 10) / 10; }

  /* ── 집계 버킷 ────────────────────────────────────────────────── */
  var fontHist = {}, fontChars = {};
  var lhHist = {}, lhNormalCount = 0;
  var lsHist = {};
  var bigNoTracking = [];        // >=32px 인데 자체 letter-spacing 선언 없음(상속 -0.32px)
  var smallCount = 0, smallChars = 0;   // 22px 미만(표·코드·헤더 제외)
  var small20Long = 0;                  // 20px 이면서 25자 이상
  var smallByCls = {};
  var anchors = { titleL: {}, titleT: {}, bodyL: {}, imgL: {}, imgR: {}, imgT: {}, chartL: {}, chartT: {}, titleGap: {} };
  var allAnchorCoords = [];      // 스냅 비용 계산용
  var perSlide = [];
  var vizNarrow = 0, vizGate = 0, vizWide = 0;   // F13 — 세 정의

  function isChart(e) {
    return !!(e.matches('[class*="viz-"], [data-viz], canvas, .code-chart, .code-diagram')
      || (e.tagName === 'SVG' && !e.closest('.s-head')));
  }

  for (var i = 0; i < slides.length; i++) {
    slides.forEach(function (x) { x.classList.remove('is-active'); });
    var sl = slides[i];
    sl.classList.add('is-active');
    var sr = sl.getBoundingClientRect();
    var L = function (px) { return round1(px - sr.left); };
    var T = function (px) { return round1(px - sr.top); };

    var sSmall = 0, sBoxes = 0, sChars = 0;

    /* 1) 텍스트 요소 전수 — 폰트·행간·자간 */
    [].slice.call(sl.querySelectorAll('*')).forEach(function (e) {
      if (chromeExcluded(e)) return;
      var t = ownText(e);
      if (!t) return;
      var cs = visible(e);
      if (!cs) return;
      var fs = Math.round(parseFloat(cs.fontSize) * 10) / 10;
      bump(fontHist, fs);
      bumpN(fontChars, fs, t.length);
      sChars += t.length;

      var lhRaw = cs.lineHeight;
      if (lhRaw === 'normal') { lhNormalCount++; bump(lhHist, 'normal'); }
      else {
        var ratio = Math.round((parseFloat(lhRaw) / fs) * 100) / 100;
        bump(lhHist, ratio);
      }

      var ls = cs.letterSpacing === 'normal' ? 0 : Math.round(parseFloat(cs.letterSpacing) * 100) / 100;
      bump(lsHist, ls);
      if (fs >= 32 && Math.abs(ls - (-0.32)) < 0.01) {
        bigNoTracking.push({ s: sl.dataset.slide, c: (e.className || e.tagName).toString().slice(0, 28), fs: fs, ls: ls });
      }

      /* §3-1의 22px 미만 집계 — 표·코드·헤더 제외 */
      if (!tableOrCode(e) && fs < 22) {
        smallCount++; smallChars += t.length; sSmall++;
        var key = (e.className || e.tagName).toString().split(/\s+/)[0].slice(0, 24) || e.tagName;
        bump(smallByCls, key);
        if (Math.abs(fs - 20) < 0.01 && t.length >= 25) small20Long++;
      }
    });

    /* 2) 앵커 좌표 */
    var title = sl.querySelector('.s-title');
    var titleBottom = null;
    if (title) {
      var rt = title.getBoundingClientRect();
      if (rt.width > 1) {
        bump(anchors.titleL, Math.round(L(rt.left)));
        bump(anchors.titleT, Math.round(T(rt.top)));
        allAnchorCoords.push(L(rt.left), T(rt.top));
        titleBottom = T(rt.bottom);
      }
    }
    /* 본문 좌변 — 슬라이드 직계 본문 컨테이너의 첫 텍스트 블록 */
    var bodyEl = sl.querySelector('.s-body, .s-lead, .s-full > p');
    if (bodyEl) {
      var rb = bodyEl.getBoundingClientRect();
      if (rb.width > 1) { bump(anchors.bodyL, Math.round(L(rb.left))); allAnchorCoords.push(L(rb.left)); }
      if (titleBottom !== null) bump(anchors.titleGap, Math.round(T(rb.top) - titleBottom));
    }

    var seenChart = [];
    [].slice.call(sl.querySelectorAll('img, svg, canvas, [class*="viz-"], [data-viz], .code-chart, .code-diagram')).forEach(function (e) {
      if (e.closest('.s-head')) return;
      var r = e.getBoundingClientRect();
      if (r.width < 24 || r.height < 24) return;
      /* 중첩된 viz 컨테이너는 가장 바깥 것만 */
      for (var k = 0; k < seenChart.length; k++) if (seenChart[k].contains(e)) return;
      seenChart.push(e);
      var isImg = e.tagName === 'IMG';
      if (isImg) {
        bump(anchors.imgL, Math.round(L(r.left)));
        bump(anchors.imgR, Math.round(L(r.right)));
        bump(anchors.imgT, Math.round(T(r.top)));
        allAnchorCoords.push(L(r.left), L(r.right), T(r.top));
      } else if (isChart(e)) {
        bump(anchors.chartL, Math.round(L(r.left)));
        bump(anchors.chartT, Math.round(T(r.top)));
        allAnchorCoords.push(L(r.left), T(r.top));
      }
    });

    /* 3) 박스 수 — audit_render.js와 같은 판정(테두리 또는 배경 + 24x24 이상) */
    [].slice.call(sl.querySelectorAll('*')).forEach(function (e) {
      if (e.closest('.s-head') || e.classList.contains('asset-slot')) return;
      var cs = getComputedStyle(e);
      var bw = parseFloat(cs.borderTopWidth) + parseFloat(cs.borderLeftWidth);
      var bg = cs.backgroundColor;
      var hasBg = bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent';
      if (!(bw > 0 || hasBg)) return;
      var r = e.getBoundingClientRect();
      if (r.width < 24 || r.height < 24) return;
      sBoxes++;
    });

    /* 4) F13 — 시각자료 세 정의 */
    var nNarrow = [].slice.call(sl.querySelectorAll('img, svg, canvas')).filter(function (e) {
      if (e.closest('.s-head')) return false;
      var r = e.getBoundingClientRect();
      return r.width >= 6 && r.height >= 6;
    }).length;
    var logoRe = /(?:^|\s)(?:s-logo|brand-logo|favicon|cover-logo)(?:\s|$)/i;
    var nGate = [].slice.call(sl.querySelectorAll('[class*="viz-"], [data-viz], canvas')).length
      + [].slice.call(sl.querySelectorAll('img')).filter(function (e) {
        return !logoRe.test(e.className || '') && (e.getAttribute('aria-hidden') || '').toLowerCase() !== 'true';
      }).length;
    var nWide = nGate + [].slice.call(sl.querySelectorAll('svg')).filter(function (e) {
      if (e.closest('.s-head') || e.closest('[class*="viz-"]') || e.closest('[data-viz]')) return false;
      var r = e.getBoundingClientRect();
      return r.width >= 24 && r.height >= 24;
    }).length;
    if (nNarrow > 0) vizNarrow++;
    if (nGate > 0) vizGate++;
    if (nWide > 0) vizWide++;

    perSlide.push({
      i: i, id: sl.dataset.slide || '',
      small: sSmall, boxes: sBoxes, chars: sChars,
      vN: nNarrow, vG: nGate, vW: nWide
    });
  }

  /* ── 스냅 비용(§3-5) ──────────────────────────────────────────── */
  function snapCost(unit) {
    var moved = 0, maxMove = 0;
    allAnchorCoords.forEach(function (v) {
      var d = Math.abs(v - Math.round(v / unit) * unit);
      if (d > 0.5) { moved++; if (d > maxMove) maxMove = d; }
    });
    return { unit: unit, moved: moved, total: allAnchorCoords.length,
      pct: Math.round(moved / allAnchorCoords.length * 1000) / 10, max: round1(maxMove) };
  }

  /* ── 근-미스 군집(§3-4) — 지배값 ±1~5px인데 불일치 ─────────────── */
  function nearMiss(hist) {
    var keys = Object.keys(hist).map(Number).sort(function (a, b) { return a - b; });
    var clusters = [], cur = [];
    keys.forEach(function (k) {
      if (cur.length && k - cur[cur.length - 1] <= 5) cur.push(k);
      else { if (cur.length > 1) clusters.push(cur); cur = [k]; }
    });
    if (cur.length > 1) clusters.push(cur);
    return clusters.map(function (c) {
      return { range: c[0] + '~' + c[c.length - 1], values: c.length,
        items: c.reduce(function (s, k) { return s + hist[k]; }, 0) };
    }).filter(function (c) { return c.values >= 2; });
  }

  function sortHist(h) {
    return Object.keys(h).sort(function (a, b) { return h[b] - h[a]; })
      .map(function (k) { return k + ':' + h[k]; });
  }

  return JSON.stringify({
    meta: {
      url: location.pathname, slides: slides.length,
      scale: scaleVar, rect: [probeRect.width, probeRect.height], pretendard: pretendard,
      sheets: document.styleSheets.length
    },
    font: {
      kinds: Object.keys(fontHist).length,
      hist: sortHist(fontHist),
      chars: sortHist(fontChars),
      under22_elements: smallCount, under22_chars: smallChars,
      px20_over25chars: small20Long,
      under22_byClass: sortHist(smallByCls).slice(0, 25)
    },
    lineHeight: { normal: lhNormalCount, kinds: Object.keys(lhHist).length, hist: sortHist(lhHist) },
    letterSpacing: { hist: sortHist(lsHist), big32NoOwnTracking: bigNoTracking },
    anchors: {
      titleL: sortHist(anchors.titleL), titleT: sortHist(anchors.titleT),
      bodyL: sortHist(anchors.bodyL), titleGap: sortHist(anchors.titleGap),
      imgL: sortHist(anchors.imgL), imgR: sortHist(anchors.imgR), imgT: sortHist(anchors.imgT),
      chartL: sortHist(anchors.chartL), chartT: sortHist(anchors.chartT),
      kinds: { imgL: Object.keys(anchors.imgL).length, imgR: Object.keys(anchors.imgR).length,
        imgT: Object.keys(anchors.imgT).length, chartL: Object.keys(anchors.chartL).length,
        chartT: Object.keys(anchors.chartT).length, titleT: Object.keys(anchors.titleT).length },
      nearMiss: { chartT: nearMiss(anchors.chartT), titleT: nearMiss(anchors.titleT) }
    },
    snap: [snapCost(4), snapCost(8), snapCost(12)],
    visualsF13: { narrow_imgSvgCanvas: vizNarrow, gate_vizCanvasImg: vizGate, wide_plusStandaloneSvg: vizWide, of: slides.length },
    perSlide: perSlide
  });
})()
