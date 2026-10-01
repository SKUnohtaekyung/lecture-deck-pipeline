import sys, glob
from PIL import Image
pat = sys.argv[1]; out = sys.argv[2]; cols = int(sys.argv[3]) if len(sys.argv) > 3 else 3
files = sorted(glob.glob(pat))
sel = files if len(sys.argv) <= 4 else files[int(sys.argv[4]):int(sys.argv[5])]
W, H = 640, 360
rows = (len(sel) + cols - 1) // cols
im = Image.new('RGB', (W * cols, H * rows), (200, 200, 200))
for i, f in enumerate(sel):
    t = Image.open(f).convert('RGB').resize((W, H)); im.paste(t, ((i % cols) * W, (i // cols) * H))
im.save(out); print(len(sel), 'shots ->', out)
