/* Runs Python in a Web Worker with Pyodide, so a runaway loop can be killed
   by terminating the worker instead of freezing the page. */
importScripts("https://cdn.jsdelivr.net/pyodide/v0.28.3/full/pyodide.js");

var RUNNER = [
  "import sys, io, json, traceback",
  "_buf = io.StringIO()",
  "_saved = sys.stdout, sys.stderr",
  "sys.stdout = sys.stderr = _buf",
  "_ns = {'__name__': '__main__'}",
  "_ok, _stage, _where = True, 'setup', None",
  "try:",
  "    exec(compile(__prelude, 'setup.py', 'exec'), _ns)",
  "    _stage = 'your code'",
  "    exec(compile(__code, 'your_code.py', 'exec'), _ns)",
  "    _stage = 'tests'",
  "    exec(compile(__tests, 'tests.py', 'exec'), _ns)",
  "except BaseException as _e:",
  "    _ok = False",
  "    _tb = traceback.extract_tb(_e.__traceback__)",
  "    _mine = [f for f in _tb if f.filename in ('your_code.py', 'tests.py')]",
  "    if _mine:",
  "        _where = {'file': _mine[-1].filename, 'line': _mine[-1].lineno}",
  "    print(''.join(traceback.format_exception_only(type(_e), _e)).rstrip())",
  "    _src = {'your_code.py': __code, 'tests.py': __tests}",
  "    for _f in _mine[-3:]:",
  "        _lines = _src[_f.filename].split(chr(10))",
  "        _text = _lines[_f.lineno - 1].strip() if 0 < _f.lineno <= len(_lines) else ''",
  "        print(f'  {_f.filename}, line {_f.lineno}: {_text}')",
  "finally:",
  "    sys.stdout, sys.stderr = _saved",
  "json.dumps({'ok': _ok, 'stage': _stage, 'where': _where, 'output': _buf.getvalue()[-8000:]})",
].join("\n");

var ready = loadPyodide().then(function (py) {
  self.postMessage({ type: "ready" });
  return py;
}, function (err) {
  self.postMessage({ type: "error", output: "Could not load Python: " + err });
});

self.onmessage = function (e) {
  ready.then(function (py) {
    try {
      py.globals.set("__prelude", e.data.prelude || "");
      py.globals.set("__code", e.data.code || "");
      py.globals.set("__tests", e.data.tests || "");
      var result = JSON.parse(py.runPython(RUNNER));
      result.type = "result";
      self.postMessage(result);
    } catch (err) {
      self.postMessage({ type: "result", ok: false, stage: "runner", output: String(err) });
    }
  });
};
