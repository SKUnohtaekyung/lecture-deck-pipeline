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
  var agg = { below: 0, off: 0, lap: 0, lapAbs: 0, wb: 0, ovf: 0, slots: 0, hollow: 0 };
  var offenders = [];
  slides.forEach(function (s) {
    var b = (s && s.broken) || {};
    agg.below += b.below || 0;
    agg.off += b.off || 0;
    agg.lap += b.lap || 0;
    agg.lapAbs += b.lapAbs || 0;
    agg.wb += b.wb || 0;
    agg.ovf += b.ovf || 0;
    agg.hollow += (s && s.hollow) || 0;
    agg.slots += ((s && s.emptySlots) || []).length;
    if ((b.below || 0) + (b.off || 0) + (b.lap || 0) + (b.wb || 0) + ((s.emptySlots || []).length)) {
      offenders.push({
        id: s.id, below: b.below || 0, off: b.off || 0, lap: b.lap || 0,
        wb: b.wb || 0, slots: (s.emptySlots || []).length,
        d: (b.d || []).filter(Boolean).slice(0, 3)
      });
    }
  });

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
    render: { totals: agg, offenders: offenders },
    typography: {
      textElements: (typo.meta || {}).textElements,
      fontFloor: { count: (typo.fontFloor || {}).count, byRole: (typo.fontFloor || {}).byRole,
        worst: ((typo.fontFloor || {}).worst || []).slice(0, 12) },
      tracking: { count: (typo.tracking || {}).count, byClass: (typo.tracking || {}).byClass },
      lineHeightNormal: (typo.lineHeightNormal || {}).count,
      nearMissAnchors: { total: nmTotal, dominantClashTotal: clashTotal, byAxis: nmByAxis }
    }
  }, null, 1);
})()
