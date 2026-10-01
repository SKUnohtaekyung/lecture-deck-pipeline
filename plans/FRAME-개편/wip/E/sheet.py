"""메인 점검용 — _main_<ID>.png 여러 장을 한 장으로(2열 · 장당 800px). 사용: sheet.py <out> ID…"""
import sys
from PIL import Image, ImageDraw
out, ids = sys.argv[1], sys.argv[2:]
W, H, C = 800, 450, 2
rows = (len(ids) + C - 1) // C
im = Image.new('RGB', (W * C, H * rows), 'white'); d = ImageDraw.Draw(im)
for n, i in enumerate(ids):
    s = Image.open(f'tmp/frame/E/shots/_main_{i}.png').convert('RGB').resize((W, H), Image.LANCZOS)
    x, y = (n % C) * W, (n // C) * H
    im.paste(s, (x, y)); d.rectangle([x, y, x + W - 1, y + H - 1], outline='#888'); d.text((x + 6, y + 4), i, fill='red')
im.save(out); print('sheet', len(ids))
