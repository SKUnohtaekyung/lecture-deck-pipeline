/*! presenter-runtime.js — 발표 런타임 (kit 공통 정본) v1.0.0
 *
 * 계획서 §7~§13 구현. 청중 창(이 스크립트가 실행되는 창)이 **유일한 상태 소유자이자
 * 유일한 저장소 기록자**다. 발표자 팝업은 상태를 소유하지 않는다.
 *
 * 통신은 방향마다 정확히 하나다:
 *   부모 → 팝업 : 직접 DOM 조작 (직렬화 0)
 *   팝업 → 부모 : opener.postMessage (부모 재로드 내성)
 *
 * 이 스크립트는 `.deck` 내부를 절대 수정하지 않는다. 주입 노드는 전부 `.deck` 밖에 있다.
 */
(function (global) {
  'use strict';

  var RUNTIME_VERSION = '1.0.0';

  /* ══════════════════════════════════════════════════════════════════
     ID 계약 — 런타임이 getElementById로 찾는 이름을 한 곳에 모은다.
     (계획서 §16 대체검증 2: 이 목록과 생성 마크업을 정적 대조한다)
     ══════════════════════════════════════════════════════════════════ */
  var ID = {
    blackout:         'blackout',
    controls:         'controls',
    counter:          'counter',
    prevBtn:          'prevBtn',
    nextBtn:          'nextBtn',
    menuBtn:          'menuBtn',
    fsBtn:            'fsBtn',
    presentationMenu: 'presentationMenu',
    menuClose:        'menuClose',
    menuPart:         'menuPart',
    menuTitle:        'menuTitle',
    homeBtn:          'homeBtn',
    pageInput:        'pageInput',
    goBtn:            'goBtn',
    pdfBtn:           'pdfBtn',
    helpBtn:          'helpBtn',
    keyboardHelp:     'keyboardHelp',
    helpClose:        'helpClose',
    slideList:        'slideList'
  };

  var SEL_DECK = '.deck';
  var SEL_SLIDE = '.deck > .slide';   /* §8 불변조건 2 — querySelectorAll('.slide') 금지 */

  /* ══════════════════════════════════════════════════════════════════
     KEYMAP — 단축키의 **단일 정본**.
     키 처리와 `?` 도움말 UI를 둘 다 이 배열 하나에서 만든다. 하드코딩된 안내
     마크업을 두지 않으므로 "도움말 문구 ≠ 실제 키"가 구조적으로 불가능하다.

       keys : KeyboardEvent.key 값(대소문자는 매칭 시 무시)
       label: 도움말에 보일 키 표기
       desc : 도움말 설명
       move : 이동 키인가 — 모달이 열려 있거나 blackout 중이면 이 키만 막는다(§8-5)
     ══════════════════════════════════════════════════════════════════ */
  var KEYMAP = [
    { id: 'next',       keys: ['ArrowRight', 'PageDown', ' ', 'Spacebar'], label: '→ · Space · PgDn', desc: '다음 슬라이드',        move: true  },
    { id: 'prev',       keys: ['ArrowLeft', 'PageUp'],                     label: '← · PgUp',         desc: '이전 슬라이드',        move: true  },
    { id: 'first',      keys: ['Home'],                                    label: 'Home',             desc: '첫 슬라이드(표지)',    move: true  },
    { id: 'last',       keys: ['End'],                                     label: 'End',              desc: '마지막 슬라이드',      move: true  },
    { id: 'blackout',   keys: ['b'],                                       label: 'B',                desc: '화면 가리기 · 해제',   move: false },
    { id: 'menu',       keys: ['g'],                                       label: 'G',                desc: '상세 메뉴 열기 · 닫기', move: false },
    { id: 'help',       keys: ['?', '/'],                                  label: '?',                desc: '단축키 안내',          move: false },
    { id: 'fullscreen', keys: ['f'],                                       label: 'F',                desc: '전체화면 전환',        move: false },
    { id: 'presenter',  keys: ['p'],                                       label: 'P',                desc: '발표자 창 열기',       move: false },
    { id: 'escape',     keys: ['Escape'],                                  label: 'Esc',              desc: '열린 창 닫기 · 가리기 해제', move: false }
  ];

  function keymapLookup(key) {
    if (key == null) return null;
    var lower = String(key).toLowerCase();
    for (var i = 0; i < KEYMAP.length; i++) {
      var entry = KEYMAP[i];
      for (var j = 0; j < entry.keys.length; j++) {
        if (String(entry.keys[j]).toLowerCase() === lower) return entry;
      }
    }
    return null;
  }

  /* ══════════════════════════════════════════════════════════════════
     저장소 — 부모 창만 기록한다(§10.3). 실패는 숨기지 않고 상태로 남긴다.
     ══════════════════════════════════════════════════════════════════ */
  function makeStore(pick) {
    var raw = null, usable = false;
    try {
      raw = pick();
      var probe = 'pv:probe';
      raw.setItem(probe, '1');
      raw.removeItem(probe);
      usable = true;
    } catch (e) {
      usable = false;
    }
    return {
      available: function () { return usable; },
      get: function (key) {
        if (!usable) return null;
        try { return raw.getItem(key); } catch (e) { return null; }
      },
      set: function (key, value) {
        if (!usable) return false;
        try { raw.setItem(key, value); return true; } catch (e) { return false; }
      },
      remove: function (key) {
        if (!usable) return false;
        try { raw.removeItem(key); return true; } catch (e) { return false; }
      }
    };
  }

  var localStore = makeStore(function () { return global.localStorage; });
  var sessionStore = makeStore(function () { return global.sessionStorage; });

  /* 키 규약(§10.3) — buildHash는 절대 키에 넣지 않는다(재빌드해도 메모가 살아남아야 한다). */
  var KEYS = {
    note:  function (deckId, slideId) { return 'pv:' + deckId + ':note:' + slideId; },
    theme: function () { return 'pv:theme'; },
    pos:   function (deckId) { return 'pv:' + deckId + ':pos'; },
    timer: function (deckId) { return 'pv:' + deckId + ':timer'; },
    sid:   function (deckId) { return 'pv:' + deckId + ':sid'; }
  };

  /* ══════════════════════════════════════════════════════════════════
     보조
     ══════════════════════════════════════════════════════════════════ */
  function clamp(n, lo, hi) {
    n = parseInt(n, 10);
    if (isNaN(n)) return lo;
    return n < lo ? lo : (n > hi ? hi : n);
  }

  /** 슬라이드 제목 — 첫 h1/h2/h3의 텍스트. <br>은 공백으로 바꾼다
   *  (scripts/verify_notes.py의 SlideParser와 같은 규칙). */
  function titleOf(slideEl) {
    var heading = slideEl.querySelector('h1, h2, h3');
    if (!heading) return '';
    var clone = heading.cloneNode(true);
    var brs = clone.querySelectorAll('br');
    for (var i = 0; i < brs.length; i++) {
      brs[i].parentNode.replaceChild(clone.ownerDocument.createTextNode(' '), brs[i]);
    }
    return String(clone.textContent || '').replace(/\s+/g, ' ').trim();
  }

  /* ══════════════════════════════════════════════════════════════════
     ThemeStore — 발표 UI 스코프 전용(§12). 슬라이드 본문에는 적용되지 않는다.
     ══════════════════════════════════════════════════════════════════ */
  function createThemeStore() {
    var VALID = { light: true, dark: true };
    var current = 'light';
    var listeners = [];

    function preferred() {
      try {
        if (global.matchMedia && global.matchMedia('(prefers-color-scheme: dark)').matches) return 'dark';
      } catch (e) { /* 무시 */ }
      return 'light';
    }

    function initial() {
      var saved = localStore.get(KEYS.theme());
      /* 저장값이 있으면 항상 저장값이 이긴다. 손상된 값은 무시하고 초깃값 규칙으로 복귀. */
      return (saved && VALID[saved]) ? saved : preferred();
    }

    function applyTo(doc, value) {
      if (!doc || !doc.documentElement) return;
      doc.documentElement.setAttribute('data-pv-theme', value);
    }

    return {
      get: function () { return current; },
      /** 발표 UI 스코프에만 적용 + localStorage 저장. 실패는 조용히 기본값(§10.3). */
      set: function (value, docs) {
        current = VALID[value] ? value : preferred();
        localStore.set(KEYS.theme(), current);
        var targets = docs || [global.document];
        for (var i = 0; i < targets.length; i++) applyTo(targets[i], current);
        for (var j = 0; j < listeners.length; j++) {
          try { listeners[j](current); } catch (e) { /* 구독자 예외는 격리 */ }
        }
        return current;
      },
      apply: applyTo,
      init: function (docs) { return this.set(initial(), docs); },
      onChange: function (fn) { if (typeof fn === 'function') listeners.push(fn); }
    };
  }

  /* ══════════════════════════════════════════════════════════════════
     DeckState — 단일 진실 공급원(§8).
     불변 조건
       1. 슬라이드 전이는 항상 goTo 1회를 통한다(버튼 클릭 흉내 금지).
       2. 슬라이드 컬렉션은 `.deck > .slide`로만, 로드 시 1회만 캡처한다.
       3. 팝업은 상태를 소유하지 않는다.
       4. 저장소에 쓰는 주체는 부모 창 하나뿐이다.
     ══════════════════════════════════════════════════════════════════ */
  function createDeckState(options) {
    var doc = options.document;
    var deckEl = doc.querySelector(SEL_DECK);
    /* 로드 시 1회 캡처 — 이후 컬렉션을 다시 만들지 않는다(미리보기 복제본과 충돌 방지). */
    var slides = deckEl ? Array.prototype.slice.call(deckEl.querySelectorAll(SEL_SLIDE)) : [];
    var deckId = options.deckId;

    var slideIds = slides.map(function (el, i) {
      return (el.getAttribute('data-slide') || '').trim() || ('#' + (i + 1));
    });
    var titles = slides.map(titleOf);

    var state = { index: 0, blackout: false, theme: 'light', presenter: 'closed' };
    var subscribers = [];
    var themeStore = options.themeStore;

    function snapshot() {
      return {
        index: state.index,
        blackout: state.blackout,
        theme: themeStore ? themeStore.get() : state.theme,
        presenter: state.presenter,
        count: slides.length,
        slideId: slideIds[state.index] || '',
        title: titles[state.index] || ''
      };
    }

    function notify(reason) {
      var snap = snapshot();
      for (var i = 0; i < subscribers.length; i++) {
        try { subscribers[i](snap, reason); } catch (e) { /* 구독자 예외는 격리 */ }
      }
    }

    function goTo(target) {
      if (!slides.length) return -1;
      var next = clamp(target, 0, slides.length - 1);
      state.index = next;

      for (var i = 0; i < slides.length; i++) {
        slides[i].classList.toggle('is-active', i === next);
      }

      notify('goTo');

      sessionStore.set(KEYS.pos(deckId), String(next));

      /* 최선 노력. 위치 복원의 근거로 쓰지 않는다(§10.3). goTo당 최대 1회. */
      try {
        if (global.history && global.history.replaceState) {
          global.history.replaceState(null, '', '#slide=' + (next + 1));
        }
      } catch (e) { /* file://에서 실패할 수 있다 — 무시 */ }

      return next;
    }

    return {
      /* ── 이동 ── */
      goTo: goTo,
      next: function () { return state.index < slides.length - 1 ? goTo(state.index + 1) : state.index; },
      prev: function () { return state.index > 0 ? goTo(state.index - 1) : state.index; },
      first: function () { return goTo(0); },
      last: function () { return goTo(slides.length - 1); },

      /* ── blackout — 역할과 무관하게 이 경로 하나(§8) ── */
      setBlackout: function (on) {
        state.blackout = !!on;
        var el = doc.getElementById(ID.blackout);
        /* 덱 규약: #blackout(.presentation-blackout)은 hidden 속성으로만 제어한다. */
        if (el) el.hidden = !state.blackout;
        notify('blackout');
        return state.blackout;
      },
      toggleBlackout: function () { return this.setBlackout(!state.blackout); },
      isBlackout: function () { return state.blackout; },

      /* ── 테마 ── */
      setTheme: function (value, docs) {
        var applied = themeStore ? themeStore.set(value, docs) : value;
        state.theme = applied;
        notify('theme');
        return applied;
      },

      /* ── 발표자 창 연결 상태 ── */
      setPresenter: function (value) {
        state.presenter = value;
        notify('presenter');
        return value;
      },
      getPresenter: function () { return state.presenter; },

      /* ── 구독 ── */
      subscribe: function (fn) {
        if (typeof fn !== 'function') return function () {};
        subscribers.push(fn);
        return function () {
          var at = subscribers.indexOf(fn);
          if (at >= 0) subscribers.splice(at, 1);
        };
      },

      /* ── 조회 전용 ── */
      getIndex: function () { return state.index; },
      getCount: function () { return slides.length; },
      getSlide: function (i) { return slides[i] || null; },
      getSlideId: function (i) { return slideIds[i] || ''; },
      getTitle: function (i) { return titles[i] || ''; },
      getSlideIds: function () { return slideIds.slice(); },
      snapshot: snapshot,

      /* ── 복원(§10.3: sessionStorage · 실패 시 조용히 표지) ── */
      restorePosition: function () {
        var saved = sessionStore.get(KEYS.pos(deckId));
        return goTo(saved == null ? 0 : saved);
      }
    };
  }

  /* ══════════════════════════════════════════════════════════════════
     발표자 팝업 — ID 계약 (팝업 문서 안에서만 쓰인다)
     ══════════════════════════════════════════════════════════════════ */
  var PID = {
    root:        'pvRoot',
    link:        'pvLink',
    pos:         'pvPos',
    timer:       'pvTimer',
    timerToggle: 'pvTimerToggle',
    timerReset:  'pvTimerReset',
    clock:       'pvClock',
    theme:       'pvTheme',
    print:       'pvPrint',
    quit:        'pvQuit',
    now:         'pvNow',
    nextPrev:    'pvNextPreview',
    title:       'pvTitle',
    nextTitle:   'pvNextTitle',
    note:        'pvNote',
    noteBadge:   'pvNoteBadge',
    noteReset:   'pvNoteReset',
    noteSmaller: 'pvNoteSmaller',
    noteLarger:  'pvNoteLarger',
    save:        'pvSave',
    prev:        'pvPrev',
    next:        'pvNext',
    black:       'pvBlack',
    goto:        'pvGoto',
    go:          'pvGo',
    notice:      'pvNotice'
  };

  /* 아이콘은 SVG만 쓴다 — 이모지는 폰트 의존적이고, 덱 검증기의 "아이콘 마커 누출" 검사와도 충돌한다. */
  function icon(name) {
    var d = {
      /* 채움 기반 아이콘은 fill을 명시한다 — 생략하면 SVG 기본값(검정)이라 다크 테마에서 묻힌다.
         CSS로 일괄 지정하면 fill="none"인 외곽선 아이콘까지 칠해지므로 여기서만 준다. */
      play:    '<path d="M8 5v14l11-7z" fill="currentColor"/>',
      pause:   '<path d="M7 5h3.5v14H7zM13.5 5H17v14h-3.5z" fill="currentColor"/>',
      reset:   '<path d="M4 11a8 8 0 1 1 2.3 5.7" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><path d="M4 5v6h6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
      prev:    '<path d="M15 5 8 12l7 7" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>',
      next:    '<path d="m9 5 7 7-7 7" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>',
      black:   '<path d="M3 3h18v14H3z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M8 21h8" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
      theme:   '<path d="M12 3a9 9 0 1 0 9 9 7 7 0 0 1-9-9z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>',
      print:   '<path d="M7 9V3h10v6M7 19H5a2 2 0 0 1-2-2v-4a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v4a2 2 0 0 1-2 2h-2" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M7 15h10v6H7z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>',
      quit:    '<path d="M6 6l12 12M18 6 6 18" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/>',
      undo:    '<path d="M9 7H5V3" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M5 7a8 8 0 1 1-1 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
      screen:  '<path d="M3 4h18v12H3z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M9 20h6M12 16v4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>'
    };
    return '<svg class="pv-i" viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" focusable="false">' +
           (d[name] || '') + '</svg>';
  }

  var PROTOCOL = { tag: 'pv', version: 1 };

  /* 팝업 bootstrap 소스 — 팝업 **자신의 JS 컨텍스트**에서 실행된다.
     그래서 부모가 재로드돼도 살아남고, opener는 새 부모를 가리킨다.
     부모는 이 스크립트를 createElement('script') + textContent + appendChild로 넣는다
     (innerHTML으로 넣으면 실행되지 않는다). __CONFIG__ 자리에 상수를 심는다. */
  var BOOTSTRAP_SOURCE = [
    '(function(){',
    '  "use strict";',
    '  var CFG = __CONFIG__;',
    '  var TAG = CFG.tag, V = CFG.version, deckId = CFG.deckId, sessionId = CFG.sessionId;',
    '  var adopted = false, helloTimer = null, pingTimer = null, watchTimer = null;',
    '  var lastPong = Date.now(), disconnected = false;',
    '  function send(kind, extra){',
    '    var msg = {t:TAG, v:V, kind:kind, deckId:deckId, sessionId:sessionId};',
    '    if (extra) for (var k in extra) if (Object.prototype.hasOwnProperty.call(extra,k)) msg[k]=extra[k];',
    '    try { if (window.opener && !window.opener.closed) { window.opener.postMessage(msg, "*"); return true; } }',
    '    catch(e){}',
    '    return false;',
    '  }',
    '  window.__pvSend = send;',
    '  window.__pvAdopt = function(){ adopted = true; if (helloTimer) { clearInterval(helloTimer); helloTimer = null; } lastPong = Date.now(); setDisconnected(false); };',
    '  window.__pvPong = function(){ lastPong = Date.now(); setDisconnected(false); };',
    '  function setDisconnected(on, text){',
    '    disconnected = !!on;',
    '    var root = document.getElementById(CFG.ids.root);',
    '    if (root) root.setAttribute("data-pv-link", on ? "lost" : "live");',
    '    var notice = document.getElementById(CFG.ids.notice);',
    '    if (notice){ notice.textContent = on ? (text || CFG.text.lost) : ""; notice.hidden = !on; }',
    '    var badge = document.getElementById(CFG.ids.link);',
    '    if (badge) badge.textContent = on ? CFG.text.badgeLost : CFG.text.badgeLive;',
    '    var controls = document.querySelectorAll("[data-pv-cmd]");',
    '    for (var i=0;i<controls.length;i++) controls[i].disabled = !!on;',
    '  }',
    '  window.__pvSetDisconnected = setDisconnected;',
    '  /* UI 조작은 전부 명령 메시지 1건으로 부모에 전달된다(팝업은 상태를 소유하지 않는다). */',
    '  /* 팝업 안에서만 끝나는 조작(글자 크기·창 닫기)은 부모에 보내지 않는다. */',
    '  function noteScale(delta){',
    '    var note = document.getElementById(CFG.ids.note);',
    '    if (!note) return;',
    '    var cur = parseFloat(note.getAttribute("data-pv-scale") || "1");',
    '    var next = Math.min(1.9, Math.max(0.75, Math.round((cur + delta) * 100) / 100));',
    '    note.setAttribute("data-pv-scale", String(next));',
    '    note.style.fontSize = (17 * next).toFixed(1) + "px";',
    '    try { if (window.opener && !window.opener.closed) send("NOTE_SCALE", {scale: next}); } catch(e){}',
    '  }',
    '  window.__pvNoteScale = function(v){',
    '    var note = document.getElementById(CFG.ids.note);',
    '    if (!note) return;',
    '    note.setAttribute("data-pv-scale", String(v));',
    '    note.style.fontSize = (17 * v).toFixed(1) + "px";',
    '  };',
    '  document.addEventListener("click", function(e){',
    '    var local = e.target;',
    '    while (local && local !== document.body && !local.id) local = local.parentNode;',
    '    if (local && local.id === CFG.ids.noteSmaller) { noteScale(-0.12); return; }',
    '    if (local && local.id === CFG.ids.noteLarger)  { noteScale(0.12); return; }',
    '    if (local && local.id === CFG.ids.quit) { try { window.close(); } catch(err){} return; }',
    '    var el = e.target;',
    '    while (el && el !== document.body && !el.getAttribute) el = el.parentNode;',
    '    while (el && el !== document.body && !el.getAttribute("data-pv-cmd")) el = el.parentNode;',
    '    if (!el || !el.getAttribute) return;',
    '    var cmd = el.getAttribute("data-pv-cmd");',
    '    if (!cmd || cmd === "QUIT" || disconnected) return;',
    '    var payload = {};',
    '    if (cmd === "GOTO"){',
    '      var box = document.getElementById(CFG.ids.goto);',
    '      var n = box ? parseInt(box.value, 10) : NaN;',
    '      if (isNaN(n)) return;',
    '      payload.index = n - 1;',
    '    }',
    '    send(cmd, payload);',
    '  }, false);',
    '  document.addEventListener("input", function(e){',
    '    if (!e.target || e.target.id !== CFG.ids.note || disconnected) return;',
    '    send("NOTE_INPUT", {text: e.target.value});',
    '  }, false);',
    '  /* 팝업 안에서도 같은 단축키를 쓴다. 입력 요소에 포커스가 있으면 전부 무동작. */',
    '  document.addEventListener("keydown", function(e){',
    '    if (disconnected) return;',
    '    var t = e.target || {};',
    '    var tag = (t.tagName || "").toLowerCase();',
    '    if (tag === "input" || tag === "textarea" || tag === "select" || t.isContentEditable) return;',
    '    if (e.isComposing || e.ctrlKey || e.altKey || e.metaKey) return;',
    '    var cmd = CFG.keys[String(e.key).toLowerCase()];',
    '    if (!cmd) return;',
    '    e.preventDefault();',
    '    send(cmd, {});',
    '  }, false);',
    '  /* 미리보기 배율은 **제한이 걸리는 축** 기준이다: min(w/1280, h/720).',
    '     폭만 쓰면 박스가 세로로 눌렸을 때 슬라이드가 위아래로 잘린다. 팝업이 자기',
    '     크기를 아는 주체이므로 리사이즈 대응도 여기서 한다(부모는 백그라운드에서 스로틀된다). */',
    '  /* 16:9 박스는 높이에서 폭이 파생되는데, flex의 내재 크기 계산 시점엔 그 높이가',
    '     미확정이라 CSS만으로는 왼쪽 칸 폭을 맞출 수 없다(폭이 0으로 잡힌다). 그래서',
    '     왼쪽 칸 폭만 여기서 정하고, 남는 가로 공간은 전부 오른쪽 노트 칸이 가져간다.',
    '     → 슬라이드 주변에 죽은 여백이 남지 않는다. */',
    '  function fitStage(){',
    '    var body = document.querySelector(".pv-body");',
    '    var stage = document.querySelector(".pv-stage");',
    '    var frame = document.querySelector(".pv-stage-frame");',
    '    if (!body || !stage || !frame) return;',
    '    var stacked = window.innerWidth <= CFG.stackAt;',
    '    body.setAttribute("data-pv-stacked", stacked ? "1" : "0");',
    '    if (stacked){ stage.style.width = ""; return; }',
    '    var fh = frame.clientHeight;',
    '    var avail = body.clientWidth - CFG.sideMin - CFG.gap;',
    '    if (fh <= 0 || avail <= 0) { stage.style.width = ""; return; }',
    '    stage.style.width = Math.max(320, Math.min(fh * 16 / 9, avail)) + "px";',
    '  }',
    '  function rescale(){',
    '    fitStage();',
    '    fitStage();   /* 폭이 바뀌며 프레임 높이가 미세하게 달라질 수 있어 한 번 더 수렴시킨다 */',
    '    var ids = [CFG.ids.now, CFG.ids.nextPrev];',
    '    for (var i=0;i<ids.length;i++){',
    '      var host = document.getElementById(ids[i]);',
    '      if (!host) continue;',
    '      var w = host.clientWidth, h = host.clientHeight;',
    '      if (w > 0 && h > 0) host.style.setProperty("--scale", String(Math.min(w/1280, h/720)));',
    '    }',
    '  }',
    '  window.__pvRescale = rescale;',
    '  window.addEventListener("resize", rescale, false);',
    '  /* 타이머·시계는 팝업이 그린다. 부모 창은 포커스를 잃으면 setInterval이 스로틀돼',
    '     초가 멈춰 보인다. 상태(누적·진행여부)는 여전히 부모가 소유하고, 부모는 그 값을',
    '     data-pv-timer로 publish한다. 팝업은 읽어서 표시만 한다. */',
    '  var T = {running:false, elapsed:0, readAt:0, raw:null};',
    '  function pad2(n){ return (n<10?"0":"")+n; }',
    '  function fmtElapsed(ms){',
    '    var total = Math.floor(ms/1000), h = Math.floor(total/3600);',
    '    return h + ":" + pad2(Math.floor((total%3600)/60)) + ":" + pad2(total%60);',
    '  }',
    '  setInterval(function(){',
    '    var root = document.getElementById(CFG.ids.root);',
    '    var raw = root ? root.getAttribute("data-pv-timer") : null;',
    '    if (raw && raw !== T.raw){',
    '      try { var o = JSON.parse(raw); T = {running:!!o.running, elapsed:o.elapsed||0, readAt:Date.now(), raw:raw}; }',
    '      catch(e){}',
    '    }',
    '    var el = document.getElementById(CFG.ids.timer);',
    '    if (el) el.textContent = fmtElapsed(T.elapsed + (T.running ? (Date.now()-T.readAt) : 0));',
    '    var ck = document.getElementById(CFG.ids.clock);',
    '    if (ck){',
    '      var d = new Date(), hh = d.getHours();',
    '      ck.textContent = (hh<12?"오전":"오후") + " " + (hh%12||12) + ":" + pad2(d.getMinutes());',
    '    }',
    '  }, 250);',
    '  /* 부모 → 팝업은 직접 DOM이 유일 경로다. 부모는 살아 있다는 신호로',
    '     body의 data-pv-pong 값을 갱신한다. 그 값이 멈추면 부모가 사라진 것이다. */',
    '  watchTimer = setInterval(function(){',
    '    var stamp = document.body ? document.body.getAttribute("data-pv-pong") : null;',
    '    if (stamp && stamp !== String(lastPong)) { lastPong = stamp; window.__pvPong(); return; }',
    '    var gone = false;',
    '    try { gone = !window.opener || window.opener.closed; } catch(e){ gone = true; }',
    '    if (gone) setDisconnected(true, CFG.text.parentGone);',
    '  }, 2000);',
    '  helloTimer = setInterval(function(){ if (!adopted) send("HELLO"); }, 2000);',
    '  pingTimer = setInterval(function(){ if (adopted) send("PING"); }, 3000);',
    '  send("HELLO");',
    '})();'
  ].join('\n');

  /* ══════════════════════════════════════════════════════════════════
     PresenterLink — 팝업 생성·문서 작성·직접 렌더·채택·하트비트 (§9)
     ══════════════════════════════════════════════════════════════════ */
  function createPresenterLink(deck, themeStore, config) {
    config = config || {};
    var doc = global.document;
    var deckId = config.deckId;

    var win = null;              /* 채택된 팝업 창 */
    var sessionId = null;
    var windowName = null;
    var pongCounter = 0;
    var tickTimer = null;
    var clockTimer = null;
    var lastFailure = null;
    var onStatus = config.onStatus || function () {};
    var onCommand = config.onCommand || function () {};

    var TEXT = {
      lost: '청중 창과 연결이 끊겼습니다.',
      parentGone: '청중 창이 닫혔거나 새로고침되었습니다. 이 창을 닫으세요.',
      badgeLive: '연결됨',
      badgeLost: '연결 끊김',
      blocked: '발표자 창을 열지 못했습니다. 브라우저의 팝업 차단을 해제한 뒤 다시 시도하세요.',
      stale: '청중 창을 새로고침해 이전 발표자 창과의 연결이 끊겼습니다. 발표자 창을 다시 열어 주세요.',
      noNext: '다음 슬라이드가 없습니다'
    };

    /* ── 팝업 문서 접근 가능 여부. file://에서 부모가 재로드되면 영구히 불가능하다
       (0단계 스파이크 확정: Chrome·Edge 모두 SecurityError). ── */
    function docOf(target) {
      if (!target) return null;
      try {
        if (target.closed) return null;
        var d = target.document;
        return d && d.body ? d : null;
      } catch (e) {
        return null;
      }
    }

    /* 부모의 인라인 <style>을 전부 복사한다. 번들에서는 kit CSS와 @font-face가
       모두 인라인이므로, 이 한 번의 복사로 미리보기 줄바꿈이 실제 화면과 일치한다(§9.6). */
    function copyStyles(pdoc) {
      var styles = doc.querySelectorAll('style');
      for (var i = 0; i < styles.length; i++) {
        var s = pdoc.createElement('style');
        if (styles[i].hasAttribute('data-presenter-runtime')) {
          s.setAttribute('data-presenter-runtime', '');
        }
        s.textContent = styles[i].textContent;
        pdoc.head.appendChild(s);
      }
    }

    /* 레이아웃(사용자 지정): 좌 = 타이머·현재 시각 + 대형 현재 슬라이드 + 하단 도구·카운터·이전/다음,
       우 = 다음 슬라이드 미리보기 + 발표자 노트(글자 크기 조절). 상단은 얇은 상태 바. */
    function consoleMarkup() {
      return '' +
      '<div class="presenter-console" id="' + PID.root + '" data-pv-link="live">' +
        '<header class="pv-topbar">' +
          '<span class="pv-chip" id="' + PID.link + '">' + TEXT.badgeLive + '</span>' +
          '<span class="pv-deck">' + '발표자 화면' + '</span>' +
          '<div class="pv-topbar-actions">' +
            '<button type="button" class="pv-tbtn" id="' + PID.theme + '" data-pv-cmd="THEME" title="테마 전환" aria-label="라이트·다크 테마 전환">' +
              icon('theme') + '<span>테마</span></button>' +
            '<button type="button" class="pv-tbtn" id="' + PID.print + '" data-pv-cmd="PRINT" title="PDF로 저장" aria-label="PDF로 저장">' +
              icon('print') + '<span>PDF</span></button>' +
            '<button type="button" class="pv-tbtn pv-tbtn--quit" id="' + PID.quit + '" data-pv-cmd="QUIT" title="발표자 화면 닫기" aria-label="발표자 화면 닫기">' +
              icon('quit') + '<span>발표자 화면 닫기</span></button>' +
          '</div>' +
        '</header>' +

        '<p class="pv-notice" id="' + PID.notice + '" role="status" hidden></p>' +

        '<div class="pv-body">' +
          '<section class="pv-stage" aria-label="현재 슬라이드">' +
            '<div class="pv-stage-head">' +
              '<div class="pv-timer-wrap">' +
                '<span class="pv-timer" id="' + PID.timer + '">0:00:00</span>' +
                '<button type="button" class="pv-iconbtn" id="' + PID.timerToggle + '" data-pv-cmd="TIMER_TOGGLE" title="타이머 시작·일시정지" aria-label="타이머 시작 또는 일시정지">' +
                  icon('play') + '</button>' +
                '<button type="button" class="pv-iconbtn" id="' + PID.timerReset + '" data-pv-cmd="TIMER_RESET" title="타이머 초기화" aria-label="타이머 초기화">' +
                  icon('reset') + '</button>' +
              '</div>' +
              '<span class="pv-clock" id="' + PID.clock + '"></span>' +
            '</div>' +
            '<div class="pv-stage-frame">' +
              '<div class="pv-preview pv-preview--main" id="' + PID.now + '"></div>' +
            '</div>' +
            '<p class="pv-slide-title" id="' + PID.title + '"></p>' +
            '<div class="pv-stagebar">' +
              '<div class="pv-tools">' +
                '<button type="button" class="pv-iconbtn" id="' + PID.black + '" data-pv-cmd="BLACKOUT" title="화면 가리기 (B)" aria-label="청중 화면 가리기">' +
                  icon('black') + '</button>' +
                '<span class="pv-jump">' +
                  '<input class="pv-input" id="' + PID.goto + '" type="number" min="1" inputmode="numeric" placeholder="번호" aria-label="이동할 슬라이드 번호">' +
                  '<button type="button" class="pv-tbtn" id="' + PID.go + '" data-pv-cmd="GOTO">이동</button>' +
                '</span>' +
              '</div>' +
              '<div class="pv-pager">' +
                '<button type="button" class="pv-navbtn" id="' + PID.prev + '" data-pv-cmd="PREV" title="이전 슬라이드" aria-label="이전 슬라이드">' +
                  icon('prev') + '</button>' +
                '<span class="pv-count" id="' + PID.pos + '">-</span>' +
                '<button type="button" class="pv-navbtn" id="' + PID.next + '" data-pv-cmd="NEXT" title="다음 슬라이드" aria-label="다음 슬라이드">' +
                  icon('next') + '</button>' +
              '</div>' +
            '</div>' +
          '</section>' +

          '<aside class="pv-side">' +
            '<section class="pv-side-block">' +
              '<h2 class="pv-h">다음 슬라이드</h2>' +
              '<div class="pv-preview pv-preview--next" id="' + PID.nextPrev + '"></div>' +
              '<p class="pv-next-title" id="' + PID.nextTitle + '"></p>' +
            '</section>' +
            '<section class="pv-side-block pv-side-block--notes">' +
              '<div class="pv-notes-head">' +
                '<h2 class="pv-h">슬라이드 노트</h2>' +
                '<span class="pv-chip pv-chip--soft" id="' + PID.noteBadge + '">기본 멘트</span>' +
                '<button type="button" class="pv-tbtn" id="' + PID.noteReset + '" data-pv-cmd="NOTE_RESET" title="기본 멘트로 되돌리기">' +
                  icon('undo') + '<span>기본 멘트</span></button>' +
              '</div>' +
              '<textarea class="pv-note" id="' + PID.note + '" spellcheck="false" aria-label="발표자 노트"></textarea>' +
              '<div class="pv-notes-foot">' +
                '<p class="pv-save" id="' + PID.save + '" role="status"></p>' +
                '<span class="pv-fontsize">' +
                  '<button type="button" class="pv-iconbtn pv-iconbtn--sm" id="' + PID.noteSmaller + '" title="노트 글자 작게" aria-label="노트 글자 작게">A<span class="pv-sup">−</span></button>' +
                  '<button type="button" class="pv-iconbtn pv-iconbtn--sm" id="' + PID.noteLarger + '" title="노트 글자 크게" aria-label="노트 글자 크게">A<span class="pv-sup">＋</span></button>' +
                '</span>' +
              '</div>' +
            '</section>' +
          '</aside>' +
        '</div>' +
      '</div>';
    }

    /* 팝업 문서를 **처음부터** 작성한다. 재작성 시 죽은 리스너·낡은 DOM이 남지 않도록
       document.open()으로 문서를 통째로 비우고 다시 그린다(§9.1-5). */
    function writeDocument(target) {
      var pdoc = docOf(target);
      if (!pdoc) return false;
      try {
        pdoc.open();
        pdoc.write('<!doctype html><html lang="ko"><head><meta charset="utf-8">' +
                   '<title>발표자 화면 — ' + deckId + '</title></head><body></body></html>');
        pdoc.close();
      } catch (e) {
        return false;
      }
      pdoc = docOf(target);
      if (!pdoc) return false;

      copyStyles(pdoc);
      /* 덱 CSS를 통째로 복사하므로 html/body의 높이·여백·변형 규칙이 따라 들어온다.
         변형된 조상이 있으면 position:fixed의 기준이 뷰포트가 아니게 되어 콘솔이
         화면을 못 채운다. 팝업 문서에만 붙는 표식을 두고 그 규칙만 되돌린다. */
      pdoc.documentElement.setAttribute('data-pv-window', 'presenter');
      themeStore.apply(pdoc, themeStore.get());
      pdoc.body.innerHTML = consoleMarkup();

      var cfg = {
        tag: PROTOCOL.tag,
        version: PROTOCOL.version,
        deckId: deckId,
        sessionId: sessionId,
        ids: PID,
        text: TEXT,
        keys: bootstrapKeyTable(),
        /* 레이아웃 상수 — CSS와 값이 갈리지 않도록 여기 한 곳에서만 정한다. */
        sideMin: 340,   /* 오른쪽(다음 슬라이드·노트) 최소 폭 */
        gap: 18,        /* .pv-body의 좌우 간격 */
        stackAt: 1080   /* 이 폭 이하에서는 1단으로 접는다 */
      };
      try {
        var script = pdoc.createElement('script');
        script.textContent = BOOTSTRAP_SOURCE.replace('__CONFIG__', JSON.stringify(cfg));
        pdoc.body.appendChild(script);
      } catch (e) {
        return false;
      }
      return true;
    }

    /* KEYMAP 하나에서 팝업 키 테이블도 만든다(도움말·키 처리 정본 단일화). */
    function bootstrapKeyTable() {
      var table = {};
      var map = { next: 'NEXT', prev: 'PREV', first: 'FIRST', last: 'LAST', blackout: 'BLACKOUT' };
      for (var i = 0; i < KEYMAP.length; i++) {
        var entry = KEYMAP[i];
        if (!map[entry.id]) continue;
        for (var j = 0; j < entry.keys.length; j++) {
          table[String(entry.keys[j]).toLowerCase()] = map[entry.id];
        }
      }
      return table;
    }

    /* ── §9.6 미리보기 복제 (최소 안전 집합) ── */
    function renderPreview(pdoc, hostId, index) {
      var host = pdoc.getElementById(hostId);
      if (!host) return;
      host.textContent = '';
      var slide = deck.getSlide(index);
      if (!slide) {
        var empty = pdoc.createElement('p');
        empty.className = 'pv-empty';
        empty.textContent = TEXT.noNext;
        host.appendChild(empty);
        return;
      }
      applyScale(host);

      var clone = pdoc.importNode(slide, true);
      clone.setAttribute('data-presenter-preview', '');
      clone.setAttribute('aria-hidden', 'true');
      clone.classList.add('is-active');           /* 덱 CSS의 .slide.is-active 배치를 그대로 쓴다 */
      var ided = clone.querySelectorAll('[id]');
      for (var i = 0; i < ided.length; i++) ided[i].removeAttribute('id');
      if (clone.hasAttribute('id')) clone.removeAttribute('id');
      var scripts = clone.querySelectorAll('script');
      for (var j = 0; j < scripts.length; j++) {
        if (scripts[j].parentNode) scripts[j].parentNode.removeChild(scripts[j]);
      }
      host.appendChild(clone);
    }

    /* ── 부모 → 팝업: 직접 DOM 조작이 유일 경로다(메시지 없음) ── */
    function render() {
      var pdoc = docOf(win);
      if (!pdoc) return false;
      if (!pdoc.getElementById(PID.root)) {
        /* 팝업이 새로고침돼 내용이 사라졌다 → 처음부터 다시 작성한다(§9.4). */
        if (!writeDocument(win)) return false;
        pdoc = docOf(win);
        if (!pdoc) return false;
      }
      var snap = deck.snapshot();
      var pos = pdoc.getElementById(PID.pos);
      if (pos) pos.textContent = '슬라이드 ' + (snap.index + 1) + ' / ' + snap.count;
      var title = pdoc.getElementById(PID.title);
      if (title) title.textContent = snap.title || '';
      var nextTitle = pdoc.getElementById(PID.nextTitle);
      if (nextTitle) {
        nextTitle.textContent = (snap.index + 1 < snap.count) ? (deck.getTitle(snap.index + 1) || '') : '';
      }
      var black = pdoc.getElementById(PID.black);
      if (black) {
        black.setAttribute('aria-pressed', snap.blackout ? 'true' : 'false');
        black.setAttribute('title', snap.blackout ? '가리기 해제 (B)' : '화면 가리기 (B)');
      }
      var prevBtn = pdoc.getElementById(PID.prev);
      var nextBtn = pdoc.getElementById(PID.next);
      if (prevBtn) prevBtn.disabled = snap.index <= 0;
      if (nextBtn) nextBtn.disabled = snap.index >= snap.count - 1;

      /* 왼쪽 칸 폭은 팝업이 자기 크기를 기준으로 정한다 — 복제 전에 확정돼야
         배율이 최종 박스 크기와 맞는다. */
      try { if (win && win.__pvRescale) win.__pvRescale(); } catch (e) { /* 무시 */ }
      renderPreview(pdoc, PID.now, snap.index);
      renderPreview(pdoc, PID.nextPrev, snap.index + 1);
      themeStore.apply(pdoc, themeStore.get());
      renderClock(pdoc);
      if (config.onRender) config.onRender(pdoc, snap);
      pongCounter += 1;
      try { pdoc.body.setAttribute('data-pv-pong', String(pongCounter)); } catch (e) { /* 무시 */ }
      return true;
    }

    /* ── 타이머·현재 시각: 상태는 부모가 소유하고 sessionStorage에 남긴다(§10.3) ── */
    var timer = { running: false, elapsed: 0, since: 0 };
    (function restoreTimer() {
      var raw = sessionStore.get(KEYS.timer(deckId));
      if (!raw) return;
      try {
        var parsed = JSON.parse(raw);
        if (parsed && typeof parsed.elapsed === 'number') timer.elapsed = parsed.elapsed;
      } catch (e) { /* 손상값은 무시 — 조용히 퇴화 */ }
    })();

    function persistTimer() {
      sessionStore.set(KEYS.timer(deckId), JSON.stringify({ elapsed: timerElapsed() }));
    }
    function timerElapsed() {
      return timer.elapsed + (timer.running ? (Date.now() - timer.since) : 0);
    }
    function formatElapsed(ms) {
      var total = Math.floor(ms / 1000);
      var h = Math.floor(total / 3600);
      var m = Math.floor((total % 3600) / 60);
      var s = total % 60;
      return h + ':' + (m < 10 ? '0' : '') + m + ':' + (s < 10 ? '0' : '') + s;
    }
    function toggleTimer() {
      if (timer.running) { timer.elapsed = timerElapsed(); timer.running = false; }
      else { timer.since = Date.now(); timer.running = true; }
      persistTimer();
      renderClock(docOf(win));
    }
    function resetTimer() {
      timer.elapsed = 0;
      timer.since = Date.now();
      persistTimer();
      renderClock(docOf(win));
    }
    /* 부모는 권위 있는 타이머 상태만 DOM으로 publish한다(부모→팝업 직접 DOM 경로).
       초 단위 갱신은 팝업 bootstrap이 한다 — 부모 창은 포커스를 잃으면 타이머가 스로틀된다. */
    function renderClock(pdoc) {
      if (!pdoc) return;
      var root = pdoc.getElementById(PID.root);
      if (root) {
        root.setAttribute('data-pv-timer', JSON.stringify({
          running: timer.running,
          elapsed: timerElapsed()
        }));
      }
      var t = pdoc.getElementById(PID.timer);
      if (t && !timer.running) t.textContent = formatElapsed(timerElapsed());
      var toggle = pdoc.getElementById(PID.timerToggle);
      if (toggle) {
        toggle.innerHTML = icon(timer.running ? 'pause' : 'play');
        toggle.setAttribute('aria-label', timer.running ? '타이머 일시정지' : '타이머 시작');
      }
    }

    /* 미리보기 배율 — 제한이 걸리는 축 기준으로 축소해 항상 전체가 보이게 한다(레터박스).
       폭만 쓰면 박스가 세로로 눌렸을 때 중앙 정렬된 슬라이드의 위아래가 잘린다. */
    function applyScale(host) {
      var w = host.clientWidth || host.offsetWidth || 0;
      var h = host.clientHeight || host.offsetHeight || 0;
      if (w > 0 && h > 0) host.style.setProperty('--scale', String(Math.min(w / 1280, h / 720)));
    }

    /* 하트비트 겸 상태 감시. 부모→팝업 경로가 직접 DOM이므로 여기서도 DOM으로 신호한다. */
    function tick() {
      if (!win) return;
      if (win.closed) { detach('closed'); return; }
      var pdoc = docOf(win);
      if (!pdoc) { detach('lost'); return; }
      pongCounter += 1;
      try { pdoc.body.setAttribute('data-pv-pong', String(pongCounter)); } catch (e) { detach('lost'); }
    }

    function detach(reason) {
      win = null;
      if (tickTimer) { clearInterval(tickTimer); tickTimer = null; }
      if (clockTimer) { clearInterval(clockTimer); clockTimer = null; }
      deck.setPresenter(reason === 'closed' ? 'closed' : 'lost');
      onStatus(reason, null);
    }

    /* ── §9.5 팝업 실패 정책 ──
       발표자 DOM은 팝업 문서 안에서만 만들어진다. 실패 경로에서는 아무것도 만들지 않으므로
       청중 화면에 메모·다음 슬라이드·타이머가 노출되는 경로 자체가 존재하지 않는다. */
    function fail(reason) {
      lastFailure = reason;
      win = null;
      deck.setPresenter('closed');
      onStatus('blocked', reason);
      return false;
    }

    function open() {
      if (win && !win.closed && docOf(win)) { try { win.focus(); } catch (e) {} return true; }

      sessionId = 'pv' + Math.floor(Math.random() * 1e9).toString(36) +
                  Math.floor(Math.random() * 1e9).toString(36);
      windowName = 'pv-' + deckId + '-' + sessionId;   /* 열 때마다 고유 → 다른 탭 팝업을 가로채지 않는다 */

      var opened = null;
      try {
        opened = global.open('', windowName, 'popup=yes,width=1440,height=940');
      } catch (e) {
        return fail(TEXT.blocked);
      }
      if (!opened || !docOf(opened)) return fail(TEXT.blocked);

      win = opened;
      if (!writeDocument(win)) { return fail(TEXT.blocked); }

      sessionStore.set(KEYS.sid(deckId), sessionId);
      deck.setPresenter('open');
      render();
      if (tickTimer) clearInterval(tickTimer);
      tickTimer = setInterval(tick, 3000);
      if (clockTimer) clearInterval(clockTimer);
      clockTimer = setInterval(function () { renderClock(docOf(win)); }, 1000);
      onStatus('open', null);
      try { win.focus(); } catch (e) {}
      return true;
    }

    function close() {
      var target = win;
      detach('closed');
      try { if (target && !target.closed) target.close(); } catch (e) {}
    }

    /* ── §9.3 메시지 검증: 모두 만족해야 수용한다 ── */
    function accepts(event) {
      var d = event.data;
      if (!d || d.t !== PROTOCOL.tag || d.v !== PROTOCOL.version) return false;
      if (d.deckId !== deckId) return false;
      /* file://에서 origin은 "null"일 수 있으므로 http(s)일 때만 origin을 본다. */
      var proto = String(global.location.protocol);
      if ((proto === 'http:' || proto === 'https:') && event.origin !== global.location.origin) return false;
      if (event.source === global) return false;
      return true;
    }

    function handleMessage(event) {
      if (!accepts(event)) return;
      var d = event.data;

      if (d.kind === 'HELLO') {
        if (win && event.source === win) {              /* 이미 채택된 팝업의 재HELLO */
          try { win.__pvAdopt(); } catch (e) {}
          render();
          return;
        }
        if (win && docOf(win)) {                        /* 다른 팝업이 붙으려 한다 */
          try { event.source.postMessage({ t: PROTOCOL.tag, v: PROTOCOL.version, kind: 'REJECT', deckId: deckId, reason: 'already-paired' }, '*'); } catch (e) {}
          return;
        }
        /* 청중 창을 새로고침한 경우다. 옛 팝업의 DOM에는 영구히 접근할 수 없으므로
           (0단계 확정) 재채택하지 않고, 좀비에 자폐를 명령한 뒤 다시 열기를 안내한다. */
        try { event.source.postMessage({ t: PROTOCOL.tag, v: PROTOCOL.version, kind: 'PARENT_CLOSE', deckId: deckId }, '*'); } catch (e) {}
        deck.setPresenter('lost');
        onStatus('stale', TEXT.stale);
        return;
      }

      if (!win || event.source !== win || d.sessionId !== sessionId) return;   /* 채택 후 검증 */

      /* PING에 전체 렌더로 답하지 않는다 — 3초마다 미리보기를 다시 복제하면 낭비이고,
         편집 중인 메모를 덮어쓴다. 살아 있다는 표시만 갱신한다. */
      if (d.kind === 'PING') { tick(); return; }
      onCommand(d);
    }

    global.addEventListener('message', handleMessage, false);

    return {
      open: open,
      close: close,
      render: render,
      toggleTimer: toggleTimer,
      resetTimer: resetTimer,
      renderClock: function () { renderClock(docOf(win)); },
      isOpen: function () { return !!(win && !win.closed && docOf(win)); },
      lastFailure: function () { return lastFailure; },
      document: function () { return docOf(win); },
      sessionId: function () { return sessionId; },
      text: TEXT
    };
  }

  /* ══════════════════════════════════════════════════════════════════
     boot — 덱 크롬 통합(§20-4)
     덱에는 자체 엔진이 이미 있고 document에 keydown(버블)을 걸어 둔다. 그 엔진을
     삭제할 수는 없으므로(배포본 불변) 두 가지로 무력화한다:
       ① window **캡처** 단계 keydown에서 stopImmediatePropagation → document 버블 리스너 미도달
       ② 크롬 버튼을 cloneNode로 교체 → 옛 click 리스너만 사라지고 마크업·외형은 그대로
     그 결과 슬라이드 전이는 항상 goTo() 하나를 지난다.
     ══════════════════════════════════════════════════════════════════ */
  /* ══════════════════════════════════════════════════════════════════
     NoteStore — defaultNote(HTML 내장·읽기 전용) + savedNote(localStorage 편집본) (§11.4)
     표시값 = savedNote가 있으면 savedNote, 없으면 defaultNote.
     ══════════════════════════════════════════════════════════════════ */
  var NOTE_KIND_LABEL = { joke: '강사 설명·애드리브', demo: '시연', hint: '학생 안내' };

  function createNoteStore(deckId, doc) {
    var defaults = {};
    var block = doc.querySelector('script[type="application/json"][data-presenter-notes]');
    if (block) {
      try {
        var parsed = JSON.parse(block.textContent || '{}');
        if (parsed && typeof parsed === 'object') defaults = parsed.notes || parsed;
      } catch (e) { defaults = {}; }
    }

    /* 이모지를 저장하지 않는다 — kind 코드만 담고 라벨은 여기서 붙인다(§11.3). */
    function defaultText(slideId) {
      var items = defaults[slideId];
      if (!items || !items.length) return '';
      var lines = [];
      for (var i = 0; i < items.length; i++) {
        var it = items[i] || {};
        var label = NOTE_KIND_LABEL[it.kind] || '';
        lines.push((label ? '[' + label + '] ' : '') + String(it.text == null ? '' : it.text));
      }
      return lines.join('\n\n');
    }

    return {
      hasDefaults: function () { for (var k in defaults) { if (Object.prototype.hasOwnProperty.call(defaults, k)) return true; } return false; },
      defaultText: defaultText,
      savedText: function (slideId) { return localStore.get(KEYS.note(deckId, slideId)); },
      displayText: function (slideId) {
        var saved = this.savedText(slideId);
        return saved == null ? defaultText(slideId) : saved;
      },
      isEdited: function (slideId) { return this.savedText(slideId) != null; },
      /** 저장 결과를 그대로 돌려준다 — 실패를 숨기지 않는다(목표 #13). */
      save: function (slideId, text) {
        if (text === defaultText(slideId)) { return this.reset(slideId) ? 'reset' : 'fail'; }
        return localStore.set(KEYS.note(deckId, slideId), text) ? 'ok' : 'fail';
      },
      reset: function (slideId) {
        if (!localStore.available()) return false;
        localStore.remove(KEYS.note(deckId, slideId));
        return true;
      },
      storageAvailable: function () { return localStore.available(); }
    };
  }

  function boot(options) {
    options = options || {};
    var doc = global.document;
    var root = doc.documentElement;
    var deckId = options.deckId || root.getAttribute('data-deck-id') || 'deck';

    var themeStore = createThemeStore();
    var deck = createDeckState({ document: doc, deckId: deckId, themeStore: themeStore });
    themeStore.init([doc]);

    if (!deck.getCount()) return null;

    /* ── 크롬 재바인딩: 옛 리스너를 떼되 마크업은 한 글자도 바꾸지 않는다 ── */
    function rebind(id) {
      var el = doc.getElementById(id);
      if (!el || !el.parentNode) return el;
      var fresh = el.cloneNode(true);
      el.parentNode.replaceChild(fresh, el);
      return fresh;
    }

    var menuEl = doc.getElementById(ID.presentationMenu);
    var helpEl = doc.getElementById(ID.keyboardHelp);
    var slideListEl = rebind(ID.slideList);
    var pageInputEl = rebind(ID.pageInput);

    function isOpen(el) { return !!(el && !el.hidden); }
    function setOpen(el, on) {
      if (!el) return;
      el.hidden = !on;
      el.classList.toggle('show', !!on);   /* 덱 규약과 동일 */
      var btn = el === menuEl ? doc.getElementById(ID.menuBtn) : null;
      if (btn) btn.setAttribute('aria-expanded', on ? 'true' : 'false');
    }

    /* ── 청중 창 상태 안내(§9.5) — 메뉴 안에만 만든다.
       메모·다음 슬라이드·타이머 DOM은 청중 문서에 **생성 자체를 하지 않는다**. ── */
    var statusEl = null;
    function status(message, tone, actionLabel, action) {
      if (!menuEl) return;
      if (!statusEl) {
        statusEl = doc.createElement('div');
        statusEl.className = 'presenter-status';
        menuEl.appendChild(statusEl);
      }
      statusEl.textContent = '';
      statusEl.hidden = !message;
      if (tone) statusEl.setAttribute('data-pv-tone', tone);
      else statusEl.removeAttribute('data-pv-tone');
      if (!message) return;
      statusEl.appendChild(doc.createTextNode(message));
      if (actionLabel && action) {
        var btn = doc.createElement('button');
        btn.type = 'button';
        btn.textContent = actionLabel;
        btn.addEventListener('click', action, false);
        statusEl.appendChild(btn);
      }
    }

    /* ── 발표자 링크 ── */
    var link = createPresenterLink(deck, themeStore, {
      deckId: deckId,
      onStatus: function (kind, detail) {
        if (kind === 'open') { status('', null); return; }
        if (kind === 'blocked') { status(detail || link.text.blocked, 'warn', '다시 시도', openPresenter); return; }
        if (kind === 'stale') { status(detail || link.text.stale, 'warn', '발표자 창 다시 열기', openPresenter); return; }
        if (kind === 'closed') { status('', null); return; }
        if (kind === 'lost') { status(link.text.lost, 'warn', '발표자 창 다시 열기', openPresenter); return; }
      },
      onCommand: function (msg) { handleCommand(msg); },
      onRender: function (pdoc, snap) {
        renderNote(false);
        if (options.onPresenterRender) options.onPresenterRender(pdoc, snap);
      }
    });

    function openPresenter() { return link.open(); }

    /* ── 명령 처리: 팝업의 모든 조작은 여기로 모여 부모 API를 부른다 ── */
    function handleCommand(msg) {
      switch (msg.kind) {
        case 'NEXT':     flushNote(); deck.next(); break;
        case 'PREV':     flushNote(); deck.prev(); break;
        case 'FIRST':    flushNote(); deck.first(); break;
        case 'LAST':     flushNote(); deck.last(); break;
        case 'GOTO':     flushNote(); deck.goTo(msg.index); break;
        case 'BLACKOUT': deck.toggleBlackout(); break;
        case 'THEME':    deck.setTheme(themeStore.get() === 'dark' ? 'light' : 'dark', themeDocs()); break;
        case 'PRINT':    try { global.print(); } catch (e) {} break;
        case 'TIMER_TOGGLE': link.toggleTimer(); break;
        case 'TIMER_RESET':  link.resetTimer(); break;
        case 'NOTE_INPUT':   onNoteInput(msg.text); break;
        case 'NOTE_RESET':   onNoteReset(); break;
        case 'NOTE_SCALE':   localStore.set('pv:noteScale', String(msg.scale)); noteScale = msg.scale; break;
        default:
          if (options.onCommand) options.onCommand(msg, deck, link);
          break;
      }
    }

    /* ── 메모(§11.4): 저장 주체는 부모 하나뿐이다. 300ms debounce 후 저장하고
       결과를 매번 상태 줄에 반영한다. 실패는 숨기지 않는다(목표 #13). ── */
    var notes = createNoteStore(deckId, doc);
    var noteScale = parseFloat(localStore.get('pv:noteScale') || '1') || 1;
    var noteTimer = null;
    var pendingNote = null;
    var pendingSlideId = null;

    function twoDigits(n) { return (n < 10 ? '0' : '') + n; }
    function nowStamp() {
      var d = new Date();
      return twoDigits(d.getHours()) + ':' + twoDigits(d.getMinutes()) + ':' + twoDigits(d.getSeconds());
    }

    function setSaveStatus(text, tone) {
      var pdoc = link.document();
      if (!pdoc) return;
      var el = pdoc.getElementById(PID.save);
      if (!el) return;
      el.textContent = text;
      if (tone) el.setAttribute('data-pv-tone', tone); else el.removeAttribute('data-pv-tone');
    }

    function setNoteBadge() {
      var pdoc = link.document();
      if (!pdoc) return;
      var badge = pdoc.getElementById(PID.noteBadge);
      if (badge) badge.textContent = notes.isEdited(deck.snapshot().slideId) ? '수정됨' : '기본 멘트';
    }

    function commitNote() {
      if (pendingNote == null || pendingSlideId == null) return;
      var result = notes.save(pendingSlideId, pendingNote);
      if (result === 'fail') {
        setSaveStatus('저장 안 됨 — 브라우저가 저장을 막고 있습니다. 창을 닫으면 이 내용은 사라집니다.', 'warn');
      } else {
        setSaveStatus('저장됨 ' + nowStamp(), 'ok');
      }
      pendingNote = null;
      pendingSlideId = null;
      setNoteBadge();
    }

    function onNoteInput(text) {
      pendingNote = String(text == null ? '' : text);
      pendingSlideId = deck.snapshot().slideId;
      if (noteTimer) clearTimeout(noteTimer);
      noteTimer = setTimeout(commitNote, 300);
    }

    /* 슬라이드 이동 시 편집 중이던 값을 즉시 flush한 뒤 다음 메모를 로드한다. */
    function flushNote() {
      if (noteTimer) { clearTimeout(noteTimer); noteTimer = null; }
      commitNote();
    }

    function onNoteReset() {
      var slideId = deck.snapshot().slideId;
      if (noteTimer) { clearTimeout(noteTimer); noteTimer = null; }
      pendingNote = null;
      pendingSlideId = null;
      if (!notes.reset(slideId)) {
        setSaveStatus('되돌리지 못했습니다 — 브라우저가 저장소를 막고 있습니다.', 'warn');
        return;
      }
      renderNote();
      setSaveStatus('기본 멘트로 되돌렸습니다.', 'ok');
    }

    var noteRenderedFor = null;
    function renderNote(force) {
      var pdoc = link.document();
      if (!pdoc) return;
      var box = pdoc.getElementById(PID.note);
      if (!box) return;
      var slideId = deck.snapshot().slideId;
      /* 같은 슬라이드를 다시 그릴 때 편집 중인 값을 덮어쓰지 않는다. */
      if (!force && noteRenderedFor === slideId && pdoc.activeElement === box) return;
      noteRenderedFor = slideId;
      box.value = notes.displayText(slideId);          /* value 경로 — innerHTML 사용 금지 */
      box.setAttribute('data-pv-scale', String(noteScale));
      box.style.fontSize = (17 * noteScale).toFixed(1) + 'px';
      setNoteBadge();
      if (!notes.storageAvailable()) {
        setSaveStatus('저장 안 됨 — 브라우저가 저장을 막고 있습니다. 창을 닫으면 편집 내용이 사라집니다.', 'warn');
      } else {
        setSaveStatus('', null);
      }
    }

    function themeDocs() {
      var docs = [doc];
      var pdoc = link.document();
      if (pdoc) docs.push(pdoc);
      return docs;
    }

    /* ── 액션(키·버튼 공통 진입점) ── */
    function runAction(id) {
      switch (id) {
        case 'next':  deck.next(); break;
        case 'prev':  deck.prev(); break;
        case 'first': deck.first(); break;
        case 'last':  deck.last(); break;
        case 'blackout': deck.toggleBlackout(); break;
        case 'menu':
          if (isOpen(menuEl)) { setOpen(menuEl, false); }
          else { setOpen(helpEl, false); setOpen(menuEl, true); }
          break;
        case 'help':
          if (isOpen(helpEl)) { setOpen(helpEl, false); }
          else { setOpen(menuEl, false); buildHelp(); setOpen(helpEl, true); }
          break;
        case 'fullscreen': toggleFullscreen(); break;
        case 'presenter': openPresenter(); break;
        case 'escape':
          if (isOpen(helpEl)) setOpen(helpEl, false);
          else if (isOpen(menuEl)) setOpen(menuEl, false);
          else if (deck.isBlackout()) deck.setBlackout(false);
          break;
      }
    }

    /* ── 도움말: KEYMAP 하나에서 생성한다(문구와 실제 키가 어긋날 수 없다) ── */
    function buildHelp() {
      if (!helpEl) return;
      var list = helpEl.querySelector('[data-pv-keymap]');
      if (!list) {
        list = doc.createElement('dl');
        list.setAttribute('data-pv-keymap', '');
        helpEl.appendChild(list);
      }
      list.textContent = '';
      for (var i = 0; i < KEYMAP.length; i++) {
        var dt = doc.createElement('dt');
        dt.textContent = KEYMAP[i].label;
        var dd = doc.createElement('dd');
        dd.textContent = KEYMAP[i].desc;
        list.appendChild(dt);
        list.appendChild(dd);
      }
    }

    /* ── 전체화면: 표준 + webkit 폴백 + 실패 안내 ── */
    function fullscreenElement() { return doc.fullscreenElement || doc.webkitFullscreenElement || null; }
    function toggleFullscreen() {
      var promise = null;
      try {
        if (!fullscreenElement()) {
          promise = root.requestFullscreen ? root.requestFullscreen()
                  : (root.webkitRequestFullscreen ? root.webkitRequestFullscreen() : null);
        } else {
          promise = doc.exitFullscreen ? doc.exitFullscreen()
                  : (doc.webkitExitFullscreen ? doc.webkitExitFullscreen() : null);
        }
      } catch (e) {
        status('전체화면을 전환하지 못했습니다. 브라우저 설정을 확인하세요.', 'warn');
        return;
      }
      if (promise && typeof promise.catch === 'function') {
        promise['catch'](function () {
          status('전체화면을 전환하지 못했습니다. 브라우저 설정을 확인하세요.', 'warn');
        });
      }
    }
    function onFullscreenChange() {
      var btn = doc.getElementById(ID.fsBtn);
      if (btn) btn.setAttribute('aria-pressed', fullscreenElement() ? 'true' : 'false');
    }
    doc.addEventListener('fullscreenchange', onFullscreenChange, false);
    doc.addEventListener('webkitfullscreenchange', onFullscreenChange, false);

    /* ── 키보드: window 캡처 단계에서 덱 자체 엔진보다 먼저 잡는다 ── */
    function isTextEntry(target) {
      if (!target) return false;
      var tag = String(target.tagName || '').toLowerCase();
      return tag === 'input' || tag === 'textarea' || tag === 'select' || target.isContentEditable === true;
    }

    global.addEventListener('keydown', function (e) {
      if (e.isComposing || e.keyCode === 229) return;          /* IME 조합 중 */
      if (e.ctrlKey || e.altKey || e.metaKey) return;

      if (isTextEntry(e.target)) {
        /* 포커스가 입력 요소면 모든 단축키가 무동작이다(§8-5).
           단, 번호 입력의 Enter는 우리가 처리하고 덱 엔진에는 넘기지 않는다. */
        if (e.target === pageInputEl && e.key === 'Enter') {
          e.preventDefault();
          e.stopImmediatePropagation();
          jumpFromInput();
        }
        return;
      }

      var entry = keymapLookup(e.key);
      if (!entry) return;

      e.preventDefault();
      e.stopImmediatePropagation();                            /* 덱 자체 엔진 무력화 */

      /* 모달이 열려 있거나 blackout 중이면 이동 키만 막는다. Esc·B·?·G는 항상 동작. */
      if (entry.move && (isOpen(menuEl) || isOpen(helpEl) || deck.isBlackout())) return;
      runAction(entry.id);
    }, true);

    /* ── 버튼 배선 ── */
    function bindClick(id, fn) {
      var el = rebind(id);
      if (el) el.addEventListener('click', fn, false);
      return el;
    }

    function jumpFromInput() {
      if (!pageInputEl) return;
      var n = parseInt(pageInputEl.value, 10);
      if (isNaN(n)) return;
      deck.goTo(n - 1);
      setOpen(menuEl, false);
    }

    bindClick(ID.prevBtn, function () { deck.prev(); });
    bindClick(ID.nextBtn, function () { deck.next(); });
    bindClick(ID.menuBtn, function () { runAction('menu'); });
    bindClick(ID.counter, function () { runAction('menu'); });
    bindClick(ID.menuClose, function () { setOpen(menuEl, false); });
    bindClick(ID.fsBtn, function () { toggleFullscreen(); });
    bindClick(ID.homeBtn, function () { deck.first(); setOpen(menuEl, false); });
    bindClick(ID.goBtn, jumpFromInput);
    bindClick(ID.pdfBtn, function () { try { global.print(); } catch (e) {} });
    bindClick(ID.helpBtn, function () { runAction('help'); });
    bindClick(ID.helpClose, function () { setOpen(helpEl, false); });

    /* ── 하단 네비게이션에 발표자 모드 진입 버튼을 만든다 ──
       §9.1은 발표자 창 진입에 **사용자 제스처**를 요구한다. 버튼은 런타임이 동적으로
       만들므로 주입기는 덱 마크업을 건드리지 않는다(§15 불변성 유지). 기존 크롬과 같은
       .nav-btn 클래스를 써서 외형을 맞춘다. */
    (function addPresenterButton() {
      var fs = doc.getElementById(ID.fsBtn);
      var bar = fs ? fs.parentNode : (doc.querySelector('.controls .navbar') || doc.getElementById(ID.controls));
      if (!bar || doc.getElementById('pvOpenBtn')) return;
      var btn = doc.createElement('button');
      btn.type = 'button';
      btn.id = 'pvOpenBtn';
      btn.className = fs ? fs.className : 'nav-btn';
      btn.setAttribute('aria-label', '발표자 모드 열기 (P)');
      btn.setAttribute('title', '발표자 모드 (P)');
      btn.innerHTML = icon('screen');
      btn.addEventListener('click', function () { openPresenter(); }, false);
      if (fs && fs.nextSibling) bar.insertBefore(btn, fs.nextSibling);
      else bar.appendChild(btn);
    })();

    var blackoutEl = rebind(ID.blackout);
    if (blackoutEl) blackoutEl.addEventListener('click', function () { deck.setBlackout(false); }, false);

    /* 슬라이드 목록: 덱이 만든 버튼 마크업을 그대로 두고 위임으로만 처리한다.
       인덱스는 목록 안 버튼의 순서와 1:1이다(덱 엔진이 슬라이드 순서대로 만든다). */
    function listButtons() {
      return slideListEl ? Array.prototype.slice.call(slideListEl.querySelectorAll('button')) : [];
    }
    if (slideListEl) {
      slideListEl.addEventListener('click', function (e) {
        var node = e.target;
        while (node && node !== slideListEl && String(node.tagName || '').toLowerCase() !== 'button') {
          node = node.parentNode;
        }
        if (!node || node === slideListEl) return;
        var at = listButtons().indexOf(node);
        if (at < 0) return;
        deck.goTo(at);                       /* 목록 점프도 goTo 1회 — 버튼 반복 클릭 금지 */
        setOpen(menuEl, false);
      }, false);
    }

    /* ── 구독자: 하단 네비·목록·메뉴 머리말·팝업이 모두 같은 상태를 본다 ── */
    /* ⚠️ rebind()가 노드를 복제본으로 교체하므로, 교체 대상 요소는 **캡처해 두지 말고
       매번 다시 조회한다.** 캡처하면 화면에서 떨어져 나간 옛 노드를 갱신하게 된다. */
    deck.subscribe(function (snap) {
      var counterEl = doc.getElementById(ID.counter);
      var menuTitleEl = doc.getElementById(ID.menuTitle);
      var menuPartEl = doc.getElementById(ID.menuPart);
      if (counterEl) counterEl.textContent = (snap.index + 1) + ' / ' + snap.count;
      if (menuTitleEl) menuTitleEl.textContent = snap.title || '';
      if (menuPartEl) menuPartEl.textContent = (snap.index + 1) + ' / ' + snap.count;
      var prevBtn = doc.getElementById(ID.prevBtn);
      var nextBtn = doc.getElementById(ID.nextBtn);
      if (prevBtn) prevBtn.disabled = snap.index <= 0;
      if (nextBtn) nextBtn.disabled = snap.index >= snap.count - 1;
      var buttons = listButtons();
      for (var i = 0; i < buttons.length; i++) {
        buttons[i].classList.toggle('is-current', i === snap.index);
      }
      link.render();
    });

    buildHelp();
    deck.setBlackout(false);
    deck.restorePosition();      /* sessionStorage 기준. 새 탭이면 표지에서 시작한다. */

    var api = {
      deck: deck,
      link: link,
      theme: themeStore,
      openPresenter: openPresenter,
      runAction: runAction,
      status: status,
      deckId: deckId
    };
    global.PresenterRuntime.instance = api;
    return api;
  }

  /* ══════════════════════════════════════════════════════════════════
     공개 네임스페이스
     ══════════════════════════════════════════════════════════════════ */
  global.PresenterRuntime = {
    version: RUNTIME_VERSION,
    ID: ID,
    PID: PID,
    KEYS: KEYS,
    KEYMAP: KEYMAP,
    PROTOCOL: PROTOCOL,
    keymapLookup: keymapLookup,
    selectors: { deck: SEL_DECK, slide: SEL_SLIDE },
    stores: { local: localStore, session: sessionStore },
    createThemeStore: createThemeStore,
    createDeckState: createDeckState,
    createPresenterLink: createPresenterLink,
    boot: boot,
    titleOf: titleOf,
    clamp: clamp
  };

})(window);
