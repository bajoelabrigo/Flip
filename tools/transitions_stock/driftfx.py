"""Writes and checks .driftfx user packages, byte for byte the way the app's writeUserPackage does
(src/engine/AddonPackage.cpp): "DRIFTFX\\0", format 1, compact JSON metadata, zstd payload of the
files in path order, then the SHA-256 of everything before it. AddonManager::inspectUserPackage /
installUserPackage install it into <AppData>/<kind>/<folder>.
"""

from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path

import zstandard

MAGIC = b"DRIFTFX\0"
VERSION = 1


def write(package_dir: Path, kind: str, meta: dict, out: Path) -> None:
    folder = package_dir.name
    rels = sorted(p.relative_to(package_dir).as_posix() for p in package_dir.rglob("*") if p.is_file())
    payload = bytearray()
    files = []
    for rel in rels:
        data = (package_dir / rel).read_bytes()
        files.append({"path": f"{kind}/{folder}/{rel}", "offset": len(payload), "size": len(data),
                      "sha256": hashlib.sha256(data).hexdigest()})
        payload += data
    root = dict(meta)
    root.update({"schema": 1, "platform": "", "installedSize": len(payload), "files": files,
                 "provides": [{"kind": kind, "root": kind, "items": 1}]})
    metadata = json.dumps(root, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    compressed = zstandard.ZstdCompressor(level=19).compress(bytes(payload))
    body = MAGIC + struct.pack("<II", VERSION, len(metadata)) + metadata
    body += struct.pack("<QQ", len(compressed), len(payload)) + compressed
    out.write_bytes(body + hashlib.sha256(body).digest())


def check(path: Path) -> dict:
    """Reads a .driftfx back like the installer: magic, digest, single folder, per-file hashes."""
    raw = path.read_bytes()
    assert raw[:8] == MAGIC, "bad magic"
    version, mlen = struct.unpack("<II", raw[8:16])
    assert version == VERSION
    meta = json.loads(raw[16:16 + mlen])
    pos = 16 + mlen
    clen, rlen = struct.unpack("<QQ", raw[pos:pos + 16])
    pos += 16
    assert pos + clen + 32 == len(raw), "truncated or trailing bytes"
    assert hashlib.sha256(raw[:pos + clen]).digest() == raw[pos + clen:], "digest mismatch"
    data = zstandard.ZstdDecompressor().decompress(raw[pos:pos + clen], max_output_size=rlen)
    assert len(data) == rlen
    assert len(meta["provides"]) == 1
    kind = meta["provides"][0]["kind"]
    folders = set()
    offset = 0
    for f in meta["files"]:
        assert f["offset"] == offset
        chunk = data[offset:offset + f["size"]]
        assert hashlib.sha256(chunk).hexdigest() == f["sha256"], f["path"]
        offset += f["size"]
        rest = f["path"][len(kind) + 1:]
        folders.add(rest.split("/")[0])
    assert len(folders) == 1, "a user package must contain a single folder"
    return meta
