/* Site-wide search over search-index.js (built by build.py).
   Every query word must appear somewhere in a record; title hits rank first. */
(function () {
  "use strict";

  var esc = window.esc;
  var root = document.getElementById("search");
  var recs = (window.GRAIL_SEARCH || []).map(function (r) {
    r.tl = r.t.toLowerCase();
    r.cl = r.c.toLowerCase();
    r.bl = r.b.toLowerCase();
    return r;
  });

  var GROUPS = [
    ["all", "All", null],
    ["dsa", "DSA", ["dsa", "dsa-topic"]],
    ["deepdive", "Deep Dive", ["deepdive"]],
    ["databases", "Databases", ["databases"]],
    ["systemdesign", "System Design", ["systemdesign"]],
    ["lld", "LLD", ["lld"]],
    ["prep", "Prep", ["prep"]]
  ];
  var KIND_LABEL = {
    "dsa": "DSA problem", "dsa-topic": "DSA topic",
    "deepdive": "Deep Dive", "databases": "Databases",
    "systemdesign": "System Design", "lld": "LLD", "prep": "Prep"
  };
  var LONGFORM = { deepdive: 1, databases: 1, systemdesign: 1, lld: 1 };
  var PAGE = 40;

  var params = new URLSearchParams(location.search);
  var state = { q: params.get("q") || "", group: params.get("in") || "all", shown: PAGE, cursor: -1 };
  if (!GROUPS.some(function (g) { return g[0] === state.group; })) state.group = "all";

  root.innerHTML =
    '<div class="search-box search-big">' +
      '<input id="site-search" type="search" autocomplete="off" spellcheck="false" ' +
        'placeholder="Try: sliding window, GIL, MVCC, rate limiter, 239, __slots__" ' +
        'aria-label="Search the whole site">' +
    "</div>" +
    '<div class="chips search-groups" id="search-groups"></div>' +
    '<p class="result-count" id="search-count"></p>' +
    '<div id="search-results" class="sr-list" role="listbox"></div>';

  var input = document.getElementById("site-search");
  var groupsEl = document.getElementById("search-groups");
  var countEl = document.getElementById("search-count");
  var listEl = document.getElementById("search-results");
  input.value = state.q;

  function tokens(q) {
    return q.toLowerCase().replace(/[^\w\s.#+-]/g, " ").split(/\s+/).filter(Boolean);
  }

  function wordStart(text, tok) {
    var i = text.indexOf(tok);
    while (i !== -1) {
      if (i === 0 || /[^a-z0-9]/.test(text[i - 1])) return true;
      i = text.indexOf(tok, i + 1);
    }
    return false;
  }

  function score(r, toks, phrase) {
    var s = 0;
    for (var i = 0; i < toks.length; i++) {
      var t = toks[i], hit = false;
      if (r.tl.indexOf(t) !== -1) { s += wordStart(r.tl, t) ? 14 : 8; hit = true; }
      if (r.cl.indexOf(t) !== -1) { s += 4; hit = true; }
      if (r.bl.indexOf(t) !== -1) { s += 1; hit = true; }
      if (!hit) return 0;
    }
    if (r.tl === phrase) s += 60;
    else if (r.tl.indexOf(phrase) === 0) s += 30;
    else if (toks.length > 1 && r.tl.indexOf(phrase) !== -1) s += 20;
    if (/^\d+$/.test(phrase) && r.tl.indexOf(phrase + ". ") === 0) s += 80;   /* LeetCode number */
    if (r.k === "dsa-topic" || /\?topic=[^#]*$/.test(r.u)) s += 2;     /* a whole topic page */
    return s;
  }

  function mark(text, toks) {
    var html = esc(text);
    var words = toks.filter(function (t) { return t.length > 1; })
      .map(function (t) { return esc(t).replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); });
    if (!words.length) return html;
    return html.replace(new RegExp("(" + words.join("|") + ")", "gi"), "<mark>$1</mark>");
  }

  function inGroup(r, g) {
    var kinds = GROUPS.filter(function (x) { return x[0] === g; })[0][2];
    return !kinds || kinds.indexOf(r.k) !== -1;
  }

  function syncUrl() {
    var p = new URLSearchParams();
    if (state.q) p.set("q", state.q);
    if (state.group !== "all") p.set("in", state.group);
    var qs = p.toString();
    history.replaceState(null, "", "search.html" + (qs ? "?" + qs : ""));
    document.title = (state.q ? state.q + " — " : "") + "Search — pyvault";
  }

  function examples() {
    var ex = ["sliding window", "monotonic stack", "GIL", "__slots__", "MVCC",
              "consistent hashing", "rate limiter", "parking lot", "strategy pattern", "KMP", "segment tree", "generator", "239"];
    return '<div class="sr-empty"><p class="code-label">Try</p><div class="chips">' +
      ex.map(function (e) {
        return '<a class="chip" href="search.html?q=' + encodeURIComponent(e) + '">' + esc(e) + "</a>";
      }).join("") +
      '</div><p class="sr-hint">Press <kbd>/</kbd> on any page to jump here. ' +
      recs.length + " pages indexed.</p></div>";
  }

  function render() {
    var toks = tokens(state.q);
    var phrase = toks.join(" ");
    syncUrl();

    if (!toks.length) {
      groupsEl.innerHTML = "";
      countEl.textContent = "";
      listEl.innerHTML = examples();
      return;
    }

    var hits = [];
    for (var i = 0; i < recs.length; i++) {
      var sc = score(recs[i], toks, phrase);
      if (sc) hits.push({ r: recs[i], s: sc });
    }
    hits.sort(function (a, b) { return b.s - a.s || a.r.t.length - b.r.t.length; });

    groupsEl.innerHTML = GROUPS.map(function (g) {
      var n = hits.filter(function (h) { return inGroup(h.r, g[0]); }).length;
      if (!n && g[0] !== "all" && g[0] !== state.group) return "";
      return '<button type="button" class="chip" data-group="' + g[0] + '" aria-pressed="' +
        (g[0] === state.group) + '">' + g[1] + " <span class=\"sr-n\">" + n + "</span></button>";
    }).join("");

    var shown = hits.filter(function (h) { return inGroup(h.r, state.group); });
    countEl.textContent = shown.length + (shown.length === 1 ? " result" : " results");

    if (!shown.length) {
      listEl.innerHTML = '<p class="empty">Nothing matches every word. Try fewer words.</p>';
      return;
    }

    listEl.innerHTML = shown.slice(0, state.shown).map(function (h, i) {
      var r = h.r;
      return '<a class="sr-item" role="option" data-i="' + i + '" href="' + esc(r.u) + '">' +
        '<span class="sr-kind k-' + r.k + '">' + KIND_LABEL[r.k] + "</span>" +
        '<span class="sr-main"><span class="sr-title">' + mark(r.t, toks) + "</span>" +
          '<span class="sr-ctx">' + esc(r.c) + "</span></span>" +
        (r.d ? '<span class="badge ' + (LONGFORM[r.k] ? "lvl-" : "") + r.d + '">' + r.d + "</span>" : "") +
      "</a>";
    }).join("") +
    (shown.length > state.shown
      ? '<button type="button" class="btn sr-more" id="sr-more">Show ' +
        Math.min(PAGE, shown.length - state.shown) + " more</button>"
      : "");
    state.cursor = -1;
  }

  var timer;
  input.addEventListener("input", function () {
    clearTimeout(timer);
    timer = setTimeout(function () {
      state.q = input.value.trim();
      state.shown = PAGE;
      render();
    }, 80);
  });

  groupsEl.addEventListener("click", function (e) {
    var b = e.target.closest("[data-group]");
    if (!b) return;
    state.group = b.dataset.group;
    state.shown = PAGE;
    render();
  });

  listEl.addEventListener("click", function (e) {
    if (e.target.id === "sr-more") {
      state.shown += PAGE;
      render();
    }
  });

  /* arrow keys move through results, Enter opens */
  function items() { return listEl.querySelectorAll(".sr-item"); }
  function focusItem(i) {
    var all = items();
    if (!all.length) return;
    state.cursor = Math.max(-1, Math.min(all.length - 1, i));
    if (state.cursor === -1) input.focus();
    else all[state.cursor].focus();
  }
  document.addEventListener("keydown", function (e) {
    if (e.key === "ArrowDown") { e.preventDefault(); focusItem(state.cursor + 1); }
    else if (e.key === "ArrowUp") { e.preventDefault(); focusItem(state.cursor - 1); }
    else if (e.key === "Enter" && document.activeElement === input) {
      var first = items()[0];
      if (first) location.href = first.getAttribute("href");
    }
  });

  render();
  input.focus();
})();
