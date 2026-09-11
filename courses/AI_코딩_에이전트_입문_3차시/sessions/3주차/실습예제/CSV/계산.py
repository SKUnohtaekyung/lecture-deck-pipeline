# -*- coding: utf-8 -*-
"""
계산.py — mock_ecommerce_orders.csv → 분석대상.csv + 지표기준값.json

표준 라이브러리만 쓴다(pandas 없이 돌아간다). 원본 CSV는 **읽기만** 한다.
계산 규칙의 정본은 같은 폴더의 `지표정의.json`이고, 이 스크립트는 그 정의의
집행부다. 값이 어긋나면 `지표정의.json`을 따르고 이 파일을 고친다.

실행:
    python 계산.py                # 계산 + 산출물 갱신 + 자기검증
    python 계산.py --check        # 계산 후 기존 산출물과 비교만(파일 쓰지 않음)

종료코드: 0 통과 / 1 검증 실패
"""
import argparse
import csv
import hashlib
import io
import json
import os
import sys
from collections import Counter, OrderedDict, defaultdict
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
# 원본은 저장소의 과정 자료 폴더에 있다(읽기 전용).
SOURCE = os.path.normpath(os.path.join(
    HERE, "..", "..", "..", "..", "자료", "데이터", "mock_ecommerce_orders.csv"))
OUT_ROWS = os.path.join(HERE, "분석대상.csv")
OUT_JSON = os.path.join(HERE, "지표기준값.json")
DASHBOARD = os.path.join(HERE, "dashboard.html")
RECOVERY = os.path.join(HERE, "복구", "dashboard.html")

# 원본 스냅샷 해시 — 원본이 바뀌면 즉시 드러나게 고정한다.
SOURCE_SHA256 = "3502d6b4bcc78d28b5797566a6dbe8da5fc85d00c066bb0a3fef709e537d5192"
SOURCE_ROWS = 2424

HEADER = ["order_id", "order_date", "order_status", "customer_id", "customer_type",
          "age_group", "region", "category", "product_name", "brand", "quantity",
          "unit_price_krw", "cost_per_unit_krw", "discount_rate", "shipping_fee_krw",
          "payment_method", "delivery_days", "rating", "returned", "return_reason"]

# 판정 임계값 (지표정의.json 의 같은 값과 일치해야 한다)
QTY_MAX = 50             # 수량 50 이상은 개인 주문으로 볼 수 없다 → 제외
PRICE_SENTINEL = 999999  # 입력 오류 표식으로 쓰인 단가 → 제외
DELIV_HOLD_MIN = 30      # 배송 30일 이상은 «불가능»이 아니라 «확인 필요» → 보류
RATING_MIN, RATING_MAX = 1, 5
TODAY = date(2026, 9, 10)   # 미래 날짜 판정 기준일(제작일)


# ---------------------------------------------------------------- 반올림
def rhu(num, den, decimals):
    """정수 num/den을 소수 decimals 자리에서 **반올림(half-up)** 한 값.

    부동소수 누적 오차와 파이썬 round()의 은행가 반올림을 둘 다 피하려고
    정수 연산만 쓴다. dashboard.html의 JS도 같은 식을 쓴다.
    """
    if den == 0:
        return None
    scale = 10 ** decimals
    q, r = divmod(num * scale, den)
    if 2 * r >= den:
        q += 1
    return q if decimals == 0 else q / scale


def pct(num, den, decimals=1):
    """비율을 % 값으로. 분모 0이면 None(0이 아니다 — 미판정과 0을 구분한다)."""
    if den == 0:
        return None
    return rhu(num * 100, den, decimals)


# ---------------------------------------------------------------- 입력
def read_source():
    raw = open(SOURCE, "rb").read()
    digest = hashlib.sha256(raw).hexdigest()
    text = raw.decode("utf-8")
    reader = csv.DictReader(io.StringIO(text))
    if list(reader.fieldnames) != HEADER:
        sys.exit("FAIL 헤더가 계약과 다르다: %r" % (reader.fieldnames,))
    rows = []
    for i, r in enumerate(reader):
        r["_line"] = i + 2          # CSV 파일의 실제 행 번호(1행은 헤더)
        rows.append(r)
    return rows, digest, len(raw)


