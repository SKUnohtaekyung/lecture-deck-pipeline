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

  /* ── 상자 채움·가려짐 임계 (2026-08-18 신설) ─────────────────────────────
     선언 정본은 `kit/guide/한장-참조표.md` 「상자 채움」 절이고 여기는 집행부다.
     두 값이 갈라지면 `tests/test_declared_vs_enforced.py`가 잡는다.

     왜 신설했나 — 기존 `sparse`(면적÷글자수) 하나로는 부족하다:
       ① `!hasGfx` 조건 때문에 **그래픽이 든 상자를 통째로 제외**한다. 아이콘 하나에
          짧은 제목만 든 대형 카드가 원리적으로 검사 밖이었다.
       ② 숫자가 하나라 **«가로로 늘어났다»와 «세로로 늘어났다»를 구분하지 못한다.**
          둘은 고치는 방법이 다른데 같은 신호로 뭉개지면 사람이 봐도 무엇을 줄일지 모른다.
     ⚠️ 이 값들은 «설계 의도»로 정했고 기존 덱에 맞춰 깎지 않았다. 기존 덱이 위반하면
        그건 계약 waiver로 등재할 사실이지 임계를 낮출 이유가 아니다. */
  var BOXFILL_DEAD_X = 35;      /* % · 상자 안쪽 우측 죽은 공간 — 가로 늘림 */
  var BOXFILL_DEAD_Y = 40;      /* % · 상자 안쪽 하단 죽은 공간 — 세로 늘림 */
  var BOXFILL_MIN_FILL = 30;    /* % · 잉크 경계상자 ÷ 상자 안쪽 면적 */
  var BOXFILL_WIDE = 95;        /* % · 본문 안전영역 폭 대비 «가로를 다 쓴» 기준 */
  var BOXFILL_WIDE_DEAD = 25;   /* % · 가로를 다 쓴 상자에는 더 엄한 우측 여백을 적용 */
  /* ⚠️ 아래 둘은 픽스처 실측으로 «반드시 필요»가 확인된 오탐 차단 조건이다(2026-08-18).
     · MIN_W 없이 재면 3열 격자의 작은 카드(폭 32%)가 우측여백 39%로 잡힌다 —
       그건 «가로로 늘어난 행»이 아니라 그냥 카드다. 여기서 잡는 병은 «행이 컨테이너
       끝까지 늘어났는데 글은 왼쪽에만»이므로 애초에 넓어야 성립한다.
     · ALIGNED 없이 재면 **중앙 정렬**이 전부 잡힌다. 가운데 놓인 글은 좌우 여백이
       같이 크다 — 그건 늘림이 아니라 정렬이다. «한쪽만 비었을 때»만 늘림이다. */
  var BOXFILL_MIN_W = 40;       /* % · 이 폭 미만은 «행»이 아니라 «카드» — 가로 늘림 대상 아님 */
  var BOXFILL_ALIGNED = 15;     /* % · 반대쪽 여백이 이보다 작아야 «한쪽으로 몰렸다» */
  var BOXFILL_MIN_H = 60;       /* px · 이 높이 미만은 세로로 «늘어날» 여지가 없다(한 줄 행) */
  /* 코드·터미널·창 크롬 — 가로 늘림 판정에서 뺀다.
     빼는 이유는 취향이 아니라 **폭을 내용에 맞출 수 없다는 성질**이다: 코드는 줄바꿈
     위치가 의미를 갖고, 터미널·창 제목줄은 자기가 감싼 창이 폭을 정한다(라벨은 왼쪽에
     붙는 것이 정상이다).
     ⚠️ 2026-08-18 1주차 현물 실측으로 2종을 추가했다 — `.terminal-bar`만 있고
     `.cover-terminal`(표지 터미널 mock · dX41)·`.tree-window-bar`(파일탐색기 제목줄
     「파일 탐색기」 · dX79 f4)가 빠져 **둘 다 오탐으로 잡혔다.** 선언(참조표 「상자 채움」)은
     이미 이들을 제외로 규정하고 있었으므로 규칙이 아니라 집행부가 뒤처진 것이다(유형⑤ —
     `audit_typography.js`의 `.terminal-bar` 누락과 같은 사고). **새 창·터미널 mock을
     만들면 여기에 등재하라 — 안 하면 신규 주차가 첫날 FAIL한다.** */
  var CODE_BOX = ['pre', 'code', '.terminal-copy', '.terminal-bar', '.terminal-dark',
    '.viz-code', '.code-chart', '.code-diagram',
    '.cover-terminal', '.tree-window-bar'];
  var OCCLUSION_COVERED = 60;   /* % · 글자가 다른 요소에 가려진 비율 */

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
  /* ⚠️ 이미지 로딩 assert (2026-08-18 신설 — 반복측정으로 규명).
     폰트는 막으면서 이미지는 안 막고 있었다. 이미지가 아직 안 그려지면 상자가
     찌그러져 **바닥선 초과·오버플로가 실제보다 적게 나온다** — 실측: 1주차에서
     `below` 25→23, `ovf` 1→0. 즉 틀리는 방향이 「덱이 더 멀쩡해 보이는」 쪽이고,
     그 상태의 수치가 래칫을 통과해 버린다. 이 저장소의 과거 실패가 전부 그
     방향이었다(지도 §8.1·§8.2).
     naturalWidth === 0 은 «로드는 끝났는데 깨진» 경우다 — complete만 보면 통과한다. */
  var _imgs = [].slice.call(document.images || []);
  var _pending = _imgs.filter(function (im) { return !im.complete; }).length;
  var _brokenImg = _imgs.filter(function (im) { return im.complete && im.naturalWidth === 0; }).length;
  if (_pending) {
    _invalid.push('이미지 ' + _pending + '/' + _imgs.length + '개 미로드 — '
      + '바닥선·오버플로가 실제보다 적게 나온다. onload 를 기다린 뒤 다시 재라');
  }
  if (_brokenImg) {
    _invalid.push('이미지 ' + _brokenImg + '/' + _imgs.length + '개 깨짐(naturalWidth=0) — '
      + '경로를 고친 뒤 다시 재라');
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
    var boxes = 0, hollow = [], hollowBadge = [], sparse = [], boxList = [];
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
      boxList.push(e);          /* 3c) 채움 분석용 — 잎 상자만 따로 골라 쓴다 */
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

    /* 3c) 상자 채움 — 「상자는 큰데 잉크는 한쪽에만」을 **방향과 함께** 잡는다.
       측정 단위는 «잎 상자»(안에 다른 상자가 없는 최소 상자)다. 그릇 상자까지 세면
       같은 빈 공간이 중복 계수된다.
       잉크 = 실제 글자 줄 상자 + 그래픽의 합집합 경계상자. 그래픽을 잉크로 치므로
       «아이콘 하나 + 짧은 제목»인 대형 카드도 정상 판정된다(sparse가 못 하던 것). */
    var boxFill = { stretchX: [], stretchY: [], wideEmpty: [], lowFill: [] };
    var boxRagged = [];
    (function () {
      var measured = [];
      /* 잎 상자만 남긴다 — 다른 상자를 품고 있으면 «그릇»이다 */
      var leaves = boxList.filter(function (e) {
        return !boxList.some(function (o) { return o !== e && e.contains(o); });
      });
      leaves.forEach(function (e) {
        var r = e.getBoundingClientRect();
        var wl = r.width / K, hl = r.height / K;
        /* 배지·칩·표 셀은 대상이 아니다 — «글자가 적은 것이 정상»인 요소다(3의 판정과 동일) */
        if (wl < 160 || hl < 48) return;
        if (e.tagName === 'TH' || e.tagName === 'TD' || e.closest('table')) return;
        /* ⚠️ 원형·pill은 제외한다 — 판단이 아니라 기하다. 원은 자기 경계상자의 π/4(78%)
           까지만 차지하고 글자는 거기서 더 안쪽에 놓이므로 **채움률이 구조적으로 낮다.**
           이걸 결함으로 세면 «원을 쓰지 마라»가 되어 버린다. 기존 `hollowBadge`가 쓰는
           것과 같은 판정식이다(3의 isBadge). */
        var brRaw = getComputedStyle(e).borderTopLeftRadius || '0';
        var brTL = parseFloat(brRaw) || 0;
        /* ⚠️ `border-radius:50%`는 computed 값이 «50%» 문자열로 나온다 — px로만 읽으면
           원이 원으로 안 잡힌다(2026-08-18 실측: 2주차 vc-ring이 이 구멍으로 샜다). */
        if (brRaw.indexOf('%') >= 0 ? brTL >= 50 : brTL >= Math.min(wl, hl) / 2 - 0.5) return;
        /* 코드·터미널 블록은 가로 판정 대상이 아니다 — 판단이 아니라 성질이다.
           코드는 **줄바꿈 위치가 의미를 가져서** 상자 폭을 내용에 맞춰 줄일 수 없다.
           좁히라고 시키면 명령어가 접혀 오히려 읽기 어려워진다. 세로·채움률은 그대로 본다. */
        var isCode = CODE_BOX.some(function (sel) { return !!e.closest(sel); })
          || !!e.querySelector('pre,code');

        /* 잉크 경계상자 */
        var L = Infinity, T = Infinity, R = -Infinity, B = -Infinity, found = false, chars = 0;
        var tw = document.createTreeWalker(e, NodeFilter.SHOW_TEXT, null), tn2;
        while ((tn2 = tw.nextNode())) {
          if (!tn2.textContent.trim()) continue;
          chars += tn2.textContent.trim().length;
          var rg2 = document.createRange(); rg2.selectNodeContents(tn2);
          var rcs = rg2.getClientRects();
          for (var z = 0; z < rcs.length; z++) {
            var q = rcs[z];
            if (q.width < 1 || q.height < 1) continue;
            L = Math.min(L, q.left); T = Math.min(T, q.top);
            R = Math.max(R, q.right); B = Math.max(B, q.bottom); found = true;
          }
        }
        [].slice.call(e.querySelectorAll('img,svg,canvas,video')).forEach(function (g) {
          var q = g.getBoundingClientRect();
          if (q.width < 6 || q.height < 6) return;
          L = Math.min(L, q.left); T = Math.min(T, q.top);
          R = Math.max(R, q.right); B = Math.max(B, q.bottom); found = true;
        });
        if (!found || chars < 2) return;   /* 빈 상자는 hollow 소관 */

        var cs3 = getComputedStyle(e);
        var padL = parseFloat(cs3.paddingLeft) || 0, padR = parseFloat(cs3.paddingRight) || 0;
        var padT = parseFloat(cs3.paddingTop) || 0, padB = parseFloat(cs3.paddingBottom) || 0;
        var innerW = (r.width - padL - padR) / K, innerH = (r.height - padT - padB) / K;
        if (innerW < 200) return;      /* 세로 가드를 여기 두지 마라 — 한 줄 행(innerH≈21)이
                                          바로 이 검출기의 주 대상이다(픽스처 실측). */

        /* 네 방향 여백을 다 잰다 — «한쪽만 비었는가»를 봐야 정렬과 늘림이 갈린다 */
        var deadL = (L - (r.left + padL)) / K / innerW * 100;
        var deadX = ((r.right - padR) - R) / K / innerW * 100;
        var deadT = (T - (r.top + padT)) / K / innerH * 100;
        var deadY = ((r.bottom - padB) - B) / K / innerH * 100;
        var fill = ((R - L) / K * ((B - T) / K)) / (innerW * innerH) * 100;
        var widePct = (r.width / K) / (BODY_R - BODY_L) * 100;
        /* 그룹 키 — 같은 부모 아래 같은 «형태»면 한 벌이다(격자의 한 줄, 카드 세트) */
        var key = (e.parentElement ? (e.parentElement.className || e.parentElement.tagName) : '?')
          .toString().slice(0, 20) + '>' + e.tagName
          + '.' + (e.className || '').toString().split(/\s+/)[0];
        measured.push({ e: e, key: key, r: r, isCode: isCode,
          deadL: deadL, deadX: deadX, deadT: deadT, deadY: deadY,
          fill: fill, widePct: widePct, innerH: innerH,
          cls: (e.className || e.tagName).toString().slice(0, 28) });
      });

      /* ── 그룹 단위 판정 ──────────────────────────────────────────────
         ⚠️ **개별 상자로 판정하면 안 된다.** 나란한 카드 3장은 글 양이 달라도
         **높이가 같아야** 한 벌로 읽힌다 — 짧은 카드는 «정렬을 지키느라» 비는 것이지
         결함이 아니다. 상자마다 잡으면 검출기가 «이것만 줄여라»를 시켜 격자를
         깨뜨린다(2026-08-18 사용자 지적으로 재설계).
         그래서 한 벌 안에서는 **가장 잘 쓴 상자**를 그 벌의 성적으로 본다:
           · 가로 — 그 벌의 **최소** 우측 여백(누구도 오른쪽을 안 썼는가)
           · 세로 — 그 벌의 **최소** 하단 여백
           · 채움 — 그 벌의 **최대** 채움률
         한 장이라도 제대로 쓰고 있으면 그 벌의 크기는 «그 내용이 요구한 크기»이고,
         나머지가 비는 것은 정렬의 대가다. 위반은 상자 N건이 아니라 **벌 1건**으로 센다 —
         고쳐야 할 단위가 벌이기 때문이다. */
      var groups = {};
      measured.forEach(function (m) { (groups[m.key] = groups[m.key] || []).push(m); });
      Object.keys(groups).forEach(function (k) {
        var g = groups[k];
        var minDeadX = Math.min.apply(null, g.map(function (m) { return m.deadX; }));
        var minDeadY = Math.min.apply(null, g.map(function (m) { return m.deadY; }));
        var maxFill = Math.max.apply(null, g.map(function (m) { return m.fill; }));
        var maxWide = Math.max.apply(null, g.map(function (m) { return m.widePct; }));
        var maxInnerH = Math.max.apply(null, g.map(function (m) { return m.innerH; }));
        var leftAligned = g.every(function (m) { return m.deadL < BOXFILL_ALIGNED; });
        var topAligned = g.every(function (m) { return m.deadT < BOXFILL_ALIGNED + 5; });
        var tag = g[0].cls + (g.length > 1 ? '×' + g.length : '')
          + '@' + Math.round(maxWide) + 'w/' + Math.round(minDeadX) + 'x/' + Math.round(minDeadY) + 'y';

        var anyCode = g.some(function (m) { return m.isCode; });
        if (maxWide >= BOXFILL_MIN_W && leftAligned && !anyCode) {
          if (maxWide >= BOXFILL_WIDE && minDeadX > BOXFILL_WIDE_DEAD) boxFill.wideEmpty.push(tag);
          else if (minDeadX > BOXFILL_DEAD_X) boxFill.stretchX.push(tag);
        }
        if (maxInnerH >= BOXFILL_MIN_H && topAligned && minDeadY > BOXFILL_DEAD_Y) {
          boxFill.stretchY.push(tag);
        }
        if (maxInnerH >= BOXFILL_MIN_H && maxFill < BOXFILL_MIN_FILL) {
          boxFill.lowFill.push(tag + '/' + Math.round(maxFill) + 'f');
        }

        /* ── 짝 검출기: 정렬 파괴 ─────────────────────────────────────
           위 판정을 «상자를 줄여라»로만 읽으면 격자가 들쭉날쭉해진다. 그 반대 결함을
           같은 자리에서 함께 잡아 두 규칙이 서로를 붙든다.
           같은 줄에 나란한(상단 ±8px) 한 벌의 **높이가 6px 넘게 다르면** 결함이다 —
           6px은 반올림·서브픽셀로 생길 수 없는 차이다. */
        if (g.length >= 2) {
          var sameRow = g.filter(function (m) { return Math.abs(m.r.top - g[0].r.top) <= 8 * K; });
          if (sameRow.length >= 2) {
            var hs = sameRow.map(function (m) { return m.r.height / K; });
            var spread = Math.max.apply(null, hs) - Math.min.apply(null, hs);
            if (spread > 6) {
              boxRagged.push(g[0].cls + '×' + sameRow.length + '@높이차' + Math.round(spread) + 'px');
            }
          }
        }
      });
    })();

    /* 3d) 가려짐 — 「글자가 화면에서 실제로 보이는가」.
       종전에는 절대배치가 낀 겹침을 전부 `lapAbs`(참고치)로 내렸다. 그 판단의 근거는
       실측이었지만(2주차 7건 전부 «그림 위 라벨» 오탐), **의도된 오버레이와 «문장이
       통째로 가려진 사고»를 가르지 않고 통째로 내린 것**이 문제였다.
       여기서는 기하가 아니라 **화면 합성 결과**로 판정한다 — 글자 줄 위의 점을 찍어
       `elementFromPoint`가 그 글자를 돌려주는지 본다. 라벨은 그림을 조금 덮지만
       사고는 문장을 통째로 덮으므로 이 신호로 갈린다. */
    var occluded = [];
    (function () {
      var covers = [].slice.call(sl.querySelectorAll('*')).filter(function (e) {
        if (e.closest('.s-head')) return false;
        var q = e.getBoundingClientRect();
        if (q.width < 40 || q.height < 24) return false;
        if (isGraphic(e)) return true;
        var c = getComputedStyle(e).backgroundColor;
        var m = /rgba?\(([^)]+)\)/.exec(c);
        if (!m) return false;
        var parts = m[1].split(',');
        return parts.length < 4 || parseFloat(parts[3]) >= 0.9;   /* 불투명한 배경만 */
      });
      if (!covers.length) return;

      [].slice.call(sl.querySelectorAll('*')).forEach(function (e) {
        if (e.closest('.s-head') || e.classList.contains('s-pageno') || e.closest('.s-pageno')) return;
        var own = '';
        for (var c2 = 0; c2 < e.childNodes.length; c2++) {
          if (e.childNodes[c2].nodeType === 3) own += e.childNodes[c2].textContent;
        }
        if (own.trim().length < 4) return;
        var er = e.getBoundingClientRect();
        if (er.width < 40 || er.height < 12) return;

        /* 기하 예비필터 — 겹치는 불투명 후보가 없으면 점을 찍지 않는다(비용) */
        var hit = covers.some(function (cv) {
          if (cv === e || cv.contains(e) || e.contains(cv)) return false;
          var cr = cv.getBoundingClientRect();
          var ix = Math.max(0, Math.min(er.right, cr.right) - Math.max(er.left, cr.left));
          var iy = Math.max(0, Math.min(er.bottom, cr.bottom) - Math.max(er.top, cr.top));
          return ix * iy > 0.3 * (er.width * er.height);
        });
        if (!hit) return;

        /* 확인 — 글자 줄 위에 점을 찍어 실제로 무엇이 보이는지 본다 */
        var rg3 = document.createRange(); rg3.selectNodeContents(e);
        var lines = rg3.getClientRects();
        var vis = 0, tot = 0;
        for (var li = 0; li < lines.length; li++) {
          var ln = lines[li];
          if (ln.width < 4 || ln.height < 4) continue;
          for (var sx = 1; sx <= 5; sx++) {
            var px = ln.left + ln.width * (sx / 6), py = ln.top + ln.height / 2;
            var top = document.elementFromPoint(px, py);
            if (!top) continue;                      /* 뷰포트 밖 — 판정하지 않는다 */
            tot++;
            if (top === e || e.contains(top) || top.contains(e)) vis++;
          }
        }
        if (tot < 4) return;                          /* 표본이 적으면 판정하지 않는다 */
        var coveredPct = (1 - vis / tot) * 100;
        if (coveredPct > OCCLUSION_COVERED) {
          occluded.push((e.className || e.tagName).toString().slice(0, 28)
            + ':' + Math.round(coveredPct) + '%가려짐');
        }
      });
    })();

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

    /* 고정 구조 슬라이드 판정 — **클래스로 본다**(2026-08-03 신설).
       ⚠️ data-slide 접두어로 가르면 안 된다. 실측: 1주차에 `PAL1`·`PAL2`·`PAL3`라는
          **본문** 슬라이드가 있어 「P로 시작하면 간지」 규칙이 셋을 통째로 본문
          집계에서 빼 버렸다. 고정 슬라이드의 정의는 원래 클래스다
          (토큰-치트시트 「고정 구조 슬라이드」: cover·s02-slide·s03-slide·
          part-divider·concept-recap·closing). */
    var fixed = /\b(cover|s02-slide|s03-slide|part-divider|concept-recap|closing)\b/
      .test(sl.className);

    var title = (sl.querySelector('.s-title') || {}).innerText || '';
    var kind = /M[0-9]$/.test(sl.dataset.slide || '') ? '교시'
      : /이렇게 배웁니다|이렇게배웁니다/.test(title) ? '이렇게배웁니다'
        : /실습|해보기|따라하기|미션/.test(title) ? '실습'
          : /^P[0-9]/.test(sl.dataset.slide || '') ? '파트표지' : '설명';

    out.push({
      i: i,
      id: sl.dataset.slide,
      kind: kind,
      fixed: fixed,        /* 고정 구조 슬라이드(별도 좌표계) — 밀도 비교 대상이 아니다 */
      /* 정보 모양 — 조립 시 `data-shape="numeric"` 처럼 적어 둔 값.
         ⚠️ 없으면 **null**이다. 0이나 빈 문자열로 두지 마라 — 「모양이 없다」와
            「기록하지 않았다」가 섞이면 「해당 신호 0건」이 «검사했는데 깨끗함»으로
            잘못 읽힌다. 이 저장소가 반복해서 겪은 실패다. */
      shape: sl.dataset.shape || null,
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
        /* 가려짐 — lapAbs 중 «화면 합성 결과 글자가 실제로 안 보이는» 것만 판정 대상으로 승격 */
        occl: occluded.length,
        wb: broken.wordBreak.length,
        d: broken.belowFloor.concat(broken.overlap).slice(0, 3).concat(broken.wordBreak.slice(0, 2))
      },
      /* 상자 채움 — 방향이 있는 3지표(가로 늘림 · 세로 늘림 · 채움률) + 폭 임계 */
      boxFill: {
        stretchX: boxFill.stretchX.length, stretchY: boxFill.stretchY.length,
        wideEmpty: boxFill.wideEmpty.length, lowFill: boxFill.lowFill.length,
        /* 짝 검출기 — 「줄여라」가 격자를 깨는 쪽으로 가지 않게 붙든다 */
        ragged: boxRagged.length,
        d: boxFill.wideEmpty.concat(boxFill.stretchX).concat(boxFill.stretchY)
             .concat(boxFill.lowFill).concat(boxRagged).slice(0, 5)
      },
      occlD: occluded.slice(0, 3),
      emptySlots: emptySlots
    });
  }
  return JSON.stringify(out);
})()
