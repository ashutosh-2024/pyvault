(function () {
  "use strict";

  function esc(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }
  window.esc = esc;

  /* ---------- python syntax highlighter ---------- */
  var KEYWORDS = "False|None|True|and|as|assert|async|await|break|case|class|continue|" +
    "def|del|elif|else|except|finally|for|from|global|if|import|in|is|lambda|match|" +
    "nonlocal|not|or|pass|raise|return|try|while|with|yield";

  var BUILTINS = "abs|all|any|bool|bytes|callable|dict|dir|enumerate|filter|float|" +
    "frozenset|getattr|hasattr|hash|id|int|isinstance|issubclass|iter|len|list|map|max|min|" +
    "next|object|open|print|range|repr|reversed|round|set|setattr|sorted|staticmethod|str|" +
    "sum|super|tuple|type|vars|zip|classmethod|property|divmod|" +
    "Exception|BaseException|NameError|TypeError|ValueError|AttributeError|KeyError|" +
    "IndexError|RuntimeError|StopIteration|ImportError|OverflowError|RecursionError|" +
    "UnboundLocalError|KeyboardInterrupt|SystemExit|UnicodeDecodeError|AssertionError";

  var PY_RE = new RegExp([
    "(?<ps1>^(?:>>>|\\.\\.\\.)(?= |$))",
    "(?<com>#[^\\n]*)",
    "(?<str>[rbfuRBFU]{0,2}(?:\"\"\"[\\s\\S]*?\"\"\"|'''[\\s\\S]*?'''|\"(?:\\\\.|[^\"\\\\\\n])*\"|'(?:\\\\.|[^'\\\\\\n])*'))",
    "(?<dec>@[A-Za-z_][\\w.]*)",
    "(?<defn>\\b(?:def|class)\\s+[A-Za-z_]\\w*)",
    "(?<num>\\b\\d[\\w.]*)",
    "(?<kw>\\b(?:" + KEYWORDS + ")\\b)",
    "(?<bi>\\b(?:" + BUILTINS + ")\\b)",
    "(?<dun>\\b__\\w+__\\b)",
    "(?<fn>\\b[A-Za-z_]\\w*(?=\\())"
  ].join("|"), "gm");

  function highlight(src) {
    var out = "", last = 0, m;
    PY_RE.lastIndex = 0;
    while ((m = PY_RE.exec(src)) !== null) {
      out += esc(src.slice(last, m.index));
      var g = m.groups;
      if (g.defn) {
        var parts = g.defn.split(/(\s+)/);
        out += '<span class="tok-kw">' + esc(parts[0]) + "</span>" + esc(parts[1]) +
               '<span class="tok-fn">' + esc(parts.slice(2).join("")) + "</span>";
      } else {
        var cls = g.ps1 ? "ps1" : g.com ? "com" : g.str ? "str" : g.dec ? "dec" :
                  g.num ? "num" : g.kw ? "kw" : g.bi ? "bi" : g.dun ? "dun" : "fn";
        out += '<span class="tok-' + cls + '">' + esc(m[0]) + "</span>";
      }
      last = m.index + m[0].length;
    }
    return out + esc(src.slice(last));
  }
  window.highlight = highlight;

  /* ---------- chrome present on every page ---------- */
  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("[data-year]").forEach(function (el) {
      el.textContent = new Date().getFullYear();
    });
    document.querySelectorAll("[data-python]").forEach(function (el) {
      el.textContent = window.GRAIL_PYTHON || "3.12+";
    });
    addThemeToggle();
    addCopyButtons(document);
    new MutationObserver(function (records) {
      records.forEach(function (r) {
        r.addedNodes.forEach(function (n) { if (n.nodeType === 1) addCopyButtons(n); });
      });
    }).observe(document.body, { childList: true, subtree: true });
    document.addEventListener("keydown", function (e) {
      var tag = (e.target.tagName || "").toLowerCase();
      if (e.key === "/" && !e.metaKey && !e.ctrlKey && !e.altKey &&
          tag !== "input" && tag !== "textarea" && tag !== "select" && !e.target.isContentEditable) {
        var box = document.getElementById("site-search");
        e.preventDefault();
        if (box) box.focus(); else location.href = "search.html";
      }
    });
  });

  /* ---------- light / dark toggle ---------- */
  function addThemeToggle() {
    var nav = document.querySelector(".site-header .nav");
    if (!nav || nav.querySelector(".theme-toggle")) return;
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "theme-toggle";
    function sync() {
      var light = document.documentElement.getAttribute("data-theme") === "light";
      btn.textContent = light ? "\u263E" : "\u2600";
      btn.title = light ? "Switch to dark theme" : "Switch to light theme";
      btn.setAttribute("aria-label", btn.title);
    }
    btn.addEventListener("click", function () {
      var next = document.documentElement.getAttribute("data-theme") === "light" ? "dark" : "light";
      document.documentElement.setAttribute("data-theme", next);
      try { localStorage.setItem("grail-theme", next); } catch (e) {}
      sync();
    });
    sync();
    var gh = nav.querySelector(".gh");
    nav.insertBefore(btn, gh ? gh.nextSibling : null);
  }

  /* ---------- copy button on every source block (not on outputs) ---------- */
  function copyText(text, done) {
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(done, function () { fallback(); });
    } else {
      fallback();
    }
    function fallback() {
      var ta = document.createElement("textarea");
      ta.value = text;
      ta.setAttribute("readonly", "");
      ta.style.position = "fixed"; ta.style.opacity = "0";
      document.body.appendChild(ta);
      ta.select();
      try { document.execCommand("copy"); done(); } catch (e) {}
      document.body.removeChild(ta);
    }
  }

  function addCopyButtons(scope) {
    var pres = scope.matches && scope.matches("pre.code") ? [scope]
             : scope.querySelectorAll ? scope.querySelectorAll("pre.code") : [];
    Array.prototype.forEach.call(pres, function (pre) {
      if (pre.classList.contains("output") || pre.classList.contains("rec-formula") ||
          (pre.parentNode && pre.parentNode.classList &&
           pre.parentNode.classList.contains("code-wrap"))) return;
      var wrap = document.createElement("div");
      wrap.className = "code-wrap";
      pre.parentNode.insertBefore(wrap, pre);
      wrap.appendChild(pre);
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "copy-btn";
      btn.textContent = "Copy";
      btn.setAttribute("aria-label", "Copy code to clipboard");
      btn.addEventListener("click", function () {
        copyText(pre.textContent, function () {
          btn.textContent = "Copied";
          btn.classList.add("done");
          setTimeout(function () { btn.textContent = "Copy"; btn.classList.remove("done"); }, 1400);
        });
      });
      wrap.appendChild(btn);
    });
  }
})();
