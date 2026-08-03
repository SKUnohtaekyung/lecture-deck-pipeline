/* 렌더 감사 한 번에 — audit_render.js + audit_typography.js를 함께 돌리고
 * `run_deck_checks.py`가 읽는 **압축 증거**를 만든다.
 *
 * 왜 압축본인가: 두 감사기의 원본 출력은 합쳐서 50KB가 넘어 사람이 콘솔에서
 * 복사해 파일로 옮기기 어렵다. 러너가 판정에 실제로 쓰는 것은 집계값과 위반
 * 목록뿐이므로, 그만 담은 1~3KB짜리 증거를 만든다.
 * (원본 전체가 필요하면 두 스크립트를 따로 실행하라 — 이 파일은 러너용이다)
 *
 * 사용:
 *   1) 저장소 루트에서  python -m http.server 8799
 *   2) 브라우저로 덱을 연다 — 창은 1280x720 이상(작으면 --scale이 0이 된다)
 *   3) 콘솔:
 *        await (await fetch('/scripts/audit_all.js')).text().then(eval)
 *      → 출력된 JSON을 sessions/_verify/<주차>/deck-audit.json 으로 저장
 *   4) python scripts/run_deck_checks.py <주차> --parts N
 *
 * ⚠️ 두 감사기 중 하나라도 INVALID면 이 파일도 INVALID를 그대로 돌려준다.
 *    러너는 INVALID를 「결함 0」으로 세지 않고 실패로 처리한다.
 */
