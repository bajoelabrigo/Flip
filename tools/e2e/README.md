# End-to-end tests without a window

`flipstudio.exe --headless --mcp-stdio` speaks newline-delimited JSON-RPC on stdin/stdout with no
GUI. That is how the desktop app is exercised end to end: build the project, drive the MCP tools,
read the replies. Nothing here needs a display, and a run is reproducible from a call list.

## `mcp_e2e.py`

Runs a JSONL call list against a built executable and writes every reply to a directory.

```powershell
python tools/e2e/mcp_e2e.py `
  --exe "C:\Users\bajoe\Downloads\FlipStudio\pruebas\FlipStudio-0.9.2-prueba\app\Flip Studio\flipstudio.exe" `
  --calls tools/e2e/calls_sam2.jsonl `
  --out   tools/e2e/run_sam2
```

Each line is one tool call:

```json
{"tool": "place_clip", "args": {"asset": 0, "at": 0}}
{"tool": "segment_clip", "args": {"track": 0, "index": 0, "backend": "sam2",
                                  "points": [{"x": 0.6, "y": 0.35, "include": true}]},
 "sleep": 150}
```

- `sleep` waits after the call, which is how an async job (segmentation, export, subtitles) is given
  time to land before the next call inspects the result.
- `wait` overrides the per-call reply timeout (default 180 s).
- `save` renames the reply file; the default is `NN_<tool>.json`.
- `--project` opens a `.drift` file first.
- `--stage` points at the staged extras tree whose model directories get exported as `DRIFT_*_MODEL_DIR`
  (default `C:\Users\bajoe\Downloads\FlipStudio\codigo\flip-addons\build\stage`). The video and audio models are
  addons and are not inside the portable build, so without this the AI tools report themselves
  unavailable.

The app writes its banner and any Qt warnings to `stderr.log` in the output directory.

## `sam2_full.py`

Reproduces SAM2's whole pipeline in ONNX Runtime, without the app: vision encode, memory encoder,
the 28736-token memory layout, memory attention, mask decoder and a propagation step.

```powershell
python tools/e2e/sam2_full.py <model-dir> <image.jpg> [steps]
```

Use it to tell a bad model export from a bad C++ orchestration. If this prints sane masks
(`iou` near 0.95, a foreground fraction that matches the subject) then the graphs are fine and the
bug is in the app. It needs `onnxruntime`, `numpy` and `Pillow`; the `flip-addons` virtualenv has
them:

```powershell
C:\Users\bajoe\Downloads\FlipStudio\codigo\flip-addons\work\tts\.venv\Scripts\python.exe tools\e2e\sam2_full.py ...
```

## `sam2_probe.py`

Lighter check: loads the five graphs, prints their input/output signatures, and runs the vision
encoder once. Good for confirming a model directory is complete and correctly shaped.

## Driving the real window

`mcp_e2e.py --window` shows the editor and attaches to it; `--keep` leaves it open and
`--attach <pid>` drives it afterwards. Two helpers do the same by hand, without moving the real
mouse (they post window messages, like the harness does):

```powershell
# a picture of the app's window (PrintWindow: only that window, never the desktop)
.\tools\e2e\shot.ps1 -TargetPid 1234 -OutFile "$env:TEMP\shot.png"
# a click at a coordinate of that picture (frame included)
.\tools\e2e\click.ps1 -TargetPid 1234 -X 975 -Y 120
```

- **`--headless` has no account session.** `AccountController` loads the stored session in the
  windowed editor, so every `market_*` op comes back `authenticated:false` and the service answers
  401 (`Inicia sesión con Google…`) when the harness runs headless. Stock tests need `--window` (or
  `--attach` to an open editor).
- **`mcp/startOnLaunch` = true is what lets an agent attach.** Turn it on with a copy of the registry
  and put the copy back afterwards (CLAUDE.md); if the app used the account, export
  `HKCU\Software\Flip Studio\Flip Studio\account` *after* the run and import it back last, or the
  rotated refresh token is lost.
- `calls_stock014.jsonl` installs one item of each kind Stock serves (LUT, look, text style, text
  animation, transition, shape, music, template) and can be run against an attached editor.

## Notes

- A reply is the MCP envelope, not the answer: the payload is JSON text inside
  `result.content[0].text`.
- A fire-and-forget op returns `ok` as soon as the job starts, so `ok:true` is not success. Poll
  `inspect` and compare, and read `notice` when nothing changed.
- The portable build reports itself as version `0.0.0`, so packages that require 0.9.2 refuse to
  install from Extras. Everything else in the app is testable as normal.
- **Run the harness unsandboxed.** Anything that writes a sidecar fails with
  `Permission denied, error -13` from `avio_open` when the app runs under a file sandbox, because
  the sidecars go to `%APPDATA%\Flip Studio\Flip Studio\` (`mattes`, `facetracks`, `reversed`).
  A denied write there does not mean the feature is broken: check that a plain write to that
  directory succeeds before reading anything into the failure. The same applies to
  `testmatte.mp4`-style probes run outside the app.
- Setting `APPDATA` does not relocate it: Windows resolves the known folder through the shell API,
  not that variable, so the app keeps using the real one.
- Model directories: the six video model packages (`recorte.sujeto`, `recorte.personas`,
  `rostro.puntos`, `profundidad`, `mejorar.video`, `ruido.voz`) are extracted under
  `flip-addons/build/stage` and exposed through `--stage`. Without them the AI tools report
  themselves unavailable and every cutout op fails early.
