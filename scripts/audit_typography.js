/* 타이포그래피·정렬 렌더 감사 — audit_render.js가 보지 않는 축
 *
 * 왜 별도인가: audit_render.js는 「잉크가 어디에 얼마나 칠해졌나」를 본다.
 * 폰트 크기·행간·자간·앵커 좌표는 코드 전문에 문자열조차 없다(2026-08-03 확인).
 * 그런데 사용자 지적의 다수가 그 축이었다 — "제목과 설명 크기가 똑같다",
 * "글씨가 너무 작다", "정렬이 안 맞는다". 재는 것이 없으면 고쳤는지도 모른다.
 *
 * 실행 (audit_render.js와 같은 조건):
 *   1) 저장소 루트에서  python -m http.server 8799
 *   2) 브라우저로 덱을 연다(로컬 HTTP · file:// 금지)
 *   3) 콘솔:  fetch('/scripts/audit_typography.js').then(r=>r.text()).then(eval)
 *
 * ⚠️ fail-closed: --scale=1 · 슬라이드 rect 1280x720 · Pretendard 로드를 확인하고,
 *    하나라도 어긋나면 { INVALID:[...] }를 돌려주며 수치를 내지 않는다.
 *    반환된 INVALID를 「결함 0」으로 집계하는 코드를 만들지 마라.
 *
 * ⚠️ 판정 등급: 전부 WARN이다. 기존 두 덱의 기준선을 먼저 기록하고, 신규 주차에서
 *    기준선 대비로 본다. 임계를 0으로 만들지 않는다(금지 규칙화 방지).
 *
 * Node에서 require하면 순수 판정 함수(rules)만 노출한다 — 레이아웃이 필요 없는
 * 부분은 픽스처로 테스트할 수 있게 하기 위해서다(tests/test_typography_rules.py).
 */
