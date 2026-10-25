# -*- coding: utf-8 -*-
"""「여행 앱」 4시간 트랙(2판)의 준비물 폴더를 만든다 (설계 plans/FRAME-실습강화/P5-설계.md §10).

2판에는 완성 도구 HTML이 없다. 학생이 prd.md · design.md를 정하고 에이전트가 index.html을 처음부터 만든다.
이 스크립트는 폴더 `실습자료/여행앱_4시간/`에 아래를 둔다.

  관광지.js                         이 스크립트가 만든다 — window.관광지 = { 만든날, 출처, 지역: [ { 이름, 위도, 경도, 장소: [ … ] } ] };
  AGENTS.md · prd.md · 자료설명.md   templates/app_text_v2/ 에서 복사한다(없으면 「없음」을 찍고 계속)
  (같은 이름의 zip)                 실습자료/여행앱_4시간.zip

1판 파일(여행도구.html · 계획.js · 확장.js · 오프라인응답/ · API이름표 · 화면이름표 · 품질기준)은 만들지도 복사하지도 않는다.
1판 템플릿(app.html · app_text/)은 _archive/실습_1판_2026-10-21/templates/로 옮겼다. 폴더를 지우지 않는다(다른 도구가 같은 폴더에 쓴다).

자료 원천
  --source osm      (기본 · 키 없음 · 시제품) Overpass API. 각 지역 반경 15 km 안의 관광 · 역사 요소 가운데 이름이 있는 것.
                    주소는 addr:* 태그가 있을 때만 이어 붙이고 없으면 빈 값. 사진은 없음. 설명은 description:ko만(없으면 빈 값). 지어 쓰지 않는다.
  --source tourapi  환경변수 TOURAPI_KEY가 있어야 한다. 한국관광공사 TourAPI locationBasedList2(관광지 12 · 문화시설 14).
                    키는 어떤 파일에도 쓰지 않고 화면 출력 · 오류 글에서도 가린다.

실패하면(호출 오류 · 지역별 10~12곳 조건 · 이름 비어 있음 · 이름 중복 · 중심에서 15 km 밖) 직전 관광지.js를 그대로 두고 경고를 찍고 종료코드 2.
검증(node --check · 1판 파일 잔존 · 키 문자열)에서 걸리면 종료코드 1.

실행:  python -I gen_app.py                      (OSM · 시제품)
       python -I gen_app.py --texts-only         (관광지.js는 그대로 두고 문서 복사 · 검증 · zip만 다시 한다 · 네트워크 없음)
       python -I gen_app.py --source tourapi     (TOURAPI_KEY 필요)
       python -I gen_app.py --verify-centers     (중심 좌표를 Nominatim으로 대조해 찍기만 한다 · 바꾸지 않는다)
       python -I gen_app.py --cache DIR          (Overpass 원응답을 DIR에 저장하고, 있으면 다시 부르지 않는다 · 개발용)
"""
import argparse
import datetime
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
INST = os.path.dirname(HERE)                                  # 실습자료_강사용
BASE = os.path.join(os.path.dirname(INST), '실습자료')          # 실습자료
TPL = os.path.join(HERE, 'templates')
TEXT_V2 = os.path.join(TPL, 'app_text_v2')
TRACK = os.path.join(BASE, '여행앱_4시간')
DATA = os.path.join(TRACK, '관광지.js')
ZIP = TRACK + '.zip'

TEXTS = ('AGENTS.md', 'prd.md', '자료설명.md')   # app_text_v2 → 트랙 폴더, 같은 이름. 규칙 파일은 AGENTS.md 하나다
LIMITS = {'AGENTS.md': 8 * 1024, 'prd.md': 3 * 1024, '자료설명.md': 3 * 1024}   # 크기 상한(2026-10-21 갱신: 자료설명.md 3,072 B)
TOTAL_LIMIT = 13000                                           # AGENTS.md + prd.md + 자료설명.md 합계(관광지.js 제외) — 파일 바이트(CRLF 포함)
V1_NAMES = ('여행도구.html', '계획.js', '확장.js', '오프라인응답', 'API이름표.md', '화면이름표.md', '품질기준.md')

