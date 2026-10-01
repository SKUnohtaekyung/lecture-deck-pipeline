/* AI 활용 습관 점검 — 화면과 판정
   문항 · 결과 글은 content.js(window.CHECK_CONTENT)에서 읽는다. 이 파일은 고치지 않는다.
   외부 요청 · 저장 · 전송이 없다. 더블클릭(file://)으로 열어도 동작한다. */
(function () {
  "use strict";

  /* ── 판정 규칙 ──────────────────────────────────────────────
     축마다 답의 평균이 THRESHOLD 이상이면 높은 쪽이다. 문항 수와 상관없이 같은 기준이다.
     check_d1.py가 아래 세 값(THRESHOLD · CHOICES · TYPE_OF)을 이 파일에서 읽어 같은 규칙으로 대조한다. */
  var THRESHOLD = 1.75;
  var CHOICES = [
    { label: "거의 없다", score: 0 },
    { label: "가끔", score: 1 },
    { label: "자주", score: 2 },
    { label: "거의 항상", score: 3 }
  ];
  // "시작 값,마무리 값" → 유형 ID. 유형 이름은 두 축 값을 그대로 이어 붙인다.
  var TYPE_OF = { "high,high": "T1", "low,high": "T2", "high,low": "T3", "low,low": "T4" };

  var TYPE_IDS = ["T1", "T2", "T3", "T4"];
  var AXIS_IDS = ["start", "finish"];
  var NOTE = "내가 쓴 문항으로 만든 자기 점검입니다. 유형은 지금의 습관을 적은 것이고 바뀔 수 있습니다.";
  // 결과 글(요약 · 이번 주 한 가지)이 비어 있는 유형은 이 문구를 보여 준다. 화면이 비거나 오류가 나지 않는다.
  var EMPTY_RESULT = "아직 쓰지 않은 결과입니다. 결과 글을 채우면 이 자리에 나옵니다.";

  function axisResult(questions, answers, axis) {
    var sum = 0;
    var count = 0;
    for (var i = 0; i < questions.length; i++) {
      if (questions[i].axis === axis) {
        sum += answers[i];
        count += 1;
      }
    }
    var avg = count > 0 ? sum / count : 0;
    return { sum: sum, count: count, avg: avg, high: count > 0 && avg >= THRESHOLD };
  }

  function judge(questions, answers) {
    var start = axisResult(questions, answers, "start");
    var finish = axisResult(questions, answers, "finish");
    var key = (start.high ? "high" : "low") + "," + (finish.high ? "high" : "low");
    return { start: start, finish: finish, type: TYPE_OF[key] };
  }

  // 검사 스크립트와 콘솔에서 판정 함수를 직접 부를 수 있게 내보낸다.
  window.CHECK_APP = { judge: judge, THRESHOLD: THRESHOLD, CHOICES: CHOICES, TYPE_OF: TYPE_OF };

  if (typeof document === "undefined") { return; }

  /* ── 작은 도구 ── */
  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) { e.className = cls; }
    if (text !== undefined && text !== null) { e.textContent = text; }
    return e;
  }

  function isText(v) {
    return typeof v === "string" && v.replace(/\s+/g, "") !== "";
  }

  function cleanPrompt(v) {
    return typeof v === "string" ? v.replace(/^\s*>\s?/, "").replace(/^\s+|\s+$/g, "") : "";
  }

  // 유형의 결과 글 데이터. 키가 없으면 빈 글로 본다.
  function typeData(c, id) {
    return (c.types && c.types[id]) || {};
  }

  // 요약이나 이번 주 한 가지 중 하나라도 있으면 결과 글이 있는 유형이다.
  function hasResult(t) {
    return isText(t.summary) || isText(t.step);
  }

  function typeName(c, id) {
    var parts = "";
    Object.keys(TYPE_OF).forEach(function (k) {
      if (TYPE_OF[k] === id) { parts = k; }
    });
    var v = parts.split(",");
    return c.axes.start[v[0]] + " · " + c.axes.finish[v[1]];
  }

  function avgText(n) { return n.toFixed(2); }

  /* ── content.js 점검 ── */
  function validate(c) {
    var p = [];
    if (!c || typeof c !== "object") {
      return ["content.js를 읽지 못했습니다. index.html과 같은 폴더에 content.js가 있는지 확인합니다."];
    }
    AXIS_IDS.forEach(function (id) {
      var a = c.axes && c.axes[id];
      if (!a) { p.push("axes." + id + "가 없습니다."); return; }
      ["name", "high", "low"].forEach(function (k) {
        if (!isText(a[k])) { p.push("axes." + id + "." + k + "가 비어 있습니다."); }
      });
    });
    if (!Array.isArray(c.questions)) {
      p.push("questions가 없습니다.");
    } else {
      var counts = { start: 0, finish: 0 };
      c.questions.forEach(function (q, i) {
        if (!q || AXIS_IDS.indexOf(q.axis) < 0) {
          p.push((i + 1) + "번째 문항의 axis가 start(시작) 또는 finish(마무리)가 아닙니다.");
        } else {
          counts[q.axis] += 1;
        }
        if (!q || !isText(q.text)) { p.push((i + 1) + "번째 문항의 text가 비어 있습니다."); }
      });
      AXIS_IDS.forEach(function (id) {
        if (counts[id] < 1) { p.push(id + " 축의 문항이 없습니다. 축마다 문항이 하나 이상 필요합니다."); }
      });
    }
    // 결과 글은 비어 있어도 된다(쓰지 않은 유형은 화면이 안내 문구를 보여 준다). 형식만 본다.
    if (c.types !== undefined && (typeof c.types !== "object" || c.types === null)) {
      p.push("types가 올바르지 않습니다. T1~T4 키를 가진 객체여야 합니다.");
    }
    return p;
  }

  /* ── 복사 · 내려받기 ── */
  function fallbackCopy(text) {
    var ta = el("textarea", "copy-fallback");
    ta.value = text;
    ta.setAttribute("readonly", "");
    document.body.appendChild(ta);
    ta.select();
    ta.setSelectionRange(0, text.length);
    var ok = false;
    try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
    document.body.removeChild(ta);
    return ok;
  }

  function copyText(text, done) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(
        function () { done(true); },
        function () { done(fallbackCopy(text)); }
      );
    } else {
      done(fallbackCopy(text));
    }
  }

  function pad2(n) { return (n < 10 ? "0" : "") + n; }

  function downloadText(filename, text) {
    var blob = new Blob([text], { type: "text/plain;charset=utf-8" });
    var url = URL.createObjectURL(blob);
    var a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  }

  /* ── 터미널 요청문 카드 ── */
  function terminal(rawPrompt) {
    var text = cleanPrompt(rawPrompt);
    if (!text) { return null; }
    var fig = el("figure", "term");
    var bar = el("div", "term-bar");
    var dots = el("span", "dots");
    dots.setAttribute("aria-hidden", "true");
    dots.appendChild(el("i"));
    dots.appendChild(el("i"));
    dots.appendChild(el("i"));
    bar.appendChild(dots);
    bar.appendChild(el("span", "term-title", "요청문"));
    var status = el("span", "copy-status");
    status.setAttribute("role", "status");
    bar.appendChild(status);
    var btn = el("button", "copy", "복사");
    btn.type = "button";
    bar.appendChild(btn);
    fig.appendChild(bar);

    var body = el("div", "term-body");
    var prompt = el("span", "prompt", ">");
    prompt.setAttribute("aria-hidden", "true");
    var code = el("code", null, text);
    code.appendChild(el("span", "cursor"));
    code.lastChild.setAttribute("aria-hidden", "true");
    body.appendChild(prompt);
    body.appendChild(code);
    fig.appendChild(body);

    var timer = null;
    btn.addEventListener("click", function () {
      copyText(text, function (ok) {
        status.textContent = ok ? "복사했습니다" : "✕ 복사하지 못했습니다. 글을 직접 선택해 복사합니다";
        if (timer) { clearTimeout(timer); }
        timer = setTimeout(function () { status.textContent = ""; }, 3000);
      });
    });
    return fig;
  }

  /* ── 결과 화면 조각 ── */
  function axisRow(axis, r) {
    var row = el("div", "axis-row");
    var head = el("p", "axis-head");
    head.appendChild(el("strong", null, axis.name));
    head.appendChild(document.createTextNode(" · 평균 " + avgText(r.avg) + " · "));
    head.appendChild(el("strong", null, r.high ? axis.high : axis.low));
    row.appendChild(head);

    var meter = el("div", "meter");
    meter.setAttribute("role", "img");
    meter.setAttribute("aria-label",
      axis.name + " 평균 " + avgText(r.avg) + ", 기준 " + THRESHOLD + ", 범위 0에서 3");
    var fill = el("div", "meter-fill");
    fill.style.width = (r.avg / 3 * 100) + "%";
    var mark = el("div", "meter-mark");
    mark.style.left = (THRESHOLD / 3 * 100) + "%";
    meter.appendChild(fill);
    meter.appendChild(mark);
    row.appendChild(meter);

    var poles = el("div", "meter-poles");
    poles.appendChild(el("span", null, "0 · " + axis.low));
    poles.appendChild(el("span", null, axis.high + " · 3"));
    row.appendChild(poles);
    return row;
  }

  function otherBlock(c, id, current) {
    var t = typeData(c, id);
    var box = el("article", "other" + (current ? " current" : ""));
    var h = el("h3", null, typeName(c, id));
    if (current) { h.appendChild(el("span", "tag", "이번 결과")); }
    box.appendChild(h);
    if (!hasResult(t)) {
      box.appendChild(el("p", "empty-result", EMPTY_RESULT));
      return box;
    }
    if (isText(t.summary)) { box.appendChild(el("p", null, t.summary)); }
    if (isText(t.step)) {
      box.appendChild(el("p", "label", "이번 주 해 볼 한 가지"));
      box.appendChild(el("p", null, t.step));
    }
    var term = terminal(t.prompt);
    if (term) { box.appendChild(term); }
    return box;
  }

  function resultText(c, order, answers, r) {
    var t = typeData(c, r.type);
    var d = new Date();
    var L = [];
    L.push(c.title || "AI 활용 습관 점검");
    L.push("점검한 날: " + d.getFullYear() + "-" + pad2(d.getMonth() + 1) + "-" + pad2(d.getDate()));
    L.push("");
    L.push("유형: " + typeName(c, r.type));
    AXIS_IDS.forEach(function (id) {
      L.push(c.axes[id].name + ": 평균 " + avgText(r[id].avg) + " · " + (r[id].high ? c.axes[id].high : c.axes[id].low));
    });
    L.push("");
    if (!hasResult(t)) {
      L.push("결과 글");
      L.push(EMPTY_RESULT);
    } else {
      if (isText(t.summary)) {
        L.push("요약");
        L.push(t.summary);
        L.push("");
      }
      if (isText(t.step)) {
        L.push("이번 주 해 볼 한 가지");
        L.push(t.step);
      }
      var p = cleanPrompt(t.prompt);
      if (p) {
        L.push("");
        L.push("요청문");
        L.push(p);
      }
    }
    L.push("");
    L.push("답한 내용");
    order.forEach(function (qi, pos) {
      L.push((pos + 1) + ". " + c.questions[qi].text + " → " + CHOICES[answers[qi]].label);
    });
    L.push("");
    L.push(NOTE);
    return L.join("\r\n") + "\r\n";
  }

  /* ── 시작 ── */
  function renderProblems(root, problems) {
    root.textContent = "";
    var box = el("section", "problems");
    box.appendChild(el("h2", null, "content.js를 확인합니다"));
    var ul = el("ul");
    problems.forEach(function (m) { ul.appendChild(el("li", null, "✕ " + m)); });
    box.appendChild(ul);
    root.appendChild(box);
  }

  function start() {
    var root = document.getElementById("app");
    var c = window.CHECK_CONTENT;
    var problems = validate(c);
    if (problems.length) { renderProblems(root, problems); return; }

    var heading = document.getElementById("page-title");
    var title = isText(c.title) ? c.title : "AI 활용 습관 점검";
    if (heading) { heading.textContent = title; }
    document.title = title;

    var questions = c.questions;
    var answers = questions.map(function () { return null; });

    // 화면 순서: 시작 축 문항 → 마무리 축 문항(content.js 안의 순서는 유지)
    var order = [];
    AXIS_IDS.forEach(function (id) {
      questions.forEach(function (q, i) { if (q.axis === id) { order.push(i); } });
    });

    var formView = el("div");
    var resultView = el("div");
    resultView.hidden = true;
    root.textContent = "";
    root.appendChild(formView);
    root.appendChild(resultView);

    /* 문항 화면 */
    formView.appendChild(el("p", "lead",
      "AI를 쓰는 내 습관을 문항 " + questions.length + "개로 돌아봅니다. 문항마다 자신에게 가까운 보기를 하나 고르고, 마지막에 「결과 보기」를 누릅니다."));

    var progress = el("div", "progress");
    var progressText = el("p", "progress-text");
    var bar = el("div", "bar");
    var barFill = el("div", "bar-fill");
    bar.appendChild(barFill);
    progress.appendChild(progressText);
    progress.appendChild(bar);
    formView.appendChild(progress);

    var fieldsets = {};
    var missNotes = {};
    var inputs = {};

    function refreshProgress() {
      var done = answers.filter(function (a) { return a !== null; }).length;
      progressText.textContent = "답한 문항 " + done + " / " + questions.length;
      barFill.style.width = (done / questions.length * 100) + "%";
    }

    var pos = 0;
    AXIS_IDS.forEach(function (axisId) {
      var axis = c.axes[axisId];
      var group = el("section", "axis-group");
      group.appendChild(el("h2", null, axis.name));
      if (isText(axis.desc)) { group.appendChild(el("p", "axis-desc", axis.desc)); }
      order.forEach(function (qi) {
        if (questions[qi].axis !== axisId) { return; }
        pos += 1;
        var fs = el("fieldset", "q");
        var lg = el("legend");
        lg.appendChild(el("span", "qn", String(pos)));
        lg.appendChild(document.createTextNode(questions[qi].text));
        fs.appendChild(lg);
        var opts = el("div", "opts");
        inputs[qi] = [];
        CHOICES.forEach(function (ch) {
          var label = el("label", "opt");
          var input = document.createElement("input");
          input.type = "radio";
          input.name = "q" + qi;
          input.value = String(ch.score);
          input.addEventListener("change", function () {
            answers[qi] = ch.score;
            fs.classList.remove("missing");
            missNotes[qi].hidden = true;
            refreshProgress();
          });
          label.appendChild(input);
          label.appendChild(el("span", null, ch.label));
          opts.appendChild(label);
          inputs[qi].push(input);
        });
        fs.appendChild(opts);
        var note = el("p", "miss-note", "✕ 답해 주세요");
        note.hidden = true;
        fs.appendChild(note);
        fieldsets[qi] = fs;
        missNotes[qi] = note;
        group.appendChild(fs);
      });
      formView.appendChild(group);
    });

    var actions = el("div", "actions");
    var alertBox = el("p", "alert");
    alertBox.setAttribute("role", "alert");
    var submit = el("button", "btn", "결과 보기");
    submit.type = "button";
    actions.appendChild(alertBox);
    actions.appendChild(submit);
    formView.appendChild(actions);
    refreshProgress();

    submit.addEventListener("click", function () {
      var missing = [];
      order.forEach(function (qi) { if (answers[qi] === null) { missing.push(qi); } });
      order.forEach(function (qi) {
        var isMissing = answers[qi] === null;
        fieldsets[qi].classList.toggle("missing", isMissing);
        missNotes[qi].hidden = !isMissing;
      });
      if (missing.length) {
        alertBox.textContent = "✕ 아직 답하지 않은 문항이 " + missing.length + "개 있습니다. "
          + (order.indexOf(missing[0]) + 1) + "번 문항부터 답합니다.";
        inputs[missing[0]][0].focus();
        return;
      }
      alertBox.textContent = "";
      showResult();
    });

    /* 결과 화면 */
    function showResult() {
      var r = judge(questions, answers);
      var t = typeData(c, r.type);
      resultView.textContent = "";

      resultView.appendChild(el("p", "eyebrow", "점검 결과"));
      var h = el("h2", "type-title", typeName(c, r.type));
      h.tabIndex = -1;
      resultView.appendChild(h);

      var axisCard = el("section", "card");
      AXIS_IDS.forEach(function (id) { axisCard.appendChild(axisRow(c.axes[id], r[id])); });
      axisCard.appendChild(el("p", "rule-note",
        "축마다 답의 평균이 " + THRESHOLD + " 이상이면 높은 쪽으로 봅니다."));
      resultView.appendChild(axisCard);

      if (!hasResult(t)) {
        var empty = el("section", "card empty");
        empty.appendChild(el("p", "empty-result", EMPTY_RESULT));
        resultView.appendChild(empty);
      } else {
        if (isText(t.summary)) {
          var sum = el("section", "card");
          sum.appendChild(el("h3", null, "요약"));
          sum.appendChild(el("p", null, t.summary));
          resultView.appendChild(sum);
        }
        var term = terminal(t.prompt);
        if (isText(t.step) || term) {
          var step = el("section", "card");
          if (isText(t.step)) {
            step.appendChild(el("h3", null, "이번 주 해 볼 한 가지"));
            step.appendChild(el("p", null, t.step));
          }
          if (term) { step.appendChild(term); }
          resultView.appendChild(step);
        }
      }

      var row = el("div", "row result-actions");
      var dl = el("button", "btn", "결과 내려받기");
      dl.type = "button";
      dl.addEventListener("click", function () {
        downloadText("AI습관점검_결과.txt", resultText(c, order, answers, r));
      });
      var more = el("button", "btn ghost", "다른 유형 결과 보기");
      more.type = "button";
      more.setAttribute("aria-expanded", "false");
      more.setAttribute("aria-controls", "others");
      var again = el("button", "btn ghost", "다시 하기");
      again.type = "button";
      row.appendChild(dl);
      row.appendChild(more);
      row.appendChild(again);
      resultView.appendChild(row);

      var others = el("section", "others");
      others.id = "others";
      others.hidden = true;
      TYPE_IDS.forEach(function (id) { others.appendChild(otherBlock(c, id, id === r.type)); });
      resultView.appendChild(others);

      more.addEventListener("click", function () {
        var open = others.hidden;
        others.hidden = !open;
        more.setAttribute("aria-expanded", open ? "true" : "false");
        more.textContent = open ? "다른 유형 결과 닫기" : "다른 유형 결과 보기";
      });

      again.addEventListener("click", function () {
        answers = questions.map(function () { return null; });
        order.forEach(function (qi) {
          inputs[qi].forEach(function (input) { input.checked = false; });
          fieldsets[qi].classList.remove("missing");
          missNotes[qi].hidden = true;
        });
        alertBox.textContent = "";
        refreshProgress();
        resultView.hidden = true;
        formView.hidden = false;
        window.scrollTo(0, 0);
        if (heading) { heading.tabIndex = -1; heading.focus(); }
      });

      resultView.appendChild(el("p", "note", NOTE));

      formView.hidden = true;
      resultView.hidden = false;
      window.scrollTo(0, 0);
      h.focus();
    }
  }

  start();
})();
