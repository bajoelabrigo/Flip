"""compare.py <template folder> <ref video> <ref start (abs s of u=0)> <dur> <out.png> : the reference over ours, 10 fps
for the entrance and the exit, both at 640×360."""
import subprocess, sys
from PIL import Image, ImageDraw
folder, video, start, dur, out = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
def grab(path, t):
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", path, "-frames:v", "1", "-vf", "scale=640:360",
                        "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True)
    return Image.frombytes("RGB", (640, 360), r.stdout) if len(r.stdout) == 640 * 360 * 3 else Image.new("RGB", (640, 360))
times = [i / 10 for i in range(0, 16)] + [dur - 1.2 + i / 10 for i in range(0, 13)]
cols = 6
rows = (len(times) + cols - 1) // cols
img = Image.new("RGB", (cols * 320, rows * 360), "black")
d = ImageDraw.Draw(img)
for k, u in enumerate(times):
    a = grab(video, start + u).resize((320, 180)); b = grab(folder + "/preview-wide.mp4", u).resize((320, 180))
    x, y = (k % cols) * 320, (k // cols) * 360
    img.paste(a, (x, y)); img.paste(b, (x, y + 180)); d.text((x + 3, y + 3), f"{u:.1f}", fill="yellow")
img.save(out)