def money(row):
    """행 단위 금액. 전부 정수 원 단위이며 나머지가 생기면 즉시 실패시킨다."""
    qty = int(row["quantity"])
    price = int(row["unit_price_krw"])
    cost_unit = int(row["cost_per_unit_krw"])
    # 할인율은 0.05 단위이므로 베이시스포인트 정수로 바꿔 나머지 없이 계산한다.
    bp = int(round(float(row["discount_rate"]) * 10000))
    gross = qty * price
    disc_num = gross * bp
    if disc_num % 10000 != 0:
        sys.exit("FAIL 할인액이 정수 원이 아니다: %s" % row["order_id"])
    discount = disc_num // 10000
    return {
        "gross": gross,
        "discount": discount,
        "revenue": gross - discount,
        "cost": qty * cost_unit,
        "margin": (gross - discount) - qty * cost_unit,
        "shipping": int(row["shipping_fee_krw"]),
    }


# ---------------------------------------------------------------- 정제
def classify(rows):
    """조정표. 모든 원본 행은 정확히 하나의 판정(채택/보류/제외)을 받는다.

    단계 순서가 곧 우선순위다. 앞 단계에서 판정된 행은 뒤 단계가 다시 만지지
    않는다 — 그래야 합계가 원본 행수와 맞는다.
    """
    verdict = {}                 # _line -> (판정, 단계ID, 사유)
    flags = defaultdict(list)    # _line -> [플래그ID...] (중복 집계 · 진단용)
    checked = Counter()          # 검사기별 «검사한 행 수» — 눈먼 0 방지

    # ── 진단 플래그: 판정과 무관하게 원본 전체를 대상으로 센다.
    for r in rows:
        ln = r["_line"]
        checked["QTY"] += 1
        q = int(r["quantity"])
        if q == 0:
            flags[ln].append("A1")
        elif q >= QTY_MAX:
            flags[ln].append("A2")
        checked["PRICE"] += 1
        if int(r["unit_price_krw"]) >= PRICE_SENTINEL:
            flags[ln].append("A3")
        if int(r["unit_price_krw"]) <= 0:
            flags[ln].append("A4")
        checked["COST"] += 1
        if int(r["cost_per_unit_krw"]) > int(r["unit_price_krw"]):
            flags[ln].append("A5")
        checked["DELIV"] += 1
        if r["delivery_days"].strip():
            d = int(r["delivery_days"])
            if d < 0:
                flags[ln].append("A6")
            elif d >= DELIV_HOLD_MIN:
                flags[ln].append("A7")
        checked["DATE"] += 1
        if date.fromisoformat(r["order_date"]) > TODAY:
            flags[ln].append("A8")
        checked["RATING"] += 1
        if r["rating"].strip():
            v = int(r["rating"])
            if v < RATING_MIN or v > RATING_MAX:
                flags[ln].append("A9")
        checked["RETURN"] += 1
        if (r["returned"] == "Yes") != bool(r["return_reason"].strip()):
            flags[ln].append("A10")

    # ── 1단계: order_id 중복.
    groups = OrderedDict()
    for r in rows:
        groups.setdefault(r["order_id"], []).append(r)
    for oid, members in groups.items():
        if len(members) == 1:
            continue
        first = members[0]
        identical = all(all(m[c] == first[c] for c in HEADER) for m in members[1:])
        if identical:
            # 완전 중복 — 첫 행만 남기고 나머지를 제외한다(정보 손실 없음).
            for m in members[1:]:
                verdict[m["_line"]] = (
                    "제외", "D1", "완전중복(20열 전부 동일) — 첫 행만 채택")
        else:
            # 값이 충돌하는 중복 — 어느 쪽이 참인지 데이터로 정할 수 없다.
            diff = sorted({c for c in HEADER
                           for m in members[1:] if m[c] != first[c]})
            for m in members:
                verdict[m["_line"]] = (
                    "보류", "H1",
                    "중복 order_id의 값 충돌(%s) — 사람 승인 필요" % ",".join(diff))

    # ── 2단계: 물리적으로 불가능한 값 → 제외.
    impossible = [
        ("A1", "E1", "수량 0 — 주문으로 성립하지 않음"),
        ("A2", "E2", "수량 %d 이상 — 개인 주문 범위 밖" % QTY_MAX),
        ("A4", "E3", "단가 0 이하"),
        ("A3", "E4", "단가 %d — 입력 오류 표식" % PRICE_SENTINEL),
        ("A6", "E5", "배송일 음수"),
        ("A8", "E6", "미래 주문일"),
        ("A9", "E7", "평점 범위 밖"),
        ("A5", "E8", "원가 > 단가"),
        ("A10", "E9", "반품 여부와 반품 사유 불일치"),
    ]
    for r in rows:
        ln = r["_line"]
        if ln in verdict:
            continue
        for flag, step, why in impossible:
            if flag in flags[ln]:
                verdict[ln] = ("제외", step, why)
                break

    # ── 3단계: 확정되지 않은 주문 → 매출 집계에서 제외.
    for r in rows:
        ln = r["_line"]
        if ln in verdict:
            continue
        if r["order_status"] != "Completed":
            verdict[ln] = ("제외", "S1",
                           "주문 상태 %s — 매출 확정 전" % r["order_status"])

    # ── 나머지 전부 채택.
    for r in rows:
        verdict.setdefault(r["_line"], ("채택", "K1", "정제 통과"))

    return verdict, flags, checked


