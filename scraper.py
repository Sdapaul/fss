import requests
from bs4 import BeautifulSoup
from datetime import date, timedelta
import re

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ko-KR,ko;q=0.9",
    "Referer": "https://www.fss.or.kr/",
}

BASE_URL = "https://www.fss.or.kr"

SOURCES = [
    {
        "name": "비조치의견서",
        "url": f"{BASE_URL}/fss/bbs/B0000188/list.do?menuNo=200218",
    },
    {
        "name": "법령해석",
        "url": f"{BASE_URL}/fss/bbs/B0000189/list.do?menuNo=200219",
    },
]


def _parse_date(text: str) -> str:
    """날짜 문자열 정규화 (YYYY.MM.DD / YYYY-MM-DD → YYYY-MM-DD)."""
    text = text.strip()
    text = re.sub(r"[./]", "-", text)
    # 앞 10자만 사용 (시간 제거)
    return text[:10]


def _extract_items(soup: BeautifulSoup, source_name: str) -> list[dict]:
    """공통 BBS 테이블에서 항목 추출."""
    items = []

    rows = soup.select("table.tb_list tbody tr")
    if not rows:
        # fallback: 일반 tbody tr
        rows = soup.select("tbody tr")

    for row in rows:
        # 공지 행 건너뜀
        if row.select_one("td.notice") or "공지" in row.get_text():
            continue

        title_tag = row.select_one("td.title a") or row.select_one("td a")
        if not title_tag:
            continue

        title = title_tag.get_text(strip=True)
        href = title_tag.get("href", "")

        # 상대경로 처리
        if href.startswith("/"):
            href = BASE_URL + href
        elif not href.startswith("http"):
            href = BASE_URL + "/" + href.lstrip("./")

        # 날짜
        date_td = row.select_one("td.date") or row.select_one("td:last-child")
        raw_date = date_td.get_text(strip=True) if date_td else ""
        item_date = _parse_date(raw_date) if raw_date else ""

        # 고유 ID (URL 파라미터 또는 제목+날짜)
        item_id = href if href else f"{source_name}:{title}:{item_date}"

        items.append(
            {
                "id": item_id,
                "title": title,
                "date": item_date,
                "url": href,
                "category": source_name,
            }
        )

    return items


def fetch_new_items(seen_ids: set, days_back: int = 1) -> list[dict]:
    """
    FSS에서 항목을 가져와 seen_ids 에 없는 신규 항목만 반환.
    days_back: 오늘로부터 며칠 이내 항목까지 포함할지 (중복 방지 보조)
    """
    cutoff = (date.today() - timedelta(days=days_back)).isoformat()
    new_items: list[dict] = []

    for source in SOURCES:
        try:
            resp = requests.get(source["url"], headers=HEADERS, timeout=15)
            resp.raise_for_status()
            resp.encoding = resp.apparent_encoding or "utf-8"
        except Exception as e:
            print(f"[{source['name']}] 요청 실패: {e}")
            continue

        soup = BeautifulSoup(resp.text, "html.parser")
        items = _extract_items(soup, source["name"])
        print(f"[{source['name']}] 파싱된 항목 수: {len(items)}")

        for item in items:
            # 날짜 필터: cutoff 이후 항목만
            if item["date"] and item["date"] < cutoff:
                continue
            # 이미 발송한 항목 제외
            if item["id"] in seen_ids:
                continue
            new_items.append(item)

    return new_items
