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
  /* 1순위 표현이 차트·다이어그램인 정보 모양(kit/charts/by-shape.md 기준).
     comparison은 표·2열 패널도 정당한 1순위라 여기 넣지 않는다 — 오탐이 된다. */
  var VISUAL_FIRST_SHAPES = ['numeric', 'structure', 'containment', 'mapping', 'flow'];

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
    hollow: 0, hollowBadge: 0, sparse: 0,
    /* 2026-08-18 신설 — 상자 채움(방향 있는 3지표 + 폭)과 가려짐 */
    occl: 0, stretchX: 0, stretchY: 0, wideEmpty: 0, lowFill: 0, ragged: 0 };
  var offenders = [];
  /* ⚠️ 밀도 지표를 압축본에 반드시 싣는다(2026-08-03 신설).
     종전 압축본은 broken 계열과 hollow만 실어, 러너가 읽는 증거에
     **저밀도를 판정할 수치가 하나도 없었다.** audit_render.js는 ink·sparse·
     deadBottom·deadRight를 이미 재고 있었는데 러너까지 오지 않았다 —
     「재는데 아무도 안 보는」 상태였다. */
  var inks = [], deadZones = [], sparseSlides = [], boxFillSlides = [];
  slides.forEach(function (s) {
    var b = (s && s.broken) || {};
    agg.below += b.below || 0;
    agg.off += b.off || 0;
    agg.lap += b.lap || 0;
    agg.lapAbs += b.lapAbs || 0;
    agg.wb += b.wb || 0;
    agg.ovf += b.ovf || 0;
    agg.occl += b.occl || 0;
    var bf = (s && s.boxFill) || {};
    agg.stretchX += bf.stretchX || 0;
    agg.stretchY += bf.stretchY || 0;
    agg.wideEmpty += bf.wideEmpty || 0;
    agg.lowFill += bf.lowFill || 0;
    agg.ragged += bf.ragged || 0;
    agg.hollow += (s && s.hollow) || 0;
    agg.hollowBadge += (s && s.hollowBadge) || 0;
    agg.sparse += ((s && s.sparse) || []).length;
    agg.slots += ((s && s.emptySlots) || []).length;

    if (typeof s.ink === 'number' && !s.fixed) inks.push(s.ink);
    if ((s.deadBottom || 0) >= 96 || (s.deadRight || 0) >= 200) {
      deadZones.push({ id: s.id, bottom: s.deadBottom || 0, right: s.deadRight || 0 });
    }
    if (((s && s.sparse) || []).length) {
      sparseSlides.push({ id: s.id, n: s.sparse.length,
        worst: s.sparse.slice().sort(function (x, y) { return y.p - x.p; })[0] });
    }

    if ((b.below || 0) + (b.off || 0) + (b.lap || 0) + (b.wb || 0) + (b.occl || 0)
        + ((s.emptySlots || []).length)) {
      offenders.push({
        id: s.id, below: b.below || 0, off: b.off || 0, lap: b.lap || 0,
        occl: b.occl || 0, wb: b.wb || 0, slots: (s.emptySlots || []).length,
        d: (b.d || []).filter(Boolean).slice(0, 3).concat((s.occlD || []).slice(0, 2))
      });
    }
    /* 상자 채움 — 어느 장이 어느 방향으로 늘어났는지 사람이 바로 보게 남긴다 */
    if (bf.stretchX || bf.stretchY || bf.wideEmpty || bf.lowFill || bf.ragged) {
      boxFillSlides.push({ id: s.id, wide: bf.wideEmpty || 0, x: bf.stretchX || 0,
        y: bf.stretchY || 0, f: bf.lowFill || 0, rag: bf.ragged || 0,
        d: (bf.d || []).slice(0, 4) });
    }
  });
  inks.sort(function (a, b) { return a - b; });
  function pct(p) { return inks.length ? inks[Math.min(inks.length - 1, Math.floor(inks.length * p))] : null; }
  var body = slides.filter(function (s) { return !s.fixed; });
  var medianInk = pct(0.5), p10Ink = pct(0.1);
  var avgBoxes = body.length
    ? body.reduce(function (a, s) { return a + (s.boxes || 0); }, 0) / body.length : 0;

  /* ⚠️ **절대 임계로 「저밀도」를 정의하지 않는다**(2026-08-03 정정).
     처음엔 `ink < 0.22`를 썼는데, 2주차 최솟값이 0.257이라 **영원히 발동하지
     않는 죽은 신호**였다. 「재는데 아무도 못 보는」 문제를 고치면서 「발동하지
     않는 검사」를 새로 만든 셈이다.
     대신 **이 덱 안에서의 상대 위치**로 본다 — 「하위 10%」는 어느 덱에서나
     존재하므로 항상 볼거리가 나온다. 이건 **판정이 아니라 보고**다:
     「이 덱에서 가장 얇은 장들」이지 「기준 미달」이 아니다.
     ⚠️ 이 값을 게이트 임계로 굳히지 마라 — 그러면 그 덱 수준으로 수렴한다. */
  var thinnest = body.slice().sort(function (a, b) { return (a.ink || 0) - (b.ink || 0); })
    .slice(0, 10).map(function (s) { return [s.id, s.ink, s.boxes, s.gfx, s.txt]; });

  function boxHeavy(s) { return (s.boxes || 0) >= 4 && (s.gfx || 0) === 0; }
  var density = {
    ink: { min: inks[0], p10: p10Ink, median: medianInk, p90: pct(0.9), max: inks[inks.length - 1] },
    avgBoxes: Math.round(avgBoxes * 10) / 10,
    /* ★ 「박스는 많은데 시각자료가 없다」 — 가장 위험한 조합 */
    boxHeavyNoVisualCount: body.filter(boxHeavy).length,
    boxHeavyNoVisual: body.filter(boxHeavy)
      .sort(function (a, b) { return (b.boxes || 0) - (a.boxes || 0); })
      .slice(0, 20).map(function (s) { return [s.id, s.boxes, s.ink]; }),
    /* ★ 「잉크는 낮은데 박스는 많다」 — 큰 빈 상자로 채운 신호 */
    lowInkManyBoxes: body.filter(function (s) {
      return (s.ink || 0) < medianInk && (s.boxes || 0) > avgBoxes;
    }).map(function (s) { return [s.id, s.ink, s.boxes]; }).slice(0, 20),
    /* ★ 교시 로드맵에 시각자료 0 — 2주차에서 5장 전부 이 상태였다 */
    roadmapNoVisual: body.filter(function (s) {
      return s.kind === '교시' && (s.gfx || 0) === 0;
    }).map(function (s) { return [s.id, s.boxes]; }),
    /* ★ 「정보 모양의 1순위 표현이 시각물인데 시각자료가 0」
       — numeric·structure·containment·mapping·flow는 차트·다이어그램이 1순위다
         (kit/charts/by-shape.md). 그 모양인데 시각자료가 없으면 글·박스로 푼 것이다.
       ⚠️ **모양이 기록돼 있어야 계산된다.** 슬라이드에 `data-shape`가 없으면
          이 신호는 «0건»이 아니라 **측정 불가**다. 둘을 섞지 않으려고
          shapeCoverage로 «몇 장이 모양을 기록했는가»를 함께 낸다.
          0/N이면 이 신호를 「깨끗하다」로 읽지 마라 — 아무것도 안 본 것이다. */
    shapeCoverage: [body.filter(function (s) { return !!s.shape; }).length, body.length],
    visualShapeNoVisual: body.filter(function (s) {
      return s.shape && VISUAL_FIRST_SHAPES.indexOf(s.shape) >= 0 && (s.gfx || 0) === 0;
    }).map(function (s) { return [s.id, s.shape, s.boxes]; }).slice(0, 20),
    /* ★ 껍데기 상자가 장당 여러 개(배지 제외) */
    hollowSlides: body.filter(function (s) { return (s.hollow || 0) >= 2; })
      .map(function (s) { return [s.id, s.hollow]; }).slice(0, 20),
    thinnest: thinnest,
    deadZones: deadZones.slice(0, 20),
    sparseSlides: sparseSlides.slice(0, 20),
    /* ★ 상자 채움 — 밀도 계열과 달리 **방향**이 있어 무엇을 줄여야 할지 바로 나온다.
       wide=폭을 다 쓰고 비었다 · x=가로 늘림 · y=세로 늘림 · f=채움률 미달 */
    boxFillSlides: boxFillSlides.slice(0, 20)
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
    /* ⚠️ 측정 환경 (2026-08-18 신설 — 반복측정으로 필요성이 드러났다).
       2026-08-17 측정과 2026-08-18 재측정의 `ovf`가 2→1로 달랐는데, 증거에 환경이
       없어 「덱이 바뀐 것」인지 「환경이 바뀐 것」인지 **판별할 수단이 없었다.**
       반복측정 결과 같은 환경 안에서는 완전히 결정적이다(같은 로드 5회 · 새 로드
       3회 · 뷰포트 1440/1600 — 11개 지표 전부 동일). 따라서 수치가 달라졌다면
       ① 덱이 바뀌었거나 ② 환경이 바뀐 것이고, 이 블록이 그 둘을 가른다.
       래칫은 «환경이 같을 때»만 의미가 있다 — git diff에서 이 블록이 함께 바뀌면
       그 증가·감소를 덱의 변화로 읽지 마라. */
    env: {
      dpr: window.devicePixelRatio,
      viewport: [window.innerWidth, window.innerHeight],
      ua: navigator.userAgent,
      images: (document.images || []).length
    },
    render: { totals: agg, offenders: offenders, density: density },
    /* 장별 원자료 — 기준판 비교 도구(compare_baseline_panel.py)가 읽는다.
       ⚠️ 객체가 아니라 **배열 행**으로 싣는다. 110장을 객체로 담으면 증거가
          30KB를 넘어 콘솔에서 복사해 파일로 옮기기가 어려워진다(실측). */
    perSlideCols: ["id", "kind", "ink", "boxes", "gfx", "txt", "hollow", "deadBottom", "deadRight", "fixed"],
    perSlide: slides.map(function (s) {
      return [s.id, s.kind, Math.round((s.ink || 0) * 100) / 100, s.boxes, s.gfx,
        s.txt, s.hollow, s.deadBottom, s.deadRight, s.fixed ? 1 : 0];
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
