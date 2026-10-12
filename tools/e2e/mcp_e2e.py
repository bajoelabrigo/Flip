"""Drive Flip Studio's headless MCP stdio bridge from a JSONL call list.

    python mcp_e2e.py --exe <flipstudio.exe> --calls calls.jsonl --out DIR [--project P.drift]

Each line of the call file is {"tool": "...", "args": {...}, "sleep": <seconds>} plus an
optional "save" naming the reply file (defaults to NN_<tool>.json). The app is asked to
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

    def __init__(self, exe, project, out_dir, stage):
        self.out_dir = out_dir
        os.makedirs(out_dir, exist_ok=True)
        self.stderr_path = os.path.join(out_dir, "stderr.log")
        self._stderr = open(self.stderr_path, "wb")
        args = [exe, "--headless", "--mcp-stdio"]
        if project:
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--calls", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--project", default="")
    ap.add_argument("--stage", default=r"C:\Users\bajoe\Downloads\flip-addons\build\stage")
    ap.add_argument("--wait", type=float, default=180.0)
    opts = ap.parse_args()

    with open(opts.calls, encoding="utf-8") as fh:
        calls = [json.loads(line) for line in fh if line.strip()]

    bridge = Bridge(opts.exe, opts.project, opts.out, opts.stage)
    try:
        for index, call in enumerate(calls, start=1):
            tool = call["tool"]
            args = call.get("args", {})
            wait = float(call.get("wait", opts.wait))
            print(f"[{index}] {tool} {json.dumps(args)[:160]}")
            reply = bridge.call(tool, args, wait=wait)
            name = call.get("save") or f"{index:02d}_{tool}.json"
            save_reply(opts.out, name, reply)
            sleep = call.get("sleep")
            if sleep:
                # Give an async job started by this op time to land before the next call.
                print(f"    sleeping {sleep}s for the async job")
                time.sleep(float(sleep))
    finally:
        bridge.close()
    print(f"done; stderr in {bridge.stderr_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
