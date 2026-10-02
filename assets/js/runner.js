/* A tiny client for pyworker.js: lazily start the worker, run code with a
   time limit, restart the worker if it had to be killed. */
(function () {
  "use strict";

  var worker = null, readyPromise = null, pending = null;
  var LIMIT_MS = 12000;

  function start(onStatus) {
    if (worker) return readyPromise;
    worker = new Worker("assets/js/pyworker.js");
    readyPromise = new Promise(function (resolve, reject) {
      worker.onmessage = function (e) {
        var m = e.data;
        if (m.type === "ready") resolve();
        else if (m.type === "error") reject(new Error(m.output));
        else if (m.type === "result" && pending) {
          var p = pending;
          pending = null;
          clearTimeout(p.timer);
          p.resolve(m);
        }
      };
      worker.onerror = function (err) { reject(err); };
    });
    if (onStatus) onStatus("Loading Python in your browser (first run only, ~10 MB)...");
    return readyPromise;
  }

  function kill() {
    if (worker) worker.terminate();
    worker = null;
    readyPromise = null;
  }

  window.pyRunner = {
    run: function (job, onStatus) {
      return start(onStatus).then(function () {
        if (onStatus) onStatus("Running...");
        return new Promise(function (resolve) {
          pending = {
            resolve: resolve,
            timer: setTimeout(function () {
              pending = null;
              kill();                                  // the only way to stop Python
              resolve({ ok: false, stage: "timeout",
                        output: "Stopped after " + LIMIT_MS / 1000 + " s. " +
                                "An infinite loop, or a solution far slower than intended." });
            }, LIMIT_MS),
          };
          worker.postMessage(job);
        });
      });
    },
  };
})();
