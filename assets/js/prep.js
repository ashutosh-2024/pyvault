(function () {
  "use strict";

  var esc = window.esc;
  var hl = window.highlight;
  var data = window.GRAIL_PREP || { patterns: [], complexity: [], sizes: [] };
  var topics = window.GRAIL_DSA || [];
  var root = document.getElementById("prep");

  var byId = {};
  topics.forEach(function (t) {
    t.problems.forEach(function (p) { byId[p.id] = p; });
  });

  var TABS = [["patterns", "Patterns"], ["complexity", "Complexity"], ["mock", "Mock interview"]];

  function table(head, rows) {
    return '<div class="dd-table-wrap"><table class="dd-table"><thead><tr>' +
      head.map(function (h) { return "<th>" + h + "</th>"; }).join("") +
      "</tr></thead><tbody>" +
      rows.map(function (r) {
        return "<tr>" + r.map(function (c) { return "<td>" + c + "</td>"; }).join("") + "</tr>";
      }).join("") + "</tbody></table></div>";
  }

  /* ---------- patterns ---------- */
  function patterns() {
    var toc = '<nav class="dd-toc" aria-label="Patterns"><p class="code-label">' +
      data.patterns.length + " patterns</p><ol>" +
      data.patterns.map(function (p) {
        return '<li><a href="#p-' + p.id + '">' + p.name + "</a></li>";
      }).join("") + "</ol></nav>";

    return '<p class="try-hint">Each pattern: the signals that give it away, the core idea, and a template ' +
      "that the build executes against a check. The examples link to worked problems.</p>" + toc +
      data.patterns.map(function (p) {
        return '<section class="dd-section pattern-card-full" id="p-' + p.id + '">' +
          "<h2>" + p.name + "</h2>" +
          "<p>" + p.idea + "</p>" +
          '<p class="code-label">Reach for it when</p>' +
          '<ul class="signals">' + p.signals.map(function (s) { return "<li>" + s + "</li>"; }).join("") + "</ul>" +
          '<p class="code-label">Template</p>' +
          '<pre class="code"><code>' + hl(p.template) + "</code></pre>" +
          '<p class="code-label">Practise it on</p>' +
          '<div class="tags example-links">' + p.examples.map(function (id) {
            var q = byId[id];
            var done = window.progress.isSolved(id);
            return '<a class="tag' + (done ? " done" : "") + '" href="problem.html?id=' + encodeURIComponent(id) + '">' +
              (done ? "&#10003; " : "") + esc(q ? q.name : id) + "</a>";
          }).join("") + "</div>" +
        "</section>";
      }).join("");
  }

  /* ---------- complexity ---------- */
  function complexity() {
    return '<p class="try-hint">What Python operations actually cost (CPython), and what input size a ' +
      "complexity can afford. The second table is the fastest way to guess the intended solution " +
      "from the constraints.</p>" +
      '<section class="dd-section"><h2>Input size &rarr; target complexity</h2>' +
      table(["Constraint", "Aim for", "Typical techniques"], data.sizes) + "</section>" +
      data.complexity.map(function (c) {
        return '<section class="dd-section"><h2>' + esc(c.title) + "</h2>" +
          (c.note ? "<p>" + c.note + "</p>" : "") +
          table(["Operation", "Cost", "Note"], c.rows) + "</section>";
      }).join("");
  }

  /* ---------- mock interview ---------- */
  var chosenTopics = {}, chosenDiffs = { medium: true, hard: true };

  function mock() {
    var active = window.progress.mock();
    var activeCard = "";
    if (active && byId[active.id]) {
      var left = Math.round((active.start + active.minutes * 60000 - Date.now()) / 60000);
      activeCard = '<div class="takeaway"><strong>Interview in progress.</strong> ' +
        esc(byId[active.id].name) + " &middot; " + (left >= 0 ? left + " min left" : Math.abs(left) + " min over") +
        '<div class="cta-row"><a class="btn btn-primary btn-sm" href="problem.html?id=' +
        encodeURIComponent(active.id) + '&amp;mock=1">Resume</a>' +
        '<button type="button" class="btn btn-sm" id="abandon">Abandon</button></div></div>';
    }
    return activeCard +
      '<p class="try-hint">Pick the topics and difficulty, and a random problem opens with a countdown. ' +
      "Solutions stay hidden; running your code and passing the tests ends the interview and records your time.</p>" +
      '<div class="mock-form">' +
        '<p class="code-label">Topics</p><div class="chips" id="topic-chips">' +
          topics.filter(function (t) { return t.count; }).map(function (t) {
            return '<button type="button" class="chip" data-topic="' + t.id + '" aria-pressed="' +
              !!chosenTopics[t.id] + '">' + esc(t.title) + "</button>";
          }).join("") + "</div>" +
        '<p class="code-label">Difficulty</p><div class="chips" id="diff-chips">' +
          ["easy", "medium", "hard"].map(function (d) {
            return '<button type="button" class="chip" data-diff="' + d + '" aria-pressed="' +
              !!chosenDiffs[d] + '">' + d + "</button>";
          }).join("") + "</div>" +
        '<p class="code-label">Time limit</p><div class="chips" id="time-chips">' +
          [20, 30, 45, 60].map(function (m) {
            return '<button type="button" class="chip" data-min="' + m + '" aria-pressed="' + (m === 45) + '">' + m + " min</button>";
          }).join("") + "</div>" +
        '<label class="always-show"><input type="checkbox" id="unsolved" checked> Only problems I have not solved</label>' +
        '<div class="cta-row"><button type="button" class="btn btn-primary" id="start">Start interview</button>' +
        '<span class="run-status" id="pool"></span></div>' +
      "</div>";
  }

  function pool() {
    var none = !Object.keys(chosenTopics).some(function (k) { return chosenTopics[k]; });
    var onlyNew = document.getElementById("unsolved").checked;
    var out = [];
    topics.forEach(function (t) {
      if (!none && !chosenTopics[t.id]) return;
      t.problems.forEach(function (p) {
        if (chosenDiffs[p.difficulty] && !(onlyNew && window.progress.isSolved(p.id))) out.push(p);
      });
    });
    return out;
  }

  function wireMock() {
    var minutes = 45;
    function update() {
      var n = pool().length;
      document.getElementById("pool").textContent = n + " problem" + (n === 1 ? "" : "s") + " match" +
        (Object.keys(chosenTopics).some(function (k) { return chosenTopics[k]; }) ? "" : " (all topics)");
      document.getElementById("start").disabled = !n;
    }
    Array.prototype.forEach.call(document.querySelectorAll("#topic-chips .chip"), function (b) {
      b.onclick = function () {
        chosenTopics[b.dataset.topic] = !chosenTopics[b.dataset.topic];
        b.setAttribute("aria-pressed", chosenTopics[b.dataset.topic]);
        update();
      };
    });
    Array.prototype.forEach.call(document.querySelectorAll("#diff-chips .chip"), function (b) {
      b.onclick = function () {
        chosenDiffs[b.dataset.diff] = !chosenDiffs[b.dataset.diff];
        b.setAttribute("aria-pressed", chosenDiffs[b.dataset.diff]);
        update();
      };
    });
    Array.prototype.forEach.call(document.querySelectorAll("#time-chips .chip"), function (b) {
      b.onclick = function () {
        minutes = +b.dataset.min;
        Array.prototype.forEach.call(document.querySelectorAll("#time-chips .chip"), function (o) {
          o.setAttribute("aria-pressed", o === b);
        });
      };
    });
    document.getElementById("unsolved").onchange = update;
    document.getElementById("start").onclick = function () {
      var choices = pool();
      if (!choices.length) return;
      var p = choices[Math.floor(Math.random() * choices.length)];
      window.progress.setMock({ id: p.id, start: Date.now(), minutes: minutes });
      location.href = "problem.html?id=" + encodeURIComponent(p.id) + "&mock=1";
    };
    var abandon = document.getElementById("abandon");
    if (abandon) abandon.onclick = function () { window.progress.setMock(null); render(); };
    update();
  }

  /* ---------- tabs ---------- */
  function render() {
    var tab = (location.hash || "#patterns").slice(1);
    if (!TABS.some(function (t) { return t[0] === tab; })) tab = "patterns";
    document.title = TABS.filter(function (t) { return t[0] === tab; })[0][1] + " — Interview Prep — pyvault";
    root.innerHTML =
      '<div class="tabbar">' + TABS.map(function (t) {
        return '<a href="#' + t[0] + '" class="tab' + (t[0] === tab ? " active" : "") + '">' + t[1] + "</a>";
      }).join("") + "</div>" +
      (tab === "patterns" ? patterns() : tab === "complexity" ? complexity() : mock());
    if (tab === "mock") wireMock();
    if (/^#p-/.test(location.hash)) {
      var target = document.getElementById(location.hash.slice(1));
      if (target) target.scrollIntoView();
    }
  }

  window.addEventListener("hashchange", function () {
    if (/^#(patterns|complexity|mock)$/.test(location.hash) || !location.hash) render();
  });
  render();
})();
