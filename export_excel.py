#!/usr/bin/env python3
"""
GitHub Actions workflow_dispatch 에서 호출되는 엑셀 export 스크립트.

사용법:
  python export_excel.py <date_from> <date_to>
  예) python export_excel.py 2025-01-01 2025-12-31
"""

import sys
from db import export_excel_bytes

OUTPUT_FILE = "fss_export.xlsx"


def main() -> None:
    if len(sys.argv) != 3:
        print("사용법: python export_excel.py <date_from> <date_to>", file=sys.stderr)
        sys.exit(1)

    date_from, date_to = sys.argv[1], sys.argv[2]
    print(f"기간 조회: {date_from} ~ {date_to}")

    xlsx_bytes = export_excel_bytes(date_from, date_to)
    with open(OUTPUT_FILE, "wb") as f:
        f.write(xlsx_bytes)

    print(f"엑셀 저장 완료: {OUTPUT_FILE} ({len(xlsx_bytes):,} bytes)")


if __name__ == "__main__":
    main()