UA = 'FRAME-workshop-generator/1.0 (lecture materials)'
OVERPASS = 'https://overpass-api.de/api/interpreter'
OVERPASS_GAP = 2.5                                            # 요청 사이 최소 간격(초) — 2초 이상
NOMINATIM_GAP = 1.1
NOMINATIM_Q = {'강릉': '강릉시', '경주': '경주시', '전주': '전주시', '제주': '제주시'}   # 시 단위로 물어야 시청 근처가 나온다(부산은 광역시 그대로)
TOUR = 'https://apis.data.go.kr/B551011/KorService2/'
RADIUS_M = 15000
PER_MIN, PER_MAX = 10, 12                                     # 지역마다 장소 수

REGIONS = (                                                   # 이름, 위도, 경도
    ('강릉', 37.7519, 128.8761),
    ('경주', 35.8562, 129.2247),
    ('전주', 35.8242, 127.1480),
    ('부산', 35.1796, 129.0756),
    ('제주', 33.4996, 126.5312),
)

SRC_TEXT = {'osm': 'OpenStreetMap 기여자(ODbL) · 시제품 자료', 'tourapi': '한국관광공사 TourAPI 4.0'}

# ---- OSM 선택 규칙
TOURISM = ('attraction', 'museum', 'gallery', 'viewpoint', 'zoo', 'aquarium', 'theme_park')
HISTORIC = ('castle', 'monument', 'archaeological_site')
CAT_TOURISM = {'museum': '박물관', 'gallery': '미술관', 'viewpoint': '전망', 'zoo': '동물원',
               'aquarium': '수족관', 'theme_park': '테마공원', 'attraction': '관광지'}
INDOOR_CATS = ('박물관', '미술관', '수족관')                    # 실내 = 박물관 · 미술관 · 수족관
RIDE_VALUES = ('carousel', 'roller_coaster', 'water_slide', 'swing', 'bumper_car', 'drop_tower', 'pirate_ship',
               'kiddie_ride', 'log_flume', 'river_rafting', 'dark_ride', 'maze', 'train', 'big_wheel',
               'hedge_maze', 'summer_toboggan', 'water_park')  # 놀이기구 한 대는 장소가 아니다
SKIP_WORDS = ('주차장', '화장실', '안내소', '안내판', '매표소', '정류장', '입구', '표지석', '표지판', '쉼터',
              '사거리', '삼거리', '교차로', '본점', '지점', '식당', '쇼쿠도', '횟집', '의원', '병원', '카페')   # 장소가 아닌 이름
SKIP_AMENITY = ('restaurant', 'cafe', 'fast_food', 'bar', 'pub', 'food_court', 'bank', 'clinic', 'hospital',
                'pharmacy', 'parking', 'toilets', 'school', 'kindergarten', 'fuel')           # 관광 태그가 겹쳐 붙은 가게 · 시설
SKIP_KEYS = ('shop', 'cuisine', 'highway', 'railway', 'public_transport')
# 수업용 제외 이름(2026-10-21 메인 지시) — 이름 안에 이 글이 들어 있으면(공백 무시) 후보에서 뺀다. 빈자리는 다음 점수 항목이 채운다.
EXCLUDE_NAMES = (
    '위안부 평화비',   # 추모 시설이라 여행 일정에 넣을 재료로 맞지 않는다
    '제주러브랜드',    # 성인 대상 시설이라 수업 자료로 맞지 않는다
)
# 태그로 거르는 것 — memorial 계열(추모비 · 기념 동상 · 위령 시설)과 성인 대상 표시
ADULT_AMENITY = ('brothel', 'stripclub', 'love_hotel', 'swingerclub')
SKIP_WORDS_ADULT = ('성인', '러브랜드')
MIN_SEP_KM = 0.10                                             # 같은 곳의 다른 이름(건물 · 부속 시설)을 걸러 내는 최소 간격
CAT_CAP = 4                                                   # 분류 하나가 차지할 수 있는 칸(전망이 몰리는 것을 막는다)
INDOOR_CAP = 5
HANGUL = re.compile(r'[가-힣]')


# ---------------------------------------------------------------- 공통
def out(msg=''):
    print(msg, flush=True)


def norm(s):
    return re.sub(r'\s+', ' ', (s or '')).strip()


def name_key(s):
    return re.sub(r'[\s\-·・()（）]+', '', s).lower()


def series_key(s):
    """이름에서 번호(1호 · 3호,4호 · 제2관 …)만 지운 키 — 번호만 다른 이름은 같은 키가 된다."""
    k = name_key(s)
    k = re.sub(r'제?\d+(?:[.,~]\d+)*(?:호|번|차|기|관|동|층|단지|지구)?', '', k)
    k = k.strip(',.~')
    return k or name_key(s)


