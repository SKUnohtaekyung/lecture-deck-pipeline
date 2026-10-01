import sys
sys.stdout.reconfigure(encoding='utf-8')
p = 'tmp/frame/E1/src/frame.js'
s = open(p, encoding='utf-8').read()

marker = "    /* ── 장이 켜질 때(감사 순회 포함) — 초기 상태를 그린다 ── */"
assert marker in s and 'buildV2' not in s

v2 = r"""    /* ── 디자인 v2 그림 — 머리 글자 · 여정 지도 · 도트 · 도넛. 전부 로드 때 한 번 만든다(레이아웃 측정이 필요 없다). 초기 상태가 곧 완성본이다 ── */
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

"""
s = s.replace(marker, v2 + marker, 1)
open(p, 'w', encoding='utf-8').write(s)
print('ok')
