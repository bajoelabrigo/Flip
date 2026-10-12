"""Run SAM2's real seeding + propagation path the way Sam2Segmenter does, in ONNX Runtime.

    python sam2_full.py <model-dir> <image.jpg> [frames]

Mirrors the C++ orchestration exactly:
  seed : vision -> mask_decoder(prompt, feats2_no_mem) -> memory_encoder(binarize=1)
  step : build_memory(28736 tokens) -> memory_attention -> mask_decoder(label -1)
         -> memory_encoder(binarize=0)

If this produces sane masks, the ONNX export is sound and the bug is in the C++
orchestration. Serialised as newline JSON so a run can be diffed.
"""

import json
import os
import sys
import time

import numpy as np
import onnxruntime as ort

K_IMG = 64 * 64
K_HID = 256
K_MEM = 64
K_MASKMEM = 7
K_MAXPTR = 16
K_PTR_TOKENS = K_MAXPTR * (K_HID // K_MEM)          # 64
K_MEM_TOKENS = K_MASKMEM * K_IMG + K_PTR_TOKENS     # 28736


def nchw_to_tokens(arr):
    """Mirror Sam2Segmenter's toTokens: NCHW float vector -> [4096, 256]."""
    return arr.reshape(K_HID, K_IMG).T.copy()


def build_memory(cond_tokens, cond_pos, recent_tokens, recent_pos, temporal_pe):
    """Port of State::buildMemory for the no-pointer case the app hits on frame 1."""
    mem = np.zeros((K_MEM_TOKENS, K_MEM), dtype=np.float32)
    mem_pos = np.zeros((K_MEM_TOKENS, K_MEM), dtype=np.float32)

    # The memory encoder already returns [4096, 64] tokens, which is the slot layout.
    def write_block(slot, tokens, pos, pe_row):
        base = slot * K_IMG
        mem[base:base + K_IMG] = tokens.reshape(K_IMG, K_MEM)
        mem_pos[base:base + K_IMG] = pos.reshape(K_IMG, K_MEM) + temporal_pe[pe_row][None, :]

    write_block(0, cond_tokens, cond_pos, K_MASKMEM - 1)
    for slot in range(1, K_MASKMEM):
        back = min(slot - 1, len(recent_tokens) - 1)
        if back < 0:
            write_block(slot, cond_tokens, cond_pos, K_MASKMEM - 1)
            continue
        idx = len(recent_tokens) - 1 - back
        write_block(slot, recent_tokens[idx], recent_pos[idx], slot - 1)
    return mem, mem_pos


def main():
    root, img_path = sys.argv[1], sys.argv[2]
    n_steps = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    nested = os.path.join(root, "onnx")
    d = nested if os.path.exists(os.path.join(nested, "vision_encoder.onnx")) else root
    with open(os.path.join(root, "constants.json"), encoding="utf-8") as fh:
        const = json.load(fh)

    size = int(const["image_size"])
    mean = np.array(const["image_mean"], dtype=np.float32)
    std = np.array(const["image_std"], dtype=np.float32)
    temporal_pe = np.array(const["memory_temporal_positional_encoding"], dtype=np.float32)

    print(f"loading sessions from {d} ...", flush=True)
    opts = ort.SessionOptions()
    s = {name: ort.InferenceSession(os.path.join(d, f"{name}.onnx"), opts,
                                    providers=["CPUExecutionProvider"])
         for name in ("vision_encoder", "memory_attention", "mask_decoder",
                      "memory_encoder", "pointer_tpos")}
    print("  loaded", flush=True)

    from PIL import Image
    img = Image.open(img_path).convert("RGB").resize((size, size))
    arr = np.asarray(img, dtype=np.float32) / 255.0
    x = ((arr - mean) / std).transpose(2, 0, 1)[None].astype(np.float32)

    t0 = time.time()
    outs = s["vision_encoder"].run(None, {"pixel_values": x})
    f = dict(zip([o.name for o in s["vision_encoder"].get_outputs()], outs))
    print(f"vision encode {time.time() - t0:.1f}s", flush=True)

    feats0 = f["feats0"]
    feats1 = f["feats1"]
    feats2 = f["feats2"]
    feats2_no_mem = f["feats2_no_mem"]
    cond_tokens = nchw_to_tokens(feats2_no_mem[0])
    cond_pos = nchw_to_tokens(f["vision_pos_embed"][0])

    px, py = 0.6 * size, 0.35 * size
    pts = np.array([[[[px, py]]]], dtype=np.float32)
    labels = np.array([[[1]]], dtype=np.int32)

    t0 = time.time()
    dec = dict(zip([o.name for o in s["mask_decoder"].get_outputs()],
                   s["mask_decoder"].run(None, {"feats0": feats0, "feats1": feats1,
                                                "feats2_cond": feats2_no_mem,
                                                "input_points": pts, "input_labels": labels})))
    high = dec["high_res_mask"]
    frac = float((high > 0).mean())
    print(f"seed decoder {time.time() - t0:.1f}s  iou={np.ravel(dec['iou'])}  "
          f"fg={frac:.4f}", flush=True)

    memenc = dict(zip([o.name for o in s["memory_encoder"].get_outputs()],
                      s["memory_encoder"].run(None, {
                          "feats2": feats2, "high_res_mask": high,
                          "object_score_logits": np.array([[float(np.ravel(dec['object_score_logits'])[0])]], dtype=np.float32),
                          "binarize": np.array(1.0, dtype=np.float32)})))
    cond_tokens = memenc["memory_tokens"].reshape(K_IMG, K_MEM)
    cond_pos = memenc["memory_pos"].reshape(K_IMG, K_MEM)
    pointer = dec["object_pointer"].reshape(-1)
    print(f"  memory_encoder -> tokens {cond_tokens.shape} pointer {pointer.shape}", flush=True)

    recent_t, recent_p = [], []
    for step in range(n_steps):
        mem, mem_pos = build_memory(cond_tokens, cond_pos, recent_t, recent_p, temporal_pe)
        t0 = time.time()
        conditioned = s["memory_attention"].run(None, {
            "current_vision_features": nchw_to_tokens(feats2)[:, None, :].astype(np.float32),
            "current_vision_position_embeddings": nchw_to_tokens(f["vision_pos_embed"][0])[:, None, :].astype(np.float32),
            "memory": mem[:, None, :], "memory_pos": mem_pos[:, None, :]})[0]
        t_attn = time.time() - t0

        t0 = time.time()
        dec = dict(zip([o.name for o in s["mask_decoder"].get_outputs()],
                       s["mask_decoder"].run(None, {
                           "feats0": feats0, "feats1": feats1, "feats2_cond": conditioned,
                           "input_points": np.array([[[[0.0, 0.0]]]], dtype=np.float32),
                           "input_labels": np.array([[[-1]]], dtype=np.int32)})))
        high = dec["high_res_mask"]
        frac = float((high > 0).mean())
        print(f"step {step + 1}: attention {t_attn:.1f}s decoder {time.time() - t0:.1f}s "
              f"iou={np.ravel(dec['iou'])} fg={frac:.4f}", flush=True)

        memenc = dict(zip([o.name for o in s["memory_encoder"].get_outputs()],
                          s["memory_encoder"].run(None, {
                              "feats2": feats2, "high_res_mask": high,
                              "object_score_logits": np.array([[float(np.ravel(dec['object_score_logits'])[0])]], dtype=np.float32),
                              "binarize": np.array(0.0, dtype=np.float32)})))
        recent_t.append(memenc["memory_tokens"].reshape(K_IMG, K_MEM))
        recent_p.append(memenc["memory_pos"].reshape(K_IMG, K_MEM))

    print(json.dumps({"ok": True, "steps": n_steps, "lastFg": frac}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
