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
      '<div class="viz-body"><div class="viz-stage"></div>' +
        '<pre class="viz-code" hidden aria-label="the code, current line highlighted"></pre></div>' +
      '<div class="viz-legend"></div>' +
      '<div class="viz-vars" hidden></div>' +
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
    var legendEl = $(".viz-legend"), codeEl = $(".viz-code"), varsEl = $(".viz-vars");
    var bodyEl = $(".viz-body");
    var scene = null;                 // layout + live elements of a traced chapter

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
      if (ch.code !== undefined) { showScene(ch, f); return; }
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
      scene = null;
      var ch = chapter(), traced = ch.code !== undefined;
      codeEl.hidden = !traced;
      varsEl.hidden = !traced;
      formulaEl.hidden = true;
      bodyEl.classList.toggle("viz-traced", traced);
      if (traced) {
        buildScene(ch);
        legendEl.innerHTML = sceneLegend(ch);
      } else {
        legendEl.innerHTML = legendFor(ch);
      }
      show();
    }

    /* ================= traced chapters (content/viz/auto.py) =================
       A frame is a list of panels (arrays with index pointers, grids, and
       node-link diagrams for trees, lists, graphs, tries and heaps), plus the
       variables, the call stack and the line that just ran. Every element is
       keyed, so between frames cells change colour, pointers slide and nodes
       move instead of the picture being redrawn. */
    var SC = 40, SG = 4, WRAP = 16, U = 46, R = 17, LBL = 22, PGAP = 22;
    var SCENE_LEGEND = {
      cur: "current / just changed", src: "pointed at by an index", yes: "a 1 bit", stack: "waiting (stack, queue or caller)",
      done: "visited", path: "in a visited set", answer: "root / end of word / result"
    };

    function sceneLegend(ch) {
      var seen = {}, order = [];
      ch.frames.forEach(function (f) {
        (f.panels || []).forEach(function (p) {
          var add = function (c) { if (c && SCENE_LEGEND[c] && !seen[c]) { seen[c] = 1; order.push(c); } };
          if (p.t === "arr") p.cls.forEach(add);
          else if (p.t === "grid") p.cls.forEach(function (r) { r.forEach(add); });
          else p.nodes.forEach(function (n) { add(n[4]); });
        });
      });
      return order.map(function (c) {
        return '<span class="viz-key"><span class="vz-swatch ' + c + '"></span>' + SCENE_LEGEND[c] + "</span>";
      }).join("");
    }

    function buildScene(ch) {
      /* one fixed slot per panel id, sized for the largest it gets in the chapter */
      var meta = {}, order = [];
      ch.frames.forEach(function (f) {
        (f.panels || []).forEach(function (p) {
          var m = meta[p.id];
          if (!m) { m = meta[p.id] = { t: p.t, n: 0, rows: 0, cols: 0, maxX: 0, maxY: 0, keys: false, ptr: 0, idx: !p.noidx, edgeLabels: false }; order.push(p.id); }
          if (p.t === "arr") {
            var n = p.v.length;
            Object.keys(p.ptr || {}).forEach(function (k) {
              n = Math.max(n, +k + 1);
              m.ptr = Math.max(m.ptr, p.ptr[k].length);
            });
            m.n = Math.max(m.n, n);
            if (p.keys) m.keys = true;
          } else if (p.t === "grid") {
            m.rows = Math.max(m.rows, p.v.length);
            m.cols = Math.max(m.cols, p.v[0] ? p.v[0].length : 0);
            (p.rowLabels || []).forEach(function (l) { m.rlw = Math.max(m.rlw || 0, String(l).length); });
          } else {
            p.nodes.forEach(function (nd) { m.maxX = Math.max(m.maxX, nd[2]); m.maxY = Math.max(m.maxY, nd[3]); if (nd[5] && nd[5].length) m.tags = true; });
            p.edges.forEach(function (e) { if (e[3]) m.edgeLabels = true; });
          }
        });
      });
      var y = 8, width = 0;
      order.forEach(function (id) {
        var m = meta[id];
        m.y = y;
        var top = y + LBL;
        if (m.t === "arr") {
          m.perRow = Math.max(1, Math.min(m.n, WRAP));
          m.lines = Math.max(1, Math.ceil(m.n / m.perRow));
          m.rowH = (m.keys ? 16 : 0) + SC + (m.idx && !m.keys ? 14 : 0) + m.ptr * 14 + 8;
          m.w = m.perRow * (SC + SG) - SG;
          m.h = LBL + m.lines * m.rowH;
          m.top = top + (m.keys ? 16 : 0);
        } else if (m.t === "grid") {
          var gc = m.cols > 20 ? 24 : m.cols > 12 || m.rows > 12 ? 28 : 34;
          m.cell = gc;
          m.lw = m.rlw ? 12 + m.rlw * 7.4 : 22;
          m.w = m.lw + m.cols * (gc + 3);
          m.h = LBL + 14 + m.rows * (gc + 3);
          m.top = top + 14;
        } else {
          m.w = m.maxX * U + 2 * R + 4;
          m.h = LBL + m.maxY * U + 2 * R + (m.tags ? 16 : 4) + 6;
          m.top = top + R + 2;
        }
        width = Math.max(width, m.w);
        y += m.h + PGAP;
      });
      width = Math.max(width + 16, 240);
      order.forEach(function (id) { meta[id].x = (width - meta[id].w) / 2; });
      var height = Math.max(y - PGAP + 8, 60);
      bodyEl.classList.toggle("viz-wide", width > 620);     // too wide to sit beside the code: stack them

      stageEl.innerHTML = "";
      var svg = el("svg", { viewBox: "0 0 " + width + " " + height, class: "viz-svg viz-scene",
                            role: "img", "aria-label": "algorithm state" }, stageEl);
      svg.style.maxWidth = Math.min(860, Math.round(width * 1.15)) + "px";
      var defs = el("defs", {}, svg);
      var mid = "vz-sh-" + Math.random().toString(36).slice(2, 9);
      var marker = el("marker", { id: mid, viewBox: "0 0 10 10", refX: "9", refY: "5",
        markerWidth: "5", markerHeight: "5", orient: "auto-start-reverse" }, defs);
      el("path", { d: "M0,0 L10,5 L0,10 z", class: "vz-ehead" }, marker);
      var empty = el("text", { x: width / 2, y: height / 2, "text-anchor": "middle", class: "vz-empty" }, svg);
      scene = { svg: svg, meta: meta, order: order, items: {}, marker: mid, edges: el("g", {}, svg),
                nodes: el("g", {}, svg), empty: empty, width: width };

      codeEl.innerHTML = ch.code.split("\n").map(function (ln, i) {
        return '<span class="vc-line" data-n="' + (i + 1) + '"><span class="vc-n">' + (i + 1) + "</span>" +
               (window.highlight ? window.highlight(ln) : esc(ln)) + "\n</span>";
      }).join("");
    }

    function item(key, make) {
      var it = scene.items[key];
      if (!it) { it = scene.items[key] = make(); it.fresh = true; } else it.fresh = false;
      it.live = true;
      return it;
    }
    function place(node, x, y) { node.style.transform = "translate(" + x + "px," + y + "px)"; }

    function box(parent, key, x, y, size, text, cls, extra) {
      var it = item(key, function () {
        var g = el("g", { class: "vz-cell" }, parent);
        el("rect", { width: size, height: size, rx: 4 }, g);
        var t = el("text", { x: size / 2, y: size / 2 + 1, "text-anchor": "middle", "dominant-baseline": "middle", class: "vz-txt" }, g);
        return { g: g, t: t, v: null };
      });
      if (it.fresh) { it.g.style.transition = "none"; place(it.g, x, y); it.g.getBoundingClientRect(); it.g.style.transition = ""; }
      else place(it.g, x, y);
      it.g.setAttribute("class", "vz-cell vz-s" + (cls ? " " + cls : "") + (extra ? " " + extra : ""));
      if (it.v !== text) {
        var changed = it.v !== null && text !== "";
        it.t.textContent = text;
        it.t.setAttribute("class", "vz-txt" + (cls ? " " + cls : "") + (String(text).length >= 4 ? (String(text).length >= 6 ? " vz-xs" : " vz-sm") : ""));
        if (changed) { it.t.getBoundingClientRect(); it.t.classList.add("vz-changed"); }
        it.v = text;
      } else {
        it.t.setAttribute("class", "vz-txt" + (cls ? " " + cls : "") + (String(text).length >= 4 ? (String(text).length >= 6 ? " vz-xs" : " vz-sm") : ""));
      }
      return it;
    }

    function label(key, x, y, text, cls, anchor) {
      var it = item(key, function () {
        return { t: el("text", { class: cls || "vz-label", "text-anchor": anchor || "start" }, scene.nodes) };
      });
      if (it.fresh) { it.t.style.transition = "none"; place(it.t, x, y); it.t.getBoundingClientRect(); it.t.style.transition = ""; }
      else place(it.t, x, y);
      if (it.t.textContent !== text) it.t.textContent = text;
      return it;
    }

    function drawArr(p, m) {
      for (var i = 0; i < p.v.length; i++) {
        var row = Math.floor(i / m.perRow), col = i % m.perRow;
        var x = m.x + col * (SC + SG), y = m.top + row * m.rowH;
        box(scene.nodes, "a:" + p.id + ":" + i, x, y, SC, p.v[i], p.cls[i]);
        if (p.keys) label("k:" + p.id + ":" + i, x + SC / 2, y - 5, p.keys[i], "vz-index vz-named", "middle");
        else if (m.idx) label("i:" + p.id + ":" + i, x + SC / 2, y + SC + 12, String(i), "vz-index", "middle");
      }
      if (!p.v.length) label("z:" + p.id, m.x + 2, m.top + SC / 2 + 4, "(empty)", "vz-index", "start");
      var below = (m.idx && !p.keys ? 14 : 0);
      Object.keys(p.ptr || {}).forEach(function (k) {
        var i = +k, row = Math.floor(i / m.perRow), col = i % m.perRow;
        if (i >= p.v.length && i > 0 && col === 0 && row > 0 && i === p.v.length) { row -= 1; col = m.perRow; }
        var x = m.x + col * (SC + SG) + SC / 2, y = m.top + row * m.rowH + SC + below + 13;
        p.ptr[k].forEach(function (name, j) {
          label("p:" + p.id + ":" + name, x, y + j * 14, "\u25B2" + name, "vz-ptr", "middle");
        });
      });
    }

    function drawGrid(p, m) {
      var c = m.cell;
      var lw = m.lw;
      for (var r = 0; r < p.v.length; r++) {
        label("gr:" + p.id + ":" + r, m.x + lw - 8, m.top + r * (c + 3) + c / 2 + 4,
              p.rowLabels ? p.rowLabels[r] : String(r), p.rowLabels ? "vz-index vz-named" : "vz-index", "end");
        for (var k = 0; k < p.v[r].length; k++) {
          box(scene.nodes, "g:" + p.id + ":" + r + ":" + k, m.x + lw + k * (c + 3), m.top + r * (c + 3), c, p.v[r][k], p.cls[r][k], "vz-gc");
        }
      }
      for (var k2 = 0; k2 < (p.v[0] || []).length; k2++)
        label("gc:" + p.id + ":" + k2, m.x + lw + k2 * (c + 3) + c / 2, m.top - 4,
              p.colLabels ? p.colLabels[k2] : String(k2), "vz-index", "middle");
    }

    function drawNet(p, m) {
      var pos = {};
      p.nodes.forEach(function (nd) {
        var x = m.x + R + 2 + nd[2] * U, y = m.top + nd[3] * U;
        pos[nd[0]] = [x, y];
        var it = item("n:" + p.id + ":" + nd[0], function () {
          var g = el("g", { class: "vz-node" }, scene.nodes);
          el("circle", { r: R }, g);
          var t = el("text", { "text-anchor": "middle", "dominant-baseline": "middle", y: 1, class: "vz-ntxt" }, g);
          var tag = el("text", { "text-anchor": "middle", y: R + 13, class: "vz-tag" }, g);
          return { g: g, t: t, tag: tag, v: null };
        });
        if (it.fresh) { it.g.style.transition = "none"; place(it.g, x, y); it.g.getBoundingClientRect(); it.g.style.transition = ""; }
        else place(it.g, x, y);
        it.g.setAttribute("class", "vz-node" + (nd[4] ? " " + nd[4] : ""));
        var txt = String(nd[1]);
        if (it.v !== txt) { it.t.textContent = txt; it.v = txt; }
        it.t.setAttribute("class", "vz-ntxt" + (txt.length >= 4 ? " vz-xs" : txt.length >= 3 ? " vz-sm" : ""));
        it.tag.textContent = (nd[5] || []).join(", ");
      });
      p.edges.forEach(function (e) {
        var a = pos[e[0]], b = pos[e[1]];
        if (!a || !b) return;
        var key = "e:" + p.id + ":" + e[0] + ">" + e[1];
        var it = item(key, function () {
          return { path: el("path", { class: "vz-edge" }, scene.edges), lab: el("text", { class: "vz-elabel", "text-anchor": "middle" }, scene.edges) };
        });
        var dx = b[0] - a[0], dy = b[1] - a[1], len = Math.hypot(dx, dy) || 1;
        var curved = e[2] === "alt" || (p.dir && (Math.abs(dy) < 1 && (dx < 0 || dx > U * 2.2)));
        var pad0 = e[2] === "both" ? 2 : 0;
        var x1 = a[0] + dx / len * (R + pad0), y1 = a[1] + dy / len * (R + pad0), x2 = b[0] - dx / len * (R + (p.dir ? 2 : 0)), y2 = b[1] - dy / len * (R + (p.dir ? 2 : 0));
        var d, lx = (x1 + x2) / 2, ly = (y1 + y2) / 2;
        if (curved) {
          var bend = Math.min(60, len * 0.35) * (dx < 0 ? -1 : 1), nx = -dy / len, ny = dx / len;
          var cx = (a[0] + b[0]) / 2 - nx * bend, cy = (a[1] + b[1]) / 2 - ny * bend;
          var s1x = a[0] + (cx - a[0]) / Math.hypot(cx - a[0], cy - a[1]) * R, s1y = a[1] + (cy - a[1]) / Math.hypot(cx - a[0], cy - a[1]) * R;
          var s2x = b[0] + (cx - b[0]) / Math.hypot(cx - b[0], cy - b[1]) * (R + 2), s2y = b[1] + (cy - b[1]) / Math.hypot(cx - b[0], cy - b[1]) * (R + 2);
          d = "M" + s1x + "," + s1y + " Q" + cx + "," + cy + " " + s2x + "," + s2y;
          lx = (s1x + 2 * cx + s2x) / 4; ly = (s1y + 2 * cy + s2y) / 4;
        } else {
          d = "M" + x1 + "," + y1 + " L" + x2 + "," + y2;
        }
        if (!it.fresh && it.d !== d) {             // endpoints moved: fade the edge in once the nodes have slid over
          it.path.classList.remove("vz-moved"); it.lab.classList.remove("vz-moved");
          it.path.getBoundingClientRect();
          it.path.classList.add("vz-moved"); it.lab.classList.add("vz-moved");
        }
        it.d = d;
        it.path.setAttribute("d", d);
        it.path.setAttribute("class", "vz-edge" + (e[2] ? " " + e[2] : "") + (it.path.classList.contains("vz-moved") ? " vz-moved" : ""));
        if (p.dir || e[2] === "alt") it.path.setAttribute("marker-end", "url(#" + scene.marker + ")");
        else it.path.removeAttribute("marker-end");
        if (e[2] === "both") it.path.setAttribute("marker-start", "url(#" + scene.marker + ")");
        else it.path.removeAttribute("marker-start");
        it.lab.textContent = e[3] || "";
        var off = curved ? 0 : 9;                  // beside a straight edge, not on top of it
        it.lab.setAttribute("x", lx + (Math.abs(dy) > Math.abs(dx) ? off : 0));
        it.lab.setAttribute("y", ly - (Math.abs(dy) > Math.abs(dx) ? 0 : 5));
      });
    }

    function showScene(ch, f) {
      for (var k in scene.items) scene.items[k].live = false;
      var present = {};
      (f.panels || []).forEach(function (p) {
        var m = scene.meta[p.id];
        if (!m) return;
        present[p.id] = 1;
        label("L:" + p.id, m.x, m.y + 14, p.label, "vz-label", "start");
        if (p.t === "arr") drawArr(p, m);
        else if (p.t === "grid") drawGrid(p, m);
        else drawNet(p, m);
      });
      for (var key in scene.items) {
        var it = scene.items[key];
        if (it.live) continue;
        (it.g ? [it.g] : it.path ? [it.path, it.lab] : [it.t]).forEach(function (n) { if (n.parentNode) n.parentNode.removeChild(n); });
        delete scene.items[key];
      }
      scene.empty.textContent = (f.panels || []).length ? "" : "no data structures yet";

      var lines = codeEl.querySelectorAll(".vc-line");
      lines.forEach(function (ln) { ln.classList.toggle("on", +ln.dataset.n === f.line); });
      var on = codeEl.querySelector(".vc-line.on");
      if (on) {
        var top = on.offsetTop - codeEl.offsetTop, hgt = codeEl.clientHeight;
        if (top < codeEl.scrollTop + 8 || top > codeEl.scrollTop + hgt - 30) codeEl.scrollTop = Math.max(0, top - hgt / 3);
      }
      varsEl.innerHTML =
        (f.stack && f.stack.length ? '<div class="vv-stack"><span class="vv-h">call stack</span>' +
          f.stack.map(function (s) { return "<code>" + esc(s) + "</code>"; }).join('<span class="vv-sep">&rsaquo;</span>') + "</div>" : "") +
        (f.vars && f.vars.length ? '<div class="vv-list">' + f.vars.map(function (v) {
          return '<span class="vv' + (v[2] ? " on" : "") + '"><b>' + esc(v[0]) + "</b> = " + esc(v[1]) + "</span>";
        }).join("") + "</div>" : "");
      captionEl.innerHTML = f.caption;
      formulaEl.hidden = true;
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
