(function () {
  "use strict";

  var esc = window.esc;
  var hl = window.highlight;
  var root = document.getElementById("deepdive");
  /* one renderer, two sections: the page says which data and names to use */
  var topics = window[root.dataset.var || "GRAIL_DEEP"] || [];
  var page = root.dataset.page || "deepdive.html";
  var name = root.dataset.name || "Deep Dive";
  var docTitle = root.dataset.title || "Python Deep Dive";
  var caveatLabel = root.dataset.caveat || "CPython detail";
  var wanted = new URLSearchParams(location.search).get("topic");

  function plural(n, word) {
    return n + " " + word + (n === 1 ? "" : "s");
  }

  function slug(s) {
    return s.replace(/<[^>]+>|&\w+;/g, "").toLowerCase()
      .replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
  }

  /* ---------- one block of content ---------- */
  function block(b) {
    if (b.type === "p") return "<p>" + b.html + "</p>";

    if (b.type === "code") {
      var html = (b.label ? '<p class="code-label">' + esc(b.label) + "</p>" : "") +
        '<pre class="code"><code>' + hl(b.src) + "</code></pre>";
      if (b.output !== undefined && b.output !== "") {
        html += '<p class="code-label">' +
            (b.isError ? "output (ends in a traceback)" : "output") + "</p>" +
          '<pre class="code output' + (b.isError ? " error" : "") + '"><code>' +
            esc(b.output) + "</code></pre>";
      }
      return html;
    }

    if (b.type === "table") {
      return '<div class="dd-table-wrap"><table class="dd-table"><thead><tr>' +
        b.head.map(function (h) { return "<th>" + h + "</th>"; }).join("") +
        "</tr></thead><tbody>" +
        b.rows.map(function (r) {
          return "<tr>" + r.map(function (c) { return "<td>" + c + "</td>"; }).join("") + "</tr>";
        }).join("") +
        "</tbody></table></div>";
    }

    if (b.type === "note") {
      return '<div class="takeaway"><strong>Rule of thumb.</strong> ' + b.text + "</div>";
    }

    if (b.type === "caveat") {
      return '<div class="dd-caveat"><strong>' + esc(caveatLabel) + '.</strong> ' + b.text + "</div>";
    }
    return "";
  }

  function blocks(list) {
    return list.map(block).join("");
  }

  /* ---------- topic index: one row per topic, same card as Browse ---------- */
  function topicCard(t) {
    var tags = (t.tags && t.tags.length)
      ? t.tags.map(function (g) { return '<span class="tag tag-pattern">' + esc(g) + "</span>"; }).join("")
      : '<span class="tag">' + plural(t.sections.length, "section") + "</span>" +
        '<span class="tag">' + plural(t.questions.length, "interview question") + "</span>";
    return '<a class="entry-card" data-tags="' + esc((t.tags || []).join("|")) + '" href="' +
        page + '?topic=' + encodeURIComponent(t.id) + '">' +
        '<span class="body">' +
          '<span class="title">' + esc(t.title) + "</span>" +
          (t.summary ? '<br><span class="subtitle">' + t.summary + "</span>" : "") +
          '<span class="tags">' + tags + "</span>" +
        "</span>" +
        (t.level ? '<span class="badge lvl-' + t.level + '">' + t.level + "</span>" : "") +
      "</a>";
  }

  /* topics may carry a `group`; groups are listed in order of first appearance */
  function topicIndex() {
    document.title = docTitle + " — pyvault";
    var groups = [], byGroup = {};
    topics.forEach(function (t) {
      var g = t.group || "";
      if (!(g in byGroup)) { byGroup[g] = []; groups.push(g); }
      byGroup[g].push(t);
    });
    root.innerHTML = groups.map(function (g) {
      var list = byGroup[g];
      var allTags = [];
      list.forEach(function (t) {
        (t.tags || []).forEach(function (x) { if (allTags.indexOf(x) === -1) allTags.push(x); });
      });
      allTags.sort();
      var filter = allTags.length > 1
        ? '<p class="code-label">Filter by pattern</p><div class="chips dd-filter">' +
            '<button type="button" class="chip" aria-pressed="true" data-tag="">All ' + list.length + "</button>" +
            allTags.map(function (x) {
              var n = list.filter(function (t) { return t.tags.indexOf(x) !== -1; }).length;
              return '<button type="button" class="chip" aria-pressed="false" data-tag="' + esc(x) + '">' +
                esc(x) + ' <span class="sr-n">' + n + "</span></button>";
            }).join("") + "</div>"
        : "";
      return '<section class="dd-group">' +
        (g ? '<h2 class="section-title">' + esc(g) + "</h2>" : "") + filter +
        '<div class="entry-list">' + list.map(topicCard).join("") + "</div></section>";
    }).join("");

    root.querySelectorAll(".dd-filter").forEach(function (bar) {
      bar.addEventListener("click", function (e) {
        var chip = e.target.closest("[data-tag]");
        if (!chip) return;
        var tag = chip.dataset.tag;
        bar.querySelectorAll(".chip").forEach(function (c) { c.setAttribute("aria-pressed", String(c === chip)); });
        bar.parentNode.querySelectorAll(".entry-card").forEach(function (card) {
          var tags = card.dataset.tags ? card.dataset.tags.split("|") : [];
          card.hidden = !!tag && tags.indexOf(tag) === -1;
        });
      });
    });
  }

  /* ---------- one topic: theory, then interview questions ---------- */
  function topicPage(t, idx) {
    document.title = t.title + " — " + docTitle + " — pyvault";

    var html =
      '<p class="crumb-line"><a href="' + page + '">' + esc(name) + "</a> / " + esc(t.title) + "</p>" +
      '<h2 class="dd-topic-title">' + esc(t.title) + "</h2>" +
      ((t.tags && t.tags.length) || t.level
        ? '<p class="dd-meta">' + (t.level ? '<span class="badge lvl-' + t.level + '">' + t.level + "</span>" : "") +
          (t.tags || []).map(function (g) { return '<span class="tag tag-pattern">' + esc(g) + "</span>"; }).join("") + "</p>"
        : "") +
      '<div class="dd-intro">' + t.intro.map(function (p) { return "<p>" + p + "</p>"; }).join("") + "</div>";

    /* contents */
    html += '<nav class="dd-toc" aria-label="On this page"><p class="code-label">On this page</p><ol>' +
      t.sections.map(function (s) {
        return '<li><a href="#' + slug(s.title) + '">' + s.title + "</a></li>";
      }).join("") +
      '<li class="dd-toc-q"><a href="#interview-questions">Interview questions (' +
        t.questions.length + ")</a></li>" +
      "</ol></nav>";

    /* theory */
    html += t.sections.map(function (s) {
      return '<section class="dd-section" id="' + slug(s.title) + '">' +
        "<h2>" + s.title + "</h2>" + blocks(s.body) + "</section>";
    }).join("");

    /* interview questions */
    html += '<section class="dd-section" id="interview-questions">' +
      "<h2>Interview questions</h2>" +
      '<p class="dd-q-hint">Medium to hard questions asked on this topic. Answer out loud first, then open the answer.</p>' +
      '<div class="dd-questions">' +
      t.questions.map(function (q) {
        return '<details class="dd-q">' +
          "<summary>" +
            '<span class="badge lvl-' + q.level + '">' + q.level + "</span>" +
            '<span class="dd-q-text">' + q.q + "</span>" +
          "</summary>" +
          '<div class="dd-a">' + blocks(q.answer) + "</div>" +
        "</details>";
      }).join("") +
      "</div></section>";

    /* references */
    if (t.refs && t.refs.length) {
      html += "<h2>References</h2><ul class=\"refs\">" +
        t.refs.map(function (r) {
          return '<li><a href="' + r.url + '" target="_blank" rel="noopener">' + esc(r.label) + "</a></li>";
        }).join("") + "</ul>";
    }

    /* prev / next topic */
    var prev = topics[idx - 1], next = topics[idx + 1];
    html += '<div class="entry-nav">' +
      (prev ? '<a href="' + page + '?topic=' + encodeURIComponent(prev.id) + '">&larr; ' + esc(prev.title) + "</a>"
            : '<a href="' + page + '">&larr; All topics</a>') +
      (next ? '<a href="' + page + '?topic=' + encodeURIComponent(next.id) + '">' + esc(next.title) + " &rarr;</a>"
            : '<a href="' + page + '">All topics &rarr;</a>') +
      "</div>";

    root.innerHTML = html;

    /* the page is built after load, so honour a #section link by hand */
    if (location.hash) {
      var target = document.getElementById(location.hash.slice(1));
      if (target) target.scrollIntoView();
    }
  }

  var idx = wanted ? topics.findIndex(function (t) { return t.id === wanted; }) : -1;
  if (wanted && idx === -1) {
    root.innerHTML = '<h2 class="dd-topic-title">Unknown topic</h2>' +
      '<p><a href="' + page + '">&larr; Back to topics</a></p>';
  } else if (idx !== -1) {
    topicPage(topics[idx], idx);
  } else {
    topicIndex();
  }
})();
