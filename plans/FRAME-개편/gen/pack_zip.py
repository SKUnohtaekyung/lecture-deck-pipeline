"""D7 패키징 · 안전 점검 — `실습자료_FRAME/`을 `실습자료_FRAME.zip`으로 묶고 zip 안의 파일을 전수 검사한다.
검사: 용량 20MB 이하 · 절대경로 0 · 전화/이메일은 사양의 가상 형식만 · 옛 회사 이름 0 · 제작 흔적(사용자 이름 · 저장소 경로 · 제작일 2026-10) 0
      · 파일 이름 NFC · Windows 금지 문자 0 · zip 항목 시각 2026-03.
종료코드 0 = 전 항목 통과 / 1 = 위반 / 2 = 검사 대상 0(눈먼 0)."""
import io, re, sys, zlib, zipfile, pathlib, unicodedata, getpass, socket
sys.stdout.reconfigure(encoding='utf-8')
R = pathlib.Path(__file__).resolve().parents[3]
S1 = R / 'courses/AI_에이전트_실습워크숍_4시간/sessions/1주차/실습자료'
SRC = S1 / '실습자료_FRAME'
OUT = S1 / '실습자료_FRAME.zip'
STAMP = (2026, 3, 30, 9, 0, 0)

files = sorted(p for p in SRC.rglob('*') if p.is_file())
if not files:
    print('RESULT: 미판정 — 묶을 파일 0개'); sys.exit(2)

buf = io.BytesIO()
with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as z:
    for p in files:
        name = unicodedata.normalize('NFC', '실습자료_FRAME/' + p.relative_to(SRC).as_posix())
        zi = zipfile.ZipInfo(name, STAMP)
        zi.compress_type = zipfile.ZIP_DEFLATED
        zi.external_attr = 0o644 << 16
        zi.create_system = 0
        z.writestr(zi, p.read_bytes())
OUT.write_bytes(buf.getvalue())

TEXT = {'.txt', '.md', '.html', '.css', '.js', '.csv', '.json'}
PHONE_OK = re.compile(r'010-0000-00\d\d')
PHONE_ANY = re.compile(r'(?<![\d-])0\d{1,2}-\d{3,4}-\d{4}(?![\d-])')
MAIL_ANY = re.compile(r'[A-Za-z0-9._+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)+')
BAN = ['가온리빙', getpass.getuser(), socket.gethostname(), 'lecture-deck-pipeline', 'Noh TaeKyung', '2026-10-', 'C:\\Users', '/Users/', 'AppData']
fails, n_text, n_bin = [], 0, 0

def blobs(name, b):
    """이진 파일은 내부 zip(xlsx)과 PDF의 Flate 스트림까지 풀어 본다. 풀지 못한 PDF 스트림 수를 센다."""
    global n_raw
    out = [b]
    if name.endswith('.pdf'):
        for m in re.finditer(rb'stream\r?\n(.*?)\r?\nendstream', b, re.S):
            try: out.append(zlib.decompress(m.group(1)))
            except zlib.error: n_raw += 1
    if name.endswith('.xlsx'):
        with zipfile.ZipFile(io.BytesIO(b)) as x: out += [x.read(i) for i in x.namelist()]
    return out

n_pdf = n_raw = 0
with zipfile.ZipFile(OUT) as z:
    infos = z.infolist()
    for zi in infos:
        nm = zi.filename
        if nm != unicodedata.normalize('NFC', nm): fails.append(f'NFC 아님: {nm}')
        if re.search(r'[\\:*?"<>|]', nm) or nm.startswith('/') or re.match(r'^[A-Za-z]:', nm): fails.append(f'경로 문자: {nm}')
        if zi.date_time[:2] != (2026, 3): fails.append(f'시각: {nm} {zi.date_time}')
        b = z.read(zi)
        ext = pathlib.PurePosixPath(nm).suffix.lower()
        if ext in TEXT:
            n_text += 1
            t = b.decode('utf-8')
            for m in PHONE_ANY.finditer(t):
                if not PHONE_OK.fullmatch(m.group(0)): fails.append(f'전화 형식: {nm} {m.group(0)}')
            for m in MAIL_ANY.finditer(t):
                if not m.group(0).endswith('@example.com') and not re.fullmatch(r'[\w.-]+\.(md|txt|js|css|html)', m.group(0)):
                    fails.append(f'이메일 형식: {nm} {m.group(0)}')
            for w in BAN:
                if w and w in t: fails.append(f'제작 흔적 「{w}」: {nm}')
        else:
            n_bin += 1
            if ext == '.pdf': n_pdf += 1
            for bl in blobs(nm, b):
                for w in BAN:
                    for enc in ('utf-8', 'utf-16-le'):
                        if w and w.encode(enc) in bl: fails.append(f'제작 흔적 「{w}」({enc}): {nm}'); break

size = OUT.stat().st_size
if size > 20 * 1024 * 1024: fails.append(f'용량 {size} > 20MB')
print(f'zip {OUT.name} · 항목 {len(infos)}개 · {size/1024/1024:.2f}MB · 텍스트 {n_text} · 이진 {n_bin}')
print(f'PDF {n_pdf}개는 Flate 스트림을 풀어 판정 · 풀지 못한 스트림 {n_raw}개(미판정)')
for f in fails[:30]: print('  FAIL', f)
print(f'RESULT: {"PASS" if not fails else "FAIL"} · 판정 {len(infos)}개 파일 · 위반 {len(fails)}건 · 미판정 PDF 스트림 {n_raw}개')
sys.exit(1 if fails else 0)