(async function () {
  async function load(path) {
    var src = await (await fetch(path + '?v=' + Date.now())).text();
    /* 두 감사기 모두 «마지막 표현식이 JSON 문자열»인 IIFE다 */
    return JSON.parse(eval(src));
  }

  var render, typo;
  try {
    render = await load('/scripts/audit_render.js');
    typo = await load('/scripts/audit_typography.js');
  } catch (e) {
    return JSON.stringify({ INVALID: ['감사기 로드 실패: ' + (e && e.message || e)] }, null, 1);
  }

  if (render && render.INVALID) return JSON.stringify({ INVALID: render.INVALID }, null, 1);
  if (typo && typo.INVALID) return JSON.stringify({ INVALID: typo.INVALID }, null, 1);

  var slides = Array.isArray(render) ? render : [];
  var agg = { below: 0, off: 0, lap: 0, lapAbs: 0, wb: 0, ovf: 0, slots: 0,
    hollow: 0, hollowBadge: 0, sparse: 0 };
  var offenders = [];
  /* ⚠️ 밀도 지표를 압축본에 반드시 싣는다(2026-08-03 신설).
     종전 압축본은 broken 계열과 hollow만 실어, 러너가 읽는 증거에
     **저밀도를 판정할 수치가 하나도 없었다.** audit_render.js는 ink·sparse·
     deadBottom·deadRight를 이미 재고 있었는데 러너까지 오지 않았다 —
     「재는데 아무도 안 보는」 상태였다. */
  var inks = [], lowInk = [], deadZones = [], sparseSlides = [];
  slides.forEach(function (s) {
    var b = (s && s.broken) || {};
    agg.below += b.below || 0;
    agg.off += b.off || 0;
    agg.lap += b.lap || 0;
    agg.lapAbs += b.lapAbs || 0;
    agg.wb += b.wb || 0;
    agg.ovf += b.ovf || 0;
    agg.hollow += (s && s.hollow) || 0;
    agg.hollowBadge += (s && s.hollowBadge) || 0;
    agg.sparse += ((s && s.sparse) || []).length;
    agg.slots += ((s && s.emptySlots) || []).length;

    if (typeof s.ink === 'number') {
      inks.push(s.ink);
      if (s.ink < 0.22) {
        lowInk.push({ id: s.id, kind: s.kind, ink: s.ink, boxes: s.boxes,
          gfx: s.gfx, txt: s.txt });
      }
    }
    if ((s.deadBottom || 0) >= 96 || (s.deadRight || 0) >= 200) {
      deadZones.push({ id: s.id, bottom: s.deadBottom || 0, right: s.deadRight || 0 });
    }
    if (((s && s.sparse) || []).length) {
      sparseSlides.push({ id: s.id, n: s.sparse.length,
        worst: s.sparse.slice().sort(function (x, y) { return y.p - x.p; })[0] });
    }

    if ((b.below || 0) + (b.off || 0) + (b.lap || 0) + (b.wb || 0) + ((s.emptySlots || []).length)) {
      offenders.push({
        id: s.id, below: b.below || 0, off: b.off || 0, lap: b.lap || 0,
        wb: b.wb || 0, slots: (s.emptySlots || []).length,
        d: (b.d || []).filter(Boolean).slice(0, 3)
      });
    }
  });
  inks.sort(function (a, b) { return a - b; });
  function pct(p) { return inks.length ? inks[Math.min(inks.length - 1, Math.floor(inks.length * p))] : null; }
  var density = {
    ink: { min: inks[0], p10: pct(0.1), median: pct(0.5), p90: pct(0.9), max: inks[inks.length - 1] },
    /* ★ 「박스는 많은데 시각자료가 없다」 — 가장 위험한 조합 */
    boxHeavyNoVisualCount: slides.filter(function (s) {
      return (s.boxes || 0) >= 4 && (s.gfx || 0) === 0;
    }).length,
    boxHeavyNoVisual: slides.filter(function (s) {
      return (s.boxes || 0) >= 4 && (s.gfx || 0) === 0;
    }).sort(function (a, b) { return (b.boxes || 0) - (a.boxes || 0); })
      .slice(0, 20).map(function (s) { return [s.id, s.boxes, s.ink]; }),
    lowInk: lowInk.slice(0, 20),
    deadZones: deadZones.slice(0, 20),
    sparseSlides: sparseSlides.slice(0, 20)
  };

  var nmTotal = 0, clashTotal = 0, nmByAxis = {};
  var nmSrc = ((typo.anchors || {}).nearMiss) || {};
  Object.keys(nmSrc).forEach(function (k) {
    var a = nmSrc[k] || {};
    var n = a.nearMissCount || 0;
    var c = a.dominantClashCount || 0;
    nmTotal += n;
    clashTotal += c;
    nmByAxis[k] = { dominants: a.dominants || [], nearMiss: n,
      /* 지배값끼리 5px 이내 — 「같은 자리에 규격이 둘」. 근-미스보다 심한 형태다 */
      dominantClashes: c, clashItems: (a.dominantClashes || []).slice(0, 5) };
  });

  return JSON.stringify({
    schema: 'deck-audit/1',
    /* 언제·무엇을 쟀는지 — 러너가 «덱보다 낡았는가»를 파일 mtime으로 보지만,
       사람이 파일만 열어도 대상이 무엇인지 알 수 있게 함께 적는다 */
    url: location.pathname,
    slideCount: slides.length,
    render: { totals: agg, offenders: offenders, density: density },
    /* 장별 원자료 — 기준판 비교 도구(compare_baseline_panel.py)가 읽는다.
       ⚠️ 객체가 아니라 **배열 행**으로 싣는다. 110장을 객체로 담으면 증거가
          30KB를 넘어 콘솔에서 복사해 파일로 옮기기가 어려워진다(실측). */
    perSlideCols: ["id", "kind", "ink", "boxes", "gfx", "txt", "hollow", "deadBottom", "deadRight"],
    perSlide: slides.map(function (s) {
      return [s.id, s.kind, Math.round((s.ink || 0) * 100) / 100, s.boxes, s.gfx,
        s.txt, s.hollow, s.deadBottom, s.deadRight];
    }),
    typography: {
      textElements: (typo.meta || {}).textElements,
      fontFloor: { count: (typo.fontFloor || {}).count, byRole: (typo.fontFloor || {}).byRole,
        worst: ((typo.fontFloor || {}).worst || []).slice(0, 12) },
      tracking: { count: (typo.tracking || {}).count, byClass: (typo.tracking || {}).byClass },
      lineHeightNormal: (typo.lineHeightNormal || {}).count,
      nearMissAnchors: { total: nmTotal, dominantClashTotal: clashTotal, byAxis: nmByAxis }
    }
  });
  /* ⚠️ 들여쓰기를 넣지 않는다 — 110장 × 9열이면 들여쓴 JSON이 30KB를 넘어
     콘솔에서 옮기기 어려워진다(실측 30,111자 → 압축 시 1/3). 이 파일은 사람이
     읽는 것이 아니라 run_deck_checks.py·compare_baseline_panel.py가 읽는다.
     사람은 러너 요약을 본다. */
})()
