"""Call FFmpeg's avio_open on a path, using the portable build's own DLLs.

    python avio_probe.py <dir-with-dlls> <output-path>

Reproduces the single call that fails in MatteWriter::open. A negative return here means
libavformat genuinely cannot create the file, with Qt, the sandbox and the app out of the
picture; a zero return means the failure is elsewhere.
"""

import ctypes
import os
import sys


def main():
    dll_dir, out_path = sys.argv[1], sys.argv[2]
    os.add_dll_directory(dll_dir)

    # Load in dependency order so the later ones resolve against the earlier handles.
    libs = {}
    for name in ("avutil-59", "swscale-8", "avcodec-61", "avformat-61"):
        libs[name] = ctypes.CDLL(os.path.join(dll_dir, name + ".dll"))
    avformat = libs["avformat-61"]

    avformat.avformat_alloc_output_context2.argtypes = [
        ctypes.POINTER(ctypes.c_void_p), ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p]
    avformat.avformat_alloc_output_context2.restype = ctypes.c_int
    avformat.avio_open.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.c_char_p, ctypes.c_int]
    avformat.avio_open.restype = ctypes.c_int

    print("libavformat:", libs["avformat-61"]._name)
    for lib, ver in (("avformat-61", "avformat_version"),
                     ("avcodec-61", "avcodec_version"),
                     ("avutil-59", "avutil_version")):
        try:
            fn = getattr(libs[lib], ver)
            fn.restype = ctypes.c_uint
            v = fn()
            print(f"  {ver:18} = {v} ({v >> 16}.{(v >> 8) & 0xFF}.{v & 0xFF})")
        except AttributeError:
            pass

    fmt = ctypes.c_void_p()
    rc = avformat.avformat_alloc_output_context2(ctypes.byref(fmt), None, b"mp4",
                                                 out_path.encode("utf-8"))
    print(f"alloc_output_context2 rc={rc} fmt={'set' if fmt.value else 'NULL'}")
    if rc < 0 or not fmt.value:
        return 1

    pb = ctypes.c_void_p()
    # AVIO_FLAG_WRITE == 2
    rc = avformat.avio_open(ctypes.byref(pb), out_path.encode("utf-8"), 2)
    print(f"avio_open rc={rc}  (negative = the exact MatteWriter failure)")
    if rc < 0:
        print("  -> libavformat could NOT create the file; errno path, not Qt")
        return 1
    print(f"  -> created OK; {out_path} exists={os.path.exists(out_path)}")
    avformat.avio_closep(ctypes.byref(pb))
    try:
        os.remove(out_path)
        print("  cleaned up")
    except OSError as exc:
        print(f"  cleanup failed: {exc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
