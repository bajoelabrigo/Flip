"""Drive Flip Studio's headless MCP stdio bridge from a JSONL call list.

    python mcp_e2e.py --exe <flipstudio.exe> --calls calls.jsonl --out DIR [--project P.drift]

Each line of the call file is {"tool": "...", "args": {...}, "sleep": <seconds>} plus an
optional "save" naming the reply file (defaults to NN_<tool>.json), and an optional
"remember": {"name": "field"} that keeps a field of the reply (place_clip's "id", say) so a later
call can pass it as the string "$name" anywhere in its args. The app is asked to
attach its MCP bridge over stdin/stdout; replies come back as newline-delimited JSON-RPC.

Why this exists: the GUI-less run is the only way to exercise segment_clip and friends
end to end without a window, and the portable GUI build needs DRIFT_*_MODEL_DIR pointing
at the staged extras. See tools/e2e/README.md.
"""

import argparse
import json
import os
import queue
import subprocess
import sys
import threading
import time


def env_with_models(stage):
    """Point every model env var at the staged extras tree."""
    env = dict(os.environ)
    env["DRIFT_AUDIO_EFFECTS_DIR"] = os.path.join(stage, "voces.modificador", "audio-effects")
    env["DRIFT_SAM2_MODEL_DIR"] = os.path.join(stage, "recorte.sujeto", "models", "sam2")
    env["DRIFT_RVM_MODEL_DIR"] = os.path.join(stage, "recorte.personas", "models", "rvm")
    env["DRIFT_FACE_MODEL_DIR"] = os.path.join(stage, "rostro.puntos", "models", "face")
    env["DRIFT_DEPTH_MODEL_DIR"] = os.path.join(stage, "profundidad", "models", "depth")
    env["DRIFT_RESTORE_MODEL_DIR"] = os.path.join(stage, "mejorar.video", "models", "restore")
    env["DRIFT_DENOISE_MODEL_DIR"] = os.path.join(stage, "ruido.voz", "models", "deepfilternet3")
    return env


class Bridge:
    """One long-lived headless instance, with a reader thread draining stdout."""

    def __init__(self, exe, project, out_dir, stage, window=False):
        self.out_dir = out_dir
        os.makedirs(out_dir, exist_ok=True)
        self.stderr_path = os.path.join(out_dir, "stderr.log")
        self._stderr = open(self.stderr_path, "wb")
        # --window: the editor runs with its window (started by main(), the project on its command
        # line) and this bridge attaches to it, so "screenshot" calls see the real UI.
        args = [exe, "--mcp-stdio"] if window else [exe, "--headless", "--mcp-stdio"]
        if project and not window:
            args.append(project)
        self.proc = subprocess.Popen(
            args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=self._stderr,
            env=env_with_models(stage),
            cwd=os.path.dirname(exe),
            bufsize=0,
        )
        self.lines = queue.Queue()
        self._next_id = 0
        self._reader = threading.Thread(target=self._read_stdout, daemon=True)
        self._reader.start()

    def _read_stdout(self):
        for raw in self.proc.stdout:
            self.lines.put(raw)

    def call(self, tool, args, wait=180.0):
        """Send one tools/call and return the parsed reply (or an error dict)."""
        self._next_id += 1
        msg = {
            "jsonrpc": "2.0",
            "id": self._next_id,
            "method": "tools/call",
            "params": {"name": tool, "arguments": args},
        }
        self.proc.stdin.write((json.dumps(msg) + "\n").encode())
        self.proc.stdin.flush()
        deadline = time.time() + wait
        while time.time() < deadline:
            try:
                raw = self.lines.get(timeout=min(5.0, max(0.1, deadline - time.time())))
            except queue.Empty:
                continue
            text = raw.decode("utf-8", "replace").strip()
            if not text:
                continue
            try:
                reply = json.loads(text)
            except json.JSONDecodeError:
                continue
            if reply.get("id") == self._next_id:
                return reply
        return {"error": "timeout waiting for reply", "tool": tool}

    def close(self):
        try:
            self.proc.stdin.close()
        except Exception:
            pass
        try:
            self.proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.proc.kill()
        self._stderr.close()