# ---------------------------------------------------------------- 집계
def build(rows, verdict, flags, checked, digest, nbytes):
    adopted = [r for r in rows if verdict[r["_line"]][0] == "채택"]
    held = [r for r in rows if verdict[r["_line"]][0] == "보류"]
    excluded = [r for r in rows if verdict[r["_line"]][0] == "제외"]

    for r in adopted:
        r["_m"] = money(r)
        r["_month"] = r["order_date"][:7]
        # 배송 30일 이상은 매출에는 넣되 배송기간 지표에서만 뺀다(부분 보류).
        r["_deliv_hold"] = "A7" in flags[r["_line"]]

    total = Counter()
    for r in adopted:
        m = r["_m"]
        total["revenue"] += m["revenue"]
        total["gross"] += m["gross"]
        total["discount"] += m["discount"]
        total["cost"] += m["cost"]
        total["margin"] += m["margin"]
        total["shipping"] += m["shipping"]
        total["qty"] += int(r["quantity"])

    returned_rows = [r for r in adopted if r["returned"] == "Yes"]
    ret_rev = sum(r["_m"]["revenue"] for r in returned_rows)
    ret_margin = sum(r["_m"]["margin"] for r in returned_rows)

    # 월별
    mon_rev, mon_ord, mon_margin = Counter(), Counter(), Counter()
    for r in adopted:
        mon_rev[r["_month"]] += r["_m"]["revenue"]
        mon_margin[r["_month"]] += r["_m"]["margin"]
        mon_ord[r["_month"]] += 1
    months = sorted(mon_rev)

    # 상품군별
    cat_rev, cat_cost, cat_ord, cat_qty = Counter(), Counter(), Counter(), Counter()
    for r in adopted:
        c = r["category"]
        cat_rev[c] += r["_m"]["revenue"]
        cat_cost[c] += r["_m"]["cost"]
        cat_ord[c] += 1
        cat_qty[c] += int(r["quantity"])
    cats = sorted(cat_rev, key=lambda c: -cat_rev[c])

    # 브랜드별
    br_rev, br_ord = Counter(), Counter()
    for r in adopted:
        br_rev[r["brand"]] += r["_m"]["revenue"]
        br_ord[r["brand"]] += 1
    brands = sorted(br_rev, key=lambda b: -br_rev[b])

    # 배송 기간 — 분모를 명시한다.
    dv = sorted(int(r["delivery_days"]) for r in adopted
                if r["delivery_days"].strip() and not r["_deliv_hold"])
    d_blank = sum(1 for r in adopted if not r["delivery_days"].strip())
    d_hold = sum(1 for r in adopted if r["_deliv_hold"])
    if dv:
        mid = len(dv) // 2
        d_median = float(dv[mid]) if len(dv) % 2 else rhu(dv[mid - 1] + dv[mid], 2, 2)
    else:
        d_median = None
    d_dist = Counter(dv)

    # 평점 — 분모를 명시한다.
    rv = [int(r["rating"]) for r in adopted if r["rating"].strip()]
    r_blank = sum(1 for r in adopted if not r["rating"].strip())
    r_dist = Counter(rv)

    customers = {r["customer_id"] for r in adopted}
    order_ids = {r["order_id"] for r in adopted}

    def step_counts(kind):
        c = Counter()
        for r in rows:
            v, step, why = verdict[r["_line"]]
            if v == kind:
                c[step] += 1
        return OrderedDict(sorted(c.items()))

    flag_counts = Counter()
    for lst in flags.values():
        for f in lst:
            flag_counts[f] += 1

    B = OrderedDict()
    B["_meta"] = OrderedDict([
        ("생성", "계산.py"),
        ("정의정본", "지표정의.json"),
        ("원본파일", "courses/AI_코딩_에이전트_입문_3차시/자료/데이터/mock_ecommerce_orders.csv"),
        ("원본_sha256", digest),
        ("원본_바이트", nbytes),
        ("원본_변경없음", digest == SOURCE_SHA256),
        ("판정기준일", TODAY.isoformat()),
        ("반올림", "금액=원 단위 정수(행 단위 반올림 없음) · 비율=소수 1자리 · "
                 "평균=소수 2자리 · 전부 half-up · 집계 후 1회만"),
    ])
    B["ROW"] = OrderedDict([
        ("ROW-01_원본행수", len(rows)),
        ("ROW-02_고유주문ID수", len({r["order_id"] for r in rows})),
        ("ROW-03_분석대상행수", len(adopted)),
        ("ROW-04_제외행수", len(excluded)),
        ("ROW-05_보류행수", len(held)),
        ("ROW-06_채택비율_pct", pct(len(adopted), len(rows))),
        ("ROW-07_조정표합계", len(adopted) + len(excluded) + len(held)),
        ("ROW-08_제외_단계별", step_counts("제외")),
        ("ROW-09_보류_단계별", step_counts("보류")),
        ("ROW-10_배송지표_부분보류행수", d_hold),
    ])
    B["ORD"] = OrderedDict([
        ("ORD-01_분석대상주문수", len(order_ids)),
        ("ORD-02_한행한주문", len(order_ids) == len(adopted)),
        ("ORD-03_고유고객수", len(customers)),
        ("ORD-04_고객당평균주문수", rhu(len(adopted), len(customers), 2)),
        ("ORD-05_총수량", total["qty"]),
        ("ORD-06_기간시작", min(r["order_date"] for r in adopted)),
        ("ORD-07_기간종료", max(r["order_date"] for r in adopted)),
        ("ORD-08_집계월수", len(months)),
    ])
    B["REV"] = OrderedDict([
        ("REV-01_순매출_krw", total["revenue"]),
        ("REV-02_할인전총액_krw", total["gross"]),
        ("REV-03_할인액_krw", total["discount"]),
        ("REV-04_할인율_pct", pct(total["discount"], total["gross"])),
        ("REV-05_배송비합계_krw", total["shipping"]),
        ("REV-06_평균주문금액_krw", rhu(total["revenue"], len(adopted), 0)),
        ("REV-07_반품제외순매출_krw", total["revenue"] - ret_rev),
        ("REV-08_반품매출_krw", ret_rev),
    ])
    B["MGN"] = OrderedDict([
        ("MGN-01_원가합계_krw", total["cost"]),
        ("MGN-02_마진_krw", total["margin"]),
        ("MGN-03_마진율_pct", pct(total["margin"], total["revenue"])),
        ("MGN-04_반품제외마진_krw", total["margin"] - ret_margin),
    ])
    B["MONTH"] = OrderedDict([
        ("MONTH-01_월목록", months),
        ("MONTH-02_월별순매출_krw", [mon_rev[m] for m in months]),
        ("MONTH-03_월별주문수", [mon_ord[m] for m in months]),
        ("MONTH-04_월별마진_krw", [mon_margin[m] for m in months]),
        ("MONTH-05_최대월", max(months, key=lambda m: mon_rev[m])),
        ("MONTH-06_최소월", min(months, key=lambda m: mon_rev[m])),
    ])
    B["CAT"] = OrderedDict([
        ("CAT-01_상품군수", len(cats)),
        ("CAT-02_목록", [OrderedDict([
            ("category", c),
            ("주문수", cat_ord[c]),
            ("수량", cat_qty[c]),
            ("순매출_krw", cat_rev[c]),
            ("원가_krw", cat_cost[c]),
            ("마진_krw", cat_rev[c] - cat_cost[c]),
            ("마진율_pct", pct(cat_rev[c] - cat_cost[c], cat_rev[c])),
            ("매출비중_pct", pct(cat_rev[c], total["revenue"])),
        ]) for c in cats]),
    ])
    B["BRAND"] = OrderedDict([
        ("BRAND-01_브랜드수", len(brands)),
        ("BRAND-02_상위5", [OrderedDict([
            ("brand", b), ("순매출_krw", br_rev[b]), ("주문수", br_ord[b])])
            for b in brands[:5]]),
    ])
    B["DELIV"] = OrderedDict([
        ("DELIV-01_평균일", rhu(sum(dv), len(dv), 2) if dv else None),
        ("DELIV-02_중앙값일", d_median),
        ("DELIV-03_최소일", dv[0] if dv else None),
        ("DELIV-04_최대일", dv[-1] if dv else None),
        ("DELIV-05_분모행수", len(dv)),
        ("DELIV-06_결측행수", d_blank),
        ("DELIV-07_보류제외행수", d_hold),
        ("DELIV-08_분포", OrderedDict((str(k), d_dist[k]) for k in sorted(d_dist))),
        ("DELIV-09_3일이내_pct",
         pct(sum(v for k, v in d_dist.items() if k <= 3), len(dv))),
    ])
    B["RATE"] = OrderedDict([
        ("RATE-01_평균", rhu(sum(rv), len(rv), 2) if rv else None),
        ("RATE-02_분모행수", len(rv)),
        ("RATE-03_무응답행수", r_blank),
        ("RATE-04_무응답_pct", pct(r_blank, len(adopted))),
        ("RATE-05_분포", OrderedDict(
            (str(k), r_dist.get(k, 0)) for k in range(RATING_MIN, RATING_MAX + 1))),
        ("RATE-06_4점이상_pct", pct(r_dist.get(4, 0) + r_dist.get(5, 0), len(rv))),
    ])
    B["RET"] = OrderedDict([
        ("RET-01_반품건수", len(returned_rows)),
        ("RET-02_반품률_pct", pct(len(returned_rows), len(adopted))),
        ("RET-03_사유분포", OrderedDict(sorted(
            Counter(r["return_reason"] for r in returned_rows).items()))),
    ])
    B["QUAL"] = OrderedDict([
        ("QUAL-01_검사한행수", OrderedDict(sorted(checked.items()))),
        ("QUAL-02_플래그건수", OrderedDict(sorted(flag_counts.items()))),
        ("QUAL-03_플래그정의", OrderedDict([
            ("A1", "수량 0"), ("A2", "수량 %d 이상" % QTY_MAX),
            ("A3", "단가 %d(입력 오류 표식)" % PRICE_SENTINEL), ("A4", "단가 0 이하"),
            ("A5", "원가 > 단가"), ("A6", "배송일 음수"),
            ("A7", "배송일 %d 이상(보류)" % DELIV_HOLD_MIN), ("A8", "미래 주문일"),
            ("A9", "평점 범위 밖"), ("A10", "반품 여부와 사유 불일치"),
        ])),
        ("QUAL-04_미판정", 0),
    ])
    B["HOLD"] = OrderedDict([
        ("HOLD-01_승인필요건수", len(held) + d_hold),
        ("HOLD-02_중복충돌", [OrderedDict([
            ("행", r["_line"]), ("order_id", r["order_id"]),
            ("quantity", r["quantity"]), ("사유", verdict[r["_line"]][2])])
            for r in held]),
        ("HOLD-03_배송이상", [OrderedDict([
            ("행", r["_line"]), ("order_id", r["order_id"]),
            ("delivery_days", r["delivery_days"]),
            ("사유", "배송 %d일 — 불가능하지는 않으나 확인 필요" % int(r["delivery_days"]))])
            for r in adopted if r["_deliv_hold"]]),
    ])
    return B, adopted, held, excluded


