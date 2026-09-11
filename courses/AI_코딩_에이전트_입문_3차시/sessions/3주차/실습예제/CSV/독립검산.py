#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""T53 독립 검산 — 원본 CSV만 읽어 지표를 처음부터 다시 계산한다.

블라인드 원칙: 작성자의 계산.py / 지표기준값.json / 분석대상.csv / dashboard.html /
분석결과.md 를 참조하지 않는다. 입력은 원본 mock_ecommerce_orders.csv 하나뿐이며
읽기 전용으로만 연다(바이트 불변). 표준 라이브러리만 사용한다.

정의는 오케스트레이터가 확정해 전달한 «승인된 정의»를 그대로 구현했다.
"""
from __future__ import annotations

import csv
import hashlib
import sys
from collections import Counter, defaultdict
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

# Windows 콘솔 기본 인코딩(cp949)에서도 한글·기호가 깨지지 않게 UTF-8로 고정한다.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except Exception:      # 파이프·리다이렉트 등 reconfigure 불가 환경은 그대로 둔다
        pass

# ---------------------------------------------------------------- 입력 경로
HERE = Path(__file__).resolve().parent
COURSE_ROOT = HERE.parents[3]          # .../AI_코딩_에이전트_입문_3차시
SRC = COURSE_ROOT / "자료" / "데이터" / "mock_ecommerce_orders.csv"

STATUS_EXCLUDE = ("Cancelled", "Pending")   # 취소·대기 상태 = 분석 제외
OUT_QTY_ZERO = "0"
OUT_QTY_99 = "99"
OUT_PRICE = "999999"
OUT_DELIV_NEG = "-1"
HOLD_DELIV = "45"                            # 매출 포함 · 배송 분모에서만 제외

Z = Decimal(0)


# ---------------------------------------------------------------- 표시 반올림
def won(d):
    """금액: 원 단위 정수(표시 시점에만 반올림 · 계산은 원값 유지)."""
    return int(d.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def dec2(d):
    """비율·평균: 소수 둘째 자리."""
    return str(d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def sha256_of(path):
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------- 행 계산식
def gross_revenue(row):
    return Decimal(row["unit_price_krw"]) * Decimal(row["quantity"])


def discount_amount(row):
    """discount_rate 열은 비율(0~0.25)이므로 할인액 = 단가 × 수량 × 비율."""
    return gross_revenue(row) * Decimal(row["discount_rate"])


def net_revenue(row):
    """매출 = 단가 × 수량 − 할인. 배송비 제외."""
    return gross_revenue(row) - discount_amount(row)


def margin(row):
    """마진 = (단가 − 원가) × 수량 − 할인."""
    price = Decimal(row["unit_price_krw"])
    cost = Decimal(row["cost_per_unit_krw"])
    qty = Decimal(row["quantity"])
    return (price - cost) * qty - discount_amount(row)


def outlier_flags(row):
    flags = []
    if row["quantity"] == OUT_QTY_ZERO:
        flags.append("수량 0")
    if row["quantity"] == OUT_QTY_99:
        flags.append("수량 99")
    if row["unit_price_krw"] == OUT_PRICE:
        flags.append("단가 999999")
    if row["delivery_days"] == OUT_DELIV_NEG:
        flags.append("배송일 -1")
    return flags


# ---------------------------------------------------------------- 정제 파이프라인
def main():
    if not SRC.exists():
        sys.stderr.write("FAIL 원본 CSV 없음: %s\n" % SRC)
        return 1

    sha_before = sha256_of(SRC)
    with SRC.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        header = list(reader.fieldnames or [])
        raw = [dict(r) for r in reader]

    n_raw = len(raw)
    n_unique_id = len({r["order_id"] for r in raw})

    # (1) 완전 중복(모든 열 동일) — 1행만 남기고 제외
    key_count = Counter(tuple(r[c] for c in header) for r in raw)
    n_dup_groups = sum(1 for v in key_count.values() if v > 1)
    seen = set()
    deduped = []
    for r in raw:
        k = tuple(r[c] for c in header)
        if k in seen:
            continue
        seen.add(k)
        deduped.append(r)
    n_exact_dup_removed = n_raw - len(deduped)

    # (2) 같은 order_id인데 값이 다른 행 — 양쪽 모두 보류
    by_id = defaultdict(list)
    for r in deduped:
        by_id[r["order_id"]].append(r)
    conflict_ids = sorted(i for i, rs in by_id.items() if len(rs) > 1)
    cset = set(conflict_ids)
    n_conflict_rows = sum(1 for r in deduped if r["order_id"] in cset)
    after_conflict = [r for r in deduped if r["order_id"] not in cset]

    # (3) 취소·대기 상태 제외
    status_removed = Counter(
        r["order_status"] for r in after_conflict if r["order_status"] in STATUS_EXCLUDE
    )
    after_status = [r for r in after_conflict if r["order_status"] not in STATUS_EXCLUDE]
    n_status_removed = sum(status_removed.values())

    # (4) 이상값(입력 오류) 제외
    outlier_hits = Counter()      # 유형별 발생(겹침 포함)
    outlier_bucket = Counter()    # 유형별 배정(우선순위 · 겹침 없음)
    analysis = []
    n_outlier_rows = 0
    for r in after_status:
        flags = outlier_flags(r)
        if flags:
            n_outlier_rows += 1
            for f in flags:
                outlier_hits[f] += 1
            outlier_bucket[flags[0]] += 1
            continue
        analysis.append(r)

    n_analysis = len(analysis)
    n_orders = n_analysis   # 분석 행 = 주문 수(분모)

    # ---------------------------------------------------------------- 집계
    rev = sum((net_revenue(r) for r in analysis), Z)
    rev_gross = sum((gross_revenue(r) for r in analysis), Z)
    disc = sum((discount_amount(r) for r in analysis), Z)
    mar = sum((margin(r) for r in analysis), Z)
    ship = sum((Decimal(r["shipping_fee_krw"]) for r in analysis), Z)
    returned_rows = [r for r in analysis if r["returned"] == "Yes"]
    ret_amount = sum((net_revenue(r) for r in returned_rows), Z)
    ret_margin = sum((margin(r) for r in returned_rows), Z)

    margin_rate = (mar / rev * 100) if rev else Z
    aov = (rev / n_orders) if n_orders else Z
    return_rate = (Decimal(len(returned_rows)) / n_orders * 100) if n_orders else Z

    monthly = defaultdict(lambda: [Z, 0])
    for r in analysis:
        m = r["order_date"][:7]
        monthly[m][0] += net_revenue(r)
        monthly[m][1] += 1

    by_cat = defaultdict(lambda: [Z, Z, 0])
    for r in analysis:
        c = by_cat[r["category"]]
        c[0] += net_revenue(r)
        c[1] += margin(r)
        c[2] += 1

    brands = sorted({r["brand"] for r in analysis})

    deliv_vals = []
    n_deliv_blank = 0
    n_deliv_hold = 0
    for r in analysis:
        v = r["delivery_days"].strip()
        if v == "":
            n_deliv_blank += 1
            continue
        if v == HOLD_DELIV:
            n_deliv_hold += 1
            continue
        deliv_vals.append(Decimal(v))
    deliv_avg = (sum(deliv_vals, Z) / len(deliv_vals)) if deliv_vals else Z

    rate_vals = [Decimal(r["rating"]) for r in analysis if r["rating"].strip() != ""]
    n_rating_blank = n_analysis - len(rate_vals)
    rating_avg = (sum(rate_vals, Z) / len(rate_vals)) if rate_vals else Z

    # 모호 정의 병기
    rev_minus_return = rev - ret_amount          # B안: 반품 차감
    mar_minus_return = mar - ret_margin
    aov_b = (rev_minus_return / n_orders) if n_orders else Z
    deliv_vals_c = deliv_vals + [Decimal(HOLD_DELIV)] * n_deliv_hold   # C안
    deliv_avg_c = (sum(deliv_vals_c, Z) / len(deliv_vals_c)) if deliv_vals_c else Z
    rev_plus_ship = rev + ship                   # E안: 배송비 포함 매출

    sha_after = sha256_of(SRC)

    # ---------------------------------------------------------------- 출력
    p = print
    p("=" * 72)
    p("T53 독립 검산 — 원본 CSV 단독 재계산")
    p("=" * 72)
    p("원본 파일        : %s" % SRC.as_posix())
    p("원본 SHA-256(전) : %s" % sha_before)
    p("원본 SHA-256(후) : %s" % sha_after)
    p("해시 불변        : %s" % ("YES" if sha_before == sha_after else "NO"))
    p("헤더 %d열       : %s" % (len(header), ",".join(header)))
    p("")
    p("[1] 행 계수")
    p("  원본 행                    : %d" % n_raw)
    p("  고유 order_id              : %d" % n_unique_id)
    p("  완전중복 제거              : %d  (중복 그룹 %d개)" % (n_exact_dup_removed, n_dup_groups))
    p("  값 충돌 보류               : %d  (order_id %s)"
      % (n_conflict_rows, ", ".join(conflict_ids) if conflict_ids else "-"))
    p("  취소/대기 제외             : %d  (%s)"
      % (n_status_removed, ", ".join("%s %d" % (k, v) for k, v in sorted(status_removed.items()))))
    p("  이상값 제외(행)            : %d" % n_outlier_rows)
    for k in ("수량 0", "수량 99", "단가 999999", "배송일 -1"):
        p("    - %-12s: 발생 %d  배정 %d" % (k, outlier_hits.get(k, 0), outlier_bucket.get(k, 0)))
    p("  분석 행(= 주문 수)         : %d" % n_analysis)
    p("  부분 보류(배송일 45)       : %d  (매출 포함 · 배송 분모 제외)" % n_deliv_hold)
    p("")
    p("[2] 조정표 (원본 행 = 분석 + 제외 + 보류)")
    total_check = (n_analysis + n_exact_dup_removed + n_conflict_rows
                   + n_status_removed + n_outlier_rows)
    p("  %d + %d + %d + %d + %d = %d"
      % (n_analysis, n_exact_dup_removed, n_conflict_rows, n_status_removed,
         n_outlier_rows, total_check))
    p("  원본 행 %d 대조         : %s" % (n_raw, "OK" if total_check == n_raw else "MISMATCH"))
    p("")
    p("[3] 금액 지표 (A안 = 승인된 정의: 할인 = 단가×수량×discount_rate · 배송비 제외 · 반품 미차감)")
    p("  총매출(순액)               : %s 원" % format(won(rev), ","))
    p("  총매출(할인 전 총액)       : %s 원" % format(won(rev_gross), ","))
    p("  할인액 합                  : %s 원" % format(won(disc), ","))
    p("  반품 금액(별도 지표)       : %s 원  (반품 %d건 · 반품률 %s%%)"
      % (format(won(ret_amount), ","), len(returned_rows), dec2(return_rate)))
    p("  배송비 합(매출 제외)       : %s 원" % format(won(ship), ","))
    p("  마진                       : %s 원" % format(won(mar), ","))
    p("  마진율                     : %s %%" % dec2(margin_rate))
    p("  평균 주문금액              : %s 원  (정수 표시 %s 원)" % (dec2(aov), format(won(aov), ",")))
    p("")
    p("[4] 월별 매출 (주문일 기준)")
    for m in sorted(monthly):
        amt, cnt = monthly[m]
        p("  %s : %12s 원   주문 %4d" % (m, format(won(amt), ","), cnt))
    p("  %s : %12s 원   주문 %4d"
      % ("합계   ", format(won(sum((v[0] for v in monthly.values()), Z)), ","),
         sum(v[1] for v in monthly.values())))
    p("")
    p("[5] 상품군별 매출·마진·주문 수")
    for c in sorted(by_cat):
        rv, mg, cnt = by_cat[c]
        rr = (mg / rv * 100) if rv else Z
        p("  %-12s 매출 %12s   마진 %12s   마진율 %6s %%   주문 %4d"
          % (c, format(won(rv), ","), format(won(mg), ","), dec2(rr), cnt))
    p("  상품군 수 : %d" % len(by_cat))
    p("")
    p("[6] 브랜드 수 : %d" % len(brands))
    p("  %s" % ", ".join(brands))
    p("")
    p("[7] 배송·평점")
    p("  배송 기간 평균             : %s 일  (분모 %d)" % (dec2(deliv_avg), len(deliv_vals)))
    p("    배송일 공백 제외         : %d" % n_deliv_blank)
    p("    배송일 45 보류 제외      : %d" % n_deliv_hold)
    p("  평점 평균                  : %s 점  (분모 %d)" % (dec2(rating_avg), len(rate_vals)))
    p("    미평가 제외              : %d" % n_rating_blank)
    p("")
    p("[8] 모호 정의 병기")
    p("  B안 반품 차감 총매출       : %s 원  (마진 %s · 평균 주문금액 %s)"
      % (format(won(rev_minus_return), ","), format(won(mar_minus_return), ","), dec2(aov_b)))
    p("  C안 배송일 45 포함 평균    : %s 일  (분모 %d)" % (dec2(deliv_avg_c), len(deliv_vals_c)))
    p("  D안 할인 미적용 총매출     : %s 원" % format(won(rev_gross), ","))
    p("  E안 배송비 포함 총매출     : %s 원" % format(won(rev_plus_ship), ","))
    p("")
    p("RESULT T53-독립검산 OK (작성자 값과의 대조는 오케스트레이터 담당)")
    return 0 if (sha_before == sha_after and total_check == n_raw) else 1


if __name__ == "__main__":
    raise SystemExit(main())
