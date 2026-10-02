/* Solved / starred problems, practice preferences and editor drafts.
   Everything lives in this browser's localStorage; the site has no server.
   Every access is wrapped so a blocked or private-mode store just means
   progress is not remembered, never a broken page. */
(function () {
  "use strict";

  var KEY = "grail.progress.v1";

  function load() {
    try {
      var v = JSON.parse(localStorage.getItem(KEY) || "{}");
      return { solved: v.solved || {}, starred: v.starred || {}, prefs: v.prefs || {} };
    } catch (e) {
      return { solved: {}, starred: {}, prefs: {} };
    }
  }

  var state = load();

  function save() {
    try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) { /* ignore */ }
  }

  window.addEventListener("storage", function (e) {
    if (e.key === KEY) state = load();               // another tab changed it
  });

  window.progress = {
    isSolved: function (id) { return !!state.solved[id]; },
    isStarred: function (id) { return !!state.starred[id]; },
    setSolved: function (id, on) {
      if (on) state.solved[id] = Date.now(); else delete state.solved[id];
      save();
    },
    toggleSolved: function (id) { this.setSolved(id, !state.solved[id]); return !!state.solved[id]; },
    toggleStarred: function (id) {
      if (state.starred[id]) delete state.starred[id]; else state.starred[id] = Date.now();
      save();
      return !!state.starred[id];
    },
    countSolved: function (ids) {
      return ids.filter(function (id) { return state.solved[id]; }).length;
    },
    pref: function (name, fallback) {
      return name in state.prefs ? state.prefs[name] : fallback;
    },
    setPref: function (name, value) { state.prefs[name] = value; save(); },
    draft: function (id) {
      try { return localStorage.getItem("grail.draft." + id); } catch (e) { return null; }
    },
    saveDraft: function (id, text) {
      try { localStorage.setItem("grail.draft." + id, text); } catch (e) { /* ignore */ }
    },
    clearDraft: function (id) {
      try { localStorage.removeItem("grail.draft." + id); } catch (e) { /* ignore */ }
    },
    mock: function () {
      try { return JSON.parse(localStorage.getItem("grail.mock") || "null"); } catch (e) { return null; }
    },
    setMock: function (m) {
      try {
        if (m) localStorage.setItem("grail.mock", JSON.stringify(m));
        else localStorage.removeItem("grail.mock");
      } catch (e) { /* ignore */ }
    },
  };
})();
