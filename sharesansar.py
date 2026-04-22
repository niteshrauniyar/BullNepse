"""
ShareSansar Web Scraper
Secondary data source: https://www.sharesansar.com/today-share-price
"""

import requests
import pandas as pd
import logging
from typing import Optional
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

URL = "https://www.sharesansar.com/today-share-price"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.sharesansar.com/",
}
TIMEOUT = 20


def fetch_from_sharesansar() -> Optional[pd.DataFrame]:
    """
    Scrape today's share price table from ShareSansar.
    Returns normalized-ish DataFrame or None on failure.
    """
    try:
        response = requests.get(URL, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Locate the main data table — ShareSansar uses id="headFixed" or class patterns
        table = None
        for candidate in soup.find_all("table"):
            headers_row = candidate.find("tr")
            if headers_row:
                header_text = headers_row.get_text(separator="|").lower()
                if any(k in header_text for k in ("symbol", "ltp", "close", "volume")):
                    table = candidate
                    break

        if table is None:
            logger.warning("ShareSansar: Could not find data table in HTML.")
            return None

        rows = []
        headers = []

        for i, row in enumerate(table.find_all("tr")):
            cells = [td.get_text(strip=True) for td in row.find_all(["th", "td"])]
            if i == 0:
                headers = cells
            else:
                if cells:
                    rows.append(cells)

        if not headers or not rows:
            logger.warning("ShareSansar: Parsed empty table.")
            return None

        # Align row lengths to header length
        aligned = []
        for row in rows:
            if len(row) >= len(headers):
                aligned.append(row[: len(headers)])
            else:
                row += [""] * (len(headers) - len(row))
                aligned.append(row)

        df = pd.DataFrame(aligned, columns=headers)
        logger.info(f"ShareSansar: scraped {len(df)} rows, columns: {list(df.columns)}")
        return df

    except requests.exceptions.ConnectionError:
        logger.error("ShareSansar: Connection failed.")
    except requests.exceptions.Timeout:
        logger.error("ShareSansar: Request timed out.")
    except requests.exceptions.HTTPError as e:
        logger.error(f"ShareSansar: HTTP error {e}")
    except Exception as e:
        logger.error(f"ShareSansar: Unexpected error — {e}")

    return None