def is_excluded_by_tags(t):
    """memorial 계열 · 성인 대상 태그."""
    if t.get('historic') == 'memorial' or any(k == 'memorial' or k.startswith('memorial:') for k in t):
        return True
    if any(k == 'adult' or k.startswith('adult:') for k in t) and t.get('adult') != 'no':
        return True
    if t.get('amenity') in ADULT_AMENITY or t.get('shop') == 'erotic' or t.get('leisure') == 'adult_gaming_centre':
        return True
    m = re.match(r'\d+', str(t.get('min_age', '')))
    return bool(m and int(m.group(0)) >= 18)


def haversine_km(a, b):
    r, rad = 6371.0, math.pi / 180
    dlat, dlon = (b[0] - a[0]) * rad, (b[1] - a[1]) * rad
    x = math.sin(dlat / 2) ** 2 + math.cos(a[0] * rad) * math.cos(b[0] * rad) * math.sin(dlon / 2) ** 2
    return 2 * r * math.asin(min(1.0, math.sqrt(x)))


def key_value(k):
    """키에 %가 없고 + / =가 있으면(Decoding 키) 인코딩한다. Encoding 키는 그대로."""
    k = (k or '').strip()
    if not k:
        return ''
    if '%' not in k and re.search(r'[+/=]', k):
        return urllib.parse.quote(k, safe='')
    return k


def scrub(text, key):
    """오류 글에서 키(원형 · 인코딩형)를 가린다."""
    text = str(text)
    for v in {key, key_value(key), urllib.parse.quote(key, safe='') if key else ''}:
        if v:
            text = text.replace(v, '●●●●')
    return text


def http_get(url, timeout=30):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode('utf-8')


def render(data):
    s = json.dumps(data, ensure_ascii=False, indent=2)
    s = s.replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
    return 'window.관광지 = ' + s + ';\n'


# ---------------------------------------------------------------- OSM (Overpass)
_last_overpass = [0.0]


