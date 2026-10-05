(function () {
  "use strict";

  var esc = window.esc;
  var hl = window.highlight;

  var LC_MARK =
    '<img class="lc-mark" src="assets/img/leetcode.png" alt="" aria-hidden="true">';

  function lcLink(p) {
    if (!p.url) return "";
    return '<a class="lc-link" href="' + p.url + '" target="_blank" rel="noopener">' +
      LC_MARK + "<span>Solve " + p.lc + " on LeetCode</span>" +
      '<span aria-hidden="true">&#8599;</span></a>';
  }

  function refLink(p) {
    if (!p.ref) return "";
    return '<a class="ref-link" href="' + p.ref.url + '" target="_blank" rel="noopener">' +
      "<span>" + esc(p.ref.label) + "</span>" +
      '<span aria-hidden="true">&#8599;</span></a>';
  }

  /* ---------- locate the problem ---------- */
  var flat = [];
  (window.GRAIL_DSA || []).forEach(function (t) {
    (t.problems || []).forEach(function (p) { flat.push(p); });
  });

  var id = new URLSearchParams(location.search).get("id");
  var idx = flat.findIndex(function (p) { return p.id === id; });
  var root = document.getElementById("problem");

  if (idx === -1) {
    root.innerHTML =
      '<div class="prob-head"><h1>Problem not found</h1></div>' +
      '<div class="entry-body"><p><a href="dsa.html">&larr; Back to DSA</a></p></div>';
    return;
  }

  var p = flat[idx];
  var topicObj = (window.GRAIL_DSA || []).filter(function (t) {
    return t.id === p.topic;
  })[0] || {};
  var patternCrumb = topicObj.layout === "patterns"
    ? ' / <a href="dsa.html?topic=' + encodeURIComponent(p.topic) + "&amp;pattern=" +
        encodeURIComponent(p.section) + '">' + esc(p.sectionTitle) + "</a>"
    : "";
  document.title = (p.lc ? p.lc + ". " : "") + p.name + " — pyvault";

  var html = "";

  /* ---------- head ---------- */
  html +=
    '<div class="prob-head">' +
      '<p class="crumb"><a href="dsa.html">DSA</a> / ' +
        '<a href="dsa.html?topic=' + encodeURIComponent(p.topic) + '">' +
          esc(p.topicTitle) + "</a>" + patternCrumb + "</p>" +
      '<div class="meta">' +
        (p.lc ? '<span class="crumb">LeetCode ' + p.lc + "</span>" : "") +
        '<span class="badge ' + p.difficulty + '">' + p.difficulty + "</span>" +
        (p.premium ? '<span class="badge premium">premium</span>' : "") +
      "</div>" +
      "<h1>" + esc(p.name) + "</h1>" +
      (p.tags.length
        ? '<div class="tags">' + p.tags.map(function (t) {
            return '<span class="tag">' + esc(t) + "</span>";
          }).join("") + "</div>"
        : "") +
      '<div class="actions">' + lcLink(p) + refLink(p) +
        '<button type="button" class="track-btn" id="btn-solved"></button>' +
        '<button type="button" class="track-btn" id="btn-star"></button>' +
      "</div>" +
    "</div>";

  html += '<div class="entry-body">';

  /* ---------- problem statement ---------- */
  html += "<h2>Problem</h2>";
  html += '<div class="statement">' +
    p.statement.map(function (t) { return "<p>" + t + "</p>"; }).join("") + "</div>";

  if (p.note) {
    html += '<div class="dsa-callout"><p>' + p.note + "</p></div>";
  }

  /* ---------- examples ---------- */
  if (p.examples.length) {
    html += "<h2>Examples</h2>";
    html += p.examples.map(function (ex, i) {
      var rows = "";
      if (ex.input) {
        rows += '<div class="io"><b>Input</b><code>' + esc(ex.input) + "</code></div>";
      }
      if (ex.output) {
        rows += '<div class="io"><b>Output</b><code>' + esc(ex.output) + "</code></div>";
      }
      if (ex.explanation) {
        rows += '<div class="io"><b>Why</b><span>' + esc(ex.explanation) + "</span></div>";
      }
      return '<div class="example"><span class="ex-n">Example ' + (i + 1) + "</span>" +
             rows + "</div>";
    }).join("");
  }

  /* ---------- constraints ---------- */
  if (p.constraints.length) {
    html += "<h2>Constraints</h2><ul class=\"constraints\">" +
      p.constraints.map(function (c) { return "<li>" + c + "</li>"; }).join("") +
      "</ul>";
  }

  if (p.pitfall) {
    html += '<div class="pitfall"><strong>Common mistake.</strong> ' + p.pitfall + "</div>";
  }

  /* ---------- step-by-step animation (content/viz/) ---------- */
  if (p.viz) {
    var nCh = p.viz.chapters.length;
    html += '<details class="reveal viz-reveal" id="viz-reveal">' +
      "<summary>" + (p.viz.traced
        ? "Watch " + (nCh === 1 ? "the approach" : "every approach") + " run &mdash; " + nCh + " approach" + (nCh === 1 ? "" : "es") + ", "
        : "Watch the algorithm run &mdash; " + nCh + " chapter" + (nCh === 1 ? "" : "s") + ", ") +
        p.viz.frames + " steps <span class=\"viz-spoiler\">(shows the solution)</span></summary>" +
      '<div class="reveal-inner"><div id="viz"><p class="viz-loading">Loading animation&hellip;</p></div></div>' +
    "</details>";
  }

  /* ---------- try it: write and run your own solution ---------- */
  var mockParam = new URLSearchParams(location.search).get("mock") === "1";
  var mock = window.progress.mock();
  var inMock = mockParam && mock && mock.id === p.id;
  html += "<h2>Try it</h2>" +
    '<p class="try-hint">Write a solution below and run it against the same tests the build ran. ' +
      "Python runs in your browser; nothing is sent anywhere.</p>" +
    '<div class="editor">' +
      '<textarea id="code" spellcheck="false" autocapitalize="off" autocomplete="off"></textarea>' +
      '<div class="editor-bar">' +
        '<button type="button" class="btn btn-primary btn-sm" id="run">Run tests</button>' +
        '<button type="button" class="btn btn-sm" id="reset">Reset</button>' +
        '<span class="run-status" id="status"></span>' +
      "</div>" +
      '<pre class="code output run-output" id="result" hidden><code></code></pre>' +
    "</div>";

  var alwaysShow = window.progress.pref("showSolutions", false) && !inMock;
  html += '<details class="reveal solutions-reveal" id="solutions"' + (alwaysShow ? " open" : "") + ">" +
    "<summary>" + (inMock ? "Solutions are hidden during a mock interview"
                          : "Show solutions (" + p.approaches.length + " approach" +
                            (p.approaches.length === 1 ? "" : "es") + ")") + "</summary>" +
    '<div class="reveal-inner">' +
    '<label class="always-show"><input type="checkbox" id="always-show"' +
      (alwaysShow ? " checked" : "") + "> Always show solutions</label>";

  /* ---------- complexity summary ---------- */
  html += "<h2>At a glance</h2>" +
    '<table class="cx-table"><thead><tr>' +
      "<th>Approach</th><th>Time</th><th>Auxiliary space</th>" +
    "</tr></thead><tbody>" +
    p.approaches.map(function (a) {
      return '<tr class="' + (a.best ? "is-best" : "") + '">' +
        "<td>" + esc(a.name) + "</td>" +
        '<td class="cx">' + a.time + "</td>" +
        '<td class="cx">' + a.space + "</td>" +
      "</tr>";
    }).join("") +
    "</tbody></table>";

  /* ---------- each approach ---------- */
  // A DP problem carries a recurrence and is written as a ladder: plain
  // recursion first, then the recurrence it encodes, then each step that
  // makes it faster or smaller. Its explanations are short points.
  var ladder = !!p.recurrence;

  function points(list) {
    return ladder
      ? "<ul>" + list.map(function (t) { return "<li>" + t + "</li>"; }).join("") + "</ul>"
      : list.map(function (t) { return "<p>" + t + "</p>"; }).join("");
  }

  function recurrenceBlock(r) {
    return '<div class="recurrence">' +
      "<h3>The recurrence</h3>" +
      '<p class="rec-label">State</p>' +
      '<p class="rec-state">' + r.state + "</p>" +
      ((r.derive || []).length
        ? '<p class="rec-label">How to derive it</p><ul>' +
            r.derive.map(function (t) { return "<li>" + t + "</li>"; }).join("") + "</ul>"
        : "") +
      '<p class="rec-label">Recurrence relation</p>' +
      '<pre class="code rec-formula"><code>' + esc(r.formula) + "</code></pre>" +
      ((r.notes || []).length
        ? "<ul>" + r.notes.map(function (t) { return "<li>" + t + "</li>"; }).join("") + "</ul>"
        : "") +
    "</div>";
  }

  /* a detailed write-up (content/explain/): idea and steps before the code,
     why it works and a dry run on the problem's shared example after it */
  function bullets(title, list, cls) {
    return '<div class="ex-part' + (cls ? " " + cls : "") + '"><h4>' + title + "</h4><ul>" +
      list.map(function (x) { return "<li>" + x + "</li>"; }).join("") + "</ul></div>";
  }
  function explainTop(e) {
    return '<div class="explain">' + bullets("The idea", e.idea) + bullets("Step by step", e.steps) + "</div>";
  }
  function explainBottom(e) {
    var ex = p.example;
    var call = ex ? (ex.setup ? ex.setup + "\n" : "") + ex.call : "";
    return '<div class="explain">' + bullets("Why it works", e.why) +
      '<div class="ex-part ex-dry"><h4>Dry run</h4>' +
        (ex ? '<pre class="code ex-call"><code>' + hl(call) + "</code></pre>" : "") +
        "<ol>" + e.dry.map(function (x) { return "<li>" + x + "</li>"; }).join("") + "</ol>" +
        (ex ? '<p class="ex-result">Returns <code>' + esc(ex.expect) + "</code> &mdash; checked by the build.</p>" : "") +
      "</div></div>";
  }

  html += "<h2>" + (ladder ? "From recursion to optimal" : "Solutions") + "</h2>";
  html += p.approaches.map(function (a, i) {
    var card = '<div class="approach' + (a.best ? " is-best" : "") + '">' +
      '<div class="approach-head">' +
        (ladder ? '<span class="step-no">Step ' + (i + 1) + "</span>" : "") +
        "<h3>" + esc(a.name) + "</h3>" +
        (a.best ? '<span class="pill star">pick this</span>' : "") +
        (a.tag ? '<span class="pill">' + esc(a.tag) + "</span>" : "") +
      "</div>" +
      (a.change
        ? '<div class="step-change"><b>What changed</b><span>' + a.change + "</span></div>"
        : "") +
      '<div class="cx-inline">' +
        "<div><b>time</b><span>" + a.time + "</span></div>" +
        "<div><b>aux space</b><span>" + a.space + "</span></div>" +
      "</div>" +
      (a.explain ? explainTop(a.explain) : "") +
      '<pre class="code"><code>' + hl(a.code) + "</code></pre>" +
      (a.explain ? explainBottom(a.explain) : '<div class="why">' + points(a.why) + "</div>") +
    "</div>";
    return card + (ladder && i === 0 ? recurrenceBlock(p.recurrence) : "");
  }).join("");

  /* ---------- the assertions the build ran ---------- */
  html +=
    '<details class="reveal" style="margin-top:22px">' +
      "<summary>What the build checked</summary>" +
      '<div class="reveal-inner">' +
        '<pre class="code"><code>' + hl(p.tests) + "</code></pre>" +
        (p.smallTests
          ? "<p>Plain recursion is exponential, so it is checked against this smaller set:</p>" +
            '<pre class="code"><code>' + hl(p.smallTests) + "</code></pre>"
          : "") +
      "</div>" +
    "</details>";

  html += "</div></details>";                  /* end of the hidden solutions */

  /* ---------- prev / next, within this topic only ---------- */
  var inTopic = flat.filter(function (q) { return q.topic === p.topic; });
  var tIdx = inTopic.indexOf(p);
  var prev = inTopic[tIdx - 1], next = inTopic[tIdx + 1];
  function navLink(q, dir) {
    return '<a href="problem.html?id=' + encodeURIComponent(q.id) + '">' +
      '<span class="code-label">' + (dir < 0 ? "&larr; Previous" : "Next &rarr;") + "</span><br>" +
      esc(q.name) + "</a>";
  }
  html += '<div class="entry-nav">' +
    (prev ? navLink(prev, -1) : "<span></span>") +
    (next ? navLink(next, 1) : "<span></span>") +
    "</div>" +
    '<p class="code-label" style="text-align:center;margin-top:12px">' +
      (tIdx + 1) + " of " + inTopic.length + " in " + esc(topicObj.title || "this topic") + "</p>";

  html += "</div>";
  if (inMock) {
    html = '<div class="mock-bar" id="mock-bar"><span>Mock interview</span>' +
      '<b id="mock-clock">--:--</b>' +
      '<button type="button" class="btn btn-sm" id="mock-end">End</button></div>' + html;
  }
  root.innerHTML = html;
  /* animations live in their own file and load the first time the section is opened */
  if (p.viz && window.renderViz) {
    var vizReveal = document.getElementById("viz-reveal"), vizLoaded = false;
    vizReveal.addEventListener("toggle", function () {
      if (!vizReveal.open || vizLoaded) return;
      vizLoaded = true;
      fetch(p.viz.src).then(function (r) {
        if (!r.ok) throw new Error(r.status);
        return r.json();
      }).then(function (data) {
        window.renderViz(document.getElementById("viz"), data);
      }).catch(function () {
        vizLoaded = false;
        document.getElementById("viz").innerHTML =
          '<p class="viz-loading">Could not load the animation. Serve the site over HTTP (e.g. <code>python3 -m http.server</code>) and try again.</p>';
      });
    });
  }

  /* ---------- solved / starred ---------- */
  var solvedBtn = document.getElementById("btn-solved");
  var starBtn = document.getElementById("btn-star");
  function paintTrack() {
    var solved = window.progress.isSolved(p.id), starred = window.progress.isStarred(p.id);
    solvedBtn.textContent = solved ? "\u2713 Solved" : "Mark solved";
    solvedBtn.setAttribute("aria-pressed", solved);
    starBtn.textContent = starred ? "\u2605 Starred" : "\u2606 Star";
    starBtn.setAttribute("aria-pressed", starred);
  }
  solvedBtn.onclick = function () { window.progress.toggleSolved(p.id); paintTrack(); };
  starBtn.onclick = function () { window.progress.toggleStarred(p.id); paintTrack(); };
  paintTrack();

  /* ---------- editor ---------- */
  var area = document.getElementById("code");
  var statusEl = document.getElementById("status");
  var resultEl = document.getElementById("result");
  area.value = window.progress.draft(p.id) || p.starter;
  function fit() {
    area.style.height = "auto";
    area.style.height = Math.max(220, area.scrollHeight + 4) + "px";
  }
  fit();
  area.addEventListener("input", function () { window.progress.saveDraft(p.id, area.value); fit(); });
  area.addEventListener("keydown", function (e) {
    if (e.key === "Tab" && !e.shiftKey) {                /* indent, do not leave the box */
      e.preventDefault();
      var a = area.selectionStart, b = area.selectionEnd;
      area.value = area.value.slice(0, a) + "    " + area.value.slice(b);
      area.selectionStart = area.selectionEnd = a + 4;
      window.progress.saveDraft(p.id, area.value);
    } else if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      runTests();
    }
  });
  document.getElementById("reset").onclick = function () {
    if (area.value !== p.starter && !confirm("Discard your code and start from the template?")) return;
    area.value = p.starter;
    window.progress.clearDraft(p.id);
    resultEl.hidden = true;
    statusEl.textContent = "";
    fit();
  };

  var runBtn = document.getElementById("run");
  function runTests() {
    if (runBtn.disabled) return;
    runBtn.disabled = true;
    resultEl.hidden = true;
    statusEl.className = "run-status";
    var prelude = (window.GRAIL_PRELUDE || "") + "\n\n" + (topicObj.prelude || "");
    window.pyRunner.run({ prelude: prelude, code: area.value, tests: p.tests },
                        function (msg) { statusEl.textContent = msg; })
      .then(function (r) {
        resultEl.hidden = false;
        resultEl.className = "code output run-output" + (r.ok ? "" : " error");
        var out = r.output ? r.output.replace(/\s+$/, "") : "";
        if (r.ok) {
          statusEl.textContent = "All tests passed";
          statusEl.className = "run-status pass";
          resultEl.firstChild.textContent = (out ? out + "\n\n" : "") +
            "\u2713 Every assertion the build checks passed.";
          window.progress.setSolved(p.id, true);
          paintTrack();
          if (inMock) finishMock(true);
        } else {
          statusEl.textContent = r.stage === "tests" ? "A test failed" :
            r.stage === "timeout" ? "Timed out" : "Error in " + r.stage;
          statusEl.className = "run-status fail";
          var hint = "";
          if (r.where && r.where.file === "tests.py") {
            var line = p.tests.split("\n")[r.where.line - 1] || "";
            hint = "\n\nFailing check (tests.py line " + r.where.line + "):\n  " + line.trim();
          }
          resultEl.firstChild.textContent = out + hint;
        }
      }, function (err) {
        statusEl.textContent = String(err.message || err);
        statusEl.className = "run-status fail";
      })
      .then(function () { runBtn.disabled = false; });
  }
  runBtn.onclick = runTests;

  /* ---------- hidden solutions ---------- */
  var sol = document.getElementById("solutions");
  var always = document.getElementById("always-show");
  always.onchange = function () { window.progress.setPref("showSolutions", always.checked); };
  if (inMock) {
    sol.addEventListener("toggle", function () {
      if (sol.open && !confirm("Reveal the solutions? This ends the mock interview.")) {
        sol.open = false;
      } else if (sol.open) {
        finishMock(false);
      }
    });
  }

  /* ---------- mock interview clock ---------- */
  var clockTimer = null;
  function finishMock(passed) {
    var m = window.progress.mock();
    if (!m) return;
    var used = Math.round((Date.now() - m.start) / 1000);
    window.progress.setMock(null);
    clearInterval(clockTimer);
    var bar = document.getElementById("mock-bar");
    if (bar) {
      bar.innerHTML = "<span>" + (passed ? "Solved in " : "Ended after ") +
        Math.floor(used / 60) + " min " + (used % 60) + " s</span>" +
        '<a class="btn btn-sm" href="prep.html#mock">New interview</a>';
      bar.classList.add(passed ? "done" : "ended");
    }
  }
  if (inMock) {
    var clock = document.getElementById("mock-clock");
    var tick = function () {
      var left = Math.round((mock.start + mock.minutes * 60000 - Date.now()) / 1000);
      var neg = left < 0, a = Math.abs(left);
      clock.textContent = (neg ? "-" : "") + String(Math.floor(a / 60)).padStart(2, "0") + ":" +
        String(a % 60).padStart(2, "0");
      clock.className = neg ? "over" : left < 300 ? "low" : "";
    };
    tick();
    clockTimer = setInterval(tick, 1000);
    document.getElementById("mock-end").onclick = function () {
      if (confirm("End this mock interview?")) finishMock(false);
    };
  }
})();
