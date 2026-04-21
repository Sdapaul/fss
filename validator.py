#!/usr/bin/env python3
"""
포털 최신 항목과 DB 발송 이력을 비교해 누락·불일치를 검증.

실행:
  python validator.py [days_back=7]
"""

import sys
from datetime import date, timedelta

from scraper import _fetch_page, _build_detail_url
from db import _conn


def validate_recent(days_back: int = 7) -> dict:
    """최근 days_back일 포털 항목이 DB에 모두 있는지 검증."""
    cutoff = (date.today() - timedelta(days=days_back)).isoformat()

    try:
        raw_items = _fetch_page(start=0, length=100)
    except Exception as e:
        return {"error": str(e)}

    portal_items: dict[str, dict] = {}
    for raw in raw_items:
        item_date = raw.get("replyRegDate", "")[:10]
        if item_date < cutoff:
            continue
        item_type = raw.get("pastreqType", "")
        data_idx = raw.get("dataIdx", 0)
        uid = f"{item_type}:{data_idx}"
        portal_items[uid] = {
            "id": uid,
            "title": raw.get("title", "").strip(),
            "date": item_date,
            "category": item_type,
            "url": _build_detail_url(item_type, data_idx),
        }

    if portal_items:
        placeholders = ",".join("?" for _ in portal_items)
        with _conn() as conn:
            existing_ids = {
                row[0]
                for row in conn.execute(
                    f"SELECT id FROM items WHERE id IN ({placeholders})",
                    list(portal_items.keys()),
                )
            }
    else:
        existing_ids = set()

    missing_ids = set(portal_items.keys()) - existing_ids
    missing_items = [portal_items[uid] for uid in sorted(missing_ids)]

    return {
        "cutoff": cutoff,
        "portal_count": len(portal_items),
        "db_count": len(existing_ids),
        "missing_count": len(missing_ids),
        "missing_items": missing_items,
    }


def main() -> None:
    days_back = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    print(f"최근 {days_back}일 포털 항목 검증 중...")

    result = validate_recent(days_back)

    if "error" in result:
        print(f"오류: {result['error']}", file=sys.stderr)
        sys.exit(1)

    print(f"포털 항목 수: {result['portal_count']}건")
    print(f"DB 발송 이력: {result['db_count']}건")
    print(f"누락 항목 수: {result['missing_count']}건")

    if result["missing_items"]:
        print("\n[누락 항목 목록]")
        for item in result["missing_items"]:
            print(f"  [{item['category']}] {item['date']} {item['title']}")
            print(f"    URL: {item['url']}")
        sys.exit(2)
    else:
        print("검증 완료 — 모든 항목 정상 발송됨")


if __name__ == "__main__":
    main()