def overpass(query):
    last = None
    for attempt in range(4):
        wait = OVERPASS_GAP - (time.time() - _last_overpass[0])
        if wait > 0:
            time.sleep(wait)
        _last_overpass[0] = time.time()
        try:
            body = urllib.parse.urlencode({'data': query}).encode('utf-8')
            req = urllib.request.Request(OVERPASS, data=body, headers={
                'User-Agent': UA, 'Accept': 'application/json',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'})
            with urllib.request.urlopen(req, timeout=120) as r:
                data = json.loads(r.read().decode('utf-8'))
            remark = str(data.get('remark', ''))
            if 'error' in remark.lower():
                raise ValueError('Overpass 알림: ' + remark[:120])
            if not isinstance(data.get('elements'), list):
                raise ValueError('응답에 elements가 없음')
            return data
        except urllib.error.HTTPError as e:
            last = e
            if e.code not in (429, 502, 503, 504):
                break
        except (urllib.error.URLError, TimeoutError, ValueError) as e:
            last = e
        out('    Overpass 재시도 %d/3 — %s' % (attempt + 1, last))
        time.sleep(10 * (attempt + 1))
    raise RuntimeError('Overpass 호출 실패: %s' % last)


def osm_query(lat, lon):
    around = 'around:%d,%s,%s' % (RADIUS_M, lat, lon)
    return ('[out:json][timeout:90];\n(\n'
            '  nwr(%s)["tourism"~"^(%s)$"]["name"];\n'
            '  nwr(%s)["historic"~"^(%s)$"]["name"];\n'
            ');\nout center tags;' % (around, '|'.join(TOURISM), around, '|'.join(HISTORIC)))


def clean_name(n):
    """OSM 이름 정리 — 「A;B」는 한글이 든 쪽 하나, 「한글 - English」는 한글 쪽만."""
    n = norm(n)
    if ';' in n:
        segs = [norm(x) for x in n.split(';') if norm(x)]
        n = next((x for x in segs if HANGUL.search(x)), segs[0] if segs else '')
    m = re.match(r'^(.*?)\s+[-–]\s+(.*)$', n)
    if m and HANGUL.search(m.group(1)) and not HANGUL.search(m.group(2)):
        n = norm(m.group(1))
    return n


def osm_addr(t):
    """addr:* 태그를 이어 붙인다. 번지수만 있거나 한글이 한 글자도 없는(영문 표기만 있는) 것은 주소로 치지 않는다. 없으면 빈 값."""
    a = _osm_addr_raw(t)
    return a if HANGUL.search(a) else ''


def _osm_addr_raw(t):
    if norm(t.get('addr:full')):
        return norm(t['addr:full'])
    keys = ('addr:province', 'addr:city', 'addr:district', 'addr:subdistrict', 'addr:suburb',
            'addr:neighbourhood', 'addr:place', 'addr:street', 'addr:housenumber')
    parts = []
    for k in keys:
        v = norm(t.get(k))
        if v and v not in parts:
            parts.append(v)
    if not [p for p in parts if p != norm(t.get('addr:housenumber'))]:
        return ''
    return ' '.join(parts)


def osm_category(t, name=''):
    tour = t.get('tourism')
    if tour == 'museum' and re.search(r'미술관|갤러리', name):     # 태그는 museum인데 이름이 미술관인 곳
        return '미술관'
    if tour in ('museum', 'gallery', 'aquarium', 'zoo', 'theme_park', 'viewpoint'):
        return CAT_TOURISM[tour]
    if t.get('historic') in HISTORIC:
        return '유적'
    return CAT_TOURISM.get(tour, '관광지')


def osm_candidates(elements, center):
    """원소 → 후보 목록(이름 있음 · 놀이기구 아님 · 거름 낱말 없음 · 15 km 안 · 같은 이름은 점수 높은 하나)."""
    best = {}
    for el in elements:
        t = el.get('tags') or {}
        name = clean_name(t.get('name:ko')) or clean_name(t.get('name'))
        if not name or any(w in name for w in SKIP_WORDS + SKIP_WORDS_ADULT):
            continue
        if any(name_key(x) in name_key(name) for x in EXCLUDE_NAMES) or is_excluded_by_tags(t):
            continue
        if t.get('amenity') in SKIP_AMENITY or any(k in t for k in SKIP_KEYS):
            continue
        if t.get('attraction') in RIDE_VALUES or t.get('access') in ('private', 'no') or t.get('disused') or t.get('abandoned'):
            continue
        if 'lat' in el and 'lon' in el:
            lat, lon = el['lat'], el['lon']
        elif isinstance(el.get('center'), dict):
            lat, lon = el['center'].get('lat'), el['center'].get('lon')
        else:
            continue
        if lat is None or lon is None:
            continue
        dist = haversine_km(center, (lat, lon))
        if dist > RADIUS_M / 1000.0:
            continue
        cat = osm_category(t, name)
        score = 0.0
        score += 3 if t.get('wikidata') else 0
        score += 3 if t.get('wikipedia') else 0
        score += 2 if t.get('heritage') or t.get('heritage:operator') else 0
        score += 2 if HANGUL.search(name) else 0
        score += 1 if t.get('name:ko') else 0
        score += 1 if (t.get('website') or t.get('contact:website')) else 0
        score += 1 if t.get('opening_hours') else 0
        if t.get('historic') == 'monument' and not (t.get('wikidata') or t.get('wikipedia') or t.get('heritage')):
            score -= 1.5                                      # 근거 태그 없는 기념비 · 동상 · 표지석은 뒤로
        score -= dist * 0.1                                   # 가까운 곳을 아주 조금 앞세운다(일정 짜기 좋게)
        c = {'id': 'osm-%s-%s' % (el.get('type', 'x'), el.get('id')), 'name': name, 'cat': cat,
             'indoor': cat in INDOOR_CATS, 'addr': osm_addr(t), 'lat': lat, 'lon': lon,
             'desc': norm(t.get('description:ko')), 'score': score, 'dist': dist}
        k = series_key(name)
        if k not in best or c['score'] > best[k]['score']:
            best[k] = c
    return sorted(best.values(), key=lambda c: -c['score'])


def select_places(cands, cat_cap=CAT_CAP):
    """점수순으로 훑으며 분류 상한 · 실내 상한 · 최소 간격을 지켜 PER_MAX곳까지 고른다. 모자라면 상한을 늘려 다시 훑는다."""
    sel = []
    for cap in (cat_cap, cat_cap + 2, 99):
        for c in cands:
            if len(sel) >= PER_MAX:
                break
            if c in sel:
                continue
            if sum(1 for s in sel if s['cat'] == c['cat']) >= cap:
                continue
            if c['indoor'] and sum(1 for s in sel if s['indoor']) >= INDOOR_CAP:
                continue
            if any(haversine_km((c['lat'], c['lon']), (s['lat'], s['lon'])) < MIN_SEP_KM for s in sel):
                continue
            sel.append(c)
        if len(sel) >= PER_MIN + 1:
            break
    return sorted(sel, key=lambda c: c['dist'])


def to_place(c):
    return {'id': c['id'], '이름': c['name'], '분류': c['cat'], '실내': bool(c['indoor']), '주소': c['addr'],
            '위도': round(c['lat'], 6), '경도': round(c['lon'], 6), '사진': c.get('photo', ''), '설명': c['desc']}


def fetch_osm(args):
    regions = []
    for i, (name, lat, lon) in enumerate(REGIONS):
        raw = None
        cpath = os.path.join(args.cache, 'overpass_%s.json' % name) if args.cache else None
        if cpath and os.path.isfile(cpath):
            with open(cpath, encoding='utf-8') as f:
                raw = json.load(f)
            out('  %s: 캐시 사용 %s' % (name, cpath))
        if raw is None:
            out('  %s: Overpass 호출 …' % name)
            raw = overpass(osm_query(lat, lon))
            if cpath:
                os.makedirs(args.cache, exist_ok=True)
                with open(cpath, 'w', encoding='utf-8') as f:
                    json.dump(raw, f, ensure_ascii=False)
        cands = osm_candidates(raw['elements'], (lat, lon))
        sel = select_places(cands)
        out('  %s: 원소 %d → 후보 %d → 선택 %d' % (name, len(raw['elements']), len(cands), len(sel)))
        regions.append({'이름': name, '위도': lat, '경도': lon, '장소': [to_place(c) for c in sel]})
    return regions


# ---------------------------------------------------------------- TourAPI
def tour_rows(text):
    """응답 글 → item 목록. 함정: 인증 오류는 XML · items가 "" · item이 객체 하나 · 숫자가 문자열."""
    s = text.lstrip()
    if s.startswith('<'):
        msg = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', s)).strip()[:140]
        raise ValueError('TourAPI가 XML 오류를 돌려줌: %s' % msg)
    data = json.loads(s)
    resp = data.get('response') if isinstance(data, dict) else None
    if not isinstance(resp, dict):
        raise ValueError('TourAPI 응답 모양이 다름: %s' % str(data)[:140])
    hdr = resp.get('header') or {}
    if str(hdr.get('resultCode')) != '0000':
        raise ValueError('resultCode %s %s' % (hdr.get('resultCode'), hdr.get('resultMsg')))
    items = (resp.get('body') or {}).get('items')
    if not items or not isinstance(items, dict):                # "" 또는 빈 값 = 결과 없음
        return []
    item = items.get('item')
    if isinstance(item, dict):
        return [item]
    return item if isinstance(item, list) else []


def tour_call(key, lat, lon, ctype, rows=60):
    url = (TOUR + 'locationBasedList2?serviceKey=' + key_value(key) +
           '&MobileOS=ETC&MobileApp=FRAMEtrip&_type=json&mapX=%s&mapY=%s&radius=%d&contentTypeId=%d&arrange=E&numOfRows=%d&pageNo=1'
           % (lon, lat, RADIUS_M, ctype, rows))
    try:
        text = http_get(url)
    except Exception as e:                                       # noqa: BLE001
        raise RuntimeError('TourAPI 호출 실패: %s' % scrub(e, key))
    try:
        return tour_rows(text)
    except ValueError as e:
        raise ValueError(scrub(e, key))


def tour_category(title, ctype):
    for word, cat in (('박물관', '박물관'), ('미술관', '미술관'), ('갤러리', '미술관'), ('수족관', '수족관'), ('아쿠아', '수족관'),
                      ('동물원', '동물원'), ('전망대', '전망'), ('테마파크', '테마공원')):
        if word in title:
            return cat
    return '관광지' if ctype == 12 else '문화시설'


def tour_candidates(rows, center, ctype):
    out_rows = []
    for it in rows:
        title = norm(it.get('title'))
        try:
            lon, lat = float(it.get('mapx')), float(it.get('mapy'))      # 숫자 문자열
        except (TypeError, ValueError):
            continue
        if not title or not it.get('contentid') or (lat == 0 and lon == 0):
            continue
        cat = tour_category(title, ctype)
        photo = norm(it.get('firstimage')) or norm(it.get('firstimage2'))
        out_rows.append({'id': str(it['contentid']), 'name': title, 'cat': cat,
                         'indoor': ctype == 14 or cat in INDOOR_CATS,
                         'addr': norm('%s %s' % (it.get('addr1') or '', it.get('addr2') or '')),
                         'lat': lat, 'lon': lon, 'desc': '', 'photo': photo,
                         'dist': haversine_km(center, (lat, lon))})
    return out_rows


def fetch_tourapi(args):
    key = os.environ.get('TOURAPI_KEY', '').strip()
    if not key:
        raise RuntimeError('--source tourapi는 환경변수 TOURAPI_KEY가 필요합니다')
    regions = []
    for name, lat, lon in REGIONS:
        by_type = {}
        for ctype in (12, 14):
            by_type[ctype] = tour_candidates(tour_call(key, lat, lon, ctype), (lat, lon), ctype)
            time.sleep(0.5)
        # 사진이 있는 것을 먼저, 그다음 가까운 순. 관광지 8 + 문화시설 4를 노리고 모자라면 서로 채운다.
        pools = {t: sorted(v, key=lambda c: (not c['photo'], c['dist'])) for t, v in by_type.items()}
        picked, seen = [], set()

        def add(pool, upto):
            for c in pool:
                if len(picked) >= upto:
                    return
                k = series_key(c['name'])
                if k not in seen:
                    seen.add(k)
                    picked.append(c)
        add(pools[12], 8)
        add(pools[14], PER_MAX)
        add(pools[12], PER_MAX)
        add(pools[14], PER_MAX)
        picked.sort(key=lambda c: c['dist'])
        out('  %s: 관광지 %d + 문화시설 %d 후보 → 선택 %d' % (name, len(pools[12]), len(pools[14]), len(picked)))
        regions.append({'이름': name, '위도': lat, '경도': lon, '장소': [to_place(c) for c in picked]})
    return regions


# ---------------------------------------------------------------- 검증
def validate(regions):
    """자료 검증. 문제 목록을 돌려준다 — 하나라도 있으면 파일을 쓰지 않는다."""
    bad = []
    if [r['이름'] for r in regions] != [r[0] for r in REGIONS]:
        bad.append('지역 목록이 다름')
    names, ids, series = {}, set(), {}
    for r in regions:
        n = len(r['장소'])
        if not PER_MIN <= n <= PER_MAX:
            bad.append('%s: 장소 %d곳 (기대 %d~%d)' % (r['이름'], n, PER_MIN, PER_MAX))
        for p in r['장소']:
            for f in ('id', '이름', '분류', '실내', '주소', '위도', '경도', '사진', '설명'):
                if f not in p:
                    bad.append('%s/%s: 필드 %s 없음' % (r['이름'], p.get('이름'), f))
            if not norm(p.get('이름')):
                bad.append('%s: 이름이 빈 장소 %s' % (r['이름'], p.get('id')))
                continue
            if not norm(p.get('분류')) or not isinstance(p.get('실내'), bool):
                bad.append('%s/%s: 분류 · 실내 값이 이상함' % (r['이름'], p['이름']))
            k = name_key(p['이름'])
            if k in names:
                bad.append('이름 중복: %s (%s · %s)' % (p['이름'], names[k], r['이름']))
            names[k] = r['이름']
            sk = series_key(p['이름'])
            if sk in series and series[sk] != p['이름']:
                bad.append('번호만 다른 이름: %s · %s' % (series[sk], p['이름']))
            series[sk] = p['이름']
            if p['id'] in ids:
                bad.append('id 중복: %s' % p['id'])
            ids.add(p['id'])
            d = haversine_km((r['위도'], r['경도']), (p['위도'], p['경도']))
            if d > RADIUS_M / 1000.0 + 0.01:
                bad.append('%s/%s: 중심에서 %.1f km (15 km 밖)' % (r['이름'], p['이름'], d))
    return bad


def summarize(regions):
    out('  %-4s %6s %6s %10s  분류' % ('지역', '장소', '실내', '주소 빈칸'))
    tot = [0, 0, 0]
    for r in regions:
        ps = r['장소']
        cats = {}
        for p in ps:
            cats[p['분류']] = cats.get(p['분류'], 0) + 1
        a, b, c = len(ps), sum(1 for p in ps if p['실내']), sum(1 for p in ps if not p['주소'])
        tot = [tot[0] + a, tot[1] + b, tot[2] + c]
        out('  %-4s %6d %6d %10d  %s' % (r['이름'], a, b, c, ' '.join('%s%d' % kv for kv in sorted(cats.items(), key=lambda kv: -kv[1]))))
    out('  합계 %6d %6d %10d' % tuple(tot))


# ---------------------------------------------------------------- 중심 좌표 대조(출력만)
def verify_centers():
    out('중심 좌표 Nominatim 대조 (출력만 · 값은 바꾸지 않음)')
    for i, (name, lat, lon) in enumerate(REGIONS):
        if i:
            time.sleep(NOMINATIM_GAP)
        q = [('q', NOMINATIM_Q.get(name, name)), ('format', 'json'), ('limit', '1'), ('countrycodes', 'kr'),
             ('accept-language', 'ko'), ('featuretype', 'city')]
        try:
            arr = json.loads(http_get('https://nominatim.openstreetmap.org/search?' + urllib.parse.urlencode(q)))
            if not arr:
                out('  %s: 후보 0건' % name)
                continue
            a = arr[0]
            la, lo = float(a['lat']), float(a['lon'])
            out('  %s: 쓰는 값 (%s, %s) · Nominatim (%.4f, %.4f) %s · 거리 %.2f km' % (
                name, lat, lon, la, lo, a.get('display_name', '')[:40], haversine_km((lat, lon), (la, lo))))
        except Exception as e:                                   # noqa: BLE001
            out('  %s: 확인 실패 — %s' % (name, e))


# ---------------------------------------------------------------- 파일
def zip_dir(folder, zip_path):
    if os.path.exists(zip_path):
        os.remove(zip_path)
    root = os.path.dirname(folder)
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
        for d, _, files in os.walk(folder):
            for f in sorted(files):
                p = os.path.join(d, f)
                z.write(p, os.path.relpath(p, root))


def write_data(text):
    """직전 파일을 새 파일로 한 번에 바꾼다(쓰다 끊겨도 직전 파일이 남는다)."""
    os.makedirs(TRACK, exist_ok=True)
    tmp = DATA + '.new'
    with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    os.replace(tmp, DATA)


def drop_stale_texts():
    """트랙 폴더 맨 위의 .md 가운데 TEXTS · 1판 이름에 없는 것은 지난 판이 남긴 규칙 파일 사본이므로 지운다(관광지.js 같은 다른 파일은 건드리지 않는다)."""
    if not os.path.isdir(TRACK):
        return
    for name in sorted(os.listdir(TRACK)):
        p = os.path.join(TRACK, name)
        if os.path.isfile(p) and name.endswith('.md') and name not in TEXTS and name not in V1_NAMES:
            os.remove(p)
            out('  지움 여행앱_4시간/%s (규칙 파일은 AGENTS.md 하나)' % name)


def copy_texts():
    drop_stale_texts()
    for name in TEXTS:
        src = os.path.join(TEXT_V2, name)
        if os.path.isfile(src):
            os.makedirs(TRACK, exist_ok=True)
            shutil.copyfile(src, os.path.join(TRACK, name))
            out('  복사 app_text_v2/%s -> 여행앱_4시간/%s (%d B)' % (name, name, os.path.getsize(src)))
        else:
            out('  없음 app_text_v2/%s — 건너뜀' % name)


NODE_EVAL = ("const vm=require('vm'),fs=require('fs');const w={};"
             "vm.runInNewContext(fs.readFileSync(process.argv[1],'utf8'),{window:w});const d=w.관광지;"
             "console.log(JSON.stringify(d.지역.map(r=>[r.이름,r.장소.length,r.장소.filter(p=>p.실내).length,r.장소.filter(p=>!p.주소).length])))")


def check_folder(key):
    """폴더 정적 검증. 실패 개수를 돌려준다."""
    bad = 0
    files = []
    for d, _, fs in os.walk(TRACK):
        for f in sorted(fs):
            p = os.path.join(d, f)
            files.append((os.path.relpath(p, TRACK).replace(os.sep, '/'), os.path.getsize(p)))
    out('[여행앱_4시간] 파일 %d개' % len(files))
    for rel, size in files:
        out('  %-16s %7d B' % (rel, size))
        base = rel.split('/')[0]
        if base in LIMITS and size > LIMITS[base]:
            out('    경고: %s가 상한 %d B를 넘음' % (base, LIMITS[base]))
    total = sum(size for rel, size in files if rel in ('AGENTS.md', 'prd.md', '자료설명.md'))
    out('  AGENTS.md + prd.md + 자료설명.md 합계 %d B (상한 %d B)%s' % (total, TOTAL_LIMIT, '' if total <= TOTAL_LIMIT else ' — 경고: 넘음'))
    left = [n for n in V1_NAMES if os.path.exists(os.path.join(TRACK, n))]
    out('  1판 파일 잔존 %d개%s' % (len(left), ' ' + str(left) if left else ''))
    bad += len(left)

    keylike = []
    for d, _, fs in os.walk(TRACK):
        for f in fs:
            if f.endswith(('.html', '.js', '.md')):
                with open(os.path.join(d, f), encoding='utf-8', errors='replace') as fh:
                    text = fh.read()
                for m in re.finditer(r'[A-Za-z0-9%+/=]{60,}', text):
                    keylike.append((f, m.group(0)[:12] + '…'))
                if key and (key in text or key_value(key) in text):
                    keylike.append((f, '환경변수 키와 같은 글'))
    out('  키처럼 보이는 문자열 %d건%s' % (len(keylike), ' ' + str(keylike) if keylike else ''))
    bad += 1 if keylike else 0

    node = shutil.which('node')
    if not node:
        out('  node --check 미확인 (node 없음)')
        return bad
    r = subprocess.run([node, '--check', DATA], capture_output=True, text=True, encoding='utf-8')
    out('  node --check 관광지.js: %s' % ('통과' if r.returncode == 0 else '실패 ' + r.stderr.strip()[:200]))
    bad += 0 if r.returncode == 0 else 1
    r = subprocess.run([node, '-e', NODE_EVAL, DATA], capture_output=True, text=True, encoding='utf-8')
    if r.returncode == 0:
        out('  node 로드 [지역, 장소, 실내, 주소 빈칸]: %s' % r.stdout.strip())
    else:
        out('  node 로드 실패 %s' % r.stderr.strip()[:200])
        bad += 1
    return bad


def main(argv=None):
    ap = argparse.ArgumentParser(description='여행 앱 4시간(2판) 준비물 폴더 생성')
    ap.add_argument('--source', choices=('osm', 'tourapi'), default='osm', help='관광지 자료 원천(기본 osm · 키 없음)')
    ap.add_argument('--verify-centers', action='store_true', help='중심 좌표를 Nominatim으로 대조해 찍는다(바꾸지 않음)')
    ap.add_argument('--texts-only', action='store_true', help='관광지.js를 새로 받지 않고 문서 복사 · 검증 · zip만 다시 한다(네트워크 없음)')
    ap.add_argument('--cache', metavar='DIR', help='Overpass 원응답 저장 · 재사용 폴더(개발용 · 저장소 안 tmp/ 권장)')
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    today = datetime.date.today()
    out('생성일 %s · 원천 %s · 지역 %s' % (today, args.source, ' '.join(r[0] for r in REGIONS)))
    if args.verify_centers:
        verify_centers()

    failed = False
    if args.texts_only:
        if not os.path.isfile(DATA):
            out('경고: --texts-only는 관광지.js가 있어야 합니다')
            return 2
        out('관광지.js는 그대로 둡니다 (%d B) — 문서 복사 · 검증 · zip만 다시 합니다' % os.path.getsize(DATA))
    else:
        try:
            regions = fetch_osm(args) if args.source == 'osm' else fetch_tourapi(args)
            problems = validate(regions)
            if problems:
                raise ValueError('자료 검증 실패 %d건: %s' % (len(problems), ' / '.join(problems[:6])))
        except Exception as e:                                   # noqa: BLE001
            failed = True
            out('경고: 관광지.js를 새로 만들지 못했습니다 — %s' % scrub(e, os.environ.get('TOURAPI_KEY', '').strip()))
            if os.path.isfile(DATA):
                out('  직전 관광지.js를 그대로 둡니다 (%d B)' % os.path.getsize(DATA))
            else:
                out('  직전 관광지.js도 없습니다')
    if not failed and not args.texts_only:
        data = {'만든날': today.isoformat(), '출처': SRC_TEXT[args.source], '지역': regions}
        write_data(render(data))
        out('관광지.js 작성 — %d B' % os.path.getsize(DATA))
        summarize(regions)

    out('문서 복사')
    copy_texts()
    if failed:
        out('zip 건너뜀 (관광지.js 갱신 실패)')
        return 2
    bad = check_folder(os.environ.get('TOURAPI_KEY', '').strip())
    if bad:
        out('zip 건너뜀 (검증 실패 %d개)' % bad)
    else:
        zip_dir(TRACK, ZIP)
        n = sum(len(fs) for _, _, fs in os.walk(TRACK))
        out('zip 여행앱_4시간.zip  파일 %d개  %.1f KB' % (n, os.path.getsize(ZIP) / 1024))
    out('검증 실패 항목 %d개' % bad)
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
