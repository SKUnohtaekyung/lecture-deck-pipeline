import re
import sys

def parse_bwonjang(path):
    d = {}
    with open(path, encoding='utf-8') as fh:
        for line in fh:
            parts = [p.strip() for p in line.strip().split('|')]
            if len(parts) < 10:
                continue
            cid = parts[1]
            d[cid] = {
                'yoji': parts[2], 'seong': parts[3], 'daesang_yu': parts[4], 'daesang': parts[5],
                'bandok': parts[6], 'wonchon': parts[7], 'yaksok': parts[8],
                'yusa': parts[9] if len(parts) > 9 else ''
            }
    return d

def parse_c(path):
    d = {}
    order = []
    with open(path, encoding='utf-8') as fh:
        for line in fh:
            parts = [p.strip() for p in line.strip().split('|')]
            if len(parts) < 5:
                continue
            cid = parts[1]
            d[cid] = {'panjeong': parts[2], 'geunge': parts[3], 'bigo': parts[4]}
            order.append(cid)
    return d, order

bw = parse_bwonjang('mia_bwonjang_rows.txt')
cf, order = parse_c('mia_c파일_미반영부분반영.txt')

with open('S1_input_유형분류.md', 'w', encoding='utf-8') as f:
    f.write("# task1 input - 86 rows\n\n")
    f.write("| ID | panjeong | yoji(B) | daesang | bandok | wonchon | yaksok(B) | Cbigo |\n")
    f.write("|---|---|---|---|---|---|---|---|\n")
    for cid in order:
        b = bw.get(cid, {})
        c = cf.get(cid, {})
        f.write("| {} | {} | {} | {} | {} | {} | {} | {} |\n".format(
            cid, c.get('panjeong', '?'), b.get('yoji', '[NOMATCH]'), b.get('daesang', ''),
            b.get('bandok', ''), b.get('wonchon', ''), b.get('yaksok', '-'), c.get('bigo', '')))

n1 = len(order)
n1b = sum(1 for c in order if c in bw)

bw2 = parse_bwonjang('mia_대상소실_bwonjang.txt')
cf2, order2 = parse_c('mia_c파일_대상소실.txt')
with open('S1_input_대상소실.md', 'w', encoding='utf-8') as f:
    f.write("# task2 input - 41 rows\n\n")
    f.write("| ID | yoji(B) | daesang | bandok | wonchon | yaksok(B) | Cbigo |\n")
    f.write("|---|---|---|---|---|---|---|\n")
    for cid in order2:
        b = bw2.get(cid, {})
        c = cf2.get(cid, {})
        f.write("| {} | {} | {} | {} | {} | {} | {} |\n".format(
            cid, b.get('yoji', '[NOMATCH]'), b.get('daesang', ''), b.get('bandok', ''),
            b.get('wonchon', ''), b.get('yaksok', '-'), c.get('bigo', '')))

n2 = len(order2)
n2b = sum(1 for c in order2 if c in bw2)

with open('mia_debug.txt', 'w', encoding='utf-8') as f:
    f.write("{} {} {} {}\n".format(n1, n1b, n2, n2b))
