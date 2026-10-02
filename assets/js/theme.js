/* Loaded in <head>, before the stylesheet paints, so the page never flashes
   the wrong theme. A saved choice wins; otherwise follow the OS setting. */
(function () {
  var t = null;
  try { t = localStorage.getItem("grail-theme"); } catch (e) {}
  if (t !== "light" && t !== "dark") {
    t = window.matchMedia && matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
  }
  document.documentElement.setAttribute("data-theme", t);
})();
