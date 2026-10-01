  <script>
  /* FRAME 엔진 — 이동(data-go · 복귀) · 등장 연출 보조 · 조작 위젯 · 타이머 · 복사.
     덱 엔진(위 스크립트)이 window.__deckShow(i)를 열어 두면 그것을 쓴다.
     모든 조작은 클릭과 Enter/Space 둘 다 된다. 방향키 이동은 연출을 기다리지 않는다.
     감사 모드: 주소에 ?audit 가 있거나 <html class="no-anim">이면 연출 없이 최종 상태.
     무한 반복 연출은 없다. 위젯 상태는 페이지를 다시 열 때까지 DOM에 남는다. */
  (function(){
    'use strict';
    var root = document.documentElement;
    if (/[?&]audit\b/.test(location.search)) root.classList.add('no-anim');
    var mqReduce = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : null;
    function reduced(){ return !!(mqReduce && mqReduce.matches) || root.classList.contains('no-anim'); }
    var NS = 'http://www.w3.org/2000/svg';
    var slides = [].slice.call(document.querySelectorAll('.deck .slide'));
    function all(sel, el){ return [].slice.call((el || document).querySelectorAll(sel)); }
    function idxOf(id){ for (var i = 0; i < slides.length; i++){ if (slides[i].getAttribute('data-slide') === id) return i; } return -1; }
    function slideOf(el){ return el && el.closest ? el.closest('.slide') : null; }
    var store = {
      get: function(k){ try { return sessionStorage.getItem(k); } catch (e) { return null; } },
      set: function(k, v){ try { sessionStorage.setItem(k, v); } catch (e) {} }
    };

    /* ── 이동 — 번호 없이 data-go="<슬라이드ID>". data-vt-key가 출발·도착에 같으면 View Transition 0.45초 ── */
    var trail = [];
    function goId(id, src){
      var t = idxOf(id); if (t < 0 || !window.__deckShow) return false;
      var key = src && src.getAttribute && src.getAttribute('data-vt-key');
      var dest = key ? slides[t].querySelector('[data-vt-key="' + key + '"]') : null;
      if (!document.startViewTransition || reduced() || !dest){ window.__deckShow(t); return true; }
      src.style.viewTransitionName = 'frame-hero';
      var tr = document.startViewTransition(function(){ src.style.viewTransitionName = ''; dest.style.viewTransitionName = 'frame-hero'; window.__deckShow(t); });
      function clear(){ dest.style.viewTransitionName = ''; }
      tr.ready.catch(function(){}); tr.finished.then(clear, clear);
      return true;
    }
    /* 슬롯에서 나갈 때 출발 슬롯을 기억하고, 허브의 「수업으로 돌아가기」는 그 슬롯의 다음 장으로 간다 */
    function noteOrigin(from){
      if (from && (from.classList.contains('f-slot') || from.hasAttribute('data-return-to'))) store.set('frame.origin', from.getAttribute('data-slide'));
    }
    function doneList(){ return (store.get('frame.done') || '').split(',').filter(Boolean); }
    function noteDone(el){
      var p = el.getAttribute('data-pr'); if (!p) return;
      var list = doneList(); if (list.indexOf(p) < 0){ list.push(p); store.set('frame.done', list.join(',')); }
    }
    function applyMarks(slide){
      var list = doneList();
      all('[data-pr]', slide).forEach(function(e){ e.classList.toggle('is-done', list.indexOf(e.getAttribute('data-pr')) >= 0); });
    }
    function returnTarget(){
      var o = store.get('frame.origin'), oi = o ? idxOf(o) : -1;
      if (oi >= 0){
        var to = slides[oi].getAttribute('data-return-to');
        if (to && idxOf(to) >= 0) return to;
        if (slides[oi + 1]) return slides[oi + 1].getAttribute('data-slide');
      }
      for (var k = trail.length - 1; k >= 0; k--){      /* 슬롯을 거치지 않고 온 경우: 허브·실습 밖에서 마지막으로 본 장 */
        var s = slides[idxOf(trail[k])];
        if (s && !s.classList.contains('pr') && !s.classList.contains('f-hub')) return trail[k];
      }
      return null;
    }

    /* ── 위젯 data-w="toggle|step|pick" — 상태 하나(data-state)와 그 상태를 보여 주는 표식 ──
       root  : data-w · data-state(처음 상태) · (step) data-max
       조작  : data-toggle(0↔1) · data-set="값" · data-pick="값" · (step) data-next · data-prev · data-reset
       보기  : data-show="값 …"(그 상태에서만 표시) · data-hl="값 …"(그 상태에서 .is-on) · (step) data-from="n"(n 이상에서 .is-on) */
    function inList(v, list){ return (' ' + (list || '') + ' ').indexOf(' ' + v + ' ') >= 0; }
    function mine(w, e){ return e.closest('[data-w]') === w; }
    function syncWidget(w){
      var kind = w.getAttribute('data-w');
      if (kind !== 'toggle' && kind !== 'step' && kind !== 'pick') return;
      var st = w.getAttribute('data-state');
      if (st === null){
        var pre = w.querySelector('[data-pick].on, [data-pick][aria-pressed="true"]');
        st = pre ? pre.getAttribute('data-pick') : (kind === 'pick' ? '' : '0');
        w.setAttribute('data-state', st);
      }
      if (!w.hasAttribute('data-init')) w.setAttribute('data-init', st);
      all('[data-show]', w).forEach(function(e){ if (mine(w, e)) e.classList.toggle('is-on', inList(st, e.getAttribute('data-show'))); });
      all('[data-hl]', w).forEach(function(e){ if (mine(w, e)) e.classList.toggle('is-on', inList(st, e.getAttribute('data-hl'))); });
      all('[data-from]', w).forEach(function(e){ if (mine(w, e)) e.classList.toggle('is-on', (+st || 0) >= +e.getAttribute('data-from')); });
      all('[data-set], [data-pick]', w).forEach(function(c){
        if (!mine(w, c)) return;
        var v = c.hasAttribute('data-set') ? c.getAttribute('data-set') : c.getAttribute('data-pick');
        c.classList.toggle('on', v === st); c.setAttribute('aria-pressed', v === st ? 'true' : 'false');
      });
      all('[data-toggle]', w).forEach(function(c){
        if (!mine(w, c)) return;
        c.setAttribute('aria-pressed', st === '1' ? 'true' : 'false');
        var labels = c.getAttribute('data-labels');           /* "꺼진 상태 글|켜진 상태 글" */
        if (labels){ var t = labels.split('|')[st === '1' ? 1 : 0]; if (t){ (c.querySelector('.t') || c).textContent = t; } }
      });
      var max = +w.getAttribute('data-max');
      all('[data-next]', w).forEach(function(c){ if (mine(w, c) && max) c.disabled = (+st || 0) >= max; });
      all('[data-prev]', w).forEach(function(c){ if (mine(w, c)) c.disabled = (+st || 0) <= 0; });
    }
    function setState(w, v){
      w.setAttribute('data-state', v); syncWidget(w);
      var sl = slideOf(w); if (sl) buildRings(sl);      /* 새로 보이게 된 글자의 동그라미를 그린다 */
      try { w.dispatchEvent(new CustomEvent('frame:widget', { bubbles:true, detail:{ w:w.getAttribute('data-w'), state:v, id:w.id || null } })); } catch (e) {}
    }
    function widgetAct(c){
      var w = c.closest('[data-w]'); if (!w) return false;
      var kind = w.getAttribute('data-w'), st = w.getAttribute('data-state');
      if (kind === 'trace'){ if (c.hasAttribute('data-pick')){ all('[data-pick]', w).forEach(function(r){ r.classList.toggle('on', r === c); r.setAttribute('aria-pressed', r === c ? 'true' : 'false'); }); drawTrace(slideOf(w)); return true; } return false; }
      if (kind !== 'toggle' && kind !== 'step' && kind !== 'pick') return false;
      var max = +w.getAttribute('data-max') || 9999;
      if (c.hasAttribute('data-toggle')) setState(w, st === '1' ? '0' : '1');
      else if (c.hasAttribute('data-set')) setState(w, c.getAttribute('data-set'));
      else if (c.hasAttribute('data-pick')) setState(w, c.getAttribute('data-pick'));
      else if (c.hasAttribute('data-next')) setState(w, String(Math.min(max, (+st || 0) + 1)));
      else if (c.hasAttribute('data-prev')) setState(w, String(Math.max(0, (+st || 0) - 1)));
      else if (c.hasAttribute('data-reset')) setState(w, w.getAttribute('data-init') || '0');
      else return false;
      return true;
    }
    /* 단계·체크 목록 data-w="todo" — 눌러서 완료 표시(번호는 ✓로, ☐는 ☑로) */
    function todoAct(el){
      var box = el.closest('[data-w="todo"]'); if (!box) return false;
      var btn = el.closest('button'); if (!btn) return false;
      var on = btn.getAttribute('aria-pressed') !== 'true';
      btn.setAttribute('aria-pressed', on ? 'true' : 'false');
      (btn.closest('li') || btn.parentNode).classList.toggle('done', on);
      var bx = btn.querySelector('.bx'); if (bx) bx.textContent = on ? '☑' : '☐';
      var n = btn.querySelector('.n'); if (n){ if (!n.hasAttribute('data-n')) n.setAttribute('data-n', n.textContent); n.textContent = on ? '✓' : n.getAttribute('data-n'); }
      return true;
    }

    /* ── 실습 ③ 대조선 — 결과 표의 행을 고르면 근거 줄과 잇는다(글자를 가로지르지 않고 행 왼쪽 끝에서 멈춘다) ── */
    function offsetIn(el, slide){ var x = 0, y = 0; while (el && el !== slide){ x += el.offsetLeft; y += el.offsetTop; el = el.offsetParent; } return { x:x, y:y }; }
    function drawTrace(slide){
      var box = slide && slide.querySelector('[data-w="trace"]'); if (!box) return;
      var row = box.querySelector('[data-pick].on'), key = row && row.getAttribute('data-pick');
      all('[data-line]', slide).forEach(function(li){ li.classList.toggle('on', li.getAttribute('data-line') === key); });
      var svg = slide.querySelector('.ck-link'), line = key && slide.querySelector('[data-line="' + key + '"]');
      if (!row || !line || !svg || !line.offsetWidth) return;
      var src = line.closest('.win') || line.parentNode, a = offsetIn(line, slide), sx = offsetIn(src, slide).x + src.offsetWidth + 6, sy = a.y + line.offsetHeight / 2;
      var tb = row.closest('table'), ex = offsetIn(tb, slide).x - 8, ey = offsetIn(row, slide).y + row.offsetHeight / 2, mx = (sx + ex) / 2;
      svg.querySelector('path').setAttribute('d', 'M' + sx + ' ' + sy + ' C' + mx + ' ' + sy + ' ' + mx + ' ' + ey + ' ' + ex + ' ' + ey);
      var c = svg.querySelectorAll('circle'); c[0].setAttribute('cx', sx); c[0].setAttribute('cy', sy); c[1].setAttribute('cx', ex); c[1].setAttribute('cy', ey);
    }

    /* ── 동그라미(.ring-host) — 글자 둘레에 손으로 그린 듯한 타원을 만든다 ── */
    function ringPath(W, H){
      /* 둥근 사각형(알약)을 손으로 그린 듯 살짝 흔들고, 끝을 시작점 너머로 겹친다 — 글자 쪽으로는 들어오지 않는다 */
      function f(n){ return n.toFixed(1); }
      var r = Math.min(H / 2, 26), k = r * 0.5523, x0 = r, x1 = W - r, y0 = r, y1 = H - r, m = (x1 - x0);
      return 'M' + f(x0 * 0.9) + ' ' + f(2.5) +
        ' C' + f(x0 + m * .3) + ' ' + f(-1.5) + ' ' + f(x0 + m * .7) + ' ' + f(-1.5) + ' ' + f(x1) + ' ' + f(1) +
        ' C' + f(x1 + k) + ' ' + f(1) + ' ' + f(W + .5) + ' ' + f(y0 - k) + ' ' + f(W) + ' ' + f(y0) +
        ' L' + f(W) + ' ' + f(y1) +
        ' C' + f(W) + ' ' + f(y1 + k) + ' ' + f(x1 + k) + ' ' + f(H) + ' ' + f(x1) + ' ' + f(H - .5) +
        ' C' + f(x0 + m * .7) + ' ' + f(H + 2.5) + ' ' + f(x0 + m * .3) + ' ' + f(H + 2.5) + ' ' + f(x0) + ' ' + f(H - 1) +
        ' C' + f(x0 - k) + ' ' + f(H) + ' ' + f(-.5) + ' ' + f(y1 + k) + ' ' + f(0) + ' ' + f(y1) +
        ' L' + f(0) + ' ' + f(y0) +
        ' C' + f(0) + ' ' + f(y0 - k) + ' ' + f(x0 * .5) + ' ' + f(1) + ' ' + f(x0 * 1.25) + ' ' + f(5);
    }
    function buildRings(slide){
      all('.ring-host', slide).forEach(function(h){
        var w = h.offsetWidth, hh = h.offsetHeight; if (!w) return;
        var W = w + 24, H = hh + 8, svg = h.querySelector('.ring-svg');
        if (!svg){
          svg = document.createElementNS(NS, 'svg'); svg.setAttribute('class', 'ring-svg'); svg.setAttribute('aria-hidden', 'true');
          var p = document.createElementNS(NS, 'path'); p.setAttribute('class', 'em-ring a-draw'); p.setAttribute('pathLength', '100');
          svg.appendChild(p); h.appendChild(svg);
        }
        svg.setAttribute('viewBox', '0 0 ' + W + ' ' + H); svg.setAttribute('width', W); svg.setAttribute('height', H);
        svg.style.left = '-12px'; svg.style.top = '-4px';
        svg.firstChild.setAttribute('d', ringPath(W, H));
      });
    }

    /* ── 숫자 올라가기(data-count) — 0.5초, 끝나면 마크업의 최종 글자로 되돌려 놓는다 ── */
    function countUp(slide){
      if (reduced()) return;
      all('[data-count]', slide).forEach(function(e){
        if (e.__final === undefined) e.__final = e.textContent;
        var txt = e.__final, m = txt.match(/-?\d+(?:\.\d+)?/); if (!m) return;
        var pre = txt.slice(0, m.index), post = txt.slice(m.index + m[0].length), dec = (m[0].split('.')[1] || '').length, target = parseFloat(m[0]), t0 = null;
        if (e.__raf) cancelAnimationFrame(e.__raf);
        function step(ts){
          if (t0 === null) t0 = ts;
          var k = Math.min(1, (ts - t0) / 500), v = target * (1 - Math.pow(1 - k, 3));
          e.textContent = k < 1 ? pre + v.toFixed(dec) + post : e.__final;
          if (k < 1) e.__raf = requestAnimationFrame(step);
        }
        e.textContent = pre + (0).toFixed(dec) + post; e.__raf = requestAnimationFrame(step);
      });
    }

    /* ── 타이머 — 분 값은 data-min. 누르면 시작·멈춤, 0이 되면 끝 ── */
    function fmt(s){ var m = Math.floor(s / 60), r = s % 60; return (m < 10 ? '0' : '') + m + ':' + (r < 10 ? '0' : '') + r; }
    function timerInit(b){
      if (b.__t) return;
      var sec = Math.round(parseFloat(b.getAttribute('data-min')) * 60) || 0;
      b.__t = { total:sec, left:sec, id:0, end:0 };
      var tv = b.querySelector('.tv'); if (tv) tv.textContent = fmt(sec);
    }
    function timerToggle(b){
      timerInit(b);
      var t = b.__t, tv = b.querySelector('.tv'), tl = b.querySelector('.tl');
      if (t.id){ clearInterval(t.id); t.id = 0; t.left = Math.max(0, Math.ceil((t.end - Date.now()) / 1000)); if (tl) tl.textContent = '▶ 이어서'; return; }
      if (t.left <= 0){ t.left = t.total; b.classList.remove('end'); }
      t.end = Date.now() + t.left * 1000; if (tl) tl.textContent = '❚❚ 멈춤';
      t.id = setInterval(function(){
        var left = Math.max(0, Math.ceil((t.end - Date.now()) / 1000)); t.left = left; if (tv) tv.textContent = fmt(left);
        if (!left){ clearInterval(t.id); t.id = 0; b.classList.add('end'); if (tl) tl.textContent = '끝 · 다시 시작'; }
      }, 250);
    }

    /* ── 복사 — 터미널 창의 요청문에서 `>` 프롬프트와 커서를 빼고 글자만 ── */
    function termText(term){
      var src = term.querySelector('.terminal-copy'), out = '';
      if (!src) return '';
      (function walk(n){
        for (var c = n.firstChild; c; c = c.nextSibling){
          if (c.nodeType === 3){ out += c.nodeValue.replace(/\s+/g, ' '); }
          else if (c.nodeType === 1){
            if (c.classList.contains('terminal-prompt') || c.classList.contains('terminal-cursor')) continue;
            if (c.tagName === 'BR'){ out += '\n'; continue; }
            var blk = c.tagName === 'P' || c.tagName === 'DIV';
            if (blk && out && out.slice(-1) !== '\n') out += '\n';
            walk(c);
            if (blk && out.slice(-1) !== '\n') out += '\n';
          }
        }
      })(src);
      return out.replace(/[ \t]*\n[ \t]*/g, '\n').replace(/\n{3,}/g, '\n\n').trim();
    }
    function fallbackCopy(t, done){
      var ta = document.createElement('textarea'); ta.value = t; ta.setAttribute('readonly', '');
      ta.style.cssText = 'position:fixed;left:-9999px;top:0'; document.body.appendChild(ta); ta.select();
      try { document.execCommand('copy'); } catch (e) {}
      document.body.removeChild(ta); done();
    }
    function doCopy(btn){
      var term = btn.closest('.term'); if (!term) return;
      var text = termText(term), label = btn.getAttribute('data-label') || btn.textContent;
      btn.setAttribute('data-label', label);
      function done(){ btn.textContent = '복사됨'; clearTimeout(btn.__to); btn.__to = setTimeout(function(){ btn.textContent = label; }, 1500); }
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(done, function(){ fallbackCopy(text, done); });
      else fallbackCopy(text, done);
    }

    /* ── 클릭 · 키보드(Enter/Space) ── */
    function act(el){
      if (el.hasAttribute('data-return')){ var rt = returnTarget(); if (rt) goId(rt, el); return; }
      if (el.hasAttribute('data-go')){ noteOrigin(slideOf(el)); noteDone(el); goId(el.getAttribute('data-go'), el); return; }
      if (el.hasAttribute('data-copy')) return doCopy(el);
      if (el.hasAttribute('data-min')) return timerToggle(el);
      if (todoAct(el)) return;
      widgetAct(el);
    }
    var SEL = '[data-go], [data-return], [data-pick], [data-set], [data-toggle], [data-next], [data-prev], [data-reset], [data-copy], [data-min], [data-w="todo"] button';
    var NATIVE = 'button, summary, a[href], input, select, textarea';
    document.addEventListener('click', function(e){
      var el = e.target.closest ? e.target.closest(SEL) : null;
      if (!el || !slideOf(el) || el.getAttribute('aria-disabled') === 'true' || el.disabled) return;
      e.preventDefault(); e.stopPropagation(); act(el);
    });
    /* 조작 요소 위의 Enter/Space는 슬라이드를 넘기지 않는다(덱 keydown은 document에 걸려 있다) */
    slides.forEach(function(s){
      s.addEventListener('keydown', function(e){
        if (e.key !== 'Enter' && e.key !== ' ' && e.key !== 'Spacebar') return;
        var t = e.target; if (!t || !t.closest) return;
        if (t.closest(NATIVE)){ e.stopPropagation(); return; }     /* 네이티브 버튼·summary는 기본 동작이 눌러 준다 */
        var el = t.closest(SEL); if (!el) return;
        e.stopPropagation(); e.preventDefault();
        if (el.getAttribute('aria-disabled') !== 'true') act(el);
      });
    });

    /* ── 디자인 v2 그림 — 머리 글자 · 여정 지도 · 도트 · 도넛. 전부 로드 때 한 번 만든다(레이아웃 측정이 필요 없다). 초기 상태가 곧 완성본이다 ── */
    function svgEl(tag, attrs){ var e = document.createElementNS(NS, tag); for (var k in attrs) e.setAttribute(k, attrs[k]); return e; }
    /* 바닥 한 줄 머리의 .s-team — <br>을 「 · 」로 */
    function fixTeam(){
      all('.s-head .s-team').forEach(function(t){ if (t.querySelector('br')) t.innerHTML = t.innerHTML.replace(/<br\s*\/?>/gi, ' · '); });
    }
    /* 여정 지도 — 세 구간 3차 베지어 길(viewBox 1280×330). 단계 점은 길 위에, 「지금」 표는 data-now(1부터) 점 위에 */
    var JR = [ [[-10,250],[200,250],[260,150],[420,170]], [[420,170],[580,190],[700,250],[860,170]], [[860,170],[1020,90],[1120,90],[1300,110]] ];
    function bzPt(P, t){ var u = 1 - t; return [u*u*u*P[0][0] + 3*u*u*t*P[1][0] + 3*u*t*t*P[2][0] + t*t*t*P[3][0], u*u*u*P[0][1] + 3*u*u*t*P[1][1] + 3*u*t*t*P[2][1] + t*t*t*P[3][1]]; }
    function bzAtX(P, x){ var lo = 0, hi = 1, m = 0; for (var i = 0; i < 28; i++){ m = (lo + hi) / 2; if (bzPt(P, m)[0] < x) lo = m; else hi = m; } return { t:m, y:bzPt(P, m)[1] }; }
    function bzSplit(P, t){   /* 앞쪽 [0,t] 구간의 제어점 */
      function mix(a, b){ return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t]; }
      var a = mix(P[0], P[1]), b = mix(P[1], P[2]), c = mix(P[2], P[3]), d = mix(a, b), e = mix(b, c), f = mix(d, e);
      return [P[0], a, d, f];
    }
    function jrAt(x){ for (var i = 0; i < JR.length; i++){ if (x <= JR[i][3][0] || i === JR.length - 1){ var r = bzAtX(JR[i], x); return { seg:i, t:r.t, y:r.y }; } } }
    function pathD(segs){ var d = 'M' + segs[0][0][0] + ' ' + segs[0][0][1]; segs.forEach(function(P){ d += ' C' + P[1][0].toFixed(1) + ' ' + P[1][1].toFixed(1) + ' ' + P[2][0].toFixed(1) + ' ' + P[2][1].toFixed(1) + ' ' + P[3][0].toFixed(1) + ' ' + P[3][1].toFixed(1); }); return d; }
    function buildJourney(j){
      if (j.classList.contains('is-built')) return;
      var labels = [].slice.call(j.children).filter(function(c){ return c.tagName === 'SPAN' && c.textContent.trim(); });
      var n = labels.length; if (!n) return;
      var now = parseInt(j.getAttribute('data-now'), 10) || 0, tag = j.getAttribute('data-tag') || '지금';
      var xs = n === 4 ? [170, 500, 860, 1140] : labels.map(function(_, i){ return n === 1 ? 640 : 170 + i * (970 / (n - 1)); });
      var svg = svgEl('svg', { 'class':'jr-road', viewBox:'0 0 1280 330', preserveAspectRatio:'none', 'aria-hidden':'true' });
      svg.appendChild(svgEl('path', { 'class':'base', d:pathD(JR) }));
      if (now >= 1 && now <= n){
        var nx = xs[now - 1], at = jrAt(nx), part = JR.slice(0, at.seg).concat([bzSplit(JR[at.seg], at.t)]);
        svg.appendChild(svgEl('path', { 'class':'on', d:pathD(part) }));
      }
      var frag = document.createDocumentFragment(); frag.appendChild(svg);
      labels.forEach(function(sp, i){
        var x = xs[i], y = jrAt(x).y, st = i + 1 < now ? 'done' : (i + 1 === now ? 'now' : 'next');
        var text = sp.textContent.trim(), el = document.createElement('span');
        el.className = 'jr-st ' + st; el.style.left = (x / 12.8) + '%'; el.style.top = (y / 3.3) + '%';
        var big = st === 'now', d = svgEl('svg', { 'class':'jr-d', viewBox:big ? '0 0 60 60' : '0 0 22 22', 'aria-hidden':'true' });
        if (big){ d.appendChild(svgEl('circle', { 'class':'glow', cx:30, cy:30, r:30 })); d.appendChild(svgEl('circle', { 'class':'core', cx:30, cy:30, r:20 })); }
        else { d.appendChild(svgEl('circle', { 'class':'fill', cx:11, cy:11, r:11 })); d.appendChild(svgEl('circle', { 'class':'ring', cx:11, cy:11, r:9 })); }
        var b = document.createElement('b'); b.textContent = text;
        el.appendChild(d); el.appendChild(b); frag.appendChild(el);
        if (big){ var t = document.createElement('span'); t.className = 'jr-tag'; t.textContent = tag; t.style.left = (x / 12.8) + '%'; t.style.top = ((y - 44) / 3.3) + '%'; frag.appendChild(t); }
        j.removeChild(sp);
      });
      j.appendChild(frag); j.classList.add('is-built');
    }
    /* 도트 매트릭스 — data-n(칸 수) · data-on(켜진 칸) · data-cols(선택) */
    function buildDotgrid(g){
      if (g.querySelector('svg')) return;
      var n = parseInt(g.getAttribute('data-n'), 10) || 100, on = parseInt(g.getAttribute('data-on'), 10) || 0, cols = parseInt(g.getAttribute('data-cols'), 10) || Math.ceil(Math.sqrt(n)), rows = Math.ceil(n / cols), C = 34;
      var svg = svgEl('svg', { viewBox:'0 0 ' + (cols * C) + ' ' + (rows * C), 'aria-hidden':'true' });
      for (var i = 0; i < n; i++) svg.appendChild(svgEl('circle', { 'class':'d' + (i < on ? ' on' : ''), cx:(i % cols) * C + C / 2, cy:Math.floor(i / cols) * C + C / 2, r:12 }));
      g.setAttribute('role', 'img'); if (!g.hasAttribute('aria-label')) g.setAttribute('aria-label', n + '칸 중 ' + on + '칸');
      g.insertBefore(svg, g.firstChild);
    }
    /* 도넛 — data-v(0~100) */
    function buildDonut(dn){
      if (dn.querySelector('svg')) return;
      var v = Math.max(0, Math.min(100, parseFloat(dn.getAttribute('data-v')) || 0));
      var svg = svgEl('svg', { viewBox:'0 0 100 100', 'aria-hidden':'true' });
      svg.appendChild(svgEl('circle', { 'class':'tr', cx:50, cy:50, r:42 }));
      svg.appendChild(svgEl('circle', { 'class':'ar', cx:50, cy:50, r:42, pathLength:100, 'stroke-dasharray':v + ' ' + (100 - v), transform:'rotate(-90 50 50)' }));
      dn.insertBefore(svg, dn.firstChild);
    }
    function buildV2(){
      fixTeam();
      all('.journey').forEach(buildJourney); all('.dotgrid').forEach(buildDotgrid); all('.donut').forEach(buildDonut);
    }
    buildV2();

    /* ── 장이 켜질 때(감사 순회 포함) — 초기 상태를 그린다 ── */
    function withMeasure(fn){ root.classList.add('fr-measure'); try { fn(); } finally { root.classList.remove('fr-measure'); } }
    function onActivate(s){
      var id = s.getAttribute('data-slide'); if (trail[trail.length - 1] !== id){ trail.push(id); if (trail.length > 60) trail.shift(); }
      all('[data-w]', s).forEach(syncWidget);
      all('[data-min]', s).forEach(timerInit);
      buildRings(s); drawTrace(s); applyMarks(s);
      var back = s.querySelector('[data-return]'); if (back) back.hidden = !returnTarget();
      countUp(s);
    }
    slides.forEach(function(s){
      all('[data-w]', s).forEach(syncWidget);
      all('[data-min]', s).forEach(timerInit);
      all('[data-w="todo"] .n', s).forEach(function(n){ n.setAttribute('data-n', n.textContent); });
    });
    var mo = new MutationObserver(function(list){
      list.forEach(function(m){ var s = m.target; if (s.classList.contains('is-active') && (m.oldValue || '').indexOf('is-active') < 0) onActivate(s); });
    });
    slides.forEach(function(s){ mo.observe(s, { attributes:true, attributeFilter:['class'], attributeOldValue:true }); });
    var cur = slides.filter(function(s){ return s.classList.contains('is-active'); })[0]; if (cur) onActivate(cur);
    /* 인쇄(PDF) 전 · 글꼴 로드 뒤 — 화면에 없는 장도 대조선·동그라미를 미리 그려 둔다 */
    function prepAll(){ withMeasure(function(){ slides.forEach(function(s){ buildRings(s); drawTrace(s); }); }); }
    window.addEventListener('beforeprint', prepAll);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(prepAll);
    window.FRAME = { go: function(id){ return goId(id); }, origin: function(){ return store.get('frame.origin'); }, returnTarget: returnTarget, trail: trail, fmt: fmt };
  })();
  </script>
