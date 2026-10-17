"""One app render (or sample download) at a time across processes.

Several batches can be written in parallel, but the render drives one portable app that writes to the shared
registry key, and the sample download rewrites the shared CREDITS.json: both wait here for their turn.
"""

from __future__ import annotations

import contextlib
import msvcrt
import os
import tempfile
import time
from pathlib import Path

LOCK = Path(tempfile.gettempdir()) / "flip-scene-templates.lock"


@contextlib.contextmanager
def exclusive(what: str):
    handle = open(LOCK, "a+b")
    waited = False
    try:
        while True:
            try:
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                break
            except OSError:
                if not waited:
                    print(f"waiting for another render or download before {what}…", flush=True)
                    waited = True
                time.sleep(5)
        yield
    finally:
        with contextlib.suppress(OSError):
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        handle.close()