def reply_text(reply):
    """Flatten the MCP content array into the text payloads it carries."""
    out = []
    for block in reply.get("result", {}).get("content", []) or []:
        if block.get("type") == "text":
            out.append(block.get("text", ""))
    return out


def save_reply(out_dir, name, reply):
    with open(os.path.join(out_dir, name), "w", encoding="utf-8") as fh:
        json.dump(reply, fh, indent=1)
    for text in reply_text(reply):
        print(f"  -> {text[:400]}")


def substitute(value, memory):
    """Replace "$name" strings with what an earlier call remembered."""
    if isinstance(value, str) and value.startswith("$") and value[1:] in memory:
        return memory[value[1:]]
    if isinstance(value, dict):
        return {k: substitute(v, memory) for k, v in value.items()}
    if isinstance(value, list):
        return [substitute(v, memory) for v in value]
    return value


def remember(reply, wanted, memory):
    for text in reply_text(reply):
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            continue
        for name, field in wanted.items():
            if isinstance(data, dict) and field in data:
                memory[name] = data[field]


def screenshot(pid, path):
    """The main window of process pid, drawn by the window itself (PrintWindow), so nothing in
    front of it on the desktop can end up in the picture. Saved as a PNG."""
    import ctypes
    from ctypes import wintypes

    from PIL import Image

    user32 = ctypes.windll.user32
    gdi32 = ctypes.windll.gdi32
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # real pixels, not scaled ones
    except OSError:
        pass
    found = []

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def each(hwnd, _):
        owner = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(owner))
        if owner.value == pid and user32.IsWindowVisible(hwnd) and user32.GetWindowTextLengthW(hwnd) > 0:
            found.append(hwnd)
        return True

    user32.EnumWindows(each, 0)
    if not found:
        return "no window"
    hwnd = found[0]
    user32.ShowWindow(hwnd, 3)  # maximized, but never pulled in front of anything
    time.sleep(1.5)
    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    w, h = rect.right - rect.left, rect.bottom - rect.top
    window_dc = user32.GetWindowDC(hwnd)
    mem_dc = gdi32.CreateCompatibleDC(window_dc)
    bitmap = gdi32.CreateCompatibleBitmap(window_dc, w, h)
    gdi32.SelectObject(mem_dc, bitmap)
    user32.PrintWindow(hwnd, mem_dc, 2)  # PW_RENDERFULLCONTENT: GPU-drawn content too

    class BITMAPINFOHEADER(ctypes.Structure):
        _fields_ = [("biSize", wintypes.DWORD), ("biWidth", wintypes.LONG), ("biHeight", wintypes.LONG),
                    ("biPlanes", wintypes.WORD), ("biBitCount", wintypes.WORD), ("biCompression", wintypes.DWORD),
                    ("biSizeImage", wintypes.DWORD), ("biXPelsPerMeter", wintypes.LONG),
                    ("biYPelsPerMeter", wintypes.LONG), ("biClrUsed", wintypes.DWORD), ("biClrImportant", wintypes.DWORD)]

    info = BITMAPINFOHEADER()
    info.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    info.biWidth, info.biHeight, info.biPlanes, info.biBitCount = w, -h, 1, 32
    buffer = ctypes.create_string_buffer(w * h * 4)
    gdi32.GetDIBits(mem_dc, bitmap, 0, h, buffer, ctypes.byref(info), 0)
    Image.frombuffer("RGBA", (w, h), buffer, "raw", "BGRA", 0, 1).convert("RGB").save(path)
    gdi32.DeleteObject(bitmap)
    gdi32.DeleteDC(mem_dc)
    user32.ReleaseDC(hwnd, window_dc)
    return path


