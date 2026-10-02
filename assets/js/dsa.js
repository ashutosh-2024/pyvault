(function () {
  "use strict";

  var esc = window.esc;
  var topics = window.GRAIL_DSA || [];
  var root = document.getElementById("dsa");
  var wanted = new URLSearchParams(location.search).get("topic");

  function plural(n, word) {
    return n + " " + word + (n === 1 ? "" : "s");
  }

  var progress = window.progress;

  function ids(problems) {
    return problems.map(function (p) { return p.id; });
  }

  /* "7 / 21 solved" with a bar; empty string when nothing is tracked */
  function progressBar(problems) {
    var done = progress.countSolved(ids(problems)), n = problems.length;
    return '<span class="prog" title="' + done + " of " + n + ' solved">' +
      '<span class="prog-bar"><span style="width:' + (n ? (100 * done / n).toFixed(1) : 0) + '%"></span></span>' +
      '<span class="prog-n">' + done + " / " + n + "</span></span>";
  }

  /* ---------- topic index ---------- */
  function topicIndex() {
    document.title = "DSA — pyvault";

    var all = [];
    topics.forEach(function (t) { all = all.concat(t.problems); });
    var solvedAll = progress.countSolved(ids(all));
    root.innerHTML =
      '<p class="topic-sub overall">' + solvedAll + " of " + all.length +
        " problems solved &middot; progress is saved in this browser" +
        (solvedAll ? "" : ' &middot; open a problem and run your code, or mark it solved') + "</p>" +
      '<div class="entry-list">' + topics.map(function (t, i) {
      var ready = t.count > 0;
      var right = ready
        ? progressBar(t.problems)
        : '<span class="badge planned">' +
            (t.target ? t.target + " planned" : "planned") + "</span>";

      return '<a class="entry-card" href="dsa.html?topic=' +
        encodeURIComponent(t.id) + '">' +
        '<span class="num">' + String(i + 1).padStart(2, "0") + "</span>" +
        '<span class="body">' +
          '<span class="title">' + esc(t.title) + "</span>" +
        "</span>" +
        right +
      "</a>";
    }).join("") + "</div>";
  }

  function problemRows(problems) {
    return '<div class="entry-list">' + problems.map(function (p) {
      var solved = progress.isSolved(p.id), starred = progress.isStarred(p.id);
      return '<a class="entry-card' + (solved ? " is-solved" : "") + '" href="problem.html?id=' +
        encodeURIComponent(p.id) + '">' +
        '<span class="num">' + (p.lc || (p.ref ? "GFG" : "—")) + "</span>" +
        '<span class="body">' +
          '<span class="title">' + (solved ? '<span class="tick" title="solved">&#10003;</span> ' : "") +
            esc(p.name) + (starred ? ' <span class="star-mark" title="starred">&#9733;</span>' : "") +
          "</span>" +
          '<span class="tags">' +
            p.tags.slice(0, 4).map(function (tag) {
              return '<span class="tag">' + esc(tag) + "</span>";
            }).join("") +
          "</span>" +
        "</span>" +
        '<span class="badge ' + p.difficulty + '">' + p.difficulty + "</span>" +
      "</a>";
    }).join("") + "</div>";
  }

  function topicLink(t) {
    return '<a href="dsa.html?topic=' + encodeURIComponent(t.id) + '">' +
      esc(t.title) + "</a>";
  }

  /* ---------- one topic: straight to the problems ---------- */
  function topicPage(t) {
    document.title = t.title + " — DSA — pyvault";

    var head =
      '<p class="crumb-line"><a href="dsa.html">DSA</a> / ' + esc(t.title) + "</p>" +
      '<h2 class="topic-title">' + esc(t.title) + "</h2>";

    if (!t.problems.length) {
      root.innerHTML = head +
        '<div class="stub-note"><p>Not written up yet.</p>' +
        '<p><a href="dsa.html">&larr; Back to topics</a></p></div>';
      return;
    }

    if (t.layout === "patterns") {
      root.innerHTML = head +
        '<p class="topic-sub">' + plural(t.sections.length, "pattern") +
          " &middot; " + plural(t.count, "problem") +
          " &middot; work through them in order</p>" +
        '<div class="entry-list">' + t.sections.map(function (s, i) {
          return '<a class="entry-card pattern-card" href="dsa.html?topic=' +
            encodeURIComponent(t.id) + "&amp;pattern=" + encodeURIComponent(s.id) + '">' +
            '<span class="num">' + String(i).padStart(2, "0") + "</span>" +
            '<span class="body">' +
              '<span class="title">' + esc(s.title) + "</span>" +
              (s.summary ? '<span class="subtitle">' + s.summary + "</span>" : "") +
            "</span>" +
            progressBar(s.problems) +
          "</a>";
        }).join("") + "</div>";
      return;
    }

    var mode = "all";
    function paint() {
      var shown = t.problems.filter(function (p) {
        if (mode === "todo") return !progress.isSolved(p.id);
        if (mode === "starred") return progress.isStarred(p.id);
        return true;
      });
      document.getElementById("rows").innerHTML = shown.length
        ? problemRows(shown)
        : '<p class="empty">Nothing here yet.</p>';
      Array.prototype.forEach.call(document.querySelectorAll(".filter-chip"), function (b) {
        b.setAttribute("aria-pressed", b.dataset.mode === mode);
      });
    }
    root.innerHTML = head +
      '<div class="topic-tools">' + progressBar(t.problems) +
        '<span class="chips">' +
          ["all", "todo", "starred"].map(function (m) {
            return '<button type="button" class="chip filter-chip" data-mode="' + m + '">' +
              { all: "All", todo: "Unsolved", starred: "Starred" }[m] + "</button>";
          }).join("") +
        "</span>" +
      "</div>" +
      '<div id="rows"></div>';
    Array.prototype.forEach.call(document.querySelectorAll(".filter-chip"), function (b) {
      b.onclick = function () { mode = b.dataset.mode; paint(); };
    });
    paint();
  }

  /* ---------- one pattern: the idea, then its problems ---------- */
  function patternPage(t, i) {
    var s = t.sections[i];
    document.title = s.title + " — " + t.title + " — pyvault";

    var nav = function (j, label) {
      var o = t.sections[j];
      return o
        ? '<a href="dsa.html?topic=' + encodeURIComponent(t.id) + "&amp;pattern=" +
            encodeURIComponent(o.id) + '">' + label.replace("%", esc(o.title)) + "</a>"
        : "<span></span>";
    };

    root.innerHTML =
      '<p class="crumb-line"><a href="dsa.html">DSA</a> / ' + topicLink(t) +
        " / Pattern " + i + "</p>" +
      '<h2 class="topic-title">' + esc(s.title) + "</h2>" +
      (s.summary ? '<p class="topic-sub pattern-summary">' + s.summary + "</p>" : "") +
      (s.idea.length
        ? '<div class="pattern-idea">' +
            s.idea.map(function (para) { return "<p>" + para + "</p>"; }).join("") +
          "</div>"
        : "") +
      '<h3 class="pattern-list-head">Problems &middot; ' + s.problems.length + "</h3>" +
      problemRows(s.problems) +
      '<div class="entry-nav">' +
        nav(i - 1, "&larr; %") + nav(i + 1, "% &rarr;") +
      "</div>";
  }

  var topic = wanted && topics.filter(function (t) { return t.id === wanted; })[0];
  if (wanted && !topic) {
    root.innerHTML = "<h2>Unknown topic</h2>" +
      '<p><a href="dsa.html">&larr; Back to topics</a></p>';
  } else if (topic) {
    var wantedPattern = new URLSearchParams(location.search).get("pattern");
    var pi = wantedPattern
      ? (topic.sections || []).findIndex(function (s) { return s.id === wantedPattern; })
      : -1;
    if (pi !== -1) {
      patternPage(topic, pi);
    } else {
      topicPage(topic);
    }
  } else {
    topicIndex();
  }
})();
