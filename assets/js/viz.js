/* Step-by-step algorithm animations (data from content/viz/, built by build.py).

   window.renderViz(container, viz) draws a carousel: chapter tabs, an SVG stage
   (grid, optional array row, arrows, path), the formula and caption for the
   current frame, and controls (restart, prev, play/pause, next, scrubber,
   speed). Cells are kept between frames and only their class and text change,
   so colours and values animate with CSS transitions. */
(function () {
  "use strict";

  var SVG = "http://www.w3.org/2000/svg";
  var CELL = 54, GAP = 6, PAD = 8, LABEL_W = 46, ARRAY_GAP = 30, IDX = 20;   // IDX: room for row/col numbers

  var LEGEND = {
    base: "base case", cur: "computing now", src: "read from", done: "computed",
    dim: "finished, kept only for show", path: "a route", start: "start", goal: "goal",
    answer: "answer", stack: "waiting on the call stack", wall: "blocked",
    yes: "reachable / true", no: "not reachable / false", chosen: "chosen",
    heat1: "computed 1&times;", heat2: "2&times;", heat3: "3&times;", heat4: "4&times;", heat5: "5+&times;"
  };
  var HEAT = ["heat1", "heat2", "heat3", "heat4", "heat5"];

  function el(name, attrs, parent) {
    var n = document.createElementNS(SVG, name);
    for (var k in attrs) n.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(n);
    return n;
  }

  function dims(frame) {
    var g = frame.grid, a = frame.array;
    var rl = g && g.rowLabels ? g.rowLabels : null;
    return {
      rows: g ? g.v.length : 0,
      cols: g ? g.v[0].length : 0,
      arr: a ? a.v.length : 0,
      rowLabels: rl,
      colLabels: g && g.colLabels ? g.colLabels : null,
      rowLabelW: rl ? Math.max(IDX, 10 + 8.5 * Math.max.apply(null, rl.map(function (x) { return String(x).length; }))) : IDX
    };
  }

  function layout(d) {
    var gridW = d.cols ? d.rowLabelW + d.cols * (CELL + GAP) - GAP : 0;
    var arrW = d.arr ? LABEL_W + d.arr * (CELL + GAP) - GAP : 0;
    var gridH = d.rows ? IDX + d.rows * (CELL + GAP) - GAP : 0;
    var width = Math.max(gridW, arrW) + 2 * PAD;
    var arrY = PAD + gridH + (d.rows && d.arr ? ARRAY_GAP : 0);
    var height = arrY + (d.arr ? CELL + 16 : 0) + PAD;
    var gx = PAD + (width - 2 * PAD - gridW) / 2 + d.rowLabelW;
    var ax = PAD + (width - 2 * PAD - arrW) / 2 + LABEL_W;
    return { width: width, height: height, gx: gx, gy: PAD + IDX, ax: ax, ay: arrY };
  }

  function center(L, r, c) {
    return [L.gx + c * (CELL + GAP) + CELL / 2, L.gy + r * (CELL + GAP) + CELL / 2];
  }

  window.renderViz = function (root, viz) {
    if (!root || !viz || !viz.chapters) return;
    var esc = window.esc;
    var state = { ch: 0, fr: 0, playing: false, timer: null, speed: 1 };
    var stage = null;                 // { svg, cells, arrayCells, overlay, key }

    root.classList.add("viz");
    root.setAttribute("tabindex", "0");
    root.innerHTML =
      '<div class="viz-tabs" role="tablist">' +
        viz.chapters.map(function (ch, i) {
          return '<button type="button" role="tab" class="viz-tab" data-ch="' + i + '">' +
            '<span class="viz-tab-n">' + (i + 1) + "</span>" + esc(ch.title) + "</button>";
        }).join("") +
      "</div>" +
      '<div class="viz-stage"></div>' +
      '<div class="viz-legend"></div>' +
      '<pre class="viz-formula" aria-live="polite"></pre>' +
      '<p class="viz-caption" aria-live="polite"></p>' +
      '<div class="viz-controls">' +
        '<button type="button" class="viz-btn" data-act="restart" title="Restart chapter" aria-label="Restart chapter">&#x23EE;</button>' +
        '<button type="button" class="viz-btn" data-act="prev" title="Previous step (&larr;)" aria-label="Previous step">&#x25C0;</button>' +
        '<button type="button" class="viz-btn viz-play" data-act="play" title="Play / pause (space)" aria-label="Play">&#x25B6;</button>' +
        '<button type="button" class="viz-btn" data-act="next" title="Next step (&rarr;)" aria-label="Next step">&#x25B6;&#x25B6;</button>' +
        '<input type="range" class="viz-scrub" min="0" value="0" aria-label="Step">' +
        '<span class="viz-count"></span>' +
        '<select class="viz-speed" aria-label="Speed">' +
          '<option value="0.5">0.5&times;</option><option value="1" selected>1&times;</option>' +
          '<option value="2">2&times;</option></select>' +
      "</div>";

    var $ = function (s) { return root.querySelector(s); };
    var stageEl = $(".viz-stage"), captionEl = $(".viz-caption"), formulaEl = $(".viz-formula");
    var scrub = $(".viz-scrub"), countEl = $(".viz-count"), playBtn = $(".viz-play");
    var legendEl = $(".viz-legend");

    function chapter() { return viz.chapters[state.ch]; }
    function frame() { return chapter().frames[state.fr]; }

    /* build the SVG skeleton for a chapter's dimensions (rebuilt only when they change) */
    function buildStage(f) {
      var d = dims(f), L = layout(d);
      var key = [d.rows, d.cols, d.arr].join("x") + JSON.stringify([d.rowLabels, d.colLabels]);
      if (stage && stage.key === key) return stage;
      stageEl.innerHTML = "";
      var svg = el("svg", { viewBox: "0 0 " + L.width + " " + L.height, class: "viz-svg",
                            role: "img", "aria-label": "algorithm state" }, stageEl);
      svg.style.maxWidth = Math.min(780, Math.round(L.width * 1.2)) + "px";
      var defs = el("defs", {}, svg);
      var marker = el("marker", { id: "vz-head-" + Math.random().toString(36).slice(2, 9),
        viewBox: "0 0 10 10", refX: "8", refY: "5", markerWidth: "4", markerHeight: "4", orient: "auto-start-reverse" }, defs);
      el("path", { d: "M0,0 L10,5 L0,10 z", class: "vz-head" }, marker);

      var boxes = el("g", {}, svg);
      var overlay = el("g", { class: "vz-overlay" }, svg);
      var texts = el("g", { class: "vz-texts" }, svg);
      function cellAt(x, y) {
        var g = el("g", { class: "vz-cell", transform: "translate(" + x + "," + y + ")" }, boxes);
        el("rect", { width: CELL, height: CELL, rx: 4 }, g);
        var t = el("text", { x: x + CELL / 2, y: y + CELL / 2 + 1, "text-anchor": "middle",
                             "dominant-baseline": "middle", class: "vz-txt" }, texts);
        return { g: g, t: t, v: null };
      }
      var cells = [];
      for (var cc = 0; cc < d.cols; cc++) {                 // column numbers or labels
        el("text", { x: L.gx + cc * (CELL + GAP) + CELL / 2, y: L.gy - 7, "text-anchor": "middle",
                     class: d.colLabels ? "vz-index vz-named" : "vz-index" }, svg).textContent =
          d.colLabels ? d.colLabels[cc] : cc;
      }
      for (var rr = 0; rr < d.rows; rr++) {                 // row numbers or labels
        el("text", { x: L.gx - 8, y: L.gy + rr * (CELL + GAP) + CELL / 2 + 1, "text-anchor": "end",
                     "dominant-baseline": "middle", class: d.rowLabels ? "vz-index vz-named" : "vz-index" }, svg).textContent =
          d.rowLabels ? d.rowLabels[rr] : rr;
      }
      for (var r = 0; r < d.rows; r++) {
        cells.push([]);
        for (var c = 0; c < d.cols; c++) {
          cells[r].push(cellAt(L.gx + c * (CELL + GAP), L.gy + r * (CELL + GAP)));
        }
      }
      var arrayCells = [];
      if (d.arr) {
        var lab = el("text", { x: L.ax - 10, y: L.ay + CELL / 2 + 1, "text-anchor": "end",
                               "dominant-baseline": "middle", class: "vz-label" }, svg);
        for (var i = 0; i < d.arr; i++) {
          var x = L.ax + i * (CELL + GAP);
          arrayCells.push(cellAt(x, L.ay));
          el("text", { x: x + CELL / 2, y: L.ay + CELL + 14, "text-anchor": "middle", class: "vz-index" }, svg).textContent = i;
        }
        arrayCells.label = lab;
      }
      stage = { svg: svg, cells: cells, arrayCells: arrayCells, overlay: overlay, key: key, L: L,
                marker: marker.getAttribute("id") };
      return stage;
    }

    function setCell(cell, value, cls) {
      var changed = cell.v !== null && cell.v !== value && value !== "";
      cell.g.setAttribute("class", "vz-cell" + (cls ? " " + cls : ""));
      cell.t.setAttribute("class", "vz-txt" + (cls ? " " + cls : ""));
      if (changed) {
        cell.t.getBoundingClientRect();          // restart the pop animation
        cell.t.setAttribute("class", "vz-txt" + (cls ? " " + cls : "") + " vz-changed");
      }
      cell.t.textContent = value;
      var len = String(value).length;
      if (len >= 4) cell.t.classList.add(len >= 6 ? "vz-xs" : "vz-sm");
      cell.v = value;
    }

    function drawOverlay(f) {
      var o = stage.overlay, L = stage.L;
      o.innerHTML = "";
      if (f.path && f.path.length > 1) {
        var pts = f.path.map(function (p) { return center(L, p[0], p[1]).join(","); }).join(" ");
        el("polyline", { points: pts, class: "vz-path" }, o);
      }
      (f.arrows || []).forEach(function (a) {
        var p1 = center(L, a[0], a[1]), p2 = center(L, a[2], a[3]);
        var dx = p2[0] - p1[0], dy = p2[1] - p1[1], len = Math.hypot(dx, dy) || 1;
        var start = 15, end = CELL / 2 - 3;               // start inside the source cell
        var far = (a[0] === a[2] && Math.abs(a[1] - a[3]) > 1) || (a[1] === a[3] && Math.abs(a[0] - a[2]) > 1);
        if (far) {                                         // long jump along a row/column: curve around the cells between
          var bend = Math.min(CELL * 1.1, len * 0.35);
          var nx = a[0] === a[2] ? 0 : -1, ny = a[0] === a[2] ? -1 : 0;   // bow upward (row) or left (column)
          var s1 = [p1[0] + nx * 18, p1[1] + ny * 18], s2 = [p2[0] + nx * 22, p2[1] + ny * 22];
          var mx = (s1[0] + s2[0]) / 2 + nx * bend, my = (s1[1] + s2[1]) / 2 + ny * bend;
          el("path", { d: "M" + s1[0] + "," + s1[1] + " Q" + mx + "," + my + " " + s2[0] + "," + s2[1],
                       class: "vz-arrow vz-curve", "marker-end": "url(#" + stage.marker + ")" }, o);
        } else {
          el("line", {
            x1: p1[0] + dx / len * start, y1: p1[1] + dy / len * start,
            x2: p2[0] - dx / len * end, y2: p2[1] - dy / len * end,
            class: "vz-arrow", "marker-end": "url(#" + stage.marker + ")"
          }, o);
        }
      });
    }

    function legendFor(ch) {
      var seen = {}, order = [];
      ch.frames.forEach(function (f) {
        var add = function (c) { if (c && LEGEND[c] && !seen[c]) { seen[c] = 1; order.push(c); } };
        if (f.grid) f.grid.cls.forEach(function (row) { row.forEach(add); });
        if (f.array) f.array.cls.forEach(add);
      });
      var heat = order.filter(function (c) { return HEAT.indexOf(c) !== -1; }).sort();
      order = order.filter(function (c) { return HEAT.indexOf(c) === -1; });
      return order.map(function (c) {
        return '<span class="viz-key"><span class="vz-swatch ' + c + '"></span>' + LEGEND[c] + "</span>";
      }).join("") +
      (heat.length ? '<span class="viz-key">' + heat.map(function (c) {
        return '<span class="vz-swatch ' + c + '"></span>';
      }).join("") + " computed 1&times; &rarr; 5+&times;</span>" : "");
    }

    function show() {
      var ch = chapter(), f = frame();
      buildStage(f);
      if (f.grid) {
        for (var r = 0; r < f.grid.v.length; r++)
          for (var c = 0; c < f.grid.v[r].length; c++)
            setCell(stage.cells[r][c], f.grid.v[r][c], f.grid.cls[r][c]);
      }
      if (f.array) {
        stage.arrayCells.label.textContent = f.array.label;
        f.array.v.forEach(function (v, i) { setCell(stage.arrayCells[i], v, f.array.cls[i]); });
      }
      drawOverlay(f);
      captionEl.innerHTML = f.caption;
      formulaEl.textContent = f.formula || "";
      formulaEl.hidden = !f.formula;
      scrub.max = ch.frames.length - 1;
      scrub.value = state.fr;
      countEl.textContent = "step " + (state.fr + 1) + " / " + ch.frames.length;
      root.querySelectorAll(".viz-tab").forEach(function (b, i) {
        b.setAttribute("aria-selected", String(i === state.ch));
      });
      var last = state.fr === ch.frames.length - 1;
      $('[data-act="next"]').classList.toggle("viz-next-chapter", last && state.ch < viz.chapters.length - 1);
      $('[data-act="next"]').title = last && state.ch < viz.chapters.length - 1 ? "Next chapter" : "Next step (→)";
    }

    function goChapter(i) {
      state.ch = i; state.fr = 0;
      stage = null;                               // dimensions may differ
      legendEl.innerHTML = legendFor(chapter());
      show();
    }

    function step(delta) {
      var n = chapter().frames.length;
      if (state.fr + delta >= n) {
        if (state.ch < viz.chapters.length - 1) { goChapter(state.ch + 1); return true; }
        return false;
      }
      if (state.fr + delta < 0) return false;
      state.fr += delta;
      show();
      return true;
    }

    function setPlaying(on) {
      state.playing = on;
      clearInterval(state.timer);
      playBtn.innerHTML = on ? "&#x23F8;" : "&#x25B6;";
      playBtn.setAttribute("aria-label", on ? "Pause" : "Play");
      root.classList.toggle("viz-is-playing", on);
      if (on) {
        if (state.fr === chapter().frames.length - 1) { state.fr = -1; }
        state.timer = setInterval(function () {
          var n = chapter().frames.length;
          if (state.fr >= n - 1) { setPlaying(false); return; }  // stop at chapter end
          step(1);
        }, 1600 / state.speed);
        if (state.fr === -1) { state.fr = 0; show(); }
      }
    }

    root.addEventListener("click", function (e) {
      var tab = e.target.closest(".viz-tab");
      if (tab) { setPlaying(false); goChapter(+tab.dataset.ch); return; }
      var btn = e.target.closest("[data-act]");
      if (!btn) return;
      var act = btn.dataset.act;
      if (act === "play") { setPlaying(!state.playing); return; }
      setPlaying(false);
      if (act === "next") step(1);
      else if (act === "prev") step(-1);
      else if (act === "restart") { state.fr = 0; show(); }
    });
    scrub.addEventListener("input", function () {
      setPlaying(false);
      state.fr = +scrub.value;
      show();
    });
    $(".viz-speed").addEventListener("change", function (e) {
      state.speed = +e.target.value;
      if (state.playing) setPlaying(true);
    });
    root.addEventListener("keydown", function (e) {
      if (e.target.tagName === "SELECT" || e.target.tagName === "INPUT") return;
      if (e.key === "ArrowRight") { e.preventDefault(); setPlaying(false); step(1); }
      else if (e.key === "ArrowLeft") { e.preventDefault(); setPlaying(false); step(-1); }
      else if (e.key === " ") { e.preventDefault(); setPlaying(!state.playing); }
    });

    goChapter(0);
  };
})();