def click(pid, x, y):
    """A left click at (x, y) of the window's own picture (as a screenshot shows it), posted to the
    window as messages: the real mouse never moves and nothing else on the desktop is touched."""
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except OSError:
        pass
    found = []

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def each(hwnd, _):
        owner = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(owner))
        if owner.value == pid and user32.IsWindowVisible(hwnd) and user32.GetWindowTextLengthW(hwnd) > 0:
            found.append(hwnd)
        return True

    user32.EnumWindows(each, 0)
    if not found:
        return "no window"
    hwnd = found[0]
    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    point = wintypes.POINT(rect.left + int(x), rect.top + int(y))
    user32.ScreenToClient(hwnd, ctypes.byref(point))
    lparam = (point.y << 16) | (point.x & 0xFFFF)
    WM_MOUSEMOVE, WM_LBUTTONDOWN, WM_LBUTTONUP, MK_LBUTTON = 0x200, 0x201, 0x202, 1
    user32.PostMessageW(hwnd, WM_MOUSEMOVE, 0, lparam)
    time.sleep(0.05)
    user32.PostMessageW(hwnd, WM_LBUTTONDOWN, MK_LBUTTON, lparam)
    time.sleep(0.08)
    user32.PostMessageW(hwnd, WM_LBUTTONUP, 0, lparam)
    return f"clicked {x},{y}"


def wheel(pid, x, y, notches):
    """Wheel notches (negative: down) at (x, y) of the window, posted like click()."""
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32
    found = []

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def each(hwnd, _):
        owner = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(owner))
        if owner.value == pid and user32.IsWindowVisible(hwnd) and user32.GetWindowTextLengthW(hwnd) > 0:
            found.append(hwnd)
        return True

    user32.EnumWindows(each, 0)
    if not found:
        return "no window"
    hwnd = found[0]
    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    sx, sy = rect.left + int(x), rect.top + int(y)  # WM_MOUSEWHEEL takes screen coordinates
    lparam = ((sy & 0xFFFF) << 16) | (sx & 0xFFFF)
    for _ in range(abs(int(notches))):
        delta = 120 if notches > 0 else -120
        user32.PostMessageW(hwnd, 0x020A, (delta & 0xFFFF) << 16, lparam)
        time.sleep(0.08)
    return f"wheel {notches} at {x},{y}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--calls", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--project", default="")
    ap.add_argument("--stage", default=r"C:\Users\bajoe\Downloads\flip-addons\build\stage")
    ap.add_argument("--wait", type=float, default=180.0)
    ap.add_argument("--window", action="store_true", help="show the window; enables screenshot calls")
    opts = ap.parse_args()

    with open(opts.calls, encoding="utf-8") as fh:
        calls = [json.loads(line) for line in fh if line.strip()]

    gui = None
    if opts.window:
        gui = subprocess.Popen([opts.exe] + ([opts.project] if opts.project else []),
                               env=env_with_models(opts.stage), cwd=os.path.dirname(opts.exe))
        time.sleep(15)
    bridge = Bridge(opts.exe, opts.project, opts.out, opts.stage, window=opts.window)
    memory = {}
    try:
        for index, call in enumerate(calls, start=1):
            tool = call["tool"]
            args = substitute(call.get("args", {}), memory)
            if tool == "click":
                print(f"[{index}] {click(gui.pid if gui else bridge.proc.pid, args['x'], args['y'])}")
                time.sleep(float(call.get("sleep", 1.0)))
                continue
            if tool == "wheel":
                print(f"[{index}] {wheel(gui.pid if gui else bridge.proc.pid, args['x'], args['y'], args['notches'])}")
                time.sleep(float(call.get("sleep", 1.0)))
                continue
            if tool == "screenshot":
                # Not an MCP tool: a picture of the app's window (needs --window).
                path = os.path.join(opts.out, call.get("save") or f"{index:02d}_screenshot.png")
                print(f"[{index}] screenshot -> {screenshot(gui.pid if gui else bridge.proc.pid, path)}")
                if call.get("sleep"):
                    time.sleep(float(call["sleep"]))
                continue
            wait = float(call.get("wait", opts.wait))
            print(f"[{index}] {tool} {json.dumps(args)[:160]}")
            reply = bridge.call(tool, args, wait=wait)
            name = call.get("save") or f"{index:02d}_{tool}.json"
            save_reply(opts.out, name, reply)
            if call.get("remember"):
                remember(reply, call["remember"], memory)
            sleep = call.get("sleep")
            if sleep:
                # Give an async job started by this op time to land before the next call.
                print(f"    sleeping {sleep}s for the async job")
                time.sleep(float(sleep))
    finally:
        bridge.close()
        if gui:
            gui.kill()
    print(f"done; stderr in {bridge.stderr_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