# ---------------------------------------------------------------- 산출
DERIVED = ["order_month", "net_revenue_krw", "cost_total_krw", "margin_krw",
           "delivery_metric_included", "source_line"]

# dashboard가 쓰는 압축 스키마(열 이름 → 인덱스). 파일 크기를 줄이려고
# 객체 배열이 아니라 배열의 배열로 싣는다.
COMPACT = ["month", "category", "brand", "region", "customer_type", "quantity",
           "revenue", "cost", "margin", "delivery_days", "rating", "returned",
           "delivery_ok"]


def write_rows(adopted):
    with open(OUT_ROWS, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(HEADER + DERIVED)
        for r in adopted:
            m = r["_m"]
            w.writerow([r[c] for c in HEADER] +
                       [r["_month"], m["revenue"], m["cost"], m["margin"],
                        "No" if r["_deliv_hold"] else "Yes", r["_line"]])


def compact_rows(adopted):
    out = []
    for r in adopted:
        m = r["_m"]
        out.append([
            r["_month"], r["category"], r["brand"], r["region"], r["customer_type"],
            int(r["quantity"]), m["revenue"], m["cost"], m["margin"],
            int(r["delivery_days"]) if r["delivery_days"].strip() else None,
            int(r["rating"]) if r["rating"].strip() else None,
            1 if r["returned"] == "Yes" else 0,
            0 if r["_deliv_hold"] else 1,
        ])
    return out


def inject(path, payload, label):
    """`<!--DATA:BEGIN-->` ~ `<!--DATA:END-->` 사이를 통째로 갈아 끼운다(멱등)."""
    if not os.path.exists(path):
        return "skip(%s 없음)" % label
    src = open(path, encoding="utf-8").read()
    b, e = "<!--DATA:BEGIN-->", "<!--DATA:END-->"
    i, j = src.find(b), src.find(e)
    if i < 0 or j < 0:
        return "skip(%s 마커 없음)" % label
    new = src[:i + len(b)] + "\n" + payload + "\n" + src[j:]
    if new != src:
        open(path, "w", encoding="utf-8", newline="").write(new)
        return "updated"
    return "unchanged"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="파일을 쓰지 않고 기존 산출물과 비교만 한다")
    args = ap.parse_args()

    rows, digest, nbytes = read_source()
    fails = []
    if digest != SOURCE_SHA256:
        fails.append("원본 SHA-256 불일치 — 원본이 수정됐다")
    if len(rows) != SOURCE_ROWS:
        fails.append("원본 행수 %d != 계약 %d" % (len(rows), SOURCE_ROWS))

    verdict, flags, checked = classify(rows)
    B, adopted, held, excluded = build(rows, verdict, flags, checked, digest, nbytes)

    # ── 자기검증 ─────────────────────────────────────────────
    if B["ROW"]["ROW-07_조정표합계"] != len(rows):
        fails.append("조정표 합계 %d != 원본 행수 %d"
                     % (B["ROW"]["ROW-07_조정표합계"], len(rows)))
    if not B["ORD"]["ORD-02_한행한주문"]:
        fails.append("분석 대상에 order_id 중복이 남았다")
    if sum(B["MONTH"]["MONTH-02_월별순매출_krw"]) != B["REV"]["REV-01_순매출_krw"]:
        fails.append("월별 매출 합 != 총 순매출")
    if sum(B["MONTH"]["MONTH-03_월별주문수"]) != len(adopted):
        fails.append("월별 주문수 합 != 분석 행수")
    if sum(c["순매출_krw"] for c in B["CAT"]["CAT-02_목록"]) != B["REV"]["REV-01_순매출_krw"]:
        fails.append("상품군 매출 합 != 총 순매출")
    if sum(c["주문수"] for c in B["CAT"]["CAT-02_목록"]) != len(adopted):
        fails.append("상품군 주문수 합 != 분석 행수")
    if sum(c["마진_krw"] for c in B["CAT"]["CAT-02_목록"]) != B["MGN"]["MGN-02_마진_krw"]:
        fails.append("상품군 마진 합 != 총 마진")
    if B["REV"]["REV-01_순매출_krw"] - B["MGN"]["MGN-01_원가합계_krw"] != B["MGN"]["MGN-02_마진_krw"]:
        fails.append("매출 - 원가 != 마진")
    if B["REV"]["REV-02_할인전총액_krw"] - B["REV"]["REV-03_할인액_krw"] != B["REV"]["REV-01_순매출_krw"]:
        fails.append("할인전총액 - 할인액 != 순매출")
    dv_total = (B["DELIV"]["DELIV-05_분모행수"] + B["DELIV"]["DELIV-06_결측행수"]
                + B["DELIV"]["DELIV-07_보류제외행수"])
    if dv_total != len(adopted):
        fails.append("배송 분모+결측+보류 %d != 분석 행수 %d" % (dv_total, len(adopted)))
    if B["RATE"]["RATE-02_분모행수"] + B["RATE"]["RATE-03_무응답행수"] != len(adopted):
        fails.append("평점 분모+무응답 != 분석 행수")
    if sum(B["RATE"]["RATE-05_분포"].values()) != B["RATE"]["RATE-02_분모행수"]:
        fails.append("평점 분포 합 != 평점 분모")
    if sum(B["DELIV"]["DELIV-08_분포"].values()) != B["DELIV"]["DELIV-05_분모행수"]:
        fails.append("배송 분포 합 != 배송 분모")
    for name, n in checked.items():
        if n != len(rows):
            fails.append("검사기 %s가 %d행만 봤다(원본 %d)" % (name, n, len(rows)))

    payload_rows = compact_rows(adopted)
    if len(payload_rows) != len(adopted):
        fails.append("대시보드 행수 != 분석 행수")

    blob = json.dumps(B, ensure_ascii=False, indent=2, sort_keys=False)

    if args.check:
        if not os.path.exists(OUT_JSON):
            fails.append("지표기준값.json 없음")
        elif open(OUT_JSON, encoding="utf-8").read().strip() != blob.strip():
            fails.append("지표기준값.json이 계산 결과와 다르다")
        dash = "check(쓰기 없음)"
    else:
        open(OUT_JSON, "w", encoding="utf-8", newline="").write(blob + "\n")
        write_rows(adopted)
        payload = ('<script id="rows-data" type="application/json">'
                   + json.dumps({"cols": COMPACT, "rows": payload_rows},
                                ensure_ascii=False, separators=(",", ":"))
                   + '</script>\n'
                   + '<script id="baseline-data" type="application/json">'
                   + json.dumps(B, ensure_ascii=False, separators=(",", ":"))
                   + '</script>')
        small = ('<script id="baseline-data" type="application/json">'
                 + json.dumps(B, ensure_ascii=False, separators=(",", ":"))
                 + '</script>')
        dash = "dashboard=%s 복구=%s" % (inject(DASHBOARD, payload, "dashboard"),
                                        inject(RECOVERY, small, "복구"))

    print("원본행 %d · 채택 %d · 제외 %d · 보류 %d · 조정표합계 %d"
          % (len(rows), len(adopted), len(excluded), len(held),
             B["ROW"]["ROW-07_조정표합계"]))
    print("주문 %d · 고객 %d · 순매출 %d원 · 마진 %d원(%s%%) · 상품군 %d · 기간 %s~%s"
          % (B["ORD"]["ORD-01_분석대상주문수"], B["ORD"]["ORD-03_고유고객수"],
             B["REV"]["REV-01_순매출_krw"], B["MGN"]["MGN-02_마진_krw"],
             B["MGN"]["MGN-03_마진율_pct"], B["CAT"]["CAT-01_상품군수"],
             B["ORD"]["ORD-06_기간시작"], B["ORD"]["ORD-07_기간종료"]))
    print("배송 평균 %s일(분모 %d · 결측 %d · 보류 %d) · 평점 평균 %s(분모 %d · 무응답 %d)"
          % (B["DELIV"]["DELIV-01_평균일"], B["DELIV"]["DELIV-05_분모행수"],
             B["DELIV"]["DELIV-06_결측행수"], B["DELIV"]["DELIV-07_보류제외행수"],
             B["RATE"]["RATE-01_평균"], B["RATE"]["RATE-02_분모행수"],
             B["RATE"]["RATE-03_무응답행수"]))
    print("검사한 행 %s · 미판정 %d건 · 승인 필요 %d건 · %s"
          % (dict(B["QUAL"]["QUAL-01_검사한행수"]), B["QUAL"]["QUAL-04_미판정"],
             B["HOLD"]["HOLD-01_승인필요건수"], dash))

    if fails:
        for f in fails:
            print("FAIL " + f)
        print("RESULT FAIL (%d건)" % len(fails))
        return 1
    print("RESULT PASS (검증 17항 · 미판정 0)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
