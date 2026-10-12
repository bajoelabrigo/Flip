"""Run SAM2 exactly the way Sam2Segmenter does, straight from ONNX Runtime.

    python sam2_probe.py <model-dir> [image.jpg]

Mirrors the app's tensor shapes and normalisation from constants.json so a failure here
means the model export is wrong, and a pass means the bug lives in the C++ orchestration.
"""

import json
import os
import sys

import numpy as np
import onnxruntime as ort


def load_model_dir(root):
    """constants.json plus the five graphs, nested under onnx/ or flat as the app allows."""
    nested = os.path.join(root, "onnx")
    d = nested if os.path.exists(os.path.join(nested, "vision_encoder.onnx")) else root
    with open(os.path.join(root, "constants.json"), encoding="utf-8") as fh:
        const = json.load(fh)
    return d, const


def main():
    root = sys.argv[1]
    img_path = sys.argv[2] if len(sys.argv) > 2 else None
    d, const = load_model_dir(root)

    print(f"model dir : {d}")
    for key in ("model", "image_size", "feat_size", "hidden_dim", "mem_dim", "num_maskmem",
                "max_object_pointers"):
        print(f"  {key:22} = {const.get(key)}")
    print("  image_mean            =", const.get("image_mean"))
    print("  image_std             =", const.get("image_std"))
    files = sorted(f for f in os.listdir(d) if f.endswith(".onnx"))
    print(f"  graphs                = {files}")

    opts = ort.SessionOptions()
    sessions = {}
    for f in files:
        try:
            sessions[f] = ort.InferenceSession(os.path.join(d, f), opts,
                                               providers=["CPUExecutionProvider"])
            print(f"  loaded {f}")
        except Exception as exc:  # noqa: BLE001 - a load failure is the finding
            print(f"  !! could not load {f}: {exc}")
            return 1
    print("all graphs loaded OK")

    for name, sess in sessions.items():
        ins = [(i.name, i.shape, i.type) for i in sess.get_inputs()]
        outs = [(o.name, o.shape) for o in sess.get_outputs()]
        print(f"\n{name}\n  in : {ins}\n  out: {outs}")

    # The vision encoder is the one the app runs first, on every frame.
    size = int(const.get("image_size", 1024))
    mean = np.array(const.get("image_mean", [0.485, 0.456, 0.406]), dtype=np.float32)
    std = np.array(const.get("image_std", [0.229, 0.224, 0.225]), dtype=np.float32)

    if img_path and os.path.exists(img_path):
        from PIL import Image
        img = Image.open(img_path).convert("RGB").resize((size, size))
        arr = np.asarray(img, dtype=np.float32) / 255.0
    else:
        arr = np.random.rand(size, size, 3).astype(np.float32)
    x = ((arr - mean) / std).transpose(2, 0, 1)[None].astype(np.float32)

    vision_file = next((f for f in sessions if "image_encoder" in f or "vision" in f), None)
    if not vision_file:
        print("!! no vision/image_encoder graph found")
        return 1
    sess = sessions[vision_file]
    in_name = sess.get_inputs()[0].name
    print(f"\nrunning {vision_file} with input {in_name} {x.shape} ...")
    try:
        out = sess.run(None, {in_name: x})
    except Exception as exc:  # noqa: BLE001
        print(f"!! vision run failed: {exc}")
        return 1
    for o, val in zip(sess.get_outputs(), out):
        print(f"  -> {o.name}: shape {getattr(val, 'shape', None)} "
              f"finite={np.isfinite(val).all()} "
              f"min={np.nanmin(val):.4f} max={np.nanmax(val):.4f}")
    print("\nvision encoder OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