(function (root) {
  var W = 1280, H = 720;

  /* ═══════════════════════════════════════════════════════════════════
     순수 판정 규칙 — DOM 없이 동작한다(테스트 대상)
     ═══════════════════════════════════════════════════════════════════ */
  var rules = {};

  /* ── 역할 티어 (R-TYPE-01 · 2026-07-31 사용자 결정 반영) ──────────────
     ⚠️ 클래스 이름으로 역할을 판정하지 않는다. 종전 verify_deck.py의 폰트 하한이
        `'.s-body' in sel || '.s-lead' in sel`이라 `.desc`·`.subline`은 원리적으로
        검사 밖이었다 — 「위반이 없다」가 아니라 「보지 않았다」였다.
        여기서는 **텍스트의 성격**으로 판정한다: 길이·소속 컨테이너·줄 수.  */
  rules.TIERS = {
    code:      { floor: 0,  why: '코드·터미널 — 하한 적용 제외(가로 압축이 본질)' },
    table:     { floor: 17, why: '표 하한(R-TYPE-01)' },
    narrative: { floor: 22, why: '본문 성격 서술문 하한(R-TYPE-01)' },
    boxDesc:   { floor: 20, why: '박스 안 보조 설명문 — 2026-07-31 사용자 결정으로 20px 정식 허용' },
    label:     { floor: 14, why: '라벨·캡션·메타' },
    badge:     { floor: 11, why: '배지·축 라벨 — 용도 잠금' }
  };

  /* 「박스 안 설명문」으로 20px를 허용하는 글자 수 상한.
     D-1 결정 (c): 20px 티어를 정식화하되 글자 수로 관리한다.
     근거: 2주차 실측에서 20px이면서 25자 이상인 문장이 116건이었다 —
     짧은 보조 설명이 아니라 본문 문장이 20px로 내려간 것이다. */
  rules.BOX_DESC_MAX_CHARS = 24;

  /* 배지 티어를 허용하는 상한(§5-4: 용도가 잠긴 라벨 전용) */
  rules.BADGE_MAX_CHARS = 20;

  /* 「코드·터미널」 티어(하한 제외)로 보는 조상 컨테이너 셀렉터.
     ⚠️ run() 안에 숨겨 두면 픽스처로 검증할 수 없어 조용히 낡는다 — 그래서 선언을
        rules로 올린다(선언↔집행 규율).
     `.terminal-bar`는 2026-08-18 재판정에서 추가했다: 2주차 C3-N3의 터미널 창
     제목줄(`b < div.terminal-bar < div.w2-prompt.terminal-dark`)이 «Codex ·
     내-프로젝트 · 실습 ⑥ 화면 만들기»라는 **명사 브레드크럼**인데, 28자라
     BOX_DESC_MAX_CHARS를 넘고 한글 낱말이 2개 이상이라 looksLikeProse가 참을
     내 narrative(22px 하한)로 샜다. R-TYPE-01은 「코드·터미널 — 하한 적용 제외」를
     이미 규정하고 있고 `.terminal-bar`는 kit 정의 셀렉터(patterns.css)다 —
     집행부가 정본을 못 따라간 경우이므로 집행부를 고친다(유형⑤ 방향). */
  rules.CODE_CONTAINERS = ['pre', 'code', '.terminal-copy', '.terminal-bar',
    '.viz-code', '.code-chart', '.code-diagram'];

  /* ⚠️ 「긴 문자열 = 서술문」이 아니다(실측으로 확인).
     1주차에 그대로 걸면 `C:\VibeCoding\about-me\index.html`(33자·경로)와
     `LET'S MAKE SOMETHING MEANINGFUL`(32자·장식 태그라인)이 「8~14px 서술문」으로
     잡힌다. 둘 다 학습자가 읽는 문장이 아니다.
     그래서 **내용으로** 서술문을 가른다 — 이 과목의 본문은 한국어 산문이다.
       · 경로·코드 문장부호가 섞이고 한글이 거의 없으면 코드 취급(하한 제외)
       · 한글 8자 이상이면 산문
       · 한글이 없으면 5어절 이상일 때만 산문(짧은 영문 태그라인 제외)
     이 규칙을 「모든 과목」의 정본으로 굳히지 않는다 — 영문 강의를 만들면
     courses/<과목>/profile.md 쪽에서 다시 판단할 자리다. */
  rules.CODE_PUNCT = /[\\/{};=<>|`~]|\.\w{2,4}$/;
  rules.HANGUL = /[가-힣]/g;
  rules.HANGUL_WORD = /[가-힣]+/g;
  /* ⚠️ 이 하한은 «코드 토큰을 걷어낸 나머지»에 적용된다. 4자로 낮은 이유:
     여기 도달하는 문자열은 이미 24자를 넘긴 것들이고, 그중 URL·경로를 빼고도
     한글 낱말이 둘 이상 남았다면 그건 학습자가 읽는 문장이다.
     (실측 사례: `https://chat.openai.com/ 에서 접속 확인` — 나머지 한글 6자·3낱말) */
  rules.PROSE_MIN_HANGUL = 4;
  rules.PROSE_MIN_HANGUL_WORDS = 2;
  rules.PROSE_MIN_WORDS = 5;

  /* ⚠️ 독립 검증(2026-08-03)이 잡은 검출 누락:
     종전 판정은 「경로 문장부호가 있고 한글이 8자 미만이면 코드」였다. 그래서
     `https://chat.openai.com/ 에서 접속 확인` 같은 **실제 안내문**이 코드로
     분류돼 하한 검사를 통째로 빠져나갔다. 이 저장소의 과거 실패가 전부
     「통과로 보이는」 방향이었다는 점에서 가장 위험한 유형이다.
     고침: URL·경로 토큰을 **먼저 걷어내고** 남은 부분으로 다시 판정한다.
     남은 것이 문장이면 문장이다 — 문장 안에 경로가 들어 있을 뿐이다. */
  rules.CODE_TOKEN = /(?:https?:\/\/|www\.)\S+|[A-Za-z]:\\\S+|[.\w-]+\/[^\s]*|\S+\.(?:md|js|py|html|css|json|txt|png|jpg)\b/g;

  rules.looksLikeProse = function (text) {
    if (!text) return false;
    var rest = String(text).replace(rules.CODE_TOKEN, ' ').trim();
    var hangul = (rest.match(rules.HANGUL) || []).length;
    var hWords = (rest.match(rules.HANGUL_WORD) || []).length;
    if (hangul >= rules.PROSE_MIN_HANGUL && hWords >= rules.PROSE_MIN_HANGUL_WORDS) return true;
    /* 코드 토큰을 걷어냈는데도 코드 문장부호가 남고 한글이 거의 없으면 식별자다 */
    if (rules.CODE_PUNCT.test(rest) && hangul < rules.PROSE_MIN_HANGUL) return false;
    var words = rest ? rest.split(/\s+/).filter(Boolean) : [];
    return words.length >= rules.PROSE_MIN_WORDS;
  };

  /**
   * 텍스트의 역할을 내용·구조로 판정한다.
   * @param {{chars:number, lines:number, inCode:boolean, inTable:boolean, fontSize:number, text:string}} f
   * @returns {string} TIERS의 키
   */
  rules.roleOf = function (f) {
    if (f.inCode) return 'code';
    if (f.inTable) return 'table';
    /* 25자를 넘으면서 실제로 산문이면 «읽는 문장»이다 — 본문 하한을 적용한다.
       이 판정이 D-1(c)의 집행부다: 20px 짧은 설명은 통과, 20px 긴 문장은 위반. */
    if (f.chars > rules.BOX_DESC_MAX_CHARS) {
      if (rules.looksLikeProse(f.text)) return 'narrative';
      return 'code';        /* 경로·식별자·장식 문자열 — 하한 적용 제외 */
    }
    if (f.chars <= rules.BADGE_MAX_CHARS && f.lines <= 1 && f.fontSize < 14) return 'badge';
    /* 25자 이하 한 덩어리 — 박스 설명문 또는 라벨.
       20px 이상이면 설명문 티어로, 그 미만이면 라벨 티어로 본다. */
    return f.fontSize >= 20 ? 'boxDesc' : 'label';
  };

  /** 하한 위반 여부 */
  rules.violatesFloor = function (f) {
    var role = rules.roleOf(f);
    var floor = rules.TIERS[role].floor;
    return { role: role, floor: floor, violates: floor > 0 && f.fontSize < floor - 0.01 };
  };

  /* ── 자간 광학 보정 ────────────────────────────────────────────────
     큰 글자는 자간을 좁혀야 뭉쳐 보이지 않는다. 그런데 body의 em 자간은
     선언 시점에 px로 확정돼 자손에게 **절대값으로** 상속된다 — 56px 제목이
     16px 기준으로 계산된 -0.32px를 그대로 물려받는다(-0.0057em).
     선언 위치를 따지지 않고 «실효 자간이 크기에 비해 느슨한가»로 판정한다. */
  rules.TRACKING_MIN_SIZE = 32;      /* 이 크기 이상만 본다 */
  rules.TRACKING_MAX_EM = -0.02;     /* 이보다 느슨하면(0에 가까우면) 보정 누락 */

  rules.violatesTracking = function (fontSize, letterSpacingPx) {
    if (fontSize < rules.TRACKING_MIN_SIZE) return false;
    var em = letterSpacingPx / fontSize;
    return em > rules.TRACKING_MAX_EM;
  };

  /* ── 근-미스 앵커 ──────────────────────────────────────────────────
     「같은 자리처럼 보이지만 다른 값」을 잡는다. 전부 한 값으로 강제하지
     않는다 — 정당한 변형(파트 도입·프롬프트 장)이 있기 때문이다(§6-3).
     지배값에서 1~5px 벗어난 값만 결함으로 본다. 6px 이상 떨어지면
     「다른 자리」로 인정한다. */
  rules.NEAR_MISS_MAX = 5;
  rules.DOMINANT_MIN_COUNT = 3;

  /**
   * @param {Object<string|number, number>} hist 값 -> 개수
   * @returns {{dominants:number[], nearMiss:Array, dominantClashes:Array}}
   *
   * ⚠️ 독립 검증(2026-08-03)이 잡은 결함 2건을 고친 판본이다.
   *  ① **중복 계산**: 종전에는 한 값이 인접 지배값 여러 개와 각각 짝지어져
   *     `nearMissCount`가 부풀었다(238 하나가 236·241·242 때문에 3건으로).
   *     이제 **가장 가까운 지배값 하나**와만 짝지어 값마다 1건으로 센다.
   *  ② **지배값끼리의 근접이 안 보였다**: 「자기도 지배값이면 제외」 때문에
   *     236과 241처럼 **둘 다 지배값인데 5px 차이**인 경우가 절대 잡히지
   *     않았다. 그런데 그게 이 검출기가 잡으려는 문제의 **가장 심한 형태**다
   *     (차트 17개가 231~244에 7종으로 흩어진 것이 바로 그 모양이다).
   *     `dominantClashes`로 따로 보고한다.
   */
  rules.nearMissAnchors = function (hist) {
    var keys = Object.keys(hist).map(Number).filter(function (k) { return !isNaN(k); });
    var isDom = function (k) { return hist[k] >= rules.DOMINANT_MIN_COUNT; };
    var dominants = keys.filter(isDom).sort(function (a, b) { return hist[b] - hist[a]; });

    var nearMiss = [];
    keys.forEach(function (k) {
      if (isDom(k)) return;
      var best = null;
      dominants.forEach(function (d) {
        var gap = Math.abs(k - d);
        if (gap > 0 && gap <= rules.NEAR_MISS_MAX && (!best || gap < best.gap)) {
          best = { value: k, count: hist[k], dominant: d, gap: Math.round(gap * 10) / 10 };
        }
      });
      if (best) nearMiss.push(best);          /* 값마다 최대 1건 */
    });

    /* 지배값끼리 근접 — 「같은 자리인데 규격이 둘」 */
    var clashes = [];
    for (var i = 0; i < dominants.length; i++) {
      for (var j = i + 1; j < dominants.length; j++) {
        var gap = Math.abs(dominants[i] - dominants[j]);
        if (gap > 0 && gap <= rules.NEAR_MISS_MAX) {
          clashes.push({ a: dominants[i], aCount: hist[dominants[i]],
            b: dominants[j], bCount: hist[dominants[j]], gap: Math.round(gap * 10) / 10 });
        }
      }
    }
    return { dominants: dominants, nearMiss: nearMiss, dominantClashes: clashes };
  };

  /* ═══════════════════════════════════════════════════════════════════
     DOM 측정 — 브라우저에서만 동작한다
     ═══════════════════════════════════════════════════════════════════ */
  function run() {
    var slides = [].slice.call(document.querySelectorAll('.slide'));
    if (!slides.length) return { INVALID: ['no .slide element found'] };

    /* fail-closed assert — audit_render.js와 같은 조건 */
    document.documentElement.style.setProperty('--scale', 1);
    slides.forEach(function (x) { x.classList.remove('is-active'); });
    slides[0].classList.add('is-active');
    var pr = slides[0].getBoundingClientRect();
    var invalid = [];
    if (Math.abs(pr.width - W) > 0.5) invalid.push('slide width ' + pr.width + ' != ' + W);
    if (Math.abs(pr.height - H) > 0.5) invalid.push('slide height ' + pr.height + ' != ' + H);
    var sv = getComputedStyle(document.documentElement).getPropertyValue('--scale').trim();
    if (sv && sv !== '1') invalid.push('--scale=' + sv + ' (must be 1)');
    if (location.protocol === 'file:') invalid.push('file:// 로 열렸다 — 로컬 HTTP 서버를 쓰라');
    if (document.fonts && document.fonts.check('16px Pretendard') !== true) {
      invalid.push('Pretendard 미로드 — 폭·줄바꿈 측정이 재현되지 않는다');
    }
    if (invalid.length) return { INVALID: invalid };

    function chrome(e) {
      return !!(e.closest('.s-head') || e.closest('.s-pageno') || e.classList.contains('s-pageno')
        || e.closest('.slide-num') || e.classList.contains('slide-num'));
    }
    function inCode(e) {
      return rules.CODE_CONTAINERS.some(function (sel) { return !!e.closest(sel); });
    }
    function ownText(e) {
      var s = '';
      for (var i = 0; i < e.childNodes.length; i++) {
        if (e.childNodes[i].nodeType === 3) s += e.childNodes[i].textContent;
      }
      return s.trim();
    }
    function bump(o, k) { o[k] = (o[k] || 0) + 1; }

    var floorHits = [], trackHits = [], lhNormal = [], perSlide = [];
    var anchors = { titleTop: {}, titleLeft: {}, chartTop: {}, chartLeft: {}, imgLeft: {}, imgRight: {} };
    var lhNormalCount = 0, textElems = 0;

    for (var i = 0; i < slides.length; i++) {
      slides.forEach(function (x) { x.classList.remove('is-active'); });
      var sl = slides[i];
      sl.classList.add('is-active');
      var sr = sl.getBoundingClientRect();
      var sid = sl.dataset.slide || ('#' + i);
      var sFloor = 0, sTrack = 0, sLh = 0;

      [].slice.call(sl.querySelectorAll('*')).forEach(function (e) {
        if (chrome(e)) return;
        var txt = ownText(e);
        if (!txt) return;
        var cs = getComputedStyle(e);
        if (cs.visibility === 'hidden' || cs.display === 'none' || parseFloat(cs.opacity) === 0) return;
        textElems++;

        var fs = Math.round(parseFloat(cs.fontSize) * 10) / 10;
        var rng = document.createRange();
        rng.selectNodeContents(e);
        var lines = rng.getClientRects().length || 1;

        /* ① 폰트 하한 — 역할 기반 */
        var f = { chars: txt.length, lines: lines, inCode: inCode(e),
          inTable: !!e.closest('table'), fontSize: fs, text: txt };
        var v = rules.violatesFloor(f);
        if (v.violates) {
          sFloor++;
          if (floorHits.length < 400) {
            floorHits.push({ s: sid, role: v.role, need: v.floor, got: fs,
              n: txt.length, t: txt.slice(0, 30) });
          }
        }

        /* ② 자간 광학 보정 누락 */
        var ls = cs.letterSpacing === 'normal' ? 0 : parseFloat(cs.letterSpacing);
        if (rules.violatesTracking(fs, ls)) {
          sTrack++;
          trackHits.push({ s: sid, c: (e.className || e.tagName).toString().slice(0, 28),
            fs: fs, ls: Math.round(ls * 100) / 100, em: Math.round(ls / fs * 10000) / 10000 });
        }

        /* ③ 행간 미지정 */
        if (cs.lineHeight === 'normal') {
          lhNormalCount++; sLh++;
          if (lhNormal.length < 200) {
            lhNormal.push(sid + ':' + (e.className || e.tagName).toString().slice(0, 24) + '@' + fs);
          }
        }
      });

      /* ④ 앵커 수집 */
      var t = sl.querySelector('.s-title');
      if (t) {
        var rt = t.getBoundingClientRect();
        if (rt.width > 1) {
          bump(anchors.titleTop, Math.round(rt.top - sr.top));
          bump(anchors.titleLeft, Math.round(rt.left - sr.left));
        }
      }
      var seen = [];
      [].slice.call(sl.querySelectorAll('img, svg, canvas, [class*="viz-"], [data-viz], .code-chart, .code-diagram'))
        .forEach(function (e) {
          if (e.closest('.s-head')) return;
          var r = e.getBoundingClientRect();
          if (r.width < 24 || r.height < 24) return;
          for (var k = 0; k < seen.length; k++) if (seen[k].contains(e)) return;
          seen.push(e);
          if (e.tagName === 'IMG') {
            bump(anchors.imgLeft, Math.round(r.left - sr.left));
            bump(anchors.imgRight, Math.round(r.right - sr.left));
          } else {
            bump(anchors.chartTop, Math.round(r.top - sr.top));
            bump(anchors.chartLeft, Math.round(r.left - sr.left));
          }
        });

      perSlide.push({ id: sid, floor: sFloor, track: sTrack, lhNormal: sLh });
    }

    var nm = {};
    Object.keys(anchors).forEach(function (k) { nm[k] = rules.nearMissAnchors(anchors[k]); });

    /* 하한 위반을 역할별로 요약 — 어떤 티어가 새는지 본다 */
    var byRole = {};
    floorHits.forEach(function (h) { bump(byRole, h.role + '<' + h.need); });

    return {
      meta: { slides: slides.length, textElements: textElems, url: location.pathname },
      fontFloor: {
        count: floorHits.length, byRole: byRole,
        worst: floorHits.slice().sort(function (a, b) { return (a.got - a.need) - (b.got - b.need); }).slice(0, 20)
      },
      tracking: {
        count: trackHits.length,
        byClass: trackHits.reduce(function (o, h) { bump(o, h.c + '@' + h.fs); return o; }, {})
      },
      lineHeightNormal: { count: lhNormalCount, sample: lhNormal.slice(0, 20) },
      anchors: {
        raw: anchors,
        nearMiss: Object.keys(nm).reduce(function (o, k) {
          o[k] = { dominants: nm[k].dominants.slice(0, 5), nearMissCount: nm[k].nearMiss.length,
            items: nm[k].nearMiss.slice(0, 12),
            dominantClashCount: nm[k].dominantClashes.length,
            dominantClashes: nm[k].dominantClashes.slice(0, 8) };
          return o;
        }, {})
      },
      perSlide: perSlide
    };
  }

  /* Node(테스트) ↔ 브라우저(감사) 양쪽 진입점 */
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { rules: rules };
    return;
  }
  root.__auditTypography = { rules: rules, run: run };
  return JSON.stringify(run());
})(typeof globalThis !== 'undefined' ? globalThis : this);
