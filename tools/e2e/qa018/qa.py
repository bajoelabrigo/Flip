"""Control de calidad de la 0.18 (Jorge, 2026-10-18): una sesión sin ventana de la app por MCP, con
ayudantes para llamar herramientas y anotar fallos. Se usa desde los scripts qa_*.py de esta carpeta."""
import json
import os
import sys
import time

sys.path.insert(0, r"C:\Users\bajoe\Downloads\FlipStudio\codigo\Flip\tools\e2e")
import mcp_e2e  # noqa: E402

Q = r"C:\Users\bajoe\Downloads\FlipStudio\pruebas\qa018"
EXE = Q + r"\app\Flip Studio\flipstudio.exe"
STAGE = r"C:\Users\bajoe\Downloads\FlipStudio\codigo\flip-addons\build\stage"
OUT = Q + r"\out"


def parse(reply):
    if "error" in reply and not reply.get("result"):
        return {"ok": False, "rpc_error": reply.get("error")}
    res = reply.get("result", {})
    for c in res.get("content", []):
        if c.get("type") == "text":
            try:
                d = json.loads(c["text"])
            except json.JSONDecodeError:
                d = {"text": c["text"]}
            if res.get("isError"):
                d.setdefault("ok", False)
            return d
    return {"ok": not res.get("isError"), "raw": res}


class Session:
    def __init__(self, name):
        self.name = name
        self.log = []
        self.issues = []
        self.b = mcp_e2e.Bridge(EXE, "", os.path.join(OUT, name), STAGE)

    def raw(self, method, params=None, wait=60):
        self.b._next_id += 1
        msg = {"jsonrpc": "2.0", "id": self.b._next_id, "method": method, "params": params or {}}
        self.b.proc.stdin.write((json.dumps(msg) + "\n").encode())
        self.b.proc.stdin.flush()
        deadline = time.time() + wait
        while time.time() < deadline:
            try:
                raw = self.b.lines.get(timeout=1)
            except Exception:
                continue
            try:
                r = json.loads(raw.decode("utf-8", "replace"))
            except json.JSONDecodeError:
                continue
            if r.get("id") == self.b._next_id:
                return r
        return {"error": "timeout"}

    def call(self, tool, expect_ok=True, note="", wait=180, **args):
        t0 = time.time()
        d = parse(self.b.call(tool, args, wait=wait))
        dt = time.time() - t0
        ok = d.get("ok", True) is not False and "rpc_error" not in d and d.get("error") is None
        self.log.append({"tool": tool, "args": args, "ok": ok, "secs": round(dt, 2), "reply": d})
        if expect_ok and not ok:
            self.issue(f"{tool} falló", args=args, reply=d, note=note)
        return d

    def issue(self, what, **detail):
        self.issues.append({"what": what, **detail})
        print("  !!", what, json.dumps(detail, ensure_ascii=False)[:300], flush=True)

    def notice(self):
        d = self.call("inspect")
        return d.get("notice")

    def close(self):
        os.makedirs(OUT, exist_ok=True)
        with open(os.path.join(OUT, f"{self.name}-log.json"), "w", encoding="utf-8") as f:
            json.dump(self.log, f, ensure_ascii=False, indent=1)
        with open(os.path.join(OUT, f"{self.name}-issues.json"), "w", encoding="utf-8") as f:
            json.dump(self.issues, f, ensure_ascii=False, indent=1)
        self.b.close()
        print(f"[{self.name}] llamadas {len(self.log)}, problemas {len(self.issues)}")
