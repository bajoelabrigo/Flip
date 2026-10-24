"""Right-click that opens QML menus in a background window: tells the window it is active first
(posted WM_ACTIVATE / WM_SETFOCUS; the real foreground window and the mouse do not change)."""
import ctypes
import sys
import time

sys.path.insert(0, __file__.rsplit("\\", 1)[0].rsplit("/", 1)[0])
import mcp_e2e as m  # noqa: E402


def context_click(pid, x, y):
    user32 = ctypes.windll.user32
    hwnd, lparam = m._window_lparam(pid, 0, 0)
    if not hwnd:
        return "no window"
    user32.PostMessageW(hwnd, 0x0006, 1, 0)  # WM_ACTIVATE (WA_ACTIVE)
    time.sleep(0.2)
    user32.PostMessageW(hwnd, 0x0007, 0, 0)  # WM_SETFOCUS
    time.sleep(0.2)
    point = lparam(x, y)
    user32.PostMessageW(hwnd, 0x0200, 0, point)
    time.sleep(0.3)
    user32.PostMessageW(hwnd, 0x0204, 2, point)
    time.sleep(0.1)
    user32.PostMessageW(hwnd, 0x0205, 0, point)
    return f"context-clicked {x},{y}"


if __name__ == "__main__":
    print(context_click(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])))
