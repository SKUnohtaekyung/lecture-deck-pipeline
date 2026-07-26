/*!
 * measure_render.js — 덱 렌더 실측 (R-VERIFY-01a·01c·01d)
 *
 * 정적 파서(verify_deck.py)가 못 재는 것만 잰다: 실제 렌더 위치·겹침·오버플로.
 * 브라우저 콘솔에 이 파일 전체를 붙여넣어 실행한다. 반환은 JSON 직렬화 가능한 객체.
 *
 * 사용법 (references/phases/08-검증.md 「렌더 실측 실행 절차」 참조):
 *   python -m http.server        # file:// 로 열지 않는다
 *   콘솔에 이 파일 주입 → 반환값의 scale 이 1 인지 **먼저** 확인
 *   measureRender()              # 활성 슬라이드 1장
 *   measureRender({all:true})    # 전 슬라이드 순회
 *
 * 판정하지 않는다 — 목록만 낸다. 주차 계약(sessions/_contracts 또는 동폴더
 * deck.contract.json)의 known_violations 와 대조하는 것은 사람 몫이다.
 */
(function (global) {
  'use strict';

  var DECK_W = 1280;
  var DECK_H = 720;
  var FLOOR = 666; // 하단 상한(720-54). R-TYPE-03.

  /* --- scale 환산 (R-VERIFY-01c) -------------------------------------------
   * 덱 루트에 transform: scale(var(--scale)) 가 걸려 있어, 창이 작으면 모든 rect
   * 가 축소돼 666px 기준을 자동 통과한다. 반드시 나눠서 덱 좌표로 환산하고,
   * 반환값에 scale 을 실어 1인지 확인할 수 있게 한다. */
  function readScale(slide) {
    var v = getComputedStyle(slide).getPropertyValue('--scale');
    var n = parseFloat(v);
    if (!isNaN(n) && n > 0) return n;
    // --scale 이 비어 있으면 실제 transform matrix 에서 역산한다.
    var t = getComputedStyle(slide).transform;
    if (t && t !== 'none') {
      var m = t.match(/matrix\(([^)]+)\)/);
      if (m) {
        var a = parseFloat(m[1].split(',')[0]);
        if (!isNaN(a) && a > 0) return a;
      }
    }
    // 마지막 폴백: 렌더 폭 / 설계 폭
    var r = slide.getBoundingClientRect();
    return r.width > 0 ? r.width / DECK_W : 1;
  }

  function rectIn(el, origin, scale) {
    var r = el.getBoundingClientRect();
    return {
      top: (r.top - origin.top) / scale,
      left: (r.left - origin.left) / scale,
      bottom: (r.bottom - origin.top) / scale,
      right: (r.right - origin.left) / scale,
      width: r.width / scale,
      height: r.height / scale
    };
  }

  function round(o) {
    var out = {};
    for (var k in o) out[k] = Math.round(o[k] * 10) / 10;
    return out;
  }

  /* --- 판정 대상 선별 (R-VERIFY-01d) ---------------------------------------
   * .s-full·.dv-hero 같은 전면 배경 래퍼는 원래 720px 를 차지하므로 그대로 재면
   * 전부 오탐이다. 자식 엘리먼트가 있으면서 자기 텍스트가 없는 노드는 제외하고,
   * 텍스트를 가진 노드와 IMG 만 판정 대상으로 삼는다. */
  function ownText(el) {
    var s = '';
    for (var i = 0; i < el.childNodes.length; i++) {
      var n = el.childNodes[i];
      if (n.nodeType === 3) s += n.nodeValue;
    }
    return s.replace(/\s+/g, ' ').trim();
  }

  function isLeafTarget(el) {
    if (el.tagName === 'IMG') return true;
    if (el.children.length === 0) return ownText(el).length > 0;
    return ownText(el).length > 0; // 자식이 있어도 자기 텍스트가 있으면 대상
  }

  function isHidden(el) {
    var cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') return true;
    var r = el.getBoundingClientRect();
    return r.width === 0 && r.height === 0;
  }

  function label(el) {
    var id = el.getAttribute('data-slide');
    var cls = (el.className && el.className.baseVal !== undefined)
      ? el.className.baseVal : (el.className || '');
    return el.tagName.toLowerCase()
      + (id ? '[' + id + ']' : '')
      + (cls ? '.' + String(cls).trim().split(/\s+/).slice(0, 2).join('.') : '');
  }

  function intersects(a, b) {
    return !(a.right <= b.left || b.right <= a.left ||
             a.bottom <= b.top || b.bottom <= a.top);
  }

  function measureSlide(slide) {
    var scale = readScale(slide);
    var origin = slide.getBoundingClientRect();

    var all = Array.prototype.slice.call(slide.querySelectorAll('*'));
    var targets = [];
    for (var i = 0; i < all.length; i++) {
      var el = all[i];
      if (isHidden(el)) continue;
      if (!isLeafTarget(el)) continue;
      targets.push({ el: el, rect: rectIn(el, origin, scale) });
    }

    // (c) 하단 666px 초과
    var belowFloor = [];
    // (f) 자체 스크롤 오버플로
    var overflow = [];
    for (var j = 0; j < targets.length; j++) {
      var t = targets[j];
      if (t.rect.bottom > FLOOR + 0.5) {
        belowFloor.push({
          node: label(t.el),
          bottom: Math.round(t.rect.bottom * 10) / 10,
          over: Math.round((t.rect.bottom - FLOOR) * 10) / 10,
          text: ownText(t.el).slice(0, 40)
        });
      }
    }
    for (var k = 0; k < all.length; k++) {
      var e = all[k];
      if (isHidden(e)) continue;
      if (e.scrollWidth > e.clientWidth + 1 || e.scrollHeight > e.clientHeight + 1) {
        overflow.push({
          node: label(e),
          scrollW: e.scrollWidth, clientW: e.clientWidth,
          scrollH: e.scrollHeight, clientH: e.clientHeight
        });
      }
    }

    // (d) 형제 정보 요소 교차
    var overlaps = [];
    for (var a = 0; a < targets.length; a++) {
      for (var b = a + 1; b < targets.length; b++) {
        var A = targets[a], B = targets[b];
        if (A.el.parentNode !== B.el.parentNode) continue; // 형제만
        if (A.el.contains(B.el) || B.el.contains(A.el)) continue;
        if (intersects(A.rect, B.rect)) {
          overlaps.push({ a: label(A.el), b: label(B.el),
                          aRect: round(A.rect), bRect: round(B.rect) });
        }
      }
    }

    // (e) figure 와 그 안 img 의 높이 불일치
    var figureMismatch = [];
    var figs = slide.querySelectorAll('figure');
    for (var f = 0; f < figs.length; f++) {
      var fig = figs[f];
      var img = fig.querySelector('img');
      if (!img || isHidden(fig) || isHidden(img)) continue;
      var fh = rectIn(fig, origin, scale).height;
      var ih = rectIn(img, origin, scale).height;
      if (Math.abs(fh - ih) > 2) {
        figureMismatch.push({
          node: label(fig),
          figureH: Math.round(fh * 10) / 10,
          imgH: Math.round(ih * 10) / 10,
          gap: Math.round((fh - ih) * 10) / 10,
          objectFit: getComputedStyle(img).objectFit
        });
      }
    }

    return {
      slide: slide.getAttribute('data-slide') || '(no data-slide)',
      scale: Math.round(scale * 1000) / 1000,
      measured: targets.length,
      belowFloor: belowFloor,
      overlaps: overlaps,
      figureMismatch: figureMismatch,
      overflow: overflow,
      clean: belowFloor.length === 0 && overlaps.length === 0 &&
             figureMismatch.length === 0 && overflow.length === 0
    };
  }

  function measureRender(opts) {
    opts = opts || {};
    var slides = Array.prototype.slice.call(document.querySelectorAll('.slide'));
    if (!slides.length) {
      return { error: '.slide 요소를 찾지 못했다 — 덱 페이지에서 실행하라.' };
    }

    var targets;
    if (opts.all) {
      targets = slides;
    } else {
      var active = slides.filter(function (s) {
        return getComputedStyle(s).display !== 'none';
      });
      targets = active.length ? [active[0]] : [slides[0]];
    }

    var results = [];
    for (var i = 0; i < targets.length; i++) {
      var s = targets[i];
      var restore = null;
      if (opts.all && getComputedStyle(s).display === 'none') {
        // 순회 모드: 숨은 장을 잠시 보이게 해서 실측한다(원상복구 보장).
        restore = s.style.display;
        s.style.display = 'block';
      }
      try {
        results.push(measureSlide(s));
      } finally {
        if (restore !== null) s.style.display = restore;
      }
    }

    var scales = results.map(function (r) { return r.scale; });
    var dirty = results.filter(function (r) { return !r.clean; });

    var out = {
      scale: scales.length === 1 ? scales[0] : scales,
      scaleIsOne: scales.every(function (n) { return Math.abs(n - 1) < 0.001; }),
      slidesMeasured: results.length,
      slidesWithFindings: dirty.length,
      totals: {
        belowFloor: results.reduce(function (n, r) { return n + r.belowFloor.length; }, 0),
        overlaps: results.reduce(function (n, r) { return n + r.overlaps.length; }, 0),
        figureMismatch: results.reduce(function (n, r) { return n + r.figureMismatch.length; }, 0),
        overflow: results.reduce(function (n, r) { return n + r.overflow.length; }, 0)
      },
      results: opts.all ? dirty : results
    };

    if (!out.scaleIsOne) {
      out.WARNING = 'scale ≠ 1 — 창을 1280×720 이상으로 키우고 다시 재라. '
        + '축소 뷰포트에서는 모든 rect가 줄어 666px 기준을 자동 통과한다(R-VERIFY-01c).';
    }
    return out;
  }

  global.measureRender = measureRender;
  if (typeof console !== 'undefined' && console.log) {
    console.log('measureRender() 준비됨 — 활성 장: measureRender() / 전 장: measureRender({all:true})');
  }
  return measureRender;
})(typeof window !== 'undefined' ? window : globalThis);
